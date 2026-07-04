#!/usr/bin/env bash
# catch-no-brainer v0.1 fixture harness.
# Implements the SKILL.md classification rules over the 6 fixture briefs.
# Pass-bar: all 6 fixtures classify with the expected verdict shape. Exit 0 = PASS.
set -euo pipefail

cd "$(dirname "$0")"

classify_brief() {
  local f="$1"
  local fm
  fm=$(awk '/^---$/{c++; next} c==1{print}' "$f")

  yaml_get() { echo "$fm" | grep -E "^$1:" | head -1 | sed -E "s/^$1:[[:space:]]*//"; }
  yaml_list() { echo "$fm" | awk -v k="$1:" 'index($0,k)==1{i=1;next} /^[A-Za-z_]+:/{i=0} i && /^[[:space:]]+- /{sub(/^[[:space:]]+- /,""); print}'; }

  local branch verdict parent_closed parent_super downstream files cap_block
  branch=$(yaml_get branch)
  verdict=$(yaml_get verdict)
  parent_closed=$(yaml_get parent_bead_closed)
  parent_super=$(yaml_get parent_bead_supersession_documented)
  downstream=$(yaml_get downstream_beads_reference)
  files=$(yaml_list diff_files)
  cap_block=$(yaml_get capability_blocker)

  # Step 1: server-touching (he-xkq3 G5 fires before G9)
  local server_re='magma/scripts/dispatch\.sh|magma/make/dispatch/|^gt-dolt|^gt-upf|\.gc/daemon|\.dolt-data/|\.gc/agent-bridge/|aia-s27'
  if echo "$files" | grep -E "$server_re" >/dev/null 2>&1; then
    printf '{"brief_path":"%s","bead_id":null,"no_brainer":false,"category":null,"reason":"cat-E-server-touching","compact_eligible":false,"proposed_registry_extension":null,"requires_taylor_adjudication":false,"classified_at":"v0.1-dryrun"}\n' "$f"
    return 0
  fi

  # Step 2: user-skill-touching (as-wjv SAFETY OVERRIDE)
  local userskill_re='\.claude/skills/|repos/agent-skills/skills/'
  if echo "$files" | grep -E "$userskill_re" >/dev/null 2>&1; then
    printf '{"brief_path":"%s","bead_id":null,"no_brainer":false,"category":null,"reason":"user-skill-touching-override","compact_eligible":false,"proposed_registry_extension":null,"requires_taylor_adjudication":false,"classified_at":"v0.1-dryrun"}\n' "$f"
    return 0
  fi

  # Step 3: capability-blocker shape
  if [[ -n "$cap_block" ]]; then
    printf '{"brief_path":"%s","bead_id":null,"no_brainer":false,"category":"capability-blocker","reason":"resolve %s","compact_eligible":false,"proposed_registry_extension":null,"requires_taylor_adjudication":false,"classified_at":"v0.1-dryrun"}\n' "$f" "$cap_block"
    return 0
  fi

  # Step 4: he-lele 5-criterion
  local branch_ok=0 files_ok=1
  [[ "$branch" =~ ^(polecat|nux|[a-z]+-prefix)/ ]] && branch_ok=1
  if echo "$files" | grep -E '^(magma|latex|notes\.tex|DATA|configs)' >/dev/null 2>&1; then files_ok=0; fi
  if [[ "$branch_ok" == "1" ]] \
      && [[ "$parent_closed" == "true" ]] \
      && [[ "$parent_super" == "true" ]] \
      && [[ "$files_ok" == "1" ]] \
      && [[ "$downstream" == "false" ]] \
      && [[ "$verdict" =~ ^(DELETE|INVESTIGATE)$ ]]; then
    printf '{"brief_path":"%s","bead_id":null,"no_brainer":true,"category":"stale-branch","reason":null,"compact_eligible":true,"proposed_registry_extension":null,"requires_taylor_adjudication":false,"classified_at":"v0.1-dryrun"}\n' "$f"
    return 0
  fi

  # Step 5: novel shape (proposed registry extension is one-line synthesis from the failing criteria)
  local why="branch=$branch verdict=$verdict supersession=$parent_super"
  printf '{"brief_path":"%s","bead_id":null,"no_brainer":"candidate","category":null,"reason":null,"compact_eligible":false,"proposed_registry_extension":"new shape candidate: %s","requires_taylor_adjudication":true,"classified_at":"v0.1-dryrun"}\n' "$f" "$why"
}

expected_for() {
  case "$1" in
    stale-branch-A.md|stale-branch-B.md|stale-branch-C.md) echo '"no_brainer":true,"category":"stale-branch"';;
    server-touching.md) echo '"reason":"cat-E-server-touching"';;
    novel-shape.md) echo '"no_brainer":"candidate"';;
    capability-blocker.md) echo '"category":"capability-blocker"';;
    *) echo '???';;
  esac
}

fail=0
echo "=== catch-no-brainer v0.1 fixture run ==="
for f in stale-branch-A.md stale-branch-B.md stale-branch-C.md server-touching.md novel-shape.md capability-blocker.md; do
  out=$(classify_brief "$f")
  exp=$(expected_for "$f")
  echo "$out"
  if echo "$out" | grep -F "$exp" >/dev/null; then
    echo "  PASS: $f"
  else
    echo "  FAIL: $f"
    echo "  expected substring: $exp"
    fail=1
  fi
done

echo ""
if [[ $fail -ne 0 ]]; then
  echo "FIXTURE FAILED (one or more cases misclassified)"
  exit 1
fi
echo "ALL 6 FIXTURES PASSED"
exit 0
