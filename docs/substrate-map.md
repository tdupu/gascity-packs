# Gastown/Gascity Substrate Map

Reference for Taylor: agent classes, formula governance, pool sizing, and usage signals.  
See also: [`docs/skills-materialization.md`](skills-materialization.md)

---

## Agent Classes

### City-scoped (always-on named sessions)

| Agent | Role | Work shape | Spawn model |
|-------|------|------------|-------------|
| **mayor** | Coordinates requirements, plans, creates beads, launches formula workflows | Long-running coordinator; fields requests from Taylor or clerk; farms out implementation | Named session, `mode=always`, singleton (`max=1`) |
| **deacon** | LLM sidekick to controller: periodic tasks (gc doctor, digest generation, orphan process cleanup, stuck-dog detection) | Patrol wisp loop (`mol-deacon-patrol`); each iteration = one wisp; exponential backoff when idle | Named session, `mode=always`, singleton |
| **boot** | Deacon watchdog: answers "is deacon stuck?" on each wake | Ultra-short wake: peek deacon pane, check wisp age, drain-ack, exit | Named session, `mode=always`, singleton |
| **dog** | Utility recovery / stuck-agent shutdown dance, Dolt maintenance | Pool worker: claims warrant beads, runs `mol-shutdown-dance` | Pool, min=0, max=3 |

### Rig-scoped (per-rig, gastown pack)

| Agent | Role | Work shape | Spawn model |
|-------|------|------------|-------------|
| **witness** | Per-rig work-health monitor: orphaned bead recovery, refinery queue staleness, polecat health, help-mail triage | Patrol wisp loop (`mol-witness-patrol`); NOT process management (that's the controller) | Named session, `mode=always`, singleton per rig; `max_session_age=5h` (cred-cache rotation) |
| **refinery** | Merge review: rebase polecat branches onto base, run tests, merge, close beads; publishes PRs in `mr` mode | Patrol wisp loop (`mol-refinery-patrol`); one merge per wisp | Named session, `mode=on_demand`, singleton per rig |
| **polecat** | Feature-branch implementation workers: claim work, create branch, implement, push, reassign to refinery | Ephemeral pool workers; each runs `mol-polecat-work`; self-clean on submit | Pool, min=0, max=5 per rig |

### Rig-scoped (gascity pack, formula-driven workflows)

| Agent | Role | Spawn model |
|-------|------|------------|
| **claude / codex pool workers** | Generic pool workers; default sling formula is `mol-do-work` (read bead, implement, commit, close) | Pool, min=0, max=4 per rig (`claude`) |
| **run-operator** | Deterministic setup, gates, metadata, finalization in gascity multi-step formulas | Spawned per formula step via `gc.run_target` metadata; ephemeral |
| **review-synthesizer** | Presents briefs to Taylor, synthesizes review findings, records verdicts | Spawned per review leg; ephemeral |

### City-layer (Go process, not an LLM)

| Component | Role |
|-----------|------|
| **controller** | Manages session lifecycle: starts/stops/restarts agents, reconciles pool demand, runs health checks, dispatches `patrol_interval` ticks |
| **control-dispatcher** | Deterministic convoy compiler; non-LLM Go process that drives formula step sequencing for graph.v2 workflows |

---

## How Formulas Govern Agents

Gastown patrol formulas wire named sessions into self-refreshing loops:

```
mol-witness-patrol   →  witness (rig, always-on)
mol-refinery-patrol  →  refinery (rig, on_demand)
mol-deacon-patrol    →  deacon (city, always-on)
mol-polecat-work     →  polecat pool worker (claimed via gc hook --claim)
mol-shutdown-dance   →  dog pool worker (claimed via gc hook --claim)
mol-digest-generate  →  dog pool worker (periodic, dispatched by deacon)
```

**Loop mechanism:** each patrol session pours its next wisp before draining. The controller only bootstraps the first wisp; the formula sustains the loop from there.

**Pool work dispatch (non-patrol):** `gc sling` or `bd mol pour` pours a wisp onto a convoy with a target agent/pool. Workers claim it via `gc hook --claim --drain-ack --json`. The default pool formula in the gascity/core pack is `mol-do-work` (read → implement → commit → close → drain-ack).

**Polecat handoff contract:** polecat sets `metadata.branch` + `metadata.target` on the work bead, reassigns to refinery, and exits. Refinery merges and closes. No separate MR beads.

---

## Where Sizing Is Set

```
agent.toml (in pack)                    # canonical source
  └─ min_active_sessions                # floor (pool workers only)
  └─ max_active_sessions                # ceiling
  └─ idle_timeout                       # drain after idle
  └─ max_session_age                    # forced cycle (witness: 5h)

pack.toml [[named_session]]             # promotes agent to always-on
  └─ mode = "always" | "on_demand"

city.toml [daemon]                      # controller behavior
  └─ patrol_interval = "30s"            # how often controller reconciles pools
  └─ max_restarts = 5 / restart_window  # crash-loop guard

city.toml [[rigs]]                      # per-rig overrides (rarely needed)
```

**Override chain:** `agent.toml` defaults → rig-level overrides in `city.toml` → nothing else; there is no launchd / plist layer for agent counts.

To inspect resolved values: `gc config show` or `gc config explain`.

---

## Read-Effect Timing

| Change | Effect timing |
|--------|---------------|
| `max_active_sessions` / `min_active_sessions` in agent.toml | Next controller reconcile tick (~30s, set by `patrol_interval`) |
| Formula step descriptions | Immediate for new pours; in-flight sessions use the version they started with |
| Pack structural changes (new agents, named_session declarations) | Requires `gc pack refresh` to re-materialize, then controller restart to pick up new session templates |
| `named_session mode` changed to/from `always` | Requires `gc stop && gc start` (controller re-evaluates on startup) |
| Skill SKILL.md edits (local-path imports) | Propagate live (symlink); no reload needed |
| Skill SKILL.md edits (git-sha imports) | Requires `gc pack refresh` to update frozen snapshot |

---

## Usage Signals

| Signal | Where |
|--------|-------|
| Active sessions by agent type | `gc session list` — shows template, state, last-active time |
| Per-run cost and token usage | `gc costs` — rows per run with IN/OUT/CACHE columns |
| Session reliability (crash rate, idle-kill rate) | `gc analyze reliability` |
| City health (doctor findings, formula warnings) | `gc doctor` |
| Pool demand vs. active count | `gc session list` filtered by agent name; compare active vs. max |
| Polecat usage % (the 15%/week figure) | `gc analyze reliability` — polecat session events / total session events in rolling window; denominator is session-starts per week across all agents in the city |
| Live activity dashboard | `gc dashboard` — web UI at the configured API server port |

The 15%/week polecat figure means polecats accounted for 15% of all session-starts in the trailing week. A low percentage is normal when most rigs are idle; a high percentage means heavy implementation churn.

---

## Composition-First Pattern

Skills → formulas → agents → pack → rig/city:

```
gascity-packs/<pack>/skills/<name>/SKILL.md        # skill source
    ↓  gc materializes as symlink on every tick
.gc/agents/<rig>/<agent>/.claude/skills/<key>.<name>  # provider sink

gascity-packs/<pack>/formulas/mol-*.toml           # formula (step machine)
    references skills in step descriptions
    declares [vars] for rig-level overrides

gascity-packs/<pack>/agents/<name>/agent.toml      # agent config
gascity-packs/<pack>/agents/<name>/prompt.template.md

gascity-packs/<pack>/pack.toml                     # pack definition
    [[named_session]] declarations
    [global] session_live hooks

city.toml [imports.<key>]  →  pack resolution      # city wires it up
city.toml [[rigs]] + [defaults.rig.imports]        # rig inheritance
```

**Pack import keys matter:** the key in `[imports.<key>]` becomes the agent-name prefix (`gastown.polecat`, `gc.mayor`). Named sessions use this binding; pool workers resolve their routing target via the same prefix.

**Two pack roles in gastown:**
- `workspace.pack` → city-scoped agents (mayor, deacon, boot, dog)
- `rigs[].pack` → rig-scoped agents (witness, refinery, polecat)

See pack.toml comments for the exact distinction.
