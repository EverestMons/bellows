# Dev Log — run-check-wrapper — 2026-08-26

## Task A — worktree discipline probes

```
$ cd "$(git rev-parse --show-toplevel)" && test -d tools && echo TREE_OK
TREE_OK

$ test -f tools/run_check.py && echo 1 || echo 0
0

$ test -f tests/test_run_check.py && echo 1 || echo 0
0
```

Result: (0, 0) — full run.

## Task B — post-probes

```
$ grep -c "judge_register" tools/run_check.py
2

$ grep -c "positive control" tools/run_check.py
2

$ chmod +x tools/run_check.py
(done)
```

## Task C — targeted test run

```
$ python3 -m pytest tests/test_run_check.py -v --tb=short

tests/test_run_check.py::TestJudgeCycle::test_bar_met_pass PASSED        [ 11%]
tests/test_run_check.py::TestJudgeCycle::test_continue_strict_fail PASSED [ 22%]
tests/test_run_check.py::TestJudgeCycle::test_continue_accepted_pass PASSED [ 33%]
tests/test_run_check.py::TestJudgeCycle::test_escalate_fail PASSED       [ 44%]
tests/test_run_check.py::TestJudgeRegister::test_unconformant_fail PASSED [ 55%]
tests/test_run_check.py::TestJudgeRegister::test_conformant_pass PASSED  [ 66%]
tests/test_run_check.py::TestJudgeRegister::test_empty_stderr_positive_control_fail PASSED [ 77%]
tests/test_run_check.py::TestLiveSmokes::test_lint_on_done_plan PASSED   [ 88%]
tests/test_run_check.py::TestLiveSmokes::test_register_on_walk_register PASSED [100%]

========================= 9 passed, 1 warning in 0.27s =========================
```

Targeted result: 9 passed, 0 failed.

Derivation: 6 pure judge tests (cycle BAR_MET→PASS, CONTINUE strict→FAIL,
CONTINUE accepted→PASS, ESCALATE→FAIL; register UNCONFORMANT→FAIL,
CONFORMANT→PASS, empty stderr→FAIL positive control) + 1 judge_lint test
implicit via live smoke + 2 live smokes = 9 tests.

## Live smoke outputs

### Smoke 1 — lint on Done/executable-561.md

```
$ python3 tools/run_check.py lint knowledge/decisions/Done/executable-561.md

(o1) INFO: candidates=7 excluded=6 fired=0
(o2) WARN: Deposits entry `scripts/plan_lint.py` is not project-prefixed or absolute
(o2) WARN: Deposits entry `tests/test_plan_lint_bare_constants.py` is not project-prefixed or absolute
(o2) WARN: Deposits entry `knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md` is not project-prefixed or absolute
(o2) WARN: Deposits entry `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/pytest_full.txt` is not project-prefixed or absolute
(o2) WARN: Deposits entry `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/probes-raw.txt` is not project-prefixed or absolute
(o2) WARN: Deposits entry `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/qa-receipt.md` is not project-prefixed or absolute
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 3 path(s)
PASS: (b) step 2 deposits — 3 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 3 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 3 file(s), 0 prefix(es)
RUN_CHECK: lint VERDICT=PASS — exit 0 (WARNs, if any, are advisory)
```

Exit code: 0. Verdict: PASS.

### Smoke 2 — register on walk-register-run-check-wrapper-2026-08-26.md

```
$ python3 tools/run_check.py register knowledge/research/walk-register-run-check-wrapper-2026-08-26.md

file	line	table	row_status	file_status	columns	missing	note
walk-register-run-check-wrapper-2026-08-26.md	27	1	OK	CONFORMANT	| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |	-	-
walk-register-run-check-wrapper-2026-08-26.md	37	2	OK	CONFORMANT	| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |	-	-
RUN_CHECK: register VERDICT=PASS — 1 file(s) CONFORMANT, 0 UNCONFORMANT
```

Exit code: 0. Verdict: PASS (1 file CONFORMANT — the walk register for this plan).
Derivation: the register is CONFORMANT (verified at its deposit), so VERDICT=PASS and exit 0 — the wrapper maps the verdict channel to a real exit code, which is its entire purpose.
