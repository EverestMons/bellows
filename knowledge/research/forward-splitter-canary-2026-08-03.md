# Forward Splitter Live Canary — 2026-08-03

**Plan:** 295
**Type:** Diagnostic (read-only, post-activation canary)
**Date:** 2026-08-03

---

## Q1 — Is the running daemon executing the post-change module?

**Yes.** The daemon start postdates the code commit.

Plan 294's code commit (`eefd2a96`): **2026-08-03 07:33:24 -0500**

Daemon PID and start time (from `ps -p 86216 -o pid,lstart,command`):

```
  PID STARTED                      COMMAND
86216 Mon Aug  3 08:11:27 2026     /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python bellows.py
```

Daemon PID: **86216**
Daemon started: **Mon Aug 3 08:11:27 2026**

08:11:27 is **38 minutes after** 07:33:24 — the running process loaded the post-change module.

Note: `pgrep -f '[b]ellows\.py'` returned exit code 1 (no match). The daemon was confirmed via `ps aux | grep -F 'bellows'` and `ps -p 86216` instead. The bracket trick may interact differently with macOS pgrep's `-f` flag than with grep.

## Q2 — Before-count

Command: `grep -cE '^\|[[:space:]]*[0-9]+[[:space:]]*\|' /Users/marklehn/Developer/GitHub/bellows/knowledge/FORWARD.md`

Result: **26**

Matches the expected value from the diagnostic.

## Q3 — sanitize_items prediction for the canary payload

Input (the exact two-bullet block from the diagnostic, contiguous, no blank line):

```
- plan_lint section-4 T2 panel check matches a line's opening and never its content, so a plan whose panel line is present but hollow passes the check.
- plan_lint section-4 closing check has its negation strip defeated by one intervening word, so a plan closing on a fold can read as closing dry.
```

`sanitize_items` was reimplemented locally from `bellows.py:1409-1420` (BULLET_RE + sanitize_items) and called on the verbatim payload.

**Result: 2 items returned.**

```
Item 1: "- plan_lint section-4 T2 panel check matches a line's opening and never its content, so a plan whose panel line is present but hollow passes the check."
Item 2: "- plan_lint section-4 closing check has its negation strip defeated by one intervening word, so a plan closing on a fold can read as closing dry."
```

Both lines match `BULLET_RE` (`^(?:-\s|\d+\.\s)`), the bullet count is ≥ 2, so the function takes the multi-bullet branch and returns both items whitespace-normalized.

**Prediction:** If the daemon's post-merge append path calls `sanitize_items` as wired, FORWARD.md should gain **2 rows** (rows 27 and 28), bringing the total to **28**.

## Q4 — Other register writers during the window

No other plan is mid-dispatch:
- `.bellows-worktrees/` contains only `295` (this plan)
- `ps aux | grep -F 'claude -p'` shows only this diagnostic's subprocess (PID 86638)
- No other `claude -p` processes are running

The register should not be written by any concurrent plan during the observation window.

## Unresolved

NONE
