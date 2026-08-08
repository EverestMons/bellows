# Diagnostic: verdict-mechanization distribution refresh — does 04-30's "don't mechanize" survive the delegated-authority era?

**Type:** Diagnostic
**Project:** bellows
**Depends on:** executable-313 (Done — `decided_by` provenance `gate_auto`/`verdict_file` shipped, forward-looking only), executable-312 (Done — gate→verdict seam characterized: gates pure, `gate_events` a faithful mirror)
**Created:** 2026-08-08
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`) and does not parse the filename. This plan uses the slug+date name form; re-read `id_sequence` at deposit, never at authoring.

---

## Why this exists

The question behind this diagnostic: should the daemon's mechanical continue (`decided_by="gate_auto"`, today written only by the auto-close branch at `bellows.py:934-936`) be extended to clean-gate step boundaries — executing mechanically the same rule the delegated-verdict policy (CEO, 2026-07-02) already has the Planner perform manually?

**The standing counter-evidence is the 2026-04-30 audit** (`knowledge/research/verdict-mechanization-distribution-audit-2026-04-30.md`): **"Don't mechanize."** But that recommendation rests on 56 ledger entries over 14 days, with pause reasons **inferred** (the ledger did not record them), gathered **before** the lifecycle DB existed and **before** delegated-verdict authority shifted the continue burden onto the Planner. Its three premises: (1) spurious gate failures dominate the friction (34%) and had separate fixes shipping; (2) remaining pauses are low-friction (~7–15 min/day); (3) mechanizing introduces silent false-positive auto-resolution risk.

**What has changed since, measured by the Planner at authoring (Rule 52 — each is a prediction to re-verify at run, not a value to force):**

- `lifecycle.db` now records `pause_reason_code` natively at every verdict-request site. The live write sites and their values (`bellows.py`): `rule_22_check_failed` (748, 869) · `gate_failure` (750, 763, 871, 656, 929) · `qa_checkpoint` (752) · `agent_verdict_request` (754) · `header_pause` (756) · `auto_close` (934, 936). No inference needed — the axis the audit lacked exists. ⚠️ **The current write sites do NOT enumerate history:** the live table also carries `auto_close_disabled` (12 rows at authoring), a value no current site writes. Start from `SELECT DISTINCT pause_reason_code` and reconcile data against code — never treat the code-site list as the closed set.
- 312 proved the substrate: `gates.check` pure and deterministic; `gate_events` an exact mechanical image (7 standard gates per step). 313 made a mechanical continue auditable (`gate_auto` row from the auto-close branch — the code pattern any extension would clone).
- The `verdicts` table held **556 rows at authoring (554 `decided_by='ceo'`, 2 NULL)** — ~10× the audit's sample. Authoring-time probes (all hedged — verify at run): coverage 314 plans, 2026-06-11 → 2026-08-07, **110 pre-07-02**; **33 `stop` outcomes, 11 of them on clean-code pauses (9 `header_pause`, 2 `qa_checkpoint`)** — the surface signal that the audit's 0% finding-rate does not carry forward naively, and the single strongest reason this diagnostic must read those rows' verdict files; **22 steps carry more than the standard 7 `gate_events` rows** (multi-attempt or appended non-standard gates); 1 verdict row fails the steps join; 0 orphan verdict rows.
- The live record shows the manual load: executable-311 consumed **6** Planner self-issued continues, executable-314 **3**, all on clean gates (verify from the resolved verdict corpus, do not inherit this claim).

⚠️ **Two schema traps, stated so the queries cannot be written wrong:**

1. **`decided_by` CANNOT segment history.** 313 is forward-looking; every pre-313 row reads `'ceo'` regardless of who actually decided. Segment by `pause_reason_code` + `outcome` + the resolved verdict-file corpus — never by `decided_by`.
2. **`verdicts` has NO timestamp column** (`lifecycle.py:118-127`). The time axis is `plans.created_at` via `verdicts.plan_id → plans.id`.

## Questions (deposit findings; decide NOTHING, build NOTHING, CHANGE NOTHING)

**Q1 — Coverage window and full distribution.** Report `MIN(created_at)`/`MAX(created_at)` over `plans`, total plans, total `verdicts` rows. Then the full cross-tab: `outcome × pause_reason_code`, segmented into plans created before vs on/after **2026-07-02** (the delegated-authority date). Wrap both grouping columns in `IFNULL(col,'(NULL)')` so NULL buckets are visible rows, never silently merged or dropped (authoring probe: 1 NULL-outcome row exists). Join `verdicts` to `plans` with LEFT JOIN and report the orphan count (verdict rows with no plans row) rather than letting an inner join eat them. Authoring probe found 110 pre-07-02 plans, so the in-DB pre/post comparison should be viable — but if the pre segment proves thin for a given slice, say so and compare that slice against the 04-30 audit's published table instead of forcing an in-DB comparison. Every count sits next to its exact SQL and raw output.

**Q2 — The clean-gate continue population.** Since 2026-07-02: verdict rows joined to their step (`verdicts → steps` on `plan_id`+`step_number`, then `steps.id → gate_events.step_id`) where the step has **zero `'fail'` rows** AND `outcome='continue'`. ⚠️ "Zero fail rows" is the mandated definition of clean — NOT "exactly 7 pass rows": the authoring probe found 22 steps carrying more than 7 `gate_events` rows (multi-attempt or appended non-standard gates such as `worktree_teardown`), so a 7/7 test misclassifies them; a step with any `fail` row counts as not-clean even if a later attempt passed, and that conservatism is stated in the deposit. Report the count, its share of all pauses, and its breakdown by `pause_reason_code`. Report separately: verdict rows that fail the steps join (authoring probe: 1), steps with zero `gate_events` rows, and `auto_close` rows — that last slice is already mechanical, and it may legitimately be zero (the `auto_close` code shipped with 313 on 2026-08-07; do not force a nonzero). **This count is a population size, not an authorization** — nothing in it licenses the extension; it only prices it.

**Q3 — Finding-rate on clean-gate pauses (the audit's 0%, re-measured at ~10× sample).** The authoring probe found **11 `stop` outcomes on clean-code pauses (9 `header_pause`, 2 `qa_checkpoint`) across the whole table** — verify, then read each such row's resolved verdict file (`verdicts/resolved/`, located via `verdict_file_ref` where set) and quote what the Planner caught, verbatim. Cross-check each against Q2's gate join: a `stop` on a clean-GATE step is direct evidence of a finding the Rule 22(b) read caught and mechanization would have missed; a `stop` whose gates had failures belongs to Q4's population instead — report the two counts separately. For `continue` rows: report the distinct `disposition_summary` values with counts, verbatim — **classify nothing**; the Planner judges substance from the deposit. ⚠️ Name the channel-blindness limitation explicitly: the 04-30 audit recorded that ledger reasons are largely boilerplate, so a low count of substantive summaries can reflect what the channel can carry, not what the Planner found — a zero here is not evidence of absence on its own. Report every rate with its denominator and confidence interval, never the rate alone. This is the measured cost side of dropping the Rule 22(b) read — the fork the CEO must decide.

**Q4 — The residual manual load.** `gate_failure` + `rule_22_check_failed` pauses since 07-02: report the outcome distribution (use the actual `DISTINCT outcome` vocabulary — the authoring probe saw only `continue`/`stop`/NULL; do not assume a `redo` value exists) and, for each, the failing gate names verbatim from that step's `gate_events` `'fail'` rows. **Classify nothing** — the known-benign classes (rule_22c parser truncation, Monitor denial, scope_check on unnamed/sibling tests) are the Planner's read at adjudication, not the agent's. This population stays manual under any mechanization; the deposit sizes what remains.

**Q5 — The seam an executable would extend (report as finding, not decision).** From the implementation — read the branches, do not grep-and-infer — enumerate as code facts: for each pause code observed in Q1's distinct set, whether its write site can mechanically coincide with a clean gate result (e.g., `gate_failure` cannot by construction; which of `qa_checkpoint` / `header_pause` / `agent_verdict_request` / `rule_22_check_failed` fire with clean gates, and whether the step is terminal or non-terminal at that site); what the auto-close branch already covers; and which `notifier` calls fire at each site. Anchor every site by **function/branch name plus a quoted anchor line** — not bare line numbers, which rot under the very executable this feeds (the 313 quoted-anchor convention). No proposal ranking — the enumeration only.

**Q6 — The 04-30 premises, re-measured.** For each of the audit's three don't-mechanize premises, state what today's data says: (1) is the spurious-gate-failure class still the dominant friction, post the gate-precision fixes it anticipated? (2) what is the measured Planner-continue volume per plan now (311's 6, 314's 3 — verified, not inherited)? (3) does the `gate_auto` provenance row + notification change the silent-false-positive premise, and what silent-failure surface remains? Report; the decision is the CEO's.

## Method + boundaries

- **READ-ONLY.** Open the DB read-only: `sqlite3 -readonly /Users/marklehn/Developer/GitHub/bellows/lifecycle.db` (the `-readonly` flag is the mandated form — validated live at authoring; the `file:…?mode=ro` URI form depends on CLI URI handling and is not required). Do NOT edit `bellows.py`, any test, any doctrine file, or any `FORWARD.md`. No daemon start/stop/restart. The findings file is this plan's only write.
- **Raw output or it did not happen.** Every number in the deposit appears next to the command that produced it and that command's raw output. A summarized count with no output block is a defect.
- **Every authoring-time number above is a prediction** (556/554/2, the six pause codes, the line numbers) — verify at run, report the actual, never force a match.
- ⚠️ `grep` is a ugrep shim: `-F` for literals, `--` before leading-dash patterns; a non-`-F` search can exit 1 silently on a present line. The shell is zsh: an unmatched glob aborts the command — use `find … -name '…'`.
- If the daemon is running at dispatch, that is fine — all queries are read-only; do not restart it, and note the pid in the deposit.

## Required deposit structure

`knowledge/research/verdict-mechanization-distribution-refresh-2026-08-08.md`, containing Q1–Q6's answers with raw SQL + raw output for every count, the schema-trap acknowledgments (no `decided_by` segmentation; time via `plans.created_at`), and `## Unresolved` (or NONE).

### Output Receipt

Close with `### Status` (**Complete**), `### Deposits` (the findings file), and `### Ledger Updates` containing `#### Prompt Feedback`. No Forward Register block — this diagnostic enqueues nothing; the follow-on routing is the Planner's, from the findings.

## Drafting Cycle

> **⚠️ THIS SECTION IS A RECORD, NOT INSTRUCTIONS.** Gate-matching strings are described, never quoted.

**Tier:** T1 — **T-7 fires** (a mechanization executable will build on these findings without re-verification). T-8 also recorded as firing under the if-unsure rule: the 04-30 audit is a shape precedent but predates the doctrine, the template, the lifecycle DB, and the `decided_by` axis — this is not a structure-for-structure clone of a verified plan. Highest demand: T1.
**Clone comparison (§2.6 discipline, applied though tier is T1):** origin = the 04-30 distribution audit (`knowledge/research/verdict-mechanization-distribution-audit-2026-04-30.md`); newest same-class shipped diagnostic = `diagnostic-295` (Done), the form source this draft's skeleton follows.
**Walks:** 1 (of the walk phases run so far; ACID pending its own turn).
- Weak spots:          w1 5 folded (1.2 clean-definition vs multi-attempt gate rows; 1.3 pre-07-02 segment assumption → probed, 110 plans; 1.4 Q3/Q4 rephrased so the agent classifies nothing; Q5 code-fact phrasing; `-readonly` mandated form).
- Destruction:         w1 3 folded (2.4 Q2 population-not-authorization clause; Q3 channel-blindness named + clean-gate stops made the primary read; Q5 durable anchors, not line numbers).
- Vulnerabilities:     w1 3 folded (3.4 NULL buckets via IFNULL — 1 live NULL-outcome row; LEFT-JOIN + orphan report; live `auto_close_disabled` rows falsified the closed six-code premise → reconcile-data-vs-code mandated).
- Integration-record:  w1 2 folded (4.1 clone-comparison named — origin audit + diagnostic-295; 4.2 `auto_close` zero-row expectation hedged, 313 shipped 2026-08-07).
- ACID:                not yet run — separate turn per standing phase direction.
**Conflicts:** none yet — no fold violated a prior lens's constraint this walk.
**Closing:** pending — walk 1's last event is a fold, and ACID has not run; not deposited.
