# Ledger Fix RE-CANARY — Multi-Turn Extraction Live Verification

**Date:** 2026-06-14 | **Plan:** 55 | **Agent:** Bellows Systems Analyst | **Step:** 1

---

## Lifecycle DB Check

```
sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" \
  "SELECT id, type, lifecycle_state FROM plans WHERE id=55"
```

**Output:**
```
55|diagnostic|in_progress
```

**Verdict:** type=diagnostic, lifecycle_state=in_progress — confirmed.

---

## Fix Verification (Plan 54 Multi-Turn Extraction)

### What was broken (plan 52 canary failure)

`parser.parse()` only read `raw.get("result", "")` — the final result event's `result` field. Multi-turn agents emit the Output Receipt (containing `### Ledger Updates`) in an intermediate assistant turn, so the parser silently dropped both ledger channels.

### What plan 54 fixed

1. **runner.py:216-262** — Collects all intermediate assistant-turn text into `assistant_text_parts`, concatenates with the final result, stores as `_all_assistant_text` on the result event.
2. **parser.py:50-53** — `ledger_source = raw.get("_all_assistant_text") or result_text` — ledger extraction now reads concatenated text, falling back to `result_text` for backward compat.
3. **bellows.py:1136-1142** — Defense-in-depth WARN fires if `### Ledger Updates` heading is present in `_all_assistant_text` but parser extracted nothing.

### Test suite

272 tests pass (test_runner.py + test_bellows.py + test_lifecycle.py). Covers:
- `TestLedgerDefenseWarn` — WARN fires on heading-present-but-empty, silent when populated or absent.
- `TestExtractAgent` + `TestAgentColumnPopulated` — `extract_agent` populates agent column from `**Agent:**` in Output Receipt.

### Daemon application path (bellows.py:1144-1204)

- Feedback: `lifecycle.record_prompt_feedback(agent=parsed.get("_agent"))` — agent column will be non-empty when `**Agent:**` appears in the result text.
- Project status: `_append_project_status()` appends to `PROJECT_STATUS.md` on main.
- Both paths have idempotency guards via `check_ledger_write_exists`.

---

## Result

**PASS** — The multi-turn ledger extraction fix (plan 54) is structurally sound. The runner concatenates all assistant turns, the parser reads from the concatenated text, and the defense-in-depth WARN catches any future regression. This re-canary will exercise the fix live: both ledger channels are emitted via Output Receipt below (in a later turn than the investigation reads, per diagnostic instructions). The daemon must extract and apply both.
