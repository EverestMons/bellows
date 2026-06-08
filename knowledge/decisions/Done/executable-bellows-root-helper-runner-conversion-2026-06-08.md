# Bellows — resolve_bellows_root() helper + runner.py conversion (Plan A, proof-only ship)
**Date:** 2026-06-08 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV creates a standalone `bellows_root.py` (`resolve_bellows_root()` — config.json marker walk-up with fallback), converts `runner.py`'s `BELLOWS_ROOT` to use it, and closes the runner `LOGS_DIR` worktree-write gap with a `tests/conftest.py` autouse fixture — plus helper unit tests and a negative worktree-resolution test. QA is code-level ONLY — full-suite + diff/contract verification + a check that no log file lands in canonical `logs/` during the suite run; no live daemon run, no plan deposited into a watched `decisions/`.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY, then STOPS and waits for CEO verdict before Step 2. Bootstrap: `Read the plan at bellows/knowledge/decisions/executable-bellows-root-helper-runner-conversion-2026-06-08.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## CEO Context

**Plan A from the 2026-06-08 reachability audit** (`knowledge/research/bellows-root-worktree-reachability-audit-2026-06-08.md`). The audit proved exactly ONE of the four latent `BELLOWS_ROOT = Path(__file__).parent` instances is worktree-reachable: **runner.py**, via 13 unpatched `test_runner.py` functions that write `LOGS_DIR` while `__file__` resolves inside `.bellows-worktrees/<wt>/`. The other three (bellows.py, planner.py, verdict.py) are proven LATENT-UNREACHABLE (all reads patched / never dereferenced / conftest-isolated). CEO decision: convert ONLY the proven instance now; converting the latent three requires its own targeted reachability proof, not a proactive ride-along. This plan does NOT touch bellows.py, planner.py, or verdict.py.

**The fix:** a standalone `resolve_bellows_root()` helper modeled on the `resolve_governance_root()` marker-walk-up shipped in `decisions.py` this session. Marker = `config.json` (Planner-verified untracked + gitignored, present at canonical root, absent from worktrees), with a fallback to the legacy `Path(__file__).parent` when no marker is found anywhere (CI/fresh-clone parity). `runner.py`'s `BELLOWS_ROOT` is rebound to the helper; `LOGS_DIR` derivation is unchanged.

**Load-bearing interaction — fixture must land WITH the conversion.** Today an unpatched `LOGS_DIR` write from a worktree test lands in the transient worktree `logs/` (torn down, harmless). Once the helper is active, that same unpatched write resolves to CANONICAL `logs/` — a real pollution of the live tree. The conftest autouse fixture (`isolate_runner_logs_dir`, mirroring the existing `isolate_verdicts_dir`) is therefore not optional hygiene — it closes a gap the conversion would otherwise WIDEN. Both land in the same DEV step; there is no intermediate state where the helper runs without the fixture. QA explicitly verifies no `*-step.json` appears in canonical `logs/` after the suite run.

**Circular-import constraint.** `bellows.py` imports `runner` and `runner.py` does `from bellows import _log` — a cycle already tolerated. `bellows_root.py` MUST import only `pathlib` (and optionally `logging`); it must NOT import bellows, runner, planner, or verdict, or it introduces a new cycle.

**No daemon restart required for correctness.** The daemon runs from the canonical checkout, where both the old code and the helper resolve to the identical canonical root — daemon behavior is unchanged. The running process keeps the old `runner.py` in memory until the next restart, but since resolution is identical there, nothing is owed. (Restart only to load the new module, cosmetic.)

**Why QA is code-level only.** The contract is fully provable by reading the diff and running the suite (including the negative worktree-resolution test that fails under the old `Path(__file__).parent` and passes under the helper). No daemon start, no live deposit, no filesystem event a running daemon would observe.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) the `resolve_governance_root()` helper in `decisions.py` (locate by string `def resolve_governance_root`) — the reference implementation to mirror; (3) the `BELLOWS_ROOT`/`LOGS_DIR` declarations in `runner.py` and the `isolate_verdicts_dir` fixture in `tests/conftest.py` — located via the Pre-edit verification queries; do NOT trust line numbers, locate by symbol/string.
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** `runner.py` declares `BELLOWS_ROOT = Path(__file__).parent.resolve()` at module level with `LOGS_DIR = BELLOWS_ROOT / "logs"` immediately after. **Query:** `grep -n "BELLOWS_ROOT\|LOGS_DIR" runner.py`. **Expected:** the two module-level lines present; all other `LOGS_DIR` uses are inside functions.
> 2. **Claim:** `bellows_root.py` does NOT already exist. **Query:** `ls bellows_root.py 2>&1`. **Expected:** no such file.
> 3. **Claim:** `config.json` is the canonical-only marker — present at root, gitignored, untracked. **Query:** `git check-ignore config.json && git ls-files --cached config.json && ls config.json`. **Expected:** `config.json` echoed by check-ignore; EMPTY output from ls-files (untracked); file present on disk.
> 4. **Claim:** `tests/conftest.py` has an `isolate_verdicts_dir` autouse fixture (the pattern to mirror) and does NOT already isolate `runner.LOGS_DIR`. **Query:** `grep -n "autouse\|isolate_\|LOGS_DIR\|VERDICTS_DIR" tests/conftest.py`. **Expected:** `isolate_verdicts_dir` autouse fixture present; no existing runner LOGS_DIR isolation.
> 5. **Claim:** the circular-import context — `runner.py` does `from bellows import _log` and `bellows.py` imports `runner`. **Query:** `grep -n "^from bellows import\|^import runner\|from runner import" runner.py bellows.py`. **Expected:** confirms the existing cycle; this is WHY `bellows_root.py` must be standalone.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-bellows-root-helper-2026-06-08-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task 1 — Create `bellows_root.py`** (new module at bellows root, sibling to `runner.py`). Imports ONLY `pathlib` (and `logging` if used for the fallback warning). It MUST NOT import bellows, runner, planner, or verdict. Contents EXACTLY:
> ```python
> """Worktree-safe resolution of the canonical bellows root.
>
> Under worktree execution, __file__ resolves inside .bellows-worktrees/<wt>/,
> so the legacy `Path(__file__).parent` yields the worktree dir, not canonical
> bellows. This walks up to the nearest ancestor containing config.json (the
> gitignored, canonical-only operational config), which is absent from worktrees.
> Standalone (pathlib only) to avoid the bellows<->runner import cycle.
> """
> from pathlib import Path
>
>
> def resolve_bellows_root(_start=None) -> Path:
>     """Return the canonical bellows root (ancestor containing config.json).
>
>     Falls back to the start dir (legacy `Path(__file__).parent` behavior) when
>     no config.json is found in any ancestor — preserves current behavior in
>     CI / fresh-clone environments without a config.json.
>
>     `_start` is for testing only; production calls resolve from this file.
>     """
>     start = (_start or Path(__file__).resolve().parent).resolve()
>     current = start
>     while True:
>         if (current / "config.json").exists():
>             return current
>         parent = current.parent
>         if parent == current:  # filesystem root reached
>             return start
>         current = parent
> ```
>
> **Task 2 — Convert `runner.py`.** Replace the `BELLOWS_ROOT = Path(__file__).parent.resolve()` line with a helper call; leave `LOGS_DIR = BELLOWS_ROOT / "logs"` and every downstream `LOGS_DIR` use unchanged. Add the import near the other top-level imports:
> ```python
> from bellows_root import resolve_bellows_root
> ```
> and replace the declaration line with EXACTLY:
> ```python
> BELLOWS_ROOT = resolve_bellows_root()
> ```
> Do NOT change `LOGS_DIR`, `_write_log()`, `run_step()`, or anything else in `runner.py`. If `Path` becomes unused after the change, leave the import (harmless) — do not chase unrelated cleanups.
>
> **Task 3 — Close the runner LOGS_DIR worktree-write gap.** In `tests/conftest.py`, add an autouse fixture mirroring `isolate_verdicts_dir` EXACTLY in style:
> ```python
> @pytest.fixture(autouse=True)
> def isolate_runner_logs_dir(monkeypatch, tmp_path):
>     import runner
>     monkeypatch.setattr(runner, "LOGS_DIR", tmp_path / "logs")
> ```
> This is REQUIRED, not optional: post-conversion, an unpatched `LOGS_DIR` write from a worktree-run test resolves to CANONICAL `logs/` (not the transient worktree). The fixture closes that. Place it adjacent to `isolate_verdicts_dir`.

> **Task 4 — Helper tests** in a new `tests/test_bellows_root.py`. Use `tmp_path` to build directory structures; do NOT depend on the real filesystem layout. Cover:
> - `test_resolves_to_dir_with_config` — `_start` is a dir containing `config.json`; assert the helper returns that dir.
> - `test_walks_up_to_config` — build `<tmp>/canonical/config.json` and `<tmp>/canonical/.bellows-worktrees/wt1/`; call `resolve_bellows_root(_start=<tmp>/canonical/.bellows-worktrees/wt1)`; assert it returns `<tmp>/canonical` (the walk-up). This is the NEGATIVE worktree-resolution test — it FAILS under the legacy `Path(__file__).parent` (which would yield the `wt1` dir) and PASSES under the helper. Add a comment marking it as such.
> - `test_falls_back_when_no_config` — `_start` is a tmp dir tree with NO `config.json` anywhere up to `tmp_path`; assert the helper returns `_start` (legacy fallback). (Note: the walk stops at filesystem root; scope the assertion to the absence within the tmp tree — if a real `config.json` exists above tmp it won't be hit because tmp_path is isolated.)
>
> **Pre-edit baseline:** run `python3 -m pytest tests/ 2>&1 | tail -15` and record pass/fail counts (note known carry-over failures) BEFORE editing. Re-run AFTER editing; the delta must be ONLY the new `test_bellows_root.py` tests passing — ZERO new failures, all existing tests still green. In particular confirm the previously-unpatched `test_runner.py` functions still pass WITH the new autouse fixture active.
>
> **Canonical-logs check (DEV self-verify):** after the full post-edit suite run, confirm NO new `*-step.json` file was created in the canonical `logs/` directory: `git status --porcelain logs/` should show nothing new from the test run. Record the result in the dev log.
>
> **Commit** (do NOT push — Planner handles session-wrap): stage `bellows_root.py`, `runner.py`, `tests/conftest.py`, `tests/test_bellows_root.py`, the dev log, and `knowledge/research/agent-prompt-feedback.md`; message `fix(bellows): worktree-safe resolve_bellows_root() + convert runner.py BELLOWS_ROOT; isolate runner LOGS_DIR in tests`.
>
> **Dev log** → `knowledge/development/bellows-root-helper-runner-conversion-2026-06-08.md`: the new `bellows_root.py` verbatim, the `runner.py` diff, the conftest fixture, confirmation that `LOGS_DIR`/`_write_log`/`run_step` are byte-unchanged, the import-cycle safety check (bellows_root imports pathlib only), pre-edit verification results, both pytest runs (before/after counts), and the canonical-logs check result. Include an **Output Receipt** with a "Files Created or Modified" list.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/bellows_root.py` (new)
> - `bellows/runner.py` (modified)
> - `bellows/tests/conftest.py` (modified)
> - `bellows/tests/test_bellows_root.py` (new)
> - `bellows/knowledge/development/bellows-root-helper-runner-conversion-2026-06-08.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
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
> **Before starting, read `knowledge/development/bellows-root-helper-runner-conversion-2026-06-08.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (PASS/FAIL) | Evidence |` (use the literal words PASS / FAIL in the Status column — not glyphs). Specifically:
>
> 1. **Helper standalone** — `bellows_root.py` exists, defines `resolve_bellows_root`, and imports ONLY `pathlib` (and optionally `logging`); NO import of bellows/runner/planner/verdict. Capture `head -40 bellows_root.py` and a grep for imports to `evidence/helper_imports.txt`.
> 2. **Marker walk-up contract** — the helper returns the dir containing `config.json`, walking up, with a fallback to the start dir. Capture the function body to `evidence/helper_body.txt`.
> 3. **runner.py converted** — `BELLOWS_ROOT = resolve_bellows_root()` with `from bellows_root import resolve_bellows_root` imported; `LOGS_DIR = BELLOWS_ROOT / "logs"` unchanged. Capture to `evidence/runner_diff.txt` via `git --no-pager diff -- runner.py`.
> 4. **runner.py otherwise byte-unchanged** — the diff is confined to the import + the `BELLOWS_ROOT` line; `_write_log()`, `run_step()`, `LOGS_DIR` untouched. Confirm from the same `evidence/runner_diff.txt`; state explicitly in the table.
> 5. **conftest fixture added** — `isolate_runner_logs_dir` autouse fixture present in `tests/conftest.py`, patching `runner.LOGS_DIR` to `tmp_path / "logs"`. Capture to `evidence/conftest_fixture.txt`.
> 6. **Helper + negative tests exist** — grep `tests/test_bellows_root.py` for `test_resolves_to_dir_with_config`, `test_walks_up_to_config`, `test_falls_back_when_no_config` → all three present. Capture to `evidence/new_tests_grep.txt`.
> 7. **Latent three untouched** — confirm `git --no-pager diff --name-only` does NOT include `bellows.py`, `planner.py`, or `verdict.py` (Plan A converts ONLY runner.py). Capture to `evidence/scope_untouched.txt`.
> 8. **Dev log complete** — exists with the helper verbatim, runner diff, conftest fixture, byte-unchanged confirmation, import-cycle check, pre/post pytest runs, canonical-logs check. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any FAIL blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) the three new `test_bellows_root.py` tests appear and PASS — in particular `test_walks_up_to_config` PASS (the negative worktree-resolution proof); (b) the previously-unpatched `test_runner.py` functions still PASS with the autouse fixture active; (c) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (d) total pass count == DEV's reported post-edit number.
>
> **Negative-test integrity check.** Open `tests/test_bellows_root.py` and confirm `test_walks_up_to_config` genuinely asserts the walk-up returns the config-bearing ancestor (not the `.bellows-worktrees/wt1` start dir) — i.e. it would FAIL against the legacy `Path(__file__).parent`. Capture the test body + your one-line judgment to `evidence/negative_test_integrity.txt`. A test that passes trivially (e.g. asserts nothing about the worktree case) is a FAIL of this check.
>
> **Canonical-logs pollution check.** After the suite run, confirm no test wrote into canonical `logs/`: `git status --porcelain logs/` shows nothing new, and no fresh `*-step.json` appears in `logs/`. Capture to `evidence/canonical_logs_clean.txt`. This is the load-bearing verification that the conversion + fixture closed (not widened) the worktree-write gap.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-bellows-root-helper-runner-conversion-2026-06-08`; `qa_report_path` = `bellows/knowledge/qa/bellows-root-helper-runner-conversion-2026-06-08.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/bellows-root-helper-runner-conversion-2026-06-08/`; `required_evidence_files` = `["helper_imports.txt", "helper_body.txt", "runner_diff.txt", "conftest_fixture.txt", "new_tests_grep.txt", "scope_untouched.txt", "dev_log_check.txt", "pytest_full.txt", "negative_test_integrity.txt", "canonical_logs_clean.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-08 entry under Completed for "resolve_bellows_root() helper + runner.py BELLOWS_ROOT conversion (Plan A, the one proven-reachable instance; runner LOGS_DIR test-isolation gap closed)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **Flags for CEO (put in the QA deposit):** (1) the three latent instances (bellows.py, planner.py, verdict.py) remain unconverted by CEO decision — converting them requires its own targeted reachability diagnostic, not a proactive ride-along; (2) BACKLOG entry "Added 2026-06-06" should be updated to reflect runner.py SHIPPED + the proof-only disposition of the latent three; (3) no daemon restart required for correctness (canonical resolution identical old vs new).
>
> **Commit:** stage `knowledge/qa/bellows-root-helper-runner-conversion-2026-06-08.md`, the `knowledge/qa/evidence/bellows-root-helper-runner-conversion-2026-06-08/` evidence files, and `PROJECT_STATUS.md` with message `qa(bellows): resolve_bellows_root + runner conversion verified — walk-up proven, canonical logs clean, zero new regressions`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA bellows-root helper`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/bellows-root-helper-runner-conversion-2026-06-08.md`
> - `bellows/knowledge/qa/evidence/bellows-root-helper-runner-conversion-2026-06-08/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
