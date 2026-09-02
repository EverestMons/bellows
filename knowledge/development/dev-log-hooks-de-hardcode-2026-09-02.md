# Dev log — hooks-de-hardcode-2026-09-02 (plan 100015, Step 1 DEV)

**Date:** 2026-09-02  
**Plan:** hooks-de-hardcode-2026-09-02 (executable-100015)

---

## A1 — Pins measured

### P1 — TARGET_SHAS (pre-edit)
| file | sha256[:16] | plan pin | match |
|---|---|---|---|
| hooks/eluvian/wrap_arm_hook.py | 37c0f8af28df9fa6 | 37c0f8af28df9fa6 | ✓ |
| hooks/eluvian/wrap_stop_hook.py | 571b2552ab347e46 | 571b2552ab347e46 | ✓ |
| hooks/eluvian/wrap_check.py | c840bbfae2ad8ff9 | c840bbfae2ad8ff9 | ✓ |
| hooks/eluvian/eluvian_align_hook.py | 61e64c61a8f59804 | 61e64c61a8f59804 | ✓ |
| hooks/commands/wrap.md | 11a0af73cc11378f | 11a0af73cc11378f | ✓ |

### P2 — ANCHORS (all count 1)
| edit | anchor (abbreviated) | count |
|---|---|---|
| E1 | `_DEFAULT_ROOT = Path("/Users/marklehn/Developer/GitHub")` in wrap_arm_hook.py | 1 |
| E2 | `_DEFAULT_ROOT = Path("/Users/marklehn/Developer/GitHub")` in wrap_stop_hook.py | 1 |
| E3 | two-line ROOT = ... in wrap_check.py | 1 |
| E4 | two-line _GOV_ROOT = ... in eluvian_align_hook.py | 1 |
| E5 | `    candidates.append(ROOT / "tuyere")` in wrap_check.py | 1 |
| E6 | `touch "${ELUVIAN_WRAP_ROOT:-/Users/...}/.wrap-in-progress"` in wrap.md | 1 |
| E7 | `` glossary at `/Users/marklehn/Developer/GitHub/GLOSSARY.md` `` in wrap.md | 1 |

All 7 anchors confirmed at count 1 before editing.

### P3-pre — token counts (before edits)
- `def _default_root` → 0 in all four hooks
- `/Users/marklehn/Developer/GitHub` → 1 each in four hooks, 2 in wrap.md (total 6)
- `_resolve_bellows(ROOT).parent / "tuyere"` → 0 in wrap_check.py
- `ELUVIAN_WRAP_ROOT:?` → 0 in wrap.md

### P4 — HOOK_SUITE_PRE
```
134 passed in 9.00s
```

### P5 — HARNESS_PY
```
/usr/bin/python3 is Python 3.9.6
Harness imports (pre-edit, ELUVIAN_WRAP_ROOT set):
  wrap_arm_hook imports OK
  wrap_stop_hook imports OK
  wrap_check imports OK
  eluvian_align_hook imports OK
```

### P6 — INSTALLED_COPIES (pre-edit)
```
IDENTICAL wrap_arm_hook.py
IDENTICAL wrap_stop_hook.py
IDENTICAL wrap_check.py
IDENTICAL eluvian_align_hook.py
IDENTICAL wrap_debt_hook.py
```

---

## A2 — Seven edits (post-edit verification)

### P3-post — token counts
- `def _default_root` → 1 in each of the four hooks (4 total) ✓
- `/Users/marklehn/Developer/GitHub` → 0 in all five files ✓
- `_resolve_bellows(ROOT).parent / "tuyere"` → 1 in wrap_check.py ✓
- `ELUVIAN_WRAP_ROOT:?` → 1 in wrap.md ✓

### py_compile on four hooks
```
OK: hooks/eluvian/wrap_arm_hook.py
OK: hooks/eluvian/wrap_stop_hook.py
OK: hooks/eluvian/wrap_check.py
OK: hooks/eluvian/eluvian_align_hook.py
```

### Harness interpreter (env unset → marker-verified home)
```
wrap_arm_hook /Users/marklehn/Developer/eluvian-governance
wrap_stop_hook /Users/marklehn/Developer/eluvian-governance
wrap_check /Users/marklehn/Developer/eluvian-governance
eluvian_align_hook /Users/marklehn/Developer/eluvian-governance
```

Four lines, each ending `/Users/marklehn/Developer/eluvian-governance` — the marker-verified home on this machine. ✓

---

## A3 — Test summary

### tests/test_hook_default_root.py (new, 7 tests)
```
7 passed in 0.17s
```

### Hook suite (P4 post-edit)
```
134 passed in 8.76s
```

### test_plan_claim.py (twin test)
```
49 passed in 0.48s
```

### Full suite (P7)
```
1676 passed, 1 skipped in 49.35s
```
No FAILED line. N = 1676 ≥ 1676. Skip count = 1 (live-DB test, CWD property — expected). ✓
