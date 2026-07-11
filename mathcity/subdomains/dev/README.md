# mathcity-dev

Pack-development workflow for the owned mathcity pack family
(`mathcity/` + its subdomain child packs, per
[ADR 0002](../../../docs/adr/0002-mathcity-subdomain-pack-model.md)).

Contents:

- **[POLICY.md](./POLICY.md)** — the Pack Portability & Boundary Policy:
  four pillars (reproducibility/portability, ownership boundary,
  upstream-change discipline, plan-time impact review) with per-rule
  pass/fail criteria (P1.1–P4.3), the approve/revise/reject/defer verdict
  vocabulary, and the three input shapes (plan doc, beads convoy,
  current-state audit). Source-of-truth for the `check-hygiene` gate skill
  and for priming the mathcity mayor.

Planned:

- `skills/check-hygiene/` — the plan/convoy/audit gate built from
  POLICY.md via skill-creator (materializes as
  `mathcity-dev.check-hygiene` when this pack is imported).

Import independently of the parent pack:

```toml
[imports."mathcity-dev"]
source = "../gascity-packs/mathcity/subdomains/dev"
```
