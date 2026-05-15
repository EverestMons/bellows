# Bellows — Revert File-Checksum Snapshot Fix + Re-Open BACKLOG Entry
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (Documentation) → Step 3 (QA)

## How to Run This Plan

Bellows will auto-claim. Step 1 reverts commit `9b20d94` (the failed file-checksum snapshot fix). Step 2 edits BACKLOG.md to re-open the 2026-04-30 entry with annotation explaining the failed close. Step 3 (QA) verifies the revert landed cleanly and the BACKLOG annotation is correct.

**Bootstrap (manual fallback only):**
```
Read the plan at bellows/knowledge/decisions/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md")`. **You are the Bellows Developer.** Skip specialist file and glossary reads — this is a mechanical revert task. **Background:** commit `9b20d94` ("fix(gates): file-checksum snapshot for parallel-plan scope_check immunity") was shipped earlier today as a fix for BACKLOG entry "2026-04-30: parallel-plan scope_check diff-collision." The Planner's Rule 22 verification of the QA report identified that the fix is structurally insufficient: file-checksum snapshots of the shared working tree still capture sibling-induced file content changes during overlapping execution windows. The BACKLOG bug involved sibling agents actively editing then committing files (the modify-then-commit pattern); `_snapshot_file_state` does not isolate per-thread changes for this case. The plan must be reverted. **Task:** (1) From the `/Users/marklehn/Desktop/GitHub/bellows` directory, run `git --no-pager log --oneline -5` to confirm commit `9b20d94` is in recent history. Pipe output to a temp variable for the dev log. (2) Run `git revert --no-edit 9b20d94`. This produces a new commit (let's call it `<REVERT_SHA>`) that undoes the changes from `9b20d94`. (3) Verify the revert by running `git --no-pager log --oneline -3` (expect to see the revert commit, then `9b20d94`, then the prior commit). Pipe output for the dev log. (4) Confirm the source-of-truth state by checking: (a) `grep -c "_snapshot_file_state" bellows/bellows.py` — expect 0 (function should be gone after revert); (b) `grep -c "_capture_git_diff" bellows/bellows.py` — expect ≥3 (function should be back, called from run_plan); (c) `ls bellows/tests/test_snapshot_file_state.py` — expect "No such file or directory" (test file should be gone after revert). (5) Run `pytest bellows/tests/ -v 2>&1 | tail -20` to confirm the test suite still works post-revert. Expect the pre-existing `test_run_step_timeout` failure but no new failures from the revert. **Do NOT push the revert commit yet** — Step 3 (QA) will verify the revert landed correctly before committing/pushing is final. (Actually — the revert commit was already created locally by `git revert`. It IS on the local branch. Don't make a second commit; just don't `git push` from this step. QA in Step 3 confirms; Planner authorizes terminal close.) **Write the dev log** to `bellows/knowledge/development/revert-snapshot-fix-2026-05-01.md` with: revert commit SHA, the verification grep results, the pytest tail output, and an Output Receipt. Use canonical Python file write pattern. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/revert-snapshot-fix-2026-05-01.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows Documentation Analyst

---

> **Before starting, read `bellows/knowledge/development/revert-snapshot-fix-2026-05-01.md` and confirm the Output Receipt status is Complete. If not, stop and report to CEO before proceeding.** **You are the Bellows Documentation Analyst.** Skip specialist file and glossary reads — this is a markdown-only BACKLOG hygiene edit. Read `bellows/knowledge/BACKLOG.md` in full to understand the current Open and Closed sections. Make ONE edit: replace the existing top-of-Open entry (the line beginning `- 2026-04-30: parallel-plan scope_check diff-collision`) with an UPDATED version that reflects today's failed close attempt. Use the Filesystem MCP write_file tool to read full file → produce new content with the substitution → write full file. **The replacement bullet is:** `- 2026-04-30: parallel-plan scope_check diff-collision (REOPENED 2026-05-01 after failed close attempt) — when two plans dispatch in parallel via the \`parallel-N-\` group prefix, they share a working tree, and per-step file-state observation (whether via \`git diff --stat\` or file-checksum snapshot) does not isolate each plan's changes from concurrent sibling commits or edits. Result: spurious scope_check failures on whichever parallel plan does not commit first. Originally reproduced 2026-04-30 on \`parallel-1-executable-deposit-exists-directory-paths-2026-04-30\` and \`executable-backlog-hygiene-sweep-2026-04-30\` — both tripped scope_check listing files (\`bellows.py\`, \`verdict.py\`, \`tests/test_verdict.py\`) actually committed by sibling \`parallel-1-executable-ledger-pause-reason-code-2026-04-30\`. **Failed close attempt 2026-05-01:** Diagnostic at \`knowledge/research/parallel-plan-scope-check-collision-diagnosis-2026-05-01.md\` recommended fix shape (c1) file-checksum snapshot of tracked files at step start/end. Implemented as commit \`9b20d94\` (function \`_snapshot_file_state\` + \`_diff_file_state\` replacing \`_capture_git_diff\` + \`_parse_diff_stat\`). All gates passed, all tests passed (6 new + 183/184 baseline). Planner Rule 22 verification on the QA report identified the structural insufficiency: file-checksum snapshots read the SAME shared working tree as \`git diff --stat\`. If sibling B modifies file X on disk during plan A's execution window, X's checksum changes, and X appears in plan A's post-snapshot — same contamination vector as the original bug. The DEV agent's regression test (\`test_diff_immune_to_sibling_changes_in_unrelated_files\`) acknowledged in its own assertions that sibling-modified files DO appear in the diff. The fix only addresses the narrow case of sibling committing a previously-dirty file (no further edit) — irrelevant to the observed BACKLOG bug, where siblings actively edited files mid-step. Reverted via plan \`executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md\`. **Refined fix-shape options after 2026-05-01 analysis:** (a) timestamp-bound git range — partial isolation, doesn't handle uncommitted changes, ~15 LOC; (b) plan-slug commit-message scoping — full isolation if convention adopted, currently 0% slug-presence rate so blocked on convention adoption + agent compliance, ~20 LOC; (c) file-checksum snapshot — REJECTED 2026-05-01, doesn't isolate per-thread changes; (d) per-plan git worktree — full isolation at agent level, ~50-80 LOC, requires merging worktree commits back, may confuse agents expecting specific absolute paths; (e) per-process file-touch tracking via \`inotify\`/\`fsevents\` filtered by claude-p PID — full isolation, complex platform-specific implementation. Working-tree-shared approaches (a, c) cannot fully solve. Real candidates are (d) worktree, (b) commit scoping with convention adoption, or (e) process-filtered file-touch tracking. Practical implication: the \`parallel-N-\` pattern remains unsafe for plans that commit during DEV — only safe for read-only diagnostics or plans where commit happens after all parallel siblings finish. Until fixed, Planner should treat \`parallel-N-\` as a yellow-flag pattern and prefer sequential plans for committing work. References: original BACKLOG entry observation 2026-04-30; diagnostic + failed-close history 2026-05-01.` **Commit with message:** `docs(backlog): re-open parallel-plan scope_check collision entry after failed close`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/BACKLOG.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — Bellows QA

---

> **Before starting, read both prior step deposits: (1) `bellows/knowledge/development/revert-snapshot-fix-2026-05-01.md` and (2) `bellows/knowledge/BACKLOG.md`. Verify Step 1's Output Receipt is Complete and Step 2's BACKLOG edit landed (the `(REOPENED 2026-05-01 after failed close attempt)` annotation should appear in the top-of-Open entry). If either is missing or malformed, stop and report to CEO.** **You are the Bellows QA agent.** Skip specialist file and glossary reads. Test scope: targeted (revert is a localized change; full suite was already validated by Step 1's pytest run). **FIRST — Deliverable Verification.** Read the prior DEV step's Output Receipt. Verify each deliverable on disk: (1) `git --no-pager log --oneline -5` from `/Users/marklehn/Desktop/GitHub/bellows` — expect to see the revert commit at the top, followed by `9b20d94`, then prior commits. Pipe output to `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/git_log_after_revert.txt`. (2) `grep -c "_snapshot_file_state" bellows/bellows.py` — expect 0. Pipe full grep output (use `grep -n` for line context, even if 0 matches the file existence is what we're confirming) to `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/grep_snapshot_function_gone.txt`. (3) `grep -c "_capture_git_diff" bellows/bellows.py` — expect ≥3 (function back, called from run_plan). Pipe `grep -n` output to `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/grep_capture_function_restored.txt`. (4) `ls bellows/tests/test_snapshot_file_state.py 2>&1` — expect "No such file or directory" message. Pipe to `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/ls_test_file_gone.txt`. (5) `grep -n "REOPENED 2026-05-01 after failed close attempt" bellows/knowledge/BACKLOG.md` — expect exactly one match in the Open section. Pipe to `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/grep_backlog_reopen_annotation.txt`. (6) `pytest bellows/tests/ 2>&1 | tail -10` — expect 183 passed, 1 failed (`test_run_step_timeout` pre-existing). The total test count should drop from 184 (post-snapshot-fix) back to 183 + 1 failure baseline (pre-snapshot-fix). Pipe output to `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/pytest_targeted.txt`. **Produce verification table:** `| Deliverable | Expected | Status (✅/❌) | Evidence |` with rows for: (a) revert commit landed in git log, (b) `_snapshot_file_state` removed from bellows.py, (c) `_capture_git_diff` restored in bellows.py, (d) test_snapshot_file_state.py removed, (e) BACKLOG REOPENED annotation present in Open section, (f) test suite returns to pre-snapshot-fix baseline. **Deposit QA report** at `bellows/knowledge/qa/qa-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md` with the verification table and the literal stdout of the Rule 20 self-check below. **Update PROJECT_STATUS.md** with milestone entry: "Reverted commit `9b20d94` (file-checksum snapshot fix) after Rule 22 verification identified structural insufficiency. Re-opened BACKLOG entry `2026-04-30: parallel-plan scope_check diff-collision` with annotation capturing the failed-close analysis. Refined fix-shape candidates: (d) per-plan worktree, (b) plan-slug commit-message scoping with convention adoption, (e) process-filtered file-touch tracking. Working-tree-shared approaches structurally cannot solve the bug." Commit PROJECT_STATUS.md with descriptive message. **Final commit and STOP — do NOT move this plan to Done. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.** **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. The feedback append + commit are the absolute last operations. **Run the Rule 20 self-check at the very end and include its literal stdout in the QA report:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/qa-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "git_log_after_revert.txt",
>     "grep_snapshot_function_gone.txt",
>     "grep_capture_function_restored.txt",
>     "ls_test_file_gone.txt",
>     "grep_backlog_reopen_annotation.txt",
>     "pytest_targeted.txt",
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
> - `bellows/knowledge/qa/qa-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/` (6 files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
