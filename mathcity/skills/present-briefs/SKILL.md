---
name: present-briefs
description: Batch-present N briefs in parallel and maintain a hot queue (≥2 pre-presented at all times). Use when the user wants to process multiple briefs, says "present my next N briefs", "next N from queue", "show me the queue", "brief queue", "batch present", "I'm ready for the next one", "keep the queue warm", or wants to churn through a backlog of briefs without waiting between each one. Wraps /present-it for single artifacts; this skill fans out over N in parallel, batches outputs, and auto-backfills on each decision. Not for presenting a single artifact — use /present-it for that.
---

# present-briefs

Formalizes the batch-present + hot-queue pattern: Taylor says "next N" and gets N briefs pre-loaded in parallel, with the queue auto-backfilling so a new brief is always ready the moment a decision is made.

**Origin:** Taylor 2026-06-30 — "You should have a queue. This is dumb. We should be ready to go." — after watching a session manually fan out parallel subagents to pre-load briefs. This skill formalizes that pattern.

## When to use

- "Present my next 3 briefs"
- "Next 2 from the ripe queue"
- "Show me the brief queue"
- "I'm ready for the next one" → implies hot-queue refill
- Any time Taylor wants to process a backlog without waiting for each brief to load

Do NOT use for a single artifact. Use `/present-it` for that.

## Inputs

Via args (space-separated or comma-separated):

| Arg | Default | Meaning |
|-----|---------|---------|
| `N` or `--count N` | 2 | Number of briefs to pre-load in parallel |
| `--artifacts a,b,c` | (ripe queue) | Explicit artifact list; bypasses queue discovery |
| `--queue-path <dir>` | auto-discover | Override brief-stack directory |

Examples:
- `/present-briefs` → load next 2 from ripe queue
- `/present-briefs 3` → load next 3 from ripe queue
- `/present-briefs --artifacts feat/he-wzn,he-x8dk,#317` → present these 3 explicitly

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
2. Take the top N items.
3. Log: "Loading N briefs in parallel: [artifact-1, artifact-2, ...]"

### Phase 2 — fan out in parallel

Use the Workflow tool with `parallel()` to run `/present-it` on each artifact simultaneously:

```javascript
const ARTIFACTS = [...]; // top N from queue
const results = await parallel(
  ARTIFACTS.map(artifact => () =>
    agent(`Run /present-it on: ${artifact}. Return the complete brief text.`,
          { label: `present:${artifact}` })
  )
);
```

Wall-clock time = slowest single artifact, not sum.

If workflow tool is unavailable (environment without subagent dispatch), fall through to sequential presentation — one artifact at a time — with a note: "(Sequential mode — workflow fan-out unavailable)"

### Phase 3 — batch display

Present all N briefs to the user in one block:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRIEF [1/N] · <artifact-id> · unlock_count=<int>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<full /present-it output>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRIEF [2/N] · <artifact-id> · unlock_count=<int>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<full /present-it output>

...

QUEUE: N presented · M remaining · pre-loading next batch now…
```

End with the queue summary line and immediately begin pre-loading the next batch (Phase 4).

### Phase 4 — hot queue maintenance (auto-backfill)

**Invariant: ≥2 briefs must be pre-presented at all times.**

After the initial batch:
1. Track which artifacts have been presented (in-session set).
2. Immediately pre-load the next N items from the remaining queue in the background.
3. When the user makes a decision on any brief:
   - Look up the full slug from the manifest (find `manifest.jsonl` entry where `source == artifact_id`; use its `slug` field)
   - Invoke `brief-record-decision` via `gc sling`:
     ```bash
     # Identify rig from brief path (e.g. ~/gt/.beads/briefs → hecke)
     gc sling <rig>/gc.run-operator brief-record-decision --formula \
       --var brief_slug=<slug> \
       --var decision=<approve|reject|revise|defer> \
       --var reason="<Taylor's stated reason, or empty string>"
     ```
     Map Taylor's words: "approve"/"yes"/"ship it" → `approve`; "reject"/"no"/"drop it" → `reject`; "revise"/"fix it"/"update it" → `revise`; "defer"/"later"/"not now"/"skip" → `defer`.
   - Acknowledge: "Decision recorded: [artifact] → [choice] (brief-record-decision slung)"
   - Present the next pre-loaded brief immediately (no wait)
   - Pre-load one more from the queue to refill the hot slot
4. The user should never wait for a presentation to be generated.

**Backfill trigger phrases:** "next", "I'm ready", "continue", "what's next", "next brief", "show me another", any decision on a presented brief.

## Tracking state (in-session)

Maintain a simple in-session queue structure:

```
presented:    [set of artifact IDs already shown]
hot:          [list of pre-loaded (artifact, brief-text) pairs, ≥2]
queue:        [remaining artifacts not yet presented, in priority order]
```

On each decision: `hot.pop(0)` → present immediately; `queue.pop(0)` → fan out to refill hot.

## Error handling

| Situation | Action |
|-----------|--------|
| `/present-it` fails on artifact | Skip with note, continue to next; report failure at end |
| Queue empty at startup | "No ripe briefs. Run /brief-prep on pending artifacts first." |
| Queue drains mid-session | "Queue exhausted — N presented, 0 remaining." |
| N < 1 | Default to N=2 |
| N > 5 | Warn: "Large batch — fan-out will be slow. Proceeding with N=5." Cap at 5. |

## Invariants

- **Hot queue depth**: ≥2 briefs pre-presented while queue has items remaining
- **Sort order**: unlock_count descending (highest unblocking value first)
- **No double-presentation**: track presented IDs to avoid re-presenting in same session
- **Immediate backfill**: pre-loading starts before Taylor acknowledges the current batch

## Composes with

- **`/present-it`** — single-artifact presentation (this skill wraps it); delegates all research and brief-writing there
- **`/brief-prep`** — upstream producer that populates the ripe queue with approved briefs
- **Brief-pipeline substrate** — the brief-stack (`~/gt/.beads/briefs/`) this skill consumes
- **Workflow tool** — powers the parallel fan-out in Phase 2

## What this skill does NOT do

- Does not create or modify briefs (that's `/brief-prep`)
- Does not record decisions unilaterally — Taylor's verdict is the trigger; this skill invokes `brief-record-decision` after each verdict
- Does not call `bd close` on any bead
- Does not push any commits
