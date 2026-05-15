# Eluvian Governance — Plan-Write-Time LESSONS Re-Read Rule
**Date:** 2026-05-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOCUMENTATION_AGENT) → Step 2 (QA_ANALYST) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-plan-write-time-lessons-reread-2026-05-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

## CEO Context

Implements Lessons Forge proposal #1 (entry 1, 2026-04-14): adds a plan-write-time LESSONS re-read discipline to PLANNER_TEMPLATE Phase 1.5 Source D.

The current Source D (PLANNER_TEMPLATE.md ~line 80) instructs the Planner to read all `planner-discipline`-tagged entries at session start. This catches lessons at the wrong moment: before any specific plan is being drafted. The recurring failure mode — captured-but-not-internalized — happens when the Planner reads the rule at session start, then writes a plan hours later under different cognitive load, and forgets the rule despite having seen it.

Today's 2026-05-13 LESSONS entry is the third reproduction of this pattern in three days: the `pending/` vs `resolved/` verdict-directory error was captured 2026-05-12 (tagged `planner-bellows-integration`, not `planner-discipline`, so it didn't catch the perma-read), but even if it had been tagged correctly, the session-start read would not have helped — the violation happened when authoring verdict files mid-session, hours after the read.

The proposal locks the discipline as: before writing any plan that involves housekeeping (PROJECT_STATUS edits, verdict deposits, Done/ moves, governance edits, commit ordering), re-read the most recent `planner-discipline`-tagged LESSONS entries. This is a targeted, write-time read — not a full Source D refresh.

This plan is small (single-file governance edit). Two steps: DEV (Documentation Agent extends Source D), QA (verify edit landed correctly, full PLANNER_TEMPLATE parses cleanly).

Repo: governance root (`/Users/marklehn/Desktop/GitHub/`). Per Rule 8 governance-root commit pattern: DEV commits to governance repo, QA's PROJECT_STATUS update applies to bellows (the canonical project tracking this plan's lifecycle).

---
---

## STEP 1 — ELUVIAN_DOCUMENTATION_AGENT

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-plan-write-time-lessons-reread-2026-05-13.md", "bellows/knowledge/decisions/in-progress-executable-plan-write-time-lessons-reread-2026-05-13.md")`. You are the Eluvian Documentation Agent. Skip specialist file and glossary reads — this is a governance file edit task. Read `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` Phase 1.5 Source D (currently around line 76-84) to confirm the current text. Use `Desktop Commander:edit_block` to extend Source D with a new paragraph about plan-write-time re-reads. The anchor is the existing line `- **All entries tagged \`planner-discipline\` regardless of age** (catches discipline rules permanently)`. Replace it with that exact line followed by `\n\n**Plan-write-time discipline (re-read trigger):** The session-start read of \`planner-discipline\` entries is insufficient on its own. Captured lessons fade under task-specific cognitive load. Before authoring any plan that involves housekeeping operations — PROJECT_STATUS edits, verdict file deposits, plan moves to Done/, governance-file edits, multi-step commit orderings, or any Bellows-side artifact with a strict contract (verdict response, deposit block reference, plan header, Rule 20 banner) — the Planner re-reads the 5 most recent \`planner-discipline\`-tagged entries from \`/Users/marklehn/Desktop/GitHub/LESSONS.md\`. This is a targeted re-read, not a full Phase 1.5 refresh. The read is mechanical: open the file, scan for the tag, read the last 5 entries with that tag, note any whose mitigation guidance applies to the plan being drafted. Cost: ~30 seconds. Prevents the recurrence pattern captured 2026-05-13 (third reproduction of the \`pending/\` vs \`resolved/\` verdict-directory error within three days; the originating lesson was in context at session start but not consulted at the decision point).`. Bump PLANNER_TEMPLATE version 4.38 → 4.39 in the header (line 5) and update Last Updated date to 2026-05-13. Add a new Lessons Learned table row at the appropriate location in the Lessons Learned table: date 2026-05-13, text capturing the pattern — "Captured-but-not-internalized failure mode resolved by plan-write-time re-read discipline. Source D's session-start read of \`planner-discipline\` entries catches lessons too early in the session; recurring failure modes need a re-trigger at the moment of plan authoring. Today's 2026-05-13 incident (third \`pending/\` vs \`resolved/\` recurrence in three days) was the direct evidence. New paragraph appended to Source D making the plan-write-time re-read mandatory for housekeeping-bearing plans. Promoted from Lessons Forge accepted proposal #1." Commit the governance-root change with message: `feat(planner): plan-write-time LESSONS re-read discipline (Source D extension) — v4.39`. After the commit, append a dev log to `bellows/knowledge/development/plan-write-time-lessons-reread-2026-05-13.md` recording: file edited (PLANNER_TEMPLATE.md), version bump (4.38 → 4.39), Source D extension wording, Lessons Learned row added, commit SHA, Output Receipt status Complete. After your output receipt, read `bellows/knowledge/research/agent-prompt-feedback.md` and append a dated entry per the standard protocol. Commit the feedback entry with message: `docs: prompt feedback — Documentation Agent plan-write-time-lessons-reread`. **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
> - `bellows/knowledge/development/plan-write-time-lessons-reread-2026-05-13.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS_QA

---

> Before starting, read `bellows/knowledge/development/plan-write-time-lessons-reread-2026-05-13.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding. You are the Bellows QA Analyst. Skip specialist file and glossary reads — this is a governance file edit verification task. **FIRST — Deliverable Verification (Rule 17).** Read the prior DEV step's deposited dev log Files Modified list. For PLANNER_TEMPLATE.md: (a) grep for the literal banner string `Plan-write-time discipline (re-read trigger):` — must appear exactly once; (b) grep for the literal version string `**Version:** 4.39` in the header — must appear exactly once; (c) grep for the literal Last Updated string `2026-05-13 (v4.39)` — must appear exactly once; (d) verify the new Lessons Learned table row exists by grepping for the date `2026-05-13` in the Lessons Learned table section. For the dev log: (e) verify the file exists at the declared path; (f) verify it contains the commit SHA. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If any item is ❌, attempt to fix or report blocked. **Live render check:** read PLANNER_TEMPLATE.md from line 60 to line 100 inclusive (the Source D context window) and confirm the new paragraph reads cleanly inline — no broken markdown, no accidentally-escaped backticks. Capture the read output to `bellows/knowledge/qa/evidence/executable-plan-write-time-lessons-reread-2026-05-13/source-d-render.txt`. **Rule 20 self-check:** run the canonical Python block from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with these values: `plan_slug = "executable-plan-write-time-lessons-reread-2026-05-13"`, `qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/plan-write-time-lessons-reread-qa-2026-05-13.md"`, `evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-plan-write-time-lessons-reread-2026-05-13/"`, `required_evidence_files = ["source-d-render.txt"]`. Include literal stdout output of the block in the QA report; halt and report to CEO if FAILED. **PROJECT_STATUS update:** append a 2026-05-13 entry to `bellows/PROJECT_STATUS.md` covering this ship: PLANNER_TEMPLATE v4.38 → v4.39, Source D extended with plan-write-time re-read discipline, originating from Lessons Forge accepted proposal #1, governance-root commit SHA recorded. **Deposit QA report at `bellows/knowledge/qa/plan-write-time-lessons-reread-qa-2026-05-13.md`** with verification table, live render check, Rule 20 self-check banner, Output Receipt Complete. Commit the QA report to the bellows repo with message: `qa: plan-write-time-lessons-reread (PLANNER v4.39) — verification PASS`. After your output receipt, read `bellows/knowledge/research/agent-prompt-feedback.md` and append a dated entry per the standard protocol. Commit the feedback entry with message: `docs: prompt feedback — QA plan-write-time-lessons-reread`. **Deposits:**
> - `bellows/knowledge/qa/plan-write-time-lessons-reread-qa-2026-05-13.md`
> - `bellows/knowledge/qa/evidence/executable-plan-write-time-lessons-reread-2026-05-13/`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT move the plan to Done — that is the Planner's responsibility after Rule 22 verification.**
