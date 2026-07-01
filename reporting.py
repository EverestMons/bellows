"""Cycle reporting queries — read-only observer of Bellows lifecycle data.

Throughput and cost aggregates over time-windowed lifecycle.db data.
All DB access is read-only (?mode=ro). Never imports daemon internals.
"""

import sqlite3


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
