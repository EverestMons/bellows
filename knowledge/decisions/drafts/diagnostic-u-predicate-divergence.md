# bellows — diagnostic: CHECK (u)'s QA-STEP PREDICATE vs THE GATE'S — which of (u)'s TWO ARMS produces each divergence, whether thread 102's 74-of-861 is reproducible from git, and what 100036 did and did not establish about it

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere threads **102** (the filing under examination — still OPEN and un-re-scoped), **122** (the correction that voided 116), **116** (⛔ closed SUPERSEDED by 122 on 2026-09-04 13:09 — do not read it without 122), **124** (the wrap triage that instructed a re-scope of 102 on a premise this plan tests), **125** (the Rule 102 routing of 116's three surviving citation sites) and **120** (the ruling: for deep analysis, diagnostic output is the only admissible evidence). Clone origin: `Done/diagnostic-100036.md` — same kind, same question family, closed 2026-09-04, and the plan whose Q7 this one examines.

## What this decides

**Nothing.** ⛔ **PT Rule 82.** This measures what check (u) does and what thread 102 measured. Whether (u) should be pointed at `gates._gate_is_qa_step`, at `_parse_qa_steps`, or at a new shared parser is a design decision entangled with the still-open fallback question 100036 priced and deliberately did not choose. This produces the evidence and chooses nothing.

## Why this exists

⛔ **Thread 124 instructed that thread 102 be re-scoped "against 100036's corrected figures". 100036 has no figures about thread 102's subject.** Measured 2026-09-04, before this plan was drafted:

    grep -n "check (u)\|(u)'s\|plan_lint (u)\| (u) " Done/diagnostic-100036.md \
        governance/knowledge/research/qa-steps-parsing-2026-09-04.md   -> ZERO hits
    grep -n "861" <the same two files>                                  -> ZERO hits

100036's declared scope is two HEADER PARSERS — `plan_lint._parse_qa_steps` against `gates._gate_is_qa_step`. Thread 102's subject is a different comparison: **check (u)'s composite predicate** at `plan_lint.py:365` —

    is_qa_step = sn in qa_steps_set_u or "Rule 20" in step_text_u

— against `gates._gate_is_qa_step`. **Only the FIRST arm reads the header.** Thread 102 attributes its 66 false positives to the second: *"mostly diagnostic-*.md step 1, whose read-only audit prose mentions Rule 20."* A parser census cannot see that arm, and 100036 did not look for it.

⚠️ **So 100036's Q7 answers about a comparison thread 102 did not make.** Its reasoning — *"both parsers see the same empty value... There is no `plan_lint` vs `gates` divergence for those plans"* — is true of the parsers and silent about arm B, which fires regardless of what either parser returns. Q7 also restates 102's unit as *"~74–75 **plans**"* where 102 measured 74 of 861 **steps**; the unit slip is the tell that Q7 worked from a restatement of 102 rather than from 102's measurement.

⛔ **This is the FOURTH restatement failure in this question's history, and the first one committed by a diagnostic rather than a hand-probe.** Threads 102, `u-qa-predicate-align`, and 116 each published a wrong position about the parsers. 100036 settled the parsers and then, in its final question, restated a claim about a check it had never executed. ⚠️ **That is the licensing argument**: the instrument that settled the parsers is not the instrument that settles (u), and the difference was invisible to everyone who read 100036's Q7 — including the wrap triage that acted on it.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ **100036 never measured (u)** | zero hits for `(u)` and for `861` across `Done/diagnostic-100036.md` and `governance/knowledge/research/qa-steps-parsing-2026-09-04.md`. ⚠️ **This pin is the plan's whole license.** If it fails to re-derive, the plan's premise is gone and the correct verdict is RE-DRAFT, not a fold | the two greps above, run from `bellows/` with the governance path absolute |
| P2 | ⛔ **(u) has TWO ARMS with different mechanisms** | `plan_lint.py:365` — `sn in qa_steps_set_u or "Rule 20" in step_text_u`. **Arm A** reads the header through `_parse_qa_steps` (`:358`, bracket-correct). **Arm B** is a literal substring scan of the step's own text with no counterpart anywhere in `gates`. The (u) block spans `:358-376` | `sed -n '358,376p' scripts/plan_lint.py` |
| P3 | ⛔ **the gate's own two arms do not correspond to (u)'s** | `gates._gate_is_qa_step` (`gates.py:839`): header parse (`:848`, no bracket strip) falling back to `"qa" in <step heading>`. **Arm A vs the gate's parse is a PARSER question (settled by 100036). Arm B vs the gate's keyword fallback is not — they scan different TEXT for different TOKENS**: (u) scans the whole step body for `"Rule 20"`, the gate scans the heading line only for `"qa"` | read both functions side by side |
| P4 | ⛔ **102's denominator does NOT reproduce — measured, 9 short** | thread 102 reports 861 `## STEP` headings in `Done/` on 2026-09-03 10:55. The git tree at that moment (`df83640`) yields **870** under `grep -c "^## STEP "`. Nearest neighbours: 868 at 09:00, 870 at 12:00, 873 at EOD, **880 today**. ⚠️ **A 9-step gap at the stated timestamp is not corpus drift** — drift moves the count up over the day, and 861 is below every measured tree | `git rev-list -1 --before="2026-09-03 10:55" main`, then count `^## STEP ` across that tree's `Done/*.md` |
| P4a | the leading HYPOTHESIS for P4's gap, ⛔ **untested** | `plan_lint` extracts steps with `re.findall(r'^(## STEP (\d+)\b[^\n]*)', clean_text, re.MULTILINE)` at `:258` — over `clean_text` (fenced code stripped) and requiring a DIGIT. A raw `grep` counts headings inside fenced blocks and headings with no step number; those are candidates for the 9. ⛔ **This is a source read, which ruling 120 makes inadmissible as evidence — Q3 must EXECUTE the extractor, not reason about it** | `grep -n "step_headers *=" scripts/plan_lint.py`, then run the extractor over the 09-03 tree |
| P5 | ⛔ **Q7's "not re-derivable" is FALSE, and its stated reason is false too** | 100036 Q7: *"not re-derivable from this corpus without knowing which plans were in scope at the time of thread 102's measurement (which preceded the `qa_steps` field being introduced)."* Measured: the 2026-09-03 corpus **is fully recoverable from git** (`df83640`); and `_gate_is_qa_step` first entered `gates.py` on **2026-05-15**, the `qa_steps` field governance plan is dated **2026-05-25** — both over three months BEFORE thread 102 (2026-09-03). ⚠️ 102's measurement did not precede the field; it postdates it by a quarter | `git log -S"_gate_is_qa_step" --date=short --format="%ad" -- gates.py \| tail -1`; `git rev-list -1 --before=...` |
| P6 | ⛔ **100036's note CONTRADICTS ITSELF on Q7** | its coverage statement says, in both the header and the footer, *"No question was unassessable"* / *"Unassessable: None. All seven questions are fully answerable"* — while Q7's body says 102's counts are *"not re-derivable"*. And `diagnostic-100036.md`'s own STEP 1 post-condition requires *"thread 102's figures re-derived."* ⚠️ **A post-condition not met by the deposited output, with a coverage statement asserting it was.** Report it; this plan does not adjudicate it | read the note's two coverage statements against its Q7 |
| P7 | the fallback population (u) may be BLIND to | 100036 Q4 measured **169 plan+step combinations** where `gates` detects QA by keyword fallback alone (165 with an empty `qa_steps`, 4 with `none`, 1 mis-numbered). For every one of those, (u)'s arm A is EMPTY by construction (`qa_steps_raw` falsy → `set()`), so (u) sees them only if arm B's literal `"Rule 20"` appears in the step body. ⛔ **Thread 102 counted 8 blind spots. P7 says the candidate population is 169.** Whether the gap is arm B doing the work or 102 undercounting is Q4's question — ⚠️ **do not assume either; both are live** | Q4 of `qa-steps-parsing-2026-09-04.md`; then measure |
| P8 | (u)'s reachability guard | (u) skips a step when `gates._extract_step_text` returns falsy (`:362-363`). ⛔ **A step (u) never examines is not a "no" from (u)** — the census must separate SILENT-because-skipped from SILENT-because-predicate-false, or it will report the first as the second | `sed -n '360,364p' scripts/plan_lint.py` |
| P9 | ⛔ **`_parse_qa_steps` is the correct reference for the HEADER — and 100036 says nothing about (u)'s arm B** | 100036 Q6: both header consumers *"answer the same question"*, a single shared parser is possible, and `_parse_qa_steps` *"is the correct reference implementation"*. ⚠️ **That finding is about the header parse ONLY.** `plan_lint.py:379-380` carries a live MUST-PRESERVE comment pointing (v) at `gates._gate_is_qa_step` and citing *"P11 measured 74 divergences across 861 steps"*. ⛔ **This plan does not decide whether that comment is now wrong** — it measures whether its cited figure reproduces (Q3) and reports the tension | read `:379-383` beside Q6 |
| P10 | file identity — the check | `scripts/plan_lint.py` sha256 `14548102179255895aa55eac4da4180bd66d2615ef6bfc3b01e112e187a05c9d` | `shasum -a 256 scripts/plan_lint.py` |
| P11 | corpus size at drafting | `Done/` 551 plans / 880 `^## STEP ` headings; `drafts/` 28 plans | `ls knowledge/decisions/Done/*.md \| wc -l`; `grep -h "^## STEP " knowledge/decisions/Done/*.md \| wc -l` |
| P12 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |
| P13 | ⛔ **file identity — the gate. Its row is SEPARATED from P10 deliberately; do not move it back** | `gates.py` sha256 `33ecbbf67d98745148d1e13e73611d5b32c7c82a97cded2a1d6bf544f2b6e7c6`. ⚠️ **Measured at walk 0**: `plan_lint`'s check (q) resolves a sha pin's file from a THREE-LINE window `[n-2, n-1, n]` (`_check_pins`) and `_extract_pin_path` returns the path from the FIRST line in that window matching `\bsha(?:sum\|256(?:sum)?)\b`. Two sha pins on adjacent rows therefore make the SECOND resolve against the FIRST's file — this pin reported `MISMATCH on scripts/plan_lint.py` until two clean rows were placed between them. ⛔ **A false-positive class in a shipped check, filed for its own diagnostic; NOT this plan's subject** | `shasum -a 256 gates.py` |

## The questions

⛔ **Answer each from the instrument's output.** An unanswerable question is a FINDING, and this plan's clone origin is the reason: 100036 answered Q7 from a restatement and its coverage statement recorded no unassessable question. ⚠️ **"Unknown" is an acceptable answer here and "not re-derivable" is not, unless a COMMAND is shown to fail.**

> **Q1 — What does (u) actually decide, per step, across the corpus?** For every step `plan_lint` extracts from `Done/` + `drafts/`, record: arm A's value, arm B's value, (u)'s combined verdict, and whether the step was SKIPPED at `:362` (P8). ⛔ **Four columns, not one** — a combined verdict alone cannot attribute a divergence to an arm.
>
> **Q2 — Where does (u) diverge from `gates._gate_is_qa_step`, and WHICH ARM causes each?** The divergence set, split into: arm-A-only, arm-B-only, both-arms, and gate-says-QA-(u)-silent. ⛔ **Attribute every divergence to a mechanism.** Thread 102's 66 FP / 8 blind split is the hypothesis under test, not the frame — report the measured split whatever shape it takes.
>
> **Q3 — Is thread 102's 74-of-861 reproducible at the tree it was measured on?** Check out `df83640` (2026-09-03 10:55) and run the same census. ⛔ **Report the denominator FIRST and separately** — P4 measured 870 by raw grep against 102's 861, and P4a's extractor hypothesis is a SOURCE READ that ruling 120 makes inadmissible. Execute the extractor; do not reason about it. ⚠️ If the denominator reproduces but the divergence counts do not, that is a different finding from neither reproducing, and the two must not be reported as one.
>
> **Q4 — How many steps is (u) BLIND to that the gate gates?** P7 puts the candidate population at 169 and thread 102 reported 8. ⛔ **Measure the true count and, for every blind step, record whether arm B fired.** ⚠️ Report SKIPPED steps (P8) as their own category, never folded into "blind".
>
> **Q5 — What is arm B's false-positive population, and what text triggers it?** For every step where arm B fires and the gate says NOT-QA, record the matched context. ⛔ 102 claims *"mostly diagnostic-*.md step 1"* — report the actual distribution by plan kind, and the count of steps where arm B is the SOLE reason (u) says QA.
>
> **Q6 — What does 100036's Q7 establish about thread 102, stated exactly?** ⛔ **A record question, answered by quotation, not by judgement.** Quote what Q7 measured, quote what it asserted about 102, and state which assertions its instrument's output supports. ⚠️ Report P5's and P6's re-derivations here (the false parenthetical, the recoverable corpus, the self-contradicting coverage statement). ⛔ **This plan does not rule on 100036's closure** — it records what is re-derivable and routes the rest.
>
> **Q7 — What is the blast radius of each candidate for (u)?** Per option, as a count of plan+step outcomes that change: (a) point (u) at `gates._gate_is_qa_step` (thread 102's stated fix, and what `:379`'s comment already does for (v)); (b) point (u) at `_parse_qa_steps` alone, dropping arm B; (c) keep arm B, fix only arm A's header handling; (d) leave (u) as it is. ⛔ **Price all four and choose none** — (a) and (b) move in opposite directions and 100036's Q6 bears on only half of the question.

## MUST-PRESERVE — this plan is a LIVE SPECIMEN of the defect it measures

⛔ **`plan_lint` (u) fires on this plan's own STEP 1, and the gate disagrees. Do not reword to silence it.** Measured 2026-09-04 at walk 0's consumer dry-run, with a positive control run first (`_parse_qa_steps('2') -> {2}`, the one-line control whose absence produced thread 116):

    qa_steps_raw                      = ''          # arm A empty by construction
    arm A: 1 in _parse_qa_steps('')   = False
    arm B: "Rule 20" in step_1_text   = True        # Item 2 QUOTES (u)'s own source line
    (u) is_qa_step                    = True
    gates._gate_is_qa_step(text, 1)   = False       # <- the divergence

**This is an arm-B-only FALSE POSITIVE — the exact class thread 102 attributes its 66 FPs to, reproduced on the plan that exists to count them.** The two `(u) WARN` lines about STEP 1's Deposits order and missing `.txt` are downstream of it and are likewise expected.

⛔ **The literal string `Rule 20` must survive in Item 2 and in P2/P3.** It is quoted from `plan_lint.py:365`, it is what the instrument must evaluate, and removing it would make the plan lint clean by hiding its own subject. ⚠️ **Thread 102 set this precedent on plan 100028** — pre-declare the WARN in MUST-PRESERVE rather than dodge it by rewording — and the specimen is evidence for Q5, not noise. ⚠️ A later tidier who "fixes" these WARNs destroys the specimen.

## Drafting Cycle

**Tier:** T1 — **T-3 fires** ((u) runs where plans are drafted, `gates` where they are dispatched) and **T-7 fires** (a later plan will act on these findings without re-verification). **T-6 does NOT fire**: read-only; it READS a check and a gate, which is not editing one. **T-8 not fired**: clone by kind of `Done/diagnostic-100036.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-u-predicate-divergence-2026-09-04.md`
**Walks:** walk 0 complete (context pin + consumer dry-run). ⛔ **v0 — NO LENS HAS WALKED IT and NO DIRECTION VERDICT has been issued.** DC §2.0's entry gate (walk 1, then PROCEED / CUT-AND-PROCEED / RE-DRAFT) is manual and remains open.
**Battery at walk 0:** `plan_lint` **0 FAIL** · `cycle_check` **CONTINUE** · `fold_check` **baselined** (readers=1, signals=8) · `walk_register_lint` **NO_TABLE** (correct for a register with no walk rows) · `propagation_check` **DIVERGENT:164 — all 164 classified false positive** (78 `100036` + 48 `102` are plan/thread IDs, thread 96's row-id fallback class; 18 `20` from the literal `Rule 20` this plan must quote; 13 date/timestamp fragments; 3 line numbers; the only real quantity, `861` ×4, is consistent across all eight of its occurrences).
**Consumer dry-run (EXECUTION, DC §2.0's sixth act):** depositor `_assign_class` over the declared write set → **`shop-infra`**, matching the manifest. ⛔ It found TWO defects — the live-specimen (u) firing (see MUST-PRESERVE) and check (q)'s 3-line pin window (P13). Both recorded in the walk register as M12a / M12b.

## Cycle Manifest
tier: T1
target: check (u)'s composite QA-step predicate vs gates._gate_is_qa_step; read-only census, per-arm attribution
class: shop-infra
reads: scripts/plan_lint.py, gates.py, knowledge/decisions/Done/, knowledge/decisions/drafts/, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/qa-steps-parsing-2026-09-04.md
writes: tools/u_predicate_divergence_census.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/u-predicate-divergence-2026-09-04.md, knowledge/development/dev-log-u-predicate-divergence-2026-09-04.md
open_forks: whether (u) should point at gates, at _parse_qa_steps, or keep arm B — this plan prices all four candidates and makes none of the choices; entangled with 100036's still-open fallback fork
walks: 0
yields: (none — no lens has walked v0)
validation: cycle_check=CONTINUE, plan_lint=0_FAIL, fold_check=BASELINED, propagation_check=DIVERGENT:164
coherence: n/a — walk 0 only; the register carries M1-M12c and no findings table

## STEP 1 — the (u) census (read-only; decides nothing)

> **Scope:**
> - `tools/u_predicate_divergence_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/u-predicate-divergence-2026-09-04.md`
> - `knowledge/development/dev-log-u-predicate-divergence-2026-09-04.md`
>
> ⚠️ **TWO REPOSITORIES.** Governance by absolute path with `git -C "$GOV"`, never `cd`; commit it by **EXPLICIT PATHSPEC** — this plan's own walk register lives there and will be dirty. ⛔ Commit bellows LAST.
>
> **Item 1 — re-derive P1–P10 and HALT on P1's failure.** ⛔ **The HALT condition is P1 alone.** If `(u)` or `861` now appears in `diagnostic-100036.md` or its research note, then 100036 measured (u) after all, this plan's license is void, and the correct outcome is a HALT and a RE-DRAFT — not a fold. ⚠️ Every other pin mismatch is a finding to record, not a halt.
>
> **Item 2 — build `tools/u_predicate_divergence_census.py`.** ⛔ **Import `plan_lint` and `gates` and call them; re-implement neither.** ⛔ **The instrument must expose (u)'s TWO ARMS SEPARATELY** — evaluate `sn in qa_steps_set_u` and `"Rule 20" in step_text_u` as distinct recorded values, not only their `or`. A census that records only the combined verdict cannot answer Q2 and would repeat 100036's failure in a new place. ⛔ **Record the `:362` skip as a third state**, never as False (P8).
>
> ⚠️ **POSITIVE CONTROL, before any corpus run** — thread 122's method note, and the reason three probes failed: call each function on a KNOWN-GOOD input and confirm the expected value. `_parse_qa_steps('2') -> {2}`; arm B on a step body containing the literal `Rule 20` -> True; `_gate_is_qa_step` on `Done/executable-312.md` step 2 -> True. ⛔ **Deposit the control's output.** A census whose control is absent is not evidence.
>
> **Item 3 — Q1: the four-column per-step table** over `Done/` + `drafts/` at HEAD.
>
> **Item 4 — Q2: the divergence set with per-arm attribution**, split four ways.
>
> **Item 5 — Q3: re-run the census at `df83640`.** ⛔ Use a git worktree or `git show`; do NOT check out over the working tree while the daemon is running. ⛔ **Report the denominator separately from the divergence counts.**
>
> **Item 6 — Q4: the blind-spot count**, with arm B's status per blind step and SKIPPED broken out.
>
> **Item 7 — Q5: arm B's FP population** and its trigger text, distributed by plan kind.
>
> **Item 8 — Q6: what 100036's Q7 establishes**, by quotation, with P5 and P6 re-derived.
>
> **Item 9 — Q7: blast radius for candidates (a)–(d)**, each a count of plan+step outcomes that change.
>
> **Item 10 — deposit the research note** with a coverage statement naming anything unassessable. ⛔ **If a question is unassessable, SAY SO** — the clone origin's coverage statement asserted zero unassessable questions while its Q7 said "not re-derivable", and that contradiction is why this plan exists.
>
> **Item 11 — dev-log**, recording that a diagnostic's final question was answered from a restatement of a thread rather than from its instrument, and that a wrap triage then acted on it.
>
> **Item 12 — commit** (message tagged with the plan id); record `numstat` — **TWO commits in two repos**: 1 governance, 2 bellows.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named here, overridden by the Planner with reference to this note — the 100032/100034/100036 precedent.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/u-predicate-divergence-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-u-predicate-divergence-2026-09-04.md`
>
> **Post-conditions:** (u)'s two arms measured separately for every extracted step; every divergence attributed to an arm; the `:362` skip reported as its own state; thread 102's denominator re-run at its own tree with the result stated whether or not it reproduces; the blind-spot count measured against P7's 169-candidate population; all four candidates priced; ⛔ **no recommendation and no design anywhere in the note** — it prices, it does not choose.
