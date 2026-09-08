---
name: austere-astra
description: Use GPT-6 Astra at xhigh as the root planner, architect, integrator, and reviewer while dynamically routing bounded work to capable lower-cost Codex models. Use for substantial implementation, debugging, research, migrations, and multi-phase work; skip small single-chain tasks.
---

# Austere Astra

Keep GPT-6 Astra at `xhigh` responsible for the decisions where intelligence compounds,
then delegate bounded work at the lowest model and effort that can meet an explicit
acceptance gate. The 10–30% comparative cost goal is aspirational; it never justifies
lowering Astra's root effort, weakening the requested result, or accepting bad work.

## Root authority and runtime truth

Astra owns framing, scout questions, evidence synthesis, architecture, tradeoffs,
phase boundaries, the evolving task graph, model and effort selection, integration,
acceptance, replanning, final review, and the user-facing answer. Workers never make
those project-level decisions and never delegate to other workers. Under an authorized
plan, Astra keeps planning, integration, and acceptance at the root while routing most
bounded exploration, implementation, and test execution to suitable lower-cost workers.

A skill cannot change the live root model or effort. Record requested and effective
values when the runtime exposes them, otherwise record `unknown`. Do not claim an
Astra-xhigh run when either value differs. Do not edit global configuration or silently
substitute Sol. `xhigh` is the requested root setting; do not raise it to `max` or
`ultra` merely because a higher setting exists.

## Shared operating references

Read [references/model-catalog.md](references/model-catalog.md) before routing workers.
It defines the shared model categories, capability boundaries, effort labels, and
selection criteria used by both orchestration skills.

Read [references/orchestration.md](references/orchestration.md) before a multi-task
delegation. It defines the adaptive dependency graph, parallel and waterfall criteria,
task board, handoff contract, acceptance loop, and collaboration-tool adapter.

Read [references/cost-model.md](references/cost-model.md) before estimating or reporting
cost. It defines the shared pricing snapshot, ledger, comparison rules, and limits of
the token guard.

## Adaptive execution

1. When present, Astra uses the existing authorized plan as the source of scope and
   acceptance; otherwise it frames the outcome, constraints, unknowns, risks, and
   first evidence needs.
2. Astra creates a provisional dependency graph and selects a model and effort for
   every ready task with a one-line reason.
3. Astra runs independent, safe tasks concurrently when the expected time or context
   benefit exceeds coordination cost. It sequences dependent, overlapping, or
   shared-state work as a waterfall.
4. After every return, Astra inspects the relevant evidence or diff, accepts or rejects
   the task, updates dependencies and assumptions, and decides the next wave. Evidence
   may change task ordering, grouping, or routing, but not the authorized plan's scope
   or acceptance criteria without user direction.
5. At each phase gate, Astra verifies integrated behavior and revises the remaining
   graph. Final acceptance covers the original outcome, not merely completed subtasks.

Delegate most bounded exploration, implementation, and test execution; Astra keeps
project judgment, integration, and acceptance. Assign each worker a coherent
deliverable with its verification, rather than splitting closely coupled fragments by
role. Parallel writers require disjoint file ownership, stable contracts, isolated
validation state, and independent acceptance. If these conditions fail, Astra
serializes the work. Reuse a related worker when its context remains useful; reroute
when its accumulated context is a burden. Astra diagnoses partial or stopped-short
returns; a worker's practical allowance exhaustion alone does not stop other ready,
authorized work. Keep handoffs lean and avoid duplicate exploration, unnecessary
fan-out, repeated large context transfers, and automatic retry swarms. For a plan-only
request, stop after delivering the plan. Once implementation is authorized, internal
task gates and skill-default checkpoints do not require repeated user permission.

## Context and verification

Use `fork_turns="none"` and a self-contained handoff. Keep raw exploration and logs in
task-scoped scratch artifacts when allowed. Workers return concise paths, findings,
confidence, verification results, and stopped-short status. Astra reviews focused
evidence and relevant diffs; it does not replay worker exploration or tests unless an
integration changed, evidence is invalid, or risk warrants it.

Allow one targeted remediation after a failed gate, missing evidence, or capability
failure. Astra diagnoses whether the problem is specification, environment, effort, or
model capability before changing the route. After another failure, Astra replans,
takes ownership, or reports the blocker. Never create an automatic retry swarm.

## Cost checkpoints

Before the first delegation, after each completed wave, and before a new phase, run
`scripts/token_budget_guard.py --session <root-session.jsonl> --tree --json` from this
skill directory when Codex session logs are available. Select the actual current root
session log, rather than relying on a newest-log default. Exit `10` at the default
100,000-token checkpoint and exit `20` at the default 250,000-token checkpoint are
advisory cost and routing reviews:
report observed usage, forecast, and remaining user budget when one exists; then
continue the authorized plan and its workers with the leanest suitable route. Exit `20`
retains its legacy `hard` telemetry label, but it creates no permission gate. Exit `30`
means aggregate usage is unavailable: report that uncertainty and continue
conservatively. The guard cannot stop an in-flight call and is not a platform spending
cap.

An explicit user hard budget is binding and supersedes these defaults. Honor it exactly,
reforecast against it, and never silently reset, reinterpret, or exceed it. Do not
request renewed budget approval to continue the authorized plan unless it would cross
that explicit hard budget. Treat material scope changes and other permission or safety
boundaries separately.

The target is 10–30% of a comparable all-Astra-xhigh run. Reforecast after every phase
and before an expensive escalation. Reduce duplicate context, unnecessary fan-out, and
oversized tasks when the forecast misses. Do not reduce authorized scope or spend more
merely to reach the lower bound. For each accepted milestone, use the shared ledger to
report available root versus worker usage, revisions, and coordination cost; distinguish
observed, estimated, and unknown values. These are decision records, never numeric
quotas or automated hard caps.

## Final acceptance

Astra maps every original acceptance criterion within each milestone to its owner, gate,
evidence, and final status. Continue until each is verified or has a concrete blocker;
a blocked item is never complete. Astra then checks integrated behavior, remaining
risks, routing deviations, and cost status. Preserve these decisions across compaction
and revalidate repository and task state when resuming.
