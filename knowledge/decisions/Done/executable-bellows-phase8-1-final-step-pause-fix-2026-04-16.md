# Bellows — Phase 8.1: Final-Step Pause Logic Fix
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## Context

Phase 8 shipped the verdict layer redesign but left a gap in the final-step block of `run_plan()`. The while-loop's mid-plan gate check (line 207–211) correctly checks four pause conditions: `not gate_result["passed"]`, `gate_result["is_qa_step"]`, `verdict_requested`, and `header_says_pause()`. But the final-step block (line 253) only checks the first two.

For single-step diagnostics, the while-loop is never entered (`is_final_step(1, 1)` is True immediately). All pause logic must live in the final-step block. With Phase 8's defaults-flip making diagnostics default to `auto_close=false`, a clean single-step diagnostic lands in this state:

- `gates.passed = True` → first condition False
- `gates.is_qa_step = False` → second condition False
- Plan has no header → `header_says_pause()` is False
- No verdict-request file → `verdict_requested.requested` is False
- But `effective_auto_close = False` (diagnostic default with no header opt-in)

The final-step block skips (no verdict posted). The auto-close block skips (`effective_auto_close` is False). The plan falls through to the strand check.

**Observed last night (2026-04-16):** the `_parse_diff_stat` audit diagnostic stranded despite clean gates. Demonstrated the gap.

## The fix

Add two conditions to the final-step gate check that match the while-loop's check, plus `not effective_auto_close`:

```python
# BEFORE (line 253)
if not gate_result["passed"] or gate_result["is_qa_step"]:

# AFTER
if (not gate_result["passed"]
        or gate_result["is_qa_step"]
        or gate_result.get("verdict_requested", {}).get("requested", False)
        or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
        or not effective_auto_close):
```

The `or not effective_auto_close` is the critical addition. It catches the "clean gates + diagnostic default pause" case that stranded last night.

**Case analysis:**

| Case | gates.passed | is_qa | verdict_req | header_pause | effective_auto_close | Final-step check | Correct? |
|---|---|---|---|---|---|---|---|
| Clean exec, `auto_close: true` | T | F | F | F | T | All conditions False → fall through → auto-close fires | ✅ |
| Clean diagnostic, no header | T | F | F | F | F | `not effective_auto_close` → True → post verdict | ✅ (new) |
| Diagnostic, `pause_for_verdict: after_step_1` | T | F | F | T | F | header + effective_auto_close both True → post verdict | ✅ (new) |
| Exec with flag fires | F | F | F | F | T | `not passed` → True → post verdict | ✅ |
| Diagnostic with `auto_close: true` | T | F | F | F | T | All False → fall through → auto-close | ✅ (new — today's test path) |

## Files changed

- **MODIFIED:** `bellows.py` — one logical change to the final-step block in `run_plan()` (~5 lines added)
- **MODIFIED:** `tests/test_bellows.py` — add 2 new tests:
  - `test_clean_diagnostic_no_header_posts_verdict` — the case that stranded last night; verifies verdict request posted, plan renamed to `verdict-pending-*`
  - `test_clean_diagnostic_auto_close_true_moves_to_done` — regression test confirming the existing `test_diagnostic_auto_close_moves_to_done` path still works

## How to Run This Plan

Manual bootstrap (Bellows is the subject — stop Bellows first). Paste into Claude Code:

```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md and execute Step 1 ONLY. After Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV (Bellows Developer)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md")`. Skip specialist file and glossary reads — full spec in this plan. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Read `bellows.py` (focus on `run_plan()` lines 197–265 — the gate check loop and final-step block) and `tests/test_bellows.py` (focus on `test_diagnostic_auto_close_moves_to_done` as the pattern to follow). **MODIFY bellows.py — extend final-step gate check.** Find the final-step gate check block. It currently reads `if not gate_result["passed"] or gate_result["is_qa_step"]:`. Replace with the five-condition form: `if (not gate_result["passed"] or gate_result["is_qa_step"] or gate_result.get("verdict_requested", {}).get("requested", False) or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"]) or not effective_auto_close):`. Preserve existing indentation. Do NOT touch any other part of `run_plan()`. **ADD tests/test_bellows.py — 2 new tests.** Test A: `test_clean_diagnostic_no_header_posts_verdict`. Same setup pattern as the existing `test_diagnostic_auto_close_moves_to_done` but the `clean_gates` dict must set `"plan_header": {}` (empty, no `auto_close` key — this triggers the diagnostic default `effective_auto_close = False`). Patch `bellows.verdict.post_verdict_request` and `bellows.notifier.notify_verdict_request` (in addition to the existing `bellows.notifier.push` patch). Call `bellows.run_plan(...)`. Assert: (a) `post_verdict_request` was called once, (b) `notify_verdict_request` was called, (c) the plan file was renamed from its original name to `verdict-pending-{original_name}` (check via `os.path.isfile(os.path.join(decisions_dir, "verdict-pending-" + plan_filename))`), (d) the plan is NOT in Done/, (e) `verdict.log_to_ledger` was NOT called with "auto-close" (because auto-close branch didn't fire). Test B: `test_clean_diagnostic_auto_close_true_moves_to_done`. Same setup pattern but `clean_gates["plan_header"] = {"auto_close": "true"}`. Assert: plan moved to Done/, ledger called with "auto-close", notifier.push called. This is a regression test — it validates the existing Phase 7-polish behavior still works after the Phase 8.1 fix. **Run full test suite:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /tmp/test_bellows_phase81.txt`. Expected count: 66 (64 previous + 2 new). All must pass. If `test_diagnostic_auto_close_moves_to_done` regresses, the fix is wrong — stop and report. **Write a development log** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase8-1-final-step-pause-fix-2026-04-16.md` with: the before/after of the final-step check, a table of the 5 cases the fix covers (copy from this plan's Case Analysis table), test results, Output Receipt with Status=Complete. **Final operations follow Rule 23.** Step A — Feedback append to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. Step B — Commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add bellows.py tests/test_bellows.py knowledge/development/bellows-phase8-1-final-step-pause-fix-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "fix: phase 8.1 — final-step gate check respects verdict-request, header-pause, and effective_auto_close"`. **End of Step 1. STOP and wait for CEO confirmation.**

---
---

## STEP 2 — QA (Bellows QA)

---

> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase8-1-final-step-pause-fix-2026-04-16.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue.** Skip specialist file and glossary reads. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Evidence directory: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16/` (mkdir -p first via Python). **Deliverable Verification (Rule 17):**

```python
import os
os.makedirs("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16", exist_ok=True)
checks = []
with open("/Users/marklehn/Desktop/GitHub/bellows/bellows.py") as f:
    bc = f.read()
# Final-step block now has 5 conditions (count "or" occurrences around the check — sloppy but functional)
checks.append(("bellows.py final-step block has verdict_requested check", "verdict_requested" in bc and bc.count("get(\"verdict_requested\"") >= 2, "should appear in both while-loop and final-step"))
checks.append(("bellows.py final-step block has header_says_pause check", bc.count("header_says_pause(header") >= 3, "should appear in while-loop, final-step, and auto-close"))
checks.append(("bellows.py final-step block has effective_auto_close check", bc.count("effective_auto_close") >= 3, "definition + auto-close branch + NEW final-step"))
with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py") as f:
    tbc = f.read()
checks.append(("test_clean_diagnostic_no_header_posts_verdict present", "test_clean_diagnostic_no_header_posts_verdict" in tbc, ""))
checks.append(("test_clean_diagnostic_auto_close_true_moves_to_done present", "test_clean_diagnostic_auto_close_true_moves_to_done" in tbc, ""))
with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16/grep_deliverables.txt", "w") as f:
    for name, ok, evidence in checks:
        status = "PASS" if ok else "FAIL"
        f.write(f"{status} | {name} | {evidence}\n")
for name, ok, evidence in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {name}")
```

> Build a verification table with the above checks. Any ❌ blocks the plan. **Test regression.** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16/pytest_full.txt`. Expected: 66 passed (64 previous + 2 new), 0 failed. If any test fails, the fix introduces a regression — stop. **Behavioral verification.** Run this Python script to verify the fix handles all 5 cases correctly via module-level inspection (not full run_plan integration — that's covered by the unit tests). Write output to `behavioral_check.txt`:

```python
# Inspect the final-step conditional to confirm all 5 clauses are present
import sys
sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")
with open("/Users/marklehn/Desktop/GitHub/bellows/bellows.py") as f:
    src = f.read()

# Find the final-step block marker
marker = "# Final step completed"
idx = src.find(marker)
assert idx != -1, "could not find final-step block marker"
# Extract ~20 lines starting at the marker
block = src[idx:idx+1200]

required_clauses = [
    'not gate_result["passed"]',
    'gate_result["is_qa_step"]',
    'verdict_requested',
    'header_says_pause(header',
    'not effective_auto_close',
]

results = []
for clause in required_clauses:
    present = clause in block
    results.append((clause, present))
    status = "PASS" if present else "FAIL"
    print(f"{status}: '{clause}' in final-step block")

all_pass = all(p for _, p in results)
with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16/behavioral_check.txt", "w") as f:
    for clause, present in results:
        f.write(f"{'PASS' if present else 'FAIL'}: '{clause}'\n")
    f.write(f"\nOverall: {'ALL CLAUSES PRESENT' if all_pass else 'MISSING CLAUSES'}\n")

if not all_pass:
    sys.exit(1)
```

> If any clause is missing, fix is incomplete. **Write the QA report** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase8-1-final-step-pause-fix-2026-04-16.md` with the verification table, test results, behavioral check results, and Output Receipt. **Run the Rule 20 self-check:**

```python
import os, sys
plan_slug = "executable-bellows-phase8-1-final-step-pause-fix-2026-04-16"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase8-1-final-step-pause-fix-2026-04-16.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "behavioral_check.txt"]
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

> Include literal stdout of self-check at end of QA report. If FAILS, stop. If PASSES, continue. **Update PROJECT_STATUS.md.** Add milestone: "Phase 8.1 (2026-04-16) — Final-step gate check extended with 3 additional pause conditions (`verdict_requested`, `header_says_pause`, `not effective_auto_close`) to match while-loop logic. Fixes stranding of clean single-step diagnostics with `auto_close=false` (the new Phase 8 default). Discovered when `_parse_diff_stat` audit stranded 2026-04-16. 66/66 tests pass (64 + 2 new)." **Final operations follow Rule 23. Step A — Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git commit -m "qa: phase 8.1 final-step pause fix verification + status update"`. **Step C — Move-to-Done as the LAST operation:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md")`. **Move-to-Done is the absolute LAST operation per Rule 23.**
