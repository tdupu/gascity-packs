---
name: pull-data-from-server
description: Pull computed flat files from the remote server to local disk — rsync into a timestamped snapshot under magma/DATA/snapshots/, then replace canonical local DATA/ working dirs from the most recent snapshot. Reads connection details from magma/scripts/data-generation.conf. Use whenever the user says "pull data from server", "sync server data locally", "import server results", "get the latest computed data from the server", or any time remote computation results need to be brought to local disk.
---

# pull-data-from-server

**Purpose:** Copy remotely-computed flat files to local disk. The pipeline is:

```
remote:$REMOTE_REPO/magma/DATA/  →  local magma/DATA/snapshots/data-server-MM-DD-YY-NN/
                                  →  local magma/DATA/gamma0/
                                  →  local magma/DATA/orders/
                                  →  local magma/DATA/sl2/
                                  →  local magma/DATA/subgroups/
                                  →  local magma/DATA/cbmf_gamma0_eigenforms/
                                  →  local magma/DATA/cbmf_sub_eigenforms/
```

The script `magma/scripts/pull-from-server.sh` handles this entirely. Just run it:

```bash
bash magma/scripts/pull-from-server.sh
```

That script reads `magma/scripts/data-generation.conf` for connection details. If it does not exist, copy `magma/scripts/data-generation.conf.example` and fill in the values.

## What the script does (for reference)

1. Determines a fresh snapshot name `data-server-MM-DD-YY-NN` (incrementing NN if today already has one).
2. rsyncs each canonical DATA/ dir from the remote server into the snapshot.
3. Finds the most-recent snapshot and rsyncs it into the canonical local working dirs (`--delete` so local matches server exactly).
4. Reports which dirs were updated and which were absent from the snapshot.

Re-running is safe and idempotent. Local-only dirs (e.g. quarantine dirs) are never touched.

## Report to the user

- Snapshot path created
- Which canonical dirs were updated and approximate file counts
- Any dirs absent from the snapshot (skipped)
