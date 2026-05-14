"""Extracts log lines within a given time range from a (possibly rotated) log file."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterator, Optional

from logslice.binary_search import find_end_offset, find_start_offset
from logslice.timestamp_parser import parse_line_timestamp


def extract_lines(
    file_path: str,
    start_time: datetime,
    end_time: datetime,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[str]:
    """Yield log lines whose timestamps fall within [start_time, end_time].

    Uses binary search to locate the byte range of interest, then performs a
    linear scan over only that segment — avoiding a full file read.

    Args:
        file_path:  Path to the log file.
        start_time: Inclusive lower bound (timezone-aware or naive, must match
                    the timestamps present in the file).
        end_time:   Inclusive upper bound.
        encoding:   File encoding (default utf-8).
        errors:     How to handle decode errors (default 'replace').

    Yields:
        Raw log lines (including the trailing newline) whose parsed timestamp
        lies within the requested window.  Lines whose timestamp cannot be
        parsed are skipped.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return

    with open(file_path, "rb") as fh:
        start_offset: int = find_start_offset(fh, start_time, file_size)
        end_offset: int = find_end_offset(fh, end_time, file_size)

        if start_offset >= end_offset:
            return

        fh.seek(start_offset)
        remaining = end_offset - start_offset

        while remaining > 0:
            raw = fh.readline()
            if not raw:
                break
            remaining -= len(raw)
            line = raw.decode(encoding, errors=errors)
            ts: Optional[datetime] = parse_line_timestamp(line)
            if ts is None:
                continue
            if ts < start_time:
                continue
            if ts > end_time:
                break
            yield line
