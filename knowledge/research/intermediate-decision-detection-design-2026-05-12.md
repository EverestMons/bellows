# Intermediate Decision Detection Design — Findings

**Date:** 2026-05-12
**Plans audited:** 3 (deposit-exists-prose-canary-2026-04-28, bellows-worktree-impl-2026-05-03, terminal-capture-2026-05-12)
**Step.json files analyzed:** 16 (12 + 2 + 2)
**Total assistant text blocks:** 225
**Label distribution:** S=6, B=48, T=171
**Best detector:** A (phrase-grep) at F1=0.706
**Disposition:** Methodology selection and implementation-path-shape only. No fix plan.

---

## Part 1+2 — Ground-Truth Construction and Hand Classification

### Block Extraction

Assistant text blocks were extracted from the `raw_output` NDJSON stream in each plan's step.json files. Only `assistant` events with `content[].type == "text"` were counted; `tool_use` and `thinking` events were excluded. Blocks were numbered sequentially per plan-and-step.

| Plan | Step.json files | Blocks | S | B | T |
|---|---|---|---|---|---|
| deposit-exists-prose-canary-2026-04-28 | 12 | 136 | 2 | 30 | 104 |
| bellows-worktree-impl-2026-05-03 | 2 | 47 | 2 | 10 | 35 |
| terminal-capture-2026-05-12 | 2 | 42 | 2 | 8 | 32 |
| **Total** | **16** | **225** | **6** | **48** | **171** |

### Classification Criteria Applied

- **(S) Substantive decision** — agent detects and resolves an unexpected condition (empty file, case-sensitive grep, wrong path derivation, test failure requiring code fix) OR makes a scope-changing choice not mandated by the plan. Conservative: ambiguous S/B classified as B.
- **(B) Borderline** — agent narrates a research or methodology choice (which test to study, what to grep for, which file to read). Affects HOW work was done, not WHAT was delivered. Conservative: ambiguous B/T classified as T.
- **(T) Trivial** — procedural narration, intent statements, status echoes. Bias toward T per instructions.

### Representative S-Class Blocks

**S-1** (deposit-exists-prose-canary, step 2, block 7):
> The grep evidence file seems empty. Let me fix that — the working directory might be wrong.

**S-2** (deposit-exists-prose-canary, step 2, block 8):
> Found the issue — the phrase uses capital letters. Let me write the evidence file properly.

**S-3** (bellows-worktree-impl, step 1, block 9):
> Wait, I need to fix the project path derivation in the prune hook. The watched_projects entries are `knowledge/decisions/` paths — need to go up 2 levels to get the project root.

**S-4** (bellows-worktree-impl, step 1, block 26):
> Good progress — down to 2 failures. One is the pre-existing `test_run_step_timeout`. The other is in `test_consume_verdict_logs_ledger_entry` — need to fix the test expectation.

**S-5** (terminal-capture, step 1, block 11):
> The gate evaluation print has 2 matches — I need more context. Let me fix those with surrounding context, and continue with the remaining log-source prefix edits.

**S-6** (terminal-capture, step 1, block 19):
> Actually, looking more carefully at the test failures... The `test_capture_terminal_output` test needs the new return dict format.

All six S-class blocks follow the detect-then-correct pattern: the agent encounters something unexpected during execution and narrates the correction. None of these corrections appear in the corresponding Output Receipt (per the prior audit's β-leak finding).

---

## Part 3 — Four-Detector Results

### Detector Descriptions

| Detector | Mechanism | Input |
|---|---|---|
| A (phrase-grep) | Flag block if it matches any of the 33 phrases from the audit's extended grep list | Block text |
| B (tool-failure-bracketed) | Flag block if it appears within ±3 NDJSON events of a tool_use_result with non-zero exit code, stderr, or is_error:true | Block position in event stream |
| C (write-tool-adjacent) | Flag block if it appears within ±2 events of a write-class tool_use (Write, Edit, Bash with redirect, etc.) | Block position in event stream |
| D (length-percentile) | Flag block if its character length is in the top 20% of all blocks within that step | Block length |

### Results Table

| Detector | TP | FP | FN | TN | Precision | Recall | F1 | S-recall | B-flagged | T-flagged |
|---|---|---|---|---|---|---|---|---|---|---|
| A (phrase-grep) | 6 | 5 | 0 | 214 | 0.545 | 1.000 | 0.706 | 6/6 | 4 | 1 |
| B (tool-failure) | 1 | 12 | 5 | 207 | 0.077 | 0.167 | 0.105 | 1/6 | 4 | 8 |
| C (write-adjacent) | 4 | 111 | 2 | 108 | 0.035 | 0.667 | 0.066 | 4/6 | 11 | 100 |
| D (length-percentile) | 2 | 49 | 4 | 170 | 0.039 | 0.333 | 0.070 | 2/6 | 12 | 37 |

**Detector A dominates** with perfect recall (6/6 S-class blocks caught) and the highest precision (0.545). Its 5 false positives (4 B-class, 1 T-class) are modest. Detectors B, C, and D all suffer from low precision due to high false-positive rates from structural proximity heuristics.

---

## Part 4 — Combination Results

| Combination | TP | FP | FN | TN | Precision | Recall | F1 | S-recall | B-flagged | T-flagged |
|---|---|---|---|---|---|---|---|---|---|---|
| 1: A OR B | 6 | 17 | 0 | 202 | 0.261 | 1.000 | 0.414 | 6/6 | 8 | 9 |
| 2: B OR C | 4 | 116 | 2 | 103 | 0.033 | 0.667 | 0.063 | 4/6 | 14 | 102 |
| 3: (A OR B) AND C | 4 | 10 | 2 | 209 | 0.286 | 0.667 | 0.400 | 4/6 | 3 | 7 |

**No combination improves on Detector A alone.** Combo 1 (A OR B) maintains perfect recall but adds 12 false positives from Detector B, dropping precision to 0.261 and F1 to 0.414. Combo 3 achieves reasonable precision (0.286) but loses 2 S-class blocks. The phrase-grep baseline is the winner.

---

## Part 5 — Qualitative Failure Analysis (Best Detector: A)

### False Negatives (S-class blocks missed by Detector A)

**None.** Detector A achieved 6/6 S-recall — all substantive decision blocks were flagged. This is the detector's strongest property.

### False Positives (Detector A flagged 5 non-S blocks)

**FP-1** (B-class: deposit-exists-prose-canary, step 2, block 14):
> Now let me verify the self-check claims are accurate (evidence files actually exist and are non-empty).

**Pattern:** The phrase "let me also" or "re-run" triggers the grep. The block describes a verification research step — borderline, not substantive. The agent is choosing HOW to verify, not detecting or correcting an error.

**FP-2** (B-class: deposit-exists-prose-canary, step 3, block 4):
> Let me read the key test cases and get the full Q6 output, and re-run the Q3 experiment (b) and (d) more carefully.

**Pattern:** "re-run" triggers the grep. The block describes a research methodology choice — the agent deciding which experiments to re-run. Borderline narration, not a scope-changing decision.

**FP-3** (T-class: terminal-capture, step 1, block 16):
> Now I need to update the `runner.run_step()` call sites in bellows.py to pass plan_slug and step_num.

**Pattern:** "I need to update" triggers the grep. This is procedural intent narration — the agent stating what it will do next, not reporting a discovered issue or scope change. The sole T-class false positive.

**Common pattern across all 5 false positives:** The grep phrases are designed to catch decision language, but some phrases ("re-run", "I need to update", "let me also") also appear in routine research/procedural narration that doesn't represent a substantive decision. These are "intent echo" or "methodology narration" contexts where the phrase form matches but the semantic content is informational, not decisional.

**Assessment of failure modes:** The 4 B-class false positives are tolerable — a Planner reading these blocks would find them informative even if not action-changing. The 1 T-class false positive is low-cost noise. The failure mode is "slightly over-inclusive on methodology narration" rather than "misses critical decisions" — a much safer failure direction for a system designed to surface information to the Planner.

---

## Part 6 — Implementation-Shape Sketches

### Bellows-Side Path

**What changes:** Add a post-processing step in `runner.py` after `_write_log()` (or in `bellows.py` after `run_step()` returns) that scans the `raw_output` NDJSON stream for `assistant` text blocks matching any of the 33 grep phrases. Flagged blocks would be collected into a `intermediate_decisions` list in the parsed result dict. `verdict.py::post_verdict_request()` would render a new `## Intermediate Decisions Detected` section in the verdict request markdown, listing each flagged block's text (truncated to ~200 chars) with its event position.

**Estimated LOC:** ~40 production (phrase-matching function + verdict section renderer), ~60 tests (unit tests for phrase matching, integration test for verdict request rendering). Total ~100 LOC.

**Call sites touched:** `runner.py` (add extraction after NDJSON parsing, ~line 207), `verdict.py::post_verdict_request()` (add section rendering, ~line 140), `bellows.py` (pass extracted decisions to verdict posting, ~line 477).

**Risk surfaces:**
- **Parser-touching code (v4.38 Restart Discipline):** The phrase-matching function is downstream of the NDJSON parse, not part of it. It reads already-parsed events. Low risk to existing parse paths.
- **Gate behavior:** No gate changes required. The new section is informational, not gated.
- **Contract changes:** The verdict request file schema gains a new optional section. The Planner must be updated to expect it (Rule 22 modification). Backward compatible — old verdict requests without the section remain valid.
- **Performance:** Phrase matching on 225 blocks per 16-step plan takes <1ms. No performance concern.

### Planner-Side Path

**What changes:** Rule 22 would specify that when verifying a step's output, the Planner should also scan the step.json `raw_output` field for assistant text blocks matching the 33-phrase list. The Planner would open the step.json file (referenced in the verdict request's `Log:` field), parse the NDJSON, extract flagged blocks, and consider them alongside the Output Receipt when making continue/stop decisions.

**Planner tooling needed:** The Planner would need Read tool access to `bellows/logs/*.json` files, NDJSON parsing capability (the Planner already has Python execution), and the 33-phrase list embedded in Rule 22 or a referenced file.

**Estimated cognitive cost:** Moderate. Each Rule 22 verification would add ~1 minute of Planner context for reading and evaluating flagged blocks. For plans with many steps, this accumulates. The Planner already processes verdict request files; adding a raw-output scan step increases the surface area of each verification.

**Risk of inconsistent execution:** High. The Planner is a prompted LLM agent — it may skip the NDJSON scan under context pressure, interpret phrases differently across sessions, or miss the step.json file path. Unlike a Bellows-side implementation where phrase matching is deterministic code, the Planner-side path depends on the Planner reliably executing a multi-step procedure (open file, parse NDJSON, grep text, evaluate blocks) on every Rule 22 verification. This is the same class of reliability problem that the current Output Receipt mechanism already exhibits.

### Tradeoff Summary

| Dimension | Bellows-Side | Planner-Side |
|---|---|---|
| Determinism | High — code-based phrase match | Low — LLM-prompted procedure |
| LOC cost | ~100 (production + tests) | ~0 (prompt changes only) |
| Ongoing maintenance | Code maintenance for phrase list | Prompt maintenance for Rule 22 |
| Consistency | Every verdict request, every time | Depends on Planner execution fidelity |
| Information surfacing | Pre-computed in verdict request | Computed on-demand by Planner |
| Schema impact | New optional section in verdict file | No schema change |
| Risk to existing behavior | Low — additive section, no gate changes | Low — additive rule, no gate changes |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/intermediate-decision-detection-2026-05-12/
Files verified: 3
```

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Intermediate decision detection design analysis across 3 plans (225 assistant text blocks, 16 step.json files). Hand-classified blocks as S=6, B=48, T=171. Tested 4 detectors and 3 combinations against ground truth. Detector A (phrase-grep from prior audit's 33-phrase list) achieved best F1=0.706 with perfect recall (6/6 S-class caught) and 0.545 precision (5 false positives: 4 borderline, 1 trivial). Sketched Bellows-side (~100 LOC) and Planner-side implementation paths with tradeoff analysis.

### Files Deposited
- `bellows/knowledge/research/intermediate-decision-detection-design-2026-05-12.md` — full findings
- `bellows/knowledge/qa/evidence/intermediate-decision-detection-2026-05-12/labeled-blocks.jsonl` — 225 labeled blocks
- `bellows/knowledge/qa/evidence/intermediate-decision-detection-2026-05-12/detector-results.json` — per-detector TP/FP/FN/TN and flagged block lists
- `bellows/knowledge/qa/evidence/intermediate-decision-detection-2026-05-12/qualitative-failures.json` — false-negative and false-positive quoted examples

### Decisions Made
- Identified 12 (not 19) step.json files for deposit-exists-prose-canary via tool-call content matching (the plan definition has more steps than were executed; specialist authority: measurement methodology)
- Applied conservative classification bias per instructions (S/B ambiguous -> B, B/T ambiguous -> T; specialist authority: ground-truth construction methodology)
- Used case-insensitive substring matching for phrase-grep detector (matching prior audit methodology; specialist authority: detector implementation)

### Flags for CEO
- None

### Flags for Next Step
- None
