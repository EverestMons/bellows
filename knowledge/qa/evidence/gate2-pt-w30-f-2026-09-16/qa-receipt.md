# QA Receipt — gate2-pt-w30-f-2026-09-16

**Plan:** bellows executable-100122 — DOCTRINE Gate 2 PT tranche six (PT v4.118, flip 444/474/489/513/518/538/567/587)
**Step:** 2 (QA)
**Date:** 2026-09-16
**QA Agent:** bellows dispatcher-invoked QA

---

## Verification Table

| Item | What verified | Status |
|------|---------------|--------|
| Step 1 receipt | check_deposit step 1 → 0 failure(s) | ✅ |
| Item 1 — governance commit | `3d2dbaf5` carries `[100122]` and `gate2-pt-w30-f` | ✅ |
| Item 1 — Task C counts | 47/47 counts as pinned in A3, see probes-raw.txt | ✅ |
| Item 1 — wc -l | 2668 lines | ✅ |
| Item 1 — porcelain | EMPTY (clean for PLANNER_TEMPLATE.md and g2ptw30f-flip.sql) | ✅ |
| Item 2 — builder run | BUILT: edits=10 blocks=1 lines+29 bytes+14485 post=47/47 deltas=pinned, builder_exit=0 | ✅ |
| Item 2 — BYTE_IDENTICAL | cmp of rebuilt output vs live file | ✅ |
| Item 2 — P4 digest | a03e802789dd5462 on-disk == blob at 59c2ec28 | ✅ |
| Item 2 — refusal 1 | out == in refused | ✅ |
| Item 2 — refusal 2 | under forbidden root refused | ✅ |
| Item 2 — refusal 3 | already-built refused | ✅ |
| Item 3 — eight rows | 444–587 all implemented\|codify\|ceo, stamp 2026-09-16T20:07:10Z (outside vintages) | ✅ |
| Item 3 — accepted count | 17 | ✅ |
| Item 3 — accepted at vintage stamps | 17 of 17 at the two vintage stamps | ✅ |
| Item 3 — implemented count | 402 | ✅ |
| Item 3 — capture line count | 590 lines | ✅ |
| Item 3 — capture pre-flip rows | 444–587 read accepted\|codify in the capture | ✅ |
| Item 3 — capture committed by DEV | git log subject carries [100122] and gate2-pt-w30-f | ✅ |
| Item 4 — suite file | full-suite-gate2-pt-w30-f.txt, exit=0 | ✅ |
| Item 4 — drift probe | git log 7fdc06cb..HEAD -- tests → empty (no drift) | ✅ |

---

## Follow-ups

- DC/PST tranche next — the PT route empties with this plan; 17 accepted rows remain, each its own plan.
- The Planner pushes governance after this close and projects the LESSONS.md markers (`forge_lessons/scripts/project_status_markers.py --apply`).
- Thread 336 at the keyboard after the seventh tranche closes.

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100122/knowledge/qa/evidence/gate2-pt-w30-f-2026-09-16/
Files verified: 3
