# QA Receipt — id-range-partitioning-doc (2026-08-26)

**Plan:** executable-555 | **Step:** 2 (QA) | **CAPTURE_COMMIT:** 632561b

## Verification Table

| Item | Check | Status |
|---|---|---|
| 1a | `grep -cF "Multi-machine id ranges"` on committed CLAUDE.md == 1 | ✅ |
| 1b | `grep -cF "100000-block"` on committed CLAUDE.md == 1 | ✅ |
| 1c | `grep -cF "NEVER re-seed"` on committed CLAUDE.md == 1 | ✅ |
| 1d | Pre-existing tail "Recommended cadence: at session-wrap or weekly." count == 1 | ✅ |
| 1e | All 6 parent section headings preserved in committed file | ✅ |
| 1f | Line arithmetic: old (34) + added (21) == recorded wc -l (55) | ✅ |
| 1g | `cmp` committed vs live CLAUDE.md exit 0 | ✅ |
| 2a | GLOSSARY.md contains "id-range partitioning" (>= 1) | ✅ |
| 2b | shop_next_session.md contains "seed its" (>= 1) | ✅ |
| 3a | numstat: exactly 2 files (CLAUDE.md 21-0, dev-log 20-0) | ✅ |
| 3b | toplevel correct (worktree 555) | ✅ |
| 3c | reflog -n 4: 0 amends | ✅ |

## Evidence

- `probes-raw.txt` — full raw output of all probes
- `qa-receipt.md` — this file

## Gate Note

Probe-battery QA, no pytest scope — benign class (doc-only append, no code path).

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/555/knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/
Files verified: 2
