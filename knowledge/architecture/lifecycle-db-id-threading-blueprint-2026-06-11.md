# Lifecycle DB + Monotonic Id Threading — Blueprint

**Date:** 2026-06-11
**Author:** Bellows Systems Analyst
**Plan:** diagnostic-bellows-lifecycle-db-id-threading-surface-2026-06-11
**Step:** 1 (SA diagnostic)
**Conforms to:** `reporting-phase-0-coverage-map-2026-06-10.md` (all design decisions locked)

---

## Section 1 — Filename/Slug Consumer Census

Every code site that derives, parses, matches, or constructs anything from the plan filename or slug. Each row identifies: where, what it extracts, what it does with it, and what changes when the name shifts from `<type>-<descriptive-slug>-YYYY-MM-DD.md` to `<type>-<id>.md`.

### 1.1 `slug_for()` — log-tag derivation

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:71-81 |
| **What it extracts** | Strips `.md`, strips lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`), strips trailing `-YYYY-MM-DD` via `re.sub(r'-\d{4}-\d{2}-\d{2}$', '', s)`, truncates to 30 chars |
| **What it does** | Produces a short display slug for `_log()` messages |
| **Impact of id-only name** | The date-strip regex fires harmlessly (no trailing date to strip). Input `diagnostic-142.md` → output `diagnostic-142` (25 chars, well under 30). No functional change, but the regex becomes dead code for new-format names. **No edit required** (tolerate both). |

### 1.2 `slug_from_path()` — verdict filename key

| Attribute | Value |
|---|---|
| **File:line** | verdict.py:82-92 |
| **What it extracts** | Strips lifecycle prefixes (`in-progress-`, `verdict-pending-`) AND type prefixes (`executable-`, `diagnostic-`), then strips `.md`. Returns the remaining string as the slug. |
| **What it does** | Used as the key in verdict-request filenames (`verdict-request-{slug}-step-{N}.md`), verdict response filenames (`verdict-{slug}-step-{N}.md`), cleanup globs, `_seen` set membership, `_cleanup_verdicts_for_slug()` matching, and `plan_slug in pname` substring matching in `_consume_verdicts()`. |
| **Impact of id-only name** | Legacy: `diagnostic-foo-bar-2026-06-10.md` → `foo-bar-2026-06-10`. New: `diagnostic-142.md` → `142`. Verdict files become `verdict-request-142-step-1.md`, `verdict-142-step-1.md`. The slug is now a bare integer string. **Critical:** the `plan_slug in pname` substring match at bellows.py:1424 becomes fragile — `"142" in "verdict-pending-diagnostic-1423.md"` would false-match via substring containment of `142` within `1423`. **Must convert to exact slug comparison or regex-bounded match.** |

### 1.3 `_shadow_path()` — shadow cache key

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:229-237 |
| **What it extracts** | Strips lifecycle prefixes from plan_filename to get the "canonical name", appends `.pristine` |
| **What it does** | Maps plan filenames across lifecycle states to the same shadow-cache file at `.bellows-cache/<canonical>.pristine` |
| **Impact of id-only name** | `diagnostic-142.md` → `.bellows-cache/diagnostic-142.md.pristine`. No issue. The prefix-stripping still works since the `in-progress-diagnostic-142.md` → `diagnostic-142.md` mapping is prefix-based, not date-based. **No edit required.** |

### 1.4 `_write_shadow()` / `_read_shadow()` / `_delete_shadow()`

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:240-259 |
| **What it extracts** | Delegates to `_shadow_path()` |
| **Impact of id-only name** | Transparent — follows `_shadow_path()`. **No edit required.** |

### 1.5 `_cleanup_verdicts_for_slug()` — verdict request cleanup

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:262-272 |
| **What it extracts** | Takes a slug string, globs `verdict-request-{slug}-step-*.md` in verdicts/pending/ |
| **What it does** | Removes stale verdict-request files when a plan reaches terminal state (Done/ or halted-) |
| **Impact of id-only name** | Slug is now `142` → glob becomes `verdict-request-142-step-*.md`. Glob pattern is exact-prefix, so no ambiguity with `1420` or `1423`. **No edit required.** |

### 1.6 `is_runnable_plan()` — plan detection regex

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1141-1144 |
| **What it extracts** | `re.match(r"^(parallel-\d+-)?(executable\|diagnostic\|qa)-.*\.md$", filename)` |
| **What it does** | Determines if a filename in decisions/ is a claimable plan |
| **Impact of id-only name** | `diagnostic-142.md` matches `diagnostic-.*\.md$`. **No edit required.** |

### 1.7 In-progress rename (claim)

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:358-414 |
| **What it extracts** | `base_filename` by stripping lifecycle prefixes; constructs `inprogress_path = os.path.join(plan_dir, f"in-progress-{base_filename}")` |
| **What it does** | Atomically claims the plan by renaming to `in-progress-<base_filename>` |
| **Impact of id-only name** | `diagnostic-142.md` → `in-progress-diagnostic-142.md`. Prefix-based, no date dependency. **This is the insertion point for the id mint + rename** — the new flow replaces the Planner's deposit filename with the id-bearing canonical name at this site. See Section 2. |

### 1.8 Verdict-pending rename

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:449, 540, 636, 667 (four identical sites) |
| **What it extracts** | `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")` |
| **What it does** | Renames from in-progress to verdict-pending before posting verdict request |
| **Impact of id-only name** | `in-progress-diagnostic-142.md` → `verdict-pending-diagnostic-142.md`. Prefix-based. **No edit required.** |

### 1.9 Done/ filing (auto-close path)

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:677-685 |
| **What it extracts** | `done_path = os.path.join(done_dir, base_filename)` |
| **What it does** | Moves plan to `Done/diagnostic-142.md` after auto-close |
| **Impact of id-only name** | Filed as `Done/diagnostic-142.md`. **No edit required.** |

### 1.10 Done/ filing (verdict continue-to-done path)

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1471-1476 |
| **What it extracts** | `done_path = os.path.join(done_dir, original_name)` where `original_name = pname.replace("verdict-pending-", "", 1)` |
| **What it does** | Same as 1.9 but via verdict consumption |
| **Impact of id-only name** | `original_name` = `diagnostic-142.md`. **No edit required.** |

### 1.11 Halted filing (verdict stop + teardown-failure paths)

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:398, 1442, 1498 |
| **What it extracts** | `halted_path = os.path.join(plan_dir, f"halted-{base_filename}")` or `halted_name = f"halted-{original_name}"` |
| **What it does** | Renames plan to `halted-diagnostic-142.md` on rejection/stop |
| **Impact of id-only name** | Prefix-based. **No edit required.** |

### 1.12 Verdict-request filename construction

| Attribute | Value |
|---|---|
| **File:line** | verdict.py:183-185 |
| **What it extracts** | `slug = slug_from_path(plan_path)` → `filename = f"verdict-request-{slug}-step-{step_number}.md"` |
| **What it does** | Creates the verdict-request file in `verdicts/pending/` |
| **Impact of id-only name** | Slug becomes `142`, filename becomes `verdict-request-142-step-1.md`. Conforms to coverage map `verdict-P0142-step-2.md` shape (format TBD — bare `142` or prefixed `P0142`). **No edit required** to this site itself, but slug derivation upstream must produce the correct id-based slug. |

### 1.13 Verdict-response filename construction + consumption parsing

| Attribute | Value |
|---|---|
| **File:line** | verdict.py:284 (check_verdict), bellows.py:1363-1369 (_consume_verdicts regex) |
| **What it extracts** | `check_verdict`: `filename = f"verdict-{plan_slug}-step-{step_number}.md"`. `_consume_verdicts`: `re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)` → captures `plan_slug` from group(1). |
| **What it does** | Locates and parses the Planner's verdict response file |
| **Impact of id-only name** | Verdict files become `verdict-142-step-1.md`. The regex `(.+)` greedily matches `142`. **Critical:** with bare integer slugs, the regex `verdict-(.+)-step-(\d+)\.md$` could ambiguously parse a slug like `verdict-142-step-1-step-2.md` — but that filename shape never exists (step numbers don't compound). However, the greedy `.+` before `-step-` means for `verdict-142-step-2.md`, group(1) = `142` and group(2) = `2`. **No edit required** — greedy match is correct here. |

### 1.14 Verdict consumption — plan slug matching

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1424 |
| **What it extracts** | `if pname.startswith("verdict-pending-") and plan_slug in pname` |
| **What it does** | Matches a verdict's extracted slug against verdict-pending plan filenames in decisions/ |
| **Impact of id-only name** | **BUG:** Substring match `"142" in "verdict-pending-diagnostic-1423.md"` → True (false match). Must change to exact comparison: extract the slug from `pname` and compare with `==`. **Edit required.** |

### 1.15 Verdict consumption — slug prefix stripping for lookup

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1373-1377 |
| **What it extracts** | `lookup_slug = plan_slug; for prefix in ("diagnostic-", "executable-"): ...` strips type prefix from the verdict's captured slug |
| **What it does** | Normalizes the slug for looking up the pending verdict-request file |
| **Impact of id-only name** | The verdict regex captures `142` (no type prefix). The prefix strip loop fires harmlessly (no match). **No edit required** — but this code becomes dead for new-format names. |

### 1.16 Orphan-guard startup sweep

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1549-1583 (`_perform_startup_sweep`) |
| **What it extracts** | `re.match(r"^verdict-request-(.+)-step-\d+\.md$", pf)` → `extracted_slug`, compared against `active_slugs` (derived from `slug_from_path()` on active plan filenames) |
| **What it does** | Removes orphaned verdict-request files whose slugs don't match any active plan |
| **Impact of id-only name** | Regex captures `142` from `verdict-request-142-step-1.md`. `active_slugs` contains `142` (from `slug_from_path("diagnostic-142.md")` = `142`). Exact set membership (`extracted_slug not in active_slugs`) — **no substring bug here.** No edit required. |

### 1.17 `_seen` set membership

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1164, 1177, 1179, 1181, 1197, 1201, and throughout `_consume_verdicts` |
| **What it extracts** | `verdict.slug_from_path(path)` or `verdict.slug_from_path(plan_path)` |
| **What it does** | De-duplicates plan dispatch — ensures a plan is only dispatched once per daemon lifetime |
| **Impact of id-only name** | Slug becomes `142`. Set membership uses `==` (Python set). **No edit required.** However, if two plans from different projects happen to have the same bare-integer id (they won't — the id is global-monotonic), this would collide. |

### 1.18 Stale verdict detection — Done/ and halted- scan

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1521-1538 |
| **What it extracts** | `if plan_slug in dname` — substring match against filenames in Done/ and halted- files |
| **What it does** | Detects stale verdicts whose plan already reached terminal state |
| **Impact of id-only name** | **BUG:** Same substring issue as 1.14 — `"142" in "diagnostic-1423.md"` → false match. **Edit required.** |

### 1.19 Worktree branch naming

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:854, 984 |
| **What it extracts** | `branch_name = f"bellows-wt/{re.sub(r'[^a-zA-Z0-9._/-]', '-', slug)}"` (creation at :854) and `branch_name = f"bellows-wt/{slug}"` (teardown at :984) |
| **What it does** | Creates a git branch per plan execution for worktree isolation |
| **Impact of id-only name** | Slug (from `slug_from_path`) = `142`. Branch = `bellows-wt/142`. The sanitization regex at :854 is a no-op on a numeric string. **Potential issue:** very short branch name (`bellows-wt/142`) is unusual but valid. The creation slug comes from `plan_slug = verdict.slug_from_path(base_filename)` at bellows.py:364. **No edit required.** |

### 1.20 `record_run()` — operational DB write

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:275-304, called at :471, :547, :569, :643 |
| **What it extracts** | Takes `plan_slug` as parameter (from `verdict.slug_from_path()`) |
| **What it does** | Inserts a row into `bellows.db` `runs` table with `plan_slug` column |
| **Impact of id-only name** | `plan_slug` = `142`. Stored as-is. **No edit required** — this is the operational DB, not the lifecycle DB. |

### 1.21 `_invalidate_seen_on_redeposit()`

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1205-1218 |
| **What it extracts** | `slug = verdict.slug_from_path(path)` |
| **What it does** | Invalidates `_seen` entry when a new plan file appears at an already-seen slug |
| **Impact of id-only name** | Works on slug equality. **No edit required.** |

### 1.22 PlanHandler `_handle()` + `on_moved()`

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:1168-1203, 1220-1233 |
| **What it extracts** | Uses `is_runnable_plan(filename)`, `verdict.slug_from_path(path)`, `slug_for(filename)` |
| **What it does** | Event dispatch for file creation/modification/move in watched directories |
| **Impact of id-only name** | All callees are analyzed above. **No edit required.** |

### 1.23 Verdict ledger entries

| Attribute | Value |
|---|---|
| **File:line** | verdict.py:315-332 (`log_to_ledger`) |
| **What it extracts** | `plan_path` (full path string stored in the `plan_path` field of JSONL entry) |
| **What it does** | Appends JSON line to `verdicts/ledger.jsonl` with the full plan path |
| **Impact of id-only name** | Path changes from `.../in-progress-diagnostic-foo-2026-06-10.md` to `.../in-progress-diagnostic-142.md`. The path is stored verbatim — **no parsing issue**. Historical entries retain legacy format. **No edit required.** |

### 1.24 Notification text

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:403, 544-545, 687 (calls to `notifier.notify_*` and `notifier.push`) |
| **What it extracts** | `plan_name = os.path.basename(plan_path)` passed to notification functions |
| **What it does** | Pushover notification text includes the plan filename |
| **Impact of id-only name** | Notification says `diagnostic-142.md` instead of `diagnostic-foo-bar-2026-06-10.md`. Less descriptive but functionally correct. **No edit required.** |

### 1.25 Step-log naming

| Attribute | Value |
|---|---|
| **File:line** | runner.py:57 |
| **What it extracts** | `log_path = LOGS_DIR / f"{timestamp}-step.json"` |
| **What it does** | Names log files by timestamp, NOT by plan slug/filename |
| **Impact of id-only name** | **No impact** — log naming is timestamp-based. |

### 1.26 Bootstrap prompt construction

| Attribute | Value |
|---|---|
| **File:line** | bellows.py:431-438, 553 |
| **What it extracts** | `shadow_prompt_path = str(_shadow_path(plan_filename))` |
| **What it does** | Constructs the initial prompt given to `claude -p`, referencing the shadow cache path |
| **Impact of id-only name** | Shadow path becomes `.bellows-cache/diagnostic-142.md.pristine`. **No edit required.** |

### 1.27 Dispatch-validator (`validate_at_claim`)

| Attribute | Value |
|---|---|
| **File:line** | validators.py:155-207 |
| **What it extracts** | Receives `header` (parsed from plan text) and `plan_path`. Does NOT parse the filename — only inspects header fields. |
| **What it does** | Validates dispatch_mode, STOP-prose, pause_for_verdict, field types |
| **Impact of id-only name** | **No edit required** — filename-agnostic. |

### Census Summary — Edit-Required Sites

| # | File:line | Issue | Fix |
|---|---|---|---|
| 1.14 | bellows.py:1424 | `plan_slug in pname` substring match → false positive with numeric ids | Exact slug comparison |
| 1.18 | bellows.py:1521-1538 | `plan_slug in dname` substring match in Done/halted scan → false positive | Exact slug comparison |
| 1.2 | verdict.py:82-92 | `slug_from_path()` strips type prefix; new id-only slugs are bare integers → no structural issue but callers must be aware | Extend to handle id-only format if needed |

---

## Section 2 — Id Authority + Claim-Rename Mechanics

### 2.1 The Mint: `id_sequence` Table

The id is a **global-monotonic integer**, minted from a dedicated counter table `id_sequence` in the new lifecycle DB. The mint is a single-row table:

```sql
CREATE TABLE id_sequence (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    next_id INTEGER NOT NULL DEFAULT 1
);
INSERT INTO id_sequence (id, next_id) VALUES (1, 1);
```

Minting: `UPDATE id_sequence SET next_id = next_id + 1 RETURNING next_id - 1;` (SQLite supports `RETURNING` since 3.35). The transaction that mints the id also writes the initial `plans` row — atomically, in a single `BEGIN IMMEDIATE ... COMMIT` block. This ensures no id is burned without a corresponding plans row.

### 2.2 Insertion Point in the Claim Path

Current claim flow (bellows.py:395-414):

```
(1) validate_at_claim()         [bellows.py:396]
(2) halted filing if rejected   [bellows.py:398-404]
(3) shutil.move → in-progress-  [bellows.py:411]
(4) _write_shadow()             [bellows.py:414]
```

**New claim flow:**

```
(1) validate_at_claim()                        — unchanged
(2) halted filing if rejected                  — unchanged, uses deposit placeholder name
(3) MINT ID (lifecycle DB transaction)         — NEW: mint id + write plans row atomically
(4) RENAME: deposit placeholder → id-canonical — NEW: single rename, replaces step (3)
    deposit_name → in-progress-<type>-<id>.md
(5) _write_shadow()                            — unchanged, uses new canonical name
```

**Key: one rename, not two.** The current flow does: `diagnostic-foo-draft.md` → `in-progress-diagnostic-foo-draft.md`. The new flow does: `diagnostic-draft-143022.md` → `in-progress-diagnostic-142.md`. The deposit placeholder name is entirely discarded at claim — it's transient.

### 2.3 Post-Claim Canonical Name Through Full Lifecycle

| State | Filename |
|---|---|
| Planner deposit (pre-claim) | `diagnostic-draft-HHMMSS.md` (placeholder, uniqueness-only) |
| Claimed (in-progress) | `in-progress-diagnostic-142.md` |
| Verdict-pending | `verdict-pending-diagnostic-142.md` |
| Halted | `halted-diagnostic-142.md` |
| Closed (Done/) | `diagnostic-142.md` (in `Done/` directory) |

Confirm: this matches current rename mechanics at bellows.py:411 (claim), :449/:540/:636/:667 (verdict-pending), :677-685 (Done/), :398/:1442/:1498 (halted). All use `base_filename` which is the canonical name with lifecycle prefixes stripped. Post-fix, `base_filename` = `diagnostic-142.md`.

### 2.4 Crash-Window Behavior

The crash window is between id-mint and rename completion. Two sub-cases:

**(a) Id minted + plans row written, rename fails (process crash before `shutil.move` completes):**

Recovery predicate: the lifecycle DB has a `plans` row with `lifecycle_state = 'claimed'` but no file on disk matches `in-progress-<type>-<id>.md`. On next startup, scan for `plans` rows in `claimed` state and check for their plan file. If missing, check for the deposit placeholder (the `deposit_placeholder_name` column in the `plans` row stores the original deposit filename). If the placeholder still exists, re-execute the rename. If the placeholder is also gone, mark the `plans` row as `abandoned`.

**(b) Rename succeeds, plans row update (to `in_progress` state) fails:**

Cannot happen — the plans row is written in the SAME transaction as the id mint (step 3 above). The rename (step 4) happens AFTER the transaction commits. If the rename succeeds, the plans row is already durable.

**(c) Id minted but DB write fails (SQLite error):**

The `RETURNING` clause is inside a transaction. If the transaction fails, the id is not consumed — `next_id` is not incremented. No id is burned.

### 2.5 Pre-Claim Deposit-Placeholder Convention

The Planner deposits plans with a **transient placeholder name**. The only requirement is uniqueness within the decisions directory at deposit time. Recommended form:

```
<type>-draft-<HHMMSS>.md
```

Example: `diagnostic-draft-143022.md`, `executable-draft-091500.md`.

**Validation against current detection/validation code:**

- `is_runnable_plan()` (bellows.py:1141-1144): regex `^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$` — matches `diagnostic-draft-143022.md` ✓
- `validate_at_claim()` (validators.py:155-207): inspects header fields only, not filename. ✓
- `_parse_plan_header()` (gates.py:119-185): parses plan text, not filename. ✓
- PlanHandler `_handle()`: uses `is_runnable_plan()` + `slug_from_path()`. `slug_from_path("diagnostic-draft-143022.md")` = `draft-143022`. Unique enough for dedup during the transient pre-claim window. ✓

**Nothing in detection/validation requires a descriptive slug or date in the filename.**

---

## Section 3 — Lifecycle DB Write Surface

### 3.1 DB File Location and Root Resolution

**Location:** `<bellows_root>/lifecycle.db` — sibling to the existing `bellows.db`.

**Root resolution:** MUST use `bellows_root.resolve_bellows_root()` (bellows_root.py:12-29), NOT `Path(__file__).parent`. The marker-walk-up helper finds the canonical bellows root by searching for `config.json` upward from `__file__`. This is critical because:

- `runner.py` already uses `resolve_bellows_root()` at runner.py:21 (`BELLOWS_ROOT = resolve_bellows_root()`)
- `bellows.py` uses `Path(__file__).parent.resolve()` at bellows.py:23 — this is safe because `bellows.py` is always executed from the canonical checkout (it's the daemon entry point, never runs in a worktree)
- `verdict.py` uses `Path(__file__).parent.resolve()` at verdict.py:13 — same: verdict.py runs in-daemon
- `gates.py` has no module-level root resolution — it receives paths as arguments

**Confirm:** All lifecycle DB write sites run in-daemon from the canonical checkout. No write site executes from a worktree context. The daemon entry point is `bellows.py:__main__` which runs from the canonical bellows root. All write calls flow through `run_plan()` → `record_run()` and `_consume_verdicts()`, both executing in the daemon process. `runner.py:run_step()` launches `claude -p` as a subprocess in the worktree but returns parsed results to the daemon process for recording. `gates.py:check()` runs in-daemon, invoked from `run_plan()`.

**Flag:** If any future write site is added to `gates.py` or a module imported by the agent subprocess, it MUST use `resolve_bellows_root()`, not `Path(__file__).parent`.

### 3.2 Transition Boundaries and Available Data

#### Transition 1: CLAIM

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:395-414 (validate_at_claim → shutil.move) |
| **Data in hand** | Plan filename (deposit placeholder), plan text, parsed header (type, tier, dispatch_mode, pause_for_verdict, model, auto_close, total_steps, qa_steps, deposits list), project_path |
| **Lifecycle DB writes** | `plans` INSERT (id, type, target_project, title from `# Title` header, dispatch_mode, tier, lifecycle_state='claimed', total_steps, created_at) + `diagnostic_meta` or `executable_meta` INSERT (if derivable from header: scope, hypothesis for diagnostics; test_scope for executables) |

#### Transition 2: STEP START

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:462-466 (first step), :558-565 (subsequent steps in while loop) |
| **Data in hand** | plan_id (from claim), step_number, role (from `_gate_is_qa_step` or header `qa_steps`), model, worktree_path |
| **Lifecycle DB writes** | `steps` INSERT (plan_id, step_number, role, status='running', step_started_at) |

#### Transition 3: STEP END / GATE CHECK

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:496-508 (first step gate check), :589-604 (subsequent steps) |
| **Data in hand** | plan_id, step_number, parsed result (cost_usd, turns from parsed, duration from elapsed time), gate_result (failures list, files_changed, is_qa_step), receipt_status |
| **Lifecycle DB writes** | `steps` UPDATE (status='complete' or 'awaiting_verdict', step_ended_at, cost_usd, turns, duration_s, log_ref=log_path). `gate_events` INSERT — one row per gate evaluation: (step_id, gate_name, result='pass'/'fail', reason_code=evidence string, overridden=False). `deposits` INSERT — from `_extract_plan_required_deposits()` + agent-declared deposits: (step_id, declared_path, type='plan_required'/'agent_declared', landed=resolved_exists_bool). `commits` INSERT — from worktree `git log` at teardown (see Transition 5). |

#### Transition 4: VERDICT REQUEST WRITTEN

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:543 (mid-plan pause), :639 (final-step pause), :453 (worktree-creation failure), :670 (auto-close teardown failure) — all call `verdict.post_verdict_request()` |
| **Data in hand** | plan_id, step_number, pause_reason code, gate_result, total_steps, precondition_failure flag |
| **Lifecycle DB writes** | `steps` UPDATE (status='awaiting_verdict'). `verdicts` INSERT (plan_id, step_number, outcome=NULL (pending), pause_reason_code, verdict_file_ref=filepath). |

#### Transition 5: VERDICT CONSUMED

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:1410-1506 (`_consume_verdicts` inner loop) |
| **Data in hand** | plan_id (derive from slug→id lookup), step_number, verdict outcome ('continue'/'stop'), reason text, gate_result_from_request |
| **Lifecycle DB writes** | `verdicts` UPDATE (outcome='continue'/'stop', decided_by='ceo', disposition_summary=reason text). `plans` UPDATE (lifecycle_state transitions: 'awaiting_verdict' → 'in_progress' on continue, 'awaiting_verdict' → 'halted' on stop, 'awaiting_verdict' → 'closed' on continue-to-done). |

#### Transition 6: TEARDOWN / LAND

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:957-1088 (`_teardown_worktree`) |
| **Data in hand** | project_path, wt_path, slug (→ plan_id), commit_shas from `git log` at :1019 |
| **Lifecycle DB writes** | `commits` INSERT — one row per SHA: (step_id, repo=project_path basename, sha, message_ref=NULL). Note: commit messages are in git, not warehoused. |

#### Transition 7: CLOSE (Done/ or halted-)

| Attribute | Value |
|---|---|
| **Current code location** | bellows.py:677-688 (auto-close), :1471-1478 (continue-to-done), :1442-1448/:1498-1504 (halted) |
| **Data in hand** | plan_id, terminal outcome ('auto_closed', 'continue_to_done', 'halted'), total_cost (for auto-close) |
| **Lifecycle DB writes** | `plans` UPDATE (lifecycle_state='closed' or 'halted', closed_at). |

### 3.3 `record_run` — Extension vs. Net-New

`record_run()` (bellows.py:275-304) currently writes to `bellows.db` `runs` table — the **operational** DB. It is a single write path called at 5 sites: :471, :547, :569, :643 (and once more in `_consume_verdicts` at :547 via the VerdictPending status write).

**Decision: the lifecycle DB writes are NET-NEW call sites**, not extensions of `record_run()`. Reasons:

1. `record_run()` writes to the operational DB (`bellows.db`) which serves daemon-internal seen-tracking and orphan detection. The lifecycle DB is a separate file with a different schema for audit/reporting.
2. The lifecycle DB write surface is multi-table (plans, steps, commits, deposits, verdicts, gate_events) vs. `record_run()`'s single-table INSERT.
3. The transition granularity differs: `record_run()` fires at step completion; the lifecycle DB fires at claim, step start, step end, verdict request, verdict consumed, teardown, and close.

**Implementation:** A new `lifecycle.py` module with a `LifecycleDB` class providing typed methods: `mint_and_claim()`, `step_started()`, `step_completed()`, `verdict_requested()`, `verdict_consumed()`, `commits_landed()`, `plan_closed()`. Each method opens a connection, executes the write, commits, and closes (SQLite WAL mode for concurrent reads).

### 3.4 Proposed DDL (Core Tables)

```sql
-- lifecycle.db

CREATE TABLE id_sequence (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    next_id INTEGER NOT NULL DEFAULT 1
);
INSERT INTO id_sequence (id, next_id) VALUES (1, 1);

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
    deposit_placeholder_name TEXT,   -- original Planner deposit filename (for crash recovery)
    created_at TEXT NOT NULL,        -- ISO 8601
    closed_at TEXT                   -- ISO 8601, NULL while open
);

CREATE TABLE diagnostic_meta (
    plan_id INTEGER PRIMARY KEY REFERENCES plans(id),
    scope TEXT,
    hypothesis TEXT,
    findings_deposit_ref TEXT        -- path pointer to deposit
);

CREATE TABLE executable_meta (
    plan_id INTEGER PRIMARY KEY REFERENCES plans(id),
    test_scope TEXT,
    files_changed_count INTEGER
);

CREATE TABLE derivations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    executable_id INTEGER NOT NULL REFERENCES plans(id),
    diagnostic_id INTEGER NOT NULL REFERENCES plans(id),
    UNIQUE(executable_id, diagnostic_id)
);

CREATE TABLE steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    step_number INTEGER NOT NULL,
    role TEXT,                        -- SA, DEV, QA, or NULL
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','running','awaiting_verdict','complete')),
    step_started_at TEXT,
    step_ended_at TEXT,
    cost_usd REAL,
    turns INTEGER,
    duration_s REAL,
    log_ref TEXT,                     -- path to step JSON log
    UNIQUE(plan_id, step_number)
);

CREATE TABLE commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES steps(id),
    repo TEXT NOT NULL,
    sha TEXT NOT NULL,
    message_ref TEXT                  -- NULL; message is in git
);

CREATE TABLE deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES steps(id),
    declared_path TEXT NOT NULL,
    type TEXT,                        -- 'plan_required', 'agent_declared', 'frontmatter'
    landed INTEGER NOT NULL DEFAULT 0 -- boolean: 1 if file exists post-step
);

CREATE TABLE verdicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    step_number INTEGER NOT NULL,
    outcome TEXT,                     -- 'continue', 'stop', NULL (pending)
    pause_reason_code TEXT,
    decided_by TEXT,                  -- 'ceo', 'auto_close'
    verdict_file_ref TEXT,
    disposition_summary TEXT
);

CREATE TABLE gate_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES steps(id),
    gate_name TEXT NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('pass', 'fail')),
    reason_code TEXT,
    overridden INTEGER NOT NULL DEFAULT 0,
    override_ref TEXT
);
```

This conforms to the coverage map schema (pointers and small attributes only — no content columns). `gate_events` is core, not deferred.

---

## Section 4 — Commit-Message Id-Tagging Mechanism

### 4.1 Agent-Authored Commits (in worktree)

Agent commits happen inside the worktree during step execution. The agent is launched by `runner.run_step()` (runner.py:34-286) with a `prompt` string assembled by `run_plan()` at bellows.py:431-438 (first step) and :553 (subsequent steps).

**Assembly point:** bellows.py:431-438:

```python
if is_diagnostic:
    bootstrap_prompt = f"Read the diagnostic at {shadow_prompt_path}. Execute it fully ..."
elif resume_step is not None:
    bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {resume_step}. ..."
else:
    bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step 1 ONLY. ..."
```

And bellows.py:553:

```python
default_next_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {current_step + 1}."
```

**Mechanism:** Inject the plan id into the prompt text so the agent's commit messages naturally include it. The prompt already references the plan file — append an instruction:

```python
bootstrap_prompt += f" Tag all commits with [{plan_id}] in the commit message."
```

The agent's `BELLOWS_AGENT_SYSTEM_PROMPT` at runner.py:24 is another injection point but it's static (compiled at import time). The bootstrap prompt is per-plan and already carries plan-specific context, so it's the correct injection site.

**No commit rewriting or amending is needed.** The id is injected into the prompt BEFORE the agent runs; the agent naturally includes it in commit messages as part of its instructions.

### 4.2 Daemon-Authored Commits

Two daemon-authored commit sites:

**(a) Auto-stage deposit commit** (bellows.py:943-953):

```python
result = subprocess.run(
    ["git", "--no-pager", "commit", "-m",
     "bellows: auto-stage declared deposits before teardown"],
    cwd=wt_path, ...
)
```

**Fix:** Include the plan id in the message:

```python
f"bellows: auto-stage declared deposits before teardown [{plan_id}]"
```

**(b) Teardown merge commit** (bellows.py:1049-1051):

```python
result = subprocess.run(
    ["git", "--no-pager", "merge", "--no-ff", "--no-edit", branch_name],
    cwd=project_path, ...
)
```

The `--no-edit` flag uses git's auto-generated merge message (`Merge branch 'bellows-wt/142'`). The branch name already contains the slug/id, so the merge message inherently includes it. For consistency with the `[<id>]` convention, use `--message` instead of `--no-edit`:

```python
f"Merge branch '{branch_name}' [{plan_id}]"
```

The `--ff-only` path (bellows.py:1043-1046) produces no merge commit (fast-forward), so no message to tag. The agent's individual commits already carry `[<id>]`.

---

## Section 5 — Dual-Format Tolerance + Date-Rollover Bug

### 5.1 Parse Sites Keyed on Legacy Naming

#### `slug_for()` — bellows.py:80

```python
s = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', s)
```

**Classification: must accept both formats.** Used for log display across all plan states including historical. The date-strip regex is harmless on id-only names (no match, `s` unchanged). **No edit required.**

#### `slug_from_path()` — verdict.py:86-87

```python
for prefix in ("in-progress-", "verdict-pending-", "executable-", "diagnostic-"):
    if basename.startswith(prefix):
        basename = basename[len(prefix):]
```

**Classification: must accept both formats.** Used everywhere (verdict filenames, seen-cache, cleanup). Legacy names produce `foo-bar-2026-06-10`, new names produce `142`. Prefix stripping is format-agnostic. **No edit required.**

#### `is_runnable_plan()` — bellows.py:1144

```python
re.match(r"^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$", filename)
```

**Classification: must accept both formats.** `.*` matches both `foo-bar-2026-06-10` and `142`. **No edit required.**

#### `_consume_verdicts` regex — bellows.py:1363

```python
re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
```

**Classification: must accept both formats.** `.+` greedily matches both legacy slugs (e.g., `executable-foo-bar-2026-06-10`) and new slugs (`142`). **No edit required.**

#### `_consume_verdicts` prefix stripping — bellows.py:1373-1377

```python
for prefix in ("diagnostic-", "executable-"):
    if lookup_slug.startswith(prefix):
        lookup_slug = lookup_slug[len(prefix):]
```

**Classification: must accept both formats.** For new-format verdicts, the slug is `142` (type prefix was never part of the slug from `slug_from_path()`). But for legacy verdicts, the Planner may have written `verdict-executable-foo-bar-2026-06-10-step-1.md`, where the regex captures `executable-foo-bar-2026-06-10`. The prefix strip then produces `foo-bar-2026-06-10` for lookup. **No edit required** — new-format names pass through harmlessly.

#### Orphan-guard regex — bellows.py:1577

```python
re.match(r"^verdict-request-(.+)-step-\d+\.md$", pf)
```

**Classification: must accept both formats.** Same as verdict regex — `.+` matches both. **No edit required.**

#### `_perform_startup_sweep` active_slugs — bellows.py:1564-1572

```python
active_slugs.add(verdict.slug_from_path(stripped))
```

**Classification: must accept both formats.** `slug_from_path` handles both. **No edit required.**

#### Stale verdict scan — bellows.py:1521-1538

```python
if plan_slug in dname   # Done/ scan
if dname.startswith("halted-") and plan_slug in dname  # halted scan
```

**Classification: must accept both formats AND must be fixed.** Substring match is buggy for numeric slugs (Section 1.18). **Edit required** — both legacy and new-format names need exact slug extraction and comparison.

#### `plan_slug in pname` — bellows.py:1424

**Classification: must accept both formats AND must be fixed.** Same substring bug. **Edit required.**

### 5.2 Confirmation: No Code Re-Parses Historical Done/ or halted- in a Breaking Way

The only sites that scan Done/ or halted- are:

1. **Stale verdict detection** (bellows.py:1521-1538): iterates `os.listdir(done_dir)` and checks `plan_slug in dname`. This touches historical filenames. With the substring fix (exact comparison), both formats work.
2. **Mode A detection** (bellows.py:481-488, :577-588): checks `os.path.exists(done_check)` where `done_check = os.path.join(plan_dir, "Done", base_filename)`. This only checks for the current plan's own name — never iterates historical files. **No issue.**
3. **`_check_queue_drain`** (bellows.py:1266-1285): scans for `verdict-pending-` prefixed files in decisions/. Does not touch Done/ or halted-. **No issue.**

**Confirmed: no code path re-parses historical Done/, halted-, or resolved-verdict filenames in a way that breaks when new-format names appear beside them.**

### 5.3 Date-Rollover `scope_check` Bug — Location and Kill

**The bug:** `_gate_scope_check` at gates.py:721 performs substring matching:

```python
if fpath in union_text or basename in union_text:
    continue
```

When a plan's Deposits block specifies a deposit path with a date suffix (e.g., `knowledge/architecture/foo-2026-06-10.md`) but the agent creates the file with the current date (e.g., `foo-2026-06-11.md` after midnight), the substring match fails. The file is flagged as out-of-scope despite being the intended deposit.

**The kill:** With id-only naming, the Planner authors deposit paths without dates (the date leaves filenames and becomes a DB column per the coverage map). The Deposits block says `knowledge/architecture/foo-blueprint.md`, the agent creates `knowledge/architecture/foo-blueprint.md`, and the substring match succeeds. **The structural precondition for the bug — a date literal in the path that can change between authoring and execution — is eliminated.**

**File:line:** gates.py:721 (the match site), gates.py:697 (`_gate_scope_check` entry). The bug is not in the scope_check code per se — it's in the naming convention that puts dates in filenames. The fix is the convention change, not a code change at this site.

---

## Section 6 — Layer Impact + Executable Hand-Off

### 6.1 Layer Impact

**Affected layer: Layer 1 only.** The lifecycle DB is a mechanical byproduct of plan execution — it records what happened (id, state transitions, SHAs, gate results) without making any qualitative judgment. The id-minting and filename change are naming conventions, not domain logic. The Layer 1 / Layer 3 boundary remains crisp: Bellows dispatches and records, the Planner judges.

### 6.2 Files Touched by Executables

| File | Changes |
|---|---|
| `bellows.py` | Id mint at claim, id-canonical rename, lifecycle DB writes at all 7 transition boundaries, commit-message id injection in prompts, fix substring match bugs (1.14, 1.18), pass plan_id through `run_plan()` and `_teardown_worktree()` |
| `lifecycle.py` | **NEW** — LifecycleDB class with DDL migration + typed write methods |
| `bellows_root.py` | No change (already provides the root resolver) |
| `verdict.py` | Minor: `post_verdict_request` gains `plan_id` parameter for verdict_file_ref linkage; `log_to_ledger` gains optional `plan_id` |
| `runner.py` | No structural change — prompt assembly is in `bellows.py` |
| `gates.py` | No change (receives data, doesn't write lifecycle DB) |
| `validators.py` | No change (filename-agnostic) |
| `planner.py` | No change (Planner deposits use placeholder names; claim-rename is Bellows's responsibility) |

### 6.3 Daemon Restart Requirement

**Yes — daemon restart required.** The lifecycle DB migration runs at startup (like `migrate_db()` at bellows.py:159). The id counter starts at 1. Plans in-flight at restart will not have lifecycle DB rows — they were claimed under the legacy regime. The startup sweep should detect `in-progress-*` and `verdict-pending-*` plans without lifecycle DB rows and create retroactive entries (best-effort, with `created_at` from file mtime).

### 6.4 Sequencing Constraint: The Implementing Executable Itself

The implementing executable will be **deposited, claimed, and executed under the LEGACY naming convention** by the pre-fix daemon. This means:

- The executable's own filename will be `executable-<descriptive-slug>-YYYY-MM-DD.md` (legacy format)
- Its verdict filenames will be `verdict-request-<slug>-step-N.md` with a descriptive slug
- Its worktree branch will be `bellows-wt/<slug>` with a descriptive slug
- The Done/ filing will use the legacy name

**The first id-native plan** will be the first plan deposited AFTER the daemon is restarted with the new code. The executable's own legacy-format artifacts will coexist with future id-format artifacts in Done/, and the dual-format tolerance (Section 5) ensures both are handled correctly.

### 6.5 Recommended Executable Split

**Two executables, with dependency:**

1. **Executable A: Id-threading + filename change** — Mint id at claim, rename mechanics, fix substring bugs, dual-format tolerance, prompt injection for commit-message tagging. Ships first.
2. **Executable B: Lifecycle DB writes** — `lifecycle.py` module, DDL, write calls at all 7 transition boundaries. Ships second, depends on A (needs the plan_id from the mint).

**Rationale:** A is the riskier change (modifies the claim path, the load-bearing filename contract, and the verdict consumption matching). B is additive (new module, new write calls, no existing behavior changes). Shipping A first lets us verify the id-threading in production before adding the DB write surface. B can be rolled back independently if a schema issue is found.

**Dependency direction:** B depends on A. B cannot write a `plan_id` to the lifecycle DB without A having minted it. A is independently valuable (fixes the substring bugs, eliminates the date-rollover scope_check class, and produces id-keyed filenames even without the DB).

### 6.6 Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| No monotonic id | Plans identified by descriptive slug + date | Global-monotonic integer id minted at claim | New: lifecycle.py `mint_and_claim()`, bellows.py claim path edit |
| Slug-based filenames | `diagnostic-foo-bar-2026-06-10.md` | `diagnostic-142.md` | bellows.py:411 claim rename, Planner deposit convention |
| No lifecycle DB | `record_run()` writes flat operational row to bellows.db | Multi-table lifecycle.db written at every transition | New: lifecycle.py module + 7 call sites in bellows.py |
| Substring match bug (verdict consumption) | bellows.py:1424 `plan_slug in pname` | Exact slug comparison | bellows.py edit |
| Substring match bug (stale verdict scan) | bellows.py:1521-1538 `plan_slug in dname` | Exact slug comparison | bellows.py edit |
| No commit id-tagging | Commit messages have no plan linkage | `[<id>]` in agent prompts + daemon commit messages | bellows.py:431-438, :553, :943, :1049 |
| Date-rollover scope_check FP | Date in filenames can mismatch between authoring and execution (gates.py:721) | No dates in filenames — mismatch structurally impossible | Convention change (no code edit at gates.py:721) |
| Crash recovery for half-claimed plans | No mechanism — if daemon crashes between rename and run, plan is stranded | `plans.lifecycle_state='claimed'` + `deposit_placeholder_name` column | New: startup recovery scan in bellows.py |
| Verdict filenames not id-keyed | `verdict-request-<slug>-step-N.md` with descriptive slug | `verdict-request-<id>-step-N.md` | Flows from slug_from_path() producing the id |
| No live status | Plan state requires filesystem scan | `plans.lifecycle_state` + `steps.status` columns, NULL `closed_at` = in-flight | New: lifecycle.db schema |

---

## Section 7 — Verification Blocks

### Rule 39 Verification Triples

```
(claim, query, expected_output)
```

#### V1 — slug_from_path produces date-bearing slug

```
Claim:    verdict.slug_from_path("diagnostic-foo-bar-2026-06-10.md") includes the date
Query:    python3 -c "import verdict; print(verdict.slug_from_path('diagnostic-foo-bar-2026-06-10.md'))"
Expected: foo-bar-2026-06-10
```

#### V2 — slug_for strips the date

```
Claim:    bellows.slug_for("in-progress-diagnostic-foo-bar-2026-06-10.md") strips the trailing date
Query:    python3 -c "import bellows; print(bellows.slug_for('in-progress-diagnostic-foo-bar-2026-06-10.md'))"
Expected: diagnostic-foo-bar
```

#### V3 — is_runnable_plan accepts draft placeholder

```
Claim:    bellows.is_runnable_plan("diagnostic-draft-143022.md") returns True
Query:    python3 -c "import bellows; print(bellows.is_runnable_plan('diagnostic-draft-143022.md'))"
Expected: True
```

#### V4 — is_runnable_plan accepts id-only name

```
Claim:    bellows.is_runnable_plan("diagnostic-142.md") returns True
Query:    python3 -c "import bellows; print(bellows.is_runnable_plan('diagnostic-142.md'))"
Expected: True
```

#### V5 — plan_slug in pname substring false positive

```
Claim:    "142" in "verdict-pending-diagnostic-1423.md" is True (the substring bug)
Query:    python3 -c "print('142' in 'verdict-pending-diagnostic-1423.md')"
Expected: True
```

#### V6 — claim-path insertion point (validate_at_claim before rename)

```
Claim:    validate_at_claim is called at bellows.py:396, the in-progress rename is at bellows.py:411
Query:    grep -n "validate_at_claim\|shutil.move.*inprogress" bellows.py | head -5
Expected: Lines showing validate_at_claim at ~396, shutil.move at ~411
```

#### V7 — record_run writes to bellows.db (operational), not lifecycle

```
Claim:    record_run connects to DB_PATH which is bellows.db, not lifecycle.db
Query:    grep -n "DB_PATH\|record_run" bellows.py | head -10
Expected: DB_PATH = .../bellows.db (line ~24), record_run receives db_path parameter
```

#### V8 — date-rollover bug site at scope_check substring match

```
Claim:    _gate_scope_check uses substring match at gates.py:721
Query:    sed -n '720,722p' gates.py
Expected: "if fpath in union_text or basename in union_text:"
```

#### V9 — _teardown_worktree constructs branch name from slug

```
Claim:    _teardown_worktree uses f"bellows-wt/{slug}" at bellows.py:984
Query:    grep -n 'bellows-wt/' bellows.py
Expected: Line ~984 showing branch_name = f"bellows-wt/{slug}"
```

#### V10 — runner.py uses resolve_bellows_root, not Path(__file__)

```
Claim:    runner.py resolves BELLOWS_ROOT via the marker-walk-up helper at line 21
Query:    grep -n "BELLOWS_ROOT\|resolve_bellows_root" runner.py | head -5
Expected: Line ~21: BELLOWS_ROOT = resolve_bellows_root()
```

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a 7-section blueprint covering: (1) complete filename/slug consumer census across all 6 core modules + dispatch-validator with 27 enumerated sites, identifying 2 edit-required substring-match bugs and the date-rollover scope_check kill; (2) id mint mechanics with crash-window recovery; (3) lifecycle DB write surface mapped to 7 transition boundaries with proposed DDL; (4) commit-message id-tagging injection points; (5) dual-format tolerance classification for every legacy parse site; (6) layer impact analysis, gap assessment table, and recommended 2-executable split; (7) 10 verification triples for load-bearing facts.

### Files Deposited
- `bellows/knowledge/architecture/lifecycle-db-id-threading-blueprint-2026-06-11.md` — this blueprint

### Files Created or Modified (Code)
- None (design diagnostic only — no code edits)

### Decisions Made
- Lifecycle DB writes are net-new call sites, not extensions of `record_run()` (Section 3.3)
- Recommended 2-executable split: A (id-threading) ships before B (DB writes) (Section 6.5)
- Deposit placeholder convention: `<type>-draft-<HHMMSS>.md` (Section 2.5)
- `lifecycle.py` as new module with `LifecycleDB` class (Section 3.3)
- DB path resolves via `resolve_bellows_root()` marker-walk-up, not `Path(__file__).parent` (Section 3.1)

### Flags for CEO
- **Substring match bugs** (1.14, 1.18): `plan_slug in pname`/`plan_slug in dname` will false-match with numeric ids. These are latent bugs that become active the moment id-only names ship. The implementing executable must fix them in the same PR as the id-threading change.
- **Planner convention change required**: The Planner must adopt the `<type>-draft-<HHMMSS>.md` placeholder convention. PLANNER_TEMPLATE.md needs a documentation update (deferred per specialist operating procedure until step-persistence and watcher-reliability BACKLOG items are resolved, but the convention must be communicated to the Planner before the daemon restart).

### Flags for Next Step
- The implementing executable(s) should re-verify V1-V10 at edit time before modifying each site
- The DDL in Section 3.4 is the proposed schema — CEO review before implementation
- The `derivations` table requires the executable to parse "implements diagnostic Pxxxx" citations from plan headers — the Planner must adopt this citation convention
