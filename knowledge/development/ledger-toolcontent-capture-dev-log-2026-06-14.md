# Dev Log — Ledger Tool-Content Capture (Plan 60)
**Date:** 2026-06-14
**Plan:** 60
**Step:** 1 (DEV)
**Agent:** Bellows Developer

## Root Cause (Diagnostic 58)

Plan 57's FORWARD canary agent emitted its `### Ledger Updates > #### Forward Register`
block only inside a Write `tool_use` block (writing a dev log file). The runner's
assistant-event loop (runner.py ~230-234) captured only `type:"text"` blocks from
assistant turns, so `_all_assistant_text` lacked the ledger heading. The parser extracted
nothing. The defense WARN also missed it because `_all_assistant_text` was not propagated
into the `parsed` dict — `bellows.py:1138` read `parsed.get("_all_assistant_text")`
which was absent, fell back to `result_text`, which also lacked the heading.

## Changes Made

### G1 — runner.py: Tool-content capture (lines 235-245)

Extended the assistant-event content loop to also append text from `tool_use` blocks
named `Write` or `Edit`:
- **Write:** captures `block["input"]["content"]` (the file content being written)
- **Edit:** captures `block["input"]["new_string"]` (the replacement text)

Both are appended to `assistant_text_parts` alongside the existing `type:"text"`
capture. The existing text capture and `result` append are unchanged.

### G2 — parser.py: _all_assistant_text propagation (line 99)

Added `"_all_assistant_text": ledger_source` to the returned dict from `parse()`.
This ensures `bellows.py:1138` reads the full concatenated text (including tool content)
rather than falling back to `result_text`. The `ledger_source` variable already
contained the correct value (`raw.get("_all_assistant_text") or result_text`).

## New Tests

### test_runner.py (2 new tests)
- `test_tool_content_write_ledger_extraction` — Plan 57 repro: stream with
  `### Ledger Updates` ONLY inside a Write `tool_use` content block is captured
  into `_all_assistant_text` and forward register is extracted.
- `test_tool_content_edit_ledger_extraction` — Edit `tool_use` `new_string`
  content with `### Ledger Updates` is captured and feedback is extracted.

### test_parser.py (4 new tests in TestAllAssistantTextPropagation)
- `test_all_assistant_text_returned_from_result_text` — fallback when no
  `_all_assistant_text` in raw.
- `test_all_assistant_text_returned_from_raw` — passes through when present.
- `test_extraction_succeeds_from_all_assistant_text` — forward extraction from
  tool-buried content.
- `test_extraction_feedback_from_tool_content` — feedback extraction from
  tool-buried content.

### test_bellows.py (2 new tests in TestLedgerDefenseWarn)
- `test_warn_fires_for_tool_content_only_unparsed` — heading in tool-content-only
  `_all_assistant_text` but empty parse triggers WARN.
- `test_warn_silent_when_no_all_assistant_text_key` — missing key falls back to
  `result_text` without crash.

## Test Results

Full suite: **684 passed**, 0 failed, 1 warning (urllib3/LibreSSL).

## Files Modified
- `runner.py` — G1: tool-content capture in assistant-event loop
- `parser.py` — G2: `_all_assistant_text` propagation in returned dict
- `tests/test_runner.py` — 2 new tests
- `tests/test_parser.py` — 4 new tests (TestAllAssistantTextPropagation class)
- `tests/test_bellows.py` — 2 new tests

## Scope
All changes are within the plan-specified scope: `runner.py`, `parser.py`,
`tests/test_runner.py`, `tests/test_parser.py`, `tests/test_bellows.py`.
