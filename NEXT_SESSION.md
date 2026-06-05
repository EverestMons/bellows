# Bellows — Next Session Baton

**Last session:** 2026-06-05 (two ships: scope_check directory-mention FP, then `_teardown_worktree` (b) silent-loss fix)
**Last session focus:** Closed the last open data-safety gap in the worktree teardown/resume family — `_teardown_worktree` step (b) now raises on a `git log` failure instead of swallowing it into an empty commit list. Earlier the same session: shipped the scope_check directory-mention FP, confirmed Gap 2(b)/(c) is already closed (diagnostic), and found the "template bundle" moot.

---

## Session summary (in order)

1. **scope_check directory-mention FP — SHIPPED.** Depth-guarded trailing-slash ancestor clause in `_gate_scope_check`. (Closed 2026-06-05.) Sibling blueprint-delegation FP excluded.
2. **Gap 2(b)/(c) — confirmed CLOSED by Planner-direct diagnostic.** `_teardown_worktree` lands-or-raises; the continue-advance is gated on no-uncleared-teardown-failure (1b) + the 1c retry; resume worktree is created from a HEAD that holds the prior commit. The 2026-05-30 silent-regression repro is the path 1b/1c now cover. Residual 2(b)/(c) = auto-resume-from-branch = friction + divergence-risk → DEFERRED.
3. **`_teardown_worktree` (b) silent-loss — FILED then SHIPPED.** The diagnostic surfaced one real uncovered hole: step (b) swallowed a `git log` failure into `commit_shas = []` → silent commit loss, no recorded failure. Fix (a): raise `WorktreeTeardownError` on exception OR non-zero rc; legitimate-empty (rc 0, no commits) still proceeds. 3 tests incl. the empty-case negative; 4 existing teardown tests green. (Closed 2026-06-05.)
4. **"Template bundle" found MOOT.** The Target-Files convention already exists as **Rule 14(b)** in PLANNER_TEMPLATE v4.59 — the blueprint-delegation FP recurrence was a discipline lapse, not a missing rule. The STOP-block removal is the wrong shape (the block is load-bearing for manual_bootstrap; stop_prose is warn-only and inert under bellows). No template edit made.

---

## State (verified at wrap)

- **bellows** — both ships' fix+QA+feedback + lifecycle/BACKLOG/baton wraps on `main`, pushed; tree clean after.
- **Governance repo (= GitHub top-level, NOT an `eluvian-governance/` subdir)** — bellows submodule pointer bumped + pushed; `git submodule status` clean (space prefix). LESSONS unchanged (no new durable lesson — the misframings were caught by verify-before-fix, the existing discipline).
- **Daemon:** ⚠️ **RESTART OWED.** The teardown-(b) fix is in `_teardown_worktree`, loaded at daemon startup; the running daemon still holds the pre-edit teardown. Restart to activate, then confirm the heartbeat fingerprint shows the new `bellows.py` per-file commit. (The scope_check dir-mention fix from earlier today is already live — it shipped before the overnight restart loaded `gates.py @ ee2bb4c`.)
- No in-flight plans, no pending verdicts. (`decisions/` still carries the stale `halted-*` cruft from 05-01 — hygiene item.)

---

## THE next work item — note the well has mostly run dry on high-value cuts

This session's verification established that the high-frequency / correctness items are largely done:
- **scope_check dir-mention** → shipped. **teardown-(b) silent-loss** → shipped (last data-safety gap). **Gap 2(b)/(c)** → target closed. **blueprint-delegation** → already covered by Rule 14(b) (discipline, not a code fix).

Remaining Open candidates are LOW value — weigh carefully before dispatching:
- **stop_prose FP family** — warn-only, inert under bellows mode (the daemon owns the pause). The real decision is governance: keep-and-suppress vs **delete the vestigial check** in `validators.py:check_stop_prose`. Leaning delete — it prevents no failure under bellows and only produces claim-time noise. CEO call; low value either way.
- **U+FFFD QA-report mojibake (2026-06-01)** — trivial one-char cosmetic fix to a closed plan's QA report; near-zero value, fine as a free add-on.
- **Worktree Gap 2(b)/(c) auto-resume + Gap 3 auto-stash** — both DEFERRED (friction-reduction with divergence/unstash data-risk; no correctness gap remains).
- **Deferred/low Open items** (deposits parenthetical, verdict-filename prefix tolerance, `_extract_step_text` case-sensitivity, Bellows status UI, parallel-teardown conflicts, dirty-PROJECT_STATUS teardown) — each gated on a second occurrence or a separate planning session.

Honest read: consider whether the next session's value is higher on **another project** (anvil first executable, invoice-pulse Phase B / T0.5.1, ai-career-digest Phase 2) than on the remaining Bellows backlog.

---

## Parked governance decision (carried)

- **`stop_prose` check disposition** — now sharper after this session's read: it's warn-only and inert under bellows; the canonical `**STOP…**` block is template-prescribed and load-bearing for manual_bootstrap. Decision is keep-and-suppress-canonical vs delete-the-check. Leaning delete.

---

## Discipline reminders for next baton

- **Verify-before-fix paid off three times this session.** 2(b)/(c) target already closed; blueprint-delegation already covered by Rule 14(b); template-bundle STOP-removal wrong shape. Read the live code/template before authoring against a >7-day BACKLOG entry.
- **Read the verdict-request Gate Result JSON before EVERY verdict** (teardown failures append after the `passed=True` log line).
- **Worktree model IS per-step with teardown-cherry-pick-to-main at each pause** (confirmed this session via author<committer skew). `git worktree list` looks empty at a pause because teardown already ran; that's normal, not "no worktree."
- **Self-trip avoidance on gate/teardown-fix plans:** enumerate every evidence basename in QA `required_evidence_files`; prove new behavior with unit tests, not the plan's own execution; this plan's own teardown runs under pre-edit code (restart owed after ship).
- **Governance root is the GitHub top level**; LESSONS + submodule bump live there; per-project batons at `<project>/NEXT_SESSION.md`.

---

## On the horizon (other)

- stop_prose disposition (governance), U+FFFD cosmetic, deferred worktree friction (2b/c, Gap 3).
- Stale `halted-*` files in `decisions/` — triage-and-close hygiene pass.
- Pre-existing test carry-over (`test_decisions.py` env-variant + `test_run_step_timeout`).
- Bellows status UI (2026-05-21) — unscoped.
- Other projects: anvil (first executable pending), invoice-pulse Phase B / T0.5.1 reconciliation (pending Windows query), forge, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest Phase 2.

---
