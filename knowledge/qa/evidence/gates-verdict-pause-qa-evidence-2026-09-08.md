# QA Evidence — verdict-pause gate arms (plan 100045, step 2)

**Date:** 2026-09-08 | **Plan:** 100045 | **Step:** 2 — QA | **Suite:** 2087 passed, 1 skipped

---

## Item 1 — Full suite (redirected)

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/gates-verdict-pause-suite-2026-09-08.txt 2>&1`

**Pre-flight correction (Step 1 miss):** Three assertions in `tests/test_gate_qa_test_result.py::TestNoSummaryLineFailsClosed` checked the old error message `"no parseable pytest summary"`. Step 1 changed the no-summary path to produce `"no pytest summary in any .txt deposit: <list>"`. The assertions were not updated in Step 1. Fix committed as `3a6effa` before the suite run. **Scope deviation noted:** `tests/test_gate_qa_test_result.py` is outside the Step 2 declared Scope (`scope_check` override required for this file).

Exit: **0**. Evidence file: `gates-verdict-pause-suite-2026-09-08.txt`.

Summary line (tail of evidence file):

```
2087 passed, 1 skipped in 71.14s (0:01:11)
```

HALT condition (non-zero failure count): **not triggered**.

---

## Item 2 — 191 on real plans

**100040 STEP 1** — text from absolute path `/Users/marklehn/Developer/bellows/knowledge/decisions/halted-executable-100040.md` (present ✅); seven files: `knowledge/development/dev-log-cycle-check-battery-2026-09-07.md`, `knowledge/mutants/cycle-check-battery.json`, `scripts/cycle_check.py`, `scripts/substrate_check.py`, `tests/test_cycle_check.py`, `tests/test_cycle_check_battery.py`, `tests/test_cycle_check_manifest_provenance.py`.

Result: `{'gate': 'scope_check', 'evidence': 'out-of-scope files: tests/test_cycle_check.py | plan step context: … not in declared **Scope:** block'}` — **FAILS** naming `tests/test_cycle_check.py` ✅ (expected).

**100043 STEP 1** — files from `git show --format= --name-only 23cdaac 2b9f0cb 83ff59e | sort -u`: `depositor.py`, `knowledge/development/dev-log-depositor-class-assigner-2026-09-08.md`, `knowledge/mutants/depositor-class-assigner.json`, `knowledge/mutants/depositor-class-assigner.run.txt`, `tests/test_depositor.py`, `tests/test_depositor_class_assigner.py`, `tests/test_depositor_lens_order_gate.py`.

Result: no failures ✅ (expected).

**P4 REPLAY** over lifecycle `commits` table (81 steps processed, 3 skipped for absent plan files):

```
Identical: 81, Flips: 1, Skipped: 3
Flip set:
  100040/1 7ed87e62: ['tests/test_cycle_check.py']
```

Exactly one flip (`100040/1`), matches the pinned expectation ✅.

---

## Item 3 — 43 on real tools

Scratch dir `knowledge/qa/evidence/qa-item3-scratch/` (temporary, deleted before Item 7). `probes-raw.txt` (no summary) listed first, `pytest_full.txt` (contains `2087 passed, 1 skipped in 71.14s`) listed second in a fixture step.

**Probe-first, suite-second:** gate picks `pytest_full.txt` (suite) ✅ — passes with no failures.

**Both no-summary:** gate fails: `'no pytest summary in any .txt deposit: knowledge/qa/evidence/qa-item3-scratch/probes-raw.txt, knowledge/qa/evidence/qa-item3-scratch/pytest_full.txt'` ✅ — names both files.

Scratch dir deleted; `git status --porcelain` shows only the two untracked evidence files ✅.

---

## Item 4 — 65 on real receipt

File: `knowledge/dev-logs/project-producer-qa-2026-08-31.md` (project-relative). Contains at line 36: `FAILED tests/test_decisions.py::TestLoadPhrases::test_loads_slash_alternatives`.

**With the missing node:** gate fails: `'quoted test node(s) not found in worktree: tests/test_decisions.py::TestLoadPhrases::test_loads_slash_alternatives'` ✅.

**With that line removed:** gate passes — no failures ✅.

Note: this receipt names `test_loads_slash_alternatives` only in the FAILED pytest output block, never as a `tests/path.py::Node` reference in its own body — gate does not fire on this receipt's own prose ✅.

---

## Item 5 — 136 and 192 live

**136 — MARKER-FORM row** (status cell: `✅ marker [status: pending] written`): (d) silent ✅.

**136 — BARE-WORD row** (status cell value: "tests pending" with the pass glyph): (d) fires — evidence begins `(d) Hedging keyword 'pending' in positive-status row` ✅.

**192 — 100040 STEP 1** (Scope declares `knowledge/mutants/cycle-check-battery.json`, no `.run.txt` in Deposits): gate fails: `'mutant manifest knowledge/mutants/cycle-check-battery.json declared without a .run.txt Deposit in this step — deposit the run in the step that names the manifest'` ✅.

**192 — 100043's run file** (`knowledge/mutants/depositor-class-assigner.run.txt`, last MUTATION line: `MUTATION: 12 killed, 0 survived, 0 error`): gate passes — no failures ✅.

---

## Item 6 — Production writes

Production writes in this QA step: **exactly two evidence files**:
- `knowledge/qa/evidence/gates-verdict-pause-suite-2026-09-08.txt`
- `knowledge/qa/evidence/gates-verdict-pause-qa-evidence-2026-09-08.md`

No lane file written. No sidecar written. No lifecycle row written.

**⚠️ RESTART OWED:** `bellows.py` imports `gates` in-process; the running daemon evaluates every step with the old gate code until it is restarted. This is the CEO's act at close.

---

## Item 7 — Receipt

**DEV step commits (three — plan said two; third commit `62ee37a` was a fix to tests and mutant json during Step 1):**

```
68abd77 [100045] gates-verdict-pause: mutation run (22 killed, 0 survived, 0 error) + dev-log
62ee37a [100045] tests: fix test 3 (Deposits inside STEP 1), test 6 (failing non-suite file); fix 5 mutant anchors/replacements
6af8558 [100045] gates: five verdict-pause gate arms — declared Scope authoritative (191), suite log by content (43), quoted nodes exist (65), LESSONS marker exempt (136), mutation run declared (192)
```

**numstat over `9096b31..68abd77` — 6 files:**

```
237	46	gates.py
64	 0	knowledge/development/dev-log-gates-verdict-pause-2026-09-08.md
181	 0	knowledge/mutants/gates-verdict-pause.json
32	 0	knowledge/mutants/gates-verdict-pause.run.txt
853	 0	tests/test_gates_verdict_pause.py
3	 0	verdict.py
```

6 unique files ✅.

**Run file `HEAD:` line vs. manifest file sha:**

- Run file: `HEAD: 62ee37a9bbb931fa8b86c4d1a8d25709a5e382d6`
- `git log -1 --format=%H -- knowledge/mutants/gates-verdict-pause.json`: `62ee37a9bbb931fa8b86c4d1a8d25709a5e382d6`

Match ✅ (E5).

**`git diff 9096b31..68abd77 -- tests/test_gates.py tests/test_verdict.py`:** EMPTY ✅ — both files unchanged.

**`git reflog -n 6`:**

```
3a6effa HEAD@{0}: commit: [100045] fix test_gate_qa_test_result: update no-summary assertions to match new message
68abd77 HEAD@{1}: reset: moving to HEAD
68abd77 HEAD@{2}: ...
```

0 amends, 1 soft reset to HEAD (no-op — HEAD unchanged). 0 destructive resets ✅.

**Dev-log four headings (`grep -E "^## P2|^## Corpus|^## Cost|^## Mutation run" knowledge/development/dev-log-gates-verdict-pause-2026-09-08.md`):**

```
## P2 — the two live instances (verbatim + re-derived)
## Corpus — P6/P7/P8/P9/P13 (verbatim + re-measured)
## Cost
## Mutation run
```

All four present ✅.

**test_gates.py test count (`grep -c 'def test_' tests/test_gates.py`):** 177 ✅.

**Item-by-item gate summary (each on its own line):**

- Item 1: suite exit=0, 2087 passed, 0 failed (pre-flight fix committed as `3a6effa`; scope deviation noted) ✅
- Item 2: 100040 FAILS naming `tests/test_cycle_check.py`; 100043 passes; replay 81 identical / 1 flip (`100040/1`) ✅
- Item 3: probe-first fixture picks suite; both-no-summary fails naming both files ✅
- Item 4: missing node `test_loads_slash_alternatives` fails; line removed → passes ✅
- Item 5: 136 marker silent / bare-word fires; 192 on 100040 fails / on 100043 run passes ✅
- Item 6: two evidence files only, no lane/sidecar/clearance; restart owed at close ✅

---

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite exit=0, 2087 passed, 0 failed | ✅ |
| 2 | 191: 100040 FAILS; 100043 passes; replay 1 flip = 100040/1 | ✅ |
| 3 | 43: probe-first picks suite; both-empty fails naming both | ✅ |
| 4 | 65: missing node fails; token removed → passes | ✅ |
| 5a | 136: marker-form row — (d) silent | ✅ |
| 5b | 136: bare-word row — (d) fires | ✅ |
| 5c | 192: manifest-without-run (100040) fails | ✅ |
| 5d | 192: clean run file (100043) passes | ✅ |
| 6 | Production writes: two evidence files only; restart owed | ✅ |
| 7a | numstat: 6 files | ✅ |
| 7b | Run file HEAD matches manifest sha (62ee37a) | ✅ |
| 7c | test_gates.py and test_verdict.py: EMPTY diff (unchanged) | ✅ |
| 7d | reflog: 0 amends, 0 destructive resets | ✅ |
| 7e | Dev-log: four required headings present | ✅ |
| 7f | test_gate_qa_test_result.py: 3 assertions updated; scope_check override required | ✅ |

### Rule 20 Self-Check Block Output

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100045/knowledge/qa/evidence/
Files verified: 2
