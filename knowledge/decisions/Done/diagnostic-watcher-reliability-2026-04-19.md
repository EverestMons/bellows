# Bellows — Diagnostic: Filesystem Watcher Reliability
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted (read-only investigation, no code changes) | **Execution:** Step 1 (Bellows Developer)

**Purpose:** Characterize Bellows's current filesystem watcher behavior to explain why Planner-originated filename changes (e.g., renaming `verdict-pending-*` → `executable-*` to signal resume) are not reliably picked up without a daemon restart. The 2026-04-19 verdict schema refresh confirmed `bellows.py` imports `watchdog.observers.Observer` — so a true filesystem watcher already exists. The question is NOT "add a watcher" but "why is the existing watcher missing events?"

**Blocks:** BACKLOG item #4 executable (fix for filesystem watcher reliability). Also blocks BACKLOG #6 (Planner↔Bellows integration protocol in PLANNER_TEMPLATE).

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1. This is a single-step diagnostic — no Step 2. After completing Step 1, the agent STOPS. The Planner reads the deposited findings file in the Project conversation, performs Rule 22 verification, and handles housekeeping directly.

**Bootstrap:**
```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-watcher-reliability-2026-04-19.md. Execute Step 1. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-watcher-reliability-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-watcher-reliability-2026-04-19.md")`.
>
> You are the Bellows Developer. **Reads (mandatory):** (1) `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DEVELOPER.md` — your specialist file, (2) `/Users/marklehn/Desktop/GitHub/bellows/bellows.py` — full file, (3) `/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md` — the "filesystem watcher reliability" open item (search for "filesystem watcher reliability"). Skip domain glossary — no glossary exists for Bellows and this is pure code-tracing. This is a **read-only investigation**. Do NOT modify any source file. Do NOT write the executable — that is the Planner's job after reviewing your findings.
>
> **Answer five questions. Each answer MUST include a verbatim line-numbered code snippet from `bellows.py`, not a paraphrase.**
>
> **Q1 — Watchdog event subscriptions.** Identify the `FileSystemEventHandler` subclass(es) in `bellows.py`. For each, list every handler method the class overrides (`on_created`, `on_moved`, `on_modified`, `on_deleted`, `on_any_event`) with the verbatim method signature and body. For each overridden method: which watchdog event attributes does it read (`event.src_path`, `event.dest_path`, `event.is_directory`, `event.event_type`)? Include the `Observer.schedule()` call showing which paths are watched and whether `recursive=True`.
>
> **Q2 — Rename detection.** When the Planner renames `verdict-pending-foo.md` → `executable-foo.md` in `<project>/knowledge/decisions/`, which watchdog event fires on macOS? Read the watchdog source behavior if documented in the existing code comments, OR reason from the watchdog library's known behavior: on macOS (FSEvents), a single-directory rename typically fires `on_moved` with `event.src_path` = old name and `event.dest_path` = new name — NOT `on_created`. Verify by reading `bellows.py` — does the handler subscribe to `on_moved`? If not, that is the bug. Include the verbatim handler method(s) that would (or would not) be invoked for this rename sequence.
>
> **Q3 — Rescan loop.** Find the `_rescan` function (or equivalent directory-scanning function) in `bellows.py`. Include the full function body as a verbatim snippet. What triggers it — a timer thread? A watchdog event? The main loop? What paths does it scan, and what does it do with files it finds? Is there a mechanism for the rescan to re-dispatch a plan that transitioned from `verdict-pending-*` → `executable-*` while Bellows wasn't looking? Note: if the rescan maintains a `_seen` set and skips already-seen paths, a rename from one prefix to another changes the filename, which should present as a NEW path to `_seen` — unless `_seen` is populated by full absolute path and the file moved to a new absolute path. Trace this logic precisely.
>
> **Q4 — Heartbeat mechanism.** Find the heartbeat print statement (mentioned in BACKLOG notifier-timeout item as "Heartbeat print added to main loop (every 60s) as a canary"). Include the verbatim code. Is the heartbeat a pure print, OR does it also trigger a rescan, inbox poll, or any other filesystem operation? If pure print: the heartbeat is a liveness indicator, not a scan trigger, and the BACKLOG guess "existing heartbeat was thought to function as a file-scanner refresh" is wrong.
>
> **Q5 — Startup scan.** Find the startup code path that scans `decisions/` directories at daemon boot. Include the verbatim code. What determines whether a file is picked up on startup vs. requires a later event? If Bellows is restarted after a Planner rename (current workaround per BACKLOG), what code path handles the renamed file — the startup scan, the watchdog event handler that fires once the Observer is scheduled, or something else? If the answer is "startup scan," that confirms the workaround: restart is needed because the rename event was missed AND the in-flight watchdog session never saw the file.
>
> **Deposit format.** Write your findings to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/watcher-reliability-2026-04-19.md` using the canonical Python file write pattern: define the full content as a triple-quoted string variable, then `with open("/absolute/path", "w") as f: f.write(content)`. Do NOT use heredoc. Structure the findings as: Q1 heading → snippet → prose answer; Q2 heading → snippet → prose answer; etc. At the end, include a `## Root Cause Summary` section (one paragraph) and a `## Fix Options` section ranking the viable fix approaches based on what you found (not the BACKLOG's speculative options — YOUR ranked options based on the actual code). End with an Output Receipt. Then commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/watcher-reliability-2026-04-19.md && git commit -m "research: filesystem watcher reliability diagnostic findings"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/watcher-reliability-2026-04-19.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` (append only)
>
> **STOP. Do NOT write the executable. Do NOT proceed to move the plan to Done. The Planner handles housekeeping after reading your findings.**
