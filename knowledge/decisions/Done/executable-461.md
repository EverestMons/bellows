# bellows — mid-session log hygiene + 5 GB disk floor default
**Date:** 2026-08-19 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

Closes the known gap in `diagnostic-log-retention-disk-guard-2026-08-12` (drafts/) and the memory note `bellows-log-accumulation-fills-disk`: disk hygiene IS built, but **clearing is startup-only**, so a daemon up for days never prunes. Measured live 2026-08-19 — the running daemon (dashboard.py + bellows.py) had **18h22m uptime** with neither `_prune_old_logs` nor `_rotate_logs` having fired since startup. Currently benign (`logs/` = 2.5 MB), so this closes a latent gap, not a live fire.

Two startup-only callees:
- `_rotate_logs()` — `bellows.py:276`, called once at `:2710` (startup). Terminal logs >14d, step JSON >30d, `planner-consultation.jsonl` >10 MB.
- `_prune_old_logs(config)` — `bellows.py:304`, called once at `:2632` (startup). `log_retention_days` default 30.
- `_disk_preflight(config)` — `:334`, the only *per-claim* hygiene gate (`:843`), but it only **checks**, never clears.

**Fix (CEO-selected, 2026-08-19):**
1. **Timer in the main loop** — add a periodic hygiene tick to `start()`'s run loop (alongside the existing `rescan`/`heartbeat` timers), gated by a `HYGIENE_INTERVAL` of 6 h, that calls `_prune_old_logs` + `_rotate_logs`. Off the claim hot path; runs regardless of claim traffic. Extracted into a testable helper `_maybe_run_hygiene(config, last_hygiene, now, interval)` because the `while True` loop itself cannot be unit-tested.
2. **Raise the disk floor to 5 GB** — memory notes one agent run's scratch can exceed the 2 GB margin. **The live `config.json` is gitignored and does NOT set `disk_min_free_gb`, so it runs on the code default.** The clean, tracked, tested way to raise the floor is therefore to bump the **code default** (`:340`, `config.get("disk_min_free_gb", 2)` → `5`) and `config.example.json:15` (`2` → `5`) — NOT to edit the invisible local file. This immediately raises the live floor at next daemon restart with zero gitignored-file edits.

Single production file changed (`bellows.py`) plus `config.example.json` (doc) and the existing test file.

**Concurrency note (walk 2, deferred edge):** running `_rotate_logs` mid-session — unlike startup — can overlap active daemon writes (e.g. renaming `planner-consultation.jsonl` at its >10 MB threshold while a consultation is being appended). Both callees are filesystem-atomic (`os.remove`/`os.rename`); on POSIX an open fd keeps writing to the renamed inode, so no data is lost. Terminal/step logs deleted mid-session are always >14/>30 days old, never the current session's. Concurrent-append hardening for the consultation rotation is a pre-existing property, out of scope here and deferred.

## Drafting Cycle
**Tier:** T1 — triggers fired: T-1 (blast radius: the change lives in the daemon's core run loop, which must never crash), T-7 (authored from diag-log-retention-disk-guard per Rule 27), T-8 (novel helper). NOT T-6 (engine code, not doctrine/gates). Additive change (new helper + one call site + a default constant bump), not a clone — self-escalation to a cold panel not indicated; full-regression QA is the mitigation.

**Walk 0 (context pin):**
- `bellows.py` sha `de6aa0ce38d5` (2755 lines). Edit regions: the hygiene functions block (`_rotate_logs` `:276`, `_prune_old_logs` `:304`, `_disk_preflight` `:334`); the `min_free_gb` default at `:340`; the run loop in `start()` (`rescan_interval`/`last_rescan`/`last_heartbeat` init at `:2654–2657`, the `while True` body `:2659–2683`).
- `config.example.json` sha `116b9069` — line 15 `"disk_min_free_gb": 2,`. (Line 14 `"log_retention_days": 30,` stays.)
- `tests/test_log_hygiene.py` sha `888bfd92` (190 lines) — the EXISTING hygiene test file. It already covers `_prune_old_logs` (4 tests) and `_disk_preflight` (6 tests) and has `test_config_defaults_disk_min_free_gb` asserting the old default 2. **EXTEND this file; do not recreate.**
- `config.json` is gitignored and does NOT set `disk_min_free_gb`/`log_retention_days` (verified via `python3 -c` load) → the code default is the effective live value. This is why the fix targets the default, not the local file.
- Clone/lineage reference: `drafts/diagnostic-log-retention-disk-guard-2026-08-12.md` (the diagnostic that designed the current guard). This plan does not undo it — it adds the missing recurring call.

**Direction verdict (after walk 1):** **PROCEED** — the two-change design is sound; walk-1 folds sharpen safety/implementation, none invalidate the approach.
**Walks:** 3 (bar MET — walk 3 instruction-class dry, record-only, no restructuring fold).
- Weak spots:         w1 1 folded (F1 tick-placement, record); w2 dry (F9 placement confirmed); w3 dry.
- Destruction:        w1 1 folded (**F4 helper try/except — INSTRUCTION, critical: `_rotate_logs` has no internal guard + run loop un-wrapped → a mid-session raise would crash the daemon**; guard test `test_hygiene_swallows_callee_error` added); w2 1 folded (F10 concurrent-rotation note, record); w3 dry.
- Vulnerabilities:    w1 dry (F5 integration-test dual-callee note; F11 `_log` patch-target confirmed); w2 dry; w3 dry.
- Integration-record: w1 record notes (F6 Priority-2 intentional; F7 provenance; F12 `full_suite.txt` named per qa_test_result lesson); w2 dry; w3 dry.
- ACID:               w1 dry (no DB/transactional surface); w2 dry; w3 dry.
**Conflicts:** none.
**Instruction trend:** w1 1 (F4) → w2 0 → w3 0 — converged.
**Prediction correction (mid-cycle):** predicted id 460 was consumed by an in-window dispatch (`cycle_check.py format census`); mint is now **461** per `id_sequence`. Draft uses slug-based naming + `[<id>]` placeholders, so no hardcoded-id edit was needed (`read-id-sequence-at-deposit`).
**§5 Conformance:** `plan_lint` run on the draft at shape-stability (walk 3) → **0 FAIL**. (c) QA banner pair PASSES; `full_suite.txt` named in the Step-2 Deposits block. Benign WARNs only: o1 `test_log_hygiene.txt` (QA-produced at runtime), o2 bare-relative deposits (accepted for in-repo self-plans — executable-457 identical), pin-check "ambiguous" (valid 12-char prefix of the real `bellows.py` blob `de6aa0ce38d5`). The two Drafting-Cycle WARNs (missing lenses / no Closing) are cleared by this block.
**Closing:** walk 3 returned record-only (zero instruction-class, no restructuring fold) — the confirming-pass convergence signature (§2). §5 conformance clean (0 FAIL); closing re-read run (this block), dry; cycle CLOSED. Deposit exactly once (pending CEO go).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **Identity:** You are the Bellows Developer. Read the hygiene-function block in `bellows.py` (`_rotate_logs`, `_prune_old_logs`, `_disk_preflight` — roughly lines 276–360), the `start()` run loop (search for `rescan_interval = 30`), and `tests/test_log_hygiene.py` in full before editing. Read the Context above; the design is authoritative.
>
> **Task:** In `bellows.py`, add mid-session log hygiene on a timer and raise the disk-floor default 2 → 5 GB. Update `config.example.json`. Extend `tests/test_log_hygiene.py`. One production file (`bellows.py`), one doc file, one test file.
>
> **Change 1 — disk-floor default 2 → 5.** In `_disk_preflight`, change the single line `min_free_gb = config.get("disk_min_free_gb", 2)` to use `5` as the default. Do NOT touch the gitignored `config.json` (it does not set this key). In `config.example.json`, change `"disk_min_free_gb": 2,` to `"disk_min_free_gb": 5,` (line 15; leave `log_retention_days` at 30).
>
> **Change 2 — mid-session hygiene helper.** Add a new module-level function immediately after `_disk_preflight` (before `class WorktreeCreationError`):
> ```python
> def _maybe_run_hygiene(config: dict, last_hygiene: float, now: float,
>                        interval: float) -> float:
>     """Periodic mid-session log hygiene, driven from the run loop.
>
>     The startup calls to _prune_old_logs/_rotate_logs are not enough for a
>     daemon up for days; this fires every `interval` seconds. Returns the
>     timestamp to store as the next last_hygiene (advanced only when the
>     interval has elapsed — advanced even on failure so a persistent error
>     does not retry every loop tick).
>
>     MUST NOT raise: it runs from the `while True` run loop, which has no
>     try/except around its body — a propagating error would crash the daemon.
>     _prune_old_logs guards itself internally, but _rotate_logs does NOT
>     (bare os.remove/os.rename), so this wraps both in a fail-safe.
>     """
>     if now - last_hygiene < interval:
>         return last_hygiene
>     try:
>         _prune_old_logs(config)
>         _rotate_logs()
>     except Exception as e:
>         _log("WARN", f"mid-session hygiene failed (skipping until next interval): {e}")
>     return now
> ```
>
> **Change 3 — wire the timer into the run loop.** In `start()`, next to `rescan_interval = 30` (and the `last_rescan`/`last_heartbeat` inits), add:
> ```python
>         HYGIENE_INTERVAL = 6 * 3600  # 6h — mid-session log hygiene; the startup
>                                      # call alone leaves a multi-day daemon unpruned
>         last_hygiene = time.time()
> ```
> Then add one line at the END of the `while True:` loop body — same indentation as the `if time.time() - last_rescan ...` and `if time.time() - last_heartbeat ...` guards (i.e. one level under `while`, after the heartbeat block closes and before the loop repeats):
> ```python
>                 last_hygiene = _maybe_run_hygiene(self.config, last_hygiene, time.time(), HYGIENE_INTERVAL)
> ```
> Initializing `last_hygiene` to `time.time()` at loop entry means the first mid-session tick fires 6 h AFTER startup — correct, since startup (`:2632`/`:2710`) already ran both. Match the surrounding indentation exactly (assert `python3 -c "import ast; ast.parse(open('bellows.py').read())"` parses).
>
> **Change 4 — extend `tests/test_log_hygiene.py` (read it first; do not duplicate existing tests).**
> - **UPDATE `test_config_defaults_disk_min_free_gb`** — it asserts the default is 2; the default is now 5. Change the assertion to `config.get("disk_min_free_gb", 5) == 5`. (Leave `test_config_defaults_log_retention_days` at 30, unchanged.)
> - **ADD `test_hygiene_skips_before_interval`** — with `now - last_hygiene < interval`, `_maybe_run_hygiene` returns `last_hygiene` unchanged and calls NEITHER callee. Patch `bellows._prune_old_logs` and `bellows._rotate_logs` with MagicMocks; assert `call_count == 0` on both and that the return equals the input timestamp.
> - **ADD `test_hygiene_runs_after_interval`** — with `now - last_hygiene >= interval`, it returns `now` and calls each callee exactly once (patched MagicMocks, `call_count == 1`).
> - **ADD `test_hygiene_tick_prunes_old_log`** (integration — proves the wiring reaches the real prune) — build a tmp `logs/` with one 31-day-old `.json` and one fresh `.json`; `patch.object(bellows, "BELLOWS_ROOT", tmp_path)` and `patch.object(bellows, "_log")`; call `_maybe_run_hygiene({"log_retention_days": 30}, last_hygiene=0.0, now=interval+1, interval=interval)`; assert the old file is gone and the fresh one survives. (Mirrors `test_prune_deletes_old_json_only`. Note both real callees run here; either may delete the 31-day file — the assertion holds regardless.)
> - **ADD `test_hygiene_swallows_callee_error`** (guards the never-crash contract) — patch `bellows._prune_old_logs` to raise `RuntimeError("boom")` and `bellows._log` to a MagicMock; call `_maybe_run_hygiene({}, last_hygiene=0.0, now=interval+1, interval=interval)`. Assert it does NOT propagate, returns `now` (interval advanced so no retry-storm), and logged a WARN. This is the test for the F4 fold — without the helper's try/except a bare `_rotate_logs`/`_prune_old_logs` error would reach the daemon's un-guarded `while True` and crash it.
>
> **Targeted run + commit:** `python3 -m pytest tests/test_log_hygiene.py -q 2>&1 | cat` — all pass. Commit `feat(bellows): mid-session log-hygiene timer + 5GB disk-floor default [<id>]`. Deposit dev log `knowledge/development/bellows-midsession-log-hygiene-2026-08-19.md` (the startup-only gap, the helper-extraction rationale, the **never-crash try/except fold — `_rotate_logs` has no internal guard and the run loop is un-wrapped, so the helper must be fail-safe**, the gitignored-config-default reasoning, the 5 test outcomes, the ast-parse check). End with an Output Receipt recording **Status AND the DEV commit sha** (QA check-3 reads it).
>
> **Deposits:**
> - `bellows.py`
> - `config.example.json`
> - `tests/test_log_hygiene.py`
> - `knowledge/development/bellows-midsession-log-hygiene-2026-08-19.md`

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> **Identity:** You are the Bellows QA Analyst. Read the Step 1 dev log; if its Output Receipt is not Complete, stop and report.
>
> **(1) Hygiene test file passes + covers the new behavior.** `python3 -m pytest tests/test_log_hygiene.py -v 2>&1 | cat` → evidence file `knowledge/qa/evidence/executable-bellows-midsession-log-hygiene-2026-08-19/test_log_hygiene.txt`. Confirm the four new tests (`test_hygiene_skips_before_interval`, `test_hygiene_runs_after_interval`, `test_hygiene_tick_prunes_old_log`, `test_hygiene_swallows_callee_error`) are present and pass, and that `test_config_defaults_disk_min_free_gb` now asserts 5.
>
> **(2) Full suite — Rule 21.** `python3 -m pytest tests/ -q -rf 2>&1 | cat` → evidence file `.../full_suite.txt`. Extract FAILED node-ids via `grep -F 'FAILED ' <out> | awk '{print $2}'`; assert the set is empty (the bellows suite baseline is green — any failure is a regression). Record the raw tail + the node-id set.
>
> **(3) No unintended production change (scope) + syntax valid.** Read the DEV commit sha from the Step-1 dev log Output Receipt, then `git --no-pager show --name-only --format= <DEV_COMMIT>` → assert only `bellows.py`, `config.example.json`, `tests/test_log_hygiene.py`, and `knowledge/` paths appear (and NOT `config.json`). Also run `python3 -c "import ast; ast.parse(open('bellows.py').read())"` → exit 0. Evidence file `.../scope.txt` (both outputs).
>
> **(4) QA report** to `knowledge/qa/2026-08-19-bellows-midsession-log-hygiene-qa.md` with a `| Check | Expected | Status | Evidence |` table (rows 1–3). Do NOT mark a ❌ row ✅; hedging keywords auto-fail.
>
> **(5) Rule 20 self-check** — run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with `plan_slug: executable-bellows-midsession-log-hygiene-2026-08-19`, the qa report path, the evidence dir, and `required_evidence_files: ["test_log_hygiene.txt", "full_suite.txt", "scope.txt"]`. The block prints the banner `Rule 20 — QA Self-Check Results` and, on success, a line beginning `PASSED — SELF-CHECK PASSED` (both verbatim, em-dashes — the gate byte-matches); include the literal stdout under a heading containing "verification". If it prints `FAILED — SELF-CHECK FAILED`, halt.
>
> **Deposits:**
> - `knowledge/qa/2026-08-19-bellows-midsession-log-hygiene-qa.md`
> - `knowledge/qa/evidence/executable-bellows-midsession-log-hygiene-2026-08-19/`
> - `knowledge/qa/evidence/executable-bellows-midsession-log-hygiene-2026-08-19/full_suite.txt`
