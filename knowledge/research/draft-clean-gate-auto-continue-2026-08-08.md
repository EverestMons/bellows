# Executable: clean-gate auto-continue — the `qa_and_terminal` pause mode + mechanical-advance provenance

**Type:** Executable
**Project:** bellows
**Depends on:** diagnostic-315 (Done — the distribution refresh this is authored from: finding-rate 3.08% CI [1.7%, 5.6%], mechanizable class 83.3% of pauses, full seam map at Q5), executable-313 (Done — the `gate_auto` recording pattern Site 2 clones)
**Created:** 2026-08-08
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T2
**qa_steps:** [2]

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`) and does not parse the filename. Slug+date name form used; re-read `id_sequence` at deposit, never at authoring.

---

## Why this exists — and exactly what is being traded

Diagnostic-315 measured the trade the CEO has now taken: on clean-gate pauses the Planner's read catches something **3.08%** of the time (10/325 post-07-02, Wilson CI [1.7%, 5.6%]), while the mechanizable class (`header_pause` + `qa_checkpoint`) constitutes **83.3%** of all pauses — 317 clean-gate continues in five weeks, ~1.53 per plan. This plan mechanizes a deliberately narrowed slice of that class:

- **IN: non-terminal, non-QA steps** whose gates are all clean, for plans that **opt in at authoring time** via a new `pause_for_verdict` mode. The pause decision moves from run time (a rote Planner continue) to authoring time (the Planner chooses the mode only for plans whose intermediate gates are rote — the 311-style tranche pattern, 6 continues in one plan).
- **OUT: QA checkpoints** — both qa_checkpoint catches in 315's evidence were substantive QA-report defects (plan 128's evidence-source substitution, plan 230's dropped verification rows). The QA read stays human, always.
- **OUT: terminal steps** — the close decision stays human; `auto_close` is the existing, separate opt-in for that, untouched here.
- **OUT: any gate failure** — the pause cascade checks `gate_result["passed"]` before the header, so a failed gate pauses regardless of mode. 315 Q4's population (12.4% of pauses) is structurally unaffected.

**The provenance half:** today the non-terminal mechanical advance (taken when no pause condition fires) leaves **no `verdicts` row at all** — the last unrecorded transition class from 312's audit. Site 2 records it with the 313-shipped pattern (`pause_reason_code="clean_gate_auto"`, `decided_by="gate_auto"`), so every mechanical continue becomes a queryable row. This applies to ALL mechanical advances, not only the new mode — closing the audit gap is independent of widening the path.

**Notification decision (explicit, CEO-overridable at this plan's gate):** the mechanical advance fires **no notification** — matching the already-existing silent mechanical path it widens (315 Q6 enumerated the three options; a per-advance push would fire on every multi-step plan). The `gate_auto` row is the audit trail; the dashboard's awaiting-verdict surface is unaffected in normal operation because the paired calls set the outcome immediately. (Both lifecycle writes are fail-soft — a swallowed outcome write would strand a NULL row visible in the awaiting surface, the 310 shape; the remedy is the same manual close exercised on 310.)

**Activation boundary:** the running daemon executes pre-change code until restart. This plan's QA proves code + tests only; the **post-activation live canary is a mandatory follow-on** (the 295 precedent — Checklist #32's observed-delta standard), queued via the Forward Register bullet in Step 2's receipt.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `bellows.py` — the `header_says_pause` function (anchor `def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:`) and the non-terminal while-loop's pause cascade + mechanical advance (anchors `while not is_final_step(current_step, total_steps):` and the comment `# All gates passed and not QA — continue to next step`) — plus `lifecycle.py` (`record_verdict_request`, `record_verdict_outcome`) and `tests/test_gate_transaction_mechanization.py`. **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
> **Task A0 — pre-edit cleanliness.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- bellows.py verdicts/README.md tests/test_gate_transaction_mechanization.py tests/test_bellows.py` must be empty. If DIRTY, enumerate the hunks, attribute each to this plan; any unattributable hunk → HALT, do not restore.
>
> **Task B — three sites: two in `bellows.py`, one in `verdicts/README.md` (quoted anchors — read and locate the exact lines before editing):**
> - **Site 1 (`header_says_pause`):** after the existing `if pv == "after_qa_step":` branch and before the unrecognized-value WARN, add the new mode:
>   `if pv == "qa_and_terminal":`
>   `    return is_qa_step or is_final_step(current_step, total_steps)`
>   Call `is_final_step` (same module, anchor `def is_final_step(step: int, total_steps: int) -> bool:`) rather than mirroring its comparison — the loop's terminal predicate and the mode's must be the same function so they cannot drift. AND update the WARN's recognized-list literal (anchor `recognized: 'always', 'after_step_1', 'after_qa_step'`) to include `'qa_and_terminal'`. Both edits or neither — a recognized mode that still WARNs is a defect. **Precedence (state in the branch's one-line comment):** at the terminal step this mode returns True, which makes the auto-close branch (guarded by NOT header_says_pause) unreachable — a plan setting BOTH `auto_close: true` AND this mode gets the terminal pause; the mode wins.
> - **Site 2 (mechanical-advance provenance):** inside the non-terminal while-loop, immediately after the pause conditional's closing `return`-block and BEFORE the line anchored `default_next_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {current_step + 1}.`, add (guarded — mirror the loop's existing `if plan_id ... else None` style):
>   `if plan_id:`
>   `    lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="clean_gate_auto")`
>   `    lifecycle.record_verdict_outcome(plan_id, current_step, "continue", decided_by="gate_auto")`
>   with a one-line comment stating this records the mechanical clean-gate continue so the transition is auditable (315's evidence; clones 313's auto-close pattern). The request+outcome pairing is REQUIRED — `record_verdict_outcome` updates only a `WHERE outcome IS NULL` row (`lifecycle.py`, anchor `"""Update the most recent pending verdict row`), so the outcome call without the request call is a silent no-op.
> - **Site 3 (`verdicts/README.md`):** in the pause-reason table (anchor: the row `| `auto_close_disabled` | Auto-close is disabled for the plan |`), add TWO rows: `auto_close` (mechanical terminal auto-close, recorded since plan 313 — a pre-existing documentation gap backfilled here, disclosed in the dev log) and `clean_gate_auto` (recorded for a mechanical clean-gate non-terminal advance — NOT a pause; the row exists so the transition is auditable). ⚠️ The README's "pauses plan execution under five conditions" sentence stays FIVE — the two new rows are NOT pauses; instead add a half-sentence distinguishing recorded transition codes (`auto_close`, `clean_gate_auto`) from pause reasons, so the table's row count and the pause count cannot read as contradicting. Add one line documenting the `qa_and_terminal` header mode where the README discusses pause behavior.
> - **Touch nothing else.** `_apply_defensive_header_defaults` (sparse headers still default to `after_step_1`), the terminal-step cascade, and the auto-close branch are all out of scope.
>
> **Task C — mode tests.** Add a test class named `TestHeaderSaysPauseModes` to `tests/test_gate_transaction_mechanization.py` exercising the REAL `header_says_pause` — import from `bellows` exactly as `tests/test_bellows.py` already does (proven side-effect-free). Cases: `qa_and_terminal` returns False for a non-terminal non-QA step; True for a QA step; True for the terminal step — asserted unconditionally, which IS the auto-close precedence pin (the function does not read `auto_close`, so terminal-True holds regardless of that header); True for every step when `total_steps` is 0 (unparsed-header degenerate — the safe direction); True at step 1 of a single-step plan (mode misuse on a diagnostic is harmless); the three existing modes return unchanged values on the same inputs; an unrecognized value still returns False.
>
> **Task D — provenance test.** Add a test class named `TestCleanGateAutoProvenance` to `tests/test_gate_transaction_mechanization.py` at the lifecycle layer (per-test DB, the existing conftest isolation): the `clean_gate_auto` request+outcome pair produces a queryable row with `outcome='continue'`, `decided_by='gate_auto'`, `pause_reason_code='clean_gate_auto'` — AND that row does NOT match the dashboard's awaiting filter (`SELECT ... WHERE outcome IS NULL` returns nothing for it). A `run_plan`-level assertion follows 313's Task D standard: include it, or state in a comment exactly why it is deferred (the existing `test_bellows.py` harness coverage) — do not silently omit the decision.
>
> **Task E — run targeted tests ONLY** (never the full suite in DEV): `python3 -m pytest tests/test_gate_transaction_mechanization.py tests/test_bellows.py -k "verdict or decided or auto_close or transaction or header_says_pause or clean_gate" --tb=short -q 2>&1 | cat`. The new classes are selected via the MODULE-name term — `test_gate_transaction_mechanization` contains `transaction`, so every test in that file matches (Planner-verified by collect-only probe; the class names themselves are organization, not the selection mechanism). Paste RAW output UNTRUNCATED; all selected tests pass and `echo $?` = 0.
>
> **Scope:**
> - `bellows.py`
> - `verdicts/README.md`
> - `tests/test_gate_transaction_mechanization.py`
> - `tests/test_bellows.py`
> - `knowledge/development/clean-gate-auto-continue-dev-log-2026-08-08.md`
>
> **Deposit the dev log** with the exact before/after lines for both `bellows.py` sites and the README rows, the auto_close README-backfill disclosure, the auto-close precedence note, the **semantic-shift note** (the `verdicts` table now carries non-pause rows — distribution analyses must key on `pause_reason_code`), the Task D include-or-defer decision, and the RAW targeted-test output. Canonical Python/MCP file-write — NO heredoc. Commit all (NO push). `#### Prompt Feedback` in `### Ledger Updates`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

**Deposits:**
- `bellows/bellows.py`
- `bellows/verdicts/README.md`
- `bellows/tests/test_gate_transaction_mechanization.py`
- `bellows/tests/test_bellows.py`
- `bellows/knowledge/development/clean-gate-auto-continue-dev-log-2026-08-08.md`

---
---

## STEP 2 — QA

> **Task Q0 — re-pin state.** `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- bellows.py verdicts/README.md tests/test_gate_transaction_mechanization.py tests/test_bellows.py` — the most recent commit touching any must be Step 1's. A foreign commit → HALT and report.
>
> 1. **Run the full `bellows` test suite** → `full-suite.txt`: `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`. Record the raw summary line verbatim. ⚠️ The suite baseline before this plan was 874 passed (313's QA); this plan ADDS tests — report the fresh number, do not reconcile to 874.
> 2. **Re-run the targeted subset** → `targeted-tests.txt`: the Step 1 Task E command. Record raw output (≥ last 200 lines incl. the pytest summary line) — never a summary of it.
> 3. **Grep-proof all three sites** (bare `grep -F`, never through a pipe; state what each prints on success and on failure): `grep -F "qa_and_terminal" bellows.py` prints ≥2 lines (mode branch + WARN literal) and exits 0; `grep -F "clean_gate_auto" bellows.py` prints ≥1 line and exits 0; `grep -F "clean_gate_auto" verdicts/README.md` prints ≥1 line and exits 0.
> 4. **Observe the discrimination effect, not just execution:** cite the Task D test's assertion that a `clean_gate_auto` row is excluded by the awaiting-verdict filter, and quote that assertion's line from the test file in the report — the effect claim must trace to a line that ran, per the (D) standard.
> 5. **Emit the QA Receipt with the canonical Rule 20 self-check block.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
>    - `plan_slug`: `clean-gate-auto-continue-2026-08-08`
>    - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/clean-gate-auto-continue-qa-report-2026-08-08.md`
>    - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa`
>    - `required_evidence_files`: `[full-suite.txt, targeted-tests.txt]`
>    Deposit both evidence files BEFORE running the block — it `sys.exit(1)`s if any is missing or empty. Include the block's literal stdout. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014). If it prints FAILED, HALT.
> 6. **The QA report also states the semantic-shift note** (the `verdicts` table now carries non-pause `clean_gate_auto` rows; distribution analyses key on `pause_reason_code`) — the QA report is where a future analyst looks first.
> 7. **`### Ledger Updates` carries `#### Prompt Feedback` AND this `#### Forward Register` block — exactly TWO bullets, CONTIGUOUS, no blank line between them (the parser truncates at the first blank line; the two-bullet contiguous form is the 295-proven pattern):**
>
> - Post-activation live canary for clean_gate_auto: after the next daemon restart, a plan opted into pause_for_verdict qa_and_terminal must show gate_auto/clean_gate_auto rows for its non-terminal clean steps and pause at QA + terminal — the observed-delta proof this plan's QA cannot provide (Checklist #32; 295 precedent).
> - Document the qa_and_terminal pause mode in PLANNER_TEMPLATE.md (governance root, outside this plan's scope) at the next template touch — until then the mode is documented in bellows verdicts/README.md and the header_says_pause branch comment only.
>
> **Scope:**
> - `knowledge/qa/clean-gate-auto-continue-qa-report-2026-08-08.md`
> - `knowledge/qa/full-suite.txt`
> - `knowledge/qa/targeted-tests.txt`
>
> **STOP. Wait for CEO verdict.**

**Deposits:**
- `bellows/knowledge/qa/clean-gate-auto-continue-qa-report-2026-08-08.md`
- `bellows/knowledge/qa/full-suite.txt`
- `bellows/knowledge/qa/targeted-tests.txt`

---

## Method + boundaries

- **Scope:** one new header-mode branch + one recording pair in `bellows.py`, the `verdicts/README.md` pause-reason table (incl. the disclosed 313 `auto_close` backfill), plus tests. No schema change (`verdicts` columns all exist). No migration of historical rows. No daemon restart in-plan — activation is the canary follow-on's concern. **Documentation deferral (explicit):** `PLANNER_TEMPLATE.md` at the governance root is OUT of scope; the mode's template documentation is deferred via the second Forward bullet — not omitted silently.
- ⚠️ **HALT ROUTING:** if `bellows.py`, `lifecycle.py`, `verdicts/README.md`, `tests/test_gate_transaction_mechanization.py`, `tests/test_bellows.py`, the Bellows Developer specialist file, or `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (Step 2 item 5's block source) is unreadable, HALT the step that needs it and name it.
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim; a non-`-F` pattern can exit 1 silently on a present line); run the grep BARE, never through a pipe (`$?` after a pipe reports the last command's exit).
- ⚠️ Every `**Deposits:**` filename is the DECLARED deposit, matched by basename. Do NOT re-date any at run time.
- ⚠️ Every number above (3.08%, 83.3%, 874 baseline, ≥2 grep hits) is an authoring-time value — verify at run, report the actual, never force a match.

---

## Drafting Cycle

> **⚠️ THIS SECTION IS A RECORD, NOT INSTRUCTIONS.** Gate-matching strings are described, never quoted.

**Tier:** T2 — **T-6 fires**: this plan RELAXES a human checkpoint class (non-terminal clean-gate pauses become mechanical for opted-in plans) — the verdict-gate layer is governance surface, and unlike 313's additive relabel this changes what a human sees. T-8 also fires (a new pause mode is not a structure-for-structure clone; 313 is the pattern source for Site 2 only). Highest demand: T2 — full five-lens walk plus cold panel.
**Clone comparison (§2.6):** newest same-class shipped executable = `executable-313` (Done), the skeleton and Site-2 pattern source; the cold panel should also be handed 315's Q5/Q6 (the seam map and notification analysis this plan's design decisions cite).
**Walks:** 1, plus ACID pass a1, plus confirming pass c1 (four lenses; ACID's confirming read runs apart) — each phase its own turn, folds on CEO culminate (c1's three under the confirming-pass allowance).
- Weak spots:          w1 5 listed (2 real), culminated (Site 1 calls `is_final_step` so the predicates cannot drift; auto_close precedence pinned — mode wins at terminal, asserted structurally in Task C; the never-NULL claim made honest with the fail-soft/310-shape acknowledgment; Task C import hedge dropped — test_bellows precedent cited; Task E selection binding stated — CORRECTED at a1: the binding is the module-name term, not the class names).
- Destruction:         w1 1 listed + 1 disposition, culminated (semantic-shift note mandated in BOTH dev log and QA report — verdicts now carries non-pause rows, analyses key on pause_reason_code; disposition: Site 2 blast radius verified nil — both lifecycle writes internally fail-soft, gate failures pause regardless of mode, sole verdicts consumer is the awaiting query).
- Vulnerabilities:     w1 1 listed + 1 disposition, culminated (degenerate mode cases as Task C tests: total_steps=0 → always pause, single-step → pause at step 1; disposition: conftest isolation + import safety proven by 312/313/test_bellows precedent).
- Integration-record:  w1 2 listed, culminated (verdicts/README.md pause-table backfill added as Site 3 — clean_gate_auto row + the pre-existing 313 auto_close row, disclosed, count wording updated, scope/Deposits extended; the PLANNER_TEMPLATE documentation deferral made explicit via a second contiguous Forward bullet).
- ACID:                a1 3 listed (2 real, both introduced by w1's culmination), culminated (5.2 the -k binding rationale was false string-logic — underscored terms cannot match CamelCase class names; the true mechanism is the module-name term `transaction`, probe-verified 6/6 collected, and Task E now states it; 5.2 Task B retitled to three sites; 5.3 Q0's re-pin pathspec gained `verdicts/README.md` — the between-step window the scope extension opened and the culmination missed).
- c1 (confirming, four lenses): 3 folded then re-run dry (Weak spots 2 — A0's pre-edit pathspec and the HALT-ROUTING list both missed `verdicts/README.md` when Site 3 entered scope, the same class a1 caught at Q0, two more sites; Vulnerabilities 1 — Site 3's count-wording instruction would have had the agent write an inaccurate pause count, reworded to keep FIVE and distinguish recorded transition codes from pauses; Destruction and Integration-record dry outright, numbers re-verified against the 315 deposit).
**Cold panel (T2):** not yet run — owed after the warm cycle closes.
**Conflicts:** none recorded — no fold violated a prior lens's constraint at any culmination.
**Closing:** pending — c1 (four lenses) closed dry after its three in-pass folds; ACID's confirming read (apart) and the cold panel are owed. Not deposited.
