# bellows — executable: DOCTRINE RECORD — the shop/server invariant lands in the multi-machine sketch (addendum 2026-09-02): every machine is a shop, the server role is the only difference, and threads 81/82 re-read under it

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full (the bellows suite is UNCHANGED by this plan and is run once by QA so the test gate reads a real summary line — `1676 passed, 1 skipped` in a worktree, which holds no `config.json` — never a pre-declared override) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `shop-server-invariant-sketch-2026-09-02`

**Depends on:** the CEO, 2026-09-02 ("every machine becomes a shop to work on projects … each machine running the same. The mini is our server which should be the only difference"; "Both" — this plan A and the bound plan B); tuyere thread 86 (the invariant; combine 81 + 82 under it) and threads 81, 82, 84, 85; `Done/executable-100016.md` in forge_lessons (the clone origin by kind — a governance file written by absolute path from a project worktree, TWO REPOSITORIES ONE STEP, `git -C` never `cd`) and the held plan `bellows-bootstrap-2026-09-02` (the newest same-class plan, this shape in bellows); the sketch's four prior addenda (governance `615ac8a`, `e046185`, `3b347a7`). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-shop-server-invariant-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-1 fires** (two repositories: bellows and eluvian-governance). **T-8 fires** (a clone by kind). T-6 no — the target is `governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md`, the multi-machine DESIGN RECORD (its own header: "a DIRECTION, not a plan"); it is not doctrine, the template, a gate or a contract, and every one of its four prior addenda landed by direct docs commit (`615ac8a`, `e046185`, `3b347a7`), never through a T-6 cycle. The doctrine half — one sentence in `COMPANY.md`'s "Shop-level vs Project-level" — is SPLIT OFF as plan B (`shop-server-invariant-company`, T2, bound: named here, drafted in the same session, not deferred); the cost of the split, said out loud: until B lands, `COMPANY.md` still reads "the governance root is the shop" without the sentence that every machine runs it. T-2/T-3/T-5 no (prose appended to one file; nothing runs elsewhere; nothing destructive). → **T1: five-lens walk, no panel.**

## Why this exists

The sketch is where every ruling of this arc has landed first: the SPOF decision (addendum 1), the provisioning leg (addendum 2), the lessons store (addendum 3), the idle machine as cold reader (addendum 4). Today the CEO gave the ruling that names the whole direction — *every machine is a shop; the mini is the server; that is the only difference* — and it changes how the two open design threads read: the seat-locality constraint in thread 81's sketch dissolves under identical shops, three of thread 82's open decisions are answered by "coordination facts on the server, artifacts in git", and uniformity becomes a hard precondition of the shared lane rather than a preference. None of that is written anywhere. `COMPANY.md:59` defines the shop as the governance root (measured, `4b9b197f`, 2026-05-19) — the ruling completes that definition (the root DEFINES the shop; a machine RUNS it) and retires the usage "the shop" = the Air that `MACHINE_SETUP.md` and the baton carry. The Air's state measured today by its own session (no bellows venv, CLT 3.9 with user-site packages, no `python3.12`, the `~/Developer/GitHub/` layout) is, under the ruling, setup debt with named closing acts — the sketch should say so.

## What this plan does

**In the governance checkout, by absolute path (`GOV=/Users/marklehn/Developer/eluvian-governance`), one edit:**
- **G1 — APPEND the addendum** (exact text below) to `governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md` after its final line. Anchor: the file's last sentence `it costs nothing the order does not already build.` (count 1; the file ends with a newline, measured `0a`). The append is one blank line, then the text. Nothing above it changes.

**In the bellows worktree:** the dev log only.

**The addendum, exact text (a quoted heredoc; every `$` and backtick literal):**
```
# Addendum 2026-09-02 — the shop/server invariant: every machine is a shop, and the server role is the only difference

> **CEO, 2026-09-02:** *"the idea is that every machine becomes a shop to work on projects. We now have the mini housing our private db. We have to start thinking about this in terms of multi eluvian shop setups, each machine running the same. The mini is our server which should be the only difference."*

## The invariant, stated

- **shop — a role, and `COMPANY.md`'s definition stands.** The governance root IS the shop: it holds the files that define how every project operates (`COMPANY.md`, "Shop-level vs Project-level"). A MACHINE runs the shop when it carries the repos, a bellows daemon, a tuyere watcher and the hooks — so every machine under the process is a shop, and "the shop" as the name of one machine (the Air; `~/Developer/GitHub/`; plan ids 1–99999) is retired usage. Say "the Air", "the mini"; say "a shop" for the role.
- **server — one extra role, held by the mini: the private stores.** Measured 2026-09-02: tuyere's Postgres at `localhost:5432` on the mini, reachable over the tailnet (`tuyere/docs/SERVER.md`, the always-on host decided 2026-08-24); `forge_lessons/lessons-forge.db` — one live copy, on the mini (CEO, 2026-09-01; addendum 3). Every other shop reaches shared state over the tailnet and holds no private store.
- **the only difference.** Two shops run the SAME code (git), under the SAME interpreter rule (`bellows/.venv/bin/python` for every bellows tool, test and the daemon — `MACHINE_SETUP.md` §2; the same for each repo's own venv), from the SAME package declarations (`requirements.txt`, installed by each repo's `scripts/bootstrap.sh`), with the SAME hook registration and the SAME checks. `MACHINE_SETUP.md` §0's per-machine axis (`config.json`, venvs, the id block, launchd agents, hook registration) is PROVISIONING of one shape, not a second shape. The pair "server / not server" is the one asymmetry the design accepts.
- **setup debt — what it means when two shops differ on anything else.** A difference in layout, interpreter, package source, config form or hook install is not a supported variant; it is debt, named with its closing act. Measured on the Air 2026-09-02 (by the Air's own session, read-only): no bellows or forge venv and a daemon on the Command Line Tools 3.9.6 with user-site packages → closed by plan `bellows-bootstrap-2026-09-02` + thread 84's operator act; no `python3.12` → install `python@3.12` before the bootstraps run, so both shops build the same venv; the `~/Developer/GitHub/` layout → an operator move of the Air's checkouts to the mini's shape, then the resolver trim (`bellows_root.resolve_governance_root` admits two shapes today) — a decision owed to the CEO, not taken here.

## What the invariant does to threads 81 and 82

- **The seat-locality constraint dissolves.** Thread 81's sketch and the 2026-09-01 register held that EXECUTION and CAPSTONE seats must run where the DB, the venv and the daemon live. Under identical shops every machine has the venv and the daemon, and the store is reached over the tailnet; any idle shop can run any seat class, and addendum 4's cold-reader role becomes fully dynamic — whichever live shop holds no active claim.
- **Three of thread 82's open decisions are answered by the model, not by preference:** the seat report returns as a ROW on the server (coordination facts on the server, artifacts in git — the daemon stays push-free); lifecycle state moves to the server with each shop's `lifecycle.db` as a PROJECTION plus a local read cache (a shop stays sighted on its own in-flight work when the server is unreachable); the shared `id_sequence` falls out of that move and retires the id-block law.
- **Uniformity is a PRECONDITION of the shared drafting lane, not a nicety.** A lane watched by several daemons is exactly the double-dispatch channel the stage-3 gate exists for (`MACHINE_SETUP.md` §4; `bellows/CLAUDE.md`); stage 3 requires every shop to run the same lock mode with the same eligible classes. A shop that drifted in code, interpreter or config is a shop that can misjudge a draft every other shop trusts.
- **The sequence is unchanged; provisioning is its step 2.** Liveness that reflects the daemon → provisioning (`bellows-bootstrap`, thread 85's asserts) → stage 3 on every shop → the seat class → lifecycle to the server → materialization by sha → the drafting stage (thread 81). Diagnostic 100014 prices the last step honestly: a daemon-run battery removes the SKIP and MISREAD classes (8 of 14 recorded incidents) and cannot remove TOOL-DEFECT (5 of 14) — the checker fixes (threads 52, 58, 63) are a precondition of the drafting stage, not a side effect.

## Where it lands next (bound, not deferred)

- `COMPANY.md` "Shop-level vs Project-level": the sentence that a machine runs the shop and the server is the mini's one extra role — plan B, T-6, its own T2 cycle (`shop-server-invariant-company-2026-09-02`).
- `MACHINE_SETUP.md` v1.3: the vocabulary (lines that say "the shop" for the Air) and a §0 row for what the server holds — a T1 after `bellows-bootstrap` closes (its write set holds that file tonight).
- `GLOSSARY.md`: `shop` and `server` — definitions, a wrap act.
- Threads: 86 (this invariant), 84, 85; 81 and 82 re-read under it, unchanged in text.
```

## What this plan does NOT do

- Does not touch `COMPANY.md`, `MACHINE_SETUP.md`, `GLOSSARY.md`, `ARCHITECTURE.md`, doctrine, code, or any thread — each is named above with its own act. Does not push (the Planner pushes after the pause).
- Does not decide the Air's layout move (a CEO decision, recorded as owed).

## MUST-PRESERVE

- ⚠️ **TWO REPOSITORIES, ONE STEP.** The governance edit happens in the LIVE governance checkout at `$GOV` by absolute path — `git -C "$GOV"` for every git act there, never `cd`. Before touching it: `git -C "$GOV" status --porcelain -- <the sketch path>` must be EMPTY and `shasum` of the file must equal P1's — a dirty or moved file is a HALT. Commit there by explicit pathspec; do not push.
- **The anchor count-asserted BEFORE the append** (1), and the append proven by tokens that are 0 before and 1 after (P3), with a script — never a blind `cat >>`.
- **Append only.** `git -C "$GOV" diff --stat` must show insertions only, 0 deletions; the pre-edit file's every line is still present (P4).
- **`known_failures: 0`.** From the worktree under the canonical venv the suite is `1676 passed, 1 skipped` (a worktree holds no `config.json`; the canonical checkout's one failure, `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged`, is a CWD-`config.json` property that does not occur there — measured 2026-09-02 in a real worktree's QA evidence and twice in scratch). Any failure is a HALT/Critical.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`SKETCH_SHA`** and line count, pre-edit | `4508b20abb79eac8`; 231 lines; last writer `3b347a7` | `shasum -a 256 "$GOV/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md" \| cut -c1-16`; `wc -l`; `git -C "$GOV" log --oneline -1 -- <path>` |
| P2 | **`ANCHOR`** — the final sentence | `it costs nothing the order does not already build.` count 1; the file ends in `0a` | `/usr/bin/grep -cF`; `tail -c 1 \| xxd` |
| P3 | **`TOKENS`** — 0 before, 1 after | `# Addendum 2026-09-02` · `every machine is a shop, and the server role is the only difference` · `## The invariant, stated` · `## What the invariant does to threads 81 and 82` · `## Where it lands next (bound, not deferred)` | `/usr/bin/grep -cF` each |
| P4 | **`APPEND_ONLY`** post-edit | `git -C "$GOV" diff --stat -- <path>` → insertions only, `0 deletions`; `git -C "$GOV" show HEAD:<path> \| diff - <path>` → only `>` lines | as stated |
| P5 | **`SUITE`** — from the worktree under the canonical venv | `1676 passed, 1 skipped`, exit 0 | `BPY -m pytest tests -q -p no:cacheprovider` |
| P6 | **`COMPANY`** untouched | `COMPANY.md` sha `7883745e23467b4e` before and after | `shasum` |

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer.
>
> ⛔ **A0 — resolve BOTH roots in one compound and state both in the dev log:** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK; `GOV=/Users/marklehn/Developer/eluvian-governance; SK="$GOV/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md"; [ -f "$SK" ] && [ -f "$GOV/COMPANY.md" ] && echo GOV_OK` — HALT unless GOV_OK. Re-derive `GOV` and `SK` in every compound. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`.
>
> ⛔ **A1 — re-derive P1, P2, P3 (all five tokens 0), P6; state each; a mismatch is a HALT quoting both.** Then `git -C "$GOV" status --porcelain -- "$SK"` → EMPTY (else HALT: someone is editing it).
>
> **A2 — G1 by one script:** write the addendum text to a temp file with a QUOTED heredoc delimiter (nothing expands), assert P2's count is 1 and P3's five tokens are 0, then append (one blank line, then the text), then assert P3's five tokens are 1 and P2's anchor still 1. Then P4: `git -C "$GOV" diff --stat -- "$SK"` (state it: insertions only, 0 deletions) and `git -C "$GOV" show HEAD:governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md | diff - "$SK" | grep -c '^<'` → 0.
>
> **A3 — commit in governance by explicit pathspec:** `git -C "$GOV" add governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md && git -C "$GOV" commit -m "[<id from your plan filename>] multi-machine sketch addendum 2026-09-02: the shop/server invariant — every machine is a shop, the server role is the only difference; threads 81/82 re-read under it" -- governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md`; `git -C "$GOV" log --oneline -1 -- <path>` → that commit. Do NOT push. P6 again → unchanged.
>
> **A4 — dev-log + commit by explicit pathspec.** `knowledge/development/dev-log-shop-server-invariant-sketch-2026-09-02.md`: both roots, A1's pins, A2's token counts before and after, P4's lines, the governance commit hash. `git add knowledge/development/dev-log-shop-server-invariant-sketch-2026-09-02.md && git commit -m "[<id>] shop/server invariant: sketch addendum committed in governance (dev log)" -- knowledge/development/dev-log-shop-server-invariant-sketch-2026-09-02.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-shop-server-invariant-sketch-2026-09-02.md`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md`
>
> **Scope:**
> - `knowledge/development/dev-log-shop-server-invariant-sketch-2026-09-02.md`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `GOV=/Users/marklehn/Developer/eluvian-governance`; `SK="$GOV/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md"`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `shop-server-invariant-sketch-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-shop-server-invariant-sketch.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt` (`mkdir -p` the evidence dir first):**
> - **Item 1 — the governance commit and tokens:** `git -C "$GOV" log --oneline -1 -- "$SK"` (the `[<id>]` commit); P3's five tokens each count 1; P2's anchor count 1; `wc -l "$SK"` → 256 (231 + a blank line + the addendum's 24 lines — measured at walk 0); `git -C "$GOV" status --porcelain -- "$SK"` → EMPTY.
> - **Item 2 — append-only, by a second pair of hands:** `C=$(git -C "$GOV" log -1 --format=%H -- governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md); git -C "$GOV" show "$C^:governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md" | diff - "$SK"` (the addendum commit's PARENT is the pre-edit state — never `HEAD~1`, which is whatever landed last in governance) → every line begins with `>` (count the `<` lines: 0); the first `>` line is blank and the second is the addendum heading — quote both.
> - **Item 3 — nothing else moved:** `COMPANY.md` sha = P6; `git -C "$GOV" status --porcelain -- "$SK" COMPANY.md` → EMPTY (a dirty sketch or COMPANY.md is a HALT); then `git -C "$GOV" status --porcelain | wc -l` stated as a number, informational (other files in the governance checkout are the Planner's records, not this plan's).
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/full-suite-shop-server-invariant-sketch.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/full-suite-shop-server-invariant-sketch.txt` → `1676 passed, 1 skipped`, `exit=0` (the suite is unchanged by this plan; a worktree holds no `config.json`, so the canonical checkout's known failure does not occur here).
>
> **(C) The report** `qa-receipt.md`: the verification table — status cells carry the glyph only, and the Expected/Evidence cells of the suite row name the FILE and `exit=0`, NEVER the summary line: its word `skipped` is on the Rule 20 hedging list (`hedging_keywords` in the canonical block) and a positive row carrying it FAILS the self-check (measured 2026-09-02 by plan C's execution seat) — the bound follow-ups restated (plan B; MACHINE_SETUP v1.3; the glossary act; the Planner pushes governance), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/ && git commit -m "[<id>] QA: sketch addendum 2026-09-02 verified append-only; tokens 5/5" -- knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/full-suite-shop-server-invariant-sketch.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/full-suite-shop-server-invariant-sketch.txt`

---

## Drafting Cycle

**Tier:** T1 — T-1 (two repos), T-8 fire; T-6 does not (the sketch is the design record, its four prior addenda direct commits; the doctrine sentence is split to plan B, bound). Five-lens walk, no panel.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-shop-server-invariant-2026-09-02.md

**Walk 0 (context pin, measured):** the sketch's sha, line count and last three writers; the append anchor counted (1) and the trailing newline read as a byte; the five post-edit tokens counted 0 before authoring; `COMPANY.md`'s sha and the blame of its shop sentence; every fact the addendum states re-measured live in one pass (id ranges, the always-on date, the resolver's shapes, the stage-3 sentence, the thread titles, the Air's survey, diagnostic 100014's sentence); the clone-diff against the held bootstrap plan and 100016 in three passes; the consumer dry-run (§2.0) on the register's walk-0 line — class assigner `shop-infra`, extractor per step, the `.txt` preference.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (the ruling is the CEO's, quoted; the sketch is where every ruling of the arc landed first, by its own history), the mechanism (one append proven by tokens 0→1 and an append-only diff against the addendum commit's parent), the scope (the doctrine sentence, MACHINE_SETUP v1.3 and the glossary act are named and bound, not folded in).

**Walks:**
- Weak spots:          w1 3 folded — instruction 3 / record 0 (QA's pre-edit reference was `HEAD~1`, which is whatever landed last in governance — replaced by the addendum commit's own parent; QA Item 3's "nothing else moved" was vague — made a two-file porcelain HALT plus an informational count; the post-edit line count was an expression — stated as the measured 256)
- Destruction:         w1 dry — an append only; the pre-edit file's every line proven present by the diff's `<` count; nothing removed anywhere
- Vulnerabilities:     w1 dry — a quoted heredoc for the addendum (backticks and dollars literal); `git -C` never `cd`; roots re-derived per compound; the anchor asserted before the append
- Integration-record:  w1 dry — the manifest below is the emitter's, spliced at the freeze; the class the assigner measured
- ACID:                w1 dry — governance commit before the bellows dev-log commit, each by explicit pathspec; a HALT between leaves a committed-but-unpushed addendum visible at the pause
- **Walk 1 total: 3 findings, 3 folded — instruction 3 / record 0; 0 of 3 fold-introduced.**

- Weak spots:          w2 dry — instruction 0 / record 0 — the three folded sites re-read; the addendum text re-read whole against its measured facts; the Cycle Log covered
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w2 dry — instruction 0 / record 0 — `propagation_check` clean; release order noted in the register (the bootstrap plan first, so the addendum's `MACHINE_SETUP.md` §2 citation names the universal rule v1.2 lands)
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 3 → 0.
- Weak spots:          w3 1 folded — instruction 1 / record 0 (a sibling seat's finding swept across the plan set: the suite pin was measured in the canonical checkout and carried to the worktree, where the one failure never occurs — `known_failures: 0`, P5, the MUST-PRESERVE bullet, the header and QA Item 4 re-authored to `1676 passed, 1 skipped`, exit 0)
- Destruction:         w3 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w3 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w3 dry — instruction 0 / record 0 — unchanged
- ACID:                w3 dry — instruction 0 / record 0 — unchanged
- **Walk 3 total: 1 finding, 1 folded — instruction 1 / record 0; 0 of 1 fold-introduced (origin: plan B's EXECUTION seat, X-4, swept here).**
- Weak spots:          w4 dry — instruction 0 / record 0 — the five edited sites re-read; the Cycle Log covered
- Destruction:         w4 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w4 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w4 dry — instruction 0 / record 0 — the manifest re-emitted at the second freeze
- ACID:                w4 dry — instruction 0 / record 0 — unchanged
- **Walk 4 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 3 → 0 → 1 → 0.
- Weak spots:          w5 1 folded — instruction 1 / record 0 (a sibling seat's finding swept across the plan set: the suite summary line's word `skipped` is on the Rule 20 hedging list, and a QA receipt row quoting it beside a positive glyph fails the self-check — the report instruction now names the file and the exit, never the line)
- Destruction:         w5 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w5 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w5 dry — instruction 0 / record 0 — unchanged
- ACID:                w5 dry — instruction 0 / record 0 — unchanged
- **Walk 5 total: 1 finding, 1 folded — instruction 1 / record 0; 0 of 1 fold-introduced (origin: plan C's EXECUTION seat, X-2, swept here).**
- Weak spots:          w6 dry — instruction 0 / record 0 — the edited sentence re-read; the QA step's other cells unchanged; the Cycle Log covered
- Destruction:         w6 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w6 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w6 dry — instruction 0 / record 0 — the manifest re-emitted at this freeze
- ACID:                w6 dry — instruction 0 / record 0 — unchanged
- **Walk 6 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.**

**Conformance (§5):** first run at walk 0 (shape-stability, on v0) and re-run after walk 1's folds and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×4 (worktree-relative deposits); `cycle_check` BAR_MET; `fold_check` baseline re-saved at each intended change with a note; `propagation_check` exit 0.

**Closing:** ✅ **BAR MET — walk 6 dry (all five lenses) after walk 1's three folds and walk 3's one (a sibling seat's location finding, swept in after the first freeze); T1, no panel owed, none convened.** Substrate present (the register's rows entered at each phase from captured output and committed at each phase; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md
class: shop-infra
reads: /Users/marklehn/Developer/eluvian-governance/COMPANY.md, /Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/bellows-drafting-stage-design-sketch-2026-09-01.md, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/bellows-tuyere-dispatch-analysis-2026-09-01.md, /Users/marklehn/Developer/bellows/knowledge/research/drafting-stage-pricing-2026-09-02.md, /Users/marklehn/Developer/bellows/bellows_root.py, /Users/marklehn/Developer/tuyere/docs/SERVER.md
writes: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/architecture/multi-machine-project-status-2026-08-31.md, knowledge/development/dev-log-shop-server-invariant-sketch-2026-09-02.md, knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/qa-receipt.md, knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/probes-raw.txt, knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/full-suite-shop-server-invariant-sketch.txt
open_forks: the Air's repo layout (move to the mini's shape, then the resolver trim) — a CEO decision the addendum records as owed; whether the seat class under identical shops needs any machine affinity at all
walks: 6
yields: 3, 0, 1, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 6/6 walks have register rows


Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
