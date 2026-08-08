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

- `lifecycle.db` now records `pause_reason_code` natively at every verdict-request site. The live write sites and their values (`bellows.py`): `rule_22_check_failed` (748, 869) · `gate_failure` (750, 763, 871, 656, 929) · `qa_checkpoint` (752) · `agent_verdict_request` (754) · `header_pause` (756) · `auto_close` (934, 936). No inference needed — the axis the audit lacked exists.
- 312 proved the substrate: `gates.check` pure and deterministic; `gate_events` an exact mechanical image (7 standard gates per step). 313 made a mechanical continue auditable (`gate_auto` row from the auto-close branch — the code pattern any extension would clone).
- The `verdicts` table held **556 rows at authoring (554 `decided_by='ceo'`, 2 NULL)** — ~10× the audit's sample.
- The live record shows the manual load: executable-311 consumed **6** Planner self-issued continues, executable-314 **3**, all on clean gates (verify from the resolved verdict corpus, do not inherit this claim).

⚠️ **Two schema traps, stated so the queries cannot be written wrong:**

1. **`decided_by` CANNOT segment history.** 313 is forward-looking; every pre-313 row reads `'ceo'` regardless of who actually decided. Segment by `pause_reason_code` + `outcome` + the resolved verdict-file corpus — never by `decided_by`.
2. **`verdicts` has NO timestamp column** (`lifecycle.py:118-127`). The time axis is `plans.created_at` via `verdicts.plan_id → plans.id`.

## Questions (deposit findings; decide NOTHING, build NOTHING, CHANGE NOTHING)

**Q1 — Coverage window and full distribution.** Report `MIN(created_at)`/`MAX(created_at)` over `plans`, total plans, total `verdicts` rows. Then the full cross-tab: `outcome × pause_reason_code`, segmented into plans created before vs on/after **2026-07-02** (the delegated-authority date). Every count sits next to its exact SQL and raw output.

**Q2 — The mechanizable population.** Since 2026-07-02: verdict rows whose step's `gate_events` are all-pass (7/7 `pass`, join `steps → gate_events` on the matching `plan_id`+`step_number`) AND `outcome='continue'`. Report the count, its share of all pauses, and its breakdown by `pause_reason_code`. Report `auto_close` rows separately — that slice is already mechanical. State explicitly how many rows lack `gate_events` coverage (older rows may predate the table) rather than silently dropping them.

**Q3 — Finding-rate on clean-gate pauses (the audit's 0%, re-measured at ~10× sample).** Among clean-gate pauses since 07-02: how many resolved as anything other than plain `continue` (`stop`, redo-shaped outcomes), and how many `continue` rows carry a `disposition_summary` (or resolved verdict file under `verdicts/resolved/`) recording a substantive condition or correction? This is the measured cost of dropping the Rule 22(b) read — the fork the CEO must decide. Carry the audit's own caveat forward: report the confidence interval alongside the rate, not the rate alone.

**Q4 — The residual manual load.** `gate_failure` + `rule_22_check_failed` pauses since 07-02: what fraction resolved `continue` (the known-benign classes — rule_22c parser truncation, Monitor denial, scope_check on unnamed/sibling tests) vs `redo`/`stop` (genuine)? This population stays manual under any mechanization; size what remains.

**Q5 — The seam an executable would extend (report as finding, not decision).** From code, enumerate: which pause classes are lawfully coverable by a `gate_auto` continue (clean gates + which of the six codes; terminal vs non-terminal; are `qa_checkpoint` steps in or out and why), what the auto-close branch already covers, which notification obligations fire at each site (`notifier` calls), and the exact `bellows.py` line ranges a clean-gate `gate_auto` continue would touch. No proposal ranking — the enumeration only.

**Q6 — The 04-30 premises, re-measured.** For each of the audit's three don't-mechanize premises, state what today's data says: (1) is the spurious-gate-failure class still the dominant friction, post the gate-precision fixes it anticipated? (2) what is the measured Planner-continue volume per plan now (311's 6, 314's 3 — verified, not inherited)? (3) does the `gate_auto` provenance row + notification change the silent-false-positive premise, and what silent-failure surface remains? Report; the decision is the CEO's.

## Method + boundaries

- **READ-ONLY.** Open the DB read-only: `sqlite3 'file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro'`. Do NOT edit `bellows.py`, any test, any doctrine file, or any `FORWARD.md`. No daemon start/stop/restart. The findings file is this plan's only write.
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
**Walks:** v0 authored 2026-08-08. The five-lens walk required by T1 has not run; this draft does not deposit until it has.
**Conflicts:** ledger opens at w1.
**Closing:** pending — the last event is v0 authorship, not a lens pass.
