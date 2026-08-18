# Auto-continue-unless-errors: QA-result gate + `on_failure` mode (mechanism, canary opt-in) — Executable (DRAFT, walk-0)

**Type:** Executable
**Project:** bellows
**Predecessor / clone-diff target (walk 1):** the design doc `knowledge/research/bellows-autocontinue-design-2026-08-18.md` (diag-437) — implement it verbatim except where CEO forks A/B/C adjust it. Nearest shipped-code analogue for the gate shape: the existing `_gate_rule_20_self_check` (`gates.py:549`) — clone its deposit-path resolution (`_extract_plan_required_deposits` + `_resolve_deposit_path`) for the QA-result gate.
**Depends on:** diag-437 (Done) — the resolved design.
**Created:** 2026-08-18
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**qa_steps:** 4
**cycle_tier:** T2 — HIGHEST blast radius in the shop (edits the daemon's pause-decision path + adds a gate that decides auto-ship). Cold seat MANDATORY on: the QA-result gate parse (all pytest summary formats + fail-closed), the three-legged coupling invariant (F8), and three-site completeness. Money-path-equivalent.
**Deposit target:** `knowledge/decisions/executable-bellows-autocontinue-2026-08-18.md` (bellows project; id minted at claim — predict-not-mint).

---

## CEO decisions (settled 2026-08-18 — fixed constraints)
- **D1 — Bellows-native**, daemon is the watcher. **D2 — `on_failure` becomes the default** — BUT via **Fork C canary**: this plan ships the mechanism as an OPT-IN and does NOT flip the sparse-header default; the default-flip is a separate post-canary follow-up. **D3 — clean final QA auto-closes** (`on_failure` implies `effective_auto_close`), `notify_plan_complete` still fires.
- **Fork A — baseline = `known_failures: N` header field** (integer; default 0). Node-id file deferred to a follow-up.
- **Fork B — fail-closed:** a QA step under `on_failure` with no parseable pytest summary PAUSES, never auto-continues.
- **Fork C — canary:** ship mechanism + docs as opt-in; measure on low-stakes plans; the default-flip (sparse-header default + plan_lint check 9 relax + PLANNER_TEMPLATE default) is a FOLLOW-UP plan, NOT this one.

## Safety invariant (F8 — three legs, all in THIS plan)
`on_failure` is safe iff: (1) the QA-result gate makes a regression fail `gate_result["passed"]`; (2) the `is_qa_step` drop is mode-guarded (`on_failure` only); (3) a mis-declared QA step is a `plan_lint` FAIL. All three ship together; none alone.

## STEP 1 — DEV: test-result gate (`_gate_qa_test_result`) + `known_failures` header

`gates.py`: add `_gate_qa_test_result(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path, plan_header)`:
- **plan_header sourcing (F-Cold1):** `check()` (`gates.py:186`) does NOT take `plan_header` and is called without it (`bellows.py:969`); it PARSES the header internally (`gates.py:~203`). Wire the gate by passing `check()`'s already-parsed `header` local into `_gate_qa_test_result` — do NOT re-parse, do NOT add a param to `check()`'s external callers.
- No-op unless `is_qa_step`.
- Resolve the EVIDENCE file (F-Walk1-A — NOT the report): reuse `_extract_plan_required_deposits(step_text)` + `_resolve_deposit_path(path, project_path, wt_path=wt_path)`, but where `_gate_rule_20_self_check` takes `md_paths[0]` (the `.md` report, `gates.py:573`), THIS gate filters deposit paths for `.txt` and takes the evidence file (prefer one matching the plan's `required_evidence_files` / `*full-suite*`, else the sole `.txt`). If NO `.txt` evidence deposit exists → fail-closed (a QA step under `on_failure` with no evidence cannot be certified).
- Parse the LAST pytest summary line and count BOTH `failed` AND `errors` (F-Cold2 — CRITICAL: pytest emits collection/fixture failures as "`N errors`" SEPARATELY from "`N failed`"; a suite reporting "`0 failed, 5 passed, 3 errors`" must NOT pass). Extract via independent searches on the summary line: `(\d+)\s+failed`, `(\d+)\s+error`, `(\d+)\s+passed` (each optional, default 0). `bad = failed + errors`.
- `known_failures` (F-Cold3): `try: kf = int(plan_header.get("known_failures", 0)) except (ValueError, TypeError): fail-closed` (a malformed value must pause, never crash the daemon). Fail iff `bad > kf`, evidence naming the delta and the failed/error breakdown.
- **Fail-closed (Fork B):** if `is_qa_step` and NO parseable `passed` summary line is found (crash, "no tests ran", unrecognized format) → append a `qa_test_result` failure ("no parseable pytest summary — cannot certify clean; pausing"). The `passed`-line presence is the certification anchor; its absence is never "clean".
- Wire into `gates.check()` (`gates.py:~218`) AFTER `_gate_rule_20_self_check`, passing `plan_header`.
- `plan_lint.py`: accept `known_failures` as an int-typed header field — FAIL (not warn) if present-but-non-int (F-Cold3: the daemon-side try/except fail-closes, but the lint catches it at authoring time).
- **DEV test (targeted):** new `tests/test_gate_qa_test_result.py` — clean summary passes; `failed > known_failures` fails; `failed == known_failures` passes; no-summary-line fails-closed; error-form fails-closed; non-QA step no-ops. Run `python3 -m pytest tests/test_gate_qa_test_result.py -q 2>&1 | cat`.

**Deposits:**
- `gates.py` (new `_gate_qa_test_result` + wire-in)
- `scripts/plan_lint.py` (`known_failures` int field acceptance)
- `tests/test_gate_qa_test_result.py`
- dev note: `knowledge/development/bellows-autocontinue-gate-dev-2026-08-18.md`

## STEP 2 — DEV: `on_failure` pause mode + three-site guard + auto-close + declaration-lint

Per the design doc §Q3/Q4/Q8 (exact diffs there):
- `scripts/plan_lint.py:28` — add `on_failure` to `RECOGNIZED_PAUSE_TOKENS`.
- `bellows.py:627` `header_says_pause` — add `if pv == "on_failure": return False`.
- Guard `is_qa_step` at ALL THREE sites with `and header.get("pause_for_verdict") != "on_failure"`: `:993-996` (non-final), `:1117-1121` (final pause), and relax `:1162-1166` auto-close exclusion to `(not is_qa_step or pause_for_verdict == "on_failure")`.
- `bellows.py:989` — `effective_auto_close = (auto_close=="true") or (pause_for_verdict=="on_failure")`.
- `scripts/plan_lint.py:410-416` — add an `on_failure` branch that FAILS (not warns) when `qa_steps` is missing/unparseable (Q8 — mis-declared QA under `on_failure` auto-ships unchecked).
- **DEV test (targeted):** new `tests/test_on_failure_mode.py` — `header_says_pause` returns False for `on_failure` clean; the three-site guard verified via a unit harness on the pause conditions; `effective_auto_close` true under `on_failure`; plan_lint FAILs `on_failure` without `qa_steps`; existing modes unchanged (Q7 compat). Run `-k "on_failure or pause or header_pause"`.

**Deposits:**
- `bellows.py` (header_says_pause branch, three-site guard, :989 auto-close)
- `scripts/plan_lint.py` (token + qa_steps FAIL branch)
- `tests/test_on_failure_mode.py`
- dev note: `knowledge/development/bellows-autocontinue-mode-dev-2026-08-18.md`

## STEP 3 — DEV: doctrine as OPT-IN (canary — NO default flip)

Fork C: document `on_failure` as an AVAILABLE opt-in mode; do NOT change any default.
- `PLANNER_TEMPLATE.md` — add `on_failure` to BOTH recognized-values enumerations (F-Walk1-B, verified sites): `:890` ("recognized values: `always`, `after_step_1`, `after_qa_step`, `qa_and_terminal`") and `:894` (the identical list in the `bellows` dispatch-mode bullet). Add a semantics paragraph modeled on the `qa_and_terminal` doctrine at `:1038`: auto-continue every clean step incl. QA/terminal; pause+notify only on gate failure; REQUIRES `qa_steps` (lint-FAIL otherwise) + honors `known_failures`; implies `auto_close`. Mark it "opt-in during the canary; not yet the default."
- Add a short canary note: how to run the canary (set `pause_for_verdict: on_failure` on a low-stakes plan) and what to measure (test-result-gate catch rate) before a follow-up flips the default.
- **DO NOT** change `_apply_defensive_header_defaults` (`bellows.py:652`), `plan_lint` check 9 (`:1423`), the `:396` header-template default, or the sparse-header default — all FOLLOW-UP scope. `on_failure` is added as a valid string only; no default moves.
- **DEV test:** doc-only (PLANNER_TEMPLATE) — no Python logic; covered by STEP 4 full suite.

**Deposits:**
- `PLANNER_TEMPLATE.md` (on_failure documented as opt-in + canary note)
- dev note: `knowledge/development/bellows-autocontinue-doctrine-dev-2026-08-18.md`

## STEP 4 — QA: full suite + backward-compat + canary dry-run

Run the full bellows test suite: `python3 -m pytest tests/ -q 2>&1 | cat`. Deposit RAW output. Verify:
- backward compat (Q7): existing `always`/`after_step_1`/`after_qa_step`/`qa_and_terminal` behavior unchanged (assert via the mode tests).
- the QA-result gate parses real pytest summary lines and fails-closed correctly.
- the three-site `is_qa_step` guard fires only under `on_failure`.
- CANARY dry-run: a synthetic `on_failure` two-step plan (DEV+QA) with a clean QA auto-continues to Done in a test harness; the same with an injected regression PAUSES.

**MANDATORY — Rule 20 self-check banner** (`## Rule 20 — QA Self-Check Results` + `**PASSED — SELF-CHECK PASSED**` verbatim, canonical block from `RULE_20_SELF_CHECK_BLOCK.md`). Values: `plan_slug`: `bellows-autocontinue-2026-08-18`; `qa_report_path`: `<abs>/knowledge/qa/bellows-autocontinue-qa-2026-08-18.md`; `evidence_dir`: `<abs>/knowledge/qa/evidence/bellows-autocontinue-2026-08-18/`; `required_evidence_files`: `[full-suite.txt]`. FAILED → halt.

**Deposits:**
- `knowledge/qa/bellows-autocontinue-qa-2026-08-18.md` — QA report
- `knowledge/qa/evidence/bellows-autocontinue-2026-08-18/full-suite.txt` — raw full-suite stdout

---

## Scope / non-goals
Ships the MECHANISM (QA-result gate + `on_failure` mode) as an opt-in, documented for canary use. Does NOT flip any default (Fork C — follow-up plan). Does NOT build the `.bellows-baseline` node-id file (Fork A — follow-up). Does NOT touch existing plans' behavior (Q7).

## Drafting Cycle
**Walk-0 context pin:** Highest-blast-radius change in the shop — edits the daemon pause-decision path. CEO decisions D1/D2/D3 + forks A/B/C settled. The load-bearing correctness is F8's three-legged invariant, all three legs in this plan. Cold seat MANDATORY (T2) on the gate parse + coupling + three-site completeness. The canary framing (Fork C) is the safety net — nothing auto-ships until a plan opts in.
**Open weak spots to walk (NOT yet run):**
- WS: does `_gate_qa_test_result` correctly identify WHICH deposit is the evidence file when a QA step deposits multiple files (report + evidence)?
- V: the coupling invariant — is there any intermediate commit (STEP 2 before STEP 1) where the `is_qa_step` drop exists without the gate? (Order STEP 1 gate BEFORE STEP 2 mode — verify.)
- D: does relaxing the auto-close exclusion (`:1162`) interact with any other `is_qa_step` consumer not in the three sites?
- I: PLANNER_TEMPLATE has multiple `pause_for_verdict` enumerations (F3/F6 cited ~:890/:894/:1423) — STEP 3 must add `on_failure` to ALL of them or the lint/doctrine drift.
- A: the QA-result gate must be idempotent + read-only on the evidence file; no write to the worktree.

**Walk 1 — RUN (all five lenses, verified against HEAD). Yield 3.**
- **Weak spots (F-Walk1-A, folded → STEP 1):** `_gate_rule_20_self_check` takes `md_paths[0]` (the `.md` report, `gates.py:573`); the test-result gate needs the `.txt` EVIDENCE. STEP 1 now filters for `.txt` (prefer `required_evidence_files`/`*full-suite*`) and fail-closes if none — a wrong-file read would have silently certified the report as "tests passed."
- **Integration (F-Walk1-B, folded → STEP 3):** verified TWO recognized-values enumerations (`PLANNER_TEMPLATE:890` and `:894`), not one; STEP 3 must hit both + a semantics para modeled on `:1038`. Pinned the canary no-touch list precisely (`:652`, `:1423`, `:396`, sparse default).
- **Vulnerabilities (coupling ordering, confirmed):** STEP 1 (gate) precedes STEP 2 (is_qa_step drop) → no intermediate HEAD has the drop without the gate (F8 leg 1). The step ORDER is the invariant's enforcement; made explicit below.
- **Destruction:** dry — the `is_qa_step` sweep (diag-437 Walk 2) already proved the three sites + display branches complete; no fourth consumer.
- **ACID:** dry — gate is read-only on the evidence file (no worktree write); additive + mode-guarded (Q7).

**Direction after Walk 1:** PROCEED — cold seat owed. Yield 3, no fold invalidated D1/D2/D3 or forks A/B/C. Carries → cold seat.

**Walk 2 — COLD SEAT SPENT (T2 mandatory; fresh reader adversarial vs HEAD). Yield 3 real + confirmations; all author-verified before folding.**
- **Vulnerabilities (F-Cold2, HIGH → STEP 1) — the seat's keystone:** the gate's regex counted only `failed`, NOT `errors`. pytest emits collection/fixture failures as "`N errors`" separately, so "`0 failed, 5 passed, 3 errors`" would have AUTO-PASSED — a regression-shipping hole that only auto-continue would expose. Now counts `bad = failed + errors`. Author-verified against real pytest output.
- **Weak spots (F-Cold1, HIGH → STEP 1):** `check()` (`gates.py:186`) takes no `plan_header`; the gate must use `check()`'s internally-parsed `header` (`:203`), not a new param on external callers. Under-specification closed.
- **ACID (F-Cold3, MED → STEP 1):** `int(known_failures)` crashes the daemon on a malformed value → try/except fail-closed + a `plan_lint` FAIL.
- **Destruction (F-Cold4, author-verified DISMISSED):** the seat flagged an intermediate-window risk (gate in STEP 1, lint in STEP 2). Verified NON-issue: `on_failure` is INERT until STEP 2 — the token isn't in `RECOGNIZED_PAUSE_TOKENS`, the `is_qa_step` drop, and the qa_steps-FAIL all land together in STEP 2; STEP 1 ships only the (additive, dormant) gate. No state has the drop without the gate+lint.
- **Cold-confirmed CLEAN:** three-site completeness (`:994`/`:1118`/`:1163` exhaustive), `header_says_pause` branch safety, `effective_auto_close` scope reaches single+multi-step, backward-compat (Q7), deposit-path reuse, non-QA no-op.

**Direction after Walk 2 (cold): PROCEED to deposit.** Yield 3 → 3, but the cold findings are validation/robustness hardening — none invalidated D1/D2/D3, forks A/B/C, or the F8 invariant; the seat CONFIRMED the load-bearing core (three sites, coupling, compat). The keystone (F-Cold2 errors-count) is exactly the regression class auto-continue exists to catch — caught before ship.

**Ordering invariant (F-Cold4-strengthened):** `on_failure` is inert until STEP 2 (token + `is_qa_step` drop + qa_steps-FAIL all land in STEP 2); STEP 1 ships the dormant gate first. So the F8 three legs are all present the instant the mode becomes usable — no dangerous intermediate HEAD.

**Closing:** record-only re-read RAN — every fold-anchor (Walk1: A→STEP1, B→STEP3, ordering; Cold: 1/2/3→STEP1, 4→ordering) resolves once against its cited step; forks A/B/C intact; the canary framing (no default flip) consistent across STEP 3 + Scope; QA banner byte-exact; `## STEP`×4 parse; `qa_steps: 4` authoritative (steps 1–3 DEV). Last lens event is a dry cold-confirm. `plan_lint` at the deposit path — exit 0. **§2 bar MET + cold seat spent — deposit once.**
