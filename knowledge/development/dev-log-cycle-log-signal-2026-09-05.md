# Dev log — `cycle_log_signal_census`, Step 1 (DIAGNOSTIC)

**Date:** 2026-09-05 · **Plan:** `knowledge/decisions/drafts/diagnostic-cycle-log-signal.md`
**Dispatch mode:** `manual_bootstrap` — ⛔ **no lifecycle plan id, no `Done/` record.** Cite the
research note by path, never by a plan id.
**Machine:** the mini · **Interpreter:** `bellows/.venv/bin/python` (3.12.14)

## What was built

`tools/cycle_log_signal_census.py` — a read-only diagnostic instrument. It writes nothing, commits
nothing, and edits no checker. Its whole output is the raw text file below.

**It imports the production readers and calls them** (Item 2's binding constraint —
diagnostic 100032's walk 4 rejected a second hand-written parser, and five hand-written parses
failed on this corpus in one session):

- `cycle_yields.extract_dc_blocks`
- `cycle_check.parse_block`, `.check_assert_2`, `.run_check`, `._compute_coherence`, `._find_git_root`
- `walk_register_lint.validate_file`, `.extract_tables`, `.is_fold_table`

The one thing it carries of its own is a **mirror** of cycle_check's three-step register-ref
resolution — necessary because `check_assert_2` returns a verdict but not the resolved *path*, and
the path is what the register reader needs. ⛔ **The mirror is not trusted.** Every plan's mirror
verdict is cross-checked against `check_assert_2`'s own; C0.2 reports the comparison before any
finding is offered. Result: **102 compared, 0 disagreements.**

## Controls, and why each exists

- **C0.1 positive control** — mandated by the plan: on `executable-lessons-destination-v2.md` the
  instrument must report body-walks **0** AND register-rows **4**. Measured exactly that.
  ⛔ An empty result must be proven, never assumed; without this control a broken register reader
  would have reported "0 rows everywhere" and looked like a clean corpus.
- **C0.2 resolver mirror** — the only defence against the instrument answering a question about
  itself rather than about `cycle_check`.
- **C0.3 negative control** — an unresolved ref must yield no rows. 22 unresolved, 0 with rows.
- **C0.4** — 482 files skipped, each with its reason printed.

## Deposits

| path | what |
|---|---|
| `tools/cycle_log_signal_census.py` | the instrument |
| `knowledge/qa/evidence/cycle-log-signal-2026-09-05/census-raw.txt` | raw output, 1335 lines |
| `eluvian-governance/governance/knowledge/research/cycle-log-signal-2026-09-05.md` | the research note |
| `knowledge/development/dev-log-cycle-log-signal-2026-09-05.md` | this file |

## Results, in one line each

- **P7 HOLDS** on all three sub-claims, verified in source AND by behaviour over 102 plans. The
  plan's only halt condition did not fire.
- **P6 is 22, not 6** — three classes: 18 shop-layout-relative refs (fail-closed on the mini, file
  present on disk), 3 never-created registers, 1 parser mis-capture of prose.
- **P4 is 6 raw / 2 marginal.** The pinned 2 was a marginal-signal count; the pin does not say which
  question it answered.
- **The conjunction's false-positive rate is 4/6 (67%)** — and all four false positives already
  return `ESCALATE:unparseable` today, so the check's *marginal* false-positive rate is 0%.
- **Capability and cadence live in three different places.** `plan_lint` has the densest cadence and
  zero register capability; `walk_register_lint` has all the capability and no gating cadence;
  `cycle_check` has partial capability (status only, never rows) at the two cadences that matter.
  `fold_check.readers_for` picks exactly one reader per artifact, so **nothing anywhere reads a plan
  and its register in one invocation.**

## ⛔ The recurrence, recorded

**The failure recurred ONE CYCLE after being diagnosed and fixed.** Thread 133 is the same error
class — `cycle_check` reading the record only from the plan body while the record was written to the
walk register. It was diagnosed 2026-09-04, produced the wrong escalation (the CEO resumed past the
weaker of two rulings), and shipped as `eff3c36` **on 2026-09-04**.

On **2026-09-05**, the same author produced two more instances:
`drafts/executable-lessons-destination-v2.md` (body empty, register 4 rows) and
`drafts/executable-memory-destination-and-gate.md` (body empty, register 8 rows). These are the
**only two plans in the entire 102-plan corpus that are silently wrong** — every other plan carrying
the same shape already emits an `ESCALATE`.

Discipline was applied with full knowledge of the defect, one day after the fix, and did not hold.
⚠️ Recorded as a measurement. The remedy is not this plan's to choose.

## Two findings surfaced incidentally, neither repaired

1. **The blind spots compose.** `run_check` returns `CONTINUE` at `cycle_check.py:462-463` when
   `walk_data` is empty — *before* `check_assert_2` runs at `:470`. So a register ref pointing at
   nothing is invisible for exactly as long as the body is empty, which is precisely the window in
   which the register is the only place the record could be. Three live drafts sit in it right now,
   this plan among them.
2. **`_compute_coherence`'s walk-matching regex has a false-match class.** `\bwN\b` matches Gate-2
   cycle-week tokens (`gate2-pt-w28-a`, `forge-cycle-w29`). Measured over the corpus: 17 of 26 hits
   on the same comparison are contaminated by it. A coverage measure that almost never disagrees is
   reporting on its own regex.

## Gate expectation for this step

⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step's evidence is a `.txt`,
so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named in the plan before
execution, on the 100032/100034/100036 precedent. ⛔ This justification is committed BEFORE any
override; `--override-gate` is write-once.

## Post-conditions

All 22 unresolvable refs classified with the failed resolution named · the 2×2 complete over the
resolvable 80 with the unresolvable 22 accounted for separately and a false-positive count named ·
capability and timing reported as separate tables per tool · a noise cost per candidate, in two
counts, with one candidate's contamination measured and stated · ⛔ **no recommendation anywhere and
no checker edited.** It prices; it does not choose.
