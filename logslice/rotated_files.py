"""Utilities for discovering and ordering rotated log file archives."""

import os
import re
from pathlib import Path
from typing import List

# Matches common rotated log suffixes: .1, .2, .gz, .1.gz, .2.gz, etc.
_ROTATED_SUFFIX_RE = re.compile(r'\.(\d+)(\.gz)?$')


def _rotation_key(path: Path) -> tuple:
    """Return a sort key so that the current log sorts first,
    followed by .1, .2, ... (older files last)."""
    match = _ROTATED_SUFFIX_RE.search(path.name)
    if match:
        index = int(match.group(1))
        is_gz = 1 if match.group(2) else 0
        return (1, index, is_gz)
    # No numeric suffix — this is the active/current log file
    return (0, 0, 0)


def find_rotated_files(base_path: str) -> List[Path]:
    """Given a log file path, return an ordered list of all related rotated
    files (including the base file itself) sorted from newest to oldest.

    Example:  /var/log/app.log  →  [app.log, app.log.1, app.log.2.gz, ...]
    """
    base = Path(base_path)
    if not base.exists():
        raise FileNotFoundError(f"Base log file not found: {base_path}")

    parent = base.parent
    stem = base.name  # e.g. "app.log"

    candidates: List[Path] = []
    for entry in parent.iterdir():
        if entry.name == stem or entry.name.startswith(stem + "."):
            candidates.append(entry)

    candidates.sort(key=_rotation_key)
    return candidates


def is_compressed(path: Path) -> bool:
    """Return True if the file appears to be gzip-compressed."""
    return path.suffix == ".gz"
