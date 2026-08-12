# Executable: proposal 330 — walk-register schema v0.1 → v0.2 (the panel-row form + the Deviations open tail), on the SCHEMA-OWNER surfaces; flip 330 to `implemented`

**Type:** Executable
**Project:** bellows
**Depends on:** executable-364 (Done — whose panel seat 1 RE-SCOPED 330 to these surfaces: the schema doc, the validator, the DC pointer), executable-360/362 (the routing), plan 338 (Done — wrote the v0.1 schema doc)
**Created:** 2026-08-12
**Author:** Planner
**Slug:** `schema02-2026-08-12`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2
**Test Scope:** targeted (`tests/test_walk_register_lint.py` — baseline **19 passed / 0 failed**, measured; QA row 4 re-derives)

⚠️ **ID NOTE:** id read at deposit (`next_id` **365** at authoring — a PREDICTION; five foreign consumptions today; the freeze reads fresh).

## Why
Proposal 330 (entry 322) is the cold-panel batch's last codify row, held out of plan 364 by its own panel seat 1: the "0.1 is only a convention" premise was FALSE — the schema has a committed home (`bellows/knowledge/architecture/walk-register-schema.md`, plan 338) and a live validator (`bellows/scripts/walk_register_lint.py`); amending anywhere else would fork it. This plan lands 0.2 ON those surfaces: **(1)** the schema doc — the sanctioned per-seat panel-row form (SAME eight columns, `walk` = `panel-N`; per-finding detail in the plan's seat lines; both panel-bearing cycles converged on it independently and each had to declare it as a deviation) + the Deviations open-tail convention + the version note (0.2 is additive; 0.1 registers stay valid); **(2)** the validator's docstring version reference (its ONLY `0.1` — measured; the validator checks structure, never the declared version value, so NO logic change: stated as a verified absence, not an assumption); **(3)** DC §3's pointer — VERSION-AGNOSTIC by measurement (names the file, no version), so NO DC edit: QA row 3 proves the absence. Then flip 330. **The queue empties for real this time.**

## Scope
- **One docs file** via the COMMITTED builder `governance/knowledge/research/builder-schema02-2026-08-12.py` (all-or-nothing, anchors count-asserted; dry-run **`OK — 3 edits`**, numstat **`12 2`**).
- **One docstring line** in `bellows/scripts/walk_register_lint.py`: `walk-register-schema v0.1` → `v0.2` (count-1 anchor measured; NO other code change — the version-value-agnostic behavior is the design, verified by source read AND by 364's panel-row register passing CONFORMANT).
- **One DB write:** 330 `accepted|codify → implemented`, `status_updated_by='ceo'`, in-statement Z-stamp (prior stamp `2026-08-12T17:12:07Z` Z-GLOB-MATCHING → one-value `NOT IN` exclusion, re-measured).
- **No DC edit; no LESSONS/FORWARD touch by any step.** Env facts: the standing four (ugrep `-F`/zero-count exit-1/printed-count-is-the-assertion; same-invocation state; `find` never glob; canonical absolute DB path).

## Freeze checklist (deposit path — items 1–4 BEFORE the copy, item 5 immediately AFTER)
1. Substitute the read id at the bootstrap `<id>` site AND TASK F's `-m`; probe: `grep -oF -- '<id' <deposit-path> | wc -l` → **2** (both residual tokens on this line).
2. **Diff draft↔mirror immediately before the copy** — empty-except-substitutions is the precondition.
3. Final `plan_lint` at the FAITHFUL scratchpad mirror (never the real `decisions/`) — WARN set matches Conformance.
4. A0-fresh: 330 still `accepted|codify` @ `2026-08-12T17:12:07Z` (instrumentation); schema-doc sha still the A1 pin; builder re-run still `12 2`; tests still 19/0.
5. Post-copy `ls` the real `bellows/knowledge/decisions/` — the claim carries the item-1 id (mismatch = foreign consumption; report, never re-copy).

## Conflict Ledger
**C1** the 330 exclusion from 364 was immutable; its INCLUSION here is the same decision's completion — one row, immutable. **C2** builder all-or-nothing; the docstring edit anchor count-1 asserted before the edit. **C3** docs before DB; A0 completes the half-state. **C4** backup adjacent, `BK=1` via `?immutable=1` against THE FOUND BACKUP. **C5** flip scoped `id = 330 AND status='accepted'`. **C6** sentinels BY NAME — PRE, ACC, MAXID, BK, CHANGES, GLOBOK — SIX; `CHANGES=1`, `GLOBOK=1` with the exclusion. **C7** capture in-txn: `id <= 332 AND id != 330` → **331 rows** (measured). **C8** commits cd-first (`/Users/marklehn/Developer/GitHub/bellows`) + pathspec + name-only + bare toplevel; post-commit asserts `-C`-pinned to CAPTURE_COMMIT, never `HEAD`. **C9** serialized dispatch stated.

## How to Run This Plan
**Bootstrap:**
```
Read the plan at knowledge/decisions/in-progress-executable-365.md (the daemon renames on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```
⚠️ HALT ROUTING: Step 1 reads this plan, both live bellows files, the committed builder, the canonical DB (`/Users/marklehn/Developer/GitHub/lessons-forge/lessons-forge.db`). Step 2 reads this plan, the dev-log, the live files, the DB read-only, `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`.

---

## Drafting Cycle

**Tier:** T1 — bellows docs + one docstring line + a 1-row scoped flip (T-2 fires → T1). Clone lineage: 364's step machinery at 1-row scale; the schema content from proposal 330/entry 322 as re-scoped by 364's seat 1.

**Walk 0 (context pin):** schema-doc sha `66c4da1e…` (porcelain clean), title/version anchors count-1; validator docstring anchor `walk-register-schema v0.1` count-1 (the file's ONLY `0.1` — measured); the validator's version-value-agnostic design verified by source read (SCHEMA_DECL_RE captures, never compares) AND live (364's panel-row register CONFORMANT); test baseline 19/0 (the five `0.1`s in the test file are FIXTURE declarations — valid under the agnostic design, untouched); DC §3 pointer version-agnostic (no DC edit owed — probed); 330 `accepted|codify|instrumentation` @ `17:12:07Z`, the sole accepted row (ACC=1); MAXID=332; capture 331; dry-run `OK — 3 edits`, numstat `12 2`.

**Walk 1** (whole artifact, five lenses, sequential):
- Weak spots:          w1 1 folded — instruction, authoring (the version note's "registers declaring 0.1 remain valid" needed the validator-behavior grounding stated IN the schema doc, not just this plan — the builder's E3 text now carries "The validator checks structure, not the declared version value"; without it a future reader could add a version gate believing 0.1 registers invalid).
- Destruction:         w1 dry (additive section + two version strings + one docstring line; nothing relaxed; 0.1 registers explicitly stay valid).
- Vulnerabilities:     w1 executed — builder dry-run `12 2` stable; the docstring edit rehearsed on a scratch copy (count-1 pre, probe 1 post); flip rehearsed on a DB copy: PRE=1/ACC=1/MAXID=332/CAP=331/CHANGES=1/GLOBOK=1/re-run 0; tests 19/0 on the live tree.
- Integration-record:  w1 dry (the 364 seat-1 re-scope record cross-referenced; the plan lands exactly the surfaces it named; entry 322's fields honored — the per-seat form reuses the eight columns, no new fields invented: the 364-seat-1 MED about invented fields heeded).
- ACID:                w1 dry (docs-then-DB; the two file edits + one flip behind one gate; A0 owns the half-states; backup is the floor).

**Walk-1 split: instruction 1 / record 0.** Re-opens; walk 2 owed.

**Walk 2** (whole artifact; new surface = the version-note fold):
- Weak spots:          w2 dry (the grounding sentence verified in the builder's E3 from the artifact).
- Destruction:         w2 dry.
- Vulnerabilities:     w2 executed, **1 folded — instruction: A1's sha pin carried a FABRICATED TAIL (authored from a 20-char display prefix with the remainder invented — the predicted-number class in sha form); the fresh full-hash measurement caught it; pin corrected to the measured `66c4da1e…c96418`.** Battery otherwise stable (docstring rehearsal `1 1`; flip PRE=1/CAP=331/CHANGES=1/GLOBOK=1/POSTACC=0; the validator run LIVE on the panel-row register → CONFORMANT, QA row 3's premise proven).
- Integration-record:  w2 dry.
- ACID:                w2 dry.

**Walk-2 split: instruction 1 / record 0.** Re-opens; walk 3 owed.

**Walk 3** (whole artifact; new surface = the corrected pin):
- Weak spots:          w3 dry (the pin re-read from the artifact == the fresh measurement, both sites).
- Destruction:         w3 dry.
- Vulnerabilities:     w3 dry (battery values stable on re-run).
- Integration-record:  w3 dry (the catch recorded here and in the register).
- ACID:                w3 dry.

**Walk-3 split: instruction 0 / record 0 — LITERAL DRY. The §2 bar met on the dry branch; T1, no panel owed.**

**Conformance (§5):** shape-stability run post-walk-1, re-runs post-walk-2 and at deposit, at the FAITHFUL mirror (fidelity: bellows root files the plan references — `scripts/walk_register_lint.py`, `tests/test_walk_register_lint.py`, `knowledge/architecture/walk-register-schema.md` — copied under `<scratch>/stage-b/bellows/`). **Measured: EXIT 0, ZERO WARNs.** Last run: at deposit.

**Closing:** walk 3 dry — instruction 0 / record 0; closed on the dry branch after 3 walks; residue: none.

---

## STEP 1 — DEV (builder + docstring + commit + flip 330)

> **FIRST — visible chat message; do NOT rename this plan file.** Edits land at ABSOLUTE paths in the bellows repo; a HALT after edits leaves the tree as-is, reported loudly.
> **A0 (first match wins):** (1) 330 `implemented` → verify commit-by-slug via QA row-1's SPELLED discovery, deposits survived; report complete. (2) docs committed (both files in name-only) + 330 still `accepted` → porcelain clean on top, DOC_SHA/LINT_SHA from the commit, reuse any `pre-s02-*` backup (prefix-only `find`; >1 → HALT), re-run probes on committed content → B → G. (3) docs modified-UNCOMMITTED → HALT with the probe table. (4) fresh-with-unexplained-backup → HALT. (5) fresh — porcelain clean for both target paths, schema title reads `v0.1`, 330 `accepted|codify` @ `2026-08-12T17:12:07Z`, no backup → A1. Other → HALT with the observed triple.
> **A1 — pin:** `shasum -a 256 /Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/walk-register-schema.md` == `66c4da1e77aba74a1daa2508867aaa752cdb18db2712ecd709073740e8c96418`. Mismatch → HALT.
> **BUILDER:** `python3 /Users/marklehn/Developer/GitHub/governance/knowledge/research/builder-schema02-2026-08-12.py /Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/walk-register-schema.md /Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/walk-register-schema.md` → exit 0 + `OK — 3 edits applied`. AssertionError → HALT, quote verbatim; the file is untouched by construction. Post-probes (`grep -cF` on the live file): `# Walk Register Schema — v0.2` → 1; `**schema_version:** \`0.2\`` → 1 (⚠️ backtick-quoted — single-quote the pattern); `Panel rows and the Deviations open tail` → 1; the old title and old version line → 0 each.
> **TASK D — the docstring:** in `/Users/marklehn/Developer/GitHub/bellows/scripts/walk_register_lint.py`, replace the single occurrence of `walk-register-schema v0.1` with `walk-register-schema v0.2` (assert count 1 BEFORE the edit; python temp-and-replace, never sed -i). Post: `grep -cF 'walk-register-schema v0.2'` → 1, `grep -cF 'walk-register-schema v0.1'` → 0. **NO other line in that file changes** (numstat will prove 1/1 for it).
> **TESTS (targeted, foreground):** `cd /Users/marklehn/Developer/GitHub/bellows && python3 -m pytest tests/test_walk_register_lint.py -q` → **19 passed** (the fixtures' `0.1` declarations stay valid by the version-agnostic design — a failure here means that premise broke → HALT, never patch a test).
> **DOC_SHA + LINT_SHA** pinned before commit. **TASK F:** `cd /Users/marklehn/Developer/GitHub/bellows && git add knowledge/architecture/walk-register-schema.md scripts/walk_register_lint.py && git commit -m "[365] schema02(schema02-2026-08-12): walk-register schema v0.1 -> v0.2 — the sanctioned per-seat panel-row form + the Deviations open tail; validator docstring; 0.1 registers stay valid" -- knowledge/architecture/walk-register-schema.md scripts/walk_register_lint.py && git rev-parse HEAD && git rev-parse --show-toplevel` (expect the new hash then `/Users/marklehn/Developer/GitHub/bellows`). **The printed hash is CAPTURE_COMMIT.** Numstat, spelled: `git -C /Users/marklehn/Developer/GitHub/bellows show <CAPTURE_COMMIT> --numstat --format=` → exactly TWO lines: `12	2	knowledge/architecture/walk-register-schema.md` and `1	1	scripts/walk_register_lint.py`. **F2:** committed-content shas == DOC_SHA/LINT_SHA; name-only exactly the two paths.
> **B — backup**, exactly: `sqlite3 -bail /Users/marklehn/Developer/GitHub/lessons-forge/lessons-forge.db ".timeout 5000" ".backup /Users/marklehn/Developer/GitHub/lessons-forge/pre-s02-$(date -u +%Y%m%d_%H%M%S).db"`; locate prefix-only; assert `sqlite3 -bail "file:<found-abs>?immutable=1" ".timeout 5000" "SELECT 'BK='||COUNT(*) FROM lesson_proposals WHERE id=330 AND status='accepted';"` → **BK=1**.
> **G1** (file `knowledge/development/s02-rehearsal.sql`, exactly; runner `sqlite3 -bail <canonical-abs> ".timeout 5000" ".read <abs>"`):
> ```
> BEGIN IMMEDIATE;
> SELECT 'PRE='||COUNT(*) FROM lesson_proposals WHERE id=330 AND status='accepted' AND route='codify';
> SELECT 'ACC='||COUNT(*) FROM lesson_proposals WHERE status='accepted' AND route='codify';
> SELECT 'MAXID='||MAX(id) FROM lesson_proposals;
> ROLLBACK;
> ```
> Assert **PRE=1, ACC=1, MAXID=332** (ACC>1 → in-window routing → HALT; MAXID>332 reported-benign, the capture bound stays).
> **G2** (`mkdir -p` the evidence dir FIRST; file `knowledge/development/s02-flip.sql`, exactly; `.output` absolute):
> ```
> BEGIN IMMEDIATE;
> .output <tree-abs>/knowledge/qa/evidence/schema02-2026-08-12/outside-range-ids.txt
> SELECT id||'|'||category||'|'||status||'|'||COALESCE(route,'')||'|'||COALESCE(status_updated_at,'')||'|'||COALESCE(status_updated_by,'') FROM lesson_proposals WHERE id <= 332 AND id != 330 ORDER BY id;
> .output stdout
> UPDATE lesson_proposals SET status='implemented', status_updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), status_updated_by='ceo' WHERE id = 330 AND status='accepted';
> SELECT 'CHANGES='||changes();
> SELECT 'GLOBOK='||COUNT(*) FROM lesson_proposals WHERE id = 330 AND status_updated_at GLOB '20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z' AND status_updated_at NOT IN ('2026-08-12T17:12:07Z');
> COMMIT;
> ```
> **CHANGES=1, GLOBOK=1**; capture **331 lines** read post-commit. **G3 — read-back** (read-only form): 330 → `instrumentation|implemented|codify|ceo|<Z ≠ 17:12:07Z>`; AND the queue: `accepted|codify` COUNT → **0 — THE COLD-PANEL BATCH FULLY DISPOSED** (4 implemented by 364, 330 here, 331 reference|backlog). RAW to `flip-readback.txt`.
> **Receipt** with the SIX named sentinels + DOC_SHA + LINT_SHA + CAPTURE_COMMIT + both numstat lines · `#### Prompt Feedback` · `#### Forward Register`: `NONE`. **FINAL ACTION** — commit deposits: cd-first + pathspec + name-only + bare toplevel.
>
> **Scope:**
> - `knowledge/development/dev-log-schema02-step-1-2026-08-12.md`
> - `knowledge/development/s02-rehearsal.sql`
> - `knowledge/development/s02-flip.sql`
> - `knowledge/qa/evidence/schema02-2026-08-12/outside-range-ids.txt`
> - `knowledge/qa/evidence/schema02-2026-08-12/flip-readback.txt`
>
> **Deposits:**
> - `bellows/knowledge/development/dev-log-schema02-step-1-2026-08-12.md`
> - `bellows/knowledge/development/s02-rehearsal.sql`
> - `bellows/knowledge/development/s02-flip.sql`
> - `bellows/knowledge/qa/evidence/schema02-2026-08-12/outside-range-ids.txt`
> - `bellows/knowledge/qa/evidence/schema02-2026-08-12/flip-readback.txt`

## STEP 2 — QA

> **FIRST — do NOT rename this plan file. Deliverable Verification (Rule 8/17)**, ✅/❌ table, any ❌ → HALT. **Rule 20 self-check** (canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`; `plan_slug`: `schema02-2026-08-12`; `qa_report_path`: `<tree>/knowledge/qa/schema02-qa-2026-08-12.md`; `evidence_dir`: `<tree>/knowledge/qa/evidence/schema02-2026-08-12/`; `required_evidence_files`: `[doc-integrity.txt, db-invariants.txt, validator-run.txt, pytest_targeted.txt]`, all four BEFORE the block; literal stdout: the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line, byte-exact). ONE read-only DB form; RAW evidence.
> **1. DOC INTEGRITY** — commit by slug, spelled: `git -C /Users/marklehn/Developer/GitHub/bellows log -n 1 --format='%H %s' --grep='schema02-2026-08-12' -- knowledge/architecture/walk-register-schema.md` → exactly one line; committed shas == live == DOC_SHA/LINT_SHA; numstat two lines `12 2` + `1 1`; name-only exact; porcelain clean both paths. → `doc-integrity.txt`
> **2. THE CLAUSES LANDED** — live probes: v0.2 title → 1, version line → 1, panel section → 1, olds → 0; validator docstring v0.2 → 1, v0.1 → 0. → `doc-integrity.txt`
> **3. POINTER + BEHAVIOR** — DC §3's pointer line names the schema FILE with NO version token (`grep -F 'walk-register-schema.md' /Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md | grep -cF 'v0.1'` → 0; the pointer grep itself → ≥1 — the no-DC-edit premise, proven); **run the validator live**: `python3 /Users/marklehn/Developer/GitHub/bellows/scripts/walk_register_lint.py /Users/marklehn/Developer/GitHub/governance/knowledge/research/walk-register-gate2-coldpanel-2026-08-12.md` → file_status CONFORMANT (the panel-row register under the NEW docstring — behavior unchanged, the agnostic design's live proof). → `validator-run.txt`
> **4. TESTS** — `python3 -m pytest tests/test_walk_register_lint.py -q` FOREGROUND → vs 19/0, delta reported never asserted. → `pytest_targeted.txt`
> **5. FLIP + BLAST RADIUS** — 330 per-id `instrumentation|implemented|codify|ceo` Z ≠ prior; **`accepted|codify` → 0**; capture re-run (COPY from G2) diff vs the 331-line file; partition per convention. → `db-invariants.txt`
> `## Evidence and Narrative` · Receipt · `#### Forward Register`: `NONE`. **FINAL ACTION** — commit deposits, cd-first + pathspec + name-only + bare toplevel.
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
