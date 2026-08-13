# Dev Log — forward-none-guard-2026-08-13

## What shipped

Added `_forward_text_is_empty_or_none(text)` helper near `sanitize_items` in `bellows.py`. The helper returns True when the stripped text is empty, whitespace-only, or matches `none` (case-insensitive, with at most one trailing period removed).

The call site at the `elif forward_text:` guard (line 1357) now checks `not _forward_text_is_empty_or_none(forward_text)` before entering the append path. A NONE-form or empty forward section is logged as INFO and skipped — no row appended, no `record_ledger_write`.

A new elif branch logs: `ledger: forward register empty/NONE — nothing to append`.

`_append_forward_row` body is untouched — the guard lives at the boundary.

## Tests added

- `TestForwardTextIsEmptyOrNone`: parametrized truth table — `NONE`, `NONE.`, `none`, ` None. `, `   ` (whitespace-only), `` (empty) → True; `NONE and also a real item`, `- Implement the frobnicator` → False.
- `TestForwardAppendPositiveControl`: `_append_forward_row` with a real item appends exactly one row to a `tmp_path` FORWARD.md.

## Measured counts

- **Before:** 180 passed (targeted run, `tests/test_bellows.py`)
- **After:** 189 passed (180 + 9 new)

## Post-conditions

- `grep -cF "_forward_text_is_empty_or_none" bellows.py` = 2 (def + call site)
- INFO literal `ledger: forward register empty/NONE` present once

## Targeted run tail (raw)

```
189 passed, 1 warning in 4.70s
```
