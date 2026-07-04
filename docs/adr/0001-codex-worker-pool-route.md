# ADR-0001: Codex-worker dispatched via pool route, not Claude subagent

**Status:** Accepted  
**Date:** 2026-07-04

## Context

The mathematics pack needs a way to dispatch tasks to the OpenAI Codex model
for cross-model critical review. Two patterns exist in the codebase:

1. **Pool route** (`gc.run_target = "codex:codex-worker"`): the codex-worker
   agent claims a step bead and runs it autonomously as a Gas City pool worker.
2. **Claude subagent** (pr-pipeline pattern): a Claude-led formula step spawns
   `codex:codex-rescue` via the Agent tool and awaits its result inline.

## Decision

Use pool routing. The `codex-dispatch` formula creates a step bead with
`gc.run_target = "codex:codex-worker"`. The codex-worker claims it
independently; no Claude session bridges the call.

## Reasons

- The use cases (creative design, large-plan review, retry after failure) are
  open-ended and benefit from an autonomous session, not a timed subagent slot.
- Pool routing keeps the Claude session cost at zero for this work.
- The codex-worker's existing prompt loop (`gc hook --claim`) already handles
  autonomous claim-execute-close without modification.
- The pr-pipeline's subagent pattern is appropriate when Claude needs the
  result to synthesize a final output. Here Taylor reads the output directly
  from the bead; no synthesis step is needed.

## Trade-off

The pool-route path requires the codex provider to be configured and a pool
worker running. The subagent path would work even with no standing session.
Accepted: codex is already declared in `mathematics/pack.toml`
(`[providers.codex] base = "builtin:codex"`), and the agent is `scope = "rig"`.
