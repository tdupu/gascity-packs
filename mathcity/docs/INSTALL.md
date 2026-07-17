# Gas City Packs — Installation & User Guide
## For Mathematicians New to Gas City

> **Audience:** A mathematician who wants to use gascity-packs for research
> — briefs, decision pipelines, and agent-dispatched work — but has not
> used Gas City before. This guide covers the complete path from zero to a
> working city with the mathcity pack installed.
>
> **Deeper references** (for operators who already have a running city):
> - [CITY-OPERATION-REFERENCE.md](./CITY-OPERATION-REFERENCE.md) — architecture and command surface
> - [CITY-RESTART-CHECKLIST.md](./CITY-RESTART-CHECKLIST.md) — step-by-step restart/verify
> - [QUIMBY-ONBOARDING.md](./QUIMBY-ONBOARDING.md) — hard-won operational truths from 11 sessions

---

## Contents

1. [What Is gascity-packs?](#1-what-is-gascity-packs)
2. [Prerequisites](#2-prerequisites)
3. [Install Gas City and Beads](#3-install-gas-city-and-beads)
   - [Option A: Homebrew (macOS, quickest)](#option-a-homebrew-macos-quickest)
   - [Option B: Build from Source (recommended for power users)](#option-b-build-from-source-recommended-for-power-users)
4. [Install Dolt](#4-install-dolt)
5. [Initialize Your City](#5-initialize-your-city)
6. [Import the Packs](#6-import-the-packs)
7. [Dependency Matrix](#7-dependency-matrix)
8. [The Brief System](#8-the-brief-system)
9. [Mayor Skills and the Dispatch Model](#9-mayor-skills-and-the-dispatch-model)
10. [First Steps: A Worked Example](#10-first-steps-a-worked-example)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What Is gascity-packs?

**Gas City** (`gc`) is a multi-agent orchestration framework: a local process
that spawns AI coding agents, routes work between them through formulas and
orders, and keeps a persistent issue-tracker (beads) to record decisions.

**gascity-packs** is a collection of opt-in configuration bundles called
*packs*. Each pack adds formulas, skills, orders, and agents to your city
without you writing any of that by hand. Packs compose: a city with the
`gascity` base pack and the `mathcity` pack gets both the build-basic
workflow and the mathematical brief pipeline.

### Key concepts

| Term | What it is |
|------|-----------|
| **City** | Your local orchestration instance; lives in one directory (e.g. `~/my-city`) configured by `city.toml`. |
| **Rig** | A git repository adopted into the city via `gc rig add`. Agents work on rigs. |
| **Bead** | An issue/task in the beads tracker (`bd`). Work is dispatched, tracked, and closed as beads. |
| **Formula** | A multi-step workflow template (e.g. `build-basic`, `brief-prep`). A formula slings a bead through a sequence of agent steps. |
| **Order** | A recurring automated task: fires on a schedule, an event, or a condition. Orders run the brief pipeline automatically. |
| **Pack** | A bundle of formulas, orders, skills, and agents you import into your city via `city.toml`. |
| **Skill** | A SKILL.md instruction file that tells an agent how to do one well-defined task. Skills live in `~/.claude/skills/`. |
| **Brief** | A formatted decision document (a `.md` file) produced by the brief pipeline. Briefs describe a code artifact, the work done, and the decision needed. |
| **Stack** | The queued list of briefs ready for your review (`~/.gc/<rig>/briefs/stack/`). |

### Inside vs. outside agents

Gas City runs two kinds of agents:
- **Inside (GC) agents** — spawned by the city itself to do work (implement, review, build). They claim beads, execute formula steps, and close beads.
- **Outside agents** — your Claude Code session. You interact with the Mayor skill, read briefs, and adjudicate decisions. You do NOT claim GC-managed beads.

As a mathematician using this system, you are always the **outside agent**: you drive the Mayor, read the brief stack, and provide verdicts. Inside agents do the mechanical work.

---

## 2. Prerequisites

### Required everywhere

| Tool | Purpose | Minimum version |
|------|---------|----------------|
| `git` | Source control for all repos | 2.40+ |
| `tmux` | Session manager for the agent fleet | 3.3+ |

### Required for brew install

| Tool | Purpose |
|------|---------|
| [Homebrew](https://brew.sh) | Package manager (macOS) |

### Required for source build

| Tool | Purpose | Minimum version |
|------|---------|----------------|
| Go toolchain | Build `gc` and `bd` binaries | Go 1.22+ |
| `make` | Drives the build | any |

### Optional (capability-dependent)

| Tool | Unlocks | Notes |
|------|---------|-------|
| [Dolt](https://github.com/dolthub/dolt) | Beads issue tracker, brief pipeline | Required for `bd` and mathcity |
| [Magma](http://magma.maths.usyd.edu.au) | Math computation rigs | Licensed; install separately |
| [SageMath](https://www.sagemath.org) | Python-based math computation | Optional alternative to Magma |
| Chrome + Claude-in-Chrome extension | Browser-automation skills | For skills that interact with the web |
| Claude Code CLI | Outside-agent session | Required to run skills, drive the Mayor |

### Platform notes

**macOS (Apple Silicon / Intel):** fully supported. All commands in this guide are macOS-centric. The brew path is the fastest route.

**Linux:** Gas City builds and runs on Linux. Use the source-build path (Section 3B). Homebrew formula availability may vary; install Go from https://go.dev/dl/ if needed. Dolt is available via the official installer.

**Windows:** not currently supported in this guide. WSL2 with a Linux distribution is reported to work; treat it as a Linux install.

---

## 3. Install Gas City and Beads

### Option A: Homebrew (macOS, quickest)

```sh
brew install gascity
gc version          # should print a version string

brew install beads
bd version          # should print a version string
```

Verify both are on your `PATH`:
```sh
which gc
which bd
```

> **Caveat:** Homebrew versions may lag behind the source. If you need features
> from a specific commit, use the source-build path instead.

### Option B: Build from Source (recommended for power users)

This is the approach used in Taylor's setup. It gives you full control over
which commit you run and lets you upgrade to HEAD at any time.

**Step 1: Clone and build `gc`**

```sh
git clone https://github.com/gastownhall/gascity.git ~/repos/gascity
cd ~/repos/gascity
make install
gc version          # should print "dev" or a commit-based version
```

The `make install` step installs the `gc` binary into `$GOPATH/bin` (usually `~/go/bin`). Ensure that directory is on your `PATH`:

```sh
echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.zshrc   # or ~/.bashrc
source ~/.zshrc
```

**Step 2: Clone and build `bd`**

```sh
git clone https://github.com/gastownhall/beads.git ~/repos/beads
cd ~/repos/beads
make install
bd version
```

**Step 3: Clone gascity-packs (for local-path imports)**

```sh
git clone https://github.com/gastownhall/gascity-packs.git ~/repos/gascity-packs
```

> **Why a local clone?** The source-build workflow uses `source = "/path/to/..."` in
> `city.toml` instead of git-URL imports. This means pack edits go live without
> re-pinning. It also lets you contribute changes back to upstream via pull requests.

**Keeping your tools up to date**

```sh
cd ~/repos/gascity && git pull && make install
cd ~/repos/beads   && git pull && make install
cd ~/repos/gascity-packs && git pull
```

> **Tip:** create three shell aliases or a simple update script so you don't forget any step.

---

## 4. Install Dolt

[Dolt](https://github.com/dolthub/dolt) is a version-controlled SQL database
that powers the beads issue tracker. Without Dolt, `bd` commands will fail and
the brief pipeline will not function.

**macOS (recommended)**

```sh
brew install dolt
dolt version
```

**Linux / source**

```sh
curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh | bash
dolt version
```

Verify Dolt is on your `PATH`:
```sh
which dolt
dolt version    # should print a version string
```

---

## 5. Initialize Your City

A "city" is a directory that Gas City manages. It contains:
- `city.toml` — your configuration (packs, rigs, pool sizes, overrides)
- `.gc/` — runtime state (briefs, logs, agent output)
- `.beads/` — Dolt database export (passive; the live store is in Dolt)

**Create and start a city**

```sh
# Pick a directory for your city (NOT inside the gascity source repo)
gc init ~/my-city
cd ~/my-city
gc start
gc status           # confirm Controller: running
```

**Initialize beads inside your city**

```sh
cd ~/my-city
bd init
bd version          # confirm connectivity
```

**Verify health**

```sh
gc doctor           # all checks should PASS
gc dolt health      # should report healthy
```

> **Note:** `gc config check` does NOT exist in the current build. Use `gc config show`
> to validate your `city.toml` resolves without errors.

---

## 6. Import the Packs

### 6.1 Base pack: `gascity`

The `gascity` pack provides the core build workflow (`build-basic`) and the
`gc.mayor` coordinator skill. Import it first.

**Via URL (any install)**

```sh
cd ~/my-city
gc import add --name gc https://github.com/gastownhall/gascity-packs.git//gascity
gc import add --name gc-base https://github.com/gastownhall/gascity-packs.git//gascity
gc import install
```

> **Note:** `gascity/roles` provides agent roles; the full `gascity` pack provides
> formulas. Import the full pack as `gc-base` so both are available.

**Via local path (source-build workflow)**

In `city.toml`:

```toml
[defaults.rig.imports.gc]
source = "/Users/you/repos/gascity-packs/gascity/roles"

[defaults.rig.imports.gc-base]
source = "/Users/you/repos/gascity-packs/gascity"
```

Then run `gc import check` to confirm the paths resolve.

### 6.2 Math brief pipeline: `mathcity`

The `mathcity` pack adds the brief pipeline — the orders and formulas that
move work from completion through briefs to your adjudication.

**Via URL**

```sh
gc import add --name mathcity https://github.com/gastownhall/gascity-packs.git//mathcity
gc import install
```

**Via local path**

```toml
[defaults.rig.imports.mathcity]
source = "/Users/you/repos/gascity-packs/mathcity"
```

### 6.3 PR pipeline (optional)

The `pr-pipeline` pack adds `mol-pr-*` formulas for triage, blast-radius
analysis, and pre-push review of GitHub pull requests.

```toml
[defaults.rig.imports.pr-pipeline]
source = "/Users/you/repos/gascity-packs/pr-pipeline"
```

### 6.4 Verify imports

```sh
gc import check       # all paths should report OK
gc import status      # lists active imports: gc, gc-base, mathcity, pr-pipeline
gc formula list       # should show build-basic, brief-prep, mol-pr-* etc.
gc order list         # should show brief-shuffle-pile, brief-review-patrol, etc.
```

### 6.5 Add a rig (your research repository)

```sh
git clone https://github.com/you/my-math-project.git ~/repos/my-math-project
cd ~/repos/my-math-project
gc rig add .

# Confirm it appears
gc rig list
```

---

## 7. Dependency Matrix

Which capabilities need which tools:

| Capability | `gc` | `bd` | Dolt | tmux | Magma/Sage | Chrome MCP | Claude Code |
|------------|:---:|:---:|:----:|:----:|:----------:|:----------:|:-----------:|
| City start/stop | ✓ | | | ✓ | | | |
| Bead tracking (`bd create`, `bd list`) | | ✓ | ✓ | | | | |
| Dispatch work (`gc sling`) | ✓ | ✓ | ✓ | ✓ | | | |
| Brief pipeline (brief-prep, brief-shuffle) | ✓ | ✓ | ✓ | ✓ | | | |
| Mayor skill / outside agent | ✓ | ✓ | ✓ | | | | ✓ |
| Math rigs (Magma compute) | ✓ | ✓ | ✓ | ✓ | ✓ | | |
| Browser-automation skills | | | | | | ✓ | ✓ |
| LMFDB queries | | | | | | | ✓ |

**Minimum setup to run the brief pipeline:**  `gc` + `bd` + Dolt + tmux.

**Minimum setup to use the Mayor and review briefs:** add Claude Code CLI.

**Minimum setup to run math computation:** add Magma or SageMath.

---

## 8. The Brief System

The brief system is the decision pipeline that moves work from completion to
your adjudication. As a mathematician, you interact with it through the brief
stack — a queue of formatted documents waiting for your verdict.

### 8.1 What is a brief?

A brief is a `.md` file that contains:
- **Decision at top** — what exactly needs your verdict
- **Origin** — what bead, branch, or PR this is about
- **Math/code context** — what the work does and why
- **Gate evidence** — test results, review output, gate verdicts
- **Timeline** — when the work happened
- **Recommended action** — the agent's suggested verdict

Briefs are produced by the `brief-prep` formula (which runs `grill-and-present`,
`coordinate-review`, and the gate runner in sequence). They are NOT informal
summaries — every brief must clear all pipeline gates before reaching your stack.

### 8.2 The pipeline lifecycle

```
work (bead closed with needs-decision)
  → brief-prep formula
    → grill-and-present (structures the brief)
    → gate runner (runs check-* gate skills)
    → coordinate-review (adversarial review)
  → .pile/ (holding area)
    → brief-shuffle-pile order (promotes or rejects)
  → stack/ (ready for review)
    → catch-no-brainer (classifies: no-brainer vs. needs-Taylor)
  → present-briefs / present-it (you read it)
    → verdict (approve / reject / revise / defer)
  → brief-record-decision
    → gc.publisher (if approve+branch → lands the code)
```

### 8.3 Brief pile and stack locations

| Path | Contents |
|------|----------|
| `~/.gc/<rig>/briefs/.pile/` | Briefs in transit (not yet stack-eligible) |
| `~/.gc/<rig>/briefs/.pile/.rejected/` | Briefs that failed a gate |
| `~/.gc/<rig>/briefs/.pile/.no-brainer/` | Auto-classified safe briefs |
| `~/.gc/<rig>/briefs/stack/` | Briefs ready for your review |

### 8.4 Reading briefs

```sh
# See how many briefs are waiting
bd list --label brief --status open

# Present the next brief for your decision (in Claude Code)
# /present-briefs        ← batch mode (recommended for backlog)
# /present-it <bead-id>  ← single brief
```

The `present-briefs` skill manages a hot queue: it pre-presents the next 2
briefs while you decide the current one, so you never wait between decisions.

### 8.5 Giving a verdict

After `present-it` shows you a brief, your verdict options are:

| Verdict | Meaning | What happens next |
|---------|---------|------------------|
| **Approve** | Ship it | Publisher dispatched; branch lands (if any) |
| **Reject** | Don't ship | Brief archived; optional follow-up filed |
| **Revise** | Changes needed | Re-draft follow-up created; brief parked |
| **Defer** | Decide later | Brief parked; nothing dispatched |

---

## 9. Mayor Skills and the Dispatch Model

The Mayor is the coordinator skill (`gc.mayor` + `mathcity.mayor-math`) that
plans work, creates beads, and slings them to the right agents. You interact
with the Mayor through your Claude Code session.

### 9.1 Sling work to agents

```sh
# Create a bead describing the goal
bd create "Compute the BSD invariants for this family of curves"

# Sling it through build-basic-briefed (the standard path)
# This runs the full build and files a brief instead of auto-publishing
gc sling <rig>/gc.run-operator <bead-id> \
  --on build-basic-briefed \
  --var interaction_mode=autonomous \
  --var review_mode=agent \
  --var drain_policy=separate \
  --var push=false \
  --var open_pr=false
```

`build-basic-briefed` runs: requirements → plan → plan review → decomposition
→ parallel implementation → three-lane review → decision brief at the terminal slot.

### 9.2 Check agent status

```sh
gc status                          # city health + pool counts
gc session list                    # all active agent sessions
tmux -L gt ls                      # list tmux sessions directly (more reliable)
gc order history                   # recent order dispatches
```

> **Common gotcha:** `gc status` "0/N agents" is a **slow-API artifact**. The
> /status endpoint is slow when cold. Verify fleet health via `tmux -L gt ls`
> instead.

### 9.3 The dispatch model

Work flows through pools, not individual agents:

- `mathcity.brief-operator` pool — processes brief pipeline steps (shuffle, patrol, classify)
- `gc.run-operator` pool — general-purpose worker agents

Beads are dispatched to a pool via `gc sling`; the next idle agent in that
pool claims the bead and works on it. You never directly address an agent by
name in normal operation.

### 9.4 Communicating with agents

```sh
# Send a mail to an agent (persists across sessions)
gc mail send mayor "Please triage the new branch for hecke operator work"

# Nudge an agent (ephemeral — best for wake-up calls)
gc nudge <session-name> "Please continue your current task"
```

Prefer `gc mail` for handoffs and escalations. Prefer `gc nudge` for quick
wakeup calls (e.g. after a usage-limit reset). See
[CITY-OPERATION-REFERENCE.md](./CITY-OPERATION-REFERENCE.md) for the full
mail-vs-nudge doctrine.

---

## 10. First Steps: A Worked Example

This example creates a rig, files a bead, slings work, and reviews the brief.
It is self-contained and should take about 15–20 minutes end-to-end (most of
that is agent execution time).

### Step 1: Confirm city is running

```sh
gc status
gc dolt health
gc doctor
```

All checks should pass. If the city is not running: `gc start`.

### Step 2: Create a rig for your project

```sh
# If your project repo already exists locally:
cd ~/repos/my-project
gc rig add .

# If starting from scratch:
mkdir ~/repos/hello-math && cd ~/repos/hello-math
git init && git commit --allow-empty -m "init"
gc rig add .
```

Verify:
```sh
gc rig list         # your rig should appear
```

### Step 3: File a bead

```sh
cd ~/repos/hello-math
bd create "Add a proof sketch for the main lemma in main.tex"
```

Note the bead ID printed (e.g. `hm-abc1`).

### Step 4: Sling the bead

From your city directory:

```sh
cd ~/my-city
gc sling hello-math/gc.run-operator hm-abc1 \
  --on build-basic-briefed \
  --var interaction_mode=autonomous \
  --var review_mode=agent \
  --var drain_policy=separate \
  --var push=false \
  --var open_pr=false
```

### Step 5: Watch the fleet

```sh
tmux -L gt ls                      # see your agent sessions
gc session list --template mathcity.brief-operator
```

The agent will work through the formula steps. Depending on the task and model
speed, this may take a few minutes to several minutes.

### Step 6: Review the brief

Once the formula completes, a brief lands in the stack. In your Claude Code
session:

```
/present-briefs
```

The brief will show you the work done, the gate results, and a recommended
verdict. Choose approve, reject, revise, or defer.

### Step 7: Close the loop

If you approved and the bead had a branch, `gc.publisher` dispatches to land
it. If you rejected, the brief is archived and an optional follow-up bead is
filed for you to triage later.

---

## 11. Troubleshooting

### Dolt is down / beads commands hang

```sh
gc dolt health --json        # get a health snapshot
gc dolt logs                 # check server logs
gc dolt status               # is the server running?
gc dolt start                # start it if stopped
```

If Dolt won't start or is corrupted:
- **Never** use `rm -rf` on `~/.dolt-data/` directories.
- **Never** remove or modify files inside `.dolt/` directories (including `noms/LOCK`).
- Check `gc dolt logs` for the specific error, then search the beads for a known fix.

If Dolt is truly unreachable, escalate:
```sh
gc mail send mayor "Dolt: server unreachable" --subject "[ESCALATE CRITICAL]"
```

### City won't boot / `gc start` fails

```sh
gc config show      # validate city.toml resolves without error
gc import check     # all local-path imports must resolve
```

Common causes:
- A pack source path is wrong or the repo wasn't cloned
- `city.toml` has a TOML syntax error
- A previous city is still running (check `tmux -L gt ls`; kill stale sessions with `tmux -L gt kill-server`)

### Fleet shows "0 agents"

This is usually a slow-API artifact. Verify with:

```sh
tmux -L gt ls                   # lists actual tmux sessions
gc order history | head -20     # confirms orders are firing
```

If agents are truly not spawning:

```sh
gc supervisor start             # if the supervisor is not running
gc session list                 # see all session states
gc session logs <session-name>  # read one session's log
```

### `gc status` slow / commands time out

Dolt latency under load causes query timeouts. Symptoms:
- `bd list` returns slowly or hangs
- Brief patrol orders time out and flood the pool

Mitigation (add to `city.toml`):
```toml
[[orders.overrides]]
name = "dolt-health"
interval = "5m"

[[orders.overrides]]
name = "gate-sweep"
interval = "10m"
```

These raise the cooldown intervals so normal tick jitter does not trip the
doctor thresholds.

### Briefs stuck in `.pile/` and not reaching the stack

```sh
gc order list | grep brief          # confirm orders are present
gc order show brief-shuffle-pile    # inspect trigger and pool
gc session list --template mathcity.brief-operator  # pool must have active sessions
```

If the `mathcity.brief-operator` pool has no active sessions, the shuffle order
cannot run. Check `gc status` and `gc supervisor start`.

### `build-basic-briefed` not found

```sh
gc formula list | grep brief        # should show brief-prep, math-brief-prep, etc.
```

If missing: the `mathcity` pack import is not resolved. Check `gc import status`
and confirm the `source` path in `city.toml` points to a valid directory.

### `gc.publisher` does not merge to main automatically

This is intentional. `gc.publisher` does NOT auto-merge to main in the current
build. The publish step requires an explicit Taylor `authorize-git-operation`
approval. Briefs accumulate on the stack; no code ships without your verdict.

### Common command surface errors (commands that do NOT exist)

The following commands appear in old notes but do **not** exist in the current binary:
- `gc config check` — use `gc config show` instead
- `gc convoy show` — use `bd show <id>` instead
- `gc dolt sql --db` — use `gc dolt sql -q "..."` instead
- `gc event log` — use `gc order history` instead
- Shell `timeout` — not available on macOS; use the Bash tool's built-in timeout parameter

---

## What's Next

- **Operator reference:** [CITY-OPERATION-REFERENCE.md](./CITY-OPERATION-REFERENCE.md) — full system architecture, pool mechanics, and command surface
- **Restart checklist:** [CITY-RESTART-CHECKLIST.md](./CITY-RESTART-CHECKLIST.md) — step-by-step phases from cold city to verified brief pipeline
- **QUIMBY onboarding:** [QUIMBY-ONBOARDING.md](./QUIMBY-ONBOARDING.md) — hard-won operational truths from 11 Mayor sessions
- **Dogfood workflow:** [DOGFOOD-WORKFLOW.md](./DOGFOOD-WORKFLOW.md) — the `~/gt` ↔ `~/repos` duality and how pack changes go live
