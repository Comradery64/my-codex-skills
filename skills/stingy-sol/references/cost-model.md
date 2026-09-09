# Shared cost model and milestone ledger

This file is identical in `austere-astra` and `stingy-sol`. It supports estimates,
dispatch decisions, and workflow checkpoints; it does not create an account spending
limit.

## What is being optimized

Optimize **total resources consumed to deliver an accepted milestone**, counting the
root, every worker, and every automatic guardian. Root share and the number of
delegated tasks are diagnostics, never evidence of savings. A falling root share
alongside a rising forecast total means the route is uneconomical, not austere.

Preserve the authorized functional outcome and its correctness gates. When the
economical route is uncertain, constrain the next discovery step instead of
authorizing an open-ended implementation. When no bounded route exists, return the
preserved result and the resource blocker rather than continuing merely because
scope remains authorized.

Budget control and permission are separate. A routing checkpoint changes how
authorized work proceeds; it does not ask the user to approve the same work again.
An explicit user hard limit always overrides these defaults.

## Declare the unit and the enforcement strength

Before substantial work, declare the measured unit and how strongly it is enforced.
Use a calibrated account metric when one is available; otherwise use an explicitly
labeled processed-token or model-response allowance as a resource proxy. Never convert
that proxy into weekly allowance or dollars.

Enforcement is one of:

- `runtime`: the platform itself refuses to exceed the limit;
- `dispatch_boundary`: an adapter evaluates eligibility before each dispatch;
- `cooperative`: only the worker's early-return instruction limits it.

Boundary checks cannot cap an already-running response. With no in-flight
cancellation and no per-call token limit, there is no hard spending cap; unknown
next-call size produces headroom and uncertainty, not a guarantee. Say which mode is
actually in force, and never promise enforcement the runtime does not provide.

Missing account telemetry is `unknown`. It never becomes zero cost, unlimited
execution, or a fabricated percentage remaining. If neither a task forecast nor a
reliable allowance exists, take only a small declared diagnostic step, then forecast
the next milestone from what it returned.

## Pricing snapshot

Refresh prices before making a current dollar claim. Standard API text prices captured
2026-09-07, USD per 1M tokens:

| Model | Input | Cached input | Output |
|---|---:|---:|---:|
| GPT-6 Astra | $10.00 | $1.00 | $50.00 |
| GPT-5.6 Sol | $4.00 | $0.40 | $20.00 |
| GPT-5.6 Terra | $2.00 | $0.20 | $12.00 |
| GPT-5.6 Luna | $0.20 | $0.02 | $1.20 |

Astra cache writes are $12.50 per 1M tokens. Astra prompts above 272K input tokens
apply 2x input and cache rates and 1.5x output rates to the full request. Service tier,
batch processing, long-context rules, cache writes, tools, and account-specific terms
can change the total. Sources: [OpenAI model catalog](https://developers.openai.com/api/docs/models)
and [Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra).
API estimates are not a ChatGPT subscription or credit-balance statement.

## Ledger

For the root and every worker, record when the measurement source exposes the needed
breakdown:

- task ID plus requested and effective model and effort;
- observed or estimated input, cached input, cache-write, and output tokens;
- whether reasoning tokens are already included in output totals;
- tool or other metered costs;
- the measurement source and any unavailable fields;
- retries and repeated context.

Roles are accounted separately and reconciled once: **root**, **requested workers**,
and **automatic guardians**. Guardians are runtime approval actors, not workers the
root chose to spawn. Folding them into worker totals hides real overhead; omitting
them understates the tree. Include them in both total and incremental forecasts, and
estimate their overhead from comparable local operations when attribution is
unavailable — marking it unknown rather than zero. Legitimate safeguards stay enabled;
never evade review by switching tools or models.

For the run, also record cost per accepted milestone, per-role usage where observable,
accepted tasks and revisions, and coordination overhead when it is observable. Do not
manufacture per-thread figures or overhead precision from an aggregate. Treat
coordination overhead as a subset of recorded cost, not an additional charge. Include
failed attempts in their milestone's cost and report unfinished work separately; do not
hide its cost by counting only successes. Never convert an aggregate token total
directly into a dollar total without the applicable model, billing class, and
measurement assumptions.

Compute model cost from non-overlapping billing classes:

`cost = Σ(tokens in class × matched class rate) / 1,000,000 + other metered costs`

Do not add reasoning tokens again when the provider includes them in output. Do not
record missing usage as zero. Distinguish observed, estimated, and unknown amounts.
Usage telemetry that zero-fills omitted token classes is not proof that those billing
classes were measured as zero; cost estimates require source coverage for the billing
classes they use.

## Stable milestone accounting

Keep one **stable milestone ID** with a failure and correction ledger across every
worker. Permit one targeted remediation for a failed criterion; a repeated failure or
a repeated incomplete return requires diagnosis and a revised route. All attempts
consume the same milestone allowance. Renaming a repair, spawning a replacement
worker, or splitting a gate does not erase prior usage or failures, and replanning
never replenishes the allowance. A second failure does not start an automatic retry
chain.

Track responses and usage across a worker's entire history, not just its latest
assignment. Reuse a worker only when reuse is cheaper than a concise fresh
continuation; when a history reaches its recorded review threshold, or repeated
returns start to dominate the work, estimate compact handoff versus reuse and take
the lower sufficient cost. Rotating workers does not reset milestone accounting, and
a fresh worker receives accepted evidence rather than instructions to rederive it.

## Operational contract

Use these fields inside the existing rolling task artifact. Do not spawn a separate
narrative document per field or checkpoint.

```yaml
milestone_id: stable_across_repairs_and_worker_changes
outcome: one_reviewable_result
measurement:
  unit: processed_tokens_or_model_responses_or_calibrated_account_units
  enforcement: runtime_or_dispatch_boundary_or_cooperative
  unavailable_fields: []
allowance:
  total: finite_declared_value
  spent: includes_root_workers_guardians_and_failed_attempts
  integration_reserve: declared_value
  repair_reserve: declared_value
forecast:
  next_assignment_upper: estimate_or_unknown
  basis: comparable_evidence_or_bounded_diagnostic
assignment:
  deliverable: observable_result
  model_and_effort: explicit_with_reason
  owns: named_files_or_state
  return_threshold: finite_declared_value
  no_expansion: true
  verification: exact_command_or_artifact_contract
criteria:
  - id: stable_criterion_id
    status: pass_fail_or_unverified
    evidence: path_or_precise_blocker
```

Every numeric allowance field uses the one declared unit, and the values are chosen
before dispatch from the task and available evidence. A missing allowance is invalid,
not unlimited. No universal token budget is substantiated here.

When no forecast is available, a conservative **experimental diagnostic default** is
at most four worker model responses plus one compact root decision. That is a proposed
pilot bound, not a measured optimum and not a weekly-quota guarantee. It still sits
under a cumulative milestone allowance, so repeated "small pilots" cannot become
another unlimited run. A long external program does not need to consume repeated model
responses while it runs.

## Dispatch eligibility

A dispatch is eligible only when dependencies and permissions are satisfied, the
assignment is bounded, and its upper forecast plus the unspent reserves fits the
remaining milestone allowance:

```text
remaining = allowance - spent
headroom  = remaining - (integration_reserve + repair_reserve)
```

| Condition | Action state |
|---|---|
| `forecast <= headroom` | `proceed_within_allowance` |
| `forecast > headroom` and `headroom > 0` | `reduce_or_reframe` |
| forecast unknown and `headroom > 0` | `bounded_diagnostic` only |
| `headroom <= 0` | `resource_blocked` |
| aggregate usage unavailable | `aggregate_unavailable` |

An unknown forecast permits the separately bounded diagnostic, never a full
implementation. Never reset or raise the allowance to make a route fit. Actual
permissions and user instructions remain authoritative. When telemetry is available an
adapter computes this from the ledger; when it is not, the worker's early-return
instruction is cooperative and must be labeled that way.

## Token guard

Run `scripts/token_budget_guard.py --tree --json --session <active-root-session>` when
session logs are available. Supplying the active root session is required for correct
attribution: the default newest root can select an unrelated concurrent run. The guard
sums each selected thread's latest cumulative usage once and classifies each thread
from session metadata, so `roles.root`, `roles.worker`, and `roles.guardian` reconcile
to `tokens` exactly once. `worker_tokens` remains the requested-worker subtotal only.
It does not infer models, prices, or billing classes. If a selected thread lacks usage
the aggregate is `unknown` rather than a misleading partial total. The breakdown
remains telemetry, not proof that omitted billing fields cost zero.

Attach a milestone ledger to get incremental attribution and an explicit dispatch
decision instead of a bare number:

```sh
scripts/token_budget_guard.py --session <root-session.jsonl> --tree --json \
  --ledger <artifact>/milestone.json --milestone <stable-id> \
  --allowance <N> --integration-reserve <N> --repair-reserve <N> \
  --forecast <N|unknown>
```

Add `--snapshot <label>` at a milestone boundary to append the current totals; later
runs report `incremental_since_last_snapshot`, which is what a reused worker's next
assignment actually costs. Until a baseline snapshot exists, `spent` conservatively
equals the whole selected tree. The ledger is append-only: it refuses a changed
`milestone_id` and refuses to resize an allowance that is already declared.

Exit codes are action states, not just severities:

- exit `0`: `proceed_within_allowance` (or below the 100,000-token advisory checkpoint);
- exit `10`: `advisory_review` at 100,000 tokens with no declared allowance;
- exit `20`: `reduce_or_reframe` — at 250,000 tokens with no declared allowance
  (legacy telemetry label `hard`), or a forecast exceeding headroom;
- exit `25`: `bounded_diagnostic` — headroom exists but the next assignment is unforecast;
- exit `30`: `aggregate_unavailable`, including an unusable ledger;
- exit `40`: `resource_blocked` — reserves are not clear of the remaining allowance.

Every result carries an `action`, so a threshold produces an instruction rather than a
report. Repeated warnings without a changed route are a policy failure. The script
reads completed log records, cannot predict the size of the next worker, and cannot
stop an in-flight call. Leave enough headroom for root integration and one bounded
revision.

## Comparisons and targets

Use a matched prior run or an authorized controlled benchmark with the same outcome,
scope, quality gate, and pricing. Do not run a second expensive build solely to create
a baseline. Repricing the mixed run's token trace at one model's rates is a routing
proxy, not a measured baseline, because different models and efforts can use different
numbers of tokens and produce different quality.

For a proxy, calculate `mixed estimated cost / baseline estimated cost` and disclose
all assumptions. Keep a comparative percentage out of acceptance unless scope, quality,
accounting classes, and a matched baseline are all available; the fallback is an
absolute milestone allowance, a truthful forecast, and acceptance evidence, never an
invented savings percentage. Targets belong to the parent skill. They never justify
forced model quotas, weakened gates, hidden scope cuts, or extra spending to reach a
lower bound.
