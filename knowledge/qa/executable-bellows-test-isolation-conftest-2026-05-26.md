# Bellows Test-Isolation Conftest — QA Report

**Date:** 2026-05-26 | **Agent:** Bellows QA | **Plan:** executable-bellows-test-isolation-conftest-2026-05-26 | **Step:** 2

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `tests/conftest.py` exists | File present on disk | ✅ | `ls tests/conftest.py` returns file |
| Contains `@pytest.fixture(autouse=True)` | Decorator present | ✅ | Line 5 of file |
| Contains function `isolate_verdicts_dir` | Function definition present | ✅ | Line 6: `def isolate_verdicts_dir(monkeypatch, tmp_path):` |
| Contains `monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")` | Setattr call present | ✅ | Line 9 of file |
| Line count matches prescribed body | Plan text says "7 lines"; actual file is 9 lines (including comment `# tests/conftest.py` and two blank lines per PEP 8). Content matches the verbatim code block prescribed in Step 1 exactly. | ✅ | The prescribed code block in the plan itself contains 9 lines. The "7-LOC" label in the SA diagnostic counted non-blank code lines only. File content is byte-identical to the prescribed body. |

---

## Full-Suite Test Run

**Command:** `python3 -m pytest tests/ -v`

**Result:** `5 failed, 411 passed, 1 warning in 6.14s`

**Failures (all known carry-overs):**

| # | Test | Category |
|---|---|---|
| 1 | `test_decisions.py::TestLoadPhrases::test_loads_known_file` | worktree-context (phrase file not found) |
| 2 | `test_decisions.py::TestLoadPhrases::test_returns_empty_for_missing_file` | worktree-context |
| 3 | `test_decisions.py::TestLoadPhrases::test_includes_known_phrases` | worktree-context |
| 4 | `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` | worktree-context |
| 5 | `test_runner_parser.py::test_run_step_timeout` | timeout assertion |

**Assessment:** 5 failures matches the known carry-over baseline exactly (4 test_decisions.py + 1 test_runner_parser.py). Zero new regressions.

Full output captured at `knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/pytest_full.txt`.

---

## Leak-Closure Verification (Load-Bearing)

**Command:** `ls verdicts/pending/ | grep -v "^archived$"`

**Result:** Empty output — no `verdict-request-*` files present.

The conftest fixture is working: the full test suite ran 416 tests without producing any orphan verdict files in production `verdicts/pending/`.

Evidence captured at `knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/verdicts_pending_post_run.txt`.

---

## Specific-Test Reproduction Check

**Previously-leaking tests (per SA Diagnostic Deliverable B):**

| Test | Result |
|---|---|
| `test_bellows.py::test_apply_defensive_header_defaults_propagates_to_reparsed_header` | PASSED |
| `test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows` | PASSED |

Both tests passed. Post-run `ls verdicts/pending/ | grep -v "^archived$"` confirmed still empty — zero orphan files.

Evidence captured at `knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/previously_leaking_tests.txt`.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/bellows-test-isolation-conftest-2026-05-26/knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/
Files verified: 4
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified the `tests/conftest.py` deliverable from Step 1 (DEV). Ran the full test suite (411 passed, 5 known carry-overs, 0 regressions). Confirmed leak closure: zero orphan verdict files in `verdicts/pending/` after full-suite and individual previously-leaking test runs. Rule 20 self-check executed.

### Files Deposited
- `knowledge/qa/executable-bellows-test-isolation-conftest-2026-05-26.md` — this QA report
- `knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/` — evidence directory (4 files)

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- Line count discrepancy (plan says "7 lines", file has 9 lines) resolved as a counting convention difference in the SA diagnostic — the file content matches the prescribed body verbatim

### Flags for CEO
- None

### Flags for Next Step
- None (this is the final step)
