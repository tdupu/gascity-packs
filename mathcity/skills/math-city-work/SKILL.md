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

## Sling command — the work-dispatch formulas

The `*-briefed` set **grows** — always confirm the live catalog with Step A
(`gc formula list | grep -i briefed`) before dispatching, and never pass a name
it did not return. The five below are the Mayor-dispatchable work formulas as of
this writing (verify against Step A, do not treat as closed). Run every
`gc sling` **from the bead's rig dir** (e.g. `~/gt/hecke` for `he-*`) so bd
resolves. Shared defaults on the work formulas — `interaction_mode=autonomous`,
`review_mode=agent`, `drain_policy=separate`, `push=false`, `open_pr=false` —
mean nothing ships; a decision brief fires at the terminal slot instead.

⚠️ **`artifact_root` discipline (all builds):** scope it **per bead**
(`<rig-root>/.gc-builds/<bead>`) — never the bare rig root, never omitted.
Concurrent builds sharing an `artifact_root` silently overwrite each other's
`implementation-plan.md` / `requirements.md` / `decomposition.md` (confirmed
data loss, `gsp-1bmxuz`). Residual: re-dispatching the SAME bead while a prior
run's artifacts are still present overwrites them in place — that is what the
verify-assignee gate (next section) guards against.

| Formula | When to use it | Usage notes (vars → what they do) | Testing |
|---|---|---|---|
| **`work-briefed`** — default router | You're unsure which cycle fits, or the bead already carries a decision brief. Auto-routes to `simple-work-briefed` (bounded) vs `build-basic-briefed` (full cycle) by assessing bead complexity. Safe default. | `--var source_bead=<bead>` (bead to route, **required**); `--var artifact_root=<rig-root>/.gc-builds/<bead>` (**required** — scope per bead); `--var brief_slug=<bead>-brief` (**required** — brief filename stem); `--var model=haiku` (simple-path exec model, ignored on full-path); `--var brief_type=standard`; plus shared defaults. | Created S25 (`gt-i919hq`); routing verified live S27 (`he-7efhhb`). The well-tested auto-dispatch path. |
| **`build-basic-briefed`** — full factory | Genuinely complex, multi-file work needing requirements → plan → decompose → implement → review → finalize. **Preferred** feed formula (policy `gsp-fhdnu`) because it emits the terminal decision brief. | `--var artifact_root=<rig-root>/.gc-builds/<bead>` (⚠️ **must** scope per bead — see the callout above); `--var interaction_mode=autonomous --var review_mode=agent --var drain_policy=separate`; `--var push=false --var open_pr=false` → brief only, never ships. | Mechanism D2 POC-3 (`gsp-510c`, landed `cebde05`); full `work → build-basic-briefed → brief → pile → shuffle → stack` chain proven **live end-to-end** S10 (convoy `gsp-7x9f`); source-verified S14 (the "great regression" was a misdiagnosis, not a break); filter E2E S31–S33. Strongest evidence of the five. |
| **`simple-work-briefed`** — bounded one-off | A very easy, bounded change — Haiku-level single-file edit, a one-shot script run, a small patch, a condition check. Files a brief; never pushes/PRs. | `--var task="<exactly what to do, which inputs to read, expected output>"` (**required**); `--var source_bead=<bead>` (**required**); `--var brief_slug=<bead>-brief` (**required**); `--var context="<paths/beads to read first>"` (optional, default empty); `--var model=haiku` (haiku default; `sonnet` for light reasoning, `opus` high-stakes); `--var artifact_root=.beads/briefs`. | Created S25 (`gt-i919hq`). Exercised as `work-briefed`'s simple path; lighter standalone live-run evidence than `build-basic-briefed`. |
| **`planning-briefed`** — design-first | Planning/design work — an epic or large bead needing a PERT, decomposition, design doc, or requirements before anyone implements. | `--var source_bead=<bead>` (**required**); `--var brief_slug=<bead>-planning` (**required**); `--var interaction_mode=autonomous --var push=false`; `--var plan_type=task-decomposition`; `--var plan_target=gc.design-author` (Opus-tier **fleet address** — NEVER a model name like `opus`/`fable`); `--var context=""`; `--var artifact_root=.beads/briefs`. Pre-flight checks the Opus agent is configured (mode=on_demand, auto-spawned on dispatch). | Created S25-era; `/tmp` artifact-path bug found + fix sent to BART S29 (`gt-esgnqs`). The design-author (Opus) lane works but is **slow** — sessions oscillate asleep↔active, so don't infer death from a snapshot (S7). Lighter E2E evidence. |
| **`smoke-test-briefed`** — test an artifact | Smoke-testing a mathcity artifact — a formula TOML, a `SKILL.md`, a Magma intrinsic, a `.py`, or a `.sh`. Read-only audit; does NOT modify the artifact under test. | `--var artifact_path=<path>` (**required**); `--var artifact_type=<formula\|skill\|magma\|python\|script>` (**required** — selects the test strategy); `--var test_slug=<slug>` (**required**); `--var source_bead=<bead>` (optional — links a provenance event); `--var brief_slug=<test_slug>-smoke-test`; `--var test_root=mathcity/tests`; `--var operator_target=gc.run-operator`; `--var review_target=gc.review-synthesizer`. Writes the test to `mathcity/tests/<slug>/`, runs it, files a brief with evidence + a reproducibility guide. | Created S26 (`gt-3mi885`); it IS the F6.1 vehicle (POLICY-formulas.md: every new formula/artifact needs a passing smoke test before its deploy brief). Limited accumulated run evidence to date. |

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
