# Pack Portability & Boundary Policy

| Field | Value |
| --- | --- |
| Status | Adopted |
| Date | 2026-07-10 (amended same day: P1.9–P1.11, from the hecke-adoption / server-skills / bead-sync incidents) |
| Decided | Taylor Dupuy, via grilling session (three open questions resolved; record at bottom) |
| Applies to | All packs Taylor owns in this repo — the **owned pack set** (§ Scope) |
| Consumers | `check-hygiene` skill (to be built via skill-creator); mayor priming (`mayor-math`); any agent planning work in this repo |

Governs how work on an owned pack is planned, executed, and audited inside
`gascity-packs` — and, more broadly, how the whole local gascity install
(`gc`/`bd` binaries, pack content, city config) stays **reproducible on a
fresh machine, shareable with collaborators, and mergeable with upstream**.
Written as the source-of-truth for a plan/convoy/audit gate: every rule has
an ID and a pass/fail criterion a skill can cite.

## Scope

**Owned pack set** (the directories these rules call "yours"):

- `mathcity/` and every nested child pack under it — currently
  `mathcity/subdomains/{brief-system,computing,proof-assist,latex,lmfdb}/`
  (per [ADR 0002](../../../docs/adr/0002-mathcity-subdomain-pack-model.md)).
- Any future pack Taylor creates in this repo, added by amending this list.

The `check-hygiene` skill takes the owned-pack roots as input; it does not
hardcode `mathcity/`.

**Input shapes** — the same four pillars apply to all three:

1. **Plan doc** — checked on its stated file/dir touches and import changes.
2. **Beads convoy** — checked per-bead on each bead's declared scope, plus
   one whole-convoy aggregate pass (a convoy can violate Pillar 4 in
   aggregate even when each bead looks clean).
3. **Current-state audit** — the live repo/city/binaries checked directly
   against the P-rules (is what's running now re-derivable and shareable?).

## Pillar 1 — Reproducibility & portability

*A fresh install must reproduce your city; a collaborator must be able to
recreate what you're running; upstream must remain pullable.*

- **P1.1 Replay litmus.** If you `gc init` a scratch city and replay only
  the declared imports, you get the same behavior. Any step of the form
  "also run this command I ran manually that one time" → **fail**.
- **P1.2 Config flows through imports.** Changes to city behavior go through
  `gc import add` / `[imports.*]` entries + `gc import install` — never a
  one-off hand-edit to `city.toml`, or to a `pack.toml` outside the owned
  set. (Standing directive: city.toml changes come from pack updates, not
  hand-edits.)
- **P1.3 Never edit a materialized skill sink.** `.claude/skills/**` and
  `.codex/skills/**` are generated symlinks
  ([docs/skills-materialization.md](../../../docs/skills-materialization.md)).
  Edit the pack source under the owned set and let materialization
  propagate (`gc pack refresh` / next supervisor tick). Creating or
  modifying files *in* a sink → **fail**.
- **P1.4 Local-path imports must be remote-backed.** Local-path imports
  (decision gt-ths6) are legitimate standing config, not just a dev-loop
  hack — **provided** the import target is a clean git checkout whose HEAD
  is pushed to the canonical remote (`tdupu` fork for `gascity-packs`).
  Then another machine reproduces the city by cloning the fork at that
  commit and using the same import. A local-path import whose target has
  uncommitted or unpushed content that the city depends on → **fail**.
- **P1.5 Published packs prove it.** For packs meant for third parties,
  reproducibility is proven by the registry machinery: a
  `validate_registry.py` content-hash-validated release plus the
  release-compatibility gates
  ([README-contributing.md](../../../README-contributing.md)). A plan that claims
  "published" while skipping these → **fail**.
- **P1.6 Binaries match source.** The installed `gc` and `bd` must be clean
  builds of a synced HEAD: `go version -m <binary>` shows `vcs.revision`
  equal to the checkout's HEAD and `vcs.modified=false`. Builds and updates
  go through the sanctioned skills — `update-gascity-from-source`,
  `update-beads-from-source`, `update-gascity-packs-from-source` — which
  enforce exactly this. A dirty build, a binary from an untracked patch, or
  a stale binary shadowing the install on `$PATH` → **fail**. A
  working-tree artifact the build genuinely needs is legal **only if
  declared** — encoded in the corresponding update skill and listed in
  `.git/info/exclude` (precedent: the `go.work` beads-lockstep file in
  `~/repos/gascity`). Undeclared local patches → **fail**.
- **P1.7 Upstream stays pullable.** The per-repo reference invariants must
  hold or be restorable by the update skills:
  `~/repos/gascity` origin = fork = local main;
  `~/repos/beads` origin = local main;
  `~/repos/gascity-packs` **fork-canonical** — the fork is deliberately
  ahead of upstream (gt-5cye); upstream is *merged in*, never mirrored over.
  Work that would make a future upstream merge structurally impossible —
  e.g. rewriting upstream-owned files in the fork — → **fail**. (This is
  the reproducibility face of Pillar 2: edits outside the owned set create
  permanent merge conflicts.)
- **P1.8 Skill exposure is symlinked, named, and complete.** Every skill an
  owned pack ships is exposed exactly two ways: (a) a **relative symlink**
  in `~/repos/agent-skills/skills/<name>` (never a real-directory copy —
  a copy forks the pack source), and (b) a hand-placed city-sink symlink
  `~/gt/.claude/skills/<alias>.<name>` using the ADR 0002 alias
  (`mathcity.<name>` for the parent pack, `mathcity-<sub>.<name>` for a
  subdomain child pack). The sanctioned procedure is `skill-creator-math`.
  A dangling symlink, a real-dir duplicate, or a pack skill missing either
  exposure → **fail**. After any skill add/move/rename, run the
  `update-README` skill (mathcity-dev) — README drift is part of this rule,
  and README updates land in the same commit as the change.
- **P1.9 One real copy anywhere — adoption completes with origin dedup.**
  When a skill is adopted into the pack from another repo (agent-skills,
  hecke, any project repo), the pack copy becomes the **single real copy**;
  every consuming repo's copy becomes a relative symlink or is removed.
  P1.8 states this for agent-skills; this rule extends it to ALL repos.
  Duplicate real copies across repos → **fail** — unless the duplicate
  carries a tracked follow-up bead for its conversion (transition state,
  not an end state). (Origin: the 2026-07-10 hecke adoptions left 25
  duplicates pending exactly such a pass.)
- **P1.10 No private values in pack content.** Hostnames, usernames, SSH
  keys/jump hosts, database/schema names, alert emails, and absolute
  home-directory paths never enter pack content. Server- or
  database-touching skills read a **project-local, gitignored conf**; the
  pack ships only a placeholder `.conf.example` (model:
  `mathcity-lmfdb/assets/lmfdb-pipeline.conf.example`, inherited from
  hecke's `data-generation.conf`). Every adoption runs a scrub before
  commit: `gitleaks detect --no-git` on the adopted paths plus a targeted
  grep for IPs, `user@host`, `ssh` targets, key material, and absolute
  paths. Any hit → **fail**.
- **P1.11 Beads data plane syncs only to dedicated private repos.** A rig's
  bd `sync.remote` must be a dedicated `tdupu/<repo>-dolt` repo (the
  `dolt-init` naming invariant — never the code repo), and its
  `isPrivate=true` must be verified (`gh repo view`) before any data push.
  A public target or a code-repo target → **fail and HALT the sync** for
  that rig, never push-then-fix. (Origin: the gascity-packs rig's
  `sync.remote` was found pointing at the public code repo, 2026-07-10.)
- **P1.12 Every conf-driven skill ships a setup skill.** If a skill reads a
  project-local configuration file (a `.conf`, env file, or similar), the
  pack must ship a companion `setup-<name>` skill that creates that file
  interactively from the `.example` (copy, prompt for values, gitignore
  the copy, verify) — a fresh machine must go from `git clone` to a
  working skill without reverse-engineering the conf. A conf-reading
  skill with no setup skill → **fail**. (First instance:
  `setup-lmfdb-pipeline` for the lmfdb pipeline conf.)
- **P1.13 Every skill has a README table row.** Every skill directory in a
  pack appears exactly once in that pack's README skills table, with a
  one-line purpose. A skill with no row, or a row naming a skill that no
  longer exists, → **fail**. Enforced by the `update-README` procedure
  (same-commit rule) and audited by `check-build-hygiene`.

## Pillar 2 — Ownership boundary

*You own the owned pack set, nothing else.*

- **P2.1 Direct edits only inside the owned set.** Everything else —
  `gascity/`, `bmad/`, `pr-pipeline/`, `contributing/`, any other pack,
  gascity core, beads — is read-only (matches the scope boundary in
  [OUTSIDE-AGENTS.md](../../../OUTSIDE-AGENTS.md)).
- **P2.2 Never edit under any `vendor/**` tree.** Vendored trees mirror an
  upstream project (Superpowers, bmad-method, gstack,
  compound-engineering-plugin); hand edits create silent fork drift the
  next vendor sync clobbers.
- **P2.3 Compose through imports.** Cross-pack composition happens through
  `pack.toml` imports, not copy-paste or file surgery into a pack you don't
  own.
- **P2.4 Scope discipline (= review rule B10).** Inside the owned set, fix
  what the plan scopes; note adjacent refactors as out-of-scope follow-ups.
  This is the same rule as
  [`contributing/skills/review`](../../../contributing/skills/review/SKILL.md)
  B10 — that skill enforces it at PR time; this policy enforces it at plan
  time. One rule, two gates.

## Pillar 3 — Upstream-change discipline

*Sometimes gascity core or another pack genuinely must change to unblock
you. Allowed — through the front door only.*

- **P3.1 PR only, never direct push** to anything outside the owned set —
  even trivial-looking fixes (per OUTSIDE-AGENTS.md).
- **P3.2 Bugs: MRE first, then pr-pipeline.** Minimal reproducible example,
  then plan → blast-radius mapping → scorecard self-review → pre-push gate.
  No scattershot exploratory diffs against someone else's pack.
- **P3.3 Features: adoption-review bar.** README updated in the same PR, a
  `contributing/skills/review` scorecard pass, and — if it touches the
  `build-base` workflow contract — checked against
  [`gascity/REQUIREMENTS.md`](../../../gascity/REQUIREMENTS.md), since
  methodology packs are a shared contract other packs stand on.
- **P3.4 Tracked as a bead.** "Just this once, outside the PR record" is
  the failure mode this policy exists to prevent.
- **P3.5 Agent context is explicit.** A plan states whether it runs as an
  *inside worker* (`GT_ROLE` set, city-dispatched, operates inside its
  assigned scope) or an *outside agent* (conservative git policy, never
  commits/pushes without explicit say-so, never pushes outside the owned
  set). Ambiguity about which context executes the plan → **revise**.

## Pillar 4 — Impact review at plan time

*Answer both directions explicitly before building. Complements
`contributing/skills/map-blast-radius` (which maps Go-code blast radius
inside gascity core); this is the pack-level, plan-time analogue.*

- **P4.1 Upstream impact.** Does the plan touch anything outside the owned
  set (gascity core, another pack, a vendor tree, beads)? If yes, is that
  edit already routed through Pillar 3, or is the plan quietly assuming a
  local patch "for now"? A silent local-patch assumption → **fail** (it
  also breaks P1.6/P1.7).
- **P4.2 Downstream impact.** If this ships, does it change a contract
  other consumers rely on: the `build-base` contract, a materialization
  assumption, an import key/alias another pack's formula references, a
  file another pack reads? And the mirror image: does the plan make
  something outside the owned set depend on an owned-pack-internal detail
  without going through a declared import? Either direction of leak breaks
  isolation even when nothing looks "hacked" locally.
- **P4.3 Convoy aggregate pass.** For a convoy, run P4.1/P4.2 per bead
  *and* once over the union of all beads' scopes — cross-bead interactions
  count.

## Non-negotiables (quick checklist)

- No hand-edited `city.toml`, and no hand-edited `pack.toml` outside the
  owned set (P1.2).
- No edits under any `vendor/**` tree, ever (P2.2).
- No edits inside a materialized `.claude/skills/**` / `.codex/skills/**`
  sink (P1.3).
- No direct push outside the owned set — PR only, MRE for bugs,
  docs+scorecard for features (P3.1–P3.3).
- No undeclared working-tree patches feeding a build; no dirty binaries
  (`vcs.modified=false` or it doesn't ship) (P1.6).
- No state the city depends on that exists only on this machine —
  committed and pushed to the canonical remote, or it isn't real (P1.4).
- No real-directory copies of pack skills in agent-skills, no dangling
  exposure symlinks, no un-exposed pack skills (P1.8).
- No duplicate real copies of a pack skill in ANY repo — adoption isn't
  done until the origin is a symlink or gone (P1.9).
- No hostnames, keys, schema names, or other private values in pack
  content — conf.example only, scrub on adoption (P1.10).
- No bead-data push to anything but a verified-private `<repo>-dolt`
  target (P1.11).
- No conf-driven skill without a companion `setup-*` skill (P1.12).
- No skill without a README table row — and no ghost rows (P1.13).
- No drive-by scope creep, even inside the owned set (P2.4 / B10).

## Verdict vocabulary

Reuses the brief-cycle Decision vocabulary ([CONTEXT.md](../../../CONTEXT.md)) —
no parallel vocabulary is introduced:

- **approve** — no P-rule violations; plan/convoy is clean to build (audit
  mode: current state is compliant).
- **revise** — fixable violations; the verdict names the specific P-rule(s)
  broken, the file/directory that triggered each, and a compact brief that
  can seed a fresh brainstorming session to re-derive the plan around the
  constraint (audit mode: a drift list with per-item remediation).
- **reject** — the plan's core approach requires violating a pillar with no
  workaround (e.g. the goal is unreachable without editing gascity core
  outside the PR path). Send back for a different approach, not a patch.
  (Audit mode: not applicable — audits produce approve/revise/defer.)
- **defer** — needs a human call: ambiguous ownership, a genuinely
  contested "is this upstream's problem or mine". Escalate, don't guess.

## Resolved questions (2026-07-10 grilling)

1. **Scope:** all owned packs, not `mathcity/` alone — ADR 0002's subdomain
   child packs already make "your pack" a set; the skill parameterizes on
   owned-pack roots.
2. **Input shape:** plan docs *and* convoys *and* current-state audits —
   the policy's real subject is being able to pull from upstream, rebuild
   this install on another machine, and share it with collaborators; a
   binary or config that diverges from pushed source can't be shared or
   recreated.
3. **Placement:** this file, `mathcity/subdomains/dev/POLICY.md` — the
   normative doc of the `mathcity-dev` child pack (ADR 0002 nested-pack
   model), created in the same session. Pack development is its own
   functional domain, sibling of brief-system/computing/etc.; the future
   `check-hygiene` skill lives here too (materializing as
   `mathcity-dev.check-hygiene`), and the policy is also intended to prime
   the mathcity mayor.

## References

- [OUTSIDE-AGENTS.md](../../../OUTSIDE-AGENTS.md) — outside-agent role, git authority, scope boundary this policy extends
- [docs/adr/0002](../../../docs/adr/0002-mathcity-subdomain-pack-model.md) — owned pack set layout
- [docs/skills-materialization.md](../../../docs/skills-materialization.md) — why sinks are generated, not source
- [README-contributing.md](../../../README-contributing.md) — registry publishing, content-hash validation, release-compat gates
- [gascity/REQUIREMENTS.md](../../../gascity/REQUIREMENTS.md) — the `build-base` contract (Pillar 3/4 downstream surface)
- [contributing/skills/review](../../../contributing/skills/review/SKILL.md) (B10) and [map-blast-radius](../../../contributing/skills/map-blast-radius/SKILL.md) — the PR-time gates this plan-time gate complements
- `~/.claude/skills/update-{gascity,beads,gascity-packs}-from-source` — the sanctioned update procedures whose invariants P1.6/P1.7 encode
