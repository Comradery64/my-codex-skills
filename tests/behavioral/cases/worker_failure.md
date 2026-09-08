# Worker failure

## INPUT

The Harbor inventory project is authorized to deliver two independent changes: validate the warehouse import feed and update the receiving dashboard labels. The budget has ample remaining capacity. The import-validation package was assigned to a worker with ownership of `src/imports/validator.py` and `tests/imports/test_validator.py`.

Its first receipt says the targeted test command failed because a malformed supplier code was accepted. The worker attempted one bounded repair, adding a format check, then reran the same command. The second receipt reports a different failure: a valid legacy supplier code is now rejected. The receipts name `test_rejects_malformed` (input `WH-??`) and `test_accepts_legacy` (input `WH-12`), the changed files, and that the worker stopped after the one repair attempt. The approved contract accepts legacy prefixed codes and modern numeric codes but rejects punctuation-only suffixes. No approval was given to broaden the import rules or rewrite the parser.

Separately, the dashboard-label package is ready and disjoint. It owns `web/receiving/labels.ts` and `web/receiving/labels.test.ts`; its contract is to replace three approved display names and run its focused tests. No other worker owns those paths. The status board remains active and includes both worker receipts, the remaining budget, and the ready dashboard package.
