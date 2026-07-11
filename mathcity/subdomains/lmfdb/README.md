# mathcity-lmfdb

Query the LMFDB and cross-check computed mathematical data.

Import alias convention (ADR 0002): skills materialize as
`mathcity-lmfdb.<skill>`.

## Skills

| Skill | Purpose |
| --- | --- |
| `search-lmfdb` | Query the LMFDB via its MCP server (`mcp__lmfdb__*`): elliptic curves, modular forms, number fields, L-functions; cross-check computed data, verify labels and eigenvalues |

The `mathcity.lmfdb.querier` agent translates math questions into LMFDB
queries and cross-checks computed data against the database.

Note: this subdomain is the strongest candidate to eventually split into its
own pack, given its external MCP dependency and self-contained query surface
(ADR 0002).
