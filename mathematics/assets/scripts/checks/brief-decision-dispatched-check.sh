#!/bin/sh
# Idempotency check for brief-decision-dispatch.
#
# Verifies that every pending slug has been appended to the dispatch ledger
# (.beads/briefs/decisions-dispatched.jsonl). Used as the step check for
# the dispatch-decisions step — ensures the dispatched record is durable
# before the step completes, and prevents re-dispatch of the same slug.
#
# exit 0  -> all processed slugs appear in the dispatch ledger (success)
# exit 1  -> one or more processed slugs are missing from the ledger (retry)
#
# Inputs (env):
#   BRIEF_ROOT            brief pipeline artifact root (default: .beads/briefs)
#   PENDING_SLUGS         space-separated list of slugs that were dispatched
#                         (set by scan-undispatched step); if empty, exit 0
set -eu

ROOT="${BRIEF_ROOT:-.beads/briefs}"
LEDGER="$ROOT/decisions-dispatched.jsonl"
PENDING="${PENDING_SLUGS:-}"

fail() {
  echo "brief-decision-dispatched-check: $*" >&2
  exit 1
}

# If no slugs were pending, nothing to verify.
if [ -z "$(echo "$PENDING" | tr -d ' ')" ]; then
  echo "no pending slugs; dispatch check passes vacuously"
  exit 0
fi

# The ledger must exist once dispatch has run.
[ -f "$LEDGER" ] || fail "missing dispatch ledger: $LEDGER"

# Each pending slug must appear in the ledger.
missing=""
for slug in $PENDING; do
  if ! grep -q "\"$slug\"" "$LEDGER" 2>/dev/null; then
    missing="$missing $slug"
  fi
done

if [ -n "$(echo "$missing" | tr -d ' ')" ]; then
  fail "slugs not yet in dispatch ledger: $missing"
fi

echo "brief-decision-dispatched-check: all pending slugs found in $LEDGER"
exit 0
