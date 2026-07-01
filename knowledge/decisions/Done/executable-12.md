# Shop — Baton + LESSONS Factual Corrections (Session-Wrap 2026-06-12 Errata)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (Documentation Agent) | **Test Scope:** targeted

**Test Scope justification:** targeted — two governance-root documentation files, four line-level corrections. No code, no tests.

## Context (Rule 27)
CEO verdict on plan 11 (session wrap) found factual errors in the rewritten baton: three of five reporter function names were paraphrased instead of grepped from `forge/src/reporter.py` (the exact failure class LESSONS' occurrence-grep entry documents), the plan-7 coverage claim garbles which plans have two-row coverage, and the Forge SA filename is wrong. LESSONS entry (b) from the same wrap also duplicates its discipline-rule sentence. Corrections are dispatched as plan text per the 2026-06-12 disposition-text lesson. CROSS-REPO NOTE: both targets are governance-root files OUTSIDE the worktree — edit via Bash `python3 -c`/`with open()` (Edit tool is path-scope-denied), commit at the governance root; files_changed will show 0 worktree files plus the dev-log deposit; expected, not noise.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Documentation Agent

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). Skip specialist-file reads — four mechanical line corrections. **Allowed files (scope — exactly these, no others):** `/Users/marklehn/Developer/GitHub/shop_next_session.md`, `/Users/marklehn/Developer/GitHub/LESSONS.md`. For each edit: grep for the ANCHOR, confirm exactly one match (zero or multiple: halt and report the grep output), apply, re-grep to confirm. **Before E1, ground truth the function names yourself:** `grep -n "^def " /Users/marklehn/Developer/GitHub/forge/src/reporter.py` and confirm the replacement names below appear in it.
>
> **E1 — Baton function names.** File: shop_next_session.md. ANCHOR: `read_lifecycle_plans()`. Replace the full fragment `` `read_lifecycle_plans()`, `resolve_plan_pointer()`, `assemble_reconstruction()`, `write_reconstruction_report()`, `get_live_plans_status()` `` with `` `generate_reconstruction_data()`, `write_reconstruction_report()`, `get_live_plans_status()` (plus `_open_lifecycle_db()`, `_query_*`, and `_resolve_*` helpers) ``. After the edit, `grep -c "read_lifecycle_plans\|resolve_plan_pointer\|assemble_reconstruction" shop_next_session.md` must return 0.
>
> **E2 — Baton plan-7 coverage claim.** File: shop_next_session.md. ANCHOR: `first two-row step coverage with turns populated across plans 4/5/6/7`. Replace with: `FIRST plan with two-row step coverage and turns populated (plans 4/5 permanently lack their step-2 rows — pre-fix era; plan 6 is single-step)`.
>
> **E3 — Baton Forge SA filename.** File: shop_next_session.md. ANCHOR: `FORGE_SA.md`. Replace with `FORGE_SYSTEMS_ANALYST.md`. Confirm against `ls /Users/marklehn/Developer/GitHub/forge/agents/`.
>
> **E4 — LESSONS duplicate sentence.** File: LESSONS.md. In the `## 2026-06-12: Verdict disposition text does not reach the resumed step` entry, the body paragraph ENDS with the sentence beginning `The discipline rule: corrections discovered at verdict time` and a separate bolded `**The discipline rule:**` line then repeats the same sentence. Remove the trailing sentence from the body paragraph (keep the bolded standalone line), so the rule appears exactly once. After the edit, `grep -c "corrections discovered at verdict time" LESSONS.md` must return 1.
>
> **Commit at the governance root** (`/Users/marklehn/Developer/GitHub`): `git add shop_next_session.md LESSONS.md && git commit -m "docs: session-wrap errata — baton function names, plan-7 coverage claim, FORGE_SYSTEMS_ANALYST filename, LESSONS dedupe [<your plan id>]"`. Do NOT add any other root modifications. Record the SHA. Write the dev log (E1–E4 anchor greps before/after + root SHA) to `bellows/knowledge/development/session-wrap-errata-dev-log-2026-06-12.md`. Use `with open()` for the deposit; no heredocs. **Deposits:**
> - `bellows/knowledge/development/session-wrap-errata-dev-log-2026-06-12.md`
