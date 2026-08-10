# Dev Log — lint-class-recall Step 1 (2026-08-10)

**Diagnostic:** 337
**Slug:** `lint-class-recall-2026-08-10`
**Step:** 1 — DEV (labelled set, then recall)

---

## Task A0 — Branch selection

- **(1) NOT-INSTALLED guard:** `git status --porcelain -- scripts/ tests/` returned empty. PASS.
- **(1b) CLEANLINESS:** `git status --porcelain -- knowledge/qa/ knowledge/research/ knowledge/development/` returned empty. PASS.
- **(2) RE-ENTRY key:** `git log --oneline -- knowledge/qa/evidence/lint-class-recall-2026-08-10/labelled-positives.txt` returned no commit matching the slug. No re-entry.
- **(3) PRE-SEEDED:** `knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/` exists and is committed at `9b8c56b`. Treated as expected pre-seed, not re-entry.

**Branch: FRESH.** Proceeded at Task B.

## Task B — Verify pre-seeded instrument

`census-matchers.py` present at `knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/census-matchers.py`. Confirmed it contains the class-s noun-list identifier `ENUM_NOUNS`. All four matcher functions present: `match_m`, `match_q`, `match_r`, `match_s`.

Matcher sources: all from the deposited pre-seeded copy (commit `9b8c56b`).

## Task C — Build labelled positive set

### C.1 — Register read

Read `governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` in full from pinned commit `a7077ca` via `git show a7077ca:governance/...`. 431 lines.

Register pin verified: `git log -1 --format="%H" -- governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` returned `a7077caa012bb8dbfb35639c9ba36ab84443c8c8`, matching the authoring-time pin.

### C.2 — Instance enumeration

Authoring-time list cited lines 19, 22, 25, 87, 136, 270, 361, 414.

**Corrections to authoring-time list:**
- Line 136: NOT an instance — it is about C3's count-word check scope (would fire on Cycle Log summary counts backed by the register, not on wrong enumerations). Removed.
- Line 361: NOT a class-r instance — describes a walk methodology observation where `grep -c` recount returned MORE because fold notes quote stale wording. The `grep -c` was not piped. Moved to "Instances covered by no class."

**Additional instances found (all class s):**
- Line 13: "Three plan_lint warn-first checks" then enumerates seven
- Line 16: "two files" when six deposits were declared
- Line 23: "the eight probes" then lists ten
- Line 327: "TWO new repo files" — wrong since draft v1
- Line 328: "four deposits of Steps 1 and 2" became five
- Line 355: "Step 3's own TWO deposits" — became three
- Line 374: "exactly six paths" — stale count

**Final labelled set: 14 instances across 4 classes (m:3, q:1, r:1, s:9).**

### C.2b — Class assignment justification

Each instance justified against the matcher's own regex definition. One instance (line 361) judged as not covered by any class — reported in "Instances covered by no class" section of findings.

### C.3 — Q1 recoverability

All 14 instances: RECOVERABLE-RECONSTRUCTED. 0 VERBATIM, 0 UNRECOVERABLE.

The register describes defects as descriptions, not as the original lines. The pre-fold source text has exactly one commit (the session wrap), so pre-fold revisions are not available in git history. The undeposited draft shows only post-fold (corrected) text. Each reconstruction is built from the register's description combined with the draft's corrected form, working backward to what the original line must have been.

### C.4 — Labelled set committed

`labelled-positives.txt` committed alone at `320d547` (`evidence(337): [337] labelled positive set for lint-class recall`). No findings document in that commit's tree. C2 ordering guard satisfied.

## Task D — Q2 and Q3: matcher recall

### Redesigned matchers written

`redesigned-m-q.py` written with `extract_f_operand()` function that parses the command to find the actual `-F` operand using `shlex.split` with regex fallback.

### Positive controls run BEFORE recall measurement

Both controls PASS — each redesigned matcher separates defect-present from defect-absent lines:
- m-redesigned: fires on non-ASCII inside `-F` operand, does not fire on non-ASCII outside it
- q-redesigned: fires on backtick inside `-F` operand, does not fire on backtick outside it

### Recall results

**As-written:**
- m: 3 of 3 reconstructed, of 3 named
- q: 1 of 1 reconstructed, of 1 named
- r: 1 of 1 reconstructed, of 1 named (fires for wrong reason — catches pattern-internal `|`, not shell pipe)
- s: 2 of 9 reconstructed, of 9 named (i7 "two files" and i13 "six paths" fire; 7 miss)

**Redesigned (m and q only):**
- m-redesigned: 3 of 3 reconstructed, of 3 named
- q-redesigned: 1 of 1 reconstructed, of 1 named

**Verbatim recall: 0 for all classes (no verbatim rows exist).**

### s-class miss analysis

7 of 9 s instances miss. Four distinct causes:
1. Intervening words (i6, i11): numeral and noun separated by other words
2. Bold formatting (i8, i12, i14): `**numeral**` places `**` between numeral and whitespace
3. Vocabulary gap — noun (i9): "values" not in ENUM_NOUNS
4. Vocabulary gap — numeral (i10): "twice" not in NUMBER_WORDS

### Q3 finding: machine-countable enumerations

Several s instances have machine-countable enumerations in the same block (parenthesized items, numbered lists, bulleted lists). A tool that detects a numeral-noun pattern AND counts the associated enumeration could verify counts — addressing 336's objection that a regex cannot verify a count by not being a regex. Reported as a finding, not as grounds to change the s disposition.

## Task E — Q4 revised dispositions

- **m: REDESIGN** — precision 0/86 (336), recall 3/3 reconstructed (0 verbatim). Redesigned matcher written, 3/3 recall, precision unmeasured.
- **q: REDESIGN** — precision 0/67+1AMB (336), recall 1/1 reconstructed (0 verbatim). Redesigned matcher written, 1/1 recall, precision unmeasured.
- **r: REDESIGN** — precision 0/70 (336), recall 1/1 reconstructed (0 verbatim). Not redesigned here; the 1/1 hit is accidental (catches pattern-internal `|`).
- **s: HOLD** — precision 0/153 (336), recall 2/9 reconstructed (0 verbatim). 336's ground (regex cannot verify count) unchanged. Machine-countable-enumeration mechanism reported as new finding.

**SHIP-warn blocked for all classes:** 0 verbatim hits across the entire labelled set.

## Task F — C1 assertion

- `git status --porcelain -- scripts/ tests/` returned empty. Nothing installed. PASS.
- Both matcher files present under `knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/`:
  - `census-matchers.py` (pre-seeded at `9b8c56b`)
  - `redesigned-m-q.py` (written in Task D)
- C1 satisfied in full.

## Deposits (Commit 2)

- `knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/redesigned-m-q.py`
- `knowledge/qa/evidence/lint-class-recall-2026-08-10/positive-controls.txt`
- `knowledge/research/lint-class-recall-findings-2026-08-10.md`
- `knowledge/development/lint-class-recall-dev-log-step-1-2026-08-10.md`
