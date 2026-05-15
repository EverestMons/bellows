# PLANNER_TEMPLATE Lessons Learned — Diagnostic Verification + Test Naming
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Documentation Agent) → Step 2 (QA)

## How to Run This Plan

Bellows will auto-claim. Step 1 (Documentation Agent) adds two Lessons Learned entries to PLANNER_TEMPLATE.md v4.29 capturing today's diagnostic-verification failure and test-naming-vs-assertion mismatch lessons. Step 2 (QA) verifies edits landed and runs Rule 20 self-check. Per the split-commit pattern, governance-root edits commit to `/Users/marklehn/Desktop/GitHub/` (the eluvian-governance backup repo); plan housekeeping commits to bellows.

**Bootstrap (manual fallback only):**
```
Read the plan at bellows/knowledge/decisions/executable-planner-template-lessons-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-planner-template-lessons-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-planner-template-lessons-2026-05-01.md")`. **You are the Bellows Documentation Analyst.** Skip glossary read — this is governance-root markdown editing. **Task:** add two new entries to the Lessons Learned table in `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Find the table; the most recent entry is dated 2026-04-30 (about the Bellows Execution Model section addition). The two new entries go at the bottom of the table, both dated 2026-05-01. **Entry 1 — diagnostic verification end-to-end thought-experiment:** insert this as a new row at the bottom of the table: `| 2026-05-01 | The Planner's Rule 22 verification of a diagnostic's recommendation must include end-to-end thought-experiment of the proposed fix against the actual observed bug pattern, not categorical mapping of the bug to a sub-case. The failed close on the parallel-plan scope_check fix happened because the Planner reasoned through "scenario 1 (sibling commits previously-dirty file)" and "scenario 2 (sibling edits files mid-step)" — and concluded scenario 1 was the BACKLOG case. But the 2026-04-30 collision involved sibling DEV agents actively writing code AND committing it (modify-then-commit), which is scenario 2, not scenario 1. The categorical match made the SA's recommendation look right; an end-to-end check ("if a sibling DEV writes file X to disk during plan A's step, does plan A's diff include X?") would have surfaced that the recommendation only solves scenario 1, not the observed bug. The shipped fix (file-checksum snapshot) was reverted via plan \`executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01\`. **Lesson:** when an SA recommends a fix shape, the Planner's Rule 22 verification of the diagnostic must include the question: "If I trace through the original observed bug step-by-step, does this fix actually prevent it?" If the answer requires categorizing the bug into a sub-case to be true, the categorization must be verified against the actual incident, not assumed. Rule 22's check (b) ("does the file's content actually answer the original questions") interrogates substance, not just structural completeness — load-bearing claims in agent recommendations need to be traced, not accepted. |` **Entry 2 — test naming vs assertion mismatch:** insert this as a new row immediately after Entry 1: `| 2026-05-01 | Test names that imply a property must have assertions that verify that property. During the failed snapshot-fix close (see preceding entry), the DEV's test \`test_diff_immune_to_sibling_changes_in_unrelated_files\` had a name claiming sibling-immunity, but its assertions allowed sibling-modified files to appear in the diff — the test passed when \`plan_b_file.txt in diff_a\` was True. The mismatch was visible in the test's own commentary ("plan_b_file.txt DOES appear (it genuinely changed on disk) — but that's correct behavior for snapshot-based diff"). The Planner specified the test in the plan; the agent implemented it faithfully; QA passed it. The name-vs-assertion gap created false assurance. **Lesson:** when the Planner specifies a test in a plan, the assertion must encode the property the test name implies. If the property cannot be encoded as an assertion (because the implementation doesn't actually have the property), the test name is misleading and either the property or the name needs to change. A test named for immunity that passes when the property is violated is worse than no test — it provides false assurance and hides the bug from reviewers who skim test names rather than read assertions. |` **Tooling guidance:** Read the current PLANNER_TEMPLATE.md to locate the Lessons Learned table (search for `## Lessons Learned`), confirm the table structure (header row, separator row, data rows), and identify the last row. Use the Filesystem MCP write tool or edit_block to insert both new rows at the bottom of the table while preserving table structure. **Do NOT bump the PLANNER_TEMPLATE version number** — Lessons Learned additions don't constitute a version bump; the version stays at v4.29 (only structural rule changes warrant a version bump per existing convention). **Commit (split-commit pattern):** `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md && git commit -m "docs(planner): add 2026-05-01 lessons — diagnostic verification + test naming"`. **Output deposit:** Write a dev log to `bellows/knowledge/development/planner-template-lessons-2026-05-01.md` summarizing the two entries added, the line numbers where they were inserted, and the commit SHA. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
> - `bellows/knowledge/development/planner-template-lessons-2026-05-01.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/planner-template-lessons-2026-05-01.md` and confirm the Output Receipt status is Complete. If not, stop and report to CEO before proceeding.** **You are the Bellows QA agent.** Skip glossary read. Test scope: targeted (markdown-only edits to governance-root file, no test suite). **FIRST — Deliverable Verification.** (1) Run `grep -c "2026-05-01" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — expect at least 2 (one for each new lesson row, plus any pre-existing references). Pipe to `bellows/knowledge/qa/evidence/executable-planner-template-lessons-2026-05-01/grep_2026_05_01.txt`. (2) Run `grep -n "diagnostic verification" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — expect at least one match in Entry 1's row. Pipe to `bellows/knowledge/qa/evidence/executable-planner-template-lessons-2026-05-01/grep_diagnostic_verification.txt`. (3) Run `grep -n "test_diff_immune_to_sibling_changes_in_unrelated_files" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — expect exactly one match in Entry 2's row. Pipe to `bellows/knowledge/qa/evidence/executable-planner-template-lessons-2026-05-01/grep_test_name.txt`. (4) Run `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --format=%s -- PLANNER_TEMPLATE.md` — expect the commit message from Step 1 (`docs(planner): add 2026-05-01 lessons — diagnostic verification + test naming`). Pipe to `bellows/knowledge/qa/evidence/executable-planner-template-lessons-2026-05-01/git_log_governance.txt`. **Produce verification table:** `| Deliverable | Expected | Status (✅/❌) | Evidence |` with rows for: (a) at least 2 occurrences of "2026-05-01" in PLANNER_TEMPLATE.md, (b) Entry 1 (diagnostic verification) present, (c) Entry 2 (test naming) present, (d) governance-root commit landed with descriptive message. If ANY item is ❌, stop and report to CEO. **Deposit QA report** at `bellows/knowledge/qa/qa-planner-template-lessons-2026-05-01.md` with the verification table and the literal stdout of the Rule 20 self-check below. **Update PROJECT_STATUS.md** with milestone entry: "Added 2026-05-01 Lessons Learned entries to PLANNER_TEMPLATE.md v4.29: (1) diagnostic Rule 22 verification needs end-to-end thought-experiment; (2) test names that imply a property must encode it as assertions. Both lessons derived from the failed snapshot-fix close attempt." Commit PROJECT_STATUS.md to bellows. **Final commit and STOP — do NOT move this plan to Done. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.** **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. The feedback append + commit are the absolute last operations. **Run the Rule 20 self-check at the very end and include its literal stdout in the QA report:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-planner-template-lessons-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/qa-planner-template-lessons-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_2026_05_01.txt",
>     "grep_diagnostic_verification.txt",
>     "grep_test_name.txt",
>     "git_log_governance.txt",
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
> **Deposits:**
> - `bellows/knowledge/qa/qa-planner-template-lessons-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-planner-template-lessons-2026-05-01/` (4 files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
