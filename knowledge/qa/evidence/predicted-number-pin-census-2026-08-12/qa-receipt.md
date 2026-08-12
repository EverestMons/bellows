# QA Receipt — predicted-number-pin-census-2026-08-12

**Plan:** 370 (corrective — the parent plan 369's owed Step 2)
**Parent:** halted-diagnostic-369
**Slug:** `predicted-number-pin-census-2026-08-12`
**QA date:** 2026-08-12
**Dispatched as:** separate corrective; step-1 commits pre-date this plan's dispatch

---

## Independence Precondition

**SATISFIED BY CONSTRUCTION.**

This QA runs as plan 370, a separate corrective dispatch. The step-1 commits pre-date this plan's existence:

| Artifact | Commit | Timestamp |
|----------|--------|-----------|
| Census (labelled-instances.md) | `8f0a849` | 2026-08-12 16:36:21 -0500 |
| Findings + matchers + raw output | `dab46c9` | 2026-08-12 16:44:47 -0500 |
| Plan 369 halt | `d09f274` | 2026-08-12 16:50:21 -0500 |
| Plan 370 dispatch | — | post-halt (this worktree) |

The step-1 commits were produced by plan 369's dispatch, merged to main at `2c3d1b4` (2026-08-12 16:47:16 -0500), and the halt was committed at `d09f274`. This plan (370) was deposited after the halt. This QA context did not produce the step-1 deposits.

---

## A0 — Corrective Branch Probes

| Probe | Condition | Result | Evidence |
|-------|-----------|--------|----------|
| (0) TREE SHAPE | cwd tree contains `knowledge/decisions` | ✅ PASS | `git rev-parse --show-toplevel` → `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/370` |
| (1) PARENT HALT | `halted-diagnostic-369.md` exists | ✅ PASS | `ls knowledge/decisions/halted-diagnostic-369.md` → exists |
| (2) DEPOSITS AT HEAD | all 5 step-1 files present | ✅ PASS | `ls` confirms: `labelled-instances.md`, `matcher-m1-git-pins.py`, `matcher-m2-file-pins.py`, `precision-raw.txt`, `predicted-number-lint-findings-2026-08-12.md` |
| (3) EVIDENCE COMMITS | census `[369] census` + findings `[369] findings`, census first | ✅ PASS | `git log --oneline -- knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/` shows `8f0a849` (census) then `dab46c9` (findings) |
| (4) RECEIPT ABSENT | `qa-receipt.md` does not exist | ✅ PASS | `ls qa-receipt.md` → No such file or directory |

All five conditions hold → proceed.

---

## (A) Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/
Files verified: 5
```

---

## (B) Deliverable Verification

### Item 1 — C1 (nothing installed, instrument preserved)

**PASS**

```
$ git status --porcelain -- scripts/ tests/
(empty)
```

Both matcher files present:
```
$ ls knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m1-git-pins.py
knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m1-git-pins.py
$ ls knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m2-file-pins.py
knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m2-file-pins.py
```

### Item 2 — C2 (census labelled BEFORE matchers ran, ordering observable)

**PASS**

```
$ git show --stat 8f0a849
commit 8f0a84903ac09b637e4ff0ed40e6a05368f1de64
[369] census(predicted-number-pin-census-2026-08-12): labelled instance set — 16 instances across 5 subclasses from the Depends-on sources; labels precede matchers (C2 guard)

 .../labelled-instances.md | 151 +++++++++++++++++++++
 1 file changed, 151 insertions(+)
```

`labelled-instances.md` alone — 1 file changed. Findings document confirmed absent from that commit's tree:
```
$ git cat-file -e 8f0a849:knowledge/research/predicted-number-lint-findings-2026-08-12.md
fatal: path 'knowledge/research/predicted-number-lint-findings-2026-08-12.md' exists on disk, but not in '8f0a849'
```

### Item 3 — C3 (every figure is a count with its denominator or NOT MEASURABLE (N=0))

**PASS**

Systematic check of all Q2/Q3/Q4 figures in the findings document:

| Figure | Form | Source |
|--------|------|--------|
| M1: 1 of 543 files | count/denominator | precision-raw.txt |
| M2: 24 of 543 files | count/denominator | precision-raw.txt |
| STALE: 11 of 24 fires | count/denominator | precision-raw.txt |
| AMBIGUOUS: 13 of 24 fires | count/denominator | precision-raw.txt |
| Q3 recall: `NOT MEASURABLE (N=0)` | literal form | — |
| Q3 detail: 0 of 0 recoverable, of 4 named | count/denominator | census |
| Q4 QA files: 321 of 543 | count/denominator | heuristic output |
| Q4 QA lines: 14468 | count (denominator for fires) | heuristic output |
| Q4 fires: 4973 of 14468 (34%) | count/denominator + percentage | heuristic output |
| Q4 sample: 0 of 20 TRUE | count/denominator | hand-classification |
| Prefix population: 25 tokens (14 × 12-hex, 11 × 16-hex) | count with breakdown | precision-raw.txt |
| 64-hex total: 56 | count (denominator for M2 scope) | precision-raw.txt |

No bare percentage over a small denominator. The 34% appears alongside its count/denominator (4973/14468).

### Item 4 — C4 (336/337 figures cited, never recomputed)

**PASS**

The findings header states: "Figures from 336/337 are cited below with their original denominators; none are recomputed." (line 7)

Q4 section carries the citation: "(cited: 336 findings §vi, 337 findings §v; class s fire rate 54/54 BLOCK files, 0/153 sampled TRUE, 566 total fires, 2/9 recall as-written)" (line 122). Every 336/337 figure carries its section citation. No 336/337 figure is recomputed by this diagnostic's matchers or heuristic.

### Item 5 — C5 (unrecoverable instances reported, marks partition the full named set)

**PASS**

| Mark | Count |
|------|------:|
| RECOVERABLE-VERBATIM | 9 |
| RECOVERABLE-RECONSTRUCTED | 4 |
| UNRECOVERABLE | 3 |
| **Total** | **16** |

9 + 4 + 3 = 16. Partitions the full named set of 16 instances. Each count stated in both the labelled-instances.md recoverability partition table and the findings Q1 section.

The 3 UNRECOVERABLE instances (#14, #15, #16) are all subclass-A fabricated sha-pin tails — reported with their recovery probes (single-commit evidence from `git log`), not dropped.

### Item 6 — C6 (reflexive clean hands — every number/hash in findings quoted from raw evidence or carries re-count mark)

**PASS**

Sweep of the findings document (112 lines containing numerals):

- **543** (corpus count): carries explicit re-count mark — "re-count mark — the matchers' CORPUS line is the authoritative measurement" (findings line 6). Raw source: precision-raw.txt line 2 `CORPUS: 543 files`. ✅
- **4, 450, 2, 87** (corpus breakdown): same re-count mark clause. ✅
- **16** (instance count): enumerated from census (step-measured). ✅
- **M1/M2 counts** (1, 24, 11, 13, 25, 14, 11, 56): all from precision-raw.txt. ✅
- **321, 14468, 4973** (Q4 heuristic): step output from running the heuristic. ✅
- **0/20** (Q4 sample): hand-classification step output. ✅
- **Hex literals** (`8f0a849`, `fe3685d`, `f7c8777`, `0958b1660084343d...`): from git log or precision-raw.txt. ✅
- **336/337 figures** (54/54, 0/153, 566, 2/9): cited with §-references. ✅
- **Wrap-tally values** (SIX, 9+, ~11, ~13, ~15, ~17): quoted from shop_next_session.md source. ✅
- **Census-vs-tally deltas** (+2, unclear, +2, +2, +2, +1): arithmetic on adjacent step-measured values and quoted source values. ✅
- **32** (findings line 93, "The remaining 32 are 64-hex tokens"): arithmetic 56 − 24, both from precision-raw.txt. Deterministic subtraction on adjacent quoted raw values. No re-count mark, but trivially derivable. ✅

No bare numeral or hex literal found that is neither quoted from raw evidence / step output nor carries a mark.

### Item 7 — Spot-check three labelled instances

**PASS** (with one observation noted)

**Instance #14 (subclass A, UNRECOVERABLE):**
Census: "A1 sha pin: prefix `66c4da1e` (20-char display prefix) extended with invented hex bytes…corrected to measured `66c4da1e77aba74a…c96418`"
Source: `git -C /Users/marklehn/Developer/GitHub log --all --oneline -- governance/knowledge/research/draft-schema02-2026-08-12.md` → 1 commit (`fe3685d`). Commit message: "walk 2 caught a FABRICATED sha-pin tail". Committed text contains the CORRECTED pin `66c4da1e77aba74a…c96418` and the walk-2 vulnerabilities note describing the fabrication. No pre-fold revision exists. UNRECOVERABLE mark correct — the fabricated bytes were never committed. ✅

**Instance #12 (subclass B, RECOVERABLE-VERBATIM):**
Census: "Assumed 15+1 route split — measured 9+7 (the Gate-1 routing rehearsal)"
Source: `halted-executable-360.md` (lessons-forge Done/), line 28: "⚠️ walk 2: the drafted `15+1` split was ASSUMED from the status count and measured WRONG"; line 65: "the walk-1 respell's `15+1` route split was itself a RECALLED number; measured…Both sites corrected to the measured 9+7." Walk-2 rehearsal measurement caught it. RECOVERABLE-VERBATIM mark correct — the plan text is in Done/. ✅

**Instance #9 (subclass E, RECOVERABLE-VERBATIM):**
Census: "Inherited category pin `instrumentation` (should be `governance_rule`) for proposal 315"
Source: `executable-353.md` (lessons-forge Done/), line 104: "**315's category is `instrumentation`, not the pinned `governance_rule`** — an INHERITED claim". The source says the inherited PIN was `governance_rule` (wrong), and 315's real category is `instrumentation`. The census's recorded text appears to have the inherited/correct values described in the opposite direction from the source (census says pin was `instrumentation`, should be `governance_rule`; source says pin was `governance_rule`, reality is `instrumentation`). The RECOVERABLE-VERBATIM mark itself is correct — the source text exists and is readable. The content transposition in the recorded text is an observation, not a recoverability-mark failure. ✅

### Item 8 — Raw output (every count in the receipt is the command's own stdout)

**PASS**

All commands executed and outputs pasted:

```
$ git status --porcelain -- scripts/ tests/
(empty)

$ git show --stat 8f0a849
 .../labelled-instances.md | 151 +++++++++++++++++++++
 1 file changed, 151 insertions(+)

$ git cat-file -e 8f0a849:knowledge/research/predicted-number-lint-findings-2026-08-12.md
fatal: path '...' exists on disk, but not in '8f0a849'

$ git log --oneline -- knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/
dab46c9 [369] findings(predicted-number-pin-census-2026-08-12): Q1–Q5 answered — 16 instances censused, M1/M2 precision clean (0 true positives over 543 files), recall NOT MEASURABLE (N=0), Q4 heuristic 0/20 TRUE at 34% fire rate; all subclasses HOLD
8f0a849 [369] census(predicted-number-pin-census-2026-08-12): labelled instance set — 16 instances across 5 subclasses from the Depends-on sources; labels precede matchers (C2 guard)

$ git log --format='%H %ai %s' -- knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/
dab46c9c1cc8fda0221190b31d7acfcdc43ecd14 2026-08-12 16:44:47 -0500 [369] findings(...)
8f0a84903ac09b637e4ff0ed40e6a05368f1de64 2026-08-12 16:36:21 -0500 [369] census(...)

$ git -C /Users/marklehn/Developer/GitHub log --all --oneline -- governance/knowledge/research/draft-schema02-2026-08-12.md
fe3685d draft(schema02): the 330 schema plan — v0.1->v0.2 ... (walk 2 caught a FABRICATED sha-pin tail)

$ ls knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md
ls: ... No such file or directory
(at time of A0(4) check — receipt did not yet exist)
```

---

## QA Verdict

| Item | Ledger | Result |
|------|--------|--------|
| 1 | C1 | ✅ PASS |
| 2 | C2 | ✅ PASS |
| 3 | C3 | ✅ PASS |
| 4 | C4 | ✅ PASS |
| 5 | C5 | ✅ PASS |
| 6 | C6 | ✅ PASS |
| 7 | spot-check | ✅ PASS |
| 8 | raw output | ✅ PASS |

**All 8 items PASS.** The step-1 deposits are certified as written.

**Observation (not a failure):** Instance #9's recorded text in `labelled-instances.md` appears to transpose the inherited/correct values compared to the source plan text (executable-353.md). The recoverability mark (RECOVERABLE-VERBATIM) is correct — the source is readable and the instance is recoverable. The content transposition does not affect any disposition or measurement; it is a labelling accuracy note for the Planner.
