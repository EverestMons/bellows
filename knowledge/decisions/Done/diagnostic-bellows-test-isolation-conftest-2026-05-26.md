# Bellows Test-Isolation Conftest — Leaking-Test Audit & Fixture-Shape Diagnostic
**Date:** 2026-05-26 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** after_step_1 | **auto_close:** false

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

## CEO Context

Session 7 reproduced the same orphan pattern four times during a single plan: pytest runs in `bellows/tests/` invoke code paths that call `verdict.post_verdict_request()`, which resolves its output path through the module-level `VERDICTS_DIR` constant (`verdict.py:14`, `BELLOWS_ROOT / "verdicts"`) and writes real `verdict-request-*` files to production `bellows/verdicts/pending/`. Bellows's `tests/` has no `conftest.py`. The orphans WARN-flood every 30s until Planner archives them manually. The 2026-05-26 BACKLOG entry recommends Option (a) — `tests/conftest.py` with a session-scoped autouse fixture monkeypatching `verdict.post_verdict_request` to a no-op or tmpdir-aware variant.

CEO has locked two decisions for this work: (1) diagnostic first, then executable; (2) if a production-side change is required to enable Option (a), the acceptable shape is a module-level constant in `verdict.py` (e.g., `VERDICTS_DIR`, which already exists). The diagnostic's job is to confirm the patch surface and identify every leaking test before authoring the conftest.

Key pre-flight observation: `VERDICTS_DIR` already exists at `verdict.py:14` and is referenced from `post_verdict_request` (line 180), `resolve_verdict` (line 283), and the ledger init path (line 318). All three reads access the module attribute at call time (not closed over), so `monkeypatch.setattr("verdict.VERDICTS_DIR", tmp_path)` should propagate to all three. The diagnostic must confirm this and surface any closed-over copies or import-time captures that would defeat the patch.

Three test files reference `post_verdict_request` (`test_verdict.py`, `test_bellows.py`, `test_rule_26_deposit_parser.py`); the orphan filenames suggest a second leak vector beyond direct calls (e.g., `regression-slug-collision-2026-05-01` looks like an `in-progress-*` plan deposited in a tmpdir that PlanHandler then dispatches against, producing real verdict requests via the dispatch path rather than direct calls). The audit must enumerate both vectors.

This is a single SA step. No DEV, no QA. Findings feed directly into the Planner's next-session executable: exact fixture shape, complete list of leaking tests, and any verdict.py surface changes required (none expected if `VERDICTS_DIR` patches cleanly).

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-bellows-test-isolation-conftest-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-bellows-test-isolation-conftest-2026-05-26.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary read — this is a code+test audit against specific call sites and pytest behavior, no domain interpretation required.
>
> **Task.** Produce a complete leaking-test audit and a fixture-shape blueprint for a session-scoped autouse `tests/conftest.py` that prevents test-spawned verdict-request files from landing in production `bellows/verdicts/pending/`. The CEO has locked Option (a) (conftest autouse) from the 2026-05-26 BACKLOG entry as the chosen fix shape, with the constraint that any production-side change must be a module-level constant in `verdict.py` (and `VERDICTS_DIR` at `verdict.py:14` already exists). Verify the constant suffices, or surface what else is needed.
>
> **Inputs to read.**
> - `bellows/verdict.py` lines 1–60 (imports, module-level constants, `BELLOWS_ROOT`, `VERDICTS_DIR`).
> - `bellows/verdict.py` lines 178–270 (`post_verdict_request` full body).
> - `bellows/verdict.py` lines 280–330 (`resolve_verdict` body + ledger init).
> - `bellows/tests/test_verdict.py` — all tests calling `post_verdict_request` directly.
> - `bellows/tests/test_bellows.py` — all tests calling `post_verdict_request` directly OR creating tmpdir plans that PlanHandler dispatches against.
> - `bellows/tests/test_rule_26_deposit_parser.py` — all tests calling `post_verdict_request`.
> - `bellows/bellows.py` lines 430–660 (the four production call sites for `post_verdict_request` at 444, 531, 624, 655) — to understand what `project_path` semantics tests pass and how that interacts with `VERDICTS_DIR` (the orphan analysis showed `project_path` does NOT control output dir; `VERDICTS_DIR` does).
> - `bellows/verdicts/pending/archived/` directory listing — confirm orphan filenames present (`orphan-test-spawned-*`, `orphan-test-spawned-qa-rerun-*`) and parse their content's `**Plan:**` field to identify originating test paths.
> - `bellows/knowledge/BACKLOG.md` Open section, the "Test-isolation orphan pattern" entry (verify still Open, not closed in any way since session 7).
>
> **Audit deliverable A — Patch-surface confirmation for `VERDICTS_DIR`.** Walk the three call sites that read `VERDICTS_DIR`: `post_verdict_request` (line 180, `pending_dir = VERDICTS_DIR / "pending"`), `resolve_verdict` (line 283, `resolved_dir = VERDICTS_DIR / "resolved"`), and the ledger init (line 317-318). For each, quote the line and report: does the code read `VERDICTS_DIR` from the module's namespace at call time (so `monkeypatch.setattr("verdict.VERDICTS_DIR", tmp_path)` works), or is the value closed over at import time (so the patch would miss)? Also search `bellows/bellows.py` and any other source file for `from verdict import VERDICTS_DIR` or equivalent — if any caller imports the constant directly (`from verdict import VERDICTS_DIR`), that caller's reference is bound at import time and a `setattr` patch on `verdict.VERDICTS_DIR` will NOT propagate. Report any such direct imports verbatim. If none exist, the patch surface is clean.
>
> **Audit deliverable B — Leaking-test enumeration.** Produce a table of every test that currently writes to production `bellows/verdicts/pending/`, with these columns:
>
> ```
> | Test File | Test Function | Line | Leak Vector | Evidence (1-line code excerpt or call path) |
> ```
>
> - **Leak Vector** is one of: `direct-call` (test invokes `post_verdict_request` directly, e.g., `verdict.post_verdict_request(...)`), `dispatch-spawn` (test creates a plan file in a tmpdir then triggers a Bellows dispatch path that eventually calls `post_verdict_request` against the real `VERDICTS_DIR`), `gates-spawn` (test triggers a gate failure path that flows through to verdict posting), or `other` (describe).
>
> For each direct-call test, confirm the test actually causes a file write (it doesn't pre-monkeypatch the function or operate against a different output). For each dispatch-spawn test, trace through the code path that produces the verdict-request file and report which `bellows.py` line is the actual call site. Use grep on the leaked orphan filenames (`item4-test`, `regression-slug-collision-2026-05-01`) against the test files' contents to identify which test produced each orphan. Report findings.
>
> Expected size: at least 2 leaking tests confirmed by orphan filenames; likely more if a thorough audit catches latent leakers. Report the count and the per-test detail.
>
> **Audit deliverable C — Fixture-shape blueprint.** Given the patch-surface findings from (A) and the leaking-test enumeration from (B), design the exact conftest fixture. Required elements:
>
> - **Fixture scope and autouse**: session-scoped vs. function-scoped (justify the choice based on test isolation requirements — session-scoped is faster but doesn't reset between tests; function-scoped is slower but cleaner). Autouse yes/no (and where it should be opted-out, e.g., in `test_verdict.py` if any test legitimately needs the real `VERDICTS_DIR`).
> - **Patch target**: exact `monkeypatch.setattr` call or equivalent. If `VERDICTS_DIR` reads are all module-namespace (per audit A), specify `monkeypatch.setattr("verdict.VERDICTS_DIR", tmp_path_factory.mktemp("verdicts"))`. If any direct imports exist (per audit A), enumerate every additional patch target.
> - **Cleanup**: tmpdir teardown handled by pytest's fixture lifecycle automatically — confirm no extra cleanup logic is required, OR identify any test that creates state outside tmpdir that needs explicit cleanup.
> - **Opt-out mechanism**: for tests in `test_verdict.py` that legitimately exercise the real `VERDICTS_DIR` write behavior (the function-under-test for that file), how does a test opt out? Standard pytest pattern is a marker (`@pytest.mark.no_verdict_isolation`) checked in the fixture body, or a separate fixture override at the function scope. Recommend which.
> - **Total LOC estimate**: count the lines the conftest will contain (the BACKLOG entry estimates ~10-15; verify based on actual fixture shape required).
>
> **Audit deliverable D — Production-side surface check.** Given Option (a) (conftest only, no production change), and given `VERDICTS_DIR` already exists, confirm whether ANY production code change is required. Two outcomes possible: (1) no production change — `VERDICTS_DIR` patches cleanly and the conftest is the only artifact; (2) production change required — describe exactly what and why. The CEO-locked constraint is "module-level constant in `verdict.py`"; if any production change beyond that scope is required, surface it as a Flag for CEO with a one-paragraph rationale.
>
> **Q5 — Verification block (Rule 39).** For each line cited (in A, B, C, D), report the exact line number found in the current file. The executable's fixture body will reference these line numbers; they must be verified, not pattern-matched from memory.
>
> **Q6 — Cross-vector dependency check.** If the dispatch-spawn leak vector exists (per B), confirm whether the `VERDICTS_DIR` patch reaches it. A dispatch-spawn test creates a plan in tmpdir, triggers `PlanHandler._handle()` against that plan, which runs through `bellows.py` lines 430–660. The call site for `post_verdict_request` at (say) bellows.py:531 imports `verdict` as a module and calls `verdict.post_verdict_request(...)`. That function reads `VERDICTS_DIR` from `verdict`'s namespace. So the patch should reach. But verify: is there any path where `bellows.py` shells out, subprocesses, or otherwise invokes Python code in a fresh interpreter (where the conftest patch wouldn't apply)? If yes, that vector defeats Option (a) and the diagnostic must flag it. Answer in one paragraph.
>
> **Output format — single deposit file containing four audit deliverables (A, B, C, D), Q5 verification block, Q6 cross-vector check, and a Flags-for-CEO section.** The Flags section must recommend exactly one of: (a) executable plan ready — conftest fixture as specified, no production change, complete leaking-test list; (b) executable plan blocked — production change required beyond the locked scope, describe; (c) Option (a) defeated by a leak vector that conftest cannot reach (e.g., subprocess execution), recommend Option (b) or (c) from the BACKLOG entry instead. The Planner reads this single deposit at session-start and authors the executable directly from it.
>
> **Constraints.** Do NOT modify source code. Do NOT modify verdict.py, bellows.py, tests/, BACKLOG.md, or create `tests/conftest.py`. This is a read-only investigation. Cite line numbers and quote evidence verbatim. The diagnostic's load-bearing job is to ground the executable's fixture shape and leaking-test list in verified code state, not on baton/BACKLOG-paraphrased claims.
>
> **Deposits:**
> - `bellows/knowledge/research/bellows-test-isolation-conftest-fixture-shape-2026-05-26.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
