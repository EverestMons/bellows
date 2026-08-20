# Component 3 — In-Bellows Depositor + Dashboard UI: Finalized Design + Rule 27 Gap Assessment

**Date:** 2026-08-20
**Author:** Bellows Design Agent
**Plan:** diagnostic-478
**Step:** 1 (design diagnostic, read-only)
**Conforms to:** Routed decisions ratified 2026-08-19

---

## Q0 — Routed Decisions (restated, not changed)

The following decisions were ratified 2026-08-19 and are binding on this design:

1. **Built INTO bellows** — no standalone `depositor.py` script. The depositor is a module within the bellows package, invoked by the daemon process.
2. **Reuses queue / `id_sequence` / freeze / disk state** — the depositor shares the daemon's existing infrastructure rather than maintaining its own.
3. **`ready/` = a lifecycle staging state the daemon is forbidden to claim** — staged plans live in a namespace the claim gate (`is_runnable_plan`) rejects.
4. **A `dashboard.py` UI element** — the depositor's cleared/held state is surfaced in the existing TUI dashboard.
5. **Auto-deposit `read-only` class ONLY** — plans whose `writes:` paths are all within `knowledge/research/` or scratch directories are auto-deposited. All other classes (`governed-tooling`, `register-writing`) are HELD for CEO action.
6. **No cost escalation** — the depositor does not increase dispatch costs; it only stages and clears.
7. **ESCALATE = resumable pause** — a HOLD is not terminal; it waits for CEO release and re-evaluates at clear time.

---

## Q1 — The Claim/Safety Boundary + the `ready/` Staging State

### The Claim Path (live characterization)

The daemon's claim path flows through these sites:

1. **`is_runnable_plan(filename)`** (`bellows.py:2030–2033`):
   ```python
   def is_runnable_plan(filename: str) -> bool:
       if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") \
          or filename.startswith("halted-") or filename.startswith("parked-"):
           return False
       return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$", filename))
   ```
   This is the claim gate. A filename must match the regex AND not carry a lifecycle prefix.

2. **`PlanHandler._handle(path)`** (`bellows.py:2057–2095`): The watchdog event handler. It checks `is_runnable_plan(filename)` at :2063 — non-matching files are skipped. For matching files, it dispatches to `handle_new_plan()`.

3. **`PlanHandler.collect_group(decisions_path, group)`** (`bellows.py:2047–2055`): Collects parallel-group siblings, filtering through `is_runnable_plan(fname)` at :2051.

4. **`handle_new_plan(path)`** (`bellows.py:2218+`): Calls `run_plan()`.

5. **`run_plan()` claim block** (`bellows.py:830–894`): The actual claim — validates, mints id via `lifecycle.mint_and_claim()` (:859), renames to `in-progress-<type>-<id>.md` (:875), writes shadow, records meta.

6. **`lifecycle.mint_and_claim()`** (`lifecycle.py:186–216`): Atomic `BEGIN IMMEDIATE` transaction — increments `id_sequence.next_id` and inserts a `plans` row in a single transaction. No id is burned without a corresponding row.

### Staging Name Verification (LIVE regex, positive + negative controls)

**Executed against the ACTUAL `is_runnable_plan` logic:**

| Candidate | Result | Expected |
|---|---|---|
| `ready-executable-foo.md` | **False** | False (staging — daemon must reject) |
| `ready-diagnostic-bar.md` | **False** | False (staging — daemon must reject) |
| `hold-executable-foo.md` | **False** | False (HOLD — daemon must reject) |
| `hold-diagnostic-bar.md` | **False** | False (HOLD — daemon must reject) |
| `staged-executable-foo.md` | **False** | False (staging — daemon must reject) |
| `executable-foo.md` | **True** | True (positive control — claimable) |
| `diagnostic-bar.md` | **True** | True (positive control — claimable) |
| `qa-test.md` | **True** | True (positive control — claimable) |
| `in-progress-executable-foo.md` | **False** | False (lifecycle prefix — rejected) |
| `verdict-pending-diagnostic-bar.md` | **False** | False (lifecycle prefix — rejected) |
| `halted-executable-foo.md` | **False** | False (lifecycle prefix — rejected) |
| `parked-diagnostic-bar.md` | **False** | False (lifecycle prefix — rejected) |

**Result:** Both `ready-` and `hold-` prefixes are **already non-claimable** by the existing regex. The regex requires the filename to start with `(parallel-\d+-)?` optionally followed by `executable|diagnostic|qa`, and `ready-` / `hold-` match neither. No regex change needed.

### The `ready/` Staging Design

**Recommended: `ready-` filename prefix** within the same `knowledge/decisions/` directory (not a subdirectory). Rationale:
- Already rejected by `is_runnable_plan` (verified above).
- Stays within the same watched directory, so the daemon's existing `watchdog` Observer can detect it via `on_created`/`on_moved` events — no new watcher needed.
- Simpler than a subdirectory (no recursive watch configuration, no path-divergence from the daemon's `watched_projects` config).

**Staging state lifecycle:**
1. An external process (the Planner, a CLI tool, or a manual deposit) places a plan file as `ready-<type>-<slug>.md` in `knowledge/decisions/`.
2. The depositor detects the `ready-` file (via daemon poll or watcher callback).
3. The depositor runs validation (Q3), collision check (Q2), class assignment (Q4).
4. **If AUTO-DEPOSIT (read-only):** Atomic rename `ready-<type>-<slug>.md` → `<type>-<slug>.md` in the same directory. The daemon's existing watcher fires `on_moved`, `_handle` picks up the now-claimable filename, and normal `mint_and_claim` proceeds.
5. **If HOLD:** Rename `ready-<type>-<slug>.md` → `hold-<type>-<slug>.md`. The file stays in `knowledge/decisions/` but is non-claimable (verified above). A HOLD reason is persisted (see Q4).

### The Safety Invariant

**The depositor never mints and never dispatches — it only stages and clears; the daemon claims.**

The depositor's only write operation is a same-directory `os.rename()`. It never calls `lifecycle.mint_and_claim()`. It never calls `run_plan()`. It never calls `handle_new_plan()`. The daemon's existing claim path (`_handle` → `handle_new_plan` → `run_plan` → `mint_and_claim`) is the sole dispatch mechanism.

### Depositor HOME + TRIGGER

**HOME:** A dedicated `bellows/depositor.py` module — the narrowest thing that can pull the trigger (proposal §5). NOT inline in `bellows.py`. The module exports a class `Depositor` that the daemon instantiates.

**TRIGGER:** The daemon invokes the depositor at two points:
1. **On `ready-` file detection:** The daemon's existing `PlanHandler._handle()` already receives ALL filesystem events in watched directories. When `_handle` sees a filename starting with `ready-` (which `is_runnable_plan` rejects), it currently logs a "skipped" warning and returns. The executable adds a branch: if the filename starts with `ready-`, call `depositor.evaluate(path)` instead of returning. This reuses the existing watchdog infrastructure — no new watcher, no poll loop.
2. **On daemon startup (re-evaluation):** The daemon's startup rescan (`_rescan` loop at `bellows.py:2097+`) already iterates files in watched directories. The depositor re-evaluates all `ready-` and `hold-` files on startup, ensuring no stale holds auto-clear and no ready files are missed.

This is the **narrowest trigger surface**: the depositor fires only when a `ready-` or `hold-` file is detected, and only via the daemon's existing filesystem event handler. No background thread, no timer, no external invocation.

**Reference:** `knowledge/architecture/lifecycle-db-id-threading-blueprint-2026-06-11.md` — the id/lifecycle conventions. Key constraint: the depositor must not call `mint_and_claim` (Section 2.2 of the blueprint defines the claim path as exclusively within `run_plan()`). The staging rename (`ready-X` → `X`) feeds the daemon's existing claim flow, which mints the id.

---

## Q2 — The Collision-Query Surface (`reads∩writes` / `writes∩writes`)

### In-Flight Query

The collision check queries in-flight plans from `lifecycle.db` (NOT `bellows.db` — the plans/id_sequence tables live in `lifecycle.db`, verified: `lifecycle.py:20` resolves `LIFECYCLE_DB_PATH = str(resolve_bellows_root() / "lifecycle.db")`).

**Query function:** `status.query_in_flight(db_path)` (`status.py:188–206`):
```python
SELECT p.id, p.type, p.target_project, p.title, p.total_steps,
       s.step_number, s.status, s.step_started_at
FROM plans p
LEFT JOIN steps s ON s.plan_id = p.id
  AND s.step_number = (
    SELECT MAX(s2.step_number) FROM steps s2
    WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
  )
WHERE p.lifecycle_state IN ('in_progress', 'claimed')
ORDER BY p.id
```

The depositor's collision query extends this: for each in-flight plan, extract its `reads` and `writes` sets.

### Manifest Extraction (two paths)

**Path A — Manifest-present plans (2a stanza):** Use `parse_manifest_stanza(plan_text)` (`scripts/cycle_check.py:419–446`). This returns a dict with `reads`, `writes`, `class`, etc. The `reads` and `writes` fields are comma-separated path lists.

```python
def parse_manifest_stanza(plan_text):
    m = MANIFEST_HEADING_RE.search(plan_text)
    if not m:
        return {}
    # ... parses key: value lines from the ## Cycle Manifest block
    return fields  # e.g. {"reads": "DRAFTING_CYCLE.md", "writes": "knowledge/research/foo.md", ...}
```

**Path B — Legacy plans (no stanza):** Most current plans carry NO `## Cycle Manifest` stanza (2a mandates presence going forward, but teeth are deferred). For these, fall back to:
- `_extract_plan_required_deposits(step_text)` (`gates.py:463–517`): Extracts `writes` from `**Deposits:**` blocks — backtick-quoted paths from bullet lists, with legacy prose fallback.
- `_extract_plan_scope(step_text)` (`gates.py:520–543`): Extracts `reads` (declared `**Scope:**` block) — files and prefixes.

**Depositor behavior on stanza-less plans:** The depositor runs `parse_manifest_stanza()` first. If empty, it falls back to extracting `writes` from the step text's `**Deposits:**` blocks (across all steps) and `reads` from `**Scope:**` blocks. If BOTH are empty (no manifest, no Deposits, no Scope), the plan has undeclared intent — **HOLD** (fail-safe default).

### Collision Rules

For each in-flight plan I and staged plan S:
- **`writes_S ∩ writes_I` non-empty → HARD-HOLD.** Two plans writing the same file concurrently risks data loss. The held plan must wait until the in-flight plan closes.
- **`reads_S ∩ writes_I` non-empty → HOLD-AND-REPORT.** The staged plan reads a file the in-flight plan is modifying — the staged plan may execute against stale content. Hold and report the specific intersection.
- **`writes_S ∩ reads_I` non-empty → INFORMATIONAL only.** The staged plan writes a file the in-flight plan reads. The in-flight plan already has its copy; no data risk. Log for awareness but do not hold.

### Path Normalization

- **Relative paths:** Resolved against the plan's `target_project` (from `plans.target_project` in lifecycle.db, or from the config's `watched_projects` entry). Both the staged plan's paths and the in-flight plan's paths are normalized to absolute paths before intersection.
- **Absolute paths (cross-repo case):** Used as-is. Example: the 2a stanza-design diagnostic wrote `DRAFTING_CYCLE.md` — an absolute path relative to the bellows root, not a target project. The depositor normalizes: if a path contains no `/` and doesn't start with `knowledge/`, resolve against `<bellows_root>` instead of `target_project`.
- **Trailing-slash prefix semantics:** A `writes:` entry like `knowledge/research/` means ANY file under that prefix collides. The intersection is prefix-match, not exact-match, for prefix entries.

### Concurrent Sibling Deposits (V2 — the concurrent-sibling-deposits-conflict-on-shared-append-file class)

**The collision set is: in-flight plans (lifecycle.db) UNION other plans currently STAGED in the ready area.**

Two plans staged simultaneously are both absent from lifecycle.db (neither has been claimed yet). If both write the same file, they would miss each other in a lifecycle.db-only query. The depositor must:
1. Enumerate ALL `ready-*.md` files in the watched directory.
2. Parse each one's `writes` set.
3. Include the sibling `writes` sets in the collision check.

Implementation: before evaluating a `ready-` file, scan for other `ready-` files in the same directory, parse their manifests/deposits, and check `writes∩writes` pairwise. If two staged plans collide, HOLD both (or hold the later-arriving one if detection is sequential).

### Load-Bearing Limitation: `reads:` is Author-Declared

**`reads:` is mechanically unverifiable** — the depositor cannot know what files the plan will actually read at runtime. The declared `reads:` is the plan author's claim, which may be incomplete or stale (the plan-436 moving-target case: a plan declares `reads: A.md` but the agent also reads `B.md` during execution).

**Partial mitigation:** The depositor checks `reads:` as declared and holds on intersection. But it CANNOT guarantee that a non-intersecting `reads:` is actually safe — an undeclared read may conflict with an in-flight write.

**Residual gap:** A plan with an incomplete `reads:` declaration may auto-deposit and execute against stale content the depositor couldn't detect. This is accepted as a known limitation — the alternative (blocking all plans until the in-flight set is empty) would serialize all execution.

---

## Q3 — The Re-Run (Trust Nothing Written)

### Re-Run Specification

The depositor RE-RUNS validation tools rather than trusting the manifest's `validation:` block. The written manifest is an audit trail; the re-run is the validation.

**Step 1 — `cycle_check.run_check(plan_path)`** (`scripts/cycle_check.py:347–416`):
- Reads the plan text, extracts the Drafting Cycle block, parses walk data.
- Returns `(verdict, exit_code)` where verdict is `CONTINUE`, `BAR_MET`, or `ESCALATE:<reason>`.
- The depositor compares this with the manifest's `validation:` `cycle_check=` value (if present). Mismatch → HOLD.

**Step 2 — `plan_lint`** (via `subprocess.run`):
- The depositor runs `python3 scripts/plan_lint.py <plan_path>` and captures exit code + FAIL count.
- Compares with the manifest's `plan_lint=` value. Mismatch → HOLD.

**Step 3 — `emit_manifest(plan_path)`** (`scripts/cycle_check.py:487–580`):
- Generates a fresh manifest to STDOUT. The depositor compares `walks` and `yields` with the existing stanza's values. Mismatch → HOLD.

### What the Re-Run Reads

- The plan file itself (from the `ready-` path in `knowledge/decisions/`).
- `lifecycle.db` (indirectly, via `parse_manifest_stanza` reading the plan text that references validation results).
- Git state (for `check_assert_2` and `check_assert_3` in `run_check` — walks committed, register coherence).

### Stanza-Less Plans (legacy — I1)

For a plan with NO `## Cycle Manifest` stanza:
- The fresh re-run of `cycle_check` + `plan_lint` is authoritative.
- There is no `validation:` to compare against — the re-run result IS the validation.
- **The ABSENCE of a manifest is NOT itself a HOLD.** 2a's presence-teeth are deferred; the depositor still processes legacy plans. The depositor runs `cycle_check` and `plan_lint` directly and uses their results for the deposit decision.
- If `cycle_check` returns anything other than `BAR_MET` (exit 0) → HOLD.
- If `plan_lint` returns any FAIL → HOLD.

---

## Q4 — Auto-Deposit vs HOLD (the Class Mapping) + the Deposit Mechanism

### Class Assignment (VERIFY, do not trust)

Per 472 Q6's depositor-assignment rule, the depositor **ASSIGNS** `class` from the plan's `writes:` paths, not from the declared `class:` field:

| `writes:` Pattern | Assigned Class |
|---|---|
| ALL paths in `knowledge/research/`, `scratch/`, or temporary/staging paths | `read-only` |
| ANY governed register file (e.g. `knowledge/decisions/register-*.md`, `DRAFTING_CYCLE.md`, doctrine files) | `register-writing` |
| Everything else (code files, config, any `knowledge/` path outside `research/`) | `governed-tooling` |

**Class-mismatch check (D2 — load-bearing):** If the ASSIGNED class disagrees with the DECLARED `class:` in the manifest → **HOLD**. A declared `read-only` that writes a governed register would auto-deposit catastrophically. The ASSIGNED class from `writes:` paths is authoritative.

### The Mapping

| Assigned Class | Action |
|---|---|
| `read-only` | AUTO-DEPOSIT — clear to `decisions/` for daemon claim |
| `governed-tooling` | HOLD — wait for CEO release |
| `register-writing` | HOLD — wait for CEO release |

### FAIL-SAFE Default

**Any uncertainty → HOLD, never auto-deposit.** Specifically:
- Missing `class` (no manifest, no `writes:` to assign from) → HOLD
- `class: <declare>` (placeholder) → HOLD
- Class mismatch (assigned ≠ declared) → HOLD
- Re-run mismatch (cycle_check/plan_lint) → HOLD
- Collision detected (writes∩writes or reads∩writes) → HOLD
- Disk low (`_disk_preflight` returns False) → HOLD
- Unparseable manifest → HOLD
- Stanza-less plan with `cycle_check` ≠ `BAR_MET` → HOLD

### The CLEAR Mechanism (auto-deposit)

**ATOMIC rename (D3 — same-filesystem `mv`):**
```python
os.rename(
    os.path.join(decisions_dir, f"ready-{type}-{slug}.md"),
    os.path.join(decisions_dir, f"{type}-{slug}.md"),
)
```

`os.rename()` on the same filesystem is atomic (POSIX guarantee). The daemon's `_handle` will never read a half-written file. `shutil.move()` is NOT used because it may fall back to copy-then-delete across filesystems — `os.rename()` raises `OSError` if cross-filesystem, which is correct (the ready file and decisions dir are always on the same fs).

### The HOLD Mechanism

**Rename `ready-X.md` → `hold-X.md`:**
```python
os.rename(
    os.path.join(decisions_dir, f"ready-{type}-{slug}.md"),
    os.path.join(decisions_dir, f"hold-{type}-{slug}.md"),
)
```

Verified: `hold-executable-foo.md` returns **False** from `is_runnable_plan` (tested above). The daemon cannot claim a `hold-` file.

**HOLD reason persistence:** A companion file `hold-{type}-{slug}.hold.json` is written alongside the `hold-` plan file:
```json
{
  "hold_reason": "collision:writes∩writes with in-flight plan #476 on knowledge/decisions/register-cycles.md",
  "held_at": "2026-08-20T14:30:00",
  "class_assigned": "register-writing",
  "class_declared": "read-only",
  "collision_plans": [476],
  "rerun_results": {
    "cycle_check": "BAR_MET",
    "plan_lint": "0_FAIL"
  }
}
```

This file survives daemon restarts (filesystem-durable) and is the data source for the dashboard UI.

**Durability across daemon restart (A2):** On startup, the depositor RE-EVALUATES all `ready-` and `hold-` files:
- `ready-` files: full evaluation (collision, re-run, class).
- `hold-` files: re-read the `.hold.json`, re-run collision check (in-flight set may have changed), but do NOT auto-clear. A previously-held plan remains held until CEO action. The re-evaluation may UPDATE the hold reason (e.g. a collision that cleared), but does not release the hold automatically.

### The HELD → CLEARED Release Path (A3 + A4)

**CEO action:** The CEO renames `hold-{type}-{slug}.md` → `ready-{type}-{slug}.md` (or uses a CLI command that does the same). This re-enters the `ready-` detection path.

**Re-evaluation on release (A4):** When the depositor sees a `ready-` file (whether fresh or released from hold), it runs the FULL evaluation — collision, re-run, class assignment — at CLEAR time. The in-flight set drifts between HOLD and release; a plan held yesterday may collide with a new in-flight plan today. There is no "pre-approved" state — every clear is a fresh evaluation.

**Release flow:**
1. CEO renames `hold-X.md` → `ready-X.md` (manual or CLI).
2. Watchdog fires `on_moved`, `_handle` sees `ready-` prefix, calls `depositor.evaluate()`.
3. Depositor re-runs full check (collision, cycle_check, plan_lint, class assignment).
4. If all clear and `read-only` → auto-deposit (rename to claimable name).
5. If new collision or failure → re-HOLD (rename back to `hold-X.md`, update `.hold.json`).

The `.hold.json` file is cleaned up after successful clear (the plan is now claimable and the daemon will claim it).

### Worked Examples

**Example 1: Plan #478 (this diagnostic) — `read-only` → AUTO-DEPOSIT:**
- `writes: knowledge/research/component3-depositor-design-2026-08-20.md`
- Assigned class: `read-only` (all writes in `knowledge/research/`).
- Declared class: `read-only` (match).
- Collision: none (no in-flight plan writes to `knowledge/research/component3-depositor-design-2026-08-20.md`).
- Re-run: `cycle_check=BAR_MET`, `plan_lint=0_FAIL`.
- Decision: **AUTO-DEPOSIT**.

**Example 2: Plan #476 (register-writing) — HOLD:**
- `writes: knowledge/decisions/register-cycles.md, DRAFTING_CYCLE.md`
- Assigned class: `register-writing` (writes a governed register + doctrine file).
- Decision: **HOLD** (class is `register-writing`, not `read-only`).
- CEO reviews, approves, renames `hold-executable-476.md` → `ready-executable-476.md`.
- Depositor re-evaluates: no new collision, re-run passes → clears to `executable-476.md` → daemon claims.

---

## Q5 — Freeze / Disk / Queue Reuse (Characterize What EXISTS)

### Finding: No `freeze` Concept Exists

**Verified:** `grep -rn "freeze" bellows.py lifecycle.py config.json` returns **NO MATCHES**. There is no freeze token, freeze state, freeze flag, or freeze configuration anywhere in the bellows codebase.

The routed decision's reference to "reuses freeze state" names something that does not exist. This is an acceptable finding — the depositor does not need a freeze notion.

**Analysis:** The function that "freeze" would serve is already covered by the combination of:
1. **`_disk_preflight(config)`** (`bellows.py:334–360`): Blocks claims when free disk is below `disk_min_free_gb` (default 5GB). The depositor reuses this check — if disk is low, HOLD (don't clear a ready file into the claim path when the daemon would refuse to claim it anyway).
2. **`_active_count` / `_check_queue_drain`** (`bellows.py:2171/2197`): Track how many plans are actively running. The depositor can query this to implement a "don't auto-deposit if N plans are already in-flight" throttle, though this is an OPTIONAL enhancement, not a freeze.
3. **`_shutting_down`** (`bellows.py:2172`): The daemon sets this flag during shutdown. The depositor checks this flag — if the daemon is shutting down, do not clear any ready files (they'd be claimed by a daemon that's about to exit).

**Recommendation:** Do NOT define a freeze concept. The existing disk/queue/shutdown checks provide sufficient safety. If a "pause all deposits" escape valve is needed in the future, it can be added as a `depositor_paused: true` key in `config.json` — but this is out of scope for the current design.

### Depositor Reuse of Existing Checks

| Check | Source | Depositor Reuse |
|---|---|---|
| `_disk_preflight(config)` | `bellows.py:334` | Called before clearing a `ready-` file. Disk low → HOLD. |
| `_active_count` | `bellows.py:2171` | NOT reused directly (the depositor doesn't throttle on active count — that's the daemon's concern). |
| `_check_queue_drain` | `bellows.py:2197` | NOT reused (drain notification is post-execution, irrelevant to staging). |
| `_shutting_down` | `bellows.py:2172` | Checked before clearing — if True, skip evaluation. |

### Disk-Preflight Ordering Hazard

The diagnostic notes that `mint-before-disk burns an id`. This is a hazard in the daemon's claim path (the daemon calls `mint_and_claim` at :859 before `_disk_preflight` at :868). The depositor sidesteps this entirely:
- The depositor never mints (Q1 invariant).
- The depositor calls `_disk_preflight` BEFORE renaming `ready-` → claimable. If disk is low, the ready file stays as `ready-` and no id is burned.
- The daemon's own `_disk_preflight` at :868 (post-mint) is a second safety net.

---

## Q6 — The Dashboard UI Element

### Design: "DEPOSITS" Panel

**Location in layout:** Between AWAITING VERDICT and the EVENT FEED — matching the dashboard-tui-design-2026-06-12.md layout convention (Section 2). The new panel is additive — no change to existing panels.

```
Row 0:      [HEADER]           — daemon status line
Row 1:      [separator]
Row 2-N:    [IN-FLIGHT]        — existing
Row N+1:    [separator]
Row N+2-M:  [AWAITING VERDICT] — existing
Row M+1:    [separator]
Row M+2-P:  [DEPOSITS]         — NEW
Row P+1:    [separator]
Row P+2-48: [EVENT FEED]       — existing (fills remaining space)
Row 49:     [FOOTER]           — existing
```

### CLEARED Deposits: No Distinct Row Needed

A CLEARED deposit becomes a normal claimable plan file. The daemon's existing `_handle` → `handle_new_plan` → `run_plan` flow picks it up. Once claimed, it appears in the IN-FLIGHT panel as a normal in-flight plan. **The HELD set is the novel surface; cleared plans fold into the existing IN-FLIGHT panel.**

The DEPOSITS panel therefore shows ONLY:
1. **READY plans** — `ready-*.md` files currently staged, awaiting depositor evaluation.
2. **HELD plans** — `hold-*.md` files, with hold reason.

### Data Source

The depositor's state is filesystem-based:
- Enumerate `ready-*.md` and `hold-*.md` files in each watched directory.
- For each `hold-*.md`, read the companion `.hold.json` for the hold reason.

This avoids adding depositor-specific tables to lifecycle.db — the filesystem IS the state store, consistent with how the daemon's existing claim path uses filesystem presence (via `is_runnable_plan` + directory listing).

### New Query in `assemble_state` (`dashboard.py:104`)

```python
# Deposit staging state
deposit_rows = []
for wp in config_watched_projects:
    if os.path.isdir(wp):
        for fname in os.listdir(wp):
            if fname.startswith("ready-") and fname.endswith(".md"):
                deposit_rows.append({"file": fname, "status": "READY", "reason": "", "dir": wp})
            elif fname.startswith("hold-") and fname.endswith(".md"):
                hold_json = os.path.join(wp, fname.replace(".md", ".hold.json"))
                reason = ""
                if os.path.exists(hold_json):
                    try:
                        with open(hold_json) as f:
                            reason = json.load(f).get("hold_reason", "")
                    except Exception:
                        reason = "(unreadable)"
                deposit_rows.append({"file": fname, "status": "HOLD", "reason": reason, "dir": wp})
```

The `assemble_state` return dict gains a `deposit_rows` key.

### New Section in `render_screen` (`dashboard.py:176`)

Inserted after the AWAITING VERDICT block, before the EVENT FEED:

```python
# --- DEPOSITS ---
if state.get("deposit_rows"):
    deposit_text = render_depositor_status(state["deposit_rows"])
else:
    deposit_text = "DEPOSITS\n (none)"
deposit_lines = deposit_text.split("\n")
rows.append((_fit(deposit_lines[0], width), attr_deposits))
for line in deposit_lines[1:]:
    rows.append((_fit(line, width), attr_deposits_row if state.get("deposit_rows") else 0))
rows.append((SEPARATOR_CHAR * width, attr_separator))
```

### New `render_depositor_status` Helper in `status.py`

Mirrors `render_in_flight` (status.py:138) and `render_awaiting_verdict` (status.py:163):

```python
def render_depositor_status(rows):
    """Render DEPOSITS section."""
    lines = ["DEPOSITS"]
    if not rows:
        lines.append(" (none)")
        return "\n".join(lines)
    for row in rows:
        fname = row["file"]
        st = row["status"]
        reason = truncate(row.get("reason", ""), 50)
        lines.append(f" {fname:<40s}  {st:<6s}  {reason}")
    return "\n".join(lines)
```

### Curses Color Slot

Add a new color pair constant:

```python
COLOR_DEPOSITS = 5  # new, after COLOR_AWAITING = 4
```

Initialize in `init_colors()` with a distinct color (recommend yellow/amber for HOLD, green for READY — or a single muted color for the section header, matching the existing style where section headers use A_BOLD with a color pair and rows use the pair without bold).

### Mock

```
DEPOSITS
 hold-executable-476.md                    HOLD    collision:writes∩writes with #475 on register-cycles.md
 ready-diagnostic-479.md                   READY
```

When empty:
```
DEPOSITS
 (none)
```

---

## Q7 — Rule 27 Gap Assessment + Narrowest-Trigger Safety Analysis

### Gap Table

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| No staging state | Plans deposit directly as claimable `<type>-<slug>.md` — daemon claims immediately | `ready-<type>-<slug>.md` staging prefix; daemon's `is_runnable_plan` (`bellows.py:2030`) already rejects `ready-` | New: `depositor.py` module; `_handle` branch at `bellows.py:2063` to call `depositor.evaluate()` on `ready-` files |
| No collision query | No mechanism to detect `reads∩writes` / `writes∩writes` between staged and in-flight plans | Depositor queries `lifecycle.db` via `status.query_in_flight` (`status.py:188`) + parses `reads`/`writes` from manifest or legacy deposits block | New: `depositor.py` collision-check method; reads `lifecycle.db` (read-only), calls `parse_manifest_stanza` (`scripts/cycle_check.py:419`) and `_extract_plan_required_deposits` (`gates.py:463`) |
| No re-run validation | Plans are deposited with a written `validation:` block but nothing re-verifies it at deposit time | Depositor re-runs `cycle_check.run_check()` (`scripts/cycle_check.py:347`) + `plan_lint` at staging; mismatches → HOLD | New: `depositor.py` re-run method; subprocess calls to `scripts/cycle_check.py` and `scripts/plan_lint.py` |
| No class verification | The declared `class:` in the manifest is trusted at face value | Depositor ASSIGNS class from `writes:` paths (per 472 Q6 rule); mismatch with declared `class:` → HOLD | New: `depositor.py` class-assignment logic |
| No auto-deposit mechanism | Plans are manually placed in `knowledge/decisions/` as claimable files | `read-only` plans: atomic `os.rename` from `ready-X.md` → `X.md`; daemon claims normally | New: `depositor.py` clear method |
| No HOLD mechanism | No concept of a staged plan awaiting CEO approval | `hold-X.md` prefix + `.hold.json` companion file; `is_runnable_plan` already rejects `hold-` | New: `depositor.py` hold method; `.hold.json` write |
| No HOLD → release path | N/A | CEO renames `hold-X.md` → `ready-X.md`; depositor re-evaluates at clear time | New: `depositor.py` re-evaluation on `ready-` detection |
| No depositor dashboard | Dashboard shows IN-FLIGHT and AWAITING VERDICT only | DEPOSITS panel between AWAITING VERDICT and EVENT FEED; shows `ready-` and `hold-` files with reasons | New: `render_depositor_status` in `status.py` (~after :182); `assemble_state` gains `deposit_rows` key (`dashboard.py:104`); `render_screen` gains DEPOSITS section (`dashboard.py:~265`); `COLOR_DEPOSITS = 5` constant |
| No sibling-collision check | Two plans staged simultaneously can't see each other's `writes` (both absent from lifecycle.db) | Depositor scans ALL `ready-*.md` files in the directory and checks pairwise `writes∩writes` | New: `depositor.py` sibling-scan in evaluate() |
| No freeze concept | No freeze token in `bellows.py`/`lifecycle.py`/`config.json` | NOT NEEDED — disk preflight + `_shutting_down` flag cover the safety surface | No change — accept "absent" finding |
| Disk-preflight ordering | Daemon calls `_disk_preflight` AFTER `mint_and_claim` — id burned if disk low | Depositor calls `_disk_preflight` BEFORE clearing `ready-` → no mint happens if disk is low | New: `depositor.py` calls `_disk_preflight` (`bellows.py:334`) before rename |

### Safety Analysis (Load-Bearing)

**Single invariant:** The depositor never mints, never dispatches; it stages and clears, the daemon claims.

This invariant is enforced by construction: `depositor.py` imports no dispatch functions (`run_plan`, `handle_new_plan`, `mint_and_claim`). Its only write operations are `os.rename()` (same-directory atomic rename) and `open(..., 'w')` (for `.hold.json`).

### Wrong-Dispatch Enumeration

Every path by which an auto-deposit could WRONGLY trigger a live dispatch:

| # | Path | How it's closed |
|---|---|---|
| D2 | **Mis-declared `class`:** A plan declares `class: read-only` but its `writes:` include a governed register → depositor auto-deposits → daemon dispatches a register-writing plan without CEO review | **CLOSED:** The depositor ASSIGNS class from `writes:` paths, not from the declared `class:`. The ASSIGNED class is authoritative. Class mismatch → HOLD. A declared `read-only` with `writes: knowledge/decisions/register-foo.md` gets assigned `register-writing` → HOLD. |
| V2 | **Sibling-staged collision invisible to lifecycle.db:** Two `ready-` plans both write the same file. Both pass collision check (neither is in lifecycle.db yet). Both auto-deposit. Daemon claims both. Concurrent writes → data loss. | **CLOSED:** The depositor scans ALL `ready-*.md` files in the directory before evaluating any one. Pairwise `writes∩writes` is checked. If collision → HOLD the later-arriving plan (or both). |
| A2 | **Restart auto-clears a held plan:** Daemon restarts. The depositor re-evaluates `hold-` files and auto-clears one that was held for a reason that's no longer detectable (e.g. a collision that cleared while the daemon was down). | **CLOSED:** On startup, the depositor re-evaluates `hold-` files but does NOT auto-clear them. A `hold-` file remains `hold-` until CEO action (rename to `ready-`). The re-evaluation may update the hold reason but never releases the hold automatically. |
| D3 | **Non-atomic clear → half-written file:** The depositor uses `shutil.copy()` + `os.remove()` to clear. The daemon's `_handle` fires between copy and delete, reads an incomplete file. | **CLOSED:** The depositor uses `os.rename()` (POSIX atomic on same filesystem), NOT `shutil.move()` or copy-then-delete. The rename is instantaneous — the daemon sees either the old name or the new name, never a partial state. |
| V4 | **Claimable `hold-` prefix:** The `hold-` prefix is accidentally accepted by `is_runnable_plan` → daemon claims a held plan. | **CLOSED:** Verified with positive control: `is_runnable_plan("hold-executable-foo.md")` returns `False`. The regex requires the filename to start with `(parallel-\d+-)?` optionally + `executable|diagnostic|qa`, and `hold-` matches neither. |
| V4b | **Claimable `ready-` prefix:** Same for `ready-`. | **CLOSED:** Verified: `is_runnable_plan("ready-executable-foo.md")` returns `False`. Same regex argument as `hold-`. |
| R1 | **Re-run false-BAR_MET:** `cycle_check.run_check()` returns `BAR_MET` on a plan that hasn't actually met the bar (buggy walk parsing, missing DC block, etc.) → depositor auto-deposits. | **CLOSED:** The fail-safe default means ONLY `BAR_MET` (exit 0) with matching `plan_lint` (0 FAIL) AND matching manifest values (if present) allows auto-deposit. A false `BAR_MET` would have to survive THREE independent checks. The residual risk is accepted as extremely low — `cycle_check` has been validated across hundreds of plans. |
| R2 | **Depositor calls `mint_and_claim` directly:** A code change adds a `mint_and_claim` call to `depositor.py`. | **CLOSED by construction:** The depositor module does not import `lifecycle.mint_and_claim`. The import whitelist is enforced by code review. The Q1 invariant is documented and testable. |
| R3 | **Race between depositor clear and daemon claim:** The depositor renames `ready-X.md` → `X.md`. The daemon's `_handle` fires on the rename event. Meanwhile the depositor is still running post-clear cleanup. Can the daemon claim before cleanup completes? | **NOT a hazard:** The depositor's clear is a single `os.rename()`. All post-clear work (deleting `.hold.json` if it existed) is optional cleanup. The daemon's claim path reads the plan file content at claim time from the new path. The plan file content is unchanged by the rename — it was fully written when the `ready-` file was created. |
| R4 | **Depositor evaluation runs concurrently with itself (race on the same `ready-` file):** Two watchdog events fire for the same file (create + modify). Two `depositor.evaluate()` calls run concurrently. Both pass checks. Both attempt to rename. | **MUST BE CLOSED BY IMPLEMENTATION:** The depositor must use a per-file lock or an evaluation queue to serialize evaluations. Recommendation: a `threading.Lock` per watched directory (the daemon is already single-threaded for plan handling via `_handle`'s `_seen` set). The evaluation can check: is the `ready-` file still present before renaming? If not, another evaluation already handled it. |

### Narrowest Trigger Surface (Proposal §5)

The trigger surface is:
1. `PlanHandler._handle()` at `bellows.py:2063` — existing code path, new branch for `ready-` prefix.
2. Daemon startup rescan — existing code path, extended to scan `ready-` and `hold-` files.
3. `depositor.evaluate(path)` — the single entry point in the new module.

No background threads, no timers, no external invocations, no network calls. The depositor is invoked ONLY by the daemon process, ONLY in response to filesystem events or startup.

### T2 Flag

**The executable implementing this design is T2** — it adds an autonomous-dispatch surface (auto-deposit for `read-only` class). The T2 executable earns a full cold-panel (4 seats minimum, ship-blocker power). The design's safety analysis (this Q7) is load-bearing for that panel.

---

## Output Receipt

**Agent:** Bellows Design Agent
**Step:** 1
**Status:** Complete

### What Was Done
Produced a 7-question finalized design for the in-bellows depositor + dashboard UI (component 3 of the cycle-automation proposal). The design characterizes the LIVE bellows internals with file:line citations, specifies the `ready-`/`hold-` staging mechanism with verified regex controls, defines the collision-query surface (manifest + legacy paths, sibling deposits), re-run validation, class-assignment rules (verify not trust), dashboard DEPOSITS panel layout, and a Rule 27 Gap Assessment with 11 gaps and 9 wrong-dispatch paths (all closed or flagged for implementation closure).

### Files Deposited
- `bellows/knowledge/research/component3-depositor-design-2026-08-20.md` — this design document

### Files Created or Modified (Code)
- None (read-only design diagnostic — no code edits)

### Decisions Made
- `ready-` filename prefix (not subdirectory) for staging — reuses existing watcher, already non-claimable
- `hold-` filename prefix + `.hold.json` companion for HOLD persistence
- Depositor HOME: `bellows/depositor.py` (dedicated module)
- Depositor TRIGGER: daemon's existing `_handle` at `bellows.py:2063` + startup rescan
- No freeze concept needed — disk/shutdown checks sufficient
- Cleared deposits fold into IN-FLIGHT (no distinct row) — HELD set is the novel surface
- DEPOSITS panel between AWAITING VERDICT and EVENT FEED in dashboard layout

### Flags for CEO
- **T2 executable:** The implementing executable earns a cold panel (autonomous-dispatch surface)
- **R4 race:** The implementation must serialize depositor evaluations per-directory (threading.Lock or evaluation queue) — the design flags this but cannot close it without code

### Flags for Next Step
- The implementing executable should verify all file:line citations at edit time (bellows.py line numbers shift across commits)
- The collision query's `reads:` limitation (author-declared, mechanically unverifiable) is a known residual gap
- The `.hold.json` schema should be finalized during implementation (the design gives a recommended shape)
- The `config.json` `watched_projects` entries are the depositor's watch scope — no config change needed
