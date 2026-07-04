---
name: catch-no-brainer
description: PRELIMINARY v0.1 — classify a brief against the he-lele 5-criterion no-brainer test, plus recognize the capability-blocker shape (would-be no-brainer stalled by a permission/capability gap) and signal compact-form eligibility to downstream present-it consumers (DRY-RUN). Emits one JSON-line verdict to stdout per brief; copies no-brainer matches into /Users/tdupuy/gt/hecke/.beads/briefs/.pile/.no-brainer/ and novel-shape descriptors into /Users/tdupuy/gt/hecke/.beads/.gates-candidate-pile/. NEVER edits bead he-xkq3, NEVER auto-merges, NEVER closes briefs, NEVER runs `bd update`. Triggers triaging a brief that just landed in the main stack for Taylor-bypass eligibility (stale-scratch cleanup, mechanical promotion, sibling-PASS); architecture-class briefs (deep design, coupling, judgment-load) bypass this skill and go straight to Mayor/Taylor.
---

> **PRELIMINARY v0.1 — DRY-RUN ONLY.** Emits proposed verdicts + proposed gates-registry extensions + compact-form eligibility signal.
> NEVER writes to [[he-xkq3]], NEVER auto-merges, NEVER closes briefs, NEVER calls `bd update`/`bd close`/`bd link`.
> Allowed side effects: `mkdir -p` + file write in `.pile/.no-brainer/` and `.gates-candidate-pile/`. Nothing else.

## Purpose
Triage briefs so non-architecture cleanups bypass Taylor adjudication. Composes by reference (does not re-implement): [[he-lele]] (5-criterion + cat-A/B/C/D), [[he-xkq3]] G5 (cat-E server-touching) + G9 (no-brainer), [[he-9czp]] gate-order, [[he-cnat]] preliminary-skill-first.

Also signals [[present-it]] consumers whether the brief may be output in **compact form** (`DECISION` + `CONTEXT` + `RECOMMEND` + `CONFIRM y/n/grill-me-further`) or MUST be full-form.

## Classification rule
Given a brief at `<path>` (frontmatter + body + diff summary inside the brief):

1. **Server-touching first** ([[he-xkq3]] G5 fires before G9). If diff/disposition touches any path in [[he-lele]] §"Safety override" server set (`magma/scripts/dispatch.sh`, `magma/make/dispatch/*`, `gt-dolt*`/`gt-upf*`, `~/gt/.gc/daemon*`, `~/gt/.dolt-data/*`/`~/.dolt-data/*`, `.gc/agent-bridge/*`, ssh-writes to `aia-s27`): emit `{no_brainer:false, reason:"cat-E-server-touching", compact_eligible:false}` and STOP.

2. **User-skill-touching** ([[as-wjv]] SAFETY OVERRIDE). If diff/disposition touches any path in `~/.claude/skills/<name>/` or `~/repos/agent-skills/skills/<name>/` (SKILL.md or references): emit `{no_brainer:false, reason:"user-skill-touching-override", compact_eligible:false}` and STOP.

3. **Capability-blocker shape.** If the brief's recommended disposition WOULD satisfy the [[he-lele]] 5-criterion no-brainer test but for a permission/capability gap the polecat could not resolve in-session (`gh auth` missing, credentials not provisioned, external service unreachable, sandbox denies a required syscall, etc.) — detect via explicit `capability_blocker: <description>` frontmatter field OR body text pattern `BLOCKED-ON: <capability>` — emit `{no_brainer:false, category:"capability-blocker", reason:"resolve <blocker>, then re-classify", compact_eligible:false, requires_taylor_adjudication:false}` and STOP.

   *Rationale:* the shape IS a known no-brainer; only the capability gap blocks the mechanical disposition. Routing as "resolve the blocker, then re-run this classifier" produces cleaner throughput than presenting a full A/B/C/D brief to Taylor. Data point: he-gu79 (n=5+ per [[feedback_no_brainer_class_under_flagged]]).

4. **[[he-lele]] 5-criterion** (all 5 must hold): (1) branch regex `^(polecat|nux|<role>)/(<role>/)?<bead>(@<token>)?$`; (2) parent bead CLOSED with documented supersession (close-reason names a `bd`-resolvable artifact / merged PR / fs path); (3) diff vs `origin/master` touches ONLY scratch/transient files (no `magma/`, `latex/`, `notes.tex`, schema, `DATA/`, package files, `.beads/` except briefs themselves); (4) no downstream beads reference the branch; (5) brief verdict is `DELETE` or `INVESTIGATE`. → emit `{no_brainer:true, category:"stale-branch", compact_eligible:true}` (cat-A WIP-autosave; `cat-B` test-execution, `cat-C` verification-mid-flight, `cat-D` consolidate-mini-beads — see [[he-lele]] for definitions).

5. **Else** (shape not in A/B/C/D and not a capability-blocker) → emit `{no_brainer:"candidate", proposed_registry_extension:"<one-line gate criterion>", requires_taylor_adjudication:true, compact_eligible:false}`.

## Compact-form eligibility signal

`compact_eligible: true` means the downstream [[present-it]] consumer MAY output the brief in compact form (`DECISION` / `CONTEXT` / `RECOMMEND` / `CONFIRM y/n/grill-me-further`) instead of the full 7-section grill-ordered brief. Necessary but not sufficient — [[brief-prep]] also requires BOTH safety-override booleans (`server_touching`, `user_skill_touching_override`) to be `false` before compact form ships.

`compact_eligible: false` means the brief MUST be full-form. Applies to: server-touching, user-skill-touching, capability-blocker, and novel-shape (candidate) outputs.

`capability-blocker` shape is a hard "not compact, not full-form-yet" — the brief should not be presented in either shape until the blocker is resolved. Mayor / dispatcher's job to route the blocker for resolution.

## Output schema (one JSON-line per brief, to stdout)
```json
{"brief_path":"<abs>","bead_id":"<id|null>","no_brainer":true|false|"candidate",
 "category":"stale-branch|cat-A|cat-B|cat-C|cat-D|capability-blocker|null",
 "reason":"cat-E-server-touching|user-skill-touching-override|resolve <blocker>|null",
 "compact_eligible":true|false,
 "proposed_registry_extension":"<text|null>","requires_taylor_adjudication":true|false,
 "classified_at":"<ISO-8601-utc>"}
```

## Side effects (v0.1)
- `no_brainer:true` → `mkdir -p` + copy brief into `.pile/.no-brainer/`. Consumed by pile-processor ([[he-x3se]], not-yet-shipped); until then the file is inert.
- `no_brainer:"candidate"` → write `.gates-candidate-pile/<brief-slug>-candidate.md` with `pattern_fingerprint`, `originating_brief`, `why_classified_candidate`, `suggested_gate_criterion`. Curator promotion to [[he-xkq3]] is OUT of scope (see [[he-xxwb]]).
- `category:"capability-blocker"` → stdout only. Do NOT deposit in `.pile/.no-brainer/` (the disposition can't be executed) or `.gates-candidate-pile/` (the shape isn't novel). Mayor consumes the stdout signal and dispatches capability resolution (e.g., token-pass-outer / credential provisioning); when resolved, the brief is re-classified.
- `no_brainer:false` (server-touching / user-skill-touching) → stdout only.

## Tool restrictions (self-discipline contract)
- ALLOWED: `Read`, `Bash` (grep/find/jq/regex), `Write`/`mkdir` inside the two named dirs.
- FORBIDDEN: `Edit`/`Write` outside those dirs; `bd update`/`bd close`/`bd link`/`bd remember`; `git push`/`git merge`/`git commit`; any read/write touching [[he-xkq3]] or any other bead.
- Self-refuse → log `{verdict:"REFUSED", reason:"..."}` to stdout.

## Fixture (pass-bar: all classify correctly)
Run `bash fixtures/run.sh`:

| # | Fixture | Expected verdict |
|---|---|---|
| 1 | `stale-branch-A.md` | `{no_brainer:true, category:"stale-branch", compact_eligible:true}` |
| 2 | `stale-branch-B.md` | `{no_brainer:true, category:"stale-branch", compact_eligible:true}` |
| 3 | `stale-branch-C.md` | `{no_brainer:true, category:"stale-branch", compact_eligible:true}` |
| 4 | `server-touching.md` | `{no_brainer:false, reason:"cat-E-server-touching", compact_eligible:false}` |
| 5 | `novel-shape.md` | `{no_brainer:"candidate", requires_taylor_adjudication:true, compact_eligible:false}` |
| 6 | `capability-blocker.md` | `{no_brainer:false, category:"capability-blocker", compact_eligible:false}` |

Pass iff `fixtures/run.sh` exits 0.

## Status
PRELIMINARY v0.1 under [[he-cnat]]. FP-converge follow-up [[he-ahfr]] (gated on ≥3 dogfood examples). Self-bead [[he-6wej]]. Sling [[he-h3p2]].

## Versioning
- **v0.0 — PRELIMINARY DRY-RUN** (2026-06-24): initial 5-criterion classifier + cat-E override + fixture harness (5 fixtures).
- **v0.1 — capability-blocker shape + compact-form signal** (2026-06-30, per as-niek per Taylor "better briefs" epic): added step 2 (user-skill-touching-override consistency with [[as-wjv]]); added step 3 (capability-blocker shape — would-be no-brainer stalled by permission/capability gap; route as "resolve, then re-classify" rather than presenting A/B/C/D; data point he-gu79 n=5+); added `compact_eligible` output field consumed by [[present-it]] for compact-form eligibility; added capability-blocker.md fixture (6th case).
