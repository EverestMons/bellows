# Bellows — `_consume_verdicts` `processed-` prefix pre-scan rename
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-21 consume-verdicts drain failure diagnostic at `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md` (Planner-verified, plan in `Done/`), the discovery filter at `bellows.py:1128` —

```python
if not fname.startswith("verdict-") or not fname.endswith(".md"):
    continue
```

— silently drops files named `processed-verdict-*` because they don't start with literal `verdict-`. This is a real failure mode: when the Planner deposits a verdict file with `processed-` already in the filename (mistakenly copying the post-consumption naming convention), the consumer treats it as already-consumed and skips it. Two reproductions today; operational mitigation required Planner-side manual close + shadow cache cleanup + verdict file recall.

The diagnostic identified three resolution options. CEO selected **Option B (pre-scan rename, self-healing)** plus a governance-side companion fix (handled separately at session-wrap, not in this plan).

**Why Option B over Option A (strip in filter):**
- Self-healing: a wrongly-named file is renamed once to canonical form, then processed normally by the main loop
- No double-prefixing risk: the rename happens before the consumption-time rename at `bellows.py:1253`, so no `processed-processed-verdict-*` can occur
- Idempotent: re-running the pre-scan on canonical filenames is a no-op
- Lower risk of churn against existing tests (no change to the main filter logic)

**Why Option B over Option C (governance-only):**
- Today's reproductions proved the Planner can be wrong about Bellows write-time conventions from memory
- Code-level guard is robust against future Planner-authoring errors
- Combined with the governance fix (separate plan), this is belt-and-suspenders

---

## STEP 1 — Implement pre-scan rename + tests

**Agent:** Bellows Developer
**Estimated tokens:** ~30k

### Read order

1. `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md` — full findings. Pay particular attention to the Q5/Q6 traces and the Resolution Options Option B code sketch.
2. `bellows/bellows.py` — `_consume_verdicts` method in full. Confirm the line numbers cited in the diagnostic (1127-1131 enumeration, 1128 filter, 1133 regex, 1185 pairing, 1253 rename) before editing — the diagnostic's line citations are from this session's read and may have drifted.
3. `bellows/tests/test_consume_verdicts.py` — existing 5 tests. Read in full to understand the test fixture pattern (tempdir setup, file creation, assertion style).

### Implementation

At the top of `_consume_verdicts` body, before the existing `for fname in os.listdir(resolved_dir):` loop at bellows.py:1127, insert a pre-scan rename pass that detects `processed-verdict-*.md` files and renames them to canonical `verdict-*.md` form.

Exact insertion location: immediately before the existing `for fname in os.listdir(resolved_dir):` line, with no other modifications to the existing loop.

Code shape:

```python
# Pre-scan: normalize processed-verdict-* to verdict-* (Planner write-time naming mismatch).
# Files named processed-verdict-* at write time are structurally identical to already-consumed
# verdicts and would be silently skipped by the main filter. Rename to canonical form so the
# main loop can process them. See bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md.
for fname in os.listdir(resolved_dir):
    if fname.startswith("processed-verdict-") and fname.endswith(".md"):
        canonical = fname[len("processed-"):]
        canonical_path = os.path.join(resolved_dir, canonical)
        if os.path.exists(canonical_path):
            _log("WARN", f"cannot normalize {fname} — canonical {canonical} already exists; skipping rename")
            continue
        shutil.move(os.path.join(resolved_dir, fname), canonical_path)
        _log("WARN", f"normalized write-time processed- prefix: {fname} → {canonical}")
```

**Specific points:**
- The collision guard (`if os.path.exists(canonical_path)`) handles the edge case where both `verdict-foo-step-1.md` and `processed-verdict-foo-step-1.md` exist in `resolved/` simultaneously. This shouldn't happen in practice, but a WARN-and-skip beats a `shutil.move` that overwrites a legitimately-unconsumed file.
- Use `_log("WARN", ...)` not `print` — matches the post-2026-05-12 terminal capture convention.
- Use `os.path.join` not f-string path concatenation — the existing file uses `os.path.join` per inspection.

### Tests

Add 3 new tests to `bellows/tests/test_consume_verdicts.py`. Match the existing test pattern (tempdir + file creation + invoke `_consume_verdicts` + assert).

**Test 1 — `test_pre_scan_renames_processed_verdict_to_canonical`:**
- Set up a paused plan file at `decisions/verdict-pending-diagnostic-foo-2026-05-21.md`
- Create `resolved/processed-verdict-foo-2026-05-21-step-1.md` with `verdict: continue` content
- Invoke `_consume_verdicts`
- Assert: the file at `processed-verdict-foo-2026-05-21-step-1.md` no longer exists at that name
- Assert: the verdict was successfully consumed (plan moved out of `verdict-pending-`, or `processed-verdict-foo-2026-05-21-step-1.md` exists in `resolved/` as the consumption-time rename — confirm which by reading the existing tests' assertion style)

**Test 2 — `test_pre_scan_collision_guard_does_not_overwrite`:**
- Create `resolved/verdict-foo-2026-05-21-step-1.md` (canonical form)
- Create `resolved/processed-verdict-foo-2026-05-21-step-1.md` (write-time mistake form)
- Invoke `_consume_verdicts`
- Assert: the canonical file at `verdict-foo-2026-05-21-step-1.md` is preserved (not overwritten by the rename)
- Assert: a WARN log line was emitted for the collision
- The `processed-verdict-*` file may still be present (skipped) or renamed depending on which order things happen — assertion focus is on the canonical file's preservation

**Test 3 — `test_pre_scan_ignores_non_verdict_processed_files`:**
- Create `resolved/processed-something-unrelated.md` (not a verdict file)
- Invoke `_consume_verdicts`
- Assert: the file is not renamed (doesn't match `processed-verdict-` prefix)
- Assert: no rename WARN log emitted

### Test suite verification

After the edits, run the full bellows test suite from the bellows repo root:

```bash
cd /Users/marklehn/Developer/GitHub/bellows
python3 -m pytest 2>&1 | tail -50
```

Expected delta: +3 new tests passing, 0 regressions. Capture the tail output for the QA evidence directory.

### Out of scope

- Do not modify the main `for fname in os.listdir(resolved_dir):` loop or any code from bellows.py:1128 onward.
- Do not modify the consumption-time rename at bellows.py:1253.
- Do not modify `verdict.py` or `gates.py`.
- Do not touch PLANNER_TEMPLATE.md — governance fix is a separate session-wrap plan.
- Do not modify any production files in `bellows/verdicts/resolved/` — tests use tempdirs.

### Deliverables

**Deposits:**
- `bellows/bellows.py` — pre-scan rename block added before the existing enumeration loop
- `bellows/tests/test_consume_verdicts.py` — 3 new tests appended

### Commit

ONE commit at end of step:

```
fix(consume_verdicts): pre-scan rename processed-verdict-* to canonical verdict-*

Files written with processed- prefix at write time are structurally identical
to already-consumed verdicts and were silently skipped by the main filter at
bellows.py:1128. Pre-scan rename pass normalizes them to canonical form before
the main loop runs.

Refs: bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md
```

Do NOT push. Planner handles push at session-wrap.

---

## STEP 2 — QA verification

**Agent:** Bellows QA
**Estimated tokens:** ~25k

### Read order

1. `bellows/knowledge/decisions/in-progress-executable-consume-verdicts-prefix-fix-2026-05-21.md` (this plan) — verify deliverables match
2. `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md` — diagnostic findings
3. `bellows/bellows.py` `_consume_verdicts` — verify the pre-scan block is present, structurally correct, and placed before the main enumeration loop
4. `bellows/tests/test_consume_verdicts.py` — verify the 3 new tests are present and match the test descriptions in Step 1

### Verification checks

| # | Check | Method |
|---|---|---|
| 1 | Pre-scan block present in `_consume_verdicts` before main loop | Grep + visual inspection |
| 2 | Pre-scan block uses `_log("WARN", ...)` not `print` | Grep `_log` in the block |
| 3 | Collision guard (`os.path.exists(canonical_path)`) present | Visual inspection |
| 4 | Main filter at original line ~1128 unchanged | Diff against HEAD before edit |
| 5 | Consumption-time rename at original line ~1253 unchanged | Diff against HEAD before edit |
| 6 | Test 1 (`test_pre_scan_renames_processed_verdict_to_canonical`) present and passing | `pytest -v -k test_pre_scan_renames` |
| 7 | Test 2 (`test_pre_scan_collision_guard_does_not_overwrite`) present and passing | `pytest -v -k test_pre_scan_collision` |
| 8 | Test 3 (`test_pre_scan_ignores_non_verdict_processed_files`) present and passing | `pytest -v -k test_pre_scan_ignores` |
| 9 | Full bellows test suite passes with +3 delta, 0 regressions | `pytest 2>&1 \| tail -50` |
| 10 | Behavioral spot-check: write a `processed-verdict-*` file to a tempdir-equivalent and confirm the pre-scan renames it correctly | See behavioral spot-check below |

### Behavioral spot-check (check 10)

Run the following Python snippet (do NOT commit it; capture stdout to evidence):

```python
import os, tempfile, shutil, sys
sys.path.insert(0, "/Users/marklehn/Developer/GitHub/bellows")

# Set up a minimal Bellows env to invoke _consume_verdicts
# (Use the same setup pattern as existing tests in test_consume_verdicts.py)

# Create a temp resolved/ dir
tmpdir = tempfile.mkdtemp()
resolved_dir = os.path.join(tmpdir, "resolved")
os.makedirs(resolved_dir)

# Create a processed-verdict-* file
bad_name = "processed-verdict-spotcheck-2026-05-21-step-1.md"
with open(os.path.join(resolved_dir, bad_name), "w") as f:
    f.write("verdict: continue\nspotcheck\n")

# Confirm it exists
assert os.path.exists(os.path.join(resolved_dir, bad_name)), "setup failed"
print(f"BEFORE: {os.listdir(resolved_dir)}")

# Manually invoke the pre-scan logic (lifted from bellows.py for spot-check isolation)
for fname in os.listdir(resolved_dir):
    if fname.startswith("processed-verdict-") and fname.endswith(".md"):
        canonical = fname[len("processed-"):]
        canonical_path = os.path.join(resolved_dir, canonical)
        if os.path.exists(canonical_path):
            print(f"WARN: cannot normalize {fname}")
            continue
        shutil.move(os.path.join(resolved_dir, fname), canonical_path)
        print(f"NORMALIZED: {fname} → {canonical}")

# Confirm rename
print(f"AFTER: {os.listdir(resolved_dir)}")
assert os.path.exists(os.path.join(resolved_dir, "verdict-spotcheck-2026-05-21-step-1.md")), "rename failed"
assert not os.path.exists(os.path.join(resolved_dir, bad_name)), "old file still present"
print("SPOTCHECK PASSED")

shutil.rmtree(tmpdir)
```

The spot-check isolates the pre-scan logic from the full `_consume_verdicts` flow to confirm the rename behavior is correct. The integration is covered by the unit tests.

### QA report format

Deposit at `bellows/knowledge/qa/consume-verdicts-prefix-fix-qa-2026-05-21.md` with:
- Status table: each verification check 1-10 with ✅/❌ and one-line evidence
- Pytest tail outputs (full suite + targeted test runs) inline
- Behavioral spot-check stdout verbatim
- Final verdict line: ALL CHECKS PASSED or LIST OF FAILURES

### Rule 20 self-check

End the QA report with the canonical Rule 20 self-check Python block per the reference at `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. **USE THE VERBATIM TEMPLATE** — paste the block from the canonical file with only variable substitutions.

ACTUALLY EXECUTE THE BLOCK after writing the QA report (use python3 to run it as a script or inline) and include the literal stdout in the QA report. Do NOT just include the script.

Variable substitutions:
- `plan_slug` = `executable-consume-verdicts-prefix-fix-2026-05-21`
- `qa_report_path` = `bellows/knowledge/qa/consume-verdicts-prefix-fix-qa-2026-05-21.md`
- `evidence_dir` = `bellows/knowledge/qa/evidence/consume-verdicts-prefix-fix-2026-05-21/`
- `required_evidence_files` = `["pytest_full.txt", "pytest_targeted.txt", "spotcheck_stdout.txt"]`

### Deliverables

**Deposits:**
- `bellows/knowledge/qa/consume-verdicts-prefix-fix-qa-2026-05-21.md`
- `bellows/knowledge/qa/evidence/consume-verdicts-prefix-fix-2026-05-21/`

### Commit

ONE commit at end of step:

```
docs(qa): consume-verdicts processed- prefix fix verification

Refs: bellows/knowledge/decisions/Done/executable-consume-verdicts-prefix-fix-2026-05-21.md
```

Do NOT push. Planner handles push at session-wrap.

### STOP

Stop after Step 2. Pause for CEO verdict.
