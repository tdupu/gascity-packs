---
name: formula-work
description: >
  Dispatch a bead to the formula-creator-math formula, which drafts a
  mathcity formula TOML and gates it behind a Taylor decision brief. Use
  when the user says "create a formula for <bead>", "dispatch formula
  creation", "sling formula-creator-math", "formula-work", "make a formula
  for this bead and brief it", "codify this workflow as a mathcity formula",
  or "run formula-work on <bead>". NOT for creating skills (use
  skill-creator-math). NOT for running formula work directly inline (use
  formula-creator-math). NOT for testing (use testing-work).
---

# formula-work — dispatch a formula creation task with a brief at the end

Companion dispatch skill for [`formula-creator-math`](../formula-creator-math/SKILL.md).
While `formula-creator-math` describes HOW to write a formula inline, this
skill tells you how to **dispatch** that work through the fleet via `gc sling`
so the formula is drafted, validated, and briefed asynchronously.

Think of it as: **`simple-work` is to `simple-work-briefed`** as
**`formula-work` is to `formula-creator-math`**.

## Formula policy — read before dispatching

**Read [`mathcity/POLICY-formulas.md`](../../../../POLICY-formulas.md) (v1.3)
before authoring any formula spec or filing a sling command.** The six pillars:

| Pillar | Rules | What to check |
|--------|-------|---------------|
| F1 | F1.1–F1.3 | Planning steps → high-tier fleet address; execution → low-tier; never model names as `gc.run_target` |
| F2 | F2.1–F2.3 | Temp files cleaned up; clones bounded; shared paths declared |
| F3 | F3.1–F3.3 | Formula-creation formulas audit against POLICY-formulas.md; vars with run_target-bound defaults use fleet addresses |
| F4 | F4.1 | `/check-zero` + `/check-wheel` run before terminal brief; verdicts in brief |
| F5 | F5.1–F5.2 | `/fp-finder` (or `/coordinate-review`) + `/critical-review` pass before dispatch; plan passes `/critical-review` before execution |
| F6 | F6.1 | Smoke test exists, has been run, and passed before brief is filed |

The fleet agent running `formula-creator-math` checks F-rules in its validate
step, but reviewing them before dispatch prevents a round-trip brief rejection.

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

## Pre-dispatch review gates (F5.1)

Before slinging, run `/check-zero` and `/check-wheel` on the proposed formula,
then run `/fp-finder` (or `/coordinate-review`) and `/critical-review`. Record
verdicts. Only proceed if all return passing results (or document the exception
in the brief).

## Dispatch command

```bash
gc sling <rig>/gc.run-operator <bead> --on formula-creator-math \
  --var source_bead=<bead> \
  --var brief_slug=<bead>-<short-slug> \
  --var formula_name=<new-formula-name> \
  --var model=gc.run-operator \
  --var plan_target=gc.run-operator \
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
| `model` | `gc.run-operator` | Use `gc.design-author` (Opus-backed) when the formula shape is ambiguous or methodology; **never pass a bare model name** (F1.3) |
| `plan_target` | `gc.run-operator` | Use `gc.design-author` for methodology-shape formulas once gsp-ez3x6.7 ships; **never `fable`/`opus`/`sonnet`** |
| `artifact_root` | `.beads/briefs` | Leave at default unless the rig uses a non-standard brief root |
| `context` | (empty) | Pass file paths, bead IDs, or inline text the polecat needs to understand the formula spec |

### Fleet address guidance

- **`gc.run-operator`** — default; sufficient for clear specs (non-methodology, do-work, source-search shapes).
- **`gc.design-author`** — use when the formula is methodology shape (needs a plan/design step) or when the spec bead is underspecified. Available once gsp-ez3x6.7 ships.
- **Never pass bare model names** (`fable`, `opus`, `sonnet`, `haiku`) — these produce "unknown formulas v2 target" runtime errors (F1.3).

## MANDATORY — verify-assignee gate

**A sling you did not verify may have stranded.** Within ~30–60s of slinging:

```bash
bd show <bead> | grep -i assignee   # must be NON-EMPTY
```

If Assignee is empty after 60s, check the molecule:

```bash
bd show <molecule-bead> | head -5
```

## What happens after dispatch

1. Fleet polecat picks up the molecule (`formula-creator-math`).
2. **gather-spec**: reads `source_bead`, extracts formula name, shape, vars, step list; records spec in bead notes.
3. **draft-toml**: writes draft TOML to `/tmp/<formula_name>.toml` following shape classification.
4. **validate**: TOML hygiene + terminal-step check + F-rule audit against POLICY-formulas.md + `/check-zero` + `/check-wheel`.
5. **file-brief**: decision brief with full TOML draft inline for Taylor adjudication.
6. Brief lands on the stack → Taylor adjudicates.

After **A (approve)**: executing agent commits TOML, pushes to fork, messages BART to pull. No push without that gate.

## Testing requirement (F6.1)

Before filing the terminal brief, the formula agent must also produce a smoke
test in `mathcity/tests/<formula_name>/smoke_test.sh` (or equivalent). Use
`/testing-work` (the `smoke-test-briefed` formula) to dispatch test creation
as a parallel step, or include test creation in the formula spec bead. The
brief must include test run evidence.

## Example

```bash
cd ~/gt/gascity-packs
gc sling gascity-packs/gc.run-operator gsp-ez3x6.3 --on formula-creator-math \
  --var source_bead=gsp-ez3x6.3 \
  --var brief_slug=gsp-ez3x6.3-data-work-briefed \
  --var formula_name=data-work-briefed \
  --var model=gc.run-operator \
  --var context="Shape: do-work. Purpose: fetch data from LMFDB or a local db and store result; brief at end. See gsp-ez3x6 for overall epic context."
```

## Provenance

- Formula: `formula-creator-math` (`gc formula show formula-creator-math`)
- Policy: `mathcity/POLICY-formulas.md` (prefix F, v1.3)
- Formula epic bead: `gsp-ez3x6`
- Companion dispatch skill (testing): `testing-work` (`mathcity-dev.testing-work`)
- Companion dispatch skill (one-off work): `simple-work` (`mathcity.simple-work`)
