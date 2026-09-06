# Dev log — `cycle_log_projection_census`, Step 1

**Date:** 2026-09-06 · **Machine:** the mini · **Plan:** `knowledge/decisions/drafts/diagnostic-cycle-log-projection.md`
**Dispatch mode:** `manual_bootstrap` — ⛔ no lifecycle plan id, no `Done/` record. Cite the research
note by path: `eluvian-governance/governance/knowledge/research/cycle-log-projection-2026-09-06.md`

## The finding that licensed the plan, re-measured

⛔ **Two hand-kept records of one set of events disagree on a third of the corpus.** Over the 71 plans
carrying both a body Cycle Log with walk data and a register with walk rows: **47 exact, 23
derivable-with-gap, 1 not-derivable.**

⛔ **And the drift runs BOTH WAYS**, which is what makes it a record-keeping failure rather than a
lag:

- **BODY-AHEAD, 18** — walks declared with no register rows. The last walk's findings were never written down.
- **BODY-BEHIND, 5** — register rows for walks the body omits. This is thread 140/141's failure, and it is not historical: `executable-100010`, `executable-100013`, `executable-mandate-canary`, `executable-verdict-signal-canary`, and ⚠️ **`diagnostic-register-coverage` — whose Step 1 I ran this morning.** Its register carries walk 3; its body says walks 1–2. The instrument caught its own author's artifact.

## What was built

`tools/cycle_log_projection_census.py`, read-only.

- **Imports the shipped parsers and calls them**: `cycle_yields.extract_dc_blocks`,
  `cycle_check.parse_block` / `_compute_coherence` / `_find_git_root`,
  `walk_register_lint.extract_tables` / `normalize_column` / `validate_file` / `SCHEMA_DECL_RE`, and
  ⭐ **`lens_order_check.commit_record`** — the observer read by its own parser, not a second one.
- **Two positive controls, opposite directions, run before any corpus pass**: `executable-100030`
  (agreeing) and `executable-100017` (diverging, missing walks `[4,6]` exactly). One control proves
  only that the instrument reads the case it was written for.
- **Self-exclusion** armed by exact filename; at v0 the register does not exist, so 0 excluded.
- **Appends to the raw `.txt` as each measurement is established**, so a killed run leaves partials.

## Results, one line each

- **P4 held — no halt.** The observer carries `walk N`, `lens N(/N)` and a continuation flag. No counts, no classes.
- **Per-lens derivability is total where it matters**: 71 of 71 registers carry a lens value.
- ⛔ **One field is not derivable and it is the load-bearing one** — the instruction/record split, a `class` column in **7 of 173** registers. It is the convergence signal, so **if it is not derivable, the bar is not derivable.** `restructuring_walks` and `claims_closure` are absent from the register entirely.
- **The `class` migration is ~7× cheaper than the raw count** — 166 registers would lack the column, but `_apply_version_status` demotes an older-declared non-conformant register to LEGACY_SCHEMA, which is in `cycle_check._REGISTER_SILENT_STATUSES` and emits no WARN. Real noise is bounded by the **25 UNDECLARED** registers.
- ⛔ **Q4 is the binding constraint, and it is worse than the pin.** P5's 75-of-596 is a *commit* rate; the *plan* rate is **4 of 134 — 3%**. A Cycle Log computed from the observer today would be empty for 130 of 134 plans.
- ⛔ **Q5: no current check can verify a projection is current.** All 7 empty-body plans return `'N/A'` from `_compute_coherence`; its matcher scores Gate-2 week tokens as walks; it runs once, at freeze. **Thread 152 is a precondition, not an adjacent fix.**

## Two pin drifts, recorded as findings

**P5's denominator is 596, not 593** — three commits landed since the pin (mine, today).
**P3's class-column count is 7, not 5** — the pin was taken with a raw `grep` where the instrument
uses `normalize_column`, which absorbs header spelling variants. ⚠️ The pin under-counted because it
hand-matched a header shape; the instrument does not, which is the whole reason it must import the
lint rather than re-implement it.

## Gate expectation

⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as
`.txt`, so `_gate_qa_test_result` would find no pytest summary and FAIL. ⛔ **Under `manual_bootstrap`
no gate actually runs and there is no plan id to override** — recorded so a later reader does not
attempt the override act (thread 154).

## Post-conditions

Every plan carrying both records classified with the mismatch direction named · every `parse_block`
field classified derivable / prose / absent, with the convergence signal called out · the `class`
migration priced with the LEGACY_SCHEMA effect separated from the failure count · observer coverage
reported apart from agreement · Q5 answered from the function's source and behaviour · self register
excluded by exact name and the exclusion reported · ⛔ **no checker, schema or doctrine edited, and no
remedy chosen.**
