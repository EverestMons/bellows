# Dev Log — lint-class-census step 2 (2026-08-10)

## Task S2-A0 — Precondition checks

- **Step 1 deposits exist:** `git log --oneline -- knowledge/qa/evidence/lint-class-census-2026-08-10/` → `30c3d23 [336] lint-class-census-2026-08-10 step 1 — Q1 frequency and Q3 FP surface over final states`
- **Rubric unchanged:** `git diff HEAD -- knowledge/qa/evidence/lint-class-census-2026-08-10/classification-rubric.md` — empty (no change since Step 1 commit).
- **Corpus movement:**
  - bellows main HEAD: `53b9227` (unchanged from Step 1 PIN)
  - bellows Done/ count: 446 (was 445 in Step 1; +1)
  - governance root HEAD: `9d79d0e` (was `706676a` in Step 1; **moved**)
  - Total Done/*.md: 1710 (was 1695 in Step 1; **+15 files**)
  - **Reported as corpus movement, not absorbed.** Pre-fold analysis uses fixed commit hashes from draft histories, so the movement does not affect Q2/Q4 measurements. The Q1/Q3 measurements from Step 1 were taken at the pinned corpus and are not retroactively adjusted.

## Task S2-B — Covered population

**11 drafts found** across 3 repositories (bellows: 4, shop root: 5, lessons-forge: 2).

**Covered set (10 drafts — each has a deposited Done/ plan):**

| Draft slug | Repo | Commits | Done/ file | Join key |
|---|---|---:|---|---|
| clean-gate-auto-continue | bellows | 14 | executable-317.md | slug |
| lens-mechanization-census | bellows | 11 | diagnostic-322.md | slug |
| lint-subcheck-trio | bellows | 15 | executable-324.md | slug |
| verdict-mechanization-distribution-refresh | bellows | 8 | diagnostic-315.md | slug |
| lint-s4-hardening | shop root | 13 | executable-332.md | slug |
| gate2-s5-conformance | shop root | 18 | executable-330.md | slug |
| seat-brief-codification | shop root | 19 | executable-329.md | slug |
| template-qa-and-terminal-correction | shop root | 14 | executable-320.md | slug |
| cycle-run | lessons-forge | 16 | executable-311.md | slug |
| gate1-routing | lessons-forge | 11 | executable-326.md | slug |

Total covered commits: **139**

**Uncovered set (1 draft):**

| Draft slug | Repo | Commits | Reason |
|---|---|---:|---|
| brewbuddy-shop-import-census | shop root | 7 | No close commit; still in draft (parked for confirming walk) |

The covered set exceeds three (it is 10), so the diagnostic's unsatisfiability clause does not fire.

## Task S2-C — Q4: matchers against pre-fold revisions

Script: `pre-fold-scan.py` in scratch directory `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.7qxukpMaPm/`.

For each covered draft, iterated through all per-phase commits using `git log --all --reverse --follow -- <draft-path>`. For each commit, extracted the file via `git show <sha>:<path>` and ran all four matchers.

Output: 516 data rows (10 drafts x ~4 classes x variable commits) in `pre-fold-raw.tsv` → deposited as `pre-fold-matches.txt`.

### Count-decrease events (candidate fold-outs)

| Class | Draft | Prev | Curr | Delta | Spot-verified |
|---|---|---:|---:|---:|---|
| m | cycle-run | 10 | 9 | -1 | RESTRUCTURING |
| m | lint-s4-hardening | 3 | 1 | -2 | RESTRUCTURING — check (m) section cut |
| m | template-qa | 5 | 4 | -1 | RESTRUCTURING |
| q | cycle-run | 3 | 2 | -1 | RESTRUCTURING (same commit as m) |
| q | template-qa | 1 | 0 | -1 | RESTRUCTURING |
| s | clean-gate-auto-continue | 10 | 9 | -1 | RESTRUCTURING |
| s | cycle-run | 15 | 14 | -1 | RESTRUCTURING |
| s | gate2-s5-conformance | 8 | 7 | -1 | RESTRUCTURING |
| s | lint-s4-hardening | 9 | 6 | -3 | RESTRUCTURING — section removal |
| s | lint-subcheck-trio | 11 | 10 | -1 | RESTRUCTURING |
| s | lint-subcheck-trio | 12 | 11 | -1 | RESTRUCTURING |
| s | seat-brief-codification | 1 | 0 | -1 | RESTRUCTURING (re-appears next commit) |
| s | template-qa | 11 | 10 | -1 | RESTRUCTURING |

Total candidate events: 13. Spot-verified sample: lint-s4-hardening (m: diff read, confirmed section removal of check-m prose), lint-s4-hardening (s: diff read, confirmed section removal), cycle-run (m+q: diff read, confirmed prose condensation). **Verified fraction: 0/4 confirmed as defect folds. All verified as restructuring.**

### Verified true positives: 0 across all four classes.

## Task S2-D — Q2: re-finding rate

Definition: a re-find is a match present at revision N, absent at N+1, present again at N+2 or later, within one draft's history. "Present" = count > 0. This is an operational stand-in for fold events, which are not directly observable from commits.

| Class | Re-finds | Details |
|---|---:|---|
| m | 0 | — |
| q | 1 | template-qa: counts [0,1,1,1,1,1,0,1,1,2,2,2,2] |
| r | 0 | — |
| s | 1 | seat-brief: counts [1,0,2,2,2,2,3,5,5,7,7,7,7,10,10,10,10,11] |

**Detection floor:** per-phase commits are per walk or culmination, not per fold. A single commit can contain multiple folds. Q2 therefore systematically under-counts re-finds, and these figures are lower bounds, never rates.

The covered set exceeds five drafts (10). Cross-draft averages: m 0/10 = 0.0, q 1/10 = 0.1, r 0/10 = 0.0, s 1/10 = 0.1. These averages are reported but given the zero-heavy distribution, they convey nothing the per-draft numbers do not.

## Task S2-E — Q5: dispositions

| Class | Disposition | Reason |
|---|---|---|
| m | REDESIGN | No verified TP; false fires share an excludable shape (non-ASCII in prose vs. in -F argument) |
| q | REDESIGN | No verified TP; false fires share an excludable shape (metachar in non-F-argument quotes); 1 AMBIGUOUS counts against |
| r | REDESIGN | No verified TP; false fires share an excludable shape (| as regex alternation vs. pipe) |
| s | HOLD | No verified TP; false fires are structurally identical to true positives (correct vs. incorrect counts); no redesign path within regex |

## Deposit verification

Before commit:
- `knowledge/qa/evidence/lint-class-census-2026-08-10/pre-fold-matches.txt` — present (517 lines incl. header)
- `knowledge/research/lint-class-census-findings-2026-08-10.md` — present, one section per class with items (i)-(vii)
- `knowledge/development/lint-class-census-dev-log-step-2-2026-08-10.md` — present (this file)

## Scratch directory

All scripts in `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.7qxukpMaPm/`. Not installed (C1 satisfied).
