# Executable: rule_20 dispatcher injection — the QA-step prompt carries the Rule 20 mandate MECHANICALLY, ending the plan-wording compliance lottery

**Type:** Executable
**Project:** bellows
**Depends on:** the 360-step-2 and 365-step-2 stop-verdicts (`verdicts/resolved/processed-verdict-360-step-2.md`, `…365-step-2.md` — the measured evidence: two genuine rule_20 block-skips in one day across different plans/projects, both cured only by the 362-form corrective), executable-362/366 (Done — the correctives proving the ordering language works when it REACHES the agent)
**Created:** 2026-08-12
**Author:** Planner
**Slug:** `rule20-inject-2026-08-12`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2
**Test Scope:** targeted (`tests/test_gates.py` baseline **159/0** + `tests/test_bellows.py` baseline **180/0** + the NEW `tests/test_qa_mandate.py`; measured; QA row 3 re-derives; ⚠️ NEVER the full 979-test suite in DEV)

⚠️ **ID NOTE:** id read at deposit (`next_id` **367** at authoring — a PREDICTION; the freeze reads fresh).

## Why
Twice today a QA agent skipped the mandatory Rule 20 self-check block despite the plan spelling it (360 step 2, 365 step 2 — both verified genuine: banner count 0), and twice the 362-form corrective secured compliance by making the ORDER unmissable. The root cause is structural: **the mandate lives in plan wording the agent may compress past, while the gate that fails on its absence is mechanical.** The fix makes the mandate mechanical too: the DISPATCHER appends a Rule-20 mandate suffix to the step prompt whenever the step it is dispatching IS a QA step — detected by the same `_gate_is_qa_step` function the gate layer already uses, so the prompt-side test and the gate-side test CANNOT diverge. Plans keep their Rule 20 sections (the reference the suffix points into); the suffix is belt to the gate's braces. **Effective at the next daemon restart** — the running daemon holds old code; the Planner restarts at an idle window post-plan (an ops action with precedent, NOT this plan's job — stated so no step attempts it).

## Scope
- **`gates.py` (additive):** a module-level `QA_MANDATE_SUFFIX` string + `def qa_mandate_suffix(plan_text, step_number, plan_header=None)` returning the suffix iff `_gate_is_qa_step(...)` — placed directly after `_gate_is_qa_step`. The suffix text (single string, leading space, dispatcher-labelled): *" MANDATORY FOR THIS QA STEP (dispatcher-injected): after writing the QA report WITH its verification table and ALL required evidence files, run the Rule 20 canonical self-check block from /Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md (absolute path), then APPEND its stdout to the deposited report. The banner 'Rule 20 — QA Self-Check Results' and the 'PASSED — SELF-CHECK PASSED' line must appear byte-exact in the deposited report — this step's gate FAILS mechanically without them. Report and evidence files BEFORE the block: it exits nonzero on missing files."*
- **`bellows.py` (three call sites, append-only to existing prompt f-strings):** the step-1 bootstrap (the `Execute Step 1 ONLY` composition, bellows.py:641 region) with step 1; the resume bootstrap (`Execute Step {resume_step}`, :639 region) with `resume_step`; the next-step prompt (`default_next_prompt`, :788 region) with `current_step + 1`. Each site calls `gates.qa_mandate_suffix(<plan text>, <step>, <header>)` — where a plan-text variable is not in scope, READ the plan file the prompt already names (the shadow-prompt source); never re-derive QA-ness by any other test. **The diagnostic bootstrap (:637 region) gets NO suffix** — diagnostics are never QA steps (stated exclusion, not an omission).
- **NEW `tests/test_qa_mandate.py`:** minimum six cases — (1) header `qa_steps: 2`, step 2 → suffix; (2) step 1 → `""`; (3) header list form `[2, 4]`; (4) keyword fallback (`## STEP 3 — QA`, no header field); (5) no step heading at all (diagnostic shape) → `""`; (6) the returned suffix contains BOTH banner literals byte-exact. Import via the same path `tests/test_gates.py` uses.
- **No DB write; no doctrine touch; no LESSONS/FORWARD touch.** Env facts: the standing four.

## Freeze checklist (deposit path — items 1–3 BEFORE the copy, item 4 immediately AFTER)
1. Substitute the read id at the bootstrap `<id>` site AND TASK F's `-m`; probe: `grep -oF -- '<id' <deposit-path> | wc -l` → **2** (both residual on this line).
2. **Diff draft↔mirror immediately before the copy** — empty-except-substitutions is the precondition.
3. Final `plan_lint` at the FAITHFUL mirror — WARN set matches Conformance. A0-fresh: probes still 0-pre (`qa_mandate_suffix` count 0 in both files); shas still the A1 pins; baselines still 159/0 + 180/0.
4. Post-copy `ls` the real `bellows/knowledge/decisions/` — the claim carries the item-1 id.

## Conflict Ledger
**C1** additive-only: no existing gate, prompt, or test line is modified — the three f-strings gain a suffix call, nothing else changes (numstat proves: bellows.py insertions ≥ deletions with deletions ≤ 3 — the three edited lines). **C2** single-source QA detection: the suffix MUST route through `_gate_is_qa_step` — a second detection path is the defect this plan exists to prevent. **C3** commits cd-first (`/Users/marklehn/Developer/GitHub/bellows`) + pathspec + name-only + bare toplevel; post-commit asserts `-C`-pinned to CAPTURE_COMMIT, never `HEAD`. **C4** the daemon-restart boundary stated (Why); no step restarts, kills, or signals the daemon. **C5** serialized dispatch stated.

## How to Run This Plan
**Bootstrap:**
```
Read the plan at knowledge/decisions/in-progress-executable-367.md (the daemon renames on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```
⚠️ HALT ROUTING: Step 1 reads this plan, live `gates.py`/`bellows.py`, the two stop-verdicts. Step 2 reads this plan, the dev-log, the live files, `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`.

---

## Drafting Cycle

**Tier:** T1 — additive bellows code + tests; no DB, no doctrine (T-3 code-change fires → T1). **Newest same-class: 277 (the plan_lint edits pair) by mechanism family; no direct clone origin — the design derives from the live sites read at authoring** (bellows.py:637/639/641/788, gates.py:724 `_gate_is_qa_step` — pure function of (plan_text, step_number, header), verified importable and header-first with keyword fallback).

**Walk 0 (context pin):** shas `gates.py 27c8b779…` / `bellows.py e5ed3450…` (porcelain clean, full values in A1); probes 0-pre (`qa_mandate_suffix` 0 in both); baselines 159/0 + 180/0 measured; `tests/test_qa_mandate.py` ABSENT; the four prompt sites read and their step numbers derived (1 / resume_step / current+1 / diagnostic-excluded); the two stop-verdicts on disk as the evidence base.

**Walk 1** (whole artifact, five lenses, sequential):
- Weak spots:          w1 1 folded — instruction, authoring (the C1 numstat guard first read "insertions only"; the three call-site edits REWRITE their lines, so deletions ≤ 3 is the honest bound — respelled in C1 and QA row 1's numstat expectation).
- Destruction:         w1 dry (append-only to prompts; no gate logic touched; a suffix on a NON-QA step is the only wrong-direction failure and C2's single-source routing makes it equivalent to the gate's own misclassification — no new failure mode).
- Vulnerabilities:     w1 executed — `_gate_is_qa_step` behavior verified live (header list + string + fallback paths read from source); the f-string sites confirmed single-line and append-safe; the suffix text contains no `{`/`}` (f-string-safe, checked) and no backtick/quote hazards for the prompt channel.
- Integration-record:  w1 dry (the two stop-verdicts cited as evidence carry exactly this hardening candidate in their own text; 362/366's Done record is the compliance proof; the daemon-restart boundary follows the config-change precedent from the notifications work).
- ACID:                w1 dry (one code commit + tests behind one gate; no shared-store write; the restart boundary is outside the plan by C4).

**Walk-1 split: instruction 1 / record 0.** Re-opens; walk 2 owed.

**Walk 2** (whole artifact; new surface = the numstat respell):
- Weak spots:          w2 dry (the deletions-≤-3 bound verified coherent at both sites).
- Destruction:         w2 dry.
- Vulnerabilities:     w2 executed, **1 folded — instruction: BOTH A1 sha pins carried FABRICATED TAILS (authored from 16-char display prefixes — the SAME class caught at schema02's walk 2 hours earlier, now committed twice in one day by the same author); fresh full-hash measurements caught them; both pins corrected.** Battery otherwise stable: probes 0-pre re-run; detection rehearsed live (qa2 True / dev1 False); the suffix f-string append rehearsed clean.
- Integration-record:  w2 dry.
- ACID:                w2 dry.

**Walk-2 split: instruction 1 / record 0.** Re-opens; walk 3 owed.

**Walk 3** (whole artifact; new surface = the corrected pins):
- Weak spots:          w3 dry (both pins re-read from the artifact == fresh measurements).
- Destruction:         w3 dry.
- Vulnerabilities:     w3 dry (battery stable on re-run).
- Integration-record:  w3 dry (the class's FOURTH instance today recorded — the predicted-number lint candidate's tally now includes two sha-tail fabrications; the baton carries it).
- ACID:                w3 dry.

**Walk-3 split: instruction 0 / record 0 — LITERAL DRY. The §2 bar met; T1, no panel owed.**

**Conformance (§5):** at shape-stability and at deposit, at the FAITHFUL mirror (fidelity: `gates.py`, `bellows.py`, `tests/test_gates.py`, `tests/test_bellows.py`, both stop-verdict files under the mirror root). **Measured at the faithful mirror: EXIT 0, ONE WARN — the (o1) on `tests/test_qa_mandate.py`, which DOES NOT EXIST until Step 1 creates it (the honest expected set; a second WARN = fidelity gap, fix the mirror not the plan).** Last run: at deposit.

**Closing:** walk 3 dry — instruction 0 / record 0; closed on the dry branch after 3 walks; residue: none.

---

## STEP 1 — DEV (the helper, three call sites, the test module, commit)

> **FIRST — visible chat message; do NOT rename this plan file.** Edits land in the bellows repo at absolute paths; a HALT after edits leaves the tree as-is, reported loudly.
> **A0 (first match wins):** (1) `qa_mandate_suffix` present in both files + tests green → verify commit-by-slug via QA row-1's spelled discovery; report complete. (2) present in gates.py only, or tests absent → deposit-completion: finish the missing pieces against the committed state, never re-add what exists. (3) fresh — probes 0 in both files, `tests/test_qa_mandate.py` absent, porcelain clean for the three paths → A1. Other → HALT with the observed triple.
> **A1 — pins:** `shasum -a 256` of `/Users/marklehn/Developer/GitHub/bellows/gates.py` == `27c8b7796ac1ce2dc1b5c961ed951f4240be2f98acb0d97f4b2205bade45e36d` AND `/Users/marklehn/Developer/GitHub/bellows/bellows.py` == `e5ed34508104764aa0e5a18575a239dfbc130aa579e8243a51a6deab475e67fb`. Mismatch → HALT (a foreign in-window edit; report, never merge).
> **TASK G — gates.py:** insert, DIRECTLY after the `_gate_is_qa_step` function body (anchor: the function's closing `return False` line — assert the anchor context is unique by grepping `def _gate_is_qa_step` count 1 first), the `QA_MANDATE_SUFFIX` constant and `qa_mandate_suffix` function EXACTLY as specified in Scope (temp-and-replace python write, never sed -i). Post: `grep -cF 'def qa_mandate_suffix' gates.py` → 1; `grep -cF 'QA_MANDATE_SUFFIX' gates.py` → 2; `python3 -c "import gates; print(gates.qa_mandate_suffix('## STEP 2 — QA', 2))"` prints the suffix; `…('## STEP 1 — DEV', 1)` prints empty.
> **TASK B — bellows.py three sites** (each: locate the exact f-string, assert count 1, append the suffix call INSIDE the composition): (i) the `Execute Step 1 ONLY` bootstrap → `{gates.qa_mandate_suffix(<plan-text>, 1, <header>)}`; (ii) the `Execute Step {resume_step}` bootstrap → step `resume_step`; (iii) `default_next_prompt` → step `current_step + 1`. Where no plan-text variable is in scope, read the plan file the prompt names (same file, one `io.open(...).read()`), binding header from the already-parsed header variable at that site. **The diagnostic bootstrap gets NOTHING.** Post: `grep -cF 'qa_mandate_suffix' bellows.py` → **3**; `python3 -c "import ast; ast.parse(open('bellows.py').read())"` exits 0.
> **TASK T — tests:** write `tests/test_qa_mandate.py` with the six specified cases (Scope), same import pattern as `tests/test_gates.py`. Run FOREGROUND, targeted ONLY: `python3 -m pytest tests/test_qa_mandate.py tests/test_gates.py tests/test_bellows.py -q` → new module ≥6 passed, `test_gates` **159**, `test_bellows` **180**, zero failures (a failure → HALT with the raw tail; never patch a failing assertion to green).
> **DOC_SHAs** pinned before commit. **TASK F:** `cd /Users/marklehn/Developer/GitHub/bellows && git add gates.py bellows.py tests/test_qa_mandate.py && git commit -m "[367] rule20-inject(rule20-inject-2026-08-12): dispatcher-injected Rule 20 mandate on QA-step prompts — single-source via _gate_is_qa_step; evidence: the 360/365 stop-verdicts" -- gates.py bellows.py tests/test_qa_mandate.py && git rev-parse HEAD && git rev-parse --show-toplevel` (expect the hash then `/Users/marklehn/Developer/GitHub/bellows`). **CAPTURE_COMMIT = the printed hash.** Numstat, spelled: `git -C /Users/marklehn/Developer/GitHub/bellows show <CAPTURE_COMMIT> --numstat --format=` → exactly THREE lines — `gates.py` insertions ≥ 10 with deletions 0; `bellows.py` deletions ≤ 3; `tests/test_qa_mandate.py` all-insertions; name-only exactly the three paths.
> **Receipt** with CAPTURE_COMMIT + the three numstat lines + the four probe values + the test tallies · `#### Prompt Feedback` · `#### Forward Register`: `NONE`. **FINAL ACTION** — commit deposits: cd-first + pathspec + name-only + bare toplevel.
>
> **Scope:**
> - `knowledge/development/dev-log-rule20-inject-step-1-2026-08-12.md`
>
> **Deposits:**
> - `bellows/knowledge/development/dev-log-rule20-inject-step-1-2026-08-12.md`

## STEP 2 — QA

> **FIRST — do NOT rename this plan file. Deliverable Verification (Rule 8/17)**, ✅/❌ table, any ❌ → HALT. **Rule 20 self-check** (canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`; `plan_slug`: `rule20-inject-2026-08-12`; `qa_report_path`: `<tree>/knowledge/qa/rule20-inject-qa-2026-08-12.md`; `evidence_dir`: `<tree>/knowledge/qa/evidence/rule20-inject-2026-08-12/`; `required_evidence_files`: `[code-probes.txt, behavior.txt, pytest_targeted.txt]`, all three BEFORE the block; literal stdout: the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line, byte-exact — ⚠️ this plan EXISTS because two QA agents skipped this exact block; the gate that fails without it is the one this plan hardens).
> **1. CODE INTEGRITY** — commit by slug spelled: `git -C /Users/marklehn/Developer/GitHub/bellows log -n 1 --format='%H %s' --grep='rule20-inject-2026-08-12' -- gates.py` → exactly one line; committed shas == live; numstat three lines per the Step-1 bounds; name-only exact; porcelain clean for the three paths. → `code-probes.txt`
> **2. BEHAVIOR** — run live: `python3 -c "import gates; s=gates.qa_mandate_suffix('## STEP 2 — QA', 2); print(len(s)); print('Rule 20 — QA Self-Check Results' in s); print('PASSED — SELF-CHECK PASSED' in s)"` → nonzero / True / True; the step-1 non-QA call prints empty; `grep -cF 'qa_mandate_suffix' bellows.py` → 3 with the diagnostic bootstrap site clean (`grep -F 'single-step investigation' bellows.py | grep -cF 'qa_mandate_suffix'` → 0). → `behavior.txt`
> **3. TESTS** — `python3 -m pytest tests/test_qa_mandate.py tests/test_gates.py tests/test_bellows.py -q` FOREGROUND → vs ≥6 / 159 / 180, delta reported never asserted. → `pytest_targeted.txt`
> `## Evidence and Narrative` · Receipt · `### Ledger Updates` · `#### Forward Register`: `NONE`. **FINAL ACTION — commit-evidence-first:** cd-first + pathspec + name-only + bare toplevel.
>
> **Scope:**
> - `knowledge/qa/rule20-inject-qa-2026-08-12.md`
> - `knowledge/qa/evidence/rule20-inject-2026-08-12/code-probes.txt`
> - `knowledge/qa/evidence/rule20-inject-2026-08-12/behavior.txt`
> - `knowledge/qa/evidence/rule20-inject-2026-08-12/pytest_targeted.txt`
>
> **Deposits:**
> - `bellows/knowledge/qa/rule20-inject-qa-2026-08-12.md`
> - `bellows/knowledge/qa/evidence/rule20-inject-2026-08-12/code-probes.txt`
> - `bellows/knowledge/qa/evidence/rule20-inject-2026-08-12/behavior.txt`
> - `bellows/knowledge/qa/evidence/rule20-inject-2026-08-12/pytest_targeted.txt`
