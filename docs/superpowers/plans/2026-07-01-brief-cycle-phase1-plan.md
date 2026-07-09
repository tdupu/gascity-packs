# Brief Cycle Phase 1: Close the Loop — Implementation Plan

Spec: `docs/superpowers/specs/2026-07-01-brief-cycle-close-the-loop-design.md`
Glossary: `CONTEXT.md` (repo root)
Beads: gsp-56v, gsp-zk9, gsp-ijf, gsp-p2a, gsp-aq9 (this repo's rig workspace)

## Global Constraints

- Work happens in `~/repos/gascity-packs` on branch `close-the-loop-phase1`.
- **Never modify files under `gastown/`** — that pack syncs from upstream
  gastownhall; local changes there create divergence. Extend behavior via the
  mathematics pack (formulas, orders, `[[patches.agent]]` in pack.toml) or
  the gascity pack (which is locally owned).
- packv2 well-known directories only: `agents/`, `formulas/`, `orders/`,
  `skills/`, `assets/`, `template-fragments/`. Do not invent new top-level
  machine-readable directories (pack-spec rule).
- Beads are NOT brief-worthy by default. Only beads labeled `needs-decision`
  generate brief-records (HQ decision gt-eaia).
- Approval = merge: an approve decision reassigns the source bead to the
  owning rig's refinery using the metadata contract (`branch`, `target`
  metadata fields; reassign to refinery) — HQ decision gt-r4ou.
- Escalations: `bd human` bead; priority P0/P1 → immediate ping (gc mail +
  macOS osascript notification); P2+ accumulate (HQ decision gt-3x2d).
- Paths inside pack scripts must NOT hard-code `/Users/tdupuy/...`; resolve
  relative to the script's own location or via environment (GC_* vars).
  (Existing scripts violate this — do not copy the pattern; fixing old
  scripts is out of scope, Phase 2.)
- Validation gates for every task: `gc lint <pack-dir>` passes on each
  touched pack; existing tests under `tests/` still pass; new behavior gets
  a test where the repo's existing test idiom supports it (pytest under
  `tests/`).
- Formula/order TOML must parse: validate with `gc lint` (it validates packs
  including formulas/orders).

## Task 1: Expose gc.review-synthesizer and gc.run-operator as packv2 agents

**Bead:** gsp-56v. **Problem:** the gascity pack keeps 12 agent definitions
under `gascity/roles/agents/` — not a packv2 well-known directory — so the
formula-v2 resolver cannot see them and `gc order run brief-present-next`
fails with `unknown formulas v2 target gc.review-synthesizer`.

**Requirements:**
1. Create `gascity/agents/review-synthesizer/` and
   `gascity/agents/run-operator/` (the two agents mathematics formulas
   target). Salvaged uncommitted files from the dead polecat exist at
   `~/gt/gascity-packs/gascity/agents/review-synthesizer/{agent.toml,prompt.template.md}`
   — copy them in as the starting point for review-synthesizer; review the
   content, especially that agent.toml is v2-shaped (`agents/<name>/agent.toml`
   layout). Note: `fallback = true` is a removed mechanism (compatibility:
   stale `fallback` in v2 agent.toml is ignored; keep or drop accordingly —
   prefer drop).
2. For run-operator, derive `agents/run-operator/` from
   `gascity/roles/agents/run-operator/` content, adapted the same way.
3. Leave `roles/` untouched (other tooling references it; deprecation is
   out of scope).
4. Verification: `gc lint gascity/` passes; grep confirms
   `agents/review-synthesizer/agent.toml` and
   `agents/run-operator/agent.toml` exist and parse. If a fast local check
   for target resolution exists (e.g. `gc formula` subcommands), run it;
   otherwise lint + layout is the gate (live order-run happens later in the
   HQ smoke test, not this task).

## Task 2: Refinery post-merge hooks via mathematics pack (no gastown edits)

**Bead:** gsp-zk9. **Problem:** refinery merges and closes beads but never
files brief-records or wakes the brief pipeline; result: decided/finished
work exits the system silently and briefs never get created for
decision-worthy beads.

**Requirements:**
1. Investigate `[[patches.agent]]` (pack-spec §pack.toml) as the mechanism
   for appending post-merge duties to the gastown refinery agent's prompt
   from the mathematics pack. If patches support prompt fragments
   (`append_fragments`/`inject_fragments`), add a
   `mathcity/template-fragments/refinery-post-merge.md` fragment and the
   patch stanza in `mathcity/pack.toml`. If agent patches cannot carry
   this, fall back to a `mathcity/orders/on-merge-brief-record.toml`
   condition/event order that watches for freshly closed beads with the
   `needs-decision` label.
2. The post-merge duty, precisely: after a successful merge of bead X —
   (a) ensure X is closed (existing behavior);
   (b) IF X carries the `needs-decision` label: create a brief-record bead
       in X's rig titled `[brief-record] <X-id> <short title>` with
       metadata linking X, and touch the brief-prep pipeline (create the
       brief-prep work bead per the existing brief-prep formula's intake
       convention — read `mathcity/formulas/brief-prep.toml` for what it
       expects as source);
   (c) IF X is unlabeled: do nothing extra.
3. A pytest under `tests/` covering the decision logic if it lands as a
   script; if it lands purely as prompt fragment + order TOML, the gate is
   `gc lint mathcity/` + a test of any helper script added.
4. Verification: `gc lint mathcity/` passes; tests pass.

## Task 3: brief-decision-dispatch (approval=merge back edge)

**Bead:** gsp-ijf. **Problem:** decisions recorded in `decisions.jsonl` are
terminal; nothing dispatches follow-on work.

**Requirements:**
1. First salvage: `git fetch fork && git log fork/polecat/gsp-xhc` — commit
   `8631612` ("event-driven file-or-sendback post-decision gate" +
   `tests/test_file_or_sendback_routing.py`, 251 lines). Cherry-pick it onto
   the branch; resolve conflicts; keep its tests. Review what it already
   covers — it may implement much of the routing.
2. End state on top of the salvage:
   - `mathcity/formulas/brief-decision-dispatch.toml`: given a decision
     record (slug, decision, source bead id), route:
     approve → set `target` metadata (default branch) on the source bead if
     missing and reassign the bead to the owning rig's refinery session
     (metadata contract per gastown polecat prompt: update `branch`,
     `target`, reassign); reject/revise → create a follow-up bead in the
     source rig carrying the decision reason; defer → no-op beyond marking
     the record dispatched.
   - `mathcity/orders/brief-decision-dispatch.toml`: fires when
     undispatched decision records exist. Prefer `trigger = "event"` with a
     decision event if `brief-record-decision.toml` can emit one (check
     whether a `gc event` emit is available to formula steps); otherwise
     `trigger = "condition"` with a check script comparing `decisions.jsonl`
     entries against a dispatched ledger file
     (`.beads/briefs/decisions-dispatched.jsonl`). The check script lives in
     `mathcity/assets/scripts/` and must not hard-code absolute paths.
   - Update `mathcity/formulas/brief-record-decision.toml` minimally if
     needed to mark records dispatchable (do not restructure it).
3. Idempotency: dispatching the same decision twice must be a no-op
   (ledger check). Cover this in a pytest.
4. Verification: `gc lint mathcity/`; pytest suite passes including the
   salvaged `test_file_or_sendback_routing.py` and the new idempotency test.

## Task 4: Escalation helper (bd human + P0/P1 ping)

**Bead:** gsp-p2a.

**Requirements:**
1. `mathcity/assets/scripts/escalate.sh`: takes `--title`, `--body`,
   `--priority` (0-4), `--rig` (optional; default current). Creates a bead
   (`bd create --type=task --priority=N` + `bd human <id>` flag — check `bd
   human --help` for the exact flagging idiom), then if priority ≤ 1: sends
   `gc mail send` to the human/overseer alias AND fires a macOS
   notification via `osascript -e 'display notification ...'`. Priority ≥ 2:
   bead only. No absolute paths; executable bit set.
2. `mathcity/template-fragments/escalation-protocol.md`: a short
   fragment telling agents when to escalate and the P0/P1 bar ("stalled
   work wastes running compute or blocks a chain"), referencing the script
   by pack-relative path. Wire the fragment into the mathematics pack's
   agent prompts where formulas' judgment steps can fail
   (`codex-worker` prompt at minimum) and mention it in the brief-prep
   formula's coordinate-review step description (one-line addition).
3. Pytest (or bats-style shell test consistent with existing test idiom)
   for the script's priority branching — mock `bd`/`gc`/`osascript` with a
   PATH shim; assert P1 pings and P2 does not.
4. Verification: `gc lint mathcity/`; tests pass; `shellcheck` clean if
   shellcheck is available (skip silently if not installed).

## Task 5: brief-present-next drain-mode

**Bead:** gsp-aq9. **Depends on Task 1** (review-synthesizer must exist as a
resolvable target).

**Requirements:**
1. Rework `mathcity/formulas/brief-present-next.toml`: one run drains ALL
   pending stack briefs instead of selecting exactly one. Iterate the
   manifest queue (`stack/manifest.jsonl`) in unlock order; for each brief:
   no-brainer-classified entries render as one-line items in a single
   consolidated presentation; full briefs render via the existing
   grill-and-present/present-it step description. Presentation records
   written per brief as today.
2. The order `mathcity/orders/brief-present-next.toml` stays
   `trigger = "manual"` (accumulate-and-drain UX per HQ decision gt-3x2d).
   Update its description to say "drains all pending briefs".
3. Do not change gate semantics, shuffle, or decision recording.
4. Verification: `gc lint mathcity/`; any manifest-iteration helper
   script gets a pytest with a fixture manifest (mixed no-brainer + full
   briefs) asserting the drain order and grouping.
