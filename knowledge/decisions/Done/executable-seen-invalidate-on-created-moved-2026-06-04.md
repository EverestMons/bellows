# Bellows — Invalidate _seen on Re-Deposit via on_created / on_moved (#7, ship)
**Date:** 2026-06-04 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV extracts the existing `on_modified` `_seen`-invalidation logic into one `PlanHandler` helper method `_invalidate_seen_on_redeposit(self, path)` and calls it from `on_created`, `on_modified`, AND `on_moved` (mirroring the parity the watcher currently has only on `on_modified`). Plus 4 regression tests in `tests/test_bellows.py` mirroring the two existing `on_modified` `_seen` tests for the create/move paths. QA is code-level ONLY — no live daemon run, no plan deposited into a watched `decisions/`.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY, then STOPS and waits for CEO verdict before Step 2. Bootstrap: `Read the plan at bellows/knowledge/decisions/executable-seen-invalidate-on-created-moved-2026-06-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## CEO Context

**The #7 BACKLOG entry (2026-05-28 session 15) is partially misframed — verified against current code this session.** The entry proposed two fix shapes: (1) clear `_seen[slug]` at the Done/ transition, or (2) mirror the `on_modified` invalidation into `on_created`. Shape (1) is **already implemented** for daemon-driven closes — the daemon discards `_seen` at both its own Done/ move sites (`bellows.py:699` before the auto-close move; `bellows.py:1457` before the verdict-continue-to-Done move). It is **irrelevant to the actual reproduction**, which is a **Planner-direct** `Filesystem:move_file` close: the daemon never observes that move, so its in-memory `_seen` keeps the stale slug. Shape (2) is the correct fix — refined.

**Confirmed live mechanism.** The watcher has three entry points. `on_modified` (`bellows.py:1194`) invalidates `_seen` (with a lifecycle-prefix guard) before calling `_handle`. `on_created` (`bellows.py:1190`) and `on_moved` (`bellows.py:1208`) call `_handle` with **no** invalidation. `_handle` silently `return`s when the slug is already in `_seen` (`bellows.py:1166`). So after a Planner-direct close-to-Done, a follow-on plan deposited at the same base slug (every diagnostic→executable handoff collides, because `slug_from_path` strips both `diagnostic-`/`executable-` prefixes) arrives via `on_created` or `on_moved` — neither invalidates — and is silently skipped until a daemon restart clears the in-memory set. This is the 2026-05-28 repro (idle heartbeats, manual-rename recovery).

**Fix: one helper, three call sites.** Factor the `on_modified` invalidation body into `PlanHandler._invalidate_seen_on_redeposit(self, path)` and call it from all three callbacks (`on_created` on `src_path`, `on_modified` unchanged in effect, `on_moved` on `dest_path`). The existing `LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")` guard is preserved verbatim and is what prevents re-dispatch loops on Bellows's own lifecycle renames (which fire `on_moved`). The entry named only `on_created`; `on_moved` is included because a cross-directory staging→`decisions/` deposit can surface as `on_moved` on macOS FSEvents, and Bellows's own renames fire `on_moved` (the guard covers them).

**Why NOT inside `_handle`.** `_handle` is also called by the 30s `_rescan` sweep (`from_rescan=True`). Putting invalidation inside `_handle` would discard `_seen` on every rescan tick and defeat the dedup — re-dispatch loop. The invalidation MUST stay in the watcher callbacks, which fire only on genuine filesystem events. This plan does NOT touch `_handle`.

**No self-trip.** This plan is a single executable (not a diagnostic→executable same-slug handoff), so the bug it fixes does not affect its own dispatch. It edits the watcher; the running daemon executes this plan under PRE-edit watcher code, so the new behavior activates only after a daemon restart. Keep local `main` CLEAN at the pause (standard discipline) so this plan's own teardown succeeds.

**Why QA is code-level only.** The unit mechanism is fully provable by mirroring the two existing `on_modified` `_seen` tests (constructed events + `MagicMock` orchestrator + patched `_handle`). A live re-deposit integration test would require closing a plan via Planner-direct move then depositing a same-slug plan into a watched `decisions/` mid-session — unnecessary risk for a watcher-callback unit. No daemon start, no live deposit.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) the target regions of `bellows.py` (the `PlanHandler` watcher callbacks `on_created` / `on_modified` / `on_moved`) and `tests/test_bellows.py` (the two existing tests named below), located via the Pre-edit verification queries — do NOT trust line numbers, locate by symbol/string.
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** `PlanHandler.on_modified` currently contains the `_seen`-invalidation body inline — it computes `filename = os.path.basename(path)`, defines `LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")`, and `if not any(filename.startswith(p) ...)` then `slug = verdict.slug_from_path(path)` and `if slug in self.orchestrator._seen: self.orchestrator._seen.discard(slug)`, THEN `self._handle(path)`. **Query:** `grep -n "def on_modified\|def on_created\|def on_moved\|LIFECYCLE_PREFIXES" bellows.py` then read all three callback bodies. **Expected:** `on_modified` has the invalidation inline; `on_created` is just `self._handle(event.src_path)`; `on_moved` is just `self._handle(event.dest_path)` — NEITHER invalidates.
> 2. **Claim:** `_handle` silently returns when the slug is already in `_seen` (`if verdict.slug_from_path(path) in self.orchestrator._seen: return`), and `_handle` is ALSO called from the rescan path (search for `from_rescan`). **Query:** `grep -n "def _handle\|in self.orchestrator._seen:\|from_rescan" bellows.py`. **Expected:** confirms the `_seen` guard inside `_handle` AND that `_handle` is reachable from `_rescan` — this is WHY the invalidation must live in the callbacks, never inside `_handle`.
> 3. **Claim:** two existing regression tests already prove the `on_modified` behavior and are the mirror template — `test_on_modified_invalidates_seen_for_runnable_plan` and `test_on_modified_preserves_seen_for_lifecycle_renames`. **Query:** `grep -n "def test_on_modified_invalidates_seen_for_runnable_plan\|def test_on_modified_preserves_seen_for_lifecycle_renames" tests/test_bellows.py` and read both bodies. **Expected:** both present; they use `MagicMock()` orchestrator with `_seen = set()`, build an event with `is_directory=False` and `src_path`, patch `handler._handle`, and assert on `_seen` membership + `mock_handle.assert_called_once_with(path)`.
> 4. **Claim:** module-level `verbose`/`os`/`verdict` and the `slug_for` helper used in `_log` slug labels are available in scope for the helper. **Query:** `grep -n "^import os\|^import\|def slug_for\|import verdict\|from .* import verdict\|def _log" bellows.py | head`. **Expected:** `os`, `verdict`, `_log`, and `slug_for` available.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-seen-invalidate-on-created-moved-2026-06-04-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — extract one helper, wire three call sites, do NOT touch `_handle`.**
>
> **(A) New `PlanHandler` method** `_invalidate_seen_on_redeposit(self, path: str)` — move the EXACT invalidation logic currently inline in `on_modified` into this method, preserving the guard verbatim:
> ```
> def _invalidate_seen_on_redeposit(self, path: str):
>     # Invalidate _seen on a re-deposit at an already-seen slug so a genuinely new plan
>     # file (e.g. a follow-on executable deposited at the same base slug after the prior
>     # plan was closed OUT-OF-BAND via a Planner-direct move to Done/, which the daemon
>     # never observes) can be re-dispatched. Guard: never invalidate on Bellows-managed
>     # lifecycle renames (in-progress-/verdict-pending-/halted-) — that would loop.
>     filename = os.path.basename(path)
>     LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")
>     if any(filename.startswith(p) for p in LIFECYCLE_PREFIXES):
>         return
>     slug = verdict.slug_from_path(path)
>     if slug in self.orchestrator._seen:
>         self.orchestrator._seen.discard(slug)
>         _log("INFO", f"re-deposit at seen slug — invalidated _seen so plan can re-dispatch", slug=slug_for(filename))
> ```
> (The `_log` line is the only behavioral addition vs the current inline `on_modified` logic; it fires ONLY on an actual discard, so it is near-silent. Keep it.)
>
> **(B) Wire all three callbacks** to call the helper BEFORE `_handle`:
> ```
> def on_created(self, event):
>     if not event.is_directory:
>         self._invalidate_seen_on_redeposit(event.src_path)
>         self._handle(event.src_path)
>
> def on_modified(self, event):
>     if not event.is_directory:
>         self._invalidate_seen_on_redeposit(event.src_path)
>         self._handle(event.src_path)
>
> def on_moved(self, event):
>     if not event.is_directory:
>         self._invalidate_seen_on_redeposit(event.dest_path)
>         self._handle(event.dest_path)
> ```
> `on_modified` MUST remain behaviorally identical (invalidate-then-handle); you are only refactoring its body into the shared helper. Do NOT modify `_handle`. Do NOT modify the rescan path.
>
> **(C) Regression tests** in `tests/test_bellows.py` — mirror the two existing `on_modified` `_seen` tests for the create and move paths (place them adjacent to the existing pair). Use the SAME `MagicMock` + patched-`_handle` style:
> - `test_on_created_invalidates_seen_for_runnable_plan` — slug pre-seeded in `_seen`; `on_created` fires for a non-lifecycle runnable plan (`event.src_path`). Assert slug discarded before `_handle`; `mock_handle.assert_called_once_with(path)`.
> - `test_on_created_preserves_seen_for_lifecycle_renames` — for each of `in-progress-`/`verdict-pending-`/`halted-` prefixed names via `on_created`, assert slug RETAINED.
> - `test_on_moved_invalidates_seen_for_runnable_plan` — slug pre-seeded; `on_moved` fires with `event.dest_path` a non-lifecycle runnable plan. Assert slug discarded before `_handle`; `mock_handle.assert_called_once_with(dest_path)`.
> - `test_on_moved_preserves_seen_for_lifecycle_renames` — for each lifecycle prefix via `on_moved` (`dest_path`), assert slug RETAINED.
> Confirm the two EXISTING `on_modified` tests still pass unchanged (parity).
>
> **Pre-edit baseline:** run `python3 -m pytest tests/ 2>&1 | tail -15` and record pass/fail counts (note the known carry-over failures) BEFORE editing. Re-run AFTER editing; the only delta must be the 4 new tests passing — ZERO new failures, and the 2 existing `on_modified` tests still green.
>
> **Commit** (do NOT push — Planner handles session-wrap): stage `bellows.py`, `tests/test_bellows.py`, the dev log, and `knowledge/research/agent-prompt-feedback.md`; message `feat(bellows): invalidate _seen on re-deposit via on_created/on_moved (#7)`.
>
> **Dev log** → `knowledge/development/seen-invalidate-on-created-moved-2026-06-04.md`: the helper body, the three wired callbacks, confirmation `_handle` and the rescan path are byte-unchanged, the lifecycle-guard parity, pre-edit verification results, both pytest runs (before/after counts). Include an **Output Receipt** with a "Files Created or Modified" list.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/seen-invalidate-on-created-moved-2026-06-04.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/bellows.py` (modified)
> - `bellows/tests/test_bellows.py` (modified)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this step and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Scope note — code-level ONLY.** Do NOT start the daemon, do NOT deposit any plan into a watched `decisions/` directory, do NOT simulate a live re-deposit. Verify by reading the code and running the unit/regression suite. Nothing in this step should produce a filesystem event a running daemon would observe.
>
> **Before starting, read `knowledge/development/seen-invalidate-on-created-moved-2026-06-04.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (PASS/FAIL) | Evidence |` (use the literal words PASS / FAIL in the Status column — not glyphs). Specifically:
>
> 1. **Helper present and correct** — `PlanHandler._invalidate_seen_on_redeposit(self, path)` exists; computes `filename`, defines the `LIFECYCLE_PREFIXES` guard `("in-progress-", "verdict-pending-", "halted-")`, returns early on any lifecycle prefix, else discards the slug from `self.orchestrator._seen` only when present. Capture the full helper body to `evidence/helper_body.txt`.
> 2. **All three callbacks call the helper before `_handle`** — `on_created` (on `event.src_path`), `on_modified` (on `event.src_path`), `on_moved` (on `event.dest_path`) each call `_invalidate_seen_on_redeposit(...)` THEN `_handle(...)`. Capture all three callback bodies to `evidence/callbacks.txt`.
> 3. **Lifecycle guard preserved verbatim** — the guard tuple is exactly `("in-progress-", "verdict-pending-", "halted-")` and early-returns. Capture to `evidence/guard_check.txt`.
> 4. **`_handle` and the rescan path are byte-unchanged** — `_handle` still contains the `_seen` guard and is NOT modified; no invalidation was added inside `_handle` or the `_rescan` sweep (which would defeat dedup). Capture the relevant `_handle` region + a statement of no-change to `evidence/handle_unchanged.txt`.
> 5. **Diff scope** — `git --no-pager diff -- bellows.py` shows changes confined to (i) the new `_invalidate_seen_on_redeposit` method and (ii) the three callback bodies; nothing else in `bellows.py` changed. Capture to `evidence/diff_scope.txt`.
> 6. **Four new tests exist** — grep `tests/test_bellows.py` for `test_on_created_invalidates_seen_for_runnable_plan`, `test_on_created_preserves_seen_for_lifecycle_renames`, `test_on_moved_invalidates_seen_for_runnable_plan`, `test_on_moved_preserves_seen_for_lifecycle_renames` → all four present. Capture to `evidence/new_tests_grep.txt`.
> 7. **Parity tests intact** — the two existing tests `test_on_modified_invalidates_seen_for_runnable_plan` and `test_on_modified_preserves_seen_for_lifecycle_renames` are still present and pass unchanged. Capture to `evidence/parity_tests.txt`.
> 8. **Dev log complete** — exists with helper body, wired callbacks, `_handle`/rescan no-change confirmation, guard parity, pre-edit verification, both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any FAIL blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) all four new tests appear in verbose output and PASS; (b) the two existing `on_modified` tests still PASS; (c) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (d) total pass count == DEV's reported post-edit number.
>
> **Behavioral spot-checks (read the test assertions, do not invent new live runs).** Confirm from the test bodies: (i) the create/move invalidate tests assert the slug is GONE from `_seen` before `_handle` is called and `_handle` is called once with the right path; (ii) the create/move lifecycle tests assert the slug is RETAINED for each of the three lifecycle prefixes. Capture to `evidence/behavior_spotcheck.txt`.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-seen-invalidate-on-created-moved-2026-06-04`; `qa_report_path` = `bellows/knowledge/qa/seen-invalidate-on-created-moved-2026-06-04.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/seen-invalidate-on-created-moved-2026-06-04/`; `required_evidence_files` = `["helper_body.txt", "callbacks.txt", "guard_check.txt", "handle_unchanged.txt", "diff_scope.txt", "new_tests_grep.txt", "parity_tests.txt", "dev_log_check.txt", "pytest_full.txt", "behavior_spotcheck.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-04 entry under Completed for "Invalidate _seen on re-deposit via on_created/on_moved (#7)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the create/move `_seen` invalidation. The running daemon executed this plan with the pre-edit watcher; the fix activates on the next watcher event after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus↔Sonnet A/B."
>
> **Commit:** stage `knowledge/qa/seen-invalidate-on-created-moved-2026-06-04.md`, the `knowledge/qa/evidence/seen-invalidate-on-created-moved-2026-06-04/` evidence files, and `PROJECT_STATUS.md` with message `qa(bellows): seen-invalidate-on-created-moved verified — helper mirrored to all three callbacks, guard preserved, _handle untouched, zero new regressions (#7)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA seen-invalidate-on-created-moved`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/seen-invalidate-on-created-moved-2026-06-04.md`
> - `bellows/knowledge/qa/evidence/seen-invalidate-on-created-moved-2026-06-04/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
