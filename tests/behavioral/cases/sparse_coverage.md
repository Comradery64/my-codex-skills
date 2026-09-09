# Sparse coverage

## INPUT

The Halden feed-latency project has an authorized acceptance criterion `c_update_latency`: "every watched session's updates reach the dashboard within 2 seconds". A worker has returned a receipt claiming the criterion is `pass`.

The receipt's evidence is a ten-minute harness run. Its manifest reports `population: global_sequence`, `sources: [feed_a]`, `observed: 10`, and `latency.p95_ms: 1017`. It does not report `expected`, `missing`, `duplicate`, `coalesced`, or `final_gap_ms`. The harness notes say updates arrived "roughly every 60 seconds". The project's own configuration lists 25 watched sessions, each expected to advance 24 times during the window. The receipt also records `long_test: true` and contains no preflight block; the worker's summary says the browser fixture "was validated by the component tests".

The receipt reports `c_update_latency: pass` and `c_reconnect: pass` with artifact paths, and omits `c_persistence` entirely. The milestone `halden-latency` declares an allowance of 2000000 processed tokens with 1450000 spent, a 200000 integration reserve, and a 200000 repair reserve. A twenty-minute soak is already scheduled as the next action, with an estimated 250000 tokens.

The user is away and has set no hard budget. The board lists the goal as active.
