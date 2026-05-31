# Bellows — No-Match Verdict Warning Dedup (ship)
**Date:** 2026-05-31 | **Tier:** Small | **Dispatch Mode:** bellows | **Model:** claude-sonnet-4-6 | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV adds a module-level dedup guard so the no-match verdict WARN in `_consume_verdicts` logs once per resolved/ file instead of every 30s rescan tick, plus two regression tests. QA verifies the guard, the clear-on-leave behavior, and zero new full-suite regressions.

## CEO Context

Single confirmed-Open BACKLOG item (2026-05-21, Priority 3 audit). `_consume_verdicts` emits `⚠️ no verdict-pending plan found step {N} — leaving in resolved/ for retry` on every rescan (30s) for each unresolved verdict file in `verdicts/resolved/`. Without dedup, a single stuck file produces ~2,880 WARN lines/day. The adjacent stale-verdict WARN is already self-limiting (the file is moved to `processed-` on first detection); this branch is the one remaining un-deduped log site. Verified live this session by direct read of `bellows.py`: the no-match `else` branch is an unguarded `_log("WARN", ...)`; no dedup set exists. Fix shape is the entry's own recommendation — a module-level `_warned_no_match` guard, log-once, clear when the file leaves resolved/. House precedent to mirror: `_NOTIFIED_MISPLACED` (module top) and `_NOTIFIED_MALFORMED` in `verdict.py`.

**Why this plan runs on Sonnet (`Model: claude-sonnet-4-6`):** first item in the Opus→Sonnet execution-routing A/B. This is a deliberately small, mechanical, single-file change with a deterministic test signal — chosen to establish that routing works and to capture a Sonnet wall-time / turn-count / gate-pass data point against the Opus baseline in `logs/*-step.json` + `bellows.db`. The pytest suite is the real regression signal regardless of model; the Rule 20 banner and the Planner's Rule 22 verification catch a misreported pass.

**Daemon-restart note:** Bellows-modifies-Bellows. The running daemon executes this plan under PRE-edit code; the dedup activates only on the next plan dispatched AFTER a daemon restart. The change is confined to the no-match logging branch and does not touch the verdict MATCH path, so it has no effect on this plan's own close. QA flags the restart for the CEO.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) the target regions in `bellows.py` and `tests/test_consume_verdicts.py`, located via the Pre-edit verification queries below (do NOT trust line numbers — locate by symbol/string).
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string.
>
> 1. **Claim:** the no-match WARN site is an unguarded `_log("WARN", ...)` in `_consume_verdicts`. **Query:** `grep -n "no verdict-pending plan found step" bellows.py`. **Expected:** exactly one hit, inside the `else` branch of the `if stale:` block, with no surrounding membership/dedup check.
> 2. **Claim:** the house dedup-set precedent exists at module top. **Query:** `grep -n "_NOTIFIED_MISPLACED" bellows.py`. **Expected:** a module-level `_NOTIFIED_MISPLACED: set[...] = set()` declaration near the top of the file (the placement and style to mirror for the new set).
> 3. **Claim:** two processed-move sites exist where a verdict file leaves `resolved/` (the clear points). **Query:** `grep -n "processed-" bellows.py` and read `_consume_verdicts`. **Expected:** a `shutil.move(... resolved_dir / fname ... processed_path ...)` in BOTH the `if plan_matched:` block (match → consumed) and the `if stale:` block (stale → moved). These are where the new set entry must be cleared.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-no-match-verdict-warning-dedup-2026-05-31-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — one mechanical change in `bellows.py`, three edit points.**
>
> **Edit 1 — module-level dedup set.** Adjacent to the `_NOTIFIED_MISPLACED` declaration at the top of the file, add a `_warned_no_match: set[str] = set()` with a short comment explaining it suppresses repeat no-match WARNs per resolved/ filename, logged once, cleared when the file leaves `resolved/`, and that module-level scope makes the startup-clear automatic. Mirror the style of the `_NOTIFIED_MISPLACED` block.
>
> **Edit 2 — guard the no-match WARN.** In the no-match `else` branch (the site from query 1), wrap the existing `_log("WARN", ...)` so it fires only when `fname not in _warned_no_match`, and add `fname` to the set immediately after logging. Do NOT change the WARN message text. The variable holding the verdict filename at that scope is `fname` (confirm by reading the loop header `for fname in os.listdir(resolved_dir):`).
>
> **Edit 3 — clear on leave.** At BOTH processed-move sites from query 3 (the `if plan_matched:` consumed-move and the `if stale:` stale-move), add `_warned_no_match.discard(fname)` immediately after the `shutil.move(...)` that relocates the file to `processed-{fname}`. `discard` (not `remove`) so a never-warned file is a no-op.
>
> No `global` declaration is needed — the edits mutate the set in place (`.add`/`.discard`), they do not rebind it.
>
> **Regression tests — add to `tests/test_consume_verdicts.py`, mirroring the existing fixture/setup style in that file (resolved/ directory construction, log capture, and any conftest reset).** Add exactly two:
>
> 1. `test_no_match_warning_logged_once` — place a `verdict-<slug>-step-1.md` in `resolved/` with NO paired `verdict-pending-*` plan and NO matching entry in any `Done/` or `halted-*` (so the branch taken is genuinely no-match, not stale). Call `_consume_verdicts()` twice (two rescan ticks). Assert the `no verdict-pending plan found` WARN is emitted exactly once across both calls, and that the file remains in `resolved/`.
> 2. `test_no_match_warning_cleared_when_file_leaves_resolved` — trigger one no-match WARN (file present, `fname` now in `_warned_no_match`), then make the slug stale by creating a `Done/<...>` (or `halted-*`) entry for it, call `_consume_verdicts()` again, and assert: the file was moved to `processed-<fname>` AND `fname` is no longer in `bellows._warned_no_match`. This exercises the clear path deterministically through the stale branch.
>
> **Test-count note:** two tests are sufficient — one proves log-once (the bug), one proves the clear semantics (correct lifecycle). Do not enumerate further permutations.
>
> **CRITICAL — reset module state between tests.** `_warned_no_match` is module-level and leaks across tests. Clear it at the start of each new test (or via the existing autouse fixture pattern in `conftest.py` / `test_consume_verdicts.py`). Confirm no existing `_consume_verdicts` test breaks from leaked state.
>
> **Test execution.** Run the full suite pre-edit and capture the baseline: `python3 -m pytest tests/ -v 2>&1 | tail -120`. Record the pass count and the exact set of pre-existing failures (e.g. `test_run_step_timeout`). After edits, run full suite again. Expected post-edit: your two new tests PASS and zero NEW failures appear beyond the pre-edit carry-over baseline. Capture both runs.
>
> **Anchor verification before commit.** Run and confirm: `grep -n "_warned_no_match" bellows.py` (≥4 hits — declaration, the `not in` guard, the `.add`, and two `.discard` calls); `grep -n "no verdict-pending plan found step" bellows.py` (still exactly one, message unchanged).
>
> **Deposit:** author a dev log to `knowledge/development/no-match-verdict-warning-dedup-2026-05-31.md` documenting: the three edit points with before/after snippets (3-5 lines context each), the Pre-edit verification query results, the two new regression-test functions with their assertions, the pre-edit and post-edit full-suite pytest output (pass/fail counts), the anchor-verification grep results, and the Output Receipt per your specialist file.
>
> **Commit:** stage `bellows.py`, the test additions, and the dev log with message `fix(bellows): dedup no-match verdict WARN in _consume_verdicts — log once per resolved/ file, clear on leave (BACKLOG 2026-05-21)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV no-match warning dedup`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/development/no-match-verdict-warning-dedup-2026-05-31.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/bellows.py` (modified)
> - `bellows/tests/test_consume_verdicts.py` (modified)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this step and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Before starting, read `knowledge/development/no-match-verdict-warning-dedup-2026-05-31.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (✅/❌) | Evidence |`. Specifically:
>
> 1. **Dedup guard present** — the no-match `else` branch in `_consume_verdicts` logs the WARN only when `fname not in _warned_no_match` and adds `fname` after. Read the branch and capture it to `evidence/dedup_guard.txt`. Confirm the WARN message text is unchanged.
> 2. **Module set declared** — `_warned_no_match: set[str] = set()` exists at module top near `_NOTIFIED_MISPLACED`. Capture to `evidence/module_set_decl.txt`.
> 3. **Clear-on-leave present at BOTH sites** — `_warned_no_match.discard(fname)` appears after the `shutil.move(...)` in both the `if plan_matched:` block and the `if stale:` block. Capture both call sites to `evidence/clear_sites.txt`.
> 4. **Regression tests exist** — `grep -n "test_no_match_warning_logged_once\|test_no_match_warning_cleared_when_file_leaves_resolved" tests/test_consume_verdicts.py` → both present. Capture to `evidence/new_tests_grep.txt`.
> 5. **Dev log complete** — `knowledge/development/no-match-verdict-warning-dedup-2026-05-31.md` exists with three edit-point sections (before/after), pre-edit verification results, and both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any ❌ blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -160`. Capture to `evidence/pytest_full.txt`. Verify: (a) both new tests appear in verbose output and PASS; (b) zero NEW failures beyond the carry-over present in DEV's pre-edit baseline (e.g. `test_run_step_timeout`); (c) total pass count = DEV's reported post-edit number.
>
> **Structural checks.**
>
> (a) **Behavior preserved** — confirm the WARN message string is byte-identical to before (dedup must not alter the message). Quote the line. Capture to `evidence/message_unchanged.txt`.
> (b) **No-op safety** — confirm `.discard` (not `.remove`) is used at both clear sites, so a never-warned file does not raise. Note this in the QA report.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-no-match-verdict-warning-dedup-2026-05-31`; `qa_report_path` = `bellows/knowledge/qa/no-match-verdict-warning-dedup-2026-05-31.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/no-match-verdict-warning-dedup-2026-05-31/`; `required_evidence_files` = `["dedup_guard.txt", "module_set_decl.txt", "clear_sites.txt", "new_tests_grep.txt", "dev_log_check.txt", "pytest_full.txt", "message_unchanged.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-31 entry under Completed for "No-match verdict WARN dedup in `_consume_verdicts` — log once per resolved/ file, clear on leave (BACKLOG 2026-05-21)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the no-match WARN dedup. The running daemon executed this plan with pre-edit code; the fix activates on the next plan dispatched after restart."
>
> **Commit:** stage the QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): no-match WARN dedup verified — logs once, clears on leave, zero new regressions (BACKLOG 2026-05-21)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA no-match warning dedup`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/no-match-verdict-warning-dedup-2026-05-31.md`
> - `bellows/knowledge/qa/evidence/no-match-verdict-warning-dedup-2026-05-31/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
