# bellows — Inactivity Timeout Bump (300s → 1800s)
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

**Test Scope: targeted** — config-only change, no production code, no test execution beyond the existing config-load tests (if any). One-line edit to `bellows/config.json` plus a CEO restart.

**Background.** The activity-timeout diagnosis 2026-05-01 set `step_inactivity_timeout_seconds: 300` based on event-cadence analysis of 20 longest post-stream-JSON logs (P95=26s, P99=119s, longest=743s). That corpus was biased toward agents that completed and emitted output — silent-reasoning gaps from agents that took 500s+ to think between tool calls were not represented because those agents never produced completed logs. The 300s threshold killed today's call-site-gap diagnostic at 431s while the SA was reasoning between tool calls (last-output gaps reached 291s before kill). The kill destroyed all in-flight work — no findings file, no commit, no Output Receipt.

**Fix.** Raise `step_inactivity_timeout_seconds` from 300 to 1800 (30 minutes). At this threshold, an inactivity kill genuinely indicates a hung or runaway process, not deep reasoning. The wall-clock cap (`step_timeout_seconds: 2400` = 40 min) is unchanged — runaway-cost protection remains.

**Out of scope.** A soft/hard-threshold split (warn at one threshold, kill at another) is the structural fix. Deferred to BACKLOG. This plan is the operational unblock.

## How to Run This Plan

Paste the bootstrap into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After Step 1 reports Complete, CEO confirms ("ok") to advance to Step 2. After Step 2, CEO must restart Bellows to load the new config.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-inactivity-timeout-bump-1800s-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-inactivity-timeout-bump-1800s-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-inactivity-timeout-bump-1800s-2026-05-01.md")`.
>
> You are the Bellows Developer. Skip specialist file and glossary reads — this is a one-line config edit. Use the `Edit` tool (NOT `Desktop Commander:edit_block` — not available in Claude Code). Edit `bellows/config.json`: replace the verbatim line `  "step_inactivity_timeout_seconds": 300,` with `  "step_inactivity_timeout_seconds": 1800,` (preserve the leading two-space indent and trailing comma exactly). Verify with `cat bellows/config.json | grep -n step_inactivity_timeout_seconds` — expect output showing the new value 1800. Verify the JSON still parses with `python3 -c "import json; json.load(open('bellows/config.json')); print('valid')"` — expect output `valid`. Deposit a dev log at `bellows/knowledge/development/inactivity-timeout-bump-dev-log-2026-05-01.md` containing: (a) the verbatim before-and-after line, (b) the grep output, (c) the json.load verification output, (d) note that CEO restart is required to load the new value into the running daemon. Use the canonical Python file write pattern: `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/inactivity-timeout-bump-dev-log-2026-05-01.md", "w") as f: f.write(content)` where content is a triple-quoted string defined before the open call. Commit with: `cd /Users/marklehn/Desktop/GitHub && git add bellows/config.json bellows/knowledge/development/inactivity-timeout-bump-dev-log-2026-05-01.md && git commit -m "config: raise step_inactivity_timeout_seconds 300→1800 (BACKLOG operational unblock)"`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md` and commit with: `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "docs: prompt feedback — bellows DEV inactivity timeout bump"`.
>
> **Deposits:**
> - `bellows/config.json`
> - `bellows/knowledge/development/inactivity-timeout-bump-dev-log-2026-05-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/development/inactivity-timeout-bump-dev-log-2026-05-01.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA Agent. Skip specialist file and glossary reads — this is a config verification task. **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. For each listed deliverable, verify it exists on disk and contains the described change. Produce a verification table: `| Deliverable | Expected | Status | Evidence |`. If ANY item fails, attempt to fix or flag as blocked.
>
> **Run six verification checks** and pipe each command's literal output to the corresponding evidence file. Create the evidence directory first: `mkdir -p bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01`.
>
> Check 1: `grep -n step_inactivity_timeout_seconds bellows/config.json > bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/grep_config.txt` — expect line shows value 1800.
>
> Check 2: `python3 -c "import json; c=json.load(open('bellows/config.json')); print(c['step_inactivity_timeout_seconds'])" > bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/json_load.txt` — expect output `1800`.
>
> Check 3: `python3 -c "import json; c=json.load(open('bellows/config.json')); print(c['step_timeout_seconds'])" > bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/wall_clock_unchanged.txt` — expect output `2400` (verifies wall-clock cap was NOT touched).
>
> Check 4: `git --no-pager log -1 --name-only -- bellows/config.json > bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/git_log_config.txt` — expect commit message includes "raise step_inactivity_timeout_seconds 300→1800" and file list shows `bellows/config.json`.
>
> Check 5: `git --no-pager diff HEAD~1 HEAD -- bellows/config.json > bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/git_diff_config.txt` — expect diff shows exactly one line removed (`"step_inactivity_timeout_seconds": 300,`) and one line added (`"step_inactivity_timeout_seconds": 1800,`), no other changes.
>
> Check 6: `ls -la bellows/knowledge/development/inactivity-timeout-bump-dev-log-2026-05-01.md > bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/dev_log_exists.txt` — expect file exists with non-zero size.
>
> Deposit the QA report at `bellows/knowledge/qa/inactivity-timeout-bump-qa-2026-05-01.md` using the canonical Python file write pattern with a verification table citing each evidence file path in the Evidence column. Then run the mandatory Rule 20 self-check Python block:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-inactivity-timeout-bump-1800s-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/inactivity-timeout-bump-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_config.txt",
>     "json_load.txt",
>     "wall_clock_unchanged.txt",
>     "git_log_config.txt",
>     "git_diff_config.txt",
>     "dev_log_exists.txt",
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
> Include the literal stdout of the self-check in the QA report. If the self-check fails, STOP — do NOT update PROJECT_STATUS.md, do NOT advance, report failure to CEO. If the self-check passes, proceed.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — add a completed milestone entry under "Recent Activity" (or equivalent section) summarizing: "2026-05-01: Raised `step_inactivity_timeout_seconds` 300 → 1800 (operational unblock for SA cross-referencing tasks; wall-clock cap unchanged at 2400s). CEO restart required." Use the `Edit` tool with a verbatim anchor — read PROJECT_STATUS.md first to identify the exact existing line to anchor the insert. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit with: `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/inactivity-timeout-bump-qa-2026-05-01.md bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/ bellows/PROJECT_STATUS.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: inactivity timeout bump verified (300→1800)"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/inactivity-timeout-bump-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-inactivity-timeout-bump-1800s-2026-05-01/`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
