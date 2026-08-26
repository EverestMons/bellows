# Walk register — `reconcile-plan-tool-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-reconcile-plan-tool.md`
**Tier:** T1 (Small — one tool + tests + the one-line pointer fix; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **Batch-3 item 2 (audit item 3):** the orphan-recovery act mechanized — THREE surfaces (plans.lifecycle_state+closed_at+plan_doc_ref; verdicts.outcome/decided_by/disposition_summary WHERE outcome IS NULL — the AWAITING-VERDICT signal; the pending request file archived), from the reconciliation memory's verified contract (exec-454/458 measurements).
2. **The dangling pointer, verified live:** issue_verdict.py:91 says "see the reconciliation runbook in CLAUDE.md" — bellows/CLAUDE.md contains NO such runbook (grep 0). The line re-aims at the tool.
3. **The alive-worker law encoded:** the tool REFUSES lifecycle_state='in_progress' without `--killed-verified` (a worker can survive ENOSPC and wedge — death needs proof, the memory's measured ~70-min case); the flag's help text says what the human must have done (ps + kill).
4. **WAL law in the docstring:** updates land in the -wal and are live-correct immediately; the DBs stay uncommitted — never checkpoint from a Planner session.
5. **verdicts schema read live:** outcome/decided_by/disposition_summary columns confirmed.
6. **id prediction:** 566.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| Q1 | 1 | 1 Weak spots | 1.2 | — | QA Item 2 carried the author's own mid-sentence self-correction left in the plan text (the 545-F3 drafting-noise class — third instance across the arcs, caught by the walk this time). | `…in a mode that would mutate — expect it to print the current state and then be interrupted BY THE OPERATOR? NO — never…` | Folded: the clean scratch-copy form with the byte-unchanged dump-compare. |

**Walk 1 total: one finding, folded.** (Other lenses dry — refusal-first with dump-compare; the NULL-outcome predicate exact; live DB never a mutating operand; pointer verified before re-aiming.)

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | all five | — | — | DRY — the cleaned Item 2 re-read; probes earnable. | — | No folds. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
