---
name: repo-to-city
description: Reference skill mapping repository names to their city rig (~/gt/<name>) and working copy (~/repos/<name>). Use when you need to know where a repo lives in the city, its beads prefix, or whether it is registered as a gc rig. Trigger phrases: "which rig", "where is the rig for", "is X a rig", "what prefix does X use", "repo to city mapping", "add a new rig".
---

# repo-to-city

Every repository tracked by Gas City has **two checkouts** and a **beads database** in each:

| Location | Purpose |
|---|---|
| `~/gt/<repo-name>` | City-managed rig — gc agents (mayor, polecats, refinery) work here |
| `~/repos/<repo-name>` | Outside-agent working copy — clerk and Taylor's direct commands |

Both checkouts share the same git remote (`git@github.com:tdupu/<repo-name>.git`) and
the same Dolt remote (`git+ssh://git@github.com/./tdupu/<repo-name>-dolt.git`).
Bead changes sync via `bd dolt push/pull`.

## Check if a rig is registered

```bash
( cd ~/gt && gc rig list )
```

Or inspect `~/gt/rigs.json` directly.

## Known repo ↔ rig mappings

| Rig name | GitHub repo | Beads prefix | Status |
|---|---|---|---|
| agent_skills | tdupu/agent-skills | as | active |
| cliff-part2 | tdupu/cliff-part2 | cp2 | active |
| differential_valuations | tdupu/differential-valuations | dv | active |
| gascity | tdupu/gascity (fork of gastownhall) | gs | active |
| gascity-packs | tdupu/gascity-packs (fork of gastownhall) | gsp | active |
| hecke | tdupu/hecke | he | active |
| homog | tdupu/homog | ho | active |
| jacobi | tdupu/jacobi | ja | active |
| lmfdb | tdupu/lmfdb | lm | active |
| magma_clifford_algebras | tdupu/magma-clifford-algebras | mca | active |
| magma_diff_alg | tdupu/magma-diff-alg | mda | active |
| tdupu_github_io | tdupu/tdupu.github.io | tgi | active |
| diff_alg_public | tdupu/diff-alg-public | da_pub | suspended |
| diff_alg_problems | tdupu/diff-alg-problems | da_prob | suspended |
| dupuy_cv | tdupu/dupuy-cv | dc | suspended |

## Adding a new rig

See `/dolt-init` for the Dolt setup. The full sequence for a brand-new rig:

```bash
REPO=<repo-name>
PREFIX=<2-4 letter prefix>

# 1. Clone into the city (if not already present)
git clone git@github.com:tdupu/${REPO}.git ~/gt/${REPO}

# 2. Register with gc (creates city.toml entry + installs hooks)
cd ~/gt && gc rig add ~/gt/${REPO} --name ${REPO} --prefix ${PREFIX}

# 3. Init beads + dolt remote in BOTH checkouts (see /dolt-init)
```

Update this table whenever a new rig is added.
