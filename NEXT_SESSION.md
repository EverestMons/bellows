# bellows — Next Session Baton

**Created:** 2026-05-21 (replaces 2026-05-21 prior baton; Priority 2 resolved, Priority 1 sequencing now clear)
**Carry-forward owner:** Planner

This file exists when bellows has work to carry into the next session. Delete it when all items here close.

---

## Priority 1 — Verdict-enrichment executable (READY TO AUTHOR)

**Source roadmap:** `/Users/marklehn/Developer/GitHub/roadmap-bellows-verdict-enrichment-2026-05-27.md`
**Source diagnostic:** `bellows/knowledge/research/verdict-enrichment-surface-2026-05-27.md` (mis-dated; actual creation 2026-05-21)
**Plan filename to use:** `executable-bellows-verdict-enrichment-YYYY-MM-DD.md` (use the actual current date — run `date "+%Y-%m-%d"` per Rule 40 before authoring)

**Status:** All preconditions met. Priority 2 (parallel-SHA divergence characterization) is complete and unblocks Priority 1. The governance edit shipped (PLANNER_TEMPLATE v4.46, Rule 25 routing row for `rule_22_check_failed` now in place).

**Scope (locked from 2026-05-21 design):**
- New `_gate_rule_22_verification` gate consolidating Rule 22 (a)+(c)+(d) mechanical checks
- Verdict-request enrichment re-surfacing all 8 existing gates in a unified Verification Results table (PASS rows via post-hoc inference, ~30 LOC helper in verdict.py)
- New `rule_22_check_failed` Pause Reason Code (routing row ALREADY in PLANNER_TEMPLATE per 2026-05-21 governance plan)
- "Planner-Only Checks Remaining" fixed section at end of verdict request
- File paths + line numbers on FAIL rows, one-line details on PASS rows

**CRITICAL operational adjustment per Priority 2 findings:** Author this plan WITHOUT `git push` instructions in step prose. Replace "Commit with message X and push to origin/main" with "Commit with message X. Do NOT push — the Planner will handle session-wrap commits." This eliminates the parallel-SHA divergence at the source. The 2026-05-21 governance and bellows-diagnostic plans demonstrated divergence does occur and reconciliation is operationally fine, but the verdict-enrichment plan has 5 deposits (vs. the diagnostic's 1) and the divergence compounds linearly. Cleaner to ship without push.

**Implementation surface (per diagnostic):**
| File | Changes | Est. LOC |
|---|---|---|
| `bellows/gates.py` | New `_gate_rule_22_verification`; integration into `check()` | ~53 |
| `bellows/verdict.py` | Verification Results table builder; Planner-Only Checks Remaining section; update `_pause_reason_labels`; update Gate Failures section condition to include `rule_22_check_failed` | ~50 |
| `bellows/bellows.py` | Modify both pause-reason assignment blocks (lines 504, 590) to distinguish `rule_22_check_failed` from `gate_failure` via `all(f["gate"] == "rule_22_verification" for f in gate_result["failures"])` | ~6 |
| `bellows/tests/test_gates.py` | New gate tests | ~60 |
| `bellows/tests/test_verdict.py` | Table rendering, PASS row composition | ~60 |
| **Total** | | **~229** |

**Three follow-up flags from the SA diagnostic that the executable MUST address:**
1. Plan's `**Deposits:**` block uses **project-prefixed relative paths** (`bellows/gates.py`, NOT absolute) per the recursion-risk constraint. The new gate also performs path-comparison work; using normalized forms means the executable's deposits won't trip the gate it's modifying.
2. `verdict.py` line 116 currently gates the Gate Failures section on `pause_reason == "gate_failure"`. Update to also trigger on `rule_22_check_failed`.
3. `parsed["receipt_status"]` is NOT in `gate_result`. Use generic PASS detail `"Status: Complete"` rather than thread it through.

**Sequencing:** Restart daemon (per outstanding restart reminders from disable-autoupdater + path-form normalization shipped 2026-05-21) → Phase 1.5 reads → author executable → dispatch.

---

## Priority 2 — RESOLVED (parallel-SHA divergence)

Closed by 2026-05-21 diagnostic `knowledge/research/teardown-git-operations-mapping-2026-05-21.md`. Findings classified the pattern as architectural mismatch (agent push + Bellows cherry-pick), NOT a Bellows code bug. Recovery procedure (`git fetch origin && git log HEAD --not origin/main && git reset --hard origin/main`) verified safe with the unique-local-commits pre-check.

---

## Priority 3 — Operational housekeeping (carry-forward)

**Outstanding daemon restart needed.** Three shipped fixes are not yet live in the running daemon:
- DISABLE_AUTOUPDATER env-var (commit `93b74fb`)
- deposit_exists path-form normalization (commit `336e4fb`)
- Rule 25 / Rule 40 governance edits (PLANNER_TEMPLATE.md v4.46)

Restart with `pkill -f "bellows" && cd ~/Developer/GitHub/bellows && python3 bellows.py &` (or whatever startup pattern is current).

**BACKLOG hygiene closures pending (carried from prior baton, still open):**
- `Added 2026-05-20: Set DISABLE_AUTOUPDATER=1` — implemented and shipped 2026-05-21. Move BACKLOG entry to Closed with reference to `Done/executable-disable-autoupdater-2026-05-27.md` (mis-dated; actual ship 2026-05-21).
- `_gate_deposit_exists` path-form normalization — shipped 2026-05-21 via `Done/executable-deposit-exists-path-form-normalization-2026-05-27.md` (mis-dated). Add backdated Closed entry to BACKLOG.

**New BACKLOG entries to capture:**
- **`config.json` not gitignored.** `bellows/config.json` (containing pushover keys) is untracked but NOT in `.gitignore`. Risk: accidental commit of secrets. Fix: add `config.json` to `bellows/.gitignore`. One-line edit.
- **`Bash(git:*)` permission too broad.** `.claude/settings.local.json:4` auto-approves all git commands including `git push --force` and `git reset --hard`. Flagged in 2026-05-04 bash-permission audit, re-surfaced by 2026-05-21 teardown diagnostic. Fix surface: replace with `Bash(git add:*)`, `Bash(git commit:*)`, etc. — explicit allowlist. Cost: ~10 lines settings change + per-plan test against the allowlist.
- **PLANNER_TEMPLATE.md `git push` removal from housekeeping section.** Root cause of parallel-SHA divergence per 2026-05-21 diagnostic Q4. Future governance executable: edit Rule 23 housekeeping order from `feedback → commit → push` to `feedback → commit (Planner handles push at session-wrap)`. Cross-check all references throughout the template.
- **PLANNER_TEMPLATE.md line 671 stale count.** Says "only two codes authorize auto-proceed" but routing table has 3 (`auto_close_disabled`, `qa_checkpoint`, `header_pause`) — header_pause was added 2026-05-21 in routing-cleanup plan. One-line correction in a future governance edit.
- **Bellows expected-keys warning misleading on single-line headers.** `bellows.py:419` emits "missing: ['author', 'project', 'total_steps']" even when the safety-critical `pause_for_verdict` IS parsed. Either tighten the warning to only fire on safety-critical missing keys, or update Planner plan templates to use multi-line headers exclusively. Low priority — false alarm only, no actual plan misbehavior.
- **Pre-existing `test_decisions.py` failures (4 tests).** Surfaced first time by disable-autoupdater QA. Origin and date unknown. Open BACKLOG entry with "needs root-cause audit before fix."

**Memory amendments needed (for user memory):**
- Update Item 18 (Bellows OP-001 RESOLVED) — broader teardown-reliability claim now nuanced. Add: teardown produces parallel-SHA local-vs-origin divergence by design when the agent pushes from worktree (Planner-authored plan prose with `git push` instructions triggers this). Recovery via `git fetch origin && git reset --hard origin/main` after pre-check. Documented at `bellows/knowledge/research/teardown-git-operations-mapping-2026-05-21.md`.

---

## Priority 4 — Stale carry-overs

- 2026-05-19 baton priority 1 (stale-redirect grep audit) still not done. Defer or knock out.
- 2026-05-19 baton priority-2 items (4 minor Bellows gaps: pause_for_verdict single-enum, verdict prose directive unactionable, Deposits parenthetical qualifiers, stale verdict step warning rate-limit) — none blocking. Promote to BACKLOG or decline.

---

## What's CLEAN at session end 2026-05-21

- Path-form normalization fix shipped and committed (daemon restart pending)
- DISABLE_AUTOUPDATER env-var shipped and committed (daemon restart pending)
- Governance executable v4.46 shipped: Rule 25 routing row + Rule 40 date discipline + 2 LESSONS entries
- Teardown git-operations diagnostic shipped with mechanism characterized
- Both repos pushed to origin (bellows `b4e3cb1`, governance-root `1d80816`)
- Both repos reconciled — no parallel-SHA divergence carried forward
- Submodule pointers clean (`git submodule status` showed no `+` prefixes)
- Concurrency test result captured: Bellows demonstrably interleaves multi-project plans without contention

---

## Definition of Done for this file

Delete this file when:
1. Priority 1 (verdict-enrichment executable) is authored, shipped, and merged
2. Priority 3 housekeeping items (daemon restart, BACKLOG hygiene, memory amendment, new BACKLOG entries) are addressed or explicitly deferred
3. Priority 4 carry-overs are promoted or declined

If priority 1 ships but housekeeping remains, rewrite this file with only unresolved items.
