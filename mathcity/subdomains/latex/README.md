# mathcity-latex

Notes-tier `.tex` screening and literature search.

This sub-namespace (`mathcity.latex.*`) covers two coupled concerns:
- **check-latex / latex-hurdle**: the five-hurdle formula (compiles, labels-refs,
  citations, style, Taylor approval) that screens covered `.tex` diffs before push.
- **lit-search**: arXiv/MathSciNet/citation discovery feeding the citation-hygiene
  hurdle H3.

The `merge-latex-sections` skill (under `skills/merge-latex-sections/`) is a
placeholder for the F2 implementation deferred until F1 is complete (see gsp-fby HOLD).
