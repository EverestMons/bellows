# Dev Log: Per-Plan Model Override + Gate 5 Backtick Fix

**Date:** 2026-04-17
**Plan:** executable-model-override-backtick-fix-2026-04-17.md
**Step:** 1 (DEV)

## Changes

### Commit 1 — Per-plan model override (`feat: per-plan model override via **Model:** header field`)

**Files changed:** `bellows.py`, `gates.py`

1. **gates.py** — `_parse_plan_header`: Added `key.strip("*")` and `value.strip("*").strip()` to strip markdown bold markers (`**`) from frontmatter keys and values. Without this, a `**Model:**` field would be stored with key `**Model` instead of `Model`.
2. **bellows.py** — `run_plan`: Added early header parsing via `gates._parse_plan_header(metadata_text)` immediately after `total_steps` extraction, before the first `runner.run_step` call. Model extracted with fallback chain: `header["Model"]` -> `header["model"]` -> `config["default_model"]`.
3. **bellows.py** — Both `runner.run_step` call sites (initial bootstrap and continuation loop) now pass `model` instead of `config["default_model"]`.
4. **bellows.py** — Added conditional print: `Bellows: using model override: {model}` when the plan overrides the default.
5. **runner.py** — Verified: already receives `model` as a parameter and passes it to `--model` in the `claude -p` command. No changes needed.

### Commit 2 — Gate 5 backtick strip (`fix: gate 5 — strip leading/trailing backticks from deposit paths`)

**Files changed:** `gates.py`

1. **gates.py** — `_extract_plan_required_deposits` Pattern 2: Added `.strip('`')` after the existing `.strip().rstrip('.,;)')` chain. Pattern 2 captures `\S+\.md` which can include leading backticks when the plan text uses backtick-quoted paths without the explicit backtick delimiters that Pattern 1 requires. The leading backtick caused `os.path.isfile` to always return False.
2. **gates.py** — `_gate_deposit_exists` line 139: Verified `path = line[2:].strip().strip('`')` already strips backticks from both ends (Python's `strip` removes from both ends). No change needed.
3. **Verification:** `python3 -c "print('\`invoice-pulse/knowledge/foo.md'.strip('\`'))"` produces `invoice-pulse/knowledge/foo.md`.

## Output Receipt

- **Status:** Complete
- **Tests:** Not run (no test files specified in plan for Step 1)
- **Commits:** 2 (dfb199f, 8d8a613)
