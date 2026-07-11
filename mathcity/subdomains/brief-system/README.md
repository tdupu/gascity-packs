# mathcity-brief-system

The spine of the mathcity decision pipeline: brief formulas, the 16-hurdle
registry, orders, and the review agents that drive the brief → decision workflow.

This sub-namespace (`mathcity-brief-system.*` (ADR 0002 alias)) governs how raw artifacts enter
the pipeline, pass through hurdles, and become closed decisions. The other four
subdomains produce artifacts that feed into this pipeline.

See `mathcity/formulas/` (cross-cutting pipeline formulas) and
`mathcity/assets/brief-pipeline/` (hurdle registry, paths, thresholds).
