# Diagnostic — Phase 3b Read-Side Step-State-Resume: Ship-or-Retire
**Project:** bellows
**Date:** 2026-05-26
**Author:** Planner
**Dispatch Mode:** bellows
**Total Steps:** 1
**pause_for_verdict:** after_step_1
**auto_close:** false
**qa_steps:** none

---

## CEO Context

Phase 3b was a 2026-04-28 design intent for DB-based step-state recovery. The write-side shipped: `bellows.db`'s `runs` table has a `plan_slug` column and `record_run` populates it correctly. The read-side never shipped: there is no `_get_last_completed_step()` helper and no SELECT queries from `bellows.py` consult `runs` for resume decisions.

The 2026-05-24 daemon-restart-state-divergence diagnostic (`bellows/knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md`) confirmed this in Sections A3 and A4 — `bellows.db` is currently write-only relative to `bellows.py`. The Section E16 fix (rename-first ordering, shipped 2026-05-24) closed the RV-1 boundary by making the on-disk filename state the authoritative source for post-restart recovery, which makes the absence of DB read-side less acute but does not retire the design intent. Future hardening that wants to use DB state for cross-validation (e.g., "did the agent actually complete this step?" sanity checks) still has no read path.

The current BACKLOG entry frames this as "half-implemented" — a code-debt classification, not a bug. The disposition asks two questions:

1. **Is the DB read-side worth shipping today?** If a concrete use case needs it (a specific cross-validation, a recovery path the on-disk state cannot cover, an observability surface), ship the ~10 LOC helper. If no use case is on the horizon, retire the design intent formally.

2. **If retired, what gets recorded?** The `plan_slug` column on the runs table is benign as write-only — it costs one column-write per step completion and adds no behavioral risk. Retiring the design intent does NOT require removing the column. Document the retirement so future Planners don't re-discover Phase 3b as half-done unfinished work.

This is a single-step SA diagnostic. No code changes. The SA reads sections A3 and A4 of the 2026-05-24 diagnostic (the canonical source per Rule 27), examines the live state of `bellows.db` and `bellows.py`'s `record_run` integration, surveys recent hardening work for use cases that would benefit from a DB read-side, and proposes one of three dispositions.

The diagnostic does NOT propose code shapes for the helper unless the recommendation is SHIP. It does NOT attempt to retire the column itself — that would be a separate decision after this disposition lands. It does NOT read source code beyond what the BACKLOG entry already cites (the `record_run` write site and the `runs` table schema); deeper code investigation would be a follow-up if SHIP is selected.

---

## STEP 1 (SA) — Phase 3b Read-Side Disposition

Read your specialist file at `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip glossary read — this is a code-debt characterization task with no domain terminology surface beyond what the specialist file covers. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.

### Canonical sources (per Rule 27)

- `knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md` — sections A3 (DB write-only state) and A4 (read-side absence). These are the source-of-truth findings. Do NOT re-derive from source code reading.
- `knowledge/BACKLOG.md` — the Phase 3b read-side Open entry dated 2026-05-24 describes the resolution shape and effort estimate.

### Investigation procedure

1. **Confirm the half-implementation is still half-implemented.** Read the relevant `record_run` write-site in `bellows.py` and confirm `plan_slug` is being populated (the write-side claim). Confirm `bellows.py` contains no `SELECT` queries against the `runs` table (the read-side absence claim). Two greps are sufficient:
   - `grep -n "record_run\|plan_slug" bellows.py` — verify the write-site exists and look for any non-write references
   - `grep -nE "SELECT|conn\.execute|cursor\.execute" bellows.py` — verify no SELECT statements against `runs`

   If the greps surface anything inconsistent with the 2026-05-24 findings (e.g., a SELECT against `runs` has been added since), report it as a Block 1 contradiction and pause the disposition until reconciled.

2. **Enumerate use cases that would benefit from a DB read-side.** Survey recent hardening work (post-2026-05-21) for any pattern where the daemon needed information it could only get from on-disk state (filenames, plan headers) and where DB state would have been a better signal. Candidates to look at:
   - Daemon-restart recovery paths (the rename-first fix, the precondition-failure-field fix). Would a DB read-side have provided cross-validation that would have caught one of these bugs earlier? Or are these paths fully covered by filename state?
   - Cross-validation gates (anything in `gates.py` that consumes plan state). Do any of them duplicate state that the DB tracks better?
   - Observability surfaces (terminal logs, verdict request enrichment, the ledger). Does any of them surface step-state information today that would be cleaner from the DB?
   - Future hardening: the BACKLOG entry mentions "did the agent actually complete this step?" as a cross-validation for item #5. Is item #5 still Open, and would a DB read-side actually unblock it? (Item #5 in the BACKLOG was "step-counter loop after precondition-failure verdict" which has been Closed 2026-05-24 via the precondition-failure-field fix. Confirm or correct.)

   The bar for "use case exists" is concrete: a specific hardening direction blocked or made harder by the read-side absence, not a hypothetical "someday we might want this."

3. **Survey the cost of carrying the half-implementation forward.** The current cost is the column-write per step completion plus the BACKLOG-entry-as-reminder. The column-write is negligible. The BACKLOG entry is non-zero — it creates a recurring "is this still relevant?" question every time a Planner instance reads the BACKLOG. Two ways the cost goes up: (a) someone reads the BACKLOG and assumes the read-side is queued work and tries to ship it without a use case (analogous to the verdict-enrichment roadmap stale-claim pattern just captured 2026-05-26); (b) the design intent silently rots — a future schema change to the `runs` table breaks the unused column and no one notices because there's no read-side consumer. (b) is structural rot; (a) is process friction.

4. **Disposition recommendation.** Based on items 2 and 3, propose one of three dispositions:

   - **SHIP** — Concrete use case exists in current or near-term hardening work. Recommendation: file a follow-on executable plan to ship `_get_last_completed_step(plan_slug)` and integrate it at the named site(s). The diagnostic must specify (in its findings) WHICH sites would consume the helper and WHAT cross-validation it would enable. Do NOT design the helper signature or test surface in this diagnostic — that's the executable's scope. Just identify the integration sites.

   - **RETIRE** — No concrete use case exists; the design intent should be formally retired. Recommendation: close the BACKLOG entry as won't-fix with explicit retirement reasoning. Document a revisit trigger: under what future condition should the read-side be reconsidered? (E.g., "if a Bellows hardening item lands that requires cross-validation of step completion against on-disk state.") The `plan_slug` column stays as benign write-only state; retiring the design intent does not remove the column. The retirement must also note what happens if the column write-side is ever revisited (e.g., a schema migration) — at that point the column should either be retained-with-reason or removed.

   - **PARK-PENDING-USE-CASE** — Ambiguous; no current use case, but a plausible near-term one is visible on the horizon. Recommendation: leave the BACKLOG entry Open with explicit "park-pending" annotation specifying the use case being waited for. Specify a re-evaluation trigger. This is a middle option between SHIP and RETIRE — choose it only when there is genuine uncertainty, not as a default.

   For SHIP and PARK-PENDING-USE-CASE, the disposition must name the specific use case in concrete terms. "Future hardening might need this" is not a use case; "the upcoming work on X needs cross-validation of step state against DB" is a use case. If you cannot name a concrete use case with reference to current open work, the disposition is RETIRE.

### Discipline notes for this diagnostic

- Do NOT read source code beyond the two greps in Item 1. The 2026-05-24 findings are the canonical source; this diagnostic builds on them, it does not re-derive them. If the greps surface inconsistencies, flag and pause.
- Do NOT propose helper signatures, test surfaces, or integration code. The disposition is about whether to ship, not how to ship.
- Do NOT classify "code-debt that has been sitting on the BACKLOG" as inherently a use case. Code-debt without a concrete consumer is RETIRE-eligible, not SHIP-eligible.
- The retirement option is the default when no concrete use case is named. This is anti-sycophantic discipline — half-implementations should not be promoted to "queued work" without justification.

### Verification Blocks (Rule 39)

Capture verification blocks for the load-bearing claims:

- **Block 1:** the write-only state is current. Command: `grep -nE "SELECT|conn\.execute|cursor\.execute" bellows.py | head -20`. Expected: no SELECT against `runs` table (some SELECT statements may exist for other tables — distinguish in evidence). Actual: command output. Materiality: the entire disposition assumes the half-implementation has not advanced since 2026-05-24; this block confirms.

- **Block 2:** the BACKLOG entry's effort estimate. Command: read `knowledge/BACKLOG.md` for the Phase 3b entry, capture the exact effort estimate text. Expected: "~10 LOC for the helper plus integration sites." Materiality: SHIP recommendation budgets against this estimate; a much higher actual estimate could shift SHIP to PARK-PENDING-USE-CASE.

- **Block 3:** the use-case survey is complete. Command: enumerate the hardening areas surveyed (daemon-restart recovery, cross-validation gates, observability surfaces, named future-hardening items). Expected: at least 4 areas surveyed with explicit "no use case found" or "use case: X" for each. Materiality: the RETIRE recommendation requires explicit no-use-case confirmation, not silence.

### Deposits

**Deposits:**
- `bellows/knowledge/research/phase-3b-read-side-disposition-2026-05-26.md`

### Output Receipt Format

End the deposit with the standard Output Receipt section per the specialist template. Status: Complete. Files Deposited: the single findings file. Flags for CEO: the disposition recommendation (SHIP / RETIRE / PARK-PENDING-USE-CASE) with one-paragraph reasoning citing the concrete (or absent) use case.
