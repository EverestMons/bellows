# Executable — Thread wt_path into _gate_rule_20_self_check

**Project:** bellows | **Type:** executable | **Steps:** 2 | **Priority:** 1 | **auto_close:** false

## Context

Diagnostic at `bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md` identified Root Cause 1 (HIGH confidence) for the recurring `rule_20_self_check` false-positive class observed on 2026-05-07 and 2026-05-08:

`_gate_rule_20_self_check` (gates.py:273) was missed by the 2026-05-06 worktree-aware fix (`executable-deposit-exists-worktree-aware-2026-05-06`). The function does not accept or thread `wt_path` to `_resolve_deposit_path`. Since `gates.check()` runs BEFORE `_teardown_worktree`, the worktree directory is alive at gate evaluation time and contains the agent's committed files — but `_gate_rule_20_self_check` only attempts Strategies 1–3 (all of which look at the main project tree where the cherry-pick has not yet landed the files), producing false-positive "file not found" failures.

Fix: mirror the 2026-05-06 pattern that was applied to `_gate_deposit_exists`. ~5 LOC.

## Execution Map

Step 1 (DEV) → Step 2 (QA)

## STEP 1 — Bellows Developer: thread wt_path into _gate_rule_20_self_check

**Agent:** Bellows Developer
**Deposits:**
- `bellows/gates.py` (modified)
- `bellows/tests/test_gates.py` (modified — new regression test added)
- `bellows/knowledge/development/rule-20-self-check-wt-path-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_DEVELOPER.md, then bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md (the diagnostic findings — Root Cause 1, Recommended Fix). You are the Bellows Developer implementing a tightly-scoped fix.

OBJECTIVE
Thread `wt_path` through `_gate_rule_20_self_check` so the function can resolve deposit paths via Strategy 0 (worktree-first) when `wt_path` is provided. Mirrors the 2026-05-06 pattern already applied to `_gate_deposit_exists`.

EXACT CHANGES (gates.py)

1. `_gate_rule_20_self_check` signature (currently around line 273): add `wt_path=None` as the final keyword argument.

2. Inside `_gate_rule_20_self_check`, the call to `_resolve_deposit_path` (currently around line 292): add `wt_path=wt_path` kwarg. There is exactly one such call inside this function.

3. The caller in `gates.check()` (currently around line 105): pass `wt_path=wt_path` to the `_gate_rule_20_self_check(...)` call. Mirror the kwarg style used at line 101 for `_gate_deposit_exists`.

VERIFY THE LINE NUMBERS in the actual file before editing — the diagnostic captured them but the file may have shifted. Use `grep -n` or read the file fresh.

REGRESSION TEST (tests/test_gates.py)

Add ONE new test that locks in the fix:

`test_rule_20_self_check_resolves_via_worktree_path` — constructs a temp directory simulating a worktree containing a QA report file with a Rule 20 banner. Constructs a separate temp directory simulating the project_path WITHOUT that file. Calls `gates.check()` with `wt_path` pointing at the worktree, `project_path` pointing at the empty project. Asserts the gate result has no `rule_20_self_check` failure (passes via Strategy 0). The test should fail without the fix and pass with it.

If you find an existing pattern in test_gates.py for testing `_gate_deposit_exists` with `wt_path`, model the new test after it.

VERIFY

Run the targeted gates test file:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest tests/test_gates.py -v 2>&1 | tail -40

Capture the result. Expected: all existing tests pass + the new test passes. Append the captured pytest output to your dev log.

DEV LOG

Deposit `bellows/knowledge/development/rule-20-self-check-wt-path-2026-05-10.md` with:
- The exact diff applied to gates.py (3 small edits)
- The exact new test added to test_gates.py
- The pytest output (full output of the gates test file run)
- Confirmation that no other gates.py functions were touched
- Confirmation that no other test files were touched

GIT COMMITS

ONE commit, conventional message:
    fix(gates): thread wt_path into _gate_rule_20_self_check (BACKLOG 2026-05-07)

Include all three files: gates.py, tests/test_gates.py, the dev log. Push.

CONSTRAINTS
- Do NOT modify any other gate function. Surgical fix only.
- Do NOT modify _resolve_deposit_path itself. The function already accepts wt_path correctly; only the caller chain needs updating.
- Do NOT add wt_path threading to gates that don't currently use deposit paths (e.g., _gate_no_permission_denials, _gate_scope_check). Those have different semantics.
- Do NOT change the 2026-05-06 fix for _gate_deposit_exists. Leave it intact.
- Run pre-commit hooks if configured. If any hook fails, fix the failure and re-attempt.

OUTPUT RECEIPT
End with status (Complete / Blocked), summary of changes (lines added/removed), and deposit paths.
```

## STEP 2 — Bellows QA: verify the fix

**Agent:** Bellows QA
**Deposits:**
- `bellows/knowledge/qa/rule-20-self-check-wt-path-qa-2026-05-10.md`
- `bellows/knowledge/qa/evidence/rule-20-self-check-wt-path-2026-05-10/pytest_gates.txt`

**Prompt:**

```
Read agents/BELLOWS_QA.md, then the diagnostic at bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md (Root Cause 1 and Recommended Fix sections), then the dev log at bellows/knowledge/development/rule-20-self-check-wt-path-2026-05-10.md. You are the Bellows QA Analyst verifying the fix shipped in Step 1.

VERIFICATION CHECKS

(1) Read bellows/gates.py and confirm:
    (a) `_gate_rule_20_self_check` signature includes `wt_path=None`
    (b) The `_resolve_deposit_path` call inside `_gate_rule_20_self_check` passes `wt_path=wt_path`
    (c) The `gates.check()` caller of `_gate_rule_20_self_check` passes `wt_path=wt_path`
    (d) `_gate_deposit_exists` is unchanged (still has its own `wt_path` threading from 2026-05-06)

(2) Read bellows/tests/test_gates.py and confirm:
    (a) The new `test_rule_20_self_check_resolves_via_worktree_path` test exists
    (b) It constructs a worktree-vs-project directory split and verifies Strategy 0 resolution
    (c) No other tests were modified

(3) Run the gates test suite fresh:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest tests/test_gates.py -v 2>&1 | tee bellows/knowledge/qa/evidence/rule-20-self-check-wt-path-2026-05-10/pytest_gates.txt

    Check the tail of the output for: number of tests passed, number failed, and confirmation that the new test name appears with PASSED status.

(4) Run the full test suite to check for collateral damage:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest 2>&1 | tail -20

    Append to the QA report: pre-fix baseline failure count (you may need to consult prior session reports if any) versus post-fix failure count. The expected delta is +1 new test passing, 0 regressions.

(5) Behavioral spot-check: write a small Python snippet (not committed, just for verification) that:
    - Imports `from bellows.gates import _resolve_deposit_path, check`
    - Creates two temp directories — one acting as worktree containing a fake QA report file with the literal string `RULE 20 SELF-CHECK PASSED`, one acting as project_path with no such file
    - Calls `check()` with a minimal parsed dict, plan_text containing a `## STEP 1 — QA` header and a `**Deposits:**` block referencing the QA report path, step_number=1, project_path=empty_dir, wt_path=worktree_dir
    - Asserts the returned gate_result["failures"] does NOT contain a `rule_20_self_check` failure
    - Print PASSED or FAILED
    Capture the output and include it in the QA report.

QA REPORT FORMAT

Deposit at bellows/knowledge/qa/rule-20-self-check-wt-path-qa-2026-05-10.md with:
- Status table: each verification check (1a–1d, 2a–2c, 3, 4, 5) with ✅/❌ and one-line evidence
- Pytest tail outputs (gates suite + full suite) inline
- Behavioral spot-check output inline
- Final verdict line: ALL CHECKS PASSED or LIST OF FAILURES

RULE 20 SELF-CHECK

End the QA report with the canonical Rule 20 Python self-check block. ACTUALLY EXECUTE THE BLOCK and include the output (must print "SELF-CHECK PASSED" verbatim if the QA report and evidence file both exist on disk). The block must use absolute paths to /Users/marklehn/Desktop/GitHub/bellows/...

```python
import os
deposits = [
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/rule-20-self-check-wt-path-qa-2026-05-10.md",
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/rule-20-self-check-wt-path-2026-05-10/pytest_gates.txt",
]
missing = [d for d in deposits if not os.path.isfile(d)]
if missing:
    print(f"SELF-CHECK FAILED — missing: {missing}")
else:
    print("RULE 20 SELF-CHECK PASSED")
```

GIT COMMITS

ONE commit:
    docs(qa): rule_20_self_check wt_path fix verification (BACKLOG 2026-05-07)

Include the QA report and the pytest evidence file. Push.

OUTPUT RECEIPT
End with status (Complete / Blocked), final verdict line, and deposit paths.

NOTE FOR PLANNER: This QA step will run pre-Bellows-restart, meaning the OLD gates.py code is still loaded in the running daemon. The fix only takes effect after CEO restarts Bellows. The QA step's own rule_20_self_check gate evaluation may therefore still trip the false positive on this very plan — that's expected; it doesn't reflect the correctness of the shipped fix. Planner will Rule 22-verify the QA report and override.
```

**STOP. Do NOT proceed beyond Step 2 without CEO verdict. After Step 2 completes, the Planner moves the plan to Done/ via Filesystem:move_file.**
