# Dev log — classify-deposit — 2026-09-14

## Pins re-derived (P1, P2, P3, P4)

P1 — `depositor.py` (905 lines): the module level puts `scripts/` on `sys.path` :23–25 and imports `cycle_check`, `gates`, `lifecycle` and `status` :27–30 (`notifier` optional :31–34); `class Depositor` :55; `__init__(self, *, disk_preflight_fn, shutting_down_check, config, lifecycle_db_path)` :65 stores the four, a lock and `resolve_bellows_root()` :67–73; `_parse_plan(self, plan_text)` :253 calls `cycle_check.parse_manifest_stanza` :254, splits `writes` and `reads` on commas :262 and :265, takes `class` unless `<declare>` :266–268, falls back to `gates._extract_plan_required_deposits` :271 and `gates._extract_plan_scope` :273, and returns `writes, reads, declared_class` :276; `_infra_projects` :282 is the floor :46–48 with `config["shop_infra_projects"]` added; `_resolve_write` :296 reads `resolve_governance_root()` and `resolve_projects_parent()` :331–332; `_assign_class(self, writes, project_root)` :409 has no default; no `__main__` and no `argparse`; `lifecycle.py`'s top level sets `logger` :19 and `LIFECYCLE_DB_PATH` :21 — no connection

P2 — `scripts/cycle_check.py`: `MANIFEST_HEADING_RE = re.compile(r"^## Cycle Manifest\s*$", re.MULTILINE)` :56; `parse_manifest_stanza(plan_text)` :639 returns `{}` when the heading is absent; the stanza ends at the next line starting `## ` or `---` :647; a blank line is skipped; a line starting with two spaces continues the current field :657–660; a stripped line matching `^(\w[\w_]*):\s*(.*)` starts a field :661–665; any other line is skipped with no record, so a wrapped `writes:` value leaves only a shorter list.

P3 — `tests/test_tools_safe_to_invoke.py`: `_WRITE_NAMES` :20–23; `_py_files()` :33–34 globs `tools/*.py` and `scripts/*.py`; t1 `test_no_absolute_home_paths` :122; t2 `test_no_import_time_writes` :131; t3 `test_help_does_no_work` :140; t4 `test_writers_refuse_without_out` :179; t5 `test_every_module_parses_under_python39` :219; t6 `test_no_def_time_union_without_future_import` :310. All six passed with the new tool in their globs.

P4 — `tests/test_depositor_class_assigner.py`: root and `scripts/` on `sys.path` :23–25; `import bellows_root as br_mod`, `import depositor as dep_mod` :27–28; `_dep(tmp_path, config)` :36–50 builds a Depositor from dummies over a tmp lifecycle.db; `_mini_roots` :53–58; `_shop_roots` :61–65; resolvers patched as `monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)` and same for `resolve_projects_parent` :86–87.

No mechanism mismatch found. `tools/classify_deposit.py` was absent. `depositor.py` has no `__main__` or `argparse`. `_parse_plan` returns `(writes, reads, declared_class)`. `_assign_class` has no default for `project_root`.

## Failing-first (red, then green)

Red (tool absent): `8 failed in 0.25s`

Green (test file, c1–c8): `8 passed in 0.18s`

Green (safety suite, t1–t6 with new tool in globs): `6 passed in 3.14s`

Green (full suite): `2372 passed, 2 skipped, 9 warnings in 229.26s (0:03:49)`

## The results observed (c1–c4)

tests/test_classify_deposit.py::test_c1_match PASSED
tests/test_classify_deposit.py::test_c2_mismatch PASSED
tests/test_classify_deposit.py::test_c3_fallback PASSED
tests/test_classify_deposit.py::test_c4_unparsed_stanza PASSED

## Mutation run

MUTATION: 7 killed, 0 survived, 0 error
