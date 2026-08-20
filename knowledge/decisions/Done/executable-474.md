# bellows — Cycle Manifest tooling: cycle_check --emit-manifest + plan_lint stanza check (component 2b)
**Date:** 2026-08-19 | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_qa_step

## Context

Component 2b (tooling half) of the cycle-automation arc. Implements two gaps from the diagnostic-472 Rule 27 Gap Assessment — **(e)** a `cycle_check --emit-manifest` mode and **(f)** a `plan_lint` stanza-shape check — per the finalized grammar in `knowledge/research/cycle-manifest-stanza-design-2026-08-19.md` (Q2 grammar + Q4 validator). Rule 27, T-7: build from that spec WITHOUT re-deriving the grammar.

**Explicitly OUT of scope (do NOT touch):** `DRAFTING_CYCLE.md` (the §3 doctrine amendment is component 2a, a separate governance in-place plan — this is tooling only), and the depositor re-run (component 3, gap g). This plan touches ONLY `bellows/scripts/` + `bellows/tests/`.

**Non-disruptive posture:** the plan_lint stanza check validates a `## Cycle Manifest` stanza **IF PRESENT**; it does NOT warn on absence. No current plan carries a stanza yet, and 2a (doctrine) is what will later mandate presence. 2b must not nag stanza-less plans or turn the bellows suite red.

**Ratified/verified facts (do not relitigate):** the 10-field grammar (Q2), stanza placement (after `**Closing:**`, before the `---` separator, inside `## Drafting Cycle`), the trust taxonomy (computed: validation/coherence/walks/yields · authored-verified: reads/writes/class · authored: tier/target/open_forks), and the CEO's Option-A resolution of the yields-vs-§3 fork (kept; doctrine handled in 2a). `--emit-manifest` MUST preserve component 1's strictly-read-only invariant (STDOUT only).

## Drafting Cycle
**Tier:** T1 — triggers: T-7 (implements diagnostic-472's gap table per Rule 27), T-8 (novel). New tooling extending shipped scripts; not a T-5/T-6 doctrine surface (the doctrine is 2a). Real correctness guard is the QA **live canary** (--emit-manifest against real closed plans; the synthetic-fixture-inherits-author's-model lesson). cycle_check dogfooded per walk.
**Walk 0 (context pin):** spec = `knowledge/research/cycle-manifest-stanza-design-2026-08-19.md` (Q2 grammar specimen + edge cases a–e; Q4 Layer-1 validator; Q5 gaps e+f). Targets: `scripts/cycle_check.py` (436 lines, 27 tests — extend, preserve all), `scripts/plan_lint.py` check (f) (~lines 311–391 per the diagnostic — extend). Test siblings `tests/test_cycle_check.py`, `tests/test_plan_lint.py`. Clone-diff: `executable-464` (the cycle_check build — same script+tests class, same read-only discipline). Bellows suite baseline green (Rule 21).
**Direction verdict (after walk 1):** **PROCEED** — the angle (build gaps e+f from the diagnostic-472 grammar, non-disruptive, dogfood-guarded) is sound; no forcing finding.
**Walks:** 4 (bar MET — walk 4 class-dry, no restructuring fold). Instruction yields 4 → 1 → 1 → 0. A merge-path test candidate was weighed at w4 and rejected — adequately covered by the "well-formed stanza for a fixture plan" test + the canary's computed-field checks; folding it would be the "find small work forever" trap the bar bars.
- Weak spots (1.4):     w1 1 folded — instruction 1 / record 0 (W1: the authored-field source is a Planner-prefilled PARTIAL stanza, NOT the plan header — headers carry no reads/writes/class; undeclared → `<declare>` placeholder). w2 dry. w3 1 folded — instruction 1 / record 0 (W2: the I3 `<declare>`-warn behavior (added w2) needs a test — added the `<declare>` placeholder → WARN case to test_plan_lint.py, or the behavior ships untested). w4 dry.
- Destruction (2.4):    w1 1 folded — instruction 1 / record 0 (D1: extending plan_lint check (f) must PRESERVE its existing DC-block validation unchanged — every current plan lints identically; the stanza check is purely additive, or the shared deposit gate breaks). w2 dry. w3 dry. w4 dry.
- Vulnerabilities (3.1): w1 1 folded — instruction 1 / record 0 (V1: --emit-manifest's COMPUTED fields emit N/A when data is unparseable — `yields: N/A`, `coherence: N/A` — matching cycle_check's own discipline; never fabricate a series/count). w2 dry. w3 dry. w4 dry.
- Integration-record:   w1 1 folded — instruction 1 / record 0 (I1: locate plan_lint check (f) by CONTENT, not the cited line numbers — they've drifted (~365–388 vs the diagnostic's ~311–391); editing wrong lines would corrupt the gate). w2 1 folded — instruction 1 / record 0 (I3: the emitter's `<declare>` placeholder must be RECOGNIZED by the plan_lint check — a stanza with `<declare>` is a template, not complete → warn; else `class: <declare>` reaches the depositor and misfires the auto-deposit mapping). w3 dry. w4 dry.
- ACID (5.2):           w1 dry. w2 dry. w3 dry. w4 dry.
**Walk 1 STATUS:** 4 folded — instruction 4 / record 0 — NOT dry.
**cycle_check (dogfood) after walk 1:** initially a FALSE POSITIVE (exit 1) — **the dogfood caught a real bug in shipped cycle_check.py** on its 2nd use. True verdict `CONTINUE`. Cause: `CLOSURE_RE` matched IGNORECASE, so the lowercase word for "cl-osed" in Tier-line prose tripped step-8. **Fixed + shipped (executable-473)**; re-run on the fixed tool → `CONTINUE`.
**Walk 2 STATUS:** 1 folded — instruction 1 / record 0 — NOT dry (yield 4→1, falling; Weak-spots/Destruction/Vulnerabilities/ACID dry).
**cycle_check (dogfood) after walk 2:** `CONTINUE` (exit 0) — agrees (instruction 1, not dry); the fixed tool now runs cleanly on this draft (no false positive).
**Walk 3 STATUS:** 1 folded — instruction 1 / record 0 — NOT dry (yield 4→1→1; a test-coverage fold for the w2 behavior, Weak-spots only).
**cycle_check (dogfood) after walk 3:** `CONTINUE` (exit 0) — agrees; no plateau despite flat 1→1, because Weak-spots (dry at w2) folded this walk (the "previously-dry lens folded" condition resets it).
**Walk 4 STATUS:** 0 folded — full dry walk across all five lenses, no restructuring fold. §2 class bar MET.
**cycle_check (dogfood) after walk 4:** **`BAR_MET`** (exit 0) — the tool signals the close: class-dry walk, asserts #1 PASS / #2 #3 N/A (scratchpad draft), no restructuring, no plateau.
**Conflicts:** none.
**§5 Conformance:** `plan_lint` at shape-stability (walk 4) → **0 FAIL**; STEP count = 2; Rule 20 banner pair inlined in Step 2 (check (c) byte-match). Benign residual WARNs are the location-dependent bellows-in-tree class. cycle_check re-confirms `BAR_MET` with the Closing present (step-8 does not fire — the close is earned).
**Closing:** full walk 4 class-dry across all five lenses, no restructuring fold; cycle_check `BAR_MET`; §5 conformance 0 FAIL; closing-record re-read run (this block), dry; cycle CLOSED. Deposit exactly once (pending CEO go).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **Identity:** You are building `cycle_check --emit-manifest` (gap e) and the `plan_lint` stanza check (gap f). Read `knowledge/research/cycle-manifest-stanza-design-2026-08-19.md` FIRST — its Q2 grammar and Q4 validator are the Rule 27 spec; implement them, do not re-derive. Do NOT touch `DRAFTING_CYCLE.md` (component 2a).
>
> **Gap (e) — `cycle_check --emit-manifest <plan>`.** A new flag that emits the complete `## Cycle Manifest` stanza to STDOUT and exits 0. It COMPUTES the four computed fields from the plan's DC block + git/register/baseline state (reusing cycle_check's existing parsers):
> - `walks:` = walk count in the block; `yields:` = the per-walk instruction-class series (cycle_check already derives this for plateau) as comma-separated ints;
> - `validation:` = `cycle_check=<own verdict>, plan_lint=<N>_FAIL, fold_check=<PASS|N/A>` — RUN plan_lint and the fold_check baseline check as subprocesses/reads (read-only) and encode their results;
> - `coherence:` = `<K>/<N> walks have register rows` (from assert #2), or `N/A (no register declared)` for the common register-less plan — never fabricate a register count.
> It MERGES the authored declarations (`tier`, `target`, `class`, `reads`, `writes`, `open_forks`) from a **Planner-prefilled PARTIAL `## Cycle Manifest` stanza** — the plan HEADER does not carry `reads`/`writes`/`class`, so the partial stanza is the source (tier may fall back to the header's `**Tier:**`/`cycle_tier`). For any authored field the plan does not declare, emit a `<declare>` placeholder, never a guess. ⚠️ **The COMPUTED fields emit N/A when their data is not parseable** — `yields: N/A` for a block with no per-walk instruction counts, `coherence: N/A (no register declared)` for a register-less plan — matching cycle_check's own N/A discipline (component 1 V3); never fabricate a series or a count. Grammar per Q2: field order, `reads:`/`writes:` comma-lists with 2-space continuation lines, path normalization, placement.
> ⚠️ **Preserve component 1's invariants:** STDOUT ONLY — write no file, modify no plan, never `--save-baseline`. Preserve all 27 existing tests. `--emit-manifest` is an additive mode; the default verdict behavior is unchanged.
>
> **Gap (f) — `plan_lint` stanza-shape check (extend check (f)).** ⚠️ **Locate check (f) by CONTENT (grep its DC-block logic), not by the cited line numbers — they have drifted** (this session measured its core at ~365–388, the diagnostic cited ~311–391). Extending it must **PRESERVE its existing DC-block validation UNCHANGED** — every current plan must lint identically; the stanza check is PURELY ADDITIVE. Per Q4 Layer 1, but **presence-optional (non-disruptive):** if a `## Cycle Manifest` stanza is PRESENT (after `**Closing:**`), validate it — all 10 fields present + non-empty; `class:` ∈ `{read-only, governed-tooling, register-writing}`; `reads:` non-empty for any plan and `writes:` non-empty for a non-`read-only` plan; `validation:` contains at least `cycle_check=` and `plan_lint=`. **A field value that is the literal `<declare>` placeholder is treated as INCOMPLETE → warn** — a fresh `--emit-manifest` stanza is a template the Planner must fill, and a governed field like `class: <declare>` reaching the depositor would misfire its auto-deposit mapping. **WARN-first.** If NO stanza is present, do NOTHING (no warn) — 2a will later mandate presence. This keeps every current stanza-less plan clean.
>
> **Tests.** `tests/test_cycle_check.py`: --emit-manifest emits a well-formed 10-field stanza for a fixture plan; computed fields correct (walks/yields from the block, validation includes the three checkers, coherence N/A when no register); STDOUT-only (asserts the plan file is byte-unchanged after the run); `<declare>` placeholders for undeclared authored fields. `tests/test_plan_lint.py`: a well-formed stanza passes; a malformed one (missing field / bad class / empty reads) WARNs; **a stanza with a `<declare>` placeholder value WARNs (incomplete template — the I3 behavior);** a stanza-LESS plan produces NO stanza warn.
>
> **DEV discipline + dogfood:** targeted runs only (`python3 -m pytest tests/test_cycle_check.py tests/test_plan_lint.py -q 2>&1 | cat`). Then dogfood: `python3 scripts/cycle_check.py --emit-manifest knowledge/decisions/Done/executable-464.md` and include the emitted stanza in the dev log. Commit `feat(bellows): cycle_check --emit-manifest + plan_lint stanza check (component 2b) [<id>]`.
>
> **Deposits:**
> - `scripts/cycle_check.py`
> - `scripts/plan_lint.py`
> - `tests/test_cycle_check.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/cycle-manifest-tooling-2026-08-19.md`
>
> End with an Output Receipt recording Status AND the DEV commit sha (QA reads it). Standard prompt-feedback protocol.

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> **Identity:** You are QA for the Cycle Manifest tooling. Verify against the diagnostic-472 grammar. Evidence is RAW command output, never summaries.
>
> **(1) Targeted suites pass.** `python3 -m pytest tests/test_cycle_check.py tests/test_plan_lint.py -v 2>&1 | cat` → evidence `knowledge/qa/evidence/executable-cycle-manifest-tooling-2026-08-19/targeted.txt`. Confirm the --emit-manifest cases (well-formed stanza, computed fields, STDOUT-only, placeholders) and the plan_lint cases (well-formed pass, malformed warn, stanza-less no-warn) are all present.
>
> **(2) LIVE CANARY — --emit-manifest against REAL closed plans (the load-bearing guard).** Capture raw stdout+exit to `.../live_canary.txt`:
> - `--emit-manifest knowledge/decisions/Done/executable-464.md` → a well-formed 10-field stanza; `walks: 6`, `yields:` matches 464's `5, 2, 2, 1, 1, 0`, `validation:` carries cycle_check=BAR_MET + plan_lint result, `coherence:` is N/A-or-register per 464's reality. **Assert the plan file is byte-unchanged after the run** (`git status --porcelain` clean) — the read-only invariant, live.
> - `--emit-manifest knowledge/decisions/Done/diagnostic-460.md` → well-formed; `walks: 4`, `yields:` matches `8, 2, 2, 0`.
> - `plan_lint` on a plan carrying a well-formed stanza (paste 464's emitted stanza into a temp copy) → the new check PASSES; and `plan_lint` on a real stanza-LESS Done plan → NO stanza warn (non-disruptive).
> **Any crash, wrong computed value, or file mutation is a FAIL.**
>
> **(3) Full suite — Rule 21.** `python3 -m pytest tests/ -q -rf 2>&1 | cat` → `.../full_suite.txt`. Extract FAILED node-ids; assert empty (the 27 cycle_check tests + plan_lint tests + all others green — any failure is a regression).
>
> **(4) DRAFTING_CYCLE.md untouched.** `git diff --stat` shows NO `DRAFTING_CYCLE.md` and nothing outside `bellows/scripts/` + `bellows/tests/` + `knowledge/` — 2b is tooling only; the doctrine is 2a.
>
> **(5) Rule 20 self-check** — run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with `plan_slug: executable-cycle-manifest-tooling-2026-08-19`, the qa report path, the evidence dir, and `required_evidence_files: ["targeted.txt", "live_canary.txt", "full_suite.txt"]`. Prints the banner `Rule 20 — QA Self-Check Results` and, on success, `PASSED — SELF-CHECK PASSED` (verbatim, em-dashes — the gate byte-matches). If `FAILED — SELF-CHECK FAILED`, halt. `qa_test_result` gate: `full_suite.txt` + `targeted.txt` named in Deposits proactively (plan-452 lesson).
>
> **Deposits:**
> - `knowledge/qa/2026-08-19-cycle-manifest-tooling-qa.md`
> - `knowledge/qa/evidence/executable-cycle-manifest-tooling-2026-08-19/`
> - `knowledge/qa/evidence/executable-cycle-manifest-tooling-2026-08-19/targeted.txt`
> - `knowledge/qa/evidence/executable-cycle-manifest-tooling-2026-08-19/live_canary.txt`
> - `knowledge/qa/evidence/executable-cycle-manifest-tooling-2026-08-19/full_suite.txt`
>
> End with an Output Receipt (Status). Standard prompt-feedback protocol.
