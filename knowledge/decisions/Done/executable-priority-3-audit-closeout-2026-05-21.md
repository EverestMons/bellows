# Bellows — Priority 3 Audit Closeout
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA) | **pause_for_verdict:** after_qa_step
**Priority:** 3
**Depends on:** diagnostic-priority-3-carryover-audit-v2-2026-05-21 (Step 1 SA findings)

## Context

The SA's five-item Priority 3 carry-over audit returned: 1× UNRESOLVABLE (close), 1× STALE (close), 3× LIVE-MINOR (BACKLOG additions). Zero LIVE-LOAD-BEARING. SA findings cited concrete file:line evidence for each disposition.

This executable lands the audit decisions:
- Three BACKLOG.md entries (items 2/4/5) with SA-supplied reproduction notes
- NEXT_SESSION.md Priority 3 section retired (replaced with one-line audit-closure note)

No source code changes. Markdown-only.

The SA findings live at `bellows/logs/20260521-093802-step.json` (`parsed.result_text` field) — they were a conversation-report diagnostic with zero deposits. The disposition text below is sourced from that step log.

---
---

## STEP 1 — Bellows Documentation Analyst

---

Specialist: read `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md`. Working directory: `/Users/marklehn/Developer/GitHub/bellows/`.

Make two edits, both surgical:

**Edit 1 — Append three entries to `bellows/knowledge/BACKLOG.md` Open section.** Insert these entries at the top of the Open section (above the existing 2026-05-27 `test_decisions.py` entry), in this exact order:

```markdown
- **Added 2026-05-21:** `pause_for_verdict` unvalidated enum (Priority 3 audit). `header_says_pause` at `bellows.py:305-314` recognizes three string values (`always`, `after_step_1`, `after_qa_step`); any other value (typos, `never`, empty after defensive default) silently returns False with no warning. `_apply_defensive_header_defaults` at `bellows.py:317-326` mitigates the missing-key case for multi-step plans, but unrecognized values fall through. **Disposition recommendation:** small — add a WARN log for unrecognized values in `header_says_pause`. Optional follow-up: PLANNER_TEMPLATE alignment check (template field documentation vs. parser-accepted enum). Reference: `Done/diagnostic-priority-3-carryover-audit-v2-2026-05-21.md`, SA findings at `logs/20260521-093802-step.json`.

- **Added 2026-05-21:** Deposits parser does not strip parenthetical qualifiers (Priority 3 audit). `_extract_plan_required_deposits` at `gates.py:380` and `_gate_deposit_exists` agent-declared path parser at `gates.py:323` both use backtick-only regex (`r'`([^`]+)`'`) — parenthetical text outside backticks is harmlessly ignored, but parenthetical text inside backticks (e.g., `` `knowledge/foo.md (volunteered)` ``) is captured into the path string and causes a clear `deposit_exists` gate trip (recoverable via Rule 22 override). Rule 26 governance prevents the Planner from authoring the problematic pattern; no documented incident exists. **Disposition recommendation:** small — add `re.sub(r'\s*\([^)]*\)\s*$', '', path)` strip at both call sites if a Planner-authored parenthetical incident ever occurs. Defer until then. Reference: `Done/diagnostic-priority-3-carryover-audit-v2-2026-05-21.md`, SA findings at `logs/20260521-093802-step.json`.

- **Added 2026-05-21:** No-match verdict warning rate-limit (Priority 3 audit). `_consume_verdicts` at `bellows.py:1280` emits `⚠️ no verdict-pending plan found step {N} — leaving in resolved/ for retry` every 30 seconds (rescan_interval) per unresolved verdict file in `resolved/`. Without dedup, a single stuck file produces ~2,880 warning lines per day. Adjacent stale-verdict warning at `bellows.py:1278` is self-limiting (file moved to processed on first detection). The S3 Bug A fix (commit `dc0bdd7`, exclusion filter for `verdict-request-*` files) eliminated the primary source of stuck files, making accumulation rare. **Disposition recommendation:** small — add `_warned_no_match: set` dedup guard (log once per file, clear on match or startup). Low priority; no documented flooding incident. Reference: `Done/diagnostic-priority-3-carryover-audit-v2-2026-05-21.md`, SA findings at `logs/20260521-093802-step.json`.
```

**Edit 2 — Replace the `## Priority 3 — Stale carry-overs` section in `bellows/NEXT_SESSION.md`** with the following one-line closure note. Replace the entire section (heading line, both bullet items, and any trailing blank lines that belong to the section).

Old text to replace (preserve any surrounding section separators):

```markdown
## Priority 3 — Stale carry-overs

- **2026-05-19 baton priority 1 (stale-redirect grep audit)** still not done. Defer or knock out.
- **2026-05-19 baton priority-2 items** (4 minor Bellows gaps: pause_for_verdict single-enum, verdict prose directive unactionable, Deposits parenthetical qualifiers, stale verdict step warning rate-limit) — none blocking. Promote to BACKLOG or decline.
```

New text:

```markdown
## Priority 3 — Closed

Five-item carry-over audit completed 2026-05-21. Disposition: 1× UNRESOLVABLE (stale-redirect — no referent), 1× STALE (verdict prose directives — superseded by 2026-05-21 verdict-enrichment), 3× LIVE-MINOR added to BACKLOG (pause_for_verdict enum validation, Deposits parenthetical stripping, no-match verdict warning dedup). Reference: `Done/diagnostic-priority-3-carryover-audit-v2-2026-05-21.md`, `Done/executable-priority-3-audit-closeout-2026-05-21.md`.
```

Commit both edits in one commit with message: `docs: close Priority 3 carry-over audit (BACKLOG +3, NEXT_SESSION retired)`. Use `git --no-pager` throughout. Do NOT push — the Planner handles push at session-wrap.

**Output Receipt** — Agent: Bellows Documentation Analyst, Step: 1, **Status: Complete** if both edits landed and committed; **Blocked** if either grep target was missing or the commit failed. What Was Done: appended three BACKLOG.md entries to Open section, replaced NEXT_SESSION.md Priority 3 section with closure note, single commit. Files Created or Modified: `bellows/knowledge/BACKLOG.md`, `bellows/NEXT_SESSION.md`. Files Deposited: none (in-place edits, no knowledge deposit). Decisions Made: none — disposition text sourced verbatim from SA findings. Flags for CEO: none expected. Flags for Next Step: QA agent verifies both edits landed and references resolve.

**Deposits:**
- `bellows/knowledge/BACKLOG.md`
- `bellows/NEXT_SESSION.md`

**STOP.** Do NOT proceed to Step 2. Wait for CEO confirmation.

---
---

## STEP 2 — Bellows QA

---

Specialist: read `bellows/agents/BELLOWS_QA.md`. Working directory: `/Users/marklehn/Developer/GitHub/bellows/`.

Before starting, read Step 1's Output Receipt status. If status is not Complete, stop and report.

This is a markdown-only verification step. No test suite. Per Rule 8 / Position A, QA's role here is deliverable verification + commit verification + Rule 20 self-check.

**Verification table** — produce a markdown table with one row per deliverable. Use status tokens that pass the Rule 20 hedging-keyword scan (✅ or PASS).

| Deliverable | Status | Evidence |
|---|---|---|
| BACKLOG.md: pause_for_verdict entry present | ✅ | grep -n "Added 2026-05-21:.*pause_for_verdict" bellows/knowledge/BACKLOG.md → line N |
| BACKLOG.md: Deposits parenthetical entry present | ✅ | grep -n "Added 2026-05-21:.*Deposits parser" bellows/knowledge/BACKLOG.md → line N |
| BACKLOG.md: No-match verdict warning entry present | ✅ | grep -n "Added 2026-05-21:.*No-match verdict warning" bellows/knowledge/BACKLOG.md → line N |
| BACKLOG.md: entries appended to Open section (not Closed) | ✅ | inspect: all three entries sit above the existing `## Closed` header |
| NEXT_SESSION.md: Priority 3 section replaced with closure note | ✅ | grep -n "Priority 3 — Closed" bellows/NEXT_SESSION.md → line N |
| NEXT_SESSION.md: old bullets removed | ✅ | grep -c "2026-05-19 baton priority" bellows/NEXT_SESSION.md → 0 |
| Single commit with both files | ✅ | git --no-pager log -1 --name-only → both files listed |
| Commit message matches spec | ✅ | git --no-pager log -1 --pretty=%s → "docs: close Priority 3 carry-over audit (BACKLOG +3, NEXT_SESSION retired)" |

Replace `N` placeholders with actual line numbers from the grep output. Replace each ✅ with the actual verification result — only mark ✅ when the evidence command produced the expected output.

**Rule 20 self-check.** Execute the canonical Python block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Run it against this plan's QA report. Append the literal banner output to the QA report.

**Deposit the QA report at:** `bellows/knowledge/qa/priority-3-audit-closeout-2026-05-21.md`. The report must contain (a) the verification table above with real evidence, (b) the Rule 20 self-check banner with PASSED line, (c) the Output Receipt below.

After QA report deposit and Rule 20 self-check pass, update `bellows/PROJECT_STATUS.md` with a session entry summarizing the Priority 3 audit closeout (one paragraph, 3-5 sentences). Then commit the QA report + PROJECT_STATUS update in one commit: `docs: QA — Priority 3 audit closeout`. Do NOT push.

**Output Receipt** — Agent: Bellows QA, Step: 2, **Status: Complete** if all 8 verification rows are ✅, Rule 20 self-check PASSED, QA report and PROJECT_STATUS entry committed; **Blocked** otherwise. What Was Done: deliverable verification table (8 rows), Rule 20 self-check, QA report deposit, PROJECT_STATUS update, commit. Files Created or Modified: `bellows/knowledge/qa/priority-3-audit-closeout-2026-05-21.md`, `bellows/PROJECT_STATUS.md`. Files Deposited: QA report at the path above. Decisions Made: none — pure verification. Flags for CEO: any ❌ row or Rule 20 FAILED indicates the executable needs Planner attention before housekeeping. Flags for Next Step: Planner Rule 22 verification on the QA report, then Done/ move.

**Deposits:**
- `bellows/knowledge/qa/priority-3-audit-closeout-2026-05-21.md`
- `bellows/PROJECT_STATUS.md`

**STOP.** Do NOT move the plan to Done. Wait for Planner Rule 22 verification.
