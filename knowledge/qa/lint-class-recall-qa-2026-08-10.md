# QA Report — Lint-Class Recall (Diagnostic 337, Step 2)

**Diagnostic:** 337
**Slug:** `lint-class-recall-2026-08-10`
**Step:** 2 — QA
**Step 1 commits:** `320d547` (labelled set), `8b1c538` (findings + matchers + controls + dev log)

---

## Preconditions

### Precondition 1 — register has not moved

Step 1 recorded the register pin as `a7077caa012bb8dbfb35639c9ba36ab84443c8c8`.

Re-derived:
```
$ git -C /Users/marklehn/Developer/GitHub log -1 --format="%H" -- governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md
a7077caa012bb8dbfb35639c9ba36ab84443c8c8
```

**UNCHANGED.** The register blob is the same file Step 1 labelled against.

### Precondition 2 — Step 1 ran as its own dispatch

```
$ git log --oneline -- knowledge/qa/evidence/lint-class-recall-2026-08-10/
8b1c538 findings(337): [337] lint-class recall — all four classes measured, SHIP-warn blocked (0 verbatim)
320d547 evidence(337): [337] labelled positive set for lint-class recall — 14 instances across 4 classes
9b8c56b evidence: preserve diag-336's matcher sources before the temp dir is reaped
```

Step 1 commits (`320d547` at 13:43:23, `8b1c538` at 13:53:41) exist before this dispatch. This step's context did not produce them. **Independence confirmed.**

---

## (B) Deliverable Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Nothing installed, instrument preserved (C1) | ✅ |
| 2 | Labelling preceded matching (C2) | ✅ |
| 3 | Recall is a count (C3) | ✅ |
| 4 | Precision is cited, not recomputed (C4) | ✅ |
| 5 | Unrecoverable set is named (C5) | ✅ |
| 6 | Spot-check three labelled positives | ✅ |
| 7 | Raw output | ✅ |
| 8 | Recall split present, control HALT honoured | ✅ |
| 9 | Labelled text was NOT normalized | ✅ |
| 10 | Class assignments justified, no-class section exists | ✅ |
| 11 | Multi-class instances linked | ✅ |

### Item 1 — nothing installed, instrument preserved (C1)

**No change under scripts/ or tests/:**

```
$ git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/
(empty)
```

**Both matcher files present (C1 second half):**

```
$ ls knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/
census-matchers.py     (pre-seeded at 9b8c56b)
redesigned-m-q.py      (written in Task D, committed at 8b1c538)
```

Both files named by C1 exist. PASS.

### Item 2 — labelling preceded matching (C2)

```
$ git show --stat 320d547
commit 320d5473797a656fc782a8de47d426a2c74babac
    evidence(337): [337] labelled positive set for lint-class recall — 14 instances across 4 classes
    No matcher has been run yet. Labels precede matching (C2).

 .../labelled-positives.txt | 66 ++++++++++++++++++++++
 1 file changed, 66 insertions(+)
```

The labelled set is committed **alone** — 1 file changed, no findings document.

```
$ git ls-tree 320d547 -- knowledge/research/lint-class-recall-findings-2026-08-10.md
(empty — findings document absent from this commit's tree)
```

The findings document does not exist in the labelled-positives commit. The next commit (`8b1c538`) adds the findings, matchers, controls, and dev log — all after the labels were committed. **C2 satisfied: ordering is observable from git.**

### Item 3 — recall is a count (C3)

Every Q2/Q3 figure in the findings uses the form `k of N reconstructed, of T named` with a separate `Verbatim: 0` line. Since all instances are RECONSTRUCTED and the plan mandates split reporting (verbatim vs reconstructed separately), the split form is used rather than the pooled `k of N recoverable` form. All figures are counts with explicit denominators; no percentages appear. The `NOT MEASURABLE (N=0)` form is not needed (no class has N=0).

Verified figures:
- m Q2: "3 of 3 reconstructed, of 3 named" + "Verbatim: 0"
- m Q3: "3 of 3 reconstructed, of 3 named" + "Verbatim: 0"
- q Q2: "1 of 1 reconstructed, of 1 named" + "Verbatim: 0"
- q Q3: "1 of 1 reconstructed, of 1 named" + "Verbatim: 0"
- r Q2: "1 of 1 reconstructed, of 1 named" + "Verbatim: 0"
- s Q2: "2 of 9 reconstructed, of 9 named" + "Verbatim: 0"

PASS.

### Item 4 — precision is cited, not recomputed (C4)

Every precision figure in the findings cites diagnostic 336 explicitly:

| Class | 337 citation | 336 source |
|-------|-------------|------------|
| m | "Precision (336): 0 of 86 sampled TRUE" | 336 §m(iii): TRUE 0, FALSE 86, Sampled 86 |
| q | "Precision (336): 0 of 67 sampled TRUE, 1 AMBIGUOUS" | 336 §q(iii): TRUE 0, FALSE 67, AMBIGUOUS 1, Sampled 68 |
| r | "Precision (336): 0 of 70 sampled TRUE" | 336 §r(iii): TRUE 0, FALSE 70, Sampled 70 |
| s | "Precision (336): 0 of 153 sampled TRUE" | 336 §s(iii): TRUE 0, FALSE 153, Sampled 153 |

All match. No recomputation. PASS.

### Item 5 — the unrecoverable set is named (C5)

Q1's three marks partition the full register-named set:

| Mark | Count |
|------|-------|
| RECOVERABLE-VERBATIM | 0 |
| RECOVERABLE-RECONSTRUCTED | 14 |
| UNRECOVERABLE | 0 |
| **Total** | **14** |

Both the findings summary and the labelled-positives.txt footer state these counts. The partition is complete: 0 + 14 + 0 = 14 = total named. PASS.

### Item 6 — spot-check three labelled positives

Three instances spot-checked against the register at pinned blob `a7077ca`, not the working tree:

**i1 (class m, register line 87):**

Register (pinned blob): `P10 grepped the two checkbox glyphs — non-ASCII literals that must survive a blockquote, an agent retyping them, a shell, and -F`

Labelled as: class m, RECOVERABLE-RECONSTRUCTED, source "register description + draft corrected P10". Reconstruction: `grep -c -F "☑" /Users/marklehn/Developer/GitHub/gate1-packet-2026-08-08.md`

The register describes non-ASCII glyphs in a grep -F command. The labelled class (m = non-ASCII inside a -F literal) matches. Recoverability mark correct — the register describes the defect but does not quote the original line. **Confirmed.**

**i4 (class q, register line 22):**

Register (pinned blob): `P7's literal carries backticks that must survive a blockquote, a shell, and -F.`

Labelled as: class q, RECOVERABLE-RECONSTRUCTED, source "register description + draft corrected P7". Reconstruction: `grep -c -F "never grep` `` `### N.` `` `unscoped" /Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md`

The register says backticks in a -F literal. The labelled class (q = shell metacharacter inside a -F literal) matches. Recoverability mark correct. **Confirmed.**

**i9 (class s, register line 270):**

Register (pinned blob): `"Record all four" over an enumeration carrying five values — (ii) is two shasums.`

Labelled as: class s, RECOVERABLE-RECONSTRUCTED, source "register description + draft corrected text". Reconstruction: `Record all four values`

The register describes a numeral-noun mismatch (four vs five). The labelled class (s = numeral asserting the size of an enumeration) matches. Recoverability mark correct. **Confirmed.**

All three spot-checks pass.

### Item 7 — raw output

All counts in this report are from command stdout, pasted above in Items 1, 2, Preconditions 1 and 2. The verification figures (Item 4 cross-reference, Item 5 partition, Item 6 register quotes) are read from the deposited files and the pinned register blob via `git show a7077ca:...`.

### Item 8 — recall split present, control HALT honoured

**Split present:** Every class in the findings reports recall separately for verbatim and reconstructed rows. Each class's Q2/Q3 section shows "Reconstructed: k of N reconstructed, of T named. Verbatim: 0 (no verbatim rows exist)."

**Control separation confirmed:** From `positive-controls.txt`:
- m-redesigned: defect-present → True, defect-absent → False. **Separates.**
- q-redesigned: defect-present → True, defect-absent → False. **Separates.**

**HALT honoured:** Both controls passed (separated). No failing control occurred, so the HALT condition was not triggered. The reachable failure path — a control that does NOT separate — would have prevented the recall run, and no recall figure would have been published for that matcher.

PASS.

### Item 9 — labelled text was NOT normalized

**Encoding stated:** `labelled-positives.txt` header declares "Encoding: UTF-8".

**Three non-ASCII-carrying rows byte-compared against the register blob:**

| Row | Character | Unicode | Bytes in deposit | Register source |
|-----|-----------|---------|-----------------|----------------|
| i1 | ☑ | U+2611 BALLOT BOX WITH CHECK | `\xe2\x98\x91` | Register line 87 says "checkbox glyphs" |
| i2 | § | U+00A7 SECTION SIGN | `\xc2\xa7` | Register line 414 has `\xc2\xa7` |
| i2 | — | U+2014 EM DASH | `\xe2\x80\x94` | Register line 414 uses em-dash |
| i3 | — | U+2014 EM DASH | `\xe2\x80\x94` | Register line 414 says "em-dash" |

No straightened quotes, no hyphenated em-dashes, no stripped section signs. All non-ASCII characters preserved as their original Unicode code points.

**Constructed violation:** Replacing the first em-dash (3 bytes: `\xe2\x80\x94`) with a hyphen (1 byte: `\x2d`) produces a 2-byte length difference at offset 809. The byte comparison detects the tidied character immediately:
```
original: 0xe2 (context: b'SS m \xe2\x80\x94 n')
tidied:   0x2d (context: b'SS m - non')
CONSTRUCTED VIOLATION DETECTED
```

PASS.

### Item 10 — class assignments justified, no-class section exists

**Class assignments justified:** Each class section's (ii) subsection lists its instances with register line citations and descriptions explaining why each is an instance of that class. The dev log records "Each instance justified against the matcher's own regex definition."

Spot-checked justifications:
- i1 (m): register says "grepped the two checkbox glyphs" with -F → non-ASCII (☑) in a -F command. Matches m's definition.
- i4 (q): register says "literal carries backticks" in -F → shell metacharacter in a -F literal. Matches q's definition.
- i9 (s): register says "Record all four" over five values → numeral asserting wrong enumeration size. Matches s's definition.

**No-class section exists:** "## Instances covered by no class" is present in the findings with one row (register line 361 — `grep -c` recount inflated by self-referential corrections). The justification states it is adjacent to class r's concern but not the r-class defect (piped exit code masking vs. self-referential text inflation). No existing class describes this.

**Authoring-time list corrections stated:** Lines 136 and 361 from the authoring-time list are explicitly removed with reasons (136: not a defect instance; 361: not a class-r instance).

PASS.

### Item 11 — multi-class instances linked

Each `instance_id` (i1 through i14) appears exactly once in the labelled set. No instance is classified under multiple classes — each defect belongs to exactly one class:
- m: i1, i2, i3
- q: i4
- r: i5
- s: i6, i7, i8, i9, i10, i11, i12, i13, i14

Instances i2 and i3 share register line 414 (two different defects described in the same register entry) but are distinct instances with distinct instance_ids. Each class's denominator counts each instance once.

PASS.

---

## (A) Rule 20 — QA Self-Check Results

```
plan_slug = 'lint-class-recall-2026-08-10'
qa_report_path = '/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/lint-class-recall-qa-2026-08-10.md'
evidence_dir = '/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/'
required_evidence_files = ['matchers/redesigned-m-q.py', 'positive-controls.txt', 'labelled-positives.txt']
```

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/
Files verified: 3
```

---
