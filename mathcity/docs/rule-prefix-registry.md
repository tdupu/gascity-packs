# Mathcity Rule Prefix Registry

All rule ID prefixes for mathcity policies are reserved here. Rule IDs are globally unique and immutable (PP1.5). Every policy domain must reserve a prefix here before assigning rule IDs. A prefix once assigned is never reused, even after deprecation.

| Prefix | Domain | POLICY.md home | Status | Example ID |
| --- | --- | --- | --- | --- |
| B, N, L, E, T, D, S | Brief system (multi-pillar) | `subdomains/brief-system/POLICY.md` | Draft (revision 2026-07-12) | B1.4, N5, L2, E3, T1, D2, S7 |
| P | Dev / build hygiene | `subdomains/dev/POLICY.md` | Adopted (amended 2026-07-12) | P1.6, P5.3 |
| SK | Agent skills | `agent-skills/POLICY.md` | Pending (file not yet written) | SK1.1 |
| BP | Bead policy | `BEADPOLICY.md` (pack root) | Draft (2026-07-12) | BP1.1, BP4.3 |
| PP | Policy-policy (meta) | `POLICY-POLICY.md` (pack root) | Draft (2026-07-12) | PP1.1, PP3.2 |
| LX | LaTeX subdomain (bead-side LaTeX work) | `subdomains/latex/POLICY.md` | Draft (2026-07-12) | LX1.1, LX4.6 |
| M | Magma packages (naming, READMEs, testing, bead lifecycle, profiling, pipelines) | `subdomains/magma/POLICY.md` | Draft (2026-07-12) | M1.3, M7.5 |
| LM | LMFDB subdomain (labels, experiments, server usage, type creation) | `subdomains/lmfdb/POLICY.md` | Draft (2026-07-12) | LM1.3, LM3.4 |
| C | Computing (caching/memoization, DRY/code-factoring, intrinsic testing, regression testing) | `subdomains/computing/POLICY.md` | Draft (2026-07-12) | C1.1, C3.2, C4.1 |

## Rules

- Reserve a prefix BEFORE assigning any rule IDs (PP5.2).
- Prefix must be 1–3 uppercase letters, unique across this table.
- Once a prefix appears in a committed POLICY.md, it is permanent.
- Add a row here as part of the same commit that creates the POLICY.md.
