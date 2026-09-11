# QA Receipt — check-deposit-expect-missing-2026-09-10

**Plan:** bellows #100067 | **Step:** 2 (QA) | **Date:** 2026-09-10

## DEV numstat (f947741..65879b6, five files)

```
69	0	knowledge/development/dev-log-check-deposit-expect-missing-2026-09-10.md
33	0	knowledge/mutants/check-deposit-expect-missing.json
12	0	knowledge/mutants/check-deposit-expect-missing.run.txt
92	0	tests/test_check_deposit.py
98	9	tools/check_deposit.py
```

## Verification

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | Full suite | ✅ | `2212 passed` with one skip (test_gate_watcher, live-DB) — `check-deposit-expect-missing-suite-2026-09-10.txt` |
| 2 | Real first-commit shape of #100062 | ✅ | Control: `PRECHECK: 7 failure(s) — plan.md step 1` rc 1 (includes `FAIL rule_22_verification: (a) Plan-declared deposit missing: knowledge/mutants/hooks-shared-common.run.txt` and `… dev-log-hooks-shared-common-2026-09-10.md`); flag: `PRECHECK: 0 failure(s) — plan.md step 1 (expecting 2 missing)` rc 0 with two N/A lines; guard: `PRECHECK: 2 failure(s) — plan.md step 1 (expecting 2 missing)` rc 1 with `FAIL expect_missing: … is present` for both files |
| 3 | Production writes | ✅ | No production writes beyond the two evidence files; no lane file, no lifecycle row, no lifecycle import; `$T` removed |

## Item 2 — three runs (pasted)

**Control** (shipped tool, #100062 first-commit tree `7afd777`, neutral CWD):
```
FAIL rule_22_verification: (a) Plan-declared deposit missing: knowledge/mutants/hooks-shared-common.run.txt
FAIL rule_22_verification: (a) Plan-declared deposit missing: knowledge/development/dev-log-hooks-shared-common-2026-09-10.md
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Pins re-derived (P1, P2, P4, P5)
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Failing-first (test (d) and s1–s4 red, s5 and six green, then all green)
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Extraction diff
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Mutation run
FAIL dev_log_declared_text: heading missing: ## Pins re-derived (P1, P2, P4, P5)
PRECHECK: 7 failure(s) — plan.md step 1
rc=1
```

**Flag** (`--expect-missing knowledge/development/dev-log-hooks-shared-common-2026-09-10.md knowledge/mutants/hooks-shared-common.run.txt`, same first-commit tree):
```
PRECHECK: mutation_result N/A — run file expected missing (knowledge/mutants/hooks-shared-common.run.txt)
PRECHECK: dev_log_declared_text N/A — dev-log expected missing (knowledge/development/dev-log-hooks-shared-common-2026-09-10.md)
PRECHECK: 0 failure(s) — plan.md step 1 (expecting 2 missing)
rc=0
```

**Guard** (same flag, #100062 second-commit tree `514dd23` where both files are present):
```
PRECHECK: mutation_result N/A — run file expected missing (knowledge/mutants/hooks-shared-common.run.txt)
PRECHECK: dev_log_declared_text N/A — dev-log expected missing (knowledge/development/dev-log-hooks-shared-common-2026-09-10.md)
FAIL expect_missing: knowledge/development/dev-log-hooks-shared-common-2026-09-10.md is present in the worktree — drop it from --expect-missing
FAIL expect_missing: knowledge/mutants/hooks-shared-common.run.txt is present in the worktree — drop it from --expect-missing
PRECHECK: 2 failure(s) — plan.md step 1 (expecting 2 missing)
rc=1
```

**Note:** the control was run from a neutral CWD (`$T`, not the bellows worktree) because `_resolve_deposit_path`'s CWD fallback (line 448) finds the Done #100062 files in the bellows worktree, masking the expected failures. Running from a directory without those files demonstrates the flag's value correctly.


============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100067/knowledge/qa/evidence/
Files verified: 1
