# Bellows — Close Activity Timeout BACKLOG + Tighten Inactivity Config
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

**Test scope justification:** Config-only change to `bellows/config.json` (one new key) + markdown edit to `bellows/knowledge/BACKLOG.md`. No production Python code touched. Targeted scope runs `tests/test_bellows.py` and `tests/test_runner.py` — the two test files that exercise config lookup and timeout enforcement — as regression sanity. Full suite not justified.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After Step 1, the agent STOPS and waits for CEO confirmation (`ok`) before proceeding to Step 2. After Step 2, the agent STOPS — Bellows posts a verdict request, the Planner verifies and authorizes the Done/ move.

Bootstrap prompt:

```
Read the plan at bellows/knowledge/decisions/executable-close-activity-timeout-backlog-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-close-activity-timeout-backlog-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-close-activity-timeout-backlog-2026-05-01.md")`. **You are the Bellows Developer. Skip specialist file and glossary reads — this is a config + governance edit task, no domain interpretation needed.** **Background.** The 2026-05-01 SA diagnostic at `bellows/knowledge/research/activity-based-timeout-diagnosis-2026-05-01.md` confirmed the inactivity-based timeout was already shipped 2026-04-17 (QA report at `bellows/knowledge/qa/activity-timeout-qa-2026-04-17.md` confirms via 8 grep checks). The BACKLOG entry was stale. Diagnostic also recommended tightening the inactivity threshold from current 2400s (40 min) to 300s (5 min) based on empirical P99 inter-event gap of 119.5s and longest legitimate run of 743s (12.4m). **Edit 1 — `bellows/config.json`.** Add a new top-level key `"step_inactivity_timeout_seconds": 300`. Place it adjacent to the existing `"step_timeout_seconds"` key for readability. Do NOT remove or modify `"step_timeout_seconds"` — `bellows.py` uses it as a fallback per the chain `config.get("step_inactivity_timeout_seconds", config.get("step_timeout_seconds", 300))`. Both keys remain valid; the new one takes precedence. **Edit 2 — `bellows/knowledge/BACKLOG.md`.** The Open section contains the entry beginning with `- 2026-04-17: activity-based timeout — runner.py uses a fixed timeout (now 1200s)`. Use edit_block to remove it from Open (delete the entire bullet including the trailing blank line). In the Closed section, insert a new closure entry at the top (immediately after the `## Closed` header and its blank line, before the existing `**Closed 2026-05-01 (hygiene)**` entry). The new entry uses verbatim text: `- **Closed 2026-05-01:** BACKLOG \`2026-04-17: activity-based timeout\`. The inactivity-based timeout was already shipped 2026-04-17 via \`executable-activity-timeout-2026-04-17\` — QA report at \`bellows/knowledge/qa/activity-timeout-qa-2026-04-17.md\` confirms via 8 grep checks (subprocess.Popen replacing subprocess.run, threading for concurrent stream reads, last_output_time reset on every stdout line, proc.kill on timeout, stderr_partial in error dict, step_inactivity_timeout_seconds config lookup with backward-compat fallback, hard wall-clock cap via timeout*10). BACKLOG entry was stale — never closed when the work landed. Diagnostic at \`bellows/knowledge/research/activity-based-timeout-diagnosis-2026-05-01.md\` audited current state, ran empirical event-cadence analysis on 20 longest post-stream-JSON logs (P50=4.0s, P90=16.8s, P95=26.0s, P99=119.5s, longest run=743s/12.4m, zero timeout kills in 100-log corpus), and recommended tightening the inactivity threshold from 2400s to 300s. Config tightened: \`step_inactivity_timeout_seconds: 300\` added to \`bellows/config.json\` (5 min inactivity, 50 min wall-clock cap via existing \`timeout * 10\` formula). REMINDER: restart Bellows to load new config.` **Verify edits.** After both edits, run `python3 -c "import json; c = json.load(open('bellows/config.json')); print(c.get('step_inactivity_timeout_seconds'))"` and confirm output is `300`. Run `grep -c "Closed 2026-05-01:.*activity-based timeout" bellows/knowledge/BACKLOG.md` and confirm output is `1`. Run `grep -c "^- 2026-04-17: activity-based timeout" bellows/knowledge/BACKLOG.md` and confirm output is `0` (entry removed from Open). **Deposit a dev log** at `bellows/knowledge/development/close-activity-timeout-backlog-2026-05-01.md` documenting: files modified, exact diff summary (1 line added to config.json, 1 entry moved Open→Closed in BACKLOG.md), the three verification commands run and their outputs, and the Output Receipt with Status: Complete. Use the canonical Python file write pattern (`with open(...) as f: f.write(content)` after defining content as triple-quoted string) — NO heredoc. **Commit.** Single commit: `chore: close BACKLOG 2026-04-17 activity-based timeout, tighten inactivity config to 300s`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/development/close-activity-timeout-backlog-2026-05-01.md`
> - `bellows/config.json`
> - `bellows/knowledge/BACKLOG.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/close-activity-timeout-backlog-2026-05-01.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **You are the Bellows QA. Skip specialist file and glossary reads — this is a deliverable verification + targeted regression task, no domain interpretation needed.** **FIRST — Deliverable Verification.** Read the prior DEV step's Output Receipt "Files Created or Modified (Code)" list. For EVERY listed file, verify the change exists. Produce a verification table with this exact column structure: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Required rows: (1) `step_inactivity_timeout_seconds` key in config.json — expected: key present with value 300 — evidence: pipe `python3 -c "import json; c = json.load(open('bellows/config.json')); print(c.get('step_inactivity_timeout_seconds'))"` output to `bellows/knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/config_key_value.txt`; (2) `step_timeout_seconds` key still present in config.json (backward-compat preserved) — expected: key still present — evidence: pipe `grep -c "step_timeout_seconds" bellows/config.json` output to `bellows/knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/config_backcompat_check.txt`, expect `>= 1`; (3) BACKLOG Open section no longer contains the 2026-04-17 entry — expected: 0 matches — evidence: pipe `grep -c "^- 2026-04-17: activity-based timeout" bellows/knowledge/BACKLOG.md` output to `bellows/knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/backlog_open_removed.txt`, expect `0`; (4) BACKLOG Closed section contains the new closure entry at the top — expected: 1 match — evidence: pipe `grep -c "Closed 2026-05-01:.*activity-based timeout" bellows/knowledge/BACKLOG.md` output to `bellows/knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/backlog_closed_added.txt`, expect `1`; (5) Commit landed with descriptive message — expected: matching commit in `git --no-pager log -1 --oneline` — evidence: pipe `git --no-pager log -1 --oneline` output to `bellows/knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/git_log.txt`. If ANY row is ❌, attempt to fix (re-run the edit, re-commit) before proceeding. If unfixable, stop and report to CEO — do NOT mark the plan complete. **Targeted regression — `tests/test_bellows.py` and `tests/test_runner.py`.** Run `cd bellows && python3 -m pytest tests/test_bellows.py tests/test_runner.py -v 2>&1 | tee knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/pytest_targeted.txt`. Expected: prior baseline tests pass; the 1 known pre-existing failure `test_run_step_timeout` (referenced in PROJECT_STATUS.md as unrelated to this work) MAY still fail and that does not block close — note it explicitly in the QA report if it appears. NO new failures introduced. **QA report.** Deposit at `bellows/knowledge/qa/close-activity-timeout-backlog-qa-2026-05-01.md`. Include the verification table, the test result summary, the literal stdout of the Rule 20 self-check, and an Output Receipt. Use the canonical Python file write pattern — NO heredoc. **Final.** Update `PROJECT_STATUS.md` — add a Completed milestone entry under the Completed section, top of list, with verbatim text: `- 2026-05-01: BACKLOG \`2026-04-17: activity-based timeout\` closed via executable-close-activity-timeout-backlog-2026-05-01. Diagnostic at knowledge/research/activity-based-timeout-diagnosis-2026-05-01.md confirmed the inactivity-based timeout was already shipped 2026-04-17 (QA at knowledge/qa/activity-timeout-qa-2026-04-17.md). Empirical event-cadence analysis on 20 longest post-stream-JSON logs justified tightening step_inactivity_timeout_seconds from 2400s to 300s. Pure config change, no code modified. REMINDER: restart Bellows daemon to load new config.` Use edit_block to insert the new line immediately after the existing `**Last Updated:** 2026-05-01` header line and the `## Status: Phase 1 Complete — Live` line, in the Completed section. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **STOP.** Do NOT move this plan to Done. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes. Final commit message: `chore: QA + project status close for activity-timeout BACKLOG`. **Deposits:**
> - `bellows/knowledge/qa/close-activity-timeout-backlog-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-close-activity-timeout-backlog-2026-05-01/`
> - `bellows/PROJECT_STATUS.md`
>
> **Mandatory Rule 20 self-check** (run AFTER QA report is written, BEFORE final commit):
>
> ```python
> import os, sys
> plan_slug = "executable-close-activity-timeout-backlog-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/close-activity-timeout-backlog-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "config_key_value.txt",
>     "config_backcompat_check.txt",
>     "backlog_open_removed.txt",
>     "backlog_closed_added.txt",
>     "git_log.txt",
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
