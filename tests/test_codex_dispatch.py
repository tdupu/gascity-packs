"""Tests for the codex-dispatch formula (gsp-fta).

The formula creates a single step bead routed to the codex-worker pool.
It is always poured explicitly — no order fires it automatically.
"""
from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]

PACK_ROOT = Path(__file__).parent.parent / "mathcity"
FORMULA_PATH = PACK_ROOT / "formulas" / "codex-dispatch.toml"
AGENT_PATH = PACK_ROOT / "agents" / "codex-worker" / "agent.toml"


# ---------------------------------------------------------------------------
# Formula structure
# ---------------------------------------------------------------------------


def test_formula_file_exists() -> None:
    assert FORMULA_PATH.is_file(), f"formula file missing: {FORMULA_PATH}"


def test_formula_parses_as_toml() -> None:
    tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))


def test_formula_name_matches_file() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data.get("formula") == "codex-dispatch"


def test_formula_is_not_vapor() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data.get("phase") != "vapor", (
        "codex-dispatch must not be vapor — the codex-worker does LLM reasoning"
    )


def test_formula_has_single_step() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = data.get("steps", [])
    assert len(steps) == 1, f"codex-dispatch must have exactly one step, got {len(steps)}"


def test_formula_step_id_is_codex_task() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data["steps"][0]["id"] == "codex-task"


def test_formula_step_routes_to_codex_worker() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    step = data["steps"][0]
    run_target = step.get("metadata", {}).get("gc.run_target", "")
    assert "codex" in run_target, (
        f"step must route to codex-worker pool, got gc.run_target={run_target!r}"
    )


def test_formula_has_no_graph_v2_constructs() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        assert "needs" not in step, (
            f"step {step.get('id')!r} must not use 'needs' (graph-v2 construct)"
        )
        assert "check" not in step, (
            f"step {step.get('id')!r} must not use 'check' (graph-v2 construct)"
        )


# ---------------------------------------------------------------------------
# Vars contract
# ---------------------------------------------------------------------------


def test_formula_has_required_task_var() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    vars_ = data.get("vars", {})
    assert "task" in vars_, "formula must declare a 'task' var"
    assert vars_["task"].get("required") is True, "'task' var must be required=true"


def test_formula_has_context_var_with_default() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    vars_ = data.get("vars", {})
    assert "context" in vars_, "formula must declare a 'context' var"
    assert "default" in vars_["context"], "'context' var must have a default"


def test_formula_has_codex_target_var() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    vars_ = data.get("vars", {})
    assert "codex_target" in vars_, "formula must declare a 'codex_target' var"
    default = vars_["codex_target"].get("default", "")
    assert "codex" in default, (
        f"codex_target default must reference codex pool, got {default!r}"
    )


# ---------------------------------------------------------------------------
# Step description contract
# ---------------------------------------------------------------------------


def test_step_description_references_task_var() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    desc = data["steps"][0].get("description", "")
    assert "{{task}}" in desc, "step description must interpolate {{task}}"


def test_step_description_includes_drain_ack() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    desc = data["steps"][0].get("description", "")
    assert "drain-ack" in desc, "step must instruct the worker to call drain-ack on completion"


def test_step_description_includes_escalation_path() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    desc = data["steps"][0].get("description", "")
    assert "escalat" in desc.lower(), "step must reference the escalation path for blocked cases"


# ---------------------------------------------------------------------------
# Explicit-pour discipline
# ---------------------------------------------------------------------------


def test_no_order_fires_codex_dispatch() -> None:
    """codex-dispatch must not be referenced by any order (explicit pour only)."""
    orders_dir = PACK_ROOT / "orders"
    for order_file in orders_dir.glob("*.toml"):
        text = order_file.read_text(encoding="utf-8")
        assert "codex-dispatch" not in text, (
            f"order {order_file.name} references codex-dispatch — "
            "this formula must be pour-only, never fired by an order"
        )


# ---------------------------------------------------------------------------
# Agent exists
# ---------------------------------------------------------------------------


def test_codex_worker_agent_exists() -> None:
    assert AGENT_PATH.is_file(), f"codex-worker agent.toml missing: {AGENT_PATH}"


def test_codex_worker_agent_uses_codex_provider() -> None:
    data = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
    assert data.get("provider") == "codex", (
        "codex-worker agent must declare provider='codex'"
    )
