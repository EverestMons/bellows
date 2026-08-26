# Walk register — `diff-stat-rename-normalize-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-diff-stat-rename-normalize.md`
**Tier:** T1 (Small — one normalization in `_parse_diff_stat` + tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **Batch-3 item 3 (the audit's scope_check-rename defect, root-caused deeper):** the hole is NOT in `_gate_scope_check` — it is fed poisoned input: `_parse_diff_stat` passes `git diff --stat` rename renderings VERBATIM into `files_changed`, so a rename surfaces as the literal `{a/b => c}/f.md` or `top.md => renamed-top.md`, which no Scope declaration can ever match (the scope-check-illusory-for-renames memory's mechanism, now located). One parser fix feeds scope_check AND file_change_audit correctly at once.
2. **The REAL forms, captured live this authoring from an actual cross-dir `git mv` (tmp repo):** `{a/b => c}/f.md          | 0` and `top.md => renamed-top.md | 0` — these exact strings are the test fixtures.
3. **Normalization law:** resolve to the NEW path (brace form: substitute the right side of each `{l => r}`, then collapse any `//`; bare form: take the right side of ` => `). The OLD path is deliberately NOT emitted (files_changed answers "what does the tree contain now"; the audit trail of the move lives in git itself).
4. **id prediction:** 567.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 1 | all five | — | — | DRY on all five — the regex hand-traced over all fixture shapes incl. both empty-side brace arms; anchors verified live; new-path-only with reason; downstream strictly-more-matchable. | — | No folds. |

**Walk 1 total: 0 findings.**

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | all five | — | — | DRY — confirming pass. | — | No folds. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
