# Bellows — Dashboard Visual Styling: Distinct Categories + Separators
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
CEO request: add styling separation to the Bellows dashboard TUI so it is more readable and each category is visually distinct. Today `dashboard.py::render_screen` (line 163) returns plain text rows drawn with `stdscr.addnstr(i, 0, line, width)` (no curses attributes, zero color — confirmed). Sections are IN-FLIGHT (~200), AWAITING VERDICT (~213), EVENT FEED (~224/229) plus the daemon header and footer keybar. This plan adds stdlib-curses styling (NO new dependencies — consistent with the plan-33 design): bold/colored section headers, full-width separator rules between categories, and state-based emphasis, with graceful fallback on terminals without color. Scope is the TUI (`dashboard.py`) only; the plain-text CLI (`status.py`) is out of scope this plan (it stays plain). NOTE: the running dashboard loads `dashboard.py` at startup — these changes take effect only when the CEO QUITS and relaunches `python dashboard.py` (the `r` key restarts the child daemon, not the dashboard process). The live relaunch is where the CEO judges the look and can request tweaks. Anchors (re-verify by grep): `render_screen` (~163), the draw loop `addnstr` (~394), section builders (~200/213/224).

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then `dashboard.py` (`render_screen`, the draw loop, the curses init in `_main_loop`/`_do_restart`). **Scope is exactly these files: `dashboard.py`, `tests/test_dashboard.py`.**
>
> Implement stdlib-curses styling so each category is visually distinct and the screen is more readable:
> - **Carry attributes through the render:** change `render_screen` to return each row as a `(text, attr)` pair (or equivalent structure) where `attr` is a curses attribute (e.g. `curses.A_BOLD`, a color pair, or `0`); update the draw loop to apply it: `stdscr.addnstr(i, 0, text, width, attr)`. Keep the existing line-count / single-screen budget — separators count toward height; ensure the EVENT FEED still fills remaining space and the footer stays pinned.
> - **Color init:** in the curses setup, call `curses.start_color()` / `use_default_colors()` and define color pairs ONLY if `curses.has_colors()`; when color is unavailable, fall back to monochrome attributes (A_BOLD / A_REVERSE / A_DIM) so the dashboard still renders cleanly on a no-color terminal.
> - **Distinct categories:** style the three section headers (IN-FLIGHT, AWAITING VERDICT, EVENT FEED) BOLD and each a distinct color — e.g. IN-FLIGHT cyan, AWAITING VERDICT yellow (it is the actionable "needs you" section — make it the most prominent; if there are awaiting rows, emphasize them), EVENT FEED dim. The daemon header line: bold, RUNNING in green / STOPPED in red. The footer keybar: bold or reverse so the keys stand out.
> - **Separator rules:** insert a full-width horizontal rule (a line of `─` box-drawing chars sized to `width`, rendered dim) between categories so the boundaries are obvious. Handle minimum-width gracefully.
> - Keep the content (rows, values, `(none)`/`stale?` handling, the type-qualified `executable #N` ids) exactly as-is — this is presentation only.
>
> **Tests:** update/extend `tests/test_dashboard.py` for the new return shape: (a) `render_screen` returns `(text, attr)` rows; (b) section headers carry a bold attr; (c) AWAITING VERDICT emphasis attr applied when rows exist; (d) a separator rule row is present between sections; (e) monochrome fallback path (no color) still returns valid rows; (f) the single-screen line-budget contract still holds for a representative state. Then run the FULL suite (`python3 -m pytest tests/`) to explicit pass/fail and READ THE TAIL. Capture a plain-text representation of the styled layout (text rows + which attr each carries) into the dev log so the structure is reviewable without a live terminal. Write the dev log to `bellows/knowledge/development/dashboard-styling-dev-log-2026-06-14.md`. Use `with open()`; no heredocs. Standard prompt feedback → emit via `### Ledger Updates > #### Prompt Feedback`. **Deposits:**
> - `bellows/knowledge/development/dashboard-styling-dev-log-2026-06-14.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md` and the dev log. **Verify, each with executed evidence (files into `knowledge/qa/evidence/dashboard-styling-2026-06-14/`):** (1) **Full suite** — final 15 lines, zero failures, new-test count matches dev log; `full_suite_tail.txt`. (2) **Attributed rows** — `render_screen` returns `(text, attr)` rows and the draw loop applies `attr`; `attributed_rows.txt`. (3) **Distinct categories** — each section header carries bold + a distinct attr/color; AWAITING VERDICT is emphasized; daemon header green/red by state; `categories.txt`. (4) **Separators** — a full-width rule row appears between categories; `separators.txt`. (5) **No-color fallback** — the monochrome path returns valid rows (simulate `has_colors()` False); `fallback.txt`. (6) **Single-screen budget** — line count still fits the contract with separators included; `budget.txt`. (7) **Content unchanged** — values/ids/`(none)`/`stale?` identical to before (presentation-only); `content_unchanged.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `dashboard-styling-2026-06-14`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/dashboard-styling-qa-report-2026-06-14.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/dashboard-styling-2026-06-14/`; `required_evidence_files`: `[full_suite_tail.txt, attributed_rows.txt, categories.txt, separators.txt, fallback.txt, budget.txt, content_unchanged.txt]`. Include the literal stdout of the block. If it prints `FAILED`, halt and report to CEO. Write the QA report (verification table + Rule 20 banner) to `bellows/knowledge/qa/dashboard-styling-qa-report-2026-06-14.md`. **Receipt Flag for CEO:** the running dashboard shows the new styling only after QUIT + relaunch (`q`, then `python dashboard.py`) — `r` (child-daemon restart) does NOT reload the dashboard's render code; the relaunch is where the CEO judges the look and can request color/layout tweaks. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/dashboard-styling-qa-report-2026-06-14.md`
> - `bellows/knowledge/qa/evidence/dashboard-styling-2026-06-14/` (seven evidence files per Rule 20 self-check)
