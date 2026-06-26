# Mathematics Pack

Research-tooling pack for math projects running under Gas City. Initial scope:
a `codex` agent role that performs targeted consults (LaTeX review, Magma
critique, theorem-sketch sanity checks, pinpoint-citation pulls) against
research artifacts. Future scope, queued in `PLAN.md`, covers wrapping the
agent in formulas and orders for repeatable workflows (e.g. notes-section
review, Magma diff-alg / Clifford-algebra checks, hecke-style notes pipelines).

## Status: initial stub

This pack is the scaffold for math-research agentry. The design space is still
open: see `PLAN.md` for the five queued questions (generalist vs. variants,
composition with polecat/order/skill primitives, the `create-gas-city-agent`
skill, math-pack home structure, first use case) and the five future polecat
dispatches that flesh it out.

## Import

```toml
[imports.mathematics]
source = "../packs/mathematics"
```

Use the pack as a rig pack for projects that need math-specific agentry. It
imports `gascity` (workflow primitives) and `gastown` (rig roles) transitively
so the codex agent can compose with the standard worker pool.

## What's in the pack

- `pack.toml` — imports + agent stamping (currently stub; no `[[named_session]]`
  until the generalist-vs-variants question resolves)
- `README.md` — this file
- `PLAN.md` — design-space record migrated from the superseded `as-4wx`
  planning bead (see Privacy notes below)
- `agents/codex/agent.toml` — stub definition of the codex agent. Marks the
  shape ("this is where the agent lives") without committing to its scope
  or wake mode
- `formulas/` — empty. Future formulas (e.g. `mol-codex-review`,
  `mol-latex-pinpoint`) land here once the first use case is fixed
- `orders/` — empty. Future scheduled orders (e.g. periodic notes-section
  sweeps) land here
- `skills/` — empty. Future skills (e.g. `codex-consult`, `latex-review`,
  `create-gas-city-agent`) land here
- `assets/` — empty. Templates / helper scripts land here as the agent
  acquires runtime needs

## Privacy

**This pack is PUBLIC.** Per Taylor: "I certainly don't want that public
because it could be insecure." That refers to credentials, not to agent
definitions. The split is:

- **OK to ship in this pack**: agent definitions (TOML), prompt templates,
  formulas, orders, skill descriptions, README / PLAN content
- **NEVER in this pack**: Codex API keys, PATs, any secret value

When configuration eventually needs a credential, the pack references the
*env var name* (e.g. `$CODEX_API_KEY`) — the actual value stays in
1Password / Keychain / a gitignored shell rc. The
`[[never-echo-credentials]]` memory governs the discipline.

## Codex MCP prerequisite

The codex agent invokes Codex via MCP, configured at user scope (per
verdict A on `he-j6zp`). Until the operator action on `~/.claude.json`
lands, the agent is definitionally a stub — the pack ships, but no
formula or order should fire that depends on a live Codex MCP.
