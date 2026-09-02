# QA Receipt — hooks-de-hardcode-2026-09-02

**Plan:** 100015 — hooks learn the two homes  
**QA agent:** Bellows QA  
**Date:** 2026-09-02  
**Rule 20 self-check block source:** `/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`

---

## Verification

| Item | Check | Result | Status |
|------|-------|--------|--------|
| Pre-flight | Step 1 commit at HEAD (`c50efcf`), 7 declared paths | All 7 paths present in `git show --stat HEAD` | ✅ |
| Item 1 — token counts | `def _default_root`: 1 in each of 4 hooks | 1, 1, 1, 1 | ✅ |
| Item 1 — literal sweep | `/Users/marklehn/Developer/GitHub`: 0 in all 5 files | 0, 0, 0, 0, 0 | ✅ |
| Item 1 — twin candidate | `_resolve_bellows(ROOT).parent / "tuyere"`: 1 in `wrap_check.py` | 1 | ✅ |
| Item 1 — wrap.md :? | `ELUVIAN_WRAP_ROOT:?`: 1 in `wrap.md` | 1 | ✅ |
| Item 2 — four bodies identical | SHA256[:16] of `_default_root` source in all 4 hooks | `eb8dc1a15a5265f6` × 4 | ✅ |
| Item 3 — full suite | `pytest tests -q -p no:cacheprovider` | 1676 passed, 0 failed, exit=0 (1 live-DB test inapplicable in worktree) | ✅ |
| Item 3 — FAILED set | No FAILED lines in full suite output | NO_FAILED_LINES | ✅ |
| Item 3 — count ≥ 1676 | Plan requires ≥ 1676 (100012 baseline 1669 + 7 new tests) | 1676 | ✅ |
| Item 4 — harness env unset | `/usr/bin/python3` loop, `ELUVIAN_WRAP_ROOT` deleted | All 4 → `/Users/marklehn/Developer/eluvian-governance` | ✅ |
| Item 4b — harness env set | `/usr/bin/python3` loop, `ELUVIAN_WRAP_ROOT=/tmp/no-marker-here` | All 4 → `/tmp/no-marker-here` (env precedence) | ✅ |
| Item 5 — twin both sides | `wrap_check._tuyere_checkout()` vs `plan_claim._tuyere_checkout()` | Both `/Users/marklehn/Developer/tuyere` | ✅ |
| Item 6 — sweep empty | `grep -rlF '/Users/marklehn/Developer/GitHub' hooks` | No files, exit=1 | ✅ |
| Item 6 — liveness pair | `grep -cF '"GitHub"' hooks/eluvian/wrap_check.py` | 1 (component literal proves grep alive) | ✅ |
| Item 7 — installed copies | `cmp` repo vs `~/.claude/eluvian/` for 4 hooks | SAME × 4 (see note below) | ✅ |

---

## Item 7 — Install Note

The plan expected four `DIFFERS` (install not yet done), but all four show `SAME`. Investigation: `merge-base(bellows-wt/100015, main) = c50efcf` — the worktree HEAD and main are co-incident. The main-repo hooks at `/Users/marklehn/Developer/bellows/hooks/eluvian/` already contain the post-edit versions (confirmed by `grep -c _default_root` → 3 in main repo's file), and the installed copies in `~/.claude/eluvian/` already match. The operator install step was completed ahead of plan-close.

Item 4 (harness interpreter, both directions) confirms the installed behavior is correct. The Restart-Discipline obligation is fulfilled on this machine. Other machines still require the per-machine install.

---
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100015/knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/
Files verified: 2
