#!/usr/bin/env bash
# Renders the QUIMBY restart document from session-catalog.json + PROMPT-mayor-restart.j2.
# Falls back to PROMPT-mayor-restart.txt if jinja2 is unavailable or catalog is empty.

CATALOG="$HOME/gt/mathcity-mayor/session-catalog.json"
TEMPLATE="$HOME/gt/mathcity-mayor/PROMPT-mayor-restart.j2"
FALLBACK="$HOME/gt/mathcity-mayor/PROMPT-mayor-restart.txt"

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

cat "$FALLBACK"
