---
description: Align the session with the Eluvian path (ELUVIAN_PATH.md) — advisory environment assert + parked-arc surfacing
---

# Eluvian alignment pass

The governance root is `$ELUVIAN_WRAP_ROOT` (shop machine: `~/Developer/GitHub`;
Mac mini: `~/Developer/eluvian-governance`) — same override the wrap hooks read,
set per machine in `~/.claude/settings.json`. Bellows is the root's populated
submodule on the shop machine and the sibling checkout `~/Developer/bellows` on
the mini — use whichever `<bellows>/status.py` exists.

1. **Read the doctrine.** Load `$ELUVIAN_WRAP_ROOT/ELUVIAN_PATH.md` in full. This is the governing process document.

2. **Assert the environment:**
   - **cwd** is `$ELUVIAN_WRAP_ROOT` (the governance root)
   - **bellows daemon** is RUNNING — verify with `python3 <bellows>/status.py`
     (on the mini, STOPPED is the correct, deliberate state — report it as such,
     not as a failure; the live daemon is the shop machine's)
   - **wrap debt** — run `python3 <bellows>/hooks/eluvian/wrap_check.py` READ-ONLY (report its output, arm nothing)
   - **parked arcs** — report every line containing `⏸`, `PARKED`, or `RESUME AT` from the head of `$ELUVIAN_WRAP_ROOT/shop_next_session.md`

3. **Report alignment or misalignment loudly.** State each check's result. If any check fails, state the failure clearly as a warning. **ADVISORY: never refuse to proceed** — a failed assert reports but does not block (fork 3 ruling). Say so in the report.
