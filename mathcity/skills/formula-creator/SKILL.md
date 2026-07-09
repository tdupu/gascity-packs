---
name: formula-creator
description: Create a new formula TOML in any gascity-packs pack and validate gc/bd command surface before committing. Use whenever the user says "create a formula", "add a formula to <pack>", "new formula for <workflow>", "formula-creator", or asks to codify a multi-step agent workflow as a reusable gc formula. Handles mathcity/, gascity/, superpowers/, pr-pipeline/, and other packs under ~/repos/gascity-packs/. Counterpart of skill-creator-math (which creates bare SKILL.md skills, not formula TOMLs).
---

# formula-creator

Create a **formula TOML** in a gascity-packs pack and run the command-surface
quality gate before committing to the fork.

## When to use which creator

| Goal | Tool | Destination |
| --- | --- | --- |
| Multi-step gc-native workflow (formula TOML) | **this skill** | `~/repos/gascity-packs/<pack>/formulas/<name>.toml` |
| Agent skill / slash-command | `skill-creator-math` | `~/repos/gascity-packs/mathcity/skills/<name>/` |
| Personal/utility skill | `skill-creator-plus` | `~/repos/agent-skills/skills/<name>/` |

Standing ruling: gascity-packs owns substrate codification; fork
`tdupu/gascity-packs` is canonical (gt-5cye, gt-evr7). NEVER PR to
upstream `gastownhall/gascity-packs` without Taylor's explicit approval.

---

## Creating a formula — step-by-step

### 1. Choose pack and name

- **Pack**: one of `mathcity`, `gascity`, `superpowers`, `pr-pipeline`,
  `compound-engineering`, `bmad`, or `gstack`.
- **Name**: lowercase, hyphenated, pack-namespaced when needed
  (e.g., `brief-foo`, `mol-pr-bar`, `superpowers-baz`).
- **File location**: `~/repos/gascity-packs/<pack>/formulas/<name>.toml`
  — note mathcity uses the bare `.toml` extension; other packs often
  use `.formula.toml`. Match the convention already used in the target pack.

### 2. Write the TOML skeleton

Every formula needs these top-level fields:

```toml
description = """
One-paragraph description of what this formula does.
Include: purpose, input assumptions, and what it does NOT do.
"""
formula = "<name>"          # must match the filename stem
version = 1

[requires]
formula_compiler = ">=2.0.0"   # include when using check blocks or metadata

[catalog]
name = "<name>"
description = "One-line catalog entry (shown in gc bd formula list)."
```

Add `[vars]` for every runtime parameter the formula needs:

```toml
[vars]
[vars.<param_name>]
description = "What this parameter controls."
required = true              # or omit and set default
default = "<value>"          # omit if required = true
pattern = "^[A-Za-z0-9._-]+$"  # optional regex guard
enum = ["a", "b", "c"]      # optional allowlist
```

### 3. Write steps

Each step is a `[[steps]]` block:

```toml
[[steps]]
id = "step-id"              # unique, kebab-case, stable (used by `needs`)
title = "Human-readable title"
needs = ["previous-step-id"]   # omit for the first step; array of ids
metadata = { "gc.run_target" = "{{some_target}}" }   # see pool routing below
description = """
What the agent does in this step.

Include fenced bash blocks for any gc/bd commands the agent should run:

```bash
gc bd formula show <name>
bd update {{bead_id}} --notes "step complete"
```

Use 4-space indented blocks as an alternative:

    gc runtime drain-ack

Exit criteria: what must be true before the step is done.
"""
```

Dependency rules:
- `needs` is an array of step `id` strings — gc will not start a step until
  all `needs` steps are complete.
- Steps with no `needs` are roots and may run in parallel with other roots.
- Avoid cycles (gc rejects them at compile time).

#### Optional: check block

Attach a shell check that must pass for the step to advance:

```toml
[steps.check]
max_attempts = 3

[steps.check.check]
mode = "exec"
path = "/absolute/path/to/check-script.sh"
timeout = "2m"
```

Place check scripts in `<pack>/assets/scripts/checks/`. Paths must be
absolute — gc rejects `../` traversal.

#### Optional: vapor phase

For deterministic shell-only steps where no LLM judgment is needed:

```toml
phase = "vapor"
```

Add this at the formula top level (not per-step). Use vapor only when
every step in the formula is a scripted operation — no judgment calls,
no skill invocations.

### 4. Pool routing

The `gc.run_target` metadata key controls which pool or role runs a step.
Choose based on what the step requires:

| Step character | `gc.run_target` value |
| --- | --- |
| Deterministic bookkeeping, file ops, shell | `"gc.run-operator"` |
| Judgment, review, analysis | `"gc.review-synthesizer"` |
| Brief-cycle presentation | `"{{presenter_target}}"` (var) |
| Pack-specific role | `"superpowers.brainstorming"`, `"gc.implementation-worker"`, etc. |

When the appropriate target varies by deployment, expose it as a `[vars]`
entry with a sensible default, then use `{{var_name}}` in the metadata.

**Mayor vs. gastown.dog**: the mayor routes steps to pools based on
`gc.run_target`. Gastown.dog (the pool demand-scaler) wakes workers when
a pool has queued work. Do not hard-code agent names — target the role,
not the instance.

### 5. Run the surface-test quality gate (mathcity formulas only)

After writing the TOML, run the command-surface test before committing.
This verifies every `gc`/`bd` subcommand referenced in inline
`description` fenced-bash blocks actually exists in the live CLI:

```bash
cd ~/repos/gascity-packs
python -m pytest tests/test_command_surface.py -k "<formula-name>" -v
```

If the formula has no `gc`/`bd` commands in inline descriptions, the test
produces zero parametrised cases and passes vacuously — that is correct
behaviour, not a false pass on a misconfigured run. Confirm with `-v` that
the expected test IDs appear.

**Scope note**: this gate currently covers only `mathcity/formulas/`.
For formulas in other packs, skip this step and note it in the commit
message until the test is generalised (tracked: gsp-8n7).

Fix any reported unknown subcommands before proceeding to commit. Common
mistakes:
- `gc bd set-metadata` does not exist — use `bd update ... --notes`
- `gc events --since-cursor` does not exist — check `gc events --help`
- `gc bd mol sling` does not exist — use `gc mol sling`

### 6. Safety scan and commit

```bash
cd ~/repos/gascity-packs
gitleaks detect --no-git --source <pack>/formulas/<name>.toml
```

Then commit to the fork only:

```bash
git add <pack>/formulas/<name>.toml
git commit -m "add <name> formula to <pack>

[autogenerated by <model> on <date>]"
git push origin main   # fork tdupu/gascity-packs only
```

### 7. Verify registration

```bash
cd ~/gt && gc pack refresh
gc bd formula show <name>
```

If `gc bd formula show` returns the formula, it is live in the city.

---

## TOML anatomy quick reference

| Field | Level | Required | Notes |
| --- | --- | --- | --- |
| `description` | top | yes | Multi-line docstring |
| `formula` | top | yes | Must match filename stem |
| `version` | top | yes | Integer; start at 1 |
| `phase` | top | no | `"vapor"` for shell-only |
| `contract` | top | no | `"graph.v2"` for build-base |
| `extends` | top | no | Array of base formula names |
| `target_required` | top | no | Boolean; require a sling target |
| `[requires]` | top | no | `formula_compiler = ">=2.0.0"` |
| `[catalog]` | top | yes | `name` + `description` |
| `[vars.<name>]` | top | no | Repeat per variable |
| `[[steps]]` | repeating | yes | At least one step |
| `steps.id` | step | yes | Unique, kebab-case |
| `steps.title` | step | yes | Human label |
| `steps.needs` | step | no | Array of prior step ids |
| `steps.metadata` | step | no | Inline table; `gc.run_target` key |
| `steps.description` | step | yes* | Inline or via `description_file` |
| `steps.description_file` | step | yes* | Alternative to inline description |
| `[steps.check]` | step | no | `max_attempts`, nested check block |

*One of `description` or `description_file` is required per step.

---

## What this skill does NOT do

- Does NOT touch `~/repos/gascity-packs/gastown/` (standing: never modify gastown/).
- Does NOT push to `gastownhall/gascity-packs` upstream or open upstream PRs.
- Does NOT create bare SKILL.md skills (use `skill-creator-math` for those).
- Does NOT run the surface test for non-mathcity packs (test is not yet
  generalised — see gsp-8n7).
- Does NOT commit automatically — always show the diff and get confirmation
  before `git commit`.
