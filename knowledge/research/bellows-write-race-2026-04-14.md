# Bellows — Planner Write-Race Diagnosis (2026-04-14)

**Status:** Diagnosed, workaround adopted, formal fix deferred
**Severity:** High for Planner-side workflow, Low for Bellows core
**Discovered by:** Planner (Claude Project conversation, 2026-04-14)
**Incident:** First plan deposit of 2026-04-15 session; stranded after partial execution
**Bellows commit at time of incident:** Post-Bug-A/B/C reliability fixes shipped 2026-04-14

---

## What happened

The Planner attempted to deposit `executable-anvil-test-failures-fixture-2026-04-14.md` to `anvil/knowledge/decisions/` using the standard Desktop Commander chunked-write pattern: one initial `write_file` with `mode: rewrite` followed by multiple `mode: append` calls to build up the plan in ~25-line chunks. This is the pattern the Desktop Commander tool description recommends for any file over ~30 lines.

Bellows' watchdog observer fired `on_created` on the initial write. The `PlanHandler._handle` method:
1. Saw the file was a runnable plan (`is_runnable_plan` passed)
2. Added the path to `_seen`
3. Dispatched to `handle_new_plan` which spawned a thread running `_run_tracked` → `run_plan`
4. `run_plan` called `load_file(plan_path)` to read the plan contents
5. At that moment, the file contained only the first ~20 lines (header + "How to Run" section + start of Step 1)
6. `extract_total_steps` counted `## STEP` headers in that partial content — an unknown count depending on timing (the log reported `plan has 1 steps` which is internally inconsistent with later file state)
7. The bootstrap prompt was dispatched to Claude Code, which began executing Step 1
8. Step 1's agent ran `shutil.move(plan_path, in-progress-plan_path)` — renaming the file out from under the Planner
9. The Planner's subsequent `mode: append` calls to the original filename created a NEW file at the original path containing only the later chunks — a malformed Step 2 fragment
10. Step 1 DEV completed and committed the fix (`c49f060`) successfully despite the mess
11. Bellows' `_is_plan_stranded` check at the end of `run_plan` fired correctly: `in-progress-` file still present, expected Done file missing → STRANDED notification
12. The malformed fragment remained in the decisions folder and would have been picked up as a new plan by the next `_rescan` tick

## Why it happened

The Planner's chunked-write pattern assumes the target directory is not under an active filesystem watcher. Desktop Commander's `write_file` tool documentation recommends 25-30 line chunks and even emits performance warnings for files over 50 lines. This guidance is sound for normal file creation. It is **incompatible** with a directory that has a live watchdog observer dispatching `on_created` events on the first byte.

Bellows' watcher has no debounce, no settle period, and no write-completion detection:
- `on_created` fires on the first filesystem event
- `PlanHandler._handle` immediately calls `is_runnable_plan` and dispatches
- There is no delay between file detection and `load_file` being called
- There is no check that the file is stable (size unchanged over N milliseconds) before reading

This is a reasonable default for plans that arrive atomically (single-write deposits, git operations, mv commands). It is a race hazard for chunked writes.

## Why Bellows' existing stranded detection caught the symptom but not the cause

The Bug A fix (stranded plan detection) shipped on 2026-04-14 correctly identified that the plan file was not in Done/ after the agent reported step complete. That fix prevents silent failures but does not diagnose root causes. The write-race would have been invisible before Bug A — the agent would have completed Step 1, the Planner's later appends would have created a new file, Bellows would have skipped the `_check_queue_drain` congratulation, and nobody would have known anything was wrong until the rogue fragment got picked up on the next rescan.

The stranded detection turned a silent failure into a loud one, which is exactly what it was designed to do. But loud ≠ diagnosed. The diagnosis required reading `bellows.py` source, re-reading the stranded plan's current contents, and realizing the `in-progress-` file contained only the early chunks while a freshly-created `executable-` file contained only the late chunks.

## Workaround adopted (Planner-side, effective 2026-04-14)

**Staging-move write pattern:**

1. Planner writes the full plan content to a staging location OUTSIDE any watched directory. For anvil: `anvil/knowledge/research/_staging_<filename>.md`. For other projects: equivalent path under `knowledge/research/`. For cross-project plans: `/tmp/` or a per-Planner scratch folder.
2. The staging write may use chunked appends safely because no watcher is observing the staging location.
3. After the final chunk is written, the Planner reads the staging file back via `Filesystem:read_text_file` and verifies the content is complete and well-formed.
4. Only then does the Planner call `Filesystem:move_file` to move the staging file into `decisions/` with its canonical filename. The move is a single atomic filesystem rename that fires exactly one `on_created` event on Bellows' watcher, and the file content is complete at the moment the event fires.

This pattern sidesteps the race entirely without requiring any Bellows-side changes. It is a Planner discipline, enforced in prompt content and reinforced via this note.

## Formal Bellows-side fix (deferred)

The correct long-term fix is Bellows-side, not Planner-side. A well-behaved filesystem watcher for plan dispatch should:

1. **Debounce file events.** After `on_created` fires, wait some minimum window (suggested: 500ms) and check whether the file has been modified again. If yes, reset the timer. Only dispatch after the file has been stable for the full window. This guarantees the writer has finished.
2. **Verify plan structure before dispatch.** Before calling `extract_total_steps`, verify the file parses as a valid plan (has a header, has at least one `## STEP` section OR is a diagnostic, and ends with a complete block rather than mid-sentence). A simple "does the file end with `>` or `---` or a closing code fence?" check would catch most truncation cases.
3. **Distinguish `on_created` from `on_modified` more carefully.** The current handler treats both identically and short-circuits on `_seen`. But a modify event on a file that was never in `_seen` because it was created-then-modified quickly might race against the initial create. Consider coalescing events per-path with a small buffer.

None of these fixes are trivial. All of them require testing against the existing plan deposit flow to make sure they don't regress. This is material for a Bellows reliability session, not a quick patch.

**Priority:** Medium. The Planner workaround is effective and cheap. The Bellows-side fix is correct but not urgent. File a ticket for the next Bellows session.

## What got fixed in the incident recovery

- Anvil test fixture fix shipped correctly (DEV commit `c49f060`)
- Malformed Step-2-only fragment deleted manually by CEO via `rm`
- In-progress file closed out via manual Claude Code bootstrap (not routed through Bellows)
- Anvil PROJECT_STATUS.md updated with full context including Bellows write-race as the root cause
- Plan moved to Done
- Anvil fully green (217/217 tests pass)

## Open items

- [ ] Validate the staging-move pattern with a throwaway test plan against live Bellows
- [ ] Log Bellows-side debounce work as a future reliability session deliverable
- [ ] Add the staging-move pattern to PLANNER_TEMPLATE.md as a Rule (candidate: Rule 23 — Watcher-safe file writes)
- [ ] Update the Desktop Commander prompt feedback log noting that the 25-30 line chunk guidance is incompatible with watched directories

## Related source

- `bellows/bellows.py` — `PlanHandler._handle`, `on_created`, `on_modified`, `run_plan`, `_is_plan_stranded`
- `anvil/knowledge/decisions/Done/executable-anvil-test-failures-fixture-2026-04-14.md` — the stranded plan that triggered the diagnosis
- `anvil/PROJECT_STATUS.md` entry dated 2026-04-14 — incident closeout
- `PLANNER_TEMPLATE.md` v4.20 — does not yet include a rule governing watcher-safe writes

## Credit

Diagnosis performed by the Planner in conversation with the CEO during the 2026-04-15 session kickoff. Root cause located by cross-referencing the Bellows source dump (provided by CEO), the disk state of both the `in-progress-` file and the malformed fragment, and the `git log` showing DEV's commit landed successfully despite the stranding. The diagnosis took about 20 minutes and required three tool calls to the Filesystem MCP plus one source read of `bellows.py`.
