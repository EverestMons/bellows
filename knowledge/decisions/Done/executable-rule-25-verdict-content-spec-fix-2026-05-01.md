# Governance — PLANNER_TEMPLATE Rule 25 Verdict Content Spec Correction
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted (markdown audit only, no test execution) | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA)
**Priority:** 1

## Context

PLANNER_TEMPLATE.md currently documents the verdict file content spec incorrectly in three places. The README at `bellows/verdicts/README.md` requires the first line to match `^verdict:\s*(continue|stop)$` (case-insensitive), but PLANNER_TEMPLATE describes the content as `continue\n{reason}` (no `verdict:` prefix). This discrepancy stranded 13 verdict files in `bellows/verdicts/resolved/` during today's session — every verdict the Planner deposited per Rule 25's terminal-step resolution path was silently rejected by Bellows's parser. The fix is to correct three occurrences in PLANNER_TEMPLATE.md so they match the README.

The three occurrences:
1. Rule 25 "Terminal-step resolution and Planner-owned Done/ move", item 3
2. Bellows Execution Model — "The Verdict Cycle" subsection
3. Manual Execution Model — "Resume Protocol (Verdict-Only)" subsection

Version bump: 4.29 → 4.30 (content correction to existing rules; minor bump per the precedent that rule additions or rewrites bump the version).

Test Scope: targeted — no production code, single governance-root file edit, mechanical verification via grep + git log. Per Position A (no markdown-only QA carve-out), Step 2 is required even though the work is markdown-only.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-rule-25-verdict-content-spec-fix-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-rule-25-verdict-content-spec-fix-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-rule-25-verdict-content-spec-fix-2026-05-01.md")`. **Skip specialist file and glossary reads — this is a mechanical governance edit.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all grep operations against PLANNER_TEMPLATE.md** — do NOT use the native Grep tool. **Task:** Apply four anchored str_replace edits to PLANNER_TEMPLATE.md correcting three wrong-format verdict content specs and bumping the version. Use `Desktop Commander:edit_block` for each edit. **Edit 1 (Rule 25 terminal-step resolution item 3):** find the exact line `3. Resolve the Bellows verdict by depositing a verdict file to `bellows/verdicts/resolved/verdict-[slug]-step-[N].md` with content `continue\nRule 22 passed — Planner-authorized terminal close.`` and replace with `3. Resolve the Bellows verdict by depositing a verdict file to `bellows/verdicts/resolved/verdict-[slug]-step-[N].md` with content `verdict: continue\nRule 22 passed — Planner-authorized terminal close.` Bellows's parser requires the literal `verdict:` prefix on line 1 (case-insensitive) per `bellows/verdicts/README.md` regex `^verdict:\s*(continue|stop)$`. Files lacking the prefix are silently rejected.`. **Edit 2 (Bellows Execution Model — Verdict Cycle):** find the exact line `The Planner (per Rule 25) polls `verdicts/pending/` each conversation turn, reads matching verdict requests, routes on the Pause Reason Code (auto-proceeding to Rule 22 for `auto_close_disabled` and `qa_checkpoint`; halting and reporting to CEO for `gate_failure` and all other codes), and performs Rule 22 (a)–(e) verification on the deposit. On a clean pass, the Planner deposits a continue verdict to `bellows/verdicts/resolved/verdict-{slug}-step-{N}.md` with content `continue\n{reason}` (or `stop\n{reason}` to halt the plan).` and replace with `The Planner (per Rule 25) polls `verdicts/pending/` each conversation turn, reads matching verdict requests, routes on the Pause Reason Code (auto-proceeding to Rule 22 for `auto_close_disabled` and `qa_checkpoint`; halting and reporting to CEO for `gate_failure` and all other codes), and performs Rule 22 (a)–(e) verification on the deposit. On a clean pass, the Planner deposits a continue verdict to `bellows/verdicts/resolved/verdict-{slug}-step-{N}.md` with content `verdict: continue\n{reason}` (or `verdict: stop\n{reason}` to halt the plan). The `verdict:` prefix is required on line 1 (case-insensitive) per `bellows/verdicts/README.md`; files without it are silently rejected by `_consume_verdicts()`.`. **Edit 3 (Manual Execution Model — Resume Protocol code block):** find the exact 3-line block `continue\n<reason — Rule 22 verification pass, CEO authorization, etc.>` (the literal content inside the fenced code block; match exactly including the leading `continue` line) and replace with `verdict: continue\n<reason — Rule 22 verification pass, CEO authorization, etc.>`. **Edit 4 (Version bump):** find the exact line `**Version:** 4.29` and replace with `**Version:** 4.30`. Also find `**Last Updated:** 2026-04-30 (v4.29)` and replace with `**Last Updated:** 2026-05-01 (v4.30)`. After all four edits, verify by running `bash`: `grep -n "verdict: continue" PLANNER_TEMPLATE.md > /tmp/verify.txt && grep -n "Version: 4.30" PLANNER_TEMPLATE.md >> /tmp/verify.txt && cat /tmp/verify.txt`. Expect at least 3 `verdict: continue` matches (the three corrected places) and 1 `Version: 4.30` match. **Deposit dev log** at `bellows/knowledge/development/rule-25-verdict-content-spec-fix-dev-log-2026-05-01.md` containing: (1) verbatim anchor text for each of the 4 edits, (2) verbatim new text for each, (3) verification grep output. **Commit:** the edits are at governance root — `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md && git commit -m "docs(planner): v4.30 — correct verdict content spec in 3 places (verdict: prefix required by Bellows parser)"`. **Then commit the dev log to bellows repo:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/development/rule-25-verdict-content-spec-fix-dev-log-2026-05-01.md && git commit -m "docs: dev log for PLANNER_TEMPLATE v4.30 verdict content spec fix"; cd /Users/marklehn/Desktop/GitHub`. This is the split-commit pattern for governance-root edits per PLANNER_TEMPLATE Plan File Structure. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/rule-25-verdict-content-spec-fix-dev-log-2026-05-01.md`
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/rule-25-verdict-content-spec-fix-dev-log-2026-05-01.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip specialist file and glossary reads — this is mechanical QA for a governance markdown edit.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all grep operations against PLANNER_TEMPLATE.md** — do NOT use the native Grep tool.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. Verify every listed deliverable exists with the described change.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/`):**
>
> (1) **All three `verdict: continue` corrections present** — `grep -n "verdict: continue" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_verdict_continue.txt 2>&1`. Expect at least 3 matches across distinct sections (Rule 25, Bellows Execution Model, Manual Execution Model).
>
> (2) **No remaining bare `continue\n` patterns in verdict-spec contexts** — `grep -n "content \`continue\\\\n" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_no_bare_continue.txt 2>&1; echo "exit_code=$?" >> bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_no_bare_continue.txt`. Expect exit_code=1 (grep found nothing — clean), or 0 matches in the file body.
>
> (3) **Version bumped to 4.30** — `grep -n "^\*\*Version:\*\* 4.30$" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_version.txt 2>&1`. Expect exactly 1 match.
>
> (4) **Last Updated line carries new date** — `grep -n "^\*\*Last Updated:\*\* 2026-05-01 (v4.30)$" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_last_updated.txt 2>&1`. Expect exactly 1 match.
>
> (5) **Governance-root commit landed** — `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --name-only > bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/git_commit_governance.txt 2>&1; cd /Users/marklehn/Desktop/GitHub`. Expect commit message includes "v4.30" and the file list contains `PLANNER_TEMPLATE.md`.
>
> (6) **Bellows dev log commit landed** — `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --name-only > /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/git_commit_bellows.txt 2>&1; cd /Users/marklehn/Desktop/GitHub`. Expect commit message references "v4.30 verdict content spec fix" and file list contains the dev log path.
>
> **Deposit QA report** to `bellows/knowledge/qa/rule-25-verdict-content-spec-fix-qa-2026-05-01.md` with the verification table citing each evidence file path in the Evidence column. **Include the literal stdout of the Rule 20 self-check block in the QA report body.**
>
> **Mandatory Rule 20 self-check block (execute verbatim from /Users/marklehn/Desktop/GitHub/, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "executable-rule-25-verdict-content-spec-fix-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/rule-25-verdict-content-spec-fix-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_verdict_continue.txt",
>     "grep_no_bare_continue.txt",
>     "grep_version.txt",
>     "grep_last_updated.txt",
>     "git_commit_governance.txt",
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
> If the self-check prints `FAILED`, STOP — do not proceed with closeout, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23: **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: PLANNER_TEMPLATE v4.30 verdict content spec fix verified"; cd /Users/marklehn/Desktop/GitHub`. **STOP. Plan complete after this step. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification per Rule 25.**
>
> **Deposits:**
> - `bellows/knowledge/qa/rule-25-verdict-content-spec-fix-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_verdict_continue.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_no_bare_continue.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_version.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/grep_last_updated.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/git_commit_governance.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-25-verdict-content-spec-fix-2026-05-01/git_commit_bellows.txt`
