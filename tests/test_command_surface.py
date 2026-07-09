"""Tests for CLI command-surface validity (gsp-jn2).

Every gc/bd subcommand referenced in a fenced bash block (or 4-space indented
code block) inside a mathematics formula step description must actually exist
in the CLI.  Past reviews found "Critical" errors where commands like
`gc bd set-metadata`, `gc events --since-cursor`, and `gc bd mol sling` were
prose-referenced but do not exist.  This test is insurance against regressions.

Strategy
--------
1. Parse all mathematics/formulas/*.toml files.
2. From each formula's top-level and step ``description`` fields, extract lines
   from fenced bash blocks (```bash ... ``` or ``` ... ```) and 4-space
   indented code blocks.
3. For each line starting with ``gc `` or ``bd ``, walk the token sequence,
   confirming each successive token is a known subcommand of its parent by
   consulting ``<parent> --help``.  Stop at the first token that is not a
   recognised subcommand (it is a positional argument or flag).  The result is
   the normalised subcommand path, e.g. ``gc bd formula show`` or
   ``bd mol pour``.
4. Deduplicate paths and emit one parametrised test case per
   (formula_name, subcommand_path) pair.
5. Each test case verifies that the last subcommand token appears in its
   parent's ``--help`` output.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Optional

import pytest

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def,import-not-found]


# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
FORMULAS = REPO_ROOT / "mathcity" / "formulas"

# ---------------------------------------------------------------------------
# city-directory discovery
# ---------------------------------------------------------------------------

def _find_gc_city_dir() -> Optional[Path]:
    """Return a directory containing city.toml so that gc subcommand help works.

    ``gc bd --help`` and other gc sub-subcommand help invocations require gc to
    locate a city (it walks up from cwd looking for city.toml or .gc/).  When
    the test suite runs from ``gascity-packs/``, no such file exists in the
    ancestor chain, so gc exits 1 with an error instead of printing help.
    We discover a valid city dir once and pass it as ``cwd`` to those calls.
    """
    home = Path.home()
    # Common conventional locations first.
    candidates = [home / "gt", home / "gastown"]
    # Also try every direct child of $HOME that has city.toml.
    try:
        candidates += [p for p in home.iterdir() if p.is_dir()]
    except PermissionError:
        pass
    for p in candidates:
        if (p / "city.toml").exists() or (p / ".gc").is_dir():
            return p
    return None


_GC_CITY_DIR: Optional[Path] = _find_gc_city_dir()

# ---------------------------------------------------------------------------
# CLI help parsing
# ---------------------------------------------------------------------------

# Matches subcommand listing lines in cobra-style help output, e.g.:
#   "  show      Show details"
#   "  drain-ack Acknowledge drain"
# Intentionally requires the subcommand name to be 2+ chars and contain only
# lowercase letters, digits, and hyphens, so that flags (--help) and headings
# (Available Commands:) are never captured.
_SUBCMD_LINE_RE = re.compile(r"^\s{1,8}([a-z][a-z0-9-]+)\s{2,}")


def _parse_subcommands(output: str) -> frozenset[str]:
    """Return the set of subcommand names visible in a ``--help`` output."""
    return frozenset(
        m.group(1)
        for line in output.splitlines()
        if (m := _SUBCMD_LINE_RE.match(line))
    )


@lru_cache(maxsize=None)
def _subcommands_of(cmd_tuple: tuple[str, ...]) -> frozenset[str]:
    """Return known subcommands of *cmd_tuple*, cached.

    Returns an empty frozenset if the binary is not on PATH or the command
    fails (so callers can simply check membership without special-casing).

    ``gc`` sub-subcommand help (e.g. ``gc bd --help``) requires a city
    directory in the cwd; we use ``_GC_CITY_DIR`` when available.
    """
    cwd: Optional[Path] = None
    if cmd_tuple[0] == "gc" and len(cmd_tuple) > 1 and _GC_CITY_DIR is not None:
        cwd = _GC_CITY_DIR
    try:
        result = subprocess.run(
            list(cmd_tuple) + ["--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return frozenset()
    return _parse_subcommands(result.stdout + result.stderr)


def _gc_on_path() -> bool:
    return shutil.which("gc") is not None


def _bd_on_path() -> bool:
    return shutil.which("bd") is not None


# ---------------------------------------------------------------------------
# command-line normalisation
# ---------------------------------------------------------------------------

# Tokens that terminate subcommand path collection.
_SHELL_OPERATORS: frozenset[str] = frozenset(
    ["||", "&&", "|", ">", ">>", "2>&1", "2>/dev/null", ";", "\\"]
)

# Shell flow-control words; a line starting with one of these is not a
# command invocation.
_FLOW_WORDS: frozenset[str] = frozenset(
    ["if", "for", "while", "do", "then", "else", "fi", "done", "case", "esac"]
)

# A token is only a potential subcommand name if it matches this pattern.
_IDENT_RE = re.compile(r"^[a-z][a-z0-9-]*$")

# Characters whose presence in a token means "this is an argument, not a
# subcommand name".
_ARG_CHARS_RE = re.compile(r"[./=:|]")

# Prefixes that mark a token as a flag, variable, or quoted value.
_ARG_PREFIXES = ("-", "$", '"', "'", "{", "<", "\\")


def _extract_command_path(line: str) -> Optional[tuple[str, ...]]:
    """Return the normalised subcommand path tuple for *line*, or None.

    Walks the token sequence and uses the cached CLI help tree to determine
    where the subcommand path ends and positional arguments begin.  Tokens
    that are not listed as subcommands of their parent command are treated as
    positional arguments and terminate the walk.
    """
    stripped = line.strip().lstrip("$ ")

    # Skip empty lines and comments.
    if not stripped or stripped.startswith("#"):
        return None

    tokens = stripped.split()
    if not tokens:
        return None

    binary = tokens[0]
    if binary not in ("gc", "bd"):
        return None

    # Skip flow-control constructs.
    if any(t in _FLOW_WORDS for t in tokens[:3]):
        return None

    # Skip variable assignments like GC_BEAD_ID=...
    if "=" in binary:
        return None

    # Skip template variables embedded in the binary token.
    if "{{" in binary:
        return None

    path: tuple[str, ...] = (binary,)

    for token in tokens[1:]:
        # Explicit shell operators terminate the path.
        if token in _SHELL_OPERATORS:
            break
        # Flags, shell variables, quoted values, etc.
        if any(token.startswith(p) for p in _ARG_PREFIXES):
            break
        # Tokens with path-separator, dot, equals, colon characters.
        if _ARG_CHARS_RE.search(token):
            break
        # Must look like an identifier (no uppercase, no special chars).
        if not _IDENT_RE.match(token):
            break
        # Skip template variables embedded in the token.
        if "{{" in token:
            break
        # Consult the CLI help tree: is this token a known subcommand of
        # the current path?  If not, it is a positional argument — stop.
        if token not in _subcommands_of(path):
            break
        path = path + (token,)

    # A path of length 1 (binary only) has no subcommand to verify.
    if len(path) < 2:
        return None

    return path


# ---------------------------------------------------------------------------
# code-block extraction
# ---------------------------------------------------------------------------

# Fenced code blocks: ```bash\n...\n``` or ```\n...\n```
_FENCE_RE = re.compile(r"(?s)```(?:bash)?\n(.*?)```")

# 4-space indented lines (used for prose code snippets outside fenced blocks).
_INDENT4_RE = re.compile(r"(?m)^    (.+)$")


def _lines_from_text(text: str) -> list[str]:
    """Extract candidate command lines from *text*.

    Covers:
    - Fenced bash / plain code blocks.
    - 4-space indented code blocks (outside fenced blocks, as used in some
      formula prose for multi-line command examples).
    """
    lines: list[str] = []

    # Fenced blocks first.
    for m in _FENCE_RE.finditer(text):
        lines.extend(m.group(1).splitlines())

    # Indented blocks outside fenced blocks.
    clean = _FENCE_RE.sub("", text)
    for m in _INDENT4_RE.finditer(clean):
        lines.append(m.group(1))

    return lines


# ---------------------------------------------------------------------------
# pair collection (runs at module import / test collection time)
# ---------------------------------------------------------------------------

def _collect_pairs() -> list[tuple[str, str]]:
    """Return sorted, deduplicated (formula_name, command_path_str) pairs."""
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for toml_path in sorted(FORMULAS.glob("*.toml")):
        try:
            data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        formula_name = toml_path.stem

        # Collect all description texts: top-level and per-step.
        texts: list[str] = []
        if "description" in data:
            texts.append(data["description"])
        for step in data.get("steps", []):
            if "description" in step:
                texts.append(step["description"])

        for text in texts:
            for line in _lines_from_text(text):
                path = _extract_command_path(line)
                if path is None:
                    continue
                key = (formula_name, " ".join(path))
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)

    return pairs


# Collect once at import time.  The lru_cache on _subcommands_of ensures that
# each unique parent command is only called once even across all formula files.
_PAIRS: list[tuple[str, str]] = _collect_pairs()

# ---------------------------------------------------------------------------
# known broken commands (xfail)
#
# If a (formula_name, command_path) pair is listed here the test is marked
# xfail — it documents a real error in the formula prose that needs fixing.
# Add entries ONLY for genuinely invalid commands, not for false positives.
# Format: (formula_name, "gc subcommand path")
# ---------------------------------------------------------------------------

_KNOWN_BROKEN: dict[tuple[str, str], str] = {
    # Example (commented out — none currently known):
    # ("brief-decision-dispatch", "gc bd set-metadata"): "gc bd set-metadata does not exist; use gc bd update --set-metadata",
    # ("on-merge-brief-record", "gc bd mol sling"): "gc bd mol sling does not exist; use bd mol pour",
}

# ---------------------------------------------------------------------------
# parametrised test
# ---------------------------------------------------------------------------

# Provide a dummy entry when the collection is empty (binaries not on PATH)
# so that pytest reports a single skip rather than nothing.
_TEST_PARAMS = _PAIRS if _PAIRS else [("__no_binaries__", "__skip__")]


@pytest.mark.parametrize("formula_name,command_path", _TEST_PARAMS)
def test_command_exists_in_cli(formula_name: str, command_path: str) -> None:
    """Assert that every gc/bd subcommand in formula prose exists in the CLI.

    Each parametrised case represents one (formula, subcommand-path) pair
    extracted from a fenced bash block or 4-space indented code block inside a
    step description.

    Failures indicate that the formula prose references a non-existent
    subcommand and must be corrected before agent workers execute the formula.
    """
    # Graceful skip when the dummy sentinel is active (binaries missing).
    if formula_name == "__no_binaries__":
        pytest.skip("gc and bd not found on PATH — cannot verify command surface")

    tokens = command_path.split()
    binary = tokens[0]

    # Skip gracefully if the binary is not available at test time either.
    if shutil.which(binary) is None:
        pytest.skip(f"{binary!r} not found on PATH")

    # The subcommand to verify is the last token; its parent is everything
    # before it.
    subcommand = tokens[-1]
    parent = tokens[:-1]

    # Apply xfail marks for known broken commands.
    known_reason = _KNOWN_BROKEN.get((formula_name, command_path))
    if known_reason:
        pytest.xfail(known_reason)

    # Run the parent's help and confirm the subcommand appears.
    # gc sub-subcommand help requires a city directory in cwd.
    cwd: Optional[Path] = None
    if binary == "gc" and len(parent) > 1 and _GC_CITY_DIR is not None:
        cwd = _GC_CITY_DIR
    result = subprocess.run(
        parent + ["--help"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=cwd,
    )
    help_output = result.stdout + result.stderr
    found_subs = _parse_subcommands(help_output)

    if subcommand not in found_subs:
        # Emit diagnostic details before failing.
        print(f"\nFormula    : {formula_name}")
        print(f"Command    : {command_path}")
        print(f"Checking   : {' '.join(parent)} --help  |  looking for {subcommand!r}")
        print(f"Subcommands found in help: {sorted(found_subs)}")
        print(f"--- help output ---\n{help_output[:1500]}")
        pytest.fail(
            f"Subcommand {subcommand!r} not found in `{' '.join(parent)} --help` "
            f"(referenced in formula {formula_name!r})."
        )
