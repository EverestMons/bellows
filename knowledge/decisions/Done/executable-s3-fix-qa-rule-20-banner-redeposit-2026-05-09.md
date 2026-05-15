# Executable — S3 Fix QA Re-deposit with Verbatim Rule 20 Banner

**Created:** 2026-05-09
**Author:** Planner
**Project:** bellows
**Type:** executable
**auto_close:** false
**Total Steps:** 1

---

## Context

The Step 2 QA report for `executable-s3-verdict-resolved-retry-loop-fix-2026-05-09` failed Bellows's `rule_20_self_check` gate because the Planner's plan asked QA to write a custom Python self-check rather than the verbatim Rule 20 template block from PLANNER_TEMPLATE. The gate searches for the literal banner string `Rule 20 — QA Self-Check Results` and the line `PASSED — SELF-CHECK PASSED`; the original report contained `## Rule 20 Self-Check` and `Rule 20 Self-Check: PASSED` instead.

Underlying fix substance is sound (commits `dc0bdd7` and `5136326` on main; 241/236 + 5 new tests, 0 regressions). The original QA report's Tasks A, B, and C are correct and complete. This re-QA touches only the Rule 20 self-check section and adds the missing pytest evidence file (Rule 18).

The original QA report path is `bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md`. This plan modifies that file in place.

## STEP 1 — Bellows QA: re-deposit Rule 20 self-check with verbatim banner

You are the Bellows QA. Re-deposit the existing S3 fix QA report with the verbatim Rule 20 self-check template block, replacing the prior custom self-check. Also deposit the missing pytest evidence file per Rule 18.

**Read first (required):**
- `bellows/agents/BELLOWS_QA.md` — your role
- `bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md` — the existing QA report you will modify
- `PLANNER_TEMPLATE.md` Rule 20 — the verbatim self-check template you will use

### Task A — Deposit pytest evidence file

Run the full Bellows test suite and capture the output to an evidence file:

```bash
mkdir -p bellows/knowledge/qa/evidence/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09
cd /Users/marklehn/Desktop/GitHub/bellows
python3 -m pytest tests/ -v > knowledge/qa/evidence/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09/pytest_full.txt 2>&1
```

Verify the file exists and is non-empty. Report total/passed/failed counts and confirm they match the prior QA report (241 passed, 1 pre-existing failure, 0 regressions). If the counts differ, halt and flag for CEO.

### Task B — Replace the Rule 20 Self-Check section

Open `bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md` and locate the existing `## Rule 20 Self-Check` section (everything from that heading through the end of its `**Output:**` code block, before the `## Output Receipt` heading).

Replace that entire section with the verbatim Rule 20 template block below, with substitutions:
- `plan_slug` = `executable-s3-verdict-resolved-retry-loop-fix-2026-05-09`
- `qa_report_path` = `bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md`
- `evidence_dir` = `bellows/knowledge/qa/evidence/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09/`
- `required_evidence_files` = `["pytest_full.txt"]`

Replacement section (paste verbatim, then update only the four substitution variables):

````markdown
## Rule 20 — QA Self-Check Results

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-s3-verdict-resolved-retry-loop-fix-2026-05-09"
qa_report_path = f"bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md"
evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    "pytest_full.txt",
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
<paste literal output of running the block from the bellows project root>
```
````

After substitution, EXECUTE the Python block from the bellows project root and paste the actual stdout into the `**Output:**` code block. Do NOT fabricate output — the block must be run.

### Task C — Self-verify

After the edit, grep the QA report file for the literal strings the gate enforces:

```bash
grep -c "Rule 20 — QA Self-Check Results" bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md
grep -c "PASSED — SELF-CHECK PASSED" bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md
```

Both counts must be `>= 1`. Report the counts in the Output Receipt.

### Constraints

- Do NOT modify Tasks A, B, or C of the original QA report. They are correct.
- Do NOT modify any code file. This is a QA-report-only edit + one new evidence file.
- Do NOT re-run the Step 1 DEV deliverable verification.
- The em-dash in `Rule 20 — QA Self-Check Results` is U+2014 (em-dash), not a hyphen. Copy it verbatim.

### Output Receipt

- Status: Complete / Partial / Blocked
- Files modified: cite each by path (`bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md`, `bellows/knowledge/qa/evidence/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09/pytest_full.txt`)
- Grep counts from Task C: both should be `>= 1`
- Test counts from Task A: total / passed / failed (must match prior report)
- CEO Flags: anything ambiguous, any deviation from the verbatim template

**Append agent-prompt-feedback** entry covering: clarity of the substitution instructions, whether the verbatim template was directly usable, whether anything tripped you up.

**Deposits:**
- `bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md`
- `bellows/knowledge/qa/evidence/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09/pytest_full.txt`
- `bellows/knowledge/research/agent-prompt-feedback.md`

---

## Bootstrap prompt for CEO

```
RUN EXE bellows
```
