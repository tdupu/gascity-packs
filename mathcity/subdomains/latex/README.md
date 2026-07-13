# mathcity-latex

Notes-tier `.tex` screening and literature search.

Import alias convention (ADR 0002): skills materialize as
`mathcity-latex.<skill>`.

## Skills

| Skill | Purpose |
| --- | --- |
| `check-latex` | The runnable latex-gate (G6/F1b) evidence engine: compile check, semantic diff summary, approve/reject evidence block (`check-latex-report.{json,md}`) |
| `check-labels-and-refs` | Scan LaTeX files for label/reference consistency, orphan labels/refs, and non-pinpoint cross-references (hurdle H2); composed by `check-latex` |
| `merge-latex-sections` | PLACEHOLDER — merge/reorder sections preserving label/ref integrity; F2 implementation deferred until F1 completes (gsp-fby HOLD) |
| `new-latex-policy` | Propose and apply an amendment to the LaTeX Subdomain Policy (LX-rules) — sole write path for LX-rule changes; every proposal is approved by Taylor in conversation and recorded in the policy Change Log; companion to `check-latex-hygiene` |

## Concerns

- **check-latex / latex-hurdle**: the five-hurdle formula (compiles,
  labels-refs, citations, style, Taylor approval) that screens covered
  `.tex` diffs before push. The parent-pack gate
  `mathcity/gates/latex-gate.toml` invokes
  `subdomains/latex/skills/check-latex/check-latex.sh`.
- **lit-search**: arXiv/MathSciNet/citation discovery feeding the
  citation-hygiene hurdle H3.
