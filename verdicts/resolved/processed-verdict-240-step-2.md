verdict: continue

**Rule 22(b) verified. The plan's own deliverable is clean — suite 2352 (2348 + 4, computed and exact), every code-facing row genuine, the forced-failure tests real. Rows 1-7 and 9-11 stand. ROW 8 IS CORRECTED BELOW: it under-reports its own command's output, and the Planner re-ran the scan. Because row 8 is informational (it feeds a CEO decision, it gates no code), the correction is supplied here rather than re-running the plan — precedent: plan 231's Planner-closed verification gap.**

## Row 8 corrected — the command shown returns 12 files; the table reported 4

Running the QA's own printed command against the same tree returns **12 files, not the 4 tabulated**. The mechanism is unknowable from the report (most likely a shell-quoting difference between what was printed and what actually ran — the printed command is not the run command, LESSONS 91's shape). The empirical map, Planner-verified twice by independent patterns:

**Files carrying the REAL username (8 tracked files, 24 occurrences):**

| File | Count | Reported by QA? |
|---|---|---|
| `knowledge/research/error log.txt` | **14** | **missed** |
| `knowledge/data/ingestion_log-export.json` | 3 | yes |
| `knowledge/handoff/fuel-ceiling-migration_20260720_011123.md` | 2 | yes |
| `knowledge/decisions/Done/diagnostic-windows-compatibility-2026-04-01.md` | 1 | yes |
| `knowledge/telemetry/fuel-coverage-20260717T151750Z.json` | 1 | **missed** |
| `scripts/check_contract_84_zips.py` | 1 | **missed** |
| `scripts/check_staleness_query.py` | 1 | **missed** |
| `scripts/inspect_contract_84_actions.py` | 1 | **missed** |

Benign pattern-only hits (fabricated examples, no real name): `Done/executable-239.md`, `tests/test_migrate_fuel_ceilings.py`, the QA report and its evidence file (all FAKEUSER or generic `C:\Users\...`).

## ⭐ The correction surfaced a NEW defect of exactly this plan's class

**`knowledge/telemetry/fuel-coverage-20260717T151750Z.json` — the plan-218 SANITIZED coverage export — carries `"db_path": "C:\\Users\\<username>\\invoice-..."`.** The coverage exporter emits its database path into its header, full and absolute, into an artifact whose entire purpose is to be the sanitized channel. **This is the identical leak class plan 240 just fixed in the migration script, live in a sibling tool** — the fifth instance of the sibling-file-same-defect pattern this project has hit (the label allocators, the `99.0` triplication, the G5 threshold, and now the db_path header twice).

Also surfaced: **three `scripts/*.py` carry hardcoded `DB_PATH = Path(r"C:\Users\<username>\...")`** — work-machine helper scripts swept into the repo by the Sync's `git add -A`.

**Both are Forward Register items, not fixes for this plan.** The coverage-exporter fix is small and should go through the drafting cycle as its own plan; the scripts question (parameterize vs gitignore vs accept) belongs with the CEO's remediation decision, which now has the real map.

## Why continue rather than stop

The deliverable this plan shipped — the migration-script fix — is verified clean end to end: the helper exists once and is pure, the abort paths are pinned by diff AND by `exit_code == 9` asserts, both forced-failure tests carry fabricated paths and presence assertions, and the suite delta is exact. Row 8's purpose is to inform the CEO, and that purpose is now served — better than the row itself served it. Stopping would re-run a 25-minute suite to regenerate a table this verdict has already corrected.

**Close plan 240. The username-exposure decision goes to the CEO with the corrected map: 8 tracked files / 24 occurrences in invoice-pulse, plus the redacted-live-but-present-in-history governance baton, plus both repos' git histories.**
