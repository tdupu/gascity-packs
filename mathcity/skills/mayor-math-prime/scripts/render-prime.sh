#!/usr/bin/env bash
# render-prime.sh — renders the QUIMBY prime input (the restart PROMPT).
#
# Resolution order:
#   1. Jinja: $STATE_DIR/restart/PROMPT-mayor-restart.j2 rendered with
#      $STATE_DIR/session-catalog.json + live `bd show <handoff-bead>`.
#   2. Fallback: $STATE_DIR/restart/PROMPT-mayor-restart.txt (curated text).
#   3. Generic:  <skill>/templates/PROMPT-mayor-generic.txt (first-import
#      experience — printed with bootstrap instructions).
#
# State dir defaults to ~/gt/mathcity-mayor; override with MAYOR_STATE_DIR.

STATE_DIR="${MAYOR_STATE_DIR:-$HOME/gt/mathcity-mayor}"
CATALOG="$STATE_DIR/session-catalog.json"
TEMPLATE="$STATE_DIR/restart/PROMPT-mayor-restart.j2"
FALLBACK="$STATE_DIR/restart/PROMPT-mayor-restart.txt"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GENERIC="$SKILL_DIR/templates/PROMPT-mayor-generic.txt"

# --- 1. jinja render (requires jinja2 + non-empty catalog + template) -------
if [ -f "$CATALOG" ] && [ -f "$TEMPLATE" ]; then
    python3 - "$CATALOG" "$TEMPLATE" <<'PYEOF' && exit 0
import sys, json, subprocess

try:
    from jinja2 import Template
except ImportError:
    sys.exit(1)

catalog_path, template_path = sys.argv[1], sys.argv[2]

with open(catalog_path) as f:
    sessions = json.load(f)

if not sessions:
    sys.exit(1)

last = sessions[-1]
handoff_bead = last.get("bead")
quimby_number = last["quimby"] + 1

def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n % 10, f"{n}th")

_words = {1:"first",2:"second",3:"third",4:"fourth",5:"fifth",6:"sixth",
          7:"seventh",8:"eighth",9:"ninth",10:"tenth"}

quimby_word = _words.get(quimby_number, ordinal(quimby_number))
next_word = _words.get(quimby_number + 1, ordinal(quimby_number + 1))

handoff_content = "(no handoff bead recorded)"
if handoff_bead:
    try:
        result = subprocess.run(["bd", "show", handoff_bead],
                                capture_output=True, text=True, timeout=15)
        handoff_content = result.stdout.strip() or "(empty bead)"
    except Exception as e:
        handoff_content = f"(could not fetch {handoff_bead}: {e})"

with open(template_path) as f:
    tmpl = Template(f.read())

print(tmpl.render(
    sessions=sessions,
    quimby_number=quimby_number,
    quimby_number_word=quimby_word,
    quimby_number_ordinal=ordinal(quimby_number),
    next_quimby_word=next_word,
    handoff_bead=handoff_bead or "none",
    handoff_bead_content=handoff_content,
    city_state=last.get("city_state") or "(not recorded)",
    charge=last.get("charge_for_next") or "(no charge recorded)",
))
PYEOF
fi

# --- 2. curated plain-text fallback ------------------------------------------
if [ -f "$FALLBACK" ]; then
    cat "$FALLBACK"
    exit 0
fi

# --- 3. generic mayor statement (first import — no state dir yet) ------------
cat "$GENERIC"
cat <<BOOTSTRAP

######
BOOTSTRAP (no mayor state found at $STATE_DIR)
######
This city has no mayor session state yet. To set it up:
  mkdir -p "$STATE_DIR/restart"
  echo "[]" > "$STATE_DIR/session-catalog.json"
Then, at the end of this first session, run /mayor-math-handoff — it writes
your first handoff bead, session-catalog entry, and restart PROMPT, after
which future sessions prime from your own city's state instead of this
generic statement.
BOOTSTRAP
