verdict: continue

Planner verification (Rule 22(b)) — plan 335, Step 1. Gate clean; verification done by **re-measuring against the artifacts**, not by reading the dev log back.

## Verified independently

- **All four declared deposits landed**, committed as `efae953`: `scripts/cycle_yields.py` (12534 B), `tests/test_cycle_yields.py` (12002 B), the corpus capture (206352 B), and the step-1 dev log.
- **C1 holds — the tool has no write path.** Grep for write-mode `open(`, `write_text`, `writelines`, `shutil`, `os.remove`/`rename`, `--output`/`--fix` returns **0**. The tool emits on stdout; the step redirected.
- **I re-ran the tool myself.** Output reproduces the deposited capture.
- Step log: `success: True`, `terminal_reason: completed`, zero permission denials, empty stderr.

## The measurement

| | |
|---|---|
| files discovered under `Done/` | **1694** |
| carrying a `## Drafting Cycle` block | **61** |
| rows OK / UNPARSEABLE / NO_BLOCK | **342 / 194 / 1633** |
| origin ABSENT / PRESENT / PARTIAL | **342 / 0 / 0** |

## Two findings that outrank the pass

**1. `origin=PRESENT` is ZERO, the tool is correct, and the authoring premise was wrong.** The plan predicted two plans carrying an origin split (`diagnostic-322`, `executable-332`). That prediction came from a **file-level** `grep -l "fold-introduced"`, which matches the string anywhere in a file. Read at the right granularity, `executable-332` carries its origin data in a **narrative running-tally line** — *"Fold-origin classification (LESSONS 227), running: w1 7/7 pre-existing · a1 4/4 pre-existing…"* — while its per-lens lines read plainly `w1 2 folded; w2 1 folded`. Same shape in 322.

**So the fold-origin ratio is not sparse in the machine-readable record — it is absent from it entirely, 0 of 61.** The two plans that "have" it have it as prose. This is the collector working: it produced, on its first run, the finding that D5's headline metric cannot be computed from history at all, and that its value is wholly forward-looking. The plan's own instruction applies — *a difference from the authoring prediction is a finding to report, not an error to correct.*

**2. 194 of 536 block-derived rows are UNPARSEABLE — 36%**, against an authoring prediction of roughly eight files differing in shape. This is the field the plan insisted must never be a silent skip, and it is now the most interesting number in the corpus. **Step 2's QA must report it as a result, not treat it as a defect to be tuned away**; whether the parser should be widened is a decision for after the QA read, not during it.

## Recorded, not blocking

The deposited capture is missing the `# Discovery: 1694 files, 61 with Drafting Cycle block` comment line that the tool emits — the redirect dropped one line the tool produced. Minor evidence-integrity nick; noted so Step 2 does not treat the capture as byte-complete.

## Continue

Step 2 (QA) proceeds as written. Its Item 1 re-runs the tool against a **simultaneous** independent `find` count — not against Step 1's number — and reports any delta as corpus movement; that guard is now load-bearing, since this session has plans closing into `Done/` while the diagnostic runs.
