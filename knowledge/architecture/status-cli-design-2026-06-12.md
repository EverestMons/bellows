# Status CLI Design — Single-Glance Observability Surface

**Date:** 2026-06-12 | **Author:** Bellows Systems Analyst | **Plan:** 31 | **FORWARD Row:** 2

---

## 1. Placement Decision (SA Authority)

**Decision: new `status.py` module at project root** (alongside `bellows.py`, `lifecycle.py`, `gates.py`, etc.).

Justification: the CLI is a read-only observer with zero daemon imports. Placing it in the project root follows the existing flat-module convention (`lifecycle.py`, `runner.py`, `notifier.py`). A standalone module means it can be invoked while the daemon is stopped, requires no `__init__.py` packaging, and cannot accidentally import daemon state. It imports only `sqlite3`, `fcntl`, `os`, `sys`, `datetime`, and `pathlib` — no bellows internals. Collocating with `bellows.py` also makes the invocation obvious.

**Invocation:** `python status.py` from the bellows project root.

---

## 2. Single-Glance Contract

The default output fits **one terminal screen (~40 lines max)** with zero scrolling for normal shop state. Five sections, top to bottom:

### Section A — Daemon Header (1 line)

```
● Bellows RUNNING  pid 48231  sha 5077b92  up 2h 16m
```

- Status indicator: `●` (green-capable) when running, `○` when stopped
- Daemon liveness via flock probe (see Data Contract)
- PID: derived from `lsof -t .bellows.lock` on macOS (best-effort; shows `—` if unavailable)
- SHA: `git log -1 --format=%h -- bellows.py` (matches the daemon's own fingerprint source)
- Uptime: derived from PID process start time via `ps -o lstart= -p <pid>` (shows `—` if PID unavailable)

When daemon is stopped: `○ Bellows STOPPED` (no PID/uptime fields).

### Section B — In-Flight (variable, 1 header + 1 row per active plan)

```
IN-FLIGHT
 #31  bellows   Step 1/3  running   41m  Status CLI (FORWARD Row 2: Obs…
 #30  govern…   Step 1/2  running   41m  Databases Out of Git (forge.db…
```

Columns: plan ID, target project (truncated to 8 chars), current step/total, step status, elapsed since step start, title (truncated to fill ~80-col terminal).

### Section C — Awaiting Verdict (conditional, only shown if any exist)

```
AWAITING VERDICT
 #14  forge     Step 2/3  qa_checkpoint  verdict-request-forge-backlog-step-2.md
```

Same first columns as In-Flight, plus the verdict-request filename (the actionable artifact the CEO needs to resolve).

When no plans are awaiting verdict: section omitted entirely (saves screen lines).

### Section D — Recent Completions (up to 5 today)

```
COMPLETED TODAY
 #29  18:15  $2.62  stop_prose Pattern Narrowing (Zero-True-Posit…
 #28  18:01  $3.20  Per-Plan Diff Baseline (Parallel-Plan scope_…
 #27  17:41  $2.45  Gate False-Positive Cluster Root Cause (scop…
 #26  17:28  $2.55  FORWARD Reconciliation + Staleness Sweep (Al…
 #25  16:51  $1.81  Session Wrap s2 (Phase 3 + Reliability Queue…
```

Columns: plan ID, closed time (HH:MM), cost (USD), title truncated. Capped at 5 most recent.

### Section E — Footer Totals (1 line)

```
Today: 26 plans  24 closed  2 in-flight  $53.27
```

### Line Budget

| Section | Lines |
|---|---|
| Daemon header | 1 |
| Blank separator | 1 |
| In-Flight header + rows | 1 + n (typically 1-3) |
| Blank separator | 1 |
| Awaiting Verdict header + rows | 0 (omitted) or 1 + n |
| Blank separator | 1 |
| Completed Today header + rows | 1 + min(5, closed_today) |
| Blank separator | 1 |
| Footer | 1 |
| **Typical total** | **~14 lines (2 in-flight, 0 awaiting, 5 completions)** |
| **Max before scrolling** | **~22 lines (5 in-flight, 5 awaiting, 5 completions)** |

Comfortably within the 40-line contract.

### Flags

- `--all`: show all plans today (not just last 5 completions). Adds `CLOSED` column count in completions header.
- `--watch N`: re-render every N seconds (default 5). Implemented with `time.sleep` + terminal clear. Omit from v1 if deemed non-trivial; the single-shot default is the priority.

---

## 3. The Mock (Load-Bearing Deliverable)

### Mock A — Daemon Running (real state at 2026-06-12 ~18:38 UTC)

```
● Bellows RUNNING  pid 48231  sha 5077b92  up 2h 16m

IN-FLIGHT
 #31  bellows   Step 1/3  running   41m  Status CLI (FORWARD Row 2: Obs…
 #30  govern…   Step 1/2  running   41m  Databases Out of Git (forge.db…

COMPLETED TODAY
 #29  18:15  $2.62  stop_prose Pattern Narrowing (Zero-True-Posit…
 #28  18:01  $3.20  Per-Plan Diff Baseline (Parallel-Plan scope_…
 #27  17:41  $2.45  Gate False-Positive Cluster Root Cause (scop…
 #26  17:28  $2.55  FORWARD Reconciliation + Staleness Sweep (Al…
 #25  16:51  $1.81  Session Wrap s2 (Phase 3 + Reliability Queue…

Today: 26 plans  24 closed  2 in-flight  $53.27
```

**14 lines total.** No AWAITING VERDICT section (none exist right now). PID and uptime are illustrative (derived at runtime).

### Mock B — Daemon Stopped

```
○ Bellows STOPPED

IN-FLIGHT
 (none)

COMPLETED TODAY
 #29  18:15  $2.62  stop_prose Pattern Narrowing (Zero-True-Posit…
 #28  18:01  $3.20  Per-Plan Diff Baseline (Parallel-Plan scope_…
 #27  17:41  $2.45  Gate False-Positive Cluster Root Cause (scop…
 #26  17:28  $2.55  FORWARD Reconciliation + Staleness Sweep (Al…
 #25  16:51  $1.81  Session Wrap s2 (Phase 3 + Reliability Queue…

Today: 26 plans  24 closed  0 in-flight  $53.27
```

**13 lines total.** In-flight shows `(none)` because without the daemon no plans can be actively running (DB state is stale snapshot; steps may show `running` in DB but daemon is dead, so CLI reports them as `(none)` — the daemon-stopped state is the authoritative signal).

Note on stopped + stale `running` rows: if the daemon is stopped but DB has steps with `status='running'`, the CLI should still show them under IN-FLIGHT with a `stale?` marker instead of hiding them, so the CEO can see what was interrupted. Revised Mock B with stale rows:

```
○ Bellows STOPPED

IN-FLIGHT
 #31  bellows   Step 1/3  stale?    41m  Status CLI (FORWARD Row 2: Obs…
 #30  govern…   Step 1/2  stale?    41m  Databases Out of Git (forge.db…

COMPLETED TODAY
 #29  18:15  $2.62  stop_prose Pattern Narrowing (Zero-True-Posit…
 #28  18:01  $3.20  Per-Plan Diff Baseline (Parallel-Plan scope_…
 #27  17:41  $2.45  Gate False-Positive Cluster Root Cause (scop…
 #26  17:28  $2.55  FORWARD Reconciliation + Staleness Sweep (Al…
 #25  16:51  $1.81  Session Wrap s2 (Phase 3 + Reliability Queue…

Today: 26 plans  24 closed  2 in-flight  $53.27
```

**14 lines.** The `stale?` marker replaces `running` when daemon is stopped, signaling these were in-flight when the daemon died/was stopped.

---

## 4. Data Contract

### 4a. Flock Probe (Daemon Liveness)

```python
import fcntl, os

def probe_daemon(lock_path):
    """Returns True if daemon is running (lock held), False if stopped."""
    if not os.path.exists(lock_path):
        return False
    fd = os.open(lock_path, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Lock acquired — no daemon holds it
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except (BlockingIOError, OSError):
        # Lock held by another process — daemon is running
        return True
    finally:
        os.close(fd)
```

Lock path: `<bellows_root>/.bellows.lock` (matches `bellows.py` line 1838).

### 4b. PID Derivation (best-effort, macOS)

```python
import subprocess

def get_daemon_pid(lock_path):
    """Best-effort PID from lsof. Returns int or None."""
    try:
        result = subprocess.run(
            ["lsof", "-t", lock_path],
            capture_output=True, text=True, timeout=5
        )
        pids = result.stdout.strip().splitlines()
        return int(pids[0]) if pids else None
    except Exception:
        return None
```

### 4c. Uptime Derivation (best-effort, macOS)

```python
import subprocess, datetime

def get_uptime(pid):
    """Process start time → uptime string. Returns str or None."""
    try:
        result = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True, text=True, timeout=5
        )
        start_str = result.stdout.strip()
        if not start_str:
            return None
        start = datetime.datetime.strptime(start_str, "%c")
        delta = datetime.datetime.now() - start
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m"
    except Exception:
        return None
```

### 4d. DB Queries (all read-only, `?mode=ro`)

**Connection:**
```python
db_uri = f"file:{db_path}?mode=ro"
conn = sqlite3.connect(db_uri, uri=True)
conn.row_factory = sqlite3.Row
```

**In-Flight plans (Section B):**
```sql
SELECT p.id, p.target_project, p.title, p.total_steps, p.lifecycle_state,
       s.step_number, s.status, s.step_started_at
FROM plans p
LEFT JOIN steps s ON s.plan_id = p.id
  AND s.step_number = (
    SELECT MAX(s2.step_number) FROM steps s2
    WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
  )
WHERE p.lifecycle_state IN ('in_progress', 'claimed')
ORDER BY p.id;
```

**Awaiting Verdict plans (Section C):**
```sql
SELECT p.id, p.target_project, p.title, p.total_steps,
       s.step_number, s.status
FROM plans p
JOIN steps s ON s.plan_id = p.id AND s.status = 'awaiting_verdict'
WHERE p.lifecycle_state = 'awaiting_verdict'
ORDER BY p.id;
```

Verdict-request filename: derived from slug convention: `verdict-request-<slug>-step-<n>.md`. Verify existence by scanning `verdicts/pending/`.

**Completed Today (Section D):**
```sql
SELECT p.id, p.title, p.closed_at, SUM(s.cost_usd) as cost
FROM plans p
JOIN steps s ON s.plan_id = p.id
WHERE p.lifecycle_state = 'closed'
  AND p.closed_at >= date('now')
GROUP BY p.id
ORDER BY p.closed_at DESC
LIMIT 5;
```

(`--all` flag: remove the `LIMIT 5`.)

**Footer Totals (Section E):**
```sql
SELECT COUNT(*) as total,
       SUM(CASE WHEN lifecycle_state = 'closed' THEN 1 ELSE 0 END) as closed,
       SUM(CASE WHEN lifecycle_state IN ('in_progress', 'claimed') THEN 1 ELSE 0 END) as in_flight
FROM plans
WHERE created_at >= date('now');

SELECT SUM(cost_usd) as total_cost
FROM steps s
JOIN plans p ON s.plan_id = p.id
WHERE p.created_at >= date('now');
```

### 4e. Degradation: DB Absent

If `lifecycle.db` does not exist at the expected path:
```
○ Bellows STOPPED  (no lifecycle.db)

No data available — lifecycle.db not found at <path>.
Run the daemon at least once to initialize the database.
```

3 lines total. The CLI exits 0 (not an error — fresh install is a valid state).

### 4f. Root Resolution

Use `bellows_root.py::resolve_bellows_root()` to find the canonical bellows root (handles worktree execution). DB path: `<root>/lifecycle.db`. Lock path: `<root>/.bellows.lock`.

---

## Layer Impact

**Layer 1 (Bellows):** new read-only observer module; no changes to dispatch, gates, or verdict flow.
**Layer 2 (Agents):** unaffected.
**Layer 3 (Planner):** unaffected.

No responsibility shift between layers. The CLI is pure observation.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Designed the single-glance status CLI: placement decision (standalone `status.py` at project root), output format (5 sections, 14 lines typical, 40-line max), two mocks rendered from real lifecycle.db state, and complete data contract (flock probe, read-only queries, degradation).

### Files Deposited
- `knowledge/architecture/status-cli-design-2026-06-12.md` — full CLI spec with mocks and data contract

### Files Created or Modified (Code)
- None (design step only)

### Decisions Made
- Standalone `status.py` at project root (SA authority: new module placement)
- `stale?` marker for in-flight rows when daemon is stopped (observation accuracy over hiding data)
- PID/uptime as best-effort fields (graceful `—` fallback)
- `--watch` deferred to v1 assessment (not guaranteed in initial implementation)

### Flags for CEO
- Mock A and Mock B are the acceptance targets for Step 2. Approve, adjust, or redirect at the pause.

### Flags for Next Step
- The Developer should match the mock output structurally; live values will differ.
- `bellows_root.py::resolve_bellows_root()` is the canonical root resolver — import it, don't reimplement.
- All DB access must use `?mode=ro` URI — the CLI must never write.
