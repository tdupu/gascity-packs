# Brief-System Policy

| Field | Value |
| --- | --- |
| Status | Draft revision (supersedes Adopted 2026-07-11 version) |
| Date | 2026-07-12 |
| Decided | Taylor Dupuy |
| Applies to | `mathcity-brief-system` subdomain — brief definition and lifecycle, pile/ordering, no-brainer automation, LaTeX gate, experiment gates, testing/spec gates, documentation gates, closure discipline, Magma package updates, server-touching work |
| Consumers | `brief-prep`, `catch-no-brainer`, `present-it`, `present-briefs`, `create-brief`, `is-good-experiment`, `is-good-test`, `record-decision`, `bead-flight-precheck`, mayor-math priming, any polecat that produces or adjudicates briefs |

Governs what a brief IS, how briefs enter and leave the decision pipeline, how they are ordered for presentation, when automation may execute them without Taylor, how experiments and tests are designed and evidenced, when work can be closed, how Magma packages are updated, and what requires explicit Taylor authorization before execution. Every rule has an ID and a pass/fail criterion a skill can mechanically check. Gate IDs (G1–G16, G5b) refer to the registry at `mathcity/assets/brief-pipeline/gates.toml`.

Rule-ID letters: **B** = brief production/lifecycle/closure/package (B1.x production, B2.x lifecycle, B3.x closure, B4.x Magma packages), **N** = no-brainer, **L** = LaTeX, **E** = experiment, **T** = testing/spec, **D** = documentation, **S** = server-touching.

---

## Core definitions

*These definitions override any conflicting language elsewhere in the pack. The bead store is the source of truth; the filesystem is a cache.*

- **Brief.** A brief is a **bead** that is in exactly one of two adjudication states: **adjudicated** or **not adjudicated**. It is attached to another bead or collection of beads — its **source** — via bead dependencies.
- **Source.** The bead(s) whose disposition the brief exists to decide. Every brief bead links its source(s) through the dependency graph (`bd dep` / `--deps`); a brief with no source link is malformed (B2.1).
- **Adjudication.** The event where Taylor (or authorized automation, see N-rules) renders a verdict on the brief. Adjudication ALWAYS produces a **decision bead** (`bd create -t decision`) attached to the brief bead. A brief is adjudicated **if and only if** a decision bead references it.
- **No-resurface invariant.** An adjudicated brief can NEVER resurface for presentation. A deferred brief cannot resurface within its defer window. Presenters filter mechanically on these conditions (B2.3, B2.7).
- **Pile.** The single fixed accumulation point for unadjudicated briefs. Canonical membership is a bead query, not a directory listing (B2.4, B2.8).
- **Decision bead.** A bead of type `decision` (existing `bd` type; see `bd help create -t` and `record-decision` skill). It records verdict, rationale, and authorizer, and is linked to the brief bead it adjudicates.

---

## Pillar 1 — Brief production (B1.x)

*A brief is a decision aid, not a report. Its purpose is to give Taylor exactly enough structured context to answer one question, in one session, without asking follow-up questions.*

- **B1.1 Decision-at-Top INVARIANT.** The first content after the artifact header MUST be "What is being decided." Not origin. Not mathematics. Not timeline. Not required gates. The decision. Every downstream section is evidence for the decision; the question is the anchor. A brief that opens with anything else is rejected before deposit — `brief-prep` self-rejects, `create-brief` refuses to write the file. In-conversation terminal dumps (`present-it`) have no auto-rejector, but the same rule applies and violating it is a skill failure.
- **B1.2 One decision per brief.** A brief routes one artifact to one decision. Splitting concerns ("we need to decide A and also B") → two briefs. A brief that bundles two unrelated decisions cannot be adjudicated atomically.
- **B1.3 Compact form is gated, not default.** Compact form (`DECISION / CONTEXT / RECOMMEND / CONFIRM`) is allowed ONLY when ALL four conditions hold simultaneously: (a) `catch-no-brainer` returned `no_brainer: true` with `compact_eligible: true`; (b) `server_touching = false` (G5); (c) `user_skill_touching_override = false` (G5b); (d) shape is NOT `capability-blocker`. If any condition fails → full-form (7 sections per `present-it` §"Full-form template"). Capability-blocker shapes always force full-form and route via the capability-resolution path before re-classification. Note: under N5 (revised), a compact-eligible brief normally does not surface at all — it auto-executes. Compact form is the presentation shape used when a compact-eligible brief must surface anyway (kill switch engaged, or stop gate fired late).
- **B1.4 All 16 gates must have evidence or N/A.** Every gate in the `standard` profile (G1–G16, G5b) must appear in the brief with either evidence or an explicit N/A plus a one-sentence reason. A gate with no entry at all is a mechanical failure. Gates that don't fire (e.g., G6 LaTeX-gate on a non-LaTeX artifact) must still appear as N/A.
- **B1.5 Measure twice, cut once — no follow-up questions.** All evidence, context, and gate results are assembled BEFORE the brief reaches Taylor. **A brief that requires a follow-up question from Taylor is a pipeline failure**, recorded as a regression against the producing skill (same severity class as N6). Mechanical check: the brief contains no unresolved "Open question", "TBD", or "for grilling" item at deposit time — every open question is either resolved with evidence, converted into a defer recommendation, or the brief self-rejects back to preparation. Pattern reference: `bead-flight-precheck` (the pre-sling go/no-go gate in `~/repos/agent-skills/skills/bead-flight-precheck/`), which shadow-runs every applicable gate and refuses SLING_READY while any gate lacks evidence. Brief production follows the same preflight discipline: assemble → gate-check → deposit; never deposit → ask → patch.
- **B1.6 External review gate G4 critical-review.** Every full-form brief passes through `critical-review` before deposit. The reviewer explicitly looks for: correctness risks, policy misses (P-rule or B/N/L/E/T/D/S-rule violations), missing evidence, and — per B1.5 — any question the brief would force Taylor to ask. A brief deposited without a G4 record → mechanical failure.
- **B1.7 Brief-record bookkeeping G8 is always required.** After deposit: the brief bead, its source links, the pile query, and the decision/archive records must remain consistent. A brief deposited without its bead record, or an adjudicated brief whose decision bead is missing, → G8 FAIL. (Filesystem manifest consistency is subordinate to bead consistency — see B2.8.)
- **B1.8 Test, experiment, LaTeX, and documentation evidence follow their own rule sets.** Test evidence → T-rules. Experiment design → E-rules. LaTeX surface → L-rules. README/documentation → D-rules. A brief citing "gates pass" without the specific rule-level evidence those sections require → the corresponding gate FAILs.

---

## Pillar 2 — Brief lifecycle, pile, and adjudication (B2.x)

*The bead IS the brief. Adjudication is a one-way door. The pile is ordered by what adjudication unlocks, not by arrival time.*

- **B2.1 A brief is a bead with a source link.** Every brief is materialized as a bead, linked to its source bead(s) via the dependency graph (e.g., `bd create --deps discovered-from:<source-id>` or `bd dep add`). Mechanical check: `bd show <brief-id>` lists at least one source dependency. A brief file with no corresponding bead, or a brief bead with no source link, is malformed and cannot enter the pile.
- **B2.2 Adjudication attaches a decision bead.** Rendering a verdict on a brief REQUIRES creating a decision bead (`bd create -t decision`, via the `record-decision` skill) linked to the brief bead, recording: verdict (approve/revise/reject/defer), rationale, authorizer (Taylor, or the automation identity for N-rule auto-execution), and date. Mechanical check: adjudicated ⇔ a decision bead references the brief bead. A verdict recorded only in conversation, only in `decisions.jsonl`, or only in a markdown file is NOT an adjudication (those channels remain required as redundancy per decision-recording discipline, but the decision bead is the canonical record).
- **B2.3 No resurface after adjudication — EVER.** Once a brief has a decision bead attached, it can never be presented again. `present-briefs` and any pile-reading skill MUST filter out beads with attached decision beads before presenting. Re-presenting an adjudicated brief is a pipeline failure of the same class as N6. If circumstances change after adjudication, the remedy is a NEW brief bead (linking the old brief and its decision bead as sources), never reopening the old one.
- **B2.4 One fixed pile.** Unadjudicated briefs accumulate in exactly one pile. Canonical membership is the bead query: open brief beads with no attached decision bead and no active defer window. There are no side-piles, per-agent piles, or "urgent" bypass piles; urgency is expressed through ordering (B2.5), not location.
- **B2.5 Ordering = unlock count.** Briefs are ordered for presentation by industrial-engineering priority: `priority(brief) = unlock_count` — the number of downstream beads that adjudicating this brief unblocks (transitively, via the dependency graph). Largest-unblock first (Goldratt: subordinate to the constraint; the constraint is Taylor's decision budget). Ties break by bead priority field, then age (oldest first). Mechanical check: the presenter computes unlock_count from `bd dep` data at presentation time and records the computed ordering in the docket. References: bd memories `industrial-engineering-dispatch-principles` (principle 5) and `review-order-by-unlock-count`.
- **B2.6 Clump like a court docket.** Similar briefs (same source repo, same rule family, same decision shape) are presented as ONE docket/cohort artifact rather than dripped one at a time indefinitely. Threshold: when ≥3 pile briefs share a natural cluster, the presenter MUST produce a cohort docket (cohort-reassemble pattern). Cohort verdicts may split per-item ((E)-hybrid/MIXED shapes are expected); each item still gets its own decision bead per B2.2.
- **B2.7 Defer is first-class and timed.** Taylor may skip any presented brief and defer it for X days, with X specified by Taylor at defer time. Implementation: `bd defer <brief-id> --until=+Xd --reason="..."`. A deferred brief (a) leaves the presentable pile immediately, (b) CANNOT reappear until the defer window expires, and (c) counts toward the no-resurface rule within its window — presenting a deferred brief before expiry is a B2.3-class failure. On window expiry the brief re-enters the pile with unlock_count recomputed. Defer is not adjudication: no decision bead is created for a defer unless Taylor asks for one.
- **B2.8 Artifact root is the bead.** ALL brief state — adjudication status, decision bead reference, source links, defer state, gate evidence pointers — lives in the bead store. The `.beads/briefs/` filesystem layout (pile/stack/manifest files, archived .md briefs) is an implementation detail and cache; it may be regenerated from bead state at any time. On any disagreement between filesystem and bead store, the bead store wins and the filesystem is repaired to match. Mechanical check: every lifecycle transition (deposit, present, defer, adjudicate, archive) is expressed as a bead operation first; file moves are derived.
- **B2.9 Auto-executed briefs are still adjudicated.** No-brainer auto-execution (N-rules) is an adjudication: it creates a decision bead (authorizer = the automation identity + classifier evidence) attached to the brief bead, and the brief then falls under B2.3 no-resurface like any other adjudicated brief. Auto-execution with no decision bead → G8 FAIL.

---

## Pillar 3 — Work closure discipline (B3.x)

*A bead is not closed until the work is verifiably done. Closing early to make a dashboard green is worse than leaving it open. Some beads must never be closed at all.*

- **B3.1 Closure requires verifiable acceptance.** Before calling `bd close`, the polecat must confirm at least one of: (a) acceptance criteria in the bead description are individually checked off, (b) a linked test passes, (c) a `critical-review` verdict says PASS, or (d) Taylor has explicitly said "close it." Closing on vibes → fail.
- **B3.2 Server-touching items require Taylor OK before close, not after.** A bead tagged `TAYLOR_OK_REQUIRED` or `server-touching` cannot be closed by a polecat without recorded explicit Taylor authorization (a decision bead per B2.2, plus the redundant channels: `decisions.jsonl` entry, inline plan annotation, or session statement). Closing first and noting the Taylor-OK-needed status later → policy violation.
- **B3.3 Downstream beads must not be orphaned on close.** Before closing a bead, check: does any open bead list this as a dependency? If so, the dependency is satisfied — but the downstream bead's metadata must be updated to mark this dep closed. Closing without checking downstream → G8 FAIL (bookkeeping).
- **B3.4 Cross-repo work self-closes.** When a polecat ships work that spans repositories (e.g., a hecke bead whose commit touches `~/repos/hecke` and `~/repos/gascity-packs`), the polecat self-closes the work-bead on completion. Do NOT reassign to refinery or wait for Mayor to close. The work-bead is the polecat's responsibility from claim to close.
- **B3.5 Convoy close requires all members closed.** An owned convoy (`gc convoy create --owned`) is only eligible for `gc convoy land` when ALL member beads are in a terminal state (CLOSED or superseded). A convoy landed with open members is a silent data loss — the open members lose their convoy context.
- **B3.6 The all-closed check is never skipped for brief auto-merge.** No-brainer automation must check that all beads in scope are closed before executing. The phasemapping bug (text-scanning bead descriptions for "blocked") is a known regression surface — all closure checks must be against status values, not text content.
- **B3.7 Research beads are NEVER closed destructively.** Two subtypes exist (see BEADPOLICY.md BP2): (a) **Math research** — original mathematical work (proofs, derivations, examples); these are `type: task` or `type: feature` with label `[RESEARCH_JOURNAL]`; math research is NEVER `type: spike`. (b) **Technical investigation** — code/infrastructure research (spike beads with `[RESEARCH_JOURNAL]`). In both cases, once the work contains extended notes/history without actionable remaining criteria, it must never be transitioned to CLOSED. The correct terminal state is **ARCHIVED** (upstream feature request pending). **Interim protocol:** (a) label the bead `[RESEARCH_JOURNAL]`, (b) protect it with `bd defer <id> --reason="research journal — ARCHIVED-equivalent, do not close"` so it leaves `bd ready` but stays in `bd list`. Mechanical check: any `bd close` targeting a `[RESEARCH_JOURNAL]`-labeled bead → policy violation; sweepers, convoy landers, and no-brainer executors must exclude such beads. See BEADPOLICY.md BP2 for the full math/tech distinction. Note: `type: research-journal` is not a real bd type — P5.3 violation.
- **B3.8 Adjudicated briefs close through their decision bead.** Closing a brief bead without an attached decision bead is a B2.2 violation. The close reason must reference the decision bead ID.

---

## Pillar 4 — Magma package update discipline (B4.x)

*package-certify.mag and its siblings are production artifacts. Changes to them propagate to every hecke certify run. The standards are accordingly higher than for test scripts.*

- **B4.1 Proto-intrinsics must be promoted before the handoff bead closes.** An intrinsic that exists only in a test script (`test-*.mag` or `make/one-offs/`) is a proto-intrinsic. It must be promoted into its appropriate package (`package-certify.mag`, `package-LMFDB.mag`, etc.) before the implementing bead closes. A handoff bead whose intrinsics are still in test scripts is not done.
- **B4.2 Dead code is removed at promotion time.** When a new algorithm (e.g., cyclic sweep) replaces an old one (e.g., CSP solver, Approach A pre-screen), the old code is removed in the same commit that adds the new code. Leaving the old code behind for "reference" creates drift — the production path and the legacy path coexist, and the next polecat won't know which is current. Exception: the old code is labeled `// legacy: kept for offline diagnostics` and tracked by a follow-up cleanup bead.
- **B4.3 README coverage after every intrinsic change.** Any commit that adds, renames, or removes a public intrinsic from a `package-*.mag` file fires the documentation rules D1–D3 (improve-package-README, G10/G15). See the Documentation policy below; the pass/fail criteria live there.
- **B4.4 Four certify gates on every repaired record.** Any gamma0 record modified by a repair script must pass all four certify gates before the repair bead closes:
  - `certify_gamma0_stored_matrix_presentation`
  - `certify_gamma0_presentation`
  - `certify_defining_element_canonical`
  - `certify_subgroup`
  Passing only a subset and closing → B3.1 FAIL (acceptance criteria not met).
- **B4.5 Offline-only intrinsics are labeled or retired.** An intrinsic used only in `make/one-offs/` or `test-*/` diagnostics (never called from production `make/` scripts) must be either (a) labeled with a `// offline-only diagnostic` comment, or (b) retired in a cleanup bead. Unlabeled offline intrinsics accumulate as dead weight and confuse the next polecat. The retirement decision is tracked as a separate bead (not bundled into a production repair bead) so it can be deferred without blocking.
- **B4.6 Package changes go through a brief.** Any change to a `package-*.mag` file that adds or modifies an intrinsic used in production certify/repair pipelines requires a brief before the PR opens. The brief covers: what the intrinsic does, test evidence (T1 + T6), and the README gate (D1). Direct commits without a brief → pipeline bypass.

---

## No-brainer policy (N-rules)

*No-brainers are briefs a skilled reviewer would approve without hesitation given only the compact 4-line summary. They exist to clear low-stakes queue items without consuming Taylor's decision budget. Automation is ON by default; the kill switch is a brake, not a parking brake.*

- **N1 Classification is catch-no-brainer's job, not the polecat's.** A polecat must not self-classify a brief as a no-brainer. Every brief goes through `catch-no-brainer` before the compact/full-form branch. A polecat that skips this step and emits compact form or auto-executes → N1 FAIL.
- **N2 Four eligible categories (cat-A/B/C/D).** No-brainer classification requires the brief to fall into one of four clean categories:
  - cat-A: trivially correct mechanical change (e.g., rename, format)
  - cat-B: revert of a known-good prior state
  - cat-C: delete of confirmed-superseded artifact
  - cat-D: bookkeeping/metadata update with no code path impact
  Any artifact outside these four categories → not a no-brainer → full-form pile entry. Classification must also be **confident**: `catch-no-brainer` emits a confidence field; anything below its confident threshold → full-form.
- **N3 Stop gates trump classification.** G5 server-touching (S-rules) and G5b user-skill-touching (any change to `~/.claude/skills/` or `~/repos/agent-skills/skills/`) block auto-execution and compact form regardless of cat classification. `catch-no-brainer` must emit `server_touching: true` or `user_skill_touching_override: true` when these surfaces are in scope. L4 (notes.tex / LaTeX-bearing surfaces) is likewise a stop condition.
- **N4 Capability-blocker shape routes to resolution, not compact.** If `catch-no-brainer` identifies a `capability-blocker` shape (the brief cannot proceed because a required capability is missing), the brief must route through the capability-resolution path first. Resolving the blocker, then re-classifying, is the protocol — NOT emitting compact form with a blocker note.
- **N5 Auto-execute is the DEFAULT; kill switches are safety brakes.** *(Revised — supersedes the previous fail-closed rule.)* When `catch-no-brainer` returns a confident cat-A/B/C/D classification AND all stop gates pass (N3, N4, plus the applicable `no_brainer` gate profile in `gates.toml`), the brief auto-executes via `gc sling` WITHOUT surfacing to Taylor, and is archived per B2.9 (decision bead + no-resurface). **Kill switch hierarchy (two levels):** automation runs unless a kill switch is ENGAGED at either level — city-wide takes precedence, then rig-level. Engaging or releasing a kill switch requires explicit Taylor authorization, recorded as a decision bead.
  - **City-wide switch** (`~/gt/.beads/auto_merge_enabled`): if this file exists and reads `false`, ALL rigs halt auto-execution. Absent or `true` → proceed to rig check.
  - **Rig-level switch** (`<rig_root>/.beads/auto_merge_enabled`): if this file exists and reads `false`, that rig halts auto-execution. Absent or `true` → automation active for that rig.
  - Executor check order: (1) read city-wide flag; if `false` → halt; (2) read rig flag; if `false` → halt; (3) execute. A halted no-brainer routes to the pile in compact form (not dropped silently).
  NOTE: `gates.toml` G12 currently states fail-closed semantics; that gate description must be updated to match this rule — tracked as a follow-up bead. Until then, skills follow THIS policy (POLICY.md is authoritative for semantics; gates.toml for gate inventory).
- **N6 Surfacing a no-brainer at Taylor is a regression.** If a brief reaches the human-review layer (clerk presents to Taylor) and Taylor's immediate reaction is "this is obvious, why am I seeing it?" → that is a catch-no-brainer regression, not a scheduling slip. The fix is in the classifier prompt or category definitions, not in asking Taylor to accept more noise.
- **N7 Auto-execution leaves a full audit trail.** Every auto-executed no-brainer must have: the classifier output (category, confidence, stop-gate flags) staged as evidence, the decision bead (B2.9) naming the automation as authorizer, and the archive record. Missing any element → G8 FAIL. Taylor can audit the auto-executed stream at any time; an unauditable auto-execution is grounds for engaging the kill switch.

---

## LaTeX policy (L-rules) — gate G6

*Mathematical prose is a production surface. The LaTeX gate exists because a wrong sign in notes.tex outlives every session that touched it.*

- **L1 What fires the LaTeX gate.** G6 fires when the artifact adds or modifies: (a) any `.tex` file (including `notes.tex` and paper sources), (b) rendered mathematical statements destined for papers, notes, or LMFDB knowls, (c) mathematical definitions/theorems/proofs in any format that downstream documents will cite. Mechanical check: diff touches `*.tex`, OR the brief declares mathematical-prose content. If G6 fires, the brief cannot be compact-form and cannot auto-execute (N3).
- **L2 What does NOT require LaTeX.** Code comments, commit messages, plain markdown without mathematical claims, gate evidence, bead bodies, and README prose that describes tooling (not mathematics) do not fire G6. In these cases the brief records G6 as N/A with the explicit surface check: "no `.tex` diff, no mathematical-prose content" (one sentence). A silent missing G6 entry → B1.4 FAIL.
- **L3 How the gate is satisfied.** A fired G6 requires BOTH: (a) mechanical evidence — the touched LaTeX compiles (compiler command + exit code + date, same format as T1), and (b) review evidence — a `check-latex` (or equivalent reviewer) verdict on mathematical correctness of the changed statements, naming the reviewer. Compile-only or review-only → G6 FAIL. The runnable check `latex-gate-approval-required.sh` enforces presence of the G6 record.
- **L4 notes.tex changes are never no-brainers.** Changes to a repo's primary mathematical documentation (`notes.tex` convention) always route full-form to Taylor regardless of size — a one-character sign change is exactly the case the gate exists for. `catch-no-brainer` must treat `notes.tex` (and paper `.tex`) diffs as a stop condition equivalent to N3.

---

## Experiment policy (E-rules)

*An untestable claim is not a result. An experiment without a falsifiable question wastes compute.*

- **E1 Every experiment has exactly one falsifiable question.** A goal ("explore X"), a wish ("understand Y"), or a description ("run Gamma0_fp on order O") is not a question. A question has possible answers. "Does `Gamma0_fp` cost scale linearly in `coprime_pairs(n)`?" is a question. Missing → `is-good-experiment` Checkpoint 1 REJECT, experiment does not run.
- **E2 Both outcomes must be interpreted.** For any experiment question, the brief or proposal must state: what Taylor learns if the answer is YES, and what Taylor learns if the answer is NO. An experiment whose NO outcome is uninterpreted is a confirmation trap — it can only confirm, never refute. Single-outcome proposals → `is-good-experiment` Checkpoint 2 BLOCKING → NEEDS-REVISION.
- **E3 Coverage must support an inferential leap.** A single data point rarely allows a general conclusion. An exhaustive sweep is rarely the cheapest way to answer a coverage question. The proposal must state why the chosen coverage (which inputs, which orders, which levels) is the smallest set that would let Taylor conclude something about the general behavior. Over-narrow and over-broad are both checkable failures (Checkpoint 3).
- **E4 Cost estimate is required for long-running experiments.** Any experiment expected to take more than 30 minutes wall time on the target machine must include a resource estimate (wall time, RAM, disk for outputs). Missing estimate on a long-running experiment → Checkpoint 4 MAJOR. Short-term experiments may omit detailed estimates.
- **E5 Two pitfalls are always checked.** The `is-good-experiment` reviewer MUST explicitly evaluate:
  - **Not loading data.** Does the proposal name every data dependency and how it is loaded? (`AttachSpec`, `SetLMFDBRootFolder`, `load_*` calls.) Missing → Checkpoint 5 flag.
  - **Slow route of computation.** Does the proposal state which intrinsics it calls and why those are the right ones (not a generic fallback)? Failing to use a cached result, calling a quadratic helper inside a loop, or defaulting to a full recompute when a fast path exists → flag.
- **E6 Unrunnable experiments are not silent.** If an experiment cannot run (no Magma, missing DATA/, timeout too short, environment mismatch), the polecat reports `UNRUNNABLE` with the reason, obtains a `critical-review` verdict that confirms the conclusion from static evidence, and deposits a brief with that evidence. An experiment that silently fails and produces no brief → G7 FAIL (no artifacts staged). Deferred or abandoned experiments leave a durable breadcrumb (D4/G11).
- **E7 Experiment results feed research beads, not the void.** Experiment outputs with interpretive value (logs, tables, negative results) are attached to a research bead or the source bead's notes; research beads so created fall under B3.7 protection (ARCHIVED, never destructively closed).

---

## Testing & spec policy (T-rules)

*"Tests pass" is not evidence. Evidence is a command, a scope, an exit code, and a date.*

- **T1 Gate G1 test-evidence is non-optional.** Any claim about tests must include: the exact command run, the scope (files/functions tested), the result (exit code + first 200 lines or summary), and the date. Missing any element → G1 FAIL → brief cannot be deposited. "Tests pass" with no command or output is not evidence.
- **T2 Gate G16 base-ref required.** Test evidence that depends on `main`/`master` state must record the exact base commit (`git rev-parse HEAD` in the target repo at test time). Test evidence with no base ref recorded is unverifiable as the repo moves → G16 FAIL.
- **T3 Unrunnable tests are declared, not skipped.** If a test cannot run in the current session (no Magma license, missing DATA/, requires aia-s27, etc.), the brief records the test file path, the reason it is unrunnable, and what surface-check evidence stands in (e.g., diff-read of the test + review of the intrinsic). "Did not run tests" with no further text → G1 FAIL.
- **T4 Test files name what they test.** A Magma test file (`test-*.mag`) MUST identify X — the intrinsic, function, or pipeline under test — in a header docstring or explicit annotation. `is-good-test` infers X from the file; if X cannot be identified, that is a Checkpoint 1 REJECT. Action: add a header docstring naming the intrinsic/function/pipeline.
- **T5 Test pass AND fail must both be meaningful.** A test where PASS means "something happened" and FAIL means "something went wrong" is a confirmation trap. The test must be designed so FAIL specifically indicates the named thing X is broken. Assert-by-accident (e.g., `nil eq nil` always true) is a Checkpoint 2 failure. A test that never fails is not a test.
- **T6 G2 good-test verdict required before merge.** Any brief proposing to merge code that adds or modifies tests must include a G2 good-test verdict on the new/modified test files, emitted by `is-good-test`. The G2 verdict is a review (not mechanical) — it must name the reviewer (session ID or polecat ID). A diff that adds test files without G2 evidence → G2 FAIL.
- **T7 Gate G14 tri-state declaration is never silent.** Every brief carries an explicit test-execution declaration: `PASSED` / `NOT APPLICABLE` / `REQUIRED`. Silent or absent declaration → auto-throwback (G14, source he-8akk). `NOT APPLICABLE` requires the one-sentence reason; `REQUIRED` means execution is owed before adjudication and the brief says by whom.

---

## Documentation policy (D-rules)

*Undocumented intrinsics and silent README skips are how the next polecat re-derives what this one already knew.*

- **D1 improve-package-README after every intrinsic addition.** Any commit that adds, renames, or removes a public intrinsic from a `package-*.mag` file requires a corresponding update to the `magma/test/README-tests/` coverage (gate G10). The `improve-package-README` skill is the executor. An intrinsic with no README-tests coverage → G10 FAIL.
- **D2 README evidence is never silent (G15).** The brief records either the applied README improvement (file + diff summary) or an explicit N/A with the reason "no README surface exists for this change." A missing entry → G15 FAIL.
- **D3 README update lands with the change.** The README-tests update lands in the same commit or the immediately following commit, tracked by the same bead as the intrinsic change. A README update parked in a separate untracked follow-up → D3 FAIL (it will be forgotten).
- **D4 Breadcrumbs for deferred and experimental work (G11).** Any experiment, deferred brief, or partially-landed work must leave a durable breadcrumb — in the bead (per B2.8), naming: the source, the staged artifacts, and the next owner. Work abandoned without a breadcrumb → G11 FAIL.

---

## Server-touching policy (S-rules)

*Server-touching work requires a separate authorization track because mistakes are slow to reverse, run on hardware Taylor doesn't control, and can corrupt live database state.*

- **S1 Definition.** Server-touching means any of: dispatching to `aia-s27`; writing to the `DATA/` directory tree; running `queue-repairs.sh` without `--dry-run`; running `make-recompute-gamma0-from-transversal.mag` with `I_HAVE_A_BACKUP=1`; adding an entry to `magma/make/dispatch/priority.conf`; any SSH-routed command that modifies server state. All other work (local Magma scripts, local test runs, bead updates, package edits) is NOT server-touching.
- **S2 Dry-run first, always.** Every server-touching sweep (classification, repair batch, recompute queue) must complete a successful dry-run pass before a non-dry-run dispatch is authorized. Dry-run output is staged under `~/gt/tmp-for-taylor/` and referenced in the brief.
- **S3 Smoke test before full batch.** Between the dry-run and any full-batch dispatch, a smoke test of 4 representative items (one per repair route) must be completed and presented as a Taylor gate. The smoke test brief must include all four certify-gate results per item. Taylor's explicit go/no-go is required before the batch.
- **S4 Per-item Taylor OK for each TAYLOR_OK_REQUIRED bead.** Taylor OK is not transitive. Authorizing the dry-run sweep does NOT authorize the recompute batch. Each TAYLOR_OK_REQUIRED bead in a convoy requires its own recorded authorization — a decision bead (B2.2) plus the redundant `decisions.jsonl` / inline-annotation channels.
- **S5 Long-running recomputes queue early.** Recompute jobs that take hours to days (full `Gamma0_fp(:redo:=true)`, RECOMPUTE_IQ via transversal on large orders) should be queued as early as possible so they run in parallel with code work. A bead that blocks the relabel step and has a multi-day recompute hidden inside it is a planning failure — queue it in its own bead immediately on identification.
- **S6 Recompute route: transversal beats full Gamma0_fp.** When a record has a stored transversal and the transversal recompute produces a clean result (under 1 second), the route is `RECOMPUTE_IQ` (transversal). Full `Gamma0_fp(:redo:=true)` is the fallback for records with no stored transversal. Proposing a full Gamma0_fp recompute for a transversal-eligible record is a planning error.
- **S7 Gate G5 stops server-touching work at the brief.** A brief whose artifact is server-touching must record `server_touching: true` in its frontmatter. No-brainer auto-execute is blocked (N3/N5) — server-touching is a stop gate that no confidence level overrides. The brief goes to full-form review and Taylor adjudication. A server-touching brief routed through compact form or auto-execution → G5 FAIL.

---

## Non-negotiables (quick checklist)

- A brief is a bead; adjudication attaches a decision bead; adjudicated briefs NEVER resurface (B2.1–B2.3).
- One fixed pile; ordering by unlock_count, largest-unblock first; ≥3 similar briefs → one docket (B2.4–B2.6).
- Defer is timed (`bd defer --until=+Xd`); deferred briefs stay hidden until expiry (B2.7).
- Canonical state lives in the bead store; files are cache (B2.8).
- Decision-at-Top: the first content after the artifact header MUST be "What is being decided" (B1.1).
- One decision per brief. Two decisions → two briefs (B1.2).
- No follow-up questions to Taylor — a brief that needs one is a pipeline failure (B1.5).
- No-brainer auto-execute is ON by default for confident cat-A/B/C/D past all stop gates; kill switch = file present AND `false` (N5); every auto-execution leaves a decision bead + audit trail (N7/B2.9).
- Stop gates G5 (server), G5b (user-skill), L4 (notes.tex/LaTeX) override any classification (N3).
- G1 evidence = command + scope + exit code + output + date; G16 base-ref; G14 tri-state never silent (T1/T2/T7).
- Unrunnable tests/experiments are declared, not skipped (T3/E6).
- External review G4 on every full-form brief before deposit (B1.6).
- Closure requires verifiable acceptance, not vibes (B3.1); TAYLOR_OK_REQUIRED needs recorded authorization BEFORE close (B3.2).
- Research beads are NEVER destructively closed — ARCHIVED (interim: `[RESEARCH_JOURNAL]` label + `bd defer`) (B3.7).
- Convoy landing requires all members terminal (B3.5).
- Proto-intrinsics promoted before handoff bead closes (B4.1); dead code removed at promotion (B4.2).
- improve-package-README after every intrinsic addition, never silently skipped (D1/D2).
- Server-touching: dry-run → smoke test → per-item Taylor OK → batch (S2–S4); transversal route preferred (S6).
- LaTeX gate: compile evidence + reviewer verdict, both (L3); notes.tex never a no-brainer (L4).

---

## Verdict vocabulary

Reuses the brief-cycle Decision vocabulary — no parallel vocabulary introduced. Every verdict except defer is an adjudication and creates a decision bead (B2.2).

- **approve** — all applicable rules pass; brief or work item is clean to proceed (gates all have evidence or explicit N/A). Decision bead created; brief archived; no resurface.
- **revise** — fixable violations; the decision bead names the specific rule(s) broken, the artifact that triggered each, and a compact brief that seeds the fix. The REVISED artifact returns as a NEW brief bead (linked to the old brief + decision bead) — the original brief does not resurface.
- **reject** — the approach itself violates a rule with no workaround (e.g., server-touching without authorization; experiment with no falsifiable question). Decision bead created; send back for a different approach via a new brief.
- **defer** — Taylor skips the brief for X days (Taylor specifies X). NOT an adjudication: implemented as `bd defer --until=+Xd`; no decision bead unless requested; the brief re-enters the pile after expiry (B2.7).

---

## Upstream requests and known drift

- **ARCHIVED lifecycle state** — file an upstream `bd` feature request for a first-class ARCHIVED status (not actionable, not dispatchable, permanently searchable) for research-journal beads; tracked as its own bead. Interim protocol in B3.7.
- **gates.toml G12 wording** — currently states fail-closed automation semantics; must be revised to the N5 default-ON / kill-switch-as-brake semantics. Tracked as a follow-up bead. Until updated, this POLICY.md governs semantics.

---

## References

- `mathcity/assets/brief-pipeline/gates.toml` — G1–G16 + G5b gate registry (source of truth for gate IDs and profiles: `standard`, `no_brainer`, `test_execution`)
- `mathcity/skills/brief-prep/SKILL.md` — end-to-end brief pipeline procedure
- `mathcity/skills/catch-no-brainer/SKILL.md` — no-brainer classifier (categories, confidence, capability-blocker, stop-gate flags)
- `mathcity/skills/create-brief/SKILL.md` — brief producer (frontmatter schema, gate slots)
- `mathcity/skills/present-it/SKILL.md` — terminal context dump producer (Decision-at-Top INVARIANT, full-form template, compact form conditions)
- `mathcity/skills/present-briefs/SKILL.md` — pile presenter (must implement B2.3 no-resurface filter, B2.5 unlock-count ordering, B2.6 docket clumping, B2.7 defer)
- `mathcity/skills/record-decision/SKILL.md` — decision bead creator (`bd create -t decision`; B2.2 executor)
- `mathcity/skills/is-good-experiment/SKILL.md` — 6-checkpoint experiment reviewer (E-rules)
- `mathcity/skills/is-good-test/SKILL.md` — test-design reviewer (T4/T5/T6)
- `mathcity/skills/critical-review/SKILL.md` — G4 reviewer
- `~/repos/agent-skills/skills/bead-flight-precheck/SKILL.md` — the preflight pattern referenced by B1.5 (assemble → gate-check → go/no-go, read-only and advisory)
- `bd help create`, `bd help defer` — decision bead type (`-t decision`) and timed defer (`--until`) primitives this policy builds on
- bd memories: `industrial-engineering-dispatch-principles` (pull-not-push, priority = unlock_count, poka-yoke binary checks, scrap policy), `review-order-by-unlock-count`, `decision-recording-discipline`, `no-brainers-auto-execute`, `cohort-reassemble-pattern`
- `mathcity/subdomains/dev/POLICY.md` — P-rule set for pack portability and boundary discipline (G5 server-touching is downstream of those P-rules; this file governs the brief-pipeline expression of that constraint)
- `he-xkq3` (bead) — the live hecke gate registry that `gates.toml` was derived from; consult for hecke-specific gate calibration decisions
