Use the built-in Gas City publish flow.

If publishing is enabled, publish the finalized build-basic result with the existing publish helper. If publishing is disabled, record a no-op publish outcome with the final artifact paths.

For build-basic, a finalized result can be an approved source anchor/worktree.
Do not mark publish failed or downgrade the workflow merely because the launcher
rig root was not mutated. When publishing is disabled, record a `noop` publish
result while preserving the approved build outcome.

Close only after the push, PR creation, or no-op publish result is recorded.
