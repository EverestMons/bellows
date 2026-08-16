# Bellows restart-lock diagnostic findings — 2026-08-15

**Diagnostic:** `bellows-restart-lock-2026-08-15`
**Date:** 2026-08-15
**Scope:** Read-only investigation of the daemon start/stop/restart/lock machinery.
**Prior art:** `Done/diagnostic-daemon-restart-state-divergence-2026-05-24.md`

---

## Q1 — Start surfaces

Every way `bellows.py` is launched as a daemon process:

### 1a. Dashboard-spawned child (documented primary path)

`dashboard.py:362-368` — `CursesShell._spawn_child`:

```python
self.child = subprocess.Popen(
    [sys.executable, "bellows.py"],
    cwd=str(self.bellows_root),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
)
```

Called at two sites: `dashboard.py:423` (initial spawn inside `_main_loop`) and `dashboard.py:404` (respawn after restart). The spawned process becomes a direct child of the dashboard's Python process. The dashboard holds a reference to it as `self.child`. This is the documented model from `CLAUDE.md`: "python dashboard.py — primary — full-screen TUI that owns the daemon."

**Parent:** The dashboard process (Python). The dashboard considers it `self.child` because it holds the `Popen` object.

### 1b. Bare `python bellows.py` / `nohup python bellows.py` (documented headless path)

`bellows.py:2447` — `if __name__ == "__main__":` — the standard direct-execution entry. `CLAUDE.md` documents this as "python bellows.py — headless daemon (no TUI)."

A `nohup python bellows.py` invocation would reparent to PID 1 (init/launchd) once the launching shell exits. **No dashboard instance would consider this process `self.child`** — the dashboard's `self.child` is only ever set by `_spawn_child`, which calls `subprocess.Popen` and stores the return value.

**This is the out-of-band incumbent surface.** PID 3969 (started 2026-08-13 11:08:10, state `SN`, writing to `logs/daemon-nohup.log`) was launched via this path. It is not any dashboard's `self.child`.

### 1c. `status.py` — read-only observer, never starts the daemon

`status.py:231-268` — `main()` calls `probe_daemon` and `get_daemon_pid` but never spawns or starts `bellows.py`. It is a display-only tool. Not a start surface.

### 1d. No other start surfaces found

No Makefile, shell scripts, or other Python files spawn `bellows.py`. The only two launch paths are 1a (dashboard) and 1b (bare/nohup).

---

## Q2 — Restart/stop reach

### `_do_restart` trace

`dashboard.py:397-405`:

```python
def _do_restart(self, stdscr):
    """Restart sequence: terminate → wait for lock → respawn."""
    self._terminate_child()
    if not self._wait_for_lock_release():
        # Lock not released — don't respawn
        self.mode = "normal"
        return
    self._spawn_child()
    self.mode = "normal"
```

### `_terminate_child` trace

`dashboard.py:370-386`:

```python
def _terminate_child(self):
    """SIGTERM → wait → SIGKILL if needed. Returns True if child is dead."""
    if self.child is None:
        return True
    if self.child.poll() is not None:
        return True
    self.child.terminate()
    try:
        self.child.wait(timeout=SIGTERM_TIMEOUT)
        return True
    except subprocess.TimeoutExpired:
        self.child.kill()
        try:
            self.child.wait(timeout=SIGKILL_TIMEOUT)
            return True
        except subprocess.TimeoutExpired:
            return False
```

**Confirmed:** `_terminate_child` acts ONLY on `self.child`. It returns `True` immediately if `self.child is None` (line 372-373). The signals (`terminate()` = SIGTERM, `kill()` = SIGKILL) are sent exclusively via the `subprocess.Popen` object stored in `self.child`.

**Consequence confirmed:** A daemon started out-of-band (not spawned by THIS dashboard instance) is never killed by the `r` restart. After `_terminate_child` returns (immediately, since `self.child` is `None` or already dead), `_do_restart` calls `_wait_for_lock_release` (line 400), which polls `status.probe_daemon` up to `FLOCK_RETRY_LIMIT=10` times with `FLOCK_RETRY_INTERVAL=0.5s` intervals (5 seconds total). Since the out-of-band incumbent holds the flock and is never killed, the lock never releases, `_wait_for_lock_release` returns `False`, and the restart aborts at line 402 — no new child is spawned.

If the dashboard was freshly started (rather than restarting), the initial `_spawn_child` at `dashboard.py:423` spawns a new `bellows.py` child that immediately hits the flock guard at `bellows.py:2472-2480` and exits with code 1. The dashboard then shows `child_exit_code=1` but continues running (it doesn't exit on child death — it just displays the state).

### Flock-probe liveness check at `dashboard.py:129-130`

```python
# Daemon liveness (via flock probe — works whether we own the child or not)
daemon_running = status.probe_daemon(lock_path)
```

This is called inside `assemble_state` (line 104), which is called every 2 seconds in the `_main_loop` (line 430). **Its result is used exclusively for display** — it feeds `daemon_running` into the header render via `status.render_daemon_header` at line 118 of `status.py`, and gates `status.get_daemon_pid` at line 137 of `dashboard.py`.

**The flock probe result is NEVER used to stop, kill, or adopt a non-child incumbent.** It is display-only. There is no adoption path — no code anywhere in `dashboard.py` that says "if daemon is running but it's not my child, take ownership" or "if daemon is running and it's not my child, kill it."

---

## Q3 — The lock

### `bellows.py:2472-2480` — the daemon's single-instance flock guard

```python
# G2: flock single-instance guard — must precede all DB/recovery/watcher work
_lock_path = str(BELLOWS_ROOT / ".bellows.lock")
_lock_fd = open(_lock_path, "w")
try:
    fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except (BlockingIOError, OSError):
    _log("ERROR", "another Bellows instance holds .bellows.lock — exiting")
    sys.exit(1)
# _lock_fd intentionally kept open — kernel releases flock on process death
```

**Confirmed:**
1. The lock file is opened with `"w"` mode (line 2474) — this truncates the file to 0 bytes on every open.
2. **No PID or identity is written into the lock file** after acquiring the flock. The fd is held open but the file content is always empty.
3. The error message at line 2478 names no holder PID — it says only "another Bellows instance holds .bellows.lock."
4. The flock is fd-scoped (`fcntl.flock` on `_lock_fd`). Per POSIX advisory-lock semantics, the lock is released when ALL file descriptors referencing the open file description are closed — in practice, on process death (the comment at line 2480 states this intent).

### Is there a separate pidfile?

**No.** Searched `bellows.py`, `dashboard.py`, `status.py`, and `runner.py` for `os.getpid`, `pidfile`, `.pid`. None found. There is no pidfile anywhere in the codebase.

### Dashboard lock at `dashboard.py:341-351`

```python
def _acquire_dashboard_lock(self):
    lock_path = str(self.bellows_root / ".bellows-dashboard.lock")
    self.dashboard_lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(self.dashboard_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        self.dashboard_lock_fd.close()
        self.dashboard_lock_fd = None
        print("Another dashboard instance is already running")
        sys.exit(1)
```

**Same shape** — opened `"w"`, no PID written, flock is the only guard. The only difference: the dashboard lock uses a separate file (`.bellows-dashboard.lock` vs `.bellows.lock`) and the dashboard has an explicit `_release_dashboard_lock` at line 352 that calls `LOCK_UN` then `close()` — the daemon has no such release (it relies on process death).

---

## Q4 — Stale vs live disambiguation

**No existing code path can distinguish a stale lock from a live one, or report which PID holds it.**

- `bellows.py:2475-2479`: The flock attempt either succeeds (lock was free/stale — the kernel auto-releases advisory locks on holder death) or fails with `BlockingIOError`/`OSError`. On failure, it logs a generic message and exits. It does not attempt to identify the holder.

- `status.py:22-34` — `probe_daemon`: This function CAN distinguish "lock held" from "lock free" via a non-blocking flock attempt. If the flock succeeds, the lock was free (holder dead or never existed); if it fails, the lock is held (holder alive). **But this is binary — it reports held/not-held, not who holds it.** It is also read-only (it immediately releases any flock it acquires, line 29).

- `status.py:37-47` — `get_daemon_pid`: This function attempts to identify the holder via `lsof -t <lock_path>`. It is used only for display in the dashboard header and `status.py main()`. **It is never called by the daemon or by any stop/restart path.** It returns the first PID from `lsof` output, or `None` on failure.

**Summary:** The codebase has the building blocks (`probe_daemon` for liveness, `get_daemon_pid` for identity) but they are used only for display. The daemon's own flock guard at `bellows.py:2478` has NO access to either — it just logs a generic error and exits.

---

## Q5 — Fix options (specify, do not implement)

### Recommended fix order (cheapest-safe-path first)

The fix must follow this **explicit guard sequence** on any daemon start or restart attempt:

1. **Attempt atomic `flock(LOCK_EX|LOCK_NB)` acquire.** If it SUCCEEDS, the lock was free or stale — no incumbent exists, no kill needed. Write `os.getpid()` and timestamp into the lock file (option (a) below), proceed to start. This is the happy path that covers both clean starts and stale-lock recovery.

2. **Only if acquire FAILS** does an incumbent exist. Now run the identity guard (Q6 ii) and idle guard (Q6 i) — both must pass before any signal is sent.

3. **If both guards pass:** send SIGTERM, wait `SIGTERM_TIMEOUT`, escalate to SIGKILL if needed, then **re-acquire the flock as the authoritative arbiter.** The kill decision is not atomic; the flock re-acquire is what proves success. If re-acquire fails (another process raced and won), refuse and exit.

4. **If either guard fails:** refuse — log the holder PID and the guard that failed, and exit. This is the current behavior (exit with "another Bellows instance holds .bellows.lock") made more informative.

### Option (a): Write PID + timestamp into the lock file (information fix)

After acquiring the flock at `bellows.py:2476`, write `os.getpid()` and `datetime.now().isoformat()` into the lock file (the fd is already open for writing). On flock failure at line 2477-2479, read the lock file to extract the holder's claimed PID and start time, and include them in the error message.

**Trade-offs:**
- Minimal change (~10 LOC in `bellows.py:2474-2480`).
- Self-diagnosing: the "another Bellows instance" error now says *who* and *how old*.
- Does NOT enable automatic kill — only improves error reporting.
- The PID in the file is a claim, not a proof — it can be stale after PID reuse. It must NOT be trusted for kill without identity verification (Q6 ii).

**Files touched:** `bellows.py` — the `if __name__ == "__main__"` block around lines 2472-2480.

### Option (b): Stop/restart path that discovers and terminates the incumbent

Add a stop/restart command that:
1. Reads the PID from the lock file (requires option (a) to have been deployed first).
2. Verifies the PID is genuinely `bellows.py` via `ps -o command= -p <pid>` or by checking the `lsof` fd on the lock file (identity guard — Q6 ii).
3. Checks idle state (idle guard — Q6 i).
4. Sends SIGTERM → wait → SIGKILL (the same ladder `dashboard.py:370-386` uses).
5. Re-acquires the flock as the arbiter of success.

**Discovery mechanism choice:** `lsof -t <lock_path>` (already implemented in `status.py:37-47` as `get_daemon_pid`) is the preferred discovery path. Advantages: it identifies the ACTUAL flock holder by querying the kernel's open-file table, which is more authoritative than a stored PID. Failure modes:
- `lsof` absent on the system → refuse (safe fallback).
- Multiple PIDs returned (multiple openers) → use the one that holds the write-mode fd, or refuse if ambiguous.
- Zero PIDs returned (race — holder just died) → re-try the flock acquire; if it succeeds, proceed without killing.

The stored PID from option (a) serves as a fast-path hint and self-diagnosis aid; `lsof`/`ps` verification serves as the identity proof.

**Trade-offs:**
- ~40-60 LOC across `bellows.py` and/or a new `bellows_ctl.py` CLI.
- Solves the structural problem: restarts can now reach out-of-band incumbents.
- Requires the idle guard (Q6 i) and identity guard (Q6 ii) to prevent killing a busy daemon or a recycled PID.
- Requires a clean SIGTERM handler in `bellows.py` to avoid mid-transition state divergence (see Q6 i).

**Files touched:** `bellows.py` (flock guard block + new SIGTERM handler), `dashboard.py` (`_do_restart` to use the new stop path instead of `_terminate_child` alone).

### Option (c): Dashboard adopt-and-kill vs refuse-with-message for non-child incumbents

On dashboard startup or restart, when the flock is held by a non-child process:
- **Adopt-and-kill:** Discover the incumbent via `lsof`, verify identity and idle state, kill it, re-acquire, and adopt the new child as `self.child`.
- **Refuse-with-message:** Display "Daemon PID {pid} (started {age} ago) holds the lock — kill it manually or use `bellows stop`" and do not spawn a child.

**Recommendation: refuse-with-message is safer.** Reasons:
- Automatic killing on dashboard startup is a surprise — the user may not have intended to kill the running daemon.
- The dashboard is a UI tool; its `r` key restart is an explicit user action, but the *initial spawn* at `_main_loop:423` is implicit.
- Refuse-with-message is the minimal extension of the current behavior (exit with a better error) and lets the user decide.
- Adopt-and-kill requires both guards (Q6 i, ii) and a clean SIGTERM handler — significant complexity for a path that should be rare.

### Recommended minimal fix

**Option (a) + a scoped version of (b) integrated into `_do_restart`:**

1. In `bellows.py:2474-2480`: after acquiring the flock, write PID + timestamp. On failure, read the file and include holder identity in the error. (~10 LOC)

2. In `dashboard.py:397-405` (`_do_restart`): after `_terminate_child` returns, if `_wait_for_lock_release` fails, attempt incumbent discovery via `status.get_daemon_pid` on the lock file. If the incumbent is identified and passes both the identity guard and the idle guard, send SIGTERM→wait→SIGKILL to it, then re-try `_wait_for_lock_release`. If any guard fails, log the holder and refuse. (~30 LOC)

3. In `bellows.py`: install a SIGTERM handler that sets a shutdown flag, waits for `_active_count == 0`, then exits cleanly. (~15 LOC — see Q6 i for details.)

**Files/functions the executable would touch:**
- `bellows.py`: the `if __name__ == "__main__"` block (lines 2472-2480) — PID+timestamp write + improved error message.
- `bellows.py`: new SIGTERM handler (registered near the flock guard, after line 2480).
- `dashboard.py`: `_do_restart` (line 397) — incumbent discovery and guarded kill.
- `status.py`: no changes needed — `get_daemon_pid` and `probe_daemon` already exist and are sufficient.

---

## Q6 — Kill-safety (two independent guards)

### (i) Idle guard

An incumbent may be mid-plan. The fix must detect idle-vs-busy BEFORE killing.

**Detection mechanism:** The heartbeat log at `bellows.py:2434-2436` distinguishes idle from busy:
- `heartbeat: idle` — `_active_count == 0` AND no `verdict-pending-*` files in watched directories.
- `heartbeat: {n} in-flight, {m} awaiting verdict` — at least one plan is running or pending.

However, the heartbeat is an internal log line, not an externally queryable state. From outside the process, the idle state can be approximated by:
- Querying `lifecycle.db` (read-only) for in-flight plans via `status.query_in_flight` (already implemented in `status.py:82-105`).
- Scanning the watched `decisions/` directories for `in-progress-*` files (indicating a plan is currently executing).

**Recommended idle check for the stop path:**
1. Call `status.query_in_flight(db_path)` — if rows are returned with `status='running'`, the daemon is busy → refuse.
2. Scan watched directories for `in-progress-*` files — if any exist, the daemon may be mid-transition → refuse.
3. Only if both checks pass (no running plans, no in-progress files) is it safe to signal.

**Mid-transition hazard:** The prior diagnostic (`Done/diagnostic-daemon-restart-state-divergence-2026-05-24.md`) established that a daemon killed mid-transition splits non-atomic filename/verdict/`bellows.db` operations. Specifically: verdict-request post and filename rename are separate non-atomic operations (Section A, boundaries 2-4 in that diagnostic). Killing between them produces the exact state-divergence failures catalogued as items #2, #3, #5.

**SIGTERM handler — does one exist?** No. `bellows.py` has **no signal handler registration anywhere.** Searched for `import signal`, `signal.signal`, `signal.SIGTERM`, `signal.SIGINT`, `signal.SIGHUP` — none found. The only signal-aware code is `dashboard.py:16` (`import signal`) but no handler is registered there either (the import is present but unused for handler registration — it may have been planned but never implemented).

The daemon's main loop at `bellows.py:2416-2444` catches only `KeyboardInterrupt` (line 2442), which handles Ctrl-C in the foreground case but does NOT catch SIGTERM. A SIGTERM to the daemon would trigger Python's default behavior: raise `SystemExit`. Since `SystemExit` is not `KeyboardInterrupt`, it would NOT be caught by the `except KeyboardInterrupt` at line 2442 — it would propagate up, and the process would exit. However, any in-flight `run_plan` threads (spawned by the watchdog handler) would be running concurrently. Python's threading model means daemon threads die on main-thread exit, but `run_plan` threads are likely not daemon threads (they're spawned via `threading.Thread` without `daemon=True` — this would need verification in the plan-dispatch code). If they're non-daemon, the process hangs until they complete, which is actually safer (the SIGTERM becomes a "wait for current work to finish, then exit") but unpredictable.

**Recommendation:** The fix MUST install a clean SIGTERM handler in `bellows.py` that:
1. Sets a global `_shutting_down` flag.
2. Prevents new plans from being dispatched (checked in the watchdog handler / `_handle` method).
3. Waits for `_active_count == 0` (using `_active_lock`).
4. Then exits cleanly (stops the observer, closes the response server, lets the flock release on exit).

Without this handler, SIGTERM + SIGKILL is the only reliable kill path, and SIGKILL cannot be trapped — it risks the same mid-transition state divergence the prior diagnostic catalogued. **"No clean-shutdown path exists" is a reason to prefer refuse over kill** in ambiguous cases.

### (ii) Identity guard

The fix must prove the kill target is genuinely the Bellows daemon, not a recycled PID.

**A PID read from a file is NOT authoritative** — after PID reuse, the stored PID could name an unrelated process. The authoritative identity signal is:

1. **`lsof` on the lock file:** `status.get_daemon_pid(lock_path)` at `status.py:37-47` runs `lsof -t <lock_path>` and returns the PID(s) with an open fd on `.bellows.lock`. If the lock file is held (confirmed by `probe_daemon`), the `lsof`-returned PID is the actual holder. This is more authoritative than a stored PID because it queries the kernel's open-file table.

2. **`ps` cmdline verification:** After obtaining a candidate PID from `lsof`, verify via `ps -o command= -p <pid>` that the process command line contains `bellows.py`. This guards against the edge case where `lsof` returns a PID that opened the file for reading (e.g., `status.py` itself during a probe) rather than the flock holder.

**Recommended identity check:**
1. `pid = status.get_daemon_pid(lock_path)` — get PID via `lsof`.
2. If `pid is None` → refuse (cannot identify holder; `lsof` may be absent or returned no results).
3. Verify `bellows.py` appears in `ps -o command= -p {pid}` output.
4. If verification fails → refuse (PID holds the file but is not Bellows).
5. Only if both steps pass → proceed to idle guard.

**Safe-refuse fallback:** Whenever identity OR idle-state cannot be confirmed, log the holder PID (if known) and the reason for refusal, then exit — the CURRENT behavior at `bellows.py:2478`, but with better diagnostics. Refuse is the default; killing is the exception that must earn both guards.

### (iii) Degenerate and concurrent lock states

The fix must survive:

1. **Genuinely stale lock (holder already dead):** The kernel releases advisory flocks on process death. A subsequent `flock(LOCK_EX|LOCK_NB)` call will SUCCEED — the lock was free. The fix must detect this via the initial flock attempt (step 1 of the guard sequence in Q5) and simply ACQUIRE the lock. There is no process to signal. The lock file may contain a stale PID from the dead holder (if option (a) is deployed) — this is harmless because the flock acquire succeeded, meaning the PID is irrelevant.

2. **Empty or malformed lock file (the current 0-byte reality):** The lock file is currently always 0 bytes (opened with `"w"`, nothing written). After option (a), it will contain PID+timestamp. The discovery path must handle both states: if the file is empty or unparseable, fall back to `lsof` discovery (which doesn't depend on file content). The PID read from the file is a hint, not a requirement.

3. **Two restarts racing:** If two restart attempts run concurrently (e.g., two dashboards, or a manual restart and an automated one), the atomic `flock(LOCK_EX|LOCK_NB)` acquire is the authoritative final arbiter. Exactly one process can hold the flock at any time. The fix's success is OBSERVED as "the new daemon now holds the flock" (the re-acquire after kill succeeds), never as "kill() returned 0." The kill decision is not atomic — a race between kill-and-acquire must be resolved by the flock, not by the kill return code. If the re-acquire fails (another process raced and won the flock), the fix must refuse and exit.

**Cross-reference with prior diagnostic:** The state-divergence failures catalogued in `Done/diagnostic-daemon-restart-state-divergence-2026-05-24.md` (items #2, #3, #5) are all caused by killing the daemon between non-atomic filename/verdict operations. The idle guard (Q6 i) directly addresses this overlap: by refusing to kill a busy daemon, the fix prevents new instances of the catalogued divergence. Additionally, the SIGTERM handler (recommended in Q6 i) would allow the daemon to drain in-flight work before exiting, closing the mid-transition vulnerability at its source.

---

## Recommended minimal fix — summary

**Problem:** The restart mechanism in `dashboard.py` can only terminate `self.child`. An out-of-band daemon (launched via bare `python bellows.py` or `nohup`) is invisible to the dashboard's restart path. The flock guard correctly prevents a second instance, but the error is undiagnosable (no holder identity) and there is no path to stop the incumbent.

**Fix (three coordinated changes):**

1. **`bellows.py` — PID+timestamp in lock file + improved error** (lines 2472-2480): After acquiring the flock, write `f"{os.getpid()} {datetime.now().isoformat()}\n"` into the lock file. On flock failure, read the file to extract the holder's PID and age, and include them in the error message. ~10 LOC.

2. **`bellows.py` — SIGTERM handler** (register after line 2480): Install `signal.signal(signal.SIGTERM, ...)` that sets `_shutting_down = True`, blocks new plan dispatch, waits for `_active_count == 0`, then exits cleanly. ~15 LOC.

3. **`dashboard.py` — guarded incumbent stop in `_do_restart`** (line 397): After `_terminate_child` returns, if `_wait_for_lock_release` fails, run the identity guard (via `status.get_daemon_pid` + `ps` verification) and idle guard (via `status.query_in_flight` + `in-progress-*` file scan). If both pass, SIGTERM the incumbent, wait for flock release, and respawn. If either guard fails, log and refuse. ~30 LOC.

**Guard sequence (mandatory order):**
1. Attempt `flock(LOCK_EX|LOCK_NB)` — if succeeds, no kill, proceed.
2. Only on failure: identity guard → idle guard → SIGTERM → wait → re-acquire flock as arbiter.
3. Refuse is the default; killing is the exception.

**No blind kill-by-PID.** A stored PID is a hint for diagnostics, never authorization to signal. Kill authorization requires both the identity guard (prove the target is Bellows via `lsof`/`ps`) and the idle guard (prove the target is not mid-plan).

---

### Ledger Updates

#### Prompt Feedback

The diagnostic instructions were clear and well-structured. The Q1–Q6 framework covered all necessary aspects. The explicit requirement to cite `file:line` and quote code kept findings grounded. The cross-reference to the prior state-divergence diagnostic was essential — Q6's idle guard and SIGTERM handler recommendation could not have been properly scoped without understanding the mid-transition hazards already catalogued there. The "do not fix — investigate and describe" constraint was appropriate for this class of problem where the fix shape depends on understanding the full machinery first.
