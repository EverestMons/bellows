# Executable: plan_lint §4 — two in-place check fixes (FORWARD rows 27 + 28)

**Type:** Executable
**Project:** bellows
**Depends on:** **executable-303** (bellows, Done — the CLONE ORIGIN whose §4 check machinery this carries; restored to the header after the cut dropped it), **executable-286** (bellows, Done — FIRST hardened both of these checks; its fold-side fence, its message-text pin and its deliberate negation bound all bind this plan), **executable-324** (bellows, Done — newest same-class; its QA machinery is carried here and its coordination clause names this plan), **executable-304** (bellows, Done — removed check (i) at 8/11 false positives; the precedent that cut this plan's third change). DRAFTING_CYCLE at v1.8.
**Created:** 2026-08-09
**Author:** Planner
**Slug:** `lint-s4-hardening-2026-08-09` (stable across any crash-redo re-deposit — the A0 re-entry key and the Rule 20 `plan_slug`)
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T2
**qa_steps:** 2
**Test Scope:** targeted — this plan changes two regexes in one file; Step 1 runs the lint tests only (`-k "plan_lint or lint"`, baseline **97 passed**, measured 2026-08-09) and Step 2 runs the full bellows suite, where a suite-wide regression is the thing being measured. Per the DEV-step lesson the full suite is deliberately NOT in Step 1.

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim. **Re-read `id_sequence` at deposit.**

---

## Why this exists

Two `plan_lint` §4 checks are hardened and still defeated. **Both defects were reproduced by construction against the live file at authoring (2026-08-09), not inherited from the register rows:**

- **Row 27 — the T2 cold-panel check matches an OPENING, never CONTENT.** A block whose panel line is `**Cold panel (T2):**` with nothing after the colon produces **no WARN**. Positive control: deleting the line entirely **does** WARN.
- **Row 28 — the closing check's negation strip requires the negator ADJACENT to `dry`.** A last lens line reading `- ACID: a1 2 folded; not yet dry.` produces **no WARN**. Positive controls: `a1 2 folded.` WARNs, and adjacent `not dry.` WARNs — 286's fix is intact and defeated only by the intervening word.

⚠️ **Both are SECOND hardenings.** Plan 286 shipped "structurally-anchored cold-panel" and "negation-aware closing status" as the first fixes. **286 was not careless — it bounded the negation deliberately and fenced the fold side, and this plan must respect both** (see M3).

⛔ **A third change was designed here and CUT at the panel (CEO decision 2026-08-09):** a new check for FORWARD row 25 (warn when a plan emits warnings but declares no expected lint state). Measured firing population **1379/1390 = 99.2%** (as of 2026-08-09; the denominator drifts — see the sweep row) against check (i)'s deletion at **eleven** firings. **Row 25 is RETURNED to the register with that measurement attached** (QA ledger, row 2) so the next attempt starts from it. **Nothing here implements it.**

## Scope

- **Edits exactly TWO files:** `scripts/plan_lint.py` and `tests/test_plan_lint.py`. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
- **Both changes are IN-PLACE edits to existing checks. NO new check label is added.** An agent writing a new check, an expectation marker, or a WARN counter has left this plan → **HALT**.
- **WARN-only invariant (140/303):** both checks stay bare `print(...)` — never appending to `results`, never assigning `all_passed`, never raising.
- ⚠️ **A §4 DOCTRINE EDIT IS OWED AND IS EXPLICITLY DEFERRED** (discharged by SAYING). ⚠️ **Citation corrected at panel seat B:** §6's pair-or-defer-and-say licenses deferring the GATE when DOCTRINE moves — this is the INVERSE case, so the governing clause is `## When this file changes` and the shipped precedent is gate-first-then-version-bump (v1.2 documented 286's four fixes after the fact; v1.5 records that 306 shipped the gate side first). §4 does not merely mandate these checks, it DESCRIBES their mechanics: it calls the panel check "line-anchored" and enumerates the strip as `not dry` / `no dry` / `never dry`. Both descriptions become understatements. **The update is a governance-root edit and out of scope for a bellows plan; it rides out as QA ledger row 1.** ⚠️ **An agent must NOT "fix" this by editing `DRAFTING_CYCLE.md` — that is a HALT.**
- ⚠️ **VERDICT-WINDOW POSTURE — this ships EXECUTABLE CODE.** From Step 1's commit until close, the modified `plan_lint` governs every conformance pass in the shop. A Step-2 HALT leaves it live **by design; that is NOT a rollback instruction.** Never `git restore`/`revert` on a HALT — rollback is a CEO decision. This is why the WARN-only invariant and the sweep-diff are load-bearing: a `plan_lint` that crashed or blocked would break every drafting cycle in the window.
- ⚠️ **SIBLING COORDINATION:** 324 names this plan and requires whichever runs second to re-derive every anchor at DEV time. **324 shipped first (`9c06524`), so this is the second** — every anchor re-derived at DEV; a moved anchor is HALT-and-report, never a guess.
- **No LESSONS.md touch. No FORWARD hand-edit** — the two ledger rows go through the channel the daemon appends; nobody types in the register. Rows 27/28 close by wrap reconciliation.

### ⚠️ Environment facts — observed, not predicted
1. `grep` is a ugrep shim: **`-F` for every literal**, **`-e` for any pattern that could begin with `-`** (a dash-leading pattern parses as an OPTION — exit 2, empty stdout, which a read-the-count rule turns into a false answer).
2. A zero-match `grep -c` prints `0` and exits **1** — the printed count is the assertion.
3. Shell state does NOT persist between commands — assign and use in the same invocation.
4. **`plan_lint` returns 1 on any FAIL, not only on a crash** — 668/1390 corpus plans exit nonzero on ordinary FAILs (measured). **Exit status cannot detect a crash; a traceback on STDERR is the only discriminator.**

---

## The two changes — behaviour specified, code composed by the DEV

**M2 — row 27: the cold-panel check must require CONTENT, not just an opening.** A line carrying only its opening (with or without a trailing colon) is HOLLOW and must WARN exactly as an absent line does.

⚠️⚠️ **The live pattern has TWO alternatives and BOTH must be specified, or the fix ships half-applied.** `^\*\*cold[\s-]+panel` is the bold-label branch; `^-\s*cold[\s-]` matches ANY dash line opening `- Cold …`.

⚠️⚠️ **RETRACTION — an earlier fold of this plan asserted the dash branch matches cold LENS-RESULT lines but "NOT a `- Cold panel` label". THAT IS FALSE and is corrected here (panel seat B, measured).** `executable-306` carries **zero** `**Cold panel` lines and its T2 check is satisfied SOLELY by `- Cold panel (§2.6), seat 1 (Lens 1 cold): …` — a `- Cold panel` label on the dash branch, the dominant real form. 286's Task D says the branch accepts **BOTH** structural forms; it never excluded the panel label. The retracted claim would have left a DEV with no rule for the most common line in the corpus.

**Hollowness, per branch:** for `**Cold panel…`, the label plus any parenthetical and an OPTIONAL colon; for the dash branch, the `- Cold <word…>` label plus any parenthetical and colon — **whatever follows `- Cold` is the label, whether that is `panel` or a lens name.** Content is what remains after it. **BOTH branches get tests, and the dash tests cover BOTH `- Cold panel (§2.6), …` and `- Cold weak-spots: …`.**

⚠️⚠️ **THE COLON IS OPTIONAL AND THAT IS LOAD-BEARING — the corpus contains colonless panel lines** (`executable-277`: `**Cold panel materially changed the draft (CB1 HIGH) → …**`). Two spec-conformant openers differ on exactly these, one false-WARNing them, and **neither the prescribed tests nor the sweep discriminates** because those plans also carry a satisfying line elsewhere. **A colonless real-corpus panel line is a REQUIRED negative control in Task E.**

⚠️ **SCOPE OF M2, STATED HONESTLY — it does not close the whole class.** The check is an existence-OR across the block, so "require content" means SOME cold line has content. **A hollow `**Cold panel (T2):**` sitting beside substantive `- Cold <lens>:` lines still produces no WARN** — the shape plans 274/306/307/309 actually use. That residue is ACCEPTED here (closing it means restructuring the check from an OR into a per-line rule, which is a different change with its own blast radius) — but it is accepted **explicitly**, and Task E carries the combined case as a documented no-WARN expectation so the boundary is recorded rather than discovered later.

**M3 — row 28: the negation strip must tolerate a BOUNDED gap. ⚠️ THIS REVERSES A PRICED DECISION.**

⚠️⚠️ **286 did not miss the gap — it chose the narrow window and recorded why:** *"The negation window is the IMMEDIATELY preceding word only … That under-detection is accepted: warn-first means a missed reminder is soft, whereas a wider window would start swallowing legitimate dry closes."* The §2.6 inverse question fires on M3 itself; this is its answer. **What is new is that 286 priced *a wider window* generically and never priced a gap of exactly one word**, which is all three recorded defect forms need. Measured across gap widths on the live corpus and the shipped fixtures:

| gap | `not yet dry` / `no longer dry` / `never quite dry` | a legitimate dry close (`…w2 no further findings so dry`) |
|---|---|---|
| N=0 (286's shipped bound) | missed | safe |
| **N=1 — THIS PLAN** | **all three caught** | **safe** |
| N≥3 | caught | ⛔ **FALSE WARN — 286's predicted failure, reproduced** |

**PIN: N = 1, ceiling N = 2. The DEV may not exceed it.** Gap tolerance is licensed nowhere else in the check.

⚠️⚠️ **THE FOLD SIDE IS FENCED — CHANGE NOTHING ABOUT IT** (286's constraint). `has_fold` stays the plain substring test `'fold' in line`. **Do not word-tokenise, stem, enumerate, or "tidy" it while editing the adjacent line.** 286 proved by execution that a `{fold, folded}` word-set drops the plural `folds` and `\bfold\w*` drops `refolded` — both are UNCHARTERED RELAXATIONS. ⚠️ **This is the plan's most dangerous edit site: a fold-side relaxation is invisible to the tests, invisible to the sweep-diff (which is expected EMPTY), and invisible to every QA row (they look for the check firing MORE).** ⚠️⚠️ **THERE ARE TWO FOLD-SIDE TESTS AND THE FENCE COVERS BOTH** (panel seat C): the primary `has_fold = 'fold' in ll_lower`, AND the legacy fallback `if 'fold' in closing_text and 'dry' not in closing_text:` — which `DRAFTING_CYCLE.md:152` documents as part of the same check and which fires when no lens line parses. **A DEV "tidying" only the fallback passes the tests, the sweep-diff and the QA fold-side row, because none of them names it.** **Quote BOTH lines before and after and prove both byte-identical.**

⚠️ **PIN THE WARN MESSAGE TEXT** (286's CB2). ⚠️ **The count decomposes, and an earlier draft priced it wrongly — corrected here:** the literal `dry lens pass` occurs **14×** in `tests/test_plan_lint.py`, but that is **6 positive asserts + 4 NEGATIVE asserts + 4 fixture prose** (measured). A reword fails the 6 — which Task D would misread as "a pre-existing test changed behaviour" and invite fixture edits, the disguise path 286 named — **and silently turns the 4 `not in` asserts VACUOUSLY TRUE, which is the opposite direction and the one nothing would catch.** **The real pin is in the source, not the tests: `grep -c -F -e "dry lens pass" scripts/plan_lint.py` must remain exactly 2 (the two print sites, measured).** The message is unchanged.

⚠️ **MEASURED BLAST RADIUS OF BOTH CHANGES: ZERO.** M2 changes the output of no plan in the 1390-plan corpus (no hollow panel line exists); M3 changes none at any gap width N≤4, including the seven never-editable `REAL_LOG_*` fixtures. **Both are correct-going-forward fixes with no current corpus signal** — which is exactly why the proofs below are structural rather than statistical.

---

## Conflict Ledger

- **C1** — both checks stay WARN-only: bare `print(...)`, never `results`, never `all_passed`, never raising. Verified by MECHANISM (grep), not by exit code — an exit-code check passes trivially.
- **C2** — every anchor is QUOTED from the live file, never a line number; re-derived at DEV (the 324 coordination clause).
- **C3** — **BOTH fold-side tests** (`has_fold` and the legacy `closing_text` fallback) and the WARN message text are BYTE-IDENTICAL after the edit. ⚠️ Two sites, not one.
- **C4** — existing tests are PROTECTED: run before and after; a fixture edit preserves the test's INTENT and is reported with its reason. **Never weaken a check to avoid editing a test.**
- **C5** — test fixtures are EMBEDDED string literals at **column 0** (306's self-fire lesson). **No cross-tree plan reads** (277's V1).
- **C6** — row 25 is OUT OF SCOPE: no new check, no expectation marker, no WARN counter. Building one → HALT.
- **C7** — targeted tests in Step 1; full suite in Step 2 only.
- **C8** — SCHEDULE: **A0(0) already-landed probe, FIRST and unconditional** → A0(clean/dirty state) → A0(b) PRE_EDIT_BLOB pin → A1(warn-first at HEAD) → M2/M3 → mechanical fold-side gate → tests → targeted run → live run → commit deposits as the final action. ⚠️ **A0(0) precedes the clean/dirty split deliberately** — see its own note.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

Step 1 (DEV) → verdict gate → Step 2 (QA). `pause_for_verdict: always`. No step renames this file.

⚠️ **HALT ROUTING — if any input is missing or unreadable, HALT the step that needs it and NAME it, never improvise.** **Step 1 reads** this plan, `scripts/plan_lint.py`, `tests/test_plan_lint.py`, and `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md` §3/§4 (ABSOLUTE path — it lives at the shop root, OUTSIDE this worktree). **Step 2 reads** this plan, the Step-1 dev log, both edited files, the five `Done/` trees (absolute paths), and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`.

---
---

## STEP 1 — DEV

---

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py`; read `DRAFTING_CYCLE.md` §3/§4 at the ABSOLUTE path for the authoritative behaviour. **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
>  ⚠️⚠️ **TASK A0(0) — HAS THE WORK ALREADY LANDED? RUN THIS FIRST, BEFORE THE CLEAN/DIRTY SPLIT AND UNCONDITIONALLY.** Probe `scripts/plan_lint.py` for the M2 content-check and the M3 bounded-gap negation, using markers derived from the live file. **Either present → a prior dispatch COMMITTED and this is a resume, not a fresh run → HALT and report WITH PAYLOAD:** the matching lines quoted, `git -C /Users/marklehn/Developer/GitHub/bellows log -3 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py`, whether a Step-1 dev log exists, and the targeted lint suite result — so the CEO can see whether the prior run left the checks WORKING or half-applied.
> ⚠️ **The ordering is load-bearing (panel seat C):** an earlier fold placed this probe on the CLEAN branch only, where it could NEVER fire in the state it exists for. The likeliest crash-redo state is *committed edits plus a partial re-edit left uncommitted* — a DIRTY tree — and the dirty branch below routes to `git restore` + reapply. **`git restore` restores to HEAD, which on that path ALREADY CONTAINS M2/M3**, so the DEV would re-apply over committed edits: verbatim the double-apply this probe exists to prevent.
>
> **⚠️ TASK A0 — PRE-EDIT STATE.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py gates.py` must be EMPTY. ⚠️ **`gates.py` is in the pathspec deliberately:** the `(f)` block is gated on `gates._parse_plan_header` and the corpus is fence-stripped by `gates.strip_fenced_code_blocks`, so a gates change alters which plans enter the block at all — any gates dirt here is foreign by definition.
> **If DIRTY:** ⚠️⚠️ **a `git restore` is licensed ONLY by FULL HUNK ATTRIBUTION via `git diff` enumeration — NEVER by a presence-grep**, which cannot prove the absence of a foreign hunk it would destroy (324's C2, restoring 306's). Every hunk attributable to this plan's own edits → restore both files and reapply from scratch, **never hand-patch a partial apply**. **A single unattributable hunk → HALT, do NOT restore** — a parallel terminal is live and restore destroys uncommitted foreign work with no record.
>
>
> **⚠️ TASK A0(b) — PIN THE PRE-EDIT BLOB, BEFORE THE FIRST KEYSTROKE.** `git -C /Users/marklehn/Developer/GitHub/bellows hash-object scripts/plan_lint.py` → record verbatim in the dev log as **PRE_EDIT_BLOB** and name it in the Output Receipt. ⚠️ **Step 2's sweep-diff cannot run without it and cannot re-derive it** (`<Step-1-commit>^` goes self-referential if this step makes two commits touching the file).
>
> **⚠️ TASK A1 — CONFIRM WARN-FIRST AT HEAD BEFORE EDITING.** Verify every `(f)`-family WARN is a bare `print(...)` touching neither `results` nor `all_passed`, and that the return is `0 if all_passed else 1`. **If any has flipped to blocking, HALT — C1's reasoning no longer holds.**
>
> **TASKS M2 / M3 — implement the two behaviours specified above.** ⚠️ **Anchors are QUOTED from the live file (C2) and re-derived now** — a moved anchor is HALT-and-report. Quote each before/after pair in the dev log. The checks operate on the already-extracted `dc_block` — **do not re-extract it.** ⚠️ **The fold-side line and the WARN message text are byte-identical afterward (C3) — quote both before and after and prove it.**
>
> **TASK D — PROTECT THE EXISTING TESTS (C4).** Run the lint tests BEFORE the edit (baseline 97 passed) and after. Any pre-existing test changing behaviour → preserve its INTENT, report every fixture edit with its reason. **Do NOT weaken a check to avoid a test edit.**
>
> **TASK E — NEW OBSERVE-THE-EFFECT TESTS: a positive and a negative control per change, each asserting exit 0.** Fixtures are EMBEDDED string literals at column 0 (C5).
> - **M2, BOTH BRANCHES:** hollow `**Cold panel (T2):**` → WARN; substantive panel line naming seats/yields → no WARN; hollow `- Cold weak-spots:` → WARN; substantive `- Cold weak-spots: 9 findings, 2 HIGH` → no WARN; ⚠️ **AND the dominant real corpus form, which the retraction above exists to rescue and which had NO case: substantive `- Cold panel (§2.6), seat 1 (Lens 1 cold): 11 findings` → no WARN** (this is `executable-306`'s SOLE satisfying line), plus its hollow twin `- Cold panel (§2.6):` → WARN. ⚠️ **Disambiguation the DEV needs:** "the label" is `- Cold` plus the following WORD and any parenthetical — not the rest of the line; under the rest-of-line reading every dash cold line is hollow and 306 false-WARNs; line absent entirely → WARN (the unchanged-behaviour regression control).
> - **M3:** `not yet dry` / `no longer dry` / `never quite dry` on a fold-bearing last lens line → WARN; **a legitimate dry close carrying an unrelated negator at distance (`w1 2 folded, w2 no further findings so dry`) → NO WARN** — this is the bound control and it is what fails at N≥3, so it is not decorative; adjacent `not dry` → WARN (286's behaviour, unchanged).
> - **M2, THE TWO CASES THE PROSE ABOVE DECLARES MANDATORY** (a prior fold stated them and did not add them here): **(a) colonless negative control** — a real-corpus form such as `**Cold panel materially changed the draft (CB1 HIGH) → …**` as the block's ONLY cold line → **no WARN**; **(b) the accepted-residue case** — a hollow `**Cold panel (T2):**` sitting beside substantive `- Cold <lens>:` lines → **no WARN**, asserted as the DOCUMENTED boundary of the existence-OR, not as a defect.
> - **Degenerate:** empty block, no lens lines, malformed closing, T0/T1 plans → no crash, no false WARN.
> - ⚠️ **On "each asserting exit 0": a fixture can exit 1 for reasons unrelated to §4** — e.g. a declared `**qa_steps:** 2` with no QA-labeled step trips `FAIL: (c)`. **Fix the FIXTURE, never the check**, and say which header line you removed.
>
> ⚠️⚠️ **MECHANICAL FOLD-SIDE GATE, IN THIS STEP — the plan's most dangerous edit must not rest on DEV self-report alone.** `git -C /Users/marklehn/Developer/GitHub/bellows diff -U0 scripts/plan_lint.py | grep -F -e "'fold' in"` must print **nothing**. ⚠️ Step 1 can commit a relaxed fold side and pause; Step 2's row 4 is the only other check and may never run. This gate costs one command and removes that member from the half-completed state set.
>
> **RUN TARGETED TESTS ONLY:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. ⚠️ **Do NOT run the full suite here (C7).** Then run `plan_lint` live against a real `Done/` plan and against each tripping fixture — ⚠️ **materialize the fixtures into a fresh `mktemp -d` OUTSIDE every git tree** (Step 2 says this explicitly and Step 1 had lost it; fixtures written under `bellows/` survive as untracked residue and dirty the next plan's A0, and this plan's own Q0 status check) — and **record each fixture's placement path in the dev log beside its source text**; **paste RAW output and `echo $?` = 0 on every one.**
>
> **Output Receipt required** — **PRE_EDIT_BLOB**, ⚠️ **the full SOURCE TEXT of every tripping fixture pasted verbatim** (QA row 5 re-materializes them and cannot do so from output alone; C5 makes them string literals inside the test file, so they exist nowhere else as standalone artifacts), the before/after pair per change, **BOTH fold-side lines and the WARN message quoted before and after as byte-identical** (two fold-side sites, not one — C3), targeted-test counts before and after, every fixture edit with its reason, and the RAW live-run output with exit codes. **NO heredoc — use your file-write tool.** End with `### Ledger Updates` and `#### Prompt Feedback`.
>
> **⚠️ FINAL ACTION — COMMIT YOUR DEPOSITS**, pathspec on the COMMIT naming exactly the Scope files, then assert `git show --name-only --format= HEAD` prints exactly them. **Commit only — NO push.**
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/lint-s4-hardening-dev-log-2026-08-09.md`
>
> **Deposits:**
> - `bellows/scripts/plan_lint.py`
> - `bellows/tests/test_plan_lint.py`
> - `bellows/knowledge/development/lint-s4-hardening-dev-log-2026-08-09.md`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

## STEP 2 — QA

---

⚠️⚠️ **THE RISK HERE IS A SILENT RELAXATION, NOT NOISE.** Both changes make existing checks fire MORE, and their measured corpus firing population is **ZERO** — so no corpus specimen can reveal a regression. **The sweep-diff and the fold-side byte-comparison stand in for a signal that does not exist.**

> **FIRST — Deliverable Verification (Rule 8 / Rule 17).** Open the Step-1 dev log, confirm its Output Receipt is Complete, verify every file it claims exists and carries the described change. Table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ → report and HALT; make no edits yourself.
>
> **Task Q0 — RE-PIN BEFORE MEASURING.** `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py gates.py knowledge/development/lint-s4-hardening-dev-log-2026-08-09.md` — the newest commit touching any of them must be Step 1's; **a foreign commit intervening → HALT.**
> ⚠️⚠️ **AND `git … status --porcelain --` THE SAME FOUR PATHS MUST BE EMPTY — restored at panel seat C, which found the cut had deleted the status check while KEEPING the prose that justifies it.** The rationale is a *status* rationale: the dev log is the sole carrier of PRE_EDIT_BLOB, so an UNCOMMITTED verdict-window edit to it (or to the test file) feeds this step a baseline nobody wrote — and `log` cannot see uncommitted work. Row 3's blob assertion covers `scripts/plan_lint.py` only, so without this check that edit is invisible to every row. Step 1 has this guard; its sibling had lost it.
> ⚠️⚠️ **PIN THE FIVE CORPUS ROOTS AND BOOKEND THE SWEEP — also restored at seat C, and the cut's subsumption test checked the WRONG PROPERTY.** The cut removed the per-root `rev-parse HEAD` pins after verifying "no surviving row reads per-root fire counts" — true, but **the pins never guarded fire counts; they guarded CORPUS STABILITY ACROSS THE SWEEP**, and the sweep is this plan's central proof. `git -C <root> rev-parse HEAD` for each of the five roots BEFORE the sweep, recorded verbatim, and **re-run all five immediately AFTER it**. ⚠️ **This shop files plans into `Done/` mid-session**, so a single plan landing between the two passes yields a non-empty diff — and row 3 says any changed line is a HALT. **A pin delta is concurrent activity: NAME it and re-run the sweep; never force-reconcile it, and never read it as a defect in the edit.** Governance has no `.git`, so its pin is the shop-root HEAD by design.
>
> **MANDATORY — Rule 20 self-check (canonical block, Checklist #4 — the exact template, NOT a paraphrase)** from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (ABSOLUTE path). **All FOUR placeholders — a partial enumeration reads as complete and the block `sys.exit(1)`s on the one you omit:** `plan_slug`: `lint-s4-hardening-2026-08-09`; **`qa_report_path`: `<your-tree-abs>/knowledge/qa/lint-s4-hardening-qa-2026-08-09.md`** (⚠️ omitted by an earlier draft — a missing/unwritten report is `CRITICAL: QA report not found`, which makes the PASSED line below unsatisfiable on a CORRECT run); `evidence_dir` derived from `pwd`, NOT hardcoded; `required_evidence_files`: `[targeted-tests.txt, full-suite.txt, sweep-diff.txt]`. Deposit **all three** BEFORE running the block — it `sys.exit(1)`s on any missing name. **Include the block's literal stdout: the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must both appear byte-exact (em-dash U+2014).**
>
> ⚠️ **REPORT STRUCTURE — the verification section never closes on its own: immediately after the verification table write exactly `## Evidence and Narrative`**, keeping the Rule 20 stdout, the Output Receipt and `### Ledger Updates` at `##`-level.
>
> **Evidence rule:** RAW command output, never a summary.
>
> **Verification table, one row per claim (HALT on any FAIL):**
>
> **1. FULL SUITE.** Run the whole bellows suite; record the raw summary line VERBATIM. → `full-suite.txt`
> **2. TARGETED SUITE.** Re-run the lint tests; confirm the count rose by the new tests and that no pre-existing test was weakened — cross-check against the dev log's fixture-edit list and its reasons. → `targeted-tests.txt`
> **3. ⚠️⚠️ SWEEP-DIFF — the plan's central proof, and the EXPECTED RESULT IS EMPTY.**
> - Materialize the pre-edit lint: **`git cat-file -p <PRE_EDIT_BLOB> > $S/plan_lint.py`** where `S=$(mktemp -d)` is created and used in the SAME invocation. ⚠️ **NOT `git show <blob>:path`, which is FATAL** — a blob is not a tree and cannot be path-addressed. ⚠️ **A fresh `mktemp -d`, never bare `/tmp`**, where a stale `gates.py` would shadow the import (script-dir precedes PYTHONPATH). Invoke with `PYTHONPATH=/Users/marklehn/Developer/GitHub/bellows`.
> - Run BOTH versions over every plan in the five `Done/` trees, **glob pinned to `Done/*.md`** (invoice-pulse's `Done/files.zip` crashes the lint — 306's finding), addressed ABSOLUTELY (`/Users/marklehn/Developer/GitHub/{anvil,bellows,governance,invoice-pulse,lessons-forge}/knowledge/decisions/Done/`), both under `PLAN_LINT_UNCAP=1` so no `(+K more)` tail truncates, with ONLY lint stdout entering the diffed streams.
> - ⚠️ **Capture STDERR per file. A traceback on stderr is a CRASH and a HALT; a nonzero exit with clean stderr is an ordinary FAIL and is recorded, not halted** (668/1390 exit nonzero on ordinary FAILs — exit status cannot discriminate).
> - ⚠️⚠️ **A correct run and a stale-tree run produce the SAME empty diff, so the blob pin is the ONLY thing separating them:** `git hash-object scripts/plan_lint.py` must equal the blob in Step 1's commit AND must DIFFER from PRE_EDIT_BLOB. **PASS = empty diff AND both blob assertions hold. Any changed or lost line, of any label → HALT.**
> - ⚠️⚠️ **`sweep-diff.txt` MUST BE A RECEIPT, NOT THE BARE DIFF STREAM — an empty file FAILS the Rule 20 block and inverts this gate.** The canonical block treats a zero-byte evidence file as `CRITICAL: evidence file empty` and `sys.exit(1)`s, so writing the expected-empty diff verbatim makes a CORRECT run fail and a defective run (non-empty diff) pass the file check. **Write a receipt containing: both blob hashes, `files_compared=<N>` per root and in total, the per-file stderr survey, and the literal line `DIFF: none` (or the diff body when non-empty).** → `sweep-diff.txt`
> - ⚠️ **ASSERT COVERAGE, NOT JUST EQUALITY.** An empty diff is also what "zero files compared" produces — a mistyped root, a renamed `Done/`, or a loop dying at file 3 all yield it, and the blob pins guard tree staleness, not iteration. **Re-derive the corpus count in the same invocation (`ls -1 <the five Done/>/*.md | wc -l`) and assert `files_compared` equals it.** Measured at authoring: **1390** — ⚠️⚠️ **and it is ALREADY 1391: the corpus drifted DURING this plan's own panel when this session closed plan 330 into `Done/`.** That is not a defect in the number; it is the live proof of why the root pins and the sweep bookend exist. **Never compare against the literal 1390 — re-derive the count in the same invocation and assert `files_compared` against THAT.** A figure pinned in plan text is a measurement with a timestamp, not a constant.
> - ⚠️ **PROVE THE IMPORT ISOLATION, because the `mktemp -d` guard is off by one directory.** `plan_lint.py` computes `BELLOWS_ROOT = Path(__file__).parent.parent` and inserts it at `sys.path[0]` — for `$S/plan_lint.py` that resolves to **`$TMPDIR`, which is shared and long-lived, not the fresh dir `mktemp` made.** A stale `gates.py` there shadows the real one ahead of PYTHONPATH, and if BOTH streams run from scratch dirs they import the same wrong `gates` and the diff is empty — a spurious PASS on this very proof. **Print `gates.__file__` for each stream into the receipt and assert both resolve under `/Users/marklehn/Developer/GitHub/bellows`.**
> **4. FOLD-SIDE AND MESSAGE INTEGRITY (C3) — the relaxation the sweep-diff cannot see.** Independently of the dev log, diff the pre-edit and post-edit `plan_lint.py` and confirm **BOTH fold-side tests** (`has_fold` and the legacy `closing_text` fallback) and the WARN message string are **byte-identical**, and that **`grep -c -F -e "dry lens pass" scripts/plan_lint.py` returns exactly 2** — the two print sites, which is where the message actually lives. ⚠️⚠️ **Do NOT assert the test-file count equals 14.** Task E's mandated new tests ADD occurrences in the file's own house style (measured: authoring the ten prescribed tests takes it to ~34), so a `=14` post-condition **fails a correct run** and can only be satisfied by omitting the message assertions the new tests exist to make. **Assert `≥ 14` in the test file** — the floor proves nothing was deleted — and take the exact pin from the source. ⚠️ **A fold-side relaxation produces an empty sweep-diff and green tests; this row is the only thing that catches it.**
> **5. REGRESSION DIRECTION, from live fixtures.** Re-materialize Step 1's tripping fixtures from the dev log's pasted SOURCE TEXT **into a fresh `mktemp -d` outside every git tree** (never inside `bellows/`, whose Scope names only four files) and run them in this session: **M2 must fire on a hollow line in BOTH branches, M3 on all three negated forms, and NEITHER may fire on the legitimate controls** — or the zeros above are a dead check rather than a clean corpus.
> **6. WARN-ONLY BY MECHANISM (C1).** Grep both changed checks and show **neither appends to `results` nor assigns `all_passed`** — with `-F`, in a BARE (unpiped) invocation, and **with a positive-control grep beside the negatives** (an empty result is otherwise indistinguishable from a mistyped pattern). THEN `echo $?` = 0 on a fixture tripping both. **Both, never just the second.**
>
> **Then `## Evidence and Narrative`, then the Output Receipt.**
>
> ⚠️ **`### Ledger Updates`** — author via `Write`/`Edit` (the daemon parses assistant text and Write/Edit content, NOT Bash), EXACTLY ONCE, complete, never re-edited; `##`-level after `## Evidence and Narrative`; substance INSIDE the section; blank line after the last subsection; one row per bullet, no second physical line.
>
> **`#### Forward Register`: TWO rows, and only these two.**
> 1. **Deferred §4 prose update:** *DRAFTING_CYCLE §4 describes the T2 panel check as line-anchored-only and enumerates the negation strip as `not dry` / `no dry` / `never dry`; M2 and M3 changed both mechanics, so §4's descriptions are now understatements and owe a governance-root edit (deferred per §6's pair-or-defer-and-say).*
> 2. **Row 25 — MEASUREMENT ATTACHED (an UPDATE to the existing open row, not a new item):** *row 25 remains OPEN and unchanged in scope; this plan attempted its check, measured it, and cut it. 1379 of 1390 corpus plans already emit ≥1 warning (99.2%) and exactly one declares, so the check would have fired ~1378 times against check (i)'s eleven; the newest-20 bellows rate is 15/20. Any successor must state its expected firing population as a MEASURED number before authoring.*
>
> ⚠️⚠️ **Rule 44 forbids a duplicate row where an open one already covers the area, and row 25 IS open** (`bellows/knowledge/FORWARD.md`, status `open`) — but the ledger channel is append-only with `status="open"` hardcoded, so it CANNOT update in place. **Emit the bullet as written (its text names row 25, so the two are linkable) AND flag in the QA narrative that the Planner must consolidate them into row 25 at the wrap via the Rule 42 direct edit.** Panel seat B: an earlier draft called this "re-opened", which was false — row 25 was never closed.
>
> ⚠️ Rows 27 and 28 are NOT appended — they close by wrap reconciliation (Rule 42, the row-29 precedent).
>
> **⚠️ FINAL ACTION — COMMIT YOUR DEPOSITS**, pathspec on the COMMIT naming exactly the Scope files, then assert `git show --name-only --format= HEAD` prints exactly them. **Commit only — NO push.**
>
> **Scope:**
> - `knowledge/qa/lint-s4-hardening-qa-2026-08-09.md`
> - `knowledge/qa/evidence/lint-s4-hardening-2026-08-09/targeted-tests.txt`
> - `knowledge/qa/evidence/lint-s4-hardening-2026-08-09/full-suite.txt`
> - `knowledge/qa/evidence/lint-s4-hardening-2026-08-09/sweep-diff.txt`
>
> **Deposits:**
> - `bellows/knowledge/qa/lint-s4-hardening-qa-2026-08-09.md`
> - `bellows/knowledge/qa/evidence/lint-s4-hardening-2026-08-09/targeted-tests.txt`
> - `bellows/knowledge/qa/evidence/lint-s4-hardening-2026-08-09/full-suite.txt`
> - `bellows/knowledge/qa/evidence/lint-s4-hardening-2026-08-09/sweep-diff.txt`

---

## Drafting Cycle

**Tier:** T2 — trigger fired: T-6 (governance surface: the gate enforcing DRAFTING_CYCLE §3/§4). **Proven clone** of executable-303's §4 check machinery, diffed against executable-324 (newest same-class) and executable-286 (the first hardening of these two checks).

**Walks:** 2, plus ACID a1 and a five-seat panel run across two artifacts (see below).
- Weak spots:          w1 2 folded; w2 1 folded; **w3 (confirming) 2 folded — NOT dry**: the Step-1 receipt still said fold-side "line" singular after seat C established TWO sites, and ledger C3 said the same — the seat-C fold had landed in the spec and the QA row but not in its two mirror sites.
- Destruction:         w1 1 folded; w2 dry; **w3 dry** — the confirming folds add obligations only; no guard weakened.
- Vulnerabilities:     w1 2 folded; w2 1 folded; **w3 1 folded — the live one**: the pinned corpus count 1390 is ALREADY 1391, because this session closed plan 330 into `Done/` DURING this plan's own panel. Seat C predicted exactly this instability and restored the pins for it; the confirming pass caught it happening. The literal is now marked as a timestamped measurement, never a constant, and QA re-derives it.
- Integration-record:  w1 2 folded; w2 2 folded; **w3 1 folded**: ledger C8's schedule row predated the A0(0) fold and still described the old three-task A0, omitting the probe seat C required to run FIRST.
- ACID:                a1 4 folded, run apart (the §4 doctrine debt; the missing verdict-window posture for a plan shipping executable code; the sweep-diff baseline provenance; an A0 HALT with no payload).

**Cold panel (T2):** FIVE seats under v1.7's registry — two on the pre-cut artifact, three on the reduced one after the CEO's scope cut. **Seat 1 (weak-spots + evidence-attack): 8 findings, 3 HIGH** — measured the cut change's firing population at 99.2% and destroyed its design. **Seat 2 (destruction + clone-diff vs 286/303/304/324): 15 findings, 7 HIGH** — the session's largest yield: 286's fold-side fence and message-text pin recovered, 286's deliberate negation bound surfaced (M3 reverses a priced decision), M2's dash branch retracted from a seat-1 misdefinition, an invalid `git show <blob>:path` that made the central proof unrunnable, and the measured zero blast radius that makes the expected diff empty. **RE-PANEL seat A (vulnerabilities, register-plain, on the CUT artifact): 9 findings, 2 HIGH** — the strongest seat of the session, every finding executed rather than argued. It implemented M2/M3 in a scratch copy and ran them: **the N-table is CONFIRMED exactly as written** (N=1 catches all three forms and leaves the legitimate close silent; N≥3 false-WARNs) and **the ZERO corpus impact is CONFIRMED** at N=1/2/3/4 with zero crashes. Its two HIGHs would each have failed a CORRECT run: (1) **the Rule 20 block treats a zero-byte evidence file as CRITICAL**, so depositing the expected-EMPTY sweep-diff verbatim fails the mandatory self-check while a DEFECTIVE non-empty diff passes it — the gate inverted; (2) **QA's `=14` message-count post-condition is unsatisfiable**, because Task E's own mandated tests add occurrences (~34), so it could only be met by omitting the assertions the tests exist to make. It also found the `mktemp -d` import guard is **off by one directory** (`BELLOWS_ROOT` resolves to the shared `$TMPDIR`, not the fresh dir), that an empty diff cannot be distinguished from zero-files-compared, and that M2's colon-bearing definition false-WARNs two real colonless corpus panel lines. ⚠️ **It also corrected this plan's own premise: the "14 assertions" figure is 6 positive + 4 NEGATIVE + 4 prose, and a reword turns the four negatives VACUOUSLY TRUE — the blind spot runs opposite to the one the plan had priced.**

**RE-PANEL seat B (integration/record): 12 findings, 4 HIGH** — caught what the CUT itself broke: the cut had silently deleted the A0 already-landed probe (leaving the slug's crash-redo re-entry key inert) and the §5 conformance record (v1.8's own mandate, on the plan whose subject is §4 conformance), while the cut's commit claimed "17 guards asserted retained" — **a hand-picked retained-material list cannot see an unintended removal; the instrument for a subtractive edit is a DIFF review.** It also RETRACTED a factually false dash-branch claim folded in at seat 2 (`executable-306` carries zero `**Cold panel` lines and is satisfied SOLELY by `- Cold panel (§2.6)`, the form the plan said the branch excluded), found Task E missing two cases its own prose declared mandatory, a Rule 44 duplicate-row hazard, and a §6 citation running the wrong direction.

**RE-PANEL seat C (ACID + system brief, last, on the fully-folded artifact): 13 findings, 3 HIGH** — the fold-interaction seat, and it found more cut damage plus a defect in seat B's own repair. **The restored A0 probe had been placed on the CLEAN branch, where it could never fire in the crash state it exists for** — and the DIRTY branch then routes to `git restore` (to a HEAD that already contains the edits) plus reapply, verbatim the double-apply the probe prevents; it now runs FIRST and unconditionally. **The cut's subsumption test checked the WRONG PROPERTY:** it verified that no surviving row reads per-root fire counts (true) and removed the five corpus pins and the sweep bookend — which never guarded fire counts, they guarded CORPUS STABILITY across the sweep, and this shop files plans into `Done/` mid-session, so a landing plan would HALT the central proof with no attribution instrument. Also: Q0 had lost its status check while KEEPING the prose that justifies it; the Rule 20 mandate enumerated three of four placeholders (the omitted `qa_report_path` is itself a CRITICAL); and **the fold-side fence named one of TWO fold-side tests** — the legacy fallback was unfenced and invisible to every instrument.

⚠️ **Fold-origin classification (LESSONS 227), running:** w1 7/7 pre-existing · a1 4/4 pre-existing · w2 3 of 4 FOLD-INTRODUCED · seat 2 ~6 of 15 fold-introduced, several traceable directly to seat-1 folds. **The ratio turned at walk 2 and stayed turned, which is the §2.8 signal — and it is why the panel was halted rather than completed.**

⛔ **CUT (CEO decision 2026-08-09) — the §2.8 third resolution, taken deliberately.** After seat 2 the plan stood at **248 lines to change two regexes whose measured corpus impact is ZERO**, with 34 findings across two seats concentrated in the machinery rather than in the change. **Cut to the shippable core:** the two behaviour specs with their 286-derived fences, the fold-side byte-comparison, test protection, and the sweep-diff. **The corpus-sweep false-positive apparatus was removed because its only consumer was the cut check** — subsumption verified before removal: no surviving row reads per-root or per-check fire counts. Every guard that survives is one that can catch a defect in what actually ships.

**Conformance (§5, v1.8 — the mandate this session shipped, applied to its own first inheritor):** run at shape-stability before any adversarial pass, and re-run after every culmination since. ⚠️ **RESTORED here after the cut DELETED it — panel seat B.** The cut removed the record while the commit message asserted "17 load-bearing guards asserted retained": that assertion covered a hand-picked list and could not see what was removed unintentionally. **Latest run (post-seat-B culmination): exit 0, all checks PASS, ONE warning** — the fold-as-last-event warning, EARNED (the last event is a fold) and clearing only when a confirming pass runs dry. ⚠️⚠️ **DEPOSIT-STATE DECLARATION, REVISED AT DEPOSIT — CEO DECISION 2026-08-09.** The earlier bar ("exit 0 with ZERO warnings") is superseded: **this plan deposits at exit 0 with exactly ONE warning — `Drafting Cycle closing indicates fold as last event, not a dry lens pass` — and that warning is TRUE, EARNED, and EXPECTED.** It is not silenced, not reworded, and not cleared by authoring a dry line: the closing genuinely is a fold. **Any OTHER warning at deposit is unexplained → do not deposit.**

**Panel metering (this batch is the designated METERED A/B against the 563k-token / 45-finding baseline; recorded here because a yield without its cost cannot enter the comparator):** seat 1 evidence-attack **96k tokens → 8 findings / 3 HIGH**; seat 2 clone-diff **181k → 15 / 7**; re-panel seat A vulnerabilities, register-plain, on the CUT artifact **106k → 9 / 2**; re-panel seat B integration/record **156k → 12 / 4**. **Seat C system brief 121k → 13 / 3. Total 660k → 57 findings / 19 HIGH across five seats.** ⚠️ **The register-plain seat again produced findings no aimed brief did — both of its HIGHs would have failed a CORRECT run — which contradicts the 324 baseline's reading that HIGHs come from aimed briefs; a fourth consecutive datum for adds-not-monopolizes.**

**Closing:** ⚠️ **DEPOSITED ON A NON-DRY CLOSE — A DECLARED §2 DEVIATION BY CEO DECISION (2026-08-09).** §2 requires the last event before deposit to be a lens pass; it is a fold, and that is stated rather than engineered away. **The reasoning, recorded so a later reader can judge it:** the two regex specifications at this plan's centre have not changed since walk 1 and were independently implemented and executed by a cold seat, which confirmed the N-table exactly and the zero blast radius at every gap width. Everything since has been apparatus — and the apparatus is now generating most of its own findings: **walk 2 was 3-of-4 fold-introduced, the confirming pass 3-of-4, with the panel's own folds supplying the mirror-site defects in between.** Per §2.8 that is the oscillation signal, and per LESSONS 227 the answer to a mostly-fold-introduced pass is to stop, not to walk again. **Walking further would have hardened scaffolding around an executable core that stopped moving five phases ago.** ⚠️ **What this costs, stated honestly:** an unrun confirming pass might have found another mirror-site half-fold like the three walk 3 found. The residual risk is scoped to the plan's INSTRUCTIONS, not to what ships — the two behaviour specs, their 286-derived fences, and the N=1 bound are the most-verified parts of the artifact. **Fold-and-deposit exactly once.**
