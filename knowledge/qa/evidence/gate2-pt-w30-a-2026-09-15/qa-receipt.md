# QA Receipt — gate2-pt-w30-a-2026-09-15

**Plan:** `gate2-pt-w30-a-2026-09-15`
**Step:** 2 (QA)
**Date:** 2026-09-15
**Agent:** bellows QA

---

## Verification

| # | Item | Status |
|---|------|--------|
| 1a | Template commit: `f402a9dd` carries `[100109]` and `gate2-pt-w30-a` subject | ✅ |
| 1b | 30/30 counts as pinned in A3, see probes-raw.txt | ✅ |
| 1c | `wc -l PLANNER_TEMPLATE.md` → 2558 | ✅ |
| 1d | Porcelain empty (template and flip-sql) | ✅ |
| 2a | Builder rebuilt output byte-identical from pre-edit blob (`BYTE_IDENTICAL`) | ✅ |
| 2b | P4 digest match: on-disk `3d96ad997d9a9b06` = committed blob | ✅ |
| 2c | Refusal 1 (out == in): `BUILDER REFUSED`, exit 1 | ✅ |
| 2d | Refusal 2 (out under governance root): `BUILDER REFUSED`, exit 1, no file written | ✅ |
| 2e | Refusal 3 (already built): `BUILDER REFUSED`, exit 1 | ✅ |
| 3a | 12 rows `implemented\|codify\|ceo\|2026-09-15T20:49:16Z` (stamps outside both vintages) | ✅ |
| 3b | `accepted` count = 74; all 74 at the two vintage stamps | ✅ |
| 3c | `implemented` count = 345 | ✅ |
| 3d | `flip-capture.txt` committed by DEV (`[100109]` subject); 590 lines | ✅ |
| 3e | Capture's 12 rows for flipped ids show `accepted\|codify` (pre-flip state) | ✅ |
| 4  | Suite file `full-suite-gate2-pt-w30-a.txt`; `exit=0` | ✅ |

**Test drift note (Item 4):** `git log --oneline f9e35f36..HEAD -- tests` is non-empty — 6 commits on the `tests` path since P7's baseline (`f9e35f36`). Pass count moved from P7's 2395 to 2445; zero failures. Drift listed in probes-raw.txt under Item 4. Summary line is in the suite file only.

---

## Follow-ups (not this plan's act)

- Six remaining tranches (tranches 2–6 and the DC/PST tranche) — their own plans, per the packet's order.
- Planner pushes governance and projects the LESSONS.md markers after the close.
- Threads 326 and 336 closed at the keyboard (326 at this close; 336 closes with the seventh tranche).

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100109/knowledge/qa/evidence/gate2-pt-w30-a-2026-09-15/
Files verified: 3
