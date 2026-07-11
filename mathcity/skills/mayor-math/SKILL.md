---
name: mayor-math
description: Supplement to gc.mayor for Gas Town (gt HQ) context. Provides the correct rig-scoped sling mechanics for build-basic convoy workflows, including the rule that the bare gc.run-operator form doesn't resolve at HQ level and that gt-prefix beads have no worker fleet by default. Invoke alongside or after gc.mayor when about to sling work through build-basic in a Gas Town session.
---

# mayor-math

Supplement to [[gc.mayor]] with Gas Town (gt HQ) sling mechanics. The upstream gc.mayor
skill is community-shared and cannot be edited — use this skill to apply the correct
rig-scoped rules for our setup.

## The core rules

### Rule 1 — Always use the rig-scoped coordinator

The bare `gc.run-operator` does NOT resolve at HQ level. The city returns
"agent not found" and fails the sling. **Always** use the rig-scoped form:

```
<rig>/gc.run-operator
```

The rig prefix must match the convoy or bead prefix:

| Bead prefix | Correct coordinator |
|---|---|
| `he-` | `hecke/gc.run-operator` |
| `gs-` | `gascity/gc.run-operator` |
| `gsp-` | `gascity-packs/gc.run-operator` |
| `as-` | `agent_skills/gc.run-operator` |
| `gt-` | `gt/gc.run-operator` (only after Phase 0 pack.toml fix) |

Verify the rig has the coordinator before slinging:
```bash
gc agent list | grep "gc.run-operator"
```

### Rule 2 — build-basic requires a convoy

`build-basic` (the concrete child of `build-base`) has `target_required = true`.
You CANNOT use `--formula` with it. You MUST:

1. Create a convoy
2. Add bead(s) to it
3. Sling using `--on build-basic` against the convoy ID

`build-base` itself is `internal = true` — it does NOT appear in `gc formula catalog`
and must NEVER be named in a sling. Always name the concrete child (`build-basic`,
`superpowers-build`, `compound-build`, etc.).

### Rule 3 — gt HQ has no worker fleet by default

The `gt-` prefix HQ rig only has `bd.dog`, `claude`, `core.control-dispatcher`. The
full worker fleet (`gc.requirements-planner`, `gc.design-author`, `gc.task-decomposer`,
`gc.implementation-worker`, `gc.implementation-reviewer`) is present only at child rigs
via `defaults.rig.imports.gc` in city.toml — NOT at HQ.

**Fix (Phase 0):** Add these to `~/gt/pack.toml` and run `gc import install && gc supervisor reload`:
```toml
  [imports.gc-roles]
    source = "/Users/tdupuy/repos/gascity-packs/gascity/roles"
  [imports.pr-pipeline]
    source = "/Users/tdupuy/repos/gascity-packs/pr-pipeline"
```

Until that fix is applied, file work that needs `build-basic` in rigs that have workers:
- `he-` prefix → hecke rig
- `gs-` prefix → gascity rig
- `gsp-` prefix → gascity-packs rig
- `as-` prefix → agent_skills rig

### Rule 4 — Rig prefix must match the work's target repo

Per AGENTS.md: "Any work towards beads related to a specific repository needs to be
performed in the `~/repos` version of the repository."

| If the work is a PR to... | File the bead as... |
|---|---|
| `gastownhall/gascity` core | `gs-` (gascity rig) |
| `gastownhall/gascity-packs` | `gsp-` (gascity-packs rig) |
| `gastownhall/agent-skills` | `as-` (agent_skills rig) |
| `~/gt` config repo itself | `gt-` (HQ rig) |
| hecke math repo | `he-` (hecke rig) |

DO NOT file gascity core PRs as `gt-` beads — they cannot reach the right repo.

## Correct build-basic sling pattern

```bash
# Step 1 — Create bead in the rig with workers
bd create -t feature -p 2 -T "<title>" -m "<body>" --rig <rig>   # → <bead-id>

# Step 2 — Create convoy
gc convoy create <slug> --owned \
  --target <branch> \
  --merge local \
  --owner gastown.mayor
# note convoy ID (e.g., he-xyz)

# Step 3 — Add bead to convoy
gc convoy add <convoy-id> <bead-id>

# Step 4 — Write plan artifacts (requirements.md + implementation-plan.md, status: approved)
mkdir -p ~/gt/<rig>/plans/<slug>
# ... write artifacts ...

# Step 5 — Sling with rig-scoped coordinator
gc sling <rig>/gc.run-operator <convoy-id> --on build-basic \
  --var artifact_root=/Users/tdupuy/gt/<rig>/plans/<slug> \
  --var requirements_path=/Users/tdupuy/gt/<rig>/plans/<slug>/requirements.md \
  --var plan_path=/Users/tdupuy/gt/<rig>/plans/<slug>/implementation-plan.md \
  --var drain_policy=separate \
  --var interaction_mode=interactive \
  --var review_mode=agent \
  --var push=false \
  --var open_pr=false
```

## Lightweight dispatch (no build-basic)

For atomic tasks that don't need the full requirements→plan→implement→review pipeline:

```bash
# Route directly to a polecat (no convoy needed):
gc sling <rig>/gastown.polecat <bead-id>

# Targetless formula (formula must NOT have target_required):
gc sling <rig>/gc.run-operator <formula-name> --formula --var key=value
```

## Cross-reference

- [[gc.mayor]] — the upstream coordinator skill this supplements
- `~/gt/tmp-for-taylor/master-plan-workers-and-dispatch.md` — full Phase 0-5 plan
- `~/gt/tmp-for-taylor/build-base-vs-build-basic.md` — build-base vs build-basic deep dive
