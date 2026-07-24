---
name: skill-creator-math
description: Create a new skill in the gascity-packs mathcity pack family (~/repos/gascity-packs/mathcity/ — parent skills/ or a subdomain child pack per ADR 0002) and expose it to plain sessions (agent-skills symlink) and city agents (hand-placed ~/gt/.claude/skills symlink). Use whenever the user says "create a math skill", "add a skill to the mathcity pack", "pack skill for X", "skill-creator-math", or asks to make a brief-cycle / math-workflow / pack-dev skill available to city agents. Also handles "reload-skills" / "refresh skills". Counterpart of skill-creator-plus, which publishes personal/utility skills to ~/repos/agent-skills as real directories; use THIS skill when the new skill feeds pack formulas, gates, or must ship with a mathcity pack.
---

# skill-creator-math

Create a skill in the **mathcity pack family** of `~/repos/gascity-packs`
and expose it everywhere it's needed. Updated 2026-07-10: pack renamed
`mathematics/` → `mathcity/`; subdomain child packs added (ADR 0002);
exposure mechanism corrected (mathcity is NOT a city import — see below).

## When to use which creator

| Skill kind | Tool | Destination |
| --- | --- | --- |
| Feeds pack formulas/gates, brief-cycle, or ships with a mathcity pack | **this skill** | `~/repos/gascity-packs/mathcity/...` |
| Personal/utility (bridge, supervision, one-off helpers) | `skill-creator-plus` | `~/repos/agent-skills/skills/<name>/` (real dir) |

Standing rulings: gascity-packs owns substrate codification; pack copy is
canonical (gt-4jt2, gsp-lw3). Mechanism reference:
`~/repos/gascity-packs/docs/skills-materialization.md`.

## Step 0 — Route to the right pack root

Per [ADR 0002](~/repos/gascity-packs/docs/adr/0002-mathcity-subdomain-pack-model.md),
mathcity is a family: a parent pack plus nested child packs, each with its
own `pack.toml`. Pick the destination:

| Domain of the new skill | Destination `skills/` dir | Sink name in `~/gt/.claude/skills/` |
| --- | --- | --- |
| Cross-domain / brief-cycle core | `mathcity/skills/<name>/` | `mathcity.<name>` |
| Brief-system pipeline internals | `mathcity/subdomains/brief-system/skills/<name>/` | `mathcity-brief-system.<name>` |
| Computing (magma/sage/etc.) | `mathcity/subdomains/computing/skills/<name>/` | `mathcity-computing.<name>` |
| Proof assistants | `mathcity/subdomains/proof-assist/skills/<name>/` | `mathcity-proof-assist.<name>` |
| LaTeX / notes-tier screening | `mathcity/subdomains/latex/skills/<name>/` | `mathcity-latex.<name>` |
| LMFDB queries | `mathcity/subdomains/lmfdb/skills/<name>/` | `mathcity-lmfdb.<name>` |
| Pack development / hygiene / policy gates | `mathcity/subdomains/dev/skills/<name>/` | `mathcity-dev.<name>` |

Default to the parent pack only when the skill genuinely spans domains.
Pack-dev skills (anything derived from
`mathcity/subdomains/dev/POLICY.md`) go in `dev`.

## Creating a skill

0. **Wheel-check FIRST (P1.20 — REQUIRED).** Before authoring anything, run the
   `check-wheel` skill on the proposed skill (its name + one-line purpose) — just
   make sure we aren't reinventing the wheel. This is the gate that stops
   duplicates (e.g. a second brief-stack skill).
   - Existing skill/formula/tool already covers it → **STOP.** Adopt or extend the
     existing one, or bring the overlap to Taylor. Do NOT create a duplicate.
   - Genuine gap confirmed → proceed. Record the verdict (adopt / adapt / build) in
     the skill's provenance or the creation bead.

1. **Author** `<destination>/SKILL.md` with `name:` and `description:`
   frontmatter. The description drives triggering — state *when* to use it
   and include trigger phrases. Supporting scripts go in the same
   directory; keep paths absolute or pack-relative (gc rejects `../`
   traversal in check paths).
2. **No pack.toml change is needed** — `skills/` is discovered by
   convention (any `<pack>/skills/<name>/SKILL.md`).
3. **Safety scan** before committing (secrets never enter history):
   ```bash
   cd ~/repos/gascity-packs && gitleaks detect --no-git --source <destination>
   ```
   (The repo's pre-push hook re-scans the push range as a second net.)
3a. **P1.14 dependency pre-flight** — If the skill reads a conf file or depends on an external tool (database, SSH server, etc.):
   - Add a pre-flight check at the very top of the skill body (before any action) that probes for the dependency with `[ -f "$CONF" ]` or equivalent.
   - Fail with the standard P1.14 error format:
     ```
     I'm sorry, I can't do that — <what is missing>.
     Run /<setup-skill> (or <fix action>) to set it up.
     (<One sentence on what the dependency enables.>)
     ```
   - Reference the companion setup skill in the error message (`/configure-server` for SSH confs, `/configure-database` for pipeline confs).
   - Never let a raw `source`, `psql`, or SSH invocation fail with a cryptic OS error — the pre-flight must exit first.
   - Use the conf-discovery loop pattern (project root first, hecke fallback) when the conf follows the `lmfdb-server.conf` / `lmfdb-pipeline.conf` convention.
4. **Commit and push to the fork** — fork `tdupu/gascity-packs` is
   canonical and pushing to it is standing-authorized (gt-5cye). NEVER
   open an upstream PR. Commit message ends with the standard
   `[autogenerated by <model> on <date>]` footer when Claude writes it.
5. **Expose to BOTH sinks — REQUIRED, verified, atomic.** Every skill has
   two independent consumers, and a skill exposed to only one is a
   regression (this is exactly how `prime-clerk` shipped visible to plain
   sessions but invisible to city agents + the `gascity:mathcity.*`
   registry). You MUST create **both** symlinks and **confirm both
   resolve** before you consider the skill exposed. Never treat either
   sink as optional or "nice to have."

   - **Sink A — agent-skills** (plain-session Claude Code; `~/.claude/skills`
     is a symlink to `~/repos/agent-skills/skills`, so this one link serves
     every plain session). This MUST be a **relative symlink** — never a
     real copy of the directory (a real dir forks the pack source;
     `search-lmfdb` was that failure mode):
     ```bash
     cd ~/repos/agent-skills/skills
     ln -s ../../gascity-packs/mathcity/<subpath>/skills/<name> <name>
     ```
   - **Sink B — city sink** (city / managed agents + the
     `gascity:mathcity.*` skill registry). mathcity is NOT imported in
     `~/gt/city.toml` (imports are gc, gc-base, pr-pipeline only), so
     `gc pack refresh` will NEVER create this — it is a **hand-placed
     absolute symlink** using the sink name from the Step 0 table. Match
     the form of existing `~/gt/.claude/skills/mathcity.*` links (absolute
     path into the working tree):
     ```bash
     ln -s ~/repos/gascity-packs/mathcity/<subpath>/skills/<name> \
           ~/gt/.claude/skills/<sink-name>
     ```
     The materializer never prunes user-placed sink entries, so this
     survives supervisor ticks.

   **Confirm-resolves gate (do not skip — this is the step that catches a
   one-sink miss):** verify BOTH targets resolve to a readable `SKILL.md`.
   If either check fails, STOP and fix the missing/broken link before
   proceeding — a skill is not exposed until both pass:
   ```bash
   test -r ~/.claude/skills/<name>/SKILL.md \
     && echo "Sink A OK" || echo "Sink A MISSING — create the agent-skills symlink"
   test -r ~/gt/.claude/skills/<sink-name>/SKILL.md \
     && echo "Sink B OK" || echo "Sink B MISSING — create the city-sink symlink"
   ```
6. **Commit the agent-skills symlink** (Sink A is tracked in a git repo;
   Sink B is a hand-placed link under `~/gt`, not committed here):
   ```bash
   cd ~/repos/agent-skills
   sh scripts/check-skill-symlinks.sh   # must report OK for the new link
   git add skills/<name>
   git commit -m "refactor: symlink <name> to mathcity pack (pack canonical)"
   git push origin main
   ```
7. **Update the skills index** — append the new skill to
   `mathcity/README-skills.md`, the single canonical cross-pack index of
   every mathcity skill (parent + all subdomains). This is a required
   creation step; skipping it makes the index drift.
   - Add ONE row under the correct section (Parent pack, or the matching
     `subdomains/<sub>` section), alphabetical by skill name:
     `` | `<name>` | `<alias>` | <one-sentence purpose> | `` where
     `<alias>` is `mathcity.<name>` (parent) or `mathcity-<sub>.<name>`
     (subdomain) per Step 0, and `<one-sentence purpose>` is the first
     sentence of the skill's frontmatter `description:`.
   - Bump the section count and the total count in the header line.
   - **Do NOT create a second skills index.** `README-skills.md` is the one
     source of truth; the `## Skills` table in `README.md` and the
     `subdomains/*/README.md` tables are pack-local views that point here.
     `update-README` full-syncs this same file on any pack change — if
     unsure about drift, run `/update-README` rather than hand-patching.
   - Commit it with the pack changes (same fork `tdupu/gascity-packs`).
8. **Final verification — three gates, all required.** A skill is not
   shipped until all three pass:

   **Gate A — sink resolve** (Step 5 already ran this; re-confirm after commit):
   ```bash
   test -r ~/.claude/skills/<name>/SKILL.md \
     && echo "Sink A OK" || echo "FAIL Sink A — fix symlink"
   test -r ~/gt/.claude/skills/<sink-name>/SKILL.md \
     && echo "Sink B OK" || echo "FAIL Sink B — fix symlink"
   ```

   **Gate B — README-skills.md entry (REQUIRED — no exceptions):**
   ```bash
   grep -q '<name>' ~/repos/gascity-packs/mathcity/README-skills.md \
     && echo "README-skills.md OK" \
     || echo "FAIL README-skills.md — add row per step 7 before marking done"
   ```
   A skill with no README-skills.md entry is invisible to future agents
   auditing the index. This is a hard stop — do not report success until
   the grep passes.

   **Gate C — symlink health:**
   ```bash
   sh ~/repos/agent-skills/scripts/check-skill-symlinks.sh 2>&1 | grep -E "BROKEN|MISSING|OK"
   ```

   New Claude Code sessions see the skill at startup; running sessions pick it
   up on their next skill-list reload; city agents and the
   `gascity:mathcity.*` registry see it via Sink B.

## reload-skills

When the user says "reload-skills" / "refresh skills":

- **mathcity skills need no refresh** — both exposure paths are symlinks
  into the working tree, so edits to an existing SKILL.md are live
  immediately. Only **new skill dirs** need their two symlinks (steps 5–6).
- `cd ~/gt && gc pack refresh` re-materializes only the *imported* packs
  (gc, gc-base, pr-pipeline — local-path imports per gt-ths6). Run it in
  the background (gc CLI is slow); the supervisor tick also
  re-materializes idempotently.
- While you're there, check for drift:
  ```bash
  sh ~/repos/agent-skills/scripts/check-skill-symlinks.sh
  for l in ~/gt/.claude/skills/*; do [ -L "$l" ] && [ ! -e "$l" ] && echo "DANGLING: $l"; done
  ```
  Dangling `mathematics/*` targets are the old pack name — retarget them
  to `mathcity/`.

## What this skill does NOT do

- ❌ Touch `~/repos/gascity-packs/gastown/` (standing: never modify gastown/).
- ❌ Push to `gastownhall/gascity-packs` upstream or open upstream PRs.
- ❌ Commit a real directory to `~/repos/agent-skills` — only a relative symlink (step 5).
- ❌ Edit anything outside the mathcity family in gascity-packs (see `mathcity/subdomains/dev/POLICY.md`, Pillar 2).
- ❌ Auto-migrate existing agent-skills skills.
