# Codex Skills Collection

A collection of reusable skills for Codex.

## Skills

### [Austere Astra](./skills/austere-astra)

Use GPT-6 Astra at xhigh for planning, architecture, and review, with cheaper models
for bounded work. Astra dynamically chooses parallel waves or waterfall sequencing as
evidence changes, selects every worker's model and effort, and reviews each result.

- [Full skill](./skills/austere-astra/SKILL.md)
- [Model catalog](./skills/austere-astra/references/model-catalog.md)
- [Adaptive orchestration](./skills/austere-astra/references/orchestration.md)
- [Cost model](./skills/austere-astra/references/cost-model.md)

### [Stingy Sol](./skills/stingy-sol)

Use GPT-5.6 Sol for planning, coordination, integration, and final review while routing
independent, verifiable work to GPT-5.6 Terra or Luna with explicit reasoning floors,
file ownership, verification gates, and root-owned adaptive sequencing.

- [Full skill](./skills/stingy-sol/SKILL.md)
- [Model catalog](./skills/stingy-sol/references/model-catalog.md)
- [Adaptive orchestration](./skills/stingy-sol/references/orchestration.md)
- [Cost model](./skills/stingy-sol/references/cost-model.md)

## Install

Copy a skill directory into `~/.codex/skills/`, or point Codex at its `SKILL.md` using
the skill configuration supported by your client.
