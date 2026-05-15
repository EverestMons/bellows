# Executable — S3 Verdict-Resolved Retry Loop Fix

**Created:** 2026-05-09
**Author:** Planner
**Project:** bellows
**Type:** executable
**auto_close:** false
**Total Steps:** 2

---

## Execution Map

Step 1 (DEV) → Step 2 (QA)

Sequential. QA depends on DEV's code + tests landing on main.

---

## Context

Per `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md`, the S3 retry loop has two distinct root causes:

- **Bug A — Format intolerance in `check_verdict()`** (`verdict.py:157`): regex `r"^verdict:\s*(continue|stop)$"` rejects bare `continue`/`stop` first lines. 14 stranded files affected. Failed files are silently skipped at `bellows.py:922` with no log line — the architecturally-correct stale-verdict Done/ check at `bellows.py:1004-1021` is unreachable.
- **Bug B — Missing `verdict-request-` prefix exclusion** (`bellows.py:881`): file-listing filter `fname.startswith("verdict-")` admits `verdict-request-*` files into the verdict-consumption pipeline, producing corrupted slugs and active retry-loop log noise. 2 stranded files affected.

Both bugs are Layer 1 mechanical concerns (pattern matching, prefix filtering). Fix is ~5 LOC + tests.

**Cleanup strategy:** Fix (a) self-heals the 14 bare-format files on next Bellows scan after restart — the stale-verdict Done/ check renames them to `processed-`. Fix (b) prevents future request-shaped pollution. The 2 existing `verdict-request-*` files in `resolved/` will be `rm`ed by the CEO after the fix ships (one-time manual action; not in plan scope to avoid encoding judgment in Bellows).

## STEP 1 — Bellows Developer: implement format tolerance and prefix exclusion

You are the Bellows Developer. Implement two surgical fixes to `_consume_verdicts()` and `check_verdict()`. Do NOT change behavior beyond what is specified.

**Read first (required):**
- `bellows/agents/BELLOWS_DEVELOPER.md` — your role
- `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md` — diagnostic findings (the source of truth for this fix)
- `bellows/knowledge/research/agent-prompt-feedback.md` — last ~30 entries

**Read for context (skim):**
- `bellows/verdict.py` lines 140-170 (the `check_verdict` function)
- `bellows/bellows.py` lines 870-1025 (the `_consume_verdicts` function and stale-check)
- `bellows/verdicts/README.md` — verdict file format spec

### Fix A — Format tolerance in `check_verdict`

**File:** `bellows/verdict.py`
**Line:** ~157 (locate via grep for `r"^verdict:\s*(continue|stop)$"`)

**Change:** Modify the first-line regex to accept BOTH the spec-compliant `verdict: continue` form AND the legacy bare `continue` form. The new regex must accept:

- `verdict: continue` (spec-compliant)
- `verdict:continue` (no space — already accepted by `\s*`)
- `continue` (bare, lowercase)
- `stop` (bare, lowercase)
- `Verdict: Continue` (case-insensitive — already accepted by `re.IGNORECASE`)

**Recommended regex:** `r"^(?:verdict:\s*)?(continue|stop)$"` with `re.IGNORECASE` flag preserved.

**Constraint:** Do NOT change the function's return shape or any other code path in `check_verdict`. Only the first-line regex changes.

### Fix B — Prefix exclusion in file listing

**File:** `bellows/bellows.py`
**Line:** ~881 (locate via grep for `if not fname.startswith("verdict-")`)

**Change:** Extend the skip condition to also exclude files starting with `verdict-request-`. These are request-shaped files that should never appear in `resolved/`; if they do, Bellows must skip them rather than parse them as verdict responses with corrupted slugs.

**Recommended approach:**
```python
if not fname.startswith("verdict-") or not fname.endswith(".md"):
    continue
if fname.startswith("verdict-request-"):
    continue
```

**Constraint:** Do NOT auto-archive, auto-rename, or auto-delete `verdict-request-*` files. Skip them silently — but this is acceptable because their presence is rare (Planner-side naming errors) and the CEO can `rm` them manually. Bellows must not encode judgment about Planner-deposited files.

### Tests — write all five

Add to existing test files (use `grep -r "check_verdict\|_consume_verdicts" tests/` to find the right test files; if no obvious file exists, create `tests/test_verdict_consume_s3_fix.py`).

**Test 1 — `check_verdict` accepts bare `continue`:**
Create a temp file with first line `continue\nReason text.`, call `check_verdict`, assert `result["found"] == True` and `result["verdict"] == "continue"`.

**Test 2 — `check_verdict` accepts bare `stop`:**
Create a temp file with first line `stop\nReason text.`, call `check_verdict`, assert `result["found"] == True` and `result["verdict"] == "stop"`.

**Test 3 — `check_verdict` still accepts `verdict: continue` (regression):**
Create a temp file with first line `verdict: continue\nReason text.`, call `check_verdict`, assert `result["found"] == True` and `result["verdict"] == "continue"`.

**Test 4 — `check_verdict` rejects garbage:**
Create a temp file with first line `random text\nMore text.`, call `check_verdict`, assert `result["found"] == False`.

**Test 5 — `_consume_verdicts` skips `verdict-request-` files:**
In a temp directory simulating `verdicts/resolved/`, drop a file named `verdict-request-foo-step-1.md` with valid `verdict: continue` content. Run `_consume_verdicts` (or equivalent unit-testable subset) against the temp directory. Assert the file is NOT renamed to `processed-` and NOT moved. The file remains in place, no exception raised.

If `_consume_verdicts` is not directly unit-testable due to coupling with global state, use a smaller-scope test: assert that the file-listing filter at the top of the function would skip a `verdict-request-foo-step-1.md` filename.

### Quality requirements

- All five new tests pass
- Existing test suite passes (run `pytest tests/` and report counts: before / after)
- No changes to any file outside `bellows/verdict.py`, `bellows/bellows.py`, and the test file
- Commit message: `fix(s3): format-tolerant check_verdict + verdict-request- prefix exclusion`

### Output Receipt

- Status: Complete / Partial / Blocked
- Files modified (cite each by path and line range)
- Test counts: before fix / after fix (full suite + new tests)
- Commit SHA on main
- CEO Flags: any deviation from the spec above, any test that needed scope adjustment, any regression encountered

**Append agent-prompt-feedback** entry covering: clarity of fix specification, whether the regex/prefix recommendations were directly implementable or needed adaptation, whether test scope was right-sized.

**Deposits:**
- `bellows/verdict.py`
- `bellows/bellows.py`
- (test file — declare exact path in Output Receipt)
- `bellows/knowledge/research/agent-prompt-feedback.md`

---

## STEP 2 — Bellows QA: regression suite + live canary

You are the Bellows QA. Verify the Step 1 fix.

**Read first (required):**
- `bellows/agents/BELLOWS_QA.md` — your role
- The Step 1 Output Receipt (above) and the dev log if deposited
- `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md` — original diagnostic

### QA Task A — Deliverable verification (Rule 17)

For each item declared in Step 1's Output Receipt:
- Verify the file exists and the cited lines contain the expected change (read the file, quote the relevant lines).
- Verify the test file exists and contains all five tests by name.

Produce a Markdown verification table: deliverable / expected / observed / pass-fail.

### QA Task B — Test execution

Run the full Bellows test suite from the project root:
```
pytest tests/ -v 2>&1 | tail -50
```

Report:
- Total tests run, passed, failed, skipped
- Compare to pre-fix baseline cited in Step 1 Output Receipt
- If any failures are unrelated to this fix, list them and confirm they are pre-existing (cross-reference against `bellows/knowledge/qa/` baselines if available)

### QA Task C — Live canary on stranded files

After confirming Tasks A and B pass, request the CEO to restart Bellows (Bellows does not hot-reload). Once restarted, observe for ~2 minutes and verify:

1. The 14 bare-format `verdict-*-step-*.md` files in `bellows/verdicts/resolved/` get auto-processed: each is renamed to `processed-verdict-*` after the stale-verdict Done/ check matches their slug against bellows/forge/IP Done/ directories.
2. The 2 `verdict-request-*` files in `bellows/verdicts/resolved/` are now silently skipped — the retry-loop log line `⚠️  no verdict-pending plan found for request-pipe-header-parser-...` should STOP appearing.

**Evidence required:**
- `ls bellows/verdicts/resolved/ | grep -c '^verdict-'` — should drop from 16 to 2 (only the request-shaped files remain).
- `ls bellows/verdicts/resolved/ | grep -c '^processed-verdict-'` — should increase by 14 (from 168 to 182).
- Log tail showing absence of S3 retry-loop warnings for ~2 minutes.

If CEO restart has not happened by the time of this step, mark the canary as "Pending CEO restart" and complete the rest of QA. Do NOT block the QA report on the restart — note it as a CEO action.

### QA Task D — Rule 20 self-check

Generate a Python self-check that verifies the QA report is internally consistent. The block should:
1. Read the deposited QA report file via `os.path.isfile()` to confirm it exists at the declared path.
2. Parse the verification table (Task A) and confirm every row has a positive status indicator (one of: `✅`, `OK`, `PASS`, `[x]`, `done`, `complete`, `verified`).
3. Confirm Task B reports a pass count and that no new failures were introduced (if pre-fix baseline was N passing, post-fix must be ≥ N).
4. Confirm Task C reports either "canary passed" with the three evidence items OR "Pending CEO restart" — anything else is an inconsistency.

Embed the self-check Python block at the end of the QA report under a `## Rule 20 Self-Check` heading. Run it once and paste the output below the block. If the self-check fails, fix the QA report before completing.

### QA Output Receipt

- Status: Complete / Partial / Blocked
- Test counts: before / after
- Canary status: passed / pending CEO restart / failed
- Files modified during QA: only the QA report and feedback log
- CEO Flags: anything ambiguous, any test that should have been added but wasn't, any concern about the fix's completeness

**Append agent-prompt-feedback** entry.

**Update PROJECT_STATUS.md** with the S3 closure milestone (one anchored line under Completed Milestones, dated 2026-05-09).

**Deposits:**
- `bellows/knowledge/qa/s3-verdict-fix-qa-2026-05-09.md`
- `bellows/PROJECT_STATUS.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`

---

## Bootstrap prompt for CEO

```
RUN EXE bellows
```
