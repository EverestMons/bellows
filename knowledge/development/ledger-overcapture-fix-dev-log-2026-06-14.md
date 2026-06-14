---
## Dev Log: Ledger Subsection Over-Capture Fix
**Plan:** 62
**Date:** 2026-06-14
**Agent:** Bellows Developer
**Step:** 1

---

### Problem
The three subsection regexes in parser.py (feedback ~L60, project_status ~L67, forward ~L75) used
`(.*?)(?=\n#### |\Z)` with DOTALL, capturing everything from the heading to the next `#### `
or end-of-text. When a subsection was the LAST block and the agent emitted trailing prose after a
blank line (e.g. "Now commit the deposit. Complete. All 5 checks passed:"), that prose was captured
into the ledger value. For FORWARD this broke the markdown table row (observed: row 23 had 3 pipes
instead of 7 with stray prose on following lines).

### Changes

#### (1) parser.py — subsection capture tightened (lines 59-81)
Changed all three subsection regexes to stop at the FIRST of:
- Next `#### ` heading
- Next `### ` or `## ` heading
- A blank line (`\n\s*\n`)
- End-of-text (`\Z`)

Pattern change: `(?=\n#### |\Z)` → `(?=\n#### |\n### |\n## |\n\s*\n|\Z)`

Legitimate multi-line content (no blank line separators) still captures fully.

#### (2) bellows.py — _append_forward_row single-line sanitization (line ~1296)
Added belt-and-suspenders sanitization before building the table row:
- Takes the first non-empty line from item_text
- Collapses internal whitespace runs to single spaces
- Strips trailing period-only artifact (` .`)

This guarantees a valid 6-column row regardless of what extraction returns.

#### (3) knowledge/FORWARD.md — malformed row 23 cleanup
Removed the stray trailing prose lines ("Now commit the deposit.", "Complete. All 5 checks passed:"
and duplicated canary text) from the over-captured row 23. Marked row as withdrawn (canary verified,
cleaned up by plan 62).

### Tests Added
- **test_parser.py::TestSubsectionOverCapturefix** (5 tests):
  - feedback/project_status/forward trailing prose excluded after blank line
  - legitimate multi-line (no blank line) still captures fully (feedback + forward)
- **test_bellows.py::TestForwardSingleLineItem** (3 tests):
  - multi-line item_text → valid single-line 7-pipe row
  - normal single-line item unchanged
  - internal whitespace collapsed

### Existing Tests Updated
- test_parser.py::test_extracts_feedback_from_output_receipt — removed blank line in fixture
  (was testing old over-capture behavior; now tests clean multi-line without blank separator)
- test_runner.py::test_multiturn_ledger_extraction — same blank-line fixture fix

### Test Results
706 passed, 0 failed, 1 warning (was 705 before — net +1 from 8 new tests vs existing test count changes)

### Files Modified
- parser.py — tightened 3 subsection regexes
- bellows.py — added item_text sanitization in _append_forward_row
- knowledge/FORWARD.md — cleaned malformed row 23
- tests/test_parser.py — 5 new tests + 1 fixture update
- tests/test_bellows.py — 3 new tests
- tests/test_runner.py — 1 fixture update

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Fixed ledger subsection over-capture bug by tightening parser.py regexes to stop at blank lines,
added single-line sanitization in _append_forward_row as belt-and-suspenders, and cleaned up the
malformed FORWARD.md row 23 produced by the over-capture.

### Files Deposited
- knowledge/development/ledger-overcapture-fix-dev-log-2026-06-14.md — this dev log

### Files Created or Modified (Code)
- parser.py — tightened 3 subsection capture regexes to stop at blank lines
- bellows.py — added item_text single-line sanitization in _append_forward_row
- knowledge/FORWARD.md — cleaned malformed canary row 23
- tests/test_parser.py — 5 new over-capture tests + 1 fixture update
- tests/test_bellows.py — 3 new single-line item tests
- tests/test_runner.py — 1 fixture update for blank-line change

### Decisions Made
- Updated two existing test fixtures (test_parser.py, test_runner.py) that relied on blank-line-in-content
  behavior — these were testing the old (buggy) over-capture; updated to test clean multi-line without
  blank separators

### Flags for CEO
- DAEMON RESTART REQUIRED after merge

### Flags for Next Step
- QA should verify all 23 FORWARD.md rows have exactly 7 pipes
- After daemon restart, a final FORWARD re-canary should land a clean single-line row

### Ledger Updates
#### Prompt Feedback
None
