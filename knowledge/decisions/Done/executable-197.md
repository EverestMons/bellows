# Executable: Bellows auto-park guard fix — stop `num_turns`/`output_tokens` from false-blocking a park

**Type:** Executable
**Project:** bellows
**Depends on:** memory `[[bellows-rate-limit-exit1-no-park]]`; the plan-185 impl (`runner.py:113-175`, `_check_exit1_rate_limit`); diag-184 findings `knowledge/research/bellows-rate-limit-exit1-park-scoping-2026-07-14.md` (context for the original design).
**Created:** 2026-07-15
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 20
**Tier:** Small
**qa_steps:** 2

All commands run from `/Users/marklehn/Developer/GitHub/bellows`. Ops: `--no-pager` on git; RAW pytest output as QA evidence; append prompt feedback via the Output Receipt `### Ledger Updates` -> `#### Prompt Feedback`.

## Root cause — CONFIRMED by the daemon's own log (not a hypothesis)

The plan-185 auto-park (`runner._check_exit1_rate_limit`, `runner.py:113`) declines to park when `num_turns > 1 OR total_output_tokens >= 500 OR has_mutating_tool_use` (`runner.py:165`). `num_turns` is incremented on **every `user` event carrying a `tool_result`** (`runner.py:149`) — i.e. every read-only tool call (reading the plan, reading a source file). So any real step that reads more than one thing before a cap death fails the guard.

Proven for exec-194 (2026-07-15) by the daemon's own log line:
```
runner: five_hour rate_limit_event found but step had progress (turns=4, tokens=48, mutating=False); not parking
```
`mutating=False` = ZERO committable work; `tokens=48` = trivial; the park was blocked **purely by `num_turns > 1`** (4 read-only tool_results). The auto-park is effectively dead-on-arrival for any step that reads the plan + a file.

**The fix:** only **committable progress** may block a park. `has_mutating_tool_use` (a `tool_use` in {Write, Edit, Bash, NotebookEdit}) is the true signal — backstopped by `bellows._maybe_park_session_limit`'s worktree-commit check (which refuses to park if the agent actually committed). `num_turns` (read-only tool_results) and `total_output_tokens` (reasoning) are NOT committable progress and must become log-only, not blockers.

---

## STEP 1 — Bellows Developer

---

Read your specialist file at `agents/BELLOWS_DEVELOPER.md` first.

**Files in scope:** `runner.py`, `tests/test_session_limit_park.py` (plus any `tests/test_*.py` whose assertions this change touches), `knowledge/development/bellows-autopark-guard-fix-dev-2026-07-15.md`, `knowledge/research/agent-prompt-feedback.md`.

1. **`runner.py:165` — relax the park-blocking guard.** Change the condition from `if num_turns > 1 or total_output_tokens >= 500 or has_mutating_tool_use:` to block **only** on committable progress: `if has_mutating_tool_use:`. Keep computing `num_turns` and `total_output_tokens` (they stay in the log for visibility) but they no longer block. Update the log messages so the decision + reason are explicit in BOTH branches:
   - blocked branch: "...found but step made committable progress (mutating tool use; turns=N, tokens=T); not parking"
   - **new** granted branch (log BEFORE returning the park dict): "...five_hour event + no committable progress (turns=N, tokens=T, mutating=False); parking" — this is the governance ask: always log WHY a park was granted or declined.
   Add a short code comment citing exec-194 (turns=4, mutating=False) as the regression this fixes and noting the `bellows.py` commit-check backstop.
2. **Verify the backstop is intact (no change unless broken).** Confirm `bellows._maybe_park_session_limit` still refuses to park when the worktree HEAD differs from the plan baseline (agent committed) — this is the safety net that makes relaxing the runner guard safe against stranding committed work. If it is present and wired, do NOT modify it; note the confirmation in the DEV log. If it is missing/unwired, STOP and report (do not silently expand scope).
3. **Tests — `tests/test_session_limit_park.py`:** (a) **regression for exec-194:** a five_hour event + 4 read-only `tool_result` user events (num_turns=4) + `output_tokens` ~48 + NO mutating tool_use -> `_check_exit1_rate_limit` returns a park dict (NOT None). (b) high-turns/high-tokens but NO mutating tool -> parks (proves turns/tokens no longer block). (c) five_hour event + a `Bash`/`Write` tool_use -> returns None (mutating progress still blocks — no stranding). (d) no rate_limit_event -> None. **Find and update any existing test that encoded the old `num_turns <= 1` / `output_tokens < 500` blocking behavior** (e.g. a case asserting NOT-parkable purely on turns/tokens without a mutating tool) — such a test asserts the bug; correct it and note it in the DEV log.
4. **Targeted self-verify:** `python3 -m pytest tests/test_session_limit_park.py tests/test_runner.py -v 2>&1 | tail -30` — read to an explicit pass/fail. Commit.

**Deposits:**
- `knowledge/development/bellows-autopark-guard-fix-dev-2026-07-15.md`

Emit prompt feedback via the Output Receipt `### Ledger Updates` -> `#### Prompt Feedback` section.

---

## STEP 2 — Bellows QA

---

Read your specialist file at `agents/BELLOWS_QA.md` first.

**Files in scope:** `knowledge/qa/evidence/bellows-autopark-guard-fix-qa-2026-07-15.md`.

1. **Full suite:** `python3 -m pytest tests/ -q 2>&1 | cat`. **Deposit the RAW pytest summary line verbatim.** Any failure beyond known pre-existing ones is a regression — halt and report.
2. **Behavior checks (read + assert against the code):** (a) `runner.py:165` blocks a park **only** on `has_mutating_tool_use` (turns/tokens are log-only); (b) the exec-194 scenario (turns=4, tokens=48, mutating=False) now returns a park dict — cite the new regression test; (c) a mutating-tool step still returns None (no stranding); (d) the `bellows._maybe_park_session_limit` worktree-commit backstop is intact; (e) the graceful-429 `_check_session_limit` path is unchanged (no regression).
3. **Rule 17** deliverable verification (Step 1 DEV commit + DEV log present).

Your QA deposit MUST contain, verbatim, the banner section:
`## Rule 20 — QA Self-Check Results`
`**PASSED — SELF-CHECK PASSED**`

**Deposits:**
- `knowledge/qa/evidence/bellows-autopark-guard-fix-qa-2026-07-15.md`

Emit prompt feedback via the Output Receipt `### Ledger Updates` -> `#### Prompt Feedback` section.

---

## Post-merge (CEO / ops)

The fix only takes effect after a **daemon restart** (the running daemon has the old `runner.py` in memory — same as plan 185 required). After merge, restart the Bellows daemon so the relaxed guard goes live, then update memory `[[bellows-rate-limit-exit1-no-park]]` from "auto-park unreliable" back toward "fixed" once a real cap death parks cleanly.
