---
name: bead-promote
description: >-
  Promote a bead from user-space to city-managed by stamping gc.origin=user
  on its metadata. Idempotent: skips silently if gc.origin is already set.
  Trigger phrases: "gc bead promote", "promote bead", "stamp gc.origin",
  "move bead to city", "promote <bead-id>".
---

# bead-promote

Stamp `gc.origin=user` on a bead to promote it from user-space into the
city's managed bead graph. This is the pack-level implementation of
`gc bead promote` — it uses `bd update --set-metadata` and works in any
city with the `gascity` pack imported.

## Step 0 — Resolve the bead ID

Identify the bead to promote from the user's request. If the user says
"promote <id>" or "gc bead promote <id>", use that ID directly.

If no ID is given, ask the user which bead to promote before proceeding.

```bash
BEAD_ID="<bead-id>"
```

## Step 1 — Idempotency check

Read the bead's current metadata and confirm `gc.origin` is not already set:

```bash
EXISTING_ORIGIN=$(bd show "$BEAD_ID" --json | jq -r '.[0].metadata."gc.origin" // ""')
```

If `EXISTING_ORIGIN` is non-empty, output:

```
bead-promote: $BEAD_ID already has gc.origin=$EXISTING_ORIGIN — no change needed.
```

Stop here. Do not overwrite an existing `gc.origin` value.

## Step 2 — Promote

Stamp the metadata:

```bash
bd update "$BEAD_ID" --set-metadata "gc.origin=user"
```

If the command fails (bead not found, permission error, etc.), report the
exact error and stop — do not retry blindly.

## Step 3 — Confirm

Verify the stamp was written:

```bash
bd show "$BEAD_ID" --json | jq -r '.[0].metadata."gc.origin"'
```

Output a confirmation message:

```
bead-promote: $BEAD_ID promoted — gc.origin=user set.
```

## Hard rules

- **Never overwrite an existing gc.origin.** The idempotency check in Step 1
  is mandatory. Overwriting a city-assigned origin (e.g. `gc.origin=city`)
  could break routing or ownership invariants.
- **Never promote a bead that is already closed.** Check `bd show "$BEAD_ID"`
  and confirm `status != closed` before stamping. If it is closed, report:
  "bead-promote: $BEAD_ID is already closed — cannot promote a closed bead."
- **One bead at a time.** This skill promotes exactly one bead per invocation.
  If the user asks to promote multiple beads, run the steps once per bead ID
  in sequence, confirming each one before proceeding to the next.

## Notes

- `gc.origin=user` signals that the bead was authored by the human user and
  should participate in city-managed routing (formula dispatch, convoy
  membership, etc.).
- The binary subcommand `gc bead promote` will follow as a separate upstream
  PR (C.5 in the packs roadmap) after this formula-level implementation is
  proven stable locally.
