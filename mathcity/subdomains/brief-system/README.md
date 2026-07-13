# mathcity-brief-system

The spine of the mathcity decision pipeline: brief formulas, the 16-hurdle
registry, orders, and the review agents that drive the brief → decision workflow.

This sub-namespace (`mathcity-brief-system.*` (ADR 0002 alias)) governs how raw artifacts enter
the pipeline, pass through hurdles, and become closed decisions. The other four
subdomains produce artifacts that feed into this pipeline.

See `mathcity/formulas/` (cross-cutting pipeline formulas) and
`mathcity/assets/brief-pipeline/` (hurdle registry, paths, thresholds).

---

## Skills

| Skill | Purpose |
|---|---|
| `check-brief-policy` | Audit the live brief pipeline against brief-system POLICY.md (B/N/L/E/T/D/S rules). Read-only: reports approve / revise / defer. |
| `new-brief-policy` | Sole write path for brief-system rules. Proposes and commits Taylor-approved amendments to POLICY.md; records each change in the Change Log. |

---

## The brief system as a scheduling problem

Taylor is the shared serial resource. Every artifact the pipeline produces must
eventually pass through Taylor's review before closing — structurally identical
to how an observatory's data reduction pipeline is the one instrument all
observations must pass through. The brief system is the queue management layer
for that resource.

This framing has concrete consequences. A factory that models token cost but not
attention has priced the cheap resource and ignored the scarce one. The
no-brainer layer (N-rules, `catch-no-brainer`) routes low-stakes items away from
Taylor automatically — this is the primary lever for protecting review bandwidth.
The pile ordering (B2.5) determines which of the remaining items Taylor sees
first.

Reference: Jarmak (2026), *Operations research as a framework for software-factory
scheduling* — frames the brief-review queue as the "one shared serial instrument"
in the observatory-factory correspondence, and proposes human attention as a
quantity that should be explicitly priced and managed.

---

## Pile ordering (B2.5) — current rule and planned improvements

**Current rule:** `priority(brief) = unlock_count` (downstream beads transitively
unblocked by adjudicating this brief). Ties break by bead priority field, then
age (oldest first).

This captures the core industrial-engineering insight: subordinate to the
constraint, maximize throughput by adjudicating the highest-unlock item first.
But it has five documented gaps:

### 1. Age as a weighted component, not a tiebreaker

Age only resolves exact ties today. A 30-day-old brief with the same unlock_count
as a fresh brief ranks identically until the tie-break fires.

Fix: `score = unlock_count + 0.06 × normalized_age`

Borrowed from the LSST feature scheduler (Naghib 2019): declared priority
dominates at weight 1.0, secondary features (age, urgency) at 0.06–0.10 each,
normalized to [0,1] so the ordering within a priority band is well-defined.

### 2. Attention-cost denominator within a band

Not all briefs cost Taylor equal time. Within a priority tier, order by
`unlock_count / attention_cost`:

| Brief class | attention_cost |
|---|---|
| Standard (no stop gates) | 1.0 |
| LaTeX/L4 (requires math review) | 2.0 |
| Server-touching S-rule (dry-run + smoke + per-item OK) | 5.0 |

High-unlock cheap briefs surface before high-unlock expensive briefs.

### 3. Urgency step-function from due-date metadata

The due-date metadata key is the one schema gap worth closing early. Add it as a
bead metadata convention key (not a new bd type). Score becomes:

`score = unlock_count + 0.10 × urgency`

where urgency = 1.0 if due ≤24h, 0.5 if ≤3 days, 0.0 otherwise. A full Whittle
index (urgency × completion probability) requires the replay harness; this
step-function gets most of the value immediately.

### 4. Starvation floor (DSN fairness)

Pure unlock_count starves small programs. The DSN scheduling model writes
fairness as a coefficient in the objective, not an afterthought. Simpler
equivalent as a hard constraint:

**Rule B2.5.1 (proposed):** Any brief aged ≥7 days in the pile is promoted into
the next docket regardless of unlock_count. `present-briefs` checks `bead_age ≥
7d` before sorting and inserts those briefs at the front.

### 5. Context affinity tiebreaker (slew cost)

After unlock_count and age, break remaining ties by `source_rig` matching the
most recently adjudicated brief. If Taylor just approved a hecke brief, show the
next hecke brief before switching to gascity-packs. Context-switch cost is real;
eliminating it at the tiebreak level costs nothing to implement.

### 6. Historical approval-rate weight (requires replay harness — Phase 0)

`score = approval_rate(class) × unlock_count`

A brief class that gets rejected 60% of the time is worth 0.4× its nominal
unlock_count — Taylor should see higher-confidence unlocks first. The data is
already in the audit ledgers. Do not implement until the Phase 0 replay harness
exists to query it.

**Not yet:** Whittle index, bandit-tuned weights, multi-objective dominance
ranking. All three require the replay harness baseline.

---

## No-brainer threshold — the math

The question of how strict to be with no-brainer auto-execution has a
determinate answer once you know the classifier error rate.

**Setup:** N items in queue, fraction α get the wrong recommendation under
auto-execute, Taylor always gets it right. Each item takes time T to execute and
time S for Taylor to decide (not counting execution — that happens either way).

**Auto-execute everything:**
Correct completions at rate `(1−α)/T`, capped at `(1−α)N` total.

**Taylor reviews everything:**
Correct completions at rate `1/(S+T)`, eventually reaches N.

**Breakeven: S = T**

| Condition | Rate winner | Total-count winner |
|---|---|---|
| S > T (Taylor slow relative to execution) | Auto | Taylor (N vs αN) |
| S < T (Taylor fast relative to execution) | Taylor | Taylor |
| S = T | Equal | Taylor |

N only determines when the auto cap is hit, not the rate comparison.

**Current estimates for Taylor:**
- N ≈ 20–40 (pile as of 2026-07-12)
- S ≈ 30 seconds/item in docket mode; 10–30 min for standalone full-form briefs
- T ≈ 5–20 min for true cat-A/B/C/D items

With S ≈ 30s and T ≈ 10 min: S/T ≈ 0.05. Taylor review is ~20× more efficient
at producing correct outcomes per unit Taylor-time than auto-execute at α = 0.5.

**The critical number:** Auto-execute beats Taylor review when α < S/(S+T) ≈ 0.05
for these item types. If the classifier achieves fewer than ~5% wrong on
confident cat-A/B/C/D past all stop gates, auto-execute wins. If more than 5%
wrong, Taylor review wins.

**The missing measurement is α.** The current N5 default-ON policy is the right
prior when α is unknown — designed for α up to 0.5, which is conservative.
Once the Phase 0 replay harness exists, α can be estimated from audit ledger
replay and the threshold can be calibrated. The N7 `classifier_accuracy` field in
no-brainer audit trails should be populated so this estimate is available.

**The question is not "should I be less strict?"** It is "what is the empirical
wrong rate on confident classifications?" That answer changes the policy
derivation. At α < 0.05, relaxing is correct. At α > 0.05, the current
strictness is correct. The math is determinate; the measurement is missing.
