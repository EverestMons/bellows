# QA Receipt — wrap-3d-central-glossary (2026-08-26)

**Plan:** 543 | **Step:** 2 (QA) | **CAPTURE_COMMIT:** `1503249`

## Verification Table

| Item | Check | Expected | Measured | Status |
|------|-------|----------|----------|--------|
| 1a | `"NEVER write to"` in wrap.md | 1 | 1 | ✅ |
| 1b | `"If the file does not exist, create it"` in wrap.md | 0 | 0 | ✅ |
| 1c | `"surface that belongs in the project's glossary?"` in wrap.md | 0 | 0 | ✅ |
| 1d | `"/Users/marklehn/Developer/GitHub/GLOSSARY.md"` in wrap.md | 1 | 1 | ✅ |
| 1e | `"3d."` in wrap.md | 1 | 1 | ✅ |
| 1f | Case-insensitive `"glossary"` count in wrap.md (vs dev note) | 4 | 4 | ✅ |
| 1g | `"RETIRED"` in glossary.md | 1 | 1 | ✅ |
| 1h | `^## ` count (regex) in glossary.md | 0 | 0 | ✅ |
| 1i | `"[project: bellows]"` in glossary.md | >= 2 | 2 | ✅ |
| 1j | wrap.md live-vs-committed cmp | IDENTICAL | IDENTICAL | ✅ |
| 1k | glossary.md live-vs-committed cmp | IDENTICAL | IDENTICAL | ✅ |
| 2 | Completeness proof re-run (10 MATCH lines, parent bytes) | 10 matches | 10 matches | ✅ |
| 3a | numstat file count | 3 | 3 | ✅ |
| 3b | show-toplevel == bellows worktree root | bellows worktree | `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/543` | ✅ |
| 3c | reflog -n 4: 0 amends | 0 | 0 | ✅ |

All 15 checks pass.

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/543/knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/
Files verified: 2
