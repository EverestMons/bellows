# Dev Log — Declared `**Scope:**` Block for scope_check
**Date:** 2026-07-02 | **Plan:** 119 | **Step:** 1

## Summary

Implemented the declared `**Scope:**` block convention for `scope_check` in `gates.py`. Plans can now declare exact files and directory prefixes in a `**Scope:**` block (sibling convention to `**Deposits:**`). Files matching declared scope pass silently; undeclared-and-unmentioned files still fail exactly as before. Plans without a Scope block behave byte-for-byte as today (backward compatible).

## Parser Code — `_extract_plan_scope`

```python
def _extract_plan_scope(step_text):
    """Extract declared scope from a **Scope:** block in plan step text.

    Returns (files, prefixes) where bullets ending in ``/`` are prefixes
    and all others are exact relative paths. Returns ([], []) when absent.
    Modeled on _extract_plan_required_deposits — keep in sync on parsing idiom.
    """
    block_match = re.search(r'[> ]*\*\*Scope:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)', step_text)
    if not block_match:
        return ([], [])
    block_text = block_match.group(1)
    files = []
    prefixes = []
    for line in block_text.splitlines():
        line = line.strip()
        if not line or not line.startswith(("-", ">")):
            continue
        line = re.sub(r'^[> ]*-\s+', '', line).strip()
        m = re.match(r'`([^`]+)`', line)
        path = m.group(1).strip() if m else line.strip().strip("`")
        if not path:
            continue
        if path.endswith("/"):
            prefixes.append(path)
        else:
            files.append(path)
    return (files, prefixes)
```

## Gate Diff Hunk — `_gate_scope_check`

```diff
@@ -723,6 +754,14 @@ def _gate_scope_check(plan_text, step_number, files_changed, failures):
         return
     union_text = "\n".join(all_step_texts)

+    # Build union of declared scope across all steps
+    declared_files = set()
+    declared_prefixes = set()
+    for st in all_step_texts:
+        files, prefixes = _extract_plan_scope(st)
+        declared_files.update(files)
+        declared_prefixes.update(prefixes)
+
@@ -733,6 +772,11 @@ per-file loop:
+        # Declared **Scope:** block: exact file match or prefix match
+        if fpath in declared_files or basename in declared_files:
+            continue
+        if any(fpath.startswith(p) for p in declared_prefixes):
+            continue

@@ evidence extension:
+        scope_note = "; not in declared **Scope:** block" if (declared_files or declared_prefixes) else ""
         failures.append({
             "gate": "scope_check",
-            "evidence": f"out-of-scope files: {', '.join(out_of_scope)} | plan step context: {context}",
+            "evidence": f"out-of-scope files: {', '.join(out_of_scope)} | plan step context: {context}{scope_note}",
         })
```

## Test Names

1. `test_scope_check_declared_prefix_passes` — (i) file under declared prefix passes
2. `test_scope_check_declared_exact_file_passes` — (ii) exact declared file passes
3. `test_scope_check_undeclared_file_fails_with_scope_mention` — (iii) undeclared fails with extended evidence
4. `test_scope_check_no_scope_block_backward_compat` — (iv) backward compat, both pass and fail
5. `test_scope_check_declared_scope_unions_across_steps` — (v) cross-step union
6. `test_lint_empty_scope_block_fails` — (vi) lint check (d) empty scope block
7. `test_lint_test_mentioned_no_test_scope_warns` — (vii) lint WARN for missing test scope

## Full Suite Tail

```
tests/test_worktree.py::test_auto_stage_handles_multiple_deposits PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

=============================== warnings summary ===============================
../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 736 passed, 1 warning in 30.37s ========================
```

## Self-Lint Output

```
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 5 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 1 file(s), 0 prefix(es)
```

## Commit

`c1b5094` — `feat(gates): declared **Scope:** block for scope_check — norm-shaped changes are not failures [119]`

### Ledger Updates

#### Prompt Feedback

No prompt feedback to report. The plan instructions were clear and the existing `_extract_plan_required_deposits` idiom provided a clean template to follow.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented `_extract_plan_scope()` parser in `gates.py`, consumed it in `_gate_scope_check` for exact-file and prefix matching, added lint check (d) for empty scope blocks and WARN for missing test scope in `plan_lint.py`, and wrote seven tests covering all specified scenarios.

### Files Deposited
- `knowledge/development/scope-block-declared-scope-2026-07-02.md` — dev log for plan 119 step 1

### Files Created or Modified (Code)
- `gates.py` — added `_extract_plan_scope()`, consumed in `_gate_scope_check` with extended evidence
- `scripts/plan_lint.py` — added check (d) and WARN for test scope
- `tests/test_gates.py` — 5 new tests (i-v)
- `tests/test_plan_lint.py` — 2 new tests (vi-vii)

### Decisions Made
- Parser matches both backtick-quoted and plain-text bullets (consistent with `_extract_plan_required_deposits`)
- basename matching added for declared files (e.g. `gates.py` matches changed file `gates.py`) to mirror existing union_text behavior
- Evidence extension appended (not replaced) to preserve existing evidence format

### Flags for CEO
- None

### Flags for Next Step
- Daemon restart required after this lands to load the updated `gates.py`
