# Stingy Sol routing cheatsheet

## Two controls

1. Set the lowest reasoning floor that clears the slice's bar.
2. Delegate independent work to the least expensive capable model.

Sol keeps decomposition, architecture, shared integration, conflict resolution, final
review, and the user-facing synthesis.

## Routing floor

| Work | Owner | Effort |
|---|---|---|
| Search, inventory, large-file scan, logs, straightforward summary | Luna | low |
| Bounded patch, targeted test, reproduction, adversarial check | Terra | low-medium |
| Difficult bounded implementation, subtle/security-critical review | Sol child | medium-high |
| Plan, coordinate shared files, integrate, decide, final review | Root Sol | hardest root-only phase |

Risk axes: stakes, reversibility, ambiguity, coupling. The highest axis sets the floor.
Overrides go upward only and include a reason.

## Effort

- `low`: clear and bounded; speed matters.
- `medium`: balanced default.
- `high`: complex logic, assumptions, or edge cases.
- `xhigh` / `max`: unusually difficult and justified by risk or observed failure.
- Avoid `none` for planning and tool-using agents.

Root effort may be fixed for the whole turn. Do not claim phase-by-phase changes unless
the runtime actually supports them.

## Delegate when

- Two or more workstreams are independent.
- Separate context improves focus or protects the root context.
- Parallel execution improves time or coverage.
- Writers own disjoint files.

Keep one agent when work is small, sequential, tightly coupled, write-contentious, or
dominated by one slow external operation.

Children never delegate. Use `fork_turns="none"`; default to one child and allow at
most two concurrent read-only scouts. Run `scripts/token_budget_guard.py --json`
before delegation, after each return, and before a new phase. Soft 100,000 requires a
visible reforecast; hard 250,000 requires explicit user confirmation to continue.

## Context firewall

When repository writes are permitted, write noisy output to
`.stingy-sol/<task>/<slice>/`. Otherwise use a task-specific OS temporary directory
outside the repository; if neither is safe, return concise inline evidence. Return only
path, a three-line summary, confidence, verification result, and stopped-short status.
Record unavailable collaboration, model, or effort overrides as deviations; never claim
that an unavailable route occurred. Root Sol reads full artifacts only on demand.

## Handoff

Objective + why; absolute repo path; in/out of scope; model + reasoning floor; source
edit permission + file ownership; scratch path; exact gate; stop conditions; concise
return contract.

## Escalation

Signal required: failed gate, low confidence, stopped short, missing evidence, review
mismatch, or visible capability failure. Retry that slice once. Raise reasoning when
depth is the problem; raise Luna -> Terra -> Sol when capability is the problem. Then
root Sol owns it or reports the blocker.

## Final gate

Reports are leads. Reopen high-impact evidence, inspect final diffs, run relevant
checks, reconcile conflicts, and account for every slice before declaring completion.
