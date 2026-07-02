# Bellows — Pre-Deposit Plan Lint + rule_20 Receipt Fallback (FORWARD row 9)
**Date:** 2026-07-02 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

CEO-approved 2026-07-02, both halves. Trigger: plan 116 step 2 fired a `rule_20_self_check` gate_failure ("deposits block declares no .md paths") on a substantively perfect QA deposit — the plan had declared its deposit as inline `**Deposit:**` prose, invisible to `_extract_plan_required_deposits` (gates.py:437). This is the FOURTH occurrence of the strict-convention-string authoring family (bellows FORWARD row 9; three prior in session 12: header shape, QA banner, Deposits block), and row 9's recorded disposition is "if it recurs, build the script." Producer fix: the row-9 pre-deposit lint script. Consumer fix: `_gate_rule_20_self_check` (gates.py:494) falls back to agent-receipt-declared deposits — the same source `_gate_deposit_exists` (gates.py:371) already parses into its `agent_declared` set, which is how the daemon knew the correct deposit path on plan 116 even while rule_20 failed. NOTE for CEO: the gates.py change requires a daemon restart to load.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent executes Step 1 ONLY, then STOPS for verdict before Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-plan-lint-and-rule20-receipt-fallback-2026-07-02.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Deliverable 1 — `scripts/plan_lint.py` (pre-deposit lint, FORWARD row 9 spec).** Standalone script, `python3 scripts/plan_lint.py <plan-path>`, reusing existing parsers via `import gates` (add the repo root to sys.path the same way the existing scripts in `scripts/` do — read one first and match its idiom). Checks, each reported as its own PASS/FAIL line:
> (a) **Header parses:** `gates._parse_plan_header` returns a non-empty dict; `dispatch_mode` (or `Dispatch Mode`) normalizes to `bellows` or `manual_bootstrap`; if `pause_for_verdict` is present it must be a recognized token (inspect the daemon's accepted values in `bellows.py` `header_says_pause` and mirror them — do not invent the list).
> (b) **Deposits blocks:** for every `## STEP` section whose text mentions a deposit (case-insensitive `deposit`), `gates._extract_plan_required_deposits(step_text)` must return at least one path. Reuse the daemon's own step-splitting logic if importable (look for the step-extraction helper in `bellows.py`/`gates.py` — the one behind `_extract_step_text`); if not cleanly importable, split on `^## STEP` headers.
> (c) **QA banner pair:** if the header carries `qa_steps` or any step title contains `QA`, the plan text must contain BOTH byte-exact strings `Rule 20 — QA Self-Check Results` and `PASSED — SELF-CHECK PASSED`.
> Exit 0 if all checks pass, exit 1 otherwise. No third-party dependencies.
>
> **Deliverable 2 — receipt fallback in `_gate_rule_20_self_check` (gates.py:494).** Current behavior at gates.py:503-506: `deposit_paths = _extract_plan_required_deposits(step_text)`; if empty → immediate failure "deposits block declares no .md paths". New behavior: when `deposit_paths` is empty, fall back to the agent-receipt-declared deposit paths — extract them from `parsed` using the SAME source/logic `_gate_deposit_exists` (gates.py:371-389) uses to build `agent_declared`, filtered to `.md` paths (refactor that extraction into a small shared helper rather than duplicating it — both gates then call the helper). Only if BOTH sources yield no `.md` paths does the gate emit a failure, with updated evidence text noting both sources were empty (e.g. "no QA deposit paths found in plan **Deposits:** block or agent receipt"). Downstream banner/PASSED-line checks (gates.py:518-542) operate on the fallback paths unchanged. Do NOT weaken the banner checks themselves.
>
> **Deliverable 3 — tests.** Add to the existing test layout (find where gates tests live — `tests/` — and match conventions):
> Lint: (i) a well-formed fixture plan passes all checks exit 0; (ii) missing `**Deposits:**` block in a deposit-mentioning step → exit 1 naming check (b); (iii) QA plan missing the banner pair → exit 1 naming check (c); (iv) unrecognized `dispatch_mode` → exit 1 naming check (a).
> Gate fallback: (v) plan step WITHOUT a Deposits block + receipt declaring a `.md` QA report containing the banner pair → rule_20 PASSES (the plan-116 false-positive class, now green); (vi) neither plan block nor receipt declares any `.md` → rule_20 FAILS with the new both-sources evidence; (vii) existing rule_20 behavior with a proper Deposits block is unchanged (regression).
>
> **Self-verify.** Run the FULL suite with `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and READ THE TAIL — never infer green from a subset. Also run `python3 scripts/plan_lint.py` against this very plan file (it must exit 0 — this plan was authored with proper Deposits blocks) and capture the output.
>
> **Commit** with a descriptive message. Deposit a dev log with: file list, the shared-helper refactor shape, all test names, the full-suite tail verbatim, the self-lint output of this plan, and an Output Receipt with status. In `### Ledger Updates` include `#### Prompt Feedback`.
>
> **Deposits:**
> - `bellows/knowledge/development/plan-lint-and-rule20-receipt-fallback-2026-07-02.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for verdict before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step 1 dev-log deposit at `bellows/knowledge/development/plan-lint-and-rule20-receipt-fallback-2026-07-02.md` and check its Output Receipt status. If status is not Complete, halt and report the blocker before proceeding.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; the verification table below does NOT by itself satisfy the gate — end with a self-grep confirming the banner is present in your deposited report.
>
> Verify both deliverables. Verification table, one row per claim: (1) `scripts/plan_lint.py` exists, takes a path arg, exits 0 on a known-good plan (run it on this plan file — capture output); (2) it exits 1 on each of the three failure fixtures (run tests (ii)-(iv) in isolation, or invoke the script on the fixtures directly); (3) the `pause_for_verdict` token list in the lint mirrors `header_says_pause` in bellows.py — quote both; (4) `_gate_rule_20_self_check` falls back to receipt-declared `.md` deposits when the plan block is empty — quote the new code path and run test (v) in isolation; (5) the both-sources-empty failure preserves gate strictness — run test (vi); (6) regression: proper-Deposits-block behavior unchanged — run test (vii); (7) the shared helper is used by BOTH `_gate_deposit_exists` and `_gate_rule_20_self_check` (no duplicated extraction logic) — quote both call sites; (8) full suite green: re-run `timeout 600 python3 -m pytest tests/ -v` to explicit pass/fail and show the tail. If any row fails, report it and halt — do not pass a broken deliverable.
>
> Deposit the QA report. Commit it. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph: FORWARD row 9 lint script shipped + rule_20 receipt fallback closes the plan-116 false-positive class, daemon restart required to load gates.py; `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/plan-lint-and-rule20-receipt-fallback-qa-2026-07-02.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
