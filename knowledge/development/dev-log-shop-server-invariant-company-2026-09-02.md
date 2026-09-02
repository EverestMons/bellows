# Dev Log — shop/server invariant: COMPANY.md v2.8
**Plan:** 100019 — shop-server-invariant-company-2026-09-02
**Date:** 2026-09-02
**Step:** 1 (DEV)

## A0 — Roots and Precondition

**Bellows root:**
`cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d tests ] && echo TREE_OK`
→ TREE_OK (worktree: /Users/marklehn/Developer/bellows/.bellows-worktrees/100019)

**Governance root and builder:**
`GOV=/Users/marklehn/Developer/eluvian-governance; B="$GOV/governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py"; [ -f "$GOV/COMPANY.md" ] && [ -f "$B" ] && echo GOV_OK`
→ GOV_OK

**P6 (addendum landed):**
`/usr/bin/grep -cF -- '# Addendum 2026-09-02 — the shop/server invariant' "$GOV/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md"`
→ 1 (plan A closed; addendum present)

**RE-ENTRY check:**
`git -C "$GOV" log -1 --format=%s -- COMPANY.md`
→ `COMPANY.md v2.7: add tuyere to Active Projects (CEO-directed)` — FRESH path, no RE-ENTRY.

## A1 — Pins

| Pin | What | Measured | Expected | Match |
|-----|------|----------|----------|-------|
| P1 | COMPANY_SHA | 7883745e23467b4e | 7883745e23467b4e | ✓ |
| P1 | Line count | 350 | 350 | ✓ |
| P2 | E1 anchor count | 1 | 1 | ✓ |
| P2 | E2 anchor count | 1 | 1 | ✓ |
| P2 | E3 anchor count | 1 | 1 | ✓ |
| P3 | 'A MACHINE runs the shop' | 0 | 0 | ✓ |
| P3 | '**Version:** 2.8' | 0 | 0 | ✓ |
| P3 | 'the only permitted difference between shops' | 0 | 0 | ✓ |
| P4 | BUILDER_DISK digest | 07374437b30be915 | 07374437b30be915 | ✓ |
| P4 | BUILDER_BLOB digest | 07374437b30be915 | 07374437b30be915 | ✓ |
| P4 | Builder last commit | af5b21648362e8568774cc265b8482cd55f27ed4 | (governance af5b216) | ✓ |

`git -C "$GOV" status --porcelain -- COMPANY.md` → EMPTY (clean).

## A2 — Dry Run (scratch→scratch)

**Builder run:**
`rm -rf /tmp/ssic-scratch; mkdir -p /tmp/ssic-scratch; python3 "$B" "$GOV/COMPANY.md" /tmp/ssic-scratch/COMPANY-out.md; echo "builder_exit=$?"`
→ `BUILT: /tmp/ssic-scratch/COMPANY-out.md lines=350 delta_chars=507 delta_bytes=509 date=2026-09-02 edits=3 post=7/7`
→ `builder_exit=0`

**Diff line count:**
`diff "$GOV/COMPANY.md" /tmp/ssic-scratch/COMPANY-out.md | /usr/bin/grep -c '^[<>]'`
→ 6 (expected: 6)

**Output line count:**
`wc -l /tmp/ssic-scratch/COMPANY-out.md`
→ 350 (expected: 350)

**Refusal 1 — out==in:**
`python3 "$B" "$GOV/COMPANY.md" "$GOV/COMPANY.md"`
→ `BUILDER REFUSED: out == in` (exit 1)

**Refusal 2 — under governance root:**
`python3 "$B" "$GOV/COMPANY.md" "$GOV/scratch-out.md"`
→ `BUILDER REFUSED: out is under the governance root /Users/marklehn/Developer/eluvian-governance` (exit 1)

**Refusal 3 — already-built input:**
`python3 "$B" /tmp/ssic-scratch/COMPANY-out.md /tmp/ssic-scratch/COMPANY-out2.md`
→ `BUILDER REFUSED: anchor count 0 != 1 for: **Version:** 2.7` (exit 1)

**Refusal 4 — malformed date:**
`SSIC_DATE=tomorrow python3 "$B" "$GOV/COMPANY.md" /tmp/ssic-scratch/x.md`
→ `BUILDER REFUSED: SSIC_DATE malformed: 'tomorrow'` (exit 1)

## A3 — Apply and Measure Live File (Task C)

`cp /tmp/ssic-scratch/COMPANY-out.md "$GOV/COMPANY.md"` → cp_exit=0

**Live measurements:**
- P3 'A MACHINE runs the shop' → 1
- P3 '**Version:** 2.8' → 1
- P3 'the only permitted difference between shops' → 1
- '**Version:** 2.7' → 0 (retired)
- old Last-Updated line → 0 (retired)
- E1 anchor → 1 (preserved)
- Line 4: `**Last Updated:** 2026-09-02 — the shop/server invariant: a machine runs the shop, the mini is the server, and that is the only difference (CEO-directed)`
- `wc -l` → 350
- `git -C "$GOV" diff --stat -- COMPANY.md` → 1 file changed, 3 insertions(+), 3 deletions(-)
- `cmp /tmp/ssic-scratch/COMPANY-out.md "$GOV/COMPANY.md"` → CMP_IDENTICAL

**Governance commit:**
`git -C "$GOV" add COMPANY.md && git -C "$GOV" commit -m "[100019] COMPANY.md v2.8: a machine runs the shop, the mini is the server, the only permitted difference (CEO 2026-09-02)" -- COMPANY.md`
→ `9c99ff0 [100019] COMPANY.md v2.8: a machine runs the shop, the mini is the server, the only permitted difference (CEO 2026-09-02)`
