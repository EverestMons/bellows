# Research — Plan File Truncation Trace
**Date:** 2026-04-17

## Summary

No code in `bellows.py`, `verdict.py`, `runner.py`, or `gates.py` writes to the plan file after it is claimed. All plan lifecycle transitions use `shutil.move` (filesystem rename — content-preserving). The truncation must originate from the executing agent subprocess (`claude -p`), which receives the plan file path in the bootstrap prompt, runs with `Write`/`Edit`/`Bash` tools, and is free to modify that path during step execution.

## Evidence

### All file writes in the Bellows codebase — none target the plan path

| Location | What it writes | Target path |
|---|---|---|
| `verdict.py:75` | verdict request metadata | `verdicts/pending/verdict-request-{slug}-step-{N}.md` |
| `verdict.py:119` | ledger JSONL entry | `verdicts/ledger.jsonl` (append) |
| `runner.py:20` | step JSON log | `logs/{timestamp}-step.json` |
| `planner.py:83` | planner consult file | `/tmp/bellows-consult-{uuid}.md` |
| `planner.py:100` | planner log | `logs/planner-consultation.jsonl` (append) |

No call to `write_text`, `open(..., "w")`, or `shutil.move` in any Bellows module targets a path derived from the plan file name.

### Plan lifecycle is rename-only

- `bellows.py:165` — `shutil.move(plan_path, inprogress_path)` — rename to `in-progress-`
- `bellows.py:228` — `shutil.move(inprogress_path, verdict_pending_path)` — rename to `verdict-pending-`
- `bellows.py:572` / `bellows.py:564` — rename back to `in-progress-` or to `Done/`

`shutil.move` between paths on the same filesystem is an `os.rename`; it never touches file content.

### Where re-reads happen (truncation would matter)

`_consume_verdicts` at `bellows.py:553` re-reads the plan from disk:
```python
plan_text_c = load_file(full_plan_path)   # full_plan_path = verdict-pending-{name}
total_steps_c = 1 if is_diag else extract_total_steps(plan_text_c)
```
If the agent modified the `in-progress-` file during step execution (before the rename to `verdict-pending-`), this read sees the modified — potentially truncated — content, producing a wrong step count and causing a 2-step plan to be treated as complete after step 1.

### Why the agent can do this

`runner.run_step` (`runner.py:29`) grants the subprocess `allowedTools: Read,Edit,Write,Bash`. The bootstrap prompt (`bellows.py:176-180`) passes the full absolute path of the `in-progress-` plan file. The agent's CWD is `project_path` (2 levels above `knowledge/decisions/`). Nothing prevents the agent from calling `Write` or `Edit` on the plan path — either because plan instructions explicitly tell it to "claim" the file, or inadvertently.

### Grep confirmation — no `open(.*plan.*"w")` matches

Running `grep -r 'open.*plan.*"w"\|write_text' bellows/*.py` returns only the entries listed in the table above; none resolve to the plan file path.

## Conclusion

The plan file content is not overwritten by Bellows itself. Truncation comes from outside Bellows — specifically the `claude -p` agent subprocess modifying the in-progress plan file via its file-editing tools during step execution. The fix would be to either (a) strip `Write`/`Edit` tool access for plan files at the runner level, or (b) Bellows re-reads plan content after step execution directly from the renamed `verdict-pending-` file, which it already does — meaning any mitigation must prevent the agent from being able to write to plan paths in the first place.
