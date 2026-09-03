# bellows — executable: make walk-register conformance ENFORCEABLE, then enforce it warn-first (thread 103)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (three checker suites) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 103 (opened 2026-09-03); exec-100023 (Done 2026-09-02 — the clone origin: newest SHIPPED same-class plan on `cycle_check.py`, a checker-defect fix with tests); exec-392 (Done 2026-08-13 — the same-class parent for `walk_register_lint.py`, which authored schema v0.3); commit `45d7aff` (2026-09-03, a CEO-run one-liner this plan tests and completes).

## Why this exists

Nothing enforces walk-register conformance. `walk_register_lint.py` is standalone and human-invoked; `cycle_check`'s assert #2 resolves the register's path and sets `register_result = "PASS"` on **`.exists()` alone** — the assert is named *"Evidence exists"* and that is exactly, and only, what it checks.

**Measured consequence, from a plan that shipped today:** `executable-100028` reached **`BAR_MET`** while its own walk register returns **`NO_TABLE`** from the validator. A cycle can converge, close, deposit, dispatch and close again on a register no instrument can read.

The accumulated cost is measured: of 157 committed registers, **106 CONFORMANT / 25 PRE-SCHEMA / 23 UNCONFORMANT / 3 NO_TABLE**, and **117 fold rows are missing `pre_fold_text`** — the field the schema calls load-bearing. Those 117 cannot be repaired (see below). Enforcement going forward is the only remedy that exists.

## ⚠️ What this plan does NOT do, stated first

- ⛔ **It does not back-fill `pre_fold_text` anywhere.** 117 rows lack it. The field is defined as *"the exact bytes the fold replaced"*, captured **before editing** (schema rule (a), VERBATIM ALWAYS). Its own schema note records why it exists: diagnostic 337 asked whether fold records preserve the text they record and found **14 of 14 were reader reconstructions, zero verbatim**. Filling those rows now would put reconstructions into the one field created to exclude them, and nothing downstream could then separate the real from the invented. **Refused on measurement, not deferred.**
- **It does not rewrite any historical register.** In particular the two schema-`0.1` registers are NOT converted — see Defect A.
- **It does not promote the check to blocking.** Warn-first; 26 files fail today and blocking would halt every cycle carrying a historical register.
- **It does not touch `(u)`'s QA-step predicate** (thread 102) — different blast radius, its own plan.

## The three defects

**A — `walk_register_lint` is VERSION-BLIND.** It reads `schema_version` (`SCHEMA_DECL_RE`, `has_schema_declaration`) but branches only on its PRESENCE:
`pre_schema = not has_schema_declaration(text)` → `status = STATUS_PRE_SCHEMA if pre_schema else STATUS_NO_TABLE`.
A register honestly declaring `0.1` is therefore judged against v0.3's `REQUIRED_COLUMNS` and reported `NO_TABLE`. Two of the three `NO_TABLE` files are this false positive — both declare `0.1`, both carry tables in the era-correct `# | measurement | result` shape. ⛔ **They are not defects and must not be rewritten**; conforming a 0.1-era register to 0.3 would invent `pre_fold_text` for folds made a month ago.

**B — `run_check`'s failure label is now inaccurate.** Commit `45d7aff` made `judge_register` count `NO_TABLE` as bad (verified: a 1-CONFORMANT + 1-NO_TABLE sweep went `PASS/exit 0` → `FAIL/exit 1`). The message still reads `N UNCONFORMANT file(s)`. The count is right; the label is not. **That commit also ships without a test — this plan adds one.**

**C — assert #2 checks existence, not validity.** `register_result` becomes `"PASS"` at three sites, each on `.exists()`. ⚠️ **The `"FAIL"` arm is already wired at `cycle_check.py:424` (`if a2_reg in ("FAIL", "UNRESOLVED")` → `ESCALATE:assert-fail:2`) and is UNREACHABLE — `register_result` is only ever assigned `N/A`, `PASS`, or `UNRESOLVED`.** The escalation path for this defect already exists and has never fired. That makes the later promotion to blocking a one-token change, and it is why this plan can be warn-first without building a second mechanism.

## Numbers discipline

⚠️ **Measured 2026-09-03 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | targets | `scripts/walk_register_lint.py` 364 lines sha256 `19a41ab0b879`; `scripts/cycle_check.py` 674 lines `12c23a3345a8`; `tools/run_check.py` 113 lines `65f6de0a7d8e` | `shasum -a 256` |
| P2 | Defect-A anchors | the `pre_schema = …` line and the `status = … if pre_schema else …` ternary — **count-1 each** | `/usr/bin/grep -cF` → 1, 1 |
| P3 | Defect-C anchors | `register_result` assigned at `:261`, `:275`, `:285`, `:299`, `:301`; consumed once at `:420`; **no consumer outside this file** | `grep -rn register_result` |
| P4 | ⚠️ the pre-wired dead arm | `cycle_check.py:424` routes `"FAIL"` to `ESCALATE:assert-fail:2`; **nothing ever assigns `"FAIL"`** (only `N/A`/`PASS`/`UNRESOLVED`) | `/usr/bin/grep -n -F 'register_result = '` |
| P5 | the enforcement gap, demonstrated | `cycle_check` on `Done/executable-100028.md` → **BAR_MET**, while `walk_register_lint` on its register → **NO_TABLE** | both commands, same session |
| P6 | corpus distribution | 157 registers: **106 CONFORMANT / 25 PRE-SCHEMA / 23 UNCONFORMANT / 3 NO_TABLE**. ⚠️ Measured from **stderr** — the per-file verdict is on stderr by design (`run_check.py:17`); a stdout-only sweep reports everything conformant and is reading nothing | `walk_register_lint <dir> >/dev/null 2>err` |
| P7 | the un-repairable rows | of the UNCONFORMANT rows: 89 missing `pre_fold_text`, 28 missing `walk,lens,sub_question,origin,pre_fold_text`, 4 missing `sub_question` only, 347 clean | the TSV `missing` column |
| P8 | output contract | `cycle_check`'s verdict is the **LAST stdout line** (`print(verdict)`, `:669`). Any new signal prints BEFORE it or on stderr, or `run_check`'s documented channel fact breaks | read `:640-669` and `run_check.py:14-16` |
| P9 | no inherited mutant debt | `mutation_check` on `checker-defects-cycle_check.json` → **4 killed / 0 survived** at `45d7aff`. (100022's two survivors were discharged by plan 100025, `386b06f`, 2026-09-02 — a claim this Planner carried as outstanding and struck on re-measurement.) | the run in Task A |
| P10 | suite baseline | targeted: 42 pass for `run_check` + `walk_register` (`-k`); `test_cycle_check.py` and `test_walk_register_lint.py` = 27 tests each | `pytest -q` |
| P12 | the silent-library invariant | `cycle_check.run_check()` has **0** print calls; only `main()` prints (`:669`). `depositor.py` imports the module (`:27`) and calls `run_check()` in-process (`:476`) — so a print inside an assert reaches the daemon's stdout, not a consumer's parse | `grep -c 'print('` in the run_check body; read `depositor.py:27,476` |
| P13 | the validator imports cleanly | `walk_register_lint.validate_file(Path)` → `(status, rows, shapes)`, no printing, no CLI side effects; verified live on a CONFORMANT and a NO_TABLE register | the import probe in Task A |
| P16 | the gate run, not the commands | `gates.check` on a SIMULATED step 2 with deposit-shaped scratch copies → **passed=True, is_qa_step=True, 0 failures**; **negative control fires** (`qa_test_result: no parseable pytest summary`); step 1 → `is_qa_step=False` | the simulation in Step 1 Item 1 |
| P15 | ⚠️ `run_check()`'s arity is LOAD-BEARING | **43** call sites, all unpacking exactly 2 values: 3 in production — `cycle_check.py:562`, `:666`, and **`depositor.py:476` (the daemon, in-process)** — plus **40 in `tests/test_cycle_check.py`**, every one `verdict, code = cycle_check.run_check(plan)`. A 3-tuple raises `ValueError: too many values to unpack (expected 2)` — a production break. Use an optional collector kwarg | `/usr/bin/grep -n -F 'run_check('` across the three files |
| P14 | assert-2 blast radius | `check_assert_2` has **1** caller (`:420`) and **0** test references — the 4-tuple change touches one line | `grep -rn check_assert_2` |
| P11 | no in-flight collision | `lifecycle.db` → zero plans in `claimed`/`in_progress`/`awaiting_verdict` | `sqlite3` query |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **The verdict stays the LAST stdout line** (P8). A register WARN prints before it or on stderr. Prove it: after the change, `cycle_check <plan> | tail -1` must still be the bare verdict token.
- ⚠️ **Do NOT assign `"FAIL"` to `register_result` in this plan.** The arm at `:424` is live and would escalate immediately on 26 corpus files. Warn-first; the promotion is a later plan earned on a re-measured funnel.
- ⚠️ **Do not rewrite any register.** Not the two 0.1 files, not the 4 `sub_q` rows, not the 117 missing `pre_fold_text`. This plan changes instruments, never records.
- ⚠️ **`PRE-SCHEMA` is not a defect** — 25 registers legitimately predate the declaration. Neither the validator's new branch nor `judge_register` may treat it as bad.
- ⚠️ **The worktree has no `.venv`** — bind the canonical interpreter absolutely: `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`, as plans 100022/100026/100027/100028 all do. A relative `.venv/bin/python` is dead from the dispatch cwd.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**
- ⚠️ **Read the verdict channel from stderr** when sweeping the corpus (P6). A stdout-only sweep is the measured MISREAD that produced a false "157 conformant / 0 NO_TABLE" in this plan's own authoring session.

## Drafting Cycle

**Tier:** T1 — triggers fired: T-1 (three subsystems) and T-3 (the checkers run on every machine that deposits). T-6 assessed and NOT fired: conformance instruments, not the ten step gates — the ruling 473/474, 100022 and 100023 all took. T-8 not fired: clone by kind of exec-100023.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-register-enforcement-2026-09-03.md`
**Walks:** 7 (walks 0–7 complete).
- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry; w6 dry; w7 dry.
- Destruction:         w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w4 dry; w5 1 folded — instruction 1 / record 0; w6 1 folded — instruction 1 / record 0; w7 dry.
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 1 folded — instruction 1 / record 0; w5 dry; w6 dry; w7 dry.
- Integration-record:  w1 dry; w2 dry; w3 dry; w4 1 folded — instruction 1 / record 0 (the gate-run mandate the plan owed its agent); w5 dry; w6 dry; w7 dry.
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry; w7 dry — two steps, one verdict gate, the DEV-commit window guarded by plan-id-tag resolution throughout.
- Record sweep:        w0 1 folded (instruction); w5 2 folded (record); w7 dry.
**Per-walk yields:** w0 1 · w1 3 · w2 1 · w3 2 · w4 2 · w5 3 · w6 1 · w7 0. **Total 13 — instruction 11 / record 2; 8 of 13 fold-introduced.**
**Walk 0 — context pin:** nine measurements, all in the register. The load-bearing two: the `"FAIL"` arm at `cycle_check.py:424` is **pre-wired and unreachable**, so the promotion to blocking already exists as machinery; and the gap is demonstrated by a plan that shipped this morning — `BAR_MET` against a `NO_TABLE` register.
**Walk 0 — consumer dry-run (the execution act):** class derives `shop-infra` (holds by design); both steps' QA-ness and deposits resolve as intended; `plan_lint` returned **0 FAIL on v0's first pass**.
**Walk 4 — EXECUTION pass:** `gates.check` on a simulated step 2 → passed/0 with a **firing negative control** and step 1 `is_qa=False`. It found no defect in the artifact and one in the plan's instructions.
**⚠️ Self-application:** this plan is about enforcing register conformance, so its own register was run through the validator — via `run_check register`, the sanctioned checker, not a hand-rolled sweep. It FAILED first pass on `headerless_rows`, was fixed, and is **CONFORMANT**, carrying **verbatim `pre_fold_text` captured at fold time** — the field 117 corpus rows are missing and cannot get back.
**⚠️ The cycle's own shape:** 8 of 13 findings were this cycle's own fold damage, and three of them were the SAME defect one layer out — w1 measured `check_assert_2`'s blast radius then changed `run_check()` without measuring it; w2 froze the arity on 3 callers and missed 40 tests; w5 introduced a status without ruling how the judge reads it, which is the very defect the plan fixes. **The recurring error was measuring the thing below the thing being changed.**
**Auto-advance:** walks 2–7 ran self-driving per §2's cadence — substrate present (register CONFORMANT, reference line committed, per-walk commits, `fold_check` baseline), `cycle_check` CONTINUE at every walk, no direction-class finding. The previous cycle could not auto-advance because its own register did not validate; this one could, and did.
**Direction verdict — PROCEED.** None of the three forcers fired: the clone origin stands (100023, shipped, on the primary target); the mechanism is intact, with walk 1 refining how the signal travels before any implementation existed; and the licensing premise was re-measured rather than recalled.
**Closing:** w7 met the bar — **instruction 0 / record 0**, a fully dry full-lens pass: counts reconcile (11 tests declared and claimed; 16 pins defined and 16 cited; both Scope blocks match their numstat claims) and every command the final fold set touched was RE-RUN and executes. Walk 7 restructured nothing, so the convergence clock did not reset. The mandatory closing-record re-read was run and produced one record fold — this log's own walk count, which had lagged at 1 while seven walks ran. ⚠️ **Two counts appear in this record and they differ for a stated reason:** the prose total is **13 findings**, the manifest's machine-derived `yields:` sums to 11. The emitter reads per-LENS lines; walk 5's two record-decay findings sit on a `Record sweep` line, which §3 asks be counted separately from artifact findings and which the emitter therefore cannot parse. The manifest carries the emitter's number verbatim; this sentence is the reconciliation, so a later reader meets both rather than picking one. **`propagation_check=DIVERGENT:22` is declared as emitted and all 22 rows were classified before the close** — every one the numeral-in-string class (pin values that are line numbers 424/476/562/666/420 or plan ids 100028/100022, matched against the same numerals in ordinary prose). Zero real restatement divergences; thread 96's rider, carried in `open_forks`. ⚠️ **FROZEN, NOT DEPOSITED:** deposit authority for this plan has not been given.

## Cycle Manifest
tier: T1
target: scripts/walk_register_lint.py
target_class: detector
state_space: declared-schema-version (absent / below-validator / equal / above-validator) x table-shape (conformant / wrong-shape / headerless / none) x judge-classification (good / bad / neither) — every dimension read from SYSTEM artifacts over the 157 committed registers, never from the author's model: the version axis from the corpus's own declarations (25 carry none, 2 declare 0.1, the rest 0.3), the shape axis from the validator's `missing`/`note` columns over 23 UNCONFORMANT files (89 rows missing `pre_fold_text`, 28 missing five columns, 4 missing `sub_question`, 347 clean), and the judge axis measured directly against `judge_register`'s real substring predicate on eight candidate status names. Cells enumerated as tests 1, 1b, 2-5, 5b, 6-9 in STEP 1 Item 2, including the positive control (test 8, a valid register stays silent) and the arity CONTROL mutant
mutants: knowledge/mutants/register-enforcement.json
class: shop-infra
reads: scripts/walk_register_lint.py, scripts/cycle_check.py, tools/run_check.py, depositor.py, scripts/fold_check.py, tests/test_cycle_check.py, tests/test_walk_register_lint.py, tests/test_run_check.py, knowledge/architecture/walk-register-schema.md, knowledge/mutants/checker-defects-cycle_check.json
writes: scripts/walk_register_lint.py, scripts/cycle_check.py, tools/run_check.py, tests/test_walk_register_lint.py, tests/test_cycle_check.py, tests/test_run_check.py, knowledge/mutants/register-enforcement.json, knowledge/dev-logs/register-enforcement-dev-2026-09-03.md
open_forks: promoting the register check from WARN to the pre-wired `"FAIL"` arm at `cycle_check.py:424` — earned on a re-measured funnel, a later plan; the 117 fold rows missing `pre_fold_text`, refused for back-fill on measurement and closable only going forward; the 23 UNCONFORMANT and 3 NO_TABLE files, left as records and not rewritten; `(u)`'s QA-step predicate wrong on 74 of 861 steps (thread 102, its own plan); the `propagation_check` numeral-in-string class — thread 96's rider, and the whole of this plan's DIVERGENT count
walks: 7
yields: 3, 1, 2, 2, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:22
coherence: 7/7 walks have register rows

## STEP 1 — DEV (three instruments, their tests, and the mutants)

> **Scope:**
> - `scripts/walk_register_lint.py`
> - `scripts/cycle_check.py`
> - `tools/run_check.py`
> - `tests/test_walk_register_lint.py`
> - `tests/test_cycle_check.py`
> - `tests/test_run_check.py`
> - `knowledge/mutants/register-enforcement.json`
> - `knowledge/dev-logs/register-enforcement-dev-2026-09-03.md`
>
> **Item 1 — re-derive P1, P2, P3, P4, P5, P9, P10 and HALT on mismatch.** P5 is the plan's justification and must be reproduced as two commands whose answers disagree: `cycle_check` on `Done/executable-100028.md` → `BAR_MET`, and `walk_register_lint` on `governance/knowledge/research/walk-register-qa-predeclaration-2026-09-03.md` → `NO_TABLE` **read from stderr**. ⛔ If they now agree, the premise is gone — HALT and request a verdict.
>
> **Item 2 — write the failing tests FIRST.** Pinned modules, no branch: extend `tests/test_walk_register_lint.py`, `tests/test_cycle_check.py`, `tests/test_run_check.py` (all three exist; this is not a new-module case, unlike exec-576's). Tests:
> 1. a register declaring `0.1` with an era-correct table → **not** `NO_TABLE`; reported as its own legacy status
> 1b. ⚠️ a register declaring a version ABOVE the validator's → reported as unjudgeable, **from a CONSTRUCTED fixture**: no register in the corpus declares >0.3 today, so this arm is built for a case that cannot yet occur. Say so in the test's docstring rather than implying it was found in the wild.
> 2. a register declaring `0.3` with a wrong-shaped table → still `NO_TABLE`/`UNCONFORMANT` as today
> 3. a register with **no** declaration → still `PRE-SCHEMA` (unchanged)
> 4. `judge_register` counts a `NO_TABLE` line as bad (the test commit `45d7aff` shipped without)
> 5. `judge_register` does **not** count `PRE-SCHEMA` as bad
> 5b. ⛔ **`judge_register` treats the NEW legacy status explicitly** — not by omission. `judge_register` matches `\tUNCONFORMANT`, `\tNO_TABLE` and `\tCONFORMANT` as substrings; a status matching none of them is invisible to the judge, **which is precisely the defect this plan exists to fix**. Introducing a status without deciding its judge treatment would create the next instance of it. Ruled here: a legacy-schema register is **not bad** (it is honest, not defective) and **not good** (nothing was validated against the current schema), so it must not satisfy the positive control on its own — a sweep containing only legacy registers still FAILs with 'nothing was scanned'. Test both arms.
> 6. the failure message names the actual status rather than always saying `UNCONFORMANT`
> 7. assert #2 on a plan whose register is invalid → the WARN appears and the verdict is **unchanged**
> 8. assert #2 on a plan whose register is valid → no WARN
> 9. ⚠️ **the contract test:** after the change, `cycle_check`'s last stdout line is still the bare verdict token (P8)
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — Defect A: make the validator version-aware.** Branch on the declared VALUE, not its presence.
> - ⛔ **The new status's NAME is load-bearing and must not begin with `CONFORMANT` or `NO_TABLE`.** `judge_register` classifies by tab-prefixed substring, so the name silently decides the semantics. Measured: `CONFORMANT_LEGACY` → counted **good** (a legacy register would satisfy the positive control on its own); `NO_TABLE_LEGACY` → counted **bad** (a legacy register would fail the sweep); `LEGACY_SCHEMA` → neither, which is w5-3's ruled behaviour. Pick a name that classifies as neither, and pin the choice with test 5b rather than leaving it to whoever types the constant. A declared version below the validator's own gets its own status; a declared version ABOVE it is also reported (the validator is too old to judge it) rather than silently mis-scored. Keep `PRE-SCHEMA` for no-declaration.
>
> **Item 4 — Defect B: correct the failure label** in `judge_register` so the message names the statuses it actually counted.
>
> **Item 5 — Defect C: assert #2 validates, warn-first.** After `resolved` is true, validate the resolved register and surface the result — ⛔ **without printing from inside the assert.**
> - ⛔ **`run_check()` contains ZERO print calls** (measured: 0 in its body; only `main()` prints, at `:669`). That silent-library property is load-bearing — **`depositor.py` imports `cycle_check` as a MODULE (`:27`) and calls `cycle_check.run_check()` in-process (`:476`), taking the returned tuple and never reading stdout.** A print inside the assert would inject a line into the DAEMON's stdout on every deposit evaluation, for every plan, forever. Return the signal instead: `check_assert_2` gains a fourth element and **`main()` prints the WARN before the verdict.** `check_assert_2` has exactly ONE caller (`:420`) and ZERO test references. ⛔ **But `run_check()`'s OWN arity must NOT change.** It has THREE callers, every one unpacking exactly two values — `cycle_check.py:562`, `cycle_check.py:666`, and **`depositor.py:476`, which is the daemon**. A third return element raises `ValueError: too many values to unpack (expected 2)` and breaks every deposit evaluation. Thread the signal through an **optional collector kwarg** instead — `run_check(plan_path, warnings=None)`, appended to when supplied — so all 43 existing call sites are byte-for-byte unaffected and only `main()`'s verdict path passes a list. ⚠️ **Do NOT pass a collector on the `--emit-manifest` path** (`:562`): it calls `run_check` only to fill the manifest's `validation:` field, which records checker verdicts and not warnings. Emitting a register WARN during manifest emission would put advisory text into an artifact the depositor cross-checks. *(Walk 1 measured the inner function's blast radius and then proposed changing the outer one without measuring it. Measure the function you are actually changing.)*
> - ⚠️ **IMPORT the validator, do not shell out.** `walk_register_lint.validate_file(path)` returns `(status, rows, shapes)` with no printing and no CLI side effects — verified by importing it and running it on two real registers. Importing avoids a subprocess on every deposit evaluation AND avoids `sys.executable` picking the wrong interpreter, which is thread 29's open defect against `mutation_check` and the same idiom `fold_check` uses at `:97-99`.
> - ⛔ **Do not assign `"FAIL"`** (MUST-PRESERVE, P4). Record in a comment that the `:424` arm is the earned promotion path and why it is deliberately not taken here.
>
> **Item 6 — mutants** at `knowledge/mutants/register-enforcement.json`, in the shape of `checker-defects-cycle_check.json`. At least: drop the version branch → legacy registers mis-scored (killed by test 1); treat `PRE-SCHEMA` as bad (test 5); assign `"FAIL"` instead of warning → escalation returns (test 7); print the WARN after the verdict → contract broken (test 9). ⚠️ **Add a fifth, as a CONTROL:** change `run_check()`'s return to a 3-tuple → must be **killed by the EXISTING suite**, not by a new test, because 40 sites in `tests/test_cycle_check.py` unpack two values. This mutant exists to prove that guard is real rather than assumed — **if it survives, the arity is unprotected and P15's entire design rests on nothing.** ⚠️ **A survivor is a missing test, stated as Critical, never a note.**
>
> **Item 7 — re-measure the corpus distribution** (P6) post-change, reading stderr, and state the delta. Expect the two `0.1` files to move out of `NO_TABLE`. **Report your numbers; only a class change is a HALT.**
>
> **Item 8 — commit** (message tagged with the plan id); record `numstat` — exactly 8 files.
>
> **Deposits:**
> - `knowledge/dev-logs/register-enforcement-dev-2026-09-03.md`
> - `knowledge/mutants/register-enforcement.json`
>
> ⚠️ **On the QA gate:** this step is not a QA step.
>
> **Post-conditions:** all eleven tests pass (1, 1b, 2–5, 5b, 6–9); corpus re-measured with the two 0.1 files reclassified; `mutation_check` 5 killed / 0 survived (the four defect mutants plus the arity CONTROL); `cycle_check`'s last stdout line unchanged in form.

## STEP 2 — QA (full suite + the instruments run against the REAL corpus)

> **Scope:**
> - `knowledge/qa/evidence/register-enforcement-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/register-enforcement-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/register-enforcement-2026-09-03/pytest_full.txt`
>
> **Item 1 — full suite from a WORKTREE:**
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> mkdir -p knowledge/qa/evidence/register-enforcement-2026-09-03
> "$BPY" -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/register-enforcement-2026-09-03/pytest_full.txt
> ```
>
> Derive the count from P10 plus your additions and state the arithmetic. Confirm with `pwd` that you are in a worktree and that no repo-root config file is present.
>
> **Item 2 — the instruments against the REAL corpus**, raw tails to the evidence file:
> 1. the corpus distribution, **read from stderr**, before/after the change — the two `0.1` files must leave `NO_TABLE`
> 2. `run_check register` over the corpus → still FAIL naming the genuine failures, and the message now names the right statuses
> 3. the enforcement gap CLOSED: `cycle_check` on `Done/executable-100028.md` now emits the register WARN, and its verdict is still `BAR_MET` (warn-first — a changed verdict here is a FAILURE of this plan, not a success)
> 4. **the contract holds:** `cycle_check <plan> | tail -1` is the bare verdict token
> 5. ⚠️ **the negative control:** a plan whose register is VALID emits no WARN. A check that fires on everything is not a check — show it staying silent.
>
> **Item 3 — `mutation_check`** on the new manifest; paste the kill map.
>
> **Item 4 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; the re-measured distribution stated plainly; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> **Item 5 — commit the evidence** (message tagged with the plan id); verify exactly 3 files.
>
> ⚠️ **On the QA gate:** this plan has a real test scope. Item 1 produces the pytest summary the gate parses; no override clause applies here, and none should be copied from this step.
>
> **Deposits:**
> - `knowledge/qa/evidence/register-enforcement-2026-09-03/pytest_full.txt`
> - `knowledge/qa/evidence/register-enforcement-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/register-enforcement-2026-09-03/qa-receipt.md`
>
> **Post-conditions:** suite green at the derived count; the two 0.1 files reclassified; the WARN fires on 100028's register and stays silent on a valid one; the verdict token unchanged; kill map clean.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
