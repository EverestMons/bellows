**project:** bellows | **type:** diagnostic | **steps:** 1 | **pause_for_verdict:** always | **auto_close:** false

# Diagnostic — PATH-001 Rule 20 self-check staleness audit

## Why this exists

BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` was authored before the 2026-05-10 Rule 20 single-source migration (closed entry `executable-rule-20-single-source-2026-05-10`). The migration moved the canonical Python block to `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` and eliminated Planner-side block authoring.

Hypothesis: the entry is stale by side effect of the migration. The current canonical block uses absolute paths throughout (`evidence_dir`, `qa_report_path`, `os.path.join(evidence_dir, fname)`) and contains no `bellows/` prefix, so the originally-documented PATH-001 failure mode (CWD-relative paths assuming execution from the parent directory) cannot reproduce against the canonical block.

This diagnostic confirms or refutes the staleness hypothesis before any executable fix is authored. Same pattern as the 2026-05-10 closures of S3 Bug C, S3 verdict-resolved retry, and plan filename rename — verify whether an upstream fix already resolved the symptom before designing a follow-up.

## Step 1 — Systems Analyst: PATH-001 staleness audit

You are the Bellows Systems Analyst. Read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` before starting; if it does not exist, fall back to `bellows/agents/BELLOWS_SA.md` or the closest available SA spec.

### Context

A BACKLOG entry dated 2026-04-19 documents a recurrence of a pattern called PATH-001 in the Rule 20 self-check. The entry's exact text:

> 2026-04-19: PATH-001 recurrence in Rule 20 self-check — the CWD-relative path issue first documented in agent-prompt-feedback.md Patterns (PATH-001) has now recurred in executable-verdict-lifecycle-coupling-2026-04-19 QA. The self-check script prefixes paths with `bellows/` assuming execution from the parent directory, but agents often execute from inside the project directory. Pattern was identified but the PLANNER_TEMPLATE Rule 20 template was not updated to fix it. Candidate fix: change the Rule 20 block template to use either `os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` as the first line (if the block is known to be run from an evidence-file path) or explicit absolute paths. Deferred to next governance pass.

Since this entry was authored, the 2026-05-10 single-source migration (`executable-rule-20-single-source-2026-05-10`) moved the canonical Rule 20 block to `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. The Planner no longer authors the block in plans; the PLANNER_TEMPLATE Rule 20 section no longer inlines the block; the QA agent reads the canonical file directly.

### Task

Determine whether PATH-001 still reproduces against the current canonical Rule 20 self-check block, or whether it is structurally fixed by the 2026-05-10 migration.

Answer the following questions in order. For each question, cite specific file paths, line numbers, or commit SHAs as evidence.

1. **Locate the original PATH-001 pattern definition.** Search the bellows repo and the governance root for `agent-prompt-feedback.md`. If multiple copies exist, identify all of them. Read the PATH-001 entry in each (if present) and quote the original failure mode verbatim. If `agent-prompt-feedback.md` does not exist anywhere, search for `PATH-001` as a literal string across all `.md` files under `/Users/marklehn/Desktop/GitHub/` and report every occurrence with surrounding context.

2. **Audit the current canonical block.** Read `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` in full. Enumerate every path-related variable and expression in the Python block (`evidence_dir`, `qa_report_path`, every `os.path.*` call). For each, determine whether it is absolute or CWD-relative as written, and whether the placeholder comments instruct the QA agent to supply absolute or relative values. State whether any `bellows/` prefix appears anywhere in the canonical block.

3. **Audit the broken plan that triggered the original entry.** Read `bellows/knowledge/decisions/Done/executable-verdict-lifecycle-coupling-2026-04-19.md` and the corresponding QA report (likely in `bellows/knowledge/qa/`). Identify the exact Rule 20 block as it was inlined in that plan's QA step and locate the lines that exhibited PATH-001. Quote them verbatim. Compare to the current canonical block — does the current block contain the same broken pattern, a different pattern, or no equivalent code at all?

4. **Population audit on post-migration QA reports.** List every QA report in `bellows/knowledge/qa/` with filename matching `*-2026-05-*` (post-migration). For each, scan for either (a) Rule 20 self-check `FAILED` output, or (b) any indication that path resolution failed during the self-check. Report counts: total post-migration QA reports examined, count exhibiting any path-resolution failure, count exhibiting PATH-001-style CWD-relative failures specifically. If any exist, cite the report filename and quote the failing output.

5. **Cross-project canonical reference audit.** The 2026-05-10 close mentions `bellows/agents/BELLOWS_QA.md` and `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` were updated with reference paragraphs. Read both files. Confirm neither inlines a Rule 20 block. Confirm both point to the canonical file. Report any deviation.

6. **Verdict.** Based on questions 1–5, classify the BACKLOG entry as one of:
   - **STALE — close as hygiene.** PATH-001 cannot reproduce against the post-migration canonical block; the 2026-05-10 single-source migration structurally fixed the failure mode. No code or governance change required. Recommend closing the BACKLOG entry as a hygiene closure citing the migration commit.
   - **PARTIALLY STALE — narrowed scope.** PATH-001 cannot reproduce against the canonical block, but a related path-resolution risk exists in a different surface (specify which). Recommend a follow-up scoped to the actual residual surface.
   - **STILL ACTIVE — fix needed.** PATH-001 can still reproduce against the canonical block as currently written. Recommend a fix shape: either the `os.chdir(...)` first-line approach from the original BACKLOG entry, or absolute-paths-only enforcement (specifying placeholder comments more strictly), or a third option you propose. For each, estimate LOC impact on `RULE_20_SELF_CHECK_BLOCK.md` and any downstream files.

### Out of scope

- Do NOT propose Bellows code changes. The Rule 20 self-check banner enforcement in `bellows/gates.py` is not in scope.
- Do NOT modify any file. This is a read-only audit.
- Do NOT propose changes to the canonical block itself in this diagnostic. If the verdict is "STILL ACTIVE," recommend a fix SHAPE only; the executable will be a separate plan.

### Deliverables

A findings file at `bellows/knowledge/research/path-001-rule-20-staleness-audit-2026-05-11.md` containing:
- One section per question (1–6) with the question restated, evidence cited (file paths, line numbers, commit SHAs, quoted text), and a clear answer.
- A final "Recommendation" section restating the verdict from question 6 in one paragraph.
- An Output Receipt at the bottom per BELLOWS_SYSTEMS_ANALYST.md format.

**Deposits:**
- `bellows/knowledge/research/path-001-rule-20-staleness-audit-2026-05-11.md`
