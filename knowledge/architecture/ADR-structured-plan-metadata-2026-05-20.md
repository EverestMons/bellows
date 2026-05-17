# ADR: Structured Plan Metadata for Gate Consumption

**Date:** 2026-05-20
**Status:** Proposed
**Author:** Bellows Systems Analyst
**Scope:** Parser-fragility class (strikes 1, 3, 4, 5)

---

## 1. Status

**Proposed.** This ADR recommends the introduction of YAML frontmatter on plan files as the authoritative source of structured metadata for Bellows gates. Awaiting CEO decision before implementation planning proceeds.

---

## 2. Context

Bellows gates consume human-readable plan prose as authoritative specification. The `deposit_exists` gate extracts file paths from `**Deposits:**` blocks and legacy prose patterns; the `rule_20_self_check` gate greps QA deposit files for a banner string with specific formatting. Both approaches treat agent-facing prose — authored for readability and containing mechanism descriptions, transient filenames, and decorated output — as machine-readable contracts. When plan prose mentions staging filenames as part of describing the atomic-deposit pattern, or when agents render the Rule 20 banner with shell-prompt prefixes or `===` decoration, the gates cannot distinguish prose-as-instruction from prose-as-spec and produce false positives.

Five strikes have been documented across a 6-week window (2026-04-28 through 2026-05-19). Four are in scope as one architectural problem class:

| Strike | Date | Gate | Root Cause Shape |
|--------|------|------|-----------------|
| 1 | 2026-05-06 | `deposit_exists` | Gate resolved paths from `**Deposits:**` block that existed on disk but path resolution failed (newly-created files, worktree path not threaded) |
| 3 | 2026-05-17 | `rule_20_self_check` | Banner present in QA deposit but rendered inside fenced code block with `$ python3 -c "..."` shell-prompt prefix; gate literal-match failed |
| 4 | 2026-05-18 | `deposit_exists` | Gate extracted literal `_staging_*` filename from Deposits prose describing the atomic-deposit mechanism; transient file never persists on disk |
| 5 | 2026-05-18 | `rule_20_self_check` | Banner present inside fenced code block with `===` separator decoration lines; gate regex did not tolerate the surrounding context |

**Excluded from scope:**
- **Strike 2** (2026-04-28, `no_permission_denials`): cross-repo grep trip on read-class tools. Already closed via `READ_CLASS_TOOLS` allowlist. Different problem class (tool-category classification, not prose parsing).
- **2026-05-19 `claude -p exit code 1` auth-failure misrouting**: the `gate_failure` pause reason misframes environmental auth failures as plan defects. This requires a separate pause-reason taxonomy change (new `auth_failure` reason code) and should ship as its own SA/DEV plan — it is not a parser-fragility issue and is not addressed by frontmatter.

**Source citations:**
- LESSONS.md 2026-05-18: "Strike 4 — `deposit_exists` gate keys on literal staging filename inside Deposits prose; 4th Bellows gate false positive"
- LESSONS.md 2026-05-18: "Strike 5 — Rule 20 banner inside fenced code block with `=` separators still trips `rule_20_self_check` gate"
- LESSONS.md 2026-05-17: "Bellows Rule 20 gate keys on a specific stdout pattern; documenting the banner as a captured block trips the gate"
- PROJECT_STATUS.md 2026-05-06: "BACKLOG hygiene wrap from invoice-pulse session — `deposit_exists` gate reports plan-required deposits as missing when files exist on disk. Three reproductions."

**Production code dedicated to prose-pattern extraction:**

In `gates.py` (319 lines total):
- `strip_fenced_code_blocks`: 5 LOC (regex constant + function)
- `_extract_step_text`: 8 LOC
- `_filter_transient_paths`: 3 LOC
- `_extract_plan_required_deposits`: 38 LOC (3 extraction paths: Rule 26 block regex, inline format regex, 3 legacy prose-matching regexes)
- `_gate_rule_20_self_check` banner matching: ~52 LOC (banner literal, multi-line regex search with MULTILINE flag)

In `verdict.py` (240 lines total):
- 6 regex constants: `DEPOSITS_BLOCK_RE`, `BLOCK_BULLET_RE`, `STRICT_DEPOSIT_RE`, `BOLD_NOUN_DEPOSIT_RE`, `INLINE_DEPOSIT_RE`, `FEEDBACK_EXCLUSION_RE`
- `strip_fenced_code_blocks`: 5 LOC (duplicate)
- `_extract_step_text_from_plan`: 8 LOC (duplicate)
- `extract_primary_deposit`: 29 LOC

**Total: ~148 production LOC** across two modules dedicated to extracting structured metadata from prose.

**Rule 22 overrides issued in response to parser-fragility gate trips (past 5 weeks, 2026-04-20 to 2026-05-20):**

| Date | Gate | Override Reason |
|------|------|----------------|
| 2026-05-06 | `deposit_exists` | 3 occurrences — files existed on disk, path resolution failed |
| 2026-05-10 | `rule_20_self_check` | Non-canonical banner string substituted by plan |
| 2026-05-12 | `deposit_exists` + `rule_20_self_check` | Inline `**Deposits:**` format not parsed |
| 2026-05-13 | `deposit_exists` | Placeholder `[test-file-path]` in Deposits block |
| 2026-05-17 | `rule_20_self_check` | Banner with shell-prompt prefix (strike 3) |
| 2026-05-18 | `deposit_exists` | `_staging_*` filename in Deposits (strike 4) |
| 2026-05-18 | `rule_20_self_check` | Banner with `===` decoration (strike 5) |
| 2026-05-19 | `rule_20_self_check` | Banner omitted entirely (strike 6) |

**8 documented Rule 22 overrides** in 5 weeks. Each requires CEO attention to verify substantive work was complete, then issue a continue verdict — consuming 5–15 minutes of Planner attention per override and contributing to verdict-queue latency.

---

## 3. Decision

Introduce YAML frontmatter at the head of every plan file, fenced by `---` lines, parsed BEFORE any markdown processing. The frontmatter becomes the authoritative source for gate-consumed metadata fields, replacing prose-pattern extraction as the primary source.

### Schema Definition

```yaml
---
# Required fields (every plan)
deposits:
  - path/to/final-artifact-1.md
  - path/to/final-artifact-2.md
  # List of final-artifact paths, one per terminal/QA step that produces files.
  # Only final persistent paths — never staging/transient filenames.
  # Empty list [] if no file deposits (e.g., code-only changes).

# Required for plans with QA steps
qa:
  self_check_required: true  # bool: whether QA deposit must contain Rule 20 banner
  evidence_dir: knowledge/qa/evidence/my-plan-slug/  # optional: path to evidence directory

# Fields that remain in the prose header (NOT duplicated in frontmatter)
# pause_for_verdict, auto_close, total_steps, tier, test_scope, execution, date
---
```

### Field Semantics

| Field | Type | Required | Maps to Gate | Semantics |
|-------|------|----------|--------------|-----------|
| `deposits` | `list[str]` | Yes | `deposit_exists` | Final artifact paths the plan will produce. Gate checks existence of these paths after step execution. Replaces `_extract_plan_required_deposits` prose extraction. |
| `qa.self_check_required` | `bool` | Yes (if plan has QA step) | `rule_20_self_check` | Whether the Rule 20 banner must appear in QA deposits. Replaces grep-for-banner in QA step detection. |
| `qa.evidence_dir` | `str` | No | `rule_20_self_check` | Path to evidence directory. When present, gate can verify directory existence instead of grepping file content for banner. |

### Fields Excluded from Frontmatter (Rationale)

The following fields currently live in the prose header line (`**Date:** ... | **Tier:** ... | **Execution:** ...`) and are NOT moved to frontmatter:

- **`pause_for_verdict`**: Already parsed reliably by `_parse_plan_header` Strategy 1 (YAML) and Strategy 2 (bold-Markdown). No false positives in the strike history. Moving it would expand the schema beyond the gate-consumption scope without addressing any observed failure.
- **`auto_close`**: Same rationale as `pause_for_verdict` — reliably parsed, never caused a false positive.
- **`total_steps`**: Derived from `## STEP N` headers in plan body. Fence-strip fix (2026-05-11) closed the structural bug. No benefit from duplicating in frontmatter.
- **`tier`** and **`test_scope`**: Informational metadata consumed by the Planner, not by gates. No gate references these fields.

The schema is deliberately minimal: only fields that map to gates with documented false-positive histories are included. This prevents frontmatter from becoming a second plan header that must be kept in sync with the prose body.

### Complete Example

```yaml
---
deposits:
  - bellows/knowledge/development/my-feature-dev-log-2026-05-20.md
  - bellows/knowledge/qa/my-feature-qa-2026-05-20.md
qa:
  self_check_required: true
  evidence_dir: bellows/knowledge/qa/evidence/my-feature-2026-05-20/
---
# Bellows — My Feature Implementation
**Date:** 2026-05-20 | **Tier:** Implementation | **Test Scope:** unit | **Execution:** Step 1 (DEV), Step 2 (QA) | **pause_for_verdict:** after_step_1

## How to Run This Plan
...

## STEP 1 — BELLOWS DEVELOPER
> **Task:** Implement the feature...
> **Deposit:** Write the dev log to `bellows/knowledge/development/my-feature-dev-log-2026-05-20.md`

## STEP 2 — BELLOWS QA
> **Task:** Verify the implementation...
> **Deposit:** Write QA report to `bellows/knowledge/qa/my-feature-qa-2026-05-20.md`

---
## Deposits
- `bellows/knowledge/development/my-feature-dev-log-2026-05-20.md`
- `bellows/knowledge/qa/my-feature-qa-2026-05-20.md`
```

---

## 4. Layer Impact

### Layer 1 — Bellows

**Functions that change:**
- `gates.py::_gate_deposit_exists` — add frontmatter-first extraction: parse YAML `deposits` list before falling through to prose extraction. If frontmatter `deposits` field is present, use it as authoritative source; do NOT fall through to `_extract_plan_required_deposits`.
- `gates.py::_gate_rule_20_self_check` — add frontmatter-aware path: if `qa.self_check_required` is explicitly `false`, skip banner check entirely. If `qa.evidence_dir` is specified, verify directory existence as an alternative evidence path.
- `gates.py::_parse_plan_header` Strategy 1 — already handles `---\n...\n---\n` YAML frontmatter parsing but currently flattens to key:value pairs. Must be extended to handle nested YAML (`qa:` block with sub-fields, `deposits:` as a list).
- `gates.py::check` — pass parsed frontmatter to gate functions.

**Constants that become obsolete (after migration completes):**
- The 3 legacy prose-matching regexes in `_extract_plan_required_deposits` (Pattern 1: `Deposit...to`, Pattern 2: `Deposit...to path.md`, Pattern 3: `with open`)
- `verdict.py::STRICT_DEPOSIT_RE`, `BOLD_NOUN_DEPOSIT_RE`, `INLINE_DEPOSIT_RE`, `FEEDBACK_EXCLUSION_RE` (legacy deposit extraction)

**Constants that stay as legacy fallback (during dual-mode period):**
- `DEPOSITS_BLOCK_RE` and `BLOCK_BULLET_RE` (Rule 26 `**Deposits:**` block extraction — stays as fallback for plans without frontmatter)
- `strip_fenced_code_blocks` (still needed for `_extract_step_text` and `extract_total_steps`)
- `_filter_transient_paths` (stays as defense-in-depth even after frontmatter — belt and suspenders)

### Layer 2 — Agents

- **Agent prompt construction does NOT change.** Frontmatter is authored by the Planner at plan-write time, not by agents at execution time. Agents read plan prose and execute steps; they do not read or interpret frontmatter.
- **Specialist files do NOT need updating.** The Rule 20 self-check block format (what agents deposit) stays the same — frontmatter only changes how the *gate* finds and evaluates the deposit, not what the agent writes.
- **No agent behavior change required.** This is explicitly a Layer 1 → Layer 3 coordination improvement that is transparent to Layer 2.

### Layer 3 — Planner

- **PLANNER_TEMPLATE.md needs a new rule** for frontmatter authoring. The Planner must emit YAML frontmatter at the head of every new plan. The rule specifies: list only final persistent paths in `deposits`, never staging/transient names; set `qa.self_check_required: true` for plans with QA steps.
- **Rule 22 verification changes.** Rule 22 (e) can add a frontmatter-vs-prose consistency check: if frontmatter `deposits` diverges from prose `**Deposits:**` block, flag for Planner review.
- **Rule 26 `**Deposits:**` block stays.** It remains in plan prose as human-readable documentation of what each step produces. It is no longer the authoritative source for gate consumption (frontmatter takes that role), but it stays for agent and Planner readability. No deprecation.

**Responsibility shift:** The determination of "what files does this plan produce" shifts from being extracted by Layer 1 at runtime (fragile, depends on prose format) to being declared by Layer 3 at authoring time (explicit, machine-readable). Layer 1 validates the declaration; Layer 3 authors it.

---

## 5. Per-Strike Coverage Table

| Strike # | Date | Gate | Root Cause Shape | How Frontmatter Eliminates It | Residual Risk After Fix |
|----------|------|------|-----------------|------------------------------|------------------------|
| 1 | 2026-05-06 | `deposit_exists` | Gate resolved paths from `**Deposits:**` block; path resolution failed on newly-created files in worktree | Frontmatter `deposits` list contains only final paths; gate reads from YAML, never from prose. Worktree path resolution bug (fixed separately 2026-05-06/2026-05-10) was the actual cause for strike 1, but frontmatter eliminates the prose-extraction vector entirely. | **Low.** If Planner authors an incorrect path in frontmatter, the gate will still trip — but this is a true positive (Planner error), not a false positive (parser fragility). |
| 3 | 2026-05-17 | `rule_20_self_check` | Banner present in QA deposit with `$ python3 -c "..."` shell-prompt prefix; gate literal-match failed | `qa.self_check_required: true` in frontmatter tells the gate to check for the banner. The tolerant regex (shipped in Gate 2c) handles format variation. Frontmatter does NOT eliminate the content-matching — it provides explicit opt-in/opt-out control. | **Medium.** If the banner is entirely absent (strike 6 shape), frontmatter cannot compensate — the gate still needs to find the banner in the deposit file. However, `qa.evidence_dir` provides an alternative evidence path the gate can validate structurally. |
| 4 | 2026-05-18 | `deposit_exists` | `_staging_*` filename in Deposits prose extracted as required deposit; transient file never persists | Frontmatter `deposits` contains only final artifact paths. The Planner never lists `_staging_*` names in frontmatter because the schema definition explicitly requires final persistent paths. Prose `**Deposits:**` block may still mention staging for documentation, but the gate doesn't read it. | **Low.** Risk is Planner accidentally including a staging filename in frontmatter. Mitigated by schema definition clarity + Rule 22 verification. |
| 5 | 2026-05-18 | `rule_20_self_check` | Banner present inside fenced code block with `===` decoration; gate regex broke on surrounding context | Same as strike 3: `qa.self_check_required` declares intent; Gate 2c tolerant regex handles format. Frontmatter separates "should we check?" (frontmatter) from "how do we check?" (regex). | **Medium.** Same residual as strike 3 — content-matching still has edge cases. Reduced by the Gate 2c tolerant regex already shipped. |

---

## 6. Migration Strategy

### Recommendation: Phased Cutover (3-phase, ~2 weeks)

**Phase 1 (Week 1): Dual-mode with frontmatter-preferred.**
- Ship the parser: `_parse_plan_header` Strategy 1 extended to extract `deposits` and `qa` fields from YAML frontmatter.
- `_gate_deposit_exists`: if frontmatter `deposits` is present, use it; else fall through to prose extraction (existing code path).
- `_gate_rule_20_self_check`: if frontmatter `qa.self_check_required` is present, use it for opt-in/opt-out; else use existing QA-step detection.
- PLANNER_TEMPLATE updated: new plans MUST include frontmatter. Existing plans in queue execute via prose fallback.
- Telemetry: log `deposit_source: frontmatter | prose | legacy` in gate result to track adoption.

**Phase 2 (Week 2): Verify and warn.**
- After 5+ plans ship with frontmatter and 0 gate failures sourced from frontmatter extraction: add WARN log when prose fallback is triggered. This signals a plan was authored without frontmatter (governance slip) or frontmatter was malformed.
- Verify: zero Rule 22 overrides sourced from deposit_exists or rule_20_self_check on frontmatter-sourced plans.

**Phase 3 (Post-verification): Strict cutover.**
- Remove prose fallback from `_gate_deposit_exists` (legacy regexes become dead code, can be deleted).
- Plans without frontmatter still parse via bold-Markdown header for `pause_for_verdict`/`auto_close`, but `deposit_exists` gate emits a blocking failure: "no frontmatter deposits field — plan does not declare deposits."
- Legacy regex constants in `verdict.py` deprecated and removed.

### Rationale for Phased (Not Strict Cutover)

The LESSONS evidence shows that agents and the Planner adapt to new conventions inconsistently. The 2026-05-11 "plans drift between authoring and dispatch" entry documents how inter-session convention changes produce anchor mismatches. A strict day-one cutover would cause every in-queue plan (authored pre-frontmatter) to fail `deposit_exists` immediately. The dual-mode phase gives the queue time to drain.

### Rationale Against Indefinite Dual-Mode

Indefinite dual-mode means maintaining ~148 LOC of prose extraction code alongside the frontmatter parser. The prose code is the fragility source — keeping it alive indefinitely means the architectural problem is never actually resolved, only layered over. The 2-week phased cutover balances queue drainage against code hygiene.

### Cutover Signal

The cutover from Phase 2 to Phase 3 fires when:
1. Telemetry shows `deposit_source: frontmatter` on 10 consecutive plans with 0 overrides.
2. Zero plans in `knowledge/decisions/` lack frontmatter (queue is fully drained).
3. CEO authorizes the cutover (explicit human gate).

---

## 7. Prototype Scope (Minimum-Viable First Executable)

### Recommendation: Migrate `deposit_exists` gate for frontmatter `deposits` field (strike 4)

**Why strike 4:** Clearest empirical reproduction (the `_staging_*` canary in Gate 2c), smallest blast radius (only `_gate_deposit_exists` changes; `rule_20_self_check` stays on existing code path), and the `_filter_transient_paths` fix already in place provides belt-and-suspenders defense.

### Functions Touched

1. `gates.py::_parse_plan_header` — extend Strategy 1 YAML parsing to extract `deposits` as a list (currently flattens all values to strings via `line.partition(":")`)
2. `gates.py::_gate_deposit_exists` — add frontmatter-first branch: if `plan_header.get("deposits")` returns a list, use it directly; skip `_extract_plan_required_deposits` entirely
3. `gates.py::check` — pass `plan_header` (already computed at line 138) to `_gate_deposit_exists` via parameter

### Tests Added

1. `test_deposit_exists_uses_frontmatter_when_present` — plan with YAML frontmatter `deposits: [path/a.md]`; file exists → passes
2. `test_deposit_exists_frontmatter_missing_file_fails` — plan with YAML frontmatter `deposits: [path/missing.md]`; file absent → fails (true positive)
3. `test_deposit_exists_falls_back_to_prose_without_frontmatter` — plan without YAML frontmatter → existing prose extraction behavior preserved
4. `test_parse_plan_header_extracts_deposits_list` — verify list extraction from YAML
5. `test_deposit_exists_frontmatter_ignores_staging_in_prose` — plan WITH frontmatter but whose prose `**Deposits:**` mentions `_staging_*` → gate uses frontmatter, ignores prose, passes (strike 4 reproduction)

### Canary Plan

A single-step canary plan with:
- YAML frontmatter declaring `deposits: [bellows/knowledge/research/frontmatter-canary-2026-05-XX.md]`
- Prose `**Deposits:**` block that ALSO mentions `_staging_frontmatter-canary-2026-05-XX.md` (transient filename)
- Agent deposits the final file
- Expected gate behavior: `deposit_exists` reads from frontmatter, finds the file, passes. Does NOT trip on the `_staging_*` name in prose.

### Cost Estimate

| Dimension | Estimate |
|-----------|----------|
| Production LOC | ~25 (YAML list parsing + frontmatter-first branch in `_gate_deposit_exists`) |
| Test LOC | ~80 (5 targeted regression tests) |
| Agent time | Single DEV step (~10 min) + single QA step (~8 min) |
| Calendar time | 1 session (same-day ship with canary) |

---

## 8. Risks & Rejected Alternatives

### Rejected Alternatives

**(a) Scale up `_filter_transient_paths` to a full prose-classifier blacklist.**

Add more prefix/suffix patterns to `_filter_transient_paths` to cover future transient filename conventions beyond `_staging_*`. Rejected because:
- It treats the symptom (specific filenames tripping the gate) rather than the cause (gate reads prose as spec).
- Each new naming convention requires a new filter rule — the allowlist grows unboundedly.
- Does not address `rule_20_self_check` strikes at all (different gate, different problem shape).
- Maintains the ~148 LOC prose-extraction surface permanently.

**(b) Deprecate prose `**Deposits:**` blocks entirely and require frontmatter from day one.**

Strict cutover with no dual-mode period. Rejected because:
- Plans currently in the queue (authored before frontmatter convention) would immediately fail `deposit_exists`.
- The LESSONS evidence (2026-05-11 drift entry, 2026-05-13 recurrence entry) shows convention adoption requires a transition period — agents and the Planner adapt at different rates.
- Prose `**Deposits:**` blocks have human-readability value for agents executing steps; removing them degrades agent UX without benefit.

**(c) Introduce frontmatter but only for QA fields, keep `**Deposits:**` as the deposit source.**

Half-migration: frontmatter covers `qa.self_check_required` only; deposit extraction stays on prose. Rejected because:
- 6 of 8 documented Rule 22 overrides in the past 5 weeks came from `deposit_exists`, not `rule_20_self_check`. Leaving deposit extraction on prose leaves the dominant failure class unaddressed.
- The architectural principle (gates should not consume prose as spec) applies equally to both fields. A half-fix creates an inconsistent mental model: "QA metadata is in frontmatter, deposit metadata is in prose — why?"

### Top Three Risks of the Proposed Change

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Planner forgets to author frontmatter** on a new plan | Medium (first 2 weeks) | Gate falls through to prose extraction during dual-mode; after cutover, gate emits blocking failure | Phase 1 dual-mode fallback prevents immediate breakage. PLANNER_TEMPLATE rule enforces authoring. Phase 2 WARN log surfaces governance slips before strict cutover. |
| **Frontmatter `deposits` list drifts from prose body** (Planner updates prose but not frontmatter, or vice versa) | Low-Medium | Gate validates against frontmatter; prose says something different. Could mask a real missing deposit or produce a false negative. | Rule 22 (e) consistency check: if frontmatter deposits ≠ prose deposits, flag for review. Long-term: frontmatter is authoritative, prose is documentation only. |
| **YAML parse errors halt otherwise-correct plans** (malformed frontmatter: bad indentation, missing colon, tab characters) | Low | `_parse_plan_header` currently returns `{}` on parse failure; plan proceeds without frontmatter. During dual-mode this is safe (falls back to prose). After cutover, malformed frontmatter → blocking failure. | Prototype parser should emit a WARN log on YAML parse failure (not silent `{}`). Planner template includes a lint check: "verify frontmatter is valid YAML before deposit." |

---

## 9. Open Questions

1. **Should the frontmatter `deposits` field be per-step or plan-global?** The current schema proposes a flat list at plan level. An alternative is per-step deposits nested under step numbers (`deposits: {1: [path/a.md], 2: [path/b.md]}`). Per-step is more precise but more complex to author and parse. The current `_gate_deposit_exists` already scopes to the current step via `_extract_step_text` — should frontmatter replicate this scoping, or is a flat list (validated against all steps collectively) sufficient?

2. **Should the YAML parser use `yaml.safe_load` or continue with the current line-splitting approach?** Adding a `pyyaml` dependency gives robust YAML parsing but adds a dependency to a currently zero-dependency module. The current `_parse_plan_header` Strategy 1 does naive line-splitting on `:` — this handles flat key:value but breaks on nested structures (`qa:` block) and lists. The prototype needs to choose: add `pyyaml` (clean, handles all edge cases) or extend the naive parser (no new dependency, fragile on edge cases)?

3. **Does the `qa.evidence_dir` field replace or supplement banner grep?** If `evidence_dir` is specified and the directory exists with files in it, is that sufficient to pass `rule_20_self_check` without grepping for the banner string? Or is banner grep still required and `evidence_dir` is only an additional check? The answer determines whether strike 6 (banner entirely absent) is architecturally addressable by frontmatter or remains a pure agent-discipline problem.

4. **What is the deprecation timeline for the prose `## Deposits` section at plan tail?** The plan currently has both a YAML `deposits` field and a prose `## Deposits` section. Should the prose section eventually be removed from plan templates, or does it serve a durable documentation purpose that outlives the gate-consumption role?

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Authored Architecture Decision Record proposing YAML frontmatter on plan files as the authoritative source of structured metadata for Bellows gates. The ADR covers the parser-fragility class (strikes 1, 3, 4, 5), proposes a minimal schema (`deposits` list + `qa` block), defines a 3-phase migration strategy, and specifies a prototype scope targeting strike 4 (`deposit_exists` on `_staging_*` filenames) as the first implementation.

### Files Deposited
- `bellows/knowledge/architecture/ADR-structured-plan-metadata-2026-05-20.md` — Architecture Decision Record (this file)

### Files Created or Modified (Code)
- None (ADR is an inert architecture document)

### Decisions Made
- Schema scoped strictly to gate-consumed fields (`deposits`, `qa`); prose header fields (`pause_for_verdict`, `auto_close`, `total_steps`, `tier`, `test_scope`) excluded from frontmatter
- Phased cutover recommended over strict cutover or indefinite dual-mode
- Strike 4 (`deposit_exists` on `_staging_*`) recommended as prototype target over strikes 3/5 (`rule_20_self_check`)
- Prose `**Deposits:**` block retained for agent readability; not deprecated

### Flags for CEO
- Open Question 1 (per-step vs flat deposits) affects schema complexity — CEO preference requested
- Open Question 2 (`pyyaml` dependency vs extended naive parser) has operational implications — CEO preference requested
- The 2026-05-19 auth-failure misrouting is explicitly out of scope and named as requiring a separate SA/DEV plan

### Flags for Next Step
- None (single-step plan; no next step)
