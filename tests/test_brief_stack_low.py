"""Tests for mathcity/assets/scripts/brief-stack-low.sh (gsp-i9j).

Covers the 9 fixture test cases from the review README:
- low/healthy outcomes
- empty directory (no .md files)
- missing dirs (BRIEF_STACK_DIRS points nowhere)
- multi-dir summing
- threshold override via BRIEF_STACK_LOW_THRESHOLD
- usage error on invalid argument
- --emit suppressed on healthy stack
- order TOML existence and correctness
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "mathcity" / "assets" / "scripts" / "brief-stack-low.sh"
ORDER_PATH = REPO_ROOT / "mathcity" / "orders" / "brief-watchdog-refill-on-stack-low.toml"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def write_briefs(directory: Path, briefs: list[dict]) -> None:
    """Write brief .md files to a directory.

    Each brief dict can have:
      name: filename stem (default auto-indexed)
      status: if present, written as 'status: <value>' in frontmatter
      unlock_count: if > 0, written as 'unlock_count: <value>' in frontmatter
    """
    directory.mkdir(parents=True, exist_ok=True)
    for i, b in enumerate(briefs):
        name = b.get("name", f"brief-{i:02d}")
        lines = ["---"]
        if "status" in b:
            lines.append(f"status: {b['status']}")
        if b.get("unlock_count", 0) > 0:
            lines.append(f"unlock_count: {b['unlock_count']}")
        lines += ["---", ""]
        (directory / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")


def run_script(
    dirs: list[Path],
    *args: str,
    threshold: str | None = None,
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["BRIEF_STACK_DIRS"] = " ".join(str(d) for d in dirs)
    if threshold is not None:
        env["BRIEF_STACK_LOW_THRESHOLD"] = threshold
    return subprocess.run(
        [str(SCRIPT), *args],
        env=env,
        capture_output=True,
        text=True,
    )


def parse_output(result: subprocess.CompletedProcess) -> dict:
    return json.loads(result.stdout.strip())


# ---------------------------------------------------------------------------
# script existence
# ---------------------------------------------------------------------------


def test_script_exists() -> None:
    assert SCRIPT.exists(), f"brief-stack-low.sh not found at {SCRIPT}"
    assert os.access(SCRIPT, os.X_OK), "brief-stack-low.sh is not executable"


# ---------------------------------------------------------------------------
# low / healthy outcomes
# ---------------------------------------------------------------------------


def test_low_when_approved_at_threshold(tmp_path: Path) -> None:
    """approved=1 (at threshold=1) → LOW (exit 0)."""
    write_briefs(tmp_path, [{"status": "approved"}])
    result = run_script([tmp_path], threshold="1")
    assert result.returncode == 0
    data = parse_output(result)
    assert data["low"] is True
    assert data["approved"] == 1


def test_healthy_when_all_above_threshold(tmp_path: Path) -> None:
    """All signals > 1 → healthy (exit 1)."""
    write_briefs(
        tmp_path,
        [
            {"status": "approved"},
            {"status": "approved"},
            {"unlock_count": 1},
            {"unlock_count": 2},
        ],
    )
    result = run_script([tmp_path], threshold="1")
    assert result.returncode == 1
    data = parse_output(result)
    assert data["low"] is False
    assert data["approved"] == 2
    assert data["total"] == 4
    assert data["unlock_pos"] == 2


def test_low_when_total_at_threshold(tmp_path: Path) -> None:
    """total=1 (at threshold=1) → LOW regardless of other signals."""
    write_briefs(tmp_path, [{"unlock_count": 5}])
    result = run_script([tmp_path], threshold="1")
    assert result.returncode == 0
    data = parse_output(result)
    assert data["low"] is True
    assert data["total"] == 1


# ---------------------------------------------------------------------------
# empty / missing dirs
# ---------------------------------------------------------------------------


def test_empty_directory(tmp_path: Path) -> None:
    """Directory exists but has no .md files → all signals = 0, low."""
    result = run_script([tmp_path], threshold="1")
    assert result.returncode == 0
    data = parse_output(result)
    assert data["approved"] == 0
    assert data["total"] == 0
    assert data["unlock_pos"] == 0
    assert data["low"] is True


def test_missing_directory(tmp_path: Path) -> None:
    """BRIEF_STACK_DIRS points to non-existent dir → treated as empty → low."""
    missing = tmp_path / "nonexistent"
    result = run_script([missing], threshold="1")
    assert result.returncode == 0
    data = parse_output(result)
    assert data["total"] == 0
    assert data["low"] is True


# ---------------------------------------------------------------------------
# multi-dir summing
# ---------------------------------------------------------------------------


def test_multi_dir_summing(tmp_path: Path) -> None:
    """Counts are summed across multiple directories (all signals > threshold)."""
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    write_briefs(dir_a, [{"status": "approved"}, {"status": "approved"}, {"unlock_count": 1}])
    write_briefs(dir_b, [{"status": "approved"}, {"unlock_count": 2}])
    result = run_script([dir_a, dir_b], threshold="1")
    assert result.returncode == 1
    data = parse_output(result)
    assert data["approved"] == 3
    assert data["total"] == 5
    assert data["unlock_pos"] == 2
    assert data["low"] is False


# ---------------------------------------------------------------------------
# threshold override
# ---------------------------------------------------------------------------


def test_threshold_override_via_env(tmp_path: Path) -> None:
    """BRIEF_STACK_LOW_THRESHOLD overrides the default."""
    write_briefs(
        tmp_path,
        [
            {"status": "approved"},
            {"status": "approved"},
            {"unlock_count": 1},
        ],
    )
    # threshold=3: total=3 <= 3 → LOW
    result = run_script([tmp_path], threshold="3")
    assert result.returncode == 0
    data = parse_output(result)
    assert data["threshold"] == 3
    assert data["low"] is True


# ---------------------------------------------------------------------------
# usage error
# ---------------------------------------------------------------------------


def test_usage_error_on_invalid_arg(tmp_path: Path) -> None:
    """Unknown argument → exit 2 and usage message on stderr."""
    result = run_script([tmp_path], "--invalid")
    assert result.returncode == 2
    assert "usage" in result.stderr.lower()


# ---------------------------------------------------------------------------
# --emit suppressed on healthy
# ---------------------------------------------------------------------------


def test_emit_suppressed_on_healthy(tmp_path: Path) -> None:
    """--emit with a healthy stack does not fail and stack stays healthy."""
    write_briefs(
        tmp_path,
        [
            {"status": "approved"},
            {"status": "approved"},
            {"unlock_count": 1},
            {"unlock_count": 2},
        ],
    )
    result = run_script([tmp_path], "--emit", threshold="1")
    assert result.returncode == 1
    data = parse_output(result)
    assert data["low"] is False


# ---------------------------------------------------------------------------
# order TOML
# ---------------------------------------------------------------------------


def test_order_file_exists() -> None:
    assert ORDER_PATH.exists(), f"order not found at {ORDER_PATH}"


def test_order_parses_as_toml() -> None:
    with ORDER_PATH.open("rb") as f:
        data = tomllib.load(f)
    assert "order" in data


def test_order_trigger_is_event() -> None:
    with ORDER_PATH.open("rb") as f:
        data = tomllib.load(f)
    assert data["order"]["trigger"] == "event"


def test_order_event_name() -> None:
    with ORDER_PATH.open("rb") as f:
        data = tomllib.load(f)
    assert data["order"]["on"] == "brief.stack-low"


def test_order_formula_is_watchdog_refill() -> None:
    with ORDER_PATH.open("rb") as f:
        data = tomllib.load(f)
    assert data["order"]["formula"] == "brief-watchdog-refill"


def test_order_is_idempotent() -> None:
    with ORDER_PATH.open("rb") as f:
        data = tomllib.load(f)
    assert data["order"].get("idempotent") is True
