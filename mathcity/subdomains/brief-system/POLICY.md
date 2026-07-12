# Brief-System Policy

| Field | Value |
| --- | --- |
| Status | Adopted |
| Date | 2026-07-11 |
| Decided | Taylor Dupuy |
| Applies to | `mathcity-brief-system` subdomain — brief pipeline, experiment gates, closure discipline, Magma package updates, server-touching work, no-brainer automation |
| Consumers | `brief-prep`, `catch-no-brainer`, `present-it`, `create-brief`, `is-good-experiment`, `is-good-test`, mayor-math priming, any polecat that produces or adjudicates briefs |

Governs how artifacts enter the decision pipeline, how experiments and tests are designed and evidenced, when work can be closed, how Magma packages are updated, and what requires explicit Taylor authorization before execution. Every rule has an ID and a pass/fail criterion a skill can cite. Gate IDs (G1–G16) refer to the registry at `mathcity/assets/brief-pipeline/gates.toml`.

---

## Pillar 1 — Brief production

*A brief is a decision aid, not a report. Its purpose is to give Taylor exactly enough structured context to answer one question, in one session, without asking follow-up questions.*

- **B1.1 Decision-at-Top INVARIANT.** The first content after the artifact header MUST be "What is being decided." Not origin. Not mathematics. Not timeline. Not required gates. The decision. Every downstream section is evidence for the decision; the question is the anchor. A brief that opens with anything else is rejected before deposit — `brief-prep` self-rejects, `create-brief` refuses to write the file. In-conversation terminal dumps (`present-it`) have no auto-rejector, but the same rule applies and violating it is a skill failure.
- **B1.2 One decision per brief.** A brief routes one artifact to one decision. Splitting concerns ("we need to decide A and also B") → two briefs. A brief that bundles two unrelated decisions cannot be adjudicated atomically.
- **B1.3 Compact form is gated, not default.** Compact form (`DECISION / CONTEXT / RECOMMEND / CONFIRM`) is allowed ONLY when ALL four conditions hold simultaneously: (a) `catch-no-brainer` returned `no_brainer: true` with `compact_eligible: true`; (b) `server_touching = false`; (c) `user_skill_touching_override = false`; (d) shape is NOT `capability-blocker`. If any condition fails → full-form (7 sections per `present-it` §"Full-form template"). Capability-blocker shapes always force full-form and route via the capability-resolution path before re-classification.
- **B1.4 All 16 gates must have evidence or N/A.** Every gate in the `standard` profile (G1–G16) must appear in the brief with either evidence or an explicit N/A plus a one-sentence reason. A gate with no entry at all is a mechanical failure. Gates that don't fire (e.g., G6 LaTeX-gate on a non-LaTeX artifact) must still appear as N/A.
- **B1.5 Gate G1 test-evidence is non-optional.** Any claim about tests must include: the exact command run, the scope (files/functions tested), the result (exit code + first 200 lines or summary), and the date. Missing any element → G1 FAIL → brief cannot be deposited. "Tests pass" with no command or output is not evidence.
- **B1.6 Gate G16 base-ref required.** Test evidence that depends on `main`/`master` state must record the exact base commit (`git rev-parse HEAD` in the target repo at test time). Test evidence with no base ref recorded is unverifiable as the repo moves → G16 FAIL.
- **B1.7 Unrunnable tests are declared, not skipped.** If a test cannot run in the current session (no Magma license, missing DATA/, requires aia-s27, etc.), the brief records the test file path, the reason it is unrunnable, and what surface-check evidence stands in (e.g., diff-read of the test + review of the intrinsic). "Did not run tests" with no further text → G1 FAIL.
- **B1.8 External review gate G4 critical-review.** Every full-form brief passes through `critical-review` before deposit. The reviewer explicitly looks for: correctness risks, policy misses (P-rule or B-rule violations), and missing evidence. A brief deposited without a G4 record → mechanical failure.
- **B1.9 No-brainer auto-execute is gated by the kill switch.** When `catch-no-brainer` confirms no-brainer + compact-eligible + safety overrides clear, the brief MAY auto-execute via `gc sling` and auto-archive to `.pile/.no-brainer`. This automation is ONLY active if `.beads/auto_merge_enabled` exists in the rig root and is `true`. Absent file = OFF. A no-brainer that surfaces at the human-review layer is a pipeline regression (catch-no-brainer should have caught it).
- **B1.10 Brief-record bookkeeping G8 is always required.** After deposit: the pile, stack, manifest, and decision/archive records must remain consistent. A brief deposited without updating the manifest, or a decided brief not archived, → G8 FAIL.

---

## Pillar 2 — Experiment and test discipline

*An untestable claim is not a result. An experiment without a falsifiable question wastes compute. A test without a named thing-under-test is an accident waiting to pass.*

- **B2.1 Every experiment has exactly one falsifiable question.** A goal ("explore X"), a wish ("understand Y"), or a description ("run Gamma0_fp on order O") is not a question. A question has possible answers. "Does `Gamma0_fp` cost scale linearly in `coprime_pairs(n)`?" is a question. Missing → `is-good-experiment` Checkpoint 1 REJECT, experiment does not run.
- **B2.2 Both outcomes must be interpreted.** For any experiment question, the brief or proposal must state: what Taylor learns if the answer is YES, and what Taylor learns if the answer is NO. An experiment whose NO outcome is uninterpreted is a confirmation trap — it can only confirm, never refute. Single-outcome proposals → `is-good-experiment` Checkpoint 2 BLOCKING → NEEDS-REVISION.
- **B2.3 Coverage must support an inferential leap.** A single data point rarely allows a general conclusion. An exhaustive sweep is rarely the cheapest way to answer a coverage question. The proposal must state why the chosen coverage (which inputs, which orders, which levels) is the smallest set that would let Taylor conclude something about the general behavior. Over-narrow and over-broad are both checkable failures (Checkpoint 3).
- **B2.4 Cost estimate is required for long-running experiments.** Any experiment expected to take more than 30 minutes wall time on the target machine must include a resource estimate (wall time, RAM, disk for outputs). Missing estimate on a long-running experiment → Checkpoint 4 MAJOR. Short-term experiments may omit detailed estimates.
- **B2.5 Two pitfalls are always checked.** The `is-good-experiment` reviewer MUST explicitly evaluate:
  - **Not loading data.** Does the proposal name every data dependency and how it is loaded? (`AttachSpec`, `SetLMFDBRootFolder`, `load_*` calls.) Missing → Checkpoint 5 flag.
  - **Slow route of computation.** Does the proposal state which intrinsics it calls and why those are the right ones (not a generic fallback)? Failing to use a cached result, calling a quadratic helper inside a loop, or defaulting to a full recompute when a fast path exists → flag.
- **B2.6 Test files name what they test.** A Magma test file (`test-*.mag`) MUST identify X — the intrinsic, function, or pipeline under test — in a header docstring or explicit annotation. `is-good-test` infers X from the file; if X cannot be identified, that is a Checkpoint 1 REJECT. Action: add a header docstring naming the intrinsic/function/pipeline.
- **B2.7 Test pass AND fail must both be meaningful.** A test where PASS means "something happened" and FAIL means "something went wrong" is a confirmation trap. The test must be designed so FAIL specifically indicates the named thing X is broken. Assert-by-accident (e.g., `nil eq nil` always true) is a Checkpoint 2 failure. A test that never fails is not a test.
- **B2.8 G2 good-test verdict required before merge.** Any brief proposing to merge code that adds or modifies tests must include a G2 good-test verdict on the new/modified test files, emitted by `is-good-test`. The G2 verdict is a review (not mechanical) — it must name the reviewer (session ID or polecat ID). A diff that adds test files without G2 evidence → G2 FAIL.
- **B2.9 Unrunnable experiments are not silent.** If an experiment cannot run (no Magma, missing DATA/, timeout too short, environment mismatch), the polecat reports `UNRUNNABLE` with the reason, obtains a `critical-review` verdict that confirms the conclusion from static evidence, and deposits a brief with that evidence. An experiment that silently fails and produces no brief → G7 FAIL (no artifacts staged).

---

## Pillar 3 — Work closure discipline

*A bead is not closed until the work is verifiably done. Closing early to make a dashboard green is worse than leaving it open.*

- **B3.1 Closure requires verifiable acceptance.** Before calling `bd close`, the polecat must confirm at least one of: (a) acceptance criteria in the bead description are individually checked off, (b) a linked test passes, (c) a `critical-review` verdict says PASS, or (d) Taylor has explicitly said "close it." Closing on vibes → fail.
- **B3.2 Server-touching items require Taylor OK before close, not after.** A bead tagged `TAYLOR_OK_REQUIRED` or `server-touching` cannot be closed by a polecat without recorded explicit Taylor authorization (a `decisions.jsonl` entry, an inline plan annotation, or a session statement). Closing first and noting the Taylor-OK-needed status later → policy violation.
- **B3.3 Downstream beads must not be orphaned on close.** Before closing a bead, check: does any open bead list this as a dependency? If so, the dependency is satisfied — but the downstream bead's metadata must be updated to mark this dep closed. Closing without checking downstream → G8 FAIL (bookkeeping).
- **B3.4 Cross-repo work self-closes.** When a polecat ships work that spans repositories (e.g., a hecke bead whose commit touches `~/repos/hecke` and `~/repos/gascity-packs`), the polecat self-closes the work-bead on completion. Do NOT reassign to refinery or wait for Mayor to close. The work-bead is the polecat's responsibility from claim to close.
- **B3.5 Convoy close requires all members closed.** An owned convoy (`gc convoy create --owned`) is only eligible for `gc convoy land` when ALL member beads are in a terminal state (CLOSED or superseded). A convoy landed with open members is a silent data loss — the open members lose their convoy context.
- **B3.6 The all-closed check is never skipped for brief auto-merge.** No-brainer automation must check that all beads in scope are closed before executing. The phasemapping bug (text-scanning bead descriptions for "blocked") is a known regression surface — all closure checks must be against status values, not text content.

---

## Pillar 4 — Magma package update discipline

*package-certify.mag and its siblings are production artifacts. Changes to them propagate to every hecke certify run. The standards are accordingly higher than for test scripts.*

- **B4.1 Proto-intrinsics must be promoted before the handoff bead closes.** An intrinsic that exists only in a test script (`test-*.mag` or `make/one-offs/`) is a proto-intrinsic. It must be promoted into its appropriate package (`package-certify.mag`, `package-LMFDB.mag`, etc.) before the implementing bead closes. A handoff bead whose intrinsics are still in test scripts is not done.
- **B4.2 Dead code is removed at promotion time.** When a new algorithm (e.g., cyclic sweep) replaces an old one (e.g., CSP solver, Approach A pre-screen), the old code is removed in the same commit that adds the new code. Leaving the old code behind for "reference" creates drift — the production path and the legacy path coexist, and the next polecat won't know which is current. Exception: the old code is labeled `// legacy: kept for offline diagnostics` and tracked by a follow-up cleanup bead.
- **B4.3 improve-package-README after every intrinsic addition.** Any commit that adds, renames, or removes a public intrinsic from a `package-*.mag` file requires a corresponding update to the `magma/test/README-tests/` coverage (gate G10 / G15). The README-tests update lands in the same commit or the immediately following commit, tracked by the same bead. An intrinsic with no README-tests coverage → G10 FAIL.
- **B4.4 Four certify gates on every repaired record.** Any gamma0 record modified by a repair script must pass all four certify gates before the repair bead closes:
  - `certify_gamma0_stored_matrix_presentation`
  - `certify_gamma0_presentation`
  - `certify_defining_element_canonical`
  - `certify_subgroup`
  Passing only a subset and closing → B3.1 FAIL (acceptance criteria not met).
- **B4.5 Offline-only intrinsics are labeled or retired.** An intrinsic used only in `make/one-offs/` or `test-*/` diagnostics (never called from production `make/` scripts) must be either (a) labeled with a `// offline-only diagnostic` comment, or (b) retired in a cleanup bead. Unlabeled offline intrinsics accumulate as dead weight and confuse the next polecat. The retirement decision is tracked as a separate bead (not bundled into a production repair bead) so it can be deferred without blocking.
- **B4.6 Package changes go through a brief.** Any change to a `package-*.mag` file that adds or modifies an intrinsic used in production certify/repair pipelines requires a brief before the PR opens. The brief covers: what the intrinsic does, test evidence (G1 + G2), and the `improve-package-README` gate (G10). Direct commits without a brief → B1.1 pipeline bypass.

---

## Server-touching policy

Server-touching work requires a separate authorization track because mistakes are slow to reverse, run on hardware Taylor doesn't control, and can corrupt live database state.

- **S1 Definition.** Server-touching means any of: dispatching to `aia-s27`; writing to the `DATA/` directory tree; running `queue-repairs.sh` without `--dry-run`; running `make-recompute-gamma0-from-transversal.mag` with `I_HAVE_A_BACKUP=1`; adding an entry to `magma/make/dispatch/priority.conf`; any SSH-routed command that modifies server state. All other work (local Magma scripts, local test runs, bead updates, package edits) is NOT server-touching.
- **S2 Dry-run first, always.** Every server-touching sweep (classification, repair batch, recompute queue) must complete a successful dry-run pass before a non-dry-run dispatch is authorized. Dry-run output is staged under `~/gt/tmp-for-taylor/` and referenced in the brief.
- **S3 Smoke test before full batch.** Between the dry-run and any full-batch dispatch, a smoke test of 4 representative items (one per repair route) must be completed and presented as a Taylor gate. The smoke test brief must include all four certify-gate results per item. Taylor's explicit go/no-go is required before the batch.
- **S4 Per-item Taylor OK for each TAYLOR_OK_REQUIRED bead.** Taylor OK is not transitive. Authorizing the dry-run sweep does NOT authorize the recompute batch. Each TAYLOR_OK_REQUIRED bead in a convoy requires its own recorded authorization in `decisions.jsonl` or an inline plan annotation.
- **S5 Long-running recomputes queue early.** Recompute jobs that take hours to days (full `Gamma0_fp(:redo:=true)`, RECOMPUTE_IQ via transversal on large orders) should be queued as early as possible so they run in parallel with code work. A bead that blocks the relabel step and has a multi-day recompute hidden inside it is a planning failure — queue it in its own bead immediately on identification.
- **S6 Recompute route: transversal beats full Gamma0_fp.** When a record has a stored transversal and the transversal recompute produces a clean result (under 1 second), the route is `RECOMPUTE_IQ` (transversal). Full `Gamma0_fp(:redo:=true)` is the fallback for records with no stored transversal. Proposing a full Gamma0_fp recompute for a transversal-eligible record is a planning error.
- **S7 Gate G5 stops server-touching work at the brief.** A brief whose artifact is server-touching must record `server_touching: true` in its frontmatter. No-brainer auto-execute is blocked (B1.3). The brief goes to full-form review and Taylor adjudication. A server-touching brief that was routed through compact form → G5 FAIL.

---

## No-brainer policy

No-brainers are briefs a skilled reviewer would approve without hesitation given only the compact 4-line summary. They exist to clear low-stakes queue items without consuming Taylor's decision budget.

- **N1 Classification is catch-no-brainer's job, not the polecat's.** A polecat must not self-classify a brief as a no-brainer. Every brief goes through `catch-no-brainer` before the compact/full-form branch. A polecat that skips this step and emits compact form → B1.3 FAIL.
- **N2 Four eligible categories (cat-A/B/C/D).** No-brainer classification requires the brief to fall into one of four clean categories:
  - cat-A: trivially correct mechanical change (e.g., rename, format)
  - cat-B: revert of a known-good prior state
  - cat-C: delete of confirmed-superseded artifact
  - cat-D: bookkeeping/metadata update with no code path impact
  Any artifact outside these four categories → not a no-brainer → full-form.
- **N3 Safety overrides trump classification.** Server-touching (S-series above) and user-skill-touching (any change to `~/.claude/skills/` or `~/repos/agent-skills/skills/`) block compact form regardless of cat classification. B1.3 is the gating rule. `catch-no-brainer` must emit `server_touching: true` or `user_skill_touching_override: true` when these surfaces are in scope.
- **N4 Capability-blocker shape routes to resolution, not compact.** If `catch-no-brainer` identifies a `capability-blocker` shape (the brief cannot proceed because a required capability is missing), the brief must route through the capability-resolution path first. Resolving the blocker, then re-classifying, is the protocol — NOT emitting compact form with a blocker note.
- **N5 Kill switch overrides all automation.** The auto-execute path (B1.9) is gated by `.beads/auto_merge_enabled` in the rig root. Missing file = false = automation off. Changing this file requires explicit Taylor authorization. No code path should assume the kill switch is on.
- **N6 Surfacing a no-brainer at Taylor is a regression.** If a brief reaches the human-review layer (clerk presents to Taylor) and Taylor's immediate reaction is "this is obvious, why am I seeing it?" → that is a catch-no-brainer regression, not a scheduling slip. The fix is in the classifier prompt or category definitions, not in asking Taylor to accept more noise.

---

## Non-negotiables (quick checklist)

- Decision-at-Top: the first content after the artifact header MUST be "What is being decided" — no exceptions (B1.1).
- One decision per brief. Two decisions → two briefs (B1.2).
- Compact form only when all four conditions hold simultaneously (B1.3).
- G1 evidence = command + scope + exit code + output + date. "Tests pass" is not evidence (B1.5 / G1).
- G16 base-ref required for any test evidence that touches master state (B1.6 / G16).
- Unrunnable tests/experiments are declared, not skipped (B1.7 / B2.9).
- External review G4 required on every full-form brief before deposit (B1.8).
- No no-brainer automation without kill switch enabled (B1.9 / N5).
- Closure requires verifiable acceptance, not vibes (B3.1).
- TAYLOR_OK_REQUIRED items cannot be closed without recorded authorization — not before, not after (B3.2).
- Convoy landing requires all members in terminal state (B3.5).
- Proto-intrinsics promoted before handoff bead closes (B4.1).
- Dead code removed at promotion time, or labeled + tracked in a cleanup bead (B4.2).
- improve-package-README runs after every intrinsic addition (B4.3).
- All four certify gates pass before any gamma0 repair bead closes (B4.4).
- Server-touching work: dry-run first, smoke test second, Taylor OK per item, then batch (S2–S4).
- Transversal recompute preferred over full Gamma0_fp for transversal-eligible records (S6).
- G5 stops server-touching at the brief; no compact form for server-touching artifacts (S7).
- No-brainers: catch-no-brainer classifies, polecats don't self-classify (N1).
- Capability-blocker shape → resolution path, not compact (N4).

---

## Verdict vocabulary

Reuses the brief-cycle Decision vocabulary — no parallel vocabulary introduced:

- **approve** — all B/S/N rules pass; brief or work item is clean to proceed (G-gates all have evidence or explicit N/A).
- **revise** — fixable violations; names the specific rule(s) broken, the artifact that triggered each, and a compact brief that seeds a fix.
- **reject** — the approach itself violates a rule with no workaround (e.g., the artifact is server-touching and Taylor has not authorized it; the experiment has no falsifiable question). Send back for a different approach.
- **defer** — needs a human call: ambiguous server-touching boundary, contested classification, or a capability-blocker where Taylor must decide the resolution path.

---

## References

- `mathcity/assets/brief-pipeline/gates.toml` — G1–G16 gate registry (source of truth for all gate IDs cited here)
- `mathcity/skills/brief-prep/SKILL.md` — end-to-end brief pipeline procedure
- `mathcity/skills/catch-no-brainer/SKILL.md` — no-brainer classifier (no-brainer categories, capability-blocker, safety overrides)
- `mathcity/skills/create-brief/SKILL.md` — the file-artifact producer (frontmatter schema, stack path, gate slots)
- `mathcity/skills/present-it/SKILL.md` — terminal context dump producer (Decision-at-Top INVARIANT, full-form template, compact form conditions)
- `mathcity/skills/is-good-experiment/SKILL.md` — 6-checkpoint experiment reviewer
- `mathcity/skills/is-good-test/SKILL.md` — test-design reviewer (wraps is-good-experiment, adds assert-by-accident check)
- `mathcity/skills/critical-review/SKILL.md` — G4 reviewer
- `mathcity/subdomains/dev/POLICY.md` — P-rule set for pack portability and boundary discipline (G5 server-touching is downstream of those P-rules; this file governs the brief-pipeline expression of that constraint)
- `he-xkq3` (bead) — the live hecke gate registry that `gates.toml` was derived from; consult for hecke-specific gate calibration decisions
