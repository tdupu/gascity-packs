---
name: mayor-math-restart
description: Full QUIMBY session orientation. Restart context (session history, handoff bead, city state, charge) is auto-injected via PreToolUse hook before this skill fires. Run at the start of every new QUIMBY session instead of manually reading PROMPT-mayor-restart.txt.
---

# mayor-math-restart

The restart context for this session has been injected above by the PreToolUse hook.

Read it carefully, then:

1. Run `/prime-outsider` to check open beads and current handoff bead status.
2. Report the session's top priority to Taylor before taking any other action.
3. Confirm with BART what BART is supposed to be doing before starting work.

At session end, add one entry to `~/gt/mathcity-mayor/session-catalog.json`:

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
