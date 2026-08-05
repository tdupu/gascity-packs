#!/usr/bin/env python3
# mathcity/assets/scripts/tail-end-detector.py
"""Catch READY-BUT-NEVER-DISPATCHED work beads (the "tail end").

stuck-bead-watch.py catches beads that WERE dispatched (carry routing
metadata) then froze. This detector catches the complementary lost class named
on gsp-2bowrk's CONSERVATION INVARIANT: beads that are ready+unblocked, were
never slung (no routing metadata), and have sat idle past the >3d age trigger.

It reuses the existing lost-bead pipeline (Fork 2): it emits the SAME
`lost-bead-classification.v1` records that `lost-bead-classification-rollup`
consumes, under distinct fingerprints, so the rollup turns them into
resling/close decision briefs. No parallel pipeline.

Design (docs/superpowers/specs/2026-08-04-tail-end-detector-design.md):
- Fork 1 real idle age = max(created_at, updated_at, last_activity); a
  genuinely-3-day-idle bead registers on the FIRST scan (no waiting room).
- Fork 3 classification split: idle >= SUPERSEDE_AGE_DAYS -> superseded ->
  close_moot brief; idle in [3d, SUPERSEDE_AGE_DAYS) -> resling. Both buckets
  batch-capped, oldest-first, so a large tail is drained at a fleet-absorbing
  cadence and never dumped at once.
- Fork 4 fail-loud (P6.1): subprocess timeouts -> nonzero exit; the
  actionable-tail count is a heartbeat -- if it GROWS or the run errors, emit
  a visible event bead; the count is printed every run.

Pure-Python, stdlib only -- no LLM/session cost per tick.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---- configuration / defaults -------------------------------------------

DEFAULT_MIN_IDLE_DAYS = 3
DEFAULT_SUPERSEDE_AGE_DAYS = 30
DEFAULT_RESLING_BATCH_CAP = 10
DEFAULT_SUPERSEDE_BATCH_CAP = 25

DEFAULT_RIGS = (
    "gascity-packs", "hecke", "agent_skills", "lmfdb",
    "jacobi", "homog", "magma_clifford_algebras",
)

# Never-dispatched == carries none of these routing keys. Same set
# stuck-bead-watch keys off; excluding them makes the two detectors' target
# sets disjoint (dedup) and encodes "never dispatched".
ROUTED_METADATA_KEYS = ("gc.routed_to", "gc.run_target", "gc.execution_routed_to")

# A "work bead" is an independently-slingable issue, not a molecule/convoy
# internal step or a meta bead (spec/convoy/epic/event/decision/session).
WORK_TYPES = ("task", "bug", "feature")

SCAFFOLD_WORDS = ("patrol", "deacon", "witness", "refinery", "polecat")
GATE_WORDS = ("taylor-gated", "gh-auth")

OBSERVER = "tail-end-detector"

SUBPROCESS_TIMEOUT_SECONDS = 30  # matches stuck-bead-watch (Dolt latency headroom)

# Distinct fingerprints so the rollup groups tail records apart from
# stuck-bead-watch's, and apart from each other by bucket.
FINGERPRINT_SUPERSEDED = "ready_idle_tail_superseded"
FINGERPRINT_RESLING = "ready_idle_tail_resling"
FINGERPRINT_GROWING = "ready_idle_tail_growing"

# Per-bucket lost-bead-classification.v1 field mapping. suspected_source is
# "unknown" because a never-dispatched bead has no dispatch provenance;
# repair_candidate is False for both so these stay OUT of the upstream
# (fix-the-producing-formula) rollup -- an un-slung bead is not a formula
# defect -- and only feed the downstream resling/close rollup.
BUCKETS = {
    "superseded": {
        "lost_class": "stale_or_duplicate",
        "recommendation": "close_moot",
        "root_class": "duplicate_or_superseded_source",
        "repair_candidate": False,
        "fingerprint": FINGERPRINT_SUPERSEDED,
        "rationale": (
            "Ready+unblocked but never dispatched and idle far past the "
            "supersession age proxy; almost certainly obsolete -- recommend "
            "close as moot (gated through a close brief, not auto-closed)."
        ),
    },
    "resling": {
        "lost_class": "immediate_strand",
        "recommendation": "resling",
        "root_class": "no_worker_claimed",
        "repair_candidate": False,
        "fingerprint": FINGERPRINT_RESLING,
        "rationale": (
            "Ready+unblocked, still within the supersession age proxy, but "
            "never dispatched -- valid work that was never slung; recommend "
            "resling at a fleet-absorbing cadence."
        ),
    },
}


def fail(message: str) -> None:
    print(f"tail-end-detector: {message}", file=sys.stderr)
    raise SystemExit(1)


def _run(cmd: list[str], **kwargs):
    """subprocess.run wrapper that fails loud (P6.1) on a hang instead of
    letting TimeoutExpired propagate as an unhandled traceback."""
    try:
        return subprocess.run(cmd, timeout=SUBPROCESS_TIMEOUT_SECONDS, **kwargs)
    except subprocess.TimeoutExpired:
        fail(
            f"command timed out after {SUBPROCESS_TIMEOUT_SECONDS}s: {' '.join(cmd)}\n"
            "Check `gc dolt health` -- a hung gc/bd call usually means Dolt is "
            "degraded or unreachable."
        )


# ---- pure core (unit-tested) --------------------------------------------

def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def real_idle_seconds(bead: dict, now: datetime) -> float:
    """Fork 1: idle age keyed off the newest of created/updated/last_activity,
    never a first-observation timestamp."""
    stamps = [
        bead.get("created_at"), bead.get("updated_at"), bead.get("last_activity"),
    ]
    parsed = [parse_ts(s) for s in stamps if s]
    if not parsed:
        return 0.0
    return (now - max(parsed)).total_seconds()


def is_scaffolding(bead: dict, rig_names=DEFAULT_RIGS) -> bool:
    title = (bead.get("title") or "").strip()
    low = title.lower()
    if any(word in low for word in SCAFFOLD_WORDS):
        return True
    if re.search(r"-rig-", bead.get("id", "")):
        return True
    if low in {r.lower() for r in rig_names}:  # bare rig-name title
        return True
    return False


def is_gated(bead: dict) -> bool:
    low = (bead.get("title") or "").lower()
    return any(word in low for word in GATE_WORDS)


def is_work_type(bead: dict, work_types=WORK_TYPES) -> bool:
    return bead.get("issue_type") in work_types


def find_actionable_tail(
    open_beads: list[dict],
    ready_ids: set[str],
    routed_ids: set[str],
    now: datetime,
    min_idle_seconds: float,
    work_types=WORK_TYPES,
    rig_names=DEFAULT_RIGS,
) -> list[dict]:
    """Never-dispatched actionable-idle work beads, sorted oldest-first."""
    out = []
    for bead in open_beads:
        if bead.get("status") not in ("open", None):
            continue
        if bead["id"] not in ready_ids:
            continue                      # blocked -> correctly waiting, not us
        if bead["id"] in routed_ids:
            continue                      # dispatched -> stuck-bead-watch's domain
        if not is_work_type(bead, work_types):
            continue
        if is_scaffolding(bead, rig_names):
            continue
        if is_gated(bead):
            continue
        if real_idle_seconds(bead, now) < min_idle_seconds:
            continue
        out.append(bead)
    out.sort(key=lambda b: real_idle_seconds(b, now), reverse=True)
    return out


def classify_bead(bead: dict, now: datetime, supersede_age_seconds: float) -> str:
    if real_idle_seconds(bead, now) >= supersede_age_seconds:
        return "superseded"
    return "resling"


def select_batches(
    candidates: list[dict],
    now: datetime,
    supersede_age_seconds: float,
    resling_cap: int,
    supersede_cap: int,
) -> tuple[list[dict], list[dict]]:
    """Split into (superseded, resling), each oldest-first and capped so a
    large tail drains steadily instead of being dumped (Fork 3)."""
    superseded, resling = [], []
    for bead in sorted(candidates, key=lambda b: real_idle_seconds(b, now), reverse=True):
        if classify_bead(bead, now, supersede_age_seconds) == "superseded":
            superseded.append(bead)
        else:
            resling.append(bead)
    return superseded[:supersede_cap], resling[:resling_cap]


def render_record(bead: dict, kind: str, now: datetime, observed_at: str) -> str:
    """Emit a lost-bead-classification.v1 TOML record for the given bucket."""
    spec = BUCKETS[kind]
    idle_days = real_idle_seconds(bead, now) / 86400
    evidence = [
        "ready+unblocked in `bd ready` but carries no routing metadata "
        f"({'/'.join(ROUTED_METADATA_KEYS)}) -- never dispatched",
        f"idle {idle_days:.1f} days (real max of created/updated/last_activity), "
        "past the >3d tail trigger",
    ]
    title = (bead.get("title") or "").replace("\\", "/").replace('"', "'")
    title = re.sub(r"\s+", " ", title).strip()  # collapse newlines/tabs -> TOML-safe
    return (
        'schema = "lost-bead-classification.v1"\n'
        f'bead_id = "{bead["id"]}"\n'
        f'observed_at = "{observed_at}"\n'
        f'observer = "{OBSERVER}"\n'
        "\n"
        "[finding]\n"
        f'lost_class = "{spec["lost_class"]}"\n'
        f"evidence = {json.dumps(evidence)}\n"
        "\n"
        "[disposition]\n"
        f'recommendation = "{spec["recommendation"]}"\n'
        f'rationale = "{spec["rationale"]}"\n'
        "reversible = true\n"
        "\n"
        "[root_cause]\n"
        f'class = "{spec["root_class"]}"\n'
        'suspected_source = "unknown"\n'
        f"repair_candidate = {str(spec['repair_candidate']).lower()}\n"
        f'fingerprint = "{spec["fingerprint"]}"\n'
        "\n"
        "[tail_end_detector]\n"
        f'bucket = "{kind}"\n'
        f'title = "{title}"\n'
        f'idle_days = {idle_days:.1f}\n'
    )


# ---- edge I/O ------------------------------------------------------------

def _bd_json(rig_dir: Path, *args: str) -> list[dict]:
    result = _run(
        ["bd", *args, "--json", "--readonly", "--limit", "0"],
        cwd=str(rig_dir), capture_output=True, text=True,
    )
    if result.returncode != 0:
        fail(f"bd {' '.join(args)} failed in {rig_dir}: {result.stderr.strip()}")
    data = json.loads(result.stdout or "[]")
    return data if isinstance(data, list) else data.get("issues", [])


def gather_rig(base_dir: Path, rig: str) -> tuple[list[dict], set[str]]:
    rig_dir = base_dir / rig
    opens = _bd_json(rig_dir, "list", "--status", "open")
    ready = {b["id"] for b in _bd_json(rig_dir, "ready")}
    return opens, ready


def gather_routed_ids(base_dir: Path) -> set[str]:
    """City-wide routed id set (all rigs) via `gc bd list --has-metadata-key`.
    Metadata is omitted from plain `bd list --json`, so this is the only way to
    identify dispatched beads server-side."""
    routed: set[str] = set()
    cwd = str(base_dir / DEFAULT_RIGS[0])
    for key in ROUTED_METADATA_KEYS:
        result = _run(
            ["gc", "bd", "list", "--all", "--has-metadata-key", key,
             "--json", "--limit=0"],
            cwd=cwd, capture_output=True, text=True,
        )
        if result.returncode != 0:
            fail(f"gc bd list --has-metadata-key {key} failed: {result.stderr.strip()}")
        for bead in json.loads(result.stdout or "[]"):
            routed.add(bead["id"])
    return routed


def _preflight() -> None:
    result = _run(["gc", "dolt", "health"], capture_output=True, text=True)
    if result.returncode != 0:
        print(
            "I'm sorry, I can't do that - Dolt is unreachable.\n"
            "Run 'gc dolt start' and retry.\n"
            "(tail-end-detector needs Dolt to read bead/ready state.)",
            file=sys.stderr,
        )
        raise SystemExit(1)


def _default_bd_create_event(title: str, description: str) -> str:
    result = _run(
        ["bd", "create", "-t", "event", "--title", title,
         "--description", description, "--silent"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _default_bd_dep_relate(event_id: str, bead_id: str) -> None:
    _run(["bd", "dep", "relate", event_id, bead_id],
         capture_output=True, text=True, check=True)


def read_heartbeat(cache_dir: Path) -> int | None:
    path = cache_dir / "tail-heartbeat.json"
    if not path.exists():
        return None
    try:
        return int(json.loads(path.read_text()).get("actionable_count"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def write_heartbeat(cache_dir: Path, count: int, observed_at: str) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "tail-heartbeat.json").write_text(
        json.dumps({"actionable_count": count, "observed_at": observed_at})
    )


def emit_growth_heartbeat(
    prev: int, current: int, observed_at: str,
    bd_create_event=_default_bd_create_event,
) -> str:
    """Fork 4 / P6.1: the tail is a heartbeat -- if it grows, escalate loudly."""
    body = (
        f'schema = "tail-end-heartbeat.v1"\n'
        f'observer = "{OBSERVER}"\n'
        f'fingerprint = "{FINGERPRINT_GROWING}"\n'
        f'observed_at = "{observed_at}"\n'
        f"previous_actionable = {prev}\n"
        f"current_actionable = {current}\n"
        f"delta = {current - prev}\n"
    )
    return bd_create_event(
        f"tail-end-detector: actionable tail GREW {prev} -> {current}", body,
    )


def _write_records(classification_root: Path, records: list[tuple[str, str]]) -> None:
    classification_root.mkdir(parents=True, exist_ok=True)
    for bead_id, toml_text in records:
        # `.tail.toml` still matches the rollup's `*.toml` glob but never
        # clobbers stuck-bead-watch's `{bead_id}.toml` records (P4.2).
        (classification_root / f"{bead_id}.tail.toml").write_text(toml_text)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, default=Path("."),
                        help="City root containing the rig checkouts.")
    parser.add_argument("--rigs", nargs="+", default=list(DEFAULT_RIGS))
    parser.add_argument("--cache-dir", type=Path,
                        default=Path(".beads/tail-end-detector"))
    parser.add_argument("--classification-root", type=Path,
                        default=Path(".beads/lost-bead-classifications"))
    parser.add_argument("--min-idle-days", type=float, default=DEFAULT_MIN_IDLE_DAYS)
    parser.add_argument("--supersede-age-days", type=float,
                        default=DEFAULT_SUPERSEDE_AGE_DAYS)
    parser.add_argument("--resling-cap", type=int, default=DEFAULT_RESLING_BATCH_CAP)
    parser.add_argument("--supersede-cap", type=int, default=DEFAULT_SUPERSEDE_BATCH_CAP)
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute + classify + report; write no records, "
                             "create no beads.")
    args = parser.parse_args(argv)

    min_idle = args.min_idle_days * 86400
    supersede_age = args.supersede_age_days * 86400

    if not args.dry_run:
        _preflight()
    now = datetime.now(timezone.utc)
    observed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    routed_ids = gather_routed_ids(args.base_dir)
    candidates: list[dict] = []
    for rig in args.rigs:
        opens, ready = gather_rig(args.base_dir, rig)
        candidates.extend(
            find_actionable_tail(opens, ready, routed_ids, now, min_idle)
        )

    superseded, resling = select_batches(
        candidates, now, supersede_age, args.resling_cap, args.supersede_cap,
    )
    actionable = len(candidates)

    records: list[tuple[str, str]] = []
    for bead in superseded:
        records.append((bead["id"], render_record(bead, "superseded", now, observed_at)))
    for bead in resling:
        records.append((bead["id"], render_record(bead, "resling", now, observed_at)))

    prev = read_heartbeat(args.cache_dir)
    grew = prev is not None and actionable > prev

    print(
        f"tail-end-detector: {actionable} actionable-idle never-dispatched "
        f"({len(superseded)} superseded-close, {len(resling)} resling this batch; "
        f"caps {args.supersede_cap}/{args.resling_cap}) "
        f"[prev_tail={prev} {'GROWING' if grew else 'steady/first'}]"
    )
    if args.dry_run:
        print(f"tail-end-detector: DRY-RUN, wrote nothing; total candidates={actionable}")
        return 0

    _write_records(args.classification_root, records)
    if grew:
        event_id = emit_growth_heartbeat(prev, actionable, observed_at)
        print(f"tail-end-detector: HEARTBEAT tail grew {prev}->{actionable} -> event {event_id}")
    write_heartbeat(args.cache_dir, actionable, observed_at)
    print(f"tail-end-detector: wrote {len(records)} classification records "
          f"to {args.classification_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
