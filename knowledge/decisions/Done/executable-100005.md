# bellows — executable: the PROJECT PRODUCER — thread the project through the claim seam (part A, tolerant by construction)

**Date:** 2026-08-31 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** `tests/test_plan_claim.py` (targeted) + a full-suite CONTROL COMPARISON | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Tier computed, not judged (§1):** **T-3 fires** — cross-machine is the entire point, and this runs on a machine it was not written on. **T-1 fires** — 3 files across the seam and the daemon. **T-2 fires** — it changes what lands in the production `plan_claims.project` column. **T-8 fires** — `100003` built the RECEIVING side; nothing has yet built the producing side, so this is not a structure-for-structure clone. No T-5 (additive, revertible) and no T-6 (`GOVERNANCE.md` belongs to thread 48, not here). Highest demand → **T1: full five-lens walk, no mandatory panel.**

**Clone origin BY KIND — measured:** `[570]` `2a25d97` — the fork-1 claim shim, which created `plan_claim.py` and the `claim_gate` call this plan threads through. ⚠️ It is also the exact sha both machines' daemons loaded at, so the running code and the clone origin coincide. **Divergence:** `[570]` built the seam; this plan gives it a datum.

## Why this exists

`executable-100003` shipped project-scope exclusivity on the **tuyere** side and it is **inert by construction** — `project_lock` defaults `off`, and no producer exists. `tuyere.claims claim` accepts `--project` and nothing passes it, so every row lands with `project` NULL.

**The datum is already in hand at the moment of the claim.** `bellows.py:833` computes `project_path = str(plan_p.parents[2])` from the plan's own path, and the claim happens at `bellows.py:936` — 103 lines later, in the same function (`run_plan`, opens at `:821`). ⛔ **NOT a `plans.target_project` read:** the claim PRECEDES the mint (`# Mint id + write plans row atomically` is the statement immediately after the `claim_gate` call), so that row does not exist yet. `100003`'s panel seat 1 severed exactly that premise as a DIRECTION finding.

**The key is the BASENAME, never the raw path.** Machine-local roots differ (`/Users/marklehn/Developer/tuyere` here, `/Users/marklehn/Developer/GitHub/tuyere` on the shop), so a path key never compares equal across machines — it would decline nothing, ever, while presenting as exclusivity. `os.path.basename` is also how bellows already names projects (`bellows.py:1142`), so this is not an invention.

## ⚠️ PART A IS TOLERANT BY CONSTRUCTION — and part B is a different plan

The CEO's ruling is that **a project declaration is an unconditional input and NULL is not a state the system may reach going forward.** That target is reached in **two** steps, and the order is not negotiable:

**tolerant-reader → producer → strict.** `100003` was step one. **This plan is step two.** Step three — `--project` becomes semantically required, the tolerance branch is DELETED rather than relaxed, and the column gains `check (project is not null) not valid` — is **thread 51 part B, a separate plan that must not land until EVERY machine produces.**

⚠️ **A strict CLI ahead of its producers disables the claim path on every machine whose shim does not yet pass the flag.** That is why `E2-project-flag` is `if project:` and not an unconditional append.

## What this plan does NOT do

- **Does not make `--project` required, delete the tolerance branch, or add the check constraint** — thread 51 part B.
- **Does not activate `project_lock`.** It stays `off`; promotion to `advisory` is a later ordered CEO config act whose precondition is **producers everywhere**, not modes everywhere.
- **Does not touch the intent lane** (`watcher.py`), the down-sweep, the class check, or `claim_seq`.
- **Does not change `_mode` or any decline path.** Under `plan_claim_lock: off` the seam returns before `claim_for_deposit` is even reached, so this change is invisible there.
- **No schema change.** The `project` column already exists (`schema/006`, shipped by `100003`).

## MUST-PRESERVE — clauses whose only carrier is prose

- ⚠️⚠️ **`project=None` DEFAULTS ON BOTH SIGNATURES.** `tests/test_plan_claim.py` is 563 lines and calls these functions throughout; a required parameter breaks every caller. The default is what makes part A additive.
- ⚠️⚠️ **`if project:` — the flag is appended ONLY when a value exists.** An unconditional append sends `--project None` to a CLI that would record the string "None" as a project key. Nothing mechanical catches that; the test `test_absent_project_omits_the_flag` is its only guard.
- ⚠️ **BASENAME, not the raw path**, at the call site (`E7`). The raw path is machine-local and can never match across machines.
- ⚠️ **The self-strand hint must branch on the decline's stated CAUSE, not the bare exit code.** After `100003`, exit 3 means EITHER a slug this machine holds (a genuine self-strand) OR a project another machine holds — where following the hint releases **someone else's claim**. tuyere prints `held: project '<key>'` for the project arm.
- ⚠️⚠️ **THE CLAIM MUST PRECEDE WORKTREE CREATION — this ordering is LOAD-BEARING, not incidental.** `claim_gate` is at `bellows.py:936`; `_create_worktree` is at `:1020`, and worktrees nest at `<project>/.bellows-worktrees/<slug>`. tuyere's `_project_key` has **no worktree awareness** — measured, a `<project>/.bellows-worktrees/<slug>` path normalizes to **`<slug>`**, not the project name. ⚠️ Written with placeholders deliberately: an absolute example here is parsed by `plan_lint`'s `(o1)` check as a real path reference and WARNs. ⛔ If the claim ever moved below `:1020`, **every dispatch would key uniquely, nothing would ever conflict, and it would present as working exclusivity** — the exact failure this plan names for raw paths ("it would decline nothing, ever"), reached through a different door. **Nothing pins this ordering** — no test asserts it, and §"Why this exists" states it as availability ("the datum is already in hand"), not as correctness. Do not reorder.
- ⚠️ **Do not adjust a test or mutant to obtain a desired result.** A surviving mutant is a STOP.

## Numbers discipline — the pins DEV re-derives

⚠️ **Measured 2026-08-31 by the Planner on the live checkout. Re-derive; yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| P1 | claim-test baseline, pre-build | **44 passed, 0 failed** | `"$PY" -m pytest tests/test_plan_claim.py -q` |
| P2 | target shas, pre-edit (first 16 hex) | `plan_claim.py` `08f82e409ce427b0` · `bellows.py` `f9855c305c8293f2` · `tests/test_plan_claim.py` `6e1101438c28b275` | `shasum -a 256` |
| P3 | `--project` occurrences, pre-edit | **0** in both `plan_claim.py` and `bellows.py` | `/usr/bin/grep -cF -- "--project" <file>` ⚠️ the `--` terminator is REQUIRED or grep parses the pattern as an option |
| P4 | full-suite baseline **IN YOUR OWN TREE** | ⚠️ **NOT PINNED TO A NUMBER — see A3** | `"$PY" -m pytest tests/ -q` |

## STEP 1 — DEV

> ⛔ **A0 — pre-flight. RESOLVE THE INTERPRETER FIRST — a worktree has no `.venv`.**
> ```
> cd "$(git rev-parse --show-toplevel)" && test -f plan_claim.py && echo TREE_OK   # HALT unless TREE_OK
> MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
> PY="$MAIN/.venv/bin/python"
> test -x "$PY" || { echo "HALT: no interpreter at $PY"; exit 1; }
> echo "RESOLVED interpreter: $PY"         # ⛔ visibility law — say which candidate won
> "$PY" -c "import yaml, watchdog, pytest; print('VENV_OK')"
> ```
> ⚠️ **Bellows plans dispatch in a WORKTREE (`bellows.py:1472`), and `.venv`, `config.json` and `lifecycle.db` are ALL gitignored — none of them exists there.** Measured: an earlier draft used a relative `.venv/bin/python` throughout and **halts at A0** with `no such file or directory`. `100003` solved this with a hardcoded absolute path; `git rev-parse --git-common-dir` reaches the main checkout without one, so this clone is portable where its parent was not. **Use `"$PY"` for every python invocation in this plan.** Re-derive P1-P3 and paste raw output.
>
> ⛔ **A1 — capture the full-suite baseline BEFORE building, in THIS tree, and keep it.**
> ```
> "$PY" -m pytest tests/ -q 2>&1 | grep "^FAILED" | sed 's/ - .*//' | sort > /tmp/before.txt
> wc -l < /tmp/before.txt
> ```
> ⚠️ **The count is deliberately NOT pinned in this plan, and that is the whole point.** This repo carries pre-existing failures that differ **by tree**: the live checkout shows 11, a copy shows 12, because `test_lifecycle_db_resolves_under_bellows_root` asserts a path that only resolves in the real checkout — and **bellows plans dispatch in a worktree** (`bellows.py:1472`). Comparing your worktree's result against a number measured elsewhere manufactures a phantom regression; the Planner did exactly that during authoring and spent a cycle chasing it. **The acceptance criterion is SET EQUALITY against your own baseline, captured here.**
>
> **A2 — run the Planner's builder.** Resolve it from the governance root rather than a literal path:
> ```
> REL="governance/knowledge/decisions/drafts/build-project-producer.py"
> BUILDER=""
> for R in "${ELUVIAN_WRAP_ROOT:-}" "$HOME/Developer/eluvian-governance" "$HOME/Developer/GitHub"; do
>   [ -n "$R" ] && [ -f "$R/$REL" ] && BUILDER="$R/$REL" && break
> done
> test -n "$BUILDER" || { echo "HALT: builder not found (tried ELUVIAN_WRAP_ROOT and both known roots)"; exit 1; }
> echo "RESOLVED builder: $BUILDER"        # ⛔ visibility law — say which candidate won
> python3 "$BUILDER" --repo "$(git rev-parse --show-toplevel)"
> ```
> ⚠️ **Not a hardcoded path:** `$ELUVIAN_WRAP_ROOT` is declared in `~/.claude/settings.json` and is therefore **absent from the daemon's environment** (measured), so the fallbacks are load-bearing, not decoration. Expect `APPLIED: 8/8 edits.` and exit 0; paste every `anchor … count=1` line. **Take the count from the builder, never from this plan.** Nonzero exits are terminal and all leave the tree intact: **2** missing target · **3** anchor not unique · **4** post-apply verification · **5** partially-applied (a STOP, not a resume) · **6** unwritable or write failure, rolled back · **7** ⛔ ROLLBACK INCOMPLETE, restore from git.
>
> **A3 — verify. Paste raw output for each.**
> 1. `"$PY" -m py_compile plan_claim.py bellows.py` → exit 0.
> 2. Claim tests → **49 passed, 0 failed** expected (44 + 5). ⚠️ A PREDICTION the run supersedes; **the HALT condition is a non-zero FAILURE count, never a differing total.**
> 3. ⭐ **Full-suite CONTROL COMPARISON — set equality, not counts.**
>    ```
>    "$PY" -m pytest tests/ -q 2>&1 | grep "^FAILED" | sed 's/ - .*//' | sort > /tmp/after.txt
>    comm -13 /tmp/before.txt /tmp/after.txt   # NEW failures — must be EMPTY
>    comm -23 /tmp/before.txt /tmp/after.txt   # newly-passing — informational
>    ```
>    **Any line from the first `comm` is a HALT.** Paste both outputs even when empty, and state the passed/failed totals for both runs.
> 4. **Earnability.** Save the built `plan_claim.py` aside FIRST (`cp plan_claim.py /tmp/pc.built`), then restore it WHOLE to pre-plan content — assert `shasum` begins `08f82e409ce427b0` before believing the result. Expect **exactly 3 failed** — `test_project_appended_to_cmd_when_supplied`, `test_claim_gate_threads_project_through`, `test_self_strand_hint_suppressed_on_a_PROJECT_decline`. **MEASURED on a scratch build, not reasoned** — an earlier draft predicted 5 and was wrong.
>    ⚠️ **TWO of the five new tests PASS in both states, and correctly so — they are REGRESSION GUARDS, not earnability proofs. Do not "fix" them.** `test_absent_project_omits_the_flag` passes on pre-plan code because that code never appends the flag at all — its job is to prove the tolerance survives the change, which is a claim about the FUTURE (part B deletes that branch), not about this diff. `test_self_strand_hint_still_fires_on_a_SLUG_decline` is the positive arm of the M1 pair: without it, M1's suppression assertion cannot be distinguished from the hint never firing.
>    Restore from `/tmp/pc.built` and expect 49 again. ⚠️ **The save-aside is mandated because the builder will refuse to re-apply to a partial tree (exit 5), which is correct behaviour and not a way back.**
> 5. **Discrimination — a surviving mutant is a STOP.** Apply each to the built tree, run the CLAIM tests, restore from `/tmp/pc.built`, paste each result:
>    | mutant | edit | expected |
>    |---|---|---|
>    | M1 | drop `and "held: project " not in detail` from the hint condition | **exactly 1 failed** — `test_self_strand_hint_suppressed_on_a_PROJECT_decline`. ⚠️ Its positive twin `test_self_strand_hint_still_fires_on_a_SLUG_decline` must stay GREEN under this mutant; if both fail the hint is broken outright rather than mis-scoped |
>    | M2 | replace `if project:` + append with an unconditional `cmd += ["--project", str(project)]` | **exactly 1 failed** — `test_absent_project_omits_the_flag` |
>    | M3 | drop `project` from the `claim_for_deposit(...)` call inside `claim_gate` | **exactly 1 failed** — `test_claim_gate_threads_project_through` |
> 6. `git diff --stat` → exactly **3** files.
>
> **A4 — dev log** `knowledge/dev-logs/project-producer-dev-2026-08-31.md`: **the `RESOLVED interpreter:` and `RESOLVED builder:` lines verbatim** (⚠️ QA Item 3b quotes them, so Step 1 must record them — they are emitted in A0 and A2, BEFORE the builder runs, and are therefore not part of "the builder's output"); P1-P3 yours-vs-table with "supersedes" where they differ; the builder's full output including every anchor line; every A3 item with raw output; **both `comm` outputs verbatim**; the earnability split with the sha guard shown firing; all three mutant results with MEASURED counts.
>
> **A5 — commit**, pathspec-scoped, never `-A`:
> `git add plan_claim.py bellows.py tests/test_plan_claim.py knowledge/dev-logs/project-producer-dev-2026-08-31.md && git commit -m "[<id>] project producer: thread the project through the claim seam (part A, tolerant)"`
>
> **Post-conditions:** claim tests green with **0 failures** at whatever total the run reports · `py_compile` clean · **the full-suite NEW-failure set is EMPTY against the A1 baseline captured in this same tree** · no mutant survived · four files committed · production DB UNTOUCHED (this step writes no database).
>
> **Deposits:**
> - `bellows/plan_claim.py`
> - `bellows/bellows.py`
> - `bellows/tests/test_plan_claim.py`
> - `bellows/knowledge/dev-logs/project-producer-dev-2026-08-31.md`
>
> **Scope:**
> - `bellows/plan_claim.py`
> - `bellows/bellows.py`
> - `bellows/tests/test_plan_claim.py`
> - `bellows/knowledge/dev-logs/project-producer-dev-2026-08-31.md`

## STEP 2 — QA

> ⚠️ Re-prove `VENV_OK` at the top of this step — a verdict gate of arbitrary wall-clock time sits between the steps.
>
> **Item 1 — claim tests, REDIRECTED not piped.** `"$PY" -m pytest tests/test_plan_claim.py --tb=short -q > knowledge/dev-logs/project-producer-suite-2026-08-31.txt 2>&1; echo "exit=$?"` → `exit=0`. ⚠️ `… | tee f` reports `tee`'s status, so a failing suite would read as exit 0.
> **Item 2 — re-run the full-suite control comparison** exactly as A3.3, in your own tree, and state that the NEW-failure set is empty. ⚠️ Re-capture the baseline if you are in a different tree than Step 1 — a baseline from another root is not a control.
> **Item 3 — the producer is REAL, proven at the seam.** Without touching production: call `plan_claim.claim_for_deposit` with `subprocess.run` monkeypatched to capture `cmd`, once with a project and once without, and state that `--project <value>` appears in the first and no `--project` token in the second. State that no live claim was made.
> **Item 3b — state WHICH candidate each resolver picked**, quoting the `RESOLVED builder:` and `RESOLVED interpreter:` lines from the Step-1 log. ⛔ **`[570]`'s visibility law (from 560's S1-5): if a resolver silently falls through to a different candidate than expected, say so LOUDLY** — otherwise "it worked on the dispatching machine" is unreproducible, and a later machine that resolves differently looks like a regression rather than a different environment.
> **Item 4 — state that the arm is still INERT end-to-end.** Confirm `plan_claim_lock` and `project_lock` values in this machine's configs and that neither was changed by this plan. **This plan makes the datum flow; it does not turn enforcement on.**
> **Item 5 — receipt** `knowledge/dev-logs/project-producer-qa-2026-08-31.md`: numstat vs the DEV commit (four files). ⛔ **Identify that commit by its `[<id>]` COMMIT TAG — `git log --oneline --grep "\[<id>\]" -1` — NEVER HEAD-relative.** `[570]` names this the *measured cross-terminal interleave class*: another terminal, or the daemon itself, can land a commit between the steps, and `HEAD~1` then points at someone else's work. This plan's own session had two machines and a daemon committing concurrently. Then: toplevel; `git reflog -n 4` → 0 amends; **Items 1, 2, 3, 3b and 4 — FIVE lines, not four** — each on its own stated line. ⚠️ This read "Items 1-4" from v0 until walk 5: **Item 3b was inserted at walk 3 and this enumeration never absorbed it**, so the receipt would have silently omitted the resolver statement that walk 3 added and walk 4 wired into the post-conditions; then the Rule 20 block inside a "Verification"-headed section.
> **Item 6 — commit**, pathspec-scoped: the two evidence files, exactly two.
>
> ⚠️ **Gate note:** pytest summary named at Item 1 — the gate parses it; no benign override pre-declared.
>
> **Post-conditions:** claim tests green from an unpiped run · full-suite NEW-failure set empty against a baseline captured in THIS tree · the flag proven present-when-supplied and absent-when-not at the seam · **both resolver results stated (Item 3b)** · enforcement still off on both sides · two evidence files committed.
>
> **Deposits:**
> - `bellows/knowledge/dev-logs/project-producer-suite-2026-08-31.txt`
> - `bellows/knowledge/dev-logs/project-producer-qa-2026-08-31.md`
>
> **Scope:**
> - `bellows/knowledge/dev-logs/project-producer-suite-2026-08-31.txt`
> - `bellows/knowledge/dev-logs/project-producer-qa-2026-08-31.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** **T1**, computed. Firing: **T-3** (cross-machine, and runs where it was not written), **T-1** (3 files across seam and daemon), **T-2** (changes what lands in production `plan_claims.project`), **T-8** (the receiving side shipped; the producing side is novel). Not T-5, not T-6.

**Walk register:** `governance/knowledge/research/walk-register-project-producer-2026-08-31.md`

⚠️ That field carries the PATH ALONE — `cycle_check`'s `WALK_REGISTER_RE` captures everything after the marker as the filename and crashes with `OSError: File name too long` on appended commentary. Notes belong here, below it.

**Walks:** walk 0 pinned (5 measurements + clone-diff FACTS/ARTEFACTS; STRUCTURE owed). **Walks 1-8 complete.** Yields **0 → 2 → 1 → 2 → 2 → 1 → 2 → 2 → 0**; instruction-class **0 → 2 → 1 → 2 → 2 → 1 → 1 → 2 → 0**. ✅ **Walk 8 is the cycle's FIRST DRY WALK.** ⛔ **Walk 7 was the first walk in which `plan_lint` actually ran** — walks 1-6 invoked it with a bare `python3` that dies on a missing module, so the manifest's second gate had never reported. **Walk 6 was a commissioned DESIGN walk** — intent, not mechanism. ✅ The clone-diff **STRUCTURE pass was discharged at walk 3** and produced both of that walk's findings. Walk 2 was run as a **worktree dry run** — the environment dispatch actually creates.

- **Walk 0 STATUS:** 0 folded — instruction 0 / record 0
- **Walk 1 STATUS:** 2 folded — instruction 2 / record 0 (weak spots 1, vulnerabilities 1; destruction dry, integration-record dry, ACID dry); 1 of 2 fold-introduced
- **Walk 2 STATUS:** 1 folded — instruction 1 / record 0 (vulnerabilities 1; weak spots dry, destruction dry, integration-record dry, ACID dry); 1 HIGH; 0 fold-introduced
- **Walk 3 STATUS:** 2 folded — instruction 2 / record 0 (integration-record 2; weak spots dry, destruction dry, vulnerabilities dry, ACID dry); both from the STRUCTURE pass
- **Walk 4 STATUS:** 2 folded — instruction 2 / record 0 (weak spots 2; destruction dry, vulnerabilities dry, integration-record dry, ACID dry); **2 of 2 fold-introduced by walk 3's own fold**
- **Walk 5 STATUS:** 1 folded — instruction 1 / record 0 (integration-record 1; weak spots dry, destruction dry, vulnerabilities dry, ACID dry); **1 of 1 fold-introduced by walk 3's own fold — the FOURTH sibling of one insertion.** ✅ Preceded by a **SECOND worktree dry run** of the full A0–A3 set against the post-walk-4 text: **zero deviations** (44/0,0 · APPLIED 8/8 · 49 claim tests · NEW-failure set EMPTY · earnability 3 · M1/M2/M3 = 1/1/1 · diff 3 files), both new visibility echoes firing. ⛔ The class was then **closed by enumeration, not sampling**: every `Item N` and `AN` reference swept, no fifth sibling exists
- **Walk 6 STATUS:** 2 folded — instruction 1 / record 1 (vulnerabilities 1, integration-record 1; weak spots dry, destruction dry, ACID dry); **0 fold-introduced — the streak is broken.** ✅ Four premises challenged and CLEARED by measurement (`parents[2]` depth · basename uniqueness across `watched_projects` · claim-before-worktree · both machine layouts through the real `_project_key`), each recorded so walk 7 does not re-walk them
- **Walk 7 STATUS:** 2 folded — instruction 2 / record 0 (integration-record 1, weak spots 1; destruction dry, vulnerabilities dry, ACID dry); 1 of 2 fold-introduced. ⛔ Both were reachable only once `plan_lint` ran under the **resolved interpreter** — the plan's own A0 defect, committed against the plan's own tooling six times. ✅ `plan_lint` now **9 PASS / 0 FAIL**; the 2 surviving WARNs are correct by design and deliberately unfolded
- **Walk 8 STATUS:** 0 folded — instruction 0 / record 0 (weak spots dry, destruction dry, vulnerabilities dry, integration-record dry, ACID dry); 0 HIGH. Narrow by design — walk 6's four cleared premises were NOT re-walked, and 0 step-block lines have changed since walk 6. Both gates run under the **resolved interpreter**: `plan_lint` **9 PASS / 0 FAIL**

⚠️ **The builder was written and VERIFIED BEFORE this prose existed**, deliberately — the previous cycle spent four reading walks on prose-about-edits before a builder retired that surface. Measured at authoring: `--check` 8/8 anchors `count=1`; applied to a scratch copy `APPLIED: 8/8`; claim tests **44 → 49**; **all three mutants kill with exactly 1 failure each**; full suite failure set **identical to a pristine-copy control**.

**CEO rulings folded into v0:**
- **Part A only; part B is a separate plan** — the ruled order tolerant-reader → producer → strict, and B cannot land until every machine produces.
- **New work goes through the drafting cycle, not a hand edit** (2026-08-31).
- **`watched_projects` is NOT standardised across machines until `project_lock` works** (2026-08-31) — so this plan dispatches on one machine only.

**Direction verdict (after walk 1): PROCEED** — none of §2.0's three RE-DRAFT triggers fires; the clone origin holds, the mechanism survived untouched, and the scope premise was re-measured at walk 0.

**Closing:** **full walk 8 dry; last event = lens pass.** ✅ Instruction 0 / record 0 across all five lenses, each applied to current text with a measurement rather than a re-read. ⛔ **BUT THE CYCLE ESCALATED AT WALK 7 AND WALK 8 DOES NOT DISSOLVE THAT.** `cycle_check` returned **`ESCALATE:yield-rising`** on its own merits — instruction-class 1 → 2 — and that is a CEO matter, not a Planner's to explain away. ⚠️ The explanation, offered as explanation and **not** as dismissal: the yield rose because walk 7 switched on an instrument that had never run this cycle. **`plan_lint` dies under a bare `python3`**, so walks 1-6 read `cycle_check` alone while the manifest requires both. Under the resolved interpreter it found two defects at once, **one latent since walk 0** — a measurement-regime change, not a quality regression. The plan did not get worse; the blindfold came off. ⛔ **A Planner explaining away his own escalation is precisely what that gate exists to catch, so it goes up.** ⚠️ Two of the last three walks' findings were defects in the GATES, not the plan — **threads 58 and 63, the same class: a mechanical check a conforming plan's natural spelling defeats.** Continuing to walk this plan cannot fix either. ⛔ **DISPATCH REMAINS BLOCKED BY THREAD 60** independently of this cycle's state. ⚠️ Prior note at walk 7: `plan_lint` had never run; the hyphen in `weak-spots` defeated the required-lens check on every walk while that lens had been walked every time; a false finding was caught one `comm` line short of the register. ⚠️ Prior note at walk 6: the design walk paid — `_project_key` has no worktree awareness, so the claim is safe only because `:936` precedes `:1020`; now a MUST-PRESERVE. ⚠️ Prior note at walk 5: fourth sibling of walk 3's insertion; class closed by enumerating every `Item N` and `AN` reference, no fifth exists; step twice-proven in a worktree with zero deviations. ⚠️ Prior note at walk 4: Two instruction-class findings, **both the debris of walk 3's own fold** — an obligation added to QA without updating the step that produces its input or the post-conditions that make it checkable. §2.7's fold-sweep rule covers exactly this; third instance across two cycles. ⛔ **The DESIGN has not been challenged since the direction verdict at walk 1** — walks 2-4 found an environment defect, two dropped parent hardenings, and the debris of fixing them. Walk 5 owed. ⚠️ Prior note at walk 3: Two instruction-class findings, **both hardenings the parent `[570]` carried and this clone had dropped** — identifying the DEV commit by its `[<id>]` tag rather than HEAD-relative, and the resolver visibility law. Neither is a design defect. ⚠️ **The STRUCTURE pass was owed from walk 0 and deferred to walk 3, so walks 1 and 2 reviewed a plan missing two of its parent's protections** — the same deferral, with the same consequence, as the previous cycle. Walk 4 owed. ⚠️ Prior note at walk 2: One instruction-class finding, HIGH: the plan HALTED AT A0 in a worktree because every python invocation was relative and `.venv` is gitignored. Now resolved via `--git-common-dir`, and the full A3 set re-run in a real worktree with **zero deviations**. Yield fell 2 → 1. Walk 3 is owed. ⚠️ Prior note at walk 1: Two instruction-class findings, and a first pass cannot close regardless. ⚠️ Both are the same class: **a result that was REASONED rather than MEASURED** — the earnability split predicted 5 and measured 3. Sixth consecutive instance across two cycles. The builder retired prose-about-EDITS; it does not retire prose-about-RESULTS. Walk 2 is owed.

## Cycle Manifest
tier: T1
target: bellows/plan_claim.py
class: shop-infra
reads: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-project-producer.py, /Users/marklehn/Developer/bellows/plan_claim.py, /Users/marklehn/Developer/bellows/bellows.py, /Users/marklehn/Developer/bellows/tests/test_plan_claim.py, /Users/marklehn/Developer/tuyere/knowledge/decisions/Done/executable-100003.md
writes: plan_claim.py, bellows.py, tests/test_plan_claim.py, knowledge/dev-logs/project-producer-dev-2026-08-31.md, knowledge/dev-logs/project-producer-suite-2026-08-31.txt, knowledge/dev-logs/project-producer-qa-2026-08-31.md
open_forks: (0) ⚠️ **E7's client-side basename is BEHAVIOURALLY REDUNDANT with tuyere's `_project_key`** — measured through the real function, the mini root, the shop root, the bare name `bellows`, and a trailing-slash spelling **all yield the identical key and identical reason**; the docstring guarantees idempotence explicitly. Not a defect, and E7 stands as written — but it splits ONE normalization rule across TWO repos, so a future rule change (case-folding, worktree rejection) must land in both or they disagree. Part B should decide whether the client sends the key or the raw `project_path` and lets the server own the rule alone; (1) ⚠️ **BOUND — thread 51 part B**: `--project` becomes semantically required, the tolerance branch is DELETED not relaxed, and the column gains `check (project is not null) not valid`. Must not land until EVERY machine produces; (2) promotion to `advisory` then `required` is a later ordered CEO config act whose precondition is producers everywhere; (3) **thread 59** — `eligible_projects` is null on both machines, so the executor flip collapses two decisions into one plist edit; settle before any machine becomes an executor; (4) ⛔ **RETRACTED 2026-08-31 — thread 60 was a FALSE ALARM and never blocked dispatch.** It claimed a bare-named blueprint in `bellows/knowledge/decisions` becomes claimable once that dir is watched. **`is_runnable_plan` is an ALLOWLIST, not a denylist** (`bellows.py:2282`): `^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$`. Measured against the real function, every entry in that directory is **inert**, the blueprint included. All six dispatch paths are gated on it — the rescan loops, group collection, and `_handle`, through which every watchdog event routes — and `is_claimable` adds a SECOND gate requiring a lifecycle clearance record. Thread 60 dropped; the file is left where it is; (5) cross-PROJECT write overlap remains uncovered by this arm
walks: 8 warm (walk 0 pin + walks 1-8; walks 2 AND 5 worktree dry runs, both zero-deviation; STRUCTURE discharged at walk 3; walk 6 a commissioned DESIGN walk; walk 8 dry); no panel (T1)
yields: 0, 2, 1, 2, 2, 1, 2, 2, 0 | instruction-class: 0, 2, 1, 2, 2, 1, 1, 2, 0 | direction verdict after walk 1: PROCEED | ESCALATED at walk 7: cycle_check=yield-rising (1->2), cause = plan_lint's first run of the cycle under a resolved interpreter; CEO matter, not dissolved by walk 8
validation: cycle_check=BAR_MET, plan_lint=0_FAIL (9 PASS; 2 residual WARNs correct by design and deliberately unfolded), builder --check=8/8 anchors unique exit 0, claim tests 44 -> 49 measured, mutants M1/M2/M3 each exactly 1 failed measured, full-suite failure set identical to pristine-copy control
coherence: 9/9 walks have register rows (walks 0-8); builder written and verified BEFORE the prose; v0 authored against measured facts rather than predictions; gate defects found DURING the cycle filed as threads 58 and 63 rather than hand-edited
