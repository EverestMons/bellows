# Dev log — [3/root] gitlink arm, published-tip check (plan 100128, 2026-09-18)

Re-draft of the first cycle for thread 417 (`executable-bellows-gitlink-arm.md`),
which ended in RE-DRAFT at walk 7 on forcing finding (d): its obligation was
stated in git vocabulary (the mechanism's own terms), so the check matched
its own reflection.  This draft judges each pointer against the submodule's
PUBLISHED tip read from its origin, not against any local clone.

## Five outcomes of the new arm

The `[3/root]` arm in `wrap_check.py:check()` loops over every tracked gitlink
(union of index and HEAD), and for each path produces exactly one of:

1. **FAIL — uncommitted change**: porcelain's STAGED column (first letter) is not
   a space (`M` bump, `A` addition, `D` removal).  Short-circuits; no tip read.
2. **FAIL — missing .gitmodules entry**: `_submodule_url` returns `None`.
   A silent skip would exempt the submodule permanently; a fail forces resolution.
3. **PASS — published tip unreadable**: `_published_tip` returns `None`.  Per CEO
   ruling 3b: when the arm cannot judge, it passes rather than blocking a machine
   (same principle as the first draft's missing-checkout case, now an unreadable
   remote).  Prints a funnel-law advisory; appends nothing to `fails`.
4. **PASS — current**: tip equals the recorded gitlink sha.  No output.
5. **FAIL — stale**: tip differs from the recorded gitlink sha.  Message carries the
   full 40-char published sha so it can be passed directly to `update-index
   --cacheinfo` without abbreviation (abbreviated shas are rejected by cacheinfo).

## SSH transport constant `_GIT_SSH`

`ssh -o ConnectTimeout=3 -o BatchMode=yes`

- **`ConnectTimeout=3`**: caps the TCP handshake at 3 s per host.  Without it an
  unroutable host stalls for the OS default (~75 s), making three sequential reads
  potentially hang a session start for ~225 s.  Measured: 3020 ms with the cap,
  vs no return without it (P6).
- **`BatchMode=yes`**: prevents ssh from issuing interactive prompts (passphrase,
  unknown-host-key confirmation).  Without it, a host whose key is not in
  known_hosts would hang the hook indefinitely.

Both are set via `GIT_SSH_COMMAND` on every `git ls-remote` subprocess; the
subprocess `timeout=10` is an additional backstop against the rare case where
the TCP handshake succeeds but the protocol stalls.

## Concurrency

All tip reads run in a `ThreadPoolExecutor`, one worker per URL, so three
submodules finish in ~1 s wall time regardless of per-read latency rather than
accumulating sequentially.  Sequential reads at 1 s each would add ~3 s to every
session start and wrap.

## Arm confinement (`try` / advisory)

The entire arm body is wrapped in a `try`.  On any exception: the advisory
`[3/root] WARN (advisory): gitlink arm error — <exc>; any gitlink not already
reported above was not judged.` is printed, and `check()` continues past the arm.
Fails already appended (uncommitted changes, missing entries, stale results from
reads that completed before the error) STAND — they are certain and should not be
discarded because an unrelated reader crashed.  Without this guard a single bug
here exits `main()` with 0 and its advisory is discarded, making it a silent
total bypass (MUST-PRESERVE L).

## What this re-draft removes

The first draft's _local-clone_ machinery: `_resolve_submodule`, detached-HEAD
checks, URL-normalisation, fetch/unpushed logic, the initialized-vs-uninitialized
branch.  None of that machinery is present here.  The arm reads only porcelain's
STAGED column and `git ls-remote`; it needs no local copy of any submodule,
and neither machine's layout can blind it (measured: mini's submodules are
uninitialized, Air's are initialized, both judged correctly — P5, P12).
