# bellows — executable: the two discriminating tests the checker-defects kill map lacks — M2 (negation stripping) and M3 (the OSError guard) in `cycle_check`, with the manifest re-pointed (thread 92) — and 100023's propagation manifest split into the per-target files the mutation tool reads

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full (the four checker test files targeted first, then the whole bellows suite from the worktree) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `checker-kill-gap-2026-09-02`

**Depends on:** tuyere thread 92; plan 100022 (`checker-defects-2026-09-02`, halted 2026-09-02 16:55 at QA on its own Item 2.5 — the fixes are on main at bellows `e088d05`, verified: fail-before/pass-after 12/12, corpus canaries 19/19 BAR_MET, the five fixtures as pinned, suite `1782 passed`; the debt is coverage, not code); Rule 106 (the kill map: a mutant that survives is a missing test); the CEO, 2026-09-02 ("Let's proceed on these as though it were night").

**Tier computed, not judged (§1):** **T-8 fires** (a clone by kind of 100022's test half, narrowed to two cells of its own state space; 100022 did not close, so this is not a structure-for-structure clone of a verified plan). T-1 no (one subsystem: `bellows/tests` and one manifest). T-6 no (no doctrine, no gate, no script). T-2/T-3/T-5/T-7 no. → **T1: five-lens walk, no panel, no scout** (both gaps are reproduced below by fixtures run against scratch copies of the mutated script — the discrimination is measured, not argued).

## Why this exists — two survivors, each measured on this machine

`tools/mutation_check.py` on the committed code (bellows `e088d05`, re-run by the Planner and by 100022's QA) scores `knowledge/mutants/checker-defects-cycle_check.json` **M1 KILLED, M2 SURVIVED, M3 SURVIVED, M4 KILLED**; the `cycle_yields` and `plan_lint` manifests score 1/0 and 2/0. The two named tests are decorative for their mutants:

- **M2 — `M2-drop-negation-stripping`** (`stripped = _NEGATION_RE.sub("", block_text)` → `stripped = block_text`). Its named test `test_58_not_closed_returns_continue` closes with `**Closing:** NOT CLOSED at walk 2 — the bar is not met.` — a text in which **no claim token appears even unstripped** (`_CLAIM_RE` is `BAR MET | met the bar | CYCLE COMPLETE`; measured: the claim search on that text is False with and without the stripping). The stripping is load-bearing only where a negation phrase and a claim token OVERLAP: `\bnot\s+met\b` removed from `has not met the bar` leaves ` the bar` (no claim); unstripped, `met the bar` matches. So the discriminating closing line is **`**Closing:** has not met the bar at walk 2 — one lens still folding.`** — CONTINUE under the live script, `ESCALATE:claimed-close-unmet` under M2 (measured on a scratch copy with the mutant's replacement applied). ⚠️ The QA's suggested `NOT BAR MET` does NOT discriminate: `_NEGATION_RE` strips `NOT CLOSED` / `NOT MET` / `not met` / `unmet`, never `NOT BAR MET`, so `BAR MET` is found either way (measured: True / True).
- **M3 — `M3-drop-oserror-guard`** (the `except OSError` at the `git_root / ref` probe → `except ValueError`). Its named test `test_c2_long_component_no_traceback` puts the oversized text in trailing COMMENTARY, which the C-2 extraction now removes before `exists()` runs, so the guard is never reached and the mutant is invisible. The guard is reached when the REFERENCE ITSELF carries an oversized component: a backticked `scripts/<300 × x>.md` staged in a git root that has a `scripts/` directory makes `(git_root / ref).exists()` raise `OSError: [Errno 63] File name too long` (measured). Under the live script that reads **`ESCALATE:assert-fail:2`** (the guard turns it into `UNRESOLVED`); under M3 the checker dies with the traceback (measured on a scratch copy).

**And a third debt of the same kind, from plan 100023 (`propagation-check-pin-forms`, its Step 1 merged at bellows `2bbdd09`):** its `knowledge/mutants/propagation-check.json` carries a `target` INSIDE each of its four mutants and no top-level `target`; `tools/mutation_check.py` reads only the top-level key (`manifest.get("target")`, :100–103) and refuses the file — `ERROR: manifest must have 'target' and non-empty 'mutants'` (measured on main). Its kill map cannot run as committed. The four mutants are sound (each anchor occurs exactly once in its target; the four selectors collect and pass — measured); only the file shape is wrong. The tool's contract is one target per manifest, so the fix is three per-target manifests.

## What this plan does

**F1 — `tests/test_cycle_check.py` gains two tests**, appended after `test_58_negation_unmet_not_a_claim` and after `test_c2_long_component_no_traceback` respectively, each with a one-line comment naming thread 92 and its mutant:
- `test_58_negated_claim_phrase_stripped_continue` — `_make_plan` with two non-dry lenses (`- Weak spots: w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 1 / record 0.` and `- Destruction: w1 dry; w2 dry.`), **no `**Walk register:**` line** (as the 58 group's fixtures have none — assert 2 then reads N/A and only the closure decides; with a relative register line the fixture in a non-git `tmp_path` reads `ESCALATE:assert-fail:2` whatever the closure says, measured), and the closing line `**Closing:** has not met the bar at walk 2 — one lens still folding.` → `cycle_check.run_check(plan)` returns `("CONTINUE", 0)`.
- `test_c2_oversized_backticked_ref_escalates_no_traceback` — a tmp git repo (`git init`) with a `scripts/` directory and a plan whose register line is `` **Walk register:** `scripts/<"x" * 300>.md` `` with the same two lens lines and `**Closing:** NOT CLOSED at walk 2.` → `cycle_check.run_check(plan)` returns `("ESCALATE:assert-fail:2", 1)` **in-process** (no subprocess: under M3 the call raises and the test errors, which is what kills the mutant).

**F2 — `knowledge/mutants/checker-defects-cycle_check.json`:** M2's `expect_fail` → `tests/test_cycle_check.py::test_58_negated_claim_phrase_stripped_continue`; M3's `expect_fail` → `tests/test_cycle_check.py::test_c2_oversized_backticked_ref_escalates_no_traceback`. M1, M4 and the `why` texts untouched except one appended sentence on each of M2/M3 naming why the earlier test was decorative.

**F3 — `knowledge/mutants/propagation-check.json` split into three per-target manifests**, each with a top-level `target` and the mutants that target it, every mutant's `name`, `why`, `anchor`, `replacement`, `expect_fail` copied byte-for-byte and its per-mutant `target` key dropped: `knowledge/mutants/propagation-check-propagation_check.json` (`target: scripts/propagation_check.py`; M1-hex-exclusion-removed, M2-row-id-fallback-removed) · `knowledge/mutants/propagation-check-run_check.json` (`target: tools/run_check.py`; M3-judge-propagation-rc2-as-pass) · `knowledge/mutants/propagation-check-cycle_check.json` (`target: scripts/cycle_check.py`; M4-manifest-propagation-pair-dropped). The combined file is removed with `git rm`. Prove the copy: a short python loads the old file and the three new ones and asserts the multiset of `(name, anchor, replacement, expect_fail)` is identical and each new file's `target` equals the dropped per-mutant `target` of every mutant in it.

**F4 —** no script changes. The two earlier `cycle_check` tests stay (they are true, only non-discriminating).

## What this plan does NOT do

- Does not touch `scripts/`, `gates.py`, the daemon, the depositor, doctrine, or the template. Does not remove the M3 guard (100022's QA called it "largely dead code" — it is reached by the oversized-reference form above, so it stays and is now tested). Does not close threads 52/58/63/77/92 (a keyboard act after QA).
- ⚠️ **Runs AFTER `propagation-check-pin-forms` closes** — both plans write `tests/test_cycle_check.py`; the depositor's write-set collision holds this plan until then, and P1/P2/P5 are RE-DERIVED at claim for that reason.

## MUST-PRESERVE

- **No script changes:** `git diff --name-only <Step 1 commit>~1 <Step 1 commit>` is exactly the seven paths (the test file, the `cycle_check` manifest, the removed combined propagation manifest, the three per-target propagation manifests, the dev log); the checker scripts' shas after equal the claim-time P1.
- **The four propagation mutants survive the split byte-for-byte** (the F3 multiset proof, quoted).
- **Additions only in the test file:** `git diff --numstat` for `tests/test_cycle_check.py` shows 0 deletions.
- **Every mutant killed:** the three manifests → `SURVIVED` 0, `ERROR` 0, and the baseline green for every selector.
- **Worktree discipline:** your cwd IS the claimed tree; `git add` by explicit pathspec; agents do not push; do NOT rename the plan file.
- **`known_failures: 0`.** From the worktree under the canonical venv the suite is `1782 passed, 1 skipped` today plus whatever `propagation-check-pin-forms` adds; after this plan, plus 2. Any failure is a HALT/Critical.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner at bellows `31e0a58`)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`SRC`** — shas, pre-edit — RE-DERIVE AT CLAIM (`propagation-check-pin-forms` lands first and writes `cycle_check.py` and the test file; state the shas you find and that they differ from these where that plan wrote) | `scripts/cycle_check.py` `2b66c914c6a484da` · `tests/test_cycle_check.py` `479a73f7d8984f1c` · `knowledge/mutants/checker-defects-cycle_check.json` `12c9fc2940d812f0` | `shasum -a 256 <f> \| cut -c1-16` |
| P2 | **`TESTS`** — the four checker test files, pre-edit — RE-DERIVE | `316 passed` today | `BPY -m pytest tests/test_cycle_check.py tests/test_cycle_yields.py tests/test_plan_lint.py tests/test_plan_lint_detector_checks.py -q -p no:cacheprovider` |
| P3 | **`KILLMAP_BEFORE`** — the four manifests on HEAD before this plan's commit | `checker-defects-cycle_check`: M1 KILLED, M2 SURVIVED, M3 SURVIVED, M4 KILLED (`2 killed, 2 survived, 0 error`) · `checker-defects-cycle_yields`: `1 killed, 0 survived, 0 error` · `checker-defects-plan_lint`: `2 killed, 0 survived, 0 error` · `propagation-check.json`: the tool REFUSES it — `ERROR: manifest must have 'target' and non-empty 'mutants'` (no scoring lines) | `BPY tools/mutation_check.py <manifest>` — the tool reads COMMITTED code (HEAD) |
| P3b | **`PROP_MUTANTS`** — the four propagation mutants as committed by 100023 | 4 mutants; per-mutant targets `scripts/propagation_check.py` ×2, `tools/run_check.py` ×1, `scripts/cycle_check.py` ×1; each `anchor` occurs exactly once in its target; the four `expect_fail` selectors collect and pass (`4 passed`) | a short python over the json; `BPY -m pytest <the four node ids> -q -p no:cacheprovider` |
| P4 | **`FIXTURES`** — the two texts (verbatim in the register's M6) against the live script and against a scratch copy carrying the mutant's replacement | `negclaim` (no register line; in a plain directory, not a git root): live `CONTINUE` · M2-copy `ESCALATE:claimed-close-unmet` · M3-copy `CONTINUE` · `longref3` (staged in a tmp git root with `scripts/`): live `ESCALATE:assert-fail:2` · M2-copy `ESCALATE:assert-fail:2` · M3-copy `OSError: [Errno 63] File name too long` (a traceback, 2 lines matching `Traceback\|OSError`) — each fixture flips exactly its own mutant | copy `scripts/cycle_check.py` + `scripts/cycle_yields.py` to `/tmp/ckg/m2/` and `/tmp/ckg/m3/`; apply each mutant's `anchor` → `replacement` (assert the anchor occurs exactly once); `BPY <copy>/cycle_check.py <fixture>`; the verdict is the last stdout line |
| P5 | **`SUITE`** — from the worktree under the canonical venv — RE-DERIVE | `1782 passed, 1 skipped`, exit 0 today | `BPY -m pytest tests -q -p no:cacheprovider` |
| P6 | **`ANCHORS`** — the two `expect_fail` strings to replace, each exactly once in the manifest | `tests/test_cycle_check.py::test_58_not_closed_returns_continue` · `tests/test_cycle_check.py::test_c2_long_component_no_traceback` | `/usr/bin/grep -cF` |

## Drafting Cycle

**Tier:** T1 — T-8 fires (a clone by kind of 100022's test half, narrowed to two cells); T-6 no; no panel, no scout (both gaps reproduced by fixtures run against scratch copies of the mutated script).

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-checker-kill-gap-2026-09-02.md

**Walk 0 (context pin, measured):** the kill map re-run on `e088d05` (2/2/0 · 1/0/0 · 2/0/0); the two regexes read at their lines and the overlap that makes the stripping load-bearing found by probing `_CLAIM_RE` and `_has_closure_claim` on candidate texts (the QA's `NOT BAR MET` rejected by measurement); a 300-byte component proven to raise `OSError` errno 63 on `Path.exists()`; the two mutants applied to scratch copies and both fixtures run under live and mutated code (four verdicts, all pinned in P4); the test file's helper (`_make_plan`) and the module-cache guard read; the neighbouring node ids listed; the manifest's `expect_fail` anchors counted; the collision with `propagation-check-pin-forms` named.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (two survivors, each measured twice — by the Planner and by 100022's QA — and each with a fixture that flips exactly its own mutant, measured against scratch copies carrying the mutants' replacements, in-process and by CLI), the mechanism (two appended tests and two re-pointed selectors; nothing else moves), the scope (tests and one manifest; the scripts' shas are a MUST-PRESERVE).

**Walks:**
- Weak spots:          w1 2 folded — instruction 1 / record 1 (the first test's fixture carried a relative register line that, inside a non-git `tmp_path`, decides the verdict before the closure is read — dropped and re-measured; the manifest's `target_class: detector` mis-described a tests-and-manifest target — removed)
- Destruction:         w1 dry — no script changes (a MUST-PRESERVE with a `diff --name-only` proof); additions-only in the test file; the earlier two tests kept; fixtures in `tmp_path`, scratch under `/tmp/ckg/`, never a watched dir
- Vulnerabilities:     w1 dry — the mutation tool audits COMMITTED code, so the kill is QA's to measure after Step 1's commit; the DEV-side proof applies the same replacement on a scratch copy; the M3 raise escapes `run_check` in-process (its only broad `except` wraps the file read); the collision with 100023 named, the pins marked RE-DERIVE
- Integration-record:  w1 dry — the manifest is the emitter's, spliced at the freeze; the class the assigner measured; the block above the first step; the register's M6 carries the fixture texts verbatim
- ACID:                w1 dry — one DEV commit by explicit pathspec after the suite; a HALT before it leaves the worktree dirty and nothing landed; QA's commit separate
- **Walk 1 total: 2 findings, 2 folded — instruction 1 / record 1; 0 of 2 fold-introduced.**

- Weak spots:          w2 dry — instruction 0 / record 0 — the two folded sites re-read; F1's texts re-read against P4's six verdicts and the register's M6; the Cycle Log covered
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w2 dry — instruction 0 / record 0 — the manifest emitted at the freeze and spliced; `propagation_check` recorded as it ran
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 1 → 0.
- Integration-record:  w3 1 folded — instruction 1 / record 0 (after the first deposit, 100023's Step 1 landed a mutant manifest in a shape `mutation_check` refuses — a per-mutant `target`, no top-level one; the same debt class this plan discharges, measured on main; F3 splits it into three per-target manifests with a byte-for-byte multiset proof, QA's Item 1 runs all six manifests, the writes/deposits/scope widened, P3/P3b pinned)
- Weak spots:          w3 dry — instruction 0 / record 0 — the new F3, A4b, Item 1 and Item 2 re-read; the removed file is not a deposit (a deletion cannot be one) and is named in Item 1 by its absence
- Destruction:         w3 dry — instruction 0 / record 0 — the four propagation mutants' anchors measured ×1 each and their selectors passing before the split; the proof is a multiset over the four tuples
- Vulnerabilities:     w3 dry — instruction 0 / record 0 — the split is by script, not by hand: the anchors are byte-exact strings that a retyping would corrupt
- ACID:                w3 dry — instruction 0 / record 0 — the `git rm` staged with the adds, one commit
- **Walk 3 total: 1 finding, 1 folded — instruction 1 / record 0; 0 of 1 fold-introduced (a sibling plan's landing after the first deposit).**

- Weak spots:          w4 dry — instruction 0 / record 0 — the folded sites re-read; the seven-path diff contract counted against the writes line
- Destruction:         w4 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w4 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w4 dry — instruction 0 / record 0 — the manifest re-emitted; the hold withdrawn and the draft re-deposited once
- ACID:                w4 dry — instruction 0 / record 0 — unchanged
- **Walk 4 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 1 → 0 → 1 → 0.

**Conformance (§5):** first run at walk 0 (on v0) and re-run at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror (expected WARN set: (o2) worktree-relative deposits); `cycle_check` BAR_MET; `fold_check` re-baselined at each intended change with a note; **`propagation_check`: at the first freeze NOT RUN — exit 2 ("no symbol declarations parsed — detector (1) cannot run"; the pin table carries no bold `**VALUE**` cells; 100023 in flight); at the second freeze, after 100023's Step 1 landed on main, exit 1 — `DIVERGENCES: 6`, the tool's restatement findings on this draft's own numbers (quoted in the register, not judged; the emitter's new pair `propagation_check=DIVERGENT:6` spliced).**

**Closing:** ✅ **BAR MET — walk 4 dry (all five lenses) after walk 1's two folds and walk 3's one (a sibling plan's landing); T1, no panel owed, none convened.** Substrate present (the register's rows entered from captured output and committed at the freeze; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: tests/test_cycle_check.py, knowledge/mutants/checker-defects-cycle_check.json, knowledge/mutants/propagation-check.json
class: shop-infra
state_space: the two surviving cells of 100022's state space — closing form {a negation phrase overlapping a claim token: `has not met the bar`} × register reference {a backticked component over 255 bytes, reaching `exists()`} — read from the SYSTEM (`_NEGATION_RE` / `_CLAIM_RE` at `cycle_check.py:40–41`; the `git_root / ref` probe at :281; `mutation_check`'s scoring: only pytest exit 1 is KILLED)
mutants: knowledge/mutants/checker-defects-cycle_check.json, knowledge/mutants/propagation-check-propagation_check.json, knowledge/mutants/propagation-check-run_check.json, knowledge/mutants/propagation-check-cycle_check.json
reads: /Users/marklehn/Developer/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/bellows/tests/test_cycle_check.py, /Users/marklehn/Developer/bellows/knowledge/mutants/checker-defects-cycle_check.json, /Users/marklehn/Developer/bellows/knowledge/mutants/propagation-check.json, /Users/marklehn/Developer/bellows/tools/mutation_check.py, /Users/marklehn/Developer/bellows/knowledge/qa/evidence/checker-defects-2026-09-02/qa-receipt.md
writes: tests/test_cycle_check.py, knowledge/mutants/checker-defects-cycle_check.json, knowledge/mutants/propagation-check.json, knowledge/mutants/propagation-check-propagation_check.json, knowledge/mutants/propagation-check-run_check.json, knowledge/mutants/propagation-check-cycle_check.json, knowledge/development/dev-log-checker-kill-gap-2026-09-02.md, knowledge/qa/evidence/checker-kill-gap-2026-09-02/qa-receipt.md, knowledge/qa/evidence/checker-kill-gap-2026-09-02/probes-raw.txt, knowledge/qa/evidence/checker-kill-gap-2026-09-02/full-suite-checker-kill-gap.txt
open_forks: whether `mutation_check` should also treat pytest exit 2 (collection/runtime error) as KILLED for an in-process raise — today a raise inside a test scores as exit 1 (a failed test), which is what this plan relies on; the four threads' closure at the keyboard
walks: 4
yields: 1, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:6
coherence: 4/4 walks have register rows


---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer. `cd "$(git rev-parse --show-toplevel)" && [ -f scripts/cycle_check.py ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` (re-derive per compound).
>
> ⛔ **A1 — re-derive P1 (state the shas found; where `propagation-check-pin-forms` wrote, they differ from the table and you say so), P2, P3 (run the four manifests with `"$BPY" tools/mutation_check.py <manifest>`; quote every scoring line; exactly M2 and M3 of the `cycle_check` manifest must read SURVIVED, every other scored mutant KILLED, and `propagation-check.json` must be REFUSED with the ERROR line quoted — anything else is a HALT quoting the lines), P3b (the four anchors ×1, the four selectors `4 passed`), P5, P6 (each anchor exactly once).**
>
> **A2 — P4, the discrimination proof BEFORE any edit:** `mkdir -p /tmp/ckg/m2 /tmp/ckg/m3`; copy `scripts/cycle_check.py` and `scripts/cycle_yields.py` into each; with a short python, read M2's `anchor` and `replacement` from the manifest, assert the anchor occurs exactly once in `/tmp/ckg/m2/cycle_check.py`, replace; the same for M3 into `/tmp/ckg/m3/`. Write the two fixture texts from the register's M4 verbatim to `/tmp/ckg/negclaim.md` and, for `longref3`, into a fresh `git init` root `/tmp/ckg/repo/` that has an empty `scripts/` directory (the file's register line names `scripts/` + 300 `x` + `.md` in backticks). Run each fixture under `scripts/cycle_check.py`, `/tmp/ckg/m2/cycle_check.py` and `/tmp/ckg/m3/cycle_check.py`; quote the six last-lines; they must match P4 exactly (the M3 line on `longref3` begins `OSError: [Errno 63]`).
>
> **A3 — F1:** the two tests, appended at the places F1 names, built exactly on the fixture texts (the `longref3` test creates its own tmp git root with `git init` and `scripts/`, as `test_c2_long_component_no_traceback` does, but calls `cycle_check.run_check(plan)` in-process and asserts the tuple). Targeted run of the four checker files → `P2 + 2 passed`; list the two new node ids.
>
> **A4 — F2:** re-point M2's and M3's `expect_fail` to the two new node ids (each replacement exactly once — P6); append one sentence to each `why`. `"$BPY" -c 'import json; json.load(open("knowledge/mutants/checker-defects-cycle_check.json"))'` → parses.
>
> **A4b — F3:** write the three per-target manifests from the combined file by a short python (never by hand-retyping — the anchors are byte-exact); run the multiset proof F3 names and quote its output; `git rm knowledge/mutants/propagation-check.json`; each new file parses (`json.load`).
>
> **A5 — full suite + dev log + commit.** `"$BPY" -m pytest tests -q -p no:cacheprovider` → `P5 + 2 passed, 1 skipped`, exit 0. `knowledge/development/dev-log-checker-kill-gap-2026-09-02.md`: the pins as found, the six P4 lines, the two node ids, the F3 proof, the suite line. `git add tests/test_cycle_check.py knowledge/mutants/checker-defects-cycle_check.json knowledge/mutants/propagation-check-propagation_check.json knowledge/mutants/propagation-check-run_check.json knowledge/mutants/propagation-check-cycle_check.json knowledge/development/dev-log-checker-kill-gap-2026-09-02.md && git commit -m "[<id>] checker-kill-gap-2026-09-02: the two discriminating tests (M2 negation overlap, M3 oversized backticked ref); manifests re-pointed; 100023's propagation manifest split per target (thread 92)"` (the `git rm` is already staged). `git diff --name-only HEAD~1 HEAD` → exactly the seven paths, quoted. Receipt `Status: Complete`.
>
> **Deposits:**
> - `knowledge/development/dev-log-checker-kill-gap-2026-09-02.md`
> - `tests/test_cycle_check.py`
> - `knowledge/mutants/checker-defects-cycle_check.json`
> - `knowledge/mutants/propagation-check-propagation_check.json`
> - `knowledge/mutants/propagation-check-run_check.json`
> - `knowledge/mutants/propagation-check-cycle_check.json`
>
> **Scope:**
> - `knowledge/development/dev-log-checker-kill-gap-2026-09-02.md`
> - `tests/test_cycle_check.py`
> - `knowledge/mutants/`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `checker-kill-gap-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/checker-kill-gap-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/checker-kill-gap-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-checker-kill-gap.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt`:**
> - **Item 1 — the kill map (Rule 106), on HEAD = Step 1's commit:** `"$BPY" tools/mutation_check.py <manifest>` for all SIX manifests — `checker-defects-cycle_check`, `checker-defects-cycle_yields`, `checker-defects-plan_lint`, `propagation-check-propagation_check`, `propagation-check-run_check`, `propagation-check-cycle_check` — every mutant `KILLED`, `SURVIVED` 0, `ERROR` 0, every baseline green (quote each scoring line and each `MUTATION:` line). A survivor or a refused manifest is a Critical finding, never a note. `ls knowledge/mutants/ \| /usr/bin/grep -c 'propagation-check.json'` → 0.
> - **Item 2 — nothing but tests and manifests moved:** `git diff --name-only HEAD~1 HEAD` → exactly the seven paths (`tests/test_cycle_check.py`, `knowledge/mutants/checker-defects-cycle_check.json`, `knowledge/mutants/propagation-check.json`, the three `knowledge/mutants/propagation-check-*.json`, `knowledge/development/dev-log-checker-kill-gap-2026-09-02.md`); `git diff --numstat HEAD~1 HEAD -- tests/test_cycle_check.py` → deletions 0; the checker scripts' shas equal Step 1's dev log P1; the F3 multiset proof re-run against `git show HEAD~1:knowledge/mutants/propagation-check.json` → identical.
> - **Item 3 — the two new node ids by name:** `"$BPY" -m pytest tests/test_cycle_check.py -q -p no:cacheprovider -k "negated_claim_phrase or oversized_backticked"` → `2 passed`.
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/checker-kill-gap-2026-09-02/full-suite-checker-kill-gap.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/checker-kill-gap-2026-09-02/full-suite-checker-kill-gap.txt` → the file carries `exit=0` and a summary with 0 failed.
>
> **(C) The report** `qa-receipt.md`: the verification table — status cells carry the glyph only, and NO positive row quotes a probe token or an output line carrying a Rule 20 hedging keyword (`hedging_keywords` in the canonical block — `skipped` among them: the suite summary line is out; rows name the FILE, the exit, and a count) — the follow-ups (the daemon restart owed since 100022; threads 52, 58, 63, 77, 92 closed at the keyboard), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/checker-kill-gap-2026-09-02/ && git commit -m "[<id>] QA: checker kill gap — kill map 4/4, 1/1, 2/2; tests-only diff; full suite"`.
>
> **Deposits:**
> - `knowledge/qa/evidence/checker-kill-gap-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/checker-kill-gap-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/checker-kill-gap-2026-09-02/full-suite-checker-kill-gap.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/checker-kill-gap-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/checker-kill-gap-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/checker-kill-gap-2026-09-02/full-suite-checker-kill-gap.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
