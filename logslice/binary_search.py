"""Binary search utilities for locating timestamp boundaries in log files."""

import os
from datetime import datetime
from typing import Optional, BinaryIO

from logslice.timestamp_parser import parse_line_timestamp


DEFAULT_CHUNK_SIZE = 8192


def _find_line_start(f: BinaryIO, pos: int) -> int:
    """Given a position, seek backward to find the start of the current line."""
    if pos == 0:
        return 0
    f.seek(pos)
    # Read backward to find preceding newline
    search_pos = max(0, pos - 1)
    while search_pos > 0:
        f.seek(search_pos)
        char = f.read(1)
        if char == b"\n":
            return search_pos + 1
        search_pos -= 1
    return 0


def _read_line_at(f: BinaryIO, pos: int) -> Optional[str]:
    """Seek to pos, find line start, and return the first full line."""
    line_start = _find_line_start(f, pos)
    f.seek(line_start)
    line = f.readline()
    if line:
        return line.decode("utf-8", errors="replace").rstrip("\n")
    return None


def find_start_offset(f: BinaryIO, start_time: datetime) -> int:
    """Binary search for the first byte offset of a line with timestamp >= start_time.

    Args:
        f: An open binary file handle.
        start_time: The lower bound timestamp (inclusive).

    Returns:
        Byte offset of the first matching line, or file size if none found.
    """
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    if file_size == 0:
        return 0

    lo, hi = 0, file_size
    result = file_size

    while lo < hi:
        mid = (lo + hi) // 2
        line = _read_line_at(f, mid)
        if line is None:
            hi = mid
            continue
        ts = parse_line_timestamp(line)
        if ts is not None and ts >= start_time:
            result = _find_line_start(f, mid)
            hi = mid
        else:
            lo = mid + 1

    return result


def find_end_offset(f: BinaryIO, end_time: datetime) -> int:
    """Binary search for the byte offset just after the last line with timestamp <= end_time.

    Args:
        f: An open binary file handle.
        end_time: The upper bound timestamp (inclusive).

    Returns:
        Byte offset one past the last matching line, or 0 if none found.
    """
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    if file_size == 0:
        return 0

    lo, hi = 0, file_size
    result = 0

    while lo < hi:
        mid = (lo + hi) // 2
        line = _read_line_at(f, mid)
        if line is None:
            hi = mid
            continue
        ts = parse_line_timestamp(line)
        if ts is not None and ts <= end_time:
            # Move past this line
            line_start = _find_line_start(f, mid)
            f.seek(line_start)
            f.readline()
            result = f.tell()
            lo = mid + 1
        else:
            hi = mid

    return result
