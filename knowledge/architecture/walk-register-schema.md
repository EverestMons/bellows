# Walk Register Schema — v0.1

**schema_version:** `0.1`
**Encoding:** UTF-8 (stated explicitly; validators open files with this encoding rather than deferring to locale)

---

## Container

A walk register is a **UTF-8 markdown document** whose fold rows live in **pipe-delimited tables**. A single file may contain one or more such tables, each preceded by a header row naming its columns. Non-fold tables (summaries, measurements, metadata) may coexist in the same document and are not governed by this schema.

Both existing registers use this container — measured 2026-08-10, not assumed.

---

## File-naming convention

Walk registers are named:

```
walk-register-<plan-slug>.md
```

where `<plan-slug>` is the plan's authoring-time slug. A validator globs for `walk-register-*.md` to discover registers in a directory.

The two existing registers follow this convention. This cycle's own register carries a doubled prefix (`walk-register-walk-register-schema-...`) because its plan slug begins with `walk-register` — an artifact of the naming rule, not a violation.

---

## Required fields

Every fold-row table header MUST contain exactly these columns, in this order:

| field | required | meaning |
|---|---|---|
| `id` | yes | stable within this register (e.g. `f1`, `f2`) |
| `walk` | yes | walk number; `0` for authoring-time findings |
| `lens` | yes | one of: Weak spots, Destruction, Vulnerabilities, Integration, ACID, Conformance, Trim |
| `sub_question` | yes | the numbered sub-question (e.g. `1.2`), or `-` if none |
| `origin` | yes | `pre-existing` or `fold-introduced` |
| `finding` | yes | what was wrong |
| `pre_fold_text` | **yes** | **the exact bytes the fold replaced** — see rules below |
| `resolution` | yes | what replaced it |

### `pre_fold_text` — the load-bearing field

This field exists because diagnostic 337 asked whether the fold record preserves the text of the defects it records. All 14 labelled instances came back as reader reconstructions and zero as verbatim bytes. A row that describes the defect instead of carrying it reproduces the failure that cost two diagnostics.

Four rules:

**(a) VERBATIM ALWAYS.** The field carries the exact bytes the fold replaced. No elision, no truncation, no length escape, no paraphrase.

**(b) A fold too large to write verbatim is too large to attribute — split it.** Two folds each carrying their own bytes beat one fold carrying neither. This is the remedy, not only the prohibition: a rule that forbids without prescribing gets worked around, and the workaround is a paraphrase, which is the defect this schema exists to end.

**(c) ESCAPE THE PIPE AND THE BACKSLASH.** Because `pre_fold_text` carries arbitrary plan bytes inside a markdown table:
- `|` is written as `\|`
- `\` is written as `\\`

Both escapes are required, or the round-trip is ambiguous: `pre_fold_text` carries plan bytes that already contain backslashes, so escaping only the pipe makes `\|` in the source indistinguishable from an escaped pipe. A markdown table's delimiter is the pipe, and an unescaped one silently truncates precisely the rows this schema exists to preserve.

The validator round-trips the escape byte-identical.

**(d) Pure ADDITION.** A fold that adds text rather than replacing it records the literal `ADDITION`. Tabs and newlines in the field are escaped (`\t`, `\n`); no other normalization.

---

## `schema_version` declaration

A conformant register declares its schema version as a header line **before the first table** in the file, in the form:

```
**schema_version:** `<version>`
```

A file with no such declaration is `PRE-SCHEMA` — it was written before the schema existed. `PRE-SCHEMA` is a distinct status from `UNCONFORMANT`: a pre-schema file is old; an unconformant file is wrong.

The validator keys the status on the presence of this declaration. The token `schema_version` appearing elsewhere in the file (e.g. in prose describing the rule) is NOT a declaration.

---

## Measured dialect table

Population measured 2026-08-10 (Step 1 Task B re-measurement, against authoring-time read).

### Committed walk registers: 3

| file | fold-table shapes | shape count |
|---|---|---|
| `walk-register-group4-rescope-2026-08-10.md` | `\| # \| sub-q \| finding \| fold \|` and `\| # \| finding \| fold \|` | 2 |
| `walk-register-lint-class-recall-2026-08-10.md` | `\| # \| sub \| finding \| resolution \|` and `\| # \| finding \| resolution \|` and `\| # \| lens \| finding \| resolution \|` | 3 |
| `walk-register-walk-register-schema-2026-08-10.md` | `\| id \| walk \| lens \| sub_q \| origin \| finding \| pre_fold_text \| resolution \|` | 1 |

### Untracked: 1

`scratchpad/walk-register-gate2-s5-conformance-2026-08-09.md` — prose-only, no pipe-delimited tables. Will not survive its session.

### Comparison against authoring-time read

| metric | authoring-time | re-measured | finding |
|---|---|---|---|
| committed count | 2 (+ this cycle's = 3) | 3 | no discrepancy — growth is this cycle's own register, expected |
| distinct fold-table shapes (original two files) | 3 | 5 | authoring-time count missed `\| # \| finding \| resolution \|` and `\| # \| lens \| finding \| resolution \|` in lint-class-recall — both existed at authoring, not new |
| files with more than one shape | 1 | 2 | both original files are multi-shape, not one |
| untracked | 1 | 1 | confirmed |

**The shape population is larger than reported at authoring.** This strengthens the plan's rationale: the dialect problem is worse than stated. Six distinct fold-table shapes exist across three files at n = 3 — the dialect problem FORWARD row 47 records for Cycle Logs is already present and already worse than measured.

---

## Cost

Capturing `pre_fold_text` means every fold's author copies the pre-edit bytes before editing. That is a real authoring burden and this plan does not pretend otherwise — it is the price of the record being joinable. Diagnostic 337 is what the alternative costs: two diagnostics ending at the same wall because the record describes folds in prose a reader can follow and no tool can join.
