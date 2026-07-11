# mathcity-computing

Magma/Sage/PARI computation workflow: dispatching and tracking heavy runs
(including UPF rig jobs), and maintaining the Magma packages that produce
them.

Import alias convention (ADR 0002): skills materialize as
`mathcity-computing.<skill>`.

## Skills

| Skill | Purpose |
| --- | --- |
| `profile-magma` | Wrap Magma code in a profiling harness to find bottlenecks (slow intrinsics, memory hogs) |
| `notebook-to-package` | Promote Magma functions from a Jupyter notebook into package intrinsics in the right `package-*.mag` |
| `improve-package-README` | Add/update documentation in a Magma or Sage project's README + README test files, keeping examples and tests in sync (formerly `improve-README`) |
| `update-issue` | Replace a GitHub issue's body with one canonical statement, consolidating prior versions into a single archive comment |

## Maintained packages

These repositories are maintained using the skills in this pack
(`notebook-to-package` for promotion, `improve-package-README` for
docs/README-tests, `update-issue` for issue hygiene, `profile-magma` for
performance work):

- [tdupu/magma-clifford-algebras](https://github.com/tdupu/magma-clifford-algebras)
- [tdupu/magma-diff-alg](https://github.com/tdupu/magma-diff-alg)

Notebook workflows run on the Jupyter Magma kernel:

- [edgarcosta/magma_kernel](https://github.com/edgarcosta/magma_kernel)

## Pipeline integration

Heavy-run dispatch wraps `upf-experiment-dispatch` and
`test-execution-request`. Computation results are collected as
`brief_type = experiment` briefs and fed back into the brief pipeline via
`math-brief-prep`.
