# Bellows — Daemon-restart state divergence covering BACKLOG items #2, #3, #5
**Date:** 2026-05-24 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Three open BACKLOG entries describe failures in distinct corners of the daemon's state machine but share a common signature: the daemon's in-memory step/pause/rename state diverges from on-disk filenames + verdict files, either because (a) a restart happened mid-transition or (b) the verdict semantics assume "step done" when the gate failure was actually "step never ran." This diagnostic characterizes the three failures together to determine whether they are surface manifestations of one underlying issue (e.g., the daemon performs filename transitions and verdict-request posting as separate non-atomic operations with no recovery on restart) or three independent bugs in adjacent code regions. The fix sequencing depends on the answer.

**Item #2 — Daemon-restart recovery shape (2026-05-23).** Plans in `in-progress-*` state with a verdict already in `resolved/` are not auto-matched after daemon restart. The matching predicate at `bellows.py:1199` (`pname.startswith("verdict-pending-") and plan_slug in pname`) requires the `verdict-pending-` prefix, but post-abnormal-termination plans may have the wrong prefix because the in-memory pause/rename state was lost. Bellows emits `[WARN] [<slug>] ⚠️ no verdict-pending plan found step N — leaving in resolved/ for retry` every 30s indefinitely. Recovery: Planner manual rename `in-progress-*` → `verdict-pending-*`, then verdict consumes on next scan.

**Item #3 — Step 2 final-step gate_failure pause rename-skip (2026-05-22).** Observed on `executable-pre-scan-orphan-guard-2026-05-22.md`: gate_failure surfaced verdict-request file correctly but plan filename stayed `in-progress-*` instead of being renamed to `verdict-pending-*`. The 2026-05-24 diagnostic (`bellows/knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md`) already partially characterized this — Section C/D found the rename IS structurally present at `bellows.py:618-620` and is symmetric with the intermediate-step gate_failure path. The diagnostic identified the root cause as **daemon restart between verdict-post (line 614) and rename (line 619)**, not a missing code path. Note that the 2026-05-24 diagnostic was scoped to the pre-scan loop investigation; the rename-skip companion conclusion is one section in a larger document. Today's diagnostic should validate that conclusion against item #2 and item #5, not re-derive it.

**Item #5 — Step-counter loop after precondition-failure verdict (2026-05-21).** When Bellows pauses on a precondition gate (worktree creation failure) labeled `step-N` and the Planner verdict-continues, Bellows re-dispatches step N rather than advancing to N+1 — BUT if step N's work was already shipped to origin from a prior run (the parallel-SHA pattern), the agent re-runs in a fresh worktree forked from origin tip, edits are no-ops, resulting commit is empty, teardown's cherry-pick fails empty, gate_failure, re-pause on the same step-N. Three iterations observed before Planner verdict: stop. The BACKLOG entry hypothesizes two root causes: (1) `_consume_verdicts` interprets continue-on-precondition-failure as "step N done, advance to N+1" without checking whether step N actually produced work; (2) step counter is computed from the verdict request's `Step` field rather than from internal daemon state.

## Reference prior art (read these to avoid re-deriving)

- `bellows/knowledge/research/step-state-persistence-map-2026-04-28.md` — 2026-04-28 SA findings on daemon state model (`bellows.db` schema, `extract_total_steps`, verdict consumer interaction). Foundation reading.
- `bellows/knowledge/decisions/Done/diagnostic-step-state-persistence-map-2026-04-28.md` — the 2026-04-28 diagnostic plan itself, for context on what was/wasn't scoped.
- `bellows/knowledge/decisions/Done/executable-step-state-resume-phase-3b-2026-04-28.md` — the implemented step-state-resume work that landed via Phase 3b.
- `bellows/knowledge/decisions/Done/diagnostic-in-progress-rename-verification-2026-05-10.md` and any deposited findings — verified rename behavior at the call-site level.
- `bellows/knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md` — TODAY'S diagnostic, especially Section C (in-progress-* → verdict-pending-* rename sites at `bellows.py:618-620`) and Section D (item #3 reproduction analysis). Do NOT re-derive what's in Section C; cite it.

Build on these. Do NOT repeat their findings; do extend them where today's three-item synthesis requires additional ground.

## Three questions to answer

**Q1 (joint state model):** What is the daemon's complete state-divergence model across these three failures? Specifically: at every transition where the daemon updates filename state, posts a verdict request, updates in-memory pause/step state, or writes to `bellows.db`, identify (a) the order of operations, (b) which operations are atomic with each other, (c) which gaps a restart can split, and (d) whether `bellows.db` step-state-resume (the 2026-04-28 Phase 3b implementation) covers the divergence or not. The goal is a single unified picture: "the daemon's state model has N atomic boundaries; restart between any boundary M and M+1 produces failure mode X." Items #2, #3, #5 should slot into this picture as specific (M, M+1) boundary failures, OR as distinct issue classes if the model shows they're independent.

**Q2 (item-by-item characterization):**
- For **item #2**: trace the exact code path from "Planner deposits verdict response in `resolved/`" through `_consume_verdicts` matching predicate at `bellows.py:1199`. What state must the daemon have lost to produce the no-match WARN? Is it specifically the `verdict-pending-` rename, or something else?
- For **item #3**: validate or refute the 2026-05-24 diagnostic Section C conclusion (the rename IS present at bellows.py:618-620; the root cause is daemon restart between verdict-post and rename). Specifically: is the gap structurally identical to item #2 (both are "rename to verdict-pending-* lost across restart"), or are they distinct gaps?
- For **item #5**: trace the verdict consumer's step-advancement logic. When a verdict-continue arrives for a Pause Reason Code = gate_failure on a precondition gate (worktree_creation), does the daemon advance step N → N+1 or re-dispatch step N? Cite the exact code path and the predicate. Is the verdict request's `Step` field used as input, or is step number derived from internal daemon state?

**Q3 (joint root cause):** Are items #2, #3, #5 surface manifestations of one underlying issue, or three independent issues?
- If shared: name the shared code site or atomic-boundary gap, and propose fix sequencing that addresses the shared cause first.
- If independent: state explicitly with the three distinct code regions named, and recommend whether they can be fixed in parallel or whether one fix masks/worsens another.

---

## STEP 1 — Characterize the daemon-restart state divergence model

**Agent:** Bellows Systems Analyst
**Estimated tokens:** ~35k

### Read order

1. The four "reference prior art" files listed above (Section, "Reference prior art (read these to avoid re-deriving)"). Read in full. Anchor on what they already characterized. Do not re-derive.
2. `bellows/bellows.py` — full read with attention to: `run_plan()` (especially the gate_failure pause branches and the verdict-posting + rename sequence around bellows.py:580-625 region), `_consume_verdicts()` (especially the step-advancement and matching-predicate logic around bellows.py:1199), the watcher/scan loop, and any startup-state-recovery code.
3. `bellows/verdict.py` — any helpers called by `_consume_verdicts` for slug extraction, filename parsing, step extraction.
4. `bellows/gates.py` — the precondition-gate path (worktree_creation, etc.) and how it interacts with the pause/rename sequence.
5. `bellows/bellows.db` schema (via `sqlite3 bellows/bellows.db .schema`). Identify whether per-plan step state is persisted post-restart and what its recovery semantics are.
6. `bellows/knowledge/BACKLOG.md` — the three open entries (item #2 dated 2026-05-23, item #3 dated 2026-05-22, item #5 dated 2026-05-21). Read in full for the reproduction records.
7. Recent reproduction artifacts (if any survive):
   - For item #2: log evidence from 2026-05-23 morning (the stuck-state-color-override final closeout cited in the BACKLOG entry, logs 08:46–08:48).
   - For item #3: log evidence from 2026-05-22 on `executable-pre-scan-orphan-guard-2026-05-22.md` Step 2 around 09:13-09:21.
   - For item #5: log evidence from 2026-05-21 on `executable-fuel-continuation-inference-ui-2026-05-21` around 15:38-15:52.
8. `bellows/logs/terminal/bellows-2026-05-2*.log` — selective grep for the timestamps cited above. Do not dump full logs.

Do NOT read source files beyond what's listed above unless the call chain requires it.

### Investigation questions

For every claim, cite specific `bellows.py` / `verdict.py` / `gates.py` line + exact code snippet (no paraphrasing). Build on the 2026-04-28 and 2026-05-24 findings; do not re-derive their content.

**Section A — The daemon's state model (joint)**

1. Enumerate every state-modifying operation the daemon performs during a single step's lifecycle, in order. State-modifying means: filename rename (via `shutil.move`), verdict-request post (file write in `verdicts/pending/`), `bellows.db` write, in-memory dict/set update. For each, cite the file:line, and note whether the operation is atomic with the next one (single function call, single transaction) or has a gap that a restart could split.
2. From the operation list, identify every (op_M, op_M+1) pair where a restart between them would leave on-disk state inconsistent with post-restart-expected state. Call these "restart-vulnerable boundaries." Number them.
3. For each restart-vulnerable boundary, document: (a) what on-disk state survives the restart, (b) what in-memory state is lost, (c) what `bellows.db` state survives, (d) what observable symptom the post-restart daemon would produce.
4. Cross-reference items #2, #3, #5 against the restart-vulnerable boundaries from question 3. Does each item map to exactly one boundary, multiple boundaries, or a non-restart logic defect that doesn't fit the boundary model?

**Section B — Item #2 trace (daemon-restart recovery shape)**

5. Trace from "Planner deposits `verdict-{slug}-step-N.md` in `resolved/`" → `_consume_verdicts()` scans `resolved/` → match against plans in `decisions/`. Cite the matching predicate at bellows.py:1199 (`pname.startswith("verdict-pending-") and plan_slug in pname`). Why does this require the `verdict-pending-` prefix specifically? Could the predicate be widened to consider `in-progress-*` plans without breaking other behavior? Cite any uses of `verdict-pending-` prefix elsewhere in `bellows.py` that would be affected.
6. At what code site is the `in-progress-*` → `verdict-pending-*` rename performed on a normal (non-restart) gate_failure pause flow? Is it before or after the verdict request is posted? Is the rename atomic with the verdict-request post, or is there a gap a restart could split?
7. Is there startup-state recovery in `bellows.py` that scans `decisions/` for `in-progress-*` plans and pairs them with `resolved/` verdicts? If yes, cite the code and explain why it doesn't fire for item #2's reproductions. If no, confirm absence.
8. Validate against the 2026-05-23 reproduction in BACKLOG #2: at the moment the daemon restarted, what was the on-disk state of (a) the plan file's filename prefix, (b) the verdict file in `resolved/`, (c) the `bellows.db` rows for the plan? Does the restart-vulnerable boundary model from Section A explain this state?

**Section C — Item #3 trace (final-step gate_failure rename-skip)**

9. Build on the 2026-05-24 diagnostic Section C — cite its conclusion that the rename is structurally present at `bellows.py:618-620` and symmetric with the intermediate-step gate_failure path. Now extend: is the rename atomic with the verdict-request post that immediately precedes it, or is there a gap a restart could split? If a gap exists, cite the lines and the order.
10. Compare the item #3 gap (from Q9) to the item #2 gap (from Q6). Are they the same gap — i.e., "verdict-request posted, then rename performed, with restart-vulnerable space between"? Or are they distinct gaps?
11. Validate against the 2026-05-22 reproduction in BACKLOG #3: there's evidence of a daemon restart sometime between Step 2 pause (09:13:30) and the log dump (09:21:12). Can you find log evidence of the restart in `bellows/logs/terminal/bellows-2026-05-22.log`? If yes, confirm the restart fell between verdict-post and rename. If no, explain what alternative could have produced the rename-skip.

**Section D — Item #5 trace (step-counter loop after precondition-failure)**

12. In `_consume_verdicts`, locate the step-advancement logic. When a verdict-continue arrives for a plan that paused with Pause Reason Code = `gate_failure` on a precondition gate (e.g., worktree_creation), what does the daemon do? Cite the code path. Specifically: does it call `run_plan` with step = N (re-dispatch same step) or step = N+1 (advance)?
13. Where does the step number for the next dispatch come from? Cite the source: (a) parsed from verdict-request filename, (b) read from `bellows.db`, (c) read from plan filename, (d) read from in-memory state, (e) other. Does this source distinguish between "step N completed successfully" and "step N never ran due to precondition failure"?
14. Identify whether the BACKLOG #5 hypothesis (1) is correct: does `_consume_verdicts` interpret continue-on-precondition-failure identically to continue-on-success? Cite the predicate that makes this decision, or confirm absence (in which case the failure mode is something else).
15. Validate against the 2026-05-21 reproduction in BACKLOG #5: at the moment of the third teardown-empty loop iteration, what was the state of (a) the verdict request file's `Step` field, (b) `bellows.db`'s last-recorded step for the plan, (c) the plan filename? Trace the third re-dispatch step-by-step.

**Section E — Joint root cause analysis**

16. From Sections A-D, are items #2, #3, #5 surface manifestations of one underlying issue, or three independent issues?
   - **If shared (one underlying issue):** name the shared boundary or code site. Explain why all three items map to it.
   - **If independent:** state explicitly with the three distinct code regions named.
   - **If two-of-three shared and one independent:** name the shared pair and the independent item.
17. **Fix sequencing question:** based on Section E.16, recommend fix order with reasoning. Specifically address: does fixing item X first leave any of items Y/Z latent? Does fixing item X mask or worsen items Y/Z? Can any subset of items be fixed in parallel without interaction risk?

**Section F — Resolution options (read-only proposals, no implementation)**

18. For each item (or for the shared boundary, if Section E identifies one), list 2-3 concrete fix shapes. For each shape: 1-2 line LOC estimate, and explicit identification of which restart-vulnerable boundary it closes (or doesn't close). If a fix shape addresses only one of the three items, note which others remain open.
19. If a shared root cause exists, propose a unified fix and note which item-specific BACKLOG entries it incidentally closes.
20. **Test coverage gaps**: for each item, identify whether existing pytest tests would catch the failure mode if reintroduced after a fix. Name the relevant test files/functions or confirm absence.

### Out of scope

- Do NOT propose or implement fixes; this is characterization only.
- Do NOT modify `bellows.py`, `gates.py`, `verdict.py`, `bellows.db`, or any test file.
- Do NOT touch any verdict files in `bellows/verdicts/` (pending/, resolved/, or archived/).
- Do NOT investigate the teardown-push silent failure (BACKLOG #18 from today, 2026-05-24) — different problem family, separate diagnostic later.
- Do NOT investigate the gate-scoping bugs (BACKLOG items 6, 7 — rule_22(c) false positive and rule_20 wrong-file) — different problem family, separate diagnostic later.

### Deliverables

**Deposits:**
- `bellows/knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md`

The findings file MUST include:
- Section A — Daemon state model (questions 1-4) with the enumerated state-modifying operations and the restart-vulnerable boundary list
- Section B — Item #2 trace (questions 5-8) with code citations
- Section C — Item #3 trace (questions 9-11) with code citations, building on the 2026-05-24 diagnostic Section C
- Section D — Item #5 trace (questions 12-15) with code citations
- Section E — Joint root cause analysis (questions 16-17)
- Section F — Resolution options (questions 18-20)
- The standard SA Output Receipt block at the end

### STOP

Stop after Step 1. Do not author an executable. The Planner will read the findings, verify Rule 22, and decide on fix scope + sequencing.
