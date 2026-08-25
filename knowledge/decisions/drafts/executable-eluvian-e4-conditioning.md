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
- **C-7 — isolation at the call site (S1-4).** The lifecycle reader (now `get_overridden_gates_for_step` after C-11's rename) is CALLED with an explicit `db_path` — `lifecycle.LIFECYCLE_DB_PATH` at the daemon site, never default-resolved inside `_consume_verdicts` — so test patching governs; A2's tests pass tmp paths.
- **C-9 — the PRECEDENCE INVERSION (S2-3 + S2-6, dissolving both).** gate_events rows persist from a step's FIRST pass while a retry's recording silently no-ops (`steps UNIQUE`) — a DB-primary read serves STALE failures against a clean re-run; and after an id-native override, the request file still carries the failure unmarked, so any conjunction reading bricks the override workflow. Corrected architecture: **the REQUEST FILE is the per-pause truth source for what failed; `gate_events` is the OVERRIDE-ANNOTATION layer only** — the check reads the request's failures, then consults gate_events solely to ask which of those gates carry `overridden=1` rows for this (plan, step); slug-only plans keep the request-file-edit override fallback. Stale rows can no longer reject anything (they are consulted only for override status of currently-reported failures), and dual-source disagreement is impossible by construction.
- **C-10 — the tail gains a declared edit site (S2-1).** A rejection cannot be contained by one inserted line: `plan_matched` is already True at :2566 and the consumption tail (:2667 class) unconditionally unlinks the pending request and moves the verdict file — for a rejected verdict that is a FileNotFoundError on the already-renamed file, OUTSIDE any handler (the poll loop catches only KeyboardInterrupt) — **every rejection would crash the daemon.** The gap table's row 2 becomes TWO sites: the helper call at :2576, and a `rejected` flag threaded to the tail's condition so it neither unlinks the request nor re-moves the verdict for rejected consumptions.
- **C-11 — record once, after the check (S2-2, deleting gap row 4).** Instead of recording `continue` at :2574 and overwriting on rejection (a multi-row UPDATE trap: the widened predicate could flip HISTORICAL continue rows, and insert-before-resolve lets `outcome IS NULL` eat the fresh row), the initial `record_verdict_outcome` call MOVES to after the re-check and records the true outcome once — `continue` or `continue-rejected` — with C-4's fresh pending row inserted only on rejection, after the resolve. **Design gap row 4 (the lifecycle.py predicate change) is DELETED**; lifecycle.py leaves this plan's write set entirely (`get_gate_failures_for_step` becomes an override-status reader per C-9, named `get_overridden_gates_for_step`).
- **C-12 — the precondition skip precedes C-1 (S2-4).** A precondition-failure retry's request may carry no meaningful gate JSON — `precondition_failure_from_request` is checked FIRST and routes to the existing retry arm untouched; C-1's refusal applies only to non-precondition continues. Test census: SIX updates (the five plus test ~975, the id-native JSON-less close assertion).
- **C-13 — Q3's probes must not touch the real DB (S2-5).** "The daemon's configured lifecycle path" does not exist as a config field; the call site passes `lifecycle.LIFECYCLE_DB_PATH` explicitly (monkeypatch-able), and the override tool gains `--db-path` (defaulting to the repo-resolved path) so QA's subprocess probes hit tmp DBs — without it, Q3(ii) writes the REAL lifecycle.db from a worktree.
- **C-14 — small arms (S2-7/8/9).** A second rejection's rename appends a numeric suffix rather than overwriting the first's evidence; the CLI-compatibility constraint extends to the FUNCTION API (`clear_plan`, `release_class_hold` are imported by test_admission_flip and test_wrap_receipts — signatures stay); an override marks ALL matching unoverridden fail rows for the (plan, step, gate), not "the" row.
- **C-15 — the tail edit is a NESTING change (S3-1, executed).** A literal `if plan_matched and not rejected:` sends every rejection into the no-match `else:` arm (spurious WARN + `_warned_no_match` pollution) and, with a stale same-slug Done/halted entry present, re-moves the renamed verdict → the crash class again. The tail keeps `if plan_matched:` outer and gains `if not rejected:` INNER around the unlink/move body.
- **C-16 — only the CONTINUE recording moves (S3-2, executed).** Moving the whole :2574 call drops STOP-verdict recording — the halted plan's verdicts row stays NULL and status.py's AWAITING VERDICT (no state filter) shows it forever, while the stop branch's Q2 byte-identity mandate forbids the repair there. Corrected: `if v != "continue": record_verdict_outcome(v)` stays at the pre-branch site; the continue path records post-check per C-11.
- **C-17 — the census crosses files: FOURTEEN updates, and test_bellows.py joins the write set (S3-5, executed — ship-blocker).** tests/test_bellows.py carries EIGHT more casualties (lines ~498/834/877/968/1029/1075/1875/3348 — JSON-less or request-less continues expecting advance); it was outside Scope and Deposits, making Q1's zero-failure gate unreachable by a compliant executor. test_bellows.py is added to A1/A2/A4, Deposits, Scope; the census is fourteen (six in test_consume_verdicts + eight in test_bellows); the seat's proto run with all fourteen applied reached 1320 passed / 5 scratch-environment-only failures.
- **C-18 — the slug-only fallback needs `--pending-dir` (S3-3, executed).** C-13 parameterized only the DB arm; the request-file fallback resolves from the hardwired root, so Q3(iv)'s tmp probe cannot run. The override tool gains `--pending-dir` (defaulting to the repo-resolved verdicts/pending); Q3(iv) mandates it.
- **C-19 — no vacuous survivors (S3-4, executed).** Tests :525/:583 pass VACUOUSLY under E4 (they now take the rejection path while asserting only the mocked ledger's arguments) — both are updated to assert the rejection explicitly, and advance-path gate-JSON coverage is added so the old behavior class keeps a real test.
- **C-20 — mixed-failure priority ruled (S3-6).** A gate set containing `worktree_teardown` PLUS other failures routes to the :2581 guard's halted/R2 arm FIRST — the rejection arm applies only when no teardown failure is present; C-3's "exclusion" is clarified to this priority.
- **C-21 — the refusal notification is its own payload (S3-7).** `notify_verdict_request` with empty failures renders "all gates passed"; the refusal notifies with a distinct message naming the refusal class (unverifiable vs failed-gates) and the gate list.
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
| X4 | failability proofs | `--override-gate` **absent** from tools/clear_plan.py (`grep -cF -- '--override-gate'` = 0); `get_overridden_gates_for_step` **absent** from lifecycle.py (= 0) | positive control, same instrument: `--release-class-hold` present in clear_plan.py, `record_gate_events` present in lifecycle.py |
| X5 | the fail-open fallback + insertion sites | bellows.py:2570 (the `or {"failures": []…}` default), :2574 (`record_verdict_outcome` before conditioning), :2576 (the `v == "continue"` entry), :2581 (teardown guard) | anchored by the code shapes, not line numbers; relocate by context on drift |
| X6 | the UPDATE predicate row-4 changes | lifecycle.py:577-581 | `UPDATE verdicts SET … WHERE plan_id = ? AND step_number = ? AND outcome IS NULL` — the `outcome IS NULL` clause is what blocks recording a rejection over an initial recording |
| X7 | gate_events substrate | 6431 rows, `SUM(overridden)=0`; pass+fail rows per step; writers only at bellows.py:1080/:1210 | sqlite ro; the columns this plan brings alive |
| X8 | consumption test surface | **20** tests in tests/test_consume_verdicts.py | must pass unchanged or with the FOURTEEN C-17 updates across test_consume_verdicts.py (six) and test_bellows.py (eight) — the design D-6's "2" is twice-superseded |

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
writes: bellows.py, lifecycle.py, tools/clear_plan.py, tests/test_consume_verdicts.py, tests/test_bellows.py, knowledge/research/e4-qa-2026-08-24.md, knowledge/research/pytest_full.txt
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

**A0 — preconditions.** Assert X1–X8 (X1/X2 HALT; X5 relocates by context). Three-way start: pins as stated → proceed; the full substrate already present (`--override-gate` + `get_overridden_gates_for_step` + the :2570 fail-closed flip) → ALREADY APPLIED no-op success; else partial → STOP with inventory.

**A1 — implement the gap table's 7 rows, the design governing:**
- **Row 5 first** — `lifecycle.py`: **`get_overridden_gates_for_step(plan_id, step_number, db_path)` per C-9/C-11** → the set of gate names carrying `overridden=1` fail rows for the step's gate_events (empty set when no rows); pure read, ro connection, whole-body try → empty-set-on-error with a WARN (an unreadable DB must not turn overrides into rejections NOR failures into passes — on error the caller treats NO gates as overridden, failing toward not-advancing). `db_path` is REQUIRED at the daemon call site: `lifecycle.LIFECYCLE_DB_PATH` passed explicitly (C-13).
- **Row 4 — DELETED per C-11.** lifecycle.py's `record_verdict_outcome` predicate is untouched; the recording moves instead (row 2).
- **Rows 1+2+3** — `bellows.py` in `_consume_verdicts`, TWO declared sites (C-10): (i) the HELPER FUNCTION called at the :2576 entry of the continue branch, (ii) the `rejected` flag at the consumption tail **as a NESTING change (C-15): `if plan_matched:` stays outer, `if not rejected:` wraps the unlink/move body inner** — a conjunction on the outer condition routes rejections into the no-match arm and can still crash on stale same-slug entries; without (ii) at all, every rejection is an unhandled FileNotFoundError in the poll loop. The helper, in order: **the precondition skip FIRST (C-12** — `precondition_failure_from_request` routes to the existing retry arm untouched); **then C-1 — request file absent, or present without parseable `Gate Result JSON` → refuse as unverifiable, every plan class**; then the check under **C-9's architecture: the request file's failures are the per-pause truth; `get_overridden_gates_for_step` (row 5) supplies the override annotations; a failure whose gate is in the override set (or carrying `"overridden": true` in the request JSON — the slug-only fallback) is discharged**; **the trigger set EXCLUDES `worktree_teardown` (C-3)** — those flow to the :2581 guard's halted/R2 arm unchanged. On surviving failures: the disposition — ledger entry; **record ONCE, after the check (C-11): `record_verdict_outcome` with `continue-rejected` (decided_by `gate_recheck`, gates in the summary), then insert the fresh pending row (C-4, via `record_verdict_request`)**; rename the verdict file `processed-rejected-verdict-<slug>-step-<N>.md` (a second rejection suffixes, never overwrites — C-14); set the `rejected` flag; the plan stays `verdict-pending-`; one notification with the REFUSAL'S OWN payload — the refusal class (unverifiable vs failed-gates) and the gate list, never `notify_verdict_request`'s default "all gates passed" rendering (C-21). **Mixed-failure priority (C-20): a set containing `worktree_teardown` plus others routes to the :2581 guard FIRST; the rejection arm applies only teardown-free.** On a CLEAN pass: `record_verdict_outcome("continue")` fires at this post-check position — **ONLY the continue recording moves; `if v != "continue"` recording stays at the pre-branch site or the halted plan haunts AWAITING VERDICT forever (C-16)**. The helper's narrow try: exception → WARN, skip this verdict file WITHOUT consuming it, retried next poll (C-5).
- **Row 6** — `tools/clear_plan.py`: `--override-gate <plan-id-or-slug> <step> <gate> --ref "<justification>"` beside `--release-class-hold`. ⚠️ **CLI compatibility constraint: the existing invocations must keep working byte-for-byte — `clear_plan.py <hold-file>` and `clear_plan.py --release-class-hold <hold-file>` (both have live tests and live muscle memory); the override mode takes a DIFFERENT argument shape, so restructure deliberately (argparse subcommands, or a mode flag whose own args are validated before the hold-file positional is demanded) rather than bolting a third shape onto the `hold_file` positional.** The arm itself: id-native → UPDATE **ALL matching unoverridden fail rows for the (plan, step, gate)** to `overridden=1, override_ref=<ref>` (C-14; refuse if none match); slug-only → the design's request-file fallback (`"overridden": true` on the failure entry) with the ledger note; **`--db-path` AND `--pending-dir` arguments, each defaulting to the repo-resolved path (C-13/C-18 — QA's tmp probes require both; without them a worktree probe writes the REAL lifecycle.db or reads the real pending dir)**; prints what it changed; the deliberate human act, mirroring the release arm's posture. **The compatibility constraint covers the FUNCTION API too (C-14): `clear_plan` and `release_class_hold` keep their signatures — test_admission_flip and test_wrap_receipts import them.**

**A2 — targeted tests (extend `tests/test_consume_verdicts.py`, tmp DBs/dirs — every new-path DB access via the C-7 explicit db_path):** continue+clean advances (regression); continue+failed-unoverridden → rejected: plan stays verdict-pending, NULL row resolved `continue-rejected` PLUS a fresh pending row exists (C-4), request file PRESERVED on disk (C-2), verdict file renamed, second scan is a no-op (idempotency); continue+failed+overridden advances and resolves the fresh row; **C-1 arms: request file absent → refused (id-native WITH gate_events pass rows too — the deleted-request attack); request file present, no Gate Result JSON → refused**; legacy slug-only + request-file failures → refused via fallback; legacy + clean request file → advances; **teardown-in-fallback → the :2581 guard's halted routing, NOT the rejection arm (C-3)**; stop verdicts byte-identical; poisoned verdict file → skipped unconsumed, next verdict still processed (C-5); `--override-gate` writes ALL matching rows via `--db-path` (and its refusal arms); **the stale-rows arm (C-9): first-pass fail rows present in gate_events + a clean retry request → advances (stale rows reject nothing)**; the precondition-retry request routes to the retry arm before C-1 (C-12); **the FOURTEEN C-17 legacy-test updates across BOTH files (six in test_consume_verdicts.py incl. the C-19 vacuous pair rewritten to assert the rejection explicitly + new advance-path gate-JSON coverage; eight in test_bellows.py at the C-17 lines), each named in the diff**.

**A3 — verify before committing:** new tests green (paste raw); `py_compile` the three source files + BOTH test files; `grep -c -F -- '--override-gate' tools/clear_plan.py` ≥ 1 and `grep -cF 'get_overridden_gates_for_step' lifecycle.py bellows.py` both ≥ 1 (the X4 absences now present — failability proven both directions).

**A4 — commit** (worktree): `git add bellows.py lifecycle.py tools/clear_plan.py tests/test_consume_verdicts.py tests/test_bellows.py && git commit -m "[<id>] E4: fail-closed gate re-check at consumption + rejection disposition + --override-gate (INERT until restart)"`

⚠️ **IF ANY A3 CHECK FAILS: no commit, no revert, no retry — leave the worktree as evidence, report, raise `### Flags for CEO`.**

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py`

## STEP 2 — QA

**Role:** QA. ⚠️ Fresh agent: re-measure; the DEV report is not evidence.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd** (X3's wrong-cwd trap); deposit RAW output as `pytest_full.txt`. Baseline **1325 collected, green, known_failures 0**; the count grows by A2's new tests; assert zero failures/errors, report the total.
**Q2 — change-set vs the design's gap table:** all 7 rows present at their sites as bound by A1; the fixed landmarks byte-identical — `git diff` scoped to the three retirement call lines, the gate_auto sites, the precondition retry, and the stop branch is EMPTY; `is_runnable_plan`/`is_claimable` untouched; no file outside the four declared.
**Q3 — behavioral spot-probes on tmp environments:** the full consume sim — tmp lifecycle DB + tmp watched dir + synthetic verdict-pending trio: (i) failed-gate continue → rejected, plan still verdict-pending, request file still on disk, re-scan no-op; (ii) override via the tool **with `--db-path` pointing at the tmp DB (C-13 — omitting it writes the REAL lifecycle.db from your worktree)** → re-issued verdict advances; (iii) request-file-absent → refused unverifiable; (iv) legacy slug-only both arms, the override fallback via `--pending-dir` at the tmp tree (C-18). Paste raw.
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
