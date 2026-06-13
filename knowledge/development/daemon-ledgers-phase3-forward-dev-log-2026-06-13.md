# Daemon-Owned Ledgers Phase 3 — FORWARD New-Rows Dev Log
**Date:** 2026-06-13 | **Plan:** 45 | **Agent:** Bellows Developer | **Step:** 1

---

## Summary

Extended the daemon-owned ledgers mechanism (Phases 1+2 shipped in plans 43/44) with Phase 3: FORWARD.md new-row additions via daemon-post-merge append. This is the final mechanism phase. The implementation reuses the established framework: `### Ledger Updates` channel parse, `_apply_ledger_updates()` per-handler branches, and `files_changed` coexistence checks. Stays DORMANT — no governance edits flip agents to the channel yet.

## What Changed

### parser.py
- Extended `### Ledger Updates` extraction to capture `#### Forward Register` subsection (also matches `#### FORWARD Additions` and `#### FORWARD` heading variants) into `parsed["ledger_updates"]["forward"]`.
- Added `"forward": None` to the `ledger_updates` dict initialization.
- Mirrors the Phase 1/2 subsection pattern: absent → None, "None"/"N/A" → None, otherwise stripped text.

### bellows.py
- Added Phase 3 handler branch in `_apply_ledger_updates()`: checks `FORWARD.md` in `files_changed` for coexistence skip, then calls `_append_forward_row()` if forward content is present.
- New function `_append_forward_row(project_path, plan_id, item_text)`:
  - Reads `<project_path>/knowledge/FORWARD.md`. Gracefully skips (log-and-return) if the file does not exist.
  - Computes next row number: `max(all existing | <n> | rows) + 1`. Handles gaps, withdrawn, and closed rows correctly.
  - Fills `Added` with today's date (`datetime.now().strftime("%Y-%m-%d")`).
  - Defaults: Type=`deferred-work`, Plan-id link=`—`, Status=`open`.
  - Appends the 6-column row at EOF.
  - Commits on main: `git add knowledge/FORWARD.md && git commit`.
  - Wrapped in the existing `_apply_ledger_updates` try/except — never crashes teardown.

## Tests Added (17 new)

### test_parser.py — TestForwardRegisterExtraction (10 tests)
1. `test_extracts_forward_register` — `#### Forward Register` heading extracts
2. `test_extracts_forward_additions_heading` — `#### FORWARD Additions` heading extracts
3. `test_extracts_forward_bare_heading` — `#### FORWARD` heading extracts
4. `test_forward_none_when_absent` — absent subsection → None
5. `test_forward_none_for_none_value` — "None" text → None
6. `test_forward_none_for_na_value` — "N/A" text → None
7. `test_forward_key_always_present` — `forward` key always in dict
8. `test_forward_with_feedback_and_project_status` — all three Phase 1/2/3 coexist
9. `test_forward_before_other_subsections` — order independence
10. `test_feedback_and_project_status_still_extract` — regression: Phase 1+2 unbroken

### test_bellows.py — TestApplyLedgerUpdatesForward (7 tests)
1. `test_skips_when_forward_in_files_changed` — coexistence: FORWARD.md in files_changed → skip
2. `test_writes_correctly_numbered_row` — next # = max+1, today's date, defaults applied
3. `test_graceful_noop_when_no_forward_file` — no FORWARD.md → log-and-skip, no crash
4. `test_row_number_handles_withdrawn_closed_rows` — counts ALL rows incl. withdrawn/closed; gap-aware (max=5 → next=6)
5. `test_commits_change_to_git` — verifies git commit with "daemon-post-merge" in message
6. `test_noop_when_no_forward_in_receipt` — forward=None → no-op
7. `test_feedback_and_project_status_still_work` — Phase 1+2 paths NOT broken by Phase 3

## Test Results

Full suite: **650 passed, 0 failures** in 18.65s.

## Scope

Files modified: `parser.py`, `bellows.py`, `tests/test_parser.py`, `tests/test_bellows.py` — exactly as scoped.

## Design Decisions

- **Item text as simple string:** The parser extracts the raw text from the `#### Forward Register` subsection. The handler treats the entire text as the Item column value. Type/Plan-id link/Status defaults are applied by the daemon. This keeps the agent-side contract simple — just write the item description.
- **Row number = max(all rows) + 1:** Counts all `| <n> |` rows regardless of status (open/closed/withdrawn). This prevents row-number collisions with existing entries and handles gaps correctly.
- **No FORWARD.md → log-and-skip:** Not every project has a FORWARD register. The handler logs at INFO level and returns without error.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extended daemon-owned ledgers with Phase 3: FORWARD.md new-row additions via daemon-post-merge. Added parser extraction for `#### Forward Register` subsection and bellows handler with coexistence skip, row-number computation, date fill, and graceful no-FORWARD handling. 17 new tests, full suite green (650 passed).

### Files Deposited
- `knowledge/development/daemon-ledgers-phase3-forward-dev-log-2026-06-13.md` — this dev log

### Files Created or Modified (Code)
- `parser.py` — added `#### Forward Register` extraction to `ledger_updates["forward"]`
- `bellows.py` — added Phase 3 handler in `_apply_ledger_updates()` + new `_append_forward_row()` function
- `tests/test_parser.py` — 10 new tests (TestForwardRegisterExtraction)
- `tests/test_bellows.py` — 7 new tests (TestApplyLedgerUpdatesForward)

### Decisions Made
- Item text treated as simple string (daemon applies defaults for Type/Plan-id link/Status)
- Row numbering uses max-of-all-rows + 1 (gap-safe, status-agnostic)

### Flags for CEO
- DAEMON RESTART REQUIRED after merge
- Phase 3 DORMANT — all three mechanism phases now landed; governance activation follow-on remains

### Flags for Next Step
- QA should verify: parser extraction, row numbering with mixed statuses, dormancy/coexistence proof, Phase 1+2 intact, scope check

### Ledger Updates
#### Prompt Feedback

**2026-06-13 — daemon-ledgers-phase3 (DEV Step 1)**

1. **Phase 1/2 code was well-structured for extension.** The `_apply_ledger_updates` per-handler branch pattern and parser subsection extraction pattern made Phase 3 a mechanical addition. The consistent coexistence-check pattern (`if any("FORWARD.md" in f for f in files_changed)`) was trivially reusable.

2. **Design doc Section 3 File 3 was precise.** The disposition (daemon-post-merge for new rows only, status-update edits unchanged) and the scope nuance (only new-row additions move) were clear enough to implement without ambiguity.

3. **The FORWARD.md 6-column table format was self-documenting.** Reading the existing file provided the exact column layout and row format needed for the append function. No additional documentation lookup required.

4. **Test fixture design mirrored Phase 2.** The `_make_git_repo` helper and coexistence/write/noop test structure from `TestApplyLedgerUpdatesProjectStatus` transferred directly to the forward tests.

5. **Row-number computation edge case (gaps) needed explicit attention.** The plan correctly flagged this: "counts all `| <n> |` rows, not just open." Using `max()` over all row numbers (rather than `len()`) handles gaps from withdrawn/renumbered rows.
