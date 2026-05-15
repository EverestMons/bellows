# Bellows — Cross-Project Verdict Scoping Fix
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-bellows-verdict-scoping-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/parallel-1-executable-bellows-verdict-scoping-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-bellows-verdict-scoping-2026-04-16.md")`. Skip specialist file and glossary reads. Read the diagnostic at `bellows/knowledge/research/cross-project-verdict-queue-diagnostic-2026-04-16.md` (Q3 matching logic, Q6 Option B fix). **Task:** Fix `_consume_verdicts` in `bellows.py` to scope its plan search by project. Currently it iterates ALL `watched_projects` directories with substring matching (`plan_slug in pname`), which could match the wrong project's plan on a slug collision. Two changes: **(1) Scope by reading the pending request file.** After extracting `plan_slug` and `step_number` from the resolved verdict filename, read the corresponding pending file at `BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"`. Parse the `**Plan:**` field to extract the absolute plan path. Derive the project's decisions directory from that path (`pathlib.Path(plan_path_from_request).parent`). If the pending file exists and the Plan field is parseable, search ONLY that directory. If the pending file is missing or unparseable, fall back to searching all watched_projects (current behavior). **(2) Add `break` after processing a match.** Inside the inner `for pname in os.listdir(decisions_path)` loop, after the verdict is processed (continue-to-done, continue-to-step, or stop), add `break` to prevent double-consumption if multiple files match the same slug substring. **Tests:** (1) Test that `_consume_verdicts` scopes to the correct project directory when the pending file contains a valid `**Plan:**` field — mock a pending file with a known plan path, verify only that project's directory is searched. (2) Test that `_consume_verdicts` falls back to all watched_projects when the pending file is missing. (3) Test that only one plan is consumed per verdict (break behavior) — create two `verdict-pending-*` files with overlapping slugs in different directories, verify only the correct one is consumed. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: scope _consume_verdicts to correct project via pending file Plan field"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed. **Deliverable Verification:** (a) Scoping logic: `grep -n "Plan:" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | grep -i "pending\|scoped\|plan_path_from"` — expect 2+ matches. (b) Break added: `grep -n "break.*match\|break.*consumed\|break  #" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 1+ match inside `_consume_verdicts`. (c) Tests: `grep -rn "scope\|scoped\|fallback\|break.*verdict" /Users/marklehn/Desktop/GitHub/bellows/tests/ --include="*.py"` — expect 3+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "verdict or consume or scope" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-scoping-fix/pytest_targeted.txt`. Full suite: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-scoping-fix/pytest_full.txt`. Create dir: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-scoping-fix/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "parallel-1-executable-bellows-verdict-scoping-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-scoping-fix-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/verdict-scoping-fix/"
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
> **Deposit:** QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-scoping-fix-qa-2026-04-16.md`. **Final:** Update PROJECT_STATUS.md. Move plan to Done. Commit: `"chore: QA + status for verdict scoping fix"`. Standard prompt feedback protocol.
>
> **STOP. Plan complete after this step.**
