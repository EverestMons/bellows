# Executable — Rule 20 Self-Check Block Single-Source File

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small-to-Medium | **Total Steps:** 2 | **pause_for_verdict:** after_step_1

---

## Context

Closes BACKLOG `2026-05-10: Rule 20 self-check block in plans should reference canonical PLANNER_TEMPLATE, not re-author` using migration shape (d.2) per CEO 2026-05-10.

**Migration shape (d.2) — single-source template file:**
- New file `RULE_20_SELF_CHECK_BLOCK.md` at governance root publishes the canonical Python block as a copy-paste template (with the existing 4 sentinel placeholders intact).
- PLANNER_TEMPLATE Rule 20 stops inlining the block; instead references the new file as the single source of truth.
- BELLOWS_QA.md and INVOICE_SECURITY_TESTING_ANALYST.md get a one-paragraph instruction pointing QA agents at the canonical file (they do NOT inline the block — only the canonical file reproduces it).
- In-flight and closed plans are not touched. New pattern applies to plans authored after this lands.

**Diagnostic that motivated this scope:** `bellows/knowledge/decisions/Done/diagnostic-rule-20-block-sourcing-2026-05-10.md` and findings at `bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md`.

**Key facts the executable must respect (from diagnostic):**
- Canonical block is 60+ lines of Python (PLANNER_TEMPLATE.md lines 512–576).
- Banner string `Rule 20 — QA Self-Check Results` is enforced by `gates.py::_gate_rule_20_self_check` — must NOT be altered.
- Rule 22(e) (PLANNER_TEMPLATE.md line 646) is position-agnostic; do NOT modify.
- Three in-flight plans exist (bellows in-progress-executable-session-wrap-2026-05-08, bellows in-progress-diagnostic-rule-20-block-sourcing-2026-05-10 [closing in this session], invoice-pulse verdict-pending-executable-action-queue-aggregation-2026-05-07) — leave them alone.

---

## Execution Map

Step 1 (DEV) → Step 2 (QA)

---

## STEP 1 — Developer: ship the single-source file and update references

**Agent:** Bellows Developer (`bellows/agents/BELLOWS_DEVELOPER.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/`

**Deposits:**
- `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (created)
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` (modified — Rule 20 rewritten)
- `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md` (modified — reference paragraph added)
- `/Users/marklehn/Desktop/GitHub/invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` (modified — reference paragraph added)
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/rule-20-single-source-2026-05-10.md` (dev log)

### Prompt

You are the Bellows Developer. Read your agent file at `bellows/agents/BELLOWS_DEVELOPER.md` and the diagnostic findings at `bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md` before making any edits.

This is a cross-repo governance change. Four files in three locations: governance root (2), bellows (1), invoice-pulse (1). Per Rule 8 governance-root pattern: governance-root files commit together; bellows and invoice-pulse changes commit separately in their own repos.

### Edit 1 — Create `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`

Create this file at the governance root. Content:

```markdown
# Rule 20 Self-Check Block — Canonical Template

**Single source of truth.** This file is the ONLY location in the system that publishes the Rule 20 self-check Python block. PLANNER_TEMPLATE.md Rule 20 references this file. Project QA agent files reference this file. Plans reference this file. No other file reproduces the block.

**Authority:** PLANNER_TEMPLATE.md Rule 20 (governance) and `bellows/gates.py::_gate_rule_20_self_check` (enforcement). Banner string `Rule 20 — QA Self-Check Results` is enforced byte-for-byte. Do not paraphrase, substitute, or reformat.

---

## How Plans Reference This Block

Every QA step in every executable plan instructs the QA agent to run the canonical Rule 20 self-check. The plan does NOT inline the Python block. Instead, the plan provides the four context values the QA agent will use, then directs the agent to the canonical file.

**Plan-side template** (paste this into every QA step prompt):

> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
>
> - `plan_slug`: `<plan-filename-without-md>`
> - `qa_report_path`: `<absolute-path-to-qa-report>`
> - `evidence_dir`: `<absolute-path-to-evidence-directory>`
> - `required_evidence_files`: `[<filename1>, <filename2>, ...]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.

The QA agent reads this file, copies the Python block, fills in the four placeholders with the values the plan provided, runs it, and includes stdout in the QA report.

---

## Canonical Python Block

Copy the block below verbatim. Replace ONLY the four placeholder lines marked `# PLACEHOLDER —`. Do not modify any other line, including comments and prints.

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "<plan-filename-without-md>"  # PLACEHOLDER — set from plan prompt
qa_report_path = "<absolute-path-to-qa-report.md>"  # PLACEHOLDER — set from plan prompt
evidence_dir = "<absolute-path-to-evidence-dir>/"  # PLACEHOLDER — set from plan prompt
required_evidence_files = [
    # PLACEHOLDER — list every filename this plan's QA step is required to deposit
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
# Glyph-agnostic positive-status detection. Any of these tokens, when appearing
# as a standalone cell value in a markdown table row, marks that row as a
# positive status row subject to the hedging scan. Bounded matching (cell
# equality, not substring) prevents false positives on words like "completed"
# or "passing". Closes the v4.19 bypass where QA could use "OK" instead of
# "✅" to evade the scan.
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    """True if the line is a markdown table row marked with a positive status token."""
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
    return False

failures = []
if not os.path.isdir(evidence_dir):
    failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
else:
    for fname in required_evidence_files:
        fpath = os.path.join(evidence_dir, fname)
        if not os.path.isfile(fpath):
            failures.append(f"CRITICAL: evidence file missing: {fpath}")
        elif os.path.getsize(fpath) == 0:
            failures.append(f"CRITICAL: evidence file empty: {fpath}")
if os.path.isfile(qa_report_path):
    with open(qa_report_path, "r") as f:
        report = f.read()
    for line in report.splitlines():
        if is_positive_row(line):
            lower = line.lower()
            for kw in hedging_keywords:
                if kw in lower:
                    failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
                    break
else:
    failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
print("=" * 60)
print("Rule 20 — QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

---

## Banner String Invariant

The line `print("Rule 20 — QA Self-Check Results")` MUST appear verbatim — including the em-dash (—, U+2014, not a hyphen) and the spaces. `bellows/gates.py::_gate_rule_20_self_check` matches the banner string by byte. Any substitution (`RULE 20 SELF-CHECK`, `Rule 20 Self-Check`, `Rule 20 -- QA Self-Check`, etc.) will cause the gate to fail.

The line beginning with `PASSED — SELF-CHECK PASSED` MUST appear after the banner on success. Same byte-level enforcement.

---

## When This File Changes

- Bug fixes in the Python block: update HERE FIRST, then verify `bellows/gates.py::_gate_rule_20_self_check` still matches the banner string and that `tests/test_gates.py` passes.
- Banner string changes: REQUIRES a coordinated gate-update plan. The banner is enforced in `bellows/gates.py` lines ~289–290 (`banner = "Rule 20 — QA Self-Check Results"` and the `PASSED — SELF-CHECK PASSED` startswith check). Do not change the banner without updating the gate.
- Format changes (e.g., adding new check categories): update the prose preamble of PLANNER_TEMPLATE Rule 20 to document the new behavior, and run a population audit on recent QA reports to confirm the new format is backward-compatible.

---

## History

- **2026-05-10:** Created as the single-source canonical location. Migration from PLANNER_TEMPLATE.md v4.35 Rule 20 inline publication. Migration plan: `bellows/knowledge/decisions/Done/executable-rule-20-single-source-2026-05-10.md`.
```

### Edit 2 — Rewrite PLANNER_TEMPLATE.md Rule 20

Open `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Locate Section 20 (spans lines 506–598 per the diagnostic). Replace the entire section with the rewritten version below.

**Replace from line 506 (`### 20. Mandatory QA self-check Python block`) through line 598 (the line ending `...what os.path.isfile() returns.`) with this content:**

```markdown
### 20. Mandatory QA self-check Python block

Every QA step in every executable plan MUST end with a mandatory Python self-check block that runs AFTER the QA report is written but BEFORE the plan can close. The self-check is mechanical — it does not depend on the agent's judgment, and the agent cannot fake its output because the Python output is deterministic. The agent must execute the block, include its literal output in the QA report, and halt the plan if any check fails. The self-check is glyph-agnostic — it detects positive-status rows by matching any of {✅, OK, PASS, [x], done, complete, verified} as a standalone cell value, preventing bypass via alternate status indicators.

**The canonical block lives at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`.** This is the single source of truth. The Planner does NOT inline the Python block into plans. Project QA agent files do NOT inline the block. Only the canonical file reproduces the block.

**Plan-side template** (paste this into every QA step prompt):

> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
>
> - `plan_slug`: `<plan-filename-without-md>`
> - `qa_report_path`: `<absolute-path-to-qa-report>`
> - `evidence_dir`: `<absolute-path-to-evidence-directory>`
> - `required_evidence_files`: `[<filename1>, <filename2>, ...]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.

**Why a single-source file:** PLANNER_TEMPLATE Lessons 2026-05-10 documented two failure modes: (a) Planners paraphrasing the banner string when re-authoring the block, tripping `bellows/gates.py::_gate_rule_20_self_check`; (b) a banner-substitution drift rate of ~30% across recent plans. The single-source file physically prevents substitution — the Planner never authors the block, so it cannot paraphrase it.

**The Planner's job when writing a QA step:**

1. Enumerate every non-trivial check in the QA step.
2. Assign each check a short evidence filename.
3. Provide the QA agent with the four context values (`plan_slug`, `qa_report_path`, `evidence_dir`, `required_evidence_files`) via the plan-side template above.
4. Write the QA prompt so each check deposits output to evidence files.

**The QA agent's job:**

1. Execute every check, depositing output to evidence files.
2. Fill in the verification table citing evidence file paths.
3. Read `RULE_20_SELF_CHECK_BLOCK.md` at the governance root, copy the canonical Python block, fill in the four placeholders with values from the plan prompt, and run it.
4. Include literal stdout in the QA report.
5. If FAILED, STOP — report to CEO.
6. If PASSED, proceed with closure.

**When a self-check fails:**

CEO reviews the FAILED output and decides: (a) re-run after fixing the deficient evidence, (b) escalate to a corrective plan, or (c) override with explicit reasoning logged in the verdict.

**This rule is the enforcement teeth for Rules 17, 18, and 19.** Rule 17 says verify deliverables. Rule 18 says deposit evidence files. Rule 19 says hedging language is invalid. Rule 20 is the Python block that mechanically checks whether all three rules were actually followed. An agent can lie in its prose, but it can't lie about what `os.path.isfile()` returns.
```

**Critical:** Use `Filesystem:read_text_file` to read lines 504–600 of PLANNER_TEMPLATE.md FIRST to get the exact pre-edit boundary text for the surrounding rules (Rule 19 above, Rule 21 or next-numbered rule below). Then use `Desktop Commander:edit_block` with a `old_string` that includes ~3 lines before line 506 and ~3 lines after line 598, replacing with the new Rule 20 plus those same surrounding lines. This anchors the edit precisely against PLANNER_TEMPLATE's actual content.

Do NOT modify Rule 22(e) (line 646), Rule 26 deposit references to Rule 20 (lines 747, 757), or the 2026-05-05 Lessons entry (line 1271). Those cross-references remain accurate against the rewritten Rule 20.

### Edit 3 — Update `bellows/agents/BELLOWS_QA.md`

Insert a new `## Rule 20 Self-Check (Canonical Block Reference)` section between the existing `## Guardrails` section (line 145) and `## Project Knowledge Base Index` section (line 154). Content:

```markdown
## Rule 20 Self-Check (Canonical Block Reference)

The canonical Rule 20 self-check Python block lives at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. When a QA step prompt instructs you to run the Rule 20 self-check:

1. Read `RULE_20_SELF_CHECK_BLOCK.md` at the governance root.
2. Copy the Python block from its `## Canonical Python Block` section.
3. Replace the four placeholder lines marked `# PLACEHOLDER —` with the values the plan prompt provided (`plan_slug`, `qa_report_path`, `evidence_dir`, `required_evidence_files`).
4. Do NOT modify any other line of the block — including the banner print `Rule 20 — QA Self-Check Results` (the em-dash and spacing are byte-significant; the Bellows gate matches the banner string literally).
5. Run the block. Include its literal stdout in the QA report.
6. If the block prints `FAILED`, STOP — do not proceed with plan closure. Report the failure and wait for CEO direction.
7. If the block prints `PASSED`, the self-check is complete. Continue with closure.

The block is NOT reproduced in this agent file. It lives in one place only. If you find yourself authoring or paraphrasing the block from memory, STOP and read the canonical file instead.
```

Also update line 16 (Role Summary) — the existing text mentions Rule 20. Append a clause to that sentence indicating the canonical source: change `"...enforces Rule 17 deliverable verification, Rule 20 self-check blocks, and Rule 21 test scope declarations..."` to `"...enforces Rule 17 deliverable verification, Rule 20 self-check blocks (canonical source: governance-root RULE_20_SELF_CHECK_BLOCK.md), and Rule 21 test scope declarations..."`.

Do NOT inline the Python block anywhere in this file.

### Edit 4 — Update `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md`

The diagnostic found this file has ZERO existing Rule 20 references. Insert a new `## Rule 20 Self-Check (Canonical Block Reference)` section between the existing `## Guardrails` section (line 162) and `## Project Knowledge Base Index` section (line 176). Use the same content as Edit 3 (BELLOWS_QA.md insertion). The block reference and instructions are identical across projects — only the canonical file path matters.

Do NOT inline the Python block.

### Commits

Per Rule 8 governance-root pattern:

1. **Governance root commit:** `RULE_20_SELF_CHECK_BLOCK.md` (created) + `PLANNER_TEMPLATE.md` (Rule 20 rewritten) committed together at `/Users/marklehn/Desktop/GitHub/`. Commit message suggestion: `feat(governance): Rule 20 single-source canonical block — v4.35 → v4.36`.

2. **Bellows commit:** `bellows/agents/BELLOWS_QA.md` (modified) + the dev log + this plan file's lifecycle moves committed in the bellows repo. Commit message suggestion: `docs(qa): reference canonical Rule 20 block in BELLOWS_QA.md`.

3. **Invoice-pulse commit:** `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` (modified) committed in the invoice-pulse repo. Commit message suggestion: `docs(qa): reference canonical Rule 20 block in INVOICE_SECURITY_TESTING_ANALYST.md`.

Bump PLANNER_TEMPLATE version header from `**Version:** 4.35` to `**Version:** 4.36` and update the `**Last Updated:**` line to `2026-05-10 (v4.36)`. Add a Lessons Learned entry at the end of the file (chronological with existing entries) summarizing the migration:

```markdown
| 2026-05-10 | Rule 20 single-source migration: the canonical Python block migrated from inline PLANNER_TEMPLATE publication to a dedicated file at `RULE_20_SELF_CHECK_BLOCK.md` (governance root). Motivation: ~30% of recent plans used non-canonical banner strings (e.g., `RULE 20 SELF-CHECK` vs. canonical `Rule 20 — QA Self-Check Results`), tripping `bellows/gates.py::_gate_rule_20_self_check`. The single-source file physically prevents Planner-side substitution — the Planner never authors the block, so paraphrasing is impossible. Project QA agent files (`bellows/agents/BELLOWS_QA.md`, `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md`) reference the canonical file rather than inlining. **Lesson:** when a Planner-authored artifact has a strict byte-level invariant enforced by a downstream gate (banner string, regex pattern, filename format, etc.), and the artifact is large enough that paraphrasing is plausible (>10 lines), single-source the artifact in a dedicated file with explicit byte-invariant warnings. Do not rely on Planner discipline to copy verbatim — the failure rate observed pre-migration was 30%. |
```

### Test discipline

This change touches no Python code in bellows or invoice-pulse. No test suite changes expected. Confirm by running `pytest -x` in `/Users/marklehn/Desktop/GitHub/bellows/`:

- Expected: same test count as pre-edit (246 passed, 1 pre-existing `test_run_step_timeout` failure).
- New failures: must be zero.

If any test fails that was passing before, stop and report — do NOT modify tests.

### Dev log

After landing the four edits and confirming tests pass, write a dev log at `bellows/knowledge/development/rule-20-single-source-2026-05-10.md` covering:

1. The four concrete edits made (file, action, summary).
2. LOC delta — count added/removed lines per file, net total. Note: governance-root files are tracked separately from bellows.
3. Test suite result — should be identical to pre-edit.
4. Three commit SHAs (governance-root, bellows, invoice-pulse).
5. Verify by `cat RULE_20_SELF_CHECK_BLOCK.md | grep "Rule 20 — QA Self-Check Results"` — must return exactly one line with the canonical banner (proves the byte-invariant survived the migration).

### Output Receipt

```
**Step:** 1
**Status:** Complete
**Deposits:**
- RULE_20_SELF_CHECK_BLOCK.md (created at governance root)
- PLANNER_TEMPLATE.md (modified — Rule 20 rewritten, version bump, Lessons entry)
- bellows/agents/BELLOWS_QA.md (modified)
- invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md (modified)
- bellows/knowledge/development/rule-20-single-source-2026-05-10.md (created)
**Commits:** <gov-sha>, <bellows-sha>, <invoice-pulse-sha>
```

STOP after Step 1. Do not advance to Step 2 — the Planner verifies the dev work before authorizing QA.

---

## STEP 2 — QA: verify the migration

**Agent:** Bellows QA (`bellows/agents/BELLOWS_QA.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/`

**Deposits:**
- `bellows/knowledge/qa/rule-20-single-source-qa-2026-05-10.md` (QA report)
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/` (evidence directory)
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/canonical-banner-grep.txt` (evidence file)
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/inline-block-search.txt` (evidence file)
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/test-suite-result.txt` (evidence file)

### Prompt

You are the Bellows QA agent. Read your agent file at `bellows/agents/BELLOWS_QA.md` and the dev log at `bellows/knowledge/development/rule-20-single-source-2026-05-10.md` before starting.

This is a cross-repo governance verification. Four files in three locations. Verify the byte-level invariants survived and that the single-source property is structurally enforced.

### Verification matrix

| # | Property | How to check | Evidence file |
|---|----------|--------------|---------------|
| 1 | `RULE_20_SELF_CHECK_BLOCK.md` exists at governance root | `os.path.isfile('/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md')` | inline in report |
| 2 | Canonical banner survives migration byte-exact | `grep -c "Rule 20 — QA Self-Check Results" /Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` — must return ≥1; deposit grep output | `canonical-banner-grep.txt` |
| 3 | PASSED line survives migration byte-exact | `grep -c "PASSED — SELF-CHECK PASSED" /Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` — must return ≥1 | inline in report |
| 4 | PLANNER_TEMPLATE Rule 20 no longer inlines the Python block | `grep -c "^import os, sys$" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — must return 0 (the block has migrated out); deposit grep output | `inline-block-search.txt` |
| 5 | PLANNER_TEMPLATE Rule 20 references the canonical file | `grep -c "RULE_20_SELF_CHECK_BLOCK.md" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — must return ≥1 | inline in report |
| 6 | PLANNER_TEMPLATE version bumped | `grep "^\\*\\*Version:\\*\\*" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — must show `4.36` | inline in report |
| 7 | BELLOWS_QA.md has new Rule 20 reference section | `grep -c "Rule 20 Self-Check (Canonical Block Reference)" /Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md` — must return 1 | inline in report |
| 8 | BELLOWS_QA.md does NOT inline the Python block | `grep -c "^import os, sys$" /Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md` — must return 0 | inline in report |
| 9 | INVOICE_SECURITY_TESTING_ANALYST.md has new Rule 20 reference section | `grep -c "Rule 20 Self-Check (Canonical Block Reference)" /Users/marklehn/Desktop/GitHub/invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` — must return 1 | inline in report |
| 10 | INVOICE_SECURITY_TESTING_ANALYST.md does NOT inline the Python block | `grep -c "^import os, sys$" /Users/marklehn/Desktop/GitHub/invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` — must return 0 | inline in report |
| 11 | Single-source invariant: canonical block appears in exactly one .md file in the governance tree | `grep -rl "Rule 20 — QA Self-Check Results" /Users/marklehn/Desktop/GitHub/ --include="*.md" --exclude-dir="Done" --exclude-dir="archived" --exclude-dir=".bellows-worktrees" --exclude-dir="logs"` — exclude historical plan files, lessons entries, and the diagnostic findings. The result should be `RULE_20_SELF_CHECK_BLOCK.md` plus PLANNER_TEMPLATE.md (which references it in prose) plus the LESSONS.md entry that mentions it. **Active publication** (the block itself) should only be in `RULE_20_SELF_CHECK_BLOCK.md` | inline in report |
| 12 | Bellows test suite unchanged | Run `cd /Users/marklehn/Desktop/GitHub/bellows && pytest -x 2>&1 | tail -20`. Must show same pass count as 2026-05-10 baseline (246 passed, 1 pre-existing failure). Deposit the tail output. | `test-suite-result.txt` |
| 13 | Three commits exist | `cd /Users/marklehn/Desktop/GitHub/ && git log -1 --oneline` and same for bellows and invoice-pulse subdirectories. All three commits dated 2026-05-10. | inline in report |
| 14 | LESSONS entry added to PLANNER_TEMPLATE | `grep "Rule 20 single-source migration" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — must return ≥1 match. | inline in report |

### QA report

Write to `bellows/knowledge/qa/rule-20-single-source-qa-2026-05-10.md` with one row per verification matrix item. Status column uses one of: ✅, OK, PASS. End with summary line: `Migration verified — N/14 checks passed.`

### Rule 20 self-check — using the new pattern

This QA step is the first plan to use the NEW single-source pattern. Run the canonical Rule 20 self-check from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use these values:

- `plan_slug`: `executable-rule-20-single-source-2026-05-10`
- `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/rule-20-single-source-qa-2026-05-10.md`
- `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/`
- `required_evidence_files`: `["canonical-banner-grep.txt", "inline-block-search.txt", "test-suite-result.txt"]`

Read `RULE_20_SELF_CHECK_BLOCK.md`, copy the Python block from its `## Canonical Python Block` section, fill in the four placeholders with the values above, run it, and include its literal stdout at the end of the QA report.

**This is the structural test of the migration** — if you can complete this step using only the new pattern (no inline block from the plan), the migration works as designed.

### Output Receipt

```
**Step:** 2
**Status:** Complete
**Deposits:**
- bellows/knowledge/qa/rule-20-single-source-qa-2026-05-10.md (created)
- bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/ (directory created with 3 evidence files)
**Verification:** N/14 checks passed
**Test suite:** <passed_count> passed, <pre_existing_failure_count> pre-existing failure, <new_failure_count> new failures
**Self-check:** PASSED (canonical block run from RULE_20_SELF_CHECK_BLOCK.md)
```

STOP after Step 2. Final-step verdict will be issued by the Planner after Rule 22 verification.

---

## Deliverables Summary

| Step | Agent | Deliverable | Location |
|------|-------|-------------|----------|
| 1 | DEV | `RULE_20_SELF_CHECK_BLOCK.md` (created) | governance root |
| 1 | DEV | `PLANNER_TEMPLATE.md` (modified) | governance root |
| 1 | DEV | `BELLOWS_QA.md` (modified) | bellows/agents/ |
| 1 | DEV | `INVOICE_SECURITY_TESTING_ANALYST.md` (modified) | invoice-pulse/agents/ |
| 1 | DEV | dev log (created) | bellows/knowledge/development/ |
| 2 | QA | QA report + evidence directory (created) | bellows/knowledge/qa/ |
