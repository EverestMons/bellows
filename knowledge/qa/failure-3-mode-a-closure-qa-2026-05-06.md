# QA Report — Failure 3 Mode A Closure: System Prompt + Lifecycle Guard

**Date:** 2026-05-06
**Plan:** `executable-failure-3-mode-a-closure-2026-05-06`
**Step:** 2 (QA)
**Agent:** Bellows QA

---

## Summary

All 5 checks pass. A1 (system prompt prohibition) is correctly implemented in `runner.py` with exact CEO-authorized wording. B2 (lifecycle guard) is correctly implemented at both `runner.run_step` invocation sites in `bellows.py` with detection, recovery, and synthetic gate failure injection. BACKLOG update in invoice-pulse is committed separately (correct cross-repo handling). All 6 new tests pass; full suite is 212 tests (211 passed, 1 known pre-existing failure `test_run_step_timeout`). Both repos have appropriate commits.

---

## Check 1 — A1 verification (runner.py)

| Criterion | Status | Evidence |
|---|---|---|
| `BELLOWS_AGENT_SYSTEM_PROMPT` constant exists at module level | PASS | `runner.py:17` — constant defined after imports, before `_write_log()` |
| Constant text matches CEO-authorized wording | PASS | Verbatim match confirmed against Step 1 Change 1 specification. Text: `"""You are executing as a Bellows-dispatched agent. BINDING CONSTRAINT: You must NEVER move plan files to Done/. You must NEVER execute mv, shutil.move, os.rename, or any equivalent operation targeting a Done/ directory within the knowledge/decisions/ tree. The Planner performs all Done/ moves after verification. Your final operation is ALWAYS the commit. If you find yourself reasoning about moving files to Done/, STOP — that is not your responsibility."""` |
| `cmd` list contains `--append-system-prompt` followed by `BELLOWS_AGENT_SYSTEM_PROMPT` | PASS | `runner.py:41` — `"--append-system-prompt", BELLOWS_AGENT_SYSTEM_PROMPT,` in cmd list, positioned after `--allowedTools` and before `if session_id is not None:` block |
| No other code modified beyond constant and cmd list | PASS | Diff shows exactly +3 lines in runner.py: 1 constant definition line, 1 blank line, 1 cmd list entry. No other changes. |

**grep evidence:**
```
17:BELLOWS_AGENT_SYSTEM_PROMPT = """You are executing as a Bellows-dispatched agent. BINDING CONSTRAINT: ...
41:        "--append-system-prompt", BELLOWS_AGENT_SYSTEM_PROMPT,
```

---

## Check 2 — B2 verification (bellows.py)

| Criterion | Status | Evidence |
|---|---|---|
| Mode A detection block after BOTH `runner.run_step` invocation sites | PASS | Site 1: `bellows.py:311-326` (initial step). Site 2: `bellows.py:398-411` (loop continuation). Both blocks are structurally identical. |
| Detection logic checks `os.path.exists(inprogress_path)` and `os.path.exists(done_check)` | PASS | Both sites: `if not os.path.exists(inprogress_path):` then `done_check = os.path.join(plan_dir, "Done", base_filename)` then `if os.path.exists(done_check):` |
| Recovery uses `shutil.move(done_check, inprogress_path)` | PASS | Site 1: `bellows.py:320`. Site 2: `bellows.py:405`. Both wrapped in try/except with `mode_a_detected = True` on both success and exception. |
| Synthetic gate failure block after `gates.check(...)` at both sites | PASS | Site 1: `bellows.py:332-337`. Site 2: `bellows.py:417-422`. Both run after `gate_result = gates.check(...)`. |
| Synthetic failure dict has `gate == "unauthorized_done_move"` | PASS | Both sites: `"gate": "unauthorized_done_move"` with evidence string referencing `base_filename` and "Failure 3 Mode A violation" |
| `gate_result["passed"] = False` set when `mode_a_detected` | PASS | Both sites: `gate_result["passed"] = False` inside `if mode_a_detected:` block |

**grep evidence:**
```
314:        mode_a_detected = False
321:                    mode_a_detected = True
324:                    mode_a_detected = True  # still flag the failure even if recovery failed
332:        if mode_a_detected:
334:                "gate": "unauthorized_done_move",
399:            mode_a_detected = False
406:                        mode_a_detected = True
409:                        mode_a_detected = True
417:            if mode_a_detected:
419:                    "gate": "unauthorized_done_move",
```

**Placement verification:** Both detection blocks are positioned AFTER `record_run` and BEFORE `_capture_git_diff(post_diff)` / `gates.check(...)`, matching the plan specification exactly.

---

## Check 3 — BACKLOG update verification (invoice-pulse)

| Criterion | Status | Evidence |
|---|---|---|
| 2026-05-05 entry replaced with CONFIRMED text | PASS | `BACKLOG.md:16` — entry begins with `- 2026-05-05: **CONFIRMED Mode A reproduction** — promoted from "possible" 2026-05-06.` |
| References `failure-3-mode-a-occurrence-investigation-2026-05-06.md` | PASS | Present in BACKLOG.md line 16: `Diagnostic at \`bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md\`` |
| References `failure-3-mode-a-closure-design-2026-05-06.md` | PASS | Present in BACKLOG.md line 16: `Closure design at \`bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md\`` |
| Old three-candidate-explanation text no longer present | PASS | No matches for "Possible Mode A reproduction", "three-candidate", or "check git log on the bellows repo" in the file |

---

## Check 4 — Test execution

### Targeted tests (test_runner.py + test_bellows.py)

```
95 passed, 1 warning in 0.35s
```

All 95 tests pass including the 6 new tests:

**test_runner.py — A1 verification (1 test):**
- `test_append_system_prompt_flag_in_command` — PASS

**test_bellows.py — B2 verification (5 tests):**
- `test_mode_a_detected_and_recovered` — PASS
- `test_mode_a_no_detection_normal_flow` — PASS
- `test_mode_a_missing_file_not_in_done` — PASS
- `test_mode_a_recovery_failure` — PASS
- `test_mode_a_synthetic_failure_in_verdict_request` — PASS

All pre-existing tests in both files continue to pass.

### Full suite

```
1 failed, 211 passed, 1 warning in 6.94s
```

| Metric | Value |
|---|---|
| Total tests | 212 |
| Passed | 211 |
| Failed | 1 |
| Baseline comparison | 212 > ~205 baseline |

**Single failure:** `tests/test_runner_parser.py::test_run_step_timeout` — known pre-existing failure (documented in plan as expected). This test patches `subprocess.run` but `runner.run_step` uses `subprocess.Popen`; the mock doesn't intercept the actual code path. Pre-dates this plan. No regression.

---

## Check 5 — Commit verification

### Bellows repo

```
commit 1256879db7e990bc93a5b7298f625ae4b70db8a1
Author: Mark Lehn <marklehn@icloud.com>
Date:   Wed May 6 11:26:13 2026 -0500

    feat: Failure 3 Mode A closure — system prompt + lifecycle guard

    Two-layer closure for Failure 3 Mode A (agent moves plan to Done/
    without authorization).

    A1 — System prompt prohibition (runner.py):
    Adds --append-system-prompt flag to claude -p invocation with binding
    behavioral constraint. Constraint lives in system prompt layer, above
    plan text in prompt hierarchy.

    B2 — Lifecycle guard (bellows.py):
    After runner.run_step returns, detects filesystem state divergence
    (in-progress missing + Done/ file present), recovers by moving file
    back to in-progress, injects synthetic gate failure so plan pauses
    for verdict via existing gate-failure pause logic.

    Plus tests: 1 in test_runner.py (A1 cmd argv), 5 in test_bellows.py
    (B2 detection, recovery, edge cases).

    Closes Failure 3 Mode A reproductions observed 2026-05-06.
    References:
    - bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md
    - bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md

    Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

 bellows/bellows.py            |  44 ++++++++
 bellows/runner.py             |   3 +
 bellows/tests/test_bellows.py | 253 ++++++++++++++++++++++++++++++++++++++++++
 bellows/tests/test_runner.py  |  14 +++
 4 files changed, 314 insertions(+)
```

| Criterion | Status | Evidence |
|---|---|---|
| Single commit at HEAD | PASS | `1256879` is HEAD |
| Commit message follows format | PASS | `feat:` prefix, three-section body (A1, B2, tests), references section |
| Files correct | PASS | Exactly 4 files: `bellows.py`, `runner.py`, `tests/test_bellows.py`, `tests/test_runner.py` |

### invoice-pulse repo (cross-repo BACKLOG)

```
commit 1f9bf4102692414fb7cbdef41f1bde4157bb530d
Author: Mark Lehn <marklehn@icloud.com>
Date:   Wed May 6 11:26:19 2026 -0500

    docs: BACKLOG 2026-05-05 Mode A entry promoted from possible to confirmed

 knowledge/BACKLOG.md | 8 ++++++--
 1 file changed, 6 insertions(+), 2 deletions(-)
```

| Criterion | Status | Evidence |
|---|---|---|
| BACKLOG.md committed in invoice-pulse (separate repo) | PASS | Commit `1f9bf41` in invoice-pulse, 6 seconds after bellows commit |
| Not bundled in bellows commit | PASS | Bellows commit has exactly 4 files, none in invoice-pulse |

**FLAG resolution:** The plan noted invoice-pulse is a separate repo. Step 1 correctly handled this by making separate commits — bellows commit `1256879` for code+tests, invoice-pulse commit `1f9bf41` for BACKLOG.md. This is the correct cross-repo behavior.

**Note:** The bellows commit message references "Plus BACKLOG hygiene" is absent from the commit body. The commit message ends at the References section. This is a minor deviation — the BACKLOG change is documented in its own commit in invoice-pulse. Not a blocking issue.

---

## Overall verdict

**PASS**

All 5 checks pass. No regressions. Both A1 and B2 are implemented exactly per specification, at both invocation sites, with correct placement relative to `record_run` and `gates.check`. All 6 new tests pass. BACKLOG update committed correctly in the separate invoice-pulse repo. The only test failure (`test_run_step_timeout`) is a known pre-existing issue unrelated to this plan.

---

## Rule 20 self-check

```
============================================================
Rule 20 Self-Check
============================================================
✅ QA report exists
✅ Has Summary
✅ Has Check 1 (A1)
✅ Has Check 2 (B2)
✅ Has Check 3 (BACKLOG)
✅ Has Check 4 (Tests)
✅ Has Check 5 (Commit)
✅ Has Overall verdict
✅ File is non-trivial (>3KB)

SELF-CHECK PASSED
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all Step 1 deliverables: A1 system prompt prohibition in runner.py (constant text, cmd list placement), B2 lifecycle guard in bellows.py (both invocation sites, detection + recovery + synthetic gate failure), BACKLOG update in invoice-pulse (cross-repo commit), test execution (6 new tests passing, 212 total, 1 known pre-existing failure), and commit verification (correct format, correct files, cross-repo handling).

### Files Deposited
- `bellows/knowledge/qa/failure-3-mode-a-closure-qa-2026-05-06.md` — QA report for Failure 3 Mode A closure plan

### Files Created or Modified (Code)
- None (QA is read-only verification)

### Decisions Made
- Classified `test_run_step_timeout` failure as known pre-existing (not a regression)
- Classified cross-repo commit split as correct behavior (not a Step 1 incompleteness)

### Flags for CEO
- Overall verdict: **PASS** — all checks pass, no regressions, no blocking issues
- Minor note: bellows commit message omits the "Plus BACKLOG hygiene" line from the specified format, but the BACKLOG change is properly committed in its own repo

### Flags for Next Step
- None (this is the terminal step)
