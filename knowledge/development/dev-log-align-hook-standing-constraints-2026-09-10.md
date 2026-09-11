# Dev Log — align-hook-standing-constraints — 2026-09-10

Plan #100066, thread 267.

## Pins re-derived (P2, P3, P4, P5)

**P2 — the hook as it stands:** `hooks/eluvian/eluvian_align_hook.py` (205 lines, sha `208f29b8a6d2`, last writer `7afd777` #100062): `_GOV_ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or _default_root())` `:22`; `_resolve_sibling` `:40`, `_sync_repos` `:63`, `_repo_sync` `:98`, `_daemon_status` `:127`, `_parked_count` `:146`; `main()` `:165–196` builds `parts` = the doctrine line `f"Eluvian doctrine: {_DOCTRINE}"`, `f"Daemon: {daemon}"`, `Parked arcs: N` when non-zero, the sync line (`⚠️ Sync: …` or `Sync: core repos current…`), `Type /eluvian for the full alignment pass.`, then `hooklog("SessionStart-align", …)` and `emit("\n".join(parts))`; the `__main__` guard `:199–205` prints `⚠️ eluvian_align_hook: internal error (FAIL-OPEN, continuing)` then `{}` and exits 0 on any exception; `_common.emit` `:53–63` wraps the text as `hookSpecificOutput.additionalContext` for `SessionStart`

**P3 — the tests as they stood:** `tests/test_align_hook_sync.py` six tests (`test_current`, `test_behind`, `test_ahead`, `test_diverged`, `test_no_upstream`, `test_fetch_failed`), all on `_repo_sync`, no call to `main()`, no `_standing_constraints` or `_compose_context`.

**P4 — the two interpreters:** `/usr/bin/python3` is Python 3.9.6 (confirmed: `Python 3.9.6`); suite runs under venv 3.12; hook carries `from __future__ import annotations`, no 3.10+ syntax used.

**P5 — the file:** `$ELUVIAN_WRAP_ROOT/STANDING_CONSTRAINTS.md` v1.0, 15 lines; heading `## Standing constraints` at line 5; first numbered line: `1. One commit per lens, the subject naming the lens`; committed at governance `bfe41d9a`.

## Failing-first (eight red, one pinned, then green)

Tests written before the hook edit. Run result: **8 failed, 7 passed**.

- `test_a1_standing_constraints_synthetic` — FAILED: `AttributeError: module has no attribute '_standing_constraints'`
- `test_a1b_standing_constraints_real` — FAILED: `AttributeError: module has no attribute '_standing_constraints'`
- `test_a2_fail_open` — FAILED: `AttributeError: module has no attribute '_standing_constraints'`
- `test_a3_truncation` — FAILED: `AttributeError: module has no attribute '_standing_constraints'`
- `test_a4_compose_with_constraints` — FAILED: `AttributeError: module has no attribute '_compose_context'`
- `test_a5_compose_without_constraints` — FAILED: `AttributeError: module has no attribute '_compose_context'`
- `test_a6_harness_canary` — FAILED: `AssertionError` (subprocess exit 1, `AttributeError: module 'h' has no attribute '_standing_constraints'`)
- `test_a7_injected_present` — FAILED: `AssertionError: '## Standing constraints' not in ctx` (today's hook lacks the heading)
- `test_a8_injected_absent` — **PASSED** (GREEN before the edit: today's hook lacks the heading, so the assertion `'## Standing constraints' not in ctx` is trivially true — pins the fail-open shape)
- Six sync tests — PASSED

After hook edit: **15 passed, 0 failed** (file-only run), then **2217 passed, 1 skipped** (full suite).

## The harness-interpreter canary (Item 3)

```
env -u ELUVIAN_WRAP_ROOT /usr/bin/python3 -c "import importlib.util,sys,pathlib; sys.path.insert(0,'hooks/eluvian'); s=importlib.util.spec_from_file_location('h','hooks/eluvian/eluvian_align_hook.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); r=m._standing_constraints(m._GOV_ROOT); print(type(r).__name__, len((r or '').splitlines()))"
```

Output: `str 10` — heading line + nine constraint lines; `splitlines()` count (not newline count). `/usr/bin/python3` is 3.9.6; `from __future__ import annotations` covers the type hint in `_standing_constraints`; no 3.10+ syntax.

## Mutation run

Manifest: `knowledge/mutants/align-hook-standing-constraints.json` — 6 mutants, target `hooks/eluvian/eluvian_align_hook.py`.

```
MUTANT cap-removed: KILLED — suite caught the defect
MUTANT except-reraises: KILLED — suite caught the defect
MUTANT heading-dropped: KILLED — suite caught the defect
MUTANT composer-drops-constraints: KILLED — suite caught the defect
MUTANT absent-line-dropped: KILLED — suite caught the defect
MUTANT main-forces-none: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: hooks/eluvian/eluvian_align_hook.py sha256=5cd7dfb25b53

MUTATION: 6 killed, 0 survived, 0 error
```
