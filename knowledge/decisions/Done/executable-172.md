# Bellows — plan_lint STEP-heading case/format guard (catch the vacuous-pass trap)
**Date:** 2026-07-13 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

**The trap (bit invoice-pulse plan 161 this arc).** `scripts/plan_lint.py` finds executable steps with a **case-sensitive** regex (`^(## STEP (\d+)\b...)`, line 68). A plan authored with title-case headings (`## Step 1` / `## Step 2`) yields ZERO matches, so the step-scoped checks — (b) deposits blocks, (d) scope blocks — **silently never run**, and the lint still prints `exit 0`. That vacuous green is exactly how plan 161's missing Rule-20 banner slipped past a lint the Planner *did* run. Reproduced live 2026-07-13: a `qa_steps: 2` plan with `## Step N` headings + `**Deposits:**` blocks lints clean with only (a) rows.

**What this adds — one new check (e), surgical, near-zero false-positive.** After computing `step_headers`, also compute a case-INSENSITIVE version. Then:

- **FAIL (e)** when the header declares `qa_steps` (i.e. it IS a multi-step DEV→QA plan) but `step_headers` (uppercase) is empty. Message names the cause and, if case-insensitive headings exist, points at the fix: *"header declares qa_steps=N but no uppercase '## STEP N' heading found — step checks (b)/(d) were skipped (vacuous pass); found lowercase '## Step N', use uppercase."* This directly blocks the 161 trap. It sets `all_passed = False` → exit 1.
- **WARN (print-only)** when there are NO uppercase step headings AND no `qa_steps` header BUT case-insensitive `## Step N` headings exist — a lower-confidence "did you mean uppercase?" nudge that does NOT block (a single-step diagnostic may legitimately use step prose).
- **Nothing** for a legit single-step diagnostic (no `qa_steps`, no step headings of any case) — stays clean, exit 0.

**Design decision for CEO (ratify at the Step-1 pause).** The (e) inconsistency is a **FAIL**, not a WARN — unlike plan 140's advisory qa_steps↔label cross-check. Rationale: a title-case executable makes the lint *lie about coverage* (it reports pass while (b)/(d) never executed), which is materially worse than a mis-gating advisory. If you'd prefer WARN-only symmetry with 140, say so at the pause and DEV will downgrade it.

**Why not a blanket "zero STEP headings" WARN** (the baton's first phrasing): several legit historical diagnostics use `## Step N` prose with no gate-relevant steps — a blanket rule false-positives on them. Gating on `qa_steps`-present-but-no-uppercase-STEP is the zero-false-positive signal that isolates the actual bug.

**Bug to avoid.** Do NOT fire (e) FAIL on single-step diagnostics (no `qa_steps` field) — they legitimately have no `## STEP` headings. Anchor the case-insensitive regex to real level-2 headings (`^##\s+step\s+\d`), not the word "step" in prose.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Execute Step 1 ONLY, then STOP for CEO verdict.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-plan-lint-step-heading-case-guard.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Files in scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/plan-lint-step-heading-case-guard-2026-07-13.md`
>
> **Change 1 — the check.** In `scripts/plan_lint.py`, immediately AFTER `step_headers = re.findall(r'^(## STEP (\d+)\b[^\n]*)', clean_text, re.MULTILINE)` (line ~68), add a new check (e). Compute `ci_step_headers = re.findall(r'^(##\s+step\s+(\d+)\b[^\n]*)', clean_text, re.IGNORECASE | re.MULTILINE)`. Read `header.get("qa_steps")` (the parsed header is already available as `header`). Then:
>   - If `not step_headers and header.get("qa_steps")`: append `("FAIL", "(e) step heading format", <msg>)` to `results` AND set `all_passed = False`. `<msg>` states qa_steps is declared but no uppercase `## STEP N` heading was found so (b)/(d) were skipped; if `ci_step_headers` is non-empty, append that lowercase `## Step N` was found and headings must be uppercase.
>   - Elif `not step_headers and ci_step_headers` (no qa_steps): `print(f"WARN: ...")` inline (print-only, like the existing WARNs at ~line 140/148/150) — nudge to use uppercase `## STEP N`; do NOT touch `all_passed`.
>   - Else: nothing.
>
> **Change 2 — tests.** Add tests to `tests/test_plan_lint.py` following the existing `_run_lint(plan_text)` subprocess+tempfile style. Cover: (a) `qa_steps: 2` plan with `## Step 1`/`## Step 2` (title-case) + `**Deposits:**` blocks → (e) FAIL, **exit 1**, WARN/FAIL text names the case fix; (b) a correct `qa_steps: 2` plan with uppercase `## STEP 1`/`## STEP 2` → NO (e) row, exit per its other checks; (c) a single-step diagnostic (no `qa_steps`, no step headings) → NO (e) FAIL, NO case WARN, exit 0; (d) a no-`qa_steps` plan that uses `## Step 1` prose → prints the case WARN but STILL exit 0 (print-only). Assert on exact substrings and on exit codes. Existing tests must pass UNCHANGED — if any fails, halt and report.
>
> **Self-verify.** Run the FULL suite: `timeout 600 python3 -m pytest tests/ -v 2>&1 | tail -30` — read the tail to an explicit pass/fail. Then dogfood: run `python3 scripts/plan_lint.py` against a constructed title-case `qa_steps` plan and confirm exit 1 + the (e) FAIL row; run it against THIS plan file (uppercase STEP headings) and confirm NO (e) row. Grep the diff to confirm the new block has exactly one `all_passed = False` (in the FAIL arm only), no stray `return`.
>
> **Commit** when coherent: `git add -A && git commit` tagged `[plan-lint-e]`. Targeted test command for the record: `python3 -m pytest tests/test_plan_lint.py -v 2>&1 | tail -20`.
>
> **Deposits:**
> - `knowledge/development/plan-lint-step-heading-case-guard-2026-07-13.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---

## STEP 2 — QA

> **FIRST — post a short visible message to chat confirming you are starting the QA step.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> Verify AT CODE LEVEL. Verification table, one row per claim, quoting the code: (1) the new (e) block sits after the `step_headers` computation and BEFORE the (b) deposits loop — cite line numbers; (2) the FAIL arm sets `all_passed = False` and appends to `results`; the WARN arm is print-only — quote both, confirm the WARN arm has NO `all_passed` assignment and NO `return`; (3) the case-insensitive regex is anchored to level-2 headings (`^##\s+step\s+\d`), NOT bare "step" in prose — quote it; (4) title-case `qa_steps` plan → (e) FAIL + exit 1 (test a, quote assertion + exit check); (5) correct uppercase plan → NO (e) row (test b); (6) single-step diagnostic → NO (e) FAIL, NO case WARN, exit 0 (test c) — this is the critical no-false-positive row; (7) no-`qa_steps` `## Step` prose → WARN + exit 0 (test d); (8) pre-existing tests unchanged — `git --no-pager diff HEAD~1 -- tests/` shows additions only; (9) full suite green — run `timeout 600 python3 -m pytest tests/ -v 2>&1 | tail -30`, paste the RAW tail incl. the summary line (a summary is NOT acceptable evidence). Any row fails → report and halt.
>
> Deposit the QA report ending with the Rule 20 self-check banner, verbatim: a section headed `## Rule 20 — QA Self-Check Results` and concluding `**PASSED — SELF-CHECK PASSED**` (only if every row genuinely passed).
>
> **Commit** the QA artifacts tagged `[plan-lint-e]`.
>
> **Deposits:**
> - `knowledge/qa/plan-lint-step-heading-case-guard-qa-2026-07-13.md`
>
> **STOP. Do NOT move the plan to Done until the CEO issues a verdict.**
