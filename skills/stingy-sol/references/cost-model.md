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

For the root and every worker, record:

- task ID plus requested and effective model and effort;
- observed or estimated input, cached input, cache-write, and output tokens;
- whether reasoning tokens are already included in output totals;
- tool or other metered costs;
- the measurement source and any unavailable fields;
- retries and repeated context.

Compute model cost from non-overlapping billing classes:

`cost = Σ(tokens in class × matched class rate) / 1,000,000 + other metered costs`

Do not add reasoning tokens again when the provider includes them in output. Do not
record missing usage as zero. Distinguish observed, estimated, and unknown amounts.

## Token guard

Run `scripts/token_budget_guard.py --tree --json` with the root session when session
logs are available. In tree mode the script finds descendants and sums each thread's
latest thread-local cumulative usage exactly once. If any selected thread lacks usage,
the aggregate is `unknown` rather than a misleading partial total.

Default workflow checkpoints are:

- exit `0`: below 100,000 aggregate tokens;
- exit `10`: soft checkpoint at 100,000;
- exit `20`: hard workflow checkpoint at 250,000;
- exit `30`: aggregate unavailable.

The root policy defines what to do at each checkpoint. The script reads completed log
records; it cannot stop an in-flight call, enforce an account cap, or predict the size
of the next worker. Leave enough headroom for root integration and a bounded revision.

## Comparisons and targets

Use a matched prior run or an authorized controlled benchmark with the same outcome,
scope, quality gate, and pricing. Do not run a second expensive build solely to create
a baseline. Repricing the mixed run's token trace at one model's rates is a routing
proxy, not a measured baseline, because different models and efforts can use different
numbers of tokens and produce different quality.

For a proxy, calculate `mixed estimated cost / baseline estimated cost` and disclose
all assumptions. Targets belong to the parent skill. They never justify forced model
quotas, weakened gates, hidden scope cuts, or extra spending to reach a lower bound.
