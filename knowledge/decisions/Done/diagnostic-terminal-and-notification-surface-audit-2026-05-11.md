**project:** bellows | **type:** diagnostic | **steps:** 1 | **pause_for_verdict:** always | **auto_close:** false

# Diagnostic — Terminal output and notification surface audit

## Why this exists

BACKLOG entry `2026-04-19: terminal output redesign + notification audit` describes the current terminal format as having no visual hierarchy: heartbeats, plan lifecycle events, gate results, and error states all have equal visual weight. Heartbeats dominate the scroll at 60s cadence. Plan events do not group visually (6+ consecutive lines per plan lifecycle). Inconsistent timestamps (heartbeats have them, plan events don't). Activity-canary message "60s elapsed, last output 60s ago" reads ambiguously. The entry also flags a parallel concern about Pushover notification structure: what triggers a push, what the payload contains, whether multi-plan sessions coalesce.

The entry proposes decomposition into (a) diagnostic audit, (b) design plan, (c) implementation plan. This is item (a). The entry's defer condition ("until BACKLOG #1, #4, #5, and verdict lifecycle coupling ship") has been met — all four shipped per the Closed section.

This diagnostic characterizes the current state of terminal output and notifications. No design proposals, no fix recommendations — just an inventory of what exists, where it is in the code, and what it produces at runtime.

## Step 1 — Systems Analyst: terminal and notification surface inventory

You are the Bellows Systems Analyst. Read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` before starting; if the exact filename differs, use the closest match in `bellows/agents/`.

### Context

The audit covers two surfaces:
- **Terminal output** — anything Bellows emits to stdout/stderr during normal operation. Heartbeats, plan lifecycle events, gate results, error logs, debug logs.
- **Pushover notifications** — outbound HTTP notifications. Source code lives in `bellows/notifier.py`. Configuration lives in `bellows/config.json`.

Read-only audit. Do NOT modify any file. Do NOT run Bellows. Static analysis of the source code plus inspection of recent log files is sufficient.

### Task

Answer the following questions in order. Cite specific file paths and line numbers. Quote code verbatim where it clarifies the answer.

#### Section A — Terminal output inventory

1. **Enumerate every print/log call site.** Search `bellows.py`, `gates.py`, `verdict.py`, `parser.py`, `runner.py`, `notifier.py`, `planner.py`, and `server.py` for every call to `print()`, `logger.info()`, `logger.warning()`, `logger.error()`, `logger.debug()`, `sys.stdout.write()`, or any other terminal-output mechanism. For each call site, report: file:line, the event category it represents (heartbeat, plan claim, plan dispatch, gate evaluation, verdict request post, verdict consume, error, debug, startup banner, module fingerprint, etc.), and a one-line summary of when it fires. Group results by event category in the findings file.

2. **Heartbeat cadence and content.** Locate the heartbeat-emission code. Report: cadence (interval in seconds), exact format of the heartbeat line (with verbatim format string and an example rendered line), whether it includes a timestamp, whether it includes any state information (number of in-flight plans, last-event-ago, etc.). Locate the module-fingerprint heartbeat (10-tick interval per the 2026-05-11 daemon-version-observability close) and report its cadence and format similarly.

3. **Activity-canary message.** Locate the "60s elapsed, last output 60s ago" message (or whatever its current exact text is). Report: file:line, the exact format string, the trigger condition, and quote a verbatim example from a recent log if one can be found.

4. **Plan lifecycle event sequence.** For a typical successful 1-step plan run, enumerate every terminal line emitted from plan-claim through Done/-move, in order. For each line, report the event category from Section A.1, whether it has a timestamp, and whether it has a severity marker. Use a recent log file from `bellows/logs/` as the source — pick the most recent log where a 1-step plan ran cleanly (Rule 20 self-check PASSED, plan moved to Done/), and quote the actual lines verbatim with their line numbers in the log.

5. **Visual hierarchy audit.** From the data in A.1–A.4, characterize the current visual hierarchy. Specifically: do timestamps appear on all event types or only some (which)? Are severity levels visually distinguishable (color, prefix, bracketed level like `[INFO]`)? Are plan events grouped (e.g., blank lines between plans, indentation, or a slug header), or interleaved with heartbeats? Quote one consecutive stretch of ~20 lines from a real log that illustrates the worst-case interleaving.

6. **Log file vs terminal output parity.** Compare `bellows/logs/<latest>.log` to what would appear in the terminal during the same run. Report whether they match byte-for-byte, whether the log file adds anything the terminal lacks (or vice versa), and whether log rotation/retention is configured (search for rotation config in `config.json`, `bellows.py`, or any logging-setup code).

#### Section B — Pushover notification inventory

7. **Notification trigger inventory.** In `bellows/notifier.py`, enumerate every code path that sends a Pushover notification. For each, report: file:line, the event that triggers it (e.g., gate failure, plan halted, plan complete), the call chain that reaches it (which function in `bellows.py` calls into `notifier.py`), and any conditional gating (e.g., only fires if `notifier_enabled = true` in config).

8. **Payload structure.** For each trigger from B.7, report the exact payload structure sent to Pushover: title format, message body format, priority level, any URL or URL-title fields, any sound override. Quote the format strings verbatim.

9. **Coalescing and rate limiting.** Determine whether Bellows coalesces multiple notifications from the same session or the same plan, or whether each event fires its own push. Determine whether any rate limiting exists (client-side throttle, Pushover-side limit awareness, dedupe logic). Cite specific code or document its absence.

10. **Configuration surface.** From `bellows/config.json` (read it directly — it is in scope for this audit since the question is about what Bellows actually does, not Planner-side schema inference), report every notifier-related config field: name, type, default, and current value. Also report whether `bellows/config.example.json` documents these fields.

#### Section C — Summary

11. **Findings rollup.** In a final summary section, list the top 5–8 specific observations that a redesign would need to address. These are observations, not proposals — e.g., "heartbeats emit on a 60s cadence with no severity marker and dominate the scroll" rather than "heartbeats should be suppressed when no events are pending." Numbered list. One sentence per observation. The goal is to give the next plan (design) a concrete starting inventory.

### Out of scope

- Do NOT propose new formats, severity levels, color schemes, or notification structures.
- Do NOT propose code changes.
- Do NOT modify any file.
- Do NOT run Bellows or run tests.

### Deliverables

A findings file at `bellows/knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md` containing:
- One section per question (A.1–A.6, B.7–B.10, C.11) with the question restated, evidence cited (file:line, code quotes, log-line quotes), and a clear answer.
- A final summary table or narrative for Section C.
- An Output Receipt at the bottom per BELLOWS_SYSTEMS_ANALYST.md format.

**Deposits:**
- `bellows/knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md`
