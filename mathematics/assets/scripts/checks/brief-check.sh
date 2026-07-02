#!/bin/sh
set -eu

COMMAND="${1:-}"
if [ -z "$COMMAND" ]; then
  echo "usage: brief-check.sh <check-name>" >&2
  exit 2
fi

ROOT="${BRIEF_ROOT:-.beads/briefs}"

fail() {
  echo "brief-check: $*" >&2
  exit 1
}

metadata_value() {
  key="$1"
  if [ -z "${GC_BEAD_ID:-}" ] || ! command -v gc >/dev/null 2>&1 || ! command -v jq >/dev/null 2>&1; then
    return 0
  fi
  gc bd show "$GC_BEAD_ID" --json 2>/dev/null |
    jq -r --arg key "$key" '.[0].metadata[$key] // empty' 2>/dev/null || true
}

first_match() {
  pattern="$1"
  find . -path "$pattern" -type f 2>/dev/null | sort | head -n 1
}

brief_path() {
  if [ -n "${GC_BRIEF_PATH:-}" ]; then
    printf '%s\n' "$GC_BRIEF_PATH"
    return 0
  fi
  value="$(metadata_value "gc.brief.path")"
  if [ -n "$value" ]; then
    printf '%s\n' "$value"
    return 0
  fi
  value="$(metadata_value "brief.path")"
  if [ -n "$value" ]; then
    printf '%s\n' "$value"
    return 0
  fi
  first_match "./$ROOT/.staging/*/brief.md"
}

require_file() {
  path="$1"
  [ -n "$path" ] || fail "missing path"
  [ -f "$path" ] || fail "missing file: $path"
}

require_dir() {
  path="$1"
  [ -d "$path" ] || fail "missing directory: $path"
}

require_text() {
  path="$1"
  pattern="$2"
  message="$3"
  grep -Eq "$pattern" "$path" || fail "$message in $path"
}

require_gate() {
  path="$1"
  key="$2"
  if grep -Eq "$key:[[:space:]]*(FAIL|BLOCKED)\\b" "$path"; then
    fail "$key is failing or blocked"
  fi
  grep -Eq "$key:[[:space:]]*(PASS|N/A)\\b" "$path" ||
    fail "$key must be PASS or N/A"
}

check_jsonl() {
  manifest="$1"
  [ -f "$manifest" ] || return 0
  if command -v jq >/dev/null 2>&1; then
    line_no=0
    while IFS= read -r line || [ -n "$line" ]; do
      line_no=$((line_no + 1))
      [ -z "$line" ] && continue
      printf '%s\n' "$line" | jq -e . >/dev/null 2>&1 ||
        fail "invalid JSONL in $manifest at line $line_no"
    done < "$manifest"
  fi
}

check_test_evidence() {
  path="$(brief_path)"
  require_file "$path"
  require_text "$path" '^##*[[:space:]]+Gate Evidence\b|^Gate Evidence\b' "missing Gate Evidence section"
  require_gate "$path" "G1 Test-evidence"
}

check_mechanical_gates() {
  path="$(brief_path)"
  require_file "$path"
  require_text "$path" '^##*[[:space:]]+Gate Evidence\b|^Gate Evidence\b' "missing Gate Evidence section"
  require_gate "$path" "G1 Test-evidence"
  require_gate "$path" "G3 Shell-scripts-testable"
  require_gate "$path" "G5 Server-touching"
  require_gate "$path" "G5b User-skill-touching"
  require_gate "$path" "G7 Artifacts-staging"
  require_gate "$path" "G8 Brief-record"
  require_gate "$path" "G10 Improve-README"
  require_gate "$path" "G11 Breadcrumb"
  require_gate "$path" "G12 Auto-merge-kill-switch"
  require_gate "$path" "G13 Stale-claim"
  require_gate "$path" "G14 Test-execution-silent"
  require_gate "$path" "G15 Improve-README-silent"
  require_gate "$path" "G16 Master-current"
}

check_disposition() {
  path="$(brief_path)"
  require_file "$path"
  require_text "$path" '^Disposition:[[:space:]]*(promote|reject|blocked)\b' "missing gate disposition"
}

check_pile_entry() {
  path="$(metadata_value "gc.brief.path")"
  if [ -z "$path" ]; then
    path="$(find "$ROOT/.pile" -mindepth 1 -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort | head -n 1)"
  fi
  require_file "$path"
  require_text "$path" '^##*[[:space:]]+Gate Evidence\b|^Gate Evidence\b' "pile entry lacks Gate Evidence"
}

check_pile_nonempty() {
  find "$ROOT/.pile" -mindepth 1 -maxdepth 1 -type f -name '*.md' 2>/dev/null | grep -q . ||
    fail "no markdown briefs in $ROOT/.pile"
}

check_shuffle_result() {
  stack_count="$(find "$ROOT/stack" -mindepth 1 -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  rejected_count="$(find "$ROOT/.pile/.rejected" -mindepth 1 -maxdepth 2 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  [ "${stack_count:-0}" -gt 0 ] || [ "${rejected_count:-0}" -gt 0 ] ||
    fail "no promoted or rejected brief found"
  check_jsonl "$ROOT/stack/manifest.jsonl"
}

check_manifest() {
  mkdir -p "$ROOT/stack"
  check_jsonl "$ROOT/stack/manifest.jsonl"
}

check_decision_record() {
  path="$(metadata_value "gc.brief.decision_path")"
  if [ -z "$path" ]; then
    path="$(find "$ROOT/decisions" -mindepth 1 -maxdepth 1 -type f -name '*.toml' 2>/dev/null | sort | head -n 1)"
  fi
  require_file "$path"
  require_text "$path" '^decision[[:space:]]*=' "decision record must set decision"
  # C2: pin source_bead so the approve dispatch path can never silently no-op.
  # The write-decision step always emits a source_bead line (possibly empty for
  # a legacy brief with no manifest source), so require the KEY to be present.
  require_text "$path" '^source_bead[[:space:]]*=' \
    "decision record must set source_bead (brief-decision-dispatch keys routing on it)"
}

check_watchdog_record() {
  require_dir "$ROOT"
  mkdir -p "$ROOT/watchdog"
}

check_test_execution_record() {
  path="$(metadata_value "gc.test.request_path")"
  if [ -z "$path" ]; then
    path="$(find "$ROOT/test-execution" -mindepth 1 -maxdepth 1 -type f -name '*.toml' 2>/dev/null | sort | head -n 1)"
  fi
  require_file "$path"
  require_text "$path" '^test_command[[:space:]]*=' "test execution request must set test_command"
  require_text "$path" '^risk[[:space:]]*=' "test execution request must set risk"
  if grep -Eq '^risk[[:space:]]*=[[:space:]]*"high"' "$path"; then
    require_text "$path" '^authorized_by[[:space:]]*=[[:space:]]*"Taylor"' "high-risk test execution requires Taylor authorization"
  fi
}

check_breadcrumb() {
  path="$(metadata_value "gc.experiment.breadcrumb_path")"
  if [ -z "$path" ]; then
    path="$(find "$ROOT/experiments" -path '*/breadcrumb.toml' -type f 2>/dev/null | sort | head -n 1)"
  fi
  require_file "$path"
  require_text "$path" '^source[[:space:]]*=' "breadcrumb must set source"
}

check_no_brainer_safety() {
  path="$(brief_path)"
  [ -n "$path" ] && [ -f "$path" ] || return 0
  if grep -Eq 'G5 Server-touching:[[:space:]]*(FAIL|BLOCKED)' "$path"; then
    fail "server-touching gate blocks no-brainer handling"
  fi
  if grep -Eq 'G5b User-skill-touching:[[:space:]]*(FAIL|BLOCKED)' "$path"; then
    fail "user-skill-touching gate blocks no-brainer handling"
  fi
}

check_no_brainer_execute_safety() {
  check_no_brainer_safety
  [ -f "$ROOT/ALLOW_NO_BRAINER_AUTO_EXECUTE" ] ||
    fail "missing no-brainer auto-execute kill switch: $ROOT/ALLOW_NO_BRAINER_AUTO_EXECUTE"
}

check_archive_sweep_record() {
  require_dir "$ROOT"
  mkdir -p "$ROOT/archive"
}

check_file_or_sendback_log() {
  log="$ROOT/decisions/file-or-sendback.jsonl"
  require_file "$log"
  check_jsonl "$log"
  if command -v jq >/dev/null 2>&1; then
    last="$(tail -n 1 "$log")"
    [ -n "$last" ] || fail "empty route log: $log"
    printf '%s\n' "$last" | jq -e '
      (.bead_id | type == "string")
      and (.brief_slug | type == "string" and length > 0)
      and (.decision | type == "string" and length > 0)
      and (.choice == "FILE" or .choice == "SEND-BACK")
      and (.reason | type == "string" and length > 0)
      and (.timestamp | type == "string" and length > 0)
      and (.agent_id | type == "string" and length > 0)
      and (if .choice == "FILE"
           then (.target_bead_id | type == "string" and length > 0)
           else true end)
    ' >/dev/null 2>&1 ||
      fail "route log last entry missing required keys or invalid choice: $log"
  fi
}

case "$COMMAND" in
  test-evidence) check_test_evidence ;;
  mechanical-gates) check_mechanical_gates ;;
  disposition) check_disposition ;;
  pile-entry) check_pile_entry ;;
  pile-nonempty) check_pile_nonempty ;;
  shuffle-result) check_shuffle_result ;;
  manifest-current) check_manifest ;;
  decision-record) check_decision_record ;;
  watchdog-record) check_watchdog_record ;;
  test-execution-record) check_test_execution_record ;;
  breadcrumb) check_breadcrumb ;;
  no-brainer-safety) check_no_brainer_safety ;;
  no-brainer-execute-safety) check_no_brainer_execute_safety ;;
  archive-sweep-record) check_archive_sweep_record ;;
  file-or-sendback-log) check_file_or_sendback_log ;;
  *) fail "unknown check: $COMMAND" ;;
esac

