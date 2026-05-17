# DEV Log: auto_close type-safety hardening for YAML frontmatter

**Date:** 2026-05-17
**Plan:** executable-auto-close-type-safety-2026-05-17
**Agent:** Bellows Developer
**Step:** 1

---

## Problem

`bellows.py:458` calls `header.get("auto_close", "false").lower() == "true"`. When a plan uses YAML frontmatter with `auto_close: true` or `auto_close: false`, `pyyaml.safe_load` returns a Python `bool` (`True`/`False`), not a string. Calling `.lower()` on a `bool` raises `AttributeError`, crashing Bellows mid-dispatch.

### Pre-fix snippet (bellows.py:458)

```python
effective_auto_close = header.get("auto_close", "false").lower() == "true"
```

### Python repro (bool .lower() crash)

```python
>>> header = {"auto_close": True}  # simulates pyyaml output
>>> header.get("auto_close", "false").lower()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'bool' object has no attribute 'lower'
```

---

## Fix Applied

### bellows.py:458 (PATCHED)

**Before:**
```python
effective_auto_close = header.get("auto_close", "false").lower() == "true"
```

**After:**
```python
effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"
```

---

## Full Audit: `header.get(...)` followed by `.lower()` across 5 files

| # | File | Line | Pattern | Disposition |
|---|------|------|---------|-------------|
| 1 | `bellows.py` | 458 | `header.get("auto_close", "false").lower()` | **PATCHED** — wrapped in `str()` |
| 2 | `bellows.py` | 282 | `pv = header.get("pause_for_verdict", "")` | No fix needed — no `.lower()` called; returns string; `pause_for_verdict` stays in bold-Markdown per ADR (never YAML bool) |
| 3 | `bellows.py` | 299 | `header.get("pause_for_verdict", "").strip()` | No fix needed — `.strip()` not `.lower()`; `pause_for_verdict` excluded from YAML frontmatter per ADR |
| 4 | `bellows.py` | 359 | `header.get("Model", header.get("model", ...))` | No fix needed — no `.lower()` called on result |
| 5 | `gates.py` | 100 | `key = m.group(1).strip().lower()` | No fix needed — `.lower()` on regex match group (always str), not `header.get()` |
| 6 | `gates.py` | 249 | `plan_header.get("deposits")` | No fix needed — no `.lower()` called |
| 7 | `gates.py` | 391 | `"qa" in match.group(0).lower()` | No fix needed — regex match group, not header.get() |
| 8 | `verdict.py` | 215 | `verdict = match.group(1).lower()` | No fix needed — regex match group, not header.get() |
| 9 | `parser.py` | 35 | `txt.lower()` | No fix needed — `txt` is from JSON parsing (always str), not header.get() |
| 10 | `runner.py` | — | No `header.get(` patterns | No fix needed — file does not use plan headers |

**Conclusion:** Only 1 call site (bellows.py:458) had the bool-coercion risk. All other `.lower()` calls in the 5 audited files operate on values guaranteed to be strings (regex match groups, JSON-parsed text, or fields excluded from YAML frontmatter).

---

## Tests Added

### `tests/test_bellows.py::test_auto_close_yaml_bool_does_not_crash`
- Feeds `plan_header: {"auto_close": True}` (Python bool) via mocked `gates.check`
- Asserts no `AttributeError` raised
- Asserts `effective_auto_close` resolves to `True` (plan moves to Done/)

### `tests/test_bellows.py::test_auto_close_yaml_bool_false`
- Feeds `plan_header: {"auto_close": False}` (Python bool) via mocked `gates.check`
- Asserts no `AttributeError` raised
- Asserts `effective_auto_close` resolves to `False` (plan pauses for verdict)

---

## Test Results

```
pytest tests/test_bellows.py: 106 passed, 0 failed
pytest tests/ (excluding pre-existing unrelated failures): 307 passed, 2 pre-existing failures
  - test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file (missing phrases file in worktree)
  - test_runner_parser.py::test_run_step_timeout (pre-existing runner mock mismatch)
```

---

## Commit

**SHA:** 52b4f53
**Message:** `fix(bellows): str-coerce header values before .lower() to tolerate YAML bool`

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Applied `str()` coercion to `header.get("auto_close", "false")` at bellows.py:458 to prevent `AttributeError` when YAML frontmatter returns a Python bool. Audited all 5 production files for the same pattern — only 1 site affected. Added 2 regression tests covering both `True` and `False` bool inputs.

### Files Deposited
- `bellows/knowledge/development/2026-05-17-auto-close-type-safety-dev-log.md` — this file

### Files Created or Modified (Code)
- `bellows/bellows.py` — line 458: wrapped `header.get("auto_close", "false")` in `str()`
- `bellows/tests/test_bellows.py` — added `test_auto_close_yaml_bool_does_not_crash` and `test_auto_close_yaml_bool_false`

### Decisions Made
- No new helper function introduced — the `str()` wrap is a single-character-class fix inline
- No changes to bold-Markdown parser behavior
- Pre-existing test failures documented but not addressed (out of scope)

### Flags for CEO
- None

### Flags for Next Step
- Pre-existing test failures (`test_decisions.py`, `test_runner_parser.py`) are unrelated to this fix — both existed before the change
