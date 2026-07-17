---
name: decisions-to-briefs
description: Use when pending decisions are piling up OUTSIDE the brief pipeline — a running decision list in conversation, a batch of "Taylor needs to decide X" items, a decision tally the Mayor is carrying in his head, or a durable decision-inbox directory — and they need to become adjudicable brief artifacts on a pile. Trigger phrases "decisions to briefs", "pile these decisions", "convert the decision list into briefs", "file my pending decisions", "brief my decision inbox". NOT for a single code artifact with runnable tests (use create-brief or brief-prep directly) and NOT for presenting briefs (use present-briefs).
---

# decisions-to-briefs

Convert pending decisions into adjudicable briefs with machine-readable
consequences.

## Overview

**A decision you need to make IS an unfiled brief.** Under the one-bead
model (brief-system POLICY B2.2), a brief bead *is* a decision bead — so a
"running decision list" living in conversation or in the Mayor's tally is
pipeline-invisible debt. This skill drains that debt: each decision becomes
one brief with §1 decision-at-top, a recommended verdict, and an
**ACTION-BLOCK** declaring what happens on each verdict.

Input shapes accepted:

- **one decision** ("should we flip gh-111's closure reason?"),
- **a batch** (the Mayor's 14-item list),
- **a durable decision-inbox** (a directory such as `~/gt/.beads/decisions/`
  or a `decisions-track` pile — drain everything not yet briefed).

## Procedure

1. **CLASSIFY the decision shape** (table below). This is the load-bearing
   step: shape determines form, action-block content, and whether any
   auto-action is permitted at all.
2. **PICK compact vs full form.** Same rules as [[present-it]] /
   [[catch-no-brainer]]: compact ONLY for y/n-shaped decisions with no
   safety override; named-options, judgment-heavy, math-content, or
   safety-flagged decisions are full-form. Either way the brief must fit
   **one terminal screen** — full-form here means "carries §options and
   §risks", not "long".
3. **DRAFT the brief**: frontmatter, then §1 "What is being decided" as the
   FIRST body content (Decision-at-Top INVARIANT), then the recommended
   verdict with a one-line rationale.
4. **ATTACH the ACTION-BLOCK** (schema below) as a fenced `yaml` block in
   the brief. Apply the safety invariant BEFORE writing any auto-action.
5. **DEPOSIT on a pile via [[create-brief]] conventions** — one file per
   decision, `NN-<slug>-brief.md`, plus one line in the pile's
   `manifest.jsonl`. Never present in the Mayor's terminal; the clerk /
   present-briefs channel drains the pile.

## Shape classification

| Shape | Symptoms | Form | Auto-action allowed? |
|---|---|---|---|
| **compact y/n** | one reversible dispatch hangs on approval ("sling X?") | compact | yes — `sling-bead`, `wire`, `file-follow-up-brief` |
| **named options** | genuine alternatives a/b/c to weigh | full | yes, per chosen option, if reversible |
| **taylor-manual-math** | verdict requires Taylor's mathematical judgment (done-vs-residual, proof content) | full, flagged | **NO** — `external-reminder` only |
| **external-reminder** | only a human can act (interactive auth, credential entry, physical/console step) | compact | **NO** — `external-reminder` only |
| **stays-out** | irreversible, server-live-write, or user-skill-touching consequence | full | **NEVER** — explicit human gate, per-node auth where applicable |

When unsure between two shapes, take the more restrictive row.

## ACTION-BLOCK schema

Every brief carries exactly one `action_block`, a fenced `yaml` block. Each
verdict key maps to an ordered list of action items:

```yaml
action_block:
  on_approve: [ {type: <action-type>, target: <bead-id|slug|path>, ...} ]
  on_reject:  [ {type: <action-type>, target: ..., ...} ]
  on_defer:   [ {type: snooze, interval: <e.g. 7d>} ]
```

Rules:

- All three keys REQUIRED. An empty list `[]` is valid and means "record
  the verdict, do nothing else".
- `on_defer` is always exactly `[{type: snooze, interval: ...}]` — defer is
  not an adjudication (POLICY verdict vocabulary); the brief resurfaces
  after the interval.
- Extra keys per item are type-specific (e.g. `worker:` for sling-bead,
  `note:` for external-reminder).
- The block is *declarative*: this skill only writes it. Execution belongs
  to the brief-record-decision verdict edge (part b of gsp-ft64, not yet
  live) or to the Mayor acting on the recorded verdict.

### Action-item types

| type | Meaning | Reversible? |
|---|---|---|
| `sling-bead` | dispatch `target` bead to a convoy/worker (`worker:` optional) | yes — a slung bead can be recalled/closed |
| `file-follow-up-brief` | create a successor brief for the next decision this one exposes | yes |
| `wire` | graph surgery: `op: dep-add \| attach-epic \| create-epic`, plus `target` | yes |
| `close-supersede` | close `target` bead(s) with a supersede reason naming the winner | yes (reopenable) |
| `run-skill` | run a named audit/hygiene skill (e.g. `bead-check`) on `target` | yes (read-only skills only) |
| `external-reminder` | CANNOT automate — re-surface `note:` to the human; the verdict edge must ping, never act | n/a |

## HARD SAFETY INVARIANT

**Action-blocks auto-execute ONLY reversible dispatch** (`sling-bead`,
`file-follow-up-brief`, `wire`, `close-supersede`, read-only `run-skill`).

**Irreversible, server-live-write, or user-skill-touching decisions carry
NO auto-action.** Their action-block entries are `external-reminder` (or
nothing), and the brief is full-form with the hazard named in §risks. The
human gate is the action. Canonical example: **#335 N2s/N2 server
writeback must NEVER be an auto-slinging brief** — it stays
external-reminder with explicit per-node authorization.

Concretely, NO auto-action for: git push / force-push / merge / branch or
tag deletion ([[authorize-git-operation]] territory), `gh issue close` or
other live GitHub writes, database/server writebacks, edits to user-scope
skills (`user_skill_touching_override`), credential operations, deletion of
non-regenerable data.

Red flags — if you catch yourself writing any of these, STOP and downgrade
the item to `external-reminder`:

| Rationalization | Reality |
|---|---|
| "The approve verdict already authorizes the push" | A verdict on a brief is not [[authorize-git-operation]]. Two different gates. |
| "It's a tiny server write, easily undone" | Server-live-write is a category, not a size. Per-node auth or nothing. |
| "The worker will re-check before acting" | The action-block IS the check. Downstream re-checks are backstops, not permission. |
| "Wrapping it in a slung bead makes it reversible" | Slinging a bead whose *content* is irreversible launders the hazard. Classify by the terminal effect. |

## Decision briefs vs the create-brief gates

These briefs decide *dispositions*, not code artifacts: [[create-brief]]'s
test-evidence and good-test gates are **N/A by construction** — declare
`gates: test-evidence N/A (decision-shaped, no runnable artifact)` rather
than silently skipping. The Decision-at-Top INVARIANT and critical-review
hygiene still apply in full.

## Pile + manifest conventions

- Files: `NN-<slug>-brief.md`, zero-padded, one decision each.
- Frontmatter (minimum): `artifact:` (bead id if the decision maps to one,
  else `none`), `status: ready-for-adjudication`, `form: compact|full`,
  `track: <track-name>`.
- `manifest.jsonl` beside the briefs, one line per brief:
  `{"n": 1, "slug": "...", "source_bead": "...", "form": "compact",
  "track": "...", "status": "ready"}` — so the presenter can count and
  order without opening files.
- Verify freshness before drafting: `bd show` every source bead — a closed
  or deferred source changes the decision (e.g. "approve the audit" becomes
  "approve the delivered plan"). Record any such reclassification in the
  brief.

## Cross-references

- [[create-brief]] — artifact format, frontmatter schema, clerk-channel
  delivery this skill deposits through.
- [[catch-no-brainer]] / [[present-it]] — compact-eligibility rules and
  both body templates.
- [[present-briefs]] / [[adjudicate-brief]] — how the pile drains.
- [[brief-prep]] — safety-override mechanics (`server_touching`,
  `user_skill_touching_override`).
- `brief-record-decision` formula — the verdict edge that part (b) of
  gsp-ft64 extends to parse and execute action-blocks.
- [[file-briefs]] (gsp-geuo) — the onboarding sibling this skill
  generalizes; wire as related, do not compete.

## Versioning

- **v0.1 — MVP** (2026-07-16, epic gsp-ft64): classification + form pick +
  action-block schema + safety invariant + pile deposit. Calibration run =
  the 14-item decision list piled at `~/gt/.beads/decisions-track/`; per
  gsp-ft64 notes, after 10 adjudications the accumulated verdict data
  triggers part (b) — the full 3-part design (skill + schema + verdict-edge
  execution).
