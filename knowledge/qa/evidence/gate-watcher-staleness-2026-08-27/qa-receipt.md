# QA Receipt — gate-watcher-staleness (exec-573)

**Date:** 2026-08-27
**Plan:** executable-573 (gate-watcher-staleness: resolved-verdict check replaces the arm-time snapshot)
**DEV commit:** 99e163d `[573] gate-watcher-staleness: resolved-verdict check replaces the arm-time snapshot; state-space suite`
**Toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/573`

## DEV commit numstat (3 files)

```
 knowledge/dev-logs/gate-watcher-staleness-dev-2026-08-27.md       |  51 +++++
 tests/test_gate_watcher.py                                        | 215 ++++++++++++++-------
 tools/gate_watcher.py                                             |  78 ++++----
 3 files changed, 231 insertions(+), 113 deletions(-)
```

## Reflog (0 amends)

```
99e163d HEAD@{0}: reset: moving to HEAD
99e163d HEAD@{1}:
```

No amend entries in reflog — all commits are distinct.

## Item 1 — Full suite

**Result:** 1611 passed, 1 skipped, 0 failed (52.94s)

**Count derivation:**
- B5 baseline: 1582 (exec-570 full suite) + 572's 8 (TestArmTimeSnapshot) = 1590 in tree
- This plan deletes 572's 8 -> 1582
- This plan adds TestPauseStateSpace: 6 named tests + 24 parametrized cells = 30
- Expected total: 1582 + 30 = 1612
- Observed: 1611 passed + 1 skipped = 1612

The 1 skipped is `test_reachable_states_match_the_classification_dimension` — the drift guard, which correctly skips in the worktree (no live lifecycle.db). It is explicitly forced to RUN in Probe 6 below.

**QA-discovered fix:** The drift guard test's skip logic originally only checked `os.path.exists(db_path)`. When the full suite runs, another test creates an empty `lifecycle.db` at the worktree root, causing the drift guard to find the file but fail on `no such table: plans` instead of skipping. Fixed by catching `sqlite3.OperationalError` on both connect and query, skipping in both cases. The fix is +7/-1 lines in `tests/test_gate_watcher.py`.

**Evidence:** `pytest_full.txt`

## Item 2 — 572 regression probes

All probes against the LIVE tool (`tools/gate_watcher.py`) with plan id 573.

### Probe 1 — Baseline (NOT a discriminating probe)

Pending present, resolved dir empty. `--status` reports `awaiting-verdict id=573 pending=verdict-request-573-step-1.md`, exit 0.

This output is the SAME before and after this plan. 572's guard lived in the poll loop (`judge_watch_line`), never in `read_state`, so `--status` was never affected by it. This is a control showing the unresolved-pause path works, not the 572 regression killed.

### Probe 1b — THE 572 REGRESSION (discriminating)

Same world (pending present, resolved dir empty), run as a 1-minute loop with 5s interval. Under 572's shipped loop, this world produced `armed over pre-existing ...` and then silence — the pause was missed.

Result:
- Log shows `WATCH: awaiting-verdict id=573 pending=verdict-request-573-step-1.md` at arm time
- Pause-line count (`/usr/bin/grep -cF "pending=verdict-request-573-step-1.md"`): **1** (>=1)
- Armed-over count (`/usr/bin/grep -cF "armed over pre-existing"`): **0**
- Exit: 3 (timeout, expected)

The regression is killed: the unresolved pause is reported at first poll.

### Probe 2 — Stale, verdict- form

`verdict-573-step-1.md` in resolved dir. Result: `WATCH: in_progress id=573` — NOT awaiting-verdict. Exit 0.

### Probe 3 — Stale, processed-verdict- form

`processed-verdict-573-step-1.md` in resolved dir. Result: `WATCH: in_progress id=573` — NOT awaiting-verdict. Exit 0.

Both forms counted (B1 verified).

### Probe 4 — Mixed (step-1 resolved, step-2 pending)

Step-1 still has `processed-verdict-573-step-1.md` in resolved. Step-2 has pending request added. Result: `WATCH: awaiting-verdict id=573 pending=verdict-request-573-step-2.md` — only step-2 named. Exit 0.

### Probe 6 — Drift guard forced to RUN

```
GATE_WATCHER_LIVE_DB=/Users/marklehn/Developer/GitHub/bellows/lifecycle.db python3 -m pytest tests/test_gate_watcher.py -q -rs -k reachable_states
```

Result: **1 passed, 45 deselected** — RAN, not skipped. The drift guard is inert in the worktree but verified live here.

**Evidence:** `probes-raw.txt`

## State-space completeness

`TestPauseStateSpace::test_state_space_is_completely_classified` asserts `len(CLASSIFICATION) == 2*3*4 == 24` and that the key set equals `set(itertools.product(PENDING, VERDICT, STATE))`. This test makes an unclassified cell impossible to leave silently. Cell count: **24**.

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite: 0 failed | ✅ |
| 1-count | 1612 total = 1582 baseline + 30 new | ✅ |
| 2.1 | Probe 1 — baseline control (awaiting-verdict) | ✅ |
| 2.1b | Probe 1b — 572 regression killed (pause-line >=1, armed-over 0) | ✅ |
| 2.2 | Probe 2 — stale verdict- form (NOT awaiting-verdict) | ✅ |
| 2.3 | Probe 3 — stale processed-verdict- form (NOT awaiting-verdict) | ✅ |
| 2.4 | Probe 4 — mixed (only unresolved step named) | ✅ |
| 2.5 | Probe 5 — scratch cleaned | ✅ |
| 2.6 | Probe 6 — drift guard RAN (1 passed, verified live) | ✅ |
| 3 | DEV numstat: 3 files | ✅ |
| 3 | Reflog: 0 amends | ✅ |
| 3 | State-space completeness: 24 cells | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/573/knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/
Files verified: 3
