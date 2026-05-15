# Phase 3b/3c Mechanism & Cost-Benefit Diagnostic Findings
**Date:** 2026-05-01 | **Plan:** diagnostic-phase-3b-mechanism-and-cost-benefit-2026-05-01

---

## Q1 — Characterize the Orphan DB State

### Schema

```sql
CREATE TABLE runs (
    id INTEGER PRIMARY KEY,
    plan_path TEXT,
    project TEXT,
    session_id TEXT,
    step INTEGER,
    status TEXT,
    cost_usd REAL,
    started_at TEXT,
    completed_at TEXT,
    timestamp TEXT,
    cost REAL,
    plan_slug TEXT
);
```

Note: `plan_hash` column does NOT exist. Phase 3c computes hashes at runtime from shadow/plan content — it never persists them to the DB. The `cost_usd`, `started_at`, `completed_at` columns are vestigial (all NULL in post-Phase-3b rows); `timestamp` and `cost` are the live columns.

### Full Row Dump for `plan_slug = 'bellows-session-wrap-2026-05-01'`

| id | session_id | step | status | timestamp | cost | plan_slug |
|----|-----------|------|--------|-----------|------|-----------|
| 554 | faebcd7f-6333-4ec4-bb01-d600bdac2987 | 1 | Complete | 2026-05-01T16:44:53.688911 | 0.635 | bellows-session-wrap-2026-05-01 |
| 555 | faebcd7f-6333-4ec4-bb01-d600bdac2987 | 2 | Complete | 2026-05-01T16:46:56.247585 | 1.104 | bellows-session-wrap-2026-05-01 |
| 556 | faebcd7f-6333-4ec4-bb01-d600bdac2987 | 2 | VerdictPending | 2026-05-01T16:46:56.651334 | 1.104 | bellows-session-wrap-2026-05-01 |
| 570 | 15804c92-5af7-448d-95ce-7e32b11b09db | 3 | Complete | 2026-05-01T20:24:07.316991 | 0.734 | bellows-session-wrap-2026-05-01 |
| 571 | 15804c92-5af7-448d-95ce-7e32b11b09db | 3 | VerdictPending | 2026-05-01T20:24:07.681443 | 0.734 | bellows-session-wrap-2026-05-01 |

### Timeline Analysis

**Rows 554–556 (session `faebcd7f`):** A PRIOR plan instance executed steps 1 and 2 between 16:44 and 16:46, then paused at VerdictPending. This matches the mtime of `verdict-request-bellows-session-wrap-2026-05-01-step-2.md` (16:46:56). These rows were deposited BEFORE the v1 wrap was dispatched.

**Rows 570–571 (session `15804c92`):** The v1 wrap plan dispatched around ~20:1X. Due to Phase 3b resume logic finding step 2 Complete in rows 554-555, it skipped to step 3 directly. Step 3 completed at 20:24 and then paused at VerdictPending (row 571).

**Hypothesis CONFIRMED:** The prior plan instance (session `faebcd7f`) left DB rows marking step 2 as Complete. The new v1 plan found these rows and triggered phantom resume. The two plans have DIFFERENT session IDs, confirming they are separate `claude -p` invocations — not a legitimate resume of the same plan.

---

## Q2 — Trace `_get_last_completed_step` End-to-End

### Function Body (`bellows.py:175-188`)

```python
def _get_last_completed_step(db_path: str, plan_slug: str) -> Optional[int]:
    """Return the highest step number marked Complete for this plan_slug, or None."""
    try:
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute(
                "SELECT MAX(step) FROM runs WHERE plan_slug = ? AND status = 'Complete'",
                (plan_slug,),
            ).fetchone()
            return row[0] if row and row[0] is not None else None
        finally:
            conn.close()
    except sqlite3.Error:
        return None
```

**WHERE clause:** Filters on `plan_slug` only. No `plan_hash`, no `session_id`, no timestamp filtering. Any row in `runs` with matching slug and status='Complete' contributes to the MAX.

### Call Site (`bellows.py:243-247`)

```python
if resume_step is None and shadow_text is not None:
    last_step = _get_last_completed_step(db_path, plan_slug)
    if last_step is not None and last_step >= 1:
        resume_step = last_step + 1
        print(f"Bellows: DB resume — last completed step {last_step}, resuming at {resume_step}")
```

### Decision Chain: Plan Detection → Claim → Dispatch

1. **Watcher detects** `executable-bellows-session-wrap-2026-05-01.md` → `is_runnable_plan()` → True
2. **`handler._handle(path)`** → `orchestrator.handle_new_plan(path)`
3. **`handle_new_plan(path, resume_step=None)`** → spawns thread → `run_plan(path, config, response_server, resume_step=None)`
4. **`run_plan()` L228:** `plan_filename = os.path.basename(plan_path)` → `executable-bellows-session-wrap-2026-05-01.md`
5. **L234:** `plan_slug = verdict.slug_from_path(base_filename)` → `bellows-session-wrap-2026-05-01`
6. **L237:** `shadow_text = _read_shadow(plan_filename)` → Reads `.bellows-cache/executable-bellows-session-wrap-2026-05-01.md.pristine` — **returns the PRIOR plan's pristine content** (shadow was NOT deleted because the prior plan was still in verdict-pending, not halted)
7. **L243:** Guard: `resume_step is None` ✅ AND `shadow_text is not None` ✅ → **enters DB resume block**
8. **L244:** `_get_last_completed_step(db_path, "bellows-session-wrap-2026-05-01")` → returns **2** (from rows 554-555)
9. **L246:** `resume_step = 3`
10. **L247:** Prints `DB resume — last completed step 2, resuming at 3`
11. **L249-254:** Phase 3c hash-drift check fires (shadow differs from new plan) → warning printed, but non-blocking
12. **L266-270:** Claim move: `executable-*` → `in-progress-*`; **shadow is OVERWRITTEN** with new plan content
13. **L289-290:** Bootstrap prompt dispatches step 3

**Critical finding:** The guard `shadow_text is not None` is intended to mean "this plan was previously in-progress and has shadow state." But it actually means "any plan with the same canonical filename was previously claimed and its shadow was not cleaned up." A new plan deposited while a prior same-slug plan is in verdict-pending will find the prior plan's shadow and trigger the DB resume path.

### Single Call Site

`_get_last_completed_step` is called ONLY at L244. It is NOT called in the verdict-resume path (`_consume_verdicts` at L757 passes `resume_step=step_number+1` explicitly, bypassing the guard).

---

## Q3 — Trace Phase 3c Hash-Drift Handling

### Code Block (`bellows.py:249-254`)

```python
if resume_step is not None and resume_step > 1 and shadow_text is not None:
    shadow_hash = hashlib.sha256(shadow_text.encode()).hexdigest()[:12]
    current_hash = hashlib.sha256(plan_text.encode()).hexdigest()[:12]
    if shadow_hash != current_hash:
        print(f"Bellows: ⚠️ plan content changed since last step — shadow={shadow_hash} current={current_hash}")
        notifier.push(app_key, user_key, "Bellows — Plan Modified",
                      f"Plan {plan_name} content changed since step {resume_step - 1}. Resuming at step {resume_step} with modified plan.")
```

**Warning is logged-only + Pushover notification.** It does NOT:
- Raise an exception
- Reset `resume_step` to None
- Block the resume
- Set any flag that downstream code checks

**This is intentional** per Phase 3c design doc (line 9): "Warn-and-proceed, not halt — per the Phase 2 design (Section 4 recommendation), trivial edits (typo fixes, formatting) shouldn't block execution."

**Hash sources:**
- `shadow_hash` (`0b32403e5789`): SHA-256 of the shadow cache file content (`.bellows-cache/executable-bellows-session-wrap-2026-05-01.md.pristine`). This was the PRIOR plan's pristine content.
- `current_hash` (`c64d9688fd4e`): SHA-256 of `plan_text` (the new plan's on-disk content read at L219).

The warning correctly detected that the two plans differ — but since warn-and-proceed is the policy, the phantom resume continued.

---

## Q4 — Map the Full Code-Path from Claim to Dispatch

### Key Finding: DB Resume Runs on FRESH Claims, Not Just Resume-After-Pause

The code does NOT distinguish between:
- **(A) Fresh claim:** New `executable-*` plan detected by watcher → `handle_new_plan(path, resume_step=None)` → `run_plan(path, ..., resume_step=None)`
- **(B) Verdict-resume:** `_consume_verdicts` processes a continue verdict → renames `verdict-pending-*` to `in-progress-*` → `handle_new_plan(inprogress_path, resume_step=step_number+1)`

In path (B), `resume_step` is explicitly set, so the guard `resume_step is None` is False — DB resume does NOT trigger. This is correct.

In path (A), `resume_step=None` and if a shadow exists from a prior same-slug plan, the guard passes — DB resume DOES trigger. **This is the bug path.** The guard was designed for a third path:

- **(C) Manual re-claim:** A plan previously in `halted-*` or `verdict-pending-*` is manually renamed back to `executable-*`, picked up by the watcher, and dispatched with `resume_step=None`. The shadow from the prior claim still exists, signaling "this plan was previously in-progress." The DB resume correctly identifies where to continue.

Path (C) is **no longer supported** per Rule 25's "Resume Protocol — Verdict-Only" subsection. The verdict-resume path (B) is the only supported resume mechanism. Phase 3b's DB resume path was built for (C) and now fires erroneously on (A) when shadow state from a same-slug plan persists.

### Why the Shadow Persists

The shadow is deleted in two places:
1. `_delete_shadow(plan_filename)` in the `stop` verdict path (L766) — when a plan is halted
2. `_delete_shadow(plan_filename)` in the `continue-to-done` and `auto-close` paths (L745, L423) — when a plan completes

The shadow is NOT deleted when a plan is merely in `verdict-pending` state — it's kept for potential resume. This is correct behavior for the verdict-resume path (B), which reads the shadow for metadata extraction (total_steps, header parsing). But it means a new same-slug plan deposited while the old plan is in verdict-pending will find the old shadow.

---

## Q5 — Characterize DB Orphan Accumulation

### Full Slug Inventory

```
SELECT plan_slug, MAX(step) as max_step, COUNT(*) as row_count, MAX(timestamp) as last_ts
FROM runs WHERE plan_slug != '' GROUP BY plan_slug;
```

| # | plan_slug | max_step | rows | last_ts | plan_state |
|---|-----------|----------|------|---------|------------|
| 1 | activity-based-timeout-2026-05-01 | 1 | 2 | T11:27 | Done/ (bellows) |
| 2 | backlog-close-2026-04-18-integration-protocol-2026-05-01 | 2 | 3 | T10:03 | Done/ (bellows) |
| 3 | backlog-hygiene-sweep-2026-04-30 | 2 | 4 | T16:14 | Done/ (bellows) |
| 4 | bellows-integration-section-audit-2026-05-01 | 1 | 2 | T09:51 | Done/ (bellows) |
| 5 | bellows-session-wrap-2026-05-01 | 3 | 5 | T20:24 | halted (bellows) |
| 6 | bellows-session-wrap-v2-2026-05-01 | 3 | 4 | T21:02 | Done/ (bellows) |
| 7 | canary-phase-3b-restart-2026-04-30 | 2 | 3 | T12:47 | Done/ (bellows) |
| 8 | cleanup-slug-normalization-2026-05-01 | 2 | 3 | T18:49 | Done/ (bellows) |
| 9 | cleanup-verdicts-call-site-gap-2026-05-01 | 1 | 2 | T17:42 | halted (bellows) |
| 10 | cleanup-verdicts-call-site-gap-rerun-2026-05-01 | 1 | 2 | T18:13 | Done/ (bellows) |
| 11 | close-activity-timeout-backlog-2026-05-01 | 2 | 3 | T11:36 | Done/ (bellows) |
| 12 | close-stranded-csv-upload-fetch-fix-2026-05-01 | 1 | 2 | T15:54 | Done/ (invoice-pulse) |
| 13 | close-stranded-lessons-step-numbering-2026-05-01 | 1 | 2 | T15:45 | Done/ (bellows) |
| 14 | inactivity-timeout-bump-1800s-2026-05-01 | 2 | 3 | T17:51 | Done/ (bellows) |
| 15 | invoice-pulse-session-wrap-2026-05-01 | 2 | 3 | T16:58 | Done/ (invoice-pulse) |
| 16 | lessons-forge-first-cycle-2026-05-01 | 1 | 2 | T12:35 | halted (forge) |
| 17 | lessons-forge-phase2a-classify-2026-05-01 | 1 | 2 | T13:06 | Done/ (forge) |
| 18 | lessons-verdict-format-and-stranded-plans-2026-05-01 | 2 | 3 | T16:33 | Done/ (bellows) |
| 19 | parallel-1-executable-deposit-exists-directory-paths-2026-04-30 | 2 | 4 | T16:16 | Done/ (bellows) |
| 20 | parallel-1-executable-ledger-pause-reason-code-2026-04-30 | 2 | 3 | T15:50 | Done/ (bellows) |
| 21 | parallel-plan-scope-check-collision-2026-05-01 | 1 | 2 | T10:11 | Done/ (bellows) |
| 22 | parallel-plan-scope-check-collision-fix-2026-05-01 | 2 | 3 | T10:26 | halted (bellows) |
| 23 | phase-3c-plan-hash-drift-warning-2026-04-30 | 2 | 3 | T13:21 | Done/ (bellows) |
| 24 | planner-template-bellows-execution-model-section-2026-04-30 | 2 | 3 | T14:20 | Done/ (bellows) |
| 25 | planner-template-lessons-2026-05-01 | 2 | 3 | T10:54 | Done/ (bellows) |
| 26 | planner-template-lessons-step-numbering-2026-04-23 | 2 | 2 | T15:56 | Done/ (bellows) |
| 27 | revert-snapshot-fix-and-reopen-backlog-2026-05-01 | 3 | 4 | T10:41 | Done/ (bellows) |
| 28 | rule-25-verdict-content-spec-fix-2026-05-01 | 2 | 3 | T16:20 | Done/ (bellows) |
| 29 | verdict-mechanization-distribution-audit-2026-04-30 | 1 | 2 | T15:08 | Done/ (bellows) |

Additionally: **493 rows** with empty/null `plan_slug` — pre-Phase-3b rows (before 2026-04-28). Harmless; `_get_last_completed_step` filters by slug = '' which returns None.

### Bucket Summary

| Bucket | Description | Count |
|--------|-------------|-------|
| (a) Active (in-progress, verdict-pending) | 0 | (the current diagnostic has no DB slug) |
| (b) Done/ | 22 |
| (c) Halted | 4 |
| (d) Pure orphan (no matching plan) | **0** |
| Pre-3b (no slug) | 493 rows (legacy) |

**Zero pure orphans.** Every slug in the DB has a matching plan file in some watched project's decisions/ tree. However, this is misleading — the bug does NOT require orphan rows. It requires a same-slug collision: two distinct plans (different content, different sessions) sharing a slug, where the earlier plan's DB rows are still present when the later plan is dispatched. This is precisely what happened with `bellows-session-wrap-2026-05-01`.

DB rows for terminal-state plans (Done/, halted) are **never cleared.** If a plan with slug `X` completes and its rows persist, and a new plan with slug `X` is deposited later (e.g., the next day's session wrap), the DB resume logic will find the old rows and trigger phantom resume — **provided a shadow cache file also exists** (the guard condition).

---

## Q6 — Cost-Benefit of Phase 3b/3c

### Q6a — Original Failure Mode

**BACKLOG closure text** (BACKLOG.md line 69):
> **Closed 2026-04-30 (hygiene):** BACKLOG `2026-04-18: step state lost across re-claim`. Superseded by BACKLOG #6 Phase 3b (DB-based step state recovery, shipped 2026-04-28: `plan_slug` column added to `runs` table; `_get_last_completed_step(db_path, plan_slug)` helper added; `run_plan()` now queries DB for last completed step when `resume_step is None` and shadow cache exists) and Phase 3c (plan-hash drift warning, shipped 2026-04-30).

**Phase 3b shipping plan** (Context section):
> Phase 3b implementation per the design at `bellows/knowledge/architecture/step-state-resume-design-2026-04-28.md`. Closes BACKLOG #6 ("step state lost across re-claim") via Hybrid 1+3 Option A: persist step completion in `bellows.db` keyed by canonical plan slug, query the DB on re-claim to determine resume step.

**Phase 3c shipping plan** (Context section):
> When a plan is re-claimed for resume (verdict-pending → continue verdict → resume at step N+1), the shadow cache holds the pristine plan content from the original claim. If the CEO edited the plan file between Step N's pause and the resume, the on-disk plan text now differs from the shadow. [...] A renumbered plan (step inserted/deleted in the middle) would dispatch the wrong step content.

**Original failure mode:** Plan state lost during re-claim. If a plan paused mid-execution and was re-dispatched, Bellows had no way to know which step was last completed. Phase 3b's DB resume logic solved this by persisting step completion in the DB and querying on re-claim. Phase 3c added a hash-drift warning for content changes between sessions.

### Q6b — Is the Failure Mode Still Possible?

**No.** The supported resume protocol is verdict-only (Rule 25). In the verdict-resume path (`_consume_verdicts` L757):
```python
self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```
`resume_step` is explicitly set from the verdict metadata. The DB is never consulted. The verdict file itself encodes which step completed — step state is carried through the verdict system, not the DB.

The manual-rename path Phase 3b was designed for (rename `verdict-pending-*` back to `executable-*`) is documented as unsupported. **There are zero instances** in the DB of a plan resuming via the Phase 3b DB-query path legitimately — every multi-step resume visible in the data used the verdict-resume path (explicit `resume_step` via `_consume_verdicts`).

The Phase 3b canary (`canary-phase-3b-restart-2026-04-30`) tested that the DB *stores* the slug and that `_get_last_completed_step` *returns* the correct value. It did NOT test a live end-to-end resume via the DB-query path. The mechanism works in isolation but is not used by any supported workflow.

### Q6c — Bug Rate

- **1 phantom-resume bug** observed in this session (2026-05-01, `bellows-session-wrap-2026-05-01`). Halted via verdict; re-deployed as `-v2` with unique slug.
- **0 other instances** of "DB resume" producing wrong behavior found in:
  - `verdicts/ledger.jsonl` — single entry for this slug is the halt verdict at T20:52
  - QA reports in `knowledge/qa/` — only mentions are in the Phase 3b QA report (expected test behavior) and the v2 wrap QA (documenting the bug)
  - Log files — `DB resume` appears in logs from 2026-04-28 onward (Phase 3b shipped), but all appear to be the canary or test scenarios, not production collisions
- **The v2 plan** (`bellows-session-wrap-v2-2026-05-01`) did NOT consume the orphan DB row — it used a different slug. The orphan rows for the original slug **are still in the DB** (rows 554-556, 570-571).
- **Collision trigger conditions:** Same-day same-slug-pattern collision + shadow cache present from prior plan. Rare in practice (requires depositing a plan with the same date-slug as a prior incomplete plan), but failure mode is silent and confusing — the plan runs step 3 with no step 1/2 deliverables.

### Q6d — Fix Shape Evaluation

#### F1: Patch — Key by `(slug, plan_hash)`
- **Pros:** Different plans with the same slug can never collide.
- **Cons:** `plan_hash` column does not exist in DB (Phase 3c computes hashes at runtime only). Would require schema migration + recording hash in `record_run()`. Adds complexity to guard a path that's not used by any supported workflow. Hash sensitivity to whitespace or trivial edits could prevent legitimate resume (if the manual-rename path were still supported, which it isn't).
- **Estimated LOC:** 15-25 (new column, migration, record_run update, query update).
- **Verdict:** Over-engineered for a dead path.

#### F2: Simplify — Make Phase 3c Hash-Drift Warning Blocking
- **Pros:** Simple (2-5 LOC — set `resume_step = None` when hash mismatch detected). Would have prevented the observed bug.
- **Cons:** Guards a path that's not used. If a plan IS legitimately re-dispatched with the same slug AND same content, this doesn't help (same hash = no warning = resume from orphan state). Legitimate same-plan edits between sessions force fresh restart (acceptable under verdict-only protocol since that path doesn't use DB resume anyway).
- **Verdict:** Treats the symptom, not the disease.

#### F3: Remove — Revert Phase 3b/3c Resume Logic
- **Pros:** Eliminates the entire bug class. Removes dead code — the manual-rename path Phase 3b guards is unsupported (Rule 25). The verdict-resume path never uses `_get_last_completed_step`. Zero operational impact on any supported workflow.
- **What to remove:** The DB-resume block (`bellows.py:243-247`), the Phase 3c hash-drift block (`bellows.py:249-254`), and the `_get_last_completed_step` function definition (`bellows.py:175-188`). Total: ~20 LOC removed.
- **What to KEEP:** `plan_slug` column in `runs` (useful for analytics/debugging), `record_run()` passing `plan_slug` (recording is still valuable), shadow cache system (used for metadata extraction, step counting, and prompt routing — all still needed).
- **Cons:** If the manual-rename resume path is ever re-enabled, DB resume would need to be re-implemented. This is acceptable — Rule 25 structurally prevents that path, and if the protocol changes, the feature can be rebuilt with the slug-collision fix baked in.
- **Estimated LOC:** ~20 lines removed, 0 added.
- **Verdict:** Clean, minimal, evidence-driven.

#### F4: Other — Shadow Cleanup on Terminal State
- Not needed as standalone fix. The shadow IS cleaned up on halt/done. The bug occurs when a new plan is deposited while the OLD plan is still in verdict-pending (shadow intact). Adding shadow cleanup to the verdict-pending transition would break the verdict-resume path (which reads shadow for metadata).

### Recommendation: **F3 (Remove)**

**Rationale:**
1. Phase 3b/3c guards a manual-rename resume path that is unsupported (Rule 25 verdict-only protocol).
2. The supported verdict-resume path passes `resume_step` explicitly and never consults the DB.
3. The only observable production effect of Phase 3b's DB-resume logic is the phantom-resume bug.
4. Zero legitimate uses of the DB-resume path exist in the operational history.
5. The `plan_slug` column and `record_run()` recording are independently valuable for analytics and should be kept.
6. Removal is the smallest change (~20 LOC deleted) with the largest impact (eliminates the bug class entirely).

**Tradeoffs:** Loss of crash-recovery resume (if daemon dies mid-step and plan is stranded as `in-progress-*`). But this was never Phase 3b's design intent, and the stranded-plan recovery gap exists regardless of Phase 3b (Rule 25 provides no recovery path for `in-progress-*` plans after daemon crash).
