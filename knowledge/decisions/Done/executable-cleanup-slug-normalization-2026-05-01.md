# bellows — Cleanup Slug Normalization Fix
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

**Test Scope: full-suite** — touches `_consume_verdicts` (core verdict lifecycle code) and the daemon startup sweep. Cross-bucket regression risk on every test that exercises verdict consumption, plan-matching, and startup paths. Targeted run insufficient.

**Background.** The diagnostic at `bellows/knowledge/research/cleanup-verdicts-call-site-gap-2026-05-01.md` characterized 51 stranded verdict-request files in `bellows/verdicts/pending/archived/` and identified the root cause as a slug normalization mismatch — NOT the missing-call-site shape the BACKLOG entry hypothesized. The Planner-side verdict filename includes the plan-type prefix (`verdict-diagnostic-foo-...`), but the verdict-request filename uses the stripped slug (`verdict-request-foo-...`). When `_consume_verdicts` parses `plan_slug` from the verdict filename it captures the prefix; passing that slug to `_cleanup_verdicts_for_slug` produces a glob that doesn't match the actual file. Cleanup silently fails.

**Fix scope.** Four LOC in `bellows.py` plus a startup-sweep loop removal:
1. Compute `cleanup_slug = verdict.slug_from_path(original_name)` after plan matching succeeds
2. Replace `plan_slug` with `cleanup_slug` at three call sites in `_consume_verdicts`
3. Normalize slug at the pending-req-file lookup (Q3 secondary bug — silent fallback to global search across all 8 watched projects)
4. Remove the loop that adds Done/ plan slugs to `active_slugs` in the startup sweep (Q3 H3 — the sweep was actively protecting completed-plan stranded files)

**SA recommendation cited verbatim.** Line numbers in this plan are from the SA findings (Q1 line 130–140 for the helper, Q3 lines 669/736/756/768 for the consumption call sites, Q3 lines 824–828 for the startup sweep). The DEV must verify these line numbers against current code before editing — line numbers drift.

**End-to-end trace verified.** Planner traced the proposed fix against the original bug observation in Rule 22 verification: Planner deposits `verdict-diagnostic-foo-step-1.md` → `_consume_verdicts` parses `plan_slug = "diagnostic-foo"` → plan matching succeeds via substring → fix computes `cleanup_slug = slug_from_path(original_name) = "foo"` → glob matches `verdict-request-foo-step-*.md` → file deleted. Fix prevents the observed bug. Robust to both Planner verdict-filename conventions (with or without prefix) because the canonical source is the plan filename, not the verdict filename.

## How to Run This Plan

Paste the bootstrap into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After Step 1 reports Complete, CEO confirms ("ok") to advance to Step 2. After Step 2, CEO must restart Bellows to load the new code.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-cleanup-slug-normalization-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-cleanup-slug-normalization-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-cleanup-slug-normalization-2026-05-01.md")`.
>
> You are the Bellows Developer. **Read the diagnostic findings at `bellows/knowledge/research/cleanup-verdicts-call-site-gap-2026-05-01.md` first** — Q3 documents the 7-step cascade and Q4 specifies the recommended fix. Skip specialist file and glossary reads — this is a code-tracing fix following an SA blueprint. Use the `Edit` tool (NOT `Desktop Commander:edit_block` — not available in Claude Code).
>
> **Pre-edit verification.** Open `bellows/bellows.py`. Run `grep -n "plan_slug" bellows/bellows.py` and `grep -n "active_slugs" bellows/bellows.py` to confirm the line numbers cited in the SA findings. Line numbers may have drifted; the SA cited 130–140 (helper), 669 (pending-req-file lookup), 706 (plan match), 736 (continue-to-done cleanup), 756 (halt cleanup), 768 (per-step cleanup), 824–828 (startup sweep Done/ loop). Report the actual current line numbers in your dev log.
>
> **Edit 1 — Compute `cleanup_slug` after plan matching.** In `_consume_verdicts`, after the plan-matching loop sets `plan_matched = True` (SA cited line 706), add a line that computes `cleanup_slug = verdict.slug_from_path(original_name)`. The variable `original_name` is the matched plan filename (with lifecycle prefix already stripped per the existing flow); `slug_from_path` strips the plan-type prefix (`diagnostic-`, `executable-`). Place the new line immediately after `plan_matched = True` is set, inside the same conditional block. Use `Edit` with a verbatim anchor of the existing line and append the new line.
>
> **Edit 2 — Replace `plan_slug` with `cleanup_slug` at three call sites.** At the three locations the SA enumerated (continue-to-done at line 736, halt at line 756, per-step cleanup at line 768), replace the variable `plan_slug` with `cleanup_slug` in the call to `_cleanup_verdicts_for_slug` (lines 736, 756) and in the `pending_file` path construction (line 768). Use three separate `Edit` calls, each with a verbatim anchor showing the existing line and the replacement showing the swap. Do NOT replace `plan_slug` anywhere else — it's still the correct variable for filename regex parsing and plan-match substring lookup.
>
> **Edit 3 — Normalize slug at pending-req-file lookup (line 669).** The SA found that the lookup uses `plan_slug` to construct the pending-req-file path, fails to find the file (slug mismatch), and falls through to `scoped_decisions_path = None` causing global search across all 8 watched projects. Replace `plan_slug` with `verdict.slug_from_path(...)` here — but the lookup happens BEFORE plan matching, so `original_name` isn't available yet. Resolution: the lookup is a heuristic for scoping the search; if `plan_slug` already matches the verdict-request filename (no prefix), the lookup succeeds; if not, it fails and falls through to global. Adding a fallback that ALSO tries the stripped-slug form keeps both code paths working. Specifically: if `(BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md")` doesn't exist, try `(BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{slug_from_path('placeholder-' + plan_slug)}-step-{step_number}.md")` — wait, this won't work because `slug_from_path` operates on a filename, not a slug. **Cleaner approach:** the lookup's purpose is to derive `scoped_decisions_path`. Strip any plan-type prefix from `plan_slug` BEFORE constructing the lookup path: `lookup_slug = plan_slug; for prefix in ("diagnostic-", "executable-"): if lookup_slug.startswith(prefix): lookup_slug = lookup_slug[len(prefix):]; break`. Use `lookup_slug` in the pending-req-file path construction. If the lookup still fails, the existing global-search fallback continues to work. Document this approach in the dev log.
>
> **Edit 4 — Remove Done/ slug loop from startup sweep.** The SA cited lines 824–828 in `Bellows.start()` where Done/ plan filenames are iterated and their slugs added to `active_slugs`. This protects historical stranded files. Remove the entire loop that walks Done/ directories — keep only the loop that adds slugs from active-state plan files (`in-progress-`, `verdict-pending-`, raw `executable-`/`diagnostic-`). The result: startup sweep treats Done/ plans as inactive and removes their orphaned verdict-requests. Read lines 820–840 first to identify the exact loop to remove; cite the verbatim removed lines in the dev log.
>
> **Verify edits.** After all four edits, run `grep -n "cleanup_slug\|plan_slug\|active_slugs" bellows/bellows.py` and confirm: (a) `cleanup_slug` appears at least 4 times (declaration + 3 use sites), (b) `plan_slug` still appears for filename regex parsing and plan-match logic, (c) the Done/ loop is removed (only active-state slug-collection loop remains in startup sweep). Run `python3 -c "import ast; ast.parse(open('bellows/bellows.py').read()); print('valid')"` to confirm the file still parses. Run the full test suite: `cd bellows && python3 -m pytest tests/ -x -v 2>&1 | tail -100`. Report the test count and any failures in the dev log.
>
> **Add three regression tests.** Append to `bellows/tests/test_consume_verdicts.py` (create if missing):
>
> 1. `test_cleanup_normalizes_prefixed_verdict_slug` — Set up a fake `verdicts/pending/verdict-request-foo-2026-05-01-step-1.md` AND a `verdicts/resolved/verdict-diagnostic-foo-2026-05-01-step-1.md` (note prefix). Set up a `verdict-pending-diagnostic-foo-2026-05-01.md` plan file. Run `_consume_verdicts`. Assert the verdict-request file is deleted (cleanup succeeded with normalized slug). This is the regression test for the actual observed bug.
>
> 2. `test_cleanup_unprefixed_verdict_slug` — Same as above but verdict file is `verdict-foo-2026-05-01-step-1.md` (no prefix). Assert verdict-request file is deleted. Backward-compatibility test.
>
> 3. `test_startup_sweep_removes_done_plan_orphans` — Place a `Done/executable-bar-2026-05-01.md` plan file and a `verdicts/pending/verdict-request-bar-2026-05-01-step-1.md` orphan request. Run `Bellows.start()` (or extract the startup-sweep block to a callable function for unit testing). Assert the orphan request is removed. Regression test for the secondary bug.
>
> If any test name suggests a property the assertion doesn't verify, the test name is wrong (per the 2026-05-01 lesson on test-name-vs-assertion gap). Verify each assertion encodes the property the name implies.
>
> **Deposit dev log** at `bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md` containing: (a) verified line numbers vs SA cited line numbers (call out drift), (b) verbatim before/after for each of the 4 edits, (c) test results (pass/fail count), (d) note that CEO restart is required. Use the canonical Python file write pattern: `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md", "w") as f: f.write(content)` where content is a triple-quoted string defined before the open call.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub && git add bellows/bellows.py bellows/tests/test_consume_verdicts.py bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "fix: normalize cleanup slug in _consume_verdicts + remove Done/ exclusion from startup sweep (BACKLOG #3)"`.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/tests/test_consume_verdicts.py`
> - `bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA Agent. Skip specialist file and glossary reads — this is verification of a localized code fix.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 dev log "Files Created or Modified" list. For each listed deliverable, verify it exists on disk with the described change. Produce a verification table: `| Deliverable | Expected | Status | Evidence |`. If ANY item fails, attempt to fix or flag as blocked.
>
> **Run nine verification checks.** Create the evidence directory first: `mkdir -p bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01`.
>
> Check 1 — `cleanup_slug` variable declared: `grep -n "cleanup_slug = " bellows/bellows.py > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/grep_cleanup_slug_decl.txt` — expect at least one match showing `cleanup_slug = verdict.slug_from_path(original_name)`.
>
> Check 2 — `cleanup_slug` used at three sites: `grep -n "cleanup_slug" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/grep_cleanup_slug_uses.txt` — expect at least 4 lines total (1 declaration + 3 use sites in `_consume_verdicts`).
>
> Check 3 — Pending-req-file lookup uses normalized slug: `grep -n "lookup_slug\|verdict-request-{" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/grep_lookup_slug.txt` — expect to see the prefix-stripping logic for the pending-req-file lookup OR the new `lookup_slug` variable. Inspect output and confirm the lookup at the SA-cited line area uses the stripped form.
>
> Check 4 — Startup sweep no longer iterates Done/: `grep -n -A 3 "active_slugs" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/grep_active_slugs.txt` — expect to see the slug-collection loop for active-state plans, but NO loop walking Done/ directories. Inspect output and confirm.
>
> Check 5 — File parses as Python: `python3 -c "import ast; ast.parse(open('bellows/bellows.py').read()); print('valid')" > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/syntax_valid.txt` — expect output `valid`.
>
> Check 6 — Targeted regression tests pass: `cd bellows && python3 -m pytest tests/test_consume_verdicts.py -v > knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/pytest_targeted.txt 2>&1` — expect three new tests pass: `test_cleanup_normalizes_prefixed_verdict_slug`, `test_cleanup_unprefixed_verdict_slug`, `test_startup_sweep_removes_done_plan_orphans`.
>
> Check 7 — Full test suite passes: `cd bellows && python3 -m pytest tests/ > knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/pytest_full.txt 2>&1` — expect all tests pass (or only known pre-existing failures matching prior session baselines documented in PROJECT_STATUS).
>
> Check 8 — Commit landed correctly: `git --no-pager log -1 --name-only -- bellows/bellows.py > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/git_log_bellows_py.txt` — expect commit message includes "normalize cleanup slug" and file list shows `bellows/bellows.py`.
>
> Check 9 — Diff is bounded to expected files: `git --no-pager diff HEAD~1 HEAD --stat > bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/git_diff_stat.txt` — expect changes only to `bellows/bellows.py`, `bellows/tests/test_consume_verdicts.py`, `bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md`, and `bellows/knowledge/research/agent-prompt-feedback.md`. No unexpected files.
>
> Deposit the QA report at `bellows/knowledge/qa/cleanup-slug-normalization-qa-2026-05-01.md` with a verification table citing each evidence file path in the Evidence column. Use the canonical Python file write pattern.
>
> **Then run the mandatory Rule 20 self-check Python block:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-cleanup-slug-normalization-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/cleanup-slug-normalization-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_cleanup_slug_decl.txt",
>     "grep_cleanup_slug_uses.txt",
>     "grep_lookup_slug.txt",
>     "grep_active_slugs.txt",
>     "syntax_valid.txt",
>     "pytest_targeted.txt",
>     "pytest_full.txt",
>     "git_log_bellows_py.txt",
>     "git_diff_stat.txt",
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
> Include the literal stdout in the QA report. If the self-check fails, STOP and report. If it passes, proceed.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — add a completed milestone entry under the Completed section summarizing: "2026-05-01: Closed BACKLOG #3 (cleanup_verdicts_for_slug call-site gap). Diagnostic identified the actual root cause as slug normalization mismatch (NOT missing call sites as BACKLOG entry hypothesized): Planner-side verdict filenames include plan-type prefix while verdict-request filenames use stripped slug; cleanup glob never matched. Fix normalizes cleanup_slug via verdict.slug_from_path(original_name) at three call sites in _consume_verdicts, normalizes pending-req-file lookup slug, and removes Done/ exclusion from startup sweep. +3 regression tests. CEO restart required to load." Use the `Edit` tool with a verbatim anchor — read PROJECT_STATUS.md first to identify the existing line to anchor the insert. Update BACKLOG.md to move the BACKLOG #3 entry from Open to Closed (with a closure note citing the diagnostic and this executable). Standard prompt feedback protocol. Commit with: `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/cleanup-slug-normalization-qa-2026-05-01.md bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/ bellows/PROJECT_STATUS.md bellows/knowledge/BACKLOG.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: cleanup slug normalization verified + close BACKLOG #3"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/cleanup-slug-normalization-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-cleanup-slug-normalization-2026-05-01/`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/BACKLOG.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
