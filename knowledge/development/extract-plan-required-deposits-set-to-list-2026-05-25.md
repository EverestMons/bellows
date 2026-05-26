# Dev Log: `_extract_plan_required_deposits` set→list conversion

**Date:** 2026-05-25
**Plan:** `executable-extract-plan-required-deposits-set-to-list-2026-05-25`

## (a) Diff of all edits in `gates.py`

```diff
diff --git a/gates.py b/gates.py
index 89a7fce..b8b5c4e 100644
--- a/gates.py
+++ b/gates.py
@@ -363,15 +363,19 @@ def _extract_step_text(plan_text: str, step_number: int):


 def _filter_transient_paths(paths):
-    """Drop paths whose basename starts with `_staging_` — these are transient
-    atomic-deposit filenames that exist only between write and move and are not
-    deliverables. Per LESSONS 2026-05-18 strike-4 entry."""
-    return {p for p in paths if not os.path.basename(p).startswith("_staging_")}
+    """Drop paths whose basename starts with `_staging_` and return as a list preserving
+    input order. These are transient atomic-deposit filenames that exist only between
+    write and move and are not deliverables. Per LESSONS 2026-05-18 strike-4 entry."""
+    return [p for p in paths if not os.path.basename(p).startswith("_staging_")]


 def _extract_plan_required_deposits(step_text):
     """Extract file paths explicitly required by deposit instructions in the plan step text.

+    Returns a list preserving insertion order; for the block form, this equals the
+    authoring order of bullets in the ``**Deposits:**`` block. Convention: the QA report
+    is the first ``.md`` entry in the block.
+
     Filters out `_staging_*` basenames (transient atomic-deposit filenames mentioned in
     step prose as part of describing the deposit mechanism, never persistent on disk).

@@ -384,9 +388,9 @@ def _extract_plan_required_deposits(step_text):
     block_match = re.search(...)
     if block_match:
         block_text = block_match.group(1)
-        paths = set()
+        paths = []
         for m in re.finditer(r'-\s+`([^`]+)`', block_text):
-            paths.add(m.group(1))
+            paths.append(m.group(1))
         # Explicit "- none" means no deposits required
         return _filter_transient_paths(paths)

@@ -395,27 +399,30 @@ def _extract_plan_required_deposits(step_text):
     inline_match = re.search(...)
     if inline_match:
         inline_text = inline_match.group(1)
-        paths = set()
+        paths = []
         for m in re.finditer(r'`-\s+([^`]+)`', inline_text):
-            paths.add(m.group(1))
+            paths.append(m.group(1))
         if paths:
             return _filter_transient_paths(paths)

     # Legacy fallback: prose-matching regexes
-    paths = set()
+    paths = []
     # Pattern 1-3: .add() → .append()
+    # Deduplicate preserving first-seen order
+    paths = list(dict.fromkeys(paths))
     return _filter_transient_paths(paths)
```

## (b) New test function

**Name:** `test_extract_plan_required_deposits_preserves_block_order`

**Assertions:**
1. `isinstance(result, list)` — confirms return type is `list` (not `set`)
2. `md_paths[0] == "knowledge/qa/foo.md"` — confirms QA-report-first convention via authoring order

## (c) Targeted pytest output

```
tests/test_gates.py::test_extract_plan_required_deposits_inline_format PASSED [ 33%]
tests/test_gates.py::test_extract_plan_required_deposits_multiline_format PASSED [ 66%]
tests/test_gates.py::test_extract_plan_required_deposits_preserves_block_order PASSED [100%]

====================== 3 passed, 123 deselected in 0.08s =======================
```

## (d) Type confirmation

The new test asserts `isinstance(result, list)` which PASSED — confirming `_extract_plan_required_deposits` now returns a `list`.

## (e) Deviations from plan

- Plan file was not present in `knowledge/decisions/` at the start (worktree may have been set up without it, or it was already claimed by the dispatcher). Skipped the `shutil.move` claim step and proceeded with the implementation.

## (f) Output Receipt

**Status: Complete**
