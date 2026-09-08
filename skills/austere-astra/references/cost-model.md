# Shared cost model and token ledger

This file is identical in `austere-astra` and `stingy-sol`. It supports estimates and
workflow checkpoints; it does not create an account spending limit.

## Pricing snapshot

Refresh prices before making a current dollar claim. Standard API text prices captured
2026-09-07, USD per 1M tokens:

| Model | Input | Cached input | Output |
|---|---:|---:|---:|
| GPT-6 Astra | $10.00 | $1.00 | $50.00 |
| GPT-5.6 Sol | $4.00 | $0.40 | $20.00 |
| GPT-5.6 Terra | $2.00 | $0.20 | $12.00 |
| GPT-5.6 Luna | $0.20 | $0.02 | $1.20 |

Astra cache writes are $12.50 per 1M tokens. Astra prompts above 272K input tokens
apply 2x input and cache rates and 1.5x output rates to the full request. Service tier,
batch processing, long-context rules, cache writes, tools, and account-specific terms
can change the total. Sources: [OpenAI model catalog](https://developers.openai.com/api/docs/models)
and [Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra).
API estimates are not a ChatGPT subscription or credit-balance statement.

## Ledger

For the root and every worker, record when the measurement source exposes the needed
breakdown:

- task ID plus requested and effective model and effort;
- observed or estimated input, cached input, cache-write, and output tokens;
- whether reasoning tokens are already included in output totals;
- tool or other metered costs;
- the measurement source and any unavailable fields;
- retries and repeated context.

For the run, also record cost per accepted milestone, root versus worker usage where
observable, accepted tasks and revisions, and coordination overhead when it is
observable. Do not manufacture per-thread figures or overhead precision from an
aggregate. Treat coordination overhead as a subset of recorded cost, not an additional
charge. Include failed attempts in their milestone's cost and report unfinished work
separately; do not hide its cost by counting only successes. Never convert an aggregate
token total directly into a dollar total without the applicable model, billing class,
and measurement assumptions.

Compute model cost from non-overlapping billing classes:

`cost = Σ(tokens in class × matched class rate) / 1,000,000 + other metered costs`

Do not add reasoning tokens again when the provider includes them in output. Do not
record missing usage as zero. Distinguish observed, estimated, and unknown amounts.
Usage telemetry that zero-fills omitted token classes is not proof that those billing
classes were measured as zero; cost estimates require source coverage for the billing
classes they use.

## Token guard

Run `scripts/token_budget_guard.py --tree --json --session <active-root-session>` when
session logs are available. Supplying the active root session is required for correct
attribution: the default newest root can select an unrelated concurrent run. The guard
sums each selected thread's latest cumulative usage once. The JSON includes
`root_tokens`, `worker_tokens`, and `thread_tokens` when available; it does not infer models, prices, or billing classes. If a selected
thread lacks usage, treat the aggregate as `unknown` rather than a misleading partial
total. The breakdown remains telemetry, not proof that omitted billing fields cost zero.
Take snapshots or deltas at milestone boundaries, especially for reused workers, to
attribute incremental usage; do not assign their cumulative history to a later task.

Default workflow checkpoints are:

- exit `0`: below the 100,000-token advisory checkpoint;
- exit `10`: advisory review at 100,000 tokens;
- exit `20`: advisory review at 250,000 tokens (legacy telemetry label: `hard`);
- exit `30`: aggregate unavailable.

The root policy defines what to do at each checkpoint. These defaults are advisory;
an explicit user hard budget is binding and must be honored without reinterpretation.
The script reads completed log records and cannot predict the size of the next worker.
Leave enough headroom for root integration and a bounded revision.

## Comparisons and targets

Use a matched prior run or an authorized controlled benchmark with the same outcome,
scope, quality gate, and pricing. Do not run a second expensive build solely to create
a baseline. Repricing the mixed run's token trace at one model's rates is a routing
proxy, not a measured baseline, because different models and efforts can use different
numbers of tokens and produce different quality.

For a proxy, calculate `mixed estimated cost / baseline estimated cost` and disclose
all assumptions. Targets belong to the parent skill. They never justify forced model
quotas, weakened gates, hidden scope cuts, or extra spending to reach a lower bound.
