# Shared model catalog and routing policy

This file is identical in `austere-astra` and `stingy-sol`. The parent `SKILL.md`
chooses the root orchestrator; this catalog classifies every available worker from the
same evidence. Runtime availability and the collaboration tool's schema take
precedence over this snapshot.

## Model categories

| Category | Model ID | Supported effort | Best fit | Do not use as the default for |
|---|---|---|---|---|
| Highest judgment | `gpt-6-astra` | `low`, `medium`, `high`, `xhigh`, `max` | Ambiguous architecture, cross-cutting tradeoffs, consequential acceptance, hardest end-to-end work | Mechanical extraction or routine high-volume work |
| Advanced judgment | `gpt-5.6-sol` | `none`, `low`, `medium`, `high`, `xhigh`, `max` | Difficult implementation, subtle refactors, security and correctness analysis, complex multi-system diagnosis | Enumeration and fixed-format processing |
| Balanced worker | `gpt-5.6-terra` | `none`, `low`, `medium`, `high`, `xhigh`, `max` | Semantic codebase tracing, focused research, test triage, bounded deterministic patches, supporting-document analysis | Novel architecture or final high-stakes acceptance |
| High-volume worker | `gpt-5.6-luna` | `none`, `low`, `medium`, `high`, `xhigh`, `max` | Enumeration, extraction, known-command runs, log reduction, and fixed-format summaries with objective checks | Semantic source tracing, architecture, security review, or correctness decisions |

Official OpenAI documentation describes Astra as the most capable end-to-end model,
Terra as the balance of intelligence and cost, and Luna as the cost-sensitive,
high-volume tier. Codex subagent guidance narrows Luna to clear, repeatable work and
positions Terra for exploration and read-heavy analysis. Sources verified 2026-09-07:
[model catalog](https://developers.openai.com/api/docs/models),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), and
[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

API capabilities do not guarantee that a spawned Codex worker receives every tool.
Use only models, effort overrides, tools, and permissions exposed in the live runtime.
Record requested and effective routing when observable; record `unknown` otherwise.
The parent skill's root authority overrides this generic capability map: Austere Astra
keeps root judgment with Astra, while Stingy Sol keeps it with Sol and does not
delegate upward to Astra.

## Effort labels

| Effort | Use when |
|---|---|
| `none` | Pure transformation with no meaningful inference, only when supported; avoid for agentic tool work |
| `low` | Clear scope, objective success condition, little ambiguity |
| `medium` | Several steps, semantic tracing, or ordinary implementation judgment |
| `high` | Complex logic, subtle assumptions, security/correctness concerns, difficult diagnosis |
| `xhigh` | The hardest reasoning where the root policy or observed evidence calls for it |
| `max` | Exceptional cases supported by the model; never an automatic upgrade from an explicitly requested lower setting |

Higher effort usually increases latency and token use. Set both model and effort
explicitly for each task; if the runtime cannot honor either override, record the
deviation rather than claiming it occurred.

## Selection procedure

For each ready task, the root assesses:

- **ambiguity:** how much interpretation or discovery remains;
- **stakes:** impact of a wrong answer or patch;
- **reversibility:** ease of detecting and undoing an error;
- **coupling:** dependence on other tasks, files, contracts, or shared state;
- **verifiability:** strength and cost of an objective acceptance check.

Then choose the least expensive model and effort that can plausibly pass the gate.
Prefer Luna only when the task is clear and mechanical. Start semantic exploration and
ordinary bounded implementation with Terra. Route subtle or high-stakes work to Sol.
Use Astra as the root only under `austere-astra`. Under `stingy-sol`, Sol remains both
the root and highest available tier for delegated work.

These are defaults, not quotas. Improve an underspecified task before gambling on a
cheaper model. Raise effort when the worker needed more depth; raise model tier when
the task exceeded its capability. Reconsider the remaining routes whenever returned
evidence changes assumptions, dependencies, risk, or verifiability.

## Choose model and effort separately

Model tier answers "can it do this at all"; effort answers "how much reasoning does
this instance need". Deciding them together is what turns a whole run expensive.

- Semantic tracing and ordinary bounded patches start at Terra with ordinary effort.
- Known-command execution is a direct tool call, or a Luna assignment at low effort
  when it needs its own context. Running a fixed command is not a reasoning task.
- Sol or high effort requires a task-specific coupling or correctness reason, recorded
  in one line on the board. High effort is never inherited: a fixed-command fixture run
  does not become high-effort because the worker that diagnosed the bug was.
- Once diagnosis is complete and the remaining work is mechanical, select the cheapest
  sufficient continuation. That includes spawning no new agent at all when spawn and
  handoff overhead would exceed the benefit.

Record a rationale for every high-effort assignment. An audit where nearly every
worker requested high effort, including the long-running verification worker, is
evidence of unexamined routing rather than caution. None of this imposes model quotas
or forces work to be fragmented to hit a routing rule.
