# bellows — E3: deposit watcher receipts — receipt store, writer tool, `[2r/receipts]` wrap-check step, session-id plumbing, retirement

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** `knowledge/research/e3-deposit-receipts-design-2026-08-24.md` — sha256 `3fda1d98012679cb4c39cd9a296e4428249736f33f6292284ba764ef35054d9e` — **the DESIGN (diagnostic-515), consumed T-7: every mechanism below is specified there with file:line, and this plan BINDS it — the C-corrections below govern where they and the design differ, the 513 precedent.** Also: `governance/knowledge/research/eluvian-path-audit-2026-08-24.md` §E3 (attestation boundary), `eluvian-path-rulings-2026-08-24.md`. Precedent: `executable-513` (the E2 build from design-511 — same two-step shape; its cold panel found 46/16 HIGH, which is why this plan's freeze convenes the full panel).

## Why this exists

Audit bypass (f): no artifact proves a watcher was armed after a deposit (S9). The design settles how; this plan builds it: a slug-keyed receipt file written by the Planner at deposit time, a writer tool that attests (never claims liveness), a `[2r/receipts]` group in `wrap_check.py`, the session-id argv plumbing the stop/debt hooks owe it, and receipt retirement at plan close. ⚠️ **The wrap lock is LIVE Tier-3 enforcement, and the hook half of this change ACTIVATES AT TEARDOWN-MERGE — the first wrap it judges is the depositing session's own.** Containment is designed in: the step blocks only on attributable facts, degrades to named SKIP/WARNING everywhere else, and never leans on the outer FAIL-OPEN.

## Design corrections (build-time, verified against the merged tree — these govern)

- **C-1 — the D-3 window anchor is VACUOUS; corrected semantics.** The design anchors gap detection on "clearances whose `cleared_at` falls within the session window (from the wrap sentinel's creation time to now)" — but the sentinel is created when `/wrap` is typed, and every deposit precedes it by construction (measured this session: clearance 16:46:37, wrap hours later). That window can never contain a deposit clearance; the gap arm as designed detects nothing. **Corrected `[2r/receipts]` semantics:** (a) **BLOCKING arm — attributable only:** every receipt in `receipts/` with `session_id == argv id` must match a clearance row (`content_hash`, lifecycle.db read-only) OR a `hold-*.hold.json` sidecar; an own-session receipt matching nothing is a **failure** (`[2r/receipts] N receipt(s) from this session match no clearance or hold — stale or mistyped receipt`). (b) **WARNING arm — global, non-blocking:** clearances with `cleared_at` in a trailing 24h lookback that match NO receipt from ANY session print `[2r/receipts] WARNING: N cleared deposit(s) in the last 24h without a receipt — arm a watcher and write a receipt at every deposit.` — never a failure (anti-foreign-block, design D-4). (c) The honest boundary, restated in the step's own output when the warning arm fires: a receipt-less deposit cannot be attributed or blocked; the narrowing is ritual + visibility, per the audit's armed-and-attested ceiling.
- **C-2 — the wrap_check env posture moved under the plan's feet.** Design D-5's "the file remains structurally incapable of env reads (no `import os`)" is superseded by origin commit `75cc1b4` (merged at `246d89c`): `wrap_check.py` NOW imports os (:32) and resolves `ROOT`/`MEMORY` via `ELUVIAN_WRAP_ROOT`/`ELUVIAN_WRAP_MEMORY`. The design's sequencing claim held exactly as written: `RECEIPTS = BELLOWS / "receipts"` derives from `BELLOWS` ← `ROOT` and inherits the override automatically. **This plan follows the file's NEW idiom, adds NO new env variables, and derives every new path from the existing constants.**
- **C-3 — the retirement anchor.** Design gap row 11 guessed "bellows.py :1201-1208 or equivalent". Measured close transitions: `lifecycle.mark_plan_state(plan_id, "closed", …)` at **bellows.py:1260 and :2582**; halted transitions exist in the same bookkeeping class. Retirement is ONE helper `_retire_receipts(slug)` (move `receipts/receipt-<slug>-*.json` → `receipts/archived/`), called from the close/halt bookkeeping at both sites, **fail-toward-WARN** — a receipts error must never break a plan close. Anchor by the `mark_plan_state` calls, never by line number.

## Numbers discipline

⚠️ **Measured 2026-08-24 against bellows `246d89c` (the merge that includes 75cc1b4); RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| X1 | design doc sha256 | `3fda1d98012679cb4c39cd9a296e4428249736f33f6292284ba764ef35054d9e` | HALT on mismatch — the spec moved |
| X2 | target blob SHA-1s BEFORE | wrap_check.py `37c453ba7173…`, wrap_stop_hook.py `0564bc6811a9…`, wrap_debt_hook.py `75e769438342…`, bellows.py `3d162ac2b082…` | `git hash-object` in YOUR worktree; HALT on mismatch — wrap_check.py is SHARED SUBSTRATE and a drift means another arc landed |
| X3 | **`T`** — tests collected BEFORE | **1288** | `python3 -m pytest tests/ --collect-only -q` tail; suite GREEN at baseline (known_failures 0) |
| X4 | failability proofs (all ABSENT) | `receipts/` **absent**; `tools/deposit_receipt.py` **absent**; `tests/test_deposit_receipt.py`, `tests/test_wrap_receipts.py` **absent** | positive control, same instrument: `tools/clear_plan.py` **present** |
| X5 | wrap_check.py post-merge posture | `import os` count **1** (:32); `sys.argv` count **0** | the argv gap is still real (G2's session-id half); the env half of the design's G2 is superseded per C-2 |
| X6 | close-transition sites | bellows.py:1260, :2582 | `grep -n 'mark_plan_state' bellows.py` — anchored by the call, not the number |
| X7 | wrap test surfaces | **20 + 28** | `grep -cE '^def test\|^    def test'` test_wrap_hooks.py / test_wrap_sentinel.py — must pass unchanged |

## Drafting Cycle
**Tier:** T2 computed — the wrap lock is live-guard enforcement (T-5/T-6-adjacent); T-7 fires (builds from the 515 design). **Cold panel: MANDATED at the freeze (full form, four seats)** — the E-family build precedent (E2: 46/16 HIGH, non-decaying) plus the hook half's activate-at-merge blast radius.
**Walk register:** `governance/knowledge/research/walk-register-executable-eluvian-e3.md`
**Walks:** walk 0 pinned; walks 1–n OWED — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk. This line is rewritten at the close from the register's actual rows, never ahead of them.
**Direction verdict (after walk 1):** owed.
**Conformance (§5):** owed per lens; recorded at the close from actual runs.
**Closing:** owed. The deposit travels the lane: ready- staging → depositor gates → **expected HOLD `shop-infra` (writes bellows code) — by construction, not a failure** → release ONLY via `tools/clear_plan.py` (manual rename is INERT under the live flip) → re-evaluation → clear → claim. ⚠️ This will be the clear tool's first LIVE happy-path release.

## Cycle Manifest
tier: T2
target: hooks/eluvian/wrap_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/knowledge/research/e3-deposit-receipts-design-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: hooks/eluvian/wrap_check.py, hooks/eluvian/wrap_stop_hook.py, hooks/eluvian/wrap_debt_hook.py, tools/deposit_receipt.py, bellows.py, receipts/README.md, tests/test_deposit_receipt.py, tests/test_wrap_receipts.py, knowledge/research/e3-qa-2026-08-24.md, knowledge/research/pytest_full.txt
open_forks: (1) a depositor-side `no_receipt` HOLD would make the receipt structural at admission — a NEW ruling beyond the audit's E3 scope (wrap_check as reader); listed for the CEO, not built; (2) design gap rows 10 (ELUVIAN_PATH.md Stage 5 line) and 12 (portability-census row) are ROOT-repo doc edits routed to a small follow-up plan, not this dispatch; (3) E5 consumes the session-id interface built here
walks: 0
yields: none
validation: pending
coherence: N/A
N/A

## MUST-PRESERVE

- ⚠️⚠️ **ACTIVATION IS SPLIT, and the hook half activates AT MERGE.** wrap_check/stop/debt changes go live for every subsequent wrap the moment teardown merges — including the wrap that closes the depositing session, whose own deposits (clearances 515/516) HAVE NO RECEIPTS (the tool did not exist when they were made). Under C-1 those produce at most the WARNING arm, never a block. **QA proves this blast-radius arm explicitly.** The daemon half (retirement in bellows.py) stays inert until the next restart.
- ⚠️⚠️ **THE `[2r/receipts]` STEP NEVER LEANS ON THE OUTER FAIL-OPEN.** `check()` has no try of its own; an unhandled exception exits 0 and silently allows the ENTIRE wrap (design D-3, wrap_check.py main try). Every error class — malformed receipt JSON, unreadable receipts dir, unreadable lifecycle.db — is handled inside the step to a named message or printed SKIP. Test each arm.
- ⚠️⚠️ **BLOCK ONLY ON ATTRIBUTABLE FACTS.** Own-session receipts matching nothing → failure. Everything unattributable → warning or SKIP (C-1; anti-foreign-block, design D-4).
- ⚠️ **Attestation says "armed", never "alive"** — tool output, receipt JSON `watcher` field, and the embedded `attestation_boundary` sentence (design D-2). Any liveness claim is a defect.
- ⚠️ **Receipts key by SLUG** (`receipt-<slug>-<session_id>.json`); session id shape `[A-Za-z0-9-]+`; hash = sha256 over raw `read_bytes` (design G4) — cross-checkable against `clearances.content_hash`.
- ⚠️ **wrap_check.py is SHARED SUBSTRATE** (portability arc + E5): follow the post-75cc1b4 idiom, derive `RECEIPTS = BELLOWS / "receipts"`, add no new env variables, keep every existing group's text byte-identical except the additions.
- ⚠️ **Worktree + test isolation:** all writes project-relative in YOUR cwd; every test uses tmp dirs AND tmp DBs — never the real `receipts/`, never the real `lifecycle.db`, never a real watched `decisions/` path (a claimable-looking file in a live watched dir summons the RUNNING daemon mid-test).
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **DEV runs TARGETED tests only; the full suite belongs to QA.**

## STEP 1 — DEV: receipts substrate, wrap-check step, plumbing, retirement

**Role:** DEV. `<id>` from your plan filename.

**A0 — preconditions.** Assert X1–X7 (X1/X2 HALT on mismatch; X6 relocates by anchor). Three-way start: pins as stated → proceed; the substrate already present (receipts/ + tool + `[2r/receipts]` in wrap_check) → ALREADY APPLIED no-op success; else partial → STOP with inventory.

**A1 — implement, the design as corrected governing:**
- `receipts/README.md` (creates the directory in git): states the contract — slug-keyed receipt files, the attestation boundary verbatim, retirement to `archived/` on plan close.
- `tools/deposit_receipt.py` (design D-2): args plan-path + session-id; derives slug (strip `ready-`/`.md`) and hash (raw `read_bytes`); validations — plan exists in a watched `decisions/` dir (config.json `watched_projects`), session id shape-valid, no existing receipt for same slug+hash (refuse loudly; a NEW hash under the same slug writes a NEW receipt); writes `receipts/receipt-<slug>-<session_id>.json` (creating `receipts/` on demand) with the design's exact content shape incl. `attestation_boundary`; prints `Receipt written: <abs path> — watcher armed (not a liveness claim)`; all refusals to stderr with the design's messages; resolves the bellows root from `__file__`, never a hardcoded absolute path.
- `hooks/eluvian/wrap_check.py`: `check(session_id: str | None = None)`; `main()` parses `sys.argv[1]` (empty → None); new `[2r/receipts]` group appended after step 4, implementing **C-1's corrected semantics** — blocking arm (own receipts vs clearances/hold-sidecars), warning arm (24h lookback, any-session), SKIP arms (`no session_id`, `receipts/ absent or unreadable`, `lifecycle.db unreadable` — each with its named printed line), every arm's errors handled in-step. lifecycle.db opened `sqlite3 "file:…?mode=ro"` equivalent (`sqlite3.connect(f"file:{path}?mode=ro", uri=True)`).
- `hooks/eluvian/wrap_stop_hook.py` :207-210 → `[sys.executable, str(CHECK), session_id or ""]`.
- `hooks/eluvian/wrap_debt_hook.py` :80-83 → same argv addition (design D-3 SessionStart arm: a new session's id matches no deposits — the step reports OK/SKIP, never debt).
- `bellows.py`: `_retire_receipts(slug)` per **C-3** — moves `receipts/receipt-<slug>-*.json` → `receipts/archived/`, whole-body try to WARN log; called at the close transitions (X6 anchors) and the halted bookkeeping.

**A2 — targeted tests:**
- `tests/test_deposit_receipt.py`: write round-trip (all fields, boundary sentence present); refusal arms — missing plan, unwatched dir, invalid/missing session id, duplicate slug+hash; new-hash-new-receipt; receipts dir auto-created.
- `tests/test_wrap_receipts.py`: `[2r/receipts]` pass (own receipts all matched); blocking arm fires on an own-session receipt matching nothing; warning arm on a receipt-less clearance (non-blocking — `check()` returns no failure for it); SKIP arms (no session id / no dir / unreadable DB); malformed receipt JSON → warning, no exception; **anti-foreign-block: a foreign session's receipt-less state never adds a failure**; **the blast-radius arm: clearances present + receipts empty + session id given → warnings only, zero failures**; `_retire_receipts` moves matching files, ignores missing, never raises. ⚠️ ALL in tmp dirs/DBs.

**A3 — verify before committing:** new tests green (paste raw); `py_compile` **all five .py files this step changes**; run `python3 hooks/eluvian/wrap_check.py` (no argv) from the worktree and paste the `[2r/receipts]` line — it must print the SKIP note (read the CHANNEL: other groups may legitimately fail mid-session; you are asserting only the new line's presence and form).

**A4 — commit** (worktree): `git add receipts/README.md tools/deposit_receipt.py hooks/eluvian/wrap_check.py hooks/eluvian/wrap_stop_hook.py hooks/eluvian/wrap_debt_hook.py bellows.py tests/test_deposit_receipt.py tests/test_wrap_receipts.py && git commit -m "[<id>] E3 receipts: store+tool+[2r] wrap-check step+argv plumbing+retirement (hook half live at merge; daemon half inert until restart)"`

⚠️ **IF ANY A3 CHECK FAILS: no commit, no revert, no retry — leave the worktree as evidence, report, raise `### Flags for CEO`.**

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/receipts/README.md`
- `/Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_deposit_receipt.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_receipts.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/receipts/README.md`
- `/Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_deposit_receipt.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_receipts.py`

## STEP 2 — QA

**Role:** QA. ⚠️ Fresh agent: re-measure; the DEV report is not evidence.

**Q1 — full suite.** `python3 -m pytest tests/ -q`; deposit RAW output as `pytest_full.txt`. Baseline **1288 collected, green, known_failures 0**; the count grows by the two new files; assert zero failures/errors, report the total. The hot-path-guard lesson applies: the argv change touches every wrap invocation — name and diagnose every failure before classification.
**Q2 — change-set vs the design's gap table AS CORRECTED:** rows 1–9 and 11 present at their sites (C-3's anchors for row 11); **rows 10 and 12 verifiably ABSENT — `git diff` shows NO edit to any file outside the bellows repo** (both are root-repo doc edits routed to a follow-up plan, open_forks (2)); every existing wrap_check group's message text byte-identical (diff the strings); `is_runnable_plan`/claim path untouched.
**Q3 — behavioral spot-probes on tmp environments:** the full ritual sim — tmp plan file → tool writes receipt → tmp lifecycle DB with a matching clearance → `wrap_check`-equivalent step invocation with the session id → pass; delete the receipt → warning arm only (no failure); corrupt the receipt's hash → blocking arm fires; foreign-session receipt-less clearance → warning only.
**Q4 — activation scoping, stated honestly:** (a) hook half LIVE AT MERGE — the next `/wrap` on this machine runs the new step; the blast-radius arm (A2) is the proof it cannot trap that wrap (clearances 515/516 receipt-less → warnings); paste the A3-style no-argv run's `[2r/receipts]` line from the merged tree; (b) daemon half (retirement) INERT until restart — the running daemon predates the merge; state the PID and its start time vs the merge time.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1–Q4 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e3-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e3-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Commit:** `git add knowledge/research/e3-qa-2026-08-24.md knowledge/research/pytest_full.txt && git commit -m "[<id>] qa: E3 receipts — full suite + evidence"`

## Deposit ritual

Stage as `ready-executable-eluvian-e3-receipts.md`. **Expected depositor outcome under the LIVE flip: HOLD `shop-infra` — by construction, not a failure.** Release ONLY via `python3 tools/clear_plan.py <hold-file>` (manual rename is INERT; the tool renames to `ready-` and the live daemon re-evaluates). The depositing session arms a slug-keyed watcher BEFORE staging, per the very contract this plan builds.
