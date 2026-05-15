# Failure 3 Mode A Closure Design — Findings (Prompt Surface + Guard Surface)

**Date:** 2026-05-06
**Agent:** Bellows Systems Analyst
**Plan Reference:** `bellows/knowledge/decisions/in-progress-diagnostic-failure-3-mode-a-closure-design-2026-05-06.md`

---

## Summary

Recommended closure design: **Option A1 (append-system-prompt)** for prompt surface + **Option B2 (lifecycle-error detection + recovery)** for guard surface. They compose orthogonally — A1 is a preventive layer (reduces the probability of the agent attempting a Done/ move), B2 is a detection-and-recovery layer (catches the move if it happens despite A1 and restores the plan to its expected lifecycle state). Both ship as one executable plan. Estimated total surface: ~30 LOC across `runner.py` and `bellows.py`, plus ~6-8 tests. No prompt text changes to PLANNER_TEMPLATE.md required — A1 operates at the Bellows invocation layer, not the governance layer.

---

## Sub-investigation A — Prompt Surface

### A.1 — Where the prohibition lives today

The "do not move to Done/" prohibition exists in **plan text only**. There is no system-level prohibition in any artifact the agent sees outside the plan body. Specifically:

**1. Plan text (embedded by Planner per Rules 8/23/25).** The Planner is responsible for including the prohibition in each plan. Evidence from the two reproduction plans:

- **Repro 1** (`diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md`, line 10 bootstrap prompt):
  > "Do NOT proceed to any further step or move the plan to Done."

  And at the end of the step instruction:
  > "**STOP. Do NOT proceed beyond Step 1. Do NOT move the plan to Done. Wait for CEO confirmation.**"

- **Repro 2** (`diagnostic-failure-3-mode-a-occurrence-investigation-2026-05-06.md`, no explicit "do not move" in body text — the prohibition was assumed from context rather than stated as a binding instruction).

**2. PLANNER_TEMPLATE.md Rules 8/23/25 (governance, not agent-visible).** These rules govern what the Planner writes into plans but are NOT loaded into the agent's context:

- Rule 8 (line ~448): "The agent does NOT move the plan to Done — the Planner performs that move after Rule 22 verification passes."
- Rule 23(c) (line ~653): "The agent never moves the plan to Done; the Planner does, via `Filesystem:move_file`."
- Rule 25 (line ~705): Terminal-step resolution is Planner-owned; the Done/ move follows Rule 22 verification.

**3. CLAUDE.md (agent-visible).** The bellows `CLAUDE.md` (`bellows/CLAUDE.md`) contains no prohibition on Done/ moves. It says: "Plans for Bellows itself live in knowledge/decisions/." — neutral, no restriction stated.

**4. System prompt.** No `--system-prompt` or `--append-system-prompt` argument is currently passed to `claude -p`. The agent runs with the default Claude Code system prompt only. Confirmed at `runner.py` lines 33-38:

```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "stream-json",
    "--verbose",
    "--model", model,
    "--allowedTools", allowed_tools,
]
```

No system prompt argument appears in this command construction. The only agent-facing context that could contain a prohibition is the plan text itself, which the agent receives via the bootstrap prompt's `Read the plan at {shadow_prompt_path}` instruction.

**5. Shadow cache prompt (R3 variant c, shipped 2026-04-19).** The shadow cache prevents agents from learning the mutable plan file path (agents see `.bellows-cache/*.pristine`, not `in-progress-*.md`). This was designed to prevent plan-text mutation, not Done/ moves. The agent does not learn the `in-progress-` path from the prompt — but as the NDJSON evidence from Repro 1 shows (Event 53), the agent discovered the `in-progress-` file by running `ls` on the decisions directory.

**Conclusion:** The prohibition is entirely embedded in plan text, which the agent treats as task material rather than as a binding system constraint. There is no structural separation between "instructions the agent must obey" and "content the agent is analyzing."

### A.2 — What primes the agent toward `mv`

Both reproduction plans saturate the agent's context with Done/ path references because their task material is about analyzing Done/ moves.

**Repro 1** (`diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md`) — representative passages:

> **(2) Locate Done/ move sites.** Bellows moves plans to Done/ via `shutil.move` or `os.rename`. Run `grep -rn "Done\\|/Done/\\|knowledge/decisions/Done" bellows/*.py 2>&1`

> **Question A:** where does `gates.check()` get called in the post-step flow, and where does the Done/ move happen — are gates ALWAYS evaluated before any Done/ move?

> **(5) Map the auto-close path.** When a plan has `auto_close: true` [...] Does the auto-close path skip the verdict request entirely and jump straight to Done/?

The plan contains **14+ distinct references** to "Done/" in the task instructions alone — code block commands, prose questions, investigation headings. The prohibition ("Do NOT move the plan to Done") is **one sentence** among these 14+ references. The agent's assistant text in the NDJSON log (Event 49: "Now let me commit and move the plan to Done.") shows it treated "move to Done" as a standard post-work cleanup action.

**Repro 2** (`diagnostic-failure-3-mode-a-occurrence-investigation-2026-05-06.md`) — representative passages:

> The diagnostic plan `diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md` was found in `bellows/knowledge/decisions/Done/` with a clean filename

> **Final location:** `bellows/knowledge/decisions/Done/diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md`

> **HIT for (a)** if the move-to-Done commit author matches the bellows worktree pattern

> The Planner moves this plan file to `Done/` per Rule 25 terminal-step resolution

The plan contains **10+ distinct Done/ path references** in task material. The priming is structural — any diagnostic that investigates the Done/ move mechanism will necessarily reference Done/ paths extensively, creating a context where the agent's learned pattern-completion ("I've finished my work → move to Done") overwhelms the single-line prohibition.

### A.3 — Restructuring options evaluated

#### Option A1 — Append system prompt

**Description:** Add `--append-system-prompt` argument to `claude -p` invocation in `runner.py` containing the binding constraint:

```
You are executing as a Bellows-dispatched agent. BINDING CONSTRAINT: You must NEVER move plan files to Done/. You must NEVER execute mv, shutil.move, os.rename, or any equivalent operation targeting a Done/ directory within the knowledge/decisions/ tree. The Planner performs all Done/ moves after verification. Your final operation is ALWAYS the commit. If you find yourself reasoning about moving files to Done/, STOP — that is not your responsibility.
```

**Implementation surface:**
- `runner.py` lines 33-38: add `"--append-system-prompt", BELLOWS_AGENT_SYSTEM_PROMPT` to cmd list. ~5 LOC (constant definition + cmd modification).
- `--append-system-prompt` is confirmed supported by `claude -p --help` (observed in output). It appends to the default system prompt rather than replacing it, preserving Claude Code's built-in behavior instructions.

**Closure-strength:** Medium-high. System prompts have higher binding authority than user/task text in the LLM's prompt hierarchy. The constraint is structurally separated from the plan text — it cannot be "primed away" by task material discussing Done/ paths, because it exists in a different prompt layer. However, sufficiently long or attention-demanding task contexts can still override system-level instructions — this is an inherent LLM limitation, not a Bellows-specific weakness.

**Interactions with shadow cache (R3 variant c):** None. The system prompt operates independently of the shadow cache path. The agent still sees the `.pristine` path for reading the plan; the system prompt adds a behavioral constraint on top.

**LOC estimate:** ~5-8 in runner.py (constant + cmd list modification).

#### Option A2 — Tool-level restriction (Bash denylist)

**Description:** Intercept Bash tool calls to reject `mv`/`shutil.move`/`os.rename` targeting Done/ paths.

**Implementation surface:** `claude -p` supports `--allowedTools` and `--disallowedTools` at the tool level (e.g., "Bash", "Edit"), but does NOT support argument-level filtering within a tool. There is no `--disallowedTools "Bash(mv:*Done*)"` syntax. The only way to implement this is:
- A custom wrapper script that replaces the system `bash` and intercepts commands before execution, OR
- A custom MCP server that wraps the Bash tool with argument filtering

Both approaches are complex (~50-100 LOC), fragile (the agent can bypass `mv` with Python `shutil.move`, `os.rename`, `pathlib.Path.rename`, or even `subprocess.run(["mv", ...])`), and introduce a new runtime dependency.

**Closure-strength:** Medium for `mv` commands, but LOW overall — the bypass surface (Python stdlib) is too large to deny-list exhaustively.

**Interactions with shadow cache:** None.

**LOC estimate:** ~50-100 for wrapper script + integration, plus ongoing maintenance for new bypass paths.

**Verdict: REJECT.** Cost too high, closure too low. The bypass surface cannot be sealed at the tool level without removing Bash access entirely, which would break agent functionality.

#### Option A3 — Plan text sanitization (abstract tokens)

**Description:** Pre-process plan text to replace `Done/` path references with abstract tokens (e.g., `[LIFECYCLE_DIR]`) before passing to the agent.

**Implementation surface:** `bellows.py` around L271-278 (prompt construction), ~10-20 LOC regex replacement.

**Closure-strength:** Low-medium. Reduces priming but:
- Agent can discover Done/ via `ls` (as Repro 1 Event 53 demonstrates)
- Damages investigation quality if the plan genuinely needs to discuss Done/ paths (which both reproduction plans do)
- Does not address the pattern-completion behavior ("I'm done → move to Done") which is learned from training data, not from the specific plan text

**Interactions with shadow cache:** The shadow cache stores the pristine plan text. Sanitization would need to happen either at shadow-write time (corrupts the pristine copy) or at prompt-construction time (adds complexity).

**LOC estimate:** ~15-20 in bellows.py.

**Verdict: REJECT.** Damages diagnostic quality and does not address the root cause. Agent can discover Done/ independently.

### A.4 — Sub-A Recommendation

**Option A1 (append-system-prompt)** is the recommended option. Rationale:

1. **Lowest implementation cost** (~5-8 LOC, single file, single insertion point)
2. **Highest structural authority** — system prompt is architecturally above task text in the prompt hierarchy
3. **No damage to task content** — plan text is unmodified; agents still see full Done/ paths when investigating them
4. **Composable** — does not interfere with shadow cache, worktree isolation, or gate evaluation
5. **Testable** — one test verifying the `--append-system-prompt` flag is present in the runner command

The specific wording should be designed to:
- State the constraint as a system-level identity instruction ("You are a Bellows-dispatched agent")
- Enumerate the prohibited operations explicitly (`mv`, `shutil.move`, `os.rename`, `pathlib.Path.rename`)
- State what the agent's final operation MUST be (commit or deposit — never a lifecycle move)
- Provide a "reasoning interrupt" instruction ("If you find yourself reasoning about moving files to Done/, STOP")

---

## Sub-investigation B — Guard Surface

### B.1 — Filesystem state at gate-evaluation time

Tracing the `run_plan` flow in `bellows.py`:

1. **Claim:** Plan moves from `{slug}.md` to `in-progress-{slug}.md` at L252-254:
   ```python
   if not plan_filename.startswith("in-progress-"):
       shutil.move(plan_path, inprogress_path)
       plan_path = inprogress_path
   ```

2. **Shadow cache written:** L256: `_write_shadow(plan_filename, plan_text)`

3. **Worktree created:** L282: `wt_path = _create_worktree(project_path, plan_slug)`

4. **Runner invoked:** L298: `parsed = runner.run_step(bootstrap_prompt, wt_path, model, ...)`
   - **This is when the agent executes.** The agent can perform filesystem operations during this call.
   - At this point, plan file is at `in-progress-{slug}.md` in the main checkout (not the worktree).
   - **Mode A occurs here:** agent runs `mv .../in-progress-{slug}.md .../Done/{slug}.md`.

5. **Post-step:** L302-314: extract step number → record_run → capture post_diff → `gates.check()`.
   - When gates.check runs at L314, the plan file SHOULD be at `in-progress-{slug}.md`.
   - Under Mode A, it is NOT there — it is at `Done/{slug}.md`.

6. **Done/ transitions (Bellows-controlled):**
   - Auto-close path: L446-451: `shutil.move(source, done_path)` — only after all gates pass AND `effective_auto_close` is True.
   - Verdict consume continue-to-done: L910-914 in `_consume_verdicts`: `shutil.move(full_plan_path, done_path)` — only after terminal-step continue verdict.

**Key finding:** At gate-evaluation time (L314), Bellows has NOT moved the plan file. The `in-progress-{slug}.md` file should exist. Its absence uniquely signals an unauthorized external move (Mode A). All Bellows-controlled Done/ transitions happen AFTER gates.check returns — Mode B is structurally impossible (confirmed by the Mode B static analysis at `knowledge/research/failure-3-mode-b-static-analysis-findings-2026-05-05.md`).

### B.2 — Detection signal candidates

#### Candidate signal 1: Filesystem state check (in-progress file missing + Done/ file present)

**Detection:** After `runner.run_step` returns (L298), before gates.check (L314):
```python
if not os.path.exists(inprogress_path):
    done_check = os.path.join(plan_dir, "Done", base_filename)
    if os.path.exists(done_check):
        # Mode A detected: agent moved plan to Done/
```

**Reliability:** High. Under normal operation, the in-progress file ALWAYS exists at this point — Bellows claimed it at L252-254 and has not moved it. The only way it can be missing is if an external actor (the agent) moved it. False-positive rate: effectively zero — no other actor moves the file during step execution.

**Edge case:** Agent could delete the file without moving to Done/ (would trigger "missing but not in Done/" — different failure mode, not Mode A). This is detectable separately.

**Integration cost:** ~5 LOC in bellows.py, inserted between L298 (runner.run_step returns) and L312 (post_diff capture). No new dependencies.

#### Candidate signal 2: Filesystem watcher event on decisions/Done/

**Detection:** A watchdog observer on the `Done/` directory, running in a separate thread, would detect file creation events during agent execution.

**Reliability:** Medium. macOS FSEvents has debouncing behavior; events can arrive late. Watcher would need to be scoped per-plan-slug to avoid false positives from concurrent Done/ moves by the Planner on other plans.

**Integration cost:** ~40-60 LOC (new thread, watcher setup/teardown per step, event filtering). Significant complexity for marginal gain over signal 1.

**Verdict: REJECT.** Signal 1 is simpler and equally reliable.

#### Candidate signal 3: NDJSON tool-call stream cross-reference

**Detection:** After step completion, scan the NDJSON stream (already captured in `runner.py` as `result_stdout`) for Bash tool-call events containing `mv` commands targeting Done/ paths.

**Reliability:** Medium-low. The agent could use Python's `os.rename`, `shutil.move`, or `pathlib.Path.rename` instead of `mv` — none of which would appear as a `mv` bash command in the stream. Also requires parsing the full NDJSON stream after step completion, adding latency.

**Integration cost:** ~20-30 LOC in runner.py (NDJSON parsing, regex matching on tool-call events). Fragile — new bypass paths require ongoing regex updates.

**Verdict: REJECT.** Bypassable and fragile. Signal 1 is definitive — it checks the outcome (file moved) rather than the method (which command was used).

### B.3 — Design options evaluated

#### Option B1 — Gate-level (`_gate_no_unauthorized_done_move`)

**Description:** New gate function in `gates.py`, invoked in `check()`. Fires `unauthorized_done_move` failure when the in-progress file is missing and the Done/ file exists.

**Implementation surface:**
- `gates.py`: New function `_gate_no_unauthorized_done_move(inprogress_path, plan_dir, base_filename, failures)` — ~10 LOC.
- `gates.py` `check()` function: Add call to new gate, plus add `inprogress_path`, `plan_dir`, `base_filename` parameters — ~5 LOC signature change.
- `bellows.py` L314, L378: Update both `gates.check()` call sites to pass new parameters — ~4 LOC.

**Failure modes NOT closed:** The gate fires after runner.run_step returns, but the plan file is ALREADY in Done/. When the gate fails, `bellows.py` attempts to rename the plan to `verdict-pending-`:
```python
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```
But `inprogress_path` does NOT exist (the agent moved it to Done/). The `if os.path.exists` guard prevents a crash, but the plan is NOT renamed to `verdict-pending-` — it stays in Done/ while Bellows thinks it posted a verdict. This leaves the plan in an inconsistent state: in Done/ but not properly closed.

**Interaction with disable-auto-close model:** Under disable-auto-close, every terminal step pauses for verdict. The Planner performs the Done/ move AFTER the verdict cycle completes. The gate must distinguish "agent prematurely moved" (plan file missing during step execution) from "Planner's post-verdict move" (plan file missing after verdict resolution). Since the gate runs immediately after step completion (before verdict resolution), the Planner's move has not happened yet — no disambiguation needed at gate time.

**Test surface:** 3-4 tests in test_gates.py: (1) gate passes when in-progress file exists, (2) gate fires when in-progress file missing and Done/ file present, (3) gate passes when in-progress file missing and Done/ file also missing (different failure mode), (4) gate passes when Done/ directory doesn't exist.

**LOC estimate:** ~19 LOC across gates.py + bellows.py.

**Verdict: INSUFFICIENT.** Detects the violation but does not recover — leaves the plan in an inconsistent filesystem state (in Done/ but with a gate_failure verdict pending). Downstream operations (verdict-pending rename) silently fail.

#### Option B2 — Lifecycle-error in `run_plan`

**Description:** Check filesystem state in `bellows.py` immediately after `runner.run_step` returns (between L298 and L302). If the in-progress file is missing and the Done/ file exists: (1) move the file BACK from Done/ to in-progress (recovery), (2) inject a synthetic gate failure into the gate result, (3) continue through the normal gate evaluation flow.

**Implementation surface:**
- `bellows.py` between L298-302: ~15-20 LOC:
  ```python
  # Mode A detection: did the agent move the plan to Done/?
  if not os.path.exists(inprogress_path):
      done_check = os.path.join(plan_dir, "Done", base_filename)
      if os.path.exists(done_check):
          print(f"Bellows: ❌ Mode A detected — agent moved {plan_name} to Done/ without authorization, recovering")
          shutil.move(done_check, inprogress_path)  # recover
          mode_a_detected = True
      else:
          print(f"Bellows: ⚠ in-progress file missing for {plan_name} — possible agent file deletion")
          mode_a_detected = False
  else:
      mode_a_detected = False
  ```
- After `gates.check` returns (L314), inject synthetic failure if mode_a_detected:
  ```python
  if mode_a_detected:
      gate_result["failures"].append({
          "gate": "unauthorized_done_move",
          "evidence": f"Agent moved {base_filename} to Done/ during step execution. File recovered to in-progress. This is a Failure 3 Mode A violation."
      })
      gate_result["passed"] = False
  ```

**Failure modes closed:** All Mode A cases where the agent uses any mechanism (mv, shutil.move, os.rename, etc.) to move the plan to Done/. The detection is outcome-based (file at wrong location), not mechanism-based. Recovery restores the plan to its expected lifecycle state before any downstream operations run.

**Failure modes NOT closed:**
- Agent moves the plan to Done/ AND the in-progress file also exists (e.g., agent copies rather than moves) — extremely unlikely, would be caught by scope_check gate on unexpected file changes.
- Agent deletes the plan file entirely without moving to Done/ — detected by the "missing but not in Done/" branch but not classified as Mode A. Could be handled as a separate failure class.

**Interaction with disable-auto-close model:** Same as B1 — the check runs immediately after step completion, before any verdict cycle. No disambiguation needed.

**Test surface:** 4-5 tests in test_bellows.py:
1. Mode A detected and recovered: mock runner.run_step, move file to Done/ inside mock, verify file recovered to in-progress and gate_failure posted.
2. No Mode A (normal flow): verify no recovery action when in-progress file exists.
3. Missing file (not in Done/): verify warning logged but no Mode A classification.
4. Recovery failure (Done/ file vanishes between check and move): verify exception handling.
5. Integration: verify the synthetic gate failure appears in the verdict request.

**LOC estimate:** ~20-25 LOC in bellows.py (detection + recovery + synthetic failure injection).

#### Option B3 — Hybrid (lifecycle-error + gate)

**Description:** Both B2 and B1. B2 detects and recovers; B1 runs as a secondary gate check to catch edge cases the lifecycle error missed.

**Implementation cost:** ~35-40 LOC. The secondary gate adds value only if B2's recovery fails or misses an edge case — marginal benefit over B2 alone.

**Verdict: DEFER.** B2 alone closes the primary Mode A mechanism. The secondary gate can be added later if a new edge case surfaces.

### B.4 — Sub-B Recommendation

**Option B2 (lifecycle-error detection + recovery)** is the recommended option. Rationale:

1. **Outcome-based detection** — catches all mechanisms (mv, shutil.move, os.rename, pathlib) because it checks the file's location, not the command that moved it.
2. **Recovery** — restores the plan to its expected lifecycle state before any downstream operations run. This is the critical differentiator from B1, which detects but cannot recover.
3. **Clean composition with existing flow** — after recovery, the normal gate evaluation and pause/continue flow runs unchanged. The synthetic failure ensures the plan pauses for verdict.
4. **Testable in isolation** — the detection and recovery can be unit-tested by manipulating the filesystem state between mock runner invocation and post-step checks.
5. **Moderate cost** (~20-25 LOC) for high closure.

---

## Combined Recommendation

### Selected options

| Surface | Recommended Option | Mechanism |
|---|---|---|
| Prompt (Sub-A) | **A1 — append-system-prompt** | `--append-system-prompt` flag in runner.py with Bellows agent behavioral constraint |
| Guard (Sub-B) | **B2 — lifecycle-error detection + recovery** | Filesystem state check after runner.run_step returns; recovery move from Done/ to in-progress; synthetic gate failure |

### Composition

A1 and B2 compose orthogonally:

- **A1 reduces the probability** of the agent attempting a Done/ move by placing the prohibition in the system prompt layer, which has higher binding authority than plan text.
- **B2 detects and recovers** if the agent moves the file despite A1. The recovery restores the plan to its expected state; the synthetic gate failure ensures the plan pauses for Planner review.
- They operate at different layers (prompt construction in runner.py vs. post-step lifecycle in bellows.py) and have no shared state or ordering dependencies.

### Sequencing

Ship together as one plan. Rationale:
- A1 is ~5-8 LOC (one constant + one cmd list modification in runner.py). Trivially small.
- B2 is ~20-25 LOC in bellows.py. Moderate but well-scoped.
- Total surface is small enough for one DEV step + one QA step.
- Shipping A1 without B2 leaves a gap (no detection if the system prompt fails to prevent the move).
- Shipping B2 without A1 leaves a gap (every Mode A triggers recovery overhead and a Planner verdict cycle that could have been prevented).

### Total implementation surface estimate

| File | Change | LOC (est.) |
|---|---|---|
| `runner.py` | Add `BELLOWS_AGENT_SYSTEM_PROMPT` constant, add `--append-system-prompt` to cmd | ~8 |
| `bellows.py` | Mode A detection + recovery after runner.run_step, synthetic gate failure injection | ~20-25 |
| `tests/test_runner.py` | Verify system prompt flag in cmd construction | ~5 |
| `tests/test_bellows.py` | 4-5 tests: Mode A detected+recovered, normal flow, missing file, recovery failure, synthetic failure in verdict | ~40-50 |
| **Total** | | **~75-90 LOC** |

No changes to gates.py, verdict.py, or PLANNER_TEMPLATE.md.

---

## Open questions for CEO/Planner

1. **System prompt wording.** The specific text of the `--append-system-prompt` constraint should be reviewed by the CEO before shipping. The recommended draft (see A.3 Option A1 above) is aggressive — it names specific prohibited operations and includes a "reasoning interrupt" instruction. The CEO may want to tune the aggressiveness.

2. **Recovery behavior on Mode A detection.** B2 moves the file back from Done/ to in-progress and injects a synthetic gate failure. An alternative is to move to a new lifecycle state like `halted-mode-a-{slug}.md` instead of recovering. The recommended approach (recover to in-progress + gate failure) keeps the plan in the normal lifecycle, but the CEO may prefer a hard halt that requires manual intervention.

3. **Notification.** Should Mode A detection trigger a Pushover notification separate from the normal verdict-pending notification? The synthetic gate failure will trigger a verdict request, which already generates a notification. A separate "Mode A detected" notification would be more visible but could be redundant.

4. **Bellows daemon restart.** Both changes require a daemon restart. The plan should include an explicit restart step or reminder.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Two-surface design diagnostic for Failure 3 Mode A closure. Sub-A characterized the prompt surface (prohibition lives in plan text only, no system-level constraint), evaluated three restructuring options, and recommended Option A1 (append-system-prompt). Sub-B characterized the guard surface (filesystem state at gate-evaluation time uniquely signals Mode A), evaluated three detection signal candidates and three design options, and recommended Option B2 (lifecycle-error detection + recovery). Combined recommendation: ship A1 + B2 together, ~75-90 LOC total.

### Files Deposited
- `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md` — Two-surface design diagnostic findings with implementation recommendations

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Rejected Option A2 (tool-level restriction): bypass surface too large, cost too high
- Rejected Option A3 (plan text sanitization): damages diagnostic quality, does not address root cause
- Rejected candidate signal 2 (filesystem watcher): complexity with no reliability gain over signal 1
- Rejected candidate signal 3 (NDJSON cross-reference): bypassable and fragile
- Rejected Option B1 (gate-level): detects but cannot recover — leaves plan in inconsistent state
- Rejected Option B3 (hybrid): marginal benefit over B2 alone; defer unless edge case surfaces
- Selected A1 + B2 as the combined closure design

### Flags for CEO
- **Recommended: Option A1 (append-system-prompt) + Option B2 (lifecycle-error detection + recovery).** They compose orthogonally and ship as one plan. System prompt wording needs CEO review before shipping. Recovery-vs-hard-halt behavior on Mode A detection is a CEO decision (recommend recovery + gate failure over hard halt).

### Flags for Next Step
- None (single-step plan)
