# bellows — diagnostic: THE `qa_steps` PARSE DIVERGENCE — what spellings the corpus actually contains, what each parser returns for each, and whether the keyword fallback has ever been silently WRONG

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere threads **122** (the correction — 116's headline is wrong), 116 (superseded in part; its `gates` half stands), 102 (the original filing, whose counts remain unre-derived), 121 (the split that deferred FO-2 here) and 119 (the ruling). ⛔ **Do not read 116 without 122.** Clone origin: `Done/diagnostic-100034.md` — same kind, one Item per question, read-only, closed 2026-09-04.

## What this decides

**Nothing.** ⛔ **PT Rule 82.** FO-2 was deferred out of `executable-close-failopen-defaults` because closing it requires deciding whether the keyword fallback should exist — a decision nobody currently has the evidence to make. This produces that evidence and chooses nothing.

## Why this exists

Three positions have been held about `qa_steps: [2]`, and **all three are wrong** — including the one filed as the correction to the other two:

| position | source | verdict, as of 2026-09-04 |
|---|---|---|
| "`plan_lint` can't parse `[2]`, `gates` can" | thread 102 | **wrong** on both halves |
| "`plan_lint` DOES parse `[2]`, `gates` does NOT" | plan `u-qa-predicate-align` | ⛔ **substantially RIGHT** — and it was marked false in error |
| "neither parses it; `gates` falls back to keyword detection" | thread 116 | ⛔ **wrong about `plan_lint`**; right about `gates` |

⛔ **THREE positions, all three wrong, TWO of them this author's.** Thread 122 records the last one: `_parse_qa_steps` strips brackets at `plan_lint.py:36` and returns `{2}` for `'[2]'`. The probe that "measured" otherwise passed an entire plan DOCUMENT to a function whose signature takes a header VALUE; a bare `except` swallowed the error and returned `set()`, read as "does not parse". ⚠️ **A one-line positive control — `_parse_qa_steps('2') -> {2}` — would have exposed it.**

⛔ **The fallback is right only by coincidence.** `gates._gate_is_qa_step` declares the field malformed and scans the step heading for "qa". On `Done/executable-312.md` (step 2 titled `## STEP 2 — QA`) it returns True and looks correct. Rename that heading to `## STEP 2 — Beta`, changing nothing else, and it returns **False** with `[2]` still in the header.

⚠️ **Three published positions, every one wrong, produced by three separate hand-probes — two of them this author's, one of them the correction to the first.** Each was plausible, each named a real function, and each was believed. **That is the licensing argument**: this question has now defeated argument-from-source three times, and the only thing not yet tried is a systematic truth table over the real input space.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the divergent parsers | `plan_lint._parse_qa_steps` and `gates._gate_is_qa_step` (`gates.py:848`, the int-comprehension over a comma split) | grep both |
| P2 | ⛔ ONE parses it, one does not — CORRECTED 2026-09-04 | passing the HEADER VALUE as each signature requires: `_parse_qa_steps('[2]')` → **`{2}`** (it strips brackets, `:36`); `_gate_is_qa_step` on the same plans → True **only via** `qa_steps field malformed: '[2]' — falling back to keyword detection`. ⛔ **Pass the VALUE, never the document** — the document form returns `set()` from the bare `except` and reads as a parse failure (thread 122) | call each on the header VALUE, and on a known-good `'2'` first as a positive control |
| P2b | ⛔ **the divergence is ONE METHOD CALL** | `_parse_qa_steps` (`plan_lint.py:36`) does `str(raw).strip().strip("[]")` before splitting; `gates._gate_is_qa_step` (`gates.py:848`) does `str(qa_steps_raw).split(",")` with **no bracket strip**, so `int("[2]")` raises and the `except` falls back to keyword detection. Verified: `_gate_is_qa_step` at `:839`, the comprehension at `:848` | read both lines side by side |
| P2c | ⛔ **`_parse_qa_steps` is a viable ORACLE** | it returns the correct set for EVERY spelling the corpus contains: `2`→`{2}` · `3`→`{3}` · `1`→`{1}` · `4`→`{4}` · `[2]`→`{2}` · `[2, 3]`→`{2,3}` · `none`→`set()` · empty→`set()` · the template placeholder→`set()`. ⚠️ **This is what makes Q3 answerable** — "what correct parsing would have given" now has a reference implementation rather than a judgement | call it over the Q1 spelling census |
| P2d | ⚠️ the docstring points the wrong way | `_parse_qa_steps`'s own docstring says *"mirroring gates._gate_is_qa_step"* — but it does not mirror it, it is strictly MORE correct. A reader trusting the docstring would treat `gates` as the reference and `plan_lint` as the copy, which is how two of the three wrong positions were reached | read `plan_lint.py:32` |
| P3 | ⛔ the isolating proof | rewrite `312`'s step-2 heading to `## STEP 2 — Beta` and re-ask: `_gate_is_qa_step` → **False**. The correct-looking answer was entirely the fallback | re-run with the heading neutralised |
| P4 | the fallback's VALUE, not just its cost | the `else` arm is what catches a plan carrying a QA step that never declared one — the direction worth keeping strict (thread 118's warning against deleting the arm) | read the arm |
| P5 | thread 102's numbers are void, for a reason 116 got wrong | its counts (74 or 75; 66 or 67 FP; 8 blind) were derived without knowing the fallback was in play — that much holds. ⚠️ But 116's stated cause for voiding them ("neither parser handles the list form") is itself false, so the counts must be re-derived from the truth table rather than from either thread's account | read threads 102, 116 **and 122** |
| P6 | the corpus spelling population, MEASURED | across `Done/` + `drafts/`: `2` ×150 · `3` ×10 · **empty ×9** · `1` ×5 · **`none` ×4** · **`[comma-separated step numbers]` ×3** · `[2]` ×3 · `4` ×1 — **eight shapes**. ⚠️ An earlier draft of this pin said "`2` (101+26 occurrences) … six shapes already observed", a partial hand count; the measured figures come from the sibling cycle's walk 2. ⛔ Q1 must still re-derive them — this pin bounds the shape of the answer, it is not the answer | `grep -ohE "qa_steps:\*\* *[^|]{1,14}" Done/*.md \| sort \| uniq -c` |
| P7 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## The questions

⛔ **Answer each from the instrument's output.** An unanswerable question is a FINDING.

> **Q1 — What spellings does the corpus ACTUALLY contain?** Enumerate every distinct `qa_steps` header value across `Done/`, `drafts/` and any resident plan, with counts. ⛔ Derive the population mechanically; P6's list is partial and must not be treated as the answer.
>
> **Q2 — For each spelling, what does EACH parser return?** The full truth table: `_parse_qa_steps` and `_gate_is_qa_step`, side by side, per spelling. ⛔ **Neutralise the step heading when testing `gates`** — a heading containing "qa" makes the fallback mask the parse result, which is the confound that produced two wrong published positions.
>
> **Q3 — ⛔ Has the fallback ever been SILENTLY WRONG in the corpus?** For every plan where `gates` fell back, determine whether the fallback's answer matched what correct parsing would have given. ⛔ **Use `_parse_qa_steps` as the ORACLE** (P2c) — it is correct on every corpus spelling, so "what correct parsing would have given" is a computed reference, not a judgement. ⛔ **Never use `_gate_is_qa_step`'s own output as ground truth**; that is circular, and the circularity is exactly what let the fallback look correct for months. ⚠️ **This is the load-bearing question.** A fallback that has always agreed is a safety net; one that has silently disagreed has been suppressing QA gates on real plans, and the count is the harm.
>
> **Q4 — What does the fallback CATCH that parsing alone would not?** Plans with a QA step and no declaration, or a declaration that parses to the wrong step. ⛔ Report the count — this is the argument FOR keeping it, and it must be measured rather than assumed from P4.
>
> **Q5 — What is the blast radius of each candidate?** Per option: (a) parse the list form in both, keep the fallback; (b) parse in both, remove the fallback; (c) parse in both, keep the fallback but make it LOUD. How many corpus plans change QA-gate outcome under each?
>
> **Q6 — Do the two consumers legitimately need different semantics?** `plan_lint` decides whether to warn at authoring; `gates` decides whether QA gates fire at dispatch. ⛔ Report whether one shared parser is possible, or whether the divergence encodes a real difference — the answer decides whether this is one fix or two.
>
> **Q7 — What do thread 102's numbers become when re-derived correctly?** Its divergence counts are void (P5). Re-measure with the fallback understood, and state the corrected figures so thread 102 can be closed or re-scoped.

## Drafting Cycle

**Tier:** T1 — T-3 fires (both parsers run where plans are drafted and dispatched). **T-6 does NOT fire**: read-only; writes no doctrine, template, gate or specialist contract. ⚠️ It READS a gate, which is not editing one. T-8 not fired: clone by kind of `Done/diagnostic-100034.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-qa-steps-parsing-2026-09-04.md`
**Walks:** 6 (walks 0–6 complete).
- Weak spots:          w1 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w6 dry.
- Destruction:         w4 1 folded — instruction 1 / record 0; w6 dry.
- Vulnerabilities:     w3 1 folded — instruction 1 / record 0; w6 dry.
- Integration-record:  w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 0 / record 1; w3 1 folded — instruction 1 / record 0; w5 1 folded — instruction 0 / record 1; w6 dry.
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry.
**Battery run at both walks.** `fold_check` baselined before the first fold and CLEAN after each; `propagation_check` DIVERGENT:4.
⚠️ **Walk 1 rewrote this plan's own premise** after thread 122 falsified thread 116, which the plan had cited as its measurement. **Walk 2 then swept by CLAIM and found three stale references walk 1's fold had not propagated** — the Depends-on line, the intro's "the first two are wrong", and P5's justification.

⚠️ **Two fold-introduced findings, both from walk 1's premise rewrite** — w2-1's unpropagated references and w4-1's self-tripping HALT. The expected cost of correcting a plan's foundation mid-cycle; both caught by the walk that followed.

**Closing:** BAR MET at walk 6 — yields 2, 1, 3, 1, 1, 0, falling to a dry pass.

## Cycle Manifest
tier: T1
target: the qa_steps parse divergence — plan_lint._parse_qa_steps vs gates._gate_is_qa_step; read-only census
class: shop-infra
reads: scripts/plan_lint.py, gates.py, knowledge/decisions/Done/executable-312.md, knowledge/decisions/Done/executable-313.md
writes: tools/qa_steps_parse_census.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/qa-steps-parsing-2026-09-04.md, knowledge/development/dev-log-qa-steps-parsing-2026-09-04.md
open_forks: whether gates' keyword fallback should exist at all — this plan prices that decision and does not make it
walks: 6
yields: 2, 0, 3, 1, 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A, propagation_check=DIVERGENT:7
coherence: 6/6 walks have register rows

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/qa_steps_parse_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/qa-steps-parsing-2026-09-04.md`
> - `knowledge/development/dev-log-qa-steps-parsing-2026-09-04.md`
>
> ⚠️ **TWO REPOSITORIES.** Governance by absolute path with `git -C "$GOV"`, never `cd`; commit it by **EXPLICIT PATHSPEC** — this plan's own walk register lives there and will be dirty. ⛔ Commit bellows LAST.
>
> **Item 1 — re-derive P1–P7 (including P2b, P2c, P2d) and HALT on mismatch.** ⛔ **The HALT condition is `gates`, NOT "either parser".** `plan_lint._parse_qa_steps` has ALWAYS handled `[2]` — that is this plan's corrected premise (P2, thread 122), so a HALT phrased as "if either parser now handles it" would fire immediately on the plan's own starting state. ⚠️ An earlier draft was phrased exactly that way; it was written before the correction and would have been self-tripping. **HALT only if `gates._gate_is_qa_step` now parses `[2]` without falling back** — i.e. if the open defect has been fixed since. ⛔ Re-run P3's isolating proof (heading neutralised) to confirm the fallback is still what produces the answer.
>
> **Item 2 — build `tools/qa_steps_parse_census.py`.** ⛔ **Import both parsers and call them; do not re-implement either.** Two readers of one format diverge — that is the defect under study, and reproducing it inside the instrument would make the census measure itself. ⛔ **When exercising `gates`, neutralise the step heading** (P3's method) so the fallback cannot mask the parse result.
>
> **Item 3 — Q1: the spelling census**, derived mechanically with counts.
>
> **Item 4 — Q2: the truth table**, both parsers per spelling, headings neutralised.
>
> **Item 5 — Q3: has the fallback been silently wrong?** Per plan where it fired, whether its answer matched correct parsing. ⛔ Report the count of disagreements as the headline; zero is as important a result as many.
>
> **Item 6 — Q4: what the fallback catches** that parsing alone would not, counted.
>
> **Item 7 — Q5: blast radius per candidate** (a), (b), (c), each as a count of plans whose QA-gate outcome changes.
>
> **Item 8 — Q6: shared parser or two**, answered from the two consumers' actual decisions.
>
> **Item 9 — Q7: thread 102's corrected numbers.**
>
> **Item 10 — deposit the research note** with a coverage statement naming anything unassessable.
>
> **Item 11 — dev-log**, recording that two published positions on this were both wrong and how the confound produced them.
>
> **Item 12 — commit** (message tagged with the plan id); record `numstat` — **TWO commits in two repos**: 1 governance, 2 bellows.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named here, overridden by the Planner with reference to this note — the 100032/100034 precedent.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/qa-steps-parsing-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-qa-steps-parsing-2026-09-04.md`
>
> **Post-conditions:** every spelling in the corpus enumerated with counts; the truth table complete for both parsers with headings neutralised; Q3 answered with a disagreement count and the plans named; Q4's catch-count measured not assumed; blast radius given per candidate; thread 102's figures re-derived; ⛔ **no recommendation and no design anywhere in the note** — it prices, it does not choose.
