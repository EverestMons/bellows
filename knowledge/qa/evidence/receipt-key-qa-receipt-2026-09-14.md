# QA Receipt — receipt-key (thread 321, 2026-09-14)

**Plan:** `executable-100112` | **Step:** 2 (QA) | **Date:** 2026-09-15

## DEV commits numstat (71c6bfc3..90de0fb1)

```
4       3       bellows.py
27      0       knowledge/development/dev-log-receipt-key-2026-09-14.md
117     0       knowledge/mutants/receipt-key.json
25      0       knowledge/mutants/receipt-key.run.txt
28      17      notifier.py
52      0       tests/test_abandoned_runner_close.py
462     0       tests/test_notifier_coverage.py
```

## Item 2 — Pages counted through their tests

Seven node ids run with `-v`; the daemon that ran STEP 1 loaded the old `notifier.py` and `bellows.py` — the restart is owed after close. No call into the module outside pytest; nothing pages.

```
tests/test_notifier_coverage.py::test_6a_receipt_key_attended_suppresses_page PASSED [ 14%]
tests/test_notifier_coverage.py::test_6b_no_receipt_key_falls_back_to_id_pages PASSED [ 28%]
tests/test_notifier_coverage.py::test_6c_neighbour_receipt_slug_mismatch_pages PASSED [ 42%]
tests/test_notifier_coverage.py::test_9f_final_verdict_page_carries_receipt_key PASSED [ 57%]
tests/test_notifier_coverage.py::test_9h_failure_page_after_mint_pages_when_attended PASSED [ 71%]
tests/test_notifier_coverage.py::test_9i_stale_checkout_page_pages_when_attended PASSED [ 85%]
tests/test_abandoned_runner_close.py::test_refusal_page_pages_when_attended PASSED [100%]
```

6a counts 0 pushes (attended receipt suppresses the verdict page). 6b counts 1 push (no receipt under the id — today's fallback, pinned). 6c counts 1 push (neighbour receipt's JSON slug ≠ stem — no match). 9f asserts `receipt_key=="executable-no-header-2026-04-24"` and `plan_slug=="1"` captured from the verdict page call. 9h counts 1 push (failure page pages despite attended receipt — attending session cannot see failures). 9i counts 1 push (stale-checkout page pages despite attended receipt — attending session cannot see wire-A holds). c-t26 counts 1 push (done-name-taken refusal pages despite attended receipt — attending session cannot see refusals).

## Item 3 — Production writes

None. No lane file, no live lifecycle row, no receipt, no daemon act, no page. Only the two evidence files (`receipt-key-suite-2026-09-14.txt`, this file) were written.

## Verification

| Item | Description | Status |
|------|-------------|--------|
| 1 | Full suite: 2483 passed, two non-running tests (test_gate_watcher live-DB; test_fallback_live_wal_window version gate), zero failed | ✅ |
| 2 | Seven page-counting tests all PASSED; daemon restart owed; nothing pages outside pytest | ✅ |
| 3 | No production writes beyond the two evidence files | ✅ |

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100112/knowledge/qa/evidence/
Files verified: 1
```

