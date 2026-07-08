---
name: dolt-init
description: Initialize the bd (beads) Dolt database and set the dolt remote in BOTH ~/gt/<repo-name> and ~/repos/<repo-name>. The Dolt repo on GitHub MUST be named exactly <repo-name>-dolt — if it is not, HALT and tell the user to rename it before continuing. Trigger phrases: "dolt init", "set up dolt remote", "initialize beads for", "wire up dolt for", "bd dolt remote add", "init bd for".
---

# dolt-init

Sets up the Dolt-backed beads database for a repo in both the city rig
(`~/gt/<repo-name>`) and the working copy (`~/repos/<repo-name>`).

## Naming invariant — HARD GUARD

The Dolt repo on GitHub **MUST** be named exactly `<repo-name>-dolt`.

Before running any step, verify:

```bash
REPO_NAME="<repo-name>"                        # e.g. cliff-part2
EXPECTED_DOLT="tdupu/${REPO_NAME}-dolt"        # e.g. tdupu/cliff-part2-dolt
echo "Expected private Dolt repo: ${EXPECTED_DOLT}"
```

If the user named the repo anything other than `<repo-name>-dolt`, **STOP** and say:

> "The dolt repo must be named `<repo-name>-dolt` (got `<actual-name>`).
> Please rename the GitHub repo to `tdupu/<repo-name>-dolt` (private) and try again."

Do not proceed until the name matches.

## Prerequisites

1. User has created a **private** GitHub repo named `tdupu/<repo-name>-dolt`.
2. `~/gt/<repo-name>` exists and is registered as a gc rig.
3. `~/repos/<repo-name>` exists as the working-copy clone.

## Steps

```bash
REPO="<repo-name>"      # e.g. cliff-part2
PREFIX="<prefix>"       # e.g. cp2
DOLT_URL="git+ssh://git@github.com/./tdupu/${REPO}-dolt.git"
# NOTE: the ./ before tdupu is REQUIRED — the URL is rejected without it.

# Step 1 — Init bd in city rig
cd ~/gt/${REPO}
bd init --prefix ${PREFIX}

# Step 2 — Set dolt remote in city rig
bd dolt remote add origin "${DOLT_URL}"

# Step 3 — Init bd in working copy
cd ~/repos/${REPO}
bd init --prefix ${PREFIX}

# Step 4 — Set dolt remote in working copy
bd dolt remote add origin "${DOLT_URL}"

# Step 5 — Verify both sides
echo "=== city rig ===" && cd ~/gt/${REPO} && bd dolt remote list
echo "=== working copy ===" && cd ~/repos/${REPO} && bd dolt remote list
# Both should show:
#   origin    git+ssh://git@github.com/./tdupu/<repo-name>-dolt.git

# Step 6 — Initial push from city rig
cd ~/gt/${REPO}
bd dolt push origin main
```

## Security

- The dolt repo **MUST** be private. Confirm with `gh repo view tdupu/${REPO}-dolt --json isPrivate`.
- If it is public, **HALT immediately** and alert the user — do not push any bead data.
- Never run `bd dolt push` to a public repo.

## See also

- `/repo-to-city` — full mapping of repo names to city rigs and prefixes
- `bd dolt push/pull` — sync between city rig and working copy
- `bd backup init/sync` — DoltHub backup (separate from the GitHub dolt remote)
