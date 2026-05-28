# Bellows — Periodic Rescan Miss Disposition

**Date:** 2026-05-28 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** n/a | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** always

## Context

The 2026-05-28 BACKLOG entry `Watcher misses move_file-deposited plans — periodic decisions/ rescan as self-heal` proposes adding a periodic `decisions/` rescan on the heartbeat cadence so a missed filesystem move-event self-heals within one rescan interval instead of needing a manual daemon restart. The entry's symptom: a session-12 `executable-*` plan deposited via atomic `move_file` sat unclaimed ~9 minutes (heartbeats continued, no `detected plan` event) until a manual restart's startup scan claimed it.

**The entry's proposed fix appears to already exist in code.** `Bellows._rescan` (bellows.py:1156) is called on the heartbeat loop every `rescan_interval = 30` seconds (bellows.py:1455, 1462-1464). Its final block (bellows.py:1171-1177) loops every watched `decisions/` directory, matches every `is_runnable_plan(fname)`, and calls `handler._handle(full_path, from_rescan=True)` — a general unclaimed-plan sweep independent of filesystem events. If this mechanism works as written, the session-12 plan should have been claimed within ~30 seconds, not ~9 minutes.

This diagnostic does NOT ship code and does NOT design a new rescan. The existing rescan is the prior art. The diagnostic's job is to explain WHY the existing `_rescan` general-sweep did not claim the session-12 plan, and to recommend whether any fix is warranted or whether the existing mechanism is sufficient and the miss was a transient/edge case. The likely outcome is either a narrow guard-fix to the existing sweep or a won't-fix closure with the BACKLOG entry re-framed (the fix it proposes is dead code).

## STEP 1 — Systems Analyst disposition (SA)

> **FIRST — before doing anything else, claim this plan:** rename `diagnostic-rescan-miss-disposition-2026-05-28.md` to `in-progress-diagnostic-rescan-miss-disposition-2026-05-28.md` using `mv` in the worktree. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor — dense SA reading phases have hung past the 600s inactivity threshold in prior sessions. **AFTER posting confirmation:** read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first, then read the files listed below.
>
> Acting as the Bellows Systems Analyst, determine why the existing periodic `_rescan` general-sweep did not claim the session-12 `move_file`-deposited plan within a rescan interval, and recommend a disposition. This is a disposition diagnostic: the proposed BACKLOG fix (add a periodic rescan) already exists at bellows.py:1171-1177, so the real question is why it did not fire — NOT how to add one.
>
> **Files to read (post a 1-line "Read X." acknowledgment after each):**
>
> 1. `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — specialist scope.
> 2. `bellows/bellows.py` — read in full: `_rescan` (line ~1156), the `start()` heartbeat loop (lines ~1419-1483, especially the rescan-interval call site ~1462), `PlanHandler._handle` (line ~1033, especially the `_seen` guard at ~1046 and the `from_rescan` branches ~1050-1066), `on_created`/`on_modified`/`on_moved` (lines ~1070-1095), and the `is_runnable_plan` function (grep for its definition).
> 3. `bellows/verdict.py` — `slug_from_path` (the `_seen` set is slug-keyed; confirm how a slug is derived and whether a `move_file`-deposited filename could collide with or differ from the slug stored at any earlier point).
> 4. The session-12 terminal log at `bellows/logs/terminal/bellows-2026-05-28.log` — this is GROUND TRUTH. Find the deposit→claim window for the session-12 executable plan. Determine: (a) did any `_rescan` tick run during the unclaimed window (look for rescan-associated log lines, `_consume_verdicts` output, parallel-group dispatch lines, or any per-tick marker); (b) did the rescan's general-sweep block (1171-1177) execute, or did `_rescan` abort earlier (exception in `_consume_verdicts` or the parallel-group loop); (c) the exact timestamps of deposit, manual restart, and startup-scan claim.
> 5. `bellows/knowledge/BACKLOG.md` — re-read the full `Added 2026-05-28: Watcher misses move_file-deposited plans` entry. Note its claim that the restart's startup scan caught it immediately.
>
> **Post a 1-line "Drafting Section N." marker at the start of each section below.**
>
> **Section 1 — Existing rescan mechanism map.** Document what `_rescan` actually does, step by step: the `_consume_verdicts` call, the parallel-group settle-window block, and the general-sweep block at 1171-1177. Cite line numbers verbatim. Confirm or refute: does the general-sweep block scan `decisions/` for ALL runnable plans regardless of filesystem events, calling `_handle(..., from_rescan=True)` on each? State plainly whether the BACKLOG entry's proposed fix already exists.
>
> **Section 2 — `_seen` guard trace.** Trace what happens when `_handle(full_path, from_rescan=True)` is called on an unclaimed `executable-*` plan whose slug is NOT yet in `_seen`. Walk the guard at line ~1046 and the `from_rescan` branches. Then trace the case where the slug IS already in `_seen` (e.g., added by an earlier `on_created`/`on_moved` event that fired but failed to dispatch). Determine whether a slug could be stranded in `_seen` such that every subsequent rescan tick skips it at the guard. This is hypothesis (b).
>
> **Section 3 — Hypothesis test against the log.** Using the session-12 log as ground truth, evaluate each hypothesis and mark each CONFIRMED / REFUTED / INSUFFICIENT-EVIDENCE with the specific log evidence:
> - (a) `is_runnable_plan(fname)` returned False for the deposited `executable-*` filename (classification bug). Check `is_runnable_plan`'s prefix logic against the actual filename.
> - (b) slug stuck in `_seen` so the guard skipped it every tick (from Section 2).
> - (c) the ~9-min claim actually came from a normal `_rescan` tick and the BACKLOG misattributed it to the manual restart (check whether the claim timestamp aligns with a 30s rescan boundary vs. the restart time).
> - (d) `_rescan` raised an exception before reaching line 1171 on the relevant ticks (e.g., in `_consume_verdicts` or the parallel-group block), silently aborting the sweep. Check the log for any error/traceback lines or an abrupt absence of post-`_consume_verdicts` output during the window.
> - (e) Any hypothesis the SA forms from the evidence that is not in this list.
>
> **Section 4 — Disposition recommendation.** Based on the confirmed hypothesis (or insufficient-evidence finding), recommend ONE of:
> - **Won't-fix / re-frame BACKLOG:** the existing rescan is sufficient; the miss was transient or unreproducible; the entry's proposed fix is dead code. State what re-framing the BACKLOG entry needs.
> - **Narrow guard-fix:** a specific, small change to the EXISTING rescan or `_seen` lifecycle (e.g., `_seen` invalidation on a specific path, an exception guard around a sweep sub-step). Specify the exact insertion point, the change shape, the LOC estimate, and the regression-test surface. Do NOT specify adding a new rescan.
> - **Insufficient evidence to disposition:** the log does not contain enough to distinguish hypotheses. State exactly what additional instrumentation or a reproduction would be needed.
>
> **Section 5 — Flags for next step.** Note any assumptions, any code read that contradicted the BACKLOG entry's framing, and any edge cases (settle-window interaction, parallel-group `_pending_groups` state, concurrent claim during a rescan tick) that a follow-on executable would need to preserve.
>
> **Deposits:**
> - `bellows/knowledge/research/rescan-miss-disposition-2026-05-28.md` — the full disposition (Sections 1-5).
