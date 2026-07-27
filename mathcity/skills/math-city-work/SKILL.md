---
name: math-city-work
description: >
  Feed a bead (or a set of ready beads) into the math-city fleet the correct,
  S14-verified way. Use whenever the Mayor wants to dispatch work:
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
S14-verified doctrine so no future Mayor session re-derives it (or re-panics over a
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
matter of course — that was the Mayor session-13 misfire. Hand-dispatch is only for a
specific bead you deliberately want built now.

## Formula selection — enumerate, then use judgement (do NOT hardcode)

The set of `*-briefed` formulas **grows and changes**. This skill deliberately
does NOT carry a fixed list to route against — a hardcoded switch falls out of
date the moment a new briefed formula lands (`smoke-test-briefed` was exactly
that miss). Selecting the formula is a **reasoning task for you**, not a lookup.

**Step A — enumerate the LIVE set at dispatch time.** Read what actually
exists right now; never assume the examples below are the complete set:

```bash
gc formula list 2>/dev/null | grep -i briefed        # authoritative: current catalog names
# fallback if gc is slow/unavailable:
ls -1 ~/gt/gascity-packs/mathcity/formulas/*briefed* 2>/dev/null
```

**Step B — read the bead and judge which enumerated formula fits.** Look at
`bd show <bead>` — its type, scope, file blast-radius, whether it needs design,
whether it is itself a test — and reason about which of the *currently
enumerated* briefed formulas is the right vehicle. The points below are
**signals to weigh, not an exhaustive routing table**; new briefed formulas
will introduce right answers this skill cannot predict, so always reason
against Step A's actual output, not this list:

- The bead already carries a decision **brief**, or you are unsure which cycle
  fits → **`work-briefed`** (the router — it decides simple vs. full for you).
  This is the safe default and the well-tested auto-dispatch path.
- A **very easy, bounded** change — Haiku-level single-file edit, a one-shot
  script run, a small patch, a condition check → **`simple-work-briefed`**.
- **Planning / design-first** work (an epic or large bead that needs a PERT,
  decomposition, design doc, or requirements before anyone implements) →
  **`planning-briefed`** (routes to Opus-tier `gc.design-author`).
- **Testing** an artifact (formula, skill, Magma intrinsic, script) →
  **`smoke-test-briefed`**.
- Genuinely **complex, multi-file, full-cycle** build work needing the
  requirements → plan → decompose → implement → review → finalize factory →
  **`build-basic-briefed`**.

If none of the enumerated formulas cleanly fits, fall back to **`work-briefed`**
and let the router decide — do not force a poor match, and never pass a formula
name that Step A did not actually return.

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

## Dispatch provenance event

Every `gc sling` outcome gets a linked event bead; files, tables, and brief
mentions are caches of that event. Use `dispatch-provenance.v1` so downstream
lost-bead filters can treat work-system and brief-system dispatch uniformly.

```toml
schema = "dispatch-provenance.v1"
source_bead = "<bead>"
dispatch_command = "gc sling <rig>/gc.run-operator <bead> --on <formula> ..."
formula = "<formula>"
verified_assignee = true
assignee_state = "non_empty"
classification_hint = "healthy"
fingerprint = "verified_sling_claimed"
observed_at = "YYYY-MM-DDTHH:MM:SSZ"
```

If the verify-assignee gate stays empty, record the event as the canonical
strand evidence before escalating:

```toml
schema = "dispatch-provenance.v1"
source_bead = "<bead>"
dispatch_command = "gc sling <rig>/gc.run-operator <bead> --on <formula> ..."
formula = "<formula>"
verified_assignee = false
assignee_state = "empty_after_60s"
classification_hint = "immediate_strand"
fingerprint = "empty_assignee_after_verified_sling"
observed_at = "YYYY-MM-DDTHH:MM:SSZ"
```

Create the event with:

```bash
bd create "dispatch provenance for <bead>" --type event --event-category dispatch.provenance --event-target <bead> --event-payload '<dispatch-provenance.v1 TOML or JSON>' --silent
```

Then link it to the source bead with `bd dep relate <event-bead> <bead>`.

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
