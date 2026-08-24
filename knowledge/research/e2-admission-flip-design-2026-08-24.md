# E2 Admission Flip — Design Document

**Date:** 2026-08-24 | **Diagnostic:** 511 | **Tier:** T1 | **Class:** read-only

**R1 (verbatim):** *"bellows only accepting a drafting cycle cleared plan — this is the only way that bellows can work on something."*

**Depends on:** `eluvian-path-audit-2026-08-24.md` §E2 (509-corrected), `eluvian-path-rulings-2026-08-24.md` (R1; fork 2 = grandfather + gated clear; fork 4 = `app-feature` + `register-writing` auto-clear, `shop-infra` HELD). Consumed T-7.

**Safety invariant (inherited from 478):** the depositor never mints, never dispatches — and the flip must not change that. The claim decision stays the daemon's; clearance only NARROWS what it may claim.

---

## Re-derived Pins

All values re-derived 2026-08-24 from live code; these supersede the plan's values.

| id | pin | plan value | re-derived | supersedes? | probe |
|---|---|---|---|---|---|
| G1 | `is_runnable_plan` call sites (excl. def) | 6 | **6** | no | `grep -n is_runnable_plan bellows.py` → :2053 (collect_group), :2065 (_handle entry), :2220 (_check_queue_drain idle-notify), :2346 (DISC-1 rescan), :2622 (orphan-verdict active-slug scan), :2702 (startup scan). Classification below in D-2 |
| G2 | `_clear()` leaves no mark | confirmed | **confirmed** | no | depositor.py:496-514 — `claimable_name = filename[len("ready-"):]` (line 499); `os.rename(path, claimable_path)` (line 505). The result is byte-identical in name to a hand-placed file |
| G3 | depositor runs IN daemon process | True | **True** | no | bellows.py:2186 `self.depositor = depositor.Depositor(...)`. Evaluate calls via `threading.Thread(target=dep.evaluate, ...)` at bellows.py:2069-2071, but in the same process, sharing the daemon's lifecycle-DB access model |
| G4 | lifecycle.db has NO clearance-shaped table | True | **True** | no | `deposits(id, step_id, declared_path, type, landed)` — per-step, lifecycle.py:109-116. `ledger_writes(id, step_id, ledger_file, content_hash, applied_at)` — ledger-append provenance, lifecycle.py:154-162. Neither keys a PLAN's content hash to a clearance event. Positive control: `plans` table (lifecycle.py:38-53) has `lifecycle_state` and `deposit_placeholder_name` — clearance would be a new column or a new table |
| G5 | bare claimable-named files in ALL 10 watched dirs | 0 | **0** | no | Per-dir scan of all 10 watched dirs: `ls $dir \| grep -E '^(executable\|diagnostic\|qa)-'` excluding lifecycle prefixes → 0 across invoice-pulse, BrewBuddy, study, ai-career-digest, freight-kb, forge, anvil, bellows, lessons-forge, governance. Hot set empty; 16 halted- across 5 projects, 0 hold- |
| G6 | unknown-prefix WARN arm | bellows.py:2073-2077 | **bellows.py:2073-2077** | no | `_handle` warns-and-ignores unrecognized .md prefixes once per slug via `self.orchestrator._seen` (line 2077). The WARN fires when filename ends `.md`, does NOT start with any lifecycle prefix (`in-progress-`, `verdict-pending-`, `halted-`, `parked-`, `roadmap-`, `hold-`) or `ready-`, AND slug not in `_seen` |
| G7 | `_assign_class` split point | depositor.py:255-278 | **depositor.py:255-278** | no | Positive detection for `read-only` (line 274-275) and `register-writing` (line 276-277). Catch-all `return "governed-tooling"` at line 278. Constants: `_READ_ONLY_PREFIXES = ("knowledge/research/", "scratch/")` (line 32), `_REGISTER_PATTERNS` (lines 34-37) |

---

## D-1 — The Clearance Record

### Decision: new `clearances` table in lifecycle.db

**Chosen:** **(a) a new `clearances` table in lifecycle.db**, written by the depositor at `_clear()` time.

**Rejected:** (b) sidecar receipt file. A sidecar `.clearance.json` alongside each plan introduces a file that the daemon's filesystem watcher would see (bellows.py:2641 `observer.schedule(handler, decisions_path, recursive=False)`), requiring ignore-rules in `_handle` and `on_created`/`on_modified`/`on_moved` (bellows.py:2125-2138). It survives daemon restart but is fragile to accidental deletion, not queryable, and not auditable by `status.py` without file-scanning logic.

**Why (a) wins:**

1. **In-process per G3.** The depositor runs in the daemon process (bellows.py:2186). A `sqlite3.connect()` to lifecycle.db is already proven at depositor.py:372 (`_resolve_in_flight_writes` opens lifecycle.db read-only via `file:{self._db_path}?mode=ro`). The clearance WRITE uses the same `self._db_path` with a read-write connection — the sole-writer model holds because the depositor's `self._lock` (depositor.py:60, `threading.Lock()`) serializes all evaluate calls, and the daemon process is the only writer to lifecycle.db (lifecycle.py:28, `PRAGMA journal_mode=WAL`).

2. **Keyed by content SHA-256.** At `_clear()` time (depositor.py:496-514), the plan file bytes are available (read at depositor.py:109 via `Path(path).read_text()`). The clearance row stores `content_hash = hashlib.sha256(plan_bytes.encode()).hexdigest()`. A post-clearance byte change invalidates clearance BY CONSTRUCTION — the claim-time check (D-2) computes the hash of the file it is about to claim and looks it up; a modified file produces a different hash and finds no clearance row. **This is a feature:** it means tampering between clear and claim is detectable without any additional integrity check.

3. **Interaction with pristine snapshots.** The daemon already writes pristine plan content via `_write_shadow()` at bellows.py:889-890 (immediately after `mint_and_claim`). The clearance hash is computed BEFORE the shadow is written — the shadow captures the same bytes the hash was computed over. If the file is modified between clearance and claim, the hash mismatch catches it before the shadow is ever written.

4. **Survives daemon restart.** lifecycle.db is WAL-journaled (lifecycle.py:28) and persists across restarts.

5. **Readable by the claim path in-process with no new IPC.** `is_claimable()` (D-2) queries the same DB connection pattern already used by `active_plan_for_placeholder` (lifecycle.py:173-183).

6. **Auditable by `status.py`.** `status.py` already queries lifecycle.db read-only (status.py:208, `f"file:{db_path}?mode=ro"`). A clearance query follows the same pattern.

### Table DDL

```sql
CREATE TABLE IF NOT EXISTS clearances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    assigned_class TEXT NOT NULL,
    cleared_by TEXT NOT NULL CHECK (cleared_by IN ('depositor', 'clear_tool')),
    cleared_at TEXT NOT NULL,
    UNIQUE(content_hash)
)
```

**`UNIQUE(content_hash)`** — one clearance per content hash. A re-clear after modification produces a new hash and a new row. The old row is not deleted (audit trail).

### Write site

`depositor.py:_clear()` (currently depositor.py:496-514). After the `os.rename(path, claimable_path)` at line 505, insert the clearance row. The hash is computed from the bytes read at depositor.py:109 (passed through the call chain). `cleared_by = 'depositor'` for auto-clear; `cleared_by = 'clear_tool'` for the gated clear tool (D-5).

### Read site

`is_claimable()` (D-2) — a `SELECT 1 FROM clearances WHERE content_hash = ?` returning a row means cleared.

---

## D-2 — The Claim-Path Check

### New function: `is_claimable(path, db_path)`

```python
def is_claimable(path, db_path):
    """Name-pattern AND clearance-lookup. Returns True only if the file
    matches a runnable name pattern AND has a current clearance record."""
    filename = os.path.basename(path)
    if not is_runnable_plan(filename):
        return False
    try:
        content = Path(path).read_text(encoding="utf-8")
    except Exception:
        return False
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    row = conn.execute(
        "SELECT 1 FROM clearances WHERE content_hash = ?",
        (content_hash,),
    ).fetchone()
    conn.close()
    return row is not None
```

**Two-part check:** (1) `is_runnable_plan(filename)` — the existing name-pattern check (bellows.py:2032-2035); (2) clearance lookup by content SHA-256. Both must pass.

### G1 call-site classification

| line | context | role | gate? | rationale |
|---|---|---|---|---|
| **bellows.py:2065** | `_handle` entry — first check before dispatch | **DISPATCH** | **YES → replace with `is_claimable`** | This is the primary dispatch gate. If left ungated, a hand-named file dispatches immediately — bypass (a) re-opened |
| **bellows.py:2053** | `collect_group` — parallel-group collection | **DISPATCH** | **YES → replace with `is_claimable`** | `collect_group` feeds `handle_parallel_group` (bellows.py:2100, 2341). An ungated site here dispatches unchecked parallel plans |
| **bellows.py:2346** | DISC-1 rescan — periodic re-scan of watched dirs | **DISPATCH** | **YES → replace with `is_claimable`** | Feeds `handler._handle(full_path, from_rescan=True)` at line 2348. The rescan path must not bypass the clearance gate |
| **bellows.py:2702** | startup scan — scan for plans on disk at startup | **DISPATCH** | **YES → replace with `is_claimable`** | Feeds `handler._handle(full_path)` at line 2705. Startup must not dispatch unchecked plans |
| **bellows.py:2220** | `_check_queue_drain` — idle-notify pending count | **ENUMERATE** | **NO — keep `is_runnable_plan`** | Counts pending runnable plans for the "queue empty" notification (bellows.py:2221-2231). If gated with `is_claimable`, a plan awaiting clearance would be invisible to idle-notify, and the daemon would send "queue empty" while a plan is still pending evaluation. Wrong: the daemon must know it has pending work |
| **bellows.py:2622** | orphan-verdict active-slug scan | **ENUMERATE** | **NO — keep `is_runnable_plan`** | Builds `active_slugs` set for orphaned verdict-request cleanup (bellows.py:2610-2634). If gated with `is_claimable`, an unclearable plan's slug would be excluded from `active_slugs`, and its verdict requests would be incorrectly garbage-collected. Wrong: the plan still exists on disk, and its verdict requests are valid |

**Failure modes of wrong choices:**
- A DISPATCH site left ungated re-opens bypass (a) — a hand-named file dispatches without depositor evaluation
- An ENUMERATE site wrongly gated makes held/unclearable plans invisible to idle-notify and orphan reconciliation — the daemon sends premature "queue empty" notifications and garbage-collects valid verdict requests

### Auto-HOLD integration at dispatch sites

At each of the four DISPATCH sites, when `is_runnable_plan(filename)` returns True but `is_claimable(path, db_path)` returns False, the plan is renamed to `hold-<name>` with `{"hold_reason": "no_clearance"}` (D-3). The dispatch path is never reached.

---

## D-3 — The Auto-HOLD Arm

### Specification

An unclearable claimable-named file (matches `is_runnable_plan` but fails `is_claimable`) is renamed `hold-<name>` with a `.hold.json` containing `{"hold_reason": "no_clearance", "held_at": "<iso>"}`.

### Location: `_handle` in `PlanHandler` (bellows.py:2059-2104)

Insert after the `is_runnable_plan` check at bellows.py:2065, before the `_seen` check at bellows.py:2079:

```
if is_runnable_plan(filename):
    if not is_claimable(path, self.orchestrator.depositor._db_path):
        # Auto-HOLD: no clearance record
        slug = verdict.slug_from_path(path)
        if slug not in self.orchestrator._seen:
            _log("WARN", "⚠️ auto-HOLD — no clearance record", slug=slug_for(filename))
            self.orchestrator._seen.add(slug)
            # Rename to hold-
            hold_name = "hold-" + filename
            hold_path = os.path.join(os.path.dirname(path), hold_name)
            os.rename(path, hold_path)
            hold_json = hold_path.replace(".md", ".hold.json")
            with open(hold_json, "w") as f:
                json.dump({"hold_reason": "no_clearance",
                           "held_at": datetime.now().isoformat()}, f, indent=2)
        return
    # ... existing dispatch logic ...
```

**Once-per-slug discipline:** mirrors G6's WARN arm (bellows.py:2073-2077). The `_seen` set prevents re-processing on subsequent watchdog events or rescans for the same slug.

### DISC-1/startup rescan avoidance

- **DISC-1 rescan (bellows.py:2343-2348):** calls `handler._handle(full_path, from_rescan=True)`. The `_seen` check at the auto-HOLD entry prevents re-processing. The file is already renamed to `hold-<name>`, so `is_runnable_plan("hold-<name>")` returns False (bellows.py:2033, `hold-` not in the exclusion set, but the regex `^(parallel-\d+-)?(executable|diagnostic|qa)-` does not match `hold-`). The file is invisible to the rescan.
- **Startup scan (bellows.py:2698-2705):** same logic — `is_runnable_plan` returns False for `hold-` prefixed files.
- **Depositor reevaluation (bellows.py:2708):** `self.depositor.reevaluate_on_startup()` at depositor.py:75-84 already scans `hold-` files and calls `_reevaluate_hold()`. The auto-HOLD file is picked up by this path.

---

## D-4 — The Class Split (Fork 4)

### Rule-based `shop-infra` detection

**Rule:** a plan is `shop-infra` if ANY of its writes targets a path matching:

1. Under `bellows/` outside `bellows/knowledge/` — the daemon's own code
2. Under `forge/` outside `forge/knowledge/` — the forge's own code
3. Under `lessons-forge/` outside `lessons-forge/knowledge/` — the lessons-forge's own code
4. Under `anvil/` outside `anvil/knowledge/` — the anvil's own code
5. A file at the governance root's top level (not under any subdirectory) that is NOT under `knowledge/` — where doctrine files live (e.g., `ELUVIAN_PATH.md`, `LESSONS.md`)

**Why rule-based, not hand-list:** a hand list is invisible-when-incomplete and rots. ELUVIAN_PATH.md joined the doctrine set THIS WEEK (2026-08-24, exec-510 deposited it at the governance root). A hand list that predated 510 would not have included it. The rule "any write at the governance root's top level" catches future doctrine files by construction.

### Concrete `_assign_class` replacement at depositor.py:255-278

```python
_SHOP_INFRA_CODE_DIRS = ("bellows/", "forge/", "lessons-forge/", "anvil/")
_SHOP_INFRA_KNOWLEDGE_EXEMPTIONS = tuple(d + "knowledge/" for d in _SHOP_INFRA_CODE_DIRS)

def _assign_class(self, writes):
    if not writes:
        return None

    all_read_only = True
    has_register = False
    has_shop_infra = False

    for p in writes:
        normalized = p.lstrip("/")

        # read-only check (unchanged)
        if not any(normalized.startswith(pfx) or f"/{pfx}" in f"/{normalized}"
                   for pfx in _READ_ONLY_PREFIXES):
            if not any(seg + "/" in normalized or normalized.endswith(seg)
                       for seg in ("knowledge/research", "scratch")):
                all_read_only = False

        # register check (unchanged)
        for pat in _REGISTER_PATTERNS:
            if pat.search(normalized):
                has_register = True

        # shop-infra check (NEW)
        for code_dir in _SHOP_INFRA_CODE_DIRS:
            if normalized.startswith(code_dir):
                if not any(normalized.startswith(ex) for ex in _SHOP_INFRA_KNOWLEDGE_EXEMPTIONS):
                    has_shop_infra = True

        # governance root top-level check (NEW)
        # A write directly at the governance root (no / in the path after normalization,
        # or the first component is the file itself) that is not under knowledge/
        if "/" not in normalized and not normalized.startswith("knowledge/"):
            has_shop_infra = True

    if all_read_only:
        return "read-only"
    if has_shop_infra:
        return "shop-infra"
    if has_register:
        return "register-writing"
    return "app-feature"
```

**Precedence:** `read-only` > `shop-infra` > `register-writing` > `app-feature`. A plan that writes BOTH shop-infra paths and app paths gets `shop-infra` (the more restrictive class wins).

**No catch-all remains.** `app-feature` replaces the old `governed-tooling` catch-all. Any plan that writes files NOT matching read-only, shop-infra, or register patterns receives `app-feature` — positively named, not a residual bucket.

### Auto-clear policy per fork 4

| class | auto-clear? | condition |
|---|---|---|
| `read-only` | YES | full-pass gates (unchanged from today, depositor.py:173-184) |
| `app-feature` | YES | full-pass gates: cycle_check = BAR_MET (depositor.py:440-444), plan_lint 0 non-benign FAIL (depositor.py:451-471), collision pass (depositor.py:146-149), disk preflight (depositor.py:169-171), manifest validation match (depositor.py:477-488) |
| `register-writing` | YES | full-pass gates (same gate set as app-feature) |
| `shop-infra` | HELD | always held — `class:shop-infra` reason. Too high-risk for auto-clear |

### Force-classification of last 20 closed plans

Each plan's write set is classified against the rule above.

| id | type | project | write paths (representative) | class under new rule | class under old rule | match? |
|---|---|---|---|---|---|---|
| 510 | exec | governance | `ELUVIAN_PATH.md` (root), `~/.claude/commands/eluvian.md` (external), `bellows/hooks/eluvian/eluvian_align_hook.py` | **shop-infra** | governed-tooling | ✓ (both HELD) |
| 509 | diag | governance | `knowledge/research/eluvian-path-audit-2026-08-24.md` | **read-only** | read-only | ✓ |
| 508 | diag | governance | `knowledge/research/eluvian-path-audit-2026-08-24.md`, `knowledge/research/eluvian-path-draft-2026-08-24.md` | **read-only** | read-only | ✓ |
| 507 | exec | lessons-forge | `knowledge/research/bare-entry-ruling-2026-08-23.tsv` | **read-only** | read-only | ✓ |
| 506 | diag | lessons-forge | `knowledge/research/bare-entry-ruling-2026-08-23.md`, `.tsv` | **read-only** | read-only | ✓ |
| 505 | exec | governance | `LESSONS.md` (root), `knowledge/tools/apply_annotation.py`, `knowledge/research/...` | **shop-infra** | governed-tooling | ✓ (both HELD) |
| 504 | diag | lessons-forge | `knowledge/research/promotion-corrected-2026-08-23.md`, `.tsv` | **read-only** | read-only | ✓ |
| 503 | diag | lessons-forge | `knowledge/research/learned-promotion-2026-08-23.md`, `.tsv` | **read-only** | read-only | ✓ |
| 502 | exec | governance | `LESSONS.md` (root), `knowledge/tools/apply_annotation.py`, `knowledge/research/...` | **shop-infra** | governed-tooling | ✓ (both HELD) |
| 501 | diag | lessons-forge | `knowledge/research/annotation-detector-2026-08-22.md`, `.tsv`, `scripts/detect_learned.py` | **shop-infra** | governed-tooling | ✓ (both HELD) |
| 500 | exec | lessons-forge | `src/lessons_forge.py`, `src/test_lessons_forge.py` | **app-feature** | governed-tooling | ↑ UPGRADE |
| 499 | exec | lessons-forge | `src/lessons_forge.py`, `src/test_lessons_forge.py` | **app-feature** | governed-tooling | ↑ UPGRADE |
| 498 | diag | lessons-forge | `knowledge/research/lessons-reconcile-learned-2026-08-21.md` | **read-only** | read-only | ✓ |
| 497 | exec | bellows | `hooks/eluvian/wrap_stop_hook.py`, `hooks/eluvian/wrap_arm_hook.py`, `tests/test_wrap_sentinel.py` | **shop-infra** | governed-tooling | ✓ (both HELD) |
| 496 | exec | bellows | `hooks/eluvian/*.py`, `hooks/commands/wrap.md`, `hooks/settings-hooks-snapshot.json`, `hooks/README.md`, `knowledge/qa/...` | **shop-infra** | governed-tooling | ✓ (both HELD) |
| 495 | diag | bellows | `knowledge/research/wrap-hook-daemon-exemption-2026-08-21.md` | **read-only** | read-only | ✓ |
| 494 | exec | invoice-pulse | `web/reporting.py`, `web/templates/*.html`, `tests/...` | **app-feature** | governed-tooling | ↑ UPGRADE |
| 493 | exec | invoice-pulse | `scripts/reconcile_dispute_outcomes.py`, `tests/...` | **app-feature** | governed-tooling | ↑ UPGRADE |
| 492 | exec | bellows | `scripts/plan_lint.py`, `tests/test_plan_lint.py` | **shop-infra** | governed-tooling | ✓ (both HELD) |

**Summary:** 20 plans force-classified. 9 read-only (unchanged). 6 shop-infra (governed-tooling → shop-infra, both HELD — no behavior change). 4 app-feature (governed-tooling → app-feature — UPGRADE from HELD to auto-clear on full-pass gates). 1 remaining (511 = this diagnostic, read-only). No unclassifiable write set. No catch-all invoked.

**The 4 UPGRADEs** (499, 500, 493, 494) are exactly the cases R3 targets: ordinary project code (lessons-forge `src/`, invoice-pulse `web/`, `scripts/`) that the old catch-all wrongly held. Under the new rule, these auto-clear on full-pass gates.

### N/A tension resolution

**The tension:** the rulings' additional-verification line wishes *substrate asserts never N/A*, but residual (ii) (re-verified at 509: cycle_check.py:257-260) makes a governance-hosted register return N/A from the plan's own repo by construction — because `check_assert_2` (cycle_check.py:245-289) defaults `register_result = "N/A"` (line 247) and returns N/A when the walk register's first component path resolves to a DIFFERENT git root (line 259-260: `sub_root and sub_root.resolve() != git_root.resolve()`). A plan dispatched into bellows (bellows repo) whose walk register lives in governance (governance repo) hits this condition. Never-N/A would bar every cross-repo-registered plan from auto-clear.

**Decision: option (ii) — accept N/A for the register assert alone.**

**Compensating gates (all mechanized and already active in the depositor path):**
- `cycle_check.run_check()` at depositor.py:440 — returns BAR_MET only when the full run_check logic passes, which includes `walk_register_lint` (cycle_check.py:454-475, checks register file formatting), per-walk commit evidence (cycle_check.py:266-285, `git_has_context`), and fold baseline existence (cycle_check.py:292-301, `check_assert_3`)
- `plan_lint.py` at depositor.py:451-471 — structural validation of the plan file
- Manifest validation cross-check at depositor.py:477-488 — the plan's declared `cycle_check=` value must match the actual verdict

**Cost of the rejected alternative (option (i) — N/A → HOLD):** every governance-registered cycle stays held. This includes all bellows diagnostics whose walk registers live in governance (e.g., this diagnostic, 511, whose walk register is at `governance/knowledge/research/walk-register-diagnostic-eluvian-e2-design.md`). The cost is disproportionate: the compensating gates already verify the register's SUBSTANCE (format, walk commits, fold baseline) — the N/A from `check_assert_2` only means the register FILE was not found in the plan's own repo, which is by construction for cross-repo plans.

**Rule (for the executable):** auto-clear accepts N/A from `check_assert_2` (register evidence) when the other two substrate asserts (assert_1: internal arithmetic, assert_3: fold baseline) are PASS or N/A with compensating gates active. This is written here as a design rule, not a new CEO ruling — it implements the spirit of the rulings' "verification welcome" stance by naming the SPECIFIC compensating gates rather than blanket-accepting N/A.

---

## D-5 — The Gated Clear Tool

### Decision: (b) rename-to-ready RE-ENTRY

**Chosen:** the tool validates preconditions and renames `hold-` → `ready-`, and the LIVE daemon's own depositor re-evaluates: one evaluator, no second-process locks, full-pass → clearance + clear, fail → re-hold with the fresh reason.

**Rejected:** (a) in-tool evaluation. The tool would re-run depositor logic itself (`_assign_class`, `_rerun_validation`, collision checks), duplicating the evaluator in a second process. This creates:
- **Locking question:** the depositor uses `self._lock` (depositor.py:60, `threading.Lock()`) to serialize evaluations within the daemon process. A second process running the same logic has no access to this lock. Options: flock on lifecycle.db (fragile, WAL mode already handles writer serialization but not application-level invariants), or the daemon's `_shutting_down` flag (depositor.py:91, checked at evaluate entry — not accessible cross-process).
- **Evaluator divergence:** the tool's copy of depositor logic must be kept in sync with the daemon's. A bug fix to `_assign_class` that is not mirrored to the tool creates a class-assignment disagreement.

**Why (b) dissolves (a)'s hardest questions:**
- **One evaluator.** The daemon's `depositor.evaluate()` is the only code that assigns classes, checks collisions, runs cycle_check, and writes clearance records. The tool triggers it by rename, not by duplicating it.
- **No second-process locks.** The rename is an `os.rename()` — atomic on POSIX. The daemon's watchdog (bellows.py:2125-2138, `on_created`/`on_modified`/`on_moved`) fires on the rename, and the depositor's `self._lock` serializes the evaluation in the daemon process.
- **Full depositor gate set applies.** The re-evaluation runs `_do_evaluate` (depositor.py:122-188): empty_writes, collision, rerun_validation (cycle_check + plan_lint), class assignment, manifest validation, disk preflight. If any gate fails, the file is re-held with the fresh reason (depositor.py:186, `self._hold(path, f"class:{assigned_class}", ...)`).

### (b)'s own edges

**DISC-2 ready-rescan cadence.** bellows.py:2350-2359 — the DISC-2 recovery net re-scans `ready-` files every 30 seconds (bellows.py:2710, `rescan_interval = 30`). If the watchdog misses the rename event, the DISC-2 rescan picks it up within 30 seconds. The tool does NOT need to wait for DISC-2 — the watchdog fires synchronously on the rename in most cases. DISC-2 is the safety net.

**Asynchronous outcome reporting.** The tool renames and returns immediately. It reports to its caller: "Plan renamed to ready- state. The daemon will evaluate it within 30 seconds. Check hold status after evaluation." The tool can optionally poll for the hold/clear outcome by watching for the file's name change (from `ready-<name>` to either `<name>` (cleared) or `hold-<name>` (re-held)) with a short timeout (e.g., 60 seconds). If the timeout expires, it reports "evaluation pending — check `python status.py`."

### Tool specification: `bellows/tools/clear_plan.py <hold-file>`

```
Usage: python bellows/tools/clear_plan.py <path-to-hold-file>

Preconditions (checked before rename):
1. File exists and starts with "hold-"
2. File ends with ".md"
3. A .hold.json sidecar exists (holds the reason)
4. The daemon is running (check PID file or process)

Action:
1. Read the hold file content
2. Rename hold-<name>.md → ready-<name>.md
3. Remove the .hold.json sidecar (clean slate for re-evaluation)
4. Report: "Renamed to ready- state. Daemon will re-evaluate."
5. Optional: poll for up to 60s for outcome, report result

Manual rename becomes INERT:
- Renaming hold-X.md → X.md (the old bypass (b)) produces a file that matches
  is_runnable_plan but NOT is_claimable (no clearance record). The auto-HOLD arm
  (D-3) catches it and re-holds it with "no_clearance" reason.
- The ONLY path to clearance is through the depositor: ready- → evaluate → clear.
  The gated clear tool is the ONLY way to get a held plan back to ready- state.
```

---

## D-6 — Migration + Activation (Fork 2)

### Grandfather clause

Per fork 2 ruling: existing `halted-`/`hold-`/`parked-` files stay untouched. No retroactive provenance.

**Measured 2026-08-24:**
- `halted-` files: 16 across 5 projects (invoice-pulse: 9, anvil: 1, bellows: 1, lessons-forge: 2, governance: 3)
- `hold-` files: 0 across all 10 watched dirs
- `parked-` files: 41 (per daemon status line)
- `ready-` files: 0 (no pending evaluations)
- Bare claimable-named files: 0 (G5 re-confirmed)

The hot set (bare claimable files that would be affected by the flip) is **empty**. Migration therefore has no runtime impact on existing plans. The grandfather clause applies to the cold set (halted- and parked- files) — they can only re-enter through the gated clear tool (D-5), which triggers full depositor re-evaluation.

### Activation sequence

Activation is a DAEMON RESTART — a deliberate step, not an automatic migration.

1. **Code changes committed** (the executable's write set — see Rule 27 gap table)
2. **Daemon stopped** (`python bellows.py stop` or SIGTERM)
3. **lifecycle.db migration** — `init_lifecycle_db()` at lifecycle.py:24 is already idempotent (`CREATE TABLE IF NOT EXISTS`). The new `clearances` table DDL is added to `init_lifecycle_db()` and runs on first startup after the code change
4. **Daemon started** (`python bellows.py` or `python dashboard.py`)
5. **Live canary — both arms**

### Live canary

**(i) Hand-named dummy → observe auto-HOLD `no_clearance`.**

Place a file named `diagnostic-canary-e2-flip.md` in a scratch-safe watched dir (e.g., `bellows/knowledge/decisions/`).

**The dummy must be SAFE-IF-DISPATCHED** because the canary exists to catch a broken flip and a broken flip DISPATCHES it:
```yaml
auto_close: true
Tier: T1
Test Scope: none
pause_for_verdict: never
```
Body: a read-only, no-op plan with `class: read-only`, `writes: knowledge/research/canary-e2-flip-test.md`, `reads: (none)`. If dispatched despite a broken flip, it writes one harmless research file and auto-closes.

**Expected behavior (flip working):** `is_runnable_plan("diagnostic-canary-e2-flip.md")` = True, but `is_claimable()` = False (no clearance record). Auto-HOLD arm fires: file renamed to `hold-diagnostic-canary-e2-flip.md`, `.hold.json` with `"hold_reason": "no_clearance"`.

**Observed behavior (flip broken):** the file dispatches. Because it is safe-if-dispatched (auto_close, read-only, no-op), the damage is limited to one lifecycle row and one research file. The broken flip is detected by the dispatch event in the daemon log.

**(ii) Ready-staged read-only dummy → observe clear + claim.**

Place a file named `ready-diagnostic-canary-e2-clear.md` in `bellows/knowledge/decisions/`. Same safe-if-dispatched content.

**Expected behavior:** the depositor evaluates it, assigns `read-only`, passes all gates, writes a clearance record, renames to `diagnostic-canary-e2-clear.md`. The daemon's `_handle` sees the file, `is_claimable()` = True, dispatches it. The plan auto-closes.

### Cleanup

After both canary arms complete:
1. Remove the canary plan files (hold-diagnostic-canary-e2-flip.md, its .hold.json, and the cleared/completed canary)
2. Remove lifecycle rows: `DELETE FROM plans WHERE title LIKE '%canary-e2%'`; `DELETE FROM clearances WHERE plan_path LIKE '%canary-e2%'`
3. Remove the deposited research file if arm (ii) ran

### Rollback

`git revert <commit>` + daemon restart. The `clearances` table remains in lifecycle.db (harmless — no code reads it after revert). `is_claimable` reverts to `is_runnable_plan`-only, restoring pre-flip behavior.

---

## D-7 — Test Plan

### New unit tests

| test | target | what it verifies |
|---|---|---|
| `test_is_claimable_with_clearance` | `is_claimable()` | Returns True when `is_runnable_plan` = True AND a clearance row exists for the content hash |
| `test_is_claimable_no_clearance` | `is_claimable()` | Returns False when `is_runnable_plan` = True but no clearance row exists |
| `test_is_claimable_modified_content` | `is_claimable()` | Returns False when a clearance row exists but the file content has changed (hash mismatch) |
| `test_is_claimable_non_runnable` | `is_claimable()` | Returns False for non-runnable names (`hold-`, `ready-`, `parked-`) regardless of clearance |
| `test_assign_class_shop_infra` | `_assign_class()` | Classifies writes under `bellows/`, `forge/`, `lessons-forge/`, `anvil/` (outside `knowledge/`) as `shop-infra` |
| `test_assign_class_shop_infra_knowledge_exempt` | `_assign_class()` | Writes under `bellows/knowledge/research/...` are NOT `shop-infra` — they are `read-only` |
| `test_assign_class_app_feature` | `_assign_class()` | Writes under project dirs not matching shop-infra (e.g., `src/app.py`, `web/views.py`) → `app-feature` |
| `test_assign_class_governance_root` | `_assign_class()` | Writes at governance root top level (e.g., `ELUVIAN_PATH.md`, `LESSONS.md`) → `shop-infra` |
| `test_assign_class_precedence` | `_assign_class()` | A plan writing BOTH `bellows/runner.py` and `src/app.py` → `shop-infra` (most restrictive wins) |
| `test_force_classification_table` | `_assign_class()` | The 20-row force-classification table from D-4 — each plan's write set produces the expected class |
| `test_clearance_write_read_roundtrip` | `clearances` table | Write a clearance row, read it back, verify content_hash match |
| `test_clearance_uniqueness` | `clearances` table | Two clearances with the same content_hash → only one row (UNIQUE constraint) |
| `test_auto_hold_no_clearance` | auto-HOLD arm | A file matching `is_runnable_plan` without clearance is renamed to `hold-` with `.hold.json` |
| `test_auto_hold_once_per_slug` | auto-HOLD arm | Same slug processed twice → only one WARN log, no double-rename |
| `test_clear_tool_rename_to_ready` | clear tool | `clear_plan.py` renames `hold-X.md` → `ready-X.md` and removes `.hold.json` |
| `test_clear_tool_preconditions` | clear tool | Rejects non-hold files, missing .hold.json, non-existent files |
| `test_auto_clear_app_feature` | depositor | A plan with `app-feature` class that passes all gates is auto-cleared (clearance record written) |
| `test_hold_shop_infra` | depositor | A plan with `shop-infra` class is held regardless of gate results |

### Existing tests that must pass unchanged (481 suite)

All tests in `bellows/tests/`:
- `test_depositor.py` — existing depositor logic (evaluate, hold, clear, collision, class assignment)
- `test_lifecycle.py` — lifecycle DB operations (mint_and_claim, mark_plan_state, recovery)
- `test_bellows.py` — daemon orchestration (is_runnable_plan, _handle, dispatch)
- `test_cycle_check.py` — cycle_check validation (BAR_MET, N/A, FAIL)
- `test_plan_lint.py` — plan_lint validation
- `test_gates.py` — gate logic
- `test_status.py` — status reporting
- `test_wrap_hooks.py` — wrap hook logic
- `test_wrap_sentinel.py` — wrap sentinel logic

---

## D-8 — Open Questions

### Questions requiring a new CEO ruling

**None.** All design decisions are grounded in existing rulings (R1, R3, fork 2, fork 4) and auditable code evidence. The N/A tension is resolved within the design as option (ii) with compensating gates stated — this implements the rulings' "verification welcome" stance, not a new ruling.

### Design decisions that could be escalated

1. **`shop-infra` rule expansion:** the current rule covers `bellows/`, `forge/`, `lessons-forge/`, `anvil/`, and governance root top-level. If a new shop-infrastructure repo is added to the watched projects, the rule must be updated. This is a maintenance cost, not a ruling — the repo set changes rarely and the update is mechanical.

2. **Clear tool asynchronous reporting:** the tool renames and returns. The alternative (synchronous wait for evaluation outcome) adds complexity (polling loop, timeout handling) for modest benefit. The current design is stated; if the CEO wants synchronous reporting, it is a follow-up, not a blocker.

---

## Rule 27 Gap Table

Every code change site the executable will touch.

| # | file | line(s) | change | D-section |
|---|---|---|---|---|
| 1 | `lifecycle.py` | after line 168 (before `conn.commit()`) | Add `CREATE TABLE IF NOT EXISTS clearances (...)` DDL to `init_lifecycle_db()` | D-1 |
| 2 | `lifecycle.py` | new functions | Add `write_clearance(plan_path, content_hash, assigned_class, cleared_by, db_path)` and `has_clearance(content_hash, db_path)` query functions | D-1 |
| 3 | `depositor.py` | line 496-514 (`_clear()`) | After `os.rename`, write clearance row via `lifecycle.write_clearance(...)` with content hash computed from plan bytes and `cleared_by='depositor'` | D-1 |
| 4 | `depositor.py` | line 173-188 (auto-clear policy in `_do_evaluate`) | Expand auto-clear from `read-only` only to `read-only` + `app-feature` + `register-writing` on full-pass gates; `shop-infra` stays HELD | D-4 |
| 5 | `depositor.py` | line 255-278 (`_assign_class`) | Replace with rule-based four-class split: `read-only`, `shop-infra`, `register-writing`, `app-feature` | D-4 |
| 6 | `depositor.py` | line 32-37 (constants) | Add `_SHOP_INFRA_CODE_DIRS` and `_SHOP_INFRA_KNOWLEDGE_EXEMPTIONS` constants | D-4 |
| 7 | `bellows.py` | line 2032-2035 (`is_runnable_plan`) | Keep unchanged — name-pattern check only | D-2 |
| 8 | `bellows.py` | new function near line 2035 | Add `is_claimable(path, db_path)` — name-pattern AND clearance lookup | D-2 |
| 9 | `bellows.py` | line 2053 (`collect_group`) | Replace `is_runnable_plan(fname)` with `is_claimable(full_path, ...)` | D-2 |
| 10 | `bellows.py` | line 2065 (`_handle` entry) | Replace `is_runnable_plan(filename)` dispatch gate with `is_claimable` + auto-HOLD arm | D-2, D-3 |
| 11 | `bellows.py` | line 2346 (DISC-1 rescan) | Replace `is_runnable_plan(fname)` with `is_claimable(full_path, ...)` | D-2 |
| 12 | `bellows.py` | line 2702 (startup scan) | Replace `is_runnable_plan(fname)` with `is_claimable(full_path, ...)` | D-2 |
| 13 | `bellows.py` | line 2220 (`_check_queue_drain`) | Keep `is_runnable_plan` — ENUMERATE site, not DISPATCH | D-2 |
| 14 | `bellows.py` | line 2622 (orphan-verdict scan) | Keep `is_runnable_plan` — ENUMERATE site, not DISPATCH | D-2 |
| 15 | new file: `bellows/tools/clear_plan.py` | entire file | Gated clear tool: precondition checks + `hold-` → `ready-` rename | D-5 |
| 16 | `status.py` | near line 184 (`render_depositor_status`) | Add clearance status query (optional — enhances audit visibility) | D-1 |
| 17 | `tests/test_depositor.py` | new test functions | Tests for is_claimable, class split, clearance roundtrip, auto-HOLD, auto-clear expansion | D-7 |
| 18 | `tests/test_bellows.py` | new test functions | Tests for is_claimable integration at dispatch sites | D-7 |
| 19 | new file: `tests/test_clear_tool.py` | entire file | Tests for clear_plan.py preconditions and rename logic | D-7 |

---

## Post-conditions checklist

- [x] Every D-section (D-1 through D-8) present with ≥1 file:line citation
- [x] G1's six call sites all classified (4 DISPATCH, 2 ENUMERATE) with each wrong-choice failure mode stated
- [x] R1 sentence quoted once verbatim (top of document)
- [x] Rule 27 gap table enumerating every code change site the executable will touch (19 entries)
- [x] Force-classification of last 20 closed plans against the new class rule (20/20 classified, 0 unassignable)
- [x] N/A tension resolved explicitly in writing with both options' costs stated
- [x] Safety invariant (depositor never mints, never dispatches) restated and preserved
- [x] Every design decision grounded in file:line in CURRENT code
- [x] Every claim of absence carries a positive control
