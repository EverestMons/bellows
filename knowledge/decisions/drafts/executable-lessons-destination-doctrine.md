# bellows — executable: DOCTRINE — the lessons-destination ruling of 2026-09-02 reaches the four surfaces that still contradict it, and the 2026-08-18 test it supersedes is STRUCK where it stands (thread 91, rebuilt after a RE-DRAFT)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** none (doc-only — no code path reads these files' CONTENT; QA proves the gates unchanged on a shipped plan and deposits its raw probes as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of Step 2's gate note, overridden by the Planner with reference to it) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 91; the CEO ruling of 2026-09-02 and its confirmation of 2026-09-03. Clone origin: `Done/executable-100027.md` (2026-09-02 — cross-repo doctrine edit by a committed builder, itself T2 on T-6 + T-1, doc-only with the same benign `qa_test_result` pre-declaration).

## ⛔ This is the REBUILD. Read why the first attempt died.

`drafts/executable-memory-destination-and-gate.md` carries a **RE-DRAFT** banner. Its premise — *"the rule is already in the code"* — was measured FALSE by a T2 cold panel: `wrap_check.py:344` is `if "class:" not in _head` over the first 600 bytes of the whole file, a substring check that accepts `class: banana`, accepts `class: keep` with no stated impossibility, and cannot tell frontmatter from the word appearing in prose. On the 139-entry shop corpus, 11 entries carry a class and **all 11 are `stale`**.

**This plan therefore CUTS the code half entirely** — it is thread 114, with six measured defects — and ships only the doctrine reconciliation. That follows the CEO's own sequencing rule: clear a system's errors before adding to it. ⚠️ **Declared widening against thread 91:** the thread names two edits (`PLANNER_TEMPLATE.md`, `wrap.md`); this plan edits four surfaces, because the cold panel found two more carriers. The widening is declared, not silent (the panel's F19).

## Why this exists

**The ruling.** CEO 2026-09-02: lessons go to the corpus unless they cannot be codified. Confirmed 2026-09-03, ruling explicitly that this **SUPERSEDES** the 2026-08-18 test.

**Four surfaces still say otherwise**, and one of them is forge-ingested and marked `[status: implemented]`.

⚠️ **Measured live on 2026-09-03:** the Planner routed a working-pattern lesson to memory, following `wrap.md`, a day after the ruling. Every wrap gate passed. **That is this plan's licensing evidence** — a ruling that lives only in a thread is not in force.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | carrier 1 — the template | `PLANNER_TEMPLATE.md:2094`, Session Wrap step 7, "THREE destinations, assigned by TWO tests" | `grep -n "memory repo" PLANNER_TEMPLATE.md` |
| P2 | carrier 2 — the ritual | `hooks/commands/wrap.md:69`, "working-pattern lessons → the memory repo" | `grep -n "working-pattern" hooks/commands/wrap.md` |
| P3 | ⛔ carrier 3, found by the cold panel | `hooks/commands/eluvian.md:31` recites *"memory repo — Planner-personal working patterns"* — **read at the start of every session on every machine**, and the only surviving home of that phrase | `grep -n "working patterns" hooks/commands/eluvian.md` |
| P4 | ⛔ carrier 4 — forge-ingested | `LESSONS.md:4447`, inside the 2026-08-19 entry marked `[status: implemented]`: *"Planner working-patterns go to the Planner's memory. Uncertain items park in the baton."* | `sed -n '4447p' LESSONS.md` |
| P5 | ⚠️ NOT carriers | `PLANNER_TEMPLATE.md:2267`/`:2272` are History rows recording v4.89/v4.84 — **strike, never tidy** | read the table column |
| P6 | unaffected | `wrap.md:103` (commit the memory repo if touched) — memory remains valid for what cannot be codified | read the step |
| P7 | ⛔ the code enforces NOTHING relevant | `wrap_check.py:344` is a 600-byte substring check; `class: banana` passes. **Do not describe the gate as enforcing this ruling.** Thread 114 | run the four-case probe |
| P8 | the vocabulary IS defined | `governance/knowledge/research/memory-to-system-audit-2026-08-25.md` — MECHANIZE→code, CODIFY→doctrine, KEEP→hardcoding impossible, STALE→retire, with a worked 28-row classification under a quoted CEO directive | `grep -n "MECHANIZE" <that file>` |
| P9 | ⛔ the sentence names a dead path | the step-7 line routes to `/Users/marklehn/Developer/GitHub/GLOSSARY.md`, which **does not exist on this machine**; `Developer/GitHub` appears 29 times in the file | `ls /Users/marklehn/Developer/GitHub` → No such file |
| P10 | version + last writer | `PLANNER_TEMPLATE.md` is v4.98 → this ships v4.99. ⚠️ `git blame -L 2094,2094` says the LINE was last written by plan **550** (v4.94), not by 100026 | `git blame -L 2094,2094 -- PLANNER_TEMPLATE.md` |
| P11 | in-flight | re-derive at execution | `sqlite3 lifecycle.db "SELECT id,lifecycle_state FROM plans WHERE lifecycle_state NOT IN ('closed','done','halted','dropped')"` |

## What this does NOT do

- ⛔ **It does not touch `wrap_check.py` or any code.** The gate's six defects are thread 114. Describing the gate as enforcement is forbidden here (P7).
- **It does not decide the BATON's status.** P4's ruling names a fourth destination this plan does not adjudicate; it is read as ORTHOGONAL — the baton holds uncertain in-flight items, not lessons routed by class. ⚠️ Stated for the CEO to correct, never assumed away.
- **It does not de-hardcode the other 28 `Developer/GitHub` references** (thread 113) — only the one inside the sentence it rewrites, because leaving a dead path in its own new prose would ship a fresh defect (P9).
- **It does not backfill `class:` onto any memory entry**, and does not change the memory frontmatter schema.

## Drafting Cycle

**Tier:** **T2 — computed, not judged.** T-6 quoted: *"Edits doctrine, **the template**, gates, or specialist contracts."* This edits `PLANNER_TEMPLATE.md` (the template), two `hooks/commands/` ritual documents, and `LESSONS.md` (doctrine corpus). **T-1 fires** — two repositories. §1: *"T2 — Cold-panel cycle. T-5 or T-6 fires … → run T1 plus the cold-reader panel (§2.6)."*
⛔ **§2.0's T2 walk-0 obligations are owed AT WALK 0 and are not deferrable** — ONE cold scout seat run BEFORE lens 1, and the clone-diff against `Done/executable-100027.md` run BEFORE walk 1, both recorded on the Cycle Log's walk-0 line. ⚠️ The predecessor plan skipped both by being re-tiered at walk 1 and never going back; three of its panel's seven HIGH findings were clone-diff findings. **Do not repeat that.**
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-lessons-destination-doctrine-2026-09-03.md`
**Walks:** 0 (context pin complete; the walk-0 scout and clone-diff are OWED before lens 1).

**Closing:** NOT CLOSED at walk 0.

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze; an unemitted manifest reclassified plan 100031 and dispatched it past the class hold, LESSONS.md 2026-09-03 entry 413)*

## STEP 1 — DEV (four surfaces reconciled, one supersede struck where it stands)

> **Scope:**
> - `/Users/marklehn/Developer/eluvian-governance/PLANNER_TEMPLATE.md`
> - `/Users/marklehn/Developer/eluvian-governance/LESSONS.md`
> - `hooks/commands/wrap.md`
> - `hooks/commands/eluvian.md`
> - `knowledge/development/dev-log-lessons-destination-doctrine-2026-09-03.md`
>
> ⚠️ **TWO REPOSITORIES, ONE STEP.** Governance by absolute path with `git -C "$GOV"`, **never `cd`**; commit by **explicit pathspec** (this plan's own walk register lives in the governance repo and will be dirty — a bare `commit -a` sweeps it in, the 100027 discipline). ⛔ **Commit bellows LAST.**
> ⛔ **A0 RE-ENTRY LADDER — three states, because the ordering above creates a half-landed one.** Before editing, read `git -C "$GOV" log -1 --format=%H -- PLANNER_TEMPLATE.md` and the file's version string:
> 1. **FRESH** — version reads v4.98 and porcelain is EMPTY for the file → proceed.
> 2. **RE-ENTRY** — version reads **v4.99** and the History row cites this plan id → the governance half ALREADY LANDED on a previous attempt. Skip Items 2–4, verify their post-conditions, and continue from Item 5. ⛔ Do NOT re-apply.
> 3. **NONE-MATCH** — anything else (dirty porcelain, an unexpected version, a History row citing another plan) → **HALT and request a verdict.** A foreign editor is live.
> ⚠️ The predecessor plan had HALT-on-mismatch with no ladder, so its own half-landed state was indistinguishable from a foreign edit. This is the parent 100027's answer, restored.
>
> **Item 1 — re-derive P1–P11 and HALT on mismatch.** ⛔ Line numbers move: thread 91 recorded `:2028` on 2026-09-02 and it was `:2094` a day later. Re-derive every one by grep. ⛔ Re-run P7's four-case probe and confirm the gate still accepts `class: banana` — if it now REFUSES, thread 114 has landed and this plan's P7 wording must be corrected before proceeding.
>
> **Item 2 — `PLANNER_TEMPLATE.md` step 7.** Demote memory from a routine destination to the named exception: lessons go to `LESSONS.md` or the central glossary; memory holds only what **cannot be codified**, and such an entry says so. Update "THREE destinations" to TWO. ⚠️ Keep the second routing test ("does this destination feed a system that ACTS on it?") — it still separates forge-ingested `LESSONS.md` from the glossary; re-word only its examples. ⛔ **Fix the dead path in the sentence you are rewriting** (P9): the glossary is at `$ELUVIAN_WRAP_ROOT/GLOSSARY.md`, matching what `wrap.md` already does. ⛔ Do NOT touch the other 28 `Developer/GitHub` references, and do NOT edit the History rows at `:2267`/`:2272` (P5).
>
> **Item 3 — the History row, v4.99**, citing the CEO ruling of 2026-09-02 as confirmed 2026-09-03 (the v4.84 direct-ruling precedent), and stating in the row that it **supersedes the 2026-08-18 test**.
>
> **Item 4 — `LESSONS.md:4447`: STRIKE the superseded clause where it stands.** ⛔ **This is the most guarded write in the shop** — a non-append edit to a forge-ingested file. Do it anyway, and do it as a STRIKE, never a deletion: `~~Planner working-patterns go to the Planner's memory.~~ ⛔ **SUPERSEDED by the CEO ruling of 2026-09-02 (confirmed 2026-09-03): working-pattern lessons go to the corpus unless they cannot be codified — see PLANNER_TEMPLATE v4.99.**` ⚠️ **Why this must happen and cannot wait:** `LESSONS.md` 2026-09-03 records that *"a refuted remedy left standing in the corpus gets rebuilt — the record's prescriptive half needs striking, not just its facts."* Leaving the clause is that exact class, in the corpus that teaches it. ⛔ Leave the rest of the entry, its `[status:]` marker, and the baton clause UNTOUCHED. ⛔ Verify non-destructive: the entry's previous and following entries byte-identical, and the file's line count changed only by the strike.
>
> **Item 5 — `hooks/commands/wrap.md:69`.** Remove the routine-destination sentence; state the exception in one clause. ⛔ Leave step 4 (`:103`) untouched (P6).
>
> **Item 6 — `hooks/commands/eluvian.md:31`.** Re-word the wiring line so it recites memory as the home of what cannot be codified, not of "Planner-personal working patterns". ⚠️ This is the surface every session reads first; the predecessor plan's post-condition ("a reader must not derive a different destination from any one of them") was unmet because this file was never in scope.
>
> **Item 7 — dev-log**, recording all four surfaces' prior text verbatim, the supersede, and BOTH commit shas.
>
> **Item 8 — commit** (message tagged with the plan id). ⛔ **numstat is TWO commits, not one** — 2 files in governance, 3 in bellows. Record both; a single-numstat post-condition is arithmetically unreachable across two repos (the predecessor's F11).
>
> **Post-conditions:** all four carriers re-read and none routes working-pattern lessons to memory by default, verified by grepping the CLAIM in several phrasings rather than one literal; the struck clause present with its supersede note and the surrounding entries byte-identical; `PLANNER_TEMPLATE.md` at v4.99 with a History row citing the ruling; the glossary path in the rewritten sentence resolves on this machine; both commit shas recorded.

## STEP 2 — QA (the four surfaces shown to agree; gates unchanged)

> ⚠️ **Pre-declared benign gate failure.** This plan's `test_scope` is `none` (doc-only) and step 2 deposits raw probes as `.txt`, so `_gate_qa_test_result` will find no pytest summary to parse and FAIL. That failure is expected, is named here, and is overridden by the Planner with reference to this note — the 100027 precedent, and the case `plan_lint` check (v) exists to make authors declare.
>
> **Item 1 — the reconciliation demonstrated:** quote the post-change sentence from each of the FOUR surfaces side by side. ⛔ A reader must not be able to derive a different destination from any one of them — and the check must cover `eluvian.md`, which the predecessor plan missed.
>
> **Item 2 — the supersede is legible:** show `LESSONS.md:4447` with the strike and its note, and show the entry's neighbours byte-identical (`git diff --numstat` on the file: one line changed).
>
> **Item 3 — no-regression on the gates:** run `plan_lint`, `cycle_check` and `gates.check` against a SHIPPED plan before and after, and show identical output. ⛔ These files' CONTENT is read by no code path; prove it rather than asserting it.
>
> **Item 4 — the dead path is gone from the rewritten sentence** and the other 28 remain untouched (count them: 29 before, 28 after).
>
> **Item 5 — hygiene + receipt:** numstat vs BOTH DEV commits; toplevel; reflog `-n 4` → 0 amends; per-item table; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `lessons-destination-doctrine-2026-09-03`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/lessons-destination-doctrine-2026-09-03/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/lessons-destination-doctrine-2026-09-03"`
> - `required_evidence_files`: `["probes-raw.txt"]`
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
> **Deposits:**
> - `knowledge/qa/evidence/lessons-destination-doctrine-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/lessons-destination-doctrine-2026-09-03/probes-raw.txt`
>
> **Post-conditions:** four surfaces quoted and agreeing; the strike legible and non-destructive; gates byte-identical on a shipped plan; 29 → 28 hardcoded paths; both DEV shas reconciled.
