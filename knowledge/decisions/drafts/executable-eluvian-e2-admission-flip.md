# bellows — E2: the admission flip — clearance record, `is_claimable` at every dispatch site, auto-HOLD, class split, gated clear tool

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** `knowledge/research/e2-admission-flip-design-2026-08-24.md` — sha256 `801f66d406be052646d217caa0bf5301f9e742e240e93bdd91c5d9bcbdfb94ad` — **the DESIGN, consumed T-7 without re-derivation: every mechanism below is specified there with file:line, and this plan BINDS it rather than restating it.** Rulings: `governance/knowledge/research/eluvian-path-rulings-2026-08-24.md` (R1; fork 2 grandfather+gated-clear; fork 4 classes). Precedent: `executable-481` (the depositor build from design-478 — same two-step shape, and its cold panel caught 5 majors, which is why this plan's freeze convenes the full panel).

## Why this exists

R1: *"bellows only accepting a drafting cycle cleared plan — this is the only way that bellows can work on something."* The design settles how; this plan builds it. ⚠️ **The claim path is the single most sensitive code in the shop: a wrong flip either blocks all dispatches or admits unchecked ones.** Containment is designed in — unclearable files HOLD visibly instead of dispatching, and activation is a separate deliberate restart with a two-arm canary.

## What this plan does NOT do

- **It does NOT activate the flip.** The running daemon keeps its old code; restart + the D-6 canary are a post-close Planner/CEO step, never part of this dispatch.
- **It does NOT migrate old files.** Fork 2 grandfather: `halted-`/`parked-`/`hold-` files stay; their only path back in is the clear tool.
- **It does NOT change verdict semantics, worktree machinery, or any gate other than admission.**
- **It does NOT touch `~/.claude`** (the E1 structural finding does not apply here — all writes are in the bellows repo).

## Numbers discipline

⚠️ **Measured 2026-08-24; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| X1 | design doc sha256 | `801f66d406be052646d217caa0bf5301f9e742e240e93bdd91c5d9bcbdfb94ad` | HALT on mismatch — the spec moved |
| X2 | target blob SHA-1s BEFORE | bellows.py `6a22a9ea306d…`, depositor.py `553a5d7d92e2…`, lifecycle.py `c8652ec63c6c…` | `git hash-object` in YOUR worktree; HALT on mismatch |
| X3 | **`T`** — tests collected BEFORE | **1231** | `python3 -m pytest tests/ --collect-only -q` tail; the suite is GREEN at baseline (known_failures 0) |
| X4 | the six `is_runnable_plan` call sites | bellows.py:2053, :2065, :2220, :2346, :2622, :2702 | per the design's G1 table AS CORRECTED by design-correction 3: TWO become `is_claimable` (2065 with the arm, 2053 on full_path), FOUR stay bare (2346/2702 as listing filters that funnel into `_handle`; 2220/2622 enumerate) — the classification and both failure modes are IN the design; re-verify the line numbers against your X2 tree, and if they drifted, locate by the design's context descriptions, never by number |
| X5 | `lifecycle.py` DDL insertion point | after the `idx_plans_active_placeholder` index block, before `conn.commit()` (measured at lines ~163-169 of 737) | anchored by the index name, not the line number |
| X6 | `bellows/tools/` | **does not exist** | `mkdir -p` it; the clear tool is its first file — and this is the failability proof for its post-condition |
| X7 | clearances table | **absent** from lifecycle.db | `pragma_table_info('clearances')` returns nothing — failability proof for D-1's post-condition |

## Drafting Cycle
**Tier:** T2 computed — **T-5/T-6-adjacent (daemon claim path = live-guard code)**, T-7 fires (builds from the 511 design). ⚠️ **FULL COLD PANEL AT THE FREEZE — mandated by the audit's risk class and the 481 precedent, not decided ad hoc:** scout → discovery → execution → capstone, sequential, findings folded between seats, every finding author-verified before folding.
**Walk register:** `governance/knowledge/research/walk-register-executable-eluvian-e2.md`
**Walks:** walk 0 pinned; walks 1+ under v2.13 auto-advance, per-lens commits, cycle_check branched after each walk.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged: one isolation hazard folded; the binding to design-511 held under attack; no premise or ruling touched. None of the forcing classes fires.
- Weak spots:          w1 dry (binding attacked, held); w2 dry
- Destruction:         w1 dry (mixed-state windows attacked, held by design); w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0 (test-dir isolation); w2 dry
- Integration-record:  w1 dry (gate-lesson checklist verified: known_failures, named .txt, banner pair); w2 dry
- ACID:                w1 dry (sweep exit-gated); w2 dry
**Conformance (§5):** per lens; recorded at the **walk-2 close** (the phase label is the LAST run): plan_lint exit 0 / 0 FAIL; register CONFORMANT (STDERR); propagation exit 0; fold_check exit 0 against the walk-1 baseline.
**Warm phase closed at walk 2 (instruction series 1 → 0); the freeze now convenes the mandated FULL COLD PANEL** — scout → discovery → execution → capstone, sequential, each seat's findings author-verified and folded before the next seat reads. The panel's verdict gates the deposit; the cycle does not close until the panel's fold set is swept.

## Cycle Manifest
tier: T2
target: bellows.py
class: governed-tooling
reads: /Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-admission-flip-design-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: bellows.py, depositor.py, lifecycle.py, tools/clear_plan.py, tests/test_admission_flip.py
open_forks: (1) activation (restart + canary) is post-close Planner/CEO work; (2) the design's two escalatable-not-blocking notes (shop-infra rule maintenance; clear-tool async reporting) ride along unresolved
walks: 0
yields: (owed)
validation: (owed)
coherence: N/A — the emitter's sentinel; NOT hand-filled
N/A

## Design corrections — cold-scout findings, author-verified, BINDING over design-511 where they conflict

⚠️⚠️ **The design is a CLOSED deposit and stays byte-stable; THIS section is the spec-of-record for the nine deltas below.** Each was found by the cold scout, re-verified by the Planner against live code, and is folded here rather than annotated around — the DEV implements the corrected form.

1. **(S-1, HIGH) `_assign_class` takes PROJECT IDENTITY.** The design's prefix rule matches only cross-repo spellings (`bellows/...`) while real write sets arrive project-relative (`scripts/plan_lint.py`) or absolute — measured: four of the design's own acceptance-table rows misclassify `app-feature` under its own code. Corrected: `_assign_class(self, writes, project_root)` — the caller `_do_evaluate` already holds `project_root`; classification is by (project identity × path rule): a write inside a shop-infra project's tree (bellows/forge/lessons-forge/anvil) outside `knowledge/` is `shop-infra` REGARDLESS of spelling; governance-root top-level likewise; the design's cross-repo prefixes remain as an ADDITIONAL match. **The 20-row acceptance test is written from the table's literal write strings + each row's project, and must pass against the corrected rule before commit.**
2. **(S-2, HIGH) `_resume_parked` is RESUME, not admission — and the grandfather sentence is corrected.** bellows.py:2259 renames `parked-X` → `in-progress-X` and calls `handle_new_plan` directly: that path resumes an ALREADY-CLAIMED plan and is deliberately NOT gated (gating it would break mid-run resumes). The design's "only path back in" claim is corrected to: *the clear tool is the only path for `hold-` files; `parked-` files resume by the existing resume machinery; `halted-` files re-enter only via a new corrective plan (existing practice).* The tool's preconditions (hold- prefix + sidecar) are correct as designed.
3. **(S-3, HIGH) The gate lives at TWO sites, not four.** Rescan (bellows.py:2346) and startup (:2702) keep `is_runnable_plan` as the LISTING filter and funnel into `_handle`, where the single gate + auto-HOLD arm decides — otherwise an unclearable file discovered by rescan is silently skipped forever, never held, and permanently pins the idle-notify count. Gated sites: `_handle` entry (:2065, with the arm) and `collect_group` (:2053, the parallel path, using full_path). Gap-table rows 11/12 are SUPERSEDED: no replacement at 2346/2702.
4. **(S-4, HIGH) Clearance row BEFORE the rename, `INSERT OR IGNORE`.** The rename fires `on_moved` → `_handle` → lookup instantly (bellows.py:2135-2138), racing a write-after-rename; and `UNIQUE(content_hash)` without OR-IGNORE breaks the legitimate re-clear of identical bytes. The hash is content-keyed and name-independent, so an early row is harmless if the rename then fails. The design's `test_clearance_uniqueness` expectation becomes idempotent-insert (second insert of the same hash: no error, one row).
5. **(S-5, HIGH) Row-level deltas vs the gap table, stated once:** row 16 (`status.py` clearance panel) deliberately SKIPPED — follow-up, not this plan; rows 17–19 CONSOLIDATED into `tests/test_admission_flip.py`. Everything else: all rows, as corrected by items 1–4 and 6–8 here.
6. **(S-6, MED) `is_claimable` fail-toward-HOLD covers the WHOLE body.** The design snippet's try wraps only the file read; a sqlite error would unwind the dispatch loop or watchdog. Corrected: one try around everything after the name check — any exception → return False.
7. **(S-7, MED) The enumerate-site test is restated to what is true:** `hold-`/`ready-` files were never visible to the bare name check. The preserved property is: a BARE unclearable file remains counted by :2220/:2622 until the arm renames it, and both sites are byte-unchanged (`git diff` scoped to their functions is empty). Both halves tested/asserted exactly so.
8. **(S-8, MED) Taxonomy consumers swept:** new gap row — `plan_lint.py:494` `_STANZA_VALID_CLASSES` becomes `{"read-only","app-feature","register-writing","shop-infra","governed-tooling"}` (old name retained as LEGACY-declarable), and the depositor's `class_mismatch` check accepts declared `governed-tooling` as matching a computed `app-feature` OR `shop-infra` — so pre-flip manifests (including this plan's own) neither lint invalid nor hard-hold after activation.
9. **(S-9, LOW, hardening) Deposit ritual:** when staging `ready-`, copy the fold-check sidecar beside it under both the `ready-` name and the post-clear name (dotfiles are not claimable) — removes any dependence on commit-message luck in cycle_check's context detection.

## MUST-PRESERVE

- ⚠️⚠️ **THE FLIP MUST FAIL TOWARD HOLD, NEVER TOWARD DISPATCH.** Any error inside `is_claimable` (DB unreadable, hash failure) returns False and the auto-HOLD arm fires — an admission check that fails open re-opens bypass (a) with extra steps. Test this branch explicitly.
- ⚠️⚠️ **THE TWO ENUMERATE SITES (bellows.py:2220, :2622) KEEP THE BARE NAME CHECK.** Gating them makes held plans invisible to idle-notify and orphan reconciliation — the design states both failure modes; re-read them before touching either site.
- ⚠️ **The depositor writes the clearance row BEFORE the rename (design-correction 4), `INSERT OR IGNORE`, keyed to the sha256 of the plan's bytes** — the same bytes the daemon will snapshot at claim. A post-clearance byte change invalidates clearance BY CONSTRUCTION; that is a feature, and a test proves it, alongside the idempotent same-hash re-insert.
- ⚠️ **`_assign_class` replacement is FORCE-CLASSIFYING: no catch-all `return` may remain.** An unmatchable write set HOLDs as `unassignable_class` (existing arm). The design's 20-plan acceptance table is reproduced as a parameterized test.
- ⚠️ **The safety invariant survives: the depositor never mints, never dispatches; the clear tool never evaluates — it renames `hold-` → `ready-` and the live daemon's evaluator decides** (design D-5, option (b)).
- ⚠️ **Worktree discipline:** all writes at project-relative paths under YOUR cwd; commit there; teardown merges. ⚠️⚠️ **Test isolation is DIRS as well as DBs: every test uses a tmp DB AND tmp directories — no test may name a real watched `knowledge/decisions/` path, because a test that renames or creates a claimable-looking file in a LIVE watched dir summons the RUNNING daemon mid-test.** The clear-tool and auto-HOLD tests in particular construct their own scratch dirs.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **DEV runs TARGETED tests only; the full suite belongs to QA** (long runs tempt end_turn before commit).

## STEP 1 — DEV

**Role:** DEV.

**A0 — preconditions.** Assert X1–X7 (X1/X2 HALT on mismatch; X4 line numbers may drift — relocate by context, report what you found). Three-way start per the standard: pins as stated → proceed; all changes already present (clearances table in DDL, `is_claimable` defined, tools/clear_plan.py exists) → ALREADY APPLIED, idempotent no-op success; anything else → partial state, STOP with the artifact-by-artifact inventory.

**A1 — implement the Rule 27 gap table, ALL rows, in the design's numbering.** The design is the spec; do not re-derive mechanisms. Summary of the change set (the design's table governs where it and this differ): lifecycle.py — `clearances` DDL (X5 anchor) + `write_clearance()` / `has_clearance()`; depositor.py — clearance write in `_clear()` after the rename, auto-clear expansion (read-only + app-feature + register-writing on full-pass; shop-infra HELD), rule-based `_assign_class` replacement + its constants; bellows.py — `is_claimable(path, db_path)` beside `is_runnable_plan` (which stays untouched), gated at the TWO sites per design-correction 3 (`_handle` entry with the auto-HOLD `no_clearance` arm mirroring the once-per-slug WARN discipline, and `collect_group` on full_path); rescan/startup keep the bare listing filter; `tools/clear_plan.py` per D-5(b) with its three preconditions and async outcome message.

**A2 — targeted tests, new file `tests/test_admission_flip.py`:** the design's D-7 table, including at minimum: clearance write/read round-trip on a tmp DB; `is_claimable` False on (no record, byte-drift after clearance, unreadable DB — the fail-toward-HOLD branch); the auto-HOLD arm renames + writes `.hold.json` `no_clearance` exactly once per slug — including via the rescan funnel (design-correction 3); the class split's 20-plan acceptance table parameterized WITH project identity (design-correction 1); same-hash re-insert idempotent (design-correction 4); clear-tool preconditions + rename target; the restated enumerate property per design-correction 7. Run the NEW file plus the design's named neighbor suites (`test_bellows.py` depositor/claim regions, `test_cycle_check.py`) — targeted, not full.

**A3 — verify before committing:** new-file tests green; `python3 -m pytest tests/test_admission_flip.py -q` output pasted raw; `py_compile` all four changed modules; `pragma_table_info('clearances')` on a tmp-initialized DB shows the DDL landed.

**A4 — commit** (worktree): `git add bellows.py depositor.py lifecycle.py tools/clear_plan.py tests/test_admission_flip.py && git commit -m "[<id>] admission flip: clearance record, is_claimable, auto-HOLD, class split, clear tool (INERT until restart)"`. `<id>` from your plan filename.

⚠️ **IF ANY A3 CHECK FAILS: no commit, no revert, no retry — leave the worktree as evidence, report every measured value, raise `### Flags for CEO`.**

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/depositor.py`
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_admission_flip.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/depositor.py`
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_admission_flip.py`

## STEP 2 — QA

**Role:** QA. ⚠️ Fresh agent: re-measure; Step 1's report is not evidence.

**B1 — full suite.** `python3 -m pytest tests/ -q` from the worktree root; deposit RAW output as `pytest_full.txt`. Baseline was **1231 collected, green, known_failures 0** — ⚠️ the count GROWS by the new file's tests; assert zero failures and zero errors, report the new total. ⚠️ **The hot-path-guard lesson applies: `is_claimable` is a new boolean gate on the dispatch path and MagicMock-based tests elsewhere may break silently — the full suite is exactly where that class surfaces; name every failure and diagnose before any classification.**
**B2 — re-verify the change set against the design's Rule 27 table:** every row's change present at its site (by context anchor); the two ENUMERATE sites verifiably UNCHANGED (`git diff` scoped to their functions is empty); `is_runnable_plan` itself byte-unchanged.
**B3 — behavioral spot-probes on a tmp environment** (never the live daemon): clearance round-trip; byte-drift invalidation; fail-toward-HOLD on an unreadable DB; the 20-plan class table.
**B4 — the INERT claim:** assert the LIVE daemon (old code) is untouched — its PID unchanged since claim, and the live lifecycle.db has NO clearances table yet (the DDL runs at init, which happens at restart). State plainly: activation is post-close.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. The Rule 20 block and the B1–B4 results go in the `.md` deposit; the raw suite output goes in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Commit:** `git add knowledge/research/e2-qa-2026-08-24.md knowledge/research/pytest_full.txt && git commit -m "[<id>] qa: admission flip — full suite + evidence"` in YOUR worktree.
