---
name: mayor-math-prime
description: PRIME a fresh math-city Mayor (QUIMBY) session. Renders the restart PROMPT (jinja template composing the session catalog + current handoff bead + charge, with plain-text and generic fallbacks), then reads the durable operation docs, the session catalog, and the handoff bead, files onboarding briefs, and orients. Run at the START of every new QUIMBY session — directly, or as the second half of mayor-math-restart (handoff → clear → prime). Trigger phrases: "prime the mayor", "mayor-math-prime", "onboard QUIMBY", "start a new mayor session".
---

# mayor-math-prime

The QUIMBY PRIMING procedure — the session-START half of the restart cycle
(`mayor-math-handoff` → `/clear` → **`mayor-math-prime`**). There is NO
auto-injecting PreToolUse hook — this skill reads its own context.

State dir: `~/gt/mathcity-mayor/` (override with `MAYOR_STATE_DIR`).
Restart PROMPT home: `~/gt/mathcity-mayor/restart/` (moved from
`~/Documents/misc/PROMPT-mayor-restart.txt` on 2026-07-16).

## 0. Render and read this session's PROMPT (jinja-wired)

```bash
bash <this-skill-dir>/scripts/render-prime.sh
```

Read the full output — it is this session's background, standing rules, city
state, and charge. The script resolves, in order:

1. **Jinja render** — `restart/PROMPT-mayor-restart.j2` composed with
   `session-catalog.json` (all prior sessions, auto-computed QUIMBY number)
   and the current **handoff bead** fetched live via `bd show`, plus the
   recorded `city_state` and `charge_for_next`.
2. **Plain-text fallback** — `restart/PROMPT-mayor-restart.txt` (the curated
   per-city prompt; kept current by `mayor-math-handoff`).
3. **Generic mayor statement** — `templates/PROMPT-mayor-generic.txt` shipped
   with this skill. This is the first-import experience: if no state dir
   exists yet, the script prints the generic statement and bootstrap
   instructions instead of failing.

## 1. Read the orientation context (target ~30KB — keep it tight)

**Read now, always:**

1. **`~/gt/gascity-packs/mathcity/docs/QUIMBY-ONBOARDING.md`** (~7KB) — the index +
   S11-corrected operational truths (the gold). It names the deeper docs but does NOT
   ask you to read them now; each is tiered below.
2. **`~/gt/mathcity-mayor/session-catalog-recent.json`** (~5–11KB) — last 5 QUIMBY
   sessions (arc, city state, charge). Full history is in `session-catalog.json` only if
   you need it. **Consistency guard:** the handoff bead named in the PROMPT must be the
   newest entry here; if it is absent, the prior session skipped its close protocol — treat
   the handoff bead (item 4) as the source of truth for the latest arc and flag the gap.
3. **Latest run-log shard** — find and read it:
   ```bash
   ls -t ~/gt/mathcity-tests/run-log/*.md | grep -v archive | head -1
   ```
   Read that file (~3–10KB) for the prior session's S<N>.x rows. Do NOT read
   `run-log.md` — it is the frozen 190KB archive monolith, not the live log; reading it
   at orientation is exactly the bloat that derails a fresh session.
4. The **handoff bead** named in the PROMPT (`bd show <id>`).

**Read when you begin city bring-up (NOT at orientation):**

- `CITY-RESTART-CHECKLIST.md` (~17KB) — Phase 0–6 step-by-step to bring the city up +
  verify. You *execute* this, so read it as you start Phase 0. Folding it into orientation
  blows the ~30KB target by half.

**On-demand only. Each doc carries its own integrity guard — obey it.**

- `CITY-OPERATION-REFERENCE.md` (~32KB) — architecture, pools/agents, command surface,
  brief pipeline. *Trigger: verifying a command exists, diagnosing fleet/pipeline issues.*
- `TEST-CYCLE-GUIDE.md` (~11KB) — test/triage cycle. *Trigger: before running a test or
  triaging a pipeline failure.*
- `DOGFOOD-WORKFLOW.md` (~11KB) — hotfix → hygienic loop, ~/gt↔~/repos duality.
  *Trigger: before a hotfix, a pack change, or any deploy.*

**Standing dispatch rule (MR1.x):** default dispatch = SLING. The Agent tool
(in-session fork) is only acceptable when ALL THREE hold: result needed in
this session, fast (≤ ~5 min), no human adjudication required. See
[[mayor-math]] Rule 0 and [[mayor-policy]].

## 2. File onboarding briefs (async)

Run `/file-briefs` immediately after reading the docs — this enumerates open
questions from the PROMPT + onboarding docs and files one brief per question
onto the brief stack for Taylor to adjudicate asynchronously. Do NOT use
`/grill-with-docs` for onboarding (it serializes Taylor on synchronous
availability and violates [[mayor-no-direct-grilling]]). Keep
`/grill-with-docs` only for explicit interactive design sessions.

## 3. Orient and confirm

1. Check open beads and the current handoff-bead status directly
   (`bd ready`; `bd show <handoff-bead>`).
2. Report the session's top priority to Taylor before taking any other action.
3. Confirm with BART (`80b87468`) what BART is supposed to be doing before
   starting work.

## 4. Surface pending decisions

List the briefs **ready to adjudicate** for Taylor in short form (one line each:
`#N slug — the decision`). Read them from the decisions-track manifest and show
only those still awaiting a call:

```bash
python3 -c "
import json
for l in open('/Users/tdupuy/gt/.beads/decisions-track/manifest.jsonl'):
    r=json.loads(l)
    if r.get('status')=='ready':
        print('#'+str(r.get('id')), r.get('slug') or r.get('title',''))
"
```

Do not adjudicate them yourself — surface them so Taylor can drain the pile.

## 5. Session toolkit (remind Taylor these are available)

- **`math-city-work`** — dispatch math work (rank campaign, repair batches) to the fleet.
- **`decisions-to-briefs`** — turn a pile of pending decisions into adjudicable brief artifacts.
- **`present-briefs`** — batch-present N briefs to Taylor with a warm queue.
- **`present-it`** — dump decision-ready context on ONE artifact into the conversation.
- **`adjudicate-brief`** — record Taylor's verdict on a brief persistently (one-bead model: verdict on the brief bead).

**Restart sequence** (end-of-session → next session):
`mayor-math-handoff` (write handoff bead + refresh PROMPT) → `/clear` → **`mayor-math-prime`** (this skill).
