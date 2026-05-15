# Bellows — `_parse_diff_stat` Audit
**Date:** 2026-04-16 | **Type:** Diagnostic

## Context

During Phase 8's own rollout, Gate 8 (scope_check) flagged four files (COMPANY.md, LESSONS.md, bellows/config.json, governance/GUARDRAILS.md) as out-of-scope for Step 2 (QA). Investigation showed these were pre-existing uncommitted changes from earlier sessions — NOT modifications made during Step 2. The scope_check correctly flagged them, but the flag was a false alarm (the agent didn't modify them; they were just part of the working tree's dirty state).

The root cause appears to be in `_parse_diff_stat()` in bellows.py. The function currently takes `post_diff` and `pre_diff` as inputs but unions the filenames from both rather than computing the set difference. A file that was already modified before the step (present in `pre_diff`) AND still modified after the step (present in `post_diff`) is reported as "changed during this step" — but it wasn't; it was already dirty.

This diagnostic investigates the bug, quantifies its impact on the Phase 8 rollout, and sketches the fix without implementing it.

## How to Run

This diagnostic runs through Bellows. No YAML frontmatter is used — the test exercises the Phase 8 default-flip where diagnostics pause for verdict by default.

---
---

## STEP 1 — DEV (Bellows Developer)

---

> Skip specialist file and glossary reads. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. **Claim the plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-bellows-parse-diff-stat-audit-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-bellows-parse-diff-stat-audit-2026-04-16.md")`. **Investigate these four questions:** (1) Read `bellows.py` and find `_parse_diff_stat`. Paste its current implementation verbatim. Confirm whether it unions `pre_diff` and `post_diff` filenames (OR-semantics) or computes files that appeared/changed between them (DIFF-of-DIFFS semantics). (2) Trace the call sites — is `_parse_diff_stat(post_diff, pre_diff)` called with post first and pre second (matching its signature) or reversed? Paste the call sites with line numbers. (3) Construct a minimal test case showing the bug: simulate a `pre_diff` that contains "foo.py | 2 +-" (file already modified before step started) and a `post_diff` that contains the same "foo.py | 2 +-" (still modified, unchanged during step). Call `_parse_diff_stat(post, pre)` and show what it returns. Then show what it SHOULD return (empty list — the step didn't modify anything new). (4) Sketch the fix without implementing it. Describe what the corrected function would compute. Consider: should it be "files in post_diff that are NOT in pre_diff" (catches new modifications only), or "files whose stat-line-contents differ between pre_diff and post_diff" (catches any change, including staged edits that grew)? Recommend one approach with justification. **Deposit findings** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/bellows-parse-diff-stat-audit-2026-04-16.md`. Structure with sections Q1–Q4 plus a Summary at the top. Include Output Receipt with Status=Complete at the bottom. **Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` per protocol. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/bellows-parse-diff-stat-audit-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "diagnostic: audit _parse_diff_stat OR-vs-DIFF semantics"`. **Do NOT move the plan to Done — closure is handled by Planner verdict per Phase 8 default behavior.**
