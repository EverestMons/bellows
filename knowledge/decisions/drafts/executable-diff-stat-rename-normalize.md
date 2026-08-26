# bellows — executable: `_parse_diff_stat` learns renames — the poisoned-input root of the scope_check rename hole, fixed at the parser

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the new tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's batch-3 proceed; the walk-0 root-cause (the hole is the parser's verbatim pass-through, not scope_check's matching); the REAL rename forms captured live from an actual git mv (the fixtures).

## Why this exists

A plan that renames a file today ships a `files_changed` entry no Scope block can match — scope_check either false-fails or, with the arrow literal never matching a real path, silently loses the move from the audit. Normalizing at the parser fixes every downstream consumer at once.

## Numbers discipline

⚠️ **Measured 2026-08-26; re-measure pre-flight; mismatch → HALT; counts carry measure-record-supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| D1 | the parser | `def _parse_diff_stat` count-1 in bellows.py; its loop's `filename = filename.strip()` line count-1 within the function | `bellows.py` (repo-relative — worktree law) |
| D2 | the fixtures | `{a/b => c}/f.md` → `c/f.md`; `top.md => renamed-top.md` → `renamed-top.md` (captured live from a real git mv) | this register's walk 0 |

## STEP 1 — DEV (the normalization + tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f bellows.py && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `/usr/bin/grep -cF -- "rename rendering" bellows.py; true`, (ii) `test -f tests/test_diff_stat_renames.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — the normalization.** In `_parse_diff_stat`, immediately after the line `        filename = filename.strip()` (D1's anchor, count-1 in the function's span), insert EXACTLY:
>
> ```python
>         # Normalize git's rename rendering to the NEW path — a verbatim
>         # "{old => new}/f" or "old => new" literal can never match a Scope
>         # declaration or a real path, which both false-fails scope_check and
>         # silently drops the move from the audit (the scope-check-illusory-
>         # for-renames mechanism, root-caused 2026-08-26). The old path is
>         # deliberately not emitted: files_changed answers "what does the
>         # tree contain now"; the move's audit trail lives in git itself.
>         if " => " in filename:
>             if "{" in filename:
>                 filename = re.sub(r"\{[^{}]* => ([^{}]*)\}", r"\1", filename)
>                 filename = filename.replace("//", "/").lstrip("/")
>             else:
>                 filename = filename.split(" => ", 1)[1].strip()
> ```
>
> (bellows.py already imports `re` — verify with a count probe, HALT if 0.) Post-probes: `"rename rendering"` == 1; `"{[^{}]* => "` present == 1.
>
> **Task C — tests `tests/test_diff_stat_renames.py`** (new): five tests. THREE over the parser with REAL captured output fed as the subprocess result (monkeypatch subprocess.run to return the walk-0 fixture block verbatim — the fixture IS real git output, provenance-commented): brace form → `c/f.md` in the result and NO `{` in any entry; bare form → `renamed-top.md`; a mixed block (both lines + a normal file line) → all three normalized/passed correctly. TWO end-to-end REAL-GIT tests (no mocks): build a tmp repo, `git mv` cross-dir exactly as walk 0 did, call `_parse_diff_stat(pre, post, path)` for real → the new paths, no arrows, no braces; and an empty-prefix brace case (`git mv f.md sub/f.md` renders `{ => sub}/f.md`) → `sub/f.md` (the lstrip guard's case). Targeted run — 0 failed (record counts; supersede with derivation).
>
> **Task D — dev log + commit.** `knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md` (probe raws, targeted raw). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add bellows.py tests/test_diff_stat_renames.py knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] diff-stat-rename-normalize(diff-stat-rename-normalize-2026-08-26): renames normalized to the new path at the parser — scope_check + audit fed clean" -- bellows.py tests/test_diff_stat_renames.py knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `bellows.py`
> - `tests/test_diff_stat_renames.py`
> - `knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md`
>
> **Scope:**
> - `bellows.py`
> - `tests/test_diff_stat_renames.py`
> - `knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + the live-repo replay)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs 1517 + 5).
> **Item 2 — the live-repo replay.** A scratch tmp repo, a real cross-dir `git mv`, the COMMITTED parser imported and called → paste the returned list (new paths only, zero entries containing ` => ` or `{`). Extraction probes on `git show`: the two Task-B probes; `cmp` vs live → 0 each. Raw → `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/probes-raw.txt`.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section; the daemon-staleness caveat stated (bellows.py is live daemon code — the fix arms at the next restart).
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one insertion at the single choke point; real-git fixtures at both DEV and QA; the manifest-pin remains the move guard until a daemon restart arms this (stated).

**Walk register:** `bellows/knowledge/research/walk-register-diff-stat-rename-normalize-2026-08-26.md`

**Walk 0 (context pin, measured):** the root cause located at the parser (not scope_check); the two real rename forms captured live; the new-path-only law with its reason; daemon staleness stated.

**Walks:**
- Weak spots:          w1 dry — the regex traced by hand over all three fixture shapes incl. the empty-prefix (`{ => sub}/f.md` → `sub/f.md`) and empty-suffix (`{a => }/f.md` → the lstrip guard) arms; the strip()-anchor count-1 and `import re` both verified live at authoring.
- Destruction:         w1 dry — a pure per-line transform on the parser's own loop variable; every non-arrow line untouched by the ` => ` guard.
- Vulnerabilities:     w1 dry — new-path-only stated with its reason; downstream consumers (scope_check, audit) receive strictly more matchable paths, never fewer.
- Integration-record:  w1 dry — the scope-check-illusory memory's mechanism located and cited; its disposition rides the batch-close triage; daemon staleness stated at three sites.
- ACID:                w1 dry — counts clause-clothed; one pathspec-limited commit.
- **Walk 1 total: 0 findings — all five lenses dry.**
- Weak spots:          w2 dry.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/bellows.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py
writes: bellows.py, tests/test_diff_stat_renames.py, knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md, knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/pytest_full.txt, knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/probes-raw.txt, knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/qa-receipt.md
open_forks: the 23-row re-queue TRIAGE at batch close (a report to the CEO, not a plan); the daemon restart arming 564+567 (deliberate, /eluvian-surfaced); the scope-check-illusory memory's disposition rides the triage
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
