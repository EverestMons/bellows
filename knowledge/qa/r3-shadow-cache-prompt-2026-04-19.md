# QA Report — R3 Variant (c): Shadow Cache Read-Only Prompt
**Date:** 2026-04-19 | **Plan:** executable-r3-shadow-cache-prompt-2026-04-19

## Summary

All deliverables from Step 2 verified. Four prompt construction sites in `bellows.py` now reference the shadow cache path (`.bellows-cache/*.pristine`) instead of the mutable `in-progress-*` path. Six tests cover all four prompt variants plus shadow file resolution. Full test suite: 118 passed, 11 failed (all 11 pre-existing in test_runner.py/test_runner_parser.py). No regressions. No unintended file modifications.

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `bellows/bellows.py` — shadow_prompt_path variable | Added at line 240 | ✅ | `bellows.py:240` |
| `bellows/bellows.py` — diagnostic prompt f-string | Uses `{shadow_prompt_path}` | ✅ | `bellows.py:243` |
| `bellows/bellows.py` — resume prompt f-string | Uses `{shadow_prompt_path}` | ✅ | `bellows.py:245` |
| `bellows/bellows.py` — fresh Step 1 prompt f-string | Uses `{shadow_prompt_path}` | ✅ | `bellows.py:247` |
| `bellows/bellows.py` — continuation prompt f-string | Uses `{shadow_prompt_path}` | ✅ | `bellows.py:303` |
| `tests/test_bellows.py` — renamed test | `test_run_plan_bootstrap_prompt_uses_shadow_path` | ✅ | `tests/test_bellows.py:987` |
| `tests/test_bellows.py` — updated test | `test_run_plan_resume_step_uses_correct_prompt` with shadow assertions | ✅ | `tests/test_bellows.py` |
| `tests/test_bellows.py` — new continuation test | `test_run_plan_continuation_prompt_uses_shadow_path` | ✅ | `tests/test_bellows.py:1029` |
| `tests/test_bellows.py` — new diagnostic test | `test_run_plan_diagnostic_prompt_uses_shadow_path` | ✅ | `tests/test_bellows.py:1074` |
| `tests/test_bellows.py` — new resume test | `test_run_plan_resume_prompt_uses_shadow_path` | ✅ | `tests/test_bellows.py:1118` |
| `tests/test_bellows.py` — new shadow resolve test | `test_shadow_path_resolves_after_claim` | ✅ | `tests/test_bellows.py:1161` |
| Commit B3 | `6b085b8` — prompt f-string updates | ✅ | `git log` |
| Commit B5 | `5297a06` — test changes | ✅ | `git log` |

## Check Results

| Check | Description | Status | Evidence |
|---|---|---|---|
| Check 1 | No `{plan_path}` or `{inprogress_path}` in prompt f-strings | ✅ | `knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/grep_prompt_sites.txt` |
| Check 2 | Shadow cache write code (lines 224-225) untouched | ✅ | `knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/grep_shadow_write.txt` |
| Check 3 | Unit tests assert shadow path present and in-progress absent | ✅ | `knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/new_tests.txt` |
| Check 4 | Full test suite: 118 passed, 11 failed (all pre-existing) | ✅ | `knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/pytest_full.txt` |
| Check 5 | Diff touches only bellows.py + test_bellows.py (2 files) | ✅ | `knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/git_diff_stat.txt` |

## Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/
Files verified: 5
```

## Final Verdict

**PASS** — All deliverables verified, all checks green, no regressions, no unintended modifications. Variant (c) correctly eliminates plan-mutation risk by routing all four prompt construction sites through the read-only shadow cache.

---

**REMINDER: Bellows daemon restart required before variant (c) takes effect. Next plan will still run under pre-fix Bellows.**
