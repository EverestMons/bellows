# Bellows — Knowledge Index

Index of knowledge base files deposited by Bellows plans, organized by category.

---

## Development Logs (`knowledge/development/`)

### 2026-05-11
- `rule-26-evidence-path-fix-dev-log-2026-05-11.md` — DEV log for PLANNER_TEMPLATE v4.37 evidence-path tightening (Rule 26 + 3 Lessons rows; governance-root commit 75904fd)
- `backlog-hygiene-cause-5-and-daemon-logging-dev-log-2026-05-11.md` — DEV log for BACKLOG hygiene: Cause 5 RC2 closure + daemon code-version logging Open entry (bellows commits 60c56e9, 2a80b3c)

### 2026-05-10
- `startup-sweep-extract-2026-05-10.md` — DEV log for `_perform_startup_sweep` helper extraction (BACKLOG 2026-05-01 close)
- `rule-20-single-source-2026-05-10.md` — DEV log for Rule 20 self-check block single-source migration (cross-repo: governance + bellows + invoice-pulse)
- `header-parser-multiline-fix-2026-05-10.md` — DEV log for multi-line bold header parser fix + defensive default helper + warning extension
- `rule-20-self-check-wt-path-2026-05-10.md` — DEV log for rule_20_self_check wt_path threading fix
- `teardown-worktree-lock-cleanup-dev-log-2026-05-10.md` — DEV log for stale-lock detection + orphan cleanup
- `phase-1-5-lessons-source-d-dev-log-2026-05-10.md` — DEV log for PLANNER_TEMPLATE v4.35 Phase 1.5 Source D
- `s3-bug-c-halted-stale-check-dev-log-2026-05-10.md` — DEV log for halted-* stale-verdict check

### 2026-05-08
- `dev-log-qa-prefix-and-skip-logging-2026-05-08.md` — DEV log for qa- prefix dispatch fix and skip-logging advisory
- `dev-log-step2-auto-advance-fix-2026-05-08.md` — DEV log for PLANNER_TEMPLATE pause_for_verdict header + advisory warning
- `dev-log-pipe-header-parser-2026-05-08.md` — DEV log for pipe-format header parser extension in gates.py
- `diagnostic-plan-pickup-failure-findings-2026-05-08.md` — Diagnostic findings: qa- prefix not in dispatch regex whitelist
- `diagnostic-step2-auto-advance-findings-2026-05-08.md` — Diagnostic findings: header-based pause decision audit, 4/631 historical plans declared pause_for_verdict

### 2026-05-06
- `deposit-exists-worktree-aware-2026-05-06.md` — DEV log for worktree-aware deposit_exists path resolution

### 2026-05-05
- `rule-20-self-check-gate-dev-log-2026-05-05.md` — DEV log for Rule 20 self-check verification gate
- `backlog-three-reliability-entries-2026-05-06.md` — Three reliability BACKLOG entries from invoice-pulse session

### 2026-05-04
- `monorepo-worktree-fix-dev-log-2026-05-04.md` — DEV log for detect-and-skip monorepo worktree fix

### 2026-05-03
- `worktree-impl-dev-log-2026-05-03.md` — DEV log for per-plan git worktree implementation
- `worktree-tests-dev-log-2026-05-03.md` — DEV log for worktree test suite
- `worktree-teardown-type-mismatch-fix-dev-log-2026-05-03.md` — DEV log for teardown type-contract fix
- `corrective-narrow-override-dev-log-2026-05-03.md` — DEV log for narrow is_diagnostic override
- `session-wrap-2026-05-03-dev-log.md` — Session wrap development notes

---

## QA Reports (`knowledge/qa/`)

### 2026-05-11
- `rule-26-evidence-path-fix-qa-2026-05-11.md` — QA report for PLANNER_TEMPLATE v4.37 evidence-path tightening (8/8 checks; verified governance-root commit + 3 Lessons rows + Rule 26 paragraph rewrite)
- `backlog-hygiene-cause-5-and-daemon-logging-qa-2026-05-11.md` — QA report for BACKLOG hygiene (7/7 checks; section structure verified — Open entry in Open, Closed entry in Closed)

### 2026-05-10
- `startup-sweep-extract-qa-2026-05-10.md` — QA report for `_perform_startup_sweep` helper extraction (13/13 checks; gate failure on banner substitution overridden via continue verdict)
- `rule-20-single-source-qa-2026-05-10.md` — QA report for Rule 20 single-source migration (14/14 checks; Step 2 was first plan to use the new canonical pattern)
- `header-parser-multiline-fix-qa-2026-05-10.md` — QA report for multi-line bold header parser fix (13/13 checks including end-to-end test confirming fix prevents earlier-today incident)
- `rule-20-self-check-wt-path-qa-2026-05-10.md` — QA report for rule_20_self_check wt_path threading fix
- `teardown-worktree-lock-cleanup-qa-2026-05-10.md` — QA report for stale-lock detection + orphan cleanup
- `phase-1-5-lessons-source-d-qa-2026-05-10.md` — QA report for PLANNER_TEMPLATE v4.35 Phase 1.5 Source D
- `s3-bug-c-halted-stale-check-qa-2026-05-10.md` — QA report for halted-* stale-verdict check

### 2026-05-09
- `s3-verdict-fix-qa-2026-05-09.md` — QA report for S3 verdict-resolved retry loop fix (Bugs A and B)

### 2026-05-08
- `qa-bellows-qa-prefix-and-skip-logging-2026-05-08.md` — QA report for qa- prefix dispatch fix
- `qa-bellows-qa-prefix-and-skip-logging-deliverable-verification-2026-05-08.md` — Deliverable verification for qa- prefix fix
- `qa-pipe-header-parser-and-comprehensive-2026-05-08.md` — Comprehensive QA report covering all three 2026-05-08 changes (Fix A + Fix B + parser)
- `qa-pipe-header-parser-deliverable-verification-2026-05-08.md` — Deliverable verification for pipe-format header parser

### 2026-05-06
- `deposit-exists-worktree-aware-qa-2026-05-06.md` — QA for worktree-aware deposit path resolution
- `failure-3-mode-a-closure-qa-2026-05-06.md` — QA for Failure 3 Mode A closure

### 2026-05-05
- `rule-20-self-check-gate-qa-report-2026-05-05.md` — QA for Rule 20 self-check gate
- `rule-22e-rule-20-tightening-qa-report-2026-05-05.md` — QA for Rule 22e tightening
- `backlog-1-close-and-lessons-qa-2026-05-05.md` — QA for BACKLOG #1 close and lessons
- `session-wrap-qa-2026-05-05.md` — Session wrap QA
- `deposit-parser-agent-receipt-fix-qa-2026-05-05.md` — QA for deposit-parser agent-receipt fix

---

## QA Evidence Directories (`knowledge/qa/evidence/`)

### 2026-05-11
- `rule-26-evidence-path-fix-2026-05-11/` — Evidence for PLANNER_TEMPLATE v4.37 edits (8 files: 6 grep checks for version + tightened guidance + prohibition + 3 Lessons rows, markdown_wellformed.txt, git_log.txt)
- `backlog-hygiene-cause-5-and-daemon-logging-2026-05-11/` — Evidence for BACKLOG hygiene (7 files: 5 grep checks for Closed/Open entries + audit references + commit SHA + executable reference, section_structure.txt, git_log.txt)

### 2026-05-10
- `header-parser-multiline-fix-2026-05-10/` — Evidence for multi-line bold header parser fix (3 files: `repl-fixture-output.txt`, `test-suite-result.txt`, `code-grep-results.txt`)
- `header-parser-canary-2026-05-10/` — Live smoke-test evidence post-daemon-restart (2 files: `marker.txt`, `step2-confirm.txt`)

### 2026-05-09
- `executable-s3-verdict-resolved-retry-loop-fix-2026-05-09/pytest_full.txt` — Full pytest evidence for S3 verdict fix

### 2026-05-08
- `pipe-header-parser/` — Evidence for pipe-format header parser comprehensive QA (7 files: `end_to_end_pause_decision.txt`, `parser_extracts_pause.txt`, `pytest_full.txt`, `pytest_targeted.txt`, `this_plan_self_test.txt`, `warning_correctness.txt`, `yaml_regression.txt`)
- `qa-prefix-and-skip-logging/` — Evidence for qa- prefix dispatch fix QA (6 files: `lifecycle_silent_skip.txt`, `pytest_full.txt`, `pytest_targeted.txt`, `regex_acceptance.txt`, `roadmap_silent_skip.txt`, `skip_logging_dedup.txt`)

---

## Research (`knowledge/research/`)

### 2026-05-11
- `deposit-exists-false-positive-audit-2026-05-11.md` — Population audit: 14 reproductions across 8 verdict requests, classified by candidate cause. Cause 1 confirmed closed (commit 2016d02, 2026-05-06); Cause 5 (plan-agent evidence path convention mismatch) identified as dominant unresolved class — 18 gate-failure lines across 3 verdict requests. Recommended fix shape: standardize plan-authored evidence paths to use full project-relative paths (governance, not code).
- `rule-26-directory-bullet-canary-2026-05-11.md` — Canary diagnostic: confirmed current gate accepts directory-only `**Deposits:**` bullets via `os.path.isfile() or os.path.isdir()` at every resolution strategy (gates.py:183-212). Identified commit e609ad3 (2026-04-30, BACKLOG #11 closure) as making the 2026-04-19 "isfile()-only" Lessons entry stale.

### Earlier
- `agent-prompt-feedback.md` — Running log of agent prompt observations and patterns (2026-05-10 late-evening entry covers today's three-closure session)
- `rule-20-block-sourcing-migration-surface-2026-05-10.md` — Diagnostic: Rule 20 block sourcing migration surface (mapped canonical block, ~30% drift rate, governance-tree population)
- `header-parser-multiline-bold-gap-2026-05-10.md` — Diagnostic: multi-line bold header parser gap (REPL fixtures confirmed root cause, 3 affected plans all in Done/, Shape g defensive default surfaced)
- `gate-path-resolution-post-teardown-2026-05-10.md` — Diagnostic: gate path-resolution post-teardown timing (overturned BACKLOG hypothesis)
- `teardown-worktree-reliability-2026-05-10.md` — Diagnostic: teardown worktree reliability (stale-lock as only real bug)
- `in-progress-rename-verification-2026-05-10.md` — Diagnostic: in-progress rename verification (overturned rename bug hypothesis)
- `inactivity-timeout-investigation-2026-05-10.md` — Diagnostic: inactivity timeout investigation (threshold mismatch, not code defect)
- `s3-done-stale-check-verification-2026-05-10.md` — Diagnostic: S3 Done/ stale-check verification (present since 2026-04-24)
- `s3-verdict-resolved-retry-loop-findings-2026-05-09.md` — Diagnostic findings for S3 verdict-resolved retry loop (Bugs A, B, C)
- `worktree-teardown-bug-diagnosis-2026-05-03.md` — Teardown type-contract violation diagnosis
- `worktree-implementation-surface-2026-05-03.md` — Worktree implementation surface mapping
- `worktree-candidate-designs-2026-05-03.md` — Worktree candidate designs D1-D8
- `worktree-cost-coverage-recommendation-2026-05-03.md` — Worktree cost-coverage recommendation
- `extract-total-steps-undercount-2026-05-03.md` — Multi-step diagnostic parser undercount diagnosis
- `deposit-parser-prose-failure-diagnosis-2026-05-05.md` — Deposit parser prose failure root cause
- `failure-3-mode-a-occurrence-investigation-2026-05-06.md` — Failure 3 Mode A occurrence investigation
- `failure-3-mode-a-closure-design-2026-05-06.md` — Failure 3 Mode A closure design

---

## Architecture (`knowledge/architecture/`)

- `step-state-resume-design-2026-04-28.md` — Step state resume design (Phase 3a/3b/3c)
- `failure-3-ordering-2026-04-24.md` — Failure 3 gate ordering analysis

---

## Documentation (`knowledge/documentation/`)

- `session-wrap-log-2026-05-10.md` — Session wrap summary log for 2026-05-10 late evening (three back-to-back closures + live smoke canary)
- `session-wrap-log-2026-05-08.md` — Session wrap summary log for 2026-05-08 reliability triple-ship

---

## Cross-References (Governance Root)

- `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` — Canonical Rule 20 self-check Python block (single-source as of 2026-05-10). Referenced by PLANNER_TEMPLATE.md Rule 20, `bellows/agents/BELLOWS_QA.md`, `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md`.
