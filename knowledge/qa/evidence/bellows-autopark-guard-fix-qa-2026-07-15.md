# Bellows Auto-Park Guard Fix — QA Evidence

**Plan:** executable-197
**Step:** 2
**Date:** 2026-07-15
**Agent:** Bellows QA

---

## 1. Full Test Suite

```
808 passed, 1 warning in 19.78s
```

No failures. No regressions beyond the pre-existing urllib3 `NotOpenSSLWarning`.

---

## 2. Behavior Checks

### (a) runner.py:165 blocks only on `has_mutating_tool_use`

**VERIFIED.** The guard at `runner.py:170` is now:

```python
if has_mutating_tool_use:
```

`num_turns` and `total_output_tokens` are still computed (lines 121-122, 149, 154) and included in log messages (lines 171-173, 179-180) but do not appear in the blocking condition. They are log-only.

### (b) exec-194 scenario returns a park dict

**VERIFIED.** Regression test `test_exit1_exec194_regression_read_only_turns_parkable` (`tests/test_session_limit_park.py:479`) constructs the exact exec-194 scenario: 4 read-only `tool_result` user events (turns=4), output_tokens=48, mutating=False. Asserts `result is not None`, `result["session_limit"] is True`, and `result["resets_at_epoch"] == 1784053800.0`. Test passes.

### (c) Mutating-tool step returns None (no stranding)

**VERIFIED.** Two tests confirm this:
- `test_exit1_five_hour_with_progress_not_parkable` (`tests/test_session_limit_park.py:462`): five_hour + Write tool_use → returns None.
- `test_exit1_five_hour_bash_tool_not_parkable` (`tests/test_session_limit_park.py:537`): five_hour + Bash tool_use → returns None. Assertion message: "Bash tool use is mutating — must block park".

### (d) `bellows._maybe_park_session_limit` worktree-commit backstop is intact

**VERIFIED.** `bellows.py:412-437` implements the backstop:
- Accepts `plan_baseline_sha` kwarg (line 417).
- At line 429-436, if `plan_baseline_sha is not None`, captures current SHA via `_capture_git_diff(wt_path)` and returns `False` if it differs from baseline ("agent committed — not parking").
- Wired at both call sites: `bellows.py:678` (with `plan_baseline_sha=pre_diff`) and `bellows.py:803` (same).
- Test `test_maybe_park_backup_guard_blocks_when_head_differs` (`tests/test_session_limit_park.py:660`) verifies the guard returns False when HEAD differs from baseline.

### (e) Graceful-429 `_check_session_limit` path is unchanged

**VERIFIED.** `runner._check_session_limit` at `runner.py:74-98` is completely unmodified by the Step 1 commit (`git diff 9eac3c3^..9eac3c3 -- runner.py` shows zero changes to this function). It still uses its own independent guard: `num_turns > 1 or total_cost > 0 or output_tokens > 0` (line 91). Test `test_graceful_429_session_limit_still_parkable` (`tests/test_session_limit_park.py:552`) confirms the path works correctly.

---

## 3. Rule 17 — Deliverable Verification

| Deliverable | Present | Content Filled | Evidence |
|---|---|---|---|
| Step 1 DEV commit | Yes | `9eac3c3 [197] fix: auto-park guard blocks only on committable progress (mutating tool use)` | `git log --oneline` |
| DEV log | Yes | `knowledge/development/bellows-autopark-guard-fix-dev-2026-07-15.md` — 90 lines, complete Output Receipt | File read |
| `runner.py` change | Yes | Guard relaxed from 3-part condition to `has_mutating_tool_use` only; log messages updated for both branches | `git diff 9eac3c3^..9eac3c3 -- runner.py` |
| 3 new tests | Yes | `test_exit1_exec194_regression_read_only_turns_parkable`, `test_exit1_high_turns_high_tokens_no_mutating_parkable`, `test_exit1_five_hour_bash_tool_not_parkable` | `tests/test_session_limit_park.py:479,518,537` |

---

## Rule 20 — QA Self-Check Results
**PASSED — SELF-CHECK PASSED**

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Ran the full test suite (808 passed), verified all five behavior checks against the code, and confirmed Rule 17 deliverables (Step 1 DEV commit, DEV log, code changes, new tests) are present and correct.

### Files Deposited
- `knowledge/qa/evidence/bellows-autopark-guard-fix-qa-2026-07-15.md` — this QA evidence report

### Files Created or Modified (Code)
- None (QA step — read-only verification)

### Decisions Made
- All behavior checks passed; no anomalies or regressions found

### Flags for CEO
- None

### Flags for Next Step
- None

### Ledger Updates

#### Prompt Feedback
- Plan QA step was well-structured: the five behavior checks mapped cleanly to verifiable assertions in code and tests
- The "cite the new regression test" instruction in check (b) was helpful — it forced traceability between the QA claim and the actual test
