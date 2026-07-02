# Bellows — Declared `**Scope:**` Block for scope_check (norm-shaped changes are not failures)
**Date:** 2026-07-02 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

CEO-ratified 2026-07-02: `scope_check`'s two-value vocabulary (silent pass / gate_failure) mislabels expected-shape work as failure. Evidence: plan 118 step 1 fired gate_failure on `tests/test_gates.py` + `tests/test_plan_lint.py` — tests the plan itself ordered but did not name inline; CEO override required for routine work. Chosen design: plans gain a machine-parsed `**Scope:**` block (sibling convention to `**Deposits:**`) listing exact files and directory prefixes (bullets ending in `/` are prefixes). Files matching declared scope PASS silently; undeclared-and-unmentioned files still FAIL exactly as today — the gate stays fully strict against anything not declared, no heuristics. Plans without a Scope block behave byte-for-byte as today (backward compatible). NOTE for CEO: gates.py changes again — one daemon restart after this lands covers both plan 118's fallback and this. Governance codification of the authoring convention (PLANNER_TEMPLATE checklist entry) is a deliberate follow-up once the mechanism is proven live.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent executes Step 1 ONLY, then STOPS for verdict before Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-scope-block-declared-scope-2026-07-02.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for confirmation. Do NOT proceed to Step 2 or move the plan to Done.
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
> - `gates.py`
> - `scripts/plan_lint.py`
> - `tests/test_gates.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/scope-block-declared-scope-2026-07-02.md`
>
> *(The block above is both this plan's declared scope and a live example of the convention this plan implements.)*
>
> **Deliverable 1 — `_extract_plan_scope(step_text)` in `gates.py`.** New parser, modeled directly on `_extract_plan_required_deposits` (gates.py:437) — read that function first and match its parsing idiom exactly (bold-colon block header `**Scope:**`, multi-line backtick-or-plain bullets). Returns `(files, prefixes)` where bullets ending in `/` are prefixes and all others are exact relative paths. Tolerates absence (returns empty).
>
> **Deliverable 2 — consume it in `_gate_scope_check` (gates.py:712).** After building `union_text` from steps 1..N (existing code at :716-724), also build the union of declared scope across those same steps via `_extract_plan_scope`. In the per-file loop (:730-737), a changed file passes if it (in priority order): matches the existing `SCOPE_ALLOWLIST`/`SCOPE_ALLOWLIST_PREFIXES` checks (unchanged), OR equals a declared scope file / starts with a declared prefix (NEW), OR appears in `union_text` by path or basename (existing, unchanged). Only files clearing none of these fail, with evidence text extended to mention the plan declared no matching scope (e.g. append `; not in declared **Scope:** block` to the existing evidence). Do NOT weaken any existing pass path or the failure itself.
>
> **Deliverable 3 — lint awareness in `scripts/plan_lint.py`.** Add check (d): if a `**Scope:**` block is present in any step, it must parse to at least one file or prefix via `_extract_plan_scope` (a present-but-empty block is a FAIL — dead convention text). Add a WARN-level line (does not affect exit code): if any step's prose mentions `test` (word-boundary, case-insensitive) but neither the declared scope nor the step text names any `test_*.py` path or `tests/` prefix, print `WARN: step N mentions tests but declares no test scope`.
>
> **Deliverable 4 — tests.** In `tests/test_gates.py`: (i) file under a declared prefix (`- tests/`) passes scope_check with no failure; (ii) exact declared file passes; (iii) undeclared+unmentioned file still fails, and its evidence contains the extended `Scope` mention; (iv) plan with NO Scope block reproduces today's behavior byte-for-byte on both a passing and failing fixture (backward compat); (v) declared scope unions across steps (a file declared in step 1's block passes on step 2's check). In `tests/test_plan_lint.py`: (vi) present-but-empty Scope block → exit 1 naming check (d); (vii) the tests-mentioned-no-test-scope WARN fires on a fixture and does NOT change the exit code.
>
> **Self-verify.** Run the FULL suite with `timeout 600 python3 -m pytest tests/ -v` to an explicit pass/fail and READ THE TAIL — never infer green from a subset. Run `python3 scripts/plan_lint.py` on THIS plan file — must exit 0, and must NOT emit the check-(d) failure (this plan's Scope block is non-empty).
>
> **Commit** with a descriptive message. Deposit a dev log to `knowledge/development/scope-block-declared-scope-2026-07-02.md` with: the parser code verbatim, the gate diff hunk, all seven test names, the full-suite tail verbatim, the self-lint output, commit hash, and an Output Receipt with status. In `### Ledger Updates` include `#### Prompt Feedback`.
>
> **Deposits:**
> - `bellows/knowledge/development/scope-block-declared-scope-2026-07-02.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for verdict before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step 1 dev-log deposit at `bellows/knowledge/development/scope-block-declared-scope-2026-07-02.md` and check its Output Receipt status. If status is not Complete, halt and report the blocker before proceeding.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Scope:**
> - `knowledge/qa/scope-block-declared-scope-qa-2026-07-02.md`
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; the verification table below does NOT by itself satisfy the gate — end with a self-grep confirming the banner is present in your deposited report.
>
> Verify the mechanism. Verification table, one row per claim: (1) `_extract_plan_scope` exists in `gates.py` and mirrors the `_extract_plan_required_deposits` idiom — quote both signatures; (2) prefix pass works — run test (i) in isolation; (3) exact-file pass works — test (ii); (4) undeclared file still fails with the extended evidence — test (iii), quote the evidence string; (5) backward compat proven — test (iv); (6) cross-step scope union — test (v); (7) lint check (d) and the WARN behave per spec — tests (vi)+(vii); (8) full suite green — re-run `timeout 600 python3 -m pytest tests/ -v` to explicit pass/fail and show the tail; (9) self-lint of this plan file exits 0. If any row fails, report it and halt — do not pass a broken deliverable.
>
> Deposit the QA report to `knowledge/qa/scope-block-declared-scope-qa-2026-07-02.md` and commit it. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph: declared `**Scope:**` block shipped (CEO 2026-07-02 design: norm-shaped changes are authorable scope, not failures); scope_check strictness against undeclared files preserved; daemon restart required to load gates.py (covers plan 118's fallback too); PLANNER_TEMPLATE codification is the follow-up. `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/scope-block-declared-scope-qa-2026-07-02.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
