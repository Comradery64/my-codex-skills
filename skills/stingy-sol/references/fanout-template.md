# Stingy Sol fan-out template

Read this reference when two or more independent slices justify a subagent team.

## 1. Create the run directory

Use a task-specific location:

```text
.stingy-sol/<task>/
├── manifest.md
├── <slice-a>/report.md
├── <slice-b>/report.md
└── <slice-c>/report.md
```

Use `.stingy-sol/` only when task permissions allow repository writes; keep it out of
version control. Otherwise use a task-specific OS temporary directory outside the
repository. If neither is safe, return concise inline evidence rather than writing an
artifact. Use a repository's existing scratch convention instead when it has one and
the task permits it. Coordination artifacts never override user write constraints.

## 2. Write the manifest

Before spawning, record the intended team in `manifest.md`:

```markdown
# <task>

| Slice | Owner | Effort | Writes | Gate | Status |
|---|---|---|---|---|---|
| auth-map | gpt-5.6-luna | low | scratch only | cited call sites | queued |
| login-fix | gpt-5.6-terra | medium | src/login.ts | targeted test | queued |
| threat-review | gpt-5.6-sol | high | scratch only | root review | queued |

Overrides:
- threat-review: Terra -> Sol because authentication semantics are security-critical.

Budget preflight:
- Hard ceiling: <none, or the user's exact limit>
- Control or bound: <enforceable control, or usage and pricing evidence>
- Stop condition: <observable threshold that stops work before the limit>
```

The manifest is an audit aid, not a reason to add process to a two-minute task.
If a hard ceiling cannot be enforced or safely bounded, stop before spawning. Ask the
user to relax it, authorize a specific reduced scope, or provide an enforceable budget
control; do not record a guessed bound or silently change the requested outcome.

## 3. Build each handoff

Use this shape and remove fields that do not apply:

```text
Objective: <one bounded outcome>
Why: <larger goal this enables>
Repository: <absolute path>

In scope:
- <files, modules, questions, or sources>

Out of scope:
- <shared or unrelated surfaces>

Assignment:
- Model: <gpt-5.6-luna|gpt-5.6-terra|gpt-5.6-sol>
- Reasoning floor: <low|medium|high|xhigh|max>
- Source edits: <none|only these disjoint files>
- Scratch artifact: .stingy-sol/<task>/<slice>/report.md, or an OS-temp path when the
  task is read-only

Verification:
- Run: <exact command>, or collect: <exact evidence>
- Success: <observable condition>

Stop and report if repository state contradicts this handoff, the command still fails
after one reasonable retry, required work crosses scope, a permission barrier appears,
or an action would be destructive.

Return only:
- path: <artifact path>
- summary: <at most three lines>
- confidence: high|medium|low
- verification: <command and result, or n/a>
- stopped_short: true|false — <reason if true>
```

If the spawn call can override the model or reasoning effort, use a self-contained
handoff and a context-limited fork supported by the current collaboration tool. Do not
combine an explicit override with full-history inheritance when the runtime forbids it.
If collaboration tools or either override are unavailable, use inherited or available
behavior, record the deviation in the manifest or concise return, and never claim the
requested route occurred.

## 4. Launch and coordinate

1. Spawn independent slices back-to-back, up to the session's available slots.
2. While they run, root Sol handles shared-context analysis, integration preparation,
   or other work that cannot be delegated.
3. Send additional information to a running agent only when it materially changes or
   unblocks that slice.
4. Wait with a long timeout only after useful root work is exhausted.
5. Update the manifest from the concise returns. Read full artifacts only where the
   decision, risk, or integration requires them.

Prefer a flat team. A child may spawn descendants only if its own scope contains
independent work and the global thread cap has room. The root remains responsible for
the final result.

## 5. Integrate safely

- Check `git status` and the relevant diff before accepting worker edits.
- Confirm that each writer stayed within its assigned, disjoint files.
- Reopen cited evidence for high-impact conclusions.
- Run the narrow acceptance gates first.
- Broaden verification only when risk, changed dependencies, or failures justify it.
- Have root Sol resolve overlapping patches and conflicting reports.

## 6. Escalate once

Escalation requires a failed gate, low confidence, stopped-short result, missing
evidence, objective mismatch, or visible capability failure.

Choose one response:

- Increase reasoning one level when the model needed deeper analysis.
- Move Luna to Terra when the task proved to require implementation judgment.
- Move Terra to Sol when the task proved subtle, ambiguous, or high-stakes.
- Give root Sol direct ownership when coordination or shared state caused the failure.

Use a targeted follow-up or replacement task containing the failed evidence. Allow one
retry for that slice. If the retry fails, stop the loop and surface it to root Sol.

## 7. Close the run

Synthesize only after all requested results are available or explicitly accounted for.
Report unresolved slices honestly. Do not launch a new broad gap-filling team unless the
user expands the scope or the original acceptance criteria cannot otherwise be met.
