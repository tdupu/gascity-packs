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
- You want to **codify the mayor-questions-as-briefs policy as an
  auto-trigger** so a Mayor (or any non-Taylor agent) surfacing a
  Taylor-decidable question lands as a brief on the stack instead of
  a synchronous Taylor grill — the clerk owns Taylor-facing dialogue
  per [[grills-here-briefs-there]] + [[mayor-no-direct-grilling]].
  Pairs with the existing brief-pipeline watchdog; codification ADDS,
  watchdog stays, per [[codification-preserves-brief-pipeline]].
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
    mol-mayor-q-brief.toml             # codify mayor-questions-as-briefs auto-trigger (as-da9n; stub)
    gates/
      experiment-must-have-target.toml      # dispatch-side check formula
      experiment-must-have-clerk-route.toml # drop-off validation check formula
  orders/
    on-experiment-dropoff.toml         # event → experiment-acknowledge
    watchdog-adaptive-check.toml       # cooldown (dynamic) → experiment-check-on-it
    on-experiment-done.toml            # event → experiment-pickup
    on-experiment-health-red.toml      # event → escalate-stuck-experiment (Phase 4; stub)
    on-experiment-session-dead.toml    # event → experiment-respawn (Phase 5; stub)
    on-mayor-question.toml             # event → mol-mayor-q-brief (as-da9n; stub)
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

## Phases

This pack lands in 7 phases. **Phase 1 (this scaffold)** is the first;
subsequent phases file as sub-beads under `as-bzu`.

| Phase | Scope | Bead |
|---|---|---|
| 1 | Pack scaffold + Phase 1 TOML stubs (this work) | `as-bzu` |
| 2 | HYBRID adaptive cadence implementation in `experiment-check-on-it` | TBD |
| 3 | Experiment-clerk daemon-formula (E4c shape per §5.3) | TBD |
| 4 | Heartbeat metadata writes + `escalate-stuck-experiment` | TBD |
| 5 | Restoration drill (cron-wakeup of brainstorm A6) | TBD |
| 6 | Cross-host SSH heartbeat tunnel | TBD |
| 7 | Cross-rig instrumentation (dispatch reliability) | TBD |

Numbering note: the brief's §9.1 cost table uses Phase 0-7 (8 rows);
this README collapses brief Phase 0 + Phase 1 into "Phase 1 scaffold"
(pack.toml + formula/order stubs together). Subsequent phase numbers in
this README correspond to brief Phase 2 → README Phase 2, etc.

## Privacy

`gascity-packs/` is a public repo. This pack ships only orders, formulas,
gates, and skills — no credentials, API keys, or tokens. Cross-host
heartbeat plumbing (Phase 6) references credentials by env-var name
only; never literals (per `[[never-echo-credentials]]`).

## Mayor-questions-as-briefs auto-trigger (as-da9n)

`mol-mayor-q-brief.toml` + `on-mayor-question.toml` codify the policy
that Mayor (or any non-Taylor agent) questions to Taylor go through the
brief stack — never through real-time grilling. The clerk owns
Taylor-facing dialogue.

When an upstream emitter (Mayor `gc mail` or `gc sling` envelope tagged
for Taylor adjudication) creates a question-bead with
`metadata.mayor_question=true` and `status=ready`, the order fires the
formula. The formula:

1. **envelope-check** — gate the question text + non-redundant fire.
2. **identify-question** — extract the verbatim question text; reject
   multi-question envelopes (one question → one brief, per
   [[no-meta-sequencing-briefs]]).
3. **frame-decision-class** — categorize as exactly one of
   `merge` / `delete` / `defer` / `investigate` / `route` /
   `scope-cut` / `escalate` / `other`. Refuse open-ended brainstorms;
   surface back to Mayor for refinement.
4. **gather-context** — pull surrounding evidence (artifacts, prior
   verdicts, unlock-count) per the chosen decision-class.
5. **compose-brief** — draft the [[present-it]] 10-section structure
   citing the verbatim question.
6. **external-review-gate** — optional FP-loop via
   [[coordinate-review]] for `investigate` / `other` classes; skipped
   for mechanical adjudications.
7. **deposit-to-stack** — atomic write to
   `.beads/briefs/mayor-q-<topic>-brief.md`; refuse on collision with
   an already-pending brief on the same topic.
8. **notify-clerk** — nudge the clerk to surface; never mail Taylor
   directly per [[mayor-no-direct-grilling]].

Codification ADDS — the existing brief-pipeline watchdog stays
operational per [[codification-preserves-brief-pipeline]].
[[catch-no-brainer]] pre-classifies the deposited brief AFTER this
formula returns; the [[no-brainer-cycle]] handles no-brainer
adjudications without Taylor surface.

## Cross-references

- **Design source**: `he-6lz0-redesign-brief.md` (Taylor verdict A
  2026-06-25)
- **Sibling pack in flight**: `gascity-packs/mathematics/` (bead `as-ajw`)
- **Pattern instance**: `[[brief-pipeline-as-formulas-and-orders]]`
  (n=1, brief-pipeline domain); ops (n=2, experiment-monitoring domain;
  n=3, no-brainer-cycle; n=5, mol-brief-prep; n=6, mol-mayor-q-brief)
- **Composes with memories**: `[[mayor-farm-out-doctrine]]`,
  `[[polecat-self-resolve-discipline]]`,
  `[[dispatcher-policy-no-infinite-loop]]`,
  `[[gate-keep-architecture]]`,
  `[[reference-bd-backup-subcommand]]`,
  `[[check-docs-before-designing-workarounds]]`,
  `[[never-echo-credentials]]`,
  `[[grills-here-briefs-there]]`,
  `[[mayor-no-direct-grilling]]`,
  `[[codification-preserves-brief-pipeline]]`,
  `[[no-meta-sequencing-briefs]]`
