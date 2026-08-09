# Lint Sub-check Trio — QA Report (Plan 324)

**Date:** 2026-08-08
**Step:** 2 (QA)
**Agent:** Bellows QA

---

## Task Q0 — Re-pin

| Check | Result |
|---|---|
| `git status --porcelain` (4 files) | Clean |
| Latest commit touching pathspec | `9c06524` — Step 1's commit ("[324] lint sub-check trio Step 1") |
| `gates.py` foreign commit | None — `9c06524` is Step 1's |
| PRE_EDIT_HASH (from dev log) | `47976bfa5f888f63bd552ca3b1849a107e43556c` |
| Post-edit blob (`git hash-object`) | `8288606eefe5a93720aa40017073aa4a52ca2f51` |
| Blob matches Step 1's commit | Yes (verified via `git ls-tree 9c06524`) |

### Pre-sweep rev-parse HEAD pins

| Root | Hash |
|---|---|
| anvil | `da17272ee00c82f987052953660940d18b59c1e0` |
| bellows | `9c06524f70cc3e6351c421aabda97e7395a2f7cb` |
| governance | `656dd2f928374e6095e5c5ce7f2b4795c69312e4` |
| invoice-pulse | `1bb0d27b550b23ea4281670bd78a22c3a758c5ae` |
| lessons-forge | `8d7e6c118d30b2c33bbbad9b1b0aaacda8771df8` |

### Post-sweep (bookend) rev-parse HEAD pins

| Root | Hash | Delta |
|---|---|---|
| anvil | `da17272ee00c82f987052953660940d18b59c1e0` | None |
| bellows | `9c06524f70cc3e6351c421aabda97e7395a2f7cb` | None |
| governance | `656dd2f928374e6095e5c5ce7f2b4795c69312e4` | None |
| invoice-pulse | `e4c54e8e931b0de0d6daf628f5c41ec8e3701638` | **DELTA** — concurrent activity (parallel terminal) |
| lessons-forge | `615bcbb00ac70ac479243ebd0c3e979a6a7c11a9` | **DELTA** — concurrent activity (parallel terminal) |

Governance has no `.git`; its pin IS the shop-root repo HEAD by design. The invoice-pulse and lessons-forge deltas are non-corpus shop activity (the parallel terminal is live this week).

---

## Item 1 — Full Bellows Suite

```
915 passed, 1 warning in 23.89s
```

Evidence: `knowledge/qa/full-suite.txt` (RAW, last 200 lines including summary).

---

## Item 2 — Targeted Lint Tests

```
97 passed, 818 deselected, 1 warning in 3.93s
```

Evidence: `knowledge/qa/targeted-tests.txt` (RAW).

---

## Item 3 — Corpus Sweep

**Command:** `PLAN_LINT_UNCAP=1 python3 scripts/plan_lint.py <plan>` for every `Done/*.md` in all five roots.

**Corpus:** 1384 files (anvil 57, bellows 443, governance 38, invoice-pulse 779, lessons-forge 67). All exit 0; zero nonzero exit codes.

### Per-check fire counts by root

| Root | (n) WARN | (o1) WARN | (o1) INFO | (o2) WARN | (p) WARN |
|---|---|---|---|---|---|
| anvil | 24 | 19 | 38 | 45 | 0 |
| bellows | 339 | 265 | 303 | 107 | 7 |
| governance | 3 | 17 | 38 | 8 | 39 |
| invoice-pulse | 210 | 285 | 580 | 302 | 0 |
| lessons-forge | 8 | 7 | 64 | 66 | 21 |
| **Total** | **584** | **593** | **1023** | **528** | **67** |

### o1 candidate/excluded/fired per root (from INFO lines)

| Root | Candidates | Excluded | Fired |
|---|---|---|---|
| anvil | 259 | 42 | 19 |
| bellows | 1165 | 346 | 265 |
| governance | 301 | 101 | 17 |
| invoice-pulse | 2361 | 388 | 285 |
| lessons-forge | 529 | 250 | 7 |
| **Total** | **4615** | **1127** | **593** |

INFO fired total (593) matches WARN count (593) — consistent. Zero `(+` tail lines in corpus-sweep.txt — uncap confirmed.

### Sweep-diff proof

Pre-edit binary: `git show 47976bf:scripts/plan_lint.py` into fresh `mktemp -d`. Post-edit binary: current `scripts/plan_lint.py` (blob `8288606eefe5a93720aa40017073aa4a52ca2f51`, verified against Step 1's commit). Both runs under `PLAN_LINT_UNCAP=1`, only lint stdout in diffed streams.

**Result:** 4938 lines in sweep-diff.txt. **Zero removed lines** (no existing check output changed). **Zero added lines without (n)/(o1)/(o1 INFO)/(o2)/(p) labels** — every diff line is an added line carrying a composed label from the new checks.

Evidence: `knowledge/qa/sweep-diff.txt` (RAW).

### Live o1 positive control

Re-materialized Step 1's tripping fixture from the dev log's pasted text at `<tmpdir>/proj/knowledge/decisions/tripping-fixture.md`. Output:

```
(n) WARN: `grep "plan_lint.py" scripts/` — grep on literal pattern without -F (ugrep-shim hazard)
(o1) INFO: candidates=2 excluded=1 fired=1
(o1) WARN: missing path `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/nonexistent-tripping-fixture-xyzzy.txt`
(o2) WARN: Deposits entry `knowledge/development/dev-log.md` is not project-prefixed or absolute
(p) WARN: C1 has no backtick-quoted command or check: token
```
Exit 0. All four labels fire. o1 fires on the absolute missing path — the sweep's zeros are the output of a live check, not a dead one.

### ⚠️ o1 Exclusion HALT — 2 Cases

**HALT case 1:** `lessons-forge/executable-gate-2b-planner-template-edits-2026-05-19.md`
- **Fired:** `governance/knowledge/development/dev-log-gate-2b-step-1-2026-05-19.md`
- **Deposits entry in same file:** `lessons-forge/knowledge/development/dev-log-gate-2b-step-1-2026-05-19.md`
- **Match type:** Prefix-stripped — fired stripped to `knowledge/development/dev-log-gate-2b-step-1-2026-05-19.md`, which equals the Deposits entry stripped.
- **Classification:** Cross-project collision. The fired path is a governance-prefixed inline mention. The Deposits entry is lessons-forge-prefixed. These refer to different files in different projects. The o1 exclusion correctly treats them as different paths (the candidate verbatim does not match any exclusion set entry). The HALT triggers because the independent check strips BOTH the fired path and the entry, producing a match. **This is NOT an implementation defect — it is a design-level question about whether cross-project stripping should exclude.** The file does not exist: TP as an o1 fire.

**HALT case 2:** `lessons-forge/executable-lessons-forge-cycle-2026-05-27.md`
- **Fired:** `knowledge/research/lessons-forge-cycle-step2b-classifications-2026-05-27.md`
- **Deposits entry in same file:** `knowledge/research/lessons-forge-cycle-step2b-classifications-2026-05-27.md` (verbatim match — Step 2B Deposits block)
- **Root cause:** The file has `## STEP 2A` and `## STEP 2B` headers, both parsed as step number "2". `gates._extract_step_text(plan_text, 2)` returns None for the duplicate, so the Step 2B Deposits block is never extracted into the exclusion set. The whole-text extraction (`re.search`) only captures the first Deposits block (Step 1's). **This is a genuine extraction gap** in the `_extract_step_text` helper — duplicate step numbers from lettered sub-steps are not handled. The file does not exist: TP as an o1 fire, but the exclusion should have caught it.

### o1/o2 FP classification

**o1 FP rate: 0/593 = 0%.** Every fired path was verified non-existent at the resolved dual-root locations. The 2 HALT cases are exclusion failures (paths that should have been excluded from candidacy), not false positives (paths that exist but were reported missing). Classification: all 593 fires are TP — paths genuinely missing at resolved locations. The fires come from old plans referencing files that were never created, were renamed, or belong to stale project structures.

**o2 FP rate: 0/528 = 0%.** Every fired Deposits entry lacks a project prefix (first segment is not in the known projects set) and is not `/Users/`-absolute. These are genuine form defects per the deposit-form convention. Classification: all 528 fires are TP.

---

## Item 4 — WARN-only by Mechanism

| Check | Result |
|---|---|
| Positive control: `grep -F '# (n) Non-F grep lint' scripts/plan_lint.py` | HIT (1 match) |
| Negative: `results.append` in new check region | 0 references — PASS |
| Negative: `all_passed` in new check region | 0 references — PASS |
| Exit 0 on tripping fixture (all 4 labels fire) | Exit 0 — PASS |

New checks (n), (o1), (o2), (p) are confirmed WARN-only: none appends to `results`, none assigns `all_passed`.

---

## Item 5 — QA Verification

| # | Item | Status | Detail |
|---|---|---|---|
| 1 | Full bellows suite | ✅ | 915 passed |
| 2 | Targeted lint tests | ✅ | 97 passed, 818 deselected |
| 3a | Corpus sweep (1384 files, 5 roots) | ✅ | All exit 0, per-check counts recorded |
| 3b | Sweep-diff proof | ✅ | Only added (n)/(o1)/(o2)/(p)-labeled lines; zero removed/changed |
| 3c | Uncap verification | ✅ | Zero `(+` tail lines; INFO totals match WARN counts |
| 3d | Live o1 positive control | ✅ | All four labels fire, exit 0 |
| 3e | o1 exclusion HALT check | ❌ | 2 exclusion failures detected — see HALT section above |
| 3f | Bookend rev-parse | ✅ | 2 deltas (invoice-pulse, lessons-forge) — concurrent activity, named |
| 3g | o1 FP classification | ✅ | 0/593 = 0% FP rate |
| 3h | o2 FP classification | ✅ | 0/528 = 0% FP rate |
| 4 | WARN-only mechanism | ✅ | No results/all_passed references; positive control hit; exit 0 |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/
Files verified: 4
```

`required_evidence_files`: `[targeted-tests.txt, full-suite.txt, corpus-sweep.txt, sweep-diff.txt]`

---

## Status

**HALTED** — 2 o1 exclusion failures detected (Item 3e). Awaiting CEO verdict.

## Deposits

- `bellows/knowledge/qa/lint-subcheck-trio-qa-report-2026-08-08.md` — this report
- `bellows/knowledge/qa/targeted-tests.txt`
- `bellows/knowledge/qa/full-suite.txt`
- `bellows/knowledge/qa/corpus-sweep.txt`
- `bellows/knowledge/qa/sweep-diff.txt`

## Ledger Updates

#### Forward Register
NONE

#### Prompt Feedback
No prompt feedback.
