# Bellows — Type-Qualified Plan IDs in Dashboard/Status Panes (`executable #35`)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
CEO request 2026-06-12: the status CLI and dashboard render plan ids as a bare `#{plan_id}`, which drops the plan TYPE — `#34` (a diagnostic) and `#35` (an executable) look identical on screen though the `plans.type` column distinguishes them. CEO decision: write the type out in full before the id — `executable #35`, `diagnostic #34` — in BOTH the IN-FLIGHT and AWAITING VERDICT panes. The `type` value is already in the same `plans` row the IN-FLIGHT query selects (just not projected); the AWAITING VERDICT query reads from `verdicts` and needs a join to `plans` for type. Convenient alignment fact: "executable" and "diagnostic" are both exactly 10 characters, so a fixed type field keeps columns aligned. Shared render layer: `status.py` is imported by `dashboard.py` (plan 33), so this one change fixes both surfaces. Anchors as of 2026-06-12 (re-verify by grep, do not trust line numbers): IN-FLIGHT render `f" #{plan_id}  {project:<8s}  Step ..."` (~status.py:155) and its query `SELECT p.id, p.target_project, ... FROM plans p` (~:190); AWAITING VERDICT render `f" #{plan_id}  step {step}  ..."` (~:175) and its query `SELECT v.plan_id, v.step_number, ... FROM verdicts v` (~:211). NOTE: the running dashboard imports status.py at startup — this change takes effect on the next dashboard restart (the `r` key, plan 33); flag in the receipt.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then `status.py` in full (locate both render functions and both queries by grep). **Scope is exactly: `status.py`, `tests/test_status.py`, `tests/test_dashboard.py` (only if its render assertions reference the id label).**
>
> Change the rendered id label from `#{plan_id}` to `{type} #{plan_id}` in BOTH panes, where `{type}` is the plan's `plans.type` value (`executable` / `diagnostic`) rendered in full:
> - **IN-FLIGHT:** add `p.type` to the SELECT at the IN-FLIGHT query; thread it into the render function; format as e.g. `f"{ptype} #{plan_id}  {project:<8s}  ..."`. Keep the rest of the line (project, step, status, elapsed, title) unchanged; adjust spacing so columns stay aligned given the fixed 10-char type width.
> - **AWAITING VERDICT:** the query reads from `verdicts` — add a `JOIN plans p ON p.id = v.plan_id` (read-only) and project `p.type`; thread it into that render function the same way (`f"{ptype} #{plan_id}  step {step}  ..."`).
> - Defensive: if `type` is ever NULL/unknown, fall back to the bare `#{plan_id}` (no crash). Keep all connects `?mode=ro`.
>
> **Tests:** update/extend `tests/test_status.py` render assertions to expect the `executable #N` / `diagnostic #N` form in both panes (use fixture rows of each type); add a NULL-type fallback test. If `tests/test_dashboard.py` asserts on the id label, update those too. Run the FULL suite (`python3 -m pytest tests/`) to an explicit pass/fail and READ THE TAIL. **Acceptance:** run `python3 status.py` against the live DB and paste its actual output into the dev log, showing the type-qualified ids. Write the dev log to `bellows/knowledge/development/type-qualified-ids-dev-log-2026-06-12.md`. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/development/type-qualified-ids-dev-log-2026-06-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md` and the dev log. **Verify, each with executed evidence (files into `knowledge/qa/evidence/type-qualified-ids-2026-06-12/`):** (1) **Full suite** — final 15 lines, zero failures, new/updated-test count per dev log; output to `full_suite_tail.txt`. (2) **Both panes labeled** — `grep -nE "type.*#\{plan_id\}|#\{plan_id\}" status.py` shows BOTH render sites now prefix the type and no bare `#{plan_id}` remains in a render f-string (except the documented NULL fallback); output to `render_sites.txt`. (3) **Live render** — run `python3 status.py` yourself; output shows `executable #N` / `diagnostic #N` form (or `(none)` panes if nothing in flight — if so, run the render functions against fixture rows of each type to demonstrate); output to `live_render.txt`. (4) **Read-only preserved** — every DB connect still `?mode=ro`, the new JOIN is read-only; output to `safety_check.txt`. (5) **NULL fallback** — the unknown-type test passes (graceful bare `#N`); output to `null_fallback.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `type-qualified-ids-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/type-qualified-ids-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/type-qualified-ids-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, render_sites.txt, live_render.txt, safety_check.txt, null_fallback.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table and the Rule 20 banner block to `bellows/knowledge/qa/type-qualified-ids-qa-report-2026-06-12.md`. **Receipt Flag for CEO:** the running dashboard shows the new labels only after the next `r` restart (status.py is imported at dashboard startup). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/type-qualified-ids-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/type-qualified-ids-2026-06-12/` (five evidence files per Rule 20 self-check)
