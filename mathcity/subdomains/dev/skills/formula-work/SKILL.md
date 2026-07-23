---
name: formula-work
description: >
  Dispatch a bead to the formula-creator-math formula, which drafts a
  mathcity formula TOML and gates it behind a Taylor decision brief. Use
  when the user says "create a formula for <bead>", "dispatch formula
  creation", "sling formula-creator-math", "formula-work", "make a formula
  for this bead and brief it", or "codify this workflow as a mathcity
  formula". NOT for creating skills (use skill-creator-math). NOT for
  running formula work directly inline (use formula-creator-math).
---

# formula-work — dispatch a formula creation task with a brief at the end

Companion dispatch skill for [`formula-creator-math`](../formula-creator-math/SKILL.md).
While `formula-creator-math` describes HOW to write a formula inline, this
skill tells you how to **dispatch** that work through the fleet via `gc sling`
so the formula is drafted, validated, and briefed asynchronously.

Think of it as: **`simple-work` is to `simple-work-briefed`** as
**`formula-work` is to `formula-creator-math`**.

## Pre-flight (fleet must be up)

```bash
tmux -L gt ls >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — no tmux fleet server."
  echo "Run 'gc restart' to give the supervisor a fresh tmux server, then retry."
  exit 1
}
gc dolt health >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — Dolt is unreachable (bd cannot resolve beads)."
  echo "Run 'gc dolt status' / 'gc dolt start' and retry."
  exit 1
}
```

## Dispatch command

```bash
gc sling <rig>/gc.run-operator <bead> --on formula-creator-math \
  --var source_bead=<bead> \
  --var brief_slug=<bead>-<short-slug> \
  --var formula_name=<new-formula-name> \
  --var model=<haiku|sonnet|opus> \
  --var context="<optional: file paths, bead IDs, or inline notes for gather-spec>"
```

Run from the rig root where the bead lives (e.g. `~/gt/gascity-packs` for
`gsp-*` beads, `~/gt/hecke` for `he-*` beads).

### Required vars

| Var | What to put |
|-----|-------------|
| `source_bead` | Bead ID describing the formula to create (the spec lives here) |
| `brief_slug` | Stable filename stem for the brief artifact (`<bead>-<topic>`) |
| `formula_name` | Proposed formula name (lowercase, hyphenated; e.g. `proof-search-briefed`) |

### Optional vars

| Var | Default | When to override |
|-----|---------|-----------------|
| `model` | `sonnet` | Use `opus` when the formula shape is ambiguous or methodology; `haiku` is not recommended for formula authoring |
| `artifact_root` | `.beads/briefs` | Leave at default unless the rig uses a non-standard brief root |
| `context` | (empty) | Pass file paths, bead IDs, or inline text the polecat needs to understand the formula spec |

### Model guidance

- **sonnet** — default; sufficient for clear specs (non-methodology, do-work, source-search shapes).
- **opus** — use when the formula is methodology shape (needs a plan/design step) or when the spec bead is underspecified.
- **haiku** — too weak for formula authoring; avoid.

## MANDATORY — verify-assignee gate

**A sling you did not verify may have stranded.** Within ~30–60s of slinging:

```bash
bd show <bead> | grep -i assignee   # must be NON-EMPTY
```

If Assignee is empty after 60s, check the molecule:

```bash
bd show <molecule-bead> | head -5   # molecule-bead ID printed at sling time
```

## What happens after dispatch

1. Fleet polecat picks up the molecule (`formula-creator-math`).
2. **Step 1 — gather-spec**: reads `source_bead`, extracts formula name,
   shape, vars, and step list; records spec in bead notes.
3. **Step 2 — draft-toml**: writes a draft formula TOML to `/tmp/<formula_name>.toml`
   following the shape classification.
4. **Step 3 — validate**: runs three hygiene checks (TOML parses, terminal
   step is `file-brief`/`brief-finalize`/`workflow-finalize`, catalog fields
   present). Fixes any failures in-place before proceeding.
5. **Step 4 — file-brief**: files a decision brief with the full TOML draft
   inline so Taylor can review and adjudicate inline.
6. Brief lands on the stack → `/check-briefs` finds it → Taylor adjudicates.

After an **A (approve)** verdict, the executing agent:
1. Commits the TOML to `mathcity/formulas/<formula_name>.toml`
2. **Adds a row to `mathcity/README-formulas.md`** (REQUIRED — same commit)
3. Pushes to fork and messages BART to pull

No formula is considered shipped until it appears in `README-formulas.md`.
Check before marking done:
```bash
grep -q '<formula_name>' ~/repos/gascity-packs/mathcity/README-formulas.md \
  && echo "README-formulas.md OK" \
  || echo "FAIL — add row before marking done"
```

## Example — dispatch a formula creation bead

```bash
cd ~/gt/gascity-packs
gc sling gascity-packs/gc.run-operator gsp-ez3x6.3 --on formula-creator-math \
  --var source_bead=gsp-ez3x6.3 \
  --var brief_slug=gsp-ez3x6.3-data-work-briefed \
  --var formula_name=data-work-briefed \
  --var model=sonnet \
  --var context="Shape: do-work. Purpose: fetch data from LMFDB or a local db and store result; brief at end. See gsp-ez3x6 for overall epic context."
```

## Hygiene invariant enforced by formula-creator-math

The validate step WILL reject any draft whose terminal step is not one of
`{file-brief, brief-finalize, workflow-finalize}`. This is the core invariant
of the mathcity formula family. If the spec bead describes a formula that
ends in `git-push`, `run-script`, or similar, the agent MUST restructure the
steps before proceeding.

## Provenance

- Formula: `formula-creator-math` (`gc formula show formula-creator-math`)
- Formula epic bead: `gsp-ez3x6`
- Companion formula-creation skill (inline): `formula-creator-math` (`mathcity-dev.formula-creator-math`)
- Companion dispatch skill (one-off work): `simple-work` (`mathcity.simple-work`)
- Briefed-terminal policy: ADR `docs/adr/0002-mathcity-subdomain-pack-model.md`
