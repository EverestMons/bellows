# QA Report — Extract `_perform_startup_sweep` from `Bellows.start()`

**Date:** 2026-05-10
**Plan:** executable-startup-sweep-extract-2026-05-10
**Step:** 2 (QA)

---

## Verification Matrix

| # | Property | Status | Evidence |
|---|----------|--------|----------|
| 1 | New method exists with correct signature | ✅ | `1060:    def _perform_startup_sweep(self) -> list[str]:` |
| 2 | New method placement | ✅ | Method at line 1060, between `_consume_verdicts` (ends line 1058) and `start` (line 1096) |
| 3 | New method returns the orphan list | ✅ | `1094:        return orphaned_removed` — last statement in method body |
| 4 | Prints did NOT move into the method | ✅ | No `print(` calls in lines 1060–1094. Nearest prints: line 1058 (`_consume_verdicts`), line 1103 (`start()`) |
| 5 | `start()` call site simplified | ✅ | `1113:        orphaned_removed = self._perform_startup_sweep()` — appears exactly once |
| 6 | `start()` retains print loop | ✅ | `1115:            print(f"Bellows: startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed")` and `1117:                print(f"  - {rm_name}")` |
| 7 | `start()` no longer contains inline sweep | ✅ | `active_slugs = set()` only at line 1070 (inside `_perform_startup_sweep`), NOT in `start()` (starts line 1096) |
| 8 | Test calls production directly | ✅ | `340:            orphaned_removed = b._perform_startup_sweep()` — appears exactly once |
| 9 | Test no longer replicates sweep logic | ✅ | `active_slugs = set()` not found anywhere in `tests/test_consume_verdicts.py` |
| 10 | Stale NOTE comment removed | ✅ | `NOTE: Done/ loop intentionally absent` not found in `tests/test_consume_verdicts.py` |
| 11 | Existing assertions preserved | ✅ | `342:        assert not orphan_file.exists()` and `345:        assert "verdict-request-bar-2026-05-01-step-1.md" in orphaned_removed` |
| 12 | Full test suite passes | ✅ | `246 passed, 1 failed` — sole failure is pre-existing `test_run_step_timeout`, 0 new failures |
| 13 | LOC delta direction matches diagnostic | ✅ | `bellows.py`: +30/−17 (net +13); `test_consume_verdicts.py`: +1/−28 (net −27); **total net −14** (reduction; diagnostic predicted −24, delta is the 8-line docstring on new method) |

Refactor verified — 13/13 checks passed.

---

## Rule 20 Self-Check

```
RULE 20 SELF-CHECK
  bellows/bellows.py: OK
  bellows/tests/test_consume_verdicts.py: OK
  bellows/knowledge/development/startup-sweep-extract-2026-05-10.md: OK
  bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md: OK
RULE 20 SELF-CHECK PASSED
```
