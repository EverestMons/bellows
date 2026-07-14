# Diagnostic: Bellows rate-limit `exit 1` no-park — detect + park a 5-hour-cap `claude -p` exit-1 that never emits a graceful 429 session-limit result

**Type:** Diagnostic
**Project:** bellows
**Depends on:** the 2026-07-14 live diagnosis (invoice-pulse plans 181-QA + 182 died to the org 5-hour cap); memory `bellows-rate-limit-exit1-no-park`
**Created:** 2026-07-14
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 20

---

## Context — the gap (root cause already traced live)

On 2026-07-14, two dispatched steps (invoice-pulse plan 181 Step 2 QA + plan 182 diagnostic) hit the org **5-hour usage cap** and **died** — but instead of Bellows PARKING + auto-resuming at reset (its designed behavior via `parked_steps` + `_resume_parked`), both surfaced as **`gate_failure`** (receipt Blocked, `ceo_flags: claude -p exit code 1`). They had to be recovered by hand (manual `parked_steps` insert → parked-resume).

**Root cause (confirmed in the code):** `runner._check_session_limit` (`runner.py:74`) only returns "parkable" when the FINAL result event has `is_error AND api_error_status == 429` (line 80) AND the result string contains "session limit"/"usage limit" (line 84). But a 5-hour-cap death frequently manifests as a **hard `claude -p` exit 1** (`error: "non_zero_exit_1"`, `cost=None`, ~5000-char truncated stream ending mid-plan-read) — there is NO graceful 429 result. The cap is signalled ONLY by a **streamed** event mid-run:
`{"type":"rate_limit_event","rate_limit_info":{"rateLimitType":"five_hour","overageStatus":"rejected","resetsAt":1784053800,...}}`
(the two 2026-07-14 cases: one `overageStatus:"rejected"` hard-cap, one `status:"allowed_warning", utilization:0.93`). `_check_session_limit` inspects the final result event, never the stream, so it misses this class entirely → no park → false gate_failure, and the step's uncommitted work is at risk.

**This is READ-ONLY scoping for the fix — no code change; findings only.** Deposit to `knowledge/research/bellows-rate-limit-exit1-park-scoping-2026-07-14.md`.

---

## Investigation targets

1. **Data availability at the park-decision point (THE load-bearing unknown).** `bellows.py:~374` calls `_check_session_limit(raw)`. On a non-zero exit-1, what is `raw`/`parsed` — is the final `{"type":"result"}` event present at all, and does the runner retain the **streamed** JSONL events (incl. `rate_limit_event`) anywhere accessible **in-process** at the park decision, or only flushed to the log file's `raw_output`? Map exactly where the claude -p stream is read/parsed and what survives to the park check. **If the stream events are NOT retained in-process, the fix must also capture them** (the diagnostic must say where).

2. **The exit-1 code path.** Where does `run_step`/`run_plan` handle a non-zero `claude -p` exit? What `parsed`/`success=False` object is constructed (the failed logs showed `parsed` with `session_id` but `is_error/stop_reason/result_text = None`)? Confirm whether a `rate_limit_event` is RELIABLY present in the stream before an exit-1 — both 2026-07-14 cases had it — and flag the residual risk if some rate-limit deaths lack it (fall back to gate_failure, never a silent hang).

3. **`resetsAt` extraction.** The `rate_limit_event` carries the reset as an **epoch int** (`resetsAt: 1784053800`) — simpler than `_parse_session_reset`'s wall-clock-string regex. Confirm the exact field name/shape (`resetsAt` vs `resets_at`), and recommend a small `_reset_epoch_from_rate_limit_event()` helper (with a `now + 5h` fallback, mirroring the existing one).

4. **Park hook + false-positive guard (correctness-critical).** Recommend broadening the park path: on an exit-1 (`non_zero_exit`), scan the streamed events for a `rate_limit_event` with `rateLimitType == "five_hour"` and a cap-hit status (`overageStatus == "rejected"`, or `status` in a blocked/rejected set, or `utilization >= ~0.95`). **Guards (both mandatory):**
   - (a) **No committable progress** — mirror the existing `num_turns>1 / total_cost>0 / output_tokens>0` guard (`runner.py:87-92`). A step that exited 1 AFTER doing work + depositing (e.g. plan 182 this session: 23KB findings complete, rule_22 PASS) must NOT be parked — it is a benign gate failure to **continue-with-reasoning**, not a re-run.
   - (b) **A genuine non-rate-limit exit-1 (real crash) must NOT be parked** — parking it would strand the plan forever waiting for a reset that resolves nothing. Park ONLY when the `rate_limit_event` cap signal is actually present.

5. **Idempotency + resume correctness.** Confirm that once parked with `resume_step=N`, `_resume_parked` re-dispatches ONLY step N cleanly with prior DEV commits preserved (verified by hand 2026-07-14 on plan 181 → step 2). Ensure the new exit-1 park path writes the identical `parked_steps` row shape (`plan_slug, plan_path, project, resume_step, resets_at_epoch, parked_at`) via `record_park`.

6. **Test strategy.** A synthetic step result matrix: (i) exit-1 + stream with a `five_hour`/`rejected` `rate_limit_event` + zero progress → **parkable**, correct `resets_at_epoch`; (ii) exit-1, NO `rate_limit_event` → **NOT parkable** (gate_failure); (iii) exit-1 WITH `rate_limit_event` but WITH progress → **NOT parkable** (benign continue); (iv) graceful 429 "session limit" result → **still parkable** (no regression to the existing path).

---

## Deliverable

`knowledge/research/bellows-rate-limit-exit1-park-scoping-2026-07-14.md` — the exit-1 data-flow map (esp. target 1's in-process availability answer), the detection + dual-guard recommendation, the `resetsAt`-from-event helper, and the target-6 test matrix. After it returns, the Planner authors the (Small) executable that broadens the park detection.
