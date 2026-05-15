# SA Blueprint — R3 Variant (c): Shadow Cache Read-Only Prompt
**Date:** 2026-04-19 | **Input:** diagnostic-r3-inline-step-text-surface-2026-04-19

---

## B1 — Shadow Path Helper

### Existing helper — no new function needed

A `_shadow_path` helper already exists at `bellows.py:90-98`:

```python
def _shadow_path(plan_filename: str) -> Path:
    """Return the shadow cache path for a given plan filename."""
    # Strip lifecycle prefixes to get the canonical name
    canonical = plan_filename
    for prefix in ("in-progress-", "verdict-pending-", "halted-"):
        if canonical.startswith(prefix):
            canonical = canonical[len(prefix):]
            break
    return SHADOW_CACHE_DIR / f"{canonical}.pristine"
```

**Return type:** `pathlib.Path` (absolute). `SHADOW_CACHE_DIR` is defined at `bellows.py:18` as `BELLOWS_ROOT / ".bellows-cache"`, where `BELLOWS_ROOT = Path(__file__).parent.resolve()` (line 16). This means `_shadow_path` returns an absolute path rooted at the bellows project directory.

**Example output for `executable-foo-2026-04-19.md`:**
`/Users/marklehn/Desktop/GitHub/bellows/.bellows-cache/executable-foo-2026-04-19.md.pristine`

**Shadow write code at `bellows.py:224-225` (verbatim):**
```python
            # Write shadow copy immediately after claim — preserves pristine content
            _write_shadow(plan_filename, plan_text)
```

`_write_shadow` calls `_shadow_path(plan_filename)` internally (line 104), so the write and read paths are guaranteed consistent as long as the same `plan_filename` value is used. No new helper is needed.

**DEV instruction:** Use the existing `_shadow_path(plan_filename)` function. Convert its return value to `str()` for f-string interpolation in prompt construction.

---

## B2 — Path Resolution from Agent CWD

### Recommendation: absolute path (option ii)

**Rationale:**
1. `runner.py:53` sets `cwd=project_path`, where `project_path` is derived from the plan file's grandparent directory (`bellows.py:198`: `project_path = str(plan_p.parents[2])`). For plans in `bellows/knowledge/decisions/`, this resolves to the parent of the `bellows/` directory (e.g., `/Users/marklehn/Desktop/GitHub`), NOT the `bellows/` directory itself.

2. `_shadow_path` returns an absolute `pathlib.Path` (via `BELLOWS_ROOT` which is `Path(__file__).parent.resolve()`). Using `str(_shadow_path(...))` produces an absolute path like `/Users/marklehn/Desktop/GitHub/bellows/.bellows-cache/executable-foo-2026-04-19.md.pristine`.

3. The existing prompts use `plan_path` and `inprogress_path`, which are constructed via `os.path.join(plan_dir, ...)` where `plan_dir = str(pathlib.Path(plan_path).parent)`. Since `plan_path` comes from a filesystem walk, these are already absolute paths. The current prompts already pass absolute paths to the agent.

4. A project-relative path (`.bellows-cache/...`) would only work if `cwd` were the bellows directory. But `cwd=project_path` is the *parent* of bellows (the GitHub root). The relative path `.bellows-cache/...` would resolve incorrectly to `/Users/marklehn/Desktop/GitHub/.bellows-cache/...` instead of `/Users/marklehn/Desktop/GitHub/bellows/.bellows-cache/...`. This is a CWD mismatch risk.

**DEV instruction:** Use `str(_shadow_path(plan_filename))` in all four prompt sites. This produces an absolute path consistent with the existing absolute-path convention and correct regardless of agent CWD.

---

## B3 — Prompt Template Changes

### Variable setup

Before the four prompt sites, DEV must compute the shadow path string. Insert a single line immediately before the `if is_diagnostic:` block (after line 239, before line 240):

```python
        shadow_prompt_path = str(_shadow_path(plan_filename))
```

### Replacement table

| Line | Current f-string (verbatim) | Replacement f-string | Context |
|---|---|---|---|
| 241 | `f"Read the diagnostic at {plan_path}. Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done."` | `f"Read the diagnostic at {shadow_prompt_path}. Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done."` | Diagnostic dispatch |
| 243 | `f"Read the plan at {plan_path}. Execute Step {resume_step}. After completing Step {resume_step}, STOP and wait for my confirmation."` | `f"Read the plan at {shadow_prompt_path}. Execute Step {resume_step}. After completing Step {resume_step}, STOP and wait for my confirmation."` | Resume (verdict-continue) |
| 245 | `f"Read the plan at {plan_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2."` | `f"Read the plan at {shadow_prompt_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2."` | Fresh Step 1 |
| 301 | `f"Read the plan at {inprogress_path}. Execute Step {current_step + 1}."` | `f"Read the plan at {shadow_prompt_path}. Execute Step {current_step + 1}."` | Mid-loop continuation |

**Note on line 301:** The current code uses `inprogress_path` (not `plan_path`). The replacement uses `shadow_prompt_path` which is computed from `plan_filename` — this is correct because `plan_filename` is set at line 201 from the original `plan_path`, and `_shadow_path` strips lifecycle prefixes internally, so it resolves to the same shadow file regardless of whether the input has the `in-progress-` prefix or not.

---

## B4 — Agent Move-to-Done Interaction

### Current move-to-Done responsibility

| Plan type | Who moves to Done today? | Code reference |
|---|---|---|
| **(a) Auto-close plans** (all gates passed, `auto_close` effective true) | **Bellows** — `bellows.py:368-374`. Moves `inprogress_path` or `plan_path` to `Done/` directory. Calls `_delete_shadow` and `_cleanup_verdicts_for_slug`. | Lines 361-379 |
| **(b) Verdict-continue to Done** (continue verdict on final step) | **Bellows** — `bellows.py:660-665`. Moves `full_plan_path` (verdict-pending variant) to `Done/`. Calls `_delete_shadow` and `_cleanup_verdicts_for_slug`. | Lines 655-668 |
| **(c) Non-auto-close plans (agent move-to-Done)** | **Agent** — plan step text contains `shutil.move("bellows/.../in-progress-...", "bellows/.../Done/...")`. The agent executes this via Bash tool during QA step housekeeping. Bellows does NOT handle this path — if the agent doesn't move, the plan stays in-progress. | Plan template convention (Step E in QA steps) |

### Impact of variant (c) on each plan type

| Plan type | After variant (c), who moves to Done? | Gap? |
|---|---|---|
| **(a) Auto-close** | **Bellows** (unchanged) — auto-close code reads `inprogress_path` and `plan_path` directly, not from the prompt. No change needed. | No gap |
| **(b) Verdict-continue-to-Done** | **Bellows** (unchanged) — `_consume_verdicts` finds the verdict-pending file by scanning the directory and uses `full_plan_path` derived from the filesystem scan. No dependency on the prompt path. | No gap |
| **(c) Non-auto-close agent move** | **Gap exists.** The agent's `shutil.move` instruction in the plan template hardcodes `in-progress-executable-...` as the source path. Under variant (c), the agent sees this instruction when it reads the shadow copy, but the instruction references the correct `in-progress-*` path by name (it's hardcoded in the plan text, not derived from the bootstrap prompt path). The agent CAN still execute the move because the path is in the plan's step text, not computed from `{plan_path}`. | **No gap** — see analysis below |

### Detailed analysis of case (c)

The agent's move-to-Done instruction in plan templates looks like this (from the current plan's Step 3, Step E):
```python
shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-r3-shadow-cache-prompt-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-r3-shadow-cache-prompt-2026-04-19.md")
```

This path is **hardcoded in the plan text** — it is NOT derived from the bootstrap prompt's `{plan_path}`. When the agent reads the shadow copy at `.bellows-cache/...pristine`, it sees the full plan text including the hardcoded move instruction. The agent can execute this `shutil.move` regardless of which path it used to *read* the plan.

**Conclusion: No housekeeping fallback is needed.** The move-to-Done instruction in plan templates uses hardcoded absolute paths, not prompt-derived paths. Variant (c) does not break agent-side move-to-Done.

---

## B5 — Test Coverage Plan

### Existing test file structure

The sole test file for `bellows.py` is `bellows/tests/test_bellows.py`. Two existing tests are directly relevant:

1. **`test_run_plan_resume_step_uses_correct_prompt`** (line 398) — captures the bootstrap prompt via a fake `run_step` and asserts content. Uses `tempfile.TemporaryDirectory` with a plan file, mocks `runner.run_step`, `gates.check`, `notifier.push`, `verdict.log_to_ledger`, `_capture_git_diff`, and `record_run`.

2. **`test_run_plan_bootstrap_prompt_uses_inprogress_path`** (line 983) — captures the bootstrap prompt and asserts it contains the `in-progress-` path. This test **must be updated** to assert the shadow path instead.

### Required test changes

**(i) Update `test_run_plan_bootstrap_prompt_uses_inprogress_path` (line 983)**

This test currently asserts:
```python
assert expected_inprogress in bootstrap
```
where `expected_inprogress = f"in-progress-{plan_filename}"`.

After variant (c), the bootstrap prompt should contain the shadow path, NOT the in-progress path. Update the test to:
- Assert the bootstrap prompt contains `.bellows-cache/` and `.pristine`
- Assert the bootstrap prompt does NOT contain `in-progress-`
- Rename the test to `test_run_plan_bootstrap_prompt_uses_shadow_path`

**(ii) New test: `test_run_plan_continuation_prompt_uses_shadow_path`**

Add a test that exercises the mid-loop continuation path (line 301). Create a 2-step plan, mock gates to pass cleanly with auto_close=true, capture the continuation prompt (second call to `run_step`), and assert:
- Continuation prompt contains `.bellows-cache/` and `.pristine`
- Continuation prompt does NOT contain `in-progress-`
- Continuation prompt contains `Step 2`

**(iii) New test: `test_run_plan_diagnostic_prompt_uses_shadow_path`**

Add a test for the diagnostic variant (line 241). Create a diagnostic plan (filename starts with `diagnostic-`), capture the bootstrap prompt, and assert:
- Prompt contains `.bellows-cache/` and `.pristine`
- Prompt contains `Read the diagnostic at`
- Prompt does NOT contain `in-progress-` or the mutable plan path

**(iv) New test: `test_run_plan_resume_prompt_uses_shadow_path`**

Add a test for the resume variant (line 243). Create an in-progress plan, call `run_plan` with `resume_step=2`, capture the bootstrap prompt, and assert:
- Prompt contains `.bellows-cache/` and `.pristine`
- Prompt does NOT contain `in-progress-` as a file path in the prompt
- Prompt contains `Step 2`

**(v) Update `test_run_plan_resume_step_uses_correct_prompt` (line 398)**

This test currently only checks for `"Step 2"` and not-`"Step 1 ONLY"`. It does not assert on the path. After variant (c), add an assertion that the prompt contains the shadow path. This test does NOT need renaming — it tests resume step number correctness, which is orthogonal.

### Test pattern

All new/updated tests should follow the established pattern from `test_run_plan_bootstrap_prompt_uses_inprogress_path`: use `tempfile.TemporaryDirectory`, create a plan file with `## STEP N` headers, mock dependencies, capture prompts via `fake_run_step`, and assert on prompt content.

**Critical detail:** The shadow path is computed by `_shadow_path(plan_filename)` which uses `SHADOW_CACHE_DIR` (an absolute path based on `BELLOWS_ROOT`). In tests, `BELLOWS_ROOT` points to the real bellows directory, so the shadow path in the prompt will reference the real `.bellows-cache/` directory, NOT one inside the temp directory. The tests should assert on the path **string content** (contains `.bellows-cache/` and `.pristine`), not on file existence. A separate test (vi) below covers file existence.

**(vi) New test: `test_shadow_path_resolves_after_claim`**

Add a test that exercises the claim → shadow-write → prompt-construct sequence:
1. Create a plan file in a temp directory
2. Call `run_plan` (which claims the plan and writes the shadow copy)
3. After `run_plan` returns, verify that `_shadow_path(plan_filename).exists()` is True (or was True before auto-close deleted it — check by patching `_delete_shadow` to no-op)
4. Verify the shadow file content matches the original plan text

---

## B6 — Regression Risk Enumeration

### Risk 1: `--resume` continuation on Step 2+

**Risk:** After Step 1 completes via the auto-advance while-loop, Step 2's continuation prompt (line 301) is passed with `--resume session_id`. The resumed session preserves Step 1's full context (prompt + tool calls + responses). Step 1's prompt referenced the shadow path. Step 2's continuation prompt also references the shadow path. The agent has consistent path references across both steps.

**Assessment: SAFE.** The `--resume` path preserves the prior session. The shadow file persists until `_delete_shadow` is called (only in auto-close at line 375 or verdict consumption at lines 665/683). During the while-loop, the shadow file is never deleted. The agent can re-read it if needed.

### Risk 2: Verdict-continue resume

**Risk:** `_consume_verdicts` (line 676) calls `self.handle_new_plan(inprogress_path, resume_step=step_number + 1)`. This enters `run_plan` with `resume_step` set, triggering the resume bootstrap prompt (line 243). This creates a **new session** (no `session_id` passed). The new prompt references `shadow_prompt_path`.

**Assessment: SAFE.** The shadow file was written at original claim time (`bellows.py:224-225`) and is NOT deleted during the verdict-pending phase (verdict-pending rename at line 294 does not touch the shadow). The `_read_shadow` call at line 205 will find the shadow file when `run_plan` re-enters for the resume. The resume prompt will reference the shadow path, and the shadow file will exist on disk. The agent can read it successfully.

**Verification detail:** `_shadow_path` strips lifecycle prefixes (line 94-96). When `run_plan` re-enters with `inprogress_path` as `plan_path`, `plan_filename` at line 201 is `os.path.basename(plan_path)` = `in-progress-executable-foo-...`. `_shadow_path("in-progress-executable-foo-...")` strips the `in-progress-` prefix and returns the same path as `_shadow_path("executable-foo-...")`. Consistent.

### Risk 3: Output Receipts referencing plan file paths

**Risk:** If agents produce Output Receipts that cite the plan file path (e.g., `in-progress-executable-...`) in their "Files Created or Modified" section, variant (c) could change those receipts to cite the shadow path instead.

**Assessment: SAFE — no receipts cite plan file paths.** Grepped the 5 most recent QA reports:
- `backlog-append-2026-04-19.md` — no `in-progress-` references
- `verdict-lifecycle-coupling-2026-04-19.md` — "Files Created or Modified" section lists code files only, no plan path
- `handle-subdirectory-guard-2026-04-19.md` — `in-progress-` appears only in a CEO flag (restart reminder), not in the file receipt
- `watcher-on-moved-verification-2026-04-19.md` — "Files Created or Modified" section lists code files only
- `bellows-specialist-roster-verification-2026-04-19.md` — "Files Created or Modified" section lists code files only

No Output Receipts cite `in-progress-` or plan-file paths in their deliverable listings. The agent's receipt content is derived from the step text's `Deposits:` block (hardcoded paths), not from the bootstrap prompt path.

### Risk 4: `plan_path` variable still used elsewhere in `run_plan`

**Risk:** After the four prompt sites are updated, `plan_path` is still used in:
- Line 194: `plan_text = load_file(plan_path)` — reads the plan content. **Not affected** — this is the initial load, before prompt construction.
- Line 222: `shutil.move(plan_path, inprogress_path)` — claim move. **Not affected** — this moves the actual plan file.
- Line 233: `shutil.move(plan_path, ...)` — zero-step skip to Done. **Not affected** — lifecycle management.
- Line 287: `verdict.post_verdict_request(plan_path, ...)` — verdict request. **Not affected** — uses plan_path for metadata, not prompt.
- Line 295: `record_run(db_path, plan_path, ...)` — database logging. **Not affected**.
- Lines 353-354, 366-374: Verdict-pending and auto-close moves. **Not affected** — lifecycle management.

**Assessment: SAFE.** `plan_path` is used for lifecycle management and metadata throughout `run_plan`. Only the four prompt-construction sites pass it to the agent. All other uses are internal Bellows operations that must continue using the real filesystem paths. No changes needed outside the four prompt sites.

---

## Output Receipt

**Step:** 1 (SA Blueprint)
**Status:** Complete
**Files Created:**
- `bellows/knowledge/architecture/r3-shadow-cache-blueprint-2026-04-19.md` (this file)

**Escalate:** No
**CEO Flags:** None
