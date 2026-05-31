# Bellows Speed Research

**Date:** 2026-05-29
**Author:** Research pass for Mark (Eluvian)
**Scope:** Where wall-time goes when Bellows executes plans, and what actually makes it faster.
**Evidence base:** All 702 successful step logs in `bellows/logs/*-step.json`, the source (`runner.py`, `bellows.py`, `planner.py`, `config.json`), `PLANNER_TEMPLATE.md`, and current Claude Code / model documentation.

---

## TL;DR

The working assumption going in was that the terminal / `claude -p` process layer is the slow part. The data does not support that. Across 702 logged steps, **about 99% of every step's wall-time is model inference**. Process startup, the polling loop in `runner.py`, git worktree create/teardown, and diffing are, combined, low-single-digit percent at most.

The slowness is **Opus thinking and taking many sequential turns** (median 23 turns/step, often 50+). That cost is identical whether it runs in a terminal, a script, or any other harness — it is not a terminal problem.

The single highest-leverage change is **routing execution off Opus onto Sonnet where plan complexity allows**. Sonnet 4.6 runs at roughly twice Opus 4.6's output throughput, the system already supports per-plan model selection, and `gates.check()` plus CEO verdicts are the safety net. Everything else (fewer turns per step, trimming resumed context, keeping the cache warm across pauses) is secondary but real. Optimizing the terminal/process layer is not worth doing — it would buy under 1%.

One factual correction to the original framing: the flag is `--model` (set from `config.json` → `default_model: claude-opus-4-6`), not `-m`.

---

## How the system runs a plan (the parts that cost time)

Bellows drives execution one step at a time. For each step, `runner.run_step()` (in `runner.py`) spawns a single `claude -p` subprocess:

```
claude -p <prompt>
  --output-format stream-json
  --verbose
  --model <model>                # from plan header, else config default_model = Opus
  --allowedTools "Read,Edit,Write,Bash"
  --append-system-prompt <binding constraint>
  --resume <session_id>          # when continuing within a plan
```

The per-step loop in `bellows.py` (lines ~527–614) is: run the step → run `gates.check()` → either pause for a CEO verdict (on gate failure, QA checkpoint, header pause, or an agent verdict-request) or continue to the next step. The same `session_id` is resumed across all steps of a plan, so the executor's context grows step over step.

Three structural facts matter for speed:

1. **`gates.check()` is pure local Python — no LLM call.** Judgment between steps is programmatic plus the human CEO verdict. There is no per-step planner inference in the hot loop.

2. **`planner.consult()` exists in `planner.py` but is not wired into the hot loop.** If it ever is, note that it cold-reads the full `PLANNER_TEMPLATE.md` (~291 KB) + `COMPANY.md` from a fresh `/tmp` file on every call with no session reuse — a large latent cost. Left as-is, it does not affect current run speed.

3. **No MCP servers load per process.** There is no `.mcp.json` in any watched project, and the per-project `CLAUDE.md` files are small (1.2–5.4 KB). So there is no MCP-init tax and negligible auto-loaded context per step — both common `claude -p` slow-downs that Bellows simply does not have.

---

## The latency profile (702 steps)

| Metric (per step) | Median | p90 | Max | Mean |
|---|---:|---:|---:|---:|
| Wall time | 183.8 s | 466.5 s | 4,464 s | 225.1 s |
| Inference time (`duration_api_ms`) | 206.0 s | 492.7 s | 4,464 s | 252.8 s |
| Turns | 23 | 50 | 102 | 25.6 |
| Output tokens | 8,280 | 20,598 | 57,635 | 9,892 |
| Cache-read tokens | 672 K | 2,046 K | 6,762 K | 922 K |
| Cache-creation tokens | 49 K | 99 K | 226 K | 50 K |
| Cost | $1.00 | $2.40 | $16.00 | $1.30 |

**Inference share of wall-time: ~99.6% (median, computed per step).** Total logged agent wall-time: ~43.6 hours; total cost ~$886.

Two readings of this table drive everything below:

- **Inference is the whole game.** Whatever is left for process startup, the 1-second polling cadence in `runner.py`, git operations, and parsing is a rounding error against a 184-second median step.
- **Turns are the multiplier.** Each turn is a full model round-trip over the (cached) context. More turns = more serial latency, independent of how fast any single turn is.

### Turn distribution

| Turns per step | Steps |
|---|---:|
| 1–10 | 230 |
| 11–25 | 222 |
| 26–50 | 269 |
| 51–100 | 85 |
| 100+ | 7 |

361 of 702 steps (51%) run 26 turns or more. The long tail of heavy steps is where the worst wall-times live.

### Which models actually run

| Model | Step-appearances | Approx. tokens |
|---|---:|---:|
| `claude-opus-4-6` | 616 | ~887 M |
| `claude-haiku-4-5-20251001` | 98 | ~45 M |
| `claude-sonnet-4-6` | 82 | ~1.3 M |

Opus is the workhorse. Sonnet appearances are mostly the planner/consult path; Haiku appearances are subagent/side-calls inside a step. (Counts are step-appearances of a model in `modelUsage`, not mutually exclusive step counts.)

---

## Why "make the terminal faster" is the wrong lever

The original hypothesis was that running through `claude -p` in a terminal adds meaningful overhead. The measurement says otherwise: by Claude's own internal accounting, ~99% of a step is API/inference. Even adding the parts that accounting doesn't capture — Node/CLI process startup, the up-to-1-second poll tail in `runner.py`, and git worktree/diff subprocesses — you are looking at a few seconds on top of a 184-second median. That is low-single-digit percent, and it shrinks further on the heavy steps that hurt most.

Concretely: shaving the poll interval, pooling processes, or speeding up git would, in the best case, save on the order of 1% of total run time. The same engineering effort spent on model routing or turn reduction targets the other 99%.

This is the main thing to internalize before spending any time on optimization: **the bottleneck is model work, not the harness around it.**

---

## Recommendations, ranked

| # | Change | Impact | Effort | Main risk |
|---|---|---|---|---|
| 1 | Route execution off Opus onto Sonnet where complexity allows | High | Low (config/header) | Quality on the hardest plans |
| 2 | Reduce turns per step (batch tool calls, precise targets) | Med–High | Med (prompt/template) | Slightly larger prompts |
| 3 | Trim resumed context (fresh session + compact handoff) | Medium | Med | Loss of cross-step continuity |
| 4 | Keep prompt cache warm across verdict pauses | Low–Med | Low (env var) | Auth-mode dependent; long pauses still cold |
| — | Optimize terminal/process/git layer | Negligible | — | Not worth doing |

### 1. Route execution off Opus where complexity allows

This is the headline lever because it attacks the 99%. Sonnet 4.6 runs at roughly 40–60 tokens/sec versus Opus 4.6's ~20–30 tokens/sec — about a 2x throughput advantage that compounds across 23–50 turns per step.

Why it's low-risk to try:

- The system **already supports per-plan model selection** via the `Model:` header (`bellows.py:408`), falling back to `default_model`.
- You **already run the planner on Sonnet** (`config.json` → `planner_model: claude-sonnet-4-6`), so there's precedent and trust in Sonnet's judgment in-system.
- `gates.check()` plus the CEO verdict flow are an existing safety net that catches regressions regardless of which model produced them.

How to do it without a blanket switch: route by plan class. Send mechanical changes, QA steps, and documentation plans to Sonnet; reserve Opus for genuinely hard multi-file reasoning or architecture work. Start as an explicit A/B (below) rather than flipping the global default.

Honest bound on the payoff: inference time is part output-generation (where Sonnet's ~2x helps directly) and part prefill + tool-call round-trip latency (where it helps less). So expect a meaningful but not exactly-2x wall-time reduction. Pilot and measure rather than assuming a fixed multiple.

### 2. Reduce turns per step

With a median of 23 turns and a 51% tail at ≥26, turns are the second-order driver. Two concrete sub-levers, both prompt-side:

- **Encourage batched, parallel tool calls.** An agent that issues independent reads/edits in one turn instead of one-at-a-time collapses round-trips.
- **Give precise targets in the step prompt.** `PLANNER_TEMPLATE.md` (line 295) already observes that specific fix-prompts ("change `X` at `file.py:837`") reduce follow-up iterations. Reinforcing this — and considering a gate that flags vague, exploration-inducing step prompts — directly lowers turn count.

This helps at any model and stacks with recommendation 1.

### 3. Trim the resumed context

Bellows resumes one growing session across all steps of a plan (cache-read median 672 K, p90 ~2 M tokens). Even though those reads are cached and cheap, a larger context still raises time-to-first-token and per-turn compute. Because steps are deliberately discrete ("Execute Step N ONLY"), a **fresh session per step seeded with a compact handoff** (the plan + a short "what's done so far" summary) may be faster on later steps than dragging the full transcript forward.

This is a real trade against continuity, so it should be piloted on one plan class and compared on wall-time and gate-pass rate, not adopted blindly.

### 4. Keep the prompt cache warm across verdict pauses

A CEO verdict pause is a human-in-the-loop gap. If it exceeds the cache TTL, the next step pays full cache-creation (median ~49 K, p90 ~99 K tokens) on a cold prefix. Claude Code requests a 1-hour cache TTL automatically on a subscription, but on an API key / Bedrock / Vertex the default is 5 minutes unless `ENABLE_PROMPT_CACHING_1H=1` is set — and there was a March-2026 regression that silently dropped some setups back to 5 minutes.

Action: confirm Bellows's auth mode. If it runs on an API key, set `ENABLE_PROMPT_CACHING_1H=1` alongside the existing `DISABLE_AUTOUPDATER=1` env handling in `runner.py`/`bellows.py`. Caveat: this only helps pauses shorter than the TTL; multi-hour human gaps go cold regardless.

### Secondary / low-priority

- **Lean into Haiku subagents** for search and exploration (already happening in 98 steps), reserving the expensive model for edits. Worth a deliberate prompt nudge, but smaller than 1–3.
- **Cross-plan parallelism** (threads are staggered 2s in `bellows.py:1193`) raises total throughput when several projects are active. It does not lower any single step's latency, so it's a throughput lever, not a speed-per-step one.

---

## Suggested sequencing (one testable change at a time)

Deliberately incremental, to match "small steps before stepping large":

1. **Opus→Sonnet A/B.** Pick a class of mechanical/QA/doc plans, set `Model: claude-sonnet-4-6` in their headers, run, and compare wall-time and gate-pass rate against the Opus baseline already in `logs/` + `bellows.db`. Decide the default from data.
2. **Turn reduction.** Add batching + precise-target guidance to the step-prompt template; measure the `num_turns` delta on the next batch of plans.
3. **Fresh-session pilot.** Try per-step sessions with a compact handoff on one plan class; compare against full-`--resume`.
4. **Cache TTL.** Confirm auth mode; if API key, set `ENABLE_PROMPT_CACHING_1H=1` and watch cache-creation tokens after short pauses.

Each step is independently measurable from the existing logs, so none of them require guessing.

---

## Threats to validity / caveats

- `duration_ms` and `duration_api_ms` are Claude's own internal timings. Runner-level process startup, the 1-second poll tail, and git subprocesses are *not* captured in them — but they are small against a 184-second median, which is the whole point.
- `modelUsage` attribution counts steps where a model appears, not exclusive ownership of a step. Haiku/Sonnet figures reflect subagents and the planner path, not a second executor.
- The logs are historical; the current default executor is Opus. The recommendations assume a similar future workload mix.
- The Sonnet quality trade-off on the hardest plans is real. The recommendation is to **route**, not blanket-switch, precisely because of this.
- A note on "previous sessions within the Eluvian project": the Cowork session history contained nothing Eluvian-related, so the session-level evidence here is the Bellows run-logs, `PLANNER_TEMPLATE.md`, and the session-wrap docs — not a prior chat transcript.

---

## Appendix

### A. Raw aggregate figures

- Successful steps analyzed: 702 (698 with full timing fields).
- Wall: median 183.8 s · p90 466.5 s · max 4,464.3 s · mean 225.1 s.
- Inference (`duration_api_ms`): median 206.0 s · p90 492.7 s · max 4,463.8 s · mean 252.8 s.
- Inference share of wall (per-step median): 99.6%.
- Turns: median 23 · p90 50 · max 102 · mean 25.6.
- Output tokens: median 8,280 · p90 20,598 · max 57,635 · mean 9,892.
- Cache-read tokens: median 672.5 K · p90 2,045.7 K · max 6,762.2 K · mean 922.4 K.
- Cache-creation tokens: median 49.1 K · p90 98.8 K · max 225.9 K · mean 50.3 K.
- Cost: median $1.00 · p90 $2.40 · max $16.00 · mean $1.30.
- Totals: ~43.6 hours agent wall-time; ~$886 cost across logged steps.
- Model step-appearances: Opus 616 (~887 M tok) · Haiku 98 (~45 M tok) · Sonnet 82 (~1.3 M tok).
- Turn buckets: 1–10 → 230 · 11–25 → 222 · 26–50 → 269 · 51–100 → 85 · 100+ → 7.

### B. Key configuration (current)

- `config.json`: `default_model: claude-opus-4-6`, `planner_model: claude-sonnet-4-6`, `step_inactivity_timeout_seconds: 600`, `step_timeout_seconds: 2400`.
- `runner.py`: `DISABLE_AUTOUPDATER=1` set via `os.environ.setdefault` (protects prompt-cache continuity across the daemon; documented in `CLAUDE.md`).
- No `.mcp.json` in any watched project; per-project `CLAUDE.md` ≤ 5.4 KB.

### C. Files referenced

`bellows/runner.py`, `bellows/bellows.py`, `bellows/planner.py`, `bellows/config.json`, `bellows/CLAUDE.md`, `bellows/logs/*-step.json`, `bellows/bellows.db`, `PLANNER_TEMPLATE.md`.

### D. External sources

- Claude Sonnet 4.6 vs Opus 4.6 throughput: https://shawnkanungo.com/blog/claude-sonnet-46-vs-opus-46-whats-the-difference-and-which-one-should-you-use
- Claude Code prompt caching (TTL behavior): https://code.claude.com/docs/en/prompt-caching
- Cache TTL regression report (Mar 2026): https://github.com/anthropics/claude-code/issues/46829
