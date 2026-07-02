"""Tests for the on-merge-brief-record order and formula (task-2-brief §2).

The decision logic lives entirely in TOML + agent prompt (no Python helper
script), so this test suite validates:
  1. The order TOML parses and carries the required structural fields.
  2. The formula TOML parses and carries the required steps in order.
  3. The decision-logic contract: step descriptions contain the verbatim
     label check, brief-record creation, and brief-prep intake invocations.

These are the same style of contract tests used in the gastown orchestration
gate (validate_gastown_orchestration_contract / GASTOWN_BUILD_WORKFLOW_CONTRACTS).
"""
from __future__ import annotations

from pathlib import Path

import pytest

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]


PACK_ROOT = Path(__file__).parent.parent / "mathematics"
ORDER_PATH = PACK_ROOT / "orders" / "on-merge-brief-record.toml"
FORMULA_PATH = PACK_ROOT / "formulas" / "on-merge-brief-record.toml"


# ---------------------------------------------------------------------------
# Order TOML contract
# ---------------------------------------------------------------------------


def test_order_file_exists() -> None:
    assert ORDER_PATH.is_file(), f"order file missing: {ORDER_PATH}"


def test_order_parses_as_toml() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert "order" in data, "order TOML must have an [order] section"


def test_order_trigger_is_event() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data["order"]
    assert order.get("trigger") == "event", (
        "on-merge-brief-record order must use trigger = \"event\""
    )


def test_order_on_is_bead_closed() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data["order"]
    assert order.get("on") == "bead.closed", (
        "order must fire on 'bead.closed' events"
    )


def test_order_scope_is_rig() -> None:
    """Rig-scoped so each rig's bead.closed events are independently watched."""
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data["order"]
    assert order.get("scope") == "rig", (
        "order must be rig-scoped (work beads are rig-local)"
    )


def test_order_formula_matches_file() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data["order"]
    assert order.get("formula") == "on-merge-brief-record", (
        "order.formula must reference the companion formula"
    )


def test_order_has_pool() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data["order"]
    assert order.get("pool"), "order must specify a pool for dispatch"


# ---------------------------------------------------------------------------
# Formula TOML contract
# ---------------------------------------------------------------------------


def test_formula_file_exists() -> None:
    assert FORMULA_PATH.is_file(), f"formula file missing: {FORMULA_PATH}"


def test_formula_parses_as_toml() -> None:
    tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))


def test_formula_name_matches_file() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data.get("formula") == "on-merge-brief-record"


def test_formula_has_required_steps() -> None:
    """The formula must have exactly the four steps mandated by the brief."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = data.get("steps", [])
    step_ids = [s["id"] for s in steps]
    required = [
        "identify-closed-bead",
        "check-needs-decision-label",
        "create-brief-record-bead",
        "touch-brief-prep-pipeline",
    ]
    for req in required:
        assert req in step_ids, f"formula missing required step: {req}"


def test_formula_steps_have_correct_dependency_chain() -> None:
    """Steps must chain: identify → check → create → touch."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in data.get("steps", [])}

    assert steps["check-needs-decision-label"].get("needs") == ["identify-closed-bead"]
    assert steps["create-brief-record-bead"].get("needs") == ["check-needs-decision-label"]
    assert steps["touch-brief-prep-pipeline"].get("needs") == ["create-brief-record-bead"]


# ---------------------------------------------------------------------------
# Decision-logic contract (verbatim per task-2-brief §2)
# ---------------------------------------------------------------------------


def _step_text(formula_data: dict, step_id: str) -> str:
    """Return the full description text of a named step."""
    for step in formula_data.get("steps", []):
        if step["id"] == step_id:
            return step.get("description", "")
    raise KeyError(f"step {step_id!r} not found")


def test_label_check_step_checks_needs_decision_label() -> None:
    """check-needs-decision-label step must check for the needs-decision label."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "check-needs-decision-label")
    assert "needs-decision" in text, (
        "check step must reference 'needs-decision' label"
    )


def test_label_check_step_exits_cleanly_on_no_label() -> None:
    """When no needs-decision label: step should exit with no action (§2(c))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "check-needs-decision-label")
    # The step must describe a clean exit when the label is absent
    assert "exit 0" in text or "nothing to do" in text, (
        "check step must exit cleanly when needs-decision label is absent"
    )


def test_brief_record_step_uses_expected_title_format() -> None:
    """Brief-record bead title must follow `[brief-record] <X-id> <title>` (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "create-brief-record-bead")
    assert "[brief-record]" in text, (
        "create step must title the bead with [brief-record] prefix"
    )
    assert "CLOSED_ID" in text or "X-id" in text, (
        "create step must reference the source bead id in the title"
    )


def test_brief_record_step_sets_source_bead_metadata() -> None:
    """Brief-record bead must carry metadata linking to source bead X (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "create-brief-record-bead")
    assert "source_bead" in text, (
        "create step must set source_bead metadata on the brief-record bead"
    )


def test_brief_prep_step_uses_source_var() -> None:
    """touch-brief-prep-pipeline must pass source=<closed-bead-id> (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "touch-brief-prep-pipeline")
    assert "source" in text, (
        "brief-prep intake step must pass source var pointing to the closed bead"
    )


def test_brief_prep_step_uses_decision_type() -> None:
    """brief_type must be 'decision' per the brief-prep formula's enum (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "touch-brief-prep-pipeline")
    assert "decision" in text, (
        "brief-prep intake must use brief_type='decision'"
    )


def test_formula_step_order_matches_brief_requirements() -> None:
    """Steps must appear in the correct execution order."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = data.get("steps", [])
    step_ids = [s["id"] for s in steps]

    identify_idx = step_ids.index("identify-closed-bead")
    check_idx = step_ids.index("check-needs-decision-label")
    create_idx = step_ids.index("create-brief-record-bead")
    touch_idx = step_ids.index("touch-brief-prep-pipeline")

    assert identify_idx < check_idx < create_idx < touch_idx, (
        "formula steps must appear in the order required by task-2-brief §2: "
        "identify → check → create → touch"
    )


def test_order_and_formula_names_are_consistent() -> None:
    """Order formula field must match formula file's formula field."""
    order_data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    formula_data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert order_data["order"]["formula"] == formula_data["formula"]


# ---------------------------------------------------------------------------
# C4 — trigger-bead rework: durable scan, no phantom event vars
# ---------------------------------------------------------------------------


def test_formula_has_no_phantom_event_machinery() -> None:
    """C4: GC_TRIGGER_BEAD_ID, `gc events --since-cursor`, and the
    `{{vars.CLOSED_ID}}` stanza are all wrong and must be gone."""
    text = FORMULA_PATH.read_text(encoding="utf-8")
    assert "GC_TRIGGER_BEAD_ID" not in text
    assert "since-cursor" not in text
    assert "{{vars.CLOSED_ID}}" not in text
    assert "mol sling" not in text, "must not reference the nonexistent `mol sling`"


def test_formula_identify_step_is_a_durable_scan() -> None:
    """C4: identify step lists recently closed needs-decision beads."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "identify-closed-bead")
    assert "bd list" in text
    assert "--status closed" in text
    assert "needs-decision" in text


def test_formula_dedupes_existing_brief_records() -> None:
    """C4: coalescing — skip beads that already have a brief-record."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "check-needs-decision-label")
    assert "[brief-record]" in text, "dedup must key on the brief-record title prefix"


def test_formula_brief_prep_uses_mol_pour() -> None:
    """I4a: primary intake idiom is `bd mol pour`, not `mol sling`."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "touch-brief-prep-pipeline")
    assert "bd mol pour" in text
