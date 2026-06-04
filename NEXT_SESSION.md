# Bellows — Next Session Baton

**Last session:** 2026-06-04 (#7 `_seen` re-deposit; second 2026-06-04 session, follows the Gap 1c session earlier the same day)
**Last session focus:** Shipped the `_seen` re-deposit invalidation fix (BACKLOG #7) — mirrored the `on_modified` `_seen`-invalidation into `on_created`/`on_moved` via one helper, so a follow-on plan deposited at a stale slug after a Planner-direct Done/ move re-dispatches without a daemon restart. Full DEV→QA on default Opus, clean close, no R2.

---

## Session summary

- **#7 — SHIPPED and closed (RE-FRAMED).** `executable-seen-invalidate-on-created-moved-2026-06-04.md` (now in `Done/`). The open entry's PRIMARY proposed fix (clear `_seen` at the Done/ transition) was already shipped for daemon-driven closes (`bellows.py:699`, `:1457`) and irrelevant to the real repro — a Planner-direct `Filesystem:move_file` close the daemon never observes. Shipped the entry's ALTERNATIVE, refined: one `PlanHandler._invalidate_seen_on_redeposit(self, path)` helper called from `on_created`/`on_modified`/`on_moved`; lifecycle-prefix guard preserved verbatim; `_handle` + 30s rescan byte-unchanged (invalidation lives ONLY in the watcher callbacks, never in `_handle`, which rescan also calls). 4 tests in `test_bellows.py` mirroring the existing `on_modified` pair (L3267/L3295). Commits `d5fd9c9` (fix) + `6411de2` (QA) + `b9baf75` (feedback). Suite 444→448 passed / 5 carry-over / zero new.
- **Clean dogfood** — both verdicts clean (read the Gate Result JSON each time; no teardown failure, `main` clean). Only the known `stop_prose` WARN at claim. No R2, no false-positive gate trips.
- **Organic Opus A/B baseline:** DEV 30 turns / ~197s / $0.82; QA 48 turns / ~304s / $1.62 (`logs/20260604-140708-step.json`, `logs/20260604-170632-step.json`).
- **Gap 3 DEFERRED** (CEO next-cut decision this session) — see "THE next work item."

---

## State (verified at wrap)

- **bellows** — #7 fix+QA+feedback on `main`; tip is this session's lifecycle/BACKLOG/baton wrap commit; tree clean after.
- **Governance repo (= GitHub top-level repo, NOT an `eluvian-governance/` subdir — memory was stale on this)** — bellows submodule pointer bumped + pushed. LESSONS unchanged this session (the #7 lesson already exists in the "BACKLOG framing lags code" family; no new entry needed).
- **Daemon:** CEO restarted this session to activate the create/move invalidation (it lives in the watcher callbacks; the running daemon executed the plan under pre-edit code). Verify exactly one `bellows.py` via `ps aux | grep [b]ellows.py`.
- No in-flight plans, no pending verdicts. (`decisions/` still carries the stale `halted-*` cruft dating 05-01→05-28 — triage-and-close hygiene item, unchanged.)

---

## THE next work item (decision, not yet authored)

**Pick the next cut on value-per-effort across ALL Open items — do NOT default to "finishing the worktree family."**

- **Gap 3 is DEFERRED.** After 1(b) halt-safe + 2(a) commit-preserve + 1(c) auto-recover-common-case, the worktree family holds no remaining correctness or data-safety gap; both leftover cuts (Gap 3, Gap 2(b)/(c)) are friction-reduction. Gap 3's only trigger-removing shape (3(a) auto-stash) injects an unstash-conflict data-risk into the just-hardened teardown cherry-pick path — a strict regression on the protected dimension. Full reasoning in the worktree-family BACKLOG entry, "Status 2026-06-04" note.
- **If staying in-family:** Gap 2(b)/(c) functional resume recovery is the higher-value target (restart-during-pause regresses the next step's base tree; gates catch it + 2(a) preserves the commits, so it's recovery-friction, not silent loss). Code-level QA only; fiddly test surface (a live multi-step run would trip the bug).
- **Other live Open candidates (value-per-effort):** scope_check FP pair (2026-05-29 blueprint-delegation + 2026-05-28 directory-mention — same family, batchable, frequent); stop_prose detector FP family (3 sources, low sev — overlaps the parked governance decision below); the cosmetic U+FFFD QA-report mojibake one-char fix (2026-06-01).

---

## Parked governance decision (carried)

- **`stop_prose` dispatch-validator vs the PLANNER_TEMPLATE `**STOP. Do NOT proceed...**` block.** Fired its WARN again this session (non-blocking; plan started normally). LIVE contradiction — CEO call between (a) remove the prose from the template vs (b) relax the validator regex. Leaning (a). Tracked in BACKLOG (2026-05-29).

---

## Discipline reminders for next baton

- **Code-verify BACKLOG/blueprint items before authoring — paid off hard this session.** #7's PRIMARY proposed fix was already shipped; only reading `bellows.py` (not trusting the entry text) caught it, and the real fix site was the entry's *alternative*. (LESSONS family 466/489/493; 2026-06-02 freshness-axis.)
- **Read the verdict-request Gate Result JSON before EVERY verdict** (the `passed=True` log line precedes teardown; a `worktree_teardown` failure appends after it and is invisible there). Did so both verdicts; clean.
- **Keep `main` clean at pauses** — stray non-lifecycle files trip `_teardown_worktree` (b2). Used `_staging_*` files at repo root for the atomic deposit + verdict moves; each removed by its `mv`.
- **Governance root is the GitHub top level** (`/Users/marklehn/Developer/GitHub`); `LESSONS.md` is there; the submodule bump runs there. Per-project batons live at `<project>/NEXT_SESSION.md`.

---

## On the horizon (other)

- Worktree family: Gap 2(b)/(c) (in-family next option), Gap 3 (deferred). `_seen` re-deposit now closed.
- scope_check FP pair, stop_prose FP family, U+FFFD mojibake one-char fix.
- 16 stale `halted-*` files in `decisions/` — triage-and-close hygiene pass.
- Pre-existing test failures (4× `test_decisions.py` + `test_run_step_timeout`) — unrelated carry-over.
- Bellows status UI (2026-05-21) — still unscoped.
- Other projects: anvil (first executable pending), invoice-pulse Phase B / T0.5.1 reconciliation (pending Windows query), forge, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---

## CEO actions before next session

- Daemon restart — DONE this session. Verify a single `bellows.py` process if not already.
- Top of next session: decide the next cut (see "THE next work item") and authorize.
