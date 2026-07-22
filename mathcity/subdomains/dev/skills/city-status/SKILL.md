---
name: city-status
description: Gas City fleet and work-queue status snapshot — checks fleet liveness, active sessions, in-progress beads, brief pipeline state, and Dolt health. Use when the user says "city status", "what's running", "fleet health", "what is the city doing", "how is the city", "are things getting done", "what beads are in progress", or "check the pipeline". Read-only: never dispatches, slingshoots, or modifies beads. Recommended model: Sonnet (mechanical read + light diagnosis).
---

# city-status

Read-only snapshot of Gas City fleet and pipeline. Run before any dispatch
decision and after city restart to confirm health. Never commits, slingshoots,
or modifies any bead.

## Pre-flight

```bash
gc dolt health 2>&1 | head -3
```

If Dolt is unreachable: report `DOLT DOWN — most bd commands will fail`.
Continue with tmux/session checks only.

## Procedure

### 1 — Fleet liveness

```bash
tmux -L gt ls 2>&1
gc session list --state active 2>&1
```

**CRITICAL**: `gc status` lies about agent count (bug gs-0cy2 — probe times
out, reports 0). Use tmux + session list as ground truth.

Report:
- Number of live tmux sessions (non-zero = city alive)
- Active session IDs, templates, worktdirs, age, last-active

### 2 — In-progress beads (per-rig)

For each major rig the user works in (hecke, gascity-packs, agent_skills, gt):

```bash
cd ~/gt/<rig> && bd list --status in_progress 2>/dev/null | head -20
```

For any in-progress bead with a suspiciously old heartbeat:
```bash
bd show <bead-id> 2>&1 | grep -E "Lease|heartbeat|Assignee|Updated"
```

**Lease expiry note**: expired leases on implementation workers are NORMAL
when the city was recently restarted (heartbeat gap = city downtime) or when
a long Magma computation is running. Check `gc session peek <session-id>` to
confirm the worker is actually computing:

```bash
gc session peek <session-id> 2>&1 | tail -10
```

An active Magma process (non-zero CPU, growing cpu-time) = computing, not
stuck.

### 3 — Brief pipeline

```bash
ls ~/gt/.beads/briefs/.pile/*.md 2>/dev/null | wc -l
ls ~/gt/.beads/briefs/stack/*.md 2>/dev/null | wc -l
gc session list --template mathcity.brief-operator 2>&1 | head -10
```

Report:
- `.pile/` count — briefs waiting to be shuffled
- `stack/` count — briefs awaiting Taylor adjudication
- Active brief-operator sessions

**Shuffler lock check**:
```bash
ls -la ~/gt/.beads/briefs/.shuffle.lock 2>/dev/null && echo "LOCK HELD" || echo "lock free"
```

A held lock lasting > 30 min without an active brief-operator session
processing is a stall (lock theft cascade bug gt-v3pisq). Remediation:
`rm ~/gt/.beads/briefs/.shuffle.lock` — only if no active session holds it.

### 4 — Dolt health detail

```bash
gc dolt health 2>&1
```

Key metrics to surface:
- Latency (warn ≥ 1000ms, critical ≥ 3000ms)
- Connections (warn ≥ 50, critical ≥ 200)
- Disk (warn ≥ 1G per DB)

High latency during concurrent `gc sling` runs is NORMAL and transient.
Sustained high latency with low connection count warrants `gc dolt logs`.

### 5 — READY queue

```bash
cd ~/gt && bd ready 2>&1 | head -20
cd ~/gt/hecke && bd ready 2>&1 | head -20
```

Report count of ready beads per rig. Many READY beads + no active
implementation workers = dispatch gap (run `/math-city-work` on the highest
priority item).

## Output format

```
FLEET — <N> live tmux sessions | <N> active agent sessions
  Workers: <list session IDs + templates + age>

BRIEF PIPELINE — pile: <N> | stack: <N> | brief-operators: <N> active
  Shuffler lock: <free|held by <session>>

IN-PROGRESS BEADS
  <rig>: <count> in_progress
    <bead-id> — <title> — lease: <ok|expired|>
    [peek: computing | stuck | unknown]

READY QUEUE
  <rig>: <N> ready beads (top 3: <ids>)

DOLT — <status> | latency: <Nms> | connections: <N>

STALLS / BLOCKERS
  [list any real stalls with diagnosis]
  [if none: "no stalls detected"]
```

## What this skill does NOT do

- Does not dispatch or sling any beads
- Does not reclaim leases or kill sessions
- Does not release the shuffler lock automatically
- Does not interpret brief contents or adjudicate
- Does not run gc status (lying metric — gs-0cy2)
