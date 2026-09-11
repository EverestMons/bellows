# Dev-log — what-works definition diagnostic (100072, thread 263)
**Date:** 2026-09-11 | **Plan:** diagnostic-100072 | **Step:** 1 (DIAGNOSTIC) | **pause_for_verdict:** after_step_1

Scratch env: `T=/tmp/what-works.J4OiGk` — venv with `datasketch==2.0.0`, scratch DB built by `anvil/scripts/reprice_bellows_build.py --checkout /Users/marklehn/Developer/bellows --tmp $T`. Bellows analysed at `main` (`cc58328`). Governance at `c16b6f2c`. Anvil at `a1910df`.

## Pins re-derived (P2, P3)

P2 (verbatim from the plan's pin cell):

> `anvil-reprice-2026-09-09.md` Q5: "Reference set … 14 names total", eight from the archetype's name rules — `run_plan`, `run_step`, `_teardown_worktree`, `notify_*`, `check_verdict`, `_consume_verdicts`, `validate_at_claim`, `extract_decision_blocks`; the walk-0 definition found 2 of 14 (`runner.py::run_step`, `parser.py::parse`); excluded by its volatility filter: `bellows.py::run_plan`, `gates.py::check`, `lifecycle.py::init_lifecycle_db`, `depositor.py::_assign_class`; the CEO's ruling: hubs kept

P3 re-derived — scratch DB rebuilt at `cc58328` vs P3 pin at `1365acc`. Counts that moved are reported as both figures (bellows moved — not a mechanism mismatch):

| metric | P3 (1365acc) | rebuilt (cc58328) |
|--------|-------------|-------------------|
| code_chunks function | 744 | 775 |
| code_chunks method | 56 | 56 |
| code_chunks class | 221 | 236 |
| code_chunks test_case | 1994 | 2065 |
| chunk_dependencies call cross_file | 4076 | 4310 |
| chunk_dependencies call within_file | 2495 | 2566 |
| chunk_dependencies import | 319 | 340 |
| tests bindings total | 3188 | 3308 |
| tests bindings with target | 1207 | 1256 |
| functional_role utility (fn+method) | 506 | 521 |
| functional_role cli_script | 107 | 123 |
| functional_role plan_dispatcher | 60 | 60 |
| functional_role gate_checker | 39 | 39 |
| functional_role notifier | 27 | 27 |
| functional_role verdict_handler | 14 | 14 |
| functional_role agent_lifecycle | 14 | 14 |
| functional_role plan_validator | 11 | 11 |
| functional_role plan_parser | 7 | 7 |
| functional_role worktree_manager | 5 | 5 |
| functional_role config_loader | 4 | 4 |
| functional_role cache_manager | 4 | 4 |
| functional_role data_model | 2 | 2 |
| functional_roles.scoring_weights empty | 13/13 | 13/13 |
| production defs (AST FunctionDef+AsyncFunctionDef) | 588 | 581 |

Production file count: 55 (unchanged). One AST parse error: `tools/cycle_log_projection_census.py` (f-string syntax at line 187; 0 tokens contributed to R).

daemon.py (anvil archetype): `NAME_RULES` 45 regex→role pairs confirmed. `FILE_PATH_RULES` at line 75. `DECORATOR_RULES` empty. `SCORING_WEIGHTS` defined in daemon.py source but not reflected in DB `functional_roles.scoring_weights` column (all 13 rows empty in the DB — the DB does not store these weights).

## The reference set (Q1)

Token rule: backticked `` `name(` `` or `` `mod.name(` `` from four sources; a name joins only if it resolves to a `def` in the 55 production files at HEAD.

| source | tokens | resolved | R members added |
|--------|--------|----------|----------------|
| CLAUDE.md | 3 | 3 | 3 |
| GLOSSARY.md | 17 | 6 | 6 |
| LESSONS.md | 46 | 11 | 9 (2 overlap) |
| daemon.py | 0 | 0 | 0 (no backtick callable notation in archetype body) |

**\|R\| = 12.** 16 of 33 R+ members with score_b = 0 (formula consequence — stable_commits = 0).

R+ = R ∪ P2 control expanded: |R+| = 33 (P2's "14 names" before notify_* expansion and R union; 33 after). Four P2 hubs all in R+: run_plan (P2_control only), gates::check (sources + P2_control), init_lifecycle_db (P2_control only), _assign_class (LESSONS.md + P2_control).

## Q1–Q6 in one table

| definition | formula | P@33 | R@33 | P@20 | R@20 | hub ranks (run_plan / gates::check / init_lifecycle_db / _assign_class) |
|------------|---------|------|------|------|------|------------------------------------------------------------------------|
| walk-0 (P2, 14-name set) | stable/bound/reused, volatility filter | — | 0.143† | — | — | excluded (volatility filter) |
| (a) import-verified inbound | verified_inbound | 0.333 | 0.333 | 0.450 | 0.273 | 7 / 3 / 1 / 5 |
| (b) survived | age_days × (1+tests_bound) × stable_commits | 0.242 | 0.242 | 0.350 | 0.212 | 1 / 3 / 10 / 127 |
| (b') survived+1 | age_days × (1+tests_bound) × (1+stable_commits) | 0.242 | 0.242 | 0.350 | 0.212 | 1 / 3 / 11 / 287 |
| (c) role-weighted | score_a × role_weight | **0.394** | **0.394** | **0.450** | **0.273** | 3 / 1 / 4 / 10 |

†walk-0 R@ is over a 14-name set; (a)/(b)/(c) are over 33-name R+. The comparison is directional.

Best: **(c)** — R@33 = 0.394 (13 of 33 R+ members in top 33). (b') does not rank above (b) at either K.

Score_b wall-clock: 8.8 s for 581 traces (P5 ~12 s for 588 — consistent). git_fails: 0.

Pooled verification rate (a): verified=2394 / total=3538 = 0.677. Path-loaded: 177. Unverified: 967.

Sensitivity (a→c): 4 top-20 positions moved. `validators.py::validate_at_claim` entered; `depositor.py::evaluate` left.

Top-5 under (c): `gates.py::check` (160.0), `verdict.py::slug_from_path` (110.0, not in R+), `bellows.py::run_plan` (104.0), `lifecycle.py::init_lifecycle_db` (101.0), `bellows.py::_consume_verdicts` (100.0).

Deposits: `what-works-definition-2026-09-11.md` and `what-works-definition-2026-09-11.tsv` → governance (Planner-commit); this dev-log → bellows commit.

## What the doc does not establish

- A reference set of 33 moves in steps of 1/33 ≈ 0.030; a one-member difference separates best from second-best.
- The sources name rules and lanes, not functions, by design; that bounds what precision/recall over this set can say.
- Role weights are the Planner's, not the archetype's (DB `scoring_weights` empty on all 13 rows).
- `-L` does not follow renames; `age_days` is bounded by the file's history under its current path.
- Import verification passes same-named functions in different imported modules (P4's name-collision class).
- Scratch DB built once, one repo, one language.
- R@33 = 0.394 is the best of three definitions over this set; whether that recall is sufficient is the CEO's threshold, not set here.
- `lifecycle.py::init_lifecycle_db` is classified as `utility` (no file_path rule for `lifecycle.py` in the archetype); a daemon-core classification would double its score_c to 202.0 and place it first.
