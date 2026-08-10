# Dev Log — walk-register-schema Step 1 (2026-08-10)

**Plan:** walk-register-schema-2026-08-10
**Step:** 1 — DEV (measure the population, then write the schema)
**Branch:** bellows-wt/338

---

## Task A0 — guards

| guard | command | result |
|---|---|---|
| (1) NOT-WIRED | `git status --porcelain -- scripts/plan_lint.py gates.py` | empty |
| (1b) CLEANLINESS | `git status --porcelain -- scripts/ tests/ knowledge/architecture/ knowledge/qa/ knowledge/development/` | empty |
| (2) RE-ENTRY | `git log --oneline -- knowledge/architecture/walk-register-schema.md` | no commits |

**Branch: FRESH** — (1) and (1b) empty AND (2) no such commit. Proceeding at Task B.

---

## Task B — population measurement

### Enumeration method

Committed walk registers found via `git log --all --name-only --format="" | grep -F "walk-register" | sort -u` at the governance root (`/Users/marklehn/Developer/GitHub`):

```
governance/knowledge/research/draft-walk-register-schema-2026-08-10.md
governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md
governance/knowledge/research/walk-register-lint-class-recall-2026-08-10.md
governance/knowledge/research/walk-register-walk-register-schema-2026-08-10.md
```

`draft-walk-register-schema-2026-08-10.md` is a draft of this plan, not a walk register — confirmed by the walk register's own line 5 reference: `**Draft:** governance/knowledge/research/draft-walk-register-schema-2026-08-10.md`. Excluded from count.

On-disk search (`find -name "*walk-register*"`) also found:
- `/Users/marklehn/Developer/GitHub/scratchpad/walk-register-gate2-s5-conformance-2026-08-09.md` — untracked (`?? scratchpad/...`), prose-only with no pipe-delimited tables.

### Table headers — verbatim

**walk-register-group4-rescope-2026-08-10.md:**
- `| # | sub-q | finding | fold |` (primary, many tables)
- `| # | finding | fold |` (line 40, one table)
- Also non-fold tables: `| window | interleaving risk | guard before | guard after |`

**walk-register-lint-class-recall-2026-08-10.md:**
- `| # | sub | finding | resolution |` (primary, many tables)
- `| # | finding | resolution |` (line 76, one table)
- `| # | lens | finding | resolution |` (line 241, one table)
- Also non-fold tables: `| lens | folded | note |`, `| metric | draft @ w3 | ... |`, `| walk | changed **instructions** | ... |`, `| finding | channel |`

**walk-register-walk-register-schema-2026-08-10.md** (this cycle's own):
- `| id | walk | lens | sub_q | origin | finding | pre_fold_text | resolution |` (the proposed schema's shape)
- Also non-fold tables: `| field | required | meaning |`, `| | measured 2026-08-10 |`, `| walk | folded | fold-introduced | pre-existing |`

**scratchpad/walk-register-gate2-s5-conformance-2026-08-09.md:**
- No pipe-delimited tables. Prose-only register.

### Findings against authoring-time read

| metric | authoring | measured | status |
|---|---|---|---|
| committed walk registers | 2 (+ this cycle's = 3) | 3 | expected growth — this cycle's register committed at walk 0 |
| distinct fold-table shapes (two original files) | 3 | 5 | UNDERCOUNT — two shapes in lint-class-recall existed at authoring but were missed |
| files with more than one fold-table shape | 1 | 2 | UNDERCOUNT — both original files are multi-shape |
| untracked registers on disk | 1 | 1 | confirmed |

**Shape population is larger than reported.** The authoring-time read listed three shapes (`| # | sub-q | finding | fold |`, `| # | finding | fold |`, `| # | sub | finding | resolution |`). Re-measurement finds five distinct fold-table shapes across the two original files, plus this cycle's 8-column shape for a total of six. The two missed shapes (`| # | finding | resolution |` at lint-class-recall line 76 and `| # | lens | finding | resolution |` at line 241) were committed before this plan was authored.

This strengthens the plan's rationale: the dialect problem is worse than stated.

---

## Task C — schema document

Deposited at `knowledge/architecture/walk-register-schema.md`. Contains:

1. **C.1 — Container:** UTF-8 markdown document, pipe-delimited tables, header row per table.
2. **C.2 — File-naming:** `walk-register-<plan-slug>.md`; validator globs `walk-register-*.md`.
3. **C.3 — Required fields:** id, walk, lens, sub_question, origin, finding, pre_fold_text, resolution. `pre_fold_text` carries four rules: (a) verbatim always, (b) too large → split the fold, (c) escape pipe as `\|` and backslash as `\\`, (d) pure ADDITION recorded as literal `ADDITION`.
4. **C.4 — `schema_version` declaration:** `**schema_version:** <value>` before the first table; the token elsewhere is not a declaration.
5. **C.5 — Encoding:** UTF-8, stated explicitly for both the file and the validator.

The schema carries a **Cost** section stating honestly that `pre_fold_text` imposes an authoring burden.

The measured dialect table from Task B is included, with all six shapes and the comparison against authoring-time read.

---

## Deposits

- `bellows/knowledge/architecture/walk-register-schema.md`
- `bellows/knowledge/development/walk-register-schema-dev-log-step-1-2026-08-10.md` (this file)
