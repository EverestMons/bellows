# Bellows — Leftover-After-Ship Tooling Blueprint
**Date:** 2026-05-26 | **Tier:** diagnostic | **Dispatch Mode:** bellows | **Test Scope:** n/a | **Execution:** Step 1 (SA) | **pause_for_verdict:** always

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows claims and dispatches Step 1 to the SA agent. SA produces a script blueprint and pauses for CEO review. After CEO reviews, a separate executable will be authored for DEV implementation and QA.

## Context

Scope findings deposited at `bellows/knowledge/research/leftover-after-ship-tooling-scope-findings-2026-05-26.md`. CEO scope decision: v1 covers code-shipped pattern only (4 ground-truth recurrences enumerated in the findings, Section D, items 1-4). Output destination: `bellows/knowledge/research/backlog-freshness-check-<YYYY-MM-DD>.md` (the script deposits this when run). Natural home: `bellows/scripts/check_backlog_freshness.py`. No pytest — hand-test against the 4 ground-truth cases. Python stdlib only.

A prior larger 3-step plan was halted on Step 1 timeout (no agent output captured in 713s — likely prompt-density issue). This plan is single-step with tighter scope.

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-leftover-after-ship-tooling-blueprint-2026-05-26.md", "bellows/knowledge/decisions/in-progress-executable-leftover-after-ship-tooling-blueprint-2026-05-26.md")`. Read your specialist file and domain glossary first. Read the scope findings at `bellows/knowledge/research/leftover-after-ship-tooling-scope-findings-2026-05-26.md` — Section D contains the 4 ground-truth recurrence cases this script must catch. **After reading those, before drafting the blueprint, post a 3-5 line plan-of-attack** sketching your intended approach (parser shape, matching key choice, output structure). This is a liveness signal AND an early-steering opportunity. Then draft the blueprint. **Deliverable:** a script blueprint for `bellows/scripts/check_backlog_freshness.py` detailed enough that a DEV agent can implement it without invention. The blueprint must cover: **parsing** — exact regex or parser logic for splitting BACKLOG.md's Open section into entries, extracting each entry's date and a matching key; same for PROJECT_STATUS.md Completed entries (extract date, title, Reference slug); same for `git --no-pager log --since="<N> days ago" --pretty=format:"%h %s"` output. Recommend N=14 with brief justification. **matching algorithm** — for each Open BACKLOG entry, how to score candidates from PROJECT_STATUS Completed entries and git commit subjects. The 4 ground-truth cases share a strong signal: commit subjects contain `closes BACKLOG <name>` AND PROJECT_STATUS entries cite an executable slug in `Reference:`. Define the simplest scoring that catches all 4 without false-positives against the 6 currently-Open entries in BACKLOG. **output format** — Markdown report shape, deposited to `bellows/knowledge/research/backlog-freshness-check-<YYYY-MM-DD>.md`. Header summary (total Open scanned, candidates surfaced, no-match). One section per Open entry: its first line, candidate closures with source (PROJECT_STATUS row or git SHA+subject) and excerpt, recommended action (`investigate-as-shipped` or `no-match`). **CLI** — zero required args, optional `--window-days N` and `--output-path PATH`. Exit 0 always (informational). **constants** — module-level `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()`, derived paths for BACKLOG and PROJECT_STATUS. Match style of existing `bellows/scripts/migrate_config.py`. **ground-truth trace** — for each of the 4 recurrences (set→list, precondition-failure-field, Phase 3b read-side, mcp__vexp__) trace the matching algorithm by hand and show the candidate it would surface. **Constraints:** Python stdlib only. Read-only — no mutation outside the report deposit. Idempotent. Target size 150-250 LOC. **Deposits:**
> - `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
