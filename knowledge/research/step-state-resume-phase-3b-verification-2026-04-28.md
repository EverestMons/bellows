# Step-State Resume — Phase 3b Implementation Verification

**Date:** 2026-04-28 | **Agent:** Bellows Systems Analyst | **Step:** 1

---

## 1. Executive Summary

All design anchors in `knowledge/architecture/step-state-resume-design-2026-04-28.md` are **accurate** against the current codebase. The BACKLOG #2 fix (commit `3ca8361`, `gates.py`) and BACKLOG #4 fix (commit `7886a1c`, `_capture_git_diff()`) landed in code regions disjoint from the design's integration points — no line drift occurred. Every function signature, DDL statement, call site, and line number referenced in the design matches the current source exactly. One finding requires attention: the live `bellows.db` schema has 3 legacy columns (`cost_usd`, `started_at`, `completed_at`) not present in the code DDL, but this does not block Phase 3b because `migrate_db()` adds missing columns idempotently without removing extras. No naming conflicts, no circular import risks, and no contradictions with the locked design.

---

## 2. Q1 — `record_run()` Current Location and Shape

**Signature** — line 140:
```python
def record_run(
    db_path: str,
    plan_path: str,
    project: str,
    session_id: str,
    step: int,
    status: str,
    cost: float,
):
```

**DDL** — lines 151–160 (inside `record_run()`):
```sql
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    plan_path TEXT,
    project TEXT,
    session_id TEXT,
    step INTEGER,
    status TEXT,
    cost REAL
)
```

**INSERT** — lines 162–164:
```python
conn.execute(
    "INSERT INTO runs (timestamp, plan_path, project, session_id, step, status, cost) VALUES (?, ?, ?, ?, ?, ?, ?)",
    (datetime.now().isoformat(), plan_path, project, session_id, step, status, cost),
)
```

**Columns in DDL:** `id`, `timestamp`, `plan_path`, `project`, `session_id`, `step`, `status`, `cost` (8 columns).

**Design vs. actual:** Design claims signature ~line 140, DDL at line 151, INSERT at lines 162–164. All match exactly.

**Note:** There is a second DDL in `migrate_db()` at lines 41–51 that also defines the `runs` table. Phase 3b must update BOTH DDLs and add `plan_slug` to the `additions` dict at lines 54–62 of `migrate_db()`.

---

## 3. Q2 — `record_run()` Call Sites

| # | Line | Calling Function | Status Passed |
|---|------|-----------------|---------------|
| 1 | 269 | `run_plan()` | `parsed["receipt_status"]` (step complete) |
| 2 | 307 | `run_plan()` | `"VerdictPending"` (mid-plan pause) |
| 3 | 327 | `run_plan()` | `parsed["receipt_status"]` (multi-step loop) |
| 4 | 365 | `run_plan()` | `"VerdictPending"` (final-step pause) |

**Design vs. actual:** Design claims 4 call sites at lines 269, 307, 327, 365, all inside `run_plan()`. All match exactly. No call sites outside `run_plan()`.

---

## 4. Q3 — `run_plan()` Integration Points

**(a) Function definition** — line 190:
```python
def run_plan(plan_path: str, config: dict, response_server: server.ResponseServer, resume_step: Optional[int] = None):
```

**(b) Shadow cache load** — line 215:
```python
        shadow_text = _read_shadow(plan_filename)
        if shadow_text is not None:
            metadata_text = shadow_text
```

**(c) Atomic claim move** — lines 231–233:
```python
        if not plan_filename.startswith("in-progress-"):
            shutil.move(plan_path, inprogress_path)
            plan_path = inprogress_path
```

**(d) Bootstrap prompt construction** — lines 252–257:
```python
        if is_diagnostic:
            bootstrap_prompt = f"Read the diagnostic at {shadow_prompt_path}. ..."
        elif resume_step is not None:
            bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {resume_step}. ..."
        else:
            bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step 1 ONLY. ..."
```

**Design vs. actual:** Design says definition ~190 ✓, shadow ~215 ✓, claim ~231 ✓ (the `if` is 231, `move` is 232), bootstrap ~252 ✓. All match.

---

## 5. Q4 — `_slug_from_path()` Current Shape

Lines 65–75 of `verdict.py`:
```python
def _slug_from_path(plan_path):
    """Extract a slug from a plan path for use in verdict filenames."""
    basename = os.path.basename(plan_path)
    # Strip common prefixes
    for prefix in ("in-progress-", "verdict-pending-", "executable-", "diagnostic-"):
        if basename.startswith(prefix):
            basename = basename[len(prefix):]
    # Strip .md extension
    if basename.endswith(".md"):
        basename = basename[:-3]
    return basename
```

**Prefixes stripped:** `in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`
**`halted-` stripped?** No.
**Edge case:** Calling `_slug_from_path()` on `halted-foo-bar.md` yields slug `foo-bar` — WRONG, it would yield `halted-foo-bar`. However, as the design notes (Open Q#2), `record_run()` is only called from `run_plan()` where the path is always `in-progress-*`, so this edge case does not arise in current code.
**Visibility:** Private (leading underscore `_slug_from_path`). Design correctly identifies this at lines 65–75.

**Pre-existing cross-module usage:** `bellows.py` already calls `verdict._slug_from_path()` at 3 locations:
- Line 384 (auto-close cleanup)
- Line 779 (startup orphan sweep)
- Line 781 (startup orphan sweep)

This means the cross-module dependency `bellows.py → verdict._slug_from_path` already exists. Decision 3 (new shared util module) remains architecturally valid but is not forced by import direction — the existing direction is `bellows.py → verdict.py`, not the reverse.

---

## 6. Q5 — `runs` Table Live Schema

```
(0, 'id',           'INTEGER', 0, None, 1)   # PK
(1, 'plan_path',    'TEXT',    0, None, 0)
(2, 'project',      'TEXT',    0, None, 0)
(3, 'session_id',   'TEXT',    0, None, 0)
(4, 'step',         'INTEGER', 0, None, 0)
(5, 'status',       'TEXT',    0, None, 0)
(6, 'cost_usd',     'REAL',    0, None, 0)   # LEGACY — not in code DDL
(7, 'started_at',   'TEXT',    0, None, 0)   # LEGACY — not in code DDL
(8, 'completed_at', 'TEXT',    0, None, 0)   # LEGACY — not in code DDL
(9, 'timestamp',    'TEXT',    0, None, 0)
(10, 'cost',        'REAL',    0, None, 0)
```

**Drift analysis:** Live DB has 11 columns; code DDL has 8. Three legacy columns (`cost_usd`, `started_at`, `completed_at`) persist in the live DB from an earlier schema version but are not referenced in current code. The `INSERT` statement only writes to the 7 non-PK columns it knows about — extra columns default to NULL.

**Phase 3b impact:** Not blocking. `migrate_db()` uses an idempotent add-if-missing pattern (lines 52–66). Adding `plan_slug` to the `additions` dict will cause it to be added on next startup if missing. Legacy columns are inert — they don't interfere with new queries.

---

## 7. Q6 — Diagnostic Plan Handling

**Detection** — line 221:
```python
is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")
```

**Force `total_steps = 1`** — lines 223–224:
```python
if is_diagnostic:
    total_steps = 1
```

**Shadow cache on plan completion — traced across all exit paths:**

| Exit Path | Shadow Deleted? | Line |
|-----------|----------------|------|
| Auto-close (all gates pass) | Yes — `_delete_shadow(plan_filename)` | 387 |
| Zero-steps skip | Yes — `_delete_shadow(plan_filename)` | 244 |
| Continue-to-done (verdict) | Yes — `_delete_shadow(original_name)` | 698 |
| Halt (verdict) | Yes — `_delete_shadow(original_name)` | 716 |
| VerdictPending (mid-plan) | No — shadow preserved for resume | — |
| VerdictPending (final step) | No — shadow preserved for verdict review | — |

**Design assumption verified:** When a diagnostic plan completes and moves to Done, the shadow cache IS deleted. A fresh diagnostic re-dispatch would have `shadow_text is None`, so the proposed Deliverable 3 guard (`if resume_step is None and shadow_text is not None`) would correctly NOT fire. DB resume cannot accidentally trigger on a fresh diagnostic.

---

## 8. Q7 — Pre-existing Slug Code or Naming Conflicts

| Name | Exists? | Location | Conflict? |
|------|---------|----------|-----------|
| `slug` | Yes | Line 127, parameter of `_cleanup_verdicts_for_slug()` | No — local parameter, different function |
| `plan_slug` | Yes | Line 629, local variable in `_consume_verdicts()` | No — local variable scope, no collision with new `record_run()` parameter |
| `_get_last_completed_step` | No | — | No conflict |
| `slug_from_path` | No | — | No conflict (only `_slug_from_path` exists in verdict.py) |

**Assessment:** No naming conflicts. The design's new function `_get_last_completed_step` and new parameter `plan_slug` for `record_run()` can be added without renaming.

---

## 9. Q8 — Import Graph Between Core Modules

```
bellows.py ──→ verdict.py    (verdict.post_verdict_request, verdict.check_verdict,
                              verdict.log_to_ledger, verdict._slug_from_path)
bellows.py ──→ gates.py      (gates.check, gates._parse_plan_header)
bellows.py ──→ parser.py     (parser — imported but called indirectly via runner)

verdict.py ──→ (none of the core four — only stdlib)
gates.py   ──→ (none of the core four — only stdlib)
parser.py  ──→ (none of the core four — only stdlib)
```

**Key observation:** All edges flow outward from `bellows.py`. There is NO `verdict.py → bellows.py` edge. A new `slug.py` module would be imported by both `bellows.py` and `verdict.py` — no circular import risk. The import graph remains a DAG.

**Decision 3 context:** D3 was resolved as "new shared util module." The verification confirms this is architecturally clean. However, the simpler alternative (importing `_slug_from_path` directly from `verdict.py`) would also work since the dependency direction is already `bellows.py → verdict.py` and `bellows.py` already calls `verdict._slug_from_path()` at 3 locations. D3 is locked — this is noted for context only, not as a recommendation.

---

## 10. Anchor Drift Table

| Design Reference | Design Line | Current Line | Drift Severity |
|---|---|---|---|
| `record_run()` signature | ~140 | 140 | None |
| `record_run()` DDL | 151 | 151 | None |
| `record_run()` INSERT | 162–164 | 162–164 | None |
| `record_run()` call site 1 | 269 | 269 | None |
| `record_run()` call site 2 | 307 | 307 | None |
| `record_run()` call site 3 | 327 | 327 | None |
| `record_run()` call site 4 | 365 | 365 | None |
| `run_plan()` definition | ~190 | 190 | None |
| Shadow cache load (`shadow_text`) | ~215 | 215 | None |
| Atomic claim move (`shutil.move`) | ~231 | 231–232 | None |
| Bootstrap prompt construction | ~252 | 252 | None |
| `_slug_from_path()` | 65–75 | 65–75 | None |
| `is_runnable_plan()` | 469–472 | 469–472 | None |
| `_consume_verdicts` substring match | 667 | 667 | None |
| Halted rename in verdict consumer | 712–715 | 712–715 | None |
| Startup scan | 803–809 | 803–809 | None |
| Diagnostic `total_steps = 1` | 224 | 224 | None |

**All 17 anchors: zero drift.**

---

## 11. Implementation-Blocking Findings

**None.**

Minor notes for the executable author (not blocking):
1. **Dual DDL sites:** `record_run()` (line 151) and `migrate_db()` (line 41) both define the `runs` table DDL. Phase 3b must update both, plus add `plan_slug` to the `additions` dict (line 54).
2. **Live DB has legacy columns:** `cost_usd`, `started_at`, `completed_at` exist in the live DB but not in code. These are inert and don't affect Phase 3b.
3. **`_slug_from_path` already used cross-module:** `bellows.py` already calls `verdict._slug_from_path()` at 3 locations (lines 384, 779, 781). If D3 creates a new `slug.py` module, these existing call sites should also be updated for consistency.

---

## 12. Recommendation

The executable can proceed with the line anchors as written in the design. All 17 design references are accurate. No design revision is needed. The only implementation detail to watch is the dual-DDL pattern (two `CREATE TABLE` statements plus the migration dict) — the executable must update all three locations when adding the `plan_slug` column.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Verified all 17 line-number anchors and code references in the Phase 3b design document against the current codebase. Confirmed zero drift across all integration points. Analyzed the live DB schema, import graph, naming conflicts, shadow cache lifecycle, and diagnostic plan handling. Deposited structured findings with an anchor drift table.

### Files Deposited
- `bellows/knowledge/research/step-state-resume-phase-3b-verification-2026-04-28.md` — Phase 3b verification findings with anchor drift table

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Confirmed all design anchors are accurate — no design revision needed before Phase 3b
- Identified dual-DDL pattern as an implementation detail for the executable author (not blocking)

### Flags for CEO
- None — design anchors verified, executable can proceed as specified

### Flags for Next Step
- Dual DDL: Phase 3b executable must update `record_run()` DDL (line 151), `migrate_db()` DDL (line 41), AND `migrate_db()` additions dict (line 54) when adding `plan_slug` column
- Existing `verdict._slug_from_path()` call sites in `bellows.py` (lines 384, 779, 781) should be updated if D3 creates a new `slug.py` module
