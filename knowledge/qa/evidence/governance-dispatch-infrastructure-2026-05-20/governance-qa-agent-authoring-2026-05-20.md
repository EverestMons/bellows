# Output Receipt: Governance QA_AGENT Authoring

**Plan:** governance-dispatch-infrastructure-2026-05-20
**Step:** 4 (DOC)
**Date:** 2026-05-20

---

## Output Receipt
**Agent:** Bellows Documentation Agent (cross-project authoring for governance)
**Step:** 4
**Status:** Complete

### What Was Done
Authored `governance/agents/QA_AGENT.md` by copying the structure of `bellows/agents/BELLOWS_QA.md` and modifying all sections for governance scope. All 11 template sections filled with governance-specific content. The extra "Rule 20 Self-Check (Canonical Block Reference)" section was preserved structurally intact from the Bellows source — it applies identically to governance QA.

### File Exists Confirmation
**Absolute path:** `/Users/marklehn/Developer/GitHub/governance/agents/QA_AGENT.md`
**Verified:** file created and committed.

### Section-by-Section Comparison: Bellows QA → Governance QA

| # | Section | Modification Type | What Changed |
|---|---|---|---|
| 1 | Header | Modified | Role → "QA Agent", Project → "governance", Version 1.0, Last Updated 2026-05-20, removed Handbook Reference line |
| 2 | Role Summary | Rewritten | Bellows gate/verdict/deposit testing → governance prose verification, registry consistency, byte-invariant compliance, contradiction checks |
| 3 | Domain Focus | Rewritten | Python module test coverage → governance-prose correctness, specialist file structural compliance, registry set-equality, LESSONS.md tag consistency |
| 3 | Key Sources | Rewritten | bellows/tests/, gates.py, verdict.py, parser.py, bellows.py → PLANNER_TEMPLATE Rules 20/22/25/26, RULE_20_SELF_CHECK_BLOCK.md, gates.py (retained as mechanical layer), SPECIALIST_TEMPLATE.md, COMPANY.md |
| 3 | Project-Specific Context | Rewritten | Layer 1 infrastructure with pytest → governance-as-project standup, prose verification vs code testing, shop-wide blast radius |
| 4 | Core Responsibilities | Rewritten (all 5) | (1) gate/verdict test coverage → prose consistency verification; (2) Rule 17 deliverable verification → three-list registry reconciliation; (3) Rule 20 self-check → preserved (applies to both); (4) Rule 21 test scope → specialist file structural compliance; (5) QA evidence files → LESSONS.md tag consistency audit. Reduced from 6 to 5 bullets (removed "design test cases for false-positive patterns" — bellows-specific) |
| 5 | Operating Procedure | Adapted | Retained deposit path checking and Rule 20 execution instructions verbatim. Added mechanical registry reconciliation requirement (load JSON, parse markdown, compare sets). Removed `_resolve_deposit_path` three-strategy reference (bellows-specific) |
| 6 | Output Format | Adapted | Verification table columns changed from section-focused to check-focused format. Removed test coverage summary requirement (bellows-specific). Added specialist file compliance enumeration and registry set-comparison requirements |
| 7 | Decision Authority | Adapted | (1) adding test cases → deliverable/deposit matching; (2) test scope accuracy → registry inconsistency flagging; (3) insufficient coverage flagging → specialist structural non-compliance flagging; (4-6) escalation rows preserved structurally, reworded for governance scope |
| 8 | Peer Consultation | Adapted | Bellows Developer/SA/DOC → Governance DOC/SA with governance-scope consultation triggers |
| 9 | Quality Standards | Adapted | Retained specificity requirement and Rule 20 literal-stdout requirement. Removed false-positive history references (BACKLOG #6 — bellows-specific). Added specialist file 11-section verification and set-based registry reconciliation requirements |
| 10 | Guardrails | Adapted | Retained mechanical-verification-only framing. Reworded from gate/deposit/state verification to structure/existence/consistency/compliance. Added shop-wide blast radius and contradiction-freedom verification requirements |
| — | Rule 20 Self-Check | Structurally intact | Preserved verbatim from Bellows QA — the 7-step procedure and canonical block reference apply identically. Updated path reference to "governance-root" rather than absolute Desktop path |
| 11 | Knowledge Base Index | Structurally intact | Table present, starts empty ("none yet") |

### Bellows-Specific Content Removed

- `_resolve_deposit_path` three-strategy reference (Operating Procedure) — bellows-specific deposit resolution mechanism
- "Design test cases that cover known false-positive patterns documented in the BACKLOG" (Core Responsibilities bullet 6) — refers to bellows BACKLOG #6 false-positive deposit extraction patterns
- Test coverage summary requirement for gate/verdict changes (Output Format) — bellows-specific pytest scope
- BACKLOG #6 false-positive history test assertions (Quality Standards) — bellows-specific test design guidance
- `Handbook Reference: COMPANY.md v2.4` header line — not present in SPECIALIST_TEMPLATE.md canonical structure

### Files Deposited
- `bellows/knowledge/research/governance-qa-agent-authoring-2026-05-20.md` — this file

### Files Created or Modified (Code)
- `governance/agents/QA_AGENT.md` — new specialist file, 192 lines, all 11 template sections filled + Rule 20 canonical block reference section

### Commit
**SHA:** c6113c7
**Message:** `feat(governance): author QA_AGENT specialist file`
**Repository:** `/Users/marklehn/Developer/GitHub/governance/` (governance repo, main branch)

### Decisions Made
- Preserved the "Rule 20 Self-Check (Canonical Block Reference)" extra section from Bellows QA — it applies identically to governance QA and is a critical operational procedure
- Removed 5 bellows-specific items cleanly (no "Not applicable" markers) to avoid structural clutter
- Reduced Core Responsibilities from 6 to 5 bullets after removing the bellows-specific false-positive test design bullet
- Updated the Rule 20 canonical block path reference to "governance-root" rather than the absolute Desktop path used in the Bellows QA file

### Flags for CEO
- None

### Flags for Next Step
- `governance/agents/QA_AGENT.md` exists and is committed. All three specialist files (DOC, SA, QA) are now in place. Step 5 (COMPANY.md three-list reconciliation) and Step 6 (QA close) can proceed.
