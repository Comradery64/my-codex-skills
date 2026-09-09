---
name: austere-astra
description: Use GPT-6 Astra at xhigh as the root planner, architect, integrator, and reviewer while dynamically routing bounded work to capable lower-cost Codex models. Use for substantial implementation, debugging, research, migrations, and multi-phase work; skip small single-chain tasks.
---

# Austere Astra

Keep GPT-6 Astra at `xhigh` responsible for the decisions where intelligence compounds,
then delegate bounded work at the lowest model and effort that can meet an explicit
acceptance gate.

## What austerity means here

Optimize **total resources consumed to deliver an accepted milestone**, counting the
root, every worker, and every automatic guardian. Root share and the number of
delegated tasks are diagnostics, never evidence of savings: a falling root share
beside a rising forecast total means the route is uneconomical. Never announce savings
from a routing split.

Preserve the authorized outcome and its correctness gates. When the economical route
is uncertain, constrain the next discovery step rather than authorizing an open-ended
implementation. When no bounded route exists, return the preserved result and the
resource blocker instead of continuing because scope remains authorized.

## Root authority and runtime truth

Astra owns framing, scout questions, evidence synthesis, architecture, tradeoffs,
phase boundaries, the evolving task graph, model and effort selection, integration,
acceptance, replanning, final review, and the user-facing answer. Workers never make
those project-level decisions and never delegate to other workers. Under an authorized
plan, Astra keeps planning, integration, and acceptance at the root while routing most
bounded exploration, implementation, and test execution to suitable lower-cost workers.

A skill cannot change the live root model or effort. Record requested and effective
values once, with the relevant evidence, when the runtime exposes them; otherwise
record `unknown`. Do not claim an Astra-xhigh run when either value differs, and do not
relabel `high` as `xhigh`. Do not edit global configuration or silently substitute Sol.
`xhigh` is the requested root setting; do not raise it to `max` or `ultra` merely
because a higher setting exists, and never prescribe raising effort as a cost repair.
Configuration validity and resource efficiency are separate questions.

## Shared operating references

Read [references/model-catalog.md](references/model-catalog.md) before routing workers.
It defines the shared model categories, capability boundaries, effort labels, and
selection criteria used by both orchestration skills.

Read [references/orchestration.md](references/orchestration.md) before a multi-task
delegation. It defines the adaptive dependency graph, parallel and waterfall criteria,
task board, bounded-assignment and complete-receipt contracts, acceptance loop, and
collaboration-tool adapter.

Read [references/cost-model.md](references/cost-model.md) before estimating or reporting
cost. It defines the shared pricing snapshot, milestone ledger, dispatch eligibility,
comparison rules, and limits of the token guard.

Read [references/verification-contracts.md](references/verification-contracts.md) before
scheduling a long or expensive test, or claiming a measurement. It defines the preflight
requirement, coverage manifest, and invariant case list.

## Adaptive execution

1. When present, Astra uses the existing authorized plan as the source of scope and
   acceptance; otherwise it frames the outcome, constraints, unknowns, risks, and
   first evidence needs.
2. Astra declares the milestone ID, measured unit, enforcement mode, allowance, and
   reserves before substantial work, then selects a model and effort for every ready
   task with a one-line reason.
3. Astra runs independent, safe tasks concurrently when the expected time or context
   benefit exceeds coordination cost. It sequences dependent, overlapping, or
   shared-state work as a waterfall.
4. After every return, Astra validates receipt completeness, inspects the relevant
   evidence or diff, accepts or rejects the task, updates dependencies and assumptions,
   and decides the next wave. Evidence may change task ordering, grouping, or routing,
   but not the authorized plan's scope or acceptance criteria without user direction.
5. At each phase gate, Astra verifies integrated behavior, closes the milestone with an
   accepted artifact or an explicit partial state, and checks the next phase's forecast
   and reserves before entering it. Final acceptance covers the original outcome, not
   merely completed subtasks.

Delegate most bounded exploration, implementation, and test execution; Astra keeps
project judgment, integration, and acceptance. Assign each worker a coherent
deliverable with its verification, rather than splitting closely coupled fragments by
role. Every assignment names one observable deliverable, the state it owns, a finite
allowance, an early-return condition, an exact verification command, and the retained
integration reserve; a subject bound is not a consumption bound. Parallel writers
require disjoint file ownership, stable contracts, isolated validation state, and
independent acceptance. If these conditions fail, Astra serializes the work. Reuse a
worker only while reuse is cheaper than a concise fresh continuation, judged from its
whole recorded history. Astra diagnoses partial or stopped-short returns; a worker's
allowance exhaustion alone does not stop other ready, authorized work. Keep handoffs
lean and avoid duplicate exploration, unnecessary fan-out, repeated large context
transfers, and automatic retry swarms. For a plan-only request, stop after delivering
the plan. Once implementation is authorized, internal task gates and skill-default
checkpoints do not require repeated user permission.

## Context and verification

Use `fork_turns="none"` and a self-contained handoff. Keep raw exploration and logs in
task-scoped scratch artifacts when allowed. Workers return concise paths, findings,
confidence, verification results, every stable criterion ID as pass/fail/unverified
with an artifact or precise blocker, and stopped-short status. A receipt that omits a
criterion is incomplete, not a phase pass; request only the missing evidence, charged
to the existing milestone allowance. Astra reviews focused evidence and relevant diffs;
it does not replay worker exploration or tests unless an integration changed, evidence
is invalid, or risk warrants it.

Require an executable end-to-end preflight on the production path before any long test,
and a coverage manifest before any measurement claim. A failing preflight cancels the
expensive stage. Provide failure examples for consequential invariants before the
coupled implementation.

Allow one targeted remediation after a failed gate, missing evidence, or capability
failure. Astra diagnoses whether the problem is specification, environment, effort, or
model capability before changing the route. After another failure, Astra replans,
takes ownership, or reports the blocker. Renaming a repair or replacing a worker does
not reset milestone accounting. Never create an automatic retry swarm.

## Cost checkpoints

Before the first delegation, after each completed wave, and before a new phase, run
`scripts/token_budget_guard.py --session <root-session.jsonl> --tree --json` from this
skill directory when Codex session logs are available, adding
`--ledger <artifact>/milestone.json --milestone <stable-id> --forecast <N|unknown>`
once a milestone allowance is declared. Select the actual current root session log,
rather than relying on a newest-log default.

Every result carries an action state, so a threshold produces an instruction rather
than a report:

- exit `0` — proceed within the allowance, or below the default 100,000-token checkpoint;
- exit `10` — advisory review at the default 100,000-token checkpoint, with no declared allowance;
- exit `20` — reduce or reframe: the default 250,000-token checkpoint with no declared
  allowance (legacy `hard` telemetry label), or a forecast exceeding headroom;
- exit `25` — bounded diagnostic only: headroom exists but the next assignment is unforecast;
- exit `30` — aggregate usage unavailable: report the uncertainty and continue conservatively;
- exit `40` — resource blocked: preserve artifacts, return partial evidence, report the blocker.

On `reduce_or_reframe` or worse, stop dispatching new substantial work and permit one
bounded routing decision; resume only with a route that fits the existing allowance.
Never reset or resize the allowance to make a route fit, and never progress from
repeated warnings into another large phase on reporting alone. None of these states is
a permission gate on already-authorized work. The guard cannot stop an in-flight call
and is not a platform spending cap; report the enforcement mode it actually provides.

An explicit user hard budget is binding and supersedes these defaults. Honor it exactly,
reforecast against it, and never silently reset, reinterpret, or exceed it. Do not
request renewed budget approval to continue the authorized plan unless it would cross
that explicit hard budget. Treat material scope changes and other permission or safety
boundaries separately.

When the user corrects austerity, persist an operating-policy delta and state the
concrete scheduling, scope, context, or allowance change in one short update. "Keep
this worker running" preserves that worker while narrowing subsequent dispatch; a clear
stop stops active work; a cost complaint triggers resource triage before another
substantial launch, not abandonment of useful work. Do not dispatch a new large
assignment under unchanged bounds after a correction, and do not answer one with
another usage split.

The 10–30% comparative goal against an all-Astra-xhigh run is aspirational and stays
out of acceptance unless scope, quality, accounting classes, and a matched baseline are
all available; the fallback is an absolute milestone allowance, a truthful forecast, and
acceptance evidence. It never justifies lowering Astra's root effort, weakening the
requested result, accepting bad work, forcing model quotas, or a second expensive build
run only to supply a baseline. For each accepted milestone, report root, worker, and
guardian usage that reconciles once, plus revisions and coordination cost; distinguish
observed, estimated, and unknown values. These are decision records, never numeric
quotas or automated hard caps.

## Final acceptance

Astra maps every original acceptance criterion within each milestone to its stable ID,
owner, gate, evidence, and final status. Continue until each is verified or has a
concrete blocker; a blocked item is never complete. Astra then checks integrated
behavior, remaining risks, routing deviations, and cost status against the milestone
ledger. Preserve these decisions across compaction and revalidate repository and task
state when resuming.
