# QA Receipt — forward-none-guard-2026-08-13

**Plan:** executable-376 (forward-none-guard-2026-08-13)
**Step:** 2 — QA
**Date:** 2026-08-13
**QA agent context:** independent from Step 1 (commit `247eb9c` made by prior dispatch)

---

## Precondition

Step 1 ran as its own dispatch. `git log --oneline -1 -- bellows.py` returns:

```
247eb9c [376] forward-none-guard-2026-08-13: boundary guard skips NONE-form forward register sections
```

This commit was made before the current context — independence confirmed.

---

## Deliverable Verification

| Item | Ledger | Check | Status |
|------|--------|-------|--------|
| 1 | C3 | Full test suite: 1006 passed, 0 failed, 1 warning (24.93s) | ✅ |
| 2 | C1 | Diff inspection: only the helper `_forward_text_is_empty_or_none` (8 lines) and the call-site guard line changed; `_append_forward_row` body untouched | ✅ |
| 3 | C4 | Restart boundary stated: the running daemon holds old code; the Planner restarts at an idle window | ✅ |
| 4 | — | Raw output deposited in `pytest-full-raw.txt` | ✅ |

---

### Item 1 — Full Suite (C3)

Command: `python3 -m pytest tests/ -q`

Result: **1006 passed, 1 warning in 24.93s**. No failures. Raw output in `pytest-full-raw.txt`.

---

### Item 2 — C1 from the Diff

Command: `git show 247eb9c --numstat --format=`

```
13	1	bellows.py
32	0	knowledge/development/forward-none-guard-dev-2026-08-13.md
60	0	tests/test_bellows.py
```

bellows.py hunks (full diff output):

**Hunk 1 — call-site guard (line 1357 area):**
- The `elif forward_text:` line was rewritten to `elif forward_text and not _forward_text_is_empty_or_none(forward_text):` — this is the boundary guard.
- Two new lines added for the skip path: a new `elif forward_text:` branch that logs `INFO ledger: forward register empty/NONE — nothing to append`.
- Net: 1 deletion (old `elif`), 3 insertions (new `elif` with guard, skip-path `elif`, skip-path log).

**Hunk 2 — new helper (line 1418 area):**
- `_forward_text_is_empty_or_none(text)` added as a standalone function (8 lines + 2 blank lines = 10 insertions).
- Placed near `sanitize_items` per the specification.

**`_append_forward_row` body:** NOT touched. The function appears in the numstat only via the call-site guard change in the `_apply_ledger_updates` caller. The `_append_forward_row` definition and body have zero hunks in this diff. C1 verified.

---

### Item 3 — C4 (Restart Boundary)

The restart boundary: **the running daemon holds old code — the guard goes live only at the next daemon restart, which is the Planner's ops action at an idle window, never the agent's.** Until then the bug remains live and any new junk row is withdrawn by hand. The plan is done when the code and tests land; the restart is recorded at wrap.

---

### Item 4 — Raw Output

All raw test output deposited in `pytest-full-raw.txt` in the evidence directory.

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/376/knowledge/qa/evidence/forward-none-guard-2026-08-13/
Files verified: 2
```
