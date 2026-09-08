# Behavioral decision checks

These four scenarios check orchestration decisions for both `austere-astra` and
`stingy-sol`. They supplement the deterministic tests with eight model responses.
They are opt-in: rendering a prompt is free of model calls; executing it consumes
model usage. Run them after changes to continuation, delegation, or acceptance policy.

| Case | Decision under test |
|---|---|
| `advisory_threshold` | Continue authorized work after the default threshold |
| `explicit_budget` | Pause additional work at an exhausted user hard budget |
| `worker_failure` | Diagnose a failed repair and continue independent work |
| `incomplete_milestone` | Keep unverified criteria open and initiate verification |

## Run

Render a self-contained packet, including the current skill and shared references:

```sh
python3 tests/behavioral/render_prompt.py \
  --skill austere-astra --case advisory_threshold > /tmp/advisory-prompt.txt
```

Repeat for each table entry and both skills. In an agent-capable session, give each
packet to a **fresh agent with no conversation history**. Permit it to read only the
packet, then produce the requested JSON action trace without tools. Use the root model
and effort appropriate to the skill; record requested settings and any runtime values
actually exposed. Do not infer effective settings from the skill text. For the initial
run, the requested settings were Astra/xhigh and Sol/high.

Do not give the responding agent this README, the rubric, other cases, prior responses,
or expected outcomes. The renderer includes only the scenario and skill instructions.
Each source has a SHA-256 fingerprint, allowing a result to be tied to exact inputs.

Save the complete response, packet hash, model settings, and run date. Keep responses
from different cases independent. If a packet is truncated, JSON is unusable, or live
tools are used after the packet read, record the run as invalid rather than a policy
pass. Retain failures; do not silently retry until a passing response appears.

## Review

After responses are saved, use [rubric.md](rubric.md) to assess the actions, arguments,
and supporting reasoning. Grade each case `pass`, `fail`, or `invalid`, and cite the
action or omission supporting that judgment. No exact-phrase checks or automatic
keyword scoring are used. A different sensible route can pass the same criteria.

These are simulated next-decision checks. A dispatch entry is a simulated action;
it does not prove that a live agent would call a tool or complete an implementation.
One passing run is evidence for the tested packet and requested configuration, not a
guarantee across models or future runs. The fixtures supply project usage independently
of the evaluator's real token usage.

The normal test command remains:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

It does not invoke these model checks. Reviewed behavioral runs live under `results/`.
