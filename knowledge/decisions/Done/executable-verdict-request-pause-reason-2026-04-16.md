# Bellows — Verdict Request Pause Reason Threading
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Depends on:** `parallel-1-executable-parse-diff-stat-fix-2026-04-16.md` | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-verdict-request-pause-reason-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-verdict-request-pause-reason-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-verdict-request-pause-reason-2026-04-16.md")`. Skip specialist file and glossary reads — bellows has no specialist files and this is a targeted code change grounded in diagnostic findings. **Read first:** diagnostic findings at `bellows/knowledge/research/verdict-request-pause-reasons-2026-04-16.md` (Q1–Q5). The diagnostic recommends Option B — add an explicit `pause_reason` parameter to `post_verdict_request`. **Changes to `verdict.py`:** (1) Change signature from `def post_verdict_request(plan_path, step_number, log_path, gate_result, planner_py_decision=None)` to `def post_verdict_request(plan_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None)`. (2) Add a `**Pause Reason:** {pause_reason_label}` line to the header block, where `pause_reason_label` is a human-readable mapping: `gate_failure` → "Gate failure", `qa_checkpoint` → "QA checkpoint", `agent_verdict_request` → "Agent verdict request", `header_pause` → "Header pause_for_verdict", `auto_close_disabled` → "Auto-close disabled". (3) Replace the Gate Failures section rendering: when `pause_reason == "gate_failure"` AND `gate_result["failures"]` is non-empty, render the current `## Gate Failures` section with the bulleted failure list (this path is unchanged). For ALL other pause reasons, render `## Pause Reason` with a one-line description appropriate to the reason. The misleading `"- None (QA checkpoint — all gates passed)\n"` fallback string is REMOVED entirely — it never renders under any condition. The diagnostic Q4 sketches show the exact target output for each of the five conditions — use those as your reference. (4) Keep the existing `## Files Changed` section and the optional `## Planner.py Decision (legacy)` section unchanged. **Changes to `bellows.py`:** Both call sites of `post_verdict_request` need to pass `pause_reason=`. (A) Mid-plan pause block (~line 207): the dispatcher already knows which condition fired from the if-chain. Map each condition to its token: `not gate_result["passed"]` → `pause_reason="gate_failure"`, `gate_result["is_qa_step"]` → `pause_reason="qa_checkpoint"`, `gate_result.get("verdict_requested", {}).get("requested", False)` → `pause_reason="agent_verdict_request"`, `header_says_pause(...)` → `pause_reason="header_pause"`. The conditions are checked in priority order (gate failure > QA > agent-requested > header), so use the first matching condition. (B) Final-step pause block (~line 253): same four conditions plus `not effective_auto_close` → `pause_reason="auto_close_disabled"`. Same priority order, with `auto_close_disabled` as the lowest-priority (last-matched) reason. **Tests:** Add tests in `tests/test_verdict.py`: (1) test each of the five `pause_reason` values produces the correct section header and body text in the output file, (2) test that `gate_failure` with populated failures list produces the `## Gate Failures` bulleted list, (3) test that the old fallback string "None (QA checkpoint — all gates passed)" does NOT appear in any output. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "feat: thread pause_reason through verdict requests"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed by running `git --no-pager log --oneline -1` and confirming the commit message matches "feat: thread pause_reason through verdict requests". If not, stop and report. **Deliverable Verification:** (a) Grep for new parameter: `grep -n "pause_reason" /Users/marklehn/Desktop/GitHub/bellows/verdict.py` — expect 3+ matches (signature + mapping + rendering logic). (b) Confirm old fallback removed: `grep -n "QA checkpoint" /Users/marklehn/Desktop/GitHub/bellows/verdict.py` — expect 0 matches (the misleading string is gone). (c) Confirm both call sites pass pause_reason: `grep -n "pause_reason=" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 2+ matches (mid-plan + final-step). (d) Confirm tests exist: `grep -rn "def test.*pause_reason\|pause_reason" /Users/marklehn/Desktop/GitHub/bellows/tests/test_verdict.py` — expect 5+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_verdict.py -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-pause-reason/pytest_targeted.txt`. All verdict tests must pass. **Deposit:** write QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-pause-reason-qa-2026-04-16.md`. Create evidence directory first: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-pause-reason/`. **Rule 20 self-check:** Run the following Python block and include its literal output in the QA report:
>
> ```python
> import os, sys
> plan_slug = "executable-verdict-request-pause-reason-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-pause-reason-qa-2026-04-16.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-pause-reason/"
> required_evidence_files = ["pytest_targeted.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             else:
>                 if cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> **Final:** Update PROJECT_STATUS.md — add completed milestone: "Verdict requests now include `pause_reason` field identifying which of five conditions triggered the pause. Misleading 'QA checkpoint — all gates passed' fallback removed." Then move this plan to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-verdict-request-pause-reason-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-verdict-request-pause-reason-2026-04-16.md")`. Commit: `"chore: QA + status update for verdict pause reason threading"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Plan complete after this step.**
