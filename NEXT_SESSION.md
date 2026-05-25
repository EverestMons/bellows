# Bellows — Next Session Baton

**Last session:** 2026-05-25
**Last session focus:** 2026-05-22 baton drain — Items 2.A, 2.B (code + governance), 3.B all closed

---

## Session summary

Five plans shipped, all closed to Done/. The 2026-05-22 NEXT_SESSION baton's Definition of Done criteria are all met. Per its own instructions, the baton was drained.

| # | Plan | Outcome |
|---|---|---|
| 1 | `executable-settings-local-bash-fallback-doc-2026-05-22` | BELLOWS_DEVELOPER.md gained `.claude/settings.local.json` bash-fallback paragraph |
| 2 | `executable-qa-steps-header-field-code-2026-05-25` | `_gate_is_qa_step` now reads `qa_steps` header field as authoritative source; 7 regression tests; keyword fallback preserved |
| 3 | `executable-qa-steps-governance-2026-05-25` | PLANNER_TEMPLATE.md → v4.50 documenting the qa_steps field (3 insertion points + Lessons row) |
| 4 | `diagnostic-mcp-read-class-tools-exemption-2026-05-25` | Characterized current READ_CLASS_TOOLS state, classified all 7 vexp tools, recommended Shape A (literal extend) |
| 5 | `executable-mcp-read-class-tools-extension-2026-05-25` | READ_CLASS_TOOLS extended with 5 read-class vexp tools; save_observation deliberately excluded as write-class; 6 regression tests |

**Daemon restart requirements:** plan 2 (new gate code) and plan 5 (extended exemption set) both require daemon restart to load. Plan 5 was tested empirically at runtime on plan 5's own QA step — gate detected `qa_step_detection: PASS | QA step detected (step 2 of 2)` confirming the new field code is live. Plan 3 (governance) is doc-only, no restart.

---

## In-flight threads (carry forward)

**None active.** All five plans shipped to Done/, all verdicts consumed, all PROJECT_STATUS entries prepended, all submodule pointers bumped (or pending session-wrap commit — see Operational below).

---

## Open BACKLOG items at session end

The 2026-05-22 baton's 5 items are closed. New items surfaced today add to the prior carry-over list. Full state in `bellows/knowledge/BACKLOG.md`.

**Promotable items (multiple reproductions, may warrant the next session):**

1. **`_extract_plan_required_deposits` set→list** — BACKLOG 2026-05-24 capability addition. Today's plan 2 hit it as a Rule 22 override (2nd reproduction). Convert from `set` to `list` preserving authoring order, so `md_paths[0]` is deterministic. Small (~3 LOC + 1 test). Next session candidate.

2. **`file_change_audit` gate false-negative** — Logged twice today (plan 1 Steps 1 and 2 both showed `0 files modified` despite real edits). BACKLOG 2026-05-21 defer-recommended. Today is 4th and 5th reproduction. Worth a diagnostic next session to characterize whether the timing/scope issue affects gate trust under Rule 25.

3. **Audit number reconciliation** — Today's plan 3 governance edit used "14/139/10.1%" matching the 2026-05-22 BACKLOG Closed entry; SA fix-shape Section 4 had "17/142/12.0%" from the original diagnostic. One of the two citations is stale. Minor; resolve next time a similar audit comes up.

**Pre-existing open (carry-over from 2026-05-22 baton, unchanged):**

- BACKLOG `config.json` gitignore (Open)
- `Bash(git:*)` too broad allowlist (Open)
- PLANNER_TEMPLATE git-push removal (Open)
- `bellows.py:419` warning ineffective (Open)
- `bellows.py:505/:594` isinstance asymmetry partial (Open)
- `pause_for_verdict` enum at `bellows.py:305` (Open)
- `gates.py:380/:323` parenthetical strip (Open)
- `bellows.py:1280` no-match warning dedup (Open)
- `_extract_step_text` case (Open, deferred)

Plus today's new BACKLOG entries (if filed): Phase 3b read-side helper, teardown push silent failure, daemon-restart recovery shape, path-keyed rejection cache, sequential-Planner-edit cherry-pick conflict, parallel-diagnostic shared-bookkeeping conflict.

---

## On the horizon (priority order if continuing Bellows hardening)

1. **`_extract_plan_required_deposits` set→list** (small, promotion candidate, 2 reproductions)
2. **Daemon-restart recovery shape** for `in-progress-*` + verdict-in-resolved pairing (BACKLOG 2026-05-23)
3. **Parallel-SHA teardown diagnostic** (BACKLOG 2026-05-27, queued)
4. **PLANNER_TEMPLATE Rule 25 codification edit** (queued in BACKLOG)
5. **Anvil pending COMPANY.md update + agent specialist files + git init** (separate stream)

---

## Operational notes for next session

- **Session-wrap git commits NOT YET RUN.** Today's session shipped 5 plans through Bellows worktree teardown. Each plan's terminal teardown pushed agent commits direct to origin and cherry-picked locally — parallel-SHA divergence is expected. Recovery: `git fetch origin && git --no-pager log --oneline HEAD..origin/main` to confirm work landed on origin, then `git reset --hard origin/main` if all content-identical (per 2026-05-27 LESSONS entry). DO THIS FIRST at session start before any new plan work.

- **Submodule pointer bumps not yet pushed at governance root.** Bellows shipped 4 commits today through its worktree-push path. If submodule pointer is stale at governance root, run `cd ~/Developer/GitHub && git status` — if `M bellows`, run `git add bellows && git commit -m "chore: bump bellows submodule (qa_steps + MCP exemption)" && git push origin main`.

- **PLANNER_TEMPLATE v4.50 changes governance landed on origin via worktree teardown.** Verify with `git log --oneline -3 PLANNER_TEMPLATE.md` at governance root.

- **Daemon may still need restart** to pick up plan 2 + plan 5 code changes if not done during today's session. Empirical evidence at end of session shows plan 5's qa_steps code is live (verdict request showed `qa_step_detection: PASS | QA step detected`). MCP exemption extension status unknown — would only show effect on next vexp denial event.

- **Phase 1.5 reads non-negotiable.** Today's session caught the 2026-05-22 baton out of date by 3 days (Items 1.A, 1.B, 3.A had already closed in the interim). Always re-confirm BACKLOG state and recent QA reports before authoring plans even when a baton seems fresh.

---

## Definition of Done for this session

- [x] Item 2.A (settings.local.json bash-fallback doc) — closed
- [x] Item 2.B code (qa_steps header field in gates.py) — closed
- [x] Item 2.B governance (PLANNER_TEMPLATE v4.50) — closed
- [x] Item 3.B (MCP READ_CLASS_TOOLS extension) — closed, with bonus scope (5 vexp tools instead of 2)
- [x] 2 LESSONS entries captured (qa-step single-deposit discipline + mechanization-governance coupling)
- [ ] Session-wrap git commits — CEO action at session-start next time
