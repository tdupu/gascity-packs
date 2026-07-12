# Mathcity Policy Governance

| Field | Value |
| --- | --- |
| Status | Draft |
| Date | 2026-07-12 |
| Decided | Taylor Dupuy |
| Applies to | All policy documents inside the `mathcity` pack and its subdomains |
| Consumers | `skill-creator-plus`, any `check-X-policy` skill, any `new-X-policy` skill, `brief-prep`, Mayor dispatch |

Governs what a policy document IS, how policy domains are structured, how rules get IDs, how policies are adopted and amended, and how sub-policies relate to their parent. Every rule in every mathcity POLICY.md must be consistent with this document. On conflict, POLICY-POLICY.md wins.

---

## Core definitions

- **Policy domain.** A named scope of decisions that recur often enough to warrant written rules. Examples: brief-system, dev, agent-skills. Each domain has exactly one POLICY.md as its canonical source of truth.
- **Rule.** A named, enumerated, mechanically checkable constraint. Rules are numbered within their domain. Every rule has exactly one ID.
- **Rule ID.** A globally unique, immutable token of the form `<prefix><section>.<number>` (e.g., `B1.4`, `P1.6`, `SK3.1`). Once assigned, a rule ID is never reused, even after deprecation.
- **Trinity.** The three artifacts required for every live policy domain: `POLICY.md` (prose + rules) + `check-X-policy` (read-only auditor) + `new-X-policy` (sole write path for rule changes).
- **Prefix registry.** The file `mathcity/docs/rule-prefix-registry.md` — maps each one-or-two-letter prefix to its owner domain, status, and home path. A domain MUST reserve a prefix there before assigning rule IDs.

---

## Pillar 1 — Policy structure (PP1.x)

- **PP1.1 Every live policy domain has exactly one trinity.** POLICY.md + check-X-policy + new-X-policy. No partial adoption: a domain with a POLICY.md but no check skill is incomplete and the POLICY.md is not enforceable.
- **PP1.2 POLICY.md is the source of truth.** check-X-policy audits against it. new-X-policy amends it. Skills, formulas, and gates.toml cite rule IDs — not prose summaries — so they stay in sync when rules are renumbered or deprecated.
- **PP1.3 check-X-policy is read-only.** It reports drift (approve / revise / defer). It never mutates bead state, files, or config. A check skill that writes anything is a PP1.3 violation.
- **PP1.4 new-X-policy is the sole write path for rules.** Rules enter, change, or exit only by Taylor approving a `new-X-policy` proposal. Editing POLICY.md in place without going through new-X-policy is a violation, even for typo fixes: update via a new-X-policy micro-proposal, commit, done.
- **PP1.5 Rule IDs are globally unique and immutable.** The prefix registry enforces uniqueness across domains. Once a rule ID appears in any committed POLICY.md, it is permanent: the rule may be deprecated (status: deprecated in the rule entry) but the ID is never reassigned to a different rule.

---

## Pillar 2 — Policy lifecycle (PP2.x)

- **PP2.1 Lifecycle states: Draft → Adopted → Deprecated.** A POLICY.md in `Status: Draft` governs nothing — it may not be cited in check skills or gate formulas. Only `Status: Adopted` policies are enforceable.
- **PP2.2 Adoption requires Taylor sign-off.** A Draft transitions to Adopted when Taylor explicitly approves the document in conversation or via a decision bead. The adopting date is recorded in the header table.
- **PP2.3 Amendment goes through new-X-policy.** No in-place edits to an Adopted POLICY.md except via a new-X-policy proposal approved by Taylor. Each change is appended to the Change Log at the bottom of the document with its date and Taylor's rationale.
- **PP2.4 Deprecated rules are tombstoned, not deleted.** A deprecated rule stays in the document with `~~strikethrough~~` title and `Status: deprecated (superseded by <new-id>)`. This preserves audit trails and prevents ID reuse.

---

## Pillar 3 — Sub-policies (PP3.x)

- **PP3.1 Sub-policies are sections first.** A new concern that belongs under an existing domain starts as a lettered section of that domain's POLICY.md with its own rule prefix series (e.g., E-rules for experiments inside brief-system). This is the default for all new rule families.
- **PP3.2 Promotion threshold.** A sub-policy graduates to its own POLICY.md (its own domain + trinity) when ALL THREE hold: (a) the sub-policy has more than ~20 rules; (b) it has or clearly warrants its own `check-X-policy` skill; (c) it has an independent amendment cadence (changes to it don't co-move with the parent domain). Below this threshold, stay as a section.
- **PP3.3 Rule IDs survive promotion.** When a sub-policy section graduates to its own file, all its rule IDs are preserved unchanged. No renumbering. The prefix registry entry is updated to point to the new file. Cross-references in other policies and check skills need no update.

---

## Pillar 4 — Relationship to gates.toml and formulas (PP4.x)

- **PP4.1 Formulas and skills cite gate IDs, not rule IDs.** The formula layer operates on gates (G1–G16 + G5b); gates cite rules. This keeps the formula layer stable when rules are amended.
- **PP4.2 Every gate entry in gates.toml must carry a `rules` field.** The `rules` field is a list of rule IDs that the gate enforces (e.g., `rules = ["B1.5", "B1.7"]`). A gate with no `rules` field is a PP4.2 violation (audited by `check-build-policy`).
- **PP4.3 Gate IDs are never deleted or reused.** A superseded gate gets `required = false` and a `superseded_by` field; its ID remains in the registry permanently.

---

## Pillar 5 — Scaffolding new domains (PP5.x)

- **PP5.1 New domains are scaffolded via `skill-creator-plus --policy-domain <name>`.** The scaffolder creates: (a) `POLICY.md` in `Status: Draft` with zero rules and the standard header table; (b) stub `check-<name>-policy` skill with empty audit checklist; (c) stub `new-<name>-policy` skill with proposal template. No rules are pre-populated — rules only enter via the first `new-X-policy` session.
- **PP5.2 Prefix registration is a prerequisite.** Before the scaffolder runs, the caller must have a reserved prefix in `mathcity/docs/rule-prefix-registry.md`. The scaffolder checks this and refuses without it.
- **PP5.3 Skill placement follows P1.14.** `check-X-policy` and `new-X-policy` skills live in the domain's subdomain directory and are exposed via the standard symlink mechanism.

---

## Current policy domains

| Domain | Prefix | POLICY.md home | Status |
| --- | --- | --- | --- |
| Brief system | B, N, L, E, T, D, S | `subdomains/brief-system/POLICY.md` | Draft (revision 2026-07-12) |
| Dev / build hygiene | P | `subdomains/dev/POLICY.md` | Adopted |
| Agent skills | SK | `agent-skills/POLICY.md` | Pending (not yet written) |
| Bead policy | BP | `BEADPOLICY.md` (pack root — provisional; see PP3.2) | Draft (2026-07-12) |
| LaTeX subdomain | LX | `subdomains/latex/POLICY.md` | Draft (2026-07-12) |

The canonical prefix registry is at `mathcity/docs/rule-prefix-registry.md` (PP5.2). The table above is a summary; the registry is authoritative.

---

## Verdict vocabulary (shared across all policy check skills)

| Verdict | Meaning |
| --- | --- |
| **approve** | Current state is compliant; no action required |
| **revise** | Drift found; each item listed with the rule violated and one-line remediation |
| **defer** | A human call is needed; the open question is stated explicitly |

`check-X-policy` skills never emit **reject** (reject applies only to artifacts, not to audits of running state).

---

## Change Log

| Date | Change | Rationale |
| --- | --- | --- |
| 2026-07-12 | Initial draft | Taylor directive: policy-first rollout of brief system; POLICY-POLICY scaffolds the governance layer |
