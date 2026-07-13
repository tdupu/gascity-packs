"""Tests for the math-brief-prep formula (gsp-98d).

Covers the produce-drain + fan-in + shuffle structure:
- formula file exists and parses as TOML
- formula name matches the file
- step structure: select-sources, produce (drain), shuffle
- produce step carries a [steps.drain] block with context=separate and formula=brief-prep
- shuffle step is gated on produce (fan-in dependency)
- shuffle step carries a [steps.check] block referencing brief-shuffle-result-required
- produce drain carries on_item_failure=continue so partial failures do not block shuffle
"""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]


REPO_ROOT = Path(__file__).resolve().parent.parent
FORMULA_PATH = REPO_ROOT / "mathcity" / "formulas" / "math-brief-prep.toml"


def _load() -> dict:
    return tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))


def _steps(data: dict) -> dict[str, dict]:
    return {s["id"]: s for s in data.get("steps", [])}


# ---------------------------------------------------------------------------
# file existence and parse
# ---------------------------------------------------------------------------


def test_formula_file_exists() -> None:
    assert FORMULA_PATH.is_file(), f"formula file missing: {FORMULA_PATH}"


def test_formula_parses_as_toml() -> None:
    _load()


def test_formula_name() -> None:
    data = _load()
    assert data.get("formula") == "math-brief-prep"


def test_formula_has_version() -> None:
    data = _load()
    assert "version" in data


def test_formula_has_requires_block() -> None:
    data = _load()
    assert "requires" in data
    assert "formula_compiler" in data["requires"]


def test_formula_has_catalog_block() -> None:
    data = _load()
    assert "catalog" in data
    assert data["catalog"].get("name") == "math-brief-prep"


# ---------------------------------------------------------------------------
# step presence
# ---------------------------------------------------------------------------


def test_formula_has_select_sources_step() -> None:
    steps = _steps(_load())
    assert "select-sources" in steps, (
        f"formula must have a select-sources step; got: {list(steps)}"
    )


def test_formula_has_produce_step() -> None:
    steps = _steps(_load())
    assert "produce" in steps, (
        f"formula must have a produce step; got: {list(steps)}"
    )


def test_formula_has_shuffle_step() -> None:
    steps = _steps(_load())
    assert "shuffle" in steps, (
        f"formula must have a shuffle step; got: {list(steps)}"
    )


# ---------------------------------------------------------------------------
# produce step: drain configuration
# ---------------------------------------------------------------------------


def test_produce_step_has_drain_block() -> None:
    steps = _steps(_load())
    assert "drain" in steps["produce"], (
        "produce step must carry a [steps.drain] block"
    )


def test_produce_drain_context_is_separate() -> None:
    steps = _steps(_load())
    drain = steps["produce"]["drain"]
    assert drain.get("context") == "separate", (
        f"produce drain must use context=separate for parallel fan-out; got: {drain.get('context')!r}"
    )


def test_produce_drain_formula_is_brief_prep() -> None:
    steps = _steps(_load())
    drain = steps["produce"]["drain"]
    assert drain.get("formula") == "brief-prep", (
        f"produce drain must delegate to brief-prep; got: {drain.get('formula')!r}"
    )


def test_produce_drain_member_access_is_exclusive() -> None:
    steps = _steps(_load())
    drain = steps["produce"]["drain"]
    assert drain.get("member_access") == "exclusive", (
        "produce drain must use member_access=exclusive"
    )


def test_produce_drain_on_item_failure_is_continue() -> None:
    """Partial failures must not block the shuffle of successfully-prepared briefs."""
    steps = _steps(_load())
    drain = steps["produce"]["drain"]
    assert drain.get("on_item_failure") == "continue", (
        "produce drain must set on_item_failure=continue so failures do not block shuffle"
    )


# ---------------------------------------------------------------------------
# step dependencies (fan-in gating)
# ---------------------------------------------------------------------------


def test_produce_needs_select_sources() -> None:
    steps = _steps(_load())
    assert "select-sources" in steps["produce"].get("needs", []), (
        "produce must need select-sources"
    )


def test_shuffle_needs_produce() -> None:
    """The fan-in gate: shuffle starts only after all produce instances settle."""
    steps = _steps(_load())
    assert "produce" in steps["shuffle"].get("needs", []), (
        "shuffle must need produce to enforce the fan-in barrier"
    )


def test_select_sources_has_no_needs() -> None:
    """select-sources is the root step; it must not depend on another step."""
    steps = _steps(_load())
    assert not steps["select-sources"].get("needs"), (
        "select-sources must be the root step with no dependencies"
    )


# ---------------------------------------------------------------------------
# shuffle step: single-writer check
# ---------------------------------------------------------------------------


def test_shuffle_has_check_block() -> None:
    steps = _steps(_load())
    assert "check" in steps["shuffle"], (
        "shuffle step must carry a [steps.check] block"
    )


def test_shuffle_check_references_shuffle_result_script() -> None:
    steps = _steps(_load())
    check_path = steps["shuffle"].get("check", {}).get("check", {}).get("path", "")
    assert "brief-shuffle-result-required" in check_path, (
        f"shuffle check must reference brief-shuffle-result-required; got: {check_path!r}"
    )


def test_shuffle_check_has_max_attempts() -> None:
    steps = _steps(_load())
    assert steps["shuffle"]["check"].get("max_attempts", 0) >= 1, (
        "shuffle check must set max_attempts >= 1"
    )


# ---------------------------------------------------------------------------
# metadata: run targets present on each step
# ---------------------------------------------------------------------------


def test_all_steps_have_run_target() -> None:
    steps = _steps(_load())
    for step_id, step in steps.items():
        meta = step.get("metadata", {})
        assert "gc.run_target" in meta, (
            f"step {step_id!r} must declare gc.run_target in metadata"
        )


# ---------------------------------------------------------------------------
# description contract: produce mentions fan-in and parallel
# ---------------------------------------------------------------------------


def test_produce_description_mentions_parallel() -> None:
    steps = _steps(_load())
    desc = steps["produce"].get("description", "").lower()
    assert "parallel" in desc, (
        "produce step description must mention parallel execution"
    )


def test_produce_description_mentions_fan_in() -> None:
    steps = _steps(_load())
    desc = steps["produce"].get("description", "").lower()
    assert "fan-in" in desc or "fan in" in desc, (
        "produce step description must mention fan-in"
    )


def test_shuffle_description_mentions_single_writer() -> None:
    steps = _steps(_load())
    desc = steps["shuffle"].get("description", "").lower()
    assert "single" in desc and "writer" in desc, (
        "shuffle step description must emphasize single-writer constraint"
    )


def test_shuffle_description_mentions_lock() -> None:
    steps = _steps(_load())
    desc = steps["shuffle"].get("description", "").lower()
    assert "lock" in desc, (
        "shuffle step description must reference the .shuffle.lock"
    )
