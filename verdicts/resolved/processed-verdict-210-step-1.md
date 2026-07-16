verdict: continue

**Rule 22(b) verified independently by the Planner. All gates PASS. The fix is correct — and the plan's QA row 4 is WRONG. Correction below is binding on Step 2.**

## The fix is right

- Both stale tests renamed and re-pinned: `test_schema_version_is_17` in `tests/test_parse_track_schema.py:86` and `tests/test_provenance_columns.py:48`. `grep -rn "test_schema_version_is_16" tests/` returns **zero** — no stale name survives to lie to the next reader.
- **The trap held.** `tests/test_schema_v17_migration.py:65` still reads `assert v_before == 16, "Precondition: version stamped to 16"` — untouched. A "change 16 to 17" sweep would have silently gutted the v16->v17 migration test while leaving the suite green. It didn't happen.
- `tests/test_contract_schema_migration.py:644` (`assert version == 17`) untouched — it was already correct.
- **Tripwires intact:** both tests still hardcode the literal. No `import database`, no `from database import CURRENT_SCHEMA_VERSION` — verified by reading the import block (`:13-15`). The tests remain able to catch the next bump.

## ⚠️ CORRECTION — the plan's QA row 4 is self-contradictory. My error, not the agent's.

Row 4 as written says: *"`grep -n "CURRENT_SCHEMA_VERSION" tests/test_parse_track_schema.py tests/test_provenance_columns.py` returns zero hits."*

**That is wrong, and it contradicts the plan's own Task B.** Task B explicitly ORDERED the agent to fix the assertion message that reads `f"CURRENT_SCHEMA_VERSION should be 16, got {ver[0]}"` -> `17`. That message **contains the string `CURRENT_SCHEMA_VERSION`**. Following Task B guarantees row 4's grep returns 1, not 0. The two instructions cannot both be satisfied.

**Ground truth (Planner-verified):** the single hit is `test_provenance_columns.py:52` — `assert ver[0] == 17, f"CURRENT_SCHEMA_VERSION should be 17, got {ver[0]}"`. That is the **assertion message**, not an import. The agent did exactly what Task B asked and kept the value hardcoded. This is correct work.

**Binding correction for Step 2 — row 4 is REPLACED by:**
> **4. Tripwires still hardcoded — verify by IMPORTS, not by string count.** Confirm neither test imports the constant: `grep -nE "^from database import|^import database|from database import CURRENT_SCHEMA_VERSION" tests/test_parse_track_schema.py tests/test_provenance_columns.py` must return **zero hits**, and both assertions must compare against a **literal** (`== 17`), not a name. The string `CURRENT_SCHEMA_VERSION` appearing inside `test_provenance_columns.py:52`'s assertion **message** is CORRECT and REQUIRED by Task B — **do NOT delete or reword that message to satisfy a grep.** Expect exactly **1** occurrence of the bare string, in that message.

**Do not "fix" working code to satisfy a bad instruction.** Deleting that message would strip a useful diagnostic (it tells whoever hits the failure what the expected value is) purely to make a wrong grep pass. If any instruction in this plan conflicts with the code being right, the instruction loses — say so in Prompt Feedback.

## The pattern, again

**This is the fifth Planner-authored error across this session** (a CHECK-constraint value, a stale suite baseline, a route count, test arithmetic, and now a self-contradictory grep). Same class every time: **a bare expected number asserted without checking reality** — exactly what the new LESSONS.md entry `2026-07-16: Never state a bare expected number in plan text` names, and what Rule 52 covers at the disposition layer. The lesson is earning its place before it has even been ingested.

## Context for Step 2 — the DB is now v17

The CEO restarted Flask at **12:17:53** today. Planner-verified on the live DB: `schema_version` = **17** (was 16), and `contract_documents` / `parsed_rate_candidates` / `parse_reconciliation_results` all now exist. exec-201's bump worked as designed — the fast-path was skipped and the migration ran. **This matters for row 6:** the two schema tests assert against a *fresh* DB built from code, so they are unaffected by the live migration — but if the full-suite count differs from the expected 2 known failures, check whether the migration shifted anything before assuming a regression.

Row 6: expect **exactly 2** failures (the CLAUDE.md pair). Plan 209's run had 4. **Report ACTUAL counts — do not force them to match mine.** Foreground `| cat` per CLAUDE.md; **do not reach for Monitor** (it tripped a denial gate on 209's QA).
