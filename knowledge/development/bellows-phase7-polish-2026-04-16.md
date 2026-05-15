# Bellows Phase 7 Polish — Flag Format Tolerance + Diagnostic Auto-Close

**Date:** 2026-04-16
**Plan:** executable-bellows-phase7-polish-2026-04-16.md
**Step:** 1 (DEV)

## Summary

Two mechanical fixes addressing problems surfaced by the first real test of Phase 7's verdict layer:

1. **Parser flag format tolerance** — the original `ceo_flags` extraction only recognised `### Flags for CEO` headings with bulleted items. Agent output using `## CEO Flag` (H2) and paragraph-form content bypassed Gate 2 silently. Parser now tries six heading/marker variants and supports both bulleted and paragraph content.
2. **Diagnostic auto-close** — diagnostic plans passed all gates (is_qa_step=False, failures=0) but stranded because `bellows.py` had no path for moving a clean diagnostic to `Done/`. Added a conditional branch in `run_plan()` that runs before the strand check: when the plan is a diagnostic, gates pass, and the step is not QA, Bellows logs to the verdict ledger, moves the plan to `Done/`, and sends a Pushover.

No architectural changes. Executables are unaffected — they still require an explicit QA step to reach `Done/`.

## Changes Per File

### MODIFIED: parser.py (~30 lines changed in the `ceo_flags` block)

**Before:**
```python
ceo_flags = []
flags_match = re.search(r"### Flags for CEO\s*\n(.*?)(?:\n###|\Z)", result_text, re.DOTALL)
if flags_match:
    for line in flags_match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- ") and line[2:].strip() and line[2:].strip() != "None":
            ceo_flags.append(line[2:].strip())
```

**After:**
```python
ceo_flags = []
flag_patterns = [
    r"###\s+Flags for CEO\s*\n(.*?)(?=\n##|\Z)",
    r"##\s+Flags for CEO\s*\n(.*?)(?=\n##|\Z)",
    r"###\s+CEO Flags?\s*\n(.*?)(?=\n##|\Z)",
    r"##\s+CEO Flags?\s*\n(.*?)(?=\n##|\Z)",
    r"\*\*Flags for CEO:\*\*\s*(.*?)(?=\n##|\Z)",
    r"\*\*CEO Flag:\*\*\s*(.*?)(?=\n##|\Z)",
]
flags_content = None
for pat in flag_patterns:
    m = re.search(pat, result_text, re.DOTALL)
    if m:
        flags_content = m.group(1)
        break

if flags_content is not None:
    lines = [l.strip() for l in flags_content.splitlines()]
    meaningful = [l for l in lines if l and l != "---"]
    bulleted = [l for l in meaningful if l.startswith("- ")]
    if bulleted:
        for line in bulleted:
            flag_text = line[2:].strip()
            if flag_text and flag_text.lower() not in ("none", "n/a"):
                ceo_flags.append(flag_text)
    elif meaningful:
        paragraph = " ".join(meaningful).strip()
        if paragraph and paragraph.lower() not in ("none", "n/a"):
            ceo_flags.append(paragraph)
```

Key behaviour:
- Six patterns tried in priority order; first match wins.
- Lookahead `(?=\n##|\Z)` stops at next H2/H3 heading or end of text (broader than the old `(?:\n###|\Z)`).
- `---` horizontal rules and empty lines filtered out of content before bulleted/paragraph classification.
- "None" and "N/A" (case-insensitive) excluded from both bulleted items and whole-paragraph flag text.

### MODIFIED: bellows.py (+19 lines in `run_plan`)

Added a branch between the final-step verdict check and the strand check:

```python
# Diagnostic auto-close: clean gates with no QA checkpoint → move to Done
# without needing the agent to do it. Executables still require an explicit
# QA step to reach Done (this branch only fires for diagnostic- plans).
if is_diagnostic and gate_result["passed"] and not gate_result["is_qa_step"]:
    verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close",
                          "diagnostic passed all gates, no CEO flag, auto-closing")
    done_dir = os.path.join(plan_dir, "Done")
    os.makedirs(done_dir, exist_ok=True)
    done_path = os.path.join(done_dir, plan_filename)
    source = inprogress_path if os.path.exists(inprogress_path) else plan_path
    if os.path.exists(source):
        shutil.move(source, done_path)
    notifier.push(app_key, user_key, "Bellows — Diagnostic Complete",
                  f"Plan: {plan_name}\nAll gates passed. Auto-closed to Done. Total cost: ${total_cost:.4f}")
    print(f"Bellows: ✅ DIAGNOSTIC AUTO-CLOSED — {plan_name}")
    return
```

The `source` computation handles both the case where the agent did claim the plan (moved to `in-progress-*`) and where the diagnostic was never claimed (still at its original path).

### MODIFIED: tests/test_runner_parser.py (+60 lines, 5 new tests)

1. `test_parse_h2_ceo_flag_paragraph` — `## CEO Flag\n\nSome flag content here\n\n---\n` → `["Some flag content here"]`
2. `test_parse_bold_ceo_flag` — `**CEO Flag:** Bold form flag text\n` → `["Bold form flag text"]`
3. `test_parse_h3_flags_for_ceo_bulleted_regression` — existing H3 + bulleted form still works
4. `test_parse_h3_flags_for_ceo_none_regression` — existing "- None" exclusion still works
5. `test_parse_h2_ceo_flag_none_paragraph` — "None" paragraph-form is excluded

Shared helper `_flag_raw()` builds the raw dict with `stop_reason: "end_turn"`, `is_error: False`.

### MODIFIED: tests/test_bellows.py (+52 lines, 1 new test)

`test_diagnostic_auto_close_moves_to_done` — creates `tmp/proj/knowledge/decisions/diagnostic-foo-2026-04-15.md`, patches `runner.run_step` to return a clean parsed dict, patches `gates.check` to return passed=True/is_qa_step=False, patches `notifier.push`, `verdict.log_to_ledger`, `_capture_git_diff`, and `record_run`. Calls `run_plan` and asserts the plan file moved to `Done/`, `log_to_ledger` was called with verdict="auto-close", and `notifier.push` was invoked.

## Test Results

`python3 -m pytest tests/ -v 2>&1 | tee /tmp/test_bellows_polish.txt`

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 61 items

tests/test_bellows.py ............. [ 21%]
tests/test_gates.py ............. [ 42%]
tests/test_notifier_server.py ... [ 47%]
tests/test_phase4_parser.py ... [ 52%]
tests/test_phase4_planner_retry.py .. [ 55%]
tests/test_planner.py ... [ 60%]
tests/test_runner.py ............ [ 77%]
tests/test_runner_parser.py ........ [ 91%]
tests/test_verdict.py ..... [100%]

======================== 61 passed, 1 warning in 0.72s =========================
```

55 pre-existing + 6 new = 61 passed. Zero regressions.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### Files Deposited
- `/Users/marklehn/Desktop/GitHub/bellows/parser.py`
- `/Users/marklehn/Desktop/GitHub/bellows/bellows.py`
- `/Users/marklehn/Desktop/GitHub/bellows/tests/test_runner_parser.py`
- `/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase7-polish-2026-04-16.md`

### Flags for CEO
- None
