# Bellows — Fix _lc_plan_id derivation for type-prefixed verdict slugs (qa-149 abandoned bug)
**Date:** 2026-07-09 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

**Diagnostic already done (this session).** When QA re-verification plan **qa-149** closed cleanly via continue-to-done (2026-07-09 09:51:35), two downstream systems disagreed with its closed state:
- `status.py` kept showing it as **AWAITING VERDICT** (pointing at a verdict-request file that no longer existed);
- the lifecycle-recovery sweep then marked it **"abandoned"** (09:55:58).

Both symptoms trace to **one line** in `_consume_verdicts` (bellows.py ~2087-2091):
```python
_lc_plan_id = None
try:
    _lc_plan_id = int(lookup_slug)
except (ValueError, TypeError):
    pass  # legacy plan — no lifecycle DB id
```
`lookup_slug` (bellows.py ~2029-2032) strips only the *lifecycle* prefixes (`in-progress-`, `verdict-pending-`, `halted-`, `parked-`) — NOT the *type* prefix. For a `qa-` plan the slug stays `qa-149`, so `int("qa-149")` raises `ValueError` → `_lc_plan_id = None`. That skips the `lifecycle.mark_plan_state(_lc_plan_id, "closed", ...)` call at ~line 2146 (and the same guards on the halt/stop paths at ~2113/2175). lifecycle.db therefore never records qa-149 as closed → `status.py query_awaiting_verdict` (which reads lifecycle.db) shows the phantom, and the recovery sweep marks it abandoned.

**Executable/diagnostic plans dodge this only because their verdict slug is a bare integer (`148`).** Any type-prefixed slug (`qa-<id>`, and any future typed slug) hits the bug — every continue/halt/stop verdict for such a plan silently drops its terminal lifecycle write.

**Fix (locked):** derive `_lc_plan_id` robustly from a type-prefixed OR bare-integer slug, reusing the exact `(?:diagnostic|executable|qa)-(\d+)` shape already established in `recover_plan_id_from_filename` (bellows.py:364) so legacy slug+date names still degrade to `None` (no regression). Plus a bounded one-off repair of the already-mis-marked qa-149 lifecycle row.

**NOT in this plan:** the separate question of *why* qa-type verdict slugs carry the type prefix while executable/diagnostic slugs are bare (a naming inconsistency, not a bug — the robust id parse tolerates both); any status.py refactor.

**Deposit-once discipline:** this file was deposited exactly once. If a second copy appears, that is a claim-dedup bug — do not double-claim.

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-verdict-consume-typed-slug-lcid-2026-07-09.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible chat message confirming you are starting this plan and your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `bellows.py`
> - `tests/test_consume_verdicts.py`
>
> **Task A — robust `_lc_plan_id` derivation.** In `_consume_verdicts` (bellows.py ~2087-2091), replace the `int(lookup_slug)` block with a parse that extracts the integer id from either a type-prefixed slug (`qa-149`, `executable-148`, `diagnostic-N`) OR a bare integer (`148`), and returns `None` for anything else (legacy slug+date names) — no exception, no WARN spam, matching the degrade-gracefully contract of `recover_plan_id_from_filename` (bellows.py:364). Reuse that exact regex shape (`(?:diagnostic|executable|qa)-(\d+)`) rather than inventing a divergent parser; a bare-`(\d+)` fallback covers the executable/diagnostic bare-id slugs. Confirm this feeds all three verdict branches (continue-to-done ~2146, halt ~2113, stop ~2175) so `mark_plan_state` fires for typed-slug plans on every terminal disposition.
>
> **Task B — one-off repair of qa-149.** The already-closed `qa-149` is currently mis-marked in `lifecycle.db` (abandoned/in_progress). Correct it: `lifecycle.mark_plan_state(149, "closed", closed_at=<now iso>, plan_doc_ref="bellows/knowledge/decisions/Done/qa-149.md")` — but ONLY if it is not already "closed" (idempotent; read current state first and log the before/after). This is a bounded data fix, not a schema change.
>
> **Tests (`tests/test_consume_verdicts.py`).** Add coverage: (1) the new id-derivation returns 149 for `qa-149`, 148 for `executable-148`, 148 for bare `148`, and `None` for a legacy `executable-foo-bar-2026-05-28`-style slug. (2) A continue-to-done for a `qa-`-type plan results in `lifecycle.mark_plan_state(..., "closed", ...)` being called with the correct integer id (use the existing test-harness/mocking style in this file — match how the file already exercises `_consume_verdicts`; do NOT spawn the daemon or `claude -p`). If the file's harness can't reach that path cleanly, at minimum unit-test the id-derivation helper directly and note the coverage boundary.
>
> **Self-verify.** Run the FULL suite `python3 -m pytest tests/ -v` (`python3 -m pytest`, NOT the `timeout` binary — unavailable on macOS). Read the tail to an explicit pass/fail; confirm 0 regressions. Then confirm the repair took: query lifecycle.db for plan 149 and show its state is now `closed`. **Commit** with a descriptive message, e.g. `fix(daemon): derive lifecycle plan_id from type-prefixed verdict slugs (qa-149 abandoned)`.
>
> **Deposit:** a dev-log with the root-cause restatement, the id-derivation change, the qa-149 repair before/after, the full-suite tail, commit hash, and an Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/verdict-consume-typed-slug-lcid-2026-07-09.md`
> - `bellows/bellows.py`
> - `bellows/tests/test_consume_verdicts.py`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — QA

---

> **FIRST — post a short visible chat message confirming you are starting Step 2 (QA) and your immediate next action.** Do NOT rename the plan file.
>
> You are Bellows QA. Read `bellows/agents/BELLOWS_QA.md` if present (skip with a note if absent). All commands run from `/Users/marklehn/Developer/GitHub/bellows`. **QA is verification + reporting only — no product-code changes.** If you find a blocker, STOP and report it.
>
> **Scope:**
> - `knowledge/qa/verdict-consume-typed-slug-lcid-qa-2026-07-09.md`
>
> **Verify:**
> 1. `_lc_plan_id` now derives correctly for `qa-149`, `executable-148`, and bare `148`, and returns `None` for legacy slug+date names (read the diff + the new tests).
> 2. The fix feeds all three terminal branches (continue-to-done, halt, stop) — a typed-slug plan gets its `mark_plan_state` on every disposition, not just continue.
> 3. The qa-149 repair took: `lifecycle.db` shows plan 149 state = `closed` (query it), and the repair logic is idempotent (re-running would not double-write).
> 4. Full suite `python3 -m pytest tests/ -v` (`python3 -m pytest`, NOT `timeout`): record exact pass/fail counts, confirm 0 regressions. Apply mechanical Rule 20 / Rule 22 gates.
>
> **MANDATORY — Rule 20 self-check banner.** Your QA deposit MUST contain, verbatim, a section headed exactly `## Rule 20 — QA Self-Check Results` followed (anywhere below it) by a line reading exactly `**PASSED — SELF-CHECK PASSED**`. This is the self-attestation the `rule_20_self_check` gate enforces byte-for-byte (its omission is what stopped plan 148 Step 3). Include it in addition to your per-item PASS/FAIL table and evidence.
>
> **Deposit:** `bellows/knowledge/qa/verdict-consume-typed-slug-lcid-qa-2026-07-09.md` — per-item verdict (PASS/FAIL + evidence), the full-suite tail with counts, the mandatory Rule 20 banner + PASSED line above, and an Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned). Update `bellows/PROJECT_STATUS.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/verdict-consume-typed-slug-lcid-qa-2026-07-09.md`
>
> **STOP. Wait for CEO verdict.**
