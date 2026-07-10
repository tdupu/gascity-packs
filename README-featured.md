# Featured packs

Comparison tables and rationale for choosing between packs that serve the
same role. See the top-level [README.md](./README.md) for the full pack list
and quick start.

## Build methodology packs

The four methodology packs below replace `build-basic`'s stages with vendored,
battle-tested processes while keeping the same launch shape — import one at
city scope and sling its build formula instead (for example `--on
bmad-build`):

```sh
gc import add https://github.com/gastownhall/gascity-packs.git//bmad
```

### Which build pack should I use?

| Pack | Process it runs | Reach for it when |
| ---- | --------------- | ----------------- |
| [gascity](./gascity) (`build-basic`) | Requirements → plan → review → decompose → implement → three-lane review | You want the default starter factory with the fewest moving parts. |
| [bmad](./bmad) (`bmad-build`) | PRD → architecture → epics/stories → readiness gate → story-by-story implementation with self-check and acceptance audit → adversarial review | You want disciplined document-first delivery with explicit story decomposition and readiness checks. |
| [compound-engineering](./compound-engineering) (`compound-build`) | Brainstorm/plan → plan review → implement → the widest reviewer-persona fanout → resolution | Review depth matters most: correctness, security, performance, migrations, and API contracts each get their own reviewer lane. |
| [superpowers](./superpowers) (`superpowers-build`) | Brainstorm → written spec approval → per-task test-driven development → spec-compliance then code-quality review | You want hard approval gates before code and strict TDD per task. |
| [gstack](./gstack) (`gstack-build`) | Office-hours intake → multi-perspective plan review → build → staff review → QA → security → release readiness | You want founder/PM-flavored gates and explicit QA + release-readiness stages before shipping. |

All five expose the same launch variables (`interaction_mode`, `review_mode`,
`drain_policy`, `push`, `open_pr`, …), so switching methodology is a one-word
change to the formula name.

### Build methodology pack framework

Raw-framework subagents become Gas City fanouts. The vendored methodology text
is treated as source material for behavior, not runtime authority: if a raw
skill says to spawn a subagent, dispatch a task tool, or invoke a plugin
command, the pack should model that work as formula steps, expansion children,
drains, or fanout/fanin lanes.

Use two mode concepts when comparing methodology packs:

- `interaction_mode` describes human participation in planning and gates:
  interactive, autonomous, or headless.
- `review_mode` describes whether review is report-only, machine handoff, or
  an interactive top-level review that may apply safe fixes.

| Pack | What it vendors |
| --- | --- |
| [gascity](./gascity) | Provides the `build-base` workflow contract, the default `build-basic` implementation, and the `build-from-*` continuation entrypoints for resuming a build from existing artifacts. |
| [compound-engineering](./compound-engineering) | Imports `gascity` as `gc` and implements `build-base` with vendored [Every Inc.](https://github.com/EveryInc) [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) skills, agent personas, and Gas City-native review/finalization expansions. |
| [superpowers](./superpowers) | Imports `gascity` as `gc` and implements `build-base` with vendored skills from [Jesse Vincent](https://github.com/obra)'s [Superpowers](https://github.com/obra/superpowers) and Gas City-native development/review expansions. |
| [bmad](./bmad) | Imports `gascity` as `gc` and implements `build-base` with vendored [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) skills and Gas City-native story/review expansions. |
| [gstack](./gstack) | Imports `gascity` as `gc` and implements `build-base` with vendored [garrytan/gstack](https://github.com/garrytan/gstack) office-hours, autoplan, review, QA, security, documentation, and release-readiness skills mapped to Gas City fanouts. |

Every row above imports `gascity` as `gc` and is built on top of the same
`build-base` compatibility contract — durable formulas, fanouts, drains,
convoy identity, artifacts, gates, and mode handling — defined in
[gascity/REQUIREMENTS.md](./gascity/REQUIREMENTS.md). That ledger is
normative, not just descriptive: it specifies what each methodology
implementation must preserve (base anchors and their order, artifact and
traceability shape, `interaction_mode`/`review_mode` handling) when it swaps
in its own vendored process, so `bmad-build`, `compound-build`,
`superpowers-build`, and `gstack-build` stay compatible with the base pack
even as their stages diverge.

See the [build methodology framework audit](./docs/design/build-methodology-framework-audit.md)
for the current parity assessment and proposed beginner-friendly updates.

## Agent context packs

| Pack | Description |
| --- | --- |
| [cass](./cass) | Adds a shared `cass-search` prompt fragment and Claude skill overlay for searching past coding-agent sessions. |

## Slack packs

The Slack provider ships as three tiers — pick the smallest one that covers
your use case:

| Tier | Pack | Use it when |
| ---- | ---- | ----------- |
| 1 | [slack-mini](./slack-mini) | The mayor only needs to post status into a single channel. No bindings, no state. |
| 2 | [slack-channel](./slack-channel) | A few named sessions share channels with distinct identities — no slash commands or cross-rig routing. |
| 3 | [slack-full](./slack-full) | Slash commands, interactive modals/buttons, peer fanout, launcher-mode spawning, or multi-rig channel routing. |

See the [tiering design memo](./docs/design/slack-pack-tiering.md) for the
rationale.
