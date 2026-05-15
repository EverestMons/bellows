# `_cleanup_verdicts_for_slug` Call-Site Gap — Diagnostic Findings

**Date:** 2026-05-01 | **Investigator:** SA agent (re-run)

---

## Q1 — Verify the v9 code actually shipped and is current

### Function signature and body

`_cleanup_verdicts_for_slug` exists at `bellows.py:130–140`:

```python
def _cleanup_verdicts_for_slug(slug: str, verdicts_root: Optional[Path] = None) -> int:
    """Remove all verdict-request files for a given plan slug from verdicts/pending/.
    Returns count of files removed."""
    pending_dir = verdicts_root if verdicts_root is not None else BELLOWS_ROOT / "verdicts" / "pending"
    matches = list(pending_dir.glob(f"verdict-request-{slug}-step-*.md"))
    for f in matches:
        f.unlink()
    count = len(matches)
    if count > 0:
        print(f"Bellows: cleaned {count} pending verdict(s) for {slug}")
    return count
```

### Call sites (3 total + startup sweep)

| # | Line | Enclosing function | Plan-state transition | Conditional gate | v9 match |
|---|---|---|---|---|---|
| 1 | 420 | `run_plan()` | Auto-close → Done | Inside auto-close block (all gates pass, no pause, no verdict_requested, effective_auto_close) | ✓ matches v9 "auto-close in run_plan" |
| 2 | 736 | `_consume_verdicts()` | Continue verdict on final step → Done | Inside `if step_number >= total_steps_c` | ✓ matches v9 "continue-to-done" |
| 3 | 756 | `_consume_verdicts()` | Stop verdict → Halted | Inside `else` (non-continue verdict) | ✓ matches v9 "halt" |

**Startup sweep** exists at `bellows.py:809–842`. One-time orphan removal on daemon start.

### Comparison to v9 diagnostic recommendations

The v9 diagnostic (verdict-lifecycle-coupling-2026-04-19.md §7) recommended 3 call sites + startup sweep. All 4 are present. No missing or extra call sites. The function signature gained an optional `verdicts_root` parameter (for testability) vs the original proposal — this is additive, not a drift.

**Commits:** `c5c7742` (helper), `7a6c5dc` (call sites), `a028c53` (startup sweep) — all 2026-04-19 21:43–21:44.

---

## Q2 — Characterize the 51 archived files

All 51 files were found in `verdicts/pending/archived/`. For the 17 files initially showing "MISSING" in the bellows decisions tree, all were located in other watched-project Done/ directories (invoice-pulse, forge, study).

**Every single file corresponds to a plan that reached a terminal state (Done or halted).**

| # | Verdict file | mtime | Slug | Step | Plan state | Plan path |
|---|---|---|---|---|---|---|
| 1 | verdict-request-activity-based-timeout-2026-05-01-step-1.md | 2026-05-01 11:27 | activity-based-timeout-2026-05-01 | 1 | Done | bellows/Done/diagnostic-activity-based-timeout-2026-05-01.md |
| 2 | verdict-request-backlog-append-2026-04-19-step-2.md | 2026-04-19 22:38 | backlog-append-2026-04-19 | 2 | Done | bellows/Done/executable-backlog-append-2026-04-19.md |
| 3 | verdict-request-backlog-close-2026-04-18-integration-protocol-2026-05-01-step-2.md | 2026-05-01 10:03 | backlog-close-2026-04-18-integration-protocol-2026-05-01 | 2 | Done | bellows/Done/executable-backlog-close-2026-04-18-integration-protocol-2026-05-01.md |
| 4 | verdict-request-backlog-hygiene-sweep-2026-04-30-step-1.md | 2026-04-30 15:46 | backlog-hygiene-sweep-2026-04-30 | 1 | Done | bellows/Done/executable-backlog-hygiene-sweep-2026-04-30.md |
| 5 | verdict-request-backlog-hygiene-sweep-2026-04-30-step-2.md | 2026-04-30 16:14 | backlog-hygiene-sweep-2026-04-30 | 2 | Done | bellows/Done/executable-backlog-hygiene-sweep-2026-04-30.md |
| 6 | verdict-request-base-dir-read-dependencies-2026-04-21-step-1.md | 2026-04-21 20:09 | base-dir-read-dependencies-2026-04-21 | 1 | Done | invoice-pulse/Done/diagnostic-base-dir-read-dependencies-2026-04-21.md |
| 7 | verdict-request-base-rates-method-not-allowed-2026-04-21-step-1.md | 2026-04-21 19:07 | base-rates-method-not-allowed-2026-04-21 | 1 | Done | invoice-pulse/Done/diagnostic-base-rates-method-not-allowed-2026-04-21.md |
| 8 | verdict-request-base-rates-url-fix-2026-04-21-step-2.md | 2026-04-21 19:14 | base-rates-url-fix-2026-04-21 | 2 | Done | invoice-pulse/Done/executable-base-rates-url-fix-2026-04-21.md |
| 9 | verdict-request-base-rates-url-fix-postmortem-2026-04-21-step-1.md | 2026-04-21 19:27 | base-rates-url-fix-postmortem-2026-04-21 | 1 | Done | invoice-pulse/Done/diagnostic-base-rates-url-fix-postmortem-2026-04-21.md |
| 10 | verdict-request-bellows-integration-section-audit-2026-05-01-step-1.md | 2026-05-01 09:51 | bellows-integration-section-audit-2026-05-01 | 1 | Done | bellows/Done/diagnostic-bellows-integration-section-audit-2026-05-01.md |
| 11 | verdict-request-canary-bugs-1-3-2026-04-24-step-1.md | 2026-04-24 15:51 | canary-bugs-1-3-2026-04-24 | 1 | Done | bellows/Done/executable-canary-bugs-1-3-2026-04-24.md |
| 12 | verdict-request-canary-phase-3b-restart-2026-04-30-step-2.md | 2026-04-30 12:47 | canary-phase-3b-restart-2026-04-30 | 2 | Done | bellows/Done/executable-canary-phase-3b-restart-2026-04-30.md |
| 13 | verdict-request-chunk-read-paths-2026-04-24-step-1.md | 2026-04-24 22:21 | chunk-read-paths-2026-04-24 | 1 | Done | study/Done/diagnostic-chunk-read-paths-2026-04-24.md |
| 14 | verdict-request-close-activity-timeout-backlog-2026-05-01-step-2.md | 2026-05-01 11:36 | close-activity-timeout-backlog-2026-05-01 | 2 | Done | bellows/Done/executable-close-activity-timeout-backlog-2026-05-01.md |
| 15 | verdict-request-close-stranded-csv-upload-fetch-fix-2026-05-01-step-1.md | 2026-05-01 15:54 | close-stranded-csv-upload-fetch-fix-2026-05-01 | 1 | Done | invoice-pulse/Done/executable-close-stranded-csv-upload-fetch-fix-2026-05-01.md |
| 16 | verdict-request-close-stranded-lessons-step-numbering-2026-05-01-step-1.md | 2026-05-01 15:45 | close-stranded-lessons-step-numbering-2026-05-01 | 1 | Done | bellows/Done/executable-close-stranded-lessons-step-numbering-2026-05-01.md |
| 17 | verdict-request-failure-3-ordering-2026-04-24-step-1.md | 2026-04-24 08:35 | failure-3-ordering-2026-04-24 | 1 | Done | bellows/Done/diagnostic-failure-3-ordering-2026-04-24.md |
| 18 | verdict-request-forge-backlog-cleanup-2026-04-23-step-2.md | 2026-04-23 09:56 | forge-backlog-cleanup-2026-04-23 | 2 | Done | forge/Done/executable-forge-backlog-cleanup-2026-04-23.md |
| 19 | verdict-request-forge-backlog-state-audit-2026-04-23-step-1.md | 2026-04-23 09:43 | forge-backlog-state-audit-2026-04-23 | 1 | Done | forge/Done/diagnostic-forge-backlog-state-audit-2026-04-23.md |
| 20 | verdict-request-forge-cycle-12-2026-04-23-step-1.md | 2026-04-23 11:03 | forge-cycle-12-2026-04-23 | 1 | Done | forge/Done/executable-forge-cycle-12-2026-04-23.md |
| 21 | verdict-request-forge-phrasing-eval-helpers-2026-04-23-step-2.md | 2026-04-23 10:17 | forge-phrasing-eval-helpers-2026-04-23 | 2 | Done | forge/Done/executable-forge-phrasing-eval-helpers-2026-04-23.md |
| 22 | verdict-request-lessons-forge-first-cycle-2026-05-01-step-1.md | 2026-05-01 12:35 | lessons-forge-first-cycle-2026-05-01 | 1 | Done | forge/Done/diagnostic-lessons-forge-first-cycle-2026-05-01.md |
| 23 | verdict-request-lessons-forge-phase2a-classify-2026-05-01-step-1.md | 2026-05-01 13:06 | lessons-forge-phase2a-classify-2026-05-01 | 1 | Done | forge/Done/executable-lessons-forge-phase2a-classify-2026-05-01.md |
| 24 | verdict-request-no-permission-denials-fix-canary-2026-04-28-step-1.md | 2026-04-28 22:01 | no-permission-denials-fix-canary-2026-04-28 | 1 | Done | bellows/Done/diagnostic-no-permission-denials-fix-canary-2026-04-28.md |
| 25 | verdict-request-no-permission-denials-read-class-fix-2026-04-28-step-2.md | 2026-04-28 21:52 | no-permission-denials-read-class-fix-2026-04-28 | 2 | Done | bellows/Done/executable-no-permission-denials-read-class-fix-2026-04-28.md |
| 26 | verdict-request-parallel-1-executable-deposit-exists-directory-paths-2026-04-30-step-2.md | 2026-04-30 16:16 | parallel-1-executable-deposit-exists-directory-paths-2026-04-30 | 2 | Done | bellows/Done/parallel-1-executable-deposit-exists-directory-paths-2026-04-30.md |
| 27 | verdict-request-parallel-1-executable-ledger-pause-reason-code-2026-04-30-step-2.md | 2026-04-30 15:50 | parallel-1-executable-ledger-pause-reason-code-2026-04-30 | 2 | Done | bellows/Done/parallel-1-executable-ledger-pause-reason-code-2026-04-30.md |
| 28 | verdict-request-parallel-plan-scope-check-collision-2026-05-01-step-1.md | 2026-05-01 10:11 | parallel-plan-scope-check-collision-2026-05-01 | 1 | Done | bellows/Done/diagnostic-parallel-plan-scope-check-collision-2026-05-01.md |
| 29 | verdict-request-parallel-plan-scope-check-collision-fix-2026-05-01-step-2.md | 2026-05-01 10:26 | parallel-plan-scope-check-collision-fix-2026-05-01 | 2 | halted | bellows/halted-executable-parallel-plan-scope-check-collision-fix-2026-05-01.md |
| 30 | verdict-request-permission-prompt-substrate-2026-04-23-step-1.md | 2026-04-23 19:44 | permission-prompt-substrate-2026-04-23 | 1 | Done | bellows/Done/diagnostic-permission-prompt-substrate-2026-04-23.md |
| 31 | verdict-request-phase-3c-plan-hash-drift-warning-2026-04-30-step-2.md | 2026-04-30 13:21 | phase-3c-plan-hash-drift-warning-2026-04-30 | 2 | Done | bellows/Done/executable-phase-3c-plan-hash-drift-warning-2026-04-30.md |
| 32 | verdict-request-planner-governance-sweep-2026-04-20-step-1.md | 2026-04-20 09:29 | planner-governance-sweep-2026-04-20 | 1 | Done | invoice-pulse/Done/diagnostic-planner-governance-sweep-2026-04-20.md |
| 33 | verdict-request-planner-governance-sweep-v4.26-2026-04-20-step-2.md | 2026-04-20 10:07 | planner-governance-sweep-v4.26-2026-04-20 | 2 | Done | invoice-pulse/Done/executable-planner-governance-sweep-v4.26-2026-04-20.md |
| 34 | verdict-request-planner-template-bellows-execution-model-section-2026-04-30-step-2.md | 2026-04-30 14:20 | planner-template-bellows-execution-model-section-2026-04-30 | 2 | Done | bellows/Done/executable-planner-template-bellows-execution-model-section-2026-04-30.md |
| 35 | verdict-request-planner-template-lessons-2026-05-01-step-2.md | 2026-05-01 10:54 | planner-template-lessons-2026-05-01 | 2 | Done | bellows/Done/executable-planner-template-lessons-2026-05-01.md |
| 36 | verdict-request-planner-template-lessons-step-numbering-2026-04-23-step-1.md | 2026-04-23 11:14 | planner-template-lessons-step-numbering-2026-04-23 | 1 | Done | bellows/Done/executable-planner-template-lessons-step-numbering-2026-04-23.md |
| 37 | verdict-request-planner-template-lessons-step-numbering-2026-04-23-step-2.md | 2026-05-01 15:56 | planner-template-lessons-step-numbering-2026-04-23 | 2 | Done | bellows/Done/executable-planner-template-lessons-step-numbering-2026-04-23.md |
| 38 | verdict-request-r3-inline-step-text-surface-2026-04-19-step-1.md | 2026-04-19 22:54 | r3-inline-step-text-surface-2026-04-19 | 1 | Done | bellows/Done/diagnostic-r3-inline-step-text-surface-2026-04-19.md |
| 39 | verdict-request-r3-shadow-cache-prompt-2026-04-19-step-2.md | 2026-04-19 23:13 | r3-shadow-cache-prompt-2026-04-19 | 2 | Done | bellows/Done/executable-r3-shadow-cache-prompt-2026-04-19.md |
| 40 | verdict-request-revert-snapshot-fix-and-reopen-backlog-2026-05-01-step-3.md | 2026-05-01 10:41 | revert-snapshot-fix-and-reopen-backlog-2026-05-01 | 3 | Done | bellows/Done/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01.md |
| 41 | verdict-request-scope-check-git-range-2026-04-22-step-1.md | 2026-04-22 15:20 | scope-check-git-range-2026-04-22 | 1 | Done | bellows/Done/diagnostic-scope-check-git-range-2026-04-22.md |
| 42 | verdict-request-scope-check-project-path-filter-2026-04-22-step-1.md | 2026-04-22 15:40 | scope-check-project-path-filter-2026-04-22 | 1 | Done | bellows/Done/executable-scope-check-project-path-filter-2026-04-22.md |
| 43 | verdict-request-session-wrap-2026-04-21-step-2.md | 2026-04-21 20:57 | session-wrap-2026-04-21 | 2 | Done | invoice-pulse/Done/executable-session-wrap-2026-04-21.md |
| 44 | verdict-request-step-state-resume-phase-3b-2026-04-28-step-2.md | 2026-04-28 22:39 | step-state-resume-phase-3b-2026-04-28 | 2 | Done | bellows/Done/executable-step-state-resume-phase-3b-2026-04-28.md |
| 45 | verdict-request-step-state-resume-phase-3b-verification-2026-04-28-step-1.md | 2026-04-28 22:24 | step-state-resume-phase-3b-verification-2026-04-28 | 1 | Done | bellows/Done/diagnostic-step-state-resume-phase-3b-verification-2026-04-28.md |
| 46 | verdict-request-stream-json-feasibility-2026-04-23-step-1.md | 2026-04-23 20:35 | stream-json-feasibility-2026-04-23 | 1 | Done | bellows/Done/diagnostic-stream-json-feasibility-2026-04-23.md |
| 47 | verdict-request-stream-json-minimal-switch-2026-04-23-step-3.md | 2026-04-23 21:12 | stream-json-minimal-switch-2026-04-23 | 3 | Done | bellows/Done/executable-stream-json-minimal-switch-2026-04-23.md |
| 48 | verdict-request-test-isolation-bleed-2026-04-21-step-1.md | 2026-04-21 20:00 | test-isolation-bleed-2026-04-21 | 1 | Done | invoice-pulse/Done/diagnostic-test-isolation-bleed-2026-04-21.md |
| 49 | verdict-request-test-isolation-conftest-fix-2026-04-21-step-2.md | 2026-04-21 20:22 | test-isolation-conftest-fix-2026-04-21 | 2 | Done | invoice-pulse/Done/executable-test-isolation-conftest-fix-2026-04-21.md |
| 50 | verdict-request-verdict-mechanization-distribution-audit-2026-04-30-step-1.md | 2026-04-30 15:08 | verdict-mechanization-distribution-audit-2026-04-30 | 1 | Done | bellows/Done/diagnostic-verdict-mechanization-distribution-audit-2026-04-30.md |
| 51 | verdict-request-verdict-only-resume-docs-2026-04-28-step-2.md | 2026-04-28 22:07 | verdict-only-resume-docs-2026-04-28 | 2 | Done | bellows/Done/executable-verdict-only-resume-docs-2026-04-28.md |

### Bucket summary

| Plan state | Unique slugs | Files | Projects |
|---|---|---|---|
| Done | 48 slugs | 50 files | bellows (33), invoice-pulse (10), forge (5), study (1), cross-project overlap with halted (1) |
| halted | 1 slug | 1 file | bellows |
| **Total** | **49 slugs** | **51 files** | |

**100% of stranded files correspond to plans in terminal state (Done or halted).** Zero active, zero missing.

---

## Q3 — Identify the gap

### The root cause: slug mismatch between verdict filenames and verdict-request filenames

Cross-referencing the 51 stranded verdict-request files against `verdicts/resolved/processed-*` reveals a **slug mismatch** in verdict filenames:

| Category | Count (files) | Description |
|---|---|---|
| **Slug mismatch** | 17 | Processed verdict uses plan-type-prefixed slug (e.g., `diagnostic-foo`) but verdict-request uses stripped slug (e.g., `foo`) |
| **No processed verdict** | 22 | No corresponding processed verdict exists; all from Apr 19–24, likely pre-v9-deployment-restart |
| **Exact slug match** | 12 | Processed verdict slug matches verdict-request slug; from Apr 28–30, likely pre-restart or matching-slug Planner runs |

### How the mismatch occurs — full trace

**Step A — verdict-request creation** (`verdict.py:83–84`):
```python
slug = slug_from_path(plan_path)  # strips "diagnostic-", "executable-" prefixes
filename = f"verdict-request-{slug}-step-{step_number}.md"
```
For plan `diagnostic-activity-based-timeout-2026-05-01.md`, slug = `activity-based-timeout-2026-05-01`.
Creates: `verdict-request-activity-based-timeout-2026-05-01-step-1.md`.

**Step B — Planner creates verdict** in `verdicts/resolved/`:
The Planner sometimes includes the plan-type prefix in the verdict filename:
`verdict-diagnostic-activity-based-timeout-2026-05-01-step-1.md`.

**Step C — `_consume_verdicts` parses slug** (`bellows.py:662–665`):
```python
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
plan_slug = match.group(1)  # = "diagnostic-activity-based-timeout-2026-05-01"
```
This captures the FULL slug including the prefix.

**Step D — pending-req-file lookup fails** (`bellows.py:669`):
```python
pending_req_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
# Constructs: verdict-request-diagnostic-activity-based-timeout-2026-05-01-step-1.md
# Actual file: verdict-request-activity-based-timeout-2026-05-01-step-1.md
# FILE NOT FOUND → scoped_decisions_path = None → falls back to all projects
```

**Step E — plan matching succeeds via substring** (`bellows.py:706`):
```python
if pname.startswith("verdict-pending-") and plan_slug in pname:
# "diagnostic-activity-based-timeout-2026-05-01" in "verdict-pending-diagnostic-activity-based-timeout-2026-05-01.md" → True
```
Plan matched = True. The verdict is consumed and plan moves to Done/halted.

**Step F — cleanup fails silently** (`bellows.py:736`):
```python
_cleanup_verdicts_for_slug(plan_slug)
# Globs for: verdict-request-diagnostic-activity-based-timeout-2026-05-01-step-*.md
# Actual file: verdict-request-activity-based-timeout-2026-05-01-step-1.md
# ZERO MATCHES → no files deleted
```

**Step G — per-step cleanup also fails** (`bellows.py:768`):
```python
pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
# Same mismatch → file doesn't exist at this path → no deletion
```

### Cascade of the slug mismatch

The mismatch is not just a cleanup problem — it also silently degrades the `scoped_decisions_path` feature (Step D). When the pending-req-file lookup fails, `_consume_verdicts` falls back to searching ALL 8 watched projects instead of the scoped project. This works by accident (substring match is lenient enough) but is fragile.

### Hypothesis evaluation

| Hypothesis | Verdict | Evidence |
|---|---|---|
| **H1** — `shutil.move` silently fails | **Rejected** | Plans successfully reach Done/; the move works. The cleanup fires BEFORE the move and fails due to slug mismatch. |
| **H2** — 4th transition path missing | **Confirmed (variant)** | Not a missing transition path per se, but the Planner's verdict filename convention creates a slug that differs from the verdict-request slug. The existing 3 call sites fire but are given the wrong slug. The slug mismatch is the functional equivalent of a missing call site. |
| **H3** — Startup sweep doesn't cover Done/ cases | **Confirmed (secondary)** | Lines 824–828 add Done/ plan slugs to `active_slugs`, so the startup sweep NEVER removes verdict-requests for completed plans. This preserves all historical stranded files across restarts. |
| **H4** — Daemon not restarted after v9 | **Partially confirmed** | 22 files from Apr 19–24 have no processed verdict, suggesting the daemon was running pre-v9 code during that period. These files persisted through subsequent restarts due to the H3 startup sweep bug. |
| **H5** — Other | **Confirmed as primary** | The slug mismatch (not identified in H1–H4 as formulated) is the primary ongoing bug. It affects all plans whose Planner verdict uses the prefixed slug convention. |

### Why the v9 fix appeared to work initially

The v9 fix was correct in design. It shipped 3 call sites and a startup sweep. At the time of the v9 diagnostic (Apr 19), the Planner was creating verdict filenames with stripped slugs (matching the verdict-request convention). The slug mismatch was introduced later when the Planner began including the plan-type prefix (`diagnostic-`/`executable-`) in verdict filenames. The mismatch is Planner-side, but the defensive fix belongs in Bellows.

---

## Q4 — Proposed minimal fix shape

### The actual fix needed

The diagnostic's candidate shapes (a) and (b) both miss the root cause. The problem is not a missing call site — the 3 call sites exist and fire correctly. The problem is that `plan_slug` in `_consume_verdicts` may differ from the slug used in verdict-request filenames.

**Recommended fix: Normalize the cleanup slug via `slug_from_path()`.**

After plan matching succeeds (`plan_matched = True`), compute a canonical cleanup slug from the matched plan's `original_name` (which has the plan-type prefix intact):

```python
cleanup_slug = verdict.slug_from_path(original_name)
```

Then use `cleanup_slug` (not `plan_slug`) in three places:

1. **Line 736** — continue-to-done: `_cleanup_verdicts_for_slug(cleanup_slug)`
2. **Line 756** — halt: `_cleanup_verdicts_for_slug(cleanup_slug)`
3. **Line 768** — per-step cleanup: `f"verdict-request-{cleanup_slug}-step-{step_number}.md"`

**Also fix the startup sweep** (line 824–828): Remove the loop that adds Done/ slugs to `active_slugs`. Done/ plans are terminal — their verdict-request files are orphans and should be swept.

### Tradeoff evaluation

| Criterion | Option (a): cleanup on every verdict consumption | Option (b): add 4th call site | **Recommended: normalize slug** |
|---|---|---|---|
| Closes mismatch bucket (17 files) | Only if slug is also fixed | Only if slug is also fixed | **Yes — directly fixes the root cause** |
| Closes pre-restart bucket (22 files) | No (startup sweep bug separate) | No | No (requires startup sweep fix, included in recommendation) |
| Closes exact-match bucket (12 files) | No (these need startup sweep fix) | No | No (requires startup sweep fix, included in recommendation) |
| LOC changed | ~3 (add call + compute slug) | ~3 | **~4** (3 slug substitutions + 1 startup sweep fix) |
| Blast radius | Low | Low | **Lowest — changes only the slug variable, not control flow** |
| Future drift risk | Medium (new call site could diverge) | Medium | **Low — slug normalization is a one-line invariant** |

**The recommended fix is the slug normalization plus startup sweep fix.** Total: ~4 lines changed, zero new call sites, zero new functions. The auto-close call site (line 420) already uses `verdict.slug_from_path(plan_path)` — this fix brings the `_consume_verdicts` call sites to parity.
