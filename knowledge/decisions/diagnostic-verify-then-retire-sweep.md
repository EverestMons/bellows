# bellows — diagnostic: the batch-4 verify-then-retire sweep — seven enforcement surfaces measured once each, licensing eight memory retirements (or routing their residues)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** the CEO-approved batch-4 work order (baton, 2026-08-26): "(1) the verify-then-retire sweep (~8 rows whose enforcement already exists ... one verification pass each, then pointer retirements with `class: stale`)"; the 08-21 audit's CODE rows marked "verify then RETIRE" (`governance/knowledge/research/memory-to-system-audit-2026-08-21.md` L127, L133, L140, L142, L154, L156, L162, L163, L167); the Planner's authoring-day scout (every pin below measured 2026-08-26, agent re-derives).

## Why this exists

Eight memory entries warn about behaviors whose mechanical enforcement has since shipped (cycle_check, fold_check, plan_lint, wrap_check, the rule-20 gate, propagation_check). The audit ruled each "verify then RETIRE." A retirement without a measured verification pass is exactly the fabricated-close class this shop mechanized against — so the sweep runs ONE honest verification per row, records raw evidence, and classifies each row COVERED (retire to a `class: stale` pointer) or PARTIAL (name the residue and route it to batch item 2/3/4). The PST §6 row (`panel-seats-report-incrementally`) is already retired (batch 3) and is out of scope here.

## What this plan does NOT do

- **It writes NO code and NO memory files.** One research deposit. The retirements are the Planner's own close-time act (daemon agents are sandbox-denied on `~/.claude`; the pointers carry `class: stale` under the 562 wrap gate).
- **It does not decide close calls silently** — a PARTIAL verdict names the exact uncovered case and the route; it never rounds up to COVERED.

## Numbers discipline

⚠️ **Measured 2026-08-26 by the Planner; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | yield-rising escalation | `scripts/cycle_check.py:394` returns `"ESCALATE:yield-rising", 1`; tests reference it in `tests/test_cycle_check.py` | read the function; `/usr/bin/grep -nF "yield-rising"` both files |
| P2 | substrate enforcement | cycle_check: `:383` `ESCALATE:uncommitted-walk`, `:377-381` `assert-fail:1/2/3`, `:262` register PASS/FAIL, `:482` walks-with-rows coverage; DC §2 L40 makes substrate-presence a HARD gate on auto-advance AND auto-close; DC changelog 2.13 records the three cadence memories rewritten to match | read both; grep the tokens |
| P3 | fold_check | `scripts/fold_check.py` present; DC §2.7 L145 makes the fold the unit carrying a post-condition; `tests/test_fold_check.py` present. OPEN: whether the tool flags a CLAIMED fold that changed nothing (the landed-nothing case) | read the tool's contract; construct the case live |
| P4 | wrap_check ritual arms | `hooks/eluvian/wrap_check.py` docstring L23-27 names the 4-repo ritual; arms `[1/project]` ~L160, `[2/bellows]` ~L177, `[3/root]` ~L194, `[3b/lessons]` ~L206, `[4/memory]` (the 562 class gate after `m_dirty = porcelain(MEMORY)`); six `tests/test_wrap_*.py` files | read; grep the arm tags |
| P5 | plan_lint (e) | `scripts/plan_lint.py:260-269`; MEASURED: an H3 `### Step` fixture WITH `qa_steps` → FAIL (e) + FAIL (c), exit 1; the same fixture WITHOUT `qa_steps` → exit 0 clean (residual hole); PT L1603: "no gate fires on step composition" | re-run both fixtures (given verbatim in R-5) |
| P6 | rule-20 enforcement | `gates.py:582` `_gate_rule_20_self_check`; plan_lint (c) `:286-309`; ten `rule_20` tests in `tests/test_gates.py`; `RULE_20_SELF_CHECK_BLOCK.md` at shop root; PT cites "Rule 60 — form by plan class" (L1459) | grep + read; verify Rule 60 exists in PT by that number |
| P7 | propagation_check | `scripts/propagation_check.py` present; DC §2.7 L192 sweep trigger ("pre-existing-class yield reaches 0 AND total yield did not fall") + DC §5 L291 freeze run; NO test file exists (positive control required for any live run) | ls tests/; live runs in R-7 |

## MUST-PRESERVE

- ⚠️ **READ-ONLY except the single deposit.** No repo file modified; fixtures and scratch copies live under `/tmp` in your sandbox, never in the worktree.
- ⚠️ **`/usr/bin/grep` for ALL probes (the shop grep shim is ugrep; `-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe; an errored probe is the instrument, not an absence.**
- ⚠️ **Every absence claim carries a POSITIVE CONTROL** (a run of the same instrument that DOES find a planted instance). Every claim cites file:line in CURRENT code. EVERY DATE IS A FIXED LITERAL.
- ⚠️ **Worktree dispatch:** repo files by repo-relative path in YOUR worktree; shop-root docs (`PLANNER_TEMPLATE.md`, `DRAFTING_CYCLE.md`, the audit) and the memory dir by ABSOLUTE path, read-only.
- ⚠️ **Targeted pytest only** (the named files below) — this is a diagnostic, not QA; record every summary line verbatim.

## STEP 1 — DIAGNOSTIC: seven verification passes, one license table

**Role:** DIAGNOSTIC.

Produce `knowledge/research/verify-then-retire-sweep-2026-08-26.md` (repo-relative in your worktree) with one section per row. Each section: (a) the re-derived code pins with file:line; (b) the instrument run(s) with raw output; (c) a one-word verdict **COVERED** or **PARTIAL**, and for PARTIAL the exact uncovered case + the route (batch item 2 depositor cluster / item 3 plan_lint cluster / item 4 singleton / new fork). End with the license table: row → memory entry → verdict → licensed act.

**R-1 — yield-rising (memory `rising-yield-means-split-not-walk`).** Re-derive P1. Run `python3 -m pytest tests/test_cycle_check.py -q 2>&1 | tail -3` and paste the summary. Confirm the DC §2.8 cut/target triggers name rising yield (grep DC — absolute path — for the trigger prose; cite line). Verdict: does the mechanical escalation + the doctrine trigger cover the memory's warning (rising yield ⇒ stop walking, consider splitting)? The memory's split-on-the-risk-boundary REMEDY is judgment prose — state where it survives (DC §2.8 trigger clause) so the pointer can cite it.

**R-2 — register substrate (memories `fabricated-close-reaches-execution-register-is-the-guard`, `no-fabricated-drafting-cycle`).** Re-derive P2 (all five sites). Same pytest run as R-1 covers the substrate asserts — name which tests hit them (`/usr/bin/grep -nE "uncommitted|substrate|register" tests/test_cycle_check.py`, list matching test names). Confirm DC §2 L40's substrate clause states BOTH: substrate verified DIRECTLY (not via cycle_check's verdict) AND substrate-less close is MANUAL. Verdict per memory: is a fabricated close now mechanically distinguishable wherever auto-advance/auto-close would act, with the substrate-less arm falling back to manual? Planner-attested fact (the memory files live outside your sandbox — do not attempt to read them; record this as attested, not self-verified): both entries already carry a "MECHANIZED by the DC v2.13 §2 auto-advance cadence" header, and DC changelog 2.13 records the paired rewrite — cite the CHANGELOG line, which IS in your reach.

**R-3 — fold_check (memory `claimed-fold-may-never-have-landed`).** Read `scripts/fold_check.py` end-to-end and state its ACTUAL contract (what it compares, when it fails). Run `python3 -m pytest tests/test_fold_check.py -q 2>&1 | tail -3`. Then construct the LANDED-NOTHING case live in /tmp: baseline a copy of any Done plan, change NOTHING, run the tool's check mode, record verbatim what it reports. The memory's core claim is "a fold can be recorded and exist nowhere" — classify honestly: does fold_check DETECT a claimed-but-absent fold, or does it only detect UNINTENDED changes (a no-op fold passing silently)? If the latter, the verdict is PARTIAL: name the uncovered half (the record-vs-artifact attestation, and the memory's second trap — probes must be EARNABLE against the pre-edit file) and propose the route (plan_lint cluster WARN, a fold_check mode, or KEEP the memory — say which and why).

**R-4 — wrap ritual (memory `eluvian-session-wrap-ritual`).** Re-derive P4 (all five arms — cite each arm's line). Run `python3 -m pytest tests/test_wrap_hooks.py tests/test_wrap_3b_keyed.py tests/test_wrap_memory_class_gate.py tests/test_wrap_sentinel.py tests/test_wrap_receipts.py tests/test_wrap_r2_registry.py -q 2>&1 | tail -3`. Map each ritual step to the wrap_check arm that enforces it — a table, one row per step, no unmapped step left silent. The ritual's steps, INLINED here because the memory file lives outside your sandbox (the Planner transcribed them 2026-08-26): (1) project repos — commit completed plan files in `knowledge/decisions/Done/`; (2) bellows — commit + push consumed `verdicts/resolved/` files; (3) governance root — refresh + commit the baton, bump the bellows gitlink, push; (3b) BEFORE the baton refresh, the transferable-lessons sweep (LESSONS.md append + memory-repo lessons), recorded as a `Lessons-swept:` baton line; (4) memory repo — commit + push if touched; and push each repo. The memory is a HOW-TO (type: reference); enforcement ≠ instruction — state where the instruction now lives (the `/wrap` skill + wrap_check's own docstring) so the pointer aims at an in-path home. Any ritual step with NO enforcing arm and NO in-path doc home → PARTIAL with the route.

**R-5 — step headers (memory `bellows-step-headers-h2-required`).** Construct BOTH fixtures in /tmp from this SPEC (not from a paste — write real markdown): line 1 an H1 title reading `test — executable: probe`; line 3 the bold header `**Date:** 2026-08-26 | **Project:** bellows | **qa_steps:** 2`; then two H3 step sections headed `### Step 1 — DEV: thing` and `### Step 2 — QA: check`, each with one body line. Fixture B is byte-identical except its header line omits the `**qa_steps:** 2` field and the ` | ` separator BEFORE it (the field is last on the line; B's header ends at `**Project:** bellows`). Run `python3 scripts/plan_lint.py <fixture>` on each; paste raw output + `$?`. Expected from the Planner's measurement: A → FAIL (e) exit 1; B → exit 0. Then the census: `/usr/bin/grep -rlE '^### Step' knowledge/decisions/` in the bellows worktree AND (absolute, read-only) in `/Users/marklehn/Developer/GitHub/{governance,invoice-pulse,lessons-forge}/knowledge/decisions/` — how many real deposited plans ever carried H3 steps (the memory's incident, plan 434, may appear; count and name them). Verdict: PARTIAL is the Planner-predicted outcome (the qa_steps-less arm is uncovered and PT L1603 says no gate fires on step composition) — confirm or refute, and state the route: the batch-item-3 plan_lint cluster gains "(e) extension: FAIL any `executable-*` plan parsing zero `^## STEP ` headers regardless of qa_steps" (or a better shape you argue for). The memory retires WITH that cluster, not before.

**R-6 — rule-20 (memory `rule-20-form-by-plan-class`).** Re-derive P6. Run `python3 -m pytest tests/test_gates.py -k "rule_20" -q 2>&1 | tail -3`. Verify `RULE_20_SELF_CHECK_BLOCK.md` exists at the shop root and PT "Rule 60" exists by that number and carries the form-by-plan-class choice (full block + evidence files vs simple banner) — cite PT line numbers. The memory's residual content is the class-choice judgment; if Rule 60's text carries it, verdict COVERED with the pointer aiming at Rule 60 + the block file; if Rule 60 is thinner than the memory (e.g. missing the evidence_dir-from-pwd trap or the unsatisfiable-QA-step trap), verdict PARTIAL naming exactly which clauses lack a doctrine home and the route (a PT edit is a batch-item-4 singleton).

**R-7 — propagation_check (memory `walking-cannot-close-propagation-defects`).** Re-derive P7. Live run 1: `python3 scripts/propagation_check.py knowledge/decisions/Done/executable-563.md` — record exit + last lines. Live run 2 (the POSITIVE control, mandatory): FIRST read `scripts/propagation_check.py`'s detectors and construct a /tmp fixture in exactly the representation its restated-value detector matches (derive the planted disagreement from the tool's own patterns — a probe modeled on a guess instead of the instrument's representation returns a confident false absence); the tool must FIND the plant; record the finding verbatim. If the positive control does not fire, the absence claims are void — say so and mark the row PARTIAL (instrument unproven). Confirm the DC sweep trigger (§2.7 L192) matches the memory's trigger verbatim ("pre-existing-class yield is 0 AND total yield did not fall") and that §5 L291 mandates the freeze run. Check whether DC carries the memory's ⚠️ never-substitute-a-symbol-inside-a-code-fence caveat (`/usr/bin/grep -nF "fence" + context` on DC, absolute path); if absent, that single clause is the residue — name it for the pointer text rather than blocking retirement, and say so explicitly.

**Post-conditions:** every P-pin re-derived or superseded with the measurement shown; every absence claim paired with its positive control; every row carries exactly one verdict word; the license table enumerates all eight memories (both R-2 memories; R-5's deferred-to-cluster row included with its route) with the licensed act per row.

**Deposits:**
- `knowledge/research/verify-then-retire-sweep-2026-08-26.md`

**Scope:**
- `knowledge/research/verify-then-retire-sweep-2026-08-26.md`

**Commit:** `cd "$(git rev-parse --show-toplevel)" && git add knowledge/research/verify-then-retire-sweep-2026-08-26.md && git commit -m "[<id from your plan filename>] diag: batch-4 verify-then-retire sweep — seven surfaces measured, eight retirements licensed or routed" -- knowledge/research/verify-then-retire-sweep-2026-08-26.md` in YOUR worktree.

## Drafting Cycle

**Tier:** T1 computed — read-only single-deposit diagnostic.

**Walk register:** `bellows/knowledge/research/walk-register-verify-then-retire-sweep-2026-08-26.md`

**Walks:** walk 0 pinned (the scout's measurements above); **walks 1–3 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the sweep's shape (per-row honest verdicts, routes for residues) survived contact with all three walk-1 findings; none was direction-class.
- Weak spots:          w1 1 folded (instruction 1 / record 0) — fixture encoding; w2 1 folded (instruction 1 / record 0) — pipe direction; w3 dry
- Destruction:         w1 dry; w2 dry; w3 dry
- Vulnerabilities:     w1 2 folded (instruction 2 / record 0) — sandbox read + positive-control representation; w2 1 folded (instruction 1 / record 0) — second sandbox-read site; w3 dry
- Integration-record:  w1 dry; w2 dry; w3 dry
- ACID:                w1 dry; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — read-only single-deposit diagnostic; the E-family rule (515-528/531 precedent).
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block: run_check cycle BAR_MET (branched-on), run_check lint at the lintmirror path (branched-on), run_check register CONFORMANT (branched-on), propagation N/A (single-declaration pins; the deposit doc is the agent's).
**Closing:** **walk 3 met the bar — all five lenses dry, instruction 0 / record 0, no restructuring fold.** Instruction series **3 → 2 → 0** (falling). Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: knowledge/research/verify-then-retire-sweep-2026-08-26.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/GitHub/bellows/scripts/fold_check.py, /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/GitHub/bellows/scripts/propagation_check.py, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/GitHub/bellows/gates.py, /Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md, /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md, /Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md
writes: knowledge/research/verify-then-retire-sweep-2026-08-26.md
open_forks: R-3's route if fold_check is PARTIAL; R-5's (e) extension shape (feeds batch item 3); R-6's PT-edit singleton if Rule 60 is thin
walks: 3
yields: 3, 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x2
coherence: N/A

## Rule 20 — QA Self-Check Block

This step is DIAGNOSTIC-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
