# Executable: remove plan_lint check (i), keep (g) and (h) intact

**Type:** Executable
**Project:** bellows
**Depends on:** **executable-303** (Done — the plan that added checks `(g)`/`(h)`/`(i)`; **the newest same-class plan and this plan's clone origin**, diffed before drafting per §2.6).
**Created:** 2026-08-06
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`) and does not parse the filename. **Read `id_sequence` at deposit.**

---

## CEO Context

**CEO decision 2026-08-06, taken at 303's step-2 gate: DROP check `(i)`.** Its corpus sweep over **1362 plans in five pinned roots** produced **11 fires — 8 of them false** (plan ids `diagnostic-301` *discusses*, not ones it depends on). ⚠️ **`(i)` cannot distinguish a subject from an input.** That is the entity-extraction problem flagged when the check was first scoped, and narrowing it to backtick-quoted plan ids **moved the boundary rather than solving it.**

**`(g)` and `(h)` are not in question and must survive untouched.** `(g)` returned **1 fire across the same 1362 plans and it was a TRUE POSITIVE** — a genuinely out-of-order ledger in `diagnostic-299`, in a shipped and closed plan a full drafting cycle, an ACID pass and a cold panel had all read. `(h)` returned **0**.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

⚠️⚠️ **THIS IS A SUBTRACTIVE CHANGE, AND §2.7's SUBTRACTIVE-TRIM RULE GOVERNS IT:** *after any edit, assert the PRESENCE of retained material, not merely the absence of removed material.* **A deletion is invisible to a check that greps only for what is gone.** **Every verification below is framed as "what survived", not "what disappeared".**

---
---

## STEP 1 — DEV

---

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py` and `tests/test_plan_lint.py`. **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
> **Task A0 — pre-edit cleanliness + warn-first precondition.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` must be empty. **If DIRTY — resume disambiguation (Rule 56):** grep for THIS plan's own edits (an absent `(i)` block, five absent test names). All present and attributable → `git restore` both files and reapply from scratch (**NEVER hand-patch a partial apply**). Any unattributable hunk → **HALT, do NOT restore.**
> ⚠️ **Confirm at HEAD that `(g)`, `(h)` and `(i)` are all present and all bare `print(...)` calls touching neither `results` nor `all_passed`.** **If `(i)` is already absent, this plan has run — verify and STOP, do not re-delete.**
>
> **Task B — capture the BEFORE baseline, because the proof of a removal is a diff.** Run the corpus sweep exactly as 303's QA did — `plan_lint` over every plan in the five `Done/` trees, addressed ABSOLUTELY under `/Users/marklehn/Developer/GitHub/` — and save the raw output. ⚠️ **This is the artifact the AFTER sweep is diffed against; without it the removal cannot be shown to have touched only `(i)`.**
>
> **Task C — remove check `(i)` and nothing else.** Delete the `(i)` block (its comment through its final `print`). ⚠️ **Measured at authoring: ~24 lines. VERIFY the true extent before cutting — do not trust that figure.** **Leave `(g)` and `(h)` byte-identical.** **Grep-confirm afterwards that exactly one `(g)` and one `(h)` remain and zero `(i)`.**
>
> **Task D — remove `(i)`'s five tests, named explicitly:** `test_lint_halt_routing_missing_id_warns`, `test_lint_halt_routing_full_coverage_no_warn`, `test_lint_no_halt_routing_line_warns`, `test_lint_no_plan_ids_no_halt_routing_no_warn`, `test_lint_executable_with_plan_ids_no_i_warn`. ⚠️ **The last one asserted that `(i)` does NOT fire on an executable; with `(i)` gone it is vacuous and must go too — a test that can no longer fail is not coverage.**
>
> ⚠️⚠️ **Task E — PROVE WHAT SURVIVED, NOT WHAT LEFT.** These four must still exist and still pass: `test_lint_ledger_ascending_no_warn`, `test_lint_ledger_out_of_order_warns`, `test_lint_ledger_no_entries_no_warn`, `test_lint_stale_closing_warns`. **Then run the POSITIVE CONTROLS live:**
> - **`(g)` still fires** on `/Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/diagnostic-299.md` (its ledger really is out of order — re-verified at authoring). **Paste raw output.**
> - **`(h)` still fires** on a fixture with lens results recorded and a closing asserting no lens has read. **Paste raw output.**
> - **`echo $?` = 0** on each.
> ⚠️ **If either control does not fire, the removal took something with it. HALT and report.**
>
> **Run targeted tests only:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. ⚠️ **Do NOT run the full suite in this step.** ⚠️ **Measured before this plan: 54 targeted tests. Removing five predicts 49 — TREAT THAT AS A PREDICTION AND REPORT THE ACTUAL, do not assert it.**
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/remove-check-i-dev-log-2026-08-06.md`
> - `knowledge/development/sweep-before.txt`
>
> **Deposit the dev log** with the exact removed block, the five removed test names, the four surviving test names with their results, both positive controls raw, and the BEFORE sweep. **Canonical Python/MCP file-write — NO heredoc. Commit all (NO push).** `#### Prompt Feedback` in `### Ledger Updates`.
>
> **Deposits:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/remove-check-i-dev-log-2026-08-06.md`
> - `knowledge/development/sweep-before.txt`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — QA

---

> **Task Q0 — RE-PIN THE STATE.** The DEV→QA gate is an arbitrary wall-clock window over shared stores.
> 1. `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py` — **the most recent commit touching either file must be Step 1's. If a foreign commit intervened, HALT.** ⚠️ **This guard caught a real HEAD movement on plan 303; it is not ceremony.**
> 2. **`git -C <root> rev-parse HEAD` for each of the five roots, recorded verbatim beside every count.**
>
> 1. **Run the full `bellows` test suite.** Record the raw summary line verbatim — **not a summary of it.** ⚠️ **851 passed before this plan; expect 846 after removing five. REPORT THE ACTUAL.**
> 2. ⚠️⚠️ **THE CENTRAL VERIFICATION — DIFF THE SWEEPS, DO NOT COUNT WARNINGS.** Re-run the corpus sweep identically to Step 1's Task B, then `diff` it against that BEFORE artifact. **The diff must consist of EXACTLY the `(i)` warning lines and nothing else.** ⚠️ **A count of remaining warnings is not this proof — a count cannot see a `(g)` line silently lost while an `(i)` line disappeared. The diff can.** **Paste it raw.**
> 3. **Confirm `(g)`'s true positive survives:** the sweep must still report the out-of-order ledger in `diagnostic-299`. ⚠️ **If that line is missing, the removal damaged `(g)` and the plan HALTS.**
> 4. **Confirm WARN-only by mechanism:** grep the surviving checks and show neither appends to `results` nor assigns `all_passed`; then `echo $?` = 0 on a plan that trips `(g)`.
> 5. **Emit the QA Receipt with the canonical Rule 20 self-check block**, a verification row per numbered item with raw evidence.
>    - `required_evidence_files`: `[full-suite.txt, sweep-after.txt, sweep-diff.txt]`
>    - ⚠️ **Deposit all three BEFORE running the block** — it `sys.exit(1)`s if any is missing or empty.
>    - ⚠️⚠️ **The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014).** **If it prints FAILED, HALT.**
>    - **Evidence rule:** deposit **RAW command output**, never a summary.
>
> **Scope:**
> - `knowledge/qa/remove-check-i-qa-report-2026-08-06.md`
> - `knowledge/qa/full-suite.txt`
> - `knowledge/qa/sweep-after.txt`
> - `knowledge/qa/sweep-diff.txt`

**Deposits:**
- `bellows/knowledge/qa/remove-check-i-qa-report-2026-08-06.md`
- `bellows/knowledge/qa/sweep-after.txt`
- `bellows/knowledge/qa/sweep-diff.txt`

---

## Method + boundaries

- ⚠️ **`plan_lint` is a GATE. This change is purely subtractive.** **`(g)` and `(h)` must end byte-identical to their current form** — if either needs touching to make the removal work, **STOP and report.**
- ⚠️ **The half-complete state:** if Step 1 commits and Step 2 never runs, `(i)` is gone and unmeasured. **That is safe because the surviving checks are WARN-only and Step 1's positive controls already prove `(g)`/`(h)` alive** — Step 2 adds corpus-level proof, not the first proof.
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim). ⚠️ **Never truncate `plan_lint` output through `head` — a FAIL line below the cut reads as a pass.** *(That error shipped a defective deposit on 2026-08-06.)*
- ⚠️ **Agents run `git add` and `git commit` only. No `git push`.**

---

## Drafting Cycle

**This section is a RECORD, not instructions.** Gate-matching strings are described here, never quoted.

**Tier:** T2 — **computed, trigger fired: T-6** (edits `plan_lint`, a gate — the verb test does not spare it). **T-1** also fires (source plus tests). ⚠️ **T-8 does NOT fire — this is a structure-for-structure clone of `executable-303`, its immediate parent and the newest same-class plan, diffed BEFORE drafting rather than after.** T-2, T-3, T-4, T-5 do not fire.

⚠️ **Same known consequence as 303:** T2 wants a cold panel, §2.6 gates the panel on a dry walk, and no plan has reached one in five attempts. **The earned WARN is expected and is not a reason to declare a lower tier.**

**Walks:** ⚠️⚠️ **NONE RUN. Draft v0** — no lens result is recorded because no lens has run (§2.7 attestation).

- Weak spots:          not run.
- Destruction:         not run.
- Vulnerabilities:     not run.
- Integration-record:  not run.
- ACID:                not run.

**Panel status:** none run.

**Conflicts:** ⚠️ **Constraints are appended at the END of this block as they are earned, never inserted above an existing entry.**

**Closing:** NOT REACHED — no lens has read this artifact.
