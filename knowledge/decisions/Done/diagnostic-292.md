# Diagnostic: the Forward Register item-delimiter contract — can a multi-item Receipt block be split WITHOUT re-opening the narration hole plan 62 closed?

**Type:** Diagnostic
**Project:** bellows
**Depends on:** plan 291 (Done — proved the append channel works end to end; its one-item Receipt block landed as FORWARD.md row 1 in lessons-forge), plan 62 (Done — shipped the single-line sanitizer this diagnostic questions)
**Created:** 2026-08-02
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T1

## Why this exists — a backlog with a one-item-per-plan carrier, and a guard nobody should remove blind

`_append_forward_row` (`bellows.py:1409`) is invoked **once per step** with the entire `#### Forward Register` Receipt block (`bellows.py:1355`) and reduces it to its FIRST non-empty line:

```python
lines = [ln.strip() for ln in item_text.splitlines() if ln.strip()]
item_text = " ".join(lines[0].split()) if lines else item_text.strip()
```

**One block therefore produces exactly one row.** Plan 288 emitted six items as `- (a)`…`- (f)` and would have landed only `(a)`; plan 291 emitted one item deliberately, for this reason, and it landed correctly. **Four backlog items (the three `plan_lint` §4 defects and the `generate_lessons_report` encoding gap) currently have no carrier and survive only in the session baton.**

**⚠️ THE OBVIOUS FIX IS THE ONE THIS DIAGNOSTIC EXISTS TO QUESTION.** The Planner's first instinct — "split the block into N rows" — was **wrong on the record**, and the record corrected it. `tests/test_bellows.py::TestForwardSingleLineItem` (`:4917`) is titled *"Plan 62: `_append_forward_row` sanitizes item_text to a single line"* and its fixture is:

```
CANARY item text here

Now commit the deposit.
Complete. All 5 checks passed.
```

with the assertions `"Now commit" not in row` and `"All 5 checks" not in row`, under the comment *"Trailing prose excluded."* **The trailing text is AGENT NARRATION that bled past the Receipt section boundary.** The single-line reduction is a deliberate guard against exactly that, not an oversight. A naive splitter would file "Now commit the deposit." and "Complete. All 5 checks passed." as Forward Register entries.

**So the question is not "how do I split" but "can structured items be separated from unstructured narration reliably enough to be worth the change at all."** Answer it from the real corpus; decide nothing; build nothing.

## What the Planner verified before writing this (Rule 52 — measured at authoring, not inherited)

- `_append_forward_row` is called ONCE per step with the whole block (`bellows.py:1355`), and its sanitizer keeps `lines[0]` — read from source, not assumed.
- Row numbering derives from `max` of `^\|\s*(\d+)\s*\|` across the whole file, so a preamble containing a pipe-digit-pipe row would shift it.
- The append is idempotency-gated on `f"{plan_id}-{step_number}"` plus a SHA-256 of the block (`bellows.py:1349`), so an identical re-emission on a redo is skipped.
- The daemon skips its own write entirely if the agent touched the file (`if any("FORWARD.md" in f for f in files_changed)`).
- `bellows/knowledge/FORWARD.md` carries **24 rows** — the mechanism has been live in this project for months.
- `lessons-forge/knowledge/FORWARD.md` carries **1 row**, appended by plan 291 on 2026-08-02.
- Bellows suite baseline: **834 passed**, measured at authoring.
- **The daemon IS `bellows.py`, running as a live process** — so unlike `plan_lint` (which diagnostic 276 proved the daemon never invokes), any edit here requires a daemon restart. That is an operational fact any downstream plan must carry.

## Questions (deposit findings; decide NOTHING, build NOTHING)

**Q1 — Enumerate every `#### Forward Register` block ever emitted, across all watched projects.** For each: the emitting plan, the raw block text, how many items a human would say it contains, and what `lines[0]` actually produced. Sources to sweep — QA reports and dev-logs under `knowledge/` in `bellows`, `lessons-forge`, `governance`, and `anvil`. **This is the corpus every later question is tested against; do not reason from a sample.**

**Q2 — Classify the shapes.** At authoring, four are already visible: a `- (a)`…`- (f)` bulleted list (plan 288); a single unbulleted line (plan 291); a single `- ` bullet; and bare multi-sentence prose. **Report the ACTUAL distribution from Q1, not this list** — it is a starting hypothesis, not a finding.

**Q3 — How many items has the current behaviour actually dropped?** For every historical block with more than one item, name what landed and what did not. **Distinguish items lost to `lines[0]` from items never appended because the destination file did not exist** — the second class is plan 291's already-fixed problem and must not be double-counted. Quantify the real cost of doing nothing.

**Q4 — Is there a delimiter rule that separates structured items from narration?** Prototype at least one candidate (e.g. "if ≥2 lines match a leading-bullet pattern, emit one row per bullet; otherwise fall back to `lines[0]`"). **Test it against the WHOLE Q1 corpus and report per-block results.** ⚠️ **Plan 62's fixture is the mandatory NEGATIVE CONTROL: the narration case MUST still collapse to one row.** A candidate that admits "Now commit the deposit." is refuted, not tuned. ⚠️ **Also required: a positive control** — plan 288's six-bullet block must yield six rows. **A candidate that cannot do both is reported as such; do not soften either control to make one pass.**

**Q5 — What breaks in the wrapped-prose case?** If an item's text wraps across lines in the source Markdown, does the candidate fragment it into bogus rows? Test against any real wrapped item found in Q1; if none exists, construct one from a real item's text and say you constructed it.

**Q6 — Idempotency and row numbering under N rows.** With one block yielding N rows: is the existing `(plan_id, step)` + content-hash key still correct on a step redo? What happens if the process dies after row 3 of 6 — does the marker record a partial write as complete? Does `max`-based numbering stay correct across N appends in one call? **Report the failure mode, not just the happy path.**

**Q7 — Blast radius on the two live registers.** Would the candidate change the row output for any block already emitted? `bellows/knowledge/FORWARD.md` has 24 rows and `lessons-forge` has 1 — **neither may be rewritten by any downstream plan**; this asks only whether future behaviour diverges from past for identical input.

**Q8 — What does plan 62's test become?** `TestForwardSingleLineItem` asserts the current contract. Under a splitter it must be **amended, not deleted** — state exactly which assertions survive, which change, and what new coverage the negative control requires. ⚠️ **A downstream plan that deletes a guard's test rather than amending it is removing the guard.**

**Q9 — Daemon restart procedure.** Confirm from the runtime that a `bellows.py` edit requires a restart, and record the exact safe procedure — including how to verify no plan is mid-dispatch first. **This is what makes the downstream plan's shape different from a `plan_lint` change.**

**Q10 — Is the change worth making at all?** Weigh against the zero-risk alternative: keep one item per plan and let the next four plans each carry one. Give the CEO the cost of both, including the restart and the test amendment. **A defensible finding here is "no" — say so if the corpus supports it.**

## Method + boundaries

- **READ-ONLY.** Prototype in `/tmp` only. Do NOT edit `bellows.py`, any test, or either `FORWARD.md`. Do not restart the daemon.
- **Execute against the real corpus.** Every claim about what a candidate does must be backed by pasted output from running it on real blocks, not by reading the regex.
- ⚠️ **`grep` here is a ugrep shim: use `grep -F` for literals, and `--` before any pattern beginning with `-`** (a leading-dash pattern is parsed as an option, errors to stderr, and leaves stdout EMPTY — which reads as "found nothing" having measured nothing). The shell is zsh, where an unmatched glob aborts the command; use `find … -name '…'` rather than a glob.
- **Report per-block results, not aggregates.** "The candidate passes" is not a finding; a table of blocks with expected-vs-actual is.
- If a question cannot be answered from here, say so in `## Unresolved` rather than guessing.

## Required deposit structure — the answers are not the deliverable, the CONTRACT is

`knowledge/research/forward-register-item-delimiter-contract-2026-08-02.md`, containing:

1. **The Q1 corpus table** — every block found, its source plan, its item count, and what landed.
2. **The candidate rule stated precisely enough to implement**, with its per-block results on the whole corpus.
3. **Both control results, quoted** — plan 62's narration fixture collapsing to one row, and plan 288's six bullets yielding six.
4. **The idempotency and partial-write findings** from Q6.
5. **The test-amendment map** from Q8 — assertion by assertion.
6. **The restart procedure** from Q9.
7. **A recommendation on Q10 with its cost**, framed so the CEO can choose; and
8. **`## Unresolved`** — every question not settled from evidence, or the word NONE.

### Output Receipt

Close the deposit with `### Status` (**Complete**), `### Deposits`, and `### Ledger Updates` containing:

**`#### Forward Register` — EMIT EXACTLY ONE ITEM, ON ONE LINE.** ⚠️ **This is not incidental: it is the mechanism under investigation, used correctly while being investigated.** One item is the current contract's real capacity, and this diagnostic must not presume its own conclusion by emitting several. The item is:

`plan_lint section-4 zero-expectation-class check: a plan declaring no expected WARN/FAIL class is not flagged, so a deposited plan with no stated gate expectation passes section 4 silently.`

⚠️ **This diagnostic dispatches to bellows, so the row lands in `bellows/knowledge/FORWARD.md`** — the correct register for a `plan_lint` defect, since that is where the code lives. The `generate_lessons_report` encoding item belongs to lessons-forge's register and must NOT be emitted here. ⚠️ **Do NOT write to `FORWARD.md` yourself** — the daemon appends post-merge and skips its own write entirely if the file appears in `files_changed`, so an agent-written row destroys the append. ⚠️ **Do NOT claim to have observed the row landing:** the append happens after this step ends, and the observation belongs to the Planner at wrap.

Also include **`#### Prompt Feedback`**.

## Drafting Cycle

> **⚠️ THIS SECTION IS A RECORD, NOT INSTRUCTIONS.** Nothing below is addressed to any agent. Gate-matching strings are described, never quoted.

**Tier:** T1 — **firing trigger: T-4 (a change to a mechanism other plans depend on).** T-2 does not fire: this diagnostic mutates nothing. T-6 does not fire: no governance surface is touched. §1 requires the FIRING trigger be recorded, not merely the tier.
**Walks:** v0 → v1. Four lenses walked against the draft and culminated in one pass; ACID walked alone against the merged draft.
- Weak spots: w1 2 folded.
- Destruction: w1 2 folded.
- Vulnerabilities: w1 1 folded.
- Integration-record: w1 2 folded.
- ACID: w1 1 folded, then dry.

**Conflicts:** CL1 — the single-line reduction is a GUARD, not a defect; any candidate must preserve its effect on unstructured narration. CL2 — read-only is absolute: the two live registers and plan 62's test are evidence, not editable surface.
**Closing:** last event is a dry lens pass. The sharpest fold was Destruction's: an earlier draft asked "how should the splitter work," which presumes the answer to Q10 and would have licensed a downstream plan to remove plan 62's guard without ever pricing it. The questions were re-aimed at whether the split is possible and worth it, with the guard's own fixture promoted to a mandatory negative control.
