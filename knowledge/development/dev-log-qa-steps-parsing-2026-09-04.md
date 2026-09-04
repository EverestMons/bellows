# Dev-log: QA-steps Parse Divergence Census

**Date:** 2026-09-04
**Plan:** diagnostic-100036 (STEP 1)

---

## Three published positions on `qa_steps: [2]` — all wrong, and how

Three separate claims were made about how `plan_lint._parse_qa_steps` and `gates._gate_is_qa_step` handle the bracket spelling `[2]`:

| Position | Source | Status |
|---|---|---|
| "`plan_lint` can't parse `[2]`, `gates` can" | thread 102 | Wrong on both halves |
| "`plan_lint` DOES parse `[2]`, `gates` does NOT" | plan `u-qa-predicate-align` | Substantially right — marked false in error |
| "Neither parser handles `[2]`; `gates` falls back to keyword" | thread 116 | Wrong about `plan_lint`; right about `gates` |

All three positions were wrong because each relied on a hand-probe that introduced a confound.

## The confound that produced two wrong positions

`_parse_qa_steps` has this signature:

```python
def _parse_qa_steps(qa_steps_raw):
```

It takes a **header value** — the string extracted from the plan header.

The two probes that declared "`plan_lint` can't parse `[2]`" passed an **entire plan document** to this function. The function's `try` block runs `str(raw).strip().strip("[]")` and then `int()` over each token; a full document text causes `int()` to raise, the bare `except` swallows the exception, and the function returns `set()`. That reads as "does not parse" — which is wrong. The function is completely correct on its actual input. A one-line positive control — `_parse_qa_steps('2') → {2}` — would have exposed this: if the correct input works, the failure is the call site, not the function.

## What the instrument actually confirms

`_parse_qa_steps` (plan_lint.py:31–39) does:

```python
s = str(qa_steps_raw).strip().strip("[]")
return {int(tok.strip()) for tok in s.split(",") if tok.strip()}
```

`strip("[]")` removes brackets before splitting. `_parse_qa_steps('[2]')` → `{2}`. Correct on every corpus spelling.

`_gate_is_qa_step` (gates.py:848) does:

```python
qa_step_numbers = [int(s.strip()) for s in str(qa_steps_raw).split(",") if s.strip()]
```

No bracket strip. `str('[2]').split(',')` = `['[2]']`. `int('[2]')` raises. Falls back to keyword detection.

The divergence is one missing `.strip("[]")` call.

## The fallback: correct by coincidence, not by mechanism

All 3 corpus plans with `qa_steps: [2]` (executable-312, executable-313, executable-324) have `## STEP 2 — QA` headings. The keyword fallback finds "qa" in the heading and returns True. Oracle (`_parse_qa_steps`) also returns True. The gate appears to work.

Rename any of those headings to `## STEP 2 — Beta` and the gate silently stops firing. That is the defect: correctness guaranteed by heading text, not by the declaration.

The neutralised-heading test (replacing "qa" in step headings before calling the fallback) isolates the mechanism: 3 disagreements when neutralised, 0 when left as-is. This is the production reliability gap.

## Why the fallback must not be deleted without caution

169 plan+step combinations in the Done/ corpus rely on the keyword fallback as their sole QA detector — plans authored before the `qa_steps` field was introduced (pre–2026-05-25). Removing the fallback suppresses QA enforcement on all of them. Blast radius (b) = 168 actual outcome changes (1 of the 169 Q4 items is not a real outcome change because its plan has a parseable qa_steps for a different step). Thread 118's warning against deleting the arm was correct.

## Output Receipt

**Status:** Complete

**Files written:**
- `tools/qa_steps_parse_census.py` — census instrument, imports both parsers, calls them without re-implementing either
- `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/qa-steps-parsing-2026-09-04.md` — research note with Q1–Q7 answers
- `knowledge/development/dev-log-qa-steps-parsing-2026-09-04.md` — this file
