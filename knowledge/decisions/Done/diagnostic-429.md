# Diagnostic: why the Bellows daemon won't restart on command — the single-instance lock vs the out-of-band daemon

**Type:** Diagnostic
**Project:** bellows
**Depends on:** prior diagnostic `bellows/knowledge/decisions/Done/diagnostic-daemon-restart-state-divergence-2026-05-24.md` (restart-state background; cited, not re-run)
**Created:** 2026-08-15
**Author:** Planner
**Slug:** `bellows-restart-lock-2026-08-15`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 4
**cycle_tier:** T1
<!-- diagnostic — no qa_steps field -->

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring. Deposit as the transient placeholder `diagnostic-draft-<HHMMSS>.md`; the daemon mints the id and renames on claim.

⚠️ **READ-ONLY.** This plan investigates and reports. It changes NO code, kills NO process, and touches NO live daemon. A fix is a SEPARATE executable authored from these findings (Quick Fix Protocol: diagnostic → executable).

---

## Why this exists

Restarting Bellows fails with a repeating log line: `another Bellows instance holds .bellows.lock — exiting` (observed 2026-08-15 22:29:54 and 22:30:22). Planner-side triage established the immediate cause and it is NOT a stale lock:

- A live daemon **PID 3969** (started Thu 2026-08-13 11:08:10, state `SN`, idle — `heartbeat: idle`, queue empty, no `claude -p` children) still holds the `fcntl.flock` advisory lock on `bellows/.bellows.lock` via its open fd 5 (confirmed by `lsof`). The lock file is **0 bytes** — it records no PID.
- The single-instance guard at `bellows.py:2472-2480` opens the lock file in `"w"` mode (truncating it — this is the `22:30:22` mtime bump), attempts `flock(LOCK_EX | LOCK_NB)`, fails because 3969 holds it, logs the error, and `sys.exit(1)`. The comment at line 2480 states the design intent: the kernel releases the flock only on process death. 3969 never died.
- `dashboard.py` has a restart path (`r` key → `_do_restart`, line 397 → `_kill_child`, line 371: SIGTERM → wait `SIGTERM_TIMEOUT=5` → SIGKILL). Planner triage suggests it terminates only `self.child` — the daemon the *dashboard* spawned — and PID 3969 was started out-of-band (`nohup bellows.py`, writing to `logs/daemon-nohup.log`), so it is not any current dashboard's child. **If that holds, the restart mechanism structurally cannot reach an out-of-band incumbent: it spawns a new child that then loses the flock race and exits — exactly the observed loop.**

The lock is doing its job. The defect is that "restart on command" has no path to STOP an incumbent it did not spawn, and the lock's error is undiagnosable (no holder PID). This diagnostic maps the restart/stop/lock machinery from the code, confirms or refutes the Planner-side hypothesis, and specifies the minimal correct fix — WITHOUT implementing it.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the diagnostic at knowledge/decisions/in-progress-diagnostic-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 (the only step). After completing it, STOP and wait for my confirmation.
```

---
---

## STEP 1 — Bellows Developer (investigate & report; no changes)

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this diagnostic and naming your first read.** Do NOT rename this file. **Skip specialist file and glossary reads — this is a code-tracing / error-investigation task.** You are investigating the Bellows daemon start/stop/restart machinery in `bellows/`. **You change nothing: no code edits, no `kill`, no touching the running daemon or the lock file. Read-only investigation, then deposit a findings file.** Answer each question below with concrete `file:line` citations and quoted code; where a claim rests on process state, say so and mark it as runtime-observed vs. code-derived. **For any question the code cannot answer, say so plainly — "no such path exists" or "not determinable from a code read" is a valid and expected finding, never a failure to paper over: this is a read-only investigation and an honest negative IS the answer.** **Q1 — Start surfaces:** enumerate every way the daemon process (`bellows.py`) is launched — the dashboard-spawned child (trace how `dashboard.py` spawns and holds `self.child`), a bare `nohup python bellows.py` / `python bellows.py`, `status.py`, any script or Makefile target. The documented model (`bellows/CLAUDE.md`) is `dashboard.py` as primary — the TUI that OWNS the daemon — and bare `python bellows.py` as the headless path; frame each enumerated surface against that documented model and identify which one an out-of-band incumbent (not spawned by the current dashboard) would have used. For each, state what becomes the process's parent and whether a dashboard instance would consider it `self.child`. **Q2 — Restart/stop reach:** in `dashboard.py`, trace `_do_restart` (≈line 397) and `_kill_child` (≈line 371). Exactly which process do they terminate? Confirm or refute: they act ONLY on `self.child`, so a daemon started out-of-band (not spawned by THIS dashboard instance) is never killed by the `r` restart, and a fresh dashboard/daemon then fails the flock guard and exits. Trace the flock-probe liveness check at ≈`dashboard.py:129` — is its result ever used to STOP or adopt a non-child incumbent, or only to display liveness? **Q3 — The lock:** at `bellows.py:2472-2480`, confirm the lock file is opened `"w"` and NO pid/identity is written into it; confirm the "another Bellows instance holds" error names no holder; confirm the flock is fd-scoped and released only on process death. Is there any separate pidfile that records the running daemon's PID anywhere? (Check `dashboard.py`'s own dashboard-lock at ≈line 343 too — same shape? does it write a PID?) **Q4 — Stale vs live disambiguation:** with the lock file carrying no PID, is there ANY existing code path that can tell a stale lock (holder dead) from a live one (holder alive), or report WHICH pid holds it? **Q5 — Fix options (specify, do not implement):** lay out the minimal correct fix and the alternatives, with the trade-offs of each: (a) write `os.getpid()` (and a start timestamp) into the lock file after acquiring the flock, and include the holder pid + age in the "another instance holds" error so it self-diagnoses; (b) a `stop`/`restart` path that discovers the incumbent and runs it through the existing SIGTERM→wait→SIGKILL ladder BEFORE starting a new daemon — noting that there is **NO portable syscall to query a flock's holder**, so "read the flock holder" is not a real capability: discovery is necessarily either the added pidfile (from (a)) or parsing `lsof` on the lock file, and the recommendation must name which mechanism and its failure modes (`lsof` absent, multiple openers, zero openers); (c) on dashboard/daemon startup, when the flock is held by a NON-child, either adopt-and-kill or refuse with a message naming the holder pid — decide which is safer and why. Recommend one as the minimal fix and name the file(s)/function(s) an executable would touch. **The recommended fix MUST specify the ORDER of its guards as an explicit sequence, cheapest-safe-path first:** attempt the atomic `flock(LOCK_EX|LOCK_NB)` acquire — if it SUCCEEDS the lock was free or stale and NO kill happens; only if acquire FAILS does an incumbent exist, at which point the identity guard (Q6 ii) and idle guard (Q6 i) run and decide kill-or-refuse, followed by a re-acquire as the arbiter. Without a stated order these guards are only accidentally consistent — an implementation that identity-checks-and-kills before ever trying a clean acquire would kill a daemon when the lock was actually free. **The recommendation MUST NOT authorize a blind kill-by-PID** — a stop path that trusts a stored PID without verifying the target process IS Bellows is a rejected option (see Q6's identity guard); killing must earn both the identity guard and the idle guard, never assume them. **Q6 — Kill-safety (two independent guards a downstream fix must both satisfy before ANY signal is sent).** **(i) Idle guard:** an incumbent may be mid-plan (a live `claude -p` runner child, uncommitted step work). Specify how the fix should detect idle-vs-busy BEFORE killing (queue empty / `heartbeat: idle` / absence of a runner child / in-flight verdict) and what it should do when the incumbent is busy. **Idle-of-plans is necessary but NOT sufficient:** the prior diagnostic (cross-referenced below) established that a daemon killed mid-transition splits non-atomic filename/verdict/`bellows.db` operations and re-trips its catalogued state-divergence failures. So the fix must also establish whether the daemon installs a clean SIGTERM handler that completes or safely aborts an in-flight transition — report whether such a handler exists at all — and treat "no clean-shutdown path" as a reason to prefer refuse over an abrupt SIGKILL, since SIGKILL cannot be trapped. **(ii) Identity guard:** the fix must prove the kill target is genuinely the Bellows daemon, not a recycled or stale PID — a PID read from a file can name a different process after PID reuse, so the flock OWNER (discoverable via `lsof` on the lock file / the holding fd, or `ps` cmdline verification of `bellows.py`) is the authoritative "this is our daemon" signal, and a stored PID is not. Specify how the recommended stop path establishes target identity, and require a **safe-refuse fallback** — log the holder and exit, the CURRENT behavior at `bellows.py:2478` — whenever identity OR idle-state cannot be confirmed; refuse is the default and killing is the exception that must earn both guards. **(iii) Degenerate and concurrent lock states — enumerate what the fix must survive:** a genuinely STALE lock (holder already dead) must be detected and simply ACQUIRED, never "killed" — there is no process to signal; an empty or malformed lock file (the current 0-byte reality) must not crash the discovery path; and two restarts racing must resolve safely — the atomic `flock(LOCK_EX|LOCK_NB)` ACQUIRE is the authoritative final arbiter (exactly one process can hold it), so the fix's success is OBSERVED as "the new daemon now holds the flock", never as "kill() returned": the kill decision is not atomic and must not be treated as the arbiter. Cross-reference the prior diagnostic `Done/diagnostic-daemon-restart-state-divergence-2026-05-24.md` for restart-state hazards already catalogued and note any overlap. **Do not fix anything — investigate and describe what you find.** **Deposit** your findings as `bellows/knowledge/research/bellows-restart-lock-findings-2026-08-15.md` written with the canonical Python write pattern (or `Filesystem:write_file` if reachable) — a dated findings doc with one section per question (Q1–Q6), each answer citing `file:line` and quoting the relevant code, plus a one-paragraph **Recommended minimal fix** at the end naming the exact files/functions and the idle-check guard. Commit it from cwd with a pathspec naming exactly that file. Standard prompt feedback protocol → Output Receipt `### Ledger Updates` → `#### Prompt Feedback` section.
>
> **Deposits:**
> - `bellows/knowledge/research/bellows-restart-lock-findings-2026-08-15.md`
>
> **Scope:**
> - `bellows/knowledge/research/bellows-restart-lock-findings-2026-08-15.md`
>
> **STOP. This is the only step. Do NOT author or run the fix. Wait for CEO confirmation before continuing.**

---
---

## Drafting Cycle

**Tier:** T1 — triggers fired: **T-7** (authored-from diagnostic — a later executable builds the fix on these findings without re-verification). T-8 (novel pattern) considered — the investigate-and-report shape is a proven clone, but the subject is new; T1 is demanded either way. T-2/T-3/T-5/T-6 do NOT fire (read-only, same-machine, non-destructive, no governance surface).

**Walk 0 — context pin (§2.0):** clone-diff target measured (newest-of-class, sorted by ship date) = `diagnostic-337` (2026-08-10, lint-class-recall investigation) — `diagnostic-370` (2026-08-12) is newer but wrong class (QA-corrective, not a code-tracing investigation); `diagnostic-322` (2026-08-08) is older. Diffed against 337: same class carried faithfully — single investigate-and-report step, findings deposited to `knowledge/research/`, `cycle_tier: T1`, `pause_for_verdict: always`. No machinery dropped. Anchor-line measurements (2)-(5) N/A: this diagnostic edits no existing governed file (it writes a new findings doc). Prior-art citation verified present: `bellows/knowledge/decisions/Done/diagnostic-daemon-restart-state-divergence-2026-05-24.md`.

**Walk register:** `governance/knowledge/research/walk-register-bellows-restart-lock-2026-08-15.md` (schema v0.3) — created at walk 1.

**STATUS: CYCLE COMPLETE — walk 2 dry, §2 bar met.** Walk 1 folded 7 instruction-class findings across all five lenses (the plan carries a destructive downstream kill path, so it had real depth); walk 2 re-ran all five lenses over the folded draft and found nothing — a full dry walk, the §2 doneness bar. Newest same-class comparison: `diagnostic-337` (2026-08-10), diffed at walk 0, no machinery dropped. Mechanical conformance (§5): `plan_lint` run at deposit-shape, exit 0 (warn-first; residual warns are a path-resolution false positive on a `bellows/logs/` file flagged from `scratchpad/`, cleared on deposit to `bellows/knowledge/decisions/`).

**Walk 1 (all instruction-class — bar unmet, drove walk 2):**
- Weak spots:      w1 1 folded — instruction 1 / record 0 (1.4: honest-negative framing so "no such path exists" is a valid answer, per diag-229). Walk-0 also folded 2 record corrections: schema 0.2→0.3, clone-target measured.
- Destruction:     w1 1 folded — instruction 1 / record 0 (2.3/2.4: findings authorize a downstream kill path; process-IDENTITY guard added to Q5/Q6 — prove the target is Bellows, not a recycled PID; refuse-is-default).
- Vulnerabilities: w1 2 folded — instruction 2 / record 0 (3.4: Q6 (iii) degenerate/concurrent states — stale→acquire-not-kill, 0-byte/malformed lock, restart race with the atomic flock acquire as arbiter and observable success; 3.1/3.2: "read the flock holder" phantom capability corrected to lsof/pidfile with named failure modes).
- Integration:     w1 2 folded — instruction 2 / record 0 (4.2: prior diag-2026-05-24 proves mid-transition kill re-trips state-divergence — Q6 idle guard extended with a clean-SIGTERM-handler check; 4.1: Q1 anchored to CLAUDE.md's dashboard-owns-daemon model). Confirmation (no fold): NO pidfile/getpid/os.kill in bellows — Q3/Q5(a) premise holds.
- ACID:            w1 1 folded — instruction 1 / record 0 (5.2 Consistency: guards had no stated precedence; Q5 now mandates the ordered sequence — try-acquire-first → identity+idle → kill-or-refuse → re-acquire as arbiter. 5.5 Durability-as-record adequate; 5.3 Isolation structurally empty).

**Walk 2 (over the folded draft — all five lenses DRY):**
- Weak spots: dry. — Destruction: dry. — Vulnerabilities: dry. — Integration: dry. — ACID: dry.

**Closing:** walk 2 full dry — instruction 0 / record 0; the last event before deposit is a dry lens pass (§2 dry-close form). Closing-record re-read (§2.7) run after the close: the status header, per-lens lines, and this Closing checked against the artifact — the seven walk-1 folds are all present in Q1/Q5/Q6 as summarized, and the walk-2 dry claim matches the lens-by-lens pass. Deposited once.
