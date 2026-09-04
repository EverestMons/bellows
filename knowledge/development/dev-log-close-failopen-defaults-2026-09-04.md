# Dev Log — close-failopen-defaults — 2026-09-04

Plan 100037. Closes FO-1 and FO-3 identified in thread 119 diagnostic.

## FO-1: cycle_check manifest gate skips on no-stanza (cycle_check.py)

**Root cause.** `_manifest_validation_keys` returned `None` when `parse_manifest_stanza` returned `{}`. `{}` is returned for both "no `## Cycle Manifest` heading" and "heading with unparseable content" (e.g. `*(emitted at BAR_MET)*`). The call site uses `if stored is not None and ...` — so `None` silently skips the gate. A plan with no manifest, or a halted plan whose manifest was never filled, reached BAR_MET unchecked.

**Demonstrated by.** `knowledge/decisions/halted-executable-100031.md`: heading present, stanza is `*(emitted at BAR_MET)*`, gate silently passes.

**Fix.** Added two separate return arms before `manifest = parse_manifest_stanza(...)`:
- Arm A: `if not MANIFEST_HEADING_RE.search(plan_text): return frozenset()` — catches "no heading" without a parse call.
- Arm B: `if not manifest: return frozenset()` — catches "heading + unparseable stanza".
- Also changed `if not validation_val: return None` → `return frozenset()` so empty validation is not silently skipped.
- Kept `<declare>` and `N/A` returning `None` — these are legitimate mid-emission and no-walk-data values, not parse failures. Call site unchanged.

**Tests added.** `tests/test_cycle_check_manifest_provenance.py`:
- Test 1: stanza_does_not_parse_returns_continue (arm B)
- Test 2: no_manifest_heading_returns_continue (arm A)
- Test 3: positive_complete_stanza_bar_met (control)
- Test 4: positive_missing_one_key_continue (100033 gate still works)
- Test 5: gate_silent_mid_cycle (gate does not disturb non-BAR_MET verdicts)
- test_validation_empty_blocks: updated from BAR_MET expectation to CONTINUE

**Tests updated.** `tests/test_cycle_check.py`: `_make_plan` and `_build_ss_plan` helpers now include a full `## Cycle Manifest` stanza so plans that legitimately reach BAR_MET continue to do so. `--emit-manifest` tests updated to use `validation: <declare>` stubs (the pre-emission state).

## FO-3: plan_lint qa_steps: none demands banner (plan_lint.py)

**Root cause.** `if header.get("qa_steps"):` — `header["qa_steps"]` is always a string (parsed from bold-Markdown header). The string `"none"` is truthy in Python, so `qa_steps: none` (meaning "no QA steps") incorrectly set `has_qa = True` and demanded a Rule 20 banner.

**Fix.** Replaced truthy check with P4b normalization:
- Empty string and `"none"` (case-insensitive) → `has_qa` stays False.
- `"[comma-separated step numbers]"` (PLANNER_TEMPLATE placeholder) → WARN printed, `has_qa` stays False.
- All other values (real step numbers, `n/a`, etc.) → `has_qa = True`.

**Tests added.** `tests/test_plan_lint_qa_steps_none.py` (new file, 7 tests):
- Test 6: none no banner (core fix)
- Test 7: numeric demands banner (positive control)
- Test 8: absent qa_steps + QA heading demands banner (for-loop fallback)
- Test 9: empty normalizes
- Test 9b: placeholder warns + no FAIL
- Test 9c: n/a not normalized (corpus check)
- Test 10: none with banner exits 0 (advisory path)

## Mutants

`knowledge/mutants/close-failopen-defaults.json`: 6 mutants, one per codepath:
- M1 arm B None (kills test 1)
- M2 arm A None (kills test 2)
- M3 empty-validation None (kills test_validation_empty_blocks)
- M4 revert FO-3 normalization (kills test 6)
- M5 drop placeholder branch (kills test 9b)
- M6 drop qa-heading fallback (kills test 8)

## Numstat

Six files changed: `scripts/cycle_check.py`, `scripts/plan_lint.py`, `tests/test_cycle_check.py`, `tests/test_cycle_check_manifest_provenance.py`, `tests/test_plan_lint_qa_steps_none.py` (new), `knowledge/mutants/close-failopen-defaults.json` (new).
Dev log: `knowledge/development/dev-log-close-failopen-defaults-2026-09-04.md` (new — not counted in the six).
