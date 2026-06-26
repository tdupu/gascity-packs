# Ops Pack

Operational/substrate primitives for Gas Town. Sibling to `gastown/` and
`mathematics/`.

## When to choose `ops`

- You need a **long-running, monitored experiment** (compute job, soak
  test, cross-host benchmark) and want adaptive-cadence health-checks,
  Mayor escalation when it goes red, and an automatic callback when it
  finishes.
- You want **cross-rig instrumentation** (dispatch reliability,
  restoration drills, heartbeat plumbing) without dragging it into a
  domain pack.
- You want to **auto-execute briefs the classifier flagged as
  no-brainers** (stale-branch deletion, ratify-existing-held, close-
  with-cited-commit, execution-confirmation-with-proof) without Taylor
  per-brief attention — the execution half of the no-brainer cycle
  paired with the [[catch-no-brainer]] skill in agent-skills.
- You want a **public, non-mathematical** home for ops primitives so the
  math pack (`mathematics/`) stays focused on research content and
  `gastown/` stays focused on coordination.

## What the pack ships (Phase 1 scaffold)

This is the **Phase 1 scaffold** of the experiment-lifecycle pipeline
designed in `he-6lz0-redesign-brief.md` §3.2. The full plan is 7 phases
(see [Phases](#phases) below); this scaffold lands the directory layout
and the drop-off / pickup / check-on-it formulas + their triggering
orders in stub form so subsequent phases land green-field instead of
introducing new top-level shape.

```
ops/
  pack.toml
  README.md
  formulas/
    experiment-lifecycle.toml          # parent orchestrator (ack → run → check-loop → pickup)
    experiment-acknowledge.toml        # ack drop-off, stamp metadata, register check schedule
    experiment-check-on-it.toml        # one-pass check; classify; update next_check_at; maybe escalate
    experiment-pickup.toml             # wake source polecat; hand back artifacts; close bead
    experiment-respawn.toml            # decision-matrix-driven unclaim + repool (Phase 5; stub)
    escalate-stuck-experiment.toml     # Mayor mail emitter (Phase 4; stub)
    no-brainer-cycle.toml              # execute disposition of a no-brainer brief (Phase 8b; stub)
    gates/
      experiment-must-have-target.toml         # dispatch-side check formula
      experiment-must-have-clerk-route.toml    # drop-off validation check formula
      brief-must-have-classifier-verdict.toml  # no-brainer-cycle defense-in-depth gate
      brief-must-not-be-server-touching.toml   # no-brainer-cycle cat-E re-check
  orders/
    on-experiment-dropoff.toml         # event → experiment-acknowledge
    watchdog-adaptive-check.toml       # cooldown (dynamic) → experiment-check-on-it
    on-experiment-done.toml            # event → experiment-pickup
    on-experiment-health-red.toml      # event → escalate-stuck-experiment (Phase 4; stub)
    on-experiment-session-dead.toml    # event → experiment-respawn (Phase 5; stub)
    on-no-brainer-pile.toml            # event → no-brainer-cycle (Phase 8a; stub)
  agents/
    .gitkeep                           # experiment-clerk role decision deferred — see §5.3
  assets/
    .gitkeep                           # cadence script helpers land here
```

The stubs are valid TOML and parse-clean against `gc formula list` /
`gc order list`. Behaviour land in the named follow-up phases — current
state is "scaffold + design contracts captured in `description = `"
blocks", not "ready to fire".

## Core contracts

### Experiment bead

An "experiment" is any work bead with `metadata.experiment = true`.
Standard metadata the lifecycle reads:

| Key | Required | Default | Purpose |
|---|---|---|---|
| `experiment` | yes | — | Marks the bead as an experiment. |
| `heartbeat_interval` | no | `5m` | `H_floor` — stale threshold. |
| `heartbeat_grace` | no | `3 × heartbeat_interval` | CONFIRMING window. |
| `confirming_poll_interval` | no | `30s` | Dense-poll rate in CONFIRMING. |
| `healthy_max_interval` | no | `1h` | HEALTHY backoff cap. |
| `healthy_backoff_base` | no | `2` | HEALTHY doubling base. |
| `next_check_at` | written | — | ISO-8601; lifecycle writes; order reads. |
| `last_heartbeat` | written | — | Updated by source polecat. |
| `health` | written | — | `green` / `yellow` / `red`. |
| `respawn_allowed` | no | `false` | Gates `experiment-respawn`. |

### Adaptive cadence — HYBRID (A) + (C)

Two modes (per `he-6lz0-redesign-brief.md` §4.2):

- **HEALTHY**: heartbeat fresh. Cooldown follows exponential backoff
  from `healthy_backoff_base` up to `healthy_max_interval`. Each
  successful heartbeat resets to `max(current, position - 1)` — keeps
  prior backoff state; doesn't snap to floor.
- **CONFIRMING**: heartbeat stale but still within `heartbeat_grace`.
  Cooldown drops to `confirming_poll_interval` (default 30s). On
  resume → return to HEALTHY at unchanged position. On grace
  exhaustion → emit `on-experiment-health-red`, transition back to
  sparse polling (escalation owns RED, not the watchdog).

Cadence state lives in `metadata.next_check_at` on the experiment bead;
the `watchdog-adaptive-check` order is **stateless across fires** and
single-pass (satisfies `[[dispatcher-policy-no-infinite-loop]]`).

### Drop-off / pickup metaphor

Per `he-6lz0-redesign-brief.md` §5, ownership transfers from the source
polecat to the experiment-clerk daemon (formula, not literal agent —
see §5.3) on drop-off, and is handed back on pickup. The source-polecat
session can exit between drop-off and pickup; the clerk wakes it (or
its successor) when the experiment finishes.

### No-brainer cycle (execution half)

The pack also hosts the **execution half** of the no-brainer cycle —
the inverse of the classifier in [[catch-no-brainer]] (agent-skills).
Both compose into one closed loop:

  brief lands → classifier writes verdict → cycle executes disposition
  → audit line in `decisions.jsonl` → cluster moves on.

The classifier is **detection** (a skill, judgment-load floor only).
The cycle is **execution** (a formula here, mechanical only). Per
Taylor's 2026-06-25 directive this is shape n=3 of
`[[gascity-orders-and-formulas-decomposition-pattern]]`, alongside the
brief-pipeline (n=1) and experiment-monitoring (n=2).

Categories the cycle handles (set by the classifier, normative now):

| Category                              | Mechanical action                           |
|---------------------------------------|---------------------------------------------|
| `stale-branch` (cat-A)                | Delete branch; close parent bead.           |
| `done-with-cited-commit`              | Verify SHA in `origin/main`; close parent.  |
| `defer-ratify-existing-held`          | Stamp deferred; leave parent open.          |
| `execution-confirmation-with-proof`   | Verify proof reachable in git; close parent.|

Defense-in-depth gates re-check at execution time before any
destructive action — verdict freshness
(`brief-must-have-classifier-verdict`) and server-set non-touch
(`brief-must-not-be-server-touching`). Refusals append a
`disposition=refused` line to `decisions.jsonl` and route to Mayor;
never act on a stale or cat-E verdict.

Full schema for `decisions.jsonl` and the per-category dispatch table
live in `formulas/no-brainer-cycle.toml`.

## Phases

This pack lands in 8 phases. **Phase 1 (this scaffold)** is the first;
subsequent phases file as sub-beads under `as-bzu` (experiment lane) or
`as-4i8` (no-brainer-cycle lane).

| Phase | Scope | Bead |
|---|---|---|
| 1 | Pack scaffold + Phase 1 TOML stubs (this work) | `as-bzu` |
| 2 | HYBRID adaptive cadence implementation in `experiment-check-on-it` | TBD |
| 3 | Experiment-clerk daemon-formula (E4c shape per §5.3) | TBD |
| 4 | Heartbeat metadata writes + `escalate-stuck-experiment` | TBD |
| 5 | Restoration drill (cron-wakeup of brainstorm A6) | TBD |
| 6 | Cross-host SSH heartbeat tunnel | TBD |
| 7 | Cross-rig instrumentation (dispatch reliability) | TBD |
| 8a | No-brainer cycle scaffold (this work) — formula + order + 2 gates as stubs | `as-4i8` |
| 8b | No-brainer cycle runnable implementation (step bodies + decisions.jsonl writer + integration tests against [[catch-no-brainer]] fixtures) | TBD |

Numbering note: the brief's §9.1 cost table uses Phase 0-7 (8 rows);
this README collapses brief Phase 0 + Phase 1 into "Phase 1 scaffold"
(pack.toml + formula/order stubs together). Subsequent phase numbers in
this README correspond to brief Phase 2 → README Phase 2, etc.

## Privacy

`gascity-packs/` is a public repo. This pack ships only orders, formulas,
gates, and skills — no credentials, API keys, or tokens. Cross-host
heartbeat plumbing (Phase 6) references credentials by env-var name
only; never literals (per `[[never-echo-credentials]]`).

## Cross-references

- **Design source**: `he-6lz0-redesign-brief.md` (Taylor verdict A
  2026-06-25; experiment-monitoring lane); Taylor 2026-06-25 directive
  "we need to codify the no-brainer cycle with a formula" + "that is a
  bead for gascity-packs" (no-brainer-cycle lane).
- **Sibling pack in flight**: `gascity-packs/mathematics/` (bead `as-ajw`)
- **Pattern instance**:
  `[[gascity-orders-and-formulas-decomposition-pattern]]` —
  n=1 brief-pipeline; n=2 experiment-monitoring (this pack); n=3
  no-brainer-cycle (this pack). All three share the same
  formula+order+gates(+optional cooldown-sweep) shape.
- **Detection half** of the no-brainer cycle:
  `[[catch-no-brainer]]` skill in `agent-skills` repo
  (classifier; emits JSON-line verdicts; writes
  `metadata.no_brainer_verdict` on brief-beads).
- **Composes with memories**: `[[mayor-farm-out-doctrine]]`,
  `[[polecat-self-resolve-discipline]]`,
  `[[dispatcher-policy-no-infinite-loop]]`,
  `[[gate-keep-architecture]]`,
  `[[reference-bd-backup-subcommand]]`,
  `[[check-docs-before-designing-workarounds]]`,
  `[[never-echo-credentials]]`
