# Dev-log: gates evidence correspondence (plan 100052, threads 203, 211, 204, 196)
**Date:** 2026-09-09 | **Branch:** bellows-wt/100052 | **HEAD (first commit):** 91354d2aedbeed44255051a17e54f153dabd27e8

---

## Pins re-derived (P1, P2)

**P1 — the gate module** (`gates.py`):
`wc -l gates.py` → 1281 lines at `c4073c4` (pre-plan HEAD). `check()` at `:270` makes 13 dispatch calls in order (`:290–315`): `receipt_status`, `ceo_flags`, `no_errors`, `no_permission_denials`, `deposit_exists`, `is_qa_step` (informational), `rule_20_self_check`, `rule_22_verification`, `qa_test_result`, `file_change_audit`, `scope_check`, `quoted_test_nodes_exist`, `mutation_result` — twelve gates. `_gate_quoted_test_nodes_exist` at `:1175` opens with `if not is_qa_step: return`; `_TEST_NODE_RE` at `:1170`. `qa_report_path = md_paths[0]` at `:693` and `:748`. The 43 content selection at `:877–900`. `strip_fenced_code_blocks` at `:13` exists; the node gate does NOT call it (fenced pytest output stays readable — 203 needs it). Confirmed: no mechanism mismatch; proceeding.

**P2 — the three lists, their tests, and the fifth consumer** (pre-plan baseline):
`verdict._KNOWN_GATES` 13 rows at `:112–126`; `lifecycle.standard_gates` 10 names at `:527–533`; `STANDARD_GATES` 10 in `tests/test_gate_transaction_mechanization.py:15–27` with `assert len(rows) == len(STANDARD_GATES)` at `:71`; `tests/test_gates_verdict_pause.py` 20 collected tests (24 `def test_` lines — four are helpers) — `test_16` at `:634` asserts dispatch order and verdict rows, `test_17` at `:724` asserts a DEV step adds nothing; `tests/test_lifecycle.py:461` asserts pass rows for the three 100045 gates; `scripts/plan_lint.py:534–550` check (u) WARNs "rule_20_self_check reads the first .md"; `tools/passfail_record_census.py:145` carries a stale 7-name copy of `standard_gates`. After this plan: 15 rows, 12 names, 12 STANDARD_GATES.

---

## Failing-first (the sibling red, then green)

Sibling test file `tests/test_gates_evidence_correspondence.py` written before implementation (17 tests). Run before any implementation changes:

```
FFFFFFFFFFFFFFFF.                                                        [100%]
test_1_banner_wins         AssertionError: gate should select banner file
test_2_legacy_position     AssertionError: gate should pick first file when scores equal
test_3_scoring             AssertionError: gate should pick verification file
test_4_211_dev_step_missing_nodes   AssertionError: expected 1 failure, got 0
test_5_211_dev_step_nodes_exist     (passes — gate fires on DEV step but no nodes missing)
test_6_203_failed_marked_present    AssertionError: expected 0 failures, got 1
test_7_203_failed_marked_absent     AssertionError: expected 1 failure, got 0
test_8_203_passed_marked_contradicted AssertionError: expected 1 failure, got 0
test_9_203_quiet_suite_adds_nothing AssertionError: expected 0 failures, got 1
test_10_203_verbose_suite  AssertionError: expected 1 failure, got 0
test_11_203_adds_nothing   AssertionError: expected 0 failures, got 1
test_12_196_arm_a          AssertionError: expected 1 failure, got 0
test_13_196_arm_b          AssertionError: expected 1 failure, got 0
test_14_196_adds_nothing   AssertionError: expected 0 failures, got 1
test_15_dispatch_and_rows  AssertionError: gate_qa_nodes_match_suite not in dispatch order
test_16_lifecycle_rows     AssertionError: expected pass rows for two new gates
test_17_suite_selection_rule_21     AssertionError: suite file not selected
```

16 red, 1 green (test_5 passed before implementation: the widening was needed for test_4, but test_5 tested the non-fire case which passes vacuously). After full implementation (gates.py, verdict.py, lifecycle.py, tests updates):

```
tests/test_gates_evidence_correspondence.py  17 passed
Full suite: 2129 passed, 1 skipped
```

Deviation: `tests/test_step_files_record.py` required an unanticipated update — two assertions hardcoded `== 10` for gate event counts; adding 2 to `lifecycle.standard_gates` broke them. Fix: import `STANDARD_GATES` from `test_gate_transaction_mechanization` and use `_N_STANDARD_GATES = len(STANDARD_GATES)`.

---

## Mutation run

Ten mutants, all killed. Run command:

```
.venv/bin/python tools/mutation_check.py knowledge/mutants/gates-evidence-correspondence.json \
  > knowledge/mutants/gates-evidence-correspondence.run.txt 2>&1; echo "exit=$?"
```

```
MUTATION: 10 killed, 0 survived, 0 error
exit=0
```

| # | name | target | expect_fail |
|---|------|--------|-------------|
| M1 | select-qa-report-returns-first | gates.py | test_1_banner_wins |
| M2 | restore-qa-only-guard-65 | gates.py | test_4_211_dev_step_missing_nodes |
| M3 | skip-failed-marked-check | gates.py | test_7_203_failed_marked_absent |
| M4 | invert-passed-marked-check | gates.py | test_8_203_passed_marked_contradicted |
| M5 | drop-verbose-detection | gates.py | test_10_203_verbose_suite |
| M6 | heading-substring-not-full-line | gates.py | test_12_196_arm_a |
| M7 | verbatim-always-matches | gates.py | test_13_196_arm_b |
| M8 | drop-dev-log-declared-text-dispatch | gates.py | test_15_dispatch_and_rows |
| M9 | drop-verification-score | gates.py | test_3_scoring |
| M10 | drop-suite-full-and-largest-passed-tiebreaks | gates.py | test_17_suite_selection_rule_21 |

M4's first formulation (`passed_marked = True`) survived — a line with `✅` and no FAILED markers gets `failed_marked=False, passed_marked=True` → unequal, treated as passed-marked, same outcome as the real code. Fixed to `passed_marked = False` so both False → skipped, gate never fires for PASSED-marked lines → test_8 fails → KILLED.

---

## Corpus replay

28 dev-logs quote 151 distinct ids (217 `findall` matches); 5 undefined (`reattempt-teardown-on-continue-resume-2026-06-04.md` ×4 `test_consume_verdicts.py::test_retry_*`; `gate-transaction-mechanization-dev-log-2026-08-07.md` ×1); 0 undefined in the 2026-09 dev-logs

In-process replay of the three gates over 347 Done executable plans, reading their on-disk deposits (read-only; `gates.check` never called; no lifecycle import; no `**Project:**` filter). Project path: `/Users/marklehn/Developer/bellows` for deposit resolution.

**Counts:**
- Plans scanned: 347
- Steps read: 681
- QA steps with .txt deposits (receipt/suite pairs examined by gate 203): 90

**`_gate_dev_log_declared_text` (196):** 0 fires. No Done plan carries a `**Headings:**` or `**Verbatim:**` line — the gate is vacuous over the corpus by construction.

**`_gate_qa_nodes_match_suite` (203):** 2 fires.
1. `executable-100005.md` step 2 (QA, TRUE positive): 10 FAILED-marked nodes all absent from a `49 passed` suite — `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`, `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases`, `test_loads_slash_alternatives`, `test_splits_slash_alternatives`, `tests/test_notifier_server.py::test_server_respond`, `tests/test_phase4_planner_retry.py::test_planner_falls_back_to_continue_on_persistent_failure`, `test_planner_retries_on_auth_failure`, `tests/test_planner.py::test_build_consult_file`, `test_consult_bad_json`, `test_consult_timeout`.
2. `executable-100045.md` step 2 (QA, FALSE positive — the false-positive class stated in *What this does NOT do*): `gates-verdict-pause-qa-evidence-2026-09-08.md` line 61 reads "Contains at line 36: `FAILED tests/test_decisions.py::TestLoadPhrases::test_loads_slash_alternatives`" — prose attribution quoting what another file's line 36 contains, not a test verdict in this report. `FAILED` and the node appear on the same line → classified as failed-marked. This is the reported false-positive class; nothing is re-gated retroactively.

**`_gate_quoted_test_nodes_exist` (widened — fires on every step, 211):** 7 fires total. 2 are new DEV-step fires from the widening; 5 were already QA-step fires before this plan.

New DEV-step fires (thread 211 widening):
- `executable-312.md` step 1 (DEV): `gate-transaction-mechanization-dev-log-2026-08-07.md` quotes `tests/test_gate_transaction_mechanization.py::TestDecidedByGap::test_both_ver…` — class/method no longer in the worktree.
- `executable-reattempt-teardown-on-continue-resume-2026-06-04.md` step 1 (DEV): dev-log quotes `tests/test_consume_verdicts.py::test_retry_clears_dirty_tree_teardown_on_succ…` — 4 `test_retry_*` nodes (P4's 5 undefined reduced to 1 file here because only one step fires).

Pre-existing QA-step fires (unchanged by widening):
- `executable-100005.md` step 2 (QA): `test_loads_slash_alternatives` missing.
- `executable-100045.md` step 2 (QA): same node.
- `executable-bellows-notifier-timeout-2026-04-16.md` step 2 (QA): `test_configurable_timeout_passed_to…` missing.
- `executable-consume-verdicts-prefix-fix-2026-05-21.md` step 2 (QA): `test_pre_scan_renames_pro…` missing.
- `executable-gate-fp-coordinated-shape-2026-05-27.md` step 2 (QA): `test_qa_steps_field_absent_falls_bac…` missing.

Nothing is re-gated retroactively.

---

## Cost

`gates.check` timing on a QA fixture (step 2, two deposits, both resolved), three runs after warm-up. AFTER = with both new gates active; BEFORE = new gates monkeypatched to no-ops.

| Run | Before (ms) | After (ms) |
|-----|-------------|------------|
| 1   | 0.32        | 0.31       |
| 2   | 0.27        | 0.30       |
| 3   | 0.28        | 0.30       |
| **Median** | **0.28** | **0.30** |

Delta: +0.02 ms (< 10% overhead). The two new gates read the QA .md and suite .txt that `_gate_rule_20_self_check` and `_gate_qa_test_result` already opened; on a QA step with both deposits present the marginal cost is one regex scan per deposit per gate. The 196 gate exits immediately when no `**Headings:**` or `**Verbatim:**` lines are declared (the common DEV-step case).
