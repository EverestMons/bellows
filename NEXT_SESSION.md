# Bellows — Next Session Baton

**Last session:** 2026-06-01 (follows 2026-05-31)
**Last session focus:** Shipped Gap 1(b) of the worktree teardown→resume regression — a guard that blocks a continue verdict over an uncleared `worktree_teardown` failure, routing the plan to `halted-` for manual R2 instead of silently advancing. Full DEV→QA cycle on default Opus, clean close.

---

## Session summary

- **Gap 1(b) — SHIPPED and closed.** `executable-block-continue-over-worktree-teardown-failure-2026-06-01.md` (now in `Done/`). 18-line guard at the TOP of the `if v == "continue":` branch in `_consume_verdicts`, before the final/non-final split — covers BOTH inter-step resume AND final-step continue-to-done. Predicate `any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", []))`; on trip: ERROR log + `continue-blocked-worktree-teardown` ledger + move to `halted-` + cleanup + `notify_plan_halted` + `break`. 3 regression tests. Fix commit `8b2f952` (+ QA `20cfe4d`). `_teardown_worktree`/`_create_worktree` byte-unchanged. Suite 437 passed / 5 pre-existing carry-over / zero new.
- **DEV step paused on a false-positive `scope_check`** — the plan body did not literally name `tests/test_consume_verdicts.py` as a deposit target (I over-applied the "don't name test paths from memory" rule, which governs *assertions*, not deposit-target naming). Planner verified the file held only the 3 intended tests and issued a documented override continue. Lesson promoted (see below).
- **Organic Opus A/B baseline captured** (the owed item): DEV 31 turns / ~349s / $1.38; QA 47 turns / ~283s / $1.67. DEV was *slower* in wall than last session's Sonnet clean DEV (286s) and above the Opus median (184s), but a heavier task (3 tests + lifecycle routing vs the dedup's single edit) — not like-for-like. Routing-speed thesis remains under-evidenced.

---

## State (verified at wrap)

- **bellows** — fix + QA + feedback commits on `main` (tip is this session's lifecycle/baton chore commit); tree clean after wrap commit.
- **eluvian-governance** — LESSONS updated + bellows submodule pointer bumped; pushed clean.
- **Daemon:** CEO is performing the restart this session to activate the guard (it lives in `_consume_verdicts`, so a restart is required — the running daemon executed the plan under pre-edit code). **Verify exactly one `bellows.py` via `ps aux | grep bellows.py | grep -v grep` after restart.**
- No in-flight plans, no pending verdicts. (Note: `decisions/` carries 16 stale `halted-*` files dating 05-01→05-28 — accumulated cruft, unrelated to this session; a triage-and-close pass is an open hygiene item.)

---

## THE next work item (priority)

**Gap 2 — preserve un-landed commits on stranded-cleanup** (from `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md`).

- Gap 1(b) only *halts* the cascade; it does not *recover* the orphaned commits. Gap 2 is the next cut by severity — before removing a "stranded" worktree, detect un-landed commits (worktree HEAD ahead of main) and reattach/preserve on a branch rather than destroy (findings options 2a/2b).
- Genuine git-lifecycle reasoning → default Opus.
- Same QA constraint as Gap 1(b): **code-level only**, single-pause where possible — a live multi-step integration run would trip the very bug during its own close/resume.
- Gap 1(c) (re-attempt teardown on resume) and Gap 3 (dirty-tree auto-stash) follow.

---

## Parked governance decision (carried)

- **`stop_prose` dispatch-validator vs the PLANNER_TEMPLATE `**STOP. Do NOT proceed...**` block.** Fired its WARN again this session (non-blocking; plan started normally). LIVE contradiction — CEO call between (a) remove the prose from the template vs (b) relax the validator regex. Leaning (a) by v4.57 precedent. Tracked in BACKLOG (2026-05-29).

---

## LESSON promoted this session (governance LESSONS.md)

- **Name test/deposit file paths literally in plan step bodies** — `scope_check` authorizes file modifications from the literal paths named in the step body, so a deposit target that isn't named is flagged out-of-scope. The "don't name test paths from session memory" discipline is about **assertions** (claiming a specific test exists/passes), NOT about naming a deposit target. Name the file; have the agent verify it via Rule 39 pre-edit grep.

---

## Discipline reminders for next baton

- **Read the verdict-request Gate Result JSON before EVERY verdict** (the `passed=True` log line is emitted before teardown; a `worktree_teardown` failure appends after it and is invisible there). Did this both verdicts this session — no teardown failure either time (main was clean).
- **Never leave stray uncommitted non-lifecycle files in the watched repo root** — they trip `_teardown_worktree` (b2). Lived in real-time this session: a temporary probe script was written to the repo root and removed immediately after use.
- **Code-verify BACKLOG/blueprint items before authoring against them** — the blueprint mapped cleanly to real symbols this session; verified by grep before authoring.

---

## On the horizon (other)

- Worktree regression family: Gap 2 (priority above), Gap 1(c), Gap 3.
- 16 stale `halted-*` files in `decisions/` — triage-and-close hygiene pass.
- Pre-existing test failures (4× `test_decisions.py` + `test_run_step_timeout`) — unrelated carry-over.
- QA step-log result-object anomaly (1 turn / 1.75s for a long step) — logging oddity, worth a glance.
- Bellows status UI (2026-05-21) — still unscoped.
- Other projects: anvil (first executable pending), invoice-pulse Phase B / T0.5.1 reconciliation (pending Windows query), forge, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---

## CEO actions before next session

- **Restart the daemon** to activate the Gap 1(b) guard (in progress this session). Verify single `bellows.py` process after.
- Top of next session: Gap 2 executable (priority above), or pick another horizon thread.
