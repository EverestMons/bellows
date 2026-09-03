# bellows — executable: `mutation_check` silently ignores a per-mutant `target` — honour it, refuse unknown keys, and name the file searched (thread 97)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the runner's suite) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 97 (open since 2026-09-02); exec-579 (Done 2026-08-27 — the clone origin: the newest shipped plan on this exact target); exec-577 (Done 2026-08-27 — gave the runner its OWN mutants manifest, so self-application is established here); plan 100029, which produced the live specimen.

## Why this exists

`mutation_check`'s manifest format **accepts a per-mutant `target` key and does nothing with it.** `main()` reads `manifest.get("target")` once (`:100`) and never consults a mutant's own. Measured on the live artifact `knowledge/mutants/register-enforcement.json`:

| mutant | per-mutant `target` written | tool reads it |
|---|---|---|
| M1-drop-version-branch | `scripts/walk_register_lint.py` | **no** |
| M2-pre-schema-counted-bad | `tools/run_check.py` | **no** |
| M3/M4/M5 | *(none)* | n/a |

Plan 100029's agent wrote those keys in good faith — its dev log states the intent explicitly: *"per-mutant `target` fields override for M1 and M2."* They were silently ignored, both mutants anchored against the manifest's top-level `cycle_check.py`, found nothing, and reported `ERROR — anchor matched 0 times (expected 1)`. **That message is true and useless: it never says which file was searched, so the cause reads as a bad anchor rather than a wrong file.** Two mutants covering that plan's primary defect verified nothing, and the plan halted.

⚠️ **What is NOT wrong, measured before assuming it:** the tool does **not** fail silently overall. It names each offending mutant and **exits 2**. Thread 97's alternative — *"or refuse with the offending mutant named"* — is therefore already half-satisfied at the run level. What is missing is that a per-mutant `target` is neither honoured nor rejected, and the message does not name the file it searched.

**Why the workaround is not enough.** The established convention is one manifest per target — "the 100023 manifest shape" the thread names, and what `checker-defects-*` and `propagation-check-*` both do. It works, and plan 100030 uses it. But nothing documents it, nothing enforces it, and the format keeps accepting a key that implies the opposite.

## What this plan does NOT do

- **It does not change the one-manifest-per-target convention** or rewrite any existing manifest. Split manifests remain valid and are still the right shape for unrelated targets.
- **It does not change scoring.** `KILLED` remains exit-1-only; `ERROR` remains everything else; the run still exits 2 when any mutant errors.
- **It does not touch plan 100030's manifests**, which are in flight.

## Numbers discipline

⚠️ **Measured 2026-09-03 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | target | `tools/mutation_check.py` **261 lines**, sha256 `f7037a1359f1` | `shasum -a 256` |
| P2 | the defect | `manifest.get("target")` read once at `:100`; **zero** reads of a mutant's own `target` | `/usr/bin/grep -c` for per-mutant target reads → 0 |
| P3 | the live specimen | `knowledge/mutants/register-enforcement.json` carries `target` on M1 (`scripts/walk_register_lint.py`) and M2 (`tools/run_check.py`); the run reports **3 killed / 0 survived / 2 error** and **exits 2** | run it; read the manifest |
| P4 | ⚠️ what already works | the run **exits 2** on any ERROR and names each offending mutant. It is not silent — only uninformative about the file | `mutation_check … >/dev/null 2>&1; echo $?` → 2 |
| P5 | self-application is established | `knowledge/mutants/mutation_check.json` exists (exec-577) — the runner already mutates itself, so this plan extends that manifest rather than inventing the practice | `ls knowledge/mutants/` |
| P6 | suite | `tests/test_mutation_check.py` = **11 tests** | `pytest --collect-only` |
| P7 | blast radius | manifests already carrying per-mutant `target`: **1** (the specimen). Manifest families split across files: **2** (`checker-defects-*`, `propagation-check-*`) — both stay valid | enumerate `knowledge/mutants/*.json` |
| P8 | in-flight | ⚠️ plan **100030** is running and writes `knowledge/mutants/register-enforcement-*.json`. This plan writes `knowledge/mutants/mutation_check.json` only — **write sets are disjoint** | `sqlite3` + compare the declared write sets |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⛔ **A manifest with NO per-mutant targets must behave byte-identically to today.** **Measured, not assumed: 12 manifests carry ZERO unknown per-mutant keys** (the union is exactly `anchor`, `expect_fail`, `name`, `replacement`, `why`), and 11 of the 12 carry no per-mutant `target` — so neither the honouring nor the refusal can regress any of them. Prove it anyway: run every existing manifest before and after and diff the output.
- ⛔ **Scoring is untouched.** `KILLED` is exit-1-only; anything else is `ERROR`; the run exits 2 if any mutant errors. This plan changes which FILE a mutant is applied to and what the message says — never what counts as a kill.
- ⚠️ **Refuse unknown per-mutant keys rather than ignoring them.** The defect is a silently-ignored field; fixing only this instance leaves the class. An unrecognised key names itself and the mutant, and errors.
- ⚠️ **The sandbox is `git archive` of COMMITTED code** — a per-mutant target must be resolved inside that sandbox, not against the live tree. The tool's own docstring says uncommitted edits are invisible; that stays true per-target.
- ⚠️ **Do not touch 100030's manifests** (P8). If it has closed by dispatch time, still do not — they are not in this plan's scope.
- ⚠️ **Worktree dispatch; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` bound absolutely; every claim cites file:line; EVERY DATE IS A FIXED LITERAL.**

## Drafting Cycle

*(the walks record here)*

## Cycle Manifest

*(emitted at BAR_MET)*

## STEP 1 — DEV (honour the key, refuse unknown ones, name the file)

> **Scope:**
> - `tools/mutation_check.py`
> - `tests/test_mutation_check.py`
> - `knowledge/mutants/mutation_check.json`
> - `knowledge/dev-logs/mutation-per-mutant-target-dev-2026-09-03.md`
>
> **Item 1 — re-derive P1–P7 and HALT on mismatch.** P3 is the plan's justification: run the specimen manifest and show `3 killed / 0 survived / 2 error`, **exit 2**, with M1 and M2 named. ⛔ If it now reports 5 killed, the defect is gone — HALT and request a verdict.
>
> ⚠️ **Then run the GATE, not just the commands** — `gates.check` on a simulated step 2 with deposit-shaped scratch copies, the receipt dict as `{"receipt_status":"Complete","ceo_flags":[],"is_error":False,"permission_denials":[],"result_text":"### Files Deposited\n- <the three step-2 paths>\n"}`, expecting `passed=True`, `is_qa_step=True`, 0 failures; **then strip the summary line and confirm `qa_test_result` fails.** ⛔ An inert control means the simulation proves nothing — HALT.
>
> **Item 2 — write the failing tests FIRST**, in `tests/test_mutation_check.py`:
> 1. ⛔ **the specimen case:** a manifest whose mutant carries its own `target` applies to THAT file and is scored normally — the regression this plan exists for
> 2. a mutant with no `target` falls back to the manifest's top-level one (the nine existing manifests' shape)
> 3. ⛔ **byte-identical behaviour** for a manifest with no per-mutant targets at all — the positive control
> 4. a per-mutant `target` naming a file that does not exist → `ERROR` naming the mutant AND the missing path
> 5. ⛔ **an unrecognised per-mutant key → ERROR naming the key and the mutant**, not silence
> 6. the anchor-mismatch message **names the file searched** — the message that would have made 100029's failure self-explaining
> 7. scoring unchanged: a surviving mutant is still `SURVIVED`, a killed one still `KILLED`, and any ERROR still exits 2
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — honour the per-mutant `target`**, resolved inside the `git archive` sandbox, falling back to the manifest's top-level value. A manifest with no per-mutant targets takes the identical path it takes today.
>
> **Item 4 — refuse unknown per-mutant keys**, naming the key and the mutant. The recognised set, read off the 12 shipped manifests rather than from this plan's prose: `name`, `why`, `anchor`, `replacement`, `expect_fail`, and now `target`.
> - ⛔ **Underscore-prefixed keys are COMMENTARY and must be permitted, not refused.** The convention is live: `_note` appears in three manifests and `_removed_note` in a fourth — and three of those four were written today. `mutation_check` honours it by construction, reading only `target` and `mutants` and ignoring everything else. A strict refusal would contradict a convention the shop is actively using; exempt any key beginning with `_` at BOTH levels, and say so in the message so the exemption is discoverable.
>
> **Item 5 — name the file searched** in the anchor-mismatch message.
>
> **Item 6 — extend `knowledge/mutants/mutation_check.json`** (exec-577's self-application manifest) with mutants for each new branch: drop the per-mutant lookup → test 1 fails; drop the unknown-key refusal → test 5 fails; drop the filename from the message → test 6 fails. ⚠️ **A survivor is a missing test, stated as Critical, never a note** — and ⛔ **0 ERROR is required too**: an errored mutant verifies nothing, which is the failure this very plan is about.
>
> **Item 7 — the no-regression sweep:** run **every** manifest in `knowledge/mutants/` before and after the change and diff the outputs. ⛔ Any manifest whose result changes, other than the specimen, is a regression — HALT.
>
> **Item 8 — commit** (message tagged with the plan id); record `numstat` — exactly 4 files.
>
> **Deposits:**
> - `knowledge/dev-logs/mutation-per-mutant-target-dev-2026-09-03.md`
> - `knowledge/mutants/mutation_check.json`
>
> ⚠️ **On the QA gate:** this step is not a QA step.
>
> **Post-conditions:** all seven tests pass; the specimen manifest reports **5 killed / 0 survived / 0 error** from ONE manifest; every other manifest byte-identical; the runner's own mutants all killed, 0 error.
>
## STEP 2 — QA (full suite + the specimen closed from one manifest)

> **Scope:**
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/pytest_full.txt`
>
> **Item 1 — full suite from a WORKTREE:**
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> mkdir -p knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03
> "$BPY" -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/pytest_full.txt
> ```
>
> Confirm with `pwd` that you are in a worktree and that no repo-root `config.json` is present — that file's absence is why `known_failures: 0` is correct here. Derive the count and state the arithmetic.
>
> **Item 2 — the specimen, closed:** run `knowledge/mutants/register-enforcement.json` **unchanged** and show **5 killed / 0 survived / 0 error** from a single manifest, against the 3/0/2 of P3. ⚠️ Do not edit that manifest — it is 100029's artifact and the point is that the TOOL now reads it correctly.
> **Item 3 — the no-regression sweep**, every manifest before and after, diffed; paste the diff or state it empty.
> **Item 4 — the refusals fire:** a manifest with an unknown per-mutant key errors naming the key; a per-mutant target pointing at a missing file errors naming the path. ⚠️ **Negative control:** a well-formed manifest produces no refusal — show it staying silent.
> **Item 5 — the runner's own manifest**; paste the kill map, 0 error.
> **Item 6 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; then the QA self-check block inside a Verification-headed section (the 556 placement law).
> **Item 7 — commit the evidence** (message tagged with the plan id); verify exactly 3 files.
>
> ⚠️ **On the QA gate:** this plan has a real test scope. Item 1 produces the pytest summary the gate parses; no override clause applies here, and none should be copied from this step.
>
> **Deposits:**
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-03/qa-receipt.md`
>
> **Post-conditions:** suite green from a worktree, 0 failed; the specimen at 5/0/0 from one manifest; every other manifest unchanged; both refusals fire and the negative control stays silent; the runner's own kill map clean.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
