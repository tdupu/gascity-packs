# PLAN — codex-as-gas-city-agent design space

**Status**: Open. Design space, not commitments. Future polecat dispatches
flesh out each branch as Taylor calls them.

**Provenance**: Migrated from `as-4wx` (parking bead, superseded
2026-06-25 by Taylor's Path D verdict: math-packs becomes a `mathematics/`
folder in `gascity-packs`). The original PAT-create blocker that parked
`as-4wx` is bypassed — `gascity-packs` already exists.

**Anti-pattern guard** (per `[[check-docs-before-designing-workarounds]]`):
before any of the open questions below is answered with an implementation,
the deciding polecat MUST first:

1. Read `docs.gascity.com/tutorials/02-agents` for the existing agent-creation
   patterns
2. Survey existing agent definitions in `gastown/`, `superpowers/`, and
   `bmad/` packs — they cover the realistic shape space
3. Check `gc` subcommands (in the spirit of `[[reference-bd-backup-subcommand]]`)
   for a pre-existing `gc agent create` or similar

Don't reinvent.

## Open design questions

### Q1. One generalist agent OR multiple variants?

**(a)** Single `codex` agent that takes a config arg per-invocation
(persona / mode / tools as run-time parameters).

**(b)** Multiple narrow agents: `codex-reviewer`, `codex-prover`,
`codex-coder`, `codex-thinker`, ...

**Notes**: The gascity `02-agents` docs allow multiple `[[agent]]` blocks
per pack, so (b) is structurally cheap. The trade-off is prompt-template
maintenance burden vs. runtime config complexity. Variants give crisper
formula composition (an `mol-codex-review` formula targets `codex-reviewer`
specifically); a generalist needs every formula to pass the persona arg.

### Q2. How does the agent compose with existing primitives?

Candidates:

- As a **polecat-type agent in a pool** (claims work via `gc hook`, runs
  formula steps, hands off)
- As an **order-runner** (cooldown-trigger + exec — scheduled consults,
  not work-claim driven)
- As a **skill** that polecats invoke (`codex-consult` as a callable from
  within a polecat formula step)
- As a **named always-on session** that other agents nudge

Per `[[reference-codex-mcp-available]]` + `he-j6zp` verdict A (user-scope
Codex MCP), the invocation channel is MCP — that constrains but doesn't
decide the composition shape.

### Q3. What is the `create-gas-city-agent` skill?

Taylor mentioned this mid-session as a separate artifact. Likely shape:
a skill (probably in the `skill-creator-plus` family) that generates a
new pack agent from a description — emits `pack.toml` `[[agent]]` block,
prompt template, tool config, scope/mode defaults.

**Use case**: "I want a `codex-reviewer` agent" → run skill → emit agent
definition under the current pack.

**Open**: does this skill live in `mathematics/skills/` or in a more
general place (`gastown/skills/`, `skill-creator-plus`)? Probably the
latter — agent-creation is not math-specific — but it lands on the
roadmap here because the math-pack is the first concrete user.

### Q4. Math-pack home structure

Per `[[project_math_pack_architecture]]`: math skills ship as bare
`SKILL.md` first, then get wrapped in formulas + orders + assets per the
gascity-packs/superpowers shape.

**Open**: where do the codex-as-agent definitions live within the
math-pack structure?

- All under `mathematics/agents/` per the current scaffold (uniform with
  gastown), OR
- Split: `agents/` for runtime configs, `skills/` for SKILL.md-first
  drafts that mature into agents over time

Per `[[project_brief_pipeline_as_formulas_and_orders]]`, mature workflows
become TOML formulas. The codex-agent likely follows the same arc:
SKILL.md → formula → agent.toml.

### Q5. What is the FIRST use case?

Candidates pulled from prior consults:

- **LaTeX review**: pinpoint-citation check on a `notes.tex` section
  (`latex/scratch/he-ebkt-predicate-random-method-2026-06-24.md` is the
  reference style)
- **Magma critique**: review of `magma_diff_alg` / `magma_clifford_algebras`
  source for correctness or style
- **Theorem-sketch sanity check**: read a draft proof, surface gaps
- **Notes pipeline**: end-to-end "section → consult → revision" loop

**Concrete prior consult outputs to cross-link** (these are the
demonstrated capability surface):

- `he-2y55` (Langlands)
- `he-kl1y` (perfect-forms)
- `he-msqi` (Harder chain)
- `he-zarp` (cusp canonical)
- `he-hyr6` (Rahm-Sengun + Logan-Ellenberg)

The first use case should be something with a clear PASS/FAIL signal
so the codex agent's output is easy to score.

## Future polecat dispatches (queued, none firing now)

Once `mathematics/` lands and PLAN.md converges:

1. **Survey existing patterns** — research `docs.gascity.com/tutorials/02-agents`
   plus existing pack agent definitions (gastown, superpowers, bmad).
   Output: a short pattern catalog used to ground Q1 and Q2.
2. **Codex MCP integration** — gather MCP invocation patterns and token
   handling for the Codex provider. Output: a minimal `codex-consult`
   call recipe. Depends on `he-j6zp` verdict A operator action landing.
3. **Draft `codex-consult` skill** — bare `SKILL.md` first, per
   `[[project_math_pack_architecture]]` discipline. Output:
   `mathematics/skills/codex-consult/SKILL.md`.
4. **Wrap in formula + order** — once the SKILL.md stabilizes, lift the
   recipe into a TOML formula and (if a recurring use case appears) a
   scheduled order. Output:
   `mathematics/formulas/mol-codex-review.toml` (or named per Q1 outcome).
5. **First-use-case test** — file a test bead that runs the formula on
   a real artifact (e.g. a hecke `notes.tex` section). Output: a
   completed run with a verifiable consult artifact.

NONE of these fire now. They are dispatch slots Taylor (or the Mayor)
can sling once PLAN.md is settled.

## Cross-references

- `as-4wx` (parking bead; this PLAN supersedes; close on follow-up)
- `as-ajw` (this bead — pack-structure scaffold)
- `he-j6zp` (Codex MCP user-scope; pending Taylor operator action on
  `~/.claude.json`)
- `he-xqqm` (decision-pending bead under `he-j6zp`; verdict A absorbs)
- `he-xw0k` (original codex-algorithm research that surfaced the MCP gap)
- `he-2y55`, `he-kl1y`, `he-msqi`, `he-zarp`, `he-hyr6` — prior codex
  consult outputs (concrete capability surface)
- Memories: `[[project_math_pack_architecture]]`,
  `[[reference-codex-mcp-available]]`,
  `[[project_brief_pipeline_as_formulas_and_orders]]`,
  `[[never-echo-credentials]]`,
  `[[check-docs-before-designing-workarounds]]`,
  `[[reference-bd-backup-subcommand]]`

## Privacy reminder

This file is PUBLIC. Cross-references use bead IDs and memory slugs
only — never paste credentials, raw consult content, or anything else
that should stay private.
