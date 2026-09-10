# dev-log: diagnostic-bellows-anvil-reprice — 2026-09-09 [100057, thread 255]

**Plan:** `diagnostic-bellows-anvil-reprice` | **Bellows HEAD at build:** 1365acc | **Anvil HEAD:** caf7efc | **Scratch dir:** $T (mktemp /tmp/anvil-reprice.XXXXXX); cleaned after commit.

---

## Pins re-derived (P1, P3)

**P3 verbatim (sha files prod_defs chunks deps untouched later_touched unbound):**
`53e7146 2 9 9 0 0 0 9` / `cfb968e 4 2 2 3 1 0 0` / `f5c82a4 8 26 26 128 111 0 10` / `99d24c1 1 0 0 0 0 0 0` / `df6acd3 2 0 0 0 0 0 0` / `410bcd0 10 6 6 29 2 2 3` / `54e8b85 4 1 1 78 28 0 0` / `91354d2 9 15 13 193 160 1 2` / `492f50d 3 8 8 100 86 1 1` / `9ffb96c 4 4 4 48 42 4 2`

P3 re-derived from `reprice_bellows_analyze.py --checkout /Users/marklehn/Developer/bellows --db $T/anvil-scratch.db --tsv $T/anvil-reprice-2026-09-09.tsv --control 601f5b9 34eeab2`: table matches P3 pins exactly (all 10 rows, all 8 columns).

**P1 re-derived from `reprice_bellows_build.py --checkout /Users/marklehn/Developer/bellows --tmp $T`:**

| metric | pin | re-derived | match |
|--------|-----|-----------|-------|
| files_total | 5014 | 5016 | +2 (worktree plan files in scan scope — filesystem read, not git; files_processed still 162) |
| git_commits_ingested | 972 | 972 | ✓ |
| files_processed | 162 | 162 | ✓ |
| chunks total | 3015 | 3015 | ✓ |
| dependencies_resolved | 6890 | 6890 | ✓ |
| similarities_found | 153 | 153 | ✓ |
| classify classified | 1021 | 1021 | ✓ |
| avg_composite | 0.2743 | 0.2739 | ~, rounding |
| tests bindings / with target | 3188 / 1207 | 3188 / 1207 | ✓ |
| coverage dist 0.2/0.5/1.0 | 119/67/405 | 119/67/405 | ✓ |
| roles utility | 720 | 720 | ✓ |
| anvil suite | 262 passed in 1.33s | 262 passed in 10.03s | 262 ✓, time differs (hardware) |

The +2 in files_total is the worktree's plan branch files. All production-relevant counts are exact.

---

## Instrument deposited (two scripts, writers forbidden by name)

Both scripts extended from walk-0 stubs (committed at `183e85c` by the Planner):

- `/Users/marklehn/Developer/anvil/scripts/reprice_bellows_build.py` — added `argparse` (`--checkout`, `--tmp`), in-process path patches moved into `main()`, temp-dir assert before DB open, DB path printed on exit.
- `/Users/marklehn/Developer/anvil/scripts/reprice_bellows_analyze.py` — added `argparse` (`--checkout`, `--db`, `--tsv`, `--control`), temp-dir assert for DB path, `evidence` column in TSV rows, `later_sha` and `class` per untouched dependent, STANDARD_GATES check, Q3 resolver block print, stable/bound/reused ranking with and without non-source dirs, clone pair detail, complexity hotspots, TSV writer.

Post-condition verified: `grep -cE '^(from|import) .*\b(run_lab|run_cycle)\b'` = 0 for both scripts. Docstrings NAME the forbidden writers; the grep counts import-line occurrences only, which is 0.

Both scripts are Planner-commit deposits (outside bellows). Written in-place in the anvil checkout. The Planner commits them at the wrap.

---

## Q1–Q7 in one table

| Q | question | answer | key number |
|---|----------|--------|------------|
| Q1 | Dependents-untouched yield over 10 DEV commits: how many MISS? | 0 confirmed MISS / 8 later-touched instances / 430 untouched rows across 10 commits; hub (×3), new-test (×4), planned (×1 — get_coverage, plan 100056 confirmed) | 0/8 MISS |
| Q2 | Positive control: does graph flag `test_gate_transaction_mechanization.py` and `dashboard.py` consumers? | YES for both 601f5b9 (7 untouched, includes test_gate_transaction_mechanization.py) and 34eeab2 (2 untouched: assemble_state + render_screen, both later touched by 751ab87); STANDARD_GATES not a chunk (module-level constant, no `defines` binding) | control passes for function-level consumers |
| Q3 | Edge precision under name-only resolver | dashboard.py::run: 0/40 (0%); gates.py::check: 5/11 (45%); generic names are noise; files_total 5016 vs 162 tracked .py files (scan inflation: all markdown/logs registered as module chunks) | 0% for generic names |
| Q4 | tests-for bindings vs QA receipts | unbound counts correct for newly-added functions; zero-gaps in June cycle 2 explained by conjunction predicate: complex functions had tests, unbound functions were simple (composite < 0.7); current DB: 405 unbound but only 2 pass both predicates | find_coverage_gaps: 2 of 405 in current build |
| Q5 | Stable/bound/reused ranking vs shop exemplars | runner.py::run_step (#2→#1 after excl) and parser.py::parse (#2→#1) match reference set; run_plan, gates.check, init_lifecycle_db, _assign_class absent (volatility > 0.2 or coverage=1.0); #1 as-built is a knowledge-dir census script | 2/14 reference names in top-20 |
| Q6 | Clone pairs classified | 19 prod pairs: 18 real (hook utility copy-paste: _default_root, hooklog, emit, _validate_session_id; strip_fenced_code_blocks 3-way near-clone), 1 fixture (knowledge-dir QA matcher pair) | 18 real / 1 fixture |
| Q7 | Hotspots vs LESSONS.md; cost | Top hotspot: plan_lint::lint (0.848); bellows core: _apply_ledger_updates (#2, 0.781), run_plan (#3, 0.696); _teardown_worktree (8 LESSONS mentions) not in top-10; build cost: scan 2.0s + extract 40.8s + score 0.5s; pre-check shape: ~43s build + <5s query per commit | build 43s total |

---

## What the doc does not establish

- One repo, one language; generalization not measured.
- Name-matched edges are an upper bound; Q1's untouched counts overstate the true signal for generic names.
- The chunk-match in Q1 uses bare name, not qualname; same-name nested functions produce multiple IDs.
- STANDARD_GATES-class misses (module-level constants) are not counted by the graph.
- Later-touched classifier uses commit subject only; confirmed `planned` reclassification for get_coverage required reading the Done plan record.
- Build uses live filesystem, not per-commit snapshot; graph reflects HEAD state for all commits.
