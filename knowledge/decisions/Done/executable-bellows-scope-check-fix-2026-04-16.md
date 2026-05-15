# Bellows — Scope_check Infrastructure File False Positives Fix
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-scope-check-fix-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-scope-check-fix-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-scope-check-fix-2026-04-16.md")`. Skip specialist file and glossary reads. Read the diagnostic at `bellows/knowledge/research/scope-check-infra-files-diagnostic-2026-04-16.md` (Q3 recommendation + Q5 gitignore state). Two changes: **Fix 1 — Untrack and gitignore `verdicts/ledger.jsonl`.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git rm --cached verdicts/ledger.jsonl`. Then append `verdicts/ledger.jsonl` to `.gitignore`. Verify: `git status` should show `.gitignore` as modified and `verdicts/ledger.jsonl` as deleted (from index, not from disk — the file should still exist on disk). Commit: `git add .gitignore && git commit -m "chore: untrack and gitignore verdicts/ledger.jsonl"`. **Fix 2 — Add prefix-based allowlist to scope_check in `gates.py`.** The current `SCOPE_ALLOWLIST` at `gates.py:8-12` is a list of exact basenames. Add a second constant `SCOPE_ALLOWLIST_PREFIXES` as a tuple: `SCOPE_ALLOWLIST_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")`. In `_gate_scope_check`, after the existing `if basename in SCOPE_ALLOWLIST: continue` check, add: `if any(basename.startswith(p) for p in SCOPE_ALLOWLIST_PREFIXES): continue`. This skips renamed plan files regardless of the specific plan name. The existing `SCOPE_ALLOWLIST` and its exact-basename matching remain unchanged — the prefix check is additive. **Tests:** (1) Test that `ledger.jsonl` no longer appears in scope_check results — create a mock `files_changed` list including `verdicts/ledger.jsonl` and verify it doesn't trigger a failure (this tests the gitignore path indirectly — if ledger.jsonl is untracked, `_parse_diff_stat` won't include it, but test the allowlist as defense-in-depth by also adding `"ledger.jsonl"` to `SCOPE_ALLOWLIST`). Actually — the diagnostic recommends NOT adding `ledger.jsonl` to the code allowlist since gitignore handles it. Instead test: (a) `in-progress-executable-foo.md` in files_changed does NOT trigger scope_check failure, (b) `verdict-pending-executable-bar.md` does NOT trigger, (c) `halted-executable-baz.md` does NOT trigger, (d) a real out-of-scope file like `some-random-file.py` still DOES trigger. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: scope_check prefix allowlist for plan file renames"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 by running `git --no-pager log --oneline -3` — expect two commits (gitignore + prefix allowlist). **Deliverable Verification:** (a) `ledger.jsonl` gitignored: `grep "ledger.jsonl" /Users/marklehn/Desktop/GitHub/bellows/.gitignore` — expect 1 match. (b) `ledger.jsonl` untracked: `cd /Users/marklehn/Desktop/GitHub/bellows && git ls-files verdicts/ledger.jsonl` — expect empty output (not tracked). (c) `ledger.jsonl` still exists on disk: `ls /Users/marklehn/Desktop/GitHub/bellows/verdicts/ledger.jsonl` — expect present. (d) Prefix allowlist in gates.py: `grep -n "SCOPE_ALLOWLIST_PREFIXES\|in-progress-.*verdict-pending" /Users/marklehn/Desktop/GitHub/bellows/gates.py` — expect 2+ matches. (e) Prefix check in scope_check function: `grep -n "startswith.*SCOPE_ALLOWLIST_PREFIXES\|SCOPE_ALLOWLIST_PREFIXES" /Users/marklehn/Desktop/GitHub/bellows/gates.py` — expect 2+ matches. (f) Tests exist: `grep -rn "in-progress-\|verdict-pending-\|SCOPE_ALLOWLIST_PREFIXES\|prefix" /Users/marklehn/Desktop/GitHub/bellows/tests/ --include="*.py" | grep -i "scope\|allowlist"` — expect 3+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "scope" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/scope-check-fix/pytest_targeted.txt`. Full suite: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/scope-check-fix/pytest_full.txt`. Create dir: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/scope-check-fix/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "executable-bellows-scope-check-fix-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/scope-check-fix-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/scope-check-fix/"
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
> **Deposit:** QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/scope-check-fix-qa-2026-04-16.md`. **Final:** Update PROJECT_STATUS.md — add milestone: "Scope_check false positives eliminated: ledger.jsonl untracked + gitignored, prefix allowlist added for in-progress-/verdict-pending-/halted- plan files." Move plan to Done. Commit: `"chore: QA + status for scope_check fix"`. Standard prompt feedback protocol.
>
> **STOP. Plan complete after this step.**
