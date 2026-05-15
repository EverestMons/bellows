# `_gate_rule_20_self_check` False-Positive Root Cause Audit

**Date:** 2026-05-11 | **Plan:** diagnostic-rule-20-gate-false-positive-root-cause-2026-05-11 | **Step:** 1

---

## Q0 — Has Any Fix Shipped Since 2026-05-05?

```
$ git --no-pager log --since=2026-05-05 --oneline -- bellows.py gates.py verdict.py parser.py
4d57fd3 fix(parsers): strip fenced code blocks before parsing plan_text — 4 parsers
1c6c5b2 fix(parser): multi-line bold header support + defensive default + warning extension
dc1acd4 refactor: extract _perform_startup_sweep from Bellows.start()
db78919 fix(verdicts): stale-verdict check recognizes halted-* plans (BACKLOG S3 Bug C)
8eac4c3 fix(teardown): detect stale index.lock + force-remove orphaned worktree dirs
be8cba4 fix(gates): thread wt_path into _gate_rule_20_self_check (BACKLOG 2026-05-07)
dc0bdd7 fix(s3): format-tolerant check_verdict + verdict-request- prefix exclusion
ab353a7 feat: extend _parse_plan_header() to parse pipe-separated bold-Markdown headers
afc8523 feat: PLANNER_TEMPLATE pause_for_verdict header + Bellows warning
e5188fa feat: dispatch qa- prefix plans and log silent skips
2016d02 fix: thread wt_path to deposit_exists gate (BACKLOG #1)
1256879 feat: Failure 3 Mode A closure — system prompt + lifecycle guard
c9af860 feat: rule 20 self-check verification gate (gates.py + tests)
d3cf90b fix(gates): regex-extract path from agent receipt — closes deposit-parser backtick-prose false positive
```

Two commits touch `_gate_rule_20_self_check` or its support path:

| Commit | What it touches | Would it prevent 2026-05-11 FP? |
|---|---|---|
| `be8cba4` | Threads `wt_path` into `_gate_rule_20_self_check` and its `_resolve_deposit_path` call | **No.** bellows-self plans don't use worktrees — `wt_path` equals `project_path`, Strategy 0 is a no-op. |
| `4d57fd3` | Adds `strip_fenced_code_blocks()` to `_extract_step_text` entry | **No.** The inline `## STEP 2` references are in single-backtick inline code, not triple-backtick fenced blocks. `strip_fenced_code_blocks` does not affect them. |

**No shipped fix prevents the 2026-05-11 false positive. Proceeding to Q1.**

---

## Q1 — `_gate_rule_20_self_check` Source and Data Flow

**Source:** `gates.py:301-348`

```python
def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
    """Verify QA-deposited reports contain a Rule 20 self-check banner with PASSED status."""
    if not is_qa_step:
        return

    step_text = _extract_step_text(plan_text, step_number)
    if not step_text:
        return

    deposit_paths = _extract_plan_required_deposits(step_text)
    md_paths = [p for p in deposit_paths if p.endswith(".md")]
    if not md_paths:
        failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
        return

    banner = "Rule 20 — QA Self-Check Results"
    banner_found_path = None

    for dep_path in md_paths:
        resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
        if resolved is None:
            failures.append(...)
            continue
        content = ... # read file
        if banner not in content:
            continue
        # check for PASSED line
        ...
        return  # Gate passes

    if banner_found_path:
        failures.append(... "banner present but PASSED line missing" ...)
    else:
        if not any(f.get("gate") == "rule_20_self_check" for f in failures):
            failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
```

### Data Flow

| Stage | Function | Input | Output |
|---|---|---|---|
| 1. QA detection | `_gate_is_qa_step(plan_text, step_number)` at `gates.py:351-357` | Full plan text + step number | `bool` — checked via `"qa" in header_line.lower()` |
| 2. Step text extraction | `_extract_step_text(plan_text, step_number)` at `gates.py:253-262` | Full plan text + step number | Step text bounded by `## STEP N` headers |
| 3. Deposit enumeration | `_extract_plan_required_deposits(step_text)` at `gates.py:265-298` | Step text from stage 2 | Set of file paths from `**Deposits:**` block or legacy prose |
| 4. Filter to .md | List comprehension at `gates.py:311` | Deposit paths from stage 3 | `.md`-only paths |
| 5. Banner scan | File read + `banner not in content` at `gates.py:332` | Resolved file paths | Pass/fail |

**(a) Context fields used:** `plan_text` (full plan markdown), `step_number` (integer), `project_path`, `wt_path` (optional).

**(b) Deposit enumeration method:** The gate calls `_extract_plan_required_deposits(step_text)` which first searches for a `**Deposits:**` block (Rule 26 convention) via regex `[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)`. If found, extracts backtick-quoted paths from bullet list. Falls back to legacy prose patterns if no block found. The gate does NOT use the verdict request's singular `Deposit:` field — it re-parses the plan text independently.

**(c) Zero-files behavior:** When `md_paths` is empty (no `.md` deposits found), the gate immediately appends failure with evidence `"no QA deposit contains Rule 20 self-check banner"` and returns.

---

## Q2 — Filesystem State Confirmation

### Three-file verification

| File | Path | Exists | Key content |
|---|---|---|---|
| QA report | `knowledge/qa/fence-strip-plan-text-parsers-qa-2026-05-11.md` | **Yes** | Line 74: `Rule 20 — QA Self-Check Results` + Line 76: `PASSED — SELF-CHECK PASSED` |
| DEV log | `knowledge/development/fence-strip-plan-text-parsers-2026-05-11.md` | **Yes** | Development log, Step 1 deposit. No Rule 20 banner (not expected). |
| Verdict request | `verdicts/pending/verdict-request-fence-strip-plan-text-parsers-2026-05-11-step-2.md` | **Yes** | Line 10: `Deposit: bellows/knowledge/development/fence-strip-plan-text-parsers-2026-05-11.md` (points to DEV log, NOT QA report). Line 16: `rule_20_self_check: no QA deposit contains Rule 20 self-check banner` |

### Classification

The gate reads the **wrong file**. The QA report exists and contains the canonical banner with PASSED status, but the gate never inspects it. The verdict request's `Deposit:` field confirms the wrong file was selected: it shows the Step 1 DEV log path, not the Step 2 QA report path.

**Classification: deposit-enumeration bug — the gate's deposit enumeration extracts deposits from the wrong step's text, not from the actual Step 2.**

---

## Q3 — Singular-vs-Plural Deposit Parsing Trace

### `extract_primary_deposit` source

**Location:** `verdict.py:45-73`

```python
def extract_primary_deposit(step_text: str) -> Optional[str]:
    block_match = DEPOSITS_BLOCK_RE.search(step_text)   # Recognizes **Deposits:** (plural)
    if block_match:
        for m in BLOCK_BULLET_RE.finditer(block_match.group(1)):
            path = m.group(1)
            if path.endswith('.md'):
                return path
        return None
    # Legacy fallback regexes...
```

`extract_primary_deposit` DOES recognize the plural `**Deposits:**` block — the Q3 hypothesis from the diagnostic brief is **overturned**. The parser gap is NOT in `extract_primary_deposit`.

### Plan Step 2 `**Deposits:**` block

From `knowledge/decisions/Done/executable-fence-strip-plan-text-parsers-2026-05-11.md`, Step 2 (lines 33-35):

```
> **Deposits:**
> - `bellows/knowledge/qa/fence-strip-plan-text-parsers-qa-2026-05-11.md`
> - `bellows/knowledge/qa/evidence/executable-fence-strip-plan-text-parsers-2026-05-11/`
```

Step 1 (lines 20-23):
```
> **Deposits:**
> - `bellows/knowledge/development/fence-strip-plan-text-parsers-2026-05-11.md`
> - `bellows/knowledge/qa/evidence/executable-fence-strip-plan-text-parsers-2026-05-11/`
```

### Actual gap: `_extract_step_text` returns wrong step text

The true data flow gap is upstream of the deposit parser:

1. `_extract_step_text(plan_text, 2)` uses regex `## STEP 2\b.*?(?=\n## STEP |\Z)` with `re.DOTALL`.
2. The regex is NOT anchored to line-start (`^`). `re.search` finds the **first** occurrence of `## STEP 2` anywhere in the text.
3. Step 1's body contains inline code references: `` `## STEP 2` `` — mentioning test fixtures that use step headers as examples.
4. The regex matches the **inline reference** at char 5966 (inside Step 1's body) instead of the **real header** at char 8285.
5. The extracted "step text" is a portion of Step 1's body — from the inline `## STEP 2` reference to `\n## STEP 2` (the real header).
6. This wrong text contains Step 1's `**Deposits:**` block, so `_extract_plan_required_deposits` returns Step 1's deposits.
7. The gate checks Step 1's DEV log for the Rule 20 banner. Not found → false positive.

### REPL confirmation

```python
>>> import re
>>> with open('knowledge/decisions/Done/executable-fence-strip-plan-text-parsers-2026-05-11.md') as f:
...     plan_text = f.read()
>>> pattern = r'## STEP 2\b.*?(?=\n## STEP |\Z)'
>>> match = re.search(pattern, plan_text, re.DOTALL)
>>> match.start()
5966       # <-- inside Step 1 body (inline code reference)
>>> match.group(0)[:80]
'## STEP 2` before real `## STEP 2`, assert returns the REAL step body not the f'
```

```python
>>> # With line-start anchor — correct result
>>> pattern2 = r'^## STEP 2\b.*?(?=\n^## STEP |\Z)'
>>> match2 = re.search(pattern2, plan_text, re.DOTALL | re.MULTILINE)
>>> match2.start()
8285       # <-- real Step 2 header
>>> match2.group(0)[:80]
'## STEP 2 — Bellows QA\n\n---\n\n> **Before starting, read `bellows/knowledge/devel'
```

### Downstream impact on both gate and verdict request

The same root cause affected both paths:

| Consumer | Function | Input | Result |
|---|---|---|---|
| Gate (gates.py) | `_gate_rule_20_self_check` → `_extract_step_text` → `_extract_plan_required_deposits` | Wrong step text (Step 1 portion) → Step 1 deposits | Gate checks DEV log for banner → false positive |
| Verdict (verdict.py) | `post_verdict_request` → `_extract_step_text_from_plan` → `extract_primary_deposit` | Wrong step text (Step 1 portion) → Step 1 deposit | Verdict request `Deposit:` shows DEV log path |

---

## Q4 — Population Audit of Rule 20 Gate Failures

**Audit window:** 2026-05-05 (gate ship date) through 2026-05-11.

**Sources searched:** `verdicts/pending/`, `verdicts/pending/archived/`, `verdicts/resolved/` — all files matching `rule_20_self_check`.

### Gate failure inventory

| # | Verdict file | Plan slug | Step | Failure evidence | QA report path | Banner present? | Classification |
|---|---|---|---|---|---|---|---|
| 1 | `processed-verdict-backlog-hygiene-edits-2026-05-06-step-2` | backlog-hygiene-edits | 2 | Gate failure (CEO: "BACKLOG #1 race") | `invoice-pulse/knowledge/qa/backlog-hygiene-edits-qa-2026-05-06.md` | Yes (per CEO Rule 22 verification) | **FALSE POSITIVE** (Class 1: worktree path) |
| 2 | `processed-verdict-qa-report-rule-20-banner-fix-2026-05-07-step-2` | qa-report-rule-20-banner-fix | 2 | Gate failure (CEO: "path-resolution false positive") | `invoice-pulse/knowledge/qa/qa-action-queue-aggregation-2026-05-07.md` (target file) | Yes — line 77 `## Rule 20 — QA Self-Check Results`, line 112 `PASSED` (per CEO) | **FALSE POSITIVE** (Class 1: worktree path) |
| 3 | `processed-verdict-aggregated-queue-customer-display-2026-05-07-step-2` | aggregated-queue-customer-display | 2 | "no QA deposit contains Rule 20 self-check banner" | `invoice-pulse/knowledge/qa/qa-aggregated-queue-customer-display-2026-05-07.md` | Yes (per CEO Rule 22: both canonical banner + PASSED present) | **FALSE POSITIVE** (Class 1: worktree path) |
| 4 | `verdict-request-action-queue-aggregation-2026-05-07-step-3` | action-queue-aggregation | 3 | "deposit file unreadable" × 2 (file not found) | `invoice-pulse/knowledge/qa/qa-action-queue-aggregation-2026-05-07.md` | Yes (per CEO verdict on plan) | **FALSE POSITIVE** (Class 1: worktree path) |
| 5 | `verdict-request-bellows-qa-prefix-and-skip-logging-2026-05-08-step-2` | bellows-qa-prefix-and-skip-logging | 2 | "no QA deposit contains Rule 20 self-check banner" | `bellows/knowledge/qa/qa-bellows-qa-prefix-and-skip-logging-2026-05-08.md` | No — has `Rule 20 Self-Check — QA Report Hedging Scan` (non-canonical) | **TRUE POSITIVE** |
| 6 | `verdict-request-action-queue-limit-and-contract-name-2026-05-08-step-2` | action-queue-limit-and-contract-name | 2 | "deposit file unreadable" × 2 (file not found) | `invoice-pulse/knowledge/qa/qa-action-queue-limit-and-contract-name-2026-05-08.md` | Unverifiable (different project, files at worktree path) | **FALSE POSITIVE** (Class 1: worktree path) |
| 7 | `processed-verdict-startup-sweep-extract-2026-05-10-step-2` | startup-sweep-extract | 2 | Banner mismatch (CEO: "Planner authoring error — substituted non-canonical banner") | `bellows/knowledge/qa/startup-sweep-extract-qa-2026-05-10.md` | No — Planner substituted "RULE 20 SELF-CHECK" for canonical | **TRUE POSITIVE** |
| 8 | `processed-verdict-teardown-worktree-lock-cleanup-2026-05-10-step-2` | teardown-worktree-lock-cleanup | 2 | Banner mismatch (CEO: "Planner-side prompt-authoring discipline failure") | `bellows/knowledge/qa/teardown-worktree-lock-cleanup-qa-2026-05-10.md` | No — Planner substituted non-canonical block | **TRUE POSITIVE** |
| 9 | `verdict-request-fence-strip-plan-text-parsers-2026-05-11-step-2` | fence-strip-plan-text-parsers | 2 | "no QA deposit contains Rule 20 self-check banner" | `bellows/knowledge/qa/fence-strip-plan-text-parsers-qa-2026-05-11.md` | **Yes** — line 74 canonical banner + line 76 PASSED | **FALSE POSITIVE** (Class 2: step text extraction) |

### Summary

| Classification | Count | Root cause class |
|---|---|---|
| TRUE POSITIVE | 3 | Genuine banner missing or non-canonical (#5, #7, #8) |
| FALSE POSITIVE — Class 1 (worktree path) | 5 | Gate resolved deposit path against torn-down worktree (#1-4, #6). Fixed by commits `2016d02` + `be8cba4`. |
| FALSE POSITIVE — Class 2 (step text extraction) | 1 | `_extract_step_text` matched inline `## STEP N` reference before real header (#9). **Unfixed.** |

**False-positive count for the step-text-extraction class: 1 (this session only).** However, the trigger condition (plan prose containing inline `## STEP N` references) has occurred in at least 2 plans — the BACKLOG 2026-05-10 entry documents `extract_total_steps` over-counting from the same class of inline reference in `executable-header-parser-multiline-fix-2026-05-10`. That plan was a 2-step plan with no QA step, so `_gate_rule_20_self_check` wasn't triggered — but the same `_extract_step_text` regex would have returned wrong text if it had been.

---

## Q5 — Root Cause Classification and Fix Shape

### Root cause class

**(d) `_extract_step_text` parser gap — no line-start anchor on `## STEP N` pattern.**

The `## STEP {step_number}\b` regex at `gates.py:260` and `verdict.py:40` is not anchored to line-start. `re.search` finds the first occurrence of the pattern anywhere in the plan text, including inside inline code, prose descriptions, and test fixture examples. When a plan's earlier step body contains inline `## STEP N` references (common in plans that describe test fixtures or parser behavior), the regex matches the inline reference instead of the real structural header.

This is the same parser-vs-structure confusion class as the BACKLOG 2026-05-10 `extract_total_steps` over-count — but `extract_total_steps` (`bellows.py:109`) already uses `^` + `re.MULTILINE` to anchor to line-start, while `_extract_step_text` and `_gate_is_qa_step` do not.

### Affected functions

| Function | File:Lines | Pattern | Anchored? |
|---|---|---|---|
| `extract_total_steps` | `bellows.py:109` | `r"^## STEP\s+\d+"` with `re.MULTILINE` | **Yes** (already fixed by prior design) |
| `_extract_step_text` | `gates.py:259-261` | `r"## STEP {step_number}\b.*?(?=\n## STEP \|\Z)"` with `re.DOTALL` | **No** |
| `_extract_step_text_from_plan` | `verdict.py:39-41` | Same pattern (documented duplicate) | **No** |
| `_gate_is_qa_step` | `gates.py:352-356` | `r"## STEP {step_number}\b[^\n]*"` | **No** |

### `_gate_is_qa_step` is also vulnerable

REPL confirmation:

```python
>>> plan_text = '...\n> fixture where in-fence `## STEP 2 — Bellows QA` precedes real step.\n...\n## STEP 2 — Developer\n...'
>>> pattern = r'## STEP 2\b[^\n]*'
>>> match = re.search(pattern, plan_text)
>>> 'qa' in match.group(0).lower()
True           # WRONG — real Step 2 is "Developer", not "QA"
>>>
>>> # With anchor:
>>> match2 = re.search(r'^## STEP 2\b[^\n]*', plan_text, re.MULTILINE)
>>> 'qa' in match2.group(0).lower()
False          # CORRECT
```

This means a plan could have `is_qa_step` return True for a non-QA step (or False for a real QA step) if inline references appear earlier. In the 2026-05-11 case, the inline reference `## STEP 2 — Bellows QA` happens to match the real Step 2 role, so `is_qa_step` returned the right answer — by coincidence.

### Recommended fix shape

**Shape (a): Anchor `## STEP` to line-start across all 3 unanchored parsers.**

Change the regex in each function to use `^` with `re.MULTILINE`:

| Function | Current flags | Add |
|---|---|---|
| `_extract_step_text` (gates.py) | `re.DOTALL` | `re.MULTILINE` + `^` in pattern |
| `_extract_step_text_from_plan` (verdict.py) | `re.DOTALL` | `re.MULTILINE` + `^` in pattern |
| `_gate_is_qa_step` (gates.py) | none | `re.MULTILINE` + `^` in pattern |

The lookahead in `_extract_step_text` also needs anchoring: change `(?=\n## STEP |\Z)` to `(?=\n^## STEP |\Z)` (or equivalently use `(?=^## STEP |\Z)` since the `\n` before `^` is redundant with `re.MULTILINE`).

**Estimated LOC:** ~6 (3 pattern changes + 3 flag additions).

**Test surface:**
- **New tests:** 3 — one per function verifying inline `## STEP N` references don't match. Similar shape to the `_ignores_in_fence_headers` tests added in commit `4d57fd3`.
- **Tests at risk of breakage:** 0 — existing tests use `## STEP N` at line-start (standard plan format). Adding `^` + `re.MULTILINE` does not change behavior for line-start patterns.

**Dependencies:** None. No BACKLOG items block this fix. The fence-stripping fix (4d57fd3) is complementary, not conflicting — both address the same parser-vs-structure confusion class but target different subclasses (fenced blocks vs inline code).

---

## Q6 — Recurring-Bug-Class Guardrail Consistency

### Prior closed items touching `_gate_rule_20_self_check` or support path

```
$ grep -lE "rule_20|_gate_rule_20|self_check" bellows/knowledge/decisions/Done/*.md
```

| Done plan | What it changed | Prevents 2026-05-11 FP? |
|---|---|---|
| `executable-rule-20-self-check-gate-2026-05-05.md` | Initial gate implementation | No (introduced the gate) |
| `executable-rule-22e-rule-20-tightening-2026-05-05.md` | Tightened banner checking | No (addressed banner format, not deposit enumeration) |
| `executable-deposit-exists-worktree-aware-2026-05-06.md` | Threaded `wt_path` to `_gate_deposit_exists` | No (different gate, and bellows-self plans don't use worktrees) |
| `executable-rule-20-self-check-wt-path-2026-05-10.md` | Threaded `wt_path` to `_gate_rule_20_self_check` | No (bellows-self, `wt_path == project_path`) |
| `executable-rule-20-single-source-2026-05-10.md` | Canonical banner template | No (governance-side, doesn't affect step text extraction) |
| `diagnostic-gate-path-resolution-post-teardown-2026-05-10.md` | Diagnosed RC1 + RC2 of gate path resolution | No (RC1 = wt_path, RC2 = legacy prose regex, neither is step text extraction) |
| `executable-session-wrap-2026-05-10.md` | Session wrap | No |
| `executable-session-wrap-s3-2026-05-09.md` | Session wrap | No |
| `executable-s3-fix-qa-rule-20-banner-redeposit-2026-05-09.md` | S3 fix for verdict retry loop | No |

### Guardrail assessment

**2 prior code fixes** exist in `_gate_rule_20_self_check`'s support path:
1. `executable-deposit-exists-worktree-aware-2026-05-06.md` — `_resolve_deposit_path` wt_path threading
2. `executable-rule-20-self-check-wt-path-2026-05-10.md` — `_gate_rule_20_self_check` wt_path threading

Both target **Class 1** (worktree path resolution). The 2026-05-11 false positive is **Class 2** (step text extraction) — a distinct root cause that neither prior fix addresses.

**Guardrail constraint applies:** 2+ prior fixes exist in the gate's support path. However, the recommended fix (line-start anchoring) IS structural: it eliminates the entire class of inline-reference false matches for all 3 unanchored parsers, aligning them with `extract_total_steps` which already uses `^` + `re.MULTILINE`. This is not a point patch — it is a regex correction that makes the parser's intent (match structural headers) match its behavior (currently matches any occurrence).

The fix also benefits `_gate_is_qa_step` (confirmed vulnerable in Q5) and `_extract_step_text_from_plan` in verdict.py (same regex, same vulnerability), preventing future false positives across both the gate path and the verdict request path.

---

## Planner-Facing Summary

**(i) Fix shipped (Q0):** No. Neither commit `be8cba4` (wt_path threading) nor `4d57fd3` (fence-stripping) prevents the 2026-05-11 false positive. The root cause is in the `## STEP N` regex pattern, not in path resolution or fenced code blocks.

**(ii) False-positive count (Q4):** 6 total false positives across 9 gate failures since 2026-05-05. 5 are Class 1 (worktree path resolution, fixed by prior commits). 1 is Class 2 (step text extraction, this diagnostic's subject). The Class 2 trigger condition (inline `## STEP N` references in plan prose) has occurred in at least 2 plans; only 1 tripped the Rule 20 gate because the other plan had no QA step.

**(iii) Root cause class (Q5):** Class (d) — `_extract_step_text` parser gap. The `## STEP N` regex is not anchored to line-start, causing `re.search` to match inline code references (`\`## STEP 2\``) before the real structural `## STEP 2` header. The gate then extracts deposits from the wrong step's text, checks the wrong file for the Rule 20 banner, and fires a false positive.

**(iv) Recommended fix shape:** Anchor `## STEP` to line-start (`^` + `re.MULTILINE`) in 3 functions: `_extract_step_text` (gates.py), `_extract_step_text_from_plan` (verdict.py), `_gate_is_qa_step` (gates.py). ~6 LOC, 3 new tests, 0 regressions expected. Aligns with `extract_total_steps` which already uses this pattern.

**(v) Structural-fix-required (Q6):** Yes — 2 prior fixes exist in the gate's support path (wt_path threading ×2). The recommended fix meets the structural-fix bar: it eliminates the entire Class 2 false-match subclass across all 3 affected parsers, not just one call site.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Root cause audit of `_gate_rule_20_self_check` false positive on `executable-fence-strip-plan-text-parsers-2026-05-11` Step 2. Traced the false positive to `_extract_step_text` regex lacking line-start anchor, causing inline `## STEP 2` references in plan prose to match before the real structural header. Population audit of all 9 gate failures since 2026-05-05 classified 3 true positives and 6 false positives (5 Class 1: worktree path, 1 Class 2: step text extraction). Confirmed `_gate_is_qa_step` has the same vulnerability.

### Files Deposited
- `bellows/knowledge/research/rule-20-gate-false-positive-root-cause-2026-05-11.md` — full findings (Q0-Q6) with REPL fixtures, population audit table, and Planner-facing summary

### Files Created or Modified (Code)
- None (diagnostic only — no source code changes per plan constraints)

### Decisions Made
- Classified root cause as Class (d): `_extract_step_text` parser gap (line-start anchor missing)
- Recommended fix shape (a): anchor `## STEP` to `^` + `re.MULTILINE` across 3 unanchored parsers
- Confirmed `_gate_is_qa_step` is also vulnerable (same unanchored pattern)

### Flags for CEO
- None

### Flags for Next Step
- Fix must apply to both `_extract_step_text` (gates.py) and `_extract_step_text_from_plan` (verdict.py) — documented duplicates, keep in sync
- `_gate_is_qa_step` uses a different regex shape (`[^\n]*` instead of `.*?`) but needs the same `^` + `re.MULTILINE` anchor
- The lookahead `(?=\n## STEP |\Z)` in `_extract_step_text` should also anchor: `(?=\n^## STEP |\Z)` or use `(?=^## STEP |\Z)` with `re.MULTILINE`
