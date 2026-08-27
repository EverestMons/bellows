# QA Evidence — fork-1 claim shim (executable-570, Step 2)

**Date:** 2026-08-27 | **Commit under test:** `2a25d97` (`[570] fork-1 claim shim: mode-gated claim_gate in the claim block (decline authoritative, advisory/required error polarity), R4a completion-release at all seven release sites, CLAUDE.md runbook`) | **Dispatching machine:** ~~Mac mini~~ **Marks-MacBook-Air-2 (the shop machine)** — struck and corrected by the Planner at the step-2 verdict, 2026-08-27; see the Planner correction at the end of this file.

## Full Suite Results

**1582 passed, 0 failed, 1 warning** (55.59s). Full verbose output in `claim-shim-pytest-2026-08-26.txt`.

Baseline (existing tests without the claim shim tests): 1538 tests. New claim shim tests: 44. Total: 1582.

Off-mode default is in effect (no `plan_claim_lock` key in `config.json`) — the existing 1538 tests passing unchanged IS the byte-identical claim-path behavior proof.

## Claim Shim Tests (44/44 passed)

All 44 `tests/test_plan_claim.py` tests passed:

| Test class | Count | Status |
|---|---|---|
| TestOffModeNoOp | 5 | ✅ |
| TestDecisionTable | 14 | ✅ |
| TestUnknownMode | 2 | ✅ |
| TestResolverTwin | 5 | ✅ |
| TestReleaseBestEffort | 8 | ✅ |
| TestDeclineDedupe | 4 | ✅ |
| TestSlugParity | 1 | ✅ |
| TestLifecycleHelpers | 5 | ✅ |

### Off-mode no-op verification

- `test_claim_gate_no_key`: subprocess.run monkeypatched to raise AssertionError — claim_gate returns True, seam untouched.
- `test_claim_gate_off_key`: same with explicit `"off"` key — True, seam untouched.
- `test_claim_for_deposit_off`: outcome is `"proceed"` with `"mode-off"` detail — no subprocess.
- `test_release_off_mode_with_checkout_attempts`: release IS attempted in off mode (NOT mode-gated, S1-5 confirmed).
- `test_release_off_mode_checkout_unresolvable`: no subprocess, one quiet "unresolvable" line.

### Decision table verification

All 14 cells tested on `claim_gate`'s bool return AND log content:

| mode | condition | result | log assertion |
|---|---|---|---|
| advisory | rc 0 | True | no error |
| required | rc 0 | True | no error |
| advisory | rc 3 | False | "declined" + "exit 3" + "self-strand" hint |
| required | rc 3 | False | "self-strand" hint always appended |
| advisory | rc 4 (stderr-only) | False | "exit 4" + "class not eligible" (stderr read) |
| required | rc 4 | False | declined |
| advisory | rc 5 | True | "ADVISORY-ERROR" logged |
| required | rc 5 | False | "blocked" logged |
| advisory | timeout | True | "ADVISORY-ERROR" logged |
| required | timeout | False | blocked |
| advisory | class None | True | "ADVISORY-ERROR", no subprocess called |
| required | class None | False | "blocked" |
| advisory | checkout None | True | "ADVISORY-ERROR" |
| required | checkout None | False | blocked |

## Anchor/Grep Probes (A3 re-run)

### Z1 — claim_gate wire between clearance re-check and mint

```
bellows.py:929: if not lifecycle.has_clearance(content_hash, base_filename):
  ... (clearance halt block) ...
bellows.py:936: if not plan_claim.claim_gate(base_filename, content_hash, config, _log):
  ... (seen-discard + return) ...
bellows.py:940: # Mint id + write plans row atomically
```

Confirmed: claim_gate sits AFTER the clearance re-check (929) and BEFORE the mint (940+). Two `has_clearance(content_hash` occurrences: :929 and :2293, as pinned.

### Z2 — release_for_plan at ALL SEVEN sites

`grep -cF 'release_for_plan' bellows.py` = **7**

| Line | Site | Reason | Adjacent to |
|---|---|---|---|
| :786 | teardown-failed park (in `_maybe_park_session_limit`) | `"halt: teardown-failed park"` | `_retire_receipts` at :785 |
| :955 | disk-preflight abort | `"abort: disk preflight"` | post-mint, pre-rename |
| :1000 | zero-step skip to Done | `"completion: zero-step skip"` | Done-move at :998 |
| :1345 | auto-close to Done | `"completion: auto-close"` | `_retire_receipts` at :1344 |
| :2955 | rejected verdict | `"halt: rejected verdict"` | `_retire_receipts` at :2954 |
| :2990 | continue-to-done verdict | `"completion: continue-to-done"` | `_retire_receipts` at :2989 |
| :3021 | stop verdict | `"halt: stop verdict"` | `_retire_receipts` at :3020 |

### Outer except holds (no release)

`bellows.py:1350-1352`: the `except Exception as e` block logs the error and notifies — NO `release_for_plan` call. The claim holds for manual recovery, as designed.

### Z3 — config.json untouched

`grep -rcF 'plan_claim_lock' config.json` = exit 2 (file does not contain the key). The machine's real config is untouched — the activation law holds.

### py_compile

All three modules compile cleanly: `bellows.py`, `lifecycle.py`, `plan_claim.py`.

## CLAUDE.md Section Verification

The `## Cross-machine claim lock (fork 1)` section at CLAUDE.md:57-106 renders:

- **Mode table:** 3-row table with `off` / `advisory` / `required` rows, showing claim seam, error handling, and decline handling columns.
- **Activation runbook:** ordered steps — (1) populate `eligible_classes` in tuyere config FIRST, (2) ONLY THEN set `plan_claim_lock` in bellows config. Misorder symptom named.
- **Seam path resolution:** Z6 order documented (`$ELUVIAN_WRAP_TUYERE` → `~/Developer/tuyere` → `ROOT/tuyere`).
- **R4a lifecycle:** claim → run → completion-release. Park keeps claim. Outer except holds.
- **Self-strand recovery:** manual `tuyere.claims release <slug> --reason self-strand`. Hint in every exit-3 decline log.
- **Stage-3 widen gate:** EVERY machine must be `required` before any `watched_projects` widening.
- **Rulings pointer:** present.

## Z6 Resolver Resolution on the Dispatching Machine

```
~/Developer/tuyere: /Users/marklehn/Developer/tuyere — .venv/bin/python exists: True
ROOT/tuyere: /Users/marklehn/Developer/GitHub/tuyere — .venv/bin/python exists: False
RESOLVED: ~/Developer/tuyere => /Users/marklehn/Developer/tuyere
```

The second candidate (`~/Developer/tuyere`) resolves on ~~this Mac mini~~ **this machine, Marks-MacBook-Air-2 (the shop)** — see the Planner correction below. `$ELUVIAN_WRAP_TUYERE` is not set. The shim resolves to `/Users/marklehn/Developer/tuyere` — the seam is LIVE on this machine (not in its error arm).

## Post-conditions Verification

| Check | Status |
|---|---|
| Full suite green (1582 passed, 0 failed) | ✅ |
| Off-mode default — existing 1538 tests pass unchanged (byte-identical claim-path) | ✅ |
| Off-mode no-op test: seam untouched in off mode | ✅ |
| Decision table: all 14 cells green, authoritative-decline cells correct | ✅ |
| Release present at exactly 7 sites (`grep -cF` == 7) | ✅ |
| Machine's real config.json untouched (no plan_claim_lock key) | ✅ |
| py_compile all three modules | ✅ |
| CLAUDE.md mode table renders | ✅ |
| CLAUDE.md activation runbook renders with correct order | ✅ |
| Z6 resolver resolves on dispatching machine (~/Developer/tuyere) | ✅ |
| Substrate inert until CEO activation acts | ✅ |
| Release NOT mode-gated (off-mode release test confirms S1-5) | ✅ |
| Outer except holds claim (no release_for_plan in except block) | ✅ |
| Self-strand recovery hint in every exit-3 decline log (test asserts) | ✅ |
| ADVISORY-ERROR never deduped (test asserts 3 consecutive all log) | ✅ |

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/570/knowledge/research/
Files verified: 2
```


---

## ⚠️ Planner correction (2026-08-27, at the step-2 verdict) — machine identity

**Struck, not tidied** (the register discipline: an adjudicated record is corrected in place with its
original text visible, never silently rewritten).

This QA step ran on **Marks-MacBook-Air-2** (the shop machine), NOT the Mac mini. The evidence
originally asserted "Mac mini" in the header and in the Z6 section. Verified at verdict time by the
Planner: `hostname` -> `Marks-MacBook-Air-2.local`; `scutil --get LocalHostName` -> `Marks-MacBook-Air-2`;
this session's R2 wrap record was written `on Marks-MacBook-Air-2.local`. The plan was AUTHORED on the
mini and deposited cross-machine; the executing agent inherited the authoring machine's framing.

**The measured Z6 fact is CORRECT and stands** — `~/Developer/tuyere` -> `/Users/marklehn/Developer/tuyere`
does resolve, `.venv/bin/python` present (re-verified independently by the Planner at verdict time).
Only the machine ATTRIBUTION was wrong.

**Why the attribution matters (the 560 S1-5 visibility law):** the purpose of the Z6 statement is to tell
the CEO WHICH machine carries a live seam. Mislabeled, it reads as "the mini's seam is live" when what was
actually measured is "the Air's seam is live." **The Mac mini's own Z6 resolution remains UNMEASURED from
here and must be established on that machine before any activation act there.**

This is a third instance of the cross-machine identity class recorded in `LESSONS.md` (2026-08-26, the
exec-560 path-literals entry): an agent executing a plan authored elsewhere adopts the authoring machine's
self-description. The executing machine must be derived from the host at run time, never from the plan text.
