---
name: create-brief
description: Produce the durable, gated `.md` brief artifact for the brief stack from a code artifact (branch, bead-id, PR, diff, GH-issue-N). The file-artifact sibling of present-it — same grill-ordered section structure, but written to disk and REQUIRED to clear the pipeline gates (test-evidence + good-test review + critical-review) before it is stack-eligible. Delivers via the clerk channel (brief stack / mail / file-inbox), NEVER by presenting in the Mayor's terminal. Trigger phrases "create a brief for X", "write a brief file for X", "draft a brief artifact on X", "make a .md brief for X", "file a brief on X", "add a brief to the stack for X". NOT for in-conversation context dumps — use present-it for "present X / give me context on X". For the end-to-end pipeline with classification, external review, and bookkeeping, use brief-prep (which composes this skill).
---

# create-brief

Produce the **durable `.md` brief artifact** that the brief pipeline runs on: a decision-ready brief file, gated before it becomes stack-eligible, delivered through the clerk channel for Taylor's adjudication.

This is the file-artifact half of the two-skill split codified under as-4nu:

| | [[present-it]] | **create-brief** |
|---|---|---|
| Output | terminal text in the current conversation | `.md` file in the brief stack |
| Gates | none (reports evidence, never self-rejects) | test-evidence + good-test + critical-review (HARD) |
| Batch | never | batch preparation applies |
| Audience | the decision-maker in this conversation | Taylor, asynchronously, via the clerk channel |

This skill is **composition by reference**: the section structure comes from [[present-it]], the gate policies from the Mayor memories `feedback_brief_test_evidence_required.md` and `project_brief_pipeline_workflow.md`, the stack schema from `project_brief_stack_workflow.md`. Do not re-implement their rules; consult them.

## Artifact format

**Path:** `~/gt/.beads/briefs/<artifact-safe-name>-brief.md` — the canonical HQ stack (S6 2026-07-15: cross-rig consolidation completed; ALL rigs deposit briefs here for uniform landing, per Taylor — supersedes the old per-rig `~/gt/hecke/.beads/briefs/` hardcode). One canonical file per artifact; revisions in place with a `.bak` before any FP-revision; no `-vN-` suffixes.

**Frontmatter (required, per the stack schema + safety overrides):**

```yaml
---
artifact: <branch | bead-id | PR-number | gh-issue-N>
status: pending-review | in-review-iter-N | review-failed | approved | pulled | presented | adjudicated | archived
deposited_at: <ISO 8601>
deposited_by: <polecat session ID or worker name>
review_gate: pending | iter-N | APPROVED | REJECT
unlock_count: <int>
priority: P0 | P1 | P2 | P3 | P4
server_touching: <bool>                  # he-lele cat-E mechanical test — see [[brief-prep]] §"Safety overrides"
user_skill_touching_override: <bool>     # as-wjv mechanical test — see [[brief-prep]] §"Safety overrides"
---
```

**Body:** the Decision-at-Top INVARIANT and the section structure are [[present-it]]'s, written to file instead of spoken:

- **Full-form (default):** the 7 grill-ordered sections per [[present-it]] §"Full-form template" — §1 what is being decided, §2 recommended answer, §3 assumptions, §4 alternatives, §5 risks, §6 evidence (test evidence lives here), §7 plan membership + required gates.
- **Compact form:** `DECISION` / `CONTEXT` / `RECOMMEND` / `CONFIRM y/n/grill-me-further` per [[present-it]] §"Compact form" — ONLY when [[catch-no-brainer]] emitted `compact_eligible: true` AND both safety-override booleans are `false` AND the shape is not `capability-blocker`.

The FIRST content after the frontmatter MUST be "What is being decided." A brief file violating the Decision-at-Top INVARIANT is malformed: rewrite before depositing; [[brief-prep]] Phase 4 auto-rejects it.

## Gates (HARD — a brief file that fails any of these is not stack-eligible)

Unlike [[present-it]], this skill **self-rejects**: do not deposit a brief that fails a gate; fix it or surface the failure. The gates, per `feedback_brief_test_evidence_required.md` (Taylor 2026-06-22) and `project_brief_pipeline_workflow.md` §3:

1. **Test-evidence gate.** Run the artifact's tests before drafting. §6 must cite, per test: file path + exact command + exit code + pass/fail + wall time. No silent skips — an unrunnable test must be declared with its impossibility reason ("no Magma reachable", "requires hardware Taylor only has"). "Tests exist but haven't been run" → not stack-eligible. Functional FAIL is presentable *data* (record it; the verdict may become "fix-then-revisit"); missing evidence is not.
2. **Good-test gate.** Each test is evaluated against [[is-good-experiment]] / [[is-good-test]] (six checkpoints; watch the classic pitfalls: data not loaded, slow route of computation). A test that functionally passes but carries BLOCKING items is NOT a passing test for brief purposes — fix the test design and re-run.
3. **Critical-review gate.** The brief itself FP-converges to APPROVING via [[coordinate-review]] (cap 4 rounds per `project_brief_stack_workflow.md`; on non-convergence mark `review-failed`, file a follow-up bead, surface to Mayor — never deposit-and-pretend).

Divide-and-conquer is encouraged: dispatch test runs in parallel within and across artifacts.

## Batch preparation

Batch semantics live HERE, not in [[present-it]] (batching across artifacts happens at the dispatch layer that queues multiple create-brief / [[brief-prep]] runs): when N briefs are queued for adjudication, prepare ALL of them — tests + draft + review — before ANY is surfaced. Don't trickle partial batches into the stack while siblings are mid-pipeline; Taylor adjudicates batches efficiently, trickles interrupt.

## Pre-authorized conditions (stub — policy-driven)

Some dispositions are pre-authorized to skip Taylor adjudication. This skill does not decide that; it declares the inputs and defers to policy:

- **Classification** comes from [[catch-no-brainer]] (he-lele 5-criterion, cats A–D; cat-E and user-skill-touching are negative classifiers).
- **Safety overrides** (`server_touching`, `user_skill_touching_override`) are computed mechanically per [[brief-prep]] §"Safety overrides" and recorded in frontmatter. Either being `true` forbids auto-approval regardless of category.
- **Auto-approval** additionally requires the auto-merge kill-switch (`~/gt/.beads/auto_merge_enabled`, default OFF/missing=false; Mayor or Taylor authority only) per `project_brief_pipeline_workflow.md` §4, with dry-run + executed JSONL records.
- Everything else → **stack-insert** ranked by `unlock_count` for Taylor adjudication.

The mechanical policy itself lives in the gate registry and the gate-keep architecture (`project_gate_keep_architecture.md`: X-policy + X-gate + improve-X trinities). As gate-keep lands, this section delegates to it; until then, treat "pre-authorized" as: no-brainer category match AND both overrides false AND kill-switch true — otherwise Taylor decides.

## Delivery — clerk channel, NOT the Mayor's terminal

Constraint (Taylor 2026-06-24, per `feedback_mayor_no_direct_grilling.md` + `feedback_clerk_is_intermediary_only.md`): the Mayor does not grill Taylor directly; the clerk owns Taylor-facing dialogue, the Mayor owns dispatch. A finished brief therefore reaches Taylor only through the clerk channel:

- **Primary: the brief stack.** Deposit the file; the clerk pulls promoted briefs and runs [[present-it]] on them toward Taylor.
- **Signal paths:** `gc mail send` to the clerk / "human" inbox channel, or the file-inbox (see [[communicate-with-clerk]]) — to announce stack state, never to carry the brief body as terminal dialogue.
- **Forbidden:** presenting the brief in the Mayor's terminal, or expecting the Mayor to relay brief dialogue to Taylor in-conversation.

## Procedure

1. **Locate the artifact** (branch / bead / PR / GH-issue / diff). Ambiguous or nonexistent → STOP, return UNABLE-TO-RUN with the reason.
2. **Run the gates**, in order: tests (gate 1), good-test evaluation (gate 2).
3. **Draft the brief** — frontmatter + Decision-at-Top + full-form or compact body per "Artifact format" above. Compute `unlock_count` (bd queries per `project_brief_stack_workflow.md`; record the transcript in §7).
4. **Self-check** the Decision-at-Top INVARIANT and section completeness ("None surfaced" + reason is acceptable; blank is not).
5. **Critical-review** (gate 3) to APPROVING; update `status` / `review_gate` per iteration.
6. **Write the file** to the stack path; deliver per "Delivery" above.
7. **Return** the brief path + verdict + gate outcomes to the caller. When invoked from [[brief-prep]], the orchestrator's Phase 2/4/5 executions ARE gates 1–3 (do not run tests or coordinate-review a second time) and it owns deposit bookkeeping (brief-record bead, follow-up beads, epic links) — don't duplicate either; when invoked standalone, say explicitly in the return that bookkeeping has NOT been filed.

## Hard rules

- **NO presenting to Taylor** — clerk channel only (above).
- **NO `bd close` on adjudication-class beads.** Taylor decides; agents propose.
- **NO commits or pushes.** Brief deposits are local-only artifact writes.
- **NO `gh issue close`, NO branch deletes.** The brief recommends; Taylor (via decisions.jsonl) executes.
- **Credential discipline** per [[never-echo-credentials]].

## Cross-references

- [[present-it]] — the terminal sibling: defines the section structure and both output shapes; no file, no gates.
- [[brief-prep]] — the end-to-end pipeline worker: classification, safety overrides, external review gate, deposit bookkeeping; produces its artifact per THIS skill.
- [[catch-no-brainer]] — no-brainer / capability-blocker classifier; source of `compact_eligible`.
- [[coordinate-review]] — the FP-loop used by gate 3.
- [[is-good-experiment]] / [[is-good-test]] — the test-quality rules behind gate 2.
- Mayor memories: `feedback_brief_test_evidence_required.md` (gate policy), `project_brief_pipeline_workflow.md` (pipeline state machine), `project_brief_stack_workflow.md` (stack infra + schema), `project_gate_keep_architecture.md` (gate trinity; pre-authorization future home), `feedback_two_skill_split.md` (the split this skill implements).

## Versioning

- **v1.0 — two-skill split** (2026-07-03, per as-4nu): created as the gated file-artifact counterpart of [[present-it]], which simultaneously dropped its gates, batch semantics, and one-at-a-time constraint. Encodes: stack path + frontmatter schema from `project_brief_stack_workflow.md`; the three HARD gates from `feedback_brief_test_evidence_required.md`; batch preparation; pre-authorized-conditions stub referencing the gate-keep architecture; clerk-channel delivery per Taylor 2026-06-24.
