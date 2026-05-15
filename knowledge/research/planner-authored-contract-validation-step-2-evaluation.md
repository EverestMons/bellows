# Planner-Authored Contract Validation — Step 2 Evaluation

**Diagnostic:** `diagnostic-planner-authored-contract-validation-2026-05-12`
**Date:** 2026-05-12

---

## Part 3 — Per-Artifact A/B/C Recommendation

### Artifact 1: Verdict File Content — Recommend A+C (Schema Validator + Observability)

The verdict file content contract is the system's most dangerous silent-skip surface. Three incidents in 12 days (2026-05-01, 2026-05-09, 2026-05-12) — each time, correctly-intended verdicts were silently discarded because the format didn't match the regex, causing plans to strand for hours. The root problem is that `check_verdict()` returns `{"found": False}` for both "file doesn't exist" and "file exists but format is wrong" — the caller cannot distinguish between a not-yet-authored verdict and a malformed one. A schema validator (A) should intercept the file after `read_text()` and before the regex match: if the file exists and is non-empty but the first line doesn't match the verdict pattern, log a `WARN` or `ERROR` with the actual first line contents and the expected format, and post a Pushover notification. This transforms the silent-skip into a loud failure without changing the parse path. Observability (C) is cheap additive insurance — log every file scanned in `verdicts/resolved/` and its parse outcome. Writer helper (B) is inappropriate here because the Planner authors verdicts during asynchronous review sessions where Bellows is not in the execution path — there is no natural call site for a helper.

**LOC estimate:** ~25 (validator) + ~10 (logging) = ~35

---

### Artifact 2: Verdict Filename/Directory — Recommend A+C (Schema Validator + Observability)

The Planner must deposit verdict files to `verdicts/resolved/` with filename `verdict-{slug}-step-{N}.md` — but no feedback exists when the file lands in the wrong directory or with a wrong name. The 2026-05-12 wrong-directory incident (Planner wrote to `verdicts/pending/` instead of `verdicts/resolved/`) is structurally identical to Artifact 1's silent-skip problem. A validator (A) should scan `verdicts/pending/` for files that look like verdict responses (not verdict-requests) — i.e., files starting with `verdict-` but not `verdict-request-` — and log a warning: "verdict file found in pending/ instead of resolved/; expected location is verdicts/resolved/". This is a directory-level validator, not a file-content validator. Writer helper (B) is inappropriate for the same reason as Artifact 1 — async authoring context with no Bellows execution path. Observability (C) adds the file-level scan logging.

**LOC estimate:** ~20 (directory validator) + ~5 (logging) = ~25

---

### Artifact 3: Plan Headers — Recommend C (Observability-only)

Plan headers have failed once (2026-05-10 multi-line bold gap) but the failure mode is silent acceptance with downstream drift, not silent skip. The 2026-05-10 fix extended `_parse_plan_header()` to handle multi-line bold format, and `_apply_defensive_header_defaults()` provides a belt-and-suspenders backstop setting `pause_for_verdict = after_step_1` when the header looks thin. A full schema validator (A) is disproportionate because the header format is intentionally flexible (YAML or Markdown) and the Planner's format choices evolve — a rigid validator would require constant schema updates. Writer helper (B) is inappropriate because headers are part of the plan file itself, authored inline with the plan body. Observability (C) is the right response: when `_parse_plan_header()` returns fewer than 3 keys, the existing warning about missing keys (shipped 2026-05-10) already provides loud feedback. The current state is adequate.

**LOC estimate:** ~0 (already shipped via 2026-05-10 observability fix)

---

### Artifact 4: Step Headers (`## STEP N`) — Recommend C (Observability-only)

Step headers have a loud failure path for case mismatches (the `WARN` log at `bellows.py:190`) and a defensive fallback for zero-header diagnostics (`total_steps = 1`). The 2026-05-10 code-fence incident was fixed structurally by `strip_fenced_code_blocks()`. A schema validator (A) adds no value beyond the existing case-mismatch warning. Writer helper (B) is impractical — step headers are structural elements of the plan body, not standalone files. Observability (C) is already partially shipped (the case-mismatch warning). The one gap: when `extract_total_steps()` returns 0 for a non-diagnostic plan, there is no log. Adding a single warning line for that case would close the observability gap.

**LOC estimate:** ~5 (one warning for zero-count non-diagnostic plans)

---

### Artifact 5: Deposits Blocks — Recommend C (Observability-only)

Deposits blocks already have the loudest failure mode in the system — `deposit_exists` gate failures surface immediately in verdict requests with explicit evidence text. The two historical incidents (2026-05-07 path convention mismatch, 2026-04-19 prose pattern false positives) were both fixed: Rule 26 governance tightened the authoring convention (2026-05-11), and `_extract_plan_required_deposits()` now prefers the block format over legacy prose (2026-04-19). A schema validator (A) would duplicate the gate's existing validation. Writer helper (B) is inappropriate — deposits blocks are authored inline within plan steps. The current loud-failure mode is the correct architectural response. No additional LOC needed.

**LOC estimate:** ~0 (existing gate is sufficient)

---

### Artifact 6: Rule 20 Self-Check Banner — Recommend C (Observability-only)

The Rule 20 self-check was structurally fixed by the 2026-05-10 single-source migration. The Planner no longer authors the block — it references `RULE_20_SELF_CHECK_BLOCK.md`. The one post-migration incident (2026-05-10 banner substitution) was a transitional artifact, not a recurring failure. The existing `rule_20_self_check` gate provides loud failure feedback. Schema validation (A) would duplicate the gate. Writer helper (B) was effectively already shipped — the single-source canonical file IS the writer helper (Planner references the file instead of authoring the block). No additional LOC needed.

**LOC estimate:** ~0 (single-source + gate is sufficient)

---

### Artifact 7: Agent Output Markers — Recommend C (Observability-only)

Agent output markers (`### Flags for CEO`, `VERDICT_REQUESTED:`) are explicitly documented as safety-net parsers. Primary detection is via plan headers (`pause_for_verdict`) and agent-authored verdict-request files. Zero historical failures. The Planner's role is indirect — it instructs agents to emit markers via plan step text. A validator or helper is disproportionate for a safety-net with no known failures. Observability is already implicit (the `parse()` function returns structured results consumed by gates). No additional LOC needed.

**LOC estimate:** ~0 (safety-net; no change warranted)

---

## Part 4 — Cross-Cutting Pattern Observation

**Raw counts:** 0 of 7 artifacts recommend B (helper). 2 of 7 recommend A+C (validator + observability). 5 of 7 recommend C (observability-only).

**Pattern:** Recommendations split across two responses (A+C and C), with strong convergence on C. This is a **per-artifact case-by-case** outcome, not a library-level architectural response.

**Explanation:** The convergence on C reflects two structural factors:
1. **Loud-failure gates already cover 3 artifacts** (5: deposits, 6: Rule 20, 7: agent markers) — these need no additional validation because they already fail visibly.
2. **Async authoring context blocks B for the highest-risk artifacts** (1: verdict content, 2: verdict filename) — the Planner authors verdicts during CEO review sessions where no Bellows helper is available.
3. **The only artifacts warranting A** are the two verdict-lifecycle artifacts (1 and 2) where silent-skip failure has caused real operational damage (plans stranded for hours, 3 incidents in 12 days).

The right architectural move is: **ship A+C for the verdict lifecycle (Artifacts 1-2), accept C for everything else.** This is not a writer-helper-library problem — it is a verdict-observability problem.

---

## Part 5 — Implementation Cost Summary and Prioritization

| # | Artifact | Recommended Response | LOC Estimate | Priority |
|---|---|---|---|---|
| 1 | Verdict file content | A+C (validator + logging) | ~35 | **High** — failed within 30 days (2026-05-12) AND silent-skip failure mode |
| 2 | Verdict filename/directory | A+C (validator + logging) | ~25 | **High** — failed within 30 days (2026-05-12) AND silent-skip failure mode |
| 3 | Plan headers | C (observability-only) | ~0 | **Low** — failed within 30 days (2026-05-10) but already fixed; silent-acceptance mode has defensive backstop |
| 4 | Step headers | C (observability-only) | ~5 | **Medium** — no recent failure but silent-skip mode for zero-count non-diagnostic edge case |
| 5 | Deposits blocks | C (existing gate) | ~0 | **Low** — recent failure but loud-failure mode (CEO sees gate failures) |
| 6 | Rule 20 banner | C (existing gate + single-source) | ~0 | **Low** — structurally fixed; loud-failure mode |
| 7 | Agent output markers | C (safety-net, no change) | ~0 | **Low** — no known failure; safety-net only |

**Total LOC for new work:** ~65 (Artifacts 1-2 only; all others already adequate)

**Summary:** 2 artifacts need active intervention (verdict content + verdict filename/directory validators). 5 artifacts are adequately covered by existing gates, observability, or structural fixes. The highest-priority work is a verdict-lifecycle validator that transforms the silent-skip failure mode into a loud failure — this addresses the system's most dangerous and most frequently recurring failure surface.

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/planner-authored-contract-validation-2026-05-12/
Files verified: 3
```

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 2
**Status:** Complete

### What Was Done
Evaluated three architectural responses (A: schema validator, B: writer helper, C: observability-only) for each of the 7 Planner-authored artifacts enumerated in Step 1. Produced per-artifact recommendations, cross-cutting pattern analysis, and a prioritized implementation summary table.

### Files Deposited
- `bellows/knowledge/research/planner-authored-contract-validation-step-2-evaluation.md` — per-artifact A/B/C evaluation, cross-cutting pattern, priority table
- `bellows/knowledge/qa/evidence/planner-authored-contract-validation-2026-05-12/consumer-code-grep-transcripts.md` — parser entry points and contract assumptions
- `bellows/knowledge/qa/evidence/planner-authored-contract-validation-2026-05-12/reproduction-quotes.md` — historical reproduction quotes per artifact
- `bellows/knowledge/qa/evidence/planner-authored-contract-validation-2026-05-12/cross-cutting-pattern-counts.md` — raw recommendation distribution counts

### Files Created or Modified (Code)
- None (read-only audit)

### Decisions Made
- Recommended A+C (validator + observability) for verdict content and verdict filename/directory — grounded in 3+ silent-skip incidents in 12 days
- Recommended C (observability-only) for plan headers, step headers, deposits blocks, Rule 20 banner, and agent output markers — existing gates and structural fixes are adequate
- Classified the pattern as per-artifact case-by-case (A+C vs C split), not a library-level response

### Flags for CEO
- The two high-priority items (verdict content validator, verdict filename/directory validator) total ~65 LOC and address the system's most frequently recurring failure surface

### Flags for Next Step
- None (diagnostic terminal step)
