---
name: mayor-math
description: Supplement to gc.mayor for Gas Town (gt HQ) context. Provides the correct rig-scoped sling mechanics for build-basic convoy workflows, including the rule that the bare gc.run-operator form doesn't resolve at HQ level and that gt-prefix beads have no worker fleet by default. Invoke alongside or after gc.mayor when about to sling work through build-basic in a Gas Town session.
---

# mayor-math

Supplement to [[gc.mayor]] with Gas Town (gt HQ) sling mechanics. The upstream gc.mayor
skill is community-shared and cannot be edited — use this skill to apply the correct
rig-scoped rules for our setup.

## Canonical operation docs — READ FIRST (regression-proofed QUIMBY onboarding)

The hard-won gold, derived over 11 QUIMBY generations, lives in the mathcity pack
(`~/gt/gascity-packs/mathcity/docs/`):
- **QUIMBY-ONBOARDING.md** — index + S11-corrected operational truths (start here)
- **CITY-RESTART-CHECKLIST.md** — Phase 0–6 step-by-step to bring the city up + verify
- **CITY-OPERATION-REFERENCE.md** — architecture, pools/agents, brief pipeline, correct command surface
- **TEST-CYCLE-GUIDE.md** + **DOGFOOD-WORKFLOW.md** — the dogfood/test cycle

## Feed the machine via `build-basic-briefed` (S14-verified working)

**This is the dispatch mechanism for real work — use it.** build-basic-briefed does NOT
strand (the Q13 "silent strand / dead role-agents" alarm was a misdiagnosis — the
`named_session` fleet config was fixed 2026-07-14; every "stranded" build actually ran its
molecule steps; `he-j9wms` is moot; see `bd recall great-regression-misdiagnosis-s14`).

```
gc sling <rig>/gc.run-operator <bead> --on build-basic-briefed \
  --var interaction_mode=autonomous --var review_mode=agent \
  --var drain_policy=separate --var push=false --var open_pr=false
```

It runs the full build and fires a **decision brief** at the terminal step (not a publish;
`push=false` ships nothing) — that brief is how the machine surfaces work to Taylor's stack.
The `build-basic` / `interaction_mode=interactive` pattern below is retained for reference;
prefer build-basic-briefed. (`gastown.polecat` is a dead identity; use a live `gc.*` target.)

**ALWAYS verify the sling took (mandatory).** Immediately after slinging, confirm a worker
claimed it: `bd show <bead>` → non-empty **Assignee**, or `tmux -L gt ls` shows a fresh
`gc__run-operator` / `gc__implementation-worker` session. A sling you didn't verify is a
sling that may have stranded.

**Do NOT misread a slow build as a strand (S14 — this false alarm cost a whole session).**
build-basic-briefed molecules are SLOW and multi-step; three things look like failure but
are NORMAL:
- A molecule **ROOT stays OPEN by design** until every terminal step (finalize + brief)
  closes. An open root with closed child steps is *in-flight*, not stranded — count closed
  (`✓`) steps via `bd show <root>`; they climb over minutes.
- **`gc status` "stopped / 0 sessions" is usually a probe TIMEOUT**, not an idle fleet (it
  prints a stale fallback). Ground truth = `tmux -L gt ls` + climbing step-counts, never the
  dashboard count (`gs-0cy2`).
- The brief appears only AFTER the molecule reaches its terminal "Produce decision brief"
  step — no brief before then is latency, not a missing brief.

**Doctrine (S13/S14): feed the machine, don't hand-sling one-by-one.** The Mayor's job is
queue health + unblocking (file beads right, remove blockers, keep the graph clean); dispatch
ready work through build-basic-briefed and let the fleet pull. Stay available to Taylor.

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

For atomic tasks: `gc sling <rig>/gc.run-operator <bead-id>` (`gastown.polecat` is dead).

## Reference

- [[gc.mayor]] — upstream coordinator skill
- `~/gt/mathcity-mayor/` — QUIMBY session state, restart context, session catalog
