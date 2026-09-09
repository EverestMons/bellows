# Dev Log — fetch at claim, push at merge (plan 100050)
**Date:** 2026-09-09 | **Step:** 1 (DEV) | **Branch:** `bellows-wt/100050`

## Pins re-derived (P1, P2, P3, P6)

**P1 — the merge path:**
`_teardown_worktree(project_path, wt_path, slug, plan_id=None)` at `bellows.py:2019` (pre-edit), docstring `:2020-2025`. Structure: (a) detect main (`symbolic-ref`, fallback WARN), legacy-branch check, (b) dirty-file check with stash/commit recovery text, (c) `merge --ff-only` then `merge --no-ff`, `merge --abort` + `WorktreeTeardownError` on conflict, (d) `worktree remove --force`. Callers: `:834`, `:1238`, `:1373`, `:1411`, `:2279`. Pre-edit: `grep -c '"push"\|"fetch"' bellows.py` → **0 hits** — no push, no fetch anywhere in bellows.py.

**P2 — the claim path:**
Clearance re-check `:994-1000` (failure moves to `halted-`), `plan_claim.claim_gate` `:1001` (decline discards slug from `_seen` and returns — in advisory/required mode a PASS inserts the tuyere claim), `lifecycle.mint_and_claim` `:1009`; worktree cut from HEAD at `:1661`. `project_path = str(plan_p.parents[2])` at `:898`.

**P3 — the failure shapes:**
`WorktreeTeardownError` at `:459`. On the three step-path callers (`:1241`, `:1376`, `:1414`) it becomes a `worktree_teardown` gate failure and pauses `verdict-pending-`. The park path (`:834`) routes to `halted-`. On `continue`, `_retry_recoverable_teardown` (`:2266-2296`) re-attempts only when every failure's evidence carries `worktree_teardown_dirty_tree`; else the Gap-1b guard (`:3059-3072`) rejects the continue and moves to `halted-`. Worktree and branch are left alive on teardown failure.

**P6 — tests:**
`tests/test_worktree.py` → **23 tests** (`grep -c 'def test_'`), `git_repo` fixture with `git init -b main` (no remote), identity via `git config`, one commit; `--no-ff` landing test at `:687`. `tests/test_bellows.py` → **185 tests** (`grep -c 'def test_'`), 191 collected. `pytest --collect-only -q` → **2098 tests collected** before this plan. No test names `push` or `fetch`.

---

## Failing-first (the fifteen tests red, then green)

**Pre-implementation failure:**

```
ERROR collecting tests/test_checkout_sync.py
ImportError: cannot import name '_checkout_is_current' from 'bellows'
1 error in 0.23s
```

All 15 tests failed at collection because `_checkout_is_current`, `_push_main`, and `_retry_recoverable_teardown` (import) did not exist.

**Implementation order:**
1. Added `_main_branch(project_path, slug=None) -> str` — lifted from teardown's (a) block.
2. Added `_checkout_is_current(project_path, slug=None, fetch_timeout=30) -> tuple` — in-place sentinel, HEAD check, fetch, divergence count.
3. Added `_push_main(project_path, branch) -> tuple` — subprocess wrapper, timeout-safe.
4. Modified `_teardown_worktree` — (a) block replaced by `_main_branch(project_path, slug)` call; wire point B inserted after (c), before (d), guarded by `git remote get-url origin` (origin-existence check preserves existing `git_repo`-no-remote tests).
5. Modified `run_plan` — wire point A inserted between clearance re-check and `claim_gate`.
6. Modified `_rescan` — wire point A′ inserted as first arm (stale-checkout hold self-release, at most one per rescan, oldest `held_at` first).
7. Modified `_retry_recoverable_teardown` — wire point C: allowlist extended to admit `worktree_teardown_push_rejected`.

**Post-implementation targeted run:**
```
tests/test_checkout_sync.py  15 passed
tests/test_worktree.py       23 passed
tests/test_bellows.py        185 passed
tests/test_teardown_recording.py  28 passed
251 passed in 12.90s
```

Gate test suite ran via:
```
/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest \
  tests/test_checkout_sync.py tests/test_worktree.py \
  tests/test_bellows.py tests/test_teardown_recording.py -q
```

---

## Mutation run

```
PYTHON: /Users/marklehn/Developer/bellows/.venv/bin/python
HEAD: 492f50d76c414716f021aa32180d456bae44180e
TARGET: bellows.py sha256=654b0c32fa54

MUTANT M1-behind-not-checked: KILLED — suite caught the defect
MUTANT M2-ahead-not-checked: KILLED — suite caught the defect
MUTANT M3-failed-fetch-returns-true: KILLED — suite caught the defect
MUTANT M4-push-skipped-in-teardown: KILLED — suite caught the defect
MUTANT M5-rejected-push-swallowed: KILLED — suite caught the defect
MUTANT M6-wire-a-writes-no-hold: KILLED — suite caught the defect
MUTANT M7-push-uses-force: KILLED — suite caught the defect
MUTANT M8-wire-c-push-rejected-not-retryable: KILLED — suite caught the defect
MUTANT M9-head-check-removed: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: bellows.py sha256=654b0c32fa54

MUTATION: 9 killed, 0 survived, 0 error
```

Full output in `knowledge/mutants/fetch-at-claim-push-at-merge.run.txt`.

---

## Cost

**`_checkout_is_current` timing on local bare repo fixture (three runs, median):**
- Run 1: 36.6 ms
- Run 2: 36.9 ms
- Run 3: 36.7 ms
- **Median: 36.7 ms** (fetch against `file://` local bare repo)

Against GitHub (`git@github.com:EverestMons/bellows.git`): the fetch is a full network round-trip. Typical SSH-to-GitHub fetch for a single branch ref is 200–800 ms depending on latency and SSH handshake. This cost is incurred once per claim attempt and once per held re-check (every ~32 s while a plan is held). The `fetch_timeout=30 s` (claim) / `fetch_timeout=10 s` (rescan) bounds the stall; an offline shop holds every claim, fail-closed (C10).
