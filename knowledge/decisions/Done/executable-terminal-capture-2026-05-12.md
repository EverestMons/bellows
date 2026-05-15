**project:** bellows | **type:** executable | **steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false

# Executable — Terminal output redesign + capture (Plan 1 of 2)

## Why this exists

The 2026-05-11 design diagnostic (`Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`) proposed redesigns across three surfaces. CEO locked 5 design decisions on 2026-05-12:
1. Plan grouping → slug tag only (no separator lines)
2. Heartbeat → 300s cadence, state-bearing format, suppress during recent plan activity
3. Notification coalescing → urgency-gated 30s digest — **deferred to Plan 2**
4. Terminal log retention → 14 days
5. Step JSON retention → 30 days

This plan implements Section 1 (terminal output) + Section 3 (capture/retention) of the design. Section 2 (notifications) ships in a separate Plan 2 after this lands.

**Estimated LOC:** ~183 lines touched (120 terminal + 63 capture per design Section 4.1).

## Execution Map

Step 1 (Developer) → Step 2 (Bellows QA)

## Step 1 — Developer: implement terminal output redesign + capture

You are the Bellows Developer. Read `bellows/agents/BELLOWS_DEVELOPER.md` (or the closest match in `bellows/agents/`) before starting.

### Required prior reading

Read both of these in full before writing any code:
1. `bellows/knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md` — 71-call-site inventory with line numbers
2. `bellows/knowledge/research/terminal-notification-capture-design-2026-05-11.md` — locked design

The design document IS the spec for this implementation. Where the design specifies a format string, use exactly that format string. Where the design specifies a behavior, implement exactly that behavior.

### HEAD refresh

The prior audit was authored 2026-05-11. Before migrating any call site, run `git log --oneline -- bellows.py runner.py notifier.py` since 2026-05-11 to detect drift. For each file:
- Re-grep `print(` and `sys.stdout` and `sys.stderr.write` to refresh line numbers
- If counts differ from the audit (64 in bellows.py, 6 in runner.py, 1 in notifier.py), note the delta in the dev log before proceeding

### Implementation order

Implement in stages. Do not skip ahead — each stage depends on the previous.

#### Stage 1 — Helper infrastructure

Add to `bellows.py` (location: after imports and module-level constants, before any function/class definitions):

**1a. `_log()` helper.** Single function that handles timestamp, severity bracket, optional slug tag, and routes to both stdout and the rotating file handler. Signature:

```python
def _log(level: str, message: str, slug: str | None = None) -> None:
    """
    Emit a log line with format: HH:MM:SS [LEVEL] [slug] message
    
    level: one of EVENT, INFO, WARN, ERROR, PAUSE
    message: the message text (no Bellows: prefix needed)
    slug: optional plan slug for plan-related events (omit for system events like heartbeat)
    
    Side effects:
      - Routes to the 'bellows' logger (stdout via StreamHandler, file via RotatingFileHandler)
      - If level in {EVENT, WARN, ERROR, PAUSE} AND slug is provided, updates _last_plan_event_time
    """
```

Implementation notes:
- Use `datetime.now().strftime('%H:%M:%S')` for the timestamp (matches existing heartbeat format).
- Validate `level` against the 5-level whitelist; raise `ValueError` on invalid level.
- Format: `f"{ts} [{level}] [{slug}] {message}"` when slug given, `f"{ts} [{level}] {message}"` otherwise.
- The state update for `_last_plan_event_time` happens here automatically — callers don't need to remember.

**1b. `_last_plan_event_time` state.** Module-level variable. Initialize to `0.0`. The `_log()` function updates it via `globals()['_last_plan_event_time'] = time.time()` (or equivalent — pick the cleanest pattern). Thread safety: use a `threading.Lock()` since concurrent plan threads will write to it.

**1c. Logging configuration.** Configure the `bellows` logger with two handlers in `Bellows.__init__()` or at the start of `main()` (before the banner emission):

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("bellows")
logger.setLevel(logging.DEBUG)
logger.propagate = False  # Don't bubble to root logger

# Stdout handler — what the CEO sees in terminal
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(logging.Formatter('%(message)s'))  # _log() already formats
logger.addHandler(stdout_handler)

# File handler — disk capture
os.makedirs("logs/terminal", exist_ok=True)
log_path = f"logs/terminal/bellows-{datetime.now().strftime('%Y-%m-%d')}.log"
file_handler = RotatingFileHandler(log_path, maxBytes=50*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)
```

Then `_log()` calls `logger.info(formatted_string)` (level doesn't matter since both handlers are set to DEBUG; the bracket in the message is the semantic level).

**1d. `_rotate_logs()` cleanup function.** Define as a module-level function. Called once at startup BEFORE the logging configuration in 1c (so today's file isn't deleted on startup). Logic:

```python
def _rotate_logs() -> None:
    """Age-based cleanup at startup. Logs deletions via print() (logger not yet configured)."""
    now = time.time()
    # Terminal logs: 14 days
    terminal_dir = "logs/terminal"
    if os.path.isdir(terminal_dir):
        for fname in os.listdir(terminal_dir):
            fpath = os.path.join(terminal_dir, fname)
            if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > 14 * 86400:
                os.remove(fpath)
                print(f"Bellows: rotated terminal log {fname} (>14 days)")
    # Step JSON: 30 days
    logs_dir = "logs"
    if os.path.isdir(logs_dir):
        for fname in os.listdir(logs_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(logs_dir, fname)
            if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > 30 * 86400:
                os.remove(fpath)
                print(f"Bellows: rotated step JSON {fname} (>30 days)")
    # Planner consultation: 10MB
    consult_path = os.path.join(logs_dir, "planner-consultation.jsonl")
    if os.path.isfile(consult_path) and os.path.getsize(consult_path) > 10 * 1024 * 1024:
        # Simple rotation: rename to .1, delete .1 if it existed
        old_path = consult_path + ".1"
        if os.path.exists(old_path):
            os.remove(old_path)
        os.rename(consult_path, old_path)
        print(f"Bellows: rotated planner-consultation.jsonl (>10MB)")
```

Call `_rotate_logs()` once at startup, before logging configuration.

**1e. Session-start log line.** Immediately after the banner emission (currently `bellows.py:1173–1181`), emit:

```python
_log("INFO", f"session log: {log_path}")
```

Where `log_path` is the path computed in 1c. For session restarts (file already exists at startup), emit a restart separator first:

```python
if log_existed_before_session:
    _log("INFO", "── session restart ──────────────────────────────")
_log("INFO", f"session log: {log_path}")
```

Compute `log_existed_before_session` by checking `os.path.exists(log_path)` BEFORE the `RotatingFileHandler` is constructed.

#### Stage 2 — `bellows.py` call-site migration (64 sites)

Migrate every `print(` call in `bellows.py` to `_log()`. Use the audit's call-site inventory (Section A.1 of the surface audit) as the master list — that audit categorized all 64 sites. For each site, refer to the design document's Section 1.5 prefix-unification table for the new level/source mapping.

Migration rules:
- **Startup banner (8 sites at 1173–1181):** keep as `print()` — these fire before logging is configured. They are the only legitimate remaining `print()` calls in `bellows.py`.
- **All other 56 sites:** migrate to `_log(level, message, slug=...)` per the design's prefix-unification table.

Examples (illustrative — apply pattern to all call sites):

```python
# Before:
print(f"Bellows: detected plan {filename}")
# After:
_log("EVENT", f"⏳ detected and claimed ({total_steps} steps)", slug=slug_for(filename))
```

```python
# Before:
print(f"Bellows: gates for {plan_name} step {current_step}: passed={gate_result['passed']}, is_qa={gate_result['is_qa_step']}, failures={len(gate_result['failures'])}")
# After:
_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])}", slug=slug_for(plan_name))
```

```python
# Before:
print(f"Bellows: ⏸️  PAUSED — {plan_name} step {current_step} — waiting for CEO verdict")
# After:
_log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
```

Slug derivation: define `slug_for(plan_name)` as a helper that strips `.md`, strips `in-progress-`/`verdict-pending-`/`halted-` prefixes if present, and strips the trailing date suffix (`-YYYY-MM-DD`). Truncate to 30 chars if longer.

For multi-occurrence anchors (e.g., the gate-evaluation print appears at both 373 and 458 with identical format), use surrounding context in the `edit_block` `old_string` to disambiguate.

#### Stage 3 — `runner.py` call-site migration (6 sites)

Add `from bellows import _log` (or whatever import path works) at the top of `runner.py`. Then migrate all 6 print calls.

The 3 runner heartbeat sites (114, 119, 126) must accept and emit slug + step. Modify `run_step()`'s signature if necessary to plumb the slug and step number through. Per design Section 1.4:

```python
# Before (runner.py:114):
print(f"Bellows: runner — {int(elapsed)}s elapsed, last output {int(age)}s ago", flush=True)
# After:
_log("INFO", f"runner: {int(elapsed)}s elapsed, last output {int(age)}s ago (step {step_num})", slug=plan_slug)
```

The 3 debug/error sites (167, 190, 201) become WARN or ERROR per design Section 1.7 Example 3.

**Important:** runner heartbeats should NOT update `_last_plan_event_time` (per design Section 1.6 — runner heartbeats are activity signals, not plan events, and updating the timer would suppress the main heartbeat indefinitely during long step execution). Either:
- (a) `_log()` checks an additional flag and skips the state update when called from runner.py's heartbeat sites, OR
- (b) the 3 runner-heartbeat call sites pass slug but call `_log()` with a `suppress_timer_update=True` parameter.

Pick whichever pattern is cleaner. Document the choice in the dev log.

#### Stage 4 — `notifier.py` call-site migration (1 site)

Migrate `notifier.py:25` (stderr Pushover error) to `_log("ERROR", f"notifier: {e}")`. Since `_log()` routes through the `bellows` logger to stdout, this changes stderr→stdout for the Pushover error line. That's an acceptable consequence — the dev log should note it.

If routing to stderr is essential, add a `to_stderr=True` parameter to `_log()` that selects a stderr-routed handler. The design doesn't address this explicitly; pick the cleaner option and note the choice.

#### Stage 5 — Heartbeat redesign

Modify the heartbeat block in `bellows.py:1209–1215` per design Section 1.6 (combined policy):
- Change cadence from 60s to 300s
- Add state-bearing format: `_log("INFO", f"heartbeat: {n_in_flight} in-flight, {n_pending} awaiting verdict")` or `_log("INFO", "heartbeat: idle")` when both counts are zero
- Suppress the heartbeat entirely if `time.time() - _last_plan_event_time < 120` (the audit-recommended suppression window)
- Module fingerprint sub-block: keep cadence at every 10th heartbeat (now 50 minutes between fingerprints). Compute counts via existing in-flight tracking — read the surrounding code to find the right state variables.

#### Stage 6 — Final wiring

- Move `last_heartbeat` and `heartbeat_counter` from `Bellows.start()` locals to wherever they coexist cleanly with the new `_last_plan_event_time` (likely instance attributes on `Bellows` if other tracking lives there, or module-level globals otherwise — pick consistent with the existing style).
- Verify no `Bellows:` prefix remains in any migrated call site (the new format doesn't use it).

### Commit

After all stages complete and any test fixes land, commit with:

```
git add bellows/bellows.py bellows/runner.py bellows/notifier.py
git commit -m "feat(observability): terminal output redesign + log capture (Plan 1)

- Add _log() helper with 5-level severity taxonomy (EVENT/INFO/WARN/ERROR/PAUSE)
- Migrate 71 print calls to _log() with timestamp + bracket + optional slug
- Add Python logging with RotatingFileHandler → logs/terminal/bellows-YYYY-MM-DD.log
- Heartbeat: 300s cadence, state-bearing, suppress within 120s of plan event
- Runner heartbeats now carry plan slug + step number
- Log rotation: terminal 14d, step JSON 30d, planner-consultation 10MB
- Drop Bellows:/runner —/[runner] prefix inconsistency"
```

Capture commit SHA for dev log.

### Tests

The existing test suite (177→190 per memory) must still pass. Run `pytest tests/ -v` after all migrations and report results in the dev log. If any tests fail, they likely assert specific print() output strings — investigate each failure:
- If the test asserts the OLD format, update the test to assert the new `_log()` format.
- If the test mocks `print`, update it to mock `_log` or the logger.
- Do NOT skip or delete tests.

Report any test count delta in the dev log.

### Out of scope

- Do NOT implement notification coalescing, dead-code cleanup of `notify_escalation`/`notify_complete`, or `config.notifications` schema. That's Plan 2.
- Do NOT change verdict lifecycle, gates, plan parsing, or `RULE_20_SELF_CHECK_BLOCK.md`.
- Do NOT add ANSI color output. Design Section 1.1 explicitly defers color.
- Do NOT push to remote. Local commit only.

### Deliverables

- `bellows.py`, `runner.py`, `notifier.py` updated per stages 1–6
- All existing tests pass (or are updated to assert new format and pass)
- Dev log at `bellows/knowledge/development/terminal-capture-dev-log-2026-05-12.md` capturing:
  - HEAD refresh result: call-site delta vs prior audit (or "no change")
  - Per-stage completion checklist (1a–1e, 2, 3, 4, 5, 6)
  - Design choices made on the two open patterns (Stage 3 runner-suppression mechanism, Stage 4 stderr routing)
  - Commit SHA
  - Test result: count before/after, any tests modified (with rationale)
  - Output Receipt

**Deposits:**
- `bellows/knowledge/development/terminal-capture-dev-log-2026-05-12.md`

## Step 2 — Bellows QA: Verify terminal redesign + capture

You are the Bellows QA specialist. Read `bellows/agents/BELLOWS_QA.md` before starting.

### Context

Step 1 implemented the terminal output redesign + capture per design Sections 1 + 3. Read the dev log at `bellows/knowledge/development/terminal-capture-dev-log-2026-05-12.md` and the design document at `bellows/knowledge/research/terminal-notification-capture-design-2026-05-11.md` before verifying.

This is **code-level-only QA** — do NOT run Bellows live. The hot-reload gap noted in memory means a live integration test would trip the very bugs we're trying to fix mid-flight. Use static analysis, grep, and pytest only.

### Task

1. **`_log()` helper presence.** Confirm `bellows.py` defines `_log(level, message, slug=None)`. Confirm it produces format `HH:MM:SS [LEVEL] [slug] message` when slug given, `HH:MM:SS [LEVEL] message` otherwise. Confirm it validates level against the 5-level whitelist.

2. **Print call audit.** Run `grep -n "print(" bellows/bellows.py bellows/runner.py bellows/notifier.py`. Expected results:
   - `bellows.py`: 8–10 matches (only the startup banner block at 1173–1181, plus possibly the 3 `_rotate_logs()` print calls if those are kept as print since they fire before logger setup)
   - `runner.py`: 0 matches
   - `notifier.py`: 0 matches (the stderr print was migrated to `_log("ERROR", ...)`)
   
   Cite every remaining `print()` call site and confirm each is legitimate per the migration rules in Step 1.

3. **`Bellows:` prefix audit.** Run `grep -n "Bellows:" bellows/bellows.py bellows/runner.py bellows/notifier.py`. Expected: matches ONLY in the startup banner (`bellows.py:1173–1181`) and in `_rotate_logs()` print fallbacks. No other `Bellows:` prefix should remain. The `[runner]` prefix should appear 0 times.

4. **Logging configuration.** Confirm `bellows.py` configures the `bellows` logger with both `StreamHandler` (stdout) and `RotatingFileHandler` pointing at `logs/terminal/bellows-YYYY-MM-DD.log` with 50MB rotation and 5 backups. Confirm `propagate = False`.

5. **Rotation function.** Confirm `_rotate_logs()` exists and is invoked at startup BEFORE logger configuration. Confirm it deletes:
   - Files in `logs/terminal/` older than 14 days
   - `.json` files in `logs/` older than 30 days
   - Rotates `logs/planner-consultation.jsonl` when >10MB

6. **Heartbeat redesign.** Read the heartbeat block (was at `bellows.py:1209–1215`). Confirm:
   - Cadence is 300s (not 60s)
   - State-bearing format includes in-flight count and verdict-pending count
   - Suppression: if `time.time() - _last_plan_event_time < 120`, the heartbeat is skipped
   - Module fingerprint sub-block fires every 10th heartbeat (now 50min cadence)

7. **Runner heartbeat carries plan identity.** Confirm `runner.py` heartbeats include slug + step number in the message. Confirm runner heartbeats do NOT update `_last_plan_event_time` (else they'd suppress the main heartbeat indefinitely during long steps).

8. **Format spot-checks.** Pick 5 migrated call sites from different categories (plan detection, gate eval, verdict pause, worktree warning, mode A error). For each, confirm the new format matches design Section 1.7's worked examples in spirit (timestamps present, severity bracket correct, slug present, no legacy prefix).

9. **Test suite.** Run `pytest tests/ -v` and capture the result. Confirm all tests pass. Compare test count to the prior baseline (190 per memory). If count changed, confirm the dev log explains why.

10. **Static format-string validation.** For every `_log()` call site, confirm:
    - First arg is one of `"EVENT"`, `"INFO"`, `"WARN"`, `"ERROR"`, `"PAUSE"` (no others)
    - No `Bellows:` prefix in message arg
    - No leading timestamp (the helper adds it)
    Use grep + manual inspection.

11. **Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use:
    - `plan_slug`: `executable-terminal-capture-2026-05-12`
    - `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/terminal-capture-qa-2026-05-12.md`
    - `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-terminal-capture-2026-05-12/`
    - `required_evidence_files`:
      - `print_audit.txt` — grep output from check 2
      - `bellows_prefix_audit.txt` — grep output from check 3
      - `log_helper_present.txt` — quoted `_log()` definition
      - `heartbeat_block.txt` — quoted new heartbeat block
      - `pytest_result.txt` — full pytest output from check 9

### Deliverables

- QA report at `bellows/knowledge/qa/terminal-capture-qa-2026-05-12.md` with verification table covering checks 1–11, the literal Rule 20 self-check stdout, and an Output Receipt.
- Evidence directory at `bellows/knowledge/qa/evidence/executable-terminal-capture-2026-05-12/` containing the 5 files listed above.

**Deposits:**
- `bellows/knowledge/qa/terminal-capture-qa-2026-05-12.md`
- `bellows/knowledge/qa/evidence/executable-terminal-capture-2026-05-12/`
