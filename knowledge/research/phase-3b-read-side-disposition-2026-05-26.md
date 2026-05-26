# Phase 3b Read-Side Disposition — Findings

**Date:** 2026-05-26
**Agent:** Bellows Systems Analyst
**Scope:** Ship-or-retire disposition for Phase 3b DB read-side step-state-resume. Single-step SA diagnostic — no code changes.
**Canonical sources:** `knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md` Sections A3/A4; `knowledge/BACKLOG.md` Phase 3b Open entry (2026-05-24) and Closed entries (2026-04-30, 2026-05-01).

---

## Disposition: RETIRE

**One-paragraph reasoning:** No concrete use case exists in current or near-term hardening work that would benefit from a DB read-side. The read-side was previously shipped (2026-04-28) and deliberately removed (2026-05-01) after the Phase 3b/3c diagnostic confirmed it guarded a manual-rename resume path unsupported by Rule 25 — the supported verdict-resume path passes `resume_step` explicitly without consulting the DB. Since removal, the two hardening items that could have motivated a DB read-side — RV-1 boundary (items #2/#3, daemon-restart recovery) and item #5 (step-counter loop on precondition-failure) — were both closed 2026-05-24 via mechanisms that do not require DB state (rename-first ordering and precondition-failure verdict-request field, respectively). No open BACKLOG item, no gate, and no observability surface currently needs or would benefit from querying step completion from the DB. Carrying the Open BACKLOG entry forward creates process friction (recurring "is this still relevant?" triage question) and risks the stale-claim pattern (a future Planner instance reads the entry and ships the helper without a use case, analogous to the verdict-enrichment roadmap stale-claim captured 2026-05-26).

---

## Verification Blocks

### Block 1: Write-only state is current

**Command:** `grep -nE "SELECT|conn\.execute|cursor\.execute" bellows.py`

**Expected:** No SELECT against `runs` table data.

**Actual:**
```
155:    conn.execute(           # CREATE TABLE IF NOT EXISTS runs (...)
169:    existing = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
182:            conn.execute(f"ALTER TABLE runs ADD COLUMN {col} {col_type}")
279:    conn.execute(           # CREATE TABLE IF NOT EXISTS runs (...)
292:    conn.execute(           # INSERT INTO runs (...)
```

All five `conn.execute` calls are schema operations (CREATE TABLE, PRAGMA table_info, ALTER TABLE) or data writes (INSERT). Zero SELECT statements against `runs` data. The `PRAGMA table_info` at line 169 is schema introspection for the migration helper, not a data read.

Additional confirmation: `grep -n "_get_last_completed_step" bellows.py` returned no matches. The helper does not exist.

**Materiality:** Confirms the 2026-05-24 diagnostic finding (Section A3) is still current. The half-implementation has not advanced.

### Block 2: BACKLOG effort estimate

**Source:** `knowledge/BACKLOG.md` line 15, Open entry dated 2026-05-24.

**Exact text:** "Effort estimate: small (~10 LOC for the helper plus integration sites), or medium if the design needs revisiting."

**Materiality:** The estimate is moot under a RETIRE disposition. Noted for completeness: the ~10 LOC estimate was accurate for the original 2026-04-28 implementation, which was shipped and then removed.

### Block 3: Use-case survey completeness

Four areas surveyed with explicit findings:

| Area | Sites examined | Use case found? | Detail |
|---|---|---|---|
| **Daemon-restart recovery** | Rename-first fix (Shape A, shipped 2026-05-24, Closed BACKLOG entry); precondition-failure field (Shape E, shipped 2026-05-24, Closed BACKLOG entry) | **No** | RV-1 boundary closed by rename-first ordering — filename state is now always consistent post-restart. Item #5 closed by precondition-failure verdict-request field — step-advancement decision uses metadata, not DB. Neither fix required or would have benefited from a DB read-side. |
| **Cross-validation gates** | `grep -n "cross.valid\|step.state\|completed_step\|resume_step\|last.*step" gates.py` — no matches | **No** | No gate consumes plan step-state from the DB. Gates operate on file content (plan text, agent output) and file existence (deposits), not DB state. |
| **Observability surfaces** | Terminal logs (`_log` calls), verdict request content (`verdict.post_verdict_request`), verdict ledger (`verdict.log_to_ledger`) | **No** | All observability surfaces derive information from runtime variables and file content. None query the DB. The Status UI BACKLOG entry (2026-05-21) mentions `bellows.db` as a potential data source for run history display, but that is general run-history querying (reads all columns), not the step-state-resume cross-validation that Phase 3b's `_get_last_completed_step` was designed for. |
| **Future hardening (named items)** | All 12 Open BACKLOG entries surveyed: rule-20 evidence disambiguation, isinstance guard cleanup, md_paths[0] set ordering, teardown push silent failure, daemon-restart recovery (already closed), path-keyed rejection cache, worktree teardown cherry-pick conflicts (2 entries), MCP tool denials, WebSearch/WebFetch allowedTools, status UI, defensive default header, deposits parser parenthetical | **No** | None of the 12 Open entries reference DB step-state, require cross-validation of step completion, or would benefit from a `_get_last_completed_step` helper. |

**Materiality:** The survey covers all areas specified in the diagnostic procedure. No concrete use case was found. The RETIRE disposition holds.

---

## Investigation Detail

### Item 1: Confirming the half-implementation state

The write-side is active: `record_run()` (bellows.py:268-297) inserts rows into the `runs` table with `plan_slug` populated at every call site (bellows.py:456, 462, 534, 556, 627). The `plan_slug` column is defined in the schema (bellows.py:165, 289) and populated via `slug_for(plan_name)` or `verdict.slug_from_path()`.

The read-side is absent: `_get_last_completed_step` does not exist. No SELECT queries against `runs` data exist. The DB is write-only for plan-execution state.

**No Block 1 contradiction found.** The 2026-05-24 findings are current.

### Item 2: Historical context — the read-side was shipped and removed

The BACKLOG Closed entry dated 2026-04-30 (hygiene) states: "Superseded by BACKLOG #6 Phase 3b (DB-based step state recovery, shipped 2026-04-28: `plan_slug` column added to `runs` table; `_get_last_completed_step(db_path, plan_slug)` helper added; `run_plan()` now queries DB for last completed step when `resume_step is None` and shadow cache exists)."

The BACKLOG Closed entry dated 2026-05-01 states: "Phase 3b/3c DB step-state-resume slug-collision. Diagnostic at `knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md` confirmed phantom-resume mechanism. Q6 cost-benefit recommended F3 (remove dead code) — Phase 3b/3c guards a manual-rename resume path that's unsupported per Rule 25, and the supported verdict-resume path passes resume_step explicitly without consulting the DB."

**Timeline:**
1. **2026-04-28:** Phase 3b shipped — `_get_last_completed_step` added, `run_plan()` queried DB for last completed step when `resume_step is None`.
2. **2026-05-01:** Phase 3b/3c removed as dead code — the read-side guarded a manual-rename resume path (re-depositing `executable-*` to restart a plan) that is unsupported by Rule 25. The supported path (verdict-resume via `_consume_verdicts`) passes `resume_step` explicitly to `handle_new_plan`, bypassing any DB lookup.
3. **2026-05-24:** The daemon-restart-state-divergence diagnostic confirmed DB is write-only.

**Significance for disposition:** The read-side is not "never written" — it was written, evaluated, and deliberately removed because it served no purpose in the supported resume path. Re-shipping it would re-introduce code that was already evaluated and rejected. The BACKLOG Open entry's framing ("half-implemented") is imprecise; the accurate characterization is "fully implemented, evaluated, removed as dead code, write-side retained as benign."

### Item 3: Cost of carrying the half-implementation forward

- **Column-write cost:** Negligible. One INSERT per step completion. No behavioral risk.
- **BACKLOG-entry-as-reminder cost:** Non-zero. Creates two risks:
  - **(a) Process friction:** Every Planner instance reading the BACKLOG encounters the entry and must determine whether it is actionable. This is the stale-claim pattern documented in LESSONS.md 2026-05-22 ("BACKLOG defers grounded in Planner-side fallback can be silently invalidated by gate mechanization") — an entry that was valid when filed but whose context has changed.
  - **(b) Premature shipping:** A future Planner instance reads the "~10 LOC" estimate and ships the helper without a use case, adding dead code that must then be re-evaluated and re-removed (the exact 2026-04-28 → 2026-05-01 cycle).
- **Structural rot risk:** Low. The `plan_slug` column is a simple TEXT column with no constraints, no indexes, and no foreign keys. A future schema migration adding or removing columns would not be affected by its presence. If the column were ever removed, the write-side calls in `record_run` would need updating, but this is trivially detectable (INSERT fails if column doesn't exist).

### Item 4: Item #5 closure status

The diagnostic prompt states: "Item #5 in the BACKLOG was 'step-counter loop after precondition-failure verdict' which has been Closed 2026-05-24 via the precondition-failure-field fix. Confirm or correct."

**Confirmed.** BACKLOG Closed entry dated 2026-05-24: "Step-counter loop after precondition-failure verdict (originally 2026-05-21). Shipped via `executable-precondition-failure-field-2026-05-24` (DEV commit `0a90e26`). [...] Shape E (Precondition Failure verdict-request field) implemented [...] `bellows.py:1230-1237` replaced unconditional `resume_step=step_number + 1` with conditional dispatch (retry same step on precondition failure, advance otherwise)."

The fix uses a verdict-request metadata field, not DB state. The DB read-side was not needed.

---

## Retirement Terms

### BACKLOG entry closure

The Open entry dated 2026-05-24 ("Phase 3b step-state-resume is half-implemented") should be closed as won't-fix with the following retirement reasoning:

> Retired 2026-05-26. The read-side was previously shipped (2026-04-28) and removed (2026-05-01) as dead code — it guarded a manual-rename resume path unsupported by Rule 25. The two hardening items that could have motivated re-shipping (RV-1 boundary and step-counter loop) were both closed 2026-05-24 via mechanisms that do not require DB state. No current or near-term use case exists. The `plan_slug` column on the `runs` table is retained as benign write-only state.

### Revisit trigger

The read-side should be reconsidered if:

- A Bellows hardening item lands that requires cross-validation of step completion against on-disk state, AND the filename-prefix state and verdict-request metadata fields are insufficient for that cross-validation.
- The Bellows Status UI (Open BACKLOG entry, 2026-05-21) is designed and its data-source decision reveals that step-state-resume queries (not just general run history) are needed.

### Column retention

The `plan_slug` column stays. It is benign as write-only — one TEXT column per INSERT, no indexes, no constraints. If a future schema migration touches the `runs` table, the column should be evaluated: retain if a read-side use case has emerged; remove if not, updating the `record_run` INSERT to drop the column.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Executed the Phase 3b read-side ship-or-retire disposition diagnostic. Confirmed the DB write-only state is current (zero SELECTs, `_get_last_completed_step` absent). Discovered the read-side was previously shipped (2026-04-28) and deliberately removed (2026-05-01) as dead code — a fact the Open BACKLOG entry does not capture. Surveyed 4 hardening areas (daemon-restart recovery, cross-validation gates, observability surfaces, 12 named future-hardening items) and found zero concrete use cases for a DB read-side. Recommended RETIRE with explicit revisit trigger and column-retention terms.

### Files Deposited
- `knowledge/research/phase-3b-read-side-disposition-2026-05-26.md` — disposition findings (RETIRE), verification blocks, historical timeline, retirement terms

### Files Created or Modified (Code)
- None — investigation only, no source modifications

### Decisions Made
- Disposition: RETIRE. No concrete use case exists; the read-side was previously shipped and removed; the two hardening items that could have motivated it are both closed via non-DB mechanisms.
- `plan_slug` column retained as benign write-only state. No column removal.
- Revisit trigger specified: re-evaluate if a hardening item needs cross-validation that filename-prefix state and verdict-request metadata cannot provide.

### Flags for CEO
- **Disposition recommendation: RETIRE.** The Phase 3b read-side was shipped 2026-04-28, removed 2026-05-01 as dead code (guarded unsupported manual-rename resume path), and the two subsequent hardening items that could have motivated re-shipping (RV-1 boundary, step-counter loop) were both closed 2026-05-24 via non-DB mechanisms. No concrete use case exists in the current 12 Open BACKLOG items. Carrying the Open entry forward creates process friction and risks the stale-claim pattern. Recommended: close the BACKLOG entry as won't-fix with the retirement reasoning and revisit trigger documented in this disposition.

### Flags for Next Step
- None — single-step diagnostic, no further steps
