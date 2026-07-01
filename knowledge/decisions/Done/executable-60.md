# Bellows — Ledger Extraction: Capture Tool-Write Content (multi-channel robustness)
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
This executable implements diagnostic 58. CEO fork verdict (processed-verdict-58-step-1): Option A — expand the runner's assistant-text capture to ALSO include Write/Edit tool-content, so an Output Receipt the agent emits inside a file-write (not as bare text) is still parsed. ROOT CAUSE (diagnostic 58, authoritative): the plan-57 FORWARD canary agent emitted `### Ledger Updates > #### Forward Register` only inside a Write `tool_use` block; `runner.py` (~230–234) captures only `type:"text"` blocks from assistant turns, excluding tool content, so `_all_assistant_text` lacked the heading → parser extracted nothing → silent drop. The SAME issue is a LATENT risk for feedback + PROJECT_STATUS (plan 55 emitted bare text by luck). The defense WARN ALSO missed it because `_all_assistant_text` is not propagated into the `parsed` dict (bellows.py:1138 reads `parsed.get("_all_assistant_text")` which is absent → falls back to result_text, which lacked the heading too). FP RISK ACCEPTED (CEO): including tool content could in theory mis-parse a deposit file that literally contains a clean `### Ledger Updates`/`#### …` block; the subsection regexes are specific enough that this is low-risk. Two changes:
1. **G1 (runner.py ~230–234):** in the assistant-event loop, ALSO collect text from `tool_use` blocks whose `name` is `Write` or `Edit` — capture the file `content` being written (per the SDK event shape; verify the exact key, e.g. `block["input"]["content"]` for Write, the new/replacement string for Edit) and append to `assistant_text_parts`. Keep the existing `type:"text"` capture.
2. **G2 (parser.py):** propagate `_all_assistant_text` (the `ledger_source` at parser.py:53) into the returned `parsed` dict so the bellows.py:1138 defense WARN evaluates against the FULL text (tool content included) — making the WARN able to fire on any future tool-content-only or genuinely-missing emission.
Anchors (re-verify by grep): runner.py assistant loop ~230–234 + `_all_text` assembly ~259–262; parser.py:53 `ledger_source`; bellows.py:1138 WARN `_src`. DAEMON RESTART REQUIRED after close; the re-canary (a fresh FORWARD canary) is the live proof — Slice 3 / FORWARD stays unproven until it passes.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, the diagnostic root-cause IN FULL, and the existing runner.py assistant-text capture + `_all_text` assembly + parser.py:53 + the bellows.py WARN. **Scope is exactly these files: `runner.py`, `parser.py`, `tests/test_runner.py`, `tests/test_parser.py`, `tests/test_bellows.py`.**
> - **G1:** extend the runner's assistant-event content loop to also append text from `tool_use` blocks named `Write` or `Edit`. Determine the correct content key from the actual event shape (the diagnostic identified the receipt lived in a Write tool_use `content`); capture the written file content (for Edit, capture the new_string/replacement text). Append to `assistant_text_parts` alongside the existing `type:"text"` capture. Do NOT break the existing text capture or the `result` append.
> - **G2:** ensure `parser.parse()` includes `_all_assistant_text` (the `ledger_source`) in its returned dict so `bellows.py`'s defense WARN reads the full text. Confirm the WARN then fires when `### Ledger Updates` is present in the full text but the parsed ledger is all-None.
> - Do NOT add an anti-false-positive guard (CEO accepted the FP risk for Option A as-is); keep the change minimal.
>
> **Tests:** (a) `test_runner.py`: a stream whose ONLY `### Ledger Updates` block is inside a Write `tool_use` content (the plan-57 repro) is now captured into `_all_assistant_text`; the existing bare-text and intermediate-turn cases still work. (b) `test_parser.py`: `parse()` returns `_all_assistant_text`; extraction succeeds when the block is in tool content. (c) `test_bellows.py`: the defense WARN now fires for a tool-content-only-but-unparsed case and for a genuinely-missing case; does NOT fire when ledger populated. Then run the FULL suite (`python3 -m pytest tests/`) to explicit pass/fail and READ THE TAIL. If feasible, reproduce against plan-57's actual step JSON and show `parsed["ledger_updates"]["forward"]` now populates — record in the dev log. Write the dev log to `bellows/knowledge/development/ledger-toolcontent-capture-dev-log-2026-06-14.md`. Use `with open()`; no heredocs. Standard prompt feedback → emit via `### Ledger Updates > #### Prompt Feedback` (emit it as BARE TEXT in your final message — and ALSO this fix makes tool-buried receipts work). **Deposits:**
> - `bellows/knowledge/development/ledger-toolcontent-capture-dev-log-2026-06-14.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the dev log, and the diagnostic. **Verify, each with executed evidence (files into `knowledge/qa/evidence/ledger-toolcontent-capture-2026-06-14/`):** (1) **Full suite** — final 15 lines, zero failures, new-test count matches dev log; `full_suite_tail.txt`. (2) **G1 tool-content capture** — the runner now includes Write/Edit tool content in `_all_assistant_text`; the plan-57-style repro extracts the forward block; if feasible, show `parsed["ledger_updates"]["forward"]` populated from plan-57's real step JSON; `g1_capture.txt`. (3) **G2 WARN propagation** — `_all_assistant_text` is in the parsed dict and the defense WARN fires on heading-present-but-empty-parse; `g2_warn.txt`. (4) **No regression** — bare-text and intermediate-turn extraction (feedback/project_status/forward) all still work; existing ceo_flags/verdict_requested unaffected; `no_regression.txt`. (5) **Scope** — `git diff HEAD~1 --stat` only in-scope files; `scope.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `ledger-toolcontent-capture-2026-06-14`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/ledger-toolcontent-capture-qa-report-2026-06-14.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/ledger-toolcontent-capture-2026-06-14/`; `required_evidence_files`: `[full_suite_tail.txt, g1_capture.txt, g2_warn.txt, no_regression.txt, scope.txt]`. Include the literal stdout of the block. If it prints `FAILED`, halt and report to CEO. Write the QA report (verification table + Rule 20 banner) to `bellows/knowledge/qa/ledger-toolcontent-capture-qa-report-2026-06-14.md`. **Receipt Flags for CEO MUST include:** (1) DAEMON RESTART REQUIRED — do NOT restart until this plan fully closes; (2) RE-CANARY — fresh FORWARD canary after restart must land row #23; (3) this fix hardens ALL THREE channels against tool-buried receipts (not just FORWARD). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/ledger-toolcontent-capture-qa-report-2026-06-14.md`
> - `bellows/knowledge/qa/evidence/ledger-toolcontent-capture-2026-06-14/` (five evidence files per Rule 20 self-check)
