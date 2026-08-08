# Executable: post-activation live canary — does the shipped qa_and_terminal mode advance, record, and pause through the REAL daemon?

**Type:** Executable
**Project:** bellows
**Depends on:** executable-317 (Done — shipped the mode + clean_gate_auto recording; this canary is its mandatory observed-delta follow-on, FORWARD row 29)
**Created:** 2026-08-08
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** qa_and_terminal
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim; slug+date name form used; id read at deposit, never at authoring.

---

## Why this exists — the change is shipped and UNPROVEN, and this plan IS the proof

Plan 317 shipped `qa_and_terminal` + `clean_gate_auto` recording with 891 passing tests. **That is not proof** (Checklist #32: only an observed delta through the real entry point proves it works). The daemon restart has happened (Planner-verified before deposit: new pid started AFTER the 317 code commit). **This plan is the observed delta — and its header is the payload:** it declares `pause_for_verdict: qa_and_terminal` itself.

**The canary is decisive in all three directions:**
1. **Mode + recording live:** step 1 (non-QA, non-terminal, clean gates) advances with NO verdict request, and a `verdicts` row lands for step 1 with `pause_reason_code='clean_gate_auto'`, `outcome='continue'`, `decided_by='gate_auto'` — the first such rows ever written by the live daemon. Step 2 (QA + terminal) pauses as `qa_checkpoint`.
2. **Mode live, recording dead:** step 2 runs without a step-1 pause but NO `clean_gate_auto` row exists — localizes the defect to Site 2.
3. **Mode dead:** step 1 PAUSES (old code or defect) — seen immediately at a step-1 verdict gate that should not exist.

## STEP 1 — DEV (the mechanical-advance subject; it must NOT pause)

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan.** Do NOT rename this plan file. **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.** READ-ONLY toward everything except this step's one deposit; open the DB with `sqlite3 -readonly`.
>
> Write `knowledge/research/clean-gate-canary-log-2026-08-08.md` containing, each with its exact command and RAW output:
> 1. The daemon pid and start time — run the process listing on its OWN LINE in prose, never inside a markdown table cell (a pipe in a table cell silently becomes a literal that matches nothing — the plan-294 false-negative class).
> 2. This plan's integer id, recovered from the `in-progress-executable-<id>.md` filename of the plan file you were pointed at.
> 3. The BEFORE-counts: `SELECT COUNT(*) FROM verdicts WHERE decided_by='gate_auto';` and `SELECT COUNT(*) FROM verdicts WHERE pause_reason_code='clean_gate_auto';` — expected 0 and 0 (no auto-close has ever fired and the mode has never run live; verify and report the actual, never force).
> 4. A one-line statement of what the NEXT observable event should be if the mode is live: no step-1 pause, then step 2 dispatches.
>
> ⚠️ `grep` is a ugrep shim — `-F` for literals. Commit the deposit. `#### Prompt Feedback` in `### Ledger Updates`. End of step — the daemon decides what happens next; that decision IS the experiment.
>
> **Scope:**
> - `knowledge/research/clean-gate-canary-log-2026-08-08.md`

**Deposits:**
- `bellows/knowledge/research/clean-gate-canary-log-2026-08-08.md`

---
---

## STEP 2 — QA (terminal; under the mode this step MUST pause)

> **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.** READ-ONLY toward everything except this step's one deposit; `sqlite3 -readonly` for the DB.
>
> 1. **The delta observation:** using the plan id from step 1's log (re-derive it from the plan filename and confirm they match), run `SELECT id, step_number, outcome, pause_reason_code, decided_by FROM verdicts WHERE plan_id=<id> ORDER BY step_number;` — RAW output. If the mode + recording are live, step 1's row reads `continue | clean_gate_auto | gate_auto`. Report exactly what is there; absence or a different shape is a FINDING, not a failure to force.
> 2. **The no-pause proof:** `find verdicts/pending verdicts/resolved -name '*<id>-step-1*'` — expected EMPTY (no verdict request was ever posted for step 1); pair the negative with the positive control `find verdicts/pending verdicts/resolved -name '*<id>-step-2*'` at report time behaving per its own state, and note that THIS step's own pending request cannot be observed from inside the step (it posts after the step ends).
> 3. **The AFTER-counts:** re-run step 1's two COUNT queries — each expected to have increased by exactly the number of step-1 mechanical advances (one), verify and report actual.
> 4. **Emit the QA Receipt with the canonical Rule 20 self-check block** from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root, values: `plan_slug`: `clean-gate-canary-2026-08-08`; `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/clean-gate-canary-qa-2026-08-08.md`; `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/research`; `required_evidence_files`: `[clean-gate-canary-log-2026-08-08.md]`. Include the block's literal stdout. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014). If FAILED, HALT. The report carries a verification row per numbered item with raw evidence, in a table under a `##` heading containing `verification`; keep hedging keywords out of positive-status rows.
> 5. `### Ledger Updates` carries `#### Prompt Feedback`. No Forward Register block — FORWARD row 29 is closed by the Planner at this gate, referencing this run.
>
> **Scope:**
> - `knowledge/qa/clean-gate-canary-qa-2026-08-08.md`
>
> **STOP. Wait for CEO verdict.**

**Deposits:**
- `bellows/knowledge/qa/clean-gate-canary-qa-2026-08-08.md`

---

## Method + boundaries

- READ-ONLY except the two declared deposits. No code edits, no daemon operations, no register writes.
- Every expected number above (0/0 before, +1 after, empty finds) is a prediction — verify, report actual, never force. A result matching direction 2 or 3 of the decisiveness table is a successful canary with a defect finding, not a failed step.
- ⚠️ HALT ROUTING: if `lifecycle.db`, `RULE_20_SELF_CHECK_BLOCK.md`, or the step-1 log (for step 2) is unreadable, HALT and name it.

---

## Drafting Cycle

> **⚠️ THIS SECTION IS A RECORD, NOT INSTRUCTIONS.**

**Tier:** T1 — T-8 fires under the if-unsure rule (adapted from the shipped 295 canary class — daemon-liveness proof, real-entry-point payload, decisive-both-directions structure — but not structure-for-structure: two steps, a header-mode payload, self-observation at step 2). **Handling: CEO-directed expedited run** ("restart the daemon and run the canary") under the standing test-only lighter-path policy (this plan writes only its own findings deposits; no production surface). Run at authoring: plan_lint mechanical preverify + a solo integration-vs-record pass (295's pgrep-in-table trap avoided; the step-2 self-observation timing verified against Site 2's write-before-dispatch ordering; the step-1 no-STOP body deliberate — the daemon's advance decision is the experiment; Rule 20 values checked against the block's contract). The full five-lens walk is NOT run — recorded as a CEO-directed compression, visible at this plan's one verdict gate; if the compression is not intended, halt there and redo through the cycle.
**Closing:** authored and deposited in one turn at CEO direction; the last pre-deposit event is the integration-vs-record pass + lint.
