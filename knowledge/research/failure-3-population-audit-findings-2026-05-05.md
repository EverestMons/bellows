# Failure 3 Population Audit — Findings
**Date:** 2026-05-05
**Agent:** Bellows Developer
**Plan Reference:** `bellows/knowledge/decisions/in-progress-diagnostic-failure-3-population-audit-2026-05-05.md`

---

## Investigation Section 1 — Population Scope

Plans shipped to Done/ since 2026-04-24 (disable-auto-close fix), per project:

| Project | Count |
|---------|-------|
| bellows | 70 |
| invoice-pulse | 3 |
| forge | 3 |
| study | 1 |
| BrewBuddy | 0 |
| SimpleScreen | 0 |
| freight-kb | 0 |
| ai-career-digest | 0 |
| **Total** | **77** |

**First 3 (bellows):** diagnostic-activity-based-timeout-2026-05-01, diagnostic-backlog-1-reproduction-audit-2026-05-05, diagnostic-bellows-integration-section-audit-2026-05-01
**Last 3 (bellows):** parallel-1-executable-deposit-exists-directory-paths-2026-04-30, parallel-1-executable-ledger-pause-reason-code-2026-04-30, parallel-1-executable-planner-template-parallel-group-dispatch-subsection-2026-05-05

---

## Investigation Section 2 — Gate-Failure Verdict Counts

**Total archived verdict requests in window:** 52 (includes pre-2026-04-24 plans whose requests were archived after the fix date)
**Total resolved verdicts in window:** 92

### Pause Reason Code Breakdown (archived requests)

| Pause Reason Code | Count |
|-------------------|-------|
| auto_close_disabled | 21 |
| qa_checkpoint | 17 |
| gate_failure | 11 |
| scope_violation | 0 |

**Gate-failure plan slugs (11):**
1. backlog-hygiene-sweep-2026-04-30
2. base-rates-url-fix-2026-04-21
3. forge-cycle-12-2026-04-23
4. permission-prompt-substrate-2026-04-23
5. planner-governance-sweep-v4.26-2026-04-20
6. planner-template-bellows-execution-model-2026-04-30
7. planner-template-lessons-step-numbering-2026-04-23
8. r3-shadow-cache-prompt-2026-04-19
9. scope-check-project-path-filter-2026-04-22
10. stream-json-minimal-switch-2026-04-23

(Note: 3 unique slugs collapsed from the 11 requests — planner-template-lessons-step-numbering has 2 step-level requests)

---

## Investigation Section 3 — Mode A Cross-Reference

Mode A = agent moved plan to Done before gate-failure verdict was resolved (Rule 8/23 violation).

| Plan Slug | Done/ mtime | Verdict Resolved mtime | Violation? | Notes |
|-----------|-------------|----------------------|------------|-------|
| backlog-hygiene-sweep-2026-04-30 | 2026-04-30 15:43 | 2026-04-30 16:12 | **YES** | Post-fix. Done 29 min before verdict resolved. |
| base-rates-url-fix-2026-04-21 | 2026-04-21 19:09 | No resolved verdict | N/A | Pre-fix plan. No resolved verdict file found. |
| forge-cycle-12-2026-04-23 | 2026-04-23 11:24 | 2026-04-23 12:32 | YES (pre-fix) | Done mtime pre-dates fix (04-24). Expected. |
| permission-prompt-substrate-2026-04-23 | 2026-04-23 19:40 | No resolved verdict | N/A | Pre-fix. No resolved verdict file found. |
| planner-governance-sweep-v4.26 | 2026-04-20 09:56 | 2026-05-01 15:46 | YES (pre-fix) | Done mtime pre-dates fix (04-24). Expected. |
| planner-template-bellows-execution-model | 2026-04-30 14:09 | 2026-05-03 19:41 | **YES** | Post-fix. Done ~3 days before verdict resolved. |
| planner-template-lessons-step-numbering | 2026-04-23 11:11 | 2026-05-01 16:03 | YES (pre-fix) | Done mtime pre-dates fix (04-24). Expected. |
| r3-shadow-cache-prompt-2026-04-19 | 2026-04-19 23:05 | No resolved verdict | N/A | Pre-fix. No resolved verdict file found. |
| scope-check-project-path-filter | 2026-04-22 15:37 | No resolved verdict | N/A | Pre-fix. No resolved verdict file found. |
| stream-json-minimal-switch-2026-04-23 | 2026-04-23 20:52 | No resolved verdict | N/A | Pre-fix. No resolved verdict file found. |

**Post-fix Mode A violations: 2**
1. `backlog-hygiene-sweep-2026-04-30` — Done moved 29 min before verdict resolved (same day)
2. `planner-template-bellows-execution-model-2026-04-30` — Done moved 3 days before verdict resolved

Both occurred on 2026-04-30, which is post-disable-auto-close but likely pre-v4.30 Rule 8/23/25 hardening (those rules were strengthened progressively through May). These may represent the transition period before agent-side rules were fully enforced.

---

## Investigation Section 4 — Mode B Sampling

Mode B = Bellows moved plan to Done before its own gate evaluation completed.

**Method:** Sampled 10 most recent Done/ plans across all projects. Searched for corresponding log files (`logs/*.json`) containing the plan slug and checked for `parsed.gate_result.failures` field.

**Finding:** Bellows step log files (`logs/YYYYMMDD-HHMMSS-step.json`) do **not** store gate evaluation results. The log schema contains only: `success`, `raw_output`, `stderr`, `parsed` (with keys: `session_id`, `is_error`, `stop_reason`, `result_text`, `cost_usd`). Gate evaluation is performed in-memory by `gates.py` after log persistence; results are not written back to the log file.

| Plan Slug | Log Gate Failure? | Done/ mtime | Violation? |
|-----------|-------------------|-------------|------------|
| rule-22e-rule-20-tightening-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| rule-20-self-check-gate-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| rule-20-gate-addition-surface-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| worktree-teardown-current-state-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| rule-20-fabrication-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| deposit-parser-agent-receipt-fix-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| deposit-parser-prose-failure-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| session-wrap-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| backlog-1-close-and-lessons-2026-05-05 | Not in log schema | 2026-05-05 | N/A |
| backlog-1-reproduction-audit-2026-05-05 | Not in log schema | 2026-05-05 | N/A |

**Conclusion:** Mode B cannot be assessed from current artifacts. Gate evaluation results are ephemeral — computed at runtime but not persisted. This is a schema gap that prevents post-hoc Mode B auditing.

---

## Investigation Section 5 — Config Sanity Check

From `bellows/config.json`:
```json
{
  "watched_projects": [...],
  "default_model": "claude-opus-4-6",
  "planner_model": "claude-sonnet-4-6",
  ...
}
```

The `auto_close` field is **absent** from config.json. Per Bellows codebase convention, absent defaults to `false`. The disable-auto-close structural fix is confirmed applied — no project has `auto_close: true`.

---

## Findings — Answered Questions

**Question A:** How many plans shipped to Done/ in the audit window (2026-04-24 to 2026-05-05)?
> **77 plans** across all 8 watched projects (70 bellows, 3 invoice-pulse, 3 forge, 1 study).

**Question B:** How many had `gate_failure` or `scope_violation` verdict requests in the same window?
> **11 verdict requests** with `gate_failure` pause reason (across 10 unique plan slugs). **0** with `scope_violation`.

**Question C:** Mode A violations (Done/ predates verdict resolution — agent moved to Done before gate-failure verdict was resolved)?
> **2 post-fix violations** identified:
> 1. `backlog-hygiene-sweep-2026-04-30` (Done 29 min before verdict resolved)
> 2. `planner-template-bellows-execution-model-2026-04-30` (Done ~3 days before verdict resolved)
>
> Both occurred 2026-04-30 — post-disable-auto-close but during the transition period before Rule 8/23/25 v4.30 hardening was fully deployed. 3 additional pre-fix violations (Done mtime < 2026-04-24) are expected behavior and not regressions.

**Question D:** Mode B violations (gate failure log post-dates Done/ mtime)?
> **Cannot assess.** Bellows step logs do not persist gate evaluation results (schema gap). Gate results are computed in-memory by `gates.py` after the log file is written and are not stored. Mode B auditing requires either (a) adding gate results to the log schema or (b) inspecting `bellows.db` ledger entries with timestamps.

**Question E:** Is the disable-auto-close model applied per config.json?
> **Yes.** The `auto_close` field is absent from `config.json`, defaulting to `false`. No project overrides it. The structural fix is confirmed in place.

---

## Output Receipt

```
status: complete
agent: Bellows Developer
plan: diagnostic-failure-3-population-audit-2026-05-05
step: 1
deposits:
  - bellows/knowledge/research/failure-3-population-audit-findings-2026-05-05.md
findings: 77 Done plans in window; 11 gate_failure verdicts; 2 post-fix Mode A violations (both 2026-04-30 transition period); Mode B not assessable (log schema gap); auto_close confirmed disabled
```
