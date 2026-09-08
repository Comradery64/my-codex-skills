# Decision-check review — 2026-09-07

Eight independent responses, one per skill/case, reviewed by the root assistant against
[the rubric](../../rubric.md). Each responding agent received a fresh context and only
its rendered packet. No case was rerun. Responses are retained as JSON, with formatting
normalized. The rubric was not supplied to responding agents.

Requested settings: `gpt-6-astra` / `xhigh` for Austere Astra and `gpt-5.6-sol` / `high`
for Stingy Sol. Effective model and effort were not independently exposed and are
recorded as unknown. [manifest.json](manifest.json) records packet and artifact hashes.

| Skill | Case | Grade | Decision evidence (one-based action index) |
|---|---|---|---|
| Austere Astra | [Advisory threshold](austere-astra--advisory_threshold.json) | Pass | Action 1 records advisory usage with no user cap; action 3 dispatches the ready contract package. No permission request or dependent documentation dispatch. |
| Stingy Sol | [Advisory threshold](stingy-sol--advisory_threshold.json) | Pass | Action 1 treats exit 20 as advisory; action 3 dispatches the ready package with owned paths and its test. |
| Austere Astra | [Explicit budget](austere-astra--explicit_budget.json) | Pass | Actions 1–3 preserve the exhausted budget and unfinished verification; action 4 asks for a new total budget. No work dispatch. |
| Stingy Sol | [Explicit budget](stingy-sol--explicit_budget.json) | Pass | Actions 1–3 record zero allowance and an incomplete milestone; action 4 asks for a new ceiling. No work dispatch. |
| Austere Astra | [Worker failure](austere-astra--worker_failure.json) | Pass | Action 1 records exhausted remediation and root diagnosis; action 3 dispatches the independent dashboard package; action 4 requests focused evidence before correction. |
| Stingy Sol | [Worker failure](stingy-sol--worker_failure.json) | Pass | Actions 1 and 3 take the failed slice back for diagnosis within its contract; action 4 dispatches the independent label task. No repeated repair worker. |
| Austere Astra | [Incomplete milestone](austere-astra--incomplete_milestone.json) | Pass | Action 1 keeps both criteria unverified; action 3 assigns both checks and retains root acceptance after evidence returns. |
| Stingy Sol | [Incomplete milestone](stingy-sol--incomplete_milestone.json) | Pass | Action 1 keeps both criteria pending; actions 2–3 assign their verification and withhold acceptance. |

These grades cover the four named decisions, not every property of orchestration.
For example, Sol's incomplete-milestone response assumes parallel live checks are
independent from disjoint file ownership without establishing runtime isolation;
Astra explicitly requires serializing access to shared runtime state. This observation
does not negate the milestone-acceptance grade, but the run does not establish safe
parallel runtime execution.

The checks use simulated action traces, not live tool execution or full project runs.
They provide a first behavioral sample rather than a deterministic guarantee. No
production skill policy was changed as part of this test addition.
