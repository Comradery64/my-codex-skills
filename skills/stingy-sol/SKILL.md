---
name: stingy-sol
description: Use GPT-5.6 Sol as the planning, coordination, integration, and final-review agent for substantial Codex work while routing independent, bounded work to GPT-5.6 Terra or Luna at the lowest sufficient reasoning effort. Use for multi-file implementation, broad repository exploration, research, testing, debugging, migrations, or explicit requests to orchestrate subagents efficiently. Do not use for a small task that one agent can finish directly.
---

# Stingy Sol

Use two cost controls in order:

1. Choose the lowest reasoning effort that meets the slice's quality floor.
2. Delegate independent, verifiable work to the least expensive capable model.

Sol owns judgment. Subagents gather evidence, perform bounded execution, and return
reviewable artifacts. Sol owns decomposition, shared-file coordination, conflicting
findings, integration, final verification strategy, and the user-facing answer.

## Preconditions

- Apply this policy when GPT-5.6 Sol is the root orchestrator. If the root is clearly
  another model, do not claim that Sol orchestrated the result; ask the user to select
  Sol only when that distinction materially affects the request.
- Do not combine this skill with Ultra or another proactive, exhaustive delegation
  policy. If one is clearly active, explain the conflict and ask the user to disable it
  before continuing. This skill provides its own bounded delegation policy.
- A skill cannot itself enforce an account-spend ceiling. Before starting work under a
  hard ceiling, confirm that an available budget control can enforce it or that current
  usage and pricing data can bound the run safely. If neither is available, do not
  promise completion or silently reduce the requested scope. State the cost uncertainty
  and ask the user to relax the ceiling, authorize a specific reduced scope, or provide
  an enforceable control. Record the control and stop condition in the run manifest
  when one is used, and stop before crossing the bound.

## Decide whether to delegate

Keep the task with Sol when it is small, tightly coupled, mostly a single reasoning
chain, or likely to create shared-file contention. Delegate when at least two concrete
workstreams can proceed independently and doing so materially improves speed, context
isolation, or coverage.

Good first delegation targets are read-heavy exploration, source gathering, log
reduction, targeted test runs, independent hypotheses, and disjoint implementation
slices. Prefer a flat team. Let a child create its own team only when its assignment
contains genuinely independent subproblems and the global concurrency limit has room.

Do not spawn an agent merely to restate the task, create a plan Sol already needs to
create, or wait while Sol has no useful parallel work.

## Price every slice

Score stakes, reversibility, ambiguity, and coupling. The highest-risk axis sets the
model and reasoning floor.

| Slice | Default owner | Reasoning floor | Acceptance gate |
|---|---|---|---|
| Search, inventory, large-file scan, log reduction, straightforward summary | GPT-5.6 Luna | low | Cite paths, commands, or sources; sanity-check |
| Bounded patch, targeted tests, reproducible debugging, adversarial verification | GPT-5.6 Terra | low or medium | Relevant build/tests or explicit evidence pass |
| Difficult but bounded implementation, subtle refactor, security/correctness review | GPT-5.6 Sol subagent | medium or high | Root Sol reviews evidence and diff |
| Decomposition, architecture, product/safety tradeoffs, shared integration, conflict resolution, final review | Root Sol | Set for the hardest root-only phase | Never delegate ownership |

The table is a floor. Raise the model or reasoning effort when a concrete prior or task
risk warrants it, and record the reason in the handoff or run manifest. Never lower a
slice below the table to save tokens.

Use `low` for straightforward, bounded work; `medium` as the balanced default;
`high` for complex logic and edge cases. Use `xhigh` or `max` only for unusually hard
work when stakes or observed failure justify the added cost. Avoid `none` for agentic
work that needs planning or tools.

The root session's reasoning effort may be fixed for the turn. Do not pretend to change
it between phases. When it can be selected before the run, choose it for the hardest
root-only phase: typically `high` for fuzzy decomposition, `low` or `medium` for clean
integration, and `medium` or `high` for consequential final review. Set each spawned
agent's model and reasoning effort explicitly whenever the collaboration tool permits.
If collaboration tools, a requested model, or an effort override are unavailable, use
the inherited or available behavior instead, record the deviation in the handoff or
manifest, and never claim a route or override that did not occur.

## Build the team

Read [references/fanout-template.md](references/fanout-template.md) when delegating two
or more slices. It contains the handoff contract, scratch layout, manifest, and retry
procedure. For quick routing during an active task, read
[references/routing-cheatsheet.md](references/routing-cheatsheet.md).

Use the Codex collaboration tools directly:

- `spawn_agent` for a concrete, bounded slice that can run independently.
- `send_message` to add context without restarting the agent.
- `followup_task` for a targeted correction after an agent becomes idle.
- `wait_agent` with a long timeout when Sol has no useful local work remaining.
- `interrupt_agent` only when the assignment is obsolete, unsafe, or conflicting.

Spawn independent agents without waiting between spawns. Stay within the runtime's
available slots. If setting a child model or effort requires a context-limited fork,
use a self-contained handoff rather than full chat history. Give full history only when
the slice genuinely depends on it.

## Protect the main context

Use repository-local `.stingy-sol/<task>/<slice>/` scratch only when the task's
permissions allow writes to the repository. When repository writes are not allowed,
use a task-specific directory in the operating system's temporary area outside the
repository. If neither location is safely available, return concise inline evidence
instead of creating coordination artifacts. Coordination artifacts never override user
write constraints. Ask each subagent to return only:

- the artifact path;
- a summary of no more than three lines;
- `confidence: high|medium|low`;
- the exact verification command and result, when applicable;
- `stopped_short: true|false` and the blocker.

Sol reads scratch artifacts on demand. Do not pull every raw log or report into the
root context. Scratch files are coordination artifacts, not proof: reopen the files and
inspect the final diff before relying on high-impact claims.

All agents may share one filesystem. Parallel writes are allowed only for disjoint,
explicitly assigned files. When ownership overlaps, agents write findings or proposed
patches to scratch and root Sol makes the source changes. Preserve user changes and do
not let workers reset, discard, or rewrite unrelated work.

## Handoff contract

Write each delegation as if the child has no chat context. Include:

- the objective and why it matters;
- absolute repository path;
- in-scope files and explicit exclusions;
- assigned model and reasoning floor;
- whether source edits are allowed and exact file ownership;
- scratch output path and concise return format;
- verification command or evidence standard;
- stop conditions: unexpected repository state, repeated command failure, required
  out-of-scope work, permission barrier, or destructive action.

Ask the agent to stop and report rather than improvise across those boundaries.

## Verify and escalate

Treat subagent summaries as leads. Root Sol checks cited files, commands, and diffs and
reconciles conflicting reports.

Escalate a slice only after a concrete signal:

- required verification failed;
- confidence is low;
- the agent stopped short;
- evidence is missing;
- review finds that output does not match the objective;
- the model visibly cannot handle the slice.

Retry only the failed slice, once. Raise reasoning effort first when deeper analysis is
the likely remedy; raise the model when the failure is capability-related. Give the
retry the failed evidence and a narrower correction target. If it fails again, root Sol
owns the slice or reports the blocker. Do not start an automatic second gap-filling
round after successful synthesis.

## Execution lanes

- **Build:** Sol decomposes and coordinates. Luna explores; Terra owns bounded,
  disjoint patches; Sol handles difficult slices and integrates. No patch is accepted
  without a gate proportional to its risk.
- **Research:** Delegate independent questions or source families. Require direct
  links and separate sourced facts from inference. Sol resolves disagreement and
  synthesizes.
- **Testing:** Sol defines what behavior matters. Workers run targeted checks and save
  long output to scratch. Broaden tests only when failures or risk justify it.
- **Debugging:** Parallelize independent hypotheses or evidence collection. Avoid
  concurrent speculative edits. Sol chooses the supported diagnosis and owns the final
  fix when paths overlap.
- **Review:** Use separate read-only perspectives only when their concerns differ
  materially, then deduplicate and prioritize findings before reporting them.

## Planning deliverables

When the user asks for a multi-phase plan, include the routing plan in the deliverable,
not only in the current session. Add `ORCHESTRATION.md` or an equivalent section with:

- slice and owner model;
- reasoning floor and any justified upward override;
- parallel versus sequential dependencies;
- file ownership;
- verification gate;
- escalation and stop conditions.

Follow an existing repository convention for orchestration documents when one exists.

## Runtime facts

GPT-5.6 Sol, Terra, and Luna support configurable reasoning effort, but model access,
tool names, and concurrency can vary by Codex client and account. Use the collaboration
tools actually exposed in the session. Verify version-sensitive details in current
official documentation before changing persistent Codex configuration:

- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
