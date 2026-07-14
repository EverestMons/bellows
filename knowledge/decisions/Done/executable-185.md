# Executable: Bellows rate-limit `exit 1` auto-park — detect the 5-hour-cap exit-1 + streamed `five_hour` rate_limit_event and park it

**Type:** Executable
**Project:** bellows
**Depends on:** diag-184 findings `knowledge/research/bellows-rate-limit-exit1-park-scoping-2026-07-14.md` (**READ FIRST** — exit-1 data-flow map, detection logic §4, dual guards, `resetsAt` helper §3, 4-case test matrix §6)
**Created:** 2026-07-14
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 20
**Tier:** Small
**qa_steps:** 2

All commands run from `/Users/marklehn/Developer/GitHub/bellows`.

---

## Context

**Root cause (diag-184, confirmed in code).** A 5-hour org usage-cap death exits `claude -p` with a hard **exit 1** (`error: non_zero_exit_1`), signalling the cap ONLY via a streamed `rate_limit_event` (`rateLimitType: "five_hour"`, `resetsAt: <epoch int>`) — never a graceful 429 result. `runner._check_session_limit` (`runner.py:74`) fires only on a graceful 429 result (line 80) containing "session limit" (line 84), so the exit-1 block (`runner.py:246-278`) never detects it → no park → false `gate_failure` + at-risk uncommitted work. This bit invoice-pulse plans 181-QA + 182 on 2026-07-14 (recovered by hand).

**diag-184 resolved the load-bearing unknown:** the full NDJSON stream IS available in-process as `result_stdout` inside the exit-1 block — no plumbing changes; the fix scans it there. **Critical correctness nuance:** a `five_hour` rate_limit_event ALSO appears on SUCCESS runs, so it is diagnostic ONLY when combined with exit-1 AND zero committable progress.

## Hard constraints (all steps)

- **Additive + separate path.** Do NOT alter the existing graceful-429 `_check_session_limit` path (test iv must still pass — no regression). The new detection is a SEPARATE helper invoked only in the exit-1 block.
- **Both guards mandatory (diag-184 §4):** (a) park only when the stream shows NO committable progress — `num_turns <= 1 AND total_output_tokens < 500 AND NOT has_mutating_tool_use` (mutating = any `tool_use` name in {Write, Edit, Bash, NotebookEdit}); (b) park only when a `five_hour` rate_limit_event is present — a bare exit-1 (genuine crash: OOM/segfault/auth) MUST fall through to `gate_failure`, never park (parking would strand the plan waiting for a reset that resolves nothing). A parkable-looking step WITH progress → NOT parked (benign continue-with-reasoning, like plan 182).
- **No changes** to `_resume_parked`, `record_park`, `clear_park`, or the `parked_steps` schema (diag-184 §5: the existing park+resume machinery is correct, reused as-is).
- Ops: `--no-pager` on git; RAW pytest output as QA evidence; append prompt feedback.

---

## STEP 1 — DEV: add exit-1 rate-limit park detection + guards + the 4-case tests

> **Agent:** Bellows Developer. Read your specialist file at `agents/BELLOWS_DEV.md` first (if present).
> **Files in scope:** `runner.py`, `bellows.py`, `tests/test_session_limit_park.py`, **plus any `tests/test_*.py` whose assertions this change touches**, `knowledge/development/bellows-exit1-park-dev-2026-07-14.md`, `knowledge/research/agent-prompt-feedback.md`

1. **`runner.py` — helper `_reset_epoch_from_rate_limit_event(rate_limit_info, plan_slug=None)`** exactly per diag-184 §3: return `float(resetsAt)` when it is a positive number; else `time.time() + 5*3600` with a WARN log.
2. **`runner.py` — helper `_check_exit1_rate_limit(result_stdout, plan_slug=None)`** per diag-184 §4: parse each NDJSON line (skip malformed lines); find a `rate_limit_event` whose `rate_limit_info.rateLimitType == "five_hour"`; compute stream progress — `num_turns` = count of `user` events carrying a `tool_result`; `total_output_tokens` = sum of assistant `usage.output_tokens`; `has_mutating_tool_use` = any `tool_use` block with `name` in {Write, Edit, Bash, NotebookEdit}. Return `{"session_limit": True, "resets_at_epoch": <helper>, "resets_at_raw": <event dict>}` ONLY when a five_hour event is found AND `num_turns <= 1 AND total_output_tokens < 500 AND NOT has_mutating_tool_use`; otherwise return `None`.
3. **`runner.py` — exit-1 block (`runner.py:246-278`):** AFTER the existing transient-retry check and BEFORE the hardcoded gate_failure return, call `_check_exit1_rate_limit(result_stdout, plan_slug)`. If it returns a dict, merge `session_limit` / `resets_at_epoch` / `resets_at_raw` + `stop_reason="session_limit"` into the returned parsed dict (so `bellows._maybe_park_session_limit` parks it). If it returns `None`, preserve ALL existing exit-1 behavior byte-for-byte.
4. **`bellows.py` — secondary guard (diag-184 §4 backup):** in `_maybe_park_session_limit`, add an optional `plan_baseline_sha` parameter; if the worktree HEAD differs from the baseline (agent committed work), do NOT park even if `session_limit` is set. Thread `plan_baseline_sha` from the call site. Defensive: if the sha cannot be computed, fall back to the stream-level guard (never crash the park decision).
5. **Tests — `tests/test_session_limit_park.py`** (diag-184 §6 matrix; mock `subprocess.Popen` to emit the synthetic stream + exit code 1, fixtures in §6): (i) exit-1 + five_hour event + zero progress → parkable, `resets_at_epoch == 1784053800`; (ii) exit-1, NO rate_limit_event → NOT parkable (gate_failure); (iii) exit-1 + five_hour event + a Write `tool_use` + `output_tokens >= 500` → NOT parkable; (iv) graceful 429 "session limit" result (exit 0) → still parkable via the EXISTING `_check_session_limit` path (no regression). Existing tests must pass UNCHANGED — if any fails, halt and report.
6. **Targeted self-verify:** `python3 -m pytest tests/test_session_limit_park.py tests/test_runner.py -v 2>&1 | tail -30` — read to an explicit pass/fail.
7. **Commit** when coherent, tagged `[exit1-park]`.

**Deposits:**
- `runner.py`
- `bellows.py`
- `tests/test_session_limit_park.py`
- `knowledge/development/bellows-exit1-park-dev-2026-07-14.md`
- `knowledge/research/agent-prompt-feedback.md`

---

## STEP 2 — QA: full-suite + code-level verification of the guards

> **FIRST — post a short visible message to chat confirming you are starting the QA step.**
> **Agent:** Bellows QA. Read your specialist file at `agents/BELLOWS_QA.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
> **Files in scope:** `knowledge/qa/bellows-exit1-park-qa-2026-07-14.md`, `knowledge/qa/evidence/bellows-exit1-park-qa-2026-07-14/full-suite.txt`, **plus any `tests/test_*.py` a fix requires**, `knowledge/research/agent-prompt-feedback.md`

1. **Full suite:** `timeout 900 python3 -m pytest tests/ -v 2>&1 | tail -40` — deposit the RAW tail incl. the summary line to `.../full-suite.txt` (a hand-written summary is NOT acceptable evidence). Reconcile the count vs the HEAD baseline; any new failure is a regression.
2. **Code-level verification table** (one row per claim, quoting code + line numbers): (1) `_check_exit1_rate_limit` returns `None` unless a `five_hour` rate_limit_event is present (guard b) — quote it; (2) the progress guard is `num_turns<=1 AND total_output_tokens<500 AND NOT has_mutating_tool_use` — quote it; (3) the exit-1 block calls the helper AFTER the transient-retry check and merges `session_limit` only when the result is non-None — quote the call site + line; (4) the existing graceful-429 `_check_session_limit` path (lines 74-101) is UNCHANGED — `git --no-pager diff HEAD~1 -- runner.py` shows additions around it, no edits to those lines; (5) the `bellows.py` backup guard blocks park when worktree HEAD != baseline — quote it; (6) tests i–iv present + passing — quote the assertions + the pytest result lines; (7) NO change to `_resume_parked` / `record_park` / `clear_park` / `parked_steps` schema — `git --no-pager diff HEAD~1` confirms. Any row fails → report and halt.
3. **MANDATORY Rule 20 banner:** end the QA report with the self-check banner verbatim — a section headed `## Rule 20 — QA Self-Check Results` concluding `**PASSED — SELF-CHECK PASSED**` (only if every row genuinely passed).
4. **Commit** QA artifacts, tagged `[exit1-park]`.

**Deposits:**
- `knowledge/qa/bellows-exit1-park-qa-2026-07-14.md`
- `knowledge/qa/evidence/bellows-exit1-park-qa-2026-07-14/full-suite.txt`
- `knowledge/research/agent-prompt-feedback.md`

---

## After this plan (not in scope)

- **Restart the Bellows daemon** so the new `runner.py`/`bellows.py` code is loaded — the running daemon has the old modules imported; the fix takes effect only on restart (per `bellows/CLAUDE.md` upgrade cadence). Do at the next session-wrap or when convenient.
- Optional future: surface a park/resume count in `status.py`. Not needed now.
