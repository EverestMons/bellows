# bellows — diagnostic: plan_lint check-(f) reads last-lens-line, not the final-walk class split (honing Finding-6, unit c)
**Date:** 2026-08-21 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; produces a design doc, edits no code) | **Execution:** Step 1 (READ-ONLY DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

**Unit (c)** of the drafting-cycle honing backlog ([[drafting-cycle-honing-routing-arc]]) — the ONLY remaining honing proposal, and the only one that is CODE not governance-prose. This is the diagnostic-first half ([[diagnostic-first-change-workflow]]): characterize + design + enumerate the test matrix, THEN a separate executable builds the `plan_lint.py` change from this doc (T-7).

**The bug (honing notes 2026-08-18 Finding 6, confirmed against live code):** `bellows/scripts/plan_lint.py` check-(f) (L365-388) finds the **last lens result line** before `**Closing:**` (`last_lens_line`, L371-374) and WARNs iff that ONE line has `fold` and not `dry`. But §2's bar (`DRAFTING_CYCLE.md` §2, L42/L46) is a **class test over the WHOLE walk** — zero INSTRUCTION-class findings. Because lens lines list in fixed order (Weak-spots → Destruction → Vulnerabilities → Integration → ACID), the "last line" is always ACID's — and ACID/Integration go dry FIRST as a cycle converges, while Weak-spots/Vulnerabilities keep folding. So an instruction fold on the final walk in a non-ACID lens, with a dry ACID line, reads as **false-clean** — and the false-clean rate RISES exactly as the cycle nears the bar (when a Planner is most inclined to close on it).

**Preliminary census (Planner, inline — the diagnostic CONFIRMS + extends this):** 50 Done/ plans carry a `## Drafting Cycle` block; **16** use the modern class-split per-lens form (`w1 1 folded — instruction 1 / record 0; w2 dry`), **1** uses the legacy arrow form (`w1 → v1: 2 folded (...)` — NO class split), 0 use both, ~33 use neither (dry-only / compact / T0). Judged-stop forms (`instruction 0 / record N` on the final walk — a LEGITIMATE close) exist and must NOT warn.

**⚠️ Parse traps the design MUST resolve (this is why a diagnostic, not a straight fix — the cold scout proved the v0 spec would false-WARN on 44% of the class-split corpus without these):**
- **⚠️⚠️ INTRA-LINE per-walk SEGMENTATION (the load-bearing one — 7 of 16 class-split plans).** A single lens line carries ALL walks: `Weak spots: w1 2 folded — instruction 2 / record 0; w2 2 folded — instruction 2 / record 0; w3 1 folded …; w5 dry.` (diagnostic-478, executable-392/464/476/481/483/482). The final walk is the MAX-wN SEGMENT (`w5 dry` — converged); a per-LINE instruction-SUM would add w1+w2+w3's instruction folds and false-WARN on a correctly-closed plan. The check must (i) strip parentheticals, (ii) split the line into per-walk segments, (iii) select ONLY the max-wN segment, (iv) sum instruction in THAT segment. **Prior art to REUSE, not re-derive:** executable-464 already solved per-pass segmentation for `cycle_check` — its regex `instruction\s+(\d+)\s*/\s*record\s+(\d+)` and its rule "the class split binds to the immediately-preceding `N folded` pass; current walk = highest-numbered w" (464:26/58). ([[reuse-this-helper-is-a-clone-decision]] — diff against 464's parser.)
- **Segment delimiter is `;` OR `. ` (period-space before a `wN`), not just `;`** — executable-464 uses `w2 dry. w3 dry. w4 dry. w5 dry. w6 1 folded …`. Split on a `wN` at a clause boundary, having stripped parentheticals first (parens contain both `.` and `;`).
- **Annotation tokens vs walk markers.** `w1 1 folded — instruction 0 / record 1 (W1 = SC-MED: … L46 → …)`. The `(W1 = …` annotation contains `W1`; a naive `[wW]\d` regex mis-reads it as a walk. Strip parentheticals first; anchor walk markers to lowercase `w` at segment boundaries.
- **Collapsed multi-lens line** (executable-488, newest — spreading): `- Weak spots / Destruction / Vulnerabilities / ACID: w2 dry.` — one status shared by 4 lenses. Benign when dry (can't false-warn); the spec must name it (a folded shared status would need fan-out).
- **Final-walk identification** = max `wN` across ALL lens lines (not per-line): a lens dry early (`ACID: w1 1 folded; w2 dry`) still contributes its `w2` segment when the plan's max is 2.
- **Backward-compat (load-bearing).** The 34 non-class-split plans (legacy arrow + dry-only + compact) have NO `instruction N`. The fix MUST fall back to the CURRENT lenient last-lens heuristic for them — PREFER class-split-when-present, never a wholesale replacement. The full `test_lint_cycle_*` suite (**13** `"fold as last event"` must-stay-silent + **19** `"dry lens pass"` must-fire assertions) stays green.

**Deliverable:** a design doc `knowledge/research/plan-lint-check-f-class-split-design-2026-08-21.md` carrying (1) the confirmed census, (2) a CONSTRUCTED failing case run through the live check (proof the false-clean is real, not asserted), (3) the parse SPEC for the fix, (4) a Rule-27 gap table (file:line), (5) the executable's test matrix. NO code edit — read-only.

## Drafting Cycle
**Tier:** T1 — triggers: T-6-adjacent (authorizes a downstream GATE-behavior change) but the diagnostic itself is read-only single-step. Cold scout at Planner's call (T1). cycle_check from walk 2 (scratchpad → register N/A).
**Walk 0 (context pin) — REAL (2026-08-21):**
1. Newest same-class (diagnostic that designs a plan_lint change): the check-(f) code lives at `plan_lint.py:365-388`; existing tests at `tests/test_plan_lint.py:373+` — **13** `"fold as last event"` (must-stay-silent) + **19** `"dry lens pass"` (must-fire) assertions (the full regression surface, per the cold scout).
2. The deliverable is a NEW research doc (no anchor replacement) → additive; no pre-edit sha of a code file (read-only).
3. Census counts (Planner-inline, to be CONFIRMED by the diagnostic agent): 50 DC plans / 16 class-split / 1 legacy-arrow / judged-stop exists.
4. Last writer of check-(f): the 189-era plan_lint drafting-cycle check (legacy-lenient-by-design, per the `test_plan_lint.py:593-594` fixture's own diagnostic).
5. Read-only: no mutation, no sha pin needed; the diagnostic edits nothing.
- Cold scout (T1, §2.0): **RUN (walk 1)** — fresh-context, author-verified. Verdict: **ANGLE RIGHT, but a FORCING GAP in the v0 parse spec** — folded, not a re-draft (the diagnostic's JOB is to produce the spec; v0's was incomplete).
**Direction verdict (after walk 1): PROCEED.** The diagnostic's angle (characterize + design the check-(f) fix + test matrix) is right; the v0 spec's incompleteness is exactly what the diagnostic exists to close, and it is now folded. No clone-origin/mechanism/premise invalidated.
**Walk 1 — cold scout + warm diagnostic-lenses, folds applied:**
- Weak spots (1.4):   w1 2 folded — instruction 2 (SC-HIGH-1: v0 spec omitted INTRA-LINE per-walk segmentation → a per-line instruction-sum false-WARNs on 7/16 class-split plans whose earlier walks folded but final walk converged; SC-HIGH-2: segment delimiter is `;` OR `. `, not just `;` — both folded into STEP §3 (b)/(c) with the max-wN-segment rule).
- Destruction (2.4):  w1 1 folded — instruction 1 (the downstream executable this authorizes is a GATE-behavior change; a naive fix would REGRESS 7 correctly-converged plans clean→false-WARN → added the (v) multi-segment regression row to the test matrix so the executable's QA catches it).
- Vulnerabilities:    w1 1 folded — instruction 1 (SC-LOW-1: cite + REUSE executable-464's per-pass parser (`instruction\s+(\d+)\s*/\s*record\s+(\d+)`, "current walk = highest-numbered w") rather than re-derive; [[reuse-this-helper-is-a-clone-decision]]).
- Integration-record: w1 1 folded — instruction 1 (SC-LOW-2: assertion count is 13 fold-as-last-event silent + 19 dry-lens-pass fire, not "8" → corrected in Context, §5, and the walk-0 pin; the collapsed multi-lens line (488) named in §3(e)).
- ACID:               w1 dry — the folded spec is internally consistent (segmentation + fallback + WARN-first cohere; the (v) regression row is the inverse of the (i) false-clean row).
**Walk 1 STATUS:** 5 folded — instruction 5 / record 0 — not dry (all in the parse spec + test matrix, the diagnostic's core deliverable — SC caught a forcing spec gap the warm read missed).
**Walk 2 — warm re-walk over the folded spec (all diagnostic lenses):**
- Weak spots / Destruction / Vulnerabilities / ACID: w2 dry.
- Integration-record: w2 dry — spec↔matrix coherent: the max-wN-segment rule (§3 b/c) is the exact inverse of the (v) multi-segment regression row; the 464 reuse-cite, the fallback (§3 f), and WARN-first (§3 g) mutually consistent; assertion counts (13/19) consistent across Context, §5, and the walk-0 pin.
**Walk 2 STATUS:** **DRY — 0 folded. §2 BAR MET at walk 2** (instruction-dry; the walk-1 folds closed the forcing spec gap). cycle_check (dogfood): **BAR_MET** (confirmed after recording walk 2).
**Cold read:** the walk-1 cold SCOUT served as this T1 diagnostic's cold read (panel is Planner's-call on T1; the scout caught the forcing segmentation gap — the highest-value cold finding — and it is folded). The downstream EXECUTABLE (which builds the code from this doc) will run its OWN full drafting cycle + FULL cold panel + pytest QA — that is where the CODE correctness is verified.
**Closing:** 2 warm walks (bar met walk 2, instruction-dry) + walk-0 cold scout (caught the forcing spec gap, folded); cycle done — deposit exactly once. ⚠️ Read-only diagnostic (produces a design doc, edits no code); the daemon dispatches a read-only agent to write the doc. Authorizes the unit-(c) executable next.

---
---

## STEP 1 — READ-ONLY DIAGNOSTIC (census + parse design + test matrix)

---

> **Identity:** You are a READ-ONLY diagnostic agent. You produce ONE design doc and edit NO code. Read `bellows/scripts/plan_lint.py` check-(f) (L365-388) and `DRAFTING_CYCLE.md` §2 (the bar) + §3 (the per-lens Cycle Log form) FIRST. Then write `bellows/knowledge/research/plan-lint-check-f-class-split-design-2026-08-21.md`.
>
> **Read-only contract:** no edit to any `.py`, no edit to any live doctrine file, no `git add/commit`, DB reads only via `sqlite3 -readonly`. Your ONLY write is the research doc under `knowledge/research/`.
>
> **The doc must contain, each section EVIDENCE-BACKED (command + output, not assertion):**
> 1. **CONFIRMED census.** Recompute across `knowledge/decisions/Done/*.md`: how many carry a `## Drafting Cycle` block; how many use the class-split form (`^- <Lens>.*instruction [0-9]`); how many the legacy arrow form (`→ v[0-9]`); how many neither. Report the exact counts + name 2-3 example files per class. (Planner's inline estimate: 50 / 16 / 1 / 33 — confirm or correct.)
> 2. **CONSTRUCTED failing case, RUN through the live check.** Build a minimal `## Drafting Cycle` block whose FINAL walk has an INSTRUCTION fold in a non-ACID lens (e.g. `Weak spots: w2 1 folded — instruction 1 / record 0`) and a DRY ACID last line (`ACID: w1 1 folded; w2 dry`), plus a `**Closing:**` line. Run `python3 scripts/plan_lint.py <that file>` and SHOW that it emits NO "fold as last event" WARN — proving the false-clean empirically. Then build the JUDGED-STOP counter-case (final walk `instruction 0 / record 3`) which must STAY silent under the fixed check.
> 3. **Parse SPEC for the fix — specify precisely, and REUSE executable-464's `cycle_check` per-pass parser rather than re-deriving (464:26/58, regex `instruction\s+(\d+)\s*/\s*record\s+(\d+)`, "current walk = highest-numbered w"):**
>    - (a) **Strip parenthetical annotations** from each lens line first, so `(W1 = …)` / `(D1: …)` cannot be mis-read as walk markers or contribute stray `instruction N`.
>    - (b) **Segment each lens line into per-walk pieces** — split on a `wN` token appearing at a clause boundary (`;` OR sentence `. ` OR line start), NOT a fixed delimiter (executable-464 uses `. `; others use `;`). Each segment binds a `wN` to its `instruction N / record N` (or `dry`).
>    - (c) **Final walk = max `wN` across ALL lens lines.** For each lens, select ONLY its max-wN segment (a lens with no segment at that walk contributes nothing).
>    - (d) **Sum INSTRUCTION-class folds across the final-walk segments only.** WARN condition = that sum > 0. ⚠️ A per-LINE sum (ignoring segmentation) FALSE-WARNs on the 7 single-line-multi-walk plans whose earlier walks folded but final walk converged — the forcing bug the cold scout caught; the segmentation in (b)/(c) is what prevents it.
>    - (e) **Collapsed multi-lens line** (`- Weak spots / Destruction / … : w2 dry.`): treat the shared status as applying to each named lens; when dry it contributes 0 (benign) — name the handling explicitly.
>    - (f) **FALLBACK (backward-compat):** when NO lens line carries an `instruction N` token (legacy-arrow / dry-only / compact / T0), keep the CURRENT last-lens heuristic UNCHANGED. PREFER class-split-when-present; never replace wholesale.
>    - (g) **Posture:** stays WARN-first (no FAIL upgrade) — a judged stop is a NORMAL close (§2), so a FAIL would block legitimate closes; §4 is warn-first by design.
> 4. **Rule-27 gap table** (file:line): every site the executable touches — `plan_lint.py:365-388` (the check), `tests/test_plan_lint.py` (new + existing cases), and confirm NO other consumer reads check-(f)'s output shape.
> 5. **Test matrix for the executable** (each row: input shape → expected check output):
>    - (i) constructed false-clean: final walk has instruction fold in a non-ACID lens + dry ACID last line → now WARNs.
>    - (ii) judged-stop: final walk `instruction 0 / record 3` → SILENT.
>    - (iii) legacy-arrow format (`→ vN`) → SILENT (fallback unchanged).
>    - (iv) dry-only / compact / T0 → SILENT.
>    - (v) **⚠️ multi-segment REGRESSION (the inverse failure — real plans 478/464/392/476/481/483/482):** single-line-multi-walk with EARLIER-walk instruction folds but final-walk `dry` or `instruction 0` → SILENT (proves the fix does NOT regress correctly-converged plans clean→false-WARN). This is the row the segmentation gap makes essential.
>    - (vi) **the FULL existing suite stays green** — the `test_lint_cycle_*` cases: **13** `"fold as last event"` must-stay-silent assertions + **19** `"dry lens pass"` must-fire assertions (run the whole suite; do NOT cherry-pick a named subset — the count is 13+19, not 8).
>
> **Deposits:**
> - `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/plan-lint-check-f-class-split-design-2026-08-21.md`
