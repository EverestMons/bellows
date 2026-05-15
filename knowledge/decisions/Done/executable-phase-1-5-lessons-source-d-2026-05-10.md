# Executable — Phase 1.5 patch: add LESSONS.md as Source D

**Project:** bellows | **Type:** executable | **Steps:** 2 | **Priority:** 1 | **auto_close:** false | **pause_for_verdict:** after_step_1

## Context

LESSONS.md at governance root is the only cross-project knowledge artifact and is currently outside Phase 1.5's scope. The 2026-05-09 entry on Rule 20 banner format recurred on 2026-05-10 because Phase 1.5 (which covers `[project]/knowledge/research/agent-prompt-feedback.md`, recent research, recent QA) doesn't include LESSONS.md. The Planner followed Phase 1.5 correctly and still missed the lesson because the lesson lives somewhere Phase 1.5 doesn't cover. Captured as meta-lesson at LESSONS.md 2026-05-10 (entry "Meta-lesson: LESSONS.md not in Phase 1.5 scope is itself the bug").

This plan patches PLANNER_TEMPLATE.md Phase 1.5 to add Source D — LESSONS.md (governance root) — with bounded scope to keep read cost cheap as the file grows.

**Cross-repo plan:** edits land at governance root (`/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`), commit goes to the governance-root repo. The plan housekeeping (move-to-Done, dev log) commits to bellows. This is a split-commit pattern per PLANNER_TEMPLATE Output Format > "Commit repo for governance-root edits".

## Execution Map

Step 1 (DOC) → Step 2 (QA)

## STEP 1 — Documentation Agent: patch Phase 1.5 to add Source D (LESSONS.md)

**Agent:** Bellows Documentation Analyst
**Deposits:**
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` (modified — governance root)
- `bellows/knowledge/development/phase-1-5-lessons-source-d-dev-log-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_DOCUMENTATION_ANALYST.md, then read /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md to understand the current Phase 1.5 structure (lines ~50-85, "Phase 1.5 — Recent Knowledge Scan (Mandatory)" section). You are patching Phase 1.5 to add LESSONS.md as a fourth mandatory context source.

OBJECTIVE
Surgical edits to /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md. Five anchored edits, no other changes. Bump version v4.34 → v4.35.

EXACT EDITS

VERIFY THE LINE NUMBERS in the actual file before editing — line counts may have shifted. Use Filesystem:edit_file with old_text/new_text exact-match anchors.

### EDIT 1 — Version bump

Find:
    **Version:** 4.34
    **Last Updated:** 2026-05-05 (v4.34)

Replace with:
    **Version:** 4.35
    **Last Updated:** 2026-05-10 (v4.35)

### EDIT 2 — Phase 1.5 header sentence: "three" → "four"

Find:
    Before writing ANY prompt (diagnostic, fix, or orchestration step), the Planner reads three knowledge sources to pick up context that has accumulated outside formal plan files. Informal findings, agent observations, and recent QA notes live in these locations — not in `knowledge/decisions/` plans, which are templates rather than records.

Replace with:
    Before writing ANY prompt (diagnostic, fix, or orchestration step), the Planner reads four knowledge sources to pick up context that has accumulated outside formal plan files. Three are project-scoped (informal findings, agent observations, and recent QA notes); the fourth is cross-project (governance-root lessons that apply across all projects). These live outside `knowledge/decisions/` plans, which are templates rather than records.

### EDIT 3 — Insert Source D after Source C, before "This is NOT optional"

Find (this is the END of Source C, immediately before the "This is NOT optional" paragraph):
    QA reports frequently surface Advisory-level findings (🔵) that go beyond the immediate verification scope. These are often useful context the Planner would otherwise miss.

    **This is NOT optional.** Skipping any of the three sources means operating with stale context. The feedback log alone is insufficient — findings accumulate across all three locations, and the Planner's "lacks context" failure mode (documented in the Informal Sharing Friction Audit of 2026-04-09) is driven by reading only one of the three.

Replace with:
    QA reports frequently surface Advisory-level findings (🔵) that go beyond the immediate verification scope. These are often useful context the Planner would otherwise miss.

    **Source D — Cross-project lessons:**
    - `/Users/marklehn/Desktop/GitHub/LESSONS.md`

    Bounded scope to keep read cost cheap as the file grows:
    - **All entries from the last ~14 days** (catches recent lessons before they fade)
    - **All entries tagged `planner-discipline`** regardless of age (catches discipline rules permanently)

    Other tags (`bellows-architecture`, project-specific patterns, etc.) are read on-demand when the current task touches that area, not every session. This is the only cross-project knowledge artifact in the protocol — lessons captured here apply across all projects, and missing one means repeating a known failure on a different project.

    **This is NOT optional.** Skipping any of the four sources means operating with stale context. The feedback log alone is insufficient — findings accumulate across all four locations, and the Planner's "lacks context" failure mode (documented in the Informal Sharing Friction Audit of 2026-04-09, expanded 2026-05-10 with the LESSONS.md gap) is driven by reading only a subset.

### EDIT 4 — "Why three sources" → "Why four sources"

Find:
    **Why three sources instead of one:** Informal findings from agent work naturally accumulate in whichever knowledge-base location fits best at the moment of capture. Feedback entries land in the feedback log; diagnostic findings land in research; verification-adjacent observations land in QA. The Planner needs all three to reconstruct what has happened across agent sessions since the last planning pass.

Replace with:
    **Why four sources instead of one:** Informal findings from agent work naturally accumulate in whichever knowledge-base location fits best at the moment of capture. Feedback entries land in the feedback log; diagnostic findings land in research; verification-adjacent observations land in QA; cross-project discipline rules and meta-patterns land in LESSONS.md. The Planner needs all four to reconstruct what has happened across agent sessions since the last planning pass — three project-scoped, one cross-project.

### EDIT 5 — None (only 4 edits this plan; numbered for clarity)

DEV LOG

Deposit `bellows/knowledge/development/phase-1-5-lessons-source-d-dev-log-2026-05-10.md` with:
- The exact 4 edits applied to PLANNER_TEMPLATE.md (old_text → new_text for each)
- Confirmation that version bumped 4.34 → 4.35
- Confirmation that NO other lines in PLANNER_TEMPLATE.md were touched (run `git diff` and capture output; only the 4 edited regions should appear)
- Reference to LESSONS.md 2026-05-10 meta-entry that prompted this patch
- Reference to LESSONS.md 2026-05-09 entry that the patch operationalizes

GIT COMMITS

TWO commits per the cross-repo split pattern:

Commit 1 (governance root, /Users/marklehn/Desktop/GitHub/):
    docs(planner): Phase 1.5 v4.35 — add Source D (LESSONS.md) with bounded scope

    Includes only PLANNER_TEMPLATE.md and LESSONS.md (LESSONS.md was edited earlier in this session by Planner with the meta-lesson that prompted this patch — include it in this commit if not already committed).

Commit 2 (bellows repo, /Users/marklehn/Desktop/GitHub/bellows/):
    docs(dev): Phase 1.5 patch dev log

    Includes only the dev log file.

Push both.

CONSTRAINTS
- Use Filesystem:edit_file for the surgical edits, NOT write_file or rewrites. Old_text must match exactly; the patch fails loud if the file shifted.
- Do NOT modify any other section of PLANNER_TEMPLATE.md. Surgical only.
- Do NOT touch any other governance-root file (COMPANY.md, SPECIALIST_TEMPLATE.md, GUARDRAILS.md).
- Verify the commit-2 dev log path is correct (bellows/knowledge/development/, NOT governance root).
- If LESSONS.md is uncommitted at session start, commit 1 includes both PLANNER_TEMPLATE.md and LESSONS.md. If LESSONS.md is already committed (from earlier in the session), commit 1 includes only PLANNER_TEMPLATE.md. Run `git status` at governance root to determine which case.

OUTPUT RECEIPT
End with status (Complete / Blocked), summary of edits applied, and deposit paths.
```

## STEP 2 — Bellows QA: verify the patch

**Agent:** Bellows QA
**Deposits:**
- `bellows/knowledge/qa/phase-1-5-lessons-source-d-qa-2026-05-10.md`
- `bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/git_diff.txt`
- `bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/grep_source_d.txt`

**Prompt:**

```
Read agents/BELLOWS_QA.md, then read the dev log at bellows/knowledge/development/phase-1-5-lessons-source-d-dev-log-2026-05-10.md. You are verifying the Phase 1.5 patch shipped in Step 1.

VERIFICATION CHECKS

(1) Read /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md and confirm:
    (a) Version line shows `**Version:** 4.35`
    (b) Last Updated line shows `**Last Updated:** 2026-05-10 (v4.35)`
    (c) Phase 1.5 header paragraph mentions "four knowledge sources" (not "three")
    (d) Source D section exists with the literal heading `**Source D — Cross-project lessons:**`
    (e) Source D references `/Users/marklehn/Desktop/GitHub/LESSONS.md` as a bullet
    (f) Source D bounded scope mentions both "last ~14 days" and "planner-discipline"
    (g) "This is NOT optional" paragraph references "any of the four sources" (not "any of the three")
    (h) "Why N sources" paragraph reads "Why four sources instead of one"

(2) Run `git diff` at governance root and capture full output:
    cd /Users/marklehn/Desktop/GitHub
    git --no-pager diff HEAD~2 HEAD -- PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/git_diff.txt
    
    (Use HEAD~2 to span both commits if LESSONS.md was committed in the same window; adjust to HEAD~1 if only one governance-root commit was made.)
    
    Verify the diff shows ONLY the 4 edited regions (version line, Phase 1.5 header sentence, Source D insertion + "This is NOT optional" rewrite, "Why N sources" rewrite). No other regions should appear in the diff.

(3) Grep for Source D presence and capture:
    cd /Users/marklehn/Desktop/GitHub
    grep -n "Source D" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/grep_source_d.txt
    grep -n "LESSONS.md" PLANNER_TEMPLATE.md >> bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/grep_source_d.txt
    grep -n "four knowledge sources" PLANNER_TEMPLATE.md >> bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/grep_source_d.txt
    
    Verify each grep returns at least one match.

(4) Confirm bellows test suite still passes (no regressions from any side-effects):
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest 2>&1 | tail -10
    
    Expected: 245 passed (unchanged from previous session-end baseline), 1 pre-existing test_run_step_timeout failure unchanged.

QA REPORT FORMAT

Deposit at bellows/knowledge/qa/phase-1-5-lessons-source-d-qa-2026-05-10.md with:
- Status table: each verification check (1a-1h, 2, 3, 4) with ✅/❌ and one-line evidence
- Evidence file references in the Evidence column (cite the exact path)
- Final verdict line: ALL CHECKS PASSED or LIST OF FAILURES

RULE 20 SELF-CHECK

End the QA report with the canonical Rule 20 self-check Python block from PLANNER_TEMPLATE Rule 20. **USE THE VERBATIM TEMPLATE** — paste the block from PLANNER_TEMPLATE Rule 20 with only variable substitutions (`plan_slug`, `qa_report_path`, `evidence_dir`, `required_evidence_files`). DO NOT rewrite the print statements; the literal banner string `Rule 20 — QA Self-Check Results` (with em-dash U+2014) and the literal output line `PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.` are load-bearing strings the Bellows gate checks for.

ACTUALLY EXECUTE THE BLOCK after writing the QA report (use python3 to run it as a script or inline) and include the literal stdout in the QA report. Do NOT just include the script without running it.

Variable substitutions:
- plan_slug = "executable-phase-1-5-lessons-source-d-2026-05-10"
- qa_report_path = "bellows/knowledge/qa/phase-1-5-lessons-source-d-qa-2026-05-10.md"
- evidence_dir = "bellows/knowledge/qa/evidence/phase-1-5-lessons-source-d-2026-05-10/"
- required_evidence_files = ["git_diff.txt", "grep_source_d.txt"]

GIT COMMITS

ONE commit (bellows repo):
    docs(qa): Phase 1.5 Source D patch verification

Include the QA report and both evidence files. Push.

OUTPUT RECEIPT
End with status (Complete / Blocked), final verdict line, and deposit paths.
```

**STOP. Do NOT proceed beyond Step 2 without CEO verdict. After Step 2 completes, the Planner moves the plan to Done/ via Filesystem:move_file.**
