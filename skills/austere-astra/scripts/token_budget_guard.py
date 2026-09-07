#!/usr/bin/env python3
"""Read Codex JSONL token totals without exposing conversation content."""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

CLASSES = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
           "output_tokens", "reasoning_output_tokens", "total_tokens")


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


def inspect(path):
    sid = parent = timestamp = None
    turns = token_records = 0
    latest = latest_source = None
    request_totals = Counter()
    for obj in records(path):
        payload = obj.get("payload") or {}
        if obj.get("type") == "session_meta":
            sid = payload.get("id")
            parent = payload.get("parent_thread_id")
            timestamp = payload.get("timestamp") or obj.get("timestamp")
        if obj.get("type") == "turn_context":
            turns += 1
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
    return sid, parent, timestamp, turns, latest, latest_source, token_records


def emit(args, result, code):
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("status={status} threads={threads} turns={turns} total_tokens={total}".format(
            status=result.get("status", "unknown"), threads=result.get("threads", 0),
            turns=result.get("turns", 0),
            total=result.get("tokens", {}).get("total_tokens", "unknown")))
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", help="explicit JSONL session path")
    parser.add_argument("--tree", action="store_true", help="include descendant session counts")
    parser.add_argument("--cwd", default=os.path.expanduser("~/.codex"),
                        help="Codex directory or sessions root")
    parser.add_argument("--soft-limit", type=int, default=100000)
    parser.add_argument("--hard-limit", type=int, default=250000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
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
        sid, parent, timestamp, turns, usage, source, count = inspect(path)
        if sid:
            data[sid] = {"path": path, "parent": parent, "timestamp": timestamp,
                         "turns": turns, "usage": usage, "source": source,
                         "token_records": count}
    if not data:
        return emit(args, {"status": "unknown", "error": "no session metadata found"}, 30)
    selected = next((sid for sid, row in data.items() if row["path"] == explicit), None) if explicit else None
    if selected is None:
        roots = [sid for sid, row in data.items() if not row["parent"]]
        selected = max(roots, key=lambda sid: data[sid].get("timestamp") or "") if roots else None
    if not selected:
        return emit(args, {"status": "unknown", "error": "no root session found"}, 30)
    by_parent = defaultdict(list)
    for sid, row in data.items():
        by_parent[row["parent"]].append(sid)
    tree, pending = {selected}, [selected]
    while pending:
        for child in by_parent[pending.pop()]:
            if child not in tree:
                tree.add(child)
                pending.append(child)
    usage = data[selected]["usage"]
    if not usage:
        return emit(args, {"status": "unknown", "session": selected,
                           "error": "no token usage records found"}, 30)
    total = usage["total_tokens"]
    status = "hard" if total >= args.hard_limit else "soft" if total >= args.soft_limit else "ok"
    result = {"status": status, "session": selected, "session_path": data[selected]["path"],
              "threads": len(tree), "turns": data[selected]["turns"],
              "token_records": data[selected]["token_records"],
              "aggregate_source": data[selected]["source"], "tokens": usage,
              "soft_limit": args.soft_limit, "hard_limit": args.hard_limit}
    return emit(args, result, 20 if status == "hard" else 10 if status == "soft" else 0)


if __name__ == "__main__":
    sys.exit(main())
