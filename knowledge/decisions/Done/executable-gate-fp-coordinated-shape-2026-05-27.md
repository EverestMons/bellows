# Bellows — Coordinated gate-FP fix: CEO Flags null-token allowlist + Rule 22 (c) status-cell heuristic + Rule 22 (d) cell-scope match
**Date:** 2026-05-27 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## Context

Implements the 5c mixed-shape recommendation from `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md` (diagnostic shipped same day). Three independent false-positive bugs across two gates closed in one ship; daemon restart required at end.

**The three FPs and their fixes:**

1. **`_gate_ceo_flags`** at `gates.py:215-218` — fires on prose null-declarations like `"None. All anchor lines matched..."` because the parser's `txt.lower() not in ("none", "n/a")` exclusion only matches exact tokens. Fix: add `_is_null_flag_declaration(flag_text: str) -> bool` predicate at the gate site; filter null-declaration entries from the `flags` list before the `if flags:` check.

2. **`_gate_rule_22_verification` (c) row-status check** at `gates.py:527-556` — fires on enumerative tables (heading lists, proposal-ID maps) inside `## Verification Checks` sections because the existing section-scoping is too coarse (`## ` header level only). Fix: defer "missing status" failures while iterating each table; if no row in the current table matches `_is_positive_status_row()`, discard all deferred failures for that table (treat as non-verification table).

3. **`_gate_rule_22_verification` (d) hedging-detector** at `gates.py:558-568` — fires on domain terms (`pending` as state name, JSON field, function name) because the substring match is against the entire row, not the status cell. Fix: add `_hedging_in_status_vicinity(line: str, keyword: str) -> bool` predicate that splits the row into cells, identifies the status-bearing cell, and restricts the keyword match to that cell. Also bring the (d) loop under `in_verification_section` scoping (one-line addition).

**Why one executable for three fixes:** Diagnostic Q4 confirmed no cross-site interaction at the option level (the fixes are structurally independent), but they share the daemon restart, share regression-test infrastructure, and Fixes 2+3 share the iteration context within `_gate_rule_22_verification`. Bundling minimizes daemon-restart cost and lets QA verify all three FPs in one pass.

**Out of scope:**
- No governance changes (PLANNER_TEMPLATE, agent files).
- No new config schema (rejected BACKLOG option (b) per-project allowlist for hedging — overkill).
- No opt-out markers in QA reports (rejected BACKLOG option (c) for (c) — content-intrinsic heuristic preferred).

**Triggering artifacts (for fixture inspiration):**
- CEO Flags: `bellows/verdicts/resolved/processed-verdict-planner-template-bellows-operational-workarounds-2026-05-27-step-2.md`
- Rule 22 (c): `lessons-forge/knowledge/qa/plan-authoring-checklist-qa-2026-05-27.md` + `bellows/verdicts/resolved/processed-verdict-planner-template-plan-authoring-checklist-2026-05-27-step-3.md`
- Rule 22 (d): `bellows/verdicts/resolved/processed-verdict-stuck-state-color-override-2026-05-22-step-2.md` (or whichever Step 4 deferred-validation verdict captures the 5 `pending` FPs cited in the diagnostic Section A3)

## How to Run This Plan

Two-step plan, sequential. Step 1 ships the code in three coordinated edits; Step 2 verifies all three FPs are closed and no regressions exist.

---

## STEP 1 — Implement three gate fixes

**Agent:** Bellows Developer
**Estimated tokens:** ~30k

Implement three independent gate-FP fixes in one coordinated edit to `gates.py`. The findings file `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md` is the authoritative spec; cite it for any design choice.

### Read order

1. `bellows/agents/BELLOWS_DEVELOPER.md` — specialist context.
2. `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md` — findings. Section E (Recommendation) is the spec; Section A (Q1 call-site characterization) shows the current code; Section D (Q4 matrix) shows the fix-shape options chosen.
3. `bellows/gates.py` — current state. Focus on lines 59-84 (HEDGING_KEYWORDS + `_is_positive_status_row`), 215-218 (`_gate_ceo_flags`), 480-568 (`_gate_rule_22_verification` including (c) and (d) sub-checks).
4. `bellows/parser.py` — lines 28-36 (ceo_flags extraction). Read-only — no edit here.
5. `bellows/tests/test_gates.py` — locate existing tests for `_gate_ceo_flags`, `_gate_rule_22_verification` (c), and (d). Grep for `ceo_flags`, `rule_22_verification`, `pending`, `_is_positive_status_row`. Note the test fixtures' table shapes (especially anything with `## Deliverable Verification` headers from the 2026-05-24 ship).

### Changes to implement

**Fix 1 — CEO Flags null-token allowlist (gate-side):**

Add a helper at the top of `gates.py` (near `_is_positive_status_row` at line 71 for symmetry):

```python
def _is_null_flag_declaration(text: str) -> bool:
    """True if the text is a null-declaration (no flags raised)."""
    ...
```

Match prefix (case-insensitive, after stripping leading whitespace) against null tokens: `none`, `n/a`, `no flags`, `no flag`, `nothing`, `clean`, `no issues`. The match must be prefix-based with a word boundary or punctuation boundary AFTER the token — so `"None. All anchor lines..."` matches (boundary is `.`) but `"none-of-the-above..."` does not (boundary is `-`, not punctuation/whitespace). A clean implementation: regex match against `^(none|n/a|no flags?|nothing|clean|no issues)\b` (case-insensitive) on `text.strip()`.

Then in `_gate_ceo_flags` at `gates.py:215-218`, filter the flags list through `_is_null_flag_declaration` before the `if flags:` check:

```python
def _gate_ceo_flags(parsed, failures):
    flags = [f for f in parsed.get("ceo_flags", []) if not _is_null_flag_declaration(f)]
    if flags:
        failures.append({"gate": "ceo_flags", "evidence": "; ".join(flags)})
```

**Fix 2 — Rule 22 (c) status-cell heuristic (defer-and-discard pattern):**

In `_gate_rule_22_verification` at `gates.py:527-556`, modify the row-status iteration:
- When entering a new table (transition `not in_data` → `in_data` via `_TABLE_SEPARATOR_RE`), reset two table-scoped state variables: `current_table_failures: list = []` and `current_table_has_positive_row: bool = False`.
- For each data row inside `in_verification_section` AND `in_data`:
  - If `_is_positive_status_row(line)` returns True, set `current_table_has_positive_row = True`.
  - Otherwise (current behavior), build the failure dict and append to `current_table_failures` (NOT directly to `failures`).
- When the table ends (transition `in_data` → `not in_data`, either via blank line or section-end): if `current_table_has_positive_row`, extend `failures` with `current_table_failures`. Otherwise discard.

The `❌` immediate-failure branch (gates.py:548-549 approx) stays as-is — explicit failure markers always fire, regardless of table type.

**Fix 3 — Rule 22 (d) cell-scope match + section-scoping extension:**

Add a helper near `_is_positive_status_row`:

```python
def _hedging_in_status_vicinity(line: str, keyword: str) -> bool:
    """True if the hedging keyword appears in or adjacent to the row's status-bearing cell."""
    ...
```

Implementation: split the row by `|` into cells. Identify the status cell (the cell that contains a positive-status token per the same logic as `_is_positive_status_row`, OR the last non-empty cell if no positive-status token found — handle both since `_is_positive_status_row` already handles the disambiguation). Check whether the keyword appears in the status cell or the cell immediately before it (status tokens sometimes appear in a "Result" cell adjacent to a "Notes" cell containing context).

Cell adjacency rule: match in the status cell itself, OR in any cell that contains the status token (covers cases where status is embedded in a multi-token cell). Do NOT match in description/test-name/evidence cells.

In the (d) loop at `gates.py:558-568`:
- Add `if not in_verification_section: continue` as the first line inside the loop (section-scoping extension).
- Replace `if kw in lower:` with `if _hedging_in_status_vicinity(line, kw):`.

**The (d) loop currently uses its own `enumerate(lines, 1)` separate from the (c) loop.** Keep them separate — do NOT merge into a single pass. The (c) loop has table-scoped state (Fix 2's defer-and-discard); the (d) loop is row-scoped. Merging would entangle state.

### Constraints

- No edits outside `gates.py`. The parser at `parser.py` stays unchanged.
- All three helpers (`_is_null_flag_declaration`, table-scoped state in (c), `_hedging_in_status_vicinity`) are module-private (underscore prefix).
- Preserve the 2026-05-24 `_is_positive_status_row()` helper and its existing call sites unchanged.
- The (c) `❌` immediate-failure branch must still fire regardless of `current_table_has_positive_row` — explicit failure markers bypass the table-type heuristic.
- No new dependencies. Standard library only.

### Output Receipt requirements

- List exact line ranges modified in `gates.py` per fix (use post-edit line numbers).
- For each helper added, paste the final function signature + docstring (no body).
- Confirm `parser.py` was NOT modified.
- Confirm `_is_positive_status_row()` was NOT modified.
- Run `python3 -c "import gates; print('ok')"` from the bellows directory; paste output. Catches import errors before QA.

**Deposits:**

- `bellows/gates.py`
- `bellows/knowledge/development/gate-fp-coordinated-shape-2026-05-27.md`

---

## STEP 2 — QA: verify three FPs closed, no regressions

**Agent:** Bellows QA
**Estimated tokens:** ~25k

Verify each of the three fixes closes its triggering FP and produces no regressions in adjacent test surfaces. This is a targeted QA: gate-level unit tests against `gates.py`, plus reproduction of each FP using its triggering artifact's content as a test fixture.

### Read order

1. `bellows/agents/BELLOWS_QA.md` — specialist context.
2. `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md` — findings (the spec).
3. `bellows/knowledge/development/gate-fp-coordinated-shape-2026-05-27.md` — DEV log from Step 1.
4. `bellows/gates.py` — post-Step-1 state. Verify Step 1's claimed line ranges.
5. `bellows/tests/test_gates.py` — locate existing tests for the three affected sites.
6. The three triggering artifacts cited in Context — extract the specific row content that produced each FP for use as test fixtures.

### Verification deliverables

**Deliverable A — Code shape verification (cite line numbers, paste snippets):**

- `_is_null_flag_declaration` exists with correct signature and is consumed by `_gate_ceo_flags`.
- `_gate_rule_22_verification` (c) check uses table-scoped state (`current_table_failures`, `current_table_has_positive_row`) and defer-and-discard pattern.
- `_hedging_in_status_vicinity` exists with correct signature and is consumed by the (d) loop.
- (d) loop has `if not in_verification_section: continue` as first line of loop body.
- `parser.py` is unchanged (cite `git diff parser.py` output — should be empty).
- `_is_positive_status_row()` is unchanged.

**Deliverable B — Per-fix FP reproduction tests:**

Add three new tests in `tests/test_gates.py` (or appropriate test file) — one per fix. Each test must use content extracted from the actual triggering artifact (not a synthetic minimal repro):

1. `test_ceo_flags_null_declaration_prose_passes` — assertion: `_gate_ceo_flags` with `ceo_flags=["None. All SA-cited anchor lines matched verbatim. No blueprint-vs-file mismatches. No prose adjustments needed."]` produces zero failures.
2. `test_rule_22_c_enumerative_table_inside_verification_section_passes` — assertion: a QA-report-shaped string containing a `## Verification Checks` section with a 3-column enumerative table (e.g., `| # | Line | Title |`) produces zero (c) failures for that table.
3. `test_rule_22_d_pending_in_description_cell_passes` — assertion: a verification row with `pending` in the description cell but `✅` in the status cell produces zero (d) failures.

**Deliverable C — Per-fix counter-tests (verify gate still fires on real signals):**

Add three counter-tests:

1. `test_ceo_flags_real_flag_still_fires` — `_gate_ceo_flags` with `ceo_flags=["warning: build failed on macOS"]` produces one failure.
2. `test_rule_22_c_genuine_missing_status_still_fires` — a verification-type table (has at least one ✅ row) with a row missing status produces one (c) failure for that row.
3. `test_rule_22_d_pending_in_status_cell_still_fires` — a verification row with `pending` IN the status cell produces one (d) failure.

**Deliverable D — Adjacent surface regression check:**

Run the full `tests/test_gates.py` suite. Paste pytest output (last 20 lines). Required: zero new failures. Five known carry-overs (the 4 worktree-context `test_decisions.py` failures + 1 long-standing `test_run_step_timeout`) remain acceptable.

Specifically confirm pass-through on these adjacent test classes:
- All existing `_gate_ceo_flags` tests (parser-side null-token handling untouched).
- All existing (c) check tests that exercise the 2026-05-24 section-scoping (`## Deliverable Verification` header fixtures must still pass — these tables have positive-status rows, so the defer-and-discard pattern accepts the failures correctly).
- All existing (d) check hedging tests where the keyword appears in the status cell (should still fire).

**Deliverable E — Rule 20 self-check.**

Run the canonical Python block from `RULE_20_SELF_CHECK_BLOCK.md` against the QA report. Paste output verbatim including the `RULE 20 SELF-CHECK: PASSED` line.

### Output Receipt requirements

- Deliverables A-E each with a section header.
- Pass/fail status per deliverable in a verification table at the top.
- For Deliverable D, report total test count, passed/failed/skipped, time elapsed.
- Flags for CEO: any deviation from the spec, any test that required fixture modification beyond the documented `## Deliverable Verification` header pattern, any test fixture where the actual FP behavior diverged from the diagnostic's prediction.

**Deposits:**

- `bellows/knowledge/qa/executable-gate-fp-coordinated-shape-2026-05-27.md`
- `bellows/tests/test_gates.py`

---

## Daemon restart

After Step 2 ships and verdict continues to Done, the daemon MUST be restarted to load the new `gates.py`. Bellows does not hot-reload gate code. The session-wrap should include the restart command in operational notes for CEO.
