# Ledger Extraction Fix (Multi-Turn) + in_progress-Strand Recovery — Dev Log

**Date:** 2026-06-14 | **Plan:** 54 | **Agent:** Bellows Developer | **Step:** 1

---

## Summary

Implemented two fixes addressing diagnostic 53 findings:

1. **Multi-turn ledger extraction (shape A):** Fixed silent data loss where `### Ledger Updates` emitted in intermediate assistant turns was invisible to the parser. The parser only read the `result` field of the terminal stream-json event (the final assistant message). Multi-turn agents emit Output Receipts in intermediate turns followed by a short summary as the final message.

2. **in_progress-strand recovery:** Extended `recover_half_claimed` to also recover stranded `in_progress` plans — plans that reached `in_progress` state but lost their runner (e.g., daemon restart during execution). Discriminated by worktree-absence: a legitimately-running plan has its worktree on disk; a stranded one does not.

Plus defense-in-depth: WARN emitted when agent output contains `### Ledger Updates` but the parsed ledger is all-None.

---

## Changes Made

### runner.py — Multi-turn assistant text collection

- During NDJSON stream iteration, now collects text content from all `type: "assistant"` events (intermediate turns)
- Concatenates intermediate assistant text + final result text into `_all_assistant_text` field on the result event
- Sets this field BEFORE passing to `parser.parse()`, making all turns visible to ledger extraction
- Existing result/ceo_flags/verdict_requested extraction unchanged (still reads final message only)

### parser.py — Ledger source fallback

- Ledger extraction now uses `raw.get("_all_assistant_text")` as the text source for `### Ledger Updates` regex matching
- Falls back to `result_text` when `_all_assistant_text` is absent (backward compatibility)
- All other extraction (ceo_flags, verdict_requested) still uses `result_text` only — correct behavior since those belong in the final message

### bellows.py — Defense-in-depth WARN

- Added check in `_apply_ledger_updates`: if the agent's output text contains the literal `### Ledger Updates` heading but parsed `ledger_updates` is all-None, emit a WARN
- Checks both `_all_assistant_text` and `result_text` for the heading
- Converts future silent drops into loud signals

### lifecycle.py — in_progress-strand recovery

- Extended `recover_half_claimed` with a second recovery pass for `lifecycle_state = 'in_progress'` plans
- Worktree-absence discriminator: checks `<target_project>/.bellows-worktrees/<plan_id>/` on disk
- If worktree exists → plan is likely still running, skip (`skipped_worktree_exists`)
- Age guard: same `age_guard_seconds` (default 300s) as claimed recovery — young plans are not touched
- No worktree + past age guard → mark `abandoned` + set `closed_at`
- Respects `project_root` scoping (same as claimed recovery)

---

## Tests Added/Modified

### tests/test_runner.py (2 new)
- `test_multiturn_ledger_extraction` — regression repro: `### Ledger Updates` in intermediate assistant event is extracted
- `test_single_turn_ledger_extraction_still_works` — single-turn case (ledger in final result) unchanged

### tests/test_bellows.py (3 new)
- `test_warn_fires_when_heading_present_but_empty` — WARN fires when raw has heading but parsed ledger is all-None
- `test_warn_silent_when_ledger_populated` — no WARN when ledger has content
- `test_warn_silent_when_no_heading` — no WARN when no heading present

### tests/test_lifecycle.py (4 new + 4 updated)
- `test_stranded_in_progress_recovered` — in_progress + no worktree + past age guard → abandoned + closed_at
- `test_in_progress_with_worktree_not_touched` — worktree exists → not abandoned
- `test_in_progress_within_age_guard_not_touched` — within age guard → not touched
- `test_claimed_recovery_still_works_alongside_in_progress` — existing claimed path regression check
- Updated 4 existing tests to accommodate the new in_progress recovery actions in the actions list

### Full suite result
675 passed, 0 failed.

---

## Design Decisions

1. **Runner-side concatenation (shape A):** Chose to set `_all_assistant_text` on the result event dict before passing to parser, rather than modifying the parser to scan raw NDJSON. This keeps the parser's contract clean (it still takes a single event dict) while fixing the root cause at the source.

2. **Worktree-absence as discriminator:** Used `os.path.isdir()` on the worktree path rather than checking `git worktree list`, because the directory check is simpler, faster, and sufficient — the worktree directory is always created/removed as part of the dispatch lifecycle.

3. **Age guard reuse:** Applied the same `age_guard_seconds` default (300s) to in_progress recovery as claimed recovery, ensuring consistency and avoiding race conditions with just-started plans.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented multi-turn ledger extraction fix (runner.py collects all assistant text, parser.py uses it for ledger extraction), defense-in-depth WARN (bellows.py emits WARN on silent drops), and in_progress-strand recovery (lifecycle.py extends recover_half_claimed to abandon stranded in_progress plans without worktrees). All 9 new tests pass; 4 existing tests updated; full suite 675/675 green.

### Files Deposited
- `knowledge/development/ledger-extraction-recovery-fix-dev-log-2026-06-14.md` — this dev log

### Files Created or Modified (Code)
- `runner.py` — collect assistant text from intermediate NDJSON events, set `_all_assistant_text`
- `parser.py` — use `_all_assistant_text` for ledger extraction (fallback to result_text)
- `bellows.py` — defense WARN when ledger heading present but extraction empty
- `lifecycle.py` — in_progress-strand recovery in `recover_half_claimed`
- `tests/test_runner.py` — 2 new multi-turn extraction tests
- `tests/test_bellows.py` — 3 new defense WARN tests
- `tests/test_lifecycle.py` — 4 new in_progress recovery tests + 4 existing tests updated

### Decisions Made
- Runner-side concatenation (shape A) for minimal parser contract change
- Worktree directory existence check as stranded-plan discriminator
- Reused existing age guard (300s default) for in_progress recovery

### Flags for CEO
1. DAEMON RESTART REQUIRED — do NOT restart until this plan fully closes; the restart activates the fix AND triggers recovery that cleans plan 48
2. RE-CANARY — dispatch a fresh PROJECT_STATUS+feedback canary after restart; must now land both ledgers
3. Slice 3 (FORWARD) unblocks only after the re-canary passes

### Flags for Next Step
- QA should verify multi-turn extraction against plan-52's actual step JSON if feasible
- QA should verify in_progress recovery test covers worktree-present path thoroughly
- Defense WARN test should confirm WARN appears in stdout (captured by capsys)

### Ledger Updates
#### Prompt Feedback
**2026-06-14 — ledger-extraction-recovery-fix (Bellows Developer Step 1)**

1. **Plan header context was comprehensive.** The diagnostic root-cause document (plan 53) provided exact line references and a clear discriminating-difference analysis. Every anchor (runner.py:216-226, parser.py:10, bellows.py:1132, lifecycle.py:237/243) was verified correct — no re-derivation needed.

2. **Shape A (runner-side concatenation) was the right call.** Setting `_all_assistant_text` on the result event before parser keeps the parser contract unchanged while fixing the root cause. The alternative (parser scanning raw NDJSON) would have required passing the full stream string into the parser, breaking its single-event-dict contract.

#### Project Status
- 2026-06-14: **Ledger extraction multi-turn fix + in_progress recovery shipped (plan 54 Step 1).** runner.py now concatenates all assistant turn text for ledger extraction; parser.py uses it as fallback; defense WARN on silent drops; lifecycle.py recovers stranded in_progress plans. 675/675 tests green. DAEMON RESTART REQUIRED to activate fix + trigger plan-48 cleanup. Re-canary needed post-restart.
