# Bellows — Next Session Baton

**Last session:** 2026-05-27 (session 10)
**Last session focus:** Leftover-after-ship tooling — two failed implementations, retired as term-matching limit

---

## Session summary

Long session. Attempted to build `scripts/check_backlog_freshness.py` per session-9's tooling-not-rule LESSON recommendation. Two iterations shipped, both halted at Rule 22 (b) substance check. BACKLOG entry filed retiring the original problem as not achievable with term-matching; manual Phase 1.5 grep remains the working solution.

| # | Artifact | Outcome |
|---|---|---|
| 1 | Scope diagnostic | SA enumerated 4 input shapes (BACKLOG, PROJECT_STATUS, git log, 5 recurrence pairs). Clean ship. `Done/diagnostic-leftover-after-ship-tooling-scope-2026-05-26.md`. |
| 2 | V1 blueprint (single-step SA after the 3-step plan timed out at 713s with empty output) | SA delivered a comprehensive blueprint with parsing, matching algorithm, output format, CLI, and ground-truth traces for all 4 recurrences. Predicted zero false positives. `Done/executable-leftover-after-ship-tooling-blueprint-2026-05-26.md`. |
| 3 | V1 implementation | DEV shipped `scripts/check_backlog_freshness.py` (239 LOC, commit `3c377a2`) per blueprint. Live run: 6/6 entries flagged, 39 candidates. SA's hand-traced FP analysis was wrong — verified fingerprint overlap in the abstract but didn't cross-product against all Closed entries and PS slugs. Halted at Rule 22 (b). `halted-executable-leftover-after-ship-tooling-implementation-2026-05-26.md`. |
| 4 | V2 algorithm rework blueprint (3-step plan, halted at first SA at 730s; 2-step chunked plan, halted at second SA at 636s; single-step retry with explicit early-output anchors, **shipped**) | Three SA-content steps timed out in a row before the retry worked. The retry instructed: post claim confirmation BEFORE reads, post 1-line acknowledgment as each file read completes, post 1-line marker at the start of each section. Reproducible anti-timeout pattern. Blueprint delivered: high-distinctiveness term extraction (backtick ≥ 5, hyphenated ≥ 12, underscore ≥ 8 with ≥ 2 underscores, executable slugs), title-word matching dropped, source-specific thresholds tightened. Predicted 60% candidate reduction and 4/6 FP entries. Commits `550517f`, `0d219a1`. |
| 5 | V2 implementation | DEV edited script in place to 254 LOC (commit `141c0c3`), per blueprint Section 5. Live run: 37 candidates (predicted 15), 6/6 entries still flagged (predicted 4/6). Implementation faithful to blueprint; deviation was in the blueprint's prediction. **Root cause:** V2 traded one FP source (BACKLOG Closed title-word noise, ELIMINATED) for another (PROJECT_STATUS slug-token noise from generic 6+ char tokens like `bellows`, `planner`, `template`). Blueprint Section 3 only re-traced v1-flagged candidates, didn't enumerate NEW candidates v2 would surface. SA's own "Flags for Next Step" called this risk out; Planner underweighted it. Halted at Rule 22 (b). `halted-executable-freshness-check-algorithm-v2-implementation-2026-05-27.md`. |
| 6 | BACKLOG entry filed | Closed 2026-05-27 (RETIRE — term-matching approach insufficient). Captures: both failed iterations, root limit (term-matching can't distinguish same-function-different-bug without semantic understanding), session lessons (SA timeout pattern, scope_check date-mismatch pattern, blueprint FP-validation asymmetry). Revisit trigger: capability-addition framing only — if semantic-comparison primitive becomes available, reconsider. |

**Commits this session:**
- `3c377a2` V1 script
- `d2e07a9` V1 blueprint
- `301185c` Scope diagnostic findings
- `550517f` V2 outline
- `0d219a1` V2 blueprint
- `141c0c3` V2 script edit
- `285d82d` Session-wrap (BACKLOG closure + 17 lifecycle files)

**Daemon NOT restarted.** V2 script `scripts/check_backlog_freshness.py` exists in tree but is not loaded by Bellows (Bellows doesn't run it). Script is reference-only; manual Phase 1.5 grep remains the working solution.

---

## In-flight threads (carry forward)

None active. All session work halted or shipped and committed.

**Three reproducible patterns observed this session (captured in BACKLOG entry):**

1. **SA dense-content steps time out at ~600-730s with empty agent output** (3 occurrences this session: 1100w SA blueprint, 700w SA blueprint, 600w SA blueprint-fill). Successful SA steps had explicit early-output instructions like "post a 3-5 line plan-of-attack before drafting" plus per-file-read acknowledgments. The verbose acknowledgments keep the inactivity timer warm. The retry with claim-confirmation-before-reads + 1-line read acknowledgments + section-start markers WORKED at 600+ words of content. Pattern is now reproducible in both directions (with and without anchors).

2. **Bellows `scope_check` FAILs when script's deposit-file date differs from plan's expected-date.** The freshness script uses `date.today().isoformat()` in its output filename. When v2 ran on 2026-05-27, it created `backlog-freshness-check-2026-05-27.md` instead of overwriting the v1 file from 2026-05-26. Bellows saw this as an out-of-scope file. Not a script defect — a Bellows scope-check assumption about same-date overwrite. Worth filing as Bellows BACKLOG if it recurs in another context.

3. **Blueprint hand-traces validating "what to catch" without stress-testing "what to exclude" miss the asymmetry that drives false positives in production runs.** SA Section 3 should always enumerate NEW candidates the algorithm would surface, not just re-trace existing ones. This pattern hit both v1 and v2 implementations. Captured as session lesson; worth a governance-root LESSONS entry if a third occurrence arises.

---

## Open BACKLOG items added this session (0)

None added. One Closed entry filed (term-matching approach retirement).

---

## LESSONS entries added this session (0)

None. The three patterns above are documented in the BACKLOG closure but not promoted to governance-root LESSONS yet. Rationale: they're observations from a single session. If any of the three recurs, promote then.

**Candidate LESSONS for next session if patterns recur:**
- **SA early-output anchor pattern** — already reproducible enough to be a `planner-discipline` LESSON. Defer one session to see if the anchor approach holds across multiple SA tasks.
- **Same-day-overwrite assumption in Bellows scope_check** — observe one more occurrence before filing.
- **Blueprint FP-validation asymmetry** — third occurrence would qualify as a governance-root LESSON.

---

## On the horizon (next session)

Session-9 baton listed 6 horizon items. Session 10 closed zero of them; the new "leftover-after-ship tooling" Closed entry doesn't unlock anything else. Remaining horizon, unchanged from session 9:

1. **Bellows status UI** (2026-05-21) — still the natural next-session candidate if focus stays on Bellows. Genuine design work, not misframed. Open design questions: deployment shape (web vs Tauri vs menu-bar vs TUI), data source (DB vs filesystem vs daemon endpoint), update mechanism, scope of v1. Needs a dedicated planning session.

2. **Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`** (2026-05-22) — Planner-side discipline (commit before session-wrap) working. Option (b) from BACKLOG (~20 LOC pre-cherry-pick dirty-tree check) is the small build if/when second occurrence arrives.

3. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — defer-until-second-occurrence; discipline mitigation working.

4. **Deposits parser parenthetical qualifiers** (2026-05-21) — defer until first incident; Rule 26 prevents the pattern.

5. **No-match verdict warning rate-limit** (2026-05-21) — low priority, self-limiting.

6. **`_extract_step_text` regex case-sensitivity** (2026-05-13) — governance prevents the failure mode.

**Bellows hardening sweep status:** substantively complete; the leftover-after-ship attempt this session was an offshoot (Planner discipline tooling, not Bellows daemon hardening). Remaining 6 horizon items still all deferred-by-disposition. Next session can:
- **Start Bellows status UI (#1)** — biggest concrete next move within Bellows
- **Shift focus to a different project** — forge (pre-scan sync workflow), anvil (COMPANY.md update + first executable plan pending), invoice-pulse (Phase B fuel bracket data migration pending Windows production query results), study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest (Phase 2: profile seeding, form filling, app history)
- **Address shop-meta governance items** — line 1369 carry-over from session 9 still pending

---

## Open governance follow-up

- **Line 1369 historical lesson** in PLANNER_TEMPLATE — still references "the Planner-owned terminal-move pattern from Rule 25 (rename the plan file directly to `Done/` via `Filesystem:move_file`...)" — carry-over from session 8 and 9 batons. Not blocking; flag for next session if/when touching governance text.

---

## Discipline reminders for next baton

- **Cross-reference every horizon item against current state before propagating** (5/5 catch rate across sessions 7-9; held this session — no horizon items needed re-evaluation).
- **Pre-write grep of BACKLOG Closed section AND current code state before treating any baton-carried entry as live** — discipline rule holds.
- **2026-05-26 LESSONS entries (6 from sessions 5-9) remain fresh and high-relevance.** Re-read before drafting any plan that involves housekeeping operations.
- **NEW (this session): SA dense-content steps need explicit early-output anchors** (claim-confirmation message BEFORE reads, 1-line acknowledgment after each file read, 1-line marker at start of each section draft). Without them, ~600-730s inactivity timeouts are reproducible. Use the retry plan's prompt pattern as a template for any SA blueprint-fill or blueprint-author step where the content is >400 words.
- **NEW (this session): Blueprint FP-validation must enumerate NEW candidates the algorithm would surface, not just re-trace existing ones.** SA Section 3 in this session's v2 blueprint validated only v1-flagged candidates through v2 rules; it missed that v2's lowered PS threshold opened a new noise channel. Always require: "list every Open entry's full candidate set under the new rules, not just those that v1 already flagged."
- **NEW (this session): Term-matching has structural limits for same-function-different-bug detection.** If a future task requires distinguishing two entries that share a function name or project name but describe different bugs, term-matching is the wrong approach. Reconsider only if semantic-comparison primitives become available.
- **Daemon restart NOT required this session-wrap.** Script in tree is reference-only; Bellows daemon doesn't load it.

---

## CEO actions before next session

- None required. No daemon restart needed. No manual filesystem operations needed. No pending verdicts to resolve.
