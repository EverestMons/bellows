# Glossary — bellows

<!-- Discriminator: DEFINITION goes here; RUNBOOK goes in CLAUDE.md; TRAP goes into CODE. -->
<!-- Entries below. Format: ## Term \n definition \n -->

## clearance
The depositor-written lifecycle.db row that makes a plan claimable under the admission flip (R1). Keyed by content hash (sha256 over raw bytes) + claimable basename; written by the depositor at auto-clear or by the clear tool at a human release; consumed inside the claim transaction. A plan with no unconsumed clearance auto-HOLDs — the filename carries no authority.

## deposit receipt
The Planner-written attestation that a gate-watcher was armed for a deposit. A JSON file at `receipts/receipt-<slug>-<session_id>-<hash12>.json`, written against the DRAFT bytes BEFORE any ready- name exists. It proves the watcher was ARMED at write time — never that it stayed alive. Archived to `receipts/archived/` when the plan closes.

## class hold
The depositor's HOLD of a `shop-infra`-classed plan (any write to bellows/forge/lessons-forge code or root doctrine). Never auto-clears; released only by a human running `clear_plan.py --release-class-hold`, which re-runs cycle_check + plan_lint (benign-filtered) and writes the clearance as `cleared_by='clear_tool'`.

## release act
The deliberate human invocation that frees a class-held plan (rulings fork 4: the human running the tool IS the review). Distinct from auto-clear (depositor, read-only/app-feature/register-writing classes on full-pass gates).

## gate override
The deliberate human act marking a specific gate failure as discharged: `clear_plan.py --override-gate <plan> <step> <gate> --ref "<justification>"` writes `overridden=1` + the reference onto the gate_events fail rows. E4's consumption re-check advances a continue only when every reported failure is overridden — the benign-failure workflow under enforcement.

## verdict conditioning
E4's law: the daemon re-checks the gate record when consuming a `continue` (fork 5 — the enforcing party is the acting party). The request file is the per-pause truth of what failed; gate_events is the override-annotation layer; an absent or JSON-less request refuses as unverifiable; verdict files stay plain.

## keyed sweep line
E5's 3b affirmation form: `Lessons-swept: <date> [sid: <first-8-of-session-id>] — <delta>`. The stop-hook lock passes only when the NEWEST such line carries the wrapping session's id; the debt hook stays date-keyed by design (opposite polarity — it asks whether SOME session swept, not this one).

## verdict act
The Planner's continue/stop adjudication of a paused step, written as `verdicts/resolved/verdict-<id>-step-<N>.md`; since 2026-08-25 performed via `tools/issue_verdict.py` (location and grammar correct by construction — the bare-handed form is retired).

## dirty-tree precheck (intersection form)
The teardown-time guard (since exec-523) that refuses a worktree merge only when the live main tree's dirty paths INTERSECT the branch's changed files — commit-gated (skipped when the branch has no commits), quotepath-normalized, `-z -uall` porcelain-parsed. Lifecycle dirt a plan does not touch never blocks; dirt on a file the plan ships blocks with the exact filename and stash-first recovery. Its failures carry the `worktree_teardown_dirty_tree:` marker that keys the Gap-1c one-verdict retry.
