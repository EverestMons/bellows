# Dev Log — what-works-generator — 2026-09-11

Plan: executable-100075 | Step 1 (DEV) | Thread 263

## Pins re-derived (P1, P2, P5, P6)

P3 verbatim: `what-works-definition-2026-09-11.md`: Q2 formula `:108` (cross-file call edges whose caller imports the target's module), the tie rule `:179`, Q3 `:194–198` (`score_b`, the birth, the signature-line regex), the formula's consequence `:203–205` (412 of 581 defs birth-only), (c) `:260–265` (`score_c = score_a × weight(role)`; the weight table the Planner's; `P@33=0.394 R@33=0.394 P@20=0.450 R@20=0.273 hits@20=9`), the sensitivity `:322` (all weights 1.0 → (a); 4 top-20 positions moved); R+ = 33 members, the Q1 table `:49–103` (37 table rows including the header and R's 12); hubs under (c): `gates.py::check` 1, `run_plan` 3, `init_lifecycle_db` 4, `_assign_class` 10

**P1 re-derived:** `anvil/src/config.py:6` `ANVIL_ROOT = "/Users/marklehn/Developer/GitHub/anvil"` (hardcoded); `:8` `ANVIL_RUNTIME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` (already the checkout); `:10` `ANVIL_DB_PATH = os.path.join(ANVIL_ROOT, "anvil.db")`; `:14` and `:19` the two `SCAN_TARGETS` paths under `/Users/marklehn/Developer/GitHub/`; consumers: `classifier.py:14,73`, `cycle.py:15,65`, `extractor.py:18,42`, `scorer.py:18,359`, `lab.py:19,27,66,109`, `scanner.py:21–27,37,40,128,132–133`. No `PROJECTS_PARENT` present. No `what_works` module. No `build_scratch_db` in `reprice_bellows_build.py`. Mechanism mismatch: NONE.

**P2 re-derived:** 15 test files, 279 `def test_` functions. No `conftest.py`. Baseline: `262 passed in 10.25s` (recorded before any edit; `$T/venv` with `datasketch==2.0.0`).

**P5 re-derived:** `watched_projects = [tuyere, bellows, forge_lessons]` — anvil NOT a lane. `git -C anvil log -1 --format=%h` = `a1910df`. `git -C anvil status --porcelain` = clean before edits.

**P6 re-derived:** `build_scratch_db` not yet factored in `reprice_bellows_build.py` (confirmed with `grep`). `mutation_check.py --help` available at `tools/mutation_check.py`.

**T path:** `/tmp/what-works-gen.1kii1f` — venv at `$T/venv` with `datasketch==2.0.0` and `pytest` (pip version warning; datasketch 2.0.0 installed successfully).

## Failing-first (red, then green)

**Red (t1–t12 before edits):** `12 failed in 0.12s` — errors: `AssertionError` (t1: ANVIL_ROOT != ANVIL_RUNTIME_ROOT), `AttributeError: module 'src.config' has no attribute 'PROJECTS_PARENT'` (t2), `ModuleNotFoundError: No module named 'src.what_works'` (t3–t9, t11), `assert 2 != 2` (t10: script absent), `AssertionError: build_scratch_db not found` (t12).

**Green (t1–t12 after edits):** `12 passed in 0.31s`

**Anvil full suite:** `274 passed in 1.50s` (baseline 262 + 12 new tests; no `failed`)

## The anvil tree left for the Planner

```
M scripts/reprice_bellows_build.py
 M src/config.py
?? scripts/what_works.py
?? src/what_works.py
?? tests/fixtures/
?? tests/test_what_works.py
```

(`git -C /Users/marklehn/Developer/anvil status --porcelain`; exactly the six declared paths; `git -C anvil log -1 --format=%h` = `a1910df`)

## Mutation run

`MUTATION: 5 killed, 0 survived, 0 error`

(Full output at `knowledge/mutants/what-works-generator.run.txt`. Two mutants redesigned after initial run: `birth-counts-as-stable` → `stable-commits-uses-raw-length` (birth is always NOT stable in git log -L traces, so the original formulation was unobservable; replaced with raw-length vs stability-checked count); `projects-parent-hardcoded` survived because t2 only checked internal consistency, not the derived value — added `assert cfg.PROJECTS_PARENT == os.path.dirname(cfg.ANVIL_RUNTIME_ROOT)` to t2.)
