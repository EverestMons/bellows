verdict: stop

Planner verification (Rule 22(b)) — plan 499 (ingest heading-key normalization), Step 1. ⚠️ **ALL SEVEN GATES PASS, AND THE STEP IS STILL WRONG.** Stopping on a clean gate result, on measured evidence.

WHAT IS CORRECT: the helper exists (`src/lessons_forge.py:55`), is applied at all THREE sites (`:147` ingest lookup + canonical INSERT, `:381` title derivation, `:481` duplicate-check lookup), the marker regex strips `[status:]`/`[target:]` case-insensitively and leaves `[tag:]` intact, and the INSERT stores the canonical form. Behavioural spot-check passed: identity on an unmarked heading, annotated-and-unannotated produce the same key, tags preserved, markers removed.

⚠️ THE DEFECT — `_key_heading` COLLAPSES INTERNAL WHITESPACE, WHICH BREAKS MATCHING AGAINST EXISTING DATA:

    return re.sub(r'\s+', ' ', cleaned).strip()

**40 of the 370 stored `source_heading` values contain a run of more than one space** (the house heading style puts TWO spaces before the first `[tag: ...]`). The lookup now uses the collapsed form while the DB holds the original, so **those 40 rows MISS and are RE-INSERTED on every ingest** — a regression that fires on ordinary ingestion, with or without annotation, and is broader than the defect this plan set out to fix.

MEASURED, against a `cp` copy of the corpus (the live DB was verified byte-identical before and after by `shasum -a 256`):
- Controlled A/B — CONTROL (no annotation): `inserted=51`. TREATMENT (3 headings annotated): `inserted=51`. **Delta 0**, so the ANNOTATION path this plan targets is genuinely fixed.
- But the correct figure for both arms is **11**, not 51: of 324 file entries, 313 match a stored heading exactly, and the 11 non-matching are 4 entries appended during today's wrap plus the 7 un-ingested that diagnostic-498 already identified. The extra **40** are exactly the double-space rows.
⚠️ Note for the record: my first probe reported "51 inserted" and I nearly read it as a plain failure. It is not — it is 11 legitimate plus 40 regression, and only the controlled A/B separated the fix's effect from pre-existing drift. A single-arm probe here is uninterpretable.

THE CORRECTION, VERIFIED BEFORE PRESCRIBING IT — consume the whitespace PRECEDING a marker and `rstrip`, never collapse internal runs:

    _STATUS_TARGET_MARKER_RE = re.compile(r'\s*\[(?:status|target):[^\]]*\]', re.IGNORECASE)
    def _key_heading(heading: str) -> str:
        return _STATUS_TARGET_MARKER_RE.sub('', heading).rstrip()

Measured against all 370 stored headings: **0 change** (perfect identity), while an annotated heading still resolves to the same key as its unannotated form and internal double-spacing is preserved. This is the property the plan's own walk-0 pin 3 promised — "the normalizer is the identity function on today's data" — and which the shipped version silently broke.

Per the verdict grammar (continue/stop only; a redo is stop + corrected re-deposit under the stable slug), this is a STOP. Step 1's work is otherwise sound and is committed, so the corrective plan starts from committed HEAD and changes one function plus its tests — it does not redo the three call sites.

⚠️ The plan's own QA canary WOULD have caught this (`inserted == 0` and "row count UNCHANGED" both fail at 51). Stopping now rather than continuing spends one corrective dispatch instead of a full-suite QA run that rediscovers what is already proven.
