# QA Report: Shadow Copy Plan Cache

**Plan:** executable-shadow-copy-cache-2026-04-17
**Step:** 2 (QA)
**Date:** 2026-04-17

## Dev Log Check

Output Receipt status: **Complete**. Files changed: bellows.py, .gitignore. Commit present.

## Verification Matrix

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| a | `.bellows-cache/` directory creation | ✅ | SHADOW_CACHE_DIR at line 18, mkdir at line 103 |
| b | Shadow write after plan claim | ✅ | _write_shadow at line 212, after shutil.move at line 209 |
| c | Shadow read in run_plan | ✅ | _read_shadow at line 192, metadata_text used for extract_total_steps and _parse_plan_header |
| c | Shadow read in _consume_verdicts | ✅ | _read_shadow at line 619, used for total_steps_c |
| d | Shadow cleanup on Done/Skip/Halt | ✅ | _delete_shadow at lines 221, 361, 637, 654 — all four close paths |
| e | .bellows-cache/ in .gitignore | ✅ | Listed at line 12 of .gitignore |
| f | Fallback chain: shadow > verdict metadata > load_file | ✅ | Lines 618-627: shadow_text_c > total_steps_from_request > load_file |

## Summary

All six deliverables verified via direct grep and code inspection. Shadow copy mechanism correctly preserves pristine plan content at claim time, reads it for all metadata extraction, cleans up at all plan-close paths, and falls back gracefully when no shadow exists. Evidence piped to `knowledge/qa/evidence/executable-shadow-copy-cache-2026-04-17/grep_deliverables.txt`.
