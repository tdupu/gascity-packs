#!/usr/bin/env bash
# enumerate-molecules.sh — inventory every push-the-fleet-dispatchable candidate.
# Full ranked list -> $MOLECULES_FILE (default ~/gt/molecules); top N -> stdout.
# Read-only. Provenance: push-the-fleet gsp-fhdnu; artifact_root caveat gsp-1bmxuz.
set -uo pipefail

CITY_ROOT="${GC_CITY:-$HOME/gt}"
OUT="${MOLECULES_FILE:-$CITY_ROOT/molecules}"
TOP="${MOLECULES_TOP:-20}"
PRI="$CITY_ROOT/PRIORITIES.md"

# --- P1.14 dependency pre-flight ---
command -v bd >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — bd is not on PATH."
  echo "Run the Beads install/update step and retry."
  echo "(This skill enumerates dispatchable ready beads via bd.)"; exit 1; }
gc dolt health >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — Dolt is unreachable (bd cannot resolve beads)."
  echo "Run 'gc dolt start' (or 'gc start') and retry."
  echo "(This skill needs the live bead store to list ready work.)"; exit 1; }

# --- discover rigs: every dir under CITY_ROOT with a .beads/, minus build scratch ---
# (portable: no mapfile — macOS ships bash 3.2)
RIGDIRS_LIST="$(
  find "$CITY_ROOT" -maxdepth 2 -type d -name .beads 2>/dev/null \
    | sed 's#/\.beads$##' \
    | grep -vE "/(worktrees|\.gc-builds)" \
    | grep -vE -- "-(prepare|build|implement|worktree|briefpath|operator|decompose|synthesizer|review|context|anchor|owned-work|task-beads|starter|run)" \
    | grep -vE '/[^/]+\.[^/]+$' \
    | sort -u)"

tmp="$(mktemp)"; trap 'rm -f "$tmp" "$tmp.pri"' EXIT

while IFS= read -r d; do
  [ -n "$d" ] || continue
  [ -d "$d/.beads" ] || continue
  rig="$(basename "$d")"
  (cd "$d" && bd ready --json --readonly 2>/dev/null) | python3 -c "
import sys, json
rig = '$rig'
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
SKIP = ('Step spec for', 'input convoy for', 'drain unit', 'Implement owned work',
        'Apply starter review', 'Generate requirements', 'Write canonical',
        'Write implementation', 'Write requirements', 'Finalize', 'Run build',
        'Create task beads', 'do-work', '[epic]', 'brief-record', '[brief-record]')
for x in data:
    t = (x.get('title') or '').replace(chr(9), ' ')
    if any(s in t for s in SKIP):
        continue
    if x.get('status') not in (None, 'open'):
        continue
    p = x.get('priority', 9)
    try: p = int(p)
    except Exception: p = 9
    print(f\"{p}\t{x.get('id','?')}\t{rig}\t{t[:100]}\")
" >> "$tmp"
done <<< "$RIGDIRS_LIST"

# --- dedup by bead id (a store mirrored in >1 workdir yields the same bead twice) ---
awk -F'\t' '!seen[$2]++' "$tmp" > "$tmp.dd" && mv "$tmp.dd" "$tmp"

# --- PRIORITIES.md P0 overlay: mark ids listed under the P0 section with a star ---
P0IDS=""
if [ -f "$PRI" ]; then
  P0IDS="$(awk '/^## *P0/{f=1;next} /^## /{f=0} f' "$PRI" \
            | grep -oE '\b[a-z]+-[a-z0-9]+\b' | sort -u | tr '\n' '|' | sed 's/|$//')"
fi

# split starred (P0-overlay) vs rest, sort each by priority then id, concat
awk -F'\t' -v ids="$P0IDS" 'BEGIN{n=split(ids,a,"|"); for(i=1;i<=n;i++) star[a[i]]=1}
  { s = (($2 in star)?1:0); print s"\t"$0 }' "$tmp" \
  | sort -t$'\t' -k1,1nr -k2,2n -k3,3 > "$tmp.pri"

TOTAL="$(wc -l < "$tmp.pri" | tr -d ' ')"
STAMP="$(date -u '+%Y-%m-%d %H:%M UTC')"

# --- per-rig counts ---
RIGCOUNTS="$(cut -f4 "$tmp.pri" | sort | uniq -c | sort -rn | awk '{printf "%s=%s  ", $2, $1}')"

# --- write full file ---
{
  echo "# push-the-fleet candidate molecules — generated $STAMP"
  echo "# total: $TOTAL   |   per-rig: $RIGCOUNTS"
  echo "# source: bd ready across all rigs, filtered to top-level dispatchable (push-the-fleet gsp-fhdnu)."
  echo "# ★ = listed in PRIORITIES.md P0.  To dispatch: hand the top to push-the-fleet"
  echo "#   (adds per-bead artifact_root=<rig-root>/.gc-builds/<bead>; never the bare root — gsp-1bmxuz)."
  echo "#"
  printf "%-5s  %-14s  %-3s  %-26s  %-2s  %s\n" "RANK" "BEAD" "P" "RIG" "★" "TITLE"
  awk -F'\t' '{star=($1==1?"★":" "); printf "%-5s  %-14s  P%-2s  %-26s  %-2s  %s\n", NR, $3, $2, $4, star, $5}' "$tmp.pri"
} > "$OUT"

# --- print top N to stdout ---
echo "push-the-fleet candidate molecules — $STAMP"
echo "total: $TOTAL   |   per-rig: $RIGCOUNTS"
echo "full list: $OUT   (showing top $TOP)"
echo "---------------------------------------------------------------"
printf "%-4s  %-13s  %-3s  %-22s  %-2s  %s\n" "#" "BEAD" "P" "RIG" "★" "TITLE"
head -n "$TOP" "$tmp.pri" | awk -F'\t' '{star=($1==1?"★":" "); printf "%-4s  %-13s  P%-2s  %-22s  %-2s  %s\n", NR, $3, $2, substr($4,1,22), star, substr($5,1,60)}'
echo "---------------------------------------------------------------"
[ "$TOTAL" -gt "$TOP" ] && echo "... $(( TOTAL - TOP )) more in $OUT"
exit 0
