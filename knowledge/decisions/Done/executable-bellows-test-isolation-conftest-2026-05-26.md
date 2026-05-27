# Bellows Test-Isolation Conftest — Create tests/conftest.py
**Date:** 2026-05-26 | **Tier:** Executable | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

## CEO Context

The diagnostic at `bellows/knowledge/research/bellows-test-isolation-conftest-fixture-shape-2026-05-26.md` (Done 2026-05-26) audited the test-isolation orphan pattern and produced the complete fixture-shape blueprint. SA confirmed `verdict.VERDICTS_DIR` patches cleanly across all three call sites with zero direct imports and no subprocess defeat, identified exactly 2 leaking tests (both dispatch-spawn vector), and specified a 7-LOC function-scoped autouse fixture. No production code change required. The CEO-locked decisions (Option (a), module-level constant in verdict.py) are honored by the existing `VERDICTS_DIR` constant — no governance escalation needed.

This is a pure additive change — single new file `bellows/tests/conftest.py`. No edits to existing files (the SA diagnostic explicitly confirmed no test modifications are required — the fixture handles both leakers automatically). Test scope is `full-suite` per Rule 21 because the autouse fixture affects every test in the suite, the broadest possible blast radius.

DEV creates the file with the exact 7-LOC body from Diagnostic Deliverable C. QA runs the full suite to confirm zero regressions and verifies no new files appear in production `bellows/verdicts/pending/` after the run (the load-bearing verification — this is what the conftest is supposed to prevent).

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/executable-bellows-test-isolation-conftest-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-test-isolation-conftest-2026-05-26.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip the domain glossary read — this is a single-file additive change with the body pre-specified by SA.
>
> **Task.** Create `bellows/tests/conftest.py` with the function-scoped autouse fixture designed in the SA diagnostic at `bellows/knowledge/research/bellows-test-isolation-conftest-fixture-shape-2026-05-26.md` (Audit Deliverable C). The file does NOT currently exist (SA verified `bellows/tests/` has 16 test files but no conftest.py).
>
> **Pre-edit verification.** Confirm `bellows/tests/conftest.py` does NOT exist via `ls bellows/tests/conftest.py` (expect: No such file). Confirm `verdict.py:14` still reads `VERDICTS_DIR = BELLOWS_ROOT / "verdicts"` via `sed -n '14p' bellows/verdict.py`. Quote both outputs in the dev log.
>
> **Exact file body (create verbatim).** The conftest body is pre-approved by SA Deliverable C:
>
> ```python
> # tests/conftest.py
> import pytest
>
>
> @pytest.fixture(autouse=True)
> def isolate_verdicts_dir(monkeypatch, tmp_path):
>     """Redirect verdict.VERDICTS_DIR to tmpdir so tests never write to production verdicts/pending/."""
>     import verdict
>     monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")
> ```
>
> 7 lines (including blank line and trailing newline). Do NOT add additional fixtures, do NOT add session-scoped variants, do NOT add opt-out markers — the SA diagnostic confirmed function-scoped is correct (monkeypatch is inherently function-scoped) and no opt-out is needed (existing test-level `patch.object` calls in `test_verdict.py` already override within their `with` blocks per SA Audit C "Opt-out mechanism: not required" paragraph).
>
> **Test the fixture.** Run `cd bellows && python -m pytest tests/ -q 2>&1 | tail -20` and confirm: (a) the suite still completes, (b) the previously-known carry-over failures (5 from session 7 baseline: 4 test_decisions.py worktree-context failures + 1 test_runner_parser.py timeout) are the only failures, (c) no new regressions. Quote the final pytest summary line in the dev log.
>
> **Verify the leak is closed.** After the test run, run `ls bellows/verdicts/pending/ | grep -v "^archived$"` and confirm the output is empty (no new orphan verdict-request-* files). Quote the command and output in the dev log. This is the load-bearing verification — if the directory contains files, the fixture is not working and the plan must NOT proceed.
>
> **Output Receipt.** Standard format. List `bellows/tests/conftest.py` under "Files Created or Modified (Code)". List the deposit file under "Files Deposited". Flag for QA: full-suite run required; verify zero orphans in verdicts/pending/ after pytest invocation.
>
> **Deposits:**
> - `bellows/knowledge/development/bellows-test-isolation-conftest-2026-05-26.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — Bellows QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/verdict-pending-executable-bellows-test-isolation-conftest-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-test-isolation-conftest-2026-05-26.md")`.
>
> You are the Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. Skip the domain glossary read — this is verification of a single-file additive change.
>
> **FIRST — Deliverable Verification.** Read the prior DEV step's Output Receipt "Files Created or Modified (Code)" list. For every listed file: verify it exists on disk and contains the described change. For `bellows/tests/conftest.py`: confirm the file exists, contains an `@pytest.fixture(autouse=True)` decorator, contains a function named `isolate_verdicts_dir`, contains `monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")`, and is exactly 7 lines (including blank line and trailing newline). Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If ANY item is ❌, attempt to fix (re-create with correct content) before proceeding. If unfixable, stop and report to CEO — do NOT move plan to Done.
>
> **Full-suite test run.** Per Rule 21, the autouse fixture affects every test, so scope is full-suite. Run `cd bellows && python -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/pytest_full.txt`. Required outcomes: (a) suite completes without infrastructure error, (b) failures count is exactly 5 (the known carry-overs: 4 test_decisions.py worktree-context + 1 test_runner_parser.py timeout), (c) zero NEW regressions. Quote the final summary line ("X passed, Y failed in Zs"). If failures > 5 or includes any test not in the known-carry-over list, the plan does NOT close — surface the regressions and stop.
>
> **Leak-closure verification (load-bearing).** This is the test that validates the conftest's purpose. After the pytest run completes, run `ls bellows/verdicts/pending/ 2>&1 | grep -v "^archived$" | tee knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/verdicts_pending_post_run.txt`. The output MUST be empty (no `verdict-request-*` files). If ANY file is present, the fixture is not working and the plan does NOT close — surface the orphan and stop.
>
> **Specific-test reproduction check.** Confirm the two previously-leaking tests (per diagnostic Deliverable B) no longer leak by running them individually: `cd bellows && python -m pytest tests/test_bellows.py::test_apply_defensive_header_defaults_propagates_to_reparsed_header tests/test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/previously_leaking_tests.txt`. Both tests must pass. After the run, re-check `ls bellows/verdicts/pending/ | grep -v "^archived$"` is still empty.
>
> **Rule 20 Self-Check.** Embed the canonical Rule 20 banner verbatim in the QA report:
>
> ```
> ============================================================
> Rule 20 — QA Self-Check Results
> ============================================================
> ```
>
> Followed by PASSED or FAILED, evidence folder path, and file count. Required evidence files in the folder: `pytest_full.txt`, `verdicts_pending_post_run.txt`, `previously_leaking_tests.txt`, plus a `conftest_content.txt` capturing `cat bellows/tests/conftest.py` to record the exact body shipped.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-26 completion entry summarizing the conftest addition, the 2 leaks closed, and the load-bearing verification result. Commit with descriptive message. Append a feedback entry to `bellows/knowledge/research/agent-prompt-feedback.md` per standard protocol. Then final commit. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **DEPOSITS RULE:** the Deposits block below lists exactly ONE `.md` file (the QA report). PROJECT_STATUS.md update is a side effect, NOT a deposit. The evidence directory is a single deposit per Rule 26.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-bellows-test-isolation-conftest-2026-05-26.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-test-isolation-conftest-2026-05-26/`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
