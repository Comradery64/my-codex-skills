# Austere Astra run template

Use this reference when creating a multi-task plan or dispatching a worker.

## Board

```markdown
# <objective>

Runtime: requested `gpt-6-astra` / `xhigh`; effective: <value|unknown>.

| ID | Phase | Outcome / gate | Depends on | Owner | Why this route | Paths | Contract | Acceptance | Band | Status | Accepted evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | Frame | Constraints and scout questions accepted | — | Astra xhigh | Root judgment | scratch only | Scope | Decision record | small | accepted | <path> |
| T1 | Investigate | Evidence sufficient for plan | P1 | Luna low | Read-only inventory | none | Findings | cited sources | small | queued | — |
| T2 | Build | <behavior> | T1 | Terra medium | bounded implementation | <paths> | <contract> | <command> | medium | queued | — |
```

Give each phase an outcome and entry/exit gate. Detail near-term tasks; later entries
may be provisional but retain routing and gates. One execution task is active globally.

## Self-contained worker handoff

```text
Objective: <one bounded outcome>
Why: <larger outcome>
Repository: <absolute path>
In scope: <files, modules, or questions>
Out of scope: <explicit exclusions>
Assignment: model <exact>; reasoning effort <exact>; source edits <none|paths>
Do not spawn subagents. Preserve existing user changes; edit only assigned paths.
Contract: <intended behavior>
Scratch: <OS temporary path or allowed existing convention>
Verification: <command/evidence>; success is <observable result>
Stop and report: contradictory state, out-of-scope requirement, permission/safety
barrier, destructive action, or failure after one reasonable attempt.
Return (<=200 words): artifact paths; three-line summary; confidence; verification;
stopped_short: true|false and reason.
```

## Collaboration adapter

Use the exposed collaboration API and current schema. A context-limited dispatch with
explicit routing has this shape:

```js
spawn_agent({
  task_name: "task_id",
  fork_turns: "none",
  model: "gpt-5.6-terra",
  reasoning_effort: "medium",
  message: "<self-contained handoff>"
})
```

An all-history fork cannot be combined with overrides when the runtime forbids it.
Use `send_message` only to add material context to a running worker. Use
`followup_task` for an idle worker's one targeted remediation; it retains its
model/effort. To replace it, first `interrupt_agent`, wait until stopped, then spawn a
replacement with explicit overrides. `wait_agent` is at most 60 seconds (or shorter)
so the user receives progress updates.

`reasoning.effort` is an API field, `reasoning_effort` is the collaboration-tool field,
and `model_reasoning_effort` is a CLI setting. They are not interchangeable. UI metadata
in `agents/openai.yaml` never selects an execution model.
