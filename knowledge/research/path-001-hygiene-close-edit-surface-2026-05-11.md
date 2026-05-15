# PATH-001 Hygiene-Close Edit Surface Audit

**Source file:** `bellows/knowledge/research/agent-prompt-feedback.md`
**Audit date:** 2026-05-11
**Scope:** Read-only — capture byte-level structure for deterministic edit anchors.

---

## Question 1 — Section header

The PATH-001 section header is at **line 399**:

```
## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)
```

The line immediately above it is **line 398**, which is a blank line (empty).

The line above that is **line 397**:

```
---
```

This is the horizontal-rule separator closing the preceding section.

---

## Question 2 — Status marker format

The status marker is at **line 401**:

```
**Status:** OPEN. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
```

**Format:** Bold field name `**Status:**` followed by a space, then the status token `OPEN`, then a period, then additional provenance text. The marker is on its own line. It follows the `**FieldName:** VALUE` pattern used throughout the file.

**Character immediately preceding:** The line before (line 400) is a blank line. So the preceding character is a newline.

**Character immediately following:** The line after (line 402) is a blank line. So the following character is a newline.

---

## Question 3 — Line immediately after the status marker

The line immediately after the status marker is **line 402**, which is a blank line (empty).

The next non-blank line is **line 403**:

```
**Pattern:** Plans use `bellows/knowledge/...` paths in agent instructions, claim shutil.move calls, grep commands, and Rule 20 self-check evidence directories. These paths assume cwd is the governance-root (`/Users/marklehn/Desktop/GitHub/`). But agents executing inside Bellows worktree dispatches have cwd = `bellows/` (or, post-monorepo-fix, the `bellows/` project directory itself). The `bellows/` prefix produces double-prefix paths like `bellows/bellows/knowledge/...` that don't exist. Agents typically work around this via cd or absolute-path conversion, but the friction is real and recurring.
```

---

## Question 4 — Other status-like markers in the file

### `grep -n -i "status"` results

| Line | Content (truncated) | Is PATH-001 status? |
|------|----------------------|---------------------|
| 133 | `- The deliverable verification table format (Deliverable / Expected / Status / Evidence)...` | No — prose about table format |
| 296 | `...table columns: Check, Expected, Actual, Status, Evidence...` | No — prose about table format |
| 329 | `...scanned the QA report for hedging keywords in positive-status rows...` | No — prose about QA checks |
| 330 | `...Receipt status check before proceeding...` | No — prose about gating |
| 331 | `...PROJECT_STATUS.md entry text was pre-written...` | No — prose about project status file |
| 336 | `...PROJECT_STATUS.md update...` | No — prose |
| 337 | (long line, omitted) | No — prose |
| 368 | `...Receipt status check before proceeding...` | No — prose |
| 382 | `**Status:** CLOSED 2026-05-03.` | No — different section (preceding section, already CLOSED) |
| **401** | `**Status:** OPEN. First identified pre-2026-05-04...` | **Yes — PATH-001** |
| 417 | `**Status:** OPEN. Identified 2026-05-04, observed in 2 of 6...` | No — SPEC-001 section |
| 433 | `**Status:** OPEN. Identified 2026-05-04 from diagnostic-monorepo...` | No — another section |
| 449 | `**Status:** OPEN. Identified 2026-05-04, reinforced across...` | No — another section |
| 465 | `**Status:** OPEN. Identified 2026-05-04, reinforced ~10 times...` | No — another section |
| 482 | `**Status:** OPEN. Identified 2026-05-05 from diagnostic-deposit-parser...` | No — another section |
| 513, 530, 562, 604, 655, 661, 692, 694, 699, 733, 739, 810, 816, 831, 850, 857, 930, 932, 937, 976, 1084, 1089 | Various prose lines referencing `PROJECT_STATUS.md`, `status check`, `positive-status rows` | No — all prose |

### `grep -n "OPEN"` results

| Line | Content (truncated) | Is PATH-001 status? |
|------|----------------------|---------------------|
| **401** | `**Status:** OPEN. First identified pre-2026-05-04...` | **Yes — PATH-001** |
| 417 | `**Status:** OPEN. Identified 2026-05-04...` | No — SPEC-001 |
| 433 | `**Status:** OPEN. Identified 2026-05-04...` | No — other section |
| 449 | `**Status:** OPEN. Identified 2026-05-04...` | No — other section |
| 465 | `**Status:** OPEN. Identified 2026-05-04...` | No — other section |
| 482 | `**Status:** OPEN. Identified 2026-05-05...` | No — other section |

**Key finding:** `**Status:** OPEN` appears 6 times in the file. The substring is NOT unique. Any edit anchor targeting the PATH-001 status line must include additional context (e.g., the section header on line 399) to be unambiguous.

---

## Question 5 — End of the PATH-001 section

The last content line of the PATH-001 section is **line 411**:

```
**Reference:** Originally captured pre-2026-05-04. Reinforced by 2026-05-04 feedback entries from four plans across one session.
```

Line 412 is a blank line. Line 413 is the `---` separator. Line 415 begins the next section (`## SPEC-001: ...`).

The PATH-001 section spans lines 399–413 (inclusive of the trailing separator) or lines 399–411 (content only).

---

## Question 6 — File total line count

**1157 lines.**

---

## Question 7 — Recommended anchor strings

### Uniqueness strategy

Since `**Status:** OPEN` appears 6 times, both anchors include the unique section header (`## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)`) as context to guarantee unambiguous matching.

### Anchor A — Status change (OPEN to CLOSED)

**Apply first.** Changes the status token from `OPEN` to `CLOSED 2026-05-11`.

**old_string:**
```
## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)

**Status:** OPEN. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
```

**new_string:**
```
## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)

**Status:** CLOSED 2026-05-11. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
```

### Anchor B — Closure line insertion

**Apply second (after Anchor A).** Inserts a closure-reference line immediately below the status marker, before the blank line that precedes `**Pattern:**`.

**old_string:**
```
**Status:** CLOSED 2026-05-11. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).

**Pattern:** Plans use `bellows/knowledge/...` paths in agent instructions,
```

**new_string:**
```
**Status:** CLOSED 2026-05-11. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
**Closure:** Addressed by 2026-05-10 migration commits. PATH-001 conventions now codified in Planner template rules.

**Pattern:** Plans use `bellows/knowledge/...` paths in agent instructions,
```

### Application notes

- Anchors must be applied in order: A then B. Anchor B's `old_string` depends on Anchor A's output.
- Anchor A's `old_string` is unique because `## PATH-001:` appears exactly once in the file.
- Anchor B's `old_string` is unique because `CLOSED 2026-05-11` will exist only once after Anchor A is applied.
- The executable may adjust the `**Closure:**` line text to reference specific commit SHAs or plan identifiers as needed. The anchor structure remains valid regardless of the closure line's content.

---

## Output Receipt
**Agent:** Bellows Documentation Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Read-only audit of `bellows/knowledge/research/agent-prompt-feedback.md` to capture the exact edit surface of the PATH-001 section (lines 399–413). Answered all 7 diagnostic questions with verbatim quotes, line numbers, and uniqueness analysis. Proposed two sequential edit anchors (status change + closure line insertion) with deterministic `old_string`/`new_string` pairs.

### Files Deposited
- `bellows/knowledge/research/path-001-hygiene-close-edit-surface-2026-05-11.md` — edit surface audit findings with ready-to-use anchor strings

### Files Created or Modified (Code)
- None (read-only audit)

### Decisions Made
- Anchor strategy uses section header (`## PATH-001:`) as uniqueness context because `**Status:** OPEN` appears 6 times in the file
- Anchors designed for sequential application (A then B) rather than single monolithic edit, matching the two discrete changes described in the diagnostic context

### Flags for CEO
- None

### Flags for Next Step
- The `**Closure:**` line text in Anchor B is a proposed default. The executable should substitute the actual closure rationale and commit references as determined by the Planner.
