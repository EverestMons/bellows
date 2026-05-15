**project:** bellows | **type:** diagnostic | **steps:** 1 | **pause_for_verdict:** always | **auto_close:** false

# Design — Terminal output, notification, and capture redesign proposals

## Why this exists

The 2026-05-11 surface audit (`Done/diagnostic-terminal-and-notification-surface-audit-2026-05-11.md`) characterized three problem surfaces:

1. **Terminal output** — no timestamps on plan events, no severity taxonomy, no plan grouping, three coexisting prefix conventions, runner heartbeats lack plan identity, heartbeats dominate scroll.
2. **Notifications** — no coalescing (5-plan session → 6 pushes), no priority/sound configurability, two dead-code notification functions in `notifier.py`.
3. **Capture/retention** — terminal output is not captured to disk anywhere; `logs/` contains only `claude -p` step JSON; terminal history is ephemeral.

The BACKLOG entry originally proposed (a) audit → (b) design → (c) implementation. This is (b). The diagnostic produces a written design proposal — formats, taxonomy, policies, examples. It does not write code, edit Bellows source files, or modify config. The output is a design document that the CEO can mark up, revise, or accept; an implementation plan follows once design is locked.

This is "type: diagnostic" because the deliverable is a research artifact, not code changes. Multiple competing alternatives are proposed where the design space has real tradeoffs — the CEO picks per surface before implementation.

## Step 1 — Systems Analyst: produce redesign proposals across three surfaces

You are the Bellows Systems Analyst. Read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` before starting; if the exact filename differs, use the closest match in `bellows/agents/`.

### Context

Read the prior audit at `bellows/knowledge/research/terminal-and-notification-surface-audit-2026-05-11.md` in full before drafting. Every design proposal must reference specific findings from that audit. Do not re-audit the code — trust the prior findings. If a design proposal requires information not in the audit, flag it as an open question rather than re-investigating.

The CEO's working environment for Bellows:
- Bellows runs on a Mac development machine in a single terminal pane the CEO leaves visible.
- Pushover notifications go to the CEO's phone. Pushover free tier = 10,000 messages/month, well above current usage but with no coalescing the per-session push count scales linearly with plan count.
- The CEO inspects the terminal scrollback during/after sessions to reconstruct what happened. There is no centralized log viewer.
- Concurrent plans are an active feature (parallel groups, multi-plan sessions). Runner heartbeat ambiguity is a real problem, not theoretical.
- Bellows does NOT hot-reload. Any code change requires the CEO to restart the daemon (BACKLOG-noted constraint).

This design must serve solo-operator inspection — readability for one human reading scrollback is the primary fitness function, not log aggregation, alerting infrastructure, or multi-user collaboration.

### Task

Produce a design document with three sections, one per surface. For each surface, propose 2 alternatives where the design space has real tradeoffs (e.g., minimal change vs. full redesign), or 1 proposal with clearly stated rationale where the design space is narrow. Every proposal must include: (a) the new format/policy in concrete detail, (b) at least 2 realistic before/after examples drawn from the audit's reconstructed sequences, (c) the LOC impact and which files would need to change, (d) any tradeoffs or open questions.

#### Section 1 — Terminal output redesign

Address every finding from C.11 items 1–6 of the audit. The proposal must specify:

1. **Severity taxonomy.** Define exactly which severity levels exist (e.g., DEBUG, INFO, WARN, ERROR, EVENT). For each, define when it fires and how it renders. Decide: machine-parseable bracketed prefix (`[INFO]`, `[WARN]`), color (ANSI escapes), emoji-only, or a hybrid. State the tradeoff between machine-parseability and human readability.

2. **Timestamp policy.** Every event line gets a timestamp, or only some? Absolute time (`HH:MM:SS`), date+time, or relative-to-session-start? State the tradeoff between scrollback density and timeline reconstruction.

3. **Plan grouping.** Define how plan events are visually separated from each other and from heartbeats. Options to consider: blank lines, indented bodies under a slug header, explicit separator lines, no grouping but mandatory slug identifier on every plan line. Show how the grouping survives concurrent plans (the case where the audit's worst-case interleaving illustrates the problem).

4. **Runner heartbeat redesign.** The runner heartbeat must identify its plan. Specify the new format with example. State whether the heartbeat should suppress itself when no work is happening (the audit notes heartbeats dominate idle scroll).

5. **Prefix unification.** The audit found three coexisting prefix conventions (`Bellows:`, `Bellows: runner —`, `[runner]`) plus `Pushover error:` on stderr. Propose either: (a) keep distinct prefixes but standardize them, or (b) unify under one convention. Be specific about the final string for each event source.

6. **Heartbeat suppression policy.** Currently heartbeats fire on a fixed 60s cadence. Propose whether (a) keep fixed cadence, (b) suppress when plan events have fired recently (e.g., within the last 60s of any plan event), (c) only fire heartbeat when no in-flight plans exist, or (d) some other policy. State the tradeoff between liveness signal and scroll dominance.

7. **Worked examples.** Provide three rendered before/after examples using the audit's actual line content:
   - Single 1-step diagnostic plan, idle-then-execute-then-pause.
   - Two-plan parallel session with interleaving (use the audit's reconstructed worst-case as the "before").
   - A failure case (runner inactivity timeout + gate failure + verdict request).

#### Section 2 — Notification coalescing and dead-code cleanup

Address every finding from C.11 items 7–8 of the audit. The proposal must specify:

1. **Coalescing policy.** Define when multiple events combine into one push and when they don't. Options to consider: (a) per-session digest (one push at queue-empty summarizing all plans), (b) per-plan digest (one push per plan at terminal state, no per-step pushes), (c) urgency-gated (only verdict-needed and failure push immediately; completions/queue-empty batch into a digest after N seconds of quiet), (d) keep one-push-per-event but add priority levels so the CEO can mute low-priority ones.

   Compare these on (i) latency for urgent events, (ii) push count under typical session shapes (1 plan, 3 plans, 10 plans, mixed pause+complete), (iii) implementation complexity.

2. **Priority and sound mapping.** Pushover supports priority levels (-2 to +2) and sound selection. Propose which events get which priority. State which (if any) should override the user's default sound.

3. **Configurability.** Should the CEO be able to enable/disable specific event types from config? Propose a config schema addition (`notifier.events.plan_complete: bool`, etc.) or argue against it. Include the proposed `config.example.json` diff if recommending one.

4. **Dead-code cleanup.** The audit found `notify_escalation()` and `notify_complete()` are defined but never called. Propose either (a) delete them outright, or (b) preserve as documented stubs with a comment explaining the deprecation path. State which call sites should be migrated from direct `push()` to named functions, or vice versa, to reduce API drift (the audit notes 5 direct `push()` call sites and 2 named-function call sites — propose a coherent pattern).

5. **Worked examples.** Provide push-count comparisons for three session shapes from the audit's findings, before vs. after the proposed coalescing policy.

#### Section 3 — Terminal output capture and retention

This surface was not in the original BACKLOG entry but emerged as audit finding C.11.6: Bellows does not capture its own stdout to a file. Address that gap.

1. **Capture mechanism.** Propose either: (a) `tee`-equivalent via Python's `logging` framework with a `RotatingFileHandler`, (b) external tee invocation (`bellows.py 2>&1 | tee`), (c) a custom in-process buffer that writes to a session file on the way to stdout, (d) keep stdout-only and add an explicit "save scrollback" command. Compare on durability across daemon restart, multi-session retention, search-ability, and implementation cost.

2. **File location and naming.** Where do captured terminal logs live? Single growing file, per-session files, per-day files? Propose a path under `bellows/logs/` and a naming convention. State how this interacts with the existing `logs/*.json` step-output files (don't collide, don't confuse).

3. **Rotation and retention.** The audit notes no rotation is configured for the existing `logs/` JSON files either. Propose a rotation/retention policy that covers both the new terminal log and the existing step-JSON files. Be concrete: rotate at X MB or X days, keep N old files, delete or compress after Y days.

4. **Visibility from terminal output.** Should Bellows emit a startup line stating where the current session's log is being written? Propose the exact line or argue against it.

5. **Worked example.** Show what a daily directory listing of `bellows/logs/` looks like under the proposal after a typical day of usage.

#### Section 4 — Implementation roadmap

After the three design sections, produce a brief "Implementation roadmap" section proposing how to sequence the implementation plans. Address:

- Can the three surfaces ship in one executable, or do they need to be three? Recommend a sequence.
- Identify which proposals are non-controversial and ready for executable authoring, vs. which need CEO clarification first.
- Flag any cross-surface dependencies (e.g., if terminal output adds bracketed severity prefixes, does capture format need to preserve them, and does notification message format need to mirror them?).
- Estimate LOC impact per surface and total.

### Constraints

- The CEO restarts Bellows manually after code changes (no hot-reload). Design proposals must work cleanly across restart — e.g., terminal capture must handle resuming or starting a new file on restart without losing context.
- Do not propose changes that require new third-party dependencies beyond what's already in `requirements.txt` unless there is no reasonable alternative — flag explicitly if any new dependency is required.
- Do not propose changes to `RULE_20_SELF_CHECK_BLOCK.md`, the verdict lifecycle, gate logic, or plan parsing. Scope is terminal/notification/capture only.
- Do not write or modify any code in this plan. The deliverable is a design document.
- Where the design space contains a real tradeoff, propose alternatives rather than picking. Where the design space is narrow, pick and state why.

### Deliverables

A design document at `bellows/knowledge/research/terminal-notification-capture-design-2026-05-11.md` containing:

- A 1-paragraph executive summary at top.
- Section 1: Terminal output redesign — covers items 1–7 above with proposals, examples, LOC estimates.
- Section 2: Notification coalescing and dead-code cleanup — covers items 1–5 above with proposals, examples, LOC estimates.
- Section 3: Capture and retention — covers items 1–5 above with proposals, examples, LOC estimates.
- Section 4: Implementation roadmap — sequencing, dependencies, total LOC, open questions for CEO.
- An Output Receipt at the bottom per `BELLOWS_SYSTEMS_ANALYST.md` format.

**Deposits:**
- `bellows/knowledge/research/terminal-notification-capture-design-2026-05-11.md`
