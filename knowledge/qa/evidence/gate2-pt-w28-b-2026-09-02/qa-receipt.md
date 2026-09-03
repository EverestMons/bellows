# QA Receipt — gate2-pt-w28-b-2026-09-02 (plan 100026)

**Date:** 2026-09-02 | **Step:** 2 (QA) | **Status: Complete**

---

## Verification Table

| Item | Verification | Status |
|------|-------------|--------|
| 1.a | Git log: commit `de662398` carries `[100026]` and `gate2-pt-w28-b` subject | ✅ |
| 1.b | 19/19 counts as pinned in A3, see probes-raw.txt | ✅ |
| 1.c | wc -l: 2458 | ✅ |
| 1.d | Porcelain EMPTY for PLANNER_TEMPLATE.md and g2ptw28b-flip.sql | ✅ |
| 2.a | Builder rebuilt PT v4.98 from pre-commit blob — BYTE_IDENTICAL | ✅ |
| 2.b | P4: on-disk builder digest `5d032b8ce50e0faa` matches committed blob (commit `917ad5c0`) | ✅ |
| 2.c | Refusal 1 — out==in: BUILDER REFUSED, exit=1 | ✅ |
| 2.d | Refusal 2 — under forbidden root: BUILDER REFUSED, exit=1 | ✅ |
| 2.e | Refusal 3 — already built: BUILDER REFUSED, exit=1 | ✅ |
| 3.a | 8 rows: all `implemented\|codify\|ceo` with stamp `2026-09-03T01:18:58Z` ≠ vintage | ✅ |
| 3.b | accepted COUNT: 23 | ✅ |
| 3.c | W=29 accepted (stamp `2026-09-02T23:54:37Z`) COUNT: 23 | ✅ |
| 3.d | implemented COUNT: 334 | ✅ |
| 3.e | flip-capture.txt: 466 lines | ✅ |
| 3.f | capture: 31 rows with `\|accepted\|codify\|` (pre-flip state confirmed) | ✅ |
| 3.g | capture: all 8 flipped ids show `accepted\|codify` (pre-UPDATE capture) | ✅ |
| 3.h | flip-capture.txt committed with `[100026]` subject | ✅ |
| 4 | Full suite: `full-suite-gate2-pt-w28-b.txt`, exit=0 | ✅ |

---

## Notes

- Item 1.b: The raw counts are in `probes-raw.txt`. The receipt row does not quote individual probe tokens to avoid conflicts with landed texts that carry Rule 20 hedging keywords (the suite summary line, Rule 107's kin parenthetical, Rule 109's body, the Rule 45 extension body — MUST-PRESERVE §3).
- Item 4: Full suite exit=0 with no failures. P7 baseline matches. No test drift (`git log --oneline 7ed1884..HEAD -- tests` empty).
- Governance commits verified: `de662398` (PLANNER_TEMPLATE v4.98), `9679c21c` (flip SQL).

---

## Follow-ups

- The twenty-three W=29 accepted rows (442–466 less 457/465) are their own tranches; ordering per thread 95.
- The Planner pushes governance after this step's pause-for-verdict.
- Thread 76 closes at the keyboard (CEO read-back).
- The `propagation_check` numeral-in-string class (100 divergences, all classified) is a rider for thread 96.
- The register hook's four ellipsis refusals this cycle: Planner's quoting habit, not a hook defect.
- Two lesson candidates for the wrap: a HEAD-scoped git show in a multi-commit step; a precondition embedding a value the plan's own step changes.
- 100021's Done text says T-8 fired beside a holding structure-clone proxy — a record error DECLARED per Rule 102, not patched.

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100026/knowledge/qa/evidence/gate2-pt-w28-b-2026-09-02/
Files verified: 3
