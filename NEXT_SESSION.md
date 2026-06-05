# Bellows — Next Session Baton

**Last session:** 2026-06-05 (scope_check directory-mention FP; follows the #7 `_seen` session of 2026-06-04)
**Last session focus:** Shipped the directory-mention half of the scope_check false-positive pair (was Open 2026-05-28 session 16) — one depth-guarded trailing-slash ancestor-directory clause in `_gate_scope_check`, so child files written under a Deposits-block-named directory pass scope_check without an explicit per-filename mention. Full DEV→QA on default Opus, clean close, no R2.

---

## Session summary

- **scope_check directory-mention FP — SHIPPED and closed.** `executable-scope-check-dir-mention-2026-06-04.md` (now in `Done/`). One additive clause in `_gate_scope_check` (`gates.py`), inserted after `fpath in step_text or basename in step_text` and before `out_of_scope.append(fpath)`: walk the changed file's OWN ancestor dirs (`os.path.dirname`); accept if an ancestor with a trailing slash and >=2 segments (`parent.count("/") >= 1`) appears in the step text. Depth guard blocks shallow `web/`-style blanket authorization; ancestors derived from `fpath` so only a genuine parent matches. Purely additive — only widens scope, never narrows; four pre-existing clauses byte-unchanged. 4 tests in `test_gates.py` (2 positive, 2 NEGATIVE proving teeth). Commits `ee2bb4c` (fix) + `a75e0b6` (QA) + `b470a8d` (feedback). Zero new failures.
- **Scope decision (CEO this session):** directory-mention half ONLY. The sibling **2026-05-29 blueprint-delegation FP** (same root cause) was excluded as the higher-risk regex shape and is now the SOLE remaining scope_check FP — still Open.
- **No diagnostic** — direct code read fully established the matcher baseline (Rule 10 bar met, as #7's did); the entry's "appears to require per-filename mention" hypothesis confirmed verbatim against `gates.py`.
- **Clean dogfood** — both verdicts clean (read the full Gate Result JSON each time; `failures: []`). Only the known `stop_prose` WARN at claim. No R2, no false-positive gate trips.
- **Organic Opus A/B baseline:** DEV 33 turns / ~276s / $0.93; QA 39 turns / ~246s / $1.37 (`logs/20260604-175500-step.json`, `logs/20260605-072930-step.json`).

---

## State (verified at wrap)

- **bellows** — fix+QA+feedback + this wrap on `main`, pushed (`2fbde94`); tree clean after.
- **Governance repo (= GitHub top-level repo, NOT an `eluvian-governance/` subdir)** — bellows submodule pointer bumped + pushed (`f09e249`); `git submodule status` shows clean space-prefix at `2fbde94`. LESSONS unchanged this session (see observation below — no durable lesson filed on n=1).
- **Daemon:** NO restart owed. The overnight restart already loaded `gates.py @ ee2bb4c`, so the directory-mention clause is already live. Verify exactly one `bellows.py` via `ps aux | grep [b]ellows.py`; confirm heartbeat fingerprint reads `gates.py @ git:ee2bb4c` or later.
- No in-flight plans, no pending verdicts. (`decisions/` still carries the stale `halted-*` cruft dating 05-01 — triage-and-close hygiene item, unchanged.)

---

## Observation to verify next session (NOT a filed lesson)

- **This dispatch executed on `main` with no live worktree at the Step-1 pause** (`git worktree list` showed only `main`; DEV/QA commits landed directly on `main`). That contradicts the worktree-per-step model the memory snapshot and prior batons assume — it made the plan's own "runs under pre-edit gates.py / restart owed after ship" reasoning stale (the fix was live before the plan even finished). n=1; could be "this config never uses worktrees" OR "worktree torn down between steps." Worth a deliberate check next session before authoring any plan whose correctness depends on worktree isolation. Did NOT file a LESSONS entry on one observation.

---

## THE next work item (decision, not yet authored)

**Pick the next cut on value-per-effort across ALL Open items.**

- **scope_check blueprint-delegation FP (2026-05-29)** — now the sole remaining scope_check FP. Higher-value-if-tackled but the flagged 4a regex-fragility risk applies: fix (a) follow blueprint reference + view-and-extract; fix (b) inline `**Target Files:**` block in PLANNER_TEMPLATE (trivial, non-load-bearing). Frequent on SA->DEV->QA blueprint executables.
- **stop_prose detector FP family (3 sources, low sev)** — overlaps the parked governance decision below; needs a CEO call regardless. Leaning (a) remove the prose from the template.
- **Worktree Gap 2(b)/(c) functional resume recovery** — in-family, higher-value if staying; code-level QA only, fiddly test surface. (Gap 3 remains DEFERRED — do not resurface; reasoning in the worktree-family BACKLOG "Status 2026-06-04" note.)
- **U+FFFD QA-report mojibake (2026-06-01)** — cosmetic one-char fix, trivial; fold in as a free add-on, not a target.

---

## Parked governance decision (carried)

- **`stop_prose` dispatch-validator vs the PLANNER_TEMPLATE `**STOP. Do NOT proceed...**` block.** Fired its WARN again this session (non-blocking; plan started normally). LIVE contradiction — CEO call between (a) remove the prose from the template vs (b) relax the validator regex. Leaning (a). Tracked in BACKLOG (2026-05-29; note the third source — sentence-final "stop." in QA prose — which (b)'s `Do NOT proceed to Step` anchor would NOT cover).

---

## Discipline reminders for next baton

- **Code-verify BACKLOG items before authoring.** This session's baseline came from a direct `gates.py` read, not the entry text; that's also what lets you skip the diagnostic (Rule 10) when the read is conclusive.
- **Read the verdict-request Gate Result JSON before EVERY verdict** (`passed=True` log line precedes any teardown failure; on-main dispatch had no teardown, but keep the habit).
- **Self-trip avoidance on scope_check/gate-fix plans:** enumerate every evidence basename in the QA `required_evidence_files` list so the QA evidence dir passes the PRE-edit gate; prove the new gate behavior with unit tests, not the plan's own execution.
- **Keep `main` clean at pauses.** Used `_staging_*` files at repo root for atomic deposit + verdict moves; each removed by its `mv`.
- **Governance root is the GitHub top level** (`/Users/marklehn/Developer/GitHub`); `LESSONS.md` is there; the submodule bump runs there. Per-project batons live at `<project>/NEXT_SESSION.md`.

---

## On the horizon (other)

- scope_check blueprint-delegation FP (remaining half), stop_prose FP family (+ parked governance call), worktree Gap 2(b)/(c) (Gap 3 deferred), U+FFFD mojibake one-char fix.
- Stale `halted-*` files in `decisions/` — triage-and-close hygiene pass.
- Pre-existing test carry-over (`test_decisions.py` env-variant + `test_run_step_timeout`) — unrelated; varies by environment.
- Bellows status UI (2026-05-21) — still unscoped.
- Other projects: anvil (first executable pending), invoice-pulse Phase B / T0.5.1 reconciliation (pending Windows query), forge, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---
