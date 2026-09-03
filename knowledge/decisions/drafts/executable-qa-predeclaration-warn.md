# bellows — executable: plan_lint (v) — a no-pytest QA step must pre-declare its `qa_test_result` override (thread 70, warn-first with a measured funnel)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the new check) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 70 (open since 2026-09-01, CORRECTED that day — the `.txt`-deposit fix does NOT work); exec-576 (Done 2026-08-27 — the clone origin: `plan_lint` (s)+(t), warn-first with a measured funnel); exec-100026 / exec-100027 (Done 2026-09-02 — the newest same-class plans, whose SECTION ORDER this plan follows rather than 576's); plan 100022 (**halted**, code on main at `e088d05` — wrote check (u), whose `.txt` half is tagged for this thread).

## Why this exists

`_gate_qa_test_result` fires on **every** QA step and has no exemption for a plan that declares no test scope. A doc-only QA step therefore **cannot pass it** — not by depositing a `.txt`, which clears only the first of two branches. The sanctioned remedy is prose: the plan pre-declares the gate's failure as a known-benign class, and the Planner overrides at the verdict with reference to that clause. Four shipped plans do exactly this. Nothing checks that a plan carries the clause.

The cost is measured, not hypothetical. `executable-100013` (2026-09-01) declared no test scope, carried no clause, and its resolved verdict records the gate failing and being **overridden with derivation** — an override improvised at the verdict because nothing prompted the author to pre-declare it. That is the single post-gate instance in the corpus, and this check would have caught it at authoring time.

Thread 70 was first recorded as "QA steps need a `.txt` evidence deposit even when Test Scope is none." **That fix was measured and refuted on 2026-09-01.** Check (u) — shipped 2026-09-02 at `e088d05`, a day after the refutation — implements the refuted half and tags it for this thread. This plan adds the check thread 70 actually needs and corrects that tag.

## ⚠️ What this can and cannot mechanize — stated up front

**Irreducible:** whether a QA step will produce a pytest summary is not knowable from the plan text. The author's `Test Scope:` declaration is the only statement of intent, and it is authored. This plan keys on that declaration and does not pretend to infer it.

**Mechanized:** the CONSEQUENCE. Once an author declares no test scope, the gate's outcome is arithmetic — it will fail on its second branch — so the absence of a pre-declaration clause is a fully mechanical omission to flag.

**Why WARN and never FAIL:** an author may deliberately intend the halt. The check makes the omission visible at authoring time; it does not decide it. Promotion to FAIL is a later plan under the house warn-first law, earned on a re-measured funnel.

⚠️ **Two measured blind spots, stated rather than papered over** (walk 1):

1. **The check is silent when no test scope is declared at all.** Measured: **53 of 306** QA steps in `Done/` declare no `test_scope` field. (v) speaks only where the author volunteered a declaration, so roughly one QA step in six is structurally out of its reach. Closing that would require inferring test scope from step prose — the judgement this section calls irreducible. The blind spot is real, bounded, and not addressed here.
2. **The suppression pattern is negation-blind.** A step reading "no pre-declaration is needed here" contains the token and suppresses the check. This is the sibling of the negation-stripping mutants that SURVIVED at plan 100022 and remain unfixed. Not addressed here: negation-aware matching needs its own tests and its own plan, and the failure direction is a missed WARN on an advisory check — the cheap side.

## Measured funnel (the warn-first house law — prototyped BEFORE authoring)

Measured 2026-09-02 against all 543 `Done/*.md`, using the **shipped predicate** — `gates._gate_is_qa_step`, the gate's own — never a hand-rolled proxy. ⚠️ An earlier draft of this table used the plan header's `qa_steps` field alone and reported 3 fires; that proxy is narrower than the gate (it misses the gate's keyword fallback) and the number was an artifact of it. The corrected figures:

| population | count |
|---|---|
| Done plans | 543 |
| QA steps by the gate's own predicate | **306** |
| …whose `test_scope` starts with `none` | **13** |
| …carrying a pre-declaration clause | 4 (100027, 543, 548, 555) |
| …carrying none → **(v) fires** | **9** |
| …of those 9, authored BEFORE the gate existed (2026-08-18) | **8** — retrospective, expected, harmless |
| …authored after it | **1** — `executable-100013`, 2026-09-01 |

**The single post-gate fire is a confirmed TRUE POSITIVE.** `verdicts/resolved/processed-verdict-100013-step-1.md` records the gate failing on that plan for want of a pytest summary and being overridden with derivation. **False positives on the post-gate corpus: zero.** The eight retrospective fires are closed plans predating the gate; (v) firing on them is expected, exactly as (t)'s retrospective fires were at exec-576.

## The state space (enumerated from system artifacts, not the author's model)

The four correct plans all use the same authored form — a bolded gate-note line declaring the pre-declaration, that there is no pytest scope, and that the Planner overrides. Token counts measured per plan:

| plan | `pre-declar` | `gate note` | `qa_test_result` | `benign` | verdict |
|---|---|---|---|---|---|
| executable-100027 | 5 | 4 | 4 | 4 | suppressed |
| executable-543 | 2 | 1 | 1 | 1 | suppressed |
| executable-548 | 1 | 1 | 1 | 1 | suppressed |
| executable-555 | 1 | 1 | **0** | 1 | suppressed |
| executable-100013 | 0 | 0 | 0 | 0 | **fires** |
| qa-steps-governance-2026-05-25 | 0 | 0 | 0 | 0 | **fires** |
| settings-local-bash-fallback-doc-2026-05-22 | 0 | 0 | 0 | 0 | **fires** |

**Chosen token set: `pre-declar` | `gate note` | `qa_test_result`** (case-insensitive). It separates the measured space cleanly — 4/4 suppressed, 3/3 fired on the sampled rows.

- `qa_test_result` **alone is insufficient** — 555 carries a valid clause without it.
- `benign` is **deliberately excluded**: it separates these seven correctly but appears in **52 Done plans** corpus-wide, so it would suppress a future real omission on an unrelated sentence. Excluded on measured frequency, not taste.
- `no-pytest` — named in thread 70's record — is **dropped**: it occurs in **0** of 543 Done plans. A token no author has ever written cannot discriminate.

## What this plan does NOT do

- **No FAIL arm.** (v) is WARN-only. `plan_lint`'s exit code is unaffected.
- **No change to the gate.** `gates.py` is not touched. The gate's behaviour is correct; this plan changes only what the author is told before deposit.
- **No change to check (u)'s BEHAVIOUR** — one string edit only, narrowing its thread tag, because (u) implements thread 77 and this check implements thread 70. ⚠️ Side effect, stated: `halted-executable-100022.md:34` specifies the old tag as part of what that plan built, so after this edit that halted plan's record describes a string the code no longer carries. **100022's record is NOT edited** — it is a halted plan's historical spec, and striking rather than tidying is the rule; this sentence is the disclosure.
- ⚠️ **No fix to (u)'s QA-step predicate,** though this cycle measured it wrong (see P11). That is a behaviour change to a shipped check with its own blast radius — a separate plan, and a thread to file. This plan only declines to INHERIT the defect.
- **No retro-fitting of the nine plans (v) fires on.** Eight predate the gate; one is closed.
- **No memory writes** (sandbox-denied to agents; the Planner records at close).

## Numbers discipline

⚠️ **Measured 2026-09-02 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | target sha | `scripts/plan_lint.py` = **901 lines**, sha256 `e19f3be6d62419126bdf6b1c62b3272f5f2f5e9cf25816f4b5cec2d869402047` | `shasum -a 256 scripts/plan_lint.py` |
| P2 | insertion anchor | the bare `dc_block` initialisation line — **count-1** in the file, at L373; whole line, len 19 | `/usr/bin/grep -cF` on that line → 1 |
| P3 | retag anchor | the paired thread tag in (u)'s `.txt` message — **count-1**, at L371, a span inside an 89-char f-string | `/usr/bin/grep -cF` on the tag → 1 |
| P4 | anchor provenance | L370–372 last written by `e088d05` (plan **100022**, `lifecycle_state=halted` per `lifecycle.db`); L373 by `9c06524` (plan 324) | `git blame -L 370,373`; `sqlite3 lifecycle.db` |
| P5 | gate branch structure | `_gate_qa_test_result` at `gates.py:769`; branch 1 = no `.txt` → FAIL (`:784-786`); branch 2 = no pytest-summary match → FAIL (`:812-814`). The function reads no test-scope field at any point | read `gates.py:769-836` |
| P6 | the refutation, re-measured | 548's shipped raw-probe evidence file = **63 lines, 0 matches** for `gates._PYTEST_SUMMARY_RE`; positive control fires | the probe in Task A |
| P7 | `_STANZA_REQUIRED` | still the same 10 fields at `:552-555`; the three detector fields still NOT among them (576's E2 re-verified live; line drifted `:538-541` → `:552-555`) | `/usr/bin/grep -n -F '_STANZA_REQUIRED' -A 4` |
| P8 | WARN idiom holds | 19 `results.append` — 9 FAIL, 7 PASS, and **3 in `_extract_hex_tokens`'s own local list**, not the lint results. No advisory check touches the exit code (576's E3 re-verified live) | `/usr/bin/grep -n -F 'results.append'` |
| P9 | suite baseline | **`1814 passed, 1 skipped`** in 54.91s, **1815 collected**, exit 0 — measured from a DAEMON-SHAPED worktree under `.bellows-worktrees/`, which carries no repo-root config file; the canonical checkout DOES carry one and yields a different line | worktree run, 2026-09-02 |
| P10 | no in-flight collision | `lifecycle.db` returns **zero** plans in `claimed`/`in_progress`/`awaiting_verdict` | `sqlite3` query |
| P11 | ⚠️ (u)'s predicate diverges from the gate's | across **861** steps in `Done/`, (u)'s `qa_steps`-or-keyword test disagrees with `gates._gate_is_qa_step` on **74** — **66** where (u) says QA and the gate does not, **8** where the gate says QA and (u) is silent. **(v) must therefore call the gate's predicate directly** | the census script in Task A |
| P12 | class derivation | `depositor._assign_class` on this write set returns **`shop-infra`** from the bellows root (and `app-feature` from tuyere — thread 66 reproduced live). `shop-infra` is the one class that HOLDS for human release | dry-run against the declared write set |
| P13 | ⚠️ **the gate run, not just the commands** | `gates.check(parsed, plan_text, 2, <scratch root>)` against a SIMULATED step 2 with deposit-shaped scratch copies → **passed=True, 0 failures**, `is_qa_step=True`. **Negative control fires:** deleting the summary line from the evidence file yields exactly `qa_test_result: no parseable pytest summary — cannot certify clean; pausing`. Step 1 returns `is_qa_step=False`, confirming P11 at the gate itself | the simulation in Task A |
| P14 | the WARN cannot move a verdict | `run_check.judge_lint(stdout, stderr, code)` branches on the **exit code alone** and never parses stdout (`tools/run_check.py:45-48`) — 576's E3 invariant re-verified at the real consumer, not inferred from the idiom | read `run_check.py:45-48` |
| P15 | retag blast radius | the paired tag occurs in exactly **two** places: the live source line, and `halted-executable-100022.md:34`, that halted plan's historical spec of what it built. **No test asserts it** — `test_u_no_txt_warns` asserts only the check letter and a fragment of the message | `grep -rn` over `*.py` / `*.md`; read the test |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **(v) may not alter `plan_lint`'s exit code.** It prints a WARN only. Prove it: a plan tripping (v) with no FAILs must still exit 0.
- ⚠️ **(v) calls `gates._gate_is_qa_step` — never (u)'s local heuristic.** P11 measured the divergence at 74 of 861 steps. Reusing the neighbouring block's test would import 66 false-positive sites and 8 blind spots. A comment must say so, or a later tidier will "simplify" (v) into (u)'s form.
- ⚠️ **(v) is WARN-only and advisory** — say so in its comment so a later reader cannot promote it by tidying. It keys on an AUTHORED declaration, which no lint can verify.
- ⚠️ **Do not touch `gates.py`.** The gate is correct. A test-scope exemption inside the gate is a different plan at a different tier — the override-at-verdict convention is the shipped answer and the resolved-verdict corpus rests on it.
- ⚠️ **Do not add the test-scope field to `_STANZA_REQUIRED`** or every existing plan starts warning about a field it was never asked for.
- ⚠️ **The nine plans (v) fires on are CLOSED** — this plan does not edit them.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**
- ⚠️ **No date-guard.** `executable-100006` carried a one-day dispatch window and died on it. Nothing here may key on the run date.
- ⚠️ **Second-interpreter compatibility.** `plan_lint` runs on every machine that deposits. This checkout's `CLAUDE.md` names `.venv/bin/python` as the interpreter, but the Air's bellows venv is exactly what **thread 84** is open to reconcile — so a second, older interpreter is a live possibility, not a hypothetical. Write the check to the older dialect: no `match`, no PEP-604 unions evaluated at runtime, no 3.10+ stdlib. ⚠️ **This is a CARRIED pin, not one measured this cycle** — the Air was not probed here. Re-verify at pre-flight or accept the conservative dialect; it costs nothing.
- ⚠️ **This plan's own step 1 trips BOTH of (u)'s arms** — the raw-evidence arm and the report-first arm — because its Item-2 text names the token (u)'s keyword fallback matches, while step 1 is not a QA step by the gate's predicate. Neither arm's premise holds for it: nothing will ever read step 1's deposits as a QA report. Both WARNs are live specimens of P11, are expected, and are **pre-declared here** rather than avoided by rewording — a check silenced by prose the state has not earned is the defect this shop measures, not a clean lint.

## Drafting Cycle

**Tier:** T1 — triggers fired: T-3 (cross-machine: the check runs under a second interpreter on the Air). T-6 assessed and NOT fired: `plan_lint` is a deposit-time checker, not a gate module, and the three shipped same-class precedents (561, 576, 100022) all computed T1. T-8 not fired: structure-for-structure clone of 576.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-qa-predeclaration-2026-09-03.md`
**Walks:** 4 (walks 0–4 complete).
- Weak spots:          w1 3 folded — instruction 2 / record 1; w2 1 folded — instruction 1 / record 0 (step 2's suite command unspecified where the origin gives it exactly); w3 dry; w4 dry.
- Destruction:         w1 2 folded — instruction 0 / record 2; w2 dry; w3 dry; w4 dry.
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0 (a falsy header must degrade, not raise); w3 1 folded — instruction 1 / record 0 (the folded interpreter path was unexecutable from the worktree the same item mandates); w4 dry.
- Integration-record:  w1 1 folded — instruction 1 / record 0 (the corpus lesson mandating a gate run); w2 1 folded — instruction 1 / record 0 (a separate test module per check family, pinned); w3 dry; w4 1 folded — instruction 1 / record 0 (the exit-code invariant's test had no mutant proving it discriminates).
- ACID:                w1 dry — the DEV→QA window's guard is inherited and intact; w2 1 folded — instruction 1 / record 0 (a frozen corpus expectation restated as a supersede rule); w3 1 folded — instruction 1 / record 0 (that fold had half-landed, leaving step 2 contradicting step 1); w4 dry.
**Record decay swept at w4:** the walk count itself had lagged at 2 while walks 3 and 4 ran — the class §3 names, caught by sweeping the log as part of the pass rather than assuming it.
**Walk 0 — context pin (measured 2026-09-02, never recalled):** (1) newest same-class by `git log` on the target = plan 100022 at `e088d05`, `lifecycle_state=halted`; newest SHIPPED same-class = 576 (Done 2026-08-27) — 576 is the clone origin, since the magnitude proxy requires a shipped parent. (2) Both edit anchors measured for line, length and span — P2 whole-line, P3 a span inside a longer literal. (3) Both count-1 file-wide. (4) Provenance per P4. (5) Target sha per P1. (6) **Consumer dry-run (the execution act):** the class assigner returns `shop-infra` (P12 — this plan will HOLD at deposit, by design); the deposit extractor resolves both steps' blocks, and step 2's first report-class deposit and its raw-evidence entry both satisfy (u)'s two arms.
**Walk 0 — clone-diff (three passes + the two the parent's text cannot supply):** FACTS — 576's pins E2 and E3 re-verified live and still true, with the line references drifted and re-pinned. ARTEFACTS — 576's funnel-before-authoring, exit-code invariant and warn-first framing all carried; its `Done/`-corpus prototype method carried and re-run. STRUCTURE — ⚠️ **one inherited defect declined:** 576 places the record sections AFTER the last step, which the current record-placement rule forbids; the newest same-class plans (100026, 100027) place them above the first step, and this plan follows the newest. ⚠️ **Second inherited defect declined:** 576's sibling check (u) supplies a QA-step test this plan was drafted to reuse; P11 measured it wrong and (v) calls the gate's predicate instead.
**Walk 0 findings folded into v1:** 8 — instruction 6 / record 2. Instruction: the predicate correction (P11); the funnel re-measured under the shipped predicate (3 → 9 fires, restratified by the gate's own age); the record-section placement; the two lint FAILs on v0 (a missing self-check banner pair in the QA step, and a step-2 scope block that parsed to zero entries); the plan's own probe lines using an unfixed-string grep against its own rule. Record: the date literals rolled to the authoring date; the sibling-check WARN pre-declared rather than avoided.
**Per-walk yields:** w0 8 (instruction 6 / record 2) · w1 7 (instruction 4 / record 3; 2 fold-introduced) · w2 5 (instruction 4 / record 1; 3 fold-introduced) · w3 2 (instruction 2 / record 0; **both fold-introduced by w2**) · w4 2 (instruction 1 / record 1; both fold-introduced). ⚠️ The fold-introduced share rises across the cycle — the noise-floor signature §2 names, and a reason to suspect circling rather than a licence to close. The countervailing fact is that w3's instruction finding was **unreachable by reading**: the interpreter path was found dead only by RUNNING the folded command from the dispatch-shaped location.
**Walk 1 — standing-rules diff (`bellows/CLAUDE.md`, the pass the parent's text cannot supply):** every probe in this plan uses the interpreter its Start block names; the second-interpreter risk this plan carries in MUST-PRESERVE is the same one thread 84 already tracks, so the pin is re-homed onto that thread rather than asserted from a memory note. No command in this plan violates a standing rule.
**Direction verdict — PROCEED.** The angle is right. None of the three forcing findings fired: (a) the clone origin stands — 576 remains the shipped same-class parent, and the two defects declined (its record placement, its sibling check's predicate) are the clone-diff working as designed, not the origin being invalid; (b) the mechanism is intact — a WARN-only check at a count-1 anchor, gated on an authored declaration; walk 0's predicate correction and walk 1's suppression scoping both refined that mechanism before any implementation existed, which is where refinements are cheapest; (c) the licensing premise — that a no-pytest QA step cannot pass the gate and the remedy is a pre-declared clause — was re-measured twice independently (P6's regex probe with its positive control, and P13's live gate run with its firing negative control) and holds.
**Cold scout (T1, Planner's call — §2.0):** convened on the walk-2-folded artifact, lens-4-shaped, no brief layered, run on the second machine; result pending at this revision and recorded in the walk register when it reports. The close does not precede it.
**Closing:** NOT CLOSED at walk 4 — walk 4 returned one instruction-class finding (the exit-code invariant's missing discriminating mutant), so the bar is unmet and a further confirming pass is owed. This line is deliberately phrased so it cannot match a closure claim until the condition is true.

## Cycle Manifest

*(emitted at BAR_MET by `cycle_check --emit-manifest`; the three detector fields are authored)*

## STEP 1 — DEV (the check + tests + the funnel re-measurement)

> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_qa_predeclaration.py`
> - `knowledge/mutants/qa-predeclaration-plan_lint.json`
> - `knowledge/dev-logs/qa-predeclaration-dev-2026-09-03.md`
>
> **Item 1 — re-derive the load-bearing pins (P1, P2, P3, P6, P9, P11) and HALT on mismatch.** Record measured-vs-expected for each. P6 is the plan's foundation and carries its own positive control; run it with the REAL regex imported from `gates`, never retyped:
>
> ⚠️ **The worktree has no `.venv`** — it is gitignored, so a relative `.venv/bin/python` is dead on arrival from the dispatch cwd. Bind the canonical interpreter by ABSOLUTE path first, as plans 100022 / 100026 / 100027 all do:
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> "$BPY" -c "
> import sys; sys.path.insert(0,'.')
> import gates
> p='knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/probes-raw.txt'
> lines=open(p,encoding='utf-8').read().splitlines()
> hits=[l for l in lines if gates._PYTEST_SUMMARY_RE.search(l.strip())]
> print('lines',len(lines),'hits',len(hits))
> print('control', bool(gates._PYTEST_SUMMARY_RE.search('1814 passed, 1 skipped in 42.13s')))
> "
> ```
>
> Expected `lines 63 hits 0` and `control True`. **A hit count above 0, or a False control, invalidates the plan's premise — HALT and request a verdict.**
>
> ⚠️ **Then re-run P13 — the GATE, not the commands.** Build deposit-shaped copies of this step's own deposits in a scratch tree (never a live path), call `gates.check(parsed, plan_text, 2, <scratch root>)`, and record `passed` and the failure list. **Then run the negative control:** strip the summary line from the scratch evidence file and confirm the gate fails with the no-parseable-summary message. ⛔ A control that does not fire means the simulation is inert and its pass proves nothing — HALT. *(This item exists because the governing lesson of 2026-09-01 — the one this thread produced — is that executing a plan's COMMANDS is not executing the GATES that judge its steps; two full execution passes missed exactly this class.)*
>
> **Item 2 — write the failing tests FIRST** (test-first; 576 corrected this order at its own walk 1 and its shipped text does not show it). ⚠️ **Create `tests/test_plan_lint_qa_predeclaration.py` — a NEW module, pinned, no branch.** Measured: `tests/` holds `test_plan_lint_bare_constants.py` (check (r), plan 561) and `test_plan_lint_detector_checks.py` (checks (s)/(t), plan 576), so the house convention for a new check family is its own module; only (u) and (q) sit in the shared 3300-line file. 576's own walk register records this exact finding — its Task D let the agent CHOOSE the module while Deposits hardcoded one path, so any choice but that path failed `deposit_exists`. **Do not offer a choice here; the path above is the path in Scope and Deposits.** Clone the fixture idiom from `test_plan_lint_detector_checks.py`. The module's tests:
> 1. a no-pytest-scope QA step with no clause → the new WARN appears;
> 2. the same plan carrying the clause → no new WARN line;
> 3. a targeted-scope plan with no clause → silent (the check is gated on the declaration);
> 4. a plan tripping the check with no FAILs → still exits 0;
> 5. the 555 case: the clause present WITHOUT the gate-name token → suppressed (proves the token set is not narrowed to one spelling);
> 6. **step-scoped suppression:** a no-pytest-scope plan whose clause tokens appear ONLY outside its QA step (in a Why-section discussing the gate) → the WARN still fires. Without this test, whole-plan matching passes every other case and silently regresses.
> 7. **headerless plan degrades, never crashes:** a plan whose header does not parse → the lint completes and reports check (a)'s FAIL, with no traceback. Guards the `if header else` idiom above.
> 8. ⚠️ **the predicate regression test:** a NON-QA step whose body merely mentions `Rule 20` — the exact token (u)'s fallback keys on — in a plan whose QA step is elsewhere → the new check stays silent on that step. This is the P11 defect; without this test a later tidier can swap in the neighbouring block's heuristic and no test objects. (Naming the token here is deliberate: describing it instead would dodge (u) by wording rather than by state, and this step's own WARN is the plan's live specimen of P11.)
>
> Run them and record the **failure** output before any implementation exists. A test that passes here is not testing the new check.
>
> **Item 3 — implement the check** immediately before the count-1 anchor of P2, in the WARN idiom of P8 (print, never appended to the results list):
> - QA-step test: `gates._gate_is_qa_step(plan_text, sn, plan_header=header)` — **the gate's own**, per P11 and MUST-PRESERVE.
> - ⚠️ **guard the header exactly as the file already does** — the `… if header else ""` idiom, used at three existing sites (`:344`, `:376`, `:878`). A plan whose header fails to parse yields a falsy header; today that path FAILs check (a) and the lint continues to completion. An unguarded `header.get` here converts that graceful degradation into a traceback, and the lint would stop reporting everything downstream of this check.
> - gate on the header's test-scope value, stripped and lowercased, beginning with the no-scope token.
> - ⚠️ **suppress on the QA STEP'S OWN text, not the whole plan** — `gates._extract_step_text(plan_text, sn)` matched against the three-token pattern of the state-space section, case-insensitively. Measured (walk 1): all four clause-carriers keep their suppression under step-scoping, and the corpus fire count is **9 either way** — so scoping costs nothing and closes a false-negative class, where a plan that merely DISCUSSES the gate outside its QA step silences its own warning. This very plan is that case: its prose names the gate repeatedly while its steps do not.
> - the message must state BOTH branches — that a raw-evidence deposit alone will not clear the gate, and that the remedy is the pre-declared clause plus the Planner's override at the verdict.
>
> **Item 4 — narrow (u)'s thread tag** at the count-1 anchor of P3. One string. No behaviour change. Re-run the lint on an unrelated closed plan before and after and show the WARN set is otherwise identical.
>
> **Item 5 — write the mutants manifest** `knowledge/mutants/qa-predeclaration-plan_lint.json`, in the shape of `checker-defects-plan_lint.json` (`target`, then `mutants[]` of `name` / `why` / `anchor` / `replacement` / `expect_fail`). At least seven:
> - drop the scope gate → the check fires on every QA step; killed by test 3.
> - invert the suppression → fires when the clause is present; killed by test 2.
> - narrow the token set to the gate-name token alone → the 555 case regresses; killed by test 5.
> - **widen the suppression search from the step's text back to the whole plan** → killed by test 6.
> - **drop the header guard** (`header.get(...)` unguarded) → a headerless plan raises; killed by test 7.
> - **swap the gate predicate for the neighbouring block's heuristic** → killed by test 8.
> - ⚠️ **append the finding to the results list as a FAIL instead of printing it** → `plan_lint`'s exit code moves from 0 to non-zero; killed by test 4. **This mutant guards this plan's most load-bearing invariant** (MUST-PRESERVE: the check may never alter the exit code, because `run_check.judge_lint` reads that code as its only channel — P14). Without it, test 4 is an unproven discriminator: it would pass whether or not the invariant is actually enforced, which is the vacuous-check class 576 caught in its own manifest and the class whose survivors halted 100022.
>
> Run `tools/mutation_check.py` against it. ⚠️ **A survivor is a missing test, stated as Critical, never a note** — plan 100022 halted on exactly this and its two survivors are still unfixed.
>
> **Item 6 — re-measure the funnel** on the post-edit code and record the table. Expected: 9 fires across 543 Done plans, 8 of them predating the gate. ⚠️ **The corpus MOVES — `Done/` grows as plans close, so 9 and 543 are authoring-time values, not invariants.** Report YOUR numbers, state the delta against these, and treat a delta as expected rather than as a mismatch. **Only a delta that changes the CLASS of the result — a new post-gate fire, or a clause-carrier that starts firing — is a HALT.** (This is the stale-pin family that killed `executable-100006`'s dispatch window; the defence is a stated supersede rule, not a frozen number.)
>
> **Item 7 — commit** (message tagged with the plan id) and record `numstat` — exactly 4 files.
>
> **Deposits:**
> - `knowledge/dev-logs/qa-predeclaration-dev-2026-09-03.md`
> - `knowledge/mutants/qa-predeclaration-plan_lint.json`
>
> ⚠️ **Gate note:** this step is not a QA step; the raw-evidence arm does not apply to it. Its sibling-check WARN is pre-declared in MUST-PRESERVE.
>
> **Post-conditions:** all eight new tests pass; the funnel re-measures at 9; `mutation_check` reports 7 killed / 0 survived; the lint on a tripping plan exits 0.

## STEP 2 — QA (FULL suite + the check run against REAL plans)

> **Scope:**
> - `knowledge/qa/evidence/qa-predeclaration-2026-09-03/qa-receipt.md`
> - `knowledge/qa/evidence/qa-predeclaration-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/qa-predeclaration-2026-09-03/pytest_full.txt`
>
> **Item 1 — full suite from a WORKTREE**, never the canonical checkout (it carries a repo-root config file and yields a different summary line — P9):
>
> ```
> BPY=/Users/marklehn/Developer/bellows/.venv/bin/python
> "$BPY" -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/qa-predeclaration-2026-09-03/pytest_full.txt
> ```
>
> ⚠️ **`.venv` does not exist inside a worktree** (gitignored) — the absolute bind above is required, not stylistic. A relative `.venv/bin/python` here fails with "no such file or directory" and the step produces no evidence file at all, which the deposit gate then reports as a missing deposit rather than as the interpreter error it actually is.
>
> Expected: the P9 baseline (`1814 passed, 1 skipped`, 1815 collected) plus the eight new tests, 0 failed. **Derive the count from P9 plus your own additions and state the arithmetic; do not assert it from memory.** ⚠️ Run this from a worktree path — confirm with `pwd` and show that no repo-root config file is present, since that file's absence is what makes P9's line the right baseline.
>
> **Item 2 — the check against REAL plans**, raw tails to the raw-evidence file:
> 1. **fires on the known post-gate true positive:** run the lint on `knowledge/decisions/Done/executable-100013.md` and show the new WARN. Its resolved verdict records the gate failing there and being overridden — this is the case the check exists for.
> 2. **silent on all four clause-carrying plans:** 100027, 543, 548, 555 → show a zero count for the new WARN on each. ⚠️ A zero from a plan with no QA step at all is vacuous — confirm each of the four is QA-bearing first and say so.
> 3. **the corpus census:** re-run the Item-6 census and paste the list. Expected 9 at authoring; **apply Item 6's supersede rule — report your number, state the delta, and HALT only on a delta that changes the CLASS of the result.**
> 4. **exit code unaffected:** run the lint on a tripping plan and show `exit=0`. Establish "before" from the commit PRECEDING THIS PLAN'S OWN DEV COMMIT, resolved by its plan-id commit tag — never `HEAD`-relative, and never by `git stash`. Paste the resolved sha and both exit codes.
> 5. **the predicate holds:** run the lint on this very plan and show the new WARN does NOT fire on its step 1 (its scope is targeted), while the sibling check's WARN does — the pre-declared instance of P11.
>
> **Item 3 — re-run `tools/mutation_check.py`** on the committed code and paste the kill map. 7 killed / 0 survived.
>
> **Item 4 — hygiene + receipt** at `qa-receipt.md`: numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; a per-item table; the re-measured funnel stated plainly; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> **Item 5 — commit the evidence** (message tagged with the plan id); verify exactly 3 files.
>
> ⚠️ **Gate note:** a pytest summary is produced by Item 1 and named in the deposits above — the gate parses it; **no benign override is pre-declared for this plan**, because this plan has a real test scope. (Stated explicitly so the QA agent does not import the pre-declaration convention this plan is *about*.)
>
> **Deposits:**
> - `knowledge/qa/evidence/qa-predeclaration-2026-09-03/pytest_full.txt`
> - `knowledge/qa/evidence/qa-predeclaration-2026-09-03/probes-raw.txt`
> - `knowledge/qa/evidence/qa-predeclaration-2026-09-03/qa-receipt.md`
>
> **Post-conditions:** suite green at the derived count; the check fires on 100013; the corpus census matches Item 6's supersede rule (9 at authoring, class unchanged); silent on all four clause-carriers; exit code unchanged; kill map 7/7.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
