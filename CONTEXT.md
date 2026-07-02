# Glossary

Canonical vocabulary for the gascity-packs domain, especially the brief
cycle (mathematics pack). Terms were pinned during the 2026-07-01
close-the-loop design session.

- **Bead** — a beads issue; the unit of tracked work. Beads are NOT
  brief-worthy by default.
- **needs-decision** — a bd label marking a bead as brief-worthy. Set only
  by Taylor or the mayor (creation or triage). Unflagged beads close on
  merge with no ceremony.
- **Brief** — a presentation document (markdown) over a source bead and
  its branch, prepared for Taylor's verdict. A brief is a *view*;
  archiving a brief never deletes the underlying work.
- **Brief-record** — a bead recording that a brief exists / was decided;
  the bead-side handle for a brief.
- **Decision** — Taylor's recorded verdict on a brief
  (approve / reject / revise / defer). Canonically an entry in
  `decisions.jsonl` (Phase 1; bead-canonical migration deferred).
  Approval authorizes merge: the source branch is submitted to the
  owning rig's refinery.
- **Escalation** — a `bd human` bead filed when an agent is blocked
  mid-process and needs Taylor. P0/P1 escalations ping Taylor
  immediately; P2+ accumulate for the next drain.
- **Drain** — a batched session in which Taylor clears accumulated briefs
  and escalations at a time of his choosing. No-brainers are collapsed to
  one-line entries for bulk ratification.
- **No-brainer** — a brief classified as requiring no real judgment
  (ratify-existing, close-done-with-proof). Presented compactly in a
  drain; auto-execution stays off without the kill-switch file.
- **Refinery** — the per-rig merge-queue agent (gastown pack). The only
  path by which branches land on main. Submission = setting
  `branch`/`target` metadata on the work bead and reassigning it to the
  refinery. Rejection returns the bead to the pool with
  `rejection_reason`.
- **Back edge** — either of the two decision-consuming flows added in
  Phase 1: decision→dispatch (`brief-decision-dispatch` order) and
  escalation→Taylor. Their absence made the old pipeline a one-way
  funnel.
- **Sync direction (gascity-packs)** — rig (~/gt/gascity-packs) →
  fork (tdupu/gascity-packs) → ~/repos/gascity-packs. The fork is
  deliberately AHEAD of upstream (gastownhall); never mirror upstream
  over it.
