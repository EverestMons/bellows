# QA Report — wrap-hook plan A: vendor + daemon exemption

**Date:** 2026-08-21
**Plan:** wrap-hook-plan-a-vendor-and-exemption-2026-08-21
**Step:** 3 (QA)
**Role:** QA

## 1. Full Test Suite

**Command:** `python3 -m pytest tests/ -v --timeout=120`

| Metric | Baseline (Step 1) | Full Suite (Step 3) |
|--------|-------------------|---------------------|
| Passed | 1183 | 1203 |
| Failed | 0 | 0 |
| Errors | 0 | 0 |
| Warnings | 1 | 1 |
| Time | 38.45s | 38.62s |

**Baseline counts line:** `1183 passed, 1 warning in 38.45s`
**Full suite counts line:** `1203 passed, 1 warning in 38.62s`

**Regression check:** No regression. The 20 additional passing tests come from `tests/test_wrap_hooks.py` added in Step 2. Zero failures, zero errors in both runs. The failure/error count did not rise. PASSED.

**Evidence:** `knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/pytest_full.txt`

## 2. Live Exemption Canary

### (i-a) The Hook Honours the Marker — PASSED (live spawn)

Spawned a child session with `BELLOWS_DISPATCH=1` and `ELUVIAN_WRAP_ROOT` pointing at a scratch directory with an armed sentinel:

```
BELLOWS_DISPATCH=1 ELUVIAN_WRAP_ROOT=<scratch> claude -p "reply OK" \
  --session-id 7e7a700b-a849-493a-b6e3-f972f53714bc --max-turns 1 < /dev/null
```

Result: Session completed (exit 0, replied "OK"). `hooks.log` gained:
- `SessionStart → daemon-exempt sid=7e7a700b-...`
- `Stop → daemon-exempt sid=7e7a700b-...`

Scratch sentinel remained intact after the child exited — the exempt session did not attempt to unlink it.

### (i-b) The Daemon Sets the Marker — LIVE-VERIFIED

```
$ env | grep -F BELLOWS_DISPATCH
BELLOWS_DISPATCH=1
```

The daemon was restarted at the Step-2 verdict gate. This QA session was spawned by the post-edit `runner.py` and `BELLOWS_DISPATCH=1` is present in our own environment. All three spawn sites carry the marker:

- `runner.py:224`: `env={**os.environ, "BELLOWS_DISPATCH": "1"}`
- `planner.py:135`: `env={**os.environ, "BELLOWS_DISPATCH": "1"}`
- `bellows.py:2000`: `env={**os.environ, "BELLOWS_DISPATCH": "1"}`

### (ii) Interactive Lock INTACT — PASSED (live spawn)

Spawned a non-exempt child session with `BELLOWS_DISPATCH` explicitly unset and `ELUVIAN_WRAP_ROOT` pointing at a scratch directory with an armed sentinel:

```
env -u BELLOWS_DISPATCH ELUVIAN_WRAP_ROOT=<scratch2> claude -p "reply OK" \
  --session-id 6337f3c8-835a-452c-8c5a-8ea222eef88a --max-turns 1 < /dev/null
```

Result: Session was BLOCKED (`Error: Reached max turns (1)`, exit 1). `hooks.log` gained:
- `Stop → armed-BLOCK sid=6337f3c8-...`

`wrap_check` exited nonzero (repos not all clean), confirming the environment was suitable for the blocking assertion. Scratch sentinel remained intact.

**Neither canary touched the governance-root sentinel.** Pre-canary check: `find /Users/marklehn/Developer/GitHub -maxdepth 1 -name '.wrap-in-progress*'` printed nothing.

**Evidence:** `knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/canary.txt`

## 3. Settings Verification

`diff ~/.claude/settings.json bellows/hooks/settings-backup-2026-08-21.json` shows exactly three differing lines — the three eluvian hook `command` paths, now pointing at `bellows/hooks/eluvian/` instead of `~/.claude/eluvian/`. No other delta.

Both files parse as valid JSON (`python3 -m json.tool`, exit 0 for each).

## Verification Table

| # | Assertion | Method | Result |
|---|-----------|--------|--------|
| 1 | Full suite — no regression vs baseline | pytest counts comparison (1183→1203, 0 failures both) | PASSED |
| 2 | (i-a) Hook honours BELLOWS_DISPATCH=1 | Live spawn with pinned UUID, grep hooks.log for daemon-exempt | PASSED |
| 3 | (i-b) Daemon sets the marker | `env \| grep BELLOWS_DISPATCH` in own environment | LIVE-VERIFIED |
| 4 | (ii) Interactive lock intact | Live spawn with env -u, armed scratch sentinel, grep hooks.log for armed-BLOCK | PASSED |
| 5 | Scratch sentinel (i-a) survives exempt session | `test -f` after child exit | PASSED |
| 6 | Scratch sentinel (ii) survives blocked session | `test -f` after child exit | PASSED |
| 7 | settings.json points at vendored copies | diff shows only 3 eluvian command paths differ | PASSED |
| 8 | settings.json valid JSON | `python3 -m json.tool` exit 0 | PASSED |
| 9 | settings backup valid JSON | `python3 -m json.tool` exit 0 | PASSED |
| 10 | No governance-root sentinel created/deleted | pre-canary `find` printed nothing | PASSED |

## Scope Compliance

This QA report covers the daemon exemption (plan A) only. It does NOT claim to fix capture 2 (two interactive sessions sharing one sentinel) — that is plan B's subject. The canary tests verify that:
- Daemon-dispatched sessions are exempt from the wrap lock (i-a, i-b)
- Non-exempt sessions are still blocked by an armed sentinel (ii)
- The CEO's interactive lock is not weakened by the exemption

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/496/knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/
Files verified: 2
```
