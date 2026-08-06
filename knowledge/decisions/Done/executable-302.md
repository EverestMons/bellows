# Executable: three mechanical drafting-cycle checks in plan_lint

**Type:** Executable
**Project:** bellows
**Depends on:** none. ⚠️ **This plan cites no diagnostic — its evidence is three defect classes observed three times each during the drafting of plans 301, 302 and the enforceability diagnostic, all in this session's record.**
**Created:** 2026-08-06
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`) and does not parse the filename. **Read `id_sequence` at deposit.**

---

## Why this exists — three rules that are written down and still recur every plan

Option C concluded that the shop's gap is **enforcement, not detection**. These three classes are the cheapest available proof of that, and each has the same profile: **narrow, mechanical, needing no artifact but the file under test** — the profile the Rule 20 banner has, and the only profile the shop has ever successfully mechanized.

| class | occurrences | every one caught by |
|---|---|---|
| **ledger ordering** — a constraint inserted above an existing entry | 3 (`301` C23-above-C22; the enforceability draft twice) | a manual sweep |
| **stale `Closing:` disclaimer** — *"no lens has read this artifact"* after lenses have | 3 (`301`, `302`, enforceability) | a manual sweep |
| **halt-routing staleness** — a fold names a new input the routing never learns about | 3 (`301` Z3, `302` A4, enforceability G1) | ACID, one phase late |

**Each is already a written rule. Two of the three recurred AFTER being written down, in the plan that wrote them.**

⚠️⚠️ **TWO HONEST SCOPE CORRECTIONS, MADE BEFORE ANY CODE IS WRITTEN.**

1. **These fire during DRAFTING, not at deposit.** Every measured occurrence was fixed by hand before the plan was deposited, so a deposit-time run would have caught **none** of them. **Their value depends on `plan_lint` being run at shape-stability during the cycle** — which the shop already mandates after plan 298's §5 pass found three hard FAILs at deposit that six review phases had missed. **Say this in the History note; do not sell these as deposit-time guards.**
2. ⚠️ **The third check is NOT cheap in its general form and is deliberately narrowed.** Detecting "a fold added an input the routing missed" in prose is an entity-extraction problem with a high false-positive rate. **What IS mechanical: backtick-quoted plan ids.** All three observed occurrences were exactly that. **Check (i) is scoped to plan-id coverage and its limits are stated in the code comment and the History note — it does not claim to catch the general class.**

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

⚠️ **Machinery below is cloned from `executable-277` (the newest same-class plan_lint §4 plan) and `executable-140` (the WARN-only precedent), diffed at walk 1 per §2.6.** **277 is a strict superset of 140; nothing 140 carries was deliberately dropped by 277.**

---
---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py` (the current `(f)` Drafting-Cycle check and the WARN mechanism), and — for the authoritative behaviour — `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md` §4 (ABSOLUTE path; it lives at the repo root, outside this worktree). **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
> **Mechanical-only invariant (140).** All three checks are **WARN-only advisory**. They emit bare `print(...)` lines and must **NEVER** set `all_passed = False`, change the return code, or raise. **A malformed or absent block skips with no exception.**
>
> **Task A0 — pre-edit cleanliness + warn-first precondition (277).** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` must be empty. **If DIRTY — resume disambiguation (Rule 56):** grep the dirty files for THIS plan's own edits (the three new check comments, the new test names). All present and attributable → `git restore` both files and reapply from scratch (**NEVER hand-patch a partial apply**). Any unattributable hunk → **HALT, do NOT restore.**
> ⚠️⚠️ **Then confirm the `(f)` checks are warn-first AT HEAD:** read `plan_lint.py` and verify every `(f)` WARN is a bare `print(...)` that never appends to `results` and never sets `all_passed = False`, and that the return is `0 if all_passed else 1`. **If any `(f)` check has flipped to blocking, HALT and report — the back-compat reasoning changes.**
>
> **Anchor — the insertion point is quoted, not described (Rule 22(a)).** The three checks go **immediately after the `(f)` block, before the results-printing loop.** ⚠️ **Read the file and locate the verbatim line that currently ends `(f)`; insert after it.** **Grep-confirm the edit landed and that no duplicate check label was introduced.** The three checks operate on the **already-extracted `dc_block`** that `(f)` builds — **do not re-extract it.**

**(g) Ledger ordering.** Within `dc_block`, find every line matching a constraint entry of the form *bold C-then-digits followed by an em-dash*. **Extract the integers in order of appearance and WARN if the sequence is not strictly ascending**, naming the first offending pair. ⚠️ **Zero entries is not a failure — skip silently only in that case, and say so in the comment.**

**(h) Stale closing disclaimer.** ⚠️ **This is a CONTRADICTION check, not a keyword check.** Using the lens-result lines `(f)` already parses: if **any** lens line records a result other than a not-run marker, **and** the `**Closing:**` line asserts that no lens has read the artifact, **WARN**. **Neither condition alone is a defect.**

**(i) Halt-routing plan-id coverage.** Collect backtick-quoted **plan ids** (three digits) appearing in the plan's questions region; collect the same from the halt-routing line. **WARN naming any id present in the first set and absent from the second.** ⚠️⚠️ **If no halt-routing line exists, WARN that it is absent — do NOT skip silently.** A silent skip on a missing block is an already-recorded `plan_lint` defect (check `(d)`) and must not be reproduced here.

**All three are WARN-only**, matching §4's deliberate warn-first posture. **None may raise, exit non-zero, or block a deposit.**

> **Task D — PROTECT THE EXISTING TESTS (277 Task C; this plan's walk 1 had dropped it entirely).** Grep `tests/test_plan_lint.py` for the existing `(f)` tests and **run them before and after the edit.** ⚠️ **If any changes behaviour, preserve the test's INTENT rather than weakening the new check** — make the fixture internally consistent and report every fixture edit explicitly. **Do NOT weaken a check to avoid a test edit.**
>
> **Task E — new observe-the-effect tests, one positive and one negative control per check, each also asserting exit 0.**
> ⚠️⚠️ **EMBED REAL-LOG FIXTURES AS STRING LITERALS. DO NOT READ PLANS CROSS-TREE.** **277 rejected cross-tree reads explicitly (its V1): a bellows worktree reading `governance`/`lessons-forge` plans needs absolute paths and breaks if the plans ever move.** ⚠️ **An earlier draft of this plan instructed exactly that cross-tree read — re-adding machinery a shipped sibling had already paid to remove.** **Copy the `## Drafting Cycle` blocks verbatim into the test file as strings.**
> - **(g)** a ledger in ascending order → **no WARN**; one entry out of order → **WARN naming the pair.** ⚠️ **`diagnostic-301.md`'s ledger is ascending (verified at authoring) — embed it as the negative control.**
> - **(h)** lens lines showing results **plus** a closing asserting no lens has read → **WARN**; either alone → **no WARN.**
> - **(i)** a plan id in the questions region absent from the halt-routing line → **WARN naming the id**; full coverage → **no WARN**; **no halt-routing line at all → WARN that it is absent** (never a silent skip).
> - **Degenerate:** an empty block, a block with no ledger entries, a malformed closing → **no crash, no false WARN.**
>
> **Run targeted tests only:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. ⚠️ **Do NOT run the full suite in this step — that is Step 2's job.** Then run `plan_lint` live against a real compliant plan and a deliberately-tripping fixture; **paste the RAW output and `echo $?` = 0 on each.**
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/three-checks-dev-log-2026-08-06.md`
>
> **Deposit the dev log** with the exact before/after lines per check, the warn-first confirmation (exit 0 on all cases), every fixture edit with intent preserved, and the RAW targeted-test and live-run output. **Canonical Python/MCP file-write — NO heredoc. Commit all (NO push).** `#### Prompt Feedback` in `### Ledger Updates`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

**Deposits:**
- `bellows/scripts/plan_lint.py`
- `bellows/tests/test_plan_lint.py`
- `bellows/knowledge/development/three-checks-dev-log-2026-08-06.md`

---

---
---

## STEP 2 — QA

⚠️⚠️ **THE FALSE-POSITIVE MEASUREMENT IS THE POINT OF THIS STEP, NOT A FORMALITY.** A check that fires on most of the corpus is noise wearing a guard's clothes.

> **Task Q0 — RE-PIN THE STATE. The DEV→QA gate is an arbitrary wall-clock window over shared stores, and nothing currently guards it** (⚠️ **`277` does not guard it either — this is a gap the parent shipped with, added here on ACID 1's finding, not cloned**).
>
> 1. ⚠️ **Confirm Step 1's edit is what is being measured:** `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py` — **the most recent commit touching either file must be Step 1's.** **If a foreign commit intervened, HALT and report** — do not measure a file DEV did not ship.
> 2. ⚠️⚠️ **Pin the corpus before measuring it.** `git -C <root> rev-parse HEAD` **for each of the five roots, recorded verbatim in the QA report.** **The `Done/` population moves continuously — a plan closed into it during this very session — so an unpinned count is unreproducible.** **Report the pin beside the count, always.**

1. **Run the full `bellows` test suite.** Record the raw summary line verbatim — **not a summary of it.**
2. ⚠️ **Run `plan_lint` against every plan in all five `knowledge/decisions/Done/` trees, addressed ABSOLUTELY** — `/Users/marklehn/Developer/GitHub/{anvil,bellows,governance,invoice-pulse,lessons-forge}/knowledge/decisions/Done/`. ⚠️⚠️ **Absolute because this step runs inside a bellows worktree and a relative path resolves against the worktree, not the shop root.** Report, **per check**: how many plans it fires on, and the ids. **Report per-root counts including the zeros**, each beside its pinned HEAD from Task Q0.
3. ⚠️⚠️ **State the fire count as a MEASURED number with the command that produced it. This plan deliberately predicts no figure** — a predicted count invites the run to be read as confirming it.
4. ⚠️⚠️ **Confirm WARN-only by the MECHANISM, not the symptom.** An exit-code comparison passes trivially — `all_passed` is set only in the FAIL paths and no `(f)`-family check touches it, **verified at authoring (exit 0 on a WARN-ing plan).** **So assert the mechanism:** grep the three new checks and show **none appends to `results` and none assigns `all_passed`**; then show `echo $?` = 0 on a plan tripping all three. **Both, not just the second.**
5. **Emit the QA Receipt with the canonical Rule 20 self-check block** mandated by `RULE_20_SELF_CHECK_BLOCK.md`, with a verification row per numbered item above and its raw evidence.

**Deposits:**
- `bellows/knowledge/qa/three-checks-qa-report-2026-08-06.md`

---

## Method + boundaries

- ⚠️ **`plan_lint` is a GATE. Every change is additive and WARN-only** — **no existing CHECK's behaviour, wording, or status may change.** **If an existing check needs amending to accommodate these, STOP and report rather than amending it.** ⚠️ **This governs CHECKS, not TESTS. An existing TEST may need a fixture edit — Task D covers that case and requires the test's intent be preserved. The two rules do not conflict; they have different subjects.**
- ⚠️⚠️ **THE HALF-COMPLETE STATE, AND WHY IT IS SAFE — STATED, NOT LEFT ACCIDENTAL.** If Step 1 commits and Step 2 never runs, **three checks with unmeasured false-positive load are live in the gate for every plan the shop lints.** **That is acceptable for exactly one reason: they are WARN-only and cannot block a deposit or change an exit code.** ⚠️ **If any check is ever made blocking, this half-state stops being safe and the plan must be re-scheduled so the measurement precedes the flip.** **§2.5 asks whether the invariant closing each gap is stated or accidental; this one is now stated.**
- **Absolute paths:** `/Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py`, `/Users/marklehn/Developer/GitHub/bellows/tests/test_plan_lint.py`.
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim; a non-`-F` pattern can exit 1 silently on a present line).
- ⚠️ **Agents run `git add` and `git commit` only. No `git push`.**
- Where a step cannot be completed as written, **HALT and report** — do not substitute a narrower change.

---

## Drafting Cycle

**This section is a RECORD, not instructions.** Gate-matching strings are described here, never quoted.

**Tier:** T2 — **computed, trigger fired: T-6.** ⚠️⚠️ **`plan_lint` IS a gate, and T-6 fires on editing "doctrine, the template, gates, or specialist contracts."** **The verb test that spared the three diagnostics does not spare this plan: it EDITS the gate rather than mapping one.** **T-1 also fires** (source plus tests). ⚠️ **T-8 RESOLVED AT WALK 1 — IT DOES NOT FIRE.** Two direct parents exist: **`executable-140`** (a WARN-only `plan_lint` check addition) and **`executable-277`** (a `plan_lint` §4 drafting-cycle refinement, and the **newest same-class**). **This is a structure-for-structure clone of 277.** ⚠️⚠️ **An earlier draft left T-8 "open" and drafted anyway — a deferred obligation, and C11 says a deferred finding is a fold not yet paid for. The §2.6 diff against 277 was run at walk 1 and found EIGHT pieces of dropped machinery, including one 277 had explicitly removed.** T-2, T-3, T-4, T-5 do not fire.

⚠️ **THE ESCALATION IS COMPUTED, NOT CHOSEN — and it carries a known problem.** T2 requires a cold panel, and §2.6 gates the panel on a walk going dry, **a condition four consecutive plans failed to reach.** ⚠️⚠️ **This plan will therefore face the same judged-stop ending, and its `plan_lint` WARN will be earned. That is not a reason to declare a lower tier.** **Recorded so the tier is not quietly dropped later.**

**Walks:** 1 (lenses 1–4 over every region). **ACID has NOT run — separate phase.**

- Weak spots:          w1 2 raised (1.4 **Rule 22(a) violated — the plan tells the agent to FIND the insertion point instead of quoting a verbatim anchor**; QA item 4's test is vacuous as written).
- Destruction:         w1 dry — ⚠️ **the concern was checked, not assumed: nothing in the repo parses `plan_lint`'s output, so new WARN lines cannot break a consumer.**
- Vulnerabilities:     w1 1 raised (3.4 **two different output mechanisms coexist in one file and the plan names neither** — choosing wrongly changes the exit code).
- Integration-record:  w1 2 raised (4.1 **T-8 was left OPEN and two direct parents exist**, so §2.6's diff-against-the-newest obligation is unmet; the step-heading case costs lint coverage).
- ACID:                **a1 5 raised, NOT DRY** (5.3 the false-positive measurement runs over a LIVE corpus with no HEAD pin; the DEV→QA window over `plan_lint.py` itself is unguarded; the five roots are named but not absolute; 5.1 the half-complete state leaves unmeasured checks live in the gate on an ACCIDENTAL invariant; 5.2 a near-collision between "no check's behaviour changes" and the instruction for when a TEST's does).

**[ACID 1]** ⚠️⚠️ **ISOLATION WAS THE LENS THAT MATTERED, AND IT IS THE ONE EVERY DIAGNOSTIC THIS SESSION SKIPPED.** §2.5's (5.3) is structurally empty for a single-step read-only plan — all three diagnostics logged it as such. **This is the session's first two-step plan, so the lens has content for the first time, and it produced three of the five findings.**

⚠️ **ONE WINDOW IS MINE, ONE IS THE PARENT'S TOO.** The corpus-wide false-positive measurement is an addition this plan makes that `277` never had — **so its unpinned-population window is newly created, not inherited.** But the **DEV→QA window over `plan_lint.py` itself is unguarded in `277` as well** — verified, its QA step carries no porcelain or HEAD check. ⚠️ **That one is not clone-drift; it is a gap the parent shipped with, and finding it is what the lens is for.**

⚠️ **WRITTEN BEFORE ANY FOLD, per §2.7 attestation (`:90`).**

⚠️⚠️ **THREE CANDIDATES DISPROVED BY CHECKING, and one of them makes a core claim TRUE rather than merely intended:** `all_passed` is set only in FAIL paths (`:48`–`:136`) while every §4 drafting-cycle check prints a bare WARN and never touches it — **verified empirically, exit=0 on a WARN-ing plan** — so **"WARN-only" is architecturally true, not aspirational.** Also disproved: that a `plan_lint` output consumer might break (there is none), and that the deposit directories might not exist (both do).

**Panel status:** none run.

**Conflicts:** ⚠️ **Constraints are appended at the END of this block as they are earned, never inserted above an existing entry.**
- **C1** — ⚠️⚠️ **an executable is diffed against the newest same-class plan BEFORE drafting, not after.** This draft left T-8 open, drafted anyway, and the walk-1 diff against `277` found **eight** pieces of dropped machinery: the bootstrap prompt, the CEO-context and how-to-run sections, uppercase step headings, the A0 cleanliness-and-warn-first precondition, verbatim edit anchors, a `**Scope:**` block per step, the protect-existing-tests task, and the no-heredoc / no-push / STOP conventions. (walk 1)
- **C2** — ⚠️⚠️ **ask §2.6's INVERSE question, not only "what did the clone drop".** `277` **explicitly removed** cross-tree fixture reads in favour of embedded string literals, with its reason recorded (a bellows worktree reading `governance`/`lessons-forge` plans is brittle). **This draft instructed exactly that cross-tree read — re-adding machinery a shipped sibling had already paid to remove.** (walk 1)
- **C3** — **assert a guarantee by its MECHANISM, not its symptom.** "Exit code unchanged" passes trivially because no `(f)`-family check touches `all_passed`; the real assertion is that the new checks never append to `results` and never assign it. (walk 1)
- **C4** — ⚠️⚠️ **A MULTI-STEP PLAN MUST RE-PIN AT EVERY VERDICT GATE, NOT ONLY AT THE START.** A gate is an arbitrary wall-clock window over shared stores: the file DEV shipped can be modified before QA reads it, and a corpus measured at QA can have moved since DEV. **Pin both — the last commit touching the edited files, and `rev-parse HEAD` per corpus root — and report the pin beside every number.** ⚠️ **`277` shipped without this; it is not clone-drift but a gap the lens found.** (ACID 1)
- **C5** — ⚠️ **Isolation is empty for a single-step read-only plan and LOADED for a multi-step one.** Every diagnostic this session logged (5.3) as structurally empty and was right to. **The first two-step plan produced three isolation findings out of five.** **Do not carry the "structurally empty" habit across plan classes.** (ACID 1)

**Closing:** ⚠️ **NOT REACHED — and deliberately not written as one.** **State of play: walk 1 · culmination · ACID 1 · culmination — complete in that order. ACID 1 was NOT dry**, so §2's closing condition is **UNMET and NOT CLAIMED.**

⚠️⚠️ **THIS LINE HAS NOW GONE STALE TWICE INSIDE ONE PLAN — the FIFTH occurrence of the class across four plans.** The authoring form (*"no lens has read this artifact"*) was caught at the walk-1 culmination; the replacement (*"ACID has NOT run"*) went stale the moment ACID ran and was caught by the next culmination's sweep. ⚠️ **Both times by a manual sweep, in the plan whose check (h) exists to catch exactly this. The class does not decay with attention — it decays with edits, and only a mechanism tracks edits.** **This is the single strongest argument in the plan for its own check (h).**
