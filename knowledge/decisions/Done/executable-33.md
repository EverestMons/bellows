# Bellows — Live Dashboard TUI (Daemon-Owning Wrapper with Restart Key)
**Date:** 2026-06-12 | **Tier:** Medium | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA: design + screen mock) → Step 2 (DEV) → Step 3 (QA) | **pause_for_verdict:** always | **qa_steps:** 3 | **Test Scope:** full suite

## Context (Rule 27)
CEO decision 2026-06-12 (discussion, this session): Bellows gets a full-screen terminal dashboard (TUI) that REPLACES the scrolling-log workflow — `python dashboard.py` becomes the way the CEO runs Bellows. Resolved forks: (1) **dashboard owns the daemon** — it starts `bellows.py` as its child process, renders the live screen, `r` restarts the child in place (with y/n confirm), `q` quits (with confirm; quitting stops the child — wrapper semantics match today's Ctrl+C); (2) **stdlib curses with keybindings** — zero new dependencies, no mouse/textual; (3) **content** = daemon header (running/stopped, PID, code SHA, uptime) + IN-FLIGHT + AWAITING VERDICT (the `status.py` data layer, plan 32) + a LIVE EVENT FEED pane tailing the current session's lifecycle events. Auto-refresh ~2s. CEO intent: everything about the current Bellows iteration visible in one single-monitor window, no scrolling. **New files are exactly `dashboard.py` and `tests/test_dashboard.py`** (named here so scope_check can see them — plan-32 lesson). DESIGN CONSTRAINTS the SA must respect: (a) the flock guard (plan 22) — the CHILD holds `.bellows.lock`; the dashboard must never take it; restart = terminate child → kernel releases lock on death → relaunch with a short retry loop on the lock; (b) event feed sources from the dated session log file (`logs/terminal/bellows-YYYY-MM-DD.log`), NOT from piping child stdout (pipe-blocking risk; the daemon already writes the file) — child stdout goes to the log/devnull per current behavior; (c) all lifecycle.db reads remain `?mode=ro` (reuse/import the `status.py` reader, do not duplicate queries); (d) testability — rendering and data assembly must be pure functions over (state → list of lines) testable headless; the curses shell stays thin; (e) child crash detection — if the child dies on its own, the header flips to STOPPED and `r` offers relaunch. LIVE-ACCEPTANCE HONESTY: an interactive TUI cannot be fully exercised inside a dispatched agent session — QA verifies headless render tests plus a `pty`-hosted smoke (launch, one refresh, clean quit) if feasible, and the receipt names the CEO's first interactive run as the live acceptance. This plan does NOT close a FORWARD row (new CEO request, not a register item).

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst (design + screen mock)

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md`, then `status.py` (the reader you will reuse), then the daemon startup path in `bellows.py` (`__main__`, flock acquisition, log file naming) — the dashboard wraps it. Deposit a SHORT design spec covering, each in a tight section:
>
> (1) **Process model:** child spawn (exact subprocess invocation, stdout/stderr disposition consistent with Context constraint (b)), restart sequence (SIGTERM → wait → flock-release retry loop → respawn; timeouts), quit sequence, child-death detection (poll), and zombie reaping. State explicitly how a SECOND dashboard instance is prevented or behaves (the child's flock already blocks a second daemon; what blocks a second dashboard?).
> (2) **Screen layout + THE MOCK (load-bearing):** hand-render the full screen from REAL current state (read-only queries + today's real log lines) for an ~50×120 terminal: header line; IN-FLIGHT pane; AWAITING VERDICT pane (verdict-request as basename — the plan-32 full-path rider lands here); EVENT FEED pane (last ~10 session log lines, timestamp + event text, filtered to EVENT/PAUSE/ERROR/WARN classes — propose the filter); footer keybar (`r restart  q quit`). Include a second mock for child-STOPPED state and a third for the restart-confirm prompt. State the minimum-terminal-size behavior and resize handling.
> (3) **Data contract:** what is imported from `status.py` vs new (log-tail function with rotation-tolerance at midnight; uptime source), refresh cadence, and degradation (DB absent, log absent).
> (4) **Test strategy:** the pure render layer (state → lines) test list; the `pty` smoke approach and whether it is feasible in this environment (try a 5-line proof in your session and report the result — feasible or not, with evidence).
>
> Deposit the spec + mocks to `bellows/knowledge/architecture/dashboard-tui-design-2026-06-12.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Use `with open()`; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/architecture/dashboard-tui-design-2026-06-12.md`

---
---

## STEP 2 — Bellows Developer

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. The CEO continue-verdict that resumed you approved the Step 1 spec and mock — the mock is your acceptance target. **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md` and the approved spec. **Scope is exactly: `dashboard.py` (new), `tests/test_dashboard.py` (new), `CLAUDE.md` (Start section: add the dashboard as the primary way to run Bellows, keep plain `python bellows.py` documented), and — only if the spec requires a small refactor to share the reader — `status.py`.**
>
> Implement per the spec: pure render functions over a state snapshot; thin curses loop (refresh cadence per spec, `r` confirm-restart, `q` confirm-quit, resize-safe, minimum-size message); process management per the spec's model (flock-release retry on restart; child-death → STOPPED header); log-tail feed with midnight-rotation tolerance; `?mode=ro` everywhere via the shared reader. **Tests (headless):** render-layer tests for all three mock states (running, stopped, confirm-prompt) plus panes' empty/`(none)` cases, feed filtering, and degradation paths; the `pty` smoke per the spec's Step-1 feasibility finding (implement it if SA proved feasible; otherwise document the omission and the manual check). Run the FULL suite to an explicit pass/fail and READ THE TAIL. **Acceptance:** capture the render layer's actual output for the live current state next to the mock in the dev log (the interactive loop itself is CEO-acceptance per Context). Write the dev log to `bellows/knowledge/development/dashboard-tui-dev-log-2026-06-12.md`. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/development/dashboard-tui-dev-log-2026-06-12.md`

---
---

## STEP 3 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the approved spec, and the dev log. **Verify, each with executed evidence (files into `knowledge/qa/evidence/dashboard-tui-2026-06-12/`):** (1) **Full suite** — final 15 lines, zero failures, new-test count matches dev log; output to `full_suite_tail.txt`. (2) **Mock conformance (headless)** — invoke the render layer against the live current state and against fixture states for all three mock variants; structural match to the approved mocks, verdict-request shown as basename; output to `mock_conformance.txt`. (3) **Process-safety review** — grep evidence that: the dashboard never acquires `.bellows.lock`; restart path waits on lock release before respawn; child stdout disposition matches the spec (no unconsumed PIPE); output to `process_safety.txt`. (4) **Read-only + degradation** — every DB connect `mode=ro`; DB-absent and log-absent render paths graceful; output to `safety_check.txt`. (5) **pty smoke** — run it if implemented (launch → one refresh → clean quit, exit 0); if SA found it infeasible, state that with the Step-1 evidence pointer instead; output to `pty_smoke.txt`. (6) **CLAUDE.md** — Start section documents `python dashboard.py` as primary; output to `docs_check.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `dashboard-tui-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/dashboard-tui-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/dashboard-tui-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, mock_conformance.txt, process_safety.txt, safety_check.txt, pty_smoke.txt, docs_check.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table and the Rule 20 banner block to `bellows/knowledge/qa/dashboard-tui-qa-report-2026-06-12.md`. **Receipt Flags for CEO must include:** (1) live interactive acceptance is the CEO's first `python dashboard.py` run — the dispatched session cannot fully exercise the TUI; (2) the dashboard becomes the primary run mode — the CEO's current terminal workflow changes (start the dashboard instead of `python bellows.py`); (3) restart via `r` supersedes manual kill/restart for routine daemon-code activation. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/dashboard-tui-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/dashboard-tui-2026-06-12/` (six evidence files per Rule 20 self-check)
