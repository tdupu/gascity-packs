# artifact-root-scoping smoke test

Regression test for gsp-1bmxuz (concurrent `build-basic-briefed` workflows on
the same rig silently overwrite each other's stage artifacts because they
share one unsuffixed `artifact_root`).

Run:

    sh smoke_test.sh

Checks:

1. `push-the-fleet` SKILL.md no longer documents the old bare rig-root
   `artifact_root=<rig-artifact-root>` dispatch form.
2. `push-the-fleet` SKILL.md documents the scoped
   `artifact_root=<rig-root>/.gc-builds/<bead-id>` form.
3. `math-city-work` SKILL.md documents the same scoped form for its
   `build-basic-briefed` branch.
4. A simulated two-bead dispatch on one rig produces two distinct
   `artifact_root` values.
5. Neither simulated scoped value equals the bare rig root.

This is a static text/path-arithmetic check — it does not require a live
city, matching the convention of the other `mathcity/tests/*/smoke_test.sh`
fixtures (e.g. `lost-bead-filter`, `producer-failure-rollup-routing`).
