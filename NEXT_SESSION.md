# Bellows — Next Session Baton

**Last session:** 2026-05-27 (session 10)
**Last session focus:** Leftover-after-ship tooling — two failed implementations, retired as term-matching limit. Closure moves shipped: LESSONS updates, Rule 41 ratification, script header warning.

---

## Session summary

Long session. Attempted to build `scripts/check_backlog_freshness.py` per session-9's tooling-not-rule LESSON recommendation. Two iterations shipped, both halted at Rule 22 (b) substance check. BACKLOG entry filed retiring the original problem as not achievable with term-matching; manual Phase 1.5 grep remains the working solution. After CEO check-in on "how do we not redo this," three closure moves shipped: LESSONS follow-up note on the 2026-05-26 leftover-after-ship entry, new LESSON for the SA early-output anchor pattern, script header warning. After CEO check-in on "what's the logical next step," PLANNER_TEMPLATE v4.53 shipped with new Rule 41 ratifying the SA anchor pattern into governance.

| # | Artifact | Outcome |
|---|---|---|
| 1 | Scope diagnostic | SA enumerated 4 input shapes (BACKLOG, PROJECT_STATUS, git log, 5 recurrence pairs). Clean ship. `Done/diagnostic-leftover-after-ship-tooling-scope-2026-05-26.md`. |
| 2 | V1 blueprint (3-step plan halted at first SA timeout 713s; single-step SA after retry succeeded) | SA delivered a comprehensive blueprint with parsing, matching algorithm, output format, CLI, and ground-truth traces for all 4 recurrences. Predicted zero false positives. `Done/executable-leftover-after-ship-tooling-blueprint-2026-05-26.md`. |
| 3 | V1 implementation | DEV shipped `scripts/check_backlog_freshness.py` (239 LOC, commit `3c377a2`) per blueprint. Live run: 6/6 entries flagged, 39 candidates. SA's hand-traced FP analysis was wrong — verified fingerprint overlap in the abstract but didn't cross-product against all Closed entries and PS slugs. Halted at Rule 22 (b). `halted-executable-leftover-after-ship-tooling-implementation-2026-05-26.md`. |
| 4 | V2 algorithm rework blueprint (3-step plan, halted at first SA at 730s; 2-step chunked plan, halted at second SA at 636s; single-step retry with explicit early-output anchors, **shipped**) | Three SA-content steps timed out in a row before the retry worked. Retry instructed: post claim confirmation BEFORE reads, post 1-line acknowledgment as each file read completes, post 1-line marker at the start of each section. Reproducible anti-timeout pattern. Blueprint delivered: high-distinctiveness term extraction (backtick ≥ 5, hyphenated ≥ 12, underscore ≥ 8 with ≥ 2 underscores, executable slugs), title-word matching dropped, source-specific thresholds tightened. Predicted 60% candidate reduction and 4/6 FP entries. Commits `550517f`, `0d219a1`. |
| 5 | V2 implementation | DEV edited script in place to 254 LOC (commit `141c0c3`), per blueprint Section 5. Live run: 37 candidates (predicted 15), 6/6 entries still flagged (predicted 4/6). Implementation faithful to blueprint; deviation was in the blueprint's prediction. **Root cause:** V2 traded one FP source (BACKLOG Closed title-word noise, ELIMINATED) for another (PROJECT_STATUS slug-token noise from generic 6+ char tokens like `bellows`, `planner`, `template`). Blueprint Section 3 only re-traced v1-flagged candidates, didn't enumerate NEW candidates v2 would surface. SA's own "Flags for Next Step" called this risk out; Planner underweighted it. Halted at Rule 22 (b). `halted-executable-freshness-check-algorithm-v2-implementation-2026-05-27.md`. |
| 6 | BACKLOG closure | Closed 2026-05-27 (RETIRE — term-matching approach insufficient). Captures: both failed iterations, root limit (term-matching can't distinguish same-function-different-bug without semantic understanding), session lessons. Revisit trigger: capability-addition framing only — if semantic-comparison primitive becomes available, reconsider. |
| 7 | Closure moves (CEO check-in: "how do we not redo this?") | Three artifacts to prevent re-treading: (a) follow-up note appended to 2026-05-26 "Leftover after ship" LESSON explicitly saying "Do not re-attempt with pure term-matching"; (b) new 2026-05-27 LESSON for the SA dense-content early-output anchor pattern (3 reproductions documented, working anchors specified, counter-patterns noted, template prompt provided); (c) script header warning at `scripts/check_backlog_freshness.py` with halted-experiment notice, FP rate, root limit, revisit trigger, cross-references. Commits: bellows `1ac42be` (script header), governance `1925cae` (LESSONS + submodule pointer bump). |
| 8 | Rule 41 ratification (CEO check-in: "logical next step?") | PLANNER_TEMPLATE v4.52 → v4.53 with new Rule 41 "SA dispatch shape for Bellows-watched directories — distributed early-output anchors mandatory for content load >400w." Insertion: Rule body after Rule 40, rule-index table row, Lessons Learned row in chronological position. Three required anchors codified (claim-confirmation BEFORE reads, 1-line acknowledgment after each file read, 1-line marker at start of each section), two counter-patterns documented (front-loaded plan-of-attack alone, chunking), copy-paste template provided. Governance commit `97a5b45`. **Daemon NOT restarted** — pure governance edit, no Bellows code changed. |

**Commits this session (10 total):**
- `301185c` Scope diagnostic findings
- `d2e07a9` V1 blueprint
- `3c377a2` V1 script
- `550517f` V2 outline
- `0d219a1` V2 blueprint
- `141c0c3` V2 script edit
- `285d82d` Session-wrap (BACKLOG closure + 17 lifecycle files)
- `04dac2e` PROJECT_STATUS entry + initial NEXT_SESSION baton
- `1ac42be` Script header warning
- `cf14124`, `1925cae`, `97a5b45` Governance root (bellows pointer bumps + LESSONS update + Rule 41 ratification)

**Daemon NOT restarted.** V2 script `scripts/check_backlog_freshness.py` exists in tree but is reference-only — Bellows doesn't run it. No Bellows daemon code changed this session. PLANNER_TEMPLATE v4.53 is governance-only.

---

## In-flight threads (carry forward)

None active. All session work halted or shipped and committed.

---

## Open BACKLOG items added this session (0)

None added. One Closed entry filed (term-matching approach retirement).

---

## LESSONS entries added this session (1 new, 1 follow-up)

- **NEW 2026-05-27:** "SA dense-content blueprint steps need explicit early-output anchors to avoid ~600-730s inactivity timeouts" — tags `planner-discipline`, `plan-shape`, `bellows-integration`. Three reproductions documented (713s, 730s, 636s timeouts), working anchor pattern (claim-confirmation BEFORE reads, 1-line ack after each file read, 1-line marker at section starts), counter-patterns (front-loaded plan-of-attack alone fails; chunking doesn't fix it), template prompt. **Ratified into PLANNER_TEMPLATE Rule 41 this same session.**
- **Follow-up appended to 2026-05-26 "Leftover after ship" entry:** explicit "Do not re-attempt with pure term-matching" with session-10 attempt summary, root limit, and revisit trigger.

**Candidate LESSONS for future sessions if patterns recur (captured in BACKLOG entry, not yet promoted):**
- **Same-day-overwrite assumption in Bellows scope_check** — observed one occurrence (the script's date-rolled-over deposit caused scope_check FAIL on v2 implementation). Promote on second occurrence.
- **Blueprint FP-validation asymmetry** — observed twice this session (v1 and v2 blueprints both validated "what to catch" without stress-testing "what to exclude"). Third occurrence would qualify as a governance-root LESSON in its own right.

---

## Governance edits this session (v4.52 → v4.53)

- **New Rule 41:** SA dispatch shape for Bellows-watched directories — distributed early-output anchors mandatory for content load >400w. Codifies the anchor template from the 2026-05-27 LESSON. Lives in the Bellows-integration cluster of rules (alongside Rules 22-26, 35, 39, 40). Sister to Rule 13 (semantic anchoring) — Rule 41 addresses mechanical liveness anchoring.
- **Rule-index table** updated with Rule 41 row.
- **Lessons Learned table** updated with the v4.53 ratification row.

---

## On the horizon (next session)

Session-9 baton listed 6 horizon items. Session 10 closed zero of them; the leftover-after-ship Closed entry doesn't unlock anything else. Remaining horizon, unchanged from session 9:

1. **Bellows status UI** (2026-05-21) — still the natural next-session candidate if focus stays on Bellows. Genuine design work. Open design questions: deployment shape (web vs Tauri vs menu-bar vs TUI), data source (DB vs filesystem vs daemon endpoint), update mechanism, scope of v1. Needs a dedicated planning session.

2. **Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`** (2026-05-22) — Planner-side discipline (commit before session-wrap) working. Option (b) from BACKLOG (~20 LOC pre-cherry-pick dirty-tree check) is the small build if/when second occurrence arrives.

3. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — defer-until-second-occurrence; discipline mitigation working.

4. **Deposits parser parenthetical qualifiers** (2026-05-21) — defer until first incident; Rule 26 prevents the pattern.

5. **No-match verdict warning rate-limit** (2026-05-21) — low priority, self-limiting.

6. **`_extract_step_text` regex case-sensitivity** (2026-05-13) — governance prevents the failure mode.

**Bellows hardening sweep status:** substantively complete; the leftover-after-ship attempt this session was an offshoot (Planner discipline tooling, not Bellows daemon hardening). Remaining 6 horizon items still all deferred-by-disposition. Next session options:
- **Start Bellows status UI (#1)** — biggest concrete next move within Bellows
- **Shift focus to a different project** — forge (pre-scan sync workflow), anvil (COMPANY.md update + first executable plan pending), invoice-pulse (Phase B fuel bracket data migration pending Windows production query results), study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest
- **Address shop-meta governance items** — line 1369 carry-over from sessions 8, 9

---

## Open governance follow-up

- **Line 1369 historical lesson** in PLANNER_TEMPLATE — still references "the Planner-owned terminal-move pattern from Rule 25 (rename the plan file directly to `Done/` via `Filesystem:move_file`...)" — carry-over from sessions 8, 9 batons. Stale per the 2026-05-26 v4.52 reconciliation. Not blocking; flag for next session if/when touching governance text.
- **Cosmetic: commit message `97a5b45` has a literal `\u2014` instead of em-dash** from a shell escape that didn't interpret. Won't fix — force-push to clean a message crosses the destructive-git line for marginal benefit. Content is correct.

---

## Discipline reminders for next baton

- **Cross-reference every horizon item against current state before propagating** (5/5 catch rate across sessions 7-9; held this session — no horizon items needed re-evaluation).
- **Pre-write grep of BACKLOG Closed section AND current code state before treating any baton-carried entry as live** — discipline rule holds.
- **2026-05-26 LESSONS entries (7 from sessions 5-10) remain fresh and high-relevance.** Re-read before drafting any plan that involves housekeeping operations.
- **2026-05-27 LESSONS entry on SA early-output anchors is now codified as Rule 41.** Any Bellows-dispatched SA prompt >400w MUST include the three anchors. The LESSON is for context; the rule is for compliance.
- **Term-matching has structural limits for same-function-different-bug detection.** If a future task requires distinguishing two entries that share a function name or project name but describe different bugs, term-matching is the wrong approach. Reconsider only if semantic-comparison primitives become available. The retired `scripts/check_backlog_freshness.py` has a header warning preserving this signal.
- **Daemon restart NOT required this session-wrap.** No Bellows code changed; governance-only.

---

## CEO actions before next session

- None required. No daemon restart needed. No manual filesystem operations needed. No pending verdicts to resolve.
