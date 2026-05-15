# Bellows — Add Parallel Group Dispatch Subsection to Bellows Execution Model
**Date:** 2026-05-05 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After Step 1 completes and the CEO confirms, paste the bootstrap a second time to advance to Step 2. The agent does NOT move the plan to Done — the Planner performs the Done/ move after Rule 22 verification on Step 2's deposits.

Bootstrap prompt:
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05.md. Execute the next pending step ONLY. After completing the step, STOP and wait for my confirmation. Do NOT proceed to subsequent steps. Do NOT move the plan to Done.
```

**Note on commit repos:** This plan edits `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` (governance root) AND deposits artifacts under `bellows/knowledge/`. Per Rule 8 / Plan File Structure "Commit repo for governance-root edits": the PLANNER_TEMPLATE edit commits to the governance-root repo at `/Users/marklehn/Desktop/GitHub/`. The plan's own housekeeping deposits (dev log, QA report) commit to the bellows repo. Two commits, one per repo.

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05.md", "bellows/knowledge/decisions/in-progress-parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05.md")`. Skip specialist file and glossary reads — this is a markdown documentation edit. You are the Bellows Documentation Analyst. **Context:** BACKLOG entry 2026-05-01 identifies a documentation gap in PLANNER_TEMPLATE.md v4.31's "Bellows Execution Model" section — the section describes the state machine, eight gates, verdict cycle, and disable-auto-close model, but does not mention parallel group dispatch (the `parallel-N-` filename prefix, `_pending_groups`, 5-second settle window in PlanHandler). The mechanic is documented in the File Naming Convention subsection elsewhere in PLANNER_TEMPLATE.md (around line 385) but a reader consulting the Bellows Execution Model section to understand how Bellows dispatches plans would not learn that parallel dispatch exists as a native path with its own concurrency semantics. **Task:** Add a new subsection titled "Parallel Group Dispatch" to the Bellows Execution Model section in PLANNER_TEMPLATE.md. Insert it BETWEEN the Planner Discipline cross-reference table (which ends with the Rule 26 row) and the existing `### What Bellows Does NOT Do` subsection. Use `Desktop Commander:edit_block` for the insertion with this exact anchored edit: replace the verbatim line `| Rule 26 | \`**Deposits:**\` field convention — declarative deposit enumeration that replaces prose-embedded path scanning. |` with that same line followed by the new subsection content. **New subsection content (verbatim):**
> ```
> | Rule 26 | `**Deposits:**` field convention — declarative deposit enumeration that replaces prose-embedded path scanning. |
>
> ### Parallel Group Dispatch
>
> Plans with the `parallel-N-` filename prefix are dispatched as a group. All plans sharing the same group number `N` (e.g., `parallel-1-executable-foo-2026-05-05.md`, `parallel-1-diagnostic-bar-2026-05-05.md`) are claimed and dispatched concurrently rather than sequentially. The `parallel-N-` prefix is the Planner's signal to Bellows that the plans in the group have been verified file-conflict-free and can run simultaneously. The naming convention itself is documented in the File Naming Convention subsection above; this subsection covers the dispatch mechanics.
>
> **Mechanics.** Bellows's `PlanHandler` (the watchdog filesystem event handler) maintains a `_pending_groups` dictionary keyed by `(project_path, group_number)`. When a `parallel-N-` plan file is created or moved into a watched `knowledge/decisions/` directory, the handler does not dispatch immediately — it adds the plan to the pending group and arms a 5-second settle timer. If additional `parallel-N-` plans with the same group number land within the settle window, they accumulate into the same group entry. When the settle window expires with no further additions, Bellows claims all plans in the group atomically (via `shutil.move` to `in-progress-*` for each) and dispatches them concurrently as separate `claude -p` subprocesses through `runner.py`. The settle window exists to absorb the time gap between the Planner's atomic deposits of multiple group members.
>
> **Concurrency model.** Each plan in a parallel group runs in its own subprocess with its own working directory, its own gate evaluation, and its own verdict request file. The group has no shared lifecycle — one plan can pause for verdict while siblings continue, one plan can fail and trip a gate while siblings succeed, and one plan can complete and move to Done while siblings are still mid-step. From Bellows's perspective each plan is an independent dispatch that happens to have been claimed at the same instant.
>
> **Working-tree shared state.** All plans in a parallel group execute against the same project working tree. There is no per-plan worktree isolation. This is the source of the open BACKLOG item (`scope_check` diff-collision from concurrent activity, original observation 2026-04-30, expanded with external-vector reproduction 2026-05-04): when two parallel siblings both modify or commit files during their respective execution windows, each plan's `_capture_git_diff()` post-step observation includes files changed by the OTHER plan, which trips `scope_check` on whichever plan does not commit first. The same failure class extends beyond parallel siblings — any concurrent activity in the project subtree (CEO `mv`, another Claude session, cron jobs, cleanup scripts) produces the same false-positive trip.
>
> **Practical implication.** Until the working-tree-shared issue is structurally fixed (per-plan git worktree, process-filtered file-touch tracking, or commit-message slug scoping — fix candidates enumerated in the BACKLOG entry), the `parallel-N-` pattern is currently safe ONLY for plans that do not commit during DEV — read-only diagnostics, plans where commits are deferred until all parallel siblings finish, or plans whose deposits target disjoint file sets that scope_check reliably distinguishes. For plans that commit during execution, sequential dispatch (no `parallel-N-` prefix) is the safer choice. The Planner is responsible for evaluating commit-time overlap when deciding whether to assign the `parallel-N-` prefix.
> ```
> Use `Desktop Commander:edit_block` with the file_path argument set to `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`, old_string set to the verbatim line `| Rule 26 | \`**Deposits:**\` field convention — declarative deposit enumeration that replaces prose-embedded path scanning. |`, and new_string set to the full block above (the Rule 26 line followed by the new subsection content, including the blank line before `### Parallel Group Dispatch`). Then update the version footer: replace verbatim `**Version:** 4.31` (line 5) with `**Version:** 4.32`, and replace verbatim `**Last Updated:** 2026-05-01 (v4.31)` (line 6) with `**Last Updated:** 2026-05-05 (v4.32)`. Three edit_block calls total. After edits, deposit a short development log to `bellows/knowledge/development/parallel-group-dispatch-subsection-dev-log-2026-05-05.md` recording: (a) the three edits applied with old→new summaries, (b) line count of the new subsection, (c) Output Receipt. Then commit BOTH repos. First commit (governance root): `cd /Users/marklehn/Desktop/GitHub/ && git --no-pager add PLANNER_TEMPLATE.md && git commit -m "docs: PLANNER_TEMPLATE v4.32 — add Parallel Group Dispatch subsection to Bellows Execution Model"`. Second commit (bellows): `cd /Users/marklehn/Desktop/GitHub/bellows/ && git --no-pager add knowledge/development/parallel-group-dispatch-subsection-dev-log-2026-05-05.md knowledge/decisions/in-progress-parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05.md && git commit -m "docs: dev log for v4.32 PLANNER_TEMPLATE parallel-group subsection"`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
> - `bellows/knowledge/development/parallel-group-dispatch-subsection-dev-log-2026-05-05.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation.**

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/parallel-group-dispatch-subsection-dev-log-2026-05-05.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. Skip specialist file and glossary reads — this is a markdown documentation verification task. You are the Bellows QA. **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. For EVERY listed file: verify it exists on disk and contains the described change. Specifically: (1) verify `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` contains a `### Parallel Group Dispatch` heading — `grep -n "### Parallel Group Dispatch" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/grep_subsection_heading.txt`. Expect exactly one match between line 887 (where Rule 26 row was) and line 889 (where `### What Bellows Does NOT Do` was). (2) verify the version footer was updated — `grep -n "^\*\*Version:\*\* 4.32$" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/grep_version.txt` and `grep -n "^\*\*Last Updated:\*\* 2026-05-05 (v4.32)$" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/grep_last_updated.txt`. Expect one match each. (3) verify the new subsection mentions: `_pending_groups`, `5-second settle window`, `working-tree`, `scope_check`, `parallel-N-`, and the BACKLOG cross-reference (the phrase `2026-04-30` and `2026-05-04`) — `grep -nE "(_pending_groups|5-second settle|working-tree|scope_check|parallel-N-|2026-04-30|2026-05-04)" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/grep_subsection_content.txt`. Expect at least 6 matches in the new subsection range. (4) verify both commits exist — `cd /Users/marklehn/Desktop/GitHub/ && git --no-pager log --oneline -1 -- PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/git_log_governance.txt` and `cd /Users/marklehn/Desktop/GitHub/bellows/ && git --no-pager log --oneline -1 -- knowledge/development/parallel-group-dispatch-subsection-dev-log-2026-05-05.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/git_log_bellows.txt`. Expect non-empty output for each. (5) verify the existing `parallel-1-` content elsewhere in PLANNER_TEMPLATE.md (around line 385 in the File Naming Convention subsection) is unchanged — `grep -nA 6 "Parallel plan groups" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/grep_naming_convention_unchanged.txt`. Expect the original three filename examples to be present unchanged. **Test Scope: targeted** — no test suite to run for a documentation-only edit; no `pytest_targeted.txt` is required. Produce a verification table in the QA report: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If any item is ❌, attempt to fix or flag as blocked for CEO. Deposit QA report to `bellows/knowledge/qa/parallel-group-dispatch-subsection-qa-2026-05-05.md` using `Filesystem:write_file`. Append a dated entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Final commit (bellows repo): `cd /Users/marklehn/Desktop/GitHub/bellows/ && git --no-pager add knowledge/qa/parallel-group-dispatch-subsection-qa-2026-05-05.md knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: parallel-group-dispatch subsection v4.32"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes. **Mandatory Rule 20 self-check** — execute this Python block exactly and include its literal stdout in the QA report:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05"
> qa_report_path = "bellows/knowledge/qa/parallel-group-dispatch-subsection-qa-2026-05-05.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_subsection_heading.txt",
>     "grep_version.txt",
>     "grep_last_updated.txt",
>     "grep_subsection_content.txt",
>     "git_log_governance.txt",
>     "git_log_bellows.txt",
>     "grep_naming_convention_unchanged.txt",
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
> If self-check prints `FAILED — SELF-CHECK FAILED`, STOP — do NOT do the final commit, report the failure to the CEO. If self-check prints `PASSED — SELF-CHECK PASSED`, proceed with the final commit above. **Deposits:**
> - `bellows/knowledge/qa/parallel-group-dispatch-subsection-qa-2026-05-05.md`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05/` (multiple files per Rule 20 self-check)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT move this plan to Done. Wait for CEO confirmation. The Planner performs the Done/ move after Rule 22 verification.**
