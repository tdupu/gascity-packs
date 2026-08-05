# Tail-End Detector — Design Spec (2026-08-04)

## Problem

`mathcity/assets/scripts/stuck-bead-watch.py` catches beads that WERE dispatched
(carry routing metadata `gc.routed_to` / `gc.run_target` / `gc.execution_routed_to`)
then froze. It cannot see an entire class: **ready-but-never-dispatched** work —
beads that are unblocked, wanted, but were never slung and sit idle. Per the
CONSERVATION INVARIANT on `gsp-2bowrk`: every bead that CAN be worked
(ready+unblocked) and SHOULD be worked and ISN'T, past a >3d age trigger, must be
caught by the lost filter. This is the second lost class named there.

## Verified evidence (live bd queries, 2026-08-04)

Across rigs gascity-packs, hecke, agent_skills, lmfdb, jacobi, homog,
magma_clifford_algebras: open∩ready, idle>3d, non-scaffolding, non-gated =
**1795**. The stale brief figure (~202) predates today's brief-factory run which
created ~1000 `task`-type convoy/molecule-adjacent beads. Refining to
issue_type∈{task,bug,feature} and excluding routed beads (stuck-bead-watch's
domain) → **1064 never-dispatched actionable-idle work beads**. This magnitude is
exactly why resling must be batch-capped: dumping 1064 reslings would re-strand
them all.

## Fork resolutions

### Fork 1 — Idle measure
Real idle age = `now − max(created_at, updated_at, last_activity)` per bead
(`last_activity` absent in `bd list --json` → falls back to created/updated).
Threshold default 3 days. NO first-observation waiting room: a genuinely
3-day-idle bead registers on the FIRST scan. (Contrast stuck-bead-watch's
two-tick `first_seen_stuck` grace, which is for freshly-dispatched beads.)

### Fork 2 — Integration (reuse, do not fork the pipeline)
Emit `lost-bead-classification.v1` TOML records into the SAME
`.beads/lost-bead-classifications/` root consumed by
`lost-bead-classification-rollup` (validated by `lost-bead-filter.py`). Distinct
fingerprints keep them grouped separately from stuck-bead-watch's records. Mirror
stuck-bead-watch's event-bead creation + `bd dep relate` + `escalated/` idempotency
markers so re-runs never duplicate an event.

### Fork 3 — Classification split (load-bearing)
Conservative supersession heuristic keyed on idle age:
- **Superseded-candidate** — idle ≥ `SUPERSEDE_AGE_DAYS` (default 30d):
  `lost_class=stale_or_duplicate`, `recommendation=close_moot`,
  `root_cause.class=duplicate_or_superseded_source`, `repair_candidate=false`,
  fingerprint `ready_idle_tail_superseded`. Rollup → close brief (no-brainer
  auto-close downstream). Deliberately conservative: age flags a *candidate*; the
  actual close is still gated through a brief, never done by the detector.
- **Resling (still-wanted)** — idle in [3d, 30d):
  `lost_class=immediate_strand`, `recommendation=resling`,
  `root_cause.class=no_worker_claimed`, `repair_candidate=true`, fingerprint
  `ready_idle_tail_resling`. Rollup → resling brief.

**Batch caps** (fleet-absorbing cadence, never dump): resling capped at
`RESLING_BATCH_CAP` (default 10) oldest-first per run; superseded capped at
`SUPERSEDE_BATCH_CAP` (default 25). Follow-up bead filed for smarter
supersession detection (title/dependency/duplicate analysis) beyond the age proxy.

### Fork 4 — Fail loud (P6.1)
- Every subprocess time-bounded (30s); hang → `fail()` nonzero exit to stderr.
- Heartbeat: persist actionable-tail count in `tail-heartbeat.json`. If the count
  GROWS vs the previous run (producers outpacing reclaim), emit a heartbeat event
  bead (fingerprint `ready_idle_tail_growing`). Tail size is never silent — count
  printed every run.
- Any error → nonzero exit, not silent log.

## Filter (never-dispatched actionable work bead)
open ∧ in `bd ready` ∧ issue_type∈{task,bug,feature} ∧ real-idle≥3d ∧
NOT scaffolding (title∌Patrol/Deacon/Witness/Refinery/Polecat; id∌`-rig-`; not a
bare rig-name title) ∧ NOT gated (title∌taylor-gated/gh-auth) ∧ NOT routed
(id∉ union of routed-metadata-key sets — the dedup boundary with stuck-bead-watch
and the operational meaning of "never dispatched").

## Architecture (pure core + edge I/O, mirrors stuck-bead-watch)
- Pure/testable: `parse_ts`, `real_idle_seconds`, `is_scaffolding`, `is_gated`,
  `is_work_type`, `find_actionable_tail`, `classify_bead`, `select_batch`,
  `render_record`.
- Edge: `_gather_rig` (`bd list`/`bd ready` per rig, `--limit 0`),
  `_gather_routed_ids` (`gc bd list --has-metadata-key`), `_preflight`,
  event create/relate, `main`.
- `--dry-run`: compute + classify + report counts, write nothing, create no beads.

## Order
`mathcity/orders/tail-end-detector.toml`: exec, scope=city, trigger=cooldown,
interval 15m, timeout 5m, idempotent=false. Writes into the shared
classification-root; the 10m rollup cooldown consumes the records.

## Record filename & collision (P4.2)
Records written as `{bead_id}.tail.toml` (still matches the rollup's `*.toml`
glob) so they never clobber stuck-bead-watch's `{bead_id}.toml` records in the
shared root. The routed-exclusion filter already keeps the two detectors'
bead sets disjoint; the suffix is defensive.

## §E — Alternatives surveyed (check-wheel, P1.20)
- **Parallel reclaim pipeline** — ruled out (Fork 2): Taylor is de-duplicating
  overlapping reclaim mechanisms; a second pipeline is a regression. Adopt: reuse
  the lost-bead-classification.v1 record contract + existing rollup.
- **First-observation grace (stuck-bead-watch's two-tick model)** — ruled out
  (Fork 1): would delay a genuinely-3-day-idle bead by a whole scan cycle. Adopt:
  key off real max(created/updated/last_activity) idle age; register on first scan.
- **Detector auto-closes superseded beads directly** — ruled out (Fork 3): too
  aggressive, no human gate. Adopt: emit `close_moot` classification → rollup files
  a close brief (no-brainer auto-close is downstream and gated).
- **Full supersession detector now (title/dep/duplicate analysis)** — deferred as
  too large; adopt the conservative age-proxy *named workaround* with a follow-up
  bead (P1.17).

## Testing
TDD on the pure core: idle-on-first-scan, scaffolding/gated/routed exclusion,
superseded-vs-resling split, batch cap (oldest-first), record schema validity
(round-trips through `lost-bead-filter.py validate`).
