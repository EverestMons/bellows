# Bellows — plan_lint qa_steps ↔ step-label cross-check (WARN-only)
**Date:** 2026-07-07 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

Closes the plan-133 trap class. `qa_steps` is a **step-number list**, not a count (`gates.py:_gate_is_qa_step`, ~line 724): `qa_steps: 1` on a DEV→QA plan silently gated the DEV step as QA (false-positive Rule 22 FAIL, CEO override) and left the real QA step ungated by Rule 20/22. plan_lint currently has no cross-check between the `qa_steps` header and the actual step labels — grep-confirmed absent. This adds one.

**Scope of the change:** a new **WARN-only** block in `plan_lint.py` (CEO decision A, 2026-07-07: advisory, does NOT block deposit — mirrors the existing "mentions tests but declares no test scope" WARN at ~line 116-129, which prints without touching `all_passed`). Two conditions warn:
1. A step whose `## STEP N` header contains "qa" (case-insensitive) whose number **N is absent** from `qa_steps` — a QA step that won't be gated.
2. A number in `qa_steps` whose corresponding step header **does not** contain "qa" — a non-QA step that will be gated as QA (the exact plan-133 shape: `qa_steps: 1` pointing at STEP 1 DEV).

`qa_steps` parsing MUST mirror `gates._gate_is_qa_step` exactly — handle both the YAML-list form (`[2, 4]`) and the comma-string form (`"2,4"`), and tolerate a malformed value (skip the check, no crash) rather than inventing new parse rules. When the header has no `qa_steps` field at all, skip silently — there is nothing to cross-check.

**Mechanical-only invariant:** this is a lint advisory. It emits `print(...)` lines and never changes the exit code or `all_passed`. A malformed header must never raise out of the linter.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-plan-lint-qa-steps-cross-check-2026-07-07.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
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
> - `knowledge/development/plan-lint-qa-steps-cross-check-2026-07-07.md`
>
> **Mechanical-only invariant reminder:** this is a WARN-only advisory. The new block emits `print(...)` lines and must NEVER set `all_passed = False`, change the return code, or raise. A malformed `qa_steps` value skips the check with no output beyond an optional warn — never an exception.
>
> **Change 1 — parse helper.** In `scripts/plan_lint.py`, add a small helper that parses the `qa_steps` header value into a set of ints, mirroring `gates._gate_is_qa_step` EXACTLY: accept a YAML list (`[2, 4]`) and a comma-string (`"2,4"`); on `ValueError`/`TypeError` return an empty set (treat as "unparseable — skip"). Do NOT invent new syntax. Read the current `gates.py` logic first and match it token-for-token.
>
> **Change 2 — cross-check block.** Add a WARN-only block (place it alongside the existing test-scope WARN at ~line 116, following that print-only pattern). Using the `step_headers` list already extracted at ~line 57 (each entry is `(header_line, step_num_str)`): build the set of QA-labeled step numbers (header contains `qa`, case-insensitive) and the parsed `qa_steps` set. Then:
>   - For each QA-labeled step number NOT in the `qa_steps` set: `print(f"WARN: step {n} looks like a QA step (header: {...}) but is not listed in qa_steps={...} — it will not be Rule 20/22 gated")`.
>   - For each number in the `qa_steps` set whose step header is NOT QA-labeled (or names a step number that has no `## STEP` header at all): `print(f"WARN: qa_steps lists step {n} but that step is not QA-labeled — it will be gated as QA (plan-133 trap)")`.
>   - If the header has no `qa_steps` field, skip the entire block silently.
>
> **Change 3 — tests.** Add tests to `tests/test_plan_lint.py` following the existing `_run_lint(plan_text)` subprocess+tempfile style (assert on `result.stdout` / `result.returncode`). Cover: (a) canonical good DEV→QA plan (`qa_steps: 2`, STEP 2 QA-labeled) emits NO qa_steps WARN and stays exit 0; (b) the plan-133 shape (`qa_steps: 1`, STEP 1 DEV / STEP 2 QA) emits the "gated as QA" WARN and STILL exits 0 (proves warn-only); (c) a QA-labeled step absent from `qa_steps` emits the "will not be gated" WARN, exit 0; (d) list-form `qa_steps: [2]` parses identically to the string form (no false WARN); (e) malformed `qa_steps: abc` emits no crash / no traceback and exits without error; (f) a plan with no `qa_steps` field emits no qa_steps WARN. Existing tests must pass UNCHANGED — if any fails, halt and report; do NOT rewrite assertions.
>
> **Self-verify.** Run the FULL suite with `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and READ THE TAIL — never infer green from a subset or collect count. Confirm the warn-only invariant by grepping the diff: the new block must contain no `all_passed` assignment and no `return`.
>
> **Commit** with a descriptive message (e.g. `feat(plan_lint): WARN when qa_steps disagrees with step labels (plan-133 trap guard)`).
>
> **Deposit:** `bellows/knowledge/development/plan-lint-qa-steps-cross-check-2026-07-07.md` — dev log with: exact diff hunks (or verbatim old/new blocks) for the helper + WARN block, confirmation the parse helper matches `gates._gate_is_qa_step` (quote both), new test names + one-line rationale each, the full-suite tail verbatim, the warn-only grep result, commit hash, and an Output Receipt with status. Use the canonical Python file-write pattern — no heredoc. In `### Ledger Updates` include `#### Prompt Feedback` (daemon-owned; do NOT edit any feedback file directly).
>
> **Deposits:**
> - `bellows/knowledge/development/plan-lint-qa-steps-cross-check-2026-07-07.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step 1 dev-log deposit at `bellows/knowledge/development/plan-lint-qa-steps-cross-check-2026-07-07.md` and check its Output Receipt status. If status is not Complete, halt and report the blocker before proceeding.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; the verification table below does NOT by itself satisfy the gate — end with a self-grep confirming the banner is present in your deposited report.
>
> **Scope:**
> - `knowledge/qa/plan-lint-qa-steps-cross-check-qa-2026-07-07.md`
>
> Verify AT CODE LEVEL. Produce a verification table, one row per claim: (1) the parse helper matches `gates._gate_is_qa_step` — quote both and confirm list-form and comma-string both handled plus the malformed→skip branch; (2) the WARN block is print-only — cite the block and confirm it contains no `all_passed` assignment and no `return`/exit change (quote the surrounding lines); (3) the plan-133 shape (`qa_steps: 1` on a DEV step) produces the trap WARN AND exit 0 — run test (b) in isolation and quote its assertion; (4) a QA-labeled step absent from `qa_steps` produces the "will not be gated" WARN — test (c) in isolation; (5) list-form `qa_steps: [2]` produces no false WARN — test (d); (6) malformed `qa_steps` does not crash the linter — test (e), confirm no traceback in output; (7) no-`qa_steps` plan produces no WARN — test (f); (8) pre-existing tests pass with assertions untouched — verify via `git diff HEAD~1 -- tests/` that no existing assertion lines were modified (additions only); (9) full suite green: re-run `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and show the tail. If any row fails, report it and halt — do not pass a broken deliverable.
>
> **Deposit:** `bellows/knowledge/qa/plan-lint-qa-steps-cross-check-qa-2026-07-07.md` — verification table, full-suite tail, the Rule 20 self-check block, and an Output Receipt with status. Commit the QA report. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph: plan_lint qa_steps↔step-label cross-check shipped 2026-07-07 (WARN-only, guards the plan-133 trap class); `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/plan-lint-qa-steps-cross-check-qa-2026-07-07.md`
>
> **STOP. Do NOT move the plan to Done until the CEO issues a verdict.**
