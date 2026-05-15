# QA Report — Close Monorepo-Worktree BACKLOG Entry

**Date:** 2026-05-04
**Plan:** executable-close-monorepo-worktree-backlog-2026-05-04
**Step:** 2 — QA
**Role:** Bellows QA

## Output Receipt

**Status:** Complete
**Files Created or Modified:**
- `bellows/knowledge/qa/close-monorepo-worktree-backlog-qa-2026-05-04.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/` — 4 evidence files
- `bellows/PROJECT_STATUS.md` — new milestone entry appended

## Deliverable Verification (Rule 17)

Prior step's Output Receipt listed 3 files:
1. `bellows/knowledge/BACKLOG.md` — verified via Checks 1–3
2. `bellows/knowledge/documentation/close-monorepo-worktree-backlog-dev-log-2026-05-04.md` — read and confirmed Status: Complete
3. `bellows/knowledge/research/agent-prompt-feedback.md` — listed in receipt, not gated by this QA scope

## Verification Table

| # | Deliverable | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|
| 1 | Entry removed from Open section | grep count = 0 | 0 | ✅ | `knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/grep_open_section.txt` |
| 2 | Entry added to Closed section | grep count = 1 | 1 | ✅ | `knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/grep_closed_section.txt` |
| 3 | Closed section ordering preserved | Line 1: Closed 2026-05-04 monorepo, Line 2: Closed 2026-05-03 worktree teardown, Line 3: Closed 2026-05-03 step-count | Line 59: Closed 2026-05-04 monorepo, Line 61: Closed 2026-05-03 worktree teardown, Line 63: Closed 2026-05-03 step-count | ✅ | `knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/grep_closed_ordering.txt` |
| 4 | Commit landed | Top entry: `docs: backlog — close 2026-05-04 monorepo-worktree-at-governance-root entry` | `9f04b59 docs: backlog — close 2026-05-04 monorepo-worktree-at-governance-root entry` | ✅ | `knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/git_log_backlog.txt` |

## Test Regression

**NOT REQUIRED** — markdown-only edits, no production code touched, no test-exercised code touched.

## Rule 20 — Mandatory QA Self-Check

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-close-monorepo-worktree-backlog-2026-05-04"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/close-monorepo-worktree-backlog-qa-2026-05-04.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    "grep_open_section.txt",
    "grep_closed_section.txt",
    "grep_closed_ordering.txt",
    "git_log_backlog.txt",
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
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
        if fname == "grep_open_section.txt":
            if not os.path.isfile(fpath):
                failures.append(f"CRITICAL: evidence file missing: {fpath}")
        else:
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

**Self-check output:**
```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/
Files verified: 4
```
