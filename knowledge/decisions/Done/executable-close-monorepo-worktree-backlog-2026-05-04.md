# Bellows — Close Monorepo-Worktree BACKLOG Entry (Hygiene)
**Date:** 2026-05-04 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-close-monorepo-worktree-backlog-2026-05-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Test Scope: targeted — markdown-only edits to BACKLOG.md and PROJECT_STATUS.md, no production code touched, no test-exercised code touched. Per Rule 21, no full-suite required. No test commands run at all (no Python code paths exercised).**

**Context:** the BACKLOG entry for the monorepo-worktree fix was authored on 2026-05-04 capturing the open work, but the fix itself shipped same-day via `executable-monorepo-worktree-fix-2026-05-04.md` and was validated via `diagnostic-monorepo-worktree-fix-canary-2026-05-04.md` (both in `Done/`). The dev log at `bellows/knowledge/development/monorepo-worktree-fix-dev-log-2026-05-04.md` documents the implementation choices: `.git` detection at top of `_create_worktree` with early return of `project_path`, sentinel signal via `wt_path == project_path` equality in `_teardown_worktree`, 3 unit tests added. The 2026-05-03 type-fix at commit `0f2059f` (lines 340/405/433 of `bellows.py`) remains intact as the safety net for cherry-pick failures in projects with their own `.git`. This plan does the BACKLOG hygiene close so the open list reflects reality.

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-close-monorepo-worktree-backlog-2026-05-04.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-close-monorepo-worktree-backlog-2026-05-04.md")`. You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — this is a markdown-only BACKLOG hygiene task with no domain interpretation required. **Goal:** move the `2026-05-04: monorepo-worktree-at-governance-root structural fix` entry from the `## Open` section of `bellows/knowledge/BACKLOG.md` to the `## Closed` section, adding a close note that references the implementation plan, the canary, and the key implementation choices from the dev log. **Edit 1 (remove from Open):** in `bellows/knowledge/BACKLOG.md`, delete the entire entry that begins `- 2026-05-04: monorepo-worktree-at-governance-root structural fix — flagged as TBD-if-not-already-captured` and ends with `Implementation plan: executable-monorepo-worktree-fix-2026-05-04.md.` — also delete the trailing blank line that separates this entry from the next `- 2026-05-01: test_startup_sweep_removes_done_plan_orphans` entry, so the Open section closes cleanly with no double-blank-line artifact. Use `Desktop Commander:edit_block` with the verbatim entry text plus its trailing blank line as `old_string` and empty string as `new_string`. **Edit 2 (add to Closed, top of section):** in the same file, immediately after the `## Closed` header line and its blank line, insert this new close entry as the first item in the Closed section (the Closed section is reverse-chronological, newest at top), preserving the existing first entry that begins `- **Closed 2026-05-03:** worktree teardown crash`. The new entry text:

```
- **Closed 2026-05-04:** `2026-05-04: monorepo-worktree-at-governance-root structural fix`. Shipped via `executable-monorepo-worktree-fix-2026-05-04.md` (Option A: detect-and-skip). Implementation: `_create_worktree` checks `os.path.exists(os.path.join(project_path, ".git"))` at the top of the function — when False, logs `⚠ {project_name} has no project-local .git — running in-place without worktree isolation` and returns `project_path` directly, skipping all worktree creation. `_teardown_worktree` becomes a no-op via sentinel comparison `if wt_path == project_path: return` (no `git worktree remove`, no cherry-pick). Bellows-self plans now run in-place against the live working tree without isolation; all 7 projects with their own `.git` (invoice-pulse, BrewBuddy, study, ai-career-digest, freight-kb, forge, anvil) are unaffected. 3 new unit tests added (`test_create_worktree_returns_project_path_when_no_git`, `test_teardown_worktree_noop_when_wt_equals_project`, `test_create_worktree_proceeds_when_git_exists`); 90/90 targeted tests passing. The 2026-05-03 type-fix at commit `0f2059f` (string-vs-dict in `gate_result["failures"]`) remains intact as the safety net for cherry-pick failures in `.git`-having projects. Validated via `diagnostic-monorepo-worktree-fix-canary-2026-05-04.md`. Dev log: `bellows/knowledge/development/monorepo-worktree-fix-dev-log-2026-05-04.md`. **Tradeoff acknowledged:** bellows-self plans no longer get worktree isolation — they execute in-place against governance-root's working tree, so dirty state in unrelated projects can affect bellows-self execution. CEO accepted this tradeoff at planning time as the fastest unblock; option (b) from the diagnostic Q4 (worktree-at-repo-root with subdirectory cwd) preserves isolation but was deferred. Reference: `executable-monorepo-worktree-fix-2026-05-04.md`, `diagnostic-monorepo-worktree-fix-canary-2026-05-04.md`.

```

> Use `Desktop Commander:edit_block` with `old_string` = the verbatim `## Closed\n` header line followed by the existing `\n- **Closed 2026-05-03:** worktree teardown crash.` line opening, and `new_string` = the same `## Closed\n` header followed by the new entry above (with its trailing blank line already included) followed by the original `- **Closed 2026-05-03:** worktree teardown crash.` opening. This anchored insertion preserves all existing Closed entries below. **Verification before commit:** re-read `bellows/knowledge/BACKLOG.md` and confirm: (a) the `2026-05-04: monorepo-worktree-at-governance-root` line no longer appears anywhere under `## Open`, (b) the new `**Closed 2026-05-04:** \`2026-05-04: monorepo-worktree-at-governance-root structural fix\`` entry appears as the first item under `## Closed`, (c) the existing `**Closed 2026-05-03:** worktree teardown crash` entry remains immediately after the new entry. **Commit:** one commit from `/Users/marklehn/Desktop/GitHub/bellows/`, message `docs: backlog — close 2026-05-04 monorepo-worktree-at-governance-root entry`. Deposit dev log at `bellows/knowledge/documentation/close-monorepo-worktree-backlog-dev-log-2026-05-04.md` with the Output Receipt — what was changed, decisions made, flags. After the dev log and before commit, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/BACKLOG.md`
> - `bellows/knowledge/documentation/close-monorepo-worktree-backlog-dev-log-2026-05-04.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> **Before starting, read `bellows/knowledge/documentation/close-monorepo-worktree-backlog-dev-log-2026-05-04.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** You are the Bellows QA. Skip specialist file and glossary reads — this is a markdown verification task. **Deliverable verification (Rule 17) FIRST.** Read the prior step's Output Receipt "Files Created or Modified" list and verify every listed deliverable. Run these 4 checks from `/Users/marklehn/Desktop/GitHub/`, piping each output to `bellows/knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/<filename>.txt`: **Check 1 (entry removed from Open):** `sed -n '/^## Open/,/^## Closed/p' bellows/knowledge/BACKLOG.md | grep -c "2026-05-04: monorepo-worktree-at-governance-root structural fix"` — expected count `0`. Pipe to `grep_open_section.txt`. **Check 2 (entry added to Closed):** `sed -n '/^## Closed/,$p' bellows/knowledge/BACKLOG.md | grep -c "Closed 2026-05-04:.*2026-05-04: monorepo-worktree-at-governance-root structural fix"` — expected count `1`. Pipe to `grep_closed_section.txt`. **Check 3 (Closed section ordering preserved):** `grep -n "^- \*\*Closed " bellows/knowledge/BACKLOG.md | head -3` — expected: line 1 is the new `Closed 2026-05-04: \`2026-05-04: monorepo-worktree-at-governance-root structural fix\``, line 2 is `Closed 2026-05-03: worktree teardown crash`, line 3 is `Closed 2026-05-03: BACKLOG \`2026-05-03: multi-step plan step-count regression\``. Pipe to `grep_closed_ordering.txt`. **Check 4 (commit landed):** `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -5 -- knowledge/BACKLOG.md` — expected: top entry has subject `docs: backlog — close 2026-05-04 monorepo-worktree-at-governance-root entry`. Pipe to `git_log_backlog.txt`. **Test regression: NOT REQUIRED — markdown-only edits, no production code touched, no test-exercised code touched.** **Build the QA report** at `bellows/knowledge/qa/close-monorepo-worktree-backlog-qa-2026-05-04.md` with a verification table `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering all 4 checks, citing the evidence file paths in the Evidence column. **PROJECT_STATUS.md update:** open `bellows/PROJECT_STATUS.md`, find the most recent `## Completed Milestones` section (or equivalent), and append a new milestone entry: `### 2026-05-04 — BACKLOG hygiene: monorepo-worktree-at-governance-root closed` with body `BACKLOG entry for the monorepo-worktree fix moved from Open to Closed. Fix shipped earlier 2026-05-04 via executable-monorepo-worktree-fix-2026-05-04 (Option A: detect-and-skip in _create_worktree); canary validated. Entry was stale at time of session-open scan. References: executable-close-monorepo-worktree-backlog-2026-05-04.md.` Use `Desktop Commander:edit_block` with the existing `## Completed Milestones` header (or its equivalent newest entry) as the anchor — read PROJECT_STATUS.md first to get the verbatim anchor before editing. **Run the mandatory Rule 20 self-check Python block AT THE END of the QA report**, including its literal stdout:

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
            # Allowed to contain only "0" (count expected to be 0)
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

> If the self-check prints `PASSED — SELF-CHECK PASSED`, proceed to the final commit. If `FAILED`, stop and report. **Final commit:** one commit from `/Users/marklehn/Desktop/GitHub/bellows/`, message `docs: qa — close monorepo-worktree-backlog hygiene plan`. After the QA report and PROJECT_STATUS update, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **DO NOT move this plan to Done.** Per the disable-auto-close model, the Planner performs the terminal Done/ move after Rule 22 verification passes. Per Rule 23 ordering, the agent's last operation is the final commit; the Planner's Rule 22 verification follows.
>
> **Deposits:**
> - `bellows/knowledge/qa/close-monorepo-worktree-backlog-qa-2026-05-04.md`
> - `bellows/knowledge/qa/evidence/executable-close-monorepo-worktree-backlog-2026-05-04/` (4 files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
