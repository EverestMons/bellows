# Bellows — PROJECT_STATUS Update + BACKLOG Addition (Session Wrap)
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted (markdown audit only, no test execution) | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA)
**Priority:** 1

## Context

Today's session in bellows scope produced 6+ items worth recording in PROJECT_STATUS.md and surfaced one new BACKLOG entry for the `_cleanup_verdicts_for_slug` gap.

Session work to record:
1. Verdict format mismatch discovery — 13 verdict files stranded due to PLANNER_TEMPLATE Rule 25 documenting wrong content spec; all 13 patched with `verdict: ` prefix prepend.
2. PLANNER_TEMPLATE v4.30 shipped (executable-rule-25-verdict-content-spec-fix-2026-05-01) — Rule 25 verdict content spec corrected at 3 occurrences. Commits b705e48 (governance) + f3c414f (bellows dev log).
3. Pending/ archive operation — 51 verdict-request files moved from `bellows/verdicts/pending/` to `bellows/verdicts/pending/archived/` after cross-referencing against Done/ across all watched projects. Pending/ now empty except 3 truly-active verdict requests.
4. Stranded plan resolution — `verdict-pending-executable-planner-template-lessons-step-numbering-2026-04-23` (9 days old) closed via fresh QA executable `executable-close-stranded-lessons-step-numbering-2026-05-01`.
5. Accidental Step 2 dispatch incident — Planner deposited continue verdict on 9-day-old plan thinking it would close (it advances to N+1 instead). Plan correctly executed Step 2, gate-failed on session-noise scope_check, recovered via stop verdict.
6. PLANNER_TEMPLATE v4.31 shipped (executable-lessons-verdict-format-and-stranded-plans-2026-05-01) — three Lessons rows codifying verdict format mismatch, continue verdict semantics, stranded plans audit. Commit 3030402.

New BACKLOG entry: `_cleanup_verdicts_for_slug` does not sweep pending/ on consumption paths actually used in today's session (stale-verdict, continue-to-done, stop). 17 successful verdict consumptions, 0 pending sweeps.

Test Scope: targeted — no production code, two markdown files (`bellows/PROJECT_STATUS.md` + `bellows/knowledge/BACKLOG.md`), mechanical verification via grep + git log. Per Position A, Step 2 is required.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-session-wrap-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-session-wrap-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-bellows-session-wrap-2026-05-01.md")`. **Skip specialist file and glossary reads — this is a mechanical session-wrap edit appending entries to two markdown files.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all grep operations against the markdown files** — do NOT use the native Grep tool.
>
> **Task:** Apply two `Desktop Commander:edit_block` operations and bump `Last Updated` on PROJECT_STATUS.md.
>
> **Edit 1 (PROJECT_STATUS.md — append session entries above the existing 2026-05-01 first entry).** The existing `## Completed` section starts with a 2026-05-01 entry about the activity-based timeout BACKLOG close. Find the exact line `## Completed` and replace with `## Completed\n- 2026-05-01: PLANNER_TEMPLATE v4.31 shipped (plan: executable-lessons-verdict-format-and-stranded-plans-2026-05-01). Three Lessons rows appended codifying today's failure modes: (1) verdict format mismatch — Rule 25 documented \`continue\\n{reason}\` while \`bellows/verdicts/README.md\` requires \`verdict:\` prefix on line 1 per regex \`^verdict:\\s*(continue|stop)$\`; meta-lesson on validating governance prescriptions against system READMEs. (2) Continue verdict semantics — \`verdict: continue\` advances step N→N+1, does NOT close the plan; close requires terminal-step continue OR \`verdict: stop\`. (3) Stranded plans audit — 5 plans across 3 projects silently stranded over 2-3 weeks before today's session caught them; "stranded plans audit" promoted to routine Planner discipline. Commit 3030402 governance-root.\n- 2026-05-01: PLANNER_TEMPLATE v4.30 shipped (plan: executable-rule-25-verdict-content-spec-fix-2026-05-01). Rule 25 verdict content spec corrected at 3 occurrences in PLANNER_TEMPLATE.md (Rule 25 terminal-step resolution item 3 line 709, Bellows Execution Model verdict cycle line 861, Manual Execution Model resume protocol line 973). All three now reference \`verdict: continue\\n{reason}\` matching Bellows's parser regex. Commits b705e48 (governance-root) + f3c414f (bellows dev log).\n- 2026-05-01: Verdict format mismatch root-caused and patched mid-session. 13 verdict files stranded in \`bellows/verdicts/resolved/\` (8 from prior sessions + 5 from today's first close attempts) because all 13 were missing the \`verdict:\` prefix that \`bellows/verdicts/README.md\` requires. Empirical test: prepending \`verdict: \` to one stranded resolved file caused immediate consumption on next 30s scan. Patched all 13 via shell loop. All consumed cleanly as \`processed-*\`. Underlying governance bug (PLANNER_TEMPLATE describing wrong content spec) fixed via v4.30 plan above.\n- 2026-05-01: Pending/ archive operation. Audited 47 verdict-request files in \`bellows/verdicts/pending/\` against \`*/knowledge/decisions/Done/\` across all watched projects: 41 archive-safe (slug present in some Done/), 3 stale halted-plan requests, 3 truly active. Archived 44 files (41 + 3) to \`bellows/verdicts/pending/archived/\` (mirrors decisions/Done/ pattern). 0 truly-orphan files. Pending/ now contains only the 3 active verdicts.\n- 2026-05-01: Stranded plan recovered. \`verdict-pending-executable-planner-template-lessons-step-numbering-2026-04-23\` (9 days old) had Step 1 work complete (lesson row live in PLANNER_TEMPLATE.md line 1235) but Step 2 never ran due to BACKLOG #2 pre-fix gate behavior. Closed via fresh QA executable \`executable-close-stranded-lessons-step-numbering-2026-05-01\` which adapted the original Step 2's checks to current state. Bellows ran the close-plan cleanly; Rule 22 verification PASSED. Original 2026-04-23 plan moved to Done/.\n- 2026-05-01: Accidental Step 2 dispatch incident on the 2026-04-23 stranded plan during recovery. Planner deposited \`verdict: continue\` thinking it would close the plan, but a non-terminal continue advances step N→N+1. Bellows correctly executed the original Step 2 (which had been authored 9 days ago and was internally inconsistent with current state); Step 2 gate-failed on session-noise scope_check (34 files modified during today's heavy session activity). Recovered via \`verdict: stop\`. Plan ended in Done/ rather than \`halted-\` (acceptable outcome since the work is verified by the fresh close-plan above). Lesson captured in v4.31 Row 2.`. After this, find the exact existing line `**Last Updated:** 2026-05-01` and verify it's already current — no edit needed unless date changed.
>
> **Edit 2 (BACKLOG.md — prepend new Open entry).** Find the exact existing line that opens the Open section's first entry: `- 2026-05-01: Bellows section omits parallel-N- dispatch mechanics — surfaced by audit at` (this is the start of the most recent open BACKLOG entry). Replace with this new entry followed by the original line:
>
> ```
> - 2026-05-01: `_cleanup_verdicts_for_slug` does not fire on stale-verdict consumption, continue-to-done, or stop verdicts — surfaced today during a session that consumed 17 verdicts across multiple paths (13 patched verdicts from format-mismatch recovery + 4 from corrected-batch closes) with 0 pending request files swept. The BACKLOG #9 close (closed 2026-04-24, "4 terminal-state call sites + one-time startup sweep") apparently doesn't cover the consumption paths actually used today. Trace symptom: 51 pending request files accumulated in `bellows/verdicts/pending/` from prior sessions despite their parent plans being long-closed. CEO had to perform a batched `mv` operation today to archive 51 files to `pending/archived/`. **Cheap diagnostic to scope:** trace `_cleanup_verdicts_for_slug` call sites in `bellows.py` and identify which transitions trigger sweeps (current behavior) vs which don't (today's failures). Suspected gaps: (a) stale-verdict consumption path (verdict file consumed when plan already in Done/), (b) continue-to-done transition (terminal-step continue verdict closes plan), (c) stop verdict path (plan moved to halted-). **Possible fix shape:** fire `_cleanup_verdicts_for_slug` on every successful verdict consumption regardless of plan transition type, OR fire from `_consume_verdicts` outer loop after the verdict-to-processed rename completes. Low priority — quality-of-life only, not reliability. Pending/ accumulation produces silent cruft requiring periodic batch cleanup, not stuck plans. Reference: today's session archive operation, 51 files moved to `pending/archived/`.
> - 2026-05-01: Bellows section omits parallel-N- dispatch mechanics — surfaced by audit at
> ```
>
> **Note on Edit 2 anchor:** The original line is long and ends with "knowledge/research/bellows-integration-section-audit-2026-05-01.md" — match that exact opening fragment. If `Desktop Commander:edit_block` cannot find it because of formatting differences, read the first 30 lines of `bellows/knowledge/BACKLOG.md` and use a shorter unique anchor (e.g., the first 60 characters of the line). Preserve the entire original line verbatim in the replacement.
>
> **After both edits**, verify by running `bash`:
> - `head -10 bellows/PROJECT_STATUS.md > /tmp/verify_status.txt`
> - `awk '/## Open/,/^---$/' bellows/knowledge/BACKLOG.md | head -5 > /tmp/verify_backlog.txt`
> - `cat /tmp/verify_status.txt /tmp/verify_backlog.txt`
>
> Expect: PROJECT_STATUS.md shows the 6 new 2026-05-01 entries before the activity-timeout entry, BACKLOG.md shows the new `_cleanup_verdicts_for_slug` entry as the first item under `## Open`.
>
> **Deposit dev log** at `bellows/knowledge/development/bellows-session-wrap-dev-log-2026-05-01.md` containing: (1) verbatim anchor for each edit, (2) summary of new content (counts: PROJECT_STATUS gained 6 entries, BACKLOG gained 1 entry), (3) verification grep output.
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add PROJECT_STATUS.md knowledge/BACKLOG.md knowledge/development/bellows-session-wrap-dev-log-2026-05-01.md && git commit -m "docs: 2026-05-01 session wrap (PROJECT_STATUS x6 + BACKLOG cleanup_verdicts_for_slug gap)"; cd /Users/marklehn/Desktop/GitHub`. Single commit (single repo, no governance-root changes). **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/bellows-session-wrap-dev-log-2026-05-01.md`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/BACKLOG.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/bellows-session-wrap-dev-log-2026-05-01.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip specialist file and glossary reads — this is mechanical QA for two markdown appends.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all grep operations** — do NOT use the native Grep tool.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. Verify every listed deliverable exists with the described change.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/`):**
>
> (1) **PROJECT_STATUS.md gained v4.31 entry** — `grep -n "PLANNER_TEMPLATE v4.31 shipped" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_v431.txt 2>&1`. Expect exactly 1 match.
>
> (2) **PROJECT_STATUS.md gained v4.30 entry** — `grep -n "PLANNER_TEMPLATE v4.30 shipped" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_v430.txt 2>&1`. Expect exactly 1 match.
>
> (3) **PROJECT_STATUS.md gained verdict-format-mismatch entry** — `grep -n "Verdict format mismatch root-caused and patched" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_format.txt 2>&1`. Expect exactly 1 match.
>
> (4) **PROJECT_STATUS.md gained pending-archive entry** — `grep -n "Pending/ archive operation" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_archive.txt 2>&1`. Expect exactly 1 match.
>
> (5) **PROJECT_STATUS.md gained stranded-plan recovery entry** — `grep -n "Stranded plan recovered" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_stranded.txt 2>&1`. Expect exactly 1 match.
>
> (6) **PROJECT_STATUS.md gained accidental-step-2 incident entry** — `grep -n "Accidental Step 2 dispatch incident" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_incident.txt 2>&1`. Expect exactly 1 match.
>
> (7) **BACKLOG.md gained `_cleanup_verdicts_for_slug` entry as first Open item** — `awk '/## Open/{found=1; next} found && /^- 2026/{print; exit}' bellows/knowledge/BACKLOG.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/awk_first_open_entry.txt 2>&1`. Expect output to start with `- 2026-05-01: \`_cleanup_verdicts_for_slug\` does not fire`.
>
> (8) **BACKLOG.md preserved prior first-Open entry (parallel-N- audit)** — `grep -c "Bellows section omits parallel-N- dispatch mechanics" bellows/knowledge/BACKLOG.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_backlog_anchor.txt 2>&1`. Expect count `1`.
>
> (9) **Single-repo commit landed (bellows)** — `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --name-only > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/git_commit_bellows.txt 2>&1; cd /Users/marklehn/Desktop/GitHub`. Expect commit message contains "session wrap" and the file list contains both `PROJECT_STATUS.md` and `knowledge/BACKLOG.md`.
>
> **Deposit QA report** to `bellows/knowledge/qa/bellows-session-wrap-qa-2026-05-01.md` with the verification table citing each evidence file path in the Evidence column. **Include the literal stdout of the Rule 20 self-check block in the QA report body.**
>
> **Mandatory Rule 20 self-check block (execute verbatim from /Users/marklehn/Desktop/GitHub/, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "executable-bellows-session-wrap-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/bellows-session-wrap-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_status_v431.txt",
>     "grep_status_v430.txt",
>     "grep_status_format.txt",
>     "grep_status_archive.txt",
>     "grep_status_stranded.txt",
>     "grep_status_incident.txt",
>     "awk_first_open_entry.txt",
>     "grep_backlog_anchor.txt",
>     "git_commit_bellows.txt",
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
> **Note on hedging-keyword false-positive risk:** the Step 1 work captures the Pending/ archive operation, and "pending" appears as a literal noun in some verification check evidence text. The Rule 20 scan only flags hedging in **positive-status rows of the QA verification table** (rows containing ✅/OK/PASS/etc.). The check descriptions and evidence-file content are NOT scanned. To be safe, AVOID writing the literal string "pending" in any QA verification table cell — describe the entry as "v4.30 entry" or "verdict-format-mismatch entry", not "pending-archive entry" in the Status or Evidence columns. The check name in the prose around the table can use "pending" freely.
>
> If the self-check prints `FAILED`, STOP — do not proceed with closeout, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23: **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: 2026-05-01 bellows session wrap verified"; cd /Users/marklehn/Desktop/GitHub`. **STOP. Plan complete after this step. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification per Rule 25.**
>
> **Deposits:**
> - `bellows/knowledge/qa/bellows-session-wrap-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_v431.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_v430.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_format.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_archive.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_stranded.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_status_incident.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/awk_first_open_entry.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/grep_backlog_anchor.txt`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-2026-05-01/git_commit_bellows.txt`
