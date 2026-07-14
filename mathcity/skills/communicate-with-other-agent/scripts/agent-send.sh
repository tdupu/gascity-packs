#!/usr/bin/env bash
# agent-send.sh — V2: per-recipient inbox + hybrid rotation trigger
# Usage: agent-send.sh FROM TO SUBJECT BODY_FILE [INBOX_DIR_OVERRIDE]
#
# Writes to <INBOX_DIR>/<TO>.md instead of the V1 shared <PROJECT>/.claude/.agent-inbox.md.
# Calls agent-inbox-rotate.sh on the target recipient file before append, so the
# 4h-or-30-entries hybrid trigger fires lazily on each send.
#
# Inbox-dir resolution precedence (highest wins):
#   1. INBOX_DIR_OVERRIDE positional arg (5th) — explicit caller-supplied path
#   2. $CLAUDE_INBOX_DIR environment variable
#   3. CWD walk-up looking for .claude/inbox/ (V2) or .claude/.agent-inbox.md (V1)
#   4. Fallback: $(pwd)/.claude/inbox/
#
# The 5th positional arg is OPTIONAL — backward-compatible with 4-arg callers.
set -euo pipefail

FROM="$1"; TO="$2"; SUBJECT="$3"; BODY_FILE="$4"
INBOX_DIR_OVERRIDE="${5:-}"

UUID_RE='^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
[[ "$FROM" =~ $UUID_RE ]] || { echo "bad FROM uuid: $FROM" >&2; exit 2; }
[[ "$TO"   =~ $UUID_RE ]] || { echo "bad TO uuid: $TO" >&2; exit 2; }
[[ -f "$BODY_FILE" ]] || { echo "body file missing: $BODY_FILE" >&2; exit 2; }

# --- Inbox directory resolution (V2) ---
# Precedence: explicit override arg > $CLAUDE_INBOX_DIR > CWD walk-up > pwd fallback.
INBOX_DIR=""
if [[ -n "$INBOX_DIR_OVERRIDE" ]]; then
    INBOX_DIR="$INBOX_DIR_OVERRIDE"
    mkdir -p "$INBOX_DIR"
else
    INBOX_DIR="${CLAUDE_INBOX_DIR:-}"
fi
if [[ -z "$INBOX_DIR" ]]; then
    dir="$(pwd)"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.claude/inbox" ]]; then
            INBOX_DIR="$dir/.claude/inbox"
            break
        fi
        if [[ -f "$dir/.claude/.agent-inbox.md" ]]; then
            INBOX_DIR="$dir/.claude/inbox"
            mkdir -p "$INBOX_DIR"
            echo "LEGACY_INBOX_DETECTED: $dir/.claude/.agent-inbox.md — run agent-inbox-migrate.sh to upgrade" >&2
            break
        fi
        dir="$(dirname "$dir")"
    done
fi
if [[ -z "$INBOX_DIR" ]]; then
    INBOX_DIR="$(pwd)/.claude/inbox"
    mkdir -p "$INBOX_DIR"
fi
mkdir -p "$INBOX_DIR/archive"

INBOX="$INBOX_DIR/$TO.md"
[[ -f "$INBOX" ]] || touch "$INBOX"

# Hybrid rotation trigger before append (4h elapsed OR ≥30 entries OR legacy day change).
bash "$(dirname "$0")/agent-inbox-rotate.sh" "$INBOX_DIR" "$TO" || true

TS=$(date '+%Y-%m-%d %H:%M:%S %z')

{
  printf '\n---\nfrom: %s\nto:   %s\nat:   %s\nsubject: %s\n---\n' \
    "$FROM" "$TO" "$TS" "$SUBJECT"
  cat "$BODY_FILE"
  printf '\n'
} >> "$INBOX"

echo "sent at $TS to $INBOX"
