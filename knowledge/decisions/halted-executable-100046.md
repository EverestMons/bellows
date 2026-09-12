# bellows — executable: QA-only — the per-mutant `target` fix that landed as `f00a9e0` (plan 100031 STEP 1) gets the STEP 2 battery it never had, its evidence and its Done record (threads 97, 109, 214)

**Date:** 2026-09-08 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full suite + the runner's own suite; no code write | **Execution:** Step 1 (QA) | **qa_steps:** 1 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1 | **Discharges:** thread 97, thread 109, thread 214

**auto_close:** false

**Depends on:** the CEO re-ruling of 2026-09-08 on thread 112 (thread 214: NO revert — a QA-only plan runs 100031's STEP 2 battery against the merged code). Clone origin for the SHAPE: `Done/executable-100013.md` (2026-09-01 — the newest one-step QA-classified plan, `qa_steps: 1`, evidence-only writes); clone origin for the CONTENT: `knowledge/decisions/halted-executable-100031.md` STEP 2 (its Items 1–7, re-read against today's tree). Thread 105 (the absolute-target sandbox escape, the ordering prerequisite 112 named) is done.

## What this changes

⛔ **No code. One QA step over `main` as it is, producing the three evidence files STEP 2 of plan 100031 owed and, at close, the Done record.** The DEV half already happened: `f00a9e0` (2026-09-03) rewrote `tools/mutation_check.py` to honour a per-mutant `target`, refuse unknown mutant keys and name the file searched, with `tests/test_mutation_check.py` (26 tests), the runner's own manifest and a dev-log — merged when plan 100031 halted at its deposit defect, never gated by a QA step.

## Why this exists

Plan 100031 halted after STEP 1 on a deposit/classification defect (the Cycle Manifest was never emitted; LESSONS 2026-09-03 entry 413), not on a work defect. Its STEP 1 had committed and the daemon merged `f00a9e0`. The code has since been exercised by every mutation run in the shop — plan 100045's 22-mutant manifest carries a per-mutant `target` on every mutant and ran 22 killed / 0 survived / 0 error today — but no QA step ever ran STEP 2's battery, so there is no evidence file, no receipt and no Done record. The CEO's 2026-09-03 ruling was to revert and re-deposit; measured tonight, a revert would make a shipped plan's mutation run unreproducible, and the CEO re-ruled (thread 214): QA the merged code.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the merged fix | `f00a9e0` (2026-09-03): `tools/mutation_check.py` +118/−28, `tests/test_mutation_check.py` +266 (new), `knowledge/mutants/mutation_check.json` +35, `knowledge/dev-logs/mutation-per-mutant-target-dev-2026-09-03.md` +119 | `git show --stat f00a9e0` |
| P2 | ⛔ old vs new tool | parent `b143604`: 261 lines, **0** reads of a mutant's own `target`, no `_KNOWN_MUTANT_KEYS`; HEAD: 368 lines, `mutant.get("target")` read, `_KNOWN_MUTANT_KEYS` present; `tools/mutation_check.py` sha256 `1063e817ff24…` | `git show b143604:tools/mutation_check.py \| grep -c 'mutant.get("target")'` → 0; the same on HEAD → 1 |
| P3 | the runner's suite | **26** tests collected in `tests/test_mutation_check.py`, all passing | `pytest tests/test_mutation_check.py --collect-only -q` |
| P4 | the runner's own kill map today | `knowledge/mutants/mutation_check.json` → `MUTATION: 7 killed, 0 survived, 0 error`, `LIVE-TREE UNCHANGED` at HEAD `34eeab2` | run the manifest |
| P5 | ⛔ the manifest corpus | **17** manifests, 90 mutants; **2** carry a per-mutant `target` on every mutant — `close-failopen-defaults.json` (6/6) and `gates-verdict-pause.json` (22/22); **3** `.run.txt` files exist (100042, 100043, 100045) | enumerate `knowledge/mutants/*.json` with the per-mutant count |
| P6 | ⛔ the live demonstration already exists | plan 100045's run file: `MUTATION: 22 killed, 0 survived, 0 error` over a manifest whose every mutant names `gates.py` or `verdict.py` as its own target — the defect 97 described (a per-mutant target ignored) cannot produce that line | `tail -1 knowledge/mutants/gates-verdict-pause.run.txt` |
| P7 | 100031's STEP 2, re-read | Items 1–7: full suite from the worktree; a purpose-built fixture scored 0 ERROR under the new tool AND shown to ERROR under the old (the inert-control law); every manifest re-run and diffed; the two refusals fire, a negative control stays silent; the runner's own kill map; hygiene + receipt; commit exactly three files. Its historical specimen (`register-enforcement.json` at `305506c`) stays evidence only — 100030 stripped the keys | read the halted plan |
| P8 | this plan's own class | evidence-only writes under `knowledge/qa/evidence/` → `_assign_class` → **app-feature** (auto-clears; no class hold, no CEO release act). `is_qa_step(1)` under `qa_steps: 1` → True — verified by execution on this draft at walk 1 (f6) | `depositor.Depositor._assign_class(writes, root)`; `gates._gate_is_qa_step` |
| P10 | ⛔ the sweep BASELINE (walk 1, HEAD `34eeab2`) | 17 manifests run: **15** clean (their `MUTATION:` lines in the register — the three with run files match them; `mutation_check.json` = P4); **2** ERROR on stale anchors — `checker-defects-cycle_check.json` `3 killed, 0 survived, 1 error`, `manifest-provenance-gate.json` `1 killed, 0 survived, 3 error` (error lines in the register). Item 4 is judged against THIS table | re-run all 17; diff against the register's table |
| P11 | ⛔ the discriminating fixture, RUN both ways at walk 2 | three mutants copied from clean P10 manifests (register-enforcement-run_check M2 as the fallback; -wrl M1 with target `scripts/walk_register_lint.py`; -cycle_check M3 with target `scripts/cycle_check.py`), top-level target `tools/run_check.py`. HEAD's tool: `3 killed, 0 survived, 0 error`, LIVE-TREE UNCHANGED ×3. `b143604`'s tool (`--repo-root` at the worktree): M1 and M3 `ERROR — anchor matched 0 times (expected 1)`, M2 KILLED, `1 killed, 0 survived, 2 error`; porcelain unchanged after both | assemble from the register's pasted fixture; run both tools |
| P12 | the refusals, RUN at walk 3 | unknown key → `ERROR — unknown key(s) 'targt' (prefix with _ to mark as commentary)`, exit 2; per-mutant target at a missing file → `ERROR — target not in archive: <path>` (the top-level form `ERROR: target not found:` is a different site), exit 2; the run continues and reports `1 error` in both; the clean fixture exits 0 | `tools/mutation_check.py` on the two variants of the register's fixture |
| P9 | in-flight | none at walk 0 (daemon pid 42126, HEAD `34eeab2`) | `status.py` |

## What this does NOT do

- ⛔ **It does not touch `tools/mutation_check.py`, its tests or any manifest.** A finding against the code is a HALT and a new thread, never a QA-side edit (the 100045 STEP 2 class, thread 212).
- ⛔ **It does not re-run STEP 1.** The DEV work is `f00a9e0`; this plan judges it.
- **It does not build the plan_lint (s) manifest-shape check** thread 97 also asks for — that is a plan_lint change, its own thread (fork 1).
- **It does not decide the per-target-file convention** (100031's M6) — documenting it is a doctrine item (fork 2).

## MUST-PRESERVE

⛔ **Invariants that must still be TRUE afterwards.**

- ⛔ **`main` is byte-identical outside the three evidence files** — numstat over the step's commit is exactly three paths under `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/`.
- ⛔ **Every existing manifest reports the same kill map before and after** — trivially, since nothing changes; the sweep proves the runner reads all 17 today.
- ⛔ **The fixture is DISCRIMINATING**: it scores 0 ERROR under HEAD's tool and ERRORs under `b143604`'s — a fixture that passes both ways proves nothing.
- ⛔ **No production write**: no lane file, no sidecar, no lifecycle row by the agent, no repo-root `config.json` in the worktree.

## Drafting Cycle

**Tier:** **T1** — T-3 (the runner runs on every machine that deposits) as 100031 read it; T-6 not claimed (a conformance instrument, not a step gate); no panel. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-mutation-per-mutant-target-qa-2026-09-08.md
**Walks:** walk 0 pinned (P1–P9 measured on bellows `34eeab2`; clone-diff against `Done/executable-100013.md` (shape) and `halted-executable-100031.md` STEP 2 (content) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit, emit after the re-save (v2.30). ⛔ **One commit per lens** (§2.7) — `lens_order_check` runs with `cycle_check` at every walk close.

- Weak spots:          w1 4 folded — instruction 3 / record 1; w2 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w4 dry
- Destruction:         w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 dry
- Vulnerabilities:     w1 dry; w2 dry; w3 dry; w4 dry
- Integration-record:  w1 1 folded — instruction 0 / record 1; w2 dry; w3 dry; w4 dry
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry

**Walk 4 — DRY, all five lenses, one commit per lens; `lens_order_check` OK across walks 1–4. Instruction 0 on a full pass: the WARM close meets §2's bar (T1, no panel) — a judged stop, with the classification shown (8 findings: instruction 6 / record 2; yield by walk 4 → 1 → 1 → 0).**
**Closing:** WARM close after walk 4 — the QA-only plan over `f00a9e0` under the CEO's 2026-09-08 re-ruling (thread 214). Deposit via `ready-`; class app-feature auto-clears; no restart owed (no code).

## Cycle Manifest
tier: T1
target: tools/mutation_check.py
class: app-feature
reads: tools/mutation_check.py, tests/test_mutation_check.py, knowledge/mutants/mutation_check.json, knowledge/mutants/gates-verdict-pause.json, knowledge/decisions/halted-executable-100031.md, knowledge/decisions/Done/executable-100013.md, knowledge/dev-logs/mutation-per-mutant-target-dev-2026-09-03.md
writes: knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/pytest_full.txt, knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/probes-raw.txt, knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/qa-receipt.md
open_forks: 1. plan_lint (s) validates a manifest's shape at deposit (thread 97's second ask) — its own thread; 2. document the one-manifest-per-target convention and the per-mutant alternative (100031's M6) — doctrine; 3. two manifests ERROR at HEAD on stale anchors (P10) — the runner audits committed code and the anchors drifted; decide re-anchor or retire, its own thread
walks: 4
yields: 4, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:16
coherence: 4/4 body walks named in the register (11 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-mutation-per-mutant-target-qa.md.foldcheck.json

---

## STEP 1 — QA (the STEP 2 battery plan 100031 owed, over `main` as it is)

> ⛔ **Re-establish the root first** — `cd "$(git rev-parse --show-toplevel)" && test -f tools/mutation_check.py && echo TREE_OK`; HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE** (a dispatch worktree carries no `.venv`); prove `VENV_OK` with `-c 'import pytest'`. Confirm with `pwd` that you are in the worktree and that no repo-root `config.json` is present — its absence is why `known_failures: 0` is correct. `mkdir -p knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08` (call it `$EV`).
>
> **Scope:**
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/qa-receipt.md`
>
> **Item 1 — re-derive P2, P3, P4 and HALT on mismatch** (the mechanism pins); paste the three results into `probes-raw.txt`.
> **Item 2 — full suite, REDIRECTED not piped, gated on the exit code:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > $EV/pytest_full.txt 2>&1 || { echo HALT-SUITE-RED; exit 1; }`. Derive the count from the summary line and state the arithmetic (`known_failures: 0`).
> **Item 3 — the DISCRIMINATING fixture.** Build the fixture OUTSIDE the evidence dir and outside any lane, in a scratch dir under the worktree root — `$(git rev-parse --show-toplevel)/.qa-scratch/` (never `/tmp`: the runner's sandbox resolves targets against the repo; delete the dir before Item 6, whose porcelain check must show only `$EV`): a manifest with top-level `"target": "tools/run_check.py"` and EXACTLY these three mutants, copied verbatim (name/why/anchor/replacement/expect_fail) from manifests that killed at HEAD in the P10 sweep — do not design new ones: (1) `M2-pre-schema-counted-bad` from `register-enforcement-run_check.json`, NO per-mutant target (falls back to the top-level); (2) `M1-drop-legacy-schema-branch` from `register-enforcement-wrl.json` with `"target": "scripts/walk_register_lint.py"`; (3) `M3-assign-fail-not-warn` from `register-enforcement-cycle_check.json` with `"target": "scripts/cycle_check.py"` (P11; the assembled fixture is pasted in the register). Run it under HEAD's tool → `MUTATION: 3 killed, 0 survived, 0 error`, three `LIVE-TREE UNCHANGED` lines (P11). Then extract the pre-change tool — `git show b143604:tools/mutation_check.py > .qa-scratch/mc_old.py` — ⚠️ the OLD tool carries thread 105's sandbox escape (an ABSOLUTE `target` mutated the live tree and reported SURVIVED): the fixture uses RELATIVE targets only, and `git status --porcelain` is checked unchanged immediately after the old-tool run — and run the SAME fixture under it from the worktree root with `--repo-root "$(git rev-parse --show-toplevel)"` (both tools resolve the repo from the CWD by `git rev-parse --show-toplevel` and accept the flag) → `MUTANT M1-drop-legacy-schema-branch: ERROR — anchor matched 0 times (expected 1)`, the same for `M3-assign-fail-not-warn`, `M2-pre-schema-counted-bad: KILLED`, `MUTATION: 1 killed, 0 survived, 2 error` (P11). ⚠️ Paste both runs verbatim; a fixture that behaves the same both ways proves nothing (the inert-control law) — if it does, the fixture is wrong, not the tool: fix the fixture.
> **Item 4 — the no-regression sweep:** run every `knowledge/mutants/*.json` (17, P5) through HEAD's tool, one line per manifest `<name>: MUTATION: …`; for the three with a `.run.txt` (100042, 100043, 100045) the counts must equal the run file's last `MUTATION:` line; for the runner's own manifest the count must equal P4. Paste the 17 lines. Compare against P10's baseline: a manifest whose line DIFFERS from the baseline is a HALT (a code finding → thread, never a QA edit); the two manifests P10 records as ERRORing on stale anchors at HEAD must reproduce their baseline lines exactly (they are the corpus's drift, fork 3, not this plan's subject).
> **Item 5 — the refusals fire, the control stays silent:** (a) the Item 3 fixture with mutant (2)'s `target` key misspelt `"targt"` → the run continues and reports `MUTANT M1-drop-legacy-schema-branch: ERROR — unknown key(s) 'targt' (prefix with _ to mark as commentary)`, `MUTATION: 2 killed, 0 survived, 1 error`, exit **2**; (b) the fixture with mutant (2)'s `target` set to `scripts/does_not_exist.py` → `MUTANT M1-drop-legacy-schema-branch: ERROR — target not in archive: scripts/does_not_exist.py`, `2 killed, 0 survived, 1 error`, exit **2**; (c) the negative control — the Item 3 fixture unchanged → no ERROR line, exit **0** (P12: all three measured at walk 3). Paste all three with `; echo "exit=$?"`.
> **Item 6 — hygiene + receipt** `$EV/qa-receipt.md`: `git rev-parse --show-toplevel`; `git status --porcelain` shows only `$EV` (the scratch dir deleted); `git reflog -n 4` → 0 amends, 0 resets; P1 re-quoted from `git show --stat f00a9e0`; a per-item table (Items 1–5, each on its own line with its result); then the Rule 20 block inside a `## Verification` section. ⛔ Quote test node ids ONLY as pytest printed them (`quoted_test_nodes_exist` reads this receipt); never place a hedging keyword in a ✅ row.
> **Item 7 — commit the evidence**, pathspec-scoped and gated: `grep -Eq '^[0-9]+ passed' $EV/pytest_full.txt && ! grep -Eq '[0-9]+ (failed|error)' $EV/pytest_full.txt && git add $EV && git commit -F <msg-file>` — exactly three files, message tagged with the plan id.
>
> ⚠️ **On the QA gate:** `qa_test_result` now selects the `.txt` by content (plan 100045); `pytest_full.txt` is the only summary-bearing `.txt`. No override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/qa-receipt.md`
>
> **Post-conditions:** suite green, 0 failed; the fixture `3 killed, 0 survived, 0 error` under HEAD and `1 killed, 0 survived, 2 error` under `b143604` (P11); 17 manifests re-run, the three with run files matching, P4 matching; both refusals fire, the control silent; exactly three files in the commit.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
