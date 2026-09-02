# bellows — executable: A PROBE'S LOCATION IS PART OF ITS ENVIRONMENT — six seam tests learn to hide the projects parent, the watcher's test STATE dimension gains `awaiting_verdict`, and plan 100011's suite proof is re-run on main in the shapes that matter

**Date:** 2026-09-01 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_plan_claim.py`, `tests/test_gate_watcher.py`, `tests/test_governance_root.py`) + a full-suite CONTROL COMPARISON in the worktree shape (set EMPTY) with the canonical-shape run measured by the Planner at the pause | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1

**auto_close:** false

**Slug:** `seam-tests-projects-parent-2026-09-01`

**Depends on:** plan 100011 (`halted-executable-100011.md`, STOP at Step 1 on 2026-09-01 — its DEV commit `6b892a3` is on main and STAYS; the verdict's reason text in `verdicts/resolved/processed-verdict-100011-step-1.md` is the citable finding); the CEO's direction that authorized 100011 (*"minimize the notion of a 'shop machine'"*, 2026-09-01 — this plan finishes that work; the standing release sentence *"If gates have all passed you have permission to run it"* applies to whatever hold the depositor assigns); 100011 as the clone origin BY KIND (its Step 2 items are the source of this plan's QA). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-de-hardcode-2026-09-01.md` (the child section "Follow-up cycle — seam-tests-projects-parent").

**Tier computed, not judged (§1):** **T-1 fires** (two test files in one subsystem — more than one localized change). **T-8 fires** (a clone by kind of 100011, not by shape: tests only, no builder). T-6 no (no gate, no doctrine; `tools/gate_watcher.py` is untouched — the STATE dimension that lacks the state lives in the TEST). T-2, T-3, T-5 no. → **T1: the five-lens walk, no panel.** No builder: three anchored edits, each anchor counted by the Planner at walk 0 and re-derived by DEV (one anchor deliberately count 6, stated).

## Why this exists — measured on main at `6b892a3`, 2026-09-01 23:1x

Plan 100011 replaced the seam's third candidate root (`ROOT/tuyere`) — the shop literal — with `bellows_root.resolve_projects_parent()`. On this machine that resolves to `/Users/marklehn/Developer`, which HOLDS `tuyere/.venv/bin/python`. Six tests in `tests/test_plan_claim.py` construct "no tuyere resolvable" by deleting `$ELUVIAN_WRAP_TUYERE` and `$ELUVIAN_WRAP_ROOT` and monkeypatching `Path.home` — the two sources the OLD code had, plus a literal that was dead here. They never hid the third source because it could not resolve on this machine. Now it can, so four of them fail (`TestOffModeNoOp::test_release_off_mode_checkout_unresolvable`, `TestDecisionTable::test_advisory_checkout_none`, `TestResolverTwin::test_both_none`, `TestResolverTwin::test_shim_reads_env_at_call_time`) and two pass only because an earlier candidate or the mode short-circuits (`test_required_checkout_none`, `test_root_env_tuyere`). Measured directly: `_tuyere_checkout()` with the projects parent forced to `/Users/marklehn/Developer` → `…/tuyere`; forced to `/private/tmp` → `None`.

Separately, `tests/test_gate_watcher.py::TestPauseStateSpace::test_reachable_states_match_the_classification_dimension` reads the LIVE `lifecycle.db` and asserts every reachable `plans.lifecycle_state` is in its `STATE` tuple `("in_progress", "closed", "halted", "abandoned")`. Plan 100009 taught the daemon to write `awaiting_verdict`; the tuple never learned it. The test fails exactly while a plan is paused — it failed at 100011's pause and passes now that 100011 is halted. The tool itself (`tools/gate_watcher.py`) classifies the phase `awaiting-verdict` correctly (`:104`, `:110`, `:222`); only the test's dimension is stale.

Why no proof caught the seam tests: every scratch proof of 100011 — its walk-0 clone, both scouts' clones, the EXECUTION seat's worktree replica, the Planner's `/tmp` worktree — sat under a parent that held no `tuyere/`; the resolver's answer depends on where the tree SITS, and only the canonical checkout (and the daemon's real `.bellows-worktrees/<wt>`, which resolves the canonical root through its `config.json` sentinel) sits under `/Users/marklehn/Developer`. A probe's location is part of its environment. This plan's QA therefore runs where the daemon runs, and the Planner runs the canonical shape at the pause.

## What this plan does

- **E1 — `tests/test_plan_claim.py`, the import:** anchor `import lifecycle\nimport plan_claim\n` (count 1) → `import bellows_root\nimport lifecycle\nimport plan_claim\n`.
- **E2 — `tests/test_plan_claim.py`, the six home-hiding lines:** anchor `        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")\n` (**count 6 — all six intended**, lines 79, 217, 232, 317, 328, 337 at `6b892a3`) → the same line followed by `        monkeypatch.setattr(bellows_root, "resolve_projects_parent", lambda _start=None: tmp_path / "noprojects")\n`. `plan_claim._tuyere_checkout` imports the resolver from `bellows_root` INSIDE the function at call time, so the monkeypatch on the module attribute is what it reads (the same mechanism `tests/test_governance_root.py::TestConsumers::test_tuyere_seam_third_candidate_is_projects_parent` already relies on).
- **E3 — `tests/test_gate_watcher.py`, the state-space dimension (three anchored edits, one dimension):** the STATE tuple feeds `itertools.product(PENDING, VERDICT, STATE)` and a `CLASSIFICATION` table whose every cell is proven LIVE by the parametrized `test_every_cell_behaves_as_classified` (it builds the DB row and the files and calls `read_state`), and `test_state_space_is_completely_classified` asserts the product's size. So: **E3a** anchor `    STATE = ("in_progress", "closed", "halted", "abandoned")\n` (count 1) → `    STATE = ("in_progress", "awaiting_verdict", "closed", "halted", "abandoned")\n`. **E3b** anchor `        ("present", "processed", "in_progress"): "NO_PAUSE",\n    }\n` (count 1) → the same line, then six rows before the `}`: `("absent"|"present") × ("none"|"issued"|"processed") × "awaiting_verdict"` → **`"REPORT_PAUSE"` for all six**, with the comment `# row state awaiting_verdict → REPORT_PAUSE regardless of the file dimensions (100009's DB corroboration: the state IS the pause; tools/gate_watcher.py returns the awaiting-verdict phase on it after the file checks)`. Derived by READING `tools/gate_watcher.py`: the `if state == "awaiting_verdict": return {"phase": "awaiting-verdict", …}` after the pending-file branch — the file dimensions can only ADD a pause, never remove one, for that state; the parametrized test then RUNS each of the six cells against `read_state`, so a wrong derivation fails in A3, not in production. **E3c** anchor `        assert len(self.CLASSIFICATION) == 2 * 3 * 4\n` (count 1) → `2 * 3 * 5`.
- Nothing else. No code file changes; the resolver, the seam and the watcher stay as 100011 left them.

## What this plan does NOT do

- Does not touch `plan_claim.py`, `bellows_root.py`, `tools/gate_watcher.py` or any 100011 target; does not revisit 100011's QA mutants (three cold seats and the Planner executed them — the register). Does not restart the daemon (Restart Discipline: the CEO's dashboard act; the running daemon, pid 93535, still injects the pre-fix QA mandate into THIS plan's Step 2 — told below).
- Does not close the seven-site `hooks-de-hardcode` follow-up or the `MACHINE_SETUP` lines 100011 named — they stay named there.

## MUST-PRESERVE

- **The tests hide ALL THREE sources of a tuyere checkout** — env override, home, projects parent — before asserting "unresolvable". A test that hides two and relies on the third being dead on the author's machine is the defect this plan removes; do not "fix" a test by asserting the machine-specific answer.
- **The STATE tuple is the TEST's dimension, not the tool's**: the tool already classifies `awaiting-verdict`; the tuple lists the plan-row states the classification must cover. `awaiting_verdict` is a real row state since 100009.
- **`known_failures: 0` and the gate's count semantics** (100011's MUST-PRESERVE, unchanged): the gate compares a COUNT with ≤; the NAMED-set property is carried by QA Item 3. The flake protocol from 100011 applies (`tests/test_notifier_server.py::test_server_respond` flaked once for a scout).

## Numbers discipline — the pins DEV re-derives (measured by the Planner at bellows `6b892a3`)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`TARGET_SHAS`** — the two test files | `tests/test_plan_claim.py` `4d5e7faac54920a9` · `tests/test_gate_watcher.py` `6f55a13f3b7acead` | `shasum -a 256 <f> \| cut -c1-16` |
| P2 | **`ANCHOR_E1`** / **`ANCHOR_E2`** / **`ANCHOR_E3A`** / **`ANCHOR_E3B`** / **`ANCHOR_E3C`** counts, pre-edit | 1 / **6** / 1 / 1 / 1 | `/usr/bin/grep -cF -- '<anchor line>' <f>` (E3b is a two-line anchor — count it with a script, or count its first line: `("present", "processed", "in_progress"): "NO_PAUSE",` → 1) |
| P3 | **`NEW_LINES`** — post-edit tokens | `resolve_projects_parent` in `tests/test_plan_claim.py` pre **0** → post **6**; `import bellows_root` pre 0 → post 1; `"awaiting_verdict"` in `tests/test_gate_watcher.py` pre **2** (two existing fixtures name it) → post **9** (+ the tuple + six cells); `2 * 3 * 5` pre 0 → post 1 | same |
| P3b | **`WATCHER_TESTS`** — `tests/test_gate_watcher.py` collected | pre: the parametrized cell test has 24 ids; post **30** (six new cells, all `REPORT_PAUSE`, each executed against `read_state`) | `"$PY" -m pytest -q -p no:cacheprovider tests/test_gate_watcher.py` — state the pass count pre and post; the difference must be exactly 6 |
| P4 | **`SEAM_PRE`** — the six seam tests on main, canonical shape, pre-edit | `4 failed, 2 passed` over the six ids | `"$PY" -m pytest -q -p no:cacheprovider tests/test_plan_claim.py` → `4 failed, 45 passed` (49 tests in the file, measured) |
| P5 | **`SUITE_PRE`** — the full suite on main at `6b892a3`, canonical shape, no plan paused | expected `1 failed` (the CWD survivor `test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged`) + the four seam ids = **5 failed**; measured `6 failed, 1658 passed` WHILE 100011 was paused (the sixth: the STATE test — E3's cause). The Planner re-measures after the halt | `"$PY" -m pytest tests -q -p no:cacheprovider` |
| P6 | **`SUITE_POST`** — post-edit, in the WORKTREE shape (QA's) | failing set **EMPTY**; passed ≥ **1663**; skipped 0 or 1 (a location property: the live-DB test skips only where `lifecycle.db` is unreachable) | same, from the worktree |
| P7 | **`SUITE_POST_CANONICAL`** — post-edit, canonical shape, no plan paused (the Planner, at the pause, from the merged main) | failing set == {the CWD survivor}; passed at or above P6's floor | same, from `/Users/marklehn/Developer/bellows` |

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the Bellows Developer.
>
> ⛔ **A0 — pre-flight.** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -f tests/test_plan_claim.py ] && echo TREE_OK` — HALT unless TREE_OK. `MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd); PY="$MAIN/.venv/bin/python"; [ -x "$PY" ] && echo VENV_OK || echo NO_VENV` — HALT unless VENV_OK. Re-derive `PY` in every compound. zsh: explicit arrays for lists. `/usr/bin/grep -F` for every literal.
>
> ⛔ **A1 — re-derive P1, P2, P3-pre, P4; state each; a mismatch is a HALT quoting both values.** For P4 expect the four named ids in the `FAILED` lines (`4 failed, 45 passed`) — in your WORKTREE the projects parent still resolves to `/Users/marklehn/Developer` (through the canonical `config.json` sentinel), so the four fail there too; if they PASS pre-edit, your worktree is not where the daemon puts them — HALT and say where you are (`git rev-parse --show-toplevel`; `"$PY" -c "import bellows_root as b; print(b.resolve_projects_parent())"`).
>
> **A2 — the three edits, with a script (never a blind global replace), asserting each anchor count BEFORE editing:** E1 (count 1), E2 (count 6 — insert the projects-parent line directly after EACH occurrence, same indentation), E3a (count 1), E3b (count 1 — the six rows inserted before the table's closing brace, same indentation as the row above, the comment line first), E3c (count 1). Then P3-post: `resolve_projects_parent` → 6, `import bellows_root` → 1 in `tests/test_plan_claim.py`; `"awaiting_verdict"` → 7 and `2 * 3 * 5` → 1 in `tests/test_gate_watcher.py`; `"$PY" -m py_compile` both files.
>
> **A3 — tests.** `"$PY" -m pytest -q -p no:cacheprovider tests/test_plan_claim.py` → `49 passed` (no FAILED line — the same 49, the four now passing under the condition that failed them); `"$PY" -m pytest -q -p no:cacheprovider tests/test_gate_watcher.py` → no FAILED line and a pass count exactly 6 above A1's pre-edit count (P3b — the six new cells ran; a skip of the live-DB test is a location property — state it); `"$PY" -m pytest -q -p no:cacheprovider tests/test_governance_root.py` → `12 passed`. Then the full suite from your worktree (P6): no `FAILED` line; state `N passed` with N at or above P6's floor (measured at walk 0); if any id fails, re-run that one file once and report FLAKE-PASSED-ON-RERUN or HALT.
>
> **A4 — dev-log + commit by explicit pathspec.** Write `knowledge/development/dev-log-seam-tests-2026-09-01.md`: A1's measured pins, the three anchor counts, P3 post, the A3 summary lines verbatim, the worktree path and the projects-parent line. Then `git add tests/test_plan_claim.py tests/test_gate_watcher.py knowledge/development/dev-log-seam-tests-2026-09-01.md && git commit -m "[<id from your plan filename>] seam tests hide the projects parent (six sites); gate_watcher test STATE gains awaiting_verdict" -- tests/test_plan_claim.py tests/test_gate_watcher.py knowledge/development/dev-log-seam-tests-2026-09-01.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-seam-tests-2026-09-01.md`
> - `tests/test_plan_claim.py`
> - `tests/test_gate_watcher.py`
>
> **Scope:**
> - `knowledge/development/dev-log-seam-tests-2026-09-01.md`
> - `tests/test_plan_claim.py`
> - `tests/test_gate_watcher.py`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the Bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; re-derive `PY` as in A0.
>
> **(A) Rule 20 self-check** — the canonical block from **`"$("$PY" -c "import bellows_root as b; print(b.resolve_governance_root())")/RULE_20_SELF_CHECK_BLOCK.md"`** — ⚠️ the dispatcher's injected mandate (this daemon still runs pre-100011 code until the CEO's restart) names the SHOP's path; quote in your report the path the mandate GAVE you and the path you USED. Run with:
> - `plan_slug`: `seam-tests-projects-parent-2026-09-01`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/seam-tests-2026-09-01/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/seam-tests-2026-09-01"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-seam-tests.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt` (`mkdir -p` the evidence dir first):**
> - **Item 1 — the edits are what the plan says:** `/usr/bin/grep -cF -- 'monkeypatch.setattr(bellows_root, "resolve_projects_parent"' tests/test_plan_claim.py` → 6; `/usr/bin/grep -cF -- 'import bellows_root' tests/test_plan_claim.py` → 1; `/usr/bin/grep -cF -- '"awaiting_verdict"' tests/test_gate_watcher.py` → 9; `/usr/bin/grep -cF -- '2 * 3 * 5' tests/test_gate_watcher.py` → 1; `"$PY" -m pytest -q -p no:cacheprovider tests/test_gate_watcher.py -k "behaves_as_classified and awaiting_verdict"` → `6 passed` (the six cells, by id); `git show --stat HEAD --format=` lists exactly the three declared paths.
> - **Item 2 — the seam is really hidden, not merely passing:** `"$PY" -c "import bellows_root as b; print(b.resolve_projects_parent())"` → `/Users/marklehn/Developer` (your worktree resolves the canonical parent — the very condition that failed the four tests pre-edit); then `"$PY" -m pytest -q -p no:cacheprovider tests/test_plan_claim.py -k "unresolvable or advisory_checkout_none or both_none or call_time"` → `4 passed` (exactly the four ids — measured at walk 0: a looser `checkout_none` also selects `test_required_checkout_none`, five) — they pass UNDER the condition that failed them, because they now hide the third source.
> - **Item 3 — the full suite with the CONTROL COMPARISON (P6):** `"$PY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/seam-tests-2026-09-01/full-suite-seam-tests.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/seam-tests-2026-09-01/full-suite-seam-tests.txt`; the `FAILED` set must be EMPTY (the CWD survivor cannot appear in a worktree — if it does, HALT: you are not in one); any other id → re-run that file once, FLAKE-PASSED-ON-RERUN or Critical; state N (at or above P6's floor, measured at walk 0) and the skip count.
> - **Item 4 — 100011's proof re-affirmed on main (three lines, both ways):** `env -u ELUVIAN_WRAP_ROOT "$PY" -c "import bellows_root as b, plan_claim, gates; print(b.resolve_governance_root()); print(b.resolve_projects_parent()); print(plan_claim._tuyere_checkout()); print('Developer/GitHub' in gates.QA_MANDATE_SUFFIX)"` and the same with the variable → identical: `/Users/marklehn/Developer/eluvian-governance`, `/Users/marklehn/Developer`, `/Users/marklehn/Developer/tuyere`, `False`.
> - **Item 5 — residual-literal sweep on main (100011's Item 5, options before `--`):** `/usr/bin/grep -rlF --include='*.py' --exclude-dir=.venv --exclude-dir=.git --exclude-dir=knowledge --exclude-dir=tests --exclude-dir=hooks --exclude-dir=.bellows-worktrees --exclude-dir=.bellows-cache -- '/Users/marklehn/Developer/GitHub' .; echo "exit=$?"` → no files, `exit=1`; liveness pair `/usr/bin/grep -cF -- 'Developer/GitHub' bellows_root.py` → 1.
>
> **(C) The report** `qa-receipt.md`: the verification table, the Restart Discipline note (pre-fix daemon; the CEO's restart; the first QA step after it quotes its received mandate path), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/seam-tests-2026-09-01/ && git commit -m "[<id>] QA: seam tests hide the projects parent — four ids pass under the failing condition; full suite empty set in the worktree" -- knowledge/qa/evidence/seam-tests-2026-09-01/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/seam-tests-2026-09-01/qa-receipt.md`
> - `knowledge/qa/evidence/seam-tests-2026-09-01/probes-raw.txt`
> - `knowledge/qa/evidence/seam-tests-2026-09-01/full-suite-seam-tests.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/seam-tests-2026-09-01/qa-receipt.md`
> - `knowledge/qa/evidence/seam-tests-2026-09-01/probes-raw.txt`
> - `knowledge/qa/evidence/seam-tests-2026-09-01/full-suite-seam-tests.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Drafting Cycle

**Tier:** T1 — T-1 and T-8 fire; no T2 trigger. Five-lens walk, no panel; scout not convened (every claim above is a measured line from 100011's pause).

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-de-hardcode-2026-09-01.md

**Walk 0 (context pin, measured):** the two target shas P1 at bellows `6b892a3`; the three anchors counted (P2 — one deliberately count 6, all six named by line and test); the six tests read at source (which of them fail and why the other two pass); the STATE tuple read at `tests/test_gate_watcher.py:244` and the tool's own phase classification read at `tools/gate_watcher.py:104/110/222`; the seam measured under both projects parents; the consumer dry-run (§2.0): `plan_lint` at a faithful mirror, `cycle_check`, the class assigner on the declared writes, the deposit extractor — results on the register's child section.

**Direction verdict (after walk 1): PROCEED.** Tested: the mechanism (three anchored edits in two test files, no code), the premise (measured at 100011's pause and re-measured after its halt), the scope (100011's code stays; the tests learn the third source).

**Walks:**
- Weak spots:          w1 1 folded — instruction 1 / record 0 (Item 2's `-k "… checkout_none …"` selected FIVE tests, `test_required_checkout_none` included, against an expected `4 passed` — measured with `--collect-only`; tightened to `advisory_checkout_none`, exactly the four)
- Destruction:         w1 dry — nothing destructive: three insertions in two test files, `git revert` restores; E3 TIGHTENS the state-space (six cells now asserted where none were); the code under test is untouched; a wrong E3b derivation fails in A3 (each cell RUNS against `read_state`), never in production
- Vulnerabilities:     w1 dry — no loops (no zsh-array hazard), no scratch variables, absolute Rule 20 paths from the start; A1 asserts the worktree resolves the CANONICAL parent (the four must FAIL pre-edit there) and HALTS otherwise — the location-of-probe trap that took 100011 is a stated precondition here
- Integration-record:  w1 3 folded — instruction 0 / record 3 (the manifest's placeholder `class: pending` → `shop-infra`, the depositor's measured assignment; the verdict file cited as `verdict-100011-step-1.md` had been renamed `processed-verdict-…` by the daemon — (o1) caught it; P6's floor restated three times unqualified — `propagation_check` 3 → 0). Walk-0 corrections stated in their rows (P3's pre-count 0 → 2; P4's 51/55 → 45/49)
- ACID:                w1 dry — one DEV commit of three paths by explicit pathspec, one QA commit of the evidence dir; the tests' three sources hidden together or not at all (MUST-PRESERVE)
- **Walk 1 total: 4 findings, 4 folded — instruction 1 / record 3; 0 of 4 fold-introduced.**
- Weak spots:          w2 dry — instruction 0 / record 0 — the three edits re-read as written; E2's insertion indentation stated; E3b's comment line stated
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — the four `-k` ids re-listed with `--collect-only`
- Integration-record:  w2 dry — instruction 0 / record 0 — `propagation_check` clean; the manifest below is the emitter's, spliced at the freeze
- ACID:                w2 dry — instruction 0 / record 0 — unchanged requirement set
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 1 → 0.

**Conformance (§5):** first run at walk 0 (shape-stability) and re-run after walk 1 and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×9 (worktree-relative deposits, the parent's convention) and the advisory (t) detector heuristic on `tests/test_gate_watcher.py`'s basename (left undeclared deliberately: this plan edits a test's classification TABLE, it declares no detector); `cycle_check` BAR_MET; `fold_check` baseline saved; `propagation_check` exit 0.

**Closing:** ✅ **BAR MET — walk 2 dry (all five lenses) after walk 1's four folds; T1, no panel owed, none convened.** Substrate present (the register's child section committed at each phase; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: tests/test_plan_claim.py, tests/test_gate_watcher.py
class: shop-infra
reads: /Users/marklehn/Developer/bellows/tests/test_plan_claim.py, /Users/marklehn/Developer/bellows/tests/test_gate_watcher.py, /Users/marklehn/Developer/bellows/plan_claim.py, /Users/marklehn/Developer/bellows/tools/gate_watcher.py, /Users/marklehn/Developer/bellows/verdicts/resolved/processed-verdict-100011-step-1.md
writes: tests/test_plan_claim.py, tests/test_gate_watcher.py, knowledge/development/dev-log-seam-tests-2026-09-01.md, knowledge/qa/evidence/seam-tests-2026-09-01/qa-receipt.md, knowledge/qa/evidence/seam-tests-2026-09-01/probes-raw.txt, knowledge/qa/evidence/seam-tests-2026-09-01/full-suite-seam-tests.txt
open_forks: none
walks: 0
yields: 0
validation: cycle_check=PENDING, plan_lint=PENDING, fold_check=PENDING
coherence: 0/0 walks have register rows
