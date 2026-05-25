# QA Report — MCP READ_CLASS_TOOLS Extension

**Date:** 2026-05-25 | **Agent:** Bellows QA | **Plan:** executable-mcp-read-class-tools-extension-2026-05-25 | **Step:** 2

---

## Deliverable Verification Table

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | `READ_CLASS_TOOLS` in `gates.py` contains all 9 expected entries and does NOT contain `mcp__vexp__save_observation` | ✅ | `gates.py:35-43` — set literal contains `"Grep", "Glob", "Read", "mcp__vexp__run_pipeline", "mcp__vexp__get_context_capsule", "mcp__vexp__get_session_context", "mcp__vexp__get_skeleton", "mcp__vexp__index_status", "mcp__vexp__search_memory"`. grep for `save_observation` in gates.py returns zero matches. |
| 2 | `_gate_no_permission_denials` filter mechanism unchanged — still uses `tool_name in READ_CLASS_TOOLS` exact set membership | ✅ | `gates.py:235` — `if tool_name in READ_CLASS_TOOLS:` unchanged. No pattern matching or regex added. |
| 3 | 5 positive test functions present for newly-added tools (count went from 1 to 6 total vexp tests) | ✅ | `grep 'def test_permission_denials_vexp_' tests/test_gates.py` returns 7 matches (lines 874, 885, 896, 907, 918, 929, 940) — 6 exempt tests + 1 negative test. |
| 4 | Negative test `test_permission_denials_vexp_save_observation_is_not_exempted` present and asserts gate DOES fire | ✅ | `test_gates.py:940-950` — asserts `result["passed"] is False` and `failures` contains `gate == "no_permission_denials"` with `"1 blocking denial"` in evidence. |
| 5 | Dev log has all 6 sections (a-f) + Output Receipt with Status: Complete | ✅ | `knowledge/development/mcp-read-class-tools-extension-2026-05-25.md` — sections (a) READ_CLASS_TOOLS Diff, (b) New Test Functions, (c) Full-Suite Test Counts, (d) save_observation Denial Test Confirmation, (e) Deviations from SA Section 3, (f) Output Receipt with `Status: Complete`. |

---

## Full Pytest Suite

```
collected 412 items
407 passed, 5 failed, 1 warning
```

**5 pre-existing failures (all carry-overs, zero new regressions):**
- 3 x `test_decisions.py::TestLoadPhrases` — worktree artifact (phrase file path resolves to worktree root)
- 1 x `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — worktree artifact
- 1 x `test_runner_parser.py::test_run_step_timeout` — pre-existing runner timeout test issue

**Targeted vexp test run (7 selected, 7 passed):**
- `test_permission_denials_vexp_run_pipeline_exempt` — PASSED
- `test_permission_denials_vexp_get_context_capsule_exempt` — PASSED
- `test_permission_denials_vexp_get_session_context_exempt` — PASSED
- `test_permission_denials_vexp_get_skeleton_exempt` — PASSED
- `test_permission_denials_vexp_index_status_exempt` — PASSED
- `test_permission_denials_vexp_search_memory_exempt` — PASSED
- `test_permission_denials_vexp_save_observation_is_not_exempted` — PASSED

Evidence: `evidence/executable-mcp-read-class-tools-extension-2026-05-25/pytest_full.txt`

---

## Structural Compliance

**DEV commit (`git show --stat HEAD`):**
```
 gates.py                                           |  10 +-
 knowledge/development/mcp-read-class-tools-extension-2026-05-25.md | 111 +++
 knowledge/research/agent-prompt-feedback.md        |  12 ++-
 tests/test_gates.py                                |  68 +++++++++++++++
 4 files changed, 199 insertions(+), 2 deletions(-)
```

The commit touched 4 files: the 3 expected files (`gates.py`, `tests/test_gates.py`, `knowledge/development/...`) plus the standard protocol `agent-prompt-feedback.md`. No unexpected files.

**`git diff HEAD~1 gates.py`:** diff is bounded to the `READ_CLASS_TOOLS` set literal (lines 35-43). No other functions, constants, or logic modified.

Evidence: `evidence/executable-mcp-read-class-tools-extension-2026-05-25/dev_commit.txt`, `evidence/executable-mcp-read-class-tools-extension-2026-05-25/diff_gates.txt`

---

## Rule 20 Self-Check

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-mcp-read-class-tools-extension-2026-05-25"
qa_report_path = "knowledge/qa/executable-mcp-read-class-tools-extension-2026-05-25.md"
evidence_dir = "knowledge/qa/evidence/executable-mcp-read-class-tools-extension-2026-05-25/"
required_evidence_files = [
    "pytest_full.txt", "dev_commit.txt", "diff_gates.txt"
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    """True if the line is a markdown table row marked with a positive status token."""
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
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
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-mcp-read-class-tools-extension-2026-05-25/
Files verified: 3
```

---

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all DEV deliverables against the plan specification. Ran full pytest suite confirming zero new regressions. Performed structural compliance checks on the DEV commit. Executed Rule 20 self-check.

### Files Deposited
- `knowledge/qa/executable-mcp-read-class-tools-extension-2026-05-25.md` — this QA report
- `knowledge/qa/evidence/executable-mcp-read-class-tools-extension-2026-05-25/` — evidence directory

### Flags for CEO
- None — all checks pass, zero new regressions
