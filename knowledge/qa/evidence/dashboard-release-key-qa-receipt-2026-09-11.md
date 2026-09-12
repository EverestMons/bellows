# QA Receipt: dashboard-release-key-2026-09-11

**Plan:** 100093 — dashboard releases a class hold via `l` key  
**Step:** 2 (QA)  
**Date:** 2026-09-12  
**Interpreter:** `/Users/marklehn/Developer/bellows/.venv/bin/python` (absolute)

## DEV commits numstat (69d42b8..HEAD — five files)

```
97	18	dashboard.py
42	0	knowledge/development/dev-log-dashboard-release-key-2026-09-11.md
33	0	knowledge/mutants/dashboard-release-key.json
12	0	knowledge/mutants/dashboard-release-key.run.txt
118	0	tests/test_dashboard.py
```

## Item 2 — seven tests by name (eight node lines, each PASSED)

```
tests/test_dashboard.py::TestPTYSmoke::test_pty_launch_refresh_quit PASSED [ 12%]
tests/test_dashboard.py::TestClassHoldRows::test_only_class_holds_sorted PASSED [ 25%]
tests/test_dashboard.py::TestReleaseFooter::test_offers_release_for_a_class_hold PASSED [ 37%]
tests/test_dashboard.py::TestReleaseFooter::test_no_release_key_without_a_class_hold PASSED [ 50%]
tests/test_dashboard.py::TestReleaseFooter::test_confirm_release_footer PASSED [ 62%]
tests/test_dashboard.py::TestDoRelease::test_runs_the_same_command_with_the_target_path PASSED [ 75%]
tests/test_dashboard.py::TestDoRelease::test_nonzero_exit_is_shown PASSED [ 87%]
tests/test_dashboard.py::TestHandleKey::test_confirm_cancels_and_l_needs_a_class_hold PASSED [100%]
```

## Verification

| Item | Status | Evidence |
|------|--------|----------|
| Item 1: full suite | ✅ | `dashboard-release-key-suite-2026-09-11.txt` last line: `2313 passed` — two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate) |
| Item 2: seven tests + PTY smoke by name | ✅ | Eight node lines above, each `PASSED` |
| Item 3: production writes | ✅ | None outside the two evidence files; no lane file, no live lifecycle row, no daemon act, no release; scratch dir `/tmp/release-key-qa.x40GRD` removed |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100093/knowledge/qa/evidence/
Files verified: 1
