# Lint-Class Recall Findings — 2026-08-10

**Diagnostic:** 337
**Slug:** `lint-class-recall-2026-08-10`
**Register pin:** `a7077ca` (verified: `git -C /Users/marklehn/Developer/GitHub log -1 --format="%H" -- governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` returned `a7077caa012bb8dbfb35639c9ba36ab84443c8c8`, matching the authoring-time pin)
**Labelled positive set:** 14 instances across 4 classes; 0 VERBATIM, 14 RECONSTRUCTED, 0 UNRECOVERABLE
**Predecessor:** `lint-class-census-findings-2026-08-10.md` (diagnostic 336), which measured precision only

---

## Class m — non-ASCII inside a -F literal

### (i) Matcher source

**As-written** — from deposited `census-matchers.py` (Task B verified present, ENUM_NOUNS identifier confirmed):

```python
GREP_F_RE = re.compile(r'grep\b.*-[A-Za-z]*F')

def match_m(line):
    if not GREP_F_RE.search(line):
        return False
    return any(ord(c) > 127 for c in line)
```

**Redesigned** — from `redesigned-m-q.py` (written in Task D, deposited):

```python
def match_m_redesigned(line):
    operand = extract_f_operand(line)
    if operand is None:
        return False
    return any(ord(c) > 127 for c in operand)
```

Parses the command to find the actual `-F` operand using `shlex.split` with a regex fallback. Positive control validated: fires on non-ASCII inside the operand, does not fire on non-ASCII in surrounding prose.

### (ii) Labelled positives

| instance_id | register_line | recoverability | source | description |
|---|---|---|---|---|
| i1 | 87 | RECOVERABLE-RECONSTRUCTED | register + draft P10 | P10's checkbox glyphs (☑/☐) in grep -F |
| i2 | 414 | RECOVERABLE-RECONSTRUCTED | register + draft version pin | Version pin carrying § in grep -x -F |
| i3 | 414 | RECOVERABLE-RECONSTRUCTED | register + draft C2 | Packet anchor carrying em-dash (—) in grep -c -F |

**Reconstruction basis for each:**
- i1: Register says "P10 grepped the two checkbox glyphs" with -F; draft shows corrected P10 as `grep -c -F "**Decision:**"`. Original used the glyph characters directly. Reconstructed: `grep -c -F "☑" /Users/.../gate1-packet-2026-08-08.md`
- i2: Register says "The version literal carried §"; draft shows corrected pin as `grep -c -F "**Version:** 2.0 (2026-08-09)"`. Original used `-x -F` with the full version line containing §. Reconstructed: `grep -x -F "**Version:** 2.0 (2026-08-09) — §2 shape amendment" /Users/.../DRAFTING_CYCLE.md`
- i3: Register says "the packet anchor carried an em-dash"; draft C2 shows corrected anchor as `grep -c -F "DRAFTING_CYCLE surgical batch: 19 items"` (ASCII-only, em-dash dropped). Reconstructed: `grep -c -F "Group 4 — DRAFTING_CYCLE surgical batch: 19 items" /Users/.../gate1-packet-2026-08-08.md`

### (iii) Q2 — Recall as-written

**Reconstructed: 3 of 3 reconstructed, of 3 named. Verbatim: 0 (no verbatim rows exist).**

All three reconstructed instances fire. The as-written matcher catches non-ASCII anywhere on a line with grep -F, so any instance where the non-ASCII character appears on the line fires — including these, where the non-ASCII is in the -F operand.

### (iv) Q3 — Recall redesigned

**Reconstructed: 3 of 3 reconstructed, of 3 named. Verbatim: 0 (no verbatim rows exist).**

The redesigned matcher also fires on all three. It correctly parses the -F operand and finds the non-ASCII character (☑, §, —) inside it. The redesign narrows what fires without losing any of the true positives.

### (v) Q4 — Disposition: REDESIGN

**Precision (336): 0 of 86 sampled TRUE — 100% false positive rate as-written. Recall (here): 3 of 3 reconstructed (0 verbatim), of 3 named.**

**REDESIGN.** The as-written matcher has perfect recall on reconstructed instances but zero precision. The redesigned matcher also has perfect recall and should have substantially better precision (it checks only the -F operand), but its precision has not been measured by either diagnostic.

**Case against SHIP-warn:** 0 verbatim hits — the recall rests entirely on reconstructed text, and SHIP-warn requires at least one verbatim hit. Additionally, the redesigned matcher's precision is unmeasured. **Case against HOLD:** the redesigned matcher is written, its recall is measured, and it separates on positive controls. What is owed is a precision census of the redesigned matcher over the Done/ corpus.

### (vi) Case against the disposition

The strongest argument for upgrading to SHIP-warn would be that the redesigned matcher has 3/3 recall and a plausible precision improvement. Against: all 3 hits are on reconstructed text — a reader's phrasing, not the original bytes — so a matcher firing on them measures the reconstructor's command-line style. And the redesigned matcher's precision is genuinely unknown; the as-written matcher's 100% false-positive rate was not predicted before measurement.

---

## Class q — shell metacharacter inside a -F literal

### (i) Matcher source

**As-written** — from deposited `census-matchers.py`:

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

**Redesigned** — from `redesigned-m-q.py`:

```python
def match_q_redesigned(line):
    operand = extract_f_operand(line)
    if operand is None:
        return False
    return '`' in operand or '$' in operand or '!' in operand
```

### (ii) Labelled positives

| instance_id | register_line | recoverability | source | description |
|---|---|---|---|---|
| i4 | 22 | RECOVERABLE-RECONSTRUCTED | register + draft P7 | P7's backtick literal in grep -c -F |

**Reconstruction basis:** Register says "P7's literal carries backticks that must survive a blockquote, a shell, and -F." Draft says original pinned `never grep ### N. unscoped` (with backticks around `### N.`), corrected to `the two sections number independently`. Reconstructed: `grep -c -F "never grep` `` `### N.` `` `unscoped" /Users/.../DRAFTING_CYCLE.md`

### (iii) Q2 — Recall as-written

**Reconstructed: 1 of 1 reconstructed, of 1 named. Verbatim: 0 (no verbatim rows exist).**

The as-written matcher fires: the line contains grep -F, and a quoted string on the line contains a backtick.

### (iv) Q3 — Recall redesigned

**Reconstructed: 1 of 1 reconstructed, of 1 named. Verbatim: 0 (no verbatim rows exist).**

The redesigned matcher fires: it parses the -F operand and finds the backtick inside it.

### (v) Q4 — Disposition: REDESIGN

**Precision (336): 0 of 67 sampled TRUE, 1 AMBIGUOUS — 96% of fires were metacharacters in OTHER quoted strings, not the -F argument. Recall (here): 1 of 1 reconstructed (0 verbatim), of 1 named.**

**REDESIGN.** Same structure as class m: the redesigned matcher has 1/1 recall on the one reconstructed instance, but 0 verbatim hits block SHIP-warn, and the redesigned matcher's precision is unmeasured.

### (vi) Case against the disposition

With only 1 named instance, the denominator is too small for any strong disposition. The redesigned matcher's recall (1/1) is perfect but trivially so. The precision measurement is what the class needs next.

---

## Class r — grep -c piped into another command

### (i) Matcher source

**As-written** — from deposited `census-matchers.py`:

```python
GREP_C_PIPE_RE = re.compile(r'grep\b[^|]*-[A-Za-z]*c[A-Za-z]*\b[^|]*\|')

def match_r(line):
    return bool(GREP_C_PIPE_RE.search(line))
```

**Not redesigned** — per the diagnostic plan: r's redesign direction is shell-aware pipe detection, and no instance justifies building it yet.

### (ii) Labelled positives

| instance_id | register_line | recoverability | source | description |
|---|---|---|---|---|
| i5 | 25 | RECOVERABLE-RECONSTRUCTED | register + draft Step 3 | Step 3 Item 1's grep -c piped, masking exit code |

**Reconstruction basis:** Register says original mixed `-F` and regex with `^| 2` and resolution is "never through a pipeline." Draft shows corrected form uses `grep -c -E` against files with no pipe. Reconstructed: `grep -c -F "^| 2" gate1-packet-2026-08-08.md | grep "20"`

**Note on the match mechanism:** The r matcher fires on this line, but it catches the `|` inside the grep pattern (`^| 2`), not the shell pipe after the filename. The regex `grep\b[^|]*-[A-Za-z]*c[A-Za-z]*\b[^|]*\|` scans for grep with -c followed by the first `|` it finds — which is the regex alternation character inside the pattern argument, not the shell pipe. The matcher fires for the wrong reason on this line, though the defect (piped grep -c masking exit code) is real.

### (iii) Q2 — Recall as-written

**Reconstructed: 1 of 1 reconstructed, of 1 named. Verbatim: 0 (no verbatim rows exist).**

The matcher fires, though it catches the pattern-internal `|` rather than the shell pipe.

### (iv) Not redesigned

Per the diagnostic plan, r is not redesigned here. r's redesign direction (shell-aware pipe detection) is stated in 336 §(vi).

### (v) Q4 — Disposition: REDESIGN

**Precision (336): 0 of 70 sampled TRUE — the `|` that triggers the matcher is regex alternation, markdown table cells, or receiving-from-pipe, never the piped-exit-code defect. Recall (here): 1 of 1 reconstructed (0 verbatim), of 1 named.**

**REDESIGN.** The matcher fires on the one instance but for the wrong reason (it catches the `|` inside the pattern, not the shell pipe). Zero precision and an accidental hit do not meet the shipping bar. 0 verbatim hits block SHIP-warn.

### (vi) Case against the disposition

The 1/1 recall is real — the matcher does fire on the reconstructed line — but the match is accidental: it catches the pattern-internal `|` rather than the shell pipe. A redesigned r matcher would need to distinguish shell pipes from in-pattern `|` characters, which requires the shell-aware parsing 336 described.

---

## Class s — numeral asserting the size of an enumeration

### (i) Matcher source

**As-written** — from deposited `census-matchers.py`:

```python
NUMBER_WORDS = ['two', 'three', ..., 'twenty']
ENUM_NOUNS = r'items?|steps?|files?|...'  # ~70 noun patterns
S_RE = re.compile(rf'\b({NW_ALT})\s+({ENUM_NOUNS})\b', re.IGNORECASE)

def match_s(line):
    return bool(S_RE.search(line))
```

Full noun list in the deposited `census-matchers.py`.

**Not redesigned** — per the diagnostic plan: s is HOLD on 336's ground that a regex cannot verify a count. That ground is not re-argued here.

### (ii) Labelled positives

| instance_id | register_line | recoverability | source | description | s fires? | why not |
|---|---|---|---|---|---|---|
| i6 | 13 | RECOVERABLE-RECONSTRUCTED | register fragment | "Three checks" → seven | NO | intervening words between "Three" and "checks" |
| i7 | 16 | RECOVERABLE-RECONSTRUCTED | register fragment | "two files" → six | YES | — |
| i8 | 23 | RECOVERABLE-RECONSTRUCTED | register fragment | "eight probes" → ten | NO | `**eight**` bold formatting separates numeral from noun |
| i9 | 270 | RECOVERABLE-RECONSTRUCTED | register + draft | "all four" → five | NO | "values" not in ENUM_NOUNS |
| i10 | 19 | RECOVERABLE-RECONSTRUCTED | register fragment | "twice" → unverified | NO | "twice" not in NUMBER_WORDS |
| i11 | 327 | RECOVERABLE-RECONSTRUCTED | register description | "TWO new repo files" → seven | NO | `**TWO**` bold + intervening words |
| i12 | 328 | RECOVERABLE-RECONSTRUCTED | register description | "four deposits" → five | NO | `**four**` bold formatting separates numeral from noun |
| i13 | 374 | RECOVERABLE-RECONSTRUCTED | register description | "six paths" → stale | YES | — |
| i14 | 355 | RECOVERABLE-RECONSTRUCTED | register description | "TWO deposits" → three | NO | `**TWO**` bold formatting separates numeral from noun |

### (iii) Q2 — Recall as-written

**Reconstructed: 2 of 9 reconstructed, of 9 named. Verbatim: 0 (no verbatim rows exist).**

The s matcher fires on only 2 of 9 instances. The 7 misses have four distinct causes:
1. **Intervening words** (i6, i11): "Three `plan_lint` warn-first checks" has words between the numeral and noun; `\s+` can only match whitespace.
2. **Bold formatting** (i8, i12, i14): `**eight**` places `**` between the numeral and the following whitespace, so `\beight\s+` fails.
3. **Vocabulary gap — noun** (i9): "values" is not in ENUM_NOUNS.
4. **Vocabulary gap — numeral** (i10): "twice" is not in NUMBER_WORDS.

### (iv) Not redesigned

Per the diagnostic plan, s is not redesigned here. 336's ground — that a regex cannot verify a count — is not re-argued.

**However, a mechanism 336 never considered is reportable (per Q3).** Several instances have **machine-countable enumerations** in the same block:
- i6: "Three checks" then enumerates (j)(k)(l)+(n)(o1)(o2)(p) — seven parenthesized items
- i8: "eight probes" then lists P1–P10 — ten P-prefixed items
- i9: "all four values" with items (i)–(iv) but (ii) carries two — five by sub-item count
- i12: "four deposits" followed by a bulleted list — countable

A tool that (a) detects a numeral-noun pattern, (b) finds the associated enumeration (numbered list, parenthesized items, bulleted list), and (c) counts the items could verify whether the count is correct. This is not a regex and is not what class s was designed to be. But it is a concrete mechanism that addresses 336's objection ("a regex cannot verify a count") by not being a regex. **This finding is reported as such, not as grounds to change the s disposition.**

### (v) Q4 — Disposition: HOLD (336's ground unchanged)

**Precision (336): 0 of 153 sampled TRUE — 100% false positive rate, fires on 100% of BLOCK files (54/54). Recall (here): 2 of 9 reconstructed (0 verbatim), of 9 named.**

**HOLD** on 336's ground: a regex matching `\b(numeral)\s+(noun)\b` cannot verify whether the count is correct. The recall data confirms this is not merely a theoretical limitation — the matcher misses 7 of 9 known wrong counts due to formatting, vocabulary, and word-order gaps that a regex redesign could partially address but that do not touch the fundamental objection.

**What survives from 336:** s HOLD is sound. The recall measurement reinforces it: even detecting the numeral-noun pair is unreliable (2/9), and detecting it says nothing about whether it is wrong.

**What is new:** the machine-countable-enumeration mechanism described in (iv). This does not change the disposition — HOLD means no build work — but it names a concrete successor approach that is not "a better regex." If the fold-granular history instrumentation (bellows FORWARD row 49) makes a real measurement possible, and the next diagnostic considers non-regex approaches, this mechanism is the candidate.

### (vi) Case against the disposition

The strongest argument for RETIRE would be: 2/9 recall, zero precision, and the class is fundamentally limited. Against RETIRE: the 7 misses are in the MATCHER, not in the CLASS. The defect (wrong count asserting an enumeration's size) is real and was found 9 times in one cycle. Retiring the class because the current matcher can't see it would discard the finding about the defect. **HOLD preserves the finding while acknowledging the matcher cannot deliver it.** RETIRE-PENDING-INSTRUMENTATION would also be defensible but overstates the case: the defect class does not need new instrumentation to be real — what needs instrumentation is a MEASUREMENT that can price a matcher against it.

---

## Instances covered by no class

| register_line | description | why no class covers it |
|---|---|---|
| 361 | Walk 4 sweep: `grep -c` recount returned MORE than before because corrections cite the stale wording they fix | Adjacent to class r's concern (grep -c producing misleading results) but not the r-class defect (piped exit code masking). The issue is self-referential text inflating a count, not a shell pipeline. No existing class describes "a measurement tool that double-counts its own corrections." |

**Note on authoring-time list corrections:** The authoring-time list cited register lines 136 and 361. Line 136 is NOT a defect instance — it is a finding about C3's count-word check scope being too broad (it would fire on Cycle Log summary counts backed by the register, not on wrong enumerations). Line 361 is NOT a class-r instance per the matcher definition — see above. Both are removed from the labelled set.

---

## Summary

| Class | Precision (336) | Recall as-written (reconstructed) | Recall as-written (verbatim) | Recall redesigned (reconstructed) | Recall redesigned (verbatim) | Q4 |
|---|---|---|---|---|---|---|
| m | 0/86 | 3 of 3 reconstructed, of 3 named | 0 | 3 of 3 reconstructed, of 3 named | 0 | REDESIGN |
| q | 0/67, 1 AMB | 1 of 1 reconstructed, of 1 named | 0 | 1 of 1 reconstructed, of 1 named | 0 | REDESIGN |
| r | 0/70 | 1 of 1 reconstructed, of 1 named | 0 | not redesigned | — | REDESIGN |
| s | 0/153 | 2 of 9 reconstructed, of 9 named | 0 | not redesigned | — | HOLD |

**The gap Q1 was written to answer:** all 14 instances are RECOVERABLE-RECONSTRUCTED; 0 are VERBATIM; 0 are UNRECOVERABLE. The register describes defects as descriptions, not as the lines that carried them. The pre-fold source text is recoverable only as reconstructions — a reader's rendering of what the register describes, not the original bytes. **This means every recall figure above measures the reconstructor's phrasing, not the matcher against the original. SHIP-warn requires at least one verbatim hit and no class has one.**

**The finding behind the finding:** the reason no instance is VERBATIM is that the drafting cycle had exactly one commit (the session wrap). A cycle committed per phase — which bellows FORWARD row 49 would enable — would preserve pre-fold revisions in git history, making VERBATIM recovery possible for the next cycle. This diagnostic's inability to produce VERBATIM rows is itself the strongest argument for that instrumentation.

**Owed artifact:** an instrumentation plan for fold-granular draft history (the concrete successor bellows FORWARD row 49 names). Any class whose disposition lands at HOLD or whose recall rests entirely on reconstructed rows routes there. Today that is all four.
