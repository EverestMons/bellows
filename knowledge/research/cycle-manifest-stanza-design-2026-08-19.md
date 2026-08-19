# Cycle Manifest Stanza Design — Findings

**Date:** 2026-08-19 | **Source diagnostic:** 472 (component 2 of the cycle-automation proposal §4)

---

## Q0 — Ratified Format (restated verbatim)

`## Cycle Manifest` — a fixed `key: value` block emitted at BAR_MET. Ten fields:

| # | Field | Value |
|---|-------|-------|
| 1 | `tier` | T0 / T1 / T2 |
| 2 | `target` | primary target file or subsystem |
| 3 | `class` | `read-only` / `governed-tooling` / `register-writing` |
| 4 | `reads` | explicit path list (enables collision checks) |
| 5 | `writes` | explicit path list (enables collision checks) |
| 6 | `open_forks` | CEO forks carried forward, or `none` |
| 7 | `walks` | integer walk count |
| 8 | `yields` | per-walk instruction-class series |
| 9 | `validation` | COMPUTED `checker=verdict` pairs |
| 10 | `coherence` | COMPUTED register/commit coherence statement |

**Reconciliation against proposal §4:** §4 listed `plan_lint exit` and `battery results` as separate items — both are SUBSUMED into `validation:` as `checker=verdict` pairs (e.g. `plan_lint=0_FAIL, cycle_check=BAR_MET`). `walks` and `yields` were ADDED for the plateau/convergence record. The ratified 10-field set is complete; the executable must not reintroduce §4's items as separate fields.

---

## Q1 — Current §3 Rules: Characterization and Reconciliation

### §3 rules in doctrine (located by line)

§3 is "The Cycle Log (compact, in the plan)" at `DRAFTING_CYCLE.md:206`. Its rules are spread throughout the file. The load-bearing rules the stanza amendment must reckon with:

**Rule A — The per-class number form (line 40).** Within §2's bar definition:
> `The walk's per-class split is stated as numbers in the Cycle Log (instruction 0 / record 5).`

This establishes the compact numeric form for per-walk results. The stanza's `yields:` captures the instruction-class half of this split.

**Rule B — The ONE bounded exception (line 50, restated at line 216).** §2 states:
> `This is the ONE bounded exception to §3's compact-form rule, and §3 states it — the bar cannot be audited from a log that may not name what it stopped on.`

The exception allows a judged stop's Closing line to name each residue finding's class individually. Line 216 restates: "One bounded exception to the compact form above: a cycle closing on a judged stop names each residue finding's CLASS in a clause apiece on the Closing line."

**Rule C — The running fold-count prohibition (line 194, restated at line 210).** §2.8 states at line 194:
> `§3 forbids a running fold-count in the log and mandates the compact per-lens form, and that prohibition is unchanged.`

§3 proper at line 210 states the prohibition directly:
> `Do not keep a running fold-count in the Cycle Log — fold counts belong in the compact per-lens lines (e.g., w1 2 folded; w2 dry), not as a separate running tally.`

**Rule D — Compact form is load-bearing (line 208).** §3 opens:
> `The compact form is load-bearing — the plan body carries structure, not narrative.`

**Rule E — Walk register is the detail home (line 210).** Full walk-by-walk analysis lives in the walk register, not the Cycle Log. Only per-lens summary lines appear in the plan's `## Drafting Cycle` block.

**Rule F — No gate-matching strings (line 218).** The Cycle Log must contain no string a gate matches.

**Rule G — Record placement: outside step spans (line 226).** Record sections are placed above the first step heading, never trailing after the last.

### Done/ corpus census

**40** Done/ plans carry a `## Drafting Cycle` block (confirmed by `grep -l '## Drafting Cycle' Done/*.md | wc -l`). **39** carry a `**Closing:**` line; **5** carry `Walk N STATUS:` aggregate lines.

Total DC block bytes across corpus: **181,994 bytes** (avg 4,549 per plan). The largest DC block is executable-306 at 13,196 bytes. For context, executable-306's total plan size is 53,509 bytes — its DC block is 24.7% of the plan.

The compaction evidence from proposal §4: across the plans measured, 47,959 bytes of record vs 47,715 of instruction. The DC blocks' Closing, STATUS, and §5 Conformance prose — the authored, drifting portion — is where the stanza's structured compaction applies.

**Representative Closing lines (the prose being compacted):**

| Plan | Closing bytes | Form |
|------|-------------|------|
| executable-332 | ~1,100 | Long §2-deviation reasoning |
| executable-306 | ~430 | Judged-stop narrative |
| executable-324 | ~460 | Sequence + count narrative |
| diagnostic-460 | ~210 | Compact dry-close |
| executable-271 | ~60 | Minimal dry |

The variance is itself the problem: Closing lines range from 60 to 1,100 bytes of free-text prose carrying COMPUTABLE facts (walk count, dry/not, lint exit code) mixed with authored reasoning. The stanza extracts the computable portion into structured fields.

### Reconciliation: stanza vs each §3 rule (the load-bearing integration)

**Conflict (i): Does `yields:` violate Rule C (no running fold-count)?**

`yields: 5, 2, 2, 1, 1, 0` is a per-walk instruction-class count series. Rule C at line 210 prohibits "a running fold-count in the Cycle Log" and mandates "fold counts belong in the compact per-lens lines." Line 194 reaffirms: "that prohibition is unchanged."

**This IS a genuine conflict.** The `yields:` field is literally a fold-count series across walks — the precise form Rule C prohibits. However, two mitigating factors bear on the CEO's decision:

1. **Purpose vs letter.** Rule C's PURPOSE (measured at line 44) is to prevent a falling total finding-count from being mistaken for convergence during the cycle. The stanza is emitted AFTER BAR_MET — the cycle is closed; `yields:` is a post-close summary, not a running tally that influences cycle judgment. The prohibition was written to govern the DRAFTING phase, not the deposit summary.

2. **Existing practice already carries yields data.** The `**Walks:**` line in diagnostic-460 reads: `Walks: 4 (bar MET — walk 4 dry, zero findings, no restructuring fold). Yields 8 → 2 → 2 → 0.` This is the same data in prose. The stanza makes it structured and computed rather than authored.

**Resolution options:**
- **(A) Supersede Rule C with a refinement:** the prohibition applies to the walk-by-walk drafting phase; the BAR_MET stanza's `yields:` is a computed summary exempt from it. This requires explicitly amending the line 210 text and the line 194 cross-reference.
- **(B) Remove `yields:` from the stanza.** This loses the convergence record the cycle_check plateau detector can cross-check at deposit.
- **(C) Rename and reframe:** replace `yields:` with a differently-structured field that captures convergence without being a "fold-count series" — e.g. `convergence: 6 walks, class-dry at walk 6, instruction-yield 5→0`. This is cosmetically different from `yields:` but semantically identical.

**Recommendation:** Option (A). `yields:` is a COMPUTED field emitted post-close for the deposit record. Rule C's purpose is served by the amendment clarifying its scope. But this IS a doctrine supersession and the CEO's call.

**Conflict (ii): Does the stanza duplicate the per-class number form (Rule A)?**

No genuine conflict. The per-lens lines carry per-walk, per-lens fold counts with class splits (`w1 2 folded — instruction 1 / record 1`). The stanza's `yields:` carries the per-walk AGGREGATE instruction-class count. The stanza REPLACES the `Walk N STATUS:` aggregate lines, which already carry this aggregation. The per-lens lines are retained; the stanza does not duplicate them.

**Conflict (iii): Does `validation:`/`coherence:` create a second compact-form exception (Rule B)?**

No genuine conflict. Rule B grants ONE exception for judged-stop residue enumeration on the Closing line. The stanza's computed fields (`validation:`, `coherence:`) are not "exceptions to compact form" — they ARE compact form, structured as `key: value` pairs. The stanza replaces the Closing/STATUS prose that currently varies from 60 to 1,100 bytes; it does not add a second narrative exception. The judged-stop residue enumeration (Rule B) continues to live on the Closing line, OUTSIDE the stanza (the Closing line precedes the stanza in the block).

---

## Q2 — Finalized Stanza Grammar

### Specimen (populated from executable-464's actual data)

```
## Cycle Manifest
tier: T1
target: bellows/scripts/cycle_check.py
class: governed-tooling
reads: bellows/scripts/cycle_yields.py, bellows/scripts/plan_lint.py, bellows/scripts/fold_check.py, knowledge/research/cycle-check-format-census-2026-08-19.md
writes: bellows/scripts/cycle_check.py, bellows/tests/test_cycle_check.py
open_forks: none
walks: 6
yields: 5, 2, 2, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL
coherence: 6/6 walks have register rows
```

### Edge cases resolved

**(a) Multi-line values for `reads:`/`writes:`.** When the path list exceeds ~5 entries or ~100 characters, use continuation lines indented by 2 spaces:

```
reads: bellows/scripts/cycle_yields.py, bellows/scripts/plan_lint.py,
  bellows/scripts/fold_check.py, bellows/scripts/walk_register_lint.py,
  knowledge/research/cycle-check-format-census-2026-08-19.md
```

Rationale: the `key: value` block is parsed line-by-line; a line starting with 2+ spaces after a `reads:` or `writes:` line is a continuation. The emitter joins continuations before splitting on `,`.

**(b) Path expression.** Paths are relative to the plan's repository root. Cross-repo reads use absolute paths. Examples:
- Same-repo: `bellows/scripts/cycle_check.py` (relative to the bellows repo root)
- Cross-repo (the governance case): `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md`

Normalization: trailing slashes stripped, no trailing `/.`, no `..` components. The depositor resolves relative paths against the plan's declared `project:` header field.

**(c) `validation:` value form.** Comma-separated `checker=verdict` pairs. The verdict is the checker's STDOUT token (for cycle_check) or exit-code summary (for plan_lint). Examples:
- `cycle_check=BAR_MET` (the cycle_check verdict string)
- `plan_lint=0_FAIL` (0 FAIL results; the `N_FAIL` form encodes the count)
- `fold_check=PASS` (baseline advanced for the latest walk)

`validation:` is COMPUTED and re-run by the depositor — the depositor does NOT trust the written verdicts; it re-executes each checker and compares. A mismatch is a HOLD.

**(d) `yields:` form.** Comma-separated integers: per-walk instruction-class counts, walk 1 through walk N, in order. A dry walk is `0`. Example: `yields: 5, 2, 2, 1, 1, 0` means walk 1 had 5 instruction findings, walk 6 had 0.

**(e) Stanza placement.** The `## Cycle Manifest` heading sits AFTER the `**Closing:**` line and BEFORE the step-separator `---`. It is within the `## Drafting Cycle` block but after all walk/closing prose. It does NOT replace the per-lens lines or the Closing line — it replaces the `Walk N STATUS:` aggregate lines and compacts the §5 Conformance prose into the `validation:` field.

Block structure after amendment:
```
## Drafting Cycle
**Tier:** ...
**Walk 0 (context pin):** ...
**Direction verdict:** ...
**Walks:** N.
- Weak spots: ...
- Destruction: ...
- Vulnerabilities: ...
- Integration-record: ...
- ACID: ...
**Conflicts:** ...
**Closing:** ...

## Cycle Manifest
tier: ...
target: ...
...
```

The stanza is the LAST element before the `---` separator and the first `## STEP` heading. This satisfies Rule G (record sections outside step spans) and keeps the stanza parseable by a separate heading.

**(f) `validation:` and `coherence:` are both COMPUTED.** `coherence:` (e.g. "6/6 walks have register rows") is emitted by cycle_check from its own walk/register check. It is NOT typed by the Planner. If the Planner writes `coherence:`, the depositor discards it and substitutes the computed value. The same applies to `validation:`, `walks:`, and `yields:`.

**(g) Per-field trust taxonomy.**

| Field | Trust class | Rationale |
|-------|------------|-----------|
| `validation` | **COMPUTED** | Re-run by cycle_check, plan_lint, fold_check at deposit; values compared, never trusted |
| `coherence` | **COMPUTED** | Emitted by cycle_check from walk-register and commit inspection |
| `walks` | **COMPUTED** | Derived from the block's walk data by cycle_check |
| `yields` | **COMPUTED** | Derived from per-walk instruction-class counts by cycle_check |
| `reads` | **AUTHORED-BUT-DEPOSITOR-VERIFIED** | Author-declared; depositor cross-checks against `targets`/required-reading and runs collision query |
| `writes` | **AUTHORED-BUT-DEPOSITOR-VERIFIED** | Author-declared; depositor cross-checks against Deposits block and runs collision query |
| `class` | **AUTHORED-BUT-DEPOSITOR-VERIFIED** | Author-declared; depositor verifies against `writes:` paths and applies the auto-deposit mapping |
| `tier` | **AUTHORED DECLARATION** | Set by the Planner per §1; the computed trigger-check is the Planner's obligation, not the emitter's |
| `target` | **AUTHORED DECLARATION** | Set by the Planner; no mechanical derivation available |
| `open_forks` | **AUTHORED DECLARATION** | Set by the Planner; forks are CEO-level decisions not mechanically detectable |

**Four of ten fields are COMPUTED** (validation, coherence, walks, yields). Three are AUTHORED-BUT-DEPOSITOR-VERIFIED (reads, writes, class). Three are irreducibly AUTHORED (tier, target, open_forks).

**Why the three authored fields are irreducible:** `tier` requires evaluating whether §1's triggers fire, which involves domain judgment (is this novel? does it touch governance?). `target` is the plan's subject, not mechanically derivable from its file paths. `open_forks` tracks CEO decisions that exist only in conversation, not in code.

---

## Q3 — reads:/writes: Collision Computation

### Collision queries

The depositor runs two intersection checks at deposit time against all in-flight plans (status = `active` or `pending` in the `plans` table):

1. **`writes ∩ writes` → HARD HOLD.** If the depositing plan's `writes:` set intersects any in-flight plan's `writes:` set, the deposit is HELD. Two plans writing the same file concurrently is a merge conflict waiting to happen.

2. **`reads ∩ writes` → HOLD AND REPORT.** If the depositing plan's `reads:` set intersects any in-flight plan's `writes:` set (or vice versa), the deposit is HELD and the collision is reported. A plan reading a file another plan is writing may be reading stale state (the plan-436 moving-target case).

### Path normalization for sound intersection

- Strip trailing `/` from all paths
- Resolve relative paths against the plan's `project:` header value (e.g. `bellows/` → `/Users/marklehn/Developer/GitHub/bellows/`)
- Absolute paths used as-is
- No glob expansion — paths are exact file references or directory prefixes
- Directory prefixes (paths ending without an extension) match any file under that directory
- Case-sensitive comparison (macOS notwithstanding — the convention is lowercase paths)

### The exact query

```sql
SELECT p.plan_id, p.plan_file
FROM plans p
WHERE p.lifecycle_state IN ('active', 'pending')
  AND p.plan_id != :depositing_plan_id
```

For each returned plan, extract its `reads:` and `writes:` from either its stanza (if present) or its Scope/Deposits blocks (legacy). Then compute:
- `depositing.writes ∩ inflight.writes` → HARD HOLD if non-empty
- `depositing.reads ∩ inflight.writes` → HOLD AND REPORT if non-empty
- `depositing.writes ∩ inflight.reads` → HOLD AND REPORT if non-empty

### The load-bearing limitation

**`reads:` is AUTHOR-DECLARED and its completeness cannot be mechanically verified.** An undeclared read gives false collision-safety — the depositor's `reads∩writes` check passes when it should hold. The plan-436 memory-repo case is the precedent: had that plan's cross-repo read not been declared, the collision would have gone undetected.

### Partial mitigation

Cross-check `reads:` against the plan's own declared data:
1. Every path in `writes:` should also appear in `reads:` (you read before you write) — flag if a `writes:` path has no corresponding `reads:` entry
2. Every declared `target` and required-reading path should appear in `reads:` — flag if a walk-0 target is absent from `reads:`
3. These cross-checks catch OBVIOUSLY incomplete `reads:` declarations but cannot detect an undeclared external read

**State plainly:** the depositor's `reads∩writes` safety is only as good as the declared `reads:`. This is an irreducible limitation of a declaration-based system. The mitigation reduces the gap; it does not close it.

---

## Q4 — Stanza Validation (Deposit-Time, NOT Per-Walk)

### Ordering constraint

The stanza is emitted AFTER cycle_check returns `BAR_MET`. cycle_check validates the walk-by-walk cycle; the stanza summarizes it. Therefore:

- The stanza **CANNOT** be a per-walk cycle_check check — cycle_check would be validating its own not-yet-emitted output
- The stanza check is **strictly downstream** of `BAR_MET`
- cycle_check's role stays the per-walk verdict that SIGNALS close; stanza validation is a deposit-time concern

### Validation layers

**Layer 1: plan_lint at deposit-shape (existing check (f) extended).**

plan_lint already validates the `## Drafting Cycle` block (check (f), lines 311-391 of `plan_lint.py`). Extend it to:
- Check `## Cycle Manifest` heading is present after `**Closing:**`
- Check all 10 fields are present with non-empty values
- Check `class:` is one of `{read-only, governed-tooling, register-writing}`
- Check `reads:` and `writes:` are non-empty for a non-`read-only` plan (a `read-only` plan may have empty `writes:` but must have non-empty `reads:`)
- Check `validation:` contains at least `cycle_check=` and `plan_lint=` entries
- WARN-first (matching §4's landing posture)

**Layer 2: depositor re-run (component 3).**

The depositor:
1. Re-runs `cycle_check` against the plan → compare emitted verdict with `validation:`'s `cycle_check=` value
2. Re-runs `plan_lint` against the plan → compare exit code with `validation:`'s `plan_lint=` value
3. Verifies `walks:` and `yields:` match cycle_check's computed values
4. Runs the `reads∩writes` collision query (Q3 above)
5. Applies the `class:` → auto-deposit mapping (Q6 below)

A mismatch at any of 1-3 is a HOLD — the stanza's computed fields disagree with the live re-run.

**Recommendation:** both plan_lint AND the depositor own validation, at different moments. plan_lint checks SHAPE (is the stanza present and well-formed?) at deposit-shape. The depositor checks CONTENT (do the computed fields match fresh re-runs?) at deposit time. Shape is cheap; content requires execution.

---

## Q5 — Rule 27 Gap Assessment

### Gap table

| Gap | Current State | Proposed State | Change Required |
|-----|--------------|----------------|-----------------|
| **(a) §3 doctrine text — stanza grammar** | §3 (DRAFTING_CYCLE.md:206-227) defines the compact Cycle Log form. No structured manifest stanza exists. Walk STATUS lines, §5 Conformance, and Closing carry free-text summaries. | §3 amended to define the `## Cycle Manifest` stanza: 10-field `key: value` block, emitted at BAR_MET, with the trust taxonomy (4 computed, 3 verified, 3 authored). The stanza REPLACES `Walk N STATUS:` aggregate lines. | Amend §3 to add the stanza grammar after the existing compact-form rules. The specimen and field definitions from Q2 become the normative text. |
| **(b) §3 doctrine text — compaction** | Closing lines range from 60-1,100 bytes of free-text prose mixing computable facts with authored reasoning. `Walk N STATUS:` lines carry per-walk aggregates in varied prose. `§5 Conformance:` lines carry lint results in prose. | The stanza extracts computable facts into structured fields. Closing line retains ONLY the authored reasoning (dry/judged-stop, residue enumeration). STATUS/§5 prose absorbed into `validation:`/`coherence:`/`walks:`/`yields:`. | Remove the `Walk N STATUS:` prose convention from §3. Amend the Closing line specification to state it carries reasoning only; computable facts move to the stanza. |
| **(c) §3 doctrine text — `yields:` vs Rule C** | Line 210: "Do not keep a running fold-count in the Cycle Log." Line 194: "§3 forbids a running fold-count in the log and mandates the compact per-lens form, and that prohibition is unchanged." | `yields:` carries a per-walk instruction-class count series — technically a fold-count in the Cycle Log. | **CEO FORK.** If `yields:` is kept: amend line 210 to scope the prohibition to the drafting phase ("Do not keep a running fold-count in the Cycle Log during drafting — the BAR_MET stanza's computed `yields:` is a post-close summary, not a running tally"). Amend line 194's cross-reference to match. If `yields:` is removed: no amendment needed, but the plateau/convergence record is lost from the deposit summary. |
| **(d) `reads:` field introduction** | Plans declare targets in walk-0 and Scope blocks. No structured `reads:` list exists. Collision detection is manual. | `reads:` is an authored, depositor-verified path list. The depositor runs intersection queries against in-flight plans' `writes:` sets. | No doctrine change to §3 for this. The depositor's collision query is component 3's build. The `reads:` field is defined by the stanza grammar (gap (a)). |
| **(e) The emitter — `cycle_check --emit-manifest`** | `cycle_check.py` (436 lines, 27 tests) emits a single verdict to stdout: CONTINUE / BAR_MET / ESCALATE:*. Strictly read-only. | A new `--emit-manifest` mode COMPUTES `validation`, `coherence`, `walks`, `yields` from the plan's DC block and its commit/register state, then merges authored declarations (`tier`, `target`, `class`, `reads`, `writes`, `open_forks`) from the plan header/stanza. Emits the complete `## Cycle Manifest` block to STDOUT. | Extend `cycle_check.py` with `--emit-manifest` flag. Must preserve existing 27 tests. Must preserve the strictly-read-only invariant: writes to STDOUT ONLY, never writes to any file, never `--save-baseline`, never modifies the plan. The emitted stanza is placed into the plan by the Planner/close step, not by cycle_check. |
| **(f) plan_lint stanza check** | plan_lint check (f) validates the `## Drafting Cycle` block structure: tier, lens lines, cold-panel line, closing fold/dry status. No stanza check. | plan_lint extended with a stanza-presence + well-formedness check at deposit-shape. WARN-first. | Extend plan_lint check (f) with stanza validation per Q4's Layer 1 spec. |
| **(g) Depositor re-run (component 3)** | No automated deposit-time re-validation of cycle verdicts. The written verdict is trusted. | The depositor re-runs `cycle_check`, `plan_lint`, compares against `validation:` values. Runs `reads∩writes` collision query. Applies `class:` mapping. | Component 3's build (separate plan). Depends on gaps (a), (d), (e), (f). |

### Compaction byte-delta estimate

**Removed by the stanza (per plan, estimated):**
- `Walk N STATUS:` lines: ~100-300 bytes per walk × avg 3 walks = ~450 bytes
- `§5 Conformance:` prose absorbed into `validation:`: ~200-400 bytes
- Closing line computable-fact portion: ~100-300 bytes
- **Total removed:** ~750-1,150 bytes

**Added by the stanza:**
- `## Cycle Manifest` heading: 20 bytes
- 10 `key: value` lines: ~400-600 bytes (varies with path list length)
- **Total added:** ~420-620 bytes

**Net delta:** approximately **-200 to -530 bytes per plan**, net-neutral-or-shrinking. The compaction is modest per plan but accumulates across the corpus and — more importantly — replaces DRIFTING prose with STRUCTURED fields. The byte saving is secondary to the drift-resistance.

### Subtractive-cut safety: line-by-line subsumption proof

The §3 amendment removes or modifies the following lines. For each, the subsuming stanza field or obsolescence reason:

| §3 line / convention removed | Subsuming field or reason |
|------------------------------|--------------------------|
| `Walk N STATUS:` aggregate lines (convention, not in §3 proper) | `walks:` + `yields:` (COMPUTED; carry the same walk-count and instruction-class data in structured form) |
| §5 Conformance prose (convention, not in §3 proper) | `validation:` (COMPUTED; carries `plan_lint=N_FAIL` + other checker verdicts) |
| Closing-line computable facts (walk count, dry/not, lint exit code embedded in prose) | `walks:`, `yields:`, `validation:` (COMPUTED fields extract the computable portion; Closing line retains the authored reasoning only) |

**No §3 line is REMOVED from doctrine.** The stanza is an ADDITION to §3, not a deletion. The removed items are conventions that evolved in practice (Walk STATUS lines, §5 Conformance prose in the DC block) but were never codified as §3 rules. The §3 rules themselves (compact form, walk register, gate-matching prohibition, etc.) are all RETAINED. The only §3 text that changes is:
1. Line 210's fold-count prohibition — REFINED to scope to drafting phase (if `yields:` is kept — CEO fork)
2. A new paragraph added to §3 defining the `## Cycle Manifest` stanza

---

## Q6 — class: Taxonomy and Auto-Deposit Mapping

### Mapping

| `class:` value | Deposit action | Rationale |
|----------------|---------------|-----------|
| `read-only` | **AUTO-DEPOSIT** | Blast radius bounded: a bad auto-deposit costs one wasted run; the plan writes only ephemeral/research artifacts |
| `governed-tooling` | **HOLD FOR CEO** | Writes production code, scripts, or tooling; a bad deposit could break the daemon or validators |
| `register-writing` | **HOLD FOR CEO** | Writes to governed registers (Forward, lessons-forge, DRAFTING_CYCLE.md); a bad deposit could corrupt governance state |

### Worked examples from real plans

1. **diagnostic-460** (this arc's census diagnostic): `class: read-only` → **AUTO-DEPOSIT.** Deposits one findings file at `knowledge/research/cycle-check-format-census-2026-08-19.md`. Reads `cycle_yields.py`, `plan_lint.py`, `fold_check.py`, `walk_register_lint.py`, and the Done/ corpus. Changes no code, no doctrine, no register. A bad auto-deposit wastes one diagnostic run.

2. **executable-464** (cycle_check.py builder): `class: governed-tooling` → **HOLD FOR CEO.** Writes `scripts/cycle_check.py` and `tests/test_cycle_check.py` — production tooling that other plans depend on. A bad deposit ships a broken validator.

3. **A forge-register append** (e.g. a lessons-forge codification): `class: register-writing` → **HOLD FOR CEO.** Writes to `DRAFTING_CYCLE.md` or `LESSONS.md` — governed doctrine. A bad deposit corrupts the governance record.

### Boundary case

A bellows-scripts write (e.g. a new `scripts/foo.py`) is `governed-tooling` → HOLD, not AUTO. The test is not "is it inside bellows/" but "does it write production code or tooling." A diagnostic that creates `knowledge/research/*.md` is `read-only` even though it writes a file — the file is a research artifact, not production code.

### Precise definition of `read-only`

A plan is `class: read-only` when its `writes:` paths are ALL in:
- `knowledge/research/` (findings files, census data)
- `scratchpad/` or session-local scratch directories
- Temporary/ephemeral artifacts that do not persist beyond the session

It writes NO:
- Governed register (Forward, LESSONS.md, DRAFTING_CYCLE.md, etc.)
- Production code (scripts/, src/, etc.)
- Schema or doc-of-record
- Test files (which ARE production code for the test suite)

A diagnostic that deposits a findings file at `knowledge/research/*.md` IS `read-only` by this definition. The test is blast radius: a bad auto-deposit of a research file costs one wasted diagnostic. A bad auto-deposit of production code costs a broken system.

### Depositor assignment rule

The depositor assigns `class:` from the plan's `writes:` paths:
1. If ALL `writes:` paths match `knowledge/research/*` or `scratchpad/*` → `read-only`
2. If ANY `writes:` path is a governed register or doctrine file → `register-writing`
3. Otherwise (production code, scripts, tests, schemas) → `governed-tooling`

Priority: `register-writing` > `governed-tooling` > `read-only`. The highest-stakes write determines the class.

---

## Output Receipt

**Status:** COMPLETE. All seven questions (Q0-Q6) answered.

**Deposits:** `knowledge/research/cycle-manifest-stanza-design-2026-08-19.md` (this file).

**CEO fork surfaced:** `yields:` vs §3 line 210's running-fold-count prohibition (Q1 conflict (i), Q5 gap (c)). Keeping `yields:` requires explicitly superseding a live §3 rule — the CEO's call. Recommendation: keep it (option A), amend the prohibition to scope it to the drafting phase.

**Open for downstream executable:** the §3 amendment itself, the `--emit-manifest` emitter, the plan_lint stanza check, and the depositor's collision query are all BUILD items in the Rule 27 Gap Assessment table (Q5). This diagnostic supplies the grammar + gap table; the executable implements it.
