"""Extract log lines across multiple rotated log files within a time range."""

from datetime import datetime
from pathlib import Path
from typing import Iterator, List

from logslice.compressed_reader import open_log_file, file_size
from logslice.rotated_files import find_rotated_files
from logslice.binary_search import find_start_offset, find_end_offset
from logslice.extractor import extract_lines
from logslice.timestamp_parser import parse_line_timestamp


def extract_from_rotated(
    base_path: str,
    start: datetime,
    end: datetime,
) -> Iterator[str]:
    """Yield log lines from rotated log files that fall within [start, end].

    Files are processed in chronological order (oldest first).
    """
    files: List[Path] = find_rotated_files(base_path)

    for log_path in files:
        with open_log_file(str(log_path)) as fh:
            size = file_size(str(log_path))
            if size == 0:
                continue

            start_offset = find_start_offset(fh, size, start)
            if start_offset is None:
                # All lines in this file are after `end` — no need to continue
                # checking later (newer) files.
                break

            end_offset = find_end_offset(fh, size, end)

            fh.seek(start_offset)
            for line in extract_lines(fh, start_offset, end_offset, start, end):
                yield line


def count_matching_lines(
    base_path: str,
    start: datetime,
    end: datetime,
) -> int:
    """Return the total number of log lines within [start, end] across all rotated files."""
    return sum(1 for _ in extract_from_rotated(base_path, start, end))
