"""Tests for mathematics/assets/scripts/escalate.sh (Task 4, gsp-p2a).

Priority branching:
  P0/P1 → bd create + bd label add human + gc mail send + osascript
  P2+   → bd create + bd label add human (bead only, no mail/notification)

Uses PATH shims (fake executables in tmp_path) to intercept all external calls.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "mathematics" / "assets" / "scripts" / "escalate.sh"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_FAKE_BD = """\
#!/bin/sh
# Fake bd: log every invocation to $SHIM_LOG and emit a synthetic bead ID
# on "bd create".
echo "bd $*" >> "${SHIM_LOG:-/dev/stderr}"
if [ "$1" = "create" ]; then
  echo "bd-test-001"
fi
exit 0
"""

_FAKE_GC = """\
#!/bin/sh
echo "gc $*" >> "${SHIM_LOG:-/dev/stderr}"
exit 0
"""

_FAKE_OSASCRIPT = """\
#!/bin/sh
echo "osascript $*" >> "${SHIM_LOG:-/dev/stderr}"
exit 0
"""


def _write_shim(bin_dir: Path, name: str, content: str) -> None:
    p = bin_dir / name
    p.write_text(content)
    p.chmod(0o755)


def _make_shim_env(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Create shim executables and return (log_path, env)."""
    bin_dir = tmp_path / "shim_bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    for name, body in [("bd", _FAKE_BD), ("gc", _FAKE_GC), ("osascript", _FAKE_OSASCRIPT)]:
        _write_shim(bin_dir, name, body)
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "SHIM_LOG": str(log),
        # Ensure HOME is set for any tool that needs it
        "HOME": str(tmp_path),
    }
    return log, env


def _run_escalate(
    args: list[str],
    env: dict[str, str],
    cwd: Path,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(SCRIPT)] + args,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
    )


def _read_log(log: Path) -> str:
    if log.exists():
        return log.read_text()
    return ""


# ---------------------------------------------------------------------------
# sanity: script exists and is executable
# ---------------------------------------------------------------------------


def test_script_exists() -> None:
    assert SCRIPT.is_file(), f"escalate.sh not found: {SCRIPT}"


def test_script_is_executable() -> None:
    assert SCRIPT.stat().st_mode & 0o111, "escalate.sh must be executable"


# ---------------------------------------------------------------------------
# argument validation
# ---------------------------------------------------------------------------


def test_missing_title_fails(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(["--body", "b", "--priority", "2"], env, tmp_path)
    assert result.returncode != 0, "should fail without --title"


def test_missing_priority_fails(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(["--title", "t", "--body", "b"], env, tmp_path)
    assert result.returncode != 0, "should fail without --priority"


def test_invalid_priority_fails(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(["--title", "t", "--body", "b", "--priority", "9"], env, tmp_path)
    assert result.returncode != 0, "priority 9 is out of range 0-4"


# ---------------------------------------------------------------------------
# P0: bead + human label + mail + notification
# ---------------------------------------------------------------------------


def test_p0_creates_bead(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P0 test", "--body", "urgent", "--priority", "0"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "bd create" in calls


def test_p0_flags_bead_as_human(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P0 human", "--body", "urgent", "--priority", "0"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "bd label add" in calls and "human" in calls


def test_p0_sends_mail(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P0 mail", "--body", "body text", "--priority", "0"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "gc mail send" in calls


def test_p0_fires_notification(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P0 notify", "--body", "body text", "--priority", "0"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "osascript" in calls


# ---------------------------------------------------------------------------
# P1: bead + human label + mail + notification
# ---------------------------------------------------------------------------


def test_p1_sends_mail(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P1 test", "--body", "blocked", "--priority", "1"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "gc mail send" in calls


def test_p1_fires_notification(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P1 notify", "--body", "blocked", "--priority", "1"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "osascript" in calls


# ---------------------------------------------------------------------------
# P2: bead + human label only — NO mail, NO notification
# ---------------------------------------------------------------------------


def test_p2_creates_bead(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P2 test", "--body", "waiting", "--priority", "2"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "bd create" in calls


def test_p2_flags_bead_as_human(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P2 human", "--body", "waiting", "--priority", "2"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "bd label add" in calls and "human" in calls


def test_p2_does_not_send_mail(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P2 no mail", "--body", "waiting", "--priority", "2"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "gc mail send" not in calls, f"P2 must not send mail; calls:\n{calls}"


def test_p2_does_not_fire_notification(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P2 no notify", "--body", "waiting", "--priority", "2"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    calls = _read_log(log)
    assert "osascript" not in calls, f"P2 must not fire notification; calls:\n{calls}"


# ---------------------------------------------------------------------------
# P3 and P4: bead only, no ping
# ---------------------------------------------------------------------------


def test_p3_no_mail(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P3", "--body", "low", "--priority", "3"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert "gc mail send" not in _read_log(log)


def test_p4_no_notification(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "P4", "--body", "low", "--priority", "4"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert "osascript" not in _read_log(log)


# ---------------------------------------------------------------------------
# optional --rig flag is accepted
# ---------------------------------------------------------------------------


def test_rig_flag_accepted(tmp_path: Path) -> None:
    log, env = _make_shim_env(tmp_path)
    result = _run_escalate(
        ["--title", "rig test", "--body", "b", "--priority", "2", "--rig", "my-rig"],
        env, tmp_path,
    )
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# template-fragment file
# ---------------------------------------------------------------------------


def test_escalation_protocol_fragment_exists() -> None:
    frag = REPO_ROOT / "mathematics" / "template-fragments" / "escalation-protocol.md"
    assert frag.is_file(), f"fragment missing: {frag}"


def test_escalation_protocol_mentions_script() -> None:
    frag = REPO_ROOT / "mathematics" / "template-fragments" / "escalation-protocol.md"
    text = frag.read_text()
    assert "escalate.sh" in text, "fragment must reference the escalate.sh script"


def test_escalation_protocol_mentions_p0_p1_bar() -> None:
    frag = REPO_ROOT / "mathematics" / "template-fragments" / "escalation-protocol.md"
    text = frag.read_text()
    assert "P0" in text or "P1" in text, "fragment must mention P0/P1 bar"


# ---------------------------------------------------------------------------
# codex-worker wiring
# ---------------------------------------------------------------------------


def test_codex_worker_prompt_references_escalation() -> None:
    prompt = REPO_ROOT / "mathematics" / "agents" / "codex-worker" / "prompt.template.md"
    text = prompt.read_text()
    assert "escalat" in text.lower(), (
        "codex-worker prompt must mention escalation protocol"
    )


# ---------------------------------------------------------------------------
# brief-prep formula wiring
# ---------------------------------------------------------------------------


def test_brief_prep_coordinate_review_mentions_escalation() -> None:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]

    formula_path = REPO_ROOT / "mathematics" / "formulas" / "brief-prep.toml"
    data = tomllib.loads(formula_path.read_text(encoding="utf-8"))
    coord_step = next(
        (s for s in data.get("steps", []) if s["id"] == "coordinate-review"), None
    )
    assert coord_step is not None, "coordinate-review step not found in brief-prep.toml"
    desc = coord_step.get("description", "")
    assert "escalat" in desc.lower(), (
        "coordinate-review step description must mention escalation"
    )
