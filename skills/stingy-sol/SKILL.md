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
never make those project-level decisions and never delegate to other workers.

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

1. Sol frames the outcome, constraints, risks, unknowns, and first evidence needs.
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

Each worker owns one bounded task. Parallel writers require disjoint file ownership,
stable contracts, isolated validation state, and independent acceptance. If any
condition fails, Sol serializes the work. Small, tightly coupled work may stay with Sol
when delegation overhead would exceed its benefit. For a plan-only request, stop after
the plan.

## Context and verification

Use `fork_turns="none"` and a self-contained handoff for every worker. Put noisy output
in task-scoped scratch artifacts when permitted. Workers return concise paths,
findings, confidence, verification results, and stopped-short status. Treat summaries
as leads: Sol reopens high-impact evidence, reviews final diffs, reconciles conflicts,
and runs acceptance checks proportional to risk.

Permit one targeted remediation after a failed gate, missing evidence, or visible
capability failure. Diagnose specification, environment, effort, and model choice
before rerouting. Raise effort when more depth is needed; raise model tier when the
task exceeded capability. After another failure, Sol owns the slice or reports the
blocker. Do not start an automatic gap-filling round after successful synthesis.

## Cost checkpoints

Before the first delegation, after each completed wave, and before a new phase, run
`scripts/token_budget_guard.py --tree --json` from this skill directory when Codex
session logs are available. Exit `10` is a soft checkpoint at 100,000 tokens: report
observed usage, remaining hard-limit budget, and forecast. Exit `20` is a hard workflow
checkpoint at 250,000 tokens: start no new phase or worker without explicit user
confirmation. Exit `30` means aggregate usage is unavailable. The guard cannot stop an
in-flight call and is not a platform spending cap.

Use the ledger to prevent cheap-agent fan-out from becoming an expensive run. Reuse
accepted contracts, avoid repeated context, reserve capacity for root integration and
one remediation, and report observed, estimated, and unknown cost separately.

## Planning and final acceptance

For a multi-phase plan, include dependencies, proposed parallel waves, required
waterfall gates, exact model and effort assignments, file ownership, verification, and
escalation conditions. Sol finally checks the original requirements, integrated
behavior, accepted evidence, remaining risks, routing deviations, and budget status.
Preserve those decisions across compaction and revalidate state when resuming.
