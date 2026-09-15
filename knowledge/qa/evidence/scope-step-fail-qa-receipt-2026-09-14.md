# QA receipt — scope-step-fail — 2026-09-14

## numstat — DEV commits (9c512f05..2e0b1c6f)

```
63	77	gates.py
44	0	knowledge/development/dev-log-scope-step-fail-2026-09-14.md
90	0	knowledge/mutants/scope-step-fail.json
22	0	knowledge/mutants/scope-step-fail.run.txt
1	1	tests/test_gate_transaction_mechanization.py
172	11	tests/test_scope_step.py
10	6	verdict.py
```

Seven files. Two commits: `62f3287f` (five production/test files + manifest) and `2e0b1c6f` (run file + dev-log).

## Unchanged tests, checked

### tests/test_gate_transaction_mechanization.py

`git diff 9c512f05..2e0b1c6f -- tests/test_gate_transaction_mechanization.py` — one comment line changed at :30. Declared rewrite 4 (What this changes 4):

```
-    # plan 100074: scope_step warn arm — pass row always, reason_code carries earlier-step-only paths
+    # plan 100074/100104: scope_step — one row per step, pass or fail
```

### tests/test_scope_step.py

Base class/method outline (`git show "9c512f05:tests/test_scope_step.py" | grep -nE '^class |def test_'`):

```
76:class TestScopeStepArm:
79:    def test_t1_step2_own_scope_no_warn(self):
88:    def test_t2_step2_earlier_step_file_warns(self):
99:    def test_t3_step2_undeclared_file_fails_not_warned(self):
110:    def test_t4_step1_no_warn(self):
119:    def test_t5_allowlisted_file_neither(self):
128:    def test_t6_legacy_plan_no_warn(self):
137:class TestScopeStepVerdict:
140:    def test_t7_warn_row_when_warnings_present(self):
154:    def test_t8_pass_row_when_no_warnings(self):
168:class TestScopeStepLedger:
171:    def test_t9_scope_step_row_with_warning(self):
189:    def test_t10_scope_step_row_without_warning(self):
207:    def test_t11_no_warnings_key_no_raise(self):
226:class TestScopeStepT12:
229:    def test_t12_empty_own_step_set_warns_all_union_files(self):
```

Hunk headers (`git diff -U0 9c512f05..2e0b1c6f -- tests/test_scope_step.py | grep -F '@@'`):

```
@@ -34,0 +35,2 @@ PLAN_TWO_STEP = """# bellows — scope-step test fixture
@@ -74,0 +77,32 @@ PLAN_TEXT_LEGACY = """# bellows — scope-step test fixture
@@ -77 +111 @@ class TestScopeStepArm:
@@ -88,2 +122,2 @@ class TestScopeStepArm:
@@ -94,4 +128,3 @@ class TestScopeStepArm:
@@ -107,0 +141,2 @@ class TestScopeStepArm:
@@ -134,0 +170,2 @@ class TestScopeStepArm:
@@ -227 +264 @@ class TestScopeStepT12:
@@ -229,2 +266,2 @@ class TestScopeStepT12:
@@ -234,0 +272,84 @@ class TestScopeStepT12:
@@ -236 +357,41 @@ class TestScopeStepT12:
```

Hunk mapping — every hunk to its declared rewrite (What this changes 3, items i–v):

| Hunk | base range | declared rewrite | added names |
|------|-----------|-----------------|-------------|
| H1 | -34,0 (PLAN_TWO_STEP STEP 1 Scope) | (i) two lines in PLAN_TWO_STEP's STEP 1 Scope | — |
| H2 | -74,0 (after PLAN_TEXT_LEGACY) | (ii) new module-level names before first class | BELLOWS_ROOT, PLAN_T18_TWO_STEP, PLAN_T19_TWO_STEP |
| H3 | -77 (TestScopeStepArm :77) | (iii) TestScopeStepArm class docstring | — |
| H4 | -88,2 (TestScopeStepArm t2 def+doc) | (iv) t2 renamed (test_t2_step2_earlier_step_file_fails) and docstring | — |
| H5 | -94,4 (TestScopeStepArm t2 body) | (iv) t2 body rewritten (passed False, failures, warnings) | — |
| H6 | -107,0 (after TestScopeStepArm t3) | (iv) t3 assertion added (scope_step_fails == []) | — |
| H7 | -134,0 (after TestScopeStepArm t6) | (iv) t6 assertion added (scope_step_fails == []) | — |
| H8 | -227 (TestScopeStepT12 :227) | (iii) TestScopeStepT12 class docstring | — |
| H9 | -229,2 (TestScopeStepT12 t12 def+doc) | (iv) t12 renamed (test_t12_empty_own_step_set_fails_on_union_files) and docstring | — |
| H10 | -234,0 (after TestScopeStepT12 t12 check call) | (iv) t12 body new assertions; (v) class TestScopeStepFail t13–t19 (through check call) | test_t13_test_file_declared_earlier_fails, test_t14_knowledge_file_declared_earlier_fails, test_t15_multiple_earlier_step_files_one_failure, test_t16_table_scope_step_fail_row, test_t17_ledger_scope_step_fail_row, test_t18_leading_segment_own_step_passes, test_t19_absolute_path_own_step_passes |
| H11 | -236 (t12 old WARN assertion) | (v) t19 final assertions; t20, t21, t22 | test_t20_direct_caller_no_warnings_reads_union_only, test_t21_recorded_100061_step2_scope_step_fails, test_t22_recorded_100037_step2_scope_check_and_scope_step |

Every hunk falls in (i)–(v). No hunk touches t1 (:79), t4 (:110), t5 (:119), t7 (:140), t8 (:154), t9 (:171), t10 (:189), t11 (:207) — MUST-PRESERVE tests, each at their base line, untouched.

## Item 2 — arm read through its own tests

Ten PASSED lines:

```
tests/test_scope_step.py::TestScopeStepArm::test_t2_step2_earlier_step_file_fails PASSED [ 10%]
tests/test_scope_step.py::TestScopeStepT12::test_t12_empty_own_step_set_fails_on_union_files PASSED [ 20%]
tests/test_scope_step.py::TestScopeStepFail::test_t13_test_file_declared_earlier_fails PASSED [ 30%]
tests/test_scope_step.py::TestScopeStepFail::test_t14_knowledge_file_declared_earlier_fails PASSED [ 40%]
tests/test_scope_step.py::TestScopeStepFail::test_t15_multiple_earlier_step_files_one_failure PASSED [ 50%]
tests/test_scope_step.py::TestScopeStepFail::test_t16_table_scope_step_fail_row PASSED [ 60%]
tests/test_scope_step.py::TestScopeStepFail::test_t17_ledger_scope_step_fail_row PASSED [ 70%]
tests/test_scope_step.py::TestScopeStepFail::test_t20_direct_caller_no_warnings_reads_union_only PASSED [ 80%]
tests/test_scope_step.py::TestScopeStepFail::test_t21_recorded_100061_step2_scope_step_fails PASSED [ 90%]
tests/test_scope_step.py::TestScopeStepFail::test_t22_recorded_100037_step2_scope_check_and_scope_step PASSED [100%]
```

`10 passed in 0.30s`

Daemon: `ps -axo pid,lstart,command | grep '[b]ellows.py'` → started Mon Sep 14 09:34:57 2026. DEV first commit: `git log -1 --format=%ci 62f3287f` → 2026-09-15 10:47:13 -0500. Daemon started before that commit, so it loaded the old `gates.py`. A clean STEP 1, continuing under `after_qa_step` with no verdict request, ran under it too. This step's verdict carries the WARN arm's `scope_step` row, not this plan's FAIL arm.

## Item 3 — production writes

None outside the two evidence files (`scope-step-fail-suite-2026-09-14.txt` and `scope-step-fail-qa-receipt-2026-09-14.md`). No lane file, no live lifecycle row, no daemon act. `$T` removed.

## Verification

| Item | Status | Line |
|------|--------|------|
| 1 — full suite | ✅ | `2406 passed, 9 warnings in 228.16s (0:03:48)` — two skips: test_gate_watcher live-DB; test_fallback_live_wal_window version gate |
| 2 — arm (10 nodes) | ✅ | `10 passed in 0.30s` — t2, t12, t13, t14, t15, t16, t17, t20, t21, t22 all PASSED; daemon Mon Sep 14 09:34:57 2026 before DEV commit 2026-09-15 10:47:13 → WARN arm ran this step |
| 3 — production writes | ✅ | No production writes outside the two evidence files; $T removed |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100104/knowledge/qa/evidence/
Files verified: 1
