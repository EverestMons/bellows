# Dev Log — Deposit-Exists Prose-Path Canary (Step 1)

**Date:** 2026-04-28
**Plan:** executable-deposit-exists-prose-canary-2026-04-28
**Step:** 1 — Bellows Developer
**Starting SHA:** 75ac134

## Files Deposited

1. `bellows/knowledge/research/deposit-exists-prose-canary-findings-2026-04-28.md` — canary findings file (1032 bytes)
2. `bellows/knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md` — this dev log

## Verbatim Findings Content

```markdown
# Deposit-Exists Prose-Path Canary — Findings

**Date:** 2026-04-28 | **Plan:** executable-deposit-exists-prose-canary-2026-04-28 | **Bellows Generation:** post-2026-04-19 structural fix

This canary closes the BACKLOG.md item logged 2026-04-23: `deposit_exists false positive on prose-embedded directory paths`. The original failure observed Gate 5 flagging two prose-only directory references — `bellows/knowledge/decisions/` and `bellows/knowledge/decisions/Done/` — on a Rule 26-compliant plan whose real deposit was declared via a declaration block. This step's prose intentionally embeds those same two directory paths as distractors to reproduce the original failure conditions. The expected gate behavior is that `_extract_plan_required_deposits()` scopes extraction to the declaration block (per the 2026-04-19 fix) and ignores the prose-embedded directory paths entirely. If the `deposit_exists` gate passes without flagging these prose paths, the structural fix is confirmed live and the BACKLOG item is closeable.
```

## Post-Write Verification

- Findings file exists: **yes** (verified via ls -la, 1032 bytes, 2026-04-28)

## Anomalies

- None. Plan file was already claimed (in-progress prefix present) before Step 1 execution — consistent with prior observations (TOOL-001 pattern).

---

## Output Receipt

- **Status:** Complete
- **Deposits:** 2 files (findings + dev log)
- **Commit:** see below
