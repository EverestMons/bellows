# Step-State Persistence Map — Diagnostic Findings

**Date:** 2026-04-28 | **Diagnostic:** BACKLOG #5 Phase 1 | **Agent:** Bellows Systems Analyst

---

## 1. Executive Summary

When a CEO manually renames a `verdict-pending-*` file back to `executable-*` to resume a plan that previously completed step N (of T total), Bellows dispatches Step 1 from scratch. The root cause is a split in the resume path: the automated verdict consumer (`_consume_verdicts()` at `bellows.py:614`) correctly passes `resume_step=step_number+1` when processing a resolved verdict, but the manual-rename path bypasses `_consume_verdicts()` entirely — the watcher detects a fresh `executable-*` file, calls `handle_new_plan(path)` with no `resume_step` argument, and `run_plan()` defaults `current_step` to 1. No DB lookup, filename parse, or shadow-cache consultation ever intervenes to recover the completed-step count. The `runs` table in `bellows.db` records per-step dispatch history but is write-only — Bellows never queries it. The shortest fix is a DB query in `run_plan()` that checks `MAX(step)` for the plan slug before defaulting to step 1, but this carries design risks enumerated in Q6.

---

## 2. Q1 — Re-Claim Flow

### Scenario (a): Fresh `executable-*` file appears

1. **Detection:** `PlanHandler._handle()` (`bellows.py:497`) receives the path. `is_runnable_plan()` (`bellows.py:469–472`) returns `True` for filenames matching `^(parallel-\d+-)?(executable|diagnostic)-.*\.md$` that don't start with `in-progress-`, `verdict-pending-`, or `halted-`.
2. **Dispatch:** `_handle()` calls `self.orchestrator.handle_new_plan(path)` (`bellows.py:525`) with no `resume_step`.
3. **Thread:** `handle_new_plan()` (`bellows.py:578`) spawns a thread calling `_run_tracked(path)` (`bellows.py:547`), which calls `run_plan(path, config, response_server, resume_step=None)` (`bellows.py:551`).
4. **Claim:** In `run_plan()` (`bellows.py:190`):
   - Reads plan text (`line 198`)
   - Checks shadow cache: `shadow_text = _read_shadow(plan_filename)` (`line 215`)
   - Counts steps from metadata text: `total_steps = extract_total_steps(metadata_text)` (`line 222`)
   - Since filename doesn't start with `in-progress-` (`line 231`), renames to `in-progress-*` (`line 232`) and writes shadow (`line 235`)
5. **Step 1 dispatch:** `bootstrap_prompt` is set to "Execute Step 1 ONLY" (`line 257`) because `resume_step is None`. `current_step = 1` (`line 266`).
6. **File state:** `executable-*` → `in-progress-*` → (after step completion and gate pause) → `verdict-pending-*`.

### Scenario (b): `verdict-pending-*` renamed back to `executable-*` (manual CEO action)

1. **Detection:** Same as (a) — `is_runnable_plan("executable-*")` returns `True`. The watcher/rescan has no way to distinguish a "fresh" executable from a "re-instated" one.
2. **Dispatch:** `handle_new_plan(path)` called with **no `resume_step`** (`bellows.py:525`).
3. **Shadow cache:** `_shadow_path()` (`bellows.py:94–102`) strips lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`) but NOT `executable-` or `diagnostic-`. So `_read_shadow("executable-foo.md")` looks for `.bellows-cache/executable-foo.md.pristine` — which exists from the original claim. Shadow text IS found.
4. **Step dispatch:** `resume_step is None` → `bootstrap_prompt` dispatches Step 1 (`line 257`). `current_step = 1` (`line 266`).
5. **THIS IS THE BUG.** No state lookup occurs. The file enters `run_plan()` identically to a never-before-seen plan.

### Scenario (c): Orphaned `in-progress-*` file (daemon crash mid-step)

1. **Detection:** `is_runnable_plan()` returns `False` for `in-progress-*` (`line 470`).
2. **Result:** File is never picked up. Stays orphaned until manual intervention.
3. **No recovery mechanism exists.** The startup scan (`bellows.py:803–809`) only processes files matching `is_runnable_plan()`.

---

## 3. Q2 — bellows.db Schema

### Schema

```sql
CREATE TABLE runs (
    id INTEGER PRIMARY KEY,
    plan_path TEXT,
    project TEXT,
    session_id TEXT,
    step INTEGER,
    status TEXT,
    cost_usd REAL,
    started_at TEXT,
    completed_at TEXT,
    timestamp TEXT,
    cost REAL
);
```

Single table, 473 rows. No other tables.

### Sample rows (most recent)

| id | plan_path (truncated) | step | status | cost |
|---|---|---|---|---|
| 473 | ...in-progress-executable-deposits-block-regex-blank-line-2026-04-28.md | 2 | VerdictPending | 0.865 |
| 472 | ...in-progress-executable-deposits-block-regex-blank-line-2026-04-28.md | 2 | Complete | 0.865 |
| 471 | ...in-progress-executable-deposits-block-regex-blank-line-2026-04-28.md | 1 | Complete | 0.383 |

### Step-state assessment

**(i) Per-plan step-state table:** No. There is no table that records "plan X has completed through step N."

**(ii) What IS recorded:** The `runs` table is an append-only dispatch log. Each row records one `runner.run_step()` invocation. Two rows are typically written per step: one for the step completion (`status=Complete`) and one for the subsequent gate pause (`status=VerdictPending`). The `step` column records which step number was dispatched. The `plan_path` column contains the full filesystem path including lifecycle prefix at time of recording.

**(iii) Write-only:** `record_run()` (`bellows.py:140–167`) is called at lines 269, 307, 327, and 365 — always `INSERT`. No `SELECT` query on this table exists anywhere in the codebase. Bellows never reads from the DB to determine step state.

---

## 4. Q3 — `extract_total_steps` and Step Counting

### Function (`bellows.py:86–91`)

```python
def extract_total_steps(plan_text: str) -> int:
    case_insensitive_count = len(re.findall(
        r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    case_sensitive_count = len(re.findall(
        r"^## STEP\s+\d+", plan_text, re.MULTILINE))
    if case_insensitive_count > 0 and case_sensitive_count == 0:
        print(f"Bellows: ⚠️  WARNING: plan has step headers but case ...")
    return case_insensitive_count
```

**(i) Input:** Full plan text string (`plan_text`). In `run_plan()`, the input is `metadata_text` which is either the shadow cache content or the live file content (`lines 216–219`).

**(ii) Derivation:** Always from parsing the current plan content. Never from prior dispatch state or the database. Purely structural — counts `## STEP N` headers.

**(iii) Usage:** Stored as `total_steps` (`line 222`). Used as upper bound in:
- `while not is_final_step(current_step, total_steps)` (`line 284`) — controls the step loop
- `is_final_step(step, total_steps)` (`line 170`) — `return step >= total_steps`
- Passed to `verdict.post_verdict_request(..., total_steps=total_steps, ...)` (`lines 299, 358`) for inclusion in verdict request metadata
- In `_consume_verdicts()` (`line 688`): `if step_number >= total_steps_c` — determines if continue verdict should go to Done or dispatch next step

---

## 5. Q4 — Verdict Consumer Interaction

### `_consume_verdicts()` (`bellows.py:614–749`)

**Step number source:** Parsed from the verdict filename at `line 626`:
```python
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
plan_slug = match.group(1)
step_number = int(match.group(2))
```

The step number `N` originates from the verdict filename pattern `verdict-{slug}-step-{N}.md`. This filename is created by `verdict.check_verdict()` (`verdict.py:142–146`) which looks for files in `verdicts/resolved/`. The CEO creates (or the Planner deposits) the verdict file with the step number matching the pending verdict request filename `verdict-request-{slug}-step-{N}.md`.

**On `continue` verdict for non-final step (`lines 702–709`):**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason)
inprogress_name = f"in-progress-{original_name}"
inprogress_path = os.path.join(decisions_path, inprogress_name)
shutil.move(full_plan_path, inprogress_path)
print(f"Bellows: verdict continue — resuming {original_name}")
# Dispatch next step
self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```

**Key finding:** The verdict consumer passes `resume_step=step_number + 1` to `handle_new_plan()`. This flows through to `run_plan()` which then:
- Sets `bootstrap_prompt` to "Execute Step {resume_step}" (`line 255`)
- Sets `current_step = resume_step` (`line 266`)

**The verdict consumer path works correctly.** Step number is preserved through the verdict filename → `_consume_verdicts()` parse → `handle_new_plan(resume_step=N+1)` → `run_plan(resume_step=N+1)` chain.

**On `continue` verdict for final step (`lines 688–701`):** Moves plan to `Done/`, deletes shadow, cleans up verdicts. No re-dispatch.

**On non-continue verdict (`lines 710–719`):** Renames to `halted-*`, deletes shadow, cleans up verdicts.

---

## 6. Q5 — The Gap

### What happens today

When the CEO renames `verdict-pending-foo.md` → `executable-foo.md` (after step N completed), Bellows:

1. Watcher/rescan detects `executable-foo.md` via `is_runnable_plan()` → `True`
2. `handle_new_plan(path)` called — **no `resume_step`**
3. `run_plan()` enters with `resume_step=None`
4. `current_step = resume_step if resume_step is not None else 1` → **`current_step = 1`**
5. `bootstrap_prompt` = "Execute Step 1 ONLY"
6. Agent dispatched to re-execute Step 1

**Bellows dispatches Step 1.** The wrong step number comes from the default at `bellows.py:266`:
```python
current_step = resume_step if resume_step is not None else 1
```

No mechanism exists to recover `N` from:
- The database (never queried)
- The filename (no step metadata encoded)
- The shadow cache (contains plan text, not step state)

### Why the two paths diverge

| Path | How Bellows learns the step | Correct? |
|---|---|---|
| Verdict consumer (`_consume_verdicts`) | Parses step N from verdict filename, passes `resume_step=N+1` | ✅ Yes |
| Manual CEO rename (verdict-pending → executable) | No mechanism — defaults to 1 | ❌ No |
| Manual CEO rename (halted → executable) | No mechanism — defaults to 1 | ❌ No |

### Shortest possible fix shape

**Option A — DB lookup in `run_plan()`:** When `resume_step is None` and a shadow cache exists (indicating a prior claim), query:
```sql
SELECT MAX(step) FROM runs
WHERE plan_path LIKE '%{slug}%' AND status = 'Complete'
```
If result is N ≥ 1, set `resume_step = N + 1`. ~10 lines of code, confined to `run_plan()`.

**Option B — Watcher awareness:** In `PlanHandler._handle()`, when detecting an `executable-*` file that has an existing shadow cache, query the DB for prior step state and pass `resume_step` to `handle_new_plan()`. Same DB query, different location.

**Option C — Eliminate the manual rename path entirely:** Document that the ONLY correct resume path is through the verdict system. The CEO should create a verdict file in `verdicts/resolved/` rather than renaming plan files. Zero code changes — purely procedural. But does not address the `halted-*` → `executable-*` case or crash recovery.

---

## 7. Q6 — Risk Surface and Unknowns

- **Plan edited between step N and re-claim:** If the plan text was modified (steps added, removed, or renumbered) between step N completion and re-claim, the DB step number N no longer maps to the correct step in the modified plan. The shadow cache preserves the original plan text, but if the CEO edited the plan before renaming, the shadow is stale and the step numbering could be wrong. **Unknown: should re-claim with a modified plan invalidate the shadow and force re-parse? Should Bellows compare plan hashes?**

- **Prior step N output incomplete or corrupted:** The DB records `status=Complete` based on the agent's receipt status field (`parsed["receipt_status"]`), which the agent self-reports. An agent could report Complete without actually finishing its deposits. The DB-based fix would trust this status and skip to N+1, potentially building on incomplete work. **Unknown: should the fix also verify deposit existence before resuming?**

- **Multiple `verdict-pending-*` for the same plan:** The slug-matching in `_consume_verdicts()` uses substring matching (`plan_slug in pname`, `bellows.py:667`). If two plan slugs are substrings of each other (e.g., `foo` and `foo-bar`), the wrong plan could be matched. This is independent of the step-state bug but represents a latent correctness issue in the verdict consumer. **Unknown: should slug matching be exact rather than substring?**

- **Orphaned `in-progress-*` files (crash recovery):** If the daemon crashes mid-step, the plan remains as `in-progress-*` forever. `is_runnable_plan()` rejects this prefix. No startup recovery exists. The DB has a `Complete` record for the last finished step but no mechanism to detect or recover orphaned in-progress plans. **Unknown: should startup scan detect `in-progress-*` files and either resume or surface them for CEO action?**

- **DB query slug ambiguity:** `plan_path` in the DB contains the full filesystem path with the `in-progress-` prefix at recording time. A slug-based `LIKE` query could match unrelated plans if slugs overlap. **Unknown: should `record_run()` also store a canonical slug column for reliable querying?**

- **Race condition on concurrent re-claim:** If two watcher events fire for the same renamed file (watchdog can emit duplicate events), two threads could both query the DB, both get `MAX(step)=N`, and both dispatch step N+1 concurrently. The existing `shutil.move()` claim acts as a crude mutex (only one move succeeds), but the DB query would happen before the move. **Unknown: is the move-as-mutex sufficient, or does the fix need explicit locking?**

- **`halted-*` → `executable-*` rename:** Same gap as `verdict-pending-*` rename. A halted plan re-instated as executable re-dispatches Step 1. The DB fix would address this too, but the semantics differ — a halted plan may have been halted because the step FAILED, not because it completed. Resuming at N+1 after a failed step N could be wrong. **Unknown: should the fix distinguish between "halted after complete step N" and "halted after failed step N"?**

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced the complete step-state lifecycle through bellows.py, bellows.db, and verdict.py. Mapped the divergence between the automated verdict-consumer resume path (correct) and the manual CEO rename path (broken). Documented the DB schema, step counting logic, and verdict interaction. Identified 7 risk-surface unknowns for Phase 2 design.

### Files Deposited
- `bellows/knowledge/research/step-state-persistence-map-2026-04-28.md` — full diagnostic findings for BACKLOG #5 Phase 1

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- None (diagnostic scope — no fix proposed)

### Flags for CEO
- None

### Flags for Next Step
- Phase 2 design should address all 7 unknowns listed in Q6 before selecting a fix option
- Option C (eliminate manual rename path) is zero-cost and could ship immediately as an interim mitigation while the DB-based fix is designed
