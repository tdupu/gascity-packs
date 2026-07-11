---
name: setup-lmfdb-pipeline
description: Meta-setup skill: runs configure-database then configure-server to create both project-root confs the LMFDB skills need. Use this skill whenever the user says "setup lmfdb pipeline", "set up the lmfdb confs", "configure everything for lmfdb", or on a fresh clone before first use of any conf-driven lmfdb skill.
---

# setup-lmfdb-pipeline

Meta-setup: create both project-local, gitignored confs that the mathcity-lmfdb
server and database skills read. Private values (hostnames, users, SSH keys,
schema names) live ONLY in the resulting files — never in pack content, the
conversation transcript, or git history (POLICY.md P1.10).

## Procedure

Run both sub-skills in sequence:

1. **`mathcity-lmfdb.configure-database`** — creates `lmfdb-pipeline.conf` at the
   project root (PGDATABASE, PGSCHEMA, DATA_DIR, SCHEMA_MD).
2. **`mathcity-lmfdb.configure-server`** — creates `lmfdb-server.conf` at the
   project root (REMOTE_HOST, REMOTE_USER, REMOTE_REPO, SSH_JUMP, SSH_KEY,
   MAX_PARALLEL, ALERT_EMAILS).

Each sub-skill handles its own gitignore check and validation step. If either
reports `blocked`, stop and surface the exact failing step to the user before
continuing.

## Output

`ready` (both confs created, gitignored, and validated) or `blocked` with the
sub-skill and step that failed. Never print conf contents.

## See also

- `mathcity-lmfdb.configure-database` — database/pipeline conf only
- `mathcity-lmfdb.configure-server` — SSH/compute-server conf only
- `assets/lmfdb-pipeline.conf.example` — database conf template
- `assets/lmfdb-server.conf.example` — server conf template
- POLICY.md P1.10 (no private values) and P1.12 (this skill's reason to exist)
