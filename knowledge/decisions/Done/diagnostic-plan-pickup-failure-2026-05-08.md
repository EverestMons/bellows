# bellows — Diagnostic: Plan Pickup Failure Investigation
**Date:** 2026-05-08 | **Tier:** Small | **Test Scope:** N/A (diagnostic) | **Execution:** Step 1 (DEV)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-plan-pickup-failure-2026-05-08.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

## CEO Context

**Today (2026-05-08), Bellows silently skipped a deposited plan.** Sequence:

1. CEO performed manual cleanup (archived stuck verdicts, moved a stranded plan to Done) and restarted Bellows daemon at ~13:51:20.
2. Bellows came up cleanly: heartbeats only, no warnings, "Watching 8 projects, Rescan interval: 30s."
3. Planner deposited a new QA-only plan to `invoice-pulse/knowledge/decisions/qa-action-queue-limit-and-contract-name-2026-05-08.md` shortly after.
4. Bellows continued heartbeating with no further log output. **No "RUNNING" line, no "started" line, no dispatch to claude -p.**
5. CEO eventually ran the plan manually via Claude Code (standalone subprocess outside Bellows orchestration).
6. The agent self-paused with "STOPPED. Waiting for your confirmation," and Planner moved the plan to Done by hand.

The plan made it to `Done/qa-action-queue-limit-and-contract-name-2026-05-08.md` successfully via manual run, so the original `decisions/qa-action-queue-limit-and-contract-name-2026-05-08.md` file no longer exists at the path it was deposited at.

**CEO uncertainty:** "Not sure — first time I'm paying close attention." Unknown whether this is a single occurrence or a recurring silent failure mode.

This diagnostic answers: **why didn't Bellows pick up the plan, and is this a one-off or systemic?**

Three secondary observations from the same session that the agent should mention IF stumbled across during investigation but should NOT proactively investigate:
- (S1) Plan filename remained `in-progress-qa-...md` after the agent paused — Bellows normally flips to `verdict-pending-` prefix at this stage. (Possibly because Bellows never claimed the plan in step 1 — consistent with non-pickup.)
- (S2) Earlier in the session, an executable plan's Step 1 (DEV) completed, then Bellows ran Step 2 (QA) without a verdict pause despite the prompt instructing "STOP after Step 1." Plan slug: `executable-action-queue-limit-and-contract-name-2026-05-08`.
- (S3) Earlier in the session, a verdict-resolved file targeting a plan already moved to Done caused a retry loop ("no verdict-pending plan found for ... — leaving in resolved/ for retry") that ran for ~12 minutes until manual intervention.

This is read-only. Do not modify any Bellows code. Do not run Bellows. Do not modify watched project plan files.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-plan-pickup-failure-2026-05-08.md", "bellows/knowledge/decisions/in-progress-diagnostic-plan-pickup-failure-2026-05-08.md")`. You are the Bellows Developer. Read your specialist file and the BACKLOG before reading any source. This is a read-only diagnostic — do NOT modify code, do NOT run Bellows. Investigate why the QA plan was not dispatched and deposit findings to `bellows/knowledge/development/diagnostic-plan-pickup-failure-findings-2026-05-08.md`. **Q1 — Reconstruct the rescan code path.** Read `bellows.py` and identify the function(s) that scan watched project `knowledge/decisions/` directories during each rescan tick. For each function: file, line range, and a one-paragraph summary of what files it considers eligible for dispatch. Specifically identify (a) the filename-prefix filter (which prefixes get dispatched — typically `executable-`, `diagnostic-`, `roadmap-`, etc., and which prefixes get skipped — `_staging-`, `in-progress-`, `verdict-pending-`, `halted-`, etc.). (b) Any debounce, deduplication, or "already seen this filename" memoization logic that could cause Bellows to skip a freshly-deposited file because the slug or path was previously known. (c) The exact log line(s) emitted when a plan IS picked up (e.g., "▶ started …") versus when a plan is silently skipped (likely no log line at all). **Q2 — Confirm or refute the most likely cause.** The Planner used the slug `qa-action-queue-limit-and-contract-name-2026-05-08`. The `qa-` prefix is unusual — diagnostic, executable, roadmap are common; qa- as a top-level plan prefix may not be in the dispatch whitelist. Read the prefix-filter code and report definitively: is `qa-` in the list of dispatched prefixes? If yes, that rules this hypothesis out and Q3 must explore alternatives. If no, this is the root cause and the silent-skip is by design (filename filter rejects it) but Bellows fails to log the rejection — a usability defect even if the filter is correct. **Q3 — Alternate hypotheses (only investigate if Q2 ruled out).** Consider: (a) was the plan's slug already known to Bellows from a prior session and de-duplicated? (b) does the rescan compare against a state file or in-memory set that survives restarts? (c) was there a worktree-prune timeout (BrewBuddy and forge timed out at startup per CEO log) that left the rescan in a degraded state? Cite the specific code path for whichever hypothesis you investigate. **Q4 — Check Bellows logs.** Find the log file at `bellows/logs/` — list the most recent 3 log files by mtime. For the log file covering 2026-05-08 ~13:51 to ~14:00, grep for the slug `qa-action-queue-limit-and-contract-name-2026-05-08` and for substring `action-queue-limit-and-contract-name`. Report every match with timestamp and surrounding 2 lines of context. If zero matches: state plainly that Bellows never logged seeing this plan filename — strong evidence of silent-skip at filter time, not a downstream failure. If matches exist: they reveal where dispatch broke down. **Q5 — Frequency check (was today a one-off?).** Grep the most recent 30 days of Bellows logs for the literal string ` started ` (the dispatch log line) and count occurrences per day. Then list every plan filename in `Done/` directories across all watched projects (the canonical list at `/Users/marklehn/Desktop/GitHub/[project]/knowledge/decisions/Done/`) — count files per project. Compare: rough ratio of "Done plans" vs "Bellows started lines" gives a sanity check for whether plans have been silently slipping past Bellows. A large disparity (many Done plans, few started lines) suggests systemic skipping. State the numbers without interpretation if they're inconclusive. **Q6 — Fix shape.** Based on findings: state whether the fix is (a) add `qa-` to the dispatch prefix whitelist (one-line fix if Q2 confirms), (b) add a "rejected/skipped: <filename> reason: <reason>" log line so silent skips become visible (small defensive logging change), (c) something more structural (debounce/dedup bug, etc.) that warrants its own executable. Estimate LOC for the recommended fix. **Secondary observations:** if during investigation the agent encounters code paths relevant to (S1) plan filename not flipping to `verdict-pending-`, (S2) Step 2 auto-advance without verdict pause, or (S3) verdict-resolved retry loop targeting plans in Done, mention them under a "Secondary Observations" heading with file/line citations — but do NOT investigate proactively. These are tracked for separate work. Deposit findings using a single-call write (Filesystem:write_file). The findings file MUST end with an Output Receipt: Complete. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit with message: "docs: bellows plan pickup failure diagnostic findings".
>
> **STOP. Do NOT proceed. Do NOT move the plan to Done — that is the Planner's responsibility after Rule 22 verification.**
