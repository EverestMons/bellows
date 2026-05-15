# Diagnostic — deposit_exists False Positive Root Cause Audit

**Project:** bellows
**Type:** Diagnostic
**Priority:** 10
**Author:** Planner
**Date:** 2026-05-11

## Context

BACKLOG item: `deposit_exists` gate trips with `fail` status on plans where the
declared deposit file genuinely exists on disk. Recurring pattern — Planner has
overridden via Rule 22 + continue verdict to `bellows/verdicts/resolved/`
multiple times. Root cause is unverified. Four candidate causes are on the
table; this diagnostic determines which (if any) is the real one.

**Candidate causes:**
1. **Path resolution mismatch** — gate's multi-strategy resolution (absolute,
   project-relative, parent-relative) fails to find the file at the path the
   agent actually wrote it to.
2. **Timing / fsync gap** — gate runs before the OS flushes the write.
3. **Parser-gap interaction with Rule 26** — `extract_primary_deposit()` reads
   the singular `**Deposit:**` form and misses the plural `**Deposits:**` list,
   so the gate scans prose and asserts existence of a path the agent didn't
   actually create (or vice versa).
4. **Path normalization / case sensitivity** — declared path and written path
   differ in case or normalization; `os.path.isfile()` resolves differently
   than the agent's write call.

The diagnostic is a **population audit**: enumerate all reproductions in
Bellows history, classify each by candidate cause, produce a count per
candidate, and recommend the fix shape that addresses the dominant cause.

## STEP 1 — Systems Analyst: deposit_exists false-positive root cause audit

You are the Systems Analyst. Investigate the `deposit_exists` gate (gate 5)
false-positive failure mode in Bellows. Do NOT propose or implement a fix.
Produce findings only.

**Scope:**

1. Enumerate every reproduction on disk. Search these locations for evidence
   of `deposit_exists` failures where the declared deposit file genuinely
   exists at audit time:
   - `bellows/verdicts/pending/` — any current pending verdict request
     showing `deposit_exists: fail` (or equivalent JSON/text representation).
   - `bellows/verdicts/resolved/` — any resolved verdict that was originally
     a gate-5 failure (look for resolved files whose corresponding plan still
     exists in `Done/` — i.e., the failure was overridden).
   - `bellows/Done/` — plan files whose lifecycle history includes a gate-5
     fail (check shadow cache or any audit log Bellows maintains).
   - Any Bellows daemon log file (`bellows/*.log`, `bellows/logs/`,
     `~/Library/Logs/bellows*`, or wherever the daemon writes logs — discover
     via `find` and `bellows/config.json`).

   For each reproduction, capture:
   - Plan slug and step number.
   - Declared deposit path (from `**Deposits:**` block in the plan).
   - Actual file path on disk (verify via `os.path.isfile` and `find`).
   - Timestamp of gate run vs. file mtime.
   - Whether the plan was Rule-26-compliant (plural `**Deposits:**`) or
     legacy (singular `**Deposit:**` or prose-only).

2. Read the gate-5 implementation in `bellows/gates.py` (function name likely
   `_gate_deposit_exists` or similar). Capture verbatim:
   - The path-resolution strategy list (absolute, project-relative,
     parent-relative — confirm the exact strategies).
   - The function used to assert existence (`os.path.isfile`, `os.path.exists`,
     `pathlib.Path.is_file`).
   - The source of the path list it checks (does it read the parsed
     `**Deposits:**` block, the `extract_primary_deposit()` output, or scan
     prose?).

3. Read `extract_primary_deposit()` in `bellows/verdict.py`. Capture the
   parsing logic — what forms does it recognize, what does it return for
   plural-list `**Deposits:**` declarations.

4. For each reproduction enumerated in (1), classify by candidate cause:
   - **Cause 1 (path resolution):** declared path doesn't resolve to the
     actual file via any of the gate's strategies. Verify by running each
     strategy manually against the reproduction's declared path.
   - **Cause 2 (timing):** declared path resolves correctly at audit time,
     file mtime is earlier than gate-run timestamp, but gate still failed.
     Indicates fsync race. Mark as "suspected — cannot verify retroactively"
     if mtime data isn't available.
   - **Cause 3 (parser gap):** plan uses plural `**Deposits:**`, gate scans
     prose and finds a non-deposit path (e.g., a reference path inside the
     prompt) that doesn't exist. Verify by running the current gate logic
     against the plan text and checking what paths it extracts.
   - **Cause 4 (normalization):** declared path and actual path differ in
     case, trailing slash, or unicode normalization. Verify by exact byte
     comparison.
   - **Cause 5 (other):** doesn't fit any candidate. Describe what you found.

5. Produce a classification table:

   | Plan slug | Step | Declared path | Cause | Evidence |
   |---|---|---|---|---|

6. Tally the causes. Identify the dominant one(s).

7. Recommend a fix shape for the dominant cause. Do NOT write code. The
   recommendation is a one-paragraph description of WHAT needs to change and
   WHERE (which file, which function), not how.

**Out of scope (do not do):**
- Do not modify any source file.
- Do not write tests.
- Do not propose multiple fixes for non-dominant causes — those become
  separate BACKLOG items if the dominant fix doesn't cover them.
- Do not investigate `scope_check` (gate 8), `receipt_status` (gate 1), or
  any other gate.

**Reporting requirements:**

Deposit your findings as a single markdown file. Structure:

1. **Summary** — one paragraph: how many reproductions found, dominant
   cause, recommended fix shape in one sentence.
2. **Method** — locations searched, search commands used, gate/parser code
   captured verbatim with file paths and line numbers.
3. **Reproductions** — the classification table from step (5).
4. **Per-cause analysis** — for each candidate cause that has at least one
   reproduction, explain the mechanism with reference to specific lines in
   `gates.py` / `verdict.py`.
5. **Recommended fix shape** — the one-paragraph recommendation from step
   (7). Include which file, which function, what the behavior change is.
6. **Open questions** — anything you couldn't verify (e.g., timing-related
   causes if mtime data isn't preserved).

**Deposits:**
- `bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md`
