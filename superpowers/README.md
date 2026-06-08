# Superpowers Pack

This pack implements the Gas City `build-base` workflow contract with vendored
[Superpowers](https://github.com/obra/superpowers) skills.

## What It Provides

- Formula: `superpowers-build`
- Vendored skills: `brainstorming`, `writing-plans`, `executing-plans`,
  `subagent-driven-development`, `requesting-code-review`,
  `receiving-code-review`, `finishing-a-development-branch`,
  `test-driven-development`, `verification-before-completion`, and
  `using-git-worktrees`
- Provenance: `vendor/superpowers/upstream.toml`

## Import It

Import this pack at city scope. It imports the Gas City pack internally as
`gc`, so `build-base` is available transitively:

```toml
[imports.superpowers]
source = "../gascity-packs/superpowers"
```

Then launch `superpowers-build` from the target rig context. Rig role agents
still use the Gas City `gc.*` override surface.
