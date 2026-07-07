# Bellows — plan_lint qa_steps cross-check (plan-133 trap class)
**Date:** 2026-07-07 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

Plan 133 (2026-07-07) shipped with header `qa_steps: 1` intended as a count; `gates.py` parses the field as a list of QA step numbers. Result: the DEV step was gated as QA (false-positive Rule 20 FAIL requiring CEO override) and the real QA step ran with mechanical Rule 20/22 gates skipped. plan_lint passed the header — it validates qa_steps presence/parse, not consistency with step labels. This plan adds the cross-check.

**Locked behavior:**
1. New lint check (e): for each step heading matching the `## STEP N — <ROLE>` convention, if `<ROLE>` contains `QA` and `N` is absent from the parsed qa_steps list → **FAIL** (exit-code-affecting), message naming the step and the fix.
2. If qa_steps names a step number whose heading role does NOT contain `QA` → **WARN** only (labels vary on older/irregular plans; the dangerous direction is silently ungated QA, not over-gating).
3. If no step headings match the convention, the check is skipped with an informational line (older plan formats must not start failing).
4. Detection heuristics must reuse whatever step-heading parse plan_lint already performs — do not introduce a second, divergent parser.
5. Constraint (parser-self-trip class): this plan's own header and step labels must satisfy the new check — DEV runs the updated lint against THIS plan file as part of self-verification and it must PASS.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are Bellows DEV. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` if present (skip with a note if absent). All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/` (only if needed)
> - `knowledge/development/plan-lint-qa-steps-guard-2026-07-07.md`
>
> 1. Read `scripts/plan_lint.py` in full. Locate the existing header parse (qa_steps) and step-heading parse; implement check (e) per the locked behavior above, reusing the existing parses (locked decision 4).
> 2. Add targeted tests covering: QA-labeled step missing from qa_steps → FAIL; non-QA step named in qa_steps → WARN, exit 0 when no FAILs; conforming plan → PASS; plan with no matching step headings → skip-informational. Follow the repo's existing test layout for lint/gates tests — locate by grep, not recall.
> 3. Self-verification: run the updated lint against (a) this plan file (must PASS — locked decision 5), (b) a recent Done plan `../lessons-forge/knowledge/decisions/Done/executable-134.md` (must PASS — regression guard on existing conventions), and (c) a copy of this plan file with qa_steps deliberately set to `1` (must FAIL with the new message). Quote all three outputs in the deposit.
> 4. Run the relevant test file(s) to a pass/fail result and quote the tail.
>
> **Deposit:** `bellows/knowledge/development/plan-lint-qa-steps-guard-2026-07-07.md` — check design, code locations touched, the three self-verification outputs, test tail, Output Receipt with status. In `### Ledger Updates` include: `#### Project Status` — one paragraph: plan_lint now cross-checks qa_steps against step labels (plan-133 trap class closed at authoring time); `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/development/plan-lint-qa-steps-guard-2026-07-07.md`
>
> STOP. Do NOT proceed to Step 2.

---
---

## STEP 2 — QA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this step and stating your immediate next action.** Do NOT rename the plan file.
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` if present (skip with a note if absent). All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; author and run the canonical block per `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`, reproduce its stdout byte-identically, then self-grep your report for the banner.
>
> **Scope:**
> - `knowledge/qa/plan-lint-qa-steps-guard-qa-2026-07-07.md`
>
> Verification table, one PASS/FAIL row per claim, evidence quoted: (1) re-run lint on this plan file → PASS with no new-check FAIL; (2) re-run lint on `../lessons-forge/knowledge/decisions/Done/executable-134.md` and one additional Done plan of your choosing → both PASS (regression guard); (3) construct a temp copy of this plan with `qa_steps: 1` → new check FAILs with the named-step message and nonzero exit; (4) construct a temp copy with qa_steps naming a non-QA step → WARN emitted, exit 0; (5) targeted tests pass in isolation, tail quoted; (6) check (e) reuses the existing step-heading parse — cite the code path (no second parser introduced). If any row fails, report and halt.
>
> **Deposit:** `bellows/knowledge/qa/plan-lint-qa-steps-guard-qa-2026-07-07.md` — verification table, evidence, Rule 20 block stdout, Output Receipt. Commit the QA report and Step 1 deposits if uncommitted. In `### Ledger Updates` include: `#### Project Status` — one paragraph: qa_steps cross-check verified; `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/plan-lint-qa-steps-guard-qa-2026-07-07.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
