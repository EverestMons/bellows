# QA Receipt — close_cycle prefix-and-prime — 2026-09-11

**Plan:** 100090 | **Step:** 2 (QA) | **Date:** 2026-09-11

## DEV commits numstat (c7b0d36..bf183be — five files)

```
47      0       knowledge/development/dev-log-close-cycle-prefix-and-prime-2026-09-11.md
34      0       knowledge/mutants/close-cycle-prefix-and-prime.json
12      0       knowledge/mutants/close-cycle-prefix-and-prime.run.txt
27      1       scripts/close_cycle.py
112     7       tests/test_close_cycle.py
```

## Item 2 — Replay: old tool (pre-merge) then new tool (this worktree)

**Draft:** `401715f7^` (readonly-probe, one commit before its close); walk register ref rewritten to clone path and committed in the clone. Both runs with `--dry-run`.

**Pre-merge tool** (`/Users/marklehn/Developer/bellows/scripts/close_cycle.py`, canonical checkout, unmodified):
```
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK
CLOSE: baseline OK
CLOSE: stored==live FAIL — stored 'validation: cycle_check=ESCALATE:claimed-close-unmet, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:13' != live 'validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:13'
```

**This worktree's tool** (`scripts/close_cycle.py` at `bf183be`, with prime):
```
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK
CLOSE: prime OK — the first emit read a placeholder manifest; re-emitted on the spliced draft
CLOSE: baseline OK
CLOSE: stored==live OK
CLOSE: battery OK
CLOSE: commit(skipped) OK
```

## Verification

| Item | Evidence | Status |
|---|---|---|
| 1 — full suite | 2305 passed; 2 tests excluded by live-environment guards (test_gate_watcher live-DB; test_fallback_live_wal_window version gate); no failed | ✅ |
| 2 — replay | Pre-merge: `CLOSE: stored==live FAIL`; this worktree: `CLOSE: prime OK`, `CLOSE: stored==live OK`, `CLOSE: battery OK` | ✅ |
| 3 — production writes | None outside the two evidence files; clone and `$T` removed after Item 2; no lane file, no lifecycle row, no daemon act | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100090/knowledge/qa/evidence/
Files verified: 1
