# extract_primary_deposit Block-Aware — Dev Log
**Date:** 2026-04-19

## Output Receipt

**Status:** Complete

### Files Created or Modified (Code)

| File | Change |
|---|---|
| `bellows/verdict.py` | Added `DEPOSITS_BLOCK_RE` and `BLOCK_BULLET_RE` module-level constants. Added block-form detection pass at top of `extract_primary_deposit` — searches for `**Deposits:**` block before legacy regex cascade. Block is authoritative: if present, returns first `.md` path or None (no fallback). Added sync comment referencing `gates.py::_extract_plan_required_deposits`. |
| `bellows/tests/test_extract_primary_deposit_blocks.py` | New file — 6 targeted pytest tests covering block single/multi `.md`, `- none`, directory-only, legacy fallback, and blockquote-prefix scenarios. |

### Test Results

- 6/6 new tests pass
- 11/11 existing verdict tests pass (zero regressions)
- Total: 17/17 pass

### Commit Message

```
feat(verdict): extract_primary_deposit recognizes Rule 26 **Deposits:** blocks
```
