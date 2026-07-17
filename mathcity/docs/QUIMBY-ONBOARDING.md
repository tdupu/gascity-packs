# QUIMBY Onboarding — operate the Gas City the way it's working now

> Canonical, regression-proofing onboarding for every QUIMBY (the math-city Mayor).
> This context was derived painfully over 11 generations — it is gold; do not
> throw it away. When something here proves wrong at source, correct it here in
> the same pass (P5.4). Home: `mathcity/docs/`.

## Reference docs — mandatory vs on-demand

**Read at every startup (mandatory):**

1. **[CITY-RESTART-CHECKLIST.md](./CITY-RESTART-CHECKLIST.md)** — Phase 0–6 step-by-step
   to bring the city up from cold and verify orders/formulas/events actually fire.
   *The single most valuable doc — it has restarted the city for 11 QUIMBYs.*

**Read on-demand only — NOT at startup:**

2. **[CITY-OPERATION-REFERENCE.md](./CITY-OPERATION-REFERENCE.md)** — the userguide:
   system architecture, pools/agents/workers, brief-pipeline lifecycle, no-brainer
   system, and the **correct command surface** (what actually exists vs what doesn't).
   *Read when you need architecture details or to verify a command exists.*
3. **[TEST-CYCLE-GUIDE.md](./TEST-CYCLE-GUIDE.md)** — the dogfood/test cycle: the
   two-layer system-under-test, the test matrix, and fix-at-source (P5.4) triage.
   *Read when you are about to run tests or triage a test failure.*
4. **[DOGFOOD-WORKFLOW.md](./DOGFOOD-WORKFLOW.md)** — the ~/gt↔~/repos duality and how
   a change actually reaches the running city.
   *Read when you are about to make a pack change or need to deploy something.*

The live trust record is per-session shards in `~/gt/mathcity-tests/run-log/`.
Write each session to `run-log/S{N}.md` (new file). KEEP AND EXPAND — Taylor
values the command→result log highly. Full archive at `run-log/archive-S1-S15.md`.

## S11-corrected operational truths (the hard-won gold)

These are the things a fresh QUIMBY must know to operate the city as well as QUIMBY 11.

**Restart & health**
- A cold or wedged city is fixed by **`gc restart`** — it gives a fresh tmux server and
  respawns the fleet (S8/S9: the "0 agents" wedge was a missing tmux server, not a spawn bug).
- **`gc status` "0/N agents" is a SLOW-API ARTIFACT** (the /status endpoint is slow cold).
  Do NOT trust the count. Verify fleet health via `tmux -L gt ls` + pane capture +
  `gc order history` + counting open "briefed publish slot" beads.
- Verify Dolt with `gc dolt health` (or a direct `bd list` timing), not the count.

**Verify at source (P5.4) — the discipline behind every S6–S11 win**
- Do NOT inherit behavioral claims from handoffs/plans/narratives. Ground every claim in
  the code / TOML / running behavior. S11 wins: caught the server running a STALE incomplete
  fix; a SHA-mismatch that was a false alarm (fix content present under a rebased SHA);
  a gate that could pass VACUOUSLY. Narrative docs are orientation, presumed stale.

**Server operations (aia-s27) — S11 policy `gsp-zgfq`**
- The server must NEVER have uncommitted changes. Author fixes LOCALLY (commit+push to
  master), then deploy ONLY via **`push-to-server`** (fetch + ff-merge). Pull data ONLY via
  **`pull-data-from-server`**. Never edit files directly on the server.
- ALWAYS verify the server code is correct BEFORE any live-write (the verify-first guard
  caught the incomplete-fix near-disaster in S11).
- Every server LIVE-WRITE = its own explicit per-node Taylor authorization (dry-runs need none).
  Take a fresh backup before writes; the backup is the recovery point.

**The brief/work pipeline (trusted, D2-primary)**
- Dispatch work through **`build-basic-briefed`** (`gc sling <rig>/gc.run-operator <bead> --on
  build-basic-briefed --var interaction_mode=autonomous --var review_mode=agent --var
  drain_policy=separate --var push=false --var open_pr=false`). It runs the full build and
  fires a **decision brief** at the terminal slot instead of publishing — `push=false` means
  nothing ships; briefs accumulate on Taylor's stack.
- Flow: work → build-basic-briefed → brief → catch-no-brainer → `.pile` → brief-shuffle →
  `stack` → `/present-briefs` → Taylor adjudicates → verdict edge → `gc.publisher` → BART lands.
- **FINDING #1 (every build)**: the build's commits live in DETACHED-HEAD worktrees that
  `gc.publisher` will NOT auto-recover — they must be cherry-picked/anchored before publish
  or the ship omits them. BART handles this on landing; always flag it.
- Finalize `control_quarantine` on a missing `.gc/scripts` path recurs every build — cosmetic.

**The ~/gt ↔ ~/repos duality**
- The running city loads pack content from `~/repos/gascity-packs` (local-path import).
  Pack-FILE edits under `~/gt/gascity-packs` are STAGED-not-live; durable pack/skill/binary
  changes go through BART (~/repos) + a rebuild/reload. Beads sync via the Dolt remotes.
- BART (`80b87468`) does all git landings (push/merge/branch-delete), each behind a FRESH
  Taylor `authorize-git-operation`. Consensus with BART before major work. Contact via
  `communicate-with-other-agent` (shared inbox `~/gt/.claude/.agent-inbox.md`).

**Command-surface corrections (do NOT use — they don't exist)**
- `gc.publisher` does NOT merge to main (no build/publish path merges to master automatically).
- Non-existent verbs seen in old narratives: `gc config check`, `gc convoy show`,
  `gc dolt sql --db`, `gc event log`, and the `timeout` shell command (not on this mac).
  Use the Bash tool's own timeout, not `timeout`.

**Session hygiene**
- Farm out execution to forked workers (Fable/Opus plan; Haiku/Sonnet execute).
- Mail vs nudge: `gc mail` persists (handoffs/escalations); `gc nudge` is ephemeral. Default nudge.
- The mail inbox is a firehose of stale escalations — verify live before believing any
  (esp. Dolt-down escalations: check `gc dolt health` first).
- At session end: write a handoff bead, add a `session-catalog.json` entry, expand the run-log,
  and update `PROMPT-mayor-restart.txt`.

## Handoff-bead chain (each holds that session's full arc)
S1 gt-gnh7m · S2 gt-v6azs · S3 gt-a6ty4 · S4 gt-shezv · S5 gt-yygvi · S6 gt-n587i ·
S7 gt-00snc · S8 gt-mvq3s · S9 gt-qion7 · S10 gt-49683 · S11 gt-h16p88.
