# ADR 0002: mathcity subdomain layout — nested child packs (gascity/roles model)

**Date:** 2026-07-09  
**Status:** Accepted  
**Deciders:** Taylor Dupuy (via grilling session)

## Context

mathcity needs to organize five functional domains (brief-system, computing, proof-assist, latex, lmfdb) without forking the hurdle registry or duplicating review agents. The EXPANDED-STRUCTURE-DRAFT-2026-07-08.md proposed a `mathcity/subdomains/<name>/` directory layout with three-segment run targets (`mathcity.<subdomain>.<agent>`).

A survey of all packs in gascity-packs found:
- No pack uses a `subdomains/` directory layout
- No pack has three-segment run targets — aliases are flat (`<alias>.<agent>`)
- The only working sub-namespace example is `gascity/roles/pack.toml`: a nested child pack inside a parent pack directory, imported independently via its own alias
- The `slack-mini/channel/full` family are mutually exclusive tier variants, not composition
- `compound-engineering` and methodology adapters use flat agent-name prefixing (`ce-brainstorm`)

## Decision

Adopt the **`gascity/roles` nested child pack model**:

- Each subdomain gets its own `pack.toml` at `mathcity/subdomains/<name>/pack.toml`
- Run targets use the import alias: `mathcity-latex.<agent>`, `mathcity-lmfdb.<agent>` etc.
- City/rig imports each subdomain separately: `[imports."mathcity-latex"] source = ".../mathcity/subdomains/latex"`
- Each subdomain dir holds its own `formulas/`, optional `agents/`, `assets/`, `README.md`

**Three-segment targets (`mathcity.latex.*`) are aspirational**, not achievable with today's gc alias resolution. The EXPANDED-STRUCTURE-DRAFT spec is aspirational; implementation uses two-segment targets with hyphenated aliases.

## Directory scaffold

```
mathcity/
  subdomains/
    brief-system/    pack.toml (name = mathcity-brief-system)
    computing/       pack.toml (name = mathcity-computing)
    proof-assist/    pack.toml (name = mathcity-proof-assist)
    latex/           pack.toml (name = mathcity-latex)
    lmfdb/           pack.toml (name = mathcity-lmfdb)
```

## Consequences

- mathcity pioneers this pattern in the repo — no prior art to copy verbatim
- The parent `mathcity/pack.toml` does NOT auto-import its children; cities must import the subdomains they need
- If gc adds native three-segment alias support, rename targets without changing directory layout
- lmfdb remains the strongest candidate to eventually split into a fully independent pack (external MCP dependency, self-contained query surface)
