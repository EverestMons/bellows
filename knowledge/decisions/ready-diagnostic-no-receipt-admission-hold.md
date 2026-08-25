# bellows — diagnostic: the `no_receipt` admission hold (R-F3) — matching predicate, grandfathering, arm placement, the [2r] residual

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** ruling R-F3 (`governance/knowledge/research/eluvian-follow-up-rulings-2026-08-25.md`): receipts become STRUCTURAL at admission — a deposit with no matching active receipt auto-HOLDs like `no_clearance`, released by the same clear tool. The ruling names four questions this diagnostic must settle before the executable: the matching predicate, grandfathering, arm interaction, and the wrap-time `[2r]` check's residual role.

## Why this exists

Today a receipt-less deposit sails through admission and surfaces (at most) as a wrap-time warning in whatever session happens to wrap — detection, not enforcement, and only for wrapping sessions. The E2 precedent is exact: the filename carried no authority until the clearance record did; the receipt should gain authority the same way, at the same gate. But the mechanics are not free: the ruling's own scouting found that **"depositor-side" is a misnomer in code terms** — the `no_clearance` hold arm lives in bellows.py's scan path, not depositor.py, and depositor.py has zero receipt awareness today. The executable needs the real map.

## What this plan does NOT do

- **It writes NO code.** One research deposit with a Rule 27 gap table.
- **It does not re-open R-F3.** The HOLD is ruled; this settles HOW, and any genuinely new fork lands in D-7.
- **It does not touch receipts, holds, or the DB** — reads only (`mode=ro`).

## Numbers discipline

⚠️ **Measured 2026-08-25 by the Planner against bellows main post-525 (daemon PID 80340); RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| N1 | the no_clearance precedent sites | bellows.py:2301 and :2337 — TWO hold-writing sites (`"hold_reason": "no_clearance"`), NOT in depositor.py | `/usr/bin/grep -n -F "no_clearance" bellows.py depositor.py` → depositor.py zero hits |
| N2 | depositor receipt-awareness today | **ZERO** — `/usr/bin/grep -c -iF "receipt" depositor.py` → 0 (⚠️ a zero-match `/usr/bin/grep` EXITS 1 like the shim — never &&-chain a zero-count probe) | positive control measured: same grep on hooks/eluvian/wrap_check.py → 40 |
| N3 | the receipt's fields | slug, content_hash (full sha256), session_id, armed_at, watcher, attestation_boundary | read any `receipts/archived/receipt-*.json`; the attestation boundary is EXPLICIT: armed-at-write-time, not liveness |
| N4 | the ritual's byte-identity | receipt taken against DRAFT bytes BEFORE the ready- rename; the rename moves, never edits — receipt.content_hash equals the deposit's admission-time hash WHEN the ritual was followed | the E3 design (`Done/diagnostic-515.md` era) + `tools/deposit_receipt.py`'s hashing; the clearance system already hashes raw bytes at admission — cite the shared hash site |
| N5 | active-vs-archived semantics | active `receipts/` = deposits not yet closed; `receipts/archived/` = retired at plan close by `_retire_receipts` | ls both dirs; the 517/518 pre-restart residue (2 active, stale) is the measured grandfathering-adjacent case |
| N6 | the release path | `tools/clear_plan.py` arms: `clear_plan()` (rename-to-ready re-entry) + `release_class_hold()` (re-runs cycle_check + plan_lint, writes clearance `cleared_by='clear_tool'`) | read :62-135; the question is which arm (or a third) releases a `no_receipt` hold |
| N7 | the [2r] wrap check | wrap_check.py:209-215 `_check_receipts(session_id, fails)`; RECEIPTS constant :46 | its blocking arm is own-session-only; its warning arm is global 24h |
| N8 | the hold sidecar shape | `{"hold_reason": ..., "held_at": ...}` (+ `class_assigned` for class holds); `_hold(path, reason, details)` at depositor.py:554 is generic — a new reason is a string, not a schema change | read depositor.py:554-590 and a live-written hold JSON from today (13:48:23) |

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. DB via `mode=ro` only; never touch `receipts/`, holds, or `knowledge/decisions/` beyond your own deposit.
- ⚠️ **THE GREP SHIM IS BROKEN on this machine (every invocation errors `unknown option '-G'`, including `-F` forms). Use `/usr/bin/grep` for ALL probes. An errored probe is the shim, not an absence.**
- ⚠️ **THE SPLIT-PATH LAW:** your dispatch worktree contains only TRACKED files — `receipts/` IS tracked (probe it), but `lifecycle.db` and `logs/` are NOT; every untracked-target read uses the absolute live-checkout path under `/Users/marklehn/Developer/GitHub/bellows/`.
- ⚠️ **Every claim cites file:line in CURRENT code; every absence claim carries a positive control. EVERY DATE IS A FIXED LITERAL. Worktree dispatch; deposit path project-relative.**

## STEP 1 — DIAGNOSTIC: map the admission path, settle the four questions

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/no-receipt-admission-hold-design-2026-08-25.md` (project-relative in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the real admission map.** Trace a deposit from file-appearance to claim: where the scan sees it, where `_seen` gates re-processing, where the two N1 hold sites fire, what the depositor's `_clear`/`_assign_class` contribute, and where `is_claimable` re-checks at claim. Deliverable: the ordered pipeline with file:line per stage, and the EXACT stage where a `no_receipt` check belongs — stated with the reasoning (before/after class assignment? before/after the clearance check? the answer determines whether a receipt-less deposit shows `no_receipt` or `no_clearance` first, and double-hold behavior must be specified: can one deposit carry two hold sidecars, or does first-reason-wins apply — read the sidecar-before-rename mechanics from N8 and say which the code does today).

**D-2 — the matching predicate.** From N3/N4: the admission check reads the deposit's raw bytes, hashes them, and looks for an ACTIVE receipt whose `content_hash` matches (and whose `slug` matches the deposit's placeholder-derived slug — state whether hash-only suffices or slug+hash is required, and what each choice costs: hash-only tolerates renames; slug+hash catches a receipt reused for a different artifact with identical bytes — is that case real?). Settle the drift arms: (a) post-receipt edit (hash mismatch → hold, correct — the receipt attests THE BYTES); (b) receipt present but ARCHIVED (N5 — a re-deposit of a closed plan's artifact: hold or pass? the retirement semantics decide); (c) multiple active receipts for one slug (re-receipted after a fix: newest-wins or any-match — say which and why); (d) the hold-release-re-entry loop: after a `no_receipt` hold, the operator writes a receipt and re-releases — trace that the release path re-evaluates receipt presence (or specify where it must).

**D-3 — grandfathering.** The measured population: probe every file currently in the watched decisions/ dirs (all 10 projects — ⚠️ these live OUTSIDE your bellows worktree entirely; use absolute paths `/Users/marklehn/Developer/GitHub/<project>/knowledge/decisions/` per the split-path law's spirit) for deposit-shaped names; count which would hold under the new arm (expected: zero pending deposits today — verify, the queue is empty); then the REAL grandfather cases: (i) a legacy plan re-deposited from Done/ for a corrective re-run (pre-E3 artifact, no receipt ever existed); (ii) the 517/518 stale active receipts (N5) — do they satisfy or confuse the predicate for any future same-slug deposit; (iii) a hand-authored emergency deposit in a daemon-down scenario (the manual lane). For each: hold-and-release (the deliberate act, R-F3's spirit) vs exempt-by-rule (state the exemption's abuse surface). Recommend one posture; the E2 precedent (grandfather+gated-clear) is the prior.

**D-4 — arm placement and interaction.** Given D-1's map: does the `no_receipt` check land beside the N1 sites in bellows.py's scan (mirroring no_clearance exactly), inside depositor.py's clear path (making the depositor genuinely receipt-aware, N2), or at `is_claimable` (claim-time only)? State the failure modes of each (a scan-side arm fires once with `_seen`; a claim-time arm fires late, after class release acts). Then the release: which clear_plan arm handles `no_receipt` (N6) — the ruling says "released by the same clear tool"; specify whether `release_class_hold`'s re-checks extend (cycle_check + plan_lint + NOW receipt-presence) or whether the re-entry loop (D-2d) suffices. And the [2r] residual (N7): with admission enforcing, the wrap check's blocking arm becomes redundant-by-construction for daemon-lane deposits — recommend keep-as-defense-in-depth vs retire-to-warning-only, with the manual-lane (daemon-down) case weighed.

**D-5 — test surface.** The executable's tests: receipt-present passes admission; receipt-absent holds with the `no_receipt` sidecar; hash-mismatch holds; archived-receipt case per D-2b; grandfather posture per D-3; release-re-entry re-evaluates; no_clearance+no_receipt double-condition ordering per D-1; `_seen` non-re-fire; the [2r] posture change if any. Regression floor: current suite count, re-derived (`--collect-only -q`).

**D-6 — the executable's shape.** Small or split? (The arm + tests is one plan; a [2r] posture change could ride or split.) Name the change sites as the Rule 27 gap table.

**D-7 — open questions.** Anything needing a NEW ruling beyond R-F3's letter — LISTED, never decided silently. (Candidates from authoring: the D-2 slug+hash choice if genuinely contested; the D-3 exemption if hold-and-release proves too costly for the manual lane.)

**Post-conditions:** D-1 through D-6 each with ≥1 file:line citation; D-7 present, exempt exactly when truthfully empty; the N1-N8 pins each re-derived or explicitly superseded with the measurement shown; the Rule 27 gap table enumerates every change site.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/no-receipt-admission-hold-design-2026-08-25.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/no-receipt-admission-hold-design-2026-08-25.md`

**Commit:** `git add knowledge/research/no-receipt-admission-hold-design-2026-08-25.md && git commit -m "[<id>] diag: no_receipt admission hold (R-F3) — admission map, matching predicate, grandfathering, arm placement"` in YOUR worktree cwd. `<id>` from your plan filename.

## Drafting Cycle
**Tier:** T1 computed — read-only single-deposit diagnostic.
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-no-receipt-hold.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** — five lenses each, sequential; walk 1 folded 2 (the cross-project absolute-path law; N2's zero-count exit-1 warning), walk 2 dry across all five lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry
**Cold panel: NOT convened, decided with reasoning** — the E-family rule; read-only diagnostics 515/517/519/521/522 all closed on warm walks.
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the lintmirror deposit path.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **2 → 0**. The deposit travels the lane with the receipt ritual → predicted depositor AUTO-CLEAR (class read-only) → claim.

## Cycle Manifest
tier: T1
target: knowledge/research/no-receipt-admission-hold-design-2026-08-25.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/depositor.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-follow-up-rulings-2026-08-25.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/diagnostic-515.md
writes: knowledge/research/no-receipt-admission-hold-design-2026-08-25.md
open_forks: none authored here — genuinely new forks land in D-7
walks: 2
yields: 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

This step is DIAGNOSTIC-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
