---
name: mayor-math
description: Supplement to gc.mayor for Gas Town (gt HQ) context. Provides the correct rig-scoped sling mechanics for build-basic convoy workflows, including the rule that the bare gc.run-operator form doesn't resolve at HQ level and that gt-prefix beads have no worker fleet by default. Invoke alongside or after gc.mayor when about to sling work through build-basic in a Gas Town session.
---

# mayor-math

Supplement to [[gc.mayor]] with Gas Town (gt HQ) sling mechanics. The upstream gc.mayor
skill is community-shared and cannot be edited — use this skill to apply the correct
rig-scoped rules for our setup.

## Rule 1 — Always use the rig-scoped coordinator

The bare `gc.run-operator` does NOT resolve at HQ level. Always use:

```
<rig>/gc.run-operator
```

| Bead prefix | Correct coordinator |
|---|---|
| `he-` | `hecke/gc.run-operator` |
| `gs-` | `gascity/gc.run-operator` |
| `gsp-` | `gascity-packs/gc.run-operator` |
| `as-` | `agent_skills/gc.run-operator` |
| `gt-` | `gt/gc.run-operator` (only after Phase 0 pack.toml fix) |

## Rule 2 — build-basic requires a convoy

`build-basic` has `target_required = true`. You CANNOT use `--formula`. Create a convoy,
add bead(s), then sling against the convoy ID.

## Rule 3 — gt HQ has no worker fleet by default

The `gt-` prefix HQ rig only has `bd.dog`, `claude`, `core.control-dispatcher`. Full
workers (`gc.requirements-planner`, `gc.design-author`, `gc.task-decomposer`,
`gc.implementation-worker`, `gc.implementation-reviewer`) exist only at child rigs.
File work in `he-`, `gs-`, `gsp-`, or `as-` until Phase 0 is applied.

## Rule 4 — Rig prefix must match the work's target repo

| Work targets... | File bead as... |
|---|---|
| `gastownhall/gascity` core | `gs-` |
| `gastownhall/gascity-packs` | `gsp-` |
| `gastownhall/agent-skills` | `as-` |
| `~/gt` config repo | `gt-` |
| hecke math repo | `he-` |

## Quick sling pattern

```bash
# 1 — bead in rig with workers
bd create -t feature -p 2 -T "<title>" -m "<body>" --rig <rig>

# 2 — convoy
gc convoy create <slug> --owned --target <branch> --merge local --owner gastown.mayor
gc convoy add <convoy-id> <bead-id>

# 3 — plan artifacts (requirements.md + implementation-plan.md, status: approved)
mkdir -p ~/gt/<rig>/plans/<slug>

# 4 — sling
gc sling <rig>/gc.run-operator <convoy-id> --on build-basic \
  --var artifact_root=~/gt/<rig>/plans/<slug> \
  --var requirements_path=~/gt/<rig>/plans/<slug>/requirements.md \
  --var plan_path=~/gt/<rig>/plans/<slug>/implementation-plan.md \
  --var drain_policy=separate \
  --var interaction_mode=interactive \
  --var review_mode=agent \
  --var push=false \
  --var open_pr=false
```

For atomic tasks: `gc sling <rig>/gastown.polecat <bead-id>`

## Reference

- [[gc.mayor]] — upstream coordinator skill
- `~/gt/mathcity-mayor/` — QUIMBY session state, restart context, session catalog
