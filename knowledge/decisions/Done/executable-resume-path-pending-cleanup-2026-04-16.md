# Bellows — Resume Path Fix + Pending File Cleanup
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-resume-path-pending-cleanup-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-resume-path-pending-cleanup-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-resume-path-pending-cleanup-2026-04-16.md")`. Skip specialist file and glossary reads — bellows has no specialist files and this is a targeted code change grounded in diagnostic findings. **Read first:** diagnostic findings at `bellows/knowledge/research/resume-path-pending-cleanup-diagnostic-2026-04-16.md` (Q1–Q6). **Two bugs, one plan. Do NOT touch `gates.py` — there is a known separate bug there (agent self-request filename mismatch) that is out of scope for this plan.** **Bug 1 fix — Resume from correct step.** The diagnostic confirmed the call chain: `_consume_verdicts` → `handle_new_plan(path)` → `_run_tracked(path)` → `run_plan(path, config, response_server)`. None of these pass step information. `run_plan` always builds a Step 1 bootstrap. Fix by threading `resume_step` through the chain: **(a) `run_plan` signature:** change to `def run_plan(plan_path: str, config: dict, response_server: server.ResponseServer, resume_step: Optional[int] = None)`. When `resume_step` is not None: (i) override the bootstrap prompt to `f"Read the plan at {plan_path}. Execute Step {resume_step}. After completing Step {resume_step}, STOP and wait for my confirmation."`, (ii) after the first `runner.run_step` call, set `current_step = resume_step` instead of `current_step = 1`. When `resume_step` is None, existing behavior is unchanged. **(b) `_run_tracked` signature:** add `resume_step: Optional[int] = None`, pass through: `run_plan(path, self.config, self.response_server, resume_step=resume_step)`. **(c) `handle_new_plan` signature:** add `resume_step: Optional[int] = None`, pass through: `t = threading.Thread(target=self._run_tracked, args=(path,), kwargs={"resume_step": resume_step}, daemon=True)`. **(d) `_consume_verdicts` call site** (the mid-plan continue branch, diagnostic Q1 showed lines 529–535): change `self.handle_new_plan(inprogress_path)` to `self.handle_new_plan(inprogress_path, resume_step=step_number + 1)`. The continue-to-done branch and the stop branch are unchanged — they don't dispatch. **(e) `handle_parallel_group`:** does NOT need changes — it only handles fresh plans from the watcher, never resumes. Leave it alone. **Bug 2 fix — Clean up pending verdict request files.** The diagnostic confirmed `_consume_verdicts` never deletes pending files and the filename is reliably reconstructable as `verdict-request-{plan_slug}-step-{step_number}.md`. Add cleanup AFTER the per-verdict branching logic (after the continue-to-done / continue-to-step / stop branches) and BEFORE or AFTER the `processed_path` shutil.move. Use: `pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"` then `if pending_file.exists(): pending_file.unlink()`. This runs for ALL verdict types (continue, stop) since the pending file is always stale after consumption. **Tests:** Add tests in `tests/test_bellows.py` (or a new `tests/test_resume.py`): (1) test that `run_plan` with `resume_step=2` builds a bootstrap prompt containing "Step 2" and NOT "Step 1" — mock `runner.run_step` and capture the prompt argument, (2) test that `_consume_verdicts` with a continue verdict on step 1 of a 2-step plan calls `handle_new_plan` with `resume_step=2` — mock `handle_new_plan` and check kwargs, (3) test that after `_consume_verdicts` processes a verdict, the corresponding `verdicts/pending/verdict-request-*` file is deleted, (4) test that pending cleanup is safe when the pending file doesn't exist (no crash on missing file). **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: resume from correct step after verdict + clean up pending files"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed by running `git --no-pager log --oneline -1` and confirming the commit message matches "fix: resume from correct step after verdict + clean up pending files". If not, stop and report. **Deliverable Verification:** (a) `resume_step` parameter exists in `run_plan`: `grep -n "resume_step" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 4+ matches (signature + bootstrap override + current_step assignment + _consume_verdicts call). (b) `resume_step` threaded through `_run_tracked` and `handle_new_plan`: `grep -n "resume_step" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | wc -l` — expect ≥6 (run_plan sig + run_plan body + _run_tracked sig + _run_tracked call + handle_new_plan sig + _consume_verdicts call). (c) Pending cleanup exists: `grep -n "pending_file\|unlink" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 2+ matches. (d) `gates.py` NOT modified: `git --no-pager diff HEAD~1 HEAD --name-only | grep gates` — expect no output. (e) Tests exist: `grep -rn "resume_step\|pending.*unlink\|pending.*cleanup" /Users/marklehn/Desktop/GitHub/bellows/tests/` — expect 4+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "resume or pending" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/resume-pending-fix/pytest_targeted.txt`. All resume/pending tests must pass. Also run full test suite to check for regressions: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/resume-pending-fix/pytest_full.txt`. **Deposit:** write QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/resume-pending-fix-qa-2026-04-16.md`. Create evidence directory first: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/resume-pending-fix/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "executable-resume-path-pending-cleanup-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/resume-pending-fix-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/resume-pending-fix/"
> required_evidence_files = ["pytest_targeted.txt", "pytest_full.txt"]
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
> **Final:** Update PROJECT_STATUS.md — add completed milestone: "Resume-from-correct-step fix: mid-plan verdict continue now dispatches Step N+1 instead of restarting from Step 1. Pending verdict request files cleaned up after consumption." Then move this plan to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-resume-path-pending-cleanup-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-resume-path-pending-cleanup-2026-04-16.md")`. Commit: `"chore: QA + status update for resume path fix"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Plan complete after this step.**
