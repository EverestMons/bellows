# Lint-Class Census Findings — 2026-08-10

**Diagnostic:** 336
**Slug:** `lint-class-census-2026-08-10`
**Census date:** 2026-08-10
**Corpus pins (Step 1):** 1695 Done/*.md files; bellows HEAD `53b9227`; governance HEAD `706676a`
**Corpus movement (Step 2):** 1710 Done/*.md files (+15); governance HEAD `9d79d0e` (moved). Pre-fold analysis unaffected — uses fixed commit hashes.

---

## Class m — non-ASCII inside a -F literal

### (i) Matcher source

```python
GREP_F_RE = re.compile(r'grep\b.*-[A-Za-z]*F')

def match_m(line):
    if not GREP_F_RE.search(line):
        return False
    return any(ord(c) > 127 for c in line)
```

Fires when a line contains `grep` with `-F` AND any non-ASCII character anywhere on the same line.

### (ii) Q1 — Frequency (stratified)

**BLOCK-CARRYING stratum (54 files):**
- Files with match: 40 / 54 (74%)
- Total matches: 162
- Max matches/file: 24
- Distribution: 15×1, 5×2, 5×3, 5×4, 2×5, 1×6, 1×7, 2×9, 2×12, 1×13, 1×24

**NO_BLOCK stratum (1633 files):**
- Files with match: 17 / 1633 (1.0%)
- Total matches: 18

### (iii) Q3 — False-positive surface

| Verdict | Count |
|---------|------:|
| TRUE | 0 |
| FALSE | 86 |
| AMBIGUOUS | 0 |
| **Sampled** | **86** |

Stride sample: BLOCK 54/162 (stride 3), NO_BLOCK 18/18 (stride 1), UNKNOWN 14/14 (stride 1). Remainder: 108 BLOCK matches unsampled. Full row-level data in `final-state-matches.txt`.

**No AMBIGUOUS rows.**

ALL 194 matches have non-ASCII in prose (em-dashes, bullet marks), never inside a -F pattern argument. Verified programmatically: extracted quoted strings after -F flags across all 194 matches; none contained non-ASCII.

### (iv) Q2 — Re-finding rate (lower bound)

**0 re-finds** across 10 covered drafts (139 commits).

Covered set: clean-gate-auto-continue (14 commits), lens-mechanization-census (11), lint-subcheck-trio (15), verdict-mechanization-distribution-refresh (8), lint-s4-hardening (13), gate2-s5-conformance (18), seat-brief-codification (19), template-qa-and-terminal-correction (14), cycle-run (16), gate1-routing (11).

Uncovered set: brewbuddy-shop-import-census (no close commit; still in draft).

The covered set exceeds five drafts (10); however, the zero count makes a cross-draft average meaningless. This is a lower bound — per-phase commits are per walk or culmination, not per fold. A class folded and re-introduced inside one commit is invisible to this measurement.

### (v) Q4 — Pre-fold candidate true positives

**4 count-decrease events** found across 3 drafts:
- cycle-run: 10→9 at commit a209a82a
- lint-s4-hardening: 3→1 at commit 8e631fcd
- template-qa-and-terminal-correction: 5→4 at commit 142d674e

**Spot-verified: 0 verified true positives.** All decreases result from plan restructuring — sections removed or condensed (e.g., lint-s4-hardening's check (m) section was cut from the plan, removing prose that discussed grep -F and contained em-dashes; the m matches were in that prose, not in actual -F arguments). The disappearances correspond to text restructuring, not to folds of the non-ASCII-in-F-literal defect.

### (vi) Q5 — Disposition: REDESIGN

**REDESIGN.** Neither shipping bar is met:

(a) No verified candidate true positive on any pre-fold state. The matcher has not been shown to catch a real instance of the defect.

(b) The FALSE fires share a shape the regex cannot exclude: any line containing `grep -F` AND an em-dash, bullet, or other non-ASCII in surrounding prose. Plans routinely use non-ASCII in instructional text on lines that mention `grep -F`, and the matcher cannot distinguish prose non-ASCII from pattern-argument non-ASCII.

**Case against shipping:** the matcher fires on 74% of BLOCK files (40/54), producing 162 matches, ALL of which are false. A lint check with 100% false-positive rate on its target population would generate noise proportional to the corpus size. The precedent (FORWARD row 25) cut a check at 1379/1390 = 99.2% fire rate; this class's BLOCK fire rate is comparable.

**Redesign direction:** restrict the non-ASCII scan to the actual argument following the -F flag, not the entire line. This requires parsing the command structure to identify which quoted string is the -F operand.

### (vii) Taxonomy mapping (diag-322)

Nearest bucket: **M8** ("non-ASCII scan"). However, M8 is scoped to CEO-run scripts, not -F literals — the fit is partial. The class targets a different surface (plan-mandated grep commands) than M8's original scope.

---

## Class q — shell metacharacter inside a -F literal

### (i) Matcher source

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

Fires when a line contains `grep -F` AND any quoted string on the line contains backtick, `$`, or `!`.

### (ii) Q1 — Frequency (stratified)

**BLOCK-CARRYING stratum (54 files):**
- Files with match: 21 / 54 (39%)
- Total matches: 55
- Distribution: 8×1, 6×2, 2×3, 2×4, 1×5, 1×6, 1×10

**NO_BLOCK stratum (1633 files):**
- Files with match: 8 / 1633 (0.5%)
- Total matches: 8

### (iii) Q3 — False-positive surface

| Verdict | Count |
|---------|------:|
| TRUE | 0 |
| FALSE | 67 |
| AMBIGUOUS | 1 |
| **Sampled** | **68** |

All 68 matches sampled exhaustively (stride 1 for all strata). Full row-level data in `final-state-matches.txt`.

**AMBIGUOUS row (1):**

| class | plan_file | line | stratum | fenced | verdict | rubric_ref | matched_text |
|-------|-----------|------|---------|--------|---------|------------|-------------|
| q | executable-321.md | 49 | BLOCK | no | AMBIGUOUS | R4 | `grep -n -F "AND status != 'retired'" web/carrier_profiles.py` |

The `!` in `!= 'retired'` is inside the -F pattern. `!=` is not a valid bash history event designator and would not trigger expansion, but the character IS present. The defect is technically present but would not cause the stated failure mode.

65 of 68 matches have metacharacters in OTHER quoted strings on the line (e.g., `"$?"` for exit-code checking, not in the -F argument). 3 matches have metacharacters in actual -F pattern arguments: 2 are intentional shell variable expansion (`grep -F "$slug"`), 1 is the AMBIGUOUS case above.

### (iv) Q2 — Re-finding rate (lower bound)

**1 re-find** across 10 covered drafts:
- template-qa-and-terminal-correction: q appeared at commit 1, disappeared at commit 6 (count 1→0), reappeared at commit 7 (count 0→1).
  Count trajectory: [0, 1, 1, 1, 1, 1, 0, 1, 1, 2, 2, 2, 2]

Covered set: same 10 drafts as class m. Uncovered set: brewbuddy-shop-import-census.

This is a lower bound. The re-find is at the presence/absence level (count > 0 vs == 0), not at the individual-match level. A match that disappeared and reappeared at a different line within a commit with count > 0 at both ends is invisible.

### (v) Q4 — Pre-fold candidate true positives

**2 count-decrease events** found:
- cycle-run: 3→2 at commit a209a82a
- template-qa-and-terminal-correction: 1→0 at commit 7a5ae48b (then reappears — this is the Q2 re-find)

**Spot-verified: 0 verified true positives.** The cycle-run decrease is part of the same restructuring commit that reduced m (prose section condensed). The template-qa decrease is a section rewrite that temporarily removed text containing `$` in a quoted string on a grep -F line.

### (vi) Q5 — Disposition: REDESIGN

**REDESIGN.** Neither shipping bar is met:

(a) No verified candidate true positive.

(b) The FALSE fires share a shape the regex cannot exclude: any quoted string containing backtick/$/! on a line with `grep -F`, regardless of whether that quoted string is the -F argument. Plans routinely have `"$?"`, `"$slug"`, and other shell constructs on lines that also mention `grep -F`.

**Case against shipping:** 65/68 matches (96%) fire on metacharacters in quotes that are NOT the -F argument. The matcher conflates "a line mentions grep -F and also mentions a shell variable" with "the -F argument contains a shell metacharacter." The 1 AMBIGUOUS match counts against shipping per the diagnostic's standing rule.

**Redesign direction:** parse the command to identify which quoted string is the operand of -F, and check only that string.

### (vii) Taxonomy mapping (diag-322)

No existing bucket. Nearest is **O** ("other-mechanizable — propose it precisely enough to implement"). The `q` class is genuinely new — 322's taxonomy does not cover shell-metacharacter checking in -F patterns.

---

## Class r — grep -c piped into another command

### (i) Matcher source

```python
GREP_C_PIPE_RE = re.compile(r'grep\b[^|]*-[A-Za-z]*c[A-Za-z]*\b[^|]*\|')

def match_r(line):
    return bool(GREP_C_PIPE_RE.search(line))
```

Fires when a line contains `grep` with `-c` flag followed by a pipe `|` character.

### (ii) Q1 — Frequency (stratified)

**BLOCK-CARRYING stratum (54 files):**
- Files with match: 7 / 54 (13%)
- Total matches: 15
- Distribution: 3×1, 1×2, 2×3, 1×4

**NO_BLOCK stratum (1633 files):**
- Files with match: 182 / 1633 (11%)
- Total matches: 219

Notable: r fires more in NO_BLOCK than BLOCK. 182 NO_BLOCK files contain `grep -c` + `|` — the `|` is almost always regex alternation inside the pattern or a markdown table cell, not a shell pipe.

### (iii) Q3 — False-positive surface

| Verdict | Count |
|---------|------:|
| TRUE | 0 |
| FALSE | 70 |
| AMBIGUOUS | 0 |
| **Sampled** | **70** |

Stride sample: BLOCK 15/15 (stride 1), NO_BLOCK 55/219 (stride 4). Remainder: 164 NO_BLOCK matches unsampled. Full row-level data in `final-state-matches.txt`.

**No AMBIGUOUS rows.**

The `|` that triggers the matcher is: regex alternation inside the grep pattern, markdown table cells, or grep receiving from a pipe (not sending to one). One genuine `grep -c | tee` case found outside stride (executable-bellows-worktree-tests-2026-05-03.md:147, NO_BLOCK) but the plan reads the printed count, not the exit code.

### (iv) Q2 — Re-finding rate (lower bound)

**0 re-finds** across 10 covered drafts.

Covered/uncovered sets same as class m.

### (v) Q4 — Pre-fold candidate true positives

**0 count-decrease events.** The class never fired and then stopped firing in any draft. In the 2 drafts where it appeared (cycle-run: constant at 1; seat-brief-codification: appeared at commit 12 and remained), it was stable or increasing.

**0 candidate true positives. 0 verified true positives.**

### (vi) Q5 — Disposition: REDESIGN

**REDESIGN.** Neither shipping bar is met:

(a) No candidate true positive at all — not even an unverified one.

(b) The FALSE fires share a shape the regex cannot exclude: the `|` character appears as regex alternation (`grep -c 'pattern1|pattern2'`), in markdown table rows, and in other non-pipe contexts. The regex cannot distinguish a shell pipe from these uses.

**Case against shipping:** the matcher fires 13× more in NO_BLOCK (219 matches) than BLOCK (15 matches). A check that fires predominantly on files that never went through a drafting cycle is measuring a surface that has nothing to do with cycle-introduced defects. The 0 candidate TPs across 139 pre-fold commits means this class has never been observed in the wild.

**Redesign direction:** require the `|` to be outside quoted strings and preceded by a command-termination boundary, or use shell-aware parsing to distinguish pipe operators from regex/markdown characters.

### (vii) Taxonomy mapping (diag-322)

Adjacent to **M3** (which flags non-`-F` greps) but not the same check. M3 targets grep without fixed-strings mode; r targets a specific pipe-exit-code interaction with `-c`. The fit is partial — r is a specialization of the exit-code-handling surface that M3 does not cover.

---

## Class s — numeral asserting the size of an enumeration

### (i) Matcher source

```python
NUMBER_WORDS = ['two', 'three', ..., 'twenty']
ENUM_NOUNS = r'items?|steps?|files?|checks?|...'  # ~70 noun patterns
S_RE = re.compile(rf'\b({NW_ALT})\s+({ENUM_NOUNS})\b', re.IGNORECASE)

def match_s(line):
    return bool(S_RE.search(line))
```

Fires when a word-numeral (two through twenty, digits excluded) directly precedes an enumeration noun. Full noun list in `census-matchers.py` (scratch directory).

### (ii) Q1 — Frequency (stratified)

**BLOCK-CARRYING stratum (54 files):**
- Files with match: **54 / 54 (100%)**
- Total matches: 566
- Max matches/file: 41
- Distribution: 6×1, 6×2, then long tail up to 41. Every BLOCK file has at least one match.

**NO_BLOCK stratum (1633 files):**
- Files with match: 506 / 1633 (31%)
- Total matches: 828

### (iii) Q3 — False-positive surface

| Verdict | Count |
|---------|------:|
| TRUE | 0 |
| FALSE | 153 |
| AMBIGUOUS | 0 |
| **Sampled** | **153** |

Stride sample: BLOCK 57/566 (stride 10), NO_BLOCK 60/828 (stride 14), UNKNOWN 36/36 (stride 1). Remainder: 509 BLOCK + 768 NO_BLOCK unsampled. Full row-level data in `final-state-matches.txt`.

**No AMBIGUOUS rows.**

ALL sampled matches are either numerals that correctly match their enumerations (R5) or numerals used in non-enumerative contexts like version numbers or measurements (R6). This is expected: Done/ files passed QA, so count mismatches were folded out during drafting cycles.

### (iv) Q2 — Re-finding rate (lower bound)

**1 re-find** across 10 covered drafts:
- seat-brief-codification: s present at commit 0 (count 1), absent at commit 1 (count 0), present again at commit 2 (count 2).
  Count trajectory: [1, 0, 2, 2, 2, 2, 3, 5, 5, 7, 7, 7, 7, 10, 10, 10, 10, 11]

Covered/uncovered sets same as class m.

This is a lower bound. The re-find is at presence/absence level.

### (v) Q4 — Pre-fold candidate true positives

**7 count-decrease events** found across 5 drafts:
- clean-gate-auto-continue: 10→9 at last commit
- cycle-run: 15→14 at commit 4
- gate2-s5-conformance: 8→7 at commit 12
- lint-s4-hardening: 9→6 at commit 7 (largest decrease)
- lint-subcheck-trio: 11→10, 12→11 (two events)
- template-qa-and-terminal-correction: 11→10 at commit 10

**Spot-verified: 0 verified true positives.** All count decreases result from plan restructuring (sections condensed, bullets removed, prose rewritten). The lint-s4-hardening 9→6 decrease corresponds to the cut of the check-(m) section, which removed three number-word + noun patterns from the prose (e.g., "three options", "eleven total firings"). These were accurate counts in descriptive prose, not incorrect enumeration assertions that were folded.

### (vi) Q5 — Disposition: HOLD

**HOLD.** The shipping bar is not met:

(a) No verified candidate true positive. The matcher has not been shown to catch a wrong enumeration count in any pre-fold state. All observed numeral-noun patterns in drafts are either correct or are in descriptive prose.

(b) The FALSE fires do NOT share a shape the regex can exclude — the pattern `\b(numeral)\s+(noun)\b` IS the intended target. The issue is not that the regex matches the wrong thing; it is that the regex matches ALL numeral-noun pairs and cannot determine whether the count is correct without counting the actual items. This is a fundamental limitation, not a pattern-exclusion problem.

**Case against shipping:** s fires on 100% of BLOCK files (54/54) with 566 total matches, ALL false. The fire rate exceeds every other class by an order of magnitude. Even if redesigned, a count-verification check would need semantic understanding of what constitutes "the enumeration" being counted — a problem no regex can solve.

The FORWARD row 25 precedent cut a check at 99.2% (1379/1390). Class s would fire on 100% of its target population. The measurement is complete.

**Why HOLD rather than REDESIGN:** REDESIGN implies a clear path to a better matcher. For s, the defect class (wrong enumeration count) is real and valuable, but the detection method (regex pattern matching) cannot distinguish correct from incorrect counts. A redesign would need to count items and compare — a fundamentally different approach that is not a regex redesign. The class is parked pending a technique that can verify counts, not merely detect them.

### (vii) Taxonomy mapping (diag-322)

No existing bucket. Nearest: **O** ("other-mechanizable"). The `s` class is genuinely new — 322's taxonomy does not cover enumeration-count verification. The class is mechanizable in principle but not by a regex matcher.

---

## Summary

| Class | Q1 BLOCK fire rate | Q3 TRUE | Q3 FALSE | Q3 AMB | Q2 re-finds | Q4 verified TPs | Q5 |
|-------|-------------------|---------|----------|--------|-------------|-----------------|-----|
| m | 40/54 (74%) | 0 | 86 | 0 | 0 | 0 | REDESIGN |
| q | 21/54 (39%) | 0 | 67 | 1 | 1 | 0 | REDESIGN |
| r | 7/54 (13%) | 0 | 70 | 0 | 0 | 0 | REDESIGN |
| s | 54/54 (100%) | 0 | 153 | 0 | 1 | 0 | HOLD |

**All four classes fail the shipping bar.** Zero verified true positives across all classes and all 139 pre-fold commits from 10 covered drafts. The measurement is structurally sound — the matchers fire, but they fire on prose and correct constructs, never on the defects they claim to detect.

Three classes (m, q, r) are REDESIGN: each has a clear redesign direction (parse the command structure to identify the -F argument, or distinguish pipe from alternation). One class (s) is HOLD: the detection technique (regex) cannot solve the underlying problem (count verification) regardless of redesign.

**Proportionality note (residual 5 from the diagnostic):** this diagnostic is 220+ lines to price four regexes. The answer is "hold all four." The drafting cost has exceeded the finding's value, which is itself a datum for the funnel.
