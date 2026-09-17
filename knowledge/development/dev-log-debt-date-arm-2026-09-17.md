# dev-log — debt-date-arm — 2026-09-17 [100126]

## Pins re-derived (P1 to P5)

TREE_OK (toplevel asserted: /Users/marklehn/Developer/bellows/.bellows-worktrees/100126)
VENV_OK (pytest, yaml, watchdog importable)
BUILDER_PIN_OK (sha256 d01f397c59233d73a79f0c0d414926ef1868ec7232da17e0dc4449b9be892b1e)

**P1** — `sed -n 263,310p hooks/eluvian/wrap_check.py` (untouched tree):
```
    # 3b: the MOST-SKIPPED step. Force an explicit affirmation in today's baton.
    try:
        baton_text = BATON.read_text(errors="replace") if BATON.exists() else ""
    except Exception:
        baton_text = ""
    if caller == "debt" or not session_id:
        swept_ok = any(
            line.strip().lstrip(">").strip().lower().startswith("lessons-swept:")
            and today in line
            for line in baton_text.splitlines()
        )
        if not swept_ok:
            fails.append(
                f"[3b/lessons] No `Lessons-swept: {today}` line in the baton. Do the 3b "
                f"transferable-lessons sweep AS ITS OWN ACT (distinct from the arc note), "
                f"then add a `Lessons-swept: {today} [sid: <session-prefix-8>] — "
                f"<delta, or 'none'>` line to shop_next_session.md and commit."
            )
    else:
        newest = _find_newest_sweep_line(baton_text)
        ...session-keyed arm (unchanged)...
```
→ `:268` is `if caller == "debt" or not session_id:` — matches P1. ✓

**P2** — `sed -n 106,135p tests/test_wrap_3b_keyed.py` (untouched tree):
Arm 5 at `:122–134` shows `test_debt_caller_date_fallback_hit` and
`test_debt_caller_date_fallback_miss` — matches P2. ✓

**P3** — `sed -n 137,185p tests/test_wrap_r2_registry.py` (untouched tree):
`class TestNeverSuppressPositivePrint` at `:137`; `assert len(fails_with) > 0` at `:181`. ✓

**P4** — `sed -n 94,98p hooks/commands/wrap.md` (untouched tree):
```
   **Then add a line to `shop_next_session.md`:**
   `Lessons-swept: <today's date> [sid: <first-8-of-session-id>] — <one-line delta, or 'none'>`
   (the stop-hook lock verifies the NEWEST such line carries THIS session's id;
   the debt hook checks for today's date. Your session prefix is the first 8
   characters of the session UUID — visible in `hooks.log` or receipt filenames).
```
Parenthesis at `:96`: "the debt hook checks for today's date" — matches P4. ✓

**P5** — callers:
- `sed -n 83p hooks/eluvian/wrap_debt_hook.py`: `[sys.executable, str(CHECK), check_sid, "debt"]` ✓
- `sed -n 186p hooks/eluvian/wrap_stop_hook.py`: `[sys.executable, str(CHECK), session_id or "", "stop"]` ✓
- `sed -n 24p hooks/commands/eluvian.md`: bare checker call (thread 409, unchanged) ✓
- `sed -n 548,551p hooks/eluvian/wrap_check.py`: `main()` maps empty arg to no session id ✓
- `stat -f '%i' ~/.claude/eluvian/wrap_check.py hooks/eluvian/wrap_check.py`:
  `13458658` / `38578256` — worktree has its own inode (expected; symlink targets
  main checkout; post-close merge lands the change via symlink). ✓

**Builder check** (`--phase tests --check`, untouched tree):
```
TREE /Users/marklehn/Developer/bellows/.bellows-worktrees/100126: worktree
STATE tests=pristine (0/2) code=pristine (0/3)
anchor T1-arm5-debt-no-3b (tests/test_wrap_3b_keyed.py): count=1
anchor T2-registry-real-debt-arm (tests/test_wrap_r2_registry.py): count=1
anchor C1-debt-skips-3b (hooks/eluvian/wrap_check.py): count=1
anchor C2-wrap-3b-parenthesis (hooks/commands/wrap.md): count=1
CHECK OK: phase tests: 4 anchors unique, 0 file(s) to create; no write performed.
```
exit=0 ✓

**Execution note (P11 / import resolution):** The daemon places this worktree at
`.bellows-worktrees/100126/` which is a child of the main checkout. `depositor.py`'s
`resolve_bellows_root()` traverses up and finds the main checkout's `config.json`;
`cycle_check.py` then inserts the main checkout at `sys.path[0]`. A temporary root
`conftest.py` (never committed; deleted before Item 6) pre-seeded `sys.modules` from
the worktree at conftest-load time, before any fixture chain ran. The mutation run
(Item 6) used `git archive HEAD` in a fresh temp dir outside `.bellows-worktrees`,
so the import resolved from the archived tree directly — no conftest needed there.

## Failing-first (red, then green)

Tests phase applied: `APPLIED: phase tests: 2 edit(s), 0 file(s) created.`

RED (`exit=1`):
```
FAILED tests/test_wrap_3b_keyed.py::test_debt_caller_stale_line_no_3b - asser...
FAILED tests/test_wrap_3b_keyed.py::test_debt_caller_no_sweep_line_no_3b - as...
FAILED tests/test_wrap_3b_keyed.py::test_debt_caller_without_sid_no_3b - asse...
FAILED tests/test_wrap_3b_keyed.py::test_debt_caller_clean_tree_reports_no_debt
4 failed, 30 passed in 3.78s
```
— exactly P10's four named failures (P13: `4 failed`). ✓

Code phase applied: `APPLIED: phase code: 2 edit(s), 1 file(s) created.`

GREEN (`exit=0`):
```
34 passed in 3.36s
```
✓

## Full suite and mutation run

Suite before (untouched tree, Item 2):
`2524 passed, 2 skipped, 9 warnings in 242.40s (0:04:02)` — exit=0 ✓

Suite after (post-code-phase, Item 5):
`2527 passed, 2 skipped, 9 warnings in 243.00s (0:04:03)` — exit=0 ✓

Mutation run (Item 6):
`MUTATION: 3 killed, 0 survived, 0 error` — exit=0 ✓
