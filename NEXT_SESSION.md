# Bellows — Next Session Baton

**Last session:** 2026-05-25
**Last session focus:** Bellows hardening — set→list capability fix + file_change_audit false-negative diagnostic + structural fix + test regression follow-up

---

## Session summary

Four plans shipped, all closed to Done/. Three are structural Bellows hardening; one is a follow-up to close a regression detected during the third plan's full-suite run.

| # | Plan | Outcome |
|---|---|---|
| 1 | `executable-extract-plan-required-deposits-set-to-list-2026-05-25` | `_extract_plan_required_deposits` and `_filter_transient_paths` return `list` (preserving authoring order); `md_paths[0]` selection now deterministic. 1 new test, 126/126 pass in `test_gates.py`. Closes BACKLOG 2026-05-24 capability entry. |
| 2 | `diagnostic-file-change-audit-false-negative-2026-05-25` | H1 CONFIRMED: `git diff --stat` is blind to committed changes. Cascading effect: `_gate_scope_check` silently bypassed on every code-edit step. 3 Rule 39 verification blocks captured. |
| 3 | `executable-file-change-audit-fix-2026-05-25` | `_capture_git_diff` and `_parse_diff_stat` rewritten to use HEAD SHA + commit-range diff. Function names preserved (32 mock-patch sites unchanged). 396/407 pass, 11 carry-over failures. Closes BACKLOG 2026-05-21 entry AND closes the cascading silent bypass. |
| 4 | `executable-test-rule-26-set-to-list-followup-2026-05-25` | 6 set-literal assertions in `tests/test_rule_26_deposit_parser.py` wrapped in `set(...)` to accommodate plan 1's list return. 9/9 tests now PASS. |

**Daemon restart REQUIRED at session start next time.** Three of today's plans (1, 3, 4) shipped code that the live daemon hasn't loaded. The daemon will continue dispatching with old gate code and old `_capture_git_diff` until restarted.

---

## In-flight threads (carry forward)

**None active.** All four plans shipped to Done/, all verdicts consumed, all PROJECT_STATUS entries prepended, all carry-over regressions resolved.

---

## Open BACKLOG items at session end

Two new closures from today (file_change_audit + extract_plan_required_deposits set→list). Pre-existing open carryover from 2026-05-22 baton:

- BACKLOG `config.json` gitignore (Open)
- `Bash(git:*)` too broad allowlist (Open)
- PLANNER_TEMPLATE git-push removal (Open)
- `bellows.py:419` warning ineffective (Open)
- `bellows.py:505/:594` isinstance asymmetry partial (Open)
- `pause_for_verdict` enum at `bellows.py:305` (Open)
- `gates.py:380/:323` parenthetical strip (Open)
- `bellows.py:1280` no-match warning dedup (Open)
- `_extract_step_text` case (Open, deferred)

**Closed this session:**
- 2026-05-21 `file_change_audit` 0-files-modified (was Open; closed by plan 3)
- 2026-05-24 `_extract_plan_required_deposits` set→list (was Open; closed by plan 1)

---

## On the horizon (priority order if continuing Bellows hardening)

The 2026-05-22 baton listed these in priority order. Today closed one of them (file_change_audit is no longer on the list because it's a NEW closure, not the original carryover #2 reproduction). The remaining horizon:

1. **Daemon-restart recovery shape** for `in-progress-*` + verdict-in-resolved pairing (BACKLOG 2026-05-23) — characterization needed; medium-sized SA diagnostic
2. **Parallel-SHA teardown diagnostic** (BACKLOG 2026-05-27) — characterization
3. **PLANNER_TEMPLATE Rule 25 codification edit** (queued in BACKLOG) — small governance edit
4. **Anvil pending COMPANY.md update + agent specialist files + git init** (separate stream)
5. **Rule 21 update** based on today's LESSONS entry on test-scope-vs-test-coverage — small governance edit (~10 LOC change to PLANNER_TEMPLATE.md)

Item 5 is new for next session — captures today's empirical finding into Rule 21 itself so the test_rule_26-style regression class can't recur.

---

## Operational notes for next session

- **Daemon restart REQUIRED before any new plan dispatch.** Three of today's plans shipped code: plan 1 (set→list in gates.py), plan 3 (file_change_audit rewrite in bellows.py), plan 4 (test-only, no daemon impact). The first plan dispatched next session will run gates with the OLD code unless restart happens first. Restart with: `cd /Users/marklehn/Developer/GitHub/bellows && python3 bellows.py`. Verify startup banner shows new module fingerprints.

- **Session-wrap git commits NOT YET RUN.** Today's session shipped 4 plans through Bellows worktree teardown. Each plan's terminal teardown pushed agent commits direct to origin and cherry-picked locally. Lifecycle artifacts (4 plan files in `Done/`, 7 processed verdicts in `verdicts/resolved/`) accumulated as untracked changes. Standard wrap procedure at session start next time: `git add -A knowledge/decisions/Done/ verdicts/ && git commit -m "chore: session-wrap 2026-05-25 lifecycle artifacts" && git push origin main`. Then bump bellows submodule pointer at governance root.

- **Two LESSONS entries captured at governance root** (`/Users/marklehn/Developer/GitHub/LESSONS.md`): (1) targeted-scope QA can miss regressions in test files outside the targeted bucket — `planner-discipline`, `rule-21`; (2) `git diff --stat` blindness to committed changes + the broader pattern of misclassifying blocking gates as informational — `bellows-architecture`, `gate-design`.

- **`file_change_audit` gate now reports real file counts** post-restart. The 11 carry-over failures composition (4 worktree + 6 test_rule_26 + 1 timeout) is reduced to 5 after today's plan 4 — should be exactly 5 (4 worktree + 1 timeout) on next session's full-suite run.

- **Phase 1.5 reads non-negotiable.** Today's session caught an important nuance about the 2026-05-22 baton's framing: it referenced the file_change_audit gate as "informational gate produces misleading signal" but the actual cascade meant `_gate_scope_check` was silently bypassed. The framing in BACKLOG entries can be subtly wrong — re-read recent QA reports and verdict requests to triangulate, don't trust the BACKLOG entry alone.

---

## Definition of Done for this session

- [x] Plan 1 (extract_plan_required_deposits set→list) — closed
- [x] Plan 2 (file_change_audit diagnostic) — closed
- [x] Plan 3 (file_change_audit structural fix) — closed
- [x] Plan 4 (test_rule_26 set-literal follow-up) — closed
- [x] 2 LESSONS entries captured (targeted-scope test-coverage trap + blocking-gate-as-informational framing pattern)
- [ ] Session-wrap git commits — CEO action at session-start next time
- [ ] Daemon restart — CEO action at session-start next time
