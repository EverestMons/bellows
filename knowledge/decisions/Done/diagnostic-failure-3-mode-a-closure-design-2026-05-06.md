# Diagnostic — Failure 3 Mode A Closure Design (Prompt Surface + Guard Surface)

**Project:** bellows
**Plan Type:** Diagnostic
**Date:** 2026-05-06
**Total Steps:** 1

---

## Context

Failure 3 Mode A reproduced twice on 2026-05-06 (the same day). Both reproductions occurred in plans whose subject matter discussed Done/ moves:

- **Repro 1:** `diagnostic-failure-3-mode-b-static-analysis-2026-05-05` (re-dispatched 2026-05-06 at 09:04). Agent executed `mv in-progress-... Done/...` at 09:07:25, before Bellows recorded VerdictPending at 09:07:31. Evidence: NDJSON log `logs/20260506-090416-step.json` Event 55.
- **Repro 2:** `diagnostic-failure-3-mode-a-occurrence-investigation-2026-05-06` (the diagnostic that confirmed Repro 1). Agent moved this plan to Done/ during its own execution. Evidence: `logs/20260506-094652-step.json` contains a `mv /Users/marklehn` Bash invocation; plan was in Done/ before Planner's verdict deposit.

Both reproductions occurred under v4.30 Rule 8/23/25 governance hardening. Both plans contained explicit "Do NOT move the plan to Done/" instructions in plan text. The hardening did not prevent the failures.

**Hypothesis:** The agent's prompt context primes it toward `mv` whenever the task discusses Done/ paths, and the prohibition lives in plan text the agent treats as task material rather than as binding constraint.

This diagnostic characterizes two surfaces in parallel sub-investigations:

- **Sub-investigation A — prompt surface:** where exactly does the "do not move to Done/" wording appear in the agent's prompt context, and what restructuring options exist?
- **Sub-investigation B — guard surface:** what code surface in `bellows.py`/`gates.py` could mechanically detect an unauthorized Done/ move, and which of two design options (gate-level vs. lifecycle-error) is feasible?

The deliverable is a single findings file with recommendations on both fronts. Plan 2 (executable, written separately) will ship the chosen prompt restructuring + guard implementation + BACKLOG entry promotion.

### Scope boundary

This is a **read-only design diagnostic**. No code changes. No test additions. No prompt changes. The output is design recommendations cited against current code/prompt artifacts.

---

## Step 1 — SA: Two-Surface Design Diagnostic

**Agent:** Bellows Systems Analyst

**Deposits:**
- `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md`

### Read first

- `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — your specialist file
- `bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md` — the prior diagnostic that confirmed Mode A; cites the smoking-gun NDJSON event
- `bellows/PROJECT_STATUS.md` — recent context on disable-auto-close (2026-04-24), shadow-cache prompt (R3 variant c, 2026-04-19), and the v4.30 hardening lineage

### Sub-investigation A — Prompt Surface

Goal: enumerate every place "do not move to Done/" wording exists in the agent's prompt context today, and propose 2–3 restructuring options ranked by closure-strength vs. implementation cost.

#### What to read

- `bellows/planner.py` — `build_context_envelope()` and any related prompt-construction functions. This is the envelope wrapped around the agent's context.
- `bellows/runner.py` — how `claude -p` is invoked, what `--system-prompt` arguments (if any) are passed, what tool allowlist is set (per the 2026-04-23 permission prompt substrate diagnostic, `--allowedTools Read,Edit,Write,Bash` is passed).
- `bellows/bellows.py` — the `run_plan` and `_run_tracked` paths around the runner invocation, to understand what plan text reaches the agent and via which path (shadow-cache vs. live file per R3 variant c).
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` Rule 8 + Rule 23 + Rule 25 sections — the canonical "do not move to Done/" wording the Planner is asked to embed in plans.
- The two reproduction plans (read both): `bellows/knowledge/decisions/Done/diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md` and `bellows/knowledge/decisions/Done/diagnostic-failure-3-mode-a-occurrence-investigation-2026-05-06.md`. Search both for prohibition wording. Note: the second plan was authored by today's Planner so wording reflects current Planner discipline.

#### What to characterize

For each prompt-context surface, answer:

1. **Where does the prohibition wording live today?** Plan text only? System prompt? Envelope wrapper? Tool descriptions? Cite exact file/function/line ranges.
2. **What primes the agent toward `mv`?** Look at the two reproduction plans. Both discuss Done/ paths as part of their task material (one analyzes Done/ move code, the other investigates a Done/ move violation). Does the plan text contain Done/ paths in code blocks, prose, file paths, or commands? Quote representative passages.
3. **What is the minimum change that would let a future plan task discuss Done/ paths without priming the agent toward `mv`?** This is the design question.

#### Restructuring options to evaluate

Evaluate each option's closure-strength (how reliably it prevents Mode A) and implementation cost. Propose 2–3 options minimum; include or reject the three below as you see fit:

- **Option A1 — Move prohibition to system prompt.** Add a `--system-prompt` argument to `claude -p` invocation in `runner.py` that includes the binding constraint: "You are executing as a Bellows-dispatched agent. You must NEVER move plan files to Done/. The Planner performs all Done/ moves." Plan text no longer carries the prohibition.
- **Option A2 — Tool-level restriction.** Bellows constrains the agent's `Bash` tool with a denylist or wrapper that rejects `mv` commands targeting Done/ paths within the watched-projects tree. Investigate whether `claude -p` supports tool argument filtering or if this requires a custom tool wrapper.
- **Option A3 — Plan text sanitization.** Bellows pre-processes plan text to strip Done/ path references from the agent-facing context, replacing them with abstract tokens. (Plan still references Done/ in CEO/Planner-facing text, but agent only sees the abstract version.)

Document each option's implementation surface (which file, which function, ~LOC estimate). Note interactions with the shadow-cache prompt (R3 variant c) — agents currently see the shadow path, not the live `in-progress-` path, so any Done/-prohibition wording that references "the in-progress file" needs to match what the agent actually sees.

#### Recommendation

Conclude Sub-A with a single recommended option (or hybrid). State why.

### Sub-investigation B — Guard Surface

Goal: characterize the code surface where a mechanical guard could detect an unauthorized Done/ move, evaluate Option A (gate-level) vs. Option B (lifecycle-error) for feasibility, and recommend one.

#### What to read

- `bellows/gates.py` — full file. Pay attention to: gate composition in `check()`, the existing `_gate_*` functions for pattern, what evidence format each produces, how the result dict is shaped, scope allowlist constants.
- `bellows/bellows.py` — focus on `run_plan` and `_consume_verdicts`. Trace the lifecycle from agent step completion → gate evaluation → verdict request posting → Done/ transition. Identify the exact line ranges where:
  - The agent's step completes (`runner.run_step` returns)
  - Gates run (`gates.check(...)`)
  - The plan file's filesystem state is potentially read or moved
  - The Done/ transition happens (auto-close path AND continue-verdict-to-done path)
- `bellows/verdict.py` — verdict request construction and the `slug_from_path` helper, since any guard that fires needs to communicate via the verdict request schema.

#### What to characterize

1. **Filesystem state at gate-evaluation time.** When `gates.check()` runs, what is the expected state of the plan file on disk? Specifically: is the plan still at `decisions/in-progress-{slug}.md`, or has it been renamed already? When does Bellows itself rename it? When could an agent rename it (the failure mode under investigation)?
2. **Detection signal for Mode A.** Given the filesystem state semantics above, what is the minimum signal that uniquely identifies "agent moved plan to Done/ without authorization"?
   - Candidate signal 1: `decisions/in-progress-{slug}.md` is missing AND `decisions/Done/{plan-base}.md` exists, AND the current step is not a final step authorized to move (note: under the current disable-auto-close model, NO step is authorized to move; the Planner does it).
   - Candidate signal 2: A filesystem watcher event on `decisions/Done/` during agent step execution.
   - Candidate signal 3: Cross-reference the agent's NDJSON tool-call stream for `mv` commands targeting Done/ paths.
   Evaluate each signal's reliability, false-positive rate, and integration cost.
3. **Where the guard fires.** For the chosen signal, what is the right place to fire it?

#### Design options to evaluate

- **Option B1 — Gate-level (`_gate_no_unauthorized_done_move`).** New gate in `gates.py`, runs in `check()` after step completion. Fires `unauthorized_done_move` failure when detection signal trips. Plan goes to `verdict-pending-` with gate_failure. Planner sees it via Rule 22 and decides whether to accept (rare) or reject (default).
- **Option B2 — Lifecycle-error in `run_plan`.** Check filesystem state in `bellows.py` after `runner.run_step` returns but before `gates.check()` runs. If unauthorized move detected, raise a custom exception that routes the plan to a `halted-mode-a-violation-` state. Stronger structural answer; can't be waved through by Planner.
- **Option B3 — Hybrid.** Both layers: lifecycle-error catches the structural case (plan file gone), gate catches secondary cases (e.g., partial state, race conditions). Higher implementation cost.

For each option:
- Implementation surface: which file, which function, ~LOC estimate
- Failure modes the option does NOT close
- Interaction with the disable-auto-close model (2026-04-24): under disable-auto-close, NO terminal-step automatic transition happens — every plan pauses for verdict. The guard must distinguish "agent prematurely moved" from "Planner's terminal-step Rule 25 move" (which happens AFTER the verdict cycle, not during step execution).
- Test surface: what new tests in `test_gates.py` or `test_bellows.py` would lock the guard's contract?

#### Recommendation

Conclude Sub-B with a single recommended option (or hybrid). State why.

### Combined recommendation section

After Sub-A and Sub-B, write a "Combined Recommendation" section that:

1. Names the recommended Sub-A option and the recommended Sub-B option
2. States whether they compose (most should — they're orthogonal layers)
3. Identifies any sequencing constraints (e.g., "ship Sub-A first because the system prompt change has lower test surface" or "ship Sub-B first because the prompt change requires a test plan that depends on the guard being in place")
4. Estimates total implementation surface (LOC, files touched, tests added) for the combined Plan 2 executable

### Output structure

Findings file at `bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md` with these sections:

1. **Summary** — One paragraph stating the recommended Sub-A option, recommended Sub-B option, and whether they ship as one plan or sequenced.
2. **Sub-investigation A — Prompt Surface**
   1. Where the prohibition lives today (cited)
   2. What primes the agent toward `mv` (cited from both reproduction plans)
   3. Restructuring options evaluated (with implementation surface + closure-strength)
   4. Recommendation
3. **Sub-investigation B — Guard Surface**
   1. Filesystem state at gate-evaluation time (cited)
   2. Detection signal candidates evaluated
   3. Design options evaluated (with implementation surface + LOC + tests)
   4. Recommendation
4. **Combined Recommendation** — composition, sequencing, total surface estimate
5. **Open questions for CEO/Planner** — anything that requires a decision before Plan 2 can be authored

### Constraints

- Read-only diagnostic. Do not modify any files outside the deposit path.
- Do not write or modify tests. Test surface is described as future work.
- Cite raw evidence (file paths with line ranges, code excerpts, plan-text quotes). The Planner needs to verify your claims via Rule 22.
- If a candidate option turns out to be infeasible (e.g., `claude -p` does not support `--system-prompt`, or a filesystem state cannot be reliably observed), say so explicitly and explain why. Do not invent feasibility.
- Single-step plan: complete both sub-investigations and the combined recommendation in this step.

### Rule 20 self-check

After writing the findings file, run this self-check Python block:

```python
import os

deposit_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/failure-3-mode-a-closure-design-2026-05-06.md"

print("=" * 60)
print("Rule 20 Self-Check")
print("=" * 60)

checks = []
checks.append(("Findings file exists", os.path.isfile(deposit_path)))

if os.path.isfile(deposit_path):
    with open(deposit_path) as f:
        content = f.read()
    checks.append(("Has Summary section", "## Summary" in content or "# Summary" in content))
    checks.append(("Has Sub-investigation A", "Sub-investigation A" in content or "Sub-Investigation A" in content))
    checks.append(("Has Sub-investigation B", "Sub-investigation B" in content or "Sub-Investigation B" in content))
    checks.append(("Has Combined Recommendation", "Combined Recommendation" in content or "## Combined" in content))
    checks.append(("Sub-A has recommendation", "Recommendation" in content.split("Sub-investigation B")[0] if "Sub-investigation B" in content else False))
    checks.append(("Sub-B has recommendation", content.count("Recommendation") >= 2 or content.count("recommendation") >= 2))
    checks.append(("File is non-trivial (>4KB)", len(content) > 4000))

for label, result in checks:
    glyph = "✅" if result else "❌"
    print(f"{glyph} {label}")

all_pass = all(result for _, result in checks)
print()
print("SELF-CHECK PASSED" if all_pass else "SELF-CHECK FAILED")
```

### Output Receipt

End your response with the standard SA output receipt block (per `BELLOWS_SYSTEMS_ANALYST.md`). The "Status" should be `Complete`. The "Files Deposited" should list the findings file path. "Flags for CEO" should briefly state the recommended Sub-A option, the recommended Sub-B option, and any open questions.

### CRITICAL — Do not move plan to Done/

This plan is a diagnostic. Do NOT move this plan file to Done/. Do NOT execute `mv` or any equivalent operation on the plan file. Do NOT touch the `decisions/` directory at all. The Planner performs the Done/ move after Rule 22 verification. If you find yourself reasoning about Done/ paths, that is task material — not authorization. The two prior Mode A reproductions occurred because agents performed unauthorized Done/ moves on plans whose subject matter discussed Done/ paths. This plan's subject matter discusses Done/ paths even more directly than the prior two. Stop after writing the findings file and the Output Receipt. Do not perform any cleanup operations.

---

## Plan Lifecycle

Single-step diagnostic. After Step 1 completes:

1. Planner reads deposited findings file directly (Rule 22)
2. Planner verifies cited evidence
3. Planner authors Plan 2 (executable) implementing the recommendations
4. Planner moves this plan file to `Done/` per Rule 25 terminal-step resolution

No auto-close.
