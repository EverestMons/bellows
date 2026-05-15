# QA Report — PlanHandler._seen Slug Refactor

**Date:** 2026-05-11
**Plan:** `executable-plan-handler-seen-slug-refactor-2026-05-11`
**Step:** 2 (BELLOWS_QA)

---

## Deliverable Verification

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | `Bellows.__init__` contains `self._seen = set()` | Line 852 | ✅ | `evidence/init_seen.txt` |
| 2 | `PlanHandler.__init__` does NOT contain `self._seen = set()` | Absent from lines 780-784 | ✅ | `evidence/handler_no_seen.txt` |
| 3 | `run_plan` signature includes `bellows=None` | Line 227 | ✅ | `evidence/run_plan_signature.txt` |
| 4 | Auto-close area contains `bellows._seen.discard(` | Line 529 | ✅ | `evidence/auto_close_discard.txt` |
| 5 | `_consume_verdicts` contains two `self._seen.discard(cleanup_slug)` | Lines 1030, 1051 | ✅ | `evidence/consume_verdicts_discards.txt` |
| 6 | PlanHandler `_seen` refs use `self.orchestrator._seen` | 7 instances (6 logical sites; bulk-add at lines 824-825 is one site with 2 references) | ✅ | `evidence/handler_orchestrator_seen.txt` |
| 7 | Four new tests exist | Lines 2830, 2849, 2869, 2912 | ✅ | `evidence/new_tests.txt` |

---

## Targeted Test Run

```
101 passed, 0 failed, 1 warning (0.41s)
```

Full output: `evidence/pytest_targeted.txt`

Zero new failures. No pre-existing `test_run_step_timeout` failure observed (test not in current suite).

---

## Behavioral Regressions

### Dispatch-Window Guard

Instantiated `Bellows` + `PlanHandler`, added slug to `_seen`, called `handler._handle(path)` — `handle_new_plan` was NOT called. Then called `bellows._rescan(handler)` — `handle_new_plan` was NOT called. Guard holds for both code paths.

Full transcript: `evidence/dispatch_window_guard_repl.txt`

### Post-Done/ Re-Dispatch

Added slug to `_seen`, discarded it (simulating continue-to-done), then called `handler._handle(path)` — `handle_new_plan` WAS called and slug re-entered `_seen`. Plan can be re-dispatched after Done/ lifecycle event.

Full transcript: `evidence/post_done_redispatch_repl.txt`

### Post-Halt Re-Dispatch

Added slug to `_seen`, discarded it (simulating halt), then called `handler._handle(path)` — `handle_new_plan` WAS called and slug re-entered `_seen`. Plan can be re-dispatched after halt lifecycle event.

Full transcript: `evidence/post_halt_redispatch_repl.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/plan-handler-seen-slug-refactor-2026-05-11/
Files verified: 11
```
