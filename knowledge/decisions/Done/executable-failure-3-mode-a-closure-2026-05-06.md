# Executable — Failure 3 Mode A Closure: System Prompt + Lifecycle Guard + BACKLOG Update

**Project:** bellows
**Plan Type:** Executable
**Date:** 2026-05-06
**Total Steps:** 2

---

## Context

Failure 3 Mode A reproduced twice on 2026-05-06 (the same day). Both reproductions occurred in plans whose subject matter discussed Done/ paths:

- **Repro 1:** `diagnostic-failure-3-mode-b-static-analysis-2026-05-05` (re-dispatched 2026-05-06). NDJSON Event 55 in `logs/20260506-090416-step.json` shows agent executed `mv in-progress-... Done/...`.
- **Repro 2:** `diagnostic-failure-3-mode-a-occurrence-investigation-2026-05-06`. Same pattern. NDJSON in `logs/20260506-094652-step.json`.

Closure design diagnostic at `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md` recommended **Option A1 (append-system-prompt)** + **Option B2 (lifecycle-error detection + recovery)** as orthogonal layers. CEO authorized all agent recommendations as-is.

This plan ships three coordinated changes:

1. **A1 — System prompt prohibition** in `runner.py`. Adds `--append-system-prompt` flag with a binding behavioral constraint that lives in the system prompt layer rather than plan text.
2. **B2 — Lifecycle guard** in `bellows.py`. After `runner.run_step` returns, detect filesystem state divergence (in-progress missing + Done/ file present), recover by moving file back, inject synthetic gate failure so plan pauses for verdict.
3. **BACKLOG hygiene.** Update `invoice-pulse/knowledge/BACKLOG.md` 2026-05-05 entry from "possible Mode A reproduction" to "confirmed — see closure design 2026-05-06."

---

## Step 1 — DEV: Implement A1 + B2 + BACKLOG update

**Agent:** Bellows Developer

**Deposits:**
- `bellows/runner.py` (modified)
- `bellows/bellows.py` (modified)
- `bellows/tests/test_runner.py` (modified or created)
- `bellows/tests/test_bellows.py` (modified)
- `invoice-pulse/knowledge/BACKLOG.md` (modified)

### Read first

- `bellows/agents/BELLOWS_DEVELOPER.md` — your specialist file
- `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md` — closure design diagnostic with full implementation surface mapped
- `bellows/runner.py` — current `run_step` implementation, focus on lines 26-39 where `cmd` is constructed
- `bellows/bellows.py` — `run_plan` function, focus on lines around `runner.run_step` invocation and `gates.check()` call

### Change 1 — A1 (System prompt prohibition in runner.py)

Add a module-level constant and pass `--append-system-prompt` to `claude -p`.

**Constant location:** Top of `runner.py`, after the imports and before `_write_log()`. Use this exact text per CEO authorization:

```python
BELLOWS_AGENT_SYSTEM_PROMPT = """You are executing as a Bellows-dispatched agent. BINDING CONSTRAINT: You must NEVER move plan files to Done/. You must NEVER execute mv, shutil.move, os.rename, or any equivalent operation targeting a Done/ directory within the knowledge/decisions/ tree. The Planner performs all Done/ moves after verification. Your final operation is ALWAYS the commit. If you find yourself reasoning about moving files to Done/, STOP — that is not your responsibility."""
```

**cmd modification:** In `run_step`, add `--append-system-prompt` to the `cmd` list. Place it immediately after `--allowedTools` and before the `if session_id is not None:` block. Final form:

```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "stream-json",
    "--verbose",
    "--model", model,
    "--allowedTools", allowed_tools,
    "--append-system-prompt", BELLOWS_AGENT_SYSTEM_PROMPT,
]
```

### Change 2 — B2 (Lifecycle guard in bellows.py)

Insert Mode A detection + recovery between `runner.run_step` return and `gates.check()` in `run_plan`. Apply to BOTH locations: the initial step invocation (around the lines after `parsed = runner.run_step(bootstrap_prompt, ...)`) AND the loop continuation invocation (around the lines after `parsed = runner.run_step(default_next_prompt, ...)` inside the `while not is_final_step(...)` loop).

**Detection + recovery block** — insert immediately after `runner.run_step` returns and after `record_run` is called, but BEFORE `_capture_git_diff(post_diff)` and `gates.check(...)`:

```python
# Mode A detection: did the agent move the plan to Done/ during execution?
# Outcome-based check: in-progress file missing AND Done/ file present indicates
# unauthorized agent move. Per Failure 3 closure design 2026-05-06 (Option B2).
mode_a_detected = False
if not os.path.exists(inprogress_path):
    done_check = os.path.join(plan_dir, "Done", base_filename)
    if os.path.exists(done_check):
        print(f"Bellows: ❌ Mode A detected — agent moved {plan_name} to Done/ without authorization, recovering")
        try:
            shutil.move(done_check, inprogress_path)
            mode_a_detected = True
        except Exception as e:
            print(f"Bellows: ⚠ Mode A recovery failed for {plan_name}: {e}")
            mode_a_detected = True  # still flag the failure even if recovery failed
    else:
        print(f"Bellows: ⚠ in-progress file missing for {plan_name} — possible agent file deletion")
        # Not classified as Mode A; let downstream logic handle missing file
```

**Synthetic gate failure injection** — immediately after the existing `gate_result = gates.check(...)` line at both invocation sites:

```python
if mode_a_detected:
    gate_result["failures"].append({
        "gate": "unauthorized_done_move",
        "evidence": f"Agent moved {base_filename} to Done/ during step execution. File recovered to in-progress. This is a Failure 3 Mode A violation."
    })
    gate_result["passed"] = False
```

The synthetic failure ensures the existing pause logic routes the plan to `verdict-pending-` with `gate_failure` reason. No new pause path needed — the existing gate-failure pause logic catches it. Notification is the existing verdict-request notification (piggyback per CEO decision).

### Change 3 — BACKLOG hygiene (invoice-pulse)

Edit `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/BACKLOG.md`. Find the 2026-05-05 entry that begins:

```
- 2026-05-05: Possible Mode A reproduction during the same session that closed Mode A.
```

Replace the entire entry text (the full multi-paragraph block from `- 2026-05-05: Possible Mode A reproduction during the same session that closed Mode A.` through the end of that bullet, ending with `...check git log on the bellows repo for the Done/ move commit signature.`) with:

```
- 2026-05-05: **CONFIRMED Mode A reproduction** — promoted from "possible" 2026-05-06. Diagnostic at `bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md` confirmed Failure 3 Mode A reproduction via three-source evidence audit: NDJSON `logs/20260506-090416-step.json` Event 55 contains explicit `mv` Bash invocation moving `in-progress-diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md` to `Done/`. DB ledger shows single-dispatch lifecycle (no double consumption). Verdict file timestamps confirm Planner did NOT trigger the move. Second reproduction same-day on `diagnostic-failure-3-mode-a-occurrence-investigation-2026-05-06` (the diagnostic that confirmed the first repro also exhibited Mode A) — `logs/20260506-094652-step.json`. Both plans had Done/-related task material; priming hypothesis confirmed. v4.30 Rule 8/23/25 governance hardening was insufficient. Closure design at `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md` recommends Option A1 (append-system-prompt prohibition) + Option B2 (lifecycle-error detection + recovery in bellows.py). Closure shipping via `executable-failure-3-mode-a-closure-2026-05-06`.
```

### Tests

#### test_runner.py — A1 verification

Add or modify a test that verifies the `--append-system-prompt` flag is present in the `cmd` list constructed by `run_step`. The test should mock `subprocess.Popen` and assert the cmd argv contains `--append-system-prompt` followed by the `BELLOWS_AGENT_SYSTEM_PROMPT` constant. ~5-10 LOC.

#### test_bellows.py — B2 verification

Add ~4-5 tests for Mode A detection and recovery. Each test sets up a temporary plan directory with an in-progress file, mocks `runner.run_step`, and configures the mock to perform a filesystem operation that simulates the agent's behavior:

1. **`test_mode_a_detected_and_recovered`** — Mock runner.run_step's side effect: move the in-progress file to Done/. After mock returns, verify (a) file is back at in-progress, (b) `gate_result["failures"]` contains an entry with `gate == "unauthorized_done_move"`, (c) `gate_result["passed"] == False`, (d) plan is renamed to `verdict-pending-`.
2. **`test_mode_a_no_detection_normal_flow`** — Mock runner.run_step with no filesystem side effect. Verify (a) no recovery action taken, (b) no synthetic failure injected, (c) normal gate evaluation flow runs.
3. **`test_mode_a_missing_file_not_in_done`** — Mock runner.run_step's side effect: delete the in-progress file (not move to Done/). Verify warning is logged but `mode_a_detected == False` and no synthetic failure is injected (different failure mode).
4. **`test_mode_a_recovery_failure`** — Mock runner.run_step's side effect: move file to Done/. Mock `shutil.move` to raise an exception when called for recovery. Verify recovery exception is logged AND synthetic failure is still injected (`mode_a_detected = True` set even on recovery failure).
5. **`test_mode_a_synthetic_failure_in_verdict_request`** — End-to-end test: simulate Mode A, allow `verdict.post_verdict_request` to run, read the resulting verdict request file, verify the `unauthorized_done_move` gate appears in the gate failures section.

Use existing test patterns in `test_bellows.py` for mocking — `tempfile.TemporaryDirectory`, `MagicMock`, patching `bellows.runner.run_step`. Match style of existing tests like `test_run_plan_pauses_on_cherry_pick_conflict`.

### Commit

Single commit at end of step with all three changes (A1, B2, BACKLOG hygiene) plus tests. Commit message:

```
feat: Failure 3 Mode A closure — system prompt + lifecycle guard

Two-layer closure for Failure 3 Mode A (agent moves plan to Done/
without authorization).

A1 — System prompt prohibition (runner.py):
Adds --append-system-prompt flag to claude -p invocation with binding
behavioral constraint. Constraint lives in system prompt layer, above
plan text in prompt hierarchy.

B2 — Lifecycle guard (bellows.py):
After runner.run_step returns, detects filesystem state divergence
(in-progress missing + Done/ file present), recovers by moving file
back to in-progress, injects synthetic gate failure so plan pauses
for verdict via existing gate-failure pause logic.

Plus tests: 1 in test_runner.py (A1 cmd argv), 5 in test_bellows.py
(B2 detection, recovery, edge cases).

Plus BACKLOG hygiene: invoice-pulse 2026-05-05 entry promoted from
"possible" to "confirmed" with citation to closure design diagnostic.

Closes Failure 3 Mode A reproductions observed 2026-05-06.
References:
- bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md
- bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md
```

### Constraints

- Do NOT move this plan file to Done/. Do NOT execute `mv`, `shutil.move`, `os.rename`, or any equivalent on this plan file. The Planner performs the Done/ move after Rule 22 verification on the QA report. Stop after committing.
- Single commit only — all three changes plus tests in one commit.
- Do not modify `gates.py`, `verdict.py`, or `PLANNER_TEMPLATE.md`. The closure design intentionally avoids those files.
- Do not modify any other tests beyond `test_runner.py` and `test_bellows.py`.

### Output Receipt

End your response with the standard DEV output receipt block (per `BELLOWS_DEVELOPER.md`). Status: Complete. Files Deposited: list each modified file. Files Created or Modified (Code): same list. Flags for CEO: any deviations from plan or unexpected behaviors. Flags for Next Step: anything QA needs to know.

---

## Step 2 — QA: Verify A1 + B2 + BACKLOG update

**Agent:** Bellows QA

**Deposits:**
- `bellows/knowledge/qa/failure-3-mode-a-closure-qa-2026-05-06.md`

### Read first

- `bellows/agents/BELLOWS_QA.md` — your specialist file
- `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md` — closure design diagnostic
- The Step 1 commit's diff (run `git --no-pager show HEAD --stat` from `/Users/marklehn/Desktop/GitHub/bellows/` to see what landed)

### QA checks

#### Check 1 — A1 verification (runner.py)

- [ ] `BELLOWS_AGENT_SYSTEM_PROMPT` constant exists in `runner.py` at module level
- [ ] Constant text matches the wording authorized by CEO (see Step 1 Change 1 above for verbatim text)
- [ ] `cmd` list in `run_step` contains `"--append-system-prompt"` followed by `BELLOWS_AGENT_SYSTEM_PROMPT`
- [ ] No other code in `runner.py` was modified beyond the constant and cmd list

Use `grep -n "append-system-prompt\|BELLOWS_AGENT_SYSTEM_PROMPT" bellows/runner.py` to verify presence.

#### Check 2 — B2 verification (bellows.py)

- [ ] Mode A detection block exists in `run_plan` AFTER both `runner.run_step` invocation sites (initial step + loop continuation)
- [ ] Detection logic checks `os.path.exists(inprogress_path)` and `os.path.exists(done_check)`
- [ ] Recovery uses `shutil.move(done_check, inprogress_path)`
- [ ] Synthetic gate failure block runs after `gates.check(...)` at both sites
- [ ] Synthetic failure dict has `gate == "unauthorized_done_move"` and an evidence field
- [ ] `gate_result["passed"] = False` is set when `mode_a_detected`

Use `grep -n "mode_a_detected\|unauthorized_done_move" bellows/bellows.py` to verify.

#### Check 3 — BACKLOG update verification (invoice-pulse)

- [ ] `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/BACKLOG.md` has the 2026-05-05 entry replaced with the CONFIRMED text
- [ ] New entry text references both diagnostic findings files (`failure-3-mode-a-occurrence-investigation-2026-05-06.md` and `failure-3-mode-a-closure-design-2026-05-06.md`)
- [ ] Old entry's three-candidate-explanation text is no longer present

Use `grep -n "2026-05-05" invoice-pulse/knowledge/BACKLOG.md | head -5` and read the 2026-05-05 entry to verify.

#### Check 4 — Test execution

Run the targeted tests for Step 1's changes:

```bash
cd /Users/marklehn/Desktop/GitHub/bellows
python -m pytest tests/test_runner.py tests/test_bellows.py -v 2>&1 | tail -50
```

- [ ] All new tests added in Step 1 pass (5 in test_bellows.py for B2, 1 in test_runner.py for A1)
- [ ] Pre-existing tests in `test_runner.py` and `test_bellows.py` still pass
- [ ] If any pre-existing test breaks, document which one and the failure mode

Then run the full suite:

```bash
python -m pytest 2>&1 | tail -20
```

- [ ] Full suite test count is greater than or equal to the prior baseline (~205 tests per recent PROJECT_STATUS entries)
- [ ] Only known-pre-existing failures present (e.g., `test_run_step_timeout` if still pre-existing)
- [ ] No regressions

#### Check 5 — Commit verification

```bash
cd /Users/marklehn/Desktop/GitHub/bellows
git --no-pager log -1 --stat
```

- [ ] Single commit at HEAD
- [ ] Commit message follows the format from Step 1 (feat: prefix, three-section body)
- [ ] Files in commit are exactly: `runner.py`, `bellows.py`, `tests/test_runner.py`, `tests/test_bellows.py`, plus `invoice-pulse/knowledge/BACKLOG.md` (note: the BACKLOG file lives in a different repo, so it may be a separate concern — see flag below)

**FLAG:** invoice-pulse is a separate git repo from bellows. The BACKLOG.md edit needs to be committed in the invoice-pulse repo, not in the bellows commit. If Step 1 attempted to bundle both edits into one commit, that's a problem. QA should verify both repos have appropriate commits:

```bash
cd /Users/marklehn/Desktop/GitHub/invoice-pulse && git --no-pager log -1 --stat
cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --stat
```

If invoice-pulse has no recent commit for BACKLOG.md, flag this as Step 1 incomplete.

### QA report structure

Deposit at `bellows/knowledge/qa/failure-3-mode-a-closure-qa-2026-05-06.md` with these sections:

1. **Summary** — One paragraph: pass/fail status across all 5 checks
2. **Check 1 — A1 verification** — pass/fail per criterion with evidence (grep output, line citations)
3. **Check 2 — B2 verification** — pass/fail per criterion with evidence
4. **Check 3 — BACKLOG update verification** — pass/fail per criterion with evidence
5. **Check 4 — Test execution** — full pytest output (or relevant tail), test count baseline comparison, regression analysis
6. **Check 5 — Commit verification** — git log output, BACKLOG-cross-repo check, flags
7. **Overall verdict** — Pass / Pass-with-flags / Fail with reasoning
8. **Rule 20 self-check** — see below

### Rule 20 self-check

After writing the QA report, run this self-check Python block:

```python
import os

deposit_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/failure-3-mode-a-closure-qa-2026-05-06.md"

print("=" * 60)
print("Rule 20 Self-Check")
print("=" * 60)

checks = []
checks.append(("QA report exists", os.path.isfile(deposit_path)))

if os.path.isfile(deposit_path):
    with open(deposit_path) as f:
        content = f.read()
    checks.append(("Has Summary", "## Summary" in content or "# Summary" in content))
    checks.append(("Has Check 1 (A1)", "Check 1" in content))
    checks.append(("Has Check 2 (B2)", "Check 2" in content))
    checks.append(("Has Check 3 (BACKLOG)", "Check 3" in content))
    checks.append(("Has Check 4 (Tests)", "Check 4" in content))
    checks.append(("Has Check 5 (Commit)", "Check 5" in content))
    checks.append(("Has Overall verdict", "Overall verdict" in content or "## Verdict" in content))
    checks.append(("File is non-trivial (>3KB)", len(content) > 3000))

for label, result in checks:
    glyph = "✅" if result else "❌"
    print(f"{glyph} {label}")

all_pass = all(result for _, result in checks)
print()
print("SELF-CHECK PASSED" if all_pass else "SELF-CHECK FAILED")
```

### Constraints

- Do NOT move this plan file to Done/. Do NOT execute `mv`, `shutil.move`, `os.rename`, or any equivalent on this plan file. The Planner performs the Done/ move after Rule 22 verification on the QA report. Stop after writing the QA report and the Output Receipt.
- Do not modify any source code. QA is read-only verification.
- If a check fails, document the failure clearly with evidence — do NOT attempt to fix the failure yourself. Surface the issue to the Planner via the QA verdict.

### Output Receipt

End your response with the standard QA output receipt block (per `BELLOWS_QA.md`). Status: Complete. Files Deposited: the QA report path. Flags for CEO: overall pass/fail and any flags surfaced. Flags for Next Step: none (this is the terminal step).

---

## Plan Lifecycle

After Step 2 QA report is deposited:

1. Planner reads QA report directly (Rule 22)
2. Planner verifies the cited evidence (grep outputs, test results, git log)
3. Planner authors a `verdict: continue` deposit (if QA passes) or a follow-up plan (if QA flags issues)
4. Planner moves this plan file to `Done/` per Rule 25 terminal-step resolution

**REMINDER:** After this plan closes, the Bellows daemon must be restarted by the CEO to load the runner.py and bellows.py code changes. Pre-restart, the running daemon is on the OLD code; new plans dispatched after restart will use A1 + B2.
