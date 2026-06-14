# Agent Prompt Feedback

**2026-06-14 — ledger-toolcontent-capture (DEV Step 1)**

1. The tool_use event shape confirmed: `block["input"]["content"]` for Write and `block["input"]["new_string"]` for Edit — matching the diagnostic's prediction.
2. The `ledger_source` variable in parser.py already held the correct value (`raw.get("_all_assistant_text") or result_text`), so G2 was a single-line addition to the return dict.
3. All changes strictly within the 5-file scope specified by the plan.

---

Stopping here. Ready for your confirmation before proceeding to Step 2.
Step 1 complete. Here's what was done:

**G1 (runner.py):** Extended the assistant-event content loop to also capture text from `Write` (`input.content`) and `Edit` (`input.new_string`) `tool_use` blocks — fixing the plan-57 root cause where an Output Receipt emitted inside a file-write was invisible to `_all_assistant_text`.

**G2 (parser.py):** Added `_all_assistant_text: ledger_source` to the `parse()` return dict, so `bellows.py:1138`'s defense WARN now reads the full text (tool content included) instead of falling back to `result_text`.

**8 new tests** (2 in test_runner, 4 in test_parser, 2 in test_bellows). Full suite: **684 passed, 0 failed**.

**Deposit:** `knowledge/development/ledger-toolcontent-capture-dev-log-2026-06-14.md`

---

### Ledger Updates

CANARY-FEEDBACK3-153330 — feedback via channel; agent column must populate.
Complete.

---

CANARY-FEEDBACK-124753 — feedback emitted via Output Receipt channel, daemon should record to prompt_feedback DB and regenerate the md.

