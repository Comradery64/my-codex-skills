# Shared verification contracts

This file is identical in `austere-astra` and `stingy-sol`. It governs *how* evidence
must be produced before an expensive acceptance stage, not what the project's gates
are. Correctness gates and user authorization are unchanged by anything here.

## Preflight before any long test

Require an executable end-to-end preflight before a long, load-bearing, or otherwise
expensive test. The preflight uses the **exact provider configuration and the
production request and render path** that the long test will exercise — not a component
harness that happens to import the same modules.

A failing preflight cancels the scheduled expensive stage automatically and returns the
minimal reproducer. It does not trigger a repair-and-retry loop at full test scale.

Component acceptance alone never establishes the integration path. Before a long test
runs, the preflight must show the whole chain producing a real, observable change:
source event → ingestion → projection → the surface a user actually sees. Basic
integration defects found *during* an expensive test are the most costly possible
place to find them.

## Coverage manifest before any measurement claim

Assign source event identifiers and define the measured population **before** running,
then report, alongside any latency figure:

| Field | Meaning |
|---|---|
| `population` | what was measured, e.g. per-session delivery vs global cadence |
| `sources` | the source event identifiers expected to contribute |
| `expected` | observations the defined population should produce |
| `observed` | observations actually recorded |
| `missing` | expected minus observed |
| `duplicate` | repeated deliveries of one source event |
| `coalesced` | source events merged into one delivery |
| `final_gap_ms` | time from the last source event to its final delivery |

Missing coverage, or a population different from the one specified, makes the result
incomplete or failed. Never compute a passing claim from the successful samples only:
ten observations out of six hundred expected advances is not a pass, and a
600-observation global sequence is not 15,000 per-session measurements. Distinguish
global cadence from individual-session delivery explicitly, in the manifest, every
time.

Validate the manifest mechanically before root review:

```sh
scripts/receipt_check.py --receipt <artifact>/receipt.json --require <id1,id2,...>
```

The validator rejects a latency figure reported with missing observations, counts that
do not reconcile, an undeclared population, and a long test with no passing preflight.
It checks completeness only.

## Invariant failure examples before implementation

Provide failure examples for consequential invariants *before* the coupled
implementation, and have the worker demonstrate the relevant failure and its fix with
focused tests. Keep a small reusable case list; do not open a broad investigation. If a
design cannot explain an invariant, resolve that architecture question first. A miss
found later consumes the existing repair reserve.

## Cheap checks derived from real defect classes

Derive the case list from the defect classes the project has actually produced. These
families recur in event-driven, multi-source, long-lived systems and are cheap to test
directly:

| Case family | Small check to require before expensive acceptance |
|---|---|
| Scoped identity links | Create a versioned provider/source link and verify that only an exactly resolved identity opens the intended target. |
| Coalesced vs separate continuations | Append evidence to a long same-ordinal message and again as a separate block; both must change the visible excerpt and its revision. A trailing empty or non-text block must not hide the update. |
| Watched roots | Configure only a fake source root, drain startup notifications, append content, and assert the exact new content and refresh arrive before periodic reconciliation. Replacing configuration must change the watched roots. |
| Measurement harness | Observe several sequential updates from every required source before the soak, and validate sample counts and final gaps in the harness output automatically. |
| Controller identity | Two path aliases for one database must contend on a single run lock. A resolved source association must be idempotent and must reject a different identity. |
| Command durability | Verify the durability setting and commit-before-dispatch ordering, inject interruption around dispatch, and require a conservative unknown or no-replay outcome. This is not a claim about every possible hardware power-loss behavior. |
| Lifecycle | A verified fake provider keeps its process identity across detach and reconnect; a foreign or replaced target receives no input and no stop. |

Run only the cases a change affects. A successful receipt stays reusable until code,
configuration, artifact identity, or the measured contract changes in a way that
invalidates it. Record that invalidating reason when it happens.

Testing orchestration policy does not require rerunning the project's expensive
suites: exercise tiny fixtures that contain the known defect instead.
