# Bellows — Prototype: YAML Frontmatter for `deposit_exists` Gate (Strike 4)
**Date:** 2026-05-20 | **Tier:** Implementation | **Test Scope:** unit + canary | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_each_step

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent executes Step 1 ONLY (Developer), STOPS after deposit, and waits for CEO confirmation. After CEO "ok", Bellows dispatches Step 2 (QA). After QA, the agent STOPS again and waits for final CEO confirmation before the Planner closes the plan.

Bootstrap prompt:
```
Read the plan at bellows/knowledge/decisions/executable-frontmatter-prototype-deposit-exists-2026-05-20.md. Execute the next unexecuted step ONLY. After completing the step, STOP and wait for my confirmation.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-frontmatter-prototype-deposit-exists-2026-05-20.md", "bellows/knowledge/decisions/in-progress-executable-frontmatter-prototype-deposit-exists-2026-05-20.md")`. **Identity:** You are the Bellows Developer. **Reads (in order):** `bellows/agents/BELLOWS_DEVELOPER.md`, the full ADR at `bellows/knowledge/architecture/ADR-structured-plan-metadata-2026-05-20.md` (focus: Sections 3, 4, 7 — schema, Layer 1 changes, prototype scope), the current `bellows/gates.py` source (focus: `_parse_plan_header` Strategy 1 lines that flatten YAML to string key:value pairs, `_gate_deposit_exists` deposit-collection flow, `check()` signature), the current `bellows/requirements.txt`, and the four LESSONS strike entries cited in the ADR Section 2.
>
> **Task:** Implement YAML frontmatter parsing for the `deposit_exists` gate as the prototype migration. CEO has locked: flat plan-global `deposits` list (not per-step nesting), `pyyaml` as the YAML parser (adds dependency — that's accepted), `qa.evidence_dir` is supplemental to banner grep not a replacement (out of scope this plan — only `deposits` field is wired up; `qa.self_check_required` is parsed but not yet consumed). Implementation steps in order:
>
> **(a)** Add `pyyaml` to `bellows/requirements.txt`. Add `import yaml` to the top of `gates.py` alongside the existing `os` and `re` imports.
>
> **(b)** Extend `_parse_plan_header` Strategy 1 (lines starting with `match = re.search(r"\A---\n(.*?)\n---\n", ...)`). Replace the naive line-splitting with `yaml.safe_load(match.group(1))`. The function must return a dict where: scalar fields stay as-is (string keys, string/bool/numeric values), `deposits` returns as a Python list, `qa` returns as a nested dict (so `header["qa"]["self_check_required"]` works). On `yaml.YAMLError`, log a WARN-level message identifying the failure and fall through to Strategy 2 (bold-Markdown header) rather than returning `{}` silently — this surfaces malformed frontmatter without halting otherwise-correct plans. The existing strip/strip behavior on string values is no longer needed since pyyaml handles quoting; remove the `.strip().strip("*").strip()` calls for the YAML branch only.
>
> **(c)** Modify `_gate_deposit_exists` signature to accept `plan_header=None` as a parameter. Inside the function, before the existing prose-extraction logic, add a frontmatter-first branch: if `plan_header` is provided AND `plan_header.get("deposits")` returns a non-None value AND that value is a list, treat it as the authoritative source of plan-required deposits. Iterate the list, check each path with `_resolve_deposit_path(path, project_path, wt_path=wt_path)`, append a failure with evidence `"plan-required deposit missing (frontmatter): {path}"` if unresolved. Skip the `_extract_plan_required_deposits` call entirely in this branch. If frontmatter `deposits` is absent or empty or not-a-list, fall through to the existing prose-extraction code path unchanged (dual-mode Phase 1 per ADR Section 6).
>
> **(d)** The agent-declared deposits check at the top of `_gate_deposit_exists` (the `### Files Deposited` parsing loop) stays unchanged in both branches — it is independent of how plan-required deposits are sourced. Agent-declared files are still verified to exist.
>
> **(e)** Modify `check()` at the line `_gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number, wt_path=wt_path)` to also pass `plan_header`. The header is currently computed AFTER the gate calls (line `header = _parse_plan_header(plan_text)` near the return statement). Move that computation up to BEFORE the gate calls so the header is available to pass. Pass it as `plan_header=header` to `_gate_deposit_exists`. Other gate calls do not need the header (verify by inspection — none of them reference frontmatter fields).
>
> **(f)** Write five unit tests in `tests/test_gates.py` (or extend if file exists). Test names and shapes:
>   - `test_parse_plan_header_yaml_frontmatter_returns_deposits_list`: plan text with `---\ndeposits:\n  - foo.md\n  - bar.md\n---\n# Title`. Assert `_parse_plan_header(text)["deposits"] == ["foo.md", "bar.md"]`.
>   - `test_parse_plan_header_yaml_frontmatter_returns_nested_qa_dict`: plan text with `---\nqa:\n  self_check_required: true\n  evidence_dir: knowledge/qa/evidence/\n---\n# Title`. Assert `header["qa"]["self_check_required"] is True` and `header["qa"]["evidence_dir"] == "knowledge/qa/evidence/"`.
>   - `test_parse_plan_header_malformed_yaml_falls_through_to_bold_markdown`: plan text with malformed YAML frontmatter (e.g. `---\ndeposits:\n  - foo.md\n  badly: indented: nested\n---\n# Title\n**Date:** 2026-05-20`. Assert the bold-Markdown header is parsed (returns `{"date": "2026-05-20"}`-like).
>   - `test_gate_deposit_exists_uses_frontmatter_when_present_and_passes_when_file_exists`: construct a plan with frontmatter `deposits: [tests/fixtures/sample.md]`, ensure the file exists in the fixture dir, call `check()` with a parsed agent receipt that does NOT declare any deposits. Assert no `deposit_exists` failure in results.
>   - `test_gate_deposit_exists_uses_frontmatter_and_ignores_staging_in_prose`: construct a plan WITH frontmatter `deposits: [tests/fixtures/sample.md]` AND a prose `**Deposits:**` block that mentions `_staging_anything.md`. Ensure `tests/fixtures/sample.md` exists. Call `check()`. Assert no `deposit_exists` failure (frontmatter is consulted, prose ignored — this is the strike 4 reproduction defense).
>
> **(g)** Update `bellows/knowledge/development/dev-log-frontmatter-prototype-2026-05-20.md` with a complete dev log per the Developer agent's standard format. Include: files modified with line ranges, test cases added, the exact pip command for installing pyyaml (`pip install pyyaml` — note that the daemon process must be restarted for the import to take effect, per the no-hot-reload constraint), and a "Verification Steps for QA" section listing the manual checks QA should perform beyond unit tests.
>
> **Constraints:** Do NOT modify `_extract_plan_required_deposits` — that function is the prose fallback and must remain functionally unchanged during Phase 1 dual-mode. Do NOT modify `_gate_rule_20_self_check` — `qa.self_check_required` consumption is out of scope this plan (per CEO decision OQ3). Do NOT add backward-compatibility for `deposits` as a string-typed field — frontmatter that provides `deposits` as a string instead of a list is a Planner authoring error and should fall through to prose extraction (covered by the `isinstance(list)` check in step c). Do NOT install pyyaml as part of the dev step — the human runs `pip install -r requirements.txt` after merge. The dev log explicitly notes this. Tests run against the current Python environment which may or may not have pyyaml — if `import yaml` fails at test collection, that is the expected state pre-install and the QA step's first job is verifying the install resolves it.
>
> **Deposit:** `bellows/knowledge/development/dev-log-frontmatter-prototype-2026-05-20.md`
>
> **Feedback:** If during implementation you discover a constraint the plan didn't anticipate (e.g., `check()` is called from a path that doesn't have `plan_text` available so `plan_header` can't be computed there, or `pyyaml` import order conflicts with something), append an entry to `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO confirmation.**

---

## STEP 2 — BELLOWS QA

---

> **FIRST — before doing anything else, claim Step 2:** acknowledge the plan is already in `in-progress-` state; do not rename. **Identity:** You are Bellows QA. **Reads (in order):** `bellows/agents/BELLOWS_QA.md`, the dev log at `bellows/knowledge/development/dev-log-frontmatter-prototype-2026-05-20.md`, the modified `bellows/gates.py`, the modified `bellows/requirements.txt`, and the test file containing the five new test cases.
>
> **Task:** Verify the frontmatter prototype implementation against the ADR's prototype scope (Section 7) and the Step 1 dev log. QA covers four areas:
>
> **(1) Install verification.** Run `pip install -r requirements.txt` in a fresh venv (or document the existing environment state). Confirm `pyyaml` resolves. Run `python3 -c "import yaml; print(yaml.__version__)"` and record the version in the QA report.
>
> **(2) Unit tests.** Run `python3 -m pytest tests/test_gates.py -v` and capture the output. All five new tests must pass. If existing tests in `test_gates.py` regress, that is a QA-blocking failure — record full output and stop. Verify the five test names match the spec in Step 1 (f) — name drift is a soft failure (record in QA report, do not block).
>
> **(3) Canary plan execution.** Author a single-step canary plan at `bellows/knowledge/decisions/executable-frontmatter-canary-2026-05-20.md` (do NOT use this as the real plan filename — this is the canary the prototype is being tested against). The canary plan must have:
>   - YAML frontmatter with `deposits: [bellows/knowledge/research/frontmatter-canary-deposit-2026-05-20.md]` and nothing else
>   - A prose `**Deposits:**` block in the step body that mentions `_staging_frontmatter-canary-deposit-2026-05-20.md` (the transient name — this is the strike 4 reproduction)
>   - A simple SA or DEV step that just creates the deposit file with placeholder content
>
> Wait for Bellows to dispatch the canary, observe the gate outcome via the daemon logs, and confirm: `_gate_deposit_exists` passed, and the gate result records the deposit came from frontmatter (this requires instrumentation — if the dev log indicates a `deposit_source` field was not added in this prototype, then verify indirectly by confirming the gate did not log a "plan-required deposit missing" failure for the `_staging_*` name). After the canary completes, move it to `decisions/Done/` and capture the daemon log snippet in the QA report.
>
>   **Important:** restart the Bellows daemon before dispatching the canary — pyyaml was added to requirements after daemon start, so the running process does not have `import yaml` available. Single-daemon verification: `ps aux | grep "bellows.py" | grep -v grep` should show exactly one PID before and after restart.
>
> **(4) Regression check on the existing gate-2c canary.** Re-run (or read the last execution log of) the gate-2c canary that exercised the tolerant Rule 20 regex. Confirm it still passes — frontmatter changes should not have touched the Rule 20 code path. Record the outcome.
>
> **Deposit:** Write the QA report to `bellows/knowledge/qa/qa-frontmatter-prototype-2026-05-20.md`. The report MUST end with the Rule 20 — QA Self-Check Results banner followed by either `PASSED — SELF-CHECK PASSED` or `FAILED — SELF-CHECK FAILED`, with itemized check results.
>
> **Constraints:** Do NOT modify any production source files (gates.py, parser.py, etc.) — QA is read-only on production code. If a test fails or the canary trips the gate, record the failure and STOP — do not author a fix. The Planner authors fixes via a new diagnostic plan. If pyyaml installation fails on the human's environment, that is a CEO-flag (record under Output Receipt → Flags for CEO) not a fix-by-QA situation.
>
> **Feedback:** As Step 1.
>
> **STOP. Wait for CEO confirmation before the Planner closes the plan.**

---

## Deposits

- `bellows/knowledge/development/dev-log-frontmatter-prototype-2026-05-20.md`
- `bellows/knowledge/qa/qa-frontmatter-prototype-2026-05-20.md`
