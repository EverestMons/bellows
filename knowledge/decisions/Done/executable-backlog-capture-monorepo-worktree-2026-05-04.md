# Bellows — BACKLOG capture: monorepo-worktree-at-governance-root
**Date:** 2026-05-04 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-backlog-capture-monorepo-worktree-2026-05-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Test Scope: targeted** — markdown-only edit to BACKLOG.md, no production code touched, no cross-bucket regression risk.

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-backlog-capture-monorepo-worktree-2026-05-04.md", "bellows/knowledge/decisions/in-progress-executable-backlog-capture-monorepo-worktree-2026-05-04.md")`. You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — this is a markdown-only governance edit. Read `bellows/knowledge/BACKLOG.md` to confirm the current structure. The file has a `## Open` section followed immediately by a blank line, then existing entries starting with `- 2026-05-01: test_startup_sweep_removes_done_plan_orphans...`. Use `Filesystem:edit_file` (or equivalent surgical edit tool) to insert a new entry as the FIRST item under `## Open`. Anchor on the verbatim line `- 2026-05-01: test_startup_sweep_removes_done_plan_orphans uses inline-replicated sweep logic` — replace it with the new entry text followed by a blank line followed by the original line preserved. The new entry text to insert is exactly: `- 2026-05-04: monorepo-worktree-at-governance-root structural fix — flagged as TBD-if-not-already-captured in the 2026-05-03 worktree-teardown-crash close note. Bellows is the only watched project without its own .git (it lives inside governance-root at /Users/marklehn/Desktop/GitHub/). Git operations from cwd=bellows/ walk up to governance-root's .git, so git worktree add creates a worktree of the entire governance-root monorepo (anvil, forge, bellows, etc.), not just bellows/. Three downstream consequences: (1) origin/HEAD not set on governance-root → falls back to 'main' (annoying but works); (2) cherry-pick targets governance-root's main, and any dirty state in governance-root's working tree (119 dirty files observed at 2026-05-03 diagnosis time) can conflict with the agent's commit, causing teardown failure; (3) _capture_git_diff captures all governance-root changes — already addressed by BACKLOG #4's --relative -- . fix shipped 2026-04-28. The 2026-05-03 type-fix at commit 0f2059f made teardown failure handleable (verdict request instead of crash) but did NOT prevent the failure mode itself. Until shipped, every bellows-self plan that commits is at risk of cherry-pick failure during teardown. Diagnostic: knowledge/research/worktree-teardown-bug-diagnosis-2026-05-03.md (Q2 confirms the monorepo trap, Q4 fix-shape recommendations). CEO decision 2026-05-04: ship Option (a) — detect missing .git at project_path and skip worktree creation, fall back to in-place execution. Implementation plan: executable-monorepo-worktree-fix-2026-05-04.md.` Then commit with message: `docs: backlog — capture monorepo-worktree-at-governance-root structural fix item`. **Deposits:** - `bellows/knowledge/BACKLOG.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/BACKLOG.md` and check that the new entry from Step 1 is present at the top of the `## Open` section. If not, stop and report the issue to the CEO before proceeding. You are the Bellows QA agent. Skip specialist file and glossary reads — this is a markdown-edit verification task. **FIRST — Deliverable Verification.** Read Step 1's commit via `git --no-pager log -1 --stat` and confirm the commit message matches `docs: backlog — capture monorepo-worktree-at-governance-root structural fix item`. Then `grep -n "2026-05-04: monorepo-worktree-at-governance-root" bellows/knowledge/BACKLOG.md` and confirm exactly one match in the `## Open` section. Pipe the grep output to `bellows/knowledge/qa/evidence/executable-backlog-capture-monorepo-worktree-2026-05-04/grep_backlog_entry.txt`. Pipe the git log output to `bellows/knowledge/qa/evidence/executable-backlog-capture-monorepo-worktree-2026-05-04/git_log_commit.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` with rows for (1) BACKLOG entry inserted at top of Open section, (2) commit landed with correct message. Deposit QA report at `bellows/knowledge/qa/backlog-capture-monorepo-worktree-qa-2026-05-04.md` with the verification table and Output Receipt. Run the Rule 20 self-check Python block at the end and include literal stdout in the QA report. If self-check FAILED, STOP — report to CEO. If PASSED, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Do NOT update PROJECT_STATUS.md (this BACKLOG capture is a precursor to the actual fix plan; status update happens at the fix plan's QA). Do NOT move the plan to Done — Planner performs the move after Rule 22 verification.
>
> **Deposits:**
> - `bellows/knowledge/qa/backlog-capture-monorepo-worktree-qa-2026-05-04.md`
> - `bellows/knowledge/qa/evidence/executable-backlog-capture-monorepo-worktree-2026-05-04/grep_backlog_entry.txt`
> - `bellows/knowledge/qa/evidence/executable-backlog-capture-monorepo-worktree-2026-05-04/git_log_commit.txt`
>
> **Rule 20 self-check (run at end of QA step, include literal stdout in QA report):**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-backlog-capture-monorepo-worktree-2026-05-04"
> qa_report_path = "bellows/knowledge/qa/backlog-capture-monorepo-worktree-qa-2026-05-04.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_backlog_entry.txt", "git_log_commit.txt"]
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
