---
name: check-build-hygiene
description: Audit the CURRENT live install — gc/bd binaries, the three source repos, pack imports, and skill sinks — against the Pack Portability & Boundary Policy (mathcity/subdomains/dev/POLICY.md). Use when the user says "check build hygiene", "run check-build-hygiene", "is my install reproducible", "can I share this setup", "audit the city against the policy", or before sharing the setup with a collaborator / rebuilding on another machine. Returns approve / revise / defer with a drift list and per-item remediation. Current-state counterpart of check-plan-hygiene (which gates plans/convoys before build).
---

# check-build-hygiene

Audit the live install against [POLICY.md](../../POLICY.md): could Taylor
(or a collaborator) recreate what is running on this machine from pushed
source, and can upstream still be pulled? Read POLICY.md first — it is the
source of truth; this skill is its audit procedure. Every finding cites a
P-rule and comes with a remediation.

Read-only by default: this skill **reports** drift; it repairs only when
the user explicitly asks.

## Checks

**1. Binaries match source (P1.6).**

```bash
# gc against ~/repos/gascity
go version -m "$(which gc)" | grep -E 'vcs\.(revision|modified)'
git -C ~/repos/gascity rev-parse HEAD
# bd against ~/repos/beads
go version -m "$(which bd)" | grep -E 'vcs\.(revision|modified)'
git -C ~/repos/beads rev-parse HEAD
# stale shadows
which -a gc; which -a bd
```

Fail if: `vcs.modified=true`; `vcs.revision` ≠ the repo's HEAD; or an
unexpected `$PATH` location shadows the sanctioned install. Remediation:
the matching `update-*-from-source` skill (they rebuild, clean stale
binaries, and re-verify).

**2. Working trees clean, deviations declared (P1.6).**

```bash
for r in ~/repos/gascity ~/repos/beads ~/repos/gascity-packs; do
  echo "== $r"; git -C "$r" status --porcelain; cat "$r/.git/info/exclude"
done
```

Untracked/modified files that a build or the city depends on fail unless
declared (listed in `.git/info/exclude` AND encoded in the corresponding
update skill — precedent: the `go.work` beads-lockstep file in
`~/repos/gascity`). Uncommitted pack content in `gascity-packs` is
work-in-progress, not a violation — but flag it (P1.4: the city depends on
it and it isn't pushed).

**3. Remote lockstep — upstream stays pullable (P1.7).**

```bash
git -C ~/repos/gascity fetch origin fork -q &&
  git -C ~/repos/gascity rev-parse main origin/main fork/main   # all equal
git -C ~/repos/beads fetch origin -q &&
  git -C ~/repos/beads rev-parse main origin/main               # equal
git -C ~/repos/gascity-packs fetch upstream fork -q &&
  git -C ~/repos/gascity-packs merge-base --is-ancestor upstream/main main \
  && echo "upstream contained" || echo "UPSTREAM NOT MERGED"
git -C ~/repos/gascity-packs rev-list fork/main..main --count    # unpushed commits
```

gascity-packs is **fork-canonical** (gt-5cye): fork deliberately ahead of
upstream; upstream must be *contained in* main (merged), never mirrored
over it. Remediation: the matching `update-*-from-source` skill; never
resolve divergence by force-push.

**4. Local-path imports are remote-backed (P1.4).**

```bash
grep -A1 'imports' ~/gt/city.toml | grep 'source' 
```

For each local-path import target: its repo must be clean (check 2) and
its HEAD pushed to the canonical remote (check 3). A city standing on
unpushed content can't be recreated elsewhere.

**5. Skill exposure hygiene (P1.8, P1.3).**

```bash
for l in ~/gt/.claude/skills/* ~/repos/agent-skills/skills/*; do
  [ -L "$l" ] && [ ! -e "$l" ] && echo "DANGLING: $l -> $(readlink "$l")"
done
sh ~/repos/agent-skills/scripts/check-skill-symlinks.sh
```

Findings: dangling symlinks (e.g. old `mathematics/*` targets → retarget
to `mathcity/`); real directories in agent-skills that duplicate pack
sources (fork drift — replace with a relative symlink); files hand-created
*inside* a materialized sink.

**6. Vendor trees untouched (P2.2).**

```bash
git -C ~/repos/gascity-packs status --porcelain -- '*/vendor/' | head
```

Any modification under a `vendor/**` tree is a violation — no exceptions.

**7. Replay litmus (P1.1) — judgment call.**

Given checks 1–6, answer: "if I `gc init` a scratch city and replay only
the declared imports on a fresh machine, do I get this city?" List every
piece of load-bearing state that would be missing (hand-placed sink
symlinks are fine — they're encoded in `skill-creator-math`; an
undocumented manual step is not).

## Output format

```
check-build-hygiene — <date>

Verdict: approve | revise | defer

Drift list (revise only):
  <P-rule> — <what drifted, file/path> — <remediation, one line>

Defer items:
  <anything needing a human call, with the question stated>
```

Verdict semantics: **approve** = current state compliant; **revise** =
drift found, each item fixable and listed with remediation; **defer** =
a human call is needed. (Per POLICY.md, **reject** does not apply to
audits.)
