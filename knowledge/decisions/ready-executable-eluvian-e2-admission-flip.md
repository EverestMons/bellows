# bellows — E2: the admission flip — clearance record, `is_claimable` at every dispatch site, auto-HOLD, class split, gated clear tool

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV-A — admission substrate) → Step 2 (DEV-B — claim path + tool) → Step 3 (QA) | **qa_steps:** 3 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** `knowledge/research/e2-admission-flip-design-2026-08-24.md` — sha256 `801f66d406be052646d217caa0bf5301f9e742e240e93bdd91c5d9bcbdfb94ad` — **the DESIGN, consumed T-7 without re-derivation: every mechanism below is specified there with file:line, and this plan BINDS it rather than restating it.** Rulings: `governance/knowledge/research/eluvian-path-rulings-2026-08-24.md` (R1; fork 2 grandfather+gated-clear; fork 4 classes). Precedent: `executable-481` (the depositor build from design-478 — same two-step shape, and its cold panel caught 5 majors, which is why this plan's freeze convenes the full panel).

## Why this exists

R1: *"bellows only accepting a drafting cycle cleared plan — this is the only way that bellows can work on something."* The design settles how; this plan builds it. ⚠️ **The claim path is the single most sensitive code in the shop: a wrong flip either blocks all dispatches or admits unchecked ones.** Containment is designed in — unclearable files HOLD visibly instead of dispatching, and activation is a separate deliberate restart with a two-arm canary.

## What this plan does NOT do

- **It does NOT activate the flip.** The running daemon keeps its old code; restart + the D-6 canary are a post-close Planner/CEO step, never part of this dispatch.
- **It does NOT migrate old files.** Fork 2 grandfather, in correction 2's corrected form: `hold-` files re-enter ONLY via the clear tool; `parked-` files resume by the existing resume machinery (already-claimed, deliberately ungated); `halted-` files re-enter only via a new corrective plan.
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
| X8 | grandfather set today | **parked- 0 · hold- 0 · halted- ≈16–18 (enumerate exactly)** | per-dir scan of all 10 watched dirs; `parked_steps` lives in **bellows.db** (not lifecycle.db) and is EMPTY — the design's "41 parked" reproduces nowhere (correction 20) |

## Drafting Cycle
**Tier:** T2 computed — **T-5/T-6-adjacent (daemon claim path = live-guard code)**, T-7 fires (builds from the 511 design). **Cold panel: CONVENED AT THE FREEZE (full form, four seats) — COMPLETE.** scout 9 / discovery 12 / execution 10 / capstone 15; 46 findings, 16 HIGH; folded as corrections 1–31 + the capstone sweep (step split, instruction restatement); capstone's NOT-READY verdict discharged by the sweep and walk 3's exit-gated dry pass.
**Walk register:** `governance/knowledge/research/walk-register-executable-eluvian-e2.md`
**Walks:** walk 0 pinned; **walks 1–3 complete** — warm walks 1–2 (one fold, then dry) under v2.13 auto-advance with cycle_check branched; **the FULL COLD PANEL at the freeze: scout 9 → discovery 12 → execution 10 → capstone 15 = 46 findings (16 HIGH), every one author-verified before folding, non-decaying to the last seat**; walk 3 = the post-panel sweep walk, all lenses dry, exit-gated.
**Direction verdict (after walk 1): PROCEED — re-tested after the panel and still PROCEED:** the panel corrected mechanisms and instructions but validated the shape (two-step 478→481 lineage, the clearance mechanism, the class split under the ruled taxonomy); the capstone verified no live correction-vs-correction contradiction survives.
- Weak spots:          w1 dry (binding attacked, held); w2 dry; w3 dry (post-panel sweep: no superseded phrasing survives)
- Destruction:         w1 dry (mixed-state windows attacked, held by design); w2 dry; w3 dry (step boundaries + dispositions)
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0 (test-dir isolation); w2 dry; w3 dry (corrected asserts satisfiable AND failable)
- Integration-record:  w1 dry (gate-lesson checklist verified: known_failures, named .txt, banner pair); w2 dry; w3 dry (header/deposits/ritual/corrections agree)
- ACID:                w1 dry (sweep exit-gated); w2 dry; w3 dry (exit-gated probe battery)
**Conformance (§5):** per lens; recorded at the **walk-3 close** (the phase label is the LAST run): plan_lint exit 0 / 0 FAIL; register CONFORMANT (STDERR); propagation exit 0; fold_check re-baselined at the panel close (the panel's fold set is the intended delta).
**Closing:** **walk 3 met the bar — the post-panel sweep walk, all five lenses dry, probe battery exit-gated.** Warm series 1 → 0; panel series 9 → 12 → 10 → 15 with every finding folded or explicitly arbitrated; no unswept residue (the capstone's own check-1 verified the correction system coherent). ⚠️ The cycle is CLOSED; the deposit follows the plan's own Deposit ritual — expected HOLD `class:governed-tooling` under the live old code, released by the final sanctioned bypass-(b) rename.
**Warm phase closed at walk 2 (instruction series 1 → 0); the freeze now convenes the mandated FULL COLD PANEL** — scout → discovery → execution → capstone, sequential, each seat's findings author-verified and folded before the next seat reads. The panel's verdict gates the deposit; the cycle does not close until the panel's fold set is swept.

## Cycle Manifest
tier: T2
target: bellows.py
class: governed-tooling
reads: /Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-admission-flip-design-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: bellows.py, depositor.py, lifecycle.py, gates.py, scripts/plan_lint.py, tools/clear_plan.py, tests/test_admission_flip.py
open_forks: (1) activation (restart + canary) is post-close Planner/CEO work; (2) the design's two escalatable-not-blocking notes (shop-infra rule maintenance; clear-tool async reporting) ride along unresolved
walks: 3
yields: 1, 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: N/A
N/A

## MUST-PRESERVE

- ⚠️⚠️ **THE FLIP MUST FAIL TOWARD HOLD, NEVER TOWARD DISPATCH.** Any error inside `is_claimable` (DB unreadable, hash failure) returns False and the auto-HOLD arm fires — an admission check that fails open re-opens bypass (a) with extra steps. Test this branch explicitly.
- ⚠️⚠️ **THE TWO ENUMERATE SITES (bellows.py:2220, :2622) KEEP THE BARE NAME CHECK.** Gating them makes held plans invisible to idle-notify and orphan reconciliation — the design states both failure modes; re-read them before touching either site.
- ⚠️ **The depositor writes the clearance row BEFORE the rename (correction 4), `INSERT OR IGNORE`, under a PARTIAL unique index `(content_hash, plan_path) WHERE consumed_at IS NULL` (correction 23), storing the CLAIMABLE path (correction 25), hash = raw `read_bytes` (correction 19).** A post-clearance byte change invalidates clearance BY CONSTRUCTION; tests prove it alongside the idempotent same-hash re-insert and the correction-25 end-to-end clear→claimable round trip.
- ⚠️ **`_assign_class` replacement is FORCE-CLASSIFYING: no catch-all `return` may remain.** An unmatchable write set HOLDs as `unassignable_class` (existing arm). The design's 20-plan acceptance table is reproduced as a parameterized test.
- ⚠️ **The safety invariant survives: the depositor never mints, never dispatches; the clear tool never evaluates — it renames `hold-` → `ready-` and the live daemon's evaluator decides** (design D-5, option (b)).
- ⚠️ **Worktree discipline:** all writes at project-relative paths under YOUR cwd; commit there; teardown merges. ⚠️⚠️ **Test isolation is DIRS as well as DBs: every test uses a tmp DB AND tmp directories — no test may name a real watched `knowledge/decisions/` path, because a test that renames or creates a claimable-looking file in a LIVE watched dir summons the RUNNING daemon mid-test.** The clear-tool and auto-HOLD tests in particular construct their own scratch dirs.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **DEV runs TARGETED tests only; the full suite belongs to QA** (long runs tempt end_turn before commit).

## STEP 1 — DEV-A: the admission substrate

**Role:** DEV. ⚠️ The corrected change-set outgrew one step (capstone C-12); this is the SUBSTRATE half. `<id>` from your plan filename.

**A0 — preconditions.** Assert X1–X8 (X1/X2 HALT on mismatch; X4 lines relocate by context; X8 report-only). Three-way start: pins as stated → proceed; the substrate already present (clearances DDL + corrected `_assign_class` + widened lint class set + gates allowlist) → ALREADY APPLIED no-op success; else partial → STOP with inventory.

**A1 — implement the SUBSTRATE rows of the gap table AS CORRECTED — the corrections govern where they and the table differ (C-1):**
- `lifecycle.py`: `clearances` DDL at the X5 anchor with the **partial unique index `(content_hash, plan_path) WHERE consumed_at IS NULL`** (correction 23) + `write_clearance()` / `has_clearance(content_hash, plan_path)` requiring `consumed_at IS NULL` (correction 14) / `consume_clearance()` **called from inside `mint_and_claim`'s BEGIN IMMEDIATE transaction in DEV-B** — here you only define it.
- `depositor.py`: clearance write in `_clear()` **BEFORE the rename, storing the CLAIMABLE path, hashing raw `read_bytes`** (corrections 4/25/19); the **pre-clear recheck moves with the clear branch to every auto-clearing class** (correction 18); auto-clear expansion (read-only + app-feature + register-writing on full-pass; shop-infra HELD); rule-based `_assign_class(writes, project_root)` with **precedence read-only > shop-infra > unresolvable→None(HOLD) > register-writing > app-feature** (corrections 1/12/27/31).
- `scripts/plan_lint.py:494`: the widened `_STANZA_VALID_CLASSES` (correction 8).
- `gates.py:29`: `hold-` + `ready-` in `SCOPE_ALLOWLIST_PREFIXES` (correction 17).

**A2 — targeted tests (new file `tests/test_admission_flip.py`, substrate half):** clearance round-trip; same-hash re-insert idempotent; path-mismatch refuses; consumed refuses; **the correction-25 END-TO-END test: `_clear()` on a tmp dir then `is_claimable` on the resulting claimable path → True** (C-5); raw-bytes vs text-mode hash divergence on a CRLF file (correction 19); the class matrix — the design's 20 rows WITH project identity and **rows 499/500 expecting `shop-infra` per correction 22**, plus the adversarial rows (correction 13) and the out-of-tree-only HOLD row (correction 12). ⚠️ ALL tests in tmp dirs/DBs — never a real watched path.

**A3 — verify before committing:** new tests green (paste raw); `py_compile` **all four files this step changes**; `pragma_table_info('clearances')` on a tmp-initialized DB shows the corrected DDL.

**A4 — commit** (worktree): `git add lifecycle.py depositor.py scripts/plan_lint.py gates.py tests/test_admission_flip.py && git commit -m "[<id>] admission flip A: clearance substrate, class split, lint+gates sweep (INERT until restart)"`

⚠️ **IF ANY A3 CHECK FAILS: no commit, no revert, no retry — leave the worktree as evidence, report, raise `### Flags for CEO`.**

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/depositor.py`
- `/Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py`
- `/Users/marklehn/Developer/GitHub/bellows/gates.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_admission_flip.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/depositor.py`
- `/Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py`
- `/Users/marklehn/Developer/GitHub/bellows/gates.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_admission_flip.py`

## STEP 2 — DEV-B: the claim path and the clear tool

**Role:** DEV. ⚠️ Builds ON Step 1's committed worktree state; re-verify its four files present before starting (their A4 commit is your baseline).

**B1 — implement the CLAIM-PATH rows AS CORRECTED:**
- `bellows.py`: `is_claimable(path, db_path)` beside an untouched `is_runnable_plan` — whole-body try, any exception → False (correction 6); gated at `_handle` entry (with the auto-HOLD `no_clearance` arm) and `collect_group` **passing `full_path`** (corrections 3/… — rescan/startup keep the bare listing filter, sites 2346/2702 byte-unchanged); the arm: **sidecar `.hold.json` BEFORE the rename** (correction 29), its own fail-toward-WARN try (correction 15), **CHECKS `_seen`, never ADDS** (corrections 16/28); **the claim-time re-check in `run_plan`**: one `read_bytes`, hash those bytes, decode the same bytes as `plan_text`, require an unconsumed clearance immediately before `mint_and_claim` (corrections 10/26); **`consumed_at` stamped inside `mint_and_claim`'s BEGIN IMMEDIATE transaction, before the in-progress rename** (correction 24). **New MUST-PRESERVE honored: startup recovery stays ordered before any startup scan — assert it by reading main()'s order, change nothing there.**
- `tools/clear_plan.py`: D-5(b) re-entry — preconditions (hold- prefix, .md, sidecar exists), rename `hold-` → `ready-`, async outcome message.

**B2 — targeted tests (same test file, claim half):** gate truth table (no row / cleared / drift / consumed / three unreadable-DB shapes → False without exception); the replay pair (other-path copy refuses; post-consumption same-path refuses; fresh re-clear after transient death SUCCEEDS under the partial index); the arm — **at most one EFFECTIVE hold-rename per slug, repeat attempts logged safe no-ops, never adds to `_seen`** (C-3's corrected form), exception-safety (vanished source; read-only dir), mid-claim skip (arm sees `_seen` slug and skips); **collect_group: a mixed group dispatches its claimable members and holds the unclearable one visibly; and the full_path regression pin — `is_claimable` receives a path that resolves** (C-11); clear-tool preconditions + rename target.

**B3 — verify:** tests green (paste raw); `py_compile` both files this step changes.

**B4 — commit:** `git add bellows.py tools/clear_plan.py tests/test_admission_flip.py && git commit -m "[<id>] admission flip B: is_claimable gates, auto-HOLD arm, claim re-check + consume, clear tool (INERT until restart)"`

⚠️ Same failure disposition as Step 1.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_admission_flip.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_admission_flip.py`

## STEP 3 — QA

**Role:** QA. ⚠️ Fresh agent: re-measure; the DEV reports are not evidence.

**Q1 — full suite.** `python3 -m pytest tests/ -q`; deposit RAW output as `pytest_full.txt`. Baseline **1231 collected, green, known_failures 0**; the count grows by the new file; assert zero failures/errors, report the total. The hot-path-guard lesson applies: `is_claimable` is a new boolean gate on the dispatch path — name and diagnose every failure before classification.
**Q2 — change-set vs the gap table AS CORRECTED (C-2):** every row-as-corrected present at its site; **rows 11/12/16 verifiably ABSENT — `git diff` scoped to the 2346/2702 filter regions and to `status.py` is EMPTY; rows 17–19 satisfied by `tests/test_admission_flip.py`**; `is_runnable_plan` and the 2220/2622 enumerate sites byte-unchanged.
**Q3 — behavioral spot-probes on tmp environments:** the correction-25 end-to-end; the replay pair; byte-drift; the crash-order probe (kill between mint and rename in a harness → `recover_half_claimed` completes, no unconsumed window); the 20+adversarial class matrix.
**Q4 — the INERT claim, correctly scoped (correction 21):** live daemon PID via **process start time (`ps -o lstart=`) compared against this plan's claim timestamp in the live lifecycle DB — start-before-claim proves the same process** (C-15); live lifecycle.db has NO clearances table; AND the subprocess exception stated: `plan_lint.py` activates for the old daemon at merge (additive WARN-set change). Activation of everything else is post-close (restart + the D-6 canary).

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1–Q4 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Commit:** `git add knowledge/research/e2-qa-2026-08-24.md knowledge/research/pytest_full.txt && git commit -m "[<id>] qa: admission flip — full suite + evidence"`

## Deposit ritual (correction 9 + capstone C-10)

Stage as `ready-executable-eluvian-e2-admission-flip.md` with the fold-check sidecar copied beside it under both the ready- and post-clear names. **Expected depositor outcome under the LIVE (old) code: HOLD `class:governed-tooling` — by construction, not a failure.** Release: manual `hold-` → bare rename by the Planner — **the final sanctioned use of bypass (b), retired by this very plan at activation.**
