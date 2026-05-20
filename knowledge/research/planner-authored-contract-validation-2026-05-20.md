# Planner-Authored Contract Validation Surface — Diagnostic Findings

**Diagnostic:** `diagnostic-planner-authored-contract-validation-2026-05-20`
**Date:** 2026-05-20
**Agent:** Bellows Systems Analyst
**Context:** Successor to the 2026-05-12 two-step diagnostic. Since that audit, three validators have shipped (verdict content, verdict directory, dispatch-mode). At least three more contract-mismatch failures have been observed (verdict file format 2026-05-12; Rule 26 evidence paths 2026-05-11; Dispatch Mode header field 2026-05-20). This diagnostic produces the full surface enumeration and coherent shipping plan for the remaining gap.

---

## Q1 — Planner-Authored Artifacts with Strict Downstream Contracts

Nine distinct artifact types identified. Each is a file (or file region) the Planner authors that a deterministic Bellows component subsequently parses against a strict shape contract.

### Artifact Table

| # | File Type / Path Pattern | Consuming Component | Contract Shape | Parser Failure Mode | Current Bellows-Side Validation |
|---|---|---|---|---|---|
| 1 | **Verdict file content** `verdicts/resolved/verdict-{slug}-step-{N}.md` | `verdict.py:check_verdict()` line 207 | First line must match `^(?:verdict:\s*)?(continue\|stop)$` (case-insensitive). Lines 2+ are free-text reason. | Returns `{"found": False}` — caller silently skips (bellows.py:1160-1161). | **SHIPPED 2026-05-12:** WARN log to stderr + Pushover notification via `_notify_malformed_verdict()` (verdict.py:172-185, 209-210). `VERDICT_PARSE_LOG_VERBOSE` debug toggle. |
| 2 | **Verdict filename** `verdict-{slug}-step-{N}.md` | `bellows.py:_consume_verdicts()` line 1123 | Filename must match `^verdict-(.+)-step-(\d+)\.md$`. Must NOT start with `verdict-request-`. | Silent `continue` — file ignored without log (bellows.py:1118-1125). | None. No validator fires on malformed verdict filenames in `resolved/`. |
| 3 | **Verdict file directory** `verdicts/resolved/` | `bellows.py:_consume_verdicts()` line 1111 | Verdict files must be deposited in `verdicts/resolved/`, not `verdicts/pending/` or elsewhere. | File never scanned — `_consume_verdicts()` only reads `resolved/`. | **SHIPPED 2026-05-12:** `_scan_misplaced_verdicts()` (bellows.py:1083-1104) scans `pending/` for misplaced verdict response files. WARN log + Pushover. |
| 4 | **Plan header fields** Bold-Markdown or YAML frontmatter at top of plan files | `gates.py:_parse_plan_header()` lines 50-116 | Either YAML frontmatter (`---\n...\n---\n`) or bold-Markdown (`**Key:** value \| **Key:** value` or multi-line `**Key:** value`). Expected keys: `date`, `tier`, `dispatch_mode`, `pause_for_verdict`, `auto_close`, `project`, `author`, `total_steps`. | Returns `{}` on parse failure — downstream silently operates with default values. `pause_for_verdict` absent → potential unintended auto-advance. | **PARTIAL:** (a) Defensive default `_apply_defensive_header_defaults()` at bellows.py:313-322 sets `pause_for_verdict=after_step_1` when sparse header on multi-step plan. (b) Missing-keys warning at bellows.py:412-415 logs which keys are absent. (c) **SHIPPED 2026-05-19:** `validators.py:check_missing_dispatch_mode()` rejects plans without `dispatch_mode` field. |
| 5 | **Plan filename pattern** `(executable\|diagnostic\|qa)-*.md` | `bellows.py:is_runnable_plan()` line 922 | Filename must match `^(parallel-\d+-)?(executable\|diagnostic\|qa)-.*\.md$`. Must NOT start with `in-progress-`, `verdict-pending-`, or `halted-`. | Returns `False` — plan silently never dispatched. | **PARTIAL:** Advisory log at bellows.py:953-957 warns when a `.md` file fails the prefix filter (added 2026-05-08). But only fires for files that pass other filters and are not already in `_seen`. |
| 6 | **Step headers** `## STEP N` in plan body | `bellows.py:extract_total_steps()` lines 210-216; `gates.py:_extract_step_text()` lines 282-291; `verdict.py:_extract_step_text_from_plan()` lines 39-48 | Must be `## STEP N` (H2 + space + STEP + space + digits). Code fences stripped before matching. Case-insensitive match but warns on case mismatch. | `extract_total_steps()` returns 0 — for non-diagnostics, plan is SKIPPED and moved to Done/ (bellows.py:405-410). For diagnostics, defaulted to 1 step. `_extract_step_text()` returns `None` — gates skip deposit/scope checks for that step. | Case-mismatch WARN at bellows.py:214-215. Zero-step WARN at bellows.py:406. Fence-stripping at all three parsers. |
| 7 | **Deposits blocks** `**Deposits:**` in plan step text | `gates.py:_extract_plan_required_deposits()` lines 301-348; `verdict.py:extract_primary_deposit()` lines 51-79 | Rule 26 block format: `**Deposits:**` on own line, followed by `- \`path\`` bullets. Inline format: `**Deposits:** \`- path\``. Legacy prose fallback. | Extraction returns empty set — `deposit_exists` gate cannot fire for missing-from-plan deposits (no false negative, but no contract enforcement). When deposit is listed but doesn't exist: gate_failure (LOUD). | **ADEQUATE:** `deposit_exists` gate (gates.py:248-279) produces loud gate_failure with specific evidence text. Rule 26 governance convention tightened 2026-05-11. `_filter_transient_paths()` excludes `_staging_*` basenames. |
| 8 | **Rule 20 self-check banner** in QA deposits | `gates.py:_gate_rule_20_self_check()` lines 351-402 | QA `.md` deposits must contain literal `"Rule 20 — QA Self-Check Results"` followed by a line matching `^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED`. | gate_failure with specific evidence text. | **ADEQUATE:** Single-sourced at `RULE_20_SELF_CHECK_BLOCK.md` since 2026-05-10. Planner no longer authors the block. Gate provides loud failure. Bold-tolerance shipped 2026-05-17. |
| 9 | **Verdict request file fields** `verdicts/pending/verdict-request-{slug}-step-{N}.md` | `bellows.py:_consume_verdicts()` lines 1142-1157 | Parsed line-by-line for `**Plan:**`, `**Total Steps:**`, `**Pause Reason Code:**` fields. These are Bellows-authored (by `verdict.py:post_verdict_request()`), not Planner-authored — but the Planner uses `Total Steps` for continue-to-done decisions. | Missing fields default to `None`. `total_steps=None` triggers fallback chain (shadow → load_file → extract). Graceful degradation, not failure. | N/A — Bellows-authored, not a Planner contract surface. Included for completeness; excluded from Q2-Q6. |

### Additional Parser Entry Points (excluded — not Planner-authored)

- `extract_step_number()` at bellows.py:193-197 — parses `**Step:** N` from **agent** output
- `_perform_startup_sweep()` at bellows.py:1298 — parses `^verdict-request-(.+)-step-\d+\.md$` from **Bellows-authored** verdict request files
- `slug_from_path()` at verdict.py:82-92 — utility, no format contract
- `decisions.py:extract_decision_blocks()` — parses **agent** NDJSON output, not Planner-authored
- `parser.py:parse()` — extracts `### Flags for CEO` and `VERDICT_REQUESTED:` from **agent** output

---

## Q2 — Failure Mode Classification Per Artifact

| # | Artifact | Detectability | Recovery Cost | Observation Count |
|---|---|---|---|---|
| 1 | **Verdict file content** | **Loud failure** (post-2026-05-12 fix). WARN log + Pushover notification. Return value still `{"found": False}` so file is skipped, but CEO is alerted immediately. Pre-fix: pure silent skip. | **Minutes** — CEO sees Pushover, re-authors verdict with correct format. Pre-fix: **hours** (plans stranded until manual investigation). | **3 incidents pre-fix:** 2026-05-01 (13 files), 2026-05-09 (14 files), 2026-05-12 (4 files). **0 incidents post-fix** (2026-05-12 through 2026-05-20). |
| 2 | **Verdict filename** | **Silent skip.** `_consume_verdicts()` at bellows.py:1123-1125 silently `continue`s when filename doesn't match regex. No log. No notification. | **Hours** — requires manual investigation to discover the file exists but has wrong name. Surfaced only when plan stays stuck in `verdict-pending-` indefinitely. | **0 direct incidents observed.** However, the Planner has authored verdict files with wrong directory (2026-05-12) — wrong filename is the same error class and structurally unguarded. |
| 3 | **Verdict file directory** | **Loud failure** (post-2026-05-12 fix). `_scan_misplaced_verdicts()` emits WARN + Pushover when verdict response files appear in `pending/`. | **Minutes** — CEO sees Pushover, moves file to `resolved/`. | **1 incident pre-fix** (2026-05-12: Planner deposited to `pending/` instead of `resolved/`). **0 incidents post-fix.** Note: misplaced-verdict scan only covers `pending/` → `resolved/` mismatch, not arbitrary wrong directories. |
| 4 | **Plan header fields** | **Partially loud.** Missing `dispatch_mode` → rejected with Pushover (2026-05-19 validator). Missing other expected keys → WARN log (bellows.py:412-415). Sparse header on multi-step plan → defensive default + WARN. Complete parse failure (`{}`) on unrecognized format → **silent acceptance with downstream drift** (auto-advance past intended pause points). | **Minutes** for rejected plans (Pushover). **Minutes to hours** for silent-acceptance drift — depends on whether the drift causes a visible gate failure downstream or silently auto-advances. | **2 incidents:** (a) 2026-05-10 multi-line bold header returned partial keys (1 key instead of 6) — fixed by parser extension + defensive default. (b) 2026-05-17 YAML frontmatter `auto_close: false` → Python bool crashed `.lower()` — type-contract violation, fixed by `str()` wrap. |
| 5 | **Plan filename pattern** | **Partially loud.** Advisory WARN for `.md` files that fail prefix filter (bellows.py:953-957). But: only fires for files not already in `_seen`, and does not fire for files that don't end in `.md` or start with lifecycle prefixes. A plan deposited as `plan-feature-name.md` (missing `executable-`/`diagnostic-`/`qa-` prefix) would silently never dispatch. | **Hours** — plan sits in `decisions/` indefinitely. Surfaced only when Planner notices the plan was never picked up. | **0 direct incidents observed.** The Planner has consistently used correct prefixes. However, the 2026-05-20 missing `Dispatch Mode` header (the trigger for this diagnostic) demonstrates that Planner-authored format compliance is not guaranteed. |
| 6 | **Step headers** | **Partially loud.** Case mismatch → WARN (bellows.py:214-215). Zero headers on non-diagnostic → WARN + plan moved to Done/ as "not a standard executable" (bellows.py:405-410). Zero headers on diagnostic → silently defaulted to 1 step (bellows.py:369-370). | **Seconds** for visible WARN cases. **Minutes** for the silent diagnostic default — discovered when step extraction returns wrong content. | **1 BACKLOG entry** (2026-05-13, still open): `_extract_step_text` case-sensitivity. No production failure — governance rule prevents at plan-write time. |
| 7 | **Deposits blocks** | **Loud failure.** `deposit_exists` gate failure with evidence text naming each missing path. Pushover via verdict request. | **Minutes** — CEO sees gate failure in verdict request, verifies via Rule 22, and continues or fixes. | **Multiple incidents** (2026-04-19 prose false positives; 2026-05-06 path resolution drift; 2026-05-07/08 evidence path convention; 2026-05-11 Cause 5 audit). All fixed via code + governance. |
| 8 | **Rule 20 self-check** | **Loud failure.** `rule_20_self_check` gate failure with evidence text. | **Minutes** — gate failure is clear and specific. | **Multiple incidents** (2026-05-05 fabrication detection shipped; 2026-05-10 banner substitution; 2026-05-17 bold-tolerance). All fixed. Single-sourced since 2026-05-10 eliminates Planner authoring surface. |

---

## Q3 — Response Option Evaluation Per Artifact

### Artifact 1: Verdict File Content — **No further action needed**

The 2026-05-12 verdict content validator (A+C: schema validator + observability) fully addresses this artifact. The WARN log + Pushover notification transforms the silent-skip into a loud failure. Zero incidents post-fix in 8 days of operation. The return contract (`{"found": False}`) is preserved, so malformed verdicts are still not processed — but the CEO is immediately alerted. This is the correct design: the file stays in `resolved/` for the Planner to fix and re-deposit. No further work needed.

### Artifact 2: Verdict Filename — **Recommend A (Schema Validator)**

**(a) Schema validator:** A filename validator should scan `verdicts/resolved/` for `.md` files that don't match the expected pattern `^verdict-(.+)-step-(\d+)\.md$` and are NOT `processed-*` files. When found, emit a WARN log with the actual filename and the expected pattern, plus Pushover notification. This catches filenames like `verdict-continue-plan-slug.md` or `continue-plan-slug-step-1.md` that a Planner might plausibly author. Implementation: add a check inside `_consume_verdicts()` after the existing `fname.startswith("verdict-request-")` exclusion and before the regex match — if a file starts with `verdict-` and ends with `.md` but doesn't match the slug-step regex, log it.

**(b) Writer helper:** Inappropriate. Same async-authoring-context argument as the 2026-05-12 evaluation — the Planner authors verdict files during CEO review sessions where no Bellows helper is available in the conversation.

**(c) Observability-only:** Insufficient. A filename-format mismatch has the same silent-skip failure mode as the pre-fix verdict content case. Observability requires someone to read logs proactively; the whole point of the 2026-05-12 fix was to push notifications so the CEO doesn't have to poll.

**Justification:** The verdict filename regex match at bellows.py:1123-1125 silently `continue`s on non-matching filenames with no log, no notification — identical to the pre-2026-05-12 verdict content behavior that caused 3 incidents. The directional fix is the same: transform silent-skip into loud failure via WARN + Pushover.

### Artifact 3: Verdict File Directory — **No further action needed**

The 2026-05-12 misplaced-verdict directory validator fully addresses the `pending/` → `resolved/` mismatch case. Zero incidents post-fix. The validator covers the empirically observed failure mode. Extending to other directories is low-priority since the Planner's workflow naturally uses `pending/` and `resolved/` — depositing to an arbitrary third location has not been observed and is unlikely.

### Artifact 4: Plan Header Fields — **Recommend A (Schema Validator, targeted extension)**

The dispatch-mode validator (2026-05-19) demonstrates the pattern: claim-time validation in `validators.py` with reject/warn results. Two gaps remain:

**Gap 4a: Header field value type coercion.** The 2026-05-17 crash (`auto_close: false` as YAML bool) showed that YAML frontmatter can produce non-string values for fields the downstream code `.lower()`s. The `str()` wrap at bellows.py:491 is a point fix; a systematic claim-time check that all known header fields are strings (or coerced to strings) would prevent the class.

**Gap 4b: `pause_for_verdict` value validation.** `header_says_pause()` at bellows.py:301-310 accepts `"always"`, `"after_step_1"`, `"after_qa_step"`, and falls through to `False` for any other value. A Planner that writes `pause_for_verdict: true` (common YAML-think) gets no pause — silent acceptance with downstream drift. A claim-time validator checking against the enumerated values would catch this.

**(a) Schema validator:** Extend `validators.py` with `check_header_field_types()` (coercion check) and `check_pause_for_verdict_value()` (enum validation). Both are WARN-level, not reject — the defensive default already prevents the most dangerous outcome (unintended auto-advance).

**(b) Writer helper:** Inappropriate — headers are authored inline within the plan file, not as standalone artifacts.

**(c) Observability-only:** Already partially shipped (missing-keys warning, sparse-header warning). The gap is not observability — it's that certain value-level violations (wrong type, invalid enum) are silent.

### Artifact 5: Plan Filename Pattern — **Recommend C (Observability-only)**

The advisory WARN for non-matching `.md` files (2026-05-08) already covers the most likely failure mode. The Planner has never authored a plan with the wrong prefix in production. A schema validator would duplicate the `is_runnable_plan()` check that already gates dispatch. The missing piece is observability for the specific case where a new `.md` file appears in a watched directory and is neither runnable nor a lifecycle file — the current warning covers this but only for files not already in `_seen`. No additional work needed unless a production failure occurs.

### Artifact 6: Step Headers — **Recommend C (Observability-only)**

Step headers have loud feedback for the case-mismatch (WARN) and zero-headers (WARN + skip-to-Done) cases. The remaining gap is the case-insensitive regex BACKLOG item (2026-05-13, still open) which is deferred pending a second occurrence. The governance rule (PLANNER_TEMPLATE Rule 26) prevents lowercase `## step 1` at plan-write time. No additional validator work warranted — the governance prevention and the existing observability are adequate.

### Artifact 7: Deposits Blocks — **No further action needed**

The `deposit_exists` gate provides the system's loudest failure mode for deposits. Multiple incidents (2026-04-19 through 2026-05-11) have all been fixed via code improvements and governance tightening. The gate now correctly handles: block format, inline format, legacy prose, directory paths, worktree resolution, and `_staging_*` filtering. No further work needed.

### Artifact 8: Rule 20 Self-Check Banner — **No further action needed**

Single-sourced since 2026-05-10, eliminating the Planner authoring surface entirely. The gate provides loud failure feedback. Bold-tolerance shipped 2026-05-17. The remaining failure surface is agent-side (QA agent failing to execute the canonical block correctly), not Planner-side.

---

## Q4 — Shipping Order and Dependencies

### Recommended Sequence

| Order | Artifact | Recommended Work | Effort | LOC (prod + test) | Blast Radius | Recurrence Rate |
|---|---|---|---|---|---|---|
| 1 | **#2 Verdict filename** | Filename format validator in `_consume_verdicts()` | Small | ~15 + ~30 = ~45 | Single function (`_consume_verdicts`) | 0 observed, but same silent-skip class as verdict content (3 incidents) |
| 2 | **#4b `pause_for_verdict` enum** | Claim-time enum validator in `validators.py` | Small | ~15 + ~20 = ~35 | Single function (`validate_at_claim`) | 0 observed, but latent risk — `true`/`yes` YAML-think plausible |
| 3 | **#4a Header field types** | Claim-time type coercion check in `validators.py` | Small | ~20 + ~25 = ~45 | Single function (`validate_at_claim`) | 1 observed (2026-05-17 `auto_close` bool crash) |

**Total new LOC:** ~125 (production ~50, tests ~75)

### Dependencies

- **#2 and #4b are independent** — they modify different files (`bellows.py` vs `validators.py`) and can ship in parallel.
- **#4a and #4b both extend `validators.py`** — they can ship in a single plan or as parallel edits to the same file (no structural dependency, just co-location).
- **Shared helper opportunity:** #4a and #4b both read from the parsed header dict. The existing `_get_dispatch_mode()` helper in `validators.py:19-24` demonstrates the pattern. A `_get_pause_for_verdict()` helper would be consistent but is 3 LOC and not worth a shared-helper abstraction — just inline the `.get()` call.

### Parallel shipping recommendation

All three can ship as a single 2-step plan (DEV + QA) or as two parallel plans:
- **Parallel-1:** Verdict filename validator (#2) — modifies `bellows.py` + `tests/test_consume_verdicts.py` or `tests/test_bellows.py`
- **Parallel-2:** Header validators (#4a + #4b) — modifies `validators.py` + `tests/test_validators.py`

No inter-plan dependencies. No shared files. Clean parallel execution.

---

## Q5 — Anti-Recommendations

### Plan body prose — DO NOT validate

Plan step prose (the text between `## STEP N` and the next `## STEP` or `**Deposits:**`) is intentionally free-form. The Planner's value is exactly in composing natural-language task descriptions, agent selection, evidence requirements, and tool guidance. This content is consumed by agents via `claude -p`, not by deterministic parsers. A validator that checks prose structure would conflate "shape" (mechanical contract) with "content" (LLM judgment). The only prose-level validator that exists (`check_stop_prose()` in validators.py:65-118) intentionally operates at the pattern level (scanning for `STOP.`, `wait for confirmation`, `do not proceed` — phrases that indicate the plan was authored for manual dispatch rather than Bellows dispatch). This is a dispatch-mode check, not a content-quality check.

### Test-scope justifications — DO NOT validate

The `**Test Scope:**` field in plan headers (e.g., `none (diagnostic)`, `unit + regression`, `full suite`) is documentation for the CEO, not a parseable contract. No Bellows component reads this field or conditions behavior on it. Validating it would impose a rigid taxonomy on what is currently a free-text field, with no mechanical benefit.

### Agent specialist file content — DO NOT validate

Files in `agents/` (e.g., `BELLOWS_SYSTEMS_ANALYST.md`, `BELLOWS_QA.md`) are read by agents as natural-language prompts. Their structure is intentionally flexible — the Planner evolves agent definitions based on observed behavior. A schema validator on these files would constrain the Planner's ability to iterate on agent design, which is the system's primary adaptation mechanism.

### Verdict request file content — DO NOT validate at authoring time

Verdict request files are authored by `verdict.py:post_verdict_request()` — a Bellows function, not the Planner. The fields are deterministically constructed from function parameters. A validator on the output of a function Bellows itself controls would be testing Bellows's own code, not a Planner contract. If the format drifts, the fix is in the function, not a validator.

### `CEO Context` / `Execution Map` in plan headers — DO NOT validate

These are documentation fields consumed by the CEO and Planner, not by Bellows parsers. No Bellows component reads `CEO Context`, `Execution Map`, or `Purpose`. Validating their presence would add authoring friction with no mechanical benefit.

### The Layer 1 / Layer 3 boundary

The common thread: validators belong on artifacts where a deterministic parser produces wrong behavior on shape deviation. Artifacts consumed by LLMs (plan prose, agent prompts, CEO context) are judged by the LLM, not parsed by regex. The validator-versus-LLM-judgment line falls at the regex boundary — if there's a `re.match` or `re.search` downstream, it's a validator candidate; if it's fed to `claude -p` as prompt text, it isn't.

---

## Q6 — Gap Assessment

| Gap | Current State | Proposed Response | Type | Effort | Priority (1-3) | Notes |
|---|---|---|---|---|---|---|
| Verdict filename format — silent skip on malformed name | `_consume_verdicts()` silently `continue`s when filename regex doesn't match (bellows.py:1123-1125). No log. No notification. | WARN log + Pushover when `.md` file in `resolved/` starts with `verdict-` but doesn't match `^verdict-(.+)-step-(\d+)\.md$` | Validator | Small (~45 LOC) | **1** | Same silent-skip class as pre-fix verdict content. 0 observed incidents, but structurally identical risk. Can ship parallel with #4a/#4b. |
| `pause_for_verdict` invalid enum value — silent acceptance | `header_says_pause()` returns `False` for any unrecognized value (bellows.py:301-310). `pause_for_verdict: true` or `yes` silently means "no pause". | Claim-time WARN in `validators.py` when value is not in `{always, after_step_1, after_qa_step, ""}` | Validator | Small (~35 LOC) | **2** | Defensive default already prevents worst outcome (auto-advance on sparse headers). Risk is YAML-think values on plans with otherwise complete headers. |
| Header field type contract — YAML bool crash class | Point fix at bellows.py:491 `str()` wraps `auto_close`. No systematic type coercion for other header fields consumed via `.lower()` or string operations. | Claim-time check in `validators.py` that all known header fields (`auto_close`, `pause_for_verdict`, `dispatch_mode`) are string-typed after `_parse_plan_header()`. Coerce or WARN. | Validator | Small (~45 LOC) | **2** | Can ship in same plan as `pause_for_verdict` enum check. Both extend `validators.py` and `test_validators.py`. |

**Artifacts NOT in the gap table (already adequate):**
- Verdict content (#1): validator shipped 2026-05-12, 0 post-fix incidents
- Verdict directory (#3): validator shipped 2026-05-12, 0 post-fix incidents
- Dispatch mode (#4, partial): validator shipped 2026-05-19, rejects plans without field
- Plan filename (#5): observability adequate, 0 incidents
- Step headers (#6): observability adequate, governance prevents, 1 deferred BACKLOG item
- Deposits blocks (#7): loud gate failure, multiple fixes shipped
- Rule 20 banner (#8): single-sourced, loud gate failure

**Total remaining gap:** 3 rows, ~125 LOC, all small-effort validators. Can ship as 1 two-step plan or 2 parallel plans.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (standalone diagnostic)
**Status:** Complete

### What Was Done
Enumerated 9 Planner-authored artifact types with strict downstream contracts, classified failure modes along detectability/recovery/recurrence axes, evaluated three response options per artifact, recommended a shipping order, identified 5 anti-recommendation categories, and produced a 3-row gap assessment table for remaining unvalidated surfaces.

### Files Deposited
- `bellows/knowledge/research/planner-authored-contract-validation-2026-05-20.md` — comprehensive diagnostic findings (Q1-Q6)

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified 5 of 8 artifacts as "no further action needed" based on shipped validators and existing gate coverage
- Recommended 3 new validators (verdict filename, pause_for_verdict enum, header field types) totaling ~125 LOC
- Identified all 3 remaining gaps as Priority 1-2, small effort, parallelizable
- Distinguished validator-appropriate surfaces from LLM-judgment surfaces using the regex-boundary test

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic — Planner reviews findings and authors follow-on validator implementation plans)
