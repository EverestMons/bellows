# bellows — Shadow Copy Plan Cache (Truncation Fix v3)
**Date:** 2026-04-17 | **Type:** Executable | **Priority:** 2 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:** `Read the plan at bellows/knowledge/decisions/executable-shadow-copy-cache-2026-04-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## Context

Claude Code agents rewrite plan files during execution (removing completed step sections). Bellows reads the plan file for metadata (total_steps, step text for bootstrap prompts) and gets wrong values from the truncated file. The v2 fix (storing total_steps in verdict metadata) only covers `_consume_verdicts` — the initial `run_plan` dispatch still reads from the on-disk file, which may be truncated from a prior failed run. The structural fix: cache the pristine plan content at first claim and never read the on-disk file for metadata again.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-shadow-copy-cache-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-shadow-copy-cache-2026-04-17.md")`. Read `bellows/bellows.py` in full, focusing on `run_plan` and `_consume_verdicts`. **Single commit.**
>
> Create a shadow copy mechanism: **(a)** When `run_plan` first claims a plan (the `shutil.move` to `in-progress-`), immediately AFTER the move, write the original `plan_text` to a shadow file at `.bellows-cache/{plan_filename}.pristine`. Create the `.bellows-cache/` directory under `BELLOWS_ROOT` if it doesn't exist. This preserves the full plan content before any agent touches it. **(b)** At the top of `run_plan`, AFTER loading `plan_text = load_file(plan_path)`, check if a shadow copy exists at `.bellows-cache/{plan_filename}.pristine`. If it does, use the shadow copy for ALL metadata extraction (`extract_total_steps`, `_parse_plan_header`, bootstrap prompt construction) instead of `plan_text`. If no shadow copy exists (first run), use `plan_text` as-is — the shadow will be created after claiming. **(c)** In `_consume_verdicts`, when resuming a plan after a verdict: read the shadow copy for `total_steps` and step text instead of `load_file(full_plan_path)`. The shadow path is `.bellows-cache/{original_name}.pristine` where `original_name` strips the `verdict-pending-` prefix. Fall back to the verdict-request `Total Steps` field if no shadow exists (backward compat with plans that ran before this fix). Fall back to `load_file` as last resort. **(d)** When a plan moves to Done (either auto-close or verdict-continue-to-done), delete its shadow file from `.bellows-cache/`. Don't leave stale cache files around. **(e)** Add `.bellows-cache/` to `.gitignore` — these are ephemeral runtime files, not tracked. **(f)** Print when using shadow: `print(f"Bellows: using cached plan content ({total_steps} steps)")` so the CEO can see it's reading the pristine copy. Commit: `feat: shadow copy plan cache — preserve pristine plan content for metadata reads`.
>
> **Deposit dev log** to `bellows/knowledge/development/shadow-copy-cache-2026-04-17.md`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/shadow-copy-cache-2026-04-17.md` and check Output Receipt. If not Complete, stop. **Verification.** (a) `.bellows-cache/` directory creation — grep `bellows.py` for `bellows-cache` and `mkdir`. (b) Shadow write — grep for `.pristine` and confirm it's written after plan claim. (c) Shadow read — grep for `.pristine` in both `run_plan` and `_consume_verdicts`. Confirm metadata reads prefer shadow over on-disk file. (d) Shadow cleanup — grep for `unlink` or `os.remove` on `.pristine` at plan close. (e) `.gitignore` — confirm `.bellows-cache/` is listed. (f) Verify the fallback chain: shadow → verdict metadata → load_file. Pipe evidence to `bellows/knowledge/qa/evidence/executable-shadow-copy-cache-2026-04-17/grep_deliverables.txt`. **Deposit QA report** to `bellows/knowledge/qa/shadow-copy-cache-qa-2026-04-17.md`.
>
> **Rule 20 Self-Check:**
> ```python
> import os, sys
> plan_slug = "executable-shadow-copy-cache-2026-04-17"
> qa_report_path = "bellows/knowledge/qa/shadow-copy-cache-qa-2026-04-17.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             else:
>                 if cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence present, no hedging.")
> ```
>
> If FAILS, STOP. If PASSES: move to Done. Commit: `chore: move shadow-copy-cache to Done`. Standard prompt feedback protocol.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
