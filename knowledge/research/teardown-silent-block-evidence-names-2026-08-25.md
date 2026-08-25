# Diagnostic: the silent teardown-merge block + shared QA-evidence names

**Date:** 2026-08-25 | **Plan:** 521 | **Measured against:** bellows main `c2b72ec`, daemon PID 26078

---

## Pin Re-Derivation Table

All pins re-derived 2026-08-25 against `c2b72ec`. Where a pin's value differs from the authoring-session value, the re-derived value is stated and supersedes.

| Pin | Authoring Value | Re-Derived Value | Probe |
|-----|----------------|------------------|-------|
| P1 | bellows.py:1114-1116 (while-loop) and :1241-1243 (final-step) — catch sites call NO `_log` | **CONFIRMED.** :1114-1116 appends failure + sets `_pause_reason`, no `_log`. :1241-1243 identical. Contrast :1272-1274 (auto-close) which calls `_log("ERROR", ...)`. Park at :766-768 calls `_log("WARN", ...)` — records in terminal log but NOT in lifecycle DB. | `grep -n "WorktreeTeardownError" bellows.py` yields 4 catch sites: :767, :1114, :1241, :1272. Only :1272 and :768 call `_log`. |
| P2 | `lifecycle.record_gate_events` at :1210 runs BEFORE final-step teardown at :1238 | **CONFIRMED.** While-loop path: `record_gate_events` at :1080, teardown at :1111. Final-step path: `record_gate_events` at :1210, teardown at :1238. Both record BEFORE teardown runs. step_id 921 (520's step 2): 7 all-pass gate_events rows, zero `worktree_teardown` rows. Verdicts row 910 carries `pause_reason_code=gate_failure`. | `sqlite3 lifecycle.db "SELECT gate_name, result FROM gate_events WHERE step_id=921"` → 7 pass rows (receipt_status, no_errors, no_permission_denials, deposit_exists, scope_check, rule_20_self_check, rule_22_verification). Zero `worktree_teardown` rows. |
| P3 | 520's actual refusal in `verdicts/ledger.jsonl` 2026-08-25T08:56:34 | **CONFIRMED.** Ledger line 1412: `"verdict": "continue-blocked-worktree-teardown"`, evidence: `"merge conflict on bellows-wt/520 for slug 520: error: Your local changes to the following files would be overwritten by merge: knowledge/research/pytest_full.txt"`. Terminal log: `08:54:24` gates pass → `08:54:25` PAUSE → `08:56:34` REJECTED. No merge-time log line between 08:54:24 and 08:54:25. | Terminal log lines 246-250; ledger.jsonl line 1412. |
| P4 | 516, 518, 520 all declare `knowledge/research/pytest_full.txt` | **CONFIRMED + EXTENDED.** 513, 514, 516, 518, 520 all declare the same flat path. `git log --oneline -- knowledge/research/pytest_full.txt` returns 5 commits (8375058, d3f2b04, b379311, 87a08d7, d1b99c6) all rewriting the same file. | `grep -n "pytest_full" knowledge/decisions/Done/executable-{516,518,520}.md` + `knowledge/decisions/halted-executable-513.md` + `knowledge/decisions/Done/executable-514.md`. |
| P5 | 50+ per-plan evidence dirs | **CONFIRMED: 67 per-plan evidence files** across 239 evidence directories at `knowledge/qa/evidence/<slug>/pytest_full.txt`; plus the suffixed `knowledge/research/pytest_full_513_red.txt`. | `find knowledge/qa/evidence -name "pytest_full*.txt" -print \| wc -l` → 67. `ls knowledge/research/pytest_full_513_red.txt` → EXISTS. `ls knowledge/research/pytest_full.txt` → EXISTS. |
| P6 | Precheck shipped 6252f8c7, extended 2153fc15, REMOVED by 46505bcc | **CONFIRMED.** `git log --oneline -S "worktree_teardown_dirty_tree" -- bellows.py` → 3 commits (6252f8c7, 2153fc15, 46505bcc). Absence today: `grep -n "porcelain" bellows.py` → only :1546/:1549 (auto-stage site). Nothing in `_teardown_worktree` :1855-1990. | Positive control: `:1546` `git status --porcelain` exists in `_auto_stage_deposits`. Negative: zero matches in `_teardown_worktree`. |
| P7 | Gap-1b guard at bellows.py:2700-2707 | **CONFIRMED at :2699-2713.** `if any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", []))`. Fires by reading `gate_result_from_request` (the failures list from the verdict-request file), NOT from gate_events DB rows. Separately, the recheck at :2533-2537 detects `worktree_teardown` in the failure list and short-circuits the override check, returning False (accept the verdict) — then the main continue branch hits the Gap-1b guard at :2699. | `grep -n "worktree_teardown" bellows.py` yields :1116, :1243, :1276, :1959, :2533, :2703. The continue branch reads failures from the verdict-request file's JSON blob. |
| P8 | Plan ids minted at claim time | **CONFIRMED.** Terminal log line 201: `08:26:04 [INFO] [executable-520] minted id 520 — renamed to in-progress-executable-520.md`. Receipts naming precedent: `tools/deposit_receipt.py:97` → `receipt-{slug}-{session_id}-{hash12}.json` — keyed by SLUG, not by id. At plan-authoring time the slug is known but the id is not yet minted. | Terminal log line 201; `deposit_receipt.py` line 97. |

---

## D-1 — The 520 Reconstruction

### Timeline (step 2 only — step 1 completed normally)

| Time | Event | Source |
|------|-------|--------|
| 08:26:04 | Plan claimed: `minted id 520` | Terminal log :201 |
| 08:32:15 | Step 1 auto-stage: 5 deposits committed (cf4c694 on bellows-wt/520) | Terminal log :211-216 |
| 08:43:27 | Step 2 started (continue verdict from step 1, overridden `no_permission_denials` gate) | Terminal log :222-227 |
| 08:54:10 | Step 2 agent commits QA deposits (d1b99c6 on bellows-wt/520), including `knowledge/research/pytest_full.txt` | `git log --format="%h %ci" d1b99c6` |
| 08:54:24 | Gates pass: `passed=True, failures=0 (none), files_changed=2` | Terminal log :246 |
| 08:54:24 | `lifecycle.record_gate_events(921, gate_result)` — 7 all-pass rows written | lifecycle.db: gate_events ids 6467-6473 |
| 08:54:25 | `_teardown_worktree` called at :1238 (final-step pause path) | Inferred from PAUSE timestamp |
| 08:54:25 | **TEARDOWN FAILS:** `git merge --ff-only bellows-wt/520` returns non-zero; fallback `git merge --no-ff bellows-wt/520` also fails: `Your local changes to the following files would be overwritten by merge: knowledge/research/pytest_full.txt` | Ledger line 1412 evidence field |
| 08:54:25 | Catch at :1241-1243: `_pause_reason = "gate_failure"`, failure appended to `gate_result["failures"]` | Code path |
| 08:54:25 | Verdict request posted with `pause_reason_code=gate_failure` and the teardown failure in the failures list | verdicts row 910, ledger line 1412 |
| 08:54:25 | `⏸️ step 2 — waiting for CEO verdict` | Terminal log :247 |
| 08:56:34 | Continue verdict received; recheck at :2533 detects worktree_teardown, passes through to Gap-1b guard at :2699 | Ledger line 1412 |
| 08:56:34 | **Gap-1b REJECTS:** `continue verdict REJECTED — prior step's worktree_teardown failure uncleared` | Terminal log :250 |
| 08:56:34 | Plan routed to `halted-executable-520.md` | Terminal log :251 |

### Channel-by-channel asymmetry table

| Channel | Planner reads first? | Teardown failure appeared? | When? | Form |
|---------|---------------------|---------------------------|-------|------|
| **Terminal log** (`bellows-2026-08-25.log`) | **YES — primary** | **NO** | — | PAUSE line at :247 reads identically to a normal QA checkpoint. No ERROR line. No merge-time log line between gates-pass (08:54:24) and PAUSE (08:54:25). |
| **Lifecycle DB — gate_events** | **YES — primary** | **NO** | — | step_id 921 has 7 all-pass rows (ids 6467-6473). Zero `worktree_teardown` rows. The sequencing defect (P2) makes this structurally impossible. |
| **Lifecycle DB — verdicts** | Secondary | Partially | At verdict-request time | Row 910: `pause_reason_code=gate_failure`. The code is correct but ambiguous — any gate failure produces the same code. |
| **Lifecycle DB — steps** | Secondary | No | — | step_id 921: `status=complete`. Step end recorded BEFORE teardown; status not updated on failure. |
| **Verdict-request file** (`verdict-request-520-step-2.md`) | At verdict time | **YES** | 08:54:25 | Full evidence string including the merge error. This is the ONLY channel that carried the failure at pause time. |
| **Verdicts ledger** (`ledger.jsonl`) | At consumption | **YES** | 08:56:34 | Line 1412: `verdict=continue-blocked-worktree-teardown`. Written by the Gap-1b guard AFTER the continue verdict was rejected. |
| **Resolved verdict file** (`processed-verdict-520-step-2.md`) | At review | No (written before failure surfaced) | 08:56:34 | Contains the continue verdict text. No mention of teardown failure — written by the Planner before the failure was detectable. |
| **Git** | At recovery | **YES** | After manual R2 | d1b99c6 stranded on bellows-wt/520; landed at 7322cc9 by manual ff-merge. cf4c694 (auto-stage) also on the branch. |

**Conclusion:** The two channels a Planner reads first — the terminal log and the lifecycle DB gate_events — were exactly the silent ones. The failure was visible ONLY in the verdict-request file (a per-plan document consumed at verdict time, not during routine monitoring) and the ledger (written after the rejection, not at failure time).

### Proximate dirtier of `knowledge/research/pytest_full.txt`

The merge error reports uncommitted local changes to `knowledge/research/pytest_full.txt` on the main working tree at 08:54:25. Commit history shows 518's QA (87a08d7) was the last committed version on main (merged 2026-08-25 ~00:03). 520's worktree branched from main at 08:26:04 (after 87a08d7 was on main).

The proximate cause of the dirty state is **partially unrecoverable from available evidence**. The 8h20m window between 518's merge landing and 520's teardown (00:03 → 08:54) is long enough for multiple operations. The daemon's terminal log shows no file-write operations to that path on main between those times. The most likely explanations:

1. A Planner session or manual CLI operation wrote to the file on the main working tree without committing (e.g., a manual pytest run redirected there during session-65 work).
2. An intermediate plan's teardown left the file dirty (none of plans 517/519 declared this path, but an unrelated write could have touched it).
3. Git state left from 518's own merge (unlikely — 518's teardown completed successfully per the ledger).

The structural observation is more important than the specific dirtier: **any sequential collision on a shared deposit path creates this risk**. The shared filename means any plan that writes to the path (even successfully) leaves a state that blocks the next plan's teardown if the main working tree's copy diverges by even one character.

---

## D-2 — Catch-Site Census

### Four `_teardown_worktree` call sites

| # | Site | Line | Logs at failure? | Gains gate_events row? | Reaches verdict-request file? | Flips `gate_result["passed"]`? |
|---|------|------|-----------------|----------------------|------------------------------|-------------------------------|
| 1 | **Park** | :766-768 | **WARN** (`_log("WARN", ...)`) | **NO** — no `_lc_step_id` in scope (park function is outside `run_plan`); no `record_gate_events` call. | **NO** — park path does not post verdict requests. | N/A — park path does not use `gate_result`. |
| 2 | **While-loop pause** | :1110-1116 | **NO** — catch appends to `gate_result["failures"]` and sets `_pause_reason = "gate_failure"` only. No `_log` call. | **NO** — `lifecycle.record_gate_events` already ran at :1080 (P2 sequencing defect). The teardown failure is appended AFTER recording. | **YES** — the verdict request at :1122 includes the updated `gate_result` with the teardown failure. | **NO** — `gate_result["passed"]` is NOT set to False. |
| 3 | **Final-step pause** | :1237-1243 | **NO** — identical to site 2. Catch appends to `gate_result["failures"]` and sets `_pause_reason = "gate_failure"` only. No `_log` call. | **NO** — `lifecycle.record_gate_events` already ran at :1210 (P2 sequencing defect). The teardown failure is appended AFTER recording. | **YES** — the verdict request at :1249 includes the updated `gate_result` with the teardown failure. | **NO** — `gate_result["passed"]` is NOT set to False. |
| 4 | **Auto-close** | :1267-1287 | **YES** — `_log("ERROR", f"❌ worktree teardown failed on auto-close: {e}", ...)` at :1274. | **NO** — `record_gate_events` ran at :1210 before teardown. Same P2 sequencing issue. However, auto-close posts its OWN verdict request (:1283) and calls `lifecycle.record_verdict_request` (:1285), so the failure is tracked. | **YES** — dedicated verdict request at :1283. | **YES** — `gate_result["passed"] = False` at :1277. |

### Sequencing defect detail (P2)

The code structure in both the while-loop and final-step paths:

```
1. Step completes → gates.check() runs
2. lifecycle.record_gate_events(_lc_step_id, gate_result)  ← gate_events written HERE
3. Pause-condition check
4. _teardown_worktree() called                              ← failure happens HERE
5. except: append to gate_result["failures"]                ← too late for DB
```

The `record_gate_events` function at lifecycle.py:470 inserts one row per gate. Calling it again would duplicate all 7 standard-gate rows. The fix needs a targeted single-row insert.

### Recording fix shape for the executable

**At both pause-path catch sites (:1114-1116 and :1241-1243):**

1. **Add `_log("ERROR", ...)`** — mirror :1274's pattern:
   ```python
   _log("ERROR", f"❌ worktree teardown failed: {e}", slug=slug_for(plan_name))
   ```

2. **Add post-hoc gate_events write** — `_lc_step_id` is in scope at both sites (set at step start, used by `record_gate_events` earlier in the same scope). A new lifecycle helper is needed:
   ```python
   lifecycle.record_single_gate_event(
       _lc_step_id,
       gate_name="worktree_teardown",
       result="fail",
       reason_code=str(e)
   )
   ```
   This inserts ONE row without duplicating the 7 standard-gate rows already recorded. The function shape: a direct `INSERT INTO gate_events (step_id, gate_name, result, reason_code, overridden, override_ref) VALUES (?, ?, ?, ?, 0, NULL)` — identical to `record_gate_events`' failure-insert path (lifecycle.py:488-492) but without the surrounding loop.

3. **Flip `gate_result["passed"] = False`** — currently omitted at both pause-path sites. The auto-close site (:1277) does this. Without the flip, `gate_result["passed"]` remains True in the verdict-request's JSON blob, creating an inconsistency: the failures list contains the teardown failure, but `passed` says True. Add `gate_result["passed"] = False` at both sites.

**At the park path (:766-768):**

The park path's current posture is `_log("WARN", ...)` + silent swallow. The risk: commits on `bellows-wt/<slug>` are stranded, and when the parked plan resumes, `_create_worktree` at :836-846 deletes the old branch with `git branch -D`, destroying the unmerged commits. No record survives except the WARN line in the terminal log.

Recommendation: **upgrade to ERROR + record the failure**. The park function receives `plan_id` but not `_lc_step_id`; the step was never fully started (park happens before step execution). Two options:
- **(a)** Record the failure as a plan-level event (not step-level) — requires a new table or a sentinel step_id.
- **(b)** Do not park the plan; instead route to halted- so the worktree branch and its commits are preserved for manual R2 recovery. This is the safer option and mirrors the Gap-1b guard's behavior.

State for D-7: option (b) is recommended; the CEO decides.

**At the auto-close path (:1272-1277):**

Already logs ERROR and flips `gate_result["passed"]`. The ONLY gap is the same P2 sequencing issue: no gate_events row in the DB. Add the same `lifecycle.record_single_gate_event` call as the pause-path sites.

---

## D-3 — The Lost Precheck

### What 6252f8c7 shipped (2026-05-28)

Inserted a `(b2) Pre-cherry-pick dirty-tree check on main checkout` block inside `_teardown_worktree`, between the index.lock cleanup and the cherry-pick loop. The check:

```python
dt_result = subprocess.run(
    ["git", "--no-pager", "status", "--porcelain"],
    cwd=project_path, ...)
if dt_result.returncode == 0 and dt_result.stdout.strip():
    raise WorktreeTeardownError(
        "worktree_teardown_dirty_tree: local main has uncommitted changes ..."
    )
```

The error message included:
- Dirty file count and listing (truncated to 10 lines)
- Recovery commands: Sub-variant A (untracked artifact: `git add + commit`) and Sub-variant B (dirty bookkeeping file: `git add + commit`), then re-issue continue verdict
- Reference to LESSONS.md 2026-05-27

This was a pre-cherry-pick check on the `project_path` (main checkout), not the worktree. The CEO-approved design was from `Done/diagnostic-worktree-teardown-dirty-tree-precheck-v2-2026-05-27.md`:
- Scope: any uncommitted change (option 1a — conservative, false-positive cost is one CEO decision)
- Pause reason code: `worktree_teardown_dirty_tree`
- Recovery instructions: inline literal commands

### What 2153fc15 added (2026-06-04, Gap 1c)

Added `_retry_recoverable_teardown()` — called at verdict-consume time, BEFORE the Gap-1b halt guard. If all worktree_teardown failures contained the string `"worktree_teardown_dirty_tree"`, the function re-attempted teardown (by this time the operator has usually committed the dirty file). On success, cleared the worktree_teardown failures from `gate_result` so the normal continue/advance proceeded. On failure, left the failures for Gap-1b to halt.

### What 46505bcc removed (2026-06-06, merge-ff model)

Replaced the entire cherry-pick teardown with `git merge --ff-only` (primary) / `--no-ff` (fallback). Removed:
- The `(b2)` dirty-tree precheck (the `git status --porcelain` block)
- `_retry_recoverable_teardown()`
- `_LIFECYCLE_IGNORE_RE` and `_is_lifecycle_artifact()` (dead under merge semantics)

The rationale was sound: under the cherry-pick model, a dirty main tree caused the cherry-pick to abort with a confusing error, so the precheck gave a clear message. Under the merge model, git's own merge machinery handles the conflict — but as 520 proves, the merge's error message (`Your local changes would be overwritten`) is ALSO opaque when the cause is a shared deposit filename, and the merge still REFUSES when the working tree is dirty.

### Merge-model equivalent

The precheck for the merge model is structurally identical to the cherry-pick version but scoped to the specific failure mode:

```python
# In _teardown_worktree, after index.lock cleanup, BEFORE the merge attempt at :1942
dt_result = subprocess.run(
    ["git", "--no-pager", "status", "--porcelain"],
    cwd=project_path, capture_output=True, text=True, timeout=10,
)
if dt_result.returncode == 0 and dt_result.stdout.strip():
    dirty_lines = dt_result.stdout.strip().splitlines()
    raise WorktreeTeardownError(
        f"worktree_teardown_dirty_tree: main working tree has {len(dirty_lines)} "
        f"uncommitted file(s) that would block merge.\n"
        f"Dirty files:\n{chr(10).join(dirty_lines[:10])}\n"
        f"Recovery: commit or stash the dirty files, then re-issue continue verdict.\n"
        f"  cd {project_path}\n"
        f"  git add <file(s)> && git commit -m 'chore: commit dirty files before teardown'\n"
        f"Reference: LESSONS.md 2026-05-27 R2 recovery shape."
    )
```

**Predicate:** `git status --porcelain` on `project_path` (the main checkout, NOT the worktree) returns any output.

**Failure form:** Raises `WorktreeTeardownError` with a `worktree_teardown_dirty_tree` evidence string, which flows to the existing catch sites. With D-2's recording fix, this gains an ERROR log, a gate_events row, and correct `gate_result["passed"] = False`.

**Reuse from the May diagnostic:** The pause-message design (evidence string format, recovery commands, Sub-variant A/B distinction) from `Done/diagnostic-worktree-teardown-dirty-tree-precheck-v2-2026-05-27.md` Section 3 remains valid. The only obsolete part is the reference to cherry-pick mechanics — replace with merge mechanics. The `worktree_teardown_dirty_tree` pause-reason-code and the inline recovery commands are CEO-approved decisions that carry forward.

**Insertion point:** Between the index.lock cleanup (ending at :1938) and the merge attempt (starting at :1942) in `_teardown_worktree`.

**Interaction with Gap-1c retry:** The `_retry_recoverable_teardown` function was removed by 46505bcc. If reinstated, it would key on `"worktree_teardown_dirty_tree"` in the evidence string to decide whether re-attempt is safe. Under the merge model, a dirty-tree precheck failure IS retry-safe (if the operator commits the dirty file, the merge will succeed). A content-conflict merge failure is NOT retry-safe. The evidence string distinguishes these: precheck failures contain `worktree_teardown_dirty_tree`, content conflicts do not. Whether to reinstate Gap-1c is a D-7 fork.

---

## D-4 — The Evidence-Name Collision

### Census

**Plans declaring the flat name `knowledge/research/pytest_full.txt`:**

| Plan | Commit | Date | Commit Message |
|------|--------|------|----------------|
| 513 (halted) | 8375058 | 2026-08-24 15:45 | [513] qa: admission flip — full suite + evidence |
| 514 | d3f2b04 | 2026-08-24 16:18 | [514] qa: fixture corrective — suite green |
| 516 | b379311 | 2026-08-24 19:14 | [516] qa: E3 receipts — full suite + evidence |
| 518 | 87a08d7 | 2026-08-25 00:03 | [518] qa: E4 conditioning — full suite + evidence |
| 520 | d1b99c6 | 2026-08-25 08:54 | [520] qa: E5 keyed 3b — full suite + evidence |

All five commits rewrite the same `knowledge/research/pytest_full.txt` path. The file is a rolling overwrite — each plan's QA step deposits the full pytest suite output, replacing the previous plan's content.

**Historical norm:** 67 per-plan evidence files at `knowledge/qa/evidence/<slug>/pytest_full.txt` across 239 evidence directories. This is the PLANNER_TEMPLATE-prescribed convention (PLANNER_TEMPLATE.md:560): `[project]/knowledge/qa/evidence/<plan-slug>/<check-name>.txt`.

**Origin of the flat-name convention:** Plan 513 (`halted-executable-513.md`) is the first plan to declare `knowledge/research/pytest_full.txt` instead of the per-plan `knowledge/qa/evidence/<slug>/pytest_full.txt`. The flat name is NOT in PLANNER_TEMPLATE.md — the template prescribes the per-plan directory convention. The flat name is authoring drift: the E-family plans (513-520) were authored as a rapid clone chain for the E1-E5 arc, and the QA step template was cloned with the flat path rather than the slug-keyed path. Each subsequent plan (514, 516, 518, 520) inherited the flat name from its predecessor.

**Change site to stop propagation:** The flat name is authored into individual plan files, not generated by code or template. To stop the next clone from inheriting it: the Planner must author the slug-keyed path in new plans. No code change stops the propagation — it's a plan-authoring convention enforced by PLANNER_TEMPLATE.md Rule 18, which the E-family plans deviated from.

### Fix-shape options

#### Option (a): Slug-keyed flat file — `knowledge/research/pytest_full_<slug>.txt`

Example: `knowledge/research/pytest_full_e5-keyed-3b.txt`

| Gate | Interaction |
|------|-------------|
| `qa_test_result` | Scans declared `.txt` deposits. Resolves via `_resolve_deposit_path` in the worktree. Works — the file exists in the worktree at the slug-keyed path. **No change needed.** |
| `deposit_exists` | Resolves via `_resolve_deposit_path`. Works — file exists. **No change needed.** |
| `scope_check` | Checks `files_changed` against declared Scope paths. Works — the slug-keyed path appears in Scope. **No change needed.** |
| `_auto_stage_deposits` | Resolves via `_resolve_deposit_path` at :1542, then `git status --porcelain` and `git add` in the worktree. Works. **No change needed.** |

**Cost:** Minimal — pure plan-authoring change. Requires the slug to be known at plan-authoring time (it is — the Planner names it). Accumulates flat files in `knowledge/research/` but avoids cross-plan collision completely.

#### Option (b): Historical per-plan dir — `knowledge/qa/evidence/<slug>/pytest_full.txt`

Example: `knowledge/qa/evidence/e5-keyed-3b/pytest_full.txt`

| Gate | Interaction |
|------|-------------|
| `qa_test_result` | Scans declared `.txt` deposits. Resolves in the worktree. Works. **No change needed.** |
| `deposit_exists` | Works. **No change needed.** |
| `scope_check` | Works — directory paths are authorized by the 2026-05-28 directory-mention extension (gates.py scope_check). **No change needed.** |
| `_auto_stage_deposits` | Works. **No change needed.** |

**Cost:** Minimal — pure plan-authoring change, restores the PLANNER_TEMPLATE-prescribed convention. Creates a per-plan evidence directory (already the norm for 67+ historical plans).

#### Option (c): Id-keyed names — `knowledge/research/pytest_full_<id>.txt`

Example: `knowledge/research/pytest_full_520.txt`

Per P8: plan ids are minted at claim time, AFTER the plan is authored and deposited. At plan-authoring time, the id does not exist — the plan filename is a `draft-` or `ready-` placeholder. The daemon mints the id at claim and renames the file. An id-keyed evidence name cannot be authored into a plan unless the daemon rewrites Deposits/Scope paths at claim time.

**Cost:** Requires a new mechanism: daemon-side path rewriting at claim (scan Deposits/Scope blocks, replace `<id>` placeholder with the minted integer). This is a non-trivial new feature (~50-80 LOC) with its own test surface and failure modes.

| Gate | Interaction |
|------|-------------|
| All gates | Require the daemon to rewrite paths in the plan text AND in the worktree-local Deposits/Scope blocks before gates.check() runs. New failure mode: rewrite fails or is partial. |

### Recommendation

**Option (b)** — restore the PLANNER_TEMPLATE-prescribed per-plan evidence directory convention. Zero code changes. Zero new mechanisms. The historical convention exists precisely to prevent this class of collision. The E-family's flat name was authoring drift, not an intentional design departure.

If the CEO prefers option (a) (slug-keyed flat file) for its simplicity, it also works with zero code changes. The tradeoff: (a) accumulates files in `knowledge/research/`, (b) organizes them in per-plan directories matching the historical convention.

Option (c) is not recommended: the complexity of daemon-side path rewriting is disproportionate to the problem, and the slug-keyed alternatives solve it fully.

This recommendation is D-7's first fork if the trade-off is judged genuine.

---

## D-5 — The E4/Override Interaction

### Current flow

The E4 conditioning code path for continue verdicts with gate failures:

1. **Recheck** at :2531-2564: Reads `gate_result_from_request.get("failures", [])`.
2. **Worktree teardown short-circuit** at :2533-2537: If ANY failure has `gate == "worktree_teardown"`, records the verdict outcome and returns `False` (accept). This short-circuits the override check entirely — `get_overridden_gates_for_step` at :2539 never runs.
3. **Override filter** at :2539-2558: For non-teardown failures, checks `gate_events.overridden=1` rows. Surviving (unoverridden) failures → refuse. All overridden → accept.
4. **Gap-1b guard** at :2699-2713: In the main continue branch (AFTER recheck accepts), checks `gate_result.get("failures", [])` for `worktree_teardown`. If found → REJECT + route to halted-.

The Gap-1b guard reads the failures from the SAME source as the recheck (the verdict-request file's failure list), so the `worktree_teardown` entry is always present when the guard fires.

### What D-2's fix changes

If the executable lands teardown failures as real `gate_events` rows (via `lifecycle.record_single_gate_event`), then `clear_plan.py --override-gate` could be used to set `overridden=1` on a `worktree_teardown` row. The question: what would that mean?

**An override on `worktree_teardown` asserts: "this failure may be continued over."** But a teardown failure means **commits are not landed**. Continuing over it is exactly what Gap-1b exists to refuse — the plan would advance to the next step (or close) with stranded commits on the worktree branch, and no mechanism would ever land them.

### Current composition

The recheck's short-circuit at :2533-2537 **already excludes `worktree_teardown` from the override path.** When a teardown failure exists, the recheck accepts the verdict WITHOUT checking overrides, and the Gap-1b guard at :2699 blocks the continue. Even if someone runs `clear_plan.py --override-gate 520 2 worktree_teardown`, the recheck never consults the override — it short-circuits first.

This means `overridden=1` on a `worktree_teardown` gate_events row is **inert under the current code**: the recheck doesn't read it, and the Gap-1b guard doesn't read gate_events (it reads the request file's failures list).

### After D-2's fix

If the executable adds a `gate_events` row for teardown failures, the composition is unchanged:
- The recheck still short-circuits at :2533 before reaching the override check at :2539.
- The Gap-1b guard still reads the request file's failures, not gate_events.
- `clear_plan.py --override-gate` for `worktree_teardown` would insert an `overridden=1` row that nothing reads.

**The exclusion is structural, not explicit.** There is no explicit "exclude worktree_teardown from overridable gates" list. Instead, the short-circuit at :2533 makes the override path unreachable for teardown failures. This is correct behavior but implicit — a future refactor of the recheck could break it.

### E4 exclusion precedent

The recheck's short-circuit at :2533-2537 IS the exclusion. It was added as part of the Gap-1b implementation (the same commit that added :2699-2713). There is no separate "excluded gates" list in `clear_plan.py` or elsewhere.

### Recommendation

The current composition is safe. The executable should:

1. **Add a comment** at the short-circuit (:2533) noting that this implicitly excludes `worktree_teardown` from the override path, cross-referencing the Gap-1b guard.
2. **Optionally** add an explicit exclusion in `clear_plan.py --override-gate` that refuses to override `worktree_teardown` with a clear error message (`"worktree_teardown failures cannot be overridden — commits are not landed; use manual R2 recovery"`). This is defense-in-depth: even though the override would be inert, preventing the operator from setting it avoids confusion.
3. **Do NOT** make `worktree_teardown` overridable. The invariant (commits must be landed before advancing) is load-bearing.

---

## D-6 — Test Surface

### Follow-up executable tests

| # | Test | What it asserts | Fixture |
|---|------|----------------|---------|
| 1 | `test_pause_path_teardown_failure_logs_error` | Both pause-path catch sites (:1114-1116 and :1241-1243) emit `_log("ERROR", ...)` when teardown raises. | Inject `WorktreeTeardownError` at final-step pause teardown; assert ERROR appears in captured log. |
| 2 | `test_pause_path_teardown_failure_records_gate_event` | A `gate_events` row with `gate_name="worktree_teardown", result="fail"` is written to the lifecycle DB when teardown raises at a pause-path catch site. | Same fixture as #1; query `gate_events` for the step_id after the failure. |
| 3 | `test_pause_path_teardown_failure_flips_passed` | `gate_result["passed"]` is `False` after a teardown failure at a pause-path catch site. | Same fixture; inspect the verdict-request's gate_result JSON. |
| 4 | `test_park_path_teardown_failure_posture` | Park-path teardown failure routes to halted- (if option b chosen) OR logs ERROR and records appropriately. | Inject `WorktreeTeardownError` at park teardown; assert the plan is halted (or assert ERROR log + no silent swallow). |
| 5 | `test_dirty_tree_precheck_fires_before_merge` | When main working tree has uncommitted changes, `_teardown_worktree` raises `WorktreeTeardownError` with `worktree_teardown_dirty_tree` in evidence BEFORE attempting `git merge`. | Create a worktree with commits, dirty a file on main, call `_teardown_worktree`; assert the error message contains `worktree_teardown_dirty_tree` and no merge was attempted. |
| 6 | `test_clean_tree_precheck_proceeds_to_merge` | When main working tree is clean, `_teardown_worktree` proceeds to merge normally. | Create a worktree with commits, ensure main is clean, call `_teardown_worktree`; assert commits land on main. |
| 7 | `test_precheck_evidence_contains_recovery_commands` | The `WorktreeTeardownError` evidence string contains recovery instructions (commit/stash + re-issue continue). | Same as #5; assert evidence contains `"Recovery"` and the `cd` + `git add` commands. |
| 8 | `test_evidence_name_gate_interaction` | Whichever D-4 option is chosen: the slug-keyed evidence path passes `deposit_exists`, `scope_check`, `qa_test_result`, and `_auto_stage_deposits`. | Create a plan with the new evidence path convention; run gates.check(); assert no `deposit_exists` or `scope_check` failures. |
| 9 | `test_override_worktree_teardown_refused` | If the explicit `clear_plan.py` exclusion is added: `--override-gate worktree_teardown` returns an error. | Run `clear_plan.py --override-gate <plan> <step> worktree_teardown`; assert non-zero exit / error message. |

### Regression floor

Current suite count: **1363 tests collected**, measured 2026-08-25 (`python3 -m pytest tests/ --collect-only -q`). This matches 520's QA report (1363 passed, 0 failed). The executable's QA step should assert >= 1363 passed with zero new failures; the count grows by tests #1-#9 above (expect ~1372+).

---

## D-7 — Open Questions

### Fork 1: Evidence-name convention

D-4 recommends option (b) (per-plan evidence directory, the PLANNER_TEMPLATE-prescribed convention). If the CEO prefers option (a) (slug-keyed flat file), it works equally well with zero code changes. Option (c) (id-keyed) is not recommended. **Ruling needed: (a) or (b)?**

### Fork 2: Park-path teardown failure posture

D-2 identifies that the park path (:766-768) silently swallows teardown failures. Two options:
- **(a)** Route to halted- instead of parking (preserves commits on the worktree branch for manual R2 recovery; mirrors Gap-1b's behavior).
- **(b)** Log ERROR + leave the plan parked (simpler but risks commit loss if the plan resumes and `_create_worktree` deletes the old branch).

**Ruling needed: (a) or (b)?** Recommendation: (a).

### Fork 3: Gap-1c reinstatement

D-3 notes that `_retry_recoverable_teardown` was removed by 46505bcc. Under the merge model, a dirty-tree precheck failure IS retry-safe (the operator commits the dirty file, the merge succeeds on retry). **Should the executable reinstate Gap-1c for dirty-tree failures only?** Cost: ~30 LOC, reuses the evidence-string-keyed pattern from 2153fc15. Benefit: operator can commit the dirty file and re-issue continue without manual R2. Without it: every dirty-tree teardown failure requires manual R2 recovery (manual ff-merge + worktree removal).

**Ruling needed: reinstate or defer?**

### Fork 4: `clear_plan.py` explicit exclusion

D-5 recommends an explicit exclusion in `clear_plan.py` that refuses `--override-gate worktree_teardown`. The current implicit exclusion (recheck short-circuit at :2533) is correct but fragile. **Should the executable add the explicit exclusion?** Cost: ~10 LOC + 1 test.

**Ruling needed: add or defer?**

---

## Rule 27 Gap Table

Every change site the follow-up executable will touch:

| # | File | Line(s) | Change | Section |
|---|------|---------|--------|---------|
| G1 | bellows.py | :1114-1116 | Add `_log("ERROR", ...)` + `lifecycle.record_single_gate_event(...)` + `gate_result["passed"] = False` | D-2 |
| G2 | bellows.py | :1241-1243 | Add `_log("ERROR", ...)` + `lifecycle.record_single_gate_event(...)` + `gate_result["passed"] = False` | D-2 |
| G3 | bellows.py | :1272-1277 | Add `lifecycle.record_single_gate_event(...)` (already has `_log` and `passed` flip) | D-2 |
| G4 | bellows.py | :766-768 | Upgrade posture per D-7 Fork 2 ruling | D-2 |
| G5 | bellows.py | :1938-1942 | Insert dirty-tree precheck (`git status --porcelain` on `project_path`) before merge attempt | D-3 |
| G6 | lifecycle.py | new function | Add `record_single_gate_event(step_id, gate_name, result, reason_code)` | D-2 |
| G7 | bellows.py | :2533 | Add comment documenting the implicit override exclusion for `worktree_teardown` | D-5 |
| G8 | tools/clear_plan.py | override_gate() | Add explicit refusal for `worktree_teardown` (if D-7 Fork 4 approved) | D-5 |
| G9 | bellows.py | new function | Reinstate `_retry_recoverable_teardown` for dirty-tree-only failures (if D-7 Fork 3 approved) | D-3 |
| G10 | Plan authoring | N/A | Adopt slug-keyed evidence paths in new plans (no code change; Planner convention) | D-4 |
| G11 | tests/test_bellows.py | new tests | Tests #1-#9 from D-6 | D-6 |
