# Dev Log — S3 Bug C: stale-verdict check recognizes halted-* plans

**Date:** 2026-05-10
**Plan:** executable-s3-bug-c-halted-stale-check-2026-05-10
**Step:** 1

## Diff Applied to bellows.py

Post-edit line range: **1033–1058** (was 1033–1051).

Added 6 lines inside the `else` branch of the `if plan_matched:` check in `_consume_verdicts()`. The new code scans `decisions_path` for filenames starting with `halted-` and containing `plan_slug`, mirroring the existing Done/ search logic:

```python
                    # Also check decisions/ itself for halted-* plans (S3 Bug C fix)
                    if os.path.isdir(decisions_path):
                        for dname in os.listdir(decisions_path):
                            if dname.startswith("halted-") and plan_slug in dname:
                                stale = True
                                break
                    if stale:
                        break
```

The `if stale:` print message updated from:
```
plan already in Done/, moving to processed
```
to:
```
plan in Done/ or halted-, moving to processed
```

Comment on the `else` branch updated from:
```
# No match — check if plan is already in Done/ (stale verdict)
```
to:
```
# No match — check if plan is already in Done/ OR halted in decisions/ (stale verdict)
```

## New Test Added to tests/test_consume_verdicts.py

`test_consume_verdicts_marks_resolved_processed_when_plan_halted` — sets up:
- A temp watched_projects directory with `decisions/` and `decisions/Done/`
- A `halted-executable-foo-2026-05-09.md` file in `decisions_path` (NOT in Done/)
- A `verdict-executable-foo-2026-05-09-step-2.md` file in `verdicts/resolved/` (with `verdict: stop` content)
- An empty `verdicts/pending/` (no pending request file)

Asserts:
- Verdict file renamed to `processed-verdict-executable-foo-2026-05-09-step-2.md`
- Original verdict file no longer in `resolved/`
- Halted plan file unchanged

## Pytest Output — test_consume_verdicts.py

```
tests/test_consume_verdicts.py::test_cleanup_normalizes_prefixed_verdict_slug PASSED [ 16%]
tests/test_consume_verdicts.py::test_cleanup_unprefixed_verdict_slug PASSED [ 33%]
tests/test_consume_verdicts.py::test_consume_verdicts_skips_verdict_request_files PASSED [ 50%]
tests/test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows PASSED [ 66%]
tests/test_consume_verdicts.py::test_consume_verdicts_marks_resolved_processed_when_plan_halted PASSED [ 83%]
tests/test_consume_verdicts.py::test_startup_sweep_removes_done_plan_orphans PASSED [100%]

6 passed, 1 warning in 0.16s
```

## Pytest Output — Full Suite

```
1 failed, 246 passed, 1 warning in 6.98s

FAILED tests/test_runner_parser.py::test_run_step_timeout - assert False is True
```

Pre-existing `test_run_step_timeout` failure unchanged. +1 new test (245 → 246 passed).

## Confirmations

- **Post-edit line numbers:** stale-check block at bellows.py:1033–1058
- **No other functions in bellows.py touched** — only the `else` branch in `_consume_verdicts()` was modified
- **No other test files touched** — only `tests/test_consume_verdicts.py` received the new test

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extended the stale-verdict check in `_consume_verdicts()` to recognize `halted-*` prefixed plans in `knowledge/decisions/`, preventing the retry-loop log noise for resolved verdicts referencing halted plans. Added one regression test.

### Files Deposited
- `bellows/knowledge/development/s3-bug-c-halted-stale-check-dev-log-2026-05-10.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — +6 lines in `_consume_verdicts()` stale-check, +1 comment update, +1 print message update
- `bellows/tests/test_consume_verdicts.py` — +1 new test (`test_consume_verdicts_marks_resolved_processed_when_plan_halted`)

### Decisions Made
- Placed halted-* check after Done/ check within the same `for decisions_path` loop (mirrors plan structure)

### Flags for CEO
- None

### Flags for Next Step
- QA should verify the halted-* detection path end-to-end via behavioral spot-check
