# bellows — plan_lint regression test: T2 plan missing cold-panel line → WARN (N2, the gap in the (f) suite)
**Date:** 2026-07-25 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV add+run) → Step 2 (QA verify) | **qa_steps:** 2 | **pause_for_verdict:** always | **cycle_tier:** T0

## CEO Context

**N2 — add the one missing regression test for `plan_lint`'s §4 (f) Drafting-Cycle check: "T2 plan missing cold-panel line → WARN".** The (f) suite (`bellows/tests/test_plan_lint.py`, tests f-a…f-g) covers: compliant T2 (NO warn), tier-less, T1-missing-ACID, T0-no-block, fold-closing, real-271, real-274. It does NOT cover the T2 cold-panel branch (`plan_lint.py:194` — `WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)`). f-a proves the WARN is ABSENT on a compliant T2; nothing proves it FIRES when a T2 block omits the cold-panel line. This test closes that gap (noted in Plan B/277's cold panel).

**`cycle_tier: T0` — proven clone + trivial localized change; integration-vs-record pass only.** No §1 trigger fires: one new test function in one test file, a structure-for-structure clone of the existing f-c/f-e "missing-element → WARN" tests. The integration-vs-record pass is dry: clones the (f) pattern faithfully; complements (does not conflict with) f-a (compliant-T2, WARN absent); fills the exact uncovered branch. **The one real risk for a test-add — observe-the-effect / test-vacuity (plan 230, Checklist #32; the corpus's documented class) — is handled by §2.7's execute-against-real-data rule (applies at ALL tiers) baked into DEV+QA below**, not by the tier: the fixture is otherwise-compliant so ONLY the cold-panel WARN can fire, and both DEV and QA RUN it and confirm exactly that WARN appears (and no other) — a green suite alone is not accepted as proof.

**The exact test to add (DEV applies verbatim — a faithful applicator):**
```python
def test_lint_cycle_t2_missing_cold_panel_warns():
    """(f-h) T2 plan with a full 5-lens block + dry closing but NO cold-panel line → WARN naming cold-panel, exit 0."""
    plan = """\\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface), T-8 (novel).
**Walks:** 2.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Closing:** walk 1 dry; last event = lens pass; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\\nstdout: {result.stdout}"
    # observe-the-effect: the cold-panel WARN actually FIRES (this is the branch under test)
    assert "cold-panel" in result.stdout.lower()
    assert "missing cold-panel" in result.stdout.lower()
    # isolation: the fixture is otherwise-compliant, so NO other (f) WARN fires
    assert "missing lens" not in result.stdout.lower()
    assert "no cycle_tier" not in result.stdout.lower()
    assert "dry lens pass" not in result.stdout.lower()  # no fold-closing WARN
```

**Why the fixture isolates the branch (the SA/DEV must preserve this):** T2 declared (no cycle_tier WARN); all five lens lines present (no missing-lens WARN); the last lens line (ACID) contains `dry` (no fold-closing WARN); ONLY the `**Cold panel (T2):**` line is absent → ONLY the cold-panel WARN can fire. If the DEV alters the fixture such that another WARN also fires, the isolation assertions catch it → HALT.

**Scope discipline:** ONE file (`bellows/tests/test_plan_lint.py`), one appended test function. NO change to `plan_lint.py` (the gate is unchanged — this is pure test coverage), NO other test touched, NO doctrine/DB.

**Deposit-once discipline:** deposited exactly once.

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/in-progress-executable-<id>.md (daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — DEV (add the test + run it; observe-the-effect)

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Run commands from your own working tree. Add ONE test function to `bellows/tests/test_plan_lint.py` **verbatim** from the CEO Context block — a faithful applicator, not a re-author.
>
> **Scope:**
> - `bellows/tests/test_plan_lint.py` (add ONE test function; edit in place)
> - `bellows/knowledge/development/n2-cold-panel-test-dev-2026-07-25.md` (dev-log)
>
> **Task A — pre-edit check.** Confirm `test_lint_cycle_t2_missing_cold_panel_warns` does NOT already exist in the file (`grep -c 'def test_lint_cycle_t2_missing_cold_panel_warns'` == 0; else idempotent prior run → HALT and report). Confirm `_run_lint` and the existing `test_lint_cycle_compliant_t2_no_warn` (f-a) are present (the clone base).
>
> **Task B — add the test.** Insert the `test_lint_cycle_t2_missing_cold_panel_warns` function (exact text from CEO Context) immediately AFTER the `test_lint_cycle_compliant_t2_no_warn` function and BEFORE `def test_lint_cycle_tierless_warns():` — grouping the two T2 tests. Use `encoding='utf-8'` for the read+write. Preserve surrounding tests byte-for-byte (a `git -C bellows diff` must show ONLY the added function — no other line changed).
>
> **Task C — RUN it (execute against real data; observe-the-effect).** `cd bellows && python3 -m pytest tests/ -k "plan_lint or lint" -q` — the new test PASSES and the full plan_lint/lint suite is green (0 failures, 0 regressions vs the prior count). Then, to prove the branch is genuinely exercised (not a vacuous pass), run the fixture through the linter directly and capture the RAW stdout: confirm the line `WARN: T2 plan missing cold-panel line in Drafting Cycle block` appears AND that NO `missing lens`, `no cycle_tier`, or `dry lens pass` WARN appears (the fixture isolates the cold-panel branch). Paste the raw pytest summary + the raw linter stdout into the dev-log.
>
> **Task D — commit.** `git -C bellows add tests/test_plan_lint.py bellows/knowledge/development/n2-cold-panel-test-dev-2026-07-25.md` is WRONG (mixed roots) — instead: write the dev-log, then `git -C /Users/marklehn/Developer/GitHub/bellows add tests/test_plan_lint.py knowledge/development/n2-cold-panel-test-dev-2026-07-25.md` (explicit paths, never `-A`), then `git -C /Users/marklehn/Developer/GitHub/bellows commit -m "test(plan_lint): T2-missing-cold-panel WARN regression (f-h) [<id>]"` (substitute your minted id). Record `BELLOWS_SHA`. (Leave the root submodule-pointer bump to the Planner at wrap.)
>
> **Deposit:** `bellows/knowledge/development/n2-cold-panel-test-dev-2026-07-25.md` — the pre-edit grep, the `git diff` showing ONLY the added function, the RAW pytest summary (pass count + 0 failures), the RAW linter stdout proving the cold-panel WARN fires + the isolation (no other WARN), `BELLOWS_SHA`, and an Output Receipt. Canonical Python file-write — no heredoc. `#### Prompt Feedback` in `### Ledger Updates`.
>
> **Deposits:**
> - `bellows/knowledge/development/n2-cold-panel-test-dev-2026-07-25.md`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — QA (independent verification + observe-the-effect re-run)

---

> **Before starting, read the Step-1 dev-log and confirm its Output Receipt is Complete; else halt and report.** Post a short visible chat message confirming you are starting Step 2 (QA). You are Bellows QA. **Verification + reporting only — no test edits.** If a check fails, report it — do NOT fix it.
>
> **MANDATORY — Rule 20 self-check banner (simple form — a targeted-test plan; the move/test-verification rows ARE the evidence).** The QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; end with a self-grep confirming the banner.
>
> **Evidence rule.** Deposit RAW command output, never a summary.
>
> **Scope:**
> - `bellows/knowledge/qa/n2-cold-panel-test-qa-2026-07-25.md`
>
> Verification table, one row per claim (command + expected; HALT on any fail):
> 1. **Test present** — `grep -c 'def test_lint_cycle_t2_missing_cold_panel_warns' bellows/tests/test_plan_lint.py` == 1.
> 2. **Suite green** — `cd bellows && python3 -m pytest tests/ -k "plan_lint or lint" -q`: 0 failures; the new test among the passed; reconcile the pass count against the Step-1 dev-log (new count = prior + 1). Raw tail shown.
> 3. **⭐ Observe-the-effect (the load-bearing row) — the test genuinely exercises the branch, INDEPENDENTLY of the assertions.** Run the f-h fixture through the linter yourself (extract the fixture or re-run the single test with `-s`/verbose) and quote the RAW linter stdout: it MUST contain `WARN: T2 plan missing cold-panel line in Drafting Cycle block` and MUST NOT contain `missing lens`, `no cycle_tier`, or `dry lens pass`. A test that passes without this exact WARN firing is a vacuous pass → FAIL.
> 4. **Scope — ONLY the test file changed** — `git -C /Users/marklehn/Developer/GitHub/bellows show --stat <BELLOWS_SHA>` touches only `tests/test_plan_lint.py` (+ the dev-log); `plan_lint.py` UNCHANGED (this is coverage, not a gate change).
> 5. **Diff is only the added function** — `git -C /Users/marklehn/Developer/GitHub/bellows show <BELLOWS_SHA> -- tests/test_plan_lint.py` shows ONLY the added `test_lint_cycle_t2_missing_cold_panel_warns` function; no other test altered.
>
> If any row fails, report and halt.
>
> **Deposit:** `bellows/knowledge/qa/n2-cold-panel-test-qa-2026-07-25.md` — the table with RAW output, the row-3 raw linter stdout quote, the Rule 20 banner + PASSED + self-grep, an Output Receipt. Canonical Python file-write — no heredoc. Commit the QA report. In `### Ledger Updates` include `#### Project Status` (one milestone: the (f) suite now covers the T2 cold-panel branch — f-h added; plan_lint §4 fully test-covered) and `#### Prompt Feedback`.
>
> **Deposits:**
> - `bellows/knowledge/qa/n2-cold-panel-test-qa-2026-07-25.md`
>
> **Do NOT move this plan to Done/.** The close path is owned by Bellows on continue-verdict consumption (Rule 8) — never by the agent.
