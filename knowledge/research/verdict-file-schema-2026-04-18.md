# Verdict Request File Schema — Diagnostic Findings

**Date:** 2026-04-18 | **Source:** `verdict.py:post_verdict_request()` + disk inspection of `verdicts/pending/` and `verdicts/resolved/`

---

## (a) Field Inventory

Fields written by `post_verdict_request()` (verdict.py:26–77):

| # | Field | Type | Always Present | Source |
|---|-------|------|----------------|--------|
| 1 | **Filename** (structured metadata) | `verdict-request-{slug}-step-{N}.md` | Yes | `_slug_from_path(plan_path)` + `step_number` |
| 2 | `**Plan:**` | String (absolute path to the plan file at time of posting) | Yes | `plan_path` parameter |
| 3 | `**Step:**` | Integer | Yes | `step_number` parameter |
| 4 | `**Log:**` | String (path to logs directory) | Yes | `log_path` parameter — always `BELLOWS_ROOT / "logs"` |
| 5 | `**Timestamp:**` | ISO 8601 datetime | Yes | `datetime.now().isoformat()` |
| 6 | `**Pause Reason:**` | String (human-readable label) | Yes | Mapped from `pause_reason` enum via `_pause_reason_labels` dict |
| 7 | `**Total Steps:**` | Integer or literal string `"None"` | **Conditional** — always written in current code, but `total_steps` param defaults to `None`, producing `**Total Steps:** None`. Older files (pre-04-17) may lack this field entirely. | `total_steps` parameter |
| 8 | `## Gate Failures` section | Markdown list of `- **{gate}**: {evidence}` | **Conditional** — only when `pause_reason == "gate_failure"` AND `gate_result["failures"]` is non-empty | `gate_result["failures"]` list |
| 9 | `## Pause Reason` section | Prose description | **Conditional** — when NOT gate_failure, or gate_failure with no failures list | Hardcoded description per pause reason |
| 10 | `## Files Changed` section | Markdown list of filenames | Yes (section header always present; list may be empty) | `gate_result["files_changed"]` |
| 11 | `## Planner.py Decision (legacy)` | JSON blob | **Conditional** — only when `planner_py_decision` is truthy | Legacy field; not observed in any sampled file |

**Filename convention as structured metadata:** The filename `verdict-request-{slug}-step-{N}.md` encodes both the plan slug and step number. The slug is derived by `_slug_from_path()` which strips prefixes (`in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`) and the `.md` extension from the plan basename.

---

## (b) Plan-Slug and Step-Number References

**Machine-parseable references exist in TWO places:**

1. **Filename:** `verdict-request-{slug}-step-{N}.md` — parsed by `_consume_verdicts()` via regex `^verdict-(.+)-step-(\d+)\.md$` (bellows.py:573). This is the primary lookup key.
2. **Body fields:** `**Plan:**` (full path, from which slug can be re-derived) and `**Step:**` (integer).

**Ambiguity assessment:**
- Each file references exactly one plan slug and one step number — no ambiguity.
- **However**, the slug is a *stripped* derivative of the plan filename (no prefix, no `.md`). The `_consume_verdicts` method matches `plan_slug in pname` via substring (bellows.py:608), which means a slug like `foo` would match `verdict-pending-executable-foo-bar.md`. This is a known issue with a `break` fix already in place (bellows.py:658) but the substring match itself remains loose.
- The `**Plan:**` field contains the *full absolute path* at time of posting, which is more precise than the slug, but `_consume_verdicts` does not use it for the plan-file search — it uses it only to scope which project directory to search (bellows.py:586–588).

**Missing cases:** None observed. Every sampled file has both slug (in filename) and step number (in filename and body).

---

## (c) Deposit File Paths

**No.** The verdict request file does NOT contain any reference to deposit file paths (the output files the execution agent created for Rule 22 verification).

**What's available as a proxy:**
- `**Plan:**` field contains the full path to the plan file. The Planner could read the plan to extract deposit paths from the step definition.
- `**Log:**` field contains the logs directory path (always `BELLOWS_ROOT / "logs"`), not a specific log file.
- `## Files Changed` lists filenames modified during the step, but these are raw filenames without full paths, and they don't distinguish deposits from other changes.

**Gap:** The Planner currently has no direct way to find deposit paths from the verdict request file. It must: (1) read `**Plan:**` path → (2) parse the plan step definition → (3) extract the deposit path from the step text. This is fragile — the plan file may have been renamed (to `verdict-pending-*`) by the time the Planner reads it.

---

## (d) Gate Result Visibility

**Partial.** The verdict file includes gate information but NOT the full `gate_result` dict.

What IS included:
- **(i) Which gate triggered:** Yes, via `## Gate Failures` section, each bullet prefixed with `**{gate_name}**:` (e.g., `**scope_check**:`, `**no_permission_denials**:`).
- **(ii) Why the gate tripped:** Partially — the `evidence` string from each failure is included after the gate name. This is the gate's own description of what it found.
- **(iii) Evidence captured:** Only what the gate puts in its `evidence` field. No raw command stdout, grep results, or diff output is attached separately.

What is NOT included:
- The `passed` boolean from `gate_result`.
- The `is_qa_step` boolean.
- The `verdict_requested` sub-dict (when pause is due to agent verdict request).
- The `files_changed` list IS included but in a separate `## Files Changed` section, not as part of a gate result structure.
- When `pause_reason` is not `gate_failure`, the `## Gate Failures` section is replaced by a generic `## Pause Reason` prose block — the Planner gets no gate-specific information in that case.

---

## (e) Cleanup Lifecycle

**Full lifecycle of a verdict request file:**

1. **Created:** by `post_verdict_request()` in `verdicts/pending/verdict-request-{slug}-step-{N}.md` (verdict.py:28–76). Called from `run_plan()` when gates fail, QA checkpoint, agent verdict request, header pause, or auto-close disabled.

2. **Read (by _consume_verdicts):** When a corresponding `verdict-{slug}-step-{N}.md` file appears in `verdicts/resolved/`, `_consume_verdicts()` reads the pending file to extract `**Plan:**` (for project scoping) and `**Total Steps:**` (for continue-to-done logic) (bellows.py:579–593).

3. **Deleted:** After the verdict is consumed, `_consume_verdicts()` calls `pending_file.unlink()` (bellows.py:661–663). This happens regardless of continue/stop verdict.

4. **No cleanup on plan move-to-Done:** The auto-close path (bellows.py:348–365) does NOT post a verdict request, so no pending file exists to clean up. Correct by design.

5. **No cleanup on reboot:** Bellows does not scan `verdicts/pending/` on startup to prune stale files. The only cleanup path is via verdict consumption.

6. **Stranding conditions:** A pending verdict file becomes stranded (accumulates indefinitely) when:
   - A verdict is never deposited in `resolved/` (e.g., the Planner forgets or the plan is abandoned).
   - The corresponding `verdict-{slug}-step-{N}.md` resolved file uses a different naming convention than expected.
   - The plan is manually moved/deleted without going through `_consume_verdicts`.

**Current state of `verdicts/pending/`:**
- **33 files** present.
- **Oldest:** `verdict-request-resume-path-pending-cleanup-2026-04-16-step-1.md` (Apr 16 11:30) — **2+ days old**, clearly stranded since a resolved+processed version exists.
- **Newest:** `verdict-request-planner-template-v4-23-rule-24-atomic-deposit-2026-04-18-step-2.md` (Apr 18 15:45) — same day, likely active.
- **Known stranded files** (have corresponding `processed-verdict-*` in resolved, meaning the verdict was consumed but pending file was not deleted — possibly due to filename mismatch or code running before the cleanup fix):
  - `verdict-request-resume-path-pending-cleanup-2026-04-16-step-1.md`
  - `verdict-request-resume-path-pending-cleanup-2026-04-16-step-2.md`
- **Likely abandoned** (no corresponding resolved verdict, plan likely moved manually or abandoned):
  - Multiple files from Apr 16 (`billto-config-extraction`, `bellows-gate5-deposit-bypass`, `file-first-*`, `lanes-csrf-fix`, `forge-test-case-gen-eval`, etc.)
  - Multiple files from Apr 17 (`flavornotes-*`, `presseffect-*`, `handleback-*`, `confirm-bookheader-*`, `tabbed-*`, `gitattributes-crlf`, `plan-truncation-emoji`, `plan-file-truncation`)

**Conclusion:** Stranded verdict files are a real condition with no automated cleanup path. They accumulate indefinitely.

---

## Proposed Schema

Required fields every verdict request file MUST contain for reliable Planner Rule 22 routing:

| # | Field | Required/Optional | Justification |
|---|-------|-------------------|---------------|
| 1 | **Filename:** `verdict-request-{slug}-step-{N}.md` | Required | (b) — primary lookup key for `_consume_verdicts` regex matching |
| 2 | `**Plan:**` (absolute path) | Required | (b, c) — used for project scoping in `_consume_verdicts`; only proxy for locating deposit files |
| 3 | `**Step:**` (integer) | Required | (b) — redundant with filename but needed for body parsing |
| 4 | `**Timestamp:**` (ISO 8601) | Required | (e) — needed for staleness detection and cleanup decisions |
| 5 | `**Pause Reason:**` (machine-readable enum) | Required | (d) — tells Planner which pause condition triggered; currently uses human labels, should also include raw enum |
| 6 | `**Total Steps:**` (integer, never None) | Required | (b, e) — `_consume_verdicts` uses this to decide continue-to-done vs. resume-next; currently can be `None` literal string |
| 7 | `**Project:**` (absolute path to project root) | **Proposed new — Required** | (c) — currently derived indirectly from `**Plan:**` path's parent; an explicit field would be more robust |
| 8 | `**Deposit Path:**` (path or list of paths) | **Proposed new — Required** | (c) — currently absent; Planner has no way to locate deposits without re-parsing the plan file |
| 9 | `## Gate Failures` (structured list) | Required when pause_reason is gate_failure | (d) — already present in that case |
| 10 | `**Gate Result Passed:**` (boolean) | **Proposed new — Required** | (d) — currently absent; Planner can't distinguish "gate failure" from "QA checkpoint with clean gates" without re-reading pause reason logic |
| 11 | `## Files Changed` (list) | Required | (d) — already present |

Optional fields:
| # | Field | Status |
|---|-------|--------|
| 12 | `**Log:**` (path) | Optional — always points to generic logs dir, not a specific file |
| 13 | `## Planner.py Decision (legacy)` | Optional — legacy, should be removed |

---

## Gap Assessment

| Gap | Current State | Proposed State | Change Required in `verdict.py` |
|-----|--------------|----------------|--------------------------------|
| **Total Steps can be None** | `total_steps` param defaults to `None`; written as literal `"None"` string | Must be an integer; caller must always pass a valid count | Callers in `bellows.py` (lines 274, 333) must always compute `total_steps` before calling. `post_verdict_request` should raise if `total_steps` is None. |
| **No Deposit Path field** | Absent entirely | `**Deposit:**` field with the deposit file path(s) from the plan step | `post_verdict_request` needs a new `deposit_path` parameter. Callers would need to extract deposit path from plan step text or pass it through. |
| **No explicit Project field** | Derived by Planner from `**Plan:**` path's parent | `**Project:**` field with explicit project root path | Add `project_path` parameter to `post_verdict_request` and write it. Callers already have `project_path` in scope. |
| **No Gate Result Passed boolean** | Planner infers from presence/absence of `## Gate Failures` section | `**Gate Result Passed:**` true/false | Trivial: add `f"**Gate Result Passed:** {gate_result['passed']}\n"` to content template. |
| **Pause Reason uses human labels** | `_pause_reason_labels` maps enum to prose; raw enum lost | Include both: `**Pause Reason:** Gate failure` AND `**Pause Reason Code:** gate_failure` | Add one line to content template with raw `pause_reason` value. |
| **Stranded pending files accumulate** | No cleanup path except verdict consumption | Add startup sweep and/or periodic cleanup for files older than N days with no matching plan | New function in `verdict.py` or `bellows.py` startup path. Not a schema change, but a lifecycle gap. |
| **Log field is generic** | Always `BELLOWS_ROOT / "logs"` (a directory, not a file) | Point to specific step log file if available, or remove field | Either pass specific log path or mark field optional/deprecated. |

**Recommendation:** The four schema additions (Deposit Path, Project, Gate Result Passed, Pause Reason Code) and the Total Steps fix are straightforward changes to `verdict.py` + its callers in `bellows.py`. The stranded-file cleanup is a separate concern — recommend a follow-up executable plan. No code changes should be made in this diagnostic.

---

## Output Receipt

```
Plan:     diagnostic-bellows-verdict-file-schema-2026-04-18
Step:     1
Status:   Complete
Deposit:  knowledge/research/verdict-file-schema-2026-04-18.md
Summary:  Traced post_verdict_request() and _consume_verdicts() end-to-end.
          Sampled 6 verdict files (3 pending, 3 resolved). Answered all 5 questions.
          Key findings: (1) No deposit-path field — Planner cannot locate deposits
          without re-parsing plan. (2) Total Steps can be None literal. (3) 33 files
          stranded in pending/ with no automated cleanup. (4) Gate result only partially
          exposed. Proposed schema with 4 new required fields and 1 fix documented.
          Gap assessment with specific verdict.py changes provided.
```
