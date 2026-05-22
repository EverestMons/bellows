# Bellows — `_consume_verdicts` drain failure on well-formed `resolved/` files
**Date:** 2026-05-21 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Today's session reproduced a runtime failure where `_consume_verdicts` did not drain two valid `resolved/` verdict files across multiple daemon rescan cycles AND a clean restart. Both files had canonical bare format (verified against a known-passing reference) and slug-matching filenames. Heartbeat correctly reported `2 awaiting verdict` — daemon knew both plans were paused but never paired them with the resolved verdict files. Operational mitigation required Planner-side manual close + shadow cache cleanup + verdict file recall.

This diagnostic characterizes how `_consume_verdicts` discovers `resolved/` files, derives their target slug, and pairs them with paused plans — and identifies why the pairing failed for both reproductions.

The full BACKLOG entry capturing the symptoms is at `bellows/knowledge/BACKLOG.md` (Open section, top entry dated 2026-05-21). Reference it for the full reproduction record including filenames, timing, and known-passing reference file.

**Scope:** read-only investigation of `bellows.py` and `verdict.py`. No fixes, no code changes. Findings deposit goes to `bellows/knowledge/architecture/`. The Planner reads findings and authors a separate executable if action is warranted.

## Two hypotheses already surfaced

Both come from the BACKLOG entry's analysis:

**H1 — Slug-extraction / pairing prefix mismatch.** The paused plan files use prefixes like `verdict-pending-diagnostic-fuel-continuation-inference-v2-2026-05-21.md` (slug after `verdict-pending-` strip is `diagnostic-fuel-continuation-inference-v2-2026-05-21`). The resolved verdict files were named `processed-verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md` (slug between `processed-verdict-` and `-step-N` is `fuel-continuation-inference-v2-2026-05-21` — note no `diagnostic-` prefix). If the pairing logic compares these slugs without normalizing for the `diagnostic-`/`executable-` prefix, the consumer skips both files even though they're well-formed. Same pattern affects the executable plan in the second reproduction.

**H2 — `processed-` filename prefix collision.** Hypothesis: Bellows reads `verdict-*` (no `processed-` prefix) at write time and applies `processed-` itself upon successful consume. If that's true, then verdict files written with `processed-` already in their filename look like already-consumed files to the scanner — they're either ignored entirely or treated as no-op.

Either hypothesis would explain the failure. Both could be true simultaneously. There could also be a third unrelated root cause that the BACKLOG entry's analysis missed.

---

## STEP 1 — Characterize the `_consume_verdicts` discovery and pairing logic

**Agent:** Bellows Systems Analyst
**Estimated tokens:** ~25k

### Read order

1. `bellows/knowledge/BACKLOG.md` — open section, top entry dated 2026-05-21. Read the full entry for the reproduction record and the two hypotheses already on the table.
2. `bellows/bellows.py` — `_consume_verdicts` method in full. Trace from the `resolved/` directory scan through to the verdict-pending plan match and the `processed-` rename. Identify every place a filename is parsed, every place a slug is extracted, every place a comparison is made.
3. `bellows/verdict.py` — any helper functions `_consume_verdicts` calls for slug extraction or filename parsing (e.g., `slug_from_path`, `extract_verdict`, similar). Read the full body of each helper, not just the signature.
4. `bellows/knowledge/architecture/` — scan for any prior SA architecture document on verdict consumption, lifecycle, or filename conventions. Read any that look relevant in full.
5. One known-passing reference file: `bellows/verdicts/resolved/processed-verdict-bellows-tier-1-batch-2026-05-21-step-1.md`. This file WAS consumed successfully today. Compare its filename + content shape to the two stuck files to identify any structural difference.
6. The two stuck files referenced in the BACKLOG entry — both at `bellows/verdicts/resolved/` (one may already have been recalled with `_PLANNER_RECALLED_` prefix; check both names). Read their actual content + verify their filename slug-extraction against the consumer logic.

Do NOT read source files beyond what's listed above unless they're called by the consumer's code path and you need to follow the call chain to understand it.

### Investigation questions

Answer each in the findings file. For each answer, cite the specific `bellows.py` or `verdict.py` line + the exact code snippet (no paraphrasing).

1. **Discovery scope.** What pattern (regex / startswith / endswith) does `_consume_verdicts` use to enumerate files in `resolved/`? Does it accept files whose names start with `verdict-` only, `processed-verdict-` only, or both? Does it exclude any prefix (e.g., `_PLANNER_RECALLED_`, `verdict-request-`)?

2. **Slug extraction from verdict filename.** Given a filename like `processed-verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`, what slug does the consumer extract? Show the exact regex / string manipulation. Does it strip `processed-` first, then `verdict-`, then `-step-N`? Or does it expect `verdict-` only (no `processed-`)?

3. **Slug extraction from plan filename.** Given a `verdict-pending-diagnostic-fuel-continuation-inference-v2-2026-05-21.md` file in a watched `decisions/` directory, what slug does the consumer (or its slug helper) extract for pairing? Does the slug include the `diagnostic-` prefix or strip it?

4. **Pairing comparison.** What's the exact comparison between the verdict-side slug and the plan-side slug? Equality? Substring? Normalized? If H1 is correct, the asymmetry should be visible here.

5. **Effect of writing a verdict file with `processed-` already in the filename.** Trace the code path: does the discovery scan find it? Does the slug extraction produce a usable slug? Does the pairing comparison succeed? Or is there a branch (e.g., "skip files that look already-processed") that silently drops it before pairing? If H2 is correct, the silent-drop should be visible here.

6. **Effect of writing a verdict file with `verdict-` (no `processed-`) prefix.** Repeat question 5's trace for the canonical write-time form. Confirm the working path actually works for the slug shapes used in today's reproductions.

7. **`_PLANNER_RECALLED_` interaction.** The Planner sometimes prefixes a stuck verdict file with `_PLANNER_RECALLED_` to take it out of the queue. Does the discovery scan exclude `_PLANNER_RECALLED_*` files? If not, what happens when one is encountered?

8. **Concrete root cause.** Of H1, H2, both, or a third cause, which is the actual reason the two reproductions today failed? Cite the line(s) that prove it.

9. **Resolution options.** List 2–3 concrete fix shapes (e.g., "normalize slug by stripping `diagnostic-`/`executable-`/`qa-` prefixes at the slug-helper level," "accept both `verdict-*` and `processed-verdict-*` filename shapes in discovery scan and reuse the same slug logic," etc.). For each, give a 1–2 line LOC estimate and call out behavioral risk (false positives, churn against passing tests).

10. **Existing test coverage.** Are there pytest tests today that exercise the `_consume_verdicts` discovery and slug-pairing path with realistic filename shapes? Identify by test name + file path. Note any gaps that would let H1 or H2 (or the actual root cause) slip through.

### Out of scope

- Do not propose or implement a fix. This diagnostic is characterize-only.
- Do not modify `bellows.py`, `verdict.py`, or any test file.
- Do not touch the two reproduction files in `bellows/verdicts/resolved/`. Read-only.
- Do not analyze the step-counter-loop-after-precondition-failure BACKLOG entry. Separate diagnostic.

### Deliverables

**Deposits:**
- `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md`

The findings file MUST include:
- A "Discovery and slug-extraction trace" section answering questions 1–7 with line citations and code snippets
- A "Root cause" section answering question 8 with the specific defective line(s) cited
- A "Resolution options" section answering question 9
- A "Test coverage" section answering question 10
- The standard SA Output Receipt block at the end

### STOP

Stop after Step 1. Do not author an executable. The Planner will read the findings, verify Rule 22, and then decide on fix scope + sequencing.
