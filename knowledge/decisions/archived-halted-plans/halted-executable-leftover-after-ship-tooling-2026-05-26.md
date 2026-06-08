# Bellows — Leftover-After-Ship Tooling Script
**Date:** 2026-05-26 | **Tier:** small-build | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **qa_steps:** 3 | **pause_for_verdict:** after_step_1

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows claims and dispatches Step 1 to the SA agent. SA produces a script blueprint and pauses for CEO review. After continue verdict, DEV implements, then QA verifies against the 4 ground-truth recurrence cases.

## Context

Today's LESSON (`/Users/marklehn/Developer/GitHub/LESSONS.md`, 2026-05-26 "Leftover after ship" entry) documented the 5th recurrence of BACKLOG entries describing already-shipped work that were never moved to Closed. The recommended remediation is tooling, not a discipline rule — the Planner's Phase 1.5 grep already catches 5/5, but the catch is expensive vigilance that automation can replace.

Scope diagnostic findings: `bellows/knowledge/research/leftover-after-ship-tooling-scope-findings-2026-05-26.md`. Key inputs:
- BACKLOG.md has two H2 sections (`## Open`, `## Closed`); Open entries prefixed `**Added <DATE>:**`, Closed entries prefixed `**Closed <DATE> [(reason)]:**`. No formal IDs.
- PROJECT_STATUS.md Completed entries are `- <YYYY-MM-DD>: **<title>** ... Reference: <slug>` single-line bullets in reverse-chrono order.
- Git commits use `closes BACKLOG <name>` in fix/feat subjects; separate `chore: backlog hygiene` commits handle Open→Closed moves.
- 4 ground-truth recurrences (1-4 from the LESSON enumeration): set→list, precondition-failure-field, Phase 3b read-side, mcp__vexp__. All 4 share the pattern "code shipped to commit log + PROJECT_STATUS Completed entry, but Open BACKLOG entry never moved." Recurrence 5 (WebSearch/WebFetch defer) has different shape and is out of scope for v1.
- Natural home: `bellows/scripts/check_backlog_freshness.py` (matches existing Python convention; existing scripts `migrate_config.py`, `migrate_orphan_verdicts.py` use the `Path(__file__).parent.parent.resolve()` root pattern).
- Natural invocation: Planner's session-start Phase 1.5. Manual invocation only — no daemon integration.

CEO decisions locked: v1 scope = code-shipped pattern only (recurrences 1-4); output destination = deposit to `knowledge/research/backlog-freshness-check-<DATE>.md`; no pytest, hand-test against 4 ground-truth cases.

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-leftover-after-ship-tooling-2026-05-26.md", "bellows/knowledge/decisions/in-progress-executable-leftover-after-ship-tooling-2026-05-26.md")`. Read your specialist file and domain glossary first. Read the scope diagnostic findings at `bellows/knowledge/research/leftover-after-ship-tooling-scope-findings-2026-05-26.md` — that file contains verbatim samples of BACKLOG.md, PROJECT_STATUS.md, the git log, and the 4 ground-truth recurrence cases. Produce a script blueprint for `bellows/scripts/check_backlog_freshness.py`. **The script's job:** scan `bellows/knowledge/BACKLOG.md`'s `## Open` section, and for each Open entry, identify candidate closures by matching against (a) recent `bellows/PROJECT_STATUS.md` Completed entries and (b) recent git commit subjects from `git --no-pager log --since="<DEFAULT_WINDOW_DAYS> days ago" --pretty=format:"%h %s"` in the bellows submodule. Output a Markdown report deposited to `bellows/knowledge/research/backlog-freshness-check-<YYYY-MM-DD>.md` listing each Open entry and its top candidate closures (if any) with the matching evidence. **Blueprint must specify:** (1) **Parsing approach for BACKLOG.md** — how to identify the `## Open` section, how to split it into individual entries, how to extract the entry's date prefix and a matching key (whatever you choose — distinctive noun phrase, slug from `Reference:` field, commit SHA, or composite). State the regex or parser shape literally. (2) **Parsing approach for PROJECT_STATUS.md Completed section** — how to extract date, title, and `Reference:` field per entry. Same: state the regex or parser shape literally. (3) **Git log parsing** — how to extract commit SHAs and subjects from `git --no-pager log` output, how to scope to the last N days, what N defaults to (recommendation: 14 days, but justify). (4) **Matching algorithm** — given a BACKLOG Open entry's matching key, how to score candidate closures from PROJECT_STATUS and git commits. The 4 ground-truth cases all have an executable slug in the commit subject (`closes BACKLOG <name>` or via Reference field) — the slug-match is the strongest signal. Define the scoring shape (binary match? fuzzy? multi-signal weighted?) and the threshold for "report as candidate closure." Recommend the simplest shape that catches all 4 ground-truth cases without false positives against the 6 currently-Open entries in BACKLOG. (5) **Output format** — Markdown report shape. One section per Open entry, each section showing: the entry's first line (date + truncated title), candidate closures listed by source (PROJECT_STATUS row / git commit SHA + subject) with evidence excerpts, and a recommended action (`investigate-as-shipped`, `no-match`, etc.). Include a header summary: total Open entries scanned, total candidate closures surfaced, total no-match. (6) **CLI shape** — argument parser, defaults, exit codes. Recommendation: zero arguments (read defaults from constants), optional `--window-days N`, `--output-path PATH`. Exit 0 always (informational, not a gate). (7) **Constants and paths** — module-level constants for BACKLOG_PATH, PROJECT_STATUS_PATH, SCRIPTS_ROOT, BELLOWS_ROOT (using the `Path(__file__).parent.parent.resolve()` pattern from existing scripts). (8) **Validation against 4 ground-truth cases** — for each of the 4 recurrences from the scope findings file (set→list, precondition-failure-field, Phase 3b read-side, mcp__vexp__), trace the blueprint's matching algorithm by hand and confirm each would be flagged. Document the trace. **Constraints:** Python stdlib only (no requests, no pyyaml, no rich). No external API calls. No mutation of any file (read-only operation; the only write is the report deposit). Script must be idempotent (same inputs → same output). Total target size: ~150-250 lines including docstring, parsing, matching, output, and CLI. **Deposits:**
> - `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md` — full blueprint per (1)-(8) above
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — DEV

---

> Before starting, read `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md` and check the Output Receipt status field. If status is not Complete or Partial with known acceptable scope, stop and report the issue to the CEO before proceeding. Read your specialist file and domain glossary first. **Task:** implement `bellows/scripts/check_backlog_freshness.py` per the SA blueprint. Follow the blueprint literally — parsing regexes, matching algorithm, output format, CLI shape, constants. Match the existing scripts' style (`migrate_config.py`, `migrate_orphan_verdicts.py`): shebang `#!/usr/bin/env python3`, module-level docstring, `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()` constant, single `main()` entry point, `if __name__ == "__main__": main()` guard. **After implementing**, execute the script against the live repo (`python bellows/scripts/check_backlog_freshness.py`) and capture the produced report at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. Inspect the report to confirm the 4 ground-truth recurrence cases would have been flagged — they are now Closed in BACKLOG so they won't appear in this run, but the matching algorithm's correctness can be traced manually by reading the script's output for each of the 6 currently-Open entries and confirming no false positives surface. **Constraints:** Python stdlib only. No mutations to BACKLOG.md, PROJECT_STATUS.md, or any other file outside the deposited report. All git commands use `git --no-pager`. **Deposits:**
> - `bellows/knowledge/development/leftover-after-ship-tooling-2026-05-26.md` — dev log per `SPECIALIST_TEMPLATE.md` conventions, including the script's actual produced output excerpted, manual trace against 4 ground-truth cases confirming each would have been flagged by the algorithm, and a notes section on any blueprint deviations
>
> The freshness report itself (`bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`) is a side effect of running the script — created by the script itself, not by the agent — and is NOT listed as a deposit.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 3 — QA

---

> Before starting, read `bellows/knowledge/development/leftover-after-ship-tooling-2026-05-26.md` and check the Output Receipt status field. If status is not Complete or Partial with known acceptable scope, stop and report the issue to the CEO before proceeding. Read your specialist file and domain glossary first. **Verification checks:**
>
> 1. **Script exists and is executable** — `ls -la bellows/scripts/check_backlog_freshness.py` shows a file with reasonable size (150-250 lines per blueprint target). `head -5` shows the canonical shebang.
> 2. **Stdlib-only** — `grep -E "^import |^from " bellows/scripts/check_backlog_freshness.py` lists only stdlib modules (re, pathlib, subprocess, argparse, datetime, sys, collections, etc.). Any third-party import is a FAIL.
> 3. **Idempotency** — run the script twice (`python bellows/scripts/check_backlog_freshness.py && diff bellows/knowledge/research/backlog-freshness-check-2026-05-26.md /tmp/backlog-fresh-run2.md` after capturing the second run). Byte-identical output is PASS.
> 4. **No mutations** — `git status` after running the script should show only `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md` as modified (or untracked) and the QA-step artifacts. No changes to BACKLOG.md, PROJECT_STATUS.md, or any source file.
> 5. **Ground-truth trace** — read the dev log's manual trace section. Confirm each of the 4 recurrences (set→list, precondition-failure-field, Phase 3b read-side, mcp__vexp__) is traced through the algorithm with evidence that the algorithm would have flagged it AT THE TIME the recurrence happened (i.e., before the BACKLOG entry was moved to Closed). PASS only if all 4 traces are coherent and the algorithm flags each.
> 6. **No false positives on currently-Open entries** — read the produced freshness report. For each Open entry that the script flagged as having a candidate closure, manually verify by reading the cited PROJECT_STATUS row or git commit whether the match is a real closure signal or a false positive. Document each flagged entry's verification verdict in the QA report. PASS = zero false positives. PARTIAL = false positives surfaced but algorithm caught all 4 ground-truth cases (acceptable for v1 with documented follow-up).
> 7. **Report file shape** — the deposited freshness report has the header summary (total entries scanned, candidates surfaced, no-match count), one section per Open entry, and uses Markdown formatting consistent with other deposits in `knowledge/research/`.
>
> Run the full canonical Rule 20 self-check block (see `RULE_20_SELF_CHECK_BLOCK.md` at governance root) using these context values: `plan_slug = executable-leftover-after-ship-tooling-2026-05-26`, `qa_report_path = bellows/knowledge/qa/executable-leftover-after-ship-tooling-2026-05-26.md`, `evidence_dir = bellows/knowledge/qa/evidence/executable-leftover-after-ship-tooling-2026-05-26/`, `required_evidence_files = [check1_script_inspect.txt, check2_imports.txt, check3_idempotency_diff.txt, check4_git_status.txt, check5_ground_truth_trace.md, check6_false_positive_review.md, check7_report_shape.txt]`.
>
> Update `bellows/PROJECT_STATUS.md` with a Completed entry for this plan as a side effect — NOT listed in deposits.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-leftover-after-ship-tooling-2026-05-26.md` — QA report including all 7 verification checks with PASS/FAIL/PARTIAL verdict per check, the Rule 20 self-check banner block, and the standard Output Receipt
>
> Evidence files go in `bellows/knowledge/qa/evidence/executable-leftover-after-ship-tooling-2026-05-26/` (directory, single Rule 26 deposit bullet not required since deposits block declares only the QA report markdown).
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
