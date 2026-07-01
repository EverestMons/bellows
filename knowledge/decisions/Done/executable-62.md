# Bellows — Ledger Subsection Over-Capture Fix (trailing prose) + FORWARD single-line item
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
The FORWARD re-canary (plan 61) proved the FORWARD ledger fires end-to-end (daemon appended a row, committed, logged), BUT exposed a parser over-capture bug: the `### Ledger Updates` subsection regexes (parser.py — feedback ~L60, project_status ~L67, forward ~L75: `#### …\s*\n(.*?)(?=\n#### |\Z)` with DOTALL) capture everything from the heading to the next `#### ` OR end-of-text. When a subsection is the LAST block and the agent has trailing prose after it (e.g. "Now commit the deposit. Complete. All 5 checks passed:"), that prose is captured into the ledger value. For feedback/PROJECT_STATUS this is a quality wart (multi-line entries tolerate it); for FORWARD it BREAKS — the multi-line item_text splits the markdown table row (observed: FORWARD.md row 23 has 3 pipes instead of 7, with stray prose on the following lines). Two fixes: (1) tighten each subsection capture to stop at a blank line (`\n\s*\n`) as well as the next `#### `/`### `/`\Z`, so trailing prose after a blank line is excluded from ALL three ledgers; (2) belt-and-suspenders in `_append_forward_row` (bellows.py:1265): sanitize item_text to a SINGLE LINE (first non-empty line, collapse internal whitespace) so a FORWARD row is always valid even if extraction returns multi-line. Plus cleanup: remove the malformed canary row 23 + its stray trailing prose lines from `bellows/knowledge/FORWARD.md` (Rule 42 direct status edit). Anchors (re-verify by grep): parser.py subsection regexes ~L59–81; `_append_forward_row` ~L1265. DAEMON RESTART REQUIRED after close; a final FORWARD re-canary (clean single-line row) is the proof.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then the three subsection regexes in `parser.py` and `_append_forward_row` in `bellows.py`. **Scope is exactly these files: `parser.py`, `bellows.py`, `tests/test_parser.py`, `tests/test_bellows.py`.**
> - **(1) Tighten subsection capture (parser.py):** change each of the three subsection regexes so the captured body stops at the FIRST of: the next `#### ` heading, the next `### `/`## ` heading, a blank line (`\n\s*\n`), or end-of-text. Then `.strip()` the captured value. Goal: capture only the intended subsection content, not trailing prose that follows a blank line. Keep the existing extraction working for clean single-block and legitimate multi-line (no-blank-line) content.
> - **(2) FORWARD single-line item (bellows.py `_append_forward_row`):** before building `new_row`, sanitize `item_text` to a single line — take the first non-empty line and collapse internal runs of whitespace to single spaces, strip a trailing period-only artifact if present. This guarantees a valid 6-column row regardless of what extraction returns. (Feedback/PROJECT_STATUS keep multi-line — only FORWARD needs single-line.)
> - **(3) Cleanup:** in `bellows/knowledge/FORWARD.md`, remove the malformed canary row (the `| 23 | … | CANARY-FORWARD2-180522 …` line) AND its stray trailing prose lines (e.g. "Now commit the deposit.", "Complete. All 5 checks passed:" and any other non-table lines that the over-capture appended). Leave the rest of the register untouched. (This is a Rule 42 direct status/cleanup edit by the daemon-developer on main.)
>
> **Tests:** (a) parser: a subsection followed by a blank line + trailing prose captures ONLY the subsection content (the regression repro); a legitimate multi-line subsection (no blank line) still captures fully; (b) `_append_forward_row`: a multi-line item_text yields a single-line, valid 7-pipe row; a normal single-line item is unchanged; (c) confirm FORWARD.md no longer has a malformed row (`grep -c '^| [0-9]'` rows all have 7 pipes). Run the FULL suite (`python3 -m pytest tests/`) to explicit pass/fail and READ THE TAIL. Write the dev log to `bellows/knowledge/development/ledger-overcapture-fix-dev-log-2026-06-14.md`. Use `with open()`; no heredocs. Standard prompt feedback → emit via `### Ledger Updates > #### Prompt Feedback`. **Deposits:**
> - `bellows/knowledge/development/ledger-overcapture-fix-dev-log-2026-06-14.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md` and the dev log. **Verify, each with executed evidence (files into `knowledge/qa/evidence/ledger-overcapture-fix-2026-06-14/`):** (1) **Full suite** — final 15 lines, zero failures, new-test count matches dev log; `full_suite_tail.txt`. (2) **Over-capture fixed** — the parser test proves trailing-prose-after-blank-line is excluded; legitimate multi-line still works; `overcapture.txt`. (3) **FORWARD single-line** — multi-line item → valid single-line 7-pipe row test passes; `forward_singleline.txt`. (4) **FORWARD.md clean** — every `| <n> |` row in bellows/knowledge/FORWARD.md has exactly 7 pipes; no stray prose lines; the malformed row 23 is gone; `forward_clean.txt`. (5) **No regression** — feedback/project_status extraction unaffected for clean cases; `no_regression.txt`. (6) **Scope** — `git diff HEAD~1 --stat` only in-scope files; `scope.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `ledger-overcapture-fix-2026-06-14`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/ledger-overcapture-fix-qa-report-2026-06-14.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/ledger-overcapture-fix-2026-06-14/`; `required_evidence_files`: `[full_suite_tail.txt, overcapture.txt, forward_singleline.txt, forward_clean.txt, no_regression.txt, scope.txt]`. Include the literal stdout of the block. If it prints `FAILED`, halt and report to CEO. Write the QA report (verification table + Rule 20 banner) to `bellows/knowledge/qa/ledger-overcapture-fix-qa-report-2026-06-14.md`. **Receipt Flags for CEO:** (1) DAEMON RESTART REQUIRED; (2) final FORWARD re-canary after restart must land a CLEAN single-line 7-pipe row — that completes the daemon-owned-ledgers effort. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/ledger-overcapture-fix-qa-report-2026-06-14.md`
> - `bellows/knowledge/qa/evidence/ledger-overcapture-fix-2026-06-14/` (six evidence files per Rule 20 self-check)
