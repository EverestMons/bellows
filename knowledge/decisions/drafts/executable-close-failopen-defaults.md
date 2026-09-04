# bellows — executable: CLOSE TWO FAIL-OPEN DEFAULTS — `cycle_check`'s manifest gate stops treating silence as innocence, and `plan_lint` (c) stops reading the string `none` as truthy (thread 119, Phase 1 step 1)

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_cycle_check_manifest_provenance.py`, a new `plan_lint` sibling) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100034.md` (the fail-open census — FO-1 and FO-3 are its confirmed entries, with their demonstration inputs) and tuyere thread 119 (the ruling). Clone origin: `Done/executable-100033.md` — the newest shipped plan on `cycle_check`, which introduced FO-1 and is therefore the plan being corrected.

## What this changes

Two conditionals, both converting a permissive default to a safe one:

1. **`cycle_check`** — a `## Cycle Manifest` heading whose stanza does not parse becomes a stanza with **zero keys**, not an absent one. Silence stops being innocence.
2. **`plan_lint` (c)** — the header value is normalized before its truth test, so `none` stops meaning "has QA steps".

⛔ **FO-2 is deliberately NOT in scope.** The census's third confirmed path (`_gate_is_qa_step` on `[2]`) is entangled with thread 116, which measured that NEITHER parser handles the list form and that `gates` masks its own failure with a keyword fallback. Fixing it is three changes and a design question — whether the fallback should exist at all — not a default flip. Closing it here would smuggle a design decision into a mechanical plan.

## Why this exists

CEO ruling, thread 119: *"I don't want there to be optional gates, only a record of pass/fail."* The census found **3** confirmed fail-open paths; these are the two that close without a design question.

⛔ **FO-1 is this author's own defect, shipped as plan 100033 the day before.** That plan gated BAR_MET on manifest key completeness and wrote the skip path itself. **It misses the failure that motivated it:** `halted-executable-100031` — the plan that dispatched past a class hold — yields `stored=None` and is skipped, while `diagnostic-100032` (the lesser failure) is caught. ⚠️ The boundary was justified in 100033's prose by pointing at `plan_lint` (f); measured, (f) on 100031 emits **5 WARNs and exits 0**.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ FO-1, current location | `scripts/cycle_check.py:516-517` — `stored = _manifest_validation_keys(text)` then `if stored is not None and not MANIFEST_VALIDATION_KEYS.issubset(stored): verdict = "CONTINUE"`. The constant is at `:61` | `grep -n "MANIFEST_VALIDATION_KEYS" scripts/cycle_check.py` |
| P2 | ⛔ FO-3, current location | `scripts/plan_lint.py:288` — `if header.get("qa_steps"):` — the header value is a STRING, so `"none"` is truthy | `grep -n 'header.get("qa_steps")' scripts/plan_lint.py` |
| P3 | FO-1's demonstration input | `halted-executable-100031.md` — has a `## Cycle Manifest` heading but no parseable `validation:` field → returns `None` → SKIPPED today | call `_manifest_validation_keys` on it |
| P4 | FO-3's demonstration inputs | 4 `Done` plans carry `qa_steps: none`, and **all four carry banner=0** — every one would fail (c) today | `grep -l` the spelling; count the banner in each |
| P5 | ⛔ FO-1's blast radius is a PAST-corpus artifact | the census measured 544/547 `Done` plans (99.5%) unable to pass a closed gate — **but `cycle_check` runs on plans being AUTHORED, never over `Done/`**, and the gate fires only inside the `verdict == "BAR_MET"` branch. Legacy plans are untouched by construction | read `run_check`'s call sites and the branch guard |
| P6 | what closing FO-1 actually requires of an author | that a plan reaching BAR_MET has an EMITTED manifest — which `DRAFTING_CYCLE.md:253` already mandates ("emitted at BAR_MET") and `cycle_check --emit-manifest` already produces | read DC:253 |
| P7 | ⛔ FO-3's fallback must SURVIVE | (c)'s `else` arm scans step headings for "qa" and is what catches a plan with a QA step that never declared one. Thread 118: do not delete the `qa_steps` arm, normalize its VALUE | read `:288-296` |
| P8 | ⛔ FO-2 is out of scope and why | thread 116 measured that `plan_lint._parse_qa_steps` returns `set()` AND `gates._gate_is_qa_step` declares `[2]` malformed and falls back to keyword detection — right only when a step is titled "QA". Three changes plus a design question | read thread 116 |
| P9 | this plan's own class | run the assigner over the declared write set at execution and confirm `shop-infra`; it will HOLD by design | `_parse_plan` then `_assign_class` |
| P10 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## What this does NOT do

- ⛔ **It does not touch `gates.py`** (P8). FO-2 belongs with thread 116.
- ⛔ **It does not make (c) a FAIL or change its severity** — (c) is advisory today and stays advisory. This corrects WHEN it fires, not how loudly.
- ⛔ **It does not require a manifest to EXIST where none is expected.** The gate fires only inside the BAR_MET branch; a plan mid-cycle is unaffected.
- **It does not backfill any `Done` plan.**

## Drafting Cycle

**Tier:** T1 — T-3 fires (both checkers run on every machine that drafts). **T-6 does NOT fire**, checked against the trigger as QUOTED (*"Edits doctrine, the template, gates, or specialist contracts"*): `cycle_check` and `plan_lint` are authoring-time instruments, and four measured precedents tier `cycle_check` edits at T1 (`100023`, `100025`, `100022`, `100029`), one stating "T-6 no (no doctrine, no gate, no script)". T-8 not fired: clone by kind of `Done/executable-100033.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-close-failopen-defaults-2026-09-04.md`
**Walks:** 0 (context pin complete).

**Closing:** NOT CLOSED at walk 0.

## Cycle Manifest

*(to be EMITTED at BAR_MET with `cycle_check --emit-manifest`, AFTER the dry pass so `validation:` records the closing state — ⛔ do not hand-type it, and ⛔ fill the five AUTHORED fields the emitter leaves as `<declare>`: `class`, `reads`, `writes`, `target`, `open_forks`. Measured 2026-09-04: leaving `writes:` unfilled makes `_parse_plan` fall back to declared deposits and classify on an INCOMPLETE write set — the defect that misclassified plan 100031.)*

## STEP 1 — DEV (two conditionals, two test siblings)

> **Scope:**
> - `scripts/cycle_check.py`
> - `scripts/plan_lint.py`
> - `tests/test_cycle_check_manifest_provenance.py`
> - `tests/test_plan_lint_qa_steps_none.py`
> - `knowledge/mutants/close-failopen-defaults.json`
> - `knowledge/development/dev-log-close-failopen-defaults-2026-09-04.md`
>
> **Item 1 — re-derive P1–P10 and HALT on mismatch.** ⛔ Re-derive both line numbers by grep — `cycle_check.py` gained 34 lines on 2026-09-04 and every pin into it has moved at least once. ⛔ Re-run P3 and P4's demonstrations and confirm both still fail-open; if either now refuses, that path is already closed and this plan's scope must shrink before proceeding.
>
> **Item 2 — write the failing tests FIRST.**
> `tests/test_cycle_check_manifest_provenance.py` (extend the existing sibling):
> 1. ⛔ **a `## Cycle Manifest` heading whose stanza does not parse → verdict is CONTINUE, not BAR_MET** — the FO-1 regression, demonstrated on P3's shape
> 2. ⛔ **NO manifest section at all → CONTINUE**, same reasoning: at BAR_MET a manifest is mandated (P6)
> 3. a complete 4-key stanza → BAR_MET unaffected (the existing behaviour, unchanged)
> 4. a stanza missing one key → CONTINUE (the existing behaviour, unchanged)
> 5. ⛔ **the gate does NOT fire outside the BAR_MET branch** — a mid-cycle plan with no manifest still returns whatever it would have returned
>
> `tests/test_plan_lint_qa_steps_none.py` (new sibling, the clone origin's shape):
> 6. ⛔ **`qa_steps: none` → check (c) does NOT demand a banner** — the FO-3 regression, demonstrated on P4's four plans
> 7. `qa_steps: 2` → (c) demands the banner (unchanged)
> 8. ⛔ **`qa_steps` ABSENT but a step titled "QA" → (c) still demands the banner** — P7's fallback must survive; this is the direction worth keeping strict
> 9. the other accepted spellings (`n/a`, `0`, empty) normalize to absent
> 10. ⛔ **(c) remains ADVISORY** — assert the FAIL count and exit code are unchanged by all of the above
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — close FO-1.** Make `_manifest_validation_keys` distinguish "no manifest section" from "a section that does not parse" is NOT required — both must block at BAR_MET. The simplest correct change is at the call site: treat `None` as an empty key set. ⛔ **Do not widen the gate beyond the `verdict == "BAR_MET"` branch** (P5).
>
> **Item 4 — close FO-3.** Normalize the header value before the truth test: `none`, `n/a`, `0` and empty all mean absent. ⛔ **Keep the `else` arm intact** (P7) — deleting the `qa_steps` arm removes the heading scan that catches undeclared QA steps.
>
> **Item 5 — `knowledge/mutants/close-failopen-defaults.json`**, one mutant per branch: restore `stored is not None` → test 1 fails; drop the no-section arm → test 2 fails; widen the gate outside the BAR_MET branch → test 5 fails; drop the normalization → test 6 fails; delete the `else` arm → test 8 fails. ⚠️ **A survivor is a missing test, stated as Critical**; ⛔ **0 ERROR required**. Every anchor count-1 at HEAD; every `target` a repo-relative path (thread 105: an absolute `target` escapes the sandbox and reports every mutant falsely SURVIVED).
>
> **Item 6 — dev-log**, recording that FO-1 was this author's own defect from 100033, and why FO-2 was excluded.
>
> **Item 7 — commit** (message tagged with the plan id); record `numstat` — exactly 6 files.
>
> **Deposits:**
> - `knowledge/development/dev-log-close-failopen-defaults-2026-09-04.md`
>
> **Post-conditions:** all ten tests pass; every existing `cycle_check` and `plan_lint` test unchanged (counts re-derived at execution, not hardcoded); FO-1's and FO-3's demonstration inputs now REFUSE where they passed, shown as a before/after pair in one run; the mid-cycle case (test 5) proven unaffected; the runner's own mutants all killed, 0 error.

## STEP 2 — QA (full suite + both paths shown closed)

> **Item 1 — full suite** from the dispatch worktree, output to `pytest_full.txt`. ⚠️ The canonical checkout's `config.json` makes `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` fail; a worktree has none and the suite is green there. `known_failures: 0` is correct for the dispatch location — do not raise it.
>
> **Item 2 — both paths shown CLOSED, and shown to have been open.** Run the two demonstration inputs against the pre-change checkers and show each passing; then against the post-change checkers and show each refusing. ⛔ A fixture that only passes after the change proves nothing — it must be shown to discriminate.
>
> **Item 3 — the legacy corpus is untouched (P5).** Confirm `cycle_check`'s call sites never scan `Done/`, and that no `Done` plan is re-evaluated by this change.
>
> **Item 4 — the advisory stays advisory.** `plan_lint`'s FAIL count and exit code on a shipped plan byte-identical before and after.
>
> **Item 5 — the runner's own kill map:** `mutation_check` over `knowledge/mutants/close-failopen-defaults.json` → all killed, 0 survived, **0 error**.
>
> **Item 6 — self-application.** ⛔ Run both changed checkers against THIS plan. It must reach BAR_MET under its own tightened gate — this plan's manifest is emitted, and a plan shipping a gate it would itself trip is the degenerate-exemplar class.
>
> **Item 7 — hygiene + receipt:** numstat vs the DEV commit; toplevel; reflog `-n 4` → 0 amends; per-item table; then the QA self-check block inside a Verification-headed section (the 556 placement law).
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `close-failopen-defaults-2026-09-04`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/close-failopen-defaults-2026-09-04/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/close-failopen-defaults-2026-09-04"`
> - `required_evidence_files`: `["pytest_full.txt", "probes-raw.txt"]`
>
> Include the literal stdout of the block in the QA report. Banner, byte-exact, inside the receipt's VERIFICATION section:
>
> ```
> ============================================================
> Rule 20 — QA Self-Check Results
> ============================================================
> PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
> ```
>
> ⛔ If the block prints `FAILED`, do not proceed with closure — halt and report.
>
> **Deposits:**
> - `knowledge/qa/evidence/close-failopen-defaults-2026-09-04/qa-receipt.md`
> - `knowledge/qa/evidence/close-failopen-defaults-2026-09-04/pytest_full.txt`
> - `knowledge/qa/evidence/close-failopen-defaults-2026-09-04/probes-raw.txt`
>
> **Post-conditions:** suite green from a worktree, 0 failed; both demonstration inputs shown refusing AFTER and passing BEFORE; the legacy corpus proven untouched; the advisory proven still advisory; kill map clean; this plan passes its own tightened gate.
