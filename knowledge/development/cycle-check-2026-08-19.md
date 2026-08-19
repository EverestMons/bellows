# cycle_check.py — DEV log (2026-08-19)

## What

`scripts/cycle_check.py` — a drafting-cycle validator that reads a plan's
`## Drafting Cycle` block and emits exactly one of three verdicts:

| Verdict       | Exit | Meaning                         |
|---------------|------|---------------------------------|
| CONTINUE      | 0    | Cycle is mid-flight, keep going |
| BAR_MET       | 0    | Current walk is dry + clean     |
| ESCALATE:*    | 1    | Human attention required        |

Exit 2 = internal error. Strictly read-only — writes nothing, commits nothing.

## Reuse surface (verified before import)

```python
from cycle_yields import extract_dc_blocks, parse_lens_line, PASS_FOLDED_RE, PASS_DRY_RE
```

- `extract_dc_blocks(text)` — strips fenced code blocks, returns list of DC block strings.
- `parse_lens_line(line)` — returns None (non-lens) or list of tuples; items with `[0] == "UNPARSEABLE"` are degenerate.
- `PASS_FOLDED_RE`, `PASS_DRY_RE` — regex patterns for fold/dry pass detection (anchor set: `^;.)`).

**Anchor-set fix**: `PASS_FOLDED_RE` / `PASS_DRY_RE` anchor on `^`, `;`, `.`, `)` but the first pass token on a lens line follows `:`. cycle_check defines local `_FOLD_RE` / `_DRY_RE` with `:` added to the anchor set for use in `extract_per_pass_metadata`.

## Decision-function order

1. **Parse guard** — exactly 1 DC block, at least one parseable lens line
2. **Assert #1** (arithmetic) — instruction + record == fold total per class-split; cross-checked against Walk-N STATUS lines
3. **Assert #2** (evidence) — walk register exists; git history corroboration
4. **Assert #3** (fold happened) — foldcheck baseline exists; degrades to N/A when assert #2 has no git context
5. **Uncommitted walk** — git walk-commit count < max walk number
6. **Restructuring** — restructuring token in current walk
7. **Yield rising** — current instruction count > prior walk's
8. **Plateau** — 3+ consecutive walks at flat instruction count, no new finding class (requires 4+ walks)
9. **BAR_MET** — current walk dry + all asserts OK + no unparseable lens data
10. **CONTINUE** — default
11. **Anti-fabrication** — closure markers present but verdict is CONTINUE and no unparseable data → ESCALATE:claimed-close-unmet

## ESCALATE vocabulary (closed set)

`unparseable`, `assert-fail:1`, `assert-fail:2`, `assert-fail:3`,
`uncommitted-walk`, `restructuring-fold`, `yield-rising`, `plateau`,
`claimed-close-unmet`

Absent from implementation (no current-walk signal): `direction-class`,
`new-ceo-decision`.

## Key design decisions

- **Presence-based N/A**: 27/37 Done files lack class-split → assert #1 silently N/A.
- **Compact dry format**: `- Weak spots: dry. — Destruction: dry.` is UNPARSEABLE by cycle_yields but detected as dry via walk-section context tracking (`WALK_SECTION_RE`).
- **Bare count format**: `w2 4; w3 3` without "folded" keyword → UNPARSEABLE. Setting `has_unparseable=True` prevents BAR_MET and anti-fabrication from firing → CONTINUE (exit 0).
- **No foldcheck baselines in Done/**: assert #3 degrades to N/A when assert #2 finds no git context (git_has_context=False).
- **Walk register cross-repo**: if register path resolves to a different git root, assert #2 register check → N/A.

## Test coverage (27 tests)

Every decision-function branch and degenerate row from the format census:
unparseable (no-block, multi-block, no-parseable-lens), assert-fail (1/2/3),
restructuring-fold, yield-rising, plateau-at-3, BAR_MET, CONTINUE,
legacy N/A class-split, zero-walk, mixed parseable/unparseable,
uncommitted-walk, claimed-close-unmet, Walk-N STATUS (parsed + cross-check fail),
compact dry format, walk register cross-repo, closure marker detection,
plateau requires 4+ walks, N/A instruction counts, foldcheck baseline exists,
CLI exit codes, record-only folds, instruction-zero current walk.
