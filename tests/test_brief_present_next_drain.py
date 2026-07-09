"""Tests for brief-present-next drain-mode (Task 5, gsp-aq9).

Covers:
- The order TOML: trigger=manual, description updated to mention draining all
  pending briefs.
- The formula TOML: step structure, drain-all semantics, no-brainer grouping,
  per-brief presentation records.
- The drain-manifest helper script: reads manifest.jsonl, filters decided/
  archived, sorts by unlock_count, splits into no-brainer and full-brief files.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]


REPO_ROOT = Path(__file__).resolve().parent.parent
MATHEMATICS = REPO_ROOT / "mathcity"
SCRIPTS = MATHEMATICS / "assets" / "scripts"
ORDERS = MATHEMATICS / "orders"
FORMULAS = MATHEMATICS / "formulas"

DRAIN_SCRIPT = SCRIPTS / "brief-drain-manifest.sh"
ORDER_PATH = ORDERS / "brief-present-next.toml"
FORMULA_PATH = FORMULAS / "brief-present-next.toml"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def write_manifest(root: Path, entries: list[dict]) -> Path:
    manifest = root / ".beads" / "briefs" / "stack" / "manifest.jsonl"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8"
    )
    return manifest


def make_entry(
    slug: str,
    gate_profile: str = "standard",
    unlock_count: int = 0,
    status: str = "",
) -> dict:
    entry: dict = {
        "slug": slug,
        "path": f".beads/briefs/stack/{slug}.md",
        "source": f"bead-{slug}",
        "unlock_count": unlock_count,
        "created_at": "2026-07-01T00:00:00Z",
        "gate_profile": gate_profile,
    }
    if status:
        entry["status"] = status
    return entry


def run_drain(root: Path, out_dir: Path | None = None) -> subprocess.CompletedProcess:
    env = {
        "PATH": "/usr/bin:/bin",
        "BRIEF_ROOT": ".beads/briefs",
    }
    if out_dir is not None:
        env["OUT_DIR"] = str(out_dir)
    return subprocess.run(
        [str(DRAIN_SCRIPT)],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )


def read_slugs(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line]


# ---------------------------------------------------------------------------
# drain script: existence and executability
# ---------------------------------------------------------------------------


def test_drain_script_exists() -> None:
    assert DRAIN_SCRIPT.is_file(), f"drain script missing: {DRAIN_SCRIPT}"


def test_drain_script_is_executable() -> None:
    assert DRAIN_SCRIPT.stat().st_mode & 0o111, "drain script must be executable"


# ---------------------------------------------------------------------------
# drain script: empty / missing manifest
# ---------------------------------------------------------------------------


def test_drain_exits_0_with_no_manifest(tmp_path: Path) -> None:
    """No manifest → succeeds with empty output files."""
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr
    assert read_slugs(out / "no-brainer-slugs.txt") == []
    assert read_slugs(out / "full-brief-slugs.txt") == []


def test_drain_creates_output_files_when_manifest_missing(tmp_path: Path) -> None:
    """Output files are always created (possibly empty) even if manifest absent."""
    out = tmp_path / "out"
    out.mkdir()
    run_drain(tmp_path, out_dir=out)
    assert (out / "no-brainer-slugs.txt").exists()
    assert (out / "full-brief-slugs.txt").exists()


def test_drain_empty_manifest(tmp_path: Path) -> None:
    """Empty manifest file → both output files are empty."""
    manifest = tmp_path / ".beads" / "briefs" / "stack" / "manifest.jsonl"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr
    assert read_slugs(out / "no-brainer-slugs.txt") == []
    assert read_slugs(out / "full-brief-slugs.txt") == []


# ---------------------------------------------------------------------------
# drain script: drain order (unlock_count ascending)
# ---------------------------------------------------------------------------


def test_drain_order_by_unlock_count(tmp_path: Path) -> None:
    """Entries are emitted in unlock_count ascending order."""
    write_manifest(tmp_path, [
        make_entry("slug-high", unlock_count=5),
        make_entry("slug-low", unlock_count=1),
        make_entry("slug-mid", unlock_count=3),
    ])
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr
    full_slugs = read_slugs(out / "full-brief-slugs.txt")
    assert full_slugs == ["slug-low", "slug-mid", "slug-high"], (
        f"expected unlock_count order, got {full_slugs}"
    )


def test_drain_zero_unlock_count_comes_first(tmp_path: Path) -> None:
    """Entries with unlock_count=0 come before those with positive counts."""
    write_manifest(tmp_path, [
        make_entry("positive", unlock_count=2),
        make_entry("zero", unlock_count=0),
    ])
    out = tmp_path / "out"
    out.mkdir()
    run_drain(tmp_path, out_dir=out)
    full_slugs = read_slugs(out / "full-brief-slugs.txt")
    assert full_slugs[0] == "zero"
    assert full_slugs[1] == "positive"


# ---------------------------------------------------------------------------
# drain script: no-brainer grouping
# ---------------------------------------------------------------------------


def test_drain_separates_no_brainer_from_full(tmp_path: Path) -> None:
    """no_brainer gate_profile goes to no-brainer-slugs.txt; others to full."""
    write_manifest(tmp_path, [
        make_entry("nb-a", gate_profile="no_brainer", unlock_count=1),
        make_entry("full-b", gate_profile="standard", unlock_count=2),
        make_entry("nb-c", gate_profile="no_brainer", unlock_count=3),
        make_entry("full-d", gate_profile="standard", unlock_count=4),
    ])
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr
    nb_slugs = read_slugs(out / "no-brainer-slugs.txt")
    full_slugs = read_slugs(out / "full-brief-slugs.txt")
    assert nb_slugs == ["nb-a", "nb-c"], f"no-brainer slugs: {nb_slugs}"
    assert full_slugs == ["full-b", "full-d"], f"full brief slugs: {full_slugs}"


def test_drain_all_no_brainers(tmp_path: Path) -> None:
    """All no-brainer entries: full-brief-slugs.txt is empty."""
    write_manifest(tmp_path, [
        make_entry("nb-1", gate_profile="no_brainer"),
        make_entry("nb-2", gate_profile="no_brainer"),
    ])
    out = tmp_path / "out"
    out.mkdir()
    run_drain(tmp_path, out_dir=out)
    assert read_slugs(out / "no-brainer-slugs.txt") == ["nb-1", "nb-2"]
    assert read_slugs(out / "full-brief-slugs.txt") == []


def test_drain_all_full_briefs(tmp_path: Path) -> None:
    """No no-brainer entries: no-brainer-slugs.txt is empty."""
    write_manifest(tmp_path, [
        make_entry("full-1", gate_profile="standard"),
        make_entry("full-2", gate_profile="experiment"),
    ])
    out = tmp_path / "out"
    out.mkdir()
    run_drain(tmp_path, out_dir=out)
    assert read_slugs(out / "no-brainer-slugs.txt") == []
    assert sorted(read_slugs(out / "full-brief-slugs.txt")) == ["full-1", "full-2"]


# ---------------------------------------------------------------------------
# drain script: skip decided / archived entries
# ---------------------------------------------------------------------------


def test_drain_skips_decided_entries(tmp_path: Path) -> None:
    """Entries with status=decided are excluded from drain output."""
    write_manifest(tmp_path, [
        make_entry("pending", unlock_count=1),
        make_entry("done", unlock_count=2, status="decided"),
    ])
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr
    full_slugs = read_slugs(out / "full-brief-slugs.txt")
    assert "done" not in full_slugs
    assert "pending" in full_slugs


def test_drain_skips_archived_entries(tmp_path: Path) -> None:
    """Entries with status=archived are excluded from drain output."""
    write_manifest(tmp_path, [
        make_entry("live", unlock_count=1),
        make_entry("old", unlock_count=2, status="archived"),
    ])
    out = tmp_path / "out"
    out.mkdir()
    run_drain(tmp_path, out_dir=out)
    full_slugs = read_slugs(out / "full-brief-slugs.txt")
    assert "old" not in full_slugs
    assert "live" in full_slugs


def test_drain_all_decided_yields_empty_output(tmp_path: Path) -> None:
    """All entries decided → both output files empty (nothing to drain)."""
    write_manifest(tmp_path, [
        make_entry("a", status="decided"),
        make_entry("b", status="archived"),
    ])
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr
    assert read_slugs(out / "no-brainer-slugs.txt") == []
    assert read_slugs(out / "full-brief-slugs.txt") == []


# ---------------------------------------------------------------------------
# drain script: mixed no-brainer + full in unlock order (the key integration test)
# ---------------------------------------------------------------------------


def test_drain_mixed_manifest_fixture(tmp_path: Path) -> None:
    """
    Fixture with mixed no-brainer + full briefs in non-unlock order,
    including decided entries that must be skipped.

    Expected drain order (ascending unlock_count, decided excluded):
      no-brainer-slugs: [nb-low, nb-high]
      full-brief-slugs: [full-one, full-two]
    """
    entries = [
        make_entry("full-two", gate_profile="standard", unlock_count=4),
        make_entry("nb-high", gate_profile="no_brainer", unlock_count=3),
        make_entry("decided-one", gate_profile="standard", unlock_count=1, status="decided"),
        make_entry("nb-low", gate_profile="no_brainer", unlock_count=1),
        make_entry("full-one", gate_profile="standard", unlock_count=2),
        make_entry("archived-nb", gate_profile="no_brainer", unlock_count=0, status="archived"),
    ]
    write_manifest(tmp_path, entries)
    out = tmp_path / "out"
    out.mkdir()
    result = run_drain(tmp_path, out_dir=out)
    assert result.returncode == 0, result.stderr

    nb_slugs = read_slugs(out / "no-brainer-slugs.txt")
    full_slugs = read_slugs(out / "full-brief-slugs.txt")

    # No decided/archived entries appear
    assert "decided-one" not in nb_slugs + full_slugs
    assert "archived-nb" not in nb_slugs + full_slugs

    # No-brainer slugs sorted by unlock_count
    assert nb_slugs == ["nb-low", "nb-high"], f"no-brainer order wrong: {nb_slugs}"

    # Full brief slugs sorted by unlock_count
    assert full_slugs == ["full-one", "full-two"], f"full order wrong: {full_slugs}"


# ---------------------------------------------------------------------------
# drain script: default OUT_DIR resolves to .drain-run/ under BRIEF_ROOT
# ---------------------------------------------------------------------------


def test_drain_default_out_dir_is_drain_run(tmp_path: Path) -> None:
    """When OUT_DIR is not set, output files land in <BRIEF_ROOT>/.drain-run/."""
    write_manifest(tmp_path, [
        make_entry("pending", gate_profile="standard", unlock_count=1),
    ])
    # Run without passing out_dir so the script uses its default
    env = {
        "PATH": "/usr/bin:/bin",
        "BRIEF_ROOT": ".beads/briefs",
    }
    result = subprocess.run(
        [str(DRAIN_SCRIPT)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    drain_run = tmp_path / ".beads" / "briefs" / ".drain-run"
    assert (drain_run / "no-brainer-slugs.txt").exists(), (
        f".drain-run/no-brainer-slugs.txt not found; OUT_DIR default may be wrong\n{result.stderr}"
    )
    assert (drain_run / "full-brief-slugs.txt").exists(), (
        ".drain-run/full-brief-slugs.txt not found"
    )
    assert read_slugs(drain_run / "full-brief-slugs.txt") == ["pending"]


# ---------------------------------------------------------------------------
# drain script: awk fallback parity (no jq in PATH)
# ---------------------------------------------------------------------------


def _make_no_jq_bin(tmp_path: Path) -> Path:
    """Build a minimal bin dir with the tools brief-drain-manifest.sh needs but NO jq."""
    import os
    fake_bin = tmp_path / "_bin_no_jq"
    fake_bin.mkdir()
    needed = {
        "sh": "/bin/sh",
        "mkdir": "/bin/mkdir",
        "rm": "/bin/rm",
        "touch": "/usr/bin/touch",
        "sort": "/usr/bin/sort",
        "awk": "/usr/bin/awk",
        "mktemp": "/usr/bin/mktemp",
    }
    for name, src in needed.items():
        if os.path.isfile(src):
            (fake_bin / name).symlink_to(src)
        else:
            # Fall back to PATH lookup so the shim works regardless of location.
            import shutil as _shutil
            found = _shutil.which(name)
            if found:
                (fake_bin / name).symlink_to(found)
    return fake_bin


def test_drain_awk_fallback_parity_with_jq(tmp_path: Path) -> None:
    """
    awk fallback (no jq in PATH) must produce the same drain order and grouping
    as the jq-path integration test (test_drain_mixed_manifest_fixture).

    Expected:
      no-brainer-slugs: [nb-low, nb-high]
      full-brief-slugs: [full-one, full-two]
    """
    entries = [
        make_entry("full-two", gate_profile="standard", unlock_count=4),
        make_entry("nb-high", gate_profile="no_brainer", unlock_count=3),
        make_entry("decided-one", gate_profile="standard", unlock_count=1, status="decided"),
        make_entry("nb-low", gate_profile="no_brainer", unlock_count=1),
        make_entry("full-one", gate_profile="standard", unlock_count=2),
        make_entry("archived-nb", gate_profile="no_brainer", unlock_count=0, status="archived"),
    ]
    write_manifest(tmp_path, entries)

    fake_bin = _make_no_jq_bin(tmp_path)
    out = tmp_path / "out"
    out.mkdir()

    result = subprocess.run(
        [str(fake_bin / "sh"), str(DRAIN_SCRIPT)],
        cwd=tmp_path,
        env={
            "PATH": str(fake_bin),
            "BRIEF_ROOT": ".beads/briefs",
            "OUT_DIR": str(out),
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"awk-fallback run failed:\n{result.stderr}"

    nb_slugs = read_slugs(out / "no-brainer-slugs.txt")
    full_slugs = read_slugs(out / "full-brief-slugs.txt")

    # No decided/archived entries appear
    assert "decided-one" not in nb_slugs + full_slugs
    assert "archived-nb" not in nb_slugs + full_slugs

    # Identical to jq-path expected output (parity check)
    assert nb_slugs == ["nb-low", "nb-high"], (
        f"awk fallback no-brainer order differs from jq: {nb_slugs}"
    )
    assert full_slugs == ["full-one", "full-two"], (
        f"awk fallback full-brief order differs from jq: {full_slugs}"
    )


# ---------------------------------------------------------------------------
# order TOML contract
# ---------------------------------------------------------------------------


def test_order_file_exists() -> None:
    assert ORDER_PATH.is_file(), f"order file missing: {ORDER_PATH}"


def test_order_parses_as_toml() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert "order" in data


def test_order_trigger_is_manual() -> None:
    """Accumulate-and-drain UX: trigger must remain manual (HQ decision gt-3x2d)."""
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert data["order"].get("trigger") == "manual", (
        "brief-present-next order must use trigger = \"manual\""
    )


def test_order_description_mentions_drain() -> None:
    """Order description must say it drains all pending briefs."""
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    desc = data["order"].get("description", "").lower()
    assert "drain" in desc or "all pending" in desc, (
        f"order description should mention drain/all pending, got: {desc!r}"
    )


def test_order_formula_matches_formula_file() -> None:
    order_data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    formula_data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert order_data["order"]["formula"] == formula_data["formula"]


# ---------------------------------------------------------------------------
# formula TOML contract
# ---------------------------------------------------------------------------


def test_formula_file_exists() -> None:
    assert FORMULA_PATH.is_file(), f"formula file missing: {FORMULA_PATH}"


def test_formula_parses_as_toml() -> None:
    tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))


def test_formula_name() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    assert data.get("formula") == "brief-present-next"


def test_formula_has_read_manifest_step() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    step_ids = [s["id"] for s in data.get("steps", [])]
    assert "read-manifest" in step_ids, (
        f"formula must have a read-manifest step; got: {step_ids}"
    )


def test_formula_has_consolidate_no_brainers_step() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    step_ids = [s["id"] for s in data.get("steps", [])]
    assert "consolidate-no-brainers" in step_ids, (
        f"formula must have a consolidate-no-brainers step; got: {step_ids}"
    )


def test_formula_has_present_full_briefs_step() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    step_ids = [s["id"] for s in data.get("steps", [])]
    assert "present-full-briefs" in step_ids, (
        f"formula must have a present-full-briefs step; got: {step_ids}"
    )


def test_formula_has_record_presentations_step() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    step_ids = [s["id"] for s in data.get("steps", [])]
    assert "record-presentations" in step_ids, (
        f"formula must have a record-presentations step; got: {step_ids}"
    )


def test_formula_step_dependencies() -> None:
    """consolidate-no-brainers and present-full-briefs both need read-manifest."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in data.get("steps", [])}
    assert "read-manifest" in steps["consolidate-no-brainers"].get("needs", [])
    assert "read-manifest" in steps["present-full-briefs"].get("needs", [])


def test_formula_record_presentations_needs_both_present_steps() -> None:
    """record-presentations must come after both presentation steps."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in data.get("steps", [])}
    needs = steps["record-presentations"].get("needs", [])
    assert "consolidate-no-brainers" in needs and "present-full-briefs" in needs, (
        "record-presentations must need both presentation steps"
    )


def test_formula_consolidate_step_mentions_one_line(tmp_path: Path) -> None:
    """consolidate-no-brainers description must mention one-line item rendering."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        if step["id"] == "consolidate-no-brainers":
            desc = step.get("description", "").lower()
            assert "one-line" in desc or "one line" in desc, (
                "consolidate-no-brainers must describe one-line item rendering"
            )
            return
    pytest.fail("consolidate-no-brainers step not found")


def test_formula_present_full_briefs_mentions_grill_and_present(tmp_path: Path) -> None:
    """present-full-briefs step must mention grill-and-present or present-it."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        if step["id"] == "present-full-briefs":
            desc = step.get("description", "").lower()
            assert "grill-and-present" in desc or "present-it" in desc, (
                "present-full-briefs must reference existing rendering steps"
            )
            return
    pytest.fail("present-full-briefs step not found")


def test_formula_record_presentations_mentions_per_brief_record() -> None:
    """record-presentations must describe per-brief presentation record writing."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        if step["id"] == "record-presentations":
            desc = step.get("description", "").lower()
            assert "per" in desc or "each" in desc or "record" in desc, (
                "record-presentations must describe per-brief record writing"
            )
            return
    pytest.fail("record-presentations step not found")


def test_formula_read_manifest_uses_drain_script() -> None:
    """read-manifest step must reference the brief-drain-manifest script."""
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        if step["id"] == "read-manifest":
            check = step.get("check", {}).get("check", {})
            path = check.get("path", "")
            assert "brief-drain-manifest" in path, (
                f"read-manifest check must reference brief-drain-manifest; got: {path!r}"
            )
            return
    pytest.fail("read-manifest step not found")


def test_formula_read_manifest_check_is_absolute() -> None:
    """C1 (Phase 1): gc rejects relative ../ check paths (path-traversal guard),
    so the read-manifest check must use the absolute repo-source path. This
    replaces the former no-hardcoded-/Users/ assertion, which contradicted the
    gc containment behavior. Replace with a pack-root mechanism in Phase 2.
    """
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    for step in data.get("steps", []):
        if step["id"] == "read-manifest":
            path = step.get("check", {}).get("check", {}).get("path", "")
            assert path.startswith("/"), (
                f"read-manifest check path must be absolute (gc rejects ../); got: {path!r}"
            )
            assert not path.startswith("../"), "check path must not be relative"
            return
    pytest.fail("read-manifest step not found")
