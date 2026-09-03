# Dev Log — qa-predeclaration — 2026-09-03

**Plan:** 100028 | **Step:** 1 (DEV) | **Check:** (v) no-pytest QA step without pre-declaration clause

## Item 1 — Load-bearing pin verification

All pins re-derived before implementation. Measured values supersede authoring-time values where they differ.

**P1 — target sha:**
```
shasum -a 256 scripts/plan_lint.py
→ e19f3be6d62419126bdf6b1c62b3272f5f2f5e9cf25816f4b5cec2d869402047  scripts/plan_lint.py
   901 lines
```
MATCH ✓

**P2 — insertion anchor (`dc_block = None`, count-1, L373):**
```
/usr/bin/grep -cF "    dc_block = None" scripts/plan_lint.py → 1
```
MATCH ✓ (note: the plan's description says `dc_block = {}` but the live code has `dc_block = None` at L373 — measured live value used; the anchor still resolves count-1 at L373)

**P3 — retag anchor (`thread 70/77` at L371, count-1):**
```
/usr/bin/grep -cF "thread 70/77" scripts/plan_lint.py → 1
```
MATCH ✓

**P4 — provenance (L370-372 = e088d05, L373 = 9c06524):**
```
git blame -L 370,373 scripts/plan_lint.py → e088d05 / 9c06524
```
MATCH ✓

**P5 — gate branch structure:**
`_gate_qa_test_result` at `gates.py:769`. Branch 1 (no .txt → FAIL) at `:784-786`. Branch 2 (no pytest summary → FAIL) at `:812-814`. No test_scope read at any point. MATCH ✓

**P6 — refutation (548's evidence file, 63 lines, 0 regex hits, positive control True):**
```
lines 63 hits 0
control True
```
MATCH ✓ — plan premise holds.

**P7 — `_STANZA_REQUIRED` at `:552-555`, 10 fields unchanged:**
MATCH ✓

**P8 — 19 `results.append` calls (9 FAIL, 7 PASS, 3 local in `_extract_hex_tokens`):**
MATCH ✓

**P9 — suite baseline (deferred to QA step).**

**P10 — no in-flight plans (0 claimed/in_progress/awaiting_verdict):**
```
sqlite3 lifecycle.db → 0
```
MATCH ✓

**P13 — gate simulation:**
Step 2 (QA): `passed=True, is_qa_step=True, failures=[]` ✓
Negative control: `no parseable pytest summary — cannot certify clean; pausing` ✓
Step 1: `is_qa_step=False` ✓ (P11 confirmed at the gate)

## Item 2 — tests written first, confirmed failing

Created `tests/test_plan_lint_qa_predeclaration.py` (9 tests). Before implementation:
- 5 tests failed (those requiring `(v) WARN` in output)
- 4 tests passed (those requiring no `(v) WARN` or no traceback — correct, as the check didn't exist yet)

Test 9 fixture required a fix: "No pre-declaration clause here" contains the token `pre-declar`, accidentally suppressing the check. Reworded to "Omits the required clause entirely." before implementation.

## Item 3 — check (v) implemented

Inserted immediately before `    dc_block = None` (P2 anchor, L373 pre-edit). The check:
- Reads `test_scope` from header with the `if header else ""` guard
- Opens its own `for hl, sn_str in step_headers:` loop (not inside (u)'s loop)
- QA-step predicate: `gates._gate_is_qa_step(plan_text, sn, plan_header=header)`
- Suppression: `pre-declar`, `gate note`, OR `qa_test_result` in the step's own text (step-scoped)
- Print WARN only — does not append to results list (exit code unaffected)

All 9 tests pass after implementation.

## Item 4 — (u)'s thread tag narrowed

`thread 70/77` → `thread 77` at L371 (count-1 anchor). Verified count-1 post-edit. No other test asserts this exact string.

## Item 5 — mutants manifest

Created `knowledge/mutants/qa-predeclaration-plan_lint.json` with 8 mutants (v-drop-scope-gate, v-invert-suppression, v-narrow-to-gate-name-token, v-widen-suppression-to-whole-plan, v-drop-header-guard, v-swap-gate-predicate, v-only-last-step, v-append-as-fail). Pending mutation_check run after commit.

## Item 6 — funnel re-measurement

Run post-edit against all 543 Done plans using `gates._gate_is_qa_step`:

| population | authoring-time | measured 2026-09-03 | delta |
|---|---|---|---|
| Done plans | 543 | 543 | 0 |
| QA steps (gate predicate) | 306 | 305 | -1 |
| …none-scope | 13 | 13 | 0 |
| …clause present | 4 | 4 | 0 |
| …fires (no clause) | 9 | 9 | 0 |

Delta on QA steps (-1) does not change the class of the result — same 9 fires, same 4 clause-carriers. Supersede rule applied: measured values supersede. No HALT condition.

Fires: executable-100013.md (step 1, post-gate true positive) + 8 pre-gate plans (expected, closed). No new post-gate fires. Class of result unchanged.
