#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FORMULA="$ROOT/formulas/brief-producer-failure-rollup.toml"

require_text() {
  local pattern="$1"
  local message="$2"
  if ! rg -q -- "$pattern" "$FORMULA"; then
    printf 'producer-failure-rollup routing check failed: %s\n' "$message" >&2
    exit 1
  fi
}

require_text 'repair_rig_dir="\$\(gc rig list --json' 'repair bead must be created/found in the target rig store'
require_text 'bd -C "\$repair_rig_dir" show "\$repair_bead"' 'assignee guard must inspect the target rig store'
require_text '--var operator_target="gascity-packs/gc.run-operator"' 'repair workflow must keep child steps in the target rig store'
require_text 'repair_workflow="\$\(printf' 'dispatch verification must check the returned workflow root'
require_text 'bd -C "\$repair_rig_dir" show "\$repair_workflow"' 'workflow verification must inspect the target rig store'

printf 'producer-failure-rollup routing check: ok\n'
