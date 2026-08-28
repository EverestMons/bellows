# bellows — diagnostic: the Cycle Manifest stanza is MANDATED by doctrine and OPTIONAL at the gate — measure the gap, classify every non-compliant plan, and exercise a presence predicate before anyone writes one

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** shop_FORWARD row 4 (the machine-readable fired-list row, annotated 2026-08-27 with the measurements below); DC v2.12's §3 mandate of the ten-field `## Cycle Manifest` stanza; `scripts/plan_lint.py` (f-stanza) at HEAD; `scripts/cycle_check.py` `emit_manifest` at HEAD. Authored from the Planner's 2026-08-27 measurement pass — every pin below is RE-DERIVED by the agent, never inherited.

## Why this exists

DC v2.12 **mandates** the `## Cycle Manifest` stanza. The gate that reads it does not require it to exist: `plan_lint`'s (f-stanza) check is annotated `presence-optional` in its own source and its whole body sits behind `if manifest_m:`, so a plan that simply omits the `## Cycle Manifest` heading is not checked at all — it passes silently. The Planner measured 41 of 115 cycle-running plans since the mandate carrying no stanza, with nothing ever warning. ⚠️ **And absence is not merely unchecked — it silently DISABLES a guard.** `depositor.py:173` holds on `class_mismatch` only `if declared_class and declared_class != assigned_class`; with no stanza `declared_class` is `None`, so a stanza-less plan cannot be caught declaring the wrong class, and `_parse_plan` falls back from Path A (manifest) to Path B (legacy Deposits/Scope) without saying so. Meanwhile `tools/clear_plan.py:138` REFUSES on that same missing `class:` line ("refuse, never guess"). Two consumers, opposite behavior on one missing datum.

This is the same silent-skip shape just diagnosed on `plan_lint` (l), and it matters right now because the proposed row-4 build was going to ADD a required field (`triggers:`) to this stanza. A field added to a presence-optional stanza inherits the stanza's silent skip: omit the heading, omit the field, hear nothing. **The premise that "the stanza already makes absence loud" was recorded, tested, and falsified in one session** — this diagnostic exists so the executable that follows is built on a measured predicate instead of a second wrong one.

## What this plan does NOT do

- **It writes NO code.** One research deposit. No change to `plan_lint.py`, `cycle_check.py`, `DRAFTING_CYCLE.md`, or any register. The presence-required flip is a LATER executable and a T2 (gate edit + doctrine surface); this plan only measures and proposes.
- **It does not decide the fork.** Q5 produces an exercised predicate and its false-positive population; choosing WARN-vs-FAIL and authored-vs-hybrid stays with the CEO.
- **It does not round a legitimate absence up to non-compliance.** Q3 is the whole point: a plan that never reached BAR_MET has no stanza to emit, and counting it as drift would manufacture a defect.

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each — yours supersede and you say so.** Every date below is a FIXED LITERAL.

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | (f-stanza) is presence-optional | `scripts/plan_lint.py:508` comment reads `(f-stanza) Cycle Manifest stanza shape check (WARN-only, presence-optional)`; `:509` `manifest_m = re.search(r'^## Cycle Manifest\s*$', ...)`; `:510` `if manifest_m:` guards the entire check | read `:505-545`; `/usr/bin/grep -nF "presence-optional" scripts/plan_lint.py` |
| P2 | the silent skip, with a positive control | On `knowledge/decisions/Done/executable-579.md` (a BELLOWS plan — it must exist in your own worktree): unmodified → **0** `(f)` WARNs; delete the `coherence:` line → **1** WARN naming `coherence` (the POSITIVE CONTROL — the probe fires); rename the `## Cycle Manifest` heading → **0** WARNs | reconstruct all three arms in /tmp; paste raw output + `$?` for each |
| P3 | `_STANZA_REQUIRED` | ten fields at `scripts/plan_lint.py:532-535`: tier, target, class, reads, writes, open_forks, walks, yields, validation, coherence | read the list; cite the line span |
| P4 | corpus census | 246 plans created on/after 2026-08-07 with resolvable Done files; **74** carry a `## Cycle Manifest` stanza | re-derive the plan set by Q-2's route (each plan's own `**Date:**` header across the six Done directories — NOT `lifecycle.db`, which is absent from your worktree); `/usr/bin/grep -lE '^## Cycle Manifest$'` over those Done files |
| P5 | the compliance gap | Since the v2.12 mandate (2026-08-19): **119** plans; **115** carry a `## Drafting Cycle` block; **74** of those carry the stanza; **41 (36%)** do not. ⚠️ **P4's 74 and P5's 74 are almost certainly the SAME 74 plans, not two independent measurements** — the stanza did not exist before v2.12, so every stanza-carrying plan in the wider set should also be in this one. Do not present them as corroborating. CHECK it: if the two sets differ, a stanza predates its own mandate and that is a finding | same census, restricted to plans dated on/after 2026-08-19; report the set difference against P4 explicitly |
| P6 | how the stanza reaches a plan | `scripts/cycle_check.py` `emit_manifest` appears to `print(...)` the ten fields to stdout and `return 0` — the Planner believes it does NOT write into the plan file, making the transcription MANUAL. ⚠️ **This pin is the least verified of the six — treat it as a hypothesis and settle it by running the tool, not by reading it** | run `python3 scripts/cycle_check.py --emit-manifest <a Done plan copied to /tmp>`; diff the copy before/after |

## MUST-PRESERVE

- ⚠️ **READ-ONLY except the single deposit.** No repo file modified. Every fixture, mutation and scratch copy lives under `/tmp` in your sandbox, never in the worktree. You are measuring a live gate — do not edit the gate to observe it.
- ⚠️ **`/usr/bin/grep` for ALL probes** (the shop grep shim is ugrep; `-F` unless a regex is stated); a zero-match exits 1 — never `&&`-chain a probe; an errored probe is the instrument, not an absence.
- ⚠️ **Every absence claim carries a POSITIVE CONTROL** — a run of the same instrument that DOES find a planted instance. P2's middle arm is the model: it exists to prove the probe can fire before any 0 is believed.
- ⚠️ **Every count carries its DENOMINATOR and the predicate that produced it.** "41 missing" is meaningless without "of 115 cycle-running plans since 2026-08-19". A bare percentage is not a finding.
- ⚠️ **Worktree dispatch:** bellows files by repo-relative path in YOUR worktree; shop-root docs (`/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md`, `PLANNER_TEMPLATE.md`) and other projects' `knowledge/decisions/` by ABSOLUTE path, read-only.
- ⚠️ **`lifecycle.db` IS NOT IN YOUR WORKTREE — it is gitignored (`.gitignore:15` `lifecycle.db*`).** Do not plan around reading it from a repo-relative path; that path does not exist for you. **Derive the plan set from the plans themselves** — each Done plan carries its own `**Date:**` header, which is in your worktree and needs no database. If you additionally want the DB as a cross-check, it is READ-ONLY and ABSOLUTE at `/Users/marklehn/Developer/GitHub/bellows/lifecycle.db`, opened only via a `file:...?mode=ro` URI (the daemon is writing it live; never write, migrate, or VACUUM). ⚠️ If the two keys disagree for any plan, that disagreement is a FINDING — report it rather than silently preferring one.
- ⚠️ **No pytest run is required or wanted** — every row here is a measurement over plan TEXT and live tool output, not a suite result. If you believe a row needs the suite, that is a finding: say so rather than running it.

## STEP 1 — DIAGNOSTIC: six questions, one exercised predicate

**Role:** DIAGNOSTIC.

Produce `knowledge/research/stanza-presence-gate-gap-2026-08-27.md` (repo-relative in your worktree) with one section per question. Each section: (a) re-derived pins with file:line; (b) the instrument run(s) with RAW output; (c) an explicit verdict. End with the recommendation table Q5 produces.

**Q-1 — Is the skip real?** Re-derive P1 and P2. Reconstruct all three arms of P2 in /tmp against a COPY of `knowledge/decisions/Done/executable-579.md` (copy it out; never mutate the tracked file). Report the three `(f)` WARN counts verbatim with exit codes. ⚠️ The middle arm is the positive control and it is MANDATORY: if deleting a required field does NOT produce a WARN, your instrument is broken and the other two numbers are void — say so and stop the row. Verdict: does omitting the `## Cycle Manifest` heading silence the check entirely?

**Q-2 — How wide is the gap?** Re-derive P4 and P5. State your plan set and how you resolved it. ⚠️ **SCOPE — read this before you count.** The census spans **every project, not just bellows**, so a bellows-only count will be far smaller than the Planner's and is NOT a disagreement, just a different question. Only bellows is repo-relative to you; the others are ABSOLUTE and read-only: `/Users/marklehn/Developer/GitHub/{invoice-pulse,governance,lessons-forge,anvil,forge}/knowledge/decisions/Done/`. **Primary route: the `**Date:**` header inside each of those `Done/*.md`** — no database needed. (The Planner used `lifecycle.db` `created_at` joined to Done paths and had 30 of 276 post-08-07 plans fail to resolve; you are on a different key, so report YOUR OWN denominator and unresolved count and do not inherit 30.) Give both censuses with denominators. **Enumerate the missing plans — by id where the filename carries one (`executable-<id>.md`, `diagnostic-<id>.md`), otherwise by FILENAME.** ⚠️ Most Done files are slug-named, not id-named (measured 2026-08-27 over the full corpus: 353 of 526 in bellows, 656 of 845 in invoice-pulse), so an id-only enumeration will silently drop most of them. The list is the input to Q-3, so a count alone fails this row.

**Q-3 — Are the plans Q-2 enumerated actually non-compliant?** (The Planner's count was 41; yours governs, and Q-3's heading deliberately does not repeat it.) THE DECIDING QUESTION. For each plan Q-2 enumerated, classify why no stanza exists, using evidence in the plan text: (a) **LEGITIMATE — never closed at BAR_MET** (a RE-DRAFT, a halt, a cycle that ended without close: the stanza is emitted AT BAR_MET, so there was nothing to emit); (b) **LEGITIMATE — out of scope** (T0, doc-only, or fixture-only plan that ran no real cycle despite carrying the heading); (c) **DRIFT** (the cycle closed and the stanza was simply not pasted). Give the three-way split with counts, and name the evidence token you classified each on. ⚠️ Do not classify from the plan's Tier line alone — a judged stop and a RE-DRAFT can look identical there; read the Closing line. If a plan is genuinely ambiguous, a fourth bucket UNCLEAR is an honest answer and better than a forced call.

**Q-4 — Where does the stanza come from?** Settle P6 by RUNNING it, not reading it. Copy a Done plan to /tmp, run `python3 scripts/cycle_check.py --emit-manifest /tmp/<copy>.md`, capture stdout and `$?`, then `diff` the copy against its original. Verdict: does the tool WRITE the stanza into the plan, or only PRINT it for a human to paste? If print-only, state plainly that the stanza's path into a plan is manual transcription, and that this — not authorial laziness — is the drift surface a presence check would be policing. Also record whether anything in the repo calls `--emit-manifest` automatically (`/usr/bin/grep -rn --exclude-dir=.git -F "emit-manifest" .` in the worktree).

**Q-5 — Propose and EXERCISE a presence predicate.** The Planner's candidate: *warn when a plan contains a `## Drafting Cycle` block but no `## Cycle Manifest` stanza.* Implement it as a THROWAWAY script in /tmp (never in `scripts/`) and run it over the full post-2026-08-19 corpus — **the SAME all-projects scope Q-2 defines, not your worktree alone.** A predicate exercised on bellows only has measured one fifth of the population and its false-positive count means nothing. Report: how many plans it flags; how that set compares to Q-3's DRIFT bucket; and every FALSE POSITIVE (a plan it flags that Q-3 classified LEGITIMATE). ⚠️ A predicate whose flag set is not close to the DRIFT bucket is the wrong predicate — if that is what you measure, say so and propose a better one with its own measured flag set. Then estimate the FUTURE warn rate honestly: `plan_lint` is a PRE-DEPOSIT lint and Done plans are never re-linted, so the historical rate predicts the rate on NEW plans only — state that explicitly so the number is not read as a retro-warning flood.

**Q-6 — What else reads this stanza?** ⚠️ **Two real consumers are ALREADY KNOWN — your job is to VERIFY and EXTEND, not to rediscover.** (i) `depositor.py:238` `_parse_plan` calls `cycle_check.parse_manifest_stanza`, and when the stanza is absent falls back silently to Path B (`gates._extract_plan_required_deposits` / `_extract_plan_scope`); worse, `depositor.py:173` gates the `class_mismatch` hold on `if declared_class and ...`, so a stanza-less plan skips that guard entirely. (ii) `tools/clear_plan.py:138` fails closed on a missing `class:` line. **Confirm both by reading the current code and, where runnable, by running them**, then find any others: `/usr/bin/grep -rn --exclude-dir=.git --exclude-dir=knowledge -F "Cycle Manifest" .` plus `/usr/bin/grep -rn --exclude-dir=.git -F "parse_manifest_stanza" .`. ⚠️ A heading grep cannot see a consumer that reads stanza FIELDS without naming the heading — say explicitly how you searched for that class. For each hit say whether it READS stanza fields or merely mentions the heading. ⚠️ Reading a consumer's source is a hypothesis; where a consumer is runnable, RUN it. This row exists because a presence flip changes what those consumers see, and an unlisted consumer is how a flip breaks something nobody predicted.

**Deposits:**
- `knowledge/research/stanza-presence-gate-gap-2026-08-27.md`

**Scope:**
- `knowledge/research/stanza-presence-gate-gap-2026-08-27.md`

**Commit:** `cd "$(git rev-parse --show-toplevel)" && git add knowledge/research/stanza-presence-gate-gap-2026-08-27.md && git commit -m "[<id from your plan filename>] diag: Cycle Manifest stanza presence gap — mandated by DC v2.12, optional at the gate" -- knowledge/research/stanza-presence-gate-gap-2026-08-27.md` in YOUR worktree.

## Drafting Cycle

**Tier:** T1 computed — triggers fired: T-7 (authored-from — the presence-required executable will build on these findings). Read-only, reversible, single deposit, not itself a governance surface, so not T2 and no cold panel; the EXECUTABLE that follows IS T2 (T-6: a `plan_lint` gate edit plus a DC §3 amendment) and carries the panel. Clone framing: structure-clone of `Done/diagnostic-568.md`, the newest same-class plan (read-only single-deposit measurement diagnostic, six-to-seven lettered rows, positive-control discipline); clone-diff run at walk 0 against that parent, against this project's standing rules in `bellows/CLAUDE.md`, and against the parent's closing record.

**Walk register:** `governance/knowledge/research/walk-register-stanza-presence-2026-08-27.md` — ⚠️ **deliberately NOT the parent's location.** `Done/diagnostic-568.md` declares its register under `bellows/knowledge/research/`, which contradicts DC §3 ("committed to `governance/knowledge/research/` regardless of which project the plan targets — the register is a governance record, not a project deliverable"). Measured 2026-08-27: 133 registers sit in governance, 22 in bellows. This plan follows the doctrine, not the clone; cloning the parent here would have reproduced its violation.

**Walks:** walk 0 pinned (the Planner's measurement pass above, plus two consumer dry-runs: `Depositor._assign_class` on this write set returns `read-only`, and the `gates.py` `qa_test_result` evidence picker is N/A — no QA step, no `.txt` deposit); **walks 1–7 complete**, genuine sequential five-lens passes — see the register.

**Direction verdict (after walk 1): PROCEED** — the shape (measure, classify, propose a predicate, decide nothing) survived all five lenses; all four walk-1 findings were instruction- or record-class, none direction-class.
- Weak spots:          w1 1 folded (instruction 1 / record 0); w2 2 folded (instruction 2 / record 0); w3 dry; w4 1 folded (instruction 1 / record 0); w5 dry; w6 dry; w7 dry
- Destruction:         w1 dry; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry; w7 dry
- Vulnerabilities:     w1 1 folded (instruction 1 / record 0); w2 1 folded (instruction 1 / record 0); w3 dry; w4 1 folded (instruction 1 / record 0); w5 dry; w6 dry; w7 dry
- Integration-record:  w1 1 folded (instruction 0 / record 1); w2 1 folded (instruction 0 / record 1); w3 1 folded (instruction 1 / record 0); w4 dry; w5 dry; w6 1 folded (instruction 1 / record 0); w7 dry
- ACID:                w1 1 folded (instruction 1 / record 0); w2 dry; w3 dry; w4 1 folded (instruction 1 / record 0); w5 1 folded (instruction 1 / record 0); w6 dry; w7 dry

**Cold panel: NOT convened, decided with reasoning** — T1 read-only single-deposit diagnostic; the E-family rule and the `Done/diagnostic-568.md` precedent. The T2 executable this plan feeds carries the panel instead.
**Closing:** **walk 7 met the bar — all five lenses dry, instruction 0 / record 0, no restructuring fold.** Instruction series across walks 1–7: **3 → 3 → 1 → 3 → 1 → 1 → 0**, NOT monotonic. Stated plainly because it matters: walk 3's yield of 1 was a narrow examination axis, not convergence — walk 4 changed axis and returned 3, including the finding that the manifest `reads:` under-declaration blinds a depositor guard. 14 findings total, instruction 12 / record 2; fold-introduced 6 of 14. ⚠️ **Residue, enumerated rather than waved:** the closing re-read corrected the register's own walk-1 totals, which had counted a DRY Destruction row as a finding (5/instruction 3/record 2 → 4/instruction 3/record 1); the correction is recorded in the register beside the original. Close is MANUAL (`auto_close: false`).

## Cycle Manifest
tier: T1
target: knowledge/research/stanza-presence-gate-gap-2026-08-27.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/GitHub/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/GitHub/bellows/depositor.py, /Users/marklehn/Developer/GitHub/bellows/gates.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db, /Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/, /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions/Done/, /Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/Done/, /Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/, /Users/marklehn/Developer/GitHub/anvil/knowledge/decisions/Done/, /Users/marklehn/Developer/GitHub/forge/knowledge/decisions/Done/
writes: knowledge/research/stanza-presence-gate-gap-2026-08-27.md
open_forks: Q-5's predicate shape if the flag set diverges from Q-3's DRIFT bucket; WARN-vs-FAIL for the presence flip; authored-vs-hybrid population of a later triggers field (shop_FORWARD row 4)
walks: 7
yields: 3, 3, 1, 3, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

This step is DIAGNOSTIC-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
