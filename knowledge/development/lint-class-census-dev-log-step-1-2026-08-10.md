# Dev Log — lint-class-census step 1 (2026-08-10)

## Task A0 — Branch determination

- **(1) NOT-INSTALLED guard:** `git status --porcelain -- scripts/ tests/` — empty.
- **(1b) CLEANLINESS:** `git status --porcelain -- knowledge/qa/ knowledge/research/ knowledge/development/` — empty.
- **(2) RE-ENTRY key:** `git log --oneline -- knowledge/qa/evidence/lint-class-census-2026-08-10/` — no output.
- **Branch: FRESH.**

## Task PIN — Corpus pins

- Done/ `*.md` file count (bellows): **445**
- Done/ `*.md` file count (all repos under shop root): **1695**
- bellows HEAD: `53b922710ab0ecbc4b8aa7e083d64c26fd54be2c`
- governance root HEAD: `706676ad6677b13924245062a554216250cd1cd2`
- git toplevel: `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/336`

## Task B — Prototype matchers

Scratch directory: `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.7qxukpMaPm`

Script: `census-matchers.py` — single Python script, four matchers.

### Matcher source (verbatim)

**m** — non-ASCII inside a -F literal:
```python
GREP_F_RE = re.compile(r'grep\b.*-[A-Za-z]*F')

def match_m(line):
    if not GREP_F_RE.search(line):
        return False
    return any(ord(c) > 127 for c in line)
```
Fires when line has grep with -F AND any non-ASCII character on the same line.

**q** — shell metacharacter inside a -F literal:
```python
GREP_F_RE = re.compile(r'grep\b.*-[A-Za-z]*F')
QUOTED_RE = re.compile(r'"([^"]*)"|\'([^\']*)\'')

def match_q(line):
    if not GREP_F_RE.search(line):
        return False
    for m in QUOTED_RE.finditer(line):
        content = m.group(1) or m.group(2) or ''
        if '`' in content or '$' in content or '!' in content:
            return True
    return False
```
Fires when line has grep -F AND a quoted string containing backtick, $, or !.

**r** — grep -c piped into another command:
```python
GREP_C_PIPE_RE = re.compile(r'grep\b[^|]*-[A-Za-z]*c[A-Za-z]*\b[^|]*\|')

def match_r(line):
    return bool(GREP_C_PIPE_RE.search(line))
```
Fires when line has grep with -c flag followed by a pipe character.

**s** — numeral asserting the size of an enumeration:
```python
NUMBER_WORDS = ['two', 'three', ..., 'twenty']
ENUM_NOUNS = r'items?|steps?|files?|checks?|sites?|...'
S_RE = re.compile(rf'\b({NW_ALT})\s+({ENUM_NOUNS})\b', re.IGNORECASE)

def match_s(line):
    return bool(S_RE.search(line))
```
Fires when a word-numeral (two-twenty) directly precedes an enumeration noun. Digits excluded (narrower matcher).

## Task C.1 — Stratum from plan 335

Source: `git show efae953:knowledge/qa/evidence/cycle-yields-collector-2026-08-10/corpus-run.txt`
Path read successfully (relative to bellows repo root, not shop root).

Partition from 335's status column:
- 342 rows OK + 194 rows UNPARSEABLE = **536 BLOCK-CARRYING rows** across **54 unique files**
- 1633 rows NO_BLOCK across **1633 unique files**
- Total unique files in corpus-run.txt: **1687**
- 8 files on disk (1695) but not in corpus-run.txt — closed after 335 ran.

Note: plan 335 reports 61 block-carrying files; this parsing yields 54. The delta is unresolved — possibly parser-sensitivity differences.

## Task C.2 — Classification rubric

Deposited BEFORE any match was seen at:
`knowledge/qa/evidence/lint-class-census-2026-08-10/classification-rubric.md`

Six criteria: R1 (TRUE), R2 (FALSE-descriptive), R3 (FALSE-quoted), R4 (AMBIGUOUS), R5 (FALSE-s-numeral-matches), R6 (FALSE-s-non-enumerative).

## Task C.3 — Cap policy

322 classified **174 findings exhaustively by hand**. This census produces **1926 matches** across 1695 files — 11x larger, populations not comparable. Cap policy: **apply stride sampling per C.5.** Stride N = ceil(total / 60) within each stratum per class. Decision recorded before any match was counted.

## Task C.4 — Raw match counts

| Class | BLOCK | NO_BLOCK | UNKNOWN | Total |
|-------|------:|---------:|--------:|------:|
| m | 162 | 18 | 14 | **194** |
| q | 55 | 8 | 5 | **68** |
| r | 15 | 219 | 0 | **234** |
| s | 566 | 828 | 36 | **1430** |
| **Total** | **798** | **1073** | **55** | **1926** |

## Task C.5 — Stride sampling

| Class | Stratum | Total | Stride | Sample | Remainder |
|-------|---------|------:|-------:|-------:|----------:|
| m | BLOCK | 162 | 3 | 54 | 108 |
| m | NO_BLOCK | 18 | 1 | 18 | 0 |
| m | UNKNOWN | 14 | 1 | 14 | 0 |
| q | BLOCK | 55 | 1 | 55 | 0 |
| q | NO_BLOCK | 8 | 1 | 8 | 0 |
| q | UNKNOWN | 5 | 1 | 5 | 0 |
| r | BLOCK | 15 | 1 | 15 | 0 |
| r | NO_BLOCK | 219 | 4 | 55 | 164 |
| s | BLOCK | 566 | 10 | 57 | 509 |
| s | NO_BLOCK | 828 | 14 | 60 | 768 |
| s | UNKNOWN | 36 | 1 | 36 | 0 |

Total sampled: **377** of 1926.

## Task C.6 — Classification results

| Class | TRUE | FALSE | AMBIGUOUS | Sampled |
|-------|-----:|------:|----------:|--------:|
| m | 0 | 86 | 0 | 86 |
| q | 0 | 67 | 1 | 68 |
| r | 0 | 70 | 0 | 70 |
| s | 0 | 153 | 0 | 153 |
| **Total** | **0** | **376** | **1** | **377** |

### Key findings driving zero TRUE:

**m** — ALL 194 matches have non-ASCII in prose (em-dashes, bullet marks), never inside a -F pattern argument. Verified programmatically: extracted quoted strings after -F flags across all 194 matches, none contained non-ASCII. The matcher fires because plan lines mentioning `grep -F` also have non-ASCII in surrounding instructional prose.

**q** — 65 of 68 matches have metacharacters in OTHER quoted strings on the line (e.g., `"$?"` for exit-code checking). 3 matches have metacharacters in -F pattern arguments:
1. `grep -F "$slug"` — intentional shell variable expansion (FALSE/R2)
2. `grep -F "$B"` — match artifact from long line (FALSE/R2)
3. `grep -n -F "AND status != 'retired'"` — `!` present in `!=` context; would not trigger history expansion, but the character IS in the pattern (AMBIGUOUS/R4)

**r** — ALL 15 BLOCK matches and all NO_BLOCK stride matches: the `|` character that triggers the matcher is inside grep regex patterns (regex alternation `|`), markdown table cells, or grep receives from a pipe (not sending to one). One genuine `grep -c | tee` case found outside stride (executable-bellows-worktree-tests-2026-05-03.md:147, NO_BLOCK) but the plan reads the printed count, not the exit code.

**s** — ALL sampled matches are numerals that correctly match their enumerations (FALSE/R5) or are used in non-enumerative contexts (FALSE/R6). This is expected: Done/ files passed QA, so count mismatches were folded out during drafting cycles.

### The AMBIGUOUS match

**executable-321.md line 49** (class q, BLOCK stratum):
```
grep -n -F "AND status != 'retired'" web/carrier_profiles.py
```
The `!` in `!= 'retired'` is technically inside the -F pattern. History expansion in bash requires `!word` or `!!` patterns; `!=` is not a valid event designator and would not trigger expansion. However, the character IS present. A lint check flagging any `!` in double-quoted -F patterns would fire here. Classified AMBIGUOUS because the defect is technically present but would not cause the stated failure mode.

## Q1 — Frequency (BLOCK-carrying stratum)

| Class | Files with match | Total matches | Max matches/file |
|-------|-----------------|---------------|-----------------|
| m | 40 / 54 | 162 | 24 |
| q | 21 / 54 | 55 | 10 |
| r | 7 / 54 | 15 | 4 |
| s | 54 / 54 | 566 | 41 |

**m distribution (BLOCK):** 15 files with 1, 5 with 2, 5 with 3, 5 with 4, 2 with 5, 1 with 6, 1 with 7, 2 with 9, 2 with 12, 1 with 13, 1 with 24. Concentrated in plans with extensive grep instructions.

**q distribution (BLOCK):** 8 with 1, 6 with 2, 2 with 3, 2 with 4, 1 with 5, 1 with 6, 1 with 10. The 10-match file is heavily grep-oriented.

**r distribution (BLOCK):** 3 with 1, 1 with 2, 2 with 3, 1 with 4. Rare and concentrated in plans discussing exit-code handling.

**s distribution (BLOCK):** ALL 54 BLOCK files have at least one match. 6 with 1, 6 with 2, then long tail up to 41. Every plan with a Drafting Cycle uses number-word + noun patterns.

## Q1 — Frequency (NO_BLOCK stratum)

| Class | Files with match | Total matches |
|-------|-----------------|---------------|
| m | 17 / 1633 | 18 |
| q | 8 / 1633 | 8 |
| r | 182 / 1633 | 219 |
| s | 506 / 1633 | 828 |

r is notable: 182 NO_BLOCK files contain `grep -c` + `|` — the `|` is almost always regex alternation inside the pattern or a markdown table cell, not a shell pipe.

## Scratch directory

All matchers in `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.7qxukpMaPm/`. Not installed (C1 satisfied).
