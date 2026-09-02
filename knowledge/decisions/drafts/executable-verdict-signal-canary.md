# bellows — executable: CANARY for verdict-signal — one read-only step that pauses, so the restarted daemon proves it writes `awaiting_verdict` to the plan row

**Date:** 2026-09-01 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T0 | **Test Scope:** none (a read-only canary: one research deposit, no code, no DB write by the agent) | **Execution:** Step 1 (DEV) | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1

**auto_close:** false

**Slug:** `verdict-signal-canary-2026-09-01`

**Depends on:** `knowledge/decisions/Done/executable-100009.md` (Done 2026-09-01 21:13 — the change under test) and the CEO's dashboard restart of the daemon (pid 93535, started 21:14:31, from bellows main at `7bf0092`, which carries `2e74fc7`). Restart Discipline (PLANNER_TEMPLATE, *Restart Discipline*): after a code change, deposit a small canary whose characteristics exercise the changed path. The changed path is THE PAUSE ITSELF — so the canary's only requirement is to pause once with gates passed (the header pause, the case the old daemon left as `in_progress`).

**Tier computed (§1):** T0 — no trigger fires: one localized doc deposit under `knowledge/research/` (read-only class), no code, no production data written by the agent, same machine, nothing irreversible, no governance surface, and not authored from a diagnostic. **T0 runs the integration-vs-record pass only (Lens 4), then deposits.**

## Why this exists

Plan 100009 taught the daemon to write `awaiting_verdict` to `plans.lifecycle_state` at every pause and `in_progress` on resume, but its own two pauses ran under the pre-change process and read `in_progress` (its QA Item 6). The proof of the daemon half is the FIRST pause after the restart. This plan is that pause. **What the Planner measures at the pause, from outside the plan:** `sqlite3 -readonly /Users/marklehn/Developer/bellows/lifecycle.db "SELECT lifecycle_state FROM plans WHERE deposit_placeholder_name='executable-verdict-signal-canary.md'"` → `awaiting_verdict`; `logs/watch/executable-verdict-signal-canary.md.log` → a `WATCH: awaiting-verdict …` line followed by a `WATCH: push skipped (pushover keys empty)` line (the new delivery arm, on a machine whose keys are empty); after the `continue` verdict on this final step → `closed`. **The agent measures nothing about its own row's pause** — it cannot, it is not paused while it runs.

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the Bellows Developer.
>
> `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d knowledge/research ] && echo TREE_OK` — HALT unless TREE_OK.
>
> Write `knowledge/research/verdict-signal-canary-2026-09-01.md` with exactly these measured lines (raw command output, no interpretation):
> 1. `date -u +%Y-%m-%dT%H:%M:%SZ`
> 2. `git rev-parse --short HEAD` (your worktree HEAD — the source the daemon dispatched you from)
> 3. `/usr/bin/grep -cF -- 'mark_plan_state(plan_id, "awaiting_verdict")' bellows.py` (expected 4 — the change is in the tree you run in)
> 4. `sqlite3 -readonly /Users/marklehn/Developer/bellows/lifecycle.db "SELECT id||'|'||lifecycle_state FROM plans WHERE deposit_placeholder_name='executable-verdict-signal-canary.md'"` (expected `<id>|in_progress` — you are RUNNING; the pause comes after you stop; a `(14)` here is a WAL-sidecar environment state, record it verbatim and continue)
>
> Then commit that one file by explicit pathspec: `git add knowledge/research/verdict-signal-canary-2026-09-01.md && git commit -m "[<id from your plan filename>] verdict-signal canary: measured lines" -- knowledge/research/verdict-signal-canary-2026-09-01.md`. STOP.
>
> **Deposits:**
> - `knowledge/research/verdict-signal-canary-2026-09-01.md`
>
> **Scope:**
> - `knowledge/research/verdict-signal-canary-2026-09-01.md`

---

## Drafting Cycle

**Tier:** T0 (no trigger) — the integration-vs-record pass only, per §1.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-verdict-signal-2026-09-01.md
(This canary is recorded as a row of the parent cycle's register — its own cycle is the one T0 pass.)

- Integration-record: w1 dry — the deposit is one research file (read-only class, auto-clears); the step's four commands re-run by the Planner before deposit; the plan claims nothing about its own row's pause state (the Planner measures that from outside); `pause_for_verdict: always` on a single step is the exact shape that produced `in_progress` under the old daemon.

**Closing:** T0 floor pass dry; deposit.

## Cycle Manifest
tier: T0
target: knowledge/research/verdict-signal-canary-2026-09-01.md
class: read-only
reads: /Users/marklehn/Developer/bellows/bellows.py, /Users/marklehn/Developer/bellows/lifecycle.db
writes: knowledge/research/verdict-signal-canary-2026-09-01.md
open_forks: none
walks: 1
yields: 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: 1/1 walks have register rows
