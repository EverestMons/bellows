# Diagnostic: Bellows log-retention + disk-preflight guard — stop unbounded step.json from filling the disk and silently orphaning plans

**Type:** Diagnostic
**Project:** bellows
**Depends on:** none as prerequisite — investigates the bellows daemon at HEAD: `bellows.py` (`_rotate_logs` :90, `_create_worktree` :1055), `runner.py` (step.json writer :213, agent-never-moves-to-Done :26), `lifecycle.py` (`mark_plan_state` :219, `skipped_worktree_exists` :341, Done/halted resolution :695–717), `verdict.py` (`post_verdict_request` :179).
**Created:** 2026-08-12
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 1
**cycle_tier:** T1

---

## Why this exists

On 2026-08-12 the Data volume hit 100% (125Mi free) and cascaded: invoice-pulse plan **358's QA ran with a full disk** → ~156 test failures + 33 errors (tests couldn't write temp SQLite DBs) + a pytest summary-generation hang; the daemon couldn't create worktrees → **`skipped_worktree_exists` → plan 358 ORPHANED**; a finalize pass moved 358 to `Done/` **merged-to-main with NO Step-2 verdict review**, and the QA agent rationalized the disk-noise as "test-interaction artifacts." Deleting the accumulated logs (370 `*-step.json` files, **252M** → 616K) recovered the volume to 46Gi free.

**The root cause is a retention gap, and the deeper cause is a silent-failure gap.** This diagnostic scopes both so one executable can fix them. It decides/builds nothing (T-7 — a fix plan authors from these findings).

## What the Planner verified (re-verify at HEAD)

⚠️ **Planner read of the live bellows code + the 2026-08-12 logs; re-verify.**
1. **`_rotate_logs()` (`bellows.py:90`) has TWO gaps that together explain the fill:** (a) it prunes `*-step.json` only when **> 30 days old** — but the failure mode is VOLUME in a SHORT window (370 files / 252M in hours), none 30 days old, so it never fired; (b) it runs **at startup ONLY** ("Age-based cleanup at startup") — a daemon up for days never re-prunes. Terminal logs have the same shape (14-day age, startup-only). There is **no size or count cap**.
2. **step.json is written per step** at `runner.py:213` (`{timestamp}-step.json`) — the accumulator. Each is a full raw step transcript (100–300KB+); it is the raw-output source QA audits rely on, so retention must keep a WINDOW, not hard-purge.
3. **`_create_worktree()` (`bellows.py:1055`) is the natural disk-preflight hook** — it creates `.bellows-worktrees/<slug>/`. On a full disk this fails and the daemon takes the recovery path `skipped_worktree_exists` (`lifecycle.py:341`) — the SILENT orphan.
4. **Agents never move to Done (`runner.py:26`); the Planner/finalize does.** So a full-disk-orphaned plan can still be finalized to Done by the close path WITHOUT a verdict — the 358 process gap.

## Questions (deposit findings; decide/build NOTHING)

**Q1 — Quantify the accumulation + confirm the `_rotate_logs` gaps.** Measure the real growth rate of `logs/*-step.json` (files + MB per plan-step) from the 2026-08-12 evidence and current state. Confirm the age-only (30d) + startup-only behavior against the code, and that no size/count cap exists. Establish the realistic time-to-fill under a busy multi-session day (this session's rate).

**Q2 — Retention redesign (size/count-based, windowed).** Design retention that targets VOLUME, not just age: a cap on total step.json size or a keep-last-N-files/plans policy, pruning oldest first, with a floor that preserves the raw-output audit window (state the window — e.g., last N days OR last N plans, whichever keeps more recent). Cover the other growers too: terminal logs (same startup-only gap), `daemon-nohup.log` (does it grow unbounded?), `planner-consultation.jsonl` (already 10MB-rotated — confirm sufficient). What is safe to prune vs must-keep.

**Q3 — Cadence (not startup-only).** Where to run the sweep so a long-running daemon actually prunes: on plan-close (the `lifecycle.py` `mark_plan_state`/Done-move path — identify the exact hook), and/or a periodic timer, and/or inside `_create_worktree` before allocating. Name the hook site(s) and the trade-offs; per-close-only is insufficient because ORPHANED/HALTED plans (358, 363) skip a clean close — so a sweep independent of close is required.

**Q4 — Disk-preflight guard (fail LOUDLY).** At `_create_worktree` (`bellows.py:1055`) and/or step start, check free disk; if below a threshold (define — absolute floor like N GB, tie to the observed 125Mi break), REFUSE and surface loudly (raise + a verdict/alert/notifier) instead of the silent `skipped_worktree_exists` orphan (`lifecycle.py:341`). Trace the EXACT current path from ENOSPC → worktree-create failure → `skipped_worktree_exists` → finalize → Done, so the fix knows where to interpose the loud failure.

**Q5 — The finalize gap (fork — surface, don't decide).** 358 reached Done + merged **with no verdict** because a finalize closed a daemon-orphaned plan. Should the close/finalize path REFUSE to move a plan to `Done/` that never had a processed verdict for its final step (so a disk/daemon failure can NEVER ship unreviewed — it would `halted-` instead)? State the current finalize logic, what distinguishes a legitimate close from an orphan-finalize, and the blast radius of adding a verdict-required guard.

**Q6 — Verdict + fix scope.** Size the executable: the retention change (size/count + cadence), the disk-preflight guard, and (per Q5's fork) the optional finalize-verdict guard. Enough for a fix plan to be authored without re-running this.

## Method + boundaries

**READ-ONLY. Change no bellows code, no config; delete no logs (the 252M was already reclaimed).** Read the bellows source named in the header and the 2026-08-12 log evidence (the daemon terminal log + the accumulation record in memory `bellows-log-accumulation-fills-disk`). `grep -F` for literals; a negative needs a positive control. Deposit ONE findings doc: the accumulation quantification, the confirmed `_rotate_logs` gaps, the retention design (size/count + cadence + keep-window), the preflight-guard design + the exact silent-orphan path it interposes on, and the finalize-gap fork.

**Deposit:** `knowledge/research/log-retention-disk-guard-2026-08-12.md`

Standard prompt-feedback protocol → Output Receipt.

---

## Drafting Cycle
**Tier:** T1 — triggers: **T-7** (authored-from — a fix executable builds on these findings). Read-only, reversible, not a governance surface → not T2; no cold panel.
**Walks:** none yet — **v0**. Lens walk pending CEO direction (or promote-as-is).
**Closing:** not yet earned — v0.
