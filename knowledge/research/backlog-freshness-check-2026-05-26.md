# BACKLOG Freshness Check — 2026-05-26

**Window:** 14 days | **Open entries scanned:** 6 | **Candidates surfaced:** 6 | **No-match:** 0

---

## Entry 1: Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md` (sequential-...

**Filed:** 2026-05-22 | **Action:** investigate-as-shipped

### Candidates

- **[git]** `d2e07a9` — `research(bellows): BACKLOG freshness-check script blueprint — 4-source matching algorithm (git log, PROJECT_STATUS, BACKLOG Closed, BACKLOG Open), ground-truth traces for all 4 recurrences`
  Match terms: project, project_status, status
- **[backlog_closed]** 2026-05-10 — `_teardown_worktree` cherry-pick fragility (originally 2026-05-07). SA diagnosti
  Match terms: cherry, cherry-pick, teardown, worktree
- **[backlog_closed]** 2026-05-06 — BACKLOG #1 (`deposit_exists` gate reports plan-required deposits as missing when
  Match terms: project, worktree
- **[backlog_closed]** 2026-05-04 — `2026-05-04: monorepo-worktree-at-governance-root structural fix`. Shipped via `
  Match terms: project, worktree
- **[backlog_closed]** 2026-05-03 — worktree teardown crash. Diagnostic at `knowledge/research/worktree-teardown-bug
  Match terms: teardown, worktree

---

## Entry 2: Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files at teardow...

**Filed:** 2026-05-22 | **Action:** investigate-as-shipped

### Candidates

- **[backlog_closed]** 2026-05-26 — Teardown push silently fails on long-running plans (originally 2026-05-24). Reti
  Match terms: diagnostic, teardown
- **[backlog_closed]** 2026-05-21 — `_consume_verdicts` did not drain two valid `resolved/` verdict files across mul
  Match terms: diagnostic, files
- **[backlog_closed]** 2026-05-12 — bellows-self parallel/concurrent activity exposure (originally 2026-05-05). Clos
  Match terms: diagnostic, parallel
- **[backlog_closed]** 2026-05-10 — Stranded plan/verdict files in invoice-pulse `knowledge/decisions/` (originally 
  Match terms: diagnostic, files, invoice-pulse
- **[backlog_closed]** 2026-05-10 — `_teardown_worktree` cherry-pick fragility (originally 2026-05-07). SA diagnosti
  Match terms: cherry, cherry-pick, diagnostic, teardown
- **[backlog_closed]** 2026-05-10 — deposit_exists / rule_20_self_check gate path-resolution gap recurred on action 
  Match terms: diagnostic, teardown
- **[backlog_closed]** 2026-05-06 — BACKLOG #1 (`deposit_exists` gate reports plan-required deposits as missing when
  Match terms: diagnostic, files
- **[backlog_closed]** 2026-05-03 — worktree teardown crash. Diagnostic at `knowledge/research/worktree-teardown-bug
  Match terms: diagnostic, teardown

---

## Entry 3: Bellows status UI — replace terminal-only output as the primary observability su...

**Filed:** 2026-05-21 | **Action:** investigate-as-shipped

### Candidates

- **[git]** `d2e07a9` — `research(bellows): BACKLOG freshness-check script blueprint — 4-source matching algorithm (git log, PROJECT_STATUS, BACKLOG Closed, BACKLOG Open), ground-truth traces for all 4 recurrences`
  Match terms: bellows, status
- **[backlog_closed]** 2026-05-12 — Terminal output redesign + notification audit (originally 2026-04-19). Shipped a
  Match terms: output, terminal
- **[backlog_closed]** 2026-05-11 — Daemon code-version observability gap (originally 2026-05-11). Shipped via `exec
  Match terms: bellows, observability

---

## Entry 4: Deposits parser does not strip parenthetical qualifiers (Priority 3 audit). `_ex...

**Filed:** 2026-05-21 | **Action:** investigate-as-shipped

### Candidates

- **[git]** `4e805fa` — `fix(gates): _extract_plan_required_deposits set→list — deterministic md_paths[0] selection — closes BACKLOG capability`
  Match terms: _extract_plan_required_deposits, deposits
- **[git]** `a5b9a33` — `docs: close Priority 3 carry-over audit (BACKLOG +3, NEXT_SESSION retired)`
  Match terms: audit, priority
- **[project_status]** 2026-05-25 — `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
  Match terms: deposits, extract, plan, required
- **[project_status]** 2026-05-27 — `executable-deposit-exists-path-form-normalization-2026-05-27`
  Match terms: deposit, exists, path
- **[backlog_closed]** 2026-05-26 — `_extract_plan_required_deposits()` returns a `set` making `md_paths[0]` hash-de
  Match terms: _extract_plan_required_deposits, deposits
- **[backlog_closed]** 2026-05-11 — `deposit_exists` Cause 5 — plan-agent evidence path convention mismatch. Closure
  Match terms: _extract_plan_required_deposits, deposits
- **[backlog_closed]** 2026-04-28 — BACKLOG #5 (deposit parser gap for Rule 26 block form, originally 2026-04-19) cl
  Match terms: deposits, parser
- **[backlog_closed]** 2026-04-19 — deposit-path parser false positives (originally 2026-04-18, BACKLOG #6) resolved
  Match terms: _extract_plan_required_deposits, deposits, parser

---

## Entry 5: No-match verdict warning rate-limit (Priority 3 audit). `_consume_verdicts` at `...

**Filed:** 2026-05-21 | **Action:** investigate-as-shipped

### Candidates

- **[git]** `a5b9a33` — `docs: close Priority 3 carry-over audit (BACKLOG +3, NEXT_SESSION retired)`
  Match terms: audit, priority
- **[project_status]** 2026-05-25 — `executable-file-change-audit-fix-2026-05-25`
  Match terms: audit, file
- **[project_status]** 2026-05-21 — `executable-bellows-verdict-enrichment-2026-05-21`
  Match terms: bellows, verdict
- **[backlog_closed]** 2026-05-26 — Step 2 (final-step) gate_failure pause does NOT rename in-progress-* to verdict-
  Match terms: verdict, verdict-pending
- **[backlog_closed]** 2026-05-26 — Daemon-restart recovery shape — in-progress-* plans with verdict in resolved/ no
  Match terms: match, resolved/, verdict
- **[backlog_closed]** 2026-05-21 — `_consume_verdicts` did not drain two valid `resolved/` verdict files across mul
  Match terms: _consume_verdicts, resolved/, verdict
- **[backlog_closed]** 2026-05-10 — S3 Bug C — stale-verdict check does not search `halted-*` plans (originally 2026
  Match terms: _consume_verdicts, verdict
- **[backlog_closed]** 2026-05-10 — Plan filename not flipped from in-progress- to verdict-pending- on pause (origin
  Match terms: verdict, verdict-pending
- **[backlog_closed]** 2026-04-24 — Reliability bugs 1, 2, 3 (originally 2026-04-24) shipped via `executable-bellows
  Match terms: _consume_verdicts, match, verdict

---

## Entry 6: `_extract_step_text` regex case-sensitivity — canary plan header convention seco...

**Filed:** 2026-05-13 | **Action:** investigate-as-shipped

### Candidates

- **[project_status]** 2026-05-26 — `executable-planner-template-rule-21-contract-change-2026-05-26`
  Match terms: planner, rule, template
- **[project_status]** 2026-05-25 — `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
  Match terms: extract, plan
- **[project_status]** 2026-05-21 — `executable-planner-template-rule-25-codification-2026-05-21`
  Match terms: planner, rule, template
- **[project_status]** 2026-05-21 — `executable-planner-template-no-push-and-routing-count-2026-05-21`
  Match terms: planner, template
- **[project_status]** 2026-05-13 — `executable-plan-write-time-lessons-reread-2026-05-13`
  Match terms: lessons, plan
- **[backlog_closed]** 2026-05-11 — `deposit_exists` Cause 5 — plan-agent evidence path convention mismatch. Closure
  Match terms: convention, extract, regex

---
