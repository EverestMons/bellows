# bellows — E4: verdict conditioning — fail-closed gate re-check at consumption, refusal disposition, override tool, dual-activation prep

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** `knowledge/research/e4-verdict-conditioning-design-2026-08-24.md` — sha256 `71f9760dd14ca47b847262868c2ce835a0826f505516c2a795f10d67f6f94ff1` — **the DESIGN (diagnostic-517), consumed T-7: every mechanism below is specified there with file:line and this plan BINDS its 7-row gap table; where a build-time correction and the design differ, the correction governs (the 513/516 clause).** Rulings: fork 5 ("daemon re-checks at consumption; verdict files stay plain; the enforcing party is the acting party"). Precedent: 511→513, 515→516 — the third run of the shape; both prior builds' full cold panels earned their cost (46 and 33 findings), so this plan's freeze convenes the full panel.

## Why this exists

Bypass (d): a `continue` on failed gates advances today, and the gate record itself defaults to CLEAN when the request file is absent (bellows.py:2570). The design settles the fix; this plan builds it: the dual-source fail-closed re-check, the reject-and-leave-pending disposition, the `--override-gate` tool arm that brings `gate_events.overridden`/`override_ref` alive (6431 rows, SUM(overridden)=0 — the dead-substrate class), and the canary/restart prep. ⚠️ **`_consume_verdicts` is how every plan advances; the containment law is double-sided: fail toward NOT-advancing, and never stall the scanner loop.**

## What this plan does NOT do

- **It does NOT restart the daemon.** Activation (one deliberate restart co-activating E3 retirement + E4 conditioning, with the design's D-5 canaries) is post-close Planner/CEO work, never part of this dispatch.
- **It does NOT touch verdict-file format.** Fork 5's "plain" stands; the override arm is a tool act on gate_events, and the D-7 parked question stays parked.
- **It does NOT alter stop verdicts, gate_auto advancement, the precondition retry, or the three retirement call sites** — all byte-identical (design D-4's fixed landmarks).

## Numbers discipline

⚠️ **Measured 2026-08-24 against bellows main post-517; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| X1 | design doc sha256 | `71f9760dd14ca47b847262868c2ce835a0826f505516c2a795f10d67f6f94ff1` | HALT on mismatch — the spec moved |
| X2 | target blob SHA-1s BEFORE | bellows.py `ae26abf741a4…` (matches the design's OWN pin — dual-verified), lifecycle.py `de249360fc26…`, tools/clear_plan.py `85ca9be1169e…`, tests/test_consume_verdicts.py `3ef30bea1849…` | `git hash-object` in YOUR worktree; HALT on mismatch — bellows.py moved twice today already (E3, portability) |
| X3 | **`T`** — tests collected BEFORE | **1325** | `python3 -m pytest tests/ --collect-only -q` **run from the bellows repo root as cwd** — a wrong-cwd run collects 899 with 14 import errors (measured; a false regression signal) |
| X4 | failability proofs | `--override-gate` **absent** from tools/clear_plan.py (`grep -cF -- '--override-gate'` = 0); `get_gate_failures_for_step` **absent** from lifecycle.py (= 0) | positive control, same instrument: `--release-class-hold` present in clear_plan.py, `record_gate_events` present in lifecycle.py |
| X5 | the fail-open fallback + insertion sites | bellows.py:2570 (the `or {"failures": []…}` default), :2574 (`record_verdict_outcome` before conditioning), :2576 (the `v == "continue"` entry), :2581 (teardown guard) | anchored by the code shapes, not line numbers; relocate by context on drift |
| X6 | the UPDATE predicate row-4 changes | lifecycle.py:577-581 | `UPDATE verdicts SET … WHERE plan_id = ? AND step_number = ? AND outcome IS NULL` — the `outcome IS NULL` clause is what blocks recording a rejection over an initial recording |
| X7 | gate_events substrate | 6431 rows, `SUM(overridden)=0`; pass+fail rows per step; writers only at bellows.py:1080/:1210 | sqlite ro; the columns this plan brings alive |
| X8 | consumption test surface | **20** tests in tests/test_consume_verdicts.py | must pass unchanged or with the two declared updates (design D-6) |

## Drafting Cycle
**Tier:** T2 computed — the verdict consumption path is live-guard code (T-5/T-6-adjacent); T-7 fires (builds from the 517 design). **Cold panel: MANDATED at the freeze (full form, four seats)** — the E-family build precedent, on the path every plan's advancement crosses.
**Walk register:** `governance/knowledge/research/walk-register-executable-eluvian-e4.md`
**Walks:** walk 0 pinned; walks 1–n OWED — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk. Rewritten at the close from the register's actual rows, never ahead of them.
**Direction verdict (after walk 1):** owed.
**Conformance (§5):** owed per lens; recorded at the close from actual runs.
**Closing:** owed. The deposit travels the lane WITH the receipt ritual (tool against the DRAFT bytes before staging) → expected HOLD `class:shop-infra` → the CEO's `--release-class-hold` act → claim.

## Cycle Manifest
tier: T2
target: bellows.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/knowledge/research/e4-verdict-conditioning-design-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: bellows.py, lifecycle.py, tools/clear_plan.py, tests/test_consume_verdicts.py, knowledge/research/e4-qa-2026-08-24.md, knowledge/research/pytest_full.txt
open_forks: (1) activation (restart + the D-5 dual canaries) is post-close Planner/CEO work; (2) the D-7 parked ruling (override line vs "plain") stays parked — the tool arm avoids it; (3) the design's request-file override fallback for slug-only legacy plans rides as designed (D-3), its audit trail in the ledger
walks: 0
yields: none
validation: pending
coherence: N/A

## MUST-PRESERVE

- ⚠️⚠️ **DOUBLE-SIDED CONTAINMENT.** Every new check fails toward NOT-advancing (a refused continue leaves the plan `verdict-pending-`), AND no exception in the new code may escape to stall `_consume_verdicts`' loop — per-verdict try/except, WARN log, continue to the next file. Test BOTH directions.
- ⚠️⚠️ **THE FIXED LANDMARKS ARE BYTE-IDENTICAL:** the three `_retire_receipts` calls (:2596/:2630/:2660 anchors), gate_auto sites (:1136/:1293), the precondition retry (:2641-2646), stop-verdict handling, `is_runnable_plan`/`is_claimable`. Q2 proves each by targeted diff.
- ⚠️ **The rejection is IDEMPOTENT:** one rejection, one notification, the verdict file renamed to its processed/rejected form so the scanner never re-processes it — the malformed-verdict precedent (bellows.py:2506-2508).
- ⚠️ **Legacy plans keep a path:** `_lc_plan_id is None` → the request-file fallback (design D-1/D-4); a DB-only fail-closed check that bricks slug-only resumes is a named defect.
- ⚠️ **The design's D-5 canary spec is carried VERBATIM into the QA report's activation section as the post-close instruction sheet** — this plan preps activation, never performs it.
- ⚠️ **Worktree + test isolation:** tmp dirs and tmp DBs only; never the real lifecycle.db, never a real watched decisions/ path.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals; `--` before dash-leading literals** (this plan greps for `--override-gate`).
- ⚠️ **DEV runs TARGETED tests only; the full suite belongs to QA.**

## STEP 1 — DEV: the re-check, the disposition, the override tool

**Role:** DEV. `<id>` from your plan filename.

**A0 — preconditions.** Assert X1–X8 (X1/X2 HALT; X5 relocates by context). Three-way start: pins as stated → proceed; the full substrate already present (`--override-gate` + `get_gate_failures_for_step` + the :2570 fail-closed flip) → ALREADY APPLIED no-op success; else partial → STOP with inventory.

**A1 — implement the gap table's 7 rows, the design governing:**
- **Row 5 first** — `lifecycle.py`: `get_gate_failures_for_step(plan_id, step_number, db_path=None)` → unoverridden fail rows as `[{"gate","evidence"}]`, `None` when the step has NO gate_events rows at all (the tri-state matters: no-rows ≠ no-failures); pure read, ro connection, whole-body try → None-on-error with a WARN (the caller falls back to the request file).
- **Row 4** — `lifecycle.py:577-581`: the UPDATE predicate gains the rejection-overwrite arm the design specifies (a `continue-rejected` outcome may overwrite a just-recorded `continue`; nothing else gains overwrite rights).
- **Rows 1+2+3** — `bellows.py` in `_consume_verdicts`: at the :2576 entry of the continue branch, the dual-source re-check — primary `get_gate_failures_for_step` (id-native plans), fallback the request-file `gate_result_from_request` failures lacking `"overridden": true`; **fail-closed: BOTH sources absent (`_lc_plan_id` id-native but no gate_events rows AND no request file) → refuse as unverifiable**; slug-only legacy plans use the fallback alone, absent request file → refuse with the legacy disposition named. On unoverridden failures (and not `precondition_failure_from_request`): the D-2 disposition — ledger entry, `record_verdict_outcome(..., "continue-rejected", decided_by="gate_recheck", disposition_summary=<gates>)`, the verdict file renamed `processed-rejected-verdict-…` (scanner-idempotent), the plan LEFT `verdict-pending-`, one notification naming the failing gates, and a fresh verdict may be issued after an override or a corrective. The teardown guard (:2581) stays as its distinct halted-routing arm, evaluated AFTER the general re-check refuses or passes (its disposition differs by design). All new code inside the per-verdict try; an exception → WARN + skip this verdict file only.
- **Row 6** — `tools/clear_plan.py`: `--override-gate <plan-id-or-slug> <step> <gate> --ref "<justification>"` beside `--release-class-hold`. ⚠️ **CLI compatibility constraint: the existing invocations must keep working byte-for-byte — `clear_plan.py <hold-file>` and `clear_plan.py --release-class-hold <hold-file>` (both have live tests and live muscle memory); the override mode takes a DIFFERENT argument shape, so restructure deliberately (argparse subcommands, or a mode flag whose own args are validated before the hold-file positional is demanded) rather than bolting a third shape onto the `hold_file` positional.** The arm itself: id-native → UPDATE the gate_events fail row to `overridden=1, override_ref=<ref>` (refuse if no matching fail row); slug-only → the design's request-file fallback with the ledger note; prints what it changed; the deliberate human act, mirroring the release arm's posture.

**A2 — targeted tests (extend `tests/test_consume_verdicts.py`, tmp DBs/dirs):** continue+clean advances (regression); continue+failed-unoverridden → rejected: plan stays verdict-pending, outcome row `continue-rejected`, verdict file renamed, second scan is a no-op (idempotency); continue+failed+overridden advances; the tri-state: no gate_events rows + no request file → refused unverifiable; legacy slug-only + request-file failures → refused via fallback; legacy + clean request file → advances; stop verdicts byte-identical behavior; teardown guard still routes to halted; poisoned verdict file (unreadable/malformed mid-check) → that file skipped, next verdict still consumed (scanner containment); `--override-gate` writes the row (and its refusal arms).

**A3 — verify before committing:** new tests green (paste raw); `py_compile` the three source files + the test file; `grep -c -F -- '--override-gate' tools/clear_plan.py` ≥ 1 and `grep -cF 'get_gate_failures_for_step' lifecycle.py bellows.py` both ≥ 1 (the X4 absences now present — failability proven both directions).

**A4 — commit** (worktree): `git add bellows.py lifecycle.py tools/clear_plan.py tests/test_consume_verdicts.py && git commit -m "[<id>] E4: fail-closed gate re-check at consumption + rejection disposition + --override-gate (INERT until restart)"`

⚠️ **IF ANY A3 CHECK FAILS: no commit, no revert, no retry — leave the worktree as evidence, report, raise `### Flags for CEO`.**

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py`

## STEP 2 — QA

**Role:** QA. ⚠️ Fresh agent: re-measure; the DEV report is not evidence.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd** (X3's wrong-cwd trap); deposit RAW output as `pytest_full.txt`. Baseline **1325 collected, green, known_failures 0**; the count grows by A2's new tests; assert zero failures/errors, report the total.
**Q2 — change-set vs the design's gap table:** all 7 rows present at their sites as bound by A1; the fixed landmarks byte-identical — `git diff` scoped to the three retirement call lines, the gate_auto sites, the precondition retry, and the stop branch is EMPTY; `is_runnable_plan`/`is_claimable` untouched; no file outside the four declared.
**Q3 — behavioral spot-probes on tmp environments:** the full consume sim — tmp lifecycle DB + tmp watched dir + synthetic verdict-pending trio: (i) failed-gate continue → rejected, plan still verdict-pending, re-scan no-op; (ii) override via the tool → re-issued verdict advances; (iii) both-sources-absent → refused unverifiable; (iv) legacy slug-only both arms. Paste raw.
**Q4 — activation prep, stated honestly:** the change is daemon code, INERT until restart (state the live PID + `ps -o lstart=` vs the merge); reproduce the design's D-5 canary spec VERBATIM as the post-close instruction sheet (both canaries, the scratch watched dir, every daemon outcome enumerated); state that this plan performed NO activation.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1–Q4 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e4-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e4-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Commit:** `git add knowledge/research/e4-qa-2026-08-24.md knowledge/research/pytest_full.txt && git commit -m "[<id>] qa: E4 conditioning — full suite + evidence"`

## Deposit ritual

The E3 contract, in full: (1) `python3 tools/deposit_receipt.py <draft-path> <session-id>` against the DRAFT bytes; (2) stage as `ready-executable-eluvian-e4-conditioning.md` (same bytes; the receipt's hash must match the clearance the release writes); commit both together. **Expected depositor outcome: HOLD `class:shop-infra` — by construction.** Release: the CEO runs `python3 tools/clear_plan.py --release-class-hold <hold-file>` as the deliberate act. The depositing session arms a slug-keyed watcher BEFORE the receipt.
