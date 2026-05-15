# Verdict Lifecycle Coupling — Diagnostic Findings (BACKLOG #9)
**Date:** 2026-04-19 | **Investigator:** SA agent

---

## 1. Rename Paths in bellows.py

There are **three** terminal-state rename operations:

### (a) Auto-close to Done — `run_plan()`, lines 348–365
When all gates pass, no QA checkpoint, no pause conditions, and `effective_auto_close` is True:
```python
done_dir = os.path.join(plan_dir, "Done")            # L355
os.makedirs(done_dir, exist_ok=True)                  # L356
done_path = os.path.join(done_dir, plan_filename)     # L357
source = inprogress_path if os.path.exists(inprogress_path) else plan_path  # L358
shutil.move(source, done_path)                        # L360
_delete_shadow(plan_filename)                         # L361
```
**Key observation:** This path never posts a verdict request, so no `verdict-request-*` file exists in `verdicts/pending/` for this transition. However, if a prior step DID pause and its verdict was consumed, this path does NOT sweep for any leftover pending files from earlier steps.

### (b) Continue-to-Done via verdict — `_consume_verdicts()`, lines 637–649
When a "continue" verdict is received for the final step:
```python
done_dir = os.path.join(decisions_path, "Done")       # L643
os.makedirs(done_dir, exist_ok=True)                  # L643
done_path = os.path.join(done_dir, original_name)     # L644
shutil.move(full_plan_path, done_path)                # L645
_delete_shadow(original_name)                         # L646
```
After this block, lines 670–672 clean up only the **specific step's** pending request:
```python
pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
if pending_file.exists():
    pending_file.unlink()
```

### (c) Halted via verdict — `_consume_verdicts()`, lines 658–666
When a "stop" verdict is received:
```python
halted_name = f"halted-{original_name}"               # L660
halted_path = os.path.join(decisions_path, halted_name)# L661
shutil.move(full_plan_path, halted_path)              # L662
_delete_shadow(original_name)                         # L663
```
Same single-step cleanup at lines 670–672 applies.

**Gap confirmed:** Neither (a), (b), nor (c) performs a **glob-based sweep** of `verdicts/pending/` for all step files matching the slug. Only the specific step triggering the terminal transition is cleaned.

---

## 2. Plan Slug Extraction Rule

**Utility function:** `verdict._slug_from_path()` — `verdict.py`, lines 65–75.

```python
def _slug_from_path(plan_path):
    basename = os.path.basename(plan_path)
    for prefix in ("in-progress-", "verdict-pending-", "executable-", "diagnostic-"):
        if basename.startswith(prefix):
            basename = basename[len(prefix):]
    if basename.endswith(".md"):
        basename = basename[:-3]
    return basename
```

**Behavior on example filenames:**

| Input filename | Stripped prefixes | Resulting slug |
|---|---|---|
| `executable-create-forge-developer-specialist-2026-04-18.md` | `executable-` | `create-forge-developer-specialist-2026-04-18` |
| `diagnostic-verdict-lifecycle-coupling-2026-04-19.md` | `diagnostic-` | `verdict-lifecycle-coupling-2026-04-19` |
| `parallel-1-executable-foo-2026-04-19.md` | *(none — `parallel-` not in list)* | `parallel-1-executable-foo-2026-04-19` |
| `in-progress-executable-bar-2026-04-19.md` | `in-progress-` then `executable-` | `bar-2026-04-19` |

**Important:** The loop strips prefixes **iteratively** (not just the first match). After stripping `in-progress-`, the remaining string is re-checked against subsequent prefixes. This means `in-progress-executable-X` correctly yields slug `X`, matching the slug that would be produced from the original `executable-X` filename.

**Parallel plan caveat:** `parallel-N-` is NOT in the prefix list, so parallel plan slugs retain the `parallel-N-executable-` prefix. This is consistent — verdict requests for parallel plans use this full slug.

---

## 3. Verdict Request Filename Shape

**Construction:** `verdict.post_verdict_request()` — `verdict.py`, line 84:
```python
filename = f"verdict-request-{slug}-step-{step_number}.md"
```
Where `slug = _slug_from_path(plan_path)`.

**Resolved verdict filename:** `verdict.check_verdict()` — `verdict.py`, line 145:
```python
filename = f"verdict-{plan_slug}-step-{step_number}.md"
```

**Consumption regex:** `bellows.py`, line 577:
```python
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
```

**Slug consistency check:** The slug used in `verdict-request-{slug}-step-{N}.md` (pending) matches the slug parsed from `verdict-{slug}-step-{N}.md` (resolved). Both derive from `_slug_from_path()`. The sweep glob pattern `verdict-request-{slug}-step-*.md` will correctly match all step files for a given plan.

---

## 4. Current State of `verdicts/pending/`

**Contents (as of 2026-04-19 18:07):** 1 verdict-request file.

| File | Age | Slug | Matching plan | Classification |
|---|---|---|---|---|
| `verdict-request-verdict-lifecycle-coupling-2026-04-19-step-1.md` | Apr 19 18:07 | `verdict-lifecycle-coupling-2026-04-19` | `in-progress-diagnostic-verdict-lifecycle-coupling-2026-04-19.md` in `Done/` | **(b) stranded after Done** — plan was moved to Done/ (with `in-progress-` prefix still attached), but the verdict-request was never consumed. This IS the BACKLOG #9 pattern: terminal transition occurred without verdict-request cleanup. |

**Active verdict-pending plans in `knowledge/decisions/`:**

| Plan file | Slug (via `_slug_from_path`) | Expected pending request |
|---|---|---|
| `verdict-pending-diagnostic-bellows-deposit-path-formats-2026-04-18.md` | `bellows-deposit-path-formats-2026-04-18` | `verdict-request-bellows-deposit-path-formats-2026-04-18-step-1.md` |
| `verdict-pending-diagnostic-bellows-verdict-file-schema-2026-04-18.md` | `bellows-verdict-file-schema-2026-04-18` | `verdict-request-bellows-verdict-file-schema-2026-04-18-step-1.md` |
| `verdict-pending-diagnostic-extract-primary-deposit-shape-2026-04-19.md` | `extract-primary-deposit-shape-2026-04-19` | `verdict-request-extract-primary-deposit-shape-2026-04-19-step-1.md` |
| `verdict-pending-diagnostic-gates-deposit-parser-current-state-2026-04-19.md` | `gates-deposit-parser-current-state-2026-04-19` | `verdict-request-gates-deposit-parser-current-state-2026-04-19-step-1.md` |
| `verdict-pending-diagnostic-rule-26-gate-smoke-test-2026-04-19.md` | `rule-26-gate-smoke-test-2026-04-19` | `verdict-request-rule-26-gate-smoke-test-2026-04-19-step-1.md` |

**Anomaly:** 5 plans are in `verdict-pending-` state but ZERO corresponding `verdict-request-*` files exist in `verdicts/pending/`. These requests were either: (a) already consumed by `_consume_verdicts` and the resolved verdicts were processed but the plan was not moved out of `verdict-pending-` state (indicating a match failure in `_consume_verdicts`), or (b) manually deleted. This is a **separate anomaly** from BACKLOG #9 (stranded requests after terminal state) — here the requests are missing while plans are still awaiting verdicts. The most likely cause: the Planner consumed these verdicts (creating resolved files), `_consume_verdicts` processed them (cleaning up pending requests at line 670–672 and moving resolved to `processed-*`), but the plan-file match at line 617 (`if pname.startswith("verdict-pending-") and plan_slug in pname`) failed due to slug substring issues, so the plan was never moved.

**Classification summary:**
- Category (a) legitimately pending: 0 files
- Category (b) stranded after Done: 1 file (`verdict-request-verdict-lifecycle-coupling-2026-04-19-step-1.md` — this diagnostic's own request, stranded because the plan was moved to Done without verdict consumption)
- Category (c) stranded after halted: 0 files (no halted plans exist)
- Category (d) orphaned: 0 files

The 33 stranded files observed on 2026-04-18 have been cleaned up (likely manually). Current state exhibits exactly 1 instance of the stranding pattern (category b), confirming the code gap remains active.

---

## 5. Race Window Analysis

### Auto-close path (run_plan, lines 348–365)
No verdict request is ever posted in the auto-close path. No race window exists here. The sweep would be a no-op in practice but is defensive.

### Verdict continue-to-done path (_consume_verdicts, lines 637–649)
Sequence:
1. `shutil.move(full_plan_path, done_path)` — plan moved to Done
2. `_delete_shadow(original_name)` — shadow cleaned
3. *[proposed sweep would go here]*
4. Line 670–672: specific pending request cleaned
5. Line 675–676: resolved verdict moved to `processed-*`

**Can a new verdict-request be written after the sweep?** No. At continue-to-done, the plan is on its final step. No subsequent step execution can occur. The only writer of verdict-request files is `verdict.post_verdict_request()`, called from `run_plan` during step execution. Since no further steps will execute, no new requests can appear.

### Verdict halt path (_consume_verdicts, lines 658–666)
Same analysis applies. After halting, no further step execution occurs for this plan.

### BACKLOG #1 scope_check race
The scope_check race (if it exists) affects whether a `verdict-request-*` file is written by `run_plan` during active execution. Once a plan reaches terminal state, `run_plan` has already returned, so scope_check cannot trigger a late write. **The scope_check race does NOT affect the sweep.**

### Post-Done verdict processing
**Is there any scenario where a verdict request arriving AFTER move-to-Done should be processed?** No. Once a plan is in Done/ or halted, Bellows never processes it again. `is_runnable_plan()` (line 424–427) rejects plans with `in-progress-`, `verdict-pending-`, or `halted-` prefixes, and Done/ files are in a subdirectory not scanned by the watcher.

---

## 6. Resolved/ Folder Interaction

**Current state of `verdicts/resolved/`:** Contains 58 `processed-verdict-*` files. All are consumed verdict files renamed with the `processed-` prefix by `_consume_verdicts` (line 675–676). Zero un-processed verdict files remain.

**Interaction with pending stranding:** The `_consume_verdicts` flow is:
1. Read verdict from `resolved/` (line 573–578)
2. Act on it (continue/halt) (lines 622–667)
3. Clean specific pending request (lines 670–672)
4. Move verdict to `processed-*` (lines 675–676)

`resolved/` is append-only from the Planner's perspective, consume-once from Bellows' perspective. No stranded-file pattern exists in `resolved/`. **The sweep should NOT touch `resolved/`.**

For each verdict-pending plan, I checked for corresponding `processed-*` files in `resolved/`:
- `processed-verdict-bellows-deposit-path-formats-*`: NOT found — verdict was never rendered
- `processed-verdict-bellows-verdict-file-schema-*`: NOT found
- `processed-verdict-extract-primary-deposit-shape-*`: NOT found
- `processed-verdict-gates-deposit-parser-current-state-*`: NOT found
- `processed-verdict-rule-26-gate-smoke-test-*`: NOT found

This confirms the 5 verdict-pending plans are genuinely awaiting CEO verdicts that haven't been rendered yet. Their missing pending-request files (noted in section 4) is a separate anomaly — likely the requests were posted but cleaned up by an external process or prior debugging.

---

## 7. Sweep Call-Site Proposal

### Function signature
```python
def _cleanup_verdicts_for_slug(slug: str) -> int:
    """Remove all verdict-request files for a given plan slug from verdicts/pending/.
    Returns count of files removed."""
```

### Call sites (3 locations)

**(1) Auto-close in `run_plan()`** — insert at line 359, BEFORE `shutil.move(source, done_path)`:
```python
# Line 358: source = inprogress_path if ...
_cleanup_verdicts_for_slug(_slug_from_path(plan_path))  # NEW
# Line 360: shutil.move(source, done_path)
```
**Justification:** Defensive. No verdict requests should exist here, but if a multi-step plan's earlier step had a manually-resolved verdict with cleanup failure, this catches it.

**(2) Continue-to-done in `_consume_verdicts()`** — insert at line 644, BEFORE `shutil.move(full_plan_path, done_path)`:
```python
# Line 643: os.makedirs(done_dir, exist_ok=True)
_cleanup_verdicts_for_slug(plan_slug)  # NEW — plan_slug already extracted at L580
# Line 645: shutil.move(full_plan_path, done_path)
```
**Justification:** Cleans ALL step files for the slug, not just the current step. The line 670–672 per-step cleanup becomes redundant but harmless (belt-and-suspenders).

**(3) Halted in `_consume_verdicts()`** — insert at line 661, BEFORE `shutil.move(full_plan_path, halted_path)`:
```python
# Line 660: halted_name = f"halted-{original_name}"
_cleanup_verdicts_for_slug(plan_slug)  # NEW
# Line 662: shutil.move(full_plan_path, halted_path)
```
**Justification:** Halted plans should have all pending requests removed. If a plan is halted at step 3 and steps 1–2 had verdict requests that were never cleaned, the sweep catches them.

### Why BEFORE the move, not after
Placing the sweep before `shutil.move` ensures that if the move fails (e.g., permission error, disk full), the pending requests are already cleaned — erring on the side of fewer stranded files. The race analysis (section 5) confirms no new requests can appear between the sweep and the move.

---

## 8. Edge Cases

### (a) Multiple pending verdicts for the same slug
A plan with N steps could have up to N verdict-request files (one per step that paused). The sweep uses `glob("verdict-request-{slug}-step-*.md")` which matches all of them. **Handled by design.**

### (b) Plan moved to Done while verdict write is in flight
In the auto-close path, no verdict is being written. In continue-to-done, the verdict for the final step has already been resolved and is being consumed — no in-flight write. **Not a real race.** However, if the sweep were called from outside `_consume_verdicts` (e.g., a manual cleanup script), this could be a concern. The proposed call sites are all within Bellows' single-threaded verdict-consumption flow, so this is safe.

### (c) Halted plans with already-resolved verdicts
If a plan is halted and its verdict requests were already consumed in prior steps, `glob()` returns no matches, sweep removes 0 files. **Harmless no-op.**

### (d) Slug prefix collision
Example: `foo-2026-04-19` vs `foo-bar-2026-04-19`. The glob pattern `verdict-request-foo-2026-04-19-step-*.md` does NOT match `verdict-request-foo-bar-2026-04-19-step-1.md` because the `-bar-` segment breaks the match. **No collision risk with glob.** However, the existing `_consume_verdicts` line 617 uses `plan_slug in pname` (substring match), which IS vulnerable to prefix collisions — but that's a pre-existing issue outside BACKLOG #9's scope.

### (e) Parallel plans with shared stem
Parallel plans get slugs like `parallel-1-executable-foo-2026-04-19`. The `parallel-N-` prefix is NOT stripped by `_slug_from_path`, so `parallel-1-executable-foo-2026-04-19` and `parallel-2-executable-foo-2026-04-19` produce different slugs. **No collision.**

### (f) Re-entrant _consume_verdicts
`_consume_verdicts` is called from `_rescan` (line 544) every 30 seconds. It iterates `os.listdir(resolved_dir)` and processes each file. If the sweep deletes pending files and the same `_consume_verdicts` iteration continues, no issue — each iteration processes a different verdict. **Thread safety note:** `_consume_verdicts` runs in the main thread (rescan loop), while `run_plan` runs in worker threads. The sweep (in `run_plan`'s auto-close path) and `_consume_verdicts`'s cleanup both write to `verdicts/pending/`, but they target different slug files (auto-close fires for the current plan; `_consume_verdicts` fires for whatever verdict was just resolved). **No contention in practice.**

---

## Recommended Executable Shape

### What to implement
1. **New function** `_cleanup_verdicts_for_slug(slug: str) -> int` in `bellows.py`:
   - Glob `BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{slug}-step-*.md"`
   - Delete each match via `Path.unlink()`
   - Return count of deleted files
   - Log deletions: `print(f"Bellows: cleaned {count} pending verdict(s) for {slug}")`

2. **Three call-site insertions** as described in section 7:
   - `run_plan()` auto-close path, before `shutil.move` (line ~359)
   - `_consume_verdicts()` continue-to-done path, before `shutil.move` (line ~644)
   - `_consume_verdicts()` halt path, before `shutil.move` (line ~661)

3. **Keep existing per-step cleanup** at lines 670–672 as belt-and-suspenders.

### Where it lives
- Single function addition + 3 one-line call-site insertions in `bellows.py`
- No changes to `verdict.py`, `gates.py`, or other modules

### Test verification
- **Unit test:** Create N mock `verdict-request-{slug}-step-{1..N}.md` files in a temp `verdicts/pending/` dir. Call `_cleanup_verdicts_for_slug(slug)`. Assert all N files deleted, return value == N. Assert files for a different slug are untouched.
- **Slug prefix collision test:** Create files for slugs `foo-2026-04-19` and `foo-bar-2026-04-19`. Sweep `foo-2026-04-19`. Assert `foo-bar-*` files are untouched.
- **Integration test:** Run a 2-step plan that pauses at step 1, receives "continue", then auto-closes at step 2. Verify `verdicts/pending/` is empty after completion.
- **Halted test:** Run a plan that pauses, receives "stop". Verify `verdicts/pending/` is empty after halt.
