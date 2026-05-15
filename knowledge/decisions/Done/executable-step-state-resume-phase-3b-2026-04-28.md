# Bellows — Phase 3b: DB-Based Step State Recovery + plan_slug Column (BACKLOG #6)
**Date:** 2026-04-28 | **Tier:** Medium | **Test Scope:** full-suite | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)
**Priority:** 5

## Context

Phase 3b implementation per the design at `bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md` and the verification at `bellows/knowledge/research/step-state-resume-phase-3b-verification-2026-04-28.md`. Closes BACKLOG #6 ("step state lost across re-claim") via Hybrid 1+3 Option A: persist step completion in `bellows.db` keyed by canonical plan slug, query the DB on re-claim to determine resume step.

This phase ships Deliverables 2, 3, and 5 from the design. Deliverable 4 (plan-hash drift warning) is deferred to Phase 3c. Phase 3a (Option C documentation) shipped earlier today as `executable-verdict-only-resume-docs-2026-04-28`.

Decision 3 (slug function exposure) revised to Option β based on Q8 import-graph evidence: rename `_slug_from_path` → public `slug_from_path` in `verdict.py`, update existing call sites, use from new code. No new module — `bellows.py → verdict.py` import already exists at 3 sites.

Verification confirmed all 17 design anchors are accurate (zero drift). Dual DDL pattern surfaced: `record_run()` DDL at line 151, `migrate_db()` DDL at line 41, additions dict at line 54 — all three must be updated for the new column.

Touches load-bearing infrastructure (DB schema + `run_plan()` integration). Full-suite test required per Rule 21.

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 (Bellows Developer) implements the rename, schema additions, and resume logic, runs targeted tests. Step 2 (Bellows QA) runs full pytest, performs deliverable verification, behavioral check on a synthetic resume scenario, Rule 17 + Rule 20 checks, then commits + PROJECT_STATUS update. Per disable-auto-close, terminal step pauses for Planner verdict. **Bellows daemon restart required after this plan ships to load the new code.**

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-step-state-resume-phase-3b-2026-04-28.md", "bellows/knowledge/decisions/in-progress-executable-step-state-resume-phase-3b-2026-04-28.md")`. **Skip glossary read** — code-level implementation per Rule 16. **Read your specialist file** at `bellows/agents/BELLOWS_DEVELOPER.md` — load-bearing infrastructure work, specialist context warranted. **Mandatory reads:** `bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md` (design — treat as canonical specification) and `bellows/knowledge/research/step-state-resume-phase-3b-verification-2026-04-28.md` (verification — confirms all line anchors accurate). **Task 1 — rename `_slug_from_path` → public `slug_from_path` in verdict.py.** Use `Filesystem:edit_file`. (1a) Locate `_slug_from_path` definition (lines 65-75 per verification). Edit: change `def _slug_from_path(plan_path):` to `def slug_from_path(plan_path):`. (1b) Search for any internal callers of `_slug_from_path` within `verdict.py` itself — if any exist, update them to `slug_from_path`. Use grep or read-and-search to confirm. (1c) Update the 3 existing callers in `bellows.py` (lines 384, 779, 781 per verification): change every `verdict._slug_from_path(` to `verdict.slug_from_path(`. (1d) Search ALL test files for any reference to `_slug_from_path`: `grep -rn "_slug_from_path" /Users/marklehn/Desktop/GitHub/bellows/tests/ /Users/marklehn/Desktop/GitHub/bellows/*.py`. Update every match to `slug_from_path` (without the leading underscore). After this task, the literal string `_slug_from_path` should not appear anywhere in the codebase. **Task 2 — add `plan_slug` column to runs table — ALL THREE DDL/migration sites.** (2a) Edit `record_run()` DDL at line 151 in `bellows.py`. Add `plan_slug TEXT` column to the `CREATE TABLE IF NOT EXISTS runs (...)` statement, after the existing `cost REAL` line. Format: `cost REAL,\n            plan_slug TEXT`. (2b) Edit `migrate_db()` DDL at line 41 in `bellows.py`. Add the same `plan_slug TEXT` column to its `CREATE TABLE IF NOT EXISTS runs (...)` statement, in the same position relative to the other columns. (2c) Edit `migrate_db()` additions dict at line 54 in `bellows.py`. Add an entry: `"plan_slug": "TEXT"` (or whatever shape the existing dict uses — match the format of existing entries exactly). This ensures live DBs missing the column get it added on next startup. **Task 3 — wire `plan_slug` through `record_run()`.** (3a) Edit `record_run()` signature (line 140) to add `plan_slug: str` as the last parameter. (3b) Edit the INSERT statement (lines 162-164) to include `plan_slug` in the column list AND add a `?` placeholder AND add `plan_slug` to the values tuple. (3c) Update all 4 `record_run()` call sites at lines 269, 307, 327, 365 to pass `plan_slug`. The slug should be derived once at the top of `run_plan()` from `base_filename` (or `plan_path` if `base_filename` isn't available at the relevant scope) using `verdict.slug_from_path()`. Add this derivation near the start of `run_plan()`, after `plan_filename` is computed but before any `record_run()` call. Variable name: `plan_slug`. **Task 4 — add `_get_last_completed_step()` helper.** Add a new module-level function in `bellows.py`, placed near `record_run()` (logical grouping). Signature and body:
>
> ```python
> def _get_last_completed_step(db_path: str, plan_slug: str) -> Optional[int]:
>     """Return the highest step number marked Complete for this plan_slug, or None."""
>     try:
>         conn = sqlite3.connect(db_path)
>         try:
>             row = conn.execute(
>                 "SELECT MAX(step) FROM runs WHERE plan_slug = ? AND status = 'Complete'",
>                 (plan_slug,),
>             ).fetchone()
>             return row[0] if row and row[0] is not None else None
>         finally:
>             conn.close()
>     except sqlite3.Error:
>         return None
> ```
>
> Imports needed: `sqlite3`, `Optional` from `typing`. Verify both are already imported at the top of `bellows.py`; if not, add them. **Task 5 — add DB resume logic in `run_plan()`.** Integration point: AFTER the shadow cache load at line 215, BEFORE the atomic claim move at line 231. Insert this block:
>
> ```python
> if resume_step is None and shadow_text is not None:
>     last_step = _get_last_completed_step(db_path, plan_slug)
>     if last_step is not None and last_step >= 1:
>         resume_step = last_step + 1
>         print(f"Bellows: DB resume — last completed step {last_step}, resuming at {resume_step}")
> ```
>
> Verify `db_path` is in scope at this location — if not, derive it from `config["db_path"]` or equivalent. The `plan_slug` variable from Task 3c must be in scope (defined earlier in the function). **Task 6 — add 5 tests.** Edit `bellows/tests/test_bellows.py`. Add the following tests (skip the hash drift test from Deliverable 4 — that's Phase 3c). (6a) `test_record_run_stores_plan_slug` — call `record_run(...)` with a `plan_slug` arg, then query the DB and verify the column is populated. (6b) `test_get_last_completed_step_returns_max` — insert 3 rows for slug `foo` with steps 1/2/3 status Complete, plus 1 row for slug `bar`. Call `_get_last_completed_step(db, "foo")`. Assert returns 3. (6c) `test_get_last_completed_step_no_rows` — empty DB. Call helper. Assert returns None. (6d) `test_get_last_completed_step_excludes_non_complete` — insert rows with status Complete (step 1) and VerdictPending (step 2). Assert helper returns 1, not 2. (6e) `test_get_last_completed_step_exact_slug_match` — insert rows for slug `foo` (step 2 Complete) and slug `foo-bar` (step 3 Complete). Call helper for `foo`. Assert returns 2 (not 3). This validates the U5 fix — exact match, no LIKE substring collision. Each test should use an in-memory or tempfile SQLite DB, follow the existing test patterns in the file (look at the existing `test_record_run` if present, or `test_extract_total_steps` for general patterns). **Task 7 — run targeted tests.** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_bellows.py -v 2>&1 | tail -40`. Expected: existing tests pass + 5 new tests pass. If any fail, debug before proceeding. The pre-existing `test_run_step_timeout` failure is allowed. **Task 8 — write dev log.** Use `Filesystem:write_file` to deposit `bellows/knowledge/development/step-state-resume-phase-3b-dev-2026-04-28.md` with: (1) summary of changes; (2) before/after for each of the 8 tasks; (3) the 5 new test names; (4) targeted test output tail; (5) reference to design and verification docs. **Task 9 — commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add bellows.py verdict.py tests/test_bellows.py knowledge/development/step-state-resume-phase-3b-dev-2026-04-28.md && git commit -m "feat(bellows): DB-based step state recovery + plan_slug column — BACKLOG #6"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/step-state-resume-phase-3b-dev-2026-04-28.md`

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/step-state-resume-phase-3b-dev-2026-04-28.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.** **Skip glossary AND specialist file reads** — gate-logic verification work. **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 Output Receipt "Files Created or Modified (Code)" list. For each listed file, verify changes landed via grep (pipe ALL output to `bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/grep_deliverables.txt`): (a) `grep -rc "_slug_from_path" /Users/marklehn/Desktop/GitHub/bellows/bellows.py /Users/marklehn/Desktop/GitHub/bellows/verdict.py /Users/marklehn/Desktop/GitHub/bellows/gates.py /Users/marklehn/Desktop/GitHub/bellows/parser.py /Users/marklehn/Desktop/GitHub/bellows/tests/` should return 0 across all files (function fully renamed, no stale references in tests); (b) `grep -c "slug_from_path" /Users/marklehn/Desktop/GitHub/bellows/verdict.py` should return at least 1 (function exists with new public name); (c) `grep -c "verdict.slug_from_path" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` should return at least 4 (3 original call sites + 1+ new ones in run_plan); (d) `grep -n "plan_slug" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` should return matches in: record_run signature, record_run DDL, record_run INSERT, all 4 record_run call sites, migrate_db DDL, migrate_db additions, _get_last_completed_step query, run_plan resume logic — at least 10 distinct matches expected; (e) `grep -n "_get_last_completed_step" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` should return at least 2 (definition + 1+ usage); (f) `grep -c "test_get_last_completed_step\|test_record_run_stores_plan_slug" /Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py` should return at least 5 (5 new tests). Build a 6-row verification table. **Task 1 — full pytest suite.** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/pytest_full.txt`. Expected: prior baseline + 5 new tests, zero regressions. The pre-existing `test_run_step_timeout` failure is allowed. **Task 2 — schema verification.** Verify the live DB schema picks up the new column on a fresh start. Run `python3 -c "
> import os, sqlite3, tempfile, sys
> sys.path.insert(0, '/Users/marklehn/Desktop/GitHub/bellows')
> import bellows
> db_path = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
> # Trigger migrate_db on the fresh DB
> bellows.migrate_db(db_path)
> # Verify plan_slug column exists
> conn = sqlite3.connect(db_path)
> cols = [r[1] for r in conn.execute('PRAGMA table_info(runs)')]
> print('Columns:', cols)
> print('plan_slug present:', 'plan_slug' in cols)
> os.unlink(db_path)
> " 2>&1 | tee bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/schema_check.txt`. Expected: `plan_slug present: True`. If False, flag as Critical. **Task 3 — behavioral verification of resume logic.** Run this Python and pipe output to `bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/behavioral_check.txt`: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -c "
> import os, sqlite3, tempfile, sys
> sys.path.insert(0, '/Users/marklehn/Desktop/GitHub/bellows')
> import bellows
> # Set up a fresh DB with simulated step 2 Complete for slug 'phase3b-test'
> db_path = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
> bellows.migrate_db(db_path)
> conn = sqlite3.connect(db_path)
> conn.execute('INSERT INTO runs (timestamp, plan_path, project, session_id, step, status, cost, plan_slug) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', ('2026-04-28T22:00:00', '/path/in-progress-executable-phase3b-test.md', 'bellows', 'sess123', 1, 'Complete', 0.05, 'executable-phase3b-test'))
> conn.execute('INSERT INTO runs (timestamp, plan_path, project, session_id, step, status, cost, plan_slug) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', ('2026-04-28T22:05:00', '/path/in-progress-executable-phase3b-test.md', 'bellows', 'sess123', 2, 'Complete', 0.05, 'executable-phase3b-test'))
> conn.commit()
> conn.close()
> # Query helper
> result = bellows._get_last_completed_step(db_path, 'executable-phase3b-test')
> print('Last completed step for executable-phase3b-test:', result)
> print('Expected: 2 (resume would dispatch step 3)')
> # Test exact-match: similar slug should not collide
> result2 = bellows._get_last_completed_step(db_path, 'executable-phase3b')
> print()
> print('Last completed step for executable-phase3b (substring):', result2)
> print('Expected: None (exact match required, no LIKE collision)')
> # Test empty
> result3 = bellows._get_last_completed_step(db_path, 'nonexistent-slug')
> print()
> print('Last completed step for nonexistent-slug:', result3)
> print('Expected: None')
> os.unlink(db_path)
> " 2>&1 | tee bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/behavioral_check.txt`. Expected: 2, None, None. If any wrong, flag as Critical. **Task 4 — write QA report.** Use `Filesystem:write_file` to write `bellows/knowledge/qa/step-state-resume-phase-3b-qa-2026-04-28.md` with: (1) Rule 17 deliverable verification table (6 rows ✅); (2) test execution summary citing pytest_full.txt (count before/after, all passing); (3) schema verification result citing schema_check.txt; (4) behavioral check summary citing behavioral_check.txt (3 cases: exact match returns 2, substring returns None, nonexistent returns None); (5) verdict on closure of BACKLOG #6 Phase 3b. **Task 5 — Rule 20 self-check.** Run this Python block exactly as written and include literal stdout in QA report:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-step-state-resume-phase-3b-2026-04-28"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/step-state-resume-phase-3b-qa-2026-04-28.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "schema_check.txt", "behavioral_check.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
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
> If FAILED, stop and report. If PASSED, proceed. **Task 6 — Update PROJECT_STATUS.md.** Use `Filesystem:edit_file` to add a milestone entry referencing BACKLOG #6 Phase 3b closure, the 5 new tests, the public slug_from_path rename, the plan_slug column addition, and the Bellows-restart requirement. Phase 3c (hash drift warning) remains deferred. Anchor: read the current file first to identify the exact heading or top of Completed Milestones. **Task 7 — Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. **Task 8 — final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add PROJECT_STATUS.md knowledge/qa/step-state-resume-phase-3b-qa-2026-04-28.md knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: step-state resume Phase 3b verified, BACKLOG #6 closed"`. **STOP.** Do NOT move this plan to Done/. The Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/step-state-resume-phase-3b-qa-2026-04-28.md`
> - `bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/grep_deliverables.txt`
> - `bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/pytest_full.txt`
> - `bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/schema_check.txt`
> - `bellows/knowledge/qa/evidence/executable-step-state-resume-phase-3b-2026-04-28/behavioral_check.txt`
