# bellows — executable: `cycle_check` — BAR_MET refuses a Cycle Manifest whose `validation:` line lacks a key the emitter writes, because DC:253 declares four fields COMPUTED and never hand-typed and nothing has ever checked it

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_cycle_check.py` + a new focused sibling) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100032.md` (the drafting-battery-cost diagnostic) and `DRAFTING_CYCLE.md:253`, whose trust taxonomy this enforces. Clone origin: `Done/executable-100025.md` (2026-09-02 — the newest shipped plan that WRITES `scripts/cycle_check.py`, tiered T1, warn/gate change with a kill map).

## What this changes

⛔ **One conditional in `cycle_check`'s BAR_MET decision.** If a plan carries a `## Cycle Manifest` stanza whose `validation:` line omits any key the emitter writes, the verdict is `CONTINUE`, not `BAR_MET`. Nothing else.

## Why this exists

`DRAFTING_CYCLE.md:253` states a **provenance** invariant:

> **Trust taxonomy:** four fields are COMPUTED and never hand-typed (`walks`, `yields`, `validation`, `coherence` — the emitter derives them from the cycle's walk data, checker verdicts, and register state)

**One key of the four is checked; the other three and the key set itself are not.** ⚠️ v0 of this plan said *"nothing has ever checked it"* — an overstatement, corrected at walk 1. `depositor.py:515-524` DOES re-validate: it re-runs `cycle_check`, compares the stored `cycle_check=` value against the fresh verdict, and HOLDs on `validation_mismatch`. **That is this plan's pattern, already shipped, for one key.** What is unchecked is (a) the other three keys' values and (b) whether the keys are present at all. ⛔ **And `plan_lint` (f) checks one key too** — `:613` WARNs when `cycle_check=` is absent from `validation:`. So THREE surfaces already inspect this line, each for the single key `cycle_check`: (f) for its presence, the depositor for its value, and nothing at all for the other three. Measured on a hand-typed manifest carrying `cycle_check=` but not `propagation_check=`, `plan_lint` exits **0** and (f) emits no line — because the one key it looks for is there.

⚠️ **Measured, and the violation is the author's:** plans closed after the emitter gained `propagation_check` (`c39927c`, 2026-09-02 17:14) are 5 compliant / 3 not. Two of the three are the transition window — `100023` IS the plan that made the change, `100024` closed 22 minutes later. **`diagnostic-100032` closed a full day later with a hand-typed `validation:` line missing the key.** The rule was explicit, the tool existed and worked, and the author typed the field anyway. That is the case for a gate rather than against one.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the invariant | `DRAFTING_CYCLE.md:253` — four fields COMPUTED and "never hand-typed" | `sed -n '253p' DRAFTING_CYCLE.md` |
| P2 | ⛔ the gap, stated precisely | `plan_lint` on `Done/diagnostic-100032.md` → **exit 0**, no `(f)` line emitted; its manifest has all ten fields and only a KEY inside `validation:` is missing. ⚠️ **NOT unchecked in general:** `depositor.py:515-524` re-validates `cycle_check=`'s VALUE at deposit and holds on `validation_mismatch`. The gap is the other three keys and the key set's presence | run `plan_lint` on that file and read `depositor.py:505-525` |
| P3 | the emitter's key set | `cycle_check.py:658` builds `validation:` as `cycle_check=…, plan_lint=…, fold_check=…, propagation_check=…` — **four keys**, one f-string | read `:658` |
| P4 | ⛔ **the emitter subprocess-runs three checkers** | `emit_manifest` invokes `plan_lint.py` (`:613`), `fold_check.py` (`:628`) and `propagation_check.py` (`:640`) | read `:600-655` |
| P5 | ⛔ **THE PLACEMENT CONSTRAINT, stated precisely** | P4 means any check that INVOKES `--emit-manifest` from `plan_lint` recurses without termination: `plan_lint → cycle_check --emit-manifest → plan_lint → …`. ⚠️ **v0 overstated this as "the check must not live in `plan_lint`" — corrected at walk 2.** The hazard is invoking the EMITTER, not the placement: `plan_lint` check (f) already inspects `validation:` keys at `:613` with no subprocess and no recursion. **The constraint is: never call `--emit-manifest` from a checker the emitter runs** | trace the call graph; read `plan_lint.py:611-614` |
| P6 | the non-recursive placement | `cycle_check.py:502` — `verdict = "CONTINUE" if parsed["has_unparseable"] else "BAR_MET"`, already guarded by `asserts_ok`. Comparing a stored key set against a CONSTANT costs no subprocess and cannot recurse | read `:498-506` |
| P7 | ⛔ **why NOT value equality** | stored and freshly-emitted VALUES legitimately drift after freeze — measured on compliant `Done/executable-100028.md`: `propagation_check` `DIVERGENT:50` stored vs `DIVERGENT:56` fresh, and `fold_check` `PASS` vs `N/A`. A value check false-positives on every closed plan. **Keys do not drift; values do** | emit for that plan and diff |
| P8 | ⛔ **why NOT a bare "four keys" shape rule** | 53 plans legitimately carry three keys — they closed before `c39927c` added the fourth. The predicate must be "the key set the CURRENT emitter writes", not a hardcoded four | count key-sets across `Done/` by close time |
| P9 | positive control | `diagnostic-100032` stored 3 keys vs emitter 4 → must FIRE. `executable-100028`/`100030` stored 4 vs 4 → must NOT fire | compare key sets on those three |
| P10 | tier precedent, measured not paraphrased | four plans that WRITE `scripts/cycle_check.py` were all `cycle_tier: T1` — `100023`, `100025`, `100022`, `100029`; one states "T-6 no (no doctrine, no gate, no script)". The checkers are instruments, not gates under T-6 | grep the tier line in those plans |
| P11 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## What this does NOT do

- ⛔ **It does not add a `plan_lint` check** — but ⚠️ **not because that placement is impossible.** Walk 2 measured that `plan_lint` (f) already inspects `validation:` keys (`:613`) without recursing. The choice rests on ONE argument, stated plainly so a later reader can overturn it with evidence: **(f) emits a WARN, and the 2026-09-03 diagnostic measured that this author ignored standing `plan_lint` WARNs three times in one night.** A gate at BAR_MET cannot be walked past; a fourth WARN can. The predecessor draft that proposed a WARN is WITHDRAWN at `drafts/executable-battery-verdict-declaration.md`.
- ⛔ **It does not compare VALUES** (P7), and does not hardcode four keys (P8).
- ⛔ **It does not move or duplicate the depositor's existing value check.** `depositor.py:515-524` re-validates `cycle_check=` at deposit and must keep doing so. ⚠️ **The depositor was considered as this gate's home and rejected on TIMING, not on fit:** it already parses the manifest, already holds, and cannot recurse — but it fires at DEPOSIT, after the author has stopped working. `cycle_check`'s BAR_MET fires at FREEZE, while the plan is still in hand. Two checks at two moments is the intent, not an oversight; if they ever disagree, the depositor's is authoritative because it re-runs.
- ⛔ **It does not require a manifest to exist.** A plan with no stanza is check (f)'s and the freeze's business; firing here would double-report and train the reader to ignore both.
- **It does not make the check a WARN.** ⚠️ Deliberate: the 2026-09-03 diagnostic measured that this author ignored standing `plan_lint` WARNs three times in one night. A WARN is the delivery mechanism the finding says fails. This gates BAR_MET instead.
- **It does not verify the values were honestly computed.** A key can still be typed. This raises the floor from "silently absent" to "affirmatively false", which is a different and more visible act — it is not a proof of provenance, and must not be described as one.

## MUST-PRESERVE

- ⛔ **The emitter's stdout stays BYTE-IDENTICAL.** Two other surfaces parse the `validation:` line — `plan_lint` (f) at `:611-614` and `depositor` at `:515-524` — and the depositor's comparison is format-sensitive (DC 2.17: it held `executable-100005` on `expected=bar-met got=BAR_MET`). The refactor is internal only.
- ⛔ **`plan_lint` (f)'s guards are ADOPTED, never re-derived.** The falsy and `<declare>` tests at `:612`. Two guards written twice diverge — the class this plan exists for.
- ⛔ **The depositor's existing `cycle_check=` value check is untouched.** It re-runs and is authoritative; this gate is additive and earlier, never a replacement.
- ⛔ **No new subprocess on the normal path.** `cycle_check` runs constantly; the key-set comparison is against a constant and must cost nothing.
- ⛔ **This is a GATE, not a WARN, and must not be downgraded to one by a later tidier.** The reason is measured, not stylistic: the 2026-09-03 diagnostic recorded this author walking past standing `plan_lint` WARNs three times in one night. If a future plan proposes softening it, that plan owes new evidence that WARNs are heeded.
- ⛔ **`known_failures` stays 0.** The canonical checkout's `config.json` failure does not occur in the dispatch worktree; a pre-declared allowance for it would be the recorded Planner failure recurring.

## Drafting Cycle

**Tier:** T1 — T-3 fires (`cycle_check` runs on every machine that drafts). **T-6 does NOT fire**, checked against the trigger as QUOTED (*"Edits doctrine, the template, gates, or specialist contracts"*) and against P10's four measured precedents, one of which states the reading explicitly. ⚠️ **This is the exact reading that inverted twice today** (`wrap_check` as "a wrap gate, not a step gate"); it is grounded in precedent rather than in the author's paraphrase for that reason. T-8 not fired: clone by kind of `Done/executable-100025.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-manifest-provenance-gate-2026-09-03.md`
**Walks:** 5 (walks 0–5 complete). **BAR MET at walk 5.**
- Weak spots:          w1 dry; w2 dry; w3 dry; w4 dry; w5 dry.
- Destruction:         w1 dry; w2 dry; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry.
- Vulnerabilities:     w1 dry; w2 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry.
- Integration-record:  w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0; w3 dry; w4 1 folded — instruction 1 / record 0; w5 dry.
- ACID:                w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 dry; w5 dry.
**⛔ `propagation_check` run AT WALK 0 — DIVERGENT:12, all classified, ZERO real.** Every hit is a pin cited correctly at its use site with its qualifier — `DRAFTING_CYCLE.md:253`/`DC:253` (4), plan ids `100032`/`100025` (7), and `:502` naming the conditional's location (1). Run rather than skipped because this plan is about an unenforced invariant, and shipping it unrun would be the degenerate-exemplar failure its own QA Item 6 forbids.
**⚠️ A design killed at walk 0, recorded so it is not re-proposed.** The author described a `plan_lint` check to the CEO before measuring `emit_manifest`'s call graph. P4/P5: the emitter subprocess-runs `plan_lint.py`, so that placement recurses without termination. The gate moved to `cycle_check`'s own BAR_MET decision, which needs no subprocess and cannot recurse.

**Walk 1 — 2 findings (instruction 2 / record 0); 0 fold-introduced.** ⛔ P2 claimed *"nothing has ever checked it"* and that is false: `depositor.py:515-524` re-validates `cycle_check=`'s value at deposit and holds on `validation_mismatch`. The claim is narrowed to what is actually unchecked — the other three keys and the key set's presence — which STRENGTHENS the licensing case, because the pattern is shipped precedent rather than an invention. And the depositor, having been found, had to be explicitly considered as this gate's home and rejected on TIMING (it fires after the author has stopped working), not on fit.
**Walk 2 — 2 findings (instruction 2 / record 0); 0 fold-introduced.** ⛔ `plan_lint` (f) at `:613` already WARNs when `cycle_check=` is missing from `validation:` — so THREE surfaces inspect this line and all three look only at `cycle_check`. ⛔ And P5's recursion claim was overstated: the hazard is invoking `--emit-manifest`, not the `plan_lint` placement, which (f) demonstrates is safe. The placement choice now rests on one honest argument — a WARN is the delivery mechanism the diagnostic measured as failing on this author — stated so a later reader can overturn it with evidence rather than inherit it as fact.
⚠️ **Blast radius measured on live drafts:** 14 of 21 drafts carrying a stanza would fire, but every one is a SHIPPED plan's draft left on disk (checker-defects, verdict-signal, bellows-bootstrap and so on), not pending work. Of the genuinely never-deposited drafts, `u-qa-predicate-align` already carries all four keys — the fresh-context agent used the emitter. **Live blast radius: zero.**
**Walk 3 — 2 findings (instruction 2 / record 0); 0 fold-introduced.** ⛔ The gate had no case for `<declare>` or an empty `validation:` — `cycle_check` itself writes `<declare>` for un-derived fields (`:675-680`) and `plan_lint` (f) guards both (`:612`); a gate firing on the placeholder would block every plan mid-emission. Tests 6b/6c added and the guards must be ADOPTED from (f), not re-derived, since two guards written twice diverge — the class this plan exists for. ⛔ And Item 3's refactor restructures an f-string that TWO other surfaces parse, one of them case-sensitively (the depositor held `executable-100005` on `bar-met` vs `BAR_MET`); the emitter's stdout must now be proven byte-identical across the change. Test count 8 → 10.
**Walk 4 — 1 finding (instruction 1 / record 0); 0 fold-introduced.** ⛔ The §2.0 clone-diff against `Done/executable-100025.md` was OWED at walk 0 and had not been run. Run at walk 4: the origin carries `MUST-PRESERVE` three times and this plan carried it **zero** — the same element the predecessor plan dropped and its cold panel caught (F4), recurring one plan later. Restored with six clauses, including an explicit prohibition on a later tidier downgrading the gate to a WARN, since that is precisely the change a reader who has not seen the diagnostic would propose as a simplification.
**Walk 5 — DRY, BAR MET.** All six cited lines re-derived (`cycle_check:502`, `:658`; `plan_lint:612`, `:613`; `depositor:515`; `DC:253`); Scope 4 against numstat 4; ten tests declared and numbered.
**⚠️ Cycle shape: SEVEN findings, ZERO fold-introduced.** Every one pre-existed in v0 and every one was found by reading a CONSUMER — the depositor's re-validation, (f)'s key check and `<declare>` guard, `emit_manifest`'s call graph, the origin's `MUST-PRESERVE`. None came from re-reading prose. The opposite shape to this session's earlier cycles at 43–62% fold-introduced.
**⚠️ Two of the seven corrected claims already stated to the CEO** — "nothing has ever checked it" and "the check must not live in `plan_lint`" — both asserted before the measurement that refuted them.
**Closing:** **BAR MET at walk 5.** FROZEN pending deposit authority.

## Cycle Manifest
tier: T1
target: scripts/cycle_check.py
class: shop-infra
reads: scripts/cycle_check.py, scripts/plan_lint.py, depositor.py, /Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md, knowledge/decisions/Done/executable-100025.md, knowledge/decisions/Done/diagnostic-100032.md
writes: scripts/cycle_check.py, tests/test_cycle_check_manifest_provenance.py, knowledge/mutants/manifest-provenance-gate.json, knowledge/development/dev-log-manifest-provenance-gate-2026-09-03.md
open_forks: whether the gate should ALSO live in plan_lint (f) as a WARN — rejected on the measured ground that WARNs are ignored by this author, overturnable with evidence; whether the depositor's re-validation should extend from cycle_check= to all four keys (thread-worthy, not folded here)
walks: 5
yields: 2, 2, 2, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:17
coherence: 5/5 walks have register rows

## STEP 1 — DEV (one conditional, no new subprocess)

> **Scope:**
> - `scripts/cycle_check.py`
> - `tests/test_cycle_check_manifest_provenance.py`
> - `knowledge/mutants/manifest-provenance-gate.json`
> - `knowledge/development/dev-log-manifest-provenance-gate-2026-09-03.md`
>
> **Item 1 — re-derive P1–P11 and HALT on mismatch.** ⛔ Re-run P9's positive control; if it no longer discriminates the predicate is wrong and this plan has no case. ⛔ Re-read P4's call graph and confirm the recursion hazard is real before choosing a placement — it is the reason this plan is not a `plan_lint` check.
>
> **Item 2 — write the failing tests FIRST**, in a focused sibling:
> 1. ⛔ **stanza present, `validation:` missing a key the emitter writes → verdict is `CONTINUE`, not `BAR_MET`** — the regression this plan exists for
> 2. stanza present, `validation:` carries the full emitter key set → BAR_MET unaffected
> 3. ⛔ **no `## Cycle Manifest` stanza at all → this condition does NOT fire**; the verdict is whatever it would have been
> 4. ⛔ **VALUES differing from a fresh emit do NOT fire it** — build a stanza with the right keys and deliberately stale values and assert BAR_MET still reachable (P7's drift case, the false-positive this must not have)
> 5. ⛔ **the key set is derived from the emitter's own construction, not hardcoded** — mutate the emitter to write a fifth key and assert the gate demands it without the test being edited. This is the anti-drift test: two lists that must agree are two implementations that can diverge
> 6. a stanza whose `validation:` is `N/A` (the emitter's own fallback when walk data is absent) → does NOT fire
> 6b. ⛔ **a stanza whose `validation:` is `<declare>` → does NOT fire.** `cycle_check` itself writes `<declare>` for un-derived fields (`:675-680`) and `plan_lint` (f) already guards it explicitly (`:612`: `if validation_val and validation_val != "<declare>"`). A gate that fires on the placeholder would block every plan mid-emission
> 6c. ⛔ **an EMPTY `validation:` → does NOT fire** — same guard, same reason; `plan_lint` (f)'s truthiness test covers it and this must agree
> 7. ⛔ **no new subprocess is spawned on the normal path** — assert the check adds zero process launches, since `cycle_check` runs constantly
> 8. the existing `tests/test_cycle_check.py` suite unchanged
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — implement the conditional at `:502`.** Derive the expected key set from the SAME source the emitter uses (P3's f-string construction) so the two cannot drift — extract it to one named constant both read. ⛔ **No subprocess. No call to `--emit-manifest`** (P5).
> ⛔ **The emitter's OUTPUT must be byte-identical after the refactor.** Extracting the key list restructures a shipped f-string that other surfaces parse — `plan_lint` (f) at `:611-614` and `depositor` at `:515-524` both read this line, and the depositor's comparison is case- and format-sensitive (DC 2.17 recorded it holding `executable-100005` on `expected=bar-met got=BAR_MET`). Capture `--emit-manifest`'s full stdout on a fixed plan BEFORE the change and diff it after: **zero bytes may differ.**
> ⛔ **Adopt `plan_lint` (f)'s guards verbatim rather than re-deriving them** — the falsy and `<declare>` tests at `:612`. Two guards written twice diverge; this plan is about exactly that class.
>
> **Item 4 — `knowledge/mutants/manifest-provenance-gate.json`**, one mutant per branch: drop the missing-key arm → test 1 fails; drop the no-stanza guard → test 3 fails; compare values instead of keys → test 4 fails; hardcode the key list instead of deriving it → test 5 fails. ⚠️ **A survivor is a missing test, stated as Critical**; ⛔ **0 ERROR required**. Every anchor count-1 at HEAD; every `target` a repo-relative path (thread 105: an absolute `target` escapes the sandbox and reports every mutant falsely SURVIVED).
>
> **Item 5 — dev-log**, recording P5's recursion hazard and the two rejected predicates (P7, P8) with their measurements, so the next author does not re-propose them.
>
> **Item 6 — commit** (message tagged with the plan id); record `numstat` — exactly 4 files.
>
> **Deposits:**
> - `knowledge/development/dev-log-manifest-provenance-gate-2026-09-03.md`
>
> **Post-conditions:** all ten tests pass; the existing `test_cycle_check.py` suite unchanged (count re-derived at execution, not hardcoded); the gate fires on `diagnostic-100032` and not on `100028`/`100030`, shown as a before/after pair in one run; no new subprocess on the normal path; the runner's own mutants all killed, 0 error.

## STEP 2 — QA (full suite + the gate shown to discriminate)

> **Item 1 — full suite** from the dispatch worktree, output to `pytest_full.txt`. ⚠️ The canonical checkout's `config.json` makes `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` fail; a worktree has none and the suite is green there. `known_failures: 0` is correct for the dispatch location — do not raise it.
>
> **Item 2 — the gate discriminates, both directions.** Run `cycle_check` over the three-plan control set (P9) and show `100032` no longer reaches BAR_MET while `100028` and `100030` do. ⛔ Then run the SAME set against the pre-change `cycle_check` and show all three reach it — the fixture must be proven to discriminate, not merely to pass.
>
> **Item 3 — the drift false-positive does not occur:** run the gate over every plan in `Done/` that carries a full-key stanza and show zero fire, despite their stored values having drifted from a fresh emit (P7).
>
> **Item 4 — no-regression:** every existing `cycle_check` test green; `cycle_check`'s verdict byte-identical on a shipped plan with a compliant stanza.
>
> **Item 5 — the runner's own kill map:** `mutation_check` over `knowledge/mutants/manifest-provenance-gate.json` → all killed, 0 survived, **0 error**.
>
> **Item 6 — self-application.** ⛔ Run the shipped gate against THIS plan. It must reach BAR_MET — this plan's own stanza is emitted, not typed. A plan shipping a gate it would itself trip is the degenerate-exemplar class (`LESSONS.md` 2026-09-03: a plan seeded the exact false negative it documented, in its own QA step).
>
> **Item 7 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `manifest-provenance-gate-2026-09-03`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/manifest-provenance-gate-2026-09-03/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/manifest-provenance-gate-2026-09-03"`
> - `required_evidence_files`: `["pytest_full.txt", "probes-raw.txt"]`
>
> Include the literal stdout of the block in the QA report. Banner, byte-exact, inside the receipt's VERIFICATION section:
>
> ```
> ============================================================
> Rule 20 — QA Self-Check Results
> ============================================================
> PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
> ```
>
> ⛔ If the block prints `FAILED`, do not proceed with closure — halt and report.
>
> **Deposits:**
> - `knowledge/qa/evidence/manifest-provenance-gate-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/manifest-provenance-gate-2026-09-03/pytest_full.txt`
> - `knowledge/qa/evidence/manifest-provenance-gate-2026-09-03/probes-raw.txt`
>
> **Post-conditions:** suite green from a worktree, 0 failed; the gate shown to discriminate on the control set AND shown not to fire before the change; zero drift false-positives across `Done/`; kill map clean; this plan reaches BAR_MET under its own gate.
