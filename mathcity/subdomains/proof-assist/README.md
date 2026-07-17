# mathcity-proof-assist

Lean/Coq/Isabelle proof checking and arXiv bibliography for mathematics claims.

This sub-namespace (`mathcity-proof-assist.*` (ADR 0002 alias)) is the escalation target for
prose-math correctness that embeddings and reviewers cannot settle. A passing
Lean build is the strongest possible G4 (critical-review) evidence. Formulas:
`proof-check` (mechanical hurdle) + `formalize-claim` (agent → build gate).

## Skills

| Skill | Purpose |
|-------|---------|
| `search-arxiv` | arXiv ID or keyword → title / abstract / authors / BibTeX. Adopted upstream: [`blazickjp/arxiv-mcp-server`](https://github.com/blazickjp/arxiv-mcp-server). |
