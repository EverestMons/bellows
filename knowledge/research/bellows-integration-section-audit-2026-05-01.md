# Bellows Integration Section Audit — v4.29 PLANNER_TEMPLATE.md
**Date:** 2026-05-01 | **Auditor:** Documentation Analyst | **Scope:** Bellows Execution Model (Layer 1 Autonomous Dispatch) section vs. live code

---

## (A) Plan Lifecycle State Machine Accuracy

**Assessment: ACCURATE — no material mismatches.**

The section's state machine diagram:
```
executable-* → in-progress-* → verdict-pending-* → Done/ or halted-*
```

Verified against `bellows.py`:

| Documented behavior | Code evidence |
|---|---|
| Claim via atomic rename (`shutil.move`) | `bellows.py:266-268` — `shutil.move(plan_path, inprogress_path)` |
| Shadow cache write on claim | `bellows.py:270` — `_write_shadow(plan_filename, plan_text)` |
| Gate evaluation post-step | `bellows.py:313` — `gates.check(...)` called after `runner.run_step(...)` returns |
| Pause → verdict-pending rename | `bellows.py:339-341` — `shutil.move(inprogress_path, verdict_pending_path)` |
| `_consume_verdicts` dispatches next step or halts | `bellows.py:650-791` — full verdict consumption loop |
| Continue verdict on terminal step → Done/ | `bellows.py:727-741` — `shutil.move(full_plan_path, done_path)` |
| Stop verdict → halted-* | `bellows.py:754-758` — `shutil.move(full_plan_path, halted_path)` |
| Terminal Done/ under disable-auto-close is Planner-owned | `bellows.py:377-403` — non-auto-close terminal steps post verdict request and return; auto-close path (lines 408-427) only fires when `effective_auto_close` is True |

**Minor note:** The section says "Other watchers or sessions see `in-progress-` prefixed files and skip them." The code confirms this at `bellows.py:506` — `is_runnable_plan()` returns False for `in-progress-` prefixed files.

**DB-based resume path:** The section mentions "shadow cache mechanism" for resume. The actual code at `bellows.py:243-247` uses `_get_last_completed_step(db_path, plan_slug)` for DB-based step recovery, falling back to shadow text for total_steps. This is accurate per the "Phase 3b/3c" reference in the Restart Discipline subsection.

---

## (B) Eight-Gate Enumeration and Classification

**Assessment: ACCURATE — exact match.**

| # | Section name | Code function | Blocking in section | Blocking in code |
|---|---|---|---|---|
| 1 | `receipt_status` | `_gate_receipt_status` (gates.py:86) | Yes | Yes (appends to failures) |
| 2 | `ceo_flags` | `_gate_ceo_flags` (gates.py:92) | Yes | Yes (appends to failures) |
| 3 | `no_errors` | `_gate_no_errors` (gates.py:98) | Yes | Yes (appends to failures) |
| 4 | `no_permission_denials` | `_gate_no_permission_denials` (gates.py:106) | Yes | Yes (appends to failures for blocking denials) |
| 5 | `deposit_exists` | `_gate_deposit_exists` (gates.py:145) | Yes | Yes (appends to failures) |
| 6 | `is_qa_step` | `_gate_is_qa_step` (gates.py:219) | No (Info) | No (returns bool, does not append to failures) |
| 7 | `file_change_audit` | `_gate_file_change_audit` (gates.py:227) | No (Info) | No (returns list, does not append to failures) |
| 8 | `scope_check` | `_gate_scope_check` (gates.py:233) | Yes | Yes (appends to failures) |

**Gate count:** Exactly 8 gates in code. The `check()` function at gates.py:36-83 calls exactly these 8 gates in order.

**Blocking/informational split:** Section says gates 1-5 and 8 blocking, gates 6 and 7 informational. Code confirms: `passed` is computed as `len(failures) == 0` (gates.py:77), and only gates 1-5 and 8 append to the `failures` list.

**READ_CLASS_TOOLS exemption:** The section correctly notes "Read-class tools (Grep, Glob, Read) are exempted" for gate 4. Code confirms at gates.py:20: `READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}` with filtering at gates.py:112.

---

## (C) Verdict Cycle Accuracy

**Assessment: ACCURATE — all fields present, one minor field order difference (non-material).**

**Verdict request fields (section claims vs. code):**

| Section-listed field | Present in `verdict.py:post_verdict_request`? |
|---|---|
| `**Plan:**` | Yes (line 119) |
| `**Project:**` | Yes (line 120) |
| `**Step:**` | Yes (line 121) |
| `**Total Steps:**` | Yes (line 128) |
| `**Pause Reason Code:**` | Yes (line 125) |
| `**Deposit:**` | Yes (line 126, via `extract_primary_deposit()`) |
| `**Gate Result Passed:**` | Yes (line 127) |

**Fields in code NOT mentioned in section:**
- `**Log:**` (line 122) — log path. Minor omission; informational field.
- `**Timestamp:**` (line 123) — ISO timestamp. Minor omission; informational field.
- `**Pause Reason:**` (line 124) — human-readable label (distinct from machine-readable Code). Minor omission.

These three are informational metadata not consumed by the verdict cycle's core logic. Their omission from the section is reasonable for a conceptual overview.

**Request/response/processed flow:**
- Section: "Bellows posts a verdict request file to `bellows/verdicts/pending/`" → Code: `verdict.py:80-81` confirms.
- Section: "verdict to `bellows/verdicts/resolved/verdict-{slug}-step-{N}.md` with content `continue\n{reason}` (or `stop\n{reason}`)" → Code: `verdict.py:142-163` (`check_verdict`) parses exactly this format.
- Section: "renames the resolved verdict file to `processed-*` to prevent re-processing" → Code: `bellows.py:772-773` confirms `processed_path = resolved_dir / f"processed-{fname}"`.

**`_consume_verdicts` behavior:**
- 30-second rescan cycle: Confirmed at `bellows.py:858` (`rescan_interval = 30`) and `_rescan` calls `_consume_verdicts` at line 629.
- Pending request cleanup: Confirmed at `bellows.py:767-769`.
- Stale verdict handling: Code at `bellows.py:775-791` handles the case where a verdict exists but the plan is already in Done/ — marked as stale and moved to processed. Not mentioned in section but is an edge-case handler, not core architecture.

---

## (D) Planner Discipline Cross-References

**Assessment: ACCURATE — all five summaries correctly characterize their rules.**

| Rule | Section summary | Actual rule content | Match? |
|---|---|---|---|
| Rule 22 | "Planner verification of deposited files — the (a)–(e) checks applied to every agent deposit before plan advancement." | Lines 623-645: defines (a) file exists, (b) answers questions, (c) summary matches file, (d) no contradictions, (e) Rule 20 self-check. Applied before advancement. | Yes |
| Rule 23 | "End-of-plan housekeeping ordering — ensures PROJECT_STATUS and feedback updates happen in the correct sequence relative to plan closure." | Lines 647-657: anchored edits, enumerated sub-steps, feedback → commit ordering. | Yes |
| Rule 24 | "Atomic plan deposit — write-to-temp + move pattern for plans targeting Bellows-watched directories." | Lines 659-681: three atomic patterns (temp+move, single write_file, single Desktop Commander write), prohibits multi-call construction in watched dirs. | Yes |
| Rule 25 | "Verdict request polling, pause-reason routing, and terminal Done/ move — the Planner's scan-and-route layer for Bellows-dispatched plans." | Lines 683-722: Planner scans verdicts/pending/, routes on pause reason code, performs Rule 22 verification, handles terminal Done/ move. | Yes |
| Rule 26 | "`**Deposits:**` field convention — declarative deposit enumeration that replaces prose-embedded path scanning." | Lines 724-750: mandatory `**Deposits:**` block in every step, bulleted list of backtick-quoted paths, replaces keyword scanning. | Yes |

All summaries are faithful one-line characterizations. No misrepresentation found.

---

## (E) Architectural Omissions

**Assessment: Minor omissions exist but none are architecturally material enough to confuse a reader.**

### Mentioned in the diagnostic's checklist — findings:

| Item | In section? | Assessment |
|---|---|---|
| Shadow cache (`.bellows-cache/*.pristine`) | Yes — explicitly described in "Claim" paragraph | Fully covered |
| Pushover notification triggers | Partially — section says "CEO is notified via Pushover only on escalation or completion" | The live `notifier.py` has four notification types: `notify_escalation`, `notify_complete`, `notify_failure`, `notify_verdict_request`. The section covers the first two by mention. `notify_verdict_request` (the most commonly triggered in practice) is covered by the verdict cycle description but not called out as a distinct Pushover event. `notify_failure` (exception path) is implicit in "escalation." Minor gap — reader would not be confused. |
| config.json structure | Partially — section mentions "config.json (watched project paths, Pushover credentials, model defaults)" | Actual config has: `watched_projects`, `default_model`, `planner_model`, `pushover.app_key/user_key`, `step_timeout_seconds`, `callback_port`, `tailscale_ip`. The section's parenthetical covers the main three. Omission of `callback_port`, `tailscale_ip`, `step_timeout_seconds` is reasonable for an architectural overview. |
| READ_CLASS_TOOLS exemption (BACKLOG #2) | Yes — Gate 4 row says "Read-class tools (Grep, Glob, Read) are exempted" | Fully covered |
| `--relative -- .` scoping fix (BACKLOG #4) | Yes — Gate 8 row says "Uses `--relative -- .` to scope the diff to the project subtree" | Fully covered |
| DB-based step state recovery (`plan_slug`, `_get_last_completed_step`) | Yes — indirectly via "Phase 3b/3c" in Restart Discipline and the state machine's resume path | The section does not explicitly name `_get_last_completed_step` or the `plan_slug` column, but the resume path is described in the Verdict Consumption paragraph ("dispatches the next step") and the Resume Protocol subsection describes DB-based resume. Architecturally covered. |

### Additional observations (not in checklist):

1. **Parallel group dispatch** — `bellows.py` supports `parallel-N-` prefixed plans with a 5-second settle window (`_pending_groups`, `PlanHandler`). The section does not mention parallel group dispatch mechanics. However, the File Naming Convention subsection in the Plan File Structure section (lines 385-396) documents the `parallel-N-` convention, and the section's "What Bellows Is" paragraph mentions "watches `knowledge/decisions/` directories for new plan files" without distinguishing serial vs. parallel dispatch. This is a minor architectural concept not covered in the Bellows section itself — a reader might not realize Bellows has native parallel dispatch support.

2. **`server.py` (ResponseServer/callback server)** — mentioned in the module list ("server.py (callback server for response collection)") but never described architecturally. The code shows it's passed to `run_plan` but the current `run_plan` function doesn't use it for the core flow (it's a legacy response collection mechanism). Non-material.

3. **Startup orphan cleanup** — `bellows.py:809-840` removes orphaned verdict requests on startup. Not mentioned in section. Operational detail, not architectural concept.

4. **Queue-drain notification** — `_check_queue_drain` sends a "Queue Empty" push when all plans complete. Not mentioned. Operational convenience, not architecture.

5. **`header_says_pause` mechanism** — The `pause_for_verdict` plan header field (`always`, `after_step_1`, `after_qa_step`) is described in the section's Gate Evaluation paragraph: "evaluates the auto-close condition." The actual mechanism is a separate function (`header_says_pause` at bellows.py:195-204) that checks a plan header field. The section mentions "header-specified pause" in the verdict cycle description. Adequately covered.

---

## Closure Recommendation

**The v4.29 Bellows Execution Model section is sufficient to close BACKLOG "2026-04-18: Planner↔Bellows integration protocol underdefined" via hygiene close.**

Rationale:
- All five audit dimensions pass without material discrepancy.
- The state machine, eight gates, verdict cycle, and rule cross-references are accurate against live code.
- The three minor omissions from the verdict request schema (Log, Timestamp, Pause Reason label) are informational metadata, not architectural concepts.
- The parallel-dispatch mechanism is the only architectural concept a reader might miss, but it is documented elsewhere in the template (File Naming Convention) and is a dispatch optimization, not a core lifecycle concept.
- No omission rises to the level of "a reader trying to understand Bellows from this section alone would find an architectural concept in the running code that wasn't mentioned."

**Recommendation: Close the BACKLOG entry. No executable plan needed to amend the section.**
