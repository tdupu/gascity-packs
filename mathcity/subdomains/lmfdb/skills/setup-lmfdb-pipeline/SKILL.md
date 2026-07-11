---
name: setup-lmfdb-pipeline
description: Set up the project-local configuration that the mathcity-lmfdb server and database skills read (push-to-server, pull-data-from-server, push-data-to-server, the database side of the conversion lattice). Copies the pack's lmfdb-pipeline.conf.example into the project, walks Taylor through filling in each value interactively, gitignores the copy, and verifies the setup — the P1.12 companion setup skill for this pack's conf. Trigger phrases: "setup lmfdb pipeline", "set up the data-generation conf", "configure the compute server connection", "the server skills can't find their conf", or on a fresh clone before first use of any conf-driven lmfdb skill.
---

# setup-lmfdb-pipeline

Create the project-local, gitignored conf that this pack's server- and
database-touching skills read. Private values (hostnames, users, SSH keys,
schema names) live ONLY in the resulting file — never in pack content, the
conversation transcript summary, or git history (POLICY.md P1.10).

## Procedure

1. **Locate the target.** Default conf path is the hecke convention,
   `magma/scripts/data-generation.conf`, relative to the project root. If
   the project already has a conf there, stop and report — this is setup,
   not overwrite (offer a diff against the `.example` keys instead: new
   keys the example gained that the existing conf lacks).
2. **Copy the example.**
   ```bash
   cp ~/repos/gascity-packs/mathcity/subdomains/lmfdb/assets/lmfdb-pipeline.conf.example \
      <project>/magma/scripts/data-generation.conf
   ```
3. **Fill in values interactively.** Ask Taylor for each, one at a time
   (AskUserQuestion where available): `REMOTE_HOST`, `REMOTE_USER`,
   `REMOTE_REPO`, `SSH_JUMP` (optional), `SSH_KEY`, `MAX_PARALLEL`,
   `ALERT_EMAILS`, `PGDATABASE`, `PGSCHEMA`, `DATA_DIR`. Never echo values
   back into output beyond confirming they were set; never run a command
   whose argv contains a secret.
4. **Gitignore the copy.** Verify the conf path is matched by the
   project's `.gitignore`; add the entry if missing. Then prove it:
   ```bash
   git -C <project> check-ignore magma/scripts/data-generation.conf && echo ignored
   ```
   If this fails, STOP — do not proceed with a trackable conf.
5. **Verify.**
   - `bash -n` the conf (it's sourced shell — must parse).
   - Connection smoke test only with Taylor's go-ahead:
     `ssh -o BatchMode=yes $REMOTE_USER@$REMOTE_HOST true` (via the conf,
     not by echoing values).
   - Report which conf-driven skills are now usable.

## Output

`ready` (conf created, ignored, parsed, optionally connection-tested) or
`blocked` with the exact failing step. Never print the conf contents.

## See also

- [`assets/lmfdb-pipeline.conf.example`](../../assets/lmfdb-pipeline.conf.example) — the shipped template
- POLICY.md P1.10 (no private values in pack content) and P1.12 (this
  skill's reason to exist)
