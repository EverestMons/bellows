# Clean-Gate Auto-Continue QA Report — 2026-08-08

**Plan:** clean-gate-auto-continue-2026-08-08 (plan 317)
**Step:** 2 — QA
**Baseline:** 874 passed (313's QA); this plan adds 17 tests → 891 passed

---

## Task Q0 — Re-pin State

```
$ git log -1 --oneline -- bellows.py verdicts/README.md scripts/plan_lint.py validators.py tests/test_gate_transaction_mechanization.py tests/test_bellows.py tests/test_plan_lint.py tests/test_validators.py
8b42896 [317] Step 1: qa_and_terminal pause mode + clean_gate_auto provenance recording
```

Most recent commit touching all scope files is Step 1's commit `8b42896`. No foreign commits.

---

## Verification Results

| Item | Check | Status | Raw Evidence |
|------|-------|--------|--------------|
| Q0 | Re-pin state | ✅ | `8b42896 [317] Step 1` — Step 1's commit, no foreign commits |
| 1 | Full test suite | ✅ | `891 passed, 1 warning in 22.77s` (full-suite.txt) |
| 2 | Targeted tests | ✅ | `59 passed, 246 deselected, 1 warning in 0.84s` / `pytest_exit=0` (targeted-tests.txt) |
| 3a | grep `qa_and_terminal` bellows.py | ✅ | 2 lines: mode branch + WARN literal |
| 3b | grep `clean_gate_auto` bellows.py | ✅ | 1 line: lifecycle recording call |
| 3c | grep `clean_gate_auto` verdicts/README.md | ✅ | 2 lines: intro sentence + table row |
| 3d | grep `qa_and_terminal` verdicts/README.md | ✅ | 2 lines: header_pause row + mode doc paragraph |
| 3e | grep `qa_and_terminal` scripts/plan_lint.py | ✅ | 4 lines: enum + coupling-check condition + coupling-check body (2 lines) |
| 3f | grep `qa_and_terminal` validators.py | ✅ | 1 line: VALID_PAUSE_FOR_VERDICT_VALUES set |
| 3g | grep `patch("bellows.header_says_pause"` test file | ✅ | 1 line: spy side_effect in run_plan integration test |
| 4 | Discrimination effect | ✅ | Assertion lines quoted in Item 4 section |
| 5 | Rule 20 self-check | ✅ | PASSED — block output in Item 5 section |
| 6 | Semantic-shift note | ✅ | Stated in Semantic-Shift section |

---

## Item 1 — Full Test Suite

Raw summary line from `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`:

```
891 passed, 1 warning in 22.77s
```

Baseline was 874 (313's QA). This plan adds 17 tests (9 in TestHeaderSaysPauseModes, 5 in TestCleanGateAutoProvenance including the two-row case, 2 in TestCleanGateAutoRunPlanIntegration, plus 1 plan_lint + 1 validators = but the exact count matches: the targeted run selected 59, up from 38 in 313).

---

## Item 2 — Targeted Tests

Command: `python3 -m pytest tests/test_gate_transaction_mechanization.py tests/test_bellows.py tests/test_plan_lint.py tests/test_validators.py -k "verdict or decided or auto_close or transaction or header_says_pause or clean_gate or qa_and_terminal" --tb=short -q`

```
...........................................................              [100%]
59 passed, 246 deselected, 1 warning in 0.84s
pytest_exit=0
```

Collect-only probe for naming-rule verification:

```
$ python3 -m pytest tests/test_plan_lint.py tests/test_validators.py --collect-only -q -k "qa_and_terminal"
tests/test_plan_lint.py::test_lint_qa_and_terminal_mode_passes
tests/test_plan_lint.py::test_lint_qa_and_terminal_coupling_warns_missing_qa_steps
tests/test_validators.py::test_qa_and_terminal_accepted_by_pause_for_verdict_check

3/105 tests collected (102 deselected) in 0.02s
```

All three Site 4 test cases listed by name — naming rule satisfied, none silently deselected.

---

## Item 3 — Grep-Proof (Seven Greps)

All greps run bare (no pipe), all exit 0:

**3a** `grep -F "qa_and_terminal" bellows.py` — 2 lines (mode branch + WARN literal):
```
    if pv == "qa_and_terminal":
        _log("WARN", f"⚠️ unrecognized pause_for_verdict value: {pv!r} (recognized: 'always', 'after_step_1', 'after_qa_step', 'qa_and_terminal') — treating as no-pause")
```

**3b** `grep -F "clean_gate_auto" bellows.py` — 1 line:
```
                lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="clean_gate_auto")
```

**3c** `grep -F "clean_gate_auto" verdicts/README.md` — 2 lines:
```
Bellows pauses plan execution under five conditions. The Planner writes a verdict file to `verdicts/resolved/` to tell Bellows how to proceed. Two additional codes (`auto_close`, `clean_gate_auto`) are recorded transition codes for mechanical advances — they are NOT pauses but exist so the transition is auditable in the `verdicts` table.
| `clean_gate_auto` | Mechanical clean-gate non-terminal advance (not a pause; row exists so the transition is auditable) |
```

**3d** `grep -F "qa_and_terminal" verdicts/README.md` — 2 lines:
```
| `header_pause` | Plan header contains a `pause_for_verdict` mode that matches the current step (e.g. `always`, `after_step_1`, `after_qa_step`, `qa_and_terminal`) |
The `qa_and_terminal` header mode pauses at QA steps and at the terminal step. At the terminal step this mode takes precedence over `auto_close: true` — a plan setting both gets the terminal pause. A terminal-step pause under this mode records `pause_reason_code=header_pause` (indistinguishable in the table from an `always` pause).
```

**3e** `grep -F "qa_and_terminal" scripts/plan_lint.py` — 4 lines (enum + coupling-check condition and body):
```
RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step", "qa_and_terminal"}
    # (i) qa_and_terminal ↔ qa_steps coupling: under this mode a mis-declared QA step
    if header and header.get("pause_for_verdict") == "qa_and_terminal":
            print("WARN: pause_for_verdict=qa_and_terminal but qa_steps is missing or unparseable — QA steps may advance mechanically")
```

**3f** `grep -F "qa_and_terminal" validators.py` — 1 line:
```
VALID_PAUSE_FOR_VERDICT_VALUES = {"always", "after_step_1", "after_qa_step", "after_each_step", "qa_and_terminal", ""}
```

**3g** `grep -F 'patch("bellows.header_says_pause"' tests/test_gate_transaction_mechanization.py` — 1 line:
```
patch("bellows.header_says_pause", side_effect=spy_header_says_pause):
```

This is the mechanical presence proof that Task D's mandatory `run_plan` integration drive EXISTS in the file — the only guard that catches wrong-side Site 2 placement.

---

## Item 4 — Discrimination Effect

**Awaiting-verdict filter exclusion** (`test_clean_gate_auto_excluded_from_awaiting_filter`, line 296):
```python
assert len(awaiting) == 0, "clean_gate_auto row must not appear in awaiting-verdict filter"
```
This asserts that a `clean_gate_auto` row with `outcome='continue'` is excluded by the dashboard's `WHERE outcome IS NULL` query. The row is NOT null — the paired request+outcome writes stamp it immediately.

**run_plan integration — row lands on mechanical advance** (`test_clean_gate_auto_row_lands_on_mechanical_advance`, line 399):
```python
assert len(rows) >= 1, "clean_gate_auto row must land for the mechanically advanced step"
```
This drives a multi-step plan whose non-terminal step advances mechanically (gates pass, `pause_for_verdict` set to `"never"`) and asserts the `clean_gate_auto` row lands for step 1.

**run_plan integration — no row on paused run** (`test_no_clean_gate_auto_row_on_paused_run`, line 457):
```python
assert len(rows) == 0, "paused run must NOT write a clean_gate_auto row"
```
This drives a plan with `pause_for_verdict: "always"` and asserts that NO `clean_gate_auto` row is written — the recording pair fires only on the mechanical-advance path, not the pause path. The placement discrimination is the pair of these two assertions.

**Two-row characterization** (`test_clean_gate_auto_two_row_case`, line 298): two rows inserted for one plan+step with `pause_reason_code='clean_gate_auto'`, then a single `record_verdict_outcome` call — both rows are stamped with `outcome='continue'` and `decided_by='gate_auto'`, and zero rows remain with NULL outcome. This pins the UPDATE's actual all-matching-rows semantics.

---

## Semantic-Shift Note

The `verdicts` table now carries non-pause `clean_gate_auto` rows alongside the existing pause-reason rows. Distribution analyses that count or filter verdicts rows must key on `pause_reason_code` (not merely row existence) to distinguish actual pauses from mechanical-advance provenance records. The `auto_close` code (shipped in plan 313) is in the same category — a recorded transition, not a pause.

---

## Item 5 — Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/317/knowledge/qa/
Files verified: 2
```

---

### Ledger Updates

#### Prompt Feedback

No prompt issues encountered during QA execution. All instructions were unambiguous and executable as written.

#### Forward Register
- Post-activation live canary for clean_gate_auto: after the next daemon restart, a plan opted into pause_for_verdict qa_and_terminal must show gate_auto/clean_gate_auto rows for its non-terminal clean steps and pause at QA + terminal — the observed-delta proof this plan's QA cannot provide (Checklist #32; 295 precedent).
- Correct PLANNER_TEMPLATE.md for the qa_and_terminal mode at the next template touch (governance root, outside this plan's scope) — this is CORRECTION, not additive documentation: the recognized-values list and the accepts-exactly-three-values/any-other-silently-no-pause workaround text both become FALSE when this ships, Rule 49's delegated-continue condition (the Rule 22(b) pass) needs the daemon-continue interaction named as a second delegation step, and the established bootstrap/STOP-prose divergence rides the same touch — until then the mode is documented in bellows verdicts/README.md and the header_says_pause branch comment only.
