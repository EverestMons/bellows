# Dev log — `register_coverage_census`, Step 1

**Date:** 2026-09-04 (drafted) / executed 2026-09-05 · **Machine:** the mini
**Plan:** `knowledge/decisions/drafts/diagnostic-register-coverage.md`
**Dispatch mode:** `manual_bootstrap` — ⛔ **no lifecycle plan id, no `Done/` record.** Cite the
research note by path:
`eluvian-governance/governance/knowledge/research/register-coverage-2026-09-04.md`

## The five failed hand-probes, and the assumption each imposed

⛔ **This is why the plan exists.** Five readings of one corpus produced five different wrong
answers, every one plausible enough to have been reported. Each failed on a DIFFERENT structural
assumption, and every one of the five was a hand-written parse.

| # | what it did | the assumption it imposed | what it reported |
|---|---|---|---|
| 1 | hardcoded `len(cells) >= 8` | that every register uses the 8-column 0.3 shape | excluded every 5-cell 0.2 row → **"39 of 70 registers orphaned"** |
| 2 | called `validate_file` but read `r.get("id")` | that the lint returns the register's rows | that key does not exist — the returned rows are LINT REPORT rows (`file, line, table, row_status, …`) → **"70 of 70 orphaned"** |
| 3 | inspected the structure | — | found the real cause: **the lint has no notion of finding identity at all**; `"id"` is a name it checks for PRESENCE and never reads |
| 4 | shape-aware parse keyed on the header's own `id` column | still one header per FILE | **100% orphan** for registers that plainly have rows |
| 5 | the cause of (4) | that the id convention is one regex | **the convention VARIES** — `d1`, `w1-1`, `W1-1`, `S1-5` all observed; a regex accepting two silently drops the rest |

⛔ **The draft was about to make a sixth.** Register row L4-1 (walk 1, Integration-record) caught it:
the draft imported the lint for its STATUS and then re-implemented table parsing to reach the id
column — a second reader of one format, which diagnostic **100032**'s walk 4 had already forbidden in
terms. `split_table_row` already handles the escaped-pipe case that broke two of the five;
`normalize_column` already handles the `sub_q` variant.

## What was built

`tools/register_coverage_census.py`, read-only over the corpus.

- **Imports the shipped parser and calls it**: `extract_tables`, `split_table_row`,
  `normalize_column`, `is_fold_table`, `validate_file`, and the `STATUS_*` vocabulary. No table, row,
  cell or pipe-escape is parsed by hand.
- **Derives the id convention from each table's own header and cells.** Every id is abstracted to a
  SHAPE (upper run → `A`, lower run → `a`, digit run → `9`, everything else literal) and bound to the
  file's own literal alpha prefix. Nothing is matched against a pattern the instrument was told about.
- **Handles every table in the file.** A header is bound per TABLE, not per file — 116 of 172
  registers (67.4%) carry more than one id table, and one carries 30. The 100%-orphan signature seen
  twice in the probes is exactly what a per-file header binding produces.
- **Excludes this plan's own register by exact filename** (`walk-register-register-coverage-2026-09-04.md`)
  and reports the exclusion. The population moved 172 → 173 when that file was created.
- **Pins the population before counting it** and re-reads it after; bounded at three attempts.
- **Appends to the raw `.txt` as each measurement is established**, so a killed run leaves partials.

## Two refinements made during execution, and why

1. **Cell normalisation.** `S3-1 ⛔` and `S3-1` are the same id; treating them as different made a
   rowed id look orphaned. The instrument now takes the leading whitespace-delimited token of an id
   cell. Normalisation, not pattern matching.
2. **⛔ Not every id cell yields a scannable convention, and pretending otherwise reproduces probe 5.**
   Bare numeric ids (`1`, `2`, `3` …) are real in this corpus, but a `\d+` search pattern matches
   years, line numbers and plan ids — the first run of the instrument scored `2026`, `3969` and `2474`
   as orphans. Numeric and non-atomic cells are now **counted and reported but never turned into a
   search pattern**, and the affected registers are declared UNMEASURABLE rather than given a number.

Related, and reported the same way: families whose shape has no internal separator (`a9`, `A9`) can
collide with ordinary prose — `w1` is both a plausible id and a walk reference. Orphans are therefore
reported at two tiers, STRICT (the defensible floor, **103**) and ALL (the ceiling, **164**), with the
tier derived from the shape's own complexity.

## Controls

- **Positive, two registers, run before any corpus pass**: `walk-register-qa-steps-parsing-2026-09-04.md`
  (schema 0.3, `w1-1 …`, SINGLE-table) and `walk-register-dc-coldfront-2026-08-13.md` (schema 0.2,
  `d1 …`, MULTI-table). Both returned a non-empty rowed-id set with the expected sample id present.
  ⛔ One register would prove only that the instrument reads the convention it was written for — which
  is how probe 5 failed.
- **Population pin**: START and END `git rev-parse HEAD` identical
  (`1a99e2bb7cff30f0e0f1a5bba0cec377f883c61f`), file count identical at 172. Run VALID.

## Result, in one line each

- **172 censused** (173 present, self excluded), as-of governance HEAD `1a99e2bb`.
- **P3 HOLDS** — the sha256 pin matches and the lint still never reads the id cell's value. No halt.
- **The pin's P2 arithmetic did not close** (168 against a pinned 172) and there are **five** declared
  schema states, not four — `0.1-draft` was invisible to a `[0-9.]+` grep.
- **31 shapes / 75 prefix-bound families** derived, against the four the pin could observe.
- **103 orphans strict, 164 all**, over 2866 rowed ids — but the corpus-wide 3.5% is the wrong number
  to quote: UNDECLARED registers orphan at **23.3%** against `0.3`'s **1.5%**, a factor of ~15.
- **57 present-but-unreadable rows** across 9 registers, kept as a third state; the id is never guessed.
- **11 registers are UNMEASURABLE** and are named, not zeroed.

## Item 6 — the battery, against the stated baselines

Full table in the research note. The two that moved: `propagation_check` fell from **164/52/69/89** to
**10** while its false-positive rate stayed **100%** — the masking fix removed the class it targeted
and did not touch restated values. `fold_check` returned **VACUOUS** at execution, which is correct:
Step 1 edits no plan text, so the baseline is the state being compared, and the predecessor's
`fold_check` would have said CLEAN here — the verdict quoted three times as evidence of nothing.

⚠️ **`walk_register_lint` reported CONFORMANT throughout, including over a walk-2 register that was
missing the `w2-6` row.** The tool this plan prices failed to catch a coverage defect in the cycle
studying it. That is thread 135's finding occurring inside its own diagnostic, and it was caught by a
hand reconciliation, not by a tool.

⛔ **`mutation_check`: NO COVERAGE CLAIMED.** A read-only diagnostic exercises neither of its
2026-09-04 fixes. Stated so the absence is a declaration, not a gap.

## Gate expectation for this step

⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as
`.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Named in the plan before
execution, on the 100032/100034/100036 precedent. ⛔ This justification is committed BEFORE any
override; `--override-gate` is write-once.

⚠️ **The `.txt` deposit follows no precedent.** `diagnostic-100036` and plan `100038` both carried the
identical pre-declaration and neither deposited one. `knowledge/qa/evidence/` is a QA-shaped path for
a plan with no QA step: this establishes a convention rather than inheriting one, and a later reader
may move it once one exists.

## Post-conditions

Every register in P1's population classified · per-schema-state subtotals reported, never one
corpus-wide percentage · id conventions DERIVED and listed · no-table, rowed, named-but-unrowed and
present-but-unreadable kept as four distinct states · this cycle's battery numbers recorded against
the stated baselines · ⛔ **no recommendation and no design anywhere.** It sizes; it does not choose.
