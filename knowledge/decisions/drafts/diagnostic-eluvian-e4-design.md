# bellows — E4 design: verdict conditioning — the consumption-time gate re-check, the refusal disposition, the override arm, activation

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only design; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md` §E4 + bypass (d), and `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md` **fork 5, which RULES the mechanism: "Daemon re-checks at consumption — the daemon re-runs the gate check when consuming a `continue`; verdict files stay plain; the enforcing party is the acting party."** Both consumed T-7. **Structural precedent:** `diagnostic-511`→`executable-513` (E2) and `diagnostic-515`→`executable-516` (E3) — the same two-step shape, third running.

## Why this exists

Bypass (d): a `continue` verdict on a FAILED gate is structurally permitted — the only conditioning in `_consume_verdicts` today is the worktree_teardown rejection, and the gate record itself defaults to CLEAN when the request file is absent (G2). Fork 5 rules the fix's shape; this diagnostic settles the mechanism against the live code so the executable inherits decisions, not open questions. **The verdict consumption path is how every plan advances; a wrong implementation blocks all verdict processing — settled read-only first, like E2 and E3.**

## What this plan does NOT do

- **It writes NO code.** One research deposit with a Rule 27 gap table, the 511/515 pattern.
- **It does not re-open fork 5.** Daemon-side re-check is RULED; the design implements it. If the override arm's shape needs a NEW ruling on what "plain" permits, that lands in D-7, never decided silently.
- **It does not break continue-with-reasoning.** The benign-gate-failure workflow is real and precedented; D-3 exists to preserve it under enforcement.
- **It does not restart the daemon or touch live state.**

## Numbers discipline

⚠️ **Measured 2026-08-24 against bellows main (post-E3, `c3da7e7` era); RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| G1 | bypass (d) re-derived | only worktree_teardown conditions a continue | bellows.py:2576-2597 — the `v == "continue"` branch's sole gate consultation; `record_verdict_outcome` at :2574 fires BEFORE any conditioning; every other failed gate + continue → advances |
| G2 | the fail-open gate-record fallback | bellows.py:2570 | `gate_result = gate_result_from_request or {"failures": [], "files_changed": []}` — an absent or unparseable pending-request file reads as NO FAILURES, so deleting `verdicts/pending/verdict-request-<slug>-step-N.md` evades even the teardown guard. E4 must flip this fail-closed |
| G3 | the pre-built, unconsumed substrate | lifecycle.py:470-510; DDL `gate_events(step_id, gate_name, result CHECK IN ('pass','fail'), reason_code, overridden INTEGER DEFAULT 0, override_ref)` | `record_gate_events` writes BOTH pass rows and fail rows per step (called at bellows.py:1080, :1210) — a durable gate record that survives request-file deletion. ⚠️ **Writers of `overridden`/`override_ref`: NONE — measured on the live DB: 6431 gate_events rows, `SUM(overridden)=0`; grep across bellows.py/gates.py/verdict.py/tools/ finds no writer (positive control: `record_gate_events` found at its 2 call sites). Nothing at consumption READS gate_events either — the same dead-substrate class as `cleared_by='clear_tool'` (the 2026-08-24 enum-arm lesson). E4 brings both halves alive** |
| G4 | a full gate re-RUN post-teardown is impossible | gates.py:186 | `check(parsed, plan_text, step_number, project_path, files_changed=None, wt_path=None)` needs step-time context — the agent's parsed output and the worktree, which teardown destroys at step end (failures recorded at bellows.py:1116/:1243/:1276). "Re-runs the gate check" must therefore mean CONSUMING THE RECORD (file and/or gate_events), plus at most a re-derivable subset — the design states which honestly |
| G5 | verdict file contract | verdict.py:282-302 | first line `(?:verdict:\s*)?(continue|stop)`, reason = remainder; malformed → skip + notify (bellows.py:2504-2508). The ruling's "verdict files stay plain" constrains D-3 |
| G6 | the workflow E4 must not break | precedent | continue-with-reasoning on known-benign gate failures (the exec-493 evidence-path false positive class; the shop's benign-failure catalog) — enforcement without an override arm converts every false-positive gate into a hard block |
| G7 | consumption test surface | **20** | `grep -cE '^def test\|^    def test'` tests/test_consume_verdicts.py — must pass unchanged or with declared updates |
| G8 | live state at authoring | daemon PID 22189 predates the E3 merge (retirement inert); suite **1325** green; `id_sequence` next **517** (prediction only — key by slug); E3's `_retire_receipts` calls sit INSIDE `_consume_verdicts` at :2596/:2630/:2660 — fixed landmarks E4 edits around | ps; pytest --collect-only; sqlite ro |

## Drafting Cycle
**Tier:** T1 computed — T-7 fires twice over (consumes audit+rulings; feeds the executable). Read-only.
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-eluvian-e4-design.md`
**Walks:** walk 0 pinned; walks 1–n OWED — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk. This line is rewritten at the close from the register's actual rows, never ahead of them.
**Direction verdict (after walk 1):** owed.
**Cold panel:** owed — decided at the freeze with reasoning (the E-family precedent puts the full panel on the EXECUTABLE, where it has earned 46- and 33-finding yields; this read-only design feeds it).
**Conformance (§5):** owed per lens; recorded at the close from actual runs.
**Closing:** owed. ⚠️ When the cycle closes, the deposit travels the lane WITH THE E3 RECEIPT RITUAL — `tools/deposit_receipt.py` against the DRAFT bytes BEFORE staging (the first receipt-bearing deposit) → ready- staging → depositor auto-clear (read-only) → claim.

## Cycle Manifest
tier: T1
target: knowledge/research/e4-verdict-conditioning-design-2026-08-24.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/verdict.py, /Users/marklehn/Developer/GitHub/bellows/gates.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db, /Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: knowledge/research/e4-verdict-conditioning-design-2026-08-24.md
open_forks: none authored here — fork 5 is ruled and the design implements it; anything needing a NEW ruling (above all the "plain verdict file" boundary for the override arm) lands in D-7
walks: 0
yields: none
validation: pending
coherence: N/A

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. `lifecycle.db` via ro URI only.
- ⚠️ **Every design decision cites file:line in CURRENT code**; every absence claim carries a positive control.
- ⚠️ **The conditioning must FAIL TOWARD NOT-ADVANCING, never toward dispatch** — and equally must never crash the scanner loop: `_consume_verdicts` runs on every poll; an unhandled raise in the new check stalls ALL verdict processing for ALL plans. Both failure directions stated per mechanism.
- ⚠️ **The enum-arm lesson governs G3:** `overridden`/`override_ref` are FEATURE CLAIMS with zero writers today — the design names the writer it builds for each, or deletes the claim.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **This plan dispatches into a WORKTREE**; the deposit path is project-relative under YOUR cwd.

## STEP 1 — DIAGNOSTIC: settle the design, emit the document

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e4-verdict-conditioning-design-2026-08-24.md` (project-relative in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the re-check mechanism.** What the daemon consults when consuming a `continue`, defended against alternatives: (a) the request file's `Gate Result JSON` (today's carrier — parsed at bellows.py:2545-2549, but deletable and currently fail-open per G2); (b) `gate_events` rows for the step (durable, pass-and-fail, survives file deletion — G3); (c) both-must-agree. ⚠️ Whatever wins: **absence of a gate record is UNVERIFIABLE, not clean** — the G2 fallback flips fail-closed, with the disposition for legacy/edge plans that genuinely predate gate recording stated (how does an old parked plan's resume behave?). Decide honestly what "re-runs the gate check" means under G4: consuming the recorded verdict-time result, plus (optionally) the re-derivable subset — name which gates ARE re-derivable post-teardown against the merged tree (deposit_exists? evidence-file presence?) and whether re-deriving any is worth the drift risk (a file legitimately moved between step-end and consumption reads as a new failure). Specify the exact insertion point in `_consume_verdicts` relative to `record_verdict_outcome` (:2574 currently fires BEFORE any conditioning — should a refused continue still record an outcome row, and as what?), and the interaction with the existing teardown guard (:2581 — subsumed by the general check or kept as a distinct arm with its distinct halted-routing disposition).
**D-2 — the refusal disposition.** A `continue` on unoverridden failed gates: reject-and-leave-pending (the plan stays `verdict-pending-`, the verdict file is renamed/annotated so the scanner does not re-process it every poll — the malformed-verdict precedent at :2506-2507 — and the Planner is notified with the failing gates named) versus route-to-halted (the teardown precedent). Pick with costs; specify idempotency (the scanner loops — one rejection, one notification, no log storm), the notification content, and what the Planner does next in each arm (fix + re-issue vs corrective plan).
**D-3 — the override arm (the benign-failure workflow under enforcement).** G6's workflow must survive. Candidates, each weighed against fork 5's "verdict files stay plain": (a) an explicit override declaration in the verdict file (e.g. a line naming the overridden gate + justification — is a human judgment line "plain" in the ruling's sense? The ruling's target was embedded checker exit codes; if this reading is in doubt, D-7 it); (b) a separate gated override tool (the `clear_plan.py --release-class-hold` precedent — a deliberate second act that marks `gate_events.overridden=1` + `override_ref` BEFORE the verdict is written, keeping the verdict file untouched); (c) a benign-class allowlist in config (names the drift risk — the shop's invisible-when-incomplete lesson). ⚠️ Whichever wins WRITES `overridden`/`override_ref` (G3's dead columns get their writer) and the consumption check honors overridden fail rows; the audit trail requirement: who overrode what, why, discoverable later.
**D-4 — interaction with existing flows.** Each stated with file:line: gate_auto advancement (:1136/:1293 — already gated on clean gates; assert unaffected), precondition-failure retry (:2641-2646), stop verdicts (never conditioned — a stop on failed gates is the system working), the auto_close path, orphan-verdict reconciliation, and E3's retirement calls (:2596/:2630/:2660) as fixed landmarks the executable's diff must leave byte-identical. ⚠️ **The no-lifecycle-identity arm is its own case:** `_lc_plan_id` is None for any slug-only plan (:2572-2573 — the fullmatch is id-native only), and gate_events keys on step_id, which needs a plan id — a DB-backed fail-closed check would refuse EVERY legacy plan's continue unconditionally. The design states what the re-check consults when no DB identity exists (the request-file record alone? refuse with a named disposition?) and which grandfathered/parked resume paths can still present this shape today.
**D-5 — activation + coordination.** The change is daemon-code: INERT until restart. ⚠️ The pending restart ALSO activates E3's `_retire_receipts` — one deliberate restart, two arcs' activation; specify the post-restart canary for BOTH (a continue on a synthetic failed-gate verdict-request → observe the refusal disposition; a plan close → observe receipt retirement), each canary SAFE-IF-MISFIRED per the E2 canary lesson — ⚠️ **and safe in its CONSTRUCTION: a synthetic verdict-pending plan + request + verdict trio placed in a real watched dir is live daemon input (the incident-mandate class — the daemon acts within seconds), so the canary design must enumerate every outcome the daemon could take on it (advance, halt, reject, retire) and be harmless under ALL of them, or use a dedicated scratch watched dir added to config for the canary window.** Name the shared-file fence: bellows.py moved under E3 this same day — the executable X-pins the blob and HALTs on drift.
**D-6 — test plan.** Extend tests/test_consume_verdicts.py (20 baseline): continue+clean advances; continue+failed-unoverridden → the D-2 disposition; continue+failed+overridden advances with the override recorded; absent request file AND absent gate_events → fail-closed; stop unaffected; teardown guard preserved; scanner-loop exception containment (a poisoned verdict file cannot stall other plans' consumption). Which existing tests change and why; full suite 1325 stays green.
**D-7 — open questions.** Anything requiring a NEW CEO ruling — above all whether an override line inside the verdict file violates "verdict files stay plain" — LISTED, never decided silently.

**Post-conditions:** D-1 through D-6 each with ≥1 file:line citation; D-7 present, exempt from the citation requirement exactly when it truthfully reports none; fork 5's sentence quoted once verbatim; G2's fail-open fallback and G3's zero-writer columns re-derived with positive controls; a Rule 27 gap table enumerating every code-change site the executable will touch.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e4-verdict-conditioning-design-2026-08-24.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e4-verdict-conditioning-design-2026-08-24.md`

**Commit:** `git add knowledge/research/e4-verdict-conditioning-design-2026-08-24.md && git commit -m "[<id>] design: E4 verdict conditioning — re-check mechanism, refusal disposition, override arm, dual activation"` in YOUR worktree cwd. `<id>` from your plan filename.
