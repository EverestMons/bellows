# Daemon-Collision Recovery Race — Root Cause Analysis

**Date:** 2026-06-12 | **Plan:** 21 (diagnostic) | **FORWARD row:** 19
**Incident:** Concurrent daemon instance B misclassified actively-running plan 7 as `abandoned` at 11:31:55, ~3 seconds after instance A had claimed and renamed it.

---

## Section 1 — Recovery Logic Anatomy

### Function: `recover_half_claimed` at `lifecycle.py:190–236`

**Row selection** (`lifecycle.py:202–204`):
```python
rows = conn.execute(
    "SELECT id, type, deposit_placeholder_name FROM plans WHERE lifecycle_state = 'claimed'"
).fetchall()
```
Selects ALL plans globally with `lifecycle_state = 'claimed'`. There is **no filter on `target_project`** or any column that would scope the query to the `decisions_dir` argument. Every call sees every claimed plan in every project.

**Filesystem checks per candidate** (`lifecycle.py:206–233`):

For each `(plan_id, plan_type, deposit_name)`:

1. **Construct expected in-progress name** (`lifecycle.py:207`):
   `expected_name = f"in-progress-{plan_type}-{plan_id}.md"`

2. **Check 1 — in-progress file exists** (`lifecycle.py:208–216`):
   `expected_path = os.path.join(decisions_dir, expected_name)` — checks in the **caller-supplied** `decisions_dir`, not the plan's own `target_project` directory. If found → `already_renamed`, state → `in_progress`.

3. **Check 2 — deposit placeholder exists** (`lifecycle.py:218–227`):
   `deposit_path = os.path.join(decisions_dir, deposit_name)` — again in the caller-supplied directory. If found → `os.rename()` to in-progress name, state → `in_progress`, action → `re_renamed`.

4. **Fallthrough — abandoned** (`lifecycle.py:229–233`):
   Neither file found → state → `abandoned`, `closed_at` set. Action → `abandoned`.

**All changes are batched in a single `conn.commit()` at `lifecycle.py:234`** — they become visible to subsequent calls atomically.

### Decision tree and the `abandoned` misclassification paths

A plan whose `in-progress-<type>-<id>.md` EXISTS on disk can still be classified `abandoned` through these paths:

| # | Path to `abandoned` despite file existing | Mechanism |
|---|---|---|
| **P1** | **Wrong directory scanned (cross-project blind spot)** | The callsite (`bellows.py:1824–1826`) iterates `config["watched_projects"]` (10 directories). For each, calls `recover_half_claimed(decisions_path)`. The function queries ALL claimed plans globally. A plan from project X will have its in-progress file in X's decisions dir, but the function checks in whichever `decisions_dir` the caller passed. If project X's directory is NOT the first in the iteration, an earlier directory's call marks the plan abandoned. |
| **P2** | `target_project` mismatch — plan's `target_project` stores the project root (e.g., `/Users/marklehn/Developer/GitHub/bellows`), not the decisions directory. The function receives `decisions_dir` from the callsite. No join or lookup correlates the two. | Same mechanism as P1; the function has no way to filter plans by project. |
| **P3** | State filter selects the row before A's rename committed | If B's `SELECT` fires after A's `mint_and_claim` (which commits `lifecycle_state='claimed'`) but before A updates state, the row appears in the result set. Since A never writes `lifecycle_state='in_progress'` (FORWARD row 20), the row stays `claimed` indefinitely until close. |
| **P4** | Exception swallowed in `os.path.exists` | Theoretically possible but no evidence in logs. `os.path.exists` returns False on permission errors, but the decisions directories are world-readable. |

**P1 + P3 are the compound root cause for the 2026-06-12 incident** (confirmed in Section 2).

---

## Section 2 — Incident Forensics

### Interleaved Two-Daemon Timeline (11:30:30–11:34:00)

Sources: `logs/terminal/bellows-2026-06-12.log` (shared file handler, both instances write), `logs/terminal/nohup-restart-2026-06-12.out` (instance A's stdout/stderr).

| Time | Instance | Event | Source |
|---|---|---|---|
| 11:30:32 | A | Startup — `session log:` line, Flask binds `:5000`, "Watching 10 projects" banner | nohup log line 52; terminal log line 1 |
| 11:30:32 | A | Startup recovery runs — no claimed plans in DB (plans 1-6 are abandoned/closed) | Inferred: no recovery log lines between 11:30:32 and 11:31:52 |
| ~11:31:00 | B | Process starts in terminal (per incident report) | Diagnostic context |
| 11:31:52 | A | Detects `executable-draft-113110.md`, calls `mint_and_claim` → plan 7 created with `lifecycle_state='claimed'`, `created_at=2026-06-12T11:31:52.772799` | terminal log line 2–4; DB `plans.id=7` |
| 11:31:52 | A | `shutil.move()` renames deposit → `in-progress-executable-7.md` in `.../bellows/knowledge/decisions/` | terminal log line 4: "renamed to in-progress-executable-7.md" |
| 11:31:52 | A | **Does NOT update `lifecycle_state` to `in_progress`** — state remains `claimed` (FORWARD row 20 confirms intermediate states never written) | `bellows.py:446–466` — no `mark_plan_state` call after rename |
| 11:31:54 | A | Dispatches step 1 via `claude -p` | terminal log line 6 |
| 11:31:55 | B | Startup recovery: `lifecycle.recover_half_claimed()` called for each of 10 watched projects | `bellows.py:1823–1828` |
| 11:31:55 | B | **Recovery marks plan 7 as `abandoned`** | terminal log line 7: "lifecycle recovery: plan 7 — abandoned" |
| 11:31:55 | B | `── session restart ──` logged, `session log:` line | terminal log lines 8–9 |
| 11:31:55 | B | Flask attempts to bind `:5000` — fails (A holds it). Daemon thread dies silently; B continues without callback server. | `server.py:26–33` — `app.run()` in daemon thread; exception kills thread, main thread unaffected |
| 11:32:53 | A | Step 1 running (60s elapsed) | terminal log line 10 |
| ~11:33:00 | B | Killed manually by CEO | Diagnostic context |
| 11:34:33 | A | Step 1 gates pass, enters `awaiting_verdict` | terminal log line 12–13 |
| 11:59:19 | A | Plan 7 close: `mark_plan_state(7, "closed", ...)` overwrites `abandoned` → `closed` | terminal log line 40; DB confirms `lifecycle_state='closed'` |

### Root Cause Confirmation — Which Decision Tree Branch Fired

**The branch that fired: P1 (cross-project blind spot).**

Evidence chain:

1. `config.json` lists 10 `watched_projects`. Bellows is at **index 7** (0-based):
   ```
   [0] invoice-pulse/knowledge/decisions
   [1] BrewBuddy/knowledge/decisions
   ...
   [7] bellows/knowledge/decisions    ← plan 7 lives here
   [8] lessons-forge/knowledge/decisions
   [9] governance/knowledge/decisions
   ```

2. The startup recovery loop (`bellows.py:1824`) iterates in config order. The FIRST call is:
   `recover_half_claimed("/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions")`

3. This call queries `WHERE lifecycle_state = 'claimed'` — finds plan 7 (state still `claimed` because A never wrote `in_progress`, per P3).

4. Checks for `in-progress-executable-7.md` in **invoice-pulse's** decisions dir — **not found**.

5. Checks for `executable-draft-113110.md` in invoice-pulse's decisions dir — **not found**.

6. Falls through to `abandoned` branch. Executes:
   ```python
   UPDATE plans SET lifecycle_state = 'abandoned', closed_at = ? WHERE id = 7
   ```

7. `conn.commit()` makes the change visible.

8. When the loop reaches bellows's decisions dir (index 7), the `SELECT WHERE lifecycle_state = 'claimed'` no longer returns plan 7 — it's already `abandoned`.

**Contributing factor (P3):** A never updates `lifecycle_state` from `claimed` to `in_progress` after the rename. Even if B had only checked bellows's directory, the plan would be visible to recovery because it's still `claimed`. In a single-instance restart scenario this is harmless (no claimed plans survive a clean shutdown), but it enables the race with a concurrent daemon.

**Discriminating evidence:** The fact that the action is `abandoned` (not `already_renamed`) proves the file check failed. Since `in-progress-executable-7.md` existed in bellows's directory at 11:31:55 (A renamed it 3 seconds earlier), the only explanation is that the check ran against a different directory first.

---

## Section 3 — Collision Surface Census

Two daemon instances watching the same 10 projects. Enumeration of shared mutable surfaces:

| # | Surface | File:Line | Collision Behavior | Observed Today? | Severity |
|---|---|---|---|---|---|
| **(a)** | **Plan claiming — watcher + 30s rescan** | `bellows.py:430–466` (claim path), `bellows.py:1431–1452` (rescan) | Both instances run `watchdog.Observer` on same directories + 30s rescan. If both detect the same deposit: first to `shutil.move` wins, second gets `FileNotFoundError` (no exception handling around the move at `bellows.py:458`). `mint_and_claim` at `lifecycle.py:150` uses `BEGIN IMMEDIATE` — second writer blocks until first commits, both get unique IDs. Result: **double-mint** (two plan rows for one deposit) then one instance crashes on move. | No — plan 7 was claimed before B started | **High** |
| **(b)** | **Verdict consumption — `_consume_verdicts`** | `bellows.py:1477–1688` | Both instances scan `verdicts/resolved/`. Both see same verdict file. Both find the `verdict-pending-*` plan and process it. First `shutil.move` (plan file rename at `bellows.py:1625`) succeeds; second gets `FileNotFoundError` — unhandled, crashes the rescan. Additionally: double-dispatch risk if both reach `handle_new_plan` before either moves the file. Verdict file is renamed to `processed-*` at `bellows.py:1658` — second daemon's rename also fails. | No — B killed before any verdict consumed | **Critical** |
| **(c)** | **lifecycle.db writes** | `lifecycle.py` (all write functions) | WAL mode enabled (`lifecycle.py:28`). Two writers: `BEGIN IMMEDIATE` serializes transactions. No corruption risk from WAL, but `abandoned` written by B conflicts with A's runtime state. Close path at `bellows.py:1617` overwrites unconditionally — self-heals but only at plan close. | **Yes** — B wrote `abandoned`, A later wrote `closed` | **High** |
| **(d)** | **Shadow cache (`.bellows-cache/`)** | `bellows.py:230–260` | Both instances read/write same shadow directory. A writes shadow at claim (`bellows.py:466`), B's recovery doesn't touch shadow. In double-dispatch scenario, both could write shadow for the same plan — last-writer-wins, content identical. Deletion race on plan close is benign (`unlink` on missing file raises `FileNotFoundError` but `_delete_shadow` checks `exists()` first at `bellows.py:258`). | No | **Low** |
| **(e)** | **Port 5000 bind (Flask callback server)** | `server.py:26–33` | `app.run(host="0.0.0.0", port=5000)` in daemon thread. Second bind raises `OSError: Address already in use`. Thread dies; main thread continues. B runs without a callback server — can dispatch plans but **cannot receive CEO responses** via HTTP callback. B's `response_server.wait_for_response()` blocks forever on `queue.get(timeout=3600)`. | **Yes** — B's Flask thread died. B continued daemonless until manually killed. | **Medium** |
| **(f)** | **Startup recovery — `recover_half_claimed`** | `lifecycle.py:190–236`, `bellows.py:1823–1828` | B's recovery runs the global query and marks A's actively-running plan abandoned. This is the **observed incident**. | **Yes** — plan 7 marked abandoned | **High** |
| **(g)** | **bellows.db (legacy run DB)** | `bellows.py` (migrate_db, run tracking) | Both instances call `migrate_db()`. WAL mode; no corruption. Duplicate run entries possible but benign. | Not investigated | **Low** |
| **(h)** | **Session log file** | `bellows.py:1810–1818` | Both instances open `RotatingFileHandler` on same dated log path. `RotatingFileHandler` is not multi-process safe — interleaved writes possible. In practice, Python's `logging` flushes complete lines, so lines are intact but ordering is interleaved (observed in terminal log). | **Yes** — interleaved A/B lines in bellows-2026-06-12.log | **Low** |
| **(i)** | **Verdict pending/resolved directories** | `bellows.py:1690–1728` (startup sweep), verdict module | Both scan and potentially delete orphaned verdict requests. Race on `unlink()` — second caller gets `FileNotFoundError` if file already removed. Startup sweep at `bellows.py:1690` has no guard. | Not investigated in this incident window | **Medium** |

### Claim atomicity detail (surface a)

The rename (`shutil.move` at `bellows.py:458`) is atomic on the same filesystem (delegates to `os.rename`). However, the detection → mint → rename sequence is NOT atomic. Between detection and rename, another instance can detect the same file. The `mint_and_claim` DB transaction only serializes ID assignment — it does not prevent the second instance from attempting the same filesystem rename. The first mover wins; the second gets a crash.

---

## Section 4 — Fix Shapes

### (a) Correct `recover_half_claimed` existence check

**Fix:** Add project-awareness to the recovery function. Two sub-options:

**a1 — Filter query by directory:** Add `target_project` to the query and derive the expected decisions path from it. However, `target_project` stores the project root (e.g., `/Users/marklehn/Developer/GitHub/bellows`), not the decisions directory. The mapping `<root>/knowledge/decisions/` is a convention, not stored in the DB. This requires either storing the decisions path in the plans table or hardcoding the convention.

**a2 — Pass project filter to the function:** Change `recover_half_claimed(decisions_dir)` to join `target_project` with the known suffix, or add a `project_root` parameter and filter: `WHERE lifecycle_state = 'claimed' AND target_project = ?`. The callsite derives `project_root` from `decisions_path` by going up 2 levels (`pathlib.Path(decisions_path).parent.parent`).

| Aspect | Behavior |
|---|---|
| Crash without cleanup | Safe — next startup re-runs recovery, correctly scoped this time |
| Intentional restart | Safe — same as crash |
| Observed double-start | Partially mitigated — B's recovery only processes its own project's plans, but if both instances watch the same project, B still marks A's running plan as abandoned (because state is still `claimed`) |

**Limitation:** Does not prevent the race when two instances watch the SAME project. The `claimed` state persists because intermediate states are never written (FORWARD row 20).

### (b) Single-instance guard

Three mechanisms evaluated:

**b1 — Pidfile with liveness check:**
- On startup: read pidfile; if PID exists and process is alive (`os.kill(pid, 0)`), exit with error.
- Write own PID to pidfile. Remove on clean exit (atexit handler).
- **Crash without cleanup:** Stale pidfile left behind. Liveness check (`kill -0`) detects dead PID → proceeds. Risk: PID recycling (rare on macOS, PIDs go up to 99999).
- **Intentional restart:** Same — stale pidfile, liveness check passes.
- **Observed double-start:** B reads pidfile, finds A alive, refuses to start. **Prevents the incident.**

**b2 — Exclusive `flock` on a lockfile at BELLOWS_ROOT:**
- `fcntl.flock(fd, LOCK_EX | LOCK_NB)` on `BELLOWS_ROOT / ".bellows.lock"`.
- **Crash without cleanup:** OS automatically releases flock on process death. Next startup acquires immediately. **No stale state.**
- **Intentional restart:** Same — instant acquisition.
- **Observed double-start:** B's flock attempt returns `EWOULDBLOCK` → exit with error. **Prevents the incident.**
- Advantage over pidfile: no stale-state risk, no PID-recycling risk.

**b3 — Bind-port-5000-first-or-exit (fail-fast):**
- Move `ResponseServer.start()` before recovery and the main loop. If bind fails, exit immediately.
- **Crash without cleanup:** OS releases socket on process death. No stale state.
- **Intentional restart:** Same — instant rebind.
- **Observed double-start:** B's bind fails → exits before running recovery. **Prevents the incident.**
- Advantage: uses existing infrastructure. No new files or abstractions.
- Disadvantage: couples the single-instance guard to the Flask port. If the port changes or the server is disabled, the guard breaks.

| Mechanism | Stale-state risk | Crash recovery | Implementation complexity |
|---|---|---|---|
| b1 (pidfile) | PID recycling (low) | Liveness check | Low |
| b2 (flock) | None | OS releases | Low |
| b3 (bind-first) | None | OS releases | Minimal (reorder existing code) |

### (c) Defense-in-depth: recovery age guard

Add a time-based guard to `recover_half_claimed`: refuse to mark `abandoned` any plan whose `created_at` is younger than N minutes.

```python
# In the fallthrough branch, before marking abandoned:
if created_at and (datetime.now() - datetime.fromisoformat(created_at)).total_seconds() < N * 60:
    actions.append((plan_id, "skipped_too_recent"))
    continue
```

Requires adding `created_at` to the SELECT query.

- N = 5 minutes: covers the observed race window (3 seconds) with wide margin. Plans genuinely abandoned by a crash within 5 minutes would be recovered on next restart after the window expires.
- **Crash without cleanup:** Plan stays `claimed` for N minutes. Next startup after the window classifies correctly.
- **Intentional restart:** Same.
- **Observed double-start:** B's recovery skips plan 7 (created 3 seconds ago < 5 minutes). **Prevents the misclassification.**

### Recommendation

**Ship all three in combination (defense-in-depth):**

1. **b2 (flock)** as the primary single-instance guard — prevents all collision surfaces (a–i), not just recovery. Fail-fast, no stale state, minimal code.
2. **a2 (project-scoped recovery query)** — fixes the cross-project blind spot even in hypothetical scenarios where two separate Bellows instances legitimately watch disjoint project sets.
3. **c (age guard, N = 5 minutes)** — defense-in-depth against any remaining same-project timing race. Also protects against a future scenario where intermediate `lifecycle_state` writes are added but a bug leaves a gap.

**b3 (bind-first)** is a reasonable alternative to b2 but couples the guard to the Flask server. b1 (pidfile) is strictly inferior to b2 (flock). Neither should replace b2 as primary.

---

## Section 5 — Gap Assessment + Verification Blocks

### Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| **G1 — Cross-project blind spot** | `lifecycle.py:202`: `SELECT ... WHERE lifecycle_state = 'claimed'` — no project filter | Filter by `target_project` derived from `decisions_dir` | Add `target_project` column to SELECT + WHERE clause; callsite passes project root |
| **G2 — No single-instance guard** | `bellows.py:1796` (`__main__`): no exclusivity check before startup | `flock(LOCK_EX\|LOCK_NB)` on `.bellows.lock` at BELLOWS_ROOT; exit if held | Add flock acquisition before `migrate_db()` at `bellows.py:1821` |
| **G3 — Recovery age guard** | `lifecycle.py:229`: unconditional fallthrough to `abandoned` | Skip `abandoned` if `created_at` < N minutes old | Add `created_at` to SELECT; add time check before `abandoned` UPDATE |
| **G4 — Intermediate states never written** | `bellows.py:446–466`: `mint_and_claim` sets `claimed`, no subsequent `mark_plan_state('in_progress')` | Write `in_progress` after successful rename | Add `lifecycle.mark_plan_state(plan_id, 'in_progress')` after `shutil.move` at `bellows.py:458` (also addresses FORWARD row 20) |

### Verification Blocks

#### V1 — Recovery decision-tree branch confirmation
- **Claim:** The `abandoned` branch fired because `recover_half_claimed` was called with a non-bellows directory first, and the global query returned plan 7.
- **Query:** `sqlite3 "file:lifecycle.db?mode=ro" "SELECT id, lifecycle_state, target_project FROM plans WHERE id = 7"`
- **Expected:** `7|closed|/Users/marklehn/Developer/GitHub/bellows` — `target_project` is bellows, confirming the plan's files live in bellows's decisions dir, not the first-iterated directory.

#### V2 — Directory/state evidence
- **Claim:** Bellows is at index 7 of 10 in `watched_projects`; the first 7 directories do not contain plan 7's files.
- **Query:** `python3 -c "import json; c=json.load(open('config.json')); print(c['watched_projects'].index('/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions'))"`
- **Expected:** `7` — confirms 7 directories are iterated before bellows's, any of which would trigger the misclassification.

#### V3 — Instance B's port-bind behavior
- **Claim:** Flask bind failure kills the daemon thread silently; instance B continues without a callback server.
- **Query:** Read `server.py:26–33` — `ResponseServer.start()` spawns `app.run()` in a daemon thread with no exception handler.
- **Expected:** `threading.Thread(target=lambda: self.app.run(...), daemon=True).start()` — daemon thread. `OSError` from bind kills the thread; `daemon=True` means the exception is not propagated to the main thread. Main thread continues.

#### V4 — Double-claim atomicity (Section 3a)
- **Claim:** `mint_and_claim` serializes via `BEGIN IMMEDIATE`, but the detection→mint→rename sequence is not atomic.
- **Query:** Read `lifecycle.py:149–169` and `bellows.py:430–458`.
- **Expected:** `conn.execute("BEGIN IMMEDIATE")` at `lifecycle.py:150` serializes the DB transaction. But `shutil.move` at `bellows.py:458` is outside the transaction. Two instances can both detect the file, both mint IDs, then race on the move.

### CEO Decision Forks

**DF1 — Single-instance mechanism:**
Options: flock (b2) vs. bind-first (b3) vs. pidfile (b1).
**Recommendation:** flock (b2). No stale-state risk, decoupled from Flask, minimal code.

**DF2 — Ship recovery fix and instance guard together or separately?**
Options: one executable (both fixes) vs. two executables (guard first, then recovery fix).
**Recommendation:** One executable. The flock prevents future incidents immediately; the recovery fix is a correctness improvement that should ship alongside. Both are small changes (~10 lines each). Shipping together reduces the test surface to one plan.

**DF3 — Race-guard window N:**
Options: 2 minutes, 5 minutes, 10 minutes.
**Recommendation:** 5 minutes. The observed race was 3 seconds; 5 minutes provides 100x margin. Plans abandoned by a genuine crash within 5 minutes simply wait for the next restart cycle — negligible operational impact.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Forensic root-cause analysis of the 2026-06-12 daemon-collision recovery race. Confirmed the compound root cause (cross-project blind spot in `recover_half_claimed` + intermediate `lifecycle_state` never written), reconstructed the two-daemon timeline, enumerated 9 collision surfaces, and proposed a three-layer fix (flock guard + project-scoped recovery + age guard) with 3 CEO decision forks.

### Files Deposited
- `knowledge/research/daemon-collision-recovery-race-2026-06-12.md` — full diagnostic findings (this file)

### Files Created or Modified (Code)
- None (forensic diagnostic only — no fix code authored per plan instructions)

### Decisions Made
- Ranked flock (b2) as recommended single-instance guard over pidfile (b1) and bind-first (b3) based on stale-state risk and coupling analysis
- Recommended N = 5 minutes for age guard based on 100x margin over observed race window

### Flags for CEO
- **DF1:** Single-instance mechanism choice (flock recommended)
- **DF2:** Ship recovery fix + instance guard in one executable or two (one recommended)
- **DF3:** Age guard window N (5 minutes recommended)
- FORWARD row 20 (`lifecycle_state` intermediate states never written) is a contributing factor to this incident — consider bundling the `in_progress` state write into the fix executable

### Flags for Next Step
- None (single-step diagnostic)
