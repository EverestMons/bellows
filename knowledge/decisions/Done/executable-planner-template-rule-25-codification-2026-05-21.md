# PLANNER_TEMPLATE.md — codify Planner Rule 22 routing after verdict-enrichment shipped
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

The 2026-05-21 verdict-enrichment plan (in `bellows/knowledge/decisions/Done/executable-bellows-verdict-enrichment-2026-05-21.md`) added two Bellows gates that mechanize portions of Rule 22 verification:

- **`_gate_rule_22_verification`** mechanizes Rule 22 (a) file existence, (c) verification-table greenness, and (d) absence of hedging keywords in positive-status rows
- **`_gate_rule_20_self_check`** mechanizes Rule 22 (e) banner-byte-exact + PASSED line check

Together these two gates cover (a), (c), (d), and (e) — four of Rule 22's five sub-checks. Only **(b)** — does the deposited content actually answer the original question or fix the original bug — remains as Planner-only work because it requires substantive judgment that no gate can mechanize.

Current PLANNER_TEMPLATE Rule 22 + Rule 25 text describes the Planner doing all of (a)–(e) every time. This was correct before the verdict-enrichment shipped, but is now redundant: when a verdict request shows `rule_22_verification: PASS` and `rule_20_self_check: PASS`, the Planner re-running file-info, grep audits, and structural compliance walks duplicates Bellows's mechanical work without adding safety.

Observed first time this session (2026-05-21) on the v4.47 PLANNER_TEMPLATE plan, when the Planner re-ran file-info, grep audits, and structural compliance walks that Bellows had already passed. CEO question "why is the Planner still doing Rule 22 a-e?" surfaced the codification gap. Memory edit applied in-session to update behavior; this plan promotes the discipline change to governance text so future Planner instances pick it up structurally.

**Pre-write contradiction scan (per Rule 22 governance discipline):** Completed 2026-05-21. Keyword searches across PLANNER_TEMPLATE v4.47:

- `"mechanically"` — appears in Rule 25 routing table describing `rule_22_check_failed` gate behavior. New text reinforces this; no contradiction.
- `"(a)–(e)"` / `"(a)-(e)"` — appears in Rule 22 sub-check enumeration and Rule 25 routing paragraph. The new text amends the Rule 25 routing paragraph to specify which sub-checks Bellows mechanizes vs which remain Planner-only; it does NOT modify Rule 22's enumeration of (a)–(e) itself, which remains the canonical definition of the check set.
- `"rule_22_verification"` / `"rule_20_self_check"` — appear as gate names in Rule 25 routing table. New text references both correctly.
- `"redundant"` — does not currently appear in PLANNER_TEMPLATE; new use is unambiguous.

No contradictions found. The change is additive (clarify which checks are mechanized) and does not invalidate any prior rule.

**Anchors (Rule 23(a) verbatim):**

Anchor 1 — Rule 25 "Rule 22 routing on auto-proceed codes" paragraph (the load-bearing edit):

```
**Rule 22 routing on auto-proceed codes:** When the Pause Reason Code authorizes auto-proceed, the Planner takes the path in the verdict file's `Deposit:` field and applies Rule 22's (a)–(e) checks to that path. If the Deposit field is `none` (no deposit declared for that step), the Planner reports the verdict to the CEO for judgment — "none" is not a failure but it is not a Rule 22 pass either, and the CEO decides whether the step should have declared a deposit. If Rule 22 passes, the Planner reports the pass to the CEO ("Step N QA verification passed, safe to close Bellows verdict") and the CEO resolves the verdict via the normal Bellows workflow. If Rule 22 fails at any of (a)–(e), the Planner reports the failure in full per Rule 22's existing escalation language.
```

Replacement — same paragraph with a new follow-on paragraph appended (preserves the existing prose verbatim, adds the mechanization clarification as a new paragraph immediately after):

```
**Rule 22 routing on auto-proceed codes:** When the Pause Reason Code authorizes auto-proceed, the Planner takes the path in the verdict file's `Deposit:` field and applies Rule 22's (a)–(e) checks to that path. If the Deposit field is `none` (no deposit declared for that step), the Planner reports the verdict to the CEO for judgment — "none" is not a failure but it is not a Rule 22 pass either, and the CEO decides whether the step should have declared a deposit. If Rule 22 passes, the Planner reports the pass to the CEO ("Step N QA verification passed, safe to close Bellows verdict") and the CEO resolves the verdict via the normal Bellows workflow. If Rule 22 fails at any of (a)–(e), the Planner reports the failure in full per Rule 22's existing escalation language.

**Mechanized check routing (post-verdict-enrichment).** As of the 2026-05-21 verdict-enrichment plan, Bellows mechanizes Rule 22 (a), (c), (d), and (e) via two gates: `_gate_rule_22_verification` covers (a) file existence, (c) verification-table greenness, and (d) hedging-keyword absence; `_gate_rule_20_self_check` covers (e) Rule 20 banner-byte-exact and PASSED-line presence. When a verdict request shows BOTH `rule_22_verification: PASS` AND `rule_20_self_check: PASS` in its Verification Results table, the Planner performs Rule 22 (b) substance check ONLY — does the deposited content actually answer the original question or fix the original bug. The Planner does NOT re-run mechanical checks (a), (c), (d), or (e); Bellows has already verified them. Re-running them duplicates work without adding safety. If either gate reports FAIL or shows a Pause Reason Code that is not auto-proceed (e.g., `gate_failure`, `rule_22_check_failed`), the routing remains as described above — the Planner halts, reads the gate failure detail, and reports to the CEO. The mechanization does NOT remove (b) from the Planner's responsibility: (b) requires substantive judgment that no gate can perform (does this fix the bug? does this answer the question?). (b) remains Planner-only and is the entire scope of Planner verification on a clean-gates verdict request.
```

Anchor 2 — Version header lines (bump 4.47 → 4.48):

```
**Version:** 4.47
**Last Updated:** 2026-05-21 (v4.47)
```

Replacement:

```
**Version:** 4.48
**Last Updated:** 2026-05-21 (v4.48)
```

Anchor 3 — Last existing Lessons row (to anchor the new row append). I do not pre-quote the anchor here because plan-write-time the last row is the 2026-05-21 BACKLOG-entries-from-memory row added by the v4.47 plan; the DOC agent will read the Lessons table to capture the exact anchor.

New Lessons row to append (mandatory pipe-separated table-row format):

```
| 2026-05-21 | Once Bellows mechanizes a Rule 22 sub-check, the Planner must stop re-running it. The 2026-05-21 verdict-enrichment shipped `_gate_rule_22_verification` (covers Rule 22 (a)+(c)+(d)) and `_gate_rule_20_self_check` (covers Rule 22 (e)). For the rest of the same session, the Planner kept re-running file-info, grep audits, and structural compliance walks on every verdict — duplicating mechanical work the gates had already passed. The CEO surfaced this with "why is planner still doing rule 22 a-e?" The fix is structural: governance text (this edit) now says explicitly that when both gates PASS, the Planner does (b) only. **Pattern:** when shipping mechanization of a Planner-side discipline, the same plan or the immediate next plan must update PLANNER_TEMPLATE to reflect what the Planner stops doing. Memory edits alone do not propagate across sessions; the governance text is what future Planner instances read at session start. |
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> You are the Bellows Documentation Analyst. Read your specialist file at `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` first. **Skip glossary read — this is a governance-file edit task.** **Pre-edit verification:** Before performing any edit, run `grep -n "Rule 22 routing on auto-proceed codes" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` and confirm exactly ONE match (the anchor for Edit A). Then run `grep -n "\*\*Version:\*\* 4.47" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` and confirm exactly ONE match (Edit B). Then read the Lessons Learned table at the bottom of `PLANNER_TEMPLATE.md` and identify the verbatim text of the LAST row (most recent date entry) — this will be the anchor for Edit C. Quote the entire last row (including the closing `|` and any trailing whitespace) in the dev log. If any pre-edit check returns unexpected output, STOP — deposit a verification-mismatch report at `bellows/knowledge/flags/verification-mismatch-rule-25-codification-2026-05-21-step-1.md` and halt. **Task:** Apply three edits to `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` using `Desktop Commander:edit_block`. **Edit A — Rule 25 mechanized check routing paragraph:** locate the existing "**Rule 22 routing on auto-proceed codes:**" paragraph (verbatim text quoted in the plan Context section above as Anchor 1). Replace it with the same paragraph followed by a blank line followed by a new paragraph beginning "**Mechanized check routing (post-verdict-enrichment).**" — the full replacement text is in the plan Context section above. The original paragraph must remain verbatim; the new paragraph is additive. **Edit B — Version header bump:** Replace the two-line block `**Version:** 4.47\n**Last Updated:** 2026-05-21 (v4.47)` with `**Version:** 4.48\n**Last Updated:** 2026-05-21 (v4.48)`. **Edit C — Lessons row append:** Use `Desktop Commander:edit_block` with a verbatim anchor capturing the last existing Lessons row (identified during pre-edit verification). Append the new row immediately after, before the closing `---` separator that follows the Lessons table. The new row content is in the plan Context section above. The format must match existing rows exactly (pipe-separated, leading `|`, trailing `|`, no internal newlines in the lesson cell). **Verification after each edit:** read the edited section back via `Desktop Commander:read_file` with appropriate line range and confirm the edit landed cleanly. If any `edit_block` returns a near-miss diff, halt and report to CEO — do not retry blindly. **Deposit a dev log:** write to `bellows/knowledge/development/planner-template-v4-48-rule-25-codification-2026-05-21.md` documenting each of the three edits (A, B, C) with before/after snippets (3-5 lines surrounding context plus the changed lines), the verbatim anchor used for each, and any deviations from the plan's exact text. Include the verbatim text of the Lessons-row anchor captured during pre-edit verification. **Commit:** stage `PLANNER_TEMPLATE.md` and the dev log. Per the governance commit-repo rule, `PLANNER_TEMPLATE.md` commits to `/Users/marklehn/Developer/GitHub/` (governance root), the dev log commits to `bellows/`. Two-commit split: governance-root commit message `docs: PLANNER_TEMPLATE v4.48 — codify Rule 22 routing after verdict-enrichment`; bellows commit message `docs: dev log for PLANNER_TEMPLATE v4.48`. **DO NOT push to origin** — the Planner handles session-wrap commits. **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Third commit (bellows repo): `docs: prompt feedback — bellows DOC PLANNER_TEMPLATE v4.48`. **DO NOT push.**
>
> **Deposits:**
> - `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (modified)
> - `bellows/knowledge/development/planner-template-v4-48-rule-25-codification-2026-05-21.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read — this is a governance-file QA task.** **Before starting, read `bellows/knowledge/development/planner-template-v4-48-rule-25-codification-2026-05-21.md` (DOC's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Read DOC's Output Receipt "Files Created or Modified" list. Verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Specifically: (1) `PLANNER_TEMPLATE.md` version header reads `**Version:** 4.48` and `**Last Updated:** 2026-05-21 (v4.48)` — `grep -n "Version:" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md | head -2` shows the new version; (2) the existing "Rule 22 routing on auto-proceed codes:" paragraph is present and unchanged — grep for the literal phrase "Step N QA verification passed, safe to close Bellows verdict" returns 1 match; (3) the new "Mechanized check routing (post-verdict-enrichment)" paragraph is present — grep for the literal phrase "post-verdict-enrichment" returns 1 match; (4) the new paragraph correctly cross-references both gates — grep for "`_gate_rule_22_verification`" returns at least 1 match in Rule 25 context (the gate is also referenced in the existing routing table, so total count may be 2); (5) the new paragraph correctly identifies (b) as the Planner-only check — grep for the literal phrase "(b) substance check ONLY" returns 1 match; (6) Lessons table has the new 2026-05-21 row about Bellows-mechanization-and-Planner-stop-doing — grep for the distinctive phrase "Once Bellows mechanizes a Rule 22 sub-check" returns 1 match; (7) the dev log file exists and contains before/after snippets for all three edits — grep for the section headers; (8) `agent-prompt-feedback.md` has a new dated entry from this plan — grep for the date `2026-05-21` plus the plan slug. Capture each grep output to evidence: `bellows/knowledge/qa/evidence/executable-planner-template-rule-25-codification-2026-05-21/version_header.txt`, `existing_paragraph_preserved.txt`, `new_paragraph_present.txt`, `gate_crossref.txt`, `b_only_phrase.txt`, `lessons_row.txt`, `dev_log_sections.txt`, `feedback_entry.txt`. Any ❌ blocks plan close — report to CEO. **Structural-compliance checks.** (a) Verify the existing Rule 22 (a)-(e) sub-check enumeration paragraph is UNCHANGED — grep for the literal phrase "What the Planner specifically checks when reading a deposited file" returns 1 match, and the (a)/(b)/(c)/(d)/(e) bullet list immediately follows it unchanged. The new mechanization paragraph clarifies routing but must not modify the canonical (a)-(e) definitions. Capture to `evidence/.../rule_22_definitions_preserved.txt`. (b) Verify version bump is consistent: only `**Version:** 4.47` → `4.48` and `**Last Updated:**` date suffix updated; no other version references in the file were edited. Grep for `4.47` and confirm zero remaining occurrences. Capture to `evidence/.../version_consistency.txt`. (c) Verify the Lessons table structural integrity: the new row sits immediately before the closing `---` separator after the table; the table is still valid Markdown pipe-separated format; no other Lessons rows were modified. Capture last 5 rows of the Lessons table to `evidence/.../lessons_table_tail.txt`. **Code-level QA (no test suite).** This is a governance markdown edit; no test suite applies. Test scope is `targeted` per the plan header — no `pytest_targeted.txt` evidence file required (the targeted set is the empty set for markdown-only edits per the 2026-04-20 Lessons row codifying Position A). **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-planner-template-rule-25-codification-2026-05-21`; `qa_report_path` = `bellows/knowledge/qa/executable-planner-template-rule-25-codification-2026-05-21.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/executable-planner-template-rule-25-codification-2026-05-21/`; `required_evidence_files` = `["version_header.txt", "existing_paragraph_preserved.txt", "new_paragraph_present.txt", "gate_crossref.txt", "b_only_phrase.txt", "lessons_row.txt", "dev_log_sections.txt", "feedback_entry.txt", "rule_22_definitions_preserved.txt", "version_consistency.txt", "lessons_table_tail.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-21 entry under Completed for "PLANNER_TEMPLATE v4.48 shipped — Rule 25 codification of Planner Rule 22 routing post-verdict-enrichment" with a one-paragraph summary. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): PLANNER_TEMPLATE v4.48 Rule 25 codification`. **DO NOT push to origin** — Planner handles session-wrap commits. **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA PLANNER_TEMPLATE v4.48`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-planner-template-rule-25-codification-2026-05-21.md`
> - `bellows/knowledge/qa/evidence/executable-planner-template-rule-25-codification-2026-05-21/` (11 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
