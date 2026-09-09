# QA Receipt — mutation-per-mutant-target — 2026-09-08

**Plan:** 100047 | **Step:** 1 | **Date:** 2026-09-08 | **Tier:** T1

## Environment

```
git rev-parse --show-toplevel → /Users/marklehn/Developer/bellows/.bellows-worktrees/100047
HEAD: 751ab87a9199ea8e95c987e06a6c9ba433b6998d
Interpreter: /Users/marklehn/Developer/bellows/.venv/bin/python (VENV_OK)
config.json at repo root: ABSENT (known_failures: 0 correct)
```

## Git Status (post-sweep, scratch deleted)

```
git status --porcelain →
M knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/pytest_full.txt
```

Only the evidence directory — scratch dir deleted before this check.

## Reflog

```
git reflog -n 4 →
751ab87 HEAD@{0}: reset: moving to HEAD
751ab87 HEAD@{1}:
```

0 amends, 0 resets.

## P1 — The Merged Fix (git show --stat f00a9e0)

```
commit f00a9e086e5f60f514c3e01fb90a5bc2db2852bf
Author: Mark Lehn <22526702+EverestMons@users.noreply.github.com>
Date:   Thu Sep 3 16:01:17 2026 -0500

    fix(mutation_check): [100031] Step 1 DEV — honour per-mutant target, refuse unknown keys, name file in anchor mismatch

    Restructures main()'s per-file handling across five sites: per-target
    pristine cache, sandbox_target computed per mutant, live-sha guard
    extended to all distinct targets, uncommitted-changes warning per target,
    TARGET header per target. Adds unknown-key refusal (underscore-prefix
    exempt). Names the file searched in anchor-mismatch messages. Extends
    mutation_check.json with 5 new mutants (2 safety-critical). 9 new tests,
    20 total.

    Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 .../mutation-per-mutant-target-dev-2026-09-03.md   | 119 +++++++++
 knowledge/mutants/mutation_check.json              |  35 +++
 tests/test_mutation_check.py                       | 266 +++++++++++++++++++++
 tools/mutation_check.py                            | 118 ++++++---
 4 files changed, 510 insertions(+), 28 deletions(-)
```

## Per-Item Results Table

| Item | Description | Result |
|------|-------------|--------|
| 1 | Re-derive P2 (old=0, HEAD=1 `mutant.get("target")`), P3 (26 tests), P4 (7 killed, 0 survived, 0 error) — all match pins | ✅ |
| 2 | Full suite: 2089 passed, 0 failed — exit 0 | ✅ |
| 3 | Discriminating fixture: HEAD 3 killed/0 survived/0 error; b143604 1 killed/0 survived/2 error (M1 and M3 ERROR on stale target) | ✅ |
| 4 | 17-manifest sweep: all match P10 baseline; 3 run files match; P4 confirmed; 2 stale-anchor ERRORs reproduce exactly | ✅ |
| 5 | Refusals: (a) typo key → 2k/0s/1e exit 2; (b) missing target → 2k/0s/1e exit 2; (c) control → 3k/0s/0e exit 0 | ✅ |

## Item Detail

### Item 1 — Pin Re-derivation

**P2:** `git show b143604:tools/mutation_check.py | grep -c 'mutant.get("target")'` → **0**; same on HEAD → **1**. `tools/mutation_check.py` sha256 `1063e817ff24`. MATCH.

**P3:** `pytest tests/test_mutation_check.py --collect-only -q` → **26 tests collected**. All 26 listed in `probes-raw.txt`. MATCH.

**P4:** `tools/mutation_check.json` run → **7 killed, 0 survived, 0 error**, LIVE-TREE UNCHANGED. MATCH.

### Item 2 — Full Suite

`/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > $EV/pytest_full.txt 2>&1`

Summary line: `2089 passed, 1 skipped in 73.30s (0:01:13)` (the 1 xfail/skip is in the suite corpus, not a test_mutation_check test)

Arithmetic: 2089 passed, 0 failed, 0 errors. `known_failures: 0` satisfied.

### Item 3 — Discriminating Fixture

Fixture has top-level `"target": "tools/run_check.py"` and three mutants:
- M2 (no per-mutant target — falls back to top-level `tools/run_check.py`)
- M1 with `"target": "scripts/walk_register_lint.py"`
- M3 with `"target": "scripts/cycle_check.py"`

**HEAD run:**
```
MUTANT M2-pre-schema-counted-bad: KILLED — suite caught the defect
MUTANT M1-drop-legacy-schema-branch: KILLED — suite caught the defect
MUTANT M3-assign-fail-not-warn: KILLED — suite caught the defect
LIVE-TREE UNCHANGED: scripts/cycle_check.py sha256=0e675df6fedb
LIVE-TREE UNCHANGED: scripts/walk_register_lint.py sha256=80f7580a24ab
LIVE-TREE UNCHANGED: tools/run_check.py sha256=31a01b4c6cd5
MUTATION: 3 killed, 0 survived, 0 error
```

**b143604 run** (old tool, `--repo-root "$(git rev-parse --show-toplevel)"`, fixture uses RELATIVE targets):
```
MUTANT M2-pre-schema-counted-bad: KILLED — suite caught the defect
MUTANT M1-drop-legacy-schema-branch: ERROR — anchor matched 0 times (expected 1)
MUTANT M3-assign-fail-not-warn: ERROR — anchor matched 0 times (expected 1)
LIVE-TREE UNCHANGED: 31a01b4c6cd5
MUTATION: 1 killed, 0 survived, 2 error
```

`git status --porcelain` after old-tool run: only evidence directory (scratch already deleted). Tree unchanged.

Fixture is DISCRIMINATING: passes with 0 errors under HEAD, ERRORs under b143604 (inert-control law satisfied).

### Item 4 — No-Regression Sweep (17 manifests)

```
checker-defects-cycle_check: MUTATION: 3 killed, 0 survived, 1 error
checker-defects-cycle_yields: MUTATION: 1 killed, 0 survived, 0 error
checker-defects-plan_lint: MUTATION: 2 killed, 0 survived, 0 error
close-failopen-defaults: MUTATION: 6 killed, 0 survived, 0 error
cycle-check-battery: MUTATION: 12 killed, 0 survived, 0 error
depositor-class-assigner: MUTATION: 12 killed, 0 survived, 0 error
gate_watcher: MUTATION: 2 killed, 0 survived, 0 error
gates-verdict-pause: MUTATION: 22 killed, 0 survived, 0 error
manifest-provenance-gate: MUTATION: 1 killed, 0 survived, 3 error
mutation_check: MUTATION: 7 killed, 0 survived, 0 error
propagation-check-cycle_check: MUTATION: 1 killed, 0 survived, 0 error
propagation-check-propagation_check: MUTATION: 2 killed, 0 survived, 0 error
propagation-check-run_check: MUTATION: 1 killed, 0 survived, 0 error
qa-predeclaration-plan_lint: MUTATION: 8 killed, 0 survived, 0 error
register-enforcement-cycle_check: MUTATION: 3 killed, 0 survived, 0 error
register-enforcement-run_check: MUTATION: 1 killed, 0 survived, 0 error
register-enforcement-wrl: MUTATION: 2 killed, 0 survived, 0 error
```

Run-file verification:
- `cycle-check-battery.run.txt` (plan 100042): `12 killed, 0 survived, 0 error` — MATCH
- `depositor-class-assigner.run.txt` (plan 100043): `12 killed, 0 survived, 0 error` — MATCH
- `gates-verdict-pause.run.txt` (plan 100045): `22 killed, 0 survived, 0 error` — MATCH

P4 verification: `mutation_check` → `7 killed, 0 survived, 0 error` — MATCH

P10 stale-anchor ERRORs reproduced exactly:
- `checker-defects-cycle_check`: `3 killed, 0 survived, 1 error` — MATCH (fork 3, not this plan's subject)
- `manifest-provenance-gate`: `1 killed, 0 survived, 3 error` — MATCH (fork 3, not this plan's subject)

All 17 match P10 baseline. No HALT triggered.

### Item 5 — Refusals

**(a) Typo key (`targt` instead of `target`):**
```
MUTANT M1-drop-legacy-schema-branch: ERROR — unknown key(s) 'targt' (prefix with _ to mark as commentary)
MUTATION: 2 killed, 0 survived, 1 error
exit=2
```

**(b) Missing target file (`scripts/does_not_exist.py`):**
```
MUTANT M1-drop-legacy-schema-branch: ERROR — target not in archive: scripts/does_not_exist.py
MUTATION: 2 killed, 0 survived, 1 error
exit=2
```

**(c) Negative control (fixture unchanged):**
```
MUTATION: 3 killed, 0 survived, 0 error
exit=0
```

No ERROR line in (c). Both refusals fire (exit 2); control stays silent (exit 0). P12 satisfied.

## Test Nodes (quoted as pytest printed them)

```
tests/test_mutation_check.py::test_killed_when_mutant_breaks_the_test
tests/test_mutation_check.py::test_survived_when_suite_cannot_see_the_change
tests/test_mutation_check.py::test_empty_selector_is_error_not_killed
tests/test_mutation_check.py::test_baseline_failure_is_error_not_killed
tests/test_mutation_check.py::test_anchor_not_unique_is_error
tests/test_mutation_check.py::test_live_tree_untouched
tests/test_mutation_check.py::test_mutants_do_not_compound
tests/test_mutation_check.py::test_timeout_is_error_not_killed
tests/test_mutation_check.py::test_same_byte_length_mutation_is_killed
tests/test_mutation_check.py::test_bytecode_isolation_env_is_set
tests/test_mutation_check.py::test_consecutive_same_length_mutants_are_both_killed
tests/test_mutation_check.py::test_per_mutant_target_applies_to_that_file
tests/test_mutation_check.py::test_mutant_without_target_falls_back_to_manifest_target
tests/test_mutation_check.py::test_no_per_mutant_targets_behaves_identically
tests/test_mutation_check.py::test_per_mutant_target_missing_file_is_error
tests/test_mutation_check.py::test_unknown_per_mutant_key_is_error
tests/test_mutation_check.py::test_anchor_mismatch_message_names_file
tests/test_mutation_check.py::test_per_mutant_target_scoring_unchanged
tests/test_mutation_check.py::test_two_mutants_same_target_pristine_cache_correct
tests/test_mutation_check.py::test_report_names_the_auditing_interpreter
tests/test_mutation_check.py::test_baseline_failure_names_the_interpreter_and_hints
tests/test_mutation_check.py::test_python_flag_selects_the_interpreter
tests/test_mutation_check.py::test_refuses_an_absolute_top_level_target
tests/test_mutation_check.py::test_refuses_a_traversing_per_mutant_target
tests/test_mutation_check.py::test_a_legitimate_relative_target_is_untouched
tests/test_mutation_check.py::test_live_tree_guard_covers_all_targets
```

## Verification

| Item | Description | Status |
|------|-------------|--------|
| 1 | P2 pin: old tool 0 references, HEAD 1 reference; sha256 1063e817ff24 | ✅ |
| 2 | P3 pin: 26 tests collected in test_mutation_check.py | ✅ |
| 3 | P4 pin: 7 killed, 0 survived, 0 error on mutation_check.json | ✅ |
| 4 | Full suite: 2089 passed, 0 failed, exit 0 | ✅ |
| 5 | Fixture HEAD: 3 killed, 0 survived, 0 error; b143604: 1 killed, 0 survived, 2 error | ✅ |
| 6 | 17-manifest sweep: all match P10 baseline; run files match; no regression | ✅ |
| 7 | Refusals: typo key exit 2, missing target exit 2, control exit 0 | ✅ |
| 8 | Porcelain clean post-sweep (scratch deleted, only evidence dir modified) | ✅ |
| 9 | Reflog: 0 amends, 0 resets | ✅ |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100047/knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/
Files verified: 3
```
