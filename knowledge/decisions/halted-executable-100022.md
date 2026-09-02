# bellows — executable: the checker defects the lessons named — cycle_check's vacuous CONTINUE, register-line crash, unresolved-register N/A and closure misread (threads 52, 58); plan_lint's hyphenated lens (63); the QA Deposits-order check (77) — with a tier-2 state-space suite

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full (the four checker test files targeted first, then the whole bellows suite — `1676 passed, 1 skipped` in a worktree today, growing by the new cases) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `checker-defects-2026-09-02`

**Depends on:** the CEO, 2026-09-02 ("Proceed as recommended" — apply the lessons to the systems: the measured checker defects first, thread 77 folded in); tuyere threads 52 (cycle_check C-1/C-2/C-3), 58 (CLOSURE_RE), 63 (plan_lint's two-word lens pattern), 77 (the QA Deposits order); diagnostic 100014 (Q-5: the TOOL-DEFECT class, 5 of 14 incidents, is what no daemon-run battery removes — the tools must be fixed); `Done/executable-473.md` (the clone origin and the newest same-class plan: a cycle_check regex fix with regression tests and a LIVE CANARY on the plan that exposed it, T1, 2026-08-19); PLANNER_TEMPLATE Rule 103 (lands tonight via plan C: every detector gets a tier-2 state-space suite — this plan's test design is that rule applied to the checkers). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-checker-defects-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-8 fires** (a corrective clone by kind of 473). T-1 no (one subsystem: `bellows/scripts` and its tests). T-6 — the precedent ruling, followed: 473 and 474 fixed `cycle_check` at T1 with no T-6 claim; the checkers are conformance instruments the depositor RE-RUNS, not the ten step gates in `gates.py`; the doctrine they enforce (`DRAFTING_CYCLE.md` §4) is untouched. T-2/T-3/T-5 no. → **T1: five-lens walk, no panel** (a scout at the Planner's call — not called: every defect is reproduced by a committed fixture below, and QA's canaries are the corpus).

## Why this exists — four defects, each measured today on this machine (pins below)

- **C-1 (thread 52) — a vacuous verdict.** A Cycle Log written as plain `- Walk N: X folds` lines with no parseable lens line yields `walk_data = {}`, and `cycle_check` returns `CONTINUE` from `if not walk_data:` — the SAME token a passing mid-cycle plan returns. Measured: fixture `plainonly` → `CONTINUE`. A thirteen-walk cycle once recorded that no-op as thirteen verdicts.
- **C-2 (thread 52) — an uncaught crash.** `WALK_REGISTER_RE` captures the rest of the line as the path; a `**Walk register:**` line carrying commentary after the path, staged in a git root whose first path component exists, makes `check_assert_2`'s `.exists()` raise `OSError: [Errno 63] File name too long` and takes the whole checker down. Measured: fixture `longref2` staged inside the bellows checkout → the traceback. (From scratch, where `scripts/` is not a directory, the same file reads `CONTINUE` — the crash depends on WHERE the plan sits.)
- **C-3 (thread 52) — N/A read as PASS.** A repo-relative register reference (`governance/knowledge/research/…`) resolves only from the governance root; staged in a project's `knowledge/decisions/`, the reference does not exist under that git root, `check_assert_2` returns `N/A`, and `N/A` counts as satisfied — so the BAR_MET that `clear_plan --release-class-hold` re-runs at release never checks the substrate. Measured: fixture `relref` → `('N/A', False, False)` from a bellows-staged copy, `BAR_MET`.
- **58 — the mandated heading read as a closure claim.** `CLOSURE_RE` matches the `**Closing:**` heading DRAFTING_CYCLE §3 requires on every record and the word `CLOSED` inside `NOT CLOSED`; a plan that honestly reports an unmet bar mid-cycle escalates as `claimed-close-unmet`. Measured: fixture `notclosed` → `ESCALATE:claimed-close-unmet`.
- **63 — the hyphenated lens.** `plan_lint`'s required-lens pattern `weak\s*spots` and `cycle_yields`' lens prefix `^weak\s*spots\s*:` both miss the compound spelling `Weak-spots`: the linter WARNs "missing lens" on a walked lens, and — worse — `parse_lens_line` returns `None` for the line, so the walk's weak-spots pass silently DROPS from the machine reading and the cycle can read BAR_MET on four lenses. Measured: fixture `hyphen` → `BAR_MET` with `parse_lens_line("- Weak-spots: w1 dry") → None`; `plan_lint` → `missing lens(es): Weak spots`.
- **77 — the Deposits order.** `rule_20_self_check` reads the FIRST `.md` in a QA step's Deposits block as the QA report; a cycle report listed first made the gate scan the wrong file and fail a correct run (W=28). The rule exists in the template and transfers only by mechanization: a lint check.

**The test design is Rule 103's: a tier-2 STATE-SPACE suite for `cycle_check`.** The dimensions are enumerated from the system, not from memory — the walk-line forms `cycle_check` parses (`WALK_SECTION_RE`, `WALK_STATUS_RE`, the lens-line prefixes, the plain `- Walk N:` form the corpus used) × the closing forms DRAFTING_CYCLE §3 mandates (none; the bare heading; `NOT CLOSED`; `BAR MET`; `met the bar`) × the register-reference forms (absent; absolute; repo-relative resolvable; repo-relative unresolvable; a line with trailing commentary; a component over 255 bytes). Every cell is force-classified to a verdict; a cell the table does not classify fails as uncovered.

## What this plan does

**F1 — `scripts/cycle_check.py`:**
- **(a) C-1:** in `run_check`, before `if not walk_data: return "CONTINUE"`, compute `has_walk_signal = bool(re.search(r"(?im)^\s*-\s*Walk\s+\d+\b|\*\*Walk\s+\d+\b|\bw\d+\s+(?:\d+\s+folded|dry)\b", block))`; if `has_walk_signal and not walk_data` → return `("ESCALATE:unparseable", 1)`. A block with no walk signal at all (a v0 carrying only the pin) still returns `CONTINUE`.
- **(b) C-2:** `walk_register_ref` extraction takes a backticked span if present, else the first whitespace-delimited token that ends in `.md` — never the rest of the line; and every filesystem probe in `check_assert_2` is wrapped `try: … except OSError: register_result = "FAIL"`.
- **(c) C-3:** resolution order for the reference — (1) absolute → `Path(ref).exists()`; (2) `git_root / ref`; (3) `resolve_governance_root() / ref` (from `bellows_root` at the bellows root — `cycle_check` must first `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`, the form `plan_lint.py:22` uses, then import inside `try/except ImportError` and treat an import failure as skipping step 3); the first that exists → `PASS`; none → `"UNRESOLVED"`. `N/A` remains only for a block with no reference line. `asserts_ok` accepts `PASS` and `N/A` only — `UNRESOLVED` and `FAIL` route to `ESCALATE:assert-fail:2`.
- **(d) 58:** `CLOSURE_RE` becomes a CLAIM matcher: after stripping negated spans (`\bNOT\s+(?:CLOSED|MET)\b`, `\bnot\s+met\b`, `\bunmet\b`) from the block, a claim is `\bBAR\s+MET\b|\bmet\s+the\s+bar\b|\bCYCLE\s+COMPLETE\b`; the bare `**Closing:**` heading is not a claim. (473 made the heading a token because the shipped dry form carries it; the judged-stop form carries `met the bar` — both claim forms are in the matcher.)

**F2 — `scripts/cycle_yields.py`:** `LENS_PREFIXES` weak-spots pattern → `^weak[\s-]*spots\s*:` (the other four already tolerate their spellings; assert it in the suite).

**F3 — `scripts/plan_lint.py`:** the required-lens pattern → `weak[\s-]*spots`; and a new WARN-only check **(u)** — for every QA step (the last `## STEP` when the header declares `qa_steps`, plus any step whose text carries `Rule 20`): extract its Deposits with `gates._extract_plan_required_deposits`; if the FIRST `.md` entry's basename does not contain `receipt` → `WARN: (u) step N Deposits: first .md is <basename> — rule_20_self_check reads the first .md as the QA report (thread 77)`; if no entry ends in `.txt` → `WARN: (u) step N Deposits: no .txt evidence entry (thread 70/77)`.

**F4 — tests** (the tier-2 suite): `tests/test_cycle_check.py` gains a parametrized table over the three dimensions above with every cell's verdict forced, the C-2 fixtures (commentary; a 330-byte tail after a real first component — built in a tmp git repo), and the C-3 cases (a relative ref from a tmp project root without the register → `assert-fail:2`; the governance-root fallback monkeypatched to a tmp dir holding the register → `PASS`; an absolute ref → `PASS`); `tests/test_cycle_yields.py` gains the hyphenated prefix cases for all five lenses; `tests/test_plan_lint.py` gains the `weak-spots` no-WARN case and three (u) cases (receipt first → no WARN; report first → WARN; no `.txt` → WARN). **The committed fixtures** `tests/fixtures/checker-defects/{plainonly,longref2,notclosed,hyphen,relref}.md` are the exact files measured at walk 0 (their text is in the register's M-table).

**F5 —** each change carries a one-line comment naming its thread.

## What this plan does NOT do

- Does not touch `gates.py`, the daemon, the depositor, doctrine, or the template. Does not change what `plan_lint` FAILS on — (u) lands as a WARN (the landing posture DRAFTING_CYCLE §4 prescribes). Does not close the four threads (a keyboard act after QA).
- ⚠️ **Dispatch after the five earlier holds** (bootstrap, A, B, W=29, C): no write-set collision with any of them, but a checker change wants the daemon restarted afterwards and the next drafting cycle to be its canary, not a plan already in flight.

## MUST-PRESERVE

- **No real close may read weaker.** The five held drafts and the nine mini-era `Done/executable-1000*.md` plans (bellows and forge) read `BAR_MET` under the current checker (P4); every one must still read `BAR_MET` after F1–F2 — an under-match is a Critical finding.
- **`plan_lint` gains no FAIL.** (u) and the lens pattern are WARN-side; the exit code of every plan that exits 0 today exits 0 after.
- **Worktree discipline:** your cwd IS the claimed tree; `git add` by explicit pathspec; agents do not push; do NOT rename the plan file.
- **`known_failures: 0`.** From the worktree under the canonical venv the suite is `1676 passed, 1 skipped` before this plan (a worktree holds no `config.json`); after, `1676 + N passed, 1 skipped` where N is the new cases, stated. Any failure is a HALT/Critical.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner at bellows `d904f06`)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`SRC`** — the three scripts' shas, pre-edit | `cycle_check.py` `2efd4e2de1a3f9ea` · `cycle_yields.py` `439f2a7f9393305b` · `plan_lint.py` `fabbf1ac2d8ad95a` | `shasum -a 256 scripts/<f> \| cut -c1-16` |
| P2 | **`TESTS`** — the four checker test files, pre-edit | `210 passed` | `BPY -m pytest tests/test_cycle_check.py tests/test_cycle_yields.py tests/test_plan_lint.py tests/test_plan_lint_detector_checks.py -q -p no:cacheprovider` |
| P3 | **`FIXTURES`** — verdicts BEFORE (each fixture's text in the register's M4) | `plainonly` → `CONTINUE` · `longref2` staged INSIDE the bellows checkout (a `lintmirror-` copy under `knowledge/decisions/drafts/`) → `OSError: [Errno 63] File name too long` traceback (from scratch it reads `CONTINUE`) · `notclosed` → `ESCALATE:claimed-close-unmet` · `hyphen` → `BAR_MET` and `parse_lens_line("- Weak-spots: w1 dry")` → `None` · `relref` from a bellows-staged copy → `check_assert_2` `('N/A', False, False)`, verdict `BAR_MET` | `BPY scripts/cycle_check.py <fixture>`; the `parse_lens_line` call from `scripts/` |
| P4 | **`CORPUS`** — the regression baseline | the five held drafts (`bellows-bootstrap`, `shop-server-invariant-sketch`, `shop-server-invariant-company`, `gate2-pt-w28-a` in bellows; `forge-cycle-w29` in forge_lessons) → `BAR_MET` each; the nine `Done/executable-1000*.md` (bellows + forge_lessons) → `BAR_MET` 9 of 9 | `BPY scripts/cycle_check.py <path>` per file, the verdict line read (the last stdout line), never an exit code |
| P5 | **`LINT`** — today's five drafts under (u) | none of the five WARNs (u) — every QA Deposits block lists `qa-receipt.md` first and carries a `.txt`; positive control: `forge_lessons/knowledge/decisions/Done/executable-100007.md` step 3 lists the cycle report FIRST → WARNs (u) | `BPY scripts/plan_lint.py <a lintmirror- copy>` |
| P6 | **`SUITE`** — from the worktree under the canonical venv | `1676 passed, 1 skipped`, exit 0 | `BPY -m pytest tests -q -p no:cacheprovider` |

## Drafting Cycle

**Tier:** T1 — T-8 fires (a corrective clone by kind of 473); T-6 not claimed, following 473/474's ruling; no panel, no scout (every defect reproduced by a committed fixture, the corpus is the canary).

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-checker-defects-2026-09-02.md

**Walk 0 (context pin, measured):** the three scripts' shas and the defect sites by line; the five fixtures written and EXECUTED — from scratch and, for the crash, from inside the checkout (the location decides); the lens-line parser probed for every lens spelling (only the hyphenated weak-spots drops); the corpus baseline read file by file (five held drafts, nine Done plans, all BAR_MET); the four test files counted (210) and the suite line reused from today's worktree-shaped measurement; the closure forms enumerated from DRAFTING_CYCLE §3; the resolver's importability from `scripts/` measured; the clone-diff against 473 in three passes; the consumer dry-run (§2.0) — class assigner `shop-infra`, extractor per step with the receipt first.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (four defects, each reproduced by a fixture whose verdict is pinned; the corpus baseline that no fix may weaken), the mechanism (targeted edits in three scripts, each guarded by a test proven to fail before the edit, and a fourteen-file canary), the scope (WARN-side lint; no gate, no doctrine; the threads closed at the keyboard after QA).

**Walks:**
- Weak spots:          w1 3 folded — instruction 3 / record 0 (a literal `lintmirror-` path in the step text was an existence candidate the linter chased — described instead; a confusing clause about fixture names in the QA report rule — removed; the resolver import needs the bellows root on `sys.path` first, as `plan_lint` does — stated)
- Destruction:         w1 dry — no real close may read weaker (fourteen canaries, an under-match is Critical); `plan_lint` gains no FAIL; the fixtures live under `tests/fixtures/`, never a watched dir; the one transient copy under `drafts/` carries a non-claimable prefix and is deleted in-step
- Vulnerabilities:     w1 dry — the location-dependence of the crash stated and probed from inside the checkout; QA's pre-edit modules from `git show HEAD~1:`, never `git stash`; the negation-stripping closure matcher enumerated against the doctrine's own closing forms
- Integration-record:  w1 dry — the manifest is the emitter's, spliced at the freeze; the class the assigner measured; the block above the first step
- ACID:                w1 dry — one DEV commit by explicit pathspec after the suite; a HALT before it leaves the worktree dirty and nothing landed; QA's commit separate
- **Walk 1 total: 3 findings, 3 folded — instruction 3 / record 0; 0 of 3 fold-introduced.**

- Weak spots:          w2 dry — instruction 0 / record 0 — the three folded sites re-read; F1–F3 re-read against the defect sites by line; the fixture verdicts re-read against the register's M4; the Cycle Log covered
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w2 dry — instruction 0 / record 0 — the manifest emitted at the freeze and spliced; `propagation_check` recorded as it ran
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.**
- Integration-record:  w3 1 folded — instruction 1 / record 0 (the freeze-time conformance run raised `plan_lint` (t): the targets are detectors and the manifest declared no class — `target_class: detector` declared, the state space stated from the system's own dimensions, three mutation manifests (seven one-anchor reverts, each with its killing test) added to Step 1's deposits and the kill map to QA's Item 2.5 — Rule 106 applied to this plan's own fix)
- Weak spots:          w3 dry — instruction 0 / record 0 — the new manifest fields and Item 2.5 re-read; the Cycle Log covered
- Destruction:         w3 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w3 dry — instruction 0 / record 0 — the mutation tool audits committed code; the ordering (DEV commits, QA mutates) stated
- ACID:                w3 dry — instruction 0 / record 0 — unchanged
- **Walk 3 total: 1 finding, 1 folded — instruction 1 / record 0; 0 of 1 fold-introduced (a conformance finding at the freeze).**
- Weak spots:          w4 dry — instruction 0 / record 0 — the folded sites re-read
- Destruction:         w4 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w4 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w4 dry — instruction 0 / record 0 — the manifest re-emitted; (t) and (s) silent
- ACID:                w4 dry — instruction 0 / record 0 — unchanged
- **Walk 4 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 3 → 0 → 1 → 0.

**Conformance (§5):** first run at walk 0 (on v0) and re-run after walk 1's folds and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×15 (worktree-relative deposits); `cycle_check` BAR_MET; `fold_check` re-baselined at each intended change with a note; **`propagation_check` NOT RUN — exit 2 ("no symbol declarations parsed — detector (1) cannot run"): this plan's pin table has no bold `**VALUE**` rows for it to parse; the class it detects is unmeasured here.**

**Closing:** ✅ **BAR MET — walk 4 dry (all five lenses) after walk 1's three folds and walk 3's one (the freeze-time detector declaration); T1, no panel owed, none convened.** Substrate present (the register's rows entered at each phase from captured output and committed at the freeze; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: scripts/cycle_check.py, scripts/cycle_yields.py, scripts/plan_lint.py
class: shop-infra
target_class: detector
state_space: walk-line form {plain `- Walk N:` / bold `**Walk N**` / lens lines (each of the five prefixes, hyphenated and spaced) / none} × closing form {none / the bare mandated heading / NOT CLOSED / BAR MET / met the bar / CYCLE COMPLETE} × register reference {absent / absolute / repo-relative resolvable under the git root / repo-relative resolvable only under the governance root / unresolvable / a line with trailing commentary / a component over 255 bytes} — dimensions read from the SYSTEM (cycle_check's own regexes and parse paths at d904f06, DRAFTING_CYCLE §3's closing forms at v2.23, the corpus's register-line forms), every cell force-classified to a verdict, with a completeness assertion over the cross product
mutants: knowledge/mutants/checker-defects-cycle_check.json
reads: /Users/marklehn/Developer/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/bellows/scripts/cycle_yields.py, /Users/marklehn/Developer/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/bellows/gates.py, /Users/marklehn/Developer/bellows/bellows_root.py, /Users/marklehn/Developer/bellows/knowledge/decisions/Done/executable-473.md, /Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md
writes: scripts/cycle_check.py, scripts/cycle_yields.py, scripts/plan_lint.py, tests/test_cycle_check.py, tests/test_cycle_yields.py, tests/test_plan_lint.py, knowledge/mutants/checker-defects-cycle_check.json, knowledge/mutants/checker-defects-cycle_yields.json, knowledge/mutants/checker-defects-plan_lint.json, tests/fixtures/checker-defects/plainonly.md, tests/fixtures/checker-defects/longref2.md, tests/fixtures/checker-defects/notclosed.md, tests/fixtures/checker-defects/hyphen.md, tests/fixtures/checker-defects/relref.md, knowledge/development/dev-log-checker-defects-2026-09-02.md, knowledge/qa/evidence/checker-defects-2026-09-02/qa-receipt.md, knowledge/qa/evidence/checker-defects-2026-09-02/probes-raw.txt, knowledge/qa/evidence/checker-defects-2026-09-02/full-suite-checker-defects.txt
open_forks: promoting plan_lint (u) from WARN to FAIL after a break-in period (the §4 landing posture); bold `**VALUE**` pin rows in this shape of plan so propagation_check can run; thread 44's walk-register form check as the next checker plan
walks: 4
yields: 3, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 4/4 walks have register rows


---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer. `cd "$(git rev-parse --show-toplevel)" && [ -f scripts/cycle_check.py ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` (re-derive per compound).
>
> ⛔ **A1 — re-derive P1, P2, P3 (all five fixtures — write them from the register's M4 text into `tests/fixtures/checker-defects/` first; for `longref2`'s crash, copy it under the worktree's `knowledge/decisions/drafts/` with a `lintmirror-` prefix — that prefix is not claimable, proven by `is_runnable_plan`; never a plan-shaped name — run, quote the traceback's last line, then DELETE that copy), P4 (fourteen files, fourteen verdict lines), P6. State each; a mismatch is a HALT quoting both.**
>
> **A2 — F1–F3 as specified**, each change with its thread comment. **Prove each post-condition can fail BEFORE the edit** by running the new tests against the pre-edit scripts (they must FAIL — quote the failing node ids), then edit, then run them again (they must PASS).
>
> **A3 — F4 and the kill map:** the tier-2 table in `tests/test_cycle_check.py` (every cell classified; a completeness assertion that the table covers the full cross product of the three enumerated dimensions), the C-2 and C-3 cases, the `cycle_yields` prefix cases, the `plan_lint` cases. Targeted run: the four files → `210 + N passed`, state N and list the new node ids. Then the MUTANTS (the wrong fixes, each a one-anchor revert of one change, each killed by a NAMED test): write three manifests in the `tools/mutation_check.py` form (`{"target": <script>, "mutants": [{name, why, anchor, replacement, expect_fail}]}`) — `knowledge/mutants/checker-defects-cycle_check.json` (M1 the C-1 walk-signal guard removed → `expect_fail` the plain-walks case; M2 the negation stripping removed from the closure matcher → the NOT-CLOSED case; M3 the `OSError` guard removed → the commentary-line case; M4 `UNRESOLVED` accepted by `asserts_ok` → the unresolvable-ref case), `knowledge/mutants/checker-defects-cycle_yields.json` (M5 the weak-spots prefix reverted to `\s*` → the hyphenated-prefix case), `knowledge/mutants/checker-defects-plan_lint.json` (M6 the lens pattern reverted → the `weak-spots` no-WARN case; M7 the (u) first-`.md` test inverted → the report-first case). The tool audits COMMITTED code, so QA runs it after your commit; you run it here against a `git stash`-free sandbox only if you have already committed — otherwise state that the kill map is QA's Item 2.5.
>
> **A4 — the regression canaries (P4 after):** the fourteen corpus files → `BAR_MET` fourteen of fourteen, each verdict line quoted; the five fixtures → `plainonly` `ESCALATE:unparseable` · `longref2` (staged inside, the same `lintmirror-` copy, deleted after) `ESCALATE:assert-fail:2` with NO traceback · `notclosed` `CONTINUE` · `hyphen` `BAR_MET` with all five lenses parsed (`parse_lens_line` → `weak-spots`) · `relref` from the bellows-staged copy `PASS` on the register via the governance-root fallback (the file exists there) — and the same text with a nonexistent register name → `ESCALATE:assert-fail:2`. P5 after: the five drafts no (u) WARN; 100007 step 3 WARNs (u).
>
> **A5 — full suite + dev log + commit.** `"$BPY" -m pytest tests -q -p no:cacheprovider` → `1676 + N passed, 1 skipped`, exit 0. `knowledge/development/dev-log-checker-defects-2026-09-02.md`: the pins, the fail-before/pass-after node ids, the fourteen canary lines, the five fixture lines before and after, the (u) probes, the suite line. `git add scripts/cycle_check.py scripts/cycle_yields.py scripts/plan_lint.py tests/test_cycle_check.py tests/test_cycle_yields.py tests/test_plan_lint.py tests/fixtures/checker-defects/ knowledge/mutants/checker-defects-cycle_check.json knowledge/mutants/checker-defects-cycle_yields.json knowledge/mutants/checker-defects-plan_lint.json knowledge/development/dev-log-checker-defects-2026-09-02.md && git commit -m "[<id from your plan filename>] checker-defects-2026-09-02: cycle_check C-1/C-2/C-3 + CLOSURE_RE (threads 52, 58), the hyphenated lens (63), plan_lint (u) Deposits order (77); tier-2 state-space suite" -- scripts/cycle_check.py scripts/cycle_yields.py scripts/plan_lint.py tests/test_cycle_check.py tests/test_cycle_yields.py tests/test_plan_lint.py tests/fixtures/checker-defects/ knowledge/mutants/checker-defects-cycle_check.json knowledge/mutants/checker-defects-cycle_yields.json knowledge/mutants/checker-defects-plan_lint.json knowledge/development/dev-log-checker-defects-2026-09-02.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-checker-defects-2026-09-02.md`
> - `knowledge/mutants/checker-defects-cycle_check.json`
> - `knowledge/mutants/checker-defects-cycle_yields.json`
> - `knowledge/mutants/checker-defects-plan_lint.json`
> - `scripts/cycle_check.py`
> - `scripts/cycle_yields.py`
> - `scripts/plan_lint.py`
> - `tests/test_cycle_check.py`
> - `tests/test_cycle_yields.py`
> - `tests/test_plan_lint.py`
> - `tests/fixtures/checker-defects/plainonly.md`
> - `tests/fixtures/checker-defects/longref2.md`
> - `tests/fixtures/checker-defects/notclosed.md`
> - `tests/fixtures/checker-defects/hyphen.md`
> - `tests/fixtures/checker-defects/relref.md`
>
> **Scope:**
> - `knowledge/development/dev-log-checker-defects-2026-09-02.md`
> - `scripts/cycle_check.py`
> - `scripts/cycle_yields.py`
> - `scripts/plan_lint.py`
> - `tests/test_cycle_check.py`
> - `tests/test_cycle_yields.py`
> - `tests/test_plan_lint.py`
> - `tests/fixtures/checker-defects/`
> - `knowledge/mutants/checker-defects-cycle_check.json`
> - `knowledge/mutants/checker-defects-cycle_yields.json`
> - `knowledge/mutants/checker-defects-plan_lint.json`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `checker-defects-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/checker-defects-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/checker-defects-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-checker-defects.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt`:**
> - **Item 1 — fail-before / pass-after, by a second pair of hands:** `git stash` is FORBIDDEN; instead `git show HEAD~1:scripts/cycle_check.py > /tmp/cd-qa/cycle_check_pre.py` (and the other two) into `/tmp/cd-qa/`, run the NEW tests against the pre-edit modules by pointing `sys.path` at `/tmp/cd-qa` in a one-off runner — every new case FAILS there (quote the node ids); the same cases PASS against `scripts/`.
> - **Item 2 — the corpus canaries:** the fourteen P4 files → fourteen `BAR_MET` lines; the five fixtures → the A4 verdicts, each quoted; `longref2` staged inside via a `lintmirror-` copy → no traceback, the copy deleted (prove: `ls knowledge/decisions/drafts/ \| /usr/bin/grep -c lintmirror` → 0 after).
> - **Item 2.5 — the kill map (Rule 106):** `"$BPY" tools/mutation_check.py knowledge/mutants/checker-defects-cycle_check.json`, then the `cycle_yields` and `plan_lint` manifests — every mutant `KILLED`, `SURVIVED` 0, `ERROR` 0 (quote each scoring line; the tool audits COMMITTED code — Step 1's commit is HEAD). A mutant that SURVIVES is a missing test, stated as a Critical finding, never a note.
> - **Item 3 — the (u) check:** the five drafts → 0 `(u)` lines each; 100007 → 1 `(u)` line naming the report; a synthetic QA step with no `.txt` → the second `(u)` WARN. And the exit codes: every plan that exits 0 under `HEAD~1`'s `plan_lint` exits 0 under the new one (the fourteen corpus files).
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/checker-defects-2026-09-02/full-suite-checker-defects.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/checker-defects-2026-09-02/full-suite-checker-defects.txt` → the file carries `exit=0` and a summary with 0 failed.
>
> **(C) The report** `qa-receipt.md`: the verification table — status cells carry the glyph only, and NO positive row quotes a probe token or an output line carrying a Rule 20 hedging keyword (`hedging_keywords` in the canonical block — `skipped` among them: the suite summary line is out; rows name the FILE, the exit, and a count) — the follow-ups (the daemon restart, the four threads' closure at the keyboard, the next cycle as the canary), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/checker-defects-2026-09-02/ && git commit -m "[<id>] QA: checker defects — fail-before/pass-after, 14/14 corpus canaries, (u) probes, full suite" -- knowledge/qa/evidence/checker-defects-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/checker-defects-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/checker-defects-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/checker-defects-2026-09-02/full-suite-checker-defects.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/checker-defects-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/checker-defects-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/checker-defects-2026-09-02/full-suite-checker-defects.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
