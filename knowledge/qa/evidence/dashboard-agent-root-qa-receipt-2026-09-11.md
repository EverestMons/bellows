# QA Receipt — dashboard-agent-root-2026-09-11

**Plan:** #100087 — dashboard._spawn_child kickstarts only its own root's agent
**Step:** 2 (QA)
**Date:** 2026-09-11
**Thread:** 297

## DEV Commits (numstat 1d0260b..b5f581b)

```
38  4   bellows.py
 2  2   dashboard.py
37  0   knowledge/development/dev-log-dashboard-agent-root-2026-09-11.md
41  0   knowledge/mutants/dashboard-agent-root.json
15  0   knowledge/mutants/dashboard-agent-root.run.txt
101  2   tests/test_daemon_agent.py
 1  0   tests/test_dashboard.py
```

Seven files across two commits (`98acd47` five files, `b5f581b` two files).

## Verification

| Item | Claim | Evidence | Status |
|------|-------|----------|--------|
| 1 — counter before | `runs = 9`, `pid = 59263` before the full suite run | `launchctl print gui/501/com.eluvian.bellows-daemon \| grep -E '^\s*(runs\|pid) ='` → `runs = 9`, `pid = 59263` | ✅ |
| 2 — full suite and counter after | Suite: 2295 passed; two exclusions (test_gate_watcher live-DB; test_fallback_live_wal_window version gate); counter after `runs = 9`, `pid = 59263` — equal to before; SIGTERM count 11 before, 11 after — equal; branch closed, daemon not restarted | Suite file `dashboard-agent-root-suite-2026-09-11.txt` last line: 2295 passed, two known exclusions; same `launchctl print` command run after suite exit → `runs = 9`, `pid = 59263`; both pairs equal | ✅ |
| 3 — production writes | No production writes outside the two evidence files; no lane file, no live lifecycle row, no daemon act | Scope limited to `dashboard-agent-root-qa-receipt-2026-09-11.md` and `dashboard-agent-root-suite-2026-09-11.txt`; `git status --porcelain` after suite shows only these two untracked files | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100087/knowledge/qa/evidence/
Files verified: 1
