# Step-State Resume Design — Phase 2 Architecture Document

**Date:** 2026-04-28 | **Phase:** 2 (Design) | **Agent:** Bellows Systems Analyst
**BACKLOG Item:** #5 — Step state does not persist across re-claims
**Prior Work:** `knowledge/research/step-state-persistence-map-2026-04-28.md` (Phase 1 diagnostic)

---

## Section 1 — Option Comparison Matrix

| Dimension | Option A: DB query in `run_plan()` | Option B: Watcher-side query in `PlanHandler._handle()` | Option C: Eliminate manual rename path |
|---|---|---|---|
| **Coverage** | Verdict-pending resume ✅, halted resume ✅, crash recovery ❌ (in-progress files never reach `run_plan`), plan edited between steps ⚠️ (trusts DB step number against potentially renumbered plan) | Verdict-pending resume ✅, halted resume ✅, crash recovery ❌ (same limitation — `is_runnable_plan` rejects `in-progress-` prefix), plan edited between steps ⚠️ (same trust issue) | Verdict-pending resume ✅ (via verdict system), halted resume ❌ (no path exists), crash recovery ❌, plan edited between steps N/A |
| **Code Cost** | ~20–25 LOC realistic (not 10). Includes: (1) new `_get_last_completed_step()` query function ~8 LOC, (2) slug derivation call in `run_plan()` ~3 LOC, (3) conditional resume logic ~5 LOC, (4) canonical slug column addition to `record_run()` schema + `ALTER TABLE` migration ~6 LOC. Files touched: `bellows.py` only. Schema change: yes — add `plan_slug TEXT` column to `runs`. | ~25–30 LOC. Same DB query function as A, but integration point is `_handle()` and `handle_new_plan()`. Requires `_handle()` to accept and pass `resume_step`, which then flows through `handle_new_plan()` → `_run_tracked()` → `run_plan()`. Files touched: `bellows.py` only. Schema change: same as A. | 0 LOC. Zero schema changes. CEO documents that resume is verdict-only. |
| **Procedural Cost** | None — transparent to CEO. Manual rename works as before but now resumes correctly. | None — same as A from CEO perspective. | High. CEO must never rename `verdict-pending-*` → `executable-*`. Must instead create a verdict file in `verdicts/resolved/`. Must never rename `halted-*` → `executable-*` (no supported path). Requires PLANNER_TEMPLATE documentation update. |
| **Failure Modes** | (1) Slug `LIKE` query matches wrong plan if slugs overlap. (2) DB reports step N complete but step N's deposits are missing/corrupt — silently skips to N+1. (3) Plan renumbered between steps — DB step N maps to wrong plan section. (4) Race: two threads both query before atomic `shutil.move` claim. | Same as A, plus: (5) coupling between watcher layer and DB adds a new dependency to the file-detection path — a DB corruption could block all plan dispatch. | (1) CEO accidentally renames file instead of creating verdict — Step 1 re-executes (current bug persists). (2) Halted plans have no resume path — must be re-created as new plans. (3) No automated safety net. |

### Code Cost Reassessment

Phase 1 stated Option A is "10 lines confined to `run_plan()`." This underestimates the real cost:

- **Slug derivation:** `run_plan()` receives `plan_path` with lifecycle prefix and `.md` extension. Deriving a canonical slug requires the same logic as `verdict.py:_slug_from_path()` (lines 65–75). Either import or duplicate ~5 LOC.
- **DB query:** The `plan_path` column stores full filesystem paths with `in-progress-` prefix at recording time (Phase 1 §3 sample rows). A slug-based `LIKE '%{slug}%'` query is fragile — slug `foo` matches `foo-bar`. This is Phase 1 unknown Q6.5. A reliable query requires either (a) adding a `plan_slug` column to `runs` (schema migration) or (b) accepting `LIKE` fragility.
- **Conditional logic:** Must only fire when `resume_step is None` AND a shadow cache exists (indicating prior claim). Must handle the case where DB returns no rows (fresh plan with stale shadow — unlikely but possible after manual shadow deletion).

Realistic LOC: 20–25 including the slug column migration.

---

## Section 2 — Q6 Unknown Handling Per Option

### U1: Plan edited between step N and re-claim (plan-hash drift)

| Option | Handling |
|---|---|
| A | **Partially addressed.** DB says "step N completed" but the plan text may now have different step boundaries. `extract_total_steps()` re-counts from current plan text, so `total_steps` is correct, but `resume_step=N+1` may point to the wrong content if steps were inserted/deleted before step N. **Mitigation within A:** compare `sha256(plan_text)` at claim time against the shadow cache hash. If mismatch and `resume_step > 1`, log a warning. The SA recommends warning-only, not halting — halting would require CEO intervention for every trivial plan edit (typo fixes, formatting). |
| B | Same as A — the DB query produces the same step number regardless of where it's invoked. |
| C | **Not applicable.** The verdict consumer always knows the exact step number from the verdict filename. Plan edits between steps are the CEO/Planner's responsibility. |

### U2: Prior step deposit verification

| Option | Handling |
|---|---|
| A | **Not addressed.** DB `status=Complete` is based on the agent's self-reported `receipt_status` (Phase 1 §3). Option A trusts this. Adding deposit verification would require Bellows to parse the step's deposit block and check file existence — this is Layer 3 logic (Planner judgment) per the SA guardrails. |
| B | Same as A. |
| C | **Partially addressed.** The verdict system routes through the Planner, which CAN verify deposits before issuing a `continue` verdict. This is the architecturally correct layer for deposit verification. |
| **Assessment** | **Option-independent.** Deposit verification belongs in the Planner (Layer 3), not Bellows (Layer 1). All three options leave this to the Planner. Follow-up plan: `executable-planner-deposit-verification` if the Planner doesn't already do this. |

### U3: Multiple verdict-pending for same plan (slug substring collision)

| Option | Handling |
|---|---|
| A | **Not addressed** — this is a `_consume_verdicts()` bug (line 667: `plan_slug in pname`), not a resume-path bug. |
| B | **Not addressed** — same. |
| C | **Not addressed** — same. |
| **Assessment** | **Option-independent.** The substring match at `bellows.py:667` is a latent bug in the verdict consumer. It should use exact match: `pname == f"verdict-pending-{plan_slug}.md"` or equivalent. Follow-up plan slug: `executable-verdict-slug-exact-match`. |

### U4: Orphaned in-progress files (crash recovery)

| Option | Handling |
|---|---|
| A | **Not addressed.** `is_runnable_plan()` (line 469–472) rejects `in-progress-*` prefix. The startup scan (lines 803–809) only processes `is_runnable_plan()` matches. An orphaned `in-progress-*` file remains invisible. |
| B | **Not addressed** — same gating at `is_runnable_plan()`. |
| C | **Not addressed** — same. |
| **Assessment** | **Option-independent.** Orphan recovery requires a separate mechanism: startup scan detects `in-progress-*` files with no active thread, renames them to `executable-*` (triggering re-claim with DB-based resume if Option A is shipped) or surfaces them via Pushover for CEO action. Follow-up plan slug: `executable-orphan-recovery-startup`. |

### U5: DB query slug ambiguity

| Option | Handling |
|---|---|
| A | **Directly affected.** The `plan_path` column stores full paths like `...in-progress-executable-deposits-block-regex-blank-line-2026-04-28.md`. A `LIKE '%{slug}%'` query where slug is `deposits-block-regex-blank-line-2026-04-28` could collide with a hypothetical plan slugged `deposits-block-regex-blank-line-2026-04-28-hotfix`. **Fix within A:** add a `plan_slug TEXT` column to `runs`, populated by `_slug_from_path()` at `record_run()` call sites. Query becomes `WHERE plan_slug = ? AND status = 'Complete'` — exact match, no ambiguity. Schema migration: `ALTER TABLE runs ADD COLUMN plan_slug TEXT`. Backfill is optional — new column is only used for new queries; old rows without it return NULL and are excluded. |
| B | Same fix needed — same DB query. |
| C | **Not applicable** — no DB query. |

### U6: Race condition on concurrent re-claim

| Option | Handling |
|---|---|
| A | **Partially addressed.** The `shutil.move()` at line 232 acts as an atomic claim — only one thread's move succeeds (the source file disappears for the second). The DB query at the start of `run_plan()` happens before the move, so two threads could both read `MAX(step)=N`. However, the second thread's `shutil.move()` fails (source gone), and `run_plan()` would hit an error. **Assessment:** the move-as-mutex is sufficient. The losing thread fails at the move, not at step dispatch. No explicit lock needed. The only edge case is if the move raises an exception that isn't caught — but `run_plan()` is wrapped in a try/except at line 196 that catches and logs. |
| B | Same — the DB query in `_handle()` would fire before the move in `run_plan()`, but the move still serializes actual dispatch. |
| C | **Not applicable** — the verdict consumer processes one verdict at a time in `_consume_verdicts()` (single-threaded loop). |

### U7: halted-vs-complete distinction

| Option | Handling |
|---|---|
| A | **Partially addressed.** The `runs` table records `status` as either `Complete` or `VerdictPending` (Phase 1 §3 sample rows). A halted plan's last DB row would be `VerdictPending` (the verdict consumer renames to `halted-*` at line 712–715 and does NOT write a new `runs` row). Query `WHERE status = 'Complete'` correctly returns the last COMPLETED step, not the halted step. If step N completed and step N+1 was halted mid-execution, DB has `Complete` for step N and no `Complete` for N+1 — resume at N+1 is correct. **Edge case:** if step N itself failed (agent crashed, receipt_status != Complete), the DB row for step N shows a non-Complete status. `MAX(step) WHERE status = 'Complete'` returns step N-1. Resume at N is correct — re-execute the failed step. This handles the halted-after-failure case correctly. |
| B | Same — same DB query logic. |
| C | **Not addressed.** A halted plan renamed to `executable-*` re-dispatches Step 1. The CEO must re-create the plan if they want to resume from a specific step. |

---

## Section 3 — Hybrid Options

### Hybrid 1: C-now + A-later (Procedural Bridge)

**Shape:** Ship Option C immediately (document that verdict-only resume is the supported path). Begin Phase 3 implementation of Option A in parallel. Once A ships, C's procedural restriction is relaxed — manual rename becomes safe again.

**Tradeoffs:**
- (+) Zero risk, zero code cost for immediate mitigation
- (+) Option A is designed and implemented without time pressure
- (+) CEO gets a working (if constrained) resume path today
- (-) Halted plans have no resume path until A ships
- (-) CEO must learn and follow the procedural discipline temporarily
- (-) If A implementation is delayed, the procedural restriction persists indefinitely

**Risk:** Low. The main risk is CEO forgetting the procedural constraint and renaming a file out of habit, triggering the Step 1 re-dispatch bug. Pushover notification on such events could mitigate this.

### Hybrid 2: A + orphan-recovery guard (DB Resume + Startup Scan)

**Shape:** Ship Option A for the `verdict-pending-*` → `executable-*` and `halted-*` → `executable-*` resume paths. Add a lightweight startup scan that detects `in-progress-*` files with no active thread and renames them to `executable-*`, triggering the Option A resume logic on the next rescan cycle.

**Tradeoffs:**
- (+) Covers all three resume scenarios: verdict-pending, halted, and crash recovery
- (+) Orphan recovery leverages Option A's DB query — no separate resume logic needed
- (+) Unified mental model: "rename to executable and Bellows figures out the step"
- (-) Higher code cost: Option A (20–25 LOC) + orphan scan (~15 LOC) + startup integration (~5 LOC) = ~40–45 LOC
- (-) Orphan recovery has its own edge cases: how long before an in-progress file is considered orphaned? (Thread may still be running but slow.) Requires either thread-registry checking or a timeout heuristic.
- (-) Scope creep risk: orphan recovery is a distinct BACKLOG item (U4) being bundled into the step-state fix

**Risk:** Medium. The orphan timeout heuristic is the main design risk — getting it wrong means either (a) recovering a file whose thread is still running (duplicate dispatch) or (b) leaving genuine orphans unrecovered. Thread-registry checking (querying `self._active_count` or a thread-name registry) is more reliable but couples the startup scan to the orchestrator's thread management.

### Hybrid 3: A + plan-hash warning (DB Resume + Drift Detection)

**Shape:** Ship Option A with a plan-hash check. At `run_plan()` claim time, if `resume_step > 1`, compute `sha256(plan_text)` and compare against the shadow cache content hash. If they differ, log a warning via Pushover ("Plan content changed since step N — resuming at step N+1 with modified plan") but proceed. Do NOT halt.

**Tradeoffs:**
- (+) Directly addresses U1 (plan-hash drift) within the same Phase 3 scope
- (+) Warning-only approach avoids blocking the CEO while surfacing the risk
- (+) Minimal additional code: ~5 LOC for hash comparison + notification
- (-) Warning fatigue if CEO frequently edits plans between steps (e.g., fixing typos)
- (-) Does not prevent the actual failure mode (step N+1 dispatched against renumbered plan) — only surfaces it

**Risk:** Low. The hash check is informational, not blocking. Worst case is the CEO ignores the warning, which is the same as not having the check.

---

## Section 4 — Recommendation

**Recommended path: Hybrid 1 (C-now + A-later), with A scoped as Hybrid 3 (A + plan-hash warning).**

### Justification

1. **Immediate mitigation with zero risk.** Option C ships today as a documentation update. The CEO and Planner adopt verdict-only resume. This eliminates the Step 1 re-dispatch bug for the verdict-pending case immediately, with no code risk.

2. **Option A addresses the structural gap.** The manual rename path is a legitimate workflow — the CEO should be able to rename files without understanding Bellows internals. Option A makes `run_plan()` self-healing: it queries the DB, determines the last completed step, and resumes correctly. This is Layer 1 infrastructure behavior — mechanical, no judgment.

3. **Plan-hash warning (Hybrid 3 addition) addresses U1 at minimal cost.** A 5-LOC hash comparison catches the most dangerous failure mode (plan renumbered between steps) without blocking execution. The CEO gets a Pushover alert and can decide whether to intervene.

4. **Orphan recovery (Hybrid 2) is deferred.** U4 (orphaned in-progress files) is a real but independent bug. It has its own design considerations (thread-registry coupling, timeout heuristics) that shouldn't be bundled into the step-state fix. Follow-up plan: `executable-orphan-recovery-startup`.

5. **U3 (slug substring collision) is deferred.** The `_consume_verdicts()` substring match is a latent bug independent of step-state resume. Follow-up plan: `executable-verdict-slug-exact-match`.

### Q6 unknowns disposition

| Unknown | Disposition |
|---|---|
| U1: Plan-hash drift | **Addressed inline** in Phase 3 via plan-hash warning (Hybrid 3) |
| U2: Deposit verification | **Deferred** — Layer 3 concern. Follow-up: `executable-planner-deposit-verification` |
| U3: Slug substring collision | **Deferred** — independent bug. Follow-up: `executable-verdict-slug-exact-match` |
| U4: Orphan recovery | **Deferred** — independent bug. Follow-up: `executable-orphan-recovery-startup` |
| U5: DB slug ambiguity | **Addressed inline** in Phase 3 via `plan_slug` column addition |
| U6: Race condition | **No action needed** — `shutil.move()` mutex is sufficient (§2 analysis) |
| U7: Halted-vs-complete | **Addressed inline** — `WHERE status = 'Complete'` correctly distinguishes (§2 analysis) |

---

## Section 5 — Phase 3 Scope

### Deliverable 1: Document verdict-only resume (Option C — immediate)

- **File:** `PLANNER_TEMPLATE.md` — add a note in the plan execution/verdict section that resume is verdict-only. Manual `verdict-pending-*` → `executable-*` rename is not supported until BACKLOG #5 Phase 3 ships.
- **Effort:** ~15 minutes. Could ship as a standalone plan before Phase 3.

### Deliverable 2: Add `plan_slug` column to `runs` table

- **File:** `bellows.py`, function `record_run()` (lines 140–167)
- **Changes:**
  - Add `plan_slug TEXT` column to `CREATE TABLE IF NOT EXISTS` DDL (line 151)
  - Add `plan_slug` parameter to `record_run()` signature
  - Add `plan_slug` to the `INSERT` statement (line 162–164)
  - Import or inline `_slug_from_path()` from `verdict.py` — recommend importing to avoid duplication
- **Schema migration:** `ALTER TABLE runs ADD COLUMN plan_slug TEXT` executed once on startup. Add to `start()` method or a new `_migrate_db()` function.
- **Call site updates:** All 4 `record_run()` call sites (lines 269, 307, 327, 365) must pass `plan_slug`. Derive slug once at top of `run_plan()` from `base_filename`.

### Deliverable 3: DB resume query in `run_plan()`

- **File:** `bellows.py`, function `run_plan()` (starting at line 190)
- **New function:** `_get_last_completed_step(db_path: str, plan_slug: str) -> Optional[int]`
  ```
  SELECT MAX(step) FROM runs WHERE plan_slug = ? AND status = 'Complete'
  ```
  Returns `int` or `None` if no completed steps found.
- **Integration point:** After shadow cache check (line 215), before claim (line 231). When `resume_step is None` and shadow cache exists:
  ```python
  if resume_step is None and shadow_text is not None:
      slug = _slug_from_path(plan_path)
      last_step = _get_last_completed_step(db_path, slug)
      if last_step is not None and last_step >= 1:
          resume_step = last_step + 1
          print(f"Bellows: DB resume — last completed step {last_step}, resuming at {resume_step}")
  ```
- **Guard:** Only triggers when shadow cache exists (indicating a prior claim). Fresh plans have no shadow and no DB rows — they correctly start at step 1.

### Deliverable 4: Plan-hash drift warning

- **File:** `bellows.py`, function `run_plan()`
- **Integration point:** After Deliverable 3's resume logic, before `bootstrap_prompt` construction (line 252). When `resume_step > 1`:
  ```python
  if resume_step is not None and resume_step > 1 and shadow_text is not None:
      import hashlib
      shadow_hash = hashlib.sha256(shadow_text.encode()).hexdigest()[:12]
      current_hash = hashlib.sha256(plan_text.encode()).hexdigest()[:12]
      if shadow_hash != current_hash:
          print(f"Bellows: ⚠️ plan content changed since last step — shadow={shadow_hash} current={current_hash}")
          notifier.push(app_key, user_key, "Bellows — Plan Modified",
                        f"Plan {plan_name} content changed since step {resume_step - 1}. Resuming at step {resume_step} with modified plan.")
  ```

### Deliverable 5: Tests

New tests in `tests/test_bellows.py`:

1. **`test_run_plan_db_resume_from_verdict_pending`** — mock DB with `MAX(step)=2, status=Complete` for slug. Verify `run_plan()` dispatches step 3, not step 1.
2. **`test_run_plan_db_resume_no_prior_steps`** — mock empty DB. Verify step 1 dispatch.
3. **`test_run_plan_db_resume_slug_exact_match`** — insert DB rows for slug `foo-bar` and `foo`. Query for `foo`. Verify only `foo` rows are considered.
4. **`test_run_plan_plan_hash_drift_warning`** — set shadow cache content ≠ plan text, `resume_step=2`. Verify Pushover notification fired.
5. **`test_record_run_stores_slug`** — call `record_run()` with `plan_slug` param. Verify column populated.
6. **`test_get_last_completed_step`** — insert rows with various statuses. Verify function returns correct max.

### Files changed summary

| File | What changes |
|---|---|
| `bellows.py` | `record_run()` signature + DDL, new `_get_last_completed_step()`, resume logic in `run_plan()`, hash-drift warning, import `_slug_from_path` from verdict, DB migration in `start()` |
| `verdict.py` | None (already exports `_slug_from_path` — rename to `slug_from_path` and make public, or import the private function) |
| `tests/test_bellows.py` | 6 new tests |

### Effort estimate

- **Phase 3 implementation:** 2–3 hours (Small tier plan, 2 steps: DEV + QA)
- **Deliverable 1 (Option C documentation):** can ship independently as a standalone 1-step plan, ~15 minutes

---

## Section 6 — CEO Decisions Required Before Phase 3

### Decision 1: Canonical slug column vs. LIKE query fragility

**Question:** Should the `runs` table get a `plan_slug` column for reliable querying, or should we accept `LIKE '%slug%'` fragility for now?

| Choice | Tradeoff |
|---|---|
| **Add `plan_slug` column** (recommended) | +5 LOC, requires `ALTER TABLE` migration on first startup after deploy. Eliminates slug collision risk permanently. |
| **Accept LIKE fragility** | 0 schema changes. Works correctly as long as no two plan slugs are substrings of each other. Risk: a plan `foo` matches `foo-bar` rows. In practice, current plan naming conventions (date-suffixed slugs) make collisions unlikely but not impossible. |

### Decision 2: Plan-hash mismatch behavior

**Question:** When a re-claimed plan's content differs from the shadow cache (plan was edited between steps), should Bellows warn-and-proceed or halt-and-notify?

| Choice | Tradeoff |
|---|---|
| **Warn and proceed** (recommended) | CEO gets a Pushover notification. Plan continues executing. Risk: step N+1 prompt references content that no longer matches the plan text. Benefit: no blocking — CEO can edit plans freely for typo fixes, formatting, etc. |
| **Halt and notify** | CEO must explicitly approve resume after every plan edit. Safer but creates friction for trivial edits. Could be implemented as a halt with a dedicated "plan-modified" pause reason. |

### Decision 3: `_slug_from_path` publication

**Question:** `verdict.py:_slug_from_path()` (lines 65–75) is currently a private function. Phase 3 needs it in `bellows.py` for the DB query. Should we:

| Choice | Tradeoff |
|---|---|
| **Make it public** (`slug_from_path`) and import in `bellows.py` | Clean — single source of truth for slug derivation. Minor: renames a private function to public, which is a contract change. |
| **Duplicate the logic** in `bellows.py` | No cross-module dependency. But two copies of the same slug logic can drift. |

### Decision 4: Ship Option C documentation independently?

**Question:** Should the verdict-only resume documentation (Deliverable 1) ship as a separate immediate plan before Phase 3 implementation begins, or bundle it into Phase 3?

| Choice | Tradeoff |
|---|---|
| **Ship independently now** | CEO gets the procedural guard immediately. Phase 3 can take its time. |
| **Bundle into Phase 3** | Single plan, single review cycle. But the bug remains unmitigated until Phase 3 ships. |

---

## Open Questions

1. **Backfill strategy:** When the `plan_slug` column is added, existing rows will have `NULL` for `plan_slug`. Should we backfill by parsing `plan_path` for existing rows, or accept that historical rows won't participate in slug queries? Recommendation: no backfill — only new dispatches need the slug, and historical rows are write-only telemetry.

2. **`_slug_from_path` for `halted-*` prefix:** `verdict.py:_slug_from_path()` strips `in-progress-`, `verdict-pending-`, `executable-`, and `diagnostic-` but does NOT strip `halted-`. If a `halted-*` plan is renamed to `executable-*`, the slug derivation in `run_plan()` works correctly (it receives `executable-*` or `in-progress-*` after claim). But if `record_run()` is called with a `halted-*` path, the slug would include the `halted-` prefix. This edge case doesn't arise in current code because `record_run()` is only called from `run_plan()` where the path is always `in-progress-*`. No action needed, but worth documenting.

3. **Diagnostic plans and DB resume:** Diagnostic plans force `total_steps = 1` at line 224. The DB resume query should be skipped for diagnostics since they always re-execute from scratch (they're single-step investigations). The guard `shadow_text is not None` likely handles this — diagnostics that complete successfully are moved to `Done/` and their shadow is deleted. But this should be verified in Phase 3 testing.

---

## Layer Impact

- **Layer 1 (Bellows):** Primary impact. `run_plan()` gains self-healing resume, `record_run()` gains slug column.
- **Layer 2 (Agents):** No impact. Agents are unaware of step-state persistence.
- **Layer 3 (Planner):** Minor impact. Planner documentation updated for verdict-only resume (Option C). Deposit verification remains a Layer 3 concern (U2) — deferred.

No responsibility shift between layers. Option A keeps step-state persistence in Layer 1 where it belongs — mechanical DB lookup, no judgment.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a design comparison document evaluating three options (A: DB query in run_plan, B: watcher-side query, C: procedural elimination) and three hybrid combinations against the 7 risk-surface unknowns identified in Phase 1. Recommended Hybrid 1+3 (procedural bridge now, DB resume with plan-hash warning later). Scoped Phase 3 implementation at 5 deliverables across 2 files with 6 new tests.

### Files Deposited
- `bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md` — Phase 2 design comparison and recommendation

### Files Created or Modified (Code)
- None (design document only)

### Decisions Made
- Recommended Hybrid 1+3 (C-now + A-later with plan-hash warning) as the implementation path
- Determined that U2 (deposit verification), U3 (slug collision), and U4 (orphan recovery) are option-independent and should be deferred to follow-up plans
- Determined that U6 (race condition) requires no action — existing shutil.move() mutex is sufficient
- Assessed realistic LOC for Option A at 20–25, not 10 as Phase 1 estimated

### Flags for CEO
- 4 decisions required before Phase 3 can begin (§6): slug column vs. LIKE fragility, hash mismatch behavior, _slug_from_path publication, and Option C shipping timeline

### Flags for Next Step
- None (terminal step — design document only)
