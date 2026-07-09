---
name: authorize-git-operation
description: Explicit Taylor-authorization gate for irreversible git operations — push, force-push, merge, PR creation, branch deletion, release tag. Reads the Mayor avatar PNG so the authorization icon appears before the approval prompt. Records the approval as a bd decision bead. Trigger phrases: "authorize git push", "authorize PR", "authorize merge", "need authorization to push", "authorize this git operation", "request git authorization", "get approval to merge", "authorize branch deletion", "authorize release". NEVER skip this gate for operations listed below — always ask, never auto-proceed.
---

# authorize-git-operation

Presents a visual authorization prompt to Taylor for any irreversible git
operation and records the approval as a bd decision bead in the active rig.

## Covered operations (always gate)

| Operation | Examples |
|---|---|
| **push** | `git push`, `gh pr merge`, force-push |
| **merge** | branch merge to main/master, PR merge |
| **PR creation** | `gh pr create` to any upstream |
| **branch/tag delete** | `git branch -D`, `git push --delete` |
| **release tag** | `git tag -a`, `gh release create` |

Excluded: local commits, `git add`, `git stash`, read-only ops (`git log`,
`git diff`, `git fetch`). Those do not require this gate.

## Step 1 — Show the Mayor icon

**Read this file immediately when the skill is invoked:**

```
~/repos/agent-skills/assets/avatars/taylor-mayor-agent.png
```

In Claude Code (desktop / web app), the image renders inline — Taylor sees
the blue "M" badge before the authorization question. In a terminal-only
session it is visible to the model only, but the text prompt below still
makes the role clear.

## Step 2 — Present the authorization request

After showing the icon, output a structured prompt in the following format
(adapt fields to the operation):

```
╔══════════════════════════════════════════════════╗
║  🅼  MAYOR AUTHORIZATION REQUIRED                 ║
╚══════════════════════════════════════════════════╝

Operation : <PUSH | MERGE | PR | DELETE | RELEASE>
Target    : <remote/branch, upstream, repo:tag — be specific>
Rig       : <rig name, e.g. hecke>
Bead      : <bead ID if the operation closes or relates to one; else "—">

What will happen
  <One paragraph. Include: what changes, which ref is affected, reversibility.
   Name the commit SHA or branch tip if known.>

Risk
  <One sentence on worst-case if this goes wrong and how to undo it.>
```

Use `AskUserQuestion` for the approval — do NOT ask in plain text:

```
question: "Authorize this git operation?"
header: "Git auth"
options:
  - label: "Authorize"
    description: "Proceed with the operation as described."
  - label: "Deny"
    description: "Abort — no git action taken."
  - label: "Modify"
    description: "Abort, but I will tell you how to change the operation before re-asking."
```

## Step 3 — Record the decision

Whether approved or denied, create a bd decision bead immediately after
Taylor responds:

```bash
# From inside the relevant repo (~/repos/<rig> or ~/gt/<rig>)
bd create -t decision \
  --title "Taylor <authorized|denied> git <OPERATION>: <target>" \
  --description "Authorization gate invoked via authorize-git-operation skill." \
  --notes "Operation: <type>. Target: <ref>. Verdict: <AUTHORIZED|DENIED>. Reason: <Taylor's stated reason if any>." \
  --priority 3
```

If Taylor selects "Modify": record the denial, capture the modification in
the bead notes, then re-invoke this skill with the updated operation.

## Step 4 — Post-authorization (if approved)

### Current state (Phase 2 not yet done)

Run with the existing fallback identity (`taylor-claude-agent` App):

```bash
# Verify git credentials before the operation
cd ~/repos/<rig>  # or ~/gt/<rig> if working from city
git config --local user.name
git config --local user.email
```

Commits/PRs will show the `taylor-claude-agent[bot]` avatar (no per-role
icon on GitHub yet — that is Phase 2+3).

### When Phase 2 is complete (`~/.config/gt/mayor/key.pem` exists)

Configure git identity for the Mayor role before the operation:

```bash
bash ~/repos/agent-skills/scripts/setup-agent-github-identity.sh --role mayor
```

This sets `user.name = "🅼 taylor-mayor-agent[bot]"` and the matching
noreply email, so commits and PRs show the **blue M avatar** in the GitHub
UI.

Check with:
```bash
bash ~/repos/agent-skills/scripts/setup-agent-github-identity.sh --check
```

### Phase 2 setup (Taylor action — one time per App)

To create the Mayor GitHub App and complete Phase 2:

1. Browse to <https://github.com/settings/apps/new>
2. Name: `taylor-mayor-agent` | Homepage: `https://github.com/tdupu`
3. Permissions: Contents R/W, Issues R/W, Pull requests R/W, Metadata R
4. Webhooks: disabled | Install: only on this account
5. Upload `~/repos/agent-skills/assets/avatars/taylor-mayor-agent.png` as the avatar
6. Generate + download the private key (`.pem`), note the App ID + Installation ID
7. Install on all Gas Town repos
8. Save credentials:
   ```bash
   mkdir -p ~/.config/gt/mayor
   chmod 700 ~/.config/gt/mayor
   # Move the downloaded .pem:
   mv ~/Downloads/taylor-mayor-agent.*.pem ~/.config/gt/mayor/key.pem
   chmod 600 ~/.config/gt/mayor/key.pem
   echo <APP_ID> > ~/.config/gt/mayor/app-id
   echo <INSTALLATION_ID> > ~/.config/gt/mayor/installation-id
   ```

See `~/repos/agent-skills/docs/per-role-github-apps-plan.md` §3 for the full
flow and sequencing (Mayor first, then Refinery → Witness → Deacon → Polecat).

## Security rules

- NEVER skip this gate, even for "obviously safe" pushes.
- NEVER read or print the `.pem` file — use length-check only:
  `wc -c < ~/.config/gt/mayor/key.pem` (must be > 0).
- Taylor's approval in one conversation does NOT carry over to the next.
  Each operation requires a fresh prompt.
- If the AskUserQuestion response is "Deny" or anything ambiguous: abort,
  record the denial bead, and report what was NOT done.

## What this skill does NOT do

- Does not execute the git operation itself — it only gates it.
- Does not configure per-rig Polecat/Refinery/Witness/Deacon identities
  (those use the same pattern; file separate authorizations under the
  relevant role).
- Does not push to `gastownhall/gascity-packs` upstream or open upstream PRs.

## See also

- `~/repos/agent-skills/docs/per-role-github-apps-plan.md` — full Phase 1/2/3 plan
- `~/repos/agent-skills/assets/avatars/taylor-mayor-agent.png` — the Mayor icon source
- `~/repos/agent-skills/scripts/setup-agent-github-identity.sh` — identity configuration script
- `record-decision` skill — for recording adjudications outside the git-op context
