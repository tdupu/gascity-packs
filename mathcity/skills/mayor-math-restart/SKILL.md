---
name: mayor-math-restart
description: Full QUIMBY session orientation. Run at the start of every new QUIMBY (math-city Mayor) session. Reads the restart prompt, the durable operation docs, and the session catalog so a fresh session can operate the city the way the current QUIMBY does.
---

# mayor-math-restart

Full QUIMBY onboarding. (There is NO auto-injecting PreToolUse hook — this skill
reads its own context. Corrected 2026-07-16.) Do these in order:

## 1. Read the durable context (regression-proofed over 11 QUIMBY generations)

1. **`~/gt/mathcity-mayor/restart/PROMPT-mayor-restart.txt`** — this session's background,
   standing rules, city state, and charge.
2. **`~/gt/gascity-packs/mathcity/docs/QUIMBY-ONBOARDING.md`** — the index + S11-corrected
   operational truths (the gold). It points to:
   - `CITY-RESTART-CHECKLIST.md` — Phase 0–6 step-by-step to bring the city up + verify.
   - `CITY-OPERATION-REFERENCE.md` — architecture, pools/agents, brief pipeline, correct
     command surface.
   - `TEST-CYCLE-GUIDE.md` + `DOGFOOD-WORKFLOW.md` — the dogfood/test cycle.
3. **`~/gt/mathcity-mayor/session-catalog.json`** — one entry per prior QUIMBY (arc,
   city state, charge). Read the last few.
4. The **handoff bead** named in the PROMPT (`bd show <id>`) + `~/gt/mathcity-tests/run-log.md`
   (the prior session's S<N>.x rows).

## 2. File onboarding briefs (async)

Run `/file-briefs` immediately after reading the docs — this enumerates open
questions from the PROMPT + onboarding docs and files one brief per question
onto the brief stack for Taylor to adjudicate asynchronously. Do NOT use
`/grill-with-docs` for onboarding (it serializes Taylor on synchronous
availability and violates [[mayor-no-direct-grilling]]). Keep `/grill-with-docs`
only for explicit interactive design sessions.

## 3. Orient and confirm

1. Run `/prime-outsider` to check open beads and current handoff-bead status.
2. Report the session's top priority to Taylor before taking any other action.
3. Confirm with BART (`80b87468`) what BART is supposed to be doing before starting work.

## 4. At session end

- Write a handoff bead; update `~/gt/mathcity-mayor/restart/PROMPT-mayor-restart.txt`; expand
  `~/gt/mathcity-tests/run-log.md`; and add one entry to
  `~/gt/mathcity-mayor/session-catalog.json`:

```json
{
  "quimby": <N>,
  "bead": "<your-handoff-bead-id>",
  "date": "<YYYY-MM-DD>",
  "summary": "<what was done this session>",
  "city_state": "<city state for the next QUIMBY>",
  "charge_for_next": "<priority charge for the next QUIMBY>"
}
```
