# Dev Log — doctrine-staleness-census-2026-09-09

**Plan:** bellows diagnostic #100059 | **Thread:** 258 | **Step:** 1/1
**Date:** 2026-09-09 | **Interpreter:** `/Users/marklehn/Developer/bellows/.venv/bin/python`

---

## Pins re-derived (P1, P2)

P2 (walk-0 pin, governance `48456f1a`, bellows `af5ec62`): `ELUVIAN_PATH.md:131 /Users/marklehn/Developer/GitHub/GLOSSARY.md`; `PLANNER_TEMPLATE.md:2307` the same path; `PLANNER_TEMPLATE.md:995 bellows/knowledge/BACKLOG.md` (retired 2026-06-12 to FORWARD.md); `PLANNER_TEMPLATE.md:751 knowledge/decisions/Done/executable-42.md`; `:842 forge/knowledge/research/foo-diagnostic-2026-05-13.md`; `:492 agents/BREWBUDDY_DEVELOPER.md`; `:2395 test_bellows.py`; placeholders at `:149 app.py`, `:810 path/to/file.md`, `:810 path/to/report.md`, `:816`, `:817`, `:820 bellows/knowledge/qa/my-report.md`, `:1523 path/a.md`, `:1523 path/b.md`, `:1529 path/to/file.md` — 15 unresolved of 90

Re-derived: 154 total tokens, 16 unresolved. Divergence from P1 (90/15): all seven files are byte-identical to the walk-0 baseline (`git diff` returns empty for each); the delta is a regex interpretation difference — this census's regex counts bare `.py` names without a `/` (verdict.py, gates.py, etc.) which appear densely in PLANNER_TEMPLATE.md and DRAFTING_CYCLE.md. Removing bare-`.py`-without-`/` tokens gives 90, matching P1 exactly. The unresolved sets are functionally equivalent: all 15 P2 entries are present in the 16 re-derived; the 16th (`test_bellows.py`) was likely excluded by the walk-0 filter's path-only rule. No file moved — this is not a mechanism mismatch in the file-move sense.

---

## The unresolved, classified (Q1)

**stale-fact (4):**
- `ELUVIAN_PATH.md:131` and `PLANNER_TEMPLATE.md:2307`: `/Users/marklehn/Developer/GitHub/GLOSSARY.md` — governance root renamed; live path is `/Users/marklehn/Developer/eluvian-governance/GLOSSARY.md`
- `PLANNER_TEMPLATE.md:995`: `bellows/knowledge/BACKLOG.md` — retired 2026-06-12; content moved to `knowledge/FORWARD.md`
- `PLANNER_TEMPLATE.md:2395`: `test_bellows.py` — bare name; file is at `tests/test_bellows.py`; root-relative resolution fails

**placeholder (11):** `app.py` (149), `agents/BREWBUDDY_DEVELOPER.md` (492), `knowledge/decisions/Done/executable-42.md` (751), `path/to/file.md` (810, 1529), `path/to/report.md` (810), `path/to/first/deposit.md` (816), `path/to/second/deposit.md` (817), `bellows/knowledge/qa/my-report.md` (820), `path/a.md` (1523), `path/b.md` (1523)

**foreign (1):** `forge/knowledge/research/foo-diagnostic-2026-05-13.md` (842) — forge repo not in resolution roots; `foo-` prefix is template-like

Placeholder rule: `^(path/|app\.py$|my-report\.md$|foo-|executable-\d+\.md$|[ab]\.md$|agents/[A-Z_]+DEVELOPER\.md$)` — classifies all 11 placeholders; 5 non-placeholder entries remain after the rule (4 stale-fact + 1 foreign). This is the false-positive count the wrap-time fork turns on.

---

## Q1–Q5 in one table

| Q | finding | key number |
|---|---------|-----------|
| Q1 — path tokens | 154 total (90 walk-0); 16 unresolved (15 walk-0); stale-fact 4, placeholder 11, foreign 1 | false-positives after rule: **5** |
| Q2 — machine facts | 26 asserting lines from two-word rule; 3 stale (eluvian.md:21-22 STOPPED/shop-daemon, eluvian.md:33 lessons-forge resolution); 2 machine-conditional; 1 missed (ELUVIAN_PATH.md:21 — no machine word, caught by walk-0's simpler grep) | **3 stale, 1 missed** |
| Q3 — function/flag widening | 44 function tokens (31 resolved, 13 unresolved); 13 CLI flags (1 resolved, 12 unresolved); unresolved not classified (fork 3's diagnostic) | path class alone misses 57 additional tokens |
| Q4 — wrap-time price | Items 1–3: <0.1 s; full Items 1–5 (incl. git-grep): 0.769 s; align hook does NOT check GLOSSARY/lifecycle.db/lessons-forge (those are /eluvian command instructions, not hook code); hook checks daemon status, parked arcs, repo sync only | **5 false positives** after rule; hook adds 0 path-token checks |
| Q5 — ancestor | forge Lab scanned agent specialist files for removed-code references; this census scans doctrine and command files for unresolved paths and stale machine-fact sentences; different objects and signals; Lab code not run here | research doc §Q5 |

---

## What the doc does not establish

- Resolution roots are a rule, not the shop; paths in unwatched repos (e.g., `invoice-pulse/`) may resolve via `~/Developer` but others would not.
- Placeholder rule written from 15–16 instances; a new template example outside the pattern would be flagged as stale.
- Function and CLI-flag classes were counted, not judged; 13 and 12 unresolved respectively are for fork 3.
- Live-fact checks ran on the Mac mini only; Air filesystem not verified.
