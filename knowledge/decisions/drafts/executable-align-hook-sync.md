# bellows — executable: the align hook gains a bounded fetch-and-report sync arm (SessionStart tells every machine where it stands)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** bellows suite (`python3 -m pytest tests/`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's multi-machine directive this session + the assessment's recommended hardening (hook FETCHES and REPORTS; /eluvian PULLS — plan 548's step 1 stays the deliberate act); the measured divergence this wrap (root behind 11 / bellows behind 2, found only at fetch time).

## Why this exists

A machine that starts on stale state cannot tell — the SessionStart block reports daemon and parked arcs but nothing about git freshness. A bounded fetch (never a pull: a fetch mutates nothing) plus a problems-only report line closes the blindness at the moment it matters, on every machine, with the existing env-override portability.

## What this plan does NOT do

- No pulls, merges, or any working-tree mutation from the hook — report only; the FAIL-OPEN contract is preserved (every new call is inside the existing try/except and its own bounded timeouts).

## Numbers discipline

⚠️ **Measured 2026-08-26 at authoring; Step 1 re-derives — yours supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| S1 | the hook | 111 lines; sha-prefix `cf3184e91eb58920046c`; FAIL-OPEN wrapper at main | `hooks/eluvian/eluvian_align_hook.py` (repo-relative — worktree law) |
| S2 | insertion anchor | `parts.append("Type /eluvian for the full alignment pass.")` count-1 | ibid. |
| S3 | test baselines | hook tests 32 passed; full suite 1470 collected | `tests/` |

## STEP 1 — DEV (the arm + the test file, targeted run)

> **Task A — worktree discipline + state branch.** ⚠️ Your cwd IS the claimed tree — never cd to `/Users/marklehn/Developer/GitHub/bellows`. Open: `cd "$(git rev-parse --show-toplevel)" && test -f hooks/eluvian/eluvian_align_hook.py && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `/usr/bin/grep -cF -- "_repo_sync" hooks/eluvian/eluvian_align_hook.py; true`, (ii) `test -f tests/test_align_hook_sync.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → skip to Task D's commit-check; (0,1) → impossible, HALT.
>
> **Task B — the sync arm.** In `hooks/eluvian/eluvian_align_hook.py`: (1) insert BEFORE the `def _daemon_status():` line (anchor count-1) the following two functions EXACTLY (docstrings included):
>
> ```python
> _SYNC_TIMEOUT = 5
>
>
> def _sync_repos():
>     """Core repos to freshness-check, by existence (machine-portable)."""
>     repos = [("root", _GOV_ROOT),
>              ("bellows", _STATUS_PY.parent),
>              ("lessons-forge", _GOV_ROOT / "lessons-forge")]
>     mem = os.environ.get("ELUVIAN_WRAP_MEMORY")
>     if mem:
>         repos.append(("memory", Path(mem)))
>     return [(l, p) for l, p in repos if (p / ".git").exists()]
>
>
> def _repo_sync(label, path):
>     """Bounded fetch + upstream compare. REPORT ONLY — never mutates the tree.
>     Returns (label, state); state: current | ahead N (unpushed) | BEHIND N |
>     DIVERGED (ahead A, behind B) | no upstream | fetch FAILED[...]."""
>     def _git(*args):
>         return subprocess.run(
>             ["git", "-C", str(path), *args],
>             capture_output=True, text=True, timeout=_SYNC_TIMEOUT,
>             env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
>         )
>     try:
>         fetch_failed = _git("fetch", "origin", "--quiet").returncode != 0
>         r = _git("rev-list", "--count", "--left-right", "HEAD...@{u}")
>         if r.returncode != 0:
>             return (label, "fetch FAILED" if fetch_failed else "no upstream")
>         ahead, behind = (int(x) for x in r.stdout.split())
>         if fetch_failed:
>             return (label, f"fetch FAILED (stale view: ahead {ahead}, behind {behind})")
>         if ahead and behind:
>             return (label, f"DIVERGED (ahead {ahead}, behind {behind})")
>         if behind:
>             return (label, f"BEHIND {behind}")
>         if ahead:
>             return (label, f"ahead {ahead} (unpushed)")
>         return (label, "current")
>     except Exception:
>         return (label, "fetch FAILED")
> ```
>
> (2) Replace the anchor line `    parts.append("Type /eluvian for the full alignment pass.")` (count-1, leading four spaces exact) with:
>
> ```python
>     sync = [_repo_sync(l, p) for l, p in _sync_repos()]
>     problems = [(l, s) for l, s in sync
>                 if s != "current" and not s.startswith("ahead")]
>     if problems:
>         parts.append("⚠️ Sync: " + "; ".join(f"{l} {s}" for l, s in problems)
>                      + " — run /eluvian to pull (ff-only) or resolve deliberately")
>     else:
>         unpushed = [f"{l} {s}" for l, s in sync if s.startswith("ahead")]
>         parts.append("Sync: core repos current"
>                      + (f" ({'; '.join(unpushed)})" if unpushed else "."))
>     parts.append("Type /eluvian for the full alignment pass.")
> ```
>
> (3) Replace the hooklog anchor `hooklog("SessionStart-align", f"parked={parked}")` (count-1) with `hooklog("SessionStart-align", f"parked={parked} sync={sync}")`. Post-probes: `"_repo_sync"` count >= 3 AND `"REPORT ONLY"` == 1 AND `"Type /eluvian for the full alignment pass."` == 1 (moved, not duplicated). Smoke: `python3 hooks/eluvian/eluvian_align_hook.py < /dev/null | head -c 400` prints valid JSON containing `"Sync:"` (paste raw; network state varies — ANY reported state is the pass, the arm REPORTING is what is probed).
>
> **Task C — the test file `tests/test_align_hook_sync.py`** (new): six tests over `_repo_sync` against REAL temp git repos in tmp_path (bare origin + `git clone`; commit identity via `-c user.email=t@t -c user.name=t`): current; origin gains a commit (pushed from a second clone) → `BEHIND 1`; local commit → `ahead 1 (unpushed)`; both → `DIVERGED (ahead 1, behind 1)`; no upstream — a working clone with `git branch --unset-upstream` (⚠️ NOT init-without-remote: there fetch fails FIRST and the state reads `fetch FAILED`; walk-1 A1) → `no upstream`; origin URL re-pointed at a nonexistent path → state startswith `fetch FAILED`. Import via `sys.path.insert` of `hooks/eluvian`; NO mocks on git. Targeted run: `python3 -m pytest tests/test_align_hook_sync.py tests/test_wrap_hooks.py --tb=short -q 2>&1 | cat` → **38 passed** expected (32 baseline + 6 new; measured supersedes with derivation), 0 failed; paste raw.
>
> **Task D — dev note + commit.** `knowledge/dev-logs/align-hook-sync-dev-2026-08-26.md` (branch taken, smoke JSON, targeted raw). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add hooks/eluvian/eluvian_align_hook.py tests/test_align_hook_sync.py knowledge/dev-logs/align-hook-sync-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] align-hook-sync(align-hook-sync-2026-08-26): SessionStart fetch-and-report arm (bounded, report-only, fail-open) + 6 real-git tests" -- hooks/eluvian/eluvian_align_hook.py tests/test_align_hook_sync.py knowledge/dev-logs/align-hook-sync-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**; separate: numstat — exactly the three files.
>
> **Deposits:**
> - `hooks/eluvian/eluvian_align_hook.py`
> - `tests/test_align_hook_sync.py`
> - `knowledge/dev-logs/align-hook-sync-dev-2026-08-26.md`
>
> **Scope:**
> - `hooks/eluvian/eluvian_align_hook.py`
> - `tests/test_align_hook_sync.py`
> - `knowledge/dev-logs/align-hook-sync-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/align-hook-sync-2026-08-26/pytest_full.txt` → expected **1476 passed** (1470 collected baseline + 6 new; warnings tolerated, failures NOT — any failure HALTs with raw output; measured count supersedes with derivation).
> **Item 2 — extraction probes.** `git show <CAPTURE_COMMIT>:hooks/eluvian/eluvian_align_hook.py` (⚠️ braced `${VAR}:path` — the zsh colon-modifier trap): `"_repo_sync"` >= 3; `"REPORT ONLY"` == 1; `"GIT_TERMINAL_PROMPT"` >= 1; `"Type /eluvian for the full alignment pass."` == 1; `cmp` vs live → 0. Test-file extraction: `"def test_"` count == 6. Raw → `knowledge/qa/evidence/align-hook-sync-2026-08-26/probes-raw.txt`.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/align-hook-sync-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table + the Rule 20 block.
>
> ⚠️ **Gate note:** this QA HAS a pytest summary (`pytest_full.txt` named above) — the gate should PARSE it; no benign override pre-declared. A gate failure is REAL.
>
> **Deposits:**
> - `knowledge/qa/evidence/align-hook-sync-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/align-hook-sync-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/align-hook-sync-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/align-hook-sync-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/align-hook-sync-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/align-hook-sync-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's verification section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one hook arm + real-git tests; the FAIL-OPEN contract preserved by construction (every new call bounded and inside the existing wrapper); report-only stated at three sites.

**Walk register:** `bellows/knowledge/research/walk-register-align-hook-sync-2026-08-26.md`

**Walk 0 (context pin, measured):** hook 111 lines sha-pinned, FAIL-OPEN wrapper verified; insertion anchors count-1; baselines 32/1470; design notes (a)–(e) incl. the mini's non-git memory dir skipped by the existence test; id prediction 554.

**Walks:**
- Weak spots:          w1 1 folded — (A1) the "no upstream" test was shaped as init-without-remote, where fetch fails FIRST and the reachable state is `fetch FAILED`: the test would fail on CORRECT code. Re-shaped to unset-upstream on a working clone (fetch rc=0, `@{u}` unresolvable).
- Destruction:         w1 dry — three-arm resume table; all writes land in one commit.
- Vulnerabilities:     w1 dry — report-only stated at three sites; every call bounded + inside the FAIL-OPEN wrapper; `@{u}` is a literal argv token, no shell.
- Integration-record:  w1 dry — the smoke's any-state-is-a-pass clause matches network variability honestly; latency worst case declared at walk 0 (f).
- ACID:                w1 dry — 38 = 32 + 6 and 1476 = 1470 + 6, both with the supersede clause.
- **Walk 1 total: one finding, folded.**
- Weak spots:          w2 dry — the re-shaped test traced through the code path by hand.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/hooks/eluvian/eluvian_align_hook.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/eluvian_align_hook.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py
writes: hooks/eluvian/eluvian_align_hook.py, tests/test_align_hook_sync.py, knowledge/dev-logs/align-hook-sync-dev-2026-08-26.md, knowledge/qa/evidence/align-hook-sync-2026-08-26/pytest_full.txt, knowledge/qa/evidence/align-hook-sync-2026-08-26/probes-raw.txt, knowledge/qa/evidence/align-hook-sync-2026-08-26/qa-receipt.md
open_forks: the verdict slug-keying diagnostic + plan (next, SERIAL — the last of the CEO's three)
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
