# mathcity-lmfdb

Query the LMFDB and cross-check computed mathematical data.

**What is the LMFDB?** The [LMFDB](https://www.lmfdb.org/) — the database
of L-functions, Modular Forms, and related objects — is a large
collaborative database of mathematical objects (elliptic curves, number
fields, modular and Bianchi modular forms, L-functions, genus 2 curves,
groups, …) and the connections between them, organized around the
Langlands program. Each object has a stable label and a webpage; the data
is computed, verified, and cross-referenced by the community. This
subdomain's skills query it, cross-check our computed data against it, and
plan contributions of new object types to it.

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
