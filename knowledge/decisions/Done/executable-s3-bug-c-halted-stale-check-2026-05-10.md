# Executable — S3 Bug C: stale-verdict check for halted-* plans

**Project:** bellows | **Type:** executable | **Steps:** 2 | **Priority:** 1 | **auto_close:** false | **pause_for_verdict:** after_step_1

## Context

BACKLOG entry `2026-05-09: S3 Bug C` reports that resolved verdict files for halted plans generate a retry-loop log every ~30 seconds: `no verdict-pending plan found for {slug} step {N} — leaving in resolved/ for retry`. The stale-check in `_consume_verdicts()` searches `knowledge/decisions/Done/` for a plan filename containing the slug but does NOT search for `halted-*` prefixed plans that remain in `knowledge/decisions/` after a halt verdict. The check falls through and the file is left in `resolved/` indefinitely.

**Code verification by Planner:** the stale-check is at the `else` branch following `if plan_matched:` in `_consume_verdicts()`. Currently iterates `Done/` only. Confirmed live on 2026-05-09 with file `verdict-executable-parallel-plan-scope-check-collision-fix-2026-05-01-step-2.md` (bare-format `stop` verdict). Affected plan: `halted-executable-parallel-plan-scope-check-collision-fix-2026-05-01.md`.

**Severity:** Low — log noise only, no functional impact, no lifecycle corruption. We're shipping it because it's a clean ~5 LOC fix and the retry-loop noise can mask real verdict-consumption issues.

## Execution Map

Step 1 (DEV) → Step 2 (QA)

## STEP 1 — Bellows Developer: extend stale-check to halted-* plans

**Agent:** Bellows Developer
**Deposits:**
- `bellows/bellows.py` (modified)
- `bellows/tests/test_consume_verdicts.py` (modified — new regression test)
- `bellows/knowledge/development/s3-bug-c-halted-stale-check-dev-log-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_DEVELOPER.md, then bellows/knowledge/BACKLOG.md (the 2026-05-09 entry on S3 Bug C). You are the Bellows Developer implementing a tightly-scoped fix to `_consume_verdicts()` in `bellows.py`.

OBJECTIVE
Extend the stale-verdict check to also recognize `halted-*` prefixed plans in `knowledge/decisions/` (not just `Done/`). When a resolved verdict file references a slug whose plan was halted, the verdict should be moved to `processed-*` instead of left in `resolved/` for retry. ~5 LOC + 1 regression test.

LOCATE THE FIX SITE

In `bellows.py`, find `_consume_verdicts()`. The stale-check is in the `else` branch that follows `if plan_matched:` near the end of the per-verdict-file loop. Current code (text may shift across edits — find by content):

```python
else:
    # No match — check if plan is already in Done/ (stale verdict)
    stale = False
    for decisions_path in search_dirs:
        done_dir = os.path.join(decisions_path, "Done")
        if os.path.isdir(done_dir):
            for dname in os.listdir(done_dir):
                if plan_slug in dname:
                    stale = True
                    break
        if stale:
            break
    if stale:
        processed_path = resolved_dir / f"processed-{fname}"
        shutil.move(str(resolved_dir / fname), str(processed_path))
        print(f"Bellows: ⚠️  stale verdict for {plan_slug} step {step_number} — plan already in Done/, moving to processed")
    else:
        print(f"Bellows: ⚠️  no verdict-pending plan found for {plan_slug} step {step_number} — leaving in resolved/ for retry")
```

EXACT CHANGE

Extend the stale detection to also check the watched directory itself for `halted-*` prefixed plans matching the slug. Mirror the existing Done/ search logic. After the existing Done/ inner loop, add a parallel check that scans `decisions_path` (not the Done/ subdirectory) for files starting with `halted-` and containing the slug:

```python
else:
    # No match — check if plan is already in Done/ OR halted in decisions/ (stale verdict)
    stale = False
    for decisions_path in search_dirs:
        done_dir = os.path.join(decisions_path, "Done")
        if os.path.isdir(done_dir):
            for dname in os.listdir(done_dir):
                if plan_slug in dname:
                    stale = True
                    break
        if stale:
            break
        # Also check decisions/ itself for halted-* plans (S3 Bug C fix)
        if os.path.isdir(decisions_path):
            for dname in os.listdir(decisions_path):
                if dname.startswith("halted-") and plan_slug in dname:
                    stale = True
                    break
        if stale:
            break
    if stale:
        processed_path = resolved_dir / f"processed-{fname}"
        shutil.move(str(resolved_dir / fname), str(processed_path))
        print(f"Bellows: ⚠️  stale verdict for {plan_slug} step {step_number} — plan in Done/ or halted-, moving to processed")
    else:
        print(f"Bellows: ⚠️  no verdict-pending plan found for {plan_slug} step {step_number} — leaving in resolved/ for retry")
```

Note the print message in the `if stale:` branch is updated to reflect the broader detection scope.

REGRESSION TEST (tests/test_consume_verdicts.py)

Find the existing test patterns for stale-verdict detection (the existing tests should cover the Done/ stale case). Add ONE new test:

`test_consume_verdicts_marks_resolved_processed_when_plan_halted` — sets up:
- A temp watched_projects directory
- A `halted-executable-foo-2026-05-09.md` file in `decisions_path` (NOT in Done/)
- A `verdict-executable-foo-2026-05-09-step-2.md` file in `verdicts/resolved/` (with valid `verdict: stop` content)
- An empty `verdicts/pending/` (no pending request file — simulating prior cleanup)

Then runs `_consume_verdicts` and asserts:
- The verdict file is renamed to `processed-verdict-executable-foo-2026-05-09-step-2.md`
- The halted plan file is unchanged (still `halted-executable-foo-2026-05-09.md` in decisions_path)
- No exception raised

Model the new test after the existing Done/ stale-detection test pattern.

VERIFY

Run the targeted consume-verdicts test file:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest tests/test_consume_verdicts.py -v 2>&1 | tail -20

Expected: all existing tests pass + the new test passes.

Then run the full test suite:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest 2>&1 | tail -10

Expected: 246 passed (245 from prior session + 1 new), 1 pre-existing `test_run_step_timeout` failure unchanged.

DEV LOG

Deposit `bellows/knowledge/development/s3-bug-c-halted-stale-check-dev-log-2026-05-10.md` with:
- The exact diff applied to `bellows.py` (post-edit line range)
- The exact new test added to `tests/test_consume_verdicts.py`
- Pytest output (full output of test_consume_verdicts.py + tail of full suite)
- Confirmation: post-edit line numbers
- Confirmation: no other functions in bellows.py touched
- Confirmation: no other test files touched

GIT COMMITS

ONE commit, conventional message:
    fix(verdicts): stale-verdict check recognizes halted-* plans (BACKLOG S3 Bug C)

Include all three files: bellows.py, tests/test_consume_verdicts.py, the dev log. Push.

CONSTRAINTS
- Do NOT modify any other function in bellows.py. Surgical fix only.
- Do NOT modify the existing Done/ stale-detection logic. Add the halted-* check in parallel.
- Do NOT change error handling or the `not stale` branch (which prints the retry-loop log).
- Run pre-commit hooks if configured.

OUTPUT RECEIPT
End with status (Complete / Blocked), summary of changes (lines added), and deposit paths.
```

## STEP 2 — Bellows QA: verify the fix

**Agent:** Bellows QA
**Deposits:**
- `bellows/knowledge/qa/s3-bug-c-halted-stale-check-qa-2026-05-10.md`
- `bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/pytest_consume_verdicts.txt`
- `bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/pytest_full.txt`

**Prompt:**

```
Read agents/BELLOWS_QA.md, then the dev log at bellows/knowledge/development/s3-bug-c-halted-stale-check-dev-log-2026-05-10.md. You are the Bellows QA Analyst verifying the fix shipped in Step 1.

VERIFICATION CHECKS

(1) Read bellows/bellows.py and confirm:
    (a) Inside `_consume_verdicts()`, the stale-check `else` branch now contains a parallel halted-* detection loop that scans `decisions_path` for filenames starting with `halted-` and containing `plan_slug`
    (b) The original Done/ check is unchanged
    (c) The print message in the `if stale:` branch reflects the broader detection (mentions both "Done/" and "halted-")
    (d) The `not stale` branch (the retry-loop log message) is unchanged

(2) Read bellows/tests/test_consume_verdicts.py and confirm:
    (a) `test_consume_verdicts_marks_resolved_processed_when_plan_halted` exists
    (b) It sets up a halted-* plan in decisions_path (NOT in Done/) and asserts the verdict file is moved to processed-*
    (c) No other tests modified

(3) Run the consume_verdicts test suite fresh and capture full output:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest tests/test_consume_verdicts.py -v 2>&1 | tee bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/pytest_consume_verdicts.txt

    Verify the new test appears with PASSED status. Existing tests unchanged.

(4) Run the full test suite for collateral damage check:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest 2>&1 | tee bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/pytest_full.txt

    Expected delta: +1 new test passing, 0 regressions, 1 pre-existing `test_run_step_timeout` failure unchanged.

(5) Behavioral spot-check: write a small Python snippet (not committed) that exercises the halted-* detection end-to-end:
    - Creates a temp directory acting as `decisions_path` with a `halted-executable-spotcheck-2026-05-10.md` file
    - Creates a temp `verdicts/resolved/` with `verdict-executable-spotcheck-2026-05-10-step-1.md` containing `verdict: stop`
    - Creates an empty `verdicts/pending/`
    - Calls `_consume_verdicts` (or constructs a Bellows instance with this temp setup and calls it)
    - Asserts the verdict file is moved to `processed-*`
    - Asserts no log line containing "leaving in resolved/ for retry" was printed (capture stdout)
    - Print PASSED / FAILED with diagnostic info

QA REPORT FORMAT

Deposit at bellows/knowledge/qa/s3-bug-c-halted-stale-check-qa-2026-05-10.md with:
- Status table: each verification check (1a–1d, 2a–2c, 3, 4, 5) with ✅/❌ and one-line evidence
- Pytest tail outputs (consume_verdicts suite + full suite) inline
- Behavioral spot-check output verbatim
- Final verdict line: ALL CHECKS PASSED or LIST OF FAILURES

RULE 20 SELF-CHECK

End the QA report with the canonical Rule 20 self-check Python block from PLANNER_TEMPLATE Rule 20. **USE THE VERBATIM TEMPLATE** — paste the block from PLANNER_TEMPLATE Rule 20 with only variable substitutions. The literal banner string `Rule 20 — QA Self-Check Results` (em-dash U+2014) and the literal output line `PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.` are load-bearing strings the Bellows gate enforces.

ACTUALLY EXECUTE THE BLOCK after writing the QA report (use python3 to run it as a script or inline) and include the literal stdout in the QA report. Do NOT just include the script.

Variable substitutions:
- plan_slug = "executable-s3-bug-c-halted-stale-check-2026-05-10"
- qa_report_path = "bellows/knowledge/qa/s3-bug-c-halted-stale-check-qa-2026-05-10.md"
- evidence_dir = "bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/"
- required_evidence_files = ["pytest_consume_verdicts.txt", "pytest_full.txt"]

GIT COMMITS

ONE commit (bellows repo):
    docs(qa): S3 Bug C halted stale-check verification

Include the QA report and both evidence files. Push.

OUTPUT RECEIPT
End with status (Complete / Blocked), final verdict line, and deposit paths.
```

**STOP. Do NOT proceed beyond Step 2 without CEO verdict. After Step 2 completes, the Planner moves the plan to Done/ via Filesystem:move_file.**
