# Bellows — restart-lock-fix QA corrective: green the 4 mock-orchestrator regressions

**Type:** Executable
**Project:** bellows
**Depends on:** `bellows/knowledge/qa/evidence/bellows-restart-lock-fix-2026-08-15/qa-receipt.md` (the QA finding — SOLE source per Rule 27; the 4 test names, root cause, and exact fix are cited FROM THERE), `bellows/knowledge/decisions/halted-executable-430.md` (the plan whose Step-1 guard the fix accommodates; code landed and correct), `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`
**Created:** 2026-08-16
**Author:** Planner
**Slug:** `restart-lock-fix-qa-corrective-2026-08-16`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T0 (no trigger; integration-vs-record pass: run — see below)
**qa_steps:** 2
**Test Scope:** full-suite in QA (Step 2) — baseline is 430's landed state (1049 passed, 4 failed); expected after this fix = 1053 passed, 0 failed (the 4 mock regressions greened, the 13 new 430 tests still passing).
**Execution:** Step 1 (DEV) → Step 2 (QA)

⚠️ **ID NOTE — deposit filename decided AT DEPOSIT.** Deposit as `executable-draft-<HHMMSS>.md`; the daemon mints the id and renames on claim.

⚠️ **Commit discipline (both steps).** Every commit runs as one compound from the repo root (cwd resets between Bash calls): `cd "$(git rev-parse --show-toplevel)" && git add <exact paths> && git commit -m "<msg>" -- <same paths> && git rev-parse HEAD && git show --numstat HEAD`.

---

## Why this exists

executable-430 (the restart-lock fix) landed correct production code — the SIGTERM drain handler, the self-diagnosing lock, and the guarded stop path, all verified — but its full-suite QA found a −4 regression and correctly reported without repairing (QA reports, never repairs), so 430 halted. The regression is entirely test-side: Step 1's correct new guard `if self.orchestrator._shutting_down:` in `PlanHandler._handle` (bellows.py) reads the auto-truthy attribute that `MagicMock()` orchestrators fabricate, so 4 pre-existing tests in `tests/test_bellows.py` that construct a bare `MagicMock()` orchestrator without `_shutting_down` now return early before their assertions. This corrective adds the missing attribute to those mocks so they mirror the real `Bellows` (which sets `self._shutting_down = False` in `__init__`), greens the suite, and carries 430's work to Done. It touches NO production code.

**Cited from the QA finding (Rule 27 — do not re-derive):** the 4 tests are `test_handle_parallel_from_watchdog_adds_pending_not_dispatched`, `test_nonparallel_plan_dispatches_immediately_from_handle`, `test_two_parallel_siblings_collected_as_one_group`, `test_seen_uses_slug_not_path`, all in `tests/test_bellows.py`; each builds a `MagicMock()` orchestrator with `mock_orch._seen = set()` but no `_shutting_down`; the QA-specified fix is `mock_orch._shutting_down = False` on each.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing it, STOP and wait for my confirmation before Step 2.
```

---
---

## STEP 1 — Bellows Developer (add the missing mock attribute; no production change)

---

> **FIRST — post a short visible chat message confirming you are starting Step 1 and naming your first read.** Do NOT rename this file. Read your Bellows specialist file first, then read the QA finding at `knowledge/qa/evidence/bellows-restart-lock-fix-2026-08-15/qa-receipt.md` (§Regression investigation) — your sole source; cite it, do not re-derive. **Task.** In `tests/test_bellows.py`, locate the four tests named in the finding and, wherever each constructs its `MagicMock()` orchestrator (the same setup that sets `mock_orch._seen = set()`), add `mock_orch._shutting_down = False` so the mock mirrors the real `Bellows.__init__` (which sets `self._shutting_down = False`) — this lets `PlanHandler._handle`'s shutdown guard fall through as it did before the 430 change. If the four tests share a mock-construction helper/fixture, set the attribute once THERE (state which in the receipt); if they each build their own, add the line to each of the four. **Touch NO production code and NO other test's behavior** — this is a pure test-mock fix. **Verify (targeted, DEV — not the full suite):** run `pytest tests/test_bellows.py` and confirm 0 failures, and quote the raw summary line (was: 4 of these failing). Commit `tests/test_bellows.py` per the commit-discipline compound. **Deposit** an Output Receipt at `knowledge/dev-logs/restart-lock-qa-corrective-step1-2026-08-16.md` recording: whether a shared fixture or per-test edits, the exact lines added, and the raw `pytest tests/test_bellows.py` summary. Standard prompt feedback protocol → Output Receipt `### Ledger Updates` → `#### Prompt Feedback`.
>
> **Deposits:**
> - `bellows/knowledge/dev-logs/restart-lock-qa-corrective-step1-2026-08-16.md`
> - (code) `bellows/tests/test_bellows.py`
>
> **Scope:**
> - `bellows/tests/test_bellows.py`
> - `bellows/knowledge/dev-logs/restart-lock-qa-corrective-step1-2026-08-16.md`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO confirmation.**

---
---

## STEP 2 — Bellows Security & Testing (QA — full suite green)

---

> **Before starting, read `knowledge/dev-logs/restart-lock-qa-corrective-step1-2026-08-16.md` and check its Output Receipt status; if not Complete, stop and report before proceeding.** Post a short visible chat message confirming you are starting QA. **(A) Rule 20 self-check** — read the canonical block live from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`; the receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, when every item passes, the canonical verdict line `PASSED — SELF-CHECK PASSED`; `required_evidence_files` = the Step-1 dev-log plus the QA evidence file below. **(B) Full-suite verification with RAW output (no summaries):** run the FULL test suite and paste the raw final summary line — it MUST show **1053 passed, 0 failed** (430's landed 1049/4 with the 4 mock regressions now greened; the 13 new 430 tests still passing). Confirm by name that the four previously-failing tests now PASS (quote their raw `PASSED` lines). If the count is anything other than 1053/0, REPORT it as FAIL with the raw evidence and stop — do NOT repair. **(C)** Do NOT signal, kill, or restart the LIVE daemon (PID 3969 remains a deliberate reproduction case per the CEO); verification is via the suite only. **Deposit** the QA receipt at `knowledge/qa/evidence/restart-lock-qa-corrective-2026-08-16/qa-receipt.md`. Commit per the commit-discipline compound. Then, as the final step: move THIS plan to `Done/` via `shutil.move`, and — because this corrective completes the halted 430's work — also `shutil.move` `knowledge/decisions/halted-executable-430.md` to `Done/executable-430.md`, committing both moves. Emit the project-status milestone (restart-lock fix shipped: self-diagnosing lock + SIGTERM drain handler + guarded `bellows.py stop`/`restart` path + dashboard wiring; suite green) + prompt feedback via the Output Receipt `### Ledger Updates` channel — do NOT edit `PROJECT_STATUS.md` directly.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/restart-lock-qa-corrective-2026-08-16/qa-receipt.md`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/restart-lock-qa-corrective-2026-08-16/qa-receipt.md`
> - (housekeeping) this plan → `Done/`; `halted-executable-430.md` → `Done/executable-430.md`
>
> **STOP. Plan complete. Wait for CEO confirmation.**

---
---

## Drafting Cycle

**cycle_tier:** T0 (no trigger fires — test-only mechanical fix, one file, exact change specified by the QA finding; not production, not cross-machine, not destructive, not governance, not novel). Integration-vs-record pass (Lens 4, §2.4): RUN, dry — the fix mirrors the real `Bellows.__init__` (`self._shutting_down = False`, verified bellows.py:1994 in 430's commit `8066311`), so the mocks now match reality; no precedent conflict (QA specified the minimal fix); arithmetic reconciles (1049 passed + 4 greened = 1053/0). No instruction-class findings.

**Closing:** T0 integration-vs-record pass dry; deposited once.
