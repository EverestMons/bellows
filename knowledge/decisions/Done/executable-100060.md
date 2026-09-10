# bellows — DEV-SIDE PRE-CHECK: run the deposit-reading gates over the worktree BEFORE the DEV commit (the same five functions the pause runs, fed the plan's own Deposits block), plus a grep-based dependents WARN — a declared-heading, verbatim-cell, missing-deposit or phantom-node defect is refused at the desk, not at the pause (thread 253)

**Date:** 2026-09-09 | **Project:** bellows | **Tier:** Small (one tool, one test sibling, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — the tool imports `gates` by name; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_qa_step | **Discharges:** thread 253

**auto_close:** false

**Post-close:** no restart (a tool, imported by no daemon path). One doctrine rider, the CEO's act, PLANNER_TEMPLATE v4.105 → v4.106: the dev-log declaration paragraph (P4) gains one sentence — *the DEV's commit command chains `tools/check_deposit.py <plan> <step>` before `git add`, the way the full suite is chained* — and the Item-N commit line in the plan template carries the chain by default. The gate at the pause stays: the daemon's check is the one that counts; this moves the refusal earlier.

**Depends on:** the CEO's ruling of 2026-09-09 (session d04ebd33): evidence before implementation — this draft is cycled and PARKED at its close, deposited only after `diagnostic-bellows-anvil-reprice` (thread 255) rules whether the dependents source is the grep below or an anvil query; the WARN is written so the source swaps without the gate list moving. Clone origin by kind: `Done/executable-100052.md` (gates work: helpers, failing-first sibling, mutation run, two commits); by layout: `Done/executable-100055.md`.

**Tier computed (§1):** **T1** — T-1 fires (a new tool under `tools/` plus its test sibling and manifest: two subsystems, tools and tests); T-6 does NOT fire in the plan (the PT rider is the CEO's post-close act, the v4.105 shape — no gate, doctrine or template text changes inside the step); T-2 does not.

## CEO Context

The `dev_log_declared_text` gate shipped on the morning of 2026-09-09 and caught two record defects at the verdict PAUSE the same day: plan 100054 (five generic headings, no verbatim cell; halted on the CEO's ruling, a record-only follow-up 100055) and plan 100056 (one verbatim cell truncated by its last clause; overridden). Each catch arrived after a 15–80 minute DEV step, its suite runs, merge and teardown, and cost a halt or an override on top. The five gates that read a step's deposits are pure functions of (plan text, step number, worktree, declared deposit list); the DEV can call them over its own output in seconds before committing. Thread 253 (fork 1 of 100055) names the design; the 2026-09-09 lesson names the class: a check only the consumer runs is read after the producer's whole cost is spent. The second product, a dependents WARN, rests on P5: at the two cause commits of the known consumer-miss (`751ab87`), a plain word-grep of the changed names over the repo named the two production files the later fix touched. Whether anvil's graph adds anything over that grep is thread 255's question; this plan does not wait for it to refuse the four record classes.

## What this changes

1. **`tools/check_deposit.py <plan-path> <step> [--wt <path>] [--base <ref>] [--dependents]`** — read-only over the repo. Resolves the worktree (`--wt`, default `git rev-parse --show-toplevel`), reads the plan, extracts the step's declared deposits with `gates._extract_plan_required_deposits(gates._extract_step_text(plan_text, step))`, and SYNTHESISES the receipt the pause would have: `parsed = {"result_text": "### Files Deposited\n" + "".join(f"- `{p}`\n" for p in deposits)}` — the exact section `gates._extract_agent_declared_deposits` parses (P2). Then calls, in `check()`'s order and with `check()`'s arguments, `_gate_rule_22_verification`, `_gate_quoted_test_nodes_exist`, `_gate_mutation_result`, `_gate_qa_nodes_match_suite`, `_gate_dev_log_declared_text` (is_qa_step from `_gate_is_qa_step`), collecting `failures`. Prints one line per failure `FAIL <gate>: <evidence>` and a last line `PRECHECK: <n> failure(s) — <plan basename> step <k>`; exit 1 on any failure, else 0. ⛔ The functions are imported from `gates` by name and called — never re-implemented, never widened, never narrowed (the one-parser law; `GATES` is a module-level tuple of the five function objects, asserted by a test).
2. **`--dependents` (WARN, never a failure):** for every `.py` file in `git diff --name-only <base>..HEAD` plus the working tree (`<base>` = `--base`, default `main`), the top-level names whose definitions intersect the changed hunks (post-image AST ∩ `-U0` hunk ranges: functions, classes, and UPPER_CASE module assignments — the `STANDARD_GATES` class); for each name, `git grep -wl -- '*.py'` over the worktree; files NOT in the diff are printed as `WARN dependents: <name> → <f1>, <f2>, …` (at most 10 files per name; a name with more than 25 referencing files prints `WARN dependents: <name> → (generic, <N> files)` and no list). Exit code unaffected by WARN lines. Source-swappable: the name→files function is one module-level callable `find_referencing_files(names, wt_path)`; an anvil-backed implementation replaces that callable and nothing else.
3. **`tests/test_check_deposit.py`** — plans as strings, a worktree under `tmp_path` (with `git init` for the dependents case), the tool driven in-process via its `main(argv)`; every arm reproduced as a failing-first test (STEP 1 Item 2).
4. **`knowledge/mutants/check-deposit.json`** — the manifest for `tools/mutation_check.py` (P7): at least six hand-named mutants, each with an `expect_fail` node id from the sibling.
5. **Not changed:** `gates.py`, `bellows.py`, `scripts/plan_lint.py`, every existing test — this plan's diff touches five new files and nothing else (`git diff --stat <base>..` shows exactly the five Scope files, the run file included).

## Why this exists

A gate that only the pause runs is read after the run's whole cost is spent (LESSONS 2026-09-09). Two catches in one day by one gate is the signal that its function belongs in the producer's loop. The instructions the DEV reads (`**Headings:**`, `**Verbatim:**`) are not a check; a check reads both sides, and the DEV can run that check itself.

## What this does NOT do

- Does not change any gate, any threshold, or the pause. The daemon's check remains the one that counts.
- Does not make the dependents WARN a failure, and does not decide its source (thread 255).
- Does not edit PLANNER_TEMPLATE or the plan template inside the step (the rider is the CEO's post-close act).
- Does not run the daemon, `run_plan`, a claim, or import `lifecycle`.

## MUST-PRESERVE

- ⛔ **One parser.** The five gate functions are imported from `gates` and called with `check()`'s argument shapes; the receipt is synthesised from the plan's Deposits block by the gate module's own extractor pair, so a plan whose deposits the pause would read is the plan the desk reads.
- ⛔ **WARN is not FAIL.** The dependents lines never set the exit code; a test pins it.
- ⛔ **Suite green at both commits;** the commit lines chain the FULL suite; nothing outside the five Scope files moves.

## Numbers discipline — measured 2026-09-09 by the Planner (bellows `1365acc`, governance `b5f94ab7`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the two catches | `verdicts/resolved/processed-verdict-100054-step-1.md` line 3: `CEO ruling 2026-09-09: STOP — halt. The DEV's code half landed and is on origin (615d2cc → f5c82a4, 6b4bfb5 …)`; `verdicts/resolved/override-100056-step-1-dev_log_declared_text.md`: `**Failure:** \`cell absent from section '## Pins re-derived (P1–P4)'\``; LESSONS 2026-09-09 (the record half of a DEV step): six `dev_log_declared_text` failures on 100054 | `git show`; the files are committed |
| P2 | ⛔ the gate surface, verbatim | `check()` (`gates.py:270`) calls, in order, `_gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)`, `_gate_quoted_test_nodes_exist(is_qa_step, …)`, `_gate_mutation_result(plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)`, `_gate_qa_nodes_match_suite(is_qa_step, …)`, `_gate_dev_log_declared_text(plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)`; the four deposit gates read `_extract_agent_declared_deposits(parsed)`, which parses `parsed["result_text"]` for `### Files Deposited` and `- \`path\`` lines (`gates.py:504–526`); rule 22 (a) reads `_extract_plan_required_deposits(step_text)` (`gates.py:807`) | `sed -n 270,332p gates.py`; `sed -n 504,526p` |
| P3 | ⛔ the commit-line shape the rider extends | `Done/executable-100052.md` Item 8: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && git add <files> && git commit -F <msg-file> -- <files>` — the suite chained on `&&` before `git add`; the pre-check chains the same way, between the suite and `git add` | `sed -n 154p` of the Done file |
| P4 | ⛔ the doctrine sentence the rider follows | PLANNER_TEMPLATE v4.105 line 711 (the declaration-lines paragraph): `The gate runs at every step's pause; a step that declares nothing pays nothing.` — the rider's sentence goes immediately after it | `grep -n "a step that declares nothing pays nothing" PLANNER_TEMPLATE.md` |
| P5 | ⛔ grep recall on the known miss | at `601f5b9` (cause of 751ab87, thread 210) the changed name `record_gate_events` → `git grep -wl` names `bellows.py`, `tests/test_gate_transaction_mechanization.py`, `tools/passfail_record_census.py`; at `34eeab2` (thread 104) `get_sha` and `render_daemon_header` → `dashboard.py`; `751ab87` touched `dashboard.py`, `tests/test_dashboard.py`, `tests/test_gate_transaction_mechanization.py` — 2 of its 3 files named, both the production-side consumers; noise: `main` at `34eeab2` → 43 files (hence the generic cap) | the Planner's script: post-image AST ∩ `-U0` hunks at the sha, then `git grep -wl <name> <sha> -- '*.py'` minus the commit's own files |
| P6 | the tool and test conventions | `tools/replay_scope_check.py` header: `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` then `import gates`; docstring `Read-only: opens the db with mode=ro, writes nothing.`; gate tests live as `tests/test_gates_*.py`; `tests/conftest.py` autouse fixtures `isolate_verdicts_dir`, `isolate_runner_logs_dir`, `isolate_lifecycle_db`, `_clear_notifier_dedupe` | `sed -n 1,30p tools/replay_scope_check.py`; `ls tests`; `grep -n fixture tests/conftest.py` |
| P7 | the mutation contract | `tools/mutation_check.py`: manifest-driven, `expect_fail` is a pytest NODE ID, `KILLED` = pytest exit 1 only, `SURVIVED` = exit 0, everything else `ERROR`; manifests under `knowledge/mutants/<slug>.json`, run files `<slug>.run.txt` carrying `MUTATION: N killed, 0 survived, 0 error` (100052 Item 11's grep) | `sed -n 1,22p tools/mutation_check.py`; `ls knowledge/mutants` |
| P8 | in-flight; class; the parking rule | at drafting: `diagnostic-bellows-anvil-reprice` HOLDS on class shop-infra, unclaimed; this plan writes `tools/`, `tests/`, `knowledge/mutants/`, `knowledge/development/` → class shop-infra (HOLDS, the CEO releases); ⛔ NOT deposited while the anvil diagnostic is in flight or verdict-pending on bellows, and not before its doc is read (Depends on) | `python3 status.py`; the depositor's parse at deposit |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-dev-side-precheck-2026-09-09.md
**Walks:** walk 0 pinned (P1–P8 measured on bellows `1365acc`; clone-diff against `Done/executable-100052.md` (kind) and `Done/executable-100055.md` (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit.

**Closing:** WARM close after walk 3 — thread 253's plan, a judged stop. Three walks: instruction 5 → 3 → 0 (walk 1 folded five, walk 2 three; eight findings plus f0). T1, no panel. ⛔ PARKED at this close by the CEO's 2026-09-09 ruling (evidence before implementation): not deposited until `diagnostic-bellows-anvil-reprice` (#100057) reaches Done and its doc is read; then deposit via `ready-`, HOLDS on class shop-infra, the CEO releases; the PT v4.106 rider is the CEO's act at the plan's close.
- Weak spots:          w1 3 folded — instruction 3 / record 0
- Destruction:         w1 dry
- Vulnerabilities:     w1 2 folded — instruction 2 / record 0
- Integration-record:  w1 dry
- ACID:                w1 dry
- Weak spots:          w2 2 folded — instruction 2 / record 0
- Destruction:         w2 dry
- Vulnerabilities:     w2 dry
- Integration-record:  w2 1 folded — instruction 1 / record 0
- ACID:                w2 dry
- Weak spots:          w3 dry
- Destruction:         w3 dry
- Vulnerabilities:     w3 dry
- Integration-record:  w3 dry
- ACID:                w3 dry
**Walk 3 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the WARM close meets the bar (§2) — a judged stop (8 findings over two warm walks: instruction 8 / record 0 plus f0; yield 5 → 3 → 0). T1: no panel owed. PARKED at the close, not deposited (Depends on).**
**Walk 2 — three folds across two lenses (instruction 3 / record 0), three lenses dry; one commit per lens. Instruction non-zero: walk 3 owed.**
**Walk 1 — five folds across two lenses (instruction 5 / record 0), three lenses dry; one commit per lens.**

## Cycle Manifest
tier: T1
target: tools/check_deposit.py
class: shop-infra
reads: gates.py, tools/replay_scope_check.py, tools/mutation_check.py, tests/conftest.py, tests/test_gates_evidence_correspondence.py, knowledge/decisions/Done/executable-100052.md, knowledge/decisions/Done/executable-100055.md, knowledge/decisions/halted-executable-100054.md, verdicts/resolved/processed-verdict-100054-step-1.md, verdicts/resolved/override-100056-step-1-dev_log_declared_text.md, PLANNER_TEMPLATE.md
writes: tools/check_deposit.py, tests/test_check_deposit.py, knowledge/mutants/check-deposit.json, knowledge/mutants/check-deposit.run.txt, knowledge/development/dev-log-dev-side-precheck-2026-09-09.md, knowledge/qa/evidence/dev-side-precheck-qa-evidence-2026-09-09.md, knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt
open_forks: 1. the dependents source — the grep callable replaced by an anvil query if thread 255's doc shows the graph beats P5's recall or precision; 2. the WARN promoted to a gate arm (`dependents_untouched`) only after a measured false-positive rate over ten real DEV commits; 3. the PT rider (v4.106) and the plan template's Item-N line — the CEO's act at close, not a step
walks: 3
yields: 5, 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:19
coherence: 3/3 body walks named in the register (9 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-dev-side-precheck.md.foldcheck.json

---

## STEP 1 — DEV (one tool, one test sibling, one manifest; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; never import `lifecycle`; the tool opens nothing for writing.
>
> **Scope:**
> - `tools/check_deposit.py`
> - `tests/test_check_deposit.py`
> - `knowledge/mutants/check-deposit.json`
> - `knowledge/mutants/check-deposit.run.txt`
> - `knowledge/development/dev-log-dev-side-precheck-2026-09-09.md`
>
> **Item 1 — re-derive P2 and P5 and HALT on a mechanism mismatch** (P1, P3, P4, P6, P7 are records; a line-number drift of one is not a mismatch, a changed signature or a changed `### Files Deposited` regex is). Paste `check()`'s five calls and the extractor's regex line into the dev-log under the first declared heading, followed by P5's two grep results re-run at the two shas.
> **Item 2 — write the failing tests FIRST**, `tests/test_check_deposit.py`, driving `check_deposit.main(argv)` in-process (capture stdout, return code): (t1) a DEV plan whose Deposits name a dev-log with `**Headings:** \`## A\`; \`## B\`` and a worktree dev-log carrying only `## A` → return 1, stdout has `FAIL dev_log_declared_text` and `PRECHECK: 1 failure(s)`; (t2) the same with `## B` present → return 0, `PRECHECK: 0 failure(s)`; (t3) a Deposits path absent from the worktree → `FAIL rule_22_verification`; (t4) a deposit quoting `tests/test_x.py::test_gone` that does not exist → `FAIL quoted_test_nodes_exist`; (t5) a Deposits `.run.txt` with `1 survived` → `FAIL mutation_result`; (t6) `GATES` is exactly `(gates._gate_rule_22_verification, gates._gate_quoted_test_nodes_exist, gates._gate_mutation_result, gates._gate_qa_nodes_match_suite, gates._gate_dev_log_declared_text)` — identity, not names; (t7) the synthesised `parsed["result_text"]` for a plan with deposits `a.md` and `b.txt` round-trips through `gates._extract_agent_declared_deposits` to `["a.md", "b.txt"]`; (t8) dependents on a `git init` repo under `tmp_path` with `mod.py` defining `helper` and `use.py` calling it, a commit, then a working-tree edit to `helper` → `--dependents` prints `WARN dependents: helper → use.py` and the return code is 0 even so; (t9) a name referenced from more than 25 files prints the `(generic, N files)` form; (t10) `find_referencing_files` is a module-level callable and replacing it (monkeypatch) changes the WARN lines and nothing else. Run: all ten red for the right reason (`ModuleNotFoundError` or `AttributeError`, quoted), pasted under the second declared heading.
> **Item 3 — the tool** as *What this changes* 1–2, then the ten tests green; the FULL suite green.
> **Item 4 — first commit**, gated in one command on the FULL suite's exit code and path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && git add tools/check_deposit.py tests/test_check_deposit.py && git commit -F <msg-file> -- tools/check_deposit.py tests/test_check_deposit.py` — two files; the message tagged with the plan id and `thread 253`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/check-deposit.run.txt` (a Deposit):** the manifest `knowledge/mutants/check-deposit.json` with at least six mutants — exit code inverted (expect t1), the `### Files Deposited` header string changed (t7), a WARN line setting the exit code (t8), the generic cap removed (t9), one gate dropped from `GATES` (t6), the failure count printed as a constant (t2) — each `expect_fail` a node id from the sibling; `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/check-deposit.json > knowledge/mutants/check-deposit.run.txt 2>&1`; the last line must read `MUTATION: <n> killed, 0 survived, 0 error` with n ≥ 6 — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log FIRST, then the self-application:** write `knowledge/development/dev-log-dev-side-precheck-2026-09-09.md` under the four headings declared below (the fourth heading's section is the run file's last line), THEN run `/Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --dependents` — the plan's lane file lives in the CANONICAL checkout (the worktree carries no lane file; `<id>` is this plan's id from the prompt) — and paste its full output under the third declared heading (the paste adds no `#`-led line, so the sections the gate reads are unchanged); `PRECHECK: 0 failure(s)` is the condition for Item 7 (a failure here is the tool doing its job: fix the deposit, re-run, paste both).
> **Item 7 — second commit** (the dev-log written at Item 6 carries `## Pins re-derived (P2, P5)` opening with P5's value cell pasted verbatim, whole, to its last character; the `dev_log_declared_text` gate reads it at the pause, Item 6 read it at the desk), gated on the FULL suite AND the run file AND the pre-check, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && grep -Eq 'MUTATION: ([6-9]|[1-9][0-9]+) killed, 0 survived, 0 error' knowledge/mutants/check-deposit.run.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/mutants/check-deposit.json knowledge/mutants/check-deposit.run.txt knowledge/development/dev-log-dev-side-precheck-2026-09-09.md && git commit -F <msg-file> -- knowledge/mutants/check-deposit.json knowledge/mutants/check-deposit.run.txt knowledge/development/dev-log-dev-side-precheck-2026-09-09.md`.
> **Headings:** `## Pins re-derived (P2, P5)`; `## Failing-first (ten red, then green)`; `## Self-application (the tool over this step's own deposits)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P2, P5)` ← P5
>
> **Deposits:**
> - `tools/check_deposit.py`
> - `tests/test_check_deposit.py`
> - `knowledge/mutants/check-deposit.json`
> - `knowledge/mutants/check-deposit.run.txt`
> - `knowledge/development/dev-log-dev-side-precheck-2026-09-09.md`
>
> **Post-conditions:** ten tests in the sibling, all green; `GATES` identity-equal to the five gate functions; the mutation run file's last line `MUTATION: n killed, 0 survived, 0 error` with n ≥ 6; the self-application output pasted with `PRECHECK: 0 failure(s)`; `git diff --stat main..HEAD` names exactly the five Scope files; the four declared headings present as full lines; no gate, threshold, daemon path or existing test changed.

## STEP 2 — QA (full suite + the tool shown on the two real catches and the real miss)

> ⛔ Root re-established as in STEP 1; interpreter ABSOLUTE; read-only beyond the two evidence files.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt 2>&1`; the summary line quoted in the receipt.
> **Item 2 — the 100054 catch reproduced at the desk:** a scratch dir under `tmp_path`-style `mktemp -d` holding the halted plan text (`knowledge/decisions/halted-executable-100054.md`) and the 100054 DEV's dev-log as committed — its path and commit from `git log --diff-filter=A --name-only --format=%h 615d2cc~1..6b4bfb5 -- knowledge/development/` (the three DEV commits P1 names), then `git show <that sha>:<that path>`; run `tools/check_deposit.py <scratch plan> 1 --wt <scratch dir>`; expected: `FAIL dev_log_declared_text` lines and `PRECHECK: 6 failure(s)` (P1); paste the output. A different count is reported as measured, with the reason.
> **Item 3 — the 100056 catch reproduced:** the same with `Done/diagnostic-100056.md` and `git show 53e7146:knowledge/development/dev-log-drafting-battery-reprice-2026-09-09.md`; expected one `FAIL dev_log_declared_text: cell absent from section '## Pins re-derived (P1–P4)'` and `PRECHECK: 1 failure(s)`.
> **Item 4 — the real miss, from the desk:** in a scratch clone of the repo checked out at `601f5b9`, run `tools/check_deposit.py <this plan's canonical lane path> 1 --wt <clone> --base 601f5b9~1 --dependents` — the five gates will FAIL on the clone (this plan's deposits are not in it) and the exit code will be 1: expected, irrelevant here, only the WARN lines are read; expected a WARN naming `tests/test_gate_transaction_mechanization.py` for `record_gate_events` (P5); paste the WARN lines and the count of WARN lines for `main`-class generic names.
> **Item 5 — the tool over THIS plan's STEP 1 deposits in the worktree:** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)"` → `PRECHECK: 0 failure(s)`; paste.
> **Item 6 — production writes, stated exactly:** none outside the two evidence files; no lane file, no lifecycle row, no lifecycle import; every scratch dir removed (`[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`).
> **Item 7 — receipt** `knowledge/qa/evidence/dev-side-precheck-qa-evidence-2026-09-09.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); opens with the whole-line banner `Rule 20 — QA Self-Check Results`, carries a `## Verification` table with one row per Item 1–6, each quoting the line it rests on, and closes with the whole line `PASSED — SELF-CHECK PASSED` only when every row passes (a failing row makes the closing line `FAILED — SELF-CHECK FAILED` and the step pauses on it); the quoted node ids limited to the sibling's methods.
> **Item 8 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt && git add knowledge/qa/evidence/dev-side-precheck-qa-evidence-2026-09-09.md knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt && git commit -F <msg-file> -- knowledge/qa/evidence/dev-side-precheck-qa-evidence-2026-09-09.md knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt`.
>
> **Deposits:**
> - `knowledge/qa/evidence/dev-side-precheck-qa-evidence-2026-09-09.md`
> - `knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/dev-side-precheck-qa-evidence-2026-09-09.md`
> - `knowledge/qa/evidence/dev-side-precheck-suite-2026-09-09.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed` with N ≥ the DEV's count; Items 2–4 reproduce the two catches and the miss with their counts stated as measured; the receipt's `## Verification` table has six rows; one QA commit carrying the two evidence files.
