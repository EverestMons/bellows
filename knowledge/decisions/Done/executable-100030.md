# bellows — executable: validate BEFORE exempting — restore the 415 fold rows and 15 registers plan 100029 removed from coverage (thread 103, corrective)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the validator suite) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** plan **100029** (HALTED at step 1 today; its code is on main and this plan corrects it — the halt verdict specifies this follow-up); exec-100025 (Done 2026-09-02 — the clone origin: a corrective plan that closed a kill-map gap, and the plan that discharged 100022's two survivors); thread 103; thread 97 (`mutation_check` takes ONE target per manifest — not blocking here, only the reason for the split).

## Why this exists

Plan 100029 made `walk_register_lint` version-aware and, in doing so, **removed validation coverage instead of adding it.** The defect is a short-circuit placed BEFORE validation:

```
declared_version = _extract_schema_version(text)
if declared_version is not None:
    cmp = (...)
    if cmp[0] < cmp[1]:
        return STATUS_LEGACY_SCHEMA, [], []      # <- exits before validating, rows EMPTY
    if cmp[0] > cmp[1]:
        return STATUS_FUTURE_SCHEMA, [], []
```

A register whose header declares `0.1` or `0.2` is exempted **whether or not its table conforms** — and it returns empty `rows`, so it vanishes from the TSV stream as well.

**Two measured harms:**

| | before 100029 | after 100029 |
|---|---|---|
| CONFORMANT registers | **106** | **91** |
| fold rows on stdout, corpus-wide | **2827** | **2412** |

**15 previously-conformant registers are now exempted, and 415 fold rows left the machine-readable stream** — the stream the drafting-stage pricing diagnostic reads, whose control population was already only 2. Sampled three of the 28 now-`LEGACY_SCHEMA` files: two carry the EXACT v0.3 column shape (`| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |`) while declaring an older version in the header. They would pass if validated.

⚠️ **The root cause is a plan-text under-specification, not an implementation error.** 100029's Item 3 said *"branch on the declared VALUE, not its presence"* and never said validation must still be ATTEMPTED. The agent implemented the letter of it exactly.

## What this plan does NOT do

- **It does not revert 100029.** Its collector kwarg, both status names, the judge ruling and mutants M3/M4/M5 are all correct and stay. Only the short-circuit's PLACEMENT changes.
- **It does not back-fill `pre_fold_text`** anywhere, and does not rewrite any register.
- **It does not promote the check to blocking** — warn-first stands.
- **It does not fix thread 97.** `mutation_check` still takes one target per manifest; this plan works within that by shipping three manifests.
- ⚠️ **It does not edit 100029's records.** Deleting `knowledge/mutants/register-enforcement.json` leaves `halted-executable-100029.md` (five references) and its dev-log describing a path that no longer exists. Those are a halted plan's historical account of what it built; **strike, never tidy** — this sentence is the disclosure, and the manifests' new names carry the same slug so a reader can follow them.

## Numbers discipline

⚠️ **Measured 2026-09-03 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | target | `scripts/walk_register_lint.py` **393 lines**, sha256 `3188f3386539` | `shasum -a 256` |
| P2 | the defect anchor | `return STATUS_LEGACY_SCHEMA, [], []` — **count-1**, inside `validate_file`'s pre-validation short-circuit | `/usr/bin/grep -cF` → 1 |
| P3 | ⚠️ coverage loss | CONFORMANT **106 → 91**; 28 registers now `LEGACY_SCHEMA`, of which 12 declare `0.1` and 8 declare `0.2` | corpus sweep, **stderr** |
| P4 | ⚠️ stream loss | fold rows on stdout **2827 → 2412 = 415 lost**. Measured by running the pre-change code (`7349c89`) and HEAD over the same directory | two worktree runs |
| P5 | the exempted are conformant | a `LEGACY_SCHEMA` file carrying the exact v0.3 header emits **0** fold rows and is never validated | run the validator on `walk-register-classify-307-318-2026-08-11.md` |
| P6 | manifest split needed | `knowledge/mutants/register-enforcement.json` declares ONE `target`, but M1's anchor lives in `walk_register_lint.py` and M2's in `run_check.py`; both reported `anchor matched 0 times`. **3 killed / 0 survived / 2 ERROR** | `mutation_check` on the current manifest |
| P7 | ⚠️ a KNOWN failure, not a regression | `tests/test_gates_cross_machine_paths.py::test_relative_path_unchanged` FAILS in the canonical checkout and PASSES from a worktree at the same commit (1 failed vs 6 passed). It is the CWD-`config.json` trap. Measured whole-suite in both places: **worktree `1834 passed, 1 skipped` (0 failed)** vs canonical `1 failed, 1834 passed`. The daemon dispatches into `.bellows-worktrees/<slug>` (`bellows.py:1553`), so **`known_failures: 0` is the correct declaration** | run the suite in both locations |
| P8 | in-flight | zero plans `claimed`/`in_progress`/`awaiting_verdict` | `sqlite3` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⛔ **VALIDATE FIRST, EXEMPT SECOND.** The version comparison may only change a status that validation has already produced. A register that CONFORMS keeps `CONFORMANT` regardless of the version it declares. This is the whole plan; an implementation that short-circuits again has not done it.
- ⛔ **`rows` must never be returned empty on the exemption path.** The TSV stream is a consumer (the pricing diagnostic reads fold rows). Whatever status a register ends with, its parsed rows still travel.
- ⚠️ **Do not change `run_check()`'s arity** — 43 call sites unpack two values, 40 of them in `tests/test_cycle_check.py`. 100029's collector kwarg is correct and stays.
- ⚠️ **Do not rename `LEGACY_SCHEMA` or `FUTURE_SCHEMA`** — they are correctly chosen so `judge_register`'s tab-prefixed substring split classifies them as neither good nor bad. A name beginning with `CONFORMANT` or `NO_TABLE` silently changes the semantics.
- ⚠️ **THREE manifests, one per target file** — `mutation_check` takes a single `target` each (thread 97). A five-mutant manifest spanning three files reports `ERROR — anchor matched 0 times` and verifies nothing.
- ⛔ **`known_failures: 0`, deliberately — do NOT raise it.** An earlier revision declared `1` to cover the CWD-`config.json` test: an allowance for a failure that CANNOT occur in the dispatch location, since the daemon runs steps in `.bellows-worktrees/<slug>` where the suite is `1834 passed, 1 skipped`. **A pre-declared override for a location-bound failure measured in the wrong location is a recorded Planner failure** — three prior plans carried exactly this — and it recurred here inside a plan whose own P7 warns about it. Any failure from the worktree is real — HALT.
- ⚠️ **Worktree dispatch; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` bound absolutely; every claim cites file:line; EVERY DATE IS A FIXED LITERAL.**

## Drafting Cycle

**Tier:** T1 — triggers fired: T-3 (the validator runs on every machine that deposits). T-8 not fired: corrective clone by kind of exec-100025. T-6 not claimed: a conformance instrument, not a step gate.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-register-validate-first-2026-09-03.md`
**Walks:** 7 (walks 0–7 complete).
- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry; w6 dry; w7 dry.
- Destruction:         w1 1 folded — instruction 0 / record 1; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry; w7 dry.
- Vulnerabilities:     w1 dry; w2 dry; w3 dry; w4 1 folded — instruction 1 / record 0; w5 dry; w6 dry; w7 dry.
- Integration-record:  w1 dry; w2 dry; w3 dry; w4 1 folded — instruction 1 / record 0; w5 dry; w6 dry; w7 dry.
- ACID:                w1 dry; w2 1 folded — instruction 1 / record 0; w3 dry; w4 dry; w5 dry; w6 1 folded — instruction 1 / record 0; w7 dry.
- Record sweep:        w5 1 folded — instruction 0 / record 1; w7 1 folded — instruction 0 / record 1.
**Per-lens detail** (kept out of the machine-read lines above, which the emitter parses): w3 a self-confirming post-condition; w4 the oracle built inside the daemon's worktree dir, and an unmeasured empty-set claim; w2 absolute counts against a growing corpus; w6 step 1 failing its own scope gate; w5/w7 an incomplete fold and a count lag.
**Per-walk yields:** w0 0 · w1 2 · w2 1 · w3 1 · w4 2 · w5 1 · w6 1 · w7 1. **Total 9 — instruction 6 / record 3; 5 of 9 fold-introduced.**
**Walk 0 — context pin:** nine measurements. The two load-bearing: CONFORMANT **106 → 91** and fold rows **2827 → 2412 (415 lost)**, both reproduced against the pre-change commit `7349c89`.
**⚠️ The two findings that were NOT this cycle's own fold damage are the two that would have cost most:** `known_failures: 1`, a recorded Planner failure recurring inside a plan whose own pin warns about it; and an unnamed file deletion that `_gate_scope_check` would have rejected, failing step 1's gate. **Both were caught by asking what a CONSUMER would do — the gate, the dispatch location — not by re-reading the prose.**
**Auto-advance:** walks 2–7 ran self-driving per §2's cadence — substrate present, `cycle_check` CONTINUE at every walk, no direction-class finding.
**Closing:** w7 met the bar — **instruction 0 / record 1**, the record fold being this cycle's own numstat lag from w6-1. Counts reconcile (7 tests declared and claimed; 8 pins defined and cited; Scope 7 entries against Item 7's 7-file claim) and every command the final fold set touched was re-run and executes. Walk 7 restructured nothing, so the convergence clock did not reset. The closing-record re-read was run and produced the record fold above. ⚠️ **`propagation_check=DIVERGENT:11` declared as emitted, all 11 rows classified before the close** — every one the numeral-in-string class: the harm figures this plan is ABOUT (415, 2827, 2412, 106, 91, 28) matched against the same numerals in the prose that explains them. Zero real restatement divergences; thread 96's rider, carried in `open_forks`. ⚠️ **A record fold worth naming:** expanding the lens lines' en-dash ranges for machine-legibility stripped the `— instruction N / record N` annotations the emitter reads, and `yields:` went to `N/A`. My first diagnosis blamed the en-dashes; reading `get_instruction_counts` showed it reads the annotations. Restored, and `yields` now derives to `1, 1, 1, 2, 0, 1, 0` — six instruction findings, matching the prose. ⚠️ **FROZEN, NOT DEPOSITED** pending the CEO's go.

## Cycle Manifest
tier: T1
target: scripts/walk_register_lint.py
target_class: detector
state_space: declared-version (absent / below / equal / above the validator's) x table-validity under pure v0.3 rules (conforms / fails / no table) x resulting status (CONFORMANT / LEGACY_SCHEMA / FUTURE_SCHEMA / UNCONFORMANT / NO_TABLE / PRE-SCHEMA) — every dimension read from SYSTEM artifacts over the 159 committed registers, never the author's model: the version axis from the corpus's own declarations (25 none, 12 declare 0.1, 8 declare 0.2), the validity axis from an INDEPENDENT oracle (the pre-branch validator at 7349c89, which has zero LEGACY_SCHEMA references), and the interaction measured as the 16-register disagreement set the fix must empty. Cells enumerated as tests 1-7 in STEP 1 Item 2, including the positive control (test 6, a conformant v0.3 register unchanged) and test 7 (rows never empty on the exemption path)
mutants: knowledge/mutants/register-enforcement-wrl.json
class: shop-infra
reads: scripts/walk_register_lint.py, scripts/cycle_check.py, tools/run_check.py, gates.py, tests/test_walk_register_lint.py, tests/test_cycle_check.py, knowledge/mutants/register-enforcement.json, knowledge/decisions/halted-executable-100029.md
writes: scripts/walk_register_lint.py, tests/test_walk_register_lint.py, knowledge/mutants/register-enforcement.json, knowledge/mutants/register-enforcement-wrl.json, knowledge/mutants/register-enforcement-cycle_check.json, knowledge/mutants/register-enforcement-run_check.json, knowledge/dev-logs/register-validate-first-dev-2026-09-03.md
open_forks: promoting the register check from WARN to the pre-wired "FAIL" arm at cycle_check.py:424 — earned on a re-measured funnel, a later plan; thread 97, mutation_check's single-target-per-manifest limit, worked around here with three manifests rather than fixed; the 117 fold rows missing pre_fold_text, refused for back-fill and closable only going forward; (u)'s QA-step predicate wrong on 74 of 861 steps (thread 102); the propagation_check numeral-in-string class (thread 96) — the whole of this plan's DIVERGENT count
walks: 7
yields: 1, 1, 1, 2, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:11
coherence: 7/7 walks have register rows

## STEP 1 — DEV (move the exemption after validation; split the manifests)

> **Scope:**
> - `scripts/walk_register_lint.py`
> - `tests/test_walk_register_lint.py`
> - `knowledge/mutants/register-enforcement.json` (DELETED — see Item 4)
> - `knowledge/mutants/register-enforcement-wrl.json`
> - `knowledge/mutants/register-enforcement-cycle_check.json`
> - `knowledge/mutants/register-enforcement-run_check.json`
> - `knowledge/dev-logs/register-validate-first-dev-2026-09-03.md`
>
> **Item 1 — re-derive P1–P6 and HALT on mismatch.** P3 and P4 are the plan's justification and must be reproduced as two numbers that disagree with the pre-change code: run the corpus sweep at HEAD and at `7349c89` (a worktree at that commit) and state CONFORMANT and stdout-row counts for both. ⛔ If HEAD already matches the pre-change numbers, the defect is gone — HALT and request a verdict.
>
> ⚠️ **Then run the GATE, not just the commands** — `gates.check` on a simulated step 2 with deposit-shaped scratch copies, the receipt dict constructed as `{"receipt_status":"Complete","ceo_flags":[],"is_error":False,"permission_denials":[],"result_text":"### Files Deposited\n- <the three step-2 paths>\n"}`, expecting `passed=True`, `is_qa_step=True`, 0 failures — **then strip the summary line and confirm `qa_test_result` fails.** ⛔ A control that does not fire means the simulation is inert — HALT.
>
> **Item 2 — write the failing tests FIRST**, in `tests/test_walk_register_lint.py`:
> 1. ⛔ **the case 100029 missed:** a register declaring `0.1` whose fold table IS v0.3-conformant → stays **`CONFORMANT`**, and its rows are emitted. This is the regression this plan exists for.
> 2. a register declaring `0.1` whose table is wrong-shaped → `LEGACY_SCHEMA` (an old declaration explains a failure; it does not excuse a passing one)
> 3. a register declaring `0.1` with no fold table at all → `LEGACY_SCHEMA`, not `NO_TABLE`
> 4. a register declaring a FUTURE version whose table conforms → still reports its rows; the status flags unjudgeability without discarding data
> 5. `PRE-SCHEMA` (no declaration) unchanged
> 6. a conformant v0.3 register unchanged — the positive control
> 7. ⛔ **rows are never empty on the exemption path:** whatever status results, a register with parseable fold rows emits them
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — move the exemption after validation.** Validate first; then, if the declared version differs from the validator's, adjust the STATUS only. A conformant register keeps `CONFORMANT`. A failing register with an older declaration becomes `LEGACY_SCHEMA`. A newer declaration becomes `FUTURE_SCHEMA`. **In every case the parsed `rows` are returned.** Keep the count-1 anchor of P2 as the edit site.
>
> **Item 4 — split the mutants manifest into three**, one `target` each: `walk_register_lint.py`, `cycle_check.py`, `run_check.py`. Carry 100029's M3/M4/M5 into the `cycle_check` manifest unchanged (all three KILLED and stay killed), re-home M1 and M2 to their real files, and add a sixth: **revert the exemption to a pre-validation short-circuit** → killed by test 1. **Delete `knowledge/mutants/register-enforcement.json`** — named here in full deliberately: `_gate_scope_check` clears a changed file when its path or basename appears in the step text (`gates.py:932`), and a deletion the step never names is judged out-of-scope and FAILS the gate. Measured on an earlier revision of this plan: step 1's text contained neither the path nor the basename.
>
> **Item 5 — re-measure P3 and P4 as a BEFORE/AFTER pair over the SAME corpus, in the same run.** ⛔ **Do not compare against the authoring pins** — the corpus grows as plans close, and these pins were measured while this very session was adding registers to it: 2412 → 2414 rows and 91 → 92 CONFORMANT drifted within minutes of being written. Absolute counts cannot survive to dispatch.
>
> The post-condition is therefore **invariant to corpus size**, and it is the discriminating property:
> - ⛔ **ZERO registers whose fold table CONFORMS may be reported `LEGACY_SCHEMA` or `FUTURE_SCHEMA`** — and the check must use an INDEPENDENT oracle, not the code under test. After the fix, exempted-equals-failed holds *by construction*, so asking the new code whether its own exempted set genuinely fails is self-confirming and proves nothing. **Use the pre-change validator as the oracle.** ⚠️ **Extract it, do not create a worktree** — `walk_register_lint.py` has NO location dependency (no `__file__`, no `SCRIPTS_DIR`), so `git show 7349c89:scripts/walk_register_lint.py > "$TMPDIR/oracle.py"` and running that copy works standalone; **do NOT `git worktree add` under `.bellows-worktrees/`, which the daemon owns and reaps.** Run the oracle over the same directory, and require that **every register the new code exempts was `UNCONFORMANT` or `NO_TABLE` under the old code.** The old code had no version branch at all, so its verdict is a pure v0.3 judgement — exactly the second opinion this check needs. Any register the old code called `CONFORMANT` and the new code exempts is the short-circuit surviving.
> - ⛔ **The post-condition, stated as a SET and measured today: that set currently holds 16 registers, and after the fix it must be EMPTY.** Measured 2026-09-03 over 159 registers — oracle 108 CONFORMANT / 25 PRE-SCHEMA / 23 UNCONFORMANT / 3 NO_TABLE against the shipped code's 92 / 28 LEGACY_SCHEMA / 25 / 13 / 1 — the difference is exactly **16 registers the oracle calls CONFORMANT that the new code exempts, all 16 into `LEGACY_SCHEMA`**, among them `walk-register-classify-307-318-2026-08-11.md`, `walk-register-cycle-classify-s40sweep-2026-08-13.md` and `walk-register-cycle-run-339-2026-08-10.md`. **This is the plan's only hard post-condition and it is invariant to corpus growth**: the set is defined by disagreement between two validators over the same files, not by any count.
> - **CONFORMANT must RISE and fold rows must RISE**, measured before and after your own edit against the identical directory in the same run. State both numbers and the delta; the authoring figures (106→91, 2827→2412 = 415 lost) are context for the size of the harm, not a target to hit.
> - A CONFORMANT count that does not rise, or rows that do not rise, means coverage is still lost — HALT.
>
> **Item 6 — run `mutation_check` on all three manifests.** ⛔ **0 ERROR is required, not just 0 survived.** An ERROR means a mutant never ran and verifies nothing — the failure mode that halted 100029.
>
> **Item 7 — commit** (message tagged with the plan id); record `numstat` — **exactly 7 files**: two modified (`walk_register_lint.py`, its test module), one DELETED (the old single manifest), and four added (three manifests + the dev log).
>
> **Deposits:**
> - `knowledge/dev-logs/register-validate-first-dev-2026-09-03.md`
> - `knowledge/mutants/register-enforcement-wrl.json`
>
> ⚠️ **On the QA gate:** this step is not a QA step.
>
> **Post-conditions:** all seven tests pass; **the oracle-disagreement set is EMPTY** (currently 16); CONFORMANT and fold rows both RISE against your own before-measurement; three manifests, **6 killed / 0 survived / 0 ERROR**; the P7 test passes from a worktree, with `known_failures: 0` holding.

## STEP 2 — QA (full suite + the corpus restored)

> **Scope:**
> - `knowledge/qa/evidence/register-validate-first-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/register-validate-first-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/register-validate-first-2026-09-03/pytest_full.txt`
>
> **Item 1 — full suite from a WORKTREE:**
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> mkdir -p knowledge/qa/evidence/register-validate-first-2026-09-03
> "$BPY" -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/register-validate-first-2026-09-03/pytest_full.txt
> ```
>
> Confirm with `pwd` that you are in a worktree and that no repo-root `config.json` is present. ⚠️ **P7's test must PASS here** — from a worktree the true line is `1834 passed, 1 skipped`, 0 failed, which is why `known_failures: 0` is declared. Any failure here is real — HALT.
>
> **Item 2 — the corpus restored**, raw tails to the evidence file:
> 1. the BEFORE/AFTER pair over the same directory in the same run: CONFORMANT rises, fold rows rise, and **every** exempted register is enumerated and shown to genuinely fail validation. Report your absolute numbers; they supersede the authoring pins, which had already drifted by 2 rows and 1 register within the session that wrote them.
> 2. the specific register `walk-register-classify-307-318-2026-08-11.md` — declares an old version, carries the v0.3 shape — is **CONFORMANT** and emits its rows
> 3. a genuinely wrong-shaped legacy register still reports `LEGACY_SCHEMA`, so the exemption did not simply disappear
> 4. ⚠️ **the negative control:** a conformant v0.3 register is unaffected — the change did not turn everything conformant
> 5. `run_check register` over the corpus, and the verdict line quoted
>
> **Item 3 — `mutation_check` on all three manifests**; paste all three kill maps. **6 killed / 0 survived / 0 ERROR.**
>
> **Item 4 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; the restored counts stated plainly; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> **Item 5 — commit the evidence** (message tagged with the plan id); verify exactly 3 files.
>
> ⚠️ **On the QA gate:** this plan has a real test scope. Item 1 produces the pytest summary the gate parses; no override clause applies here, and none should be copied from this step.
>
> **Deposits:**
> - `knowledge/qa/evidence/register-validate-first-2026-09-03/pytest_full.txt`
> - `knowledge/qa/evidence/register-validate-first-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/register-validate-first-2026-09-03/qa-receipt.md`
>
> **Post-conditions:** suite green from a worktree with 0 failed; **the oracle-disagreement set is EMPTY**; CONFORMANT and fold rows both rise against the same-run before-measurement; the named register conformant; a wrong-shaped legacy register still `LEGACY_SCHEMA`; three kill maps, 6/6, 0 ERROR.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
