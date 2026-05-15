"""Discover and sort rotated log files for a given base log path."""

import re
from pathlib import Path
from typing import List


_ROTATION_RE = re.compile(
    r"^(?P<base>.+\.log)(?:\.(?P<index>\d+))?(?:\.gz)?$"
)


def _rotation_key(path: Path) -> int:
    """Return a sort key so files are ordered oldest-first.

    app.log.2.gz -> 2  (oldest)
    app.log.1    -> 1
    app.log      -> 0  (newest)
    """
    m = _ROTATION_RE.match(path.name)
    if m and m.group("index") is not None:
        return int(m.group("index"))
    return 0


def find_rotated_files(base_path: str) -> List[Path]:
    """Return all rotated variants of *base_path*, sorted oldest-first.

    Includes the base file itself plus any numbered / compressed siblings.
    """
    base = Path(base_path)
    directory = base.parent
    stem = base.name  # e.g. "app.log"

    candidates: List[Path] = []
    for entry in directory.iterdir():
        if entry.name == stem or entry.name.startswith(stem + "."):
            candidates.append(entry)

    # Sort: highest rotation index first (oldest), base file last (newest)
    candidates.sort(key=_rotation_key, reverse=True)
    return candidates


def is_compressed(path: Path) -> bool:
    """Return True if *path* is a gzip-compressed file."""
    return path.suffix == ".gz"
