# Forward Splitter — Dev Log (Plan 294)

**Date:** 2026-08-03
**Step:** 1 (DEV)
**BELLOWS_TREE:** /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/294

---

## Task A0 — Pristine Start

All three checks pass:

1. **SHA sums match authoring pins:**
   - `bellows.py`: `fc3c2654162287a1ee902250386740e8f1973f5286df3a98c0f2e4416242b1d5` (prefix `fc3c2654162287a1` matches)
   - `tests/test_bellows.py`: `3f989fba2ed068cd1e9b21b0eb8145de2c64e0768f4cfeb9d98408f4abceadc5` (prefix `3f989fba2ed068cd` matches)
2. **`git status --porcelain -- bellows.py tests/`:** EMPTY
3. **`git log --all --oneline -- bellows.py | grep '[294]'`:** EMPTY (no prior commit tagged with this plan's id)

## Task A — Pre-Change State (FULL-SUITE BASELINE (834))

**Pre-change SHA sums:**
- `bellows.py`: `fc3c2654162287a1ee902250386740e8f1973f5286df3a98c0f2e4416242b1d5`
- `tests/test_bellows.py`: `3f989fba2ed068cd1e9b21b0eb8145de2c64e0768f4cfeb9d98408f4abceadc5`

**Forward Register row count:** 25

**Full suite baseline (RAW tail):**
```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 834 passed, 1 warning in 21.61s ========================
```

## Task B — Sanitizer Implementation

Added module-level `BULLET_RE` and `sanitize_items(item_text)` per §Q4 verbatim:

```python
BULLET_RE = re.compile(r"^(?:-\s|\d+\.\s)")


def sanitize_items(item_text):
    lines = [ln.strip() for ln in item_text.splitlines() if ln.strip()]
    if not lines:
        return [item_text.strip()]
    bullet_lines = [ln for ln in lines if BULLET_RE.match(ln)]
    if len(bullet_lines) >= 2:
        return [" ".join(bl.split()) for bl in bullet_lines]
    else:
        return [" ".join(lines[0].split())]
```

**`_append_forward_row` changes:**
- Routes through `sanitize_items` to get a list of items
- Iterates over items, applying the `" ."` trailing-artifact strip to each
- Increments `next_num` per row (not computed once)
- Writes all N rows, then commits once
- Bullet markers are NOT stripped (§Q4 verbatim)
- Fallback is unconditional when < 2 bullet lines match

**Call-site audit (re-run):** `_append_forward_row` has exactly ONE call site (`bellows.py:1355`) plus its definition (`bellows.py:1423`). No new call sites since authoring.

## Task C — Docstring Amendment

`test_multiline_item_yields_single_line_row` docstring changed from:
- `"Multi-line item_text → valid single-line 7-pipe row."`
to:
- `"Narration-guard negative control: unbulleted multi-line → single row, trailing prose excluded."`

No assertion changes. All existing assertions in `TestForwardSingleLineItem` survive unchanged.

## Task D — Five New Tests (class `TestForwardMultiItemSplit`)

1. **`test_threshold_discriminator_one_bullet_one_unbulleted`** — 1 bullet + 1 unbulleted → fallback to first line (the unbulleted one). Asserts exactly 1 row carrying the unbulleted text, not the bullet. Distinguishes `>=2` from `>=1`.
2. **`test_multi_bullet_positive`** — 3 bullet lines → 3 rows, each valid 7-pipe, each carrying its own item text.
3. **`test_narration_with_bullets_negative_contiguous`** — 2 bullets followed immediately by unbulleted prose → 2 rows, prose excluded. Contiguous fixture (no blank line separation).
4. **`test_trailing_artifact_strip_multi_bullet`** — 2 bullets each ending with ` .` → artifact stripped on the multi-bullet path.
5. **`test_preamble_then_bullets`** — heading + 2 bullets → only bullets become rows, preamble excluded.

## Task E — Targeted Tests and Controls

**Targeted test tail (`tests/test_bellows.py`):**
```
======================== 180 passed, 1 warning in 4.73s ========================
```

175 pre-change + 5 new = 180. All pass.

### Negative Control (plan 62 narration guard)

```
=== NEGATIVE CONTROL (plan 62 narration guard) ===
Input lines: 'CANARY item text here\n\nNow commit the deposit.\nComplete. All 5 checks passed.\n'
Result: ['CANARY item text here']
Count: 1
"Now commit" absent: True
"All 5 checks" absent: True
```

### Positive Control (six-bullet block)

```
=== POSITIVE CONTROL (six-bullet block) ===
Input lines: '- Item alpha\n- Item beta\n- Item gamma\n- Item delta\n- Item epsilon\n- Item zeta\n'
Result: ['- Item alpha', '- Item beta', '- Item gamma', '- Item delta', '- Item epsilon', '- Item zeta']
Count: 6
```

---

## Output Receipt

### Status

**Complete**

### Deposits

- `bellows.py` — bullet-aware splitter (`BULLET_RE`, `sanitize_items`, updated `_append_forward_row`)
- `tests/test_bellows.py` — docstring amendment + 5 new tests in `TestForwardMultiItemSplit`
- `knowledge/development/forward-splitter-dev-2026-08-03.md` — this dev-log

### Ledger Updates

#### Prompt Feedback

The diagnostic's §Q4 implementation was directly usable as written — the 8-line sanitizer dropped into the module with only the routing change in `_append_forward_row` needed to integrate it. The plan's explicit mandate to NOT strip bullet markers and to ship §Q4 verbatim prevented a byte-for-byte-unchanged violation that an earlier draft would have introduced. The threshold discriminator test (Task D item 1) is the strongest guard in the set — without it, a `>=1` implementation passes every other test while inverting plan 62's guard.
