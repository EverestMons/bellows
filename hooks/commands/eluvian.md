---
description: Align the session with the Eluvian path (ELUVIAN_PATH.md) — advisory environment assert + parked-arc surfacing
---

# Eluvian alignment pass

1. **Read the doctrine.** Load `/Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md` in full. This is the governing process document.

2. **Assert the environment:**
   - **cwd** is `/Users/marklehn/Developer/GitHub` (the governance root)
   - **bellows daemon** is RUNNING — verify with `python3 bellows/status.py`
   - **wrap debt** — run `python3 bellows/hooks/eluvian/wrap_check.py` READ-ONLY (report its output, arm nothing)
   - **parked arcs** — report every line containing `⏸`, `PARKED`, or `RESUME AT` from the head of `shop_next_session.md`

3. **Report alignment or misalignment loudly.** State each check's result. If any check fails, state the failure clearly as a warning. **ADVISORY: never refuse to proceed** — a failed assert reports but does not block (fork 3 ruling). Say so in the report.
