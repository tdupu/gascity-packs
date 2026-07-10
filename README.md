# gascity-packs

A collection of opt-in [Gas City](https://github.com/gastownhall/gascity) packs.

Gas City is an orchestration-builder SDK for multi-agent coding workflows. 

A *pack* is a unit of workspace configuration: agents, commands, services,
formulas, skills, hooks, template fragments, or any combination. 

Packs are optional. A city with zero packs is valid and boots successfully.

Packs compose through `pack.toml` imports, so a city can opt into any subset of the packs in
this repo without forking. 

Skills in a pack are stored in `skills/` and automatically reach agent skills as `.claude/skills` symlinks, see[skills materialization](./docs/skills-materialization.md).

This README assumes familiarity with beads, formulas, rigs, and orders. For the full model (cities, rigs, formulas, beads, runtime providers) see the [Gas City README](https://github.com/gastownhall/gascity). 

## Sponsors

<p align="center">
  <a href="https://blacksmith.sh/">
    <img src="docs/images/blacksmith-powered.png" alt="Powered by Blacksmith" height="40">
  </a>
</p>

## Using a pack

Each pack documents its own prerequisites, import snippet, and usage.

The canonical path is the import CLI — it writes the import, fetches the
latest release, and pins the commit in `packs.lock`:

```sh
gc import add https://github.com/gastownhall/gascity-packs.git//bmad
```

Which is equivalent to this in `city.toml` (or any pack's `pack.toml`),
followed by `gc import install`:

```toml
[imports.bmad]
source = "https://github.com/gastownhall/gascity-packs.git//bmad"
```

Contributors working on the packs themselves can clone this repo and point
`source` at a local path instead:

```toml
[imports.bmad]
source = "../gascity-packs/bmad"
```

See [Contributing/Development](./README-contributing.md) for the full workflow around hacking on packs, publishing registry releases, and release compatibility gates.

## Start here: first build in about ten minutes

If you just installed Gas City and want a working multi-agent build factory,
this is the shortest path. Each step is copy-pasteable; swap names to taste.

**Install Gas City and start a city** (skip steps you have already done):

```sh
brew install gascity
gc init ~/my-city
cd ~/my-city
gc start
```



**Add the repository you want agents to work on as a rig:**

```sh
git clone https://github.com/you/your-project
cd your-project
gc rig add .
```



**Import the base pack.** 

From the city directory:

```sh
gc import add --name gc https://github.com/gastownhall/gascity-packs.git//gascity
```

This writes the import, fetches the latest release, and pins it in`packs.lock` — no clone needed. (`gc import upgrade gc` moves the pin later; contributors hacking on the packs themselves can point `source` at a local clone instead.)



**Import the rig roles**.

This is done in your city's `city.toml`. 

Rig-scoped imports are declared on the rig entry:

```toml
[[rigs]]
name = "your-project"

[rigs.imports.gc]
source = "https://github.com/gastownhall/gascity-packs.git//gascity/roles"
```

The city-level import provides the workflow formulas and the `gc.mayor` coordinator skill; the rig-level `roles` import provides the worker agents (`gc.implementation-worker`, `gc.requirements-planner`, and friends) that the formulas route work to. Run `gc import install` after editing to fetch anything newly referenced.

**Run your first build.** 

Create a bead describing the goal, then launch the starter factory against it:

```sh
gc bd create "Add a --json flag to the export command"
gc sling gc.run-operator <bead-id> --on build-basic \
  --var artifact_root=plans/json-flag/build
```

`build-basic` walks 

requirements → plan → plan review → decomposition → parallel implementation → a three-lane review fanout → finalize.

The build artifacts (which include requirements, plan, review reports, and a `factory-run.md` summary) land under `artifact_root` in your rig.

## List of packs

Each top-level directory is either a pack or a group of related packs:

- A directory containing `pack.toml` is itself a pack; import it by path.
- A directory without `pack.toml` groups related subpacks and typically ships
  an `all/` rollup that imports the group as one.

Each pack's README has its own quick start and is linked below. For a table mapping every pack to the process it runs and when to reach for it, see [README-pack-list.md](./README-pack-list.md); for build-methodology and Slack tiering comparisons, see [README-featured.md](./README-featured.md).

The `Build methodology` packs below all build on one shared contract: `gascity` provides the `build-base` workflow and its default `build-basic` implementation, and `bmad`, `compound-engineering`, `superpowers`, and `gstack` each import `gascity` as `gc` and implement that same contract with their own vendored formulas and prompt assets. See [gascity/REQUIREMENTS.md](./gascity/REQUIREMENTS.md) for the normative requirements every methodology pack is built on top of and must preserve.

| Pack | Category | Description |
| --- | --- | --- |
| [gascity](./gascity/README.md) | Build methodology | The `build-base` workflow contract and the default `build-basic` implementation. |
| [bmad](./bmad/README.md) | Build methodology | Document-first delivery (PRD → architecture → stories) as `bmad-build`. |
| [compound-engineering](./compound-engineering/README.md) | Build methodology | The widest reviewer-persona fanout, as `compound-build`. |
| [superpowers](./superpowers/README.md) | Build methodology | Hard approval gates and strict per-task TDD, as `superpowers-build`. Vendors [Jesse Vincent](https://github.com/obra)'s [Superpowers](https://github.com/obra/superpowers) skill library. |
| [gstack](./gstack/README.md) | Build methodology | Founder/PM-flavored gates plus QA and release-readiness, as `gstack-build`. |
| [cass](./cass/README.md) | Agent context | Adds a shared `cass-search` prompt fragment and Claude skill overlay for searching past coding-agent sessions. |
| [slack-mini](./slack-mini/README.md) | Slack (tier 1) | Minimal mention bridge and outbound messaging to a single channel. |
| [slack-channel](./slack-channel/README.md) | Slack (tier 2) | Shared channel routing and session identity for a few named sessions. |
| [slack-full](./slack-full/README.md) | Slack (tier 3) | Slash commands, interactive modals/buttons, peer fanout, and multi-rig routing. |
| [pr-pipeline](./pr-pipeline/README.md) | Contributor workflow | Author-side PR formulas: plan, blast-radius mapping, scorecard self-review, pre-push gate. |
| [contributing](./contributing/README.md) | Contributor workflow | The full external-contributor lifecycle for gastownhall/gascity, built on `pr-pipeline`. |
| [gastown](./gastown/README.md) | Coordination & city | The default Gas Town coding workflow: city/rig coordination, dog pool, and the polecat/refinery build-and-review pipeline. |
| [oversight-rig](./oversight-rig/README.md) | Coordination & city | An always-on, rig-scoped project-lead that triages and dispatches its own ready work with severity-based escalation. |
| [discord](./discord/README.md) | Service integration | Discord services, commands, and prompt fragments for Gas City. |
| [github](./github/README.md) | Service integration | GitHub webhook intake services and commands for Gas City. |
| [mathcity](./mathcity/README.md) | Research & ops | The brief pipeline that routes math research decisions (branches, PRs, experiments) to human adjudication. |
| [ops](./ops/README.md) | Research & ops | Operational/substrate primitives: experiment-lifecycle monitoring, cross-host heartbeat, dispatch-reliability instrumentation, restoration drills. |
| [runtime-cloudflare](./runtime-cloudflare/README.md) | Runtime | Ships the `gc-runtime-cloudflare` executable, proxying Gas City sessions to a Cloudflare Worker runtime. |

## Which pack do I use?

Most cities start with the base [gascity](./gascity/README.md) pack and add tiered Slack/contributor packs as needed. If you want a different build methodology, or need the Slack tiering comparison in one place, see **[README-featured.md](./README-featured.md)** for the full "which pack do I use" comparison tables and rationale.

## Contributing/Development

Issues and pull requests are welcome. See the **[Development Guide](./README-contributing.md)** for the full contributor workflow: publishing registry releases, publishing a new pack to the registry, and the release compatibility/inference gates.
