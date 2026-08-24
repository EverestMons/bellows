# E3 Design — Deposit Watcher Receipts

**Date:** 2026-08-24 | **Source plan:** diagnostic-515 | **Provenance:** bellows HEAD `0fe92fa` | **Scope:** read-only design document — no code modified

**Attestation boundary (audit verbatim, non-negotiable):** *"a receipt written at deposit time proves the watcher was ARMED, not that it stayed alive. Liveness of a session-local monitor is not externally verifiable, and an E3 that claims otherwise would be a printed check wearing a gate's name."*

**Consumed without re-derivation (T-7):** `eluvian-path-audit-2026-08-24.md` §E3 (509-corrected), `eluvian-path-rulings-2026-08-24.md`. **Baton correction consumed as GIVEN:** receipts key by SLUG (`plans.deposit_placeholder_name`), never by a predicted numeric id — the 512/513 id collision is the measured reason.

---

## Re-derived Numbers

All G-pins re-derived 2026-08-24 from bellows HEAD `0fe92fa`. Values that SUPERSEDE the plan are marked.

| id | pin | plan value | re-derived | supersedes? | probe |
|---|---|---|---|---|---|
| G1 | deposit-receipt artifacts | 0 (absence earned) | **0** | no | `grep -cF 'receipt'` → depositor.py **0**, wrap_check.py **0**, wrap_stop_hook.py **0**, bellows.py **2** (both `receipt_status` at :995/:1127 — CLI cost field, NOT deposit receipts). Positive control: `grep -cF 'hold-'` depositor.py = **6** |
| G2 | session id reaches hook layer but NOT wrap_check | plumbing gap | **plumbing gap** | no | wrap_stop_hook.py:80-91 extracts `session_id`; :70-77 validates `[A-Za-z0-9-]+`; :186-188 uses it. :207-210 invokes wrap_check.py with NO arguments. wrap_check.py: `grep -c 'sys.argv'` = **0**, `grep -c 'import os'` = **0** |
| G3 | clearance record shape | lifecycle.py:170-183 | **lifecycle.py:170-183** | no | `clearances(plan_path, content_hash, assigned_class, cleared_by, cleared_at, consumed_at)`; partial-unique `(content_hash, plan_path) WHERE consumed_at IS NULL`; INSERT at :207; consume at :233/:268. No session column, no slug column |
| G4 | content hash algorithm | depositor.py:538 | **depositor.py:538** | no | `hashlib.sha256(plan_bytes).hexdigest()` over RAW BYTES |
| G5 | lifecycle.db sole writer is daemon | True | **True** | no | All `sqlite3.connect` calls in lifecycle.py are made from daemon-process code (depositor.py imports lifecycle; bellows.py imports lifecycle). The Planner writes into bellows via FILES (verdicts/resolved/), never via the DB |
| G6 | sidecar idiom | depositor.py:546, :570-583 | **depositor.py:546, :570-583** | no | `hold-<name>.hold.json` `{"hold_reason", "held_at"}` — state file + JSON sidecar |
| G7 | wrap-hook test surface | 20 + 28 | **20 + 28** | no | `grep -cE '^def test\|^    def test'` test_wrap_hooks.py = 20, test_wrap_sentinel.py = 28 |
| G8 | clearances rows; id_sequence | 0 rows; next 515 | **1 row; next 516** | **YES** | `sqlite3 "file:lifecycle.db?mode=ro"` — 1 clearance row exists (activation canary arm (ii) deposited), next_id = 516. Plan prediction was pre-canary |

---

## D-1 — The Receipt Artifact

### Form: FILE

**Constraint (G5):** lifecycle.db's sole writer is the daemon. The Planner writes the receipt from its own session process. A lifecycle.db row would break the sole-writer model unless the daemon exposes a receipt-writing API — unnecessary complexity for a simple attestation. The receipt is a **file**.

The Planner already writes files into the bellows tree: `verdicts/resolved/` files are written by the Planner session, consumed by the daemon (bellows.py:2441-2557), and committed at wrap step [2] (wrap_check.py:98-103). A receipt file mirrors this proven lifecycle.

### Location: `bellows/receipts/`

**Candidates weighed:**

| option | survives rename lifecycle? | Planner-writable? | wrap_check-readable? | slug-keyed identity? |
|---|---|---|---|---|
| **(a) `bellows/receipts/`** | **YES** — decoupled from plan renames entirely; slug identity is stable across ready- → bare → in-progress- → verdict-pending- → Done/ | YES — same write model as verdicts/resolved/ | YES — stdlib Path/json only | YES — filename carries slug |
| (b) sidecar in decisions/ | **NO** — depositor.py:544 renames `ready-X.md` → `X.md`; daemon renames onward to `in-progress-`, `verdict-pending-`, `Done/`. A sidecar `receipt-X.json` adjacent to `ready-X.md` is orphaned at the first rename unless the renamer tracks it. Every rename site (depositor._clear at :544, daemon claim at bellows.py:863-864, verdict consumption at :2488-2494) would need receipt-rename logic. Fragile across 5+ rename sites | YES | YES (after locating it) | Only if renamed in lockstep |

**Decision: (a) `bellows/receipts/`.** The `verdicts/resolved/` precedent proves the Planner-writes-into-bellows lifecycle works. A `receipts/` directory mirrors it: Planner writes a JSON file, wrap_check reads it, wrap step [2] commits it.

### Naming: `receipt-<slug>-<session_id>.json`

The filename encodes slug AND session_id so two sessions depositing concurrently write distinct files by construction (D-4). The slug is `plans.deposit_placeholder_name` — the identity that survives all renames.

### Content shape

```json
{
  "slug": "<deposit_placeholder_name>",
  "content_hash": "<sha256 hex of raw plan bytes>",
  "session_id": "<session_id>",
  "armed_at": "<ISO 8601 timestamp>",
  "watcher": "gate-watcher armed in depositing session",
  "attestation_boundary": "This receipt proves the watcher was ARMED at write time. It does NOT prove the watcher stayed alive. Liveness of a session-local monitor is not externally verifiable."
}
```

- `content_hash`: sha256 of raw bytes (G4, depositor.py:538) — cross-checkable against `clearances.content_hash`
- `session_id`: shape-validated `[A-Za-z0-9-]+` (matching wrap_stop_hook.py:70-77)
- `attestation_boundary`: the audit's sentence, embedded in every receipt so each self-documents what it does NOT prove

### Git status: committed at wrap step [2]

Receipts are committed to the bellows repo alongside verdicts at wrap step [2]. The wrap_check step [2] porcelain scoping at wrap_check.py:98 currently scopes to `verdicts/resolved` — the receipts check is a **new check group** (see D-3), not governed by this existing scope. The `receipts/` directory does NOT need wrap_check's [2/bellows] scope to expand — it has its own step.

### Interaction with wrap_check porcelain scoping

wrap_check.py:98 scopes step [2] to `verdicts/resolved`. The receipts directory is orthogonal — the receipt-check step reads receipt FILES for their content, not git porcelain status. Uncommitted receipts would show up in a `porcelain(BELLOWS, "receipts")` check, which the executable may choose to add as a sub-check of [2/bellows] to enforce commit discipline — but the primary receipts step (D-3) checks receipt EXISTENCE and content, not git status.

---

## D-2 — The Writer Tool

### File: `bellows/tools/deposit_receipt.py`

Mirrors the `tools/clear_plan.py` (tools/ dir precedent). Run by the Planner AT deposit time as part of arming the watcher.

### Validations before writing

1. **Plan file exists** in a watched `decisions/` directory (cross-check against `config.json` `watched_projects`, same list the daemon uses; config.json has 10 entries at G8 re-derivation)
2. **Hash match:** tool computes `hashlib.sha256(Path(plan_path).read_bytes()).hexdigest()` and compares against the `content_hash` argument; mismatch → refuse (the file changed between the Planner's read and the tool's run)
3. **Slug derivation:** slug derived from the filename (strip `ready-` prefix if present, strip `.md` suffix) matches the `slug` argument; mismatch → refuse
4. **Session ID present and shape-valid:** `re.fullmatch(r'[A-Za-z0-9-]+', session_id)` — None/empty/invalid → refuse loudly

### Idempotency

**Refuse** if a receipt with the same slug + content_hash already exists (any session). Rationale: one receipt per deposit event. A corrected plan deposited under the same slug has a DIFFERENT content hash (the bytes changed), so it gets a new receipt — this is correct behavior. A re-run of the same deposit (same slug, same hash) is a duplicate that should not overwrite or append.

A second deposit of a DIFFERENT plan under the same slug (different hash) writes a new receipt file. The wrap_check step sees both and matches each to its clearance by hash.

### Output on success

Prints the receipt path (absolute) so the depositing session can cite it:

```
Receipt written: /Users/marklehn/Developer/GitHub/bellows/receipts/receipt-<slug>-<session_id>.json
```

### Refusal messages (loud, to stderr)

- `ERROR: plan file does not exist: <path>`
- `ERROR: plan file not in a watched decisions/ directory`
- `ERROR: content hash mismatch — file changed since read (expected <X>, got <Y>)`
- `ERROR: slug mismatch — derived '<X>' from filename, expected '<Y>'`
- `ERROR: session_id missing or invalid (must match [A-Za-z0-9-]+)`
- `ERROR: receipt already exists for slug=<X> hash=<Y> — duplicate deposit`

### Ordering contract: receipt BEFORE the `ready-` rename

The daemon claims within seconds of a file becoming claimable (the watchdog + rescan loop at bellows.py:2400-2416 fires continuously). The `ready-` → bare rename (depositor.py:544, the `_clear` method) is what makes a plan claimable — it is the moment `is_runnable_plan` returns True and `has_clearance` finds the record.

**The receipt MUST be written BEFORE the depositor clears the plan.** The depositing session's ritual is:

1. Write the plan as `ready-<slug>.md`
2. Write the receipt via `deposit_receipt.py` (attesting the watcher is armed)
3. The depositor evaluates and clears → renames `ready-` to bare name → daemon claims

If the receipt were written AFTER the clear, a race window exists: the daemon claims and begins execution before the receipt exists, and a wrap check mid-execution would find the deposit but no receipt — a false negative. Writing BEFORE the clear eliminates this class entirely. No claim can precede attestation.

**Cost of this ordering:** the receipt exists for a plan that may then be HELD (depositor refuses to clear). A held plan's receipt is harmless — the wrap check matches receipts to clearances (D-3), and a held plan has no clearance, so the receipt is inert. It will be retired when the plan is eventually cleared (new receipt for the new hash) or abandoned (D-4 retirement).

### Attestation wording

The tool's success output says **"armed"** and never **"alive"**:

> `Receipt written: receipt-<slug>-<session_id>.json — watcher armed (not a liveness claim)`

The `watcher` field in the JSON is `"gate-watcher armed in depositing session"` — never `"gate-watcher alive"` or `"gate-watcher running"`.

---

## D-3 — The Wrap-Check Step

### Exact semantics: "every deposit made BY THIS SESSION has a receipt"

The audit's sentence — *"every deposit made this session has a receipt"* — is implemented as a session-scoped check.

### Truth sources with honest boundaries

| truth source | what it proves | what it cannot prove | where |
|---|---|---|---|
| (i) Receipts in `bellows/receipts/` | Arming for deposits that HAVE receipts | Cannot catch a receipt-less deposit — absence of evidence is not evidence of absence | `receipts/receipt-<slug>-<session_id>.json` |
| (ii) `clearances` rows (lifecycle.py:207, `cleared_at`) | That a deposit was cleared (the depositor gate passed) | No session attribution (G3) — a clearance does not say WHICH session deposited it; no slug column | lifecycle.db `clearances` table |
| (iii) `hold-*.hold.json` `held_at` (G6) | That a plan was held and when | A held plan was never cleared, so it was never claimable — the watcher attestation gap (S9) is about deposits that REACHED execution, not held ones | decisions/ dirs, depositor.py:570-583 |
| (iv) `plans.deposit_placeholder_name` + `created_at` | That a plan was claimed by the daemon, and its slug identity | Daemon-side record — the Planner has no write access; timing is claim time, not deposit time | lifecycle.db `plans` table |
| (v) git history of decisions/ dirs | Full rename history of plan files | Heavy probe; would need git log parsing per watched dir; overkill for a real-time check | git |

### The check algorithm

**When session_id IS provided (normal wrap):**

1. Enumerate all receipt files in `bellows/receipts/` where `receipt.session_id == session_id`
2. For each receipt: verify the receipt's `content_hash` matches a clearance record in `clearances` (lifecycle.py read-only query). A receipt with no matching clearance is a held/abandoned deposit — **skip with a note** (not a failure)
3. Enumerate clearances whose `cleared_at` falls within the session window (from the wrap sentinel's creation time to now). For each clearance: check if a receipt exists with `receipt.content_hash == clearance.content_hash` AND `receipt.session_id == session_id`
4. A clearance with no matching receipt from THIS session is the gap. **But:** clearances have no session_id column (G3). A clearance from ANOTHER session in the same window would false-positive. This is the honest boundary — the check is a NARROWING of S9, not a guarantee

**Failure message:** `[2r/receipts] N cleared deposit(s) in session window without a matching receipt — arm a watcher before depositing.`

**When session_id is NOT provided (manual `python3 wrap_check.py`):**

The step **SKIPS with a printed note:**

```
[2r/receipts] SKIPPED — no session_id provided; receipt check requires session context.
```

Rationale: a step that false-blocks a fresh session on a PRIOR session's deposits re-creates the trap class the lock is FAIL-OPEN against (wrap_check.py:12-13). Without a session_id, the check cannot distinguish this session's deposits from prior sessions'. Skipping is safer than guessing.

### The central tension: D-3 vs D-4

**The tension:** catching a receipt-less deposit needs a global view of deposit-shaped records (clearances carry no session attribution, G3). The anti-foreign-block property (D-4) forbids blocking THIS session's wrap on ANOTHER session's deposits.

**Resolution:** The check uses the session_id to filter receipts (receipt files carry session_id in their filename and content). Clearances in the session window that lack a matching receipt from THIS session are reported as **warnings**, not **failures**, when multiple sessions may have been active (detected by the existence of foreign-session receipts in the same window or foreign sentinels). This preserves D-4: a foreign session's receipt-less deposit produces a warning, never a block.

If the check cannot distinguish (no session_id, or the window contains ambiguous clearances), it degrades to SKIP rather than false-blocking. The wrap is allowed to proceed, and the warning is printed. This is a narrowing of S9 (from "no verification at all" to "session-scoped verification with honest degradation"), which is the ceiling the audit accepts.

**The other option's cost:** a strict mode that blocks on ANY receipt-less clearance (regardless of session) would catch more gaps but would false-block wraps when another session deposited without a receipt. This violates D-4 and re-creates the anti-hijack problem (wrap_stop_hook.py:163-177). Rejected.

### Session-id plumbing: `sys.argv[1]`

**wrap_stop_hook.py:207-210 change (executable site):**

Current:
```python
res = subprocess.run(
    [sys.executable, str(CHECK)],
    capture_output=True, text=True, timeout=120,
)
```

Executable target:
```python
res = subprocess.run(
    [sys.executable, str(CHECK), session_id or ""],
    capture_output=True, text=True, timeout=120,
)
```

**wrap_check.py change (executable site):**

`check()` gains an optional `session_id` parameter:
```python
def check(session_id: str | None = None) -> list[str]:
```

`main()` reads `sys.argv[1]` if present:
```python
def main() -> int:
    session_id = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    try:
        fails = check(session_id)
    ...
```

This is the interface E5 consumes unchanged — E5 adds session-id keying to the 3b gate, reading the same `session_id` parameter.

### The SessionStart arm (wrap_debt_hook.py)

wrap_debt_hook.py:82-83 also invokes `wrap_check.py` with no arguments. At SessionStart, the session_id is the NEW session's. A prior session's deposits can never match it — the receipts step is vacuously green (no deposits from this new session exist yet).

**What the debt hook passes:** the session_id as argv[1], for plumbing symmetry and so the receipts step's SKIP message distinguishes "no id" from "new session, no deposits."

**wrap_debt_hook.py:80-83 change (executable site):**

Current:
```python
res = subprocess.run(
    [sys.executable, str(CHECK)],
    capture_output=True, text=True, timeout=120,
)
```

Executable target:
```python
res = subprocess.run(
    [sys.executable, str(CHECK), session_id or ""],
    capture_output=True, text=True, timeout=120,
)
```

At SessionStart, the step reports: `[2r/receipts] OK — no deposits in this session (session <id>, SessionStart).` A receipt-less deposit from a dead prior session is visible ONLY via the clearance truth source (ii) — the time-window probe would catch it if run with the dead session's id, but no living session holds that id. **This is the honest boundary:** a receipt-less deposit from a session that ended without wrapping is invisible to the receipts step in any subsequent session. It is visible via the debt hook's OTHER checks (uncommitted Done/ files, unpushed commits) only if the plan completed and was moved to Done/ — a plan that died mid-flight without reaching Done/ leaves no debt signal beyond the clearance row and any orphaned receipt.

### FAIL-OPEN preservation

`check()` has no `try` of its own — the FAIL-OPEN catch is `main()`'s try at wrap_check.py:152-155, wrapping the whole `check()` call. An unhandled exception in the receipts step silently allows the ENTIRE wrap, discarding every other group's verdict.

**The receipts step therefore handles its own exceptions:**

- **Malformed receipt JSON:** `try/except json.JSONDecodeError` → named message: `[2r/receipts] WARNING: malformed receipt file <path> — skipped (not a failure).` Continues checking other receipts.
- **Unreadable receipts directory:** `try/except (OSError, PermissionError)` → `[2r/receipts] SKIPPED — receipts directory unreadable.` Not a failure.
- **lifecycle.db unreadable for clearance cross-check:** `try/except` on the sqlite3 read-only open → `[2r/receipts] SKIPPED — lifecycle.db not readable for clearance cross-check.` Degrades to receipt-only counting (no gap detection vs clearances).

None of these exceptions propagate to the outer catch. The step degrades to SKIP or WARNING, never to an unhandled throw.

---

## D-4 — Receipt Lifecycle and Concurrency

### Retirement: on plan close

Receipts are retired when the plan they attest reaches a terminal state (`closed` or `halted` in lifecycle.db). The daemon, as part of plan-close bookkeeping, moves the receipt to `receipts/archived/` (or deletes it — the executable decides; archived is preferred for auditability).

**Not append-only.** An unbounded receipts directory accumulates one file per deposit across all sessions. With 10 watched projects and frequent deposits, this grows without bound. Retirement on plan close keeps the active set small (only receipts for in-flight plans). Archived receipts are available for forensic review but do not participate in the wrap check.

**Stale receipts (plans that died mid-flight):** A plan moved to `halted-` or `parked-` leaves its receipt behind. The wrap check ignores receipts for plans not in an active clearance state (no unconsumed clearance → receipt is inert). Cleanup: the daemon's periodic sweep (or a manual tool) moves orphaned receipts to `archived/` when the plan has been halted/parked for longer than a threshold (e.g., 7 days). This is a maintenance convenience, not a correctness requirement.

### What the wrap check does with OTHER sessions' receipts

The wrap check reads receipts matching `session_id == this_session`. Other sessions' receipts are **ignored** — they are not read, not counted, not reported as failures.

This follows the anti-hijack discipline of wrap_stop_hook.py:163-177: one session's wrap must never be blocked by another session's state. A foreign session's receipt-less deposit does NOT block this session's wrap. It may produce a **warning** (if a clearance in the session window has no matching receipt from any session), but never a failure.

### Concurrency: collision-free by construction

Receipt filename: `receipt-<slug>-<session_id>.json`

Two sessions depositing concurrently:
- Session A deposits `ready-foo.md` → writes `receipt-foo-<session_A_id>.json`
- Session B deposits `ready-bar.md` → writes `receipt-bar-<session_B_id>.json`

Filenames differ by slug AND session_id. No collision.

Two sessions depositing the SAME slug (e.g., a corrected re-deposit):
- Session A: `receipt-foo-<session_A_id>.json` with hash H1
- Session B: `receipt-foo-<session_B_id>.json` with hash H2

Filenames differ by session_id. Content differs by hash. No collision. The depositor's collision check (depositor.py:148) would hold the second deposit anyway, but the receipt layer is safe regardless.

This eliminates the shared-append-file collision class from the 2026-08-24 concurrent-deposit incident — there is no shared file; each session writes its own file.

---

## D-5 — Coordination and Portability Fences

### ROOT-constant idiom

E3 follows `wrap_check.py:36-39`'s existing pattern:

```python
ROOT = Path("/Users/marklehn/Developer/GitHub")
BELLOWS = ROOT / "bellows"
```

The receipts directory path is derived from `BELLOWS`:

```python
RECEIPTS = BELLOWS / "receipts"
```

E3 adds **NO env reads** to `wrap_check.py`. The file remains structurally incapable of env reads (no `import os`, no `os.environ`). Any machine-pinned path E3 introduces is declared as a new row for the portability census:

| new constant | file | derived from | census row |
|---|---|---|---|
| `RECEIPTS = BELLOWS / "receipts"` | wrap_check.py | `BELLOWS` (which derives from `ROOT`) | **new row**: inherits ROOT's pinning; no independent resolution needed |

The writer tool (`tools/deposit_receipt.py`) uses the bellows project root to locate `receipts/` — it resolves this from its own `__file__` path (same pattern as `CHECK = Path(__file__).with_name("wrap_check.py")` in wrap_stop_hook.py:35), NOT from a hardcoded absolute path. This is portable by construction.

### E5 interface: session_id as argv[1]

The argv plumbing (D-3) is designed once:

```python
# wrap_check.py
def check(session_id: str | None = None) -> list[str]:
    ...
def main() -> int:
    session_id = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    ...
```

E5 (session-id keying of the 3b gate) consumes the same `session_id` parameter in `check()`. No new plumbing needed — E5 uses the id D-3 already passes.

### Sequencing: no collision with the 512 portability executable

The portability executable (from diagnostic-512's census) changes how existing constants are resolved — it makes `ROOT`, `MEMORY`, etc. configurable via env vars. E3 adds new files (`receipts/` directory, `tools/deposit_receipt.py`) and a new check group (`[2r/receipts]`) in `wrap_check.py`.

If the portability executable lands between this design and E3's build:
- E3's `RECEIPTS = BELLOWS / "receipts"` derives from `BELLOWS`, which derives from `ROOT`. If the portability fix makes `ROOT` configurable, `RECEIPTS` inherits that configuration automatically — no conflict.
- E3's new check group is additive code (a new function called from `check()`). The portability fix modifies existing constant declarations. No overlap.

**Sequencing claim: E3 and 512's executable can land in either order without conflict.**

### Doctrine cross-reference

ELUVIAN_PATH.md cites the receipt in two places:

1. **Stage 2, line 61:** `"Deposit receipt (proves watcher was armed)"` — listed in the artifacts section. **Present and correct.** No edit needed.
2. **Stage 5, lines 117-123:** The wrap completion lock lists four check groups (project repos, bellows, governance root, memory repo). **No receipt-check step is listed.** The receipts step designed in D-3 is a new check group that Stage 5 does not yet describe.

**Follow-up needed:** ELUVIAN_PATH.md Stage 5 needs a line added to the wrap completion lock gates describing the receipt-check step. This is a `shop-infra` class write — listed in the gap table (Rule 27), not done here.

---

## D-6 — Test Plan

### Unit test surface (new tests)

| test | what it verifies | file |
|---|---|---|
| receipt write round-trip | `deposit_receipt.py` writes valid JSON; re-read matches all fields | `tests/test_deposit_receipt.py` |
| tool refusal: no plan file | tool refuses when plan path doesn't exist | same |
| tool refusal: not in watched dir | tool refuses when plan path is outside `config.json` `watched_projects` | same |
| tool refusal: hash mismatch | tool refuses when computed hash differs from argument | same |
| tool refusal: slug mismatch | tool refuses when derived slug differs from argument | same |
| tool refusal: invalid session_id | tool refuses on None/empty/invalid-shape session_id | same |
| tool refusal: duplicate receipt | tool refuses when receipt for same slug+hash exists | same |
| wrap_check receipts step: pass | session has deposits, all have receipts → no failure | `tests/test_wrap_hooks.py` or new `tests/test_wrap_receipts.py` |
| wrap_check receipts step: fail | session has deposit without receipt → failure message | same |
| wrap_check receipts step: no session_id | invoked without session_id → SKIP message, not failure | same |
| wrap_check receipts step: FAIL-OPEN on malformed receipt | corrupted receipt JSON → WARNING, not unhandled exception | same |
| anti-foreign-block | foreign session's receipt-less deposit does NOT block this session's wrap | same |
| receipts step with no receipts dir | `receipts/` doesn't exist → SKIP, not crash | same |

### Existing tests that must pass unchanged

- **G7:** `tests/test_wrap_hooks.py` = **20 tests**, `tests/test_wrap_sentinel.py` = **28 tests** — total **48 tests** in the wrap-hook surface
- **Full suite:** **1288 tests** collected (re-derived 2026-08-24 via `python3 -m pytest --collect-only`)

### Consumer sweep: who parses wrap_check's output

| consumer | where | what it reads | sees new message class? |
|---|---|---|---|
| wrap_stop_hook.py | :207-246 | `res.returncode` (0/1) + `res.stdout` (relayed as block reason) | **YES** — `[2r/receipts]` messages appear in stdout relayed to the model. No parsing of message content; stdout is passed as-is. No code change needed |
| wrap_debt_hook.py | :82-93 | `res.returncode` (0/1) + `res.stdout` (injected as context) | **YES** — same mechanism. `[2r/receipts]` messages appear in injected context. No parsing of content; passed as-is |
| test_wrap_hooks.py | 20 tests | Various — some assert exact stdout strings, some assert returncode only | **POSSIBLY** — tests asserting exact stdout strings may see new `[2r/receipts]` lines. The executable must verify each test's assertions. Tests asserting only on returncode are unaffected |
| test_wrap_sentinel.py | 28 tests | Various — sentinel creation/removal, hook dispatch | **UNLIKELY** — these test sentinel lifecycle, not wrap_check message content |

---

## D-7 — Open Questions

**No new CEO ruling is required.** All design decisions are settled within the constraints of the audit, the baton correction (slug-keyed receipts), and the existing code's measured properties. The following are noted for transparency:

1. **Clearances have no session_id column (G3).** The wrap_check receipts step uses a time-window heuristic as a consequence. Adding a `session_id` column to `clearances` would make the check precise — but this is a lifecycle.db schema migration, a write-model change to a Tier-3 shared surface. The heuristic is sufficient for E3's scope (narrowing S9 from unverifiable to armed-and-attested). If the CEO rules a schema migration is warranted, it becomes a separate diagnostic (not E3's scope).

2. **Receipt retirement mechanism.** D-4 specifies retirement on plan close, but the exact mechanism (daemon moves to `receipts/archived/` vs. deletes vs. lifecycle callback) is an implementation detail the executable resolves. The design fence: retirement MUST NOT leave the `receipts/` directory unbounded, and archived receipts MUST NOT participate in the wrap check.

3. **Doctrine Stage 5 edit.** ELUVIAN_PATH.md needs a line added to the Stage 5 wrap completion lock section describing the receipt-check step. This is a `shop-infra` write routed as a follow-up — see the gap table below.

---

## Rule 27 Gap Table

Every code-change site the executable will touch, grounded in file:line.

| # | file | site | change | grounding |
|---|---|---|---|---|
| 1 | `bellows/receipts/` | new directory | Create `receipts/` directory for receipt JSON files | D-1: receipt location decision |
| 2 | `bellows/tools/deposit_receipt.py` | new file | Writer tool: validates, writes receipt JSON, prints path | D-2: writer tool spec |
| 3 | `hooks/eluvian/wrap_check.py` | `check()` function body (after :147, before `return fails`) | Add `[2r/receipts]` check group: enumerate receipts, cross-check clearances, session-scoped | D-3: wrap_check step |
| 4 | `hooks/eluvian/wrap_check.py` | `main()` at :151-155 | Add `sys.argv[1]` parsing for session_id, pass to `check()` | D-3: session-id plumbing |
| 5 | `hooks/eluvian/wrap_check.py` | `check()` signature at :80 | Add `session_id: str \| None = None` parameter | D-3: session-id plumbing |
| 6 | `hooks/eluvian/wrap_stop_hook.py` | :207-210 (subprocess.run call) | Add `session_id or ""` as argv[1] to wrap_check invocation | D-3: session-id plumbing (G2 gap closure) |
| 7 | `hooks/eluvian/wrap_debt_hook.py` | :80-83 (subprocess.run call) | Add `session_id or ""` as argv[1] to wrap_check invocation | D-3: SessionStart arm |
| 8 | `tests/test_deposit_receipt.py` | new file | Unit tests for receipt write/read, tool refusals, idempotency | D-6: test plan |
| 9 | `tests/test_wrap_hooks.py` or `tests/test_wrap_receipts.py` | new tests / modified tests | Receipts step pass/fail/skip/FAIL-OPEN/anti-foreign-block tests | D-6: test plan |
| 10 | `ELUVIAN_PATH.md` (governance repo) | Stage 5 wrap completion lock section (~:117-123) | Add receipt-check step description to the wrap gates list | D-5: doctrine cross-reference (shop-infra follow-up) |
| 11 | `bellows.py` | plan-close bookkeeping (near :1201-1208 or equivalent close path) | Receipt retirement: move to `receipts/archived/` on plan close | D-4: receipt lifecycle |
| 12 | `governance/knowledge/research/wrap-lock-portability-census-2026-08-24.md` | census table | Add `RECEIPTS = BELLOWS / "receipts"` as new machine-pinned row (ROOT-derived) | D-5: portability fence |

### G2 plumbing gap re-derived

**Confirmed:** wrap_stop_hook.py:80-91 extracts `session_id` from stdin JSON. wrap_stop_hook.py:70-77 validates shape `[A-Za-z0-9-]+`. wrap_stop_hook.py:186-188 uses `session_id` for sentinel scoping. **But** wrap_stop_hook.py:207-210 invokes `wrap_check.py` with NO arguments — the session_id is available in the caller but never passed to the subprocess. wrap_check.py has **0** `sys.argv` reads and **0** `import os` statements (positive control: wrap_stop_hook.py has `import os` at :27 and 3 `os.environ` reads). The plumbing gap is CONFIRMED: the id exists at the call site but the truth source never reads it. Gap table rows 4, 5, 6, 7 close it.
