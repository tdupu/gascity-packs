---
name: mayor-math-restart
description: Full QUIMBY session orientation. Run at the start of every new QUIMBY (math-city Mayor) session. Reads the restart prompt, the durable operation docs, and the session catalog so a fresh session can operate the city the way the current QUIMBY does.
---

# mayor-math-restart

Full QUIMBY onboarding. (There is NO auto-injecting PreToolUse hook — this skill
reads its own context. Corrected 2026-07-16.) Do these in order:

## 1. Read the bounded context (~30KB total — do not exceed)

**Mandatory reads (always):**

1. **`~/gt/mathcity-mayor/restart/PROMPT-mayor-restart.txt`** — this session's background,
   standing rules, city state, and charge.
2. **`~/gt/gascity-packs/mathcity/docs/QUIMBY-ONBOARDING.md`** — S11-corrected operational
   truths (the gold). Contains pointer to CITY-RESTART-CHECKLIST.md.
3. **`~/gt/gascity-packs/mathcity/docs/CITY-RESTART-CHECKLIST.md`** — Phase 0–6 step-by-step
   to bring the city up + verify.
4. **`~/gt/mathcity-mayor/session-catalog-recent.json`** — last 5 QUIMBY sessions (arc,
   city state, charge). Full history is in `session-catalog.json` if needed.
5. **Latest shard** in `~/gt/mathcity-tests/run-log/` — find and read it:
   ```bash
   ls -t ~/gt/mathcity-tests/run-log/*.md | grep -v archive | head -1
   ```
   Read that file (~3–10KB). It holds the prior session's S<N>.x rows.
6. **Handoff bead** named in the PROMPT (`bd show <id>`).

**On-demand only (NOT at startup). Each doc carries its own integrity guard — obey it.**

- [`CITY-OPERATION-REFERENCE.md`](../../docs/CITY-OPERATION-REFERENCE.md) (32KB) — architecture, command surface, brief pipeline.
  *Trigger: verifying a command exists, diagnosing fleet / brief-pipeline issues.*
- [`TEST-CYCLE-GUIDE.md`](../../docs/TEST-CYCLE-GUIDE.md) (11KB) — test/triage cycle.
  *Trigger: before running any test or triaging a pipeline failure.*
- [`DOGFOOD-WORKFLOW.md`](../../docs/DOGFOOD-WORKFLOW.md) (11KB) — hotfix → hygienic loop, ~/gt↔~/repos duality.
  *Trigger: before applying a hotfix, making a pack change, or deploying anything.*
- [**Policies**](../../docs/QUIMBY-ONBOARDING.md#policies) — see the Policies section of QUIMBY-ONBOARDING.md for the full navigation tree.

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

1. Write a handoff bead.
2. Update `~/gt/mathcity-mayor/restart/PROMPT-mayor-restart.txt`.
3. Write session notes to a **new shard file** `~/gt/mathcity-tests/run-log/S{N}.md`
   (where N is your session number). Do NOT append to the old `run-log.md` monolith —
   it is preserved as archive but not extended.
4. Add one entry to **both** `session-catalog.json` (full record) and
   `session-catalog-recent.json` (keep last 5):

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

To update `session-catalog-recent.json` (keep last 5 entries):
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
