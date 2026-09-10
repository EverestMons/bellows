# Dev log — lens-record-visibility — 2026-09-10

Plan id: 100063 | Thread 270

## Pins re-derived (P2, P3, P4, P5)

**P3 (the tool's commit step, pre-edit, verbatim from the plan):**

`scripts/lens_commit.py:129–155`: `repo_dir = draft_path.parent`; `to_add = [str(register_path.resolve())]`; `bpath = _baseline_path(draft_path)` appended when a file; `git -C repo_dir add <to_add>`; `git commit -m <subject>`; the DRAFT is never added; nothing is written to the register; the docstring `:9–13` lists five steps with `5. commit — git add register + baseline, commit with composed subject`; `:110–113` the `--allow-yield-rising` WARN line appended to the register INSIDE step 3; `Done/executable-100061.md` item 2 specified `committing the draft, register and baseline` and its P6 hand shape was `git add <draft> <register> <baseline>` — the shipped tool dropped the draft against its own spec, uncaught by l1–l5 (none reads `git show --stat`; scout S3); `LENS_NAMES` `:24–30`

**P3 post-edit (what shipped):** step 0 (record check, lines 113–223) added before step 1; `--dry` flag added (line 85); `slug`, `draft_resolved`, `register_resolved`, `repo_dir` resolved before step 0 (lines 108–111); step 5 now appends the DRY line when `args.dry and not register_changed` (lines 270–276); `to_add = [str(draft_resolved), str(register_resolved)]` (line 278) — the draft rides every commit.

**P2 (observer seams, current):** `grep -n 'def \|_merge_by_time(rows\|commit_record_paths(repo' scripts/lens_order_check.py` → `commit_record` :92; `commit_record_paths` :125; `_merge_by_time` :157; `_repo_of` :174; `_draft_from_fold_baseline` :185 (new); `register_commit_record` :210; `declared_walks` :246; `main` :330; `commit_record_paths(repo, [draft, reg_path])` :362; `_merge_by_time(rows, reg_rows)` :367.

**P4 (resolver signature, current):** `cycle_check.resolve_fold_baseline(plan_path, manifest=None) -> (path_or_None, declared)` at :818. Resolution order: (1) `fold_baseline:` field via `_resolve_register_ref`; (2) beside-the-plan `.{name}.foldcheck.json`. A declared ref that doesn't resolve returns `(None, True)` with no silent fallback. A non-declared plan falls through to beside-the-plan only.

**P5 (tests as they stand, post-edit):** `tests/test_lens_order_check.py` — 24 tests; helpers `_git` :22, `_plan_text` :26, `_repo` :52, `_run` :66, `_repo_with_register` :208, `_two_repos` :383 (new); `tests/test_lens_commit.py` — 15 tests (l7c counts as 2 parametrize items = 16 items); helpers `_git` :64, `_make_lens_fixture` :69; `tests/test_depositor_lens_order_gate.py` — 6 tests, all through stubbed subprocess, untouched. Total in the two edited files: 39 passed.

## Failing-first (red or pinned, then green)

Tests written before the edit. Run against the unedited files — outcome before the edit:

- **l1, l3 (both calls), l4**: `argparse` raised `SystemExit: 2` on the unknown `--dry` flag — pytest reported FAILED/SystemExit before reaching the intended assert.
- **l6** (`test_l6_dry_lens_appends_row_and_commits_three_files`): `SystemExit: 2` (no `--dry` flag yet); then after flag added: rc 0 but register text did not end with the DRY line, and `plan.md` absent from `git show --name-only` output.
- **l7** (`test_l7_fold_without_row_refuses`): rc 0 and a commit made — no step-0 record check.
- **l7b** (`test_l7b_dry_over_fold_refuses`): `SystemExit: 2` (no `--dry`); then after flag added: rc 0, no refusal.
- **l7c** (both parametrize variants): same as l7b.
- **l6b** (`test_l6b_walk_closing_shape_admitted`): `SystemExit: 2`; then after flag: rc 1 — the `**Walk N —` shape was not in the accepted set.
- **l8** (`test_l8_fold_with_row_commits_three_files`): rc 0 but `plan.md` absent from `--name-only` (draft not in `to_add`).
- **l9** (`test_l9_register_not_committed_refuses`): rc 0 — no in-HEAD check.
- **l10** (`test_l10_duplicate_dry_run_refuses`): second run rc 0 — no duplicate guard.
- **l11** (`test_l11_mode_change_vacuity_refuses`): rc 0 — no vacuity check.
- **o1** (`test_o1_deposited_copy_reads_ok_through_fold_baseline`): rc 1, INCOMPLETE — `_draft_from_fold_baseline` did not exist; time-merge produced the hold.
- **o2** (`test_o2_without_fold_baseline_merges_by_time_and_holds`): GREEN before the edit — pins today's reading.
- **o3** (`test_o3_fold_baseline_nonexistent_no_traceback`): GREEN before the edit — pins today's reading (fallback to time-merge on any exception).
- **o4** (`test_o4_draft_missing_note_and_fallback`): rc 1 but no NOTE line in stderr — helper not yet written.
- **o4b** (`test_o4b_draft_is_directory_missing_note`): same; no NOTE.
- **o4c** (`test_o4c_draft_unreadable_note_and_no_traceback`): no NOTE and a traceback would have been possible — the `try/except OSError` not yet written.
- **o5** (`test_o5_foreign_pointer_register_ref_differs`): four verdict asserts green, but the `register ref differs` NOTE assert failed — identity tie not yet checking; the foreign draft's commits would have been unioned in.

After the edit: all 39 tests in the two files passed. Full suite: 2203 passed, 1 skipped.

## The pointer resolves from a project path (Item 1)

Harness (five lines, tmp copy of the #265 draft):

```
T=$(mktemp -d)
cp /Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/executable-bellows-lint-warn-to-fail.md $T/x.md
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path; import cycle_check, os
print(cycle_check.resolve_fold_baseline(Path(os.environ['T'] + '/x.md')))
"
```

Result:

```
(PosixPath('/Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/.executable-bellows-lint-warn-to-fail.md.foldcheck.json'), True)
```

The governance-root resolution step reached the file from the worktree path. Item 2's premise holds on this machine.

## Mutation run

Manifest: `knowledge/mutants/lens-record-visibility.json` — 14 mutants (10 targeting `scripts/lens_commit.py`, 4 targeting `scripts/lens_order_check.py`).

Run command: `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/lens-record-visibility.json > knowledge/mutants/lens-record-visibility.run.txt 2>&1`

The `dry-append-removed` mutant initially errored with `anchor matched 0 times` — the anchor was written with 8-space indentation for `if args.dry and not register_changed:` where the actual code uses 4 spaces (the block is a top-level `main()` statement, not nested inside another `if`). Anchor corrected to 4-space indent; replacement corrected to match (`    pass  # mutant: DRY append removed`).

Final result: `MUTATION: 14 killed, 0 survived, 0 error`

All 14 mutants killed. Gate satisfied (`≥14 killed, 0 survived, 0 error`).
