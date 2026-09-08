---
name: stingy-sol
description: Use GPT-5.6 Sol as the root planner, integrator, and reviewer while dynamically routing bounded work to GPT-5.6 Terra or Luna at the lowest sufficient effort. Use for substantial implementation, exploration, research, testing, debugging, and migrations; skip small single-chain tasks.
---

# Stingy Sol

Keep GPT-5.6 Sol responsible for project-level judgment. Delegate bounded work to the
least expensive capable model at the lowest sufficient effort, then require evidence
before accepting it.

## Root authority and runtime truth

Sol owns framing, decomposition, architecture, tradeoffs, the evolving task graph,
model and effort selection, shared-state coordination, integration, conflict
resolution, acceptance, replanning, final review, and the user-facing answer. Workers
never make those project-level decisions and never delegate to other workers. Under an
authorized plan, Sol retains this judgment while routing most bounded exploration,
implementation, and test execution to Terra or Luna.

Apply this policy when GPT-5.6 Sol is the root. A skill cannot change the live root
model or reasoning effort. Record requested and effective values when exposed,
otherwise record `unknown`; never claim routing that did not occur. Do not edit global
configuration. Do not combine this policy with an active exhaustive or automatic
delegation mode that would override its cost controls.

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

1. When present, Sol uses the existing authorized plan as the source of scope and
   acceptance; otherwise it frames the outcome, constraints, unknowns, risks, and
   first evidence needs.
2. Sol creates a provisional dependency graph and assigns an explicit model and effort
   to every ready task with a one-line reason.
3. Sol runs independent, safe tasks concurrently when speed or context isolation is
   worth the coordination cost. It uses waterfall sequencing for dependencies,
   overlapping ownership, shared mutable state, or unresolved contracts.
4. After every return, Sol checks the relevant evidence or diff, accepts or rejects the
   task, revises assumptions and dependencies, and selects the next wave. Findings may
   expose new work, collapse planned work, or force serialization.
5. At each phase gate, Sol verifies integrated behavior and refines what remains. Final
   acceptance covers the original outcome rather than a collection of task reports.

Delegate most bounded execution while Sol retains project judgment. Assign each worker
a coherent deliverable with its verification, rather than splitting closely coupled
fragments by role. Parallel writers require disjoint file ownership, stable contracts,
isolated validation state, and independent acceptance. If any condition fails, Sol
serializes the work. Reuse a related worker when its context remains useful; reroute
when its accumulated context is a burden. Sol diagnoses partial or stopped-short
returns; a worker's practical allowance exhaustion alone does not stop other ready,
authorized work. Small, tightly coupled work may stay with Sol when delegation overhead
would exceed its benefit. For a plan-only request, stop after the plan. Once
implementation is authorized, internal task gates and skill-default checkpoints do not
require repeated user permission.

## Context and verification

Use `fork_turns="none"` and a self-contained handoff for every worker. Put noisy output
in task-scoped scratch artifacts when permitted. Workers return concise paths,
findings, confidence, verification results, and stopped-short status. Sol reviews
focused evidence and relevant diffs; it does not replay worker exploration or tests
unless an integration changed, evidence is invalid, or risk warrants it.

Permit one targeted remediation after a failed gate, missing evidence, or visible
capability failure. Diagnose specification, environment, effort, and model choice
before rerouting. Raise effort when more depth is needed; raise model tier when the
task exceeded capability. After another failure, Sol owns the slice or reports the
blocker. Do not start an automatic gap-filling round after successful synthesis.

## Cost checkpoints

Before the first delegation, after each completed wave, and before a new phase, run
`scripts/token_budget_guard.py --session <root-session.jsonl> --tree --json` from this
skill directory when Codex session logs are available. Select the actual current root
session log, rather than relying on a newest-log default. Exit `10` at the default
100,000-token checkpoint and exit `20` at the default 250,000-token checkpoint are
advisory cost and routing reviews:
report observed usage, forecast, and remaining user budget when one exists, then
continue the authorized plan with the leanest suitable route. Exit `20` retains its
legacy `hard` telemetry label, but it creates no permission gate. Exit `30` means
aggregate usage is unavailable: report that uncertainty and continue conservatively.
The guard cannot stop an in-flight call and is not a platform spending cap.

An explicit user hard budget is binding and supersedes these defaults. Honor it exactly,
reforecast against it, and never silently reset, reinterpret, or exceed it. Do not
request renewed budget approval to continue the authorized plan unless it would cross
that explicit hard budget. Treat material scope changes and other permission or safety
boundaries separately.

Use the ledger to prevent cheap-agent fan-out from becoming an expensive run. Reuse
accepted contracts, avoid repeated context, and reserve capacity for root integration
and one remediation. For each accepted milestone, report available root versus worker
usage, revisions, and coordination cost; distinguish observed, estimated, and unknown
values. These are decision records, never numeric quotas or automated hard caps.

## Planning and final acceptance

For a multi-phase plan, include dependencies, proposed parallel waves, required
waterfall gates, exact model and effort assignments, file ownership, verification, and
escalation conditions. Sol maps every original acceptance criterion within each
milestone to its owner, gate, evidence, and final status. Continue until each is
verified or has a concrete blocker; a blocked item is never complete. Sol then checks
integrated behavior, remaining risks, routing deviations, and budget status. Preserve
those decisions across compaction and revalidate state when resuming.
