# Gate FP Coordinated Shape — DEV Log

**Date:** 2026-05-27
**Agent:** Bellows Developer
**Step:** 1
**Plan:** `executable-gate-fp-coordinated-shape-2026-05-27`
**Spec:** `knowledge/research/gate-fp-coordinated-shape-2026-05-27.md`

---

## Per-Fix Edit Summary

### Fix 1 — CEO Flags null-token allowlist (lines 70–75, 246–249)

**Added:** `_NULL_FLAG_RE` compiled regex at line 70 and `_is_null_flag_declaration(text: str) -> bool` helper at lines 73–75.

**Modified:** `_gate_ceo_flags` at lines 246–249 — filters `ceo_flags` list through `_is_null_flag_declaration` before the `if flags:` check.

**Design choice:** Used `re.compile` at module level for the null-token pattern (`^(none|n/a|no flags?|nothing|clean|no issues)\b`, case-insensitive). The `\b` word boundary handles punctuation boundaries (`.`, `,`, `;`) after the null token without requiring explicit punctuation enumeration. `text.strip()` is applied inside the helper to handle leading whitespace in flag text.

### Fix 2 — Rule 22 (c) defer-and-discard (lines 558–611)

**Modified:** The (c) loop in `_gate_rule_22_verification` now uses table-scoped state variables `current_table_failures` (list) and `current_table_has_positive_row` (bool).

**Flush points:** Table-end is detected at three transition points:
1. Non-pipe line (`"|" not in stripped`) while `in_data` is True
2. New `## ` section header while `in_data` is True
3. New `_TABLE_SEPARATOR_RE` match while `in_data` is True (consecutive tables)
4. End of loop (final table flush at line 610–611)

At each flush point: if `current_table_has_positive_row` is True, deferred failures are extended into `failures`; otherwise they are discarded (table treated as non-verification / enumerative).

**`❌` immediate-fire preserved:** Explicit `❌` rows still append directly to `failures` (line 595–600), bypassing the defer-and-discard pattern per plan constraint.

### Fix 3 — Rule 22 (d) cell-scope match + section-scoping (lines 94–115, 613–629)

**Added:** `_hedging_in_status_vicinity(line: str, keyword: str) -> bool` helper at lines 94–115. Implementation: splits the row by `|`, identifies cells containing positive-status tokens (using the same token-matching logic as `_is_positive_status_row`), and checks for the hedging keyword only in those status-bearing cells.

**Modified:** The (d) loop at lines 613–629:
- Added its own `in_verification_section_d` tracking (separate from the (c) loop's state)
- `if not in_verification_section_d: continue` as section-scoping extension (line 620–621)
- Replaced `if kw in lower:` with `if _hedging_in_status_vicinity(line, kw):` (line 624)

**Design choice — cell-scope strictness:** The helper matches hedging keywords ONLY in cells that contain a positive-status token (✅ substring or exact text-token equality). This is stricter than the plan's "cell immediately before" suggestion — the "cell before" approach would still produce FPs when the description/test-name cell is immediately before the status cell (which is the common table layout). The overriding plan constraint "Do NOT match in description/test-name/evidence cells" guided this choice.

---

## Existing Tests Affected

Two existing tests will need fixture updates in Step 2 (QA):

1. **`test_rule_22_qa_hedging_keyword`** — Table has no `## Verification` header. After the (d) section-scoping extension, `in_verification_section_d` remains False → hedging not inspected → test assertion of 1 failure will get 0. The test fixture needs a `## Deliverable Verification` header.

2. **`test_rule_22_qa_both_fail_and_hedging`** — The hedging keyword "estimated" appears in the Evidence cell (`estimated to work`), not the status cell (`✅`). After cell-scope matching, `_hedging_in_status_vicinity` returns False → test assertion of 2 failures will get 1. The test fixture needs the hedging keyword in the status cell (e.g., `✅ estimated`).

Both changes are expected behavioral improvements — the old tests demonstrated the exact FP patterns this fix addresses.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented three coordinated gate-FP fixes in `gates.py`: (1) CEO Flags null-token allowlist via `_is_null_flag_declaration`, (2) Rule 22 (c) defer-and-discard pattern for enumerative table filtering, (3) Rule 22 (d) cell-scope hedging match via `_hedging_in_status_vicinity` with section-scoping extension.

### Files Deposited
- `knowledge/development/gate-fp-coordinated-shape-2026-05-27.md` — this DEV log

### Files Created or Modified (Code)
- `gates.py` — three fixes: lines 70–75 (Fix 1 helper), 94–115 (Fix 3 helper), 246–249 (Fix 1 gate), 558–611 (Fix 2 defer-and-discard), 613–629 (Fix 3 (d) loop)

### Decisions Made
- Cell-scope strictness: `_hedging_in_status_vicinity` matches only in cells containing positive-status tokens, not "cell immediately before" — prevents FPs where description cell is adjacent to status cell
- Separate `in_verification_section_d` tracking in (d) loop rather than sharing (c) loop's state — keeps the two loops independent per plan constraint

### Flags for CEO
- None

### Flags for Next Step
- Two existing tests (`test_rule_22_qa_hedging_keyword`, `test_rule_22_qa_both_fail_and_hedging`) will fail and need fixture updates — see "Existing Tests Affected" section above
- Edge case to monitor: hedging keywords in evidence cells adjacent to status cells (e.g., `| Check | ✅ | should pass based on review |`) are now silenced. This is the intended behavior per the plan's cell-scope design, but QA should verify no genuine hedging signals are missed.
