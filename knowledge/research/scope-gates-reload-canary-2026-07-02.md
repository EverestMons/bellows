# Scope-Gates Reload Canary Report
**Plan:** executable-scope-gates-reload-canary-2026-07-02

## Probe File

- **Filename created:** scope-probe-232046.md
- **Full path:** knowledge/research/scope-probe-232046.md
- **ls -la:** `-rw-r--r--  1 marklehn  staff  134 Jul  2 18:20 knowledge/research/scope-probe-232046.md`

## Discriminator Logic

The probe basename (scope-probe-232046.md) does not appear anywhere in the plan text; only the declared Scope prefix `knowledge/research/` can clear it through scope_check, so an all-PASS result proves the restarted daemon is running the new gates.py module (plan-118 + plan-119 changes).

## Output Receipt

```
status: PASS
step: 1
plan: executable-scope-gates-reload-canary-2026-07-02
probe_file: scope-probe-232046.md
probe_path: knowledge/research/scope-probe-232046.md
```
