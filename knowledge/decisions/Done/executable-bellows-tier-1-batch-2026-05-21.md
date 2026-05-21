# Bellows — Tier 1 trivial batch: gitignore, settings allowlist, pause_for_verdict enum WARN
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Three independent BACKLOG items batched into one plan because they touch unrelated files with no interaction risk. Each is a small surgical edit with no behavioral risk to the orchestration loop.

**Item A — `bellows/config.json` not in `.gitignore`.** Per BACKLOG (added 2026-05-21, NEXT_SESSION baton Priority 2): `config.json` contains pushover `app_key` and `user_key` and is currently untracked but not gitignored — risk of accidental secret commit on a `git add -A`. Verified 2026-05-21 by Planner: `.gitignore` does NOT contain `config.json`; `config.json` on disk contains the expected secrets. Fix: append `config.json` to `bellows/.gitignore`.

**Pre-fix verification needed:** confirm `config.json` is not already tracked in HEAD. If `git ls-files | grep config.json` returns a match, the gitignore is insufficient — a `git rm --cached config.json` is also needed to untrack the historical commit and prevent future modifications from being staged. The agent must check and report.

**Item B — `Bash(git:*)` auto-approval too broad in `.claude/settings.local.json`.** Per BACKLOG (added 2026-05-21, NEXT_SESSION baton Priority 2): the current allowlist entry `"Bash(git:*)"` auto-approves all git commands including destructive ones (`git push`, `git reset --hard`, `git push --force`). Per the 2026-05-21 teardown-git-operations diagnostic, agent-side push from worktrees is the root cause of parallel-SHA divergence. Fix: replace `"Bash(git:*)"` with an explicit allowlist of non-destructive git subcommands.

Replacement allowlist (in the order they should appear):
- `"Bash(git add:*)"`
- `"Bash(git commit:*)"`
- `"Bash(git status:*)"`
- `"Bash(git log:*)"`
- `"Bash(git diff:*)"`
- `"Bash(git show:*)"`
- `"Bash(git ls-files:*)"`
- `"Bash(git checkout:*)"`
- `"Bash(git branch:*)"`
- `"Bash(git config:*)"`
- `"Bash(git rev-parse:*)"`

Explicitly omitted (will require manual approval): `git push`, `git reset --hard`, `git push --force`, `git push --force-with-lease`, `git rebase` (rewrites history), `git filter-repo` (Procedure 3 operator-only), `git worktree` (Bellows-internal, daemon handles it).

**Item C — `pause_for_verdict` unvalidated enum WARN at `bellows.py:305-314`.** Per BACKLOG (Priority 3 audit, added 2026-05-21): `header_says_pause` recognizes three string values (`always`, `after_step_1`, `after_qa_step`); any other value (typos, `never`, etc.) silently returns False with no warning. Fix: add a WARN log for unrecognized non-empty values before the implicit `return False` at the end of the function.

Anchor (verbatim from bellows.py):
```python
def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    """Return True if plan header's pause_for_verdict field matches current step."""
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
    return False
```

Replacement (with the WARN added immediately before the final `return False`):
```python
def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    """Return True if plan header's pause_for_verdict field matches current step."""
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
    if pv:
        _log("WARN", f"⚠️ unrecognized pause_for_verdict value: {pv!r} (recognized: 'always', 'after_step_1', 'after_qa_step') — treating as no-pause")
    return False
```

The `if pv:` guard avoids warning on the empty-string case (the documented "no directive present" state, handled by defensive default for sparse multi-step plans).

**Note on `_log` signature:** `header_says_pause` does not receive a `slug` argument, so the WARN call omits `slug=`. `_log` allows `slug=None` (default). The warning will appear without a plan-slug tag, which is acceptable for this kind of plan-header-content warning that fires before the step-execution loop has a slug context.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a 3-item batch of surgical edits.** **Pre-edit verification for all three items:** (1A) Run `grep -n 'config.json' bellows/.gitignore` and confirm 0 matches. (1B) Run `git -C bellows ls-files | grep '^config.json$'` and report whether `config.json` is currently tracked. (2A) Run `grep -n '"Bash(git:\*)"' bellows/.claude/settings.local.json` and confirm exactly 1 match. (3A) Run `grep -n 'def header_says_pause' bellows/bellows.py` and confirm exactly 1 match. (3B) Run `grep -n 'unrecognized pause_for_verdict value' bellows/bellows.py` and confirm exactly 0 matches (the WARN does not yet exist). If any check returns unexpected output, STOP — deposit a verification-mismatch report at `bellows/knowledge/flags/verification-mismatch-tier-1-batch-2026-05-21-step-1.md` documenting actual results, and halt. **Task A — gitignore:** Append `config.json` as a new line to `bellows/.gitignore`. The file should end with a newline; ensure the new entry sits on its own line. If the pre-edit check 1B reported that `config.json` IS currently tracked in HEAD, ALSO run `git -C bellows rm --cached config.json` to untrack it. Either way, capture the resulting state with `git -C bellows ls-files | grep '^config.json$'` (expected: 0 matches after the edit). **Task B — settings allowlist:** Edit `bellows/.claude/settings.local.json`. Locate the line containing `"Bash(git:*)"` and replace it with the 11-entry allowlist specified in the plan Context section above (`Bash(git add:*)` through `Bash(git rev-parse:*)`). Each new entry must be on its own line, comma-separated per JSON array syntax, indented to match surrounding entries. Preserve all other entries in the allowlist unchanged. After the edit, verify the JSON is still valid by running `python3 -c "import json; json.load(open('bellows/.claude/settings.local.json'))"` and confirm no exception. **Task C — pause_for_verdict WARN:** Use `Desktop Commander:edit_block` with the verbatim anchor specified in the plan Context (the entire 9-line `header_says_pause` function body) and replace with the verbatim replacement (the 11-line function body with the WARN inserted before the final `return False`). Preserve indentation exactly (4-space indent matching surrounding code at module-function scope). **Post-edit verification (after all 3 tasks):** (1A) `grep -n 'config.json' bellows/.gitignore` returns exactly 1 match. (1B) `git -C bellows ls-files | grep '^config.json$'` returns 0 matches (the file is now ignored AND not tracked). (2A) `grep -n '"Bash(git:\*)"' bellows/.claude/settings.local.json` returns 0 matches. (2B) `grep -n '"Bash(git add:\*)"' bellows/.claude/settings.local.json` returns 1 match (and the other 10 explicit git subcommands also present). (2C) JSON validity check passes. (3A) `grep -n 'unrecognized pause_for_verdict value' bellows/bellows.py` returns exactly 1 match. **Deposit a dev log:** write to `bellows/knowledge/development/bellows-tier-1-batch-2026-05-21.md` documenting each of the 3 tasks with before/after snippets (3 lines of surrounding context for each), grep verification counts pre and post, the result of the `config.json` tracking check, and a closing paragraph confirming all three BACKLOG items are now addressed. **Commit:** stage `bellows/.gitignore`, `bellows/.claude/settings.local.json`, `bellows/bellows.py`, AND the dev log. If `git rm --cached` was run, that's part of the same commit. Commit message: `chore(bellows): tier-1 batch — gitignore config.json + narrow git allowlist + warn on unrecognized pause_for_verdict`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV tier-1 batch`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/.gitignore` (modified)
> - `bellows/.claude/settings.local.json` (modified)
> - `bellows/bellows.py` (modified)
> - `bellows/knowledge/development/bellows-tier-1-batch-2026-05-21.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read — this is QA for a 3-item batch.** **Before starting, read `bellows/knowledge/development/bellows-tier-1-batch-2026-05-21.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Verification table: | # | Deliverable | Expected | Status (✅/❌) | Evidence |. Specifically: (1) `bellows/.gitignore` contains `config.json` on its own line — `grep -n '^config\\.json$' bellows/.gitignore` returns 1 match; (2) `config.json` is NOT in `git ls-files` — `git -C bellows ls-files | grep '^config\\.json$'` returns 0 matches; (3) `bellows/.claude/settings.local.json` no longer contains `"Bash(git:*)"` — `grep -n '"Bash(git:\*)"' bellows/.claude/settings.local.json` returns 0 matches; (4) `bellows/.claude/settings.local.json` contains all 11 explicit git subcommand entries — separate grep for each (`Bash(git add:*)`, `Bash(git commit:*)`, `Bash(git status:*)`, `Bash(git log:*)`, `Bash(git diff:*)`, `Bash(git show:*)`, `Bash(git ls-files:*)`, `Bash(git checkout:*)`, `Bash(git branch:*)`, `Bash(git config:*)`, `Bash(git rev-parse:*)`) — each returns exactly 1 match; (5) `bellows/.claude/settings.local.json` is valid JSON — `python3 -c "import json; json.load(open('bellows/.claude/settings.local.json'))"` runs without exception; (6) `bellows.py` contains the new WARN line — `grep -n 'unrecognized pause_for_verdict value' bellows/bellows.py` returns 1 match; (7) `bellows.py` `header_says_pause` function structure is preserved — `grep -n 'def header_says_pause' bellows/bellows.py` returns 1 match (line ~305) and the function body still contains all three recognized-value branches; (8) dev log file exists with all 3 tasks documented; (9) `agent-prompt-feedback.md` has a new 2026-05-21 entry from this plan. Capture each grep to evidence files in `bellows/knowledge/qa/evidence/executable-bellows-tier-1-batch-2026-05-21/`: `gitignore.txt`, `not_tracked.txt`, `no_git_star.txt`, `git_subcommands.txt`, `json_valid.txt`, `warn_present.txt`, `header_says_pause_intact.txt`, `dev_log_present.txt`, `feedback_entry.txt`. **Targeted test run.** Run `python3 -m pytest tests/test_bellows.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-tier-1-batch-2026-05-21/pytest_targeted.txt`. The changes are: (a) gitignore — not exercised by tests; (b) settings allowlist — not exercised by tests; (c) `header_says_pause` — exercised by tests covering pause routing. The added WARN does not change the function's return value for any recognized-value input. All existing tests should pass unchanged. If any test fails, report to CEO — do not blindly "fix" by adjusting assertions. **Structural compliance check.** Run `git -C bellows diff HEAD~1 -- bellows.py bellows/.gitignore bellows/.claude/settings.local.json 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-tier-1-batch-2026-05-21/diff.txt`. Verify: bellows.py shows exactly +1 line (the WARN); bellows/.gitignore shows exactly +1 line (`config.json`); bellows/.claude/settings.local.json shows -1/+11 line delta (the broad `Bash(git:*)` removed, the 11 explicit entries added). No other modifications to any file. **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-bellows-tier-1-batch-2026-05-21`; `qa_report_path` = `bellows/knowledge/qa/executable-bellows-tier-1-batch-2026-05-21.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/executable-bellows-tier-1-batch-2026-05-21/`; `required_evidence_files` = `["gitignore.txt", "not_tracked.txt", "no_git_star.txt", "git_subcommands.txt", "json_valid.txt", "warn_present.txt", "header_says_pause_intact.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_targeted.txt", "diff.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-21 entry under Completed for "Bellows tier-1 batch — gitignore config.json + narrow git allowlist + warn on unrecognized pause_for_verdict (3 BACKLOG items closed)" with a one-paragraph summary. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): tier-1 batch — 3 BACKLOG items`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA tier-1 batch`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-bellows-tier-1-batch-2026-05-21.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-tier-1-batch-2026-05-21/` (11 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---

## Daemon-restart note

Item C touches `bellows.py`, which Bellows does not hot-reload (Rule 35 / Restart Discipline). The running daemon continues executing pre-fix `header_says_pause` through this plan's lifecycle. Items A (gitignore) and B (settings) take effect immediately (gitignore reads from disk on each git operation; .claude settings read on each `claude -p` invocation by the runner). After plan close + daemon restart, the new pause_for_verdict WARN becomes effective for all future plan dispatches.
