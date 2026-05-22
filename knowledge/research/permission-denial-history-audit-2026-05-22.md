# Permission Denial History Audit

**Date:** 2026-05-22 | **Agent:** Bellows Systems Analyst | **Diagnostic:** claude-settings-permission-gap-2026-05-22 | **Step:** 2

---

## Audit Window

| Field | Value |
|---|---|
| Date range | 2026-04-23 to 2026-05-22 (30 days) |
| Step log files examined | 611 (`bellows/logs/*.json`) |
| Verdict files examined | 429 (`bellows/verdicts/resolved/`) |
| Ledger file | 1 (`bellows/verdicts/ledger.jsonl`) |
| **Total sources** | **1,041** |
| Step files with non-empty `permission_denials` | 107 |
| Total individual denial events | 373 |

---

## Methodology

1. Scanned all step JSON files in `bellows/logs/` for non-empty `permission_denials` arrays.
2. For each non-empty array, extracted the `tool_name` and `tool_input` fields from each denial dict to identify the tool and target path.
3. Scanned all verdict files in `bellows/verdicts/resolved/` for mentions of "no_permission_denials", "permission", or "denied".
4. Scanned the ledger (`bellows/verdicts/ledger.jsonl`) for entries with `gate_failure` pause reason.
5. Classified each denial event into one of five buckets based on the tool and target path.

---

## Event Inventory Tables

### Bucket (a): `.claude/settings.local.json` Edits

| # | Plan Slug | Date | Step | Tool | Agent Role | Change Attempted | Bash Fallback? |
|---|---|---|---|---|---|---|---|
| 1 | bellows-tier-1-batch-2026-05-21 | 2026-05-21 | 1 | Edit | Bellows Developer | Replace `Bash(git:*)` with 11 explicit git subcommands in `permissions.allow` | Yes — `python3 -c` script wrote JSON. Correct state shipped. |
| 2 | bellows-tier-1-batch-2026-05-21 | 2026-05-21 | 1 | Edit | Bellows Developer | Same as above (retry of denied attempt) | Same session — single fallback covered both. |

**Additional denied tool calls in the same session (same file, not Edit):**
- 3x Read denials on `.claude/settings.local.json` (1 parallel Read succeeded)
- 1x Grep denial on `.claude/settings.local.json`

**Total denials touching `.claude/settings.local.json`:** 6 (2 Edit + 3 Read + 1 Grep), all in a single session.

### Bucket (b): Other `.claude/` Directory Edits

**Count: 0**

No denial events targeted files under `.claude/` other than `settings.local.json`.

### Bucket (c): Edits to Project-Source Files Outside `.claude/`

**Count: 0**

No Edit or Write tool denials were recorded for project-source files. All Edit/Write operations on in-scope files succeeded.

### Bucket (d): Bash Command Denials

| # | Date | Log File | Plan Context | Command Denied | Purpose |
|---|---|---|---|---|---|
| 1 | 2026-05-06 | 20260506-190128-step.json | Unknown | `rm /Users/marklehn/Desktop/GitHub/.git/index.lock && git add ...` | Stale .git/index.lock cleanup |
| 2 | 2026-05-19 | 20260519-134726-step.json | Unknown | `rm -f .git/index.lock .git/"index "*.lock ...` | Guardrails .git lock cleanup |
| 3 | 2026-05-21 | 20260521-012347-step.json | Unknown | `rm -f .git/index.lock .git/"index "*.lock ...` | Guardrails .git lock cleanup |

**Assessment:** All three are **protective denials** — compound commands starting with `rm` that target `.git/index.lock`. These denials reflect correct operation of the permission model (preventing recursive .git/ access), not a gap.

### Bucket (e): Read-Class Tool Denials on Cross-Project Paths

**Count: 351**

| Tool | Events | % of bucket |
|---|---|---|
| Grep | 273 | 77.8% |
| Glob | 73 | 20.8% |
| MCP tools (vexp) | 5 | 1.4% |

**Top targeted paths:**

| # | Path | Events | % |
|---|---|---|---|
| 1 | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` | 95 | 27.1% |
| 2 | `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` | 88 | 25.1% |
| 3 | `/Users/marklehn/Developer/GitHub/bellows` | 30 | 8.5% |
| 4 | `/Users/marklehn/Developer/GitHub` | 21 | 6.0% |
| 5 | `/Users/marklehn/Desktop/GitHub` | 19 | 5.4% |
| 6 | `/Users/marklehn/Developer/GitHub/LESSONS.md` | 9 | 2.6% |
| 7 | Governance ADR files | 12 | 3.4% |
| 8 | Cross-project repos (invoice-pulse, forge, etc.) | 19 | 5.4% |
| 9 | Other | 58 | 16.5% |

**Assessment:** These are **expected denials** — agents attempting native Grep/Glob on files outside their project `cwd`. Over half (52%) target `PLANNER_TEMPLATE.md`, a governance-root file that agents frequently need to reference. Agents fall back to Bash equivalents (`grep`, `find`, `cat`) successfully.

### Unclassified

17 denial events had insufficient path information for bucket classification (no `tool_input` dict or missing path field). All were from early-format log files.

---

## Bucket Counts Summary

| Bucket | Description | Count | % of total |
|---|---|---|---|
| **(a)** | `.claude/settings.local.json` edits | 2 | 0.5% |
| **(b)** | Other `.claude/` directory edits | 0 | 0.0% |
| **(c)** | Project-source edits outside `.claude/` | 0 | 0.0% |
| **(d)** | Bash command denials | 3 | 0.8% |
| **(e)** | Read-class cross-project denials | 351 | 94.1% |
| — | Unclassified | 17 | 4.6% |
| **Total** | | **373** | **100%** |

---

## Recurrence Pattern

### Bucket (a) — `.claude/settings.local.json` edits

**Frequency:** 1 incident in 30 days (2 denial events in a single session).

**Trigger condition:** A Bellows plan explicitly targets `.claude/settings.local.json` for modification while the agent executes in a worktree. This is a rare operation — it occurs only when a plan needs to change Bellows's own Claude Code permission allowlist, which is a governance/configuration change rather than routine development.

**Recurrence expectation:** Low frequency, high predictability. Plans that edit `.claude/settings.local.json` are authored by the Planner for specific governance tasks (e.g., narrowing Bash wildcards, adding new tool permissions). These plans recur on the cadence of permission hygiene reviews — approximately monthly based on BACKLOG history. Every such plan will hit this denial if the agent uses Edit, and the `no_permission_denials` gate will fire, requiring a Rule 22 override.

**Risk profile:** The bash fallback workaround is reliable and the agent autonomously discovers it. The operational cost is: (1) the gate fires and produces a `gate_failure` verdict, (2) the Planner or CEO must issue a Rule 22 override, (3) the override adds ~5 minutes of latency to the plan cycle. This is a friction cost, not a correctness risk — the file state is always correct on disk.

### Bucket (e) — Read-class cross-project denials

**Frequency:** 351 events in 30 days (~12/day average). High frequency but fully expected and handled by the existing read-class taxonomy (shipped via `no-permission-denials-taxonomy-2026-04-28.md` research).

**Note:** Bucket (e) was already addressed by a prior diagnostic. The proposed `READ_CLASS_TOOLS` gate exemption would eliminate these as gate failures. This audit confirms the prior taxonomy's findings remain accurate.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 2
**Status:** Complete

### What Was Done
Audited all permission-denial events across 1,041 source files (611 step logs, 429 verdict files, 1 ledger) covering the 30-day window 2026-04-23 to 2026-05-22. Classified 373 denial events into 5 buckets. Produced per-occurrence table for bucket (a) showing a single incident with successful bash fallback.

### Files Deposited
- `bellows/knowledge/research/permission-denial-history-audit-2026-05-22.md` — audit findings with event inventory tables, bucket counts, and recurrence pattern analysis

### Files Created or Modified (Code)
- None — investigation only

### Decisions Made
- Classified all 373 events into buckets based on tool name and target path
- Determined bucket (a) recurrence as low-frequency (~monthly), high-predictability (every plan targeting `.claude/settings.local.json` will hit it)

### Flags for CEO
- None

### Flags for Next Step
- The low recurrence rate (1 incident in 30 days) is a key input for Shape 1 vs. Shape 2 evaluation — low frequency favors documentation over infrastructure changes.
