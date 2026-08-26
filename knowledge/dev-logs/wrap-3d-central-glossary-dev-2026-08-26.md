# Dev Note — wrap-3d-central-glossary (2026-08-26)

**Plan:** 543 | **Step:** 1 (DEV)

## State Branch

Probes: (i)=1, (ii)=10, (iii)=0, (iv)=0 → **FULL RUN** (Task B then C then D).

## W1 — re-point 3d (Task B)

Anchor count == 1 pre-write — PASS.

Post-write probes:
- `"NEVER write to"` count: **1** ✅
- `"If the file does not exist, create it"` count: **0** ✅ (scaffold clause removed)
- Case-insensitive `"glossary"` count: **4** (RECORDED — QA compares against this value)
- `wc -c hooks/commands/wrap.md`: **5986** bytes

## W2 — completeness guard + pointer-ize (Task C)

Old glossary: 10 `## ` entries — assert PASS.
Central `[project: bellows]` entries: 10.

Per-term match lines:
```
MATCH clearance
MATCH deposit receipt
MATCH class hold
MATCH release act
MATCH gate override
MATCH verdict conditioning
MATCH keyed sweep line
MATCH verdict act
MATCH dirty-tree precheck (intersection form)
MATCH no_receipt hold
```

All 10 bodies matched (per-line trailing-whitespace strip + outer blank-line strip).

Post-write probes on `knowledge/glossary.md`:
- `"RETIRED"` count: **1** ✅
- `^## ` count (regex): **0** ✅
