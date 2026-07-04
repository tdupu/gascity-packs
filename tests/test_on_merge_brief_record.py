"""Tests for the on-merge-brief-record order and formula (task-2-brief §2).

The decision logic lives entirely in TOML + agent prompt (no Python helper
script), so this test suite validates:
  1. The order TOML parses and carries the required structural fields.
  2. The formula TOML parses and carries the required vapor step.
  3. The decision-logic contract: the step description contains the verbatim
     label check, brief-record creation, and brief-prep intake invocations.

gsp-fqo: formula converted to vapor (phase="vapor", single step). All bd CLI
commands are deterministic — no judgment required. Structural tests updated
accordingly; contract/content tests unchanged (strings still present in the
combined script).
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


def test_order_pool_is_import_qualified() -> None:
    """gsp-fqo: pool must be import-qualified (gastown.dog) not bare 'dog'."""
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    pool = data["order"].get("pool", "")
    assert "." in pool, (
        f"order.pool must be import-qualified (e.g. gastown.dog), got: {pool!r}"
    )


# ---------------------------------------------------------------------------
# Formula TOML contract — vapor shape
# ---------------------------------------------------------------------------


def test_formula_file_exists() -> None:
    assert FORMULA_PATH.is_file(), f"formula file missing: {FORMULA_PATH}"


def test_formula_parses_as_toml() -> None:
    tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))


def test_formula_name_matches_file() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data.get("formula") == "on-merge-brief-record"


def test_formula_is_vapor() -> None:
    """gsp-fqo: formula must be phase=vapor (single shell script, zero extra LLM turns)."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data.get("phase") == "vapor", (
        "formula must declare phase='vapor' (all ops are deterministic bd CLI commands)"
    )


def test_formula_has_single_step() -> None:
    """Vapor formula: all logic collapsed into one step."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = data.get("steps", [])
    assert len(steps) == 1, f"vapor formula must have exactly one step, got {len(steps)}"


def test_formula_step_is_scan_and_record() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = data.get("steps", [])
    assert steps[0]["id"] == "scan-and-record", (
        "vapor step must be 'scan-and-record'"
    )


def test_formula_no_graph_v2_constructs() -> None:
    """Vapor formula must not use graph-v2 constructs (needs, check)."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        assert "needs" not in step, (
            f"vapor formula step {step.get('id')!r} must not use 'needs' (graph-v2 construct)"
        )
        assert "check" not in step, (
            f"vapor formula step {step.get('id')!r} must not use 'check' (graph-v2 construct)"
        )


def test_formula_no_requires_block() -> None:
    """Vapor formula must not declare [requires] formula_compiler (that flips root to blocked container)."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    requires = data.get("requires", {})
    assert "formula_compiler" not in requires, (
        "[requires] formula_compiler must not be set on a vapor formula"
    )


# ---------------------------------------------------------------------------
# Decision-logic contract (verbatim per task-2-brief §2) — content unchanged
# ---------------------------------------------------------------------------


def _step_text(formula_data: dict) -> str:
    """Return the full description text of the single vapor step."""
    steps = formula_data.get("steps", [])
    assert steps, "formula has no steps"
    return steps[0].get("description", "")


def test_label_check_step_checks_needs_decision_label() -> None:
    """check step must check for the needs-decision label."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "needs-decision" in text, (
        "step must reference 'needs-decision' label"
    )


def test_label_check_step_exits_cleanly_on_no_label() -> None:
    """When no needs-decision label: step should exit with no action (§2(c))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "exit 0" in text or "nothing to do" in text, (
        "step must exit cleanly when needs-decision label is absent"
    )


def test_brief_record_step_uses_expected_title_format() -> None:
    """Brief-record bead title must follow `[brief-record] <X-id> <title>` (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "[brief-record]" in text, (
        "step must title the bead with [brief-record] prefix"
    )
    assert "CLOSED_ID" in text or "X-id" in text, (
        "step must reference the source bead id in the title"
    )


def test_brief_record_step_sets_source_bead_metadata() -> None:
    """Brief-record bead must carry metadata linking to source bead X (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "source_bead" in text, (
        "step must set source_bead metadata on the brief-record bead"
    )


def test_brief_prep_step_uses_source_var() -> None:
    """touch-brief-prep section must pass source=<closed-bead-id> (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "source" in text, (
        "brief-prep intake section must pass source var pointing to the closed bead"
    )


def test_brief_prep_step_uses_decision_type() -> None:
    """brief_type must be 'decision' per the brief-prep formula's enum (§2(b))."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "decision" in text, (
        "brief-prep intake must use brief_type='decision'"
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
    """C4: step must list recently closed needs-decision beads."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "bd list" in text
    assert "--status closed" in text
    assert "needs-decision" in text


def test_formula_dedupes_existing_brief_records() -> None:
    """C4: coalescing — skip beads that already have a brief-record."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "[brief-record]" in text, "dedup must key on the brief-record title prefix"


def test_formula_brief_prep_uses_mol_pour() -> None:
    """I4a: primary intake idiom is `bd mol pour`, not `mol sling`."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data)
    assert "bd mol pour" in text
