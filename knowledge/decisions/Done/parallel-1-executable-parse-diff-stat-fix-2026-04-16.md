# Bellows — `_parse_diff_stat` Option B Fix
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-parse-diff-stat-fix-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/parallel-1-executable-parse-diff-stat-fix-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-parse-diff-stat-fix-2026-04-16.md")`. Skip specialist file and glossary reads — bellows has no specialist files and this is a targeted function replacement. **Background:** Diagnostic findings at `bellows/knowledge/research/bellows-parse-diff-stat-audit-2026-04-16.md` confirmed `_parse_diff_stat` (bellows.py lines 306–316) uses OR-semantics: it unions filenames from both `pre_diff` and `post_diff`, so any pre-existing dirty file appears in the output even if the step made no changes to it. This caused four false-positive scope flags during Phase 8's rollout. **Fix:** Replace the current function body with diff-of-diffs semantics per Option B from the diagnostic. The corrected implementation builds a `{filename: stat_line}` dict for both pre and post, then returns only filenames where (a) the file appears in post but not pre (new modification), OR (b) the file appears in both but the stat line content differs (step added more changes to an already-dirty file). Here is the exact replacement function from the diagnostic's Q4 fix sketch: `def _parse_diff_stat(post_diff: str, pre_diff: str) -> list:` with inner helper `parse_stat_map(diff_text)` that splits on `|` and builds `{filename.strip(): stat.strip()}`, then `changed = [f for f, s in post_map.items() if pre_map.get(f) != s]` and `return sorted(changed)`. The two call sites at bellows.py lines 191 and 240 already pass `(post_diff, pre_diff)` in the correct argument order — no call-site changes needed. **Tests:** Add tests in `tests/test_bellows.py` (or create `tests/test_parse_diff_stat.py` if cleaner) covering: (1) pre-existing dirty file with identical stat in post → returns empty list, (2) new file only in post → returns that file, (3) pre-existing dirty file with changed stat in post → returns that file, (4) summary line (no `|`) is ignored, (5) empty inputs return empty list. Import `_parse_diff_stat` directly for unit testing. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "fix: _parse_diff_stat uses diff-of-diffs instead of OR-union"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed by running `git --no-pager log --oneline -1` and confirming the commit message matches "fix: _parse_diff_stat uses diff-of-diffs instead of OR-union". If not, stop and report. **Deliverable Verification:** (a) Grep for the new implementation: `grep -n "parse_stat_map\|pre_map\|post_map" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 4+ matches showing the new helper and dict comparison. (b) Confirm old OR-union logic is gone: `grep -n "for diff_text in (post_diff, pre_diff)" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — expect 0 matches. (c) Confirm tests exist: `grep -rn "test.*parse_diff_stat\|def test.*diff_stat" /Users/marklehn/Desktop/GitHub/bellows/tests/` — expect 5+ test functions. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "diff_stat" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parse-diff-stat-fix/pytest_targeted.txt`. All diff_stat tests must pass. **Deposit:** write QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/parse-diff-stat-fix-qa-2026-04-16.md`. Create evidence directory first: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parse-diff-stat-fix/`. **Rule 20 self-check:** Run the following Python block and include its literal output in the QA report:
>
> ```python
> import os, sys
> plan_slug = "parallel-1-executable-parse-diff-stat-fix-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/parse-diff-stat-fix-qa-2026-04-16.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/parse-diff-stat-fix/"
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
> **Final:** Update PROJECT_STATUS.md — add completed milestone: "`_parse_diff_stat` fixed to use diff-of-diffs semantics (Option B). False-positive scope flags on pre-existing dirty files eliminated." Then move this plan to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-parse-diff-stat-fix-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/parallel-1-executable-parse-diff-stat-fix-2026-04-16.md")`. Commit: `"chore: QA + status update for parse_diff_stat fix"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Plan complete after this step.**
