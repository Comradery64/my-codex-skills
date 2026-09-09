#!/usr/bin/env python3
"""Read Codex JSONL token totals without exposing conversation content.

Reports usage by role (root, requested workers, automatic guardians), incremental
usage since the last recorded milestone snapshot, and an explicit dispatch action
state. Enforcement is dispatch-boundary or cooperative only: this script reads
completed records and cannot cancel an in-flight response or cap an account.
"""
import argparse
import datetime
import glob
import json
import os
import sys
from collections import Counter, defaultdict

CLASSES = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
           "output_tokens", "reasoning_output_tokens", "total_tokens")
ROLES = ("root", "worker", "guardian")
GUARDIAN_SOURCES = ("guardian_review", "guardian")
# Action states, from cheapest response to most restrictive. Each is an
# instruction to the root, not merely a number: see references/cost-model.md.
PROCEED = "proceed_within_allowance"
ADVISORY = "advisory_review"
REDUCE = "reduce_or_reframe"
DIAGNOSTIC = "bounded_diagnostic"
UNAVAILABLE = "aggregate_unavailable"
BLOCKED = "resource_blocked"
EXITS = {PROCEED: 0, ADVISORY: 10, REDUCE: 20, DIAGNOSTIC: 25,
         UNAVAILABLE: 30, BLOCKED: 40}
ZERO = {key: 0 for key in CLASSES}


def records(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    value = json.loads(line)
                except (ValueError, TypeError):
                    continue
                if isinstance(value, dict):
                    yield value
    except OSError:
        return


def classify(payload):
    """Return (role_hint, agent_path) from session metadata only.

    `guardian_review` threads are automatic approval actors created by the
    runtime, not workers the root chose to spawn. Attributing them to workers
    hides real overhead; dropping them understates the tree.
    """
    source = payload.get("source")
    other = None
    if isinstance(source, dict):
        subagent = source.get("subagent")
        if isinstance(subagent, dict):
            other = subagent.get("other")
    thread_source = payload.get("thread_source")
    if thread_source in GUARDIAN_SOURCES or other in GUARDIAN_SOURCES:
        return "guardian", payload.get("agent_path")
    return "worker", payload.get("agent_path")


def inspect(path):
    meta = {"sid": None, "parent": None, "timestamp": None, "role_hint": "worker",
            "agent_path": None, "model": None, "effort": None}
    turns = token_records = 0
    latest = latest_source = None
    request_totals = Counter()
    for obj in records(path):
        payload = obj.get("payload") or {}
        if obj.get("type") == "session_meta":
            meta["sid"] = payload.get("id")
            meta["parent"] = payload.get("parent_thread_id")
            meta["timestamp"] = payload.get("timestamp") or obj.get("timestamp")
            meta["role_hint"], meta["agent_path"] = classify(payload)
        if obj.get("type") == "turn_context":
            turns += 1
            meta["model"] = payload.get("model") or meta["model"]
            meta["effort"] = payload.get("effort") or meta["effort"]
        if obj.get("type") != "token_usage_record":
            continue
        token_records += 1
        info = payload.get("info") or {}
        request = payload.get("usage")
        if isinstance(request, dict) and "total_tokens" in request:
            request_totals.update({key: int(request.get(key, 0) or 0) for key in CLASSES})
        candidates = (
            ("thread_token_usage", payload.get("thread_token_usage")),
            ("info.total_token_usage", info.get("total_token_usage")),
            ("turn_token_usage", payload.get("turn_token_usage")),
            ("info.last_token_usage", info.get("last_token_usage")),
        )
        for source, usage in candidates:
            if isinstance(usage, dict) and "total_tokens" in usage:
                latest = {key: int(usage.get(key, 0) or 0) for key in CLASSES}
                latest_source = source
                break
    if latest_source not in ("thread_token_usage", "info.total_token_usage") and request_totals:
        latest = {key: int(request_totals.get(key, 0)) for key in CLASSES}
        latest_source = "sum(payload.usage)"
    meta.update({"turns": turns, "usage": latest, "source": latest_source,
                 "token_records": token_records})
    return meta


def add(*usages):
    return {key: sum(int((usage or {}).get(key, 0)) for usage in usages) for key in CLASSES}


def subtract(current, baseline):
    return {key: int(current.get(key, 0)) - int((baseline or ZERO).get(key, 0))
            for key in CLASSES}


def load_ledger(path, args):
    """Read the milestone ledger. Milestone accounting is append-only.

    A renamed repair, a replacement worker, or a split gate reuses the same
    milestone ID and the same baseline; none of them replenish the allowance.
    """
    existing = {}
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            existing = json.load(handle)
    if not isinstance(existing, dict):
        raise ValueError("ledger is not a JSON object")
    milestone = args.milestone or existing.get("milestone_id")
    if existing.get("milestone_id") and milestone != existing["milestone_id"]:
        raise ValueError(
            "milestone_id {saved!r} already recorded in this ledger; reuse the "
            "stable ID so prior usage and failures stay attached to the milestone "
            "instead of resetting under a new name".format(
                saved=existing["milestone_id"]))
    ledger = {
        "milestone_id": milestone,
        "unit": existing.get("unit", "processed_tokens"),
        "allowance": existing.get("allowance"),
        "integration_reserve": existing.get("integration_reserve"),
        "repair_reserve": existing.get("repair_reserve"),
        "snapshots": list(existing.get("snapshots") or []),
        "failures": list(existing.get("failures") or []),
    }
    for field in ("allowance", "integration_reserve", "repair_reserve"):
        supplied = getattr(args, field)
        if supplied is None:
            continue
        if ledger[field] is None:
            ledger[field] = supplied
        elif supplied != ledger[field]:
            raise ValueError(
                "{field} is already {saved} for milestone {mid!r}; declare an "
                "allowance before dispatch and never resize it to fit a route "
                "that no longer fits".format(field=field, saved=ledger[field],
                                             mid=ledger["milestone_id"]))
    return ledger


def milestone_view(ledger, totals, forecast):
    """Compute spent, reserves, headroom, and the dispatch action state."""
    snapshots = ledger["snapshots"]
    baseline = snapshots[0]["tokens"] if snapshots else None
    previous = snapshots[-1]["tokens"] if snapshots else None
    spent = subtract(totals, baseline)["total_tokens"]
    reserves = sum(value for value in (ledger["integration_reserve"],
                                       ledger["repair_reserve"]) if value)
    allowance = ledger["allowance"]
    view = {
        "milestone_id": ledger["milestone_id"],
        "unit": ledger["unit"],
        "allowance": allowance,
        "spent": spent,
        "spent_includes": ["root", "worker", "guardian", "failed_attempts"],
        "integration_reserve": ledger["integration_reserve"],
        "repair_reserve": ledger["repair_reserve"],
        "recorded_failures": len(ledger["failures"]),
        "snapshots": len(snapshots),
        "baseline_total_tokens": (baseline or {}).get("total_tokens"),
        "incremental_since_last_snapshot": (
            subtract(totals, previous)["total_tokens"] if previous else None),
    }
    if allowance is None:
        view.update({"remaining": None, "headroom": None})
        return view, None
    remaining = allowance - spent
    headroom = remaining - reserves
    view.update({"remaining": remaining, "headroom": headroom})
    if headroom <= 0:
        decision, reason = BLOCKED, (
            "spent {spent} of {allowance} {unit}; the remaining balance does not "
            "clear the declared integration and repair reserves. Preserve current "
            "artifacts, return partial evidence, and report the resource blocker."
        ).format(spent=spent, allowance=allowance, unit=ledger["unit"])
    elif forecast is None:
        decision, reason = DIAGNOSTIC, (
            "headroom is {headroom} {unit} but the next assignment has no upper "
            "forecast. Only a separately bounded diagnostic step is eligible; full "
            "implementation is not."
        ).format(headroom=headroom, unit=ledger["unit"])
    elif forecast > headroom:
        decision, reason = REDUCE, (
            "forecast {forecast} exceeds headroom {headroom} {unit}. Reduce context, "
            "reframe the assignment, or choose a cheaper sufficient route; do not "
            "raise the allowance to fit."
        ).format(forecast=forecast, headroom=headroom, unit=ledger["unit"])
    else:
        decision, reason = PROCEED, (
            "forecast {forecast} fits headroom {headroom} {unit} with reserves "
            "unspent."
        ).format(forecast=forecast, headroom=headroom, unit=ledger["unit"])
    return view, {"decision": decision, "eligible": decision == PROCEED,
                  "forecast_upper": forecast, "reason": reason}


def emit(args, result, code):
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        roles = result.get("roles") or {}
        print("status={status} action={action} threads={threads} turns={turns} "
              "total_tokens={total} root={root} worker={worker} guardian={guardian}".format(
                  status=result.get("status", "unknown"),
                  action=result.get("action", UNAVAILABLE),
                  threads=result.get("threads", 0), turns=result.get("turns", 0),
                  total=result.get("tokens", {}).get("total_tokens", "unknown"),
                  root=(roles.get("root") or {}).get("total_tokens", "unknown"),
                  worker=(roles.get("worker") or {}).get("total_tokens", "unknown"),
                  guardian=(roles.get("guardian") or {}).get("total_tokens", "unknown")))
        if result.get("dispatch"):
            print("dispatch={decision} eligible={eligible} {reason}".format(
                decision=result["dispatch"]["decision"],
                eligible=result["dispatch"]["eligible"],
                reason=result["dispatch"]["reason"]))
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", help="explicit JSONL session path")
    parser.add_argument("--tree", action="store_true",
                        help="sum the selected session and every descendant thread")
    parser.add_argument("--cwd", default=os.path.expanduser("~/.codex"),
                        help="Codex directory or sessions root")
    parser.add_argument("--soft-limit", type=int, default=100000)
    parser.add_argument("--hard-limit", type=int, default=250000)
    parser.add_argument("--ledger", help="milestone ledger JSON path (append-only)")
    parser.add_argument("--milestone", help="stable milestone ID for the ledger")
    parser.add_argument("--snapshot", metavar="LABEL",
                        help="append the current totals to the ledger under LABEL")
    parser.add_argument("--allowance", type=int,
                        help="finite declared milestone allowance in the ledger unit")
    parser.add_argument("--integration-reserve", type=int, dest="integration_reserve")
    parser.add_argument("--repair-reserve", type=int, dest="repair_reserve")
    parser.add_argument("--forecast", default=None,
                        help="upper forecast for the next assignment, or 'unknown'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    forecast = None
    if args.forecast not in (None, "", "unknown"):
        try:
            forecast = int(args.forecast)
        except ValueError:
            parser.error("--forecast takes an integer or 'unknown'")
    root = os.path.abspath(args.cwd)
    sessions = os.path.join(root, "sessions") if os.path.isdir(os.path.join(root, "sessions")) else root
    explicit = os.path.abspath(args.session) if args.session else None
    if explicit and not args.tree:
        paths = [explicit]
    else:
        paths = glob.glob(os.path.join(sessions, "**", "*.jsonl"), recursive=True)
        if explicit and explicit not in paths:
            paths.append(explicit)
    data = {}
    for path in paths:
        row = inspect(path)
        if row["sid"]:
            row["path"] = path
            data[row["sid"]] = row
    if not data:
        return emit(args, {"status": "unknown", "action": UNAVAILABLE,
                           "error": "no session metadata found"}, EXITS[UNAVAILABLE])
    selected = next((sid for sid, row in data.items() if row["path"] == explicit), None) if explicit else None
    if selected is None:
        roots = [sid for sid, row in data.items() if not row["parent"]]
        selected = max(roots, key=lambda sid: data[sid].get("timestamp") or "") if roots else None
    if not selected:
        return emit(args, {"status": "unknown", "action": UNAVAILABLE,
                           "error": "no root session found"}, EXITS[UNAVAILABLE])
    selected_ids = {selected}
    if args.tree:
        by_parent = defaultdict(list)
        for sid, row in data.items():
            by_parent[row["parent"]].append(sid)
        pending = [selected]
        while pending:
            for child in by_parent[pending.pop()]:
                if child not in selected_ids:
                    selected_ids.add(child)
                    pending.append(child)

    roles = {sid: ("root" if sid == selected else data[sid]["role_hint"])
             for sid in selected_ids}
    thread_tokens = {sid: data[sid]["usage"] for sid in sorted(selected_ids)}
    root_tokens = data[selected]["usage"]
    missing = sorted(sid for sid in selected_ids if not data[sid]["usage"])
    role_totals = {}
    for role in ROLES:
        members = [sid for sid in selected_ids if roles[sid] == role]
        if not members:
            role_totals[role] = dict(ZERO)
        elif any(not data[sid]["usage"] for sid in members):
            role_totals[role] = None
        else:
            role_totals[role] = add(*[data[sid]["usage"] for sid in members])
    routing = {sid: {"role": roles[sid], "agent_path": data[sid]["agent_path"],
                     "effective_model": data[sid]["model"],
                     "effective_effort": data[sid]["effort"]}
               for sid in sorted(selected_ids)}
    base = {"session": selected, "session_path": data[selected]["path"],
            "threads": len(selected_ids),
            "thread_counts": {role: sum(1 for sid in selected_ids if roles[sid] == role)
                              for role in ROLES},
            "turns": sum(data[sid]["turns"] for sid in selected_ids),
            "token_records": sum(data[sid]["token_records"] for sid in selected_ids),
            "thread_sources": {sid: data[sid]["source"] for sid in sorted(selected_ids)},
            "thread_roles": {sid: roles[sid] for sid in sorted(selected_ids)},
            "routing": routing,
            "thread_tokens": thread_tokens, "root_tokens": root_tokens,
            "roles": role_totals,
            # Legacy field: requested workers only. Guardians are reported
            # separately under roles.guardian and stay inside `tokens`.
            "worker_tokens": role_totals["worker"],
            "enforcement": "dispatch_boundary_and_cooperative",
            "enforcement_note": ("reads completed records only; cannot cancel an "
                                 "in-flight response, cap an account, or predict "
                                 "the size of the next call"),
            "unavailable_fields": (["thread usage for: " + ", ".join(missing)]
                                   if missing else [])}
    if missing:
        base.update({"status": "unknown", "action": UNAVAILABLE,
                     "missing_threads": missing,
                     "error": "one or more threads have no token usage records"})
        return emit(args, base, EXITS[UNAVAILABLE])

    # Each session file reports cumulative usage for that thread. Sum one latest
    # snapshot per selected thread; never sum multiple cumulative records from a file.
    usage = {key: sum(data[sid]["usage"].get(key, 0) for sid in selected_ids)
             for key in CLASSES}
    total = usage["total_tokens"]
    status = "hard" if total >= args.hard_limit else "soft" if total >= args.soft_limit else "ok"
    base.update({"status": status, "tokens": usage,
                 "aggregate_source": (data[selected]["source"] if len(selected_ids) == 1
                                      else "sum(latest thread-local usage)"),
                 "soft_limit": args.soft_limit, "hard_limit": args.hard_limit})

    ledger = None
    if args.ledger or args.milestone or args.allowance is not None:
        try:
            ledger = load_ledger(args.ledger, args)
        except (OSError, ValueError) as error:
            base.update({"status": "invalid", "action": UNAVAILABLE,
                         "error": "ledger unusable: {0}".format(error)})
            return emit(args, base, EXITS[UNAVAILABLE])

    if ledger is None:
        action = {"hard": REDUCE, "soft": ADVISORY}.get(status, PROCEED)
        base["action"] = action
        base["action_note"] = (
            "below the default advisory checkpoint" if action == PROCEED else
            "default checkpoint reached with no declared milestone allowance; "
            "declare a finite allowance and an upper forecast before the next "
            "substantial dispatch")
        return emit(args, base, EXITS[action])

    view, dispatch = milestone_view(ledger, usage, forecast)
    if args.snapshot:
        ledger["snapshots"].append({
            "label": args.snapshot,
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tokens": usage,
            "by_role": {role: role_totals[role] for role in ROLES},
        })
        view, dispatch = milestone_view(ledger, usage, forecast)
        if args.ledger:
            with open(args.ledger, "w", encoding="utf-8") as handle:
                json.dump(ledger, handle, indent=2, sort_keys=True)
                handle.write("\n")
    base["milestone"] = view
    if dispatch is None:
        base["action"] = ADVISORY if status != "ok" else PROCEED
        base["action_note"] = ("milestone ledger declares no allowance; a missing "
                               "allowance is invalid, not unlimited")
        return emit(args, base, EXITS[base["action"]])
    base["dispatch"] = dispatch
    base["action"] = dispatch["decision"]
    return emit(args, base, EXITS[dispatch["decision"]])


if __name__ == "__main__":
    sys.exit(main())
