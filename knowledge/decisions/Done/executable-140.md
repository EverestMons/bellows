# Bellows — plan_lint qa_steps ↔ step-label cross-check (WARN-only) [v2, single dispatch]
**Date:** 2026-07-07 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

Clean single re-dispatch of the plan_lint qa_steps guard. Prior attempts entangled: plan 136 died on a session-limit 429; a manual double-deposit then produced byte-identical plans 137 & 138 (diagnostic 139: `knowledge/research/plan-double-claim-137-138-2026-07-07.md` — dual-deposit root cause), whose two worktrees collided on teardown and both halted. This v2 is the authoritative dispatch — deposited exactly once. Any prior stray impl in main was stashed; start from a clean `scripts/plan_lint.py`.

**What it does.** `qa_steps` is a **step-number list**, not a count (`gates.py:_gate_is_qa_step`, ~line 724): `qa_steps: 1` on a DEV→QA plan silently gated the DEV step as QA (plan-133 trap). plan_lint has no cross-check between the `qa_steps` header and actual step labels — this adds a **WARN-only** advisory (CEO decision A: does NOT block deposit; mirrors the existing "mentions tests but declares no test scope" WARN at `scripts/plan_lint.py` ~line 116-129, which prints without touching `all_passed`).

**Bug to avoid (seen in the halted attempts):** the two-condition WARN must NOT be written as an `if/else` whose branches print an identical string — that dead branch is exactly what QA rejected before. Use ONE print per condition, no redundant arm.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Execute Step 1 ONLY, then STOP for CEO verdict.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-plan-lint-qa-steps-cross-check-v2-2026-07-07.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/plan-lint-qa-steps-cross-check-v2-2026-07-07.md`
>
> **Mechanical-only invariant reminder:** WARN-only advisory. The new block emits `print(...)` lines and must NEVER set `all_passed = False`, change the return code, or raise. A malformed `qa_steps` value skips the check with no exception.
>
> **Change 1 — parse helper.** In `scripts/plan_lint.py`, add a helper that parses the `qa_steps` header value into a set of ints, mirroring `gates._gate_is_qa_step` EXACTLY: accept a YAML list (`[2, 4]`) and a comma-string (`"2,4"`); on `ValueError`/`TypeError` return an empty set. Read the current `gates.py` logic first and match it.
>
> **Change 2 — cross-check block (NO dead branch).** Add a WARN-only block alongside the existing test-scope WARN (~line 116), following that print-only pattern. Using the `step_headers` list already extracted at ~line 57 (`(header_line, step_num_str)` tuples), build (i) the set of QA-labeled step numbers (header contains `qa`, case-insensitive), (ii) the parsed `qa_steps` set, and (iii) the set of step numbers that actually have a `## STEP` header. Then emit exactly two kinds of WARN, one `print` each — **do not write an if/else with identical branches**:
>   - For each `n` in `(qa_labeled_steps − qa_steps_set)`: `print(f"WARN: step {n} is QA-labeled but absent from qa_steps={qa_steps_raw!r} — it will not be Rule 20/22 gated")`.
>   - For each `n` in `(qa_steps_set − qa_labeled_steps)`: a single `print` — `WARN: qa_steps lists step {n} but step {n} is not QA-labeled — it will be gated as QA (plan-133 trap)`. (If `n` has no `## STEP` header at all, the same message applies; do NOT add a redundant second branch for that case.)
>   - If the header has no `qa_steps` field, skip the entire block silently.
>
> **Change 3 — tests.** Add tests to `tests/test_plan_lint.py` following the existing `_run_lint(plan_text)` subprocess+tempfile style. Cover: (a) good DEV→QA plan (`qa_steps: 2`, STEP 2 QA-labeled) emits NO qa_steps WARN, exit 0; (b) plan-133 shape (`qa_steps: 1`, STEP 1 DEV / STEP 2 QA) emits the "gated as QA" WARN and STILL exits 0; (c) QA-labeled step absent from `qa_steps` emits the "will not be gated" WARN, exit 0; (d) list-form `qa_steps: [2]` parses identically (no false WARN); (e) malformed `qa_steps: abc` — no crash, no traceback, exits without error; (f) no `qa_steps` field → no qa_steps WARN. Assert on exact WARN substrings so a regression to the dead-branch form (duplicate output) would be caught. Existing tests must pass UNCHANGED — if any fails, halt and report.
>
> **Self-verify.** Run the FULL suite with `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and READ THE TAIL. Grep the diff to confirm the new block has no `all_passed` assignment, no `return`, and no `if/else` with identical print bodies.
>
> **Commit** (e.g. `feat(plan_lint): WARN when qa_steps disagrees with step labels (plan-133 trap guard)`).
>
> **Deposit:** `bellows/knowledge/development/plan-lint-qa-steps-cross-check-v2-2026-07-07.md` — exact diff hunks for the helper + WARN block, confirmation the helper matches `gates._gate_is_qa_step` (quote both), the no-dead-branch grep result, new test names + one-line rationale each, full-suite tail verbatim, commit hash, Output Receipt with status. Canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/plan-lint-qa-steps-cross-check-v2-2026-07-07.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step 1 dev-log deposit at `bellows/knowledge/development/plan-lint-qa-steps-cross-check-v2-2026-07-07.md` and check its Output Receipt status. If status is not Complete, halt and report the blocker before proceeding.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; end with a self-grep confirming the banner is present in your deposited report.
>
> **Scope:**
> - `knowledge/qa/plan-lint-qa-steps-cross-check-v2-qa-2026-07-07.md`
>
> Verify AT CODE LEVEL. Verification table, one row per claim: (1) parse helper matches `gates._gate_is_qa_step` — quote both, confirm list-form, comma-string, and malformed→skip; (2) WARN block is print-only — cite it, confirm NO `all_passed` assignment, NO `return`, and **NO if/else with identical print bodies** (this was the prior defect — quote the block to prove it); (3) plan-133 shape produces the trap WARN AND exit 0 — test (b) in isolation, quote the assertion; (4) QA-labeled step absent from `qa_steps` → "will not be gated" WARN — test (c); (5) list-form no false WARN — test (d); (6) malformed `qa_steps` no crash — test (e), confirm no traceback; (7) no-`qa_steps` plan → no WARN — test (f); (8) pre-existing tests unchanged — `git diff HEAD~1 -- tests/` shows additions only; (9) full suite green — re-run `timeout 600 python3 -m pytest tests/ -v`, show the tail. Any row fails → report and halt.
>
> **Deposit:** `bellows/knowledge/qa/plan-lint-qa-steps-cross-check-v2-qa-2026-07-07.md` — verification table, full-suite tail, the Rule 20 self-check block, Output Receipt with status. Commit the QA report. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph (plan_lint qa_steps↔step-label cross-check shipped 2026-07-07, WARN-only, guards the plan-133 trap class); `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/plan-lint-qa-steps-cross-check-v2-qa-2026-07-07.md`
>
> **STOP. Do NOT move the plan to Done until the CEO issues a verdict.**
