---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Removed plan_lint check (i) (halt-routing plan-id coverage) and its five tests, per CEO decision to drop the check after its corpus sweep showed 8/11 false positives. Checks (g) and (h) remain byte-identical and verified alive via positive controls.

### Removed Block (check (i), scripts/plan_lint.py lines 250–271)
```python
                # (i) Halt-routing plan-id coverage (WARN-only): backtick-quoted three-digit
                # plan ids in the questions region must appear in the halt-routing line.
                # Scoped to the mechanical backtick-quoted class; prose refs outside scope.
                # Skip silently when the plan has no questions region — halt-routing is a
                # diagnostic concept; executables have steps, not questions.
                pre_dc_text = plan_text[:dc_match.start()]
                has_questions_region = bool(re.search(r'^## Questions\b', pre_dc_text, re.MULTILINE))
                if has_questions_region:
                    plan_id_pat = re.compile(r'`(\d{3})`')
                    pre_dc_ids = set(plan_id_pat.findall(pre_dc_text))
                    halt_rout_line = None
                    for ln in pre_dc_text.splitlines():
                        if re.search(r'halt[\s-]*rout', ln, re.IGNORECASE):
                            halt_rout_line = ln
                            break
                    if pre_dc_ids:
                        if halt_rout_line is not None:
                            halt_ids = set(plan_id_pat.findall(halt_rout_line))
                            for pid in sorted(pre_dc_ids - halt_ids):
                                print(f"WARN: plan id `{pid}` in questions region but absent from halt-routing")
                        else:
                            print("WARN: no halt-routing line found")
```

### Five Removed Test Names
1. `test_lint_halt_routing_missing_id_warns`
2. `test_lint_halt_routing_full_coverage_no_warn`
3. `test_lint_no_halt_routing_line_warns`
4. `test_lint_no_plan_ids_no_halt_routing_no_warn`
5. `test_lint_executable_with_plan_ids_no_i_warn`

### Four Surviving Test Names and Results
1. `test_lint_ledger_ascending_no_warn` — PASSED
2. `test_lint_ledger_out_of_order_warns` — PASSED
3. `test_lint_ledger_no_entries_no_warn` — PASSED
4. `test_lint_stale_closing_warns` — PASSED

### Positive Control: (g) — ledger ordering
```
$ python3 scripts/plan_lint.py /Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/diagnostic-299.md
WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)
WARN: Drafting Cycle ledger out of order: C15 before C13
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
exit code: 0
```

### Positive Control: (h) — stale closing disclaimer
```
$ python3 scripts/plan_lint.py <fixture with lens results + closing "no lens has read">
WARN: Drafting Cycle Closing claims no lens has read the artifact, but lens results are recorded
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
exit code: 0
```

### Targeted Test Run
```
49 passed, 797 deselected, 1 warning in 1.90s
```
Predicted: 49 (54 − 5). Actual: 49.

### BEFORE Sweep
Saved to `knowledge/development/sweep-before.txt`. 11 halt-routing (i) warnings across the five-root corpus (1362 plans), 1 ledger (g) warning (diagnostic-299).

### Files Deposited
- `knowledge/development/remove-check-i-dev-log-2026-08-06.md` — this file
- `knowledge/development/sweep-before.txt` — BEFORE corpus sweep raw output

### Files Created or Modified (Code)
- `scripts/plan_lint.py` — removed check (i) block (22 lines)
- `tests/test_plan_lint.py` — removed 5 tests for check (i)

### Decisions Made
- Kept `test_lint_degenerate_empty_block_new_checks_no_crash` (tests (g)/(h)/(i) degenerate case jointly; its (i) assertion trivially passes with (i) gone, and it still covers (g)/(h) degenerate behavior)

### Flags for CEO
- None

### Flags for Next Step
- None

#### Prompt Feedback
