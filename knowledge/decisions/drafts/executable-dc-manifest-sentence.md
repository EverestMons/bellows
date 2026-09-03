# bellows — executable: DOCTRINE — thread 67: the ONE edit to DRAFTING_CYCLE.md's manifest-stanza sentence — DC 2.17's four declared deferrals reconciled to the enforcing code as read, by a committed builder (DC 2.23 → 2.24); no rule changes

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** none (doc-only — no code path reads this file's CONTENT: `depositor.py:38` matches its PATH as a register pattern; QA proves the gates unchanged on a shipped plan, P6, and deposits its raw probes as the `.txt` evidence the QA gate reads) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `dc-manifest-sentence-2026-09-02`

**Depends on:** the CEO, 2026-09-02 evening ("proceed as recommended" — the thread-95 sequence opens with threads 67, 72, 74, before the W=29 tranches and the by-enforcer move); tuyere thread 67 (the four defects, one edit to one sentence; opened 2026-08-31 from the 2.17 cold read); DC History row 2.17 (the DECLARED DEFERRALS this edit discharges); `Done/executable-100026.md` in bellows (`gate2-pt-w28-b`, closed 2026-09-02 20:31 — the clone origin and the newest same-class plan: doctrine prose onto a governance-root file by a committed builder, DEV → QA, the A0 ladder with path-scoped re-entry, the HEAD-numstat discriminator) minus its DB half; the 2.17 reconcile plan `governance/knowledge/decisions/drafts/executable-doctrine-manifest-reconcile.md` (the same file, the same sentence's sibling, by kind — its gate-baseline Item 4 carried here as P6); the builder `governance/knowledge/decisions/drafts/build-dc-manifest-sentence-2026-09-02.py` (committed `a8c15d83`; digest below). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-dc-manifest-sentence-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-6 fires** — `DRAFTING_CYCLE.md` is doctrine → **T2**. T-1 fires (two repos). No T-2 (no data), no T-3 (authored and dispatched on the mini), no T-5 (one line replaced, one added — revertible by the ONE recipe), no T-7. **T-8 does NOT fire** — a structure-for-structure clone of 100026 without its DB half, and of the 2.17 reconcile by kind. **Panel form — the magnitude proxy, measured at walk 0 (all three must hold): (i) structure-clone** — the parent is 100026 (closed 2026-09-02, the newest doctrine-builder plan), and both walk-0 clone-diffs ran; **(ii) mechanized edits** — the one sentence, the version line and the History row all flow through the committed builder, whose three anchors are count-1-asserted BY EXECUTION (the sentence's head and tail on one line) and whose seventeen post-conditions and PINNED line/byte deltas are asserted on the output before any write; **(iii) scripted probes** — every new token measured 0 against the pre-edit file, the invariants at their pre-edit counts. **→ SMALL form: the walk-0 scout (two cold readers — a local seat and the Air's non-author session, the 2.17 form), then EXECUTION, then CAPSTONE.** The CEO may call the full form.

## Why this exists

DC 2.17 (2026-09-01) reconciled the §3 worked example and DECLARED, rather than fixed, four further doc-vs-code defects in the manifest-stanza sentence at `DRAFTING_CYCLE.md:253` (the row's `:228` reference has since moved), naming them thread 67 "to be fixed as ONE edit to that sentence". Each was re-read at source on 2026-09-02, with the site the reconciled sentence cites:

- **S1 — "a ten-field structured summary … The ten ordered fields":** `plan_lint.py:552-555` requires exactly those ten (`_STANZA_REQUIRED`, check (f) WARNs on missing / empty / `<declare>`) AND reads three OPTIONAL detector fields the emitter does not derive — `target_class` (`:594`), `state_space` (`:596`), `mutants` (`:603`) — checks (s)/(t). The sentence now says ten REQUIRED plus three OPTIONAL.
- **S2 + D2 — "`class:` is one of `{read-only, governed-tooling, register-writing}` … (`read-only` auto-deposits; the other two hold for the CEO)":** `depositor._assign_class` (`:266-314`) returns exactly FOUR values — `read-only` (`:307`), `shop-infra` (`:309`), `register-writing` (`:313`), `app-feature` (`:314`); a disagreeing declaration holds `class_mismatch` (`:173-178`); ONLY a derived `shop-infra` holds for a human release (`:184-186`, `class:shop-infra`); the other three auto-clear after the pre-clear collision recheck (`:187-199`). `governed-tooling` is admitted by `plan_lint.py:556`'s WARN set and written by no production code (`grep -rn governed-tooling --include='*.py'` → the lint set and tests only). The sentence now names the four, the hold, the mismatch, and `governed-tooling` for what it is.
- **S4 — "`writes∩writes` … is a HARD-HOLD, `reads∩writes` is a HOLD-AND-REPORT":** both collision types take the identical `self._hold(path, collision["reason"], collision)` (`:156`, `:197`); `collision_type` is written into the hold's sidecar at `:353`/`:362` and read by nothing (`grep -rn collision_type --include='*.py'` → the two writes and tests). The sentence now says one hold path, the type recorded for the reader.
- **The `validation:` clause — "pairs that the depositor RE-RUNS — a mismatch is a HOLD":** `_rerun_validation` (`:471-518`) re-runs `cycle_check` (any verdict but BAR_MET holds), re-runs `plan_lint` (any non-benign FAIL holds — benign letters `c`, `d`), and compares ONLY the declared `cycle_check=` token (`:513-518`); `plan_lint=` and any further pairs are read by nothing — 2.17's own History note, now in the sentence it was about.

**No rule changes.** Every corrected value was already fixed by the code; the sentence states what the code DOES. No corpus figure is claimed (the 2.17 measurements described plans; this edit describes the depositor). The §3 worked example (`:287`) is untouched. Not a lessons-forge codification (`proposed` = 0 — the W=29 packet of the same day is unrelated); a reconciliation in 2.17's form, CEO-directed, its non-author cold read (the Air's session) recorded in the register. Thread 68 (a tier floor for such reconciliations) stays open: this edit runs at T2.

## What this plan does

**In the governance checkout, by absolute path (`GOV=/Users/marklehn/Developer/eluvian-governance`), three anchored edits to `DRAFTING_CYCLE.md` by the committed builder (never by hand):**
- **E1** — the manifest-stanza sentence (the one line at `:253`, 1830 bytes, anchored by its head `**The `## Cycle Manifest` stanza: …**` and its tail `… not part of the stanza grammar defined here.`, each count 1 and both on that line) replaced whole by the reconciled sentence (3042 bytes; it closes with an italic reconciliation note naming thread 67 and DC 2.24). Its unchanged clauses — the placement after the Closing line, the trust taxonomy, the path-list form, COMPACTS, the emitter's sentinel contract — are byte-identical text.
- **E2** — `**Version:** 2.23 (2026-09-01)` → `**Version:** 2.24 (2026-09-02)`. **E3** — the History row `2.24` inserted directly under `## History`, above the surviving `2.23` row.

The builder reads the file as bytes, refuses CRLF, refuses an already-built input, asserts the three anchors (E1's head and tail each count 1 and ending the same line), applies the edits, asserts seventeen post-conditions on the OUTPUT (the new sentence once; the four corrected clauses' tokens once each; the retired class-list literal 0; `HARD-HOLD` and `HOLD-AND-REPORT` at 2 each — the 2.17 row and the new 2.24 row, the sentence's own occurrence gone; the 2.24 version 1 and the 2.23 version 0; the 2.24 row 1 and the 2.23 row surviving 1; the §3 worked example untouched 1; three section headings once each), asserts the line delta against `EXPECTED_LINES = 1` and the byte delta against `EXPECTED_BYTES = 3351`, and only then writes — to a SCRATCH path it refuses to let be the live file, anything under the literal governance root, or anything under the INPUT's git toplevel (layout-independent). Apply = copy the proven scratch output over the live file, then re-measure the live file.

**In the bellows worktree:** the dev log and the QA evidence.

## What this plan does NOT do

- Does not touch §1, §4, the §3 worked example, any other DC sentence, PLANNER_TEMPLATE.md, code, the DB, or threads. Does not add T0-R (thread 68). Does not push (the Planner pushes after the pause). Does not close thread 67 (the CEO does, at the keyboard, on the read-back).
- §6 coordinate-doctrine-and-gate: **no gate edit and none deferred** — no trigger, tier, or gate behaviour changes; P6 proves it on a shipped plan.

## MUST-PRESERVE

- ⚠️ **TWO REPOSITORIES, ONE STEP.** Governance by absolute path, `git -C "$GOV"` never `cd`; porcelain EMPTY for `DRAFTING_CYCLE.md` and sha = P1 before the builder runs; commit by explicit pathspec; no push.
- **The builder is the only editor of the doctrine file.** Its committed blob digest must equal the on-disk file (P4) before it runs; it runs scratch→scratch; the live file is replaced only by `cp` of a scratch output whose post-conditions the builder already asserted, and the live file is then re-measured (Task C).
- ⛔ **Never run any `checkout --` on an A0 halt except the ONE recipe named there**, and only when its discriminator holds; a pin mismatch otherwise means the file carries changes that are not this plan's.
- **No landed text carries a Rule 20 hedging keyword** (measured over the builder's constants at walk 0: none) — receipt rows still DESCRIBE, never quote, the sentence's body.
- **`known_failures: 0`, no suite.** The QA `.txt` evidence is `probes-raw.txt`; a doc-only plan that invokes a suite is declaring a scope it does not have (the 2.17 plan's gate note).

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`DC_SHA`**, lines, bytes — pre-edit (v2.23) | `3a84137ed3669de1`; 369 lines; 164,586 bytes | `shasum -a 256 "$GOV/DRAFTING_CYCLE.md" \| cut -c1-16`; `wc -l`; `wc -c` |
| P2 | **`ANCHORS`** — the builder's three | E1: head `**The `## Cycle Manifest` stanza: a fixed `key: value` block emitted at BAR_MET.**` 1 and tail `not part of the stanza grammar defined here.` 1, both on line 253 · E2: `**Version:** 2.23 (2026-09-01). Amended only through the Iteration Protocol (§6).` 1 · E3: the `## History` heading followed by the 2.23 row, 1 | `/usr/bin/grep -cF`; `grep -n` for the line |
| P3 | **`TOKENS`** 0 before | `ten REQUIRED fields` · `three OPTIONAL fields` · `one of the FOUR values` · `compares ONLY the declared` · `2.24 (2026-09-02)` · `slug dc-manifest-sentence-2026-09-02` — each 0; invariants: `HARD-HOLD` 2, `HOLD-AND-REPORT` 2, `{read-only, governed-tooling, register-writing}` 1, `validation: cycle_check=BAR_MET, plan_lint=0_FAIL` 1 | `/usr/bin/grep -cF` |
| P4 | **`BUILDER`** — on-disk digest = the blob at its OWN last commit | `afdc93b59638ea12` (governance `a8c15d83`) | `shasum -a 256 <builder> \| cut -c1-16`; `BC=$(git -C "$GOV" log -1 --format=%H -- governance/knowledge/decisions/drafts/build-dc-manifest-sentence-2026-09-02.py); git -C "$GOV" show "$BC:governance/knowledge/decisions/drafts/build-dc-manifest-sentence-2026-09-02.py" \| shasum -a 256 \| cut -c1-16` |
| P5 | **`DRY_RUN`** — the success line, numstat, sizes | `BUILT: <out> edits=3 lines+1 bytes+3351 post=17/17`; `git diff --no-index --numstat -- "$GOV/DRAFTING_CYCLE.md" <out>` → `3	2` (exit 1 is the differing state — read the numbers); `wc -l <out>` → 370; `wc -c <out>` → 167,937 | as stated, scratch-only |
| P6 | **`GATE_BASELINE`** — a shipped plan's gate verdicts, BEFORE the edit (2.17's Item 4) | on `knowledge/decisions/Done/executable-100026.md` (sha `5138760431ae73f1`): `plan_lint` exit 0 — PASS 9 / WARN 5 / FAIL 0 / INFO 1 / PIN-CHECK 6; `cycle_check` → `BAR_MET` | `BPY scripts/plan_lint.py <plan>` counted by prefix; `BPY scripts/cycle_check.py <plan>` |

## Drafting Cycle

**Tier:** T2 — T-6 (doctrine), T-1 fire; T-8 does not (a structure clone). **Panel: SMALL form** (the magnitude proxy measured at walk 0, all three conditions holding) — the walk-0 scout (two cold readers), then EXECUTION, then CAPSTONE; the CEO may call the full form.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-dc-manifest-sentence-2026-09-02.md

**Walk 0 (context pin, measured):** _pending — entered from the register after the consumer dry-run and the scouts._

**Direction verdict (after walk 1):** _pending walk 1._

**Walks:**
- Weak spots:          _pending_
- Destruction:         _pending_
- Vulnerabilities:     _pending_
- Integration-record:  _pending_
- ACID:                _pending_

**Cold panel (SMALL form):** _not yet convened — the meter opens at the scouts' dispatch._

**Conformance (§5):** _pending walk 0's run._

**Closing:** _not closed._

---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer. ⚠️ Governance runs IN PLACE at `$GOV` (every operand ABSOLUTE); commits there by explicit pathspec; ONE action per compound.
>
> ⛔ **A0 — roots, then the branch ladder (catch-all LAST):** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK; `GOV=/Users/marklehn/Developer/eluvian-governance; DC="$GOV/DRAFTING_CYCLE.md"; B="$GOV/governance/knowledge/decisions/drafts/build-dc-manifest-sentence-2026-09-02.py"; [ -f "$DC" ] && [ -f "$B" ] && echo GOV_OK` — HALT unless GOV_OK. Re-derive `GOV`, `DC`, `B` in every compound. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`. Then the ladder — **(1)** P1's sha matches; **(2)** `git -C "$GOV" status --porcelain -- DRAFTING_CYCLE.md` (state it; EMPTY on FRESH); **(3)** `git -C "$GOV" log -1 --format=%s -- DRAFTING_CYCLE.md` — does the subject carry `dc-manifest-sentence`?
> - **FRESH** = (1) match AND (2) empty AND (3) no → A1.
> - **RE-ENTRY (doctrine landed)** = (3) yes AND (2) EMPTY (a dirty doctrine file on re-entry is a FOREIGN edit — HALT untouched, quoting the porcelain) → verify the COMMITTED state (the Task C counts on the live file, `wc -l` 370, and `C=$(git -C "$GOV" log -1 --format=%H -- DRAFTING_CYCLE.md); git -C "$GOV" show --stat --format= "$C" -- DRAFTING_CYCLE.md` → 3 insertions, 2 deletions — the PATH-SCOPED commit, never `HEAD`, which prints nothing once a later governance commit lands), then A4 only, the dev log marked `re-derived on re-entry`.
> - **NONE-MATCH** = anything else → HALT quoting every measurement. The ONE recipe: (1) mismatch + (3) no = a pre-commit apply that died — BUT ONLY IF the dirty file is THIS plan's build: `git -C "$GOV" diff HEAD --numstat -- DRAFTING_CYCLE.md` → `3	2` (against HEAD, never the bare index-relative `diff`, which prints NOTHING in the staged half-state) AND `git -C "$GOV" status --porcelain -- DRAFTING_CYCLE.md` → ` M` or `M ` (never `MM`) AND `/usr/bin/grep -cF -- 'ten REQUIRED fields' "$DC"` → 1 (a foreign hand edit presents the SAME (1)+(3) shape and must never be discarded; any other numstat or porcelain → HALT untouched, quoting it) → `git -C "$GOV" checkout HEAD -- DRAFTING_CYCLE.md` (`HEAD`, not the index — a death between `add` and `commit` leaves 2.24 STAGED), re-assert P1, then A1. Every other shape HALTs untouched.
>
> ⛔ **A1 — re-derive P1–P6; state each; a mismatch is a HALT quoting both.** (P4 with the builder's OWN commit, never `HEAD:`.) P6 is captured BEFORE the edit — after A3 the pre-edit state is gone and QA's Item 4 would compare against nothing.
>
> **A2 — dry-run, scratch→scratch (LITERAL paths, no variables across compounds):** `rm -rf /tmp/dc67; mkdir -p /tmp/dc67; python3 "$B" "$GOV/DRAFTING_CYCLE.md" /tmp/dc67/DC-out.md; echo "builder_exit=$?"` → P5's `BUILT:` line verbatim, `builder_exit=0`; `git diff --no-index --numstat -- "$GOV/DRAFTING_CYCLE.md" /tmp/dc67/DC-out.md` → `3	2`; `wc -l /tmp/dc67/DC-out.md` → 370; `wc -c` → 167937. Refusals (each `BUILDER REFUSED`, nonzero; quote each): `python3 "$B" "$GOV/DRAFTING_CYCLE.md" "$GOV/DRAFTING_CYCLE.md"` (out == in); `python3 "$B" "$GOV/DRAFTING_CYCLE.md" "$GOV/x.md"` (under a forbidden root); `python3 "$B" /tmp/dc67/DC-out.md /tmp/dc67/DC-out2.md` (already built).
>
> **A3 — apply and measure the LIVE file (Task C), then commit:** `cp /tmp/dc67/DC-out.md "$GOV/DRAFTING_CYCLE.md"`; then from the live file, counts read never exit codes (`/usr/bin/grep -cF --`): `ten REQUIRED fields` 1 · `three OPTIONAL fields` 1 · `one of the FOUR values` 1 · `compares ONLY the declared` 1 · `{read-only, governed-tooling, register-writing}` 0 · `HARD-HOLD` 2 · `HOLD-AND-REPORT` 2 · `**Version:** 2.24 (2026-09-02)` 1 · `**Version:** 2.23 (2026-09-01)` 0 · `- **2.24 (2026-09-02):** slug dc-manifest-sentence-2026-09-02` 1 · `- **2.23 (2026-09-01):** slug gate2-dc-w28-2026-09-01` 1 (the old row survives) · `validation: cycle_check=BAR_MET, plan_lint=0_FAIL` 1 (the §3 example untouched); `wc -l` 370; `cmp /tmp/dc67/DC-out.md "$GOV/DRAFTING_CYCLE.md"` silent; `git -C "$GOV" diff --stat -- DRAFTING_CYCLE.md` → 3 insertions, 2 deletions. Any failing → FRESH: `git -C "$GOV" checkout -- DRAFTING_CYCLE.md` + HALT; RE-ENTRY: HALT, no restore. Commit: `git -C "$GOV" add DRAFTING_CYCLE.md && git -C "$GOV" commit -m "[<id from your plan filename>] dc-manifest-sentence: DRAFTING_CYCLE v2.24 — the thread-67 sentence reconciled to depositor.py/plan_lint.py (no rule changed)" -- DRAFTING_CYCLE.md`; `git -C "$GOV" log --oneline -1 -- DRAFTING_CYCLE.md` → that commit. Do NOT push.
>
> **A4 — dev log + commit by explicit pathspec.** `knowledge/development/dev-log-dc-manifest-sentence-2026-09-02.md`: the A0 determination, A1's pins (P6 verbatim — the plan named, its counts and verdict token), A2's lines and the three refusals, A3's counts and the governance commit hash. `git add knowledge/development/dev-log-dc-manifest-sentence-2026-09-02.md && git commit -m "[<id>] dc-manifest-sentence: DC v2.24 landed (dev log)" -- knowledge/development/dev-log-dc-manifest-sentence-2026-09-02.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-dc-manifest-sentence-2026-09-02.md`
> - `/Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md`
>
> **Scope:**
> - `knowledge/development/dev-log-dc-manifest-sentence-2026-09-02.md`
> - `/Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `GOV=/Users/marklehn/Developer/eluvian-governance`; `B="$GOV/governance/knowledge/decisions/drafts/build-dc-manifest-sentence-2026-09-02.py"`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `dc-manifest-sentence-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/dc-manifest-sentence-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt`:**
> - **Item 1 — the live doctrine file:** `git -C "$GOV" log --oneline -1 -- DRAFTING_CYCLE.md` (the `[<id>]` commit); every Task C count re-run (twelve probes); `wc -l` 370; `git -C "$GOV" status --porcelain -- DRAFTING_CYCLE.md` → EMPTY.
> - **Item 2 — the builder, by a second pair of hands (byte-identity):** `rm -rf /tmp/dc67-qa; mkdir -p /tmp/dc67-qa; C=$(git -C "$GOV" log -1 --format=%H -- DRAFTING_CYCLE.md); git -C "$GOV" show "$C^:DRAFTING_CYCLE.md" > /tmp/dc67-qa/DC-pre.md; python3 "$B" /tmp/dc67-qa/DC-pre.md /tmp/dc67-qa/DC-out.md; echo "builder_exit=$?"; cmp /tmp/dc67-qa/DC-out.md "$GOV/DRAFTING_CYCLE.md" && echo BYTE_IDENTICAL` → the `BUILT:` line, `builder_exit=0`, `BYTE_IDENTICAL`; P4 with the builder's own commit; the three refusals reproduced.
> - **Item 3 — the sentence against the code, clause by clause, QUOTED FROM BOTH FILES:** for each of the four corrected clauses print the sentence's phrase (`grep -o` on the live file) beside the code line it cites (`sed -n` on `/Users/marklehn/Developer/bellows/depositor.py` `:156`, `:173-178`, `:184-186`, `:197`, `:307-314`, `:353`, `:362`, `:513-518`; `/Users/marklehn/Developer/bellows/scripts/plan_lint.py` `:552-556`, `:594`, `:596`, `:603`) and state that each agrees; `grep -rn 'collision_type' --include='*.py' /Users/marklehn/Developer/bellows` → the two writes and tests only; `grep -rn 'governed-tooling' --include='*.py' /Users/marklehn/Developer/bellows` → the lint set and tests only.
> - **Item 4 — no gate behaviour changed (P6):** `"$BPY" scripts/plan_lint.py knowledge/decisions/Done/executable-100026.md` counted by prefix and `"$BPY" scripts/cycle_check.py knowledge/decisions/Done/executable-100026.md` → the SAME counts and verdict token A1 recorded in the dev log (quote both). ⚠️ A comparison against a baseline you did not read is not a comparison.
>
> **(C) The report** `qa-receipt.md`: the verification table — status cells carry the glyph only; rows DESCRIBE the sentence's clauses and name the raw file, never quoting a landed body — the follow-ups (threads 72 and 74 next; the Planner pushes governance; thread 67 closes at the keyboard), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/ && git commit -m "[<id>] QA: DC v2.24 rebuilt byte-identical from the pre-edit blob; the sentence agrees with the code clause by clause; gates unchanged on a shipped plan" -- knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/probes-raw.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/probes-raw.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
