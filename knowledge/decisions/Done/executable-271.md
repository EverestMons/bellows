# bellows — plan_lint §4 Drafting-Cycle self-check (warn-first)
**Date:** 2026-07-24 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface: edits a gate, `plan_lint`), T-8 (novel: first implementation of the §4 self-check). Run by the Planner pre-deposit.
**Walks:** 2.
- Weak spots:         w1 1 folded (the closing-line "dry vs fold" parse is fuzzy → keep it lenient; warn-first tolerates a false reminder); w2 dry.
- Destruction:        w1 1 folded (the new WARN must not break existing plan_lint tests that assert output on tier-less plans — DEV updates any, preserving intent, in the SAME step); w2 dry.
- Vulnerabilities:    w1 1 folded (3.2 observe-the-effect: tests must RUN the check on real plan text and assert the WARN actually fires, not just that the function imports; 3.4 degenerate: tier-less / block-less / malformed-block plans must WARN, never crash; read plan files as UTF-8); w2 dry.
- Integration-record: w1 dry (DRAFTING_CYCLE.md §4 is the authority [Rule 27]; the check is an additive sibling to plan_lint's existing (a)-(e) checks, using the same non-blocking WARN mechanism as the test-scope / qa_steps warnings).
- ACID:               w1 dry (stateless lint check; no multi-step schedule).
**Conflicts:** none.
**Cold panel (T2):** NOT separately run — bounded, warn-ONLY change (it can never wrongly block a deposit), and the Step-2 QA agent is an independent cold read of the deliverable. ⚠️ Iteration candidate for DRAFTING_CYCLE.md: a warn-only gate edit may warrant T1, not T2 — noted for a future lesson, not acted on here.
**Closing:** walk 2 dry; last event = lens pass; deposited once.

## CEO Context

The Drafting Cycle shipped as a canonical system (`DRAFTING_CYCLE.md` v1.0, PLANNER_TEMPLATE v4.80). This adds its **§4 enforcement half**: a `plan_lint` check that verifies a plan carries the Cycle-Log structure §3 defines. Per DRAFTING_CYCLE.md §6 ("coordinate doctrine and gate"), the gate pairs with the doctrine.

**⭐ WARN-FIRST is the whole design point (CEO: "no hard rules immediately").** Every check below emits a **WARNING**, never a FAIL — `plan_lint` still exits 0 and the plan still deposits. Use the SAME non-blocking mechanism as the existing test-scope / qa_steps warnings. It flips to blocking later, once the format proves out — that flip is a ONE-LINE change (WARN → FAIL) and is explicitly NOT in this plan.

**The spec is DRAFTING_CYCLE.md §3 and §4 — read them, do not re-derive (Rule 27).** Read `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md` §3 (the Cycle Log format + the `**cycle_tier:**` header) and §4 (exactly what the self-check verifies). The check, per §4:
- the plan header declares `**cycle_tier:** T0`/`T1`/`T2` — else WARN;
- for **T1/T2**: a `## Drafting Cycle` block is present with one result line per required lens (Weak spots, Destruction, Vulnerabilities, Integration-vs-record, ACID — all five) — else WARN naming the missing lens(es);
- for **T2**: a cold-panel line is present — else WARN;
- the closing line asserts a **dry lens pass** as the last event (not a fold) — else WARN;
- **T0**: only the tier declaration is required (no block).

**Scope discipline:** edits `scripts/plan_lint.py` + `tests/` (its test file) ONLY. No other bellows module, no daemon behavior change (plan_lint is invoked by the Planner at authoring, not by the daemon at dispatch — this changes authoring-time linting only). **Deposit-once.**

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py` (the current lint + its WARN mechanism + how checks (a)-(e) are structured) and `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md` §3 + §4 (the authoritative spec — absolute path, it lives at the GitHub root, outside this worktree).
>
> You are the Bellows Developer. Add the §4 Drafting-Cycle self-check to `plan_lint.py` as a new check, **warn-first**.
>
> **Task A — implement the check** as a sibling to the existing checks, emitting WARNINGS via the SAME non-blocking mechanism the current test-scope / qa_steps warnings use (so `plan_lint` still exits 0). Behaviour, exactly per DRAFTING_CYCLE.md §4:
> - parse the header line for `**cycle_tier:** T{0,1,2}`; absent → `WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)`.
> - if T1 or T2: require a `## Drafting Cycle` block; scan it for a result line naming each of the five lenses (match the lens keyword case-insensitively: "weak spots", "destruction", "vulnerabilit", "integration", "acid"); WARN naming any missing lens; absent block → WARN.
> - if T2: require a line matching "cold panel"/"cold-panel"; absent → WARN.
> - require a closing line indicating a dry lens pass as the last event; if the closing indicates a fold as the last event (or no closing line) → WARN. Keep this lenient (warn-first tolerates a false reminder; do NOT over-parse).
> - T0: only the tier declaration is checked (no block).
> - Read the plan file as UTF-8. Never crash on a missing/empty/malformed block — degrade to a WARN.
>
> **Task B — protect existing behaviour (destruction lens).** Grep `tests/` for existing `plan_lint` tests. Run them; if any asserts output on a plan that now emits the new cycle_tier WARN (e.g. a fixture plan with no `cycle_tier`), update that assertion to expect the WARN, **preserving its original intent** — and report each such edit explicitly. If none break, say so. Do NOT weaken the new check to avoid a test edit.
>
> **Task C — tests that OBSERVE the effect (vulnerabilities lens).** Add tests that RUN the check on real plan text and assert the WARN fires / does not fire:
> - a compliant T2 plan → NO cycle-cycle WARN. Use the real block in `/Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/executable-270.md` (a genuine T2 Cycle Log) as a fixture input.
> - a tier-less plan → cycle_tier WARN. Use a real one, e.g. `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions/Done/executable-265.md`.
> - a T1 plan missing the ACID line → WARN naming ACID (synthetic fixture).
> - a T0 plan with just the tier declaration → NO block WARN.
> - a plan whose closing line is a fold → WARN (synthetic fixture).
> - confirm `plan_lint` still **exits 0** on every one of these (warn-first).
>
> **Run targeted tests only:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat` (match the bellows test-running convention). Then run the check live against the two real plans above and paste the raw output (showing the WARN on the tier-less one, clean on 270's block).
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py` (or the existing plan_lint test file — name it as it exists)
> - `knowledge/development/plan-lint-drafting-gate-dev-2026-07-24.md`
>
> **Deposit:** `knowledge/development/plan-lint-drafting-gate-dev-2026-07-24.md` — the new check code, the WARN-mechanism confirmation (exit 0 on all cases), any existing-test edits with intent preserved, the new tests, and the raw targeted-test + live-run output. Canonical Python file-write / MCP write — NO heredoc. Commit all (NO push). Standard prompt feedback → `### Ledger Updates` → `#### Prompt Feedback`.
>
> **Deposits:**
> - `knowledge/development/plan-lint-drafting-gate-dev-2026-07-24.md`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step-1 dev-log + confirm its Output Receipt is Complete; else halt and report.** Post a short visible chat message confirming you are starting Step 2 (QA). You are Bellows QA. Verification + reporting only — no code edits. If a check fails, report it; do NOT fix it. Do NOT use Monitor.
>
> **MANDATORY — Rule 20 self-check.** The QA report MUST contain the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line (em-dash U+2014 byte-exact); end with a self-grep confirming the banner.
>
> **Evidence rule:** deposit RAW command output (≥ last 200 lines incl. the pytest summary line), never a summary.
>
> **Scope:**
> - `knowledge/qa/plan-lint-drafting-gate-qa-2026-07-24.md`
> - evidence under `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/`
>
> Verification table, one row per claim (HALT on any fail):
> 1. **Warn-first proven** — run `plan_lint` on a tier-less plan and on a T1 plan missing a lens; each prints the WARN AND exits 0 (paste both the WARN and `echo $?`). The check can never block a deposit.
> 2. **Compliant plan is clean** — `plan_lint` on `Done/executable-270.md` (real T2 block) emits NO drafting-cycle WARN.
> 3. **Each §4 rule fires** — independently reproduce: no-cycle_tier → WARN; T1 missing ACID → WARN naming ACID; T2 missing cold-panel → WARN; fold-closing → WARN; T0 tier-only → no block WARN.
> 4. **No crash on degenerate input** — an empty/malformed `## Drafting Cycle` block WARNs, does not raise.
> 5. **Existing behaviour intact** — every prior `plan_lint` test passes; confirm the ONLY test edits were assertions updated for the new WARN (Step 1 Task B), intent preserved.
> 6. **Scope** — `git --no-pager diff --stat` limited to `scripts/plan_lint.py` + the test file; no other bellows module touched.
> 7. **Full suite** — `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`, foreground; RAW tail incl. summary. Baseline: the prior bellows suite pass count; any new failure beyond the new tests is a regression.
>
> **Deposit:** `knowledge/qa/plan-lint-drafting-gate-qa-2026-07-24.md` — the table, RAW evidence, the Rule 20 banner + PASSED line, Output Receipt. Canonical Python file-write / MCP write — NO heredoc. Commit the QA report + evidence (NO push). In `### Ledger Updates` include `#### Project Status` (one milestone: DRAFTING_CYCLE.md §4 self-check live in plan_lint, warn-first — plans are now reminded to declare cycle_tier + carry the Cycle Log; blocking deferred) and `#### Prompt Feedback`.
>
> **Deposits:**
> - `knowledge/qa/plan-lint-drafting-gate-qa-2026-07-24.md`
>
> **Do NOT move this plan to `Done/`.** The close path is owned by Bellows on continue-verdict consumption (Rule 8) — never by the agent.
