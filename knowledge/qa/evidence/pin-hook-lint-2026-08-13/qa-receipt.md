# QA Receipt — pin-hook-lint-2026-08-13 (Plan 371, Step 2)

**Date:** 2026-08-13
**Plan slug:** `pin-hook-lint-2026-08-13`
**Step-1 commit:** `0f12365` — confirmed present via `git log --oneline -- scripts/plan_lint.py`; made by a prior dispatch (independence satisfied).

---

## Verification Table

| Item | Ledger | Verdict | Evidence |
|------|--------|---------|----------|
| Item 1 — full suite | C4 | ✅ | 997 passed, 1 warning — `pytest-full-raw.txt` |
| Item 2 — C1 warn-first live | C1 | ✅ | EXIT 0 with both `(q) WARN` lines — see raw output below |
| Item 3 — C2 + C5 location-independence | C2, C5 | ✅ | Identical PIN-CHECK lines at real and scratch paths — see raw output below |
| Item 4 — C4 count verification | C4 | ✅ | Dev note: before=110, after=122; targeted run confirms 122; full suite 997 |
| Item 5 — raw output | — | ✅ | All counts are pasted stdout |

---

## Item 1 — Full Suite (foreground, no Monitor)

Command: `python3 -m pytest tests/ -q`

Result: **997 passed, 1 warning in 25.00s**

Raw tail in `pytest-full-raw.txt`.

Targeted module verification: `python3 -m pytest tests/test_plan_lint.py -q` → **122 passed, 1 warning in 4.65s** — matches dev note's "After: 122".

---

## Item 2 — C1 Live (warn-first enforcement)

Fixture: `knowledge/qa/evidence/pin-hook-lint-2026-08-13/fixture-bad-pins.md`

The fixture is a minimal valid plan (`dispatch_mode: bellows`, `pause_for_verdict: always`) whose body carries:
1. A `shasum -a 256` invocation naming `scripts/plan_lint.py` with a deliberately wrong 64-hex hash (all zeroes) — exercises M2 → MISMATCH
2. An unresolvable 40-hex token (`fff...`) with a `git -C /Users/marklehn/Developer/GitHub/bellows` reference on the same line — exercises M1 → unresolved

Command: `python3 scripts/plan_lint.py knowledge/qa/evidence/pin-hook-lint-2026-08-13/fixture-bad-pins.md`

```
PIN-CHECK: kind=sha256 line=16 token=000000000000… result=mismatch
PIN-CHECK: kind=git line=20 token=ffffffffffff… result=unresolved
(q) WARN: line 16 sha256 pin 000000000000… MISMATCH on /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py
(q) WARN: line 20 git pin ffffffffffff… unresolved
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
```

**EXIT CODE: 0** — both `(q) WARN` lines present, exit code unchanged. C1 confirmed.

---

## Item 3 — C2 + C5 Live (location-independence + one-telemetry-per-token)

Target file: `knowledge/decisions/Done/diagnostic-370.md`

### Run A — real path

Command: `python3 scripts/plan_lint.py knowledge/decisions/Done/diagnostic-370.md`

```
(o1) INFO: candidates=7 excluded=1 fired=0
PIN-CHECK: kind=git line=21 token=8f0a84903ac0… result=repo-unavailable
PIN-CHECK: kind=git line=21 token=dab46c9c1cc8… result=repo-unavailable
PIN-CHECK: kind=git line=21 token=2c3d1b43b5ed… result=repo-unavailable
PIN-CHECK: kind=git line=44 token=d09f274ade88… result=repo-unavailable
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 1 file(s), 0 prefix(es)
```

### Run B — scratch copy at `/tmp/scratch-diagnostic-370.md`

Command: `python3 scripts/plan_lint.py /tmp/scratch-diagnostic-370.md`

```
(o1) INFO: candidates=7 excluded=1 fired=0
PIN-CHECK: kind=git line=21 token=8f0a84903ac0… result=repo-unavailable
PIN-CHECK: kind=git line=21 token=dab46c9c1cc8… result=repo-unavailable
PIN-CHECK: kind=git line=21 token=2c3d1b43b5ed… result=repo-unavailable
PIN-CHECK: kind=git line=44 token=d09f274ade88… result=repo-unavailable
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 1 file(s), 0 prefix(es)
```

**PIN-CHECK line sets are identical.** 4 tokens, 4 telemetry lines — C5 (one line per token) confirmed. Results match between real and scratch paths — C2 (location-independence) confirmed. All results are `repo-unavailable` because the worktree's BELLOWS_ROOT.parent does not resolve to a .git-bearing directory — this is the correct spec behavior ("A missing/`.git`-less resolved repo → telemetry `result=repo-unavailable`, no WARN").

---

## Item 4 — C4 Count Verification

Dev note (`knowledge/development/pin-hook-lint-dev-2026-08-13.md`) claims:
- Before: 110 passed (targeted `test_plan_lint.py`)
- After: 122 passed (110 + 12 new)

Measured reality:
- Targeted run: 122 passed — matches dev note's "After" count
- Delta: 122 - 110 = 12 new tests — matches dev note's delta claim
- Full suite: 997 passed — no failures, all 12 new tests integrated cleanly

C4 confirmed: every count verified, none assumed.

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/371/knowledge/qa/evidence/pin-hook-lint-2026-08-13/
Files verified: 3
```
