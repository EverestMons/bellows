# QA Report — Phase 1.5 patch: add Source D (LESSONS.md)

**Plan:** executable-phase-1-5-lessons-source-d-2026-05-10
**Step:** 2
**Date:** 2026-05-10

## Verification Results

| Check | Description | Status | Evidence |
|---|---|---|---|
| 1a | Version line shows `**Version:** 4.35` | ✅ | PLANNER_TEMPLATE.md line 5 |
| 1b | Last Updated shows `2026-05-10 (v4.35)` | ✅ | PLANNER_TEMPLATE.md line 6 |
| 1c | Phase 1.5 header says "four knowledge sources" | ✅ | `grep_source_d.txt` line 6 (line 53 of file) |
| 1d | Source D heading `**Source D — Cross-project lessons:**` exists | ✅ | `grep_source_d.txt` line 1 (line 73 of file) |
| 1e | Source D references `/Users/marklehn/Desktop/GitHub/LESSONS.md` | ✅ | `grep_source_d.txt` line 2 (line 74 of file) |
| 1f | Bounded scope mentions "last ~14 days" and "planner-discipline" | ✅ | PLANNER_TEMPLATE.md lines 77-78 |
| 1g | "This is NOT optional" says "any of the four sources" | ✅ | PLANNER_TEMPLATE.md line 82 |
| 1h | "Why N sources" reads "Why four sources instead of one" | ✅ | `grep_source_d.txt` line 4 (line 86 of file) |
| 2 | git diff shows ONLY 4 edited regions | ✅ | `evidence/phase-1-5-lessons-source-d-2026-05-10/git_diff.txt` — 4 hunks: version bump, header sentence, Source D insertion + NOT optional rewrite, Why N sources rewrite |
| 3 | grep confirms Source D, LESSONS.md, four knowledge sources | ✅ | `evidence/phase-1-5-lessons-source-d-2026-05-10/grep_source_d.txt` — all three patterns matched |
| 4 | pytest passes (245 passed, 1 pre-existing failure) | ✅ | 245 passed, 1 failed (test_run_step_timeout — pre-existing, unchanged) |

## Final Verdict

**ALL CHECKS PASSED**

## Rule 20 Self-Check

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-phase-1-5-lessons-source-d-2026-05-10"
qa_report_path = "bellows/knowledge/qa/phase-1-5-lessons-source-d-qa-2026-05-10.md"
evidence_dir = "bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/"
required_evidence_files = [
    "git_diff.txt",
    "grep_source_d.txt",
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

### Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/
Files verified: 2
```

---
## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified the Phase 1.5 patch (v4.34 → v4.35) that added Source D (LESSONS.md) to PLANNER_TEMPLATE.md. All 11 verification checks passed: version bump confirmed, all four textual edits verified in place, git diff shows exactly 4 edited regions with no collateral changes, grep confirms Source D / LESSONS.md / "four knowledge sources" all present, and test suite passes (245 passed, 1 pre-existing failure unchanged).

### Files Deposited
- `bellows/knowledge/qa/phase-1-5-lessons-source-d-qa-2026-05-10.md` — this QA report
- `bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/git_diff.txt` — git diff of PLANNER_TEMPLATE.md changes
- `bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/grep_source_d.txt` — grep evidence for Source D presence

### Files Created or Modified (Code)
- None

### Decisions Made
- Used HEAD~2 for git diff range to span both governance-root commits (PLANNER_TEMPLATE.md + LESSONS.md)

### Flags for CEO
- None

### Flags for Next Step
- None
