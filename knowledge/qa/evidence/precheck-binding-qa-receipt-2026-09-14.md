# QA Receipt — precheck-binding — 2026-09-14

Plan: in-progress-executable-100105.md  
Step: 2 (QA)  
Base commit: ded3edb2  
DEV tip: 0bb54c9b  
Date: 2026-09-15  

---

## numstat (ded3edb2..0bb54c9b)

| added | removed | file |
|------:|--------:|------|
| 57 | 1 | bellows.py |
| 47 | 0 | hooks/git/pre-commit |
| 31 | 0 | knowledge/development/dev-log-precheck-binding-2026-09-14.md |
| 229 | 0 | knowledge/mutants/precheck-binding.json |
| 46 | 0 | knowledge/mutants/precheck-binding.run.txt |
| 3 | 2 | runner.py |
| 9 | 0 | tests/conftest.py |
| 967 | 0 | tests/test_precheck_binding.py |
| 338 | 82 | tools/check_deposit.py |

9 files changed across 3 DEV commits.

---

## git diff ded3edb2..0bb54c9b -- tests/test_check_deposit.py

EMPTY — the fourteen pre-existing tests in test_check_deposit.py were not modified.

---

## Item 2 — 11 binding tests (-v, PASSED lines)

```
tests/test_precheck_binding.py::TestB1RecordOnCleanRun::test_b1 PASSED   [  9%]
tests/test_precheck_binding.py::TestB3CommitRefusedNoRecord::test_b3 PASSED [ 18%]
tests/test_precheck_binding.py::TestB5EditedPathRefused::test_b5 PASSED  [ 27%]
tests/test_precheck_binding.py::TestB8OtherRepoGoesThrough::test_b8 PASSED [ 36%]
tests/test_precheck_binding.py::TestB17MainCheckoutRefused::test_b17 PASSED [ 45%]
tests/test_precheck_binding.py::TestB9RepoOwnHookRuns::test_b9 PASSED    [ 54%]
tests/test_precheck_binding.py::TestB12ExtraEnvReachesAgent::test_b12 PASSED [ 63%]
tests/test_precheck_binding.py::TestB13PreCheckEnvReturnsRightKeys::test_b13 PASSED [ 72%]
tests/test_precheck_binding.py::TestB18RunPlanPassesBindingPerStep::test_b18 PASSED [ 81%]
tests/test_precheck_binding.py::TestB16SpacedPathsAndStageFlag::test_b16 PASSED [ 90%]
tests/test_precheck_binding.py::TestB22MutationSurvivorRefusalAndRecovery::test_b22 PASSED [100%]
```

Binding status at test time: `GIT_CONFIG_COUNT=unset BELLOWS_PRECHECK_STEP=unset` — daemon loaded old code, worktree unbound; the autouse `_scrub_binding_env` fixture removed all binding env keys before each test.

---

## Item 3 — Replay of commit 8b52344 (plan #100097 step 1)

**Act (i)** — scratch directory created, commit 8b52344 cherry-picked (no pre-check).

**Act (ii)** — commit attempted while bound (GIT_CONFIG_COUNT set):  
exit 1 — `REFUSED no passing pre-check is recorded for in-progress-executable-100097.md step 1` / `PRECOMMIT: refused`

**Act (iii)** — pre-check run with `--expect-missing 2`:  
exit 0 — `PRECHECK: 0 failure(s) — in-progress-executable-100097.md step 1 (expecting 2 missing)` / `PRECHECK: pass recorded — 9 changed path(s)`

**Act (iv)** — commit retried while bound:  
exit 0 — `PRECOMMIT: verified — in-progress-executable-100097.md step 1`

Scratch directory removed after Acts (i)–(iv).

---

## Item 4 — Hook mode and hooksPath

`git ls-files -s hooks/git/pre-commit` → `100755 c307f71d1ed36fc922c793836993444499a298bc 0	hooks/git/pre-commit`  
`git config --local --get core.hooksPath` → (no output, exit 1 — not set)

Hook written at mode 100755; local `core.hooksPath` is empty (binding is injected via `GIT_CONFIG_COUNT/KEY/VALUE` in the agent environment, not a permanent repo config).

---

## Verification

| Item | Claim | Evidence | Status |
|------|-------|----------|--------|
| 1 | Full suite run; file `precheck-binding-suite-2026-09-14.txt` deposited; last line: `2431 passed, 9 warnings in 234.57s` (2 xfail-marked) | file is 49 lines; last line contains `2431 passed` | ✅ |
| 2 | 11 binding tests run with `-v`; all PASSED; daemon-loaded code left worktree unbound | PASSED lines pasted above; binding status line confirms `GIT_CONFIG_COUNT=unset` | ✅ |
| 3 | Replay of 8b52344: refused when bound (exit 1), pre-check recorded (exit 0), commit accepted on retry (exit 0) | Act (ii)/(iii)/(iv) outputs above | ✅ |
| 4 | Hook stored at mode 100755; local `core.hooksPath` absent | `git ls-files -s` output + `git config` exit 1 above | ✅ |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100105/knowledge/qa/evidence/
Files verified: 1
```

