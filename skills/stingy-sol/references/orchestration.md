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
- `accepted`, `revision`, or `blocked_external` after review.

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
Budget: `scripts/token_budget_guard.py --tree --json` -> <status and aggregate>

| ID | Phase | State | Depends on | Model | Effort | Selection reason | Ownership | Contract | Gate | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Recon | ready | — | Luna | low | fixed file inventory | scratch only | paths only | cited paths | — |
| R2 | Recon | ready | — | Terra | medium | semantic call tracing | scratch only | behavior map | cited call sites | — |
| B1 | Build | blocked | R1,R2 | Terra | medium | bounded patch after synthesis | src/a | stable API | targeted test | — |
```

Record phase entry and exit gates, exact dependencies, requested and effective model
and effort, a one-line routing reason, owned paths or state, intended behavior,
verification, status, and accepted evidence. Fully specify the next wave. Later tasks
may stay provisional until findings make their contracts real.

## Self-contained handoff

```text
Objective: <one bounded outcome>
Why: <larger outcome it enables>
Repository: <absolute path>
In scope: <files, state, questions, or sources>
Out of scope: <explicit exclusions>
Assignment: model <exact>; effort <exact>; edits <none|owned paths>
Dependencies: <accepted inputs and contracts>
Verification: <command or evidence>; success is <observable condition>
Scratch: <task-specific allowed location>
Rules: do not spawn workers; preserve user changes; stop before crossing scope,
permissions, safety, or destructive boundaries.
Return (concise): artifact paths; findings or change summary; confidence; verification;
stopped_short: true|false and reason.
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

## Context and shared-state control

Prefer a task-specific operating-system temporary directory for noisy read-only
artifacts, or an existing permitted project convention. Do not add repository scratch
or ignore rules unless the task calls for persistent coordination artifacts. Return
summaries instead of raw logs. The root opens the artifacts needed for decisions and
acceptance.

Before launching a parallel wave, assign every mutable path and shared resource to one
worker. Workers stop and report when the repository contradicts the handoff or required
work crosses ownership. If one return changes a contract used by a still-running
worker, the root steers or stops the affected task before accepting further writes.

## Review, replan, and escalate

For each return, the root:

1. checks scope and ownership;
2. reopens critical evidence and inspects the relevant diff;
3. runs or confirms the stated gate;
4. accepts the task, requests one targeted revision, or marks it blocked;
5. updates assumptions, dependencies, routes, and the next parallel or waterfall wave.

A failed gate, missing evidence, low confidence, stopped-short status, or objective
mismatch triggers diagnosis. Keep the model and raise effort when depth was lacking;
raise the model when capability was lacking; rewrite the task when the contract was
unclear. Allow one bounded remediation, then replan, take root ownership, or report the
blocker. Stop an obsolete worker before transferring its ownership. Never bypass a
permission or safety refusal by changing models.

At phase gates, verify integrated behavior and decide whether the next phase is ready.
At the end, account for every requested outcome and unresolved task. A collection of
accepted worker reports is not a substitute for root acceptance.
