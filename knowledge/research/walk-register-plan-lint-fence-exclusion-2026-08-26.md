# Walk register — `plan-lint-fence-exclusion-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-plan-lint-fence-exclusion.md`
**Tier:** T1 (Small — the (r) check's v2: fenced-code exclusion + tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **The funnel's own product:** the (r) check's FIRST live warn (563's deposit) was a measured false positive — `if code == 0:` inside a fenced python block, a STRUCTURAL constant, not a probe. The v2 excludes fenced regions; the escape-clause judgment ("verify the constant is structural") stays for everything else.
2. **Anchor:** `def _check_bare_constants` at plan_lint.py L183; the loop walks `lines` with an `in_step` toggle — the fence toggle joins it symmetrically.
3. **Measured fixture:** the exact 563 line (L74 of its draft, reproduced from the committed blob) becomes the regression test's body.
4. **id prediction:** 565.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 1 | all five | — | — | DRY on all five — delimiter lines correctly unscanned by the toggle-then-continue order; the reopen trap tested; a WARN-only narrowing cannot fail-open; provenance blob-ref'd. | — | No folds. |

**Walk 1 total: 0 findings.**

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | all five | — | — | DRY — confirming pass. | — | No folds. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
