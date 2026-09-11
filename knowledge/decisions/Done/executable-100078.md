# bellows — AN EXECUTABLE WITH NO STEP HEADINGS FAILS THE LINT: `plan_lint`'s `(e)` gains the arm thread 13 measured — an `executable-*` plan parsing zero uppercase `## STEP N` headings FAILS regardless of `qa_steps` (today the check fires only when `qa_steps` is declared, so such a plan lints clean and every per-step check passes vacuously); a diagnostic keeps its zero-heading tolerance, which the daemon shares (thread 13's residue 1; thread 13's other items measured against today's doctrine and left for a ruling)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one lint arm, three tests, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — `plan_lint` is imported by the depositor's and the loop tools' tests; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 13 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** no restart (the lint is a script the depositor and the loop tools spawn; a running daemon spawns the new file at the next deposit — MACHINE_SETUP §4 item 4's exception for subprocess tools does not apply to `depositor.py` itself, which is unchanged); no doctrine. Thread 13's four other items are NOT built here — measured 2026-09-11 against today's doctrine (P5): the `.txt` deposit check shipped as `(u)` (thread 77); the fold-claim residue is covered by `lens_commit.py`'s vacuity refusal (#100063); a WARN on a full-suite command inside a DEV step now contradicts PT v4.107 (every DEV commit is gated on the full suite); a blast-radius WARN on a step executing a file in its own Scope would fire on every QA that reads the tool it ships (#100074, #100075); the cold-scout tier line and "expectations from the deposit path" have no measured instance since August. Their disposition is the CEO's: `threads done 13` against this plan's merge with the four named as retired, or a new thread for any the CEO keeps.

**Depends on:** thread 13 (2026-08-26; the (e) extension "fixture-measured both ways": an executable with `### Step` headers and no `qa_steps` lints CLEAN at exit 0). Clone origin: `Done/executable-100064.md` (thread 265: a new plan_lint arm with its own letter, tested by fixture files under `tmp_path`, 2026-09-10).

**Tier computed (§1):** **T1** — T-1 fires (a lint every deposit runs); T-6 does not; T-2 does not.

## CEO Context

The daemon's step machinery reads `## STEP N` headings; a plan without them has no steps for the gates to scope, no Deposits to check, no QA to detect — every per-step check passes because there is nothing to check. `plan_lint`'s `(e)` was written to catch the title-case variant of that hole, but it keys on the header's `qa_steps`: declare none, write no headings, and the lint exits 0. A diagnostic is allowed that shape by design — the daemon sets its step count to one when it finds none (P3) — so the arm is drawn at the plan's KIND: an `executable-*` plan with zero headings is a plan that cannot run as written, and the lint says so before the depositor does.

## What this changes

1. **`scripts/plan_lint.py`** — beside `(e)` (`:418–427`): when `step_headers` is empty AND the plan is an executable — its basename, after the optional lifecycle prefixes (`ready-`, `hold-`, `in-progress-`, `verdict-pending-`, `halted-`, `parallel-N-`), starts with `executable-`, OR the header's `**Type:**` field (the pre-2026-06 form, `Done/executable-443.md`) reads `Executable` — NOT the `Execution:` field, which diagnostics carry too (`Step 1 (DIAGNOSTIC)`) — append `("FAIL", "(e) step heading format", "executable plan parses zero uppercase '## STEP N' headings — no step can be scoped, deposited or gated; the daemon runs nothing as written")` and set `all_passed = False`; the `qa_steps` arm and the lowercase WARN stay as they are; a diagnostic with zero headings keeps its exit 0 (P3). The kind test is one helper `_is_executable(plan_path, header) -> bool`, so the basename and the header field are read in one place.
2. **`tests/test_plan_lint.py`** — beside the `(e-a)`–`(e-c)` tests (`:306–352`): (t1) `(e-d)` an `executable-x.md` fixture with `**Execution:** Step 1 (DEV) → Step 2 (QA)`, NO `qa_steps`, and `### Step 1` / `### Step 2` H3 headings → `(e)` FAIL, exit 1 (thread 13's measured shape); (t2) `(e-e)` the same fixture with uppercase `## STEP 1 — DEV` / `## STEP 2 — QA` → no `(e)` row, exit 0; (t3) `(e-f)` a `diagnostic-x.md` fixture with no headings and no `qa_steps` → no `(e)` row, exit 0 (the tolerance kept — the (e-c) case, restated against the new arm); (t4) `(e-g)` a `ready-executable-x.md` (the lifecycle prefix) with zero headings → `(e)` FAIL.
3. **`knowledge/mutants/lint-executable-needs-steps.json`** — three mutants: (m1) the arm keyed on `qa_steps` again (`and header.get("qa_steps")` restored) → t1; (m2) `_is_executable` reads the `Execution:` field (diagnostics FAIL too) → t3; (m3) the lifecycle-prefix strip removed → t4.
4. **Not changed:** the daemon's `extract_total_steps`, the depositor, every other lint letter.

## Why this exists

A lint that passes vacuously on the one shape that cannot run is the class the (e) check was born to close; thread 13 measured the gap and the daemon's own tolerance draws the line.

## What this does NOT do

- Change any other lint arm, or make a diagnostic's zero-heading shape a failure.
- Build thread 13's other four items (Post-close names each and its measured status).

## MUST-PRESERVE

- ⛔ **Diagnostics keep exit 0 with zero headings** (t3); the daemon's `extract_total_steps` tolerance is the precedent.
- ⛔ **The kind is read from the plan, not guessed:** the basename after the lifecycle prefixes, or the old form's `Type:` field — one helper; the `Execution:` field is never the kind (diagnostics carry it).
- ⛔ **The existing (e) tests run unchanged** beside the new ones.
- ⛔ **Every `expect_fail` is a class-qualified node id where the test is a method**; the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop** (PT v4.108 §8).

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `2e3d600`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the (e) arm today | `scripts/plan_lint.py:416` `step_headers = re.findall(r'^(## STEP (\d+)\b[^\n]*)', clean_text, re.MULTILINE)` over `gates.strip_fenced_code_blocks(plan_text)`; `:419` the case-insensitive `ci_step_headers`; `:420` `if not step_headers and header.get("qa_steps"):` → `("FAIL", "(e) step heading format", …)` (`:421–425`); `:426–427` the lowercase WARN; `_M_STEP_RE` `:230` is the manifest reader's own step regex | `sed -n 414,428p scripts/plan_lint.py` |
| P2 | ⛔ the tests | `tests/test_plan_lint.py`: `(e-a)` `:306` (title-case headings with `qa_steps: 2` → FAIL), `(e-b)` `:335` (uppercase → no row), `(e-c)` `:341` (single-step diagnostic, no `qa_steps`, no headings → no row, exit 0); the fixtures are written under `tmp_path` and the lint run on the path | the file |
| P3 | ⛔ the daemon's tolerance | `bellows.py`: in `_consume_verdicts`, `if total_steps_c == 0 and is_diag: total_steps_c = 1` (`:3319–3320`) — a diagnostic with no headings is one step; an executable with none has zero and runs nothing | `grep -nF 'total_steps_c == 0 and is_diag' bellows.py` |
| P4 | ⛔ the measured gap (thread 13) | "an executable with H3 '### Step' headers and no qa_steps field lints CLEAN at exit 0 (fixture-measured both ways)"; PT `:445` "The `## STEP N — AGENT` header is ALL CAPS"; PT `:449` `qa_steps` is required only for plans WITH QA steps | thread 13's body; the template |
| P5 | ⛔ thread 13's other items, measured today | `(u)` `:553–554` WARNs on a QA step whose Deposits carry no `.txt` (thread 77 — item 1 shipped); `lens_commit.py:210` `(iv) vacuity check` refuses a fold whose diff carries no draft change (#100063 — residue 2 covered); no arm today for a full-suite command in a DEV step, a step executing its own Scope, a cold-scout line, or deposit-path expectations (`grep -n -i 'full.suite\|blast\|scout\|expectation' scripts/plan_lint.py` → none) — and PT v4.107's Rule 23 makes the first two the standard DEV and QA shapes | the greps; PT `:2301` |
| P6 | in-flight; class; interpreter | #100076 in flight and a T0 (thread 9) holding at drafting; writes: `scripts/plan_lint.py`, `tests/test_plan_lint.py`, the manifest, run file, dev-log, two QA evidence files → **shop-infra** (`_assign_class`, walk 0) — HOLDS at admission, the CEO releases; Python 3.9.6, the bellows venv | `python3 status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-lint-executable-needs-steps-2026-09-11.md
**Walks:** walk 0 pinned (P1–P6 measured on bellows `2e3d600`; clone-diff against `Done/executable-100064.md` run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`; `lens_order_check` after every walk.

- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 dry; w2 dry
- Integration-record:  w1 dry; w2 dry
- ACID:                w1 dry; w2 dry
**Closing:** WARM close after walk 2 — BAR MET (T1), thread 13's one surviving item. Two walks: 1 → 0 (walk 1 moved the kind test off the `Execution:` field, which diagnostics carry; walk 2 dry on every lens). Every lens commit through `lens_commit.py`, the tool run bare, its exit read; the close through `close_cycle.py`. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases. Thread 13's four other items are measured in P5 and left for the CEO's disposition.

## Cycle Manifest
tier: T1
target: scripts/plan_lint.py
class: shop-infra
reads: scripts/plan_lint.py, tests/test_plan_lint.py, bellows.py, knowledge/decisions/Done/executable-100064.md
writes: scripts/plan_lint.py, tests/test_plan_lint.py, knowledge/mutants/lint-executable-needs-steps.json, knowledge/mutants/lint-executable-needs-steps.run.txt, knowledge/development/dev-log-lint-executable-needs-steps-2026-09-11.md, knowledge/qa/evidence/lint-executable-needs-steps-qa-receipt-2026-09-11.md, knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt
mutants: knowledge/mutants/lint-executable-needs-steps.json
target_class: detector
state_space: plan KIND as the lint reads it {basename after a lifecycle prefix starts `executable-` / the old form's `**Type:** Executable` / neither — a diagnostic or a qa plan} × headings the lint finds {uppercase `## STEP N` (`:416`) / lowercase-or-H3 only (`:419`) / none} × `qa_steps` {declared / absent}; the cells the tests occupy: t1 (executable, H3 only, absent), t2 (executable, uppercase, absent), t3 (diagnostic, none, absent), t4 (`ready-` prefix, none, absent); the (e-a)–(e-c) tests keep the declared-`qa_steps` cells; the untested cells (executable by the `Type:` field alone; lowercase headings with `qa_steps` absent; a `qa-` plan) fall to the same arms and are named, not tested
open_forks: 1. thread 13's four other items — each measured (P5), their disposition the CEO's; 2. the depositor refusing an executable with zero headings at admission (today the lint's FAIL is benign only for letters c and d, so this FAIL holds a deposit — the intended effect)
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:1
coherence: 2/2 body walks named in the register (5 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-lint-executable-needs-steps.md.foldcheck.json

---

## STEP 1 — DEV (one lint arm, four tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; the lint is run only on `tmp_path` fixtures; `T=$(mktemp -d /tmp/lint-steps.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/mutants/lint-executable-needs-steps.json`
> - `knowledge/mutants/lint-executable-needs-steps.run.txt`
> - `knowledge/development/dev-log-lint-executable-needs-steps-2026-09-11.md`
>
> **Item 1 — re-derive P1, P2 and P3 and HALT on a mechanism mismatch** (a line-number drift is not a mismatch; an `(e)` arm that already fires without `qa_steps`, or a daemon tolerance that has moved, IS one). Paste each pin's re-derived line beside it.
> **Item 2 — write the failing tests FIRST:** t1–t4 as *What this changes* 2 (red: t1 and t4 exit 0 with no `(e)` row). Run the file; paste the red summary line.
> **Item 3 — the edit** as *What this changes* 1; then the file green (the (e-a)–(e-c) tests and the four new), then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher`'s live-DB skip is the one).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-lint-executable-needs-steps-2026-09-11.md knowledge/mutants/lint-executable-needs-steps.run.txt && git add scripts/plan_lint.py tests/test_plan_lint.py knowledge/mutants/lint-executable-needs-steps.json && git commit -F <msg-file> -- scripts/plan_lint.py tests/test_plan_lint.py knowledge/mutants/lint-executable-needs-steps.json` — three files; the message tagged with the plan id and `thread 13`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/lint-executable-needs-steps.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/lint-executable-needs-steps.json > knowledge/mutants/lint-executable-needs-steps.run.txt 2>&1`; the last line must read `MUTATION: 3 killed, 0 survived, 0 error`.
> **Item 6 — the dev-log** `knowledge/development/dev-log-lint-executable-needs-steps-2026-09-11.md` under the three headings declared below; `## Pins re-derived (P1, P2, P3)` opens with P4's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `only for plans WITH QA steps`; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line and the green line; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare, path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P2, P3)`; `## Failing-first (red, then green)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2, P3)` ← P4
>
> **Deposits:**
> - `knowledge/mutants/lint-executable-needs-steps.json`
> - `knowledge/mutants/lint-executable-needs-steps.run.txt`
> - `knowledge/development/dev-log-lint-executable-needs-steps-2026-09-11.md`
>
> **Post-conditions:** t1–t4 green beside the existing (e) tests; the full suite `N passed, 1 skipped` with no `failed`; the mutation run's last line `MUTATION: 3 killed, 0 survived, 0 error`; two DEV commits; the dev-log's three headings present as full lines with P4's cell whole; `git status --porcelain` empty after the second commit.

## STEP 2 — QA (full suite; the lint run on this plan's own text and on a headless copy; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/lint-steps-qa.XXXXXX)`.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the arm read on this plan's own text:** `cp "$(git rev-parse --show-toplevel)/knowledge/decisions/in-progress-executable-<id>.md" "$T/executable-self.md"` and run the worktree's lint on it → no `(e)` row (this plan has two uppercase headings); then `sed 's/^## STEP /### Step /' "$T/executable-self.md" > "$T/executable-headless.md"` and run the lint on that → the `(e)` FAIL row with the new message, exit 1; paste both. A read of a scratch copy through the module under test, not a run of the daemon.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no daemon.
> **Item 4 — receipt** `knowledge/qa/evidence/lint-executable-needs-steps-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: lint-executable-needs-steps-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["lint-executable-needs-steps-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (PT v4.108 §8).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/lint-executable-needs-steps-qa-receipt-2026-09-11.md knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/lint-executable-needs-steps-qa-receipt-2026-09-11.md knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and pauses for a verdict (PT v4.108 §8).
>
> **Deposits:**
> - `knowledge/qa/evidence/lint-executable-needs-steps-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/lint-executable-needs-steps-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/lint-executable-needs-steps-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 2's two lint outputs pasted (clean on the plan's own text; the `(e)` FAIL on the headless copy); the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
