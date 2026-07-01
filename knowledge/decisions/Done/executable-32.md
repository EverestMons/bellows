# Bellows — Single-Glance Status CLI v2 (Running + Needs-Input Only)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
v2 of the status-CLI plan (v1 = plan 31, CEO-stopped at the mock-review gate to amend the design — see processed-verdict-31-step-1; not a quality failure). The SA design spec at `knowledge/architecture/status-cli-design-2026-06-12.md` remains AUTHORITATIVE for placement (the module decision), the data contract (read-only queries per section, `.bellows.lock` flock-probe liveness, absent-DB degradation, the daemon-stopped `stale?` marker rule) — EXCEPT the output format, where the CEO-AMENDED MOCK below OVERRIDES the spec's Mock A/B: the COMPLETED TODAY section and the totals footer are REMOVED. CEO intent verbatim: "mostly just wanting a way to track what is running and when something needs my input/is paused." The CLI renders exactly three elements — daemon header, IN-FLIGHT, AWAITING VERDICT — and nothing else. This plan closes FORWARD row 2.

**CEO-amended mock (acceptance target) — daemon running:**
```
● Bellows RUNNING  pid 48231  sha 5077b92  up 2h 16m

IN-FLIGHT
 #32  bellows   Step 1/2  running   4m   Single-Glance Status CLI v2 (Run…

AWAITING VERDICT
 #28  step 2  qa_checkpoint  verdict-request-28-step-2.md  12m
```
**Daemon stopped (with interrupted rows preserved per the spec's stale rule):**
```
○ Bellows STOPPED

IN-FLIGHT
 #32  bellows   Step 1/2  stale?    41m  Single-Glance Status CLI v2 (Run…

AWAITING VERDICT
 (none)
```
Empty sections render `(none)`. Values are illustrative; structure, columns, and ordering are binding. AWAITING VERDICT rows show: plan id, step, pause reason code, verdict-request filename, time since pause — the verdict-request filename is the actionable element.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then the SA spec at `knowledge/architecture/status-cli-design-2026-06-12.md` (data contract + placement), then this plan's CEO-amended mock (your acceptance target — it overrides the spec's mocks). **Scope is exactly: the module the spec places, `tests/` (one new test file matching repo naming).**
>
> Implement the CLI: read-only URI everywhere (`?mode=ro`); flock-probe liveness per the spec; absent-DB graceful message; the three-element output per the amended mock and NOTHING else (no completed section, no totals footer). AWAITING VERDICT derives from the verdicts table (`outcome IS NULL`) joined to the pending verdict-request filename convention, with time-since-pause. **Tests:** fixture lifecycle DB (existing conftest pattern): in-flight rendering; awaiting-verdict rendering with filename; both-empty `(none)` state; daemon-stopped `stale?` marker; absent-DB degradation; and a contract test that the output contains NO "COMPLETED" section. Run the FULL suite to an explicit pass/fail and READ THE TAIL. **Acceptance:** run the real CLI against the live DB and include the actual output in the dev log beside the amended mock. Write the dev log to `bellows/knowledge/development/status-cli-v2-dev-log-2026-06-12.md`. Use `with open()`; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/development/status-cli-v2-dev-log-2026-06-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the SA spec, this plan's amended mock, and the dev log. **Verify, each with executed evidence (files into `knowledge/qa/evidence/status-cli-v2-2026-06-12/`):** (1) **Full suite** — final 15 lines, zero failures, new-test count matches dev log; output to `full_suite_tail.txt`. (2) **Amended-mock conformance** — run the real CLI; structural match to the amended mock INCLUDING the absences (no COMPLETED section, no totals footer — grep the output to prove both absent); output to `mock_conformance.txt`. (3) **Needs-input correctness** — while this very plan is paused at YOUR step's end it cannot self-observe; instead verify against the fixture tests that AWAITING VERDICT renders the verdict-request filename and pause reason; output to `needs_input_check.txt`. (4) **Read-only + degradation** — grep every connect for `mode=ro`; absent-DB run is graceful; output to `safety_check.txt`. (5) **FORWARD reconciliation (Rule 42)** — `knowledge/FORWARD.md` row 2: Status → `closed-by-plan-<this plan's id>`, Plan-id link set; output diff to `forward_reconciliation.txt`. Also add the CLI invocation one-liner to `CLAUDE.md` (worktree) under a short "Status" heading.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `status-cli-v2-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/status-cli-v2-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/status-cli-v2-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, mock_conformance.txt, needs_input_check.txt, safety_check.txt, forward_reconciliation.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table and the Rule 20 banner block to `bellows/knowledge/qa/status-cli-v2-qa-report-2026-06-12.md`. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/status-cli-v2-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/status-cli-v2-2026-06-12/` (five evidence files per Rule 20 self-check)
