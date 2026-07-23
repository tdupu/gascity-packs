---
name: present-briefs
description: Present briefs one at a time in full form, maintaining a pre-loaded hot queue so the next brief is always ready the moment a decision is made. Use when the user wants to process briefs, says "next", "next brief", "Next", "continue", "what's next", "present my next brief", "next from queue", "show me the queue", "I'm ready for the next one", "keep the queue warm", or wants to churn through a backlog of briefs. Always presents one brief at a time in full — no summarizing, no batching multiple briefs in one response.
---

# present-briefs

Presents briefs **one at a time, in full**, while pre-loading the next brief in the background so Taylor never waits between decisions.

**Origin:** Taylor 2026-06-30 — "You should have a queue. This is dumb. We should be ready to go." — after watching a session manually fan out parallel subagents to pre-load briefs. Updated 2026-07-22: one brief at a time, always full form.

## When to use

- "Next" / "Next brief" / "Continue" / "What's next" — any brief-advance signal after a verdict
- "Present my next brief"
- "Next from the ripe queue"
- "Show me the brief queue"
- "I'm ready for the next one" → present pre-loaded brief + pre-load the one after
- Any time Taylor wants to process a backlog without waiting between briefs

## Inputs

Via args (space-separated or comma-separated):

| Arg | Default | Meaning |
|-----|---------|---------|
| `--artifacts a,b,c` | (ripe queue) | Explicit artifact list; bypasses queue discovery |
| `--queue-path <dir>` | auto-discover | Override brief-stack directory |

Examples:
- `/present-briefs` → present top brief from ripe queue, pre-load next
- `/present-briefs --artifacts he-wzn,he-x8dk` → present he-wzn, pre-load he-x8dk

## Queue Discovery

When no explicit artifact list is given, discover the ripe queue (approved briefs awaiting Taylor's decision):

### Method 1 — beads query (preferred)

```bash
bd list --status open --metadata-field brief_status=approved \
  --limit 0 --json 2>/dev/null \
  | jq 'sort_by(.metadata.unlock_count | -(.//0))
        | .[] | {id: .id, artifact: (.metadata.artifact // .id),
                 path: .metadata.brief_path, unlock: (.metadata.unlock_count//0)}'
```

### Method 2 — directory scan (fallback)

```bash
BRIEF_DIR="${BRIEF_QUEUE_PATH:-$HOME/gt/.beads/briefs}"
find "$BRIEF_DIR" -maxdepth 1 -name "*.md" \
  | xargs grep -l "^status: approved" 2>/dev/null \
  | while read f; do
      unlock=$(grep -m1 "^unlock_count:" "$f" | awk '{print $2}')
      echo "${unlock:-0} $f"
    done \
  | sort -rn | awk '{print $2}'
```

Sort order: **unlock_count descending** (highest unblocking value first).

If queue is empty: report "No ripe briefs in queue. Run /brief-prep on pending artifacts first." and exit.

## Execution

### Phase 1 — discover and select

1. Run queue discovery (above).
2. Take the top item (the next unpresented brief).
3. Log: "Presenting: [artifact-id] (unlock_count=N) · [M remaining in queue]"

### Phase 2 — pre-load next in background

While presenting the current brief, immediately start pre-loading the next one:

```javascript
// Fire and forget — loads while Taylor reads
agent(`Read the brief file for <next-artifact> at <path> and return its complete contents verbatim.`,
      { label: `preload:${nextArtifact}` })
```

### Phase 3 — present current brief in FULL

**Present the complete brief text verbatim.** No summarizing. No condensing. No omitting sections. The full `.md` file content, rendered as-is, inside the header/footer block:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRIEF · <artifact-id> · unlock_count=<int>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<complete brief text — every section, every line>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUEUE: [artifact-id] presented · [M] remaining
Pre-loading: [next-artifact-id]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Brief quality gate:** If the brief has fewer than 7 sections (§1–§7 minimum), do NOT present it — send it back for brief preparation with: "Brief [artifact] has only [N] sections — returning to prep queue. Run /brief-prep on [artifact]."

### Phase 4 — wait for verdict, then cycle

When Taylor gives a verdict:
1. Look up the full slug from the manifest (`manifest.jsonl` entry where `source == artifact_id`; use its `slug` field)
2. Invoke `brief-record-decision` via `gc sling`:
   ```bash
   gc sling <rig>/gc.run-operator brief-record-decision --formula \
     --var brief_slug=<slug> \
     --var decision=<approve|reject|revise|defer> \
     --var reason="<Taylor's stated reason, or empty string>"
   ```
   Map Taylor's words: "approve"/"yes"/"ship it" → `approve`; "reject"/"no"/"drop it" → `reject`; "revise"/"fix it"/"update it" → `revise`; "defer"/"later"/"not now"/"skip" → `defer`.
3. Acknowledge: "Decision recorded: [artifact] → [choice]"
4. Present the pre-loaded next brief immediately (use the content already fetched in Phase 2 — no wait)
5. Start pre-loading the brief after that

## Tracking state (in-session)

```
presented:    [set of artifact IDs already shown this session]
hot:          [next pre-loaded (artifact, brief-text) pair — always 1 ahead]
queue:        [remaining artifacts not yet presented, in priority order]
```

On each decision: `hot` → present immediately; `queue.pop(0)` → fan out to refill `hot`.

## Error handling

| Situation | Action |
|-----------|--------|
| Brief has fewer than 7 sections | Return to prep queue; skip to next |
| Brief `status` is not `approved` | Skip with note; continue to next |
| Brief source bead has `Status: HELD` | Skip with note; continue to next |
| Queue empty at startup | "No ripe briefs. Run /brief-prep on pending artifacts first." |
| Queue drains mid-session | "Queue exhausted — [N] presented, 0 remaining." |

## Invariants

- **One brief per response**: never present more than one brief in a single response
- **Full text always**: present the complete brief verbatim — no summarizing, no condensing
- **Hot pre-load**: always have the next brief pre-loading while Taylor reads the current one
- **Sort order**: unlock_count descending (highest unblocking value first)
- **No double-presentation**: track presented IDs to avoid re-presenting in same session

## Composes with

- **`/adjudicate-brief`** — records Taylor's verdict and closes the brief bead
- **`/math-city-work`** — dispatches approved artifacts (clerk runs this after approve)
- **`/brief-prep`** — upstream producer that populates the ripe queue with approved briefs
- **Brief-pipeline substrate** — the brief-stack (`~/gt/.beads/briefs/`) this skill consumes

## What this skill does NOT do

- Does not create or modify briefs (that's `/brief-prep`)
- Does not record decisions unilaterally — Taylor's verdict is the trigger
- Does not call `bd close` on any bead directly
- Does not push any commits
- Does not present multiple briefs in one response
