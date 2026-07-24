---
name: math-city-work
description: >
  Feed a bead (or a set of ready beads) into the math-city fleet the correct,
  S14-verified way. Use whenever the Mayor (QUIMBY) wants to dispatch work:
  "math-city-work", "feed the machine", "feed this bead to the fleet",
  "dispatch this the right way", "sling <bead> the preferred way", "put this
  through the fleet", or "get the fleet working on <bead>". Encodes the
  feed-don't-hand-sling doctrine, formula selection (work-briefed default,
  build-basic-briefed / planning-briefed / smoke-test-briefed explicit), the
  mandatory verify-assignee gate, and the slow-build-≠-strand rules that stop
  a healthy fleet from looking broken.
  NOT for adjudicating briefs (use adjudicate-brief) or manual one-by-one
  hand-slinging (that is the anti-pattern this skill exists to replace).
---

# math-city-work — feed the machine the correct way

The canonical dispatch skill for the math-city Mayor. It codifies the
S14-verified doctrine so no future QUIMBY re-derives it (or re-panics over a
healthy-but-slow fleet — see `bd recall great-regression-misdiagnosis-s14`).

## Pre-flight (fleet must be up)

Verify the fleet is actually alive BEFORE dispatching — and verify it the
reliable way, not via `gc status` (its runtime probe times out and reports a
false "stopped/0", bug **gs-0cy2**):

```bash
tmux -L gt ls >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — no tmux fleet server (the city can't spawn agents)."
  echo "Run 'gc restart' to give the supervisor a fresh tmux server, then retry."
  exit 1
}
gc dolt health >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — Dolt is unreachable (bd cannot resolve beads)."
  echo "Run 'gc dolt status' / 'gc dolt start' and retry."
  exit 1
}
```

## Rule 0 — FEED THE MACHINE, DON'T HAND-SLING

The Mayor's job is **queue health + unblocking**, not manual dispatch. Make
the bead **ready and unblocked** (deps closed, priority set, rig correct); the
dispatcher auto-pulls ready work. Do **not** sling work items one-by-one as a
matter of course — that was the QUIMBY-13 misfire. Hand-dispatch is only for a
specific bead you deliberately want built now.

## Formula selection — choose the right tool

**Default: `work-briefed`** — auto-routes between `simple-work-briefed` and
`build-basic-briefed` based on bead complexity. Use this when you are not
certain which formula fits; the router decides.

| Formula | Use when |
|---|---|
| `work-briefed` | **Default.** Let the router decide between simple and full cycle. |
| `build-basic-briefed` | Full 37-step factory: requirements → plan → decompose → implement → review → finalize → brief. Use when the bead is complex, multi-file, or needs starter review. |
| `simple-work-briefed` | Single bounded operation (run a script, apply a patch, verify a condition, generate an artifact). No planning needed; result still needs Taylor adjudication. |
| `planning-briefed` | Produce a planning artifact (PERT, task decomposition, design doc, requirements) **before** implementation begins. Use for epics or large beads that need design-first. Routes to `gc.design-author` (Opus-level, on_demand). |
| `smoke-test-briefed` | Run a smoke test on a formula, skill, Magma intrinsic, or script and file a brief with test evidence (satisfies F6.1). |

When in doubt between `build-basic-briefed` and `simple-work-briefed`, pick
`work-briefed` and let the router decide. Only pick `build-basic-briefed`
explicitly when you know the bead is full-cycle work.

## Sling command (replace `<formula>` with your selection above)

```bash
gc sling <rig>/gc.run-operator <bead> --on <formula> \
  --var interaction_mode=autonomous --var review_mode=agent \
  --var drain_policy=separate --var push=false --var open_pr=false
```

(Run from the correct rig dir, e.g. `~/gt/hecke` for `he-*`, so bd resolves.)

**`planning-briefed` requires two extra vars:**
```bash
gc sling <rig>/gc.run-operator <bead> --on planning-briefed \
  --var source_bead=<bead> --var brief_slug=<bead>-planning \
  --var interaction_mode=autonomous --var push=false
```

## MANDATORY — the verify-assignee gate

**A sling you did not verify is a sling that may have stranded.** Immediately
after slinging, confirm the worker claimed it:

```bash
bd show <bead> | grep -i assignee   # must be NON-EMPTY
```

If Assignee is still empty after ~30–60s, re-check and escalate — do **not**
assume success. This gate is the loud-failure guard that S13 lacked.

## SLOW-BUILD ≠ STRAND (do not misread a healthy fleet)

- **Molecule roots stay OPEN by design** until every terminal step finishes.
  An open `build-basic-briefed` root is **not** a strand — check its progress
  by counting closed steps, and watch the count climb:
  ```bash
  bd show <root> | grep -c "✓ "     # run twice, minutes apart — it rises
  ```
- **`gc status` "0/N" / "stopped" is a slow-API probe-timeout artifact**
  (gs-0cy2), NOT an idle fleet. Ground-truth liveness is `tmux -L gt ls`
  (live sessions) + climbing step-counts + fresh commits in build worktrees.
- **Brief latency is normal.** The decision brief fires only at the terminal
  publish / "Produce decision brief" step, so expect a delay after slinging.
  "No brief yet" ≠ "broken." A real bug exists only if a molecule *closes* its
  publish step and **no** brief lands on the stack.

## Provenance (source of truth)

- Policy: `gsp-fhdnu` (build-basic-briefed = preferred feed formula; work-briefed = routing wrapper)
- Bug: `gs-0cy2` (gc status probe-timeout false "stopped/0")
- Doctrine: `he-uz9fg` (verify-assignee + slow-build≠strand doc fix)
- Full story: `bd recall great-regression-misdiagnosis-s14`

Recommended model: **Sonnet** (dispatch + verify — mechanical with light
judgment). Use **Opus** or **Fable** only if the formula selection requires
architectural judgment.
