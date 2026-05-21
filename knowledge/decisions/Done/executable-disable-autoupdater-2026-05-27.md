# Executable — Disable Claude Code Autoupdater in Bellows Daemon

**Project:** bellows
**Dispatch Mode:** bellows
**Plan Type:** executable
**Date:** 2026-05-27
**Closes BACKLOG entry:** `Added 2026-05-20: Set DISABLE_AUTOUPDATER=1 in the Bellows daemon environment`

**Execution Map:** Step 1 (DEV) → Step 2 (QA)

## Context

Per Claude Code prompt-caching docs (https://code.claude.com/docs/en/prompt-caching): a new Claude Code version updates the system prompt or tool definitions, so the first request after an upgrade rebuilds the cache from the top. Auto-update downloads new versions in the background but applies them on the next launch. Every `claude -p` invocation Bellows makes is a fresh launch — any background-downloaded upgrade applies between steps, silently forfeiting cache continuity and potentially shifting agent behavior partway through a plan.

Fix: set `DISABLE_AUTOUPDATER=1` in the parent process environment before any `claude -p` subprocess invocation. Environment variables set on the parent propagate to all child processes by default, so a single mutation in the daemon module covers every step. Operational pairing: an explicit manual `claude` upgrade cadence at session-wrap or weekly, documented separately.

The BACKLOG entry endorses the in-`bellows.py` approach (`os.environ['DISABLE_AUTOUPDATER'] = '1'`) over launchd/shell-wrapper alternatives because it survives any launch mechanism without requiring external operational changes.

## STEP 1

You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Set the `DISABLE_AUTOUPDATER=1` environment variable in the Bellows daemon process so the value is inherited by every `claude -p` subprocess invocation. **Implementation:** (1) Open `bellows/runner.py` (the module that spawns `claude -p` via subprocess). Near the top, after the existing `import` block but before any function or class definition, add `os.environ.setdefault("DISABLE_AUTOUPDATER", "1")` with a one-line comment citing this plan's filename and the prompt-cache rationale. Use `setdefault` (not unconditional assignment) so an operator who explicitly sets the variable to a different value at launch time is respected. (2) Open `bellows/bellows.py`. Add the same `os.environ.setdefault("DISABLE_AUTOUPDATER", "1")` line at the top of the file, after imports but before any module-level code. Rationale: belt-and-suspenders — `runner.py` import order is not guaranteed to precede the first subprocess invocation in every dispatch path, and a parent-process-level set is the canonical location. (3) Tests in `bellows/tests/test_runner.py`: add one unit test named `test_runner_sets_disable_autoupdater_env_var` that asserts `os.environ.get("DISABLE_AUTOUPDATER") == "1"` after importing `runner`. The import side-effect IS the contract being tested. If `test_runner.py` does not exist, create it; if `runner` is imported indirectly via another test fixture, structure the test to import `runner` explicitly and assert the env var. (4) Add a second unit test `test_runner_respects_explicit_disable_autoupdater_override` that sets `os.environ["DISABLE_AUTOUPDATER"] = "0"` before importing `runner` (use `importlib.reload` if `runner` is already in `sys.modules`), then asserts the value remains `"0"` — verifies `setdefault` semantics. Use `monkeypatch.setenv` or equivalent pytest fixture to isolate the env mutation from other tests. (5) Operational doc note: append a new section to `bellows/CLAUDE.md` titled `## Claude Code upgrade cadence (manual)` describing that `DISABLE_AUTOUPDATER=1` is set inside `bellows.py` and `runner.py`, that the operator runs `claude --version` and (if newer available) `npm install -g @anthropic-ai/claude-code` manually at session-wrap or weekly, and that the rationale is prompt-cache continuity per the BACKLOG entry. Keep the section under 15 lines. (6) Run `python3 -m pytest tests/test_runner.py -v` from `bellows/` and confirm both new tests pass with zero regressions. Run full suite `python3 -m pytest tests/ -v` and confirm test count delta is +2 with zero NEW failures (pre-existing `test_run_step_timeout` failure is acceptable per PROJECT_STATUS history). (7) Deposit dev log to `bellows/knowledge/development/disable-autoupdater-2026-05-27.md` covering: implementation summary, exact lines changed in `runner.py` and `bellows.py` with before/after snippets, exact lines added to `CLAUDE.md`, test count delta, full pytest output for both targeted and full suite, any known issues. (8) Commit changes to `bellows` submodule: `git add bellows/runner.py bellows/bellows.py bellows/CLAUDE.md bellows/tests/test_runner.py bellows/knowledge/development/disable-autoupdater-2026-05-27.md`, then `git --no-pager commit -m "feat(daemon): disable Claude Code autoupdater to preserve prompt cache continuity"`, then `git --no-pager push origin main`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

**Deposits:**
- `bellows/runner.py`
- `bellows/bellows.py`
- `bellows/CLAUDE.md`
- `bellows/tests/test_runner.py`
- `bellows/knowledge/development/disable-autoupdater-2026-05-27.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`

## STEP 2

You are the Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. Verify Step 1's Output Receipt status is Complete; if not, halt and report blocker. **FIRST — Deliverable Verification.** Read Step 1 Output Receipt "Files Created or Modified (Code)" list. For EVERY listed file: verify it exists on disk and contains the described change. Specifically: (a) `bellows/runner.py` contains `os.environ.setdefault("DISABLE_AUTOUPDATER", "1")` near the top of the file with the rationale comment, (b) `bellows/bellows.py` contains the same line, (c) `bellows/tests/test_runner.py` contains both new test functions by name (`test_runner_sets_disable_autoupdater_env_var` and `test_runner_respects_explicit_disable_autoupdater_override`), (d) `bellows/CLAUDE.md` contains the new `## Claude Code upgrade cadence (manual)` section. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If any item is ❌, attempt fix; if unfixable, halt and report — do NOT advance. **Behavioral verification:** (1) Run `python3 -m pytest tests/test_runner.py -v` from `bellows/` and confirm both new tests pass plus zero regressions in pre-existing tests. Capture output to evidence file. (2) Run full suite `python3 -m pytest tests/ -v` from `bellows/` and confirm test count delta matches Step 1's claim with zero NEW failures (pre-existing `test_run_step_timeout` failure is acceptable). Capture output to evidence file. (3) Subprocess-inheritance smoke test: in a Python REPL, set `os.environ["DISABLE_AUTOUPDATER"] = "1"`, then `import subprocess; r = subprocess.run(["python3", "-c", "import os; print(os.environ.get('DISABLE_AUTOUPDATER'))"], capture_output=True, text=True); print(r.stdout)` — confirm output is `1`. Capture REPL session to evidence file. (4) Read `bellows/CLAUDE.md` upgrade-cadence section and confirm it cites the rationale (prompt cache) and the manual cadence (`claude --version` + `npm install -g @anthropic-ai/claude-code` at session-wrap or weekly). Capture the section text to evidence file. **Rule 20 self-check:** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:

- `plan_slug`: `executable-disable-autoupdater-2026-05-27`
- `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/disable-autoupdater-2026-05-27.md`
- `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/disable-autoupdater-2026-05-27/`
- `required_evidence_files`: `["pytest_test_runner_v.txt", "pytest_full_suite.txt", "subprocess_inheritance_repl.txt", "claude_md_upgrade_section.txt"]`

Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.

Deposit QA report to `bellows/knowledge/qa/disable-autoupdater-2026-05-27.md` with sections: Summary, Findings by severity, Testing Coverage, Deliverable Verification Table, Behavioral Verification Results, Rule 20 self-check banner, Recommendation (Pass/Revise/Halt). **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a completed milestone entry under Completed naming the closing BACKLOG entry, files changed, tests added, and the operational reminder that the daemon restart is required for the env-var mutation to take effect in the running process. **Then:** append feedback to `bellows/knowledge/research/agent-prompt-feedback.md`. **Then:** commit `git add bellows/knowledge/qa/ bellows/knowledge/qa/evidence/ bellows/PROJECT_STATUS.md bellows/knowledge/research/agent-prompt-feedback.md`, `git --no-pager commit -m "qa: disable-autoupdater verification"`, `git --no-pager push origin main`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.

**Deposits:**
- `bellows/knowledge/qa/disable-autoupdater-2026-05-27.md`
- `bellows/knowledge/qa/evidence/disable-autoupdater-2026-05-27/`
- `bellows/PROJECT_STATUS.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`
