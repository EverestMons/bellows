# Development Log — Phase 8: Verdict Layer Redesign
**Date:** 2026-04-16 | **Plan:** executable-bellows-phase8-verdict-layer-redesign-2026-04-16

## Summary of Architecture Change

Phase 7 Polish built Gate 2 on prose-based flag detection: parser.py scanned agent conversational output for headings like `## CEO Flag`, `**CEO Flag:**`, etc. This repeatedly failed because agents write prose differently in their conversational output than in deposit files. The fundamental problem: Gate 2 was the only gate that parsed free-form agent prose, and it was the only gate that kept failing.

**The fix:** replaced prose-based detection with two mechanical signals:
1. **Plan-header pause declarations** — `pause_for_verdict: after_step_1` in YAML frontmatter. `gates.py` reads this from the plan file, not agent output.
2. **Action-based verdict requests** — agents create `verdicts/pending/request-{slug}-step-{N}.md`. `gates.py` checks file existence. No prose parsing required.

Additionally: diagnostics now default to NOT auto-closing (pause for verdict unless `auto_close: true` in header), and `_consume_verdicts()` final-step `continue` verdict now moves plans to Done instead of re-dispatching Step 1.

---

## parser.py — Before/After

**Before:** 6 `flag_patterns` entries with priority fallback. Last three were "polish" patterns added in Phase 7: `## CEO Flags?`, `## Flags for CEO`, `**Flags for CEO:**`, `**CEO Flag:**`. Content parsed as bulleted list if bullets present, otherwise as paragraph.

**After:** Single regex `### Flags for CEO\s*\n(.*?)(?=\n##|\Z)`. Bulleted lines only — no paragraph form. `- None` / `- N/A` excluded. No multi-pattern fallback. Safety-net role only; primary detection is in gates.py.

---

## gates.py — Additions

### `VERDICT_REQUEST_DIR`
```python
VERDICT_REQUEST_DIR = "/Users/marklehn/Desktop/GitHub/bellows/verdicts/pending"
```
Module-level constant; tests monkeypatch this to tmp directories.

### `_parse_plan_header(plan_text)`
Extracts YAML frontmatter between `---\n` delimiters at top of plan text. Returns `{}` if missing or malformed. Parses each line as `key: value`. Supported keys: `pause_for_verdict` (always/after_step_1/after_qa_step/never), `auto_close` (true/false string).

### `_verdict_requested(plan_path, step_number)`
Strips `in-progress-`, `verdict-pending-`, `halted-` prefixes and `.md` suffix from plan filename to derive slug. Checks `{VERDICT_REQUEST_DIR}/request-{slug}-step-{N}.md`. Returns `(True, contents)` if exists, `(False, None)` if not.

### `check()` signature update
Added `plan_path=None` parameter. Return dict now includes `"plan_header"` and `"verdict_requested": {"requested": bool, "body": str|None}`. These are informational — they don't add gate failures directly.

---

## bellows.py — Changes

### `header_says_pause(header, current_step, total_steps, is_qa_step)`
New module-level helper. Returns True if `pause_for_verdict` field matches current step:
- `"always"` → always True
- `"after_step_1"` → True only when `current_step == 1`
- `"after_qa_step"` → True only when `is_qa_step`
- missing/other → False

### `run_plan()` — mid-plan gate check
Old condition: `if not gate_result["passed"] or gate_result["is_qa_step"]:`
New condition adds two more pause triggers:
```python
if (not gate_result["passed"]
        or gate_result["is_qa_step"]
        or gate_result.get("verdict_requested", {}).get("requested", False)
        or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])):
```

### `run_plan()` — effective_auto_close (diagnostic default flip)
```python
header = gate_result.get("plan_header", {})
effective_auto_close = header.get("auto_close", "true" if not is_diagnostic else "false").lower() == "true"
```
Diagnostics default to `"false"` (pause for verdict). Executables default to `"true"`. Explicit `auto_close: true` in header opts a diagnostic into auto-close.

### `run_plan()` — final-step auto-close condition
Removed `is_diagnostic` requirement. Now conditioned on `effective_auto_close`:
```python
if (gate_result["passed"]
        and not gate_result["is_qa_step"]
        and not header_says_pause(...)
        and not gate_result.get("verdict_requested", {}).get("requested", False)
        and effective_auto_close):
```

### `_consume_verdicts()` — final-step continue fix
Old behavior: `continue` verdict always renames to `in-progress-` and calls `handle_new_plan()` — re-dispatching Step 1 when plan was already at final step.

New behavior: check `step_number >= total_steps` (diagnostics: total_steps=1). If final step, log "continue-to-done", move to Done/, push "Bellows — Plan Complete via Verdict". If not final step, existing dispatch logic. `stop` branch unchanged. `log_to_ledger` call moved into each branch (was called unconditionally before).

---

## Test Results

```
64 passed in 0.72s
```

Previous count: 61. Changes: -3 polish tests (test_parse_h2_ceo_flag_paragraph, test_parse_bold_ceo_flag, test_parse_h2_ceo_flag_none_paragraph) +1 replacement (test_parse_paragraph_form_no_longer_extracted) +4 gates tests (header parsing x3, verdict_requested x1) +1 bellows test (final-step continue → Done) = 64.

**Regression fix:** `test_diagnostic_auto_close_moves_to_done` — updated `clean_gates` mock to include `"plan_header": {"auto_close": "true"}` and `"verdict_requested": {"requested": False, "body": None}`. Test now explicitly opts into auto-close via header, reflecting new behavior.

---

## Output Receipt

**Agent:** Bellows Developer (Claude Code)
**Step:** 1
**Status:** Complete

### Files Deposited
- /Users/marklehn/Desktop/GitHub/bellows/parser.py
- /Users/marklehn/Desktop/GitHub/bellows/gates.py
- /Users/marklehn/Desktop/GitHub/bellows/bellows.py
- /Users/marklehn/Desktop/GitHub/bellows/tests/test_runner_parser.py
- /Users/marklehn/Desktop/GitHub/bellows/tests/test_gates.py
- /Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py
- /Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase8-verdict-layer-redesign-2026-04-16.md

### Flags for CEO
- None
