# Bellows — BACKLOG #4 Phase 3a: Verdict-Only Resume Documentation
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA)
**Priority:** 5

## Context

BACKLOG #4 Phase 3a, per Phase 2 design at `bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md`. This plan ships **Option C** (procedural elimination of manual rename as a resume path) as a documentation update to PLANNER_TEMPLATE.md. Phase 3b/3c (DB-based step state recovery + plan-hash drift warning) are deferred to a separate session.

The bug: when a plan is in `verdict-pending-*` or `halted-*` state and the CEO manually renames it back to `executable-*` to resume, Bellows's runner defaults `current_step` to 1 and re-dispatches Step 1 from scratch. The verdict-consumer path (`_consume_verdicts()`) correctly tracks step state via filename parsing; the manual-rename path bypasses it.

Phase 3a closes the bug procedurally by documenting that manual rename is not the supported resume path. The supported path — deposit a continue verdict file in `bellows/verdicts/resolved/` — is what the Planner already does today (used three times this session for BACKLOG #1, #4, #5 closures). This plan codifies the constraint so future readers don't fall into the bug.

This is a markdown-only governance edit. Per the 2026-04-20 Lessons entry (Position A), markdown-only plans still get a QA step. The QA verification is lightweight: grep that the new subsection exists at the expected location, git log verification that the commit landed, Rule 20 self-check with minimal evidence files. No code, no tests.

**Split-commit pattern (per "Commit repo for governance-root edits" in PLANNER_TEMPLATE):** the DEV step produces TWO commits — one at governance root (`/Users/marklehn/Desktop/GitHub/`) for the PLANNER_TEMPLATE.md edit, one at bellows (for the dev log). The QA step's commits live at bellows.

Test Scope: none — pure documentation, no test execution required (governance edit).

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 (Documentation Analyst) inserts a new subsection into PLANNER_TEMPLATE.md under the Execution Model section, between "Execution Claiming" and "Cross-Plan Dependencies", and produces a dev log. Step 2 (Bellows QA) runs lightweight verification + Rule 20 self-check. Per disable-auto-close, terminal step pauses for Planner verdict.

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-verdict-only-resume-docs-2026-04-28.md", "bellows/knowledge/decisions/in-progress-executable-verdict-only-resume-docs-2026-04-28.md")`. Read your specialist file at `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` first. **Skip the domain glossary** — this is a governance documentation edit, no Bellows-specific domain vocabulary. **Mandatory read:** `bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md` — Phase 2 design that authorizes this edit. Treat its Section 4 recommendation and Section 5 Deliverable 1 as canonical. **Task 1 — insert new subsection into PLANNER_TEMPLATE.md.** Use `Filesystem:edit_file` against `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. The anchor for the edit is the line `**Stale detection:** If an `in-progress-` file has not been modified in over 30 minutes, another session may assume the original session crashed and reclaim it.` — this is the LAST line of the Execution Claiming subsection. Replace it with that exact line followed by `\n\n### Resume Protocol (Verdict-Only)\n\nWhen a Bellows-dispatched plan is paused (\`verdict-pending-*\` state), resume is verdict-only. Do NOT manually rename \`verdict-pending-*\` → \`executable-*\` to resume. Bellows's runner has no mechanism to recover the completed-step count from a fresh \`executable-*\` file — manual rename re-dispatches Step 1 from scratch. This is BACKLOG #4 and is structurally addressed by Phase 3b/3c (DB-based step state recovery).\n\n**Supported resume path (verdict-pending plans):** Deposit a continue verdict file at \`bellows/verdicts/resolved/verdict-{slug}-step-{N}.md\` with content:\n\n\`\`\`\ncontinue\n<reason — Rule 22 verification pass, CEO authorization, etc.>\n\`\`\`\n\nwhere \`{slug}\` is the plan's slug (filename minus lifecycle prefix and \`.md\` extension) and \`{N}\` is the step that just completed (matching the verdict request filename \`verdict-request-{slug}-step-{N}.md\`). Bellows's \`_consume_verdicts()\` parses the filename, dispatches step N+1, and renames the plan back to \`in-progress-*\`.\n\n**Halted plans:** No supported resume path exists today. A \`halted-*\` plan must be treated as cancelled. To re-attempt the work, deposit a NEW plan with a different filename. Resuming halted plans is part of the Phase 3b/3c deferred scope.\n\n**Relationship to Rule 25:** Rule 25's "Terminal-step resolution and Planner-owned Done/ move" already specifies the verdict-deposit-then-Done-move sequence for terminal steps. This subsection makes the underlying constraint explicit so it's discoverable by readers encountering the bug before reading Rule 25 in detail.`. **Task 2 — bump version.** Use `Filesystem:edit_file` to update the header. Replace `**Version:** 4.27` with `**Version:** 4.28`. Replace `**Last Updated:** 2026-04-24 (v4.27)` with `**Last Updated:** 2026-04-28 (v4.28)`. **Task 3 — add Lessons entry.** Use `Filesystem:edit_file` to append a new row to the Lessons Learned table. The anchor is the last existing row, which begins with `| 2026-04-23 | Bellows' step parser is positional and 1-indexed`. Replace that row with itself followed by `\n| 2026-04-28 | Phase 3a of BACKLOG #4 closure: Option C documentation shipped. Manual rename of \`verdict-pending-*\` → \`executable-*\` is not the supported resume path — it bypasses \`_consume_verdicts()\` and re-dispatches Step 1 from scratch. Supported resume is verdict-only: deposit a continue verdict file at \`bellows/verdicts/resolved/verdict-{slug}-step-{N}.md\` and Bellows's verdict consumer dispatches step N+1 correctly. New "Resume Protocol (Verdict-Only)" subsection added under Execution Model. Phase 3b (DB-based step state recovery) and Phase 3c (plan-hash drift warning) deferred to a separate session per the design at \`bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md\`. The Planner already follows this pattern (used 3× in this session for BACKLOG #1, #4, #5 closures); this entry codifies the procedure so future readers don't fall into the manual-rename bug. |`. **Task 4 — first commit (governance root).** `cd /Users/marklehn/Desktop/GitHub && git --no-pager status PLANNER_TEMPLATE.md && git add PLANNER_TEMPLATE.md && git commit -m "docs(planner): add Resume Protocol (Verdict-Only) subsection — BACKLOG #4 Phase 3a (v4.28)"`. **Task 5 — write dev log.** Use `Filesystem:write_file` to deposit `bellows/knowledge/development/verdict-only-resume-docs-dev-2026-04-28.md` with: (a) summary of the three edits to PLANNER_TEMPLATE.md (subsection insertion, version bump, Lessons entry); (b) the exact anchor used for each `Filesystem:edit_file` call; (c) governance-root commit hash; (d) reference to the Phase 2 design document this edit implements. **Task 6 — second commit (bellows).** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/development/verdict-only-resume-docs-dev-2026-04-28.md && git commit -m "docs(dev): verdict-only resume docs Phase 3a dev log"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/verdict-only-resume-docs-dev-2026-04-28.md`

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/verdict-only-resume-docs-dev-2026-04-28.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.** **Skip glossary AND specialist file reads** — this is governance edit verification. **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 Output Receipt "Files Created or Modified (Code)" list. For each listed deliverable, run a verification command and capture output to evidence: (a) `grep -n "### Resume Protocol (Verdict-Only)" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` should return exactly one line under the Execution Model section; (b) `grep -n "Version:.*4.28" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` should return one match; (c) `grep -c "2026-04-28.*Phase 3a of BACKLOG #4" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` should return 1; (d) `cd /Users/marklehn/Desktop/GitHub && git --no-pager log --oneline -1 -- PLANNER_TEMPLATE.md` should show the governance-root commit; (e) `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -1 -- knowledge/development/verdict-only-resume-docs-dev-2026-04-28.md` should show the bellows commit. Pipe ALL grep and git output to `bellows/knowledge/qa/evidence/executable-verdict-only-resume-docs-2026-04-28/grep_deliverables.txt`. Build a verification table with rows (a) through (e). **Task 1 — write QA report.** Use `Filesystem:write_file` to write `bellows/knowledge/qa/verdict-only-resume-docs-qa-2026-04-28.md` containing: (1) Rule 17 deliverable verification table, all rows ✅; (2) commit summary citing both governance-root and bellows commit hashes; (3) verdict on closure of BACKLOG #4 Phase 3a; (4) flag that Phase 3b/3c are deferred. **Task 2 — Rule 20 self-check.** Run this Python block exactly as written and include literal stdout in QA report:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-verdict-only-resume-docs-2026-04-28"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-only-resume-docs-qa-2026-04-28.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
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
> If self-check prints FAILED, stop and report. If PASSED, proceed. **Task 3 — Update bellows PROJECT_STATUS.md.** Use `Filesystem:edit_file` against `bellows/PROJECT_STATUS.md`. Find the most recent `### YYYY-MM-DD` heading and add a milestone entry under it (or create a new heading if today's date doesn't have one yet). Anchor: read the file first to identify the exact heading text or top of the Completed Milestones section. The entry should reference the verdict-only resume documentation, the v4.28 PLANNER_TEMPLATE bump, and the deferred Phase 3b/3c scope. **Task 4 — Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. **Task 5 — final commit (bellows).** `cd /Users/marklehn/Desktop/GitHub/bellows && git add PROJECT_STATUS.md knowledge/qa/verdict-only-resume-docs-qa-2026-04-28.md knowledge/qa/evidence/executable-verdict-only-resume-docs-2026-04-28/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: verdict-only resume docs Phase 3a verified, BACKLOG #4 Phase 3a closed"`. **STOP.** Do NOT move this plan to Done/. The Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/verdict-only-resume-docs-qa-2026-04-28.md`
> - `bellows/knowledge/qa/evidence/executable-verdict-only-resume-docs-2026-04-28/grep_deliverables.txt`
