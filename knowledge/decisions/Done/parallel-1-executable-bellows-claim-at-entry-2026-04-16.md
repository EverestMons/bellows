# Bellows — Bellows-Side Plan Claiming Fix (Eliminate Duplicate Runs)
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-bellows-claim-at-entry-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/parallel-1-executable-bellows-claim-at-entry-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-bellows-claim-at-entry-2026-04-16.md")`. Skip specialist file and glossary reads. Read the diagnostic at `bellows/knowledge/research/rescan-duplicate-runs-diagnostic-2026-04-16.md` (Q4 root cause, Q5 Fix 1). **Root cause:** Plans are claimed by the AGENT via `shutil.move` inside the step prompt, but the ORIGINAL file stays in `decisions/` until the agent executes the move instruction. If Bellows restarts between dispatch and agent claim, `_seen` is lost and the original file is re-dispatched. The agent's claim is also redundant — Bellows can claim the file itself before passing it to the runner. **Fix:** Move the plan to `in-progress-` at the START of `run_plan`, before calling `runner.run_step`. **(1) At the top of `run_plan`, after computing `plan_dir`, `plan_filename`, and `inprogress_path`:** add `if not plan_filename.startswith("in-progress-"):` then `shutil.move(plan_path, inprogress_path)` and `plan_path = inprogress_path`. This makes the claim atomic from Bellows' perspective — the file disappears from the runnable set before any agent code runs. **(2) Handle the case where `plan_path` is already `in-progress-`** (e.g., on resume from verdict). The `if not plan_filename.startswith("in-progress-")` guard handles this — if already claimed, skip the move. **(3) The agent's own claim instruction in the plan template becomes a no-op.** The `shutil.move` in the step prompt will find the source file doesn't exist (already moved by Bellows) and raise `FileNotFoundError`. The agent's claim instruction should be wrapped in a try/except or the agent should check if the file exists before moving. **However** — changing every plan template is impractical. Instead, make the Bellows-side claim idempotent: if the inprogress_path already exists (Bellows already claimed it), don't move again. And update the `run_plan` bootstrap prompt generation to reference the `in-progress-` path so the agent reads from the correct location. Check: does `run_plan` pass `plan_path` to `runner.run_step` as part of the bootstrap prompt? If yes, ensure it passes the updated `inprogress_path` after the move. **(4) Verify that `is_runnable_plan("in-progress-*.md")` returns False** (it should already — the function checks for `executable-` and `diagnostic-` prefixes). If it does, the claimed file is invisible to rescans and watchdog events. **Tests:** (1) Test that `run_plan` moves the file to `in-progress-` before calling `runner.run_step` — mock `runner.run_step`, verify the original file no longer exists and `in-progress-` file does exist when the mock is called. (2) Test that `run_plan` with an already-`in-progress-` path skips the move (idempotent). (3) Test that `is_runnable_plan("in-progress-executable-foo.md")` returns False (regression guard). (4) Test that the bootstrap prompt uses the `in-progress-` path, not the original path. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: Bellows claims plan at run_plan entry — eliminates orphan-original duplicate dispatch"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed. **Deliverable Verification:** (a) Claim-at-entry logic: `grep -n "in-progress-.*shutil\|shutil.*in-progress\|startswith.*in-progress" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | head -5` — expect 2+ matches near the top of `run_plan`. (b) Idempotent guard: `grep -n "startswith.*in-progress" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect the `if not` guard. (c) Bootstrap uses updated path: `grep -n "inprogress_path\|plan_path.*bootstrap" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect the bootstrap prompt to reference the moved path. (d) Tests: `grep -rn "claim.*entry\|in-progress.*before\|orphan\|idempotent" /Users/marklehn/Desktop/GitHub/bellows/tests/ --include="*.py"` — expect 4+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "claim or orphan or in_progress or idempotent or runnable" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/claim-at-entry-fix/pytest_targeted.txt`. Full suite: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/claim-at-entry-fix/pytest_full.txt`. Create dir: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/claim-at-entry-fix/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "parallel-1-executable-bellows-claim-at-entry-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/claim-at-entry-fix-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/claim-at-entry-fix/"
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
> **Deposit:** QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/claim-at-entry-fix-qa-2026-04-16.md`. **Final:** Update PROJECT_STATUS.md. Move plan to Done. Commit: `"chore: QA + status for claim-at-entry fix"`. Standard prompt feedback protocol.
>
> **STOP. Plan complete after this step.**
