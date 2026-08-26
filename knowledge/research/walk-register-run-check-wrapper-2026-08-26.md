# Walk register — `run-check-wrapper-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-run-check-wrapper.md`
**Tier:** T1 (Small — one new tool + tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **The audit's item 2, CEO-batched (batch 2):** one wrapper normalizing every checker's verdict channel to a REAL exit code — retiring four memory entries whose whole content is "this checker's channel lies".
2. **Each channel READ FROM CODE this authoring, never from the memories:** cycle_check → verdict is the LAST STDOUT LINE (`BAR_MET`/`CONTINUE`/`ESCALATE:*`), exit 0 for both BAR_MET and CONTINUE; plan_lint → the exit code IS the channel (grep found zero bare exit(1)s — it exits its fail count path properly; WARNs advisory); walk_register_lint → the per-file verdict `<name>\tCONFORMANT|UNCONFORMANT` prints on STDERR (L358), TSV data on stdout, and the lint path reaches end-of-main with NO exit call → ALWAYS exit 0 (verified at the source; the L593-602 exits belong to another entry path).
3. **Design:** pure `judge_*` functions (stdout, stderr, exit) → (verdict, reason), a thin subprocess runner, and the final `RUN_CHECK: <checker> VERDICT=…` line; exit 0 PASS / 1 FAIL / 2 usage-or-crash. Register mode requires a POSITIVE control (at least one CONFORMANT line seen) — absence-of-UNCONFORMANT alone could mean nothing was scanned (the negative-probe law, mechanized into the judge). Cycle mode is STRICT (BAR_MET only) with `--accept-continue` for mid-cycle callers.
4. **Retirement discipline (the audit's law, adapted to the sandbox constraint):** the four memory retirements happen as the Planner's own act AT THIS PLAN'S CLOSE (daemon agents are sandbox-denied on ~/.claude — the audit's execution-context note); the pointers will carry `class: stale` (the 562 gate binds the Planner's own writes now).
5. **id prediction:** 563.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 1 | all five | — | — | DRY on all five — judges fail-closed at every empty/crash arm; the positive-control FAIL is the mechanized trap; streams relayed verbatim; smokes record honest verdicts. | — | No folds. |

**Walk 1 total: 0 findings.**

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | all five | — | — | DRY — confirming pass. | — | No folds. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
