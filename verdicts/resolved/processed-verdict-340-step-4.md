verdict: continue

Report verified. Continuing to Step 5 (QA), the terminal step.

- reports/lessons-report-2026-08-10.md deposited, 306 lines.
- **Total proposals: 41** — matching the derived expectation exactly.
- Categories 39 governance_rule + 2 instrumentation = 41.
- Route lines: grep -Fc -- returned 0, exit 1 (the expected no-match
  result, and the exit code is the evidence the check RAN). Every insert
  left route NULL, so Gate 1 has not walked in-window.
- Overlap lines: 0, exit 1. The detector retired by plan 207 has not
  reappeared.
- Live re-query: proposed+ambiguous = 41, all 41 with entry_id > 265, so
  the surfaced set is ours and nothing foreign is in it. Q2_INTACT=42.

A THIRD DRAFTING-CYCLE FOLD IS NOW PROVEN ON A LIVE RUN. Walk 0's finding
f7 rewrote this step's derived expectation: plan 311 derived surfaced
proposals as <pre-ingest NT_COUNT> + <classified>, which on this corpus
predicts 42 + 41 = 83. generate_lessons_report selects WHERE status IN
('proposed','ambiguous') (source read, src/lessons_forge.py:536-543), and
none of the 42 accepted rows are in that predicate. The corrected
derivation is SURFACEABLE_BASE + classified = 0 + 41 = 41, and the report
returned exactly 41. The clone's formula would have HALTed a correct run
at this step.

That makes three folds that each prevented a false halt on the two live
runs: the lowercase detector sentinel and the unpinned reference byte
length (both Plan A, Step 1), and this one. The drafting cycle's cost is
now answerable with three named instances rather than an argument.

FORWARD 46: steps table 4 rows (36/37/36/40 turns); 2 declared deposits
for this step, both present.

Rule 22(b) passes. Self-issued under delegated verdict authority.
