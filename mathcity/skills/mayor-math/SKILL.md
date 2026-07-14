---
name: mayor-math
description: Supplement to gc.mayor for the ~/gt city. Decision rules for rig-scoped sling mechanics, worker fleet gaps, brief routing, and build-basic convoy requirements. Invoke alongside gc.mayor before slinging work or routing adjudication.
---

# mayor-math

Supplement to [[gc.mayor]] covering ~/gt-specific rules. The upstream skill is community-shared; this one applies the correct rig-scoped behaviour for our city.

**Full command surface:** `~/gt/plans/gascity-restart-context.md` (Sling, Fan-Out, Orders, Events sections).

---

## Rules (check all before acting)

**1. Always use the rig-scoped coordinator.**
`gc.run-operator` alone does not resolve at HQ. Always: `<rig>/gc.run-operator`.
Rig from bead prefix: `he-` → hecke, `gs-` → gascity, `gsp-` → gascity-packs, `as-` → agent_skills.

**2. build-basic requires a convoy.**
`target_required = true` — you cannot `--formula` build-basic. Create convoy → add bead → sling `--on build-basic`.

**3. HQ (`gt-` prefix) has no worker fleet.**
Only `bd.dog`, `claude`, `core.control-dispatcher` run at HQ. Worker fleet (`gc.requirements-planner`, `gc.design-author`, `gc.task-decomposer`, `gc.implementation-worker`, `gc.implementation-reviewer`) lives at child rigs only. File work that needs workers in `he-`, `gs-`, `gsp-`, or `as-` rigs.

**4. Rig prefix must match the target repo.**
`gs-` → gastownhall/gascity core, `gsp-` → gascity-packs, `as-` → agent-skills, `gt-` → ~/gt config itself, `he-` → hecke math repo. Do not file gascity PRs as `gt-` beads.

**5. Adjudication goes into the brief pile — never inline.**
Any decision, approval, policy lock, or server-touching authorization must route through `create-brief` → `.beads/briefs/.pile/` → brief pipeline → `present-briefs` → `adjudicate-brief`. Deciding inline leaves no auditable record and is a pipeline regression.

**6. gc.publisher is the merge-queue agent ("refinery").**
On brief approval, `brief-decision-dispatch` reassigns the source bead to `<rig>/gc.publisher`. This is the "refinery" in gastown-pack terminology. Do not hand off approved beads manually.

**7. No-brainer auto-execution is not yet live.**
Classification works; compact presentation works. The pile-processor (he-x3se) that fires `guarded-execute` is not yet shipped. No-brainers still require Taylor's compact-path y/n until he-x3se lands.

---

## Policy references

Check the relevant policy before designing new work or changing subdomain behaviour:

| Subdomain | Policy |
|---|---|
| Build hygiene / portability | `mathcity/subdomains/dev/POLICY.md` |
| Brief pipeline + adjudication | `mathcity/subdomains/brief-system/POLICY.md` |
| Computing / server jobs | `mathcity/subdomains/computing/POLICY.md` |
| LaTeX / writeup | `mathcity/subdomains/latex/POLICY.md` |
| LMFDB queries / uploads | `mathcity/subdomains/lmfdb/POLICY.md` |
| Magma scripts / packages | `mathcity/subdomains/magma/POLICY.md` |
| Policy governance (meta) | `mathcity/POLICY-POLICY.md` |
