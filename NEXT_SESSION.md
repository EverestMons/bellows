# Bellows — Next Session Baton

**Last session:** 2026-05-31 (follows the 2026-05-29 session)
**Last session focus:** Shipped the no-match verdict WARN dedup (BACKLOG 2026-05-21) via the first Opus→Sonnet routing A/B; discovered, diagnosed, and documented the worktree teardown→resume regression; full closeout of both repos.

---

## Session summary

A mechanical BACKLOG fix run as a deliberate model-routing experiment surfaced a high-severity lifecycle bug. Both got handled.

- **No-match dedup — SHIPPED and LIVE.** `executable-no-match-verdict-warning-dedup-2026-05-31.md` (now in `Done/`). Added module-level `_warned_no_match: set[str]` in `_consume_verdicts`; logs the no-match WARN once per `resolved/` file, `.discard()` at both processed-move sites clears on leave. 2 regression tests. Commits `e38b958` (fix) + `a004270`/`7edb969`/`3663e1a`. **Daemon restarted 2026-05-31 → the dedup is now active** (it lives in `_consume_verdicts`, so the restart was required).
- **A/B result (Opus→Sonnet routing).** Ran DEV+QA on `claude-sonnet-4-6` (set via the plan `Model:` header — per-plan, not per-step). Sonnet DEV ran ABOVE the Opus all-step median on both attempts (37 turns / 286s clean; 41 turns / 348s first attempt vs Opus median 23/184s). **Leans against the routing-speed thesis** from the speed-research doc (now filed at `knowledge/research/bellows-speed-research-2026-05-29.md`). Caveat: compared against the all-step median, NOT like-for-like. **The controlled Opus baseline is still owed** — CEO decision: collect it ORGANICALLY from the next mechanical item run on the default (Opus) model, no main revert/churn.
- **Worktree teardown→resume regression — DIAGNOSED + DOCUMENTED.** The dedup plan's first attempt cascaded: a stray untracked file on `main` tripped `_teardown_worktree` (b2) dirty-tree pre-check at the step-1 pause, the failure was invisible in the `passed=True` log line, a continue was issued over it, and `_create_worktree`'s stranded-cleanup orphaned step-1's commits at the step-2 boundary. Full mechanism + Opus-class fix blueprint at **`knowledge/research/worktree-teardown-resume-regression-2026-05-31.md`** (commit `7a6d8e9`). Recovered via a clean re-run (cleared the stray file first).

---

## State (verified at wrap)

- **bellows** main HEAD `6223780` — pushed clean, tree clean.
- **eluvian-governance** HEAD `13df358` — LESSONS updated + bellows submodule pointer bumped to `6223780`, pushed clean, submodule prefix clean (space).
- **Daemon:** RESTARTED 2026-05-31, **exactly one process** (PID 29829 at wrap), dedup live. Verify `ps aux | grep bellows.py | grep -v grep` before any fresh start.
- No in-flight plans, no pending verdicts, no halted plans.

---

## THE next work item (priority)

**Author the Opus-class worktree teardown→resume fix executable from the findings blueprint** (`knowledge/research/worktree-teardown-resume-regression-2026-05-31.md`).

- **Ship gap 1 first:** block a continue verdict when the prior step's gate result carries an uncleared `worktree_teardown*` failure (cheapest, highest safety — stops the silent skip). Gaps 2 (stranded-cleanup orphans un-landed commits) and 3 (dirty-tree ergonomics) sequenced after.
- **QA must be code-level only.** A live multi-step integration smoke test inside the fix plan would trip the very bug during its own close/resume. Keep the fix plan single-pause where possible.
- This is genuine reasoning work → default Opus model (NOT a Sonnet-route candidate).

**Also owed:** capture the **organic Opus baseline** — when the next mechanical item runs on the default model, record turns/wall to complete the A/B comparison against this session's Sonnet numbers.

---

## BACKLOG changes this session

- **Closed:** No-match verdict WARN dedup (SHIPPED). Orphan-guard wrong-step renormalization (RETIRED — the targeted site does not exist in current code; removed by `c2aeef4`; entry was authored from a mental model, not the code).
- **New (top of Open):** Worktree teardown→resume regression — consolidated entry that unifies the 2026-05-22 dirty-tree-teardown item and the 2026-05-30 resume-recreation item as ONE failure family, cross-links the findings doc, and **corrects the 2026-05-30 "restart-only" framing (it fires on a normal continue-resume).**
- **Parked governance decision (existing 2026-05-29 item):** `stop_prose` dispatch-validator matches the PLANNER_TEMPLATE-prescribed `**STOP. Do NOT proceed...**` block (~line 368). This is a LIVE contradiction, not a mechanical fix — CEO call between (a) remove the prose from the template vs (b) relax the validator regex. Leaning (a) by v4.57 precedent.

---

## LESSONS promoted this session (governance LESSONS.md, top)

1. **Read the verdict-request Gate Result JSON before EVERY verdict.** The `gates step N: passed=True` log line is emitted BEFORE teardown; a `worktree_teardown*` failure appends after it and is invisible in the log — read the gate JSON + Pause Reason Code, not just deposit substance. A `gate_failure` carrying `worktree_teardown*` → R2 recovery, never a plain continue.
2. **Never leave stray uncommitted non-lifecycle files in a watched repo root.** They fail `_teardown_worktree` (b2) on EVERY plan's teardown until committed/removed. Commit knowledge deposits (e.g. findings docs) before dispatching the next plan.

---

## Discipline reminders for next baton

- **Code-verify BACKLOG items before authoring against them.** Two-for-two this session, Open items did not match their own description (orphan-guard phantom; stop_prose-as-governance-contradiction). Read the current code first.
- **The dedup fix is live but unproven in the wild** — no-match WARN should now log once per stuck file. If a future stuck verdict floods again, suspect a restart cleared `_warned_no_match` legitimately, not a regression.
- **Stale-process check** still applies: confirm exactly one `bellows.py` via `ps aux | grep bellows.py | grep -v grep` before a fresh daemon start.

---

## On the horizon (other)

- Pre-existing test failures (4× `test_decisions.py` TestLoadPhrases/TestExtractDecisionBlocks + `test_run_step_timeout`) — unrelated carry-over, separate hygiene item.
- QA step-log result-object anomaly (1 turn / 1.75s for a ~426s step) — logging oddity, worth a glance.
- Bellows status UI (2026-05-21) — still unscoped.
- Other projects: anvil (first executable pending), invoice-pulse Phase B (pending Windows query results), forge, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---

## CEO actions before next session

- **None required.** Daemon restarted and running (dedup live), both repos pushed clean, no in-flight plans or pending verdicts.
- Top of next session: the worktree fix executable (priority above), or pick another horizon thread.
- **PROJECT_STATUS.md not updated this session** — the standing "maintain vs retire" decision is still open. Not blocking.
