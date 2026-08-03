# Diagnostic: post-activation live canary — does the shipped splitter emit one row per bullet through the REAL entry point?

**Type:** Diagnostic
**Project:** bellows
**Depends on:** plan 294 (Done — shipped `sanitize_items`, the bullet-aware Forward Register splitter), plan 292 (Done — the delimiter contract this authors from)
**Created:** 2026-08-03
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T0

## Why this exists — the change is shipped and UNPROVEN, and doctrine says so explicitly

Plan 294 shipped `sanitize_items` with 839 passing tests and both mandated controls green. **That is not proof.** Checklist #32: *"Grep proves wiring exists; a green suite proves it does not throw; only an **observed delta** proves it works. Verification of any wired call must observe a behaviour change through the real entry point."* It names Workaround #15 for this exact case, and the codified discipline is unambiguous: **for any silent/best-effort daemon write path, a post-activation live canary is mandatory, not optional.**

The Forward Register append is that path — it logs and returns on failure, which is why its breakage went unnoticed long enough to need this whole line of work. **294 could not run the canary: it cannot restart the daemon that dispatches it.** The restart has now happened, so this diagnostic is the canary.

**What the Planner verified before writing this (Rule 52 — measured, not inherited):**
- `sanitize_items` is on bellows main: `grep -c 'def sanitize_items' bellows.py` → **1**.
- 294's code commit: **2026-08-03T07:33:24-05:00**.
- The running daemon: **pid 86216, started Mon Aug 3 08:11:27** — **AFTER** the commit, so the process is executing the post-change module. This is the precondition the canary needs and it is the one thing that makes the run meaningful.
- **Before-count, `bellows/knowledge/FORWARD.md`: 26 rows.**
- Other registers, untouched by this: lessons-forge 1, governance 0, invoice-pulse 33, anvil 8.

## The canary payload is REAL work, not a synthetic probe

This diagnostic's Receipt emits a **TWO-ITEM contiguous bulleted** `#### Forward Register` block carrying the two remaining bellows backlog items. **If the splitter is live, the daemon appends TWO rows (27 and 28). If it is not, exactly one lands and the first item swallows the block.** Either outcome is a decisive, observable delta — and the payload drains real backlog either way, so the canary costs nothing beyond the dispatch.

⚠️ **CONTIGUOUS IS MANDATORY, and this is the one way to get a false refutation.** `parser.py:74-77` terminates the Receipt block at the first BLANK LINE, so bullets separated by blank lines deliver only the first to `_append_forward_row` — a correctly-shipped splitter would then emit one row and read as refuted. **The two bullets below have no blank line between them. Do not reformat them.**

## Questions (deposit findings; decide NOTHING, build NOTHING, CHANGE NOTHING)

**Q1 — Is the running daemon executing the post-change module?** Confirm from the process, not from main: report the daemon PID and start time and 294's code-commit timestamp, and state whether start postdates commit. ⚠️ **Use `pgrep -f '[b]ellows\.py'` on its own line in prose — NOT inside a markdown table cell.** A `|` in a table cell must be escaped, and the escaped form silently becomes a literal pipe that matches nothing; that exact defect produced a false "no daemon running" reading in plan 294's QA.

**Q2 — Record the before-count.** `grep -cE '^\|[[:space:]]*[0-9]+[[:space:]]*\|' /Users/marklehn/Developer/GitHub/bellows/knowledge/FORWARD.md`. Expected **26** — verify and report the actual, never force.

**Q3 — What does the shipped `sanitize_items` return for this exact two-bullet payload?** Import it from the live module and run it on the block below, verbatim. Report the returned list. **This is the in-process prediction the post-merge result is compared against** — if the function returns two items and the register still gains one, the defect is in the append path, not the sanitizer, and that distinction is the whole value of running both.

**Q4 — Does anything else write this register during the window?** Report whether any other plan is mid-dispatch.

## Method + boundaries

- **READ-ONLY.** Do NOT edit `bellows.py`, any test, or ANY `FORWARD.md`. Do not restart the daemon. Do not hand-write a register row — the daemon appends this plan's block post-merge and **skips its own write entirely if the file appears in `files_changed`.**
- ⚠️ **Do NOT attempt to observe the result.** The append happens post-merge, after this step ends. **The Planner observes the after-count.** A claim here to have seen rows land would be an attestation of something unobservable from inside the step.
- ⚠️ `grep` is a ugrep shim: use `grep -F` for literals and `--` before a leading-dash pattern. The shell is zsh: an unmatched glob aborts the command and `2>/dev/null` does not suppress it — use `find … -name '…'`.

## Required deposit structure

`knowledge/research/forward-splitter-canary-2026-08-03.md`, containing Q1–Q4's answers with raw command output, the before-count, the in-process `sanitize_items` prediction, and `## Unresolved` (or NONE).

### Output Receipt

Close with `### Status` (**Complete**), `### Deposits`, and `### Ledger Updates` containing `#### Prompt Feedback` and:

**`#### Forward Register`** — ⚠️ **EMIT BOTH BULLETS, CONTIGUOUS, NO BLANK LINE BETWEEN THEM. This block IS the canary.**

- plan_lint section-4 T2 panel check matches a line's opening and never its content, so a plan whose panel line is present but hollow passes the check.
- plan_lint section-4 closing check has its negation strip defeated by one intervening word, so a plan closing on a fold can read as closing dry.

## Drafting Cycle

> **⚠️ THIS SECTION IS A RECORD, NOT INSTRUCTIONS.** Gate-matching strings are described, never quoted.

**Tier:** T0 — **no trigger fires.** Read-only, single step, mutates nothing, ships no code, touches no governance surface. The only write is the daemon's own post-merge append, which is the subject under test rather than an action of this plan.
**Walks:** v0 → v1. Weak-spots and Vulnerabilities walked against the draft; both folded once. **Destruction is SKIPPED under §2.2's stated skip-condition — a pure-additive read-only plan touching no existing behaviour — and the reason is stated rather than the lens silently omitted.** ACID is skipped per §2.5 (T0).
- Weak spots: w1 1 folded — the payload originally sat in a bulleted list with blank lines between items, which the parser would have truncated to one, producing a false refutation of a working splitter.
- Vulnerabilities: w1 1 folded — the daemon-liveness command was specified for a table cell, the exact pipe-escaping collision that produced a false negative in 294's QA.

**Conflicts:** CL1 — the block must stay contiguous; any reformatting that inserts blank lines between the bullets invalidates the canary. CL2 — the step may not observe its own result; the Planner does, post-merge.
**Closing:** last event is a lens pass. The canary's value is that it is decisive in both directions: two rows proves the splitter live end-to-end, one row localises the defect to the append path given Q3's in-process prediction.
