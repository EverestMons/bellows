# Executable — Rule 26 Evidence Path Convention Fix and Stale Lessons Update

**Project:** bellows
**Type:** Executable
**Priority:** 10
**Author:** Planner
**Date:** 2026-05-11
**Auto-close:** false
**Test scope:** none (markdown-only governance edit, grep verification only)
**Execution Map:** Step 1 (Documentation Analyst) → Step 2 (QA)

## Context

The 2026-05-11 deposit_exists audit identified Cause 5 — plans declaring bare
`evidence/foo.txt` paths in `**Deposits:**` blocks while agents create files
at `knowledge/qa/evidence/<slug>/foo.txt`. 18 individual gate-failure lines
across 3 verdict requests trace to this convention mismatch.

The follow-up canary diagnostic
(`bellows/knowledge/research/rule-26-directory-bullet-canary-2026-05-11.md`)
confirmed:
- The current gate accepts directory-only `**Deposits:**` bullets via
  `os.path.isfile() or os.path.isdir()` at every resolution strategy
  (`bellows/gates.py:183-212`).
- The 2026-04-19 Lessons entry ("Do NOT list a directory path in the block")
  is stale — commit `e609ad3` (2026-04-30, BACKLOG #11 closure) added
  `isdir()` checks to all resolution strategies.

This plan tightens Rule 26's evidence-file guidance from permissive ("do NOT
need individual bullets") to mandatory ("MUST be represented by the directory
bullet alone"), and appends three new Lessons entries (stale-lesson retraction,
Cause 5 capture, diagnostic-before-executable discipline win).

**Commit-repo discipline (per Plan File Structure):** The PLANNER_TEMPLATE.md
edit commits to the governance-root repo at `/Users/marklehn/Desktop/GitHub/`.
The dev log, QA report, and evidence files commit to the `bellows` project
repo. This plan produces two commits, one per repo.

## STEP 1 — Documentation Analyst: Apply Rule 26 evidence-path tightening and Lessons updates

Read first:
- `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/rule-26-directory-bullet-canary-2026-05-11.md`

You are the Documentation Analyst. Apply three surgical edits to
`/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Use `Edit` tool calls
with byte-exact `old_string` anchors. Do not bulk-rewrite the file.

### Edit 1 — Version bump

**Anchor (lines 5-6, exact bytes):**

```
**Version:** 4.34
**Last Updated:** 2026-05-05 (v4.34)
```

**Replacement:**

```
**Version:** 4.35
**Last Updated:** 2026-05-11 (v4.35)
```

### Edit 2 — Rule 26 evidence-file guidance tightening

**Anchor (line 738 — single line, find by exact match):**

```
Each bullet holds exactly one path wrapped in backticks. Paths are project-relative (e.g., `bellows/knowledge/qa/my-report.md`) unless the deposit target is an absolute governance-root path (e.g., `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`) — the absolute-path case is rare and reserved for governance edits. The list is complete: every file the step writes to MUST appear. Evidence files (Rule 18) do NOT need individual bullets — list the evidence directory as a single bullet (e.g., `- `bellows/knowledge/qa/evidence/<plan-slug>/` (multiple files per Rule 20 self-check)`), because the Rule 20 self-check already enumerates the individual evidence filenames.
```

**Replacement (single line, preserve as a single line):**

```
Each bullet holds exactly one path wrapped in backticks. Paths are project-relative (e.g., `bellows/knowledge/qa/my-report.md`) unless the deposit target is an absolute governance-root path (e.g., `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`) — the absolute-path case is rare and reserved for governance edits. The list is complete: every file the step writes to MUST appear. Evidence files (Rule 18) MUST be represented by the evidence directory as a single bullet — e.g., `- `bellows/knowledge/qa/evidence/<plan-slug>/` (multiple files per Rule 20 self-check)`. Do NOT list individual evidence files (e.g., `evidence/orphan_handling.txt`, `knowledge/qa/evidence/<slug>/orphan_handling.txt`) in the `**Deposits:**` block. The Rule 20 self-check already enumerates individual evidence filenames; duplicating them in `**Deposits:**` is forbidden because (a) bare `evidence/<file>` paths do not resolve via any gate strategy (the agent writes them under `knowledge/qa/evidence/<slug>/`, not at the project root), and (b) listing both the directory and its children creates redundant gate work. The current gate accepts directory bullets via `os.path.isfile() or os.path.isdir()` resolution at every strategy (`bellows/gates.py:183-212`).
```

### Edit 3 — Append three new Lessons rows at the end of the Lessons table

The Lessons table ends just before the `## Forge Observations` section. The
boundary is: last row of Lessons (ending in `|`), blank line, `---`, blank
line, `## Forge Observations`. Insert three new rows BEFORE the blank line +
`---` boundary.

**Anchor (byte-exact — last Lessons row + boundary that follows it):**

The anchor is the final closing `|` of the last Lessons row (the 2026-05-05
"Rule 20 self-check fabrication" row), followed by the blank line, the `---`
horizontal rule, the blank line, and the `## Forge Observations` heading.

To make the anchor unambiguous, use the LAST six characters of the closing
Lessons row (` matches. |`) as the unique starting point of the `old_string`,
through the `## Forge Observations` heading.

Specifically — find this exact byte sequence in PLANNER_TEMPLATE.md:

```
matches. |

---

## Forge Observations
```

Replace it with:

```
matches. |
| 2026-05-11 | The 2026-04-19 Lessons entry stating "`**Deposits:**` blocks must list only files, not directories. The `deposit_exists` gate uses `os.path.isfile()` which returns False for directory paths" is **stale**. Commit `e609ad3` (2026-04-30, BACKLOG #11 closure) added `isdir()` checks to all four resolution strategies in `_resolve_deposit_path()` (`gates.py:183-212`). Directories now resolve at every strategy. The original lesson's `os.path.isfile()` rationale no longer holds. Future Planner sessions: when a Lessons entry's mechanical rationale references specific code behavior, periodically re-verify against current code — code evolves, lessons calcify. **Pattern:** before applying a Lessons-entry constraint that cites specific code paths, grep the cited file for the actual current behavior. One minute of verification prevents authoring against stale rules. |
| 2026-05-11 | `deposit_exists` Cause 5 — plan-agent evidence path convention mismatch. Audit (`bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md`) found 18 gate-failure lines across 3 verdict requests where the plan's `**Deposits:**` block declared bare `evidence/foo.txt` paths while the agent created files at `knowledge/qa/evidence/<slug>/foo.txt`. The bare paths don't resolve via any gate strategy (Strategy 0 tries `wt_path/evidence/foo.txt`, Strategy 2 tries `project_path/evidence/foo.txt` — neither exists). Root cause: ambiguous Rule 26 guidance ("evidence files do NOT need individual bullets") was read as permissive, not mandatory. Fix shipped this session: Rule 26 tightened to **mandatory** directory-bullet representation for evidence files, with explicit prohibition on individual evidence-file bullets. **Meta-lesson:** governance language matters — "do NOT need" reads as optional ("OK if I want to"), "MUST be represented by ... do NOT list" reads as mandatory. When a rule's intent is mandatory, the language must be mandatory. Soft language invites the workaround the rule was designed to prevent. |
| 2026-05-11 | Pre-executable scan-for-contradictions caught a stale rule before the governance edit shipped. The Rule 26 fix plan started as a one-line tightening of evidence-path guidance. While drafting, the Planner noticed line 738's "list the evidence directory as a single bullet" contradicted the 2026-04-19 Lesson "Do NOT list a directory path in the block." Rather than authoring the executable against the contradiction, the Planner deposited a tiny canary diagnostic (`diagnostic-rule-26-directory-bullet-canary-2026-05-11`) to verify the current gate behavior empirically. Diagnostic confirmed directories resolve via `isdir()` at every strategy, identified commit `e609ad3` as the change that made the 2026-04-19 Lesson stale, and authorized Path A (directory-only) as the correct resolution. Cost: one 2-minute diagnostic. Savings: a governance edit shipped against an unverified contradiction would have either propagated the stale Lesson or required a v4.36 corrective. **Pattern:** during executable plan authoring, if surrounding rules contradict each other on the topic being edited, the contradiction is the first thing to resolve — empirically, not by inference. The diagnostic-before-executable discipline applies to governance edits as strongly as to code changes. |

---

## Forge Observations
```

Verify the byte sequence `matches. |\n\n---\n\n## Forge Observations` exists
exactly once in PLANNER_TEMPLATE.md before applying. If it does not exist
exactly once, halt and report — do not attempt a near-miss replacement.

### Verification before commit

After applying all three edits, run these greps against `PLANNER_TEMPLATE.md`
and confirm each returns exactly 1 match:

```bash
grep -c "Version:.*4.35" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md
grep -c "MUST be represented by the evidence directory" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md
grep -c "Do NOT list individual evidence files" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md
grep -c "is \*\*stale\*\*. Commit" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md
grep -c "Cause 5 — plan-agent evidence path convention mismatch" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md
grep -c "Pre-executable scan-for-contradictions caught a stale rule" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md
```

Each must return 1. If any returns 0, the edit failed — re-apply before
committing.

### Commit

The PLANNER_TEMPLATE.md edit commits to the **governance-root repo** at
`/Users/marklehn/Desktop/GitHub/`, NOT to the bellows project repo. Run:

```bash
cd /Users/marklehn/Desktop/GitHub/ && \
git add PLANNER_TEMPLATE.md && \
git commit -m "docs(planner): Rule 26 evidence-path tightening, v4.35

- Tighten Rule 26 line 738: evidence files MUST be represented by the
  directory bullet alone, individual evidence-file bullets are prohibited.
- Append three Lessons rows:
  - Retraction of stale 2026-04-19 directory-prohibition lesson (commit
    e609ad3 made it stale).
  - Capture of deposit_exists Cause 5 root cause.
  - Diagnostic-before-executable discipline win (canary caught the
    contradiction before shipping).
- Source: deposit-exists-false-positive-audit-2026-05-11,
  rule-26-directory-bullet-canary-2026-05-11."
```

Do NOT push — CEO handles push.

### Dev log

Deposit a brief dev log to
`bellows/knowledge/development/rule-26-evidence-path-fix-dev-log-2026-05-11.md`
capturing: the three edits applied (with line numbers), the verification grep
output (paste the literal counts), and the commit SHA. Keep it under 60 lines.

Commit the dev log to the bellows project repo:

```bash
cd /Users/marklehn/Desktop/GitHub/bellows/ && \
git add knowledge/development/rule-26-evidence-path-fix-dev-log-2026-05-11.md && \
git commit -m "docs(bellows): rule-26 evidence-path fix dev log"
```

**Deposits:**
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
- `bellows/knowledge/development/rule-26-evidence-path-fix-dev-log-2026-05-11.md`

## STEP 2 — QA: Verify Rule 26 evidence-path edits landed correctly

Read first:
- `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md`
- `bellows/knowledge/development/rule-26-evidence-path-fix-dev-log-2026-05-11.md`

You are the QA Analyst. Verify Step 1's edits to PLANNER_TEMPLATE.md via grep
checks and markdown wellformedness. No test suite exists for governance markdown;
this QA is grep-driven plus structural sanity.

**Method:**

For each check below, capture the literal command output to an evidence file
under `bellows/knowledge/qa/evidence/rule-26-evidence-path-fix-2026-05-11/` via
Python file I/O or shell redirect (`> filename`). Each check's evidence filename
is named in the bullet.

1. **grep_version.txt** — verify version bumped:
   `grep -n "Version:.*4.35" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
   Expect 1 match.

2. **grep_tightened_guidance.txt** — verify tightened guidance present:
   `grep -n "MUST be represented by the evidence directory" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
   Expect 1 match.

3. **grep_prohibition.txt** — verify explicit prohibition present:
   `grep -n "Do NOT list individual evidence files" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
   Expect 1 match.

4. **grep_stale_lesson_retraction.txt** — verify Row A landed:
   `grep -n "is \*\*stale\*\*. Commit" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
   Expect 1 match.

5. **grep_cause_5_lesson.txt** — verify Row B landed:
   `grep -n "Cause 5 — plan-agent evidence path convention mismatch" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
   Expect 1 match.

6. **grep_discipline_win_lesson.txt** — verify Row C landed:
   `grep -n "Pre-executable scan-for-contradictions caught a stale rule" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
   Expect 1 match.

7. **markdown_wellformed.txt** — verify the file still parses cleanly. Run via
   Python and pipe stdout to the evidence file:

   ```python
   import sys
   with open('/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md') as f:
       content = f.read()
   assert content.count('```') % 2 == 0, 'unbalanced code fences'
   # Verify the Lessons table has not been broken — every row in the section
   # should have at least three pipe characters (two-column markdown row).
   in_lessons = False
   broken = []
   for i, line in enumerate(content.splitlines(), 1):
       stripped = line.lstrip()
       if stripped.startswith('## Lessons'):
           in_lessons = True
           continue
       if in_lessons and stripped.startswith('## '):
           break  # next section reached
       if in_lessons and stripped.startswith('|') and not stripped.startswith('|---'):
           if line.count('|') < 3:
               broken.append((i, line[:80]))
   if broken:
       for i, l in broken:
           print(f'line {i}: malformed Lessons row: {l}')
       sys.exit(1)
   print('PASS: code fences balanced, Lessons table well-formed')
   ```

8. **git_log.txt** — verify the commit landed in governance-root:
   `cd /Users/marklehn/Desktop/GitHub/ && git log --oneline -3 -- PLANNER_TEMPLATE.md`
   Expect the top entry to be the Rule 26 v4.35 commit.

9. **Run Rule 20 self-check** in the QA report with:

   ```python
   required_evidence_files = [
       'grep_version.txt',
       'grep_tightened_guidance.txt',
       'grep_prohibition.txt',
       'grep_stale_lesson_retraction.txt',
       'grep_cause_5_lesson.txt',
       'grep_discipline_win_lesson.txt',
       'markdown_wellformed.txt',
       'git_log.txt',
   ]
   ```

10. **Deposit a QA report** at
    `bellows/knowledge/qa/rule-26-evidence-path-fix-qa-2026-05-11.md` with:
    - Summary (one paragraph).
    - Results table (one row per check 1–8) using only ✅/❌/⚠ glyphs as
      standalone cell values. No hedging keywords ("mostly", "appears to",
      "likely", "should", "probably") in positive-status rows.
    - Evidence file references (one row per evidence file).
    - Rule 20 self-check banner and PASSED line at the end.

### Commit

The QA report and evidence files commit to the **bellows project repo**, NOT
governance root. Run:

```bash
cd /Users/marklehn/Desktop/GitHub/bellows/ && \
git add knowledge/qa/rule-26-evidence-path-fix-qa-2026-05-11.md \
        knowledge/qa/evidence/rule-26-evidence-path-fix-2026-05-11/ && \
git commit -m "qa(rule-26): verify v4.35 evidence-path edits landed"
```

Do NOT push.

**Out of scope:**
- Do not modify PLANNER_TEMPLATE.md.
- Do not run any test suite — there isn't one for governance markdown.
- Do not assess whether the rule changes are *correct* — that's the Planner's
  Rule 22 verification step. QA only verifies that what Step 1 declared it
  would do actually landed in the file.

**Deposits:**
- `bellows/knowledge/qa/rule-26-evidence-path-fix-qa-2026-05-11.md`
- `bellows/knowledge/qa/evidence/rule-26-evidence-path-fix-2026-05-11/` (multiple files per Rule 20 self-check)
