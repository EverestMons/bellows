**project:** bellows | **type:** executable | **steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false

# Executable — Notification coalescing + dead-code cleanup (Plan 2 of 2)

## Why this exists

The 2026-05-11 design diagnostic (`Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`) Section 2 proposed notification coalescing, priority/sound mapping, configurability, and dead-code cleanup. CEO locked the coalescing decision on 2026-05-12: **Alternative A — urgency-gated with 30s digest window**.

Plan 1 (`Done/executable-terminal-capture-2026-05-12.md`, commit `b11ecc4`) shipped terminal output redesign + capture. This is Plan 2 of 2 from the original design roadmap. After this, the BACKLOG entry `2026-04-19: terminal output redesign + notification audit` can be closed.

**Estimated LOC:** ~140 lines touched (~60 new named functions + ~45 coalescing logic + ~10 migrations + ~10 config + ~10 example.json - 20 dead-code deletion per design Section 4.1).

## Execution Map

Step 1 (Developer) → Step 2 (Bellows QA)

## Step 1 — Developer: implement notification coalescing + dead-code cleanup

You are the Bellows Developer. Read `bellows/agents/BELLOWS_DEVELOPER.md` (or the closest match in `bellows/agents/`) before starting.

### Required prior reading

Read all three before writing any code:
1. `bellows/knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md` — notification call-site inventory (B.7–B.10)
2. `bellows/knowledge/research/terminal-notification-capture-design-2026-05-11.md` — locked design Section 2
3. `bellows/knowledge/development/terminal-capture-dev-log-2026-05-12.md` — Plan 1 dev log (shows current state of `notifier.py`)

### HEAD refresh

Plan 1 modified `notifier.py` to migrate its single `print(file=sys.stderr)` call to `_log("ERROR", ...)`. Read current HEAD of `bellows/notifier.py` and `bellows/bellows.py` before drafting. Note any unexpected drift since Plan 1 (commit `b11ecc4`).

### Implementation order

#### Stage 1 — Dead-code deletion

Delete two unused functions from `notifier.py`:
- `notify_escalation()` (per audit B.7 — defined but never called)
- `notify_complete()` (per audit B.7 — defined but never called, superseded by direct `push()` calls)

Verify via grep that nothing imports or calls them before deletion:
```
grep -rn "notify_escalation\|notify_complete" bellows/
```

Expected: 0 results outside `notifier.py` itself.

#### Stage 2 — New named notification functions

Add 5 new functions to `notifier.py` per design Section 2.4. Each function:
- Checks `config.notifications.enabled` and `config.notifications.events.<event_name>` before any side effect
- Sets the Pushover priority and sound per design Section 2.2 priority/sound mapping
- Routes through the coalescing buffer (Stage 3) for non-urgent events; pushes immediately for urgent events
- Returns the result of the underlying `push()` call (or `True` if buffered, `False` if disabled)

Functions to add:

| Function | Urgency | Priority | Sound | Buffering |
|----------|---------|----------|-------|-----------|
| `notify_plan_complete(plan_name, total_cost)` | deferred | 0 (normal) | none (silent) | buffer |
| `notify_plan_halted(plan_name)` | deferred | 0 (normal) | none (silent) | buffer |
| `notify_plan_skipped(plan_name)` | deferred | -1 (low) | none (silent) | buffer |
| `notify_queue_empty()` | deferred | 0 (normal) | none (silent) | buffer |
| `notify_failure(plan_name, step, error)` — EXISTS, update | urgent | 1 (high) | falling | immediate, but flush buffer first |

Also update existing `notify_verdict_request(plan_name, step, gate_failures)`:
- Urgent: priority 1 (high), sound default
- Push immediately, but flush the buffer first (so the CEO sees pending completions before the verdict request, matching event order)

Title format for each (per design 2.8 worked examples and existing format conventions):
- `notify_plan_complete`: title `"Bellows — Plan Complete"`, message `f"Plan: {plan_name}\nTotal cost: ${total_cost:.4f}"`
- `notify_plan_halted`: title `"Bellows — Plan Halted"`, message `f"Plan {plan_name} halted by Planner verdict."`
- `notify_plan_skipped`: title `"Bellows — Skipped"`, message `f"Plan {plan_name} has no STEP headers — moved to Done without executing."`
- `notify_queue_empty`: title `"Bellows — Queue Empty"`, message `"All plans complete. Ready for Forge cycle."`

Internal helper: extract the Pushover priority/sound parameter handling into `push()` itself if not already there. Add `priority: int = 0` and `sound: str | None = None` keyword args to `push()`. Pass through to the Pushover API `data` dict.

#### Stage 3 — Coalescing buffer + timer thread

Add to `notifier.py`:

**3a. Buffer state.**
```python
_buffer: list[dict] = []  # Each entry: {"function": "notify_plan_complete", "args": (...), "kwargs": {...}}
_buffer_lock = threading.Lock()
_timer: threading.Timer | None = None
_timer_lock = threading.Lock()
```

**3b. `_enqueue_deferred(event_type, **payload)` function.** Called by the deferred named functions. Appends the event to `_buffer` under lock, then resets the 30s timer. If timer was already running, cancel it and start a fresh 30s timer. When the timer fires, call `_flush_buffer()`.

**3c. `_flush_buffer()` function.** Acquires `_buffer_lock`, drains the buffer into a local list, releases the lock. Builds a single coalesced digest message from the drained events. Calls `push()` with the digest. Resets timer state under `_timer_lock`.

Digest format (per design Section 2.5 worked examples):
- Title: `"Bellows — Session Update"` (or context-appropriate variant)
- Message: human-readable summary, e.g., `"3 plans complete: executable-foo ($0.0423), diagnostic-bar ($0.0112), executable-baz ($0.0301). Queue empty."` for the simple case.

Build the digest by event type:
- Group `plan_complete` events into one bullet: `"N plans complete: name1 ($cost1), name2 ($cost2), ..."`
- Group `plan_halted` into `"N plans halted: name1, name2, ..."`
- Group `plan_skipped` into `"N plans skipped: name1, name2, ..."`
- `queue_empty` becomes a trailing line `"Queue empty."` (or `"N plans awaiting verdict."` if there are verdict-pending plans — read this from a state hook if available, else just say "Queue empty.")

**3d. `_flush_buffer_immediate()` helper.** Called by urgent notifications (`notify_failure`, `notify_verdict_request`) BEFORE they push their own message. Forces an immediate flush of any pending buffered events. This ensures the CEO sees pending completion summaries before an urgent verdict request lands. Cancels any active timer.

**3e. Coalesce window from config.** Read `coalesce_window_seconds` from `config.notifications` (default 30). Pass to the timer. If 0, skip buffering entirely (revert to one-push-per-event for testing or rollback).

#### Stage 4 — Config schema

Add `notifications` section to `config.json` and `config.example.json` per design Section 2.3:

```json
{
  "notifications": {
    "enabled": true,
    "events": {
      "verdict_needed": true,
      "failure": true,
      "plan_complete": true,
      "plan_halted": true,
      "plan_skipped": true,
      "queue_empty": true
    },
    "coalesce_window_seconds": 30
  }
}
```

- Add to BOTH `config.json` (production, all events enabled) and `config.example.json` (template).
- Add config loading in `bellows.py` or wherever config is loaded today. The block should be additive — if missing in old config files, default to all-enabled with 30s window.
- Existing `pushover.app_key` and `pushover.user_key` fields are unchanged.

#### Stage 5 — Migrate direct `push()` calls in `bellows.py`

Per design Section 2.4, migrate the 5 direct `notifier.push()` call sites in `bellows.py` to named functions. The audit Section B.7 lists them; current line numbers may have shifted after Plan 1 — re-grep before editing.

Migrations:
- `bellows.py:294` (or wherever it now lives): direct `push("Bellows — Skipped", ...)` → `notifier.notify_plan_skipped(plan_name)`
- `bellows.py:534–535` (auto-close success): `push("Bellows — Plan Complete", ...)` → `notifier.notify_plan_complete(plan_name, total_cost)`
- `bellows.py:929` (queue empty): `push("Bellows — Queue Empty", ...)` → `notifier.notify_queue_empty()`
- `bellows.py:1067–1068` (continue-verdict-to-done): `push("Bellows — Plan Complete via Verdict", ...)` → `notifier.notify_plan_complete(original_name, total_cost)` (NOTE: the design unifies this with regular plan-complete since the CEO doesn't need to distinguish them in a digest)
- `bellows.py:1089–1090` (stop verdict): `push("Bellows — Plan Halted", ...)` → `notifier.notify_plan_halted(original_name)`

After migration, grep for `notifier.push(` in `bellows.py` — expected: **0 matches**. All notification intent must flow through named functions.

#### Stage 6 — Final wiring

- Confirm `notify_failure()` is still called from the unhandled-exception path in `run_plan()` (was `bellows.py:541` per audit).
- Confirm `notify_verdict_request()` is still called from verdict-pause sites (was `bellows.py:400–401` and `486–487` per audit).
- Both should now flush the buffer first before pushing.

### Commit

After all stages complete and tests pass:

```
git add bellows/notifier.py bellows/bellows.py bellows/config.json bellows/config.example.json
git commit -m "feat(notifications): urgency-gated coalescing + dead-code cleanup (Plan 2)

- Add 5 named notification functions; remove 2 dead-code functions
- All 5 direct notifier.push() calls migrated to named functions
- Urgency-gated coalescing: verdict-needed/failure push immediately,
  completions/halted/skipped/queue-empty buffer for 30s then digest
- Pushover priority/sound mapping per event type
- notifications config block (enabled toggle + per-event toggles + window)
- 5-plan completion session: 6 pushes → 1 digest"
```

Capture commit SHA for dev log.

### Tests

Existing test suite (269 per Plan 1 baseline) must still pass. Run `pytest tests/ -v` after changes.

New tests welcome but not required by this plan. If you add tests for the coalescing logic, keep them focused (assert that 3 plan_complete calls within 30s produce 1 push, not 3; assert that notify_failure flushes the buffer first; etc.). Do NOT add tests that require real Pushover API calls.

If existing tests fail because they assert on `notifier.push()` call counts, update them to assert on `notify_*` function call counts instead. Document any test changes in the dev log.

### Out of scope

- Do NOT change the terminal output / logging system (Plan 1 territory).
- Do NOT change verdict lifecycle, gates, plan parsing.
- Do NOT add new Pushover API parameters beyond priority and sound.
- Do NOT add SMS/email/Discord/Slack notification channels. Pushover only.
- Do NOT push to remote. Local commit only.

### Deliverables

- `bellows/notifier.py` updated per stages 1–3
- `bellows/bellows.py` updated per stages 5–6
- `bellows/config.json` and `bellows/config.example.json` updated per stage 4
- Dev log at `bellows/knowledge/development/notification-coalescing-dev-log-2026-05-12.md` capturing:
  - HEAD refresh result vs Plan 1 commit `b11ecc4`
  - Per-stage completion checklist (1–6)
  - Commit SHA
  - Test results (count before/after, any tests modified)
  - Confirmation that 0 direct `notifier.push()` calls remain in `bellows.py`
  - Output Receipt

**Deposits:**
- `bellows/knowledge/development/notification-coalescing-dev-log-2026-05-12.md`

## Step 2 — Bellows QA: Verify notification coalescing

You are the Bellows QA specialist. Read `bellows/agents/BELLOWS_QA.md` before starting.

### Context

Step 1 implemented Plan 2 per design Section 2. Read the dev log at `bellows/knowledge/development/notification-coalescing-dev-log-2026-05-12.md` and design Section 2 before verifying.

This is **code-level-only QA** — do NOT run Bellows live, do NOT make real Pushover API calls.

### Task

1. **Dead-code deletion.** Run `grep -rn "notify_escalation\|notify_complete" bellows/`. Expected: 0 matches anywhere.

2. **New named functions present.** Confirm `notifier.py` defines 4 new functions (existing `notify_failure` and `notify_verdict_request` are kept):
   - `notify_plan_complete(plan_name, total_cost)`
   - `notify_plan_halted(plan_name)`
   - `notify_plan_skipped(plan_name)`
   - `notify_queue_empty()`
   
   Confirm each checks the config gate (`config.notifications.enabled` and `config.notifications.events.<event_name>`) before any side effect.

3. **Priority/sound mapping.** Spot-check each named function sets the correct Pushover priority and sound per design Section 2.2:
   - `notify_verdict_request`: priority 1, default sound
   - `notify_failure`: priority 1, sound "falling"
   - `notify_plan_complete/halted/queue_empty`: priority 0, sound "none"
   - `notify_plan_skipped`: priority -1, sound "none"

4. **Coalescing buffer state.** Confirm `notifier.py` defines `_buffer`, `_buffer_lock`, `_timer`, `_timer_lock` at module level. Confirm thread safety: every read/write to `_buffer` is under `_buffer_lock`; every read/write to `_timer` is under `_timer_lock`.

5. **Coalescing logic.** Confirm:
   - `_enqueue_deferred()` appends to buffer, cancels any active timer, starts a fresh 30s (or `coalesce_window_seconds`) timer
   - When timer fires, `_flush_buffer()` builds digest, calls `push()` once
   - `_flush_buffer_immediate()` is callable from urgent functions and forces immediate digest before urgent push

6. **Urgent flush-first pattern.** In `notify_failure` and `notify_verdict_request`, confirm the buffer is flushed BEFORE the urgent push fires. Cite the line numbers.

7. **Config schema.** Confirm both `config.json` and `config.example.json` contain the `notifications` block with all 6 event toggles + `enabled` + `coalesce_window_seconds`. Confirm config loading defaults to all-enabled with 30s window when the block is missing (backward compat).

8. **Direct `push()` call migration.** Run `grep -n "notifier.push(" bellows/bellows.py`. Expected: **0 matches**. All calls must flow through named functions.

9. **Direct `push()` calls in notifier.py.** Run `grep -n "push(" bellows/notifier.py`. Expected: only `_flush_buffer()` and direct urgent paths in `notify_failure`/`notify_verdict_request` call `push()` directly. Cite each.

10. **Test suite.** Run `pytest tests/ -v`. Confirm count is ≥269 (Plan 1 baseline) and all tests pass (excluding the pre-existing `test_run_step_timeout` failure documented in Plan 1).

11. **Static call-graph check.** For each of the 5 events (verdict_needed, failure, plan_complete, plan_halted, plan_skipped, queue_empty), trace the call graph from the triggering site in `bellows.py` through to `push()`. Confirm each path passes through the appropriate named function and that the config gate is checked.

12. **Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use:
    - `plan_slug`: `executable-notification-coalescing-2026-05-12`
    - `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/notification-coalescing-qa-2026-05-12.md`
    - `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/`
    - `required_evidence_files`:
      - `dead_code_audit.txt` — grep from check 1
      - `direct_push_audit.txt` — grep from check 8
      - `notifier_functions.txt` — quoted function signatures
      - `config_diff.txt` — diff of config.example.json showing the new block
      - `pytest_result.txt` — full pytest output from check 10

### Deliverables

- QA report at `bellows/knowledge/qa/notification-coalescing-qa-2026-05-12.md` with verification table covering checks 1–12, the literal Rule 20 self-check stdout, and an Output Receipt.
- Evidence directory at `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/` containing the 5 files listed above.

**Deposits:**
- `bellows/knowledge/qa/notification-coalescing-qa-2026-05-12.md`
- `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/`
