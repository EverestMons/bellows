# Dev Log — daemon-launchd-agent — 2026-09-11

## Pins re-derived (P1, P2, P3, P4)

**P4:** `launchctl getenv PATH` → empty on the mini; the shell's PATH begins `/Users/marklehn/.local/bin:…:/opt/homebrew/bin:…`; `claude` is `/Users/marklehn/.local/bin/claude` (a symlink into `~/.local/share/claude/versions/…`); the daemon's auth preflight runs `["claude", "-p", "reply OK", "--output-format", "text"]` by name (`bellows.py:2493–2496`, 15 s timeout) and the daemon logs `auth preflight OK` at start (this morning's log, 11:21:49); `plutil` at `/usr/bin/plutil`; the daemon's session log is `logs/terminal/bellows-<date>.log` (`:3610–3613`)

**P1 re-derived (bellows `41cd3f7`):** `bellows.py:3627` `if len(sys.argv) > 1 and sys.argv[1] in ("stop", "restart"):` → `stop_daemon(...)` (`:3631`), `sys.exit(1)` on failure, and for `restart` → `_perform_restart()` (`:3636`); `_perform_restart()` at `:196–211`: if `_agent_loaded(label)` → `_kickstart(label)` and print `restarted — agent kickstarted`; else `subprocess.Popen([sys.executable, "bellows.py"], ..., start_new_session=True)` and print `restarted — new daemon spawned (detached)`; `stop_daemon` guards unchanged: `_discover_holder` by `lsof -t <lock>`, identity guard, idle guard, SIGTERM/SIGKILL; `_DRAIN_TIMEOUT = 30` at `:114`; no `start_new_session` on the old restart (confirmed before edit, now corrected); no `_agent_loaded` before this plan (confirmed). MECHANISM MATCH: no pre-existing `_agent_loaded`, `_kickstart`, or `start_new_session`.

**P2 re-derived:** `tuyere/scripts/com.eluvian.tuyere-watcher.plist.template` shape: `Label`, `ProgramArguments` (venv python + `-m tuyere.watcher`), `WorkingDirectory`, `StandardOutPath/StandardErrorPath` under `server-state/`, `RunAtLoad` true, `KeepAlive` true, `ThrottleInterval` 30, header comment; installer: `set -euo pipefail`, refuses without `.venv/bin/python` and `config.json`, `sed` render into `~/Library/LaunchAgents/`, `launchctl bootout || true` then `launchctl bootstrap gui/$(id -u)`. Bellows template adds `KeepAlive {SuccessfulExit: false}`, `ExitTimeOut 45`, `EnvironmentVariables` with PATH and HOME.

**P3 re-derived (dashboard `41cd3f7`):** `dashboard.py:419` `_spawn_child`: if `bellows._agent_loaded()` → `bellows._kickstart("com.eluvian.bellows-daemon")` and `self.child = None`; else `Popen([sys.executable, "bellows.py"], ..., start_new_session=True)`; `:434` `_terminate_child`: SIGTERM → wait → SIGKILL, only when `self.child`; `:461` `_do_restart`: terminate child (no-op when None) → wait for lock → if held: `bellows.py stop` → respawn; `:487` `_do_quit`: terminate child only (no-op when None). `assemble_state` returns `agent_loaded: bellows._agent_loaded()`. Header shows `[agent]` suffix when loaded.

## Failing-first (red, then green)

**Red:** `6 failed, 1 passed in 0.36s` — t1/t2 FileNotFoundError (template absent), t3/t4/t5 AttributeError `_agent_loaded` (not yet in bellows), t7 FileNotFoundError (installer absent); t6 passed (invariant already holds).

**Green:** `2275 passed, 1 skipped in 99.89s` — full suite after all edits; the 1 skip is `test_gate_watcher` (live-DB).

## The rendered plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<!--
  TEMPLATE — not installable as-is. Two placeholders are rendered at install
  time by scripts/install-daemon-agent.sh:
    /tmp/devlog-root  absolute path to the bellows checkout on this machine
    /tmp/devlog-home          absolute path to the user's home directory

  Deliberately a template rather than a hardcoded literal because both paths
  differ per machine (checkout location, username). Committing the literal
  makes a new machine a manual edit; rendering it is the operator's act.
-->
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.eluvian.bellows-daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/tmp/devlog-root/.venv/bin/python</string>
        <string>bellows.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/tmp/devlog-root</string>
    <key>StandardOutPath</key>
    <string>/tmp/devlog-root/logs/terminal/daemon-launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/devlog-root/logs/terminal/daemon-launchd.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <!-- launchd gives agents an empty PATH; claude lives in ~/.local/bin -->
        <key>PATH</key>
        <string>/tmp/devlog-home/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>/tmp/devlog-home</string>
    </dict>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key>
    <dict>
        <!-- A clean stop (exit 0) stays stopped; a crash is restarted. -->
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <!-- Must exceed bellows._DRAIN_TIMEOUT (30 s) so launchd waits for the
         in-flight drain before escalating to SIGKILL. -->
    <key>ExitTimeOut</key><integer>45</integer>
    <key>ThrottleInterval</key><integer>30</integer>
</dict>
</plist>
```

## Mutation run

MUTATION: 4 killed, 0 survived, 0 error
