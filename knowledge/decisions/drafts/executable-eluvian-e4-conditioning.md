# bellows — E4: verdict conditioning — fail-closed gate re-check at consumption, refusal disposition, override tool, dual-activation prep

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** `knowledge/research/e4-verdict-conditioning-design-2026-08-24.md` — sha256 `71f9760dd14ca47b847262868c2ce835a0826f505516c2a795f10d67f6f94ff1` — **the DESIGN (diagnostic-517), consumed T-7: every mechanism below is specified there with file:line and this plan BINDS its 7-row gap table; where a build-time correction and the design differ, the correction governs (the 513/516 clause).** Rulings: fork 5 ("daemon re-checks at consumption; verdict files stay plain; the enforcing party is the acting party"). Precedent: 511→513, 515→516 — the third run of the shape; both prior builds' full cold panels earned their cost (46 and 33 findings), so this plan's freeze convenes the full panel.

## Build-time corrections (panel seat 1, author-verified — these govern where they and the design differ)

- **C-1 — the REQUEST FILE is MANDATORY for any continue (unifies S1-1/S1-9).** Teardown failures NEVER reach gate_events — `record_gate_events` (:1080/:1210) runs BEFORE the teardown try appends its failure (:1110-1116/:1237-1243/:1268-1276; measured: 0 teardown rows in 6438) — and re-run steps legitimately have NO gate_events rows at all (`steps UNIQUE(plan_id, step_number)` makes their recording a silent no-op). The request file is therefore the ONLY carrier for both classes. Corrected rule: **absent request file → refuse as unverifiable, for EVERY plan class** (id-native included — a deleted request file must never read as clean even when gate_events pass rows exist); gate_events stays the corroborating primary for gate rows when present; a request file PRESENT but carrying no parseable `Gate Result JSON` → refuse as unverifiable likewise.
- **C-2 — the rejection path PRESERVES the request file and skips the consumption tail (S1-2).** The existing tail unlinks the pending request whenever `plan_matched` (:2667-2674 class) and moves the verdict file; a rejection must short-circuit before it — the request file survives (it is the override fallback's truth source and the teardown carrier), and the already-renamed verdict file must not be re-moved.
- **C-3 — teardown class EXCLUDED from the general check's trigger set (S1-6).** The general re-check runs first but skips `worktree_teardown` failures, leaving them to the :2581 guard's distinct halted/R2 disposition — otherwise a fallback-path teardown failure gets reject-and-leave-pending, orphaning unmerged commits.
- **C-4 — the audit-trail shape at rejection (S1-5).** Writing `continue-rejected` on the NULL row makes the plan vanish from status.py's AWAITING VERDICT scan and leaves the post-override re-issued continue with no row to resolve. Corrected: at rejection, resolve the NULL row as `continue-rejected` AND insert a fresh pending verdicts row (outcome NULL) for the same (plan, step) — status keeps showing the pause, and the re-issued verdict resolves the fresh row.
- **C-5 — the try's scope and skip semantics (S1-7).** No per-verdict try exists today (the loop is guarded only for KeyboardInterrupt). The re-check is implemented as a HELPER FUNCTION called from one inserted line (no re-indentation of the three retirement landmarks); its narrow try, on exception, WARNs and skips this verdict file WITHOUT consuming it — no advance, no reject, no tail — retried next poll.
- **C-6 — test-update census corrected (S1-3).** FIVE existing tests (lines ~40/93/371/423/642 in test_consume_verdicts.py) construct request files with no `Gate Result JSON` line and break under C-1's fail-closed rule — all five are UPDATED (given gate JSON or asserting the new refusal), superseding the design D-6's "2 updates"; test 642's documented fail-open expectation inverts to the refusal it now proves.
- **C-7 — isolation at the call site (S1-4).** `get_gate_failures_for_step` is CALLED with an explicit `db_path` from the daemon's configured lifecycle path — never default-resolved inside `_consume_verdicts` — so test patching governs; A2's tests pass tmp paths.
- **C-8 — divergences declared (S1-8).** The rename target `processed-rejected-verdict-<slug>-step-<N>.md`, the override CLI's explicit `<step>` argument, and the row-4 predicate's rejection-overwrite form are deliberate plan-over-design corrections under this block's governing clause.

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
| X8 | consumption test surface | **20** tests in tests/test_consume_verdicts.py | must pass unchanged or with the FIVE C-6 updates (the design D-6's "2" is superseded — five tests construct JSON-less request files that C-1 refuses) |

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
- **Rows 1+2+3** — `bellows.py` in `_consume_verdicts`, implemented as a HELPER FUNCTION called from ONE inserted line at the :2576 entry of the continue branch (C-5 — the three retirement landmarks keep their bytes): **C-1's rule first — request file absent, or present without parseable `Gate Result JSON` → refuse as unverifiable, every plan class**; then the dual-source check — gate_events primary via `get_gate_failures_for_step(plan_id, step, db_path=<the daemon's configured path>)` (C-7), request-file failures lacking `"overridden": true` as the fallback and cross-check; **the trigger set EXCLUDES `worktree_teardown` (C-3)** — those flow to the :2581 guard's halted/R2 arm unchanged. On unoverridden failures (and not `precondition_failure_from_request`): the D-2 disposition as corrected — ledger entry; resolve the NULL verdicts row as `continue-rejected` (decided_by `gate_recheck`, gates in the summary) AND insert a fresh pending row so status.py keeps the pause visible and a post-override re-issue has a row to resolve (C-4); rename the verdict file `processed-rejected-verdict-<slug>-step-<N>.md`; **short-circuit BEFORE the consumption tail — the pending request file is PRESERVED (C-2)**; the plan stays `verdict-pending-`; one notification naming the gates. The helper's narrow try: exception → WARN, skip this verdict file WITHOUT consuming it, retried next poll (C-5).
- **Row 6** — `tools/clear_plan.py`: `--override-gate <plan-id-or-slug> <step> <gate> --ref "<justification>"` beside `--release-class-hold`. ⚠️ **CLI compatibility constraint: the existing invocations must keep working byte-for-byte — `clear_plan.py <hold-file>` and `clear_plan.py --release-class-hold <hold-file>` (both have live tests and live muscle memory); the override mode takes a DIFFERENT argument shape, so restructure deliberately (argparse subcommands, or a mode flag whose own args are validated before the hold-file positional is demanded) rather than bolting a third shape onto the `hold_file` positional.** The arm itself: id-native → UPDATE the gate_events fail row to `overridden=1, override_ref=<ref>` (refuse if no matching fail row); slug-only → the design's request-file fallback with the ledger note; prints what it changed; the deliberate human act, mirroring the release arm's posture.

**A2 — targeted tests (extend `tests/test_consume_verdicts.py`, tmp DBs/dirs — every new-path DB access via the C-7 explicit db_path):** continue+clean advances (regression); continue+failed-unoverridden → rejected: plan stays verdict-pending, NULL row resolved `continue-rejected` PLUS a fresh pending row exists (C-4), request file PRESERVED on disk (C-2), verdict file renamed, second scan is a no-op (idempotency); continue+failed+overridden advances and resolves the fresh row; **C-1 arms: request file absent → refused (id-native WITH gate_events pass rows too — the deleted-request attack); request file present, no Gate Result JSON → refused**; legacy slug-only + request-file failures → refused via fallback; legacy + clean request file → advances; **teardown-in-fallback → the :2581 guard's halted routing, NOT the rejection arm (C-3)**; stop verdicts byte-identical; poisoned verdict file → skipped unconsumed, next verdict still processed (C-5); `--override-gate` writes the row (and its refusal arms); **the FIVE C-6 legacy-test updates, each named in the diff**.

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
