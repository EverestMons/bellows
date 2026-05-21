# bellows — Next Session Baton

**Created:** 2026-05-21 (replaces 2026-05-21 prior baton; Priority 1 verdict-enrichment shipped)
**Carry-forward owner:** Planner

This file exists when bellows has work to carry into the next session. Delete it when all items here close.

---

## Daemon restart — RESOLVED 2026-05-21

Daemon restarted at session start. Enriched verdict request format verified live across two plan dispatches this session (`diagnostic-priority-3-carryover-audit-v2`, `executable-priority-3-audit-closeout`): Verification Results table renders cleanly with 10 gate rows + 1 informational row; `rule_22_verification` gate reports PASS on QA-step deposits; Planner-Only Checks Remaining section present. Smoke test pass.

---

## Priority 1 — RESOLVED

Verdict-enrichment executable shipped 2026-05-21. 5-file change, 14 new tests, 386 collected / 385 passed / 1 pre-existing failure. Reference: `Done/executable-bellows-verdict-enrichment-2026-05-21.md`.

---

## Priority 2 — Operational housekeeping

**BACKLOG additions to capture (from prior baton + this session):**

- **`config.json` not gitignored.** `bellows/config.json` (containing pushover keys) is untracked but NOT in `.gitignore`. Risk: accidental commit of secrets. Fix: add `config.json` to `bellows/.gitignore`. One-line edit.
- **`Bash(git:*)` permission too broad.** `.claude/settings.local.json:4` auto-approves all git commands. Replace with explicit allowlist: `Bash(git add:*)`, `Bash(git commit:*)`, `Bash(git status:*)`, `Bash(git log:*)`, `Bash(git diff:*)`, `Bash(git checkout:*)`, etc. Explicitly omit `git push`, `git reset --hard`, `git push --force`. Per 2026-05-21 teardown diagnostic findings.
- **PLANNER_TEMPLATE.md `git push` removal from housekeeping section.** Root cause of parallel-SHA divergence. Future governance executable: edit Rule 23 housekeeping order from `feedback → commit → push` to `feedback → commit (Planner handles push at session-wrap)`. Cross-check all template references. **This session's verdict-enrichment plan validated the approach — zero parallel-SHA divergence when push instructions are omitted.**
- **PLANNER_TEMPLATE.md line 671 stale count.** Says "only two codes authorize auto-proceed" but routing table has 3. One-line correction in a future governance edit.
- **Bellows expected-keys warning misleading on single-line headers.** `bellows.py:419` emits "missing: ['author', 'project', 'total_steps']" even when the safety-critical `pause_for_verdict` IS parsed. Tighten to only fire on safety-critical missing keys OR update Planner plan templates to use multi-line headers exclusively.
- **`isinstance(f, dict)` discriminator asymmetry between bellows.py blocks.** Block 1 (line 505) has the defensive guard; Block 2 (line 594) does not. QA classified as non-defect (Block 2's code path only receives dict-format failures), but the asymmetry creates reasoning friction. Symmetric guards would clean this up.

**BACKLOG retirement (CLOSE THIS):**

- **`Pre-existing test_decisions.py failures (4 tests)`.** Retire this entry. Independently verified during 2026-05-21 verdict-enrichment QA: all 18 test_decisions.py tests PASS when pytest runs from main repo. The failures were worktree-context artifacts (missing `INTERMEDIATE_DECISION_PHRASES.md` in worktree). Not a real failure mode.

**BACKLOG closures pending (carried from prior session, still open):**

- `Added 2026-05-20: Set DISABLE_AUTOUPDATER=1` — implemented and shipped 2026-05-21. Move BACKLOG entry to Closed with reference to `Done/executable-disable-autoupdater-2026-05-27.md` (mis-dated; actual ship 2026-05-21).
- `_gate_deposit_exists` path-form normalization — shipped 2026-05-21 via `Done/executable-deposit-exists-path-form-normalization-2026-05-27.md` (mis-dated). Add backdated Closed entry to BACKLOG.

**Memory amendments needed (for user memory):**

- The "Pre-existing test_decisions.py failures (4 tests)" carry-forward in current memory is misleading and should be removed/updated. Verified worktree-context artifact, not a real failure.
- Item 18 (Bellows OP-001 RESOLVED) addendum from prior baton still valid: teardown produces parallel-SHA divergence by design when agent pushes from worktree.
- Add: 2026-05-21 verdict-enrichment plan validated the no-push approach — 4 commits, zero divergence.

---

## Priority 3 — Closed

Five-item carry-over audit completed 2026-05-21. Disposition: 1× UNRESOLVABLE (stale-redirect — no referent), 1× STALE (verdict prose directives — superseded by 2026-05-21 verdict-enrichment), 3× LIVE-MINOR added to BACKLOG (pause_for_verdict enum validation, Deposits parenthetical stripping, no-match verdict warning dedup). Reference: `Done/diagnostic-priority-3-carryover-audit-v2-2026-05-21.md`, `Done/executable-priority-3-audit-closeout-2026-05-21.md`.

---

## What's CLEAN at session end 2026-05-21

- Verdict-enrichment with Rule 22 mechanical check gate shipped, committed (daemon restart pending)
- Teardown git operations mechanism characterized; recommendation validated
- Two LESSONS-worthy patterns demonstrated: (a) Bellows interleaves multi-project plans without contention; (b) removing `git push` from plan step prose eliminates parallel-SHA divergence (zero divergence in verdict-enrichment plan with 4 agent commits)
- Both repos pushed to origin (bellows session-start commit + session-wrap pending)
- No parallel-SHA divergence carried forward
- Submodule pointer bump pending (governance-root)

---

## Definition of Done for this file

Delete this file when:
1. ~~Daemon is restarted and the enriched verdict request shape is confirmed via first dispatch post-restart~~ ✅ 2026-05-21
2. Priority 2 housekeeping items are addressed or explicitly deferred
3. ~~Priority 3 carry-overs are promoted or declined~~ ✅ 2026-05-21 (3 to BACKLOG, 2 closed)
