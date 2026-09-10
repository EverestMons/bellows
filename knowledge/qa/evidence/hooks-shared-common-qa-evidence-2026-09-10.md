# QA Evidence — hooks-shared-common — 2026-09-10

Plan: `hooks-shared-common-2026-09-10` | Step 2 (QA) | [100062] [thread 259]

## DEV commits numstat (2d317f0..HEAD — thirteen files)

```
4	5	hooks/README.md
73	0	hooks/eluvian/_common.py
2	42	hooks/eluvian/eluvian_align_hook.py
2	39	hooks/eluvian/wrap_arm_hook.py
2	15	hooks/eluvian/wrap_check.py
3	28	hooks/eluvian/wrap_debt_hook.py
2	38	hooks/eluvian/wrap_stop_hook.py
145	0	knowledge/development/dev-log-hooks-shared-common-2026-09-10.md
49	0	knowledge/mutants/hooks-shared-common.json
16	0	knowledge/mutants/hooks-shared-common.run.txt
13	10	tests/test_hook_default_root.py
146	0	tests/test_hooks_shared_common.py
1	0	tests/test_wrap_sentinel.py
```

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — Full suite | `2186 passed, 1 skip` (one skip: test_gate_watcher, live-DB — panel E7); nine hook test files `146 passed` | ✅ |
| 2 — Extraction body-for-body | `_log_path`: IDENTICAL; `hooklog`: IDENTICAL; `emit`: IDENTICAL; `_validate_session_id`: IDENTICAL; `_default_root`: docstring-only diff (last two sentences rewritten per *What this changes* 1), body unchanged | ✅ |
| 3 — Four harness hooks RUN live | All eight runs (four worktree + four canonical) exit 0; one JSON line each; log carries non-exempt lines (`ignored`, `unarmed-allow`, `DEBT-injected`, `parked=0 sync=[]`); no `daemon-exempt`; canary → `/Users/marklehn/Developer/eluvian-governance`; live wiring picks up new files at merge by symlink, no act required | ✅ |
| 4 — Identity test + regression | `tests/test_hook_default_root.py`: 7 passed; probe confirms `copy._default_root is common._default_root: False` when a local def shadows the import — test (d) guards this property | ✅ |
| 5 — Production writes | None beyond the two evidence files; no git fetch of canonical checkouts; no lifecycle import; `~/.claude/eluvian` symlink unchanged (`lrwxr-xr-x … Aug 24 16:29 /Users/marklehn/.claude/eluvian -> /Users/marklehn/Developer/bellows/hooks/eluvian`); scratch dir removed | ✅ |

## Item 2 detail — body-for-body diffs

```
=== _log_path: IDENTICAL ===
=== hooklog: IDENTICAL ===
=== emit: IDENTICAL ===
=== _validate_session_id: IDENTICAL ===
=== _default_root: DIFF ===
--- main:wrap_arm_hook.py/_default_root
+++ _common.py/_default_root
@@ -1,10 +1,12 @@
 def _default_root() -> Path:
     """The governance root when $ELUVIAN_WRAP_ROOT is unset: the two known homes,
     admitted only by their COMPANY.md marker; the first if neither holds it — a
-    hook must never crash a session. Duplicated verbatim in the four hooks by
-    design: they are standalone files copied into ~/.claude/eluvian/, and a
-    shared module would be one more file to install (test_hook_default_root
-    asserts the four bodies stay identical). Plan hooks-de-hardcode, 2026-09-02."""
+    hook must never crash a session. Shared by the hooks through `_common.py`
+    since plan hooks-shared-common (2026-09-10); the hooks load from
+    `hooks/eluvian/` on every machine — a symlink on the mini, the repo path
+    in the shop's settings (MACHINE_SETUP v1.1a). Plan 100015 duplicated this
+    body on the copies premise; `test_hook_default_root` (d) now asserts the
+    four hooks that resolve a root bind THIS function."""
     for cand in (Path.home() / "Developer" / "eluvian-governance",
                  Path.home() / "Developer" / "GitHub"):
         if (cand / "COMPANY.md").is_file():
```

## Item 3 detail — eight hook runs

### Worktree hooks (`…/hooks/eluvian/<hook>.py`)

**wrap_arm_hook [worktree]**
```
stdout: {}
exit: 0
log:   2026-09-10T12:04:15	UserPromptSubmit-arm	ignored sid=qa-1e3c2112-3942-4f62-8212-24d397080243
```

**wrap_stop_hook [worktree]**
```
stdout: {}
exit: 0
log:   2026-09-10T12:04:15	Stop	unarmed-allow sid=qa-1e3c2112-3942-4f62-8212-24d397080243
```

**wrap_debt_hook [worktree]**
```
stdout: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "⚠️ UNWRAPPED SESSION DEBT DETECTED…[3b/lessons]…"}}
exit: 0
log:   2026-09-10T12:04:15	SessionStart	DEBT-injected sid=qa-1e3c2112-3942-4f62-8212-24d397080243
```

**eluvian_align_hook [worktree]**
```
stdout: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Eluvian doctrine:…Daemon: STOPPED\n⚠️ Sync: root NOT RESOLVED…"}}
exit: 0
log:   2026-09-10T12:04:15	SessionStart-align	parked=0 sync=[]
```

No `daemon-exempt` lines in log. All four: exit 0, one JSON line.

### Canonical hooks (`/Users/marklehn/.claude/eluvian/<hook>.py`, pre-merge, old code — control)

**wrap_arm_hook [canonical]**
```
stdout: {}
exit: 0
log:   2026-09-10T12:04:15	UserPromptSubmit-arm	ignored sid=qa-1e3c2112-3942-4f62-8212-24d397080243
```

**wrap_stop_hook [canonical]**
```
stdout: {}
exit: 0
log:   2026-09-10T12:04:15	Stop	unarmed-allow sid=qa-1e3c2112-3942-4f62-8212-24d397080243
```

**wrap_debt_hook [canonical]**
```
stdout: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "⚠️ UNWRAPPED SESSION DEBT DETECTED…[3b/lessons]…"}}
exit: 0
log:   2026-09-10T12:04:15	SessionStart	DEBT-injected sid=qa-1e3c2112-3942-4f62-8212-24d397080243
```

**eluvian_align_hook [canonical]**
```
stdout: {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Eluvian doctrine:…Daemon: STOPPED\n⚠️ Sync: root NOT RESOLVED…"}}
exit: 0
log:   2026-09-10T12:04:15	SessionStart-align	parked=0 sync=[]
```

Both canonical (old inline code) and worktree (new `_common` imports) produce identical output shape. The live wiring picks up the new files at the merge, by the symlink, with no act required.

**Canary (worktree arm hook, no ELUVIAN_WRAP_ROOT):**
```
env -u ELUVIAN_WRAP_ROOT /usr/bin/python3 -c "…wrap_arm_hook.py…; print(m._default_root())"
→ /Users/marklehn/Developer/eluvian-governance
```

## Item 4 detail — identity test + regression probe

`pytest tests/test_hook_default_root.py -q` → `7 passed in 1.60s`

Regression probe (copy of wrap_arm_hook with local `def _default_root` pasted after import):

```
common._default_root id: 4376546016
copy._default_root is common._default_root: False
copy._default_root id: 4376553536
'def _default_root' in copy source: True

Conclusion: the copy's local def_default_root shadows the shared one.
test_d_four_hooks_bind_the_shared_helper guards against this: it asserts
mod._default_root IS common._default_root (identity), which fails when a
local copy re-appears after the from _common import line.
```

The identity check (`is`, not `==`) proves the property. When a hook regrows a local `_default_root`, the import shadows it and the ids diverge — test (d) fails.

## Item 5 detail — production writes

- No `git fetch` of any canonical checkout (the align hook's `_sync_repos` resolved inside scratch `$T`, where no `.git` dirs exist — `_resolved = []`, no fetch called).
- No run of the canonical `status.py` (align hook ran `$T/root/bellows/status.py`, the one-line stub).
- No launch of the canonical tuyere CLI (`ELUVIAN_WRAP_TUYERE=$T/lf`, no `.venv` there → `_tuyere_checkout()` returns None → `_session_wraps_today()` returns None without spawning a subprocess).
- No lifecycle import.
- `~/.claude/eluvian` unchanged: `lrwxr-xr-x … Aug 24 16:29 /Users/marklehn/.claude/eluvian -> /Users/marklehn/Developer/bellows/hooks/eluvian`
- Scratch dir removed.
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100062/knowledge/qa/evidence/
Files verified: 1
