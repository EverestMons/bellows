# Dev Log — Detector NDJSON Shape Fix + Module Fingerprint Observability

**Date:** 2026-05-12
**Plan:** executable-detector-shape-fix-2026-05-12, Step 1

## Part A — NDJSON Shape Fix

**File:** `decisions.py`, line 94
**Change:** `event.get("content", [])` → `event.get("message", {}).get("content", [])`

Verified against `logs/20260512-184339-step.json` (canary step.json): assistant events have top-level keys `["message", "parent_tool_use_id", "session_id", "type", "uuid"]` with content nested at `message.content`. The flat `content` key never existed on real Claude CLI assistant events.

## Part B — Fixture Rewrite

**File:** `tests/test_decisions.py`
**Fixtures rewritten:** 4 locations

1. `_make_assistant_event()` helper (line 13) — wraps content under `"message": {"content": [...]}` instead of flat `"content": [...]`
2. `test_multiple_content_items` (line 129-136) — inline assistant event rewritten to wrapped shape
3. `test_event_idx_tracking` (lines 181-183) — two inline assistant events rewritten to wrapped shape
4. Non-assistant events in `test_non_assistant_events_ignored` left unchanged (they test system/user types, not assistant shape)

All 6 S-class blocks in `test_s_class_blocks_from_ground_truth` continue to pass via the updated `_make_assistant_event` helper.

## Part C — `_module_fingerprints()` Addition

**File:** `bellows.py`, line 855
**Change:** Added `"decisions.py"` as the 6th entry in the `modules` list.

**File:** `tests/test_bellows.py`, line 2952
**Change:** Renamed `test_module_fingerprints_returns_all_five_modules` → `test_module_fingerprints_returns_all_six_modules`, updated `expected_keys` to include `"decisions.py"`.

## Test Results

- **Pre-edit:** 292 passed, 1 failed (test_run_step_timeout — pre-existing, out of scope)
- **Post-edit:** 292 passed, 1 failed (same pre-existing failure)
- **Test count delta:** 0 (no tests added or removed)

## Decisions Made on Initiative

- Non-assistant event fixtures (`test_non_assistant_events_ignored`) were not rewritten because they test `type: system` and `type: user` events, not assistant events. The NDJSON shape fix only affects the assistant-event code path.
