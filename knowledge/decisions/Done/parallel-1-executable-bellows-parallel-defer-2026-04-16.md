# Bellows — Parallel Group Deferred Dispatch Fix
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-bellows-parallel-defer-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/parallel-1-executable-bellows-parallel-defer-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-bellows-parallel-defer-2026-04-16.md")`. Skip specialist file and glossary reads. Read the diagnostic at `bellows/knowledge/research/parallel-group-collection-diagnostic-2026-04-16.md` (Q4 root cause, Q6 Option b). **Root cause:** When two `parallel-1-` files are deposited via rapid sequential `Filesystem:move_file` calls, the watchdog `on_created` fires per-file. `_handle` calls `collect_group` which only sees what's on disk at that instant — the second sibling hasn't landed yet. Result: each file is dispatched as a 1-plan "group" instead of being collected together. **Fix:** Defer parallel dispatch from the `on_created` path to the rescan tick. **(1) Add `_pending_groups` dict to `PlanHandler.__init__`.** Type: `dict[str, float]` mapping group prefix (e.g., `"parallel-1"`) to first-seen timestamp. Initialize empty. **(2) Modify `_handle` for parallel plans.** When `extract_parallel_group(filename)` returns a group AND the call is from `on_created`/`on_modified` (not from rescan): instead of calling `collect_group` + `handle_parallel_group`, add the group to `_pending_groups` with `time.time()` if not already present, add the path to `_seen`, and return WITHOUT dispatching. The key insight: `_handle` is called from both watchdog events AND from `_rescan`. We need to distinguish these. Simplest approach: add a `from_rescan=False` parameter to `_handle`. `_rescan` calls `handler._handle(full_path, from_rescan=True)`. Watchdog's `on_created`/`on_modified` call `self._handle(event.src_path)` (default `from_rescan=False`). When `from_rescan=True` AND a pending group exists, proceed with collect_group + dispatch as normal. **(3) Modify `_rescan` to dispatch pending groups.** After calling `_consume_verdicts`, before the per-file scan loop, iterate `_pending_groups`. For each group where `time.time() - first_seen > 5` (5-second settle window): call `collect_group` for the group across all watched_projects directories, dispatch via `handle_parallel_group`, remove from `_pending_groups`. The 5-second settle window gives siblings time to land. Plans deposited >5s apart are considered separate groups (which is correct — the Planner stages them atomically). **(4) Non-parallel plans are unchanged.** When `extract_parallel_group` returns None, `_handle` dispatches immediately via `handle_new_plan` regardless of `from_rescan`. **Tests:** (1) Test that `_handle` with a parallel-prefixed file from watchdog (from_rescan=False) adds to `_pending_groups` but does NOT dispatch. (2) Test that `_rescan` dispatches pending groups after the settle window. (3) Test that `_rescan` does NOT dispatch pending groups within the settle window. (4) Test that non-parallel plans still dispatch immediately from `_handle`. (5) Test that two parallel siblings deposited before the settle window expires are collected into one group. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: defer parallel group dispatch to rescan tick with 5s settle window"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed. **Deliverable Verification:** (a) `_pending_groups` field: `grep -n "_pending_groups" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 3+ matches (init, add, check in rescan). (b) `from_rescan` parameter: `grep -n "from_rescan" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 4+ matches (parameter def, two callers, condition check). (c) Settle window: `grep -n "settle\|5.*second\|time.time.*pending" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 2+ matches. (d) Tests: `grep -rn "pending_group\|from_rescan\|settle\|defer" /Users/marklehn/Desktop/GitHub/bellows/tests/ --include="*.py"` — expect 5+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "parallel or group or defer or settle or pending_group" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parallel-defer-fix/pytest_targeted.txt`. Full suite: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parallel-defer-fix/pytest_full.txt`. Create dir: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parallel-defer-fix/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "parallel-1-executable-bellows-parallel-defer-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/parallel-defer-fix-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parallel-defer-fix/"
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
> **Deposit:** QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/parallel-defer-fix-qa-2026-04-16.md`. **Final:** Update PROJECT_STATUS.md. Move plan to Done. Commit: `"chore: QA + status for parallel defer fix"`. Standard prompt feedback protocol.
>
> **STOP. Plan complete after this step.**
