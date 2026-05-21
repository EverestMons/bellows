# Dev Log — Tier-1 Batch: gitignore + git allowlist + pause_for_verdict WARN

**Date:** 2026-05-21
**Plan:** executable-bellows-tier-1-batch-2026-05-21
**Status:** Complete

---

## Task A — `.gitignore`: add `config.json`

**Pre-edit verification:**
- `grep -n 'config.json' .gitignore` → 0 matches ✅
- `git ls-files | grep '^config.json$'` → 0 matches (not tracked) ✅

**Before** (`.gitignore` lines 11–13):
```
.bellows-cache/
.bellows-worktrees/
```

**After** (`.gitignore` lines 12–14):
```
.bellows-cache/
.bellows-worktrees/
config.json
```

**Post-edit verification:**
- `grep -n 'config.json' .gitignore` → 1 match (line 14) ✅
- `git ls-files | grep '^config.json$'` → 0 matches (not tracked, now ignored) ✅

No `git rm --cached` needed — `config.json` was never tracked in HEAD.

---

## Task B — `.claude/settings.local.json`: narrow git allowlist

**Pre-edit verification:**
- `grep -n '"Bash(git:*)"' .claude/settings.local.json` → 1 match (line 4) ✅

**Before** (line 4):
```json
"Bash(git:*)",
```

**After** (lines 4–14):
```json
"Bash(git add:*)",
"Bash(git commit:*)",
"Bash(git status:*)",
"Bash(git log:*)",
"Bash(git diff:*)",
"Bash(git show:*)",
"Bash(git ls-files:*)",
"Bash(git checkout:*)",
"Bash(git branch:*)",
"Bash(git config:*)",
"Bash(git rev-parse:*)",
```

**Post-edit verification:**
- `grep -n '"Bash(git:*)"' .claude/settings.local.json` → 0 matches (removed) ✅
- All 11 explicit git subcommands present (each returns 1 match) ✅
- `python3 -c "import json; json.load(open('.claude/settings.local.json'))"` → valid JSON ✅

**Note:** `.claude/settings.local.json` is a runtime config file at the main repo root, not tracked in git. The edit was applied on disk. It takes effect immediately on next `claude -p` invocation. This file cannot be committed; it is excluded from the git commit.

---

## Task C — `bellows.py`: WARN on unrecognized `pause_for_verdict`

**Pre-edit verification:**
- `grep -n 'def header_says_pause' bellows.py` → 1 match (line 305) ✅
- `grep -n 'unrecognized pause_for_verdict value' bellows.py` → 0 matches ✅

**Before** (`bellows.py` lines 312–314):
```python
    if pv == "after_qa_step":
        return is_qa_step
    return False
```

**After** (`bellows.py` lines 312–316):
```python
    if pv == "after_qa_step":
        return is_qa_step
    if pv:
        _log("WARN", f"⚠️ unrecognized pause_for_verdict value: {pv!r} (recognized: 'always', 'after_step_1', 'after_qa_step') — treating as no-pause")
    return False
```

**Post-edit verification:**
- `grep -n 'unrecognized pause_for_verdict value' bellows.py` → 1 match (line 315) ✅

The `if pv:` guard avoids warning on empty-string (documented "no directive" state). `_log` called without `slug=` (default `None`) since `header_says_pause` has no slug context.

---

## Summary

All three BACKLOG items addressed:
1. **config.json gitignore** — secret-containing config file now gitignored; was never tracked so no `git rm --cached` needed.
2. **Git allowlist narrowing** — broad `Bash(git:*)` replaced with 11 explicit non-destructive subcommands. `git push`, `git reset --hard`, `git push --force`, `git rebase`, `git filter-repo`, and `git worktree` now require manual approval.
3. **pause_for_verdict WARN** — unrecognized non-empty values now logged at WARN level before implicit `return False`, aiding diagnosis of typos in plan headers.
