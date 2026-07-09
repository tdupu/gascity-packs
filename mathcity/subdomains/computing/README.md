# mathcity-computing

Dispatch and track heavy computations (Magma/Sage/PARI runs, UPF rig jobs).

This sub-namespace (`mathcity.computing.*`) wraps `upf-experiment-dispatch`
and `test-execution-request`. Computation results are collected as
`brief_type = experiment` briefs and fed back into the brief pipeline via
`math-brief-prep`.
