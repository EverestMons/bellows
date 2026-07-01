# Reporting Phase 2 — Read-Side Cycle Query Module Blueprint

**Date:** 2026-07-01
**Author:** Bellows Systems Analyst
**Plan:** 110
**Scope:** Throughput + cost spine — range-parameterized query over lifecycle.db

---

## 1. Design Rationale

### Why a new module (`reporting.py`), not `status.py`

`status.py` has a single-responsibility docstring: *"Renders exactly three elements: daemon header, IN-FLIGHT, AWAITING VERDICT."* A cycle report is a fundamentally different read concern — it summarizes closed plans over a time window rather than showing live daemon state. Adding cycle queries to `status.py` would violate that contract and blur two distinct responsibilities.

The new module `reporting.py` follows the exact same integration pattern as `status.py`:
- Importable query helper functions
- All DB access read-only (`?mode=ro`)
- Never imports daemon internals (bellows.py, runner.py, etc.)
- Uses `lifecycle.db` via a `db_path` parameter

### Design Constraints (verified against live DB 2026-07-01)

1. **Timestamp-keyed, not state-keyed.** `plans.lifecycle_state` only holds terminal values in practice (closed 94, halted 11, abandoned 4). Intermediate states (`claimed`/`in_progress`/`awaiting_verdict`) are never retained. The query windows on `plans.closed_at` (109/110 rows populated — only the single in_progress plan is NULL).

2. **Counting-grain separation.** The `plans → steps` join inflates row count: 69 executable plans produce 142 step rows. Plan counts MUST use `COUNT(DISTINCT p.id)`. Cost and turn sums (`SUM(s.cost_usd)`, `SUM(s.turns)`) stay on the step-grain join — they are naturally additive across steps.

3. **Range-parameterized `[start, end)`.** No cycle-boundary state exists. The query takes an arbitrary half-open date range on `closed_at`. Named calendar cycles (weekly, monthly) are a later layer — out of scope.

---

## 2. File Placement

```
bellows/reporting.py     # new module — cycle query helpers
bellows/tests/test_reporting.py  # new test file
```

---

## 3. Function Signature

```python
def query_cycle_report(db_path: str, start: str, end: str) -> list[dict]:
    """Return throughput + cost rows for plans closed in [start, end).

    Parameters
    ----------
    db_path : str
        Path to lifecycle.db.
    start : str
        ISO-8601 date or datetime string (inclusive lower bound on closed_at).
    end : str
        ISO-8601 date or datetime string (exclusive upper bound on closed_at).

    Returns
    -------
    list[dict]
        Each dict has keys:
          - target_project: str
          - type: str ('diagnostic' | 'executable')
          - plan_count: int          (plan-grain: COUNT(DISTINCT p.id))
          - total_cost_usd: float    (step-grain: SUM of step costs)
          - total_turns: int         (step-grain: SUM of step turns)
        Rows are ordered by target_project ASC, type ASC.
        If no plans match, returns an empty list.
    """
```

### Why `list[dict]` not `list[sqlite3.Row]`

`sqlite3.Row` objects are tied to the connection and column indices. Returning plain dicts makes the function easy to test, serialize, and compose with downstream formatters without coupling callers to sqlite3 internals. This also matches the pattern where `status.py` uses `sqlite3.Row` only inside its own render functions — reporting callers will be external.

---

## 4. Exact SQL

```sql
SELECT
    p.target_project,
    p.type,
    COUNT(DISTINCT p.id)    AS plan_count,
    COALESCE(SUM(s.cost_usd), 0.0) AS total_cost_usd,
    COALESCE(SUM(s.turns), 0)      AS total_turns
FROM plans p
LEFT JOIN steps s ON s.plan_id = p.id
WHERE p.closed_at >= ?
  AND p.closed_at < ?
GROUP BY p.target_project, p.type
ORDER BY p.target_project, p.type
```

### Aggregate grain notes

| Aggregate | Grain | Why |
|---|---|---|
| `COUNT(DISTINCT p.id)` | plan | The LEFT JOIN to steps duplicates plan rows; DISTINCT collapses back to plan count |
| `SUM(s.cost_usd)` | step | Each step row contributes its own cost; sum over the join is correct |
| `SUM(s.turns)` | step | Same — each step row has its own turn count |
| `COALESCE(..., 0)` | — | Ensures zero (not NULL) when all step values are NULL or no steps exist |

### Why LEFT JOIN (not INNER JOIN)

A plan with zero steps (edge case: minted but never started before being closed) should still appear in plan counts with zero cost/turns, not be silently excluded.

### Why no `lifecycle_state` filter

Per constraint (1): we window purely on `closed_at`. Plans with `closed_at IS NOT NULL` are by definition terminal. Adding a `lifecycle_state IN (...)` filter would be redundant and would create a maintenance hazard if new terminal states are added later.

---

## 5. Implementation Pattern

```python
"""Cycle reporting queries — read-only observer of Bellows lifecycle data.

Throughput and cost aggregates over time-windowed lifecycle.db data.
All DB access is read-only (?mode=ro). Never imports daemon internals.
"""

import sqlite3


def query_cycle_report(db_path: str, start: str, end: str) -> list[dict]:
    db_uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            p.target_project,
            p.type,
            COUNT(DISTINCT p.id)           AS plan_count,
            COALESCE(SUM(s.cost_usd), 0.0) AS total_cost_usd,
            COALESCE(SUM(s.turns), 0)      AS total_turns
        FROM plans p
        LEFT JOIN steps s ON s.plan_id = p.id
        WHERE p.closed_at >= ?
          AND p.closed_at < ?
        GROUP BY p.target_project, p.type
        ORDER BY p.target_project, p.type
        """,
        (start, end),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
```

### CLI entry point (optional, in `reporting.py`)

A `main()` function provides a quick CLI for ad-hoc queries:

```python
if __name__ == "__main__":
    import sys
    from bellows_root import resolve_bellows_root

    if len(sys.argv) != 3:
        print("Usage: python reporting.py <start> <end>")
        print("  Dates are ISO-8601 (e.g. 2026-06-01 2026-07-01)")
        sys.exit(1)

    db_path = str(resolve_bellows_root() / "lifecycle.db")
    results = query_cycle_report(db_path, sys.argv[1], sys.argv[2])

    if not results:
        print("No plans closed in the given range.")
        sys.exit(0)

    print(f"{'Project':<20s} {'Type':<12s} {'Plans':>5s} {'Cost ($)':>10s} {'Turns':>6s}")
    print("-" * 55)
    for row in results:
        print(
            f"{row['target_project']:<20s} "
            f"{row['type']:<12s} "
            f"{row['plan_count']:>5d} "
            f"{row['total_cost_usd']:>10.2f} "
            f"{row['total_turns']:>6d}"
        )
```

---

## 6. Test Case List (for DEV — Step 2)

All tests use an in-memory lifecycle.db seeded via `init_lifecycle_db` + INSERT fixtures.

### Test 1: Multi-step executable — plan count not inflated

Seed a single executable plan with 3 steps (all complete, with cost/turns), closed within the query range. Assert `plan_count == 1`, not 3.

### Test 2: Cost/turn SUMs match hand-computed values

Seed 2 plans (1 diagnostic with 1 step, 1 executable with 2 steps) in the same project+type group. Hand-compute expected `total_cost_usd` and `total_turns`. Assert exact match.

### Test 3: Empty range returns empty list

Query a range that contains no closed plans. Assert `result == []`, not an error.

### Test 4: Half-open boundary `[start, end)`

Seed a plan whose `closed_at` is exactly equal to `end`. Assert it is excluded from results. Seed another plan whose `closed_at` is exactly equal to `start`. Assert it is included.

### Test 5: Groups by target_project and type

Seed plans across 2 projects and 2 types. Assert that the result contains the expected number of rows (up to 4 groups), each with correct counts.

### Test 6: Read-only access

Assert that `reporting.py` does not import any daemon modules. (Static check: `import reporting; assert 'bellows' not in dir(reporting)` — or grep-based.)

---

## 7. Deferred Scope (follow-on plans — NOT designed here)

These rollups build on the throughput+cost spine but require separate design work:

- **Gate pass/fail rates** — from `gate_events` table: per-plan gate outcomes, aggregate pass/fail ratios per window
- **Deposit-landed rates** — from `deposits` table: how many required deposits were actually produced per plan
- **Verdict-outcome distribution** — from `verdicts` table: outcome breakdown (proceed/revise/halt) per window
- **Diagnostic→executable lineage** — from `derivations` table: conversion rate from diagnostic findings to executable plans

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Designed the read-side cycle query module for Reporting Phase 2. Blueprint specifies file placement (`reporting.py`), function signature, exact SQL with grain-separated aggregates, implementation pattern matching `status.py`, and a 6-item test case list for Step 2.

### Files Deposited
- `knowledge/decisions/reporting-phase2-cycle-query-blueprint-2026-07-01.md` — full blueprint for DEV implementation

### Files Created or Modified (Code)
- None (design only — code ships in Step 2)

### Decisions Made
- New `reporting.py` module (not added to `status.py`) — justified by status.py's explicit single-responsibility docstring
- `list[dict]` return type over `list[sqlite3.Row]` — decouples callers from sqlite3 internals
- LEFT JOIN (not INNER) — preserves plan count for zero-step edge case
- No `lifecycle_state` filter — pure `closed_at` windowing per constraint (1)
- COALESCE to zero for NULL cost/turns — clean API contract

### Flags for CEO
- None

### Flags for Next Step
- The CLI `main()` is optional — DEV should implement it but it's not a gating requirement
- Test 6 (read-only access) can be a static import check or grep — DEV chooses the approach
