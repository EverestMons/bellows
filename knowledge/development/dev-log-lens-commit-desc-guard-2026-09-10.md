# Dev Log — lens-commit-desc-guard — 2026-09-10

Plan #100068 · thread 271

## Pins re-derived (P2, P3)

**P2 — the observer's tokens:**

`scripts/lens_order_check.py:70` `_WALK_RE = re.compile(r"\bwalk\s+(\d+)\b", re.IGNORECASE)`; `:76` `_LENS_RE = re.compile(r"\blens\s+(\d+(?:\s*/\s*\d+)*)", re.IGNORECASE)`; `:82` `_CONT_RE`; `commit_record` `:92` applies both to every subject and keeps a row when BOTH match

**P3 — lens_commit.py step 4 and --desc census:**

Step 4 (`:275–280` on bellows `ba74706` / P3 sha `b4644b8ab55d`):
```
    # Step 4: compose + assert subject
    composed_name = LENS_NAMES[lens_n]
    expected_name = _NAMES[lens_n]
    if composed_name != expected_name:
        print(f"LENS-COMMIT: assert FAIL — LENS_NAMES[{lens_n}]={composed_name!r} != expected {expected_name!r}")
        return 1
    subject = f"draft({slug}): walk {walk_n} lens {lens_n} — {composed_name}: {desc}"
```

`desc = args.desc` at `:96`, never inspected before this plan.

`--desc` census (19 tests, l1–l16 with l6b/l7b/l7c): `test` ×6, `fold` ×4, `dry` ×3, `test fixture` ×2, `echo-test` ×2, `fail-test` ×1, `folded` ×1, `escalation` ×1, `walk-close` ×1, `b-check`-shaped — none carrying a lens or walk token. Guard does not disturb any existing test.

No mechanism mismatch: the regexes at lines 70 and 76 match the plan's P2 value cell exactly; step 4 `:275–280` matches P3; `desc` is never inspected before step 4.

## Failing-first (two red, one pinned, then green)

Three tests written against the unedited fixture before the edit:

**l17** (`--desc "QA lens 2"`, `--dry`): expected rc 1. Before edit → `FAILED` (rc 0, "commit OK" on `draft(plan): walk 1 lens 1 — Weak spots: QA lens 2`). After edit → `PASSED`.

**l18** (`--desc "walk 0 seed"`, `--dry`): expected rc 1. Before edit → `FAILED` (rc 0, "commit OK" on `draft(plan): walk 1 lens 1 — Weak spots: walk 0 seed`). After edit → `PASSED`.

**l19** (`--desc "lenses and walks in prose, lens-2 style"`, `--dry`): expected rc 0 and "commit OK". Before edit → `PASSED` (pinned — this description has no observer token; the guard must not widen past the observer's reading). After edit → still `PASSED`.

l1–l16 (plus l6b, l7b, l7c): all `PASSED` before and after the edit.

Full file after edit: 23 passed. Full suite: 2227 passed, 1 skipped.

## The class reproduced on the fixture (Item 1)

Ran the pre-edit shipped tool (`ba74706`) against a temp fixture with `--walk 1 --lens 5 --desc "QA lens 2"`:

```
LENS-COMMIT: commit OK — draft(plan): walk 1 lens 5 — ACID: QA lens 2
```

Then `lens_order_check.py plan.md --repo <fixture>`:

```
BATCHED: walk 1 — 63fbada names lenses [5, 2] in ONE commit — §2.7 requires one commit per lens: draft(plan): walk 1 lens 5 — ACID: QA lens 2
OUT-OF-ORDER: walk 1 — lens commits land in order [5, 2], which does not ascend — a later lens read the draft before an earlier lens folded
```

The incident's class is reproduced: the pre-edit tool commits the subject `… lens 5 — ACID: QA lens 2`; the observer reads lenses [5, 2] in one commit and reports BATCHED.

## Mutation run

Manifest: `knowledge/mutants/lens-commit-desc-guard.json` (3 mutants, target `scripts/lens_commit.py`).

```
PYTHON: /Users/marklehn/Developer/bellows/.venv/bin/python
HEAD: 14e4157080eb729546efe793ae22db708966fee2
TARGET: scripts/lens_commit.py sha256=4cb05841e3c5

MUTANT guard-removed: KILLED — suite caught the defect
MUTANT walk-half-removed: KILLED — suite caught the defect
MUTANT guard-widened-bare-lens: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: scripts/lens_commit.py sha256=4cb05841e3c5

MUTATION: 3 killed, 0 survived, 0 error
```
