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

## 1. Read the durable context (regression-proofed over 12+ QUIMBY generations)

1. **`~/gt/gascity-packs/mathcity/docs/QUIMBY-ONBOARDING.md`** — the index +
   corrected operational truths (the gold). It points to:
   - `CITY-RESTART-CHECKLIST.md` — Phase 0–6 step-by-step to bring the city up + verify.
   - `CITY-OPERATION-REFERENCE.md` — architecture, pools/agents, brief pipeline, correct
     command surface.
   - `TEST-CYCLE-GUIDE.md` + `DOGFOOD-WORKFLOW.md` — the dogfood/test cycle.
2. **`~/gt/mathcity-mayor/session-catalog.json`** — one entry per prior QUIMBY
   (arc, city state, charge). Read the last few.
3. The **handoff bead** named in the PROMPT (`bd show <id>`) +
   `~/gt/mathcity-tests/run-log.md` (the prior session's S<N>.x rows).

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
