# Dev Log — Tier-2 Batch: FORWARD rows 1, 3, 14

**Date:** 2026-07-02
**Plan:** 122
**Step:** 1 (DEV)

---

## Item A — Mixed-case step headers (FORWARD row 1)

### Scope Analysis

Grepped Done plans and test fixtures for line-anchored `## Step` or `## step` patterns:

- **Done plans:** All 30+ completed plans use `## Step N` (mixed-case Title Case), not `## STEP N`. The extractors only matched uppercase, silently failing on every real plan that uses the mixed-case convention.
- **Test fixtures (test_bellows.py):** `extract_total_steps` already handles case-insensitivity (uses `re.IGNORECASE` at bellows.py:233). Confirms the pattern.
- **Test fixtures (test_gates.py):** Existing fixtures use `## STEP N` (uppercase). No line-anchored lowercase `## step` patterns found that would create false-positive matches — expected, since `^## ` requires line-start header syntax that prose cannot produce.

### Code Changes

Three regex sites updated with `re.IGNORECASE`:

1. `gates.py:440` — `_extract_step_text` pattern + boundary lookahead
2. `gates.py:731` — `_gate_is_qa_step` keyword-fallback pattern
3. `verdict.py:47` — `_extract_step_text_from_plan` (sibling extractor, keep-in-sync)

Added one-line comment at gates.py and verdict.py: `# ^## anchors to line-start — prose "step 1" cannot match a header pattern`

---

## Item B — Parenthetical qualifier strip (FORWARD row 3)

### Strip Helper

```python
def _strip_trailing_parenthetical(path: str) -> str:
    return re.sub(r'\s*\([^)]*\)\s*$', '', path).strip()
```

Added at gates.py line 371 (just before `_extract_agent_declared_deposits`).

### Call Sites

1. `_extract_agent_declared_deposits` — agent receipt path extraction (line ~400)
2. `_extract_plan_required_deposits` — Deposits block parser (line ~483)
3. `_extract_plan_required_deposits` — inline format parser (line ~495)
4. `_extract_plan_required_deposits` — legacy Pattern 1 backtick-quoted (line ~503)
5. `_extract_plan_required_deposits` — legacy Pattern 2 unquoted (line ~508)
6. `_extract_plan_required_deposits` — legacy Pattern 3 `with open()` (line ~513)

The regex `\s*\([^)]*\)\s*$` only matches parentheticals at end-of-string, so `notes(v2).md` is untouched.

---

## Item C — Mojibake cell (FORWARD row 14)

### QA Report Diff

`knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` line 16:
- Before: three U+FFFD replacement chars in Status cell
- After: ✅ (single checkmark, matching all other rows)

Single-line diff confirmed. U+FFFD grep returns 0 hits.

---

## Tests

Five new tests added to `tests/test_gates.py`:

1. `test_extract_step_text_mixed_case_header` — (i) `## Step 2` extracts correctly
2. `test_extract_step_text_prose_step_does_not_create_boundary` — (ii) prose "step 1" doesn't split
3. `test_deposits_block_strips_trailing_parenthetical` — (iii) `path.md (volunteered)` → `path.md`
4. `test_parenthetical_inside_filename_preserved` — (iv) `notes(v2).md` stays intact
5. `test_agent_receipt_strips_trailing_parenthetical` — (v) receipt path qualifier stripped

---

## Full Suite Tail

```
======================= 741 passed, 1 warning in 29.38s ========================
```

---

### Ledger Updates

#### Prompt Feedback

No feedback items — plan instructions were clear and complete.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Fixed three FORWARD items: (A) made step-header regex case-insensitive across gates.py and verdict.py, (B) added `_strip_trailing_parenthetical` helper applied at all six deposit-path extraction sites in gates.py, (C) replaced U+FFFD mojibake with ✅ in the QA report.

### Files Deposited
- `knowledge/development/bellows-tier-2-batch-2026-07-02.md` — this dev log

### Files Created or Modified (Code)
- `gates.py` — case-insensitive step headers (2 sites), parenthetical strip helper + 6 call sites
- `verdict.py` — case-insensitive step header (1 site)
- `tests/test_gates.py` — 5 new tests for items A and B
- `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` — mojibake fix (1 line)

### Decisions Made
- Factored strip into a shared helper rather than repeating the regex at each site

### Flags for CEO
- None

### Flags for Next Step
- None
