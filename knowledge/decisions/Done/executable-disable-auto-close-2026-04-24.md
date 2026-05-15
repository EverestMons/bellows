# Bellows — Disable Auto-Close: Restore Terminal-Step Pause Discipline
**Date:** 2026-04-24 | **Tier:** Medium | **Test Scope:** full-suite | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (Documentation) → Step 4 (QA)

## Context

Failure 3 diagnostic (`bellows/knowledge/architecture/failure-3-ordering-2026-04-24.md`) confirmed that auto-close is the structural root cause of stranded-verdict requests: Bellows evaluates gates AFTER the agent performs Rule 8 + Rule 23 housekeeping (which includes move-to-Done). When a terminal gate trips, the plan is already in `Done/` and the verdict request references shipped work. The CEO's architectural judgment: Bellows should dispatch and gate, but NOT decide that a plan succeeded. Terminal-state decisions belong to Planner (Layer 3).

This plan disables auto-close. Every terminal step produces a verdict request. Planner reads the verdict, applies Rule 22, and moves the plan to `Done/` via direct `Filesystem:move_file`. Agent's Rule 8 housekeeping drops the move-to-Done operation.

**Secondary purpose:** restore pause visibility. Bellows eliminated manual-bootstrap friction but also eliminated the observation surface where legitimate pauses surface. This plan rebuilds that surface so future work can identify which pauses are safe to auto-approve — data-driven rather than intuition-driven.

**What this plan subsumes (BACKLOG items that dissolve or transform on ship):**
- "Move-to-Done fires before gate check (Failure 3)" — structurally resolved
- "QA-checkpoint pause is architecturally decorative" — same root cause, resolved
- "Single-step diagnostic generates verdict request on successful completion" — goes from "bug" to "intended behavior"

## How to Run This Plan

Deposit via Bellows normal dispatch. Each step pauses per `auto_close: false` behavior (which is what this plan SHIPS — dogfood will catch any regression). Planner reads each step's deposit via Rule 22 verification and resolves the verdict to proceed.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("knowledge/decisions/executable-disable-auto-close-2026-04-24.md", "knowledge/decisions/in-progress-executable-disable-auto-close-2026-04-24.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — this is an architecture + governance mapping task, no domain interpretation needed.
>
> **Task.** Produce a blueprint for four coordinated changes: (1) Bellows code change to invert auto-close default, (2) PLANNER_TEMPLATE Rule 8 edit to remove agent move-to-Done, (3) PLANNER_TEMPLATE Rule 23 edit to update the "structural completion gate" rationale, (4) PLANNER_TEMPLATE Rule 25 extension to specify Planner-owned Done/ move on clean verdict resolution. Plus pause-telemetry design.
>
> **Bellows code scoping (part 1).** Read `bellows/bellows.py` focusing on `run_plan()` and the auto-close branch (Q1 of the Failure 3 diagnostic cited lines 363-381, but verify current line numbers). Map: (a) where `auto_close` is read today (config value, plan-header field, hardcoded default?), (b) what the auto-close branch does on gate-pass (specifically the `shutil.move(source, done_path)` at L375-376), (c) what code path runs when auto-close is disabled (the existing `auto_close_disabled` pause-reason code — trace exactly what Bellows does differently in that branch), (d) the relationship between auto-close and the post-verdict-request path (L332-358 gate-fail branch vs L363-381 gate-pass branch). Produce a before-and-after pseudocode sketch showing the exact branches that change. Propose: is this a config inversion (`auto_close_default: False`), a plan-header default change, or code removal? Pick one and justify.
>
> **Governance scoping (part 2).** Read `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. For each of the three target rules (Rule 8, Rule 23, Rule 25), extract the exact paragraphs that need editing and specify the new text. Specifically:
> - **Rule 8**: The QA step's final-operations ordering ("deliverable verification → QA deposit → PROJECT_STATUS.md update → feedback append → final commit → move plan to Done") must drop "move plan to Done." The Planner now owns that move. Rewrite the final-step ordering. Also update the paragraph that begins "Diagnostic plans use a different closeout pattern — see Rule 22" — that reasoning still holds but the Planner-does-the-move detail changes.
> - **Rule 23**: The three-constraint statement (anchored edits, enumerated sub-steps, ordering) still applies to what the agent does. But the rationale "The move-to-Done is always the absolute last operation. It is the structural completion gate Bellows uses to mark the plan complete" is no longer true. Rewrite the rationale to reflect: final commit is the absolute last agent operation; the Planner performs the move-to-Done after Rule 22 verification passes.
> - **Rule 25**: Add a new routing case. Today the pause-reason table has 5 explicit routes (auto_close_disabled, qa_checkpoint, gate_failure, scope_violation, other). Under this plan, EVERY terminal step produces a verdict with pause_reason `auto_close_disabled` (or whatever new code is assigned — SA decides). Rule 25 must specify: on clean verdict (pass + Rule 22(a)-(e) clean), the Planner performs the move via `Filesystem:move_file` from `bellows/knowledge/decisions/in-progress-[slug].md` to `bellows/knowledge/decisions/Done/[slug].md` (stripping the `in-progress-` prefix). Include the exact tool call pattern. Confirm this stays within Planner's declared filesystem access scope (yes — file renames within `[project]/knowledge/decisions/` is already allowed).
>
> **Pause-telemetry design (part 3).** Every verdict resolution should produce a persistent record for future pattern analysis. Minimum viable: a shared log file at `bellows/knowledge/verdict-log.md` that the Planner appends to on every verdict resolution. Each entry captures: plan slug, step number, pause reason code, gates that passed/failed, Rule 22 result, Planner's decision (clean close / escalated to CEO / reverted), timestamp. Specify the exact markdown table schema. Do NOT design auto-approval logic — Phase 2 work. Just the observation surface.
>
> **Test impact (part 4).** Skim `bellows/tests/test_bellows.py` for tests that exercise the auto-close branch. Enumerate which tests need updating, which need new coverage (disable-auto-close is the default), and estimate net test delta (approximate: +N tests, -M tests changed). Do not rewrite tests — just enumerate.
>
> **Rollback plan (part 5).** If this ships and produces unacceptable Planner friction, what's the reversal path? Specify the single-commit revert shape: which files reverse, which governance edits undo, whether any data (verdict-log.md entries) can be preserved for future Phase 2 work. One paragraph.
>
> **Deposit.** Single file at `knowledge/architecture/disable-auto-close-blueprint-2026-04-24.md`. Structure: (1) Bellows code change pseudocode + file/line references, (2) governance edits with exact old-text and new-text blocks for Rule 8, Rule 23, Rule 25, (3) verdict-log.md schema, (4) test impact enumeration, (5) rollback plan. Close with Layer Impact table (required by your specialist file) and standard Output Receipt.
>
> **Deposits:**
> - `knowledge/architecture/disable-auto-close-blueprint-2026-04-24.md`
>
> **Do NOT write code. Do NOT edit governance files. Blueprint only.**
>
> **Feedback.** Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — BELLOWS DEVELOPER

---

> **Prior-step verification.** Before starting, read `knowledge/architecture/disable-auto-close-blueprint-2026-04-24.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` first. Skip the domain glossary — this is a Bellows internals code change, no domain interpretation needed.
>
> **Task.** Execute the Bellows code change specified in Section 1 of the SA blueprint. Cite blueprint section numbers as your guide; do not restate the design, just implement. Update or add tests per Section 4 of the blueprint. Run the full test suite and confirm no regressions.
>
> **Implementation.** Follow the blueprint's pseudocode exactly. If during implementation you discover a detail the blueprint missed (e.g., the `auto_close` flag also gates some other behavior not in the SA's scope), STOP, flag it in the dev log, and await CEO guidance. Do not exceed blueprint scope.
>
> **Test execution.** Run `python3 -m pytest tests/` from the bellows directory. Capture the full output. Pipe to `knowledge/qa/evidence/disable-auto-close-2026-04-24/pytest_dev_pre_commit.txt` so QA has a pre-commit baseline.
>
> **Commit.** Use a descriptive commit message, e.g., "feat: disable auto-close default — terminal steps always pause for Planner".
>
> **Deposit dev log** at `knowledge/development/disable-auto-close-dev-log-2026-04-24.md`. Structure per your specialist file's output format. List every file modified with line ranges. List every test added or changed. Include the pre-commit test baseline count. Close with standard Output Receipt — Files Created or Modified (Code) section must enumerate every deliverable for Rule 17 verification in Step 4.
>
> **Deposits:**
> - `knowledge/development/disable-auto-close-dev-log-2026-04-24.md`
> - `knowledge/qa/evidence/disable-auto-close-2026-04-24/pytest_dev_pre_commit.txt`
>
> **Feedback.** Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 3 — BELLOWS DOCUMENTATION ANALYST

---

> **Prior-step verification.** Before starting, read `knowledge/development/disable-auto-close-dev-log-2026-04-24.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows Documentation Analyst. Read your specialist file at `agents/BELLOWS_DOCUMENTATION_ANALYST.md` first. Skip the domain glossary — this is a governance-file edit task, no domain interpretation needed.
>
> **Task.** Execute the three governance edits specified in Section 2 of the SA blueprint. The target file is `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Edits are to Rule 8, Rule 23, and Rule 25. Use `Desktop Commander:edit_block` with exact anchor strings from the blueprint's old-text blocks. Do NOT paraphrase the blueprint's new-text — copy verbatim. Bump PLANNER_TEMPLATE.md's version field and Last Updated date.
>
> **Anchored edits (Rule 23 reminder).** Each edit must use the verbatim existing text as `old_string`. The blueprint provides the exact anchors. If an anchor doesn't match on first attempt, STOP — do not guess. Report the mismatch and wait for CEO guidance. Do not attempt fuzzy matches or multi-replacement edits.
>
> **Verification.** After each edit, read back the modified section to confirm the change landed correctly. Pipe the three modified rule sections to `knowledge/qa/evidence/disable-auto-close-2026-04-24/governance_edits_applied.txt` so QA can verify in Step 4.
>
> **Create verdict-log.md.** Per Section 3 of the blueprint, create `bellows/knowledge/verdict-log.md` with the schema the SA specified. Include a brief header block explaining purpose ("Planner appends to this log on every verdict resolution — observation surface for future auto-approval patterns"), the markdown table schema, and an initial empty table ready for entries. Do NOT backfill historical entries — log starts fresh from this plan forward.
>
> **Commit.** Descriptive message, e.g., "docs: disable auto-close — Rule 8/23/25 edits + verdict-log.md".
>
> **Deposit doc log** at `knowledge/documentation/disable-auto-close-doc-log-2026-04-24.md`. Enumerate every edit applied. Close with standard Output Receipt.
>
> **Deposits:**
> - `knowledge/documentation/disable-auto-close-doc-log-2026-04-24.md`
> - `knowledge/qa/evidence/disable-auto-close-2026-04-24/governance_edits_applied.txt`
>
> **Feedback.** Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 4 — BELLOWS QA

---

> **Prior-step verification.** Before starting, read `knowledge/documentation/disable-auto-close-doc-log-2026-04-24.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA specialist. Read your specialist file at `agents/BELLOWS_QA.md` first. Skip the domain glossary — this is a verification and regression task.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the Step 2 dev log's "Files Created or Modified (Code)" section and the Step 3 doc log's enumerated edits. For EVERY deliverable: verify it exists on disk with the described change. For bellows.py edits: grep for the specific functions/branches the blueprint changed. For test file additions: grep for new test function names. For PLANNER_TEMPLATE.md edits: grep for the new text of Rule 8, Rule 23, Rule 25 (post-edit language, not pre-edit). For verdict-log.md: confirm file exists at `bellows/knowledge/verdict-log.md` and contains the schema. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit raw grep outputs to `knowledge/qa/evidence/disable-auto-close-2026-04-24/grep_deliverables.txt`. Any ❌ item blocks the plan from closing.
>
> **Test regression.** Run the full test suite: `python3 -m pytest tests/ -v` from the bellows directory. Pipe the full output to `knowledge/qa/evidence/disable-auto-close-2026-04-24/pytest_full.txt`. Compare to Step 2's pre-commit baseline (`pytest_dev_pre_commit.txt`). Confirm: passed count is ≥ baseline, failed count is ≤ baseline, no new error categories introduced. Acknowledge any pre-existing failures explicitly and mark PASS for those rows. Record exact numbers (e.g., "137 passed, 1 failed — baseline was 137/1, no regression").
>
> **Live smoke test — the critical one.** Deposit a trivial canary plan at `bellows/knowledge/decisions/executable-auto-close-canary-2026-04-24.md` with content exactly: "# Canary\n\n## Step 1 — Bellows QA\n\n> Report 'canary ran' and do nothing else.\n>\n> **Deposits:**\n> - none". Wait for Bellows to dispatch and complete the plan. Then verify: (1) plan paused at terminal step (look for `PAUSED` in terminal output or `verdict-pending-` filename), (2) a verdict request file was created in `bellows/verdicts/pending/` with pause_reason code matching what the blueprint specified, (3) the plan file is NOT in `bellows/knowledge/decisions/Done/` (plan should still be in `verdict-pending-` or `in-progress-` state). Dump the verdict request file content to `knowledge/qa/evidence/disable-auto-close-2026-04-24/canary_verdict.txt`. If any of (1)/(2)/(3) fails, this is a CRITICAL failure — the plan did not actually disable auto-close.
>
> **Post-canary cleanup.** The canary plan will be stranded in verdict-pending state by design. Move it to `bellows/knowledge/decisions/Done/executable-auto-close-canary-2026-04-24.md` as part of this QA step — proof that the Planner-owned move works end-to-end. Remove the verdict request file from `bellows/verdicts/pending/` (manual cleanup; Planner does this in normal ops but we're simulating that flow here).
>
> **QA report.** Deposit at `knowledge/qa/disable-auto-close-qa-report-2026-04-24.md`. Structure: (i) Deliverable Verification table, (ii) Test Regression summary with baseline comparison, (iii) Live Smoke Test results (all three sub-verifications), (iv) any flags. Close with standard Output Receipt.
>
> **Rule 19 reminder.** If you cannot complete a check, mark it ❌ with reason. Do NOT mark ✅ with hedging language ("pending", "inferred", "skipped", etc.). Rule 20's self-check will auto-fail the plan if positive-status rows contain hedging keywords.
>
> **Rule 20 Self-Check.** Execute the following Python block verbatim. Include its literal stdout in the QA report. If it prints FAILED, STOP — do not update PROJECT_STATUS.md, do not perform housekeeping. Report the failure and wait.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-disable-auto-close-2026-04-24"
> qa_report_path = "knowledge/qa/disable-auto-close-qa-report-2026-04-24.md"
> evidence_dir = f"knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "pytest_dev_pre_commit.txt",
>     "governance_edits_applied.txt",
>     "grep_deliverables.txt",
>     "pytest_full.txt",
>     "canary_verdict.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED")
> ```
>
> **Final operations (ordering per Rule 23, updated for new model).** (a) Update PROJECT_STATUS.md — add completed milestone entry summarizing the four changes (Bellows code, Rule 8, Rule 23, Rule 25, verdict-log.md introduction, ~N tests added). (b) Feedback append per standard protocol. (c) Final commit with descriptive message. **STOP.** Do NOT move this plan to Done/. Per the new model (which this plan SHIPS), the Planner performs the terminal move after Rule 22 verification. Report Status: Complete and wait.
>
> **Deposits:**
> - `knowledge/qa/disable-auto-close-qa-report-2026-04-24.md`
> - `knowledge/qa/evidence/disable-auto-close-2026-04-24/grep_deliverables.txt`
> - `knowledge/qa/evidence/disable-auto-close-2026-04-24/pytest_full.txt`
> - `knowledge/qa/evidence/disable-auto-close-2026-04-24/canary_verdict.txt`

---
