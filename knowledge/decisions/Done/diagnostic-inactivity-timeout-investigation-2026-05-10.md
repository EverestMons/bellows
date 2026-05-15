# Diagnostic — inactivity timeout doesn't fire on hung runner

**Project:** bellows | **Type:** diagnostic | **Steps:** 1 | **Priority:** 1 | **auto_close:** false

## Context

BACKLOG entry `2026-05-06: Inactivity timeout does not fire on hung runner — REPRODUCED` reports the configured 1800s threshold (per `bellows/config.json` `step_inactivity_timeout_seconds: 1800`) does not kill subprocesses in observed reproductions. Reproduction 1: `executable-half-up-currency-rounding-2026-05-06` Step 1 ran 41+ minutes with `last output 256s ago` advancing to `last output 910s+ ago`; runner kept emitting heartbeats but never fired the kill. Required manual `kill` of Bellows. Reproduction 2 (partial): same plan's Step 2 also showed extended quiet periods (last output 298s ago) without kill, but agent eventually produced more output and completed normally.

The 2026-05-01 BACKLOG-closed entry "activity-based timeout" claims this shipped via `executable-activity-timeout-2026-04-17` with QA-verified subprocess.Popen + threading + last_output_time reset on every stdout line + proc.kill on timeout. Three competing hypotheses for why the kill doesn't fire:

1. **Config-load bug** — the `step_inactivity_timeout_seconds` value isn't being loaded or threaded into the runner correctly
2. **Stdout buffer deadlock** — subprocess.Popen with PIPE'd stdout may deadlock if the buffer fills, with the heartbeat thread keeping the runner technically "active" even though no agent output is being consumed
3. **Activity-canary reset on wrong signal** — the `last_output_time` is being reset by something that isn't agent output (Bellows-side log writes, heartbeat thread itself, etc.)

Operational impact: every hung runner blocks recovery until CEO notices and manually kills Bellows, then requires plan re-dispatch + worktree cleanup. Today's recovery cost ~10 minutes including manual cherry-pick of completed-but-stranded worktree commit.

This diagnostic determines the actual root cause. Single SA step, read-only investigation, no QA.

## STEP 1 — Systems Analyst: inactivity timeout investigation

**Agent:** Bellows Systems Analyst
**Deposits:**
- `bellows/knowledge/research/inactivity-timeout-investigation-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_SYSTEMS_ANALYST.md, then PLANNER_TEMPLATE.md Phase 1.5 sources for any related lessons or research, including LESSONS.md (governance root) for entries tagged `bellows-architecture` or `planner-discipline` from the last ~14 days. Then read bellows/knowledge/BACKLOG.md (the 2026-05-06 inactivity timeout entry).

Read-only investigation. No code changes. Single deposit at bellows/knowledge/research/inactivity-timeout-investigation-2026-05-10.md.

CONTEXT
The activity-based timeout shipped 2026-04-17 via `executable-activity-timeout-2026-04-17` with QA verification. The 2026-05-06 reproduction shows the kill doesn't fire — runner emits heartbeats indicating "last output 256s ago" advancing to "910s ago" without subprocess termination, despite a 1800s `step_inactivity_timeout_seconds` config threshold. Three competing hypotheses; this diagnostic determines which.

INVESTIGATION QUESTIONS

Q1. CONFIG-LOAD AUDIT — read bellows/config.json and bellows/runner.py end-to-end. Document:
   (a) Current value of `step_inactivity_timeout_seconds` in config.json
   (b) How `runner.run_step()` receives the timeout value — what parameter name, how is it passed by the caller in bellows.py?
   (c) Where in `runner.run_step()` is the timeout value compared against `last_output_time`? Quote the exact code with line numbers.
   (d) Is the timeout value ever reassigned, defaulted, or overridden inside `run_step()` between receipt and use? Look for any `timeout = timeout or X` patterns or fallback chains that could silently substitute a different value.
   (e) The wall-clock cap is reportedly `timeout * 10` per the closed BACKLOG entry — verify this is still the case and identify where it's enforced.

Q2. SUBPROCESS PLUMBING AUDIT — document the subprocess invocation in `runner.run_step()`:
   (a) How is `claude -p` launched? Is it `subprocess.Popen` with PIPE'd stdout/stderr, or some other configuration?
   (b) How is stdout consumed? Synchronous read, threaded reader, async iteration?
   (c) Where is `last_output_time` updated? Quote the exact code line.
   (d) Where is the timeout check performed? Is it polled in a loop, or event-driven?
   (e) What happens on timeout — what code path runs to kill the subprocess?

Q3. STDOUT BUFFER DEADLOCK ANALYSIS — Hypothesis 2 from the BACKLOG. Determine:
   (a) Is stderr captured separately or merged with stdout? If captured with `stderr=subprocess.PIPE` and not actively read, the stderr pipe buffer (typically 64KB) can fill and block the subprocess on its next stderr write.
   (b) Are both stdout and stderr being read concurrently (separate threads or selectors)? If only one is read while the other accumulates, the unread pipe can deadlock the subprocess.
   (c) If the subprocess is deadlocked on a buffer, no further stdout is produced — meaning `last_output_time` is never updated, meaning the inactivity threshold SHOULD eventually fire. Verify this. If the timeout fails to fire even when stdout has stopped, that means the timer mechanism itself is broken.

Q4. ACTIVITY-CANARY RESET AUDIT — Hypothesis 3 from the BACKLOG. Determine:
   (a) Every place in the code that updates `last_output_time` (or equivalent activity-canary variable). For each, classify: is it being updated by genuine subprocess stdout, or by Bellows-side activity (heartbeat thread, log write, etc.)?
   (b) Is the heartbeat printed by the runner ("runner — Ns elapsed, last output Ms ago") emitted by reading subprocess output, or by the runner's own internal timer? If the latter, does it accidentally reset `last_output_time`?
   (c) Are there any background threads in the runner that could be writing to a shared variable that resets the canary?

Q5. EMPIRICAL TIMING DATA — examine the 2026-05-06 reproduction logs if available. Specifically:
   (a) The runner emits `runner — Ns elapsed, last output Ms ago` at 60s intervals. The progression `256s → 910s+` suggests the canary IS advancing (last_output Ms ago is incrementing), which means the canary is NOT being falsely reset. This is evidence AGAINST Hypothesis 3.
   (b) If the canary IS advancing toward 1800s and never crosses it, two possibilities: (i) the threshold actually being checked is not 1800s, or (ii) the kill check itself is gated behind something that never fires. Determine which.
   (c) Check if logs at /Users/marklehn/Desktop/GitHub/bellows/logs/ contain agent session transcripts from 2026-05-06 that might show the actual subprocess output stream up to the hang point.

Q6. KILL PATH VERIFICATION — independent of WHY the kill doesn't fire, document what HAPPENS when it does fire:
   (a) What does the kill code do? `proc.kill()`, `proc.terminate()`, signal-based kill?
   (b) Does it propagate to a parsed result that the caller sees? Or does the caller receive an exception?
   (c) After the kill, what state is the worktree in? What state is the plan file in?
   (d) Is there a notification path (Pushover, log line) that the kill fired? If yes, the absence of that notification in the 2026-05-06 reproduction is additional evidence that the kill path was never reached.

Q7. CROSS-REFERENCE WITH 2026-05-01 EMPIRICAL ANALYSIS — the 2026-05-01 closed BACKLOG entry (BACKLOG `2026-04-17: activity-based timeout`) cites a diagnostic at `bellows/knowledge/research/activity-based-timeout-diagnosis-2026-05-01.md` with empirical event-cadence analysis on 20 longest post-stream-JSON logs (P50=4.0s, P90=16.8s, P95=26.0s, P99=119.5s, longest run=743s/12.4m, zero timeout kills in 100-log corpus). Read this diagnostic and:
   (a) Did the analysis observe any cases where the gap exceeded the configured threshold? If P99=119.5s and longest=743s with threshold initially 2400s then tightened to 300s, the threshold tightening should have caused MORE kills, not zero.
   (b) Was the pre-tightening threshold (2400s) actually being enforced? Or was the test environment such that the kill path was never exercised?
   (c) The BACKLOG entry mentions "zero timeout kills in 100-log corpus" — does this mean the kills weren't triggered, or that the kills triggered but weren't recorded in the logs?

Q8. RECOMMENDATION — based on Q1–Q7, classify the bug:
   (i) **Config-load bug** — value not threaded to where the kill check happens. Specify the exact code path that drops the value.
   (ii) **Stdout/stderr buffer deadlock** — subprocess wedged on a pipe buffer; canary advancing correctly but kill check has a logic bug. Specify the bug.
   (iii) **Canary reset bug** — something Bellows-side is resetting `last_output_time` while subprocess is hung. Specify the reset site.
   (iv) **Threshold mismatch** — the value being checked is not the configured value. Specify what's actually being checked.
   (v) **Other** — describe.

   For the identified root cause, recommend a fix shape with: estimated LOC, risk level, and test approach.

DELIVERABLE
A single findings file at bellows/knowledge/research/inactivity-timeout-investigation-2026-05-10.md containing:
- One section per question (Q1–Q8) with answers and code citations
- A "Root Cause" section identifying the structural mechanism
- A "Recommended Fix" section with the preferred candidate from Q8 plus rationale
- A "Confidence" section: high / medium / low per major claim with evidence that would raise it

CONSTRAINTS
- Read-only investigation. No edits to bellows/.
- Use bash for git operations and log reads (per LESSONS.md 2026-04-23).
- Cite line numbers and quote code verbatim where load-bearing.
- If investigation reveals the BACKLOG entry's hypotheses are all wrong (e.g., the actual bug is somewhere else entirely), say so explicitly and explain.

RULE 20 SELF-CHECK
End the findings file with the canonical Rule 20 self-check Python block from PLANNER_TEMPLATE Rule 20. **USE THE VERBATIM TEMPLATE** — paste the block from PLANNER_TEMPLATE Rule 20 with only variable substitutions. The literal banner string `Rule 20 — QA Self-Check Results` (em-dash U+2014) and the literal output line `PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.` are load-bearing strings the Bellows gate enforces. ACTUALLY EXECUTE the block and include the literal stdout in the findings file.

Variable substitutions:
- plan_slug = "diagnostic-inactivity-timeout-investigation-2026-05-10"
- qa_report_path = "bellows/knowledge/research/inactivity-timeout-investigation-2026-05-10.md"
- evidence_dir = "bellows/knowledge/research/"
- required_evidence_files = ["inactivity-timeout-investigation-2026-05-10.md"]

When complete, end with the standard Output Receipt: status, summary of findings, deposit path.
```

**STOP. Do NOT proceed beyond Step 1. This is a single-step diagnostic.**
