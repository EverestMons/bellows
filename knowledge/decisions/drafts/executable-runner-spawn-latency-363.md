# Bellows — Runner Pre-Stream Spawn-Latency Instrumentation
**Date:** 2026-08-12 | **Tier:** Low | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite
**cycle_tier:** T1

## Context (Rule 27)
A cold-start analysis of 361 completed `logs/*-step.json` runs established that per-step overhead is NOT the Bellows speed bottleneck: `time_to_request_ms` median 20 ms, `ttft_ms` median 3.5 s, against a median step wall-clock of 367 s (≈99% model inference). BUT those metrics all come from inside the `claude -p` stream-json `result` event — they begin measuring only *after* the CLI subprocess has already booted and emitted its first `system/init` line. The interval from `subprocess.Popen` to the first stdout byte — Node startup + Claude Code harness init + tool registration + prompt-cache load, i.e. the true pre-stream cold-start — is currently UNMEASURED. This plan adds a single durable timing field so that interval becomes visible in every step log, letting a later read quantify it against the ~3.5 s in-stream startup we already have.

The instrumentation is confined to `runner.run_step`. Relevant existing sites (grep/ANCHOR-locate at edit time; line numbers are indicative and MUST be re-verified — halt-and-report on divergence):
- `start_time = time.monotonic()` is stamped immediately before `subprocess.Popen` (runner.py ~L214/217). This is the spawn epoch.
- `last_output_time = time.monotonic()` and the shared reader `_read_stream(stream, buf)` (runner.py ~L248–259) already timestamp the *most recent* output line but never the *first*; `_read_stream` is shared by both the stdout and stderr threads.
- `elapsed = time.monotonic() - start_time` is computed after the reader threads drain (runner.py ~L304).
- The success terminal write is `_write_log(log_path, {...})` (runner.py ~L524), the dominant terminal path for completed steps — 361/367 sampled logs carried a parseable `result` event; the success branch is where the measurable ones land. Timeout / session-limit / error branches deliberately do NOT carry the field (out of scope for this pass).

The new field is derived, not a new clock source: `first_stdout_time − start_time`. Because `start_time` is the pre-Popen stamp and the first stdout byte is the `system/init` event, the delta captures exactly the pre-stream boot. No behavior changes; this is observe-only.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then read `runner.py` `run_step` in full around the anchors named in Context and the existing timing test patterns in `tests/test_runner.py` (`_make_mock_popen`, the `patch("runner.time.monotonic", side_effect=...)` tests). **Scope is exactly these files: `runner.py` and `tests/test_runner.py`.**
> - **(1) Capture the first stdout byte:** add a `first_stdout_time` state variable alongside `last_output_time` (initialize to `None`). In `_read_stream`, set it exactly once, only for the stdout stream (distinguish via `buf is stdout_buf`), on the first appended line, under the existing `lock`. **`_read_stream` currently declares `nonlocal last_output_time` only — add `first_stdout_time` to that `nonlocal` statement, or the assignment binds a dead local and the metric is always `None`.** Do NOT alter `last_output_time`, the timeout logic, or stderr handling. Locate the reader by ANCHOR/grep; zero or multiple matches → halt and report.
> - **(2) Derive and record the metric:** after the reader threads drain (where `elapsed` is computed), compute `spawn_to_first_byte_s = round(first_stdout_time - start_time, 3) if first_stdout_time is not None else None`. Add two keys to the SUCCESS `_write_log` dict (the `"success": True` terminal write): `"spawn_to_first_byte_s": spawn_to_first_byte_s` and `"runner_wall_s": round(elapsed, 1)`. (`runner_wall_s` is the runner-side total wall from pre-`Popen` to drain; it looks adjacent to the result event's in-stream `duration_ms` but is NOT redundant — `runner_wall_s − duration_ms` cross-checks the boot delta, so keep both keys.) These live at the TOP LEVEL of the step-log dict (siblings of `success`/`raw_output`/`parsed`) so the existing aggregation reads them without touching `raw_output`. Do NOT rename or nest any existing key.
>
> **Tests (targeted only — do NOT run the full suite in DEV):** add `test_spawn_to_first_byte_recorded` to `tests/test_runner.py` using `_make_mock_popen(CLEAN_NDJSON)` into a `tmp_path` log, patching `runner.time.monotonic` with the existing counter-style `fake_monotonic` **function** (as in the current timeout tests — NOT a fixed-list `side_effect`, which `StopIteration`s on run_step's many `monotonic()` calls) so `start_time` precedes the first stdout read. Assert the written log dict contains `spawn_to_first_byte_s` as a non-None float `>= 0` and contains `runner_wall_s`. Because reader-thread scheduling makes the exact delta nondeterministic, assert presence + type + non-negativity, NOT an exact value. Run ONLY `python3 -m pytest tests/test_runner.py -q` to explicit pass/fail and READ THE TAIL. Write the dev log to `bellows/knowledge/development/runner-spawn-latency-dev-log-2026-08-12.md`. Use `with open()`; no heredocs. Standard prompt feedback → emit via the `### Ledger Updates > #### Prompt Feedback` channel. **Deposits:**
> - `bellows/knowledge/development/runner-spawn-latency-dev-log-2026-08-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md` and the dev log. **Verify, each with executed evidence (files into `bellows/knowledge/qa/evidence/runner-spawn-latency-2026-08-12/`):** (1) **Full suite** — `python3 -m pytest tests/`, final 15 lines, zero failures, new-test count matches the dev log; `full_suite_tail.txt`. (2) **New test passes in isolation** — `python3 -m pytest tests/test_runner.py::test_spawn_to_first_byte_recorded -q`; `new_test.txt`. (3) **Field is wired at both sites** — grep `runner.py` showing `spawn_to_first_byte_s` appears BOTH where it is derived (`first_stdout_time - start_time`) AND inside the `"success": True` `_write_log` dict, and that `first_stdout_time` is set under lock for the stdout stream only; `wiring.txt`. (4) **No regression to existing timing keys** — grep confirming `last_output_time` and the timeout/inactivity logic are unchanged (the diff touches only the added lines); `no_regression.txt`.
>
> **MANDATORY — Rule 20 self-check (canonical block, the exact template, NOT a paraphrase)** from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (ABSOLUTE path). **All FOUR placeholders — a partial enumeration reads as complete and the block `sys.exit(1)`s on the one you omit:** `plan_slug`: `runner-spawn-latency-2026-08-12`; `qa_report_path`: `<your-tree-abs>/knowledge/qa/runner-spawn-latency-qa-report-2026-08-12.md` (a missing/unwritten report is `CRITICAL: QA report not found`, which makes the passed line below unsatisfiable on a correct run); `evidence_dir` derived from `pwd`, NOT hardcoded; `required_evidence_files`: `[full_suite_tail.txt, new_test.txt, wiring.txt, no_regression.txt]`. Deposit **all four** evidence files BEFORE running the block — it `sys.exit(1)`s on any missing name. **Include the block's literal stdout: the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must both appear byte-exact (em-dash U+2014) — and only on a genuinely clean run.** If it prints `FAILED`, halt and report to CEO. Write the QA report (verification table + Rule 20 banner) to `bellows/knowledge/qa/runner-spawn-latency-qa-report-2026-08-12.md`. **Receipt Flags for CEO MUST include:** (1) instrumentation is observe-only — no dispatch/behavior change; (2) `spawn_to_first_byte_s` + `runner_wall_s` now written on every SUCCESS step log; the pre-stream boot interval is measurable from the next dispatched plan onward; (3) downstream read pending — after ~10–20 real steps accumulate, re-run the cold-start aggregation over the new field to quantify pre-stream boot vs the known ~3.5 s in-stream ttft. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/runner-spawn-latency-qa-report-2026-08-12.md`
> - `bellows/knowledge/qa/evidence/runner-spawn-latency-2026-08-12/` (four evidence files per Rule 20 self-check)

---
---

## Drafting Cycle
**cycle_tier:** T1 | **Walks:** 1 in progress (lens 1 of 5 run; each lens acts on the draft as folded by the previous — sequential cumulation, not a batched fork).

- Weak spots:      **w1 4 folded** — (A) Step-1 item (1) omitted the `nonlocal first_stdout_time` requirement in `_read_stream`; without it the assignment is a dead local and the metric is always `None` — added. (B) Context overclaimed "the branch 361/367 real steps reach"; 361/367 is *result-event-carrying*, not *success-branch-reaching* (unmeasured) — softened to the verified statement + scoped out timeout/error branches. (C) `runner_wall_s` looked redundant with `duration_ms` and could be dropped; added the cross-check rationale. (D) test sentence said "strictly increasing `side_effect`"; a fixed list `StopIteration`s — repinned to the counter-function `fake_monotonic` pattern.
- Destruction:     not yet walked — will confirm the added lines destroy no existing timing key (`last_output_time`, the timeout/inactivity path) and that `first_stdout_time` cannot mis-set for the stderr stream.
- Vulnerabilities: not yet walked — will probe the `None` guard (`first_stdout_time is not None`) and thread-race on the first-line stamp under `lock`.
- Integration:     not yet walked — will confirm the new top-level keys are read by the existing `logs/*-step.json` aggregation without disturbing `raw_output`/`parsed` consumers.
- ACID:            not yet walked — will price the observe-only claim and the test's presence-not-value assertion against reader-thread nondeterminism.

**Closing:** walk 1 open — Weak spots ran (4 folded); Destruction lens is next, not yet dry. One lens per pass, each reading the draft as left by the prior lens.
