# bellows — E2 design: the admission flip — clearance record, claim-path check, class split, gated clear, migration, activation

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only design; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md` §E2 (509-corrected) and `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md` (R1; fork 2 = grandfather + gated clear; fork 4 = `app-feature` + `register-writing` auto-clear, `shop-infra` HELD) — both consumed T-7 without re-derivation. **Structural precedent, cited because it is the SAME build class run through the SAME two-step shape:** `diagnostic-478` (depositor design) → `executable-481` (build, full cold panel, 5 majors caught). E2's executable builds from THIS plan's deposit the way 481 built from 478's.

## Why this exists

R1 — *"bellows only accepting a drafting cycle cleared plan — this is the only way that bellows can work on something"* — is ratified but unbuilt: `is_runnable_plan` admits any hand-named `executable-/diagnostic-/qa-*.md`, and the depositor's `_clear()` rename leaves a cleared file byte-identical in NAME to a hand-named one, so no filename convention can carry clearance. The audit graded this bypass (a); the flip closes it. **The claim path is the single most sensitive code path in the shop; this diagnostic settles every design question against the real code so the executable inherits decisions, not open questions.**

## What this plan does NOT do

- **It writes NO code.** One research deposit: the design document with a Rule 27 gap table (file:line per decision), exactly the 478 pattern.
- **It does not re-open the rulings.** Fork 2 and fork 4 are decided; the design implements them.
- **It does not restart the daemon or touch any live state.**

## Numbers discipline

⚠️ **Measured 2026-08-24 by the Planner; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| G1 | **`K`** — `is_runnable_plan` call sites (excl. its def) | **6** | `grep -n is_runnable_plan bellows/*.py bellows/scripts/*.py` → bellows.py:2053 (collect_group), :2065 (_handle entry), :2220 (idle-notify pending scan), :2346 (DISC-1 rescan), :2622 (orphan-verdict active-slug scan), :2702 (startup scan). ⚠️ **Classify each: which DISPATCH (must gate on clearance) vs which merely ENUMERATE (must not double-hold)** — the Planner's read: :2065/:2346/:2702/:2053 lead to dispatch; :2220 and :2622 are reporting/reconciliation and must keep seeing held plans correctly |
| G2 | `_clear()` rename leaves no mark | **confirmed** | depositor.py:496-514 — `claimable_name = filename[len("ready-"):]`; the audit's out-of-band constraint follows |
| G3 | depositor runs IN the daemon process | **True** | bellows.py:2186 `self.depositor = depositor.Depositor(...)` — so a clearance write shares the daemon's process and its lifecycle-DB access model |
| G4 | lifecycle.db has NO clearance-shaped table | **True** | `deposits(id, step_id, declared_path, type, landed)` is per-step; `ledger_writes(id, step_id, ledger_file, content_hash, applied_at)` is ledger-append provenance. Neither keys a PLAN's content hash to a clearance event; a new table or a sidecar file is required |
| G5 | bare claimable-named files in ALL 10 watched dirs today | **0** | per-dir scan; migration therefore has an EMPTY hot set, and fork 2's grandfather covers the cold set (halted- 4, hold- 0 currently) |
| G6 | the unknown-prefix WARN arm | bellows.py:2073-2077 | `_handle` already warns-and-ignores unrecognized .md prefixes ONCE per slug via `_seen` — the auto-HOLD for unclearable claimables can mirror this arm's shape |
| G7 | `_assign_class` split point | depositor.py:255-278 | the catch-all `return "governed-tooling"` at :278 is where `app-feature` vs `shop-infra` must be positively decided (fork 4); the audit's corrected R3 section names the intended memberships |

## Drafting Cycle
**Tier:** T1 computed — T-7 fires twice over (consumes audit+rulings; feeds the executable). T-2/T-5/T-6 do not fire (read-only).
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-eluvian-e2-design.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk; walk 1 folded 4 (with the anchor-from-memory incident caught by the exit-gated sweep), walk 2 dry across all lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged: walk 1 sharpened D-4/D-5/D-6 and surfaced the N/A tension for explicit resolution; no premise failed, no ruling was touched, and the two-step 478→481 shape stands. None of the forcing classes fires.
- Weak spots:          w1 2 folded — instruction 2 / record 0 (clear-tool entry shape; the N/A tension); w2 dry
- Destruction:         w1 1 folded — instruction 1 / record 0 (rule-based shop-infra membership); w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0 (safe-if-dispatched canary); w2 dry
- Integration-record:  w1 dry; w2 dry
- ACID:                w1 dry (sweep exit-gated; first fold script aborted on an anchor-from-memory and the sweep caught the unlanded folds — see the register's walk-1 process note); w2 dry
**Cold panel:** owed — decided at the freeze with reasoning (the EXECUTABLE, not this read-only design, is where the audit mandates the full panel).
**Conformance (§5):** per lens; recorded at the **walk-2 close** (the phase label is the LAST run): plan_lint exit 0 / 0 FAIL; register CONFORMANT (STDERR); propagation exit 0; fold_check exit 0 against the walk-1 baseline.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **4 → 0**. No restructuring fold. Closing-record re-read swept the Walks line at this close; the cold-panel decision stays where the audit put it — on the EXECUTABLE. ⚠️ The cycle is CLOSED; the deposit travels the lane: ready- staging → depositor gates → auto-clear (read-only) → daemon claim.

## Cycle Manifest
tier: T1
target: knowledge/research/e2-admission-flip-design-2026-08-24.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/depositor.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: knowledge/research/e2-admission-flip-design-2026-08-24.md
open_forks: none authored here — the design implements ruled forks; anything it cannot settle without a NEW ruling is listed in its §Open questions for the CEO rather than decided silently
walks: 2
yields: 4, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
N/A

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. `lifecycle.db` is opened `immutable=1` or via `sqlite3 "file:...?mode=ro"` — the daemon is its sole writer.
- ⚠️ **Every design decision cites file:line in CURRENT code**, and every claim of absence carries a positive control (same instrument finding a known-present thing).
- ⚠️ **The safety invariant is inherited from 478 and restated:** the depositor never mints, never dispatches — and the flip must not change that. The claim decision stays the daemon's; clearance only NARROWS what it may claim.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.**
- **`grep` is ugrep: `-F` for literals**; read printed counts, never exit status.
- ⚠️ **This plan dispatches into a WORKTREE** (bellows has its own .git). The deposit path in the manifest is project-relative; write it under YOUR cwd and commit it there — the teardown merge lands it.

## STEP 1 — DIAGNOSTIC: settle the design, emit the document

**Role:** DIAGNOSTIC.

Produce `/…/bellows/knowledge/research/e2-admission-flip-design-2026-08-24.md` (project-relative `knowledge/research/e2-admission-flip-design-2026-08-24.md` in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the clearance record.** Decide its form and defend it against the alternatives: (a) a new `clearances` table in lifecycle.db (`content_hash`, `plan_path`, `cleared_at`, `cleared_by` = depositor|clear_tool, `class_assigned`) written by the depositor at `_clear()` time — in-process per G3, so the sole-writer model holds; vs (b) a sidecar receipt file. ⚠️ Whatever wins must satisfy: keyed by **content sha256** (a post-clearance byte change invalidates clearance BY CONSTRUCTION — state this as a feature and its interaction with claim-time pristine snapshots); survives daemon restart; readable by the claim path in-process with no new IPC; auditable by `status.py`.
**D-2 — the claim-path check.** Specify `is_claimable(path)` (name-pattern AND clearance-lookup) and, per G1's classification, EXACTLY which of the six call sites route through it versus keep the bare name check — with the failure mode of each wrong choice stated (a dispatch site left ungated re-opens bypass (a); an enumeration site gated wrongly makes held plans invisible to idle-notify/orphan reconciliation).
**D-3 — the auto-HOLD arm.** An unclearable claimable-named file is renamed `hold-<name>` + `.hold.json` `{"hold_reason":"no_clearance"}` mirroring G6's once-per-slug discipline — specify where in `_handle` this lands and how DISC-1/startup rescans avoid re-processing.
**D-4 — the class split (fork 4).** Concrete `_assign_class` replacement at G7: positive detection for `shop-infra` defined by RULE, not hand list — a hand list is invisible-when-incomplete and rots (ELUVIAN_PATH.md joined the doctrine set THIS WEEK): e.g. *any write under `bellows/`, `forge/`, `lessons-forge/`, `anvil/` outside their `knowledge/` trees, OR any write directly at the governance root's top level, which is where every doctrine file lives*. The design states the rule, shows the membership it induces today, and **force-classifies the last 20 closed plans' write sets against it as the acceptance table**, `register-writing` (existing patterns), `app-feature` (writes inside a watched project tree not matching the above), `read-only` (existing). ⚠️ **Force-classify: no catch-all may remain** — an unmatchable write set HOLDs as `unassignable_class`, which already exists. Auto-clear policy per the ruling: read-only + app-feature + register-writing on full-pass; shop-infra HELD. ⚠️ **Resolve the N/A tension explicitly, in writing:** the rulings' additional-verification line wishes *substrate asserts never N/A*, but residual (ii) (re-verified at 509: cycle_check.py:257-260) makes a governance-hosted register return N/A from the plan's own repo by construction — never-N/A would bar every cross-repo-registered plan from auto-clear. The design either (i) scopes auto-clear to in-project-register plans (N/A → HOLD; stated cost: every governance-registered cycle stays held), or (ii) accepts N/A for the register assert alone with the direct substrate checks (walk_register_lint, per-walk commits, fold baseline) named as the compensating gate — whichever it picks is written as a rule with the other option's cost stated, or escalated to D-8 if it is genuinely a new ruling.
**D-5 — the gated clear tool.** `bellows/tools/clear_plan.py <hold-file>`. Manual rename becomes INERT (no clearance → auto-HOLD at claim). Weigh BOTH entry shapes and pick with reasons: **(a) in-tool evaluation** — the tool re-runs depositor logic itself, which duplicates the evaluator in a second process and creates the locking question (the depositor's lock? a flock? `_shutting_down`?); **(b) rename-to-ready RE-ENTRY** — the tool validates preconditions and renames `hold-` → `ready-`, and the LIVE daemon's own watchdog/depositor re-evaluates: one evaluator, no second-process locks, full-pass → clearance+clear, fail → re-hold with the fresh reason, all through code paths that already exist. ⚠️ The Planner's read is that (b) dissolves (a)'s hardest questions, but the design must check (b)'s own edges: the DISC-2 ready-rescan cadence, and what the tool reports to its caller when the outcome is asynchronous.
**D-6 — migration + activation (fork 2).** Grandfather: existing `halted-`/`parked-`/`hold-` files untouched (G5: the hot set is empty today). Activation is a DAEMON RESTART, a deliberate step; specify the post-restart **live canary**, both arms: (i) a hand-named dummy claimable in a scratch-safe watched dir → observe auto-HOLD `no_clearance` — ⚠️ **the dummy must be SAFE-IF-DISPATCHED, because the canary exists to catch a broken flip and a broken flip DISPATCHES it**: read-only class, no-op body, `auto_close: true`, writes nothing; (ii) a `ready-`-staged read-only dummy → observe clear + claim; and the cleanup of both, including the lifecycle rows either arm creates. State the rollback: `git revert` + restart.
**D-7 — test plan.** Unit surface for `is_claimable`, the class split (force-classification table), clearance write/read round-trip, the auto-HOLD arm, the clear tool's re-evaluation; plus which existing tests (the 481 suite) must still pass unchanged.
**D-8 — open questions.** Anything requiring a NEW CEO ruling is LISTED, never decided silently.

**Post-conditions:** every D-section present with ≥1 file:line citation; G1's six call sites all classified with each wrong-choice failure mode; the R1 sentence quoted once verbatim; a Rule 27 gap table enumerating every code change site the executable will touch.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-admission-flip-design-2026-08-24.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-admission-flip-design-2026-08-24.md`

**Commit:** `git add knowledge/research/e2-admission-flip-design-2026-08-24.md && git commit -m "[<id>] design: E2 admission flip — clearance, claim gate, class split, clear tool, migration"` in YOUR worktree cwd. `<id>` from your plan filename.
