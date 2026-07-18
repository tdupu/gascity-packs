---
name: mayor-math-handoff
description: SESSION-END handoff for the math-city Mayor (QUIMBY). Writes the chained handoff bead, expands the run-log, adds the session-catalog entry, and updates the restart PROMPT so the next Mayor session can prime from it. Run at the END of every QUIMBY session — directly, or as the first half of mayor-math-restart (handoff → clear → prime). Trigger phrases: "mayor-math-handoff", "hand off the mayor session", "end the QUIMBY session", "write the mayor handoff".
---

# mayor-math-handoff

The QUIMBY SESSION-END procedure — the first half of the restart cycle
(**`mayor-math-handoff`** → `/clear` → `mayor-math-prime`). Do ALL FIVE steps,
in this order (the catalog entry must exist before the PROMPT is regenerated):

State dir: `~/gt/mathcity-mayor/` (override with `MAYOR_STATE_DIR`).
Restart PROMPT home: `~/gt/mathcity-mayor/restart/` (moved from
`~/Documents/misc/PROMPT-mayor-restart.txt` on 2026-07-16).

## 0. Check-zero gate (before writing anything)

Run `/check-zero` on the draft content for the handoff bead body and the
PROMPT update BEFORE committing either to disk or bd. This catches
hallucinated commands, fabricated bead IDs, mathematical claims without
source, and ZFC violations before they propagate to the next session.

Minimum checks:
- Every bead ID cited in the body resolves via `bd show <id>`.
- Every command cited (`gc sling`, `git push`, etc.) actually exists in the
  city surface (`gc --help`, `git --help`).
- No mathematical claims appear that were not verified at source this session.
- No file paths are cited that do not exist on disk (`ls <path>`).

Fail → revise the draft. Do not proceed to step 1 until the draft is clean.

## 1. Write the handoff bead (chained)

Write a `gt-` handoff bead holding this session's full arc (what was done,
what was verified at source, open threads, warnings for the next QUIMBY).
Reference the prior chain (S1 gt-gnh7m → … → S12 gt-9050ks → …) so
`bd show` walks the lineage. The `/handoff-bead` skill does the mechanics.

## 2. Write a run-log shard

Write this session's `S<N>.x` rows to a **new shard file**
`~/gt/mathcity-tests/run-log/S<N>.md` (where N is your session number).
Do NOT append to the `run-log.md` monolith — it is a frozen 190KB archive;
`mayor-math-prime` reads shards from the directory, not the monolith.

Format: begin with `## S<N> — QUIMBY <N> (<date>, written by <agent>)`,
then one `S<N>.x` subsection per topic (triage, infra, math, handoff).
Never rewrite prior sessions' rows.

## 3. Add the session-catalog entry (BOTH files)

Append ONE JSON entry to **both** catalog files in the same close step —
they must never drift (a missing recent-catalog entry trips the next
session's consistency guard):

- `~/gt/mathcity-mayor/session-catalog.json` — full history
- `~/gt/mathcity-mayor/session-catalog-recent.json` — keep last 5 entries only

Entry shape:

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

Keep `summary`, `city_state`, and `charge_for_next` ≤ ~40 words each —
a pointer to the handoff bead, not a retelling of it. These ARE the next
session's prime input; write them carefully.

To update `session-catalog-recent.json` (keep last 5):
```bash
python3 -c "
import json, pathlib
p = pathlib.Path('/Users/tdupuy/gt/mathcity-mayor/session-catalog-recent.json')
data = json.loads(p.read_text())
data.append({NEW_ENTRY})
data = data[-5:]
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
"
```

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
