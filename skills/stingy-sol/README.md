# Stingy Sol

Use GPT-5.6 Sol as the planner, coordinator, integrator, and final reviewer while
routing bounded work to GPT-5.6 Terra or Luna at the lowest sufficient reasoning
effort.

Use it for substantial multi-file builds, research, testing, debugging, migrations,
and explicit subagent or agent-team orchestration. Small or tightly coupled tasks stay
with one agent.

- [Full skill](./SKILL.md)
- [Model catalog](./references/model-catalog.md)
- [Adaptive orchestration](./references/orchestration.md)
- [Cost model](./references/cost-model.md)

Do not combine it with Ultra or another proactive exhaustive-delegation policy; this
skill supplies a bounded delegation policy of its own.

## Install or update

Use the current official locations: `.agents/skills/stingy-sol/` in a repository or
`$HOME/.agents/skills/stingy-sol/` for a user installation. To install from a
repository, use `$skill-installer` and its repository-install flow. `CODEX_HOME/skills`
remains a client or legacy compatibility location in some environments, including this
one, rather than the primary location.

For example, ask Codex:

```text
$skill-installer install the stingy-sol skill from https://github.com/Comradery64/my-codex-skills/tree/main/skills/stingy-sol
```

Start a new session and verify `$stingy-sol` after installation. When migrating from
the old `frugal-sol` skill, retire that copy only after the new invocation succeeds.
