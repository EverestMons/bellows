# Bellows — Close Stranded planner-template-lessons-step-numbering Plan
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted (no test execution; pure file-state verification of a 9-day-old governance edit) | **Execution:** Step 1 (Bellows QA)
**Priority:** 1

## Context

The plan `executable-planner-template-lessons-step-numbering-2026-04-23` deposited a Lessons Learned row to `PLANNER_TEMPLATE.md` on 2026-04-23. Step 1 (Documentation Agent) completed successfully — dev log at `bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md` reports Status: Complete and the lesson row is currently live in `PLANNER_TEMPLATE.md`. Step 2 (QA) never ran — the plan tripped `no_permission_denials` on Grep against PLANNER_TEMPLATE.md (BACKLOG #2's pre-fix gate behavior, since closed 2026-04-28 with READ_CLASS_TOOLS filter). Plan has been stranded at `verdict-pending-` for 9 days.

This plan runs the QA verification that should have happened on 2026-04-23 against the current state of `PLANNER_TEMPLATE.md`. The original plan's checks are adapted to 2026-05-01 reality: subsequent edits have moved the row's position relative to the table tail, and the version field has advanced to v4.29. Adapted checks verify the row is present, distinctively phrased, and adjacent to its v4.26 anchor — which proves the original work landed correctly and was preserved through subsequent edits.

After this plan closes via Rule 25 terminal-step resolution, the Planner separately deposits a continue verdict (correct `verdict: continue` format) for the original stranded plan to advance it from `verdict-pending-` to `Done/`.

Test Scope: targeted — no test execution at all. Pure read-only file verification.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-close-stranded-lessons-step-numbering-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — Bellows QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-close-stranded-lessons-step-numbering-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-close-stranded-lessons-step-numbering-2026-05-01.md")`. **Skip specialist file and glossary reads — this is a mechanical re-verification of a 9-day-old governance edit.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all Grep operations against PLANNER_TEMPLATE.md** — do NOT use the native Grep tool, as PLANNER_TEMPLATE.md lives at governance root and historical plans have tripped `no_permission_denials` when using native Grep against cross-project paths (the read-class filter shipped 2026-04-28 makes this safe today, but bash is unconditional). **Task:** Run the QA verification that was originally Step 2 of `executable-planner-template-lessons-step-numbering-2026-04-23`, adapted to current state. Create the evidence directory at `bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/` if it does not exist. **Verification checks (all use bash, all deposit literal output to evidence files):** (1) **Distinctive new-row grep** — `grep -n "Bellows' step parser is positional and 1-indexed" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/grep_new_row.txt 2>&1`. Expect exactly 1 match. (2) **v4.26 anchor row preserved** — `grep -n "2026-04-20 | v4.26 governance sweep" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/grep_anchor_preserved.txt 2>&1`. Expect exactly 1 match. (3) **Adjacency check** — both rows must be on consecutive lines, with the new row immediately after the anchor. Compute via: `awk -F: '{print $1}' bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/grep_new_row.txt > /tmp/new_line.txt && awk -F: '{print $1}' bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/grep_anchor_preserved.txt > /tmp/anchor_line.txt && echo "anchor_line: $(cat /tmp/anchor_line.txt) | new_line: $(cat /tmp/new_line.txt) | diff: $(($(cat /tmp/new_line.txt) - $(cat /tmp/anchor_line.txt)))" > bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/adjacency_check.txt 2>&1`. Expect `diff: 1`. **Deposit QA report** to `bellows/knowledge/qa/close-stranded-lessons-step-numbering-qa-2026-05-01.md` containing: (a) plan context noting this is a 9-day-late re-verification, (b) verification table with columns `| Check # | Description | Expected | Status (✅/❌) | Evidence |` citing the three evidence file paths, (c) literal stdout of the Rule 20 self-check block. **Mandatory Rule 20 self-check block (execute verbatim from /Users/marklehn/Desktop/GitHub/, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "executable-close-stranded-lessons-step-numbering-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/close-stranded-lessons-step-numbering-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_new_row.txt",
>     "grep_anchor_preserved.txt",
>     "adjacency_check.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
>
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
>
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If the self-check prints `FAILED`, STOP — do not proceed with closeout, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23: **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/ bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: close stranded planner-template-lessons-step-numbering plan (9-day-late re-verification)"`. **STOP. Plan complete after this step. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification per Rule 25.**
>
> **Deposits:**
> - `bellows/knowledge/qa/close-stranded-lessons-step-numbering-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/grep_new_row.txt`
> - `bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/grep_anchor_preserved.txt`
> - `bellows/knowledge/qa/evidence/executable-close-stranded-lessons-step-numbering-2026-05-01/adjacency_check.txt`
