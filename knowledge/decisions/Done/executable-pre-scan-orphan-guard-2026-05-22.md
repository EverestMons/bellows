# Bellows — Pre-Scan Orphan Guard
**Date:** 2026-05-22 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-22 pre-scan orphan WARN flood diagnostic findings at `bellows/knowledge/research/pre-scan-orphan-warn-flood-2026-05-22.md` (now in `Done/`), the pre-scan loop at `bellows.py:1131-1139` unconditionally renames every `processed-verdict-*.md` file in `bellows/verdicts/resolved/` back to canonical `verdict-*.md` form, regardless of whether a paired `verdict-pending-*` plan still exists in any watched `decisions/` directory.

**Population audit reveals the dominant pathology is broader than the BACKLOG entry described.** SA log analysis: 8,823 rename events and 10,827 stale-verdict events in a single day, driven by 313 unique plan slugs whose plans are in `Done/` and 8 plans that no longer exist anywhere. Zero legitimate rename cases observed on 2026-05-22 — the pre-scan is currently doing no useful work and producing ~400 file moves per cycle.

**Diagnostic Gap Assessment table — lifted verbatim:**

| Gap | Current State | Proposed State | Change Required |
|---|---|---|---|
| (a) Pre-scan unconditional rename | All `processed-verdict-*` files renamed to `verdict-*` every 30s (402 files/cycle, 8,823 renames/day) | Only rename when a `verdict-pending-*{plan_slug}*` file exists in at least one watched `decisions/` directory | `bellows.py` lines 1131-1139: add plan-existence guard before `shutil.move`. Extract `plan_slug` via regex, scan `self.config["watched_projects"]` for `verdict-pending-*` match. ~15 LOC. |
| (b) Plan-existence check helper | No existing function does this check | Inline loop in pre-scan or new helper function `_has_active_plan(plan_slug, watched_projects)` | `bellows.py`: new helper (~8 LOC) or inline in pre-scan. Reuses the same `plan_slug in pname` substring match as line 1199. |
| (c) Log line for skipped orphan | No logging for skipped files | One-shot INFO per skipped orphan per daemon lifetime, suppressed on subsequent cycles | Use a module-level `_prescan_orphan_logged: set` to deduplicate. Log at INFO: `"pre-scan: skipping orphan {fname} — no active verdict-pending plan"`. Not WARN (it's expected state). ~5 LOC. |
| (d) Cleanup of existing orphans in `resolved/` | 10 orphan `verdict-*` files exist; 8 have no paired plan; 2 have plans in `Done/` | One-shot migration: rename existing `verdict-*` orphans back to `processed-verdict-*` | Executable one-shot: for each `verdict-*` in `resolved/` with no paired plan, rename to `processed-verdict-*`. ~10 LOC (executable, not permanent code). |

**Composition order (from diagnostic Section 7):** orphan-check FIRST, then existing collision guard. Reasoning: orphan check eliminates ~99.7% of files before the filesystem collision check runs; orphan files should never be renamed regardless of collision state.

**Plan-existence check semantics (from diagnostic Section 3):** ONLY `verdict-pending-*` files in `decisions/` count as "paired." Plans in `Done/` or `halted-*` do NOT — those are terminal states where the verdict is already correctly consumed.

**Exact anchor (from diagnostic Section 1, verbatim — bellows.py:1131-1139):**

```python
        # Pre-scan: normalize processed-verdict-* to verdict-* (Planner write-time naming mismatch).
        # Files named processed-verdict-* at write time are structurally identical to already-consumed
        # verdicts and would be silently skipped by the main filter. Rename to canonical form so the
        # main loop can process them. See bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md.
        for fname in os.listdir(resolved_dir):
            if fname.startswith("processed-verdict-") and fname.endswith(".md"):
                canonical = fname[len("processed-"):]
                canonical_path = os.path.join(resolved_dir, canonical)
                if os.path.exists(canonical_path):
                    _log("WARN", f"cannot normalize {fname} — canonical {canonical} already exists; skipping rename")
                    continue
                shutil.move(os.path.join(resolved_dir, fname), canonical_path)
                _log("WARN", f"normalized write-time processed- prefix: {fname} → {canonical}")
```

**Slug extraction (from diagnostic Section 4):** the main-loop regex `^verdict-(.+)-step-(\d+)\.md$` applied to the post-strip canonical filename extracts `plan_slug`. No call to `slug_from_path()` needed — direct substring match against `verdict-pending-*` plan filenames works.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a Bellows-side reliability fix task.** **Pre-edit verification:** Before performing edits, run `grep -n 'normalized write-time processed- prefix' bellows.py` and confirm exactly ONE match between lines 1131-1139. Run `grep -c '^verdict-(.+)-step-' bellows.py` to locate the main-loop regex anchor. If counts differ from expected, STOP — deposit a verification-mismatch report at `bellows/knowledge/flags/verification-mismatch-pre-scan-orphan-guard-2026-05-22-step-1.md` documenting actual line numbers and counts, and halt. The Planner triages. **Task — three components, executed in this order:** **(A) Add orphan-check guard to pre-scan.** Modify `bellows.py` lines 1131-1139 to add a plan-existence check BEFORE the existing collision guard. For each `processed-verdict-*.md` file, extract the plan slug from the filename using the main-loop regex pattern (`^processed-verdict-(.+)-step-(\d+)\.md$`), then scan `self.config["watched_projects"]` for any `verdict-pending-*` file containing the slug. If NO match found, skip the rename (the plan is terminal or gone — leave the file as `processed-*`). Log at INFO level (not WARN) with deduplication: `"pre-scan: skipping orphan {fname} — no active verdict-pending plan"`. The orphan-check fires BEFORE the existing collision guard. **(B) Add module-level dedup set.** At the module-level (near other module constants in bellows.py), add `_prescan_orphan_logged: set = set()`. The pre-scan adds each skipped orphan filename to this set on first encounter; subsequent cycles check the set and suppress duplicate INFO logs. The set is daemon-lifetime — cleared on daemon restart. **(C) One-shot migration of existing orphans.** AFTER landing edits (A) and (B), execute a one-shot migration script that scans `bellows/verdicts/resolved/` for `verdict-*.md` files (canonical form), applies the same orphan-check logic (extract slug, scan watched_projects for `verdict-pending-*` match), and for each orphan file (no paired plan found): rename it from `verdict-*.md` to `processed-verdict-*.md`. The 2026-05-22 SA findings cite 8 expected orphans; the script may find 10 or more — process whatever exists. Capture the migration as a separate Python script invocation (NOT permanent code) and save the script output to `bellows/knowledge/development/pre-scan-orphan-migration-output-2026-05-22.txt`. The migration runs against the live `resolved/` directory while the daemon is active — this is safe per the SA findings (the daemon's stale-check ping-pong cycle is self-healing). **Verification after edit:** read `bellows.py` lines 1125-1155 and confirm the new guard is correctly placed BEFORE the collision guard (orphan-check first per diagnostic Section 7). Confirm `_prescan_orphan_logged` set initialization exists at module level. **Deposit a dev log:** write to `bellows/knowledge/development/pre-scan-orphan-guard-2026-05-22.md` documenting: (1) full before/after snippet of the pre-scan loop with 5 lines surrounding context; (2) location of `_prescan_orphan_logged` set initialization (line number); (3) migration script output (counts of orphans found, files renamed, any skipped due to collision); (4) one-paragraph summary citing the 2026-05-22 pre-scan-orphan-warn-flood diagnostic as authority. **Commit:** stage `bellows.py`, the dev log, and the migration output file; commit message `fix(bellows): pre-scan orphan guard at bellows.py:1131 — skip rename when no paired plan exists`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV pre-scan orphan guard`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/bellows.py` (modified)
> - `bellows/knowledge/development/pre-scan-orphan-guard-2026-05-22.md`
> - `bellows/knowledge/development/pre-scan-orphan-migration-output-2026-05-22.txt`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read — this is a Bellows-side reliability fix QA task.** **Before starting, read `bellows/knowledge/development/pre-scan-orphan-guard-2026-05-22.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Verify: (1) `bellows.py` pre-scan loop at lines 1131-1155 (approximate, since new code added) contains the orphan-check guard BEFORE the collision guard — grep for `pre-scan: skipping orphan` confirms the new INFO log string exists; (2) `_prescan_orphan_logged` set initialization exists at module level — grep for `_prescan_orphan_logged: set` or `_prescan_orphan_logged = set()` confirms presence; (3) The orphan-check guard uses substring match against `verdict-pending-*` files in `self.config["watched_projects"]` — read the new code and verify the loop iterates watched_projects; (4) The migration output file exists at `bellows/knowledge/development/pre-scan-orphan-migration-output-2026-05-22.txt` and reports a non-zero count of orphans renamed; (5) Post-migration: `ls bellows/verdicts/resolved/ | grep -E "^verdict-[^.]+\.md$"` returns NO canonical `verdict-*.md` orphans (all should be `processed-verdict-*` or paired with active plans); (6) Existing tests in `tests/test_consume_verdicts.py` still pass; (7) Dev log exists with all required sections; (8) `agent-prompt-feedback.md` has new 2026-05-22 entry from this plan. Capture each check to evidence files at `bellows/knowledge/qa/evidence/executable-pre-scan-orphan-guard-2026-05-22/`: `orphan_guard_grep.txt`, `dedup_set_grep.txt`, `code_inspection.txt`, `migration_output_check.txt`, `post_migration_ls.txt`, `pytest_consume_verdicts.txt`, `dev_log_present.txt`, `feedback_entry.txt`. **Add regression tests.** Per the diagnostic Section 9, add 4 new tests to `tests/test_consume_verdicts.py`: (a) `test_pre_scan_skips_rename_when_no_paired_plan` — setup `processed-verdict-foo-2026-05-22-step-1.md` in `resolved/`, no plan anywhere; assert file stays as `processed-*`, INFO log emitted (not WARN); (b) `test_pre_scan_renames_when_verdict_pending_plan_exists` — setup `processed-verdict-foo-2026-05-22-step-1.md` in `resolved/` AND `verdict-pending-diagnostic-foo-2026-05-22.md` in `decisions/`; assert file renamed to `verdict-foo-2026-05-22-step-1.md`; (c) `test_pre_scan_treats_done_plan_as_no_paired_plan` — setup plan in `Done/` only, no `verdict-pending-*`; assert file NOT renamed; (d) `test_pre_scan_collision_guard_fires_regardless_of_paired_plan` — setup both forms exist + paired plan present; assert collision guard fires (skip rename + WARN). Mirror existing fixture pattern from `tests/test_consume_verdicts.py` (tempfile.TemporaryDirectory, decisions_dir with Done/, verdicts_resolved/pending dirs, watched_projects config, patches for verdict.check_verdict and notifier.push). **Targeted test run.** Run `pytest tests/test_consume_verdicts.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-pre-scan-orphan-guard-2026-05-22/pytest_targeted.txt`. All existing + 4 new tests must pass. Run full bellows suite `pytest 2>&1 | tail -50 | tee bellows/knowledge/qa/evidence/executable-pre-scan-orphan-guard-2026-05-22/pytest_full_tail.txt` and confirm no new regressions. **Structural compliance check.** Run `git --no-pager diff HEAD~1 bellows.py tests/test_consume_verdicts.py 2>&1 | tee bellows/knowledge/qa/evidence/executable-pre-scan-orphan-guard-2026-05-22/diff.txt` and verify the diff matches the planned scope: new guard code in `_consume_verdicts`, new module-level set, 4 new tests appended to `test_consume_verdicts.py`. No unrelated modifications. **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use: `plan_slug` = `executable-pre-scan-orphan-guard-2026-05-22`; `qa_report_path` = `bellows/knowledge/qa/executable-pre-scan-orphan-guard-2026-05-22.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/executable-pre-scan-orphan-guard-2026-05-22/`; `required_evidence_files` = `["orphan_guard_grep.txt", "dedup_set_grep.txt", "code_inspection.txt", "migration_output_check.txt", "post_migration_ls.txt", "pytest_consume_verdicts.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_targeted.txt", "pytest_full_tail.txt", "diff.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-22 entry under Completed for "Bellows pre-scan orphan guard — bellows.py:1131 skips rename when no paired verdict-pending plan exists; eliminates 8,823 daily rename events and 10,827 stale-verdict events; 8 existing orphans migrated to processed-* form" with a one-paragraph summary citing the 2026-05-22 pre-scan-orphan-warn-flood diagnostic. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). Update `bellows/knowledge/BACKLOG.md` — move the "Pre-scan rename produces orphaned `verdict-*` files" open entry to Closed with a 2026-05-22 close note citing this plan and the migration outcome. Use `Desktop Commander:edit_block`. **Commit:** stage QA report, evidence files, PROJECT_STATUS, BACKLOG updates with message `qa(bellows): pre-scan orphan guard at bellows.py:1131`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA pre-scan orphan guard`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-pre-scan-orphan-guard-2026-05-22.md`
> - `bellows/knowledge/qa/evidence/executable-pre-scan-orphan-guard-2026-05-22/` (11 evidence files per Rule 20 self-check list)
> - `bellows/tests/test_consume_verdicts.py` (modified — 4 new tests appended)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/BACKLOG.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---

## Daemon-restart note

This fix touches `bellows.py`, which Bellows does not hot-reload (Rule 35 / Restart Discipline). The running daemon continues executing pre-fix code through this plan's lifecycle — the pre-scan ping-pong on 313 stale slugs continues in the background until daemon restart. The one-shot migration in Step 1 runs against the live `resolved/` directory; the SA findings explicitly confirm this is safe (the daemon's stale-check is self-healing across the rename race). After plan close + daemon restart, the new guard becomes effective and the WARN flood ceases.
