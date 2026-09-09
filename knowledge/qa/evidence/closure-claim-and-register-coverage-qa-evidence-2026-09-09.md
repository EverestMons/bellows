# QA Receipt — closure-claim-and-register-coverage — 2026-09-09

**Plan:** executable-100053 — A closure claim with no walk data ESCALATES; walk register lint gains COVERAGE verdict (ruling 213, ruling 215, closing thread 135)
**Step:** 2 (QA)
**Date:** 2026-09-09
**Interpreter:** `/Users/marklehn/Developer/bellows/.venv/bin/python`
**Tree root:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100053`

---

## DEV commit numstat

Base: `612d6fe` (session wrap, parent of Item 5 commit)
Dev: `99d24c1` (last DEV commit)

```
git diff --numstat 612d6fe..99d24c1
156	0	knowledge/development/dev-log-closure-claim-and-register-coverage-2026-09-09.md
20	0	knowledge/mutants/closure-claim-cycle_check.json
10	0	knowledge/mutants/closure-claim-cycle_check.run.txt
13	0	knowledge/mutants/register-coverage-run_check.json
9	0	knowledge/mutants/register-coverage-run_check.run.txt
41	0	knowledge/mutants/register-coverage-walk_register_lint.json
13	0	knowledge/mutants/register-coverage-walk_register_lint.run.txt
8	9	scripts/cycle_check.py
2	2	scripts/substrate_check.py
148	14	scripts/walk_register_lint.py
22	8	tests/test_cycle_check.py
61	23	tests/test_cycle_check_empty_body_silence.py
442	0	tests/test_register_coverage.py
24	9	tests/test_run_check.py
11	0	tests/test_substrate_check.py
10	10	tests/test_walk_register_lint.py
16	11	tools/run_check.py
```

**Count: 17** — plan declared 16. The 17th file is `tests/test_substrate_check.py` (11 insertions), modified in commit `410bcd0` to add worktree-isolation import logic (`sys.modules` eviction of the old `substrate_check` before re-importing from the worktree). This file is in the plan's reads list but not its writes list — a scope deviation. The modification is operationally required for worktree test isolation and does not change the test's assertions; the suite passes with 2145 tests.

---

## Run file HEAD: vs manifest sha

```
closure-claim-cycle_check.run.txt:     HEAD: 54e8b850fc7cddf7edb67e8469b5de2f712a2c79
register-coverage-walk_register_lint.run.txt: HEAD: 410bcd0bcccf50dc348af2e7a6f6e1beca259167
register-coverage-run_check.run.txt:   HEAD: df6acd35081d5cb3eb41ff3776274e0d3c081ae4

git log -1 --format=%H -- knowledge/mutants/closure-claim-cycle_check.json:
54e8b850fc7cddf7edb67e8469b5de2f712a2c79  ← matches

git log -1 --format=%H -- knowledge/mutants/register-coverage-walk_register_lint.json:
410bcd0bcccf50dc348af2e7a6f6e1beca259167  ← matches

git log -1 --format=%H -- knowledge/mutants/register-coverage-run_check.json:
df6acd35081d5cb3eb41ff3776274e0d3c081ae4  ← matches
```

All three HEAD: shas match their manifest's last-touch commit.

---

## git diff on declared-unchanged test files

```
git diff 612d6fe..99d24c1 -- tests/test_substrate_check.py tests/test_cycle_check_t0_close.py tests/test_cycle_check_register_resolver.py
```

- `tests/test_substrate_check.py`: **NON-EMPTY** — 11 lines added (worktree isolation block; see numstat deviation above). Commit `410bcd0`.
- `tests/test_cycle_check_t0_close.py`: EMPTY (unchanged)
- `tests/test_cycle_check_register_resolver.py`: EMPTY (unchanged)

---

## git reflog -n 8

```
99d24c1 HEAD@{0}: reset: moving to HEAD
99d24c1 HEAD@{1}: (commit)
```

0 amends, 0 resets to prior state. The `reset: moving to HEAD` is a no-op reset (same sha).

---

## Five dev-log headings grepped

```
grep "^## " knowledge/development/dev-log-closure-claim-and-register-coverage-2026-09-09.md
## Pins re-derived (P1, P2, P3, P6)
## Failing-first (the sibling and the two rewritten files red, then green)
## Mutation runs (three manifests)
## Corpus replay
## Cost
```

All five declared headings present.

---

## Mutation run lines

```
closure-claim-cycle_check.run.txt:          MUTATION: 2 killed, 0 survived, 0 error
register-coverage-walk_register_lint.run.txt: MUTATION: 5 killed, 0 survived, 0 error
register-coverage-run_check.run.txt:        MUTATION: 1 killed, 0 survived, 0 error
```

---

## Item 1 — Full suite

File: `knowledge/qa/evidence/closure-claim-and-register-coverage-suite-2026-09-09.txt`

Result: `2145 passed, 1 skipped in 75.56s` — PASS.

---

## Item 2 — 213 on real plans

**Probe A:** `executable-432.md` (governance Done) — existing ESCALATE path
```
ESCALATE:unparseable
```
Correct. Unchanged from pre-change behavior (unparseable check precedes new check).

**Probe B:** scratch copy of `executable-100009.md` with walk lines deleted, closing line kept — new empty-walk closure check
```
WARN: walk register 'walk-register-verdict-signal-2026-09-01.md' carries 11 findings row(s) but the Cycle Log's Walks block declares NO walks — the verdict below is computed from an empty record. Write the per-lens lines into the plan BODY (thread 141).
ESCALATE:claimed-close-unmet
```
Correct. New ruling-213 arm fires after T0 arm and before CONTINUE return.

**Probe C:** scratch T0 plan claiming closure without integration-vs-record result
```
WARN: declares T0 but states no integration-vs-record result — DRAFTING_CYCLE §3 collapses a T0 Cycle Log to `**cycle_tier:** T0 (no trigger); integration-vs-record pass: <result>`, and the RESULT is what makes the close checkable (thread 156)
ESCALATE:claimed-close-unmet
```
Correct. T0 arm returns (ok=False) without consuming; ruling-213 check fires.

---

## Item 3 — 215 on real registers (verbatim stderr summary lines)

**Probe 1:** `walk-register-gates-evidence-correspondence-2026-09-09.md`
```
walk-register-gates-evidence-correspondence-2026-09-09.md	SHAPE-OK	COVERAGE: COVERED — w1 17/17 w2 7/7 w3 1/1 w4 1/1 w5 0/0 w7 27/27 w8 4/4 (rows ≥ declared on every completed walk; w9 in progress; walk-0 rows 1)	BASIS: rows=58 shape-only; coverage: see COVERAGE	shapes: ...
```
`split("\t")[1]` = `SHAPE-OK`

**Probe 2:** `walk-register-fetch-at-claim-push-at-merge-2026-09-09.md`
```
walk-register-fetch-at-claim-push-at-merge-2026-09-09.md	SHAPE-OK	COVERAGE: COVERED — w1 11/7 w2 6/4 w3 0/0 w5 5/5 w6 10/10 (rows ≥ declared on every completed walk; w7 in progress)	BASIS: rows=55 shape-only; coverage: see COVERAGE	shapes: ...
```
Over-count w1 11/7 shown. `split("\t")[1]` = `SHAPE-OK`

**Probe 3:** scratch register `Draft:` → non-existent path
```
scratch-register-old-plan.md	SHAPE-OK	COVERAGE: UNDECLARED — plan not resolvable: governance/knowledge/decisions/drafts/executable-bellows-verdict-signal.md	BASIS: rows=1 shape-only; coverage: see COVERAGE	shapes: ...
```
UNDECLARED — plan not resolvable (simulates a renumbered plan).

**Probe 4:** scratch copy with w1 rows cut to 10, `--plan <gates-evidence-correspondence draft>`
```
scratch-register-w1-cut-to-10.md	SHAPE-OK	COVERAGE: INCOMPLETE — w1 rows=10 declared=17	BASIS: rows=51 shape-only; coverage: see COVERAGE	shapes: ...
```
INCOMPLETE — w1 rows=10 declared=17. `--plan` override used; without it → UNDECLARED.

---

## Item 4 — Consumers live, read-only

**Item 4a:** `tools/run_check.py register <gates-evidence-correspondence>`
```
RUN_CHECK: register VERDICT=PASS — 1 file(s) SHAPE-OK, 0 bad
```
PASS with SHAPE-OK.

**Item 4b:** `substrate_check.py knowledge/decisions/Done/executable-100052.md`
```
SUBSTRATE PRESENT: register committed + SHAPE-OK, walks [1, 2, 3, 4, 5, 7, 8, 9] proven, baseline present
```
Register clause says SHAPE-OK.

**Item 4c:** governance hook awk over lint STDOUT
```
awk -F'\t' 'NR>1 && $4!="OK"' (over lint stdout for gates-evidence-correspondence)
```
Output: (empty — 0 rows). Column-4 contract holds.

---

## Item 5 — Production writes

None. No lane file written, no lifecycle row, no `lifecycle` import, no `gates.check` call. All file operations on scratch files under `/private/tmp/qa-closure-claim-register-coverage/`. The two evidence files in `knowledge/qa/evidence/` are the QA step's only writes.

---

## Verification

| # | Item | Status | Note |
|---|------|--------|------|
| 1 | Full suite 2145 passed | ✅ | `closure-claim-and-register-coverage-suite-2026-09-09.txt` |
| 2 | 213 on real plans — three verdicts correct | ✅ | executable-432 → ESCALATE:unparseable; scratch-100009-no-walks → ESCALATE:claimed-close-unmet; scratch-t0-claim-no-result → ESCALATE:claimed-close-unmet |
| 3 | 215 on real registers — four probes correct | ✅ | COVERED (w1 17/17, w9 in progress); COVERED (w1 11/7 over-count); UNDECLARED (plan not resolvable); INCOMPLETE (w1 rows=10 declared=17) |
| 4 | Consumers live — run_check PASS, substrate_check SHAPE-OK, awk 0 | ✅ | All three consumer checks pass |
| 5 | Production writes — none | ✅ | Only QA evidence files written |
| 6 | Run file HEAD: shas match manifest last-touch | ✅ | All three match exactly |
| 7 | Dev-log five headings present | ✅ | All five grepped and present |
| 8 | Mutation runs — 2/5/1 killed, 0 survived, 0 error | ✅ | All three manifests killed their targets |
| 9 | git reflog — 0 amends | ✅ | reflog shows reset: moving to HEAD (no-op) only |
| 10 | test_cycle_check_t0_close.py diff EMPTY | ✅ | Confirmed empty |
| 11 | test_cycle_check_register_resolver.py diff EMPTY | ✅ | Confirmed empty |
| 12 | Numstat 16 files | ❌ | 17 files — test_substrate_check.py (11 lines, worktree isolation) outside declared writes; suite passes; functional behavior unaffected |
| 13 | test_substrate_check.py diff EMPTY | ❌ | Non-empty — 11 lines added for worktree import isolation in commit 410bcd0 |

**Items 12–13 deviation summary:** `tests/test_substrate_check.py` was modified in commit `410bcd0` (the 215 commit) to add a `sys.modules` eviction block ensuring the worktree copy of `substrate_check` is imported rather than the main-branch copy. The modification is operationally necessary for worktree isolation and does not alter the test's behavioral assertions. The file is in the plan's reads list. The plan's declared writes list omits it; the deviation is noted here for the Planner.

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100053/knowledge/qa/evidence/
Files verified: 2
```

