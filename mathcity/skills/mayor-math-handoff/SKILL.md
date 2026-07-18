---
name: mayor-math-handoff
description: SESSION-END handoff for the math-city Mayor (QUIMBY). Writes the chained handoff bead, expands the run-log, adds the session-catalog entry, and updates the restart PROMPT so the next Mayor session can prime from it. Run at the END of every QUIMBY session — directly, or as the first half of mayor-math-restart (handoff → clear → prime). Trigger phrases: "mayor-math-handoff", "hand off the mayor session", "end the QUIMBY session", "write the mayor handoff".
---

# mayor-math-handoff

The QUIMBY SESSION-END procedure — the first half of the restart cycle
(**`mayor-math-handoff`** → `/clear` → `mayor-math-prime`). Do ALL FOUR steps,
in this order (the catalog entry must exist before the PROMPT is regenerated):

State dir: `~/gt/mathcity-mayor/` (override with `MAYOR_STATE_DIR`).
Restart PROMPT home: `~/gt/mathcity-mayor/restart/` (moved from
`~/Documents/misc/PROMPT-mayor-restart.txt` on 2026-07-16).

## 1. Write the handoff bead (chained)

Write a `gt-` handoff bead holding this session's full arc (what was done,
what was verified at source, open threads, warnings for the next QUIMBY).
Reference the prior chain (S1 gt-gnh7m → … → S12 gt-9050ks → …) so
`bd show` walks the lineage. The `/handoff-bead` skill does the mechanics.

## 2. Expand the run-log

Append this session's `S<N>.x` rows to `~/gt/mathcity-tests/run-log.md`
(command → result trust record; Taylor values it highly). Never rewrite
prior sessions' rows.

## 3. Add the session-catalog entry

Append ONE JSON entry to `~/gt/mathcity-mayor/session-catalog.json`:

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

The next session's QUIMBY number, ordinals, and handoff-bead content are
computed from this entry by `mayor-math-prime`'s renderer — write only the
narrative fields, and write them carefully: they ARE the next session's
prime input.

## 4. Update the restart PROMPT

Home: `~/gt/mathcity-mayor/restart/PROMPT-mayor-restart.txt`.

Update it for the next session: refresh the S<N>→S<N+1> update block, state
of the city, standing rules (only if they changed), the charge, and the
handoff-bead chain. Two acceptable ways:

- **Curated edit (default):** edit the file directly, preserving the curated
  standing-rules prose that the jinja render does not capture.
- **Regenerate:** after step 3, render from the template:
  ```bash
  bash ~/gt/gascity-packs/mathcity/skills/mayor-math-prime/scripts/render-prime.sh \
    > ~/gt/mathcity-mayor/restart/PROMPT-mayor-restart.txt
  ```
  Only do this if the jinja render (`restart/PROMPT-mayor-restart.j2`)
  carries everything the next session needs — otherwise curate by hand.

Do NOT write to `~/Documents/misc/PROMPT-mayor-restart.txt` — that location
is retired (a pointer file remains there).
