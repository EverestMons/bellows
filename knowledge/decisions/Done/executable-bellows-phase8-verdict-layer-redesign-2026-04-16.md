# Bellows — Phase 8: Verdict Layer Redesign (Plan Headers + Action-Based Verdict Requests)
**Date:** 2026-04-16 | **Tier:** Medium | **Test Scope:** targeted | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## Context

Phase 7 and Phase 7 Polish attempted to build Gate 2 by parsing agent prose for `### Flags for CEO` headings. Today's verdict-layer test (2026-04-16 evening) failed because the agent wrote the flag heading in the deposit file but summarized it differently in its conversational output (`**Four CEO flags raised:**` + numbered list). Parser reads conversational output, didn't match, Gate 2 passed, plan auto-closed.

**Insight from CEO:** real gates measure, they don't hope. Gate 2 is the only gate that parses free-form agent prose, and it's the only gate that keeps failing. Every other gate reads structured JSON, runs a shell command, or string-matches our own files. Gate 2's architecture is wrong, not its patterns.

**The fix:** replace prose-based flag detection with two mechanical signals:
1. **Plan-header pause declarations.** Plan frontmatter declares when to pause (e.g., `pause_for_verdict: after_step_1`). gates.py reads this from the plan text, not from agent output.
2. **Action-based verdict requests.** Agents that want to escalate mid-plan create a file at `bellows/verdicts/pending/request-{slug}-step-{N}.md` using the Write tool. gates.py checks for the file's existence. No parsing of agent prose.

Remove the 5 polish regex patterns (today's test proves they don't catch real agent variance). Keep the minimal `### Flags for CEO` + bulleted regex as a last-resort safety net only — not the primary mechanism.

Also fix: `_consume_verdicts()`'s "continue" branch re-dispatches Step 1, which re-runs already-completed work when a plan is at its final step. Distinguish final-step continue (move to Done) from non-final-step continue (resume next step).

## Architectural changes

- **Plan header support.** YAML frontmatter at the top of plan files between `---` delimiters. Two new optional fields: `pause_for_verdict` and `auto_close`. Defaults are type-specific.
- **Defaults flip for diagnostics.** Diagnostics default to `pause_for_verdict: after_step_1` (not auto-close). Explicit `auto_close: true` opts into the old behavior for truly mechanical diagnostics.
- **Defaults for executables remain.** `pause_for_verdict: after_qa_step`, `auto_close: true` on non-QA steps.
- **New gate-like logic in gates.check().** Reads plan header, checks for verdict-request file, decides whether to pause. Replaces the primary role of Gate 2.
- **Safety-net Gate 2.** Simplified to one regex: `### Flags for CEO` + bulleted items. No paragraph form, no alternate headings. Catches the minority of cases where a DEV step wants to flag mid-plan without knowing about the request-file pattern.
- **Final-step continue semantics.** `continue` verdict on a plan at its final step moves it to Done. Only non-final-step continue re-dispatches.

## Files changed

- **MODIFIED:** `parser.py` — strip 5 polish patterns, keep only `### Flags for CEO` bulleted form
- **MODIFIED:** `gates.py` — add `_parse_plan_header()` helper, replace Gate 2 logic with plan-header check + verdict-request-file check (Gate 2 becomes mechanical, prose is fallback only)
- **MODIFIED:** `bellows.py` — auto-close branch respects `pause_for_verdict` from plan header; `_consume_verdicts()` final-step continue moves to Done instead of re-dispatch
- **MODIFIED:** `tests/test_runner_parser.py` — delete 4 polish tests (keep H3 bulleted + None regression tests)
- **MODIFIED:** `tests/test_gates.py` — add tests for header parsing, verdict-request-file detection, type-specific defaults
- **MODIFIED:** `tests/test_bellows.py` — add test for final-step continue → Done

## How to Run This Plan

Manual bootstrap (Bellows is the subject — stop Bellows first). Paste into Claude Code:

```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md and execute Step 1 ONLY. After Step 1, STOP and wait for my confirmation.
```


---
---

## STEP 1 — DEV (Bellows Developer)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md")`. Skip specialist file and glossary reads — full spec is in this plan. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Read `parser.py`, `gates.py`, `bellows.py`, `verdict.py`, `tests/test_runner_parser.py`, `tests/test_gates.py`, `tests/test_bellows.py` for current state. **MODIFY parser.py — strip polish patterns.** Replace the `flag_patterns` list (currently 6 entries) with a single regex: `r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)"`. Remove the paragraph-form fallback — only bulleted items are parsed. If the section contains `- None` or is empty, ceo_flags stays empty. If it contains `- something`, that something goes into ceo_flags. Keep the "none"/"n/a" exclusion for individual bulleted items. After this change, the flag block reads roughly: `ceo_flags = []; match = re.search(r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)", result_text, re.DOTALL); if match: for line in match.group(1).splitlines(): line = line.strip(); if line.startswith("- "): txt = line[2:].strip(); if txt and txt.lower() not in ("none", "n/a"): ceo_flags.append(txt)`. Update the docstring comment above the block to note this is a safety-net only, primary flag detection is in gates.py via plan headers and verdict-request files. **MODIFY gates.py — add plan header parsing.** Add a new module-level helper `_parse_plan_header(plan_text)` that extracts YAML frontmatter between `---\n` and `\n---\n` at the top of the plan text. Use a simple regex — do NOT require a YAML library: `match = re.search(r"\A---\n(.*?)\n---\n", plan_text, re.DOTALL)`. If no frontmatter, return `{}`. If present, parse each line as `key: value` (split on first `:`, strip both sides). Return a dict. Supported keys for this plan: `pause_for_verdict` (string: "always" | "after_step_1" | "after_qa_step" | "never"), `auto_close` (string "true"/"false", parse to bool). All other keys pass through as strings for future use. **MODIFY gates.py — add verdict-request-file detection.** Add a new helper `_verdict_requested(plan_path, step_number)` that checks whether `bellows/verdicts/pending/request-{plan-slug}-step-{N}.md` exists. The plan-slug is derived from the plan filename by stripping any prefix (`in-progress-`, `verdict-pending-`, `halted-`) and the `.md` suffix. Absolute path to verdicts dir: use `/Users/marklehn/Desktop/GitHub/bellows/verdicts/pending/`. If the file exists, return a tuple `(True, <file contents as string>)`. If not, return `(False, None)`. **MODIFY gates.py — rework check() signature and logic.** Update the check() function signature to accept an optional `plan_path` parameter (for deriving the plan slug for verdict-request checks): `def check(parsed, plan_text, step_number, project_path, files_changed=None, plan_path=None)`. Inside check(), after the existing gate calls but before the return, compute two new values: (a) `header = _parse_plan_header(plan_text)`, (b) `requested, request_body = _verdict_requested(plan_path, step_number) if plan_path else (False, None)`. Add these to the return dict under keys `"plan_header"` and `"verdict_requested"` (dict with `requested` bool and `body` string). These are informational — they don't add failures directly. **MODIFY bellows.py — use header and verdict-request signals.** In `run_plan()`, two places need changes: **(1) The mid-plan gate check** (inside the `while not is_final_step` loop): currently pauses if `not gate_result["passed"] or gate_result["is_qa_step"]`. Add two more pause triggers: (a) `gate_result.get("verdict_requested", {}).get("requested", False)` — pause if agent created a request file; (b) `header_says_pause(header, current_step, total_steps)` — pause if the plan header's `pause_for_verdict` field matches the current step. **Implement `header_says_pause(header, current_step, total_steps, is_qa_step)`** as a helper function near the top of bellows.py (or inside run_plan as a nested function). Logic: extract `pause_for_verdict` from header. If "always", return True. If "after_step_1", return True only when `current_step == 1`. If "after_qa_step", return True only when `is_qa_step`. If "never" or missing, return False. **(2) The final-step auto-close branch:** currently auto-closes diagnostics when `is_diagnostic and gate_result["passed"] and not gate_result["is_qa_step"]`. Change the condition to: `if gate_result["passed"] and not gate_result["is_qa_step"] and not header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"]) and not gate_result.get("verdict_requested", {}).get("requested", False)`. Also apply the `auto_close` header field: if `header.get("auto_close")` is explicitly `"false"`, skip auto-close regardless of other conditions (force verdict pause). This means the default behavior for a diagnostic WITHOUT an explicit header is: `pause_for_verdict` missing → no header pause → auto_close defaults to true → plan auto-closes. The defaults-flip is achieved by setting the default IN bellows.py: `effective_auto_close = header.get("auto_close", "true" if not is_diagnostic else "false").lower() == "true"`. Diagnostics default to NO auto-close (pause instead); executables default to YES auto-close. This is the critical behavior change. **Update the pass call to gates.check()** in both places where it's called to include `plan_path=plan_path`. **MODIFY bellows.py — fix final-step continue in _consume_verdicts().** In the `continue` branch of `_consume_verdicts()`, currently: rename `verdict-pending-` back to `in-progress-` and call `handle_new_plan()` which dispatches Step 1. This re-runs already-completed work when the plan was at its final step. Fix: before re-dispatching, check whether the step_number from the verdict filename equals or exceeds `total_steps`. Read the plan file's total steps (call `extract_total_steps(plan_text)` where plan_text is loaded from full_plan_path). For diagnostics, total_steps = 1. If `step_number >= total_steps`: this was the final step, verdict continue means "proceed to Done" — move the plan directly to Done/ instead of renaming to in-progress. Log to ledger as "continue-to-done". Send Pushover "Bellows — Plan Complete via Verdict" with the plan name. If `step_number < total_steps`: existing logic (rename to in-progress, handle_new_plan). **MODIFY bellows.py — update bootstrap prompts to reference new header support.** The bootstrap prompt strings don't need to change; header parsing is separate from dispatch. **MODIFY tests/test_runner_parser.py — delete 4 polish tests.** Remove: `test_parse_h2_ceo_flag_paragraph`, `test_parse_bold_ceo_flag`, `test_parse_h2_ceo_flag_none_paragraph`. Keep: `test_parse_h3_flags_for_ceo_bulleted_regression`, `test_parse_h3_flags_for_ceo_none_regression`. If the file has other unrelated tests, leave them alone. Add one new test: `test_parse_paragraph_form_no_longer_extracted` — input `### CEO Flag\n\nSome paragraph text\n` with H3 (mismatched heading) → `ceo_flags: []` (parser no longer recognizes H3 "CEO Flag" single or paragraph form). **ADD tests/test_gates.py — header parsing tests.** Four new tests: (1) `test_parse_plan_header_empty` — plan text without frontmatter → `{}`; (2) `test_parse_plan_header_basic` — plan text with `---\npause_for_verdict: after_step_1\nauto_close: false\n---\n# Title\n...` → `{"pause_for_verdict": "after_step_1", "auto_close": "false"}`; (3) `test_parse_plan_header_malformed` — plan text with no closing `---` → `{}` (don't crash); (4) `test_verdict_requested_file_exists` — create a tmp file at the expected verdict-request path, call `_verdict_requested("/tmp/test-plan.md", 1)`, assert (True, contents); tear down by removing the file. Use monkeypatch or explicit absolute paths for the test to match the production `/Users/marklehn/Desktop/GitHub/bellows/verdicts/pending/` path — the simplest approach is to patch the helper's hardcoded path via a module-level constant that tests can monkeypatch. Add a module constant `VERDICT_REQUEST_DIR = "/Users/marklehn/Desktop/GitHub/bellows/verdicts/pending"` at top of gates.py and use it in `_verdict_requested`; tests monkeypatch `gates.VERDICT_REQUEST_DIR` to a tmp path. **ADD tests/test_bellows.py — final-step continue test.** One test: `test_verdict_continue_at_final_step_moves_to_done` — set up a plan at total_steps=1 (diagnostic), verdict-pending on disk, verdict file in resolved/, call `_consume_verdicts()`. Assert: plan moved to Done/ (not renamed to in-progress), `log_to_ledger` called with verdict="continue-to-done" (or whatever string we chose), `handle_new_plan` NOT called. Mock notifier.push, verdict.log_to_ledger, verdict.check_verdict. **Run full test suite:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /tmp/test_bellows_phase8.txt`. Confirm all tests pass. Expected count: 61 - 3 deleted + 1 replacement + 5 new (4 gates + 1 bellows) = 64 passed. If any existing test regresses, fix it — the reason for the regression is probably that the test mocked the old `ceo_flags` behavior (polish patterns) and now needs updating to the stripped parser. **Write a development log** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase8-verdict-layer-redesign-2026-04-16.md` with: summary of architecture change (prose parsing → plan headers + action files), parser.py before/after, gates.py additions (_parse_plan_header, _verdict_requested), bellows.py changes (auto_close default flip, final-step continue fix), test results, Output Receipt with Status=Complete. **Final operations follow Rule 23.** Step A — Feedback append to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. Step B — Commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add parser.py gates.py bellows.py tests/test_runner_parser.py tests/test_gates.py tests/test_bellows.py knowledge/development/bellows-phase8-verdict-layer-redesign-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "feat: phase 8 — verdict layer redesign (plan headers replace prose-based flag detection)"`. **End of Step 1. STOP and wait for CEO confirmation.**


---
---

## STEP 2 — QA (Bellows QA)

---

> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase8-verdict-layer-redesign-2026-04-16.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue.** Skip specialist file and glossary reads. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Evidence directory: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16/` (mkdir -p first via Python). **Deliverable Verification (Rule 17).**

```python
import os
os.makedirs("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16", exist_ok=True)
checks = []
# Parser simplified
with open("/Users/marklehn/Desktop/GitHub/bellows/parser.py") as f:
    pc = f.read()
# Polish patterns should be GONE
checks.append(("parser.py no longer has H2 CEO Flag pattern", "## CEO Flag" not in pc and "CEO Flags?" not in pc, "polish patterns stripped"))
checks.append(("parser.py no longer has bold CEO Flag pattern", "**CEO Flag:**" not in pc, ""))
checks.append(("parser.py still has ### Flags for CEO", "### Flags for CEO" in pc, "safety-net kept"))
# Gates.py new helpers
with open("/Users/marklehn/Desktop/GitHub/bellows/gates.py") as f:
    gc = f.read()
checks.append(("gates.py has _parse_plan_header", "_parse_plan_header" in gc, ""))
checks.append(("gates.py has _verdict_requested", "_verdict_requested" in gc, ""))
checks.append(("gates.py has VERDICT_REQUEST_DIR constant", "VERDICT_REQUEST_DIR" in gc, ""))
checks.append(("gates.check() accepts plan_path parameter", "plan_path=None" in gc or "plan_path:" in gc, ""))
# Bellows.py header integration
with open("/Users/marklehn/Desktop/GitHub/bellows/bellows.py") as f:
    bc = f.read()
checks.append(("bellows.py has header_says_pause helper", "header_says_pause" in bc or "pause_for_verdict" in bc, ""))
checks.append(("bellows.py auto-close respects auto_close header", "auto_close" in bc, ""))
checks.append(("bellows.py final-step continue moves to Done", "continue-to-done" in bc or ("step_number >= total_steps" in bc or "final_step" in bc.lower()), "final-step continue fix"))
# Tests
with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_gates.py") as f:
    tgc = f.read()
checks.append(("test_gates.py has header parsing tests", "_parse_plan_header" in tgc or "parse_plan_header" in tgc, ""))
checks.append(("test_gates.py has verdict-request-file test", "verdict_requested" in tgc or "VERDICT_REQUEST_DIR" in tgc, ""))
with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py") as f:
    tbc = f.read()
checks.append(("test_bellows.py has final-step continue test", "final_step" in tbc.lower() or "final-step" in tbc.lower() or "continue_at_final" in tbc.lower(), ""))
# Polish tests removed
with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_runner_parser.py") as f:
    trpc = f.read()
checks.append(("test_runner_parser.py no longer tests polish H2 paragraph form", "test_parse_h2_ceo_flag_paragraph" not in trpc, "polish test deleted"))
checks.append(("test_runner_parser.py no longer tests bold form", "test_parse_bold_ceo_flag" not in trpc, "polish test deleted"))
with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16/grep_deliverables.txt", "w") as f:
    for name, ok, evidence in checks:
        status = "PASS" if ok else "FAIL"
        f.write(f"{status} | {name} | {evidence}\n")
print("Deliverable verification:")
for name, ok, evidence in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {name}")
```

> Build verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ blocks. **Test regression.** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16/pytest_full.txt`. Confirm all tests pass. Expected count: 64 (61 previous - 3 deleted polish tests + 1 replacement test + 5 new tests). Document the exact count; if the count differs from 64 explain why (e.g., agent added extra tests). **Behavioral verification.** Three end-to-end scenarios, deposit each to a separate evidence file:

```python
# Scenario A: plan with explicit pause_for_verdict: after_step_1 header
import sys
sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")
import gates

plan_with_header = """---
pause_for_verdict: after_step_1
auto_close: false
---

# Test Plan
## STEP 1
test content"""

header = gates._parse_plan_header(plan_with_header)
assert header.get("pause_for_verdict") == "after_step_1", f"Expected after_step_1, got {header}"
assert header.get("auto_close") == "false", f"Expected 'false' string, got {header}"

plan_no_header = "# No Frontmatter Plan\n## STEP 1\ntest"
header2 = gates._parse_plan_header(plan_no_header)
assert header2 == {}, f"Expected empty dict, got {header2}"

with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16/header_parsing.txt", "w") as f:
    f.write(f"Scenario A (with header): {header}\n")
    f.write(f"Scenario B (no header): {header2}\n")
    f.write("PASS: header parsing works correctly\n")
print("Header parsing: PASS")
```

```python
# Scenario B: verdict-request file detection
import os, sys, tempfile
sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")
import gates

# Use a tmp dir to avoid polluting real verdicts folder
tmp = tempfile.mkdtemp()
gates.VERDICT_REQUEST_DIR = tmp
request_path = os.path.join(tmp, "request-test-plan-slug-step-1.md")
with open(request_path, "w") as f:
    f.write("Requesting verdict for test plan\nReason: this is a test")

# Simulate a plan path whose slug is "test-plan-slug"
requested, body = gates._verdict_requested("/any/path/test-plan-slug.md", 1)
assert requested is True, f"Expected True, got {requested}"
assert "Requesting verdict" in body, f"Expected body to contain 'Requesting verdict', got {body}"

# Also verify non-existent returns False
requested2, body2 = gates._verdict_requested("/any/path/nonexistent.md", 1)
assert requested2 is False, f"Expected False, got {requested2}"

with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16/verdict_request_detection.txt", "w") as f:
    f.write(f"Scenario with existing request file: requested={requested}, body starts with '{body[:50]}...'\n")
    f.write(f"Scenario with no request file: requested={requested2}\n")
    f.write("PASS: verdict-request file detection works\n")

os.remove(request_path)
os.rmdir(tmp)
print("Verdict-request detection: PASS")
```

```python
# Scenario C: parser simplification — prose-form flag NO LONGER extracts flags
import sys
sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")
from parser import parse

# Case C1: H2 CEO Flag paragraph (today's failing format) — should extract NOTHING now
raw_c1 = {"result": "Done.\n\n## CEO Flag\n\nSome flag text\n\n---\n", "stop_reason": "end_turn", "is_error": False, "session_id": "test", "total_cost_usd": 0.0, "permission_denials": []}
p_c1 = parse(raw_c1)
assert p_c1["ceo_flags"] == [], f"Expected empty (polish removed), got {p_c1['ceo_flags']}"

# Case C2: ### Flags for CEO with bullets — should still extract (safety net)
raw_c2 = {"result": "Done.\n\n### Flags for CEO\n- Real flag one\n- Real flag two\n", "stop_reason": "end_turn", "is_error": False, "session_id": "test", "total_cost_usd": 0.0, "permission_denials": []}
p_c2 = parse(raw_c2)
assert p_c2["ceo_flags"] == ["Real flag one", "Real flag two"], f"Expected bullets, got {p_c2['ceo_flags']}"

# Case C3: ### Flags for CEO with - None — should extract empty
raw_c3 = {"result": "Done.\n\n### Flags for CEO\n- None\n", "stop_reason": "end_turn", "is_error": False, "session_id": "test", "total_cost_usd": 0.0, "permission_denials": []}
p_c3 = parse(raw_c3)
assert p_c3["ceo_flags"] == [], f"Expected empty (None excluded), got {p_c3['ceo_flags']}"

with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-verdict-layer-redesign-2026-04-16/parser_simplification.txt", "w") as f:
    f.write(f"C1 (H2 paragraph, polish REMOVED): {p_c1['ceo_flags']}\n")
    f.write(f"C2 (H3 bulleted, safety net KEPT): {p_c2['ceo_flags']}\n")
    f.write(f"C3 (H3 + None, exclusion WORKS): {p_c3['ceo_flags']}\n")
    f.write("PASS: parser simplified correctly — polish gone, safety net intact\n")
print("Parser simplification: PASS")
```

> Any assertion failure in these three scripts blocks the plan from moving to Done. **Write the QA report** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase8-verdict-layer-redesign-2026-04-16.md` with verification table, test results, 3 behavioral scenario summaries, and Output Receipt. **Run the Rule 20 self-check:**

```python
import os, sys
plan_slug = "executable-bellows-phase8-verdict-layer-redesign-2026-04-16"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase8-verdict-layer-redesign-2026-04-16.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "header_parsing.txt", "verdict_request_detection.txt", "parser_simplification.txt"]
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

> Include literal stdout of self-check at end of QA report. If FAILS, stop. If PASSES, continue. **Update PROJECT_STATUS.md.** Add milestone: "Phase 8 (2026-04-16) — Verdict layer redesign. Gate 2 transformed from prose-based parser (unreliable, agent-output dependent) to mechanical checks: plan-header `pause_for_verdict` field + agent-authored verdict-request files. Polish regex patterns removed from parser.py (safety-net only). Diagnostic default flipped: pause for verdict unless `auto_close: true` in header. Final-step 'continue' verdict moves to Done instead of re-dispatching Step 1. Parser.py, gates.py, bellows.py modified. 64 tests pass (61 → -3 deleted polish + 1 replacement + 5 new)." **Final operations follow Rule 23. Step A — Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git commit -m "qa: phase 8 verdict layer redesign verification + status update"`. **Step C — Move-to-Done as the absolute last operation:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md")`. **Move-to-Done is the LAST operation per Rule 23.**
