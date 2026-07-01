stop

Same 401 infra blocker (3rd occurrence), NOT a plan failure. #105 Step-1 (invoice-list build) failed in ~2s: claude -p → 401 authentication_failed, apiKeySource: none, files_changed=0 — the DEV agent never ran. Root cause confirmed in runner.py: claude -p is spawned via subprocess.Popen(cmd, cwd=project_path) with NO env= and nothing sets ANTHROPIC_API_KEY, so children inherit the daemon's environment verbatim. The daemon's launch context has no usable credentials → every child 401s; restarting from that same context inherits the same empty auth.

Fix is environmental (daemon launch context needs valid creds): either launch the daemon from a shell where `claude -p "ok"` succeeds, or set ANTHROPIC_API_KEY in the daemon's environment before launch. Halting #105; re-dispatch executable-invoice-list-rebuild-build-2026-06-23 once a step runs past ~4s.
