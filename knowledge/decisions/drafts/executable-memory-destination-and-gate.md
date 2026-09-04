# bellows — executable: DOCTRINE + CODE — the lessons-destination ruling of 2026-09-02 reaches the two documents that still contradict it, and the `[4/memory]` gate that already enforces it stops being inert on the mini (thread 91)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** targeted (`tests/test_wrap_memory_class_gate.py`, `tests/test_wrap_hooks.py`) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 91 (open since 2026-09-02, carrying the CEO ruling); exec-100027 (Done 2026-09-02 — the clone origin for a cross-repo doctrine edit: its `writes:` mixes an absolute `eluvian-governance` path with repo-relative bellows paths); the shipped `[4/memory]` gate and its six tests (the clone origin for the code half).

## What this changes

⛔ **This is a RECONCILIATION of three surfaces that disagree about one rule**, not a new rule. The CEO ruled on 2026-09-02 that lessons go to the corpus unless they cannot be codified. Measured 2026-09-03: the CODE already enforces exactly that, the DOCUMENTS still say the opposite, and the code cannot run on the machine where the work happens.

1. `PLANNER_TEMPLATE.md` Session Wrap step 7 — memory demoted from a routine destination to the named exception.
2. `bellows/hooks/commands/wrap.md` — the mirrored ritual sentence removed.
3. `hooks/eluvian/wrap_check.py` — the `[4/memory]` gate's change-detection made git-independent, so it fires on a non-git memory directory.

## Why this exists

**The rule is already in the code.** `wrap_check.py:344-350` fails a wrap when a new or modified memory entry lacks `class: mechanize|codify|keep|stale`, with the message stating that **`keep` requires a stated impossibility**. That IS the CEO's ruling, mechanized, with six tests in `tests/test_wrap_memory_class_gate.py`.

**The documents contradict it.** `PLANNER_TEMPLATE.md:2094` still routes "**Planner working-pattern lessons** … to the Planner's memory repo" as one of "THREE destinations", and `hooks/commands/wrap.md:69` mirrors it. A Planner following the document routes to memory by default; a Planner following the code must justify it.

**And the gate cannot fire where the work happens.** The gate derives its new/modified set from `git status --porcelain` on the memory directory. On the Mac mini that directory is the harness's auto-memory dir and is **not a git repository** — the command errors, the dirty list is empty, and every entry is skipped.

⚠️ **Measured live on 2026-09-03, this session:** the Planner routed a working-pattern lesson to memory, following the document, a day after the ruling. Every wrap gate passed. The gate that would have caught it was inert, and the entry it wrote carries no `class:` field at all.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the doctrine carrier | `PLANNER_TEMPLATE.md:2094` — step 7, the live rule, "THREE destinations, assigned by TWO tests" | `grep -n "memory repo" PLANNER_TEMPLATE.md` |
| P2 | ⚠️ NOT carriers | `PLANNER_TEMPLATE.md:2267` (v4.89 row) and `:2272` (v4.84 row) are HISTORY rows recording what past versions said. **Do not edit them** — strike, never tidy | same grep; read the table column |
| P3 | the hook carrier | `bellows/hooks/commands/wrap.md:69` | `grep -n "working-pattern" hooks/commands/wrap.md` |
| P4 | unaffected | `wrap.md:103` (step 4 — commit the memory repo if touched) stays: memory remains valid for what cannot be codified | read the step |
| P5 | the gate already enforces the ruling | `wrap_check.py:344` `if "class:" not in _head`, message at `:348-350` naming `mechanize\|codify\|keep\|stale` and "keep requires a stated impossibility" | `sed -n '326,352p' hooks/eluvian/wrap_check.py` |
| P6 | ⛔ the gate is INERT here | the mini's memory dir has no `.git`; `git status --porcelain` there exits non-zero, so `m_dirty` is empty and no entry is checked | `git -C "$ELUVIAN_WRAP_MEMORY" status --porcelain` → `fatal: not a git repository` |
| P7 | ⛔ detonation risk | **12 of 12** memory entries carry NO `class:` field. A change-detector without a grace window fails the first wrap on all of them | `for f in $ELUVIAN_WRAP_MEMORY/*.md; do head -12 "$f" \| grep -c "^class:"; done` |
| P8 | the grace the gate already intends | `wrap_check.py:327` — "Committed files are exempt until touched — gradual backfill by design; the first post-ship wrap must not detonate" | read the comment |
| P9 | current version | `PLANNER_TEMPLATE.md` is v4.98 (plan 100026, 2026-09-02) → this ships v4.99 | `grep -oE "v4\.[0-9]+" PLANNER_TEMPLATE.md \| sort -t. -k2 -n \| tail -1` |
| P10 | cross-repo precedent | `Done/executable-100027.md:105` — `writes:` carries `/Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md` beside repo-relative bellows paths, and classed `shop-infra` | read its Cycle Manifest |
| P11 | in-flight | re-derive at execution: zero plans `claimed`/`in_progress`/`awaiting_verdict` expected | `sqlite3 lifecycle.db "SELECT id,lifecycle_state FROM plans WHERE lifecycle_state NOT IN ('closed','done','halted','dropped')"` |

## What this does NOT do

- **It does not change the memory frontmatter schema.** The entries in use carry `metadata: type: user\|feedback\|project\|reference`; the gate reads `class:`. Two schemas that do not know about each other. Reconciling them is a separate decision with its own blast radius — **filed, not folded.**
- **It does not backfill `class:` onto the 12 existing entries.** P8's grace is preserved deliberately; backfill is gradual and by touch.
- **It does not de-hardcode `wrap_check.py:93`**, whose fallback memory path is the Air's `-Users-marklehn-Developer-GitHub-` layout. Same class as thread 113, filed there.
- **It does not touch `LESSONS.md` or the glossary.**

## Drafting Cycle

**Tier:** **T2 — computed, not judged.** ⛔ **T-6 fires THREE times**, quoted: *"T-6 — Governance surface. Edits doctrine, **the template**, **gates**, or specialist contracts."* This plan edits `PLANNER_TEMPLATE.md` (the template), `wrap_check.py` (a gate), and `hooks/commands/wrap.md` (doctrine). **T-1 also fires** — two repositories, the 100027 precedent. §1: *"T2 — Cold-panel cycle. T-5 or T-6 fires … → run T1 plus the cold-reader panel (§2.6)."* T-3 fires too (`wrap_check` runs on every machine that wraps). T-8 not fired: clone by kind of `Done/executable-100027.md` (doctrine half, itself T2 on the same triggers) and of the shipped `[4/memory]` gate (code half).
⚠️ **v0 declared T1 and argued "T-6 not claimed: a wrap gate, not a step gate."** That was a RESTATEMENT of the trigger, and it inverted it — T-6 says *gates*, not *step gates*. Caught at walk 1 by quoting the rule instead of paraphrasing it. **A cold panel is mandatory for this plan and is not optional at the author's judgement.**
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-memory-destination-and-gate-2026-09-03.md`
**Walks:** 4 (walks 0–4 complete).
**Walk 0 — context pin:** eleven measurements. The load-bearing one: the ruling is ALREADY in code and the documents are what dissent — which inverts the thread's framing from "remove a destination" to "make three surfaces agree." Second: the gate is inert on the mini, so the enforcement that exists has never run here.

**Walk 1 — 3 findings (instruction 3 / record 0); 0 fold-introduced.** ⛔ The tier was wrong (T1 → T2) and wrong by restating a trigger rather than quoting it — the recorded Planner failure class recurring. `plan_lint` FAILs (c): step 2 carries no Rule 20 QA banner pair. And the manifest's proposed home inside the memory directory is unversioned and deletable, so losing it silently re-seeds the grace and grandfathers a classless entry forever — it needs a home that cannot vanish, or a seed record that survives deletion.
**⛔ CONSEQUENCE OF THE TIER CORRECTION:** this plan requires a COLD PANEL (§2.6) before it can close. It cannot reach the bar on warm walks alone.
**Walk 2 — 2 findings (instruction 2 / record 0), both discharging walk 1's pending items.** The manifest's silent-reset hole closed by making SEEDING LOUD — an unversioned manifest in a harness-owned directory can vanish, and a grace reset nobody can see is the failure mode, not the seeding. And the Rule 20 banner pair added, clearing `plan_lint` (c).
**Walk 3 — 2 findings (instruction 2 / record 0); 0 fold-introduced.** ⛔ The manifest's POPULATION had to be pinned: `MEMORY.md` is the index, not an entry, and the shipped test asserts editing it alone raises no class failure — a manifest hashing every `*.md` would fail every wrap, since step 3b updates the index every time. ⛔ And the plan writes TWO repositories with no stated ordering: bellows must commit LAST, or the documents lead the code and the surfaces disagree in a new way — the very failure being removed.
**Walk 4 — 1 finding (instruction 1 / record 0); 0 fold-introduced.** ⛔ The gate demands `class: mechanize|codify|keep|stale` from a vocabulary that is defined NOWHERE — it exists only inside the failure message that demands it. Item 4 would have made `PLANNER_TEMPLATE.md` the first doctrine reference to those terms while still leaving them undefined, i.e. shipping a NEW doctrine/code gap inside the plan that exists to close one. Added Item 4b (four `GLOSSARY.md` entries), `GLOSSARY.md` to Scope, numstat 6 → 7.
**Closing:** NOT CLOSED at walk 4 — one instruction-class finding.

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze; an unemitted manifest reclassified plan 100031 and dispatched it past the class hold, LESSONS.md 2026-09-03)*

## STEP 1 — DEV (reconcile the documents to the code, and make the code able to run)

> **Scope:**
> - `/Users/marklehn/Developer/eluvian-governance/PLANNER_TEMPLATE.md`
> - `/Users/marklehn/Developer/eluvian-governance/GLOSSARY.md`
> - `hooks/commands/wrap.md`
> - `hooks/eluvian/wrap_check.py`
> - `tests/test_wrap_memory_class_gate.py`
> - `knowledge/mutants/memory-destination-gate.json`
> - `knowledge/development/dev-log-memory-destination-and-gate-2026-09-03.md`
>
> ⚠️ **TWO REPOSITORIES, ONE STEP.** Reach the governance checkout by absolute path with `git -C "$GOV"` and **never `cd`** (the 100027 discipline, same shape). Before editing, confirm `git -C "$GOV" status --porcelain -- PLANNER_TEMPLATE.md` is EMPTY and its sha matches P9's version reading; a dirty governance tree means another editor is live and this step must HALT rather than interleave. ⛔ **Commit bellows LAST.** If the governance edit lands and bellows does not, the documents lead the code and the surfaces disagree in a NEW way — which is the exact failure this plan exists to remove. State both commit shas in the dev-log.
>
> **Item 1 — re-derive P1–P11 and HALT on mismatch.** ⚠️ P1, P3 and P5 are LINE NUMBERS in files other plans edit; thread 91 recorded `PLANNER_TEMPLATE.md:2028` on 2026-09-02 and it had moved to `:2094` by 2026-09-03. Re-derive every one by grep, never by the number written here. ⛔ If the `[4/memory]` gate no longer contains the `class:` check, or the memory directory has become a git repo, HALT and request a verdict — this plan's premise is that the code is right and cannot run.
>
> **Item 2 — write the failing tests FIRST**, extending `tests/test_wrap_memory_class_gate.py`:
> 1. ⛔ **a NON-GIT memory directory with a new classless entry FAILS** — the case that is silently skipped today
> 2. a non-git memory directory whose entries are all unchanged since the last recorded wrap produces NO fail — the grace
> 3. ⛔ **first run against a non-git directory with no manifest present SEEDS it and fails nothing** — P7's twelve classless entries must not detonate
> 4. a non-git entry that is modified after seeding, still classless → FAIL naming that file
> 5. a non-git entry modified after seeding and carrying `class: codify` → no fail
> 6. ⛔ **`class: keep` without a stated impossibility → FAIL**; `keep` with one → no fail. The message at `:348-350` already promises this; assert it is true
> 7. ⛔ **byte-identical behaviour when the memory directory IS a git repo** — the positive control; the shop machine must take the path it takes today
> 8. the six existing tests still pass unchanged
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — make the gate's change detection git-independent.** Keep git as the detector when the directory IS a repo (test 7). When it is not, derive new/modified from a manifest at `<memory>/.wrap-manifest.json` mapping entry filename → sha256 as of the last successful wrap. Absent manifest → SEED it and check nothing (P8's grace, reproduced without git). ⛔ **Do not use bare mtime**: a file re-written with identical content is not a modification, and mtime alone would fail a wrap for a no-op edit.
> ⛔ **The manifest's POPULATION must reproduce the git path's exactly.** `MEMORY.md` is the index, not an entry, and the shipped test `test_memory_md_edit_alone_no_class_fail` asserts that editing it alone raises no class failure. A manifest that hashes every `*.md` in the directory would fail a wrap the moment the index is updated — which every wrap does, at step 3b. Exclude `MEMORY.md`, and add a test asserting the non-git path agrees with the git path on that exclusion.
> ⛔ **SEEDING MUST BE LOUD.** The manifest lives in a harness-owned directory, is unversioned, and can be deleted or re-provisioned; a silent re-seed would reopen the grace window and grandfather every classless entry — indistinguishable from the inert gate this plan exists to fix. Print a `[4/memory] SEEDED manifest with N entr(ies) — grace window opened` line on every seed, and assert it in the tests. A grace reset that nobody can see is the failure mode, not the seeding itself.
>
> **Item 4 — `PLANNER_TEMPLATE.md` step 7.** Demote memory from a routine destination to the exception, in the CODE's own vocabulary so the two cannot drift again: lessons go to `LESSONS.md` or the central glossary; memory holds only what cannot be codified, and an entry that stays there declares `class: keep` **with a stated impossibility**. Update "THREE destinations" to TWO. ⚠️ The second routing test ("does this destination feed a system that ACTS on it?") still does work — it separates forge-ingested `LESSONS.md` from the glossary — so keep it and re-word only its examples. Add a History row for **v4.99** citing the CEO ruling of 2026-09-02 (the v4.84 direct-ruling precedent). ⛔ **Do not edit the v4.89 or v4.84 History rows** (P2).
>
> **Item 4b — define the class vocabulary in `GLOSSARY.md`.** ⛔ **`mechanize`, `codify`, `keep` and `stale` are defined NOWHERE** — measured: they appear only inside `wrap_check.py:349`'s failure message, and in no doctrine file, no template, and no glossary entry. An agent that trips the gate has no definition to consult, and Item 4 would make `PLANNER_TEMPLATE.md` the first doctrine surface to reference the vocabulary while still not defining it — leaving a NEW disagreement in a plan whose purpose is removing one. Add one glossary entry per value, tagged `[project: bellows]`, each stating what the value asserts about the entry and what the wrap does with it. ⛔ Derive the four values from the code's own string, not from this plan's prose.
>
> **Item 5 — `hooks/commands/wrap.md:69`.** Remove the routine-destination sentence and state the exception in one clause. ⛔ Leave step 4 (`:103`) untouched (P4).
>
> **Item 6 — `knowledge/mutants/memory-destination-gate.json`**, one mutant per new branch: drop the non-git detection arm → test 1 fails; drop the manifest seed → test 3 fails; drop the impossibility requirement on `keep` → test 6 fails; drop the git arm → test 7 fails. ⚠️ **A survivor is a missing test, stated as Critical** — and ⛔ **0 ERROR is required**: an errored mutant verifies nothing. Every anchor must be count-1 in its own file at HEAD, and every `target` must be a repo-relative path that exists there.
>
> **Item 7 — dev-log**, recording the three-surface disagreement and what each surface said before the change.
>
> **Item 8 — commit** (message tagged with the plan id); record `numstat` — exactly 7 files.
>
> **Post-conditions:** all eight tests pass; the six pre-existing gate tests unchanged; a non-git memory directory with a classless touched entry now FAILS where it passed before, demonstrated as a before/after pair in the same run; the twelve existing entries do NOT fail a first wrap; `PLANNER_TEMPLATE.md` and `wrap.md` no longer route working-pattern lessons to memory by default, verified by grepping the CLAIM in several phrasings rather than one literal; the runner's own mutants all killed, 0 error.

## STEP 2 — QA (full suite + the three surfaces shown to agree)

> **Item 1 — full suite** from the dispatch worktree, output to `pytest_full.txt`. ⚠️ The canonical checkout carries a `config.json` that makes `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` fail; a worktree has none and the suite is green there. `known_failures: 0` is correct for this plan's dispatch location — do not raise it.
>
> **Item 2 — the reconciliation demonstrated:** quote the post-change sentence from each of the three surfaces (`PLANNER_TEMPLATE.md` step 7, `wrap.md`, the gate's failure message) side by side and show they name the same rule in the same vocabulary. ⛔ A reader must not be able to derive a different destination from any one of them.
>
> **Item 3 — the gate fires here:** construct a non-git memory directory in scratch, seed the manifest, touch one entry without `class:`, and show the wrap FAILS naming that file. Then show the same directory with `class: codify` passing. ⛔ Run the SAME probe against the pre-change `wrap_check` and show it does NOT fail — the fixture must be proven to discriminate, not merely to pass.
>
> **Item 4 — no-regression:** every existing `wrap_check` test file green; the git path byte-identical on a git-backed memory directory.
>
> **Item 5 — the runner's own kill map:** `mutation_check` over `knowledge/mutants/memory-destination-gate.json` → all killed, 0 survived, **0 error**.
>
> **Item 6 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `memory-destination-and-gate-2026-09-03`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/memory-destination-and-gate-2026-09-03/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/memory-destination-and-gate-2026-09-03"`
> - `required_evidence_files`: `["pytest_full.txt", "probes-raw.txt"]`
>
> Include the literal stdout of the block in the QA report. Banner, byte-exact, inside the receipt's VERIFICATION section:
>
> ```
> ============================================================
> Rule 20 — QA Self-Check Results
> ============================================================
> PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
> ```
>
> ⛔ If the block prints `FAILED`, do not proceed with closure — halt and report.
>
> **Post-conditions:** suite green from a worktree, 0 failed; the three surfaces quoted and agreeing; the gate shown to fail on a non-git classless touch AND shown not to fail before the change; the twelve existing entries not detonating; kill map clean.
