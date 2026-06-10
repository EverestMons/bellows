# scope_check False-Positive Fix Design

**Date:** 2026-06-09
**Author:** Bellows Systems Analyst
**Plan:** diagnostic-bellows-scope-check-fp-fix-2026-06-09
**Step:** 1 (SA diagnostic)
**BACKLOG entries:** #2 (2026-06-08, continuous-run cumulative diff) and #9 (2026-05-29, blueprint delegation)

---

## Section 1 — Mechanism Proof (Both FP Classes)

### (a) FP #2: Continuous-run cumulative diff

**Changed-file-set computation (bellows.py):**

Before each step, `pre_diff = _capture_git_diff(wt_path)` captures the current HEAD SHA via `git rev-parse HEAD` (bellows.py:460 for Step 1, bellows.py:553 for subsequent steps in the while loop).

After each step, `files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)` at bellows.py:496/589 runs:

```
git diff --stat=300 --relative <pre_diff> -- .
```

(bellows.py:741-743). This diffs between the `pre_diff` SHA and the **current working tree** (both committed and uncommitted changes).

For a continuous SA-DEV-QA run, cross-step leakage occurs when a prior step's file changes are not fully committed (they remain staged or as working-tree modifications). Those changes persist in subsequent steps' `git diff` output. The prior step's uncommitted files appear in `files_changed` for all subsequent steps.

Confirmed by BACKLOG #2: "Bellows cycle 2, also continuous, did NOT trip it -- its Step-1 deposits are name-referenced in the QA-step prompt, so they matched." Both cycles included prior-step files in `files_changed`; cycle 2 passed only because the file basenames happened to appear in the QA step text.

**Scope-check evaluation (gates.py):**

`_gate_scope_check` at gates.py:661 receives `plan_text`, `step_number`, and `files_changed`. At **gates.py:666**, it extracts:

```python
step_text = _extract_step_text(plan_text, step_number)
```

`_extract_step_text` (gates.py:384-393) uses the regex `r"^## STEP {step_number}\b.*?(?=^## STEP |\Z)"` with `re.DOTALL | re.MULTILINE` to extract the **full body** of only the current step -- from the `## STEP N` header to the next `## STEP` header or end of text. No other step's text is captured.

At **gates.py:677**, the matching is:

```python
if fpath in step_text or basename in step_text:
    continue
```

This is a pure substring match against the single step's text. A file from Step 1 that appears in Step 3's `files_changed` (via cross-step leakage) has no authorization path in Step 3's text.

**Capture width clarification:** BACKLOG #9 references "the ~80-char body capture." Correction: the **matching** uses the full step text (not truncated). The "~80 chars" refers to the **evidence display** at gates.py:700: `context = step_text[:200]`. A typical step header (`## STEP 2 -- Bellows Developer`) consumes ~30-40 chars of the 200-char evidence window, leaving ~160-170 chars of body visible. The ~80-char observation in the BACKLOG likely reflects a specific case where the step body was short or the evidence string was truncated in logging. The matching window is the full step body.

### (b) FP #9: Blueprint delegation

At **gates.py:677**, the check is:

```python
if fpath in step_text or basename in step_text:
```

No logic exists to follow a document reference. When Step 2 says "Implement per the blueprint deposited in Step 1" and the blueprint document at `knowledge/development/blueprint.md` lists 8 target files, the gate:

1. Sees "blueprint" and the blueprint path as text in `step_text` -- the blueprint FILE itself might match
2. Does NOT read the referenced document
3. Does NOT extract the target file list from the blueprint
4. Flags every target file (those listed only inside the blueprint) as out-of-scope

The directory-mention authorization (gates.py:679-696) also does not help because the target files are typically in multiple unrelated directories (not children of a single mentioned directory).

### Shared Root Cause

`_gate_scope_check` at gates.py:666-677 derives its allowed-file-set from a **single step's text body** (the step identified by `step_number`), while the checked-file-set (`files_changed`) can include files whose authorization lives in a **different step's text** (FP #2) or in a **referenced external document** (FP #9). The gate has a one-step-wide view of a multi-step plan's scope.

---

## Section 2 — Fix Design

### Primary Recommendation: Union of All Step Prompt Contexts

Evaluate each changed file against the **union of ALL step prompt contexts** (steps 1 through `step_number`), not only the current step's.

**Feasibility (load-bearing question):** Does `gates.check()` at the terminal step have access to all step texts?

**YES.** `gates.check()` at gates.py:187 receives `plan_text` (the full plan text, passed by bellows.py at lines 497 and 590). `_gate_scope_check` at gates.py:661 receives `plan_text` and `step_number`. It can extract all step texts internally by iterating `_extract_step_text(plan_text, s)` for `s` in `range(1, step_number + 1)`. **No caller-side change in bellows.py is needed.**

**Mechanical shape:**

In `_gate_scope_check`, replace gates.py:666-668:

```python
step_text = _extract_step_text(plan_text, step_number)
if not step_text:
    return
```

With:

```python
# Build union of all step contexts (steps 1 through step_number)
all_step_texts = []
for s in range(1, step_number + 1):
    st = _extract_step_text(plan_text, s)
    if st:
        all_step_texts.append(st)
if not all_step_texts:
    return
union_text = "\n".join(all_step_texts)

# Retain current step text for evidence display
step_text = _extract_step_text(plan_text, step_number) or ""
```

Then use `union_text` in place of `step_text` at:
- **gates.py:677** path/basename check: `if fpath in union_text or basename in union_text`
- **gates.py:691** directory-mention check: `if parent.count("/") >= 1 and (parent + "/") in union_text`

Retain `step_text` for the evidence display at gates.py:700 (`context = step_text[:200]`) -- shows only the current step's context for diagnostic clarity when a file IS flagged.

### Alternative Assessment

**Alternative 1 -- Per-producing-step attribution (via per-step commit boundaries):**

Attribute each file in `files_changed` to the step that produced it, then check each file against only its producing step's text. **Not recommended.** Requires reliable per-step commit boundaries (one commit per step, all files committed). Agents do not guarantee this: they may commit partially, commit multiple times, stage without committing, or leave files uncommitted. Would require either (a) changing agent behavior to commit deterministically (Layer 2 change, cross-boundary), or (b) a fallback when attribution fails (collapses to the union approach). High complexity for marginal precision gain.

**Alternative 2 -- Follow-the-blueprint-reference:**

When step text contains a reference pattern (e.g., "per the blueprint at `path`"), read the referenced document and extract its file list, adding those files to the allowed set. **Not recommended as primary fix.** (a) Only solves FP #9 (not #2). (b) **Regex-fragility risk:** blueprint reference patterns vary across plans ("Read the blueprint...", "Implement per the design at...", "per the blueprint deposited in Step 1", "see Step 1's deposit"). Each unrecognized pattern is a false negative. (c) Structural assumption about blueprint format (how file lists are expressed inside the document) adds a second fragility dimension. Could be added as a FUTURE enhancement layer on top of the union fix, but should not be the primary mechanism.

**Excluded:** The PLANNER_TEMPLATE `**Target Files:**`-inline alternative is excluded per SA contract constraints (non-load-bearing template edit, barred pending watcher-reliability items).

### Layer-1 Compliance

The union fix is **strictly Layer-1 mechanical**. It expands the text matching window (which step texts are searched for path/basename substrings) but does not:
- Interpret plan correctness
- Evaluate agent intent
- Read or analyze file contents
- Make qualitative judgments about output

No judgment shift between layers. The fix is the same character: text-in-text substring matching, applied to a wider text input.

---

## Section 3 — Preserve the Gate's Teeth

### Additive-Only Guarantee

The union fix is **purely additive**. It only moves files from out-of-scope to in-scope (a file mentioned in ANY step's text from 1..N is now authorized at step N). It **never** moves files from in-scope to out-of-scope. The negative case remains intact:

A file `some/random/unplanned_file.py` that appears in **no** step's text will still fail:
1. The `fpath in union_text or basename in union_text` check (gates.py:677) -- the path/basename is not a substring of any step's text
2. The directory-mention check (gates.py:688-696) -- no ancestor directory with trailing slash appears in any step's text
3. The allowlist checks (gates.py:673-676) -- the file is not in `SCOPE_ALLOWLIST` or `SCOPE_ALLOWLIST_PREFIXES`

The file is appended to `out_of_scope` and the gate fires.

### Exact Insertion Point

**gates.py:666.** The current single-step extraction is replaced with the union construction. All downstream matching logic (lines 671-697), allowlist checks (lines 673-676), and directory-mention authorization (lines 688-696) are **unchanged** -- they operate on the same text variable, which is now wider.

### Pattern Precedent

Mirrors the **directory-mention fix** (gates.py:679-696, shipped 2026-06-05, Done/executable-scope-check-dir-mention-2026-06-04.md). That fix added an additive `authorized_by_dir -> continue` clause -- a new authorization channel that only expanded the in-scope set. The union fix adds authorization through the existing matching logic by expanding the text haystack, following the same additive-clause pattern.

---

## Section 4 — Test Surface

### Positive Cases (union authorization)

1. **`test_scope_check_union_authorizes_earlier_step_file`**: 3-step plan. Step 1 mentions `knowledge/architecture/blueprint.md`. Step 3 (QA) does not mention it. Evaluate at `step_number=3` with `files_changed=["knowledge/architecture/blueprint.md"]`. Assert: no `scope_check` failure. Proves the union catches earlier-step files.

2. **`test_scope_check_union_authorizes_file_from_step_1_at_step_2`**: 2-step plan. Step 1 (DEV) mentions `gates.py`. Step 2 (QA) mentions only `tests/test_gates.py`. Evaluate at `step_number=2` with `files_changed=["gates.py", "tests/test_gates.py"]`. Assert: no `scope_check` failure. Proves cumulative authorization across steps.

### Negative Cases (teeth preserved)

3. **`test_scope_check_union_still_rejects_unmentioned_file`**: 3-step plan with specific file mentions in each step. A file `totally_unrelated.py` appears in NO step's text. Evaluate at `step_number=3` with `files_changed=["totally_unrelated.py"]`. Assert: `scope_check` failure with `totally_unrelated.py` in evidence. Proves the union does not blanket-authorize.

4. **`test_scope_check_union_does_not_blanket_authorize_across_dirs`**: 3-step plan mentioning files in `knowledge/` and `tests/`. A file `src/unrelated/other.py` is in `files_changed`. Assert: `scope_check` failure. Proves the union of specific step texts does not create directory-wide authorization beyond the existing directory-mention rules.

### Regression Guard

5. Existing `test_scope_check_passes_when_files_in_plan` and `test_scope_check_fails_when_file_not_in_plan` (test_gates.py:172, 178) continue to validate single-step behavior (union of one step = that step's text, no behavior change for step_number=1).

---

## Section 5 — Layer Impact + Executable Hand-Off

### Layer Impact

| Layer | Impact |
|---|---|
| Layer 1 (Bellows `gates.py`) | `_gate_scope_check` change: expand text matching window from single step to union of steps 1..N |
| Layer 2 (Agents) | No change |
| Layer 3 (Planner) | **Reduces** Rule 22(b) override burden -- continuous-run plans that previously required manual substance-check override for scope_check FPs will pass automatically |

No judgment shift between layers. Layer 1 remains mechanical text/path matching; Layer 3 retains all qualitative judgment.

### Files the Executable Will Touch

| File | Change |
|---|---|
| `gates.py` | Modify `_gate_scope_check` (lines 661-704): union construction + matching against `union_text` |
| `tests/test_gates.py` | Add 4 new tests: 2 positive (union authorization) + 2 negative (teeth) |

**No `bellows.py` change needed.** `gates.check()` already receives `plan_text` (full plan); no caller-side modification required.

### Daemon-Restart + Self-Fix Constraints

1. **Daemon restart required.** `gates.py` is imported at daemon startup (`bellows.py:128`). The fix takes effect only after restarting the Bellows daemon.

2. **Tight executable scope.** The implementing executable's DEV step must **explicitly enumerate** `gates.py` and `tests/test_gates.py` as target files in the step body text (not delegate to a blueprint). This ensures the pre-fix daemon's `_gate_scope_check` can find the filenames as substrings in the step text, avoiding the very false-positive this fix addresses.

### Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| Scope check matches against single step text | gates.py:666 `_extract_step_text(plan_text, step_number)` -- extracts only current step | Extract all steps 1..step_number, build union, match against union | Modify `_gate_scope_check` in gates.py |
| Prior-step files in cumulative diff flagged as out-of-scope | gates.py:677 `fpath in step_text` -- single step text haystack | `fpath in union_text` -- union of all step texts as haystack | Same change |
| Directory-mention check scoped to single step | gates.py:691 `(parent + "/") in step_text` -- single step | `(parent + "/") in union_text` -- union of all steps | Same change |
| Blueprint-delegated file list not followed | gates.py:677 pure text match, no file-read | Blueprint FILE authorized via union (Step 1 mentions it); blueprint CONTENTS still not followed | Partial fix; full blueprint-follow deferred (regex-fragility risk) |
| Evidence display shows current step context | gates.py:700 `step_text[:200]` | Unchanged -- retain current step text for diagnostic clarity | No change |

---

## Section 6 — Verification Blocks

### Rule 39 Verification

| # | Claim | Query | Expected Output |
|---|---|---|---|
| V1 | `_gate_scope_check` extracts only the current step's text for matching | `grep -n "_extract_step_text" gates.py` | Line 666 is the sole call in `_gate_scope_check`; confirms single-step extraction |
| V2 | Full step text is used for matching (not truncated) | Read gates.py:677 | `if fpath in step_text or basename in step_text` -- `step_text` is the full return of `_extract_step_text`, not `step_text[:200]` |
| V3 | `gates.check()` receives `plan_text` (full plan) | Read gates.py:187 | Function signature includes `plan_text` parameter; bellows.py passes it at lines 497 and 590 |
| V4 | No bellows.py caller-side change needed | `grep "gates.check" bellows.py` | `plan_text` is already passed to `gates.check(parsed, plan_text, current_step, ...)` at both call sites |
| V5 | `files_changed` computed as diff from pre-step HEAD to working tree | Read bellows.py:741-743 | `git diff --stat=300 --relative <pre_diff> -- .` -- diffs between pre-step SHA and current working tree |
| V6 | Directory-mention authorization checks against `step_text` (single step) | Read gates.py:691 | `if parent.count("/") >= 1 and (parent + "/") in step_text` -- same `step_text` variable from line 666 |

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a design diagnostic proving the root cause of both scope_check false-positive classes (continuous-run cumulative diff and blueprint delegation) and proposing a union-of-all-step-texts fix. The fix is purely additive (expands authorization, never narrows), requires no bellows.py caller change, and preserves the gate's negative-case teeth.

### Files Deposited
- `knowledge/architecture/scope-check-false-positive-fix-design-2026-06-09.md` -- design diagnostic with mechanism proof, fix design, test surface, gap assessment, and verification blocks

### Files Created or Modified (Code)
- None (design diagnostic only -- no source edits)

### Decisions Made
- Recommended union-of-all-step-texts as primary fix over per-step attribution and blueprint-follow alternatives
- Determined no bellows.py caller-side change is needed (gates.check already receives full plan_text)
- Scoped blueprint-contents-follow as a deferred future enhancement (regex-fragility risk)

### Flags for CEO
- Blueprint-delegation FP (#9) is only PARTIALLY addressed by the union fix: the blueprint document itself (its path) is authorized via Step 1's text, but the files LISTED INSIDE the blueprint remain unaddressed. Full resolution requires the blueprint-follow approach with its regex-fragility risk, deferred pending CEO disposition.

### Flags for Next Step
- The implementing executable MUST explicitly enumerate `gates.py` and `tests/test_gates.py` in the DEV step body (not delegate to a blueprint) to avoid tripping the pre-fix daemon's scope_check
- Daemon restart required after the fix lands
