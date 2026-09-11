# QA Receipt — guard-class-hold-parked-2026-09-11

**Plan:** bellows — the lessons guard parks a class-held deposit (thread 278) | **Step:** 2 (QA)
**Date:** 2026-09-11 | **Worktree:** bellows-wt/100076

## numstat — DEV commits (2e3d600..HEAD)

```
1	1	hooks/commands/wrap.md
33	0	knowledge/development/dev-log-guard-class-hold-parked-2026-09-11.md
26	0	knowledge/mutants/guard-class-hold-parked.json
11	0	knowledge/mutants/guard-class-hold-parked.run.txt
92	26	tests/test_lessons_guard.py
38	13	tools/lessons_guard.py
```

## Verification

| Item | Status | Evidence |
|------|--------|----------|
| 1 — full suite | ✅ | 2262 passed; one skip (test_gate_watcher, live-DB) |
| 2 — guard on copy of live lanes | ✅ | pass 1: `lanes: 1  frozen: no  class-held: 1` exit 0; pass 2 (stale probe added): FROZEN — `hold-executable-qa-probe.md` named exit 2; class-held hold absent from FROZEN list |
| 3 — production writes | ✅ | None outside the two evidence files; $T removed; no lane file, no lifecycle row, no daemon |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100076/knowledge/qa/evidence/
Files verified: 1
