# Executable: QA-only corrective for the schema02 write (plan 365's step 2) — the Rule 20 block that never ran, second instance of the class

**Type:** Executable
**Project:** bellows
**Depends on:** executable-365 (HALTED at step 2 — its STEP 1 IS COMMITTED AND CORRECT: schema v0.2 + docstring + the 330 flip, Planner-verified at both gates; only the QA process failed), executable-362 (Done — the corrective FORM this plan clones: its order-is-load-bearing spelling secured compliance)
**Created:** 2026-08-12
**Author:** Planner
**Slug:** `schema02-2026-08-12-qa-corrective`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 1
**Test Scope:** targeted (`tests/test_walk_register_lint.py`; baseline 19/0; row 4 re-derives)

⚠️ **ID NOTE:** id read at deposit (`next_id` **366** at authoring — a PREDICTION; the freeze reads fresh).

## Why
Plan 365's step 2 gate-failed on `rule_20_self_check`, verified REAL (banner count 0 — the block never ran). **The second instance of this class today** (360→362 the first); the remedy that worked is cloned: ONE read-only QA step, the same five rows, with the Rule 20 machinery's ORDER spelled as load-bearing. Step 1's deliverables stand Planner-verified: schema doc v0.2, validator docstring v0.2 (19/0), 330 `implemented|codify|ceo` @ `2026-08-12T20:22:24Z`, queue 0, capture 331 lines, CAPTURE_COMMIT `705ea50d…`.

## Scope
- **Read-only everywhere:** the canonical DB via `?mode=ro` absolute path; no writes to any table or doctrine file. The QA report path OVERWRITES 365's incomplete report (git history preserves it).
- Env facts: the standing four.

## Freeze checklist (deposit path — items 1–3 BEFORE the copy, item 4 immediately AFTER)
1. Substitute the read id at the bootstrap `<id>` site; probe: `grep -oF -- '<id' <deposit-path> | wc -l` → **2** (both residual on this line).
2. **Diff draft↔mirror immediately before the copy** — empty-except-substitution is the precondition.
3. Final `plan_lint` at the FAITHFUL mirror — WARN set matches Conformance. A0-fresh: 330 still `implemented`; schema title still v0.2.
4. Post-copy `ls` the real `bellows/knowledge/decisions/` — the claim carries the item-1 id.

## Conflict Ledger
**C1** every surface is READ — a mismatch HALTs, nothing repairs. **C2** the report overwrite is the deliverable. **C3** commits cd-first + pathspec + name-only + bare toplevel; asserts pin the printed hash.

## How to Run This Plan
**Bootstrap:**
```
Read the plan at knowledge/decisions/in-progress-executable-366.md (the daemon renames on claim). Execute Step 1 ONLY. This is the plan's only step.
```

---

## Drafting Cycle

**Tier:** T1 — read-only single-step corrective; clone of 362's PROVEN corrective form (its agent complied with the spelled order), re-targeted to 365's rows. **Newest same-class: 362 itself — the only prior QA-only corrective; clone origin and newest same-class are ONE plan, both roles stated** (the §2.6 comparison collapses to identity; the diff IS the re-target: bellows tree for lessons-forge tree, five schema02 rows for six routing rows, 19/0 for 55/0).

**Walk 0 (context pin):** the five row-values re-measured at authoring (schema v0.2 title live; docstring v0.2 count 1; 330 `implemented|codify|ceo|2026-08-12T20:22:24Z`; queue 0; capture file 331 lines on bellows main; tests 19/0); 365's incomplete QA report + four evidence files on main (git-preserved); CAPTURE_COMMIT `705ea50d…` from 365's receipt, re-verified by `git -C bellows show` name-only.

**Walk 1** (whole artifact, five lenses, sequential):
- Weak spots:          w1 dry (A0 keyed per-value; every expected value carries its measured source).
- Destruction:         w1 dry (read-only; the overwrite deliberate and git-preserved).
- Vulnerabilities:     w1 executed — all row queries rehearsed live read-only (values as pinned); the Rule 20 block's four placeholders resolve against the bellows tree; the ordering trap spelled from the block's own sys.exit behavior.
- Integration-record:  w1 dry (the corrective convention: stable slug + suffix, narrowly-keyed A0, never-rerun; the class-pattern note recorded — two instances today, the bellows-side hardening candidate named in the 365 stop-verdict).
- ACID:                w1 dry (one read-only step; no window).

**Walk-1 split: instruction 0 / record 0 — DRY at walk 1. T1 bar met; no panel owed.**

**Conformance (§5):** at shape-stability and at deposit, at the FAITHFUL mirror (fidelity files copied under the mirror root: `scripts/walk_register_lint.py`, `tests/test_walk_register_lint.py`, `knowledge/architecture/walk-register-schema.md`, `knowledge/development/s02-flip.sql`). **History: first run → EXIT 0, ONE (k) WARN — the clone framing did not name its newest same-class (362 is BOTH origin and newest; the identity is now stated, the comparison collapsing declared); cleared EARNED. Final: EXIT 0, ZERO WARNs.** Last run: at deposit.

**Closing:** walk 1 dry — instruction 0 / record 0; closed on the dry branch after 1 walk (a read-only corrective of an already-twice-verified state); residue: none.

---

## STEP 1 — QA (the only step)

> **FIRST — visible chat message; do NOT rename this plan file.**
> **A0 (narrowly keyed — first match wins):** (1) 330 reads EXACTLY `implemented|codify|ceo|2026-08-12T20:22:24Z` AND the schema title reads `# Walk Register Schema — v0.2` → proceed. (2) ANY other state → **HALT with the read-back — this plan repairs nothing.**
> **⚠️ ORDER IS LOAD-BEARING (the machinery plan 365's QA skipped — and 360's before it; the 362 form, which secured compliance, verbatim in intent):** (i) run all row checks and write ALL FOUR evidence files; (ii) write the QA REPORT with its complete `## Verification Table`; (iii) THEN run the Rule 20 canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (ABSOLUTE path) — it `sys.exit(1)`s if the report or any evidence file is missing, WHY the order matters; (iv) APPEND the block's stdout to the report; (v) self-grep the banner into evidence. Placeholders: `plan_slug`: `schema02-2026-08-12-qa-corrective`; `qa_report_path`: `<tree-abs>/knowledge/qa/schema02-qa-2026-08-12.md`; `evidence_dir`: `<tree-abs>/knowledge/qa/evidence/schema02-2026-08-12/`; `required_evidence_files`: `["doc-integrity.txt", "db-invariants.txt", "validator-run.txt", "pytest_targeted.txt"]`. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line byte-exact in the deposited report. Rule 19 verbatim; one glyph per status cell; no `|` in cells; `## Evidence and Narrative` directly after the table.
> **The five rows (columns `| # | Claim | Status (✅/❌) | Measured value | DB source | Evidence |`; ONE read-only DB form; RAW evidence):**
> **1. DOC INTEGRITY** — commit by slug spelled: `git -C /Users/marklehn/Developer/GitHub/bellows log -n 1 --format='%H %s' --grep='schema02-2026-08-12' -- knowledge/architecture/walk-register-schema.md` → exactly one line == `705ea50d…`-prefixed; committed shas == live; numstat `12 2` + `1 1`; name-only exactly the two paths; porcelain clean. → `doc-integrity.txt`
> **2. CLAUSES** — v0.2 title → 1, version line → 1, panel section → 1, olds → 0; docstring v0.2 → 1, v0.1 → 0. → `doc-integrity.txt`
> **3. POINTER + BEHAVIOR** — DC §3 pointer version-token count 0 with the pointer itself ≥1; **run the validator live** on `governance/knowledge/research/walk-register-gate2-coldpanel-2026-08-12.md` → CONFORMANT. → `validator-run.txt`
> **4. TESTS** — `python3 -m pytest tests/test_walk_register_lint.py -q` FOREGROUND → vs 19/0, delta reported never asserted. → `pytest_targeted.txt`
> **5. FLIP + BLAST RADIUS** — 330 per-id as A0's key; `accepted|codify` → 0; capture re-run (COPY the SELECT from `knowledge/development/s02-flip.sql` on main) diff vs the 331-line file; partition per convention. → `db-invariants.txt`
> `## Evidence and Narrative` · Receipt · `### Ledger Updates` · `#### Prompt Feedback` · `#### Forward Register`: `NONE`. **FINAL ACTION — commit-evidence-first:** commit ALL deposits by explicit pathspec BEFORE the receipt's closing statement; cd-first + pathspec + name-only + bare `git rev-parse --show-toplevel`.
>
> **Scope:**
> - `knowledge/qa/schema02-qa-2026-08-12.md`
> - `knowledge/qa/evidence/schema02-2026-08-12/doc-integrity.txt`
> - `knowledge/qa/evidence/schema02-2026-08-12/db-invariants.txt`
> - `knowledge/qa/evidence/schema02-2026-08-12/validator-run.txt`
> - `knowledge/qa/evidence/schema02-2026-08-12/pytest_targeted.txt`
>
> **Deposits:**
> - `bellows/knowledge/qa/schema02-qa-2026-08-12.md`
> - `bellows/knowledge/qa/evidence/schema02-2026-08-12/doc-integrity.txt`
> - `bellows/knowledge/qa/evidence/schema02-2026-08-12/db-invariants.txt`
> - `bellows/knowledge/qa/evidence/schema02-2026-08-12/validator-run.txt`
> - `bellows/knowledge/qa/evidence/schema02-2026-08-12/pytest_targeted.txt`
