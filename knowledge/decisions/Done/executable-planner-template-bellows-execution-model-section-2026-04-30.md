# PLANNER_TEMPLATE — Bellows Execution Model Section
**Date:** 2026-04-30 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (BELLOWS_DOCUMENTATION_ANALYST) → Step 2 (BELLOWS_QA)
**Priority:** 1

## Context

The 2026-04-18 BACKLOG entry "Planner↔Bellows integration protocol underdefined" is now structurally unblocked. Step-state-persistence (BACKLOG #6 Phase 3a + 3b + 3c) and watcher-reliability (BACKLOG #4) have all shipped. The protocol is settled enough to document.

The existing PLANNER_TEMPLATE.md has substantial Bellows coverage scattered across Rules 22, 23, 24, 25, 26 and the Resume Protocol subsection — but no top-down architectural overview. A reader new to the system has to reverse-engineer the architecture from the rules. This plan adds a new "Bellows Execution Model (Layer 1 Autonomous Dispatch)" section between Quick Fix Protocol and the existing Execution Model section, providing the orientation overview that makes the existing rules cohere.

The existing "Execution Model" section is renamed to "Manual Execution Model (RUN EXE / RUN DIAG / Bootstrap)" to disambiguate from the new Bellows section. The two sections describe two distinct execution paths: Manual is CEO-bootstrapped via Claude Code; Bellows is autonomous dispatch via filesystem watcher. Reader sees two clear paths.

Test Scope: none — single-file governance edit, no code, no tests. Per the 2026-04-20 Position A precedent (no markdown-only QA carve-out), every plan still gets a separate QA agent for grep + structural verification.

Split-commit pattern: DEV's edit to PLANNER_TEMPLATE.md lands at governance-root repo (`/Users/marklehn/Desktop/GitHub/`); plan housekeeping (PROJECT_STATUS update, feedback append) commits to bellows repo. The DEV step produces TWO commits, one per repo.

## How to Run This Plan

Bootstrap:
```
Read the plan at bellows/knowledge/decisions/executable-planner-template-bellows-execution-model-section-2026-04-30.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS_DOCUMENTATION_ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-planner-template-bellows-execution-model-section-2026-04-30.md", "bellows/knowledge/decisions/in-progress-executable-planner-template-bellows-execution-model-section-2026-04-30.md")`. You are the Bellows Documentation Analyst. Read your specialist file at `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` first. Skip glossary read — this is a governance documentation task. Read `bellows/bellows.py` (full file, ~1200 lines), `bellows/gates.py`, `bellows/verdict.py` to ground the section in current code reality. Read `bellows/knowledge/BACKLOG.md` Closed section for the disable-auto-close model context (closed 2026-04-24). Read the current `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` lines 1-50 (header) and locate the existing `## Execution Model` section header — it currently sits between the Quick Fix Protocol section and ends at the file's end. **Two edits to PLANNER_TEMPLATE.md.** Edit 1: rename the existing `## Execution Model` header to `## Manual Execution Model (RUN EXE / RUN DIAG / Bootstrap)` — find the exact line `## Execution Model` (only occurrence at the H2 level) and replace with the new header. Edit 2: insert a new `## Bellows Execution Model (Layer 1 Autonomous Dispatch)` section IMMEDIATELY BEFORE the renamed `## Manual Execution Model` header. The new section must contain these 9 subsections in order, written as flowing prose (NOT bullet-only), targeting ~120 lines total: **(1) What Bellows Is** — three-layer model (Layer 1 Bellows = dispatch + gate, Layer 2 agents = execute, Layer 3 Planner = judgment); mechanical-only invariant (file moves, subprocess invocation, gate evaluation, no domain judgment); ~1200 LOC across 8 modules at bellows/. **(2) Plan Lifecycle States** — text-diagram showing transitions: `executable-*` → `in-progress-*` (claim via shutil.move) → either auto-close to `Done/` (when auto_close=true header AND all gates pass AND not is_qa_step) OR pause to `verdict-pending-*` (default behavior). From `verdict-pending-*`: continue verdict resumes via `in-progress-*` → next step (loops back), or terminal-step continue moves to `Done/`. Stop verdict moves to `halted-*` (no resume path exists). Identify which actor performs each transition (Bellows for most, Planner for terminal Done/ move per Rule 25). **(3) The Eight Gates** — enumerate the 8 gates with one-liner each: `receipt_status` (agent reported Complete via Output Receipt), `ceo_flags` (any CEO-visible flags raised in receipt), `no_errors` (no exceptions or auth failures in claude -p output), `no_permission_denials` (no write-class tool denials — read-class Grep/Glob/Read exempted per BACKLOG #2 closure), `deposit_exists` (declared **Deposits:** files exist on disk), `scope_check` (files modified are within project subtree — uses --relative -- . per BACKLOG #4 closure), `is_qa_step` (heuristic detection, triggers qa_checkpoint pause reason), `file_change_audit` (informational, records files changed). State which are blocking vs. informational. State that gates run AFTER each step completes, not during. **(4) The Verdict Cycle** — describe the request/response loop: Bellows posts verdict request to `bellows/verdicts/pending/verdict-request-{slug}-step-{N}.md` when a step pauses; the request file contains Plan, Project, Step, Total Steps, Pause Reason Code, Deposit fields. The Planner (per Rule 25) polls `pending/` each turn, reads matching requests, performs Rule 22 verification, and deposits a continue verdict to `bellows/verdicts/resolved/verdict-{slug}-step-{N}.md` with content `continue\n{reason}` (or `stop\n{reason}` to halt). Bellows's `_consume_verdicts()` reads resolved/, dispatches the next step (continue) or moves to halted-* (stop), cleans up the pending file, and moves the resolved file to `processed-*`. **(5) The Disable-Auto-Close Model** — auto_close defaults to false for ALL plans as of 2026-04-24 (executable-disable-auto-close-2026-04-24). Every terminal step produces a verdict request unless the plan header explicitly opts in via `auto_close: true`. Rationale: Failure 3 root cause was auto-close racing gate evaluation; making auto-close opt-in eliminates the race structurally. Mention that the Planner (not the agent) performs the terminal Done/ move after Rule 22 verification — this is Rule 25's terminal-step resolution path. **(6) Atomic Deposit** — one-paragraph summary: plans deposited to Bellows-watched `knowledge/decisions/` directories MUST be atomic (single file event), or the watcher races the writer. Three patterns; defer details to Rule 24. **(7) Planner Discipline (Cross-References)** — pointer table mapping each Bellows-related Rule to its concern: | Rule | Concern | | Rule 22 | Planner verification of deposited files | | Rule 23 | End-of-plan housekeeping ordering | | Rule 24 | Atomic plan deposit | | Rule 25 | Verdict request polling + pause-reason routing + terminal Done/ move | | Rule 26 | **Deposits:** field convention |. **(8) What Bellows Does NOT Do** — explicit non-responsibilities: no domain judgment, no deposit content verification (Rule 22 is Planner-side), no agent quality assessment, no plan content modification (only file renames via shutil.move), no test execution decisions, no fix authoring. State why: Layer 1 invariant — anything requiring "deciding whether the work is good" is Layer 3 (Planner). **(9) Restart Discipline** — Bellows does not hot-reload Python modules; code changes to bellows.py / gates.py / verdict.py / parser.py require manual daemon restart. Reference today's Phase 3b/3c canary pattern (deposit a tiny canary plan after restart to confirm new code loaded). State the canary pattern as a recommendation, not a rule. **Header version bump.** At the top of PLANNER_TEMPLATE.md, change `**Version:** 4.28` to `**Version:** 4.29` and `**Last Updated:** 2026-04-28 (v4.28)` to `**Last Updated:** 2026-04-30 (v4.29)`. Add to the Lessons Learned table at the bottom: a new row dated 2026-04-30 summarizing why the Bellows Execution Model section was added (BACKLOG #4 + #6 closure unblocked the original 2026-04-18 documentation deferral; section provides the architectural overview that makes Rules 22-26 cohere). **Use Filesystem:edit_file for ALL edits** — atomic semantics, no Rule 24 risk for governance-root files (PLANNER_TEMPLATE.md is not in a Bellows-watched directory). Anchor every edit on a verbatim existing line. **Split commit pattern.** First commit lands at governance root: `cd /Users/marklehn/Desktop/GitHub && git --no-pager add PLANNER_TEMPLATE.md && git --no-pager commit -m "docs: add Bellows Execution Model section to PLANNER_TEMPLATE v4.29"`. Second commit (after standard prompt feedback append to `bellows/knowledge/research/agent-prompt-feedback.md`) lands at bellows repo: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/research/agent-prompt-feedback.md && git --no-pager commit -m "docs: prompt feedback — Documentation Analyst v4.29 PLANNER_TEMPLATE update"`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — BELLOWS_QA

---

> Before starting, verify Step 1 completed by running `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --stat PLANNER_TEMPLATE.md` — the most recent commit must be the v4.29 update. If the commit is missing, stop and report. You are the Bellows QA agent. Skip specialist file and glossary reads — this is a mechanical grep verification task. **FIRST — Deliverable Verification.** Verify the new section landed by running these greps against `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` and piping each output to `bellows/knowledge/qa/evidence/planner-template-bellows-execution-model-section-2026-04-30/<filename>.txt`: (a) `grep -n "^## Bellows Execution Model" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` → `grep_section_header.txt`, must match exactly once. (b) `grep -n "^## Manual Execution Model" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` → `grep_renamed_header.txt`, must match exactly once. (c) `grep -n "^### " /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md | head -60` → `grep_subsection_headers.txt`, scan for the 9 expected subsection headers somewhere in output (What Bellows Is, Plan Lifecycle States, The Eight Gates, The Verdict Cycle, The Disable-Auto-Close Model, Atomic Deposit, Planner Discipline, What Bellows Does NOT Do, Restart Discipline — exact case-insensitive match acceptable). (d) `grep -n "Version:" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md | head -3` → `grep_version_bump.txt`, must show `**Version:** 4.29` and `**Last Updated:** 2026-04-30 (v4.29)`. (e) `grep -c "receipt_status\|ceo_flags\|no_errors\|no_permission_denials\|deposit_exists\|scope_check\|is_qa_step\|file_change_audit" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` → `grep_eight_gates.txt`, must be ≥ 8 (one mention per gate name minimum). (f) `wc -l /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` before/after — actually, just confirm post-edit line count via `wc -l` and write to `wc_lines.txt`; expected ~1100-1200 lines (was ~1080 pre-edit, +120 lines for new section). Build verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. **Stale governance reference check.** Run `git --no-pager log -2 --oneline /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` from `/Users/marklehn/Desktop/GitHub/` and confirm the most recent commit is the v4.29 update; pipe to `git_log_planner.txt`. **QA Report.** Deposit at `bellows/knowledge/qa/planner-template-bellows-execution-model-section-2026-04-30.md` with verification table, all evidence file references, and Rule 20 self-check stdout. **Run the Rule 20 self-check** (template below; required_evidence_files = ["grep_section_header.txt", "grep_renamed_header.txt", "grep_subsection_headers.txt", "grep_version_bump.txt", "grep_eight_gates.txt", "wc_lines.txt", "git_log_planner.txt"]). Include literal stdout in the report. If FAILED — STOP, do NOT update PROJECT_STATUS, do NOT commit. **PROJECT_STATUS update.** Use `Filesystem:edit_file` to insert a new line. Anchor: locate the exact existing line `- 2026-04-30: Phase 3c plan-hash drift warning shipped (BACKLOG #6 fully closed). Added \`import hashlib\` + 7-LOC warning block to \`run_plan()\` in \`bellows.py\` between DB resume block and is_diagnostic check. Fires when resume_step > 1 AND shadow_text present AND sha256(shadow) != sha256(plan_text). Stdout warning + Pushover notification "Bellows — Plan Modified". Warn-and-proceed (no halt). +1 unit test (\`test_run_plan_plan_hash_drift_warning\`), 71 total in test_bellows.py. REMINDER: restart Bellows to load.` and replace it with that exact line followed by `\n` followed by `- 2026-04-30: PLANNER_TEMPLATE v4.29 — added "Bellows Execution Model (Layer 1 Autonomous Dispatch)" section providing architectural overview of three-layer model, plan lifecycle states, the 8 gates, verdict cycle, disable-auto-close model, atomic deposit, Planner discipline cross-references, what Bellows does NOT do, and restart discipline. Existing "Execution Model" section renamed to "Manual Execution Model (RUN EXE / RUN DIAG / Bootstrap)". Closes 2026-04-18 BACKLOG entry "Planner↔Bellows integration protocol underdefined" — was deferred pending step-state-persistence (BACKLOG #6 Phase 3b/3c closed today) and watcher-reliability (BACKLOG #4 closed 2026-04-28).`. **Feedback append.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit.** Single bellows-repo commit with QA report + evidence files + PROJECT_STATUS edit + feedback, message: "qa: PLANNER_TEMPLATE v4.29 Bellows Execution Model section — verified". **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/planner-template-bellows-execution-model-section-2026-04-30.md`
> - `bellows/knowledge/qa/evidence/planner-template-bellows-execution-model-section-2026-04-30/` (7 files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "planner-template-bellows-execution-model-section-2026-04-30"
> qa_report_path = "bellows/knowledge/qa/planner-template-bellows-execution-model-section-2026-04-30.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_section_header.txt", "grep_renamed_header.txt", "grep_subsection_headers.txt", "grep_version_bump.txt", "grep_eight_gates.txt", "wc_lines.txt", "git_log_planner.txt"]
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
