# Bellows Hardening Batch — Freshness & Disposition Audit
**Date:** 2026-05-26 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** after_step_1 | **auto_close:** false

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

## CEO Context

The session-6 baton (`bellows/NEXT_SESSION.md`) carried four items as the next-session horizon for Bellows hardening. A Phase 1.5 freshness check at session-7 plan-authoring time revealed that **Item 2** (`_extract_plan_required_deposits` returns a set, making `md_paths[0]` hash-dependent) was already shipped 2026-05-25 via `executable-extract-plan-required-deposits-set-to-list-2026-05-25` (Option a — deterministic ordered list with `dict.fromkeys` dedup). QA confirmed both consumers at `gates.py:450` and `gates.py:505` unchanged and now deterministic. The BACKLOG hygiene closure for Item 2 didn't happen, and the entry propagated as Open across two batons.

This is the third recurrence in three days of the BACKLOG-stale-claim pattern captured in the 2026-05-26 LESSONS entry "BACKLOG entries authored from current-state grep without scanning Closed history can misframe already-evaluated work." The fix is the same as before: grep before treating a baton-carried item as live work.

Before authoring the executable batch for items 1, 3, 4, the Planner needs the same freshness check applied to each. Items 3 and 4 reference specific line numbers (`bellows.py:494`, `bellows.py:381`, `gates.py:441`, `dispatch_mode_validator` lifecycle) that may have shifted under unrelated work — items of session 6 (Fix F removal at `bellows.py:495`, `bellows.py:587`) and the multiple `gates.py` plans of the 2026-05-2x cluster routinely touch these regions.

This is a single SA step. No DEV, no QA. Findings feed directly into the Planner's next session — either an executable batch covering only confirmed-Open items, or further investigation if items have shifted.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-bellows-hardening-batch-freshness-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-bellows-hardening-batch-freshness-2026-05-26.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary read — this is a code-state audit against specific line numbers and BACKLOG hypotheses, no domain interpretation required.
>
> **Task.** Verify the current code state of four BACKLOG items still framed as Open in `bellows/knowledge/BACKLOG.md`, and produce a Gap Assessment table the Planner can cite directly when authoring the executable batch.
>
> **Inputs to read.**
> - `bellows/knowledge/BACKLOG.md` Open section — confirm the four entries below are still listed as Open.
> - `bellows/gates.py` lines 360–470 (Item 1's `_gate_rule_20_self_check` evidence-string branches and `_extract_plan_required_deposits`).
> - `bellows/bellows.py` lines 370–510 (Item 4's `_apply_defensive_header_defaults` definition and the suspect re-parse at line ~494).
> - `bellows/bellows.py` — search for `dispatch_mode_validator` and `_rejected` (or whatever the rejection cache is named) to locate Item 3's cache and watchdog `on_modified` handler.
> - The `Closed` section of `bellows/knowledge/BACKLOG.md` — confirm none of items 1, 3, 4 appear there (Item 2 has been confirmed shipped via QA report `bellows/knowledge/qa/executable-extract-plan-required-deposits-set-to-list-2026-05-25.md`).
>
> **Items to audit (in order).**
>
> **Item 1 — `_gate_rule_20_self_check` ambiguous evidence string at `gates.py:441`.** The BACKLOG entry claims gates.py:441 (`if not md_paths`) and gates.py:464 (`if banner not in content`) both emit the same evidence string `"no QA deposit contains Rule 20 self-check banner"`. Verify by reading the function. For each branch, quote the exact `failures.append(...)` call (or equivalent) including its evidence string. Report whether the two branches currently emit identical or distinct strings.
>
> **Item 2 — `_extract_plan_required_deposits` set-vs-list (confirmation only).** Already-shipped confirmation. Verify that the function returns a list (not a set), preserves insertion order, and contains a `dict.fromkeys` dedup call. Quote the function's return statement and the `paths = []` initializer to confirm. This item is for BACKLOG hygiene closure, not a fix — the Planner needs the verified evidence to close the entry.
>
> **Item 3 — Path-keyed rejection cache for `dispatch_mode_validator`.** The BACKLOG entry claims that when `dispatch_mode_validator` rejects a plan for a missing header field (Rule 35), a corrected re-deposit at the same filename is silently skipped on subsequent scans. Locate the rejection cache: what is its variable name, what is its key (filename, full path, content hash, slug)? Locate the watchdog `on_modified` handler: does it currently invalidate any cache on file modification? Quote the relevant lines. Report whether the entry's claim (cache keyed by filename/path, not invalidated on `on_modified`) matches current code.
>
> **Item 4 — `_apply_defensive_header_defaults` ineffective at runtime.** The BACKLOG entry claims `_apply_defensive_header_defaults` at `bellows.py:381` mutates the local `header` dict to insert `pause_for_verdict = "after_step_1"` when the parse looks sparse, BUT at `bellows.py:494`, `header` is reassigned from `gate_result.get("plan_header", {})` (a re-parse from `gates.check()` that does not apply the default). The result: header used by `header_says_pause()` at lines ~502 and ~590 does not contain the defensive default at intermediate steps. Verify by reading both locations. Quote: (a) the function `_apply_defensive_header_defaults` definition, (b) the call site that first invokes it (around line 381), (c) the `header = gate_result.get("plan_header", {})` reassignment (around line 494), (d) the next two `header_says_pause(header, ...)` consumers. Confirm or refute the entry's claim about the reassignment dropping the default.
>
> **Output format — Gap Assessment table (Rule 27 Diagnostic Prompt Engineering).** Produce the table with these exact columns:
>
> ```
> | Item | BACKLOG Claim | Current State (verbatim line + quote) | Status | Recommended Disposition |
> ```
>
> - **Status** is one of: `Open-confirmed` (claim matches code, fix still warranted), `Open-shifted` (claim partially matches, code has moved, fix needs re-scoping), `Closed-shipped` (already fixed, BACKLOG hygiene closure only), `Closed-overturned` (claim was wrong, no fix needed).
> - **Recommended Disposition** is the Planner-actionable next step in one sentence: e.g., "Include in executable batch as 1-line evidence string change at gates.py:441," or "Retire from BACKLOG with reference to 2026-05-25 QA report," or "Re-scope — line number shifted to bellows.py:N; same fix shape applies."
>
> **Q5 — Verification block (Rule 39).** For each item's quoted line, report the exact line number found in the current file. This is the load-bearing claim of the entire diagnostic — the executable batch's line numbers depend on it.
>
> **Q6 — Cross-item dependency check.** Items 1 and 4 both touch `_gate_rule_20_self_check` and `_apply_defensive_header_defaults` regions of code; if any items 1, 3, 4 ship together, are there ordering constraints (e.g., must Item 4's reassignment fix land before Item 1's evidence string change to avoid merge churn), or are they independent? Answer in one paragraph.
>
> **Deposit.** `bellows/knowledge/research/bellows-hardening-batch-freshness-2026-05-26.md` containing the Gap Assessment table (Items 1–4), Q5 verification block, Q6 ordering analysis, and a Flags-for-CEO section recommending exactly one of: (a) executable batch covering confirmed-Open subset, with Item 2 closed via BACKLOG hygiene edit; (b) further investigation needed on specific items; (c) all items shifted, batch concept abandoned. Do NOT author the executable plan itself — flag for the Planner.
>
> **Constraints.** Do NOT modify source code. Do NOT modify gates.py, bellows.py, or BACKLOG.md. This is a read-only investigation. Cite line numbers and quote evidence verbatim. The diagnostic's load-bearing job is to ground the Planner's next plan in verified code state, not on baton claims.
>
> **Deposits:**
> - `bellows/knowledge/research/bellows-hardening-batch-freshness-2026-05-26.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
