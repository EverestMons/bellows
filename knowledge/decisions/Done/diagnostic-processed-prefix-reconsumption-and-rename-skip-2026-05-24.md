# Bellows — `processed-` prefix re-consumption loop & companion rename-skip on final-step gate_failure
**Date:** 2026-05-24 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Two BACKLOG entries from 2026-05-22 describe failures in adjacent regions of the `_consume_verdicts` / verdict-pause code paths:

1. **CRITICAL (P0) — Write-time `processed-` prefix normalization re-consumes already-processed verdicts.** Observed on `executable-stuck-state-color-override-2026-05-22`: a 2-step plan that passed all gates on Step 2 at 18:37 entered an infinite loop instead of closing. Every pause-cycle triggered `[WARN] normalized write-time processed- prefix: processed-verdict-stuck-state-color-override-2026-05-22-step-1.md → verdict-stuck-state-color-override-2026-05-22-step-1.md`, immediately followed by `verdict continue — resuming` and a fresh Step 2 re-run. Step 2 re-ran ≥14 times over ~3 hours, including one 600s inactivity timeout kill at 19:31. Hypothesis from the BACKLOG entry: a Bellows code path (write-event hook, gate evaluation, or step-completion bookkeeping) treats the `processed-` prefix as a write-time artifact to strip, producing a file matching `verdict-<slug>-step-<N>.md`, which the consumer reads as a fresh CEO `continue`.

2. **Companion — Step 2 (final-step) gate_failure pause does NOT rename `in-progress-*` to `verdict-pending-*`.** Observed on `executable-pre-scan-orphan-guard-2026-05-22.md`: Step 2 QA gate_failure surfaced a verdict-request correctly, but the plan filename stayed `in-progress-*` instead of being renamed. Consequence: the verdict response in `resolved/` could not be paired with any `verdict-pending-*` plan, so `_consume_verdicts` no-match-WARN'd every 30s indefinitely. Planner-side manual rename triggered watcher re-dispatch (step-counter loop, separate BACKLOG entry).

**Why investigate together.** Both involve multi-step `pause_for_verdict` flows, the verdict-resolved-side state machine, and the lifecycle of `processed-verdict-*.md` filenames. Item 1 produces phantom continue verdicts that drive Step 2 re-runs. Item 2 produces unconsumable verdicts because the plan-side filename is wrong. They MIGHT share a root cause (e.g., a refactor that introduced both the prefix-normalization-on-write AND the rename-skip on final-step gate_failure). They MIGHT be independent bugs in adjacent code regions. Cheaper to investigate together than to ship a fix for item 1 and discover after the fact that item 2 was caused by the same change.

**Scope:** read-only investigation of `bellows.py`, `gates.py`, `verdict.py`, and any helpers in the consume/pause/rename paths. No fixes, no code changes. Findings deposit goes to `bellows/knowledge/architecture/`. The Planner reads findings and authors a separate executable (or two separate executables) if the root causes differ.

**Reference prior diagnostic:** `bellows/knowledge/decisions/Done/diagnostic-consume-verdicts-drain-2026-05-21.md` already characterized `_consume_verdicts` discovery-scope, slug extraction, and pairing logic up to commit-state on 2026-05-21. Today's diagnostic builds on that — DO NOT re-derive what's already in that file or its findings deposit at `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md`. Cite back to it where relevant. Note: the 2026-05-21 fix (commit `dc0bdd7` per BACKLOG Closed entry "Closed 2026-05-21: `_consume_verdicts` did not drain two valid `resolved/` verdict files...") shipped a pre-scan rename of `processed-verdict-*` → `verdict-*`. That fix is precisely the suspected source of the new loop — verify whether today's CRITICAL symptom is downstream of that fix or independent.

## Two questions to answer

**Q1 (item 1, CRITICAL):** Which code path emits the log line `normalized write-time processed- prefix:`? What triggers it during a Step 2 pause-cycle on a multi-step plan that has already had Step 1's verdict processed? Why is it firing on already-on-disk files (not files newly-written this scan)? Why does it produce a file the verdict consumer reads as a fresh `continue`?

**Q2 (item 2, rename-skip):** In the `run_plan()` final-step gate_failure branch, why does the `in-progress-*` → `verdict-pending-*` rename not occur? Is the rename skipped, deferred, or attempted-and-failed? Does it depend on a teardown call that runs in a different branch? Is daemon-restart state loss involved?

**Q3 (joint):** Do items 1 and 2 share a root cause (e.g., a single refactor or branch-asymmetry in the pause/teardown sequence), or are they independent bugs in adjacent code? If shared, name the shared site. If independent, the fix sequencing matters: which should ship first, and does fixing one mask or worsen the other?

---

## STEP 1 — Characterize both code paths and determine root-cause relationship

**Agent:** Bellows Systems Analyst
**Estimated tokens:** ~30k

### Read order

1. `bellows/knowledge/BACKLOG.md` — the two open entries dated 2026-05-22 (the CRITICAL `processed-` re-consumption entry and the `in-progress-*` rename-skip entry). Read both in full for the reproduction record.
2. `bellows/knowledge/decisions/Done/diagnostic-consume-verdicts-drain-2026-05-21.md` AND its findings deposit `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md`. Read both to anchor on what was characterized 2026-05-21 about `_consume_verdicts` discovery and slug-pairing logic. Do not re-derive those facts; cite them.
3. `bellows/bellows.py` — `_consume_verdicts` in full; `run_plan` in full (especially the gate_failure pause branches at intermediate-step and final-step sites, the rename sites, and any teardown call ordering). Trace every code path that could produce the log line `normalized write-time processed- prefix:` — `git grep "normalized write-time processed- prefix"` if needed to locate it precisely.
4. `bellows/gates.py` — any function called by the gate_failure pause path that might touch verdict files in `resolved/`.
5. `bellows/verdict.py` — any helpers called by `_consume_verdicts` for slug extraction or filename parsing. Especially: the `processed-`-prefix normalization helper (if it lives in `verdict.py` rather than `bellows.py`).
6. `bellows/knowledge/architecture/` — scan for any other prior SA architecture document on verdict consumption, pause-rename lifecycle, or filename conventions. Read any that look relevant in full.
7. Recent reproduction artifacts:
   - The `executable-stuck-state-color-override-2026-05-22.md` plan (currently in `bellows/knowledge/decisions/Done/` based on closeout). Confirm whether it auto-closed or was halted, and reconstruct the Step 1 and Step 2 verdict file states from the BACKLOG entry's narrative + any surviving `bellows/verdicts/resolved/` files matching the slug (including any `_PLANNER_RECALLED_*` prefixed files).
   - The `executable-pre-scan-orphan-guard-2026-05-22.md` plan (in `Done/`; see BACKLOG Closed entry). Confirm its lifecycle history from any surviving verdict files matching the slug.
8. `bellows/logs/terminal/` — if present, the relevant 2026-05-22 daily log files for each plan. Search for the timestamps cited in the BACKLOG entries (18:37–20:23 for the stuck-state-color-override loop; 09:13 onward for the pre-scan-orphan-guard rename-skip).

Do NOT read source files beyond what's listed above unless they're called by the implicated code paths and you need to follow the call chain to understand them.

### Investigation questions

Answer each in the findings file. For each answer, cite the specific `bellows.py` / `gates.py` / `verdict.py` line + the exact code snippet (no paraphrasing).

**Section A — Locate the `normalized write-time processed- prefix:` log line (item 1)**

1. Which file and which function emits this log line? Cite the line. What is the function's calling context — what does it scan, what does it act on?
2. Is this the pre-scan rename helper introduced in commit `dc0bdd7` (the 2026-05-21 `_consume_verdicts` drain fix)? Or a different code path? If `dc0bdd7`, has it been modified since? If different, when was it introduced (git log timeline)?
3. Under what condition does the function rename `processed-verdict-*.md` → `verdict-*.md`? Cite the predicate. Is there ANY guard checking whether the file was already-on-disk vs newly-written-this-scan? If guard exists, cite it. If absent, confirm absence.
4. After the rename, what is the resulting file's filename + state? Does it match the canonical `verdict-<slug>-step-<N>.md` shape that the main `_consume_verdicts` filter loop accepts as a fresh verdict?

**Section B — Loop trace (item 1)**

5. Walk the full sequence from "Step 2 gate-PASS at 18:37" through the first re-run trigger. Specifically: when does the pre-scan rename fire on the `processed-verdict-stuck-state-color-override-2026-05-22-step-1.md` file (which has been on disk since Step 1 completed earlier)? What does `_consume_verdicts` do with the renamed `verdict-stuck-state-color-override-2026-05-22-step-1.md` file on the next scan cycle?
6. Does the consumer match this newly-renamed Step-1 verdict against the (now Step-2-pending) plan, treating it as a Step-2 continue? OR does it treat the Step-1 verdict as a Step-1 verdict (which would be a no-op or stale-detect)? If the former, cite the slug-matching + step-N comparison code that allows a Step-1 verdict to advance a Step-2-pending plan.
7. Is there ANY code path that would terminate the loop without external intervention? (Idempotency check, retry limit, terminal-state check, etc.)

**Section C — Trace the final-step rename-skip (item 2)**

8. In `run_plan()`, identify every site that renames `in-progress-*` → `verdict-pending-*`. Cite each line. For each, identify the conditional branch that gates it (which Pause Reason Codes, which step-N position, success vs gate_failure path).
9. For the final-step gate_failure pause path specifically (Step N == total_steps AND gate_failure code), trace what happens. Does it call the same rename site as intermediate-step gate_failure, a different one, or none? If "none," cite the missing call. If "different," compare the two.
10. Is `_teardown_worktree` called before, after, or instead of the rename on the final-step gate_failure path? Could a teardown-failure short-circuit the rename? Cite the order.
11. Could a daemon restart between pause-time and rename-time drop the rename? Specifically: is the rename a single atomic op in the parent process, or split across an in-memory "pending" marker that gets lost on restart? Cite the relevant lines.

**Section D — Verify against the 2026-05-22 reproductions**

12. For the stuck-state-color-override loop, reconstruct what the verdict files in `resolved/` looked like at the moment the loop fired. Compare to your Section A/B trace. Does your trace explain ALL 14+ iterations, or only the first?
13. For the pre-scan-orphan-guard rename-skip, reconstruct the file state when the verdict response was written by the Planner to `resolved/`. Does your Section C trace explain why the rename was missing? Is daemon-restart-during-pause involved, or was the rename never attempted by the on-pause branch?

**Section E — Joint root cause analysis**

14. Do items 1 and 2 share a code site, a common dependency (e.g., both depend on a same helper or branch predicate), or a common ancestor commit? If they share, name it. If they don't share, state that explicitly with the two distinct code regions named.
15. **Fix sequencing question:** if independent, does fixing item 1 (the loop) BEFORE item 2 (the rename-skip) leave any reproductions latent? Conversely, does fixing item 2 first inadvertently mask item 1's loop trigger? Reason from the code paths, not from speculation.

**Section F — Resolution options (read-only proposals, no implementation)**

16. For item 1, list 2–3 concrete fix shapes (e.g., "guard the pre-scan rename on file-modified-this-scan," "remove the pre-scan rename entirely and rely on the 2026-05-21 governance rule that prohibits `processed-` prefix at write time," "add idempotency check in `_consume_verdicts` that detects 'verdict matches a step already in terminal state' and no-ops"). For each, give a 1–2 line LOC estimate and call out behavioral risk.
17. For item 2, list 2–3 concrete fix shapes (e.g., "add the rename call to the final-step gate_failure branch," "unify intermediate and final-step gate_failure paths through a single helper," "make rename idempotent and call it from both pause-init and teardown to be safe"). Same LOC + risk format.
18. If items 1 and 2 share a cause, propose a unified fix. If they don't, recommend a sequencing order with reasoning.

**Section G — Test coverage**

19. Are there pytest tests today that exercise the pre-scan rename helper on already-on-disk `processed-verdict-*` files (item 1's trigger)? Cite by test name + path.
20. Are there pytest tests for the final-step gate_failure → rename path (item 2)? Cite by test name + path. Note gaps.

### Out of scope

- Do not propose or implement fixes. This diagnostic is characterize-only.
- Do not modify `bellows.py`, `gates.py`, `verdict.py`, or any test file.
- Do not touch any verdict files in `bellows/verdicts/resolved/` (including `_PLANNER_RECALLED_*` files). Read-only.
- Do not investigate the step-counter loop after precondition-failure verdict (separate BACKLOG entry, separate diagnostic later).
- Do not investigate the daemon-restart recovery shape (separate BACKLOG entry 2026-05-23, scoped for a separate diagnostic).

### Deliverables

**Deposits:**
- `bellows/knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md`

The findings file MUST include:
- A "Section A — Pre-scan rename trigger" section answering questions 1–4 with line citations and code snippets
- A "Section B — Loop mechanism" section answering questions 5–7 with the full trace
- A "Section C — Final-step rename-skip mechanism" section answering questions 8–11
- A "Section D — Reproduction verification" section answering questions 12–13
- A "Section E — Joint root cause analysis" section answering questions 14–15
- A "Section F — Resolution options" section answering questions 16–18
- A "Section G — Test coverage" section answering questions 19–20
- The standard SA Output Receipt block at the end

### STOP

Stop after Step 1. Do not author an executable. The Planner will read the findings, verify Rule 22, and decide on fix scope + sequencing.
