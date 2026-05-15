# Terminal Output, Notification, and Capture — Redesign Proposals

**Date:** 2026-05-11
**Author:** Bellows Systems Analyst
**Type:** Diagnostic — design proposals (no code changes)
**Source plan:** `knowledge/decisions/in-progress-diagnostic-terminal-notification-capture-design-2026-05-11.md`
**Prior audit:** `knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md`

---

## Executive Summary

Bellows's terminal output, Pushover notifications, and log capture currently have three structural gaps: (1) plan lifecycle events lack timestamps and severity, heartbeats lack plan identity, and no visual grouping separates concurrent plans; (2) every notification event fires independently with no coalescing, priority, or configurability; (3) terminal output is entirely ephemeral — lost on restart or scrollback overflow. This document proposes concrete redesigns for each surface with alternatives where tradeoffs are real, before/after examples drawn from the audit's reconstructed sequences, LOC estimates, and an implementation roadmap. No code changes are included; the CEO marks up or accepts each proposal before implementation begins.

---

## Section 1 — Terminal Output Redesign

### 1.1 — Severity Taxonomy

The audit found no structured severity system — differentiation relies on 7 emoji types and 3 inconsistent prefix conventions (C.11 item 3).

**Proposal: Hybrid bracketed-prefix + emoji**

Define five severity levels. Each line gets a machine-parseable bracketed prefix AND the existing emoji where one exists. The bracket enables grep/awk filtering; the emoji preserves quick human scanning.

| Level | Bracket | When it fires | Emoji (kept) |
|-------|---------|---------------|--------------|
| `EVENT` | `[EVENT]` | Plan detection, claim, dispatch, gate pass, auto-close, verdict consumption, queue drain | ⏳ ▶ ✅ 🏁 as today |
| `INFO` | `[INFO]` | Heartbeat, module fingerprint, plan metadata (step count, model override, cache hit) | None |
| `WARN` | `[WARN]` | Sparse header defaults, skipped plans, stale verdicts, worktree warnings, lock removal | ⚠️ |
| `ERROR` | `[ERROR]` | Failures: unhandled exception, Mode A, worktree creation/teardown failure, runner kill | ❌ |
| `PAUSE` | `[PAUSE]` | Verdict pause (all pause reasons) | ⏸️ |

**Tradeoffs considered:**

- *Machine-parseability vs. density:* Brackets add 7–8 characters per line. Acceptable — they enable `grep '\[ERROR\]' bellows-session.log` which is currently impossible.
- *Color (ANSI escapes):* Not proposed. Bellows runs in a single terminal pane that may be a `screen`/`tmux` session where ANSI codes can corrupt scrollback capture. Color can be added later as an opt-in config flag; the bracket taxonomy works without it.
- *Emoji removal:* Not proposed. Emoji provide instant visual landmarks in scrollback. The brackets add machine-parseability on top.

### 1.2 — Timestamp Policy

The audit found timestamps on only 2 of 71 call sites — heartbeat (`HH:MM:SS`) and runner heartbeat (relative elapsed/age). All plan lifecycle events have no temporal marker (C.11 item 2).

**Proposal: Every line gets an absolute `HH:MM:SS` timestamp**

Format: `HH:MM:SS [LEVEL] message`

Rationale for absolute over relative-to-session-start: Bellows sessions can span hours. Absolute time lets the CEO correlate terminal lines with external events (Pushover notification timestamps, git commit times, meeting interruptions). Relative time requires mental arithmetic.

Rationale for time-only over date+time: Bellows sessions rarely span midnight. For the rare case they do, the session log filename carries the date. Adding `YYYY-MM-DD` to every line wastes 11 characters of the ~120 usable columns.

**Tradeoff:** Density. Each line grows by 9 characters (`HH:MM:SS `). For a CEO reading scrollback, this is worth it — the audit's "before" examples show that post-hoc timeline reconstruction is currently impossible.

### 1.3 — Plan Grouping

The audit found no visual separation between plans (C.11 item 5). The worst-case interleaving example shows heartbeats and events from 2 plans mixed into an undifferentiated stream.

**Alternative A — Slug tag on every plan line (minimal change)**

Every plan-related line includes a short slug tag in brackets after the severity. Non-plan lines (heartbeat, startup, queue drain) omit the tag.

Format: `HH:MM:SS [LEVEL] [slug] message`

Where `slug` is the plan filename minus the date suffix and `.md`, truncated to 30 chars. Example: `executable-foo` from `executable-foo-2026-05-11.md`.

Pros: No blank lines or separators that consume vertical space. Works naturally with interleaving — each line is self-identifying. Machine-filterable via `grep '\[executable-foo\]'`.

Cons: Adds 10–30 characters per line. Does not visually group sequential events from the same plan.

**Alternative B — Slug tag + separator lines at lifecycle boundaries**

Same slug tag as Alternative A, but additionally emit a thin separator line at plan start and plan terminal state (pause/complete/fail):

```
─── executable-foo ───────────────────────────────
```

Pros: Visual grouping for sequential reading. Easy to spot plan boundaries in scrollback.

Cons: Each plan adds 2–4 separator lines. With 5 concurrent plans, separators interleave with each other and become noise. Works best for sequential or low-concurrency sessions.

**Recommendation:** Alternative A is the safer default for a concurrent-plan system. Alternative B can be layered on later if the CEO finds scrollback hard to parse even with slug tags. The worked examples below use Alternative A.

### 1.4 — Runner Heartbeat Redesign

The audit found runner heartbeats carry no plan identity — `"Bellows: runner — 120s elapsed, last output 45s ago"` is ambiguous with concurrent plans (C.11 item 4).

**Proposal: Add plan slug and step number to runner heartbeat**

New format: `HH:MM:SS [INFO] [slug] runner: {elapsed}s elapsed, last output {age}s ago (step {N})`

Example: `14:33:07 [INFO] [executable-foo] runner: 120s elapsed, last output 45s ago (step 1)`

Implementation: `runner.py`'s `run_step()` already receives the plan path. Extract the slug and step number, pass them to the heartbeat print.

### 1.5 — Prefix Unification

The audit found four coexisting prefix conventions: `Bellows:`, `Bellows: runner —`, `[runner]`, `Pushover error:` (C.11 item 3).

**Proposal: Eliminate all legacy prefixes — the timestamp+bracket+slug format replaces them**

Current prefixes are vestigial — they were the only way to identify the event source. With the new format, source is encoded in the bracket level and slug tag:

| Current prefix | New format component |
|----------------|---------------------|
| `Bellows:` | Dropped — `[EVENT]`, `[INFO]`, etc. carry the meaning |
| `Bellows: runner —` | `[INFO] [slug] runner:` |
| `[runner]` | `[WARN] [slug] runner:` or `[ERROR] [slug] runner:` (depending on the event) |
| `Pushover error:` (stderr) | `[ERROR] notifier:` (still to stderr) |

All lines now share a single format: `HH:MM:SS [LEVEL] [optional-slug] source: message`. The `Bellows:` prefix is not needed because every line comes from Bellows — the prefix was redundant.

### 1.6 — Heartbeat Suppression Policy

The audit found heartbeats fire every 60s regardless of activity, dominating idle scroll (C.11 item 1).

**Alternative A — Suppress when plan events have fired recently**

Policy: Skip heartbeat if any plan event has been printed in the last 120 seconds. This means:
- During active step execution: runner heartbeats fire (they carry plan identity now), main heartbeat is suppressed.
- During idle periods: main heartbeat fires as liveness signal.
- During verdict-wait periods: main heartbeat fires (no plan events are printing).

Implementation: Track `last_plan_event_time` globally, check it in the heartbeat block.

Pros: Drastically reduces noise during active execution (the noisiest period). Preserves liveness signal when actually idle.

**Alternative B — Increase cadence to 5 minutes, add state summary**

Policy: Change heartbeat from 60s to 300s. Add state information: in-flight plan count, verdict-pending count.

New format: `HH:MM:SS [INFO] heartbeat: 2 in-flight, 1 awaiting verdict`

Or when fully idle: `HH:MM:SS [INFO] heartbeat: idle`

Pros: Heartbeats become useful — they carry system state. 5× fewer heartbeat lines.

Cons: 5-minute gap between liveness signals. If the CEO glances at the terminal and last heartbeat was 4 minutes ago, they can't tell if Bellows is hung.

**Recommendation:** Combine both: use Alternative B's format (state-bearing heartbeat at 300s) with Alternative A's suppression (skip if plan events are recent). This gives meaningful heartbeats during idle periods and silence during active execution.

### 1.7 — Worked Examples

All examples use Alternative A (slug tags, no separators) and the combined heartbeat policy.

#### Example 1 — Single 1-step diagnostic, idle-then-execute-then-pause

**Before** (from audit A.4):
```
Bellows: heartbeat — 14:30:07
Bellows: heartbeat — 14:31:07
Bellows: detected plan diagnostic-foo-2026-05-11.md
Bellows: ⏳ RUNNING — diagnostic-foo-2026-05-11.md
Bellows: plan has 1 steps
Bellows: ▶ started diagnostic-foo-2026-05-11.md
Bellows: heartbeat — 14:32:07
Bellows: runner — 60s elapsed, last output 12s ago
Bellows: heartbeat — 14:33:07
Bellows: gates for diagnostic-foo-2026-05-11.md step 1: passed=True, is_qa=False, failures=0
Bellows: ⏸️  PAUSED — diagnostic-foo-2026-05-11.md step 1 — waiting for CEO verdict
Bellows: 🏁 Queue empty — all plans complete
```

**After:**
```
14:30:07 [INFO] heartbeat: idle
14:31:12 [EVENT] [diagnostic-foo] ⏳ detected and claimed (1 step)
14:31:14 [EVENT] [diagnostic-foo] ▶ started
14:32:14 [INFO] [diagnostic-foo] runner: 60s elapsed, last output 12s ago (step 1)
14:33:20 [EVENT] [diagnostic-foo] gates step 1: passed=True, failures=0
14:33:20 [PAUSE] [diagnostic-foo] ⏸️ step 1 — waiting for CEO verdict
14:33:20 [EVENT] 🏁 queue empty — all plans complete
```

Lines: 12 → 7. Heartbeat noise during execution eliminated. Every line has a timestamp. Plan identity on every plan line.

#### Example 2 — Two-plan parallel session with interleaving

**Before** (from audit A.5 worst-case):
```
Bellows: detected plan executable-foo-2026-05-11.md
Bellows: ⏳ RUNNING — executable-foo-2026-05-11.md
Bellows: plan has 2 steps
Bellows: detected plan diagnostic-bar-2026-05-11.md
Bellows: ⏳ RUNNING — diagnostic-bar-2026-05-11.md
Bellows: plan has 1 steps
Bellows: ▶ started executable-foo-2026-05-11.md
Bellows: ▶ started diagnostic-bar-2026-05-11.md
Bellows: heartbeat — 14:32:07
Bellows: runner — 60s elapsed, last output 12s ago
Bellows: runner — 65s elapsed, last output 3s ago
Bellows: heartbeat — 14:33:07
Bellows: gates for diagnostic-bar-2026-05-11.md step 1: passed=True, is_qa=False, failures=0
Bellows: ⏸️  PAUSED — diagnostic-bar-2026-05-11.md step 1 — waiting for CEO verdict
Bellows: runner — 120s elapsed, last output 45s ago
Bellows: heartbeat — 14:34:07
Bellows: gates for executable-foo-2026-05-11.md step 1: passed=True, is_qa=False, failures=0
Bellows: ⏸️  PAUSED — executable-foo-2026-05-11.md step 1 — waiting for CEO verdict
Bellows: ⏸️  2 plan(s) awaiting verdict
Bellows: 🏁 Queue empty — all plans complete
```

**After:**
```
14:31:00 [EVENT] [executable-foo] ⏳ detected and claimed (2 steps)
14:31:01 [EVENT] [diagnostic-bar] ⏳ detected and claimed (1 step)
14:31:02 [EVENT] [executable-foo] ▶ started
14:31:04 [EVENT] [diagnostic-bar] ▶ started
14:32:04 [INFO] [executable-foo] runner: 60s elapsed, last output 12s ago (step 1)
14:32:09 [INFO] [diagnostic-bar] runner: 65s elapsed, last output 3s ago (step 1)
14:33:15 [EVENT] [diagnostic-bar] gates step 1: passed=True, failures=0
14:33:15 [PAUSE] [diagnostic-bar] ⏸️ step 1 — waiting for CEO verdict
14:33:24 [INFO] [executable-foo] runner: 120s elapsed, last output 45s ago (step 1)
14:34:30 [EVENT] [executable-foo] gates step 1: passed=True, failures=0
14:34:30 [PAUSE] [executable-foo] ⏸️ step 1 — waiting for CEO verdict
14:34:30 [EVENT] 🏁 queue empty — 2 plan(s) awaiting verdict
```

Lines: 18 → 12. Main-loop heartbeats eliminated during active execution. Each runner heartbeat identifies its plan. The CEO can mentally filter to one plan by scanning for `[diagnostic-bar]` or `[executable-foo]`.

#### Example 3 — Failure case: runner inactivity timeout + gate failure + verdict request

**Before** (reconstructed from audit call sites):
```
Bellows: detected plan executable-big-2026-05-11.md
Bellows: ⏳ RUNNING — executable-big-2026-05-11.md
Bellows: plan has 3 steps
Bellows: ▶ started executable-big-2026-05-11.md
Bellows: heartbeat — 15:00:07
Bellows: runner — 60s elapsed, last output 60s ago
Bellows: heartbeat — 15:01:07
Bellows: runner — 120s elapsed, last output 120s ago
Bellows: heartbeat — 15:02:07
Bellows: runner — 180s elapsed, last output 180s ago
Bellows: heartbeat — 15:03:07
Bellows: runner — 240s elapsed, last output 240s ago
Bellows: heartbeat — 15:04:07
Bellows: runner — 300s elapsed, last output 300s ago
Bellows: runner — inactivity timeout (300s with no output), killing process
[runner] stderr from claude -p: Error: process killed due to inactivity
Bellows: gates for executable-big-2026-05-11.md step 1: passed=False, is_qa=False, failures=2
Bellows: ⏸️  PAUSED — executable-big-2026-05-11.md step 1 — waiting for CEO verdict
```

**After:**
```
15:00:00 [EVENT] [executable-big] ⏳ detected and claimed (3 steps)
15:00:02 [EVENT] [executable-big] ▶ started
15:01:02 [INFO] [executable-big] runner: 60s elapsed, last output 60s ago (step 1)
15:02:02 [INFO] [executable-big] runner: 120s elapsed, last output 120s ago (step 1)
15:03:02 [INFO] [executable-big] runner: 180s elapsed, last output 180s ago (step 1)
15:04:02 [INFO] [executable-big] runner: 240s elapsed, last output 240s ago (step 1)
15:05:02 [ERROR] [executable-big] runner: inactivity timeout (300s with no output), killing process (step 1)
15:05:02 [WARN] [executable-big] runner: stderr from claude -p: Error: process killed due to inactivity
15:05:03 [EVENT] [executable-big] gates step 1: passed=False, failures=2
15:05:03 [PAUSE] [executable-big] ⏸️ step 1 — waiting for CEO verdict
```

Lines: 16 → 10. Main-loop heartbeats suppressed during active execution. Inactivity timeout is immediately visible as `[ERROR]`. Runner stderr uses `[WARN]` with plan identity instead of orphan `[runner]` prefix.

### 1.8 — LOC Impact Estimate

| Change | Files affected | Estimated LOC |
|--------|---------------|---------------|
| Add `_log()` helper with timestamp + level + optional slug | New function in `bellows.py` | +25 |
| Replace 64 `print()` calls in `bellows.py` with `_log()` | `bellows.py` | ~64 lines changed |
| Replace 6 `print()` calls in `runner.py` with `_log()` + slug | `runner.py` | ~6 lines changed |
| Replace 1 `print()` in `notifier.py` with `_log()` | `notifier.py` | ~1 line changed |
| Add heartbeat suppression logic | `bellows.py` | +10 |
| Change heartbeat cadence + state summary | `bellows.py` | ~5 lines changed |
| Pass slug/step to `runner.py` | `runner.py`, `bellows.py` | ~10 lines changed |

**Total: ~120 LOC touched** (new `_log()` helper + 71 call-site updates + heartbeat changes).

---

## Section 2 — Notification Coalescing and Dead-Code Cleanup

### 2.1 — Coalescing Policy

The audit found each event fires independently — a 5-plan auto-close session produces 6 pushes in rapid succession (C.11 item 7).

**Alternative A — Urgency-gated with quiet-window digest**

Policy:
- **Immediate push:** `verdict-needed` and `failure` events push immediately — these require CEO action.
- **Deferred digest:** `plan-complete`, `plan-halted`, `plan-skipped`, and `queue-empty` events enter a 30-second coalescing window. If no new deferred event arrives within 30s, a single digest push fires summarizing all buffered events.

Example digest: `"3 plans complete (executable-foo, diagnostic-bar, executable-baz). Queue empty."`

If a `verdict-needed` fires during the coalescing window, it pushes immediately (urgent), and the deferred buffer continues accumulating.

| Session shape | Current pushes | Proposed pushes |
|---------------|---------------|-----------------|
| 1 plan, auto-close | 2 (complete + queue-empty) | 1 (digest: complete + queue-empty) |
| 3 plans, all auto-close | 4 (3 complete + queue-empty) | 1 (digest: 3 complete + queue-empty) |
| 3 plans, all pause for verdict | 4 (3 verdict-needed + queue-empty) | 3–4 (3 immediate verdict-needed + possibly 1 digest for queue-empty) |
| 5 plans, 3 auto-close + 2 pause | 6 (3 complete + 2 verdict + queue-empty) | 3–4 (2 immediate verdict + 1 digest for 3 complete + queue-empty) |
| 10 plans, all auto-close | 11 (10 complete + queue-empty) | 1 (digest: 10 complete + queue-empty) |

Implementation: Add a `_notification_buffer` list and a `_coalesce_timer` thread in `notifier.py`. When a deferred event arrives, append to buffer and reset the 30s timer. When the timer fires, format and push the digest.

Complexity: Medium — requires a timer thread and buffer, but logic is straightforward.

**Alternative B — Per-session digest only**

Policy: Suppress all pushes until the session queue is empty. Then send a single digest summarizing everything that happened.

| Session shape | Current pushes | Proposed pushes |
|---------------|---------------|-----------------|
| 1 plan, auto-close | 2 | 1 |
| 3 plans, all auto-close | 4 | 1 |
| 3 plans, all pause for verdict | 4 | 1 |
| 10 plans, all auto-close | 11 | 1 |

Pros: Maximum push reduction. Simplest to implement (accumulate, push once at queue-empty).

Cons: **Verdict-needed events are delayed until the session ends** — the CEO won't know a plan needs attention until all other plans finish. This defeats the purpose of verdict notifications, which are time-sensitive. For a session with 1 fast auto-close plan and 1 long-running plan, the verdict notification for the fast plan is delayed by the duration of the slow plan.

**Recommendation:** Alternative A. The urgency gate preserves the CEO's ability to respond to verdict requests in real time while eliminating the notification storm from completions. Alternative B's latency on urgent events is unacceptable.

### 2.2 — Priority and Sound Mapping

The audit found no Pushover priority or sound is set on any notification (all use Pushover defaults).

**Proposal:**

| Event | Pushover Priority | Sound | Rationale |
|-------|------------------|-------|-----------|
| `verdict-needed` | 1 (high) | `pushover` (default) | Requires CEO action. High priority bypasses quiet hours on Pushover. |
| `failure` | 1 (high) | `falling` | Unusual event — distinct sound helps CEO notice without reading the notification. |
| Deferred digest (completions + queue-empty) | 0 (normal) | `none` (silent) | Informational. CEO checks at their convenience. |
| `plan-skipped` | -1 (low) | `none` (silent) | No action needed. Low priority suppresses lock-screen display on iOS. |

No event uses priority 2 (emergency/require-acknowledgment) — that's too aggressive for a solo-operator tool. No event uses priority -2 (lowest/no notification) — if the CEO wants to suppress an event entirely, they use the per-event config toggle (see 2.3).

### 2.3 — Configurability

**Proposal: Add `notifications` section to config.json**

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

Semantics:
- `enabled: false` disables all Pushover pushes (replaces the current "leave keys empty" workaround).
- Each event in `events` can be toggled independently. Disabled events are silently dropped.
- `coalesce_window_seconds` controls the digest timer. Set to 0 to disable coalescing (revert to one-push-per-event).

`config.example.json` would include this block with all events enabled and `coalesce_window_seconds: 30` as defaults. This is additive — no existing config fields change.

### 2.4 — Dead-Code Cleanup

The audit found `notify_escalation()` and `notify_complete()` are defined but never called (C.11 item 8). Meanwhile, 5 call sites use `notifier.push()` directly with ad-hoc title/message formats.

**Proposal: Delete dead functions, migrate direct `push()` calls to named functions**

1. **Delete** `notify_escalation()` and `notify_complete()` — they are dead code with no callers.

2. **Create named functions** for each distinct notification event:
   - `notify_verdict_request(plan_name, step, gate_failures)` — already exists, keep it
   - `notify_failure(plan_name, step, error)` — already exists, keep it
   - `notify_plan_complete(plan_name, total_cost)` — replaces 2 direct `push()` calls (`bellows.py:534` and `bellows.py:1067`)
   - `notify_plan_halted(plan_name)` — replaces 1 direct `push()` call (`bellows.py:1089`)
   - `notify_plan_skipped(plan_name)` — replaces 1 direct `push()` call (`bellows.py:294`)
   - `notify_queue_empty()` — replaces 1 direct `push()` call (`bellows.py:929`)

3. Each named function internally checks `config.notifications.events.<event_name>` before calling `push()`. Each function sets the appropriate Pushover priority and sound per the mapping in 2.2. Each function routes through the coalescing buffer or pushes immediately per the urgency classification in 2.1.

4. `push()` remains as the low-level transport but is no longer called directly from `bellows.py`. All notification intent flows through named functions.

Result: 7 named functions (2 existing + 5 new), 0 direct `push()` calls in `bellows.py`, 0 dead-code functions.

### 2.5 — Worked Examples (Push-Count Comparisons)

**Session shape 1: 1 plan, auto-close**

Before: 2 pushes (`Plan Complete` + `Queue Empty`)
After: 1 push (digest: `"executable-foo complete ($0.0423). Queue empty."`)

**Session shape 2: 3 plans, all auto-close**

Before: 4 pushes (3× `Plan Complete` + `Queue Empty`)
After: 1 push (digest: `"3 plans complete: executable-foo ($0.0423), diagnostic-bar ($0.0112), executable-baz ($0.0301). Queue empty."`)

**Session shape 3: 5 plans, 3 auto-close + 2 pause for verdict**

Before: 6 pushes (3× `Plan Complete` + 2× `Verdict Needed` + `Queue Empty`)
After: 3 pushes:
- Push 1 (immediate): `"Verdict Needed — diagnostic-bar step 1. Gate failures: rule_20_self_check."`
- Push 2 (immediate): `"Verdict Needed — executable-baz step 2. QA checkpoint (all gates passed)."`
- Push 3 (digest, 30s after last completion): `"3 plans complete: executable-foo, executable-qux, diagnostic-quux. 2 plans awaiting verdict."`

### 2.6 — LOC Impact Estimate

| Change | Files affected | Estimated LOC |
|--------|---------------|---------------|
| Delete `notify_escalation()`, `notify_complete()` | `notifier.py` | -20 |
| Add 5 new named notification functions | `notifier.py` | +60 |
| Add coalescing buffer + timer logic | `notifier.py` | +45 |
| Add config loading for `notifications` section | `bellows.py` or config loader | +10 |
| Migrate 5 direct `push()` calls to named functions | `bellows.py` | ~10 lines changed |
| Add priority/sound params to `push()` | `notifier.py` | ~5 lines changed |
| Update `config.example.json` | `config.example.json` | +10 |

**Total: ~140 LOC touched** (net +100 after dead-code deletion).

---

## Section 3 — Terminal Output Capture and Retention

### 3.1 — Capture Mechanism

The audit found Bellows does not capture its own stdout to any file (C.11 item 6). Terminal history is lost on restart.

**Alternative A — Python `logging` with `RotatingFileHandler` (recommended)**

Route all terminal output through Python's `logging` module. Configure two handlers:
1. `StreamHandler` → stdout (what the CEO sees in terminal, identical to today)
2. `RotatingFileHandler` → session log file on disk

The `_log()` helper from Section 1 becomes a thin wrapper around `logging.getLogger("bellows")`. The formatted string (timestamp + bracket + slug + message) is identical on both handlers — what's on screen is what's on disk.

Pros:
- Survives daemon restart (each restart creates a new log file or appends to the day's file).
- Multi-session retention — old files are rotated, not overwritten.
- Searchable via grep.
- No external process dependency (unlike tee).
- No new third-party dependency — `logging` is stdlib.
- Thread-safe — important for concurrent plan threads.

Cons:
- Slightly more implementation work than external tee.
- Must ensure all output (including runner subprocess output piped to terminal) goes through the logger.

**Alternative B — External tee invocation**

Start Bellows via `python bellows.py 2>&1 | tee -a logs/bellows-terminal.log`.

Pros: Zero code changes to Bellows itself.

Cons:
- Requires the CEO to remember the tee wrapper (or a shell alias/script).
- No rotation — tee appends indefinitely unless combined with `logrotate` or a cron job.
- If the CEO starts Bellows without tee, output is lost silently — the failure mode is invisible.
- Tee buffers output — lines may not appear in the file immediately (especially with Python's default stdout buffering).
- Does not integrate with the new `_log()` helper or severity levels.

**Recommendation:** Alternative A. It integrates naturally with the Section 1 `_log()` helper, is self-contained, and doesn't rely on the CEO remembering to pipe through tee.

### 3.2 — File Location and Naming

**Proposal: `logs/terminal/` subdirectory, per-day files**

Path: `logs/terminal/bellows-YYYY-MM-DD.log`

Example: `logs/terminal/bellows-2026-05-11.log`

Rationale for per-day over per-session:
- Per-session creates many files on days with restarts (debugging, config changes). Per-day keeps one file per day regardless of restarts.
- On restart, the `RotatingFileHandler` appends to the existing day file. A restart marker line is emitted (see 3.4).
- Per-day matches the CEO's mental model: "what happened today?" → open today's file.

Rationale for `logs/terminal/` subdirectory:
- Separates terminal capture from the existing `logs/*.json` step-output files.
- No filename collision risk — step-output files use `YYYYMMDD-HHMMSS-step.json` in the `logs/` root.
- The `logs/planner-consultation.jsonl` file also stays in `logs/` root, avoiding confusion.

### 3.3 — Rotation and Retention

The audit noted no rotation exists for either the existing `logs/*.json` files or the proposed terminal logs.

**Proposal:**

| File type | Rotation trigger | Keep | After retention |
|-----------|-----------------|------|-----------------|
| Terminal logs (`logs/terminal/bellows-*.log`) | Daily (inherent from naming) | 14 days | Delete |
| Step-output JSON (`logs/*.json`) | None (per-step files) | 30 days | Delete |
| Planner consultation (`logs/planner-consultation.jsonl`) | 10 MB | 3 old files | Delete oldest |

Implementation: A `_rotate_logs()` function called once at startup. It walks `logs/terminal/` and deletes files older than 14 days. It walks `logs/` root and deletes `.json` files older than 30 days. It checks `planner-consultation.jsonl` size and rotates if >10 MB.

This is a simple age-based cleanup, not a real-time rotating handler. It runs once at startup, which is sufficient given Bellows restarts at least daily during active development. No external dependency (no `logrotate` config).

**Open question for CEO:** Are 14 days of terminal logs and 30 days of step JSON sufficient? The CEO can adjust these values in config if configurability is added, but the defaults should cover the common "what happened last week?" use case.

### 3.4 — Visibility from Terminal Output

**Proposal: Emit a session-start line stating the log path**

Exact line (emitted immediately after the startup banner):

```
14:00:00 [INFO] session log: logs/terminal/bellows-2026-05-11.log
```

On restart (appending to existing day file), also emit:

```
14:30:00 [INFO] ── session restart ──────────────────────────────
14:30:00 [INFO] session log: logs/terminal/bellows-2026-05-11.log
```

Rationale: The CEO should know where to find today's log without having to remember the path convention. The restart separator helps distinguish sessions within a single day file.

### 3.5 — Worked Example: Daily `logs/` Directory Listing

After a typical day with 2 sessions (morning start, afternoon restart), 4 plans executed (2 morning, 2 afternoon):

```
logs/
├── terminal/
│   ├── bellows-2026-05-09.log        (2 days ago — will be deleted at day 15)
│   ├── bellows-2026-05-10.log        (yesterday)
│   └── bellows-2026-05-11.log        (today — 2 sessions appended)
├── 20260511-140023-step1.json        (executable-foo step 1 output)
├── 20260511-140245-step2.json        (executable-foo step 2 output)
├── 20260511-143012-step1.json        (diagnostic-bar step 1 output)
├── 20260511-160500-step1.json        (executable-baz step 1 output)
├── planner-consultation.jsonl        (Planner API call log)
└── ... (older .json files from previous days)
```

The `terminal/` subdirectory is clearly separated from step-output JSON files. Day files are human-readable text; step files are machine-readable JSON. No naming collision.

### 3.6 — LOC Impact Estimate

| Change | Files affected | Estimated LOC |
|--------|---------------|---------------|
| Configure `logging` with dual handlers | `bellows.py` (startup) | +30 |
| Create `logs/terminal/` directory at startup | `bellows.py` | +3 |
| `_rotate_logs()` cleanup function | `bellows.py` | +25 |
| Session-start and restart log lines | `bellows.py` | +5 |

**Total: ~63 LOC** (all new, no existing code modified beyond what Section 1 already changes).

---

## Section 4 — Implementation Roadmap

### 4.1 — Sequencing

The three surfaces should ship as **two executable plans**, not three:

1. **Plan 1: Terminal output + capture** (Sections 1 + 3) — Ship together because the `_log()` helper introduced in Section 1 is the same function that routes to the `RotatingFileHandler` in Section 3. Implementing terminal format without capture means building `_log()` twice. ~183 LOC.

2. **Plan 2: Notification coalescing** (Section 2) — Independent of terminal output. Can ship before or after Plan 1, but shipping after is preferred because the notification message text can reference the new terminal log path ("see logs/terminal/bellows-2026-05-11.log for details"). ~140 LOC.

**Total LOC: ~323** across both plans.

### 4.2 — CEO Clarification Needed

The following design choices have real tradeoffs where the CEO should pick before implementation:

| # | Decision | Options | Default if no response |
|---|----------|---------|----------------------|
| 1 | Plan grouping style | A (slug tag only) vs. B (slug tag + separator lines) | A |
| 2 | Heartbeat policy | Combined (300s state-bearing + suppression during activity) vs. simple (just increase to 300s) | Combined |
| 3 | Coalescing policy | A (urgency-gated with 30s digest) vs. B (per-session digest) | A |
| 4 | Terminal log retention | 14 days (proposed) vs. CEO-specified | 14 days |
| 5 | Step JSON retention | 30 days (proposed) vs. CEO-specified | 30 days |

### 4.3 — Non-Controversial (Ready for Implementation)

These decisions have narrow design space and are ready for executable authoring without CEO input:

- Severity taxonomy (5 levels — the design space is effectively standard)
- Timestamp policy (absolute `HH:MM:SS` on every line)
- Prefix unification (drop `Bellows:` prefix, use bracket+slug)
- Runner heartbeat plan identity (add slug + step number)
- Dead-code cleanup (delete `notify_escalation()` and `notify_complete()`)
- Named notification functions (replace direct `push()` calls)
- Capture mechanism (Python `logging` with `RotatingFileHandler`)
- File location (`logs/terminal/bellows-YYYY-MM-DD.log`)
- Priority/sound mapping (verdict=high, failure=high+falling, digest=normal+silent)
- Notification config schema (additive `notifications` block in config.json)

### 4.4 — Cross-Surface Dependencies

| Dependency | Impact |
|------------|--------|
| Section 1 `_log()` → Section 3 capture | The `_log()` helper IS the capture mechanism. Must implement together. |
| Section 1 severity brackets → Section 3 file format | Terminal log files contain the bracketed format — enabling `grep '\[ERROR\]' logs/terminal/bellows-2026-05-11.log`. No additional work needed; they share the same output stream. |
| Section 1 format → Section 2 notification messages | Notification message text is independent of terminal format. However, the digest notification could include a "see logs/terminal/..." footer if capture is already implemented. Minor — can be added in either order. |
| Section 2 config schema → Section 1/3 | No dependency. The `notifications` config block is separate from any terminal output config. |

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Produced a comprehensive design document covering three surfaces: terminal output redesign (severity taxonomy, timestamps, plan grouping, heartbeat suppression, prefix unification with 3 worked before/after examples), notification coalescing (urgency-gated digest policy, priority/sound mapping, config schema, dead-code cleanup with push-count comparisons), and terminal output capture (Python logging with RotatingFileHandler, per-day files, rotation/retention policy). Includes an implementation roadmap with sequencing, LOC estimates (~323 total), 5 CEO decision points, and cross-surface dependency analysis.

### Files Deposited
- `knowledge/research/terminal-notification-capture-design-2026-05-11.md` — design proposals across 3 surfaces with alternatives, worked examples, LOC estimates, and implementation roadmap

### Files Created or Modified (Code)
- None (design document only — no code changes per plan constraints)

### Decisions Made
- Severity taxonomy: 5 levels (EVENT, INFO, WARN, ERROR, PAUSE) — standard taxonomy, narrow design space
- Timestamp format: absolute `HH:MM:SS` — relative-to-session rejected due to mental arithmetic burden
- Prefix unification: drop all legacy prefixes in favor of bracket+slug format
- Capture mechanism: Python `logging` stdlib over external tee — self-contained, thread-safe, no CEO workflow change
- File naming: per-day (`bellows-YYYY-MM-DD.log`) over per-session — fewer files, matches mental model
- Dead-code cleanup: delete over preserve-as-stubs — dead code with no migration path is pure liability
- Implementation grouping: 2 plans (terminal+capture together, notifications separate) — `_log()` helper is shared

### Flags for CEO
- 5 design choices require CEO selection before implementation begins (see Section 4.2): plan grouping style, heartbeat policy, coalescing policy, terminal log retention period, step JSON retention period
- Each has a recommended default; CEO can accept defaults or specify alternatives

### Flags for Next Step
- None — this diagnostic is complete. Implementation plans should be authored after CEO reviews and marks up this design document.
