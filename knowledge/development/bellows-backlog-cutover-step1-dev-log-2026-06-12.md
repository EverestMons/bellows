# Bellows BACKLOG Register Cutover — Step 1 Dev Log
**Date:** 2026-06-12 | **Plan:** 17 | **Agent:** Bellows Documentation Analyst | **Step:** 1

---

## Part A — Per-Entry Classification Table

### Open Section (24 entries)

| # | Date | Short title | Section | Classification | Justification |
|---|---|---|---|---|---|
| 1 | 2026-06-12 | Concurrent-daemon startup recovery race | Open | truly-open | No shipped/closed annotation; root-cause diagnostic queued |
| 2 | 2026-06-12 | `plans.lifecycle_state` intermediate states never written | Open | truly-open | No shipped/closed annotation; either-or disposition pending |
| 3 | 2026-06-11 | Persist partial agent output on inactivity-timeout kill | Open | truly-open | No shipped/closed annotation; fix shape described but unimplemented |
| 4 | 2026-06-08 | Deposits written to non-auto-staged directories | Open | closed-inline | `SHIPPED 2026-06-10` in title + `**FIX:** shipped both shapes` — no residual |
| 5 | 2026-06-08 | `scope_check` continuous-run multi-step FP | Open | truly-open | No shipped/closed annotation; fix shape described |
| 6 | 2026-06-08 | `stop_prose` WARN on error-handling prose | Open | truly-open | No shipped/closed annotation; severity very low, log noise |
| 7 | 2026-06-06 | `__file__`-relative root resolution worktree breakage | Open | shipped-with-open-residual | `Status 2026-06-08 (audit + Plan A SHIPPED)` — runner.py converted, but CEO disposition defers 3 latent instances (`bellows.py:23`, `planner.py:11`, `verdict.py:13`) |
| 8 | 2026-06-06 | 16 stale `halted-*` plans cluttering `decisions/` | Open | closed-inline | `Status 2026-06-08 (DONE — archived)` — all 16 moved to `archived-halted-plans/` |
| 9 | 2026-06-01 | QA report U+FFFD mojibake in verification table | Open | truly-open | No shipped/closed annotation; cosmetic, single-cell fix pending |
| 10 | 2026-05-31 | Worktree teardown→resume regression (family entry) | Open | shipped-with-open-residual | Gaps 1(b), 1(c), 2(a), teardown-(b) all SHIPPED; residual: Gap 2(b)/(c) auto-resume + Gap 3 auto-stash, both DEFERRED (friction-reduction only) |
| 11 | 2026-05-30 | Worktree re-creation on resume checks out `main` HEAD | Open | truly-open | No inline shipped/closed annotation; fix shape options described but unimplemented; subsumed into family (entry 10) but no closure marker on this entry |
| 12 | 2026-05-29 | `scope_check` blueprint-delegation FP | Open | truly-open | No shipped/closed annotation; sibling directory-mention FP shipped but this half remains open |
| 13 | 2026-05-29 | `stop_prose` matches PLANNER_TEMPLATE step-control language | Open | truly-open | No shipped/closed annotation; recurrence noted 2026-06-03 |
| 14 | 2026-05-28 | `stop_prose` "do not proceed" inside instructional prose | Open | truly-open | No shipped/closed annotation; regex anchoring fix described |
| 15 | 2026-05-28 | Pre-deposit plan-lint script | Open | truly-open | No shipped/closed annotation; deferred until 4th occurrence |
| 16 | 2026-05-27 | Verdict-response filename prefix tolerance | Open | truly-open | No shipped/closed annotation; investigation pending |
| 17 | 2026-05-27 | `lessons-forge.db` tracked-but-gitignored disposition | Open | truly-open | No shipped/closed annotation; CEO decision fork between options a/b |
| 18 | 2026-05-27 | Orphan-guard renormalization fires on wrong step | Open | closed-inline | `[RETIRED 2026-05-31 → moved to Closed; premise overturned, renormalization site absent in current code, removed by c2aeef4]` |
| 19 | 2026-05-22 | Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md` | Open | truly-open | No shipped/closed annotation; fix shape options described |
| 20 | 2026-05-22 | Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files | Open | truly-open | No shipped/closed annotation; deferred pending second occurrence |
| 21 | 2026-05-21 | Bellows status UI | Open | truly-open | No shipped/closed annotation; CEO design shape decision pending |
| 22 | 2026-05-21 | Deposits parser parenthetical qualifiers (Priority 3) | Open | truly-open | No shipped/closed annotation; deferred until incident |
| 23 | 2026-05-21 | No-match verdict warning rate-limit | Open | closed-inline | `[SHIPPED 2026-05-31 → moved to Closed.]` |
| 24 | 2026-05-13 | `_extract_step_text` regex case-sensitivity | Open | truly-open | No shipped/closed annotation; governance rule prevents at plan-write time, Bellows fix deferred |

### Closed Section (107 entries)

All 107 entries in the `## Closed` section carry explicit `**Closed YYYY-MM-DD:**` prefixes with closure annotations. Zero misfiled-open entries found (per Stage-3 precedent check: every entry describes completed/shipped/retired work with resolution details).

Closed entries span 2026-04-19 through 2026-06-05. Full list preserved byte-identical in `BACKLOG-ARCHIVE.md`.

### Totals

| Classification | Count | Migrates to FORWARD.md? |
|---|---|---|
| truly-open | 18 | Yes (as-is) |
| shipped-with-open-residual | 2 | Yes (as residual) |
| closed-inline | 4 | No |
| misfiled-open | 0 | N/A |
| closed (Closed section) | 107 | No |
| **Total entries** | **131** | **20 open-class → FORWARD.md** |

### Divergence from Diagnostic Survey

The diagnostic (Section 1) estimated: "~24 entries in Open section, ~10 in Closed" yielding "~20 open, ~14 closed."

- **Open-class count matches:** diagnostic's ~20 = my exact 20.
- **Closed-class count diverges massively:** diagnostic's "~10 in Closed" = 107 actual. The diagnostic's approximate survey counted ~10 entries in the Closed section; the true count is 107. This is because the diagnostic performed a summary survey ("lines: 284, ~20 open, ~14 closed") rather than an exhaustive per-entry enumeration. The Section 1 note "approximate" is accurate — the approximation was heavily biased toward the Open section where entry boundaries are clearer (shorter entries, simpler patterns).
- **4 closed-inline in Open matches:** diagnostic noted "~4 carry SHIPPED/RETIRED/DONE inline annotations" = exactly 4 found.

---

## Part B — Register Files Created

### FORWARD.md

- **Path:** `knowledge/FORWARD.md`
- **Format:** diagnostic Section 4 spec verbatim (title `# Bellows — Forward Register`, standing-queue preamble blockquote, 6-column table `| # | Added | Item | Type | Plan-id link | Status |`)
- **Rows:** 20 entries, chronological (#1 = 2026-05-13, #20 = 2026-06-12)
- **Types:** 18 `deferred-work`, 2 `ceo-decision-fork` (#2 Bellows status UI, #7 lessons-forge.db disposition)
- **Plan-id links:** all `—` (no entry explicitly references a plan authored for the work itself; shipped fixes were via plans that closed other entries, not plans targeting these open items)

### BACKLOG-ARCHIVE.md

- **Path:** `knowledge/BACKLOG-ARCHIVE.md`
- **Format:** frozen header block (title + blockquote + `---`) prepended to byte-identical BACKLOG.md content
- **Original BACKLOG.md:** 182,856 bytes
- **Archive total:** 183,208 bytes (352-byte header prepended)

---

## Confirmations

### BACKLOG.md untouched

```
$ git status
On branch bellows-wt/17
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	knowledge/BACKLOG-ARCHIVE.md
	knowledge/FORWARD.md

nothing added to commit but untracked files present (use "git add" to track)
```

BACKLOG.md does not appear in git status — no modifications, no staging, no deletions.

---

## Output Receipt
**Agent:** Bellows Documentation Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Classified all 131 BACKLOG.md entries across Open (24) and Closed (107) sections into 5 classes. Created FORWARD.md with 20 open-class entries in diagnostic Section 4 format. Created BACKLOG-ARCHIVE.md with byte-identical BACKLOG.md content under a frozen header.

### Files Deposited
- `knowledge/FORWARD.md` — 20-row forward register replacing BACKLOG.md Open section
- `knowledge/BACKLOG-ARCHIVE.md` — frozen read-only archive of full BACKLOG.md content
- `knowledge/development/bellows-backlog-cutover-step1-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- None (documentation-only step)

### Decisions Made
- Classified entry 11 (worktree re-creation, 2026-05-30) as truly-open despite being subsumed into the family entry (entry 10) — the entry itself carries no inline closure marker
- Classified entry 10's residual as shipped-with-open-residual: Gap 2(b)/(c) + Gap 3 are the migrated residuals
- Classified entry 7's residual as shipped-with-open-residual: 3 latent `__file__` instances are the migrated residuals
- Typed #2 (Bellows status UI) and #7 (lessons-forge.db disposition) as `ceo-decision-fork` — both park explicit CEO design/disposition decisions
- All Plan-id links set to `—`: no entry references a plan authored specifically for its own work

### Flags for CEO
- FORWARD.md is ready for human review before Step 2 trim

### Flags for Next Step
- Step 2 performs `git rm knowledge/BACKLOG.md` — FORWARD.md and BACKLOG-ARCHIVE.md must be committed first
