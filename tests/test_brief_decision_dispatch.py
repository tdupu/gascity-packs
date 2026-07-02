"""Tests for brief-decision-dispatch formula and order (Task 3, gsp-ijf).

Covers:
- The order TOML: parses, event trigger on brief.decided, city scope, polecat pool.
- The formula TOML: parses, step structure, routing descriptions.
- The dispatch check script (brief-decision-dispatched-check.sh): idempotency
  guard, ledger presence, vacuous pass when no pending slugs.
- Idempotency: dispatching the same decision slug twice is a no-op (ledger check).
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
MATHEMATICS = REPO_ROOT / "mathematics"
CHECKS = MATHEMATICS / "assets" / "scripts" / "checks"
ORDERS = MATHEMATICS / "orders"
FORMULAS = MATHEMATICS / "formulas"

DISPATCH_CHECK = CHECKS / "brief-decision-dispatched-check.sh"
ORDER_PATH = ORDERS / "brief-decision-dispatch.toml"
FORMULA_PATH = FORMULAS / "brief-decision-dispatch.toml"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def run_dispatch_check(
    root: Path,
    pending_slugs: str = "",
) -> subprocess.CompletedProcess:
    env: dict[str, str] = {
        "PATH": "/usr/bin:/bin",
        "BRIEF_ROOT": ".beads/briefs",
    }
    if pending_slugs:
        env["PENDING_SLUGS"] = pending_slugs
    return subprocess.run(
        [str(DISPATCH_CHECK)],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )


def write_ledger(root: Path, entries: list[dict]) -> Path:
    ledger = root / ".beads" / "briefs" / "decisions-dispatched.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        "".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8"
    )
    return ledger


def make_ledger_entry(slug: str, decision: str = "approve") -> dict:
    return {
        "brief_slug": slug,
        "decision": decision,
        "source_bead": "",
        "action": f"test dispatch of {slug}",
        "follow_up_bead": "",
        "dispatched_at": "2026-07-01T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# order TOML contract
# ---------------------------------------------------------------------------


def test_order_file_exists() -> None:
    assert ORDER_PATH.is_file(), f"order file missing: {ORDER_PATH}"


def test_order_parses_as_toml() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert "order" in data


def test_order_trigger_is_event() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert data["order"].get("trigger") == "event", (
        "brief-decision-dispatch order must use trigger = \"event\""
    )


def test_order_on_brief_decided() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert data["order"].get("on") == "brief.decided", (
        "order must fire on 'brief.decided' events"
    )


def test_order_scope_is_city() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert data["order"].get("scope") == "city"


def test_order_pool_is_polecat() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert data["order"].get("pool") == "polecat"


def test_order_idempotent_flag() -> None:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    assert data["order"].get("idempotent") is True


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
    assert data.get("formula") == "brief-decision-dispatch"


def test_formula_has_required_steps() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    step_ids = [s["id"] for s in data.get("steps", [])]
    assert "scan-undispatched" in step_ids
    assert "dispatch-decisions" in step_ids


def test_formula_step_dependency_chain() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in data.get("steps", [])}
    assert "scan-undispatched" in steps["dispatch-decisions"].get("needs", [])


def test_formula_dispatch_step_has_check() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in data.get("steps", [])}
    dispatch = steps["dispatch-decisions"]
    assert "check" in dispatch, "dispatch-decisions must have a step check"
    check = dispatch["check"]["check"]
    assert check.get("mode") == "exec"
    assert "brief-decision-dispatched-check" in check.get("path", "")


def _step_text(formula_data: dict, step_id: str) -> str:
    for step in formula_data.get("steps", []):
        if step["id"] == step_id:
            return step.get("description", "")
    raise KeyError(f"step {step_id!r} not found")


def test_formula_approve_reassigns_to_refinery() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "dispatch-decisions")
    assert "refinery" in text, "dispatch step must mention refinery for approve path"
    assert "target" in text, "dispatch step must set target metadata"
    assert "branch" in text, "dispatch step must set branch metadata"


def test_formula_reject_creates_followup() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "dispatch-decisions")
    assert "reject" in text
    assert "[rejected]" in text or "rejected" in text


def test_formula_revise_creates_followup() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "dispatch-decisions")
    assert "revise" in text
    assert "[revise]" in text or "revise" in text


def test_formula_defer_is_noop() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "dispatch-decisions")
    assert "defer" in text


def test_formula_ledger_is_append_only() -> None:
    data = tomllib.loads(FORMULA_PATH.read_text(encoding="utf-8"))
    text = _step_text(data, "dispatch-decisions")
    assert "append" in text.lower() or ">>" in text, (
        "dispatch step must append to ledger, never rewrite"
    )


# ---------------------------------------------------------------------------
# check script: brief-decision-dispatched-check.sh
# ---------------------------------------------------------------------------


def test_check_script_exists() -> None:
    assert DISPATCH_CHECK.is_file(), f"check script missing: {DISPATCH_CHECK}"


def test_check_script_is_executable() -> None:
    assert DISPATCH_CHECK.stat().st_mode & 0o111, "check script must be executable"


def test_check_passes_vacuously_with_no_pending(tmp_path: Path) -> None:
    """No PENDING_SLUGS set → vacuous pass (nothing to verify)."""
    result = run_dispatch_check(tmp_path)
    assert result.returncode == 0, result.stderr


def test_check_passes_vacuously_with_empty_pending(tmp_path: Path) -> None:
    """PENDING_SLUGS is whitespace only → vacuous pass."""
    result = run_dispatch_check(tmp_path, pending_slugs="   ")
    assert result.returncode == 0, result.stderr


def test_check_fails_when_ledger_missing(tmp_path: Path) -> None:
    """Ledger does not exist yet → check fails (dispatch not yet written)."""
    result = run_dispatch_check(tmp_path, pending_slugs="my-slug")
    assert result.returncode != 0, "check must fail when ledger is absent"
    assert "dispatch ledger" in result.stderr


def test_check_fails_when_slug_not_in_ledger(tmp_path: Path) -> None:
    """Ledger exists but pending slug absent → retry."""
    write_ledger(tmp_path, [make_ledger_entry("other-slug")])
    result = run_dispatch_check(tmp_path, pending_slugs="my-slug")
    assert result.returncode != 0
    assert "my-slug" in result.stderr


def test_check_passes_when_slug_in_ledger(tmp_path: Path) -> None:
    """Pending slug present in ledger → check passes."""
    write_ledger(tmp_path, [make_ledger_entry("my-slug")])
    result = run_dispatch_check(tmp_path, pending_slugs="my-slug")
    assert result.returncode == 0, result.stderr


def test_check_passes_for_multiple_slugs(tmp_path: Path) -> None:
    """Multiple pending slugs all present → check passes."""
    write_ledger(
        tmp_path,
        [make_ledger_entry("slug-a"), make_ledger_entry("slug-b")],
    )
    result = run_dispatch_check(tmp_path, pending_slugs="slug-a slug-b")
    assert result.returncode == 0, result.stderr


def test_check_fails_when_only_some_slugs_present(tmp_path: Path) -> None:
    """Only one of two slugs in ledger → fail."""
    write_ledger(tmp_path, [make_ledger_entry("slug-a")])
    result = run_dispatch_check(tmp_path, pending_slugs="slug-a slug-b")
    assert result.returncode != 0
    assert "slug-b" in result.stderr


# ---------------------------------------------------------------------------
# idempotency: dispatching the same slug twice is a no-op
# ---------------------------------------------------------------------------


def test_idempotency_check_passes_if_slug_already_in_ledger(tmp_path: Path) -> None:
    """
    Core idempotency requirement (task-3-brief §3): if the ledger already
    contains the slug, the check script returns success, which means the
    dispatch step would not need to re-run.

    In real operation the scan-undispatched step pre-filters known slugs
    before calling dispatch-decisions, so this tests the re-entry guard path
    (dispatch step called a second time for the same slug).
    """
    slug = "approved-bead-slug"
    write_ledger(tmp_path, [make_ledger_entry(slug)])
    # First call: slug is in ledger → passes.
    r1 = run_dispatch_check(tmp_path, pending_slugs=slug)
    assert r1.returncode == 0, f"first check failed: {r1.stderr}"
    # Second call: ledger unchanged; still passes (idempotent).
    r2 = run_dispatch_check(tmp_path, pending_slugs=slug)
    assert r2.returncode == 0, f"second check failed: {r2.stderr}"


def test_idempotency_ledger_not_duplicated(tmp_path: Path) -> None:
    """
    Simulates what happens if the scan-undispatched step skips an
    already-dispatched slug: the ledger must not grow.
    """
    slug = "my-bead"
    entry = make_ledger_entry(slug)
    ledger = write_ledger(tmp_path, [entry])
    initial_lines = len(ledger.read_text(encoding="utf-8").splitlines())
    # Running the check (equivalent to the idempotency guard) does NOT append.
    run_dispatch_check(tmp_path, pending_slugs=slug)
    final_lines = len(ledger.read_text(encoding="utf-8").splitlines())
    assert final_lines == initial_lines, (
        "idempotency guard must not append to ledger on a second check"
    )


def test_scan_skips_already_dispatched_slugs(tmp_path: Path) -> None:
    """
    The scan-undispatched step filters known slugs by checking the ledger.
    Simulate this: if the slug is in the ledger, pending_slugs is empty
    after scan, and the check must pass vacuously.
    """
    slug = "pre-dispatched-slug"
    write_ledger(tmp_path, [make_ledger_entry(slug)])
    # After scan, the slug would be excluded → pending_slugs is empty.
    result = run_dispatch_check(tmp_path, pending_slugs="")
    assert result.returncode == 0, (
        "vacuous pass when pending_slugs is empty after scan"
    )


# ---------------------------------------------------------------------------
# no expand+check combination (methodology-pack constraint)
# ---------------------------------------------------------------------------


def test_dispatch_steps_do_not_combine_expand_and_check() -> None:
    import re

    text = FORMULA_PATH.read_text(encoding="utf-8")
    for block in re.split(r"(?m)^\[\[steps\]\]\s*$", text)[1:]:
        has_expand = re.search(r"(?m)^expand\s*=", block)
        has_check = re.search(r"(?m)^\[steps\.check\]\s*$", block)
        assert not (has_expand and has_check), (
            "brief-decision-dispatch.toml: a step must not combine expand and check"
        )
