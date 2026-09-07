# Codex Skills Collection

A collection of reusable skills for Codex.

## Skills

### [Austere Astra](./skills/austere-astra)

Use GPT-6 Astra at xhigh for planning, architecture, and review, with cheaper models
for evidence gathering and one execution worker at a time. Astra selects each task's
model and effort, then reviews its result before the next task starts.

- [Full skill](./skills/austere-astra/SKILL.md)
- [Run template](./skills/austere-astra/references/run-template.md)
- [Cost model](./skills/austere-astra/references/cost-model.md)

### [Frugal Sol](./skills/frugal-sol)

Use GPT-5.6 Sol for planning, coordination, integration, and final review while routing
independent, verifiable work to GPT-5.6 Terra or Luna with explicit reasoning floors,
file ownership, verification gates, and bounded escalation.

- [Full skill](./skills/frugal-sol/SKILL.md)
- [Routing cheatsheet](./skills/frugal-sol/references/routing-cheatsheet.md)
- [Fan-out template](./skills/frugal-sol/references/fanout-template.md)

## Install

Copy a skill directory into `~/.codex/skills/`, or point Codex at its `SKILL.md` using
the skill configuration supported by your client.

