# Next Session — Pick-Up Reference

**Date written:** 2026-05-05 (end of session)
**Author:** Planner

---

## TL;DR

This session shipped end-to-end deposit-parser fix at `gates.py:157` (regex extraction replacing `.strip("`")`). Diagnostic overturned the BACKLOG hypothesis — root cause was the agent-receipt parser, not the plan-text parser. 1-LOC fix + 4 unit tests + BACKLOG closure + daemon restart with new code loaded. Bellows reliability is now strong enough for invoice-pulse work; sequential single-plan dispatches recommended initially.

---

## Step 1 — Memory hygiene (30 seconds)

Memory drift identified during today's session. The `userMemories` "On the horizon" list still cites:

1. **"Fix Bellows worktree teardown (OP-001) — prerequisite for all Bellows-dispatched work"** — shipped 2026-05-03 (type fix, commit `272fbe4`) + 2026-05-04 (structural detect-and-skip, commit `06aa938`). Both closed.
2. **"deposit_exists newly-created-files false positive (new, 2026-05-03)"** — same root cause class as today's `gates.py:157` fix. Closed 2026-05-05.

Refresh "On the horizon" before opening any new work. Updated list should be:

- PATH-001 Rule 20 self-check (governance-layer; carry-forward from Open #6)
- invoice-pulse Rule 20 fabrication fix (governance-layer, high priority)
- invoice-pulse `app.py:1651-1654` live validation architectural issue (Plan 2-class fix)
- invoice-pulse stalled `base-rates-url-fix` verdict needing manual Bellows UI resolution
- freight-kb first real data run
- ai-career-digest Phase 2 (preference seeding, Obsidian path config, launchd plist)
- Forge Tier 4 prompt optimization (deferred pending more production data)

---

## Step 2 — Verify daemon state (1 minute)

The daemon was restarted at end of session 2026-05-05 with `gates.py:157` fix loaded (`Source: bellows.py @ 06aa938`). Startup sweep cleaned 11 orphaned verdict requests in one pass. Today's deposit-parser-agent-receipt-fix verdict was in that batch — clean lifecycle close.

**Quick check before any new dispatch:**

```
ls /Users/marklehn/Desktop/GitHub/bellows/verdicts/pending/
ls /Users/marklehn/Desktop/GitHub/bellows/verdicts/resolved/
```

**Expected:** `pending/` empty (or only contains active in-flight requests). `resolved/` may contain `processed-*` from end of session — fine.

If anything is stranded, flag to Planner before dispatching.

---

## Step 3 — Pick your priority

Three options ranked by pain × ease.

### Option A — Start invoice-pulse work (RECOMMENDED if invoice-pulse is the focus)

Bellows reliability is now sufficient. Three known invoice-pulse items pre-existing:

1. **Rule 20 fabrication fix** — governance-layer, high priority. Agent QA reports faking the Rule 20 self-check (writing the section header without executing the Python block). Fix shape: tighten the self-check requirement so a missing Python execution log is automatically caught.
2. **`app.py:1651-1654` live validation architectural issue** — `persist_results() → _update_validation_quality_summary()` writes to real `config.BASE_DIR` path during test runs. Plan 2-class fix.
3. **Stale `base-rates-url-fix` verdict** needing manual Bellows UI resolution. CEO action only.

**What to do:**

- Tell Planner: "let's pick up invoice-pulse — start with Rule 20 fabrication" (or one of the other two)
- Planner authors a diagnostic-first plan for items 1 or 2; item 3 is a CEO `mv` action
- Recommended pace: sequential single-plan dispatches before parallel groups, until Bellows shows clean record on real-`.git` projects

**Cost:** ~1 session per item.

### Option B — PATH-001 Rule 20 self-check (governance-layer cleanup)

PATH-001 is the recurring pattern where Rule 20 self-check scripts use `bellows/`-prefixed paths that break depending on agent cwd. Captured in `agent-prompt-feedback.md` Patterns section as OPEN, reinforced 5+ times across recent sessions. Fix shape: standardize Rule 20 self-check to use absolute paths or `pathlib.Path(__file__).resolve()`. Single governance edit + template update.

**What to do:**

- Tell Planner: "let's fix PATH-001"
- Planner writes a Tier-Small Documentation executable updating PLANNER_TEMPLATE Rule 20 spec
- DEV (Documentation Analyst) edits + QA verifies

**Cost:** ~1 session.

### Option C — BACKLOG #2 test refactor (carry-forward from prior session)

Diagnostic shipped 2026-05-05 (`bellows/knowledge/research/startup-sweep-test-refactor-surface-2026-05-05.md`) — refactor surface mapped, ~24 LOC net reduction. Low risk. Still in BACKLOG Open.

**Cost:** ~1 session.

---

## What was shipped 2026-05-05 (this session)

| Item | Status | Reference |
|------|--------|-----------|
| Bellows stability assessment for invoice-pulse work | Verbal verdict: stable enough | (in conversation) |
| Diagnostic: deposit-parser prose failure | **Done/** + findings | `Done/diagnostic-deposit-parser-prose-failure-2026-05-05.md` + `knowledge/research/deposit-parser-prose-failure-diagnosis-2026-05-05.md` |
| Executable: gates.py:157 regex extraction fix + 4 unit tests | **Done/** | `Done/executable-deposit-parser-agent-receipt-fix-2026-05-05.md` + QA report at `knowledge/qa/deposit-parser-agent-receipt-fix-qa-2026-05-05.md` |
| BACKLOG.md hygiene | Open→Closed | Entry `2026-05-05: deposit-parser captures backtick-wrapped paths from step prose` moved to Closed |
| Bellows daemon restart with new code | Loaded | Source `bellows.py @ 06aa938`; 11 orphaned verdict requests swept on startup |
| PROJECT_STATUS.md | Updated | Top entry covers fix; session-close summary entry added |

**Current Open BACKLOG count:** 13 (closed today's deposit-parser entry; net -1)

---

## Reminders carried forward

- **Bellows still has no project-local `.git`.** Detect-and-skip worktree fix means bellows-self plans run in-place. Concurrent CEO activity in `bellows/` subtree during dispatch can trip scope_check on files agent didn't touch — known-tradeoff vector. Mitigation: avoid CEO `mv`/cleanup ops in `bellows/` subtree during bellows-self dispatch.
- **KNOWLEDGE_INDEX.md still does not exist for bellows.** Same as last session — its own dedicated executable, not a session-wrap edit. Defer until invoice-pulse work has natural pause point.
- **Pre-existing 2026-05-04 stranded verdict-request files in `pending/`** are still benign-but-cluttering (close-monorepo-worktree-backlog, claude-p-prompt-suppression, bash-permission-rules-audit, backlog-addendum-scope-check-external-vector, parallel-1-diagnostic-startup-sweep-test-refactor, parallel-1-executable-planner-template-parallel-group-dispatch-subsection). CEO `mv` to `archived/` whenever convenient.

---

## How to start the next session

Open this file. Read Steps 1–2. Tell the Planner one of:

- `let's pick up invoice-pulse — start with [Rule 20 fabrication / app.py validation / base-rates verdict]` (Option A)
- `let's fix PATH-001` (Option B)
- `let's ship the BACKLOG #2 refactor` (Option C)
- something else (just describe the work)
