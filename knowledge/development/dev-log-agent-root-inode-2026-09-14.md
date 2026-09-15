# Dev log — agent-root-inode (bellows #100106, thread 324)

## Pins re-derived (P1, P4)

`tests/test_daemon_agent.py`: 12 tests, 273 lines, a newline at its end; `import dashboard` before `import bellows` (:15–16); t5 (:84–97) patches `_agent_root` to return `str(tmp_path)`, with `create=True`; t9 :210–221 (its separator :210, its `def` :211) asserts the same directory True, the same basename under another parent False and no agent False, its docstring naming the realpath comparison; t10 (:224) patches `_agent_root` to return `str(tmp_path / "elsewhere")`, which does not exist, and asserts a child spawned and no kickstart; t11 asserts the kickstart with `replace=False` for the dashboard's own root; t12 :259–273, the file's last test

P1 re-derived (bellows.py):
- `:204` `def _agent_owns_root(root, label="com.eluvian.bellows-daemon"):`
- `:205` `"""Return True if the named agent's working directory is \`root\`."""`
- `:206` `r = _agent_root(label)`
- `:207` `return r is not None and os.path.realpath(r) == os.path.realpath(str(root))`

No mechanism mismatch: `samefile` not already in the helper; no t13 in the file; `_spawn_child` at `dashboard.py:451` still calls `_agent_owns_root`.

## Failing-first (red, then green)

Red (unedited helper, new tests):
`2 failed, 11 passed in 0.77s`

Green (test file after helper edit):
`13 passed in 0.38s`

Green (full suite):
`2432 passed, 2 skipped, 9 warnings in 234.83s (0:03:54)`

## The comparison observed (t9, t13)

```
tests/test_daemon_agent.py::test_t9_agent_owns_root_compares_by_inode PASSED [ 50%]
tests/test_daemon_agent.py::test_t13_agent_owns_root_case_variant_spelling PASSED [100%]
```

## Mutation run

`MUTATION: 3 killed, 0 survived, 0 error`
