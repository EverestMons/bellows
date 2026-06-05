# Bellows — scope_check Directory-Mention Authorization (2026-05-28 FP, ship)
**Date:** 2026-06-04 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV adds ONE directory-mention authorization clause to `_gate_scope_check` in `gates.py` (a depth-guarded, trailing-slash ancestor-directory check) plus 4 regression tests in `tests/test_gates.py`. QA is code-level ONLY — full-suite run + diff/clause verification; no live daemon run, no plan deposited into a watched `decisions/`.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY, then STOPS and waits for CEO verdict before Step 2. Bootstrap: `Read the plan at bellows/knowledge/decisions/executable-scope-check-dir-mention-2026-06-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## CEO Context

**Closes the 2026-05-28 `scope_check` directory-mention false positive — directory-mention half ONLY (CEO scope decision this session).** The sibling 2026-05-29 blueprint-delegation FP is deliberately NOT in this cut: its fix requires following a blueprint reference and parsing its file list (regex-fragility), a separate higher-risk shape left for a later cut.

**Confirmed root cause (direct code read, no diagnostic needed).** `_gate_scope_check` accepts a changed file only if (1) its basename is in `SCOPE_ALLOWLIST`, (2) its basename starts with a `SCOPE_ALLOWLIST_PREFIXES` entry, (3) the full path `fpath` is a substring of the step text, or (4) the bare `basename` is a substring of the step text. A Deposits-block mention of a parent *directory* (e.g. `.../evidence/<slug>/`) satisfies none of these for a child file: the directory string is in the step text, but the directory+basename (the file path) is not, and the bare basename is not named. So child files written under a named deposit directory get flagged out-of-scope, forcing a manual Rule 22 override on every QA step that produces multi-file evidence in a named directory. Hypothesis in the BACKLOG ("appears to require per-filename mention") confirmed verbatim against current `gates.py`.

**Fix: one depth-guarded trailing-slash clause (CEO specificity decision this session).** After the existing four clauses and before `out_of_scope.append(fpath)`, accept the file if an ANCESTOR directory **of its own path** — derived from `fpath` via `os.path.dirname`, written with a trailing slash, and at least 2 path segments deep (`>= 1` slash) — appears as a substring in the step text. The depth guard prevents a shallow single-segment mention (e.g. `web/`) from blanket-authorizing everything beneath it. Ancestors are computed from the file path itself, so only a genuine parent of the changed file can match — the clause cannot be tricked into authorizing a file whose own parents are unmentioned. This is the clean, low-risk cut: it does not parse the Deposits block separately, does not follow references, and leaves every existing clause and the gate's negative-path teeth intact.

**No self-trip.** This plan FIXES `scope_check`, and the running daemon evaluates this plan's own steps under the PRE-edit `gates.py` (the fix activates only after a daemon restart). To avoid the very FP this plan fixes tripping its own QA step, the QA prompt names EVERY evidence-file basename in the Rule 20 `required_evidence_files` list and the capture instructions — so each evidence file is in-scope under clause (4) `basename in step_text` of the OLD gate. The new directory-mention behavior is verified purely by the 4 unit tests, never by the plan's own execution. DEV deposits (`gates.py`, `tests/test_gates.py`, the named dev-log path, allowlisted `agent-prompt-feedback.md`) are all in-scope under old logic.

**Daemon restart required to activate** — the fix is in `gates.py`, which the running daemon loaded at startup. Keep local `main` CLEAN at the pause so this plan's own worktree teardown succeeds.

**Why QA is code-level only.** The clause is fully provable by unit tests against `gates.check(...)` with crafted `plan_text` + `files_changed`, mirroring the existing `test_scope_check_*` cluster. No daemon start, no live deposit, no filesystem event a running daemon would observe.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) the `_gate_scope_check` function in `gates.py` and the `test_scope_check_*` cluster in `tests/test_gates.py`, located via the Pre-edit verification queries — do NOT trust line numbers, locate by symbol/string.
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** `_gate_scope_check` loops over `files_changed` with four in-scope clauses ending in `if fpath in step_text or basename in step_text: continue`, then `out_of_scope.append(fpath)`. **Query:** `grep -n "def _gate_scope_check\|if fpath in step_text or basename in step_text\|out_of_scope.append(fpath)" gates.py` then read the full loop body. **Expected:** the substring clause `if fpath in step_text or basename in step_text:` is present immediately before `out_of_scope.append(fpath)`; `step_text` comes from `_extract_step_text(plan_text, step_number)`.
> 2. **Claim:** `os` is imported at module level (the clause uses `os.path.dirname`; `os.path.basename` is already used in the loop). **Query:** `grep -n "^import os" gates.py`. **Expected:** present.
> 3. **Claim:** the existing scope_check tests use `gates.check(_clean_parsed(), <PLAN_TEXT>, <step>, "/tmp", files_changed=[...])` and assert on `result["failures"]` entries with `f["gate"] == "scope_check"`. **Query:** `grep -n "def test_scope_check" tests/test_gates.py` and read `test_scope_check_passes_when_files_in_plan`, `test_scope_check_fails_when_file_not_in_plan`, `test_scope_check_allowlist`, `test_scope_check_prefix_allowlist_does_not_suppress_real_violations`. **Expected:** all four present; they build/reuse a plan_text containing a `## STEP 1` section and pass `files_changed`.
> 4. **Claim:** `_extract_step_text(plan_text, step_number)` returns the step's section text (the thing the clause must search). **Query:** `grep -n "def _extract_step_text" gates.py` and read its body. **Expected:** present; returns the step section string.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-scope-check-dir-mention-2026-06-04-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — insert ONE directory-mention authorization clause; change nothing else in the loop.**
>
> In `_gate_scope_check`, inside the `for fpath in files_changed:` loop, insert the following clause IMMEDIATELY BEFORE the final `out_of_scope.append(fpath)` line (i.e. after the existing `if fpath in step_text or basename in step_text: continue`). Match the existing indentation exactly:
> ```
>         # Directory-mention authorization (BACKLOG 2026-05-28 scope_check FP):
>         # accept a changed file when an ANCESTOR directory of its OWN path —
>         # written with a trailing slash and at least 2 path segments deep
>         # (>= 1 slash) — appears in the step text. Covers Deposits blocks /
>         # step prose that name a deposit directory (e.g. an evidence dir) but
>         # reference its child files only collectively. The depth guard stops a
>         # shallow single-segment mention (e.g. "web/") from blanket-authorizing
>         # everything beneath it. Ancestors are derived from fpath itself, so
>         # only a genuine parent of the changed file can match.
>         parent = os.path.dirname(fpath)
>         authorized_by_dir = False
>         while parent:
>             if parent.count("/") >= 1 and (parent + "/") in step_text:
>                 authorized_by_dir = True
>                 break
>             parent = os.path.dirname(parent)
>         if authorized_by_dir:
>             continue
> ```
> Do NOT modify the four existing clauses, the allowlist constants, the failure-append, or the evidence string. The clause is purely additive: it can only MOVE a file from out-of-scope to in-scope, never the reverse.
>
> **Regression tests** in `tests/test_gates.py` — add adjacent to the existing `test_scope_check_*` cluster, mirroring its `gates.check(...)` style. Each builds a minimal `plan_text` with a `## STEP 1` section whose body contains the relevant directory mention:
> - `test_scope_check_accepts_child_file_under_trailing_slash_dir` — step body names a deep dir WITH trailing slash, e.g. ``> Deposit evidence to `knowledge/qa/evidence/foo-2026-06-04/`.``; `files_changed=["knowledge/qa/evidence/foo-2026-06-04/check-a.txt"]` (basename `check-a.txt` NOT in step body). Assert NO `scope_check` failure.
> - `test_scope_check_accepts_child_file_under_dir_placeholder_pattern` — step body uses the `<dir>/<placeholder>` form, e.g. ``... at `knowledge/qa/evidence/foo-2026-06-04/<check-name>.txt` ...``; `files_changed=["knowledge/qa/evidence/foo-2026-06-04/check-b.txt"]`. Assert NO `scope_check` failure (the `/` before the placeholder supplies the trailing slash).
> - `test_scope_check_depth_guard_rejects_shallow_dir_mention` — step body mentions a SINGLE-segment dir with trailing slash, e.g. ``> Touch files under `web/`.``; `files_changed=["web/unmentioned_file.py"]` (basename not named). Assert a `scope_check` FAILURE IS present (depth guard: parent `web` has 0 slashes → not authorized). This test protects the gate's teeth — it MUST fail the file.
> - `test_scope_check_dir_mention_does_not_authorize_unmentioned_sibling_dir` — step body names dir `knowledge/qa/evidence/foo-2026-06-04/` but the changed file lives under a DIFFERENT unmentioned deep dir; `files_changed=["knowledge/qa/evidence/bar-2026-06-04/other.txt"]`. Assert a `scope_check` FAILURE IS present (the file's own ancestors are not in the step text).
> Confirm the four EXISTING scope_check tests still pass unchanged (parity), especially `test_scope_check_fails_when_file_not_in_plan` and `test_scope_check_prefix_allowlist_does_not_suppress_real_violations`.
>
> **Pre-edit baseline:** run `python3 -m pytest tests/ 2>&1 | tail -15` and record pass/fail counts (note the known carry-over failures) BEFORE editing. Re-run AFTER editing; the only delta must be the 4 new tests passing — ZERO new failures, all existing scope_check tests still green.
>
> **Commit** (do NOT push — Planner handles session-wrap): stage `gates.py`, `tests/test_gates.py`, the dev log, and `knowledge/research/agent-prompt-feedback.md`; message `fix(bellows): scope_check honors trailing-slash directory mentions (depth-guarded) — 2026-05-28 FP`.
>
> **Dev log** → `knowledge/development/scope-check-dir-mention-2026-06-04.md`: the inserted clause verbatim, confirmation the four existing clauses + constants + failure-append are byte-unchanged, the depth-guard rationale, pre-edit verification results, both pytest runs (before/after counts). Include an **Output Receipt** with a "Files Created or Modified" list.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/scope-check-dir-mention-2026-06-04.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/gates.py` (modified)
> - `bellows/tests/test_gates.py` (modified)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this step and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Scope note — code-level ONLY.** Do NOT start the daemon, do NOT deposit any plan into a watched `decisions/` directory, do NOT simulate a live dispatch. Verify by reading the code and running the suite. Nothing in this step should produce a filesystem event a running daemon would observe.
>
> **Before starting, read `knowledge/development/scope-check-dir-mention-2026-06-04.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (PASS/FAIL) | Evidence |` (use the literal words PASS / FAIL in the Status column — not glyphs). Specifically:
>
> 1. **Clause present and correct** — `_gate_scope_check` contains the directory-mention clause: `parent = os.path.dirname(fpath)`, an `authorized_by_dir` flag, a `while parent:` ancestor walk with the predicate `parent.count("/") >= 1 and (parent + "/") in step_text`, `parent = os.path.dirname(parent)` decrement, and `if authorized_by_dir: continue` — placed AFTER the `if fpath in step_text or basename in step_text:` clause and BEFORE `out_of_scope.append(fpath)`. Capture the full clause to `evidence/clause_body.txt`.
> 2. **Depth guard correct** — the predicate is `parent.count("/") >= 1` (rejects single-segment dirs). Capture the predicate line to `evidence/depth_guard.txt`.
> 3. **Existing clauses byte-unchanged** — the four pre-existing in-scope clauses (`SCOPE_ALLOWLIST`, `SCOPE_ALLOWLIST_PREFIXES`, `fpath in step_text or basename in step_text`), the allowlist constants, and the `out_of_scope.append` / failure-append / evidence string are unchanged. Capture the surrounding loop region to `evidence/clause_context.txt`.
> 4. **Diff scope** — `git --no-pager diff -- gates.py` shows changes confined to the single inserted clause; nothing else in `gates.py` changed. Capture to `evidence/diff_scope.txt`.
> 5. **Four new tests exist** — grep `tests/test_gates.py` for `test_scope_check_accepts_child_file_under_trailing_slash_dir`, `test_scope_check_accepts_child_file_under_dir_placeholder_pattern`, `test_scope_check_depth_guard_rejects_shallow_dir_mention`, `test_scope_check_dir_mention_does_not_authorize_unmentioned_sibling_dir` → all four present. Capture to `evidence/new_tests_grep.txt`.
> 6. **Existing scope_check tests intact** — `test_scope_check_passes_when_files_in_plan`, `test_scope_check_fails_when_file_not_in_plan`, `test_scope_check_allowlist`, `test_scope_check_prefix_allowlist_does_not_suppress_real_violations` all still present and passing. Capture to `evidence/existing_tests.txt`.
> 7. **Dev log complete** — exists with the clause verbatim, byte-unchanged confirmation, depth-guard rationale, pre-edit verification, both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any FAIL blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) all four new tests appear in verbose output and PASS — in particular the two NEGATIVE tests (`depth_guard_rejects_shallow_dir_mention`, `dir_mention_does_not_authorize_unmentioned_sibling_dir`) PASS, proving the gate still flags genuinely out-of-scope files; (b) the four existing scope_check tests still PASS; (c) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (d) total pass count == DEV's reported post-edit number.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-scope-check-dir-mention-2026-06-04`; `qa_report_path` = `bellows/knowledge/qa/scope-check-dir-mention-2026-06-04.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/`; `required_evidence_files` = `["clause_body.txt", "depth_guard.txt", "clause_context.txt", "diff_scope.txt", "new_tests_grep.txt", "existing_tests.txt", "dev_log_check.txt", "pytest_full.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-04 entry under Completed for "scope_check directory-mention authorization (2026-05-28 FP)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the scope_check directory-mention clause. The running daemon evaluated this plan under the pre-edit gates.py; the fix activates on the next gate evaluation after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus<->Sonnet A/B."
>
> **Commit:** stage `knowledge/qa/scope-check-dir-mention-2026-06-04.md`, the `knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/` evidence files, and `PROJECT_STATUS.md` with message `qa(bellows): scope_check dir-mention verified — depth-guarded clause, teeth preserved, zero new regressions`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA scope-check-dir-mention`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/scope-check-dir-mention-2026-06-04.md`
> - `bellows/knowledge/qa/evidence/scope-check-dir-mention-2026-06-04/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
