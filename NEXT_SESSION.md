# Bellows — Next Session Baton

**Last session:** 2026-06-06 (three ships: anvil report-in-worktree → bellows merge-ff teardown model → bellows suite-green fixes; merge model validated by canary)
**Last session focus:** Replaced the cherry-pick teardown model at its root with `git merge`, dissolving the entire dirty-tree failure class; fixed the anvil precondition first and the two pre-existing red tests after; validated the new model end-to-end via a real multi-step canary.

---

## Session summary (in order)

1. **Plan A — anvil cycle report writes to worktree (record canonical) — SHIPPED + pushed.** `run_cycle` wrote the cycle report to canonical MAIN via hardcoded `ANVIL_ROOT`, dirtying main mid-cycle = dominant teardown-failure trigger. Split write-target (runtime root, `__file__`-derived → resolves to worktree) from recorded-path (canonical `ANVIL_ROOT`). Retired the Planner wrap-commit rule in the cycle template; added explicit report `git add` to the cycle-DEV step. anvil `main` pushed (`68269bb`).
2. **Plan B — merge-ff teardown model — SHIPPED + pushed + VALIDATED.** Replaced cherry-pick-onto-the-live-working-tree with `git merge`: `_create_worktree` makes a named branch `bellows-wt/<slug>` (was detached HEAD); `_teardown_worktree` lands via `git merge --ff-only` primary, `git merge --no-ff` fallback when main advanced (preserves worktree SHAs as merge parents — NO rebase, NO SHA rewrite), `git merge --abort` + raise `WorktreeTeardownError` on true conflict (→ Gap-1b halt). Removed: (b2) dirty-tree pre-check, `_LIFECYCLE_IGNORE_RE`, `_is_lifecycle_artifact()`, `_retry_recoverable_teardown` + caller. Added: legacy branchless-worktree descriptive raise (migration guard), sequential-invariant fail-fast in create, and 6 permanent scenario tests incl. `test_landing_tolerates_dirty_main_invariant` (the future-proofing tripwire). bellows `main` pushed.
3. **Plan C — suite-green fixes — SHIPPED + pushed.** Two pre-existing red-test root causes: (a) `decisions.py` `GOVERNANCE_ROOT = Path(__file__).parent.parent` broke under worktree execution → `load_phrases()` returned `[]` → 4 `test_decisions` reds. Fixed with a reusable `resolve_governance_root()` that walks up to the `COMPANY.md` marker (legacy `.parent.parent` fallback). (b) `test_run_step_timeout` mocked `subprocess.run` but `run_step` uses `Popen` → rewrote the test to mock `Popen` and exercise the inactivity-timeout path. Suite now **448 passed, 0 failed** (verified in-worktree). bellows `main` pushed (`4c49fc2` + this baton).

**Canary result:** Plan C drove **three consecutive clean `--ff-only` teardowns** (SA/DEV/QA), zero `worktree_teardown` failures, linear history — the merge-ff model is proven on a real multi-step plan, not just QA-green.

---

## ⚠️ CRITICAL MODEL CHANGE — teardown is now MERGE, not cherry-pick

The single most important update for next session: **the worktree teardown model changed at root this session.** Any prior baton/BACKLOG/LESSONS text describing "teardown cherry-picks commits to main" or "dirty-tree pre-check" is now STALE.

- **New model:** per-step worktree on named branch `bellows-wt/<slug>`; at each pause `_teardown_worktree` lands it onto main via `git merge --ff-only` (linear when main hasn't advanced) or `git merge --no-ff` (merge commit when it has — SHAs preserved as parents); a true content conflict aborts cleanly and raises → Gap-1b halt → manual resolution.
- **The dirty-tree failure class is GONE.** Merge tolerates a dirty non-overlapping main working tree. So the old discipline "local main must be clean before dispatch" is now a *nicety, not a hard requirement* for teardown (still good hygiene). `test_landing_tolerates_dirty_main_invariant` is the tripwire that goes red if anyone reintroduces a checkout-based teardown step.
- **Re-evaluate the worktree-teardown/resume BACKLOG family against the new model** — Gap 3 (dirty-tree auto-stash ergonomics) is almost certainly MOOT (no dirty-tree blocker exists anymore); Gap 2(b)/(c) resume mechanics changed. Do not action those entries without re-reading them against merge-ff first.

---

## State (verified at wrap)

- **anvil** — Plan A on `main`, pushed (`68269bb`), in sync with origin. Lifecycle filed to `Done/`.
- **bellows** — Plans B + C + sweep + BACKLOG + lifecycle + this baton on `main`, pushed, in sync with origin. Suite **448 passed, 0 failed** (genuinely green for the first time in a while — Rule 21 means something again).
- **Governance root (GitHub top level)** — LESSONS got 5 new entries this session (`26f92ad`); anvil + bellows submodule pointers bumped to the pushed HEADs and pushed; `git submodule status` clean (space prefix).
- **Daemon:** running on the **merge-ff model** (CEO restarted mid-session; canary validated it). No restart owed.
- No in-flight plans, no pending verdicts.

---

## Durable captures made this session (so they're not lost)

- **bellows BACKLOG (`4b35b5f`):** (1) `__file__`-relative root fragility pattern — four LATENT `BELLOWS_ROOT = Path(__file__).parent` in `bellows.py`/`planner.py`/`runner.py`/`verdict.py`; adopt `resolve_governance_root()`-style helper, **audit worktree-reachability first**, convert-with-proof. (2) 16 stale `halted-*` plans cluttering `decisions/` — sweep with per-file landed-check.
- **LESSONS (`26f92ad`):** pause_for_verdict-enum validation; gate-enforced QA steps must be unmissable; run the FULL suite during DEV/Planner review (gates don't include suite-green); `__file__`-relative roots break in worktrees; don't inherit the baton's framing — root-cause-over-bandaid.

---

## THE next work items (weigh value across projects)

High-value Bellows items are now largely done. Remaining candidates:
- **`BELLOWS_ROOT` worktree-root audit + helper adoption** (BACKLOG 2026-06-06) — the one with a (latent) correctness angle; small per file. Audit reachability before converting.
- **Stale `halted-*` sweep** (16 files) — hygiene; per-file landed-check before removing.
- **stop_prose disposition** — still a parked governance call (keep-and-suppress vs delete the warn-only check). Leaning delete; inert under bellows.
- **U+FFFD QA-report mojibake (2026-06-01)** — trivial cosmetic, free add-on.
- **Worktree teardown/resume BACKLOG family** — RE-EVALUATE against merge-ff before actioning (likely partly moot).

Honest read (carried from last baton, still true): next session's value may be higher on **another project** — anvil (real cycle now that report-in-worktree + merge-ff are in), invoice-pulse Phase B / T0.5.1 reconciliation (pending Windows query), ai-career-digest Phase 2.

---

## Discipline reminders for next baton

- **Teardown is MERGE-FF now** (see critical section above) — update your mental model; the cherry-pick framing is dead.
- **Run the FULL suite during DEV self-verify AND Planner review** — Bellows gates do NOT include suite-green; a collect-count or per-file count hides reds. Read `pytest_full.txt` tail at the terminal verdict, not just the gate table. (This session, 5 reds hid behind a green collect-count until the evidence file was read.)
- **Gate-enforced QA steps must be UNMISSABLE in the prompt** — MANDATORY callout naming the byte-exact `Rule 20 — QA Self-Check Results` / `PASSED — SELF-CHECK PASSED` banner + a final self-grep; otherwise the agent skips it and the gate fails.
- **Validate `pause_for_verdict` against the enum** (`always`/`after_step_1`/`after_qa_step`) at authoring — invalid values silently disable pausing.
- **Enumerate literal target-file paths in DEV-step scope** — `scope_check` false-trips on mandated test edits / blueprint-delegated lists not named by path.
- **Read the verdict-request Gate Result JSON before EVERY verdict** (teardown failures append after the `passed=True` log line).
- **`__file__`-relative roots break under worktree execution** — resolve via marker walk-up (`resolve_governance_root()` exists in `decisions.py` as the pattern).
- **Governance root is the GitHub top level**; LESSONS + submodule bumps live there; per-project batons at `<project>/NEXT_SESSION.md`.

---

## Parked governance decision (carried)

- **`stop_prose` check disposition** — warn-only, inert under bellows; canonical `**STOP…**` block is template-prescribed and load-bearing for manual_bootstrap. Keep-and-suppress vs delete-the-check. Leaning delete.

---
