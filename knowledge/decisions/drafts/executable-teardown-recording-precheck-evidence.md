# bellows — executable: teardown failure recording + dirty-tree precheck + Gap-1c retry + per-plan evidence names — the 521-diagnostic build

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

**Depends on:** `knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md` (diagnostic-521's deposit — the requirements source; its Rule 27 gap table G1-G11 is this plan's change set). **CEO rulings 2026-08-25 (this session, "run the executables with the recommended options"):** Fork 1 = option (b) per-plan evidence dirs (the PLANNER_TEMPLATE Rule 18 convention); Fork 2 = option (a) park-path teardown failure routes to halted-; Fork 3 = REINSTATE Gap-1c for dirty-tree-only failures (the diagnostic stated no explicit recommendation; the Planner chose reinstatement from its favorable analysis and flags that choice here); Fork 4 = YES explicit `--override-gate worktree_teardown` refusal.

## Why this exists

520's teardown merge failure was recorded in exactly one channel; the two channels a Planner reads first (terminal log, gate_events) were structurally silent, and the dirty-tree guard that would have caught the cause was removed by the 2026-06-05 merge-model rewrite. This plan makes every teardown failure loud (log + DB row + passed-flip at all four catch sites), restores the precheck under merge semantics, reinstates the one-verdict recovery for the recoverable class, hardens the override path, and eats its own dogfood on evidence names.

## What this plan does NOT do

- **It does not restart the daemon.** Every bellows.py/lifecycle.py change is INERT until the next deliberate restart (the E2/E4 activation pattern). ⚠️ The daemon executing THIS plan runs the old code; a restart mid-plan would kill the run.
- **It does not widen what an override can do.** The opposite: `worktree_teardown` becomes explicitly un-overridable.
- **It does not migrate historical evidence files.** `knowledge/research/pytest_full.txt` and its history stay; only NEW plans (this one first) use per-plan paths.

## Numbers discipline

⚠️ **Measured 2026-08-25 by the Planner against bellows main post-522-close; line numbers WILL SHIFT as you edit — every cite below pairs the line with an anchor string; re-locate by the ANCHOR, assert count==1 before editing.**

| id | pin | value | anchor |
|---|---|---|---|
| X1 | while-loop pause catch | bellows.py:1114-1116 | ⚠️ the bare literal `except WorktreeTeardownError as e:` occurs 3× and `_pause_reason = "gate_failure"` 4× (S4-2) — locate by the COMPOUND: the catch line whose NEXT line is `_pause_reason = "gate_failure"`, of which there are exactly two; X1 is the earlier (while-loop) one |
| X2 | final-step pause catch | bellows.py:1241-1243 | the later of the two compound matches |
| X3 | auto-close catch | bellows.py:1272-1277 | `worktree teardown failed on auto-close` — has `_log("ERROR")` + passed-flip, lacks the DB row |
| X4 | park catch | bellows.py:766-768 | `worktree teardown during park` — WARN + swallow; the park rename to `parked-` follows at :770-773 |
| X5 | precheck insertion point | bellows.py:1938-1942 | between the index.lock cleanup block and the comment `# (c) Merge worktree branch onto main`; the early no-op return for in-place execution (`wt_path == project_path`) is far above at :1862 — the precheck must sit AFTER it |
| X6 | record_gate_events | lifecycle.py:470; failure-insert INSERT shape at :488-492 | `def record_gate_events(step_id, gate_result, db_path=None)` |
| X7 | E4 short-circuit | bellows.py:2533-2537 | `if any(f.get("gate") == "worktree_teardown" for f in failures):` |
| X8 | Gap-1b guard | bellows.py:2699-2713 | `continue verdict REJECTED — prior step's worktree_teardown failure uncleared` |
| X9 | the removed Gap-1c pattern | commit 2153fc15 | `git show 2153fc15 -- bellows.py` — `_retry_recoverable_teardown`, keyed on `worktree_teardown_dirty_tree` in evidence |
| X10 | the removed precheck | commit 6252f8c7 | `git show 6252f8c7 -- bellows.py` — the porcelain check + evidence format (CEO-approved message design) |
| X11 | suite floor | **1363 collected** | `python3 -m pytest tests/ --collect-only -q` from repo root; re-derive |
| X12 | override tool arm | tools/clear_plan.py `--override-gate PLAN_ID STEP GATE` | its handler is where the refusal lands |

## MUST-PRESERVE

- ⚠️ **NO daemon restart, no touching the daemon's runtime state, no writes to lifecycle.db outside the test suite's own temp DBs.**
- ⚠️ **The park path's not-parking guard (baseline-diff backup guard directly above X4) is untouched** — only the exception arm changes.
- ⚠️ **The precheck runs against `project_path` (the LIVE main checkout), never `wt_path`,** and only after the in-place early return — an in-place execution must never precheck itself.
- ⚠️ **Anchor-based editing:** every edit site re-located by its X-pin anchor with `grep -c` == 1 asserted first (⚠️ exception X1/X2: their pin rows define a COMPOUND two-match rule with earlier/later disambiguation — assert exactly 2 compound matches there). Line numbers are hints only.
- ⚠️ **Blast-radius sweep is mandatory in DEV (A9):** the teardown failure dict and `gate_result["passed"]` flip have consumers — enumerate every test touching `worktree_teardown`/`_teardown_worktree`/teardown fixtures and force-classify each as updated / unaffected / broken-by-design BEFORE running the targeted suite. The 513 lesson: a contract change's blast radius is its consumers.
- ⚠️ **`grep` is ugrep: `-F` for literals. EVERY DATE IS A FIXED LITERAL.**
- ⚠️ **Worktree dispatch; deposit paths project-relative in your worktree.**

## STEP 1 — DEV: land the recording, the precheck, the retry, the refusal

**Role:** DEV.

**A1 — `lifecycle.record_single_gate_event`.** New function in lifecycle.py beside `record_gate_events` (X6): `record_single_gate_event(step_id, gate_name, result, reason_code, db_path=None)` — a single INSERT mirroring the failure-insert shape at X6's :488-492 exactly (`overridden=0, override_ref=NULL`), no-op when `step_id is None`, same try/except discipline as its sibling.

**A2 — while-loop pause catch (X1).** Inside the except block, add in order: `_log("ERROR", f"❌ worktree teardown failed: {e}", slug=slug_for(plan_name))`; `gate_result["passed"] = False`; `lifecycle.record_single_gate_event(_lc_step_id, "worktree_teardown", "fail", str(e))`. Keep the existing `_pause_reason` set and failure append.

**A3 — final-step pause catch (X2).** Identical three additions.

**A4 — auto-close catch (X3).** Add only the `record_single_gate_event` call (log + flip already present).

**A5 — park catch (X4), Fork 2(a).** Replace the WARN+swallow: inside the existing broad catch (`except (WorktreeTeardownError, Exception)` — keep it verbatim, S2-7), `_log("ERROR", f"❌ worktree teardown failed during park — routing to halted-: {e}", ...)`; rename `inprogress_path` → `halted-{base_filename}` (not `parked-`); `record_run(..., "Halted", ...)`; **mirror the existing halted routes' bookkeeping (S2-3 + S3-6 + S4-5, the ~:2717-2719 shape, ALL SIX items): `lifecycle.mark_plan_state(plan_id, "halted", closed_at=..., plan_doc_ref=...)` + `_retire_receipts(plan_id)` + `_seen.discard(...)` + `_cleanup_verdicts_for_slug(...)` + `_delete_shadow(...)` (every existing halted/terminal route performs all of these — measured at :2711-2714/:2745-2748/:2775-2778/:1298-1303) + config-gated `notifier.notify_plan_halted(...)` (NOT a raw push)** — without the state write the plans row sits `in_progress` forever because restart recovery's worktree discriminator sees the still-alive worktree and skips; `return True` without `record_park`. The success path and the not-parking guard are untouched. Rationale in a code comment (⚠️ corrected by panel S1-4 — the naive rationale is FALSE: resume's Gap-2a stranded-cleanup at ~:1425-1458 preserves un-landed commits on `bellows-preserved/*` before the `-D` at :1477, and the teardown-site delete is safe `-d`): the halted- route is chosen because a teardown-failed park leaves the failure invisible (no verdict request, no gate row) and the parked plan's auto-resume would re-enter the same failed teardown; halting surfaces the failure for R2 immediately, with the worktree branch intact.

**A6 — dirty-tree precheck (X5), restoring X10 under merge semantics — INTERSECTION-BASED (S1-1/S1-5).** ⚠️ The day-one precheck (6252f8c7) was FILTERLESS and its production successor added `_LIFECYCLE_IGNORE_RE` (see `git show 46505bcc~1:bellows.py` :42-58) because the live main tree is dirty with daemon lifecycle artifacts during essentially every run — measured at authoring: 12 porcelain lines, all claim-renames/receipts/Done-moves/processed-verdicts. Do NOT resurrect the filterless form, and do NOT resurrect the curated RE either (curated lists rot — the drift-proof lesson). Ship the intersection form: after the index.lock block, before the merge, and ONLY when `commit_shas` is non-empty (the enumeration already sits above the insertion point — a commit-less teardown has nothing a dirty tree can block): compute the branch's changed files (`git -c core.quotepath=false diff --name-only {main_branch}...{branch_name}`, three-dot merge-base form, cwd=project_path — ⚠️ the quotepath override on BOTH commands, S3-1: without it non-ASCII paths are C-quoted on the diff side only and escape the intersection) and the dirty paths (`git -c core.quotepath=false status --porcelain -z -uall`, cwd=project_path — ⚠️ panel-measured traps, S2-1/S2-2: WITHOUT `-uall` an untracked directory collapses to `?? newdir/` and a branch-added file inside it escapes the intersection while the merge still refuses — the 520-recurrence arm, and Fork 1(b)'s per-plan evidence DIRS are exactly this shape; parse `-z` NUL-separated to survive spaced/quoted paths; ⚠️ the `-z` rename RECORD structure (S3-2, measured): `XY new\0old\0` — the new path rides the status-prefixed token and the OLD path follows as its own unprefixed NUL token; a naive strip-3-chars parse corrupts every old path — include BOTH sides in the dirty set); intersect as exact paths PLUS directory-prefix containment (a dirty entry that is a parent directory of a branch-changed file intersects). Raise `WorktreeTeardownError` ONLY when the intersection is non-empty, with evidence starting with the literal `worktree_teardown_dirty_tree:` and listing exactly the INTERSECTING files (≤10), plus the inline recovery commands — ⚠️ STASH-FIRST (S3-3, measured): under the intersection form every trip is on a genuinely conflicting file, and a commit-the-dirty-copy recovery guarantees the Gap-1c retry then fails on content conflict; the message's primary arm is `cd {project_path}` + `git stash push -- <those files>`, then re-issue the continue verdict (the stash is recoverable afterward); committing the dirty copy is the SECONDARY arm, only when the operator wants that content to win (and then the retry will conflict and R2 applies). ⚠️ rc discipline (S2-5): if EITHER precheck subprocess errors (non-zero rc or exception), raise `WorktreeTeardownError` naming the failed command — fail-closed like the neighboring commit-enumeration block, never silently skip the precheck. Lifecycle dirt that a plan does not touch never intersects and never blocks; dirt on a file the plan DOES ship is exactly the 520 case and blocks with the precise filename. Reuse X10's CEO-approved message design for the format, swapping cherry-pick wording for merge wording.

**A7 — Gap-1c reinstatement (X9), dirty-tree-only.** Restore `_retry_recoverable_teardown` per X9's pattern (`git show 2153fc15`), adapted — ⚠️ the signature changed since 2153fc15 (panel S1-6): today's `_teardown_worktree` RETURNS the landed commit SHAs, which the old code discarded. Placement + policy PINNED (S2-4): the retry runs INSIDE the continue branch, immediately BEFORE the Gap-1b guard (X8) and AFTER the E4 recheck has already accepted the verdict — and it runs ONLY when `worktree_teardown` failures are the SOLE failure class in the request (a mixed-failure continue does NOT retry; it takes the existing E4/Gap-1b paths untouched — retrying there would land commits and then be refused, halting a plan whose commits are landed). If every such failure's evidence contains `worktree_teardown_dirty_tree`, re-attempt `_teardown_worktree`; on success CAPTURE the returned SHAs and record them via `lifecycle.record_commits(lifecycle.get_step_id(plan_id, step_number), ...)` (the helper EXISTS at lifecycle.py:756 — S2-9; do not add a new one), remove those failures from the working failure list, and `_log("EVENT", "recoverable teardown re-attempt succeeded — commits landed")`; on failure leave the list untouched for X8 to reject. A content-conflict failure (no `worktree_teardown_dirty_tree` marker) must NEVER retry. ⚠️ Three consume-site derivations you must take from X9's original (`git show 2153fc15`), not invent (S3-5): the project/worktree path derivation at the consume site, the worktree-gone `isdir` skip guard (a vanished worktree means nothing to retry), and `record_commits`' repo argument (`os.path.basename(project_path)`). ⚠️ Stated residual (S3-7, accepted): the retry-success path cannot run `_apply_ledger_updates` (the step's `parsed` dict no longer exists at consume time) — recovered steps lose their FORWARD.md ledger rows; note this in a code comment, do not fake the rows.

**A8 — override refusal (X12), Fork 4.** In clear_plan.py's `override_gate()`: if the gate argument is `worktree_teardown`, print `worktree_teardown failures cannot be overridden — commits are not landed; stash the dirty files on main (git stash push -- <files>), then re-issue continue` and exit 1 — ⚠️ placed at the TOP of the function, ahead of BOTH arms (S2-6): the DB arm AND the verdict-request-file annotation arm (~:177-217) — "before any DB write" alone leaves the file arm reachable.

**A9 — consumer sweep + comment.** Add the cross-reference comment at X7 (the short-circuit implicitly excludes `worktree_teardown` from the override path; see Gap-1b at X8 and the A8 tool refusal). Then the blast-radius sweep per MUST-PRESERVE: `grep -rn -F "worktree_teardown" tests/` and `grep -rn -F "_teardown_worktree" tests/`, force-classify every hit, update tests whose fixtures now see the new log/row/flip behavior.

**A10 — tests** (new file `tests/test_teardown_recording.py` — ⚠️ this exact path is a pinned Deposit; deposit_exists and rule_22 both fail on any other name, S4-1):
1. pause-path failure logs ERROR (both sites — parametrize)
2. pause-path failure writes the `worktree_teardown` gate_events fail row (temp DB)
3. pause-path failure flips `gate_result["passed"]` to False in the posted verdict request
4. park-path failure routes to halted- (file renamed `halted-`, no `parked-`, no record_park row; plans row marked halted) — ⚠️ fixture needs a `BELLOWS_ROOT`/`_retire_receipts` monkeypatch (S3-4): `_retire_receipts` hardcodes `BELLOWS_ROOT/lifecycle.db` + the tracked `receipts/`, and the conftest autouse LIFECYCLE_DB_PATH redirect does NOT cover it
5. dirty file INTERSECTING the branch's changed files → precheck raises with `worktree_teardown_dirty_tree` BEFORE any merge attempt (assert no merge subprocess ran), evidence names the intersecting file
5b. dirty NON-intersecting file (lifecycle-artifact stand-in) → precheck passes, merge proceeds (the S1-1 arm — the every-teardown-blocks regression guard)
5c. commit-less teardown with a dirty tree → precheck skipped entirely, no raise (the S1-5 park arm)
6. clean live tree → merge proceeds, commits land
7. precheck evidence contains the recovery commands and the intersecting filenames — asserting specifically that `git stash push` appears (S4-6: an assertion on generic "recovery commands" is satisfied by the old add+commit-first wording S3-3 measured to guarantee a failed retry)
8. Gap-1c: dirty-tree-marked failure retries and clears on success (SHAs recorded via get_step_id); content-conflict failure does NOT retry; mixed-failure continue does NOT retry (fixture shapes: resurrect from `git show 2153fc15 -- tests/` — ⚠️ the originals mock the OLD no-return signature; the SHA capture makes the mock's return value load-bearing, set it explicitly — the hot-path mock-audit class, S2-8)
8b. precheck intersection arms: untracked-directory collapse (branch adds a file inside a new dir; porcelain must be run `-uall`) → raises naming the file; spaced-path and rename-entry dirt → both sides intersected (S2-1/S2-2 measured cases)
9. `clear_plan.py --override-gate <x> <y> worktree_teardown --ref <dummy>` exits 1 with the refusal text, no DB write (⚠️ `--ref` is REQUIRED with `--override-gate` — omitting it exits 2 at argparse before the refusal is reachable, S1-3)
10. `record_single_gate_event` inserts exactly one row; no-op on None step_id

Targeted DEV run: the new test file + every module the A9 sweep classified as updated. NOT the full suite (QA owns it).

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_teardown_recording.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/lifecycle.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/`

**Commit:** `git add -A lifecycle.py bellows.py tools/clear_plan.py tests/ && git commit -m "[<id>] teardown: record failures at all four catch sites, restore dirty-tree precheck, reinstate Gap-1c retry, refuse teardown overrides"` in YOUR worktree cwd.

## STEP 2 — QA: full suite + evidence, per-plan names

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd**; deposit RAW output as `knowledge/qa/evidence/teardown-recording-precheck/pytest_full.txt` — ⚠️ **this plan is the first to RETURN to the per-plan evidence convention (Fork 1(b), PLANNER_TEMPLATE Rule 18); the path above is the exact deposit, directory included.** Self-contained accounting: total collected, the new test file's own count (`--collect-only -q` on it), difference = inherited baseline vs X11's 1363; zero failures.

**Q2 — change-shape check.** `git diff HEAD~1 --stat` plus targeted greps proving the exact post-change counts (⚠️ derived from pre-existing occurrences — re-verify each expectation against the diff, yours supersede): the new ERROR literal `❌ worktree teardown failed:` count==2 (X1+X2; X3's pre-existing text says `failed on auto-close` and A5's says `during park` — neither matches); `gate_result["passed"] = False` count==5 (3 pre-existing at :1072/:1202/X3 + 2 new — the walk-1 fold's count of 3 was itself wrong, corrected by panel S1-2); `record_single_gate_event(` call sites in bellows.py count==3 (X1, X2, X3 — A5 records none: no step is running at park); the precheck sits between the lock cleanup and the merge comment; the A8 refusal sits at the TOP of `override_gate()`, ahead of BOTH arms — the DB arm and the request-file arm (S4-3); the A5 arm contains `halted-` and no `record_park` call. ⚠️ All Q2 greps run against `bellows.py` (and clear_plan.py where named) — NEVER repo-wide: the committed plan file self-quotes the literals and inflates repo-wide counts (S4-4).

**Q3 — consumer-sweep verification.** Re-run A9's greps; assert every hit is in a module the DEV report classified; no unclassified consumer.

**Q4 — QA report.** `knowledge/qa/evidence/teardown-recording-precheck/qa-report.md` with Q1-Q3 results and the gap-table coverage row per G1-G11 — ⚠️ under the approved forks ALL eleven rows are in this plan's scope (S1-8): G1-G9 implemented here, G10 satisfied BY this plan's own Q1 evidence path, G11 = the test file; no row is N/A.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1-Q4 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/teardown-recording-precheck/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/teardown-recording-precheck/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/teardown-recording-precheck/`

**Commit:** `git add knowledge/qa/evidence/teardown-recording-precheck/ && git commit -m "[<id>] qa: teardown recording + precheck — full suite + evidence (per-plan path)"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T2 computed — daemon-code build; full cold panel mandated at the freeze (the E-family rule: the execution seat measures what readers cannot).
**Walk register:** `governance/knowledge/research/walk-register-executable-teardown-recording.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** (yields 2 → 0, warm close) — then the **full cold panel: scout 10 (2 HIGH) → discovery 9 (1 HIGH, scratch-repo measured) → execution 7 (0 HIGH — the spec BUILT CLEAN: implementation + 10/10 tests + zero suite breakage) → capstone NOT-READY on 1 MED blocker, discharged by 6 folds + the sweep walk.** Every seat finding author-verified before folding; per-seat tables in the register.
**Cold panel: CONVENED AND CLOSED** — four seats (scout → discovery → execution → capstone), 32 findings total, capstone's NOT-READY discharged by its folds + the sweep walk; per-seat tables in the register.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 1 folded; w2 dry; panel folds landed per register
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry; sweep walk 1 coherence fold (the X1/X2 anchor-law exception)
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the lintmirror deposit path.
**Closing:** **panel closed, capstone discharged — FREEZE.** Warm series 2 → 0; panel 10 → 9 → 7 → 6(+sweep 1). The deposit travels the lane with the receipt ritual → staged `ready-` → class shop-infra HOLD → release via `clear_plan.py --release-class-hold` under the CEO's "run the executables" directive of 2026-08-25 → claim. Pre-dispatch obligation (S1-10/S4-7): the live porcelain committed before staging.

## Cycle Manifest
tier: T2
target: bellows.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/research/teardown-silent-block-evidence-names-2026-08-25.md, /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md
writes: bellows.py, lifecycle.py, tools/clear_plan.py, tests/test_teardown_recording.py, knowledge/qa/evidence/teardown-recording-precheck/pytest_full.txt, knowledge/qa/evidence/teardown-recording-precheck/qa-report.md
open_forks: none — the four fork rulings are recorded in the header (Fork 3's reinstatement is the Planner's flagged choice under the CEO's recommended-options directive)
walks: 2
yields: 2, 0
panel: scout 10 / discovery 9 / execution 7 / capstone 6 + sweep 1
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per the Step 2 mandate. Step 1 is DEV-only.
