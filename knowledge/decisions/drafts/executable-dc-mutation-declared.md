# bellows — executable: DC WORK DECLARES ITS MUTANTS — `plan_lint` check (w), advisory, so a plan that edits a shop instrument says how the OLD tool validated the NEW one

**Date:** 2026-09-05 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted (`tests/test_plan_lint.py`) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**Priority:** 15

**auto_close:** false

**cycle_tier:** T1 — **T-3 fires** (`plan_lint` runs on every machine that drafts). ⛔ **T-6 does NOT fire**, checked against the trigger as quoted (*"Edits doctrine, the template, gates, or specialist contracts"*): `plan_lint` is an authoring-time instrument, and four measured precedents tier `plan_lint`/`cycle_check` edits at T1 (`100023`, `100025`, `100033`, `100037`). ⚠️ **This plan deliberately does NOT write the requirement into doctrine** — see "What this does NOT do". T-8 not fired: clone by kind of `Done/executable-100037.md`.

**Depends on:** the DC-work path question (CEO, 2026-09-05) and threads **141**, **119**. Clone origin: `Done/executable-100037.md` — same kind, `plan_lint` edit, advisory check, T1.

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-dc-mutation-declared.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

## What this changes

One advisory check. **A plan whose manifest `writes:` names a shop instrument, and whose `mutants:` is absent or `NONE`, gets a WARN.** Nothing blocks; the exit code is untouched.

## Why this exists

⛔ **The circularity, stated precisely — narrower than it first appears.** Measured 2026-09-05: `gates.py` never invokes a DC instrument, and all three acceptance points (`depositor.py:476`, `tools/clear_plan.py:112`, `tools/run_check.py`) run **before** the plan executes. So no acceptance gate is ever run by the tool a plan is modifying. **The one real self-validation is a DC plan's own QA step, which runs the instrument its DEV step just edited.**

⛔ **The remedy already exists and is already practised — it is simply not declared.** Six instrument fixes shipped 2026-09-04 each carried a mutation control: revert the tool, confirm the new tests FAIL. That is the old tool validating the new one — the bootstrap principle as evidence rather than infrastructure.

⚠️ **And it is unevenly applied.** Of **11** `Done` plans whose `writes:` name a shop instrument, **6 declared `mutants:` and 5 did not** — the five including `100033` and `100037`, which changed `cycle_check` and `plan_lint` themselves.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the population | **11** `Done` plans declare a shop instrument in `writes:` | `grep -lE "^writes:.*(cycle_check\|plan_lint\|fold_check\|propagation_check\|walk_register_lint\|mutation_check)" Done/*.md` |
| P2 | ⛔ the gap | **6 declared `mutants:`, 5 did NOT** — `100037`, `100033`, `561`, `565`, `575` | `grep -m1 "^mutants:"` each |
| P3 | ⛔ **no new parse and no new import** | `plan_lint` ALREADY parses the stanza at check `(f-stanza)`, `:580–606`, into `stanza_fields`; `writes` and `mutants` are both in hand there | read `:580–606` |
| P4 | the free letter | existing checks are `a b c d e f i j k l n o1 o2 p q r s t u v` — **`w` is free** | `grep -oE '"\([a-z][0-9]?\)' scripts/plan_lint.py \| sort -u` |
| P5 | the acceptance points, and their timing | `depositor.py:476`, `tools/clear_plan.py:112`, `tools/run_check.py:85` — **all pre-execution**; `gates.py` invokes none | grep each |
| P6 | ⚠️ the honest weakness | `mutation_check` is the least-trusted instrument in the set: **5% recording rate** (`100032`), two un-QA'd fixes inside it from 2026-09-04, and threads **97/107/112** open against it | read `Done/diagnostic-100032.md` and those threads |
| P7 | in-flight | re-derive at execution | `sqlite3 "file:$PWD/lifecycle.db?mode=ro" …` |

## What this does NOT do

- ⛔ **It does not make the declaration REQUIRED, and does not touch doctrine.** Advisory only. ⚠️ **The reason is P6:** a shop-wide requirement would make the least-trusted instrument load-bearing for the most sensitive work. Promote it only after `mutation_check`'s own debt (97/107/112) is settled — that is a separate decision with its own evidence.
- ⛔ It does not change `plan_lint`'s exit code, any existing check, or any verdict.
- It does not backfill `mutants:` onto the 5 plans in P2.

## MUST-PRESERVE

- ⛔ **`plan_lint`'s exit code is unchanged for every input.** Proven by test, not asserted.
- ⛔ **Check (w) is WARN-only** — it appends no FAIL and does not set `all_passed = False`.
- ⛔ **`(f-stanza)`'s own WARNs are unchanged** — (w) reads `stanza_fields` and adds nothing to that block's output.
- ⛔ **A plan with no `## Cycle Manifest` stanza emits no (w) WARN** — absence of a manifest is `(f)`'s business, not this check's.

## Drafting Cycle

**Tier:** T1 — T-3 fires. **Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-dc-mutation-declared-2026-09-05.md`
**Walks:** 0 — ⛔ **v0. No lens has walked it; no §2.0 direction verdict issued.**
⚠️ **Keep the per-lens lines in THIS BLOCK current per lens** — `cycle_check` reads the body and nothing else; an unwritten block makes it return `CONTINUE` having evaluated nothing (thread 141).

**Closing:** ⛔ NOT CLOSED.

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze.)*

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1–2 sentences) confirming you are starting this plan and stating your immediate next action.**
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/mutants/dc-mutation-declared.json`
> - `knowledge/development/dev-log-dc-mutation-declared-2026-09-05.md`
>
> **Item 1 — re-derive P1–P6 and HALT on P3's failure.** ⛔ If `(f-stanza)` no longer parses the stanza into `stanza_fields`, this plan's premise of "no new parse" is void and it must be re-derived.
>
> **Item 2 — add check (w).** Inside the existing `(f-stanza)` block, where `stanza_fields` is already populated: if `writes` names any of `cycle_check`, `plan_lint`, `fold_check`, `propagation_check`, `walk_register_lint`, `mutation_check`, and `mutants` is missing, empty, or begins `NONE`, print one WARN naming the instrument(s) matched. ⛔ **Append no FAIL; do not touch `all_passed`.**
>
> **Item 3 — ⛔ THIS PLAN MUST SATISFY ITS OWN RULE.** Its `writes:` names `scripts/plan_lint.py`, so it is DC work by its own definition. Declare `mutants: knowledge/mutants/dc-mutation-declared.json` and build that manifest — at minimum a mutant that removes the instrument match and one that inverts the `mutants`-absent test. ⚠️ **A rule whose own introducing plan is exempt from it is not a rule.**
>
> **Item 4 — tests.** (w) fires on a plan writing an instrument with no `mutants:`; is silent when `mutants:` is declared; is silent for a plan writing no instrument; is silent when there is no manifest stanza at all; and `plan_lint`'s exit code is unchanged across all four.
>
> **Item 5 — dev-log**, recording the measured 6-of-11 gap and why the check is advisory rather than required (P6).
>
> **Item 6 — commit** (message tagged with the plan id); record `numstat`.
>
> **Deposits:**
> - `knowledge/development/dev-log-dc-mutation-declared-2026-09-05.md`
> - `knowledge/mutants/dc-mutation-declared.json`
>
> **Post-conditions:** (w) present and WARN-only; the four test cases pass; `plan_lint` exit code unchanged for every input; this plan's own `mutants:` declared and its manifest built; ⛔ **no doctrine file touched**.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO confirmation.**

---
---

## STEP 2 — QA

---

> Before starting, read `knowledge/development/dev-log-dc-mutation-declared-2026-09-05.md` and check its Output Receipt status. If status is not Complete, HALT and report.
>
> **Item 1 — the four cases demonstrated** with literal `plan_lint` output for each.
> **Item 2 — ⛔ the MUTATION CONTROL, which is this plan's whole subject:** run `mutation_check` against `knowledge/mutants/dc-mutation-declared.json` and show the kill map. ⚠️ **A plan introducing a mutation-declaration rule must itself be killed by its own mutants**; report survivors as failures.
> **Item 3 — no-regression:** full suite, and `plan_lint` before/after on a shipped plan showing identical output.
> **Item 4 — hygiene + receipt:** `numstat`, `reflog -n 4`, per-item table, then the Rule 20 self-check inside a Verification-headed section.
>
> **Deposits:**
> - `knowledge/qa/evidence/dc-mutation-declared-2026-09-05/qa-receipt.md`
> - `knowledge/qa/evidence/dc-mutation-declared-2026-09-05/probes-raw.txt`
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root, with:
> - `plan_slug`: `dc-mutation-declared-2026-09-05`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/dc-mutation-declared-2026-09-05/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/dc-mutation-declared-2026-09-05"`
> - `required_evidence_files`: `["probes-raw.txt"]`
>
> Include the literal stdout of the block in the QA report. Banner, byte-exact, inside the receipt's VERIFICATION section:
>
> ```
> Rule 20 — QA Self-Check Results
> ...
> PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
> ```
>
> ⛔ **Step 2 does not close on a FAILED self-check.** ⚠️ And no row of the per-item table may QUOTE a Rule 20 hedging keyword — describe markers, never quote them (thread 136).
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation.**
