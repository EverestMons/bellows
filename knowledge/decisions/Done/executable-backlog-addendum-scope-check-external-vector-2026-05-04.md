# Bellows — Append External-Vector Addendum to BACKLOG #2 (Scope_Check Diff-Collision)
**Date:** 2026-05-04 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-backlog-addendum-scope-check-external-vector-2026-05-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Test Scope: targeted — markdown-only edit to BACKLOG.md, no production code touched, no test-exercised code touched. Per Rule 21, no full-suite required. No tests run at all.**

**Context:** the BACKLOG #2 entry (`2026-04-30: parallel-plan scope_check diff-collision`) frames the scope_check noise problem narrowly — as a parallel-sibling collision. The 2026-05-04 plan `executable-close-monorepo-worktree-backlog-2026-05-04` Step 1 reproduced the same structural failure on a DIFFERENT vector: 23 stale verdict-request files were moved into `bellows/verdicts/pending/archived/` by an external process (CEO cleanup `mv`) during the agent's execution window. The step's `git diff --stat` correctly captured those moves; `scope_check` correctly flagged them; but the agent didn't touch any of them. Same root cause class as BACKLOG #2 — working-tree-shared approaches (git diff or file-checksum snapshot) cannot isolate per-step changes from concurrent activity in the same project subtree — but on the **external/CEO** vector rather than the **parallel-sibling** vector. The existing fix-shape candidates ((d) per-plan worktree, (b) commit-scoping, (e) process-filtered file-touch tracking) all address both vectors equivalently; only the working-tree-shared options (a, c) fail in different ways across the two. This plan appends an addendum subsection to the existing entry to broaden its scope without changing the fix-shape list, and updates the entry's leading tag to reflect both vectors.

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-backlog-addendum-scope-check-external-vector-2026-05-04.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-backlog-addendum-scope-check-external-vector-2026-05-04.md")`. You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — markdown-only BACKLOG hygiene task. **Goal:** append an "External-vector reproduction 2026-05-04" addendum to the existing BACKLOG #2 entry that begins `- 2026-05-30: parallel-plan scope_check diff-collision` (note: the entry is dated 2026-04-30, the leading tag may say `2026-04-30:`), and update the entry's leading tag to reflect that the failure class spans both parallel-sibling and external/CEO vectors. **Edit 1 (retitle the leading tag):** in `bellows/knowledge/BACKLOG.md`, find the line that begins `- 2026-04-30: parallel-plan scope_check diff-collision (REOPENED 2026-05-01 after failed close attempt) — when two plans dispatch in parallel via the` and use `Desktop Commander:edit_block` with `old_string` = `- 2026-04-30: parallel-plan scope_check diff-collision (REOPENED 2026-05-01 after failed close attempt) — when two plans dispatch in parallel via the` and `new_string` = `- 2026-04-30: scope_check diff-collision from concurrent activity (REOPENED 2026-05-01 after failed close attempt; external-vector reproduction added 2026-05-04) — originally surfaced as a parallel-sibling collision: when two plans dispatch in parallel via the`. This retitle preserves the leading date/tag (`2026-04-30:`) and the original framing as the first sentence, while broadening the headline to reflect that the failure class is not parallel-only. **Edit 2 (append addendum):** find the line that ends `References: original BACKLOG entry observation 2026-04-30; diagnostic + failed-close history 2026-05-01.` and use `Desktop Commander:edit_block` with `old_string` = `References: original BACKLOG entry observation 2026-04-30; diagnostic + failed-close history 2026-05-01.` and `new_string` = the original `References:` text followed by the addendum below as a continuation paragraph (preserving the entry as a single bullet — no extra newlines, append within the same bullet). The addendum text:

```
 **External-vector reproduction 2026-05-04:** the same structural failure surfaced on a non-parallel-sibling vector during `executable-close-monorepo-worktree-backlog-2026-05-04` Step 1. The step was a markdown-only BACKLOG edit (no parallel siblings dispatched). During the ~2-minute execution window (16:13:58 → 16:15:35), an external process — a CEO cleanup `mv` operation — moved 23 stale verdict-request files from `bellows/verdicts/pending/` into `bellows/verdicts/pending/archived/`. Bellows's `_capture_git_diff()` correctly captured those moves as files-changed during the step (the `--relative -- .` monorepo fix scoped them to the bellows/ subtree, which is correct — they ARE under bellows/), and `scope_check` correctly flagged them as out-of-scope (they don't appear in the plan text). The agent did not touch any of those 23 files. Planner Rule 22 verification on the actual deposits (BACKLOG.md edits, dev log) passed cleanly; the gate trip was pure environmental noise. **Same structural class as the parallel-sibling vector:** working-tree-shared file-state observation cannot isolate per-step changes from concurrent activity in the same project subtree, regardless of whether the concurrent activity comes from a parallel sibling agent or from an external process (CEO `mv`, another Claude session, a cron job, a cleanup script). **Fix-shape implications unchanged:** the existing candidates (a, b, c, d, e in the original entry) all address both vectors equivalently — (a) timestamp-bound git range partially helps both, (c) file-checksum snapshot fails on both for the same reason, (d) per-plan git worktree fully isolates both, (b) commit-scoping fully isolates both if convention is adopted, (e) process-filtered file-touch tracking fully isolates both. Wider-blast-radius framing strengthens the case for (d) or (e) over the cheaper-but-narrower options because external-vector contamination is harder to predict than parallel-sibling contamination — operators have no obvious reason to avoid `mv` during a step window the way they might avoid dispatching parallel-N- groups for committing work. **Practical implication update:** the existing "yellow-flag for parallel-N- with committing DEV" guidance is unchanged but incomplete — operators should also avoid running cleanup commands (verdict archival, log rotation, file moves) inside any project subtree while a plan is dispatched against that project. Until fixed at the gate level, the Planner-side workaround for both vectors is the same: when scope_check trips with files the agent demonstrably did not touch, run Rule 22 on the actual deposits and override if the work is correct. Reference: `executable-close-monorepo-worktree-backlog-2026-05-04` Step 1 verdict request at `bellows/verdicts/pending/archived/` (cleaned by next CEO sweep) and the Planner conversation override that depositd a continue verdict authorizing Step 2 dispatch.
```

> **Verification before commit:** re-read the modified entry in `bellows/knowledge/BACKLOG.md`. Confirm: (a) the leading tag now reads `- 2026-04-30: scope_check diff-collision from concurrent activity (REOPENED 2026-05-01 after failed close attempt; external-vector reproduction added 2026-05-04) — originally surfaced as a parallel-sibling collision: when two plans dispatch in parallel via the`; (b) the entry still ends with the addendum's final sentence (`...the Planner conversation override that depositd a continue verdict authorizing Step 2 dispatch.`); (c) the entry remains a single bullet (no spurious newlines that would split it into two BACKLOG items); (d) all existing fix-shape options (a, b, c, d, e) and the existing `Refined fix-shape options after 2026-05-01 analysis:` paragraph remain unchanged in content. **Commit:** one commit from `/Users/marklehn/Desktop/GitHub/bellows/`, message `docs: backlog — broaden scope_check diff-collision entry with external-vector reproduction`. Deposit dev log at `bellows/knowledge/documentation/backlog-addendum-scope-check-external-vector-dev-log-2026-05-04.md` with the Output Receipt — what was changed, decisions made, flags. After the dev log and before commit, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/BACKLOG.md`
> - `bellows/knowledge/documentation/backlog-addendum-scope-check-external-vector-dev-log-2026-05-04.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> **Before starting, read `bellows/knowledge/documentation/backlog-addendum-scope-check-external-vector-dev-log-2026-05-04.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** You are the Bellows QA. Skip specialist file and glossary reads — markdown verification task. **Deliverable verification (Rule 17) FIRST.** Read the prior step's Output Receipt and verify each listed deliverable. Run these 4 checks from `/Users/marklehn/Desktop/GitHub/`, piping each output to `bellows/knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/<filename>.txt`: **Check 1 (leading tag retitled):** `grep -c "^- 2026-04-30: scope_check diff-collision from concurrent activity" bellows/knowledge/BACKLOG.md` — expected count `1`. Pipe to `grep_retitle.txt`. **Check 2 (addendum subsection landed):** `grep -c "External-vector reproduction 2026-05-04:" bellows/knowledge/BACKLOG.md` — expected count `1`. Pipe to `grep_addendum.txt`. **Check 3 (entry still single bullet — fix-shape paragraph still inside same bullet):** `grep -n "Refined fix-shape options after 2026-05-01 analysis:" bellows/knowledge/BACKLOG.md` — expected: exactly 1 match, on the same line as the original `2026-04-30:` entry (not on its own bullet). Pipe to `grep_fixshape_inline.txt`. **Check 4 (commit landed):** `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -3 -- knowledge/BACKLOG.md` — expected: top entry has subject `docs: backlog — broaden scope_check diff-collision entry with external-vector reproduction`. Pipe to `git_log_backlog.txt`. **Test regression: NOT REQUIRED — markdown-only edits, no production code touched.** **Build the QA report** at `bellows/knowledge/qa/backlog-addendum-scope-check-external-vector-qa-2026-05-04.md` with a verification table `| # | Deliverable | Expected | Actual | Status (✅/❌) | Evidence |` covering all 4 checks, citing the evidence file paths in the Evidence column. **PROJECT_STATUS.md update:** open `bellows/PROJECT_STATUS.md`, find the most recent `## Completed Milestones` section, and append a new milestone entry: `### 2026-05-04 — BACKLOG hygiene: scope_check diff-collision entry broadened (external-vector reproduction)` with body `BACKLOG entry for scope_check diff-collision broadened to capture the external/CEO vector reproduced today during executable-close-monorepo-worktree-backlog-2026-05-04 Step 1. Same structural class as parallel-sibling collision — working-tree-shared file-state observation cannot isolate per-step changes from concurrent activity in the same project subtree. Fix-shape candidates unchanged. References: executable-backlog-addendum-scope-check-external-vector-2026-05-04.md.` Use `Desktop Commander:edit_block` with the existing newest `### 2026-05-04 — BACKLOG hygiene: monorepo-worktree-at-governance-root closed` milestone header (added by the prior plan) as the anchor — read PROJECT_STATUS.md first to get the verbatim anchor before editing, and insert the new milestone IMMEDIATELY ABOVE it (newer-on-top convention). **Run the mandatory Rule 20 self-check Python block AT THE END of the QA report**, including its literal stdout:

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

> If the self-check prints `PASSED`, proceed to the final commit. If `FAILED`, stop and report. **Final commit:** one commit from `/Users/marklehn/Desktop/GitHub/bellows/`, message `docs: qa — backlog addendum scope_check external-vector hygiene`. After the QA report and PROJECT_STATUS update, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **DO NOT move this plan to Done.** Per the disable-auto-close model, the Planner performs the terminal Done/ move after Rule 22 verification passes. Per Rule 23 ordering, the agent's last operation is the final commit; the Planner's Rule 22 verification follows.
>
> **Deposits:**
> - `bellows/knowledge/qa/backlog-addendum-scope-check-external-vector-qa-2026-05-04.md`
> - `bellows/knowledge/qa/evidence/executable-backlog-addendum-scope-check-external-vector-2026-05-04/`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
