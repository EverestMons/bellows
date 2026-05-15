# QA Report — Backlog Addendum: scope_check External-Vector Reproduction

**Date:** 2026-05-04
**Plan:** executable-backlog-addendum-scope-check-external-vector-2026-05-04
**Step:** 2 — Bellows QA

## Deliverable Verification

| # | Deliverable | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|
| 1 | Leading tag retitled | grep count = 1 for `^- 2026-04-30: scope_check diff-collision from concurrent activity` | 1 | ✅ | `knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/grep_retitle.txt` |
| 2 | Addendum subsection landed | grep count = 1 for `External-vector reproduction 2026-05-04:` | 1 | ✅ | `knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/grep_addendum.txt` |
| 3 | Entry still single bullet (fix-shape inline) | exactly 1 match on line 13 (same line as `2026-04-30:` entry) | line 13 match (same bullet) | ✅ | `knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/grep_fixshape_inline.txt` |
| 4 | Commit landed | top git log entry = `docs: backlog — broaden scope_check diff-collision entry with external-vector reproduction` | `eb0e8ad docs: backlog — broaden scope_check diff-collision entry with external-vector reproduction` | ✅ | `knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/git_log_backlog.txt` |

## Test Regression

NOT REQUIRED — markdown-only edits, no production code or test-exercised code touched. Per Rule 21, no full-suite run needed.

## Rule 20 — Mandatory QA Self-Check

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-backlog-addendum-scope-check-external-vector-2026-05-04"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/backlog-addendum-scope-check-external-vector-qa-2026-05-04.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    "grep_retitle.txt",
    "grep_addendum.txt",
    "grep_fixshape_inline.txt",
    "git_log_backlog.txt",
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["\u2705", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "\u2705":
                if "\u2705" in cell:
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
print("Rule 20 \u2014 QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED \u2014 SELF-CHECK FAILED \u2014 {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED \u2014 SELF-CHECK PASSED \u2014 all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

**Self-check output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/
Files verified: 4
```
