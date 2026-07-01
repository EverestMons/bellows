stop

Same 401 infra blocker, NOT a plan failure. #104 Step-1 (invoice-list-rebuild UX design) failed in ~3s with HTTP 401 authentication_failed (apiKeySource: none, files_changed=0) — the design agent never ran. The Bellows daemon was restarted (PID 57257, 14:22) but its claude -p children still 401: a restart re-reads the same expired credentials. Needs an actual re-login (claude → /login, or claude setup-token), then restart the daemon from that authenticated context.

Halting #104 to leave a clean queue. Re-dispatch this plan (executable-invoice-list-rebuild-2026-06-23) once auth is genuinely fixed — verify a step runs past ~4s before trusting it.
