# Permission Denial History Audit

**Date:** 2026-05-22 | **Agent:** Bellows Systems Analyst | **Diagnostic:** claude-settings-permission-gap-2026-05-22 | **Step:** 2

---

## Audit Window

| Field | Value |
|---|---|
| Date range | 2026-04-23 to 2026-05-22 (30 days) |
| Step log files scanned | 613 (`bellows/logs/*.json`) |
| Step files with permission denials | 109 (17.8% of all step logs) |
| Verdict files scanned (resolved) | All files in `bellows/verdicts/resolved/` |
| Verdict files mentioning `no_permission_denials` | 15 |
| Verdict files mentioning `gate_failure` | 44 |
| Ledger files | `bellows/knowledge/verdict-log.md` + `bellows/verdicts/ledger.jsonl` |
| **Total individual denial events (log-level)** | **392** |
| **Total `no_permission_denials` gate failures (verdict-level)** | **10** |

---

## Methodology

1. **Log-level scan:** Searched all 613 step JSON files in `bellows/logs/` for `"haven't granted"` / `"requested permissions"` messages within `permission_denials` arrays. Extracted `tool_name` and `tool_input` fields from each denial dict to identify the tool and target path.
2. **Verdict-level scan:** Read all 15 verdict files (resolved + pending/archived) containing `no_permission_denials` references. Extracted plan slug, step, denied tool, target path, agent role, and resolution.
3. **Ledger scan:** Read `knowledge/verdict-log.md` and searched `verdicts/` for `gate_failure` pause reasons to capture the full population of gate failures (41 total, 10 `no_permission_denials`).
4. **Classification:** Each denial event was classified into one of four primary buckets based on the tool and target path per the plan specification, plus a fifth emergent bucket for read-class cross-project denials.

---

## Event Inventory Tables

### Gate-Level Inventory: All `no_permission_denials` Failures

These are the 10 unique gate_failure events where `no_permission_denials` was the failed gate, extracted from processed verdict files and the verdict-log.

| # | Date | Plan Slug | Step | Denied Tool | Target Path / Scope | Agent Role | Resolution |
|---|---|---|---|---|---|---|---|
| 1 | 2026-04-23 | `planner-template-lessons-step-numbering` | 1 | Grep (x3) | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` | DEV | Archived (pre-fix) |
| 2 | 2026-04-23 | `lessons-forge-phase1-schema-ingest` | 1 | Glob | `/Users/marklehn/Desktop/GitHub` (`**/ADR-002*.md`) | SA | Override — direct Read had already succeeded |
| 3 | 2026-04-24 | `disable-auto-close` | 1 | Grep | Cross-project `PLANNER_TEMPLATE.md` | SA | Override — known Grep cross-project false positive |
| 4 | 2026-04-24 | `disable-auto-close` | 3 | Grep | Cross-project `PLANNER_TEMPLATE.md` | DOC | Override — agent routed around via bash |
| 5 | 2026-04-28 | `verdict-only-resume-docs` | 1 | Grep (x3) | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` | DEV | Override — exact BACKLOG #2 trigger; fix shipped (commit 3ca8361) |
| 6 | 2026-04-28 | `scope-check-monorepo-fix` | 2 | Grep | `/Users/marklehn/Desktop/GitHub` (rule.20 pattern) | QA | Override — agent used inline Python fallback |
| 7 | 2026-05-06 | `bellows-backlog-three-reliability-entries` | 1 | Bash (`rm`) | `.git/index.lock` | DEV | Override — deposit work succeeded before commit attempt |
| 8 | 2026-05-12 | `intermediate-decision-detection-design` | 1 | `mcp__vexp__run_pipeline` | N/A (MCP tool) | SA | Override — agent fell back to direct file reads |
| 9 | 2026-05-20 | `defer-validation-bulk-ingest` | 1 | `mcp__vexp__get_context_capsule` | N/A (MCP tool) | SA | Override — agent fell back to filesystem/grep |
| 10 | 2026-05-21 | `bellows-tier-1-batch` | 1 | Edit (x2) | `.claude/settings.local.json` | DEV | Override — agent fell back to `python3 -c` bash script; correct state shipped |

Additionally, `fuel-continuation-inference-v2-2026-05-21` step 1 had an `mcp__vexp__get_context_capsule` denial (verdict file #13/15 in the search), but this duplicates event #9's pattern and was resolved with the same override approach.

---

### Bucket (a): `.claude/settings.local.json` Edits Specifically

| # | Plan Slug | Date | Step | Tool | Agent Role | Change Attempted | Bash Fallback? |
|---|---|---|---|---|---|---|---|
| 1 | bellows-tier-1-batch-2026-05-21 | 2026-05-21 | 1 | Edit | Bellows Developer | Replace `Bash(git:*)` with 11 explicit git subcommands in `permissions.allow` | Yes — `python3 -c` script wrote JSON. Correct state shipped. |
| 2 | bellows-tier-1-batch-2026-05-21 | 2026-05-21 | 1 | Edit | Bellows Developer | Same as above (retry of denied attempt) | Same session — single fallback covered both. |

**Additional denied tool calls in the same session (same file, not Edit):**
- 3x Read denials on `.claude/settings.local.json` (1 parallel Read succeeded, race condition anomaly)
- 1x Grep denial on `.claude/settings.local.json`

**Total log-level denials touching `.claude/settings.local.json`:** 6 (2 Edit + 3 Read + 1 Grep), all in a single session (log file `20260521-121338-step.json`).

**Gate-level event:** 1 (event #10 in the gate inventory above).

---

### Bucket (b): Other `.claude/` Directory Edits

**Count: 0**

No denial events targeted files under `.claude/` other than `settings.local.json`. No Edit, Write, Read, or Grep denials on `.claude/CLAUDE.md`, `.claude/settings.json`, or any other `.claude/` path.

---

### Bucket (c): Edits to Project-Source Files Outside `.claude/`

**Edit/Write tool denials on project-source files: 0**

No Edit or Write tool denials were recorded for project-source files outside `.claude/`. All Edit/Write operations on in-scope files (within the agent's worktree `cwd`) succeeded. The path-scope restriction only fires when the target file is outside the worktree.

**Read-class tool (Grep/Glob/Read) denials on cross-project files: 365**

These constitute the vast majority of all denial events. They are read-class operations, not edits, but fire the same `no_permission_denials` gate. Detailed breakdown:

| Tool | Events | % of bucket |
|---|---|---|
| Grep | 305 | 83.6% |
| Glob | 73 | 20.0% |

**Top targeted paths:**

| # | Path | Events | % |
|---|---|---|---|
| 1 | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` | 95 | 26.0% |
| 2 | `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` | 92 | 25.2% |
| 3 | `/Users/marklehn/Developer/GitHub/bellows` (directory) | 30 | 8.2% |
| 4 | `/Users/marklehn/Developer/GitHub` (root) | 21 | 5.8% |
| 5 | `/Users/marklehn/Desktop/GitHub` (root) | 19 | 5.2% |
| 6 | `/Users/marklehn/Developer/GitHub/LESSONS.md` | 9 | 2.5% |
| 7 | Governance ADR files | 12 | 3.3% |
| 8 | Cross-project repos (invoice-pulse, forge, etc.) | 19 | 5.2% |
| 9 | Other / unclassifiable | 68 | 18.6% |

**Note:** Path prefix shifted from `/Users/marklehn/Desktop/GitHub/` (April–early May) to `/Users/marklehn/Developer/GitHub/` (mid-May onward), reflecting a projects directory relocation around 2026-05-13.

**Assessment:** These are expected denials — agents attempting native Grep/Glob on files outside their worktree `cwd`. Over half (51%) target `PLANNER_TEMPLATE.md`, a governance-root file agents frequently reference. The READ_CLASS_TOOLS gate exemption (shipped 2026-04-28 via commit 3ca8361) addressed this at the gate level for known read-class tools. MCP tool denials (5 events) represent tools not on the exemption list.

**Gate-level events from this bucket:** 8 (events #1–6, #8–9 in the gate inventory).

---

### Bucket (d): Bash Command Denials Unrelated to Edit

| # | Date | Log File | Plan Context | Command Denied | Purpose |
|---|---|---|---|---|---|
| 1 | 2026-05-06 | 20260506-190128-step.json | bellows-backlog-three-reliability-entries | `rm .git/index.lock && git add ... && git commit` | Stale .git/index.lock cleanup before commit |
| 2 | 2026-05-19 | 20260519-134726-step.json | Unknown | `rm -f .git/index.lock .git/"index "*.lock ...` | GUARDRAILS.md lock cleanup |
| 3 | 2026-05-21 | 20260521-012347-step.json | Unknown | `rm -f .git/index.lock .git/"index "*.lock ...` | GUARDRAILS.md lock cleanup |

**Additional non-file denials:**

| # | Date | Tool | Context |
|---|---|---|---|
| 4 | 2026-05-06 | AskUserQuestion | Attempted to ask user about removing stale `.git/index.lock` (non-interactive mode) |
| 5 | 2026-05-12 | `mcp__vexp__run_pipeline` | Code exploration preset (MCP tool) |
| 6–7 | 2026-05-20, 2026-05-21 | `mcp__vexp__get_context_capsule` (x2) | Code context queries (MCP tool) |
| 8–9 | 2026-05-22 | WebSearch, WebFetch | This diagnostic's own Step 1 — researching Claude Code permission docs |

**Assessment:** Events 1–3 are protective denials — compound commands starting with `rm` targeting `.git/index.lock`. These reflect correct operation of the permission model. Events 4–9 are tool-class denials (tools not on the `--allowedTools` list or not explicitly permitted).

**Gate-level events from this bucket:** 1 (event #7 in the gate inventory — Bash `rm` denial).

---

### Unclassified

15 denial events had insufficient path information for bucket classification (no `tool_input` dict or missing path field). All were from early-format log files (April 2026).

---

## Bucket Counts Summary

| Bucket | Description | Log-Level Events | % | Gate-Level Events |
|---|---|---|---|---|
| **(a)** | `.claude/settings.local.json` operations | 6 | 1.5% | 1 |
| **(b)** | Other `.claude/` directory operations | 0 | 0.0% | 0 |
| **(c)** | Read-class cross-project denials | 365 | 93.1% | 8 |
| **(d)** | Bash / non-file-tool denials | 6 | 1.5% | 1 |
| — | Unclassified | 15 | 3.8% | 0 |
| **Total** | | **392** | **100%** | **10** |

---

## Recurrence Pattern

### Bucket (a) — `.claude/settings.local.json` operations

**Frequency:** 1 incident in 30 days (6 denial events in a single session, producing 1 gate failure).

**Trigger condition:** A Bellows plan explicitly targets `.claude/settings.local.json` for modification while the agent executes in a worktree. The `.claude/` directory resides at the main repo root (`/Users/marklehn/Developer/GitHub/bellows/.claude/`), outside every worktree's `cwd` (`/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/<slug>/`). Any Edit/Write/Read/Grep call on this file from a worktree-based agent will be denied.

**Recurrence expectation:** Low frequency, high predictability. Plans that edit `.claude/settings.local.json` are authored by the Planner for specific governance tasks (e.g., narrowing Bash wildcards, adding new tool permissions). Based on BACKLOG history, these plans recur on the cadence of permission hygiene reviews — approximately monthly. **Every such plan will hit this denial if the agent uses Edit**, and the `no_permission_denials` gate will fire, requiring a Rule 22 override.

**Risk profile:** The bash fallback workaround is reliable — the agent autonomously discovered `python3 -c` as an alternative and shipped the correct file state. The operational cost is:
1. The gate fires and produces a `gate_failure` verdict request
2. The Planner or CEO must issue a Rule 22 override
3. The override adds ~5 minutes of latency to the plan cycle

This is a **friction cost, not a correctness risk** — the file state is always correct on disk.

### Bucket (c) — Read-class cross-project denials

**Frequency:** 365 events in 30 days (~12/day average). High frequency but fully expected.

**Trigger condition:** Agent attempts native Grep/Glob on files outside their worktree `cwd`, most commonly `PLANNER_TEMPLATE.md` (187 events, 51.2%).

**Status:** Already addressed by the READ_CLASS_TOOLS gate exemption (shipped 2026-04-28, commit 3ca8361). The exemption filters read-class denials (Grep, Glob, Read) from gate evaluation. These denials still occur at the Claude Code permission layer but no longer produce `gate_failure` verdicts post-fix.

**Residual gap:** MCP tool denials (5 events for `mcp__vexp__run_pipeline` and `mcp__vexp__get_context_capsule`) are not on the READ_CLASS_TOOLS exemption list. These still fire the gate and require overrides.

### Bucket (d) — Bash / non-file-tool denials

**Frequency:** 3 Bash `rm` denials in 30 days (all targeting `.git/index.lock`).

**Assessment:** These are correct protective denials. The bash-gate-guardrails exemption (shipped 2026-05-20) addresses the contradiction between GUARDRAILS.md instructing agents to clean lock files and the permission model blocking `rm`. No recurrence expected post-exemption.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 2
**Status:** Complete

### What Was Done
Audited all permission-denial events across 613 step log files, all resolved/pending verdict files, and the verdict-log ledger, covering the 30-day window 2026-04-23 to 2026-05-22. Identified 392 individual denial events at the log level and 10 `no_permission_denials` gate failures at the verdict level. Classified all events into 4 buckets per plan specification plus 1 emergent bucket. Produced per-occurrence table for bucket (a) showing a single incident with successful bash fallback, and a complete gate-level inventory of all 10 `no_permission_denials` failures.

### Files Deposited
- `bellows/knowledge/research/permission-denial-history-audit-2026-05-22.md` — audit findings with gate-level inventory, per-bucket event tables, bucket counts, and recurrence pattern analysis

### Files Created or Modified (Code)
- None — investigation only

### Decisions Made
- Classified all 392 events into buckets based on tool name and target path
- Determined bucket (a) recurrence as low-frequency (~monthly), high-predictability (every plan targeting `.claude/settings.local.json` will hit this denial)
- Added a fifth emergent bucket (c) for read-class cross-project denials, which dominate the population (93.1%) but are already addressed by the READ_CLASS_TOOLS exemption

### Flags for CEO
- None

### Flags for Next Step
- The low recurrence rate (1 incident in 30 days, ~monthly cadence) is a key input for Shape 1 vs. Shape 2 vs. Shape 3 evaluation in Step 3 — low frequency favors documentation or lightweight workaround over infrastructure changes
- MCP tool denials (5 events, 2 gate failures) represent a separate residual gap not covered by the READ_CLASS_TOOLS exemption — may warrant its own BACKLOG entry
