# Brief Cycle: Close the Loop (Approach C)

**Date:** 2026-07-01
**Status:** Approved by Taylor (brainstorm session); pending implementation plan
**Owner:** Taylor Dupuy
**Repos touched:** gascity-packs (mathematics pack), ~/gt city config, agent-skills (skill relocation)

## Problem

The brief cycle behaves as a one-way funnel: work is prepared, gated,
decided (301 decisions in `hecke/.beads/briefs/decisions.jsonl`), and
archived — but nothing acts on decisions and nothing merges approved work.
Meanwhile the substrate that fires orders has been down since 2026-06-21
(daemon crash: `table "d" does not have column "depends_on_id"`).

Observed consequences (audited 2026-07-01):

- 40+ unmerged `polecat/*` branches in the ~/gt city; completed Sigma_18
  hecke computations (`polecat/he-0rk2.11/.12`) stranded 22 commits ahead.
- 48 briefs on disk in hecke, 9 approved brief-records in agent_skills,
  none reaching Taylor (presentation order broken: unknown formula-v2
  target `gc.review-synthesizer`; step beads gt-a3h/f0k/pk1/qaq/ga7/9dl
  form a dependency cycle).
- 587 ready beads idle behind a dormant brief-prep pool; watchdog
  (as-ujb) designed but never implemented.
- Mid-process escalations land in agent inboxes nobody reads.
- Token burn: LLM agents execute mechanical steps (shuffle, archive
  sweep); 14 witnesses + deacon/boot/dog patrol on timers; idle polecat
  sessions; full 9-section grill applied to no-brainer briefs.

Design-level root causes (distinct from the outages):

1. **No back edges.** Decision → dispatch and decision → merge were never
   designed. All verdicts are terminal archive operations.
2. **Every bead treated as brief-worthy.** The pipeline assumes all
   finished work deserves a brief and a decision. Most beads (including
   gascity-internals chores) should close on merge with no ceremony.
3. **Dual state.** Pipeline state lives in files (`.pile/`,
   `stack/manifest.jsonl`, locks) parallel to beads; the two have drifted.
4. **Hidden skill dependency.** 9 companion skills are string-referenced
   by formulas/gates but live only in `~/.claude/skills`; agents may lack
   them and gates fail silently.

## Goal and success criteria

Work flows: polecat → refinery merge → **bead closed**, with zero ceremony
for ordinary work. Only decision-worthy work generates briefs. Briefs
accumulate; Taylor drains them in batched sessions at will; **approval
auto-merges via refinery**; escalations may optionally interrupt
immediately.

Success is measured by landing, not machinery:

- Sigma_18 branches merged to hecke main; their beads closed.
- One brief demonstrated through the full loop:
  prep → shuffle → present → approve → refinery merge → bead close.
- The 9 stranded approved brief-records in agent_skills dispatched.
- Unmerged-branch count and open-bead count falling week over week.

## Decisions made (brainstorm outcomes)

| Question | Decision |
| --- | --- |
| Complete vs simplify the built design | Phased middle path (C): flow first, canonicalize later |
| Skills integration | Move the 9 formula-referenced brief-cycle skills into `mathematics/skills/` (pack materialization ships them to every city agent); keep personal/utility skills in agent-skills; dual-home `grill-and-present` / `present-it` |
| Decision UX | Batched accumulation, drained on demand; escalations get an optional immediate-interrupt path |
| What approval authorizes | Approval = merge: submit source branch to the rig refinery; gates run; land on main |
| Brief-worthiness | Inverted default: beads are NOT brief-worthy unless flagged (`needs-decision` label or narrow criteria). Most beads close on merge silently |
| Beads-canonical state migration (Approach B) | Deferred; filed as a scoped bead, executed after flow is proven |

## Phase 0 — Substrate (prerequisite, mostly complete)

Already done 2026-07-01: gc rebuilt clean at `791e515f1`, bd at
`9626f4f1a` (includes new schema-migration code), gascity-packs local main
confirmed ahead of upstream by design (mathematics + ops packs).

Remaining:

- Restart the daemon; verify the `depends_on_id` schema error is gone and
  orders fire (`gc order check`; doctor's `order-firing-current` clears).
- Verify the reconciler at HEAD reclaims the phantom mayor/deacon session
  records (`gastown__mayor-gt-wisp-k1dnvi`, `gastown__deacon-gt-wisp-yhvy1s`).
- Reap idle polecat sessions (6 on hecke).
- Fix the import tangle: `city.toml` `[defaults.rig.imports.mathematics]`
  pins a GitHub sha while `pack.toml` imports the local path. Point both
  at the local path so pack edits propagate without re-pinning.
- **Stop condition:** if the daemon still crashes on the schema error with
  new bd, escalate upstream (beads bug); Phase 1 file/manual work proceeds,
  but event-triggered orders wait.

## Phase 1 — Close the loop

### 1a. Decision-worthiness triage (new)

Refinery post-merge behavior branches on a `needs-decision` flag:

- Unflagged bead (default): merge → close bead → done. No brief.
- Flagged bead: merge → close bead → file brief-record → wake brief-prep.

Flag criteria (initial, refinable): changes to public API / mathematical
content (proofs, intrinsics, paper text) / policy or standing directives.
Gascity-internals chores are never flagged.

### 1b. Fix the three known breaks

- Land `gsp-6bk`: `gc.review-synthesizer` agent in the gascity pack
  (unblocks `brief-present-next`'s formula-v2 target).
- Refactor the circular step beads (gt-a3h, gt-f0k, gt-pk1, gt-qaq,
  gt-ga7, gt-9dl) into a linear chain; close duplicates (gt-ga7 dupes
  gt-9dl).
- Land `gsp-itx`: refinery post-merge hooks (close-bead, conditional
  brief-filing per 1a, watchdog-wake).

### 1c. Add the two back edges

- **`brief-decision-dispatch` order** (trigger: new decision records).
  approve → submit source branch to the owning rig's refinery; gates run;
  land; close bead. reject/revise → file follow-up bead to the source
  rig. Also used to drain the 9 stranded approved brief-records.
- **Escalation path.** A blocked/failed judgment step files a `bd human`
  escalation bead; urgent ones optionally ping Taylor immediately over the
  peer channel; the rest accumulate beside briefs.

### 1d. Batched presentation

`brief-present-next` becomes drain-mode: one session presents all pending
briefs; no-brainers pre-collapsed to one-line entries for bulk
ratification. Manual trigger stays (accumulate-and-drain is the intended
UX, per Taylor).

### 1e. Prove it

1. Synthetic brief through the full loop end to end.
2. Real cargo: Sigma_18 branches (`polecat/he-0rk2.11/.12`) through
   refinery; beads closed.

## Phase 2 — Canonicalize + economize (beads filed now, executed after flow)

- Move the 9 formula-referenced brief-cycle skills into
  `mathematics/skills/`: brief-prep, coordinate-review, is-good-test,
  is-good-experiment, critical-review, catch-no-brainer, record-decision,
  present-it, grill-and-present;
  dual-home the two Taylor-facing ones. Personal/utility skills
  (search-lmfdb, profile-magma, notebook-to-package, claude-commit,
  update-*-from-source, supervisor skills) stay in agent-skills.
- Convert mechanical formula steps (shuffle, archive-sweep, manifest ops)
  from agent-judgment steps to command/script steps (≈zero tokens).
- Switch condition-polling orders to event triggers once the daemon event
  bus is back; widen patrol cooldowns (deacon/boot/dog/witnesses).
- Route mechanical/patrol roles to the cheap `codex-worker` backend.
- Fix hard-coded `/Users/tdupuy/gt/...` paths in the 17 check scripts
  (env var / relative resolution).
- Witness branch hygiene: delete merged `polecat/*` branches; TTL policy
  for stale ones.
- **Deferred (explicit bead):** beads-canonical migration of pipeline
  state (Approach B) — briefs as beads, stack as a bd query, files as
  generated views.

## Risks and handling

- **Daemon schema error survives the bd upgrade** → upstream beads
  escalation; manual/file work proceeds; event orders wait.
- **Refinery gate failure on an approved brief** → never force-merge;
  bounce as an escalation bead to Taylor.
- **Repo sync direction** (~/gt/gascity-packs rig vs ~/repos/gascity-packs):
  one direction only — rig work lands via refinery → pushed to fork →
  ~/repos pulls. The update-gascity-packs-from-source skill's sync model
  must be fixed to match (it currently assumes upstream→fork mirroring,
  which rejects the user's own pack development).
- **Phase 2 slippage** once Phase 1 "works" → guarded by filing all
  Phase 2 beads up front, scoped, before Phase 1 begins.

## Out of scope

- Beads-canonical state migration (deferred, Phase 2 bead).
- MCP activation, other packs' internals, upstream gascity changes beyond
  the escalation above.
- Any change to what the 16 gates check (gate *content* unchanged; only
  who executes mechanical ones).

## Next step

Implementation plan via grill-with-docs; plan items are then beaded out
(`bd create`, dependencies wired) so execution is tracked in beads, per
Taylor's instruction.
