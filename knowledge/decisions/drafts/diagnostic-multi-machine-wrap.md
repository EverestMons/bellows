# bellows — diagnostic: WHAT DOES A WRAP MEAN WHEN TWO MACHINES ARE LIVE — which of its artifacts are shared, which of its seven gates hold a FILE-GLOBAL invariant, and where the scope rule and the ordering rule contradict each other

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** the three documents under examination — `hooks/commands/wrap.md`, `hooks/commands/eluvian.md`, `$ELUVIAN_WRAP_ROOT/MACHINE_SETUP.md` (v1.2, 2026-09-02) — and `hooks/eluvian/wrap_check.py`, the enforcer none of them describes completely. Related threads: **53** (`wrap_debt_hook` keys on today's date where `/wrap` keys on session id), **57** (the multi-machine project-status goal sketch), **9**, **89**, **113**. Clone origin: `Done/diagnostic-100036.md` — same kind, read-only, one Item per question, closed 2026-09-04.

## What this decides

**Nothing.** ⛔ **PT Rule 82.** It prices a question the CEO asked on 2026-09-04 — *"what does the wrap command mean when we have multiple machines going?"* — and chooses no remedy. ⚠️ Two of its candidate answers are doctrine amendments (T-6) and one is a gate change; **deciding any of them here would smuggle a governance edit into a read-only census.**

## Why this exists

⛔ **The question is not hypothetical. It was answered by an incident on 2026-09-04, mid-cycle**, while this Planner was walking an unrelated plan:

1. Session `3b6ea354` on the shop machine wrapped and pushed.
2. **Both of this machine's pushes were REJECTED** (`! [rejected] main -> main (fetch first)`) — bellows and governance.
3. Its wrap inserted its session block ABOVE this machine's in `shop_next_session.md`, so **the FIRST `Lessons-swept:` line in the file is now the shop's**, not the mini's.
4. `LESSONS.md` moved a SECOND time that afternoon, by a second writer (entries 424–425 after this machine's 419–423).

**Each machine obeyed the doctrine exactly.** `/wrap`'s scope rule is about whose SESSIONS you narrate; both narrated only their own. What no document governs is that both wraps WRITE THE SAME THREE FILES.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the three documents | `hooks/commands/wrap.md`, `hooks/commands/eluvian.md`, `MACHINE_SETUP.md` **v1.2 (2026-09-02)** | `grep -m1 "^\*\*Version" MACHINE_SETUP.md` |
| P2 | ⛔ `/wrap`'s scope rule governs NARRATIVE, not ARTIFACTS | `wrap.md:11` `## Scope: THIS MACHINE ONLY`; `:15` *"never sweep, narrate, or complete another machine's sessions: their arcs, verdicts, and `Lessons-swept:` lines are theirs."* ⚠️ **Every noun in that clause is a story; none is a file** | `sed -n '11,20p' hooks/commands/wrap.md` |
| P3 | `/eluvian`'s multi-machine law bounds the SESSION START only | `eluvian.md:14` — *"Pull latest code (multi-machine law: every machine runs the newest committed state)"* ⚠️ It fires at align time. A wrap hours later has no equivalent | `sed -n '14p' hooks/commands/eluvian.md` |
| P4 | ⛔ `MACHINE_SETUP` covers PARITY, not CONCURRENCY | its goal is quoted CEO 2026-08-31: *"bring in a new machine and have it working in the same way as the others"* — provisioning. The ONE concurrent-operation hazard it addresses is id-range partitioning (`:34`), because ids *"key shared git namespaces"*. **Shared DOCUMENTS get no equivalent clause** | `grep -nE "multi\|concurrent\|other machine" MACHINE_SETUP.md` |
| P5 | the enforcer's gate set, derived mechanically | seven: `[0/resolve] [1/project] [2/bellows] [2r/receipts] [3/root] [3b/lessons] [4/memory]` | `grep -oE '\[[0-9][a-z]?/[a-z]+\]' hooks/eluvian/wrap_check.py \| sort -u` |
| P6 | ⛔ `[3b/lessons]`'s invariant is FILE-GLOBAL, not machine-local | `_find_newest_sweep_line` returns the **FIRST** `Lessons-swept:` line in the whole baton, and `[3b]` requires it carry THIS session's id. **Any machine that writes above you takes "newest" from you** | read `_find_newest_sweep_line`; `grep -n "^Lessons-swept:" shop_next_session.md \| head -3` |
| P7 | ⛔ the incident, measured after the fact | the baton's first sweep line is now `[sid: 3b6ea354]` (line 19); this machine's are at 42 and 44. The shop's session block sits at line 3, this machine's at 21 | `grep -n "^Lessons-swept:\|^> ## ⭐" shop_next_session.md \| head -6` |
| P8 | ⛔ **the contradiction, stated as two quotes** | `[3b/lessons]` requires the newest sweep line be yours (P6); `wrap.md` requires *"never rewrite another machine's blocks"*. **A second wrap on this machine now must write above the shop's block to pass.** Whether that IS a rewrite is undecided — no document says | run a second wrap here and read the failure |
| P9 | fetch-first does not bound a long session | `wrap.md` step 0 mandates `git fetch` before judging. Measured 2026-09-04: this machine fetched at wrap start and both pushes were still rejected hours later | the reflog + the rejection text |
| P10 | two-machine wrap days are NOT rare | `2026-09-04` carries wraps from `42ce7e32` ×3 and `d04ebd33` (mini) plus `3b6ea354` (shop); `2026-09-02` carries an Air wrap beside the mini's | `git log --format="%ad %s" --date=short -- shop_next_session.md \| grep -i "session wrap"` |
| P11 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## The questions

⛔ **Answer each from the instrument's output.** An unanswerable question is a FINDING — and this plan's clone origin is the reason: `diagnostic-100036` answered its last question from a restatement while its coverage statement claimed nothing was unassessable.

> **Q1 — What does a wrap WRITE, and which writes are shared?** Enumerate every path a `/wrap` touches, from the ritual text and from the last four wrap commits. Classify each: **machine-local** (only this host's sessions ever write it) or **SHARED** (two hosts can write the same file in one day). ⛔ Derive from the commits, not from the ritual's prose — the ritual describes intent, the commits describe practice.
>
> **Q2 — For each of the seven gates, is the invariant machine-local or file-global?** Per gate: what it reads, what it asserts, and whether another machine's push can falsify it AFTER it passed. ⛔ **Report the ones that survive as prominently as the ones that break** — a census that only lists failures cannot say how big the problem is.
>
> **Q3 — Reproduce P8's contradiction, or refute it.** Construct the exact sequence (machine A wraps → machine B wraps and lands above → machine A wraps again) against a scratch copy of the baton and run `wrap_check` on it. ⛔ **Report whether `[3b/lessons]` actually fails, and what the minimum conforming edit is** — then state whether that edit rewrites another machine's block under `wrap.md`'s own words. ⚠️ If it does NOT fail, P8 is void and that is the finding.
>
> **Q4 — How long does a wrap outlive its own fetch?** Measure the wall-clock from step 0's `git fetch` to the final push for the last several wraps. ⛔ The question is not "was there a collision" but "how wide is the window the ritual leaves open".
>
> **Q5 — What do the three documents each say, and where are the SILENCES?** For `wrap.md`, `eluvian.md` and `MACHINE_SETUP.md`: quote every clause bearing on multiple machines, and name what none of them covers. ⛔ **A silence is a finding; do not paper one over by inferring intent.**
>
> **Q6 — How often has this actually happened?** Count the days on which two or more machines wrapped, and for each, what landed in what order and whether anything was lost. ⛔ **Check for LOSS specifically** — an append that rebased cleanly is not evidence that none ever failed to.
>
> **Q7 — Price the candidates, choose none.** At minimum: (a) per-machine sweep lines keyed by machine rather than file order; (b) a wrap-time re-fetch immediately before push; (c) a per-machine baton section with a merge convention; (d) leave it and document the hazard. Per candidate: what breaks, what it costs, and ⛔ **which are T-6 doctrine amendments** — `wrap.md` and `MACHINE_SETUP.md` are governance surfaces and an amendment is its own plan at its own tier.

## Drafting Cycle

**Tier:** T1 — **T-3 fires** (the subject is behaviour across machines and locales) and **T-7 fires** (a later plan will act on these findings without re-verification). ⛔ **T-6 does NOT fire for THIS plan**: it READS `wrap.md`, `eluvian.md` and `MACHINE_SETUP.md` and edits none of them. ⚠️ **Its Q7 candidates (a)–(c) are T-6 and must be split into their own plans** — DC §1's split-on-tier rule, priced before the ceremony is accepted. **T-8 not fired**: clone by kind of `Done/diagnostic-100036.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-multi-machine-wrap-2026-09-04.md`
**Walks:** walk 0 complete (context pin). ⛔ **v0 — NO LENS HAS WALKED IT and NO DIRECTION VERDICT has been issued.**

## Cycle Manifest
tier: T1
target: the wrap ritual's behaviour when two machines are live — shared-artifact census, gate-invariant classification, read-only
class: shop-infra
reads: hooks/commands/wrap.md, hooks/commands/eluvian.md, hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md, /Users/marklehn/Developer/eluvian-governance/shop_next_session.md
writes: tools/wrap_concurrency_census.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/multi-machine-wrap-2026-09-04.md, knowledge/development/dev-log-multi-machine-wrap-2026-09-04.md
open_forks: whether the [3b/lessons] ordering rule or the never-rewrite rule yields — a doctrine decision this plan prices and does not make
walks: 0
yields: (none — no lens has walked v0)
validation: (not yet run)
coherence: n/a — walk 0 only

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/wrap_concurrency_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/multi-machine-wrap-2026-09-04.md`
> - `knowledge/development/dev-log-multi-machine-wrap-2026-09-04.md`
>
> ⚠️ **TWO REPOSITORIES.** Governance by absolute path with `git -C "$GOV"`, never `cd`; commit by EXPLICIT PATHSPEC — this plan's own walk register lives there and will be dirty. ⛔ Commit bellows LAST. Define the roots in the same invocation as their use: `GOV=/Users/marklehn/Developer/eluvian-governance`, `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`, then `test -f "$GOV/MACHINE_SETUP.md"` before proceeding.
>
> **Item 1 — re-derive P1–P10 and HALT on P6's failure.** ⛔ **The HALT condition is P6 alone**: if `_find_newest_sweep_line` no longer returns the FIRST line, the invariant under study has changed and this plan's premise must be re-derived before proceeding. Every other pin mismatch is a finding, not a halt.
>
> **Item 2 — build `tools/wrap_concurrency_census.py`.** ⛔ **Import `wrap_check` and call it; do not re-implement any gate.** ⛔ **Run it against SCRATCH COPIES of the baton only** — never against the live `shop_next_session.md`, and never write into `$ELUVIAN_WRAP_ROOT`.
>
> ⚠️ **POSITIVE CONTROL before any census run:** call `_find_newest_sweep_line` on a baton copy whose first sweep line is known, and confirm it returns that line. A parser believed without a known-good input is how three published positions went wrong on the `qa_steps` question.
>
> **Item 3 — Q1: the write census**, derived from the last four wrap commits, each path classified machine-local or SHARED.
>
> **Item 4 — Q2: the seven-gate table**, invariant scope per gate, survivors reported as prominently as breakers.
>
> **Item 5 — Q3: reproduce or refute the contradiction** on a scratch baton, running `wrap_check` at each step.
>
> **Item 6 — Q4: the fetch-to-push window**, measured over recent wraps.
>
> **Item 7 — Q5: the three documents' clauses and their silences**, quoted.
>
> **Item 8 — Q6: the two-machine-wrap day count**, and a LOSS check per occurrence.
>
> **Item 9 — Q7: candidates priced**, each tagged T-6 or not. ⛔ Choose none.
>
> **Item 10 — deposit the research note** with a coverage statement naming anything unassessable.
>
> **Item 11 — dev-log**, recording that the question was asked by the CEO after an incident that had already occurred unnoticed mid-cycle.
>
> **Item 12 — commit** (message tagged with the plan id); record `numstat` — **TWO commits in two repos**: 1 governance, 2 bellows.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named here, overridden by the Planner with reference to this note — the 100032/100034/100036 precedent. The override act is `tools/clear_plan.py --override-gate <id> 1 qa_test_result --ref <committed path>`; ⛔ the justification is committed BEFORE the override, which is write-once.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/multi-machine-wrap-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-multi-machine-wrap-2026-09-04.md`
> - `/Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md`
>
> ⛔ **`MACHINE_SETUP.md` is listed in Deposits as a READ-ONLY anchor so the depositor's fallback derives `shop-infra` and this plan HOLDS for a human release.** Measured on a sibling plan the same day: a Deposits block containing only paths under `knowledge/` yields `app-feature`, which AUTO-CLEARS. ⛔ **This plan writes NOTHING to `MACHINE_SETUP.md`** — see "What this decides".
>
> **Post-conditions:** every wrap-written path classified machine-local or shared; all seven gates classified with survivors named; Q3 reproduced or refuted with `wrap_check` output at each step; the fetch-to-push window measured; each document's silences named; the two-machine day count with a per-occurrence loss check; all four candidates priced and tagged for tier; ⛔ **no recommendation and no doctrine edit anywhere** — it prices, it does not choose.
