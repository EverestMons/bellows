# bellows — executable: DOCTRINE — COMPANY.md v2.8: a machine RUNS the shop, the mini is the SERVER, and that role is the only permitted difference between shops (one sentence, by a committed builder)

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full (the bellows suite is UNCHANGED by this plan and is run once by QA so the test gate reads a real summary line — the one named known failure — never a pre-declared override) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 1 | **Priority:** 2

**auto_close:** false

**Slug:** `shop-server-invariant-company-2026-09-02`

**Depends on:** the CEO, 2026-09-02 ("every machine becomes a shop … The mini is our server which should be the only difference"; "Both"); plan A `shop-server-invariant-sketch-2026-09-02` (held today; this plan's A0 HALTs until its addendum is in the live sketch — the sentence cites it. P6 reads the addendum ON DISK, which plan A commits in its Step 1 before its pauses — so B may run once A's Step 1 has landed, not only after A closes. Released BEFORE that, A0 halts before any write, the plan routes to `halted-`, and the id is consumed — the id prediction goes stale, nothing else); tuyere thread 86; `Done/executable-100008.md` in forge_lessons (the clone origin and the newest same-class plan: doctrine prose in a governance file by a COMMITTED builder from a project worktree, `git -C` never `cd`; closed 2026-09-01T19:58:22 by `lifecycle.db` — local time, the column is naive); the builder `governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py` (committed; digest below). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-shop-server-invariant-company-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-6 fires** — `COMPANY.md` is doctrine (the handbook that defines the shop) → **T2**. T-1 fires (two repos). T-8 fires (a clone by kind of 100008). T-2/T-3/T-5 no. **Panel form — the magnitude proxy, measured at walk 0 (all three must hold): (i) structure-clone** — the parent is 100008, closed 2026-09-01T19:58:22 (local), and both walk-0 clone-diffs ran (against 100008's final text and its register); **(ii) mechanized edits** — every mutation flows through the committed builder, whose three anchors are count-1-asserted BY EXECUTION and whose seven post-conditions are asserted on the output before any write (proven at walk 0 and again after the scout's fold: a scratch build, four refusals — live output, output under the governance root, an already-built input, a malformed date — a 6-line diff of exactly three changed lines, and a byte-identical rebuild from the pre-edit file); **(iii) scripted probes** — every post-condition is provably earnable against the pre-edit file: the three P3 tokens count 0 there and the two retired tokens (`**Version:** 2.7`, the old Last-Updated line) count 1 there. **→ SMALL form: the walk-0 scout, then EXECUTION, then CAPSTONE.** The CEO may call the full form.

## Why this exists

`COMPANY.md:59` defines the shop as the governance root ("The governance root is the shop — it contains the files … that define how all projects operate. Project repositories are workpieces the shop operates on."; blame `4b9b197f`, 2026-05-19). It says nothing about MACHINES, and in that silence the Air became "the shop" in the baton, in `MACHINE_SETUP.md` and in `bellows/CLAUDE.md`'s id-range law ("Shop machine: 1–99999"). The CEO's ruling today completes the definition: the root DEFINES the shop; a machine RUNS it; every machine under the process is a shop; the mini additionally holds the SERVER role (the private stores); that role is the only permitted difference. Plan A records the ruling and its consequences in the multi-machine sketch (the design record); this plan puts the one sentence that binds it into the handbook. The split follows DC §1: the code-free record half shipped at T1, the doctrine half bound as this named T2.

## What this plan does

**In the governance checkout, by absolute path (`GOV=/Users/marklehn/Developer/eluvian-governance`), three anchored edits to `COMPANY.md` by the committed builder (never by hand):**
- **E1** — after the sentence `Project repositories are workpieces the shop operates on.` (line 59, count 1), IN-LINE, the sentence: ` A MACHINE runs the shop when it carries the repos, a bellows daemon, a tuyere watcher and the hooks — every such machine is a shop, running the same code under the same rules; the Mac mini additionally holds the SERVER role, the one machine housing the private stores (tuyere's Postgres, the lessons DB), and that role is the only permitted difference between shops (CEO, 2026-09-02; the multi-machine sketch's addendum 2026-09-02).`
- **E2** — `**Version:** 2.7` → `**Version:** 2.8` (line 3, count 1).
- **E3** — `**Last Updated:** 2026-08-24 — added `tuyere` to Active Projects (CEO-directed)` → `**Last Updated:** <landing date> — the shop/server invariant: a machine runs the shop, the mini is the server, and that is the only difference (CEO-directed)` (line 4, count 1). The builder stamps the LANDING date at run time (today, local), or the `SSIC_DATE` environment variable (`YYYY-MM-DD`, validated) — so a release on a later day lands the right date with no re-commit, and QA can rebuild a committed output byte-identically by passing the date the live line carries (scout SC-2).

The builder reads the file as bytes, refuses CRLF, asserts each anchor's count is 1, asserts the output tokens are absent in the input, applies the three edits, asserts seven post-conditions on the OUTPUT (the E1 sentence 1, `A MACHINE runs the shop` 1, `**Version:** 2.8` 1, `**Version:** 2.7` 0, the new Last-Updated line 1, the old 0, `the only permitted difference between shops` 1), asserts the line count is unchanged (350) and the character delta equals the three edits (507 characters; 509 bytes — E1 carries one three-byte em dash), and only then writes — to a SCRATCH path it refuses to let be the live file or anything under the governance root. Apply = copy the proven scratch output over the live file, then re-measure the live file.

**In the bellows worktree:** the dev log only.

## What this plan does NOT do

- Does not touch the sketch (plan A's), `MACHINE_SETUP.md`, `GLOSSARY.md`, `ARCHITECTURE.md`, code or threads. Does not push (the Planner pushes after the pause). Does not decide the Air's layout.

## MUST-PRESERVE

- ⚠️ **TWO REPOSITORIES, ONE STEP.** Governance by absolute path, `git -C "$GOV"` never `cd`; porcelain EMPTY and sha = P1 before touching `COMPANY.md`; commit by explicit pathspec; no push.
- **The builder is the only writer.** Its committed blob digest must equal the on-disk file (P4) before it runs; it runs scratch→scratch; the live file is replaced only by `cp` of a scratch output whose post-conditions the builder already asserted, and the live file is then re-measured (Task C).
- ⛔ **Never run any `checkout --` on an A0 halt** — a pin mismatch means the file carries changes that are not this plan's (100008's rule).
- **`known_failures: 1`, named:** `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` from the worktree under the canonical venv. Any OTHER failure is a HALT/Critical.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`COMPANY_SHA`** and line count, pre-edit (v2.7) | `7883745e23467b4e`; 350 lines | `shasum -a 256 "$GOV/COMPANY.md" \| cut -c1-16`; `wc -l` |
| P2 | **`ANCHORS`** E1, E2, E3 | each count 1 (lines 59, 3, 4; lengths 712, 16, 81) | `/usr/bin/grep -cF -- '<anchor>' "$GOV/COMPANY.md"` |
| P3 | **`TOKENS`** 0 before, 1 after | `A MACHINE runs the shop` · `**Version:** 2.8` · `the only permitted difference between shops` | `/usr/bin/grep -cF` |
| P4 | **`BUILDER`** — on-disk digest = committed blob | `1aa29fcfd5d5ce50` (first 16 of sha-256, both; governance `392bae9`) | `shasum -a 256 <builder> \| cut -c1-16`; the blob at the builder's OWN last commit: `BC=$(git -C "$GOV" log -1 --format=%H -- <builder-relpath>); git -C "$GOV" show "$BC:<builder-relpath>" \| shasum -a 256 \| cut -c1-16` (never `HEAD:` — governance HEAD moves with every record commit) |
| P5 | **`DRY_RUN`** — the builder's success line and diff shape | `BUILT: <out> lines=350 delta_chars=507 delta_bytes=509 date=<today> edits=3 post=7/7`; `diff COMPANY.md <out> \| grep -c '^[<>]'` → 6 | as stated, scratch-only |
| P6 | **`ADDENDUM_LANDED`** (precondition: plan A closed) | `# Addendum 2026-09-02 — the shop/server invariant` count **1** in the live sketch | `/usr/bin/grep -cF -- '# Addendum 2026-09-02 — the shop/server invariant' "$GOV/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md"` |
| P7 | **`SUITE`** — from the worktree under the canonical venv | `1 failed, 1676 passed`; the one failure named above | `BPY -m pytest tests -q -p no:cacheprovider` |

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer.
>
> ⛔ **A0 — roots and the precondition, one compound each, stated in the dev log:** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK; `GOV=/Users/marklehn/Developer/eluvian-governance; B="$GOV/governance/knowledge/decisions/drafts/build-shop-server-invariant-company-2026-09-02.py"; [ -f "$GOV/COMPANY.md" ] && [ -f "$B" ] && echo GOV_OK` — HALT unless GOV_OK. **P6 → 1, else HALT with the message `plan A (shop-server-invariant-sketch) has not landed — the sentence cites its addendum`** (do not proceed; do not edit the sketch). Re-derive `GOV` and `B` in every compound. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`.
>
> ⛔ **A1 — re-derive P1–P4; state each; a mismatch is a HALT quoting both.** Then `git -C "$GOV" status --porcelain -- COMPANY.md` → EMPTY (else HALT: someone is editing it). ⛔ Never `checkout --` on a mismatch.
>
> **A2 — dry-run, scratch→scratch (the scratch dir is the LITERAL `/tmp/ssic-scratch` in every compound — no `$S`; 100008's walk-1 fold made every path literal because a variable set in one compound is empty in the next):** `rm -rf /tmp/ssic-scratch; mkdir -p /tmp/ssic-scratch; python3 "$B" "$GOV/COMPANY.md" /tmp/ssic-scratch/COMPANY-out.md; echo "builder_exit=$?"` → P5's `BUILT:` line (the `date=` field is today's local date) and `builder_exit=0`; `diff "$GOV/COMPANY.md" /tmp/ssic-scratch/COMPANY-out.md | /usr/bin/grep -c '^[<>]'` → 6; `wc -l /tmp/ssic-scratch/COMPANY-out.md` → 350. Then the refusals (each must print `BUILDER REFUSED` and exit nonzero; quote each): `python3 "$B" "$GOV/COMPANY.md" "$GOV/COMPANY.md"` (out == in); `python3 "$B" "$GOV/COMPANY.md" "$GOV/scratch-out.md"` (under the governance root); `python3 "$B" /tmp/ssic-scratch/COMPANY-out.md /tmp/ssic-scratch/COMPANY-out2.md` (already built: anchor count 0); `SSIC_DATE=tomorrow python3 "$B" "$GOV/COMPANY.md" /tmp/ssic-scratch/x.md` (malformed date).
>
> **A3 — apply and measure the LIVE file (Task C):** `cp /tmp/ssic-scratch/COMPANY-out.md "$GOV/COMPANY.md"`; then from the live file: P3's three tokens → 1 each; `**Version:** 2.7` → 0; the old Last-Updated line → 0; P2's E1 anchor → 1; `sed -n 4p "$GOV/COMPANY.md"` starts with `**Last Updated:** <today's date>` (quote it); `wc -l` → 350; `git -C "$GOV" diff --stat -- COMPANY.md` → 3 insertions, 3 deletions (state it); `cmp /tmp/ssic-scratch/COMPANY-out.md "$GOV/COMPANY.md"` → silent. Commit: `git -C "$GOV" add COMPANY.md && git -C "$GOV" commit -m "[<id from your plan filename>] COMPANY.md v2.8: a machine runs the shop, the mini is the server, the only permitted difference (CEO 2026-09-02)" -- COMPANY.md`; `git -C "$GOV" log --oneline -1 -- COMPANY.md` → that commit. Do NOT push.
>
> **A4 — dev-log + commit by explicit pathspec.** `knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md`: both roots, P6, A1's pins, A2's `BUILT:` line and the three refusal lines, A3's live measurements and the governance commit hash. `git add knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md && git commit -m "[<id>] shop/server invariant: COMPANY.md v2.8 committed in governance (dev log)" -- knowledge/development/dev-log-shop-server-invariant-company-2026-09-02.md`. `git status --short` → empty. STOP.
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
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/full-suite-shop-server-invariant-company.txt` → `1 failed, 1676 passed`, the one named known failure, `exit=1`.
>
> **(C) The report** `qa-receipt.md`: the verification table, the follow-ups restated (MACHINE_SETUP v1.3; the glossary act; the Planner pushes governance), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/ && git commit -m "[<id>] QA: COMPANY.md v2.8 rebuilt byte-identical from the pre-edit blob; tokens 3/3; refusals 3/3" -- knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/`. STOP.
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

---

## Drafting Cycle

**Tier:** T2 — T-6 (COMPANY.md is doctrine), T-1 (two repos), T-8 (a clone by kind) fire. **Panel: SMALL form** (the magnitude proxy measured at walk 0, all three conditions holding) — the walk-0 scout, then EXECUTION, then CAPSTONE; the CEO may call the full form.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-shop-server-invariant-company-2026-09-02.md

**Walk 0 (context pin, measured):** the target's sha, line count and last three writers; the three anchors' lines, lengths and counts; the retired tokens counted 1 and the new tokens 0 against the pre-edit file; the parent's close stamp read from the lifecycle DB (local time); the builder executed scratch-to-scratch with its refusals and its diff shape, its on-disk digest against its committed blob; the clone-diff against 100008's final text and its register in three passes; the consumer dry-run (§2.0) — class assigner, extractor per step, the `.txt` preference, the QA test gate's arithmetic read at source. **Scout (cold, local, lens 4, before lens 1): 10 findings, 0 HIGH, 0 DIRECTION** — 2 MED (a scratch variable not re-derived across compounds; a landing date baked into the builder) and 8 LOW; nine folded, one recorded; the builder re-committed date-dynamic and re-proven four ways including a byte-identical rebuild.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (COMPANY.md's shop definition is silent on machines — measured at its line 59 — and the CEO's ruling completes it), the mechanism (a committed builder whose anchors and post-conditions execute, the live file replaced only by a proven scratch output and re-measured), the scope (one sentence and the version header; the sketch, MACHINE_SETUP and the glossary are other plans' or wrap acts).

**Walks:**
- Weak spots:          w1 2 folded — instruction 1 / record 1 (the agent's greps switched to the absolute binary — the environment's grep is a shim; the proxy paragraph's evidence count updated to the re-proven set)
- Destruction:         w1 dry — three edits, all in-line or whole-line, line count unchanged, the pre-edit blob rebuilt byte-identically by QA; the never-`checkout --` rule carried
- Vulnerabilities:     w1 dry — literal scratch paths in every compound; `git -C` never `cd`; the builder refuses a live or in-root output four ways; the date validated
- Integration-record:  w1 dry — the manifest below is the emitter's, spliced at the freeze; the class the assigner measured; SC-8 (the deposit gate cannot see the governance commit) recorded as the reason QA Items 1–3 exist
- ACID:                w1 dry — governance commit before the dev-log commit, each by pathspec; a HALT between leaves COMPANY.md v2.8 committed-unpushed, visible at the pause
- **Walk 1 total: 2 findings, 2 folded — instruction 1 / record 1; 0 of 2 fold-introduced.**

**Status (after walk 1): the EXECUTION and CAPSTONE seats not yet convened — the record above is as of walk 1's fold round.**

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
