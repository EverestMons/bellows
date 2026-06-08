# Executable — Bellows-Side Dispatch Mode Validator

**Last Updated:** 2026-05-19
**Project:** bellows
**Total Steps:** 3
**Dispatch Mode:** bellows
**auto_close:** false
**pause_for_verdict:** after_each_step

## Execution Map

Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)

All steps sequential. No parallelism.

## CEO Context

Implements `shop_backlog.md` entry `bellows-side-dispatch-mode-validator`. PLANNER_TEMPLATE v4.43 Rule 35 shipped the `**Dispatch Mode:** [bellows | manual_bootstrap]` plan-header field as Planner-facing only. This plan adds the mechanical enforcement layer.

Three checks the validator performs at plan claim time:

| Check | Trigger | Disposition |
|---|---|---|
| (a) Mismatch — `dispatch_mode: manual_bootstrap` deposited into a Bellows-watched directory | claim time | warn |
| (b) STOP-prose in step bodies under `dispatch_mode: bellows` | claim time | warn |
| (c) Field missing entirely | claim time | reject |

Disposition rationale: (a) and (b) ship clean today via Bellows default behavior — a warn surfaces the discrimination failure without blocking work. (c) is a Rule 35 authoring error; the field's existence forces the discrimination check at authoring time. Rejecting (c) forces the author to answer the question.

STOP-prose regex set for v1: `STOP\.`, `wait for confirmation`, `do not proceed`. Case-insensitive. Tight set deliberately — extension comes when a real-world miss surfaces.

The validator's home (gates.py vs. new validators.py) is delegated to the SA based on what they find in the code. Gates.py handles step-level gate failures during execution; this validator runs at claim/deposit time, which is a different lifecycle moment.

## Bellows-bug-aware authoring note

Per 2026-05-17 LESSONS and the 2026-05-20 recurrence, this plan ships the validator that warns about STOP-prose under `dispatch_mode: bellows`. The plan itself is authored under `dispatch_mode: bellows` and is dispatched by un-fixed Bellows. The plan body must NOT contain `STOP\.`, `wait for confirmation`, or `do not proceed` in any step prose — once the validator ships, those phrases would trigger the warn the validator is designed to surface. The plan's QA step verifies this self-consistency.

---

## STEP 1 — Systems Analyst: validator design

**Agent:** Systems Analyst (`bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`)

### Inputs
- `shop_backlog.md` entry `bellows-side-dispatch-mode-validator` at `/Users/marklehn/Developer/GitHub/shop_backlog.md`
- PLANNER_TEMPLATE.md Rule 35 at `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (search for "Dispatch Mode")
- `bellows/bellows.py` (claim-time code path; `_parse_plan_header()` and surrounding)
- `bellows/gates.py` (existing gate architecture)
- `bellows/notifier.py` (Pushover call signature — see agent-prompt-feedback.md recurring note: actual signature is `notifier.push(app_key, user_key, title, message)` positional)

### Deliverables

Design note at `bellows/knowledge/research/dispatch-mode-validator-design-2026-05-19.md` answering:

1. **Module placement.** gates.py extension or new validators.py module. Justify based on lifecycle moment (claim time vs. step gate time) and existing patterns. State the chosen path with exact file:line for new code insertion.

2. **Header field parser.** How the validator reads `**Dispatch Mode:**` from plan header. Cite the existing `_parse_plan_header()` or equivalent. Specify how YAML-frontmatter plans vs. bold-Markdown header plans expose the field. Include the regex or parse approach.

3. **Check (a) — mismatch detection.** Pseudocode for: given a plan path and parsed header, decide whether the plan's deposit directory is a Bellows-watched directory, AND the declared mode is `manual_bootstrap`. Specify how the validator reads `bellows/config.json` for the `watched_projects` list and matches the plan path against those entries.

4. **Check (b) — STOP-prose detection.** Pseudocode for: given a plan body, scan for any of the three regexes in step prose only. The three regexes are `STOP\.`, `wait for confirmation`, `do not proceed` — case-insensitive. Specify the exclusion scoping:
   - **Excluded sections:** plan header (everything before the first `## STEP`), CEO Context, Execution Map, any section preceding step bodies. Step bodies are the regions between `## STEP N` headers (and from the final `## STEP N` header to end-of-file).
   - **Excluded inline contexts within step bodies:** backtick-wrapped inline code (`` `...` ``), fenced code blocks (```` ``` ```` ... ```` ``` ````), and `**Deposits:**` blocks. These contexts contain regex literals, file paths, and other directive-shaped strings that are not directive prose.
   - **Rationale:** The goal is catching directive prose ("the agent should STOP. and wait for confirmation"), not catching the regex constants when they are named as things being discussed. A plan that ships the validator necessarily references the regexes by name; the scope must distinguish naming-a-pattern from using-the-pattern-as-instruction.
   - Specify the exact parse approach: line-based scan with state tracking for fenced code blocks, regex-based stripping of inline backticks per line, header-boundary detection via `^## STEP \d+` match.

5. **Check (c) — missing field detection.** Pseudocode for: given a parsed header, decide whether `dispatch_mode` key is present. Specify the absence condition explicitly (key not present vs. key present with empty value vs. key present with value not in `[bellows, manual_bootstrap]`).

6. **Warn vs. reject mechanics.** For warn cases (a, b): exact log format string, whether to also push a Pushover notification, dedup key shape (to avoid spamming on every poll cycle). For reject case (c): how the validator signals reject to the claim-time path. Does it raise an exception? Return a sentinel? Halt the plan to `halted-` prefix? Cite the existing halt patterns in bellows.py.

7. **Integration point.** Exact line in bellows.py where the validator is invoked. Cite the existing `_parse_plan_header()` call site or the immediate post-parse code. State the call ordering relative to existing claim-time gates.

8. **Test specification.** Enumerate the unit tests the DEV will write. Each test: name, setup, the function under test, the assertion. Minimum coverage: positive case (clean plan, all three checks pass), each warn case (a and b independently), the reject case (c), and at least one negative case per warn check (mismatch-only-on-watched, STOP-prose-only-under-bellows-mode).

**Constraint:** Do NOT propose extending the regex set beyond the three specified. Do NOT propose validator dispositions other than the warn/warn/reject specified in CEO Context. The design surface is the implementation shape, not the policy.

**Deposits:**
- `bellows/knowledge/research/dispatch-mode-validator-design-2026-05-19.md`

---

## STEP 2 — Developer: implementation

**Agent:** Developer (`bellows/agents/BELLOWS_DEVELOPER.md`)

### Inputs
- `bellows/knowledge/research/dispatch-mode-validator-design-2026-05-19.md` (Step 1 deposit)
- All files cited in the Step 1 design note

### Deliverables

1. Implement the validator per the Step 1 design note. Use the exact module placement, function signatures, regex set, integration point, and disposition mechanics specified.

2. Write unit tests per the test specification in the Step 1 design note. All tests must pass.

3. Run the full bellows test suite (`pytest tests/ --tb=short -q`). Capture output to `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/dev_pytest.txt`. Note pre-existing failures from PROJECT_STATUS.md; do not investigate them.

4. Commit per conventional commit format. Single commit covering the validator + tests. Push to origin/main.

5. Deposit a dev log to `bellows/knowledge/dev-logs/dispatch-mode-validator-2026-05-19.md` capturing: files modified with line ranges, test count added, commit SHA, full-suite pre/post failure delta.

**Self-consistency constraint:** The validator MUST be implemented exactly as specified in Step 1. The DEV does not freelance additional regexes, additional checks, or additional disposition behaviors. If the Step 1 design has a gap, halt and request clarification rather than improvising.

**Notifier signature note:** If the design specifies pushing notifications via `notifier.push`, the actual signature is `notifier.push(app_key, user_key, title, message)` positional — read the file to confirm. The plan-feedback log has flagged this signature mismatch in multiple prior plans.

**Deposits:**
- `bellows/knowledge/dev-logs/dispatch-mode-validator-2026-05-19.md`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/dev_pytest.txt`

---

## STEP 3 — QA: verification

**Agent:** QA (`bellows/agents/BELLOWS_QA.md`)

### Inputs
- Step 1 design note
- Step 2 dev log and code changes (commit SHA from Step 2)

### Deliverables

QA report at `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md` with the following verification table. Each row paired with an evidence file deposited under `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/`.

| Check | Verification | Evidence file |
|---|---|---|
| 1. Validator module exists at design-specified path | `read_text_file` the path, confirm function presence | `[1]` |
| 2. Integration call site present at design-specified bellows.py line | `read_text_file` the cited line range | `[2]` |
| 3. Three regexes encoded literally as `STOP\.`, `wait for confirmation`, `do not proceed` | `read_text_file` the validator module, grep the regex constants | `[3]` |
| 4. Watched-projects list source matches design (config.json read) | `read_text_file` the validator module, confirm config read | `[4]` |
| 5. Unit tests present per Step 1 test specification | `read_text_file` the test file, enumerate test names | `[5]` |
| 6. All targeted unit tests pass | `pytest tests/test_<dispatch_validator>.py -v` captured | `[6]` |
| 7. Full suite pass count regression delta from PROJECT_STATUS.md baseline is zero (excluding pre-existing failures) | run `pytest tests/ --tb=short -q`, compare to baseline | `[7]` |
| 8. Self-consistency: when the validator scans this plan, it produces zero warns | Run the validator's Check (b) function against this plan file directly. Capture output. | `[8]` |
| 9. Self-consistency: this plan header declares `**Dispatch Mode:** bellows` | `read_text_file` of plan header, confirm field value | `[9]` |

**Behavioral spot-check 1 — reject case:** Construct a synthetic plan file in a tmpdir with no `**Dispatch Mode:**` field. Invoke the validator's claim-time function directly. Confirm it rejects per design (raises the design-specified exception OR returns the design-specified sentinel OR moves to `halted-` per design). Capture the REPL session output as evidence file `[10]`.

**Behavioral spot-check 2 — warn case (b):** Construct a synthetic plan file in a tmpdir with `**Dispatch Mode:** bellows` AND step prose containing `do not proceed`. Invoke the validator. Confirm it logs the warn per design and does not block claim. Capture REPL output as evidence file `[11]`.

**Rule 20 self-check:** Paste the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, substituting:
- `plan_slug`: `dispatch-mode-validator-2026-05-19`
- `qa_report_path`: `knowledge/qa/dispatch-mode-validator-2026-05-19.md`
- `evidence_dir`: `knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/`
- `required_evidence_files`: `["dev_pytest.txt", "qa_targeted_pytest.txt", "qa_full_suite_pytest.txt", "reject_repl.txt", "warn_b_repl.txt", "self_consistency_scan.txt", "plan_header_dispatch_mode.txt"]`

**Deposits:**
- `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/qa_targeted_pytest.txt`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/qa_full_suite_pytest.txt`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/reject_repl.txt`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/warn_b_repl.txt`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/self_consistency_scan.txt`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/plan_header_dispatch_mode.txt`
