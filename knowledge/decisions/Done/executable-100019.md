# bellows — executable: DOCTRINE — COMPANY.md v2.8: a machine RUNS the shop, the mini is the SERVER, and that role is the only permitted difference between shops (one sentence, by a committed builder)

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full (the bellows suite is UNCHANGED by this plan and is run once by QA so the test gate reads a real summary line — `1676 passed, 1 skipped` in a worktree, which holds no `config.json` — never a pre-declared override) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `shop-server-invariant-company-2026-09-02`

**Depends on:** the CEO, 2026-09-02 ("every machine becomes a shop … The mini is our server which should be the only difference"; "Both"); plan A `shop-server-invariant-sketch-2026-09-02` (held today; this plan's A0 HALTs until its addendum is in the live sketch — the sentence cites it. P6 reads the addendum ON DISK, which plan A commits in its Step 1 — but plan A's QA Item 3 pins `COMPANY.md`'s sha as UNTOUCHED, so B landing inside A's verdict windows would HALT A: release B only after A CLOSES. Released before A's Step 1, A0 halts before any write and the plan PAUSES for a verdict (a Halted receipt fails the receipt-status gate; `halted-` is a verdict's outcome, not the agent's) — the id is consumed and the prediction goes stale, nothing else); tuyere thread 86; `Done/executable-100008.md` in forge_lessons (the clone origin and the newest same-class plan: doctrine prose in a governance file by a COMMITTED builder from a project worktree, `git -C` never `cd`; closed 2026-09-01T19:58:22 by `lifecycle.db` — local time, the column is naive); the builder `governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py` (committed; digest below). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-shop-server-invariant-company-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-6 fires** — `COMPANY.md` is doctrine (the handbook that defines the shop) → **T2**. T-1 fires (two repos). T-8 fires (a clone by kind of 100008). T-2/T-3/T-5 no. **Panel form — the magnitude proxy, measured at walk 0 (all three must hold): (i) structure-clone** — the parent is 100008, closed 2026-09-01T19:58:22 (local), and both walk-0 clone-diffs ran (against 100008's final text and its register); **(ii) mechanized edits** — every mutation flows through the committed builder, whose three anchors are count-1-asserted BY EXECUTION and whose seven post-conditions are asserted on the output before any write (proven at walk 0 and again after each builder re-commit: a scratch build, the refusals — live output, output under the governance root, an already-built input, a malformed date, an impossible date, an out-of-range date — a 6-line diff of exactly three changed lines, and a byte-identical rebuild from the pre-edit file); **(iii) scripted probes** — every post-condition is provably earnable against the pre-edit file: the three P3 tokens count 0 there and the two retired tokens (`**Version:** 2.7`, the old Last-Updated line) count 1 there. **→ SMALL form: the walk-0 scout, then EXECUTION, then CAPSTONE.** The CEO may call the full form.

## Why this exists

`COMPANY.md:59` defines the shop as the governance root ("The governance root is the shop — it contains the files … that define how all projects operate. Project repositories are workpieces the shop operates on."; blame `4b9b197f`, 2026-05-19). It says nothing about MACHINES, and in that silence the Air became "the shop" in the baton, in `MACHINE_SETUP.md` and in `bellows/CLAUDE.md`'s id-range law ("Shop machine: 1–99999"). The CEO's ruling today completes the definition: the root DEFINES the shop; a machine RUNS it; every machine under the process is a shop; the mini additionally holds the SERVER role (the private stores); that role is the only permitted difference. Plan A records the ruling and its consequences in the multi-machine sketch (the design record); this plan puts the one sentence that binds it into the handbook. The split follows DC §1: the code-free record half shipped at T1, the doctrine half bound as this named T2.

## What this plan does

**In the governance checkout, by absolute path (`GOV=/Users/marklehn/Developer/eluvian-governance`), three anchored edits to `COMPANY.md` by the committed builder (never by hand):**
- **E1** — after the sentence `Project repositories are workpieces the shop operates on.` (line 59, count 1), IN-LINE, the sentence: ` A MACHINE runs the shop when it carries the repos, a bellows daemon, a tuyere watcher and the hooks — every such machine is a shop, running the same code under the same rules; the Mac mini additionally holds the SERVER role, the one machine housing the private stores (tuyere's Postgres, the lessons DB), and that role is the only permitted difference between shops (CEO, 2026-09-02; the multi-machine sketch's addendum 2026-09-02).`
- **E2** — `**Version:** 2.7` → `**Version:** 2.8` (line 3, count 1).
- **E3** — `**Last Updated:** 2026-08-24 — added `tuyere` to Active Projects (CEO-directed)` → `**Last Updated:** <landing date> — the shop/server invariant: a machine runs the shop, the mini is the server, and that is the only difference (CEO-directed)` (line 4, count 1). The builder stamps the LANDING date at run time (today, local), or the `SSIC_DATE` environment variable (a REAL calendar date, not before 2026-09-02 and not after tomorrow — a malformed or out-of-range value is refused) — so a release on a later day lands the right date with no re-commit, and QA can rebuild a committed output byte-identically by passing the date the live line carries (scout SC-2).

The builder reads the file as bytes, refuses CRLF, asserts each anchor's count is 1, asserts the output tokens are absent in the input, applies the three edits, asserts seven post-conditions on the OUTPUT (the E1 sentence 1, `A MACHINE runs the shop` 1, `**Version:** 2.8` 1, `**Version:** 2.7` 0, the new Last-Updated line 1, the old 0, `the only permitted difference between shops` 1), asserts the line count is unchanged (350) and the character delta equals the three edits (507 characters; 509 bytes — E1 carries one three-byte em dash), and only then writes — to a SCRATCH path it refuses to let be the live file or anything under the governance root. Apply = copy the proven scratch output over the live file, then re-measure the live file.

**In the bellows worktree:** the dev log only.

## What this plan does NOT do

- Does not touch the sketch (plan A's), `MACHINE_SETUP.md`, `GLOSSARY.md`, `ARCHITECTURE.md`, code or threads. Does not push (the Planner pushes after the pause). Does not decide the Air's layout.

## MUST-PRESERVE

- ⚠️ **TWO REPOSITORIES, ONE STEP.** Governance by absolute path, `git -C "$GOV"` never `cd`; porcelain EMPTY and sha = P1 before touching `COMPANY.md`; commit by explicit pathspec; no push.
- **The builder is the only writer.** Its committed blob digest must equal the on-disk file (P4) before it runs; it runs scratch→scratch; the live file is replaced only by `cp` of a scratch output whose post-conditions the builder already asserted, and the live file is then re-measured (Task C).
- ⛔ **Never run any `checkout --` on an A0 halt** — a pin mismatch means the file carries changes that are not this plan's (100008's rule).
- **`known_failures: 0`.** From the worktree under the canonical venv the suite is `1676 passed, 1 skipped` (a worktree holds no `config.json`; the canonical checkout's one failure, `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged`, is a CWD-`config.json` property that does not occur there — measured 2026-09-02 in a real worktree's QA evidence and by this plan's EXECUTION seat). Any failure is a HALT/Critical.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`COMPANY_SHA`** and line count, pre-edit (v2.7) | `7883745e23467b4e`; 350 lines | `shasum -a 256 "$GOV/COMPANY.md" \| cut -c1-16`; `wc -l` |
| P2 | **`ANCHORS`** E1, E2, E3 | each count 1 (lines 59, 3, 4; lengths 712, 16, 81) | `/usr/bin/grep -cF -- '<anchor>' "$GOV/COMPANY.md"` |
| P3 | **`TOKENS`** 0 before, 1 after | `A MACHINE runs the shop` · `**Version:** 2.8` · `the only permitted difference between shops` | `/usr/bin/grep -cF` |
| P4 | **`BUILDER`** — on-disk digest = committed blob | `07374437b30be915` (first 16 of sha-256, both; governance `af5b216`) | `shasum -a 256 <builder> \| cut -c1-16`; the blob at the builder's OWN last commit: `BC=$(git -C "$GOV" log -1 --format=%H -- <builder-relpath>); git -C "$GOV" show "$BC:<builder-relpath>" \| shasum -a 256 \| cut -c1-16` (never `HEAD:` — governance HEAD moves with every record commit) |
| P5 | **`DRY_RUN`** — the builder's success line and diff shape | `BUILT: <out> lines=350 delta_chars=507 delta_bytes=509 date=<today> edits=3 post=7/7`; `diff COMPANY.md <out> \| grep -c '^[<>]'` → 6 | as stated, scratch-only |
| P6 | **`ADDENDUM_LANDED`** (precondition: plan A closed) | `# Addendum 2026-09-02 — the shop/server invariant` count **1** in the live sketch | `/usr/bin/grep -cF -- '# Addendum 2026-09-02 — the shop/server invariant' "$GOV/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md"` |
| P7 | **`SUITE`** — from the worktree under the canonical venv | `1676 passed, 1 skipped`, exit 0 | `BPY -m pytest tests -q -p no:cacheprovider` |

## Drafting Cycle

**Tier:** T2 — T-6 (COMPANY.md is doctrine), T-1 (two repos), T-8 (a clone by kind) fire. **Panel: SMALL form** (the magnitude proxy measured at walk 0, all three conditions holding) — the walk-0 scout, then EXECUTION, then CAPSTONE; the CEO may call the full form.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-shop-server-invariant-company-2026-09-02.md

**Walk 0 (context pin, measured):** the target's sha, line count and last three writers; the three anchors' lines, lengths and counts; the retired tokens counted 1 and the new tokens 0 against the pre-edit file; the parent's close stamp read from the lifecycle DB (local time); the builder executed scratch-to-scratch with its refusals and its diff shape, its on-disk digest against its committed blob; the clone-diff against 100008's final text and its register in three passes; the consumer dry-run (§2.0) — class assigner, extractor per step, the `.txt` preference, the QA test gate's arithmetic read at source. **Scout (cold, local, lens 4, before lens 1): 10 findings, 0 HIGH, 0 DIRECTION** — 2 MED (a scratch variable not re-derived across compounds; a landing date baked into the builder) and 8 LOW; nine folded, one recorded; the builder re-committed date-dynamic and re-proven four ways including a byte-identical rebuild.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (COMPANY.md's shop definition is silent on machines — measured at its line 59 — and the CEO's ruling completes it), the mechanism (a committed builder whose anchors and post-conditions execute, the live file replaced only by a proven scratch output and re-measured), the scope (one sentence and the version header; the sketch, MACHINE_SETUP and the glossary are other plans' or wrap acts).

**Walks:**
- Weak spots:          w1 2 folded — instruction 1 / record 1 (the agent's greps switched to the absolute binary — the environment's grep is a shim; the proxy paragraph's evidence count updated to the re-proven set)
- Destruction:         w1 dry — three edits, all in-line or whole-line, line count unchanged, the pre-edit blob rebuilt byte-identically by QA; the never-`checkout --` rule carried
- Vulnerabilities:     w1 dry — literal scratch paths in every compound; `git -C` never `cd`; the builder refuses a live or in-root output four ways; the date validated
- Integration-record:  w1 dry — the manifest is the emitter's, spliced at the freeze; the class the assigner measured; SC-8 (the deposit gate cannot see the governance commit) recorded as the reason QA Items 1–3 exist
- ACID:                w1 dry — governance commit before the dev-log commit, each by pathspec; a HALT between leaves COMPANY.md v2.8 committed-unpushed, visible at the pause
- **Walk 1 total: 2 findings, 2 folded — instruction 1 / record 1; 1 of 2 fold-introduced (the record lagging the builder's re-proof after the scout round).**

**Cold panel (SMALL form; meter opened at the scout's dispatch 10:58, before any seat):** SCOUT (lens 4, local, 138k tokens, 34 tool uses) — 10 findings, 0 HIGH, 0 DIRECTION, 9 folded / 1 recorded, instruction 3 / record 7: 2 MED (a scratch variable not re-derived across compounds; a landing date baked into the builder) and 8 LOW · EXECUTION (lens 3 + the execution brief, local, 149k tokens, 47 tool uses; 60 commands logged, 31 plan commands run, 29 matched, 2 mismatched) — 5 findings, 0 HIGH, 0 DIRECTION, 5 folded, instruction 2 / record 3, by lens: weak-spots 1 (X-4, pre-existing: the suite pin measured in the canonical checkout and carried to the worktree, where the failure never occurs — `known_failures: 0`, re-authored in four hunks and swept to plans A and bootstrap), vulnerabilities 2 (X-1: releasing B inside A's verdict windows would HALT A on its COMPANY.md pin — B runs after A CLOSES; X-2: the date check was shape-only — the builder now requires a real calendar date within [2026-09-02, tomorrow], re-committed and re-proven), integration-record 2 (X-3: "three refusal lines" where the steps carry four; X-5: the register's consumer line omitted the advisory test-scope WARN); 4 of 5 fold-introduced (the scout round's SC-10 and SC-2, the walk-1 block), 1 pre-existing · CAPSTONE (integration-record + ACID + the system brief, on the FOLD SET): convened next — its closure read is the closing walk's licence.

**Capstone (integration-record + ACID + the system brief, on the fold set; local, 215k tokens, 48 tool uses; the freeze checklist re-run on a scratch mirror, every pin re-derived, QA Item 2's rebuild under the final builder run for the first time → BYTE_IDENTICAL): 11 findings — 0 HIGH, 3 MED, 8 LOW; record 11 / instruction 0 (two with instruction consequences); 0 DIRECTION; the instruction class read DRY on the fold set.** Folded 10, one owed at close (the comparison row): the register's last line promised a re-read it did not carry; walk 1's fold-introduced count contradicted the register (1 of 2, not 0); the record block trailed the last step against §2.7's placement rule — moved above the first step heading, and the advisory test-scope WARN the trailing block had caused VANISHED with the move (the doctrine's geometry, measured); the panel round's class split restored on this line; "five sites" was four hunks; a stale register line about a baked date struck; the scout line's "P1–P7 as pinned" annotated (P7 had been measured from a `config.json` CWD); "the manifest below" reworded; an early release PAUSES for a verdict, it does not route to `halted-` (a Halted receipt fails the receipt-status gate); a RE-ENTRY rule added to A0 for death after A3's governance commit (the FRESH branch measured live today). **Panel meter vs the five-seat baseline (563k tokens / 45 findings / every HIGH from the aimed briefs):** three seats, 502k tokens, 26 findings, 0 HIGH, 0 DIRECTION — instruction 5 / record 21; the execution brief alone produced both mismatches that would have executed wrongly (a variable not re-derived; a pin from the wrong location).

- Weak spots:          w2 dry — instruction 0 / record 0 — the capstone's ten folds re-read in place; the A0 RE-ENTRY rule's probe run live (FRESH branch: the subject names v2.7, the tokens count 0); the Cycle Log covered as part of the artifact
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged (three edits, line count unchanged, byte-identical rebuild)
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — the moved block re-linted; the deposit extractor per step unchanged by the move
- Integration-record:  w2 dry — instruction 0 / record 0 — `propagation_check` clean; the manifest emitted at the freeze and spliced
- ACID:                w2 dry — instruction 0 / record 0 — governance commit (A3) before the dev-log commit (A4); a HALT between leaves v2.8 committed-unpushed and the RE-ENTRY rule resumes at A4; every commit by explicit pathspec
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 1 → 0 (warm walks); the panel's 26 findings folded between them.
- Weak spots:          w3 1 folded — instruction 1 / record 0 (a sibling seat's finding swept across the plan set: the suite summary line's word `skipped` is on the Rule 20 hedging list, and a QA receipt row quoting it beside a positive glyph fails the self-check — the report instruction now names the file and the exit, never the line)
- Destruction:         w3 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w3 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w3 dry — instruction 0 / record 0 — unchanged
- ACID:                w3 dry — instruction 0 / record 0 — unchanged
- **Walk 3 total: 1 finding, 1 folded — instruction 1 / record 0; 0 of 1 fold-introduced (origin: plan C's EXECUTION seat, X-2, swept here).**
- Weak spots:          w4 dry — instruction 0 / record 0 — the edited sentence re-read; the QA step's other cells unchanged; the Cycle Log covered
- Destruction:         w4 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w4 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w4 dry — instruction 0 / record 0 — the manifest re-emitted at this freeze
- ACID:                w4 dry — instruction 0 / record 0 — unchanged
- **Walk 4 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.**

**Conformance (§5):** first run at walk 0 (on v0) and re-run after every fold round and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×4 (worktree-relative deposits) once the block moved above the steps; `cycle_check` BAR_MET; `fold_check` re-baselined at each intended change with a note; `propagation_check` exit 0.

**Closing:** ✅ **BAR MET — walk 4 dry (all five lenses) after walk 1's two folds and three cold seats (scout 10, execution 5, capstone 11 — 25 folded, 1 recorded, 0 HIGH, 0 DIRECTION); T2 small form, panel discharged, the capstone's closure read covered the fold set and the freeze checklist.** Substrate present (the register's rows entered at each phase from captured output and committed at each phase, three lags recorded as lags; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T2
target: /Users/marklehn/Developer/eluvian-governance/COMPANY.md
class: shop-infra
reads: /Users/marklehn/Developer/eluvian-governance/COMPANY.md, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md, /Users/marklehn/Developer/forge_lessons/knowledge/decisions/Done/executable-100008.md, /Users/marklehn/Developer/bellows/knowledge/decisions/drafts/executable-shop-server-invariant-sketch.md
writes: /Users/marklehn/Developer/eluvian-governance/COMPANY.md, knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md, knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/qa-receipt.md, knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/probes-raw.txt, knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt
open_forks: the trailing-block geometry the two sibling held plans still carry (the parent's, gate-safe today, against §2.7's placement rule — a judged deviation recorded in their registers, the CEO's to overrule); whether `bellows/CLAUDE.md`'s "Shop machine" wording is MACHINE_SETUP v1.3's or a CLAUDE.md touch
walks: 4
yields: 1, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 4/4 walks have register rows


---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer.
>
> ⛔ **A0 — roots and the precondition, one compound each, stated in the dev log:** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK; `GOV=/Users/marklehn/Developer/eluvian-governance; B="$GOV/governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py"; [ -f "$GOV/COMPANY.md" ] && [ -f "$B" ] && echo GOV_OK` — HALT unless GOV_OK. **P6 → 1, else HALT with the message `plan A (shop-server-invariant-sketch) has not landed — the sentence cites its addendum`** (do not proceed; do not edit the sketch). **RE-ENTRY (the governance half already landed on an earlier attempt that died before A4):** if `git -C "$GOV" log -1 --format=%s -- COMPANY.md` contains `COMPANY.md v2.8` AND P3's three tokens count 1 in the live file → skip A2–A3, re-run Task C's counts and P4 on the live file, then A4 with that commit's hash. Otherwise FRESH (measured today: the subject is `COMPANY.md v2.7: add tuyere …`, P3 tokens 0). Re-derive `GOV` and `B` in every compound. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`.
>
> ⛔ **A1 — re-derive P1–P4; state each; a mismatch is a HALT quoting both.** Then `git -C "$GOV" status --porcelain -- COMPANY.md` → EMPTY (else HALT: someone is editing it). ⛔ Never `checkout --` on a mismatch.
>
> **A2 — dry-run, scratch→scratch (the scratch dir is the LITERAL `/tmp/ssic-scratch` in every compound — no `$S`; 100008's walk-1 fold made every path literal because a variable set in one compound is empty in the next):** `rm -rf /tmp/ssic-scratch; mkdir -p /tmp/ssic-scratch; python3 "$B" "$GOV/COMPANY.md" /tmp/ssic-scratch/COMPANY-out.md; echo "builder_exit=$?"` → P5's `BUILT:` line (the `date=` field is today's local date) and `builder_exit=0`; `diff "$GOV/COMPANY.md" /tmp/ssic-scratch/COMPANY-out.md | /usr/bin/grep -c '^[<>]'` → 6; `wc -l /tmp/ssic-scratch/COMPANY-out.md` → 350. Then the refusals (each must print `BUILDER REFUSED` and exit nonzero; quote each): `python3 "$B" "$GOV/COMPANY.md" "$GOV/COMPANY.md"` (out == in); `python3 "$B" "$GOV/COMPANY.md" "$GOV/scratch-out.md"` (under the governance root); `python3 "$B" /tmp/ssic-scratch/COMPANY-out.md /tmp/ssic-scratch/COMPANY-out2.md` (already built: anchor count 0); `SSIC_DATE=tomorrow python3 "$B" "$GOV/COMPANY.md" /tmp/ssic-scratch/x.md` (malformed date).
>
> **A3 — apply and measure the LIVE file (Task C):** `cp /tmp/ssic-scratch/COMPANY-out.md "$GOV/COMPANY.md"`; then from the live file: P3's three tokens → 1 each; `**Version:** 2.7` → 0; the old Last-Updated line → 0; P2's E1 anchor → 1; `sed -n 4p "$GOV/COMPANY.md"` starts with `**Last Updated:** <today's date>` (quote it); `wc -l` → 350; `git -C "$GOV" diff --stat -- COMPANY.md` → 3 insertions, 3 deletions (state it); `cmp /tmp/ssic-scratch/COMPANY-out.md "$GOV/COMPANY.md"` → silent. Commit: `git -C "$GOV" add COMPANY.md && git -C "$GOV" commit -m "[<id from your plan filename>] COMPANY.md v2.8: a machine runs the shop, the mini is the server, the only permitted difference (CEO 2026-09-02)" -- COMPANY.md`; `git -C "$GOV" log --oneline -1 -- COMPANY.md` → that commit. Do NOT push.
>
> **A4 — dev-log + commit by explicit pathspec.** `knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md`: both roots, P6, A1's pins, A2's `BUILT:` line and the four refusal lines, A3's live measurements and the governance commit hash. `git add knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md && git commit -m "[<id>] shop/server invariant: COMPANY.md v2.8 committed in governance (dev log)" -- knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md`
> - `/Users/marklehn/Developer/eluvian-governance/COMPANY.md`
>
> **Scope:**
> - `knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md`
> - `/Users/marklehn/Developer/eluvian-governance/COMPANY.md`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `GOV=/Users/marklehn/Developer/eluvian-governance`; `B="$GOV/governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py"`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `shop-server-invariant-company-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/shop-server-invariant-company-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-shop-server-invariant-company.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt` (`mkdir -p` the evidence dir first):**
> - **Item 1 — the governance commit and the live tokens:** `git -C "$GOV" log --oneline -1 -- COMPANY.md` (the `[<id>]` commit); P3's three tokens 1 each; `**Version:** 2.7` 0; `wc -l` 350; `git -C "$GOV" status --porcelain -- COMPANY.md` → EMPTY.
> - **Item 2 — the builder, by a second pair of hands (the parent's Item 2, C1 byte-identity):** one compound, literal paths: `rm -rf /tmp/ssic-qa; mkdir -p /tmp/ssic-qa; C=$(git -C "$GOV" log -1 --format=%H -- COMPANY.md); git -C "$GOV" show "$C^:COMPANY.md" > /tmp/ssic-qa/COMPANY-pre.md; D=$(sed -n 4p "$GOV/COMPANY.md" | /usr/bin/grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1); echo "landing_date=$D"; SSIC_DATE="$D" python3 "$B" /tmp/ssic-qa/COMPANY-pre.md /tmp/ssic-qa/COMPANY-out.md; echo "builder_exit=$?"; cmp /tmp/ssic-qa/COMPANY-out.md "$GOV/COMPANY.md" && echo BYTE_IDENTICAL` → `landing_date=` the date the live line carries, the `BUILT:` line with that `date=`, `builder_exit=0`, `BYTE_IDENTICAL` (the pre-edit blob rebuilt by the committed builder equals the live file byte for byte). Then P4 with the builder's OWN commit, not `HEAD:` — `BC=$(git -C "$GOV" log -1 --format=%H -- governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py); git -C "$GOV" show "$BC:governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py" | shasum -a 256 | cut -c1-16` equals the on-disk digest equals P4 — and the four refusals of A2 reproduced (quote each).
> - **Item 3 — nothing else moved:** `git -C "$GOV" status --porcelain -- COMPANY.md governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md` → EMPTY (a dirty file here is a HALT); `git -C "$GOV" status --porcelain | wc -l` stated as a number, informational.
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt` → `1676 passed, 1 skipped`, `exit=0` (a worktree holds no `config.json`, so the canonical checkout's known failure does not occur here).
>
> **(C) The report** `qa-receipt.md`: the verification table — status cells carry the glyph only, and the Expected/Evidence cells of the suite row name the FILE and `exit=0`, NEVER the summary line: its word `skipped` is on the Rule 20 hedging list (`hedging_keywords` in the canonical block) and a positive row carrying it FAILS the self-check (measured 2026-09-02 by plan C's execution seat) — the follow-ups restated (MACHINE_SETUP v1.3; the glossary act; the Planner pushes governance), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/ && git commit -m "[<id>] QA: COMPANY.md v2.8 rebuilt byte-identical from the pre-edit blob; tokens 3/3; refusals 4/4" -- knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
