"""File-or-sendback post-decision gate (gsp-xhc).

Covers the three pieces the gate is made of:

- the audit-log check (`brief-check.sh file-or-sendback-log`) accepting
  valid FILE / SEND-BACK entries and rejecting malformed ones,
- the stack-low combo check (`brief-stack-low-check.sh`) against low and
  healthy stack fixtures,
- the shape of the new event orders and formulas (event types, pools,
  and the emit hook in brief-record-decision).

Fixtures under tests/fixtures/file-or-sendback/ show the two routing
outcomes on sample decisions: decision-with-successor.toml carries a
lean-investigation emission and routes FILE; decision-self-contained.toml
has no emission and routes SEND-BACK under the inline fallback rules.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKS = REPO_ROOT / "mathematics" / "assets" / "scripts" / "checks"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "file-or-sendback"
ORDERS = REPO_ROOT / "mathematics" / "orders"
FORMULAS = REPO_ROOT / "mathematics" / "formulas"

FILE_ENTRY, SENDBACK_ENTRY = [
    json.loads(line)
    for line in (FIXTURES / "expected-log.jsonl").read_text(encoding="utf-8").splitlines()
    if line
]


def run_log_check(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(CHECKS / "brief-file-or-sendback-log-required.sh")],
        cwd=root,
        env={"PATH": "/usr/bin:/bin", "BRIEF_ROOT": ".beads/briefs"},
        capture_output=True,
        text=True,
    )


def write_log(root: Path, entries: list[dict]) -> Path:
    log = root / ".beads" / "briefs" / "decisions" / "file-or-sendback.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    return log


def run_stack_check(root: Path, threshold: str | None = None) -> subprocess.CompletedProcess:
    env = {"PATH": "/usr/bin:/bin", "BRIEF_ROOT": ".beads/briefs"}
    if threshold is not None:
        env["STACK_LOW_THRESHOLD"] = threshold
    return subprocess.run(
        [str(CHECKS / "brief-stack-low-check.sh")],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------- audit log


def test_log_check_accepts_file_and_sendback_entries(tmp_path) -> None:
    write_log(tmp_path, [FILE_ENTRY, SENDBACK_ENTRY])
    result = run_log_check(tmp_path)
    assert result.returncode == 0, result.stderr


def test_log_check_fails_without_log_file(tmp_path) -> None:
    (tmp_path / ".beads" / "briefs" / "decisions").mkdir(parents=True)
    result = run_log_check(tmp_path)
    assert result.returncode != 0
    assert "missing file" in result.stderr


def test_log_check_fails_on_invalid_jsonl(tmp_path) -> None:
    log = write_log(tmp_path, [FILE_ENTRY])
    log.write_text(log.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
    result = run_log_check(tmp_path)
    assert result.returncode != 0
    assert "invalid JSONL" in result.stderr


def test_log_check_fails_on_unknown_choice(tmp_path) -> None:
    bad = dict(SENDBACK_ENTRY, choice="MAYBE")
    write_log(tmp_path, [bad])
    result = run_log_check(tmp_path)
    assert result.returncode != 0
    assert "required keys or invalid choice" in result.stderr


def test_log_check_fails_on_file_without_target(tmp_path) -> None:
    bad = {k: v for k, v in FILE_ENTRY.items() if k != "target_bead_id"}
    write_log(tmp_path, [bad])
    result = run_log_check(tmp_path)
    assert result.returncode != 0


@pytest.mark.parametrize(
    "missing", ["brief_slug", "decision", "reason", "timestamp", "agent_id"]
)
def test_log_check_fails_on_missing_required_key(tmp_path, missing) -> None:
    bad = {k: v for k, v in SENDBACK_ENTRY.items() if k != missing}
    write_log(tmp_path, [bad])
    result = run_log_check(tmp_path)
    assert result.returncode != 0


# ------------------------------------------------------------- stack check


def stack_fixture(tmp_path: Path, name: str) -> Path:
    root = tmp_path / name
    shutil.copytree(FIXTURES / name, root)
    return root


def test_stack_check_fires_on_low_stack(tmp_path) -> None:
    result = run_stack_check(stack_fixture(tmp_path, "stack-low"))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "approved": 1,
        "total": 1,
        "unlock_pos": 1,
        "threshold": 1,
        "low": True,
    }


def test_stack_check_quiet_on_healthy_stack(tmp_path) -> None:
    result = run_stack_check(stack_fixture(tmp_path, "stack-healthy"))
    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "approved": 3,
        "total": 3,
        "unlock_pos": 3,
        "threshold": 1,
        "low": False,
    }


def test_stack_check_fires_on_empty_stack(tmp_path) -> None:
    result = run_stack_check(tmp_path)
    assert result.returncode == 0
    assert json.loads(result.stdout)["total"] == 0


def test_stack_check_threshold_env_override(tmp_path) -> None:
    result = run_stack_check(stack_fixture(tmp_path, "stack-healthy"), threshold="3")
    assert result.returncode == 0
    assert json.loads(result.stdout)["threshold"] == 3


# ------------------------------------------------------ fixtures round-trip


def test_fixture_decisions_match_expected_routing() -> None:
    with (FIXTURES / "decision-with-successor.toml").open("rb") as fh:
        with_successor = tomllib.load(fh)
    with (FIXTURES / "decision-self-contained.toml").open("rb") as fh:
        self_contained = tomllib.load(fh)

    # The emission on the successor fixture routes FILE at its target.
    assert with_successor["route_choice"] == "FILE"
    assert FILE_ENTRY["choice"] == "FILE"
    assert FILE_ENTRY["target_bead_id"] == with_successor["route_target_bead"]
    assert FILE_ENTRY["brief_slug"] == with_successor["brief_slug"]
    assert FILE_ENTRY["source"] == "lean-investigation"

    # No emission on the self-contained fixture: inline fallback SEND-BACK.
    assert "route_choice" not in self_contained
    assert SENDBACK_ENTRY["choice"] == "SEND-BACK"
    assert SENDBACK_ENTRY["brief_slug"] == self_contained["brief_slug"]
    assert SENDBACK_ENTRY["source"] == "inline-fallback"


# ------------------------------------------------------- orders and formulas


def load_order(name: str) -> dict:
    with (ORDERS / name).open("rb") as fh:
        return tomllib.load(fh)["order"]


def test_post_decision_order_catches_brief_decided() -> None:
    order = load_order("post-decision-file-or-sendback.toml")
    assert order["trigger"] == "event"
    assert order["on"] == "brief.decided"
    assert order["formula"] == "file-or-sendback-route"
    assert order["pool"] == "polecat"
    assert order["scope"] == "city"


def test_archive_on_request_order_catches_archive_requested() -> None:
    order = load_order("brief-archive-on-request.toml")
    assert order["trigger"] == "event"
    assert order["on"] == "brief.archive_requested"
    assert order["formula"] == "brief-archive-sweep"
    assert order["pool"] == "dog"
    assert order["scope"] == "city"


def test_route_formula_parses_and_gates_on_the_log() -> None:
    with (FORMULAS / "file-or-sendback-route.toml").open("rb") as fh:
        formula = tomllib.load(fh)
    assert formula["formula"] == "file-or-sendback-route"
    steps = {step["id"]: step for step in formula["steps"]}
    assert set(steps) == {
        "scan-pending",
        "resolve-and-log",
        "route-downstream",
        "stack-check",
    }
    check = steps["resolve-and-log"]["check"]["check"]
    assert check["path"].endswith("brief-file-or-sendback-log-required.sh")
    # The bells the route formula rings.
    assert "brief.archive_requested" in steps["route-downstream"]["description"]
    assert "brief.stack_low" in steps["stack-check"]["description"]


def test_record_decision_formula_rings_the_bell() -> None:
    with (FORMULAS / "brief-record-decision.toml").open("rb") as fh:
        formula = tomllib.load(fh)
    steps = {step["id"]: step for step in formula["steps"]}
    emit = steps["emit-decided-event"]
    assert emit["needs"] == ["write-decision"]
    assert "gc event emit brief.decided" in emit["description"]


def test_gate_steps_do_not_combine_expand_and_check() -> None:
    # Mirrors the methodology-pack constraint for the files this change owns.
    for name in ("file-or-sendback-route.toml", "brief-record-decision.toml"):
        text = (FORMULAS / name).read_text(encoding="utf-8")
        for block in re.split(r"(?m)^\[\[steps\]\]\s*$", text)[1:]:
            has_expand = re.search(r"(?m)^expand\s*=", block)
            has_check = re.search(r"(?m)^\[steps\.check\]\s*$", block)
            assert not (has_expand and has_check), name
