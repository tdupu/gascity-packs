---
name: check-brief-policy
description: >-
  Audit the current brief pipeline state against the brief-system POLICY.md
  (B1.x–B3.x, N.x, L.x, E.x, T.x, D.x, S.x rules). Use when the user says
  "check brief policy", "run check-brief-policy", "is the pipeline compliant",
  "audit brief pipeline", "does the current pipeline violate any rules", or
  before a major brief pipeline change. Read-only: reports drift but never
  mutates bead state, files, or config (PP1.3). Returns approve / revise /
  defer. Companion to new-brief-policy (write path). Policy home:
  mathcity/subdomains/brief-system/POLICY.md.
---

# check-brief-policy

Audit the live brief pipeline state against
[POLICY.md](../../POLICY.md). Read the policy first — it is the
authoritative source. This skill checks WHAT IS, not what was planned.

> **Status guard (PP2.1):** If `POLICY.md` header shows `Status: Draft`,
> the policy is not yet enforceable. Run this audit informally and flag any
> section that is clearly non-compliant, but do NOT issue "revise" verdicts
> for rules that haven't been adopted. For sections previously adopted
> (the 2026-07-11 adopted version), treat those rules as binding; flag
> draft-revision additions as informational only. Return **defer** on the
> overall verdict until the revision is adopted.

---

## Scope

Check the following dimensions in order:

### 1. Trinity completeness (PP1.1)

- Is `mathcity/subdomains/brief-system/POLICY.md` present and at a known status?
- Does `check-brief-policy` skill exist and point to this policy?
- Does `new-brief-policy` skill exist?

```bash
ls ~/repos/gascity-packs/mathcity/subdomains/brief-system/POLICY.md
ls ~/.claude/skills/check-brief-policy
ls ~/.claude/skills/new-brief-policy
```

### 2. Brief pipeline structure (B2.4, B2.8)

Canonical pile and stack locations per `paths.toml`:

```bash
PATHS_TOML=~/repos/gascity-packs/mathcity/assets/brief-pipeline/paths.toml
cat "$PATHS_TOML"
# Check pile and stack dirs exist:
PILE_DIR=$(grep pile_dir "$PATHS_TOML" | ... )
STACK_DIR=$(grep stack_dir "$PATHS_TOML" | ... )
ls "$PILE_DIR" "$STACK_DIR"
```

Check: pile = `.beads/briefs/.pile/`, stack = `.beads/briefs/stack/`. Both
must exist; neither may be an ad-hoc location.

### 3. Ordering (B2.5)

Examine `stack/manifest.jsonl`. Every entry must have an `unlock_count`
field. Verify that higher-count entries appear earlier in the stack (the
single-writer `brief-shuffle` should sort on promote).

```bash
cat ~/gt/hecke/.beads/briefs/stack/manifest.jsonl | \
  python3 -c "
import sys,json
rows = [json.loads(l) for l in sys.stdin if l.strip()]
print([(r.get('slug','?'), r.get('unlock_count',0)) for r in rows])
"
```

Flag any manifest where a lower-count brief appears before a higher-count
one — ordering violation (B2.5 drift).

### 4. No-resurface invariant (B2.3)

Check that no adjudicated brief (`brief-closed` label in bead store) appears
in the stack or pile:

```bash
STACK_DIR=~/gt/hecke/.beads/briefs/stack
for f in "$STACK_DIR"/*.md; do
  slug=$(basename "$f" .md)
  # derive bead ID from slug; check its labels
  BEAD_ID=$(echo "$slug" | sed 's/-brief$//')   # rough extraction
  # bd show "$BEAD_ID" | grep brief-closed && echo "VIOLATION: $slug"
done
```

### 5. No-brainer kill switch (N rules)

Check whether `ALLOW_NO_BRAINER_AUTO_EXECUTE` kill switch file exists:

```bash
KILL_SWITCH=$(grep kill_switch \
  ~/repos/gascity-packs/mathcity/assets/brief-pipeline/paths.toml | \
  awk -F'"' '{print $2}')
HECKE_ROOT=~/gt/hecke
if [ -f "$HECKE_ROOT/$KILL_SWITCH" ]; then
  echo "Auto-execute: ON — confirm this is intentional"
else
  echo "Auto-execute: OFF (fail-safe)"
fi
```

### 6. Stack freshness (B2.7 / B2.9)

Check for briefs older than 7 days in the stack without a presented-at
record in `presentations/`:

```bash
ls -lt ~/gt/hecke/.beads/briefs/stack/*.md | head
# Compare with presentations/ directory mtime
ls ~/gt/hecke/.beads/briefs/presentations/ | head
```

Flag any brief with a stack entry and no corresponding `*-presented.toml`
that is more than 7 days old.

### 7. Decision record integrity (B3.x)

Check that the `decisions/` directory and `decisions.jsonl` are non-empty
if any briefs have been adjudicated:

```bash
ls ~/gt/hecke/.beads/briefs/decisions/ | wc -l
wc -l ~/gt/hecke/.beads/briefs/decisions.jsonl
```

---

## Verdict

After each check, emit one of:
- **approve (section)** — no drift found
- **revise (section)** — specific rules violated; cite rule ID + one-line
  remediation per item
- **defer (section)** — a human call is needed; state the open question

Overall verdict = worst of per-section verdicts. **Never emit "reject"** —
that applies only to artifacts, not audits.

Report format:

```
## check-brief-policy audit — <date>

### Trinity (PP1.1)
verdict: approve | revise | defer
[items if revise/defer]

### Pipeline structure (B2.4, B2.8)
...

### Ordering (B2.5)
...

### No-resurface invariant (B2.3)
...

### No-brainer kill switch
...

### Stack freshness
...

### Decision records (B3.x)
...

## Overall: approve | revise | defer
[Summary of all revise/defer items]
```

This skill is **read-only**. Never run `bd close`, `bd update`, `git commit`,
or any state-mutating command during an audit. If you find a problem, describe
it and propose the fix — let the user or `new-brief-policy` apply it.
