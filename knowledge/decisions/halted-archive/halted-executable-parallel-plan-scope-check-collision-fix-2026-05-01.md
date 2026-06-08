# Bellows — Parallel-Plan scope_check Collision Fix (File-Checksum Snapshot)
**Date:** 2026-05-01 | **Tier:** Medium | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Bellows will auto-claim. Step 1 (DEV) implements the file-checksum snapshot replacement for `_capture_git_diff`, modifies `_parse_diff_stat` to consume the new data shape, updates both call sites in `run_plan`, adds unit tests, runs targeted tests. Step 2 (QA) verifies deliverables, runs the full test suite, regression-checks scope_check behavior on a synthetic collision scenario, runs Rule 20 self-check.

**Bootstrap (manual fallback only):**
```
Read the plan at bellows/knowledge/decisions/executable-parallel-plan-scope-check-collision-fix-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-parallel-plan-scope-check-collision-fix-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-parallel-plan-scope-check-collision-fix-2026-05-01.md")`. **You are the Bellows Developer.** Skip glossary read — this is a code change. Read the diagnostic findings at `bellows/knowledge/research/parallel-plan-scope-check-collision-diagnosis-2026-05-01.md` for full context. **Goal:** replace `_capture_git_diff` (working-tree git-diff observation, contaminated by parallel sibling commits) with `_snapshot_file_state` (per-step file-checksum snapshot, immune to sibling contamination). **Implementation:** in `bellows/bellows.py`, (1) add new function `_snapshot_file_state(project_path: str) -> dict[str, str]` that walks the project subtree and returns `{relative_path: sha256_hexdigest}` for every tracked file (use `git ls-files` to enumerate tracked files, hash each via `hashlib.sha256`); skip the `.git` directory, the `.bellows-cache/` directory, and any file matching `*.pyc`. The function should be defensive — return `{}` on any subprocess or filesystem exception, matching the existing `_capture_git_diff` failure semantics. (2) Add new function `_diff_file_state(pre: dict, post: dict) -> list[str]` that returns sorted list of relative paths where `pre.get(path) != post.get(path)` (catches modifications, additions, deletions in both directions). (3) Replace the two `_capture_git_diff` call sites in `run_plan` (find them — the diagnostic cites `bellows.py:295` and `bellows.py:351` for pre, `bellows.py:311` and `bellows.py:369` for post; verify against current line numbers via grep) with calls to `_snapshot_file_state`, and replace the `_parse_diff_stat(post_diff, pre_diff, project_path)` calls with `_diff_file_state(pre_state, post_state)`. (4) Keep `_capture_git_diff` and `_parse_diff_stat` as-is for now — do NOT delete them. Mark them with a docstring note: `"""DEPRECATED 2026-05-01: superseded by _snapshot_file_state for parallel-collision immunity. Retained pending full removal after a stability period."""`. We can remove them in a follow-up after this fix has been live for a week. **Tests:** add `bellows/tests/test_snapshot_file_state.py` with at minimum: (a) `test_snapshot_returns_checksums_for_tracked_files` — create a temp git repo with 3 files, snapshot, assert all 3 paths present with non-empty SHA256s; (b) `test_snapshot_excludes_dotfiles_and_cache` — create temp repo with `.git/`, `.bellows-cache/`, and `*.pyc` content, snapshot, assert excluded; (c) `test_diff_detects_modification` — snapshot, modify a file, re-snapshot, assert file in diff result; (d) `test_diff_detects_addition_and_deletion` — snapshot, add a file, re-snapshot, assert added file in diff result; same for removal; (e) `test_diff_immune_to_sibling_changes_in_unrelated_files` — snapshot, modify file X (simulating sibling), assert file Y (unrelated) NOT in diff result. The fifth test is the regression guard for the BACKLOG bug — it should fail with the old `_capture_git_diff`+`_parse_diff_stat` approach and pass with the new approach (do not test the old approach explicitly; just lock in the desired behavior). (f) `test_diff_returns_empty_list_when_no_changes` — snapshot twice with no changes, assert empty list. **Run `pytest bellows/tests/test_snapshot_file_state.py -v` and confirm all pass before committing.** Then run `pytest bellows/tests/ -v` for the targeted test suite (per Rule 21 this plan is full-suite, but the targeted run is the DEV gate for "did I break anything obvious"; the full suite runs in QA). **Commit with message:** `fix(gates): file-checksum snapshot for parallel-plan scope_check immunity`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/tests/test_snapshot_file_state.py`
> - `bellows/knowledge/development/parallel-plan-scope-check-collision-fix-2026-05-01.md` (dev log with what was changed, why, line numbers, test results)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/parallel-plan-scope-check-collision-fix-2026-05-01.md` and check the Output Receipt status. If not Complete, stop and report to CEO before proceeding.** **You are the Bellows QA agent.** Skip glossary read. Test scope: full-suite (per Rule 21, change touches gate logic = load-bearing infrastructure). **FIRST — Deliverable Verification.** Read the prior DEV step's Output Receipt "Files Created or Modified (Code)" list. For each listed file, verify on disk: (1) `bellows/bellows.py` — grep for `_snapshot_file_state` and `_diff_file_state` definitions, expect both present; grep for the deprecation note on `_capture_git_diff`, expect present; grep call sites — `_capture_git_diff` should appear ONLY in its own definition and the deprecation note (no remaining call sites in `run_plan`). Pipe output to `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/grep_function_definitions.txt` and `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/grep_call_sites.txt`. (2) `bellows/tests/test_snapshot_file_state.py` — verify file exists, count test functions (`grep -c "^def test_" bellows/tests/test_snapshot_file_state.py`), expect ≥6. Pipe to `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/test_function_count.txt`. (3) Verify the dev log was deposited at `bellows/knowledge/development/parallel-plan-scope-check-collision-fix-2026-05-01.md` (cite via `ls -la` output). **Run targeted tests:** `pytest bellows/tests/test_snapshot_file_state.py -v 2>&1` and pipe to `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/pytest_targeted.txt`. Expect all tests pass. **Run full suite:** `pytest bellows/tests/ -v 2>&1` and pipe to `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/pytest_full.txt`. Expect baseline of pass/fail consistent with the pre-fix baseline (the known pre-existing `test_run_step_timeout` failure is acceptable; any NEW failure is a regression and Critical). Compare to baseline by counting failures: `grep -c "FAILED" bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/pytest_full.txt` and report the count. **Synthetic collision smoke test:** in a temp directory, simulate the parallel collision scenario: (a) create a temp git repo, (b) add files A.txt and B.txt, commit, (c) call `_snapshot_file_state` → save as pre1, (d) modify B.txt (simulating sibling commit on B), (e) call `_snapshot_file_state` → save as post1, (f) assert `_diff_file_state(pre1, post1)` returns `["B.txt"]` (only B, not A). The point of this smoke test is to demonstrate per-file isolation: if "plan A" only modified A.txt and "plan B" modified B.txt, plan A's diff would correctly NOT include B.txt. Write smoke test as a Python script and pipe its stdout (use `print()` for the assertion result) to `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/synthetic_collision_smoke.txt`. **Produce verification table:** `| Deliverable | Expected | Status (✅/❌) | Evidence |` with rows for: (a) `_snapshot_file_state` defined in bellows.py, (b) `_diff_file_state` defined in bellows.py, (c) `_capture_git_diff` deprecation note present, (d) no remaining `_capture_git_diff` call sites in `run_plan`, (e) test file exists with ≥6 tests, (f) targeted tests all pass, (g) full suite no new regressions, (h) synthetic collision smoke shows per-file isolation, (i) dev log deposited. If ANY item is ❌, STOP and report to CEO. **Deposit QA report** at `bellows/knowledge/qa/qa-parallel-plan-scope-check-collision-fix-2026-05-01.md` with the verification table, baseline comparison, and the literal stdout of the Rule 20 self-check below. **Update PROJECT_STATUS.md** with a milestone entry: "Closed BACKLOG `2026-04-30: parallel-plan scope_check diff-collision`. Replaced `_capture_git_diff` (working-tree observation, contaminated by sibling commits) with `_snapshot_file_state` (per-step file-checksum snapshot, immune to sibling contamination). Diagnosis at `knowledge/research/parallel-plan-scope-check-collision-diagnosis-2026-05-01.md`. +6 unit tests. The `parallel-N-` pattern is no longer yellow-flagged for committing plans. REMINDER: restart Bellows daemon to load." Commit PROJECT_STATUS.md. **Final commit and STOP — do NOT move this plan to Done. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.** **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. The feedback append + commit are the absolute last operations. Then stop. **Run the Rule 20 self-check at the very end and include its literal stdout in the QA report:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-parallel-plan-scope-check-collision-fix-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/qa-parallel-plan-scope-check-collision-fix-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_function_definitions.txt",
>     "grep_call_sites.txt",
>     "test_function_count.txt",
>     "pytest_targeted.txt",
>     "pytest_full.txt",
>     "synthetic_collision_smoke.txt",
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
> **Deposits:**
> - `bellows/knowledge/qa/qa-parallel-plan-scope-check-collision-fix-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/` (6 files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
