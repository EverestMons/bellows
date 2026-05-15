# Terminal Output and Notification Surface Audit

**Date:** 2026-05-11
**Author:** Bellows Systems Analyst
**Type:** Diagnostic — read-only inventory
**Source plan:** `knowledge/decisions/in-progress-diagnostic-terminal-and-notification-surface-audit-2026-05-11.md`

---

## Section A — Terminal Output Inventory

### A.1 — Every print/log call site

Bellows uses **no logging framework** — all terminal output is via bare `print()` calls to stdout. One call site writes to stderr. No `logger.*`, `logging.*`, or `sys.stdout.write()` usage exists. Flask's built-in logger produces its own output in `server.py` but is not explicitly configured.

The following enumerates every call site, grouped by event category.

#### Startup banner (8 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:1173` | `print("=" * 50)` | Once at daemon start |
| `bellows.py:1174` | `print("  🔥 Bellows is running")` | Once at daemon start |
| `bellows.py:1175` | `print(f"  Source: bellows.py @ {_source_sha()}")` | Once at daemon start |
| `bellows.py:1176` | `print(f"  Watching {len(...)} projects")` | Once at daemon start |
| `bellows.py:1177` | `print(f"  Rescan interval: 30s")` | Once at daemon start |
| `bellows.py:1178` | `print(f"  Callback: http://{...}:{...}/respond")` | Once at daemon start |
| `bellows.py:1180` | `print(f"  Module: {mod_name} @ {fp}")` | Once per module at daemon start (loop over 5 modules) |
| `bellows.py:1181` | `print("=" * 50)` | Once at daemon start — closing separator |

#### Startup scan/cleanup (3 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:1187` | `print(f"Bellows: startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed")` | Once at startup if orphaned verdict requests exist |
| `bellows.py:1189` | `print(f"  - {rm_name}")` | Once per orphaned file removed |
| `bellows.py:1197` | `print(f"Bellows: startup scan found {fname}")` | Once per pre-existing runnable plan found at startup |

#### DB migration (1 call site)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:79` | `print(f"Bellows: migrated DB — added column {col}")` | Once per missing column during `migrate_db()` at startup |

#### Module fingerprint (startup and periodic, 2 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:1180` | `print(f"  Module: {mod_name} @ {fp}")` | At startup (in banner) |
| `bellows.py:1213` | `print(f"  Module: {mod_name} @ {fp}")` | Every 10th heartbeat (600s cadence), per module |

#### Heartbeat (1 call site)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:1210` | `print(f"Bellows: heartbeat — {datetime.now().strftime('%H:%M:%S')}")` | Every 60 seconds of idle time |

#### Plan detection/dispatch (6 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:840` | `print(f"Bellows: ⚠️  skipped {filename} — prefix not in dispatch whitelist")` | When a `.md` file doesn't match runnable-plan pattern |
| `bellows.py:860` | `print(f"Bellows: parallel group {group} — {len(all_paths)} plans")` | When a parallel group is dispatched from watchdog event |
| `bellows.py:864` | `print(f"Bellows: detected plan {filename}")` | When a single plan is detected and claimed |
| `bellows.py:935` | `print(f"Bellows: ▶ started {os.path.basename(path)}")` | When a plan thread is launched (after 2s stagger) |
| `bellows.py:942` | `print(f"Bellows: ▶ started {len(threads)} parallel threads")` | When parallel group threads are launched |
| `bellows.py:957` | `print(f"Bellows: parallel group {group} — {len(all_paths)} plans (deferred dispatch)")` | When a parallel group is dispatched from rescan settle-window |

#### Plan claim/metadata (8 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:235` | `print(f"Bellows: ⏳ RUNNING — {plan_name}")` | Immediately when `run_plan()` begins |
| `bellows.py:278` | `print(f"Bellows: ⚠️  sparse header ({prev_len} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)")` | When defensive header default is applied |
| `bellows.py:290` | `print(f"Bellows: using cached plan content ({total_steps} steps)")` | When shadow cache is used for plan content |
| `bellows.py:293` | `print(f"Bellows: ⚠️  SKIPPED — {plan_name} has no ## STEP headers — not a standard executable")` | When plan has 0 steps and is not a diagnostic |
| `bellows.py:298` | `print(f"Bellows: plan has {total_steps} steps")` | After step-count extraction |
| `bellows.py:302` | `print(f"Bellows: ⚠️  {plan_name} has {total_steps} steps but parsed header is missing: {sorted(missing_keys)}...")` | When multi-step plan header is missing expected keys |
| `bellows.py:304` | `print(f"Bellows: using model override: {model}")` | When plan header specifies a non-default model |
| `bellows.py:114` | `print(f"Bellows: ⚠️  WARNING: plan has step headers but case does not match expected '## STEP N' — count={case_insensitive_count} matched case-insensitively")` | When step headers have wrong case |

#### Gate evaluation (2 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:373` | `print(f"Bellows: gates for {plan_name} step {current_step}: passed={gate_result['passed']}, is_qa={gate_result['is_qa_step']}, failures={len(gate_result['failures'])}")` | After gates run on first/resume step |
| `bellows.py:458` | Same format as above | After gates run in the multi-step while-loop |

#### Mode A detection (6 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:353` | `print(f"Bellows: ❌ Mode A detected — agent moved {plan_name} to Done/ without authorization, recovering")` | When agent unauthorized Done/ move detected (first step) |
| `bellows.py:358` | `print(f"Bellows: ⚠ Mode A recovery failed for {plan_name}: {e}")` | When Mode A recovery fails (first step) |
| `bellows.py:361` | `print(f"Bellows: ⚠ in-progress file missing for {plan_name} — possible agent file deletion")` | When in-progress file vanishes without Done/ match (first step) |
| `bellows.py:438` | Same as :353 | Mode A detected (loop) |
| `bellows.py:443` | Same as :358 | Mode A recovery failed (loop) |
| `bellows.py:446` | Same as :361 | In-progress file missing (loop) |

#### Verdict request/pause (5 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:327` | `print(f"Bellows: ⏸️  PAUSED — {plan_name} — worktree creation failed, awaiting CEO verdict")` | After worktree creation failure |
| `bellows.py:409` | `print(f"Bellows: ⏸️  PAUSED — {plan_name} step {current_step} — waiting for CEO verdict")` | Mid-step pause in while-loop |
| `bellows.py:494` | `print(f"Bellows: ⏸️  PAUSED — {plan_name} step {current_step} — waiting for CEO verdict")` | Final-step pause |
| `bellows.py:519` | `print(f"Bellows: ⏸️  PAUSED — {plan_name} — worktree teardown failed, awaiting CEO verdict")` | Teardown failure on auto-close path |
| `bellows.py:510` | `print(f"Bellows: ❌ worktree teardown failed on auto-close for {plan_slug}: {e}")` | Teardown failure error line (precedes :519) |

#### Verdict consumption (6 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:1044` | `print(f"Bellows: using cached plan content ({total_steps_c} steps)")` | When shadow cache used during verdict resume |
| `bellows.py:1069` | `print(f"Bellows: verdict continue-to-done — {original_name}")` | When continue verdict on final step moves plan to Done |
| `bellows.py:1076` | `print(f"Bellows: verdict continue — resuming {original_name}")` | When continue verdict resumes next step |
| `bellows.py:1088` | `print(f"Bellows: verdict stop — halting {original_name}")` | When stop verdict halts plan |
| `bellows.py:1126` | `print(f"Bellows: ⚠️  stale verdict for {plan_slug} step {step_number} — plan in Done/ or halted-, moving to processed")` | When verdict has no matching active plan |
| `bellows.py:1128` | `print(f"Bellows: ⚠️  no verdict-pending plan found for {plan_slug} step {step_number} — leaving in resolved/ for retry")` | When verdict has no matching plan at all |

#### Auto-close/completion (1 call site)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:536` | `print(f"Bellows: ✅ AUTO-CLOSED — {plan_name}")` | When auto-close path completes successfully |

#### Queue drain (2 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:927` | `print(f"Bellows: ⏸️  {len(verdict_pending)} plan(s) awaiting verdict")` | When queue drains but verdict-pending plans remain |
| `bellows.py:928` | `print("Bellows: 🏁 Queue empty — all plans complete")` | When last active plan finishes (every queue drain) |

#### Verdict cleanup (1 call site)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:160` | `print(f"Bellows: cleaned {count} pending verdict(s) for {slug}")` | When pending verdict files are cleaned for a slug |

#### Error (general) (1 call site)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:540` | `print(f"Bellows: ❌ FAILED — {plan_name}: {e}")` | Unhandled exception in `run_plan()` |

#### Worktree operations (13 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `bellows.py:611` | `print(f"Bellows: ⚠ {project_name} has no project-local .git — running in-place without worktree isolation")` | When project has no .git directory |
| `bellows.py:623` | `print(f"Bellows: ⚠ worktree creation failed for {slug}, retrying in 2s: {result.stderr.strip()}")` | On first worktree creation failure before retry |
| `bellows.py:659` | `print(f"Bellows: ⚠ could not detect main branch for {slug}, falling back to 'main'")` | Main branch detection failure (subprocess result) |
| `bellows.py:661` | Same as :659 | Main branch detection failure (exception) |
| `bellows.py:680` | `print(f"Bellows: ⚠ removed stale .git/index.lock ({lock_age:.0f}s old) for {slug}")` | When stale lock file removed |
| `bellows.py:682` | `print(f"Bellows: ⚠ could not remove .git/index.lock for {slug}: {e}")` | When lock removal fails |
| `bellows.py:689` | `print(f"Bellows: ⚠ removed .git/index.lock after 3s wait for {slug}")` | Lock removed after fresh-lock wait |
| `bellows.py:691` | `print(f"Bellows: ⚠ could not remove .git/index.lock for {slug}: {e}")` | Lock removal after wait fails |
| `bellows.py:733` | `print(f"Bellows: ⚠ dirty file copy-back failed for {slug}: {e}")` | Dirty file copy-back error |
| `bellows.py:742` | `print(f"Bellows: ⚠ worktree removal failed for {slug}: {result.stderr.strip()} — next startup prune will clean it")` | `git worktree remove` failure |
| `bellows.py:744` | `print(f"Bellows: ⚠ worktree removal failed for {slug}: {e} — next startup prune will clean it")` | `git worktree remove` exception |
| `bellows.py:751` | `print(f"Bellows: ⚠ could not force-remove orphaned worktree dir {wt_path}: {e}")` | Force-remove shutil.rmtree failure |
| `bellows.py:898` | `print(f"Bellows: ⚠ worktree prune failed for {project_root}: {e}")` | Startup worktree prune failure |

#### Runner heartbeat / activity-canary (3 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `runner.py:114` | `print(f"Bellows: runner — {int(elapsed)}s elapsed, last output {int(age)}s ago", flush=True)` | Every 60s while a step subprocess is running |
| `runner.py:119` | `print(f"Bellows: runner — inactivity timeout ({timeout}s with no output), killing process", flush=True)` | When step exceeds inactivity timeout |
| `runner.py:126` | `print(f"Bellows: runner — hard wall-clock cap reached ({max_wall_clock}s), killing process", flush=True)` | When step exceeds wall-clock cap |

#### Runner debug/error (3 call sites)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `runner.py:167` | `print(f"[runner] stderr from claude -p: {result_stderr[:500]}", flush=True)` | When `claude -p` exits non-zero with stderr |
| `runner.py:190` | `print(f"[runner] stderr from claude -p: {result_stderr[:500]}", flush=True)` | When `claude -p` exits 0 but has stderr output |
| `runner.py:201` | `print(f"[runner] skipping malformed NDJSON line: {line[:200]}", flush=True)` | When a stream-JSON line fails to parse |

#### Pushover error (1 call site, stderr)

| File:Line | Format | When it fires |
|-----------|--------|---------------|
| `notifier.py:25` | `print(f"Pushover error: {e}", file=sys.stderr)` | When `requests.post()` to Pushover API raises `RequestException` |

#### Files with zero terminal output

- `gates.py` — no print/log calls
- `verdict.py` — no print/log calls
- `parser.py` — no print/log calls
- `server.py` — no explicit print calls (Flask has its own `werkzeug` logger)
- `planner.py` — no print/log calls

**Total: 71 print call sites** across `bellows.py` (64), `runner.py` (6), and `notifier.py` (1).

---

### A.2 — Heartbeat cadence and content

#### Primary heartbeat

- **Location:** `bellows.py:1209–1215` (inside `Bellows.start()` main loop)
- **Cadence:** 60 seconds (checked via `if time.time() - last_heartbeat >= 60:`)
- **Format string:** `f"Bellows: heartbeat — {datetime.now().strftime('%H:%M:%S')}"`
- **Example rendered line:** `Bellows: heartbeat — 14:32:07`
- **Timestamp:** Yes — `%H:%M:%S` format (time only, no date)
- **State information:** None. No in-flight plan count, no last-event-ago, no system status.

Code (verbatim):

```python
if time.time() - last_heartbeat >= 60:
    print(f"Bellows: heartbeat — {datetime.now().strftime('%H:%M:%S')}")
    if heartbeat_counter % MODULE_FINGERPRINT_HEARTBEAT_INTERVAL == 0:
        for mod_name, fp in sorted(_module_fingerprints().items()):
            print(f"  Module: {mod_name} @ {fp}")
    heartbeat_counter += 1
    last_heartbeat = time.time()
```

#### Module fingerprint heartbeat

- **Location:** `bellows.py:1211–1213` (inside the heartbeat block)
- **Cadence:** Every 10th heartbeat = every 600 seconds (10 minutes). Controlled by `MODULE_FINGERPRINT_HEARTBEAT_INTERVAL = 10` at `bellows.py:19`.
- **Format string:** `f"  Module: {mod_name} @ {fp}"` — one line per module (5 modules: `bellows.py`, `gates.py`, `verdict.py`, `parser.py`, `runner.py`)
- **Example rendered lines:**
  ```
    Module: bellows.py @ git:b13b52b
    Module: gates.py @ git:d742f88
    Module: parser.py @ git:7da3a06
    Module: runner.py @ git:1385d45
    Module: verdict.py @ git:06453da
  ```
- **Timestamp:** Inherits the heartbeat timestamp on the preceding line
- **State information:** Git short-SHA or mtime timestamp per module — version observability only

---

### A.3 — Activity-canary message

- **Location:** `runner.py:114`
- **Exact format string:** `f"Bellows: runner — {int(elapsed)}s elapsed, last output {int(age)}s ago"`
- **Trigger condition:** Every 60 seconds while a step subprocess (`claude -p`) is actively running — checked via `if now - last_heartbeat >= 60:` inside the process-monitoring loop (`runner.py:113`)
- **Context:** This is the **runner heartbeat**, distinct from the main-loop heartbeat. It fires only during active step execution.
- **Example rendered line:** `Bellows: runner — 120s elapsed, last output 45s ago`
- **No verbatim log example available:** Log files in `logs/` contain JSON step output, not terminal lines. Bellows does not capture its own stdout to a file (see A.6).

The BACKLOG described this as "60s elapsed, last output 60s ago" — the actual text is `"{elapsed}s elapsed, last output {age}s ago"` where both values are dynamic integers, not fixed at 60.

---

### A.4 — Plan lifecycle event sequence

No terminal-output log file exists to quote verbatim (see A.6). The `logs/` directory contains JSON output from `claude -p` subprocess calls, not the terminal output of Bellows itself. The following is the reconstructed terminal-line sequence for a **typical successful 1-step diagnostic plan** with `auto_close: false` (the default), derived from static code analysis in `bellows.py`.

Sequence (each row is one `print()` call in execution order):

| # | Event Category | Timestamp? | Severity marker? | Line |
|---|----------------|------------|-------------------|------|
| 1 | Plan detection | No | No | `Bellows: detected plan diagnostic-foo-2026-05-11.md` |
| 2 | Plan claim | No | Emoji ⏳ | `Bellows: ⏳ RUNNING — diagnostic-foo-2026-05-11.md` |
| 3 | Plan metadata | No | No | `Bellows: plan has 1 steps` |
| 4 | Plan dispatch | No | Emoji ▶ | `Bellows: ▶ started diagnostic-foo-2026-05-11.md` |
| 5* | Runner heartbeat | No | No | `Bellows: runner — 60s elapsed, last output 12s ago` |
| 6 | Gate evaluation | No | No | `Bellows: gates for diagnostic-foo-2026-05-11.md step 1: passed=True, is_qa=False, failures=0` |
| 7 | Verdict pause | No | Emoji ⏸️ | `Bellows: ⏸️  PAUSED — diagnostic-foo-2026-05-11.md step 1 — waiting for CEO verdict` |
| 8 | Queue drain | No | Emoji 🏁 | `Bellows: 🏁 Queue empty — all plans complete` |

\* Row 5 only appears if the step takes >60s. Interspersed main-loop heartbeats (`Bellows: heartbeat — HH:MM:SS`) may also appear between rows 4 and 6 if execution takes >60s.

For a plan that **auto-closes** (`auto_close: true`, gates pass):

| # | Event Category | Line |
|---|----------------|------|
| 1–5 | Same as above | Same as above |
| 6 | Gate evaluation | `Bellows: gates for ... step 1: passed=True, is_qa=False, failures=0` |
| 7 | Auto-close | `Bellows: ✅ AUTO-CLOSED — ...` |
| 8 | Queue drain | `Bellows: 🏁 Queue empty — all plans complete` |

---

### A.5 — Visual hierarchy audit

**Timestamps:** Only **two** event types carry timestamps:
- Heartbeat: `%H:%M:%S` (time only) — `bellows.py:1210`
- Runner heartbeat: elapsed/age in seconds (relative, not absolute) — `runner.py:114`

All other events (plan detection, claim, gate results, pause, error, auto-close, verdict consumption, queue drain) have **no timestamp whatsoever**.

**Severity levels:** No structured severity. No `[INFO]`, `[WARN]`, `[ERROR]` prefixes. No color output (no ANSI escape codes used anywhere). Visual differentiation relies solely on:
- Emoji prefixes: ⏳ (running), ⚠️ (warning), ❌ (error/failure), ⏸️ (paused), ✅ (auto-closed), ▶ (started), 🏁 (queue empty), 🔥 (startup)
- Prefix convention: most lines start with `Bellows:` but runner lines use `Bellows: runner —` and some use `[runner]`

**Plan event grouping:** None. No blank lines between plans. No indentation (except module-fingerprint lines which use 2-space indent). No slug header or section separator between plan runs. In a multi-plan session, plan events from different plans interleave freely with heartbeats.

**Worst-case interleaving (reconstructed):** During a session with 2 concurrent plans and idle heartbeats, the terminal would show:

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

Note: runner heartbeats from different plans are indistinguishable — they don't include the plan name or slug. The only way to correlate a runner heartbeat to a plan is temporal proximity, which breaks down with concurrent plans.

**Prefix inconsistency:** Three distinct prefix conventions coexist:
- `Bellows:` — most lines in `bellows.py`
- `Bellows: runner —` — runner heartbeats (`runner.py:114`)
- `[runner]` — runner error/debug lines (`runner.py:167, 190, 201`)
- `Pushover error:` — notifier error (`notifier.py:25`, to stderr)

---

### A.6 — Log file vs terminal output parity

**Key finding: The `logs/` directory and terminal output are entirely different data streams.**

- **`logs/*.json`** — Contains JSON output from `claude -p` subprocess calls. Each file is the raw NDJSON stream from one step execution, parsed by `runner.py:_write_log()`. These are **step results**, not terminal output.
- **Terminal output** — All `print()` calls go to stdout. **Bellows does not capture, mirror, or redirect its own stdout to any file.** There is no tee, no rotating file handler, no log-to-file mechanism.
- **`logs/planner-consultation.jsonl`** — A separate JSONL file written by `planner.py:_log_consultation()` for Planner API consultation results. Also not terminal output.

**Log rotation/retention:** None configured. No rotation config in `config.json`. No `RotatingFileHandler` or equivalent. No max-size or max-age logic. JSON log files accumulate in `logs/` indefinitely. The only implicit retention is that filenames include timestamps (`YYYYMMDD-HHMMSS-step.json`), enabling manual cleanup.

**Parity verdict:** Terminal output and log files do **not** match. They serve different purposes. A terminal session's history is lost when the process is restarted or the terminal scrollback overflows. No mechanism exists to reconstruct what the terminal showed for a historical run.

---

## Section B — Pushover Notification Inventory

### B.7 — Notification trigger inventory

`notifier.py` defines 5 functions. Four are named notification triggers; one is the underlying transport. All notifications route through `notifier.push()`.

| # | Function | File:Line | Event trigger | Call chain | Conditional gating |
|---|----------|-----------|---------------|------------|-------------------|
| 1 | `push()` | `notifier.py:9` | Generic transport — not called directly for events (see below for direct callers) | Called by all others | Requires non-empty `app_key` and `user_key` (Pushover API rejects empty tokens) |
| 2 | `notify_escalation()` | `notifier.py:29` | Escalation with callback URL | **Not called anywhere in the current codebase** — dead code (was used by the legacy response-server flow) | Same as push() |
| 3 | `notify_complete()` | `notifier.py:40` | Plan complete | **Not called anywhere in the current codebase** — dead code (superseded by direct `push()` calls) | Same as push() |
| 4 | `notify_failure()` | `notifier.py:49` | Unhandled exception in `run_plan()` | `bellows.py:541` → `notifier.notify_failure()` | Same as push() |
| 5 | `notify_verdict_request()` | `notifier.py:58` | Verdict request posted (gates failed, QA checkpoint, header pause, etc.) | `bellows.py:400–401` and `bellows.py:486–487` → `notifier.notify_verdict_request()` | Same as push() |

**Direct `notifier.push()` call sites in `bellows.py`:**

| File:Line | Event | Context |
|-----------|-------|---------|
| `bellows.py:294` | Plan skipped (0 steps) | `push("Bellows — Skipped", ...)` |
| `bellows.py:534–535` | Auto-close success | `push("Bellows — Plan Complete", ...)` |
| `bellows.py:929` | Queue empty | `push("Bellows — Queue Empty", ...)` |
| `bellows.py:1067–1068` | Continue verdict on final step → Done | `push("Bellows — Plan Complete via Verdict", ...)` |
| `bellows.py:1089–1090` | Stop verdict → halted | `push("Bellows — Plan Halted", ...)` |

**Total trigger events: 7** distinct notification events (2 named functions actually called + 5 direct `push()` calls).

### B.8 — Payload structure

#### `notify_failure()` — `notifier.py:49`

```python
title = "Bellows — Failed"
message = f"Plan: {plan_name}\nStep: {step}\nError: {error}"
```
- **Priority:** Not set (Pushover default = normal)
- **URL/URL-title:** Not set
- **Sound:** Not set (Pushover default)

#### `notify_verdict_request()` — `notifier.py:58`

```python
title = "Bellows — Verdict Needed"
message = f"Plan: {plan_name}\nStep: {step}\nGate failures: {failure_text}"
```
Where `failure_text` is either `", ".join(f["gate"] for f in gate_failures)` or `"QA checkpoint (all gates passed)"`.
- **Priority:** Not set
- **URL/URL-title:** Not set
- **Sound:** Not set

#### `notify_escalation()` — `notifier.py:29` (dead code)

```python
title = "Bellows — Escalation"
message = f"Plan: {plan_name}\nStep: {step}\nReason: {reason}"
url = callback_url
url_title = "Respond"
```
- **Priority:** Not set
- **URL/URL-title:** callback_url with title "Respond"
- **Sound:** Not set

#### `notify_complete()` — `notifier.py:40` (dead code)

```python
title = "Bellows — Complete"
message = f"Plan: {plan_name}\nTotal cost: ${total_cost:.4f}"
```
- **Priority:** Not set
- **URL/URL-title:** Not set
- **Sound:** Not set

#### Direct `push()` calls:

| Call site | Title | Message format |
|-----------|-------|----------------|
| `bellows.py:294` | `"Bellows — Skipped"` | `f"Plan {plan_name} has no STEP headers — moved to Done without executing."` |
| `bellows.py:534` | `"Bellows — Plan Complete"` | `f"Plan: {plan_name}\nAll gates passed. Auto-closed to Done. Total cost: ${total_cost:.4f}"` |
| `bellows.py:929` | `"Bellows — Queue Empty"` | `"All plans complete. Ready for Forge cycle."` |
| `bellows.py:1067` | `"Bellows — Plan Complete via Verdict"` | `f"Plan: {original_name}\nContinue verdict on final step — moved to Done."` |
| `bellows.py:1089` | `"Bellows — Plan Halted"` | `f"Plan {original_name} halted by Planner verdict."` |

All direct calls: no priority, no URL, no URL-title, no sound override.

### B.9 — Coalescing and rate limiting

**Coalescing:** None. Each event fires its own independent Pushover notification. There is no session-level batching, plan-level aggregation, or time-windowed coalescing. A 3-plan session where all plans auto-close will produce at minimum:
- 3× "Bellows — Plan Complete" notifications
- 1× "Bellows — Queue Empty" notification
= **4 pushes** in rapid succession.

A session where 3 plans all pause for verdict will produce:
- 3× "Bellows — Verdict Needed"
- 1× "Bellows — Queue Empty"
= **4 pushes**.

**Rate limiting:** None. No client-side throttle, no dedupe logic, no awareness of Pushover's own rate limits (250 messages per month on free tier, 10,000/month on paid). Each `requests.post()` fires immediately. The only implicit throttle is the 2-second stagger between thread starts (`bellows.py:934`, `bellows.py:941`), which spaces out plan execution but does not limit notification frequency.

**Error handling:** `notifier.push()` catches `RequestException` and prints to stderr (`notifier.py:25`), returning `False`. All callers ignore the return value — notification failure is silent at the application level.

### B.10 — Configuration surface

**From `config.json` (production):**

| Field | Type | Current Value | Purpose |
|-------|------|---------------|---------|
| `pushover.app_key` | string | `"abkvra22nmscanz89d61vhcxtrw1ju"` | Pushover application API token |
| `pushover.user_key` | string | `"u1bce5ht5finkriqfv38oooxq2eyj7"` | Pushover user/group key |

**From `config.example.json`:**

| Field | Type | Default | Documented? |
|-------|------|---------|-------------|
| `pushover.app_key` | string | `""` (empty) | Yes — present in example |
| `pushover.user_key` | string | `""` (empty) | Yes — present in example |

**Missing from both configs:** No fields for notification enable/disable toggle, priority override, sound selection, rate limit, quiet hours, or per-event notification control. The only way to disable notifications is to leave `app_key` and `user_key` empty (Pushover rejects the request). There is no `notifier_enabled` boolean.

Fields present in `config.example.json` but **not** related to notifications: `watched_projects`, `default_model`, `planner_model`, `callback_port`, `tailscale_ip`, `step_timeout_seconds`.

Fields present in `config.json` but absent from `config.example.json`: `step_inactivity_timeout_seconds` — this is not notification-related but indicates config.example.json drift.

---

## Section C — Summary

### C.11 — Findings rollup

The following observations characterize the current terminal and notification surfaces. Each is a fact about the current state, not a proposal.

1. **Heartbeats emit on a 60s cadence with a time-only timestamp and no state information** (no in-flight plan count, no active-step identifier), and dominate the scroll during idle periods — every 60 seconds produces a line regardless of whether anything is happening.

2. **Plan lifecycle events have no timestamp at all** — detection, claim, gate results, pause, auto-close, verdict consumption, and queue-drain lines carry no temporal marker, making post-hoc timeline reconstruction from terminal scrollback impossible.

3. **No structured severity system exists** — event importance is conveyed solely via emoji prefixes (⚠️, ❌, ⏸️, ✅, ▶, 🏁, ⏳) which are not machine-parseable and do not sort by severity. Three distinct text prefixes coexist (`Bellows:`, `Bellows: runner —`, `[runner]`), with a fourth on stderr (`Pushover error:`).

4. **Runner heartbeats do not identify which plan or step they belong to** — the format `"Bellows: runner — {elapsed}s elapsed, last output {age}s ago"` contains no plan slug or step number, making concurrent-plan monitoring ambiguous.

5. **Plan events are not visually grouped** — no separators, headers, indentation, or blank lines distinguish one plan's lifecycle from another's. In multi-plan sessions, events from different plans interleave freely with heartbeats, creating a flat, undifferentiated stream.

6. **Bellows does not capture its own terminal output to a file** — the `logs/` directory contains JSON step-execution output from `claude -p`, not terminal lines. Terminal history is ephemeral and lost on process restart or scrollback overflow. No log rotation or retention mechanism exists for either stream.

7. **Pushover notifications fire independently with no coalescing or rate limiting** — each event produces its own push. A 5-plan auto-close session generates 6 pushes (5 completions + 1 queue-empty) in rapid succession. No priority, sound, or per-event gating is configurable.

8. **Two named notification functions (`notify_escalation`, `notify_complete`) are dead code** — they are defined in `notifier.py` but never called from `bellows.py`. Their functionality has been superseded by direct `notifier.push()` calls with different title/message formats, creating API surface drift.

---

## Output Receipt

**Status:** Complete
**Deposit:** `bellows/knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md`
**Files read (not modified):** `bellows.py`, `gates.py`, `verdict.py`, `parser.py`, `runner.py`, `notifier.py`, `server.py`, `planner.py`, `config.json`, `config.example.json`, `logs/scaffold-step1.json`
**Files modified:** None (read-only audit)
**Files created:** This file only
