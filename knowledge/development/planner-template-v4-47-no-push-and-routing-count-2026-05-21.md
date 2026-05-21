# Dev Log: PLANNER_TEMPLATE v4.47 — Explicit Agent No-Push Rule + Rule 25 Routing-Count Fix

**Plan:** `executable-planner-template-no-push-and-routing-count-2026-05-21`
**Date:** 2026-05-21
**Agent:** Bellows Documentation Analyst (Step 1)
**Status:** Complete

---

## Output Receipt

**Files Created or Modified:**
- `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (modified — 5 edits: A, B, C, D, E)
- `bellows/knowledge/development/planner-template-v4-47-no-push-and-routing-count-2026-05-21.md` (created — this file)

---

## Edit A — Rule 8 Mirror Paragraph (No-Push Sentence)

**Anchor used:** `**Per Rule 23 (housekeeping discipline), the order is feedback append → final commit.** The final commit is the absolute last agent operation. [...] producing stranded verdict requests for already-shipped work.`

**Location:** Line 477

**Before (last ~50 chars of paragraph):**
```
...producing stranded verdict requests for already-shipped work.
```

**After (appended to same paragraph):**
```
...producing stranded verdict requests for already-shipped work. **Agents do NOT run `git push` during step execution.** The Planner handles all push activity at session-wrap. Agent-side push from inside a Bellows worktree is the root cause of parallel-SHA divergence (per 2026-05-21 teardown-git-operations diagnostic), validated by the 2026-05-21 verdict-enrichment plan which produced 4 commits with zero divergence by omitting push from step prose.
```

**Deviation from plan:** None. Edit landed as specified — additive append, same paragraph block, no paragraph break.

---

## Edit B — Rule 23(c) Paragraph (No-Push Sentences)

**Anchor used:** `**(c) Ordering: feedback → commit.** The final commit is the absolute last agent operation. [...] the deposited files pass Rule 22's (a)–(e) checks.`

**Location:** Line 631

**Before (last ~50 chars of paragraph):**
```
...the deposited files pass Rule 22's (a)–(e) checks.
```

**After (appended to same paragraph):**
```
...the deposited files pass Rule 22's (a)–(e) checks. **Agents do NOT run `git push` during step execution.** Push is a Planner session-wrap activity, not an agent step instruction. Agent-side push from inside a Bellows worktree commits to origin but leaves local main behind the worktree branch tip, producing parallel-SHA divergence (root cause identified 2026-05-21 teardown-git-operations diagnostic; mitigation validated by 2026-05-21 verdict-enrichment plan). Plan step prose MUST NOT include `git push` for agents; only `git add` and `git commit` are agent-side git operations. Rule 31 (submodule pointer bump) and Procedure 3 (git filter-repo post-execution) describe Planner-side and operator-side push activity respectively and are unaffected by this rule.
```

**Deviation from plan:** None. Edit landed as specified — additive append, same paragraph block.

---

## Edit C — Rule 25 Preamble Count

**Anchor used:** `only two codes authorize auto-proceed, everything else stops:`

**Location:** Line 671

**Before:**
```
...The routing is deliberately conservative — only two codes authorize auto-proceed, everything else stops:
```

**After:**
```
...The routing is deliberately conservative — only three codes authorize auto-proceed, everything else stops:
```

**Deviation from plan:** None. Single-word substitution (`two` → `three`).

---

## Edit D — Version Header Bump

**Anchor used:** `**Version:** 4.46\n**Last Updated:** 2026-05-21 (v4.46)`

**Location:** Lines 5–6

**Before:**
```
**Version:** 4.46
**Last Updated:** 2026-05-21 (v4.46)
```

**After:**
```
**Version:** 4.47
**Last Updated:** 2026-05-21 (v4.47)
```

**Deviation from plan:** None. Two-line replacement, version bumped from 4.46 to 4.47.

---

## Edit E — Lessons Row Append

**Anchor used:** Last existing Lessons row beginning `| 2026-05-21 | Multi-session date-drift pattern`

**Location:** After line 1380 (inserted as new line 1381)

**Before (end of Lessons table):**
```
| 2026-05-21 | Multi-session date-drift pattern resolved by new Rule 40 (v4.46). [...] |

---
```

**After (new row appended before the `---` separator):**
```
| 2026-05-21 | Multi-session date-drift pattern resolved by new Rule 40 (v4.46). [...] |
| 2026-05-21 | BACKLOG entries written from memory can misdescribe the current file state. The 2026-05-21 governance pass started from a BACKLOG entry saying "remove `git push` from Rule 23 housekeeping" — but the pre-write contradiction scan (Rule 22) found that Rule 23(c) had no push verb to remove. The actual fix needed was additive (explicit prohibition), not subtractive. Caught at draft time; BACKLOG entry corrected before the plan shipped. **Pattern:** when authoring a governance plan from a BACKLOG entry that proposes "remove X" or "delete Y" wording, the pre-write contradiction scan must include verifying X or Y actually exists in the current file. Third occurrence of pre-executable-scan catching a stale rule before ship (after 2026-04-10 v4.18 contradiction and 2026-05-11 Rule 26 directory-bullet canary). The scan is doing its job; it works because the Planner runs it. |

---
```

**Deviation from plan:** None. New row appended immediately after the last existing row, before the closing `---` separator.

---

## Verification Summary

All five edits verified by reading the modified sections back after each edit:
- Edit A: Line 477 — no-push sentence present, paragraph unbroken
- Edit B: Line 631 — no-push sentences present, paragraph unbroken
- Edit C: Line 671 — "three" confirmed (was "two")
- Edit D: Lines 5–6 — v4.47 confirmed
- Edit E: Line 1381 — new Lessons row present, table structure intact
