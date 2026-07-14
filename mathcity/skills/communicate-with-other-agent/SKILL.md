---
name: communicate-with-other-agent
description: |
  Send and read messages between concurrent Claude Code agents via the shared inbox
  ~/gt/.claude/.agent-inbox.md. Use for "tell the other agent", "message agent X",
  "send this to <UUID>", "check the agent inbox".
---

# communicate-with-other-agent

Shared inbox: `~/gt/.claude/.agent-inbox.md`.
Your UUID: `$CLAUDE_CODE_SESSION_ID`, else the stem of the newest
`*.jsonl` in `~/.claude/projects/<hash>/`. Format `[a-f0-9-]{36}`.

## STEP 0 — Monitor (do first, keep alive)

Arm it with the **Monitor tool, `persistent: true`**:

```
bash ~/.claude/scripts/agent-monitor.sh ~/gt/.claude/.agent-inbox.md <YOUR_UUID>
```

The monitor DIES (harness kills, file rotation, session recovery) and you go
deaf when it does. So:

- Before each send, check `TaskList`. If no live task is watching the inbox,
  **re-arm** before doing anything else. One live monitor only — don't stack.
- At every natural pause, tail-check anyway as backup:
  `grep -n "^to:.*<YOUR_UUID>" ~/gt/.claude/.agent-inbox.md | tail`
- When it fires, `Read` the inbox for the full body.

## Send

Write the body with the Write tool (never `>>`), then send:

```bash
bash ~/.claude/scripts/agent-send.sh "$FROM" "$TO" "Subject" /tmp/body.md ~/gt/.claude/.agent-inbox.md
```

Args: `FROM_UUID  TO_UUID  "Subject"  BODY_FILE  INBOX_PATH`. The 5th arg is
mandatory — omitting it breaks routing. Always send to the SHARED inbox above,
not a per-agent inbox file, or the recipient's monitor won't see it.

## Read

`Read` the inbox, or filter: `grep -A30 "^to:.*<YOUR_UUID>" <inbox>`.

## Conventions

- Subject ≤80 chars. Sign the last line `-- <uuid-prefix> (<name>)`.
- One topic per message. ACK proposals before acting.
- Don't start cross-agent threads without user approval.
