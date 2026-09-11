# dev-log — action-census-2026-09-11 [100085] [thread 293]

## Pins re-derived (P2, P3, P5)

P5's value cell, verbatim: `steps` 143 rows: 137 carry `cost_usd`, 139 carry `duration_s`; by `step_number` (n, mean `cost_usd`, mean minutes): 1 → 80, $2.631, 17.2; 2 → 55, $1.395, 8.7; 3 → 2, $0.938, 5.2; per plan (sum of its steps): `executable` 65 plans mean $3.949, `diagnostic` 15 plans mean $2.156; `plans` by state: closed 71, halted 11, abandoned 3, in_progress 1; `verdicts` 141 rows by `decided_by`: `verdict_file` 121, `gate_auto` 18, `gate_recheck` 2; `gate_events` 1289 rows; 14 tables (`clearances, commits, deposits, derivations, diagnostic_meta, executable_meta, gate_events, id_sequence, ledger_writes, plans, prompt_feedback, steps, step_files, verdicts`) — NO table prices a Planner session, a wrap, a release or a restart

Re-derived values (read 2026-09-11, mode=ro, data_version=2 before and after):
- `tools/*.py`: 20 files (P2 said 20 — MATCH); `grep -l argparse` → 15 (P2 said 15 — MATCH)
- `scripts/*.py`: 13 files (P2 said 13 — MATCH); `grep -l argparse` → 6 (P2 said 6 — MATCH)
- `grep -cF '_log("EVENT"' bellows.py` → 22 (P2 said 22 — MATCH)
- `grep -cF '@mcp.tool' server/tools.py` → 9 (P3 said 9 — MATCH)
- `grep -n noop_echo tuyere/handlers.py` → `HANDLERS = {"noop_echo": noop_echo}` (P3 said one handler — MATCH)
- tuyere commands: claims 3, enqueue 3, threads 9, wraps 2, control 4 subcommands (P3 match)
- steps total: **147** (P5 said 143 — moved: 4 steps ran since drafting); cost_usd: 141 (P5: 137); duration_s: 143 (P5: 139)
- step_number 1: n=87 (P5: 80), mean=$2.847 (P5: $2.631), mean_min=18.3 (P5: 17.2) — counts moved, both figures stated
- step_number 2: n=58 (P5: 55), mean=$1.451 (P5: $1.395), mean_min=9.1 (P5: 8.7) — counts moved
- step_number 3: n=2 (P5: 2 — MATCH), mean=$0.938 (MATCH), mean_min=5.2 (MATCH)
- executable plans: 71 (P5: 65), mean plan cost $4.109 (P5: $3.949) — 6 more plans closed since drafting
- diagnostic plans: 17 (P5: 15), mean plan cost $2.156 (P5: $2.156 — MATCH on mean)
- plans by state: closed 73 (P5: 71), halted 11 (MATCH), abandoned 3 (MATCH), in_progress 1 (MATCH)
- verdicts by decided_by: verdict_file 124 (P5: 121), gate_auto 19 (P5: 18), gate_recheck 2 (MATCH)
- gate_events: 1341 (P5: 1289) — no mechanism mismatch; counts moved because plans ran between drafting and read
- tables: 15 (P5 said 14; the read found sqlite_sequence as the 15th — system table, not listed in P5's named 14)

No mechanism mismatch: every count that moved is a plan running since drafting (P8 stated this in advance). The `sqlite_sequence` table is a system table absent from P5's named list; not a mismatch in the depositor or gate logic sense.

## The two shares (Q5)

Total rows: 126 (127 TSV lines including header).

**All rows:**
- model-run + mixed: 19/126 = 15.1%
- model-run alone: 13/126 = 10.3%
- deterministic: 107/126 = 84.9%

**Plan cost share (lifecycle DB):**
- 100% of recorded dollars (cost_usd) are model-run; deterministic acts cost $0 in the DB
- Deterministic timed seconds for one plan's life: ≈22 s (deposit ≤12 s + restart ≈9 s + release ≈1 s); gate evaluation, merge, and verdict file write are not timed

**CEO-keyboard rows (71 rows):**
- model-run + mixed: 10/71 = 14.1%
- model-run alone: 8/71 = 11.3%
- deterministic: 61/71 = 85.9%

## Q1–Q5 in one table

See `governance/knowledge/research/action-census-2026-09-11.md` for Q1–Q5 in full and `action-census-2026-09-11.tsv` for one row per act. Summary:

| Q | finding |
|---|---|
| Q1 (inventory) | 126 rows across 13 surfaces; 71 CEO-keyboard, 28 daemon, 24 Planner-session |
| Q2 (classification) | 107 deterministic, 13 model-run, 6 mixed |
| Q3 (price) | $2.847 mean DEV step, $1.451 mean QA step, $2.156 mean DIAGNOSTIC step; deterministic acts: $0 in DB |
| Q4 (reachability) | 100 rows keyboard+ssh; 26 keyboard-only; 9 mcp; 1 intent; tuyere.control keyboard-only by GOVERNANCE |
| Q5 (shares) | 15.1% (model-run+mixed)/all; 100% of DB dollars model-run; 14.1% CEO-keyboard rows model-run+mixed |

## What the doc does not establish

- Planner session token cost (no DB table records it)
- CEO's time per act
- Hub auth model (292's decision)
- Whether any act should be a button (292's decision — no recommendation made)
- Durations from one day's log are one sample
- Air's rows (mini's inventory by MACHINE_SETUP symmetry; not directly read on the Air)
- Reverse ssh (Air → mini) not yet proven; Air Remote Login unread from this machine
- Handler map beyond noop_echo (thread 78 deferred)
