# PATH-001 Rule 20 Staleness Audit — Findings

**Diagnostic:** `diagnostic-path-001-rule-20-staleness-audit-2026-05-11`
**Date:** 2026-05-11
**Agent:** Bellows Systems Analyst

---

## Question 1 — Locate the original PATH-001 pattern definition

**Source file:** `bellows/knowledge/research/agent-prompt-feedback.md`, lines 399–412.

The PATH-001 pattern entry is titled `## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)` and has status **OPEN**. The original failure mode, quoted verbatim:

> **Pattern:** Plans use `bellows/knowledge/...` paths in agent instructions, claim shutil.move calls, grep commands, and Rule 20 self-check evidence directories. These paths assume cwd is the governance-root (`/Users/marklehn/Desktop/GitHub/`). But agents executing inside Bellows worktree dispatches have cwd = `bellows/` (or, post-monorepo-fix, the `bellows/` project directory itself). The `bellows/` prefix produces double-prefix paths like `bellows/bellows/knowledge/...` that don't exist. Agents typically work around this via cd or absolute-path conversion, but the friction is real and recurring.

The entry was first identified pre-2026-05-04 and reinforced 4 times in the 2026-05-04 session feedback. It documents two recommended fixes for Rule 20 blocks specifically (line 409):

> For Rule 20 self-check blocks specifically: use `os.path.abspath(__file__)` or `pathlib.Path(__file__).resolve()` to anchor paths regardless of cwd, OR use absolute paths in `qa_report_path` and `evidence_dir`.

No other copy of `agent-prompt-feedback.md` exists in the bellows repo. The string `PATH-001` also appears in:
- `NEXT_SESSION.md` lines 23, 70, 72, 76, 118 (session planning references)
- `knowledge/BACKLOG.md` line 15 (the BACKLOG entry under audit)
- `PROJECT_STATUS.md` lines 18–19, 28, 255 (status references)
- `knowledge/qa/qa-scope-check-project-path-filter-2026-04-22.md` line 72 (QA workaround note)
- `knowledge/decisions/Done/executable-r3-shadow-cache-prompt-2026-04-19.md` lines 109, 115 (plan that used absolute-path workaround citing PATH-001)
- `knowledge/decisions/Done/executable-session-wrap-evening-2026-05-10.md` line 26 and `executable-session-wrap-2026-05-10.md` line 83 (open backlog counts)
- Multiple per-plan feedback entries in `agent-prompt-feedback.md` lines 660, 698, 717, 737 (reinforcements)

**Answer:** The original PATH-001 definition is at `agent-prompt-feedback.md:399–412`. The failure mode is CWD-relative paths with `bellows/` prefix in Rule 20 self-check blocks producing broken paths when agents execute from inside the `bellows/` directory.

---

## Question 2 — Audit the current canonical block

**Source file:** `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`, lines 32–100.

### Path-related variables and expressions

| Variable / Expression | Line(s) | Absolute or CWD-relative | Placeholder instruction |
|---|---|---|---|
| `plan_slug` | 35 | N/A (string identifier, not a path) | `# PLACEHOLDER — set from plan prompt` |
| `qa_report_path` | 36 | **Placeholder reads `<absolute-path-to-qa-report.md>`** — explicitly instructs absolute path | `# PLACEHOLDER — set from plan prompt` |
| `evidence_dir` | 37 | **Placeholder reads `<absolute-path-to-evidence-dir>/`** — explicitly instructs absolute path | `# PLACEHOLDER — set from plan prompt` |
| `os.path.isdir(evidence_dir)` | 66 | Inherits from `evidence_dir` — absolute if placeholder followed | N/A |
| `os.path.join(evidence_dir, fname)` | 70 | Inherits from `evidence_dir` — absolute if placeholder followed | N/A |
| `os.path.isfile(fpath)` | 71 | Inherits from `fpath` = `os.path.join(evidence_dir, fname)` — absolute | N/A |
| `os.path.getsize(fpath)` | 73 | Same as above — absolute | N/A |
| `os.path.isfile(qa_report_path)` | 75 | Inherits from `qa_report_path` — absolute if placeholder followed | N/A |

Additionally, the plan-side template (lines 15–22) that plans paste into QA steps explicitly marks both values as absolute:

> - `qa_report_path`: `<absolute-path-to-qa-report>`
> - `evidence_dir`: `<absolute-path-to-evidence-directory>`

### `bellows/` prefix audit

**No occurrence of the string `bellows/` appears anywhere in the canonical block** (lines 32–100) or in the plan-side template (lines 15–22). The block contains no hardcoded project-relative paths at all — only placeholders that instruct the QA agent to supply absolute paths.

**Answer:** The current canonical block uses exclusively placeholder-based paths that explicitly instruct "absolute-path-to-..." for both `qa_report_path` and `evidence_dir`. All `os.path.*` calls derive from these two variables. No `bellows/` prefix exists anywhere in the canonical block. The PATH-001 failure mode (CWD-relative paths with `bellows/` prefix) cannot reproduce against this block as written.

---

## Question 3 — Audit the broken plan that triggered the original entry

**Source file:** `bellows/knowledge/decisions/Done/executable-verdict-lifecycle-coupling-2026-04-19.md`, lines 98–166.

The Rule 20 block inlined in that plan's QA step (Step 2) contained these PATH-001-exhibiting lines (quoted verbatim from lines 102–103):

```python
qa_report_path = "bellows/knowledge/qa/verdict-lifecycle-coupling-2026-04-19.md"
evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
```

These are CWD-relative paths with `bellows/` prefix — the exact PATH-001 pattern. The `evidence_dir` uses an f-string that resolves to `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/`, which only resolves correctly if the agent's CWD is the governance-root (`/Users/marklehn/Desktop/GitHub/`), not the bellows project directory.

The QA report for this plan (`knowledge/qa/verdict-lifecycle-coupling-2026-04-19.md`, line 75) shows the self-check ultimately passed, with evidence paths corrected by the QA agent:

```
Evidence folder: knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/
```

The QA report for a related plan (`qa-scope-check-project-path-filter-2026-04-22.md`, line 72) explicitly documents the PATH-001 workaround:

> Ran self-check with corrected paths (without `bellows/` prefix) per PATH-001 pattern — execution CWD is already inside the bellows directory

### Comparison to current canonical block

| Aspect | Broken 2026-04-19 block | Current canonical block |
|---|---|---|
| `qa_report_path` | `"bellows/knowledge/qa/..."` (CWD-relative, `bellows/` prefix) | `"<absolute-path-to-qa-report.md>"` (placeholder, explicitly absolute) |
| `evidence_dir` | `f"bellows/knowledge/qa/evidence/{plan_slug}/"` (CWD-relative, `bellows/` prefix) | `"<absolute-path-to-evidence-dir>/"` (placeholder, explicitly absolute) |
| Block authorship | Planner inlined the block in the plan | Planner references `RULE_20_SELF_CHECK_BLOCK.md`; QA agent reads and fills placeholders |
| `POSITIVE_STATUS_TOKENS` | Not present (older block version) | Present (line 48, glyph-agnostic detection) |

**Answer:** The broken 2026-04-19 plan inlined the Rule 20 block with hardcoded CWD-relative `bellows/`-prefixed paths — the exact PATH-001 pattern. The current canonical block contains no equivalent code. The placeholder approach structurally eliminates the failure mode: the Planner no longer authors paths inside the block, and the placeholder names (`<absolute-path-to-...>`) explicitly instruct the QA agent to supply absolute paths.

---

## Question 4 — Population audit on post-migration QA reports

All QA reports in `bellows/knowledge/qa/` with filenames containing `2026-05-10` or `2026-05-11` were scanned (post-migration, since the single-source migration shipped 2026-05-10 via commit `a109e47`).

### 2026-05-10 reports (7 files)

| Report | Rule 20 Self-Check | Path-Resolution Failure |
|---|---|---|
| `header-parser-multiline-fix-qa-2026-05-10.md` | PASSED | None |
| `phase-1-5-lessons-source-d-qa-2026-05-10.md` | PASSED | None |
| `rule-20-self-check-wt-path-qa-2026-05-10.md` | PASSED | None |
| `rule-20-single-source-qa-2026-05-10.md` | PASSED | None |
| `s3-bug-c-halted-stale-check-qa-2026-05-10.md` | PASSED | None |
| `startup-sweep-extract-qa-2026-05-10.md` | PASSED | None |
| `teardown-worktree-lock-cleanup-qa-2026-05-10.md` | PASSED | None |

### 2026-05-11 reports (10 files)

| Report | Rule 20 Self-Check | Path-Resolution Failure |
|---|---|---|
| `backlog-append-fix-plan-trips-own-bug-qa-2026-05-11.md` | PASSED | None |
| `backlog-hygiene-cause-5-and-daemon-logging-qa-2026-05-11.md` | PASSED | None |
| `canary-step-header-parser-fixes-qa-2026-05-11.md` | PASSED | None |
| `daemon-version-observability-qa-2026-05-11.md` | PASSED | None |
| `fence-strip-plan-text-parsers-qa-2026-05-11.md` | PASSED | None |
| `plan-handler-seen-slug-refactor-qa-2026-05-11.md` | PASSED | None |
| `planner-template-parser-self-trip-and-session-wrap-qa-2026-05-11.md` | PASSED | None |
| `rule-26-evidence-path-fix-qa-2026-05-11.md` | PASSED | None |
| `session-end-full-suite-qa-2026-05-11.md` | PASSED | None |
| `step-header-line-anchor-qa-2026-05-11.md` | PASSED | None |

### Summary counts

- **Total post-migration QA reports examined:** 17
- **Count exhibiting any path-resolution failure:** 0
- **Count exhibiting PATH-001-style CWD-relative failures:** 0
- **Count with Rule 20 self-check PASSED:** 17/17

**Answer:** Zero path-resolution failures across all 17 post-migration QA reports. The canonical block pattern with explicit absolute-path placeholders has produced a clean 17/17 pass rate since migration.

---

## Question 5 — Cross-project canonical reference audit

### `bellows/agents/BELLOWS_QA.md`

**Source file:** `bellows/agents/BELLOWS_QA.md`, lines 154–166.

The file contains a `## Rule 20 Self-Check (Canonical Block Reference)` section (lines 154–166) that:

1. **Points to the canonical file:** Line 156 states `The canonical Rule 20 self-check Python block lives at /Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`.
2. **Does NOT inline the block:** Line 166 explicitly states `The block is NOT reproduced in this agent file. It lives in one place only.`
3. **References the canonical file in the Role Summary:** Line 16 includes `(canonical source: governance-root RULE_20_SELF_CHECK_BLOCK.md)`.

**No deviation.** BELLOWS_QA.md correctly points to the canonical file and does not inline the block.

### `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md`

**Unable to read directly** — file is outside the bellows project directory and filesystem permissions are scoped to the bellows repo. However, the BACKLOG Closed entry for the single-source migration (line 35 of `knowledge/BACKLOG.md`) documents that both files were updated:

> `bellows/agents/BELLOWS_QA.md` and `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` updated with reference paragraphs (no inlining). Three commits across three repos: governance `a109e47`, bellows `b05dc42`, invoice-pulse `02702201`.

The migration plan's QA report (`rule-20-single-source-qa-2026-05-10.md`) verified 14/14 properties including the "no-inline-block invariant across all 4 governance-tree files."

**Answer:** BELLOWS_QA.md confirmed: no inlined block, correctly points to canonical file. INVOICE_SECURITY_TESTING_ANALYST.md documented as updated with reference paragraph (no inlining) per the migration QA report; commit `02702201` in invoice-pulse captures the change. Direct verification deferred due to filesystem scope, but the migration QA report provides verified evidence.

---

## Question 6 — Verdict

### **STALE — close as hygiene.**

PATH-001 cannot reproduce against the post-migration canonical Rule 20 self-check block. The 2026-05-10 single-source migration (commit `a109e47` governance, `b05dc42` bellows) structurally fixed the failure mode through two reinforcing design changes:

1. **Placeholder-enforced absolute paths.** The canonical block at `RULE_20_SELF_CHECK_BLOCK.md` uses `<absolute-path-to-qa-report.md>` and `<absolute-path-to-evidence-dir>/` as placeholder names, explicitly instructing QA agents to supply absolute paths. The plan-side template repeats this instruction. No `bellows/` prefix appears anywhere in the canonical block.

2. **Elimination of Planner-side block authoring.** The Planner no longer inlines the Rule 20 block in plans. Plans reference `RULE_20_SELF_CHECK_BLOCK.md`; the QA agent reads the canonical file and fills placeholders. The original PATH-001 failure mode — the Planner hardcoding CWD-relative `bellows/`-prefixed paths into an inlined block — is structurally impossible under this model because the Planner never touches the block's path variables.

The population audit confirms this: 17/17 post-migration QA reports show Rule 20 self-check PASSED with zero path-resolution failures, compared to multiple documented PATH-001 workarounds in pre-migration reports.

No code or governance change is required. Recommend closing the BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` as a hygiene closure citing the single-source migration commit `a109e47`.

---

## Recommendation

The BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` is stale. The CWD-relative path failure mode it describes was structurally eliminated by the 2026-05-10 Rule 20 single-source migration, which moved the canonical block to a placeholder-based template that enforces absolute paths by design and removed the Planner's ability to author (and mis-path) the block inline. Seventeen consecutive post-migration QA reports confirm zero PATH-001 recurrences. Close the BACKLOG entry as hygiene, citing migration commit `a109e47`. The `agent-prompt-feedback.md` PATH-001 pattern entry (line 399) should also be updated to CLOSED status with a note referencing the structural fix.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Executed a six-question staleness audit of the BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check`. Traced the original pattern definition, audited the current canonical block, compared to the broken pre-migration block, scanned 17 post-migration QA reports, and verified cross-project canonical references. Classified the entry as STALE with recommendation to close as hygiene.

### Files Deposited
- `bellows/knowledge/research/path-001-rule-20-staleness-audit-2026-05-11.md` — staleness audit findings (this file)

### Files Created or Modified (Code)
- None (read-only audit)

### Decisions Made
- Classified BACKLOG entry as STALE based on structural evidence that the 2026-05-10 migration eliminated the PATH-001 failure mode
- Recommended hygiene closure citing migration commit `a109e47`
- Recommended updating `agent-prompt-feedback.md` PATH-001 status from OPEN to CLOSED

### Flags for CEO
- None

### Flags for Next Step
- BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` ready for hygiene closure
- `agent-prompt-feedback.md` PATH-001 pattern entry (line 399) ready for status update to CLOSED
