# Session Lessons — 2026-04-16

Captured during session wrap. Migrate to `/Users/marklehn/Desktop/GitHub/LESSONS.md` tomorrow after the 4 stashed governance files are un-stashed and committed or discarded. These are the durable lessons from today's six-phase Bellows push plus the Forge findings.

## Lesson 1 — Real gates measure, they don't hope

Gate 2 (ceo_flags) was the only gate in Bellows' validation suite that tried to parse free-form agent prose. Every other gate read structured JSON from claude -p's output, ran a shell command, or did string matching against our own files. Gate 2 was the only gate that kept failing — across Phase 7, Polish, and the first real test.

Every patch to Gate 2 added more regex patterns. The patches made the gate more lenient without making it more reliable. Agents kept finding new ways to express "CEO flags raised" (`**Four CEO flags raised:**` + numbered list, `## CEO Flag` heading, `### Action Items Needing CEO Decision`, etc.) that the regex didn't match.

Phase 8's fix replaced prose parsing with mechanical signals: plan-header YAML `pause_for_verdict` field + agent-authored verdict-request files. Both are filesystem state the gate can check via `os.path.exists()` and simple YAML parsing of our own plan files. No agent cooperation on format required.

**Generalized lesson:** any time the answer to "how do we catch X?" is "add another regex pattern to match agent output," the architecture is probably wrong. Real gates check filesystem state, parse structured data, or string-match our own files. When a gate depends on the subject-being-gated cooperating with a specific prose format, it will silently fail.

**Related:** invoice-pulse's validation gates work this way. They parse carrier invoices (structured data from an external system) against known rules. They don't ask carriers to format invoices nicely — they parse what arrives. Bellows' gates should do the same.

## Lesson 2 — Tests passing ≠ design correct

Phase 8 shipped with 64/64 tests passing. The test suite verified header parsing, verdict-request detection, the defaults-flip for diagnostics, and the continue-to-Done fix. All green.

Then the first real single-step diagnostic (no YAML frontmatter) stranded. Reason: the final-step block in `run_plan()` only posts a verdict request when gates fail OR it's a QA step. The conditions that ARE checked in the mid-plan while-loop (`header_says_pause`, `verdict_requested`, `effective_auto_close`) were never added to the final-step block. For diagnostics (single step, so while-loop never runs), this means the new pause signals don't work at all.

The tests didn't catch this because none of them exercised "clean single-step diagnostic with `auto_close=false` should post verdict, not strand." I specified what the tests should verify; I didn't specify the gap.

**Generalized lesson:** tests verify what you ask them to verify. They don't catch gaps in your asks. When shipping a feature with a behavior-change (like "diagnostics now pause by default"), write a test that exercises the END-TO-END new behavior, not just the individual new code paths. Phase 8's tests tested each new helper function in isolation. None tested "plan lands in decisions/ → Bellows runs it → ends up where it should."

## Lesson 3 — Pattern recognition: stop patching after the second iteration

Phase 7 shipped flag detection. Phase 7 Polish patched the flag regex to add 5 more patterns. Phase 8 redesigned flag detection entirely to use plan headers and action files.

Three iterations on the same problem in one session. The third was the right architecture, but the first two were noise that cost implementation time, test time, and cleanup of stranded plans.

**Generalized lesson:** when we're about to write the third patch on the same thing in one session, stop and redesign. "The second patch didn't work; this third one will" is almost always wrong. Budget a design pass before touching the code a third time. Phase 8 was 2 hours including design conversation and tests. Phase 7 Polish was 45 minutes and didn't solve the problem. The time math favors stepping back earlier.

## Lesson 4 — Scope_check with OR-semantics produces false positives

Phase 8's QA Step 2 was flagged by Gate 8 (scope_check) as out-of-scope for modifying four files: `COMPANY.md`, `LESSONS.md`, `bellows/config.json`, `governance/GUARDRAILS.md`. None of these were modified by Step 2 — they were pre-existing uncommitted drift from earlier sessions.

The bug is in `_parse_diff_stat(post_diff, pre_diff)`: it unions filenames from both diffs instead of computing the difference. A file that was already dirty BEFORE a step runs will always appear in the output as "changed during this step," even if nothing was done to it.

Confirmed root cause and sketched fix (Option B — diff-of-diffs: compare per-file stat lines between pre and post) in `knowledge/research/bellows-parse-diff-stat-audit-2026-04-16.md`. Fix not yet implemented.

**Generalized lesson:** gates that detect change need to compare before-and-after, not union before-OR-after. "This file appears in the diff" is not the same as "this file was modified during the step." Any step that runs against a working tree with uncommitted state will hit this class of bug. Fix: always compute `post - pre` (with stat-line comparison for changes to already-dirty files), never `post ∪ pre`.

## Lesson 5 — Staging → decisions discipline prevents race conditions

This morning's test had two diagnostics run accidentally — I wrote one, the watcher fired, I tried to pull it back by renaming, but the dispatch was already in flight. Result: both diagnostics ran in parallel on related questions.

All of today's subsequent plans staged to `knowledge/research/_staging_*` first and only moved into `knowledge/decisions/` after I was certain the prompt was correct and I was ready for dispatch. Zero race conditions since that change.

**Generalized lesson:** the filesystem IS the protocol. Watchers fire on creation; once a file is in a watched directory, you cannot reliably revoke dispatch. Stage elsewhere first. The `_staging_` prefix convention worked cleanly all day.

## Lesson 6 — Planner-as-verification-step (Rule 22) is load-bearing

Three separate times today, Rule 22's Planner-reads-the-deposit-file verification caught things the agent's conversation summary didn't surface:

1. Phase 8 dev log showed "Status: Complete" — reading it verified 7 expected files changed, none of the 4 scope-flagged files were in the dev log's Files Deposited list → correct interpretation: stale working-tree drift, not new changes.

2. Polish QA report self-check showed PASSED — reading the evidence files confirmed all 3 were present and non-empty before authorizing Step 2 close.

3. The stranded `_parse_diff_stat` diagnostic's findings were verified via direct read before manual move to Done — confirmed the deposit actually contained Q1-Q4 answers, not a hollow "Status: Complete" receipt.

**Generalized lesson:** an agent's conversation summary is not a substitute for the Planner reading the actual file. Every time I deferred to the agent's summary without reading the file, I missed something. Every time I read the file first, I caught it.

## Lesson 7 — Forge calibration data can be orphaned, not just unreliable

The 2026-03-21 phrasing evaluations were first characterized as "rubber-stamped" (75% `would_prevent=1` with templated reasoning like "Cycle 2 eval against chunk XXXX"). That's true. But tonight's mismatch investigation uncovered a deeper finding: even re-running those calibration groups TODAY with the current `get_relevant_chunks` would produce completely different chunks (IDs jumped from 2080–3703 range to 11385–11490 range — ~5500 new higher-ID chunks have been ingested since March, and `ORDER BY id DESC` displaces them).

There is no path to reproduce the 2026-03-21 calibration. The 57 rows aren't just unreliable — they're orphaned from any reproducible retrieval state. This strengthens the case for annotation rather than re-evaluation.

**Generalized lesson:** when evaluating whether to invalidate historical data, check whether the system can reproduce the input conditions that generated it. Reliability is not the only axis — reproducibility matters too. Data from an irreproducible state is closed-book history, not live calibration.

---

## Meta-observation for the Forge appendage idea (future)

Today produced a lot of structural-fix signals that a future "plan-writing failure ledger" (mining verdict events for plan-design patterns) would want to capture:

- "Third patch in a session" as a halt signal (Phase 7/Polish/Phase 8 trio)
- "Tests pass but new behavior stranded" as a design-gap signal (Phase 8's final-step miss)
- "Scope_check fires on stale working tree" as a false-positive signal (false positives teach us about the underlying gate logic)
- "Prose parsing used where structured data would work" as an anti-pattern signal (Gate 2's whole arc)

These become candidate rules for the Forge appendage when it's built. Not tonight's work, but the lessons compound.


## Lesson 8 — Planner multi-chunk writes race against Bellows watcher

The Planner (in Claude Projects) wrote a completion diagnostic plan to `bellows/knowledge/decisions/` using three sequential `Desktop Commander:write_file` calls: chunk 1 (rewrite, header + bootstrap), chunk 2 (append, step claim block), chunk 3 (append, step body). Between chunk 1 and chunk 2, Bellows' filesystem watcher detected the new file, `_handle()` fired, and the agent ran `shutil.move()` to claim it — renaming it to `in-progress-`. Chunks 2 and 3 then appended to the ORIGINAL filename (no longer the claimed file), creating a new file with only the step body and no header. Result: Bellows ran a 1.36 KB fragment (header only, no instructions); the 5.60 KB file with the real instructions sat orphaned; the fragment ended up in Done as the "plan."

The race is deterministic: any multi-chunk write to a watched directory will lose the race if the watcher fires between chunks. Bellows' watchdog observer has no settle delay — `on_created` fires immediately.

**What Lesson 5's staging pattern should have prevented:** Lesson 5 (written earlier this same session) documented exactly this class of bug and established the `_staging_` prefix convention for staging plans outside the watched directory before atomic-moving them in. The Planner didn't follow its own lesson because the staging pattern was established in Claude Code (where agents write files), not in the Planner's MCP filesystem-tool workflow. The failure mode is the same; the tool surface is different.

**Fix options (ranked):**
1. **Planner always writes to a staging path first, then `Filesystem:move_file` into `decisions/`.** This is the Planner-side equivalent of Lesson 5. Zero Bellows changes needed. The staging path can be anywhere outside the watched directories — e.g., `knowledge/research/_staging_plan.md` or even the Planner's own container filesystem followed by a copy.
2. **Bellows adds a 5-second settle delay** — after detecting a new file, wait 5s with no further modification events before claiming. Bellows-side fix, protects against all multi-chunk writers.
3. **Planner writes the entire plan in a single tool call.** Fragile — large executables won't fit.

Option 1 is the immediate discipline fix. Option 2 is the right structural fix for a future Bellows reliability session. Both should happen.

**Broader lesson:** any watched-directory architecture has this race. The producer must guarantee atomic appearance (write elsewhere, move in) or the consumer must guarantee settle detection (debounce). Without either, multi-step writes are inherently unsafe.
