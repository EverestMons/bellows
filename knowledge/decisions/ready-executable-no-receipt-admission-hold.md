# bellows — executable: the `no_receipt` admission hold (R-F3) — receipts become structural at the depositor's stage 12

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

**Depends on:** `knowledge/research/no-receipt-admission-hold-design-2026-08-25.md` (diagnostic-526's deposit — BINDING: the D-1 pipeline map, D-2 predicate + four drift arms, D-3 hold-and-release grandfathering, D-4 placement + release routing, D-5 test list, and the G1-G3 gap table are this plan's spec; D-7 was truthfully empty, so nothing here is discretionary). Ruled under R-F3 (`governance/knowledge/research/eluvian-follow-up-rulings-2026-08-25.md`), CEO directive this session: "run the executable with the recommended options."

## Why this exists

A receipt-less deposit sails through admission today (depositor receipt-awareness measured ZERO); the wrap-time `[2r]` check is detection-not-enforcement and only for sessions that wrap. The E2 precedent completes: the filename carries no authority, the clearance record does — and after this plan, the clearance is unreachable without an attested receipt. Three production files (S4-4): depositor.py carries the check; two surgical panel-mandated hunks in the receipt and release tools close the deadlock and the routing bypass the panel measured.

## What this plan does NOT do

- **It does not restart the daemon.** The arm is INERT until the next deliberate restart. ⚠️ No restart mid-plan — and note the pleasant asymmetry: THIS plan's own deposit is evaluated by the PRE-arm daemon, so it cannot block itself; it carries a receipt anyway (the ritual).
- **It does not touch bellows.py or wrap_check.py** (per the gap table's fence). ⚠️ **The fence is AMENDED by panel findings for two surgical edits, each closing a defect that would defeat R-F3's enforcement:** `tools/deposit_receipt.py` gains `hold-` prefix stripping in its slug derivation (S2-1 — without it the documented release ritual DEADLOCKS: a receipt written against the hold file carries slug `hold-<slug>`, never matches, and the release loops forever; rehearsed and measured); `tools/clear_plan.py`'s `release_class_hold` gains a POSITIVE routing guard (S2-4 found the unenforced routing; S3-1's executed demo overturned the first negative-list form — allow only class-provenance sidecars, refuse everything else; the full rule is in A5). Neither amendment duplicates the receipt CHECK (D-4's rejection of a second check path stands) — one fixes slug derivation, one enforces routing.
- **It does not add exemptions.** D-3: hold-and-release everywhere; exemption predicates were shown unenforceable.

## Numbers discipline

⚠️ **Measured 2026-08-25 by the Planner against bellows main post-526 (daemon PID 80340); line numbers are hints — re-locate by ANCHOR, assert count==1 via `/usr/bin/grep` before editing.**

| id | pin | value | anchor |
|---|---|---|---|
| V1 | the stage-12 seam | depositor.py:159-164 — between the rerun-validation hold-return and `assigned_class = self._assign_class(writes, project_root)` | the ONLY `_assign_class(` call site in `_do_evaluate`; insert immediately BEFORE it |
| V2 | the hold primitive | `self._hold(path, reason, details)` — depositor.py:554; sidecar `{"hold_reason", "held_at"}` + merged details; deterministic filename, one sidecar per slug | the neighboring arms (`unassignable_class` :166, `empty_writes`) are the call-shape template |
| V3 | the hash pattern | depositor.py:537-538 (`_clear`'s own `Path(path).read_bytes()` → `hashlib.sha256(...).hexdigest()`) — G1 REUSES this exact pattern; all three lane hash sites are SHA256-of-raw-bytes (526 N4) | copy the pattern, do not invent a variant |
| V4 | the receipts dir | `self._bellows_root / "receipts"` — `self._bellows_root` set at depositor.py:69 via `resolve_bellows_root()`; ACTIVE receipts only (never `receipts/archived/`) | `/usr/bin/grep -n -F "_bellows_root" depositor.py` |
| V5 | the predicate template | deposit_receipt.py:92 — `data.get("slug") == slug and data.get("content_hash") == content_hash` | the match is slug AND hash, both required (526 D-2); slug derived by stripping `ready-` prefix and `.md` suffix |
| V6 | suite floor | **1412 collected** | `python3 -m pytest tests/ --collect-only -q` from repo root; re-derive |
| V7 | the test harness | `tests/test_depositor.py` — the existing depositor fixture home; new tests live here (or a sibling `test_depositor_receipts.py` — ⚠️ if a NEW file, it must be added to this plan's Deposits by being the named file below; the pinned deposit path is `tests/test_depositor_receipts.py` — use exactly it) | read its fixture shapes before writing |
| V8 | malformed-receipt posture | a `.json` in receipts/ that fails to parse must be SKIPPED (treated as non-matching), never crash the depositor — the depositor runs inside the daemon | the S1-3-class lesson from 524's panel: unguarded parse in a daemon loop |

## MUST-PRESERVE

- ⚠️ **NO daemon restart; no writes outside the worktree; lifecycle.db only via the test suite's temp DBs.**
- ⚠️ **THE GREP SHIM IS BROKEN (every form errors `unknown option '-G'`): use `/usr/bin/grep` for ALL probes; a zero-match `/usr/bin/grep` exits 1 — never &&-chain zero-count probes; an errored probe is the shim, not an absence.**
- ⚠️ **The AMENDED fence (S4-1 — the original four-module fence was amended by panel findings S2-1/S2-4/S3-1, declared in the header):** bellows.py and hooks/eluvian/wrap_check.py — zero edits. tools/deposit_receipt.py and tools/clear_plan.py — ONLY the two A5 hunks (the write_receipt slug-derivation hunk; the release_class_hold positive-routing guard). `git diff --stat` at commit time must show exactly depositor.py + the two tool files + the test file (+ A3-updated existing test modules, each named).
- ⚠️ **The receipt scan is fail-safe per V8:** unreadable/malformed receipt JSONs are skipped with no raise; an unreadable receipts DIRECTORY (missing, permissions) counts as no-match → hold (fail-closed: absence of provable attestation holds; state this in a code comment).
- ⚠️ **Anchor-based editing; blast-radius sweep mandatory in DEV (A3).**
- ⚠️ **Worktree dispatch; deposit paths project-relative in your worktree.**

## STEP 1 — DEV: the check, the call site, the tests

**Role:** DEV.

**A1 — `_check_receipt` (G1).** New method on the depositor beside its sibling helpers: derive the slug from the `ready-*` filename (strip `ready-` prefix, `.md` suffix); read the file's raw bytes and hash via the V3 pattern; iterate `self._bellows_root / "receipts"` for `*.json` (ACTIVE only — never descend into `archived/`); for each, load JSON inside a try/except (V8 — parse failure → skip, continue); match per V5 (slug AND content_hash, both equal). Return True on first match; False when the scan completes matchless OR the directory is unreadable (fail-closed, commented).

**A2 — the stage-12 call (G2).** At the V1 seam, immediately before `_assign_class`:
```
if not self._check_receipt(path):
    self._hold(path, "no_receipt", {})
    return
```
Shape-matched to the neighboring arms (V2). Nothing else in `_do_evaluate` moves.

**A2b — hold-reason preservation in `_reevaluate_hold` (panel S1-7, a DECLARED scope extension beyond 526's gap table — same file, adjacent defect, and D-4's release routing DEPENDS on the sidecar reason):** the daemon-restart re-evaluation path (`_reevaluate_hold`, depositor.py:201-227 region) overwrites a surviving hold sidecar's reason via `_update_hold_json` (measured: a `no_receipt` sidecar would become `held_pending_ceo_release`, erasing the reason the operator's release-tool routing reads; the same mechanism already rewrites `class:*` sidecars). Fix, minimal — ⚠️ FIRST-WINS carry-forward (S2-2: the naive differs-only rule loses the field on the SECOND restart, measured): when `_update_hold_json` rewrites a sidecar, (i) if the existing JSON already carries `original_reason`, PRESERVE it unchanged; (ii) else if the existing `hold_reason` differs from the new one, set `original_reason` to the existing `hold_reason`; (iii) a missing or malformed existing sidecar → write fresh with no `original_reason`, never raise; (iv) ⚠️ the read runs UNLOCKED while clear_plan may remove the sidecar concurrently (S2-6) — a vanished-between-read-and-write sidecar must not raise (write-fresh posture). (v) the details-merge filter must exclude `original_reason` from being clobbered by merged detail dicts (S3-6 — latent today, one-line guard now). Test 15 (ADDITION): TWO consecutive `_reevaluate_hold` passes preserve `original_reason == "no_receipt"` — in BOTH restart-2 shapes (S4-5): same-reason rewrite (the DROP bug) AND differing-reason rewrite, e.g. a collision surfacing at restart 2 (the OVERWRITE bug — clause (i)'s precedence is what this arm pins). Test 15b (ADDITION, S3-5): the clause-(iv) race — sidecar vanished between read and write → no raise, fresh write.

**A5 — the fence amendments (S2-1, S2-4; declared above):**
- `tools/deposit_receipt.py`: the slug derivation strips `hold-` in addition to `ready-` (the bytes are identical across the rename, so the hash already matches; only the slug broke). Test 16 (ADDITION): a receipt written against a `hold-*.md` path derives the bare slug and satisfies the admission check after the clear_plan rename — exercised with the REAL `write_receipt`, not a hand-built JSON (the S2-1 rehearsal's exact loop, now passing). ⚠️ The receipt TOOL has its OWN module-level `_RECEIPTS_DIR` derived from its `__file__` (deposit_receipt.py:21-23), untouched by the `resolve_bellows_root` repointing (S3-2 measured: an unpatched test 16 writes into the LIVE receipts/ and can fail a real wrap after the grace window) — monkeypatch `deposit_receipt._RECEIPTS_DIR` per the existing precedent in test_deposit_receipt.py; the isolation mandate covers BOTH the depositor's scan dir and the tool's write dir.
- `tools/clear_plan.py` `release_class_hold`: before any clearance write, read the sidecar and apply POSITIVE routing (S3-1 — the panel's executed demo showed a negative-list guard under-blocks: a receipt-less plan held at any PRE-stage-12 reason, e.g. `collision:*`, released straight to a clearance, bypassing the receipt check; a curated negative list is invisible-when-incomplete): ALLOW only when `hold_reason` starts with `class:` OR (`hold_reason == "held_pending_ceo_release"` AND (`original_reason` absent OR starts with `class:`)) — the absent arm keeps the pinned legacy behavior (`test_release_works_with_restart_rewritten_sidecar`, pre-A2b sidecars carry no original_reason). Everything else refuses with `release_class_hold is for class holds only; this hold releases via clear_plan (the depositor re-evaluates all gates)` and exit 1. Test 17 (ADDITION): refusal fires on `no_receipt` direct, `no_receipt`-via-original_reason, AND a pre-stage-12 reason (`collision:*` — the S3-1 demo case); test 18 (ADDITION): a genuine `class:*` hold AND the legacy no-original_reason rewritten sidecar both still release.

**A3 — blast-radius sweep, with the ACCURATE expectation (S1-4).** `/usr/bin/grep -rn -F "_do_evaluate" tests/` and `/usr/bin/grep -rln -F ".evaluate(" tests/` — force-classify every hit into three bins: **(a)** tests that hold BEFORE stage 12 (empty-writes, collision, lint fixtures — stages 7-11) need NO receipt fixture and must keep passing unchanged; **(b)** tests whose fixtures REACH stage 12 need a matching-receipt fixture helper (writes the receipt JSON into the test's receipts dir); **(c)** ⚠️ the vacuous-pass trap (measured by the panel): `test_two_concurrent_evals_one_clear` asserts `cleared <= 1`, which passes VACUOUSLY at 0 when both evaluations hold on `no_receipt` — silently deleting the one-clear invariant from coverage; it MUST gain receipt fixtures AND its assertion should tighten to `cleared == 1` so the invariant is actually exercised. ⚠️ `test_hold_creates_holdfile_and_json` is NOT a bin-(a) example (S2-3 measured): its fixture's writes make it shop-infra, holding AFTER stage 12 — fixture-less post-change it holds `no_receipt` and its bare `"hold_reason" in data` assertion passes vacuously, silently deleting class-hold coverage; it needs a receipt fixture AND its assertion pinned to the expected class reason. The naive "passing without fixtures = check not firing" inference is wrong in both directions; every touched assertion must pin the EXPECTED hold_reason, never mere presence. Also sweep `reevaluate_on_startup` callers (S2-5) AND bare `Depositor(` constructions (S3-3 — the measured hole: test_admission_flip.py:46 builds a Depositor and drives `_clear` directly, invisible to both other probes; classify it too — stage-12-safe today since `_clear` sits after the check, but the classification must be recorded, not assumed). **Isolation mandate (S1-5): EVERY depositor test run must point the receipts scan at a tmp dir — fixture-less bin-(a) tests included — because a stage-12-reaching test otherwise scans the LIVE `receipts/` (resolve_bellows_root finds the canonical root even from worktrees). Use one autouse fixture in the new file + the touched modules repointing the instance's `_bellows_root` (or patching `resolve_bellows_root`) — state which you did. `_bellows_root` is dual-use (:483 plan_lint path) — verify the existing `depositor.subprocess` mock keeps that arm inert in the affected tests.**

**A4 — tests (G3), in `tests/test_depositor_receipts.py` — ⚠️ D-5's ELEVEN tests VERBATIM (S1-1: the deposit is binding; the first draft dropped three), PLUS the declared additions: 12-14 below, 15/15b in A2b, 16-18 in A5 — NINETEEN tests total (S4-6):**
1. receipt-present passes admission (clears, no hold)
2. receipt-absent → HOLD, sidecar `hold_reason == "no_receipt"`
3. hash-mismatch → HOLD
4. archived-only receipt → HOLD (D-2b)
5. grandfather posture: legacy artifact, no receipt → HOLD (same arm as 2; no exemption path exists)
6. release-re-entry: hold → write receipt → clear_plan rename → re-evaluation clears (D-2d) — ⚠️ the 5s dedup window keys on the READY- PATH which the rename restores (S1-3): use the harness's own precedent `depositor._DEDUP_WINDOW = 0.0` (test_depositor.py:449-452), restoring it in teardown
7. ordering across paths: `no_receipt` fires on ready- files (depositor), `no_clearance` on bare-name files (bellows.py scan) — never both on one deposit
8. `_seen` non-re-fire: a `no_receipt` hold does NOT add the slug to `_seen`; the hold-* name fails `is_runnable_plan`, so the scan path stays quiet
9. [2r] posture unchanged: the wrap check's blocking arm still catches matchless receipts (no behavioral change — assert against wrap_check's existing test patterns)
10. multiple active receipts, one matching → passes (D-2c any-match)
11. slug mismatch with hash match → HOLD (the slug+hash predicate)
12. (ADDITION) malformed receipt JSON → skipped, a matching receipt elsewhere still found; no raise (V8)
13. (ADDITION) missing receipts directory → HOLD **with `hold_reason == "no_receipt"` pinned** (S2-7: the catch-all at depositor.py:124-127 would satisfy a bare "holds, no raise" via an `exception:FileNotFoundError` hold — pin the reason so fail-closed is proven deliberate, not accidental)
14. (ADDITION) one-sidecar invariant: re-hold on the same slug overwrites, never duplicates

Targeted DEV run: the new file + every module the A3 sweep classified as updated. NOT the full suite.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/depositor.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_depositor_receipts.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/depositor.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/`

**Commit:** `git add depositor.py tools/deposit_receipt.py tools/clear_plan.py tests/ && git commit -m "[<id>] depositor: no_receipt admission hold (R-F3) — receipts structural at stage 12; hold-slug fix + positive release routing (panel S2-1/S3-1)"` in YOUR worktree cwd.

## STEP 2 — QA: full suite + evidence, per-plan names

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd**; deposit RAW output as `knowledge/qa/evidence/no-receipt-admission-hold/pytest_full.txt`. Self-contained accounting: total, the new file's own count, derived inherited baseline vs V6's 1412; zero failures.

**Q2 — change-shape check.** `git diff HEAD~1 --stat` shows EXACTLY depositor.py + tools/deposit_receipt.py + tools/clear_plan.py + tests/test_depositor_receipts.py (+ any A3-updated existing test module, each named in the DEV report); `/usr/bin/grep -c -F 'self._hold(path, "no_receipt"' depositor.py` == 1 (the A2 call literal — NOT the bare word, which comments would inflate; pre-change baseline measured 0); the AMENDED fence holds: NO bellows.py or wrap_check.py line in the diff, and the two tool edits are confined to `write_receipt`'s inline slug-derivation hunk (S3-4: there is no separate derivation function — the measured hunk is `@@ -65,6 +65,10 @@`-shaped) and the `release_class_hold` routing guard respectively (name the hunks).

**Q3 — QA report.** `knowledge/qa/evidence/no-receipt-admission-hold/qa-report.md` with Q1-Q2 + the G1-G3 coverage rows + the activation note (arm inert until the next deliberate restart; first live canary = the first post-restart deposit, which the Planner will run receipted and then deliberately receipt-less in a sandbox slug if the CEO wants the negative proven live).

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1-Q3 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/no-receipt-admission-hold/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/no-receipt-admission-hold/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/no-receipt-admission-hold/`

**Commit:** `git add knowledge/qa/evidence/no-receipt-admission-hold/ && git commit -m "[<id>] qa: no_receipt admission hold — full suite + evidence (per-plan path)"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T2 computed — daemon admission-path code (highest blast radius: a defect blocks ALL deposits); full cold panel mandated at the freeze.
**Walk register:** `governance/knowledge/research/walk-register-executable-no-receipt-hold.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** (yields 1 → 0, warm close) — then the **full cold panel: scout 8 (2 HIGH) → discovery 10 (2 HIGH, incl. the EXECUTED release-ritual deadlock) → execution 6 (0 HIGH — the folded spec BUILT: 19 new + 7 updated tests passing in scratch, the deadlock closed end-to-end) → capstone NOT-READY on 4 fold-damage blockers, discharged by 7 folds + a dry sweep walk.** Every seat finding author-verified before folding; per-seat tables in the register.
**Cold panel: CONVENED AND CLOSED** — 31 findings total across four seats; the fence was amended twice under declaration (S2-1 hold-slug, S3-1 positive routing) and the capstone verified the five-way agreement of the amended reality.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 dry; w2 dry; panel folds per register
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry; sweep walk dry
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the lintmirror deposit path.
**Closing:** **panel closed, capstone discharged — FREEZE.** Warm 1 → 0; panel 8 → 10 → 6 → 7(+sweep 0). The deposit travels the lane with the receipt ritual → staged `ready-` → class shop-infra HOLD → release via `clear_plan.py --release-class-hold` under the CEO's "run the executable with the recommended options" directive of 2026-08-25 → claim. ⚠️ Post-close activation: the arm is inert until the NEXT deliberate daemon restart; from that restart on, every deposit requires its receipt BEFORE staging.

## Cycle Manifest
tier: T2
target: depositor.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/depositor.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_depositor.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/bellows_root.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/research/no-receipt-admission-hold-design-2026-08-25.md
writes: depositor.py, tools/deposit_receipt.py, tools/clear_plan.py, tests/test_depositor_receipts.py, knowledge/qa/evidence/no-receipt-admission-hold/pytest_full.txt, knowledge/qa/evidence/no-receipt-admission-hold/qa-report.md
open_forks: none — 526's D-7 was truthfully empty; every choice is bound to the deposit
walks: 2
yields: 1, 0
panel: scout 8 / discovery 10 / execution 6 / capstone 7 + sweep 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per the Step 2 mandate. Step 1 is DEV-only.
