# bellows — `lens_commit.py` REFUSES A `--desc` THAT NAMES A LENS OR WALK NUMBER, USING THE OBSERVER'S OWN TOKEN REGEXES — the description is part of the subject the record is read from, and one description turned a correct lens-5 commit into a batched, out-of-order, repeated breach (thread 271)

**Date:** 2026-09-10 | **Project:** bellows | **Tier:** Small (one script gains one check at its assert step, one test file gains three tests, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — the tool imports the observer's regexes; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 271

**auto_close:** false

**Post-close:** no restart (`lens_commit.py` is Planner-side, run per invocation). No doctrine: DRAFTING_CYCLE:196 already says the observer reads `walk <N>` and `lens <M>` anywhere in the subject line and that a subject names EXACTLY ONE lens — this plan makes the tool that composes the subject refuse the one input that can break that rule. STANDING_CONSTRAINTS line 1 stays as written (the tool now enforces the clause its register already carries: "no lens or walk number in any `--desc`").

**Depends on:** bellows #100065 (Done 2026-09-10, thread 266 — the tool commits folding lenses now, so this guard runs on every commit of a cycle, not only dry ones); #100063 (thread 270 — the record rule at step 0; this guard sits at step 4, after it); the CEO's 2026-09-10 history rewrite of governance commit `5768483`'s subject (path 1), the repair this guard makes unnecessary. Clone origin by kind: `Done/executable-100065.md` (the same tool, one gate, three tests); by layout: the closed 266 draft. In flight: none.

**Tier computed (§1):** **T1** — T-1 fires (one script, one test file); T-6 does NOT fire — Planner-side tool, no daemon gate changes (100061/100065's reasoning); T-2 does not.

## CEO Context

`scripts/lens_order_check.py` reads a lens commit's WHOLE subject line for `walk N` and `lens M` tokens (P2 — `_WALK_RE`, `_LENS_RE`, case-insensitive, anywhere in the line), because DRAFTING_CYCLE:196 fixes the subject as the record. `scripts/lens_commit.py` composes that subject as `draft(<slug>): walk <N> lens <n> — <NAME>: <desc>` and never looks at `desc`. On 2026-09-10 the 270 cycle's walk-3 lens-5 commit carried the description "…C4 refusal order, slug guard, QA lens 2; C5…": the observer read lenses `[5, 2]` in one commit — BATCHED — then OUT-OF-ORDER and REPEATED for the walk, `close_cycle.py` refused at its battery, and the deposit would have held on a breach with no release arm. A later commit cannot repair a commit-ordered read; the CEO rewrote that one subject by history (P1). The register's own rule since that morning — "no lens or walk number in any `--desc`" — is a sentence the author must remember. This plan puts it where the subject is composed: the tool refuses the description before anything is written, using the observer's regexes so the two can never disagree on what a token is.

## What this changes

1. **`scripts/lens_commit.py` step 4** (`:273–280`, the compose-and-assert step): before composing the subject, `import lens_order_check` (the sibling module in `scripts/` — the tool's `run_checker` already resolves `SCRIPTS`; the import uses the same directory on `sys.path`, the ONE-copy rule) and refuse when `lens_order_check._LENS_RE.search(desc)` or `lens_order_check._WALK_RE.search(desc)` matches: `LENS-COMMIT: assert FAIL — --desc must not name a lens or walk number (the observer reads every token in the subject line): <desc>`; exit 1; nothing written (step 4 precedes every write except step 3's yield-rising WARN line, which is the existing order). The regexes are the observer's own objects, not copies: `\bwalk\s+(\d+)\b` and `\blens\s+(\d+(?:\s*/\s*\d+)*)`, both `IGNORECASE` (P2) — so "QA lens 2", "Lens 2", "walk 0 seed" and "lens 1/4" refuse, while "lenses", "walks", "lens-2" and "the second lens" pass — checked against the regexes' letters: `\bwalk\s+` needs whitespace after `walk`, so `walks` (an `s`) does not match; `\blens\s+` likewise passes `lens-2` and `lenses` (the observer reads none of those either). The module docstring's step-4 line becomes `4. assert — subject lens name checked against internal table; --desc must not name a lens or walk number`.
2. **`tests/test_lens_commit.py`** — three tests, failing-first, on `_make_lens_fixture` (19 tests today, P3; this plan's are l17–l19): **l17**: `--desc "QA lens 2"` with `--dry` on the unedited fixture → rc 1, stdout carries `assert FAIL — --desc must not name a lens or walk number`, `git rev-list --count HEAD` unchanged; **l18**: `--desc "walk 0 seed"` → the same refusal; **l19**: `--desc "lenses and walks in prose, lens-2 style"` → rc 0 and `commit OK` (no token the observer reads). Every existing test's `--desc` is `test`, `fold`, `dry`, `test fixture`, `echo-test`, `fail-test` or `b-check`-shaped (P3) — none refuses.
3. **`knowledge/mutants/lens-commit-desc-guard.json`** — at least three mutants (`target: scripts/lens_commit.py`; every `expect_fail` a plain `tests/test_lens_commit.py::<test>` node id): the guard removed (l17); the walk half removed (l18); the guard widened to refuse the bare word `lens` (l19 — the inverse mutant, so the guard cannot grow past the observer's reading).
4. **Not changed:** `lens_order_check.py` (its regexes are imported, never edited), steps 0–3 and 5, every other test. The diff touches two files plus the manifest, the run file and the dev-log.

## Why this exists

The record is read from subjects, and the subject is composed from the author's words. A rule that lives in a register sentence is met by memory; the same rule at the point of composition is met by the tool. The cost of the miss was a history rewrite the CEO had to run.

## What this does NOT do

- Does not change what the observer reads (DRAFTING_CYCLE:196 stands); does not refuse hand commits — a hand commit stays the author's risk, and the standing rule stays in words for it.
- Does not scan the slug (`draft(<slug>)` never carries a lens token — the slug is the file stem).

## MUST-PRESERVE

- ⛔ **One regex, two readers.** The guard imports the observer's regex objects; it never copies the pattern.
- ⛔ **A refusal writes nothing.** The guard runs before step 5 and before the DRY append.
- ⛔ **Suite green at both commits;** nothing outside the two files moves.

## Numbers discipline — measured 2026-09-10 by the Planner (bellows `ba74706`, governance `88f42fa6`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the incident | governance commit `5768483` (walk 3 lens 5 of the 270 cycle, subject ending `… QA lens 2; C5 l11 + three mutants)`): `lens_order_check` on the draft → `BATCHED: walk 3 — 5768483 names lenses [5, 2] in ONE commit`, `OUT-OF-ORDER: walk 3 — lens commits land in order [1, 2, 3, 4, 5, 2]`, `REPEATED: walk 3 — lens [2] passed more than once`; repaired only by the CEO's `git filter-branch --msg-filter` over sixteen commits (`5768483` → `bb0e96a5`, 2026-09-10); thread 271 filed the same hour | `git -C <governance> log --format='%h %s' --grep='walk 3 lens 5' -- governance/knowledge/decisions/drafts/executable-bellows-lens-record-visibility.md` (the rewritten subject) |
| P2 | ⛔ the observer's tokens | `scripts/lens_order_check.py:70` `_WALK_RE = re.compile(r"\bwalk\s+(\d+)\b", re.IGNORECASE)`; `:76` `_LENS_RE = re.compile(r"\blens\s+(\d+(?:\s*/\s*\d+)*)", re.IGNORECASE)`; `:82` `_CONT_RE`; `commit_record` `:92` applies both to every subject and keeps a row when BOTH match | `sed -n '70p;76p' scripts/lens_order_check.py` |
| P3 | ⛔ the tool and its tests as they stand | `scripts/lens_commit.py` (sha `b4644b8ab55d`, last writer #100065): step 4 `:273–280` — `composed_name = LENS_NAMES[lens_n]` `:274`, the name assert `:276–278`, `subject = f"draft({slug}): walk {walk_n} lens {lens_n} — {composed_name}: {desc}"` `:280`; `desc = args.desc` at `:96`, never inspected; `tests/test_lens_commit.py`: 19 tests (l1–l16 with l6b, l7b, l7c), every `--desc` one of `test` ×6, `fold` ×4, `dry` ×3, `test fixture` ×2, `echo-test` ×2, `fail-test`, none carrying a lens or walk token | `grep -nF '# Step 4' -A8 scripts/lens_commit.py`; `grep -oE '"--desc", "[^"]*"' tests/test_lens_commit.py \| sort \| uniq -c` |
| P4 | the doctrine and the record | DRAFTING_CYCLE:196 — *a per-lens commit carries `walk <N>` and `lens <M>` in its subject (either casing, anywhere in the line) and names EXACTLY ONE lens*; STANDING_CONSTRAINTS line 1; the four registers of 2026-09-10 after the incident each carry the sentence "no lens or walk number in any `--desc`" — a rule met by memory four times | `grep -cF 'no lens or walk number' governance/knowledge/research/walk-register-*-2026-09-10.md` |
| P5 | the mutation contract; class; in-flight | `tools/mutation_check.py`: manifest-driven, KILLED = exit 1 only, sandbox = `git archive HEAD`; run file `knowledge/mutants/<slug>.run.txt` ending `MUTATION: N killed, 0 survived, 0 error`; this plan writes `scripts/` and `tests/` → **shop-infra** (HOLDS, the CEO releases); in flight: none (daemon pid 70398, HEAD `ba74706`) | `python3 status.py` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-lens-commit-desc-guard-2026-09-10.md
**Walks:** walk 0 pinned (P1–P5 measured on bellows `ba74706`; clone-diff against `Done/executable-100065.md` (kind) and the closed 266 draft (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py` (folding lenses too, since #100065); the tool run bare, its exit read; no lens or walk number in any `--desc`.

- Weak spots:          w1 2 folded — record 2 (three greps to -F; the register's Draft: line the coverage lint resolves by); w2 dry

- Destruction:           w1 dry; w2 dry

- Vulnerabilities:     w1 1 folded — record 1 (the pass/refuse examples checked letter by letter against the regexes); w2 dry

- Integration-record:    w1 dry; w2 dry

- ACID:                  w1 dry; w2 dry

**Closing:** WARM close after walk 2 — BAR MET (T1), thread 271's plan. Two walks: the walk-1 folds → 0 (walk 2 fully dry). Every lens commit through `lens_commit.py` (folding lenses under the CONTINUE it now accepts — #100065; dry lenses under `--dry`), the tool run bare, its exit read, the observer after each walk; no lens or walk number in any `--desc`. `walks:` set by hand for the last time (thread 269 is this pair). Deposit via `ready-`; HOLDS on class shop-infra, released on the CEO's behalf under the 2026-09-10 delegation.

## Cycle Manifest
tier: T1
target: scripts/lens_commit.py
class: shop-infra
reads: scripts/lens_commit.py, scripts/lens_order_check.py, tests/test_lens_commit.py, tools/mutation_check.py, knowledge/decisions/Done/executable-100065.md, DRAFTING_CYCLE.md, STANDING_CONSTRAINTS.md
writes: scripts/lens_commit.py, tests/test_lens_commit.py, knowledge/mutants/lens-commit-desc-guard.json, knowledge/mutants/lens-commit-desc-guard.run.txt, knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md, knowledge/qa/evidence/lens-commit-desc-guard-qa-receipt-2026-09-10.md, knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt
mutants: knowledge/mutants/lens-commit-desc-guard.json
open_forks: 1. a `plan_lint` or `walk_register_lint` arm that reads the register's hand-commit subjects for the same tokens (hand commits stay unguarded) — after one measured hand-commit instance; 2. the guard applied to `close_cycle.py`'s closing text (a close subject carries `walk N` by design and no lens — not a lens row; nothing to guard today)
walks: 2
yields: N/A
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:6
coherence: 2/2 body walks named in the register (3 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-lens-commit-desc-guard.md.foldcheck.json

---

## STEP 1 — DEV (one guard, three tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; never import `lifecycle`. ⛔ Every deposit is written in THIS worktree (`"$(git rev-parse --show-toplevel)"`), never in the canonical checkout; the plan's own lane file lives in the canonical checkout at `/Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md` (`<id>` from the prompt).
>
> **Scope:**
> - `scripts/lens_commit.py`
> - `tests/test_lens_commit.py`
> - `knowledge/mutants/lens-commit-desc-guard.json`
> - `knowledge/mutants/lens-commit-desc-guard.run.txt`
> - `knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md`
>
> **Item 1 — re-derive P2 and P3 and HALT on a mechanism mismatch** (P1, P4, P5 are records; a line-number drift is not a mismatch, a changed regex or a `desc` already inspected is). Paste both regex lines, step 4, and the `--desc` census under the first declared heading. Then reproduce P1's class on the fixture: `--desc "QA lens 2"` through the shipped tool commits (`commit OK`), and `lens_order_check.py plan.md --repo <fixture>` on that repo reads `BATCHED` — paste both lines.
> **Item 2 — write the failing tests FIRST:** *What this changes* 2 — l17, l18, l19. Run the file: l17 and l18 red (rc 0 and a commit where a refusal was expected), l19 GREEN before the edit (it pins what must stay admitted — say so); l1–l16 green. Paste under the second declared heading.
> **Item 3 — the edit** as *What this changes* 1; then the file green (22 tests), then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher` skips in a worktree; a skip is not a failure).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md knowledge/mutants/lens-commit-desc-guard.run.txt && git add scripts/lens_commit.py tests/test_lens_commit.py knowledge/mutants/lens-commit-desc-guard.json && git commit -F <msg-file> -- scripts/lens_commit.py tests/test_lens_commit.py knowledge/mutants/lens-commit-desc-guard.json` — three files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 271`; the paste MUST contain `PRECHECK: 0 failure(s) — … (expecting 2 missing)` — the first plan whose first commit passes the pre-check as shipped.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/lens-commit-desc-guard.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/lens-commit-desc-guard.json > knowledge/mutants/lens-commit-desc-guard.run.txt 2>&1`; the last line must read `MUTATION: <n> killed, 0 survived, 0 error` with n ≥ 3 — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md` under the four headings declared below; `## Pins re-derived (P2, P3)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the VALUE cell (third column) ends with the words `keeps a row when BOTH match`; paste through those words, then stop. **Second commit**, gated on the FULL suite AND the run file AND the pre-check run BARE, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && grep -Eq 'MUTATION: ([3-9]|[1-9][0-9]+) killed, 0 survived, 0 error' knowledge/mutants/lens-commit-desc-guard.run.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/mutants/lens-commit-desc-guard.run.txt knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md && git commit -F <msg-file> -- knowledge/mutants/lens-commit-desc-guard.run.txt knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md` — two files.
> **Headings:** `## Pins re-derived (P2, P3)`; `## Failing-first (two red, one pinned, then green)`; `## The class reproduced on the fixture (Item 1)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P2, P3)` ← P2
>
> **Deposits:**
> - `scripts/lens_commit.py`
> - `tests/test_lens_commit.py`
> - `knowledge/mutants/lens-commit-desc-guard.json`
> - `knowledge/mutants/lens-commit-desc-guard.run.txt`
> - `knowledge/development/dev-log-lens-commit-desc-guard-2026-09-10.md`
>
> **Post-conditions:** three new tests green and the nineteen prior green; `--desc "QA lens 2"` refuses with the `assert FAIL` line and no commit; a prose description without a token commits; the first commit's pre-check line reads `0 failure(s)` with `(expecting 2 missing)`; the mutation run's last line `n ≥ 3 killed, 0 survived, 0 error`; `git diff --stat main...HEAD` (three-dot) names exactly the five Scope files; the four declared headings present with P2's cell whole; `lens_order_check.py` unchanged.

## STEP 2 — QA (full suite + the guard on the real incident's description)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files. ⛔ No plan-shaped file under any real `knowledge/decisions/`; scratch under `$T` only.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the incident's own description:** in a scratch fixture repo under `$T` (the `_make_lens_fixture` shape), run the tool with `--dry` and the EXACT description of governance `5768483` as rewritten's original: `--desc "CAPSTONE folded — five (C1 l9 seed; C2 root-relative HEAD path; C3 o4c; C4 refusal order, slug guard, QA lens 2; C5 l11 + three mutants)"` → the `assert FAIL — --desc must not name a lens or walk number` line, rc 1, `git rev-list --count HEAD` unchanged; then the CEO's rewritten form (`… QA cases on the second lens; …`) → `commit OK`. Paste both.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no lifecycle import.
> **Item 4 — receipt** `knowledge/qa/evidence/lens-commit-desc-guard-qa-receipt-2026-09-10.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: lens-commit-desc-guard-2026-09-10`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["lens-commit-desc-guard-suite-2026-09-10.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/lens-commit-desc-guard-qa-receipt-2026-09-10.md knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt && git commit -F <msg-file> -- knowledge/qa/evidence/lens-commit-desc-guard-qa-receipt-2026-09-10.md knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt`. ⛔ A QA step that finds it must change production code STOPS and requests a verdict (thread 262) rather than committing the change.
>
> **Deposits:**
> - `knowledge/qa/evidence/lens-commit-desc-guard-qa-receipt-2026-09-10.md`
> - `knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/lens-commit-desc-guard-qa-receipt-2026-09-10.md`
> - `knowledge/qa/evidence/lens-commit-desc-guard-suite-2026-09-10.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 2's two runs pasted (the incident's description refused; the rewritten one committed); the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
