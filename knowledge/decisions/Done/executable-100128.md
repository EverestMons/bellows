# bellows — THE `[3/root]` GITLINK ARM ASKS WHETHER EACH TRACKED POINTER NAMES ITS SUBMODULE'S PUBLISHED TIP (thread 417, re-draft)

**Date:** 2026-09-18 | **Project:** bellows | **Tier:** Small (one checker arm replaced by a five-outcome loop over the index and HEAD together — three FAIL, two PASS — reading each submodule's published tip; two ritual sentences; one new test file of ten named cases; a mutation manifest of at least ten mutants, with its run; one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — the checker is the wrap gate; `pytest tests/ -q`), plus the edited checker run against a scratch fixture under the harness interpreter `/usr/bin/python3`, a mutation run in which every mutant must be KILLED, and one LIVE read under the hook's stripped environment against a scratch clone of governance with ONE pointer planted off its real published tip, which a working arm must flag (T-3) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 417 | **cycle_tier:** T2

**This is a RE-DRAFT.** The first cycle for thread 417 (`executable-bellows-gitlink-arm.md`) ended in RE-DRAFT at walk 7, CEO-ruled 2026-09-18, governance `3f161920`. Its forcing finding was (d), the keying: its obligation was stated as a submodule's local HEAD, the mechanism's own vocabulary, so the check matched it and clause (d) passed against its own reflection. It judged each pointer against a LOCAL CLONE and spent 35 findings over seven walks on that clone's state — resolver, identity, URL forms, detached, unpushed, unfetched — with HIGH findings in every walk. This draft judges each pointer against the submodule's PUBLISHED tip read from its origin, and none of that machinery exists in it. Justification half: `governance/knowledge/decisions/drafts/premise-bellows-gitlink-arm-remote-2026-09-18.md` (governance `79b8713f`).

**When this goes live, and what the verdict is therefore about.** ⛔ The change lands BEFORE the verdict. This plan pauses after QA; the daemon's teardown merges onto `main` and pushes at the pause path (`bellows.py:3068`), and `~/.claude/eluvian` is a symlink to `hooks/eluvian`, so the arm is live on the mini at that merge. The verdict is about whether to KEEP it.

⛔⛔ **The failure mode is not symmetric with #100126's.** That plan removed an arm; this one ADDS a failing condition to the arm the Stop-hook lock reads during a wrap. A false stale during a wrap blocks the turn from ending until it clears. ⛔ **The escape, stated precisely:** `wrap_check` is fail-open — `main()` `:561` returns 0 on any exception — but fail-open covers a CRASH, and a false stale is a confident wrong answer that exits 1. The real escape is `git revert` of the DEV commits, which works because the lock blocks ending a turn, not running commands. The design narrows the exposure on its own terms: a FAIL requires a published tip that was READ successfully and differs from the gitlink, and anything the arm cannot read passes.

⛔ **`/eluvian` reads this arm too, and this plan does not touch it.** `eluvian.md:24` runs `wrap_check.py "" debt`, the same `check()`. Thread 409 owns whether `/eluvian` should exist; the coupling is inherited deliberately.

**Post-close:** no restart — the harness runs the hooks from this checkout, so the change is live on the mini at the merge and on the Air at its next pull.

**Not self-repair exempt.** A plan editing the wrap ritual is verified by `gates.py`, its QA step and the Planner's verdict, none of which is the wrap ritual. #100126 is the precedent.

## CEO Context

A governance pointer exists so that a machine taking governance at its published state lands on each submodule at the commit the shop actually published. On this machine the arm that is supposed to check that has never been able to: it asks whether a bump was staged and not committed, and with every submodule directory empty that question is always answered no. Two of three pointers drifted six days in September with no gate firing.

This plan makes the arm ask the obligation's own question. For each tracked gitlink — enumerated from the index and HEAD together — it reads the submodule's published tip from its origin, and fails only when that tip was read and differs. It needs no local copy of any submodule, and it reads only porcelain's STAGED column, so neither machine's layout can blind it — measured 2026-09-18, the mini's submodules are uninitialized and the Air's are INITIALIZED, all three showing ` M`, and both are judged against the published tip, and the whole class of local-clone edge cases the first draft spent seven walks on does not arise.

**What it gives up.** Each check is a network read, about 1 s per submodule, run concurrently, so about 1 s in all. It runs only at session start, during a wrap and at `/eluvian` — the Stop hook is a no-op unless a wrap is armed (`wrap_stop_hook.py:4–5`). When a tip cannot be read — offline, a host that will not answer — the arm cannot judge and PASSES, per the CEO's 3b ruling. ⛔ **And that pass is invisible:** the funnel-law advisory it prints is discarded by both hooks on a passing check (`wrap_debt_hook.py:89`, `wrap_stop_hook.py:196`). So a remote that stays unreadable would leave the arm silently passing — the original defect again. That is why QA's live read under the hook's own stripped environment is part of this plan and not an optional check: the arm's non-vacuity rests on it.

**CEO rulings, 2026-09-18 — decisions, not the author's defaults** (recorded on thread 417 as a `noted` event). ⛔ **3a, CORRECTED the same morning: the governance submodules are not initialized on the MINI; the Air's stay INITIALIZED.** On the mini, `_resolve_bellows` checks `<root>/bellows` before the sibling checkout (`wrap_check.py:70–72`), so initializing there would silently re-point the `[2/bellows]` arm at a detached copy. That reason never applied to the Air: its submodules are initialized by design and ARE its working checkouts (P12, measured during walk 3). The ruling was first recorded as "any machine", which overstated the Planner's own reason; the correction is noted on thread 417. This arm no longer depends on either layout, since it reads only porcelain's STAGED column (W3-2). ⛔ **3b: when the arm cannot judge, it PASSES rather than blocking a machine.** The first draft's trigger was a missing checkout; here it is an unreadable remote, and the principle is the same. And on thread 161 the same morning, the schema-drift check will also live as a `wrap_check` arm, so this arm's shape is the pattern that work follows.

**What it does not do.** It does not bump anything; the ritual text still instructs the bump by hand, now for every tracked gitlink rather than bellows alone, and TO THE PUBLISHED TIP the arm names rather than to a local HEAD. And it does not make the funnel-law advisories visible on a pass — that is a pre-existing limit affecting `[4/memory]` too, and is filed as its own thread, **427**.

## What this changes

1. **`hooks/eluvian/wrap_check.py`** — the `[3/root]` gitlink arm at `:256–259` is replaced by a loop over the tracked gitlinks read from the index and HEAD together, with **five outcomes: three FAIL, two PASS**. The outcomes, the helper functions and the order they run in are specified ONCE, in STEP 1 Item 2, and not restated here. The docstring's step-3 line at `:26` changes from "bellows gitlink bumped" to "every tracked submodule gitlink current".
2. **`hooks/commands/wrap.md`** — step 3's `` `git add bellows` `` (`:117`) and the mini's `update-index --cacheinfo …,bellows` sentence (`:128–129`) widened to every tracked gitlink.
3. **`tests/test_wrap_gitlink_arm.py`** (new) — the arm has ZERO coverage today (P4). Ten named cases, enumerated once, in STEP 1 Item 1.
4. **A dev-log** under `knowledge/development/`.
5. **`knowledge/mutants/gitlink-arm-remote.json`** (new) — the mutation manifest, and its run output beside it; specified in STEP 1 Item 5.

## MUST-PRESERVE

Each carries its observer; observers A–I and L are the ten named cases of STEP 1 Item 1, in order.

- ⛔ **A. A stale pointer FAILS.** A FAIL means the published tip was READ and differs from the gitlink, and its message names the recorded sha and the published sha IN FULL — the bump's target, usable directly in `update-index --cacheinfo`. *Observer A: a fixture whose submodule's published origin (a local bare repo) has moved one commit past the gitlink.*
- ⛔ **B. A current pointer PASSES.** *Observer B: the gitlink equal to the published tip — no `[3/root]` fail for it.*
- ⛔ **C. An unreadable tip PASSES and is never read as stale.** The failed read prints a funnel-law advisory and appends nothing to `fails` (3b). *Observer C: a submodule whose URL names no repository at all — a nonexistent LOCAL path, which fails rc 128 in about 14 ms with no ssh and no DNS — assert zero `[3/root]` fails for it AND the advisory line in stdout, beside a second, genuinely stale submodule that still fails, so the pass is not the whole arm going quiet.*
- ⛔ **D. Any uncommitted change to a gitlink — a staged bump, addition or removal — FAILS exactly once.** The index already carries the new sha, so the arm reports the bump and judges nothing further for that path. *Observer D: a bump staged to the CURRENT tip, a staged addition and a staged removal — and, beside them, an INITIALIZED submodule whose checkout moved with nothing staged (` M`), which must NOT be reported as uncommitted but judged against the published tip, — exactly one `[3/root]` fail for each, naming the uncommitted change, not staleness.*
- ⛔ **E. A tracked gitlink with no `.gitmodules` entry FAILS.** With no URL there is nothing to read, and a silent skip would exempt that submodule permanently. *Observer E: a gitlink added with no `.gitmodules` entry — a fail naming the path and the missing entry.*
- ⛔ **F. The enumeration is derived from the index and HEAD together, never listed.** *Observer F: a submodule named nothing like anvil, bellows or lessons-forge is still judged — and one whose `.gitmodules` NAME differs from its path is found by its path and judged, not failed as a missing entry.*
- ⛔ **G. The arm writes nothing.** Every call is a read. *Observer G: the fixture root's `git status --porcelain` byte-identical before and after `check()`.*
- ⛔ **H. Every submodule is judged on every run; the loop never returns early.** *Observer H: two simultaneously stale submodules — BOTH names in one run's output, asserted as a count.*
- ⛔ **I. Remote reads are bounded, concurrent and non-interactive.** Measured: an unreachable host fails only after ssh's connect timeout (3020 ms with `ConnectTimeout=3`), so three sequential reads could stall a session start by about 9 s; and an ssh that prompts — a passphrase, an unknown host key — would hang the hook indefinitely. *Observer I, in two halves because one fixture cannot prove both.* ⛔ **Concurrency:** replace the arm's tip reader in the test with one that sleeps 0.5 s, judge three submodules in one `check()`, and assert it finishes in UNDER 1.0 s — a sequential implementation takes at least 1.5 s and FAILS. (Unreadable URLs cannot prove this: measured, three unresolvable ones run SEQUENTIALLY in 45 ms, so a sequential arm would have passed the 3 s bound this observer first carried.) **Non-interactive and bounded connect:** assert the module's ssh constant contains `BatchMode=yes` and `ConnectTimeout=`.*
- ⛔ **J. `_resolve_bellows`, `BELLOWS` and the `[2/bellows]` arm are untouched.** *Observer J: `tests/test_hook_default_root.py` and `tests/test_gates_cross_machine_paths.py` pass unchanged.*
- ⛔⛔ **K. The arm is NOT vacuous where it runs.** C makes an unreadable tip pass silently, so if the tips are unreadable from inside the hook's environment the arm judges nothing, ever, and says nothing — the original defect. *Observer K: QA's live read (STEP 2 item 6) plants ONE pointer that is NOT at its real published tip — a synthetic sha, so no local checkout is involved — in a scratch clone of governance, runs the checker under `env -i` with the root passed inside it, and asserts a stale line for exactly that submodule and no advisory. ⛔ Not an absence assertion against the real root: every pointer there is current today, so a working arm and an arm that judges nothing print the same nothing — the original arm's defect, which a check for its replacement must not reproduce.*

- ⛔⛔ **L. A failure inside this arm is confined to this arm.** `main()` `:561` catches any exception from `check()` and exits 0, and the `[3/root]` region sits bare in `check()` with no guard of its own. So without one, a single bug in this arm — a parse error, a thread-pool fault — passes the ENTIRE wrap lock and skips every other arm, and the `internal error, failing open` line it prints is stdout on exit 0, which both hooks discard (P7): a silent, total bypass. The arm's body therefore runs inside its own `try`, and an exception there prints one advisory and judges no FURTHER gitlinks — fails already appended stand, and the advisory says so rather than claiming nothing was judged — while every other arm still runs. *Observer L: `check()` called on the STOP path, its default — the debt path skips 3b since #100126 (`:274`), so a debt call could never return the fail this asserts — with the tip reader replaced in the test by one that RAISES, in a fixture whose baton carries no sweep line for the session — assert that no exception escapes `check()`, that the arm's error advisory is printed, and that the `[3b/lessons]` fail, from an arm that runs AFTER this one, is still returned.*

## Numbers discipline — measured 2026-09-18 by the Planner (bellows `f704f95c`, governance `79b8713f`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the arm | `hooks/eluvian/wrap_check.py` (575 lines; sha256 `14ce7156a5d471eb071bc1373b70ae365b710eb31018c36930551726f39238a9`): `gitlink_dirty = porcelain(ROOT, "bellows")` at `:257` in the block `:256–259`; the docstring's step-3 line at `:26`; the funnel law at `:347` — advisories printed, never appended to `fails` | `sed -n 256,260p hooks/eluvian/wrap_check.py` |
| P2 | ⛔ when the arm runs | the Stop hook is a no-op unless a wrap is armed (`wrap_stop_hook.py:4–5`); the debt hook runs it at session start; `/eluvian` runs it bare. Not at every turn end | `sed -n 1,8p hooks/eluvian/wrap_stop_hook.py` |
| P3 | ⛔ the tracked set | `git ls-files -s` mode `160000` in the governance root yields exactly `anvil`, `bellows`, `lessons-forge`; `.gitmodules` records `git@github.com:EverestMons/anvil.git`, `…/bellows.git` and `…/forge_lessons.git`, and each remote's default branch is `refs/heads/main` (`git ls-remote --symref <url> HEAD`) | `git -C <root> ls-files -s; git -C <root> config -f .gitmodules --get-regexp url` |
| P4 | ⛔ the coverage hole | no test pins this arm: `/usr/bin/grep -rl` over `tests/` finds 0 files for `3/root` and 0 for `gitlink`, against positive controls `3b/lessons` 4, `2/bellows` 1, `shop_next_session` 8 | `/usr/bin/grep -rl '3/root' tests/` |
| P5 | ⛔ the live reads | `git ls-remote <url> HEAD` returned `cfd6fd92`, `f704f95c`, `a1ebf458`, each equal to its gitlink, about 1 s per call and 2954 ms for three in sequence; under `env -i HOME=… PATH=/usr/bin:/bin` with `/usr/bin/python3` 3.9.6 and no `SSH_AUTH_SOCK` it returned `cfd6fd92`, rc 0, in 1041 ms, because ssh reads `~/.ssh/id_ed25519` directly | the premise brief's measurement section |
| P6 | ⛔ the unreadable cases | with `GIT_SSH_COMMAND="ssh -o ConnectTimeout=3 -o BatchMode=yes"`: an unroutable host fails rc 128 after 3020 ms; an unresolvable name fails rc 128 after 77 ms | the timing harness, two URLs, `subprocess.run` with a 10 s backstop |
| P7 | ⛔ advisories on a pass | both hooks discard the checker's stdout on exit 0: `wrap_debt_hook.py:89` `if res.returncode == 0:` then `emit(None)`; `wrap_stop_hook.py:196` the same test, and `reason = (res.stdout …)` at `:213` is reached only on a block | `sed -n 85,95p hooks/eluvian/wrap_debt_hook.py` |
| P8 | the ritual text | `hooks/commands/wrap.md` (148 lines; sha256 `2cf37761e7ca27c3bb3033b58d1aa89df130229f5a11135279f8f02f8a09a20b`): `` `git add bellows` `` at `:117`, the mini's `cacheinfo` sentence at `:128–129` | `sed -n 115,130p hooks/commands/wrap.md` |
| P9 | the drift that motivated it | anvil's gitlink stood at `caf7efcc` against a published `cfd6fd92` and lessons-forge's at `dacccbb0` against `a1ebf458`, found by a person and bumped by hand in governance `1ab6791f` | `git -C <root> show --stat 1ab6791f` |
| P10 | class and queue | ⛔ taken at walk 0 with `tools/classify_deposit.py` against this plan's own Cycle Manifest, which exists from v0 so that it can be | `tools/classify_deposit.py <plan> --project-root /Users/marklehn/Developer/bellows` |
| P11 | the suite | the DEV measures its own baseline at A0; the newest figure in evidence is `2527 passed, 2 skipped` (#100126) | the DEV's own A0 run |
| P12 | ⛔ the Air's layout | read-only over the tailnet 2026-09-18: the Air's governance root is `~/Developer/GitHub` and all three submodules are INITIALIZED (21, 50 and 90 entries), each showing ` M` — the checkout moved, nothing staged. The mini's are uninitialized (P5 of the first cycle). An arm that short-circuits on any non-empty status judges index against worktree on the Air | `ssh marklehn@100.79.204.47 'git -C ~/Developer/GitHub status --porcelain -- anvil bellows lessons-forge'` |

## Drafting Cycle
**Tier:** **T2** — T-6 (the wrap gate the Stop-hook lock reads during a wrap, and the command file carrying the ritual), T-3 (the hooks under `/usr/bin/python3` 3.9.6, the suite under the venv's 3.12.14), T-1 (checker, command text, tests). T-2, T-4, T-5, T-7 and T-8 do not fire.
**Depth:** to walk 7 unless a fully dry walk arrives sooner (standing drafting-cycle practice, CEO 2026-09-17).
**Walk register:** `governance/knowledge/research/walk-register-bellows-gitlink-arm-remote-2026-09-18.md`
**Target class — `plan_lint` (t), decided deliberately:** `target_class` is left UNDECLARED, as #100126 left it on this same target. The detector discipline it would require is carried instead by the mutation manifest (STEP 1 Item 5), which proves mechanically that each observer can fail against a broken arm — the class W1-1 and W1-3 found by hand in walk 1.
**Walk 0 (context pin, measured):** P1–P11; the first cycle's Closing line and register as input (DRAFTING_CYCLE `:264`); the live read under a stripped environment; the unreachable-remote timings; the advisory channel's reach.
**Cold panel (T2):** not convened at v0. This draft replaces a cycle that ran seven warm walks; whether a cold seat is spent on it is decided at the close against the per-walk yield, not assumed here. The first cycle's lesson governs: a high fold-introduced share means another warm pass is the wrong instrument, and a cold seat is the one it names.
**Walk 0 direction verdict:** PROCEED — recorded with its reasoning in the register.
- Weak spots:          w1 1 folded (1.2); w2 1 folded (1.2); w3 1 folded (1.2); w4 1 folded (1.2); w5 1 folded (1.1); w6 1 folded (1.2); w7 dry
- Destruction:         w1 1 folded (2.1); w2 1 folded (2.1); w3 1 folded (2.1); w4 dry; w5 dry; w6 dry; w7 dry
- Vulnerabilities:     w1 2 folded (3.2); w2 2 folded (3.2); w3 1 folded (3.1); w4 1 folded (3.2); w5 1 folded (3.3); w6 1 folded (3.2); w7 dry
- Integration-record:  w1 1 folded (4.1); w2 1 folded (4.1); w3 1 folded (4.1); w4 dry; w5 1 folded (4.1); w6 1 folded (4.1); w7 dry
- ACID:                w1 1 folded (5.2); w2 dry; w3 dry; w4 1 folded (5.1); w5 dry; w6 1 folded (5.3); w7 dry
**Closing:** **BAR MET — walk 7 fully dry across all five lenses** (the doctrine's bar, not `cycle_check`'s instruction-class reading alone, which had read BAR_MET after walk 7's first lens). Seven walks, 25 findings (16 HIGH), 35 lens commits; per-walk yield 6, 5, 4, 3, 3, 4, 0, with HIGH findings falling 4, 3, 3, 2, 2, 2, 0 and fold-introduced findings 0, 5, 2, 2, 1, 2 — 12 of 25. ⚠️ Every figure in this line was MEASURED from the register's rows after the first close stated two of them from memory, the total as 24 and walk 6's fold-introduced count as 1; that close was never pushed, and this one supersedes it. This cycle is the RE-DRAFT of one that ended at walk 7 on forcing finding (d) — an obligation stated in the mechanism's own vocabulary — and its first act was to state the obligation with no git vocabulary at all and to measure, before writing a word of mechanism, that `git ls-remote` authenticates inside the hook's stripped environment. Two shifts carried it. When the mechanism simplified, the defects moved from the arm into its CHECKS: walk 1 found four ways the verification could not fail against the wrong code — a concurrency bound a sequential arm passed, a fixture routing every case down the wrong branch, a missing mutation backstop, and a non-vacuity proof that was itself vacuous — each folded with a measured fix and, for the proof, a planted positive control. And when walk 5's HIGH findings turned out to be execution-fidelity defects, walk 6 stopped reading the plan and RAN it: executing the fixture recipe as written found two HIGH findings five reading walks had missed (an uncommitted baseline reading as a staged addition, and a reused fixture whose ROOT is not a repository), and walk 7 rehearsed the whole recipe in one root and routed every case to its intended outcome. The Air was read over the tailnet and found INITIALIZED, which reshaped the short-circuit to porcelain's staged column and led the CEO to correct 3a to the mini only. Conformance at the close: `plan_lint` 7 PASS, 0 FAIL, 18 WARN, each read and dispositioned; `lens_order_check` OK over 35 lens commits; the register SHAPE-OK and COVERED; `propagation_check` 15 divergences, all read — 10 consistent restatements of a pinned value and 5 collisions of a plan id with a pin's source note, none a propagation miss. **Cold panel:** not convened — walk 1 found nothing fold-introduced, the late walks' findings came from execution rather than re-reading, and walk 7 is dry by rehearsal as well as by lens. Deposits to the bellows lane; the class is `shop-infra`, MATCH, so it HOLDS at admission and its release is the CEO's.

## Cycle Manifest
tier: T2
target: hooks/eluvian/wrap_check.py
class: shop-infra
reads: hooks/eluvian/wrap_check.py, hooks/eluvian/wrap_stop_hook.py, hooks/eluvian/wrap_debt_hook.py, hooks/commands/wrap.md, tests/test_wrap_3b_keyed.py, tests/test_hook_default_root.py, tests/test_gates_cross_machine_paths.py
writes: hooks/eluvian/wrap_check.py, hooks/commands/wrap.md, tests/test_wrap_gitlink_arm.py, knowledge/development/dev-log-gitlink-arm-remote-2026-09-18.md, knowledge/qa/evidence/gitlink-arm-remote-qa-receipt-2026-09-18.md, knowledge/qa/evidence/gitlink-arm-remote-suite-2026-09-18.txt, knowledge/qa/evidence/gitlink-arm-remote-nodes-2026-09-18.txt, knowledge/qa/evidence/gitlink-arm-remote-live-read-2026-09-18.txt, knowledge/mutants/gitlink-arm-remote.json, knowledge/mutants/gitlink-arm-remote.run.txt
mutants: knowledge/mutants/gitlink-arm-remote.json
open_forks: 1. the funnel-law advisories are discarded by both hooks on a passing check, so every advisory — this arm's and `[4/memory]`'s — is invisible unless something else fails; a pre-existing limit, filed as thread 427, which leaves to the CEO whether a passing check should surface them
walks: 7
yields: N/A
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:15
coherence: 7/7 body walks named in the register (25 register rows; walk-token match, NOT row coverage)

## STEP 1 — DEV (the tests first and red, then the checker, then the ritual text; two commits)

⛔ **ESTABLISH THE ROOT FIRST — a dispatched step inherits no shell.** Begin the step with:

```bash
cd "$(git rev-parse --show-toplevel)"
test -f status.py -a -d hooks/eluvian && echo TREE_OK: "$PWD" || { echo 'TREE_WRONG — not the bellows checkout'; exit 1; }
```

and paste the `TREE_OK` line. `status.py` is the marker `_resolve_bellows` uses to tell bellows from the governance root, and the two are siblings on this machine.

**A0 — measure before touching anything (paste raw output):** the full suite via the venv (`pytest tests/ -q`), stating the baseline pass/skip/fail counts as YOUR OWN measurement; `git rev-parse HEAD`; `shasum -a 256 hooks/eluvian/wrap_check.py hooks/commands/wrap.md`, confirming both match P1 and P8 — ⛔ a mismatch means the file moved since the plan was pinned: HALT and say so rather than re-pinning.

⛔ **BEFORE EACH OF THIS STEP'S TWO COMMITS, run the DEV-side pre-check and paste its output.** `hooks/git/pre-commit` runs `check_deposit.py --verify-commit` against that record, so a commit with no fresh passing pre-check covering every staged path is REFUSED. The plan argument is THIS plan's lane file — `/Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md`, with your own id — never the governance draft. ⛔ And each pre-check names, with `--expect-missing`, the declared deposits that commit does NOT write yet: rule 22(a) fails on an absent declared deposit and skips exactly the paths listed (the tool's own help), so without it BOTH commits are refused. Matching #100126's form:

- **the red commit** (the test file alone — the dev-log, the manifest and the run are all still absent): `.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-gitlink-arm-remote-2026-09-18.md knowledge/mutants/gitlink-arm-remote.json knowledge/mutants/gitlink-arm-remote.run.txt`
- **the green commit** (checker, ritual text, dev-log and manifest — only the run is still absent, since it is written after this commit): `.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/mutants/gitlink-arm-remote.run.txt`

The Cycle Manifest's `writes:` names every path this step stages.

**Item 1 — the test file, RED.** Create `tests/test_wrap_gitlink_arm.py`. Point every `ELUVIAN_*` path into `tmp_path` exactly as `tests/test_wrap_3b_keyed.py`'s autouse fixture `wc_env` does (`:37–59`) — read it and reuse its shape, or the tests read the real shop. ⛔ **`git init` the fixture ROOT — `wc_env` makes a plain directory, not a repository.** `wrap_check`'s `git()` helper returns `''` on any failure and never checks the exit code — measured: `ls-files -s` in a non-repo exits 128 with empty stdout — so against wc_env's ROOT the arm enumerates NOTHING, and cases B, C and G pass having judged nothing, as does case 9's concurrency half, since zero reads finish in under a second however they are scheduled. ⛔ So every case asserts FIRST that `_tracked_gitlinks(ROOT)` returns exactly the gitlinks it placed — a positive control on the fixture itself, which fails loudly where the fixture is wrong instead of letting the case pass on an empty enumeration. (wc_env's own `root/bellows` directory coexists with a gitlink at that path — measured, porcelain clean — so it needs no special handling.) ⛔ **The fixtures never touch the network.** Each submodule's "published" origin is a LOCAL BARE REPO under `tmp_path`, and the fixture's `.gitmodules` records that repo's PATH as its URL — `git ls-remote <path> HEAD` reads it with no network at all. A gitlink is placed in the fixture root's index with `git update-index --add --cacheinfo 160000,<sha>,<path>` and needs no checkout of the submodule — ⛔ but an EMPTY DIRECTORY must be created at `<path>`, as on the mini. Measured: without one, porcelain reports ` D <path>` for an UNCHANGED committed gitlink, so every submodule reads as an uncommitted change and none ever reaches the published-tip comparison. ⛔ And COMMIT the gitlinks and `.gitmodules` as the fixture's BASELINE. Measured by executing this recipe as written: an uncommitted gitlink reads `A  <path>`, a staged ADDITION, so the arm reports an uncommitted change and never reads the published tip — the same wrong branch as the missing directory, by a second route. Only case 4 stages anything, and it stages on top of that committed baseline. ⛔ Give those commits a HERMETIC identity — `git -c user.name=test -c user.email=t@t commit …`, or `git config` inside the fixture root — as 19 of the 20 bellows test files that commit already do. The machine's global identity is not guaranteed wherever the suite runs, and this machine's would mask the omission. ⛔ Where a case builds an INITIALIZED submodule with `git submodule add` from a local path (cases 4 and 6), pass `-c protocol.file.allow=always` ON THAT COMMAND. Since git 2.38.1 the file transport is restricted for submodule clones — measured on git 2.55.0: exit 128, `fatal: transport 'file' not allowed`, and exit 0 with the flag. ⛔ NEVER set it globally (`git config --global …`), which weakens that restriction, a CVE mitigation, for the whole machine. The arm's own `ls-remote` against a local path needs no flag — measured, exit 0 — so this is a fixture concern only. ⛔ And every case asserts the specific MESSAGE — stale, uncommitted, missing entry or advisory — never merely that a fail exists; otherwise a fixture artifact like that one passes A, D and E for the wrong reason. ⛔ **Ten named cases, one per MUST-PRESERVE observer A–I and L, in order:**

1. `test_stale_pointer_fails` — A, asserting the message carries the FULL 40-character published sha. Its docstring records the drift that motivated the plan (anvil `caf7efcc` against a published `cfd6fd92`) as provenance only: a git sha is content-derived, so the fixture's commits carry their own.
2. `test_current_pointer_passes` — B.
3. `test_unreadable_remote_passes_with_advisory` — C: a nonexistent LOCAL path as the URL (rc 128 in about 14 ms, no ssh, no DNS) beside a genuinely stale submodule; zero fails for the first, the advisory in stdout, one fail for the second.
4. `test_uncommitted_change_reports_once` — D, including an initialized submodule (added with `git submodule add` from a local source repo) whose checkout is moved with nothing staged, asserted NOT reported as uncommitted: a bump staged to the current tip, a staged addition and a staged removal, one fail each, each naming the uncommitted change.
5. `test_missing_gitmodules_entry_fails` — E.
6. `test_enumeration_is_derived_not_listed` — F, including a submodule added with `git submodule add --name <other> ...` so its name differs from its path, asserted judged and NOT reported as a missing entry.
7. `test_arm_writes_nothing` — G.
8. `test_two_stale_submodules_both_named` — H.
9. `test_remote_reads_are_bounded_and_batch` — I, in its two halves: the tip reader replaced by one sleeping 0.5 s, three submodules judged in one `check()` in under 1.0 s (sequential would take 1.5 s); and the ssh constant containing `BatchMode=yes` and `ConnectTimeout=`.
10. `test_arm_failure_is_confined_to_the_arm` — L, on the STOP path (debt skips 3b, `:274`): the tip reader raises; no exception escapes `check()`, the arm's error advisory is printed, and the `[3b/lessons]` fail from a later arm is still returned.

Run the file and paste the raw red output. ⛔ **State the red count and confirm each fails for the RIGHT reason** — a test that errors on a missing helper is broken, not red. Commit the test file alone.

**Item 2 — the checker, GREEN.** In `hooks/eluvian/wrap_check.py`, ⛔ keeping it runnable under Python 3.9 (T-3): no runtime `X | Y` unions — `from __future__ import annotations` defers annotations only.
(a) A module constant for the ssh transport: `ssh -o ConnectTimeout=3 -o BatchMode=yes`.
(b) `_tracked_gitlinks(root)` — `git ls-files -s` in `root`, keep mode `160000`, return `(path, sha)` pairs. ⛔ Enumerate the UNION of the gitlink paths in the index and in `git ls-tree HEAD`. Neither source alone sees every staged change — measured: the index sees a staged ADDITION and misses a staged REMOVAL, and HEAD is the reverse. With the union, (e)'s porcelain check reports each as uncommitted. (The first cycle's reason for the index alone, that a HEAD-sourced arm reports a staged bump twice, does not hold here: (e) short-circuits any staged path before a comparison runs, under either source. Unstaged paths carry the same sha in both.)
(c) `_submodule_url(root, path)` — find the `.gitmodules` section whose `path` equals the gitlink path (`git config -f .gitmodules --get-regexp '^submodule\..*\.path$'` in `root`), then read THAT section's `url`; `None` if no section names this path. ⛔ NOT `submodule.<path>.url`: sections are keyed by submodule NAME, which only defaults to the path. Measured on a submodule named `forge` at path `lessons-forge`: the path-keyed lookup exits 1, and the arm would FAIL "missing .gitmodules entry" on an entry that is present — a false fail that blocks a wrap.
(d) `_published_tip(url)` — `git ls-remote <url> HEAD` with `GIT_SSH_COMMAND` set to (a) and a subprocess timeout of 10 s as the backstop; return the tip sha, or `None` on any non-zero exit, timeout or empty output.
(e) The `[3/root]` arm at `:256–259`, replaced — **the five outcomes, specified here and only here.** For each tracked gitlink, in order: if porcelain's STAGED column — the FIRST of its two status letters — is not a space for that path, FAIL with the uncommitted CHANGE — naming which, from that letter: `M` a bump, `A` an addition, `D` a removal — and judge nothing more for that path. ⛔ An UNSTAGED change, first letter a space as in ` M`, does NOT short-circuit: on a machine whose submodules are initialized — the Air, measured — it means only that the local checkout moved, and the gitlink is still judged against the published tip below. Short-circuiting on any non-empty status would make the arm judge index against worktree there, which is the old arm's predicate. Else if `_submodule_url` is `None`, FAIL with the missing `.gitmodules` entry. Else collect the URL. Then read every collected URL's `_published_tip` CONCURRENTLY — a thread pool, one worker per URL — and for each: `None` → print `[3/root] WARN (advisory): <path> — published tip unreadable; gitlink not judged.` and append NOTHING to `fails`; equal to the gitlink → nothing; differing → FAIL: `[3/root] <path> gitlink is stale — <gitlink[:8]> recorded, <tip> published; bump it to that sha and commit. ⛔ The published sha is printed in FULL: `update-index --cacheinfo` rejects an abbreviated one (measured: `option 'cacheinfo' expects <mode>,<sha1>,<path>`, exit 129), and QA item 6 compares it to `$TIP` whole.` ⛔ The loop never returns early.
(f) The docstring's step-3 line at `:26` — "bellows gitlink bumped" becomes "every tracked submodule gitlink current".
(g) ⛔ Wrap the whole of (e) in its own `try` inside `check()`. On any exception, print `[3/root] WARN (advisory): gitlink arm error — <exc>; any gitlink not already reported above was not judged.`, append nothing FURTHER, and let `check()` continue to the arms after it. ⛔ Fails that (e) appended before the error STAND. They are uncommitted changes and missing entries, found locally and certain, plus any stale results collected before the failing read; discarding them to make the arm all-or-nothing would hide certain fails because an unrelated remote read crashed. Without this, one bug here fails the whole checker open (MUST-PRESERVE L).
⛔ `_resolve_bellows`, `BELLOWS`, `RECEIPTS`, `LIFECYCLE_DB` and the `[2/bellows]` arm are NOT touched.

**Item 3 — the ritual text.** `hooks/commands/wrap.md`: `:117`'s `` `git add bellows` `` becomes a bump of every stale tracked gitlink TO THE PUBLISHED TIP the arm names — `git update-index --cacheinfo 160000,<published sha>,<path>`, which works on either layout — and `:128–129`'s mini sentence, which today bumps to `<bellows-HEAD-sha>`, a LOCAL head, names the published sha instead. ⛔ A local head can be unpushed, and a bump to it commits a pointer no other machine can fetch — the vocabulary the RE-DRAFT removed from the obligation must not survive in the remedy. `git add <path>` on an initialized machine remains correct only when that checkout already sits at the published tip. Two sentences; do not restructure step 3.

**Item 4 — the dev-log**, naming the five outcomes, the ssh transport constant and why each option is there, and the RE-DRAFT this plan replaces.

**Item 5 — the mutation manifest.** Write `knowledge/mutants/gitlink-arm-remote.json` in the format of `knowledge/mutants/debt-date-arm.json` (#100126) — each mutant a `name`, a `why`, an `anchor` taken from YOUR OWN green code, a `replacement`, and the test it must fail in `expect_fail`. ⛔ **At least these ten, one per invariant that decides a pass or a fail:** `stale-reads-as-pass` (the differing branch appends nothing) killed by case 1; `unreadable-reads-as-stale` (a `None` tip treated as differing) by case 3; `one-source-enumeration` (the index alone, HEAD dropped from the union) by case 4's staged-removal sub-case; `missing-entry-skipped` (a `None` URL skipped, not failed) by case 5; `early-return` (the loop returns after its first fail) by case 8; `sequential-reads` (the thread pool replaced by a plain loop) by case 9's concurrency half; `interactive-ssh` (`BatchMode=yes` dropped) by case 9's transport half; `unguarded-arm` (the (g) `try` removed) by case 10; `short-circuit-on-unstaged` (the staged-column test widened to any non-empty status) by case 4's initialized sub-case; `url-keyed-by-path` (the lookup by `submodule.<path>.url`) by case 6's differing-name sub-case.

> **Deposits:**
> - `knowledge/development/dev-log-gitlink-arm-remote-2026-09-18.md`
> - `knowledge/mutants/gitlink-arm-remote.json`
> - `knowledge/mutants/gitlink-arm-remote.run.txt`

**A3 — verify before committing (paste raw output for each):** the full suite via the venv, stating your A0 baseline and the new total, the ten new tests the only delta, 0 failures; `python3 -m py_compile` on the changed checker; ⛔ the checker run under `/usr/bin/python3` against a scratch fixture built by Item 1's recipe — ALL of it, not a subset: ⛔ each part of it was found necessary because a fixture missing it exercises the wrong branch or none (W1-3, W6-1, W6-2) — that DRIVES ALL FIVE OUTCOMES — not merely imports the module, because a 3.10+ construct in an unreached branch passes both the suite and an import — pasting its exit, its `[3/root]` lines and its advisory line; and the fixture root's `git status --porcelain` before and after, identical. Then commit the checker, the ritual text, the dev-log and the mutation manifest — and ONLY THEN run the mutation check, because it audits `git archive HEAD`: `.venv/bin/python tools/mutation_check.py knowledge/mutants/gitlink-arm-remote.json > knowledge/mutants/gitlink-arm-remote.run.txt 2>&1`, pasting its `MUTATION:` line and `LIVE-TREE UNCHANGED`. ⛔ Every mutant must be KILLED. A survivor means an observer cannot fail against the broken arm it was written for: HALT and name it.

## STEP 2 — QA (the full suite; ten nodes by name; the checker on a scratch fixture; the live read; the receipt)

⛔ **ESTABLISH THE ROOT FIRST — this step is read on its own, so the command is here in full, not referenced:**

```bash
cd "$(git rev-parse --show-toplevel)"
test -f status.py -a -d hooks/eluvian && echo TREE_OK: "$PWD" || { echo 'TREE_WRONG — not the bellows checkout'; exit 1; }
```

and paste the `TREE_OK` line.

⛔ **Run every check and paste RAW output. A check whose output is summarised is not run.**

1. **Full suite** via the venv: `pytest tests/ -q`. State the DEV's A0 baseline, the new total, and that the delta is exactly the ten new tests with 0 failures.
2. **The ten nodes by name**, each `pytest tests/test_wrap_gitlink_arm.py::<name> -q`, all passing.
3. **An unreadable tip passes, a stale one fails:** node 3, pasted, its output showing the advisory line AND the other submodule's fail.
4. **Bounded and non-interactive:** node 9, pasted, with its measured wall time.
5. **The harness interpreter:** the checker run under `/usr/bin/python3` against a scratch fixture driving all five outcomes — ⛔ with an EMPTY DIRECTORY created at every gitlink path, since without one porcelain reports ` D <path>` for an unchanged gitlink and every submodule reads as uncommitted, so only one outcome could ever be reached — ⛔ and with the gitlinks and `.gitmodules` COMMITTED as its baseline, since an uncommitted gitlink reads `A  <path>`, a staged addition, and is reported as uncommitted before any tip is read — exit and every `[3/root]` line pasted.
6. ⛔⛔ **The live read — the non-vacuity proof (Observer K), with a POSITIVE control.** Against the real
   governance root every pointer is current today, so a working arm prints nothing for them — and so does
   an arm that judges nothing. That read cannot tell them apart. So build a root where the arm MUST speak:
   clone the governance root to a scratch directory (the clone creates each submodule's empty directory,
   so porcelain stays clean), point anvil's gitlink at a sha that is NOT its published tip, and COMMIT it —
   staged, it would read as uncommitted rather than stale:

   ```bash
   SCRATCH=$(mktemp -d) && echo "SCRATCH=$SCRATCH"   # ⛔ FIRST — unset, every "$SCRATCH/gov" below expands to /gov
   git clone -q /Users/marklehn/Developer/eluvian-governance "$SCRATCH/gov"
   TIP=$(git ls-remote "$(git -C "$SCRATCH/gov" config -f .gitmodules submodule.anvil.url)" HEAD | cut -f1)
   git -C "$SCRATCH/gov" update-index --cacheinfo "160000,1111111111111111111111111111111111111111,anvil"
   git -C "$SCRATCH/gov" commit -qm "positive control: anvil gitlink not at its published tip"
   ```

   ⛔ The sha is SYNTHETIC on purpose. The arm compares shas and never needs the object, so no local
   checkout is consulted — a real parent taken from `~/Developer/anvil` would make this check depend on
   that checkout being current, and a stale one would leave the clone all-current and HALT QA against
   a working arm. `$TIP` is kept for the assertion below.

   Then run the checker from THIS worktree in the hook's stripped environment, with the root passed INSIDE
   `env -i`, which clears everything else:

   ```bash
   env -i HOME="$HOME" PATH=/usr/bin:/bin ELUVIAN_WRAP_ROOT="$SCRATCH/gov" /usr/bin/python3 hooks/eluvian/wrap_check.py "" debt
   ```

   Paste the whole output. ⛔ **Assert POSITIVELY: exactly ONE `[3/root]` stale line, naming `anvil`, whose published sha EQUALS `$TIP` — the arm could only have read that from the remote — and
   the tip `ls-remote` returned; NO stale line for `bellows` or `lessons-forge`; NO `published tip
   unreadable` advisory.** The stale line is the proof that the arm read the real published tip from
   inside the hook's environment — measured feasible 2026-09-18 (gitlink `fc32f630` against a published
   `cfd6fd92`). Its absence means the arm is vacuous where it runs: HALT and say so. Other arms' lines
   are expected against a scratch root and are not QA failures — read only the gitlink lines.
7. **The arm writes nothing:** node 7, plus the fixture root's porcelain before and after, identical.
8. **The ritual text:** `sed -n 115,130p hooks/commands/wrap.md`, pasted, showing no `bellows`-only instruction remains in step 3 — ⛔ AND that the bump target is the PUBLISHED tip the arm names, not a local head (W3-3). Paste `/usr/bin/grep -c 'HEAD-sha' hooks/commands/wrap.md`, which must be 0, and, as its positive control, `/usr/bin/grep -c 'published' hooks/commands/wrap.md`, which must be at least 1 — an absence proves nothing until the same probe finds what should be there.
9. **`_resolve_bellows` untouched:** `pytest tests/test_hook_default_root.py tests/test_gates_cross_machine_paths.py -q`, passing.
10. **The mutation run:** `knowledge/mutants/gitlink-arm-remote.run.txt`, pasted whole — `MUTATION: 10 killed, 0 survived, 0 error` or better, and `LIVE-TREE UNCHANGED`. A survivor is a QA failure.
11. **The receipt and the three raw-output files**, written at the paths the Deposits block names.

> **Deposits:**
> - `knowledge/qa/evidence/gitlink-arm-remote-qa-receipt-2026-09-18.md`
> - `knowledge/qa/evidence/gitlink-arm-remote-suite-2026-09-18.txt`
> - `knowledge/qa/evidence/gitlink-arm-remote-nodes-2026-09-18.txt`
> - `knowledge/qa/evidence/gitlink-arm-remote-live-read-2026-09-18.txt`

**Rule 20 — QA Self-Check Results**

| # | check | result |
|---|---|---|
| 1 | full suite, delta is the ten new tests only | |
| 2 | ten nodes by name | |
| 3 | unreadable passes with advisory, stale fails | |
| 4 | reads bounded, transport non-interactive | |
| 5 | checker green under `/usr/bin/python3`, five outcomes driven | |
| 6 | live read flagged the planted stale pointer against the real remote; no advisory | |
| 7 | arm writes nothing | |
| 8 | ritual text bumps every gitlink to the published tip; no bellows-only or HEAD-sha instruction remains | |
| 9 | `_resolve_bellows` tests still pass | |
| 10 | every mutant killed, live tree unchanged | |
| 11 | receipt and raw outputs written | |

PASSED — SELF-CHECK PASSED
