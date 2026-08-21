# bellows — check-(f) corrective: final-walk detection must read **Walk N** headers, not just wN-on-lens-lines (honing unit c fix)
**Date:** 2026-08-21 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (DEV) + full suite + corpus scan (QA) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

## Context

**Corrective for exec-490** ([[bellows-verdict-grammar-no-redo]]: stop + corrected re-deposit). exec-490 shipped the check-(f) class-split parse (honing unit c) — 133 unit tests green — but its own **corpus-regression scan caught a real defect**: the fixed check FALSE-WARNs on 2 shipped plans (`diagnostic-429`, `executable-430`). exec-490 was STOPPED; its DEV commit `0dbdcd1` is on main (WARN-only, non-blocking). This plan repairs it forward.

**Root cause (Planner-verified):** both plans express their FINAL walk (walk 2, dry) as a `wN`-LESS combined line under a `**Walk 2 … DRY**` header — e.g. `- Weak spots: dry. — Destruction: dry. …` with no `w2` token. The current check computes `max_walk` ONLY from `\bw\d\b` tokens on lens lines → sees max_walk=1 → sums walk-1's instruction folds → WARNs. The real final walk (2) is dry. A format diag-489's census never checked ([[live-canary-catches-real-format-gaps]] — the 133 constructed tests inherited the same blind spot as the code; only the live-corpus scan caught it).

**The fix (Planner-VERIFIED against the WHOLE Done/ corpus before authoring — 0 false-WARN, still catches the constructed false-clean, judged-stop stays silent):** two additions to the existing class-split path in check-(f):
1. **`max_walk` also reads `**Walk N**` section headers** across the whole DC block, not just `\bw\d\b` on lens lines. Regex: `\*\*Walk\s+(\d+)\b` — take the max over BOTH sources. (For 429/430, the `**Walk 2 …**` header sets max_walk=2; no lens line has a `w2` segment → instruction_sum 0 → SILENT.)
2. **A `**Walk {max_walk} STATUS:** … instruction K` line is authoritative when present** — regex `\*\*Walk\s+(\d+)\s+STATUS:\*\*.*?instruction\s+(\d+)` (matching `max_walk`); use K directly and WARN iff K>0, else fall through to the per-lens-segment sum. (Handles a final walk whose class info is only in the STATUS aggregate, not per-lens — the inverse gap.)
Everything else in exec-490's check-(f) stays: parens stripped, `;` + `. `-before-wN segmentation, per-lens final-walk instruction sum, the conservative +1 for a fold-without-class-split, the fallback to the last-lens heuristic when NO `instruction N` anywhere, verbatim WARN message, WARN-first exit 0.

**⚠️ QA-plumbing lessons from exec-490's FAILED QA step (do not repeat):** (a) `mkdir -p` the evidence dir BEFORE the `>` redirect (a redirect into a missing dir fails rc=1, suite never runs); (b) write the QA report `.md` carrying the byte-exact `Rule 20 — QA Self-Check Results` banner (the `rule_20_self_check` gate needs a `.md` deposit — [[rule-20-form-by-plan-class]]); (c) COMMIT the evidence + report (exec-490's evidence was uncommitted → lost at teardown); (d) the corpus scan must cover the WHOLE `Done/` corpus (that is what caught this).

**Scope:** `scripts/plan_lint.py` (check-(f) class-split path only) + `tests/test_plan_lint.py` (+1 test for the 429/430 format). Worktree-isolated bellows DEV/QA.

## Drafting Cycle
**Tier:** T1 — a targeted corrective to a WARN-gate whose FIX is already corpus-verified (the residual risk is the QA plumbing, known from exec-490). Cold scout on the QA plumbing + fix faithfulness. cycle_check from walk 2.
**Walk 0 (context pin) — REAL (2026-08-21):**
1. Newest same-class: exec-490 (`0dbdcd1`, the check-(f) parse this corrects); the broken `max_walk` block at `plan_lint.py` ~L384 (`_walk_token_re.finditer` only).
2. Fix VERIFIED via `/tmp/probe_fix.py` against the full corpus: 0 false-WARN, false-clean still WARNs, judged-stop silent. The corrective implements that verified logic.
3. The 2 canary plans: `diagnostic-429`, `executable-430` — final dry walk as a `wN`-less line under a `**Walk 2 … DRY**` header.
4. Worktree isolation; no in-place sha pin.
5. ⚠️ A concurrent terminal (plan 491) also touches check-(f) design — CEO said proceed; if a claim-time snapshot conflict arises, re-dispatch ([[bellows-serves-claim-time-pristine-snapshot]]).
- Cold scout (T1, §2.0): **RUN (walk 1)** — fresh-context, author-verified. Verdict: **SOUND, no forcing problem, 0 HIGH.** Independently swept the whole Done/ corpus: the header regex matches 429/430's `**Walk 2 (…DRY):**` → max_walk 1→2 → instruction_sum 7/8→0 → silent; ONLY 429/430 have header_max>lens_max (no third unhandled format); STATUS branch live on 13 plans with no verdict flip; all 4 QA gates satisfiable; exactly 2 corpus flips (429/430), zero new false-WARN or false-clean.
**Direction verdict (after walk 1): PROCEED.** The fix is corpus-verified (Planner prototype) AND cold-scout-confirmed; the corrective's angle is right.
**Walk 1 — cold scout + warm lenses:**
- Weak spots:         w1 1 folded — instruction 1 (WARM: the STATUS-line regex hint carried a nonsense flag `re.I|re.DOTALL-not-needed` → corrected to `re.I` with the no-DOTALL rationale; a copy-literal syntax error avoided).
- Destruction/Vulnerabilities/Integration/ACID: w1 dry — scout confirmed no regression (133 pass, 2 intended flips only), no new false-clean, QA plumbing satisfies all 4 gates exec-490 failed, scope bounded to the class-split branch.
**Walk 1 STATUS:** 1 folded — instruction 1 / record 0 — not dry.
**Walk 2 — confirming read:** w2 dry — the fix logic is doubly verified (prototype + scout corpus sweep); STEP-2 plumbing consistent (mkdir → redirect → corpus scan → Rule 20 report → commit both). Instruction-yield 1→0.
**Walk 2 STATUS:** DRY — 0 folded. §2 BAR MET at walk 2.
**Cold read:** the walk-1 cold scout served as the cold read (T1) and independently corpus-verified the fix — the CODE is further verified by STEP 2's QA gate (full 134-suite + whole-corpus scan asserting 429/430 now silent).
**Closing:** 2 warm walks (bar met walk 2; yield 1→0) + walk-0 cold scout (corpus-verified the fix, 0 HIGH); the fix was Planner-prototyped against the full corpus BEFORE authoring (0 false-WARN); cycle done — deposit exactly once. Corrective for exec-490.

---
---

## STEP 1 — DEV: header/STATUS-aware max_walk + the 429/430 test

---

> **Identity:** You edit `scripts/plan_lint.py` (the check-(f) CLASS-SPLIT path only) and add 1 test to `tests/test_plan_lint.py`, in the bellows worktree. The check-(f) class-split path already exists (from exec-490); you AUGMENT its `max_walk` computation — do not rewrite the whole check.
>
> **Implement (the Planner-verified fix):**
> - In the class-split branch, AFTER computing `max_walk` from `\bw(\d+)\b` tokens on lens lines, ALSO scan the WHOLE `dc_block` for `**Walk N**` headers (`re.compile(r'\*\*Walk\s+(\d+)\b')`) and raise `max_walk` to the overall max. This makes a final dry walk expressed as a header + `wN`-less line (diagnostic-429 / executable-430) set `max_walk` correctly → no lens segment at that walk → `instruction_sum` 0 → no WARN.
> - BEFORE the per-lens segment sum, check for an authoritative `**Walk {max_walk} STATUS:** … instruction K` line (`re.compile(r'\*\*Walk\s+(\d+)\s+STATUS:\*\*.*?instruction\s+(\d+)', re.I)` — no DOTALL, STATUS and its instruction count are on one line); if one matches `max_walk`, WARN iff K>0 and SKIP the per-lens sum; else do the existing per-lens sum. Keep everything else (parens strip, `;`+`. ` segmentation, conservative +1, fallback, verbatim message, WARN-first) UNCHANGED. Do NOT touch the fallback branch, the no-Closing WARN, or checks (g)/(h).
> - **Targeted test** ([[dev-step-no-full-suite]]): add `test_lint_cycle_classsplit_final_dry_walk_headered_silent` — a block with walk-1 instruction folds on lens lines AND a `**Walk 2 (… DRY):**` header + a `wN`-less combined dry line (mirroring diagnostic-429) + a dry `**Closing:**`; assert `"fold as last event" not in result.stdout.lower()`. Run `python3 -m pytest tests/test_plan_lint.py -k cycle -q` — assert the 27 existing cycle tests + your 1 new = 28 all pass; paste the raw tail.
> - Commit both files in the worktree: `fix(plan_lint): check-(f) max_walk reads **Walk N** headers — no false-WARN on headered final-dry walks (honing unit c corrective) [<id>]`.
>
> **Deposits:**
> - `scripts/plan_lint.py` (check-(f) max_walk augmentation)
> - `tests/test_plan_lint.py` (+1 test: headered final-dry-walk)

---

## STEP 2 — QA: full suite + WHOLE-corpus scan (0 false-WARN) + Rule 20

---

> **Identity:** You VERIFY against the committed DEV HEAD; you write ONLY the QA report `.md` + the evidence `.txt`, and you COMMIT them.
>
> **1. Create the evidence dir FIRST** (a `>` into a missing dir fails rc=1 — exec-490's failure): `mkdir -p knowledge/qa/evidence/check-f-final-walk-fix-2026-08-21`
>
> **2. Run + capture RAW** ([[qa-evidence-raw-output]]):
> - `python3 -m pytest tests/test_plan_lint.py -q > knowledge/qa/evidence/check-f-final-walk-fix-2026-08-21/pytest_full.txt 2>&1` — assert ALL pass (133 prior + 1 new = **134**; 0 failures). Named `pytest_full.txt` = the `qa_test_result` gate evidence ([[qa-test-result-gate-needs-named-txt]]).
> - **WHOLE-corpus regression scan (the guard that caught the exec-490 defect — run over EVERY Done/ plan, no sampling):** append to the evidence file —
>   `for f in knowledge/decisions/Done/*.md; do grep -ql 'instruction [0-9]' "$f" 2>/dev/null && out=$(python3 scripts/plan_lint.py "$f" 2>&1) && echo "$out" | grep -qi 'fold as last event' && echo "FALSE-WARN: $f"; done; echo "corpus-regression scan complete"`
>   Assert ZERO `FALSE-WARN:` lines — INCLUDING diagnostic-429 and executable-430 (the exec-490 canaries, which must now be SILENT). If any `FALSE-WARN:` appears, HALT and report — the fix is incomplete.
> - Spot-verify the new `test_lint_cycle_classsplit_final_dry_walk_headered_silent` PASSED.
>
> **3. Rule 20 self-check** (MANDATORY on every QA step — [[rule-20-form-by-plan-class]], simple-banner form): run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Values: `plan_slug`=`check-f-final-walk-header-fix-2026-08-21`; `qa_report_path`=the report below; `evidence_dir`=`knowledge/qa/evidence/check-f-final-walk-fix-2026-08-21`; `required_evidence_files`=`[pytest_full.txt]`. Include the block's literal stdout in the report. If `FAILED`, HALT.
>
> **4. Write + COMMIT the QA report** `knowledge/qa/check-f-final-walk-fix-qa-2026-08-21.md` carrying: the byte-exact `Rule 20 — QA Self-Check Results` banner, the self-check stdout (PASSED line), the full-suite result (134/0), and the corpus-scan result (0 FALSE-WARN, 429/430 now silent). ⚠️ **COMMIT both the report and pytest_full.txt** (exec-490's evidence was uncommitted → lost at teardown → gate FAIL): `git add knowledge/qa/check-f-final-walk-fix-qa-2026-08-21.md knowledge/qa/evidence/check-f-final-walk-fix-2026-08-21/pytest_full.txt && git commit -m "qa(plan_lint): check-(f) final-walk header fix — 134 green, corpus clean [<id>]"`.
>
> **Deposits:**
> - `knowledge/qa/check-f-final-walk-fix-qa-2026-08-21.md` (QA report — Rule 20 banner + PASSED; committed)
> - `knowledge/qa/evidence/check-f-final-walk-fix-2026-08-21/pytest_full.txt` (raw full-suite + corpus-scan output; committed)
