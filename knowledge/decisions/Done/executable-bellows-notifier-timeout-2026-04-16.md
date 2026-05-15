# Bellows — Notifier Timeout + Heartbeat + Dead Code Cleanup
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-notifier-timeout-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-notifier-timeout-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-notifier-timeout-2026-04-16.md")`. Skip specialist file and glossary reads. Read the diagnostic at `bellows/knowledge/research/post-plan-hang-diagnostic-2026-04-16.md` (Q6 fix proposals). Three changes: **Fix 1 (CRITICAL) — Add timeout to `notifier.push()`.** In `notifier.py`, change `response = requests.post(PUSHOVER_API_URL, data=payload)` to `response = requests.post(PUSHOVER_API_URL, data=payload, timeout=(5, 10))`. This gives a 5-second connect timeout and 10-second read timeout. `requests.Timeout` is a subclass of `requests.RequestException` which is already caught by the existing try/except — no additional error handling needed. This single change fixes the root cause of the terminal freeze. **Fix 2 — Add heartbeat to main loop.** In `bellows.py`, in the `start()` method's `while True` loop, add a heartbeat print every 60 seconds: track `last_heartbeat = time.time()` before the loop, then inside the loop add `if time.time() - last_heartbeat >= 60: print(f"Bellows: heartbeat — {datetime.now().strftime('%H:%M:%S')}"); last_heartbeat = time.time()`. Import `datetime` at the top if not already imported. This is a canary — if the heartbeat stops, the main thread is hung. **Fix 3 — Remove dead code at bellows.py lines 306-313.** The diagnostic confirmed the stranded-check block and its `notifier.push`/`notifier.notify_complete` calls are unreachable (the two `if` conditions above are logical complements — execution always returns before reaching this block). Remove the dead code. Do NOT remove the preceding auto-close block or the verdict-pending block — only the unreachable stranded-check after them. Read the diagnostic Q1 "Dead code note" for the exact line range confirmation. **Tests:** (1) Test that `notifier.push` passes `timeout=(5, 10)` to `requests.post` — mock `requests.post` and assert the `timeout` kwarg. (2) Test that a `requests.Timeout` exception is handled gracefully (returns False, no crash) — mock `requests.post` to raise `requests.Timeout`. (3) Verify the dead code block is gone — grep for the specific string or function call that was in the removed block (e.g., `_is_plan_stranded` if that was the function, or the specific print message) and assert 0 matches in bellows.py. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: add timeout to notifier, heartbeat to main loop, remove dead code"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed by running `git --no-pager log --oneline -1`. **Deliverable Verification:** (a) Timeout in notifier: `grep -n "timeout" /Users/marklehn/Desktop/GitHub/bellows/notifier.py` — expect 1+ match with `(5, 10)`. (b) Heartbeat in main loop: `grep -n "heartbeat" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 2+ matches (variable + print). (c) Dead code removed: `grep -n "_is_plan_stranded\|STRANDED" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 0 matches for the removed block's identifiers (the function definition may still exist if used elsewhere — check that the CALL SITE is gone, not necessarily the function). (d) Tests exist: `grep -rn "timeout.*5.*10\|Timeout\|heartbeat\|stranded.*dead" /Users/marklehn/Desktop/GitHub/bellows/tests/ --include="*.py"` — expect 3+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "timeout or heartbeat or notifier or dead_code" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/notifier-timeout-fix/pytest_targeted.txt`. Full suite: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/notifier-timeout-fix/pytest_full.txt`. Create dir: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/notifier-timeout-fix/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "executable-bellows-notifier-timeout-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/notifier-timeout-fix-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/notifier-timeout-fix/"
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
> **Deposit:** QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/notifier-timeout-fix-qa-2026-04-16.md`. **Final:** Update PROJECT_STATUS.md — add milestone: "Notifier timeout fix: requests.post now has (5, 10) timeout. Heartbeat added to main loop. Dead code removed from run_plan." Move plan to Done. Commit: `"chore: QA + status for notifier timeout fix"`. Standard prompt feedback protocol.
>
> **STOP. Plan complete after this step.**
