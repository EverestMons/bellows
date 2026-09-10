The repo directory `hooks/eluvian/` IS what the Claude Code harness loads: a
symlink on the mini (`~/.claude/eluvian -> …/bellows/hooks/eluvian`), the repo
path named directly in the shop's `~/.claude/settings.json`. `_common.py` is
imported by every hook from this directory — no installation required.

All edits to the enforcement layer must be made HERE, in version control,
and never directly in `~/.claude/`. The live wiring picks up changes from
this tree after the repoint.
