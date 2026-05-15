# Bellows — BACKLOG Hygiene Sweep
**Date:** 2026-04-30 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA)
**Priority:** 5

## Context

Three BACKLOG/PROJECT_STATUS hygiene closes derived from independent reverification of carried items against live code:

1. **BACKLOG `2026-04-23: no_permission_denials gate trips on successful diagnostics`** — superseded by BACKLOG #2 close 2026-04-28 (`READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}` exempts read-class tools entirely). Verified live in `gates.py::_gate_no_permission_denials`. The 2026-04-23 entry described Grep/Glob denials specifically, which is exactly what the 2026-04-28 fix exempts. Move to Closed with cross-reference.

2. **BACKLOG `2026-04-18: step state lost across re-claim`** — superseded by BACKLOG #6 Phase 3b (DB-based step state recovery, shipped 2026-04-28: `plan_slug` column + `_get_last_completed_step` helper) and Phase 3c (plan-hash drift warning, shipped 2026-04-30). The 2026-04-18 entry's recommended fix option (a) — "persist step state in `bellows.db` keyed by plan slug" — was implemented exactly as described. Move to Closed with cross-reference.

3. **PROJECT_STATUS `Pending: Phase 8 QA paperwork catchup`** — Phase 8 (verdict layer redesign, shipped 2026-04-16) had its QA Step 2 abort on dirty working tree. Code shipped fine; subsequent dependent work (Phase 8.1, resume-from-correct-step, agent self-request, claim-at-entry, parallel defer, scope_check fix, cross-project verdict scoping, all closed cleanly) has functionally verified Phase 8 over the past two weeks. CEO decision (this session): close as functionally-verified-by-downstream-use rather than write retroactive QA paperwork. Drop from Pending.

Test Scope: targeted — no code changes, no test additions, no test runs needed beyond verifying the markdown edits landed. Per Position A (2026-04-20), markdown-only plans still get a QA step but with lightweight verification: grep, git log, Rule 20 self-check.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-backlog-hygiene-sweep-2026-04-30.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-backlog-hygiene-sweep-2026-04-30.md", "bellows/knowledge/decisions/in-progress-executable-backlog-hygiene-sweep-2026-04-30.md")`. **Skip specialist file and glossary reads — this is mechanical markdown editing across three documented items.** All commands run from `/Users/marklehn/Desktop/GitHub/bellows/`.
>
> **Edit 1 — BACKLOG.md: close 2026-04-23 no_permission_denials entry.** Use `Filesystem:edit_file` to find the verbatim line beginning `- 2026-04-23: \`no_permission_denials\` gate trips on successful diagnostics` and replace its leading `- ` with `- ~~`. Then find the trailing portion of that same long entry — it ends with the sentence `Fix (a) or (b) from above would eliminate the noise; (c) would too but is harder to scope.` — and append immediately after that sentence: ` **[CLOSED 2026-04-30 — superseded by BACKLOG #2 fix shipped 2026-04-28; READ_CLASS_TOOLS = {"Grep", "Glob", "Read"} in gates.py exempts read-class denials entirely. Verified live in code.]**~~`. (The double-`~~` closes the strikethrough started on the leading `- ~~` token.)
>
> **Edit 2 — BACKLOG.md: close 2026-04-18 step-state-lost-across-re-claim entry.** Use `Filesystem:edit_file` to find the verbatim line beginning `- 2026-04-18: step state lost across re-claim` and replace its leading `- ` with `- ~~`. Then find the trailing portion of that entry — it ends with the sentence `Blocks accurate PLANNER_TEMPLATE documentation of Bellows integration — the "correct" resume protocol cannot be documented until this is resolved.` — and append immediately after: ` **[CLOSED 2026-04-30 — superseded by Phase 3b (DB-based step state recovery, plan_slug column + _get_last_completed_step helper, shipped 2026-04-28) and Phase 3c (plan-hash drift warning, shipped 2026-04-30). The original 2026-04-18 entry's fix option (a) was implemented as recommended.]**~~`.
>
> **Edit 3 — BACKLOG.md: append both new Closed entries.** Use `Filesystem:edit_file` to append two new entries to the `## Closed` section, immediately after the existing `**Closed 2026-04-30:**` entry (the verdict mechanization closure). The two new Closed entries verbatim:
> ```
> - **Closed 2026-04-30 (hygiene):** BACKLOG `2026-04-23: no_permission_denials gate trips on successful diagnostics`. Superseded by BACKLOG #2 close (2026-04-28) which added `READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}` to gates.py and modified `_gate_no_permission_denials` to filter read-class denials. The 2026-04-23 entry described Grep/Glob denials on cross-project paths — exactly the failure class the 2026-04-28 fix targeted and resolved. Verified live in `bellows/gates.py` (READ_CLASS_TOOLS constant + filter loop in _gate_no_permission_denials). No further action needed.
> - **Closed 2026-04-30 (hygiene):** BACKLOG `2026-04-18: step state lost across re-claim`. Superseded by BACKLOG #6 Phase 3b (DB-based step state recovery, shipped 2026-04-28: `plan_slug` column added to `runs` table; `_get_last_completed_step(db_path, plan_slug)` helper added; `run_plan()` now queries DB for last completed step when `resume_step is None` and shadow cache exists) and Phase 3c (plan-hash drift warning, shipped 2026-04-30). The original 2026-04-18 entry's fix option (a) — "persist step state in `bellows.db` keyed by plan slug" — was implemented exactly as recommended.
> ```
>
> **Edit 4 — PROJECT_STATUS.md: close Phase 8 QA paperwork pending item.** Use `Filesystem:edit_file` on `PROJECT_STATUS.md` to find the verbatim line beginning `- Phase 8 QA paperwork catchup — QA Step 2 never completed cleanly` (this is the first bullet under `## Pending (next session)`) and DELETE that entire line including its trailing newline. Verify after the edit that `## Pending (next session)` retains at least one bullet — the `_parse_diff_stat` fix bullet should remain.
>
> **Edit 5 — PROJECT_STATUS.md: add a milestone entry documenting these hygiene closes.** Use `Filesystem:edit_file` to add a new bullet under `## Completed`. Anchor: insert as the FIRST bullet under the `## Completed` header (immediately after the header line). New entry verbatim: `- 2026-04-30: BACKLOG hygiene sweep — three carried items reverified against live code and closed: (1) BACKLOG 2026-04-23 no_permission_denials cross-project entry — superseded by BACKLOG #2 fix shipped 2026-04-28; (2) BACKLOG 2026-04-18 step-state-lost-across-re-claim — superseded by Phase 3b/3c shipped 2026-04-28/30; (3) Phase 8 QA paperwork (carried since 2026-04-16) — closed as functionally-verified-by-downstream-use. CEO decision: write retroactive QA paperwork would be ceremony without value two weeks out; functional verification by 11+ dependent plans (Phase 8.1, resume-from-correct-step, agent self-request, claim-at-entry, parallel defer, scope_check fix, cross-project verdict scoping, et al, all closed cleanly) has effectively replaced it. Reference: executable-backlog-hygiene-sweep-2026-04-30.`
>
> **Verify all five edits landed** by running `git --no-pager diff knowledge/BACKLOG.md PROJECT_STATUS.md` and confirming the diff shows: 2 strikethroughs added in BACKLOG, 2 new closed entries appended in BACKLOG, 1 line deleted from PROJECT_STATUS Pending, 1 new bullet added under PROJECT_STATUS Completed. **Deposit dev log** at `bellows/knowledge/development/backlog-hygiene-sweep-dev-log-2026-04-30.md` with: (1) the verbatim five edits applied, (2) the git diff output showing all changes, (3) any deviations or unexpected findings. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/BACKLOG.md PROJECT_STATUS.md knowledge/development/backlog-hygiene-sweep-dev-log-2026-04-30.md && git --no-pager commit -m "docs: BACKLOG hygiene sweep — close 3 carried items reverified against live code"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/backlog-hygiene-sweep-dev-log-2026-04-30.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/backlog-hygiene-sweep-dev-log-2026-04-30.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip specialist file and glossary reads — this is mechanical QA for markdown edits.** All commands run from `/Users/marklehn/Desktop/GitHub/bellows/`.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. Verify every listed deliverable. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If ANY item is ❌, attempt to fix; if unfixable, stop and report.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/`):**
>
> (1) BACKLOG.md no_permission_denials strikethrough applied: `grep -n "~~2026-04-23: \`no_permission_denials\`" knowledge/BACKLOG.md > knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_strikethrough_npd.txt 2>&1`. Expect exactly 1 match.
>
> (2) BACKLOG.md step-state strikethrough applied: `grep -n "~~2026-04-18: step state lost across re-claim" knowledge/BACKLOG.md > knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_strikethrough_stepstate.txt 2>&1`. Expect exactly 1 match.
>
> (3) BACKLOG.md two new Closed entries appended: `grep -nc "Closed 2026-04-30 (hygiene)" knowledge/BACKLOG.md > knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_closed_count.txt 2>&1`. Expect count = 2.
>
> (4) PROJECT_STATUS.md Phase 8 QA paperwork bullet removed: `grep -c "Phase 8 QA paperwork catchup" PROJECT_STATUS.md > knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_phase8_removed.txt 2>&1`. Expect count = 0.
>
> (5) PROJECT_STATUS.md hygiene sweep milestone bullet added: `grep -n "BACKLOG hygiene sweep — three carried items" PROJECT_STATUS.md > knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_milestone_added.txt 2>&1`. Expect exactly 1 match.
>
> (6) Git log — last commit covers both files: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --name-only > knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/git_commit.txt 2>&1`. Expect commit message references "BACKLOG hygiene sweep" and the changed files include both `knowledge/BACKLOG.md` and `PROJECT_STATUS.md`.
>
> **Deposit QA report** to `bellows/knowledge/qa/backlog-hygiene-sweep-qa-2026-04-30.md` with the verification table citing each evidence file path in the Evidence column. Include the literal stdout of the Rule 20 self-check block in the QA report body. Mark any check that cannot be completed as ❌ with a reason; do NOT mark ✅ with hedging language.
>
> **Mandatory Rule 20 self-check block (execute verbatim, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "executable-backlog-hygiene-sweep-2026-04-30"
> qa_report_path = "knowledge/qa/backlog-hygiene-sweep-qa-2026-04-30.md"
> evidence_dir = f"knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_strikethrough_npd.txt",
>     "grep_strikethrough_stepstate.txt",
>     "grep_closed_count.txt",
>     "grep_phase8_removed.txt",
>     "grep_milestone_added.txt",
>     "git_commit.txt",
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
> **Caveat for the hedging-keyword scan:** the new BACKLOG Closed entries this plan adds contain the word "pending" in references (e.g., "carried items"). Any positive-status row in the QA REPORT that quotes those entries verbatim could trip the hedging scan. To avoid false positives, the QA report's verification table should describe the verification result without embedding the BACKLOG entry text — e.g., write "Strikethrough applied to no_permission_denials entry" rather than quoting the entry itself.
>
> If the self-check prints `FAILED`, STOP — do not move plan to Done, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23.
>
> **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md && git --no-pager commit -m "chore: QA + feedback for BACKLOG hygiene sweep"`.
>
> **STOP. Plan complete after this step. Do NOT move plan to Done — Planner performs Done/ move after Rule 22 verification per Rule 25 terminal-step resolution.**
>
> **Deposits:**
> - `bellows/knowledge/qa/backlog-hygiene-sweep-qa-2026-04-30.md`
> - `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_strikethrough_npd.txt`
> - `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_strikethrough_stepstate.txt`
> - `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_closed_count.txt`
> - `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_phase8_removed.txt`
> - `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/grep_milestone_added.txt`
> - `bellows/knowledge/qa/evidence/executable-backlog-hygiene-sweep-2026-04-30/git_commit.txt`
