# Double-Claim Forensics: Plan IDs 137 & 138

**Date:** 2026-07-07 | **Diagnostic:** Plan 139 | **Classification:** dual-deposit (not single-file double-claim)

---

## 1. Timeline

All timestamps from lifecycle.db `created_at`, bellows.db `timestamp`, `verdicts/ledger.jsonl`, and `git reflog --all`.

| Time | Event | Evidence |
|---|---|---|
| 12:31:27 | Plan 136 claimed — FAIL-level `executable-plan-lint-qa-steps-guard-2026-07-07.md` | `lifecycle.db: plans WHERE id=136`, `deposit_placeholder_name=executable-plan-lint-qa-steps-guard-2026-07-07.md` |
| 12:36:04 | Plan 136 dies — `claude -p` exit code 1 (session-limit 429), `success: False`, `raw_output` truncated at 5000 chars, no parseable result | `bellows.db: id=2248, status=Blocked`; `logs/20260707-123128-step.json` |
| 12:36:05 | Plan 136 → VerdictPending | `bellows.db: id=2249, status=VerdictPending` |
| 13:42:32 | Planner processes plan 136 stop verdict: "identical plan will be re-deposited once Claude Code usage headroom is confirmed" | `verdicts/ledger.jsonl` entry for plan 136, `verdict: "stop"` |
| ~13:50–13:54 | First deposit of WARN-only plan: `executable-plan-lint-qa-steps-cross-check-2026-07-07.md` appears in `knowledge/decisions/` | Inferred from claim timestamp (13:54:35) — deposit must precede claim |
| 13:54:35 | Daemon claims first deposit as **plan 137** — `mint_and_claim` returns id 137, file renamed to `in-progress-executable-137.md` | `lifecycle.db: id=137, deposit_placeholder_name=executable-plan-lint-qa-steps-cross-check-2026-07-07.md, created_at=2026-07-07T13:54:35.142918` |
| 13:54:35 | Worktree `bellows-wt/137` created from HEAD (`411a90d`) | `git reflog: bellows-wt/137@{2026-07-07 13:54:35} branch: Created from HEAD` |
| ~13:55–13:57 | Second deposit of **same file** (`executable-plan-lint-qa-steps-cross-check-2026-07-07.md`) appears in `knowledge/decisions/` | Inferred from claim timestamp (13:57:25) |
| 13:57:25 | `_invalidate_seen_on_redeposit` fires — slug `plan-lint-qa-steps-cross-check-2026-07-07` discarded from `_seen` | Mechanism at `bellows.py:1633-1646` (see §2b) |
| 13:57:25 | Daemon claims second deposit as **plan 138** — same `deposit_placeholder_name` | `lifecycle.db: id=138, deposit_placeholder_name=executable-plan-lint-qa-steps-cross-check-2026-07-07.md, created_at=2026-07-07T13:57:25.390438` |
| 13:57:25 | Worktree `bellows-wt/138` created from HEAD (`411a90d`) | `git reflog: bellows-wt/138@{2026-07-07 13:57:25} branch: Created from HEAD` |
| 13:59:24 | Plan 137 DEV commit: `0fa4234` | `git log bellows-wt/137` |
| 14:00:21 | Plan 137 dev-log commit: `d153a8c` | `git log bellows-wt/137` |
| 14:00:30 | Plan 137 → Complete, then VerdictPending | `bellows.db: ids 2250-2251` |
| 14:03:28 | Plan 138 DEV commit: `a8b0a2e` | `git log bellows-wt/138` |
| 14:04:26 | Plan 138 dev-log commit: `51a666e` | `git log bellows-wt/138` |
| 14:04:35 | Plan 138 → Complete, then VerdictPending | `bellows.db: ids 2252-2253` |
| 16:12:59 | CEO verdict: plan 137 stopped (duplicate dispatch); plan 138 continues | `verdicts/ledger.jsonl` entries for 137 and 138 |

**Key conclusion from timeline:** Two deposits of the same file, ~3 minutes apart. After the first was claimed and renamed (13:54), a second copy appeared (by 13:57). The daemon correctly processed each as a separate plan because the `_invalidate_seen_on_redeposit` mechanism cleared the slug dedup guard when the second file appeared.

### One source file claimed twice, or two source files?

**Two source files, each claimed once.** Evidence:

1. After plan 137's claim at 13:54:35, `shutil.move` renamed `executable-plan-lint-qa-steps-cross-check-2026-07-07.md` → `in-progress-executable-137.md`. The original file no longer existed in `knowledge/decisions/`.
2. For plan 138 to be claimed at 13:57:25, a new file with the same name had to appear. The daemon cannot claim a nonexistent file.
3. Both lifecycle.db rows share the same `deposit_placeholder_name` but have different `id` values (137, 138) and `created_at` timestamps 2 minutes 50 seconds apart.
4. Plan content is byte-identical: `MD5(halted-executable-137.md) = MD5(halted-executable-138.md) = fc42c09383c043aa02b80a7b8973cf27`.

**What deposited the second copy?** No automated re-deposit mechanism exists in bellows.py (grep confirms no code path writes `executable-*.md` files into `knowledge/decisions/`). The Planner's plan 136 stop verdict stated "identical plan will be re-deposited" — this is a Planner intent communicated in the verdict `reason` text, not an automated action. The re-deposit was manual (CEO or Planner session). A stray third variant (uncommitted code changes to `scripts/plan_lint.py` and `tests/test_plan_lint.py`) was found on main and stashed (`git stash list: stash@{0}: On main: stray plan_lint qa_steps impl (buggy dead-branch variant)`), confirming concurrent manual work on the same feature.

**Most likely scenario:** The CEO was working on the WARN-only plan after plan 136's session-limit death. The plan file was deposited twice — either by saving it twice (editor auto-save, re-drop), by two Planner sessions that each deposited the same plan, or by a manual deposit overlapping with a Planner-session deposit.

---

## 2. Claim-Exclusivity Gap Analysis

### (a) Is the scan→rename atomic?

**No.** The claim path in `bellows.py:run_plan` (lines 441–469) has three steps separated by non-trivial work:

```
1. _handle (bellows.py:1629):   _seen.add(slug)         ← dedup guard set
2. handle_new_plan (line 1751): Thread(run_plan).start() ← thread spawned
3. run_plan (line 457-469):     mint_and_claim()         ← DB write
                                shutil.move()            ← filesystem rename
```

Between step 1 and step 3, the file still exists with its original name. However, the `_seen` set prevents the `_rescan` from picking it up again — so a single deposit cannot be double-claimed by the rescan alone.

The gap: `_invalidate_seen_on_redeposit` (`bellows.py:1633-1646`) can clear `_seen` during this window if a new file event fires for the same slug:

```python
# bellows.py:1633-1646
def _invalidate_seen_on_redeposit(self, path: str):
    filename = os.path.basename(path)
    LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")
    if any(filename.startswith(p) for p in LIFECYCLE_PREFIXES):
        return  # guard: lifecycle renames don't self-invalidate
    slug = verdict.slug_from_path(path)
    if slug in self.orchestrator._seen:
        self.orchestrator._seen.discard(slug)
```

The guard only checks that the NEW file doesn't have a lifecycle prefix. It does **not** check whether an active plan for that slug is in-progress. If a second copy of the deposit file appears while plan N is running, the slug is cleared from `_seen`, and the daemon dispatches plan N+1.

### (b) How is the plan ID allocated?

`lifecycle.py:167-196` — `mint_and_claim` uses `BEGIN IMMEDIATE` + `UPDATE id_sequence SET next_id = next_id + 1 RETURNING next_id - 1` followed by an `INSERT INTO plans`. This is atomic and sequential within a single SQLite connection. Two claims always get different IDs. The ID is a global monotonic counter, not derived from content or filename.

### (c) Does anything dedup by content?

**No.** The claim path has no content-hash check. `deposit_placeholder_name` is recorded in `lifecycle.db` but has no UNIQUE constraint:

```sql
-- lifecycle.db schema (relevant column):
deposit_placeholder_name TEXT   -- no UNIQUE, no CHECK
```

Two different filenames with identical body would both be accepted. Two instances of the SAME filename would also both be accepted — as proven by this incident (both plans 137 and 138 have `deposit_placeholder_name = executable-plan-lint-qa-steps-cross-check-2026-07-07.md`).

### (d) Automated re-deposit from stop verdict?

**No automated re-deposit exists.** `grep -rn 're.deposit\|redeposit\|re_deposit\|auto.*deposit' bellows.py` returns only `_auto_stage_deposits` (unrelated — stages agent-produced files for commit) and `_invalidate_seen_on_redeposit` (the watchdog mechanism, not a depositor). The plan 136 stop verdict's "will be re-deposited" is Planner intent expressed in free text, not a Bellows automation trigger.

---

## 3. Disposition

### Root Cause

**Classification: `dual-deposit` — two file deposits for one feature, not a single-file double-claim.**

A single plan file (`executable-plan-lint-qa-steps-cross-check-2026-07-07.md`) was deposited into `knowledge/decisions/` twice within a 3-minute window. The first deposit was claimed as plan 137 at 13:54:35; the claim renamed the file to `in-progress-executable-137.md`, removing the original. A second copy of the same file appeared ~3 minutes later. The daemon's `_invalidate_seen_on_redeposit` mechanism correctly (per its design) cleared the slug dedup guard, allowing the second copy to be claimed as plan 138. Both ran to completion in separate worktrees, producing byte-identical code changes — a wasted execution and a merge hazard.

The contributing cause was plan 136's session-limit 429 death (12:36), which triggered a re-authoring cycle: the FAIL-level plan was revised to WARN-only with a different filename. During this re-authoring, the plan file was deposited twice. No automated mechanism produced the duplicate; this was a manual double-deposit (two Planner sessions, or an editor double-save, or a manual deposit overlapping a Planner deposit).

### Would session-limit-429 pause-and-hold have prevented this?

**Partially, for this specific incident.** If plan 136 had been held instead of dying with exit code 1, the Planner would not have issued a "re-deposit" intent, and the CEO would not have needed to re-author the plan. The chain of events leading to the double-deposit would not have started.

**However, the underlying claim-exclusivity gap would remain unfixed.** Any future manual double-deposit (e.g., editor auto-save writing the file twice, two Planner sessions producing the same plan, or a cloud-sync duplicate) would still produce two claims. Pause-and-hold addresses the trigger for this incident, not the mechanism vulnerability.

### Fix List (for follow-up executable)

| # | Function / Location | Change Shape | Effect |
|---|---|---|---|
| 1 | `bellows.py:run_plan` (~line 441, before `mint_and_claim`) | Add lifecycle.db query: `SELECT id FROM plans WHERE deposit_placeholder_name = ? AND lifecycle_state IN ('claimed', 'in_progress', 'awaiting_verdict')` | If an active plan exists for the same deposit placeholder, WARN-log "duplicate deposit — active plan {id} already claimed from same placeholder" and halt the duplicate (move to `halted-`, do not mint a new ID) |
| 2 | `lifecycle.py` — `plans` table | Add partial unique index: `CREATE UNIQUE INDEX IF NOT EXISTS idx_plans_active_placeholder ON plans (deposit_placeholder_name) WHERE lifecycle_state IN ('claimed', 'in_progress', 'awaiting_verdict')` | DB-level guard — `mint_and_claim` would raise `IntegrityError` on duplicate, providing defense-in-depth behind the application-level check |
| 3 | `bellows.py:_invalidate_seen_on_redeposit` (~line 1633) | Before discarding from `_seen`, query lifecycle.db for active plans with same slug. If found, log "re-deposit blocked — active plan {id} in progress" and return without invalidating | Prevents `_seen` clearance while a plan is in-progress, closing the window where a watchdog event can trigger a second dispatch |

### Summary Table

| Symptom | Evidence | Root Cause | Fix |
|---|---|---|---|
| Two plan IDs (137, 138) for one feature | `lifecycle.db`: both rows have `deposit_placeholder_name = executable-plan-lint-qa-steps-cross-check-2026-07-07.md` | Dual-deposit: same file deposited twice ~3 min apart | Fix 1: active-placeholder dedup at claim time |
| `_seen` dedup guard did not prevent second claim | `_invalidate_seen_on_redeposit` clears `_seen` on any non-lifecycle-prefixed file event at a known slug | No check for in-progress plans before `_seen` invalidation | Fix 3: guard `_invalidate_seen_on_redeposit` against active plans |
| No DB constraint prevented duplicate | `plans.deposit_placeholder_name` has no uniqueness constraint | Missing constraint | Fix 2: partial unique index on active placeholders |
| Wasted parallel execution + merge hazard | Both worktrees committed identical changes to `scripts/plan_lint.py` and `tests/test_plan_lint.py` | Two worktrees racing on same files | Consequence of the above — fixed by preventing the second claim |
| Plan 136 session-limit death triggered re-authoring chain | `logs/20260707-123128-step.json`: `success: False`, `raw_output` truncated at 5000 chars | No session-limit pause-and-hold — plan dies instead of holding | Session-limit pause-and-hold (carried from plan 132) addresses the trigger but not the mechanism |

---

### Ledger Updates

#### Prompt Feedback

- The diagnostic scope was clear and the CEO context section provided the right pointers (plan 136 death, stash, single-daemon confirmation). Citing the `_invalidate_seen_on_redeposit` mechanism as the specific gap would have further narrowed the investigation.
- The "ruled OUT by hand" note (two-daemon race) saved investigation time — confirming a negative externally and directing the agent to the claim mechanism was efficient.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Reconstructed the full timeline of the 137/138 double-claim from lifecycle.db, bellows.db, verdicts/ledger.jsonl, git reflog, and step logs. Analyzed the claim-exclusivity path in bellows.py, identifying the `_invalidate_seen_on_redeposit` mechanism as the gap that allowed a second deposit to bypass the `_seen` dedup guard. Classified the root cause as `dual-deposit` (two file deposits, not a single-file double-claim) with a 3-fix list for the follow-up executable.

### Files Deposited
- `knowledge/research/plan-double-claim-137-138-2026-07-07.md` — timeline, claim-path analysis, disposition, fix list, summary table

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified as `dual-deposit` rather than `single-file double-claim` based on evidence that the original file was renamed away before the second appeared
- Session-limit pause-and-hold assessed as addressing the trigger for this specific incident but not the underlying mechanism vulnerability

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic)
