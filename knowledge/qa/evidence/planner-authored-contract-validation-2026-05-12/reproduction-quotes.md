# Reproduction Quotes — Planner-Authored Contract Validation

**Date:** 2026-05-12

---

## Artifact 1: Verdict File Content — 3 Known Reproductions

### Reproduction 1 (2026-05-01): 13 stranded verdict files
**Source:** `Done/executable-lessons-verdict-format-and-stranded-plans-2026-05-01.md`
> "Rule 25 documented `continue\n{reason}` but `bellows/verdicts/README.md` requires the literal `verdict:` prefix. The Planner stranded 13 verdict files."

### Reproduction 2 (2026-05-09): 14 stranded verdict files
**Source:** `Done/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09.md`
> "Bug A: Format intolerance in `check_verdict()` (`verdict.py:157`). The regex `r'^verdict:\s*(continue|stop)$'` rejects bare `continue`/`stop` first lines."
> "14 stranded verdict files were silently rejected due to format mismatch"

### Reproduction 3 (2026-05-12): 4 verdict files in novel format
**Source:** `in-progress-executable-governance-lessons-verdict-format-2026-05-12.md`
> Planner authored four verdict files in a self-invented format that Bellows could not parse. Two plans stuck ~2 hours awaiting verdict.

---

## Artifact 2: Verdict Filename/Directory — 1 Known Reproduction

### Reproduction 1 (2026-05-12): Wrong directory
**Source:** `knowledge/architecture/consume-verdicts-not-processing-2026-05-12.md`
> Planner deposited two verdict files to `verdicts/pending/` instead of `verdicts/resolved/`. The verdict consumer (`_consume_verdicts` at line 1048) scans only `verdicts/resolved/`, making the correctly-formatted files invisible.

---

## Artifact 3: Plan Headers — 1 Known Reproduction

### Reproduction 1 (2026-05-10): Multi-line bold parse gap
**Source:** `Done/executable-header-parser-multiline-fix-2026-05-10.md`
> "Diagnostic empirically confirmed via REPL fixtures (multi-line bold returned `{'project': 'bellows'}` while pipe format returned 6 keys)"
> "Three affected plans identified in Done/, zero in-flight risk."

---

## Artifact 4: Step Headers — 1 Known Reproduction

### Reproduction 1 (2026-05-10): Code-fence false positives
**Source:** BACKLOG Closed 2026-05-10
> "Cosmetic anomaly during dispatch: Bellows ran 4 dispatches instead of 2 because `extract_total_steps()` counted `## STEP N` patterns inside test-fixture string literals embedded in plan prose."

---

## Artifact 5: Deposits Blocks — 2 Known Reproductions

### Reproduction 1 (2026-05-07/08): Path convention mismatch
**Source:** `Done/diagnostic-deposit-exists-false-positive-audit-2026-05-11.md`
> "18 gate-failure lines across 3 verdict requests (action-queue-aggregation, action-queue-limit-and-contract-name, bellows-qa-prefix-and-skip-logging). Mechanism: plans declared bare `evidence/foo.txt` paths in `**Deposits:**` blocks while agents created files at `knowledge/qa/evidence/<slug>/foo.txt`."

### Reproduction 2 (2026-04-19): Prose pattern false positives
**Source:** `Done/executable-rule-26-deposit-parser-scope-2026-04-19`
> "Three failure signatures: bracketed-template paths inside embedded specialist content; test-fixture strings embedded inside QA-step prompt text; literal placeholder paths inside code-fence example blocks."

---

## Artifact 6: Rule 20 Self-Check Banner — 1 Known Reproduction (post-single-source)

### Reproduction 1 (2026-05-10): Banner substitution
**Source:** BACKLOG Closed 2026-05-10 (startup-sweep-extract)
> "Step 2 tripped `rule_20_self_check` gate due to Planner banner substitution; overridden via continue verdict after Rule 22 verification."

---

## Artifact 7: Agent Output Markers — No Known Reproductions

No known reproduction. Safety-net parser with zero historical failures.
