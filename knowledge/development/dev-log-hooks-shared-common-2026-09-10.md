# Dev log — hooks-shared-common — 2026-09-10

## Pins re-derived (P1, P2, P4, P5)

**P2 re-derived (sha256[:16] and line counts, last writers):**
`wrap_arm_hook.py` sha256[:16] `cd405b04b47f990b` 143 lines; `wrap_stop_hook.py` `4171db3a0bfa4ada` 268; `wrap_check.py` `c3cdb1ff193fcac2` 580; `eluvian_align_hook.py` `06fd96aa71d6ef3f` 245; `wrap_debt_hook.py` `55cb3d0815d3bde1` 114; last writers: arm/stop/align `c50efcf` (100015, 2026-09-02), check `f1fed67` (2026-09-02), debt `cf4c694` (2026-08-25, plan 520)

**P1 re-derived (grep -n inventory):**

```
hooks/eluvian/eluvian_align_hook.py:21:def _default_root() -> Path:
hooks/eluvian/eluvian_align_hook.py:46:_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")
hooks/eluvian/eluvian_align_hook.py:51:def _log_path():
hooks/eluvian/eluvian_align_hook.py:55:def hooklog(event, detail=""):
hooks/eluvian/eluvian_align_hook.py:64:def emit(context):
hooks/eluvian/wrap_debt_hook.py:26:_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")
hooks/eluvian/wrap_debt_hook.py:29:_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")
hooks/eluvian/wrap_debt_hook.py:32:def _log_path():
hooks/eluvian/wrap_debt_hook.py:36:def hooklog(event, detail=""):
hooks/eluvian/wrap_debt_hook.py:45:def emit(context):
hooks/eluvian/wrap_arm_hook.py:36:def _default_root() -> Path:
hooks/eluvian/wrap_arm_hook.py:51:_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")
hooks/eluvian/wrap_arm_hook.py:61:_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")
hooks/eluvian/wrap_arm_hook.py:68:def _log_path():
hooks/eluvian/wrap_arm_hook.py:72:def _validate_session_id(raw_id):
hooks/eluvian/wrap_arm_hook.py:90:def hooklog(event, detail=""):
hooks/eluvian/wrap_check.py:43:def _default_root() -> Path:
hooks/eluvian/wrap_stop_hook.py:34:def _default_root() -> Path:
hooks/eluvian/wrap_stop_hook.py:50:_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")
hooks/eluvian/wrap_stop_hook.py:53:_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")
hooks/eluvian/wrap_stop_hook.py:61:def _log_path():
hooks/eluvian/wrap_stop_hook.py:65:def hooklog(event, detail=""):
hooks/eluvian/wrap_stop_hook.py:84:def _validate_session_id(raw_id):
```

Mechanism check: body hashes, line numbers, and file counts all match P1's pinned values. No mismatch — extraction proceeds.

**P4 re-derived:**

```
lrwxr-xr-x@ 1 marklehn  staff  47 Aug 24 16:29 /Users/marklehn/.claude/eluvian -> /Users/marklehn/Developer/bellows/hooks/eluvian
```

Settings entries (four hooks wired):
- `UserPromptSubmit → /usr/bin/python3 /Users/marklehn/.claude/eluvian/wrap_arm_hook.py`
- `Stop → /usr/bin/python3 /Users/marklehn/.claude/eluvian/wrap_stop_hook.py`
- `SessionStart → /usr/bin/python3 /Users/marklehn/.claude/eluvian/wrap_debt_hook.py`
- `SessionStart → /usr/bin/python3 /Users/marklehn/.claude/eluvian/eluvian_align_hook.py`

`/usr/bin/python3 --version` → `Python 3.9.6`

**P5 re-derived:**

Full suite before extraction: `2181 passed, 1 skipped in 84.50s` (hook test files contribute 141 of those). Harness interpreter 3.9.6 confirmed. All four loading idioms confirmed present in the eight hook test files.

---

## Failing-first (test (d) and s1–s4 red, s5 and six green, then all green)

Run of the two files BEFORE extraction (Item 2):

```
tests/test_hook_default_root.py::test_d_four_hooks_bind_the_shared_helper FAILED
    ModuleNotFoundError: No module named '_common'

tests/test_hooks_shared_common.py::test_s1_shared_names_in_common_not_in_hooks FAILED
    AssertionError: _common.py not found

tests/test_hooks_shared_common.py::test_s2_common_imports_under_harness_python FAILED
    _common.py failed to import under /usr/bin/python3: ModuleNotFoundError

tests/test_hooks_shared_common.py::test_s3_hooklog_writes_and_swallows FAILED
    ModuleNotFoundError: No module named '_common'

tests/test_hooks_shared_common.py::test_s4_emit_outputs_json_and_exits FAILED
    ModuleNotFoundError: No module named '_common'

5 failed, 7 passed in 0.46s
```

Seven passing: (a), (b), (c), (e), (f), (g) — the six unchanged `test_hook_default_root` tests — and (s5) which is GREEN before extraction (pins behaviour the hooks already have, panel D10).

After extraction (Item 3), nine hook test files: `146 passed in 9.73s`.
Full suite after extraction: `2186 passed, 1 skipped in 84.82s` (1 skip = `test_gate_watcher`, live-DB, absent in worktree — panel E7).

---

## Extraction diff

```
wrap_arm_hook.py | 41 ++---------------------------------------
 1 file changed, 2 insertions(+), 39 deletions(-)
 deleted def lines: 4 (_default_root, _log_path, _validate_session_id, hooklog)
 also deleted: _DEFAULT_LOG =, _VALID_SESSION_ID =

wrap_stop_hook.py | 40 ++--------------------------------------
 1 file changed, 2 insertions(+), 38 deletions(-)
 deleted def lines: 4 (_default_root, _log_path, hooklog, _validate_session_id)
 also deleted: _DEFAULT_LOG =, _VALID_SESSION_ID =

wrap_check.py | 17 ++---------------
 1 file changed, 2 insertions(+), 15 deletions(-)
 deleted def lines: 1 (_default_root only)

eluvian_align_hook.py | 44 ++-----------------------------------
 1 file changed, 2 insertions(+), 42 deletions(-)
 deleted def lines: 4 (_default_root, _log_path, hooklog, emit)
 also deleted: _DEFAULT_LOG =

wrap_debt_hook.py | 31 +++----------------------------
 1 file changed, 3 insertions(+), 28 deletions(-)
 deleted def lines: 3 (_log_path, hooklog, emit)
 also deleted: _DEFAULT_LOG =, _VALID_SESSION_ID =
```

Each hook's diff is deletions plus the two insertion lines (`sys.path.insert` + `from _common import`). Nothing else moved.

Harness-interpreter check (Item 4):
```
wrap_arm_hook imports OK
wrap_stop_hook imports OK
wrap_check imports OK
eluvian_align_hook imports OK
wrap_debt_hook imports OK
_common imports OK
```

Canary (`env -u ELUVIAN_WRAP_ROOT /usr/bin/python3 -c "...wrap_arm_hook...; print(m._default_root())"`) → `/Users/marklehn/Developer/eluvian-governance`

`~/.claude/eluvian` symlink: unchanged, quoted above.

---

## Mutation run

Manifest: `knowledge/mutants/hooks-shared-common.json` (committed in first commit).
Command: `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/hooks-shared-common.json > knowledge/mutants/hooks-shared-common.run.txt 2>&1`

Result (last line of run file):

```
MUTATION: 6 killed, 0 survived, 0 error
```

All six mutants killed. No survivors.
