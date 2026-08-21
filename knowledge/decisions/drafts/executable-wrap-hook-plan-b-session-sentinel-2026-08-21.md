# bellows — wrap-hook layer, plan B: per-session sentinel + anti-hijack message
**Date:** 2026-08-21 | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** targeted (DEV) → full suite + sentinel canary (QA) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2 | **qa_steps:** 2 | **Depends on:** plan A (`executable-wrap-hook-plan-a-vendor-and-exemption-2026-08-21`) MUST be closed first — it creates the vendored tree under `bellows/hooks/eluvian/` that this plan edits and repoints the live wiring there. Also Done/diagnostic-495.

**auto_close:** false
**pause_for_verdict:** always

## Context

The second half of the CEO-directed pair (split 2026-08-21 on `cycle_check ESCALATE:yield-rising`, corroborating diagnostic-495 Q6). Plan A exempts DAEMON sessions from the wrap hooks. This plan fixes the hazard that remains for INTERACTIVE ones.

**The capture this closes (measured 2026-08-21):** the Planner session was Stop-blocked by a *different terminal's* armed wrap and handed that session's checklist as if it were its own to complete. It held for ~5 minutes with no in-band way to distinguish "the other session is still working" from "it was abandoned". The daemon exemption does not help here — neither session is a daemon. Earlier the same day, exec-493's worker took the other branch of the same defect: it satisfied the checklist and **pushed three repos outside its scope**, then its Stop hook removed the SHARED sentinel and disarmed the CEO's in-flight wrap.

Both are one root cause: **`.wrap-in-progress` is a single file at the governance root, so ownership is global.** Any session can arm it, be blocked by it, and clear it.

**Enabler, measured:** all three hook payloads carry `session_id` — SessionStart and Stop (diagnostic-495 Q3(b)) and UserPromptSubmit (measured 2026-08-21: keys `cwd`, `hook_event_name`, `permission_mode`, `prompt`, `session_id`, `transcript_path`). Plan A already added the stdin parse and logs the id; this plan uses it for ownership.

**⚠️ A BOUND ON WHAT THIS CAN FIX — do not promise more, in code or in prose.** `wrap_check` cannot scope its *push* checks to "this session's own commits": a git branch is shared, so `git push` publishes every commit on it and "push only mine" is not expressible. This plan fixes the **disarm** hazard (session B can no longer clear session A's lock) and the **misattribution** hazard (a blocked session is told plainly that items may not be its own, and to wait rather than resolve). It does NOT let two sessions wrap independently on shared repos. That residual is real and stays documented, not designed around.

## MUST-PRESERVE

- **The CEO's interactive wrap lock must never end this plan disabled or weakened.** A wrap that is armed must still block until it verifies. The whole point is to make ownership precise, never to make the lock easier to escape.
- **Never create or delete a sentinel at the real governance root** — not by hand, not as a test side effect. Tests and the canary use `ELUVIAN_WRAP_ROOT` (plan A shipped it) to point at a scratch directory.
- Edit ONLY the vendored copies under `bellows/hooks/eluvian/`. Plan A repointed the live wiring there; `~/.claude/eluvian/` still holds the pre-migration originals and must stay untouched as the manual revert.
- ⚠️ You are a daemon-dispatched session and plan A has exempted you, so you will NOT be debt-injected or Stop-blocked. Do not read that absence as evidence the lock is broken — it is plan A working. Never resolve a wrap; never commit, push, or add outside this plan's declared scope, in any repo, for any reason.

## Drafting Cycle
**Tier:** T2 — triggers: **T-6** (enforcement surface) + T-8 (novel ownership model). T-5 no longer fires: plan A put this tree under version control, so every edit here has a diff and a revert.
**Walk 0 (context pin) — REAL (2026-08-21):**
1. Newest same-class: plan A, this plan's immediate predecessor and the source of the vendored tree. Clone-diff: A edits the same three hook files; confirm A's `session_id` parse and `ELUVIAN_WRAP_ROOT` support are present before building on them, and do NOT re-implement either.
2. Pre-edit pins (agent RE-VERIFIES, does not trust): `bellows/hooks/eluvian/wrap_stop_hook.py` gates on a sentinel and calls `SENTINEL.unlink()` on a passing check; `wrap_arm_hook.py` calls `SENTINEL.touch()` on a trigger match; both resolve the root through `ELUVIAN_WRAP_ROOT` after plan A.
3. The two capture narratives above are Planner-measured from `bellows/logs/*-step.json` and `~/.claude/eluvian/hooks.log`; diagnostic-495 carries the evidence.
- Cold panel (T2, §2.6): REQUIRED — status recorded before deposit.

## STEP 1 — DEV: per-session sentinel + anti-hijack message

**Role:** DEV. Edit ONLY under `bellows/hooks/eluvian/`.

⚠️ **Verify plan A's groundwork FIRST.** Confirm in the vendored copies that (a) each hook parses its stdin payload and has `session_id` available, and (b) the sentinel root honours `ELUVIAN_WRAP_ROOT`. If either is absent, STOP — plan A is not actually closed and this plan is being run out of order.

**(1) Per-session sentinel.** All three hooks already read stdin and discard it; parse it instead and take `session_id`.
- `wrap_arm_hook.py`: on a trigger match, touch `ROOT / f".wrap-in-progress-{session_id}"`.
- `wrap_stop_hook.py`: consider ONLY its own `.wrap-in-progress-{session_id}` when deciding whether it is armed, and on a passing check unlink ONLY that file. ⚠️ It must become structurally impossible for one session's Stop hook to clear another's sentinel — this is the defect that disarmed the CEO's wrap.
- ⚠️ **Backward compatibility — a legacy BARE `.wrap-in-progress` keeps EXACTLY today's semantics, and is never claimed by a session.** It arms any session that finds it, and it is removed on a passing check — i.e. precisely what the current code does. New arms always create per-session files, so bare sentinels exist only across the upgrade boundary and self-clear on the first completed wrap. ⚠️ **Do NOT implement migrate-on-encounter** (renaming the bare file to `.wrap-in-progress-{session_id}` to give it an owner): it sounds tidier and is worse, because the first session to END A TURN claims it — which is not necessarily the session that armed it. That converts the disarm defect into a misappropriation defect, silently locking an uninvolved session into someone else's wrap. Preserving legacy behavior unchanged adds no hazard that does not already exist today, and the transient window closes by itself. Test both: a bare sentinel still arms and still clears on pass, and a bare sentinel is NEVER renamed.
- ⚠️ **Missing `session_id`:** if stdin is unparseable or carries no `session_id`, fall back to the bare-sentinel behavior. Do NOT invent an id — a random or pid-derived id would make the sentinel unclearable by the next turn.

**(2) Other-session awareness — the anti-hijack message.** When a Stop hook blocks, have it detect OTHER `.wrap-in-progress-*` files and append to the block reason, naming them: that another session is also wrapping, that some or all listed items may belong to it, and — explicitly — **do NOT commit, push, add, or otherwise resolve work you did not do; wait for that session to finish.** ⚠️ **The message must also give a BOUNDED escape, or a session can be trapped indefinitely by an ABANDONED wrap** (measured 2026-08-21: the Planner session was held ~5 minutes by another terminal's wrap and had no in-band way to tell "still working" from "abandoned"). For each foreign sentinel, include its **age** (from mtime) — a fresh one means wait, a stale one means escalate — and state that clearing a FOREIGN sentinel is the CEO's decision alone and never the model's. ⚠️ This message is the only thing standing between a blocked session and the exec-493 behavior; it must instruct WAITING, never resolution. Keep `wrap_check.py`'s own checks unchanged — per the Context bound below, the push checks cannot be scoped per session, and pretending otherwise in code is the failure this clause exists to prevent.

**(3) Targeted tests** (the full suite runs in QA): create `bellows/tests/test_wrap_sentinel.py` covering — a per-session arm/stop round-trip; **one session's Stop hook cannot clear another session's sentinel** (the disarm defect, and the single most important assertion in this plan); a legacy BARE sentinel still arms and still clears on a passing check; a bare sentinel is NEVER renamed; the missing-`session_id` fallback; and the anti-hijack message appearing, naming the foreign sentinel and its age, when a foreign sentinel exists.
⚠️ **Control the environment explicitly in every test.** Plan A means `BELLOWS_DISPATCH=1` is set on the session running pytest, so the exemption guard fires by DEFAULT and any test asserting that a hook BLOCKS would silently invert. Add an `autouse` fixture that `monkeypatch.delenv("BELLOWS_DISPATCH", raising=False)` and sets `ELUVIAN_WRAP_ROOT` to `tmp_path`, then have each test set what it needs. ⚠️ Put it in `tests/test_wrap_sentinel.py`, NOT the shared `tests/conftest.py` — a conftest-level env fixture would change the environment every existing test runs under. This is the [[hot-path-guard-needs-mock-audit]] class.

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_sentinel.py`

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_sentinel.py`

**Commit:** repo-asserting absolute form (`git -C /Users/marklehn/Developer/GitHub/bellows add <abs> && git -C ... commit -m "..."`), explicit pathspec, add before commit. Your final operation is the commit.

## STEP 2 — QA: full suite + the two-session sentinel canary

**Role:** QA.

**MANDATORY Rule 20 self-check banner** — the deposited QA report MUST contain, verbatim, the heading `## Rule 20 — QA Self-Check Results` and, below it, `**PASSED — SELF-CHECK PASSED**`. Canonical block: `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. `plan_slug: wrap-hook-plan-b-session-sentinel-2026-08-21`; `qa_report_path: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/wrap-hook-sentinel-qa-2026-08-21.md`; `evidence_dir: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/`; `required_evidence_files: [pytest_full.txt, canary.txt]`. FAILED → halt.

0. `mkdir -p` the evidence directory before writing into it — it is new, and a declared deposit whose parent does not exist fails the write and then gate-fails `deposit_exists`.
1. **Full suite**, foreground, raw output to `pytest_full.txt`. Quote the counts line verbatim and compare it against plan A's baseline at `knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/pytest_baseline.txt`, quoting BOTH lines side by side. Any regression is a HALT; a MISSING baseline is also a HALT, because "no regression" would otherwise be unfalsifiable.
2. **Two-session sentinel canary** — raw output to `canary.txt`. Drive the hook SCRIPTS directly with synthetic payloads, two distinct `session_id` values, and `ELUVIAN_WRAP_ROOT` pointed at a scratch dir. ⚠️ Do NOT spawn real sessions: a genuinely blocked session cannot end its turn and would loop against the lock until timeout — reproducing the trap instead of testing it. All four assertions must hold and must be reported SEPARATELY, never as one combined verdict:
   - **(i)** session A's arm creates `.wrap-in-progress-<A>` and no bare file.
   - **(ii)** session B's Stop hook, with wrap_check passing, **leaves `.wrap-in-progress-<A>` in place** — this is the disarm defect, and it is the assertion the whole plan exists for. ⚠️ Run it in BOTH shapes, because they exercise different branches: **(ii-a)** B is UNARMED (no sentinel of its own) — the hook must take the not-armed/allow path and never reach an unlink; and **(ii-b)** B is ALSO ARMED with `.wrap-in-progress-<B>` and passes — the hook must remove ONLY `<B>` and leave `<A>`. (ii-b) is the realistic shape of the 2026-08-21 capture (two sessions both wrapping) and is the one an implementation keyed on "a sentinel exists" rather than "MY sentinel exists" would fail.
   - **(iii)** session A's own Stop hook, with wrap_check passing, removes `.wrap-in-progress-<A>`.
   - **(iv)** session B's Stop hook, while blocked, emits the anti-hijack text naming A's sentinel and its age, and instructs waiting rather than resolving.
   - ⚠️ **A FAILING canary looks like:** (ii) removing A's file (the defect intact), or (iii) NOT removing it (a lock that can never clear — worse than the defect). Neither may be read as a pass.
3. Confirm `~/.claude/eluvian/` still holds the untouched pre-migration originals. ⚠️ Do NOT compare them against the CURRENT vendored copies — plan A and this plan have both edited those by design, so that diff is meaningless and non-empty. The earnable check is against plan A's **vendor-time** commit, where the copies were byte-identical to the originals: `git -C /Users/marklehn/Developer/GitHub/bellows show <plan-A-vendor-commit>:hooks/eluvian/<file>` piped to `cmp` against the live `~/.claude/eluvian/<file>`, for all four hook files plus `wrap_check.py`. Identify that commit from plan A's Done record rather than guessing, and paste the raw `cmp` output for each file.

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/wrap-hook-sentinel-qa-2026-08-21.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/canary.txt`

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/wrap-hook-sentinel-qa-2026-08-21.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/canary.txt`

**Commit:** repo-asserting absolute form, explicit pathspec. Your final operation is the commit.
