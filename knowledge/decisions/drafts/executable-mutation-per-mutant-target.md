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
| P3 | ⚠️ the specimen is HISTORICAL, not live | `knowledge/mutants/register-enforcement.json` carried `target` on M1 (`scripts/walk_register_lint.py`) and M2 (`tools/run_check.py`) and reported **3 killed / 0 survived / 2 error**, exit 2. **Plan 100030 renamed that file and stripped both keys while this plan was being drafted** — measured: **0** manifests in the tree carry a per-mutant `target` today, down from 1 at walk 0. The artifact is extractable at `305506c` (also `5956d26`, `a048ea7`) and must be reconstructed as a TEST FIXTURE, never pinned to a live path | `git show 305506c:knowledge/mutants/register-enforcement.json` |
| P4 | ⚠️ what already works | the run **exits 2** on any ERROR and names each offending mutant. It is not silent — only uninformative about the file | `mutation_check … >/dev/null 2>&1; echo $?` → 2 |
| P5 | self-application is established | `knowledge/mutants/mutation_check.json` exists (exec-577) — the runner already mutates itself, so this plan extends that manifest rather than inventing the practice | `ls knowledge/mutants/` |
| P6 | suite | `tests/test_mutation_check.py` = **11 tests** | `pytest --collect-only` |
| P7 | blast radius | manifests carrying a per-mutant `target`: **0** (was 1 before 100030's split). Manifest families split across files: **3** (`checker-defects-*`, `propagation-check-*`, `register-enforcement-*`) — all stay valid | enumerate `knowledge/mutants/*.json` |
| P8 | ⛔ the collision I cleared with the WRONG intersection | at walk 0 I checked **writes ∩ writes** against in-flight 100030 and declared it safe. The exposure was **reads ∩ writes**: this plan READ `register-enforcement.json` as its specimen, and 100030 WROTE (renamed) it. The depositor checks both — `writes∩writes` **or** `reads∩writes` — and I used half its vocabulary. 100030 has since closed; the lesson is that a pin on a live artifact is a READ, and an in-flight sibling's write set must be checked against a plan's reads as well as its writes | compare both intersections, not one |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⛔ **A manifest with NO per-mutant targets must behave byte-identically to today.** **Measured, not assumed: 12 manifests carry ZERO unknown per-mutant keys** (the union is exactly `anchor`, `expect_fail`, `name`, `replacement`, `why`), and 11 of the 12 carry no per-mutant `target` — so neither the honouring nor the refusal can regress any of them. Prove it anyway: run every existing manifest before and after and diff the output.
- ⛔ **Scoring is untouched.** `KILLED` is exit-1-only; anything else is `ERROR`; the run exits 2 if any mutant errors. This plan changes which FILE a mutant is applied to and what the message says — never what counts as a kill.
- ⚠️ **Refuse unknown per-mutant keys rather than ignoring them.** The defect is a silently-ignored field; fixing only this instance leaves the class. An unrecognised key names itself and the mutant, and errors.
- ⚠️ **The sandbox is `git archive` of COMMITTED code** — a per-mutant target must be resolved inside that sandbox, not against the live tree. The tool's own docstring says uncommitted edits are invisible; that stays true per-target.
- ⚠️ **Do not touch 100030's manifests** (P8). If it has closed by dispatch time, still do not — they are not in this plan's scope.
- ⚠️ **Worktree dispatch; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` bound absolutely; every claim cites file:line; EVERY DATE IS A FIXED LITERAL.**

## Drafting Cycle

**Tier:** T1 — T-3 fires (the runner runs on every machine that deposits). T-8 not fired: clone by kind of exec-579. T-6 not claimed: a conformance instrument, not a step gate.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-mutation-per-mutant-target-2026-09-03.md`
**Walks:** 5 (walks 0–5 complete).
- Weak spots:          w1 1 folded — instruction 0 / record 1; w2 dry; w3 dry; w4 dry; w5 dry.
- Destruction:         w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 dry; w5 1 folded — instruction 1 / record 0.
- Vulnerabilities:     w1 dry; w2 dry; w3 dry; w4 1 folded — instruction 1 / record 0; w5 1 folded — instruction 1 / record 0.
- Integration-record:  w1 dry; w2 dry; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry.
- ACID:                w1 dry; w2 2 folded — instruction 2 / record 0; w3 dry; w4 dry; w5 dry.
- Record sweep:        w5 1 folded — instruction 0 / record 1.
**Walk 0 — context pin:** seven measurements. The load-bearing one: `main()` reads the manifest's `target` once at `:100` and a mutant's own **zero** times — the key is accepted by the format and consumed by nothing. ⚠️ Also measured, correcting my own first framing: the tool is NOT silent — it names each offending mutant and exits 2.
**⚠️ Walk 2's two findings were caused EXTERNALLY, by a sibling plan closing underneath this one.** 100030's manifest split destroyed this plan's specimen mid-draft, and my walk-0 collision check had cleared it by comparing `writes ∩ writes` when the exposure was `reads ∩ writes` — half the vocabulary the depositor itself defines.
**Direction verdict — PROCEED.** Clone origin stands; the mechanism is narrow; the premise re-measured, including the correction that the tool already refuses loudly.
**⚠️ The escalation, and why it resolved:** `cycle_check` returned `ESCALATE:yield-rising` at walk 2 (instruction 1 → 2) and the cadence paused for the CEO, correctly. The rise was EXTERNAL — 100030 closed underneath this draft and destroyed its specimen — and the CEO resumed. Walk 3 fell to 1. ⚠️ It escalated a second time only because this log still said `Walks: 2`: the record lagged the practice and cycle_check read a stale series. The clock is the log, and I ran a walk before writing its row.
**⚠️ Walks 3–5 each found the PREVIOUS walk's fold incomplete or unexecutable.** Walk 4 found the plan's central post-condition unachievable by construction — `git archive HEAD` is hardcoded (`:132`) and M1's anchor was deleted from HEAD by 100030, so no run could ever report 5/5. Walk 5 found walk 4's own replacement unexecutable — `target` is repo-anchored three times, so scratch fixtures are impossible, and an absolute path escapes the sandbox and reports every mutant falsely SURVIVED. **The fixture was then BUILT AND RUN rather than specified:** measured `1 killed, 0 survived, 2 error` against the unfixed tool, with both the before and after results now pinned in step 1. Every one of these was caught by reading the consumer's path resolution, never by re-reading the prose.
**Out of scope, filed not folded:** the absolute-`target` sandbox escape is a latent `mutation_check` defect beyond this plan's mechanism — its own thread, not a widening of this one.
**Closing:** NOT CLOSED at walk 5 — three instruction-class findings, the convergence clock reset. Phrased so it cannot match a closure claim until earned.

## Cycle Manifest

*(emitted at BAR_MET)*

## STEP 1 — DEV (honour the key, refuse unknown ones, name the file)

> **Scope:**
> - `tools/mutation_check.py`
> - `tests/test_mutation_check.py`
> - `knowledge/mutants/mutation_check.json`
> - `knowledge/dev-logs/mutation-per-mutant-target-dev-2026-09-03.md`
>
> **Item 1 — re-derive P1–P8 and HALT on mismatch.** ⛔ **A manifest `target` MUST be a repo-relative path that exists at HEAD — scratch fixture files are impossible.** `target` is resolved three times, all repo-anchored: `os.path.join(repo_root, target)` (`:106`, must be a real file), `git status --porcelain -- target` (`:112`, must be a git path), and `os.path.join(sandbox, target)` (`:147`, must be inside `git archive HEAD`). ⚠️ An ABSOLUTE path defeats all three joins and mutates the real file OUTSIDE the sandbox while pytest runs unchanged code — every mutant then falsely SURVIVES. Do not use one.
> - **The fixture is BUILT AND VERIFIED — do not redesign it.** Extract `305506c`'s manifest, then assemble `$TMPDIR/fixture.json` as: top-level `target` `tools/run_check.py`; mutant `M2-pre-schema-counted-bad` with its `target` key **removed** (exercises the fallback); mutants `M3-assign-fail-not-warn` and `M4-warn-printed-after-verdict` each given `target: scripts/cycle_check.py` (exercise the per-mutant path). The manifest path itself is read from disk and may live in scratch; only the `target` VALUES are constrained. The manifest is a **positional** argument — there is no `--manifest` flag.
> - **Measured against the unfixed tool at `09a4a43`:** `M2 KILLED`, `M3 ERROR — anchor matched 0 times (expected 1)`, `M4 ERROR — …`, summary **`1 killed, 0 survived, 2 error`**, `LIVE-TREE UNCHANGED`. ⛔ Re-run and reproduce that exactly before touching code. If M3/M4 score normally instead, the defect is already fixed — HALT and request a verdict. If the summary differs in any other way, the fixture drifted — HALT.
> - **After the change the SAME fixture must report `3 killed, 0 survived, 0 error`.** All three anchors were confirmed count-1 in their own files at HEAD; nothing but the per-mutant-target read stands between the two results.
> - 100029's historical artifact is EVIDENCE only and is NOT runnable today: `mutation_check` hardcodes `git archive HEAD` (`:132`) and its M1 anchor was deleted from HEAD by plan 100030 (measured: count 0). Read it at `305506c` to confirm the keys were written and ignored; never make it a post-condition.
>
> ⚠️ **Then run the GATE, not just the commands** — `gates.check` on a simulated step 2 with deposit-shaped scratch copies, the receipt dict as `{"receipt_status":"Complete","ceo_flags":[],"is_error":False,"permission_denials":[],"result_text":"### Files Deposited\n- <the three step-2 paths>\n"}`, expecting `passed=True`, `is_qa_step=True`, 0 failures; **then strip the summary line and confirm `qa_test_result` fails.** ⛔ An inert control means the simulation proves nothing — HALT.
>
> **Item 2 — write the failing tests FIRST**, in `tests/test_mutation_check.py`:
> 1. ⛔ **the per-mutant-target case:** a manifest whose mutant carries its own `target` applies to THAT file and is scored normally — the regression this plan exists for
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
> **Item 7 — the no-regression sweep:** run **every** manifest in `knowledge/mutants/` before and after the change and diff the outputs. ⛔ **NO exclusions** — measured at walk 1, zero shipped manifests carry a per-mutant `target`, so any result that changes at all is a regression. HALT. (The old "other than the specimen" carve-out is void: the specimen is not in the tree.)
>
> **Item 8 — commit** (message tagged with the plan id); record `numstat` — exactly 4 files.
>
> **Deposits:**
> - `knowledge/dev-logs/mutation-per-mutant-target-dev-2026-09-03.md`
> - `knowledge/mutants/mutation_check.json`
>
> ⚠️ **On the QA gate:** this step is not a QA step.
>
> **Post-conditions:** all seven tests pass; the purpose-built fixture scores every mutant from ONE manifest with **0 ERROR**, and the SAME fixture ERRORs against the pre-change tool (proving it discriminates); every existing manifest byte-identical; the runner's own mutants all killed, 0 error. ⛔ **The historical specimen is evidence, not a post-condition** — M1's anchor is gone from HEAD and no run can restore it.
>
## STEP 2 — QA (full suite + the defect closed on a discriminating fixture)

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
> **Item 2 — the defect closed, on a PURPOSE-BUILT fixture:** ⛔ **100029's historical artifact CANNOT be used as the demonstration.** `mutation_check` hardcodes `git archive HEAD` (`:132`), and at HEAD **M1's anchor no longer exists** (count 0) — plan 100030 rewrote the exact version branch M1 targets. Running the specimen today can never score 5/5, before or after this change, so a post-condition demanding it is unachievable by construction.
> - The historical artifact stays as EVIDENCE only (P3): it proves the keys were written and ignored, and is extractable at `305506c` where all five anchors resolve count-1.
> - The DEMONSTRATION is a fixture manifest you build, with anchors valid at HEAD: at least two mutants carrying their own `target` pointing at two DIFFERENT real files, plus one with no per-mutant target falling back to the top-level. Show **all scored, 0 ERROR** — and show the same fixture reporting ERROR against the pre-change tool, so the fixture is proven to discriminate rather than merely to pass.
> ⚠️ **A fixture that passes on both the old and new tool proves nothing** — that is the inert-control failure this shop keeps paying for. Run it both ways.

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
> **Post-conditions:** suite green from a worktree, 0 failed; the purpose-built fixture fully scored with 0 ERROR from one manifest AND shown to ERROR against the pre-change tool; every existing manifest unchanged; both refusals fire and the negative control stays silent; the runner's own kill map clean.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
