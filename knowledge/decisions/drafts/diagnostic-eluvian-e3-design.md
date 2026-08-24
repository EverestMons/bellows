# bellows — E3 design: deposit watcher receipts — receipt artifact, writer tool, wrap-check step, session-id plumbing, coordination fences

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only design; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md` §E3 (509-corrected) and `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md` — both consumed T-7 without re-derivation. **Baton correction consumed as a GIVEN:** receipts are keyed by SLUG (`plans.deposit_placeholder_name`), never by a predicted numeric id — the 512/513 id collision is the measured reason (LESSONS.md 2026-08-24). **Structural precedent, cited because it is the SAME build class run through the SAME two-step shape:** `diagnostic-511` (E2 design) → `executable-513` (build; its cold panel found 46/16 HIGH). E3's executable builds from THIS plan's deposit the way 513 built from 511's.

## Why this exists

Audit bypass (f): *no artifact proves a watcher was armed after a deposit* — the watcher-per-deposit directive lives in Planner memory alone (S9). E3 writes a receipt at deposit time that the wrap check reads, narrowing S9 from unverifiable to **armed-and-attested**. The attestation boundary is fixed by the audit and non-negotiable: *"a receipt written at deposit time proves the watcher was ARMED, not that it stayed alive. Liveness of a session-local monitor is not externally verifiable, and an E3 that claims otherwise would be a printed check wearing a gate's name."* This diagnostic settles every design question against the real code so the executable inherits decisions, not open questions — E3 touches `wrap_check.py`, a LIVE Tier-3 guard shared with two other efforts (D-5), which is exactly why the design is settled read-only first.

## What this plan does NOT do

- **It writes NO code.** One research deposit: the design document with a Rule 27 gap table (file:line per decision), exactly the 511 pattern.
- **It does not claim liveness.** Any design text implying the receipt proves the watcher STAYED alive is a defect, not a feature.
- **It does not fix wrap-lock portability.** The 512 census owns that repair; this design DECLARES what it adds to that census (D-5), nothing more.
- **It does not restart the daemon or touch any live state.**

## Numbers discipline

⚠️ **Measured 2026-08-24 by the Planner; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| G1 | deposit-receipt artifacts in the shop today | **0** (absence earned) | `grep -cF 'receipt'` → depositor.py **0**, hooks/eluvian/wrap_check.py **0**, wrap_stop_hook.py **0**, bellows.py **2** — both `receipt_status`, the claude-CLI cost field at :995/:1127, NOT deposit receipts. Positive control, same instrument: `grep -cF 'hold-'` depositor.py = **6**. Bypass (f) re-derived |
| G2 | session id reaches the hook layer but NOT wrap_check | **plumbing gap confirmed** | wrap_stop_hook.py:80-91 extracts `session_id` from stdin JSON, :70-77 validates `[A-Za-z0-9-]+`, :186-188 uses it — yet :207-210 invokes wrap_check.py with NO arguments; wrap_check.py reads `sys.argv` **0** times and has **no `import os`** (the 512 census's half-wired lesson: inheritance is not consumption — the truth source must READ the id) |
| G3 | clearance record shape | lifecycle.py:170-183 | `clearances(plan_path, content_hash, assigned_class, cleared_by, cleared_at, consumed_at)`; partial-unique `(content_hash, plan_path) WHERE consumed_at IS NULL`; INSERT at :207; consume at :233/:268. **No session column, no slug column** — clearance identity ≠ receipt identity |
| G4 | content hash algorithm to mirror | depositor.py:538 | `hashlib.sha256(plan_bytes).hexdigest()` over RAW BYTES — a receipt that hashes any other representation cannot be cross-checked against clearances |
| G5 | lifecycle.db sole writer is the daemon | **True** (511 G3, restated) | the Planner writes the receipt from ITS OWN session process — so a receipt CANNOT be a lifecycle.db row without breaking the sole-writer model; the receipt is a FILE, or the design defends otherwise explicitly |
| G6 | the sidecar idiom the receipt can mirror | depositor.py:546, :570-583 | `hold-<name>.hold.json` `{"hold_reason", "held_at"}` — the shop already pairs a state file with a JSON sidecar |
| G7 | existing wrap-hook test surface | **20 + 28** | `grep -cE '^def test|^    def test'` tests/test_wrap_hooks.py = 20, tests/test_wrap_sentinel.py = 28 — the surfaces the executable must leave green |
| G8 | live state at authoring | clearances **0** rows; `id_sequence` next **515** (prediction only — RE-READ at deposit, key nothing on it); 10 watched projects | `sqlite3 "file:lifecycle.db?mode=ro"`; config.json `watched_projects` |

## Drafting Cycle
**Tier:** T1 computed — T-7 fires twice over (consumes audit+rulings+baton correction; feeds the executable). T-2/T-5/T-6 do not fire (read-only).
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-eluvian-e3-design.md`
**Walks:** walk 0 pinned; walks 1–n OWED — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk. This line is rewritten at the close from the register's actual rows, never ahead of them.
**Direction verdict (after walk 1):** owed.
**Cold panel:** owed — decided at the freeze with reasoning (the EXECUTABLE, not this read-only design, is where the E-family's panel evidence points; E2's panel ran on the build).
**Conformance (§5):** owed per lens; recorded at the close from actual runs.
**Closing:** owed. ⚠️ When the cycle closes, the deposit travels the lane: ready- staging → depositor gates → auto-clear (read-only) → daemon claim. ⚠️ **This deposit is activation canary arm (ii)** — the first real `ready-` plan through the LIVE admission flip; the depositing session observes clearance row 1 and the claim, and records both.

## Cycle Manifest
tier: T1
target: knowledge/research/e3-deposit-receipts-design-2026-08-24.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/depositor.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_sentinel.py, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: knowledge/research/e3-deposit-receipts-design-2026-08-24.md
open_forks: none authored here — the design implements the audit's §E3 under the baton's slug-key correction; anything needing a NEW CEO ruling is listed in D-7 rather than decided silently
walks: 0
yields: none
validation: pending
coherence: N/A
N/A

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. `lifecycle.db` is opened via `sqlite3 "file:...?mode=ro"` — the daemon is its sole writer.
- ⚠️ **Every design decision cites file:line in CURRENT code**, and every claim of absence carries a positive control (same instrument finding a known-present thing).
- ⚠️ **The attestation boundary is a hard fence:** the receipt proves the watcher was ARMED at write time — never that it stayed alive. Design text claiming more is a defect to remove, not a feature to spec.
- ⚠️ **Receipts key by SLUG (`deposit_placeholder_name`), never a predicted numeric id** — the 512/513 collision is the measured reason; any id that appears in a receipt is decorative provenance, never a lookup key.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.**
- **`grep` is ugrep: `-F` for literals**; read printed counts, never exit status.
- ⚠️ **This plan dispatches into a WORKTREE** (bellows has its own .git). The deposit path in the manifest is project-relative; write it under YOUR cwd and commit it there — the teardown merge lands it.

## STEP 1 — DIAGNOSTIC: settle the design, emit the document

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e3-deposit-receipts-design-2026-08-24.md` (project-relative `knowledge/research/e3-deposit-receipts-design-2026-08-24.md` in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the receipt artifact.** Form and location, defended against alternatives. G5 constrains form: the Planner writes from its own session process, so a lifecycle.db row is ruled out unless you defend a safe write path explicitly — the default answer is a FILE. Location candidates to weigh: (a) a new `bellows/receipts/` directory keyed by slug (e.g. `receipt-<slug>.json`); (b) a sidecar next to the plan file in the watched `decisions/` dir. ⚠️ Whatever wins must satisfy: **survives the plan's whole rename lifecycle** — the depositor renames `ready-X.md` → `X.md` (depositor.py:496-514 class of behavior) and the daemon renames onward (`in-progress-`, `Done/`), so a sidecar that travels by filename adjacency breaks at the first rename — state how the chosen location holds identity across ALL renames (this is what slug-keying buys; show it); Planner-writable with no daemon cooperation; wrap_check-readable with stdlib only; keyed by slug + content hash (sha256 raw bytes, G4, cross-checkable against `clearances.content_hash`) + session id (shape-validated like wrap_stop_hook.py:70-77) + `armed_at` timestamp + an honest attestation field (what watcher, e.g. "gate-watcher armed in depositing session"); the audit's boundary sentence embedded so every receipt self-documents what it does NOT prove. Decide git status: committed to the bellows repo (then WHICH wrap step commits them) or untracked-by-design (then how the wrap check treats them and how they never rot) — state the interaction with wrap_check's porcelain scoping (wrap_check.py:97-106 scopes step [2] to `verdicts/resolved`) either way.
**D-2 — the writer tool.** `bellows/tools/deposit_receipt.py` (name yours to decide; the tools/ dir precedent is clear_plan.py). Run by the Planner AT deposit time as part of arming the watcher. Specify: what it validates before writing (plan file exists in a watched decisions/ dir; hash it computes matches the file's raw bytes; slug derived from the filename matches; session id present and shape-valid); its idempotency arm (re-run for the same slug+hash: refuse, overwrite, or append — pick with reasons; a second deposit of a corrected plan under the same slug has a DIFFERENT hash — say what happens); what it prints on success (the receipt path — the depositing session cites it); what it refuses loudly. ⚠️ The tool ATTESTS, it cannot VERIFY a session-local Monitor exists — its output text must say "armed" and never "alive"; specify the exact attestation wording.
**D-3 — the wrap_check step.** The audit's sentence: *"every deposit made this session has a receipt."* Settle its exact semantics against the measured truth sources, each with what it can and cannot see: (i) receipts themselves — prove arming for deposits that HAVE receipts, structurally cannot catch a receipt-less deposit; (ii) `clearances` rows in a time window (lifecycle.py:207, `cleared_at`) — catch cleared deposits with no matching receipt, but carry no session attribution (G3) and require a window boundary; (iii) `hold-*.hold.json` `held_at` (G6) — the held-deposit arm; (iv) `plans.deposit_placeholder_name` + `created_at` — claimed plans; (v) git history of the watched decisions/ dirs. Pick the check's semantics, state the honest boundary (which deposit routes a receipt-less deposit CAN evade, and why that is still a narrowing of S9 worth shipping — the audit already accepts armed-and-attested as the ceiling). **Session-id plumbing:** wrap_stop_hook already holds a validated session id (G2) — specify passing it to wrap_check as **argv** (the truth source must READ it; the 512 census measured what happens when a wrapper honors an override the verdict subprocess never consumes), the exact invocation-site change (wrap_stop_hook.py:207-210), and the degrade arms: wrap_check invoked with NO session id (wrap_debt_hook at SessionStart, manual `python3 wrap_check.py`) — does the receipts step SKIP with a printed note, or fall back to a window heuristic? Pick with reasons; a step that false-blocks a fresh session on a PRIOR session's deposits re-creates the trap class the lock is FAIL-OPEN against. **FAIL-OPEN preserved:** the step lives inside `check()`'s try (wrap_check.py:151-155); a malformed receipt JSON must degrade to a named failure message or a skip, never an unhandled trap; state which.
**D-4 — receipt lifecycle and concurrency.** When is a receipt retired — on plan close, on wrap pass, never (append-only audit trail)? Where do stale receipts go; what stops unbounded accumulation; what does the wrap check do with receipts from OTHER sessions' deposits (it must NOT block this session on them — the anti-hijack discipline of wrap_stop_hook.py:163-177 is the precedent) and with receipts for plans that died mid-flight. Two sessions depositing concurrently: receipts keyed slug+session collide nowhere by construction — show it (the shared-append-file collision class from the 2026-08-24 concurrent-deposit incident is the failure being designed away).
**D-5 — coordination and portability fences.** `wrap_check.py` is SHARED SUBSTRATE: (a) the wrap-lock-portability arc (census: `governance/knowledge/research/wrap-lock-portability-census-2026-08-24.md`, diagnostic-512, closed; its repair executable is NOT yet authored) — E3 follows the file's existing ROOT-constant idiom (wrap_check.py:36-39), adds NO env reads, and DECLARES every machine-pinned path it introduces as new rows for that census; (b) **E5** (session-id keying of the 3b gate) needs exactly the argv plumbing D-3 designs — name the interface once so E5 consumes it unchanged; (c) state the sequencing/no-collision claim explicitly: what happens if their portability executable lands between this design and E3's build. Also the doctrine cross-reference: ELUVIAN_PATH.md Stage 2 already names "Deposit receipt (proves watcher was armed)" in its artifact list and Stage 5 gains the receipt-read step — cite both lines and state whether doctrine text needs a follow-up edit (that is a `shop-infra` write; if yes it goes in the gap table, not in silence).
**D-6 — test plan.** Unit surface: receipt write/read round-trip; the tool's refusal arms; the wrap_check step's pass / fail / no-session-id arms; FAIL-OPEN on malformed receipt; the anti-foreign-block property (a foreign session's receipt-less deposit does not block MY wrap). Which existing tests must still pass unchanged: G7's 20 + 28, and the full suite (1288 green at E2 activation). ⚠️ Consumer sweep, per the 2026-08-24 contract-consumers lesson: enumerate every consumer of wrap_check's OUTPUT (wrap_stop_hook parses returncode + stdout at :207-246; wrap_debt_hook likewise; any test fixture asserting on its message strings) and state which see a NEW message class.
**D-7 — open questions.** Anything requiring a NEW CEO ruling is LISTED, never decided silently.

**Post-conditions:** every D-section present with ≥1 file:line citation; the audit's attestation-boundary sentence quoted once verbatim; G2's plumbing gap re-derived; a Rule 27 gap table enumerating every code-change site the executable will touch (wrap_check.py step, wrap_stop_hook.py invocation, the new tool file, test files, any doctrine edit routed as follow-up).

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e3-deposit-receipts-design-2026-08-24.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e3-deposit-receipts-design-2026-08-24.md`

**Commit:** `git add knowledge/research/e3-deposit-receipts-design-2026-08-24.md && git commit -m "[<id>] design: E3 deposit watcher receipts — artifact, writer tool, wrap-check step, session-id plumbing"` in YOUR worktree cwd. `<id>` from your plan filename.
