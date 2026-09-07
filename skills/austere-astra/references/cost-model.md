# Cost model and ledger

Pricing is a snapshot, not a billing promise. Refresh it before estimates. Official
model comparison prices captured 2026-09-05 (USD per 1M tokens): Astra input/cached/
output = $10/$1/$50; Sol = $4/$0.40/$20; Terra = $2/$0.20/$12. Luna is
$0.20/$0.02/$1.20. Sources: [model comparison](https://developers.openai.com/api/docs/models/compare)
and [Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

For Astra requests above 272K prompt tokens, full-request input/cache rates are 2× and
output is 1.5×; cache writes are $12.50 per 1M tokens (1.25× regular Astra input). See the
[Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra).
Account rates, service tier, long-context, cache-write, and tool fees can differ.
These API estimates are not a ChatGPT subscription or credit bill.

## Formula and ledger

`model cost = sum(nonoverlapping token billing classes × matched price) / 1,000,000
+ applicable other costs`.

Count root and every child, retries, repeated context, planning, and review. Reasoning
is already included in output: do not double count it. Include tool and scratch-tool
fees where applicable. For every task record requested/effective model and effort;
observed or estimated input, cached input, cache writes, and output (including
reasoning); source of metrics; and whether root cumulative metrics already include
child totals. Unknown actual cost is `unknown`, never zero. Do not promise
instrumentation that is unavailable.

Use a matched prior outcome or an authorized controlled benchmark with the same quality
gate, scope, and pricing as baseline. Do not run a second full Astra build merely to
measure. Repricing a mixed token trace as all-Astra is only a routing proxy, not a
measured savings claim or true baseline.

## Target illustration

With equal-token, output-heavy work and output-token shares Astra .08, Sol .04, Terra
.68, Luna .20, model-rate ratios are 1, .40, .24, .024. The normalized mix is
`.08 + .04×.40 + .68×.24 + .20×.024 = .264`. Adding .015 overhead gives `.279`, or
27.9%. This is illustrative only: shares are not task counts or effort benchmarks, and
worker token volume may differ. A Terra-heavy equal-token mix makes 10% implausible;
reach it only with more cheap work or measured token savings. Never force quotas over
quality.

Forecast `Cmix / Cbaseline`; target `<= .30` and aspirational `.10`. Reserve review
and one correction, then reforecast after each phase. A miss triggers routing/context
optimization and disclosure, not scope reduction.
