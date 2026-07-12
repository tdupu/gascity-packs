# Bead Types Reference (mathcity)

Reference document for the bd bead types and their intended use in the mathcity ecosystem. This is a reference, not a policy — the binding rules live in [BEADPOLICY.md](BEADPOLICY.md) (rules BP1.x–BP4.x).

## The 9 bd types

These are the only types bd supports (`bd create --help`). Aliases: `enhancement`/`feat` → `feature`; `dec`/`adr` → `decision`. Default type is `task`.

| Type | Flag | Purpose | Example use here |
|---|---|---|---|
| `task` | `bd create -t task` | Concrete unit of work with clear acceptance criteria; the default | "Add certify gate for defining-element canonicality"; ongoing math research (with `[MATH_RESEARCH]` label) |
| `feature` | `bd create -t feature` | New user-visible capability; implies a PR/merge outcome | "New intrinsic `CliffordOrderBasis` in package-LMFDB.mag" |
| `bug` | `bd create -t bug` | Defect or regression; implies root-cause + fix + test evidence | "gamma0 presentation certify fails on level 91" |
| `chore` | `bd create -t chore` | Maintenance/housekeeping, no user-visible change | "Prune dead one-off scripts from make/"; dep bumps, renames |
| `epic` | `bd create -t epic` | Large effort decomposing into multiple tasks/features; the fan-out container | "Cones-first fundamental domain pipeline" (decompose via `create-convoy` + `fan-out`) |
| `story` | `bd create -t story` | User-facing narrative ("As a … I want …"); decomposes into tasks | Rarely used here — prefer `feature` |
| `milestone` | `bd create -t milestone` | Time-bound goal aggregating epics/features | "magma_clifford_algebras public by 2026-07-15" |
| `decision` | `bd create -t decision` | Recorded adjudication: what was decided, by whom, rationale, rejected alternatives | Briefs (`brief-open`/`brief-closed`); Taylor verdicts via `record-decision` |
| `spike` | `bd create -t spike` | Time-boxed **technical** investigation; output is knowledge about the system | "Investigate why decisions/ is empty"; "check if Option Z propagates retroactively" |

## Mathematical research vs technical investigation

These are two different kinds of "research" and they must not be conflated. A **mathematical research bead** is original mathematical work — exploring a theorem, deriving a formula, proving a conjecture, working through examples. Its output is NEW MATHEMATICS. It is never time-boxed (it can take months), and it is never "investigating technical uncertainty" — it IS the work. Mathematical research beads are **never** `type: spike`. Ongoing math research is `type: task` or `type: feature` with the `[MATH_RESEARCH]` label. When the work completes and the result is a permanent reference, the bead gets the `[RESEARCH_JOURNAL]` label plus `bd defer` protection so it can never be destructively closed (brief-system rule B3.7; BEADPOLICY BP2.x).

A **technical investigation (deep-research) bead** investigates a technical question about code, infrastructure, or system state — "why does this fail?", "what does this function do?", "is this approach feasible?". Its output is KNOWLEDGE ABOUT THE SYSTEM, not new mathematics. This IS a `type: spike` bead: time-boxed, produces a finding, and leads to further work. Examples: "investigate why decisions/ is empty", "research what bd types are available", "check if Option Z propagates retroactively". Rule of thumb: if the deliverable would go in a math paper, it is math research (task/feature); if the deliverable is a finding about the system that unblocks other work, it is a spike.

## Labels

| Label | Applies to | Meaning |
|---|---|---|
| `[MATH_RESEARCH]` | `task`/`feature` beads | Ongoing original mathematical work. Not time-boxed; excluded from staleness reaping; never retyped to `spike`. |
| `[RESEARCH_JOURNAL]` | Completed research-reference beads | Permanent reference content. Protected by B3.7: never `bd close`; interim ARCHIVED protocol is label + `bd defer <id> --reason="research journal — ARCHIVED-equivalent, do not close"`. Batch-closing skills must exclude this label. |
| `brief-open` | `decision` beads | A brief pending adjudication in the brief pipeline. |
| `brief-closed` | `decision` beads | An adjudicated brief. Immutable; never reopened — follow-up work is a new bead. |

Briefs are always `type: decision`; the `record-decision` skill creates them and records Taylor's verdicts.

## Memory quick-reference

Memories are for persistent knowledge (facts, design insights, debugging discoveries, agent identity) — NOT for task state or TODO lists (those are beads). Memories survive session death and are injected at `bd prime` time.

```bash
bd remember --key <slug> "<content>"   # store (reusing a key updates in place)
bd recall <key>                        # retrieve one memory by key
bd memories <keyword>                  # search memories
bd list -t decision                    # adjudication history (decisions are beads, not memories)
```

## Full rules

See [BEADPOLICY.md](BEADPOLICY.md) for the binding policy: type selection (BP1.x), research bead protection (BP2.x), memory policy (BP3.x), and old/stale bead removal (BP4.x).
