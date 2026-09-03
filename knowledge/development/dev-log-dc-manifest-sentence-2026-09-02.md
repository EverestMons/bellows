# Dev Log — dc-manifest-sentence-2026-09-02 (plan 100027)

**Date:** 2026-09-02 | **Step:** 1 (DEV)

## A0 — Root check and branch ladder

TREE_OK: `bellows.py` and `tests/` present in bellows root.
GOV_OK: `DRAFTING_CYCLE.md` and `build-dc-manifest-sentence-2026-09-02.py` present in governance root.

**Branch ladder:**
- (1) P1 SHA: `3a84137ed3669de1` — MATCHES
- (2) `git -C "$GOV" status --porcelain -- DRAFTING_CYCLE.md` → EMPTY
- (3) last commit subject on `DRAFTING_CYCLE.md`: `[100008] gate2-dc(gate2-dc-w28-2026-09-01): …` — does NOT carry `dc-manifest-sentence`

**Determination: FRESH → A1.**

## A1 — Pins re-derived

**P1 — DC sha, lines, bytes (pre-edit v2.23):**
- SHA: `3a84137ed3669de1` ✓ (expected `3a84137ed3669de1`)
- Lines: 369 ✓
- Bytes: 164586 ✓

**P2 — ANCHORS:**
- E1 head (`**The \`## Cycle Manifest\` stanza: a fixed \`key: value\` block emitted at BAR_MET.**`): count 1 ✓
- E1 tail (`not part of the stanza grammar defined here.`): count 1 ✓
- E1 head + tail on line 253: confirmed ✓
- E2 (`**Version:** 2.23 (2026-09-01). Amended only through the Iteration Protocol (§6).`): count 1 ✓
- E4 (`class: governed-tooling` whole line at line 281): count 1 ✓
- E5 (`validation: cycle_check=BAR_MET, plan_lint=0_FAIL` whole line at line 287): count 1 ✓

**P3 — TOKENS 0 before (new tokens, each 0):**
- `ten REQUIRED fields`: 0 ✓
- `three OPTIONAL fields`: 0 ✓
- `one of the FOUR values`: 0 ✓
- `compares ONLY the declared`: 0 ✓
- `2.24 (2026-09-02)`: 0 ✓
- `slug dc-manifest-sentence-2026-09-02`: 0 ✓

**Invariants (pre-edit):**
- `HARD-HOLD`: 2 ✓
- `HOLD-AND-REPORT`: 2 ✓
- `{read-only, governed-tooling, register-writing}`: 1 ✓
- `class: governed-tooling` (whole line): 1 ✓
- `class: shop-infra` (whole line): 0 ✓
- four-pair validation line (whole): 0 ✓

**P4 — Builder digest:**
- On-disk: `a9e4d099e11f213d` ✓ (expected `a9e4d099e11f213d`)
- Blob at builder's own last commit (`f0ab037d`): `a9e4d099e11f213d` ✓ (MATCH)

**P5 — DRY_RUN (A2):** see A2 below.

**P6 — Gate baseline on `knowledge/decisions/Done/executable-100026.md` (sha `5138760431ae73f1`) — captured BEFORE the edit:**
- `plan_lint` exit 0: PASS 9 / WARN 5 / FAIL 0 / INFO 1 / PIN-CHECK 6
- `cycle_check` → `BAR_MET`
- Matches plan-declared baseline ✓

## A2 — Dry-run (scratch→scratch)

```
BUILT: /tmp/dc67/DC-out.md edits=5 lines+1 bytes+4669 post=20/20
builder_exit=0
```

numstat: `5  4` (exit 1 = differing state) ✓ (expected `5	4`)
`wc -l /tmp/dc67/DC-out.md` → 370 ✓
`wc -c /tmp/dc67/DC-out.md` → 169255 ✓

**Four refusals (each BUILDER REFUSED, nonzero exit):**
1. out == in: `BUILDER REFUSED: out == in` (exit 1) ✓
2. Under forbidden root: `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)` (exit 1) ✓
3. Already built: `BUILDER REFUSED: output tokens already present in input — already built?` (exit 1) ✓
4. Input missing: `BUILDER REFUSED: input missing: /tmp/dc67/absent.md` (exit 1) ✓

## A3 — Apply, Task C counts, commit

`cp /tmp/dc67/DC-out.md "$GOV/DRAFTING_CYCLE.md"` — exit 0.

**Task C counts (live file, 14 probes):**
- `ten REQUIRED fields`: 1 ✓
- `three OPTIONAL fields`: 1 ✓
- `one of the FOUR values`: 1 ✓
- `compares ONLY the declared`: 1 ✓
- `{read-only, governed-tooling, register-writing}`: 0 ✓
- `HARD-HOLD`: 2 ✓
- `HOLD-AND-REPORT`: 2 ✓
- `**Version:** 2.24 (2026-09-02)`: 1 ✓
- `**Version:** 2.23 (2026-09-01)`: 0 ✓
- `- **2.24 (2026-09-02):** slug dc-manifest-sentence-2026-09-02`: 1 ✓
- `- **2.23 (2026-09-01):** slug gate2-dc-w28-2026-09-01`: 1 ✓ (old row survives)
- `class: governed-tooling` (whole line): 0 ✓
- `class: shop-infra` (whole line): 1 ✓
- `validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=CLEAN` (whole line): 1 ✓

`wc -l` → 370 ✓
`cmp /tmp/dc67/DC-out.md "$GOV/DRAFTING_CYCLE.md"` → SILENT (identical) ✓
`git diff --stat` → 1 file changed, 5 insertions(+), 4 deletions(-) ✓

**Governance commit:** `d02fa149`
```
[100027] dc-manifest-sentence: DRAFTING_CYCLE v2.24 — the thread-67 sentence and the §3 example reconciled to depositor.py/plan_lint.py/cycle_check.py (no rule changed)
```
