# Classification Rubric — lint-class-census-2026-08-10

Written BEFORE any match is seen (C.2 ordering). Every verdict in `final-state-matches.txt` names exactly one criterion below in its `rubric_ref` column.

---

## Criteria

**R1 — TRUE (live defect).** The match identifies a LIVE instance of the defect class in normative plan text. The defective construct (non-ASCII in -F pattern / metachar in -F pattern / piped grep -c / count-mismatch numeral) appears as a mandated instruction or standing assertion. The defect is active: it would cause the stated failure mode if executed or applied as written.

**R2 — FALSE (descriptive prose).** The match fires on text that DISCUSSES the defect without committing it. The construct appears in prose that describes, corrects, retracts, or documents the defect class. The text is about the defect, not an instance of it. Includes: correction notes ("changed X to Y"), lesson-learned prose, diagnostic findings, and documentation of the class itself.

**R3 — FALSE (quoted/exemplar).** The match fires on a quotation, worked example, citation, or capture-format specimen from another source. The construct is presented as an illustration or reference, not as the plan's own mandated text. Includes: pasted command output, format examples, and cross-plan quotations.

**R4 — AMBIGUOUS.** The match cannot be assigned to R1, R2, or R3 with reasonable confidence. Includes: constructs in context that could be read as either mandated or illustrative; text where the normative/descriptive boundary is unclear; edge cases where intent is not determinable from context. AMBIGUOUS counts AGAINST shipping per the diagnostic's standing rule.

**R5 — FALSE (s-class: numeral matches count).** Class `s` only. The numeral correctly matches the actual count of the enumeration it quantifies. The matcher fires because it detects a numeral-enumeration pattern, but the count is accurate. Not a defect.

**R6 — FALSE (s-class: non-enumerative numeral).** Class `s` only. The numeral is used in a non-enumerative context: a version number, a date component, a line number, a plan id, a measurement, or a quantity that is not counting items in a visible list. The matcher fires on the pattern but the numeral is not asserting a count.
