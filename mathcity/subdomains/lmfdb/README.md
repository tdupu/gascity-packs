# mathcity-lmfdb

Query the LMFDB and cross-check computed mathematical data.

This sub-namespace (`mathcity.lmfdb.*`) uses the `search-lmfdb` skill and
`mcp__lmfdb__*` tools to query elliptic curves, modular forms, number fields,
and L-functions. The `mathcity.lmfdb.querier` agent translates math questions
into LMFDB queries and cross-checks computed data against the database.

Note: this subdomain is the strongest candidate to eventually split into its own
pack, given its external MCP dependency and self-contained query surface.
