"""Tests for the tail-end-detector pure core (ready-but-never-dispatched tail).

RED-first: the module under test does not exist yet.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "assets" / "scripts"
MODULE_PATH = SCRIPTS / "tail-end-detector.py"
VALIDATOR = SCRIPTS / "lost-bead-filter.py"

spec = importlib.util.spec_from_file_location("tail_end_detector", MODULE_PATH)
ted = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ted)

NOW = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)


def bead(bid, *, days_idle, title="do the thing", itype="task",
         created=None, updated=None):
    """Build a bead whose real idle age is `days_idle` days."""
    ts = (NOW - timedelta(days=days_idle)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "id": bid,
        "title": title,
        "issue_type": itype,
        "status": "open",
        "priority": 2,
        "created_at": created or ts,
        "updated_at": updated or ts,
    }


# ---- Fork 1: idle measure = max(created, updated, last_activity) ----

def test_real_idle_uses_the_most_recent_activity():
    b = {
        "id": "x-1",
        "created_at": "2026-06-01T00:00:00Z",   # very old
        "updated_at": "2026-08-03T12:00:00Z",   # 1 day before NOW
        "last_activity": "2026-08-02T12:00:00Z",
    }
    idle_days = ted.real_idle_seconds(b, NOW) / 86400
    assert 0.9 < idle_days < 1.1  # keyed off the newest ts, not created_at


def test_three_day_idle_bead_registers_on_first_scan():
    # No cache / first-observation state involved: a 4-day-idle bead is
    # actionable immediately.
    b = bead("x-2", days_idle=4)
    out = ted.find_actionable_tail(
        [b], ready_ids={"x-2"}, routed_ids=set(), now=NOW,
        min_idle_seconds=3 * 86400,
    )
    assert [x["id"] for x in out] == ["x-2"]


def test_fresh_bead_under_three_days_is_excluded():
    b = bead("x-3", days_idle=2)
    out = ted.find_actionable_tail(
        [b], ready_ids={"x-3"}, routed_ids=set(), now=NOW,
        min_idle_seconds=3 * 86400,
    )
    assert out == []


# ---- Filter: work-type / scaffolding / gated / routed / blocked ----

def test_blocked_bead_not_in_ready_is_excluded():
    b = bead("x-4", days_idle=10)
    out = ted.find_actionable_tail(
        [b], ready_ids=set(), routed_ids=set(), now=NOW,
        min_idle_seconds=3 * 86400,
    )
    assert out == []


def test_routed_bead_is_excluded_dedup_with_stuck_bead_watch():
    b = bead("x-5", days_idle=10)
    out = ted.find_actionable_tail(
        [b], ready_ids={"x-5"}, routed_ids={"x-5"}, now=NOW,
        min_idle_seconds=3 * 86400,
    )
    assert out == []


@pytest.mark.parametrize("title", [
    "Refinery patrol sweep", "Deacon witness", "Polecat drain",
])
def test_scaffolding_titles_excluded(title):
    b = bead("x-6", days_idle=10, title=title)
    out = ted.find_actionable_tail(
        [b], ready_ids={"x-6"}, routed_ids=set(), now=NOW,
        min_idle_seconds=3 * 86400,
    )
    assert out == []


def test_rig_id_and_bare_rig_title_excluded():
    b1 = bead("he-rig-abc", days_idle=10)
    b2 = bead("x-7", days_idle=10, title="hecke")
    out = ted.find_actionable_tail(
        [b1, b2], ready_ids={"he-rig-abc", "x-7"}, routed_ids=set(),
        now=NOW, min_idle_seconds=3 * 86400,
    )
    assert out == []


def test_gated_titles_excluded():
    b = bead("x-8", days_idle=10, title="do X (taylor-gated)")
    out = ted.find_actionable_tail(
        [b], ready_ids={"x-8"}, routed_ids=set(), now=NOW,
        min_idle_seconds=3 * 86400,
    )
    assert out == []


def test_non_work_issue_types_excluded():
    for itype in ("spec", "convoy", "epic", "event", "decision"):
        b = bead("x-9", days_idle=10, itype=itype)
        out = ted.find_actionable_tail(
            [b], ready_ids={"x-9"}, routed_ids=set(), now=NOW,
            min_idle_seconds=3 * 86400,
        )
        assert out == [], itype


def test_actionable_tail_sorted_oldest_first():
    beads = [bead("young", days_idle=4), bead("old", days_idle=40),
             bead("mid", days_idle=10)]
    out = ted.find_actionable_tail(
        beads, ready_ids={"young", "old", "mid"}, routed_ids=set(),
        now=NOW, min_idle_seconds=3 * 86400,
    )
    assert [x["id"] for x in out] == ["old", "mid", "young"]


# ---- Fork 3: classification split + batch cap ----

def test_classify_superseded_when_very_old():
    assert ted.classify_bead(bead("a", days_idle=40), NOW, 30 * 86400) == "superseded"


def test_classify_resling_when_recent_enough():
    assert ted.classify_bead(bead("b", days_idle=5), NOW, 30 * 86400) == "resling"


def test_select_batches_caps_and_prioritizes_oldest():
    # 5 superseded (>=30d) + 5 resling (3-30d); caps 2 and 3.
    sup = [bead(f"s{i}", days_idle=30 + i) for i in range(5)]
    res = [bead(f"r{i}", days_idle=4 + i) for i in range(5)]
    cands = ted.find_actionable_tail(
        sup + res, ready_ids={b["id"] for b in sup + res},
        routed_ids=set(), now=NOW, min_idle_seconds=3 * 86400,
    )
    superseded, resling = ted.select_batches(
        cands, NOW, supersede_age_seconds=30 * 86400,
        resling_cap=3, supersede_cap=2,
    )
    assert len(superseded) == 2 and len(resling) == 3
    # oldest-first within each bucket
    assert superseded[0]["id"] == "s4"
    assert resling[0]["id"] == "r4"


# ---- Fork 2: emitted record validates against the real pipeline schema ----

@pytest.mark.parametrize("kind", ["superseded", "resling"])
def test_rendered_record_passes_lost_bead_filter_validate(kind, tmp_path):
    b = bead("gsp-demo1", days_idle=40 if kind == "superseded" else 5)
    toml_text = ted.render_record(b, kind, NOW, observed_at="2026-08-04T12:00:00Z")
    (tmp_path / "gsp-demo1.tail.toml").write_text(toml_text)
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "validate", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    # correct fingerprint per bucket so the rollup groups them apart
    assert f"ready_idle_tail_{kind}" in toml_text


def test_fingerprints_differ_between_buckets():
    sup = ted.render_record(bead("a", days_idle=40), "superseded", NOW,
                            observed_at="2026-08-04T12:00:00Z")
    res = ted.render_record(bead("b", days_idle=5), "resling", NOW,
                            observed_at="2026-08-04T12:00:00Z")
    assert "close_moot" in sup and "resling" in res
