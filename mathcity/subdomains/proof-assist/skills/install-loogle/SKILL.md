---
name: install-loogle
description: Install and configure a Loogle / Mathlib4 search MCP server so Lean 4 lemma lookup works through a connected MCP tool instead of only the raw web API. The canonical server is mathlas (`claude mcp add mathlas -- uvx mathlas-mcp`), which proxies Loogle + LeanSearch with a cache; verifies with `claude mcp list` and falls back to the direct Loogle JSON API (see search-mathlib) if the MCP will not connect. Use when the user says "install loogle", "set up mathlib mcp", "add loogle mcp", "install-loogle", "configure loogle search", or when search-mathlib reports no Loogle/mathlas MCP is connected and the user wants one. Companion to search-mathlib (which USES the server this skill installs).
---

# install-loogle

Installs an MCP server that exposes **Loogle** (the Lean 4 / Mathlib4 search
engine) as a callable tool, mirroring how `stacks` and `scholar` are set up in
this subdomain. Loogle itself is a hosted web service; this skill wires a local
MCP server in front of it so lemma search is a first-class tool call.

## Pre-flight

- `claude` CLI must be on PATH (`command -v claude`). If missing, stop and tell
  the user to install/point at the Claude Code CLI first.
- `uvx` (from `uv`) is needed for the `uvx` install form. Check `command -v uvx`;
  if absent, either install `uv` (https://docs.astral.sh/uv/) or use a clone +
  `pip install -e .` form of whichever server is chosen.

## Primary path — mathlas (Loogle + LeanSearch)

`mathlas` is the recommended server: it wraps **Loogle** and **LeanSearch**
behind one `search_formal_math` tool with a 7-day cache.

```bash
claude mcp add mathlas -- uvx mathlas-mcp
```

Verify it connected:

```bash
claude mcp list | grep -i mathlas    # want: "mathlas: ✓ Connected"
```

Once connected, `search-mathlib` will call its `search_formal_math` tool
automatically instead of the raw API.

## Fallback — no MCP required

If the MCP will not connect (network, `uvx` missing, package unavailable),
**do not block Mathlib search** — `search-mathlib` already queries the Loogle
JSON API directly and fails soft:

```bash
curl -s "https://loogle.lean-lang.org/json?q=add_comm"
```

Report the MCP failure, then point the user at `search-mathlib` for the
direct-API path. Installation is an enhancement (caching, one tool call), not a
prerequisite for search.

## Alternative servers

If `mathlas` is unsuitable, these also expose Loogle/Mathlib to MCP (cite
whichever you install in the `## Sources` section of any work that uses it):

| Server | What it adds | Install |
|--------|--------------|---------|
| `lean-lsp-mcp` | Full LSP server with Loogle integration | see repo (Sources) |
| `lean-mathlib-docs-mcp` | Local Mathlib docs search | see repo (Sources) |

## Sources / Citations

Cite these wherever this server or its results are used (per repo policy: cite
all sources).

- **Loogle** — the Lean 4 / Mathlib4 search engine, hosted by the **Lean FRO**
  (Lean Focused Research Organization). https://loogle.lean-lang.org
  (JSON API: `https://loogle.lean-lang.org/json?q=<query>`).
- **mathlas MCP** — Loogle + LeanSearch proxy with cache.
  https://github.com/Archerkattri/mathlas
- **lean-lsp-mcp** — LSP-based Lean MCP server with Loogle integration.
  https://github.com/oOo0oOo/lean-lsp-mcp
- **lean-mathlib-docs-mcp** — local Mathlib docs search MCP.
  https://github.com/CriticalLine/lean-mathlib-docs-mcp
- **Mathlib4** — the Lean 4 mathematical library being searched.
  https://github.com/leanprover-community/mathlib4
- **Mathlib4 docs** — rendered declaration documentation.
  https://leanprover-community.github.io/mathlib4_docs/

## See also

- `search-mathlib` — the skill that USES this server (and works without it via
  the direct JSON API).
- `mcp/stacks/README.md`, `mcp/scholar/README.md` — the sibling MCP install
  patterns this skill mirrors.
