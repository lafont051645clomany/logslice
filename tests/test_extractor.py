"""Tests for logslice.extractor.extract_lines."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone

import pytest

from logslice.extractor import extract_lines


LINES = [
    "2024-01-10T08:00:00Z INFO  server started\n",
    "2024-01-10T08:01:00Z DEBUG request received\n",
    "2024-01-10T08:02:00Z INFO  processing\n",
    "2024-01-10T08:03:00Z WARN  slow query\n",
    "2024-01-10T08:04:00Z ERROR connection dropped\n",
    "2024-01-10T08:05:00Z INFO  recovered\n",
]


def _make_log(lines: list[str]) -> str:
    """Write lines to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".log")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    return path


def dt(hour: int, minute: int) -> datetime:
    return datetime(2024, 1, 10, hour, minute, 0, tzinfo=timezone.utc)


@pytest.fixture()
def log_file():
    path = _make_log(LINES)
    yield path
    os.unlink(path)


def test_extract_full_range(log_file):
    result = list(extract_lines(log_file, dt(8, 0), dt(8, 5)))
    assert len(result) == 6


def test_extract_middle_range(log_file):
    result = list(extract_lines(log_file, dt(8, 1), dt(8, 3)))
    assert len(result) == 3
    assert "DEBUG request received" in result[0]
    assert "WARN  slow query" in result[-1]


def test_extract_single_line(log_file):
    result = list(extract_lines(log_file, dt(8, 2), dt(8, 2)))
    assert len(result) == 1
    assert "processing" in result[0]


def test_extract_before_all_lines(log_file):
    result = list(extract_lines(log_file, dt(7, 0), dt(7, 59)))
    assert result == []


def test_extract_after_all_lines(log_file):
    result = list(extract_lines(log_file, dt(9, 0), dt(9, 30)))
    assert result == []


def test_empty_file():
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    try:
        result = list(extract_lines(path, dt(8, 0), dt(8, 5)))
        assert result == []
    finally:
        os.unlink(path)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        list(extract_lines("/nonexistent/path/file.log", dt(8, 0), dt(8, 5)))
