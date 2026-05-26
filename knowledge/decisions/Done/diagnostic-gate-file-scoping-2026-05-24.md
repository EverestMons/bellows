# Bellows — Gate file-scoping: shared root cause for BACKLOG items #6 and #7
**Date:** 2026-05-24 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Two open BACKLOG entries describe gate parsers misreading **the wrong file or the wrong rows within a file**. Both surfaced on QA steps on 2026-05-22 against `executable-invoice-pulse-specialist-file-drift-refresh-2026-05-22` Step 2 QA — same reproduction artifact for both items. This temporal coincidence is suspicious and suggests possible shared root cause: a gate-file-scoping mechanism that treats all step-modified files as candidates for inspection rather than scoping to the QA report's declared deposit path.

**Item #6 (2026-05-22): `rule_22_verification` (c) gate false-positive on tables.** Observed twice — once on 2026-05-22 invoice-pulse drift refresh, once on 2026-05-24 pre-scan removal QA. Both times, the gate flagged rows as "missing status" despite the rows having explicit PASS or N/A status glyphs in trailing columns. The 2026-05-24 case flagged the **failure-classification table** (a 3-column table with Test name | Classification | Notes, no status column by design — its purpose is to explain failures, not mark pass/fail), suggesting the gate may be misidentifying which tables in a QA report are "verification tables" requiring status glyphs vs other table types. The 2026-05-22 case flagged 47 verification-table rows where the final column ALWAYS reads PASS but the gate's quoted-row snippet appears truncated before the status column. Likely two contributing factors: (a) **row truncation** at some character/length boundary preventing the gate from seeing the final cell, and/or (b) **table-type confusion** treating any table in a QA report as a verification table.

**Item #7 (2026-05-22): `rule_20_self_check` gate fires on the wrong file.** Observed 2026-05-22 on the same plan reproduction. The Rule 20 banner exists in the QA report deposit (`invoice-pulse/knowledge/qa/specialist-file-drift-refresh-qa-2026-05-22.md`) and is valid with all 6 ✅ rows and `RULE 20 SELF-CHECK: PASSED` as the terminating line. The gate apparently scanned `agent-prompt-feedback.md` (because the QA step also appended a prompt-feedback entry) and matched a Rule-20-shaped pattern inside the feedback entry text without finding a paired PASSED line. BACKLOG hypothesizes: (a) gate iterates all files-modified-this-step looking for Rule 20 banners and stops at the first hit, regardless of whether that file is the QA deposit; (b) gate scans for any text matching the Rule 20 banner regex anywhere in any deposit and the feedback file got pattern-matched on incidental text describing Rule 20.

**Why investigate together — common signature:**
- Both are about gates reading the WRONG content (wrong file in #7, wrong rows or wrong table type in #6).
- Both surfaced on the SAME 2026-05-22 QA reproduction.
- Both potentially involve gate file-resolution logic that doesn't respect the QA report's declared deposit path.
- **Critical prior art:** the 2026-05-10 Closed BACKLOG entry "deposit_exists / rule_20_self_check gate path-resolution gap" identified that `_gate_rule_20_self_check` was previously **missed by the 2026-05-06 worktree-aware fix** — surgical patches were applied without addressing the underlying scoping design. Today's reproductions may be a fourth (or fifth) occurrence of "the gate looks at the wrong file" with previous fixes addressing symptoms rather than root cause.

**What this diagnostic must determine:**
- Q1: For both gates, identify EXACTLY which file(s) are scanned and where the file-resolution logic lives in `gates.py`.
- Q2: For #6, identify whether the failure is row-truncation, table-type confusion, or both — and whether the gate distinguishes "verification tables" from other tables.
- Q3: For #7, identify whether the gate iterates step-modified files, parses deposit-block declarations, or uses some other scoping mechanism.
- Q4: Whether items #6 and #7 share a root cause (e.g., common helper that resolves "the QA report file" incorrectly) or are independent.
- Q5: If shared, propose unified fix; if independent, recommend sequencing.

## Reference prior art (read these to avoid re-deriving)

- `bellows/knowledge/research/gates-deposit-parser-current-state-2026-04-19.md` — foundational deposit parser state; documents how gates discover what files to scan.
- `bellows/knowledge/research/rule-20-gate-false-positive-root-cause-2026-05-11.md` — prior Rule 20 false-positive root-cause analysis (RC1 from the closed 2026-05-10 entry).
- `bellows/knowledge/research/rule-20-gate-addition-surface-findings-2026-05-05.md` — original Rule 20 design surface.
- `bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md` — the diagnostic that identified `_gate_rule_20_self_check` was missed by an earlier worktree-aware fix. Critical context.
- The 2026-05-22 reproduction artifact: the QA report at `bellows/verdicts/pending/archived/verdict-request-invoice-pulse-specialist-file-drift-refresh-2026-05-22-step-2.md` (or its processed equivalent in `verdicts/resolved/`).
- The 2026-05-24 reproduction artifact: `bellows/knowledge/qa/executable-remove-pre-scan-processed-rename-v2-2026-05-24.md` and its verdict request at `bellows/verdicts/pending/archived/verdict-request-remove-pre-scan-processed-rename-v2-2026-05-24-step-2.md`.

Build on these. Do NOT repeat their findings; do extend them where today's joint synthesis requires.

## Five questions to answer

**Q1 (joint file resolution):** Where in `gates.py` does each gate decide which file(s) to scan? Specifically for `_gate_rule_22_verification` and `_gate_rule_20_self_check` — cite the exact function and line that selects the target file(s). Do both gates use the same file-resolution helper? Or do they each implement their own scoping logic? Has the file-resolution logic been touched by prior fixes (2026-05-06 worktree-aware fix, 2026-05-10 missed-gate fix)?

**Q2 (item #6 mechanism):** When the rule_22 (c) gate fires on a QA report containing multiple tables (some verification tables, some non-verification — like a failure-classification table without a status column), how does the gate decide which tables to inspect? Cite the table-discovery logic. Is there a "table type" classification, or does the gate inspect every markdown table in the file? Additionally: when the gate quotes a row in its evidence output and the row appears truncated, where is the truncation happening — markdown parser, regex pattern, output-formatting?

**Q3 (item #7 mechanism):** Trace `_gate_rule_20_self_check`'s file-resolution end-to-end. Does it (a) parse the plan's declared deposit path from the verdict-request, (b) iterate step-modified files looking for Rule 20 banners, (c) scan all files in some directory, (d) use some other mechanism? Cite the exact code. When the 2026-05-22 reproduction occurred, what files were modified during the QA step, and which one did the gate end up scanning? Was the QA report's correctly-formed banner ever read by the gate, or did the gate stop at the first file with a Rule-20-shaped pattern?

**Q4 (joint root cause):** Are items #6 and #7 surface manifestations of one underlying issue (e.g., gate file-resolution that doesn't respect the QA report's declared deposit path), or two independent issues?
- **If shared:** name the shared helper, predicate, or design assumption. Trace how both items map to it.
- **If independent:** state explicitly with two distinct code regions named.

Cross-reference the 2026-05-10 Closed entry's note that "`_gate_rule_20_self_check` was missed by the 2026-05-06 worktree-aware fix." If file-resolution is the shared cause, is this the SAME design flaw that the 2026-05-10 fix surgically patched without addressing structurally?

**Q5 (fix sequencing and shape):** Based on Q4, recommend fix shapes (2-3 per item, or unified if shared). For each, give LOC estimate and identify whether it closes the boundary structurally vs surgically. Address: does any proposed fix interact with the existing worktree-aware path resolution shipped in 2026-05-06 / 2026-05-10? Are there tests today that would catch regression after the fix?

---

## STEP 1 — Joint gate file-scoping characterization

**Agent:** Bellows Systems Analyst
**Estimated tokens:** ~30k

### Read order

1. The six "reference prior art" files listed in the Context section. Read in full. Anchor on what they already characterized — do not re-derive.
2. `bellows/gates.py` — full read with attention to: `_gate_rule_22_verification` (especially the (c) check that mechanizes "every row has a status"), `_gate_rule_20_self_check`, any helpers for file resolution (`_extract_plan_required_deposits`, `_extract_step_deposits`, or similar), and any worktree-path normalization logic added in 2026-05-06 or 2026-05-10 fixes.
3. `bellows/bellows.py` — only the call sites where these two gates are invoked. Cite the call lines and the arguments passed (especially file path arguments).
4. The two reproduction artifacts:
   - 2026-05-22: `bellows/verdicts/pending/archived/verdict-request-invoice-pulse-specialist-file-drift-refresh-2026-05-22-step-2.md` (or processed equivalent if archived). Note which gate failures it shows, and what files were in the step's modified-files list (the verdict request includes a Files Changed section).
   - 2026-05-24: `bellows/verdicts/pending/archived/verdict-request-remove-pre-scan-processed-rename-v2-2026-05-24-step-2.md` (or processed equivalent). Note the rule_22 (c) failure rows and the corresponding QA report at `bellows/knowledge/qa/executable-remove-pre-scan-processed-rename-v2-2026-05-24.md`.
5. The 2026-05-22 invoice-pulse QA deposit (mentioned in BACKLOG #7) — its Rule 20 banner. Cross-reference with the reproduction artifact.

Do NOT read source files beyond what's listed above unless the call chain requires it.

### Investigation questions

For every claim, cite specific `gates.py` / `bellows.py` line + exact code snippet (no paraphrasing).

**Section A — Joint file resolution (Q1)**

1. Locate `_gate_rule_22_verification` in `gates.py`. Cite the function signature and the line(s) where it decides what file to read. What is the file-resolution mechanism — does it receive a path argument, parse the plan's deposit declaration, or use some other method?
2. Locate `_gate_rule_20_self_check` in `gates.py`. Same question.
3. Are the two gates' file-resolution mechanisms the same code path (shared helper) or independent implementations? If shared, cite the helper. If independent, identify the two distinct code regions.
4. From `bellows.py`, cite the call sites for both gates. What arguments are passed? Is file-resolution done at the call site (bellows.py passes the resolved path) or inside the gate (gates.py resolves)?
5. The 2026-05-10 closed BACKLOG entry noted "_gate_rule_20_self_check was missed by the 2026-05-06 worktree-aware fix" and a surgical patch added a worktree-path argument. Has the same surgical-patch pattern been applied to `_gate_rule_22_verification`? Or does it have a different file-resolution mechanism that isn't worktree-path-related?

**Section B — Item #6 mechanism (Q2)**

6. Trace `_gate_rule_22_verification`'s (c) check end-to-end. What is the table-discovery mechanism? Does it iterate all markdown tables in the file, or does it filter to "verification-shaped" tables somehow?
7. For each discovered table, what is the row-status check? What constitutes a valid status (glyphs, keywords, etc.)? Cite the predicate.
8. When the gate reports "row N missing status" with a quoted row snippet, where does the snippet come from? Is the entire row read and quoted, or is there a length-cap or other truncation? Examine the 2026-05-22 reproduction: the BACKLOG entry says quoted rows appeared truncated mid-row before reaching the status cell. If truncation is happening, cite the truncation point.
9. For the 2026-05-24 reproduction (rows 40-44 of the pre-scan removal QA report flagged as missing status): read that QA report and identify which table the flagged rows belong to. Is it the Deliverable Verification table (which has explicit status glyphs) or the Test Execution failure-classification table (which has Test name | Classification | Notes columns with NO status column by design)? If the latter, the gate is mistakenly treating a non-verification table as a verification table — cite where the gate makes this classification decision (or confirm absence of any classification — gate inspects all tables).
10. Identify the fix shape: does the gate need to (a) better identify "verification tables" by some signal (e.g., the column header contains "Status" or "✅"), (b) only inspect tables in a specific named section (e.g., under "## Deliverable Verification"), (c) accept N/A as a valid status, (d) something else?

**Section C — Item #7 mechanism (Q3)**

11. Trace `_gate_rule_20_self_check`'s file-resolution end-to-end. The 2026-05-10 fix added a worktree-path argument. Does the gate currently use that path correctly — and does it then further scope to a specific file within the worktree, or scan all files?
12. From the 2026-05-22 reproduction: what files were modified during the QA step (`agent-prompt-feedback.md` and the QA report at minimum, possibly others)? Which file did the gate end up scanning when it reported "banner present but PASSED line missing"?
13. Does the gate parse the plan's declared `**Deposits:**` block to identify which file is THE QA report? Or does it use a heuristic (e.g., "first file with a Rule 20 banner"), or does it scan all files?
14. The BACKLOG hypothesizes two root causes (iterate-all-files OR regex-anywhere-in-any-deposit). Determine which is correct, OR identify a third mechanism that explains the observed behavior. Cite the relevant code.

**Section D — Joint root cause analysis (Q4)**

15. From Sections A-C, do items #6 and #7 share a root cause?
   - **If shared:** name the shared helper, predicate, or design assumption. Trace how both items map to it. Specifically: is there a missing "scope to the declared QA report deposit path" check that should constrain BOTH gates?
   - **If independent:** state explicitly. Name the two distinct code regions.
16. Cross-reference the 2026-05-10 Closed entry's note that "_gate_rule_20_self_check was missed by the 2026-05-06 worktree-aware fix." If file-resolution is the shared cause, has the same pattern of surgical patches been applied without structural resolution? Is today's #7 a recurrence of a known pattern? Is today's #6 a NEW manifestation of the same design flaw?
17. Identify the structural fix vs surgical patches. What design assumption would close the file-scoping boundary permanently for both gates?

**Section E — Fix shapes (Q5)**

18. For each item (or unified if shared), list 2-3 concrete fix shapes. For each:
   - LOC estimate (production + tests)
   - Whether it closes the issue structurally or surgically
   - Whether it interacts with the 2026-05-06 / 2026-05-10 worktree-aware path fixes
   - Test names that would catch regression after the fix
19. If a shared root cause exists, propose a unified fix shape. Note which items it incidentally closes.
20. Identify test coverage gaps. For each item, are there existing pytest tests that would catch the failure mode if reintroduced? Name tests by file:function or confirm absence.

### Out of scope

- Do NOT propose or implement fixes; characterization only.
- Do NOT modify `gates.py`, `bellows.py`, or any test file.
- Do NOT touch verdict files or reproduction artifacts.
- Do NOT investigate other gate issues (#4 path-keyed rejection cache, #10 file_change_audit false-negative, #11 defensive header default) — those are different problem families, separate diagnostics later.

### Deliverables

**Deposits:**
- `bellows/knowledge/architecture/gate-file-scoping-2026-05-24.md`

The findings file MUST include:
- Section A — Joint file resolution (questions 1-5) with code citations
- Section B — Item #6 mechanism (questions 6-10) with table-discovery analysis
- Section C — Item #7 mechanism (questions 11-14) with file-iteration analysis
- Section D — Joint root cause analysis (questions 15-17)
- Section E — Fix shapes (questions 18-20)
- The standard SA Output Receipt block at the end

### STOP

Stop after Step 1. Do not author an executable. The Planner will read the findings, verify Rule 22, and decide on fix scope + sequencing.
