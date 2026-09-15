# QA Receipt — agent-root-inode — 2026-09-14

**Plan:** bellows #100106 — `_agent_owns_root` compares by inode (thread 324)
**Step:** 2 (QA)
**Date run:** 2026-09-15
**Worktree:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100106`
**Branch:** `bellows-wt/100106`
**Base commit:** `e1a477f2`
**DEV commits:** `37788818` (fix) + `bf4fce8a` (mutation run and dev-log)

---

## Item 1 — Counter Before

```
launchctl print gui/$(id -u)/com.eluvian.bellows-daemon | grep -E '^\s*(runs|pid) ='
	runs = 14
	pid = 23737
```

Log file and SIGTERM count before:
```
/Users/marklehn/Developer/bellows/logs/terminal/bellows-2026-09-15.log
1
```

---

## Item 2 — Full Suite

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/agent-root-inode-suite-2026-09-14.txt 2>&1`

Suite count: `2432 passed, 2 skipped` (two skips: test_gate_watcher live-DB; test_fallback_live_wal_window version gate)

**Counter after** (equal to before — suite restarted no agent):
```
	runs = 14
	pid = 23737
```

Log SIGTERM count after:
```
1
```

Both counter pairs equal; branch stayed closed while this step ran.

---

## Item 3 — Comparison Read Through Its Tests

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v tests/test_daemon_agent.py::test_t5_spawn_child_agent_loaded tests/test_daemon_agent.py::test_t9_agent_owns_root_compares_by_inode tests/test_daemon_agent.py::test_t10_spawn_child_foreign_root_spawns_a_child tests/test_daemon_agent.py::test_t11_spawn_child_own_root_kickstarts_without_replace tests/test_daemon_agent.py::test_t13_agent_owns_root_case_variant_spelling`

```
tests/test_daemon_agent.py::test_t5_spawn_child_agent_loaded PASSED      [ 20%]
tests/test_daemon_agent.py::test_t9_agent_owns_root_compares_by_inode PASSED [ 40%]
tests/test_daemon_agent.py::test_t10_spawn_child_foreign_root_spawns_a_child PASSED [ 60%]
tests/test_daemon_agent.py::test_t11_spawn_child_own_root_kickstarts_without_replace PASSED [ 80%]
tests/test_daemon_agent.py::test_t13_agent_owns_root_case_variant_spelling PASSED [100%]
```

t13 PASSED (not SKIPPED) — the mini's filesystem treats case-variant spelling as the same file.

---

## Item 4 — Production Writes

None outside the two evidence files:
- `knowledge/qa/evidence/agent-root-inode-suite-2026-09-14.txt` (suite output)
- `knowledge/qa/evidence/agent-root-inode-qa-receipt-2026-09-14.md` (this file)

No lane file, no lifecycle row, no daemon act. Counter pairs and log counts equal (Items 1 and 2).

---

## DEV Commits — numstat (`e1a477f2..HEAD`)

```
7	2	bellows.py
35	0	knowledge/development/dev-log-agent-root-inode-2026-09-14.md
26	0	knowledge/mutants/agent-root-inode.json
11	0	knowledge/mutants/agent-root-inode.run.txt
20	2	tests/test_daemon_agent.py
```

---

## `bellows.py` Diff (`e1a477f2..HEAD`)

```diff
diff --git a/bellows.py b/bellows.py
index 7579e719..d321cb6b 100644
--- a/bellows.py
+++ b/bellows.py
@@ -202,9 +202,14 @@ def _agent_root(label="com.eluvian.bellows-daemon"):
 
 
 def _agent_owns_root(root, label="com.eluvian.bellows-daemon"):
-    """Return True if the named agent's working directory is `root`."""
+    """Return True iff the named agent's working directory is `root` by inode; False when no agent, directory absent, or empty path."""
     r = _agent_root(label)
-    return r is not None and os.path.realpath(r) == os.path.realpath(str(root))
+    if r is None:
+        return False
+    try:
+        return os.path.samefile(r, str(root))
+    except OSError:
+        return False
 
 
 def _kickstart(label, replace=True):
```

---

## Test File Hunk Headers (`e1a477f2..HEAD`)

Base file line count: 273

```
@@ -211,2 +211,2 @@ def test_t8_agent_root_parses_working_directory(tmp_path):
@@ -221,0 +222,5 @@ def test_t9_agent_owns_root_compares_realpath(tmp_path):
@@ -273,0 +279,13 @@ def test_t12_kickstart_replace_flag():
```

Hunk analysis:
- `@@ -211,2 +211,2 @@` — line 211 is within t9's range (:210–221) ✅
- `@@ -221,0 +222,5 @@` — line 221 is the last line of t9's range (:210–221) ✅
- `@@ -273,0 +279,13 @@` — line 273 equals the base's last line (273) ✅

All hunks are inside t9's lines or after the base file's last line. No hunk touches any MUST-PRESERVE test.

---

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — Counter before (runs=14, pid=23737, SIGTERM=1) | `launchctl print gui/…/com.eluvian.bellows-daemon` + `grep -cF 'SIGTERM received'` | ✅ |
| 2 — Suite 2432 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate); counter after equal (runs=14, pid=23737, SIGTERM=1) | `knowledge/qa/evidence/agent-root-inode-suite-2026-09-14.txt` | ✅ |
| 3 — Five PASSED lines including t13 PASSED and ran (not deferred) on the mini's filesystem | pytest -v output pasted above | ✅ |
| 4 — No production writes outside two evidence files; counter pairs equal | git status --porcelain empty; Items 1 and 2 equal pairs | ✅ |


---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100106/knowledge/qa/evidence/
Files verified: 1
