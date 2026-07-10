This is the `build-from-decompose-base` decompose handoff step.

Concrete rule: concrete methodology packs extend this base rather than copying the suffix graph.

Validate the prerequisite inputs before any side effects:

- artifact_root: {{artifact_root}}
- context_path: {{context_path}}
- requirements_path: {{requirements_path}}
- plan_path: {{plan_path}}
- plan_review_path: {{plan_review_path}}
- decomposition_path: {{decomposition_path}}
- decomposition_formula: {{decomposition_formula}}
- drain_policy: {{drain_policy}}
- interaction_mode: {{interaction_mode}}
- review_mode: {{review_mode}}

Do not rerun requirements, plan, or plan-review. This continuation is valid
only when the supplied requirements and implementation plan artifacts exist.

**Plan-review handling:**

If `plan_review_path` is non-empty, verify that the plan-review artifact at
that path exists and records approval or an equivalent pass verdict before
proceeding to decomposition.

If `plan_review_path` is empty or blank, no review document was provided.
Proceed without validating a review verdict — this is expected for legacy plans
(e.g. gascity-bead-plan-opus format) that predate the plan-review artifact
schema. Note the absence in the step's closing metadata:

```bash
bd update "$CLAIMED_BEAD_ID" --set-metadata "gc.build.plan_review_path=none"
```

Record `gc.build.continuation_entrypoint=decompose` when this suffix is
launched directly. Close only after the decompose stage can create or reuse the
decomposition artifact and implementation convoy.
