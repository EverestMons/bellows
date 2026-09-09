# bellows — executable: A CLOSURE CLAIM WITH NO WALK DATA ESCALATES, AND THE WALK REGISTER LINT SAYS WHAT IT COVERS — `cycle_check` moves its closure check above the empty-walk return (213); `walk_register_lint` gains a COVERAGE verdict reconciled against the plan's declared folds per walk and renames CONFORMANT to SHAPE-OK (215, closing 135)

**Date:** 2026-09-09 | **Project:** bellows | **Tier:** Medium (nine source and test files, two drafting instruments) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — checker logic; a verdict TOKEN three consumers read changes, so `pytest tests/` gates every DEV commit — LESSONS 2026-09-08/09; new sibling `tests/test_register_coverage.py`; `tests/test_cycle_check.py` edited at its state-space generator; `tests/test_cycle_check_empty_body_silence.py` rewritten at one test and extended by one; `tests/test_walk_register_lint.py` and `tests/test_run_check.py` edited at their token literals; `tests/test_substrate_check.py`, `tests/test_cycle_check_t0_close.py`, `tests/test_cycle_check_register_resolver.py` unchanged) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1 | **Discharges:** thread 213, thread 215, thread 135

**auto_close:** false

**Post-close:** the daemon imports neither script (`cycle_check` runs as a subprocess from the depositor's battery and from `fold_check`; `walk_register_lint` from `fold_check`, `run_check` and the governance pre-commit hook) — **no restart owed**; the new verdicts are live at merge. ⚠️ One governance-side comment names the old token: `.githooks/pre-commit` lines 4/10/38 say "CONFORMANT" in comments only (its logic reads the row-status column, unchanged) — a one-line comment edit by the Planner at close, outside this plan's Scope. GLOSSARY gains *coverage verdict* at the wrap.

**Depends on:** the CEO rulings of 2026-09-08 — **213** (a closure claim with NO walk data ESCALATES `claimed-close-unmet`; the eight Tier-2 state-space cells `none × {bar_met, met_the_bar} × {absent, absolute, unresolvable, commentary}` flip in the SAME commit as the code; `28a08e5`'s UNRESOLVABLE WARN stays) and **215** on thread 135's three-way decision — (i) the lint reconciles rows-per-walk against the plan's Drafting Cycle declaration, reporting SHAPE and COVERAGE as SEPARATE verdicts; (ii) CONFORMANT renamed so it stops implying completeness; (iii) panel findings become rows when they are folded; (iv) the lint stays runnable mid-cycle — the highest-numbered walk is in progress and never INCOMPLETE (`lens_order_check`'s convention). Clone origin BY KIND: `Done/executable-100030.md` (2026-09-03, the newest `walk_register_lint` plan — validate-first, one manifest per target; T1) and `Done/executable-100042.md` (2026-09-08, the newest `cycle_check` plan; T1); BY LAYOUT: `Done/executable-100049.md` (2026-09-08, the newest T1). `clone-origin` threads naming any: none open (DC v2.33 query at walk 0).

**Tier computed (§1):** **T1** by the CEO's rulings on both threads. T-6 is ADJACENT, not fired: the two scripts are drafting instruments consumed by the depositor's battery and the pre-commit hook, not doctrine, the template, a gate module or a specialist contract; no doctrine text names the token (DC line 44 names the tool, not its verdict). T-1 does not fire (two instruments, one subsystem — the drafting battery); T-2 does not (no data).

## What this changes

⛔ **One check moved and eight cells flipped (213); one new verdict field, one renamed token, three consumers re-pointed (215). Nothing else in either instrument moves.**

1. **`cycle_check.run_check` — the empty-walk branch** (`scripts/cycle_check.py:463-523`): AFTER the thread-156 T0 arm (a well-formed T0 close still reaches BAR_MET first) and BEFORE the `_nw_verdict` CONTINUE return, insert the closure check that `:633` applies on every other path: `if parsed["claims_closure"] and not parsed["has_unparseable"]: return "ESCALATE:claimed-close-unmet", 1`. The 151/158 comment block (`:514-522`, "DELIBERATELY LEFT OPEN … RATIFIED") is REPLACED by a comment naming ruling 213. ⚠️ Consequence, stated: a T0 plan that BOTH claims closure and states no lens-4 result now ESCALATES instead of WARN + CONTINUE (ruling 119's "refuse on silence", made blocking only where a claim is made); a T0 plan claiming closure WITH its result is unchanged (BAR_MET via the T0 arm, which runs first). `28a08e5`'s UNRESOLVABLE WARN is emitted before the check and is unchanged.
2. **The Tier-2 state-space generator** (`tests/test_cycle_check.py:770-830`): rule 2 splits — `none walk + claim close → ESCALATE:claimed-close-unmet` (eight cells) and `none walk + non-claim close → CONTINUE` (twelve cells); the `_WALK_DIM` comment `no walk lines → CONTINUE regardless` and the rules comment are re-worded; `test_state_space_table_complete` is untouched. The characterisation test `test_claiming_closure_with_an_empty_body_stays_CONTINUE_by_RATIFIED_precedence` (`tests/test_cycle_check_empty_body_silence.py:82`) is REWRITTEN as `test_claiming_closure_with_an_empty_body_ESCALATES_by_ruling_213` (its docstring names the ruling and thread 158's reasoning), and the file gains `test_T0_claiming_closure_without_a_result_ESCALATES` (the consequence in change 1, pinned).
3. **`walk_register_lint` — the tokens** (`scripts/walk_register_lint.py:17-24`): `STATUS_CONFORMANT`'s VALUE becomes `SHAPE-OK` and `STATUS_UNCONFORMANT`'s `SHAPE-FAIL`; the constant NAMES stay (three importers: `cycle_check.py:27-35`, `substrate_check.py:31`, the tests) and two aliases `STATUS_SHAPE_OK`/`STATUS_SHAPE_FAIL` are added; `PRE-SCHEMA`, `NO_TABLE`, `LEGACY_SCHEMA`, `FUTURE_SCHEMA` are unchanged; the `:21` comment ("Names must NOT start with CONFORMANT or NO_TABLE — judge_register classifies by …") is re-worded to the new names. `coverage_basis`'s text `coverage NOT checked` becomes `coverage: see COVERAGE` and its docstring's first paragraph names the new field.
4. **`walk_register_lint.coverage_verdict(text, register_path, plan_path=None) -> (token, detail)`** — new. **Plan resolution:** `plan_path` (the new CLI option `--plan <path>`), else the register's `Draft:` line (`` Draft: `<governance-relative path>` ``) resolved by walking UP from the register's directory until `<ancestor>/<that path>` exists, else that path's basename under `<ancestor>/governance/knowledge/decisions/*/` or `<ancestor>/knowledge/decisions/{,Done/}` for any ancestor; unresolved → `("UNDECLARED", "plan not resolvable: <ref>")`. **Declared folds per walk:** the plan's FIRST Drafting Cycle block (`cycle_yields.extract_dc_blocks`) parsed by `cycle_check.parse_block` (imported INSIDE the function — `cycle_check` imports this module at load, so a module-level import would be circular) → `walk_data[wn]["total_folds"]`, else `instruction + record`; no lens lines → `("UNDECLARED", "plan declares no lens walks")`. **Rows per walk:** over every fold table (`is_fold_table`) with a `walk` column, count rows by the walk cell; a cell that is not a positive integer (`panel-1`, `panel`, `0`) is counted separately as `panel rows` / `walk-0 rows` and NEVER reconciled (ruling iii's rows are visible in the detail; they are not walk rows). **Reconciliation:** for every declared walk EXCEPT the highest-numbered (ruling iv — in progress), rows ≥ declared → covered, rows < declared → short; `("INCOMPLETE", "w2 rows=3 declared=5; w4 rows=0 declared=2")` when any completed walk is short, else `("COVERED", "w1 11/7 w2 6/4 … (rows ≥ declared on every completed walk; w7 in progress; panel rows 46)")`. A register with no fold table → `("UNDECLARED", "no fold table")`. Measured on the nine September registers whose plan resolves (P4): every completed walk is COVERED; five walks carry MORE rows than declared folds (sub-rows `f17b`/`f17c` count as rows) — which is why the test is `≥`, never `==`.
5. **The lint's output line** (`main`, `:451-453`): the stderr summary gains ONE field after the status — `<name>\t<status>\tCOVERAGE: <token> — <detail>\tBASIS: …\tshapes: …` — so `run_check.judge_register`'s `split("\t")[1]` still reads the status; stdout rows are unchanged (the pre-commit hook reads column 4 of stdout, untouched). `--plan <path>` is accepted before the target.
6. **The three consumers.** `tools/run_check.py:65-76` `judge_register`: `bad` matches `\tSHAPE-FAIL`, `\tNO_TABLE` OR `\tCOVERAGE: INCOMPLETE`; `good` matches `\tSHAPE-OK`; the three messages say `SHAPE-OK`; the module docstring `:17-20` re-worded. `scripts/substrate_check.py:80` compares to `walk_register_lint.STATUS_CONFORMANT` instead of the literal `"CONFORMANT"`, and `:117`'s text says `SHAPE-OK`. `scripts/cycle_check.py:33-35`'s comment re-worded (the frozenset already holds the constants). ⚠️ Consumers enumerated by EFFECTS too (LESSONS 2026-09-09): every test that asserts the stderr line's text — `tests/test_walk_register_lint.py` (28 literals), `tests/test_run_check.py` (20 literals), `tests/test_cycle_check.py:1136` (a docstring only, left) — and no test asserts the field COUNT of the stderr line (measured at walk 0: `split("\t")` on the summary line appears in `run_check` only).

## Why this exists

Thread 158 (split from 151) measured the asymmetry: `cycle_check`'s closure check at `:633` returns `ESCALATE:claimed-close-unmet` whenever a plan claims closure and the verdict is CONTINUE — except on the empty-walk path, where an early return answers CONTINUE first; a plan asserting BAR MET with no walks is told CONTINUE in silence, the shape a fabricated close takes. It was ratified by eight state-space cells, so it needed a ruling, and the CEO ruled on 2026-09-08: change it (213). Thread 135 (a cold CAPSTONE seat, 2026-09-04) measured `walk_register_lint` reporting CONFORMANT over a register carrying rows for 14 of 48 findings — CONFORMANT attests row SHAPE and was read as "the register is in order" in freeze records and to the CEO; the 2026-09-04 repair stated the BASIS ("coverage NOT checked") and the CEO ruled on 2026-09-08 (215): reconcile, rename, panel rows, mid-cycle safe. Both are the same class as thread 196's: a verdict that cannot see absence is quoted as if it could.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ `cycle_check`'s empty-walk branch | `scripts/cycle_check.py` at bellows `612d6fe`: `if not walk_data:` `:463`; the 151 UNRESOLVABLE WARN `:488-493`; the T0 arm `:499-509` (`_t0_close` `:729`); the 151/158 "DELIBERATELY LEFT OPEN" comment `:514-522`; `_nw_verdict` CONTINUE return `:523`; the closure check `:633` `if parsed["claims_closure"] and verdict == "CONTINUE" and not parsed["has_unparseable"]: return "ESCALATE:claimed-close-unmet", 1`; `parse_block` `:114` returns `walk_data`, `claims_closure`, `has_unparseable` | `grep -n`; read `:455-530`, `:625-637` |
| P2 | ⛔ the ratified table | `tests/test_cycle_check.py:770-830`: `_WALK_DIM` (`none`, `plain_walk`, `lens_spaced`, `lens_hyphen`), `_CLOSE_DIM` (5), `_REG_DIM` (4); `_EXPECTED` built by five rules in priority order, rule 2 `elif _w == "none": "CONTINUE"`; 80 cells, `test_state_space_table_complete`; 64 `def test_`, 143 collected (parametrized). `tests/test_cycle_check_empty_body_silence.py`: 4 tests, the ratified one at `:82`. `tests/test_cycle_check_t0_close.py`: 6 tests; its `_t0` fixture (`:20-30`) writes NO `**Closing:**` line, so no T0 test claims closure today | grep; `pytest --collect-only -q` |
| P3 | ⛔ the lint and its consumers | `scripts/walk_register_lint.py` 460 lines: tokens `:17-24`, `coverage_basis` `:73-97` (`_FINDING_DECL_RE` `:70`, the unreconciled prose count), `validate_file` `:264-335` returns `(status, rows, shapes)`, `main` `:418-457` prints `HEADER` then per file the stderr line `<name>\t<status>\tBASIS: …\tshapes: …` and stdout TSV rows. Consumers of the TOKEN: `tools/run_check.py:65-76` (`judge_register`: `"\tUNCONFORMANT"`, `"\tNO_TABLE"`, `"\tCONFORMANT"` substrings on stderr; `split("\t")[1]` for the label), `scripts/substrate_check.py:77-81,117` (literal `"CONFORMANT"`), `scripts/cycle_check.py:27-35` (imports the constants into `_REGISTER_SILENT_STATUSES`); the governance hook `.githooks/pre-commit:37-46` reads stdout column 4 (`$4!="OK"`), never the token (comments only). Runners: `scripts/fold_check.py:99-101`, `tools/run_check.py:87`, `scripts/plan_lint.py:811` (a name list) | grep from the token, from the constant names, and from `split("\t")` |
| P4 | corpus 215 (replay at walk 0, in-process, read-only) | of 48 September registers, 9 resolve their `Draft:` line to a plan with lens lines; rows-per-walk vs declared folds: every completed walk has rows ≥ declared; rows EXCEED declared on w1/w2/w3/w6 of five registers (sub-rows counted as rows); two registers carry `panel-1`/`panel-2` walk cells; 39 registers resolve NO plan (older plans renumbered into `Done/executable-<id>.md`, or governance-lane plans) — UNDECLARED by design | the script in the register |
| P5 | corpus 213 (replay at walk 0) | of 193 plans with a Drafting Cycle block (bellows Done, governance drafts and Done), ONE has a closure claim with empty `walk_data`: `executable-432.md`, already `ESCALATE:unparseable` (the unparseable check precedes the new one). Thread 158's "0 plans" holds: the change flips nothing live | the script in the register |
| P6 | tests | `tests/test_walk_register_lint.py` 45; `tests/test_run_check.py` 17 (`test_conformant_pass` `:86`, `test_unconformant_fail` `:80`, `test_register_on_walk_register` `:234`); `tests/test_substrate_check.py` 8 (0 token literals); `tests/test_cycle_check_register_resolver.py` 6 (0 literals) | `grep -c`; `pytest --collect-only` |
| P7 | in-flight | none; daemon pid 69409 on `d323637` (restarted after 100052), not a consumer of either script | `status.py` |
| P8 | class; eligibility | `scripts/*.py` → shop-infra; HOLDS at admission, the CEO releases | `_assign_class` |
| P9 | the mutation tool | one manifest per `target` (100030's shape): `{"target": "scripts/cycle_check.py", "mutants": [ … ]}` — the `target` value is the repo-relative path as `knowledge/mutants/cycle-check-battery.json` spells it | that file |

## What this does NOT do

- ⛔ **It does not make coverage a commit blocker.** The pre-commit hook reads row status only; `run_check` (the battery's judge) FAILS on `COVERAGE: INCOMPLETE` — the depositor's battery is where a short register is refused, at deposit, not at every draft commit.
- ⛔ **It does not reconcile panel rows or walk-0 rows** — they are counted and shown in the detail (ruling iii makes them ROWS; the walk they fold at has no lens line to declare against). Fork 1: a `panel: N findings` declaration on the plan's panel line, reconciled like a walk.
- ⛔ **It does not require rows == declared** — five registers already carry more rows than folds (sub-rows). `≥` is the assertion; an over-count is shown, never failed.
- **It does not change `cycle_check`'s verdict for any plan in the corpus today** (P5); the flip is pre-emptive by ruling.
- **It does not touch doctrine** — DC line 44 names the tool, not the token; the GLOSSARY entry *vacuous verdict* quotes the old token as history (append-only); the hook's comments are the Planner's close act.
- **It does not rename the constant NAMES** — three importers keep working; the aliases are for new code.

## MUST-PRESERVE

⛔ **Invariants that must still be TRUE afterwards.**

- ⛔ **Every non-claiming plan's `cycle_check` verdict is byte-identical** — the 72 non-claim cells of the state-space table, every T0 test, the resolver tests and the silence file's other three tests pass UNCHANGED. Proven by the full suite at every commit.
- ⛔ **A well-formed T0 close still reaches BAR_MET** (`test_a_well_formed_T0_reaches_BAR_MET`). Proven by the suite; mutant M2 is killed by the new T0 test's second half (claim + result → BAR_MET).
- ⛔ **The lint stays runnable mid-cycle and never judges the walk in progress** — the highest declared walk is excluded from INCOMPLETE. Proven by tests 6–7.
- ⛔ **Stdout rows are byte-identical** — the hook's column-4 read is unaffected; the stderr line gains one field at position 3 and `split("\t")[1]` still yields the status. Proven by tests 9–10 and QA Item 4.
- ⛔ **A register whose plan cannot be found is UNDECLARED, never INCOMPLETE** (39 of 48 September registers). Proven by test 8.
- ⛔ **No importer of `STATUS_CONFORMANT`/`STATUS_UNCONFORMANT` breaks** — the names stay. Proven by the suite (`cycle_check`, `substrate_check`).

## Drafting Cycle

**Tier:** **T1** — the CEO's rulings on 213 and 215; T-6 adjacent, not fired. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-closure-claim-and-register-coverage-2026-09-09.md
**Walks:** walk 0 pinned (P1–P9 measured on bellows `612d6fe`; clone-diff against `Done/executable-100030.md` and `Done/executable-100042.md` (kind) and `Done/executable-100049.md` (layout) run: FACTS, ARTEFACTS, STRUCTURE; two corpus replays run in-process, read-only); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit, emit after the re-save (v2.30). ⛔ **One commit per lens** (§2.7); `lens_order_check` runs with `cycle_check` at every walk close; the commit loop asserts each subject names its lens and gates on the register lint (LESSONS 2026-09-09).

**Closing:** WARM close after walk 5 — the plan for threads 213/215/135, a judged stop. Five walks: 6 → 3 → 4 (ESCALATE:yield-rising — the CEO ruled PROCEED, read-only) → 1 → 0; T1, no panel. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases (`clear_plan --release-class-hold`). No restart owed. Close acts: the Planner's one-line comment edit in the governance `.githooks/pre-commit`; `threads done` for 213, 215, 135 with `--commit bellows:<DEV sha>` after the daemon's push; fork 4's thread filed at deposit; GLOSSARY *coverage verdict* at the wrap.
- Weak spots:          w1 6 folded — instruction 6 / record 0
- Destruction:         w1 dry
- Vulnerabilities:     w1 dry
- Integration-record:  w1 dry
- ACID:                w1 dry
- Weak spots:          w2 2 folded — instruction 2 / record 0
- Destruction:         w2 1 folded — instruction 1 / record 0
- Vulnerabilities:     w2 dry
- Integration-record:  w2 dry
- ACID:                w2 dry
- Weak spots:          w3 4 folded — instruction 4 / record 0
- Destruction:         w3 dry
- Vulnerabilities:     w3 dry
- Integration-record:  w3 1 folded — instruction 0 / record 1
- ACID:                w3 dry
- Weak spots:          w4 1 folded — instruction 1 / record 0
- Destruction:         w4 dry
- Vulnerabilities:     w4 dry
- Integration-record:  w4 dry
- ACID:                w4 dry
- Weak spots:          w5 dry
- Destruction:         w5 dry
- Vulnerabilities:     w5 dry
- Integration-record:  w5 dry
- ACID:                w5 dry
**Walk 5 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the WARM close meets the bar (§2) — a judged stop (14 findings over four walks: instruction 13 / record 1; yield 6 → 3 → 4 → 1 → 0; the CEO ruled PROCEED read-only at walk 3's ESCALATE). T1: no panel owed.**

## Cycle Manifest
tier: T1
target: scripts/walk_register_lint.py
class: shop-infra
reads: scripts/cycle_check.py, scripts/walk_register_lint.py, scripts/cycle_yields.py, tools/run_check.py, scripts/substrate_check.py, tests/test_cycle_check.py, tests/test_cycle_check_empty_body_silence.py, tests/test_cycle_check_t0_close.py, tests/test_walk_register_lint.py, tests/test_run_check.py, knowledge/decisions/Done/executable-100030.md, knowledge/decisions/Done/executable-100042.md, knowledge/decisions/Done/executable-100049.md
writes: scripts/cycle_check.py, scripts/walk_register_lint.py, tools/run_check.py, scripts/substrate_check.py, tests/test_cycle_check.py, tests/test_cycle_check_empty_body_silence.py, tests/test_walk_register_lint.py, tests/test_run_check.py, tests/test_register_coverage.py, knowledge/mutants/closure-claim-cycle_check.json, knowledge/mutants/register-coverage-walk_register_lint.json, knowledge/mutants/register-coverage-run_check.json, knowledge/mutants/closure-claim-cycle_check.run.txt, knowledge/mutants/register-coverage-walk_register_lint.run.txt, knowledge/mutants/register-coverage-run_check.run.txt, knowledge/development/dev-log-closure-claim-and-register-coverage-2026-09-09.md
open_forks: 1. a `panel: N findings` declaration on the plan's panel line, reconciled against `panel-*` rows like a walk (ruling iii's mechanical half); 2. a register-side declaration line (`**Walk N declared:** K`) as an override when the plan is unreachable — only if UNDECLARED proves too common on live cycles; 3. the pre-commit hook judging COVERAGE at the close commit only — a governance-hook change, its own thread; 4. `_has_closure_claim`'s vocabulary (`BAR MET`, `met the bar`) does not read the current closing idiom (`WARM close after walk N — … meets the bar`) as a claim, measured at walk 3 on 100049 and 100045 — so the closure check guards none of September's plans; a thread at deposit (widen the claim vocabulary, or the idiom writes the token)
walks: 5
yields: 6, 3, 4, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:24
coherence: 5/5 body walks named in the register (16 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-closure-claim-and-register-coverage.md.foldcheck.json

---

## STEP 1 — DEV (one check moved + eight cells; one verdict field, one rename, three consumers; three manifests; three commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f scripts/cycle_check.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE**; prove `VENV_OK` with `-c 'import pytest'`. ⛔ **Never run the daemon, `run_plan`, or a claim; never import `lifecycle`** — the tests build plans and registers as strings under `tmp_path` and live under `tests/`; a corpus replay is in-process and read-only (no `git` writes, no lane files). ⛔ **Every commit gates on the FULL suite** and uses `git commit -F <msg-file> -- <paths>` (Rule 75).
>
> **Scope:**
> - `scripts/cycle_check.py`
> - `scripts/walk_register_lint.py`
> - `tools/run_check.py`
> - `scripts/substrate_check.py`
> - `tests/test_cycle_check.py`
> - `tests/test_cycle_check_empty_body_silence.py`
> - `tests/test_walk_register_lint.py`
> - `tests/test_run_check.py`
> - `tests/test_register_coverage.py`
> - `knowledge/mutants/closure-claim-cycle_check.json`
> - `knowledge/mutants/register-coverage-walk_register_lint.json`
> - `knowledge/mutants/register-coverage-run_check.json`
> - `knowledge/mutants/closure-claim-cycle_check.run.txt`
> - `knowledge/mutants/register-coverage-walk_register_lint.run.txt`
> - `knowledge/mutants/register-coverage-run_check.run.txt`
> - `knowledge/development/dev-log-closure-claim-and-register-coverage-2026-09-09.md`
>
> **Item 1 — re-derive P1, P2, P3, P6 and HALT on a mechanism mismatch** (P4, P5, P7–P9 are records; a line-number drift is not a mechanism mismatch). Also grep for consumers BY EFFECT: `grep -rn 'split("\\t")' scripts/ tools/ tests/ | grep -i regist` and any test asserting the stderr summary line's field count — paste the (expected-empty) result into the dev-log.
>
> **Item 2 — write 213's failing tests FIRST.** In `tests/test_cycle_check_empty_body_silence.py`: rewrite the `:82` test to `test_claiming_closure_with_an_empty_body_ESCALATES_by_ruling_213` (a plan with `**Closing:** ✅ BAR MET`, no walk lines, a resolvable register → `ESCALATE:claimed-close-unmet`); add `test_T0_claiming_closure_without_a_result_ESCALATES` (the `_t0` shape from `tests/test_cycle_check_t0_close.py` PLUS a `**Closing:** BAR MET` line and no lens-4 result → ESCALATE; with the result → BAR_MET — the T0 arm first). In `tests/test_cycle_check.py`: change rule 2 of `_EXPECTED` as change 2 (the eight cells flip; nothing else). Run those two files and record the output before Item 3 (the rewritten test and the new T0 test red; the eight flipped cells red).
>
> ⛔ 215's tests are written AFTER Item 5's commit (Item 6a): the 48 token-literal edits would turn the full suite red before Item 5 could gate on it.
>
> **Item 3 — 213** as change 1 (the check after the T0 arm, before the CONTINUE return; the comment block replaced). **Item 4 — the table** as change 2.
> **Item 5 — first commit (213)**, gated on the FULL suite, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && git add scripts/cycle_check.py tests/test_cycle_check.py tests/test_cycle_check_empty_body_silence.py knowledge/mutants/closure-claim-cycle_check.json && git commit -F <msg-file> -- scripts/cycle_check.py tests/test_cycle_check.py tests/test_cycle_check_empty_body_silence.py knowledge/mutants/closure-claim-cycle_check.json` — four files, message tagged with the plan id AND `thread 213`. THEN run manifest A (Item 8) before touching any 215 file. ⛔ Manifest A `{"target": "scripts/cycle_check.py", "mutants": [ … ]}` (keys `name`/`why`/`anchor`/`replacement`/`expect_fail`, anchors count-1, one test per selector) — TWO: M1 the new check deleted → `test_claiming_closure_with_an_empty_body_ESCALATES_by_ruling_213`; M2 the check moved ABOVE the T0 arm → `test_T0_claiming_closure_without_a_result_ESCALATES` (its second half: claim + result must still reach BAR_MET; `test_a_well_formed_T0_reaches_BAR_MET` cannot kill it — its fixture claims nothing).
> **Item 6a — 215's failing tests, written AFTER Item 5's commit and manifest A's run.** In `tests/test_register_coverage.py` (new; plans and registers as strings under `tmp_path`, the register in a `governance/knowledge/research/` subtree and the plan at the `Draft:` path under the same tmp root so resolution walks up):
> 1. ⛔ **COVERED** — plan lens lines `w1 3 folded`, `w2 1 folded`, `w3 dry`; register rows: three `| 1 |`, one `| 2 |` → `("COVERED", …)` with `w1 3/3 w2 1/1` in the detail and `w3 in progress`
> 2. ⛔ **INCOMPLETE** — the same plan, register with two `| 1 |` rows and the one `| 2 |` row kept → `("INCOMPLETE", "w1 rows=2 declared=3")`; w2 (1/1) is not named
> 3. ⛔ **rows exceed declared is COVERED** — four `| 1 |` rows against `w1 3 folded` → COVERED, detail `w1 4/3`
> 4. ⛔ **panel and walk-0 rows are counted, not reconciled** — rows `| panel-1 |`, `| panel-2 |`, `| 0 |` beside the walk rows → the verdict is unchanged and the detail says `panel rows 2; walk-0 rows 1`
> 5. ⛔ **`--plan` overrides the `Draft:` line** — a register whose `Draft:` is unresolvable but `--plan <tmp plan>` given → reconciled; the CLI accepts `--plan` before the target
> 6. ⛔ **the highest walk is never judged** — plan `w1 3 folded`, `w2 4 folded` (w2 the highest) and a register with three `| 1 |` rows and zero `| 2 |` rows → COVERED (`w2 in progress`)
> 7. ⛔ **a single-walk plan** (`w1 5 folded` only) with 0 rows → COVERED (w1 in progress) — mid-cycle at walk 1
> 8. ⛔ **UNDECLARED** — (a) no `Draft:` line and no `--plan` → `("UNDECLARED", "plan not resolvable: …")`; (b) a plan with no lens lines → `plan declares no lens walks`; (c) a register with no fold table → `no fold table`; none of the three is INCOMPLETE
> 9. ⛔ **the stderr line** — running `main` as a subprocess on `Path(__file__).resolve().parent.parent / "scripts" / "walk_register_lint.py"` (the script BESIDE the test — under the mutation sandbox that is the mutated copy; never an absolute repo path) prints `<name>\tSHAPE-OK\tCOVERAGE: COVERED — …\tBASIS: …\tshapes: …`; `split("\t")[1] == "SHAPE-OK"`; a shape-bad register prints `SHAPE-FAIL`
> 10. ⛔ **stdout rows are byte-identical** to the pre-change output for a fixture register (the expected stdout is a LITERAL in the test, pasted from `main`'s output on the fixture at the moment the test is written — after Item 5, before Item 6's implementation — the hook's column-4 contract)
> 11. ⛔ **`run_check.judge_register`** — stderr with `\tSHAPE-OK\tCOVERAGE: COVERED` → PASS; with `\tSHAPE-OK\tCOVERAGE: INCOMPLETE — w1 rows=2 declared=3` → FAIL naming INCOMPLETE; with `\tSHAPE-FAIL` → FAIL; with no `\tSHAPE-OK` line → the positive-control FAIL
> 12. ⛔ **`substrate_check`** compares to the constant — monkeypatch `walk_register_lint.STATUS_CONFORMANT` to a sentinel and assert `substrate_check` accepts a register whose `validate_file` returns it (its `:80` no longer holds a literal)
> Then edit the 28 + 20 token literals in `tests/test_walk_register_lint.py` and `tests/test_run_check.py` to `SHAPE-OK`/`SHAPE-FAIL`. Run the sibling and the two edited files; record the output before Item 6 (tests 1–9 and 11–12 red; test 10 green by construction; the 48 literal edits red).
> **Item 6 — 215** as changes 3–6: the tokens and aliases; `coverage_verdict` (plan resolution, `parse_block` imported inside the function, rows per walk, `≥`, the highest walk excluded, panel/walk-0 rows counted); `main`'s `--plan` and the new stderr field; `run_check.judge_register`; `substrate_check:80,117`; the `cycle_check:33-35` comment.
> **Item 7 — second commit (215)**, gated on the FULL suite, path-scoped over `scripts/walk_register_lint.py tools/run_check.py scripts/substrate_check.py tests/test_walk_register_lint.py tests/test_run_check.py tests/test_register_coverage.py knowledge/mutants/register-coverage-walk_register_lint.json knowledge/mutants/register-coverage-run_check.json` — eight files, message tagged with the plan id AND `thread 215, thread 135`. ⛔ Manifest B (`target` `scripts/walk_register_lint.py`) — FIVE: M3 `≥` becomes `==` → test 3; M4 the highest walk judged → test 6; M5 UNDECLARED replaced by COVERED when the plan is unresolvable → test 8a; M6 `STATUS_CONFORMANT` left `"CONFORMANT"` → test 9; M7 `panel-*` cells counted as walk rows of walk 1 → test 4. Manifest C (`target` `tools/run_check.py`) — ONE: M8 `judge_register` ignores `COVERAGE: INCOMPLETE` → test 11.
> **Item 8 — the three mutation runs, REDIRECTED** into `knowledge/mutants/closure-claim-cycle_check.run.txt`, `…/register-coverage-walk_register_lint.run.txt`, `…/register-coverage-run_check.run.txt` (Deposits): `tools/mutation_check.py <manifest> > <run> 2>&1; echo "exit=$?"` → `exit=0` each; last `MUTATION:` lines `2 killed`, `5 killed`, `1 killed`, `0 survived, 0 error`; `HEAD:` the FULL sha of the commit that last touched that manifest — TRUE only if manifest A's run happens IMMEDIATELY after Item 5's commit (before any 215 file is edited) and B's and C's immediately after Item 7's: the tool archives HEAD, so a run made later carries a later sha. A survivor is a missing test: fix the test AND re-touch the manifest in ONE further commit, re-run.
> **Item 9 — dev-log** with FIVE literal headings, declared for the gate on the `**Headings:**` line below; no declared section carries a fenced block with `#`-led lines. `## Corpus replay` OPENS with P5's value cell pasted verbatim (arm (b) reads it), then re-runs both walk-0 replays over the corpus AFTER the change (in-process, read-only): the 213 replay must again name only `executable-432.md`; the 215 replay prints each September register's COVERAGE token and detail — expected: every resolvable register COVERED, the 39 without a plan UNDECLARED, none INCOMPLETE. `## Cost`: median of three `walk_register_lint` runs on the largest September register (`walk-register-cycle-check-battery-2026-09-07.md`) before (`coverage_verdict` monkeypatched to return `("UNDECLARED", "stub")`) and after.
> **Headings:** `## Pins re-derived (P1, P2, P3, P6)`; `## Failing-first (the sibling and the two rewritten files red, then green)`; `## Mutation runs (three manifests)`; `## Corpus replay`; `## Cost`
> **Verbatim:** `## Corpus replay` ← P5
> **Item 10 — third commit:** the three run files and the dev-log, gated in one command on the FULL suite AND the three run files' `MUTATION:` lines, path-scoped over those four files. `numstat` over the DEV commits (`<base>..<dev>`) — exactly 16 files; `git reflog -n 8` → 0 amends, 0 resets.
>
> **Deposits:**
> - `knowledge/development/dev-log-closure-claim-and-register-coverage-2026-09-09.md`
> - `knowledge/mutants/closure-claim-cycle_check.run.txt`
> - `knowledge/mutants/register-coverage-walk_register_lint.run.txt`
> - `knowledge/mutants/register-coverage-run_check.run.txt`
>
> **Post-conditions:** all twelve sibling tests pass; the full suite passes at each of the three commits; the three run files end `MUTATION: 2 killed, 0 survived, 0 error` / `5 killed …` / `1 killed …`; the five dev-log headings present and `## Corpus replay` carries P5's cell verbatim; sixteen files over the DEV commits.

## STEP 2 — QA (full suite + both instruments on real artifacts)

> ⛔ **Re-establish the root first** — `cd "$(git rev-parse --show-toplevel)" && test -f scripts/cycle_check.py && echo TREE_OK`; interpreter `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE; prove `VENV_OK`. ⛔ **The receipt never writes an undefined `tests/…::name` id**; gate evidence quoting nodes elides the `tests/` prefix. Scratch under `/private/tmp/qa-closure-claim-register-coverage/`, never under `knowledge/`.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt 2>&1 || { echo HALT-SUITE-RED; exit 1; }`.
> **Item 2 — 213 on real plans:** `cycle_check.py` (subprocess) on `knowledge/decisions/Done/executable-432.md` → `ESCALATE:unparseable` (unchanged); on a scratch copy of `Done/executable-100009.md` (a plan `parse_block` reads as a closure CLAIM — 100049's `WARM close after walk 3` is not one, measured) with its lens lines DELETED and its `**Closing:**` line kept → `ESCALATE:claimed-close-unmet` (the new arm, on a real plan's text); on a scratch T0 plan claiming closure without a result → the same. Paste all three verdicts.
> **Item 3 — 215 on real registers:** `walk_register_lint.py` (subprocess, from the bellows root) on `<governance>/governance/knowledge/research/walk-register-gates-evidence-correspondence-2026-09-09.md` (its `Draft:` resolves to the governance drafts lane — the file is still there) → `SHAPE-OK`, `COVERAGE: COVERED` with `w1 17/17 … w9 in progress`; on `walk-register-fetch-at-claim-push-at-merge-2026-09-09.md` → COVERED with over-counts shown (`w1 11/7`); on a register whose `Draft:` names a plan renumbered into `Done/` → `UNDECLARED: plan not resolvable`; on a scratch copy of the first with its w1 rows cut to 10, run WITH `--plan <the governance draft's absolute path>` (a copy under /private/tmp has no governance ancestor to resolve the `Draft:` line against — without `--plan` it reads UNDECLARED, which is test 8a, not this) → `INCOMPLETE — w1 rows=10 declared=17`. Paste the four stderr lines verbatim.
> **Item 4 — the consumers live, read-only:** `tools/run_check.py register <that register>` → PASS with `SHAPE-OK` (the INCOMPLETE → FAIL path is proven by test 11 alone — `run_check` cannot pass `--plan` through, so the /private/tmp copy would read UNDECLARED under it; not run live); `substrate_check.py knowledge/decisions/Done/executable-100052.md` (the PLAN path — the tool resolves the register itself) → its register clause says `SHAPE-OK`; the governance hook's awk (`awk -F'\t' 'NR>1 && $4!="OK"'`) over the lint's STDOUT for the register → 0 (the column-4 contract). Paste each.
> **Item 5 — production writes, stated exactly:** none outside the two evidence files; no lane file, no lifecycle row, no import of `lifecycle`; `gates.check` never called.
> **Item 6 — receipt** `knowledge/qa/evidence/closure-claim-and-register-coverage-qa-evidence-2026-09-09.md`: numstat over the DEV commits (sixteen files; `<base>` = the parent of Item 5's commit, `<dev>` = the last DEV commit); each run file's `HEAD:` equal to `git log -1 --format=%H -- <its manifest>`; `git diff <base>..<dev> -- tests/test_substrate_check.py tests/test_cycle_check_t0_close.py tests/test_cycle_check_register_resolver.py` → EMPTY; toplevel; `git reflog -n 8` → 0 amends; the five dev-log headings grepped; Items 1–5 each on its own line; the Rule 20 block inside a `## Verification` section. ⛔ Never place a hedging keyword in a ✅ row.
> **Item 7 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt && git add knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt knowledge/qa/evidence/closure-claim-and-register-coverage-qa-evidence-2026-09-09.md && git commit -F <msg-file> -- knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt knowledge/qa/evidence/closure-claim-and-register-coverage-qa-evidence-2026-09-09.md` — exactly two files (`git show --name-only --format= HEAD`).
>
> **Deposits:**
> - `knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt`
> - `knowledge/qa/evidence/closure-claim-and-register-coverage-qa-evidence-2026-09-09.md`
>
> **Scope:**
> - `knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt`
> - `knowledge/qa/evidence/closure-claim-and-register-coverage-qa-evidence-2026-09-09.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
