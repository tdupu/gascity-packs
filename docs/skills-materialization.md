# How pack skills reach agents (materialization)

A pack ships skills by **convention**: any directory at
`<pack>/skills/<skill-name>/` containing a `SKILL.md` is a skill. Nothing is
declared in `pack.toml` — the `skills/` tree is discovered automatically.
Working examples in this repo: [`gascity/skills/mayor/`](../gascity/skills/mayor/SKILL.md)
(the 1.3 mayor-as-skill) and the [`superpowers/skills/`](../superpowers/skills/)
catalog.

## The mechanism

The `gc` binary **materializes** every imported pack's skills into each agent
workspace's provider skill sink (`.claude/skills/` for Claude, `.codex/skills/`
for Codex, etc.) as **symlinks** named `<import-key>.<skill-name>`:

```
~/gt/.claude/skills/gc.mayor          -> ~/repos/gascity-packs/gascity/skills/mayor
~/gt/.claude/skills/superpowers.brainstorming
                                      -> ~/repos/gascity-packs/superpowers/skills/brainstorming
~/gt/.claude/skills/core.gc-agents    -> ~/.gc/cache/repos/<sha256>/.../core/skills/gc-agents
```

The prefix is the **import key** from the consuming city's `city.toml` /
`pack.toml` — `[imports.gc] source = ".../gascity-packs/gascity"` surfaces the
mayor as `gc.mayor`, not `gascity.mayor`.

Two source-resolution modes:

- **Local-path imports** (`source = "/path/to/checkout/<pack>"`): symlinks
  point straight into the checkout, so edits to a SKILL.md propagate live —
  no re-pin, no refresh needed for *content* changes.
- **Remote git imports** (`source = "https://...git//<pack>"`, pinned): `gc`
  clones into a content-addressed cache (`~/.gc/cache/repos/<hash>/`) and
  symlinks against that frozen snapshot. Picking up new content requires
  re-pinning the import.

Materialization is **idempotent** and runs on every supervisor tick and as a
PreStart step for sessions whose worktree differs from the scope root. It only
prunes/replaces symlinks that point under a gc-managed root — user-placed
files and directories in the sink are never touched.

## Adding a new skill to a pack

1. Create `<pack>/skills/<skill-name>/SKILL.md` with `name:` and
   `description:` frontmatter (the description drives skill triggering — say
   *when* to use it, with trigger phrases).
2. Refresh the consuming city: `cd <city> && gc pack refresh` (or just wait
   for the next supervisor tick). A new symlink
   `<import-key>.<skill-name>` appears in the city's `.claude/skills/`.
3. New Claude Code sessions in the city see the skill immediately; running
   sessions pick it up on their next skill-list reload.

Note the difference between **new skill dirs** (need a materializer pass —
step 2) and **edits to existing skills** (live immediately under local-path
imports, since the symlink already points at your working tree).
