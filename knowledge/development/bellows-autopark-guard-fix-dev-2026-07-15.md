# Bellows Auto-Park Guard Fix — DEV Log

**Plan:** executable-197
**Step:** 1
**Date:** 2026-07-15
**Agent:** Bellows Developer

## Problem

The plan-185 auto-park guard in `runner._check_exit1_rate_limit` (runner.py:165) used a three-part condition to block parking: `num_turns > 1 OR total_output_tokens >= 500 OR has_mutating_tool_use`. The `num_turns` counter incremented on every `user` event carrying a `tool_result` — including read-only tool calls (reading the plan, reading source files). This meant any real step that read more than one file before a cap death was false-blocked from parking.

Proven by exec-194 log: `turns=4, tokens=48, mutating=False` — zero committable work, park blocked purely by `num_turns > 1`.

## Changes

### runner.py — relaxed park-blocking guard

**Before (line 165):**
```python
if num_turns > 1 or total_output_tokens >= 500 or has_mutating_tool_use:
```

**After:**
```python
if has_mutating_tool_use:
```

- Only committable progress (mutating tool use: Write, Edit, Bash, NotebookEdit) blocks a park.
- `num_turns` and `total_output_tokens` are still computed and included in log messages for visibility, but no longer block.
- Log messages updated for both branches:
  - Blocked: "...found but step made committable progress (mutating tool use; turns=N, tokens=T); not parking"
  - Granted (new): "...five_hour event + no committable progress (turns=N, tokens=T, mutating=False); parking"
- Code comment cites exec-194 regression and the `bellows.py` commit-check backstop.

### Backstop verification

Confirmed `bellows._maybe_park_session_limit` (bellows.py:427-437) still checks worktree HEAD against `plan_baseline_sha`. If the agent committed work (HEAD differs from baseline), parking is refused regardless of the runner guard. This backstop is intact, wired at both call sites (bellows.py:678 and :803), and NOT modified. The relaxed runner guard is safe because:
1. No mutating tool use = no commits possible = backstop is a no-op.
2. If somehow a commit did happen without mutating tool use detection, the backstop catches it.

### tests/test_session_limit_park.py — new tests

- `test_exit1_exec194_regression_read_only_turns_parkable`: Exact exec-194 scenario (4 read-only tool_results, tokens=48, mutating=False) — asserts park dict returned.
- `test_exit1_high_turns_high_tokens_no_mutating_parkable`: 10 turns, 2000 tokens, no mutating tool — asserts park dict returned (proves turns/tokens are log-only).
- `test_exit1_five_hour_bash_tool_not_parkable`: five_hour + Bash tool_use — asserts None (mutating progress still blocks).

No existing tests asserted the old `num_turns > 1` / `output_tokens >= 500` blocking behavior without a mutating tool — no test corrections needed.

### Existing tests — no breakage

All existing tests in `test_session_limit_park.py` and `test_runner.py` continue to pass (60 total). The existing `test_exit1_five_hour_with_progress_not_parkable` uses a Write tool_use, so it's still correctly blocked by `has_mutating_tool_use`.

## Test Results

```
======================== 60 passed, 1 warning in 0.45s =========================
```

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Relaxed the auto-park guard in `runner._check_exit1_rate_limit` to block only on committable progress (mutating tool use), fixing the exec-194 regression where read-only tool_results false-blocked parking. Added 3 new tests and verified the bellows.py commit-check backstop is intact.

### Files Deposited
- `knowledge/development/bellows-autopark-guard-fix-dev-2026-07-15.md` — this DEV log

### Files Created or Modified (Code)
- `runner.py` — relaxed park guard condition from `num_turns > 1 or total_output_tokens >= 500 or has_mutating_tool_use` to `has_mutating_tool_use` only; updated log messages for both branches
- `tests/test_session_limit_park.py` — added 3 new tests: exec-194 regression, high-turns/tokens without mutating, Bash tool blocks park

### Decisions Made
- No existing tests needed correction (none encoded the old blocking behavior without a mutating tool)
- Kept `num_turns` and `total_output_tokens` computation for log visibility per plan instruction

### Flags for CEO
- None

### Flags for Next Step
- The `_check_session_limit` (graceful 429 path) is unchanged — its separate num_turns/cost/output_tokens guard is for a different scenario (progress during a successful session) and was not part of this fix scope

### Ledger Updates

#### Prompt Feedback
- Plan instructions were precise and actionable — the exec-194 log citation made root cause verification trivial
- The "verify backstop is intact" sub-task was efficient: grep + read confirmed the wiring without ambiguity
