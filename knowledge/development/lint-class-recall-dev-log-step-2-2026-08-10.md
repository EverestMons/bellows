# Dev Log — lint-class-recall Step 2 (2026-08-10)

**Diagnostic:** 337
**Slug:** `lint-class-recall-2026-08-10`
**Step:** 2 — QA

---

## Precondition 1 — register unchanged

`git log -1 --format="%H" -- governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` returned `a7077caa012bb8dbfb35639c9ba36ab84443c8c8`. Matches Step 1's recorded pin. Register has not moved.

## Precondition 2 — Step 1 ran as its own dispatch

Evidence directory commits show Step 1's two commits (`320d547` at 13:43:23, `8b1c538` at 13:53:41) were made before this QA dispatch. This context did not produce them.

## QA execution

### Item 1 (C1)
`git status --porcelain -- scripts/ tests/` empty. Both matcher files present: `census-matchers.py` (pre-seeded), `redesigned-m-q.py` (Task D). PASS.

### Item 2 (C2)
`git show --stat 320d547` shows 1 file (labelled-positives.txt). `git ls-tree 320d547 -- knowledge/research/lint-class-recall-findings-2026-08-10.md` returns nothing. Labelling preceded matching, proven from git. PASS.

### Item 3 (C3)
All Q2/Q3 figures are counts with denominators in the split form (reconstructed and verbatim separately). No percentages. PASS.

### Item 4 (C4)
Cross-referenced all four precision figures against 336 findings. All cite 336 directly, none recomputed. PASS.

### Item 5 (C5)
Three marks partition: 0 VERBATIM + 14 RECONSTRUCTED + 0 UNRECOVERABLE = 14 total. Stated in both findings and labelled-positives.txt. PASS.

### Item 6
Spot-checked i1 (m, line 87), i4 (q, line 22), i9 (s, line 270) against pinned register blob via `git show a7077ca:...`. All three confirmed: class assignment matches register description, recoverability marks correct. PASS.

### Item 7
All raw command outputs included in QA report. PASS.

### Item 8
Recall split present in every class section. Both positive controls (m, q) show separation. No failing controls. PASS.

### Item 9
Encoding stated (UTF-8). Three non-ASCII rows byte-compared: ☑ (U+2611), § (U+00A7), — (U+2014) all preserved. Constructed violation: replacing em-dash with hyphen detected at offset 809 (length difference: 6903 vs 6901). PASS.

### Item 10
Class assignments justified in findings (ii) sections. "Instances covered by no class" section present with 1 row (line 361) and justification. PASS.

### Item 11
Each instance_id unique (i1-i14). No multi-class instances in this dataset. PASS.

## Rule 20 self-check

PASSED. All 3 evidence files present and non-empty, no hedging keywords in positive-status rows.

## Deposits

- `knowledge/qa/lint-class-recall-qa-2026-08-10.md`
- `knowledge/development/lint-class-recall-dev-log-step-2-2026-08-10.md`
