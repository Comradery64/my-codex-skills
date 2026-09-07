---
name: austere-astra
description: Use GPT-6 Astra at xhigh for framing, architecture, acceptance, and final review while routing bounded evidence and execution tasks to the least expensive capable Codex model. Use for substantial implementation, debugging, research, migration, or multi-phase work; skip small single-chain tasks.
---

# Austere Astra

Adapted from `stingy-sol`, originating in the user's frugal-fable project (archived).
Use it to preserve Astra-led quality while reducing avoidable worker cost. It is a
cost target, never permission to reduce the required outcome or Astra's xhigh effort.

## Authority and runtime truth

Astra at `xhigh` owns initial framing, scout questions, evidence synthesis,
architecture, alternatives and tradeoffs, success criteria, phase boundaries, task
routing, acceptance, replanning, and final review. It does not delegate those
judgments to a planner proxy.

A skill cannot change the running root model or effort. When runtime metadata is
available, record the requested and effective model/effort; otherwise record
`unknown`. Do not claim an Astra-xhigh run if it is not one. When identity is needed
to meet the user's explicit request, prepare a concrete plan, handoff, and evidence
with current capabilities and ask the user to select Astra xhigh. Do not silently
substitute Sol or edit global configuration. `xhigh` is exact: do not upgrade it to
`max` or `ultra` merely for intelligence.

Use only tools and overrides actually exposed by the runtime. A hard cost cap needs
an enforceable controller or conservative preflight bound; a skill alone cannot
enforce one. Do useful authorized work first, then request only the clarification
needed before crossing an unbounded cap.

## Astra-led phases

1. **Frame.** Astra defines outcome, constraints, unknowns, risks, and targeted scout
   questions before reconnaissance.
2. **Investigate and plan.** Luna `low` gathers read-only evidence; use Terra `low` or
   `medium` for complex tracing. Astra resolves contradictions, checks important
   primary sources, and writes the phase/task plan.
3. **Execute one accepted task at a time.** Before starting, Astra confirms accepted
   dependencies, selects the exact worker model and effort with a reason, and supplies
   a self-contained handoff. One worker patches, verifies, or integrates; it returns
   artifacts. Astra inspects the relevant diff, contracts, and evidence, then accepts,
   requests a correction, or replans. Do not start the next execution task before
   acceptance, unless an explicit Astra replan removes that dependency.
4. **Gate each phase and finish.** Astra verifies integrated behavior, refines the next
   phase plan, and finally accepts the original requirements rather than a collection
   of passing subtasks.

For a plan-only request, stop after the plan. Once the user authorizes a build,
internal acceptance gates do not require asking the user after every task.

## Plan and task board

Maintain a compact board in the task artifact or existing project convention. Include
phase outcome plus entry/exit gates; ordered IDs and dependencies; exact owner
model/effort; one-line selection reason; allowed paths; intended contracts; acceptance
checks; estimate or budget band; status; and accepted evidence. Fully specify near-term
tasks; later tasks may be provisional but must name proposed routing and gates.

Tiny direct Astra work is permitted where delegation overhead dominates; record why.
Root Astra owns coordination and integration decisions, although it may assign a
mechanical integration step to the sole execution worker.

## Route by task evidence

Choose model and effort from ambiguity, stakes, reversibility, coupling, verifiability,
and local evidence; the table is guidance, not an immutable floor.

| Work | Typical route | Gate |
|---|---|---|
| Inventory, log reduction, mechanical docs, read-only source gathering | Luna `low` | Cited paths, commands, or sources |
| Bounded code/test implementation | Terra `medium`; `low` if deterministic | Relevant checks or explicit evidence |
| Difficult refactor, security concern, cross-system diagnosis | Sol `high`; `medium` if clearly bounded | Astra review of diff and evidence |
| Novel or ambiguous high-stakes design; planning and acceptance | Astra `xhigh` | Astra decision record |

Luna is not a default code architect or semantic/security implementer: improve the
specification before gambling on a cheap route. Sol is not the default worker. Astra
may select another supported effort when evidence justifies it, but never automatically
downshift orchestration to meet a cost target. Record every exact selection.

## Global execution lane

There is one execution task globally: patching, verification work, and integration all
occupy that lane. Do not allow parallel coding, even on disjoint files, in the default
mode. Do not let workers autonomously delegate.

Independent, read-only scouts may run in parallel only during reconnaissance or while
Astra has useful independent work. Respect the runtime slot limit; do not hard-code a
number. A scout must not mutate shared test state while a writer is active: freeze its
inputs or defer it. Never spawn merely to delegate.

## Handoffs, context, and acceptance

Use a compact, no-history handoff: objective and why; absolute repository path;
in/out-of-scope paths; assigned model and effort; edit authority; intended behavior;
scratch artifact; verification; stop conditions; and the return contract below.

Prefer a task-specific OS-temporary scratch directory outside the repository, unless
an allowed project convention already exists. Do not add `.gitignore` entries merely
for scratch. Preserve accepted contracts, decisions, gates, routing, and actual cost
data across compaction; revalidate state after resuming.

Workers return at most about 200 words: artifact path(s), a three-line summary,
confidence, verification result, and `stopped_short` with reason. Astra opens only
relevant diffs, contracts, and critical evidence rather than every raw log.

## Retry and coordination tools

After a failed gate, missing evidence, mismatch, or stopped-short result, Astra first
diagnoses specification, environment, or capability. Permit one bounded remediation
per task. A follow-up retains its model/effort; stop an obsolete worker before a
replacement, and specify overrides when changing either. After the retry fails, Astra
replans or takes ownership. Do not create cheap retry loops or bypass a refusal by
model swapping.

For exact collaboration calls, handoff and retry mechanics, read
[references/run-template.md](references/run-template.md). It distinguishes API
`reasoning.effort`, collaboration `reasoning_effort`, and CLI
`model_reasoning_effort`. Do not invent Workflow/TaskCreate, budget controls, or a
persistent goal; create a goal only on the user's explicit request.

## Cost control and truthful reporting

The aspirational target is **10–30%** of a comparable all-Astra-xhigh cost (70–90%
savings), while retaining quality. It is not a guarantee or quota. Read
[references/cost-model.md](references/cost-model.md) before estimates or final cost
claims. It contains the pricing snapshot, ledger, baseline rules, and worked algebra.

Reserve review and one correction. Reforecast after each phase before an expensive
escalation. If forecast cost exceeds 30%, reduce duplicated context and task size or
route only work a cheaper capable model can do; disclose the miss and finish authorized
scope. If it is under 10%, do not spend merely to reach the target.

## Final acceptance

Astra checks the original outcome, relevant integrated behavior, accepted evidence,
remaining risks, and deviations from requested/effective routing. Report cost as
observed, estimated, or unknown—never zero by omission—and distinguish API estimates
from a ChatGPT subscription or credit bill.
