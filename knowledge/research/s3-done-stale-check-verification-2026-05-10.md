# S3 Done/ Stale-Check Verification — 2026-05-10

**Diagnostic:** diagnostic-s3-done-stale-check-verification-2026-05-10
**Date:** 2026-05-10
**Type:** Read-only investigation (single step)

---

## Q1. Current Code State

The Done/ stale-check lives at `bellows.py:1033-1058` inside `_consume_verdicts()`. Verbatim:

```python
            else:
                # No match — check if plan is already in Done/ OR halted in decisions/ (stale verdict)
                stale = False
                for decisions_path in search_dirs:
                    done_dir = os.path.join(decisions_path, "Done")
                    if os.path.isdir(done_dir):
                        for dname in os.listdir(done_dir):
                            if plan_slug in dname:
                                stale = True
                                break
                    if stale:
                        break
                    # Also check decisions/ itself for halted-* plans (S3 Bug C fix)
                    if os.path.isdir(decisions_path):
                        for dname in os.listdir(decisions_path):
                            if dname.startswith("halted-") and plan_slug in dname:
                                stale = True
                                break
                    if stale:
                        break
                if stale:
                    processed_path = resolved_dir / f"processed-{fname}"
                    shutil.move(str(resolved_dir / fname), str(processed_path))
                    print(f"Bellows: ⚠️  stale verdict for {plan_slug} step {step_number} — plan in Done/ or halted-, moving to processed")
                else:
                    print(f"Bellows: ⚠️  no verdict-pending plan found for {plan_slug} step {step_number} — leaving in resolved/ for retry")
```

**Slug-matching logic:** `if plan_slug in dname` — Python substring match via `in` operator. Position-independent, non-regex. `plan_slug` is parsed from the verdict filename by regex `^verdict-(.+)-step-(\d+)\.md$` (line 913).

**Search scope:** `search_dirs` is either `[scoped_decisions_path]` (if pending request file existed and declared a `**Plan:**` path) or all `config["watched_projects"]` entries as fallback (line 957).

---

## Q2. Git History

Commits touching `bellows.py` between 2026-05-07 and 2026-05-11:

| SHA | Date | Summary | Modified Done/ stale-check? |
|-----|------|---------|---------------------------|
| `e5188fa` | 2026-05-08 | qa-prefix dispatch | No |
| `afc8523` | 2026-05-08 | pipe-header-parser | No |
| `dc0bdd7` | 2026-05-09 | S3 Bug A/B fix (format-tolerant check_verdict + verdict-request- exclusion) | No — added `if fname.startswith("verdict-request-"): continue` at line 910, upstream of the stale-check |
| `8eac4c3` | 2026-05-10 | teardown lock detection | No |
| `db78919` | 2026-05-10 | S3 Bug C fix (halted-* stale-check) | **Yes** — extended the stale-check to also search `halted-*` plans in decisions/ |

**Critical finding:** The Done/ stale-check was introduced in commit `c7f69f3` on **2026-04-24** as part of "reliability bugs 1-3" (verdict consume gate fix). It was NOT added between 2026-05-08 and 2026-05-10. The check has been present for 16 days before the 2026-05-08 BACKLOG entry was written.

---

## Q3. Pre-Fix State

Pre-`c7f69f3` (i.e., at commit `c7f69f3^`), `_consume_verdicts` had NO conditional on plan matching. The tail of the per-verdict loop was:

```python
                        break  # only one match per verdict

            # Clean up pending verdict request file — stale after verdict consumption
            pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
            if pending_file.exists():
                pending_file.unlink()

            # Move the verdict file out of resolved to prevent re-processing
            processed_path = resolved_dir / f"processed-{fname}"
            shutil.move(str(resolved_dir / fname), str(processed_path))

    def start(self):
```

**Key insight:** Before `c7f69f3`, verdict files were moved to `processed-*` **unconditionally** regardless of whether a matching `verdict-pending-*` plan was found. There was NO retry-loop behavior possible — every verdict was consumed on first scan. The `plan_matched` boolean gate AND the Done/ stale-check were introduced simultaneously in `c7f69f3`.

**Therefore:** The retry-loop described in the 2026-05-08 BACKLOG entry could only exist on code running AFTER `c7f69f3` (2026-04-24). Since the Done/ stale-check was part of the same commit that introduced the conditional logic creating the retry-loop, the Done/ stale-check has been present for the entire lifetime of the retry-loop behavior.

---

## Q4. Slug Matching Analysis

**(a) Standard case:** `plan_slug = "executable-foo-2026-05-08"`, `dname = "executable-foo-2026-05-08.md"`. Evaluation: `"executable-foo-2026-05-08" in "executable-foo-2026-05-08.md"` is `True`. Correct.

**(b) cleanup_slug case:** Verdict file `verdict-executable-foo-2026-05-08-step-2.md` parses to `plan_slug = "executable-foo-2026-05-08"`. Done/ file `executable-foo-2026-05-08.md`. Evaluation: `"executable-foo-2026-05-08" in "executable-foo-2026-05-08.md"` is `True`. Correct. Note: `plan_slug` includes the lifecycle-type prefix (`executable-`/`diagnostic-`), which matches the Done/ filename (also includes the prefix). No mismatch.

**(c) Prefix-collision edge case:** `plan_slug = "executable-foo-2026-05-08"`, `dname = "executable-foo-extended-2026-05-08.md"`. Evaluation: `"executable-foo-2026-05-08" in "executable-foo-extended-2026-05-08.md"` is `True`. This IS a false-positive stale match. **However, this fails SAFE:** the verdict gets moved to `processed-*` (consumed), not left in `resolved/` for retry. The consequence is that a legitimate verdict for the shorter-named plan would be prematurely consumed if a longer-named plan happened to be in Done/. In practice, slug naming conventions (plan-specific names with full date suffixes) make substring collisions between distinct plans extremely unlikely. No known occurrence in 56+ historical ledger entries.

**(d) Regex-special characters:** Python's `in` operator performs literal substring matching — it is NOT regex-based. Characters like `.`, `*`, `+`, `(`, `)` in `plan_slug` are treated as literal characters. Safe unconditionally.

---

## Q5. Empirical Data

**Current `verdicts/resolved/` state (non-processed):**
- `_PLANNER_RECALLED_verdict-action-queue-aggregation-2026-05-07-step-3.md` — does NOT start with `verdict-`, skipped by filter at line 908
- `verdict-request-billto-extraction-architecture-2026-05-07-step-1.md` — starts with `verdict-request-`, skipped by filter at line 910-911
- `verdict-request-pipe-header-parser-and-comprehensive-qa-2026-05-08-step-2.md` — same, skipped

**No stuck verdict files.** Zero evidence of active retry loop.

**Current `verdicts/pending/` state:**
- 4 verdict-request files (legitimate pending requests for active/paused plans)
- `archived/` subdirectory

**Done/ cross-check:** No verdict file in `resolved/` has a slug matching a plan in Done/ — the stale-check has no work to do at present.

**2026-05-08 reproduction files:** The BACKLOG entry does not name specific files. Based on the S3 Bug A diagnosis (below), the 2026-05-08 symptoms were caused by `verdict-request-*` files being processed as verdict files — their parsed `plan_slug` would start with `request-` and match nothing in Done/. These files would have been the `verdict-request-*` files that existed in `resolved/` at the time (now either archived or excluded by the `dc0bdd7` filter).

---

## Q6. Recommendation

### Classification: **(i) Structurally fixed (close as superseded)**

**Reasoning:**

The Done/ stale-check was introduced on **2026-04-24** in commit `c7f69f3` as part of the same atomic change that created the `plan_matched` conditional (which is what enables retry-loop behavior). The check has never been absent while the retry-loop was possible.

The 2026-05-08 BACKLOG symptoms ("retry loop when target plan in Done/") were caused by **S3 Bug A** (fixed 2026-05-09 in `dc0bdd7`): before that fix, `verdict-request-*` files in `resolved/` were not excluded from processing. The regex `^verdict-(.+)-step-(\d+)\.md$` would parse `verdict-request-foo-step-1.md` as `plan_slug = "request-foo"` — a slug that matches nothing in Done/ (actual Done/ filenames are `executable-foo.md` or `diagnostic-foo.md`). This produced the infinite retry-loop for misclassified verdict-request files.

The separate S3 Bug C (halted-* plans not searched, fixed 2026-05-10 in `db78919`) addresses a different failure mode that was not described in the 2026-05-08 BACKLOG entry.

**Closure citation:** The Done/ stale-check for the exact scenario described in the 2026-05-08 BACKLOG entry (plan legitimately in Done/) has been present since commit `c7f69f3` (2026-04-24). The actual 2026-05-08 symptoms were fixed by `dc0bdd7` (2026-05-09, S3 Bug A). BACKLOG entry is stale — close as superseded.

---

## Verdict

**(i) Structurally fixed (close as superseded).** The Done/ stale-check was introduced on 2026-04-24 in commit `c7f69f3`, simultaneously with the conditional logic that enables retry-loop behavior. The 2026-05-08 symptoms were caused by S3 Bug A (verdict-request- prefix not excluded from processing), fixed 2026-05-09 in commit `dc0bdd7`.

---

## Confidence

| Claim | Confidence | Evidence that would raise it |
|-------|-----------|------------------------------|
| Done/ stale-check introduced in c7f69f3 (2026-04-24) | HIGH | Verified via `git show c7f69f3 -- bellows.py` — the `plan_matched` boolean + Done/ check are in the same diff hunk |
| 2026-05-08 symptoms caused by S3 Bug A (verdict-request parsing) | HIGH | `dc0bdd7` adds exactly the `verdict-request-` exclusion filter; BACKLOG S3 Bug C entry (2026-05-09) explicitly states "Confirmed live on 2026-05-09 after the S3 Bug A/B fix shipped" for the halted-* variant, implying the Done/ variant was already resolved |
| No current retry loop active | HIGH | `ls verdicts/resolved/` shows zero `verdict-*` files matching the processing regex (all are `verdict-request-*` or `_PLANNER_RECALLED_*`, both excluded by filters) |
| Substring match (Q4c) is safe in practice | MEDIUM | No historical collision observed in 56 ledger entries; would require two plans with overlapping slug substrings to be active concurrently. Observation that would lower confidence: a real plan slug collision producing a false stale detection |

---

## Rule 20 Self-Check

```
Rule 20 — QA Self-Check Results
========================================
  s3-done-stale-check-verification-2026-05-10.md: FOUND
  QA report (bellows/knowledge/research/s3-done-stale-check-verification-2026-05-10.md): FOUND
  Hedging keywords: none detected

PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
