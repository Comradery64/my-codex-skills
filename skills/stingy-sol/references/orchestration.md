# Shared adaptive orchestration

This file is identical in `austere-astra` and `stingy-sol`. The root model named by the
parent skill owns the task graph and every delegation decision. Each worker receives
one bounded task and never spawns another worker.

## Build an evolving dependency graph

Start with the outcome, constraints, unknowns, contracts, and acceptance criteria.
Create only the detail justified by current evidence. Mark each task as:

- `ready`: inputs and acceptance gate are known;
- `blocked`: named dependencies must be accepted first;
- `provisional`: likely work whose scope or route depends on new evidence;
- `accepted`, `revision`, or `blocked_external` after review. `blocked` records an
  unmet dependency or external condition; it is never acceptance.

The graph is a decision aid, not a promise to execute the initial ordering. After every
worker return, the root reviews the evidence and may add, remove, merge, split, reorder,
parallelize, or serialize remaining tasks.

## Decide between parallel and waterfall work

Run tasks in the same wave only when all of these are true:

- neither consumes the other's output;
- their questions or contracts can be evaluated independently;
- they do not mutate the same files, generated artifacts, services, test fixtures, or
  other shared state;
- each has a separate acceptance gate and explicit ownership;
- expected latency or context-isolation benefit exceeds coordination overhead.

Use waterfall sequencing when any task establishes another's requirements, contracts,
schema, migration state, reproduction, or integration base; when ownership overlaps;
when validation shares mutable state; or when uncertainty could invalidate parallel
work. Parallel writers are allowed only for disjoint files behind stable interfaces
with isolated verification. When in doubt, parallelize evidence gathering and
serialize mutation.

Respect the runtime's thread limit, but never spawn workers merely to occupy available
slots. A typical project may move through parallel scouts, root synthesis, one or more
safe implementation waves, sequential integration, isolated verification, and root
acceptance. The root chooses each wave from current evidence rather than following a
fixed topology.

## Task board

```markdown
# <outcome>

Runtime: requested <root model/effort>; effective <value|unknown>
Milestone: <stable_id> | unit <declared unit> | enforcement <runtime|dispatch_boundary|cooperative>
Allowance: <total> | spent <root+workers+guardians+failed attempts> | integration reserve <n> | repair reserve <n>
Budget: `scripts/token_budget_guard.py --session <root-session.jsonl> --tree --json --ledger <artifact>/milestone.json` -> <action state and aggregate>

| ID | Phase | State | Depends on | Model | Effort | Selection reason | Ownership | Contract | Gate | Allowance | Forecast | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Recon | ready | — | Luna | low | fixed file inventory | scratch only | paths only | cited paths | 1 response | 8k | — |
| R2 | Recon | ready | — | Terra | medium | semantic call tracing | scratch only | behavior map | cited call sites | 3 responses | 40k | — |
| B1 | Build | blocked | R1,R2 | Terra | medium | bounded patch after synthesis | src/a | stable API | targeted test | 6 responses | 120k | — |
```

Map each acceptance criterion within a milestone to a **stable criterion ID**, an
owner, acceptance evidence, and current status. Keep the IDs unchanged across repairs
and worker replacements. Record phase entry and exit gates, dependencies, requested and
effective model and effort, a one-line routing reason, owned paths or state, intended
behavior, verification, the assignment's finite allowance, its upper forecast, and
accepted evidence. Fully specify the next wave. Later tasks may stay provisional until
findings make their contracts real. Preserve an approved plan and continue ready work;
replan only where evidence changes dependencies, contracts, or feasibility.

Keep one rolling state artifact. Do not create a separate narrative document per
checkpoint, and do not reread skills, plans, or logs already represented by accepted
evidence unless a named change invalidates them.

## Bounded assignments

Subject bounds are not consumption bounds. A long list of owned files and acceptance
clauses does not stop a worker from discovering, repairing, and reinterpreting until
its context is enormous. Every assignment therefore names all of:

- one observable deliverable;
- the state it owns;
- a finite allowance in the declared unit, counting discovery, retries, and reporting;
- an early-return condition;
- an exact verification command or artifact contract;
- the integration reserve held back at the root.

Assignments are eligible for dispatch only under the rules in
[cost-model.md](cost-model.md#dispatch-eligibility): an unforecast assignment gets a
separately bounded diagnostic, not an implementation. When work needs additional
deliverables or reaches its return threshold, the worker preserves its artifacts and
returns partial evidence. Nothing described as "the remaining gate" may keep expanding.
Closely coupled work can stay in one assignment, but only with an explicit combined
allowance.

## Self-contained handoff

```text
Objective: <one bounded outcome>
Why: <larger outcome it enables>
Repository: <absolute path>
Milestone: <stable milestone ID>
In scope: <files, state, questions, or sources>
Out of scope: <explicit exclusions>
Assignment: model <exact>; effort <exact>; edits <none|owned paths>
Owns: <named files or state, exclusively>
Dependencies: <accepted inputs and contracts>
Verification: <exact command or artifact contract>; success is <observable condition>
Criteria: <stable IDs this assignment must return, one line each>
Allowance: <finite value in the declared unit>, counting discovery, retries, and
reporting. Enforcement is cooperative unless the adapter states otherwise.
Return threshold: <finite value>; on reaching it, stop and return partial evidence.
No expansion: do not add deliverables, broaden scope, or start a second repair.
Scratch: <task-specific allowed location>
Rules: do not spawn workers; preserve user changes; stop before crossing scope,
permissions, safety, or destructive boundaries.
Return (concise): deliverable or artifact paths; every criterion ID as
pass|fail|unverified with an artifact path or a precise blocker; change summary;
verification output including partial results; coverage manifest when a measurement
is claimed; confidence; stopped_short: true|false and reason.
A worker return ends that assignment only; the root decides whether the project
continues, replans, escalates, or reports a blocker. The allowance does not stop other
ready authorized work; actual budget, permission, and safety boundaries remain binding.
```

Use `fork_turns="none"` with explicit `model` and `reasoning_effort` when the live
collaboration tool supports them. A representative call is:

```js
spawn_agent({
  task_name: "task_id",
  fork_turns: "none",
  model: "gpt-5.6-terra",
  reasoning_effort: "medium",
  message: "<self-contained handoff>"
})
```

Use the runtime tool schema as authority. `reasoning.effort` is an API field,
`reasoning_effort` is a collaboration-call field, and `model_reasoning_effort` is a
Codex configuration field. UI metadata in `agents/openai.yaml` does not select a model.

## Complete receipts

A return is complete only when every stable criterion ID comes back as `pass`, `fail`,
or `unverified` with an artifact path or a precise blocker. A receipt that omits an ID
is incomplete, not a phase pass. Validate completeness mechanically before root review:

```sh
scripts/receipt_check.py --receipt <artifact>/receipt.json --require <id1,id2,...>
```

The validator proves completeness, never correctness — the root still reads the
evidence. When a criterion is absent, request only the missing evidence, charged to the
existing milestone allowance. Do not reread the complete handoff to reconstruct what
the receipt should have contained.

See [verification-contracts.md](verification-contracts.md) for the preflight ordering
and coverage-manifest requirements the validator also enforces.

## Context and shared-state control

Prefer a task-specific operating-system temporary directory for noisy read-only
artifacts, or an existing permitted project convention. Do not add repository scratch
or ignore rules unless the task calls for persistent coordination artifacts. Return
summaries instead of raw logs. The root opens the artifacts needed for decisions and
acceptance, and receives compact receipts and focused diffs.

Before launching a parallel wave, assign every mutable path and shared resource to one
worker. Workers stop and report when the repository contradicts the handoff or required
work crosses ownership. If one return changes a contract used by a still-running
worker, the root steers or stops the affected task before accepting further writes.

Reuse is a cost decision, not a default. Track a worker's responses and usage across
its entire history. Reuse it only while that is cheaper than a concise fresh
continuation; when the history reaches its recorded review threshold, or repeated
returns dominate the work, compare compact handoff against reuse and take the lower
sufficient cost. A new worker receives accepted evidence, not instructions to repeat
it, and rotating workers never resets milestone accounting.

## Checkpoints produce action states

Every threshold result is an action, not a number. The permitted states are
`proceed_within_allowance`, `reduce_or_reframe`, `bounded_diagnostic`,
`resource_blocked`, and `aggregate_unavailable`; the guard returns one on every run.

When a threshold is crossed, or the forecast exceeds the remaining allowance: stop
dispatching new substantial work and permit one bounded routing decision. Resume only
with a route that fits the existing allowance. Never reset the allowance to make it
fit, and never progress from repeated warnings into another large phase on reporting
alone.

Before implementation, provide failure examples for consequential invariants; a design
that cannot explain an invariant means the architecture question is resolved before
the coupled implementation, not during review. A later miss consumes the existing
repair reserve.

## Review, replan, and escalate

For each return, the root:

1. checks scope and ownership;
2. validates receipt completeness, then reopens the evidence that can change acceptance;
3. confirms the evidence satisfies the stated gate; reruns affected checks when
   integration changes their validity, evidence is stale or questionable, or risk warrants it;
4. accepts the task, requests one targeted revision, or marks it blocked;
5. updates assumptions, dependencies, routes, and the next parallel or waterfall wave.

Root review focuses on the decision that can change acceptance: architecture, a
contested invariant, integration, or a concrete evidence gap. Each repeated read or
test needs a concrete validity reason. Routine status checks do not reopen a large root
context; prefer event completion over model-driven progress polling where the runtime
supports it. Required user updates stay brief.

A failed gate, missing evidence, low confidence, stopped-short status, or objective
mismatch triggers diagnosis. Keep the model and raise effort when depth was lacking;
raise the model when capability was lacking; rewrite the task when the contract was
unclear. Count a worker's attempted repair toward the single bounded remediation
allowance; after another failure, replan, take root ownership, or report the blocker.
A repeated incomplete return is itself a signal to revise the route. Do not duplicate
credible worker work or rerun broad validation merely because a worker returned. Stop
an obsolete worker before transferring its ownership. Never bypass a permission or
safety refusal by changing models.

## User corrections change the next dispatch

When the user corrects austerity, persist an operating-policy delta in the rolling
artifact and state the concrete scheduling, scope, context, or allowance change in one
short update. Acknowledging the concern and printing another usage split is not a
response.

- "keep this worker running" preserves that worker and narrows subsequent dispatch;
- a clear stop stops active work;
- a cost complaint triggers resource triage before another substantial launch, not
  automatic abandonment of useful work.

No new large assignment is dispatched under unchanged bounds after a correction.

## Milestone closure

At phase gates, verify integrated behavior and decide whether the next phase is ready.
Close each milestone with an accepted artifact or an explicit partial state, and check
the next phase's forecast and reserves before entering it, even under an authorized
multi-phase plan. Acceptance of one phase does not authorize an economically unbounded
next one: the functional scope stays authorized, but its execution route still has to
fit the resource controls. Preserve deployable or reviewable increments where feasible.

At the end, account for every requested outcome and unresolved task. A collection of
accepted worker reports is not a substitute for root acceptance.
