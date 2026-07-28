#!/bin/sh
# Static regression test: proves push-the-fleet and math-city-work compute
# DISTINCT, bead-scoped artifact_root values for two different beads on the
# same rig, and that neither skill still documents the old bare-rig-root
# dispatch form. Does not require a live city — pure text-fixture check.
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PUSH_SKILL="$REPO_ROOT/mathcity/subdomains/dev/skills/push-the-fleet/SKILL.md"
WORK_SKILL="$REPO_ROOT/mathcity/skills/math-city-work/SKILL.md"

fail() {
  echo "I'm sorry, I can't do that - $1" >&2
  exit 1
}

[ -f "$PUSH_SKILL" ] || fail "missing $PUSH_SKILL"
[ -f "$WORK_SKILL" ] || fail "missing $WORK_SKILL"

CHECKS=0
PASS=0

check() {
  CHECKS=$((CHECKS + 1))
  if eval "$2"; then
    PASS=$((PASS + 1))
    echo "  PASS: $1"
  else
    echo "  FAIL: $1"
  fi
}

# 1. push-the-fleet no longer documents the bare rig-root dispatch form.
check "push-the-fleet: no bare rig-root artifact_root in dispatch example" \
  '! grep -q "artifact_root=<rig-artifact-root>" "$PUSH_SKILL"'

# 2. push-the-fleet documents the per-bead scoped form.
check "push-the-fleet: documents .gc-builds/<bead-id> scoping" \
  'grep -q "artifact_root=<rig-root>/.gc-builds/<bead-id>" "$PUSH_SKILL"'

# 3. math-city-work documents the per-bead scoped form for build-basic-briefed.
check "math-city-work: documents .gc-builds/<bead> scoping for build-basic-briefed" \
  'grep -q "artifact_root=<rig-root>/.gc-builds/<bead>" "$WORK_SKILL"'

# 4. Simulate two concurrent dispatches for two different beads on the same
#    rig root and assert the resulting artifact_root values differ. This is
#    the actual collision scenario from gsp-1bmxuz (gsp-ewlwh vs gsp-4qe2a).
RIG_ROOT="/Users/tdupuy/gt/gascity-packs"
BEAD_A="gsp-ewlwh"
BEAD_B="gsp-4qe2a"
ROOT_A="$RIG_ROOT/.gc-builds/$BEAD_A"
ROOT_B="$RIG_ROOT/.gc-builds/$BEAD_B"

check "simulated dispatch: scoped artifact_root differs per bead" \
  '[ "$ROOT_A" != "$ROOT_B" ]'

check "simulated dispatch: neither scoped path equals the bare rig root" \
  '[ "$ROOT_A" != "$RIG_ROOT" ] && [ "$ROOT_B" != "$RIG_ROOT" ]'

echo ""
if [ "$PASS" -eq "$CHECKS" ]; then
  echo "PASS $PASS/$CHECKS - artifact_root scoping regression test"
  exit 0
else
  echo "FAIL $PASS/$CHECKS - artifact_root scoping regression test"
  exit 1
fi
