---
name: push-to-server
description: SSH into the remote compute server and git pull the latest master branch. Reads connection details from magma/scripts/data-generation.conf. Use this skill whenever the user says "push to server", "pull on the server", "sync the server", "deploy the changes", "update the server", or any time changes have been committed locally and need to be applied on the remote server before restarting computations.
---

# push-to-server

Pull the latest `master` branch onto the remote compute server.

## Step 0 — Load config

```bash
source magma/scripts/data-generation.conf
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=15"
[[ -n "${SSH_JUMP:-}" ]] && SSH_OPTS="$SSH_OPTS -o ProxyJump=$SSH_JUMP"
[[ -n "${SSH_KEY:-}"  ]] && SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
```

If `data-generation.conf` does not exist, tell the user to copy `magma/scripts/data-generation.conf.example` to `magma/scripts/data-generation.conf` and fill in their values.

## Step 1 — Pull latest changes

Always use an explicit fetch + checkout + merge, not a bare `git pull`. A bare
`git pull` fails silently if the server's tracking branch points to a deleted
remote branch (e.g. after a feature branch is merged and removed).

```bash
ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "
  cd $REMOTE_REPO
  git fetch origin
  git checkout master
  git merge --ff-only origin/master
  echo '=== Pull complete. Current HEAD ==='
  git log --oneline -3
"
```

If `--ff-only` fails (diverged history), stop and report — do not force.

## Step 2 — Verify

```bash
ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "
  cd $REMOTE_REPO
  git status
  echo '---'
  git log --oneline -1
"
```

## Step 3 — Report

Tell the user:
- Whether the pull succeeded or produced conflicts
- Which files were updated (from the git output)
- The current HEAD commit

If there are merge conflicts, stop and report them — do not attempt to resolve.
