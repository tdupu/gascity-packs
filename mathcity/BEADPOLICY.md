# Mathcity Bead Policy

| Field | Value |
| --- | --- |
| Status | Draft |
| Date | 2026-07-12 |
| Decided | Taylor Dupuy |
| Applies to | All bead creation, typing, labeling, memory use, and bead removal in the mathcity ecosystem (all rigs, all agents) |
| Consumers | `record-decision`, `gc-recycle-bead`, `remember-this`, `brief-prep`, `create-convoy`, `fan-out`, any sweeper/reaper skill, Mayor dispatch |

Governs how beads are typed, how research beads are protected, when knowledge goes into `bd remember` versus a bead, and when an old bead may be removed. Companion reference (non-normative): [README-beads.md](README-beads.md). On conflict with POLICY-POLICY.md, POLICY-POLICY.md wins.

Rule prefix: **BP** (pending reservation in `mathcity/docs/rule-prefix-registry.md` per PP5.2 — see Change Log).

---

## Core definitions

- **Mathematical research bead.** A bead whose work product is NEW MATHEMATICS — exploring a theorem, deriving a formula, proving a conjecture, working through examples. Not time-boxed; may run for months. This is never "investigating technical uncertainty" — it IS the work.
- **Technical investigation (deep-research) bead.** A bead whose work product is KNOWLEDGE ABOUT THE SYSTEM — "why does this fail?", "what does this function do?", "is this approach feasible?". Time-boxed, produces a finding, leads to further work.
- **Old useless bead.** A bead meeting one of the BP4.2 removal criteria and none of the BP4.4 protections.
- **Reaper sweep.** A batch pass that closes old useless beads under the BP4.3 protocol.

---

## Pillar 1 — Bead type selection (BP1.x)

- **BP1.1 Only documented bd types are used.** The canonical set is exactly what `bd create --help` documents: `bug`, `feature`, `task`, `epic`, `chore`, `decision`, `spike`, `story`, `milestone`. No invented types (e.g., `research-journal`) may appear in beads, policy prose, or skill code (cross-ref: dev policy P5.3).
- **BP1.2 task/feature/bug are the standard work types.** `task` is the default for concrete implementation work with acceptance criteria; `feature` for new user-visible capability (implies a PR/merge outcome); `bug` for defects and regressions (implies root-cause + fix, test evidence before close).
- **BP1.3 spike = technical investigation ONLY.** A `spike` bead investigates a technical question about code, infrastructure, or system state. It is time-boxed, produces a finding (in bead notes or a follow-up bead), and leads to further work. Examples: "investigate why decisions/ is empty", "research what bd types are available", "check if Option Z propagates retroactively".
- **BP1.4 Mathematical research is NEVER a spike.** Original mathematical work (theorem exploration, formula derivation, proof work, example computation) is `type: task` or `type: feature` carrying the `[MATH_RESEARCH]` label while ongoing. Mathematical research is not time-boxed and its output is new mathematics, not system knowledge. Typing math research as `spike` is a BP1.4 violation. See Pillar 2 for the completed-research lifecycle.
- **BP1.5 decision = briefs and adjudications.** Briefs are `type: decision` labeled `brief-open` (pending) or `brief-closed` (adjudicated). Recorded adjudications, policy locks, and verdicts are `type: decision` created via `record-decision`. Decision beads are never reopened; follow-up is a new bead (cross-ref: brief-system B2.2, B3.8).
- **BP1.6 epic = grouped work; decompose via convoy.** A large effort spanning multiple tasks/features is an `epic`, decomposed with `create-convoy` + `fan-out`. An epic closes only when all members are terminal (cross-ref: B3.5).
- **BP1.7 chore = maintenance.** Housekeeping with no user-visible change (renames, dep bumps, dead-code pruning). Low-ceremony; usually no brief needed.
- **BP1.8 milestone = release/date markers.** Time-bound goals aggregating epics and features: release markers, conference-deadline targets (e.g., the July 15 public-release target).
- **BP1.9 story is discouraged.** Agile user stories are rarely the right shape here; prefer `feature`. `story` remains legal (it is a documented type) but a new `story` bead should justify why `feature` does not fit.

---

## Pillar 2 — Research bead protection (BP2.x)

- **BP2.1 Ongoing mathematical research carries `[MATH_RESEARCH]`.** Any bead whose work is original mathematics in progress is `type: task` or `type: feature` with the `[MATH_RESEARCH]` label. The label signals: not time-boxed, not eligible for staleness-based reaping (BP4.4), and never reclassifiable to `spike` (BP1.4).
- **BP2.2 Completed reference mathematics becomes a research journal.** When a `[MATH_RESEARCH]` bead completes and its content is a permanent mathematical reference, it transitions to the research-journal state: add the `[RESEARCH_JOURNAL]` label and protect with `bd defer <id> --reason="research journal — ARCHIVED-equivalent, do not close"`. This is the interim ARCHIVED protocol of brief-system B3.7; B3.7's mechanical protections (no `bd close`, sweeper exclusion) apply in full.
- **BP2.3 `[RESEARCH_JOURNAL]` beads are never closed destructively.** Restatement of B3.7 for this domain: any `bd close` targeting a bead labeled `[RESEARCH_JOURNAL]` is a policy violation; batch-closing skills (sweepers, convoy landers, no-brainer executors, the BP4.3 reaper) must exclude beads carrying this label.
- **BP2.4 B3.7's spike-typing step does not apply to mathematical research.** B3.7(a) ("ensure the bead is `type: spike`") was written for investigation-output journals and predates the math-research/tech-investigation distinction. For mathematical research journals, retain `type: task`/`feature` + `[RESEARCH_JOURNAL]` + defer; do NOT retype to `spike`. Technical-investigation journals (spike output worth keeping permanently) remain `type: spike` + `[RESEARCH_JOURNAL]` + defer as B3.7 specifies. (Flagged for reconciliation in the brief-system policy via `new-brief-policy`.)
- **BP2.5 Spike findings that matter get durable homes.** A closed spike's finding must land somewhere durable before close: bead notes on the spike, a follow-up work bead, or a `bd remember` entry when the finding is a persistent fact (Pillar 3). A spike closed with no recorded finding is a BP2.5 violation.

---

## Pillar 3 — Memory policy (BP3.x)

- **BP3.1 Memories are for persistent knowledge, not task state.** Use `bd remember --key <slug> "<content>"` for: persistent facts, design insights, hard-won debugging discoveries, agent identity info. Do NOT use memories for: ephemeral task state, TODO lists, or anything that belongs in a bead's description/notes. Task tracking lives in beads; knowledge that must survive session death lives in memories.
- **BP3.2 The retrieval contract.** Memories are injected at `bd prime` time and retrieved via `bd recall <key>` (exact key) or `bd memories <keyword>` (search). Adjudications are NOT memories — they are decision beads, retrieved via `bd list -t decision`. A fact stored only in a session transcript or a scratch file has not been remembered.
- **BP3.3 Keys are stable slugs.** Memories use explicit `--key` slugs (kebab-case) so `bd recall` is deterministic. Updating a memory reuses its key (in-place update) rather than creating a near-duplicate under a new key.
- **BP3.4 Bead-vs-memory routing.** If the content is actionable (someone should DO something) → bead. If the content is a fact/insight future sessions need (someone should KNOW something) → memory. If it is an adjudication (someone DECIDED something) → decision bead via `record-decision`. The `remember-this` skill implements this routing and is the preferred entry point.

---

## Pillar 4 — Old/stale bead removal (BP4.x)

- **BP4.1 Removal means close-with-reason, never delete.** Reaping an old useless bead is a `bd close` with an explicit reason naming the BP4.2 criterion met. Bead deletion (`bd delete`) is reserved for accidental creations within the same session; history is otherwise preserved.
- **BP4.2 Definition of an old useless bead.** A bead is old-useless iff it meets at least ONE of:
  - **(a) Orphaned step bead** from an old build-basic run: titled "Finalize workflow", "Write implementation plan", "Create task beads", "Step spec for...", or similar convoy-remnant boilerplate, with no active parent convoy and no actionable acceptance criteria.
  - **(b) Superseded bead**: explicitly marked superseded by a newer bead, or whose scope was demonstrably absorbed into another bead (close reason must name the absorbing bead ID).
  - **(c) Duplicate bead**: verbatim or near-verbatim title+description duplicate of another OPEN bead (close reason names the surviving bead ID).
  - **(d) Ghost bead**: no title, no description, no assignee, no dependencies, and creation date more than 60 days ago.
- **BP4.3 The reaper sweep protocol.** A reaper sweep (manual or skill-driven) proceeds: (1) enumerate candidates per BP4.2; (2) filter out every BP4.4 protection; (3) close each survivor with a reason citing the criterion and any cross-referenced bead ID; (4) report the reaped list — IDs, titles, criteria — in the session handoff. Sweeps never run silently.
- **BP4.4 What can never be reaped.** The following are excluded from any sweep regardless of age or appearance:
  - **(a)** Beads labeled `[RESEARCH_JOURNAL]` or `[MATH_RESEARCH]` (B3.7, BP2.x).
  - **(b)** BLOCKED beads — they may be waiting on something real; a blocked bead is triaged, not reaped.
  - **(c)** Any bead Taylor has personally touched, claimed, or commented on.
  - **(d)** Decision beads (`type: decision`) — adjudication history is permanent (B2.2).
- **BP4.5 Doubt defers.** If a sweep cannot mechanically establish a BP4.2 criterion (e.g., "is this really superseded?"), the bead is left open and surfaced to Taylor with a **defer** verdict rather than closed.

---

## Verdict vocabulary (shared, per POLICY-POLICY)

| Verdict | Meaning |
| --- | --- |
| **approve** | Current state is compliant; no action required |
| **revise** | Drift found; each item listed with the rule violated and one-line remediation |
| **defer** | A human call is needed; the open question is stated explicitly |

A future `check-bead-policy` skill never emits **reject** (reject applies only to artifacts, not to audits of running state).

---

## Change Log

| Date | Change | Rationale |
| --- | --- | --- |
| 2026-07-12 | Initial draft (BP1–BP4) | Taylor decree: distinguish mathematical research from technical investigation; codify memory routing and old-bead reaping. NOTE: `mathcity/docs/rule-prefix-registry.md` does not yet exist, so the BP prefix is provisionally claimed here pending registry creation (PP5.2). BP2.4 flags a needed B3.7 amendment via `new-brief-policy`. Trinity incomplete: `check-bead-policy` / `new-bead-policy` skills not yet scaffolded (PP1.1). |
