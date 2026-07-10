# Contributing/Development

Issues and pull requests are welcome. 

A number of packs have been made for helping gascity and gascity-packs development. 

Discipline for sending good work *to* another repo — planning, building, reviewing, and shipping the PRs your city authors.

| Pack | Description |
| --- | --- |
| [contributing](./contributing) | Stitches the full external-contributor lifecycle for `gastownhall/gascity` — write a good issue, find priority work, open a PR, self-review — into one map. It imports `pr-pipeline` for steps 2-4 and adds the net-new `write-issue` issue-authoring discipline for step 1. |
| [pr-pipeline](./pr-pipeline) | Ships the author-side PR workflows as formulas (and four wrapper `pr` commands): plan an issue into a structured plan, map a change's blast radius, self-review an outgoing PR against an 11-category scorecard, and run a pre-push gate. None of them push or open PRs. |

## Build Methodology Packs

A **methodology pack** is a pack that implements the `build-base` workflow contract — the shared lifecycle of requirements, plan, plan review, decomposition, implementation, review, and finalize — with its own formulas and prompt assets (for example `bmad`, `compound-engineering`, `superpowers`, and `gstack`, alongside the `gascity` base pack's own `build-basic` reference implementation).

If you are creating a build methodology pack like superpowers or gascity, start with the [base requirements](./gascity/REQUIREMENTS.md) — the normative compatibility contract every methodology pack must preserve — then see the [build methodology framework audit](./docs/design/build-methodology-framework-audit.md) for the current parity assessment and proposed beginner-friendly updates.

## Update the pack's README

When a pack's surface changes, update its README in the same PR so the docs stay current with the code.

## Publishing registry releases

Registry releases are content-addressed. 

Use the Make targets so the release commit and hash are stamped by `gc` instead of hand-authored:

```sh
GC=/path/to/gc make registry-publish \
  PACK=slack-mini \
  VERSION=0.1.1 \
  DESCRIPTION="Release summary."
```

`GC` defaults to `gc`, so local testing can point it at an uninstalled build.
`REGISTRY_COMMIT` defaults to `HEAD`, and only tracked files at that commit are
hashed; commit pack content before publishing. For new packs, also pass
`PACK_DESCRIPTION="..."`. 



To withdraw a bad consumed release without rewriting it:

```sh
make registry-withdraw \
  PACK=slack-mini \
  VERSION=0.1.0 \
  REASON="Superseded by 0.1.1."
```



Before opening a pull request, run:

```sh
make registry-format-validate
GC=/path/to/gc make registry-validate
```

## Publishing a pack to the registry

The `registry.toml` is the public catalog. Each `[[pack.release]]` carries a content hash that `validate_registry.py` enforces against the pack tree at the pinned `commit`. To register a new pack, commit it on your branch, then mint a ready-to-paste entry with the canonical hash:

```bash
# Print just the content hash for a pack at a given commit (default: HEAD)
python3 validate_registry.py --compute <pack> --commit <ref>

# Print a full [[pack]] block to paste into registry.toml
python3 validate_registry.py --emit-entry <pack> \
  --version 0.1.0 \
  --pack-description "One-line catalog description." \
  --release-description "Initial <pack> pack release."

# Validate the catalog (default, no-arg invocation — same as CI)
python3 validate_registry.py
```

The hash is derived from a sorted manifest of each tracked file's relative path, mode, and blob SHA-256 — so it is deterministic and reproducible. A maintainer re-pins releases to a single published commit at release time.

## Release compatibility and inference gates

Supported pack releases are also gated by the registry-driven compatibility smoke in `scripts/pack_release_compat.py` and the
`Pack Release Compatibility` workflow. First-class supported packs also have a model-backed formula gate in `scripts/gascity_pack_inference_gate.py`, plus a scheduled supported-pack nightly workflow. See [Release Compatibility Testing](./docs/design/release-compatibility-testing.md) for the release-time and nightly test contract.
