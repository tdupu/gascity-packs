"""Unit tests for the stuck-bead-watch detector's pure logic (no bd/gc calls)."""
import sys
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import importlib.util

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "assets" / "scripts" / "stuck-bead-watch.py"
_spec = importlib.util.spec_from_file_location("stuck_bead_watch", _SCRIPT_PATH)
sbw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sbw)


def _bead(bead_id, priority=2, assignee=None, routed_to="mathcity.brief-operator",
          status="open", created_at="2026-07-28T00:00:00Z"):
    return {
        "id": bead_id,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "created_at": created_at,
        "metadata": {"gc.routed_to": routed_to} if routed_to else {},
    }


def _session(session_name, state="active"):
    return {"session_name": session_name, "state": state}


def test_never_claimed_bead_is_stuck_candidate():
    now = datetime(2026, 7, 28, 0, 10, 0, tzinfo=timezone.utc)
    beads = [_bead("gt-a1", assignee=None)]
    sessions = []
    candidates = sbw.find_stuck_candidates(beads, sessions, now, min_age_seconds=180)
    assert [c["id"] for c in candidates] == ["gt-a1"]


def test_claimed_by_live_session_is_not_stuck():
    now = datetime(2026, 7, 28, 0, 10, 0, tzinfo=timezone.utc)
    beads = [_bead("gt-a2", assignee="mathcity__brief-operator-gt-x5twj")]
    sessions = [_session("mathcity__brief-operator-gt-x5twj")]
    candidates = sbw.find_stuck_candidates(beads, sessions, now, min_age_seconds=180)
    assert candidates == []


def test_claimed_by_dead_session_is_stuck_candidate():
    now = datetime(2026, 7, 28, 0, 10, 0, tzinfo=timezone.utc)
    beads = [_bead("gt-a3", assignee="mathcity__brief-operator-gt-x5twj")]
    sessions = [_session("mathcity__brief-operator-gt-OTHER")]
    candidates = sbw.find_stuck_candidates(beads, sessions, now, min_age_seconds=180)
    assert [c["id"] for c in candidates] == ["gt-a3"]


def test_too_young_bead_is_not_yet_a_candidate():
    now = datetime(2026, 7, 28, 0, 0, 30, tzinfo=timezone.utc)
    beads = [_bead("gt-a4", assignee=None, created_at="2026-07-28T00:00:00Z")]
    candidates = sbw.find_stuck_candidates(beads, [], now, min_age_seconds=180)
    assert candidates == []


def test_bead_without_routed_to_is_ignored():
    now = datetime(2026, 7, 28, 0, 10, 0, tzinfo=timezone.utc)
    beads = [_bead("gt-a5", assignee=None, routed_to=None)]
    candidates = sbw.find_stuck_candidates(beads, [], now, min_age_seconds=180)
    assert candidates == []


def test_in_progress_bead_is_eligible():
    now = datetime(2026, 7, 28, 0, 10, 0, tzinfo=timezone.utc)
    beads = [_bead("gt-a6", assignee=None, status="in_progress")]
    candidates = sbw.find_stuck_candidates(beads, [], now, min_age_seconds=180)
    assert [c["id"] for c in candidates] == ["gt-a6"]


def test_closed_bead_is_ignored():
    now = datetime(2026, 7, 28, 0, 10, 0, tzinfo=timezone.utc)
    beads = [_bead("gt-a7", assignee=None, status="closed")]
    candidates = sbw.find_stuck_candidates(beads, [], now, min_age_seconds=180)
    assert candidates == []


def test_grace_window_seconds_maps_priority():
    windows = {0: 300, 1: 600, 2: 1200, 3: 2700, 4: 2700}
    assert sbw.grace_window_seconds(0, windows) == 300
    assert sbw.grace_window_seconds(2, windows) == 1200
    assert sbw.grace_window_seconds(4, windows) == 2700


def test_grace_window_seconds_unknown_priority_falls_back_to_p4():
    windows = {0: 300, 1: 600, 2: 1200, 3: 2700, 4: 2700}
    assert sbw.grace_window_seconds(9, windows) == 2700


def test_cache_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp)
        assert sbw.read_cache_entry(cache_dir, "gt-b1") is None
        sbw.write_cache_entry(cache_dir, "gt-b1", "2026-07-28T00:00:00Z")
        entry = sbw.read_cache_entry(cache_dir, "gt-b1")
        assert entry["first_seen_stuck"] == "2026-07-28T00:00:00Z"
        sbw.clear_cache_entry(cache_dir, "gt-b1")
        assert sbw.read_cache_entry(cache_dir, "gt-b1") is None


def test_classify_and_escalate_writes_valid_schema_toml():
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "cache"
        classification_root = Path(tmp) / "classifications"
        bead = _bead("gt-c1", assignee=None)
        create_calls = []
        relate_calls = []

        def fake_bd_create_event(title, description):
            create_calls.append((title, description))
            return "gt-event-1"

        def fake_bd_dep_relate(a, b):
            relate_calls.append((a, b))

        event_id = sbw.classify_and_escalate(
            bead, cache_dir, classification_root, "2026-07-28T01:00:00Z",
            bd_create_event=fake_bd_create_event,
            bd_dep_relate=fake_bd_dep_relate,
        )
        assert event_id == "gt-event-1"
        toml_path = classification_root / "gt-c1.toml"
        assert toml_path.exists()
        content = toml_path.read_text()
        assert 'schema = "lost-bead-classification.v1"' in content
        assert 'bead_id = "gt-c1"' in content
        assert len(create_calls) == 1
        # P1.19 — append a new LINKED bead: the event bead must be bd-dep-related
        # back to the source bead it classifies, not just referenced in prose.
        assert relate_calls == [("gt-event-1", "gt-c1")]


def test_classify_and_escalate_includes_routed_step_bead_reason_dead_assignee():
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "cache"
        classification_root = Path(tmp) / "classifications"
        bead = _bead("gt-c2", assignee="mathcity__brief-operator-gt-dead")

        event_id = sbw.classify_and_escalate(
            bead, cache_dir, classification_root, "2026-07-28T01:00:00Z",
            bd_create_event=lambda t, d: "gt-event-2",
            bd_dep_relate=lambda a, b: None,
        )
        assert event_id == "gt-event-2"
        content = (classification_root / "gt-c2.toml").read_text()
        assert "mathcity__brief-operator-gt-dead" in content
