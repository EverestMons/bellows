# Dev Log: test_rule_26_deposit_parser set-literal assertion follow-up

**Date:** 2026-05-25
**Plan:** `executable-test-rule-26-set-to-list-followup-2026-05-25`

## (a) Diff of `tests/test_rule_26_deposit_parser.py`

```diff
diff --git a/tests/test_rule_26_deposit_parser.py b/tests/test_rule_26_deposit_parser.py
index c5d6725..067d545 100644
--- a/tests/test_rule_26_deposit_parser.py
+++ b/tests/test_rule_26_deposit_parser.py
@@ -23,7 +23,7 @@ def test_extract_plan_required_deposits_prefers_declared_block():
 > - `knowledge/dev/beta.md`
 """
     result = gates._extract_plan_required_deposits(step_text)
-    assert result == {"knowledge/dev/alpha.md", "knowledge/dev/beta.md"}
+    assert set(result) == {"knowledge/dev/alpha.md", "knowledge/dev/beta.md"}
     assert "other-path.md" not in result


@@ -49,7 +49,7 @@ def test_extract_plan_required_deposits_handles_none_bullet():
 > - none
 """
     result = gates._extract_plan_required_deposits(step_text)
-    assert result == set()
+    assert set(result) == set()


 def test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present():
@@ -69,7 +69,7 @@ def test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_
 > - `knowledge/dev/real-deposit.md`
 """
     result = gates._extract_plan_required_deposits(step_text)
-    assert result == {"knowledge/dev/real-deposit.md"}
+    assert set(result) == {"knowledge/dev/real-deposit.md"}
     assert "path/to/file.md" not in result
     assert "legacy/false-positive.md" not in result

@@ -120,7 +120,7 @@ def test_extract_plan_required_deposits_blank_quoted_line():
 > - `bellows/foo.md`
 """
     result = gates._extract_plan_required_deposits(step_text)
-    assert result == {"bellows/foo.md"}
+    assert set(result) == {"bellows/foo.md"}


 def test_extract_plan_required_deposits_multiple_blank_quoted_lines():
@@ -134,7 +134,7 @@ def test_extract_plan_required_deposits_multiple_blank_quoted_lines():
 > - `bellows/foo.md`
 """
     result = gates._extract_plan_required_deposits(step_text)
-    assert result == {"bellows/foo.md"}
+    assert set(result) == {"bellows/foo.md"}


 def test_extract_plan_required_deposits_does_not_span_paragraphs():
@@ -150,7 +150,7 @@ Some other prose.
 - `unrelated/bar.md`
 """
     result = gates._extract_plan_required_deposits(step_text)
-    assert result == set()
+    assert set(result) == set()
```

## (b) Pytest output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Applications/Xcode.app/Contents/Developer/usr/bin/python3
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/test-rule-26-set-to-list-followup-2026-05-25
plugins: anyio-4.12.1, xdist-3.8.0, cov-7.0.0
collecting ... collected 9 items

tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_prefers_declared_block PASSED [ 11%]
tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_falls_back_to_legacy_when_no_block PASSED [ 22%]
tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_handles_none_bullet PASSED [ 33%]
tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present PASSED [ 44%]
tests/test_rule_26_deposit_parser.py::test_extract_primary_deposit_scoping_in_post_verdict_request PASSED [ 55%]
tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_blank_quoted_line PASSED [ 66%]
tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_multiple_blank_quoted_lines PASSED [ 77%]
tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_does_not_span_paragraphs PASSED [ 88%]
tests/test_rule_26_deposit_parser.py::test_extract_step_text_helper_gates_py PASSED [100%]

========================= 9 passed, 1 warning in 0.12s =========================
```

All 6 previously-failing tests now PASS:
- `test_extract_plan_required_deposits_prefers_declared_block` — PASSED
- `test_extract_plan_required_deposits_handles_none_bullet` — PASSED
- `test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present` — PASSED
- `test_extract_plan_required_deposits_blank_quoted_line` — PASSED
- `test_extract_plan_required_deposits_multiple_blank_quoted_lines` — PASSED
- `test_extract_plan_required_deposits_does_not_span_paragraphs` — PASSED

## (c) Files modified

Only `tests/test_rule_26_deposit_parser.py` was modified (plus this dev log deposit). No production code touched. Confirmed via `git status --short` after commit.

## (d) Deviations

None. All 6 sites matched the plan exactly.

## (e) Output Receipt

**Status:** Complete
**Files modified:** `tests/test_rule_26_deposit_parser.py` (6 assertion lines), `knowledge/development/test-rule-26-set-to-list-followup-2026-05-25.md` (this file)
**Tests:** 9/9 PASSED in `tests/test_rule_26_deposit_parser.py`
