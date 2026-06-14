# Ledger Extraction Fix + in_progress-Strand Recovery — QA Report

**Date:** 2026-06-14 | **Plan:** 54 | **Agent:** Bellows QA | **Step:** 2

---

## Verification Table

| # | Check | Evidence File | Status |
|---|---|---|---|
| 1 | Full suite — 675 passed, 0 failed, 9 new tests match dev log | `full_suite_tail.txt` | ✅ |
| 2 | Multi-turn extraction — regression repro proves intermediate assistant turn ledger now extracted; single-turn backward compatible | `multiturn_extraction.txt` | ✅ |
| 3 | Defense WARN — fires on heading-present-but-empty-parse; silent when populated; silent when no heading | `defense_warn.txt` | ✅ |
| 4 | in_progress recovery — stranded (no worktree, past age guard) → abandoned+closed_at; worktree-present NOT touched; age-guarded NOT touched; claimed-path regression intact | `recovery.txt` | ✅ |
| 5 | No regression to existing extraction — ceo_flags, verdict_requested, result all parse from final message; 9 runner-parser integration tests pass | `existing_extraction.txt` | ✅ |
| 6 | Scope — only in-scope files modified (runner.py, parser.py, bellows.py, lifecycle.py, test files, dev log) | `scope.txt` | ✅ |

---

## Verification Details

### 1. Full Suite

`python3 -m pytest tests/` — 675 passed, 1 warning (urllib3/OpenSSL), 0 failures. New test count: 9 (2 runner + 3 bellows + 4 lifecycle) matches dev log declaration.

### 2. Multi-Turn Extraction (Regression Repro)

`test_multiturn_ledger_extraction` constructs the exact regression scenario from diagnostic 53: an intermediate `type: "assistant"` event carries `### Ledger Updates > #### Prompt Feedback`, followed by a final `type: "result"` with a short summary (no ledger). Before the fix, the parser only read the final result field — ledger was all-None. After the fix, the runner concatenates all assistant text into `_all_assistant_text`, and the parser extracts ledger from it.

Assertions verified:
- `result["ledger_updates"]["feedback"] is not None`
- `"Multi-turn observation" in result["ledger_updates"]["feedback"]`

`test_single_turn_ledger_extraction_still_works` confirms backward compatibility: ledger in the final result text is still extracted.

### 3. Defense WARN

Three tests in `TestLedgerDefenseWarn`:
- **Fires:** raw text has `### Ledger Updates` but parsed ledger all-None → stdout contains `"agent emitted ### Ledger Updates but parser extracted nothing"`
- **Silent (populated):** parsed ledger has content → no WARN
- **Silent (no heading):** raw text has no heading → no WARN

### 4. in_progress Recovery

Four tests in `TestInProgressStrandRecovery`:
- **Stranded recovered:** in_progress + no worktree + backdated 10min → `abandoned` + `closed_at` set
- **Worktree present:** in_progress + worktree exists → `skipped_worktree_exists`, state unchanged
- **Age guarded:** in_progress + no worktree + just created → `skipped_too_recent`, state unchanged
- **Claimed regression:** existing claimed-path recovery still works alongside in_progress recovery

### 5. Existing Extraction

All 9 `test_runner_parser.py` integration tests pass — covering `ceo_flags` (bulleted + None cases), `verdict_requested` (present, absent, mid-text), and `result` (clean, blocked). These parse from `result_text` (final message only) — unaffected by the multi-turn fix which only touches `_all_assistant_text` for ledger extraction.

### 6. Scope

`git diff HEAD~1 --stat` shows 8 files changed, all in scope: `runner.py`, `parser.py`, `bellows.py`, `lifecycle.py`, `tests/test_runner.py`, `tests/test_bellows.py`, `tests/test_lifecycle.py`, and the dev log deposit. No out-of-scope files.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/54/knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/
Files verified: 6
```

---

## Flags for CEO

1. **DAEMON RESTART REQUIRED** — do NOT restart until this plan fully closes. The restart activates the fix AND triggers the `recover_half_claimed` recovery that cleans plan 48 (verify post-restart: plan 48 no longer in the `closed_at IS NULL` set).

2. **RE-CANARY** — dispatch a fresh PROJECT_STATUS+feedback canary after restart. It must now land both ledgers (multi-turn extraction fix is active).

3. **Slice 3 (FORWARD) unblocks only after the re-canary passes** — the Forward Register uses the same `### Ledger Updates` extraction path. The fix unblocks it, but the re-canary proves it works end-to-end.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed six verification checks with executed evidence for the ledger extraction multi-turn fix, defense-in-depth WARN, and in_progress-strand recovery. Full suite 675/675 green, 9 new tests match dev log, all verification criteria met. Scope is clean — only in-scope files modified.

### Files Deposited
- `knowledge/qa/ledger-extraction-recovery-fix-qa-report-2026-06-14.md` — this QA report
- `knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/full_suite_tail.txt`
- `knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/multiturn_extraction.txt`
- `knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/defense_warn.txt`
- `knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/recovery.txt`
- `knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/existing_extraction.txt`
- `knowledge/qa/evidence/ledger-extraction-recovery-fix-2026-06-14/scope.txt`

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- All 6 verification checks passed with executed evidence — no issues found
- Scope is clean, no out-of-scope files modified

### Flags for CEO
1. DAEMON RESTART REQUIRED — do NOT restart until this plan fully closes; the restart activates the fix AND triggers recovery that cleans plan 48
2. RE-CANARY — dispatch a fresh PROJECT_STATUS+feedback canary after restart; must now land both ledgers
3. Slice 3 (FORWARD) unblocks only after the re-canary passes

### Flags for Next Step
- None (final QA step)

### Ledger Updates
#### Prompt Feedback
**2026-06-14 — ledger-extraction-recovery-fix (Bellows QA Step 2)**

1. **Dev log was comprehensive and accurate.** All test counts, file lists, and design decisions matched executed results exactly. No discrepancies found between dev log claims and actual state.

2. **Test quality is strong.** The multi-turn regression repro test precisely reconstructs the diagnostic 53 scenario. Recovery tests cover all three discriminant paths (stranded, worktree-present, age-guarded) with explicit assertions on both the action tuple and DB state.

#### Project Status
- 2026-06-14: **Ledger extraction multi-turn fix + in_progress recovery QA verified (plan 54 Step 2).** 675/675 tests green, 9 new tests. All 6 verification checks passed. DAEMON RESTART REQUIRED to activate fix + trigger plan-48 cleanup. Re-canary needed post-restart before Slice 3 unblocks.
