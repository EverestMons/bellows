# Bellows — Next Session Baton

**Last session:** 2026-05-26 (continuation, session 6)
**Last session focus:** BACKLOG hygiene sweep + Fix F isinstance guard removal

---

## Session summary

Six artifacts shipped end-to-end. Final BACKLOG state: Open down from 13 to 7 entries; 6 retirements + 1 ship close.

| # | Artifact | Outcome |
|---|---|---|
| 1 | Stale roadmap archived | `obsolete-roadmap-bellows-verdict-enrichment-2026-05-27.md` (verdict-enrichment work shipped 2026-05-21; roadmap was post-ship documentation mistaken for queued plan by 2 prior batons) |
| 2 | NEXT_SESSION baton corrected | Stale-priority correction note added; horizon reprioritized |
| 3 | `diagnostic-phase-3b-read-side-step-state-resume-2026-05-26` | **RETIRE.** SA surfaced that the read-side was previously shipped 2026-04-28 and deliberately removed 2026-05-01 as dead code per Phase 3b/3c cost-benefit diagnostic. BACKLOG entry closed. |
| 4 | `diagnostic-teardown-push-silent-failure-2026-05-26` | **RETIRE — premise wrong.** Fresh grep confirmed zero `git push` calls in bellows source (unchanged from 2026-05-21 finding). `_teardown_worktree` mapped: 5 git subprocess calls, all local, zero origin interactions. The 2026-05-24 50-commit accumulation was caused by P0 loop, not push absence. BACKLOG entry closed. |
| 5 | `executable-fix-f-guard-removal-2026-05-26` | **Shipped DEV + QA.** 2 lines removed from `bellows.py` (Fix F guards at lines 495, 587); test fixture conformed from string-list to production dict shape. 2026-05-21 isinstance symmetry pattern at lines 509, 600 correctly preserved as structurally distinct. Suite: 407 passed / 5 known carry-overs / 0 regressions. Rule 20 self-check PASSED. BACKLOG entry closed. |
| 6 | BACKLOG hygiene sweep (Planner-direct) | 3 entries retired via Closed-section cross-reference: step-counter loop (duplicate of 2026-05-24 closure); Step 2 final-step rename-skip (structurally resolved by 2026-05-24 rename-first ordering); daemon-restart recovery shape (structurally resolved by same fix). |

Two governance commits at session-wrap. Bellows submodule at `cf96a27`. Governance root at `432cb79`. Both pushed clean.

**Daemon NOT restarted at session end.** The Fix F simplified discriminator (without isinstance guards on `.join()` log expression) requires daemon restart to load. **Restart before next session.**

---

## In-flight threads (carry forward)

None active. All session work shipped and committed.

**Pattern observed this session (worth carrying forward):** 6 of 7 BACKLOG closures today were retirements of 2026-05-2x-era entries. All 6 shared the same root cause — entries authored from current-state observation without scanning architectural shifts (v4.47 agent-push prohibition shipped 2026-05-21; rename-first ordering and precondition-failure field shipped 2026-05-24) or the BACKLOG's own Closed section. Misframings concentrated in a ~10-day window when major Bellows fixes were landing rapidly. The 2026-05-26 BACKLOG-current-state-grep LESSON captures the discipline rule (~30 second grep of Closed before filing Open entries whose premise is "X is missing/never done/half-implemented"). Today's pre-write check would have prevented every one of these retirements.

---

## Open BACKLOG items added this session (0)

None. This session's net effect on Open was -6 (retirements alone) + -1 (Fix F ship close) = **-7 entries**.

The Fix F entry that was Open at start-of-session was also closed (via ship), so no leftover work from session 5's BACKLOG additions remains.

---

## LESSONS entries added this session (2)

1. **Stale priority claims propagate across batons without PROJECT_STATUS cross-check** [tag: planner-discipline, baton-discipline]. The verdict-enrichment roadmap claim propagated through 2 consecutive batons (sessions 3 + 4 of 2026-05-26) before catching the stale-claim pattern. Pre-write check: every "On the horizon" item carried from prior baton MUST be cross-referenced against PROJECT_STATUS Completed before propagating.

2. **BACKLOG entries authored from current-state grep without scanning Closed history can misframe already-evaluated work** [tag: planner-discipline, backlog-discipline]. Phase 3b read-side was the trigger case (entry's "half-implemented" framing missed the 2026-04-28 ship + 2026-05-01 removal cycle already in Closed). Pre-write check: when filing entries whose hypothesis is "X is missing/never done/half-implemented," grep the BACKLOG Closed section for the feature/function name before filing. ~30 seconds.

---

## On the horizon (next session)

In priority order:

1. **`_gate_rule_20_self_check` ambiguous evidence string** — trivial 1-line evidence string change at `gates.py:441` + 1 regression test. Disambiguates `if not md_paths` failure (Planner-authoring discipline) from `if banner not in content` failure (QA-agent discipline). Surfaced 2026-05-26 session 5; deferred during hardening discipline; still trivial.

2. **`_extract_plan_required_deposits()` returns `set` making `md_paths[0]` hash-dependent** — capability addition at `gates.py:373, 380, 397`. Option (b) from the BACKLOG entry — select "the QA report" by `*-qa-*` path suffix rather than positional index — is most robust. ~10 LOC + regression test. Currently works in practice (QA steps typically have one `.md` deposit), but not deterministic.

3. **Path-keyed rejection cache (2026-05-22)** — `dispatch_mode_validator` cache keyed by filename, so corrected re-deposit at same name is silently skipped. Concrete code-grounded entry, real failure mode observed. Small fix: invalidate cache on `on_modified` watchdog event OR key cache by content SHA. ~10 LOC + 1 regression test.

4. **`_apply_defensive_header_defaults` ineffective at runtime (2026-05-21)** — defensive default applied to original header but `header` is reassigned from `gate_result.get("plan_header", {})` at `bellows.py:494`, which does NOT inherit the default. Warning at `bellows.py:382-383` claims "safe-pause" behavior but the reassignment makes the safety net illusory at intermediate steps. Two resolution shapes: apply default to reparsed header too, or remove the misleading "safe-pause" claim.

5. **Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`** (2026-05-22) — Planner-side mitigation (commit before session-wrap) is working. Option (b) from the BACKLOG entry — teardown detects dirty working tree and produces clearer pause-for-CEO — is small (~20 LOC). Defer until second occurrence demonstrates the discipline alone is insufficient.

6. **WebSearch/WebFetch not in agents' `--allowedTools` list** (2026-05-22) — real capability gap for SA diagnostics that need current external docs. Small fix (~2 LOC). Open question: uniform allowance vs role-conditional. Defer pending decision.

7. **MCP tool denials `mcp__vexp__*` not on READ_CLASS_TOOLS exemption** (2026-05-22) — low frequency (~2 gate failures/30 days). Small fix. Defer until usage increases.

8. **Bellows status UI** (2026-05-21) — genuine design question, not misframed. Worth a dedicated planning session, not snap-decided. Open design questions: deployment shape (web vs Tauri vs menu-bar vs TUI), data source (DB vs filesystem vs daemon endpoint), update mechanism, scope of v1.

9. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — BACKLOG explicitly says defer-until-second-occurrence; Planner-discipline mitigation (serialize same-project plans) working.

10. **Deposits parser parenthetical qualifiers** (2026-05-21) — BACKLOG says defer until first incident; Rule 26 governance prevents the problematic pattern. No incidents to date.

11. **No-match verdict warning rate-limit** (2026-05-21) — low priority, self-limiting.

12. **`_extract_step_text` regex case-sensitivity** (2026-05-13) — governance prevents the failure mode. Defer.

---

## Discipline reminders for next baton

- **Cross-reference every horizon item against PROJECT_STATUS Completed before propagating.** Items 1, 2, 3, 4, 5, 6, 7, 9, 10, 11 above are carried from prior baton or from BACKLOG; verify each is still Open in BACKLOG and not in Completed before treating as live work.
- **Before filing any new "X is missing/never done/half-implemented" BACKLOG entry, grep Closed section for the feature/function name.** This session retired 6 entries that failed this check.
- **2026-05-26 LESSONS entries are both fresh and high-relevance to baton authoring.** Read them before drafting the next baton.

---

## CEO actions before next session

- **Restart Bellows daemon** to load `cf96a27` (Fix F isinstance guard removal). The simplified `.join()` log expressions activate on next plan dispatched after restart.
- No other actions required — all session work shipped, committed, pushed.
