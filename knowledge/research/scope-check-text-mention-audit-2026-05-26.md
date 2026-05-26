# Scope_Check Text-Mention Predicate — Plan-Authoring vs Structural Gap Audit

**Date:** 2026-05-26 | **Agent:** Bellows Systems Analyst
**Plan:** diagnostic-scope-check-text-mention-audit-2026-05-26
**Step:** 1 (SA)

---

## Q1 — Empirical Predicate Trace

### Source of truth

The halted plan body at `knowledge/decisions/Done/halted-executable-planner-template-rule-21-contract-change-2026-05-26.md` is the source of truth for what `_extract_step_text` parsed at gate time. Bellows only renames plan files; the shadow cache was deleted at halt time (`_delete_shadow` at bellows.py:1282).

### Step text extraction

`_extract_step_text(plan_text, 1)` returns 7,070 characters, matching from `## STEP 1 — BELLOWS DOCUMENTATION ANALYST` (plan line 25) up to `## STEP 2` (plan line 98). `strip_fenced_code_blocks` has no effect because all fenced code blocks in the step are inside blockquote lines (prefixed with `> `), and the strip regex `^```[^\n]*\n.*?^```[^\n]*$` requires backticks at line-start.

### Three-tier predicate results

Candidate file path: `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md`
Candidate basename: `planner-template-rule-21-contract-change-2026-05-26.md`

| Tier | Check | Result | Evidence |
|---|---|---|---|
| (a) `basename in SCOPE_ALLOWLIST` | `planner-template-rule-21-contract-change-2026-05-26.md` not in `["agent-prompt-feedback.md", "PROJECT_STATUS.md", ".gitkeep"]` | **FAIL** | — |
| (b) `basename.startswith(prefix)` for `SCOPE_ALLOWLIST_PREFIXES` | Does not start with `in-progress-`, `verdict-pending-`, or `halted-` | **FAIL** | — |
| (c) `fpath in step_text or basename in step_text` | Both conditions **TRUE** | **PASS** | See match table below |

### Match table for tier (c)

| Match type | Byte offset | Context (±30 chars) |
|---|---|---|
| `fpath` match #1 | 6184 | `...three changes)\n> - \`bellows/knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md\` (dev log per Rule 8...` |
| `fpath` match #2 | 6675 | `...commit the dev log: \`git add knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md && git commit...` |
| `basename` match #1 | 208 | `...decisions/executable-planner-template-rule-21-contract-change-2026-05-26.md", "/Users/marklehn/Developer...` |
| `basename` match #2 | 350 | `...decisions/in-progress-executable-planner-template-rule-21-contract-change-2026-05-26.md")\`.` |
| `basename` match #3 | 6206 | `...bellows/knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md\` (dev log per Rule 8...` |
| `basename` match #4 | 6697 | `...git add knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md && git commit...` |

**Total:** 2 fpath matches, 4 basename matches.

### Near-miss analysis

Not needed — the predicate PASSES with exact matches. The basename minus extension (`planner-template-rule-21-contract-change-2026-05-26`) also appears as a substring of all 6 matches. No path-form mismatch, encoding, or escaping issues.

### Key finding

**The text-mention predicate PASSES for the dev log deposit.** The Planner included the deposit path in the step text — both in the `**Deposits:**` block (line 84 of the plan, byte offset 6184 in step text) and in the git commit instructions (line 89 of the plan, byte offset 6675 in step text).

---

## Q2 — Predicate Failure Classification

### Classification: **(iv) Other — unidentified file in `files_changed`**

The assumed failure mode (dev log not mentioned in step text) is **empirically disproven**. The text-mention predicate passes for the only deposit file (`knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md`).

However, scope_check DID trip. The evidence chain:

1. **Terminal log (2026-05-25 23:26:13):** `gates step 1: passed=False, failures=1` — confirmed at `logs/terminal/bellows-2026-05-25.log`
2. **Pushover notification:** `notify_verdict_request` at notifier.py:214 formats `failure_text = ", ".join(f["gate"] for f in gate_failures)`. The CEO's verdict references "scope_check" by name, consistent with this notification.
3. **Verdict ledger:** `pause_reason_code: "gate_failure"` — read from the verdict request file's `**Pause Reason Code:**` field at consumption time.
4. **CEO verdict file** (`verdicts/resolved/processed-verdict-planner-template-rule-21-contract-change-2026-05-26-step-1.md`): `"Step 1 gate_failure on scope_check flagged the plan file's own claim rename as out-of-scope."`

So scope_check was the failing gate. But the dev log file passes the predicate. **The file that tripped scope_check was a different file in `files_changed`** — one not identified by any available evidence.

### Evidence gap: original gate failure destroyed

The original `gate_result` (containing `failures` with the actual out-of-scope file list, and `files_changed` with the full diff) was:
- Written into the verdict request file at `verdict.py:200-204` (the `## Gate Failures` section) and `verdict.py:241-242` (the `## Files Changed` section)
- **Destroyed** when `_consume_verdicts` at bellows.py:1292-1293 deleted the pending verdict request file after processing

The verdict ledger at bellows.py:1226 creates a **fresh empty** `gate_result = {"failures": [], "files_changed": []}` instead of preserving the original. This is why the ledger entry shows `gate_failures: []` and `files_changed: []` — **these are not evidence that gates passed; they are data-loss artifacts.**

### Agent file operations traced from raw step output

| File | Tool | Committed? | Scope_check result |
|---|---|---|---|
| `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` | Edit (x8) | Yes (governance root, different repo) | N/A — not in bellows worktree |
| `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md` | Write (x1) | Yes (bellows worktree) | PASS (text-mention) |
| `knowledge/research/agent-prompt-feedback.md` | Edit (x4) | **Not committed** (uncommitted change) | PASS (SCOPE_ALLOWLIST) |

All identified agent file operations produce files that pass scope_check. The tripping file is **outside this known set** — possibly an OS artifact (`.DS_Store`), an editor swap file, or a transient file created by a tool operation that was captured by the diff window.

---

## Q3 — Fix-Shape Decision Matrix

The original four fix shapes (A–D) from the prior diagnostic were predicated on the assumption that the text-mention predicate FAILED for the dev log. That assumption is disproven. The fix-shape analysis must be reframed.

### Original shapes — applicability assessment

| Shape | Description | Applicable? | Rationale |
|---|---|---|---|
| A | Exempt `knowledge/` subtree | **No** | The dev log passed. Exempting knowledge/ wouldn't have prevented this trip — the tripping file is unidentified. |
| B | Parse Deposits block structurally | **No** | The deposit path IS mentioned in step text. Structural parsing adds no benefit when the substring match already passes. |
| C | Slug-substring exempt | **No** | Same — the deposit basename is already matched by substring. |
| D | Governance rule (Planner mentions path) | **No** | The Planner already DID mention the path. Governance compliance is confirmed. |

### New fix shapes identified by this diagnostic

| Shape | Description | Blast | Robustness | Coupling | Score |
|---|---|---|---|---|---|
| **E** — Preserve `gate_result` in verdict ledger | At bellows.py:1226, pass the original `gate_result` from the verdict request file through to `log_to_ledger` instead of creating a fresh empty one | None | **High** — closes the evidence-loss gap for ALL gate types | Low — reads existing verdict request file already in memory | **Recommended** |
| **F** — Log `files_changed` and failure evidence to terminal | At bellows.py:495, log the actual failure details and `files_changed` list, not just the count | None | Medium — provides real-time evidence but doesn't persist across daemon restarts | None | Complementary |
| **G** — Add `.DS_Store` / OS artifacts to `SCOPE_ALLOWLIST` | Add common OS-generated files to the allowlist | Low | Low — only addresses one specific file type | None | Speculative (root cause unconfirmed) |

### Recommendation

**Fix Shape E** (preserve gate_result in ledger). This diagnostic is inconclusive because the original gate failure evidence was destroyed. Fix Shape E closes that structural gap, making all future gate-failure investigations conclusive. It is the only fix that addresses the actual blocking issue — not the scope_check predicate (which works correctly), but the inability to determine what scope_check flagged.

**Fix Shape F** is complementary and should be implemented alongside E — real-time evidence in the terminal log is valuable for immediate triage even before the ledger is consulted.

---

## Q4 — Systemic-Risk Scope

### Deposit directories and agent roles

| Directory | Agent role(s) | Plan tier / step type | Example |
|---|---|---|---|
| `knowledge/development/` | Documentation Analyst | DOC steps (Rule 8 split-commit) | Dev logs for governance edits |
| `knowledge/research/` | Systems Analyst, QA | SA diagnostic steps, QA evidence | Findings files, agent-prompt-feedback |
| `knowledge/architecture/` | Systems Analyst | SA architecture design steps | ADRs, blueprints |

### Population at risk

**This diagnostic disproves the systemic risk estimated by the prior diagnostic's side-finding 3.** The prior diagnostic stated: "knowledge/development/ deposits are a recurring scope_check risk if the Planner doesn't include the deposit path in step text." The empirical evidence shows the Planner DID include the deposit path — the text-mention predicate passes.

Current deposit file counts in the bellows project: 270 total across all three directories. Every one of these was deposited by a plan step. If the Planner consistently includes deposit paths in `**Deposits:**` blocks (as Rule 26 requires), and `_extract_plan_required_deposits` handles the blockquote prefix (which it does — the `[> ]*` prefix in the regex at gates.py:388), then the text-mention predicate will pass for all deposits.

**Revised risk estimate:** The systemic risk from the text-mention predicate is **LOW**, not HIGH as the prior diagnostic estimated. The Planner IS mentioning deposit paths. The actual risk surface is **unidentified files** appearing in `files_changed` that are not declared deposits and not in allowlists — a different failure mode entirely.

---

## Q5 — Verification Block (Rule 39)

### Block 1 — Substring searches at exact byte offsets

Re-running the substring searches from Q1 with exact byte offsets to confirm the load-bearing claim.

**Method:** Python script reading the halted plan file, calling `_extract_step_text(plan_text, 1)` with the production gates.py module, then performing `str.find()` searches.

| Search | Byte offset | Verified? |
|---|---|---|
| `fpath` ("knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md") match #1 | 6184 | Yes — within `bellows/knowledge/development/...` on Deposits block line |
| `fpath` match #2 | 6675 | Yes — within `git add knowledge/development/...` on commit instruction line |
| `basename` ("planner-template-rule-21-contract-change-2026-05-26.md") match #1 | 208 | Yes — within `executable-planner-template-rule-21...` on claim instruction |
| `basename` match #2 | 350 | Yes — within `in-progress-executable-planner-template-rule-21...` on claim instruction |
| `basename` match #3 | 6206 | Yes — same line as fpath match #1 (basename is suffix of full path) |
| `basename` match #4 | 6697 | Yes — same line as fpath match #2 (basename is suffix of full path) |

**Conclusion:** The text-mention predicate `fpath in step_text or basename in step_text` evaluates to `True` for the dev log deposit. This is the load-bearing claim. **The assumed failure mode — deposit path absent from step text — is definitively disproven.**

### Block 2 — Terminal log gate failure confirmation

```
23:26:13 [EVENT] [executable-planner-template-ru] gates step 1: passed=False, failures=1
```

Source: `logs/terminal/bellows-2026-05-25.log`. Exactly 1 gate failure, confirmed.

### Block 3 — Ledger data-loss confirmation

Ledger entry for the Rule 21 plan (`verdicts/ledger.jsonl`):
- `gate_failures: []` — empty because `_consume_verdicts` at bellows.py:1226 creates `gate_result = {"failures": [], "files_changed": []}`
- `files_changed: []` — same cause
- `pause_reason_code: "gate_failure"` — preserved from the verdict request file's `**Pause Reason Code:**` field

The empty arrays are data-loss artifacts, not evidence of clean gates. The `pause_reason_code` is the only preserved signal from the original gate check.

---

## Decisions Made

1. **Classified the failure mode as (iv) Other — unidentified file in `files_changed`.** The text-mention predicate passes for all identified agent file operations. The tripping file is unknown.
2. **Recommended Fix Shape E** (preserve original gate_result in verdict ledger) as the primary structural fix. This closes the evidence-loss gap that made this diagnostic inconclusive.
3. **Downgraded the systemic risk from HIGH to LOW** for the text-mention predicate on deposit files. The Planner IS mentioning deposit paths in step text per Rule 26 convention.
4. **Identified a new risk surface:** unidentified files in `files_changed` (OS artifacts, editor temps, transient tool outputs) are a more likely recurring trigger than missing deposit mentions.

---

## Flags for CEO

1. **INCONCLUSIVE — evidence destroyed by verdict lifecycle data-loss.** The single scope_check gate failure at step 1 of the Rule 21 plan cannot be attributed to a specific file because `_consume_verdicts` at bellows.py:1226 creates a fresh empty `gate_result` and the original verdict request file is deleted at bellows.py:1292. The assumed failure mode (dev log not mentioned in step text) is empirically disproven — the text-mention predicate PASSES with 2 fpath matches and 4 basename matches.

2. **Fix Shape E recommended:** Preserve the original `gate_result` (failures + files_changed) in the verdict ledger instead of creating a fresh empty one at consumption time. This is a ~5-line change to `_consume_verdicts` that would have made this diagnostic conclusive. Without it, any future scope_check investigation will hit the same evidence wall.

3. **Fix Shape F complementary:** Expand the terminal log at bellows.py:495 to include the actual failure details and `files_changed` list, not just the count. This provides real-time forensic evidence during triage.

4. **Prior diagnostic disposition superseded.** The DESIGN-INTENT-AUDIT-NEEDED from `scope-check-post-fix-behavior-2026-05-26.md` asked "was the deposit path in the step text?" Answer: **YES.** The fix-shape decision between B (structural Deposits-block parsing) and D (governance rule) is moot — neither addresses the actual failure mode (unidentified file in files_changed).

5. **Next action:** Planner authors an executable for Fix Shape E (verdict ledger evidence preservation) + Fix Shape F (terminal log expansion). No scope_check code changes needed — the text-mention predicate works correctly.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done

Comprehensive empirical trace of the scope_check text-mention predicate against the Rule 21 plan's step 1 text. Proved the deposit path IS mentioned (2 fpath matches, 4 basename matches), disproving the prior diagnostic's leading hypothesis. Traced the gate failure to an unidentified file in `files_changed` and identified a structural evidence-loss gap in the verdict lifecycle that prevented conclusive attribution.

### Files Deposited

- `knowledge/research/scope-check-text-mention-audit-2026-05-26.md` — findings file with Q1–Q5 answers, fix-shape analysis, and evidence-loss gap identification

### Files Created or Modified (Code)

- None (read-only investigation)

### Decisions Made

- Classified failure mode as (iv) Other — unidentified file in files_changed
- Recommended Fix Shape E (preserve gate_result in ledger) as primary structural fix
- Downgraded systemic risk estimate from HIGH to LOW for text-mention predicate on deposits
- Identified new risk surface: unidentified files (OS artifacts, tool temps) in files_changed

### Flags for CEO

- INCONCLUSIVE — evidence destroyed by verdict lifecycle data-loss gap (bellows.py:1226)
- Fix Shape E (preserve gate_result in ledger) recommended — ~5-line change, enables all future gate forensics
- Fix Shape F (terminal log expansion) complementary
- Prior diagnostic's DESIGN-INTENT-AUDIT-NEEDED disposition superseded — text-mention predicate works, fix shapes A–D are moot

### Flags for Next Step

- None (single-step diagnostic)
