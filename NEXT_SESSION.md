# bellows — Next Session Baton

**Created:** 2026-05-27 (replaces 2026-05-19 baton; that baton's items are addressed or rolled into the items below)
**Carry-forward owner:** Planner

This file exists when bellows has work to carry into the next session. Delete it when all items here close.

---

## Priority 1 — Verdict-enrichment executable (ready to author)

**Source roadmap:** `/Users/marklehn/Developer/GitHub/roadmap-bellows-verdict-enrichment-2026-05-27.md`
**Source diagnostic:** `bellows/knowledge/research/verdict-enrichment-surface-2026-05-27.md` (committed via origin `7f0c6f2`)
**Plan filename to use:** `executable-bellows-verdict-enrichment-YYYY-MM-DD.md` (use the actual current date, not 2026-05-27)

**Status:** diagnostic complete, Rule 22 verified, executable not yet written. The diagnostic gave the full surface map; the executable is straightforward to author.

**Scope (locked from this session's design discussion):**
- New `_gate_rule_22_verification` gate consolidating Rule 22 (a)+(c)+(d) mechanical checks
- Verdict-request enrichment that re-surfaces all 8 existing gates in a unified Verification Results table (PASS rows via approach ii — post-hoc inference, ~30 LOC helper in verdict.py)
- New `rule_22_check_failed` Pause Reason Code routed via Rule 25 to "stop and report CEO"
- "Planner-Only Checks Remaining" fixed section at end of verdict request listing what Bellows did NOT verify
- File paths + line numbers on FAIL rows, one-line details on PASS rows

**Out of scope (explicitly rejected this session):**
- Auto-continue / auto-close on all-green. Risk of dropping CEO review is not acceptable. Planner still authors every continue verdict.

**Implementation surface (per diagnostic):**
| File | Changes | Est. LOC |
|---|---|---|
| `bellows/gates.py` | New `_gate_rule_22_verification`; integration into `check()` | ~53 |
| `bellows/verdict.py` | Verification Results table builder; Planner-Only Checks Remaining section; update `_pause_reason_labels`; update Gate Failures section condition to include `rule_22_check_failed` | ~50 |
| `bellows/bellows.py` | Modify both pause-reason assignment blocks (lines 504, 590) to distinguish `rule_22_check_failed` from `gate_failure` via `all(f["gate"] == "rule_22_verification" for f in gate_result["failures"])` | ~6 |
| `bellows/tests/test_gates.py` | New gate tests | ~60 |
| `bellows/tests/test_verdict.py` | Table rendering, PASS row composition | ~60 |
| **Total** | | **~229** |

**Three follow-up flags from the SA that the executable MUST address:**
1. Plan's `**Deposits:**` block uses **project-prefixed relative paths** (`bellows/gates.py`, NOT absolute) per the recursion-risk constraint (LESSONS 2026-05-19 + 2026-05-27). The new gate also performs path-comparison work; using normalized forms means the executable's deposits won't trip the gate it's modifying.
2. `verdict.py` line 116 currently gates the Gate Failures section on `pause_reason == "gate_failure"`. Update to also trigger on `rule_22_check_failed` since the failures list contains the evidence.
3. `parsed["receipt_status"]` is NOT in `gate_result`. Use generic PASS detail `"Status: Complete"` rather than thread it through (semantically equivalent — receipt_status != Complete is already a gate failure).

**Paired governance edit (separate small executable):** PLANNER_TEMPLATE.md Rule 25 routing table needs a row added for `rule_22_check_failed` → "stop and report CEO". Same routing class as `gate_failure` and `scope_violation`.

**Sequencing:** Restart daemon → Phase 1.5 reads → author executable → dispatch → restart daemon → governance edit.

---

## Priority 2 — Daemon parallel-SHA divergence (characterization needed)

**Observed pattern (2026-05-27):** Four of today's commits had parallel SHAs between local and origin:
- `eeaedcb` (local) ≡ `4294706` (origin) — normalize fix
- `289df0c` (local) ≡ `8469c44` (origin) — normalize QA
- `3075764` (local) ≡ `80ca915` (origin) — normalize diagnostic
- `9acd499` (local recovery) ≡ `7f0c6f2` (origin) — verdict-enrichment diagnostic

All four pairs were content-identical (`git diff` returned empty in every case). Local was 3 commits ahead of origin and origin was 4 commits ahead of local at session end; reconciled via `git reset --hard origin/main`.

**The likely mechanism:** Bellows's worktree teardown pushes the agent's commit from the worktree directly to origin. Then locally, the teardown cherry-picks the agent's commit onto local main, producing a content-identical commit with a different SHA (different parent or timestamp). The local push then becomes non-fast-forward against origin (which already has the agent's commit). What happens to that local push isn't fully understood — Bellows may resolve it silently, or local main just diverges and nobody notices until the next session.

**Symptom this produces:** the cherry-pick during teardown reports "previous cherry-pick is now empty, possibly due to conflict resolution" when the branch tip the worktree was created from is a stale commit (e.g., the previous diagnostic's branch tip). The agent's actual new commit lands on origin via the worktree push but local main never gets it cleanly. Looks like a worktree teardown failure but is actually a "local divergence from origin" situation.

**Recovery procedure (proven):** `git fetch origin && git reset --hard origin/main`. Working-tree state preserved. Tested this session — clean.

**Why this is a Priority 2, not Priority 1:**
- Recovery is mechanical (one command)
- No data loss
- No incorrect behavior in agent output
- Affects operator confidence and clarity of `git log` history, not correctness

**Proposed diagnostic shape (run before authoring Priority 1 executable):**
- Single SA step, read-only, scope-bounded
- Three questions:
  1. What git operations does `_teardown_worktree` perform, in what order? (Trace `bellows.py` teardown code path through subprocess calls.)
  2. Does it push from worktree to origin? Does it also push from local to origin? Both? Either conditionally?
  3. When both: what's the resolution mechanism for the local push — fast-forward expected (origin already has the commit), force-push, `--ff-only` with silent fail, or something else?

**Filename:** `diagnostic-teardown-git-operations-mapping-YYYY-MM-DD.md`

**Recommendation: run this diagnostic BEFORE authoring the verdict-enrichment executable.** If teardown has a real bug, we want to know before depositing a 229-LOC plan that runs through the teardown path multiple times.

---

## Priority 3 — Operational housekeeping

**BACKLOG hygiene closures pending:**
- `Added 2026-05-20: Set DISABLE_AUTOUPDATER=1` — implemented and shipped this session. Move to Closed with reference to `Done/executable-disable-autoupdater-2026-05-27.md`.
- New entry to add as Closed: shop_next_session.md Thread 3 (`_gate_deposit_exists` path-form normalization) — shipped via `Done/executable-deposit-exists-path-form-normalization-2026-05-27.md`. Was never formally captured in BACKLOG.md before close, so this needs a backdated entry.

**New BACKLOG entry to capture:**
- Pre-existing `test_decisions.py` failures (4 tests: `TestLoadPhrases::test_loads_phrases_from_file`, `test_includes_known_phrases`, `test_splits_slash_alternatives`, `TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`). PROJECT_STATUS history through 2026-05-27 only documented `test_run_step_timeout` as pre-existing; these four were surfaced for the first time by the disable-autoupdater QA. Origin and date of failures unknown. Open entry with "needs root-cause audit before fix."

**Memory amendments needed:**
- Item 18 ("Bellows OP-001 RESOLVED ... Bellows is operational") is still true but the broader teardown-reliability claim is now nuanced. Add: teardown can produce misleading "empty cherry-pick" messages when the worktree's source branch tip is a stale commit and the agent's real work pushed directly to origin (see Priority 2). Recovery is `git reset --hard origin/main`.

---

## Priority 4 — Stale stuff to clean up

- The 2026-05-19 baton (priority 1 item — stale-redirect grep audit) still hasn't been done. Should be cheap. Defer or just do it next session.
- The four priority-2 items from the 2026-05-19 baton (Bellows-specific known gaps: pause_for_verdict single-enum, verdict prose directive unactionable, Deposits parenthetical qualifiers, stale verdict step warning rate-limit) — none are blocking. Either promote to BACKLOG.md or explicitly decline.

---

## What's CLEAN at session end

- Path-form normalization fix shipped and live (daemon restarted).
- DISABLE_AUTOUPDATER fix shipped and live (daemon restarted twice this session).
- Verdict-enrichment diagnostic shipped, Rule 22 verified, verdict authored.
- Local main is reconciled to origin via reset.
- All 4 of today's plans either in Done/ (3) or about to land there (1, pending Bellows verdict consumption).

---

## Definition of Done for this file

Delete this file when:
1. Priority 1 (verdict-enrichment executable) is authored, shipped, and merged.
2. Priority 2 (parallel-SHA diagnostic) is run OR consciously deferred to BACKLOG.
3. Priority 3 (BACKLOG hygiene + test_decisions.py entry + memory amendment) is complete.
4. Priority 4 (2026-05-19 carry-overs) are either promoted or declined.

If priorities 2–4 are deferred but priority 1 ships, rewrite this file with only the unresolved items.
