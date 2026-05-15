# Post-Plan Hang Diagnostic Findings
**Date:** 2026-04-16 | **Plan:** diagnostic-bellows-post-plan-hang-2026-04-16.md | **Status:** Complete

---

## Q1 — Post-Final-Step Code Path in `run_plan`

After the final `runner.run_step` returns (bellows.py lines 179 or 234), the sequence is:

**For a diagnostic plan (effective_auto_close=False), the verdict-pending path is taken:**

1. `record_run(...)` (lines 185–189 or 242–246) — SQLite connect/INSERT/commit/close
2. `post_diff = _capture_git_diff(project_path)` (line 192 or 249) — subprocess, **10s timeout**, safe
3. `files_changed = _parse_diff_stat(post_diff, pre_diff)` (line 193 or 250) — pure string processing
4. `gate_result = gates.check(...)` (line 194 or 251) — regex + file-existence checks, no I/O
5. `print(...)` gate result (line 195 or 252)

Final-step block (lines 257–283) — entered because `not effective_auto_close` is True:

6. `verdict.post_verdict_request(plan_path, ...)` (line 273) — file write to `verdicts/pending/`. Pure local I/O, fast.
7. `notifier.notify_verdict_request(...)` → `notifier.push(...)` (line 274) — **HTTP POST to `https://api.pushover.net/1/messages.json` with NO TIMEOUT. Synchronous. Can block indefinitely.**
8. `shutil.move(inprogress_path, verdict_pending_path)` (line 279) — file rename, fast
9. `record_run(...)` (line 280) — SQLite write
10. `print(...)` (line 282)
11. `return`

**Blocking operation summary for Q1:**
- `notifier.push()` at step 7 is the only unbounded blocking call. All others have timeouts (subprocess) or are local disk I/O (fast on SSD, no external dependency).
- `record_run` uses SQLite's default 5-second busy timeout — not a 40-minute risk.
- `_capture_git_diff` has a 10-second timeout and swallows exceptions — not a hang risk.

**Dead code note:** Lines 306–313 (stranded check + `notifier.notify_complete`) are unreachable. The conditions at line 257 and line 288 are logical complements (De Morgan duals) — if the first `if` is False, the second `if` is necessarily True, so execution always returns at line 304 before reaching line 306. This means `notifier.push()` at line 310 and `notifier.notify_complete()` at line 313 are never called.

---

## Q2 — After `run_plan` Returns

`run_plan` is called from `_run_tracked` (lines 432–440), which runs in a **daemon background thread**:

```python
def _run_tracked(self, path: str, resume_step: Optional[int] = None):
    with self._active_lock:
        self._active_count += 1
    try:
        run_plan(path, self.config, self.response_server, resume_step=resume_step)
    finally:
        with self._active_lock:
            self._active_count -= 1
        self._check_queue_drain()  # ← called in finally, even if run_plan raises
```

After `run_plan` returns, `_check_queue_drain()` is called (lines 442–454):

```python
def _check_queue_drain(self):
    with self._active_lock:
        if self._active_count > 0:
            return
    pending = []
    for d in self.config.get("watched_projects", []):
        if os.path.isdir(d):
            pending.extend([f for f in os.listdir(d) if is_runnable_plan(f)])
    if not pending:
        ...
        print("Bellows: 🏁 Queue empty — all plans complete")
        notifier.push(app_key, user_key, "Bellows — Queue Empty", "...")
```

**(a)** `_check_queue_drain` can block: `notifier.push()` at line 454, **NO TIMEOUT**. This runs in the background daemon thread. It does not freeze the main thread directly — but it means the "Queue empty" print may never appear, because the thread is hung before reaching it.

**(b)** `_rescan` is called every 30 seconds from the **main thread** (lines 583–587):
```python
while True:
    time.sleep(1)
    if time.time() - last_rescan >= rescan_interval:
        self._rescan(handler)  # ← blocks main thread if anything inside hangs
        last_rescan = time.time()
```

`_rescan` calls `_consume_verdicts()` first (line 471), which contains `notifier.push()` calls at lines 527 and 544 — **both with NO TIMEOUT**. If either hangs, the **main thread is frozen**, preventing Ctrl+C from being processed and making the terminal unresponsive.

**(c)** `_rescan` runs entirely in the main thread — it is NOT a timer thread. It is a synchronous call inside the `while True` loop. Any blocking call inside `_rescan` (especially `_consume_verdicts`'s `notifier.push()`) directly stalls the main event loop.

---

## Q3 — Notifier Blocking Calls

Full `notifier.push` signature (notifier.py lines 9–26):

```python
def push(app_key: str, user_key: str, title: str, message: str,
         url: str = "", url_title: str = "") -> bool:
    payload = { ... }
    try:
        response = requests.post(PUSHOVER_API_URL, data=payload)  # NO TIMEOUT
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Pushover error: {e}", file=sys.stderr)
        return False
```

**(a)** Yes, `notifier.push` makes an HTTP request to `https://api.pushover.net/1/messages.json`.

**(b)** **No timeout is set.** `requests.post(url, data=payload)` without a `timeout` argument uses the OS-level socket default, which on macOS is `None` (no timeout). If the server accepts the TCP connection but stalls the response (half-open), the call blocks indefinitely.

**(c)** If the Pushover API is unreachable or slow, the call **can block indefinitely**. The try/except only catches `requests.RequestException`, which is raised on connection errors or DNS failures — not on a stalled response where the TCP connection is established but the server never sends a complete HTTP response. In the stall scenario, `requests` waits forever with no exception raised.

**(d)** Yes, `notifier.push` is called synchronously from `run_plan` (at lines 274, 301, 310, 313 — though 310 and 313 are dead code).

**(e)** In the diagnostic plan's post-final-step path, there are **two sequential `notifier.push()` calls**:
1. `notifier.notify_verdict_request(...)` → `push()` in `run_plan` (line 274, background thread)
2. `notifier.push(...)` in `_check_queue_drain()` (line 454, same background thread, called after `run_plan` returns)

Each call is unbounded. If the first stalls for any duration, the second is delayed by the same amount before also potentially stalling. On top of this, the main thread's 30-second rescan can trigger additional `notifier.push()` calls in `_consume_verdicts()` (lines 527, 544) on the **main thread**, making the terminal unresponsive.

---

## Q4 — `_capture_git_diff` Subprocess Hang Risk

Full implementation (bellows.py lines 320–329):

```python
def _capture_git_diff(project_path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except Exception:
        return ""
```

**(a)** Uses `subprocess.run` — a blocking call, but with an explicit timeout.

**(b)** Timeout is **10 seconds**. `subprocess.TimeoutExpired` is caught by the bare `except Exception` and returns `""`. No hang possible.

**(c)** `git diff --stat` could be slow on a large repo or with a locked `.git/index`, but the 10-second timeout prevents a hang. A locked index causes git to fail or wait, but subprocess will kill it after 10 seconds regardless.

**(d)** It is called after the final step in two places:
- Line 192: pre-step snapshot (before the initial `runner.run_step`)
- Line 249: post-step snapshot inside the while loop (after each step including the final)

For single-step plans, only lines 177 and 192 are executed (pre and post for step 1). **Not a hang risk.**

---

## Q5 — Verdict Consumption Loop

`_consume_verdicts()` (bellows.py lines 479–554) is called from `_rescan()` (line 471) which is called from the **main thread**.

**(a)** `_consume_verdicts` holds **no locks**. It does not acquire `_active_lock` or any other mutex. There is no deadlock risk from locking.

**(b)** `shutil.move` at lines 526, 534, 542, 554 are all within the same filesystem on macOS (bellows root or the watched project directory) — these are atomic `rename(2)` syscalls, effectively instantaneous. If the destination exists for `shutil.move`, Python's implementation will overwrite it (POSIX rename semantics). No blocking risk.

**(c)** The `time.sleep(1)` in the main loop does NOT interact badly with rescan timing in itself — the rescan check is `if time.time() - last_rescan >= 30`. However, if `_consume_verdicts()` blocks on `notifier.push()`, the `time.sleep(1)` never completes — the next iteration never starts, `last_rescan` is never updated, and the main loop is frozen. The sleep is not the cause; it is simply never reached when `_consume_verdicts` hangs.

**Race condition:** If a verdict file is partially written (e.g., the Planner writes it in two passes), `check_verdict` at line 497 parses the first line for `verdict: (continue|stop)`. If the first line is not yet written, `check_verdict` returns `{"found": False}`. The file is left in `resolved/` and consumed on the next 30-second rescan. This is a benign miss, not a deadlock or data corruption.

---

## Q6 — Root Cause Identification and Fix Proposal

### Hang Points Ranked by Likelihood

**#1 — `notifier.push()` in `_consume_verdicts()` (MOST LIKELY — main thread freeze)**

Location: bellows.py lines 527, 544 (inside `_consume_verdicts`, called from `_rescan` in the main thread)

This is the most likely cause of the observed 40-minute terminal freeze. When `_rescan` fires every 30 seconds and there are processed verdicts to consume (e.g., from the 9 resolved verdict files in `verdicts/resolved/processed-*`), `_consume_verdicts` runs and calls `notifier.push()` for each "continue-to-done" or "stop" verdict. Since `notifier.push()` has no timeout, if the Pushover API is slow or the connection stalls, the **main thread blocks indefinitely**. Ctrl+C is buffered until the blocking C-level socket call returns. The terminal becomes unresponsive. This requires force-quit.

**#2 — `notifier.push()` in `run_plan` (verdict pending notification, background thread)**

Location: bellows.py line 274 (inside the verdict-pending branch of `run_plan`, called from the background thread via `_run_tracked`)

This blocks the background thread. The "Queue empty" print from `_check_queue_drain` never appears because the thread never reaches it. The main thread continues its `time.sleep(1)` loop — but if the main thread then also hits a `notifier.push()` in `_rescan`, both threads are hung.

**#3 — `notifier.push()` in `_check_queue_drain()` (background thread)**

Location: bellows.py line 454 (called after `run_plan` returns in `_run_tracked`)

Two sequential `push()` calls (line 274 first, then line 454 in `_check_queue_drain`) can both block. If the first finishes but the second stalls, the background thread is hung. The main thread is still alive but the "Queue empty" message and notification are lost.

### Proposed Fixes

**Fix 1 (CRITICAL): Add timeout to `requests.post()` in `notifier.push()`**

Change:
```python
response = requests.post(PUSHOVER_API_URL, data=payload)
```
To:
```python
response = requests.post(PUSHOVER_API_URL, data=payload, timeout=(5, 10))
```
`timeout=(5, 10)` means: 5-second connect timeout, 10-second read timeout. Any Pushover call that doesn't complete in 15 seconds total will raise `requests.Timeout`, which is a subclass of `requests.RequestException` and is already caught by the existing handler. This eliminates all indefinite blocks in the notifier.

**Fix 2 (RECOMMENDED): Add heartbeat print in the main loop**

Add a heartbeat print every 60 seconds so the CEO can verify Bellows is alive:
```python
last_heartbeat = time.time()
while True:
    time.sleep(1)
    if time.time() - last_rescan >= rescan_interval:
        self._rescan(handler)
        last_rescan = time.time()
    if time.time() - last_heartbeat >= 60:
        print(f"Bellows: 💓 heartbeat — {datetime.now().strftime('%H:%M:%S')}")
        last_heartbeat = time.time()
```
This also serves as a canary: if the heartbeat stops appearing, the main thread is hung.

**Fix 3 (CLEANUP): Remove dead code at lines 306–313**

The stranded check and `notifier.notify_complete` at lines 306–313 are unreachable due to the logical complement relationship between the two `if` conditions above them. Removing this dead code eliminates two phantom `notifier.push()` call sites and simplifies the control flow.

### Timeline Reconstruction

- 1:13 PM: Final step log written (`success: true, stop_reason: end_turn`)
- ~1:13 PM: `run_plan` enters verdict-pending path, calls `notifier.push()` (line 274) — possibly stalls here
- ~1:13 PM: `_check_queue_drain` calls `notifier.push()` (line 454) — possibly stalls here
- Every 30s after: `_rescan` → `_consume_verdicts` → `notifier.push()` (lines 527/544) — main thread stalls here if not already blocked
- ~1:53 PM (~40 min later): force-quit required — consistent with OS-level TCP retransmission exhaustion (macOS TCP keepalive + retransmission can hold a stalled connection for 30–75+ minutes before the OS aborts it, depending on network conditions)

The 40-minute duration is consistent with a TCP connection to Pushover's API that was established (no connection error, no `RequestException`) but for which the HTTP response was never received. The OS kept retrying at the TCP layer. The fix is exclusively adding `timeout=` to `requests.post()`.

---

**Files Deposited:**
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/post-plan-hang-diagnostic-2026-04-16.md`

**Output Receipt:**
- Status: Complete
- All six questions (Q1–Q6) answered with code citations by file and line number
