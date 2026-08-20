# bellows — cycle_check.py: the drafting-cycle validator (CONTINUE / BAR_MET / ESCALATE)
**Date:** 2026-08-19 | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_qa_step

## Context

Component 1 of the routed cycle-automation proposal (`proposal-cycle-automation-depositor-2026-08-18.md`, CEO-routed 2026-08-19). Builds `scripts/cycle_check.py` — a deterministic, stdlib-only validator that replaces the CEO's manual "walk N" gate, emitting exactly one of `CONTINUE` · `BAR_MET` · `ESCALATE:<reason>`. It is a NEW, UNWIRED script (no caller yet — the Planner adopts it per-walk in-session; the in-bellows depositor re-runs it later); a bug is fully contained until adoption, which is why T1 warm is right-sized (self-escalation available).

**This executable implements the diagnostic-460 census WITHOUT re-verification (Rule 27, T-7).** The build spec is the 9-row Rule 27 Gap Assessment and the Q6 contract in `knowledge/research/cycle-check-format-census-2026-08-19.md` (in the bellows tree; also `knowledge/decisions/Done/diagnostic-460.md` for the plan). Do NOT re-derive the format census — the counts (37 blocks · 3 per-lens class-split · 2 STATUS-aggregate · presence-based discriminator) are Planner-verified and fixed.

**Load-bearing design facts from the census (do not re-litigate):**
- `cycle_yields.py` provides reusable primitives — `extract_dc_blocks`, `parse_lens_line`, `LENS_PREFIXES`, `PASS_FOLDED_RE`, `PASS_DRY_RE` — but has NO instruction/record class-split parser. `cycle_check` adds one: `instruction\s+(\d+)\s*/\s*record\s+(\d+)`.
- The class split is present in only 3/37 Done blocks → **presence-based N/A** (not date/id). Absent split → assert #1 N/A silently, never FAIL, never block BAR_MET.
- `fold_check.py` stores baselines at `<artifact.parent>/.<artifact.name>.foldcheck.json` (confirmed `fold_check.py:121`).
- `plan_lint` check (f) is SUPERSEDED, not removed — no edit to `plan_lint.py` in this build.

## Drafting Cycle
**Tier:** T1 — triggers: T-7 (implements diagnostic-460's Gap Assessment per Rule 27), T-8 (novel). Not a T-5/T-6 surface (a new unwired script, reads doctrine but changes none — proposal §9). No mandatory cold panel; the real correctness guard is the QA **live canary** against real Done/ blocks (synthetic fixtures inherit the author's wrong model — DC live-canary lesson).
**Walk 0 (context pin):** spec = `knowledge/research/cycle-check-format-census-2026-08-19.md` (Q5 gap table (a)–(i) + Q6 contract). Reuse targets in `scripts/cycle_yields.py`: `extract_dc_blocks` (block extraction, `^## Drafting Cycle$` after fence-strip), `parse_lens_line` (lens/pass/fold/dry/origin), `LENS_PREFIXES` (handles `Integration`≡`Integration-record`) — verified present this session. `fold_check.py` baseline at `.{name}.foldcheck.json`. Test convention: `tests/test_<script>.py` + `tests/conftest.py` + `tests/fixtures/` (siblings: `test_cycle_yields.py`, `test_fold_check.py`, `test_plan_lint.py`). Clone-diff: structural sibling `cycle_yields.py` (same parse-the-Cycle-Log class, stdlib, `find_root` via `DRAFTING_CYCLE.md`); reuse is by IMPORT, and the import surface is verified before use ("reuse is a clone decision"). Bellows suite baseline is green (Rule 21).
**Direction verdict (after walk 1):** **PROCEED** — the build angle (implement the census's gap table + contract as a stdlib validator, guarded by a live canary) is sound; no forcing finding. Walk 1's folds are implementability corrections, not a premise kill.
**Walks:** 6 (bar MET — walk 6 class-dry: zero instruction-class, one record completeness note; no restructuring fold). Instruction yields 5 → 2 → 2 → 1 → 1 → 0.
- Weak spots (1.4):     w1 1 folded — instruction 1 / record 0 (W1: define "current walk" = highest-numbered walk carrying lens data; the decision function referenced current/prior without defining them). w2 dry. w3 dry. w4 dry. w5 dry. w6 1 folded — instruction 0 / record 1 (R1: QA check-(1) enumeration synced to include claimed-close-unmet — record completeness; already covered by "EACH branch").
- Destruction (2.4):    w1 1 folded — instruction 1 / record 0 (D1: cycle_check must be strictly READ-ONLY — never re-save fold_check baselines / write / commit; the census's "re-run --save-baseline" alternative would clobber the state it validates). w2 dry. w3 dry. w4 dry. w5 dry. w6 dry.
- Vulnerabilities (3.2): w1 1 folded — instruction 1 / record 0 (V1: restructuring-fold detection was referenced but unspecified and not textually inferable — made it convention-token-based, never fabricated from prose). w2 1 folded — instruction 1 / record 0 (V2: the class split binds to the immediately-preceding `N folded` pass; multi-pass lens lines must be checked per-pass). w3 1 folded — instruction 1 / record 0 (V3: steps 4/5 (yield-rising, plateau) must be N/A when per-walk instruction counts are unparseable). w4 1 folded — instruction 1 / record 0 (V4: the ANTI-FABRICATION guard — a claimed close steps 1–7 do not earn must `ESCALATE:claimed-close-unmet`, not fall through to CONTINUE; proposal §1). w5 1 folded — instruction 1 / record 0 (V5: COLLAPSED step 8 (my w4 addition, under-specified twice) into one crisp rule — token-based claim detection + precedence: override only a computed CONTINUE). w6 dry.
- Integration-record:   w1 1 folded — instruction 1 / record 0 (I1: assert #2 fragile/mis-specified — reframed toward register-presence + git best-effort). w2 1 folded — instruction 1 / record 0 (I2: reuse must follow the EXISTING sibling-script import convention — no new sys.path hack). w3 1 folded — instruction 1 / record 0 (I3: CORRECTS I1 — the walk register is a SEPARATE, OPTIONAL, sometimes cross-repo file (schema v0.3); collapsed assert #2 to its fail-safe core). w4 dry. w5 dry. w6 dry.
- ACID (5.2):           w1 1 folded — instruction 1 / record 0 (A1: assert #3 must degrade CONSISTENTLY with #2 — read-only baseline-existence always; timestamp-compare only when #2 reliably knows the commit). w2 dry. w3 dry. w4 dry. w5 dry. w6 dry.
**Walk 1 STATUS:** 5 folded — instruction 5 / record 0 — NOT dry.
**Walk 2 STATUS:** 2 folded — instruction 2 / record 0 — NOT dry (yield 5→2, falling).
**Walk 3 STATUS:** 2 folded — instruction 2 / record 0 — NOT dry (yield flat; one fold corrected a walk-1 fold).
**Walk 4 STATUS:** 1 folded — instruction 1 / record 0 — NOT dry (the anti-fabrication guard added).
**Walk 5 STATUS:** 1 folded — instruction 1 / record 0 — NOT dry (a self-correction collapsing step 8 — the region my w4 fold created).
**Walk 6 STATUS:** 0 instruction / 1 record — **CLASS-DRY** (zero instruction-class per DC:40; the single record note is completeness, not a behavior change), no restructuring fold. §2 bar MET.
**Conflicts:** none.
**§5 Conformance:** `plan_lint` run at shape-stability (walk 6) → **0 FAIL** after correcting two items it surfaced at close: `pause_for_verdict` `after_step_2`→`after_qa_step` (invalid enum) and the Rule 20 QA banner pair inlined (check (c) byte-matches `Rule 20 — QA Self-Check Results` + `PASSED — SELF-CHECK PASSED`). STEP count asserted = 2 (`grep -c '^## STEP '`). Benign residual WARNs: no-Closing cleared by this block; the (o1) missing-path and (o2) relative-deposit WARNs are the location-dependent bellows-in-tree class — the reused/deposit paths resolve at the deposit path (`bellows/…`), not from `scratchpad/` — same class `diagnostic-455`/`-460` cleared.
**Closing:** full walk 6 class-dry (zero instruction-class, one record completeness note), no restructuring fold; §5 conformance clean (0 FAIL); closing-record re-read run (this block), dry; cycle CLOSED. Deposit exactly once (pending CEO go).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **Identity:** You are building `scripts/cycle_check.py` and its tests. Implement the diagnostic-460 census's Gap Assessment (a)–(i) and Q6 contract EXACTLY — it is a Rule 27 build spec; do not re-derive the format census. Read `knowledge/research/cycle-check-format-census-2026-08-19.md` first (Q5 table + Q6 contract are the authority).
>
> **Reuse (verify before importing — "reuse is a clone decision").** `from cycle_yields import extract_dc_blocks, parse_lens_line, LENS_PREFIXES` (same `scripts/` dir; import runs no side effects — `cycle_yields` guards `main()` under `__main__`). Confirm each name's signature by reading `cycle_yields.py` before wiring it; if a signature differs from the census's description, STOP and report rather than adapting silently. **Match the EXISTING sibling-script import convention** used by `tests/test_cycle_yields.py` / `tests/test_fold_check.py` (they already import a `scripts/` module under pytest) so that BOTH the `python3 scripts/cycle_check.py <plan>` CLI and `pytest` resolve `from cycle_yields import …` identically — read one of those test files and follow its pattern; do not invent a new `sys.path` hack.
>
> **Implement `scripts/cycle_check.py` — stdlib only, no model judgment. The contract (Q6):**
> - Emits exactly one line to stdout then exits: `CONTINUE` (exit 0) · `BAR_MET` (exit 0) · `ESCALATE:<reason>` (exit 1).
> - ESCALATE reason vocabulary (closed set): `direction-class` · `new-ceo-decision` · `yield-rising` · `restructuring-fold` · `plateau` · `unparseable` · `uncommitted-walk` · `claimed-close-unmet` · `assert-fail:<N>`. (Cost/token and battery-failure escalations are DROPPED per routing.)
> - Usage: `cycle_check.py <plan.md>` — reads the plan's `## Drafting Cycle` block.
> - **Strictly READ-ONLY.** cycle_check reads the plan file, `git log`, and `fold_check` baseline files, then emits a verdict. It writes NOTHING, commits nothing, and NEVER invokes `fold_check --save-baseline` (that would clobber the baseline it is meant to inspect). A validator that mutates the state it validates is a defect.
> - **Definitions:** "current walk" = the highest-numbered walk carrying lens data in the block; "prior walk" = the walk before it.
>
> **The three asserts (Gap table a–c):**
> - **#1 Internal arithmetic.** New regex `instruction\s+(\d+)\s*/\s*record\s+(\d+)`. Per-lens: `instruction + record == the walk's stated fold total` (fold total via reused `PASS_FOLDED_RE`). **The split binds to the immediately-preceding `N folded` pass on the line;** a multi-pass lens line (`w1 2 folded — instruction 2 / record 0; w2 dry`) is checked per-pass, only for the passes that carry a split. If a STATUS/Walk-N aggregate class line exists, cross-check `aggregate == sum of per-lens`. **Presence-based N/A:** a pass with no class split → assert #1 N/A for it (silent, never FAIL, never block BAR_MET). Only 3/37 Done blocks carry the per-lens split; 2/37 carry the aggregate.
> - **#2 Evidence exists — fail-safe, never a false FAIL.** The walk register is a SEPARATE, OPTIONAL file (schema v0.3, `walk_register_lint.py`), referenced from the DC block by a `**Walk register:** <path>` line and present only for SOME cycles (diagnostic-429 declares one — cross-repo into `governance/`; diagnostic-460 and most plans have none). There is NO always-available inline register, so assert #2 corroborates when it can and returns N/A otherwise: **(a)** a register referenced at a path INSIDE the plan's own repo but MISSING → `assert-fail:2` (a broken reference is a real defect); a cross-repo reference (unreachable from the plan's repo) or no reference at all → N/A. **(b)** git corroboration: count the plan's `drafting(` / `[draft]` / `deposit(` commits scoped to the plan path in the repo holding the plan; a reliable committed context showing fewer commits than walks claimed → `ESCALATE:uncommitted-walk`; an ambiguous or uncommitted context → N/A. Do NOT exact-match `walk N` per commit and do NOT depend on `[<id>]` (absent pre-deposit — the Planner runs cycle_check on a slug draft before any id is minted). **Assert #2 NEVER FAILs on a plan that simply has no register and no reachable git context — that is the common, legitimate case (corrects walk-1 I1, whose "register always available" premise was wrong).**
> - **#3 Fold happened — read-only, degrades with #2.** For each walk claiming folds, verify `fold_check`'s baseline (`<plan.parent>/.<plan.name>.foldcheck.json`) EXISTS (read only; never re-save). Timestamp-compare (baseline no older than the walk's commit) ONLY when assert #2 reliably knows that commit; otherwise require existence alone (consistent degradation with #2 — never a FAIL on a signal #2 couldn't establish either). Baseline absent for a folding walk → `assert-fail:3`.
>
> **Decision function (Gap f — the load-bearing aggregation), evaluated in this order:**
> 1. `extract_dc_blocks` returns 0 or >1 blocks, OR no lens line parses → `ESCALATE:unparseable` (fail closed FIRST).
> 2. Any assert FAIL → `ESCALATE:assert-fail:<N>`.
> 3. Restructuring fold present in the current walk → `ESCALATE:restructuring-fold`. **Detection is convention-based, not inferred:** there is no reliable way to infer a restructuring fold from prose, so cycle_check flags it ONLY when a lens/STATUS line carries an explicit token from a documented set (`restructuring` / `restructure` / `reorder`). Absent that token it is treated as ABSENT — never fabricate this ESCALATE from free text. (If the convention proves too weak in adoption, that is a follow-up, not an inference to bake in now.)
> 4. Current walk instruction-class yield > prior walk's → `ESCALATE:yield-rising`.
> 5. Plateau: **3** consecutive walks at a flat instruction-class count with no new finding class → `ESCALATE:plateau`.
> 6. Current walk is dry (0 instruction-class) AND all asserts PASS/N/A AND no restructuring fold AND no plateau → `BAR_MET`.
> 7. Otherwise → `CONTINUE`.
> 8. **Anti-fabrication cross-check — the guard this validator exists for.** "Claims closure" is token-based, not inferred (same discipline as the restructuring token, V1): the block contains any of `**Closing:**`, `CLOSED`, `CYCLE COMPLETE`, or `bar met` / `§2 bar met`. If the block claims closure AND the verdict computed by steps 1–7 is `CONTINUE` (not BAR_MET, and not already an ESCALATE), override to `ESCALATE:claimed-close-unmet`. **Precedence:** a pre-existing ESCALATE from 1–7 (e.g. `assert-fail:N`) is more specific and STANDS — do not mask it. A self-authored close the evidence does not earn is the §1 failure mode; a bare CONTINUE would silently accept the claim.
> N/A asserts participate NEUTRALLY (never block BAR_MET, never trigger ESCALATE).
>
> **Stateless plateau (Gap f / Q6).** Derive the counter from the block's own walk history each run: parse per-walk instruction-class counts (per-lens class-split sums, or Walk-N STATUS lines); working back from the current walk, count consecutive walks with an identical instruction count AND no lens that was previously dry producing a fold. No in-memory state. **If per-walk instruction counts are NOT parseable (legacy/no-split plans with no Walk-N STATUS lines), decision-function steps 4 (yield-rising) and 5 (plateau) are N/A** — never compute a yield trend or plateau from missing data; a plan whose instruction counts cycle_check cannot read must never draw `ESCALATE:yield-rising`/`ESCALATE:plateau`.
>
> **Degenerate inputs (Gap i / Q3 table) — implement each:** zero-walk (walk-0-only) → `CONTINUE`; multiple DC blocks → `ESCALATE:unparseable`; all-unparseable lens lines → `ESCALATE:unparseable`; mixed parseable/unparseable → `CONTINUE` (fail closed on the unparseable portion — cannot BAR_MET); partial mid-cycle (Closing/STATUS absent) → normal, absent lines are NOT a defect.
>
> **Partial live-block (Gap h).** Do NOT require `**Closing:**`/`**STATUS:**`/`**§5 Conformance:**` — they exist only in closed blocks. Parse whatever is present; missing data → N/A. If `**Closing:**` IS present (block claims closed), the anti-fabrication cross-check (decision step 8) verifies the claim holds — `ESCALATE:claimed-close-unmet` if it does not.
>
> **Tests — `tests/test_cycle_check.py` (fixtures under `tests/fixtures/`).** Cover every decision-function branch and every degenerate row with synthetic fixtures: unparseable (0/multi block), each assert-fail, restructuring-fold, yield-rising, plateau-at-3, BAR_MET (dry + clean), CONTINUE (mid-cycle), N/A class-split (legacy form), zero-walk, mixed parseable/unparseable, uncommitted-walk, **claimed-close-unmet (a `**Closing:**` present but the current walk is NOT dry — the fabricated-close guard)**. Assert both the stdout verdict AND the exit code.
>
> **DEV discipline:** targeted run only (no full suite in DEV — that is QA/Rule 21). `python3 -m pytest tests/test_cycle_check.py -q 2>&1 | cat` — all pass. Commit `feat(bellows): cycle_check.py drafting-cycle validator (CONTINUE/BAR_MET/ESCALATE) [<id>]`. Deposit a dev log with the reuse-surface verification and the decision-function truth table.
>
> **Deposits:**
> - `scripts/cycle_check.py`
> - `tests/test_cycle_check.py`
> - `knowledge/development/cycle-check-2026-08-19.md`
>
> End with an Output Receipt recording Status AND the DEV commit sha (QA reads it). Standard prompt-feedback protocol.

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> **Identity:** You are QA for `scripts/cycle_check.py`. Verify against the diagnostic-460 contract. Evidence is RAW command output, never summaries.
>
> **(1) Targeted suite passes + covers every branch.** `python3 -m pytest tests/test_cycle_check.py -v 2>&1 | cat` → evidence `knowledge/qa/evidence/executable-cycle-check-2026-08-19/test_cycle_check.txt`. Confirm a test exists for EACH decision-function branch and degenerate row (unparseable, each assert-fail, restructuring-fold, yield-rising, plateau, BAR_MET, CONTINUE, N/A-class-split, zero-walk, mixed, uncommitted-walk, claimed-close-unmet). Name any branch lacking a test.
>
> **(2) LIVE CANARY — run cycle_check.py against REAL Done/ blocks (the load-bearing guard; synthetic fixtures inherit the author's wrong model).** Run the built script against actual plans and assert the expected verdict, capturing raw stdout+exit to `.../live_canary.txt`:
> - `diagnostic-429.md` (per-lens class-split, all 5 lenses; closed cycle; declares a **cross-repo** `**Walk register:**` into `governance/` → assert #2 N/A per rule (a), NOT assert-fail) — assert #1 runs (arithmetic), verdict is a clean terminal (`BAR_MET` on its closing walk or `CONTINUE`, NOT an ESCALATE/crash).
> - `executable-286.md` (legacy bare-count form, no class split) — assert #1 N/A silently; NO false FAIL/ESCALATE from the absent split.
> - `diagnostic-460.md` (this arc's own plan — carries `**Walk N STATUS:**` per-walk lines, the live-format variant absent from older Done blocks) — parses without `unparseable`.
> - a crafted **multiple-`## Drafting Cycle`** input (temp file) → `ESCALATE:unparseable`, exit 1.
> **Any crash, traceback, or false verdict on real input is a FAIL** — this is exactly the real-format gap unit tests miss. Record raw output for each.
>
> **(3) Full suite — Rule 21.** `python3 -m pytest tests/ -q -rf 2>&1 | cat` → evidence `.../full_suite.txt`. Extract FAILED node-ids (`grep -F 'FAILED ' <out> | awk '{print $2}'`); assert the set is empty (bellows baseline is green — any failure is a regression). Record raw tail + node-id set.
>
> **(4) plan_lint check (f) untouched.** Confirm `scripts/plan_lint.py` is unmodified by this plan (`git diff --stat` shows no `plan_lint.py`) — check (f) is superseded, NOT removed (census Q4).
>
> **(5) Rule 20 self-check** — run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with `plan_slug: executable-cycle-check-2026-08-19`, the qa report path, the evidence dir, and `required_evidence_files: ["test_cycle_check.txt", "live_canary.txt", "full_suite.txt"]`. The block prints the banner `Rule 20 — QA Self-Check Results` and, on success, a line beginning `PASSED — SELF-CHECK PASSED` (both verbatim, em-dashes — the gate byte-matches); include the literal stdout under a heading containing "verification". If it prints `FAILED — SELF-CHECK FAILED`, halt. `qa_test_result` gate: `full_suite.txt` and `test_cycle_check.txt` are named in Deposits proactively (plan-452 lesson — a bare evidence-dir fails the gate on a green suite).
>
> **Deposits:**
> - `knowledge/qa/2026-08-19-cycle-check-qa.md`
> - `knowledge/qa/evidence/executable-cycle-check-2026-08-19/`
> - `knowledge/qa/evidence/executable-cycle-check-2026-08-19/test_cycle_check.txt`
> - `knowledge/qa/evidence/executable-cycle-check-2026-08-19/live_canary.txt`
> - `knowledge/qa/evidence/executable-cycle-check-2026-08-19/full_suite.txt`
>
> End with an Output Receipt (Status). Standard prompt-feedback protocol.
