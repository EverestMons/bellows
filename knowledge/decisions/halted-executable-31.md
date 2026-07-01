# Bellows — Single-Glance Status CLI (FORWARD Row 2: Observability Surface)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA: design + mock) → Step 2 (DEV) → Step 3 (QA) | **pause_for_verdict:** always | **qa_steps:** 3 | **Test Scope:** full suite

## Context (Rule 27)
CEO decision 2026-06-12 (discussion, this session) resolving FORWARD row 2's shape fork: the observability surface is a **CLI**, not a web route on the daemon (no new daemon attack/availability surface). CEO framing, verbatim intent: "bellows functions quite well, it's just a matter of keeping it more viewable at a single glance without having to scroll too much" — the CLI's job is the at-a-glance answer to "what is Bellows doing right now," replacing log-scrolling. The data layer already exists: `bellows/lifecycle.db` (the daemon writes `in_progress` live as of plan 22) and the Forge reader precedent (`forge/src/reporter.py::get_live_plans_status`, plan 10). Specialist rule: new Python modules in bellows require SA sign-off — Step 1 IS that consultation, and its pause puts the proposed output mock in front of the CEO before anything is built. ALL `lifecycle.db` access read-only (`?mode=ro`); the CLI must never write the DB and must work while the daemon runs (WAL concurrent read) AND while it is stopped (state from DB + filesystem only — detect daemon liveness via the `.bellows.lock` flock probe, plan 22 precedent).

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst (design + output mock)

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md`, then `forge/src/reporter.py::get_live_plans_status` (the reader precedent) and `lifecycle.py` (schema). Design the CLI and deposit a SHORT spec (this is a Small-tier design step, not a forensic diagnostic):
>
> (1) **Placement decision (SA authority):** new `bellows/status.py` module (standalone, no daemon imports) vs extension of an existing module — decide and justify in one paragraph. Invocation should be a single short command from the bellows root (document it).
> (2) **The single-glance contract:** the default output fits ONE terminal screen (~40 lines max) with zero scrolling for normal shop state. Propose the sections, e.g.: a one-line daemon header (running/stopped via flock probe, PID if derivable, code SHA, uptime); IN-FLIGHT plans (id, type, title truncated, current step n/total, step status, elapsed); AWAITING VERDICT (id, step, pause reason, verdict-request filename — the actionable line); recent completions today (id, title truncated, closed time, total cost) capped at ~5; a one-line totals footer (today's plans/cost from the steps table). Flags worth proposing: `--all` for history depth, `--watch` polling refresh ONLY if trivially cheap, otherwise omit.
> (3) **THE MOCK (the load-bearing deliverable):** render the proposed output BY HAND from the REAL lifecycle.db state at design time (read-only queries) — the CEO approves this mock at the pause; it becomes Step 2's acceptance target. Include a second mock for the daemon-stopped state.
> (4) **Data contract:** the exact read-only queries per section, the flock-probe liveness check, and degradation when the DB is absent.
>
> Deposit the spec + both mocks to `bellows/knowledge/architecture/status-cli-design-2026-06-12.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Use `with open()`; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/architecture/status-cli-design-2026-06-12.md`

---
---

## STEP 2 — Bellows Developer

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. The CEO continue-verdict that resumed you approved the Step 1 mock — it is your acceptance target. **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md` and the approved spec. **Scope is exactly: the module the spec places (e.g. `status.py`), `tests/` (one new test file matching repo naming).** Implement the CLI exactly per the spec: read-only URI everywhere, flock-probe liveness, absent-DB degradation, output format matching the mock. **Tests:** fixture lifecycle DB (existing conftest pattern) covering: in-flight + awaiting-verdict + closed rows render in the right sections; daemon-stopped header path; absent-DB graceful message; output line-count stays within the single-screen contract for a representative state. Run the FULL suite to an explicit pass/fail and READ THE TAIL. **Acceptance:** run the real CLI against the live DB and capture its actual output in the dev log next to the mock (structural match; live values may differ). Write the dev log to `bellows/knowledge/development/status-cli-dev-log-2026-06-12.md`. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/development/status-cli-dev-log-2026-06-12.md`

---
---

## STEP 3 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the approved spec, and the dev log. **Verify, each with executed evidence (files into `knowledge/qa/evidence/status-cli-2026-06-12/`):** (1) **Full suite** — final 15 lines, zero failures, new-test count matches dev log; output to `full_suite_tail.txt`. (2) **Mock conformance** — run the real CLI yourself; section-for-section structural match against the approved mock; capture both; output to `mock_conformance.txt`. (3) **Single-glance contract** — the default output's line count fits the spec's one-screen bound with the current real state; output to `glance_contract.txt`. (4) **Read-only + degradation** — grep every DB connect for `mode=ro`; run the CLI with a nonexistent DB path env/arg per spec and confirm graceful output; output to `safety_check.txt`. (5) **FORWARD reconciliation (Rule 42)** — `knowledge/FORWARD.md` row 2: Status → `closed-by-plan-<this plan's id>`, Plan-id link set; output diff to `forward_reconciliation.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `status-cli-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/status-cli-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/status-cli-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, mock_conformance.txt, glance_contract.txt, safety_check.txt, forward_reconciliation.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table and the Rule 20 banner block to `bellows/knowledge/qa/status-cli-qa-report-2026-06-12.md`. Also add the CLI invocation one-liner to `CLAUDE.md` (worktree) under a short "Status" heading. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/status-cli-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/status-cli-2026-06-12/` (five evidence files per Rule 20 self-check)
