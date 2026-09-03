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
**Walks:** 1 (walks 0 and 1 complete).
- Weak spots:          w1 1 folded — instruction 1 / record 0 (an arm built for a case that cannot yet occur, now fixture-declared).
- Destruction:         w1 1 folded — instruction 1 / record 0 (the warning would have printed into the daemon's stdout on every deposit evaluation).
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0 (subprocess vs import left unstated; import chosen and verified).
- Integration-record:  w1 dry — the clone origin's conventions carried; no precedent conflict found.
- ACID:                w1 dry — two steps, one verdict gate; the DEV-commit window is already guarded by plan-id-tag resolution.
**Walk 0 — context pin:** nine measurements, all in the register. The load-bearing two: the `"FAIL"` arm at `cycle_check.py:424` is **pre-wired and unreachable**, so the promotion path already exists; and the gap is demonstrated by a plan that shipped this morning — `BAR_MET` against a `NO_TABLE` register.
**Walk 0 — consumer dry-run (the execution act):** class derives `shop-infra` (holds by design); both steps' QA-ness and deposits resolve as intended; `plan_lint` returned **0 FAIL on v0's first pass**.
**⚠️ Self-application:** this plan is about enforcing register conformance, so its own register was run through the validator — via `run_check register`, not a hand-rolled sweep. It failed first pass on `headerless_rows` (fold tables written without separator rows), was fixed, and now returns **CONFORMANT**. It is written with **verbatim `pre_fold_text` captured at fold time**, which the 117 corpus rows this plan measures could not be.
**Direction verdict — PROCEED.** None of the three forcers fired: the clone origin stands (100023, shipped, on the primary target); the mechanism is intact, with walk 1 refining how the signal travels before any implementation existed; and the licensing premise was re-measured rather than recalled.
**Closing:** NOT CLOSED at walk 1 — three instruction-class findings. Phrased so it cannot match a closure claim until earned.

## Cycle Manifest

*(emitted at BAR_MET)*

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
> 6. the failure message names the actual status rather than always saying `UNCONFORMANT`
> 7. assert #2 on a plan whose register is invalid → the WARN appears and the verdict is **unchanged**
> 8. assert #2 on a plan whose register is valid → no WARN
> 9. ⚠️ **the contract test:** after the change, `cycle_check`'s last stdout line is still the bare verdict token (P8)
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — Defect A: make the validator version-aware.** Branch on the declared VALUE, not its presence. A declared version below the validator's own gets its own status; a declared version ABOVE it is also reported (the validator is too old to judge it) rather than silently mis-scored. Keep `PRE-SCHEMA` for no-declaration.
>
> **Item 4 — Defect B: correct the failure label** in `judge_register` so the message names the statuses it actually counted.
>
> **Item 5 — Defect C: assert #2 validates, warn-first.** After `resolved` is true, validate the resolved register and surface the result — ⛔ **without printing from inside the assert.**
> - ⛔ **`run_check()` contains ZERO print calls** (measured: 0 in its body; only `main()` prints, at `:669`). That silent-library property is load-bearing — **`depositor.py` imports `cycle_check` as a MODULE (`:27`) and calls `cycle_check.run_check()` in-process (`:476`), taking the returned tuple and never reading stdout.** A print inside the assert would inject a line into the DAEMON's stdout on every deposit evaluation, for every plan, forever. Return the signal instead: `check_assert_2` gains a fourth element, `run_check()` threads it through, and **`main()` prints the WARN before the verdict.** Blast radius is one line — `check_assert_2` has exactly ONE caller (`:420`) and ZERO test references.
> - ⚠️ **IMPORT the validator, do not shell out.** `walk_register_lint.validate_file(path)` returns `(status, rows, shapes)` with no printing and no CLI side effects — verified by importing it and running it on two real registers. Importing avoids a subprocess on every deposit evaluation AND avoids `sys.executable` picking the wrong interpreter, which is thread 29's open defect against `mutation_check` and the same idiom `fold_check` uses at `:97-99`.
> - ⛔ **Do not assign `"FAIL"`** (MUST-PRESERVE, P4). Record in a comment that the `:424` arm is the earned promotion path and why it is deliberately not taken here.
>
> **Item 6 — mutants** at `knowledge/mutants/register-enforcement.json`, in the shape of `checker-defects-cycle_check.json`. At least: drop the version branch → legacy registers mis-scored (killed by test 1); treat `PRE-SCHEMA` as bad (test 5); assign `"FAIL"` instead of warning → escalation returns (test 7); print the WARN after the verdict → contract broken (test 9). ⚠️ **A survivor is a missing test, stated as Critical, never a note.**
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
> **Post-conditions:** all nine tests pass; corpus re-measured with the two 0.1 files reclassified; `mutation_check` 4+ killed / 0 survived; `cycle_check`'s last stdout line unchanged in form.

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
