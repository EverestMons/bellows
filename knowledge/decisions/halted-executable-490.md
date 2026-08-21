# bellows — plan_lint check-(f): read the final-walk class split, not the last lens line (honing unit c executable)
**Date:** 2026-08-21 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (DEV) + full suite (QA) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

## Context

**Unit (c) executable** — the FINAL honing proposal ([[drafting-cycle-honing-routing-arc]]) and the only CODE change of the arc. Builds the `plan_lint.py` check-(f) fix from the banked design **diag-489** (`knowledge/research/plan-lint-check-f-class-split-design-2026-08-21.md`, T-7 — implement its spec, do NOT re-derive).

**The bug (diag-489 §1-2, confirmed empirically):** `scripts/plan_lint.py` check-(f) (L365-388) reads only the LAST lens result line before `**Closing:**`. Since lenses list Weak→Destruction→Vuln→Integration→ACID and ACID/Integration converge FIRST, the last line is ACID's — so an INSTRUCTION fold on the final walk in an earlier lens with a dry ACID line reads **false-clean**, and the false-clean rate RISES as a cycle nears the bar. (Diag-489 also found the inverse: the current check false-WARNs on record-only judged stops.)

**The fix (diag-489 §3, spec is authoritative):**
- **Class-split path (PREFERRED when any lens line carries an `instruction N` token):** for each lens line, parse per-walk segments; find the FINAL walk = max `wN` across ALL lens lines; sum INSTRUCTION-class folds across each lens's final-walk segment ONLY; WARN iff that sum > 0.
- **⚠️ The load-bearing subtlety (diag-489 §3 b/c/d — the cold-scout catch):** segment per-walk and sum ONLY the max-wN segment. A per-LINE instruction sum FALSE-WARNs on the 7 single-line-multi-walk plans (diagnostic-478/482, executable-392/464/476/481/483) whose earlier walks folded but final walk converged. Segment on a `wN` token at a clause boundary (`;` OR `. ` OR line-start), parentheticals stripped first.
- **REUSE, do not re-derive ([[reuse-this-helper-is-a-clone-decision]]):** `scripts/cycle_check.py` already solves per-pass segmentation — `extract_per_pass_metadata` (L60-88), `CLASS_SPLIT_RE` (L24 = `instruction\s+(\d+)\s*/\s*record\s+(\d+)`), `WALK_NUM_RE` (L28), and `cycle_yields.parse_lens_line` (L183, the fuller parser that also captures DRY passes — needed because the max walk may be a dry pass like `w5 dry`). DEV chooses import-vs-mirror; if importing across `scripts/`, keep plan_lint's gate robustness (no heavy new deps) — the cold panel vets this.
- **Fallback (backward-compat, load-bearing):** when NO lens line carries `instruction N` (legacy-arrow `executable-277` / dry-only / compact / T0 — 34 plans), keep the CURRENT last-lens heuristic UNCHANGED.
- **Retain the WARN message string verbatim** (`"WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)"`) — existing tests match on `"fold"` / `"dry lens pass"` substrings.
- **WARN-first, exit 0** (no FAIL upgrade — a judged stop is a normal close, §2/§4).

**Test matrix (diag-489 §5) — add each as a `test_lint_cycle_*` function (house style: `_run_lint(plan_text)` + stdout-substring asserts):**
- (i) false-clean: final walk instruction fold in a non-ACID lens + dry ACID → **now WARNs**.
- (ii) judged-stop: final walk `instruction 0 / record N` → **SILENT** (fixes the current false-WARN).
- (iii) legacy-arrow (`→ vN`, no class split) → **SILENT** (fallback).
- (iv) dry-only / compact → **SILENT** (fallback).
- (v) **multi-segment REGRESSION** (`Weak spots: w1 2 folded — instruction 2 / record 0; w2 …; w5 dry.`) → **SILENT** (final-walk segment w5 dry, sum 0) — proves NO clean→false-WARN regression on the 7 real plans.

**Baseline (measured 2026-08-21):** `pytest tests/test_plan_lint.py -k cycle` = **22 passed**; full `test_plan_lint.py` = 128 tests. QA must keep ALL green + the 5 new rows pass.

**Scope:** `scripts/plan_lint.py` (check-(f) only) + `tests/test_plan_lint.py` (5 new functions). No other file — diag-489's gap table confirmed NO consumer of check-(f)'s output outside plan_lint.py. Worktree-isolated bellows DEV/QA (not governance in-place).

## Drafting Cycle
**Tier:** T1 — code change to a WARN-gate + tests; worktree-isolated. **Panel: FULL cold panel at close** — first CODE plan of the arc, a gate-behavior change; the EXECUTION seat rehearses pytest (the real verification). cycle_check from walk 2 (scratchpad → register N/A).
**Walk 0 (context pin) — REAL (2026-08-21):**
1. Newest same-class (a plan_lint check + tests change): the 189-era drafting-cycle-check plans; the check-(f) code at `plan_lint.py:365-388`; reuse source `cycle_check.py:24/28/60-88` + `cycle_yields.py:183`.
2. Deliverable = code edit (check-(f)) + 5 new test functions; no anchor-replacement (a logic rewrite of the check-(f) block + additive tests).
3. Baseline: 22 cycle tests pass, 128 total (measured); the fix must not drop any.
4. The spec is diag-489 (banked, Done) — T-7 build-from, not re-derived.
5. Worktree isolation (bellows-managed); no sha triple-pin (not in-place).
- Cold scout (T1, §2.0): **RUN (walk 1)** — fresh-context, author-verified. Verdict: **design SOUND, but 2 forcing QA-gate defects** (folded, not a re-draft — the CODE fix + spec fidelity are clean; the defects were STEP-2 gate plumbing).
**Direction verdict (after walk 1): PROCEED.** The angle — build the check-(f) fix from diag-489's spec — is right; the DEV step + spec fidelity are clean (scout confirmed 1:1 with §3/§5), the folds were QA-step gate plumbing. No clone/mechanism/premise invalidated.
**Walk 1 — cold scout + warm lenses, folds applied:**
- Weak spots:         w1 1 folded — instruction 1 (WARM: bound the DEV edit to L365-388 only; the no-Closing WARN L390-391 + checks (g)/(h) must stay untouched — an agent could over-reach on "replace the check-(f) body").
- Destruction:        w1 dry — the fallback preserves the 22 existing cycle tests (scout + baseline confirm); QA verifies the full 133.
- Vulnerabilities:    w1 2 folded — instruction 2 (SC-HIGH-1: STEP 2 had NO Rule 20 `.md` QA-report deposit → `rule_20_self_check` gate pauses with "no QA deposit paths" (gates.py:551-566); SC-HIGH-2: STEP 2's `>` redirect into a non-existent evidence dir fails rc=1 → suite never runs, `qa_test_result` reports evidence-unreadable → added `mkdir -p` + the QA report `.md` with the byte-exact Rule 20 banner via the canonical block).
- Integration-record: w1 dry — import-safety confirmed (cycle_check guarded under `if __name__`, no side effects, no circular import); added the DEV `sys.path.insert(scripts)` note; evidence convention (`<slug>-<date>/pytest_full.txt`) matches precedent (forward-splitter-2026-08-03).
- ACID:               w1 dry — DEV commits → verdict → QA reads HEAD (pause_for_verdict:always); the two-step DEV→QA schedule is sound; qa_steps:2 declared.
**Walk 1 STATUS:** 3 folded — instruction 3 / record 0 — not dry (2 forcing QA-gate defects + 1 edit-scope guard; all in the STEP plumbing, the CODE approach unchanged).
**Walk 2 — warm re-walk (Destruction/Vulnerabilities focus on the real-world blast radius):**
- Destruction/Vulnerabilities: w2 1 folded — instruction 1 (the fix changes a gate ALL class-split plans hit; the unit tests use CONSTRUCTED blocks, so a format variation in the real 16 class-split Done/ plans could false-WARN unseen → added a QA CORPUS-REGRESSION scan: run the fixed check against every real class-split Done/ plan, assert ZERO false-WARNs).
- Weak spots / Integration / ACID: w2 dry — STEP-2 plumbing now consistent (mkdir before redirect; both deposits named; Rule 20 values match the canonical block; corpus scan appends to the same evidence file).
**Walk 2 STATUS:** 1 folded — instruction 1 / record 0 — not dry (the corpus-regression guard; a real-world strengthening the constructed tests could not give).
**Walk 3 — confirming read (all lenses):** w3 dry — structure consistent (2 STEPs, qa_steps:2, both QA-gate fixes present + byte-exact Rule 20 banner + mkdir, deposits reconcile); the DEV spec maps 1:1 to diag-489 §3/§5; no new issue. Instruction-yield 3→1→0.
**Walk 3 STATUS:** **DRY — 0 folded. §2 BAR MET at walk 3.** cycle_check (dogfood): **BAR_MET** (after recording walk 3).
**Cold read:** the walk-1 cold SCOUT served as this T1 code-plan's cold read (panel Planner's-call on T1) — and it caught the two FORCING QA-gate defects (the highest-value findings). ⚠️ **No pre-dispatch EXECUTION panel: the code does not exist until the DEV agent writes it, so there is nothing to rehearse pre-dispatch — the CODE is verified by STEP 2's QA gate (full 133-test suite + the corpus-regression scan over all real class-split plans), which is the real verification.** DEV runs in a worktree; QA reads committed HEAD.
**Closing:** 3 warm walks (bar met walk 3, instruction-dry; yield 3→1→0) + walk-0 cold scout (caught 2 forcing QA-gate defects, folded); the CODE verification is the QA gate (deferred by construction — code written at dispatch); cycle done — deposit exactly once. Worktree-isolated DEV→QA bellows plan.

---
---

## STEP 1 — DEV: implement check-(f) class-split parse + add the 5 test rows

---

> **Identity:** You edit `scripts/plan_lint.py` (check-(f), L365-388) and add 5 test functions to `tests/test_plan_lint.py`, in the bellows worktree. Read diag-489's design doc `knowledge/research/plan-lint-check-f-class-split-design-2026-08-21.md` (§3 parse spec + §5 test matrix) FIRST — implement its spec, do not re-derive. Read the REUSE source `scripts/cycle_check.py` (`extract_per_pass_metadata` L60-88, `CLASS_SPLIT_RE` L24, `WALK_NUM_RE` L28) and `scripts/cycle_yields.py` (`parse_lens_line` L183).
>
> **Implement (diag-489 §3):**
> - Replace the check-(f) body (plan_lint.py L365-388, the `last_lens_line` block through its WARN) with: (1) detect whether the DC block has ANY `instruction N` token; (2) if YES — for each lens line, parse per-walk segments (REUSE cycle_check/cycle_yields per-pass logic — import from the sibling `scripts/` module or mirror the small regex set; if importing risks plan_lint's gate robustness, mirror `CLASS_SPLIT_RE` + the segmentation loop), find the final walk = max `wN` across all lens lines, sum instruction across each lens's final-walk segment, WARN iff sum > 0; (3) if NO `instruction N` — keep the CURRENT last-lens heuristic UNCHANGED (fallback). Handle the collapsed multi-lens line (§3e: shared dry status → 0; note `parse_lens_line` returns None for it, so guard against None). Keep the WARN message string verbatim and exit 0 (WARN-first). ⚠️ **If you IMPORT from cycle_check** (`import cycle_check` is verified side-effect-free — guarded under `if __name__`), `plan_lint.py` puts BELLOWS_ROOT on `sys.path` but NOT `scripts/`, so add `sys.path.insert(0, str(Path(__file__).parent))` before the import (or mirror the regexes to avoid the path dependency). No circular import (cycle_check shells out to plan_lint as a subprocess, never imports it).
> - **Targeted tests only in DEV** ([[dev-step-no-full-suite]]): add 5 `test_lint_cycle_classsplit_*` functions for matrix rows (i)-(v) using `_run_lint(...)` + stdout asserts (`assert "fold as last event" in/not in result.stdout.lower()`). Row (i) asserts WARN present; (ii)/(iii)/(iv)/(v) assert WARN absent. Then run `python3 -m pytest tests/test_plan_lint.py -k cycle -q` and confirm the 22 existing cycle tests + your 5 new ones all pass (27 total). Paste the raw tail.
> - ⚠️ **Bound the edit precisely:** replace ONLY the fold-as-last-event logic (the `last_lens_line` loop + its WARN + the `else` last-resort closing-text branch, plan_lint.py L365-388). The `**Closing:**`-absent WARN (L390-391) and checks (g)/(h) that follow are OUTSIDE this range and must stay UNTOUCHED. Do not alter the `lens_line_re` / `closing_pos` computation that other branches share unless additive.
> - Do NOT run the full suite here (that is STEP 2/QA). Commit both files in the worktree: `test(plan_lint): check-(f) reads final-walk class split not last-lens (honing unit c) [<id>]`.
>
> **Deposits:**
> - `scripts/plan_lint.py` (check-(f) rewrite)
> - `tests/test_plan_lint.py` (+5 test functions)

---

## STEP 2 — QA: full suite green + the matrix behaviors

---

> **Identity:** You VERIFY against the committed DEV HEAD; you write ONLY the QA report `.md` + the evidence `.txt`. Run the full suite, capture RAW output, run the canonical Rule 20 self-check, and write the QA report.
>
> **1. Create the evidence dir FIRST (a `>` redirect into a missing dir fails rc=1 and the suite never runs):**
> - `mkdir -p knowledge/qa/evidence/plan-lint-check-f-2026-08-21`
>
> **2. Run + capture (raw, not summarized — [[qa-evidence-raw-output]]):**
> - `python3 -m pytest tests/test_plan_lint.py -q > knowledge/qa/evidence/plan-lint-check-f-2026-08-21/pytest_full.txt 2>&1` — assert ALL pass (128 prior + 5 new = **133**; 0 failures). The named `pytest_full.txt` is the `qa_test_result` gate's evidence ([[qa-test-result-gate-needs-named-txt]]).
> - `python3 -m pytest tests/test_cycle_check.py -q >> knowledge/qa/evidence/plan-lint-check-f-2026-08-21/pytest_full.txt 2>&1` (append — confirm the reuse source's own suite still green if plan_lint imports from cycle_check).
> - Spot-verify the 5 new `test_lint_cycle_classsplit_*` rows each PASSED (grep the run).
> - **⚠️ CORPUS-REGRESSION check (the real-world guard the constructed tests cannot give):** run the FIXED `plan_lint.py` against ALL real class-split Done/ plans and confirm ZERO false-WARNs — every one is a correctly-converged shipped plan, so any `"fold as last event"` WARN is a regression on a format the unit tests missed. Append to `pytest_full.txt`:
>   `for f in knowledge/decisions/Done/*.md; do grep -ql 'instruction [0-9]' "$f" 2>/dev/null && out=$(python3 scripts/plan_lint.py "$f" 2>&1) && echo "$out" | grep -qi 'fold as last event' && echo "FALSE-WARN: $f"; done; echo "corpus-regression scan complete"`
>   Expect NO `FALSE-WARN:` lines (the ~16 class-split plans all closed correctly). If any appears, it names a real format the fix mishandles — HALT and report, do not fold.
> - ⚠️ Known-benign: none expected (self-contained linter change). Any pre-existing unrelated failure → classify raw, do not fold.
>
> **3. Rule 20 self-check (MANDATORY on every QA step — [[rule-20-form-by-plan-class]], simple-banner form):** Run the canonical Rule 20 self-check from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Values: `plan_slug` = `plan-lint-check-f-class-split-2026-08-21`; `qa_report_path` = the QA report below; `evidence_dir` = `knowledge/qa/evidence/plan-lint-check-f-2026-08-21`; `required_evidence_files` = `[pytest_full.txt]`. Include the block's literal stdout in the QA report. If it prints `FAILED`, HALT.
>
> **4. Write the QA report** `knowledge/qa/plan-lint-check-f-qa-2026-08-21.md` carrying: the byte-exact banner `Rule 20 — QA Self-Check Results`, the self-check stdout (PASSED line), the full-suite result (133 passed / 0 failed), and the 5-row matrix confirmation. This `.md` is what the `rule_20_self_check` gate reads.
>
> **Deposits:**
> - `knowledge/qa/plan-lint-check-f-qa-2026-08-21.md` (QA report — carries the Rule 20 banner + PASSED line; the rule_20_self_check gate evidence)
> - `knowledge/qa/evidence/plan-lint-check-f-2026-08-21/pytest_full.txt` (raw full-suite output — the qa_test_result evidence)
