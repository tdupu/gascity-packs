# Compound Engineering Pack

This pack implements the Gas City `build-base` workflow contract with vendored
[Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin)
skills.

## What It Provides

- Formula: `compound-build`
- Vendored skills: `ce-brainstorm`, `ce-plan`, `ce-work`, `ce-code-review`,
  and `ce-compound`
- Provenance: `vendor/compound-engineering-plugin/upstream.toml`

`ce-compound` is used during the `finalize` stage. The base workflow does not
add a separate compound stage.

## Import It

Import this pack at city scope. It imports the Gas City pack internally as
`gc`, so `build-base` is available transitively:

```toml
[imports.compound-engineering]
source = "../gascity-packs/compound-engineering"
```

Then launch `compound-build` from the target rig context. Rig role agents still
use the Gas City `gc.*` override surface.
