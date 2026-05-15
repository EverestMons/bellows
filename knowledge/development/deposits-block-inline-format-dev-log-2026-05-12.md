# Dev Log: Deposits Block Inline-Format Support
**Date:** 2026-05-12

## Fix Shape

Chose approach **(b)**: added a second branch that runs only when the block regex fails. The inline branch searches the same line as `**Deposits:**` for backtick-wrapped path tokens via a separate regex.

## Lines Changed in `gates.py`

Inserted 7 new lines after line 281 (after the block regex branch, before the legacy fallback):

- **Lines 283-289** (post-edit numbering): New inline-format branch
  - Line 283-284: Comment explaining the inline format
  - Line 285: `re.search(r'[> ]*\*\*Deposits:\*\*[ \t]+(.+)', step_text)` — matches `**Deposits:**` followed by inline content on the same line
  - Lines 286-289: Extract backtick-wrapped `- /path` tokens via `re.finditer(r'`-\s+([^`]+)`', inline_text)`, guarded by `if paths:` to fall through to legacy patterns if no tokens found

## New Test Names

- `test_extract_plan_required_deposits_inline_format` — verifies inline format with trailing period and directory-trailing-slash variant
- `test_extract_plan_required_deposits_multiline_format` — locks the existing multi-line block format behavior (no prior direct unit test existed)

## Commit

SHA: `d46f42a`
Subject: `fix(gates): _extract_plan_required_deposits handles inline **Deposits:** format`
Files: `gates.py`, `tests/test_gates.py`

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extended `_extract_plan_required_deposits` in `gates.py` with an inline-format branch that handles `**Deposits:**` blocks where paths appear on the same line as the marker. Added two regression tests covering both inline and multi-line formats.

### Files Deposited
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/deposits-block-inline-format-dev-log-2026-05-12.md` — this dev log

### Files Created or Modified (Code)
- `gates.py` — added inline-format branch (7 LOC) after block regex, before legacy fallback
- `tests/test_gates.py` — added `test_extract_plan_required_deposits_inline_format` and `test_extract_plan_required_deposits_multiline_format`

### Decisions Made
- Chose approach (b) (separate branch) over (a) (regex modification) for clarity and to avoid complicating the existing block regex

### Flags for CEO
- None

### Flags for Next Step
- None
