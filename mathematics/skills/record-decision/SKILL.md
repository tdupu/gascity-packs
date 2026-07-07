---
name: record-decision
description: Use whenever a decision needs to be recorded persistently in a bd-managed rig — Taylor adjudications, architecture choices, policy locks, brief-pipeline verdicts, gate-criterion additions. Enforces the `bd create -t decision` canonical primitive per the bd-decision-canonical architecture principle (gascity triage 2026-06-26, LD #10 + AP2). Refuses to write decisions to non-`bd decision` stores (no markdown files, no custom jsonl writes, no `bd remember`-with-decision-content). Trigger phrases include "record a decision", "log this decision", "file the verdict", "this needs to be a decision-record", "preserve this for posterity", or any moment when an agent or human surfaces a verdict / rationale / chosen-alternative that should survive across sessions and be queryable by future work.
---

> **Canonical copy**: `mathematics.record-decision` in gascity-packs. This agent-skills copy is retained as fallback.

# record-decision

The canonical way to record a decision in the gascity / beads substrate. **Don't roll your own** — `bd decision` already exists with a structured template and queryability; this skill enforces using it.

## When to use

A "decision" is **a verdict that closes deliberation**, with a recorded rationale and alternatives. Examples:

- Taylor adjudicates a brief: "use iCloud Drive for backups, not DoltHub Pro"
- A worker reaches a verdict on an architecture choice: "math-pack is the canonical home for our custom substrate"
- A policy lock: "all hard gates → TOML formalized"
- A brief-pipeline verdict: "consolidate the 3 parallel specs via lineage-audit-then-union"
- A gate-criterion addition: "add DEFER-ratify-existing-HELD to no-brainer classifier"

A "decision" is **NOT**:
- An ephemeral observation → use a comment or chat
- A cross-session **fact** that isn't a chosen-alternative → use `bd remember` (memories) instead
- A TODO / task / work item → use `bd create` with `--type task`/`feature`/`bug`/etc.
- A judgment that needs human review before recording → that's a brief; use the brief-pipeline (see `[[brief-prep]]`)

## How (canonical command)

```bash
bd create "<title>" --type decision \
  --description "$(cat <<'EOF'
## Decision

<one-sentence summary of what was decided>

## Rationale

<why this was chosen — the substantive reasoning>

## Alternatives Considered

- **<alt 1>**: <why rejected>
- **<alt 2>**: <why rejected>

## Affects

- <bead IDs, files, or area descriptions>

EOF
)"
```

`--type decision` is a first-class beads type with aliases `dec` and `adr`. After creation, link to any beads the decision affects:

```bash
bd dep add <decision-id> <affected-bead-id> --type related
```

## What this skill does NOT do

- ❌ Write decisions to a markdown file (e.g., `~/gt/.claude/decision-*.md` files in the triage session are a historical session-artifact pattern, NOT the canonical going-forward path)
- ❌ Write to `~/gt/<rig>/.beads/decisions.jsonl` directly (those 3 legacy ledgers stay as historical archives per LD #10; new decisions go through `bd decision`)
- ❌ Use `bd remember "<decision text>"` (`bd remember` is for cross-session facts, NOT decisions; the bd-CLI canonical distinction is: STORE-persistent-knowledge vs RECORD-adjudicated-verdict)
- ❌ Create a "decision" bead with `--type task` and a `[DECISION]` title-marker (use the real `bd decision` type; title-markers are pre-bd-decision-era pattern)
- ❌ Skip the Decision / Rationale / Alternatives / Affects template (the structured form is what makes decisions queryable + supersede-able)

## Refuse-and-explain

If an agent or user asks to record a decision via any non-canonical path, refuse and explain:

> "Per the bd-decision-canonical architecture principle (gascity triage 2026-06-26), all decisions go through `bd create -t decision` with the canonical template. The path you proposed (`<their path>`) would create a parallel decision store, which the principle explicitly forbids. Let me reformulate this as `bd decision`:
>
> ```bash
> bd create '<title>' --type decision --description ...
> ```
>
> Sound good?"

Then proceed to the canonical command.

## Supersede pattern (when a decision is replaced)

When a new decision replaces an old one:

```bash
# 1. Record the new decision (as above)
NEW_ID=$(bd create "<title>" --type decision --description "..." --silent)

# 2. Link new → old via 'related' dependency
bd dep add $NEW_ID <old-decision-id> --type related

# 3. Note the supersession on the old decision
bd comments add <old-decision-id> "Superseded by $NEW_ID: <brief reason>"

# 4. Close the old decision
bd close <old-decision-id> --reason "Superseded by $NEW_ID"
```

## List / search existing decisions

```bash
bd list --type decision               # all open decisions in this rig
bd list --type decision --all         # incl. closed/superseded
bd show <decision-id>                 # single decision detail
bd comments <decision-id>             # discussion / supersession history
bd search "<keyword>"                 # find by title or body content
```

For cross-rig query (per beads-topology canonical: prefix-scoped isolation, requires Dolt-direct):

```bash
# Direct Dolt query across the shared store
dolt sql -q "SELECT id, title, status FROM issues WHERE issue_type = 'decision' AND status = 'open'"
```

(Or use the future `mathematics/formulas/cross-rig-decision-query.toml` math-pack tooling once it's built.)

## Cross-references

- **bd-decision canonical doc:** `~/repos/beads/plugins/beads/skills/beads/commands/decision.md`
- **Architecture principle (this session):** `~/gt/.claude/details-2026-06-26/decision-2026-06-26-grill2-architecture-bd-decision-is-canonical.md`
- **Beads-topology canonical:** `https://docs.gascity.com/reference/internal/beads-topology.md` (prefix-scoped per rig; cross-rig requires Dolt-direct)
- **Golden rule:** `~/gt/.claude/details-2026-06-26/decision-2026-06-26-grill2-PRINCIPLE-golden-rule-dont-violate-docs.md` ("don't violate the docs" — bd canonical wins over local convention)
- **CONTEXT.md** at `~/gt/CONTEXT.md` §Gas City has the canonical primitive ordering

## Why this skill exists

History: prior to grill-2 (2026-06-26 ~13:00 -1000), decisions were scattered across 3 different `.jsonl` files (bd-side, brief-pipeline, mayor-side) + bd memories + title-marker beads + markdown files. The session locked `bd decision` as canonical (LD #10 + AP2). This skill is the **enforcement mechanism** that future agents read before recording a decision — they see the canonical command + the refuse-and-explain pattern + the structured template.

Per Taylor's verbatim 2026-06-26 13:58: *"We need this to work around the bd decision framework"* and *"That should impose what happens"* (the principle drives downstream behavior). This skill operationalizes that.

## What stays in the legacy stores (do NOT migrate)

The 3 historical `decisions.jsonl` files (`~/gt/hecke/.beads/decisions.jsonl` — 29 records; `~/gt/hecke/.beads/briefs/decisions.jsonl` — 301 records; `~/gt/.gc/agents/mayor/decisions.jsonl` — 23 records) stay as LEGACY artifacts. They are preserved via off-machine backup (iCloud Drive per session decision). **DO NOT extend them.** New decisions go through `bd decision` only. Opportunistic backfill: when a historical decision surfaces in work, promote it to `bd decision` at that time (don't bulk-migrate).
