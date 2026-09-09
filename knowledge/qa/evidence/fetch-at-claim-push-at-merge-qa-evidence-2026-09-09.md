# QA Receipt — fetch-at-claim-push-at-merge — 2026-09-09

**Plan:** executable-100050 (Step 2 — QA)
**Branch:** bellows-wt/100050
**Base commit:** e94efda (qa(step-files-record): full suite green + live-db read-only probe [100049])
**DEV commit 1:** 492f50d76c414716f021aa32180d456bae44180e — feat(checkout-sync): fetch at claim, push at merge — three helpers, three wire points (thread 231) [100050]
**DEV commit 2:** 8d4bb57daee41a4701e6e7783a9484e135bdb72c — chore(dev-log): mutation run + dev-log for fetch-at-claim-push-at-merge (thread 231) [100050]

---

## Item 1 — Full Suite

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/fetch-at-claim-push-at-merge-suite-2026-09-09.txt 2>&1`

Result: **2112 passed, 1 skipped** — exit 0.

Evidence file: `knowledge/qa/evidence/fetch-at-claim-push-at-merge-suite-2026-09-09.txt`

## Item 2 — `_checkout_is_current` on Live Canonical Checkout (Read-Only)

Target: `/Users/marklehn/Developer/bellows` (not the worktree).

**FETCH_HEAD mtime before:** 1788966705
**FETCH_HEAD mtime after:** 1788966835 — mtime changed, fetch was performed.
**main SHA before:** 8d4bb57daee41a4701e6e7783a9484e135bdb72c
**main SHA after:** 8d4bb57daee41a4701e6e7783a9484e135bdb72c — **UNCHANGED**
**`git status --porcelain`:** identical before and after — **working tree UNCHANGED**

Result tuple:

```
(False, 'stale checkout: main is 0 behind / 2 ahead of origin/main — pull (behind) or push (ahead) on this checkout; the hold releases itself on the next poll that finds it current')
```

Expected: the live canonical checkout is 2 ahead of `origin/main` (the DEV commits of this plan — 492f50d and 8d4bb57 — were merged by the daemon into `main` but not yet pushed; the daemon restart and first-claim canary will push them). `_push_main` was NOT called.

## Item 3 — CEO-Facing Refusal Texts (from tmp synced_repo)

**Behind (1 behind / 0 ahead):**
```
(False, 'stale checkout: main is 1 behind / 0 ahead of origin/main — pull (behind) or push (ahead) on this checkout; the hold releases itself on the next poll that finds it current')
```

**Ahead (0 behind / 1 ahead):**
```
(False, 'stale checkout: main is 0 behind / 1 ahead of origin/main — pull (behind) or push (ahead) on this checkout; the hold releases itself on the next poll that finds it current')
```

**Diverged (1 behind / 1 ahead):**
```
(False, 'stale checkout: main is 1 behind / 1 ahead of origin/main — pull (behind) or push (ahead) on this checkout; the hold releases itself on the next poll that finds it current')
```

**Fetch failed (no remote):**
```
(False, "fetch failed: fatal: 'origin' does not appear to be a git repository")
```

**HEAD elsewhere (on branch `side`, not `main`):**
```
(False, 'stale checkout: HEAD is on side, not main')
```

**Hold sidecar JSON (wire point A writes — example with behind detail):**
```json
{
  "hold_reason": "stale-checkout",
  "detail": "stale checkout: main is 1 behind / 0 ahead of origin/main — pull (behind) or push (ahead) on this checkout; the hold releases itself on the next poll that finds it current",
  "held_at": "2026-09-09T10:00:00Z"
}
```

**Test 8 halt text (`WorktreeTeardownError`):**
```
worktree_teardown_push_rejected: push rejected — push of main after merging bellows-wt/test-plan-slug for slug test-plan-slug was refused: To /var/folders/…/origin.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '/var/folders/…/origin.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details. — someone landed on origin/main outside a plan; on this checkout: git fetch origin && git merge origin/main (resolve by hand), then re-issue continue — the retry merges (a no-op) and pushes again
```

## Item 4 — Production Writes

None outside the two evidence files committed in this step. No push was made in QA. No fetch was made except the single read-only `_checkout_is_current` call against the live canonical checkout (Item 2). The daemon restart, the P10 canary, and MACHINE_SETUP v1.5 are the CEO's acts at close.

---

## Verification

| # | Check | Result | Status |
|---|-------|--------|--------|
| V1 | `git diff --numstat e94efda..8d4bb57` — exactly 5 files | `171+14 bellows.py`, `93+0 dev-log`, `68+0 mutants-json`, `17+0 mutants-run`, `581+0 test_checkout_sync.py` | ✅ |
| V2 | run file `HEAD:` equals `git log -1 --format=%H -- knowledge/mutants/fetch-at-claim-push-at-merge.json` | both `492f50d76c414716f021aa32180d456bae44180e` | ✅ |
| V3 | `git diff e94efda..8d4bb57 -- tests/test_worktree.py tests/test_bellows.py tests/test_teardown_recording.py` → empty | empty | ✅ |
| V4 | `git diff -U0 e94efda..8d4bb57 -- bellows.py \| grep '^+' \| grep -c '--force\|rebase\|reset'` → 0 | 0 | ✅ |
| V5 | `git rev-parse --show-toplevel` | `/Users/marklehn/Developer/bellows/.bellows-worktrees/100050` | ✅ |
| V6 | `git reflog -n 6` — 0 amend entries | no amend entries in reflog | ✅ |
| V7 | Four dev-log headings present | `## Pins re-derived (P1, P2, P3, P6)`, `## Failing-first (the fifteen tests red, then green)`, `## Mutation run`, `## Cost` | ✅ |
| V8 | Item 1: full suite result | 2112 passed, exit 0; 1 test conditionally deferred (test_gate_watcher.py:336 — worktree lifecycle.db has no plans table) | ✅ |
| V9 | Item 2: live canonical checkout read-only probe | tuple returned, fetch performed (FETCH_HEAD mtime changed), main SHA unchanged, working tree unchanged, `_push_main` not called | ✅ |
| V10 | Item 3: CEO-facing texts produced verbatim | all six cases (behind, ahead, diverged, fetch-failed, HEAD-elsewhere, hold-sidecar, halt-text) captured above | ✅ |
| V11 | Item 4: production writes | none outside evidence files; no push; no fetch except Item 2 read-only | ✅ |
| V12 | Full suite passes (`tests/test_checkout_sync.py` — 15 tests, `tests/test_worktree.py`, `tests/test_bellows.py`, `tests/test_teardown_recording.py`) | 2112 passed, exit 0; see suite evidence file for full count | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100050/knowledge/qa/evidence/
Files verified: 2
