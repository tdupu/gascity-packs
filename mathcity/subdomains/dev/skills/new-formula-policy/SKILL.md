---
name: new-formula-policy
description: >
  Amend POLICY-formulas.md (mathcity formula policy, prefix F) with a new
  or revised rule. Use when the user says "add a formula policy rule",
  "amend formula policy", "new-formula-policy", or when check-formula-hygiene
  finds a gap that requires a new rule rather than a code fix. Full
  Taylor-gated amendment procedure. Companion: check-formula-hygiene.
companion: "[[check-formula-hygiene]]"
---

# new-formula-policy

Amend `mathcity/POLICY-formulas.md` (prefix F, version controlled) by adding,
revising, or repealing a rule. Taylor approval is required before any edit.

## Step 0 — Read current policy

```bash
cat ~/gt/gascity-packs/mathcity/POLICY-formulas.md
```

Note the current version, status, and the highest-numbered rule in each
pillar. Also read `mathcity/docs/rule-prefix-registry.md` to confirm prefix F
is registered.

## Step 1 — Draft the amendment

Present a structured draft to Taylor (or to the brief stack via `create-brief`
if Taylor is not in-session):

```
PROPOSED AMENDMENT to POLICY-formulas.md — <date>

  Rule ID:      F<N.M>   (next available in pillar N)
  Action:       Add | Revise | Repeal
  Rule text:    <what the rule requires>
  Pass:         <checkable condition>
  Fail:         <what a violation looks like>
  Rationale:    <why this rule is needed; what failure it prevents>
  Change log:   Version <current+0.1>, <date>, "<short description>"
```

For a repeal: the rule ID is permanent — mark it `[REPEALED <date>]` in the
policy body and note the reason. Never delete a rule ID.

## Step 2 — Gate on Taylor approval

Full [[present-it]] — a policy amendment is architecture-class. Do not edit
any file before Taylor approves in this conversation, or before a Taylor-signed
brief verdict reaches APPROVED.

If Taylor is not in-session: file a brief via `create-brief` and stop here.

## Step 3 — Apply the amendment

Only after approval:

```bash
# Edit the policy doc
$EDITOR ~/gt/gascity-packs/mathcity/POLICY-formulas.md
# Add the new rule under the correct pillar
# Bump the version number (minor increment for new/revised rule, patch for repeal)
# Append a row to the Change Log table
```

Run gitleaks to confirm no secrets entered the file:
```bash
gitleaks detect --no-git --source ~/gt/gascity-packs/mathcity/POLICY-formulas.md
```

## Step 4 — Verify with check-formula-hygiene

Run the checker on any existing formula that might be affected by the new rule:
```bash
# Example: check formula-creator-math after a pillar-3 amendment
cat ~/gt/gascity-packs/mathcity/formulas/formula-creator-math.toml | \
  # invoke check-formula-hygiene with the TOML path
```

Use `check-formula-hygiene` (this skill's companion) to confirm the policy
and the checker are in sync.

## Step 5 — Commit to ~/gt/gascity-packs

```bash
cd ~/gt/gascity-packs
git add mathcity/POLICY-formulas.md
git commit -m "policy(formulas): add/revise/repeal F<N.M> — <one-line description>"
git push origin main
```

Report the commit SHA.

## Hard rules

- Never edit the policy before Taylor approves.
- Rule IDs are permanent — repeal, never delete.
- Draft policies (Status: Draft) may be amended freely while Draft.
  Adopted policies require this full procedure even for typos (PP2.3).
- Do not amend to excuse an existing violation — fix the formula first.
- After amending, run check-formula-hygiene on all affected formulas.
