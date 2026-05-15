"""Transparent reader that handles both plain-text and gzip-compressed logs."""

import gzip
import io
from pathlib import Path
from typing import IO


def open_log_file(path: Path, mode: str = "rb") -> IO[bytes]:
    """Open a log file for reading, decompressing on-the-fly if needed.

    Always returns a binary file-like object so callers can seek freely.
    For gzip files the entire content is decompressed into a BytesIO buffer
    to support random-access (required by the binary-search module).
    """
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as gz:
            data = gz.read()
        buf = io.BytesIO(data)
        return buf
    return open(path, mode)


def file_size(path: Path) -> int:
    """Return the byte size of a (potentially compressed) log file.

    For gzip files this is the *decompressed* size, because binary search
    operates on decompressed offsets.
    """
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as gz:
            gz.seek(0, 2)  # seek to end
            return gz.tell()
    return path.stat().st_size
