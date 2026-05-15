# Dev Log — Rule 20 Single-Source Migration

**Plan:** executable-rule-20-single-source-2026-05-10
**Agent:** Bellows Developer
**Date:** 2026-05-10

---

## Edits Made

| # | File | Action | Summary |
|---|------|--------|---------|
| 1 | `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` | Created | Canonical single-source file for the Rule 20 self-check Python block. Contains the full block with four sentinel placeholders, banner string invariant documentation, and change-management instructions. |
| 2 | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` | Modified | Rule 20 rewritten: removed inline Python block, replaced with reference to canonical file + plan-side template. Version bumped 4.35 → 4.36. Lessons Learned entry added documenting the migration and ~30% banner drift rate. |
| 3 | `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md` | Modified | Added `## Rule 20 Self-Check (Canonical Block Reference)` section between Guardrails and Project Knowledge Base Index. Updated Role Summary to mention canonical source. |
| 4 | `/Users/marklehn/Desktop/GitHub/invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` | Modified | Added `## Rule 20 Self-Check (Canonical Block Reference)` section between Guardrails and Project Knowledge Base Index. Net-new Rule 20 reference (file had zero prior references). |

---

## LOC Delta

| File | Added | Removed | Net |
|------|-------|---------|-----|
| `RULE_20_SELF_CHECK_BLOCK.md` (governance root) | +122 | 0 | +122 |
| `PLANNER_TEMPLATE.md` (governance root) | +32 | -83 | -51 |
| **Governance root subtotal** | **+154** | **-83** | **+71** |
| `bellows/agents/BELLOWS_QA.md` | +18 | -1 | +17 |
| **Bellows subtotal** | **+18** | **-1** | **+17** |
| `invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md` | +16 | 0 | +16 |
| **Invoice-pulse subtotal** | **+16** | **0** | **+16** |
| **Total** | **+188** | **-84** | **+104** |

---

## Test Suite Result

```
1 failed, 246 passed, 1 warning in 5.91s
```

- Pre-existing failure: `test_run_step_timeout` (unchanged)
- New failures: 0
- Identical to pre-edit baseline.

---

## Commit SHAs

| Repo | SHA | Message |
|------|-----|---------|
| Governance root | `a109e47` | `feat(governance): Rule 20 single-source canonical block — v4.35 → v4.36` |
| Bellows | `5a5ae90` | `docs(qa): reference canonical Rule 20 block in BELLOWS_QA.md` |
| Invoice-pulse | `02702201` | `docs(qa): reference canonical Rule 20 block in INVOICE_SECURITY_TESTING_ANALYST.md` |

---

## Banner Invariant Verification

```
$ cat RULE_20_SELF_CHECK_BLOCK.md | grep "Rule 20 — QA Self-Check Results"
print("Rule 20 — QA Self-Check Results")
```

Canonical banner `Rule 20 — QA Self-Check Results` (em-dash U+2014) is present in the canonical file. Byte-invariant survived the migration.
