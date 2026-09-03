# bellows — executable: plan_lint (u) calls the gate's QA-step predicate (thread 102 — 75 divergences over 865 steps)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the (u) predicate tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 102 (filed 2026-09-03 by plan 100028's cycle, which measured the defect and declined to inherit it); `exec-100028` (Done 2026-09-03 — the clone origin: the newest shipped plan on this exact target, which added check (v) calling the gate's predicate directly); `exec-565` (Done 2026-08-26 — the same-KIND parent: a measured narrowing of a shipped `plan_lint` check's behaviour, not an addition); plan 100022 (**halted**, code on main at `e088d05` — wrote check (u), including the predicate this plan replaces).

## Why this exists

Check (u) asks "is this a QA step?" with its own local test — the plan's `qa_steps` header field, OR the literal Rule-20 banner token appearing anywhere in the step's body. The gate that actually judges the step asks `gates._gate_is_qa_step`. **They disagree on 75 of the 865 `## STEP` headings in header-parsing `Done/` plans** (78 of 872 counted raw).

(u) exists to tell an author, before deposit, what the QA gates will do to their step. ⚠️ **That is a citation, not a framing:** `gates.py:230` computes `is_qa_step` once from `_gate_is_qa_step` and hands that one value to all three blocking QA gates — `_gate_rule_20_self_check` (which reads the first `.md` deposit, (u)'s first arm), `_gate_rule_22_verification`, and `_gate_qa_test_result` (whose first branch is (u)'s `.txt` arm). There is no second QA-step determination in `gates.check`. A warning about a step nothing will ever gate as QA is noise, and silence on a step that WILL be gated is the failure the check exists to prevent. Both are live:

- **67 false positives** — steps (u) calls QA and the gate does not. ⚠️ **Every one comes from the keyword arm; zero from the `qa_steps` arm.** Twenty-seven of them are `diagnostic-*.md` step 1, whose read-only audit prose quotes the banner token while nothing will ever read that step's deposits as a QA report.
- **8 blind spots** — steps the gate calls QA and (u) is silent on. All eight are `## STEP 2 — QA` in plans predating the `qa_steps` header field, so neither of (u)'s arms fires. This is the dangerous direction: the check is quiet exactly where the gate will speak.

Check (v), shipped one commit ago on this same file, already calls `gates._gate_is_qa_step` — with a MUST-PRESERVE clause, a regression test and a mutant, precisely so a later tidier could not "simplify" it into (u)'s form. **This plan makes (u) agree with its own neighbour.** The two predicates sitting six lines apart in one function, answering the same question differently, is the state that produced the 75.

## ⚠️ What this can and cannot mechanize — stated up front

**Mechanized:** the predicate. "Is step N a QA step?" has exactly one authoritative answer — the function the gate calls — and (u) can call it.

**Irreducible, and NOT closed here:** whether `gates._gate_is_qa_step` is itself right. It is not, in one measured respect (the bracket-parse gap — property 1 below, pinned as P10), and this plan deliberately inherits that. (u)'s job is to PREDICT the gate, so where the gate is wrong (u) must be wrong in the same direction, or its warning is false. The gate's own defect is routed as a thread, not smuggled into this plan.

**Why this is a narrowing, not a widening:** 128 WARN lines stop firing and 11 start. The direction of the change is toward silence, and the silence is earned per-step by the gate's own answer.

⚠️ **Two measured properties of the change, stated rather than papered over:**

1. ⚠️ **The fix INHERITS the gate's bracket-parse gap, and that is the point, not an oversight.** `gates._gate_is_qa_step` cannot parse the bracketed string form of the `qa_steps` header (`int("[2]")` raises, it logs `malformed`, and it falls back to keyword detection on the step heading); `plan_lint._parse_qa_steps` strips the brackets and CAN. ⚠️ **Thread 102's record states this the other way round — that plan_lint cannot parse the form and the gate can. Measured 2026-09-03: the opposite.** Live cost today: **zero** — all 3 `Done/` plans carrying that form label their step 2 `— QA`, so the gate's fallback lands on the same answer, and the divergence count is identical with and without them. The gap is real, it is the gate's, and it is owed a thread.
2. **The `qa_steps` arm was never the problem.** All 69 raw false positives come from the keyword arm alone. This is worth stating because the cheap-looking fix — deleting the keyword arm and keeping the header arm — would close the false positives and leave all 8 blind spots standing, since the blind-spot population has no `qa_steps` field at all. Only the gate's own predicate closes both directions.

## Measured funnel (the warn-first house law — prototyped BEFORE authoring)

Measured 2026-09-03 against all 545 `Done/*.md`, running BOTH predicates over the same step population and diffing the emitted WARN lines. ⚠️ The predicate comparison is run with `gates._gate_is_qa_step` imported, never re-implemented.

| population | count |
|---|---|
| `Done/*.md` plans | 545 |
| plans whose header does not parse | 16 |
| `## STEP` headings, raw | 872 |
| …in header-parsing plans (the stated exclusion) | **865** |
| steps where (u) and the gate DISAGREE | **75** (raw: 78) |
| …(u) says QA, gate says NOT — false positives | **67** (raw: 69) |
| …gate says QA, (u) silent — blind spots | **8** (raw: 9) |
| (u) WARN lines emitted over the corpus TODAY | **560**, across 305 plans |
| (u) WARN lines emitted AFTER the fix | **443**, across 270 plans |
| …lines that DISAPPEAR | **128** |
| …lines that APPEAR | **11** |

⚠️ **The 128 and the 11 are line counts over two arms per step; the 67 and the 8 are step counts. They are different units and are not expected to match** — a step can emit zero, one or two lines. The reconciliation: the 8 blind-spot steps emit 11 lines between them; the 67 false-positive steps emit 128.

## The records that cite a (u) WARN — checked, not assumed stale

⚠️ **Doctrine's rule, applied: any plan whose record cites a (u) WARN that then disappears is CHECKED.** Four files in `bellows/` contain the literal WARN prefix; each was resolved to a plan and step and re-run under both predicates.

| record | cited case | under the gate's predicate |
|---|---|---|
| `knowledge/development/dev-log-checker-defects-2026-09-02.md:105` | `eluvian-governance/…/halted-executable-328.md` step 2 | **SURVIVES** — `qa_steps: 2`, heading `— QA`, both arms still fire |
| `…:107` | `executable-100007.md` step 3 (⚠️ the dev-log records its repo as `eluvian-governance`; it is in `forge_lessons`) | **SURVIVES** — `qa_steps: 3`, first `.md` is `reports/lessons-report-2026-09-01.md` |
| `…:109` | three drafts recorded as producing NO (u) WARN | unchanged — a silence cannot disappear |
| `knowledge/qa/evidence/qa-predeclaration-2026-09-03/qa-receipt.md:97` | `executable-100028` step 1, both arms | ⛔ **DISAPPEARS — and that disappearance is this plan's whole point.** 100028's MUST-PRESERVE pre-declares those two WARNs as *live specimens of the divergence*, and its step 1 is a DEV step nothing will gate as QA. The one record whose citation goes silent is the record that filed the thread. |
| `knowledge/decisions/drafts/executable-checker-defects.md:134` / `knowledge/decisions/halted-executable-100022.md:134` | 100007 step 3 again, plus five drafts with no WARN | **SURVIVES** (same case as row 2) |

**Zero shipped records lose a citation they intended to keep.**

## The state space (enumerated from system artifacts, not the author's model)

Every axis below was read off the corpus, never typed from memory.

- **QA-step signal** — `qa_steps` lists the step · the step HEADING carries `qa` · the step BODY carries the banner token · none of these. Measured over 872 headings.
- **`qa_steps` header form** — measured distinct values across 545 plans: `'2'` ×127, `'3'` ×9, `'1'` ×4, `'none'` ×4, `'[2]'` ×3, `'4'` ×1, `'1,2'` ×1, absent for the rest. The `'none'` and `'[2]'` forms are both unparseable by the gate and both fall back to keyword detection.
- **Header parses / does not** — 16 plans do not; a falsy header must degrade, never raise.
- **Deposits shape (the two arms (u) already owns)** — first `.md` carries `receipt` / does not / no `.md` at all; a `.txt` entry present / absent.

Cells are enumerated as tests 1–8 in STEP 1 Item 3, including the positive control (test 1, an unchanged true positive) and the two discriminators no existing test supplies (tests 2 and 3).

## What this plan does NOT do

- **No change to either of (u)'s two ARMS.** The Deposits-order arm and the raw-evidence arm are untouched; only the gate in front of them moves. Prove it: on any step where both predicates agree, the emitted lines must be byte-identical.
- **No change to `gates.py`.** ⚠️ The bracket-parse gap named above is the gate's and is owed a thread; fixing a gate is a different plan at a different tier, and the gates' own tests are not this plan's scope.
- **No change to check (v).** (v) already does what this plan makes (u) do. Its block is read as the idiom to copy and is not edited.
- ⚠️ **No change to the `qa_steps` ↔ step-label cross-check above (u).** That block deliberately compares the header arm against the heading arm and warns when they disagree — the divergence is its SUBJECT. Aligning it to the gate would delete the check. It keeps `_parse_qa_steps`, which is why that helper is not removed.
- **No FAIL arm.** (u) stays WARN-only. `plan_lint`'s exit code is unaffected.
- **No retro-fitting of the 67 plans that stop warning, or the 9 that start.** All are closed.
- **No `LESSONS.md` edit.** The corpus bullet that still teaches the refuted `.txt`-deposit remedy (`LESSONS.md:5224`) was routed by 100028 and remains routed; it is not this plan's subject and is not smuggled in.
- **No memory writes** (sandbox-denied to agents; the Planner records at close).

## Numbers discipline

⚠️ **Measured 2026-09-03 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | target sha | `scripts/plan_lint.py` = **928 lines**, sha256 `0cec3ff1091433f1e0f9ce78c1055ff83511cea39db64c5cc001eb831f534649` | `shasum -a 256 scripts/plan_lint.py` |
| P2 | ⛔ the predicate anchor | the whole line assigning (u)'s local QA test — **count-1** file-wide, at L360, whole line, len 69, 8-space indent (inside (u)'s own `for hl, sn_str in step_headers:` loop) | `/usr/bin/grep -cF` on the whole line → 1 |
| P3 | the dead-binding anchor | the `qa_steps_set_u = …` line — **count-1** file-wide, at L354, whole line, len 77, 4-space indent (function body, ABOVE the loop) | `/usr/bin/grep -cF` on the whole line → 1 |
| P4 | token blast radius | `qa_steps_set_u` occurs **exactly 2×** in the file — L354 and L360, both edited here; **0** occurrences anywhere else in `scripts/`, `tools/`, `tests/`, `gates.py` | `/usr/bin/grep -rn -F 'qa_steps_set_u'` |
| P5 | `_parse_qa_steps` survives | the helper is called at **4** sites — `:346` (the qa_steps↔label cross-check), `:354` (this plan's deletion), `:673` and `:679` (the `pause_for_verdict` coupling checks). Removing `:354` leaves 3 live callers, so the helper is NOT dead and is NOT removed | `/usr/bin/grep -n -F '_parse_qa_steps'` |
| P6 | anchor provenance | L353–362 all last written by `e088d05` (plan **100022**, `lifecycle_state=halted` per `lifecycle.db`). Its halt was two SURVIVING `cycle_check` mutants, not a `plan_lint` defect — and plan 100025 (`386b06f`) has since killed both. Nothing defective is inherited from the halt itself | `git blame -L 353,362`; `sqlite3 lifecycle.db` |
| P7 | ⛔ the divergence, re-measured | over all 545 `Done/*.md`: **75** disagreements across **865** step headings in header-parsing plans — **67** false positives, **8** blind spots. ⚠️ **Reproducible only with the exclusion stated:** count `## STEP` headings ONLY in plans whose header parses; 16 do not, and including them gives 78 over 872 (69 / 9). **The conclusion is identical under both variants**, so a numeric delta here is NOT a halt condition — only a change in the CLASS of the result is | the census in Step 1, Item 1 |
| P8 | ⛔ the WARN-line delta | (u) emits **560** lines across 305 plans today and **443** across 270 after the fix: **128 disappear, 11 appear.** Every disappearing line is on a step the gate does not gate as QA; every appearing line is on a step the gate does | the census in Step 1, Item 1 |
| P9 | the arm attribution | **69 of 69** raw false positives come from the keyword arm; **0** from the `qa_steps` arm. This is why deleting the keyword arm is not the fix — it would leave all 8 blind spots standing | the census in Step 1, Item 1 |
| P10 | ⚠️ the inverted claim in the thread record | `gates._gate_is_qa_step` **cannot** parse the bracketed `qa_steps` string form (logs `malformed`, falls back to keyword); `plan_lint._parse_qa_steps` **can** (it strips `[]`). Thread 102 states the reverse. Live divergence contributed by the form: **0** — all 3 `Done/` plans carrying it label step 2 `— QA` | the probe in Step 1, Item 1 |
| P11 | WARN idiom holds | (u) emits with `print`, never `results.append`; **19** `results.append` calls in the file — 9 FAIL, 7 PASS, and **3 in `_extract_hex_tokens`'s own local list**, a different variable. No advisory check touches the exit code | `/usr/bin/grep -n -F 'results.append'` |
| P12 | the WARN cannot move a verdict | ⚠️ **All three consumers of `plan_lint`'s output read the exit code or stdout, never stderr — read at each consumer, not inferred from one.** (i) `tools/run_check.py:45-48` `judge_lint` branches on the **exit code alone**; (ii) `depositor.py:489-507` reads `lr.returncode` and filters `lr.stdout` for `FAIL:` lines; (iii) `scripts/fold_check.py`'s `is_signal` admits only lines starting `WARN`/`ERROR`/`PIN-CHECK`/`FAIL` or containing `WARN:` | read all three sites |
| P18 | ⛔ **`_gate_is_qa_step` IS the authority, named at its dispatch site** | `gates.py:230` computes `is_qa_step` **once** and passes that single value to all three blocking QA gates — `_gate_rule_20_self_check` (`:582`, which reads `md_paths[0]`, exactly (u)'s first arm), `_gate_rule_22_verification`, and `_gate_qa_test_result` (whose branch 1 is (u)'s second arm). **There is no second QA-step determination anywhere in `gates.check`.** So aligning (u) to this function aligns it to the only thing that decides, for both arms | read `gates.py:215-236, 582-607` |
| P19 | ⚠️ **the fix opens a new STDERR channel — measured, not reasoned** | `_gate_is_qa_step` calls `logger.warning("qa_steps field malformed: %r — falling back to keyword detection", …)` when it cannot `int()` the header value. After the fix (u) triggers that once per step heading on any such plan: **7** `Done/` plans qualify — 3 with the bracketed form, 4 with `none`. **Measured on a constructed fixture:** the line reaches **stderr**, unprefixed, twice for a two-step plan. It moves nothing (P12's three consumers) and is arguably informative — it tells the author the gate cannot read their header | the probe in Step 1, Item 1 |
| P13 | suite baseline | canonical checkout: **`1 failed, 1850 passed`** in 58.67s (1851 collected). ⚠️ **The one failure is a CWD ARTIFACT, not a regression:** `test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` resolves the relative name `config.json`, and the canonical checkout has a real one at its root. **Positive control run:** the same file from a config-free cwd → **`6 passed`**. From a worktree (no `config.json`, gitignored) the expected baseline is **1851 passed** | the run in Step 2, Item 1 |
| P14 | existing (u) tests | three, at `tests/test_plan_lint.py:3285-3380` (`test_u_receipt_first_no_warn`, `test_u_report_first_warns`, `test_u_no_txt_warns`). ⚠️ **All three declare BOTH `qa_steps: 2` AND a `## STEP 2 — QA` heading, so all three pass under EITHER predicate — not one of them discriminates.** That is why this plan adds tests 2 and 3 | read the three fixtures |
| P15 | class derivation | `depositor._assign_class` on this write set returns **`shop-infra`** from the bellows root (and `app-feature` from tuyere — thread 66 reproduced live). `shop-infra` is the one class that HOLDS for human release | dry-run against the declared write set |
| P16 | no in-flight collision | `lifecycle.db` returns **zero** plans in `claimed`/`in_progress`/`awaiting_verdict` | `sqlite3` query |
| P17 | ⚠️ **the gate run, not just the commands** | `gates.check(parsed, plan_text, 2, <scratch root>)` against a SIMULATED step 2 with deposit-shaped scratch copies → `passed=True`, `is_qa_step=True`, 0 failures; `gates.check(…, 1, …)` → `is_qa_step=False`. **Negative control fires:** deleting the summary line from the scratch evidence file yields the `qa_test_result` failure verbatim | the simulation in Step 1, Item 2 |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⛔ **(u) calls `gates._gate_is_qa_step(plan_text, sn, plan_header=header)` — the SAME call (v) makes six lines below, argument for argument.** A comment must say why, or the next tidier reintroduces the local heuristic and no existing test objects (P14).
- ⚠️ **Do NOT guard the call with `if header`.** `_gate_is_qa_step` tests `if plan_header:` internally and falls through to keyword detection on a falsy header. Adding an outer guard would silence (u) entirely on the 16 unparseable-header plans — a NEW blind-spot class created by the fix for the blind-spot class.
- ⛔ **(u) may not alter `plan_lint`'s exit code.** It prints; it never appends to the results list. Prove it: a plan tripping (u) with no FAILs must still exit 0 (P11, P12).
- ⚠️ **Neither ARM changes.** On any step where the two predicates agree, the emitted WARN text must be byte-identical to today's. The regression evidence is a full-corpus before/after diff, not a spot check.
- ⚠️ **Do not touch `gates.py`,** and do not "fix" the bracket-parse gap on the way past. (u) must predict the gate, including where the gate is wrong.
- ⚠️ **Do not remove `_parse_qa_steps` or the `qa_steps` ↔ step-label cross-check at `:344-351`.** Three callers survive (P5), and that cross-check's SUBJECT is the header-vs-heading disagreement.
- ⚠️ **Do not touch check (v).** It is the idiom being copied, not an edit site.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**
- ⚠️ **No date-guard.** `executable-100006` carried a one-day dispatch window and died on it. Nothing here may key on the run date.
- ⚠️ **Second-interpreter compatibility.** `plan_lint` runs on every machine that deposits, and thread 84 is open on the Air's bellows venv. Write to the older dialect: no `match`, no runtime-evaluated PEP-604 unions, no 3.10+ stdlib. ⚠️ **A CARRIED pin, not one measured this cycle** — the Air was not probed here. The change is a single call expression, so the dialect costs nothing.
- ⚠️ **This plan's own STEP 1 trips BOTH of (u)'s arms TODAY, and is expected to — verified by RUNNING the lint, not by reading this sentence.** Step 1 Item 3's test-2 fixture spells the banner token that (u)'s keyword arm matches, while step 1 is not a QA step by the gate's predicate and nothing will ever read its deposits as a QA report. It is a live specimen of the very defect — **pre-declared here rather than avoided by rewording**, because a check silenced by prose the state has not earned is the defect this shop measures. ⚠️ **After this plan ships, that WARN pair is exactly what stops firing** — which makes this plan's own lint output a before/after demonstration, and Step 2 Item 2 case 5 makes it show that. ⚠️ **The two lines are therefore an INTENDED part of this plan's `fold_check` baseline, not drift.**

## Drafting Cycle

**Tier:** T1 — triggers fired: T-3 (cross-machine: `plan_lint` runs on every machine that deposits; thread 84 is open on the Air's venv). T-6 assessed and NOT fired: `plan_lint` is a deposit-time conformance instrument, not one of the step gates — the ruling 561, 565, 576, 100022 and 100028 all took on this same file. T-8 assessed and NOT fired: structure-for-structure clone of 100028 on the same target, and same-KIND as 565 (a measured narrowing of a shipped `plan_lint` check rather than an addition). T-1 assessed: one file plus its tests and manifest, one subsystem. ⚠️ **Newest same-class is a MEASUREMENT, not an assertion:** `git log --oneline -- scripts/plan_lint.py` returns `675f43a [100028]` at its head, so `Done/executable-100028.md` (Done **2026-09-03**) is both the clone origin AND the newest same-class comparison; `exec-565` (Done 2026-08-26) is the same-KIND parent and is diffed separately.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-u-qa-predicate-align-2026-09-03.md`
**Walks:** 0 (in progress — this line is rewritten at each walk's commit).
- Weak spots:          not yet run.
- Destruction:         not yet run.
- Vulnerabilities:     not yet run.
- Integration-record:  not yet run.
- ACID:                not yet run.
**Closing:** the cycle is open; no close claimed.

## Cycle Manifest

<declare>emitted at BAR_MET</declare>

## STEP 1 — DEV (the census, the predicate swap, the tests, the mutants)

> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/mutants/u-predicate-plan_lint.json`
> - `knowledge/dev-logs/u-predicate-align-dev-2026-09-03.md`
>
> **Item 1 — re-derive the load-bearing pins (P1, P2, P3, P4, P5, P7, P8, P9, P10) and record measured-vs-expected for each.** ⚠️ **P7, P8 and P9 are deliberately NOT halt conditions on their numbers** — `Done/` grows, so 545/865/75/560/443 are authoring-time values. **Only a delta that changes the CLASS of the result is a HALT:** a false positive attributable to the `qa_steps` arm, or a disappearing WARN line on a step the gate DOES gate as QA.
>
> ⚠️ **The worktree has no `.venv`** — it is gitignored, so a relative `.venv/bin/python` is dead on arrival from the dispatch cwd. Bind the canonical interpreter by ABSOLUTE path first:
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> ```
>
> Run the census with BOTH predicates over the same step population, importing `gates._gate_is_qa_step` rather than re-implementing it, and emit the two WARN-line sets for a set difference. Record: plan count, headings raw and header-only, disagreements split into false positives and blind spots, WARN lines before and after, and the arm attribution of every false positive.
>
> ⚠️ **Then run the P10 probe and report which side parses the bracketed form:**
>
> ```
> "$BPY" -c "
> import sys; sys.path.insert(0,'.'); sys.path.insert(0,'scripts')
> import gates, plan_lint
> h={'qa_steps':'[2]'}
> print('plan_lint parses ->', plan_lint._parse_qa_steps(h['qa_steps']))
> t='# T\n\n## STEP 2 — DEV\n\n> x\n'
> print('gate says ->', gates._gate_is_qa_step(t, 2, plan_header=h))
> "
> ```
>
> Expected: `plan_lint parses -> {2}` and `gate says -> False`. **If the gate returns True the thread's record is right and this plan's premise sentence is wrong — HALT and request a verdict.**
>
> ⚠️ **Then measure the new STDERR channel (P19) — separate the two streams or you cannot see it.** Lint a plan whose `qa_steps` the gate cannot parse (`Done/executable-312.md`, `Done/executable-313.md`, `Done/executable-324.md` carry the bracketed form; four more carry `none`) with `1>out 2>err` and count the `falling back to keyword detection` lines in `err`. Expected: **0 before the edit** (nothing in (u) calls the gate yet), **one per step heading after it**. ⛔ **Never `2>&1` this probe** — merging the streams is exactly what would hide the channel, and a channel that only appears on stderr is byte-identical, on stdout, to no channel at all.
>
> **Item 2 — run the GATE against a simulated step 2, not just the commands.** Build deposit-shaped copies of **step 2's** deposits in a scratch tree (never a live path — the incident mandate), then:
>
> ```
> parsed = {
>   "receipt_status": "Complete",
>   "ceo_flags": [], "is_error": False, "permission_denials": [],
>   "result_text": "### Files Deposited\n- <the three step-2 deposit paths, one per line>\n",
> }
> res = gates.check(parsed, plan_text, 2, "<scratch root>", files_changed=[<the same three paths>])
> ```
>
> Record `res["passed"]`, `res["is_qa_step"]` and the failure list. Expected `passed=True`, `is_qa_step=True`, 0 failures. **Then the negative control:** strip the summary line from the scratch evidence file and re-run — the `qa_test_result` failure must appear. ⛔ **A control that does not fire means the simulation is inert and its pass proves nothing — HALT.** Also record `gates.check(…, 1, …)`'s `is_qa_step`, which must be `False`.
>
> **Item 3 — write the failing tests FIRST.** ⚠️ **They go in the EXISTING thread-77 section of `tests/test_plan_lint.py`** (measured at `:3285`), beside the three tests already there. **This is a deliberate departure from the separate-module convention 576's register established, and the reason is stated:** that convention is for a NEW check family; (u) is an existing family whose three tests live in that file, and splitting a family across two modules is the worse error. Do not create a new module.
>
> Clone the fixture idiom from the three existing (u) fixtures. Add:
> 1. **positive control — an unchanged true positive:** `qa_steps: 2`, `## STEP 2 — QA`, first `.md` not a receipt → the WARN still fires with byte-identical text. Without this the other tests cannot distinguish "correctly silent" from "broken".
> 2. ⛔ **the false-positive discriminator:** `qa_steps: 2`, a `## STEP 1 — DEV` step whose BODY carries the literal string `Rule 20` — the exact token (u)'s keyword arm matches — with deposits on step 1 that would trip both arms → **no (u) WARN naming step 1**. This is the 67-step class and no existing test reaches it. ⚠️ **The token is spelled out here rather than described, deliberately:** the fixture must contain those exact bytes or it tests nothing, and spelling it makes THIS step a live specimen of the defect (see MUST-PRESERVE).
> 3. ⛔ **the blind-spot discriminator:** **no `qa_steps` field at all**, `## STEP 2 — QA`, deposits tripping an arm → **the WARN fires on step 2**. This is the 8-step class and no existing test reaches it.
> 4. **the header arm without the heading:** `qa_steps: 2` with `## STEP 2 — DEV` (no `qa` in the heading) → the WARN still fires, because the gate's primary arm returns the `qa_steps` membership and never consults the heading. Guards against a mutant that keeps only the keyword fallback.
> 5. **the bracketed form:** `qa_steps: [2]` with `## STEP 2 — QA` → the WARN fires (via the gate's keyword fallback). This is the inherited-gap case, pinned so a later change to `gates.py` shows up here.
> 6. **headerless plan degrades, never crashes:** a plan whose header does not parse, with a `## STEP 2 — QA` heading → the lint completes, reports check (a)'s FAIL, emits (u)'s WARN from the keyword fallback, and produces no traceback. This is the MUST-PRESERVE do-not-add-a-header-guard clause, made executable. ⛔ **This fixture exits NON-ZERO** — measured against the current code: `exit 1`, `FAIL: (a) header — plan header parse returned empty` plus `FAIL: (c) QA banner pair`. Assert `returncode == 1` and `"Traceback" not in stdout+stderr`; **do not clone test 7's `returncode == 0` assertion into it.**
> 7. **exit code unaffected:** a plan tripping (u) with no FAILs → exit 0. Clone the `_QA_PLAN_NO_TXT` fixture, which is measured to return exactly that today.
> 8. **no step headings at all:** a plan with zero `## STEP` headings → no traceback, no (u) output. ⛔ **Also exits NON-ZERO** — measured: `exit 1`, `FAIL: (e) step heading format` plus `FAIL: (c)`. Same warning as test 6.
>
> Run them and record the **failure** output before any implementation exists. ⚠️ **Tests 1, 4, 5 and 7 pass BEFORE the edit** — they are the non-regression half and must be recorded as already-green, with tests 2, 3, 6 and 8 recorded as the failing half. A test that fails to fail is not proving anything; say which is which.
>
> **Item 4 — make the edit. Two lines, both count-1 anchors.**
> - At the P2 anchor (L360, inside (u)'s own loop), replace the local test with `gates._gate_is_qa_step(plan_text, sn, plan_header=header)` — **no `if header` guard** (MUST-PRESERVE).
> - At the P3 anchor (L354), remove the now-dead `qa_steps_set_u` binding. ⚠️ **Assert the deletion with SCOPED probes, and the scope is load-bearing** — a deletion is invisible to a probe that greps only for new strings, and an unscoped probe here reports a false survivor:
>   - `/usr/bin/grep -cF 'qa_steps_set_u' scripts/plan_lint.py` → **0** (was 2). ⛔ **Scope it to that one file.** A repo-wide `grep -rn` returns ~4.3 MB, because the token also lives in `scripts/__pycache__/plan_lint.cpython-312.pyc` and 3 `logs/*.json` dispatch transcripts — neither editable, neither in scope (P4).
>   - `/usr/bin/grep -cF '_parse_qa_steps' scripts/plan_lint.py` → **4** (was 5): one `def` line plus three surviving call sites at `:346`, and the two `pause_for_verdict` checks. ⚠️ **The count includes the `def` line — say the number you expect and what it is made of, or the probe cannot be read** (P5).
> - Extend (u)'s header comment to say WHY the gate's predicate is used, naming the measured divergence and the two directions, so a tidier reading only this block cannot undo it.
> - ⚠️ **Nothing else in the block moves.** Diff the block and confirm the two arms' bodies are byte-identical.
>
> **Item 5 — write the mutants manifest** `knowledge/mutants/u-predicate-plan_lint.json`, in the shape of `knowledge/mutants/qa-predeclaration-plan_lint.json` (`target`, then `mutants[]` of `name` / `why` / `anchor` / `replacement` / `expect_fail`). At least six:
> - **restore the old local heuristic verbatim** → killed by test 2 AND test 3. This is the tidier mutant; it is the one that matters.
> - **keep only the `qa_steps` membership arm** (`sn in _parse_qa_steps(qa_steps_raw)`) → the blind spots return; killed by test 3.
> - **keep only the keyword arm** → killed by test 4.
> - **drop the `plan_header=header` kwarg** so the gate always falls back to keyword detection → killed by test 4.
> - **wrap the call in `if header:`** (the guard MUST-PRESERVE forbids) → the headerless plan goes silent; killed by test 6.
> - ⚠️ **append the finding to the results list as a FAIL instead of printing it** → the exit code moves from 0; killed by test 7. **This mutant guards the plan's most load-bearing invariant** (P11, P12) — without it, test 7 is an unproven discriminator that would pass whether or not the invariant is enforced.
>
> Run `tools/mutation_check.py` against it. ⚠️ **A survivor is a missing test, stated as Critical, never a note.**
>
> **Item 6 — re-run the corpus census on the post-edit code** and record the after-table beside Item 1's before-table, plus the two set differences (lines lost, lines gained) in full. ⚠️ **Assert the byte-identity property:** for every step where both predicates agree, the emitted line text is unchanged.
>
> **Item 7 — commit** (message tagged with the plan id) and record `numstat` — exactly 4 files.
>
> **Deposits:**
> - `knowledge/dev-logs/u-predicate-align-dev-2026-09-03.md`
> - `knowledge/mutants/u-predicate-plan_lint.json`
>
> ⚠️ **Gate note:** this step is not a QA step by the gate's predicate; the raw-evidence arm does not apply to it. Its two (u) WARNs are pre-declared in MUST-PRESERVE and are the plan's own specimen of the defect.
>
> **Post-conditions:** all eight tests pass; `grep -cF 'qa_steps_set_u' scripts/plan_lint.py` → 0; `grep -cF '_parse_qa_steps' scripts/plan_lint.py` → 4 (1 `def` + 3 calls); the census re-measures with the class of the result unchanged; `mutation_check` reports 6 killed / 0 survived; the lint on a tripping plan exits 0.

## STEP 2 — QA (FULL suite + the check run against REAL plans)

> **Scope:**
> - `knowledge/qa/evidence/u-predicate-align-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/u-predicate-align-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/u-predicate-align-2026-09-03/pytest_full.txt`
>
> **Item 1 — full suite from a WORKTREE**, never the canonical checkout:
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> mkdir -p knowledge/qa/evidence/u-predicate-align-2026-09-03
> "$BPY" -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/u-predicate-align-2026-09-03/pytest_full.txt
> ```
>
> ⚠️ **`.venv` does not exist inside a worktree** (gitignored) — the absolute bind is required, not stylistic. A relative interpreter path here produces no evidence file at all, which the deposit gate then reports as a missing deposit rather than as the interpreter error it is.
>
> Expected: the P13 worktree baseline (1851 collected, 0 failed) plus the eight new tests. **Derive the count from P13 plus your own additions and state the arithmetic; do not assert it from memory.** ⚠️ **Confirm with `pwd` that you are in a worktree and show that no repo-root `config.json` is present** — its absence is exactly what makes P13's worktree line the right baseline, and its presence is what makes the canonical checkout report one failure that is not a regression. If a `config.json` IS present, report the failure as the P13 artifact by name and re-run that one test file from a config-free cwd as the positive control.
>
> **Item 2 — the check against REAL plans**, raw tails to the raw-evidence file:
> 1. ⛔ **the false positives are gone:** lint `knowledge/decisions/Done/diagnostic-100024.md` and show that no (u) WARN names step 1. Before the fix it emitted one; its step 1 is a read-only audit step nothing gates as QA.
> 2. ⛔ **the blind spots now speak:** lint `knowledge/decisions/Done/executable-scaffold-2026-04-13.md` and show (u) firing on step 2 (both arms). Before the fix it was silent, and `gates._gate_is_qa_step` returns True for that step — print the predicate's own answer beside the WARN.
> 3. ⛔ **the teeth are intact, proven SIDE BY SIDE** (the mechanism `exec-565` used when it narrowed check (r), carried here): show the identical (u) WARN line before and after the edit on a `Done/` plan whose WARN is RETAINED. **The measured specimen is `knowledge/decisions/Done/executable-100005.md` step 2** — one arm (`first-md`, `'project-producer-qa-2026-08-31.md'`), `qa_steps: 2`, gate predicate `True`. Print `gates._gate_is_qa_step`'s own answer for that step beside the WARN. **A narrowing that cannot be shown still firing on the class it must keep catching has not been proven to have teeth**, and the aggregate census in case 5 cannot substitute for one displayed pair.
> 4. **the cited records still hold:** lint `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/halted-executable-328.md` (step 2) and `/Users/marklehn/Developer/forge_lessons/knowledge/decisions/Done/executable-100007.md` (step 3) and show the WARNs cited in `knowledge/development/dev-log-checker-defects-2026-09-02.md:105,107` still fire. ⚠️ These are absolute paths in OTHER repos, read-only; do not copy, stage or edit them. ⚠️ **If the dispatch sandbox denies the read, that is an expected outcome, not a halt:** say so plainly, cite the authoring-time measurement in the "records that cite a (u) WARN" table, and let case 3's in-repo side-by-side carry the property. ⛔ **Do not work around a denial by copying either file into this repo.**
> 5. **the corpus census:** re-run Step 1 Item 6's census and paste the before/after table and both set differences. **Apply that item's supersede rule — report your numbers, state the delta against 545/865/75/560/443, and HALT only on a delta that changes the CLASS of the result.**
> 6. ⚠️ **the plan's own specimen closes:** lint `knowledge/decisions/Done/executable-100028.md` and show that its step 1's two (u) WARNs no longer fire, while its step 2 stays clean — the citation at `knowledge/qa/evidence/qa-predeclaration-2026-09-03/qa-receipt.md:97` names exactly this pair, and this is the one record whose citation the fix retires. Then lint **this very plan** and show the same pair gone from its own step 1. ⚠️ **Resolve this plan's own file by its id, never by a hardcoded name:** `find knowledge/decisions -name '*executable-<id>*.md'` — the claimed file is renamed through `in-progress-` and `verdict-pending-` as it runs.
> 7. **exit code unaffected:** run the lint on a tripping plan and show `exit=0`. Establish "before" from the commit PRECEDING THIS PLAN'S OWN DEV COMMIT, resolved by its plan-id commit tag — never `HEAD`-relative, and never by `git stash`. Paste the resolved sha and both exit codes.
>
> **Item 3 — re-run `tools/mutation_check.py`** on the committed code and paste the kill map. 6 killed / 0 survived.
>
> **Item 4 — hygiene + receipt** at `qa-receipt.md`: numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; a per-item table; the before/after census stated plainly; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> **Item 5 — commit the evidence** (message tagged with the plan id); verify exactly 3 files.
>
> ⚠️ **On the QA gate:** **this plan has a real test scope.** Item 1 produces the pytest summary the gate parses, named in the deposits below; no override applies here and none should be copied from this step into a doc-only clone.
>
> **Deposits:**
> - `knowledge/qa/evidence/u-predicate-align-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/u-predicate-align-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/u-predicate-align-2026-09-03/pytest_full.txt`
>
> **Post-conditions:** suite green at the derived count; the false-positive specimen silent; the blind-spot specimen firing; both cited records still firing; census class unchanged; exit code unchanged; kill map 6/6.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
