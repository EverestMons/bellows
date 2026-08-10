# Dev Log — walk-register-schema Step 2 (2026-08-10)

**Plan:** walk-register-schema-2026-08-10
**Step:** 2 — DEV (the validator and its tests)
**Branch:** bellows-wt/338

---

## Task S2-A0 — guards

| guard | command | result |
|---|---|---|
| Step 1 deposit exists | `ls knowledge/architecture/walk-register-schema.md` | present |
| Step 1 commit names slug | `git log --oneline -- knowledge/architecture/walk-register-schema.md` | `3533e67 [338] step-1: walk-register schema and population measurement` |
| (1) NOT-WIRED | `git status --porcelain -- scripts/plan_lint.py gates.py` | empty |
| (1b) CLEANLINESS | `git status --porcelain -- scripts/ tests/ knowledge/architecture/ knowledge/qa/ knowledge/development/` | empty |

All guards pass. Proceeding.

---

## Task S2-B — the validator

Deposited at `scripts/walk_register_lint.py`.

**B.0 — Input:** accepts a single file path OR a directory to glob `walk-register-*.md`. Usage line states both options explicitly.

**B.1 — Shape cloned from `scripts/cycle_yields.py` (plan 335).** Inherited:
- `STATUS_*` constants as file-level statuses (`PRE-SCHEMA`, `CONFORMANT`, `UNCONFORMANT`, `NO_TABLE`)
- Per-file status to stderr, per-row TSV to stdout
- Unparseable input reported, never skipped
- Standard-library-only, read-only, encoding explicit (`utf-8`)

**B.2 — Per-row conformance marks.** Every fold row emits a `row_status` of `OK` or `WARN`. TSV columns: `file`, `line`, `table`, `row_status`, `file_status`, `columns`, `missing`, `note`. Truncation detection (ellipsis `...` or `…`) marks `WARN` with note `truncated_pre_fold_text`.

**B.3 — Actual columns named.** Each output row carries the table's column shape in the `columns` field. Multi-shape files get each table's own shape. Per-file stderr summary lists all shapes separated by ` ; `.

**B.4 — STATUS PRECEDENCE.** `has_schema_declaration()` is evaluated first. A file with no `**schema_version:**` declaration before the first table is `PRE-SCHEMA` regardless of its table shapes. The check scans line-by-line, stopping at the first table row — `schema_version` appearing only in prose is not a declaration.

---

## Task S2-C — tests

Deposited at `tests/test_walk_register_lint.py`. **19 tests, all using constructed fixtures.**

| test | what it asserts |
|---|---|
| `test_conformant_row` | 2-row conformant register → `CONFORMANT`, all `OK` |
| `test_missing_pre_fold_text_warns` | constructed row with empty `pre_fold_text` → `WARN` fires, `UNCONFORMANT` |
| `test_two_shape_file` | file with 8-column + 3-column fold tables → `UNCONFORMANT`, 2 shapes reported |
| `test_no_table_file` | prose-only file with schema declaration → `NO_TABLE` |
| `test_pre_schema_status` | file with fold table but no declaration → `PRE-SCHEMA` |
| `test_pre_schema_multi_shape` | multi-shape pre-schema file → shapes still reported |
| `test_schema_version_in_prose_is_pre_schema` | `schema_version` only in prose → `PRE-SCHEMA` |
| `test_pipe_escape_round_trip` | `foo\|bar` → `\|` escaped, unescaped back to `\|` byte-identical |
| `test_backslash_escape_round_trip` | `foo\\bar` → `\\` escaped, unescaped back byte-identical |
| `test_backslash_pipe_escape_round_trip` | `foo\\\|bar` — the ambiguity case — round-trips byte-identical |
| `test_unescaped_pipe_corrupts_row` | escaped pipe → 8 cells (correct); unescaped → 9 cells (corrupted) |
| `test_addition_literal_conformant` | `ADDITION` in `pre_fold_text` → `OK`, `CONFORMANT` |
| `test_empty_pre_fold_text_warns` | empty `pre_fold_text` (not ADDITION) → `WARN` |
| `test_truncated_pre_fold_text_warns` | ellipsis in `pre_fold_text` → `WARN` with `truncated_pre_fold_text` |
| `test_non_fold_tables_skipped` | `\| field \| required \| meaning \|` and `\| lens \| folded \| note \|` → skipped |
| `test_normalize_column_strips_markdown` | bold, backticks, hyphens → normalized |
| `test_is_fold_table_positive` | 3 known fold-table shapes → detected |
| `test_is_fold_table_negative` | 3 known non-fold shapes → rejected |
| `test_directory_glob` | glob picks `walk-register-*.md`, skips `not-a-register.md` |

All 19 passed.

---

## Task S2-D — corpus run

### D.1 — PRE-SCHEMA baseline (two files)

| file | blob | status | fold tables | distinct shapes | fold rows |
|---|---|---|---|---|---|
| `walk-register-group4-rescope-2026-08-10.md` | `ef2fa9e` | `PRE-SCHEMA` | 21 | 2 (`\| # \| sub-q \| finding \| fold \|`, `\| # \| finding \| fold \|`) | 130 |
| `walk-register-lint-class-recall-2026-08-10.md` | `7e70716` | `PRE-SCHEMA` | 7 | 3 (`\| # \| sub \| finding \| resolution \|`, `\| # \| finding \| resolution \|`, `\| # \| lens \| finding \| resolution \|`) | 25 |

Both are `PRE-SCHEMA` — no `schema_version` declaration. All fold rows are `WARN` with `wrong_shape` (none carry the required 8 columns). **Neither file was edited.**

### D.2 — This cycle's register (reported separately)

| file | blob | status | fold tables | distinct shapes | fold rows |
|---|---|---|---|---|---|
| `walk-register-walk-register-schema-2026-08-10.md` | `7ebe326` | `UNCONFORMANT` | 7 | 1 (`\| id \| walk \| lens \| sub_q \| origin \| finding \| pre_fold_text \| resolution \|`) | 45 |

Status: `UNCONFORMANT`. The register uses `sub_q` as the column name; the schema requires `sub_question`. All 45 fold rows are `WARN` with `missing: sub_question, note: wrong_shape`.

**D.4 observation:** the register was written to match the schema's intent but used a shortened column name (`sub_q` vs. `sub_question`). The validator correctly reports this as a shape mismatch — it is measuring the schema's strictness against its own first test subject, not an error in either artifact.

### D.3 — Blob IDs

| file | blob ID |
|---|---|
| `walk-register-group4-rescope-2026-08-10.md` | `ef2fa9e43a04ec2a08941ae2f9774b714bbd8b07` |
| `walk-register-lint-class-recall-2026-08-10.md` | `7e707163c06725caa23054a2513236a3212da41a` |
| `walk-register-walk-register-schema-2026-08-10.md` | `7ebe3264acb6b31be9134534f550d2cc4ca252a5` |

Raw output deposited at `knowledge/qa/evidence/walk-register-schema-2026-08-10/existing-registers-run.txt`.

---

## Deposits

- `bellows/scripts/walk_register_lint.py`
- `bellows/tests/test_walk_register_lint.py`
- `bellows/knowledge/qa/evidence/walk-register-schema-2026-08-10/existing-registers-run.txt`
- `bellows/knowledge/development/walk-register-schema-dev-log-step-2-2026-08-10.md` (this file)
