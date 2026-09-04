# bellows — executable: `cycle_check` — BAR_MET refuses a Cycle Manifest whose `validation:` line lacks a key the emitter writes, because DC:253 declares four fields COMPUTED and never hand-typed and nothing has ever checked it

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_cycle_check.py` + a new focused sibling) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100032.md` (the drafting-battery-cost diagnostic) and `DRAFTING_CYCLE.md:253`, whose trust taxonomy this enforces. Clone origin: `Done/executable-100025.md` (2026-09-02 — the newest shipped plan that WRITES `scripts/cycle_check.py`, tiered T1, warn/gate change with a kill map).

## What this changes

⛔ **One conditional in `cycle_check`'s BAR_MET decision.** If a plan carries a `## Cycle Manifest` stanza whose `validation:` line omits any key the emitter writes, the verdict is `CONTINUE`, not `BAR_MET`. Nothing else.

## Why this exists

`DRAFTING_CYCLE.md:253` states a **provenance** invariant:

> **Trust taxonomy:** four fields are COMPUTED and never hand-typed (`walks`, `yields`, `validation`, `coherence` — the emitter derives them from the cycle's walk data, checker verdicts, and register state)

**Nothing has ever checked it.** `plan_lint` check (f) verifies field PRESENCE — measured on a hand-typed manifest with all ten fields present and a short `validation:` line, `plan_lint` exits **0** and (f) emits no line at all. Presence is not provenance.

⚠️ **Measured, and the violation is the author's:** plans closed after the emitter gained `propagation_check` (`c39927c`, 2026-09-02 17:14) are 5 compliant / 3 not. Two of the three are the transition window — `100023` IS the plan that made the change, `100024` closed 22 minutes later. **`diagnostic-100032` closed a full day later with a hand-typed `validation:` line missing the key.** The rule was explicit, the tool existed and worked, and the author typed the field anyway. That is the case for a gate rather than against one.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the invariant | `DRAFTING_CYCLE.md:253` — four fields COMPUTED and "never hand-typed" | `sed -n '253p' DRAFTING_CYCLE.md` |
| P2 | ⛔ nothing enforces it | `plan_lint` on `Done/diagnostic-100032.md` → **exit 0**, no `(f)` line emitted. Its manifest has all ten fields; only a KEY inside `validation:` is missing | run `plan_lint` on that file, read all output |
| P3 | the emitter's key set | `cycle_check.py:658` builds `validation:` as `cycle_check=…, plan_lint=…, fold_check=…, propagation_check=…` — **four keys**, one f-string | read `:658` |
| P4 | ⛔ **the emitter subprocess-runs three checkers** | `emit_manifest` invokes `plan_lint.py` (`:613`), `fold_check.py` (`:628`) and `propagation_check.py` (`:640`) | read `:600-655` |
| P5 | ⛔⛔ **THE PLACEMENT CONSTRAINT — a `plan_lint` check would RECURSE** | P4 means `plan_lint → cycle_check --emit-manifest → plan_lint → …` without termination. **The check must NOT live in `plan_lint`, and must NOT invoke `--emit-manifest`.** The author proposed exactly that before measuring P4 | trace the call graph |
| P6 | the non-recursive placement | `cycle_check.py:502` — `verdict = "CONTINUE" if parsed["has_unparseable"] else "BAR_MET"`, already guarded by `asserts_ok`. Comparing a stored key set against a CONSTANT costs no subprocess and cannot recurse | read `:498-506` |
| P7 | ⛔ **why NOT value equality** | stored and freshly-emitted VALUES legitimately drift after freeze — measured on compliant `Done/executable-100028.md`: `propagation_check` `DIVERGENT:50` stored vs `DIVERGENT:56` fresh, and `fold_check` `PASS` vs `N/A`. A value check false-positives on every closed plan. **Keys do not drift; values do** | emit for that plan and diff |
| P8 | ⛔ **why NOT a bare "four keys" shape rule** | 53 plans legitimately carry three keys — they closed before `c39927c` added the fourth. The predicate must be "the key set the CURRENT emitter writes", not a hardcoded four | count key-sets across `Done/` by close time |
| P9 | positive control | `diagnostic-100032` stored 3 keys vs emitter 4 → must FIRE. `executable-100028`/`100030` stored 4 vs 4 → must NOT fire | compare key sets on those three |
| P10 | tier precedent, measured not paraphrased | four plans that WRITE `scripts/cycle_check.py` were all `cycle_tier: T1` — `100023`, `100025`, `100022`, `100029`; one states "T-6 no (no doctrine, no gate, no script)". The checkers are instruments, not gates under T-6 | grep the tier line in those plans |
| P11 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## What this does NOT do

- ⛔ **It does not add a `plan_lint` check.** P5 is fatal to that placement. A predecessor draft proposing it is WITHDRAWN at `drafts/executable-battery-verdict-declaration.md`.
- ⛔ **It does not compare VALUES** (P7), and does not hardcode four keys (P8).
- ⛔ **It does not require a manifest to exist.** A plan with no stanza is check (f)'s and the freeze's business; firing here would double-report and train the reader to ignore both.
- **It does not make the check a WARN.** ⚠️ Deliberate: the 2026-09-03 diagnostic measured that this author ignored standing `plan_lint` WARNs three times in one night. A WARN is the delivery mechanism the finding says fails. This gates BAR_MET instead.
- **It does not verify the values were honestly computed.** A key can still be typed. This raises the floor from "silently absent" to "affirmatively false", which is a different and more visible act — it is not a proof of provenance, and must not be described as one.

## Drafting Cycle

**Tier:** T1 — T-3 fires (`cycle_check` runs on every machine that drafts). **T-6 does NOT fire**, checked against the trigger as QUOTED (*"Edits doctrine, the template, gates, or specialist contracts"*) and against P10's four measured precedents, one of which states the reading explicitly. ⚠️ **This is the exact reading that inverted twice today** (`wrap_check` as "a wrap gate, not a step gate"); it is grounded in precedent rather than in the author's paraphrase for that reason. T-8 not fired: clone by kind of `Done/executable-100025.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-manifest-provenance-gate-2026-09-03.md`
**Walks:** 0 (context pin complete).
**⛔ `propagation_check` run AT WALK 0 — DIVERGENT:12, all classified, ZERO real.** Every hit is a pin cited correctly at its use site with its qualifier — `DRAFTING_CYCLE.md:253`/`DC:253` (4), plan ids `100032`/`100025` (7), and `:502` naming the conditional's location (1). Run rather than skipped because this plan is about an unenforced invariant, and shipping it unrun would be the degenerate-exemplar failure its own QA Item 6 forbids.
**⚠️ A design killed at walk 0, recorded so it is not re-proposed.** The author described a `plan_lint` check to the CEO before measuring `emit_manifest`'s call graph. P4/P5: the emitter subprocess-runs `plan_lint.py`, so that placement recurses without termination. The gate moved to `cycle_check`'s own BAR_MET decision, which needs no subprocess and cannot recurse.

**Closing:** NOT CLOSED at walk 0.

## Cycle Manifest

*(to be EMITTED at BAR_MET with `cycle_check --emit-manifest` — ⛔ **do NOT hand-type this stanza.** DC:253 names `validation` a computed field; hand-typing it is the exact violation this plan gates, and a plan shipping this gate while tripping it is the degenerate-exemplar failure.)*

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
> 7. ⛔ **no new subprocess is spawned on the normal path** — assert the check adds zero process launches, since `cycle_check` runs constantly
> 8. the existing `tests/test_cycle_check.py` suite unchanged
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — implement the conditional at `:502`.** Derive the expected key set from the SAME source the emitter uses (P3's f-string construction) so the two cannot drift — extract it to one named constant both read. ⛔ **No subprocess. No call to `--emit-manifest`** (P5).
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
> **Post-conditions:** all eight tests pass; the existing `test_cycle_check.py` suite unchanged (count re-derived at execution, not hardcoded); the gate fires on `diagnostic-100032` and not on `100028`/`100030`, shown as a before/after pair in one run; no new subprocess on the normal path; the runner's own mutants all killed, 0 error.

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
