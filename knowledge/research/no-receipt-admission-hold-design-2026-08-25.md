# no_receipt admission hold — design (R-F3 diagnostic)

**Date:** 2026-08-25 | **Ruling:** R-F3 (governance/knowledge/research/eluvian-follow-up-rulings-2026-08-25.md) | **Plan:** 526

This document settles the four questions R-F3 deferred to the diagnostic: the matching predicate, grandfathering, arm placement, and the [2r] residual. Every claim cites file:line in current code (bellows main post-525, daemon PID 80340). Pins re-derived below supersede the Planner's.

---

## N-pin re-derivation

All pins measured 2026-08-25 against the worktree (bellows-wt/526, tracking main post-525). These supersede the Planner's pins.

| id | pin | re-derived value | probe |
|---|---|---|---|
| N1 | no_clearance precedent sites | bellows.py:2301 and :2337 — TWO hold-writing sites (`"hold_reason": "no_clearance"`), ZERO in depositor.py | `/usr/bin/grep -n -F "no_clearance" bellows.py depositor.py` → depositor.py zero hits. **CONFIRMED.** |
| N2 | depositor receipt-awareness | **ZERO** — `/usr/bin/grep -c -iF "receipt" depositor.py` → 0 (exit code 1, zero-match grep exits 1 on this machine). Positive control: same grep on hooks/eluvian/wrap_check.py → 40. | **CONFIRMED.** |
| N3 | receipt fields | slug, content_hash (full SHA256), session_id, armed_at, watcher, attestation_boundary — all six fields present in every inspected receipt. Measured from `receipts/archived/receipt-executable-root-docs-shipped-state-c1f03a88-...-abd1fba1a7c6.json` and the active receipt for this diagnostic. | **CONFIRMED.** |
| N4 | the ritual's byte-identity | Receipt is taken against DRAFT bytes BEFORE the ready- rename. The rename (`os.rename`) moves the inode, never edits content. `deposit_receipt.py:73-74`: `plan_bytes = Path(plan_path).read_bytes()` → `content_hash = hashlib.sha256(plan_bytes).hexdigest()`. The depositor hashes the same bytes at clear-time: `depositor.py:537-538`: `plan_bytes = Path(path).read_bytes()` → `content_hash = hashlib.sha256(plan_bytes).hexdigest()`. The clearance system in `is_claimable` (bellows.py:2265-2267) uses the identical `hashlib.sha256(raw_bytes).hexdigest()` call. All three hash sites share SHA256-of-raw-bytes. Receipt hash == depositor hash == claim-time hash WHEN the ritual order (receipt → ready-rename → depositor evaluate) is followed. | **CONFIRMED.** |
| N5 | active-vs-archived semantics | Active `receipts/`: 3 files (2 from session d79bad0b, 1 from session c1f03a88 — the receipt for THIS diagnostic). Archived `receipts/archived/`: 7 files — retired at plan close by `_retire_receipts` (bellows.py:411-453). The retirement moves receipts to archived/ by slug+JSON-slug equality check (bellows.py:446-448). **The Planner's "517/518 pre-restart residue (2 active, stale)" are NOT present** — the 2 d79bad0b receipts are for the E4 arc (diagnostic + executable), not 517/518. The 517/518 stale receipts were retired or removed before this session. | **SUPERSEDED.** The stale-residue pin is obsolete; measured active population is 3, none stale. |
| N6 | the release path | `tools/clear_plan.py:62-76` (`clear_plan()`): validates hold-prefix + sidecar existence → renames hold- → ready- → removes sidecar JSON. The daemon's depositor re-evaluates the ready- file within 30 seconds. `tools/clear_plan.py:79-133` (`release_class_hold()`): validates → runs cycle_check (BAR_MET required) → runs plan_lint (non-benign FAILs block) → reads class from manifest → writes clearance (`cleared_by='clear_tool'`) → renames hold- → bare name → removes sidecar. **Two distinct release arms**: `clear_plan` re-enters depositor evaluation; `release_class_hold` bypasses the depositor and writes clearance directly. | **CONFIRMED.** |
| N7 | the [2r] wrap check | wrap_check.py:209-210 `_check_receipts(session_id, fails)`. RECEIPTS constant at :46. **Blocking arm** (wrap_check.py:296-343): own-session receipts vs clearances/hold-sidecars — matchless receipts fail the wrap. 10-minute grace window for pending evaluation (:319-328). **Warning arm** (wrap_check.py:348-361): 24h lookback, any-session, non-blocking — cleared deposits without any receipt (active or archived) emit a warning. | **CONFIRMED.** |
| N8 | hold sidecar shape | Depositor path (depositor.py:572): `{"hold_reason": reason, "held_at": datetime.now().isoformat()}` plus optional detail fields merged from the `details` dict. Class holds add `class_assigned` (depositor.py:171,182). Bellows.py scan path (bellows.py:2301,2337): `{"hold_reason": "no_clearance", "held_at": datetime.now().isoformat()}` — no class_assigned. The `_hold` function (depositor.py:554-578) is generic: a new reason is a string constant, not a schema change. One sidecar per deposit: the filename is deterministic (`hold-<slug>.hold.json`), and a second hold overwrites the same file. | **CONFIRMED.** |

---

## D-1 — The real admission map

### Ordered pipeline

A deposit traverses these stages from file-appearance to claim. The left column is the code site; the right is the gate or action.

| # | site | stage | gate / action |
|---|---|---|---|
| 1 | bellows.py:2390-2403 | **Filesystem event** | `on_created` / `on_modified` / `on_moved` fires |
| 2 | bellows.py:2371-2388 | **_invalidate_seen_on_redeposit** | If slug is in `_seen` but no active plan exists in lifecycle.db, discard slug from `_seen` so a re-deposit can re-dispatch |
| 3 | bellows.py:2309-2313 | **_handle: watched check** | `path_parent` must be in `config["watched_projects"]` |
| 4 | bellows.py:2315 | **_handle: is_runnable_plan** | Regex `^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$` — the dispatch-whitelist fork |
| 4a | bellows.py:2316-2321 | ↳ NOT runnable, `ready-*.md` | Thread to `depositor.evaluate(path)` → **enters depositor pipeline** (stage 5) |
| 4b | bellows.py:2329-2342 | ↳ IS runnable, NOT claimable | `is_claimable` fails → **HOLD with `no_clearance`** (N1 site 2) |
| 4c | bellows.py:2344-2345 | ↳ IS runnable, in `_seen` | Skip (already dispatched) |
| 4d | bellows.py:2367-2369 | ↳ IS runnable, claimable | Add to `_seen`, dispatch to orchestrator |
| 5 | depositor.py:97-110 | **_evaluate_locked: preflight** | Shutdown check, file-exists check, ready- prefix check, dedup window |
| 6 | depositor.py:130 | **_do_evaluate: parse** | Extract writes, reads, declared_class from plan text |
| 7 | depositor.py:132-136 | **empty_writes** | No writes → HOLD |
| 8 | depositor.py:138-143 | **sibling writes** | Parse sibling ready- files' writes; unparseable → HOLD |
| 9 | depositor.py:145-150 | **in-flight writes** | Resolve currently dispatched plans' writes; unresolvable → HOLD |
| 10 | depositor.py:153-157 | **collision check** | writes∩writes or reads∩writes with siblings/in-flight → HOLD |
| 11 | depositor.py:159-162 | **rerun validation** | cycle_check + plan_lint gates; failure → HOLD |
| **12** | **(NEW)** | **receipt check** | **`no_receipt` HOLD — the R-F3 arm. Belongs HERE: after structural validation, before class assignment.** |
| 13 | depositor.py:164-167 | **class assignment** | `_assign_class(writes, project_root)` |
| 14 | depositor.py:169-174 | **class mismatch** | declared ≠ assigned → HOLD |
| 15 | depositor.py:176-178 | **disk preflight** | Low disk → HOLD |
| 16 | depositor.py:180-195 | **class-gated clear** | shop-infra → HOLD; else re-check collisions → `_clear` |
| 17 | depositor.py:528-552 | **_clear** | Hash bytes → `write_clearance` to lifecycle.db → rename ready- → bare name → remove hold sidecar |
| 18 | bellows.py:2315→2329→2344→2367 | **Re-enter _handle** | Bare-name file triggers _handle again; is_claimable passes → claim |

### Why stage 12

The receipt check belongs between rerun validation (stage 11) and class assignment (stage 13) because:

1. **After structural validation:** A structurally invalid plan (empty writes, collision, lint failure) should fail on its structural defect, not on a missing receipt. Receipt presence is an authorization concern, not a structural one.
2. **Before class assignment:** Class assignment determines the release path (auto-clear vs class:shop-infra hold). A receipt-less plan should never reach class assignment because the clear path after class assignment writes a clearance record — allowing a receipt-less deposit to get a clearance record defeats the purpose.
3. **Before _clear:** The critical invariant: `_clear` writes a clearance and renames to the claimable name. A receipt-less deposit must NEVER reach `_clear`.

### Double-hold behavior

**One hold reason per deposit; mutually exclusive paths.** The code does first-reason-wins today, and the `no_receipt` arm preserves this:

- `no_receipt` fires in depositor.py on `ready-*.md` files (stage 12). If it holds, the file becomes `hold-*.md` and never reaches the bare-name state.
- `no_clearance` fires in bellows.py on bare-name files (stage 4b). It only fires on files that somehow bypassed the depositor entirely (direct bare-name deposit, manual drop).

A single deposit follows ONE path (ready- → depositor → clear → bare-name → claim) or holds at one gate. The sidecar filename is deterministic (`hold-<slug>.hold.json`), so a re-hold on the same slug overwrites the sidecar — never two sidecars.

**The ordering question:** Can one deposit show both `no_receipt` AND `no_clearance`? No. `no_receipt` fires on the `ready-*` file. If held, the file is renamed to `hold-*`. Even if the operator releases via `clear_plan` (hold → ready → re-evaluate), the depositor re-evaluates and either holds again (same or different reason) or clears. The bare-name state only exists AFTER `_clear` writes a clearance record, so `no_clearance` has no entry point once the depositor is in the loop.

---

## D-2 — The matching predicate

### Predicate: slug + content_hash (both required)

The admission check reads the `ready-*` file's raw bytes, computes `hashlib.sha256(plan_bytes).hexdigest()`, derives the slug (strip `ready-` prefix and `.md` suffix), and looks for an ACTIVE receipt (in `receipts/`, not `receipts/archived/`) whose `slug` field matches AND whose `content_hash` field matches.

**Why slug+hash, not hash-only:**
- Hash-only tolerates renames (same bytes, different slug). This is wrong: a receipt attests SPECIFIC BYTES for a SPECIFIC ARTIFACT. Two different plans could have identical bytes (copy-paste of a template before edits). Hash-only would let one receipt cover both.
- Slug+hash ensures the receipt names the artifact it attests. The cost: a renamed artifact needs a new receipt. This is correct — the ritual order is receipt → deposit, so the slug is known before the receipt is written.
- The deposit_receipt.py tool already keys on slug+hash for duplicate detection (deposit_receipt.py:92): `if data.get("slug") == slug and data.get("content_hash") == content_hash`.

### Drift arms

**(a) Post-receipt edit (hash mismatch).** The receipt attests THE BYTES at receipt-write time. If the plan is edited after receipting but before the depositor evaluates, the content_hash won't match → HOLD with `no_receipt`. This is correct: the edited bytes are unattested. The operator must write a new receipt for the edited bytes.

**(b) Receipt present but ARCHIVED.** An archived receipt means the original plan was closed (`_retire_receipts`, bellows.py:411-453, moves receipts to `receipts/archived/` at plan close). A re-deposit of the same slug arrives as a fresh deposit. The admission check looks ONLY at active receipts (`receipts/`, not `receipts/archived/`). An archived-only receipt → HOLD with `no_receipt`. This is correct: a re-deposit is a new lifecycle act that requires its own attestation. The retired receipt is evidence of the prior lifecycle, not authorization for a new one.

**(c) Multiple active receipts for one slug.** `deposit_receipt.py:84-95` prevents exact duplicates (same slug AND same hash). But a re-receipted plan (edited bytes → new hash) creates a second active receipt with the same slug but different hash. The admission check finds the receipt matching the current bytes (slug + current hash). Any-match semantics: if ANY active receipt for the slug matches the current hash, the deposit passes. No newest-wins needed — the hash match is sufficient. Orphaned receipts (old hash, no matching deposit) are harmless and retire at plan close.

**(d) Hold-release-re-entry loop.** After a `no_receipt` hold:
1. Operator writes a receipt: `python3 tools/deposit_receipt.py <hold-path-or-ready-path> <session_id>`
2. Operator runs `clear_plan`: `python3 tools/clear_plan.py <hold-path>` (clear_plan.py:62-76)
3. `clear_plan` renames `hold-<slug>.md` → `ready-<slug>.md` and removes the hold sidecar
4. The daemon's depositor re-evaluates the `ready-*` file within 30 seconds (bellows.py:2316-2321 threads to `dep.evaluate`)
5. The receipt check now finds the matching active receipt → passes
6. Depositor proceeds through remaining gates → `_clear`

The re-entry path uses `clear_plan`, NOT `release_class_hold`. `release_class_hold` (clear_plan.py:79-133) bypasses the depositor entirely (writes clearance directly and renames to bare name), which would skip the receipt check. `clear_plan` re-enters the depositor pipeline, re-running ALL checks including the new receipt check.

---

## D-3 — Grandfathering

### Measured population: ZERO pending deposits

Probed all 11 watched project `knowledge/decisions/` directories (absolute paths per the split-path law):
- `/Users/marklehn/Developer/GitHub/freight-kb/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/BrewBuddy/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/study/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/SimpleScreen/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/ai-career-digest/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/forge/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/anvil/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/governance/knowledge/decisions/`
- `/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/`

Grep for `^(executable|diagnostic|qa|ready-|hold-)` across all 11 directories: **zero matches.** The queue is empty. No pending deposits would hold under the new arm.

### Grandfather cases

**(i) Legacy plan re-deposited from Done/ for a corrective re-run.** A pre-E3 artifact has no receipt (the receipt system didn't exist). Under the new arm, re-depositing it as `ready-<slug>.md` would trigger `no_receipt` hold. The operator must write a receipt before releasing.

**Recommendation: HOLD-AND-RELEASE (the deliberate act).** This is the E2 precedent — grandfather+gated-clear. The cost is exactly two commands: `deposit_receipt.py <path> <session_id>` + `clear_plan <hold-path>`. The benefit: every deposit through the daemon is explicitly attested, no exemption windows. An exemption-by-rule (e.g., "exempt plans whose bytes predate E3") is unenforceable — there is no timestamp in the plan bytes that proves pre-E3 authorship, and any exemption predicate based on file metadata (mtime, git history) is spoofable or brittle.

**(ii) The 517/518 stale active receipts.** **Pin superseded:** the measured active population is 3 receipts, none related to 517/518 (see N5 re-derivation). The two d79bad0b-session receipts are for the E4 arc (diagnostic-eluvian-e4-design and executable-eluvian-e4-conditioning), not stale. No grandfather concern from stale receipts.

For future same-slug deposits: if a receipt is active and a new deposit arrives with the same slug but different bytes (edited plan), the hash mismatch means the existing receipt doesn't satisfy the check → hold. If same bytes (exact re-deposit), the existing receipt DOES satisfy → passes. Both behaviors are correct.

**(iii) Hand-authored emergency deposit (daemon-down, manual lane).** If the daemon is down, the operator drops a file directly. When the daemon restarts, `reevaluate_on_startup` (depositor.py:82-91) evaluates all `ready-*` files. The receipt check fires at that point.

**Recommendation: same posture — HOLD-AND-RELEASE.** The manual lane is rare and deliberate. Requiring a receipt for manual deposits is the same friction as requiring a clearance (which already exists). The daemon-down scenario doesn't exempt the operator from attesting the deposit — if anything, an unattended deposit in a daemon-down situation warrants MORE scrutiny, not less.

### Posture summary

**HOLD-AND-RELEASE for all cases.** No exemptions. The E2 precedent (grandfather+gated-clear for `no_clearance`) is the direct prior. The abuse surface of any exemption exceeds the two-command cost of the release ritual.

---

## D-4 — Arm placement and interaction

### Placement: depositor.py `_do_evaluate`, stage 12

The `no_receipt` check lives in **depositor.py**, between rerun validation (depositor.py:159) and class assignment (depositor.py:164). This is the depositor pipeline, NOT bellows.py's scan path.

**Why NOT bellows.py (beside the N1 sites):**
- The N1 sites fire on bare-name files that bypassed the depositor. The `no_receipt` check is conceptually part of the depositor's evaluation — it validates that the deposit was ritually prepared (receipt written before staging).
- A scan-side arm (bellows.py) fires once per `_seen` cycle. If it fires, the slug enters `_seen` and the file is renamed to `hold-*`. On release, `clear_plan` renames to `ready-*`, which re-enters the depositor — but the bellows.py scan side would need `_seen` invalidation for the new ready- file, adding complexity. The depositor path avoids this: ready- files always enter depositor.evaluate, and the dedup window (depositor.py:107-113, 5-second) handles rapid re-evaluations.

**Why NOT at `is_claimable` (claim-time):**
- `is_claimable` (bellows.py:2259-2269) fires on bare-name files AFTER the depositor has already cleared the deposit and written a clearance record. Checking receipt presence at claim-time is too late — the clearance already exists, and the deposit has already been granted authority. A claim-time check would need to revoke authority already granted, which is incoherent with the clearance model.

**Why NOT inside depositor.py `_clear`:**
- `_clear` (depositor.py:528-552) is the action, not the gate. Putting the check inside _clear means all preceding gates (collision, class, disk) have already passed — the system has decided the deposit SHOULD clear, then discovers it can't. The hold at stage 12 is cleaner: the deposit is held before the system commits to clearing it.

### Making depositor receipt-aware

This addresses N2 (depositor receipt-awareness = ZERO today). The executable adds receipt-lookup logic to depositor.py:
- Import: `os`, `json` (already imported), plus the receipts directory path (derived from `self._bellows_root`).
- Logic: derive slug from the `ready-*` filename, hash the bytes (already done at _clear time; the same `Path(path).read_bytes()` + `hashlib.sha256()` pattern), iterate `receipts/` directory for `.json` files, load each, check `slug == derived_slug AND content_hash == computed_hash`.
- If no match → `self._hold(path, "no_receipt")`.

### Release path

The `no_receipt` hold is released by `clear_plan` (tools/clear_plan.py:62-76), NOT `release_class_hold`. `clear_plan` renames `hold-` → `ready-`, and the depositor re-evaluates. The re-evaluation re-runs the receipt check at stage 12. If the operator has written a receipt in the interim, the check passes.

`release_class_hold` (tools/clear_plan.py:79-133) must NOT be used for `no_receipt` holds because it bypasses the depositor entirely: it writes clearance directly and renames to bare name, skipping stage 12. This is safe because `release_class_hold` is documented as "the deliberate human release act for class-held plans (RULINGS forks 2+4)" — it is scoped to class holds by design.

**Whether `release_class_hold`'s re-checks should extend:** No. `release_class_hold` already runs cycle_check and plan_lint (clear_plan.py:88-108). Adding a receipt check there would create a second receipt-checking code path that must stay in sync with the depositor's check. The simpler design: `release_class_hold` is for class holds only; `no_receipt` holds use `clear_plan` exclusively. The release tool routing is by hold reason, which the operator reads from the hold sidecar JSON.

### The [2r] residual

**Recommendation: KEEP as defense-in-depth. No code change.**

With admission enforcing, the wrap check's blocking arm (wrap_check.py:296-343) becomes redundant-by-construction for daemon-lane deposits: any deposit that reaches `_clear` has a matching active receipt. The blocking arm's `matchless_count` check would find zero matchless receipts for daemon-lane deposits.

But the blocking arm serves three residual purposes:

1. **Manual-lane catch.** If the daemon is down and the operator deposits directly, no depositor evaluation runs. When the operator wraps, the blocking arm catches uncleared deposits (receipts with no matching clearance or hold sidecar). This is the daemon-down safety net.

2. **Future-proofing.** A code bug that bypasses the depositor check would be caught at wrap time. Defense-in-depth costs one DB query per wrap.

3. **Stale-receipt detection.** The blocking arm also catches receipts whose deposits were abandoned (receipt written but plan never staged). The operator must remove the receipt file to disarm — the sanctioned path (wrap_check.py:337-338).

The warning arm (wrap_check.py:348-361, 24h lookback) is unaffected: it catches cleared deposits without ANY receipt (active or archived), which detects non-ritual deposits regardless of the admission arm.

**Retire-to-warning-only is NOT recommended.** The blocking arm's cost is near-zero (one DB query + file scan), and the manual-lane case is real (the daemon has been down during this session's lifetime — measured).

---

## D-5 — Test surface

The executable's tests (new test file or additions to existing test files):

1. **receipt-present passes admission** — ready- file with matching active receipt → depositor clears, no hold
2. **receipt-absent holds with `no_receipt` sidecar** — ready- file with no matching receipt → hold, sidecar contains `{"hold_reason": "no_receipt", "held_at": ...}`
3. **hash-mismatch holds** — active receipt exists for slug but content_hash differs → hold with `no_receipt`
4. **archived-receipt case** — receipt exists only in `receipts/archived/`, not `receipts/` → hold with `no_receipt`
5. **grandfather posture** — legacy artifact with no receipt → hold (same as case 2; no exemption path)
6. **release-re-entry re-evaluates** — after `no_receipt` hold, write receipt, `clear_plan` rename → depositor re-evaluates → receipt found → clears
7. **no_clearance + no_receipt ordering** — verify no_receipt fires on ready- files (depositor path), no_clearance fires on bare-name files (bellows.py path), never both on the same deposit
8. **`_seen` non-re-fire** — after depositor holds a ready- file with `no_receipt`, the slug is NOT added to `_seen`; the file is renamed to `hold-*` which doesn't match `is_runnable_plan`, so the scan path doesn't re-fire
9. **[2r] posture unchanged** — wrap check blocking arm still catches matchless receipts; no behavioral change
10. **multiple active receipts** — two receipts for same slug with different hashes; deposit matches one → passes
11. **slug mismatch, hash match** — receipt with matching hash but different slug → hold with `no_receipt` (slug+hash predicate)

**Regression floor:** `python3 -m pytest --collect-only -q` → **1412 tests** (measured 2026-08-25).

---

## D-6 — The executable's shape

**Small: single plan.** The change set is:

1. **depositor.py** — add receipt-lookup logic in `_do_evaluate` (between rerun validation and class assignment). One new method (`_check_receipt`) plus one call site in `_do_evaluate`. The depositor gains receipt-awareness (N2 goes from 0 to >0).
2. **tests/** — new test cases (11 cases per D-5, likely in a new test file or appended to `tests/test_wrap_receipts.py` depending on organizational preference).

The [2r] posture is KEEP-AS-IS (no code change). No split needed.

---

## D-7 — Open questions

**D-7 is truthfully empty.** No genuinely new ruling is needed beyond R-F3's letter:

- **The slug+hash predicate** (D-2): settled here, not contested. Hash-only is demonstrably weaker (cross-slug abuse). Slug+hash is the natural match to the receipt schema and the deposit_receipt.py duplicate check.
- **The hold-and-release grandfathering posture** (D-3): follows the E2 precedent exactly. No exemption proposed; the two-command cost is minimal and the abuse surface of any exemption exceeds it.
- **The release tool routing** (D-4): `clear_plan` for `no_receipt`, `release_class_hold` for class holds. No ambiguity — the tools are already scoped by hold type.

No fork lands in D-7 because all four of R-F3's questions are settleable from the code and the E2 precedent without new doctrine.

---

## Rule 27 gap table

| # | file | change | nature |
|---|---|---|---|
| G1 | `depositor.py` | Add `_check_receipt(self, path)` method: derive slug, hash bytes, scan `receipts/` for matching active receipt (slug+hash). Return True if found, False if not. | new method |
| G2 | `depositor.py` | Call `_check_receipt` in `_do_evaluate` between rerun validation (line ~162) and class assignment (line ~164). If False → `self._hold(path, "no_receipt")` + return. | new call site in existing method |
| G3 | `tests/` | 11 test cases per D-5. Cover: present/absent/mismatch/archived/re-entry/ordering/multi-receipt/slug-mismatch. | new tests |

**Total change sites: 2 production (both in depositor.py) + 1 test file.** The bellows.py scan path, clear_plan.py, wrap_check.py, and deposit_receipt.py are UNCHANGED.
