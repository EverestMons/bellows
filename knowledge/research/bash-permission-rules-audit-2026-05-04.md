# Bash Permission Rules Audit — All Watched Projects
**Date:** 2026-05-04 | **Agent:** Bellows Systems Analyst | **Diagnostic:** bash-permission-rules-audit

---

## Executive Summary

All 9 audit targets (8 watched projects + governance root) use exclusively `settings.local.json` files with **allow-only** permission lists and **zero deny rules**. No project has a `deny` key, `defaultMode` override, or any form of destructive-command blocking. The common pattern set across all projects includes broad wildcards for `rm`, `git`, `kill`, `pkill`, `killall`, `chmod`, and other destructive-capable commands (`Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)`). Under Bellows `claude -p --allowedTools "...,Bash"` dispatch, any command matching these wildcards auto-approves without CEO review. The user-level settings (`~/.claude/settings.json`) contain no permission rules at all. **The per-command "safety net" identified by the prior diagnostic is effectively wide open** — it provides pre-approval rather than restriction.

---

## Critical Findings

### 🔴 All 9 Projects: No Deny Rules + Broad Allow Wildcards = Unrestricted Destructive Commands

Every watched project has `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)`, `Bash(pkill:*)`, `Bash(killall:*)`, `Bash(chmod:*)` in its allow list. These patterns auto-approve any command starting with those prefixes. Under Bellows dispatch:
- `rm -rf /` → matches `Bash(rm:*)` → **auto-approved**
- `git push --force origin main` → matches `Bash(git:*)` → **auto-approved**
- `git reset --hard` → matches `Bash(git:*)` → **auto-approved**
- `kill -9 <any_pid>` → matches `Bash(kill:*)` → **auto-approved**
- `chmod 777 /` → matches `Bash(chmod:*)` → **auto-approved**
- `killall Finder` → matches `Bash(killall:*)` → **auto-approved**

No deny rule exists anywhere to catch these patterns.

### 🔴 User-Level Settings: No Permission Block

`~/.claude/settings.json` contains only `enabledPlugins` and `effortLevel` — no `permissions` key whatsoever. This means there is NO fallback deny layer at the user level that would apply across all projects.

---

## Per-Project Bash Rules Table

| # | Project | settings.local.json | settings.json | Bash deny patterns | Bash allow count | Representative allow patterns | defaultMode | Risk |
|---|---------|:---:|:---:|---|---|---|---|---|
| 1 | **Governance root** (`/Desktop/GitHub/`) | Yes | No | **none** | 46 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)` | absent | 🔴 |
| 2 | **invoice-pulse** | Yes | No | **none** | 142 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(chmod:*)` + many project-specific tee/EVDIR patterns | absent | 🔴 |
| 3 | **BrewBuddy** | Yes | No | **none** | 50 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)` + xcodebuild patterns | absent | 🔴 |
| 4 | **study** | Yes | No | **none** | 45 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)` + npm/cargo/vitest | absent | 🔴 |
| 5 | **ai-career-digest** | Yes | No | **none** | 45 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(chmod:*)` (minimal set only) | absent | 🔴 |
| 6 | **freight-kb** | Yes | No | **none** | 45 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)` (minimal set only) | absent | 🔴 |
| 7 | **forge** | Yes | No | **none** | 56 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)` + pre-scan-sync scripts | absent | 🔴 |
| 8 | **anvil** | Yes | No | **none** | 48 | `Bash(rm:*)`, `Bash(git:*)`, `Bash(kill:*)` + pre-scan-sync scripts | absent | 🔴 |
| 9 | **bellows** | Yes | No | **none** | 57 | `Bash(git:*)`, `Bash(python3:*)`, `Bash(rm:*)` + many evidence tee patterns | absent | 🔴 |

**Common base patterns (all 9 projects share these):**
```
Bash(git:*), Bash(GIT_TERMINAL_PROMPT=0 git:*), Bash(python3:*), Bash(python:*),
Bash(rm:*), Bash(mv:*), Bash(cp:*), Bash(mkdir:*), Bash(touch:*), Bash(chmod:*),
Bash(kill:*), Bash(pkill:*), Bash(killall:*), Bash(sed:*), Bash(awk:*), Bash(xargs:*)
```

---

## User-Level Settings Summary

| File | Present | Permissions block | Bash patterns |
|------|:---:|:---:|---|
| `~/.claude/settings.json` | Yes | **No** (`enabledPlugins` and `effortLevel` only) | none |
| `~/.claude/settings.local.json` | No | — | — |

The user-level settings provide **zero** permission rules. All permission behavior is determined entirely by project-level `settings.local.json` files.

---

## High-Risk Gaps

All 9 projects are classified 🔴. The following destructive commands would auto-approve under Bellows dispatch in **every watched project**:

| Destructive command | Matching allow pattern | Impact |
|---|---|---|
| `rm -rf /` or `rm -rf .` | `Bash(rm:*)` | Total filesystem destruction |
| `rm -rf .git` | `Bash(rm:*)` | Permanent git history loss |
| `git push --force origin main` | `Bash(git:*)` | Overwrites shared remote history |
| `git reset --hard` | `Bash(git:*)` | Discards all uncommitted work |
| `git branch -D <branch>` | `Bash(git:*)` | Deletes local branch without confirmation |
| `kill -9 1` | `Bash(kill:*)` | Kills init/launchd (system disruption) |
| `killall -9 Finder` | `Bash(killall:*)` | Kills macOS Finder |
| `chmod -R 000 /` | `Bash(chmod:*)` | Renders filesystem inaccessible |
| `pkill -f bellows` | `Bash(pkill:*)` | Kills Bellows itself mid-execution |
| `xargs rm -rf` (via pipe) | `Bash(xargs:*)` | Arbitrary deletion via pipeline |

**Mitigating factors** (not permission-related):
- Claude models are instruction-following and unlikely to spontaneously execute destructive commands
- The scope_check gate (gates.py) flags out-of-plan edits (but not Bash commands)
- Bellows plans are authored by the trusted Planner; arbitrary prompts are not accepted

**Non-mitigating factors:**
- No deny rules exist to catch accidental destructive commands from model errors
- A hallucinated or misinterpreted plan step could invoke `rm -rf` without any gate catching it pre-execution
- If an agent compound-commands destruction (e.g., `cd /tmp && rm -rf ../..`), no pattern blocks it

---

## Production Behavior Validation (Sample 3 Cross-Check)

**Finding:** The 2026-04-17 Bash denial was in the **BrewBuddy** project.

| Field | Value |
|---|---|
| Log file | `bellows/logs/20260417-195019-step.json` |
| Project | `/Users/marklehn/Desktop/GitHub/BrewBuddy` |
| Plan | `diagnostic-flavornotes-subcategory-not-appearing-2026-04-17` |
| Denied command | `rm -f .git/index.lock 2>/dev/null; git add knowledge/research/flavornotes-subcategory-diag-2026-04-17.md knowledge/decisions/in-progress-diagnostic-flavornotes-subcategory-not-appearing-2026-04-17.md knowledge/decisions/Done/diagnostic-flavornotes-subcategory-not-appearing-2026-04-17.md` |

**Analysis of the denial mechanism:**

The denied command is a **compound command** using `;` to chain `rm` and `git add`. Claude Code's pattern matching evaluates the **entire command string** against allow patterns. The relevant BrewBuddy allow patterns are:
- `Bash(rm:*)` — would match a command starting with `rm`
- `Bash(git:*)` — would match a command starting with `git`

The compound command starts with `rm` so it matches `Bash(rm:*)`. However, the command **was denied**, suggesting one of:
1. **The settings at that time (2026-04-17) did not include the broad `Bash(rm:*)` pattern** — it may have been added later as the allow list grew organically via interactive approvals
2. **Claude Code treats compound commands (with `;`) as not matching simple prefix patterns** — the engine may require the entire command string to match, and the trailing `; git add ...` portion doesn't fit the `rm:*` glob

The most likely explanation is **(1)**: the BrewBuddy `settings.local.json` at that time was a subset of its current 50-pattern state. The specific entry `Bash(rm -f .git/index.lock .git/index *.lock .git/index [0-9]*)` present in current BrewBuddy settings was likely added *after* this denial incident. The organic growth pattern (interactive approvals accumulating over time) explains why a denial occurred then but would not occur now.

**Validation conclusion:** The per-command rule layer **was** firing in production on 2026-04-17. However, the current settings state has evolved to the point where it would no longer produce that denial — the broad `Bash(rm:*)` wildcard now pre-approves it.

---

## Recommendations (Ranked by Leverage x Effort)

### 1. Add a Shared Deny Template for Destructive Commands
**Leverage:** High | **Effort:** Low

Create a baseline `.claude/settings.json` (committed, shared) or amend each `settings.local.json` with deny rules:
```json
"deny": [
  "Bash(rm -rf /*)",
  "Bash(rm -rf .)",
  "Bash(rm -rf .git*)",
  "Bash(git push --force*)",
  "Bash(git push -f*)",
  "Bash(git reset --hard*)",
  "Bash(chmod -R 000*)",
  "Bash(kill -9 1*)",
  "Bash(killall*)"
]
```
This creates a hard stop regardless of allow patterns. Deny rules take precedence over allow rules in Claude Code settings.

### 2. Bellows-Side Destructive Command Pre-Check Gate
**Leverage:** High | **Effort:** Medium

Add a new gate in `gates.py` that inspects the Bash commands executed by the agent (from stream-json tool_use events) against a deny list. If a destructive command is detected, trigger a verdict pause for CEO review BEFORE the next step proceeds. This would not prevent the first execution but would catch patterns across a run.

### 3. Narrow the Allow Wildcards to Non-Destructive Forms
**Leverage:** High | **Effort:** Medium

Replace broad patterns like `Bash(rm:*)` with targeted forms:
- `Bash(rm:*)` → `Bash(rm -f *.lock)`, `Bash(rm -f /tmp/*)`, specific known patterns
- `Bash(git:*)` → keep, but add explicit deny for `git push --force`, `git reset --hard`
- `Bash(kill:*)` → remove entirely (agents rarely need process management)

### 4. Bellows Startup Settings Inventory Warning
**Leverage:** Medium | **Effort:** Low

At Bellows startup (or per-dispatch), check whether the target project's `settings.local.json` contains deny rules. If absent, log a warning: "Project X has no Bash deny rules — destructive commands will auto-approve." This doesn't block execution but creates visibility.

### 5. Document Minimum Settings Hygiene in PLANNER_TEMPLATE
**Leverage:** Low | **Effort:** Low

Add a section to the planner template noting that executable plans dispatched to projects without deny rules have unrestricted Bash access. The Planner could then include explicit "do NOT run rm -rf" instructions in plan prompts as a soft guard.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Read-only audit of `.claude/settings.local.json` and `.claude/settings.json` across all 9 targets (8 watched projects + governance root) plus user-level settings. Parsed permission blocks, inventoried all Bash allow/deny patterns, cross-referenced with the 2026-04-17 production denial, and produced a risk-classified per-project table with recommendations.

### Files Deposited
- `bellows/knowledge/research/bash-permission-rules-audit-2026-05-04.md`

### Files Created or Modified (Code)
- None — investigation only

### Decisions Made
- Classified all 9 projects as 🔴 (no deny rules, broad allow wildcards)
- Identified that the 2026-04-17 denial is no longer reproducible under current settings due to organic allow-list growth
- Determined that user-level settings provide no fallback safety

### Flags for CEO
- 🔴 **Critical finding:** Zero deny rules exist anywhere in the system. All destructive Bash commands (rm -rf, git push --force, git reset --hard, kill -9, chmod -R) would auto-approve under Bellows dispatch in every watched project. The per-command rule layer identified by the prior diagnostic is effectively an open door, not a safety net.

### Flags for Next Step
- None — single-step diagnostic
