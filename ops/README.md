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
- You want **bounded fixed-point convergence machinery** for an
  artifact-shaping skill (e.g. `coordinate-review`, `fp-finder-skill`)
  — monotone shrink-OR-split + quality floor + cap=10 + wall-time
  gate — as a reusable formula instead of in-skill logic
  (`meta-fp-cycle`).
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
    meta-fp-cycle.toml                 # per-iteration META-FP convergence check (Phase 8d; stub)
    gates/
      experiment-must-have-target.toml         # dispatch-side check formula
      experiment-must-have-clerk-route.toml    # drop-off validation check formula
      iteration-must-shrink-or-split.toml      # meta-fp-cycle math gate (as-bb5)
      iteration-must-be-approving.toml         # meta-fp-cycle quality floor (as-bb5)
      as-wjv-dispatch-gate.toml                # SAFETY OVERRIDE on SKILL.md dispatch (Phase 1; stub)
  orders/
    on-experiment-dropoff.toml         # event → experiment-acknowledge
    watchdog-adaptive-check.toml       # cooldown (dynamic) → experiment-check-on-it
    on-experiment-done.toml            # event → experiment-pickup
    on-experiment-health-red.toml      # event → escalate-stuck-experiment (Phase 4; stub)
    on-experiment-session-dead.toml    # event → experiment-respawn (Phase 5; stub)
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

### META-FP convergence framework

The pack hosts a **reusable bounded fixed-point convergence framework**
for artifact-shaping skills. Lifted from `[[as-bb5]]`'s `fp-finder-skill`
SKILL.md design (CLOSED) into a TOML formula so multiple skills
(`coordinate-review`, `fp-finder-skill`, future siblings) share the
convergence machinery instead of each re-implementing it.

The framework is **two convergence guarantees**:

1. **Mathematical** — per-skill char-count strictly decreases each
   accepted iteration (or the iteration factors a chunk into a sibling
   artifact). Char-count is bounded below by 0; bounded-monotone →
   convergent. Gate: `iteration-must-shrink-or-split`.

2. **Defense-in-depth** — cap=10 rounds (per Taylor 2026-06-25 verdict
   on `as-h7r`: "Let's do cap=10. Then I agree with the brief.")
   PLUS a 15-minute wall-time gate. The cap is belt-and-brace on top
   of the math guarantee; a cap-hit is a SIGNAL that the artifact +
   gates need tuning.

Plus a **quality floor** — revision wins ONLY if shorter AND
`APPROVING` per critical-review. Prevents trivial-deletion gaming.
Gate: `iteration-must-be-approving`.

The formula `meta-fp-cycle.toml` is called per iteration by the
artifact-shaping skill; it returns one of `ACCEPT_REVISION`,
`SPLIT_INTO_SIBLING`, `TERMINATE_CONVERGED`, `TERMINATE_CAP`, or
`REJECT_AND_RETRY` (full schema in the formula's description block).
The skill loops on the verdict, not on its own counter — defense-in-
depth against a skill that "forgets" to check.

First consumer: `coordinate-review` SKILL.md (agent-skills); install
gated by Taylor approval per `[[as-wjv]]` SAFETY OVERRIDE policy
(sub-bead `as-gz0n`).

### as-wjv-dispatch-gate (SAFETY OVERRIDE on SKILL.md dispatch)

Codification of `[[as-wjv]]` — Taylor's standing directive that any
edit to a SKILL.md or agent-prompt artifact requires explicit
per-session greenlight. The gate fires synchronously on dispatch:
BLOCK if any path in the envelope matches the 5 SKILL.md / agent-prompt
prefixes (`agent_skills/skills/**/SKILL.md`,
`~/.claude/skills/**/SKILL.md`, `gascity-packs/**/agents/*.md`,
`.claude/commands/**`, `CLAUDE.md`) AND no `GC_TAYLOR_GREENLIGHT` is
set in the current session; otherwise ALLOW.

Every BLOCK and ALLOW_WITH_OVERRIDE writes a JSON-line audit record
to `~/gt/<rig>/.beads/decisions.jsonl`. Per
`[[never-echo-credentials]]`: the audit record logs paths + the
greenlight token only, NEVER the file contents or diff hunks.

Gate (not formula) — single-pass, exits 0 (ALLOW) or 1 (BLOCK). The
calling dispatch substrate owns the consequence: typically halting the
flow and surfacing the greenlight request to Taylor via
`mol-mayor-q-brief` (sibling 2/4, bead `as-da9n`).

This is the **heavy gate** in the
`[[gate-keep-architecture]]` X-policy / X-gate / improve-X trinity.
The advisory pre-flight is `mol-pre-action-checklist` check 6
(sibling 4/4, bead `as-ktkx`).

## Phases

This pack lands in 8+ phases across two lanes (experiment-monitoring +
no-brainer-cycle + META-FP convergence). **Phase 1 (this scaffold)**
is the first; subsequent phases file as sub-beads under the
appropriate parent.

| Phase | Scope | Bead |
|---|---|---|
| 1 | Pack scaffold + Phase 1 TOML stubs (this work) | `as-bzu` |
| 2 | HYBRID adaptive cadence implementation in `experiment-check-on-it` | TBD |
| 3 | Experiment-clerk daemon-formula (E4c shape per §5.3) | TBD |
| 4 | Heartbeat metadata writes + `escalate-stuck-experiment` | TBD |
| 5 | Restoration drill (cron-wakeup of brainstorm A6) | TBD |
| 6 | Cross-host SSH heartbeat tunnel | TBD |
| 7 | Cross-rig instrumentation (dispatch reliability) | TBD |
| 8a | No-brainer cycle scaffold (formula + order + 2 gates as stubs) | `as-4i8` |
| 8b | No-brainer cycle runnable implementation (step bodies + decisions.jsonl writer + integration tests against `[[catch-no-brainer]]` fixtures) | TBD |
| 8c | META-FP convergence framework scaffold (this work; formula + 2 gates as stubs) | `as-2h0` |
| 8d | META-FP runnable implementation (step bodies + integration tests against `coordinate-review` iteration logs) | TBD |
| 9a | Policy-conversion lane scaffolds (4 sibling formulas as stubs: dispatch-gate, mayor-q-brief, never-echo-credentials-lint, pre-action-checklist) | `as-oat3` / `as-da9n` / `as-82ty` / `as-ktkx` |
| 9b | Policy-conversion runnable implementation (per-formula Phase 2 / 3 bodies + integration tests against memory references) | TBD |

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
  "we need to codify the no-brainer cycle with a formula" (no-brainer
  cycle lane); Taylor 2026-06-25 verdict on `as-h7r` "Let's do cap=10.
  Then I agree with the brief." (META-FP lane).
- **Sibling pack in flight**: `gascity-packs/mathematics/` (bead `as-ajw`)
- **Pattern instance**:
  `[[gascity-orders-and-formulas-decomposition-pattern]]` —
  n=1 brief-pipeline; n=2 experiment-monitoring (this pack); n=3
  no-brainer-cycle + META-FP convergence (this pack). All share the
  same formula+order+gates(+optional cooldown-sweep) shape.
- **Detection half** of the no-brainer cycle:
  `[[catch-no-brainer]]` skill in `agent-skills` repo (classifier).
- **First consumer of META-FP**: `coordinate-review` SKILL.md in
  `agent-skills` repo; install gated by Taylor approval per
  `[[as-wjv]]` policy (sub-bead `as-gz0n`).
- **Composes with memories**: `[[mayor-farm-out-doctrine]]`,
  `[[polecat-self-resolve-discipline]]`,
  `[[dispatcher-policy-no-infinite-loop]]`,
  `[[gate-keep-architecture]]`,
  `[[reference-bd-backup-subcommand]]`,
  `[[check-docs-before-designing-workarounds]]`,
  `[[codification-preserves-brief-pipeline]]`,
  `[[as-wjv]]`,
  `[[never-echo-credentials]]`
