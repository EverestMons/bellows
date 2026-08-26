# Dev Log: wrap-check memory class-frontmatter gate

**Plan:** 562 — wrap_check's [4/memory] arm gains class-frontmatter gate + orphan/size-cap advisories
**Date:** 2026-08-26
**Step:** 1 (DEV)

## Task A — worktree discipline

```
TREE_OK
Probe (i): m_classless count = 0 (pre-change)
Probe (ii): test file exists = 0 (pre-change)
Result: (0,0) → full run
```

## Pin verification (W1)

```
wrap_check.py: 456 lines
m_dirty = porcelain(MEMORY): count-1 (confirmed)
```

## Pin verification (W3)

```
tests/test_wrap_hooks.py: 32 passed, 1 warning (pre-change baseline)
```

## Task B — the arm

Inserted class-frontmatter gate + WARN-first advisories immediately after `m_dirty = porcelain(MEMORY)` anchor.

**Fix applied:** `git()` helper changed `strip()` → `rstrip()` — the `strip()` was destroying the leading space from the first porcelain line (e.g. `" M MEMORY.md"` became `"M MEMORY.md"`), causing `_ln[3:]` to produce `"EMORY.md"` instead of `"MEMORY.md"`. Latent bug exposed by the new line-parsing code.

### Post-probes

```
m_classless count: 6 (>= 3)
WARN (advisory) count: 2
NEVER appended to fails count: 1
```

### Smoke

```
$ python3 hooks/eluvian/wrap_check.py 2>&1 | tail -3
  ✗ [3/root] bellows gitlink is uncommitted — `git add bellows` and commit the bump.

Complete these, then this lock clears automatically.
```

Verdict line reached — arm crashes nothing on the live layout.

## Task C — tests

Created `tests/test_wrap_memory_class_gate.py` with 6 tests:
1. `test_new_entry_without_class_fails` — uncommitted entry missing class → FAIL
2. `test_new_entry_with_class_no_fail` — entry with `class: codify` → no class fail
3. `test_memory_md_edit_alone_no_class_fail` — MEMORY.md-only edit → no class fail (index exempt)
4. `test_committed_classless_entry_clean_tree_no_fail` — committed classless, clean tree → exempt
5. `test_committed_orphan_warns_but_no_fail` — committed orphan → WARN prints, fails empty
6. `test_oversized_memory_md_warns_but_no_fail` — >140-line MEMORY.md → cap WARN prints, fails empty

### Targeted run

```
38 passed, 0 failed, 1 warning (32 existing + 6 new)
```
