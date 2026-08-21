Canonical copy of the Eluvian wrap-hook enforcement layer, per the CEO's
2026-08-21 decision.

`~/.claude/eluvian/` is the LIVE location the Claude Code harness loads hooks
from. Step 2 of the wrap-hook vendor plan repoints the live wiring here.

All edits to the enforcement layer must be made HERE, in version control,
and never directly in `~/.claude/`. The live wiring picks up changes from
this tree after the repoint.
