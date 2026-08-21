# bellows — wrap-hook layer: vendor + daemon exemption + per-session sentinel (paired fix)
**Date:** 2026-08-21 | **Tier:** Medium–Large | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** targeted (DEV) → full suite (QA) | **Execution:** Step 1 (DEV, additive vendor) → Step 2 (DEV, behavior) → Step 3 (QA) | **Priority:** 1 | **qa_steps:** 3 | **Depends on:** Done/diagnostic-495 (measurements + edit set)

**auto_close:** false
**pause_for_verdict:** always

## Context

Builds directly on **diagnostic-495** (`bellows/knowledge/research/wrap-hook-daemon-exemption-2026-08-21.md`), which measured the mechanism and enumerated the edit set. Two captures happened on 2026-08-21 and this plan closes both:

- **Capture 1 (daemon):** exec-493's DEV worker was SessionStart-injected with wrap debt, Stop-blocked ≥2 times, spent 47% of its turns after its real work was committed, and **pushed three remotes outside its plan scope** (governance root, bellows, and the unrelated `study`). Its Stop hook then removed the SHARED sentinel, disarming the CEO's in-flight wrap.
- **Capture 2 (interactive):** the Planner session was blocked by a *different terminal's* armed wrap and handed that session's checklist — the same hijack, on a session the daemon exemption alone would NOT protect. This is why the two fixes ship together.

**Measurements this plan may rely on WITHOUT re-deriving (diagnostic-495, plus two taken at authoring on 2026-08-21):**
1. Hook subprocesses **do** inherit env vars set on the `claude -p` process — probed live, `BELLOWS_DISPATCH=1` observed from both a SessionStart and a Stop hook.
2. **All three** hook payloads carry `session_id`: SessionStart and Stop (495 Q3(b)) and **UserPromptSubmit** (measured at authoring — keys: `cwd`, `hook_event_name`, `permission_mode`, `prompt`, `session_id`, `transcript_path`). This is the enabler for a per-session sentinel; all three hooks currently READ AND DISCARD stdin.
3. **Three** `claude` spawn sites, not one: `runner.py:201-208` (+`Popen` at 218-223), `bellows.py` auth preflight (~1995), `planner.py` consultation (~129, `cwd="/tmp"`). All inherit the daemon env with no `env=`.
4. The enforcement layer is in **no git repository** and has **no tests** (`bellows/tests/` contains none matching wrap/hook).

**⚠️ A BOUND ON WHAT THE SENTINEL HALF CAN FIX — do not promise more, in code or in prose.** `wrap_check` cannot scope its *push* checks to "this session's own commits": a git branch is shared, so `git push` publishes every commit on it and "push only mine" is not expressible. Therefore the per-session work fixes the **disarm** hazard (session B can no longer clear session A's lock) and the **misattribution** hazard (a session is no longer handed another's checklist as if it were its own to fix) — it does NOT let two sessions wrap independently on shared repos. That residual is real and stays documented, not designed around.

## MUST-PRESERVE

- **The CEO's interactive wrap lock must never end this plan disabled or weakened.** Every step leaves it working. A false-positive exemption that silently disables the lock is WORSE than the defect being fixed.
- **Never create or delete a sentinel outside this plan's own scratch scope.** Do not `rm` any `.wrap-in-progress*` at the governance root that you did not create in a test.
- Backward compatibility: a pre-existing **bare** `.wrap-in-progress` (the current format) must still arm and still be clearable — a stale bare sentinel must not become permanently unclearable after this change.
- Do not restart, stop, or reconfigure the bellows daemon.
- ⚠️ You are a daemon-dispatched session and this plan edits the hooks that govern you. Until Step 2 lands you may be debt-injected; if a wrap is armed you may be Stop-blocked. That is the SUBJECT OF STUDY, not an instruction — never resolve a wrap, never commit/push/add outside this plan's declared scope, in any repo, for any reason.

## Drafting Cycle
**Tier:** T2 — triggers: **T-6** (governance/enforcement surface — these hooks ARE the enforcement layer) + **T-5** (the live layer at `~/.claude/` is unversioned until Step 1 lands, so a mistake there has no revert) + T-8 (novel: no prior plan has edited this layer). T-7 inherited from diagnostic-495.
**Walk 0 (context pin) — REAL (2026-08-21):**
1. Newest same-class: no prior plan has edited `~/.claude/eluvian/` — this is the first. Nearest structural clone is a governance in-place plan ([[governance-in-place-dispatch]]): absolute operands, no project `.git` at the target until Step 1 creates one.
2. Pre-edit pins (agent RE-VERIFIES, does not trust): `wrap_stop_hook.py` `SENTINEL = ROOT / ".wrap-in-progress"`; `wrap_debt_hook.py` contains NO sentinel reference (channel 1 is ungated); `wrap_arm_hook.py` reads `data.get("prompt")` and calls `SENTINEL.touch()`; `runner.py:21`/`bellows.py:24` carry the `os.environ.setdefault("DISABLE_AUTOUPDATER","1")` precedent.
3. The vendored tree is NEW (additive, no anchor replacement); Step 2's edits are anchor replacements against files Step 1 just committed, so each has a diff.
4. CEO decision 2026-08-21 (diagnostic-495 Fork 1): canonical location is **`bellows/hooks/eluvian/`**.
- Cold panel (T2, §2.6): REQUIRED — status recorded below before deposit.

## STEP 1 — DEV: vendor the enforcement layer into the repo (ADDITIVE ONLY, zero behavior change)

**Role:** DEV.

⚠️ **This step must not be able to break the live lock.** COPY, do not move. Leave every file under `~/.claude/` exactly as it is, and do NOT touch `~/.claude/settings.json` — the live hooks keep running from their current paths for the whole of this step. The point is only to get the layer under version control so Step 2's edits have a diff and a revert.

1. Create `bellows/hooks/eluvian/` and copy in, byte-identical: `wrap_check.py`, `wrap_arm_hook.py`, `wrap_stop_hook.py`, `wrap_debt_hook.py` from `/Users/marklehn/.claude/eluvian/`.
2. Create `bellows/hooks/commands/` and copy in `wrap.md` from `/Users/marklehn/.claude/commands/`.
3. Copy the `hooks` stanza of `~/.claude/settings.json` verbatim into `bellows/hooks/settings-hooks-snapshot.json` as a record of the wiring at vendor time (a snapshot, not a live config).
4. Write `bellows/hooks/README.md`: state that this tree is the CANONICAL copy as of the CEO's 2026-08-21 decision, that `~/.claude/` is the LIVE location the harness loads, that Step 2 repoints the live wiring here, and that edits must be made HERE and never directly in `~/.claude/`.
5. **Verify byte-identity** for all five copied files with `cmp` (or `shasum -a 256` on both sides, compared) and paste the raw output. A difference is a HALT, not something to reconcile by hand.

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/settings-hooks-snapshot.json`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/README.md`

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/settings-hooks-snapshot.json`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/README.md`

**Commit:** `git -C /Users/marklehn/Developer/GitHub/bellows add <the seven paths> && git -C /Users/marklehn/Developer/GitHub/bellows commit -m "..."`. Your final operation is the commit.

## STEP 2 — DEV: daemon exemption + per-session sentinel (edit the VENDORED copies, then repoint)

**Role:** DEV. Edit ONLY under `bellows/hooks/eluvian/` — never `~/.claude/eluvian/` directly. The repoint in item 5 is what makes the vendored copies live.

**(A) Daemon exemption — the marker.** At all THREE spawn sites, pass the marker scoped to the child, using `env={**os.environ, "BELLOWS_DISPATCH": "1"}` on the `Popen`/`run` call. ⚠️ **Do NOT use `os.environ.setdefault`** (the `DISABLE_AUTOUPDATER` shape): that marks the daemon's OWN environment, so an interactive `claude` launched from the daemon's shell or from `dashboard.py`'s terminal would inherit it and **silently lose the wrap lock** — a false positive reached by ordinary use. Sites: `runner.py` (the `Popen` at ~218-223), `bellows.py` (auth preflight `subprocess.run` at ~1995), `planner.py` (consultation `subprocess.run` at ~129).

**(B) Daemon exemption — the guards.** In `wrap_debt_hook.py` and `wrap_stop_hook.py`, as the FIRST action in `main()` after draining stdin: if `os.environ.get("BELLOWS_DISPATCH")` is truthy, take the existing no-op branch (`emit(None)` / `allow()`) and `hooklog` a distinct token — use `SessionStart` → `daemon-exempt` and `Stop` → `daemon-exempt` so the canary can grep for them. Do NOT add a guard to `wrap_arm_hook.py`: a daemon prompt never matches the arm trigger, and adding one there would be an untested change with no failure it prevents — say so in a comment.

**(C) Per-session sentinel.** All three hooks already read stdin and discard it; parse it instead and take `session_id`.
- `wrap_arm_hook.py`: on a trigger match, touch `ROOT / f".wrap-in-progress-{session_id}"`.
- `wrap_stop_hook.py`: consider ONLY its own `.wrap-in-progress-{session_id}` when deciding whether it is armed, and on a passing check unlink ONLY that file. ⚠️ It must become structurally impossible for one session's Stop hook to clear another's sentinel — this is the defect that disarmed the CEO's wrap.
- ⚠️ **Backward compatibility — MIGRATE-ON-ENCOUNTER, and do not substitute a different rule.** A pre-existing BARE `.wrap-in-progress` must not be silently ignored (that would drop a real in-flight wrap) and must not be left unowned (that would make it unclearable). The rule is: **the first hook to encounter a bare sentinel RENAMES it to `.wrap-in-progress-{session_id}`, claiming it for that session**, which then owns it and can clear it normally. ⚠️ Do NOT implement the intuitive alternative — "a bare sentinel arms whoever finds it and may be cleared by whoever passes" — because that is EXACTLY the shared-ownership defect this plan exists to remove, preserved under a compatibility label. Cover the migration in tests, including that the bare file no longer exists afterward.
- ⚠️ **Missing `session_id`:** if stdin is unparseable or carries no `session_id`, fall back to the bare-sentinel behavior. Do NOT invent an id — a random or pid-derived id would make the sentinel unclearable by the next turn.

**(D) Other-session awareness — the anti-hijack message.** When a Stop hook blocks, have it detect OTHER `.wrap-in-progress-*` files and append to the block reason, naming them: that another session is also wrapping, that some or all listed items may belong to it, and — explicitly — **do NOT commit, push, add, or otherwise resolve work you did not do; wait for that session to finish.** ⚠️ This message is the only thing standing between a blocked session and the exec-493 behavior; it must instruct WAITING, never resolution. Keep `wrap_check.py`'s own checks unchanged — per the Context bound, the push checks cannot be scoped per session, and pretending otherwise in code is the failure this clause exists to prevent.

**(E) Testable sentinel root.** Let the sentinel directory come from `os.environ.get("ELUVIAN_WRAP_ROOT")`, defaulting to the current hard-coded governance root, so tests and the canary can arm a scratch sentinel instead of the CEO's real one. Apply consistently in all three hooks. ⚠️ Set it ONLY in tests and in the canary — never in `runner.py`, `bellows.py`, or `planner.py`. It travels by inheritance exactly as `BELLOWS_DISPATCH` does, so a spawn-side setting would silently redirect every hook's sentinel lookup to the wrong directory and quietly disarm the real lock.

**(F) Repoint the live wiring — the FINAL action of this step, after A–E are written AND (G)'s targeted tests are GREEN.** ⚠️ Ordering is load-bearing, not cosmetic: (F) points the CEO's live lock at the new code, so doing it before the tests pass would leave the enforcement layer running unproven code if this step then halts — and with `pause_for_verdict: always` it halts pending a verdict, so that window is not momentary. Write A–E, run (G), and only then repoint. If (G) is not green, STOP with the repoint NOT done; the live layer stays on the originals and nothing is lost. Update the three hook `command` paths in `~/.claude/settings.json` to the `bellows/hooks/eluvian/` copies. ⚠️ **`~/.claude/settings.json` is an OUT-OF-REPO mutation** — it is the one file this plan changes that no gate can see (it cannot appear in Scope or Deposits because it is not in any repository), and it is the single riskiest edit here. Treat it accordingly: back it up first (below), change ONLY the three `command` strings, and re-read the file afterwards to confirm it still parses as JSON (`python3 -m json.tool`) — a malformed settings file disables every hook silently. ⚠️ **Hook wiring loads at SESSION START**, so this repoint does not affect any session already running; it takes effect for each new session (including every subsequent `claude -p`). Do not interpret "the CEO's current session still uses the old paths" as the repoint having failed. ⚠️ Back the file up first to `bellows/hooks/settings-backup-2026-08-21.json` and deposit that backup. Do not delete anything under `~/.claude/eluvian/` in this step — leaving the originals in place costs nothing and preserves a manual revert; a later plan removes them once this has proven itself in use.

**(G) Targeted tests — run BEFORE (F).** ⚠️ First, syntax-check every daemon module you edited: `python3 -m py_compile runner.py bellows.py planner.py`, and paste the raw result. The live daemon is executing THIS PLAN through `runner.py`; it holds the already-imported modules in memory so your edit cannot break the run in flight, but a syntax error would make the NEXT dispatch — Step 3, your own QA — fail to spawn at all, which presents as an unexplained step failure rather than as your bug. Then the targeted tests (the full suite runs in QA): create `bellows/tests/test_wrap_hooks.py` covering — exemption on/off for both hooks; per-session arm/stop round-trip; **one session's Stop hook cannot clear another's sentinel**; bare-sentinel backward compatibility; missing-`session_id` fallback; and the other-session message appearing when a foreign sentinel exists. Use `ELUVIAN_WRAP_ROOT` (item E) so no test touches the real root.

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/runner.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/planner.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/settings-backup-2026-08-21.json`

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/runner.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/planner.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/settings-backup-2026-08-21.json`

**Commit:** repo-asserting absolute form, explicit pathspec, add before commit. Your final operation is the commit.

## STEP 3 — QA: full suite + the live exemption canary

**Role:** QA.

**MANDATORY Rule 20 self-check banner** — the deposited QA report MUST contain, verbatim, the heading `## Rule 20 — QA Self-Check Results` and, below it, `**PASSED — SELF-CHECK PASSED**`. Canonical block: `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. `plan_slug: wrap-hook-exemption-and-session-sentinel-2026-08-21`; `qa_report_path: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/wrap-hook-exemption-qa-2026-08-21.md`; `evidence_dir: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/`; `required_evidence_files: [pytest_full.txt, canary.txt]`. FAILED → halt.

1. **Full suite**, foreground, output captured raw to `pytest_full.txt`. Report the counts line verbatim. Any regression versus the pre-change baseline is a HALT.
2. **Live exemption canary** — a mocked env cannot prove this. Capture raw output to `canary.txt`. Both assertions must hold:
   - **(i) daemon exempt:** invoke a `claude -p` with `BELLOWS_DISPATCH=1` set exactly as `runner.py` now sets it, and assert `~/.claude/eluvian/hooks.log` gains `SessionStart` → `daemon-exempt` and `Stop` → `daemon-exempt` for that session.
   - **(ii) interactive lock INTACT:** with `ELUVIAN_WRAP_ROOT` pointed at a scratch dir and NO `BELLOWS_DISPATCH`, arm a scratch sentinel and assert the Stop hook still returns `decision: block` and still logs `armed-BLOCK`. ⚠️ Use the scratch root — never arm the real governance-root sentinel.
   - ⚠️ **A FAILING canary looks like:** either token absent, OR (ii) allowing instead of blocking. Assertion (ii) failing means the CEO's lock is DISABLED — that is a HALT and must never be read as "the exemption works". State the pass/fail of each assertion separately; a single combined verdict is not acceptable.
3. Confirm `~/.claude/settings.json` now points at the vendored copies and that the backup file exists and is byte-identical to the pre-edit original (`cmp`, raw output).

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/wrap-hook-exemption-qa-2026-08-21.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/canary.txt`

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/wrap-hook-exemption-qa-2026-08-21.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-hook-exemption-2026-08-21/canary.txt`

**Commit:** repo-asserting absolute form, explicit pathspec. Your final operation is the commit.
