# Walk register — `verify-then-retire-sweep-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/diagnostic-verify-then-retire-sweep.md`
**Tier:** T1 (Small — read-only single-deposit diagnostic). **Panel: none (E-family; 515-528/531 precedent).**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **The batch-4 work order, CEO-approved (baton 19cb574):** sweep item (1) — one verification pass per row whose enforcement already exists, then `class: stale` pointer retirements; PST §6 row already retired in batch 3.
2. **Every surface READ FROM CODE this authoring:** cycle_check yield-rising at :394 and the substrate asserts at :262/:377-383/:482; fold_check + propagation_check present in scripts/ (propagation has NO test file — positive control mandated); plan_lint (e) at :260-269 — MEASURED live: H3 `### Step` + qa_steps → FAIL (e)+(c) exit 1, H3 without qa_steps → exit 0 (the residual the R-5 verdict must carry); wrap_check arms [1]..[4] incl. 562's class gate; gates.py:582 rule-20 + plan_lint (c) :286-309.
3. **Honest-verdict design:** per-row COVERED/PARTIAL with residue + route; two rows PREDICTED partial by the Planner's own scout (R-3 landed-nothing case; R-5 qa_steps-less arm) — the diagnostic confirms or refutes, never rounds up.
4. **Retirement discipline:** Planner's own act at close (agents sandbox-denied on ~/.claude); pointers carry `class: stale` (the 562 gate binds these writes); R-5's row retires with the batch-item-3 cluster, not before, if PARTIAL confirms.
5. **id prediction:** 568.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.
