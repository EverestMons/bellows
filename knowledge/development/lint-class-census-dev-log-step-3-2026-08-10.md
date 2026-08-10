# Dev Log — lint-class-census step 3 (2026-08-10)

## Rule 20 self-check

Source: `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (read live).

Values:
- `plan_slug`: `lint-class-census-2026-08-10`
- `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/336/knowledge/qa/lint-class-census-qa-2026-08-10.md`
- `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/336/knowledge/qa/evidence/lint-class-census-2026-08-10/`
- `required_evidence_files`: `['classification-rubric.md', 'final-state-matches.txt', 'pre-fold-matches.txt']`

Result: **PASSED** — all evidence files present, no hedging keywords found. Files verified: 3.

## Deliverable verification

### Item 1 — nothing installed

```
$ git status --porcelain -- scripts/ tests/
(empty)
```

```
$ git diff --name-only 30c3d23..HEAD
knowledge/development/lint-class-census-dev-log-step-2-2026-08-10.md
knowledge/qa/evidence/lint-class-census-2026-08-10/pre-fold-matches.txt
knowledge/research/lint-class-census-findings-2026-08-10.md
```

All changed files are declared deposits. No scripts/ or tests/ changes.

### Item 2 — populations never blended

Verified by reading `lint-class-census-findings-2026-08-10.md`: Q1/Q3 sections cite "final states" and point to `final-state-matches.txt`; Q2/Q4 sections cite "pre-fold states" and point to `pre-fold-matches.txt`. No single number spans both populations. The summary table lists each question's source population in its column header.

### Item 3 — Q3 is a list (5 spot-checks)

1. **m | executable-330.md:209 | BLOCK | FALSE/R2** — Line contains `grep -cF` probes in QA verification prose. Non-ASCII (em-dash) in surrounding text, not in -F argument. Verdict confirmed.
2. **q | executable-330.md:211 | BLOCK | FALSE/R2** — Version verification probes; metacharacter in OTHER quoted strings on the line. Verdict confirmed.
3. **q | executable-321.md:49 | BLOCK | AMBIGUOUS/R4** — `grep -n -F "AND status != 'retired'"` — `!` in -F pattern but `!=` is not a valid bash history designator. Verdict confirmed.
4. **s | executable-project-docs-reset-2026-03-29.md:34 | NO_BLOCK | FALSE/R5** — "three files" counts PROJECT_BRIEF.md, PROJECT_STATUS.md, CLAUDE.md — three items, count correct. Verdict confirmed.
5. **r | diagnostic-flavornotes-...-v2-2026-04-17.md:33 | NO_BLOCK | FALSE/R2** — Long instruction line; `|` appears in markdown structure and prose, not as a shell pipe. Verdict confirmed.

All 5 verdicts survive the reader.

### Item 4 — uncovered set named

Verified: findings doc section (iv) for each class states "Uncovered set: brewbuddy-shop-import-census (no close commit; still in draft)." The uncovered set is named, not omitted.

### Item 5 — case against present

No SHIP recommendations made. All four classes received REDESIGN (m, q, r) or HOLD (s). Each disposition section includes "Case against shipping" with specific numbers and structural arguments.

### Item 6 — raw output

All counts derived from command stdout:
- Match counts: `python3 census-matchers.py` stdout → `raw-matches.tsv`
- Pre-fold counts: `python3 pre-fold-scan.py` stdout → `pre-fold-raw.tsv`
- Corpus counts: `find ... | wc -l` stdout in dev log
- Commit counts: `git log --oneline ... | wc -l` stdout in dev log

## Deposits

- `knowledge/qa/lint-class-census-qa-2026-08-10.md` — QA report (this step)
- `knowledge/development/lint-class-census-dev-log-step-3-2026-08-10.md` — dev log (this file)
