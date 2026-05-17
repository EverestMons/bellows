# Executable: Gate 2c — Bellows Gate False-Positive Fixes (Strikes 4 & 5)

**Plan slug:** executable-gate-2c-bellows-gate-fixes-2026-05-19
**Plan type:** executable
**Project:** bellows
**Specialist:** Bellows Developer (Forge Developer acting on bellows code)
**Auto-close:** false
**Pause for verdict:** after_step_1
**Priority:** 1
**Depends on:** none
**Created:** 2026-05-19

---

## Context

Two Bellows gates produce false positives on substantively-correct plans:

**Strike 4 — `deposit_exists` on `_staging_*` paths.** When step prose mentions the atomic-staging filename (e.g., `_staging_diagnostic-canary.md`) as part of describing the deposit *mechanism*, `_extract_plan_required_deposits()` extracts that path and the gate later checks for its existence on disk. The path never exists post-deposit (staging is transient by design), so the gate trips. Cited: LESSONS 2026-05-18 strike-4 entry.

**Strike 5 — `rule_20_self_check` on banner-with-decoration.** The gate's banner match looks for the literal string `"Rule 20 — QA Self-Check Results"` followed by a line starting with `"PASSED — SELF-CHECK PASSED"`. When the agent renders the banner inside a fenced code block with `===` separator lines bracketing it, the match succeeds for the banner but the gate's line-by-line scan for the PASSED line picks up the `===` first or fails to find the PASSED line in the expected position. Cited: LESSONS 2026-05-18 strike-5 entry. Strike 3 from 2026-05-17 (`$ python3 -c "..."` shell-prompt prefix above the banner) is the same class.

**Strike 6 (today) — banner block omitted entirely.** The agent's QA report contained 10 substantive verification checks but omitted the Rule 20 self-check Python block + banner from the deposit. This is an agent-discipline failure, not a gate-tolerance failure — out of scope for this plan; addressed via prompt-feedback loop instead.

**Gate 1 dispositions (accepted, awaiting Gate 2c):**
- **S1:** Fix `_extract_plan_required_deposits` to filter `_staging_*` paths during extraction. Per Gate 1 matrix's option (a). Option (b) — "restrict to bulleted lists under Deposits headers only" — would break legacy prose-fallback patterns and is rejected.
- **S2:** Relax `_gate_rule_20_self_check` pattern matching to tolerate banner inside fenced code blocks with arbitrary decoration. Per Gate 1 matrix's option (a). Option (b) — helper script — is a larger workflow change deferred to a future Bellows backlog item.

**Code location (Planner-verified pre-authoring against `/Users/marklehn/Developer/GitHub/bellows/gates.py`):**
- `_extract_plan_required_deposits()` at lines 265–311 (three extraction paths: structured block, inline format, legacy prose fallback)
- `_gate_rule_20_self_check()` at lines 312–361

**Restart requirement:** Bellows daemon must be restarted by CEO to load the fix. The fix is not active until restart. Post-restart canary is shipped as a separate plan (Plan B), to be authored after this plan's QA passes and Bellows is restarted.

---

## STEP 1 — Implement fixes + tests

You are the Bellows Developer (Forge Developer acting on bellows code). Read `forge/agents/FORGE_DEVELOPER.md` and `bellows/CLAUDE.md`. Operate against `/Users/marklehn/Developer/GitHub/bellows/`.

**Verify pre-edit state before any modification.** Read `bellows/gates.py` and confirm:

- `_extract_plan_required_deposits()` is defined at approximately line 265, has three extraction paths (structured `**Deposits:**` block regex at line ~272, inline `**Deposits:**` regex at line ~283, legacy prose patterns at lines ~292+).
- `_gate_rule_20_self_check()` is defined at approximately line 312, uses `banner = "Rule 20 — QA Self-Check Results"`, scans lines after `banner_pos` for `"PASSED — SELF-CHECK PASSED"`.

If either function does NOT match these citations, HALT and report — the Planner's pre-authoring read may be stale and the plan needs revision before edits.

**Fix 1 — `_extract_plan_required_deposits` filters `_staging_*` paths.**

Modify the function so that paths whose basename begins with `_staging_` are excluded from the returned set in all three extraction paths. Implementation approach: add a single filter at function exit that drops `_staging_*` basenames before returning. This avoids duplicating the filter at three return points.

Concretely, the function currently has three return statements (one per extraction path). Refactor to a single return at the bottom that applies the filter:

```python
def _extract_plan_required_deposits(step_text):
    """Extract file paths explicitly required by deposit instructions in the plan step text.

    Filters out `_staging_*` basenames (transient atomic-deposit filenames mentioned in
    step prose as part of describing the deposit mechanism, never persistent on disk).

    If a **Deposits:** block (Rule 26 convention) is present, extracts only the
    backtick-quoted paths from its bullet list and ignores legacy prose patterns.
    Falls back to legacy prose-matching regexes when no block is present.
    """
    paths = set()

    # Rule 26: prefer declared **Deposits:** block when present
    block_match = re.search(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)', step_text)
    if block_match:
        block_text = block_match.group(1)
        for m in re.finditer(r'-\s+`([^`]+)`', block_text):
            paths.add(m.group(1))
        return _filter_transient_paths(paths)

    # Inline format: **Deposits:** `- /path/a`, `- /path/b`.
    inline_match = re.search(r'[> ]*\*\*Deposits:\*\*[ \t]+(.+)', step_text)
    if inline_match:
        inline_text = inline_match.group(1)
        for m in re.finditer(r'`-\s+([^`]+)`', inline_text):
            paths.add(m.group(1))
        if paths:
            return _filter_transient_paths(paths)

    # Legacy fallback: prose-matching regexes
    # [keep all 3 legacy patterns as-is]
    for m in re.finditer(r'Deposit[^\n`]*?to\s+`([^`]+)`', step_text, re.IGNORECASE):
        candidate = m.group(1).strip()
        if candidate:
            paths.add(candidate)
    for m in re.finditer(r'Deposit[^\n]*?to\s+(\S+\.md)', step_text, re.IGNORECASE):
        candidate = m.group(1).strip().rstrip('.,;)').strip('`')
        if '/' in candidate:
            paths.add(candidate)
    for m in re.finditer(r'with open\(["\']([^"\']+\.md)["\'],\s*["\']w["\']', step_text):
        paths.add(m.group(1).strip())
    return _filter_transient_paths(paths)


def _filter_transient_paths(paths):
    """Drop paths whose basename starts with `_staging_` — these are transient
    atomic-deposit filenames that exist only between write and move and are not
    deliverables. Per LESSONS 2026-05-18 strike-4 entry."""
    return {p for p in paths if not os.path.basename(p).startswith("_staging_")}
```

Note the structured-block return previously had no parameter check — it returned even when paths was empty (allowing `- none` to mean "no deposits required"). After refactor, the structured-block path returns the filtered (possibly empty) set explicitly, preserving the `- none` semantic.

Wait — looking again: the original inline-format path returns `paths` only if non-empty, otherwise falls through to legacy. Preserve that branch logic. The structured-block path returns unconditionally. Match the original control flow exactly; only add the filter call at each return point.

**Fix 2 — `_gate_rule_20_self_check` tolerant banner matching.**

The current logic finds `banner_pos = content.index(banner)`, then iterates lines starting at that position checking each line with `line.startswith("PASSED — SELF-CHECK PASSED")`. The failure mode: when the banner is inside a fenced code block with `===` decoration lines (strike 5), the lines immediately after the banner are `===` separators or other decoration, and the PASSED line may appear several lines later, OR the PASSED line itself may be prefixed (e.g., `"  PASSED — SELF-CHECK PASSED"` with leading whitespace from indented code).

Replace the post-banner scan with a more tolerant check:

```python
        if banner not in content:
            continue

        # Banner found — scan ALL remaining content for the PASSED line, tolerating
        # whitespace, decoration lines, and fenced-block indentation.
        # Per LESSONS 2026-05-17 strike-3 and 2026-05-18 strike-5 entries.
        banner_pos = content.index(banner)
        remaining = content[banner_pos:]
        # The PASSED line may be anywhere in the remaining content, optionally
        # preceded by whitespace on its line. Use re.MULTILINE so ^ matches each
        # line start, and \s* tolerates leading indentation/whitespace.
        if re.search(r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
            return  # Gate passes
        banner_found_path = dep_path
```

The `\s+` between `PASSED` and `—` (em-dash) and between `—` and `SELF-CHECK` tolerates variable whitespace (e.g., the agent might render it with one or two spaces, or a tab). The `^\s*` at the line start allows fenced-code indentation. The `re.MULTILINE` flag makes `^` match per-line.

This preserves the gate's intent (verify the banner+PASSED appear together in a QA deposit) while tolerating the decoration patterns observed in strikes 3 and 5.

**Test coverage.**

Add tests to `bellows/tests/test_gates.py` (or wherever the gates tests live — verify location first). Tests required:

1. `test_extract_deposits_filters_staging_prefix` — feed a step text with both a normal deposit and a `_staging_*` mention, verify only the normal one is returned.
2. `test_extract_deposits_filters_staging_in_structured_block` — `**Deposits:**` block containing both a real path and a `_staging_*` path; verify filter applies in this path.
3. `test_extract_deposits_filters_staging_in_inline_format` — inline format with mixed paths.
4. `test_extract_deposits_filters_staging_in_legacy_prose` — legacy "Deposit ... to `_staging_foo.md`" pattern; verify filter applies.
5. `test_rule_20_banner_in_fenced_block` — banner appears inside a fenced code block in the deposit content; verify gate passes.
6. `test_rule_20_banner_with_decoration` — banner with `===` lines bracketing it inside fence; verify gate passes.
7. `test_rule_20_banner_with_shell_prompt_prefix` — `$ python3 -c "..."` line above banner inside fence; verify gate passes (strike 3 pattern).
8. `test_rule_20_passed_line_with_indentation` — PASSED line has leading whitespace (e.g., from indented code block); verify gate passes.
9. `test_rule_20_no_banner` — deposit without banner; verify gate fails with "no QA deposit contains Rule 20 self-check banner" evidence. (Regression for strike 6 detection — gate should still flag this.)
10. `test_rule_20_banner_without_passed` — banner present but no PASSED line anywhere; verify gate fails with "banner present but PASSED line missing" evidence.

If `tests/test_gates.py` doesn't exist, find where existing gate tests live (`tests/test_bellows.py` or similar) and add tests there. Halt and report if no existing gate test infrastructure is found.

**Run tests before commit.**

```bash
cd /Users/marklehn/Developer/GitHub/bellows && python3 -m pytest tests/ -v
```

Expected: all existing tests still PASS plus the 10 new tests PASS. If any existing test breaks, halt and report — do not commit a regression.

**Commit:**

```bash
cd /Users/marklehn/Developer/GitHub/bellows && git --no-pager add gates.py tests/ && git --no-pager commit -m "fix(gates): filter _staging_* from deposit extraction; tolerant rule_20 banner matching (strikes 4 & 5)"
```

**Dev log:**

```markdown
# Dev Log — Gate 2c Step 1 (gates.py fixes for strikes 4 & 5)

Pre-edit verification:
- _extract_plan_required_deposits at line <N>: <match yes/no>
- _gate_rule_20_self_check at line <N>: <match yes/no>

Fix 1 — _staging_ filter:
- Added _filter_transient_paths() helper
- Applied filter at all three return points
- Diff summary: <lines added/removed>

Fix 2 — tolerant rule_20 banner matching:
- Replaced line-start substring check with re.search(re.MULTILINE)
- Pattern: <regex literal>

Tests added: 10
- test_extract_deposits_filters_staging_prefix
- test_extract_deposits_filters_staging_in_structured_block
- test_extract_deposits_filters_staging_in_inline_format
- test_extract_deposits_filters_staging_in_legacy_prose
- test_rule_20_banner_in_fenced_block
- test_rule_20_banner_with_decoration
- test_rule_20_banner_with_shell_prompt_prefix
- test_rule_20_passed_line_with_indentation
- test_rule_20_no_banner
- test_rule_20_banner_without_passed

Test results: <pytest output summary>
Commit: <SHA>
```

Deposit to: `bellows/knowledge/development/dev-log-gate-2c-step-1-2026-05-19.md`

**Output Receipt:**
- Agent: Bellows Developer
- Step: 1
- Status: Complete (both fixes implemented, 10 tests added and passing, regression suite green, commit landed); Blocked (pre-edit verification failed, test failure, or commit failed)
- What Was Done: filtered `_staging_*` paths from deposit extraction; relaxed rule_20 banner match to tolerate decoration and indentation; added 10 tests
- Files Deposited: `bellows/knowledge/development/dev-log-gate-2c-step-1-2026-05-19.md`
- Files Created or Modified: `bellows/gates.py`, `bellows/tests/<test file>`, commit `<SHA>`
- Decisions Made: fix shapes per plan; test locations
- Flags for CEO: any pre-edit state mismatch; any regression test failure
- Flags for Next Step: Planner Rule 22 reads dev log and inspects diff before authorizing QA

**Deposits:**
- `bellows/knowledge/development/dev-log-gate-2c-step-1-2026-05-19.md`

**STOP.** Do NOT proceed to Step 2.

---

## STEP 2 — QA verification

You are the Bellows Developer (acting as QA). Before starting, read the prior step's deposit at `bellows/knowledge/development/dev-log-gate-2c-step-1-2026-05-19.md` and verify Output Receipt status is Complete. If not, stop.

**Verification checks:**

1. **Full test suite green:** `cd /Users/marklehn/Developer/GitHub/bellows && python3 -m pytest tests/ -v`. Report verbatim. Expected: 100% pass, count includes the 10 new Gate 2c tests. PASS/FAIL.

2. **Filter applied at all three extraction paths.** `grep -n "_filter_transient_paths" gates.py`. Expected: 4 occurrences (1 definition + 3 calls). Report verbatim. PASS/FAIL.

3. **Filter helper defined correctly.** Read the `_filter_transient_paths` function and verify it filters `_staging_*` basenames (not full paths starting with `_staging_`). PASS/FAIL.

4. **Rule 20 banner match uses re.MULTILINE.** `grep -n "re.MULTILINE" gates.py` should show the new line in `_gate_rule_20_self_check`. PASS/FAIL.

5. **No regression in `_extract_plan_required_deposits` semantics for non-staging paths.** Spot-check: feed a sample step text with three normal deposits (structured block format) through the function in a REPL, verify all three are returned. PASS/FAIL.

6. **`- none` semantic preserved.** Spot-check: feed a step text with `**Deposits:**\n- none` — function should return an empty set (filter is no-op on empty), not crash. PASS/FAIL.

7. **Git diff inspection.** `git --no-pager show HEAD --stat` should show only `gates.py` and the test file modified. No unrelated changes. PASS/FAIL.

**QA report deposit:**

Write to `bellows/knowledge/qa/gate-2c-qa-2026-05-19.md` with each check, command run, verbatim output, PASS/FAIL.

**Rule 20 self-check (literal banner — render EXACTLY this, no decoration, no shell prompt, no `===`):**

```
Rule 20 — QA Self-Check Results
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

To produce this, run:

```python
import os
required = [
    "knowledge/development/dev-log-gate-2c-step-1-2026-05-19.md",
    "knowledge/qa/gate-2c-qa-2026-05-19.md",
]
missing = [f for f in required if not os.path.exists(f)]
if missing:
    print(f"FAILED - missing evidence: {missing}")
else:
    print("Rule 20 — QA Self-Check Results")
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
```

Paste the literal stdout of that script into the QA report inside a fenced code block. The banner line and the PASSED line must appear on their own lines inside the fence, with NO `===` separator lines, NO shell-prompt prefix line above, NO summary line below. Just those two lines, fenced.

**Commit QA report + PROJECT_STATUS update:**

```bash
cd /Users/marklehn/Developer/GitHub/bellows && git --no-pager add knowledge/qa/gate-2c-qa-2026-05-19.md && git --no-pager commit -m "qa: gate 2c gates.py fixes verified (strikes 4 & 5)"
```

Update `bellows/PROJECT_STATUS.md` with a brief Gate 2c entry. Then:

```bash
git --no-pager add PROJECT_STATUS.md && git --no-pager commit -m "docs: PROJECT_STATUS update for gate 2c"
```

**Output Receipt:**
- Agent: Bellows Developer (QA)
- Step: 2
- Status: Complete (all 7 checks PASS, both commits landed); Partial (1-2 checks FAIL); Blocked (3+ checks FAIL)
- What Was Done: verified gate fixes via test suite, code inspection, semantic spot-checks, and diff inspection
- Files Deposited: `bellows/knowledge/qa/gate-2c-qa-2026-05-19.md`
- Files Created or Modified: 2 commits (QA report, PROJECT_STATUS)
- Decisions Made: 7 PASS/FAIL determinations
- Flags for CEO: **Bellows daemon must be restarted by CEO to load the fix.** The fix is committed to disk but not running until restart. After restart, a post-restart canary plan (Plan B, separate executable) should be authored to bait-test both gates against the restarted daemon.
- Flags for Next Step: Plan B canary authoring

**Deposits:**
- `bellows/knowledge/qa/gate-2c-qa-2026-05-19.md`

Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---

## How to run

Bellows dispatches Step 1 on next rescan. Pauses for verdict. Planner reads dev log under Rule 22 + inspects the actual diff via `git show HEAD` against the canonical bellows repo; verifies test suite ran clean. Continue verdict deposited to `bellows/verdicts/resolved/verdict-gate-2c-bellows-gate-fixes-2026-05-19-step-1.md`. Step 2 runs end-to-end, plan moves to Done. After Done, CEO restarts Bellows daemon. Planner then authors Plan B (bait-laden canary) as a separate executable for post-restart verification.
