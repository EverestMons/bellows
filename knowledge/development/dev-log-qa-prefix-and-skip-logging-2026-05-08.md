# Dev Log: qa- Prefix Dispatch + Silent-Skip Logging

**Date:** 2026-05-08 | **Plan:** executable-bellows-qa-prefix-and-skip-logging-2026-05-08 | **Step:** 1 (DEV)

## Changes Implemented

### Change 1 — Add `qa-` to dispatch whitelist (bellows.py:709)

Updated the regex in `is_runnable_plan()` from:
```python
r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$"
```
to:
```python
r"^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$"
```

This allows `qa-` prefixed plans (and `parallel-N-qa-` variants) to be dispatched by Bellows.

### Change 2 — Add silent-skip log line (bellows.py:740-746)

Added a guarded log block in `PlanHandler._handle()` that fires when:
- File ends with `.md`
- Not lifecycle-prefixed (`in-progress-`, `verdict-pending-`, `halted-`)
- Not roadmap-prefixed (`roadmap-` — silent skip is desired for these)
- Not already in `self._seen` (deduplication)

Log format: `"Bellows: ⚠️  skipped {filename} — prefix not in dispatch whitelist"`

After logging, the path is added to `_seen` to prevent repeat warnings on rescan.

## Test Results

- 6 new tests added, all passing
- Full suite: 223 passed, 1 failed (pre-existing `test_run_step_timeout` in `test_runner_parser.py` — unrelated to this change)

## Output Receipt

**Status:** Complete

### Files Created or Modified (Code)

| File | Change |
|------|--------|
| `bellows.py` | Added `qa` to `is_runnable_plan()` regex alternation at line 709; added silent-skip logging block with dedup guard at lines 740-746 in `PlanHandler._handle()` |
| `tests/test_bellows.py` | Added 6 tests: `test_is_runnable_plan_qa_prefix`, `test_is_runnable_plan_parallel_qa_prefix`, `test_is_runnable_plan_rejects_roadmap`, `test_is_runnable_plan_rejects_staging`, `test_skip_logging_fires_once`, `test_skip_logging_deduplication` |

### Files Created (Knowledge)

| File | Description |
|------|-------------|
| `knowledge/development/dev-log-qa-prefix-and-skip-logging-2026-05-08.md` | This dev log |
