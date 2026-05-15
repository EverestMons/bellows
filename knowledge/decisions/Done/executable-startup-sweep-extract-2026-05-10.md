# Executable — Extract `_perform_startup_sweep` from `Bellows.start()`

**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Tier:** Small
**Total Steps:** 2

**pause_for_verdict:** after_step_1

---

## Context

Closes BACKLOG `2026-05-01: test_startup_sweep_removes_done_plan_orphans uses inline-replicated sweep logic`. Diagnostic at `bellows/knowledge/research/startup-sweep-test-refactor-surface-2026-05-05.md` mapped the refactor surface: ~24 LOC net reduction, no behavioral change, zero observer/event-loop entanglement.

The current `tests/test_consume_verdicts.py::test_startup_sweep_removes_done_plan_orphans` replicates the startup-sweep logic inline. This refactor extracts the sweep into a private method on `Bellows` so the test can call production code directly. Variant (i) chosen: the new method returns the list of removed filenames; the print loop stays in `Bellows.start()` so stdout behavior is unchanged.

---

## Execution Map

Step 1 (DEV) → Step 2 (QA)

---

## STEP 1 — Developer: extract `_perform_startup_sweep` and migrate test

**Agent:** Bellows Developer (`bellows/agents/developer.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/bellows/`
**Deposits:**
- `bellows/bellows.py` (modified — new method + simplified `start()` call site)
- `bellows/tests/test_consume_verdicts.py` (modified — test exercises production directly)
- `bellows/knowledge/development/startup-sweep-extract-2026-05-10.md` (dev log)

### Prompt

You are the Bellows Developer. Read your agent file at `bellows/agents/developer.md` and the diagnostic at `bellows/knowledge/research/startup-sweep-test-refactor-surface-2026-05-05.md` before making any code edits.

This is a refactor — no behavioral change. The startup sweep block currently lives inline inside `Bellows.start()` in `bellows/bellows.py` (the block beginning with the comment `# One-time startup sweep: remove orphaned verdict requests`, immediately after `time.sleep(3)`). Extract it into a private method on `Bellows` with this signature:

```python
def _perform_startup_sweep(self) -> list[str]:
    """Remove orphaned verdict-request files from verdicts/pending/.

    Returns the list of removed filenames (basenames only, no path).
    A verdict-request file is orphaned if its slug does not appear in any
    active plan in the watched-project decisions directories (active = the
    plan is in-progress, verdict-pending, or a runnable un-claimed plan).
    Plans in Done/ are NOT considered active, so their orphaned verdict
    requests are removed.
    """
```

### Variant choice

This is **variant (i)** from the diagnostic:
- The new method returns the list of removed filenames.
- The print loop ("Bellows: startup cleanup — N orphaned verdict requests removed" + per-file lines) **stays in `Bellows.start()`** so stdout output is byte-identical to the pre-refactor behavior.
- Do NOT move the prints inside `_perform_startup_sweep`.

### Concrete edits

**Edit 1 — `bellows/bellows.py`:** Add the new `_perform_startup_sweep` method to the `Bellows` class. Place it directly after `_consume_verdicts` and before `start`. The body must be a faithful move of the existing inline block (lines beginning `active_slugs = set()` through `orphaned_removed.append(pf)`), with these adjustments:
- Use `self.config.get("watched_projects", [])` (already does in the inline block — keep as-is).
- The `pending_dir` line stays `BELLOWS_ROOT / "verdicts" / "pending"` (module-level constant, not on `self`).
- Return `orphaned_removed` at the end.
- Do NOT include the trailing `if orphaned_removed: print(...)` block — that stays in `start()`.

**Edit 2 — `bellows/bellows.py`:** Replace the inline block in `start()` with a call to the new method. The inline block to remove is the section starting `# One-time startup sweep: remove orphaned verdict requests` and ending with the closing `orphaned_removed.append(pf)` line (do not remove the trailing print block — keep it, but it now reads from the returned list). After the edit, `start()` should contain:

```python
        # One-time startup sweep: remove orphaned verdict requests
        orphaned_removed = self._perform_startup_sweep()
        if orphaned_removed:
            print(f"Bellows: startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed")
            for rm_name in orphaned_removed:
                print(f"  - {rm_name}")
```

**Edit 3 — `bellows/tests/test_consume_verdicts.py`:** In `test_startup_sweep_removes_done_plan_orphans`, replace the inline replica (the entire `with patch("bellows.BELLOWS_ROOT", tmp_path):` block that constructs `active_slugs` and iterates `pending/`) with a direct call to the new method. The block to replace begins at the `with patch("bellows.BELLOWS_ROOT", tmp_path):` line and ends at `orphaned_removed.append(pf)`. The replacement is:

```python
        with patch("bellows.BELLOWS_ROOT", tmp_path):
            orphaned_removed = b._perform_startup_sweep()
```

Keep both existing assertions (`assert not orphan_file.exists()` and `assert "verdict-request-bar-2026-05-01-step-1.md" in orphaned_removed`) unchanged.

Also: delete the now-obsolete `NOTE: Done/ loop intentionally absent` comment that lived inside the removed inline block. (The comment is no longer applicable; the test now exercises production code which inherently lacks the Done/ loop.)

### Test discipline

Run the full bellows test suite (`pytest -x`) after the edits. The two `test_consume_verdicts.py` tests that touch this surface must pass; the broader suite must show **zero new failures** relative to the pre-refactor baseline. The pre-existing `test_run_step_timeout` failure is the only acceptable continuing failure.

If any test fails that was passing before, stop and report — do NOT modify other tests to make them pass.

### Output

After landing the three edits and confirming tests pass, write a dev log at `bellows/knowledge/development/startup-sweep-extract-2026-05-10.md` covering:

1. The three concrete edits made (file, line range, summary of change).
2. LOC delta — count added and removed lines per file, net total.
3. Test suite result — pass count, pre-existing failure count, any new failures (must be zero).
4. `extract_total_steps`-style spot check (optional): in a Python REPL or one-liner, instantiate `Bellows(minimal_config)` against an empty temp dir and confirm `_perform_startup_sweep()` returns `[]` without raising.
5. Commit SHA.

### Output Receipt

When complete, output a receipt block in this exact format:

```
**Step:** 1
**Status:** Complete
**Deposits:**
- bellows/bellows.py (modified)
- bellows/tests/test_consume_verdicts.py (modified)
- bellows/knowledge/development/startup-sweep-extract-2026-05-10.md (created)
**Commit:** <short-sha>
```

STOP after Step 1. Do not advance to Step 2 — the Planner verifies the dev work before authorizing QA.

---

## STEP 2 — QA: verify the refactor

**Agent:** Bellows QA (`bellows/agents/qa.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/bellows/`
**Deposits:**
- `bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md` (QA report)

### Prompt

You are the Bellows QA agent. Read your agent file at `bellows/agents/qa.md` and the dev log at `bellows/knowledge/development/startup-sweep-extract-2026-05-10.md` before starting verification.

This refactor changed two files and added one. Verify the following properties:

### Verification matrix

| # | Property | How to check |
|---|----------|--------------|
| 1 | New method exists with correct signature | grep `bellows/bellows.py` for `def _perform_startup_sweep(self) -> list[str]:` — must match exactly |
| 2 | New method placement | Method must be defined inside the `Bellows` class, between `_consume_verdicts` and `start` |
| 3 | New method returns the orphan list | Read the method body — confirm `return orphaned_removed` is the last statement |
| 4 | Prints did NOT move into the method | grep the new method body — must NOT contain any `print(` call referencing "startup cleanup" or the per-file removal log |
| 5 | `start()` call site simplified | grep `bellows/bellows.py` `start()` for `orphaned_removed = self._perform_startup_sweep()` — must appear exactly once |
| 6 | `start()` retains print loop | grep `start()` for `f"Bellows: startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed"` and the per-file `for rm_name in orphaned_removed:` loop — both must still be present, immediately after the method call |
| 7 | `start()` no longer contains the inline sweep | grep `start()` body for `active_slugs = set()` — must NOT appear in `start()` anymore (it lives only inside `_perform_startup_sweep` now) |
| 8 | Test calls production directly | grep `tests/test_consume_verdicts.py::test_startup_sweep_removes_done_plan_orphans` for `b._perform_startup_sweep()` — must appear exactly once |
| 9 | Test no longer replicates sweep logic | Same test must NOT contain `active_slugs = set()` anywhere in its body (the inline replica is fully removed) |
| 10 | Stale NOTE comment removed | grep the test for `NOTE: Done/ loop intentionally absent` — must NOT appear |
| 11 | Existing assertions preserved | Both `assert not orphan_file.exists()` and `assert "verdict-request-bar-2026-05-01-step-1.md" in orphaned_removed` must remain at end of test |
| 12 | Full test suite passes | Run `pytest` from `/Users/marklehn/Desktop/GitHub/bellows/` — record total passed, expected pre-existing failure (`test_run_step_timeout`), and any unexpected failures (must be zero) |
| 13 | LOC delta direction matches diagnostic | Compute net delta `bellows.py` + `tests/test_consume_verdicts.py` against pre-refactor — must be a net reduction (diagnostic predicted ~–24 LOC; ±5 LOC tolerance) |

### QA report format

Write the report to `bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md` with one row per verification matrix item: status (✅ / ❌), evidence (grep snippet or test output line cited verbatim). End with a single summary line: `Refactor verified — N/13 checks passed.`

### Rule 20 self-check

After writing the QA report, run the following Python block in your working directory and include its output verbatim at the end of the QA report:

```python
import os
RULE_20_BANNER = "RULE 20 SELF-CHECK"
print(RULE_20_BANNER)
deposits = [
    "bellows/bellows.py",
    "bellows/tests/test_consume_verdicts.py",
    "bellows/knowledge/development/startup-sweep-extract-2026-05-10.md",
    "bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md",
]
root = "/Users/marklehn/Desktop/GitHub/"
all_ok = True
for d in deposits:
    full = os.path.join(root, d)
    exists = os.path.isfile(full)
    print(f"  {d}: {'OK' if exists else 'MISSING'}")
    if not exists:
        all_ok = False
print("RULE 20 SELF-CHECK PASSED" if all_ok else "RULE 20 SELF-CHECK FAILED")
```

### Output Receipt

```
**Step:** 2
**Status:** Complete
**Deposits:**
- bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md (created)
**Verification:** N/13 checks passed
**Test suite:** <passed_count> passed, <pre_existing_failure_count> pre-existing failure, <new_failure_count> new failures
```

STOP after Step 2. Final-step verdict will be issued by the Planner after Rule 22 verification.

---

## Deliverables Summary

| Step | Agent | Deliverable | Location |
|------|-------|-------------|----------|
| 1 | DEV | `bellows.py` (modified) | `bellows/bellows.py` |
| 1 | DEV | test file (modified) | `bellows/tests/test_consume_verdicts.py` |
| 1 | DEV | dev log (created) | `bellows/knowledge/development/startup-sweep-extract-2026-05-10.md` |
| 2 | QA | QA report (created) | `bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md` |
