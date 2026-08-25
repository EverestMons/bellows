# bellows — diagnostic: the silent teardown-merge block + shared QA-evidence names — channel census, the lost precheck, the collision fix shape

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** the 520 salvage record (`shop_next_session.md` SESSION 65 block + the LESSONS.md heading `2026-08-25: A shared deposit FILENAME is a SEQUENTIAL collision`) and the E-family arc close. **The measured defect this characterizes:** executable-520's step-2 worktree teardown merge was refused by git (`Your local changes to the following files would be overwritten by merge: knowledge/research/pytest_full.txt`) and the daemon recorded that failure in exactly ONE consumable channel — the verdict-request file — with NO gate_events row, NO merge-time log line, and a pause that read like a normal QA checkpoint. The Gap-1b guard caught the stranded commits only at continue-consumption, two minutes later. The trigger was the SHARED evidence filename `knowledge/research/pytest_full.txt` that 516, 518, and 520 all declare — a sequential collision through the live tree.

## Why this exists

Two defects stack. **(1) Silence:** both verdict-pause teardown catch sites append the failure to an in-memory `gate_result` AFTER the step's gate rows were already persisted, and neither logs — the failure is invisible in the lifecycle DB and the terminal log, the two places a Planner looks first. **(2) The collision:** every recent QA step deposits raw suite output under the same flat name, so any dirty or divergent state on that ONE path in the live tree blocks every subsequent plan's teardown — and the older per-plan convention (`knowledge/qa/evidence/<slug>/`) shows the flat name is authoring drift, not the historical norm. A third thread ties them: a dirty-tree precheck for exactly this failure mode SHIPPED in May (`worktree_teardown_dirty_tree` gate) and was dropped by the June merge-model rewrite. This diagnostic maps all three so a follow-up executable can ship recording + precheck + per-plan names without re-deriving anything.

## What this plan does NOT do

- **It writes NO code.** One research deposit with a Rule 27 gap table.
- **It does not re-litigate the 520 salvage.** The manual R2 recovery is done and correct; 520 is CLOSED. This characterizes the mechanism, not the incident response.
- **It does not pick the CEO's fork.** Where the fix shape needs a ruling (evidence-name keying, override posture on teardown rows), the options land in D-7 with costs, never decided silently.

## Numbers discipline

⚠️ **Measured 2026-08-25 by the authoring session against bellows main `c2b72ec`, daemon PID 26078; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| P1 | the silent catch sites | bellows.py:1114-1116 (while-loop pause) and :1241-1243 (final-step pause) — `except WorktreeTeardownError` appends `{"gate": "worktree_teardown", ...}` to `gate_result["failures"]`, sets `_pause_reason = "gate_failure"`, and calls NO `_log` | contrast :1272-1274 (auto-close arm DOES `_log("ERROR", ...)`) and :766-768 (park arm logs WARN and fully swallows — no record anywhere) |
| P2 | the sequencing defect | `lifecycle.record_gate_events` at :1210 runs at step end, BEFORE the final-step teardown at :1238 — a pause-path teardown failure can never gain a gate_events row | measured on 520: step_id 921 (step 2) holds 7 all-pass rows, zero `worktree_teardown` rows, while verdicts row 910 carries `pause_reason_code=gate_failure` |
| P3 | 520's actual refusal | `verdicts/ledger.jsonl` 2026-08-25T08:56:34 entry: `merge conflict on bellows-wt/520 … Your local changes … would be overwritten by merge: knowledge/research/pytest_full.txt` | terminal log `logs/terminal/bellows-2026-08-25.log`: gates pass 08:54:24 → PAUSE 08:54:25 → REJECTED 08:56:34 — no merge-time line between |
| P4 | the shared filename | 516, 518, 520 ALL declare `knowledge/research/pytest_full.txt` in Deposits/Scope | `grep -n -F "pytest_full" knowledge/decisions/Done/executable-{516,518,520}.md`; `git log --oneline -- knowledge/research/pytest_full.txt` → d1b99c6 [520], 87a08d7 [518], b379311 [516] rewriting one path |
| P5 | the historical norm | 50+ per-plan evidence dirs `knowledge/qa/evidence/<slug>/pytest_full.txt`; plus the suffixed one-off `knowledge/research/pytest_full_513_red.txt` | `find knowledge/qa/evidence -name "pytest_full*.txt" -print` and count the lines; positive control for the flat name: `ls knowledge/research/pytest_full.txt` |
| P6 | the lost guard | precheck shipped as 6252f8c7 (`worktree_teardown_dirty_tree` gate), extended 2153fc15 (Gap-1c re-attempt), REMOVED by 46505bcc (merge-ff model) | `git log --oneline -S "worktree_teardown_dirty_tree" -- bellows.py`; absence today: `grep -n -F "porcelain" bellows.py` → only the auto-stage site :1546/:1549, nothing in `_teardown_worktree` :1855-1990 |
| P7 | the guard that DID fire | the Gap-1b continue-block at bellows.py:2700-2707 rejected 520's continue and routed to halted- | `grep -n -F "uncleared" bellows.py`; characterize at execution WHICH channel it reads the prior failure from |
| P8 | the id-at-authoring constraint | plan ids are minted at claim (`minted id 520 — renamed to in-progress-…`), so an id-keyed evidence name cannot be authored into a plan; receipts key by SLUG for exactly this reason | `logs/terminal/bellows-2026-08-25.log` line 201; the receipts naming precedent in `tools/deposit_receipt.py` |

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. No code edits, no DB writes, no log truncation.
- ⚠️ **Every claim cites file:line in CURRENT code**; every absence claim carries a positive control.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **The lifecycle DB is opened read-only** (`sqlite3 "file:lifecycle.db?mode=ro"` or plain SELECTs only); the daemon is live on it.
- ⚠️ **THE SPLIT-PATH LAW (measured, W1-2):** your dispatch worktree contains only TRACKED files — `lifecycle.db`, `logs/`, and `verdicts/ledger.jsonl` are gitignored and ABSENT from it (`git check-ignore` matches all three). Every live-state read (the DB, the terminal log, the ledger, the resolved verdict files, the live tree's `knowledge/research/pytest_full.txt`) MUST use the absolute live-checkout path under `/Users/marklehn/Developer/GitHub/bellows/`. A relative probe against these targets returns a confident false absence. Only the deposit write (and its commit) is worktree-relative.
- ⚠️ **Worktree dispatch; deposit path project-relative.**

## STEP 1 — DIAGNOSTIC: census the channels, reconstruct 520, settle the fix shapes

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md` (project-relative in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the 520 reconstruction.** The full step-2 timeline across EVERY channel: terminal log lines (gates-pass 08:54:24, PAUSE 08:54:25, REJECTED 08:56:34), lifecycle DB rows (steps 920/921, gate_events for both, verdicts 909/910), `verdicts/ledger.jsonl`, the resolved verdict files, and git (d1b99c6's landing via the manual ff-merge; the daemon's own auto-stage commit cf4c694 on the worktree branch). For each channel state: did the teardown failure appear, when, and in what form. The deliverable is a channel-by-channel table proving the asymmetry P1-P3 pin — which channels a Planner reads first, and that those were exactly the silent ones. Also establish (from git evidence or state honestly as unrecoverable) WHY the live tree's `knowledge/research/pytest_full.txt` was locally modified at 08:54:25 — the proximate dirtier of the file.

**D-2 — the catch-site census.** All four `_teardown_worktree` call sites (:766 park, :1111 while-loop pause, :1238 final-step pause, :1269 auto-close) classified on four axes: logs at failure time? gains a gate_events row? reaches the verdict-request file? flips `gate_result["passed"]`? Include the sequencing fact (P2) that makes a pause-path gate row impossible as written. Then propose the recording fix shape for the executable: at minimum a `_log("ERROR", …)` at both pause-path catch sites (mirroring :1274) plus a post-hoc `lifecycle.record_gate_events`-compatible write so the teardown failure lands in the DB attached to the step it interrupted — state the exact call shape and where `_lc_step_id` is still in scope. State what the park path (:766-768) SHOULD do — its swallow predates the Gap-1b guard; a parked plan's teardown failure leaves no record at all.

**D-3 — the lost precheck.** Reconstruct what 6252f8c7's dirty-tree precheck checked (read the commit: `git show 6252f8c7 -- bellows.py`), what 2153fc15 added, and what 46505bcc kept vs dropped. State the merge-model equivalent: a `git status --porcelain` scoped check of the LIVE `project_path` tree run before the merge attempt in `_teardown_worktree`, its predicate, and its failure form (a `WorktreeTeardownError` whose evidence names the dirty files and the R2 recovery commands — the May diagnostic `Done/diagnostic-worktree-teardown-dirty-tree-precheck-v2-2026-05-27.md` already carries a CEO-approved pause-message design; cite and reuse its decisions rather than re-opening them, noting which are obsolete under the merge model).

**D-4 — the evidence-name collision.** The census (P4/P5): which plans declare the flat name, where the flat-name convention came from (grep the plan-authoring sources — `PLANNER_TEMPLATE.md`, recent Done/ plans, the E-family clone chain — and name the change site that stops the next clone inheriting it), and the fix-shape options with costs: **(a)** slug-keyed flat file `knowledge/research/pytest_full_<slug>.txt`; **(b)** the historical per-plan dir `knowledge/qa/evidence/<slug>/pytest_full.txt`; **(c)** id-keyed names — note P8 makes (c) unauthorable at plan-writing time unless the daemon rewrites paths at claim (a new mechanism; price it honestly). For each option state the interaction with: the `qa_test_result` gate's named-.txt scan (a bare evidence dir fails the gate on a green suite — the measured 2026-08 lesson), `deposit_exists` resolution, `scope_check`, and `_auto_stage_deposits`' path resolution (:1540-1568). Recommend one; the recommendation is D-7's first fork if the options genuinely trade off.

**D-5 — the E4/override interaction.** P7's Gap-1b guard fired at consumption; E4's conditioning reads gate_events and honors `overridden=1`. If D-2's fix lands teardown failures as real gate_events rows, state precisely what `clear_plan.py --override-gate` would then mean for a `worktree_teardown` row — an override asserts "this failure may be continued over," but a teardown failure means COMMITS ARE NOT LANDED, and continuing over it is exactly what Gap-1b exists to refuse. State whether the executable must exclude `worktree_teardown` from overridable gates (and where that exclusion lives), or whether an override plus the Gap-1b re-check compose safely as-is. Cite the E4 exclusion precedent (the teardown class was already excluded once — find it).

**D-6 — test surface.** Enumerate the follow-up executable's tests: the two pause-path catch sites log + record (fixture: a teardown raise injected at final-step pause), the park-path posture, the precheck arms (dirty live tree → precheck failure BEFORE merge attempt; clean tree → merge proceeds), evidence-name migration (whichever D-4 option, its gate interactions asserted), and the regression floor (current suite count, measured — the last known full-suite figure is 1363 passed from 520's QA; re-derive).

**D-7 — open questions.** Anything needing a CEO ruling: the evidence-name option if D-4's trade-off is genuine; the override posture on teardown rows if D-5 finds tension; anything NEW the census surfaces — LISTED, never decided silently.

**Post-conditions:** D-1 through D-6 each with ≥1 file:line citation; D-7 present, exempt exactly when truthfully empty; the P1-P8 pins each re-derived or explicitly superseded with the measurement shown; a Rule 27 gap table enumerating every change site the executable will touch.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md`

**Commit:** `git add knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md && git commit -m "[<id>] diag: teardown silent block + evidence names — channel census, lost precheck, collision fix shape"` in YOUR worktree cwd. `<id>` from your plan filename.

## Drafting Cycle
**Tier:** T1 computed — read-only single-deposit diagnostic.
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-teardown-silent-block.md`
**Walks:** walk 0 pinned; **walks 1–3 complete** — five lenses each, sequential; walk 1 folded 2 (incl. the HIGH untracked-live-state W1-2), walk 2 folded 2 (both record-accuracy), walk 3 dry across all five lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged: two instruction folds; no premise failed; the incident record binds.
- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry
- Destruction:         w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry
- Vulnerabilities:     w1 dry; w2 dry; w3 dry
- Integration-record:  w1 dry (close obligation tracked); w2 dry; w3 dry — cycle block finalized at close
- ACID:                w1 dry; w2 2 folded — instruction 2 / record 0; w3 dry
**Cold panel: NOT convened, decided with reasoning** — the E-family rule: panels earn their cost on builds (yields 46/33/31/20 all on executables); read-only diagnostics 515/517/519 each closed on warm walks alone.
**Conformance (§5):** recorded at the walk-3 close from actual runs: walk_register_lint CONFORMANT (STDOUT verdict channel, all 17 rows OK, branched-on); cycle_check re-run post-finalization (verdict channel, branched-on — the placeholder-manifest run returned CONTINUE and was treated as not-at-bar); plan_lint run at the lintmirror deposit path before the move.
**Closing:** **walk 3 met the bar — all five lenses dry.** Instruction series **2 → 2 → 0**. The cycle is CLOSED; the deposit travels the lane with the receipt ritual → predicted auto-clear (class read-only) → claim.

## Cycle Manifest
tier: T1
target: knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db, /Users/marklehn/Developer/GitHub/bellows/verdicts/ledger.jsonl, /Users/marklehn/Developer/GitHub/bellows/logs/terminal/bellows-2026-08-25.log, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/executable-516.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/executable-518.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/executable-520.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/diagnostic-worktree-teardown-dirty-tree-precheck-v2-2026-05-27.md, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md
writes: knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md
open_forks: none authored here — fix-shape forks land in D-7 for the CEO
walks: 3
yields: 2, 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

This step is DIAGNOSTIC-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
