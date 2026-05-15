# Bellows — Close BACKLOG Entry: 2026-05-03 multi-step plan step-count regression
**Date:** 2026-05-03 | **Tier:** Small | **Test Scope:** targeted (markdown-only, no production code) | **Execution:** Step 1 (BELLOWS DOCUMENTATION) → Step 2 (BELLOWS DOCUMENTATION QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. The Planner moves the plan to Done after Rule 22 verification passes.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-close-2026-05-03-step-count-regression-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

## Background (read before executing)

The BACKLOG entry dated 2026-05-03 titled "multi-step plan step-count regression" describes Bellows reporting `plan has 1 steps` for plans with multiple `## STEP N —` headers. The entry was authored after the symptom was observed today, but BEFORE the corrective fix shipped later the same day.

The bug was actually a different cause than the BACKLOG entry's hypothesis: not a regex problem (em-dash, execution-map line, shadow-cache divergence) but an unconditional `if is_diagnostic: total_steps = 1` override at two sites in `bellows.py` that forced all diagnostic plans to single-step regardless of header count.

The fix shipped via:
- Diagnostic that identified the cause: `bellows/knowledge/decisions/Done/diagnostic-extract-total-steps-undercount-2026-05-03.md` (findings at `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md`)
- A first corrective attempt (`executable-remove-is-diagnostic-step-override-2026-05-03`) which removed both overrides outright but broke Phase 8.1 for header-less diagnostics — halted via stop verdict
- The narrow-override re-fix that landed (`executable-corrective-narrow-is-diagnostic-override-2026-05-03.md` in Done/) — commit `9786e87` for the fix, `799f908` for the dev log

QA report at `bellows/knowledge/qa/corrective-narrow-override-qa-2026-05-03.md` confirms: behavioral spot-check ran `extract_total_steps()` against `diagnostic-worktree-implementation-surface-2026-05-03.md` (the exact 3-step plan the BACKLOG entry cites) and got the correct return value of 3. Test regression: 66 passed, 0 failed. Bellows daemon was restarted post-fix, picking up the live narrow override at line 245 of bellows.py.

This plan is markdown-only — it adds a Closed entry to BACKLOG.md and removes the corresponding Open entry. No production code changes. Per PLANNER_TEMPLATE Position A (no markdown-only QA carve-out), Step 2 QA is mandatory but lightweight: grep verification that edits landed, git log verification of commit, Rule 20 self-check.

---
---

## STEP 1 — BELLOWS DOCUMENTATION

---

> **STOP REMINDER (TOP):** This is the implementation step. After completing this step, STOP and wait for CEO confirmation. Do NOT execute Step 2 (QA verification). Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes. **If any phase below fails, write the failure details to `bellows/knowledge/development/close-step-count-regression-failure-log-2026-05-03.md` BEFORE stopping. Do not stop silently.**
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-close-2026-05-03-step-count-regression-2026-05-03.md", "bellows/knowledge/decisions/in-progress-executable-close-2026-05-03-step-count-regression-2026-05-03.md")`.
>
> You are the Bellows Documentation Agent. Skip specialist file and glossary reads — this is markdown housekeeping.
>
> **Phase 1 — Remove the stale Open entry from BACKLOG.md.** Use `Desktop Commander:edit_block` against `bellows/knowledge/BACKLOG.md`. The `old_string` is the entire BACKLOG entry bullet — read the file first to get the EXACT verbatim text. The bullet starts with `- 2026-05-03: **multi-step plan step-count regression — Bellows reports` and ends with `~$0.10 diagnostic. High priority — affects every future multi-step plan.`. The bullet is one continuous markdown line (~2700 characters). Replace with empty string (delete the bullet AND the trailing blank line that separates it from the next bullet — but verify by reading the file structure that the resulting BACKLOG.md does not have two consecutive blank lines at the deletion site). `expected_replacements=1`. If edit_block reports a near-miss diff, STOP and write the diff output to the failure log.
>
> **Phase 2 — Add the Closed entry to BACKLOG.md.** Use `Desktop Commander:edit_block`. The Closed section starts with the line `## Closed` followed by a blank line and the first existing closed entry. Newest closed entries go at the top per the file's existing convention (which already shows `Closed 2026-05-01` first, then `Closed 2026-04-30`, etc.). The `old_string` is the verbatim two-line anchor: the `## Closed` header line, followed by the blank line, followed by the first existing closed bullet's first line `- **Closed 2026-05-01:** Phase 3b/3c DB step-state-resume slug-collision.`. The `new_string` keeps the `## Closed` header and blank line, then inserts the new closed entry as a NEW bullet, then a blank line, then the existing first closed bullet's first line resumes. The new closed entry text:
>
> `- **Closed 2026-05-03:** BACKLOG `2026-05-03: multi-step plan step-count regression`. The entry was authored after observing the symptom (Bellows reporting `plan has 1 steps` for `diagnostic-parallel-scope-check-collision-2026-05-03` and `diagnostic-worktree-implementation-surface-2026-05-03`) but before the corrective fix shipped the same day. Root cause was NOT a regex regression as the entry hypothesized — it was an unconditional `if is_diagnostic: total_steps = 1` override at two sites in `bellows.py` that forced all diagnostic plans to single-step. Identified by `diagnostic-extract-total-steps-undercount-2026-05-03` (findings at `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md`). First corrective attempt (`executable-remove-is-diagnostic-step-override-2026-05-03`, halted) removed the overrides outright but broke Phase 8.1 for header-less diagnostics. The narrow-override re-fix (`executable-corrective-narrow-is-diagnostic-override-2026-05-03`, commit `9786e87`) replaced the unconditional override with `if total_steps == 0 and is_diagnostic: total_steps = 1` at both sites, preserving Phase 8.1 single-step fallback for header-less diagnostics while letting multi-step diagnostics count their headers correctly. QA verification (`bellows/knowledge/qa/corrective-narrow-override-qa-2026-05-03.md`): behavioral spot-check confirmed `extract_total_steps()` returns 3 for the exact 3-step worktree-implementation-surface plan that the BACKLOG entry cited as broken; 66 passed, 0 failed. Bellows daemon restarted post-fix. **Lesson — BACKLOG entries should be authored AFTER scanning Done/ for same-day corrective activity.** This entry was written from the symptom-observation conversation without checking whether a fix had landed; the Planner caught the staleness only by reading Done/ before authoring a follow-up diagnostic. Reference: `executable-close-2026-05-03-step-count-regression-2026-05-03`.`
>
> Verify the edit landed: `grep -n "Closed 2026-05-03.*multi-step plan step-count regression" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md` should return one match.
>
> **Phase 3 — Verify Open section no longer contains the stale entry.** `grep -c "2026-05-03.*multi-step plan step-count regression" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md` — expected exactly 1 match (the new Closed entry only). If 2 matches: Phase 1 deletion did not land cleanly; STOP and write the failure log with the grep output.
>
> **Phase 4 — Commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/BACKLOG.md && git --no-pager commit -m "docs(backlog): close 2026-05-03 step-count regression — fixed by 9786e87"`. Verify the commit landed: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --oneline`.
>
> **Phase 5 — Dev log deposit.** Write a development log to `bellows/knowledge/development/close-step-count-regression-dev-log-2026-05-03.md` documenting: (a) the BACKLOG.md edit confirmation (grep counts before/after), (b) the commit SHA from Phase 4, (c) Output Receipt with Status: Complete and the deposit list. Use the canonical Python file write pattern: `with open("bellows/knowledge/development/close-step-count-regression-dev-log-2026-05-03.md", "w") as f: f.write(content)`. Commit the dev log: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/development/close-step-count-regression-dev-log-2026-05-03.md && git --no-pager commit -m "docs: dev log for backlog step-count close"`.
>
> **Constraints:**
> - Do NOT modify any source code. This is a markdown-only plan.
> - Do NOT use heredoc syntax for any file write (banned per PLANNER_TEMPLATE Rule 5). Use canonical `with open() as f: f.write(content)` Python pattern or `Desktop Commander:edit_block` for surgical edits.
> - Do NOT touch any other BACKLOG entries. Only the 2026-05-03 step-count regression entry is in scope for removal; only the new Closed entry is in scope for addition.
> - **Failure-deposit discipline:** if any phase fails, write the failure details to `bellows/knowledge/development/close-step-count-regression-failure-log-2026-05-03.md` BEFORE stopping. The Planner cannot see your conversation text — it can only see deposited files and Bellows's gate output.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/close-step-count-regression-dev-log-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when (a) Phase 1 removed the stale Open entry, (b) Phase 2 added the Closed entry, (c) Phase 3 verified exactly one BACKLOG match for the close-entry text, (d) Phase 4 commit landed, (e) Phase 5 dev log deposited and committed. Do NOT execute Step 2 (QA verification). Do NOT move the plan to Done. Wait for CEO confirmation before any further action.

---
---

## STEP 2 — BELLOWS DOCUMENTATION (QA)

---

> Before starting, read `bellows/knowledge/development/close-step-count-regression-dev-log-2026-05-03.md` and check the Output Receipt status. If the dev log doesn't exist OR if its status is not Complete, stop and report the issue to the CEO before proceeding. Also check whether `bellows/knowledge/development/close-step-count-regression-failure-log-2026-05-03.md` exists — if it does, Step 1 hit a failure path and Step 2 should NOT proceed; report to CEO instead.
>
> **STOP REMINDER (TOP):** This is the QA verification step. Do NOT modify production code. Do NOT modify BACKLOG.md (Step 1 owns that). Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> You are the Bellows Documentation Agent (acting as QA). Skip specialist file and glossary reads.
>
> **Task: verify Step 1's BACKLOG.md edits landed correctly, run the Rule 20 mandatory self-check, write the QA report.**
>
> **Phase 1 — Deliverable verification (Rule 17).** For each listed deliverable, verify it exists with the expected change:
>
> 1. **Closed entry added.** Run: `grep -n "Closed 2026-05-03.*multi-step plan step-count regression" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/grep_closed_entry.txt`. Expected: exactly one match in the Closed section.
> 2. **Open entry removed.** Run: `grep -c "2026-05-03.*multi-step plan step-count regression" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/grep_total_count.txt`. Expected: exactly 1 (the new Closed entry only — proves the original Open entry was removed cleanly).
> 3. **Closed entry cites the fix commit.** Run: `grep -n "9786e87" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/grep_commit_cite.txt`. Expected: at least one match (the close entry references the fix commit).
> 4. **Commits landed.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -3 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/git_log.txt`. Expected: top 2 commits are the dev log commit (`docs: dev log for backlog step-count close`) and the BACKLOG edit commit (`docs(backlog): close 2026-05-03 step-count regression — fixed by 9786e87`).
> 5. **Narrow-override fix is live in bellows.py (sanity check).** Run: `grep -n "total_steps == 0 and is_diagnostic" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/grep_narrow_override_live.txt`. Expected: at least one match. This confirms the BACKLOG close is consistent with the actual code state — i.e., we're not closing a BACKLOG entry whose fix has been reverted.
>
> Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Cite the evidence file paths in the Evidence column. Any ❌ item is a Critical finding that blocks the plan from closing — do NOT proceed to subsequent phases. Attempt to fix ❌ items if possible (re-run a missed grep, re-deposit a missed file); if unfixable, stop and report to CEO.
>
> **Phase 2 — Write the QA report.** Deposit to `bellows/knowledge/qa/close-step-count-regression-qa-2026-05-03.md`. Include: (a) Phase 1 deliverable verification table with evidence file paths cited; (b) Output Receipt with Status; (c) the Rule 20 self-check stdout output appended at the end. Use canonical Python file write pattern.
>
> **Phase 3 — Mandatory Rule 20 self-check.** Run the standard self-check Python block at the end of this step. Required evidence files (must all be present in the evidence directory): `grep_closed_entry.txt`, `grep_total_count.txt`, `grep_commit_cite.txt`, `git_log.txt`, `grep_narrow_override_live.txt`. Plan slug: `executable-close-2026-05-03-step-count-regression-2026-05-03`. QA report path: `bellows/knowledge/qa/close-step-count-regression-qa-2026-05-03.md`. Include the literal stdout of the self-check in the QA report.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-close-2026-05-03-step-count-regression-2026-05-03"
> qa_report_path = "bellows/knowledge/qa/close-step-count-regression-qa-2026-05-03.md"
> evidence_dir = "bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/"
> required_evidence_files = [
>     "grep_closed_entry.txt",
>     "grep_total_count.txt",
>     "grep_commit_cite.txt",
>     "git_log.txt",
>     "grep_narrow_override_live.txt",
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
> If the self-check prints `FAILED`, the agent STOPS — does NOT update PROJECT_STATUS.md, does NOT move the plan to Done, reports the failure to the CEO and waits.
>
> **Phase 4 — Update PROJECT_STATUS.md.** Add a completed milestone entry summarizing this BACKLOG-close (one short bullet referencing the close of the 2026-05-03 step-count regression entry, citing the corrective fix commit `9786e87`). Use `Desktop Commander:edit_block` with exact anchor (the existing line above the Completed Milestones list). If the file structure makes anchoring ambiguous, append at the bottom of the Completed Milestones section.
>
> **Phase 5 — Final commit.** After QA report and PROJECT_STATUS.md edit are deposited, single final commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/close-step-count-regression-qa-2026-05-03.md knowledge/qa/evidence/close-step-count-regression-2026-05-03/ PROJECT_STATUS.md && git --no-pager commit -m "qa: verify BACKLOG step-count regression close"`.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/close-step-count-regression-qa-2026-05-03.md`
> - `bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/` (five evidence files per Rule 20 self-check)
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
