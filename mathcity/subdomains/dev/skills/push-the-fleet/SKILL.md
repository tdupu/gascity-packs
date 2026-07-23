---
name: push-the-fleet
description: >
  Saturate the city fleet with ready, unblocked work. Use when Taylor says
  "push the fleet", "fire more things", "get N things running", "dispatch
  everything ready", or "I want 10 things being worked on at a time". Finds
  all ready beads across rigs and dispatches them via build-basic-briefed
  (math-city-work pattern, policy gsp-fhdnu) until the active worker count
  reaches TARGET. Never slows down to ask for confirmation — it dispatches
  and reports.
---

# push-the-fleet

Saturate the fleet. Dispatch every ready, unblocked bead via
`build-basic-briefed` until active workers ≥ TARGET (default: 10).

This skill is the batch version of `math-city-work`: same formula, same
vars, same verify-assignee doctrine — but it sweeps the whole queue instead
of one bead.

## Pre-flight (same as math-city-work)

```bash
tmux -L gt ls >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — no tmux fleet server (city can't spawn agents)."
  exit 1
}
gc dolt health >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — Dolt is unreachable (bd cannot resolve beads)."
  exit 1
}
```

## Step 1 — Read target and current count

```bash
TARGET=${1:-10}
```

Count active workers via `gc session list` (NOT `gc status` — bug gs-0cy2):

```bash
ACTIVE=$(gc session list --state active 2>/dev/null \
  | grep -c "run-operator\|impl-worker" || echo 0)
echo "Active workers: $ACTIVE / target $TARGET"
```

If `ACTIVE >= TARGET`: report fleet is at target and stop. Do not re-dispatch
already-running beads.

## Step 2 — Enumerate ready beads per rig

For each rig, run `bd ready` from the rig's working directory to get its
unblocked queue. Only dispatch from rigs where work actually exists.

**Rig → working dir → artifact_root mapping:**

| Rig prefix | Working dir | artifact_root |
|---|---|---|
| `gsp-` | `~/gt/gascity-packs` | `/Users/tdupuy/gt/gascity-packs` |
| `he-` | `~/gt/hecke` | `/Users/tdupuy/gt/hecke` |
| `hom-` | `~/gt/homog` | `/Users/tdupuy/gt/homog` |
| `jac-` | `~/gt/jacobi` | `/Users/tdupuy/gt/jacobi` |
| `lm-` | `~/gt/lmfdb` | `/Users/tdupuy/gt/lmfdb` |
| `mca-` | `~/gt/magma_clifford_algebras` | `/Users/tdupuy/gt/magma_clifford_algebras` |

Detect rig from the bead ID prefix (first 2–4 chars before the first `-`).

## Step 3 — Priority filter before dispatching

**Skip these automatically — they need special handling or Taylor input:**

- `[epic]` — epics are scheduling containers, not direct work items
- `taylor-gated` / `taylor-ok-required` in the title — requires Taylor's explicit OK before dispatch
- `[reconcile D]` or BART-coordinated deploy beads — route to BART
- `brief-record` type — recording a verdict, not building; dispatching via build-basic-briefed is wrong for these
- `input convoy for <other>` — convoys feed context to another bead; dispatch the parent bead instead
- `Step spec for` — step specs are auto-managed by the formula machinery
- Status already `in_progress` or `closed` — skip

**Prefer in this order:**
1. P0 bugs and incidents
2. P1 bugs (especially infra and brief-system)
3. P1 implementation and design beads
4. P1 policy/skill beads
5. P2+ (fill remaining slots)

## Step 4 — Dispatch the canonical formula

For each candidate bead (run from the bead's rig dir):

```bash
gc sling <rig>/gc.run-operator <bead-id> --on build-basic-briefed \
  --var interaction_mode=autonomous \
  --var review_mode=agent \
  --var drain_policy=separate \
  --var push=false \
  --var open_pr=false \
  --var artifact_root=<rig-artifact-root>
```

Dispatch in parallel batches (multiple `gc sling` calls at once) — the
dispatcher queues what it can't run immediately; do not serialize.

Stop dispatching when DISPATCHED_COUNT + ACTIVE >= TARGET.

## Step 5 — Verify assignees (mandatory gate)

After each batch, wait ~30–60s then spot-check a sample of the freshly
created molecule beads:

```bash
bd show <molecule-bead> | grep -i assignee   # must be NON-EMPTY
```

If a molecule still has no assignee after 60s, the slot may be full. Report
it — do not silently assume success. An open root bead is NOT a strand (see
gs-0cy2 and `math-city-work` slow-build doctrine); wait before escalating.

## Step 6 — Report

Emit one concise table:

```
Fleet loaded — <N> dispatched, <ACTIVE> workers active.

| Bead | Title | Rig | Molecule |
|------|-------|-----|----------|
| he-2zv | conductor bug | hecke | he-xxxx |
| gsp-ws6hx | reaper order | gascity-packs | gsp-xxxx |
...

Target: <TARGET> | Active (post-dispatch): <ACTIVE> | Queue remaining: <N>
```

If the queue was exhausted before reaching TARGET, say so explicitly — that
is a "no more unblocked work" state, not a failure.

## Guardrails

- Never dispatch the same bead twice — check for an existing `in_progress`
  molecule before slinging.
- Do not dispatch beads that are blocked (dependencies open).
- Do not touch ~/repos/ — all git operations are BART's lane.
- Do not hand-edit city.toml to raise worker caps — use `adjust-workers` if
  the worker ceiling itself is the bottleneck.
- If the bottleneck is worker *slots* (too few run-operators in the pool),
  use `/adjust-workers` AFTER this skill to raise the cap.

## Composes with

- `math-city-work` — single-bead dispatch (this skill is the batch form)
- `adjust-workers` — raise worker cap when slot count limits throughput
- `hourly-check` — periodic fleet health that surfaces when queue depth > 0
  but active workers = 0

## Source policy

Dispatch formula: `gsp-fhdnu` (build-basic-briefed preferred).
Slow-build ≠ strand: `gs-0cy2`, `he-uz9fg`.
