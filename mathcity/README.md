# mathcity

**local mathematical work pack.** Codifies the brief pipeline — formulas, orders, gate policy, and skills — that routes math research decisions (branches, PRs, experiments) from artifact to adjudication.

## Links

- Gas City platform: https://github.com/gastownhall/gascity
- Beads issue tracker docs: https://gastownhall.github.io/beads/

---

## What is the brief system

The brief system is a structured decision pipeline for math research work. When an agent completes a branch, closes a bead, or proposes an experiment, it does not automatically merge or act. Instead it produces a brief — a formatted document that describes the artifact, the work done, the gate evidence, and a clear statement of what decision is needed. Briefs are the unit of work that flows between automated agents and human user.

The pipeline has two main phases. In the production phase, `brief-prep` (a skill that composes `grill-and-present`, `coordinate-review`, and the gate runner) prepares the brief from the source artifact, runs all required gates, and deposits the result into the `.pile` at `~/.gc/mathcity/briefs/.pile/`. The `brief-shuffle-pile` order fires on condition, picks up pile items one at a time, applies gate-keep rules, and either promotes each brief to the `~/.gc/mathcity/briefs/stack/` with a manifest entry or rejects it to `.pile/.rejected/`.

In the adjudication phase, `brief-present-next` drains the stack and presents briefs to human. No-brainer-classified briefs are collapsed into a single one-line block; full briefs are rendered through `grill-and-present`. human adjudicates — approve, reject, defer, or revise. `brief-record-decision` records the verdict as a `bd decision` record. Then two event-driven orders fire on `brief.decided`: `brief-decision-dispatch` acts on the decision (merges the branch, creates a follow-up bead, or marks defer), and `post-decision-file-or-sendback` routes the brief itself to either a successor re-briefing or archive. The `brief-archive-sweep` cooldown order handles residual cleanup.

---

## Skill canonicality

**The mathematics pack is the single source of truth for all brief-pipeline and math-workflow skills.**

- `~/repos/gascity-packs/mathcity/skills/<name>/SKILL.md` is the canonical file.
- `~/repos/agent-skills/skills/<name>` is a relative symlink into the pack — it exists only so plain-session Claude Code agents (using `~/.claude/skills/`) can load these skills without a running city.
- **Edits always land as commits to `gascity-packs` (fork `tdupu/gascity-packs`).** Never edit the agent-skills side of the symlink; it points back here.
- **New brief-pipeline or math skills are created inside `mathcity/skills/<name>/` first**, then symlinked into `~/repos/agent-skills/skills/<name>` with `ln -s ../../gascity-packs/mathcity/skills/<name> <name>` (relative, from inside `agent-skills/skills/`). The symlink is committed to agent-skills.
- Run `~/repos/agent-skills/scripts/check-skill-symlinks.sh` to verify all symlinks resolve and every skill dir contains `SKILL.md`.

Skills currently managed under this policy (all 11 as of 2026-07-07):
`brief-prep`, `catch-no-brainer`, `coordinate-review`, `critical-review`,
`formula-creator`, `grill-and-present`, `is-good-experiment`, `is-good-test`,
`present-briefs`, `present-it`, `record-decision`.

---

## Skills

These skills ship with the parent pack (subdomain child packs carry their own — see `subdomains/*/README.md`). They are bare `SKILL.md` composition units — no wrapper scripts. The `grill-with-docs` and its derivatives are based off [Matt Popocock's Skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs). Most of the skill formulas and plans were developed using a ``fixed point finder'' where artifacts (in this case the skill) goes through a comprehensive review until the agents converge on the skill. (The fixed point finder is now deprecated in favor of the gascity native version.)

| Skill | Description |
|---|---|
| `brief-prep` | End-to-end brief production: turns an artifact (branch, bead, PR, diff) into a stack-eligible brief with all gates satisfied and bookkeeping recorded. Branches on no-brainer classification to compact or full-form output. |
| `catch-no-brainer` | Classifies a brief against the 5-criterion no-brainer test and signals compact-form eligibility to downstream consumers. Records candidates; never auto-merges or closes beads. |
| `coordinate-review` | Iterative create/review loop: spawns `critical-review` and `revise-artifact` subagents in alternation until an artifact converges to approved state under the META-FP formula. |
| `critical-review` | Adversarial reviewer for any artifact (SKILL.md, plan, theorem, LaTeX, code). Produces a structured APPROVING or NEEDS-REVISION verdict with prioritized action items. |
| `grill-and-present` | Produces decision-ready briefs by gathering all 10 present-it sections, grilling on ambiguity, running tests, and FP-converging the brief through `critical-review` before presenting. |
| `is-good-experiment` | Pre-flight check for experiment proposals. Decides whether a computation or research probe is well-designed before any compute is spent running it. |
| `is-good-test` | Thin specialization of `is-good-experiment` for test files. Evaluates whether a test's design answers "does X work?" meaningfully. |
| `present-it` | Produces a decision-ready brief on a code artifact. Enforces the Decision-at-Top invariant. Supports full-form and compact form outputs. |
| `record-decision` | Records human adjudications, policy locks, and brief-pipeline verdicts using `bd create -t decision`. Refuses non-canonical stores. |
| `present-briefs` | Batch-presents N briefs in parallel and keeps a hot queue (≥2 pre-presented) with auto-backfill on each decision. |
| `create-brief` | Produces the durable, gated `.md` brief artifact for the brief stack — the file-artifact sibling of `present-it`. |
| `create-artifact` | Creator half of the review loop: produces a new artifact from a spec (dispatched by `coordinate-review` or directly). |
| `revise-artifact` | Applies a list of action items (typically from `critical-review`) to an artifact and outputs the revised version. |
| `compare-artifacts` | Semantic diff between two text artifacts: similarity score + token-overlap signal for "are these effectively the same?" |
| `fp-finder-skill` | Fixed-point convergence engine for SKILL.md files: every accepted revision must be strictly shorter AND still APPROVING. |
| `formula-creator` | Creates a formula TOML in any gascity-packs pack and validates the gc/bd command surface before committing. |
| `create-convoy` | Creates a properly configured OWNED convoy for an epic bead — the fan-out container for one WIP-dispatcher slot. |
| `fan-out` | Fans an epic bead out into convoy sub-beads without consuming extra WIP-dispatcher slots; companion of `create-convoy`. |
| `immediate-work` | In-session synchronous dispatch: spawn the right agent NOW for a specific bead or task (no pool, no queue). |
| `priority-work` | Async targeted dispatch: bump a bead to P0 and dispatch it to a NAMED agent immediately, bypassing queue order. |
| `mayor-math` | Supplements `gc.mayor` with rig-scoped sling mechanics for the mathcity workflow. |
| `authorize-git-operation` | Taylor-authorization gate for irreversible git operations (push, merge, PR, delete, release); records the verdict as a decision bead. |
| `remember-this` | Routes a mid-session insight to the right durable store (`bd remember`, decision bead, MEMORY.md pointer). |
| `gc-recycle-bead` | Graceful lifecycle transitions for research beads: ABSORB (merge unique content into canonical bead, close with `absorbed_by` metadata), ARCHIVE (add `archived-research` label + defer to prevent dispatch), MATERIALIZE (write key content to versioned file). |
| `prime-outsider` | Primes an outside (non-gascity) agent after compaction or a new session: finds beads + handoff, restates standing rules. |
| `repo-to-city` | Reference map from repository names to city rig (`~/gt/<name>`), working copy (`~/repos/<name>`), and beads prefix. |
| `dolt-init` | Initializes the bd Dolt database and sets the dolt remote in both `~/gt/<repo>` and `~/repos/<repo>` (HALTs unless the remote is named `<repo>-dolt`). |
| `dolt-pull` / `dolt-push` | Pull/push the bead database against its private `-dolt` remote (data plane; bans force-push). |
| `get-best-apis` | Fetches live LLM benchmark rankings + current API pricing across vendors and renders a comparison table. |
| `get-best-models` | Recommends the best open-weights/local LLM for a hardware constraint and use case. |
| `gate-test-execution-silent` | G14 gate — pure PASS/FAIL check: verifies that a brief carries a non-silent test-execution tri-state declaration (`test-execution: PASSED/NOT APPLICABLE/REQUIRED`) and, when PASSED is claimed, that §5 contains command + exit code + wall time evidence. Auto-throwback gate; no Taylor adjudication. |
| `improve-test-execution-silent` | G14 improve step — auto-repair companion to `gate-test-execution-silent`. Adds `test-execution: REQUIRED — not yet run` when the brief is silent (Case A); emits ESCALATE when evidence is incomplete (Case B). Identity on passing input. |

---

## Formulas

Formulas are the executable units the order system pours. Each is a `.toml` in `formulas/`.

| Formula | What it does |
|---|---|
| `brief-archive-sweep` | Sweeps old rejected and decided brief artifacts into archive state via deterministic file moves. Runs as phase=vapor (no LLM turn per step). |
| `brief-decision-dispatch` | For each undispatched decision record, executes the routing action: reassign source bead on approve, create follow-up bead on reject/revise, mark-only on defer. |
| `brief-gate-keep` | Runs the gate registry against one brief. Mechanical gates checked by scripts; judgment gates as explicit work steps; stop/manual gates fail closed unless evidence records human authorization. |
| `brief-prep` | Producer side of the brief-bundle workflow. Turns a bead, artifact, or user request into a staged brief with gate evidence attached, then submits to the pile. |
| `brief-present-next` | Drains all pending stack briefs in one session. No-brainers are collapsed into one-line items; full briefs are rendered via `grill-and-present`. |
| `brief-record-decision` | Records human's decision for a presented brief and archives the run. |
| `brief-shuffle` | Single-writer shuffler: processes at most one pile item per run, applies gate-keep, and either promotes to stack (with manifest append) or rejects to `.pile/.rejected/`. |
| `brief-watchdog-refill` | Monitors the brief stack; when below target, identifies ready source work and opens or routes brief-prep work. Does not fabricate briefs. |
| `codex-dispatch` | Dispatches a task to the codex-worker for cross-model critical review, creative design, or large-plan analysis. Never fired by automated orders — pour explicitly only. |
| `file-or-sendback-route` | Post-decision gate: logs the routing choice for a decided brief and fires downstream work — FILE (re-brief a successor) vs SEND-BACK (archive). Never reassigns or merges. |
| `no-brainer-classify` | Classifies no-brainer candidates and records results. Shortcut execution is blocked unless the local kill switch file exists and all stop gates are clear. |
| `on-merge-brief-record` | Inspects recently closed beads; for those carrying the `needs-decision` label, creates a brief-record bead and enters the brief-prep pipeline. |
| `test-execution-request` | Formal request workflow for test execution that carries risk or cost and should not happen silently. |
| `upf-experiment-dispatch` | Dispatches and breadcrumbs an experiment that belongs on UPF (the compute rig). |

---

## Orders

Orders wire formulas to triggers. Nine orders are registered in `orders/`.

| Order | Trigger | Description |
|---|---|---|
| `brief-archive-on-request` | event (`brief.archive_requested`) | Archives a sent-back brief immediately when routing requests it, without waiting for the 24h sweep. |
| `brief-archive-sweep` | cooldown 24h | Archives decided and rejected brief artifacts without deleting decision records. |
| `brief-decision-dispatch` | event (`brief.decided`) | Dispatches the approval/merge back-edge after a brief decision is recorded. |
| `brief-present-next` | manual | Drains all pending stack briefs: no-brainers as one-line items, full briefs via `grill-and-present`. Pool: mayor. |
| `brief-shuffle-pile` | condition | Fires whenever `~/.gc/mathcity/briefs/.pile/` contains at least one `.md` file. Promotes or rejects one brief per run. Pool: gastown.dog. |
| `brief-watchdog-refill` | cooldown 30m | Checks whether the brief stack needs refill work and routes brief-prep tasks. |
| `no-brainer-process` | manual | Manually classifies one no-brainer candidate under the shortcut policy. |
| `on-merge-brief-record` | event (`bead.closed`) | Files a brief-record after the refinery closes a bead carrying `needs-decision`. Rig-scoped because work beads are rig-local. |
| `post-decision-file-or-sendback` | event (`brief.decided`) | Routes the decided brief: FILE (re-brief a successor bead) or SEND-BACK (archive). Never reassigns or merges. |

---

## Agents

### codex-worker

Located at `agents/codex-worker/agent.toml`. A simple Codex worker scoped to the rig, using the `codex` provider with `fallback = true` and `permission_mode = "suggest"`. It is the execution target for `codex-dispatch` pours — used when an independent cross-model perspective is needed on a design decision, a prior agent attempt has failed, or a large-plan analysis warrants a second opinion before committing. It is never fired automatically; all dispatches are explicit.

---

## 16-Gate system

Every brief is evaluated against a registry of 16 gates before it can be promoted from the pile to the stack. This system was made autonomously after initially recieving many reviews. As the user approved decisions one has to classify them as "no-brainers". Every 10 new "no-brainers" sparks a review of the gate process so that the no-brainer reviews are caught and immediately processed. This allows us to cut down on the number of briefs we have to read. 

Gates have developed into four kinds (so far):

- **mechanical** — checked deterministically by script; no judgment required.
- **review** — requires an agent or human reviewer to evaluate evidence.
- **stop** — fails closed unconditionally unless explicit human authorization is recorded in the evidence.
- **manual** — requires a human outcome or explicit N/A.

`fail_closed = true` is set at the registry level, meaning any missing or failing gate blocks promotion.

| Gate | Name | Kind | Brief description |
|---|---|---|---|
| G1 | test-evidence | mechanical | Test claims must include exact command, scope, result, and date — or explicit N/A with surface-check evidence. |
| G2 | good-test | review | A reviewer must judge whether the test evidence meaningfully tests the claimed behavior. |
| G3 | shell-scripts-testable | mechanical | Shell-script changes must name runnable validation or state why no script surface is touched. |
| G4 | critical-review | review | A critical-review pass must look for correctness risks, policy misses, and missing evidence. |
| G5 | server-touching-exclusion | stop | Server-touching work cannot pass the shortcut path without explicit human authorization. |
| G5b | user-skill-touching-exclusion | stop | User skill changes cannot pass shortcut automation without explicit human authorization. |
| G6 | latex-gate | manual | LaTeX-bearing work needs the LaTeX gate outcome or an explicit no-LaTeX surface check. |
| G7 | artifacts-staging | mechanical | Artifacts must be staged under the brief run directory and referenced from the brief. |
| G8 | brief-record-bookkeeping | mechanical | Pile, stack, manifest, and decision/archive records must remain consistent. |
| G9 | no-brainer-filter | review | Shortcut classification must be explicit and cannot override stop gates or human-only decisions. |
| G10 | improve-readme | mechanical | Each qualifying iteration must show the README improvement or explain why no README surface exists. |
| G11 | breadcrumb | mechanical | Experiment or deferred work must leave a durable breadcrumb to the source, artifacts, and next owner. |
| G12 | auto-merge-kill-switch | stop | Automation must fail closed unless the local kill switch (`ALLOW_NO_BRAINER_AUTO_EXECUTE`) explicitly permits the shortcut. |
| G13 | stale-claim | mechanical | Briefs must not rely on stale claims; claim freshness or revalidation must be recorded. |
| G14 | test-execution-silent | mechanical | Risky or high-cost test execution must be requested explicitly rather than silently run. |
| G15 | improve-readme-silent | mechanical | A missing README improvement cannot be silent; the brief must record applied or N/A evidence. |
| G16 | master-current-for-test-evidence | mechanical | Test evidence depending on main/master state must record the base ref used. |

### Gate profiles

Different brief types apply different gate subsets. The default profile is `standard`.

| Profile | Gates applied |
|---|---|
| `standard` | All 16 gates (G1–G16) |
| `no_brainer` | G1, G5, G5b, G7, G8, G9, G12, G13, G14, G16 |
| `test_execution` | G1, G2, G4, G8, G13, G14, G16 |
| `experiment` | G1, G2, G4, G7, G8, G11, G13, G16 |

The `no_brainer` profile skips review and README gates because no-brainer briefs are mechanical and time-constrained. The `experiment` profile requires the breadcrumb gate (G11) since experiments produce artifacts that must be traceable. Stop gates G5 and G5b are enforced only on `standard` and `no_brainer` profiles because those are the paths where automation might otherwise short-circuit human review.

---

## End-to-end workflow

A single brief cycle from artifact to decision proceeds as follows.

1. **Artifact exists.** A branch is merged, a bead is closed with the `needs-decision` label, or human directs `brief-prep <artifact>` explicitly. This produces or identifies the source artifact.

2. **brief-prep fires.** The `brief-prep` skill (or the `on-merge-brief-record` order + formula chain) runs. It calls `grill-and-present` to gather all 10 brief sections, grills on ambiguity, runs tests, FP-converges the brief through `coordinate-review`, and checks `catch-no-brainer` to determine output shape (compact or full-form).

3. **Brief lands in .pile.** The finished brief markdown is written to `~/.gc/mathcity/briefs/.pile/<run-id>/brief.md` with gate evidence in `evidence.toml`. The `brief-shuffle-pile` order's condition check (`find ~/.gc/mathcity/briefs/.pile -name '*.md'`) becomes true.

4. **brief-shuffle promotes or rejects.** The single-writer shuffler picks up the pile item, runs `brief-gate-keep` against the gate registry, and either promotes the brief to `~/.gc/mathcity/briefs/stack/` (appending to `manifest.jsonl`) or rejects it to `.pile/.rejected/` with a reason.

5. **brief-present-next drains the stack.** human or the mayor triggers this manual order. All pending stack briefs are presented. No-brainer-classified briefs appear as a single collapsed block; full briefs are rendered one at a time through `present-it`. The Decision-at-Top invariant ensures the first content human sees is what is being decided.

6. **human adjudicates.** human issues a verdict: approve, reject, defer, or revise. The `record-decision` skill (via `brief-record-decision`) writes the decision as a `bd decision` record and rings the `brief.decided` event.

7. **Two event-driven orders fire in parallel.** `brief-decision-dispatch` acts on the verdict — merging the source branch on approve, creating a follow-up work bead on reject/revise, or recording a defer marker. `post-decision-file-or-sendback` routes the brief itself: FILE (a successor bead gets re-briefed) or SEND-BACK (the brief archives and the work returns to the originator).

8. **Brief archives.** Either `brief-archive-on-request` fires immediately on a SEND-BACK event, or `brief-archive-sweep` picks up the brief in its next 24h cooldown run. Decision records are never deleted; only the working artifacts move to `~/.gc/mathcity/briefs/archive/`.

---

## Bead types

See [README-beads.md](README-beads.md) for bead type reference and bead policy.

---

## Bead Backup Setup

This section is intended to provide some documentation for how you can backup your beads directly on github by making new repositories and so you don't need to purchase a dolthub account. I haven't shared beads yet so I don't know who this works. This described my personal setup which you can adapt. If you read this and end up using something like this, please modify these instructions to remove my name and make them more general. Also, if you find a better solution please update this and make a PR. 

Each rig runs a Dolt-backed bead store. Beads hold internal operational context — decision records, brief history, bead metadata — that must not be exposed publicly even when the code repo is public. Back up bead data to a dedicated **private** GitHub repo.

### Naming convention

```
<X>-dolt
```

Examples: `hecke-dolt`, `lmfdb-dolt`, `agent-skills-dolt`. HQ (`~/gt`) uses `gascity-HQ-dolt`. Renamed 2026-07-07 from the older `<rig-name>-city-tdupu` convention; GitHub redirects the old names but local remotes should use the new URLs. Never share the beads repo with the code repo for public code repos; keep them separate.

### Setup steps

**1. Create a private GitHub repo.**

```bash
gh repo create tdupu/<X>-dolt --private
```

Verify it is private before continuing. A public beads repo is a hard error.

**2. Configure the Dolt remote.**

```bash
bd dolt remote remove origin    # drop any stale remote
bd dolt remote add origin git+ssh://git@github.com/./tdupu/<X>-dolt.git
```

The `./` after `github.com` is required by the Dolt SSH protocol — omitting it breaks the push.

**3. Push bead data.**

```bash
bd dolt push
```

Dolt writes to `refs/dolt/data`, a non-standard ref that is separate from git branches. It will not appear in the branch list and will not pollute the repo's branch history.

**4. Verify.**

```bash
git ls-remote origin refs/dolt/data
```

A SHA line in the output confirms the push landed. If the output is empty, re-check the remote URL and SSH key access.

### Two-sided sync (~/repos/X ↔ ~/gt/X)

Both the Gas City copy (`~/gt/X`) and the working copy (`~/repos/X`) point their `bd dolt remote origin` at the same tdupu/`<X>`-dolt repo. Sync is manual and on-demand:

- When you sit down to work in `~/repos/X`, run `bd dolt pull` to fetch the latest beads from the backup remote.
- When you finish working in `~/repos/X`, run `bd dolt push` to send local changes back to the remote.
- The `~/gt/X` side has its own patrol and can push independently; both sides will converge on the remote's state.

Critical: bead data must NEVER be pushed to the code repositories. Ensure that neither `~/repos/X` nor `~/gt/X` carry `refs/dolt/data` or `__dolt_remote_info__` on their code remotes (the remotes that point at `tdupu/X`, not `tdupu/X-dolt`).

### Restore from backup

To restore a rig's bead store from its private GitHub backup into a fresh directory:

```bash
mkdir -p /path/to/restore-dir
cd /path/to/restore-dir
bd init --remote "git+ssh://git@github.com/./tdupu/<X>-dolt.git" --non-interactive
```

`bd init --remote` clones the full Dolt database from `refs/dolt/data` and adopts the project identity. It downloads all bead chunks (expect ~200 MB for a large rig) and makes `bd list` immediately functional.

**After restore:** the cloned database does not auto-configure a push remote. Before pushing from a disaster-recovery clone, re-add the remote explicitly:

```bash
bd dolt remote add origin "git+ssh://git@github.com/./tdupu/<X>-dolt.git"
bd dolt push
```

**Delta on restore is normal:** beads created after the last `bd dolt push` will be missing from the restore. The delta equals the beads created since the last backup push.
