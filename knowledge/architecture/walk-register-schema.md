# Walk Register Schema — v0.3

**schema_version:** `0.3`
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

## Panel rows and the Deviations open tail (v0.2)

**Per-seat panel rows are SANCTIONED.** Default granularity remains one row per FINDING; a cold-panel seat MAY coarsen to one row per SEAT, reusing the SAME eight required columns: `walk` carries the seat label (`panel-N`), `origin` the seat's origin tally, `finding` the seat's findings with severities and classes, `pre_fold_text` the touched sites (or a site count), `resolution` the fold summary — with per-finding detail living in the plan's own seat lines. Both panel-bearing cycles (gate2-pt3, gate2-coldpanel) converged on this form independently and each had to declare it as a deviation; a deviation filed by every member of a class is a schema amendment owed — hence 0.2. (Proposal 330, entry 322, codified 2026-08-12.)

**The Deviations open tail.** A register's Deviations line naming a per-phase commit range ends with a defined OPEN TAIL — "…plus the closing commit, named in the wrap" — because a register cannot name its own closing commit (measured: every register's recovery range ended one commit early until the tail convention was improvised twice).

**Version note:** registers declaring `0.1` remain valid — 0.2 is additive (a sanctioned form plus a tail convention; no column, container, or naming change). The validator checks structure, not the declared version value.

---

## Cost

Capturing `pre_fold_text` means every fold's author copies the pre-edit bytes before editing. That is a real authoring burden and this plan does not pretend otherwise — it is the price of the record being joinable. Diagnostic 337 is what the alternative costs: two diagnostics ending at the same wall because the record describes folds in prose a reader can follow and no tool can join.

---

## v0.3 — the verbatim-ellipsis annotation, structural guards, and the every-tier coherence line

**The verbatim-ellipsis annotation.** `pre_fold_text` carrying a literal source ellipsis (`...` or `…`) as part of COMPLETE pre-image bytes is verbatim, not truncation — rule (a) forbids rewriting it, and the validator previously could not distinguish the two (the s40sweep ingest register owned the false-positive class; the 2026-08-13 gate1 packet's rider routed it here). The author attests per row by placing the literal marker `verbatim-ellipsis` in the row's `finding` or `resolution` cell (never inside `pre_fold_text` itself); the validator then reports the row OK with note `verbatim_ellipsis_annotated`. An unannotated ellipsis stays `truncated_pre_fold_text` — the annotation is an attestation and prices like one (the lens-attestation rules apply). ⚠️ The marker is a substring match: a row whose finding or resolution merely MENTIONS the marker token silently annotates a real truncation — a known, priced collision channel (the validator is warn-only and the author-verify duty covers it; describe the marker rather than exhibiting it in rows that are not attesting). Closed registers carrying prose ownership notes stay byte-stable and UNCONFORMANT per their own text; the annotation is forward-looking.

**Structural guards (validator v0.3).** Three classes, measured live in the committed corpus at authoring:

- `duplicate_row` — two byte-identical eight-cell data rows within any parsed table in one file (the DUP-APPEND channel class, measured twice in one register during the s40sweep arc; the guard reads all parsed tables, not only fold tables — stated mechanism). Structural: flips the file UNCONFORMANT. Repeated table HEADERS are the multi-table norm and are excluded from this guard.
- `headerless_rows` — pipe rows with fold-row cell counts (seven or more cells) that belong to no parsed table (no header+separator reaches them; a blank line or prose detached them — including a file with no parsed table at all). Such rows were INVISIBLE to v0.2 validation — measured at authoring: 46 rows across 4 committed registers, including 16 panel-seat rows in one register no validator run had ever read. Structural: flips UNCONFORMANT.
- `duplicate_adjacent_line` — two adjacent byte-identical non-empty prose lines outside tables and code fences (the duplicated open-tail line's shape). Advisory: reported, does not flip status.

**The record-coherence check runs at EVERY tier (the gate2-dc deferral, landed).** The walk-0 battery and every culmination run the register-rows ↔ per-phase-commits check, both directions, at every tier — T1 included, not only where DRAFTING_CYCLE §2.6's residue battery mandates it for T2 panels. (A declared synthesis: the deferral's letter covered the walk-0 battery home; the every-culmination cadence is §2.6's own, restated here so the tier widening carries it — stated, not silent.) The register licenses the cycle's own record at every tier. The check is git-side and deliberately outside this validator (the validator stays repo-blind).

**Version note:** 0.3 is additive — no column, container, or naming change; 0.1/0.2 registers stay valid as written (closed registers are not retro-annotated).
