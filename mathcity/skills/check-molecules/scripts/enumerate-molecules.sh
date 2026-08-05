#!/usr/bin/env bash
# enumerate-molecules.sh — COMPLETE molecule accounting, classified by status, in order.
#   [A] BEING WORKED ON  — in_progress molecule with a LIVE worker session on it (W✓,P advancing)
#   [B] STRANDED         — in_progress molecule with NO live worker (W✗; the reclaim backlog)
#   [C] READY            — top-level bd-ready dispatchable candidates (push-the-fleet feed)
# Full accounting -> $MOLECULES_FILE (default ~/gt/molecules); capped summary -> stdout.
# Read-only. W/P taxonomy: gsp-5pen4l / ~/gt/CONTEXT.md. Provenance: push-the-fleet gsp-fhdnu,
# artifact_root caveat gsp-1bmxuz. bash-3.2 portable (macOS); no `timeout` (absent on mac).
set -uo pipefail

CITY_ROOT="${GC_CITY:-$HOME/gt}"
OUT="${MOLECULES_FILE:-$CITY_ROOT/molecules}"
TOP="${MOLECULES_TOP:-20}"
PRI="$CITY_ROOT/PRIORITIES.md"

# --- P1.14 dependency pre-flight ---
command -v bd >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — bd is not on PATH."
  echo "Run the Beads install/update step and retry."
  echo "(This skill enumerates molecule status via bd.)"; exit 1; }
gc dolt health >/dev/null 2>&1 || {
  echo "I'm sorry, I can't do that — Dolt is unreachable (bd cannot resolve beads)."
  echo "Run 'gc dolt start' (or 'gc start') and retry."
  echo "(This skill needs the live bead store.)"; exit 1; }

tmp_dir="$(mktemp -d)"; trap 'rm -rf "$tmp_dir"' EXIT
LIVE_IDS="$tmp_dir/live_ids"; WORKED="$tmp_dir/worked"
STRANDED="$tmp_dir/stranded"; READY="$tmp_dir/ready"
: > "$LIVE_IDS"; : > "$WORKED"; : > "$STRANDED"; : > "$READY"

# ---------------------------------------------------------------------------
# [A] BEING WORKED ON: cross-reference live worker sessions -> the molecule/bead
#     in their workdir. W = a live run-operator / implementation-worker on it.
# ---------------------------------------------------------------------------
gc session list --state active 2>/dev/null \
  | grep -E "gc\.run-operator|gc\.implementation-worker" \
  | while IFS= read -r line; do
      sid="$(printf '%s\n' "$line" | grep -oE '^[[:space:]]*[a-z]+-[a-z0-9]+' | head -1 | tr -d ' ')"
      # workdir bead token: the deepest /<prefix>-<id>-<step> path segment
      wd="$(printf '%s\n' "$line" | grep -oE '/Users/[^ ]*/gt/[^ ]+' | head -1)"
      bead="$(printf '%s\n' "$wd" | grep -oE '(gsp|gt|he|as|lm|ja|hom|mca|dv|tgi|cp2)-[a-z0-9]+' | tail -1)"
      role="$(printf '%s\n' "$line" | grep -oE '(run-operator|implementation-worker)[^ ]*' | head -1)"
      [ -n "$bead" ] || continue
      printf '%s\n' "$bead" >> "$LIVE_IDS"
      printf '%s\t%s\t%s\n' "$bead" "${role:-worker}" "${sid:-?}" >> "$WORKED"
    done
sort -u "$LIVE_IDS" -o "$LIVE_IDS"

# ---------------------------------------------------------------------------
# discover rigs: dirs under CITY_ROOT with a .beads/, minus build scratch
# ---------------------------------------------------------------------------
RIGDIRS_LIST="$(
  find "$CITY_ROOT" -maxdepth 2 -type d -name .beads 2>/dev/null \
    | sed 's#/\.beads$##' \
    | grep -vE "/(worktrees|\.gc-builds)" \
    | grep -vE -- "-(prepare|build|implement|worktree|briefpath|operator|decompose|synthesizer|review|context|anchor|owned-work|task-beads|starter|run)" \
    | grep -vE '/[^/]+\.[^/]+$' \
    | sort -u)"

# ---------------------------------------------------------------------------
# [B] STRANDED  +  [C] READY, per rig
# ---------------------------------------------------------------------------
while IFS= read -r d; do
  [ -n "$d" ] || continue
  [ -d "$d/.beads" ] || continue
  rig="$(basename "$d")"

  # [B] STRANDED: in_progress briefed molecule, empty assignee, id NOT in a live workdir.
  (cd "$d" && bd list --status in_progress --json --readonly 2>/dev/null) | python3 -c "
import sys, json
rig='$rig'
try: data=json.load(sys.stdin)
except Exception: sys.exit(0)
live=set()
try:
    for L in open('$LIVE_IDS'):
        L=L.strip()
        if L: live.add(L)
except Exception: pass
for x in data:
    t=(x.get('title') or '').replace(chr(9),' ')
    if 'briefed' not in t: continue          # molecule roots are '<formula>-briefed'
    a=(x.get('assignee') or '').strip()
    i=x.get('id','?')
    if a and i in live: continue              # genuinely being worked
    if i in live: continue
    upd=(x.get('updated_at') or x.get('updated') or '')[:16].replace('T',' ')
    print(f\"{i}\t{rig}\t{t[:60]}\t{upd or '-'}\")
" >> "$STRANDED"

  # [C] READY: top-level dispatchable candidates (unchanged feed logic).
  (cd "$d" && bd ready --json --readonly 2>/dev/null) | python3 -c "
import sys, json
rig='$rig'
try: data=json.load(sys.stdin)
except Exception: sys.exit(0)
SKIP=('Step spec for','input convoy for','drain unit','Implement owned work',
      'Apply starter review','Generate requirements','Write canonical',
      'Write implementation','Write requirements','Finalize','Run build',
      'Create task beads','do-work','[epic]','brief-record','[brief-record]')
for x in data:
    t=(x.get('title') or '').replace(chr(9),' ')
    if any(s in t for s in SKIP): continue
    if x.get('status') not in (None,'open'): continue
    p=x.get('priority',9)
    try: p=int(p)
    except Exception: p=9
    print(f\"{p}\t{x.get('id','?')}\t{rig}\t{t[:100]}\")
" >> "$READY"
done <<< "$RIGDIRS_LIST"

# dedup each by bead id (a store mirrored in >1 workdir yields the same bead twice)
awk -F'\t' '!seen[$1]++' "$STRANDED" > "$STRANDED.dd" && mv "$STRANDED.dd" "$STRANDED"
awk -F'\t' '!seen[$2]++' "$READY" > "$READY.dd" && mv "$READY.dd" "$READY"

# PRIORITIES.md P0 overlay for READY
P0IDS=""
if [ -f "$PRI" ]; then
  P0IDS="$(awk '/^## *P0/{f=1;next} /^## /{f=0} f' "$PRI" \
            | grep -oE '\b[a-z]+-[a-z0-9]+\b' | sort -u | tr '\n' '|' | sed 's/|$//')"
fi
awk -F'\t' -v ids="$P0IDS" 'BEGIN{n=split(ids,a,"|"); for(i=1;i<=n;i++) star[a[i]]=1}
  { s=(($2 in star)?1:0); print s"\t"$0 }' "$READY" \
  | sort -t$'\t' -k1,1nr -k2,2n -k3,3 > "$READY.pri"

N_WORKED="$(wc -l < "$WORKED" | tr -d ' ')"
N_STRAND="$(wc -l < "$STRANDED" | tr -d ' ')"
N_READY="$(wc -l < "$READY.pri" | tr -d ' ')"
STAMP="$(date -u '+%Y-%m-%d %H:%M UTC')"
RIGCOUNTS="$(cut -f4 "$READY.pri" | sort | uniq -c | sort -rn | awk '{printf "%s=%s  ", $2, $1}')"

# --- write full accounting ---
{
  echo "# molecule accounting — generated $STAMP"
  echo "# BEING WORKED ON: $N_WORKED   |   STRANDED (no worker): $N_STRAND   |   READY: $N_READY"
  echo "# ready per-rig: $RIGCOUNTS"
  echo "# status by W/P taxonomy (gsp-5pen4l): WORKED=W✓P✓ | STRANDED=W✗P✗ (reclaim backlog) | READY=unstarted top-level."
  echo "# STRANDED = in_progress molecule with no live worker -> should be reclaimed (orphan-sweep/lost-bead); if it lingers, the reclaim path is broken."
  echo "# READY: ★ = PRIORITIES.md P0. Dispatch top via push-the-fleet (per-bead artifact_root=<rig-root>/.gc-builds/<bead>; gsp-1bmxuz)."
  echo "#"
  echo "== [A] BEING WORKED ON ($N_WORKED) =="
  if [ "$N_WORKED" -gt 0 ]; then
    printf "%-14s  %-26s  %s\n" "BEAD" "WORKER" "SESSION"
    awk -F'\t' '{printf "%-14s  %-26s  %s\n", $1, $2, $3}' "$WORKED"
  else
    echo "(none — no live run-operator/impl-worker is on a molecule right now)"
  fi
  echo ""
  echo "== [B] STRANDED — in_progress, NO worker, frozen ($N_STRAND) =="
  if [ "$N_STRAND" -gt 0 ]; then
    printf "%-14s  %-16s  %-16s  %s\n" "BEAD" "RIG" "LAST-UPDATE" "TITLE"
    awk -F'\t' '{printf "%-14s  %-16s  %-16s  %s\n", $1, $2, $4, $3}' "$STRANDED"
  else
    echo "(none — no in_progress molecule is worker-less)"
  fi
  echo ""
  echo "== [C] READY — top-level dispatchable ($N_READY) =="
  printf "%-5s  %-14s  %-3s  %-26s  %-2s  %s\n" "RANK" "BEAD" "P" "RIG" "★" "TITLE"
  awk -F'\t' '{star=($1==1?"★":" "); printf "%-5s  %-14s  P%-2s  %-26s  %-2s  %s\n", NR, $3, $2, $4, star, $5}' "$READY.pri"
} > "$OUT"

# --- stdout summary ---
echo "molecule accounting — $STAMP"
echo "  BEING WORKED ON: $N_WORKED   |   STRANDED (no worker): $N_STRAND   |   READY: $N_READY"
echo "  full accounting: $OUT"
echo "---------------------------------------------------------------"
echo "[A] BEING WORKED ON ($N_WORKED):"
if [ "$N_WORKED" -gt 0 ]; then awk -F'\t' '{printf "    %-14s  %s\n", $1, $2}' "$WORKED"; else echo "    (none)"; fi
echo "[B] STRANDED — in_progress, no worker ($N_STRAND)  <- reclaim backlog:"
if [ "$N_STRAND" -gt 0 ]; then head -n "$TOP" "$STRANDED" | awk -F'\t' '{printf "    %-14s  %-14s  %s\n", $1, $2, substr($3,1,44)}'; [ "$N_STRAND" -gt "$TOP" ] && echo "    ... $(( N_STRAND - TOP )) more in $OUT"; else echo "    (none)"; fi
echo "[C] READY — top $TOP of $N_READY:"
printf "    %-4s  %-13s  %-3s  %-20s  %-2s  %s\n" "#" "BEAD" "P" "RIG" "★" "TITLE"
head -n "$TOP" "$READY.pri" | awk -F'\t' '{star=($1==1?"★":" "); printf "    %-4s  %-13s  P%-2s  %-20s  %-2s  %s\n", NR, $3, $2, substr($4,1,20), star, substr($5,1,52)}'
echo "---------------------------------------------------------------"
exit 0
