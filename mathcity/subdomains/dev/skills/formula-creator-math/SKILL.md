---
name: formula-creator-math
description: >
  Create a new formula TOML for the mathcity pack family, enforcing the
  mandatory "briefed" terminal step convention. Use whenever the user says
  "create a mathcity formula", "formula-creator-math", "new formula for
  <mathcity workflow>", "add a formula that ends in a brief", or asks to
  codify a math-city multi-step workflow as a gc formula. Extends
  formula-creator with mathcity-specific shape selection (methodology vs
  non-methodology), Opus routing (plan_target/proof_target vars), hygiene
  gate, and the enforced briefed-terminal-step policy. NOT for generic
  gascity/superpowers formulas (use formula-creator). NOT for skill SKILL.md
  files (use skill-creator-math).
---

# formula-creator-math

Create a **mathcity formula TOML** with the enforced briefed-terminal-step
convention. All mathcity formulas MUST end with a step that files a decision
brief for Taylor adjudication — this skill enforces that invariant.

Extends [formula-creator](~/repos/gascity-packs/mathcity/skills/formula-creator/SKILL.md)
with mathcity-specific rules. Read formula-creator first for base TOML
mechanics; this skill adds only the delta.

---

## Mandatory invariant — briefed terminal step

Every mathcity formula produced by this skill MUST end with one of:

| Terminal step id | When to use |
|---|---|
| `file-brief` | Task completes and files a brief to `.beads/briefs/` for adjudication |
| `brief-finalize` | After filing, writes a finalization record and drains |
| `workflow-finalize` | Combined brief-file + drain (use when formula is 1–3 steps) |

**Never ship a mathcity formula whose last step is a pure implementation
step** (e.g., `git-push`, `run-script`, `commit`). The brief IS the gate
before anything is merged or published.

---

## Step 0 — Pre-flight

```bash
tmux -L gt ls >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — no tmux fleet server."
  exit 1
}
gc dolt health >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — Dolt is unreachable."
  exit 1
}
```

---

## Step 1 — Determine formula shape

Before writing any TOML, classify the formula into exactly one shape:

| Shape | When | Terminal step |
|---|---|---|
| **do-work** | Bounded single-operation (run a script, apply a patch, generate an artifact). No planning/decompose. | `workflow-finalize` |
| **methodology** | Multi-step: gather requirements → plan → implement → validate → file-brief. Opus needed at plan step. | `file-brief` + `brief-finalize` |
| **non-methodology** | Multi-step but no Opus-class planning. Haiku/Sonnet throughout. | `file-brief` |
| **source-search** | Literature or database search as primary deliverable. | `file-brief` |

**Decision rule:** if the formula needs a `plan` or `design` step, it is
methodology. If it only needs to *execute* something already planned, it is
do-work or non-methodology.

---

## Step 2 — Pick file location

All mathcity formulas go in:

```
~/repos/gascity-packs/mathcity/formulas/<name>.toml
```

Name rules: lowercase, hyphenated. End in `-briefed` when the formula is the
"with-brief-gate" variant of an existing do-work formula (e.g.,
`simple-work-briefed`, `build-basic-briefed`).

---

## Step 3 — Write the TOML skeleton

```toml
description = """
<One paragraph. Include: purpose, input shape, what it enforces (briefed gate),
what it does NOT do.>
"""
formula = "<name>"
version = 1

[requires]
formula_compiler = ">=2.0.0"

[catalog]
name = "<name>"
description = "<One-line for gc formula list.>"

[vars]
[vars.source_bead]
description = "Work bead ID this formula is executing on."
required = true

[vars.brief_slug]
description = "Stable filename stem for the brief artifact (<bead>-<topic>)."
required = true
pattern = "^[A-Za-z0-9._-]+$"

[vars.model]
description = "Execution model. haiku for mechanical; sonnet for judgment; opus for planning."
default = "sonnet"
enum = ["haiku", "sonnet", "opus"]

[vars.artifact_root]
description = "Root for brief artifacts."
default = ".beads/briefs"
```

Add shape-specific vars:

- **methodology**: `[vars.plan_target]` and/or `[vars.proof_target]` (Opus
  routing — the planning/proof steps use these to override the fleet pool).
- **non-methodology/do-work**: `[vars.context]` for optional extra context.

---

## Step 4 — Write steps

### do-work shape (1–3 steps)

```toml
[[steps]]
id = "execute-task"
title = "Execute {{source_bead}}"
metadata = { "gc.run_target" = "{{model}}" }
description = """
<What to do. Read the bead. Perform the bounded operation.
Record results to bd notes.>
"""

[[steps]]
id = "workflow-finalize"
needs = ["execute-task"]
title = "File brief and finalize"
metadata = { "gc.run_target" = "mathcity.brief-operator" }
description = """
File a decision brief summarizing what was done, what changed, and what
Taylor needs to adjudicate. Then drain.

```bash
# File brief
mkdir -p {{artifact_root}}/stack
cat > {{artifact_root}}/stack/{{brief_slug}}.md << 'EOF'
---
status: approved
brief_bead: {{source_bead}}
...
EOF

gc runtime drain-ack
```
"""
```

### methodology shape (5+ steps)

Include: `gather-requirements` → `plan` (Opus via `plan_target`) →
`implement` → `validate` → `file-brief` → `brief-finalize`.

The `plan` step MUST carry:
```toml
metadata = { "gc.run_target" = "{{plan_target}}" }
```

with `[vars.plan_target]` defaulting to `opus` or a named Opus session.

### non-methodology shape (3–5 steps)

Include the relevant work steps and end with `file-brief`. No `plan_target` var.

---

## Step 5 — Hygiene gate

Before committing:

```bash
cd ~/repos/gascity-packs

# 1. Secrets scan
gitleaks detect --no-git --source mathcity/formulas/<name>.toml

# 2. Verify briefed terminal step exists
python3 -c "
import tomllib, sys
with open('mathcity/formulas/<name>.toml', 'rb') as f:
    d = tomllib.load(f)
steps = d.get('steps', [])
assert steps, 'No steps defined'
last = steps[-1]['id']
allowed = {'file-brief', 'brief-finalize', 'workflow-finalize'}
assert last in allowed, f'Terminal step is \"{last}\" — must be one of {allowed}'
print(f'OK: terminal step = {last}')
"

# 3. Validate TOML parses
python3 -c "import tomllib; tomllib.load(open('mathcity/formulas/<name>.toml','rb'))" \
  && echo "TOML valid"
```

If the terminal-step assertion fails, fix before committing. No exceptions.

---

## Step 6 — Update README-formulas.md (REQUIRED — hard gate)

Every new mathcity formula MUST have a row in `mathcity/README-formulas.md`
before the brief is filed. This is a hard gate — do not file the brief until
this check passes:

```bash
grep -q '<name>' ~/repos/gascity-packs/mathcity/README-formulas.md \
  && echo "README-formulas.md OK" \
  || echo "FAIL README-formulas.md — add row before filing brief"
```

Add ONE row under the formulas table, alphabetically by formula name:

```
| `<name>` | <methodology|do-work|proof> | <One sentence from the TOML description field.> |
```

Commit the README-formulas.md update together with the formula TOML (same commit).

---

## Step 7 — Commit and push

```bash
cd ~/repos/gascity-packs
git add mathcity/formulas/<name>.toml mathcity/README-formulas.md
git commit -m "feat(mathcity): add <name> formula (briefed terminal step enforced)

[autogenerated by claude-sonnet-4-6 on $(date +%Y-%m-%d)]"
git push fork main
```

Then message BART to pull the fork into `~/gt/gascity-packs`:

```
gc mail send bart "New formula <name> pushed to tdupu/gascity-packs fork main. Please pull and run gc supervisor install --force." --subject "[ACTION REQUIRED]"
```

---

## Common mistakes to avoid

| Mistake | Fix |
|---|---|
| Last step is `git-push` or `run-script` | Must be `file-brief` / `workflow-finalize` |
| `plan_target` missing for methodology shape | Add `[vars.plan_target]` defaulting to `opus` |
| Formula in wrong pack | mathcity formulas go in `mathcity/formulas/`, NOT `gascity/formulas/` |
| No `[catalog]` block | Required for `gc formula list` discovery |
| `needs` missing on all but first step | Every step after the first MUST declare `needs` |

---

## Provenance

- Base skill: `formula-creator` (`~/repos/gascity-packs/mathcity/skills/formula-creator/SKILL.md`)
- Briefed-terminal policy: gsp-ez3x6 (formula-creator-math epic)
- Pack boundary rules: `mathcity/subdomains/dev/POLICY.md`
- ADR: `docs/adr/0002-mathcity-subdomain-pack-model.md`
