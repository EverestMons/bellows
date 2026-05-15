# Bellows — BACKLOG Hygiene Close: 2026-04-18 Planner↔Bellows Integration
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Documentation Agent) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. After Step 2 completes, the Planner performs Rule 22 verification and the terminal Done/ move.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-backlog-close-2026-04-18-integration-protocol-2026-05-01.md")`. **You are the Bellows Documentation Analyst.** Skip specialist file and glossary reads — this is a markdown-only BACKLOG hygiene edit. Make two edits to `bellows/knowledge/BACKLOG.md` using the canonical Python file write pattern via Filesystem MCP tools (read full file → produce new content → write full file). **Edit 1 — remove the closing entry from Open.** Find the verbatim line beginning with `- 2026-04-18: Planner↔Bellows integration protocol underdefined — we nearly committed a` and ending with `compose into a single "Bellows becomes reliable Layer 1 infrastructure" workstream.` (single bullet, multi-sentence — find and remove the entire bullet including its trailing newline). **Edit 2 — add the closure entry to the top of the Closed section.** Find the line `## Closed` followed by a blank line, and insert the following bullet immediately after the blank line (before the existing `- **Closed 2026-04-30:** BACKLOG #11` entry): `- **Closed 2026-05-01 (hygiene):** "2026-04-18: Planner↔Bellows integration protocol underdefined." All three blocking dependencies resolved — step-persistence (closed 2026-04-30 via Phase 3b/3c), watcher reliability (closed 2026-04-19 / 2026-04-28), verdict mechanization (closed 2026-04-30, "don't build" recommendation). Bellows Execution Model section added to PLANNER_TEMPLATE.md v4.29 (2026-04-30) covering three-layer model, plan lifecycle state machine, eight-gate classification, verdict cycle, disable-auto-close model, atomic deposit cross-reference, Planner discipline cross-references (Rules 22–26), Layer 1 invariant, and restart discipline. Rules 22–26 codify the Planner-side discipline this entry was waiting to specify. Audit findings at \`bellows/knowledge/research/bellows-integration-section-audit-2026-05-01.md\` confirm v4.29 section is accurate against live code across all five audit dimensions; the original 2026-04-18 concern ("would document an incorrect state machine") is structurally gone — the v4.29 section was written from the post-resolution architecture. Reference: \`diagnostic-bellows-integration-section-audit-2026-05-01.md\`.` (Note: the closure entry is a single line in the BACKLOG bullet list — preserve it as one line with backtick code spans escaped as in the source above.) **Edit 3 — add new Open entry at top of Open section.** Find the line `## Open` followed by a blank line, and insert the following bullet immediately after the blank line (before the existing `- 2026-04-30: parallel-plan scope_check diff-collision` entry): `- 2026-05-01: Bellows section omits parallel-N- dispatch mechanics — surfaced by audit at \`knowledge/research/bellows-integration-section-audit-2026-05-01.md\`. The v4.29 PLANNER_TEMPLATE.md "Bellows Execution Model" section describes the state machine, eight gates, verdict cycle, and disable-auto-close model, but does not mention parallel group dispatch (the \`parallel-N-\` filename prefix, \`_pending_groups\`, 5-second settle window in PlanHandler). The mechanic is documented in the File Naming Convention subsection elsewhere in PLANNER_TEMPLATE.md, but a reader consulting the Bellows section to understand how Bellows dispatches plans would not learn that parallel dispatch exists as a native path with its own concurrency semantics. Compounded by the open 2026-04-30 entry above (parallel-plan scope_check diff-collision) — readers evaluating whether to use \`parallel-N-\` for committing plans need both the dispatch mechanics AND the reliability gap in one place. Fix shape: add a short "Parallel Group Dispatch" subsection to the Bellows Execution Model section explaining the filename prefix convention, the settle window, and a cross-reference to the open scope_check diff-collision item. Low priority — quality-of-life documentation gap, not a reliability bug. Captured per audit recommendation 2026-05-01.` **After both edits commit:** verify the file by reading it back and confirming both edits landed (the 2026-04-18 entry is gone from Open, the closure entry is at top of Closed, the new 2026-05-01 entry is at top of Open). Commit with message `docs: close 2026-04-18 BACKLOG entry, add parallel-dispatch documentation gap`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/BACKLOG.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/BACKLOG.md` and check that Step 1's three edits landed: (1) the 2026-04-18 entry no longer appears in the Open section, (2) the closure entry "Closed 2026-05-01 (hygiene)" appears at the top of the Closed section, (3) the new "2026-05-01: Bellows section omits parallel-N- dispatch mechanics" entry appears at the top of the Open section. If any edit is missing or malformed, stop and report the issue to the CEO before proceeding.** **You are the Bellows QA agent.** Skip specialist file and glossary reads — this is a markdown-only QA verification. Test scope: targeted (no test suite execution — this is a documentation-only change). **FIRST — Deliverable Verification.** Read the prior DEV step's Output Receipt "Files Created or Modified (Code)" list. The only listed file should be `bellows/knowledge/BACKLOG.md`. Verify the three edits via grep. Pipe each grep's literal output to its evidence file using Python file I/O. Specifically: (1) Run `grep -c "2026-04-18: Planner↔Bellows integration protocol underdefined" bellows/knowledge/BACKLOG.md` — expect output `1` (the closure entry references the topic name; the original Open bullet should be gone). Pipe to `bellows/knowledge/qa/evidence/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01/grep_open_entry_removed.txt`. Manually inspect the file to confirm the single match is in the Closed section, not Open. (2) Run `grep -n "Closed 2026-05-01 (hygiene)" bellows/knowledge/BACKLOG.md` — expect exactly one match. Pipe to `bellows/knowledge/qa/evidence/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01/grep_closure_entry.txt`. (3) Run `grep -n "2026-05-01: Bellows section omits parallel-N- dispatch mechanics" bellows/knowledge/BACKLOG.md` — expect exactly one match. Pipe to `bellows/knowledge/qa/evidence/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01/grep_new_open_entry.txt`. (4) Run `git --no-pager log -1 --format=%s -- bellows/knowledge/BACKLOG.md` — expect the commit message from Step 1. Pipe to `bellows/knowledge/qa/evidence/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01/git_log.txt`. **Produce verification table:** `| Deliverable | Expected | Status (✅/❌) | Evidence |` with rows for: (a) 2026-04-18 entry removed from Open, (b) closure entry present at top of Closed, (c) new 2026-05-01 entry present at top of Open, (d) commit landed with descriptive message. If ANY item is ❌, stop and report to CEO — do NOT proceed to PROJECT_STATUS update or Rule 20 self-check. **Deposit the QA report** to `bellows/knowledge/qa/qa-backlog-close-2026-04-18-integration-protocol-2026-05-01.md` with the verification table and the literal stdout of the Rule 20 self-check below. **Update PROJECT_STATUS.md** — add a completed milestone entry: "Closed 2026-04-18 BACKLOG entry (Planner↔Bellows integration protocol underdefined) via hygiene close. Audit at knowledge/research/bellows-integration-section-audit-2026-05-01.md confirmed v4.29 PLANNER_TEMPLATE.md Bellows Execution Model section accurate. Captured new low-priority BACKLOG item: parallel-N- dispatch mechanics not documented in Bellows section." Commit PROJECT_STATUS.md with descriptive message. **Final commit and STOP — do NOT move this plan to Done. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.** **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. The feedback append + commit are the absolute last operations. Then stop. **Run the Rule 20 self-check at the very end and include its literal stdout in the QA report:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-backlog-close-2026-04-18-integration-protocol-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/qa-backlog-close-2026-04-18-integration-protocol-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_open_entry_removed.txt",
>     "grep_closure_entry.txt",
>     "grep_new_open_entry.txt",
>     "git_log.txt",
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
> - `bellows/knowledge/qa/qa-backlog-close-2026-04-18-integration-protocol-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01/` (4 files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
