---
name: push-data-to-server
description: rsync canonical local magma/DATA/ working folders to the remote compute server, skipping all snapshot directories (data-*/). Reads connection details from magma/scripts/data-generation.conf. Use whenever the user says "push data to server", "send local DATA to the server", "upload computed data", "sync data to remote", or any time locally-computed flat files need to be available on the remote server.
---

# push-data-to-server

**Purpose:** rsync only the canonical working data folders from local `magma/DATA/` to the remote server. Any subdirectory whose name starts with `data-` is a snapshot and must never be sent.

## Step 0 — Load config

```bash
source magma/scripts/data-generation.conf
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=15"
[[ -n "${SSH_JUMP:-}" ]] && SSH_OPTS="$SSH_OPTS -o ProxyJump=$SSH_JUMP"
[[ -n "${SSH_KEY:-}"  ]] && SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
```

If `data-generation.conf` does not exist, tell the user to copy `data-generation.conf.example` and fill in values.

## What gets copied vs. skipped

| Folder | Action |
|--------|--------|
| `orders/`, `sl2/`, `gamma0/`, `subgroups/`, etc. | Copied |
| Anything named `data-*/` | Skipped (snapshots) |
| Folders on remote that don't exist locally | Left untouched |

## Step 1 — Preview (dry run)

```bash
rsync -avzn \
  --exclude='data-*/' \
  -e "ssh $SSH_OPTS" \
  magma/DATA/ \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_REPO/magma/DATA/"
```

Show the output to the user. Confirm no `data-*` directories appear before proceeding.

## Step 2 — Push

After the user confirms (or if the dry run is clean):

```bash
rsync -avz \
  --exclude='data-*/' \
  -e "ssh $SSH_OPTS" \
  magma/DATA/ \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_REPO/magma/DATA/"
```

## Step 3 — Verify on the server

```bash
ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "
  echo '=== DATA on server ==='
  ls -lh $REMOTE_REPO/magma/DATA/
"
```

## Step 4 — Report

Tell the user:
- Which folders/files were transferred
- Total bytes sent
- Confirmation that no `data-*` snapshot directories were included
