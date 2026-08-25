# QA Report — issue_verdict tool + daemon verdict-detector arms (plan 524)

**Date:** 2026-08-25 | **Plan:** executable-524 | **Step:** 2 (QA)

## Q1 — Full Suite

```
python3 -m pytest tests/ -q
1412 passed, 1 warning in 47.12s
```

- **Total collected:** 1412
- **New file (test_issue_verdict.py):** 27 tests
- **Inherited baseline:** 1412 − 27 = 1385 (matches Y8 floor of 1385)
- **Failures:** 0

Raw output deposited: `pytest_full.txt`.

## Q2 — Live Tool Rehearsal (scratch-only)

All runs against a temp dir via `--pending-dir` / `--resolved-dir` overrides — never the live `verdicts/` tree.

**Run 1 — issue_verdict continue:**
```
$ python3 tools/issue_verdict.py 999 1 continue --reason "rehearsal" --pending-dir "$TMP/pending" --resolved-dir "$TMP/resolved"
outcome: continue
file: .../resolved/verdict-999-step-1.md
Exit code: 0
```

Verification: `verdict-999-step-1.md` exists in resolved/ with first line exactly `continue`, permissions `0644`.

**Run 2 — without --force (expect refusal):**
```
$ python3 tools/issue_verdict.py 999 1 continue --reason "retry" --pending-dir "$TMP/pending" --resolved-dir "$TMP/resolved"
ERROR: verdict file already exists (not consumed yet): .../resolved/verdict-999-step-1.md — use --force to overwrite
Exit code: 1
```

**Run 3 — with --force (expect success):**
```
$ python3 tools/issue_verdict.py 999 1 continue --reason "forced" --pending-dir "$TMP/pending" --resolved-dir "$TMP/resolved" --force
outcome: continue
file: .../resolved/verdict-999-step-1.md
Exit code: 0
```

All three rehearsal outcomes match spec.

## Q3 — Change-Shape Check

| Check | Command | Expected | Actual | Status |
|---|---|---|---|---|
| VERDICT_FIRST_LINE_RE in verdict.py | `grep -cF "VERDICT_FIRST_LINE_RE" verdict.py` | 2 (definition + usage) | 2 | ✅ |
| Used inside check_verdict | `grep -nF "VERDICT_FIRST_LINE_RE" verdict.py` | :16 (def) + :303 (use) | :16, :303 | ✅ |
| bellows.py references in auto-move | `grep -nF "VERDICT_FIRST_LINE_RE" bellows.py` | present | :2755 | ✅ |
| EVENT literal exactly once | `grep -cF "auto-moved well-formed verdict to resolved/" bellows.py` | 1 | 1 | ✅ |
| Full WARN with first_line exactly once | `grep -c 'first line:' bellows.py` (in WARN context) | 1 | 1 (line 2856) | ✅ |
| Base WARN phrase total | `grep -c 'verdict file exists but does not parse as a verdict' bellows.py` | 2 (per S3-6) | 3 (see note) | ✅ |
| No daemon imports in tool | `grep -cE "^(import\|from) (verdict\|bellows\|notifier\|requests\|lifecycle)\b" tools/issue_verdict.py` | 0 | 0 | ✅ |

**Note on base WARN phrase count (3 vs S3-6's predicted 2):** The B3 spec says "Guard the read (unreadable/empty file → log without the first-line clause)." The DEV implementation correctly separates the three cases: (1) readable with content → log with first_line (line 2856), (2) readable but empty → log without (line 2858), (3) exception reading → log without (line 2860). The plan's S3-6 grouped both guard paths as one "without" clause when predicting count=2; the actual count of 3 is the correct implementation of B3's guarding spec. No behavioral defect.

## G1-G7 Coverage and Verification Table

| Gap | Target | What shipped | Status |
|---|---|---|---|
| G1 | tools/issue_verdict.py | Tool created: argparse CLI, id derivation, atomic write, self-verify, stdlib-only | ✅ |
| G2 | tests/test_issue_verdict.py | 27 tests: happy path, id derivation, normalization, enum/overwrite refusals, --force, atomicity, self-verify, regex byte-identity, reason sources, daemon integration (13/13b/14/15) | ✅ |
| G3 | bellows.py auto-move arm | Auto-move of parse-valid misplaced files with 4-condition gate (filename, content, destination-free, freshness via active request) | ✅ |
| G4 | bellows.py malformed WARN | WARN promotion at consumption not-found site with first-line content (Fork 2+5) | ✅ |
| G5 | tests (daemon auto-move) | Test 13 (auto-move + EVENT logged) and test 13b (stale duplicate NOT moved — condition-iv freshness gate) | ✅ |
| G6 | tests (malformed WARN) | Test 14 (parse-invalid NOT moved + WARN persists) and test 15 (malformed WARN with first-line content via capsys) | ✅ |
| G7 | knowledge/glossary.md | DEFINITION entry `## verdict act` shipped (S1-1 recast: definition form, matching `## release act` precedent) | ✅ |
| G8 | ~/.claude memory entry | Planner's post-close act — out of sandbox reach by design; NOT in this plan's write set | N/A |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/524/knowledge/qa/evidence/issue-verdict-tool/
Files verified: 2
```
