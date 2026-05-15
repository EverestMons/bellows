# R3 Inline Step Text — Prompt-Construction Surface Findings
**Date:** 2026-04-19 | **Diagnostic:** diagnostic-r3-inline-step-text-surface-2026-04-19

## Summary

The bootstrap prompt is constructed in a single function (`run_plan` in `bellows.py`, lines 240–245) with three f-string variants (diagnostic, resume, fresh Step 1) plus one mid-loop continuation prompt (line 301). All four interpolate a filesystem path (`plan_path` or `inprogress_path`) that directs the agent to read the plan file itself. The agent depends on this path for five capabilities: reading step instructions, claiming the plan via `shutil.move`, moving the plan to Done, committing the plan file in git, and deriving sibling deposit paths. Cross-step references in production plans are overwhelmingly satisfiable from deposited artifacts (type b), making the strictest R3 variant (inline current step only) feasible for all examined plans. The `--resume` flag is used for Step 2+ and preserves full session history, meaning prior-step context is available even without re-reading the plan file.

---

## Q1 — Bootstrap Prompt Construction

### Primary prompt construction site: `bellows.py:run_plan()` (lines 240–245)

```python
# bellows.py lines 240-245
if is_diagnostic:
    bootstrap_prompt = f"Read the diagnostic at {plan_path}. Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done."
elif resume_step is not None:
    bootstrap_prompt = f"Read the plan at {plan_path}. Execute Step {resume_step}. After completing Step {resume_step}, STOP and wait for my confirmation."
else:
    bootstrap_prompt = f"Read the plan at {plan_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2."
```

Three variants:
1. **Diagnostic** — single-step, directs agent to read the full diagnostic at `{plan_path}`
2. **Resume** — used when `resume_step` is not None (verdict-continue path), directs agent to read plan and execute a specific step
3. **Fresh Step 1** — default initial dispatch

### Mid-loop continuation prompt: `bellows.py:run_plan()` (line 301)

```python
# bellows.py line 301
default_next_prompt = f"Read the plan at {inprogress_path}. Execute Step {current_step + 1}."
```

Used when the while-loop auto-advances to the next step (all gates passed, not QA, no pause).

### Call sites invoking `runner.run_step()`

**Site 1 — Initial dispatch** (`bellows.py` lines 250–252):
```python
parsed = runner.run_step(bootstrap_prompt, project_path, model,
                          timeout=config.get("step_inactivity_timeout_seconds",
                                             config.get("step_timeout_seconds", 300)))
```
No `session_id` passed — creates a new session.

**Site 2 — Continuation** (`bellows.py` lines 306–311):
```python
parsed = runner.run_step(
    default_next_prompt, project_path, model,
    session_id=parsed.get("session_id"),
    timeout=config.get("step_inactivity_timeout_seconds",
                       config.get("step_timeout_seconds", 300)),
)
```
Passes `session_id` from prior step — resumes existing session.

### `runner.run_step()` subprocess construction (`runner.py` lines 33–40)

```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "json",
    "--model", model,
    "--allowedTools", allowed_tools,
]
if session_id is not None:
    cmd += ["--resume", session_id]
```

Arguments received: `prompt` (str), `project_path` (str, used as `cwd`), `model` (str), `session_id` (Optional[str]), `allowed_tools` (str, default `"Read,Edit,Write,Bash"`), `timeout` (int).

The prompt string is passed directly as the second positional argument to `claude -p`. The `project_path` sets the working directory (`cwd=project_path`, line 53). The plan file path appears only inside the prompt text — it is NOT passed as a separate CLI argument.

### Additional prompt-construction sites

**`planner.py` lines 119–124 — Planner consultation prompt:**
```python
prompt = (
    f"Read {consult_path} carefully. You are the Eluvian Project Planner. "
    "Return ONLY a JSON object — no prose, no markdown fences. "
    'Schema: {"decision": "continue" | "rewrite" | "escalate", '
    '"reason": "one sentence", '
    '"next_step_prompt": "full revised prompt string or null"}'
)
```
This is a separate code path (Planner API, not agent execution). It reads a temporary consultation file, not the plan itself. **Not in scope for R3** — the Planner's prompt does not contain a plan path that the agent could mutate.

**No other prompt-construction sites found** in `bellows/*.py` (excluding tests).

### Inventory summary

| Function | File:Line | Receives plan path via | Path appears in prompt as | Purpose |
|---|---|---|---|---|
| `run_plan` (diagnostic) | `bellows.py:241` | `plan_path` local var | `f"Read the diagnostic at {plan_path}..."` | Initial diagnostic dispatch |
| `run_plan` (resume) | `bellows.py:243` | `plan_path` local var | `f"Read the plan at {plan_path}..."` | Verdict-continue resume |
| `run_plan` (fresh) | `bellows.py:245` | `plan_path` local var | `f"Read the plan at {plan_path}..."` | Initial Step 1 dispatch |
| `run_plan` (continuation) | `bellows.py:301` | `inprogress_path` local var | `f"Read the plan at {inprogress_path}..."` | Mid-loop auto-advance |

---

## Q2 — Agent Capabilities Depending on Plan File Path

### Sources of path-dependent instructions

1. **Bootstrap prompt** — all four variants interpolate `{plan_path}` or `{inprogress_path}`, directing the agent to read the plan file.
2. **Plan step text (Planner conventions)** — every executable plan's Step 1 contains a "claim this plan" `shutil.move` instruction with the original plan filename hardcoded. Final steps often contain a "move to Done" `shutil.move` with the `in-progress-` filename hardcoded. Git commit instructions reference the plan file path.

### Capability table

| # | Capability | Where expected | Requires plan path? | Alternative if path unknown |
|---|---|---|---|---|
| 1 | **Read step instructions** — agent reads the plan file to find the `## STEP N` block and the quoted instructions within it | Bootstrap prompt: `"Read the plan at {plan_path}"` | **Yes** — agent uses the path to open and read the file | Inline step text directly in the bootstrap prompt (R3 core change) |
| 2 | **Claim plan (shutil.move to in-progress-)** — agent moves original plan filename to `in-progress-` prefix | Plan step text (Step 1 blockquote): `shutil.move("bellows/.../executable-...", "bellows/.../in-progress-executable-...")` | **Yes** — hardcoded source + dest paths in step text | **Already handled by Bellows** (`bellows.py:221–223`). The agent's claim instruction is now redundant. Bellows claims atomically before dispatching the agent. Can be removed from plan templates. |
| 3 | **Move plan to Done** — agent moves in-progress plan to Done/ directory | Plan step text (final step housekeeping): `shutil.move("bellows/.../in-progress-...", "bellows/.../Done/...")` | **Yes** — hardcoded paths in step text | **Already handled by Bellows** for auto-close plans (`bellows.py:366–378`). For non-auto-close plans, the agent move is the primary mechanism. R3 would need to either: (a) rely entirely on Bellows auto-close / verdict-continue-to-done, or (b) pass the plan path as a housekeeping-only variable. |
| 4 | **Commit plan file in git** — some QA steps include `git add bellows/knowledge/decisions/...` | Plan step text (final step housekeeping): `git add bellows/knowledge/decisions/ && git commit -m "..."` | **Partially** — uses the decisions directory, not the specific filename | Agent can still `git add bellows/knowledge/decisions/` without knowing the specific filename. Low risk. |
| 5 | **Derive deposit paths relative to plan** — deposits are typically at paths like `bellows/knowledge/research/...` or `bellows/knowledge/qa/...` | Plan step text (Deposits block): deposit paths are absolute from project root | **No** — deposit paths are hardcoded in the step text, not derived from the plan path | No change needed. |
| 6 | **Feedback log append** — standard protocol appends to `bellows/knowledge/research/agent-prompt-feedback.md` | Plan step text: `"Standard prompt feedback protocol → bellows/knowledge/research/agent-prompt-feedback.md"` | **No** — path is hardcoded | No change needed. |
| 7 | **Cross-step verification** — later steps reference earlier step's deposits to verify completion | Plan step text (Step 2 verification): `"read bellows/knowledge/development/...-2026-04-19.md and check the Output Receipt"` | **No** — references deposited artifacts by their own paths, not the plan path | No change needed. |

### Key finding

Only capabilities 1–3 depend on the plan file path. Capability 1 is the core R3 target. Capability 2 is already redundant (Bellows handles claiming). Capability 3 is the only remaining structural dependency — and it is already handled by Bellows for auto-close/verdict paths, leaving only the "agent moves to Done" convention in non-auto-close plan templates.

---

## Q3 — Cross-Step Reference Counts

### Plan 1: executable-backlog-append-2026-04-19 (Small, 2 steps)

| Reference in Step 2 | Target | Classification |
|---|---|---|
| "read `bellows/knowledge/BACKLOG.md` and confirm the three new bullets from Step 1 are present" | Step 1's deposited artifact (BACKLOG.md) | **(b)** satisfiable by deposited artifact |
| Rule 20 self-check references `evidence_dir` and `qa_report_path` | Artifacts created in Step 2 itself | **(c)** present in current step text |

**Count: 1 cross-step reference, 1 type (b), 0 type (a)**

### Plan 2: executable-verdict-lifecycle-coupling-2026-04-19 (Medium, 2 steps)

| Reference in Step 2 | Target | Classification |
|---|---|---|
| "read `bellows/knowledge/development/verdict-lifecycle-coupling-2026-04-19.md` and check the Output Receipt status field" | Step 1's deposit (dev log) | **(b)** satisfiable by deposited artifact |
| "Read the Step 1 dev log's 'Files Created or Modified (Code)' list" | Step 1's deposit (dev log) | **(b)** satisfiable by deposited artifact |
| grep checks for `_cleanup_verdicts_for_slug` and call sites in `bellows.py` | Code changes made by Step 1 | **(b)** satisfiable by reading the modified source files |
| "baseline from the 2026-04-19 `_handle` subdirectory guard work was 42/42 passing" | Static context | **(c)** present in current step text |
| Step 2 references plan template conventions (Rule 17, 20, 23) | Governance documents | **(c)** present in current step text |

**Count: 3 cross-step references, 3 type (b), 0 type (a)**

### Plan 3: executable-plan-mutation-canary-2026-04-19 (Small, 2 steps)

| Reference in Step 2 | Target | Classification |
|---|---|---|
| "read `bellows/knowledge/research/_canary-step1-2026-04-19.txt` and verify it contains `step1-sentinel`" | Step 1's deposit (sentinel file) | **(b)** satisfiable by deposited artifact |
| `shutil.move("bellows/knowledge/decisions/in-progress-executable-plan-mutation-canary-2026-04-19.md", "bellows/knowledge/decisions/Done/...")` | Plan file itself (move-to-Done) | **(a)** requires reading plan file for its path |

**Count: 2 cross-step references, 1 type (b), 1 type (a)**

### Aggregate findings

| Plan | Total cross-step refs | Type (a): requires plan file | Type (b): deposited artifact | Type (c): in current step text |
|---|---|---|---|---|
| backlog-append (Small) | 1 | 0 | 1 | 0 |
| verdict-lifecycle (Medium) | 3 | 0 | 3 | 0 |
| plan-mutation-canary (Small) | 2 | 1 | 1 | 0 |

**Conclusion:** Cross-step references are overwhelmingly type (b) — satisfiable from deposited artifacts, not from re-reading the plan file. The only type (a) reference found is the `shutil.move` to Done, which is a housekeeping action that Bellows already handles for auto-close and verdict paths. **R3's strictest variant (inline current step only) is structurally feasible** — no step requires reading sibling step content from the plan file for its core work.

---

## Q4 — `--resume` Session Context Preservation

### Code evidence

`runner.py` lines 39–40:
```python
if session_id is not None:
    cmd += ["--resume", session_id]
```

`bellows.py` Step 1 dispatch (line 250): **No** `session_id` — creates a new session.

`bellows.py` continuation dispatch (lines 306–311): **Passes** `session_id=parsed.get("session_id")` — resumes prior session.

`bellows.py` verdict-continue resume path (`_consume_verdicts`, line 676):
```python
self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```
This calls `handle_new_plan` → `_run_tracked` → `run_plan` with `resume_step` set. In `run_plan`, the resume bootstrap prompt (line 243) does NOT pass a `session_id` — it creates a **new** session. The previous session from pre-verdict steps is **lost**.

### Session semantics

Two distinct multi-step continuation paths exist:

1. **Auto-advance (while-loop)** — uses `--resume session_id`. The agent's full conversation history from Step 1 is available in Step 2. Prior-step context IS preserved.

2. **Verdict-continue (post-pause resume)** — creates a new session. The agent has NO prior context from the pre-verdict steps. The new prompt tells the agent to re-read the plan file at `{plan_path}` to reacquire context.

### Implications for R3

- **Auto-advance path:** Since `--resume` preserves the full session, the agent already has the plan content from Step 1's read. Inlining the current step's text in the continuation prompt would be additive (the agent has prior + current context). This is safe — the agent doesn't need to re-read the plan file.

- **Verdict-continue path:** Since no session is resumed, the agent starts cold. Currently it re-reads the plan file. Under R3 (inline current step only), the agent would receive just the current step's text in the prompt — it would NOT have prior step context. This is viable because cross-step references are type (b) (deposited artifacts), not type (a) (plan file content). But the agent would lose the plan's header metadata (Date, Tier, Test Scope) and the "How to Run This Plan" context. These are informational, not operational.

**Open empirical question:** Does `claude -p --resume session_id` preserve the full prompt+response history including tool call results, or just the text messages? If tool results (file reads) are preserved, then the auto-advance agent already has the plan content cached in its context. If not, it would need to re-read. **Flag:** This question cannot be definitively answered from the code alone — it depends on Claude Code's internal session management, which is not inspectable from this codebase.

---

## Q5 — R3 Variants (Smallest-Diff to Largest-Diff)

### Variant (a): Inline current step only

**What changes:** `run_plan` extracts the current step's text from the plan (using the step number and a regex or parser to find the `## STEP N` block) and injects it directly into the bootstrap prompt. The plan file path is NOT included in the prompt. The prompt becomes: `"You are executing Step {N} of plan {plan_name}. Here are your instructions:\n\n{step_text}"`.

**Code surface:** ~10-line change in `bellows.py:run_plan()` — add a step-text extractor function, modify the four prompt-construction sites to use the extracted text instead of the path.

| Capability | Impact |
|---|---|
| 1. Read step instructions | **Preserved** — instructions are in the prompt |
| 2. Claim plan (shutil.move) | **N/A** — already handled by Bellows; agent instruction becomes dead code |
| 3. Move to Done | **Broken** — agent doesn't know the path. Mitigated: Bellows handles this for auto-close + verdict paths. Plan templates can remove agent-side move-to-Done instructions. |
| 4. Commit plan file in git | **Partially broken** — agent can still `git add bellows/knowledge/decisions/` but won't know the specific filename. Low impact since the plan file itself shouldn't be modified by the agent. |
| 5. Derive deposit paths | **Preserved** — hardcoded in step text |
| 6. Feedback log append | **Preserved** — hardcoded path |
| 7. Cross-step verification | **Preserved** — references deposited artifacts |

### Variant (b): Inline full plan, strip path

**What changes:** `run_plan` reads the full plan content and injects it verbatim into the bootstrap prompt. No plan file path is included. The prompt becomes: `"Here is the full plan:\n\n{plan_text}\n\nExecute Step {N} only."`.

**Code surface:** ~5-line change — replace path interpolation with content interpolation.

| Capability | Impact |
|---|---|
| 1. Read step instructions | **Preserved** — full plan in prompt |
| 2. Claim plan | **Broken** — agent sees the move instruction but can't execute it (no path). Mitigated: Bellows handles this. |
| 3. Move to Done | **Broken** — same as (a). Agent sees the instruction but can't derive the actual filesystem path. |
| 4. Commit plan file | **Partially broken** — same as (a) |
| 5–7 | **Preserved** |

**Advantage over (a):** Agent can cross-reference steps (e.g., Step 2 can see Step 1's Deposits block). **Disadvantage:** Larger prompt token count (full plan vs. single step). Plan mutation risk is NOT eliminated — the agent can't write to the plan path, but the full plan text is in the prompt and could still be truncated by context limits on very large plans.

### Variant (c): Pass shadow cache path as read-only

**What changes:** Instead of the mutable `in-progress-` path, the prompt passes `{shadow_cache_path}` (`.bellows-cache/{name}.pristine`). Shadow copies are already written by Bellows at claim time (`bellows.py:224–225`). The prompt becomes: `"Read the plan at {shadow_path}. Execute Step {N}."`.

**Code surface:** ~3-line change — replace `plan_path`/`inprogress_path` with `_shadow_path(plan_filename)` in prompt construction.

| Capability | Impact |
|---|---|
| 1. Read step instructions | **Preserved** — agent reads the shadow copy |
| 2. Claim plan | **Broken** — agent's claim instruction references the original path, not the shadow. Mitigated: Bellows handles this. The shadow path is intentionally read-only. |
| 3. Move to Done | **Broken** — agent doesn't know the mutable path. Same mitigation as (a). |
| 4. Commit plan file | **Broken** — shadow cache is in `.bellows-cache/`, not in `knowledge/decisions/`. Agent shouldn't commit it. |
| 5–7 | **Preserved** |

**Advantage:** Eliminates plan-mutation risk entirely — the shadow copy is pristine and the agent reads from `.bellows-cache/` which is not the plan's lifecycle-managed location. **Disadvantage:** Agent still reads a file (token cost of the read tool call), and the `.bellows-cache/` path leaks an implementation detail.

### Variant (d): Hybrid — inline full plan text + pass plan path for housekeeping only

**What changes:** The bootstrap prompt includes the full plan text inline AND the plan path in a separate "housekeeping context" section. The prompt becomes: `"Here is the full plan:\n\n{plan_text}\n\nExecute Step {N}. For housekeeping moves, the plan file is at: {plan_path}"`.

**Code surface:** ~8-line change — concat plan text + path into prompt.

| Capability | Impact |
|---|---|
| 1. Read step instructions | **Preserved** — full plan in prompt |
| 2. Claim plan | **Preserved** — agent has the path (though Bellows already handles this) |
| 3. Move to Done | **Preserved** — agent has the path |
| 4. Commit plan file | **Preserved** — agent has the path |
| 5–7 | **Preserved** |

**Advantage:** All capabilities preserved. Agent doesn't need to read the plan file (saves a tool call). **Disadvantage:** Does NOT eliminate plan-mutation risk — agent still knows the path and can write to it. Prompt is larger (full plan text + path). This variant is the most conservative but delivers the least protection against the original BACKLOG #6/#7 problem (agent truncating the plan file).

### Variant comparison matrix

| Variant | Diff size | Plan-mutation risk eliminated? | Capabilities broken | Token overhead | Requires plan template changes? |
|---|---|---|---|---|---|
| **(a) Inline current step** | ~10 lines | **Yes** | #3 (move-to-Done) | Low (1 step) | Yes — remove agent-side claim + move-to-Done |
| **(b) Inline full plan** | ~5 lines | **Partially** (no path, but full text in context) | #2, #3 | High (full plan) | Yes — remove agent-side claim + move-to-Done |
| **(c) Shadow cache read-only** | ~3 lines | **Yes** | #2, #3, #4 | Medium (file read) | Yes — remove agent-side claim + move-to-Done |
| **(d) Hybrid (inline + path)** | ~8 lines | **No** | None | High (full plan + path) | No |

---

## Output Receipt

**Step:** 1 (single-step diagnostic)
**Status:** Complete
**Files Created:**
- `bellows/knowledge/research/r3-inline-step-text-surface-2026-04-19.md` (this file)

**Escalate:** No
**CEO Flags:** None
