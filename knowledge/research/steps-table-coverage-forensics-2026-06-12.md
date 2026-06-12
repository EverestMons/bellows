# Steps-Table Coverage + turns NULL Forensics — Findings
**Date:** 2026-06-12 | **Plan ID:** 6 | **Tier:** Medium | **Step:** 1 (SA)

---

## Section 1 — DB Ground Truth

### Schema

**`steps` DDL** (from `sqlite_master`):
```sql
CREATE TABLE steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    step_number INTEGER NOT NULL,
    role TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','running','awaiting_verdict','complete')),
    step_started_at TEXT,
    step_ended_at TEXT,
    cost_usd REAL,
    turns INTEGER,
    duration_s REAL,
    log_ref TEXT,
    UNIQUE(plan_id, step_number)
)
```

**`plans` DDL** (from `sqlite_master`):
```sql
CREATE TABLE plans (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('diagnostic', 'executable', 'qa')),
    target_project TEXT NOT NULL,
    title TEXT,
    dispatch_mode TEXT,
    tier TEXT,
    lifecycle_state TEXT NOT NULL DEFAULT 'claimed'
        CHECK (lifecycle_state IN ('claimed','in_progress','awaiting_verdict','closed','halted','abandoned')),
    total_steps INTEGER,
    deposit_placeholder_name TEXT,
    created_at TEXT NOT NULL,
    closed_at TEXT
)
```

### All `steps` rows (full dump)

| id | plan_id | step_number | role | status | step_started_at | step_ended_at | cost_usd | turns | duration_s | log_ref |
|----|---------|-------------|------|--------|-----------------|---------------|----------|-------|------------|---------|
| 1 | 4 | 1 | NULL | complete | 2026-06-11T17:22:30 | 2026-06-11T17:34:05 | 3.617 | **NULL** | 694.43 | NULL |
| 2 | 5 | 1 | NULL | complete | 2026-06-11T18:31:38 | 2026-06-11T18:36:04 | 1.052 | **NULL** | 266.20 | NULL |
| 3 | 6 | 1 | NULL | running | 2026-06-12T10:47:30 | NULL | NULL | NULL | NULL | NULL |

### All `plans` rows (full dump)

| id | type | lifecycle_state | total_steps | created_at | closed_at |
|----|------|-----------------|-------------|------------|-----------|
| 1 | executable | abandoned | 2 | 2026-06-11T14:30:26 | 2026-06-11T16:12:40 |
| 2 | executable | abandoned | 2 | 2026-06-11T14:58:18 | 2026-06-11T16:12:40 |
| 3 | executable | closed | 2 | 2026-06-11T15:36:58 | 2026-06-11T16:13:43 |
| 4 | executable | closed | 2 | 2026-06-11T17:22:29 | 2026-06-11T17:51:47 |
| 5 | executable | closed | 2 | 2026-06-11T18:31:37 | 2026-06-11T20:47:35 |
| 6 | diagnostic | claimed | 1 | 2026-06-12T10:47:29 | NULL |

### Answers

- **Plans 4 and 5: the surviving row carries step_number = 1.** No step_number = 2 row exists for either plan.
- **No plan has EVER accumulated two or more step rows.** Plans 1–3 (all 2-step plans) have ZERO step rows (they ran before the lifecycle DB write code was shipped or were abandoned before step completion). Plans 4 and 5 each have exactly one step row (step 1 only). Plan 6 has one step row (step 1, currently running).
- **`turns` is NULL for all rows** that have end-of-step data (ids 1, 2). `cost_usd` and `duration_s` are populated for step 1 of plans 4 and 5.
- **This plan's own rows (plan 6):** `plans` row id=6 with lifecycle_state='claimed'. `steps` row id=3 with plan_id=6, step_number=1, status='running', step_started_at='2026-06-12T10:47:30'. This confirms the initial-dispatch write path (`bellows.py:505`) fires correctly when `plan_id` is non-NULL.

---

## Section 2 — Daemon Log Forensics (Plans 4–5)

Source: `bellows/logs/terminal/bellows-2026-06-11.log`

### Plan 4 transition timeline

| Time | Transition | Log line |
|------|-----------|----------|
| 17:22:29 | detected + RUNNING | `[EVENT] [executable-draft-172228] ⏳ detected plan` / `⏳ RUNNING` |
| 17:22:29 | WARN (dispatch-validator) | `[WARN] dispatch-validator: stop_prose` — not a lifecycle write WARN |
| 17:22:29 | claim (mint id 4) | `[INFO] [executable-4] minted id 4 — renamed to in-progress-executable-4.md` |
| 17:22:31 | step 1 dispatch | `[EVENT] ▶ started` |
| 17:34:05 | step 1 gates pass | `[EVENT] gates step 1: passed=True, failures=0` |
| 17:34:05 | verdict-pending pause | `[PAUSE] ⏸️ step 1 — waiting for CEO verdict` |
| 17:38:40 | verdict consumed | `[EVENT] verdict continue — resuming` |
| 17:38:40 | RUNNING (resume) | `[EVENT] ⏳ RUNNING` |
| 17:38:42 | step 2 dispatch | `[EVENT] ▶ started` |
| 17:46:25 | step 2 gates pass | `[EVENT] gates step 2: passed=True, failures=0` |
| 17:46:25 | verdict-pending pause | `[PAUSE] ⏸️ step 2 — waiting for CEO verdict` |
| 17:51:47 | verdict consumed | `[EVENT] verdict continue-to-done` |

### Plan 5 transition timeline

| Time | Transition | Log line |
|------|-----------|----------|
| 18:31:37 | detected + RUNNING | `[EVENT] ⏳ detected plan` / `⏳ RUNNING` |
| 18:31:37 | claim (mint id 5) | `[INFO] [executable-5] minted id 5 — renamed to in-progress-executable-5.md` |
| 18:31:39 | step 1 dispatch | `[EVENT] ▶ started` |
| 18:36:04 | step 1 gates pass | `[EVENT] gates step 1: passed=True, failures=0` |
| 18:36:05 | verdict-pending pause | `[PAUSE] ⏸️ step 1 — waiting for CEO verdict` |
| 20:41:01 | verdict consumed | `[EVENT] verdict continue — resuming` |
| 20:41:01 | RUNNING (resume) | `[EVENT] ⏳ RUNNING` |
| 20:41:03 | step 2 dispatch | `[EVENT] ▶ started` |
| 20:46:14 | step 2 gates pass | `[EVENT] gates step 2: passed=True, failures=0` |
| 20:46:15 | verdict-pending pause | `[PAUSE] ⏸️ step 2 — waiting for CEO verdict` |
| 20:47:35 | verdict consumed | `[EVENT] verdict continue-to-done` |

### Lifecycle write WARNs

**Zero lifecycle write WARNs on 2026-06-11.** `grep -c 'WARN.*lifecycle' bellows-2026-06-11.log` = 0. The only WARNs in the log are `dispatch-validator: stop_prose` (plans 4 and 5) and format mismatches — none are lifecycle DB write failures. The log-and-continue failure signature (`[WARN] [lifecycle]`) never appears.

---

## Section 3 — Step-JSON Reconciliation

### Step JSONs for plans 4 and 5

| JSON file | Plan | Step | cost_usd | turns | duration_s | Parsed keys |
|-----------|------|------|----------|-------|------------|-------------|
| `20260611-172230-step.json` | 4 | 1 | 3.617 | **None** | **None** | session_id, is_error, stop_reason, result_text, cost_usd, permission_denials, receipt_status, ceo_flags, escalate, verdict_requested |
| `20260611-173841-step.json` | 4 | 2 | 2.323 | **None** | **None** | (same keys) |
| `20260611-183138-step.json` | 5 | 1 | 1.052 | **None** | **None** | (same keys) |
| `20260611-204102-step.json` | 5 | 2 | 1.399 | **None** | **None** | (same keys) |

### Reconciliation: JSON files on disk vs DB rows

| Plan | Step JSONs on disk | Step rows in DB | Gap |
|------|--------------------|-----------------|-----|
| 4 | 2 (steps 1, 2) | **1** (step 1 only) | **Step 2 row missing** |
| 5 | 2 (steps 1, 2) | **1** (step 1 only) | **Step 2 row missing** |

### `turns` source analysis

The raw result event from `claude -p --output-format stream-json` **DOES** contain `num_turns`:

```
Result event keys: ['type', 'subtype', 'is_error', 'duration_ms', 'duration_api_ms',
  'num_turns', 'result', 'stop_reason', 'session_id', 'total_cost_usd', 'usage',
  'modelUsage', 'permission_denials', 'fast_mode_state', 'uuid']
num_turns: 100  (verified in plan 4 step 1's raw output)
```

The `turns` value is **present in the raw source** but **lost in the parse+write pipeline**. This is NOT a runner output-mode limitation — the data is emitted but never propagated.

---

## Section 4 — Write-Surface Census

### `steps`-touching write sites

| Site | File:Line | INSERT or UPDATE | Transition boundary | Columns written | `turns` data source |
|------|-----------|-----------------|---------------------|-----------------|---------------------|
| A | `lifecycle.py:258-262` (`record_step_start`) | INSERT | Step dispatch (pre-runner) | plan_id, step_number, role, status='running', step_started_at | N/A (start-of-step) |
| B | `lifecycle.py:280-284` (`record_step_end`) | UPDATE | Step completion (post-gates) | status, step_ended_at, cost_usd, turns, duration_s, log_ref | `turns` parameter — defaults to `None` |
| C | `bellows.py:505` | Calls site A | Initial dispatch (post-claim) | (delegates to A) | N/A |
| D | `bellows.py:557-558` | Calls site B | Initial step end | cost_usd=`parsed.get("cost_usd")`, duration_s=`_lc_step_duration` | **`turns` is NOT passed** — omitted from kwargs |
| E | `bellows.py:614` | Calls site A | While-loop next step start | (delegates to A) | N/A |
| F | `bellows.py:667-668` | Calls site B | While-loop step end | cost_usd=`parsed.get("cost_usd")`, duration_s=`_lc_step_duration` | **`turns` is NOT passed** — omitted from kwargs |

### `turns` pipeline gap (two-part)

1. **Parser gap:** `parser.py:parse()` (lines 6–57) extracts `total_cost_usd` → `cost_usd` but never extracts `num_turns` from the raw result event. The parsed dict has no `turns` key.
2. **Callsite gap:** `bellows.py:557-558` and `bellows.py:667-668` call `record_step_end()` with `cost_usd=` and `duration_s=` but **omit `turns=`**, so it defaults to `None` per `lifecycle.py:272`.

Even if the parser extracted `num_turns`, the bellows.py callsites would still need to pass it through.

### Dispatch path trace — the load-bearing gap

**Path (i): Initial dispatch (post-claim) — `run_plan()` entry:**
- `bellows.py:411`: `plan_id = None`
- `bellows.py:412-453`: `if not plan_filename.startswith("in-progress-"):` — mints plan_id via `lifecycle.mint_and_claim()`. **This is the ONLY place `plan_id` is assigned.**
- `bellows.py:505`: `_lc_step_id = lifecycle.record_step_start(plan_id, current_step) if plan_id else None` — **`plan_id` is non-None → step row IS written** ✅
- `bellows.py:557-558`: `lifecycle.record_step_end(_lc_step_id, ...)` — **`_lc_step_id` is non-None → step row IS updated** ✅

**Path (ii): Post-verdict resume dispatch — `_consume_verdicts()` → `handle_new_plan()` → `run_plan()`:**
- `bellows.py:1607`: `self.handle_new_plan(inprogress_path, resume_step=next_step)` — file is `in-progress-executable-4.md`
- `bellows.py:1391-1392`: spawns thread → `_run_tracked()` → `run_plan(path, ..., resume_step=2)`
- `bellows.py:345`: `plan_name = os.path.basename(plan_path)` → `"in-progress-executable-4.md"`
- `bellows.py:412`: `if not plan_filename.startswith("in-progress-"):` → **condition is FALSE** (file starts with `in-progress-`)
- `bellows.py:411`: **`plan_id` stays `None`** — the mint-and-claim block is entirely skipped
- `bellows.py:505`: `lifecycle.record_step_start(plan_id, current_step) if plan_id else None` → **`plan_id` is None → evaluates to `None`** → NO step row written ❌
- `bellows.py:557-558`: `record_step_end(None, ...)` → `lifecycle.py:275`: `if step_id is None: return` → NO update ❌

**The resume path never recovers `plan_id` from the filename.** The id (4, 5) is embedded in `in-progress-executable-4.md` / `in-progress-executable-5.md`, but no code extracts it. All lifecycle writes for resumed steps are silently skipped.

---

## Section 5 — Root Cause

### Cause 1: Missing step 2 row

**CONFIRMED: Write-surface gap (Context candidate (a)).**

The post-verdict resume dispatch path (`_consume_verdicts` at `bellows.py:1607` → `run_plan` at `bellows.py:342`) re-enters `run_plan()` with the plan file already named `in-progress-*`. The id-minting block (`bellows.py:412-453`) is gated by `if not plan_filename.startswith("in-progress-"):`  — on resume, this condition is FALSE, so `plan_id` stays `None` (set at `bellows.py:411`). All lifecycle writes (step start, step end, gate events, deposits, commits) are guarded by `if plan_id` or `if step_id is None: return`, so they are ALL silently skipped for every resumed step.

**Evidence chain:**
- `bellows.py:411` — `plan_id = None`
- `bellows.py:412` — condition `not plan_filename.startswith("in-progress-")` is False on resume
- `bellows.py:505` — `if plan_id else None` → None
- DB: plans 4 and 5 both have `total_steps=2` but only step_number=1 rows exist
- Daemon log: both plans ran step 2 successfully (gates passed, verdict filed)

### Cause 2: `turns` NULL

**CONFIRMED: Semantics mismatch (Context candidate (c))** — two independent gaps:

1. **Parser omission:** `parser.py:parse()` (lines 6–57) never extracts `num_turns` from the result event, even though the field is present in the raw output (`num_turns: 100` verified in `20260611-172230-step.json`). The parsed dict has no `turns` key.

2. **Callsite omission:** `bellows.py:557-558` and `bellows.py:667-668` call `lifecycle.record_step_end()` with `cost_usd=` and `duration_s=` but **omit `turns=`**. Even if the parser were fixed, the callsite would still pass `turns=None` by default.

**Evidence chain:**
- `parser.py:46-57` — return dict has no `turns` key
- Raw result event (verified): `num_turns: 100`
- `bellows.py:557-558` — `turns` kwarg not passed
- `lifecycle.py:272` — `turns=None` default
- DB: `turns` is NULL for all rows with end-of-step data

### Context candidate classification

| Candidate | Classification | Evidence |
|-----------|---------------|----------|
| (a) Write-surface gap | **CONFIRMED** | `bellows.py:411-412` — resume path leaves `plan_id = None` → step row never written |
| (b) Log-and-continue silent WARN | **ELIMINATED** | Zero lifecycle WARNs on 2026-06-11 (`grep -c 'WARN.*lifecycle'` = 0). The writes were never attempted, not attempted-and-failed. |
| (c) Semantics mismatch | **CONFIRMED** | `parser.py` omits `num_turns`; `bellows.py` omits `turns=` kwarg |

---

## Section 6 — Phase 2 Trust Verdict (Per-Column)

### `steps` table columns

| Column | Status | Notes |
|--------|--------|-------|
| **Row coverage** | **Unreliable** → reliable after fix | Only initial-dispatch steps have rows. Resume-path steps (step 2 of any paused multi-step plan) are entirely missing. |
| `id` | Reliable as-is | Auto-increment PK, no issues |
| `plan_id` | Reliable as-is | Correctly set when row exists |
| `step_number` | Reliable as-is | Always 1 (the only surviving rows); correct for those rows |
| `role` | Reliable as-is | Always NULL (never populated by current write sites) |
| `status` | Reliable as-is | Correctly reflects end-of-step state |
| `step_started_at` | Reliable as-is | Correctly set by `record_step_start` |
| `step_ended_at` | Reliable as-is | Correctly set by `record_step_end` |
| `cost_usd` | **Unreliable** → reliable after fix | Values are correct for step 1, but step 2 cost is entirely missing (no row). Session-wrap roll-up (query 4) is **currently understating cost** — plan 4 is missing $2.32 (step 2), plan 5 is missing $1.40 (step 2). |
| `turns` | **Unreliable** → reliable after fix | NULL for all rows. Two-part fix needed: parser extraction + callsite passthrough. |
| `duration_s` | Reliable as-is (for existing rows) → reliable after fix for coverage | Correctly computed from wall-clock for step 1 rows. Missing for step 2 rows (no row). |
| `log_ref` | Reliable as-is | Always NULL (never populated by current write sites — no caller passes it) |

### `plans` table columns (canonical query surfaces)

| Column | Status | Notes |
|--------|--------|-------|
| `id` | Reliable as-is | Monotonic, correctly minted |
| `type` | Reliable as-is | Correctly parsed from filename |
| `lifecycle_state` | Reliable as-is | All transitions write correctly (close and halt paths update state) |
| `total_steps` | Reliable as-is | Correctly extracted from plan headers |
| `created_at` | Reliable as-is | Set at mint time |
| `closed_at` | Reliable as-is | Set on close/halt/abandon |

### Reporting Phase 2 query safety

| Query shape | Safe now? | Notes |
|-------------|-----------|-------|
| Plan-level aggregations (lifecycle_state, created_at, closed_at) | **Safe** | `plans` table is reliable |
| Per-step cost/duration roll-up (`SUM(cost_usd)` grouped by plan_id) | **BLOCKED** | Understates cost for any plan that paused mid-run. Plans 4, 5 are each missing one step's cost. |
| Canonical session-wrap query 4 (`SUM(cost_usd), SUM(turns), SUM(duration_s)`) | **BLOCKED** | `cost_usd` understated, `turns` always NULL, `duration_s` incomplete |
| Step-count validation (`COUNT(*) FROM steps WHERE plan_id = X` vs `total_steps`) | **BLOCKED** | Will show 1 when 2 are expected for any multi-step plan that paused |
| Gate-event analysis (JOIN steps → gate_events) | **Partially blocked** | Gate events for step 1 are present; step 2 gate events are missing (no step_id to reference) |

**Canonical session-wrap roll-up (query 4) is currently understating cost.** Plan 4 reports $3.62 but actual total is $5.94. Plan 5 reports $1.05 but actual total is $2.45.

---

## Section 7 — Gap Assessment + Verification Blocks

### Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|-----|---------------------------|----------------|-----------------|
| G1: Resume path `plan_id` is None | `bellows.py:411` — `plan_id = None`; `bellows.py:412` — mint block skipped on resume | Extract `plan_id` from id-canonical filename on the `in-progress-` path (e.g., parse int from `in-progress-executable-4.md`) | Add `else` branch at `bellows.py:412` to recover plan_id from filename |
| G2: Parser omits `num_turns` | `parser.py:46-57` — return dict has no `turns` key | Add `"turns": raw.get("num_turns")` to parsed output | Edit `parser.py:parse()` return dict |
| G3: `record_step_end` callsites omit `turns` | `bellows.py:557-558` and `bellows.py:667-668` — `turns=` not passed | Pass `turns=parsed.get("turns")` at both callsites | Edit both `record_step_end` calls |
| G4: `_id_tag_instruction` empty on resume | `bellows.py:472` — `if plan_id else ""` evaluates to "" when plan_id is None on resume | Will be fixed by G1 (recovering plan_id) | No additional change needed beyond G1 |

### Verification Blocks

```
V1: Surviving-row step_number per plan
  Claim: Plans 4 and 5 each have exactly one step row, carrying step_number = 1.
  Query: SELECT plan_id, step_number, COUNT(*) FROM steps WHERE plan_id IN (4,5) GROUP BY plan_id, step_number
  Expected: (4, 1, 1), (5, 1, 1)  — two rows total, both step_number=1
```

```
V2: Skipped transition boundary
  Claim: The resume path enters run_plan() with plan_filename starting with "in-progress-",
         causing the id-minting block to be skipped and plan_id to stay None.
  Query: grep -n 'plan_id = None' bellows.py && grep -n 'not plan_filename.startswith("in-progress-")' bellows.py
  Expected: Line 411 shows `plan_id = None`; Line 412 shows the conditional gate
```

```
V3: turns source variable emptiness
  Claim: parser.py:parse() never includes "turns" in its return dict, and bellows.py callsites
         never pass turns= to record_step_end().
  Query: grep -n 'turns' parser.py && grep -n 'turns' bellows.py
  Expected: parser.py has zero occurrences of "turns" in the return dict;
            bellows.py:557-558 and 667-668 show record_step_end calls without turns= kwarg
```

```
V4: Zero lifecycle WARN on 2026-06-11
  Claim: No lifecycle write WARN was emitted on 2026-06-11.
  Query: grep -c 'WARN.*lifecycle' logs/terminal/bellows-2026-06-11.log
  Expected: 0
```

```
V5: num_turns present in raw result event
  Claim: The claude -p result event contains num_turns but the parser discards it.
  Query: python3 -c "import json; f=open('logs/20260611-172230-step.json'); d=json.load(f);
         [print(k) for k in json.loads([l for l in d['raw_output'].split(chr(10))
         if '\"type\":\"result\"' in l][-1]).keys() if 'turn' in k.lower()]"
  Expected: num_turns
```
