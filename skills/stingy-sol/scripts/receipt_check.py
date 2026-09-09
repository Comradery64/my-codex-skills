#!/usr/bin/env python3
"""Validate an acceptance receipt for completeness, never for correctness.

Three checks, all deterministic and all cheap:

  1. criterion completeness -- every stable criterion ID the assignment declared
     comes back as pass / fail / unverified with an artifact or a precise
     blocker. A receipt that omits an ID is incomplete, not a phase pass.
  2. coverage manifest -- a measured population, source identifiers, and
     expected / observed / missing / duplicate / coalesced / final-gap counts
     accompany any latency claim. A latency figure computed from successful
     samples only is rejected.
  3. preflight ordering -- a reported long or expensive test requires a passing
     executable preflight on the same production path.

Passing this check means the receipt is reviewable. It does not mean the work is
right: the root still inspects the evidence.
"""
import argparse
import json
import sys

STATUSES = ("pass", "fail", "unverified")
COVERAGE_FIELDS = ("expected", "observed", "missing", "duplicate", "coalesced",
                   "final_gap_ms")
COMPLETE, INCOMPLETE, INVALID, UNUSABLE = "complete", "incomplete", "invalid_claim", "unusable"
EXITS = {COMPLETE: 0, INCOMPLETE: 10, INVALID: 20, UNUSABLE: 2}


def check_criteria(receipt, required):
    problems = []
    entries = receipt.get("criteria")
    if not isinstance(entries, list):
        return [(INCOMPLETE, "receipt has no `criteria` list")], {}
    seen = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not entry.get("id"):
            problems.append((INCOMPLETE, "criteria[%d] has no stable id" % index))
            continue
        cid = entry["id"]
        if cid in seen:
            problems.append((INVALID, "criterion %r reported twice" % cid))
        status = entry.get("status")
        if status not in STATUSES:
            problems.append((INCOMPLETE, "criterion %r status %r is not one of %s"
                             % (cid, status, "/".join(STATUSES))))
        evidence, blocker = entry.get("evidence"), entry.get("blocker")
        if status == "pass" and not evidence:
            problems.append((INCOMPLETE, "criterion %r claims pass with no evidence" % cid))
        if status in ("fail", "unverified") and not (evidence or blocker):
            problems.append((INCOMPLETE, "criterion %r is %s with no evidence or precise blocker"
                             % (cid, status)))
        seen[cid] = status
    for cid in required:
        if cid not in seen:
            problems.append((INCOMPLETE, "required criterion %r is absent from the receipt" % cid))
    return problems, seen


def check_coverage(receipt):
    coverage = receipt.get("coverage")
    if coverage is None:
        return []
    if not isinstance(coverage, dict):
        return [(UNUSABLE, "`coverage` is not an object")]
    problems = []
    if not coverage.get("population"):
        problems.append((INCOMPLETE, "coverage has no declared measured population; a "
                                     "global cadence is not per-session delivery"))
    sources = coverage.get("sources")
    if not isinstance(sources, list) or not sources:
        problems.append((INCOMPLETE, "coverage has no source event identifiers"))
    counts = {}
    for field in COVERAGE_FIELDS:
        value = coverage.get(field)
        if not isinstance(value, int) or isinstance(value, bool):
            problems.append((INCOMPLETE, "coverage.%s is missing; record it as a count, "
                                         "not an omission" % field))
        else:
            counts[field] = value
    if len(counts) == len(COVERAGE_FIELDS):
        if counts["observed"] + counts["missing"] != counts["expected"]:
            problems.append((INVALID, "coverage does not reconcile: observed %d + missing %d "
                                      "!= expected %d"
                             % (counts["observed"], counts["missing"], counts["expected"])))
        if coverage.get("latency") and counts["missing"] > 0:
            problems.append((INVALID, "a latency figure is reported with %d missing "
                                      "observations; that describes the successful samples, "
                                      "not the measured population" % counts["missing"]))
    return problems


def check_preflight(receipt):
    if not receipt.get("long_test"):
        return []
    preflight = receipt.get("preflight")
    if not isinstance(preflight, dict):
        return [(INVALID, "a long test is reported with no executable preflight on the "
                          "same production path")]
    if preflight.get("status") != "pass":
        return [(INVALID, "preflight status %r does not permit a long test; cancel the "
                          "expensive stage and return the minimal reproducer"
                 % preflight.get("status"))]
    if not (preflight.get("command") or preflight.get("evidence")):
        return [(INCOMPLETE, "preflight records no command or artifact")]
    return []


def check_claim(receipt, seen):
    claim = receipt.get("claim")
    if claim is None:
        return [(INCOMPLETE, "receipt declares no `claim` of accepted / partial / blocked")]
    if claim not in ("accepted", "partial", "blocked"):
        return [(UNUSABLE, "claim %r is not accepted / partial / blocked" % claim)]
    if claim != "accepted":
        return []
    open_ids = sorted(cid for cid, status in seen.items() if status != "pass")
    if open_ids:
        return [(INVALID, "claim is `accepted` while these criteria are not pass: %s"
                 % ", ".join(open_ids))]
    return []


def validate(receipt, required):
    if not isinstance(receipt, dict):
        return UNUSABLE, [(UNUSABLE, "receipt is not a JSON object")]
    declared = receipt.get("required_criteria")
    ids = list(required) if required else (declared if isinstance(declared, list) else [])
    if not ids:
        return UNUSABLE, [(UNUSABLE, "no required criterion IDs supplied by --require or "
                                     "`required_criteria`; completeness is undefined "
                                     "without the assignment's stable IDs")]
    problems, seen = check_criteria(receipt, ids)
    problems += check_coverage(receipt)
    problems += check_preflight(receipt)
    problems += check_claim(receipt, seen)
    for level in (UNUSABLE, INVALID, INCOMPLETE):
        if any(kind == level for kind, _ in problems):
            return level, problems
    return COMPLETE, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--receipt", required=True, help="receipt JSON path, or - for stdin")
    parser.add_argument("--require", default="",
                        help="comma-separated stable criterion IDs the assignment declared")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    required = [cid.strip() for cid in args.require.split(",") if cid.strip()]
    try:
        text = sys.stdin.read() if args.receipt == "-" else open(
            args.receipt, encoding="utf-8").read()
        receipt = json.loads(text)
    except (OSError, ValueError) as error:
        result = {"status": UNUSABLE, "problems": ["receipt unreadable: %s" % error]}
        print(json.dumps(result, sort_keys=True) if args.json else
              "status=%s %s" % (UNUSABLE, result["problems"][0]))
        return EXITS[UNUSABLE]
    status, problems = validate(receipt, required)
    result = {"status": status,
              "milestone_id": receipt.get("milestone_id") if isinstance(receipt, dict) else None,
              "checked": ["criterion_completeness", "coverage_manifest", "preflight_ordering",
                          "claim_consistency"],
              "note": "completeness only; the root still reviews correctness",
              "problems": ["%s: %s" % (kind, message) for kind, message in problems]}
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("status=%s problems=%d" % (status, len(problems)))
        for kind, message in problems:
            print("  %s: %s" % (kind, message))
    return EXITS[status]


if __name__ == "__main__":
    sys.exit(main())
