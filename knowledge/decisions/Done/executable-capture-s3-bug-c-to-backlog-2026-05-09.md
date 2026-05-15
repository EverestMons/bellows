# Executable — Capture S3 Bug C to BACKLOG

**Created:** 2026-05-09
**Author:** Planner
**Project:** bellows
**Type:** executable
**auto_close:** false
**Total Steps:** 1

---

## Context

Today's S3 fix (commits `dc0bdd7` + `5136326`) closed Bug A (bare-format `check_verdict` regex) and Bug B (`verdict-request-` prefix exclusion). Live canary at the post-fix Bellows restart auto-processed 13 of 14 bare-format stranded files via the stale-verdict Done/ check — confirming the fix works.

One stranded file remained after the cascade: `verdict-executable-parallel-plan-scope-check-collision-fix-2026-05-01-step-2.md`. Its plan, `executable-parallel-plan-scope-check-collision-fix-2026-05-01.md`, was halted via `verdict: stop` and currently sits at `bellows/knowledge/decisions/halted-executable-parallel-plan-scope-check-collision-fix-2026-05-01.md`. The stale-verdict check at `bellows.py:1004-1021` searches `knowledge/decisions/Done/` for a matching plan filename but does NOT search for `halted-*` prefixed plans in `knowledge/decisions/`. Result: the resolved verdict file loops every ~30 seconds on `no verdict-pending plan found for ... — leaving in resolved/ for retry`.

This is structurally a third sub-bug of S3 — same retry-loop symptom, different root cause from Bugs A and B. Capturing to BACKLOG so a future session can fix it cleanly. No fix in this plan; entry only.

## STEP 1 — Bellows Documentation Analyst: append BACKLOG entry for Bug C

You are the Bellows Documentation Analyst. Append one BACKLOG entry capturing S3 Bug C. Do not modify any other file.

**Read first (required):**
- `bellows/knowledge/BACKLOG.md` — locate the existing format, find the next available entry number, and confirm placement convention (top of open items list vs. end). Match the established style exactly.

**Read for context (optional):**
- `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md` — the diagnostic that identified Bugs A and B; Bug C surfaced post-fix-canary and is not in this findings file.

### Task — append entry

Append one new BACKLOG entry with the following content. Use the next available entry number and match the formatting conventions of existing entries (header level, field labels, ordering). Do NOT renumber or modify any existing entry.

**Entry content (paraphrase to match BACKLOG.md's existing prose style; do not copy verbatim if the file uses a different field structure):**

- **Title:** S3 Bug C — Stale-verdict check does not search `halted-*` plans
- **Symptom:** A resolved verdict file in `bellows/verdicts/resolved/` whose plan was halted (filename prefix `halted-executable-*` or `halted-diagnostic-*`) generates a retry-loop log every ~30 seconds: `no verdict-pending plan found for {slug} step {N} — leaving in resolved/ for retry`. The file never escalates to `processed-*`.
- **Root cause:** `bellows.py:1004-1021` (the stale-verdict Done/ check) searches `knowledge/decisions/Done/` for a plan filename containing the slug. It does not search for `halted-*` prefixed plans that remained in `knowledge/decisions/` after a halt verdict. The check falls through and the file is left in `resolved/`.
- **Reproduction:** Confirmed live on 2026-05-09 after the S3 Bug A/B fix shipped. Affected file: `verdict-executable-parallel-plan-scope-check-collision-fix-2026-05-01-step-2.md` (bare-format `stop` verdict). Affected plan: `bellows/knowledge/decisions/halted-executable-parallel-plan-scope-check-collision-fix-2026-05-01.md`.
- **Recommended fix shape:** ~3 LOC extension to the stale-check loop in `bellows.py:1004-1021` to also glob `halted-*` patterns in `knowledge/decisions/`, mirroring the existing Done/ search logic. Add one regression test asserting that a resolved verdict whose plan is `halted-*` gets renamed to `processed-*` on the next scan.
- **Severity / priority:** Low. Single known reproduction. Symptom is log noise only — no functional impact, no lifecycle corruption. Can be batched with future Bellows reliability work.
- **Related:** S3 Bug A (closed today, commit `dc0bdd7`), S3 Bug B (closed today, same commit). Diagnostic findings: `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md`. This entry was identified post-canary and is NOT covered by that diagnostic.

### Constraints

- Do NOT modify any existing BACKLOG entry.
- Do NOT modify any code file, test file, or plan file.
- Do NOT update PROJECT_STATUS.md or KNOWLEDGE_INDEX.md (out of scope; those happen at session wrap).
- Do NOT append a feedback entry to `agent-prompt-feedback.md` for this plan — the task is too mechanical to yield useful feedback. (Intentional omission.)

### Output Receipt

- Status: Complete / Partial / Blocked
- File modified: `bellows/knowledge/BACKLOG.md`
- Entry number assigned (cite explicitly)
- Quote the first 3 lines of the new entry verbatim from the file (post-write) so the Planner can verify formatting on Rule 22 read.
- CEO Flags: any deviation from the prescribed content, any conflict with an existing entry, any field the existing BACKLOG format requires that this prompt did not specify.

**Deposits:**
- `bellows/knowledge/BACKLOG.md`

---

## Bootstrap prompt for CEO

```
RUN EXE bellows
```
