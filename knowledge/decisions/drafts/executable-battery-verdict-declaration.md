# ⛔ WITHDRAWN AT WALK 0 — THE MACHINERY ALREADY DOES THIS. Do not execute. Do not deposit.

**Withdrawn 2026-09-03, on measurement, before lens 1.** This plan proposed a `plan_lint` check warning when a Cycle Manifest's `validation:` line omits `propagation_check`. Measured after drafting it: **`cycle_check --emit-manifest` already subprocess-runs `propagation_check.py`** (`scripts/cycle_check.py:640`) and writes its real verdict — `CLEAN`, `DIVERGENT:N`, or `NOT_RUN` — into the `validation:` field it generates. Verified live: emitting for `Done/executable-100030.md` produced `propagation_check=DIVERGENT:12`.

⛔ **So the premise was false.** The declaration is MACHINE-WRITTEN, not hand-typed. `diagnostic-100032`'s manifest lacked `propagation_check` for exactly one reason: **the author hand-typed the stanza instead of running the emitter.** The plan would have added a check to catch the author bypassing a tool that already does the work — machinery to police a practice failure.

**Two design flaws found in the same zoom-out, recorded so the class is not rebuilt:**
1. **It shipped a WARN, and its own P3 measured that this author ignores WARNs** (three times the same night). A remedy whose delivery mechanism is the one the finding says fails.
2. **It checked a DECLARATION, not a RUN** — satisfiable by typing a string. Structurally identical to the `[4/memory]` substring stub filed as thread 114 hours earlier: a presence check that passes without the work being done.

**What is actually owed, much smaller:**
- **Practice:** emit the manifest with `cycle_check --emit-manifest`; never hand-type the stanza. That alone closes the gap this plan was built for.
- **Optional check, SHAPE not value:** a manifest whose `validation:` line carries fewer than the emitter's four keys was hand-typed. ⚠️ It must test SHAPE — measured, stored and freshly-emitted values legitimately DRIFT after freeze (`fold_check PASS→N/A`, `DIVERGENT:50→56` on a compliant Done plan, because the record grows), so a value-equality check would false-positive on every closed plan.

**What survives for reuse:** P2's corpus battery table, P3's 90%-blast-radius measurement (which correctly killed register-level enforcement), P4's warning against schema-version exemption, and the six-plan positive control set.

---

# bellows — executable: `plan_lint` (w) — an emitted Cycle Manifest whose `validation:` line omits `propagation_check` warns at authoring, because the detector for this shop's dominant fold-damage class is recorded in 18% of registers and was run zero times across three cycles the same night

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_plan_lint.py` and a new `tests/test_plan_lint_battery_declaration.py`) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100032.md` (2026-09-03 — the drafting-battery-cost diagnostic, whose Q1/Q2 are this plan's licensing measurements) and `LESSONS.md` 2026-09-03 entry 414. Clone origin: `Done/executable-100028.md` (2026-09-03 — added `plan_lint` check (v), the newest shipped plan on this exact target, same warn-first shape, same authoring-time surface).

## What this changes

One `plan_lint` check, WARN-only: **when a plan emits a Cycle Manifest whose `validation:` line names some battery tools but not `propagation_check`, warn at authoring time.** Nothing else. No new detector, no new parser, no register-schema change.

## Why this exists

`propagation_check` exists for exactly one class — its docstring: *"The drafting cycle's walks catch defects of COMPREHENSION. They are poor at defects of PROPAGATION: a correction applied at the site where it was noticed and not at its siblings."*

Diagnostic 100032 measured that class at **75%** of this shop's fold-introduced findings, and measured the detector's recording rate at **18%** of 164 registers — third-lowest of six. ⚠️ **Measured on the author the same night:** three cycles authored, `propagation_check` run **zero** times on any, while those plans argued at length that incomplete propagation was the dominant self-damage. A fresh-context agent under the same doctrine ran it five times in one cycle.

**The convention already exists and is young.** Four recent plans carry it. This check makes the convention hold rather than inventing one.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the classifier already exists — DO NOT WRITE A SECOND | `tools/battery_census.py` ships `detect_battery(text)` returning `verbatim`/`paraphrase`/`not_recorded` per tool, with per-tool regexes at `_VERBATIM` (`:111`) and the dispatcher at `:144`. Built by plan 100032 hours before this plan. ⚠️ Two readers of one format diverge — thread 102's defect verbatim | read `tools/battery_census.py` |
| P2 | corpus battery rates, 164 registers | `plan_lint` 28/69/67 · `cycle_check` 5/43/116 · `fold_check` 0/48/116 · `propagation_check` 17/14/133 · `walk_register_lint` 7/20/137 · `mutation_check` 0/8/156 (verbatim/paraphrase/not_recorded) | run `detect_battery` over the register glob |
| P3 | ⛔ **why the check is NOT at the register level** | requiring `propagation_check` verbatim in registers fires on **147 of 164 (90%)**, and **57** registers record no battery tool at all. A warning on 90% of a corpus is noise, and noise is ignored — measured: this author ignored `plan_lint`'s standing WARNs three times tonight | count the registers failing that predicate |
| P4 | ⛔ **why NOT a schema-version exemption** | exempting older registers by declared version is the exact pattern plan **100029** shipped and **100030** had to correct — it exempted before it validated, losing 15 CONFORMANT registers and 415 fold rows. Do not re-introduce it | read `Done/executable-100030.md` |
| P5 | the convention exists at plan level | **5** of 546 `Done/` plans carry `propagation_check` in `validation:` — `executable-100025`, `100026`, `100028`, `100030` (+1). 54 have a `validation:` line without it; 487 have no `validation:` line at all | grep `^validation:` across `Done/` |
| P6 | ⛔ **zero retroactive blast radius** | `plan_lint` runs on the plan handed to it at authoring/freeze time. It does not scan `Done/`. So this check binds only plans authored after it ships — the 487 legacy plans are untouched by construction, which is what P3 and P4 could not achieve | read `plan_lint.main()` |
| P7 | ⛔ **positive control, and it discriminates against the author** | both plans authored by this session tonight FIRE — `diagnostic-100032` (`validation:` present, no `propagation_check`) and `halted-executable-100031` (no `validation:` line at all). The four recent compliant plans do NOT fire | run the predicate over those six files |
| P8 | the free check letter | `(a)`–`(v)` are in use; `(w)` and `(x)` are defined as checks **zero** times. ⛔ Derive the next free letter mechanically at execution rather than trusting this pin | `grep -oE '# \([a-z]\) ' scripts/plan_lint.py \| sort -u` |
| P9 | test homes | `tests/test_plan_lint.py` (138 tests) plus three focused siblings — `test_plan_lint_bare_constants.py`, `test_plan_lint_detector_checks.py`, `test_plan_lint_qa_predeclaration.py`. The clone origin (100028, check (v)) used a focused sibling | `ls tests/ \| grep plan_lint` |
| P10 | in-flight | re-derive at execution | `sqlite3 lifecycle.db "SELECT id,lifecycle_state FROM plans WHERE lifecycle_state NOT IN ('closed','done','halted','dropped')"` |

## What this does NOT do

- ⛔ **It does not make the check a FAIL.** WARN-only, matching check (v)'s shape from the clone origin. A FAIL here would block authoring on a convention five plans deep.
- ⛔ **It does not touch `walk_register_lint` or the register schema.** P3 measured that surface at 90% blast radius; the register-level enforcement I first proposed is **withdrawn on measurement**.
- **It does not require the other five battery tools.** `propagation_check` is singled out because P2 + the diagnostic's 75% figure give it a licensing case the others do not have. Widening to six tools is a separate decision with its own blast radius.
- **It does not require a particular VERDICT** — `DIVERGENT:N` and a clean result both satisfy it. The check is that the tool was run and its result declared, not what the result was.
- **It does not backfill any existing plan.**

## Drafting Cycle

**Tier:** T1 — T-3 fires (`plan_lint` runs on every machine that drafts). **T-6 does NOT fire**, checked against the trigger as QUOTED (*"Edits doctrine, the template, gates, or specialist contracts"*): `plan_lint` is an authoring-time linter, not a step gate, not doctrine, not the template — and the clone origin `100028` shipped the same surface at T1. ⚠️ **This reading is the one that inverted on the predecessor plan** (`wrap_check` read as "a wrap gate, not a step gate"); it is stated here with the trigger quoted so a later reader can check it rather than trust it. T-8 not fired: clone by kind of `Done/executable-100028.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-battery-verdict-declaration-2026-09-03.md`
**Walks:** 0 (context pin complete).
**⛔ `propagation_check` run AT WALK 0 — DIVERGENT:8, all classified.** Seven are symbol collisions (plan ids `100032`/`100028`/`100031` cited correctly at their declaration sites, and "Rule 20" colliding with P2's `walk_register_lint paraphrase=20`); **one was real** — a post-condition hardcoding the existing test count at 138, folded to re-derive it at execution. ⚠️ Run at walk 0 rather than never: this plan is about that detector, and shipping it unrun would be the degenerate-exemplar failure its own Item 5 forbids.

**Closing:** NOT CLOSED at walk 0.

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze; an unemitted manifest reclassified plan 100031 and dispatched it past the class hold, LESSONS.md 2026-09-03 entry 413. ⚠️ **This plan's own manifest must carry `propagation_check` in its `validation:` line** — a plan shipping this check that would fire it is the degenerate-exemplar failure.)*

## STEP 1 — DEV (one warn-first check, on an existing classifier)

> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_battery_declaration.py`
> - `knowledge/mutants/battery-verdict-declaration.json`
> - `knowledge/development/dev-log-battery-verdict-declaration-2026-09-03.md`
>
> **Item 1 — re-derive P1–P10 and HALT on mismatch.** ⛔ Re-derive P8's free letter mechanically; do not trust `(w)`. ⛔ Re-run P7's positive control and confirm both of this session's plans still fire and the four compliant ones do not — if that no longer discriminates, the predicate is wrong and this plan has no licensing case.
>
> **Item 2 — write the failing tests FIRST**, in a focused sibling `tests/test_plan_lint_battery_declaration.py` (the clone origin's shape):
> 1. ⛔ **manifest emitted, `validation:` present, `propagation_check` absent → WARN naming the check letter** — the regression this plan exists for
> 2. manifest emitted, `validation:` names `propagation_check=DIVERGENT:11` → **no warn**
> 3. manifest emitted, `validation:` names `propagation_check` with a clean verdict → **no warn** (the check is run-and-declared, not a particular result)
> 4. ⛔ **no Cycle Manifest emitted at all → NO warn from this check.** An unemitted manifest is check (v)'s and the freeze's problem, not this one; firing here would double-report and train the reader to ignore both
> 5. ⛔ **`validation:` line absent while a manifest IS emitted → warn**, and the message must distinguish this from case 1
> 6. ⛔ **the warn is a WARN, never a FAIL** — assert the exit code and the FAIL count are unchanged
> 7. ⛔ **positive control: a plan carrying `propagation_check` in prose but NOT in `validation:` still warns.** The check reads the manifest's declaration, not the document's vocabulary — otherwise any plan discussing the tool exempts itself, which is check (u)'s measured defect (thread 102: 75 divergences on 861 steps)
> 8. byte-identical output for a plan that does not emit a manifest — the no-op control
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — implement check (w).** ⛔ **Read the declaration from the emitted Cycle Manifest's `validation:` line**, using the manifest parser `cycle_check.parse_manifest_stanza` already provides — the same one `depositor._parse_plan` calls. ⛔ **Do NOT write a second manifest parser and do NOT re-implement `detect_battery`** (P1): two readers of one format diverge, which is thread 102's defect and the class this very plan is about.
>
> **Item 4 — `knowledge/mutants/battery-verdict-declaration.json`**, one mutant per branch: drop the absent-`propagation_check` arm → test 1 fails; drop the no-manifest guard → test 4 fails; turn the WARN into a FAIL → test 6 fails; read the token from the whole document instead of `validation:` → test 7 fails. ⚠️ **A survivor is a missing test, stated as Critical** — and ⛔ **0 ERROR is required**. Every anchor must be count-1 in its own file at HEAD, and every `target` must be a repo-relative path present at HEAD (thread 105: an absolute `target` escapes the sandbox and reports every mutant falsely SURVIVED).
>
> **Item 5 — dev-log**, recording P2's corpus table, P3's withdrawn register-level design and why, and P7's positive control output verbatim.
>
> **Item 6 — commit** (message tagged with the plan id); record `numstat` — exactly 4 files.
>
> **Deposits:**
> - `knowledge/development/dev-log-battery-verdict-declaration-2026-09-03.md`
>
> **Post-conditions:** all eight tests pass; **every** existing `test_plan_lint.py` test unchanged (count re-derived at execution — it was 138 at authoring, and a hardcoded figure would make this post-condition false for a reason unrelated to this change); `plan_lint`'s FAIL count on a shipped compliant plan unchanged (WARN-only proven, not asserted); the check fires on both of this session's plans and on neither of the four compliant ones, shown as a before/after pair in one run; the runner's own mutants all killed, 0 error.

## STEP 2 — QA (full suite + the check shown to discriminate)

> **Item 1 — full suite** from the dispatch worktree, output to `pytest_full.txt`. ⚠️ The canonical checkout carries a `config.json` that makes `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` fail; a worktree has none and the suite is green there. `known_failures: 0` is correct for the dispatch location — do not raise it.
>
> **Item 2 — the check discriminates, both directions.** Run `plan_lint` over the six-plan control set: the two this session authored (must WARN) and the four carrying the declaration (must not). ⛔ Then run the SAME set against the pre-change `plan_lint` and show it warns on none — the fixture must be proven to discriminate, not merely to pass.
>
> **Item 3 — no-regression:** every existing `plan_lint` test file green; `plan_lint`'s output on a shipped compliant plan byte-identical apart from the new WARN's absence.
>
> **Item 4 — the runner's own kill map:** `mutation_check` over `knowledge/mutants/battery-verdict-declaration.json` → all killed, 0 survived, **0 error**.
>
> **Item 5 — self-application.** ⛔ Run the shipped check against THIS plan. It must NOT warn — this plan's own manifest declares `propagation_check`. A plan that ships a check it would itself fire is the degenerate-exemplar class (`LESSONS.md` 2026-09-03: a plan seeded the exact false negative it documented, in its own QA step).
>
> **Item 6 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `battery-verdict-declaration-2026-09-03`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/battery-verdict-declaration-2026-09-03/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/battery-verdict-declaration-2026-09-03"`
> - `required_evidence_files`: `["pytest_full.txt", "probes-raw.txt"]`
>
> Include the literal stdout of the block in the QA report. Banner, byte-exact, inside the receipt's VERIFICATION section:
>
> ```
> ============================================================
> Rule 20 — QA Self-Check Results
> ============================================================
> PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
> ```
>
> ⛔ If the block prints `FAILED`, do not proceed with closure — halt and report.
>
> **Deposits:**
> - `knowledge/qa/evidence/battery-verdict-declaration-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/battery-verdict-declaration-2026-09-03/pytest_full.txt`
> - `knowledge/qa/evidence/battery-verdict-declaration-2026-09-03/probes-raw.txt`
>
> **Post-conditions:** suite green from a worktree, 0 failed; the check shown to discriminate on the six-plan control set AND shown not to fire before the change; existing plan_lint tests green; kill map clean; this plan does not fire its own check.
