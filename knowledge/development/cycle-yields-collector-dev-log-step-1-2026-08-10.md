# Dev Log — cycle-yields-collector-2026-08-10 — Step 1

**Plan slug:** `cycle-yields-collector-2026-08-10`
**Date:** 2026-08-10
**Step:** 1 (DEV)

## A0 — Preconditions

- `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/` → empty (clean).
- `ls -l bellows/scripts/cycle_yields.py` → absent.
- **Branch:** FRESH. Script does not exist, no prior commit with the slug.

## Task B — Tool

Deposited `bellows/scripts/cycle_yields.py`. Read-only, standard library only, no arguments required. Root derived by walking up from `__file__` to nearest directory containing `DRAFTING_CYCLE.md`; injectable via positional CLI argument for hermetic testing (C2 constraint).

## Task C — Targeted Tests

Deposited `bellows/tests/test_cycle_yields.py`. 32 cases, all hermetic (inline fixtures or `tmp_path`).

Cases per the plan spec:
- (a) v2.0 origin split → PRESENT
- (b) pre-v2.0 no split → ABSENT, fields are `-` not `0`
- (c) malformed line → UNPARSEABLE emitted
- (d) no block → NO_BLOCK
- (e) two headings → MULTIPLE_BLOCKS
- (f) All lenses form → parsed (three variants: bare, dry, with description)
- (g) empty block → zero rows, no crash
- (h) heading in fence → not counted
- (i) column count invariant (12 fields on every status)
- (j) real + fenced heading → OK with block=1
- (k) multi-pass `w1 2 folded; w2 dry; w3 dry` → 3 rows
- (l) dry pass → folded=0
- (m) half-split → PARTIAL (both pre-existing and fold-introduced variants)

```
======================== 32 passed, 1 warning in 0.25s =========================
```

## Task D — Corpus Run

Deposited at `bellows/knowledge/qa/evidence/cycle-yields-collector-2026-08-10/corpus-run.txt`.

### Discovery

- **Files discovered:** 1694
- **Files with `## Drafting Cycle` block:** 61
- **Control:** `grep -Fl "Weak spots:"` across the same Done/ population → 55 files (matches plan's authoring measurement).

### Status tally (enumerated from script)

| Status | Count |
|---|---|
| OK | 342 |
| NO_BLOCK | 1633 |
| UNPARSEABLE | 194 |
| MULTIPLE_BLOCKS | 0 |

### Origin tally (enumerated from script)

| Origin | Count |
|---|---|
| ABSENT | 342 |
| N/A | 1827 |
| PRESENT | 0 |
| PARTIAL | 0 |

### Findings vs authoring predictions

- **Block-carrying count:** 61, plan predicted 63. Delta = -2. Not reconciled per plan instruction ("a difference is a finding to report, not an error to correct").
- **Origin splits (PRESENT):** 0 in per-lens-line format. The plan's "2 of them carry an origin split" counted fold-origin classification summary lines (⚠️ bullets), which use a different format (`w1 7/7 pre-existing`) than the per-lens `(N / N)` split this parser reads. No v2.0-format closes exist in the corpus, which is exactly what the plan stated ("0 cycles have closed under v2.0").
- **UNPARSEABLE:** 194 rows across the corpus. These are predominantly pre-v2.0 format lens lines using older conventions: bare counts without "folded" keyword (`w1 3; w2 2`), arrow format (`w1 → v5: 2 folded`), "raised" instead of "folded", dot-separated tallies (`w1 2 · cold 9`), and structural lines (`(pending)`, `not run.`, `→ dry.`). Reported faithfully — each carries the first 120 characters of the offending line in the note column.

### Exclusions (stated per plan)

Halted plans (`halted-executable-334.md`, `halted-executable-328.md`) live in `decisions/`, not `Done/`, so this tool never sees them. 334 carries the richest Cycle Log in the shop (125 findings, five-seat panel, full origin splits). **FORWARD candidate:** widening to halted plans is a v1 decision.
