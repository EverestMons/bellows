# Bellows — Phase 7 Polish: Flag Format Tolerance + Diagnostic Auto-Close
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## Context

The first real test of Phase 7's verdict layer (2026-04-16) surfaced two problems:

**Problem 1 — Parser flag format too strict.** Agent wrote a CEO flag as `## CEO Flag` (H2) and `**CEO Flag:** RAISED` in the Output Receipt. Parser only matches `### Flags for CEO` (H3) + bulleted list. Result: parsed.ceo_flags was empty, Gate 2 passed, no verdict request was posted. The verdict layer's most important gate is silently bypassed by reasonable agent format variations.

**Problem 2 — Diagnostics with clean gates strand.** Both test diagnostics passed all gates (is_qa_step=False, failures=0). bellows.py has no auto-close path for diagnostic plans that pass cleanly — it falls through to the strand check, which detects the plan as stranded since the agent didn't move it to Done. Diagnostics don't have a QA step by design, so they also don't trigger is_qa_step. Result: clean diagnostics always strand.

Both fixes are mechanical and small. Parser gets broader regex + paragraph content support. bellows.py gets a conditional auto-close for diagnostics. No architectural changes.


## Files changed

- **MODIFIED:** `parser.py` — broader ceo_flags regex + paragraph content support (~15 lines)
- **MODIFIED:** `bellows.py` — diagnostic auto-close branch in run_plan() (~10 lines)
- **MODIFIED:** `tests/test_runner_parser.py` (or new `tests/test_parser.py` if parser has no existing test file) — 5 new tests for flag formats
- **MODIFIED:** `tests/test_bellows.py` — 1 new test for diagnostic auto-close

## How to Run This Plan

Manual bootstrap (Bellows is the subject of the fix, can't run through itself). Paste into Claude Code:

```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase7-polish-2026-04-16.md and execute Step 1 ONLY. After Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV (Bellows Developer)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase7-polish-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase7-polish-2026-04-16.md")`. Skip specialist file and glossary reads — infrastructure polish with full spec here. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Read `parser.py`, `bellows.py`, `gates.py` for current state. Read `tests/test_runner_parser.py` and `tests/test_bellows.py` for test conventions. **MODIFY parser.py.** The current `ceo_flags` extraction uses: `re.search(r"### Flags for CEO\s*\n(.*?)(?:\n###|\Z)", result_text, re.DOTALL)` and then only collects lines starting with `- `. Replace the flag extraction block with logic that: **(a)** tries multiple heading patterns in order: `### Flags for CEO`, `## Flags for CEO`, `### CEO Flag`, `### CEO Flags`, `## CEO Flag`, `## CEO Flags`, `**Flags for CEO:**`, `**CEO Flag:**`. The regex should match any of these headings. **(b)** captures content from the matched heading until the next `##` or `###` heading or end of string. **(c)** within the captured content, extracts flag text as follows: if any line starts with `- `, collect all such lines as bulleted flags (current behavior). If NO bulleted lines exist but the section has non-empty text, treat the entire section's text (stripped, with "None" variants excluded) as a single flag entry. **(d)** excludes empty content and content that is just the word "None" (case-insensitive) or `-   None` or similar. **Implementation hint:** use a list of heading regex patterns, iterate through them, use the first match. For paragraph-form content, strip the matched text and check `len(stripped) > 0 and stripped.lower() not in ("none", "- none", "n/a")` before appending as a single flag. Example target behavior: text containing `## CEO Flag\n\nPattern-to-chunk linking does not distinguish...\n\n---\n` should extract `["Pattern-to-chunk linking does not distinguish..."]` (the paragraph text, stripped). Text containing `### Flags for CEO\n- Flag one\n- Flag two\n` should still extract `["Flag one", "Flag two"]`. Text containing `### Flags for CEO\n- None\n` should extract `[]`. **MODIFY bellows.py — diagnostic auto-close.** In `run_plan()`, after the "Final step completed — check gates one last time" block, add a new branch BEFORE the stranded check: `if is_diagnostic and gate_result["passed"] and not gate_result["is_qa_step"]:` — in this branch: (i) log autoclose entry to verdict ledger via `verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close", "diagnostic passed all gates, no CEO flag, auto-closing")`, (ii) move the plan file from `inprogress_path` to `Done/` using shutil.move, (iii) send Pushover via `notifier.push(app_key, user_key, "Bellows — Diagnostic Complete", f"Plan: {plan_name}\nAll gates passed. Auto-closed to Done. Total cost: ${total_cost:.4f}")`, (iv) print `Bellows: ✅ DIAGNOSTIC AUTO-CLOSED — {plan_name}`, (v) return from run_plan(). This branch runs BEFORE the strand check so clean diagnostics never reach the strand path. Leave the executable behavior unchanged — executables still need explicit QA steps to move to Done. **ADD tests to tests/test_runner_parser.py** (parser's existing test file): (1) test that `## CEO Flag\n\nSome flag content here\n\n---\n` extracts `["Some flag content here"]` via parser.parse(); (2) test that `**CEO Flag:**\nBold form flag text\n` extracts `["Bold form flag text"]`; (3) test that `### Flags for CEO\n- Bulleted flag one\n- Bulleted flag two\n` still extracts `["Bulleted flag one", "Bulleted flag two"]` (regression); (4) test that `### Flags for CEO\n- None\n` extracts `[]` (regression); (5) test that `## CEO Flag\nNone\n` also extracts `[]` (None exclusion works for paragraph form). Build the raw dict for parser.parse() with `stop_reason: "end_turn"`, `is_error: False`, and the test text as `result`. **ADD one test to tests/test_bellows.py** for diagnostic auto-close: mock runner.run_step to return a clean parsed dict (status Complete, no flags, no errors, no denials), mock gates.check to return passed=True is_qa_step=False, create a fake diagnostic plan file in a tmp directory, call run_plan, assert the plan was moved to a Done/ subdirectory. Skip Pushover in the test by mocking notifier.push. This is a narrow integration test — if mocking bellows.py's internals is too invasive, a unit-style test that just verifies the auto-close branch logic is acceptable. **Run full test suite:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /tmp/test_bellows_polish.txt`. All tests (55 existing + 6 new = 61) must pass. Zero regressions. **Write a development log** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase7-polish-2026-04-16.md` with: summary of parser changes (before/after regex), bellows.py auto-close branch (code snippet), test results, Output Receipt with Status=Complete. **Final operations follow Rule 23.** Step A — Feedback append to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. Step B — Commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add parser.py bellows.py tests/test_runner_parser.py tests/test_bellows.py knowledge/development/bellows-phase7-polish-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "fix: parser ceo_flags tolerance + diagnostic auto-close in bellows"`. **End of Step 1. STOP and wait for CEO confirmation.**


---
---

## STEP 2 — QA (Bellows QA)

---

> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase7-polish-2026-04-16.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue.** Skip specialist file and glossary reads. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Evidence directory: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/` (mkdir -p first). **Deliverable Verification (Rule 17).** Run:

```python
import os
os.makedirs("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16", exist_ok=True)
checks = []
# Parser changes
with open("/Users/marklehn/Desktop/GitHub/bellows/parser.py") as f:
    pc = f.read()
checks.append(("parser.py handles ## CEO Flag heading", "## CEO Flag" in pc or "CEO Flag" in pc, ""))
checks.append(("parser.py handles paragraph flag form", "none" in pc.lower() and ("strip" in pc or "n/a" in pc.lower()), "checks for None exclusion + stripping"))
# Bellows auto-close
with open("/Users/marklehn/Desktop/GitHub/bellows/bellows.py") as f:
    bc = f.read()
checks.append(("bellows.py has diagnostic auto-close branch", "is_diagnostic" in bc and "auto-close" in bc.lower(), ""))
checks.append(("bellows.py auto-close logs ledger entry", "log_to_ledger" in bc, ""))
checks.append(("bellows.py auto-close moves plan to Done", 'Done' in bc and 'shutil.move' in bc, ""))
# Tests
with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_runner_parser.py") as f:
    tc = f.read()
# At least 5 new parser tests (check for multiple test function signatures or references to new flag formats)
new_flag_tests = sum(1 for marker in ["## CEO Flag", "**CEO Flag", "paragraph", "None"] if marker.lower() in tc.lower())
checks.append(("tests/test_runner_parser.py has new flag format tests", new_flag_tests >= 3, f"found {new_flag_tests} flag format markers"))
with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py") as f:
    tbc = f.read()
checks.append(("tests/test_bellows.py has auto-close test", "auto" in tbc.lower() and "diagnostic" in tbc.lower(), ""))
with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/grep_deliverables.txt", "w") as f:
    for name, ok, evidence in checks:
        status = "PASS" if ok else "FAIL"
        f.write(f"{status} | {name} | {evidence}\n")
print("Deliverable verification:")
for name, ok, evidence in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {name}")
```

> Build verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ blocks. **Test regression.** Run full suite: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/pytest_full.txt`. Confirm 61 passed (55 existing + 6 new), 0 failed. **Behavioral verification.** Run this Python script to verify parser handles all 5 flag formats end-to-end, deposit output to `parser_behavioral.txt`:

```python
import sys
sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")
from parser import parse

test_cases = [
    ("H2_CEO_Flag_paragraph", "Done.\n\n## CEO Flag\n\nPattern-to-chunk linking does not distinguish failure chunks.\n\n---\n", ["Pattern-to-chunk linking does not distinguish failure chunks."]),
    ("Bold_CEO_Flag", "Done.\n\n**CEO Flag:** RAISED — architectural decision required\n\n---\n", ["RAISED — architectural decision required"]),
    ("H3_Flags_for_CEO_bulleted", "Done.\n\n### Flags for CEO\n- Flag one\n- Flag two\n\n---\n", ["Flag one", "Flag two"]),
    ("H3_Flags_for_CEO_None", "Done.\n\n### Flags for CEO\n- None\n\n---\n", []),
    ("H2_CEO_Flag_None_paragraph", "Done.\n\n## CEO Flag\n\nNone\n\n---\n", []),
]

lines = []
all_pass = True
for name, text, expected in test_cases:
    raw = {"result": text, "stop_reason": "end_turn", "is_error": False, "session_id": "test", "total_cost_usd": 0.0, "permission_denials": []}
    parsed = parse(raw)
    actual = parsed["ceo_flags"]
    status = "PASS" if actual == expected else "FAIL"
    if status == "FAIL": all_pass = False
    line = f"{status} | {name} | expected={expected} | actual={actual}"
    lines.append(line)
    print(line)

with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/parser_behavioral.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
    f.write(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}\n")

if not all_pass:
    sys.exit(1)
```

> The behavioral test validates real end-to-end parsing, not just that test code exists. If ANY case fails, the fix is incomplete. **Write the QA report** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase7-polish-2026-04-16.md` with the verification table, test results, behavioral test results, and Output Receipt. **Run the Rule 20 self-check:**

```python
import os, sys
plan_slug = "executable-bellows-phase7-polish-2026-04-16"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase7-polish-2026-04-16.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "parser_behavioral.txt"]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
def is_positive_row(line):
    if "|" not in line: return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell: return True
            else:
                if cell.lower() == token.lower(): return True
    return False
failures = []
if not os.path.isdir(evidence_dir):
    failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
else:
    for fname in required_evidence_files:
        fpath = os.path.join(evidence_dir, fname)
        if not os.path.isfile(fpath):
            failures.append(f"CRITICAL: evidence file missing: {fpath}")
        elif os.path.getsize(fpath) == 0:
            failures.append(f"CRITICAL: evidence file empty: {fpath}")
if os.path.isfile(qa_report_path):
    with open(qa_report_path, "r") as f:
        report = f.read()
    for line in report.splitlines():
        if is_positive_row(line):
            lower = line.lower()
            for kw in hedging_keywords:
                if kw in lower:
                    failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
                    break
else:
    failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
print("=" * 60)
print("Rule 20 — QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Files verified: {len(required_evidence_files)}")
```

> Include literal stdout of self-check at end of QA report. If FAILS, stop. If PASSES, continue. **Update PROJECT_STATUS.md.** Add milestone: "Phase 7 Polish (2026-04-16) — Parser now accepts 4 additional CEO flag formats (H2 CEO Flag, bold CEO Flag, paragraph content under flag headings) in addition to the original H3 + bulleted format. Bellows auto-closes clean diagnostics that pass all gates (is_diagnostic + passed + not is_qa_step → move to Done + ledger entry + Pushover). First real verdict-layer test (2026-04-16) surfaced both issues — polish plan fixes them before the next test." **Final operations follow Rule 23.** Step A — Feedback append to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git commit -m "qa: phase 7 polish verification + status update"`. **Step C — Move-to-Done as the absolute last operation:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase7-polish-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-phase7-polish-2026-04-16.md")`. **Move-to-Done is the LAST operation per Rule 23.**
