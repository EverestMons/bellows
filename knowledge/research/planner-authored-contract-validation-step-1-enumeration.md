# Planner-Authored Contract Validation — Step 1 Enumeration

**Diagnostic:** `diagnostic-planner-authored-contract-validation-2026-05-12`
**Date:** 2026-05-12

---

## Part 1 — Planner-Authored Artifact Enumeration

Seven distinct artifact types identified where the Planner authors content and Bellows parses against a strict contract.

### Artifact Table

| # | File Pattern | Consumer Function | Source Location | Contract Description | Discovery Context |
|---|---|---|---|---|---|
| 1 | `verdicts/resolved/verdict-{slug}-step-{N}.md` | `check_verdict()` | `verdict.py:160-181` | First line must match `^(?:verdict:\s*)?(continue\|stop)$` (case-insensitive). Lines 2+ are free-text reason. File must exist in `verdicts/resolved/`, NOT `verdicts/pending/`. | Grep for `re.match` in verdict.py |
| 2 | `verdicts/resolved/verdict-{slug}-step-{N}.md` (filename) | `_consume_verdicts()` | `bellows.py:1054-1064` | Filename must match `^verdict-(.+)-step-(\d+)\.md$`. Must NOT start with `verdict-request-`. Slug must match a `verdict-pending-*` plan in watched projects. | Grep for `re.match` in bellows.py |
| 3 | `knowledge/decisions/(executable\|diagnostic\|qa)-*.md` (plan headers) | `_parse_plan_header()` | `gates.py:32-98` | Either YAML frontmatter (`---\n...\n---\n`) or bold-Markdown (`**Key:** value`) format. Expected keys include `project`, `type`, `auto_close`, `pause_for_verdict`, `execution_map`. | Grep for `_parse_*` in gates.py |
| 4 | Plan step text: `## STEP N` sections | `extract_total_steps()`, `_extract_step_text()`, `_extract_step_text_from_plan()` | `bellows.py:185-191`, `gates.py:253-262`, `verdict.py:33-42` | Step headers must be `## STEP N` (H2 + space + STEP + space + digits). Matched with `re.MULTILINE`. Case-insensitive but warns if case doesn't match exactly. Code fences stripped first via `strip_fenced_code_blocks()`. | Grep for `re.findall` + `## STEP` |
| 5 | `**Deposits:**` blocks inside plan steps | `_extract_plan_required_deposits()`, `extract_primary_deposit()` | `gates.py:265-309`, `verdict.py:45-73` | Rule 26 block format: `**Deposits:**` on its own line, followed by bullet list with backtick-quoted paths (`- \`path\``). Inline format: `**Deposits:** \`- path\``. Legacy prose fallback: `Deposit ... to \`path\``. Block format is authoritative when present; legacy patterns suppressed. | Grep for `DEPOSITS_BLOCK_RE`, `_extract_plan_required_deposits` |
| 6 | Rule 20 self-check banner in QA deposits | `_gate_rule_20_self_check()` | `gates.py:312-359` | QA deposit `.md` files must contain literal string `"Rule 20 — QA Self-Check Results"` followed by a line starting with `"PASSED — SELF-CHECK PASSED"`. Now single-sourced at `RULE_20_SELF_CHECK_BLOCK.md` (2026-05-10 migration), but contract exists for any direct authoring. | Grep for `_gate_rule_20` in gates.py |
| 7 | Agent output: `### Flags for CEO` / `VERDICT_REQUESTED:` | `parse()` | `parser.py:6-57` | `### Flags for CEO` section with bulleted items (`- text`), excluding "None"/"N/A". `VERDICT_REQUESTED: <reason>` on its own line. | Grep for `re.search` in parser.py |

### Additional Parser Entry Points (non-Planner-authored, excluded)

- `is_runnable_plan()` at `bellows.py:882-885`: validates plan filenames (`^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$`). Contract enforced at Planner authoring time but filename is set once, not a recurring authoring surface.
- `extract_step_number()` at `bellows.py:168-172`: parses `**Step:** N` from agent output — agent-authored, not Planner-authored.
- `_perform_startup_sweep()` at `bellows.py:1235`: parses `^verdict-request-(.+)-step-\d+\.md$` — Bellows-authored (by `post_verdict_request()`), not Planner-authored.
- `slug_from_path()` at `verdict.py:76-86`: strips prefixes from filenames — utility, no format contract.

---

## Part 2 — Failure Mode Classification

### Artifact 1: Verdict File Content (`check_verdict()`)

**Failure Class:** Silent skip

**Evidence:** When the first line doesn't match `^(?:verdict:\s*)?(continue|stop)$`, `check_verdict()` returns `{"found": False}` at line 177. The caller `_consume_verdicts()` at line 1097-1098 sees `not verdict_result.get("found")` and executes `continue` — silently skipping the file with no log, no warning, no notification.

```python
# verdict.py:174-177
first_line = lines[0].strip()
match = re.match(r"^(?:verdict:\s*)?(continue|stop)$", first_line, re.IGNORECASE)
if not match:
    return {"found": False}
```

```python
# bellows.py:1096-1098
verdict_result = verdict.check_verdict(plan_slug, step_number)
if not verdict_result.get("found"):
    continue
```

**Historical Reproductions:** 3 known incidents
1. **2026-05-01:** 13 stranded verdict files — Planner wrote `continue\n{reason}` without `verdict:` prefix (pre-regex-fix). Lessons file at `Done/executable-lessons-verdict-format-and-stranded-plans-2026-05-01.md`.
2. **2026-05-09:** 14 stranded verdict files — format intolerance in regex rejected bare `continue`/`stop`. Fixed by extending regex to accept both forms. `Done/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09.md`.
3. **2026-05-12:** 4 verdict files in self-invented format — Planner authored verdicts in a novel format that Bellows could not parse. Two plans stuck ~2 hours. `in-progress-executable-governance-lessons-verdict-format-2026-05-12.md`.

**Authoring Frequency:** Medium (every pause cycle that requires a verdict — typically multiple times per session)

---

### Artifact 2: Verdict Filename Format (`_consume_verdicts()`)

**Failure Class:** Silent skip

**Evidence:** When filename doesn't match `^verdict-(.+)-step-(\d+)\.md$`, `_consume_verdicts()` at line 1061-1062 executes `continue` — silently skipping.

```python
# bellows.py:1060-1062
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
if not match:
    continue
```

**Historical Reproductions:** 1 known incident
1. **2026-05-12:** Planner deposited verdict files to `verdicts/pending/` instead of `verdicts/resolved/`. Consumer scans only `resolved/`. Architecture doc at `knowledge/architecture/consume-verdicts-not-processing-2026-05-12.md`.

**Authoring Frequency:** Medium (same frequency as verdict content — one filename per verdict)

---

### Artifact 3: Plan Headers (`_parse_plan_header()`)

**Failure Class:** Silent acceptance with downstream drift

**Evidence:** When neither YAML nor bold-Markdown format matches, `_parse_plan_header()` returns `{}` at line 91. The caller in `gates.check()` at line 110 assigns `plan_header = _parse_plan_header(plan_text)`. Downstream, `bellows.py` reads `plan_header.get("pause_for_verdict")` — an empty dict means no pause triggers, potentially allowing auto-advance past intended pause points.

```python
# gates.py:90-91
if not header_line or "**" not in header_line:
    return {}
```

A defensive default was added at `bellows.py` (`_apply_defensive_header_defaults()`) to set `pause_for_verdict = after_step_1` when `total_steps > 1` and `len(header) < 3`, but this is belt-and-suspenders, not a contract validator.

**Historical Reproductions:** 1 known incident
1. **2026-05-10:** Multi-line bold headers returned `{'project': 'bellows'}` (single key) while pipe format returned 6 keys. Three affected plans. `Done/executable-header-parser-multiline-fix-2026-05-10.md`.

**Authoring Frequency:** High (every plan — headers authored at plan creation)

---

### Artifact 4: Step Headers (`## STEP N`)

**Failure Class:** Loud failure (partial)

**Evidence:** `extract_total_steps()` returns 0 if no headers match. This triggers a warning at line 190 for case mismatches. For diagnostics, a `total_steps == 0` fallback sets it to 1 (`bellows.py`). For executables with 0 steps, dispatch would attempt step 1 and immediately reach "final step" logic — a silent acceptance failure mode. However, the case-mismatch path does log a visible warning.

```python
# bellows.py:189-190
if case_insensitive_count > 0 and case_sensitive_count == 0:
    _log("WARN", f"⚠️ plan has step headers but case does not match...")
```

**Historical Reproductions:** 1 known incident
1. **2026-05-10:** `extract_total_steps()` counted `## STEP N` patterns inside test-fixture string literals embedded in plan prose — plans dispatched 4 steps instead of 2. Fixed by `strip_fenced_code_blocks()` preprocessing. `Done/executable-fence-strip-plan-text-parsers-2026-05-11.md`.

**Authoring Frequency:** High (every plan — step headers authored at plan creation)

---

### Artifact 5: Deposits Blocks (`**Deposits:**`)

**Failure Class:** Loud failure (gate_failure)

**Evidence:** When `_extract_plan_required_deposits()` extracts paths that agents don't create, `_gate_deposit_exists()` produces a gate failure with evidence text `"plan-required deposit missing (not declared by agent): {path}"`. This surfaces as a gate_failure pause reason in the verdict request — visible to the CEO.

```python
# gates.py:248-250
for path in _extract_plan_required_deposits(step_text):
    if path not in agent_declared and _resolve_deposit_path(path, ...) is None:
        failures.append({"gate": "deposit_exists", "evidence": f"plan-required deposit missing..."})
```

**Historical Reproductions:** 2 known incidents
1. **2026-05-07/08:** 18 gate-failure lines across 3 verdict requests — plans declared bare `evidence/foo.txt` paths while agents wrote to `knowledge/qa/evidence/<slug>/foo.txt`. `Done/diagnostic-deposit-exists-false-positive-audit-2026-05-11.md`.
2. **2026-04-19:** Deposit-path parser false positives from prose patterns capturing non-deposit text. `Done/executable-rule-26-deposit-parser-scope-2026-04-19`.

**Authoring Frequency:** High (every plan step — deposits block authored per step)

---

### Artifact 6: Rule 20 Self-Check Banner

**Failure Class:** Loud failure (gate_failure)

**Evidence:** When the banner is missing or PASSED line absent, `_gate_rule_20_self_check()` appends to failures with evidence text. This surfaces as a gate_failure.

```python
# gates.py:354-355
if banner_found_path:
    failures.append({"gate": "rule_20_self_check", "evidence": f"banner present but PASSED line missing..."})
```

**Historical Reproductions:** 1 known incident (post-single-source)
1. **2026-05-10:** Planner banner substitution during `executable-startup-sweep-extract-2026-05-10` Step 2 — overridden via continue verdict after Rule 22 verification. `Done/executable-startup-sweep-extract-2026-05-10.md`.

Pre-single-source (eliminated surface):
2. **2026-04-19 through 2026-05-10:** PATH-001 recurrence — Planner paraphrased or abbreviated the block. Fixed structurally by single-source migration. `Done/executable-rule-20-single-source-2026-05-10.md`.

**Authoring Frequency:** Low (single-sourced since 2026-05-10 — Planner no longer authors the block directly; only triggered if Planner bypasses single-source path)

---

### Artifact 7: Agent Output Markers (`### Flags for CEO`, `VERDICT_REQUESTED:`)

**Failure Class:** Silent skip

**Evidence:** If `### Flags for CEO` section is absent or malformed, `parse()` returns an empty `ceo_flags` list — no error, no warning. If `VERDICT_REQUESTED:` line is absent, returns `{"requested": False}`. These are safety-net parsers; primary detection is via plan headers and agent-authored verdict-request files.

```python
# parser.py:29
match = re.search(r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)", result_text, re.DOTALL)
# If no match, ceo_flags stays []
```

**Historical Reproductions:** 0 known. These are agent-authored markers, not Planner-authored. Included because the Planner instructs agents to emit these markers in plan step text — making the instruction a Planner contract even though the output is agent-generated.

**Authoring Frequency:** Low (indirect — Planner's instruction text influences agent output; the markers themselves are agent-emitted)

---

## Summary Table

| # | Artifact | Failure Class | Historical Reproductions | Authoring Frequency |
|---|---|---|---|---|
| 1 | Verdict file content | Silent skip | 3 (2026-05-01, 2026-05-09, 2026-05-12) | Medium |
| 2 | Verdict filename/directory | Silent skip | 1 (2026-05-12) | Medium |
| 3 | Plan headers | Silent acceptance + drift | 1 (2026-05-10) | High |
| 4 | Step headers (`## STEP N`) | Loud failure (warn) | 1 (2026-05-10) | High |
| 5 | Deposits blocks | Loud failure (gate) | 2 (2026-05-07, 2026-04-19) | High |
| 6 | Rule 20 self-check banner | Loud failure (gate) | 1 post-migration (2026-05-10) | Low |
| 7 | Agent output markers | Silent skip | 0 | Low |
